"""
Base Benchmark Infrastructure

Provides abstract base class and data structures for all benchmark runners.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import json
import time
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


class BenchmarkStatus(Enum):
    """Status of a benchmark problem result"""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    TIMEOUT = "timeout"
    ERROR = "error"
    PARSE_FAILURE = "parse_failure"
    SKIP = "skip"


@dataclass
class BenchmarkResult:
    """Result for a single benchmark problem"""
    problem_id: str
    problem_text: str
    expected_answer: Any
    system_answer: Optional[str]
    status: BenchmarkStatus
    time_seconds: float
    specialist_used: Optional[str] = None
    domain: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        # Convert status to enum if it's a string
        if isinstance(self.status, str):
            self.status = BenchmarkStatus(self.status)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        d = asdict(self)
        d['status'] = self.status.value
        return d


@dataclass
class BenchmarkSummary:
    """Aggregate statistics for a benchmark suite"""
    benchmark_name: str
    total_problems: int
    correct: int
    incorrect: int
    timeout: int
    error: int
    parse_failure: int
    skipped: int
    accuracy: float
    mean_time_seconds: float
    median_time_seconds: float
    p95_time_seconds: float
    total_time_seconds: float
    by_category: Dict[str, Dict[str, Any]]
    start_time: str
    end_time: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class BaseBenchmark(ABC):
    """
    Abstract base class for all benchmark runners.

    Provides:
    - Standardized problem execution interface
    - Timeout management
    - Checkpoint/resume capability
    - Result collection and reporting
    - Error handling
    """

    def __init__(
        self,
        name: str,
        timeout_seconds: int = 30,
        checkpoint_interval: int = 100,
        results_dir: str = "data/benchmarks/results",
        checkpoints_dir: str = "data/benchmarks/checkpoints"
    ):
        """
        Initialize benchmark runner.

        Args:
            name: Name of the benchmark (e.g., "gsm8k", "math")
            timeout_seconds: Timeout per problem in seconds
            checkpoint_interval: Save checkpoint every N problems
            results_dir: Directory for final results
            checkpoints_dir: Directory for checkpoint files
        """
        self.name = name
        self.timeout_seconds = timeout_seconds
        self.checkpoint_interval = checkpoint_interval
        self.results_dir = Path(results_dir)
        self.checkpoints_dir = Path(checkpoints_dir)
        self.results: List[BenchmarkResult] = []

        # Ensure directories exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

        # Initialize solver (to be set by subclasses)
        self.solver = None

    @abstractmethod
    def load_problems(self) -> List[Dict[str, Any]]:
        """
        Load problems from dataset.

        Returns:
            List of problem dictionaries with at minimum:
            - 'problem_id': unique identifier
            - 'problem_text': problem statement
            - 'expected_answer': correct answer
        """
        pass

    @abstractmethod
    def extract_answer(self, raw_answer: Any) -> str:
        """
        Extract answer from dataset-specific format.

        Args:
            raw_answer: Raw answer from dataset

        Returns:
            Standardized answer string
        """
        pass

    @abstractmethod
    def compare_answers(self, system_answer: str, expected_answer: str) -> bool:
        """
        Compare system answer with expected answer.

        Args:
            system_answer: Answer from solver
            expected_answer: Correct answer from dataset

        Returns:
            True if answers match, False otherwise
        """
        pass

    def solve_problem(self, problem: Dict[str, Any]) -> BenchmarkResult:
        """
        Solve a single problem with timeout and error handling.

        Args:
            problem: Problem dictionary from load_problems()

        Returns:
            BenchmarkResult with status and timing
        """
        problem_id = problem['problem_id']
        problem_text = problem['problem_text']
        expected_answer = self.extract_answer(problem.get('expected_answer', ''))

        start_time = time.time()

        try:
            # Solve with timeout
            from symbo_agentic_reasoners.core.solver_engine import get_solver_engine
            if self.solver is None:
                self.solver = get_solver_engine()

            # Execute with timeout (simplified - full implementation would use threading/multiprocessing)
            result = self.solver.solve(problem_text)
            elapsed = time.time() - start_time

            # Check for timeout
            if elapsed > self.timeout_seconds:
                return BenchmarkResult(
                    problem_id=problem_id,
                    problem_text=problem_text,
                    expected_answer=expected_answer,
                    system_answer=None,
                    status=BenchmarkStatus.TIMEOUT,
                    time_seconds=elapsed,
                    error_message=f"Exceeded timeout of {self.timeout_seconds}s"
                )

            # Extract system answer
            system_answer = result.result if hasattr(result, 'result') else str(result)

            # Compare answers
            is_correct = self.compare_answers(system_answer, expected_answer)

            return BenchmarkResult(
                problem_id=problem_id,
                problem_text=problem_text,
                expected_answer=expected_answer,
                system_answer=system_answer,
                status=BenchmarkStatus.CORRECT if is_correct else BenchmarkStatus.INCORRECT,
                time_seconds=elapsed,
                specialist_used=getattr(result, 'specialist_used', None),
                domain=getattr(result, 'domain', None),
                category=problem.get('category'),
                difficulty=problem.get('difficulty'),
                metadata=problem.get('metadata', {})
            )

        except TimeoutError:
            return BenchmarkResult(
                problem_id=problem_id,
                problem_text=problem_text,
                expected_answer=expected_answer,
                system_answer=None,
                status=BenchmarkStatus.TIMEOUT,
                time_seconds=time.time() - start_time,
                error_message="Timeout"
            )

        except Exception as e:
            logger.error(f"Error solving {problem_id}: {e}", exc_info=True)
            return BenchmarkResult(
                problem_id=problem_id,
                problem_text=problem_text,
                expected_answer=expected_answer,
                system_answer=None,
                status=BenchmarkStatus.ERROR,
                time_seconds=time.time() - start_time,
                error_message=str(e)
            )

    def run(
        self,
        limit: Optional[int] = None,
        resume: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[BenchmarkResult]:
        """
        Run the full benchmark suite.

        Args:
            limit: Maximum number of problems to solve (None for all)
            resume: Whether to resume from checkpoint if available
            progress_callback: Optional callback function(current, total)

        Returns:
            List of BenchmarkResult objects
        """
        # Load problems
        logger.info(f"Loading {self.name} problems...")
        problems = self.load_problems()

        if limit:
            problems = problems[:limit]

        total = len(problems)
        logger.info(f"Total problems: {total}")

        # Check for checkpoint
        checkpoint_file = self.checkpoints_dir / f"{self.name}_checkpoint.json"
        start_idx = 0

        if resume and checkpoint_file.exists():
            logger.info("Resuming from checkpoint...")
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
                self.results = [BenchmarkResult(**r) for r in checkpoint_data['results']]
                start_idx = len(self.results)
                logger.info(f"Resuming from problem {start_idx}")

        # Execute problems
        for i in range(start_idx, total):
            problem = problems[i]

            # Progress update
            if progress_callback:
                progress_callback(i + 1, total)

            logger.info(f"[{i+1}/{total}] Solving {problem['problem_id']}...")

            # Solve problem
            result = self.solve_problem(problem)
            self.results.append(result)

            # Log result
            logger.info(f"  Status: {result.status.value}, Time: {result.time_seconds:.2f}s")

            # Checkpoint
            if (i + 1) % self.checkpoint_interval == 0:
                self.save_checkpoint()
                logger.info(f"Checkpoint saved at problem {i+1}")

        # Final save
        self.save_results()
        logger.info(f"Benchmark complete! Results saved to {self.results_dir}")

        return self.results

    def save_checkpoint(self):
        """Save progress checkpoint"""
        checkpoint_file = self.checkpoints_dir / f"{self.name}_checkpoint.json"
        checkpoint_data = {
            'benchmark': self.name,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'problems_completed': len(self.results),
            'results': [r.to_dict() for r in self.results]
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

    def save_results(self):
        """Save final results to JSON file"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        results_file = self.results_dir / f"{self.name}_{timestamp}.json"

        results_data = {
            'benchmark': self.name,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_problems': len(self.results),
            'results': [r.to_dict() for r in self.results],
            'summary': self.generate_summary().to_dict()
        }

        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)

        logger.info(f"Results saved to: {results_file}")

    def generate_summary(self) -> BenchmarkSummary:
        """Generate aggregate statistics"""
        if not self.results:
            raise ValueError("No results to summarize")

        # Count by status
        status_counts = {status: 0 for status in BenchmarkStatus}
        for result in self.results:
            status_counts[result.status] += 1

        # Time statistics
        times = [r.time_seconds for r in self.results if r.time_seconds > 0]
        times_sorted = sorted(times)

        mean_time = sum(times) / len(times) if times else 0
        median_time = times_sorted[len(times_sorted) // 2] if times else 0
        p95_time = times_sorted[int(len(times_sorted) * 0.95)] if times else 0
        total_time = sum(times)

        # Accuracy
        correct = status_counts[BenchmarkStatus.CORRECT]
        total = len(self.results)
        accuracy = (correct / total * 100) if total > 0 else 0

        # By category
        by_category = {}
        for result in self.results:
            category = result.category or 'unknown'
            if category not in by_category:
                by_category[category] = {
                    'total': 0,
                    'correct': 0,
                    'incorrect': 0,
                    'timeout': 0,
                    'error': 0
                }

            by_category[category]['total'] += 1
            if result.status == BenchmarkStatus.CORRECT:
                by_category[category]['correct'] += 1
            elif result.status == BenchmarkStatus.INCORRECT:
                by_category[category]['incorrect'] += 1
            elif result.status == BenchmarkStatus.TIMEOUT:
                by_category[category]['timeout'] += 1
            elif result.status == BenchmarkStatus.ERROR:
                by_category[category]['error'] += 1

        # Calculate accuracy per category
        for category in by_category:
            total_cat = by_category[category]['total']
            correct_cat = by_category[category]['correct']
            by_category[category]['accuracy'] = (correct_cat / total_cat * 100) if total_cat > 0 else 0

        return BenchmarkSummary(
            benchmark_name=self.name,
            total_problems=total,
            correct=status_counts[BenchmarkStatus.CORRECT],
            incorrect=status_counts[BenchmarkStatus.INCORRECT],
            timeout=status_counts[BenchmarkStatus.TIMEOUT],
            error=status_counts[BenchmarkStatus.ERROR],
            parse_failure=status_counts[BenchmarkStatus.PARSE_FAILURE],
            skipped=status_counts[BenchmarkStatus.SKIP],
            accuracy=accuracy,
            mean_time_seconds=mean_time,
            median_time_seconds=median_time,
            p95_time_seconds=p95_time,
            total_time_seconds=total_time,
            by_category=by_category,
            start_time=self.results[0].metadata.get('start_time', '') if self.results else '',
            end_time=time.strftime('%Y-%m-%d %H:%M:%S')
        )

    def print_summary(self):
        """Print summary statistics to console"""
        summary = self.generate_summary()

        print(f"\n{'='*70}")
        print(f"{summary.benchmark_name.upper()} BENCHMARK SUMMARY")
        print(f"{'='*70}")
        print(f"Total Problems: {summary.total_problems}")
        print(f"Correct:        {summary.correct} ({summary.accuracy:.2f}%)")
        print(f"Incorrect:      {summary.incorrect}")
        print(f"Timeout:        {summary.timeout}")
        print(f"Error:          {summary.error}")
        print(f"Parse Failure:  {summary.parse_failure}")
        print(f"")
        print(f"Time Statistics:")
        print(f"  Mean:    {summary.mean_time_seconds:.2f}s")
        print(f"  Median:  {summary.median_time_seconds:.2f}s")
        print(f"  P95:     {summary.p95_time_seconds:.2f}s")
        print(f"  Total:   {summary.total_time_seconds/3600:.2f} hours")
        print(f"")
        print(f"By Category:")
        for category, stats in summary.by_category.items():
            print(f"  {category:20s}: {stats['correct']:4d}/{stats['total']:4d} ({stats['accuracy']:.1f}%)")
        print(f"{'='*70}\n")
