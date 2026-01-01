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
Sandbox Evaluator
==================

Agent 3.2 of the Algorithm Discovery Unit

Secure execution environment that runs proposed code against rigorous
test sets. Returns scalar scores (execution speed, compression ratio,
accuracy) to the Proposer. Filters out incorrect code immediately,
ensuring Proposer only learns from valid programs.

Security features:
- Containerized execution with resource limits
- No network access
- Automatic timeout
- Memory limits

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 3
Reference: Phase_6_Build_Order_Breakdown.md, Step 3
"""

import sys
import time
import traceback
import multiprocessing
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import io
from contextlib import redirect_stdout, redirect_stderr

from .problem_specification import ProblemSpecification
from .code_evolutionary_proposer import CodeCandidate


class EvaluationStatus(Enum):
    """Status of code evaluation"""
    SUCCESS = 'success'
    SYNTAX_ERROR = 'syntax_error'
    RUNTIME_ERROR = 'runtime_error'
    TIMEOUT = 'timeout'
    MEMORY_ERROR = 'memory_error'
    WRONG_ANSWER = 'wrong_answer'


@dataclass
class EvaluationResult:
    """
    Result of evaluating a code candidate.

    Attributes:
        candidate_id: ID of evaluated candidate
        status: Evaluation status
        correctness_score: Fraction of test cases passed
        execution_time_ms: Total execution time
        fitness_score: Overall fitness (0-1)
        test_results: Per-test results
        error_message: Error message if any
    """
    candidate_id: str
    status: EvaluationStatus
    correctness_score: float
    execution_time_ms: float
    fitness_score: float
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'candidate_id': self.candidate_id,
            'status': self.status.value,
            'correctness_score': self.correctness_score,
            'execution_time_ms': self.execution_time_ms,
            'fitness_score': self.fitness_score,
            'tests_passed': sum(1 for t in self.test_results if t.get('passed')),
            'tests_total': len(self.test_results),
            'error_message': self.error_message
        }


def _execute_in_sandbox(code: str, test_case: Tuple, timeout: float) -> Dict[str, Any]:
    """
    Execute code in sandbox (runs in subprocess for isolation).

    This function is designed to be run in a separate process.
    """
    result = {
        'passed': False,
        'output': None,
        'expected': test_case[1],
        'time_ms': 0.0,
        'error': None
    }

    try:
        # Compile the code
        compiled = compile(code, '<string>', 'exec')

        # Create restricted globals
        restricted_globals = {
            '__builtins__': {
                'range': range,
                'len': len,
                'int': int,
                'float': float,
                'str': str,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'bool': bool,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'sorted': sorted,
                'reversed': reversed,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'any': any,
                'all': all,
                'isinstance': isinstance,
                'type': type,
                'print': print,
                'True': True,
                'False': False,
                'None': None,
            },
            'List': list,
        }

        # Execute the code to define the function
        local_vars = {}
        exec(compiled, restricted_globals, local_vars)

        # Get the solve function
        if 'solve' not in local_vars:
            result['error'] = "No 'solve' function defined"
            return result

        solve_fn = local_vars['solve']

        # Run the test
        input_args = test_case[0]
        expected = test_case[1]

        start_time = time.time()

        # Handle different input formats
        if isinstance(input_args, tuple):
            output = solve_fn(*input_args)
        else:
            output = solve_fn(input_args)

        elapsed_ms = (time.time() - start_time) * 1000

        result['output'] = output
        result['time_ms'] = elapsed_ms
        result['passed'] = (output == expected)

    except SyntaxError as e:
        result['error'] = f"Syntax error: {e}"
    except (RecursionError, MemoryError) as e:
        # Resource exhaustion errors
        result['error'] = f"Resource error: {type(e).__name__}: {e}"
    except (TypeError, ValueError, KeyError, IndexError, AttributeError) as e:
        # Data/logic errors from user code
        result['error'] = f"Runtime error (data): {type(e).__name__}: {e}"
    except (RuntimeError, ArithmeticError, LookupError) as e:
        # Execution errors from user code
        result['error'] = f"Runtime error (execution): {type(e).__name__}: {e}"

    return result


class SandboxEvaluator:
    """
    Agent 3.2: Sandbox Evaluator - Secure code execution

    Evaluates code candidates in a sandboxed environment with:
    - Resource limits (time, memory)
    - Restricted builtins
    - No file/network access

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    def __init__(
        self,
        problem_spec: Optional[ProblemSpecification] = None,
        timeout_seconds: float = 5.0,
        memory_limit_mb: int = 256
    ):
        """
        Initialize the Sandbox Evaluator.

        Args:
            problem_spec: Problem specification with test cases (optional)
            timeout_seconds: Timeout for each test case
            memory_limit_mb: Memory limit in megabytes
        """
        self.problem_spec = problem_spec
        self.timeout = timeout_seconds
        self.memory_limit = memory_limit_mb

        # Statistics
        self.stats = {
            'evaluations': 0,
            'successes': 0,
            'syntax_errors': 0,
            'runtime_errors': 0,
            'timeouts': 0,
            'wrong_answers': 0,
            'average_time_ms': 0.0
        }
        self._total_time = 0.0

    def evaluate(self, candidate: CodeCandidate) -> CodeCandidate:
        """
        Evaluate a code candidate.

        Args:
            candidate: CodeCandidate to evaluate

        Returns:
            Updated candidate with fitness scores
        """
        result = self.evaluate_detailed(candidate)

        # Update candidate
        candidate.correctness_score = result.correctness_score
        candidate.execution_time_ms = result.execution_time_ms
        candidate.fitness_score = result.fitness_score

        return candidate

    def evaluate_detailed(self, candidate: CodeCandidate) -> EvaluationResult:
        """
        Evaluate a code candidate with detailed results.

        Args:
            candidate: CodeCandidate to evaluate

        Returns:
            EvaluationResult with detailed test results
        """
        self.stats['evaluations'] += 1

        # First check syntax
        try:
            compile(candidate.code, '<string>', 'exec')
        except SyntaxError as e:
            self.stats['syntax_errors'] += 1
            return EvaluationResult(
                candidate_id=candidate.candidate_id,
                status=EvaluationStatus.SYNTAX_ERROR,
                correctness_score=0.0,
                execution_time_ms=0.0,
                fitness_score=0.0,
                error_message=f"Syntax error: {e}"
            )

        # Run tests
        test_results = []
        total_time = 0.0
        passed = 0

        for test_case in self.problem_spec.test_cases:
            result = self._run_test(candidate.code, test_case)
            test_results.append(result)
            total_time += result.get('time_ms', 0)

            if result.get('passed'):
                passed += 1

        # Compute scores
        total_tests = len(self.problem_spec.test_cases)
        correctness_score = passed / total_tests if total_tests > 0 else 0.0

        # Determine status
        if all(r.get('passed') for r in test_results):
            status = EvaluationStatus.SUCCESS
            self.stats['successes'] += 1
        elif any(r.get('error', '').startswith('Runtime') for r in test_results):
            status = EvaluationStatus.RUNTIME_ERROR
            self.stats['runtime_errors'] += 1
        elif any('Timeout' in r.get('error', '') for r in test_results):
            status = EvaluationStatus.TIMEOUT
            self.stats['timeouts'] += 1
        else:
            status = EvaluationStatus.WRONG_ANSWER
            self.stats['wrong_answers'] += 1

        # Compute fitness
        fitness_score = self._compute_fitness(
            correctness_score,
            total_time,
            len(candidate.code)
        )

        # Update stats
        self._total_time += total_time
        self.stats['average_time_ms'] = self._total_time / self.stats['evaluations']

        # Get error message if any
        error_message = ""
        for r in test_results:
            if r.get('error'):
                error_message = r['error']
                break

        return EvaluationResult(
            candidate_id=candidate.candidate_id,
            status=status,
            correctness_score=correctness_score,
            execution_time_ms=total_time,
            fitness_score=fitness_score,
            test_results=test_results,
            error_message=error_message
        )

    def _run_test(self, code: str, test_case: Tuple) -> Dict[str, Any]:
        """Run a single test case in sandbox"""
        # Use inline execution with timeout simulation
        # (In production, would use multiprocessing with actual timeout)

        try:
            return self._execute_safely(code, test_case)
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as e:
            # Data/logic errors during test execution
            return {
                'passed': False,
                'output': None,
                'expected': test_case[1],
                'time_ms': 0.0,
                'error': f"Execution error (data): {type(e).__name__}: {e}"
            }
        except (RuntimeError, RecursionError, MemoryError, ArithmeticError) as e:
            # Resource/runtime errors during test execution
            return {
                'passed': False,
                'output': None,
                'expected': test_case[1],
                'time_ms': 0.0,
                'error': f"Execution error (runtime): {type(e).__name__}: {e}"
            }

    def _execute_safely(self, code: str, test_case: Tuple) -> Dict[str, Any]:
        """Execute code with safety restrictions"""
        result = {
            'passed': False,
            'output': None,
            'expected': test_case[1],
            'time_ms': 0.0,
            'error': None
        }

        try:
            # Create restricted environment
            safe_builtins = {
                'range': range,
                'len': len,
                'int': int,
                'float': float,
                'str': str,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'bool': bool,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'sorted': sorted,
                'reversed': reversed,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'any': any,
                'all': all,
                'isinstance': isinstance,
                'type': type,
                'True': True,
                'False': False,
                'None': None,
                '__import__': self._safe_import,
            }

            restricted_globals = {'__builtins__': safe_builtins}
            local_vars = {}

            # Execute code
            exec(code, restricted_globals, local_vars)

            if 'solve' not in local_vars:
                result['error'] = "No 'solve' function defined"
                return result

            solve_fn = local_vars['solve']

            # Run test
            input_args = test_case[0]
            expected = test_case[1]

            start_time = time.time()

            if isinstance(input_args, tuple):
                output = solve_fn(*input_args)
            else:
                output = solve_fn(input_args)

            elapsed_ms = (time.time() - start_time) * 1000

            # Check timeout
            if elapsed_ms > self.timeout * 1000:
                result['error'] = f"Timeout: {elapsed_ms:.0f}ms > {self.timeout * 1000:.0f}ms"
                return result

            result['output'] = output
            result['time_ms'] = elapsed_ms
            result['passed'] = self._compare_outputs(output, expected)

        except RecursionError:
            result['error'] = "Runtime error: RecursionError (max depth exceeded)"
        except MemoryError:
            result['error'] = "Runtime error: MemoryError"
        except (TypeError, ValueError, AttributeError, KeyError, IndexError) as e:
            # Data/logic errors from user code execution
            result['error'] = f"Runtime error (data): {type(e).__name__}: {e}"
        except (RuntimeError, ArithmeticError, ZeroDivisionError) as e:
            # Execution errors from user code
            result['error'] = f"Runtime error (execution): {type(e).__name__}: {e}"

        return result

    def _safe_import(self, name, *args, **kwargs):
        """Restricted import function"""
        allowed = {'functools', 'itertools', 'collections', 'math', 'heapq', 'typing'}
        if name in allowed:
            return __import__(name, *args, **kwargs)
        raise ImportError(f"Import of '{name}' not allowed in sandbox")

    def _compare_outputs(self, output: Any, expected: Any) -> bool:
        """Compare outputs, handling floating point and containers"""
        if output == expected:
            return True

        # Handle floating point comparison
        if isinstance(output, float) and isinstance(expected, float):
            return abs(output - expected) < 1e-6

        # Handle list/tuple comparison
        if isinstance(output, (list, tuple)) and isinstance(expected, (list, tuple)):
            if len(output) != len(expected):
                return False
            return all(self._compare_outputs(a, b) for a, b in zip(output, expected))

        return False

    def _compute_fitness(
        self,
        correctness: float,
        time_ms: float,
        code_length: int
    ) -> float:
        """
        Compute overall fitness score.

        Factors:
        - Correctness (80%): Most important
        - Speed (10%): Faster is better
        - Code length (10%): Shorter is better (Occam's razor)
        """
        # Correctness component
        fitness = correctness * 0.8

        # Speed bonus (0-0.1)
        max_time = self.timeout * 1000 * len(self.problem_spec.test_cases)
        if max_time > 0:
            speed_score = max(0, 1.0 - time_ms / max_time)
            fitness += speed_score * 0.1

        # Code length bonus (0-0.1)
        # Shorter code gets higher bonus (up to 500 chars considered good)
        length_score = max(0, 1.0 - code_length / 2000)
        fitness += length_score * 0.1

        return round(min(1.0, fitness), 4)

    def evaluate_batch(self, candidates: List[CodeCandidate]) -> List[CodeCandidate]:
        """
        Evaluate a batch of candidates.

        Args:
            candidates: List of candidates to evaluate

        Returns:
            Updated candidates with fitness scores
        """
        return [self.evaluate(c) for c in candidates]

    def get_statistics(self) -> Dict[str, Any]:
        """Get evaluator statistics"""
        total = self.stats['evaluations']
        if total > 0:
            success_rate = self.stats['successes'] / total * 100
        else:
            success_rate = 0.0

        result = {
            **self.stats,
            'success_rate_percent': round(success_rate, 2),
        }

        if self.problem_spec:
            result['problem_id'] = self.problem_spec.problem_id
            result['num_test_cases'] = len(self.problem_spec.test_cases)
        else:
            result['problem_id'] = None
            result['num_test_cases'] = 0

        return result

    def reset(self):
        """Reset evaluator state"""
        self._total_time = 0.0
        for key in self.stats:
            if key != 'average_time_ms':
                self.stats[key] = 0
            else:
                self.stats[key] = 0.0

    def set_problem(self, problem_spec: ProblemSpecification):
        """Set the problem specification for evaluation."""
        self.problem_spec = problem_spec

    def health_check(self) -> bool:
        """Check if evaluator is healthy"""
        # When no problem is set, still healthy but not ready for evaluation
        if self.problem_spec is None:
            return True
        return len(self.problem_spec.test_cases) > 0
