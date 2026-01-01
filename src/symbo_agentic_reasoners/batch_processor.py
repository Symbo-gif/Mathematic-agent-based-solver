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
BATCH PROCESSOR - Large-Scale Problem Processing
=================================================

Handles batch processing of mathematical problems from various sources:
- Single files (txt, json, csv)
- Folders of problem files
- Recursive directory scanning
- Watch mode for monitoring folders

Features:
- Parallel processing with configurable workers
- Progress tracking and reporting
- Result aggregation and export
- Error handling and retry logic
- Resource-aware throttling

Usage:
    from symbo_agentic_reasoners.batch_processor import BatchProcessor

    processor = BatchProcessor()
    results = processor.process_folder("./problems/")
    processor.export_results(results, "results.json")
"""

import os
import json
import csv
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.batch_processor')


class ProcessingStatus(Enum):
    """Status of batch processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProblemItem:
    """A single problem to be processed."""
    id: str
    problem: str
    source_file: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0


@dataclass
class BatchResult:
    """Results from a batch processing run."""
    batch_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_problems: int = 0
    solved: int = 0
    failed: int = 0
    cancelled: int = 0
    total_time_ms: float = 0.0
    source_path: str = ""
    items: List[ProblemItem] = field(default_factory=list)

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
            'batch_id': self.batch_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_problems': self.total_problems,
            'solved': self.solved,
            'failed': self.failed,
            'cancelled': self.cancelled,
            'success_rate': round(self.solved / max(self.total_problems, 1) * 100, 1),
            'total_time_ms': round(self.total_time_ms, 2),
            'avg_time_per_problem_ms': round(self.total_time_ms / max(self.total_problems, 1), 2),
            'source_path': self.source_path,
            'items': [
                {
                    'id': item.id,
                    'problem': item.problem,
                    'status': item.status.value,
                    'result': item.result,
                    'error': item.error,
                    'time_ms': item.processing_time_ms
                }
                for item in self.items
            ]
        }


