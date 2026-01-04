# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Solver Functions
================

High-level solve functions for the public API.
These wrap the internal solver engine with timeout protection and structured results.
"""

import time
import logging
import signal
from pathlib import Path
from typing import Optional, List, Union
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from .config import SolverConfig
from .result import SolveResult

logger = logging.getLogger(__name__)


# Timeout buffer multiplier for batch operations (accounts for thread overhead)
_BATCH_TIMEOUT_BUFFER = 2.0


def _get_engine():
    """Get the solver engine singleton."""
    from symbo_agentic_reasoners.core.solver import get_solver_engine
    return get_solver_engine()


def _convert_internal_result(internal_result, problem: str, start_time: float) -> SolveResult:
    """Convert internal SolveResult to public API SolveResult."""
    from symbo_agentic_reasoners.core.solver import SolveStatus

    solve_time_ms = (time.time() - start_time) * 1000

    if internal_result.status == SolveStatus.SUCCESS:
        return SolveResult.success(
            solution=str(internal_result.result) if internal_result.result else "",
            problem=problem,
            solve_time_ms=solve_time_ms,
            domain=internal_result.domain,
            operation=internal_result.operation,
            specialist_used=internal_result.specialist_used,
            diagnostics=internal_result.metadata if hasattr(internal_result, 'metadata') else {},
        )
    elif internal_result.status == SolveStatus.TIMEOUT:
        return SolveResult.timeout(
            problem=problem,
            timeout_sec=solve_time_ms / 1000,
        )
    else:
        return SolveResult.failure(
            error=internal_result.error or "Unknown error",
            problem=problem,
            solve_time_ms=solve_time_ms,
            diagnostics=internal_result.metadata if hasattr(internal_result, 'metadata') else {},
        )


def solve_expression(
    input_str: str,
    config: Optional[SolverConfig] = None
) -> SolveResult:
    """
    Solve a single mathematical expression.

    This is the primary entry point for solving mathematical problems.
    The expression can be in natural language or symbolic notation.

    Args:
        input_str: Mathematical expression or problem description
        config: Optional configuration for timeout and limits

    Returns:
        SolveResult with status, solution, and diagnostics

    Example:
        >>> result = solve_expression("differentiate x^2 + 3x")
        >>> print(result.solution)  # "2*x + 3"

        >>> result = solve_expression("2 + 2")
        >>> print(result.solution)  # "4"

        >>> config = SolverConfig(timeout_sec=5.0)
        >>> result = solve_expression("integrate(sin(x)*cos(x), x)", config)
    """
    if config is None:
        config = SolverConfig()

    start_time = time.time()

    try:
        engine = _get_engine()

        # Execute with timeout if enabled
        if config.enable_timeouts:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(engine.solve, input_str)
                try:
                    internal_result = future.result(timeout=config.timeout_sec)
                except FuturesTimeoutError:
                    return SolveResult.timeout(
                        problem=input_str,
                        timeout_sec=config.timeout_sec,
                    )
        else:
            internal_result = engine.solve(input_str)

        return _convert_internal_result(internal_result, input_str, start_time)

    except Exception as e:
        logger.exception(f"solve_expression failed for: {input_str}")
        return SolveResult.failure(
            error=str(e),
            problem=input_str,
            solve_time_ms=(time.time() - start_time) * 1000,
        )


def solve_file(
    path: Union[str, Path],
    config: Optional[SolverConfig] = None
) -> List[SolveResult]:
    """
    Solve all problems in a file.

    Supports multiple file formats:
    - .txt: One problem per line (lines starting with # are ignored)
    - .json: Array of problem strings or objects with "problem" key
    - .csv: Must have a "problem" column

    Args:
        path: Path to the file containing problems
        config: Optional configuration for timeout and limits

    Returns:
        List of SolveResult, one per problem

    Example:
        >>> results = solve_file("problems.txt")
        >>> for r in results:
        ...     print(f"{r.problem}: {r.solution if r.is_success else r.error}")
    """
    if config is None:
        config = SolverConfig()

    file_path = Path(path)
    if not file_path.exists():
        return [SolveResult.failure(
            error=f"File not found: {path}",
            problem=str(path),
        )]

    problems = _load_problems_from_file(file_path)

    return solve_batch(problems, config)


def solve_batch(
    problems: List[str],
    config: Optional[SolverConfig] = None
) -> List[SolveResult]:
    """
    Solve a batch of problems.

    Problems are solved in parallel (up to max_parallel_problems).
    Each problem has its own timeout.

    Args:
        problems: List of problem strings
        config: Optional configuration for timeout and limits

    Returns:
        List of SolveResult, one per problem (in same order as input)

    Example:
        >>> results = solve_batch(["2+2", "3*3", "diff(x**2, x)"])
        >>> for r in results:
        ...     print(r.solution)
    """
    if config is None:
        config = SolverConfig()

    if not problems:
        return []

    results: List[SolveResult] = []

    # Use thread pool for parallelism
    max_workers = min(config.max_parallel_problems, len(problems))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all problems
        futures = [
            executor.submit(solve_expression, problem, config)
            for problem in problems
        ]

        # Collect results in order
        for future in futures:
            try:
                result = future.result(timeout=config.timeout_sec * _BATCH_TIMEOUT_BUFFER)
                results.append(result)
            except FuturesTimeoutError:
                results.append(SolveResult.timeout(timeout_sec=config.timeout_sec))
            except Exception as e:
                results.append(SolveResult.failure(error=str(e)))

    return results


def _load_problems_from_file(file_path: Path) -> List[str]:
    """Load problems from a file based on format."""
    import json
    import csv

    problems = []

    try:
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            problems.append(item)
                        elif isinstance(item, dict) and 'problem' in item:
                            problems.append(item['problem'])
                elif isinstance(data, dict) and 'problems' in data:
                    for item in data['problems']:
                        if isinstance(item, str):
                            problems.append(item)
                        elif isinstance(item, dict) and 'problem' in item:
                            problems.append(item['problem'])

        elif file_path.suffix.lower() == '.csv':
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    problem = row.get('problem') or row.get('expression') or row.get('question')
                    if problem:
                        problems.append(problem.strip())

        else:  # .txt, .md, or other text formats
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#') and not line.startswith('//'):
                        problems.append(line)

    except Exception as e:
        logger.warning(f"Failed to load problems from {file_path}: {e}")

    return problems