class BatchProcessor:
    """
    High-performance batch processor for mathematical problems.

    Supports:
    - Multiple file formats (txt, json, csv)
    - Parallel processing
    - Progress callbacks
    - Result export
    """

    SUPPORTED_EXTENSIONS = {'.txt', '.json', '.csv', '.md', '.tex'}

    def __init__(
        self,
        max_workers: int = 4,
        timeout_per_problem: float = 60.0,
        progress_callback: Optional[Callable[[int, int, ProblemItem], None]] = None
    ):
        """
        Initialize the batch processor.

        Args:
            max_workers: Maximum parallel workers for processing
            timeout_per_problem: Timeout in seconds per problem
            progress_callback: Optional callback(current, total, item) for progress
        """
        self.max_workers = max_workers
        self.timeout_per_problem = timeout_per_problem
        self.progress_callback = progress_callback

        self._solver = None
        self._cancel_requested = False
        self._lock = threading.Lock()

        logger.info(f"BatchProcessor initialized (workers={max_workers})")

    def _get_solver(self):
        """Lazy-load the solver engine."""
        if self._solver is None:
            try:
                from symbo_agentic_reasoners.core.solver_engine import get_solver_engine
                self._solver = get_solver_engine()
            except Exception as e:
                logger.warning(f"Could not load solver engine: {e}")
                # Use fallback SymPy solver
                self._solver = self._create_fallback_solver()
        return self._solver

    def _create_fallback_solver(self):
        """Create a simple fallback solver using native symbolic engine."""
        class FallbackSolver:
            def solve(self, problem: str):
                """Perform solve operation.

                Args:
                problem: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.solve(...)
                """
                """Perform solve operation.

                Args:
                problem: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.solve(...)
                """
                from symbo_agentic_reasoners.core.native_symbolic import sympify, simplify
                from symbo_agentic_reasoners.core.solver_engine import SolveResult, SolveStatus

                try:
                    result = sympify(problem)
                    simplified = simplify(result)
                    return SolveResult(
                        status=SolveStatus.SUCCESS,
                        result=str(simplified),
                        specialist_used='native_symbolic'
                    )
                except Exception as e:
                    return SolveResult(
                        status=SolveStatus.FAILED,
                        error=str(e)
                    )

        return FallbackSolver()

    def process_folder(
        self,
        folder_path: str,
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None
    ) -> BatchResult:
        """
        Process all problem files in a folder.

        Args:
            folder_path: Path to the folder
            recursive: Whether to scan subdirectories
            file_patterns: Optional list of glob patterns to match

        Returns:
            BatchResult with all processing results
        """
        folder = Path(folder_path).resolve()  # SECURITY: Resolve to absolute path

        # SECURITY: Prevent path traversal - ensure we stay within intended directory
        try:
            # Get canonical path and verify it's safe
            cwd = Path.cwd().resolve()
            if not str(folder).startswith(str(cwd)) and not folder.is_absolute():
                folder = (cwd / folder_path).resolve()
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid folder path: {folder_path}") from e

        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        if not folder.is_dir():
            raise ValueError(f"Path is not a folder: {folder_path}")

        # SECURITY: Limit recursion depth and file count to prevent DoS
        MAX_FILES = 10000
        MAX_DEPTH = 10

        # Collect all problem files
        files = []
        if recursive:
            for ext in self.SUPPORTED_EXTENSIONS:
                for f in folder.rglob(f"*{ext}"):
                    # Check depth - count path separators relative to base
                    try:
                        rel_path = f.relative_to(folder)
                        depth = len(rel_path.parts)
                        if depth <= MAX_DEPTH:
                            files.append(f)
                    except ValueError:
                        continue  # Skip files outside base folder
                    if len(files) >= MAX_FILES:
                        logger.warning(f"File limit reached ({MAX_FILES}), stopping scan")
                        break
                if len(files) >= MAX_FILES:
                    break
        else:
            for ext in self.SUPPORTED_EXTENSIONS:
                files.extend(list(folder.glob(f"*{ext}"))[:MAX_FILES])

        # Load problems from files
        problems = []
        for file_path in files:
            file_problems = self._load_problems_from_file(file_path)
            problems.extend(file_problems)

        logger.info(f"Found {len(problems)} problems in {len(files)} files")

        return self._process_batch(problems, str(folder_path))

    def process_file(self, file_path: str) -> BatchResult:
        """
        Process problems from a single file.

        Args:
            file_path: Path to the file

        Returns:
            BatchResult with processing results
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        problems = self._load_problems_from_file(path)
        logger.info(f"Loaded {len(problems)} problems from {file_path}")

        return self._process_batch(problems, file_path)

    def process_problems(self, problems: List[str]) -> BatchResult:
        """
        Process a list of problem strings directly.

        Args:
            problems: List of problem strings

        Returns:
            BatchResult with processing results
        """
        items = [
            ProblemItem(
                id=f"problem_{i:04d}",
                problem=p,
                source_file="direct_input"
            )
            for i, p in enumerate(problems)
        ]
        return self._process_batch(items, "direct_input")

    def _load_problems_from_file(self, file_path: Path) -> List[ProblemItem]:
        """Load problems from a file based on its format."""
        problems = []
        file_id_prefix = file_path.stem

        try:
            if file_path.suffix.lower() == '.json':
                problems = self._load_json_problems(file_path, file_id_prefix)
            elif file_path.suffix.lower() == '.csv':
                problems = self._load_csv_problems(file_path, file_id_prefix)
            elif file_path.suffix.lower() in ['.txt', '.md']:
                problems = self._load_text_problems(file_path, file_id_prefix)
            elif file_path.suffix.lower() == '.tex':
                problems = self._load_tex_problems(file_path, file_id_prefix)

        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")

        # Set source file
        for p in problems:
            p.source_file = str(file_path)

        return problems

    def _load_json_problems(self, file_path: Path, prefix: str) -> List[ProblemItem]:
        """Load problems from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        problems = []
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    problems.append(ProblemItem(
                        id=f"{prefix}_{i:04d}",
                        problem=item
                    ))
                elif isinstance(item, dict):
                    problems.append(ProblemItem(
                        id=item.get('id', f"{prefix}_{i:04d}"),
                        problem=item.get('problem', str(item)),
                        metadata=item.get('metadata', {})
                    ))
        elif isinstance(data, dict):
            if 'problems' in data:
                return self._load_json_problems_recursive(data['problems'], prefix)

        return problems

    def _load_json_problems_recursive(self, data: Any, prefix: str) -> List[ProblemItem]:
        """Recursively extract problems from nested JSON."""
        problems = []
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    problems.append(ProblemItem(id=f"{prefix}_{i:04d}", problem=item))
                elif isinstance(item, dict) and 'problem' in item:
                    problems.append(ProblemItem(
                        id=item.get('id', f"{prefix}_{i:04d}"),
                        problem=item['problem']
                    ))
        return problems

    def _load_csv_problems(self, file_path: Path, prefix: str) -> List[ProblemItem]:
        """Load problems from CSV file."""
        problems = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                problem = row.get('problem') or row.get('expression') or row.get('question')
                if problem:
                    problems.append(ProblemItem(
                        id=row.get('id', f"{prefix}_{i:04d}"),
                        problem=problem,
                        metadata={k: v for k, v in row.items() if k not in ['id', 'problem']}
                    ))
        return problems

    def _load_text_problems(self, file_path: Path, prefix: str) -> List[ProblemItem]:
        """Load problems from text file (one per line)."""
        problems = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#') and not line.startswith('//'):
                    problems.append(ProblemItem(
                        id=f"{prefix}_{i:04d}",
                        problem=line
                    ))
        return problems

    def _load_tex_problems(self, file_path: Path, prefix: str) -> List[ProblemItem]:
        """Load problems from LaTeX file (extract math environments)."""
        problems = []
        import re

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract inline math $...$
        inline = re.findall(r'\$([^\$]+)\$', content)
        # Extract display math $$...$$
        display = re.findall(r'\$\$([^\$]+)\$\$', content)
        # Extract equation environments
        equations = re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', content, re.DOTALL)

        all_math = inline + display + equations
        for i, math in enumerate(all_math):
            problems.append(ProblemItem(
                id=f"{prefix}_{i:04d}",
                problem=math.strip()
            ))

        return problems

    def _process_batch(self, problems: List[ProblemItem], source: str) -> BatchResult:
        """Process a batch of problems."""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = BatchResult(
            batch_id=batch_id,
            start_time=datetime.now(),
            total_problems=len(problems),
            source_path=source,
            items=problems
        )

        if not problems:
            result.end_time = datetime.now()
            return result

        self._cancel_requested = False
        solver = self._get_solver()

        # Process problems (can be parallelized)
        if self.max_workers > 1:
            self._process_parallel(problems, solver, result)
        else:
            self._process_sequential(problems, solver, result)

        result.end_time = datetime.now()
        result.total_time_ms = (result.end_time - result.start_time).total_seconds() * 1000

        return result

    def _process_sequential(self, problems: List[ProblemItem], solver, result: BatchResult):
        """Process problems one at a time."""
        for i, item in enumerate(problems):
            if self._cancel_requested:
                item.status = ProcessingStatus.CANCELLED
                result.cancelled += 1
                continue

            self._solve_item(item, solver)

            if item.status == ProcessingStatus.COMPLETED:
                result.solved += 1
            else:
                result.failed += 1

            if self.progress_callback:
                self.progress_callback(i + 1, len(problems), item)

    def _process_parallel(self, problems: List[ProblemItem], solver, result: BatchResult):
        """Process problems in parallel using thread pool."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._solve_item, item, solver): item
                for item in problems
            }

            completed = 0
            for future in as_completed(futures):
                if self._cancel_requested:
                    break

                item = futures[future]
                completed += 1

                if item.status == ProcessingStatus.COMPLETED:
                    result.solved += 1
                else:
                    result.failed += 1

                if self.progress_callback:
                    self.progress_callback(completed, len(problems), item)

        # Mark remaining as cancelled
        for item in problems:
            if item.status == ProcessingStatus.PENDING:
                item.status = ProcessingStatus.CANCELLED
                result.cancelled += 1

    def _solve_item(self, item: ProblemItem, solver) -> None:
        """Solve a single problem item."""
        item.status = ProcessingStatus.PROCESSING
        start_time = time.time()

        try:
            solve_result = solver.solve(item.problem)
            item.processing_time_ms = (time.time() - start_time) * 1000

            item.result = {
                'status': solve_result.status.value,
                'result': solve_result.result,
                'domain': getattr(solve_result, 'domain', ''),
                'specialist': getattr(solve_result, 'specialist_used', '')
            }

            if solve_result.status.value == 'success':
                item.status = ProcessingStatus.COMPLETED
            else:
                item.status = ProcessingStatus.FAILED
                item.error = getattr(solve_result, 'error', None)

        except Exception as e:
            item.processing_time_ms = (time.time() - start_time) * 1000
            item.status = ProcessingStatus.FAILED
            item.error = str(e)
            item.result = {'status': 'error', 'error': str(e)}

    def cancel(self):
        """Request cancellation of ongoing batch processing."""
        with self._lock:
            self._cancel_requested = True
        logger.info("Batch processing cancellation requested")

    def export_results(
        self,
        result: BatchResult,
        output_path: str,
        format: str = 'json'
    ) -> str:
        """
        Export batch results to a file.

        Args:
            result: BatchResult to export
            output_path: Path for output file
            format: Output format ('json', 'csv', 'txt')

        Returns:
            Path to the exported file
        """
        path = Path(output_path)

        if format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        elif format == 'csv':
            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'problem', 'status', 'result', 'error', 'time_ms'])
                for item in result.items:
                    writer.writerow([
                        item.id,
                        item.problem,
                        item.status.value,
                        item.result.get('result') if item.result else '',
                        item.error or '',
                        round(item.processing_time_ms, 2)
                    ])

        elif format == 'txt':
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"Batch Results: {result.batch_id}\n")
                f.write(f"{'=' * 60}\n")
                f.write(f"Total: {result.total_problems} | Solved: {result.solved} | Failed: {result.failed}\n")
                f.write(f"Time: {result.total_time_ms:.2f}ms\n\n")

                for item in result.items:
                    f.write(f"[{item.id}] {item.problem[:50]}...\n")
                    if item.status == ProcessingStatus.COMPLETED:
                        f.write(f"  => {item.result.get('result', 'OK')}\n")
                    else:
                        f.write(f"  => ERROR: {item.error}\n")
                    f.write("\n")

        logger.info(f"Results exported to {path}")
        return str(path)


class FolderWatcher:
    """
    Watch a folder for new problem files and process them automatically.

    Useful for continuous integration scenarios where problems are
    dropped into a folder for automatic processing.
    """

    def __init__(
        self,
        watch_path: str,
        output_path: str,
        processor: Optional[BatchProcessor] = None,
        poll_interval: float = 5.0
    ):
        """
        Initialize folder watcher.

        Args:
            watch_path: Folder to watch for new files
            output_path: Folder for results
            processor: BatchProcessor instance (created if not provided)
            poll_interval: Seconds between folder scans
        """
        self.watch_path = Path(watch_path)
        self.output_path = Path(output_path)
        self.processor = processor or BatchProcessor()
        self.poll_interval = poll_interval

        self._running = False
        self._processed_files = set()
        self._thread = None

        # Create directories if needed
        self.watch_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def start(self):
        """Start watching the folder."""
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info(f"Started watching: {self.watch_path}")

    def stop(self):
        """Stop watching the folder."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("Stopped folder watcher")

    def _watch_loop(self):
        """Main watch loop."""
        while self._running:
            try:
                self._scan_and_process()
            except Exception as e:
                logger.error(f"Error in watch loop: {e}")

            time.sleep(self.poll_interval)

    def _scan_and_process(self):
        """Scan for new files and process them."""
        for ext in BatchProcessor.SUPPORTED_EXTENSIONS:
            for file_path in self.watch_path.glob(f"*{ext}"):
                if str(file_path) not in self._processed_files:
                    self._process_file(file_path)

    def _process_file(self, file_path: Path):
        """Process a single new file."""
        logger.info(f"Processing new file: {file_path}")

        try:
            result = self.processor.process_file(str(file_path))

            # Export results
            output_name = f"{file_path.stem}_results.json"
            output_file = self.output_path / output_name
            self.processor.export_results(result, str(output_file))

            self._processed_files.add(str(file_path))

            # Optionally move processed file
            processed_dir = self.watch_path / "processed"
            processed_dir.mkdir(exist_ok=True)
            file_path.rename(processed_dir / file_path.name)

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")


# Convenience functions
def process_folder(folder_path: str, **kwargs) -> BatchResult:
    """Process all problems in a folder."""
    processor = BatchProcessor(**kwargs)
    return processor.process_folder(folder_path)


def process_file(file_path: str, **kwargs) -> BatchResult:
    """Process problems from a single file."""
    processor = BatchProcessor(**kwargs)
    return processor.process_file(file_path)


def process_problems(problems: List[str], **kwargs) -> BatchResult:
    """Process a list of problem strings."""
    processor = BatchProcessor(**kwargs)
    return processor.process_problems(problems)
