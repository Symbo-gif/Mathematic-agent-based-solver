"""
ODE Test Suite Benchmark Runner

Comprehensive ODE (Ordinary Differential Equation) test suite.
Total: 52,000 problems (500 existing + 51,500 synthetic)

Dataset: Hybrid approach
- Existing problems from Kamke's Handbook, textbooks
- Synthetically generated across ODE types
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import glob
import logging

from .base_benchmark import BaseBenchmark, BenchmarkResult
from .answer_extractors import extract_numeric_answer
from .answer_comparators import compare_answers, compare_ode_solutions

logger = logging.getLogger(__name__)


class ODEBenchmark(BaseBenchmark):
    """
    ODE Test Suite benchmark runner.

    Dataset characteristics:
    - 52,000 total problems (500 existing + 51,500 synthetic)
    - Categories: First-order (linear, separable, exact, Bernoulli),
      Second-order (constant/variable coefficients),
      Systems, Boundary value, Initial value
    - Answer type: Symbolic expressions or numeric values
    """

    def __init__(
        self,
        data_dir: str = "data/benchmarks/odes",
        use_existing: bool = True,
        use_synthetic: bool = True,
        **kwargs
    ):
        """
        Initialize ODE benchmark.

        Args:
            data_dir: Directory containing ODE problem files
            use_existing: Include existing problems from literature
            use_synthetic: Include synthetically generated problems
            **kwargs: Additional arguments for BaseBenchmark
        """
        super().__init__(name="ode_suite", timeout_seconds=15, **kwargs)
        self.data_dir = Path(data_dir)
        self.use_existing = use_existing
        self.use_synthetic = use_synthetic

    def load_problems(self) -> List[Dict[str, Any]]:
        """
        Load ODE problems from JSON files.

        Returns:
            List of problem dictionaries
        """
        logger.info(f"Loading ODE problems from {self.data_dir}...")

        problems = []

        # Load existing problems
        if self.use_existing:
            existing_file = self.data_dir / "existing_odes.json"
            if existing_file.exists():
                with open(existing_file, 'r') as f:
                    data = json.load(f)
                    existing_problems = data.get('problems', [])
                    logger.info(f"Loaded {len(existing_problems)} existing ODE problems")
                    problems.extend(self._standardize_problems(existing_problems, 'existing'))
            else:
                logger.warning(f"Existing ODE file not found: {existing_file}")

        # Load synthetic problems (may be split across multiple files)
        if self.use_synthetic:
            synthetic_files = glob.glob(str(self.data_dir / "synthetic_odes_*.json"))

            for file_path in synthetic_files:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    synthetic_problems = data.get('problems', [])
                    problems.extend(self._standardize_problems(synthetic_problems, 'synthetic'))

            logger.info(f"Loaded {len([p for p in problems if 'synthetic' in p['problem_id']])} synthetic ODE problems")

        if not problems:
            logger.error(
                f"No ODE problems loaded! Run scripts/generate_ode_test_suite.py first "
                f"to create problem files in {self.data_dir}/"
            )
            raise FileNotFoundError(f"No ODE problem files found in {self.data_dir}")

        logger.info(f"Total ODE problems loaded: {len(problems)}")
        return problems

    def _standardize_problems(
        self,
        problems_data: List[Dict],
        source: str
    ) -> List[Dict[str, Any]]:
        """Convert problem data to standard format"""
        standardized = []

        for idx, p in enumerate(problems_data):
            standardized.append({
                'problem_id': p.get('id', f"ode_{source}_{idx:05d}"),
                'problem_text': p['equation'],
                'expected_answer': p.get('solution', p.get('answer', '')),
                'category': p.get('type', 'unknown'),
                'difficulty': p.get('difficulty_level', 5),
                'metadata': {
                    'dataset': 'ode_suite',
                    'source': source,
                    'initial_conditions': p.get('initial_conditions'),
                    'boundary_conditions': p.get('boundary_conditions'),
                    'ode_order': p.get('order', 1),
                    'ode_type': p.get('type', 'unknown')
                }
            })

        return standardized

    def extract_answer(self, raw_answer: Any) -> str:
        """Extract answer from ODE solution"""
        return str(raw_answer).strip()

    def compare_answers(self, system_answer: str, expected_answer: str) -> bool:
        """
        Compare ODE solutions using ODE-specific strategies.

        ODEs can have:
        - General solutions with constants (C, C1, C2)
        - Symbolic solutions (compare symbolically)
        - Numeric solutions (compare numerically)

        Args:
            system_answer: Answer from solver
            expected_answer: Expected solution

        Returns:
            True if answers match
        """
        # Use ODE-specific comparison first
        is_correct, explanation = compare_ode_solutions(
            system_answer,
            expected_answer
        )

        if not is_correct:
            logger.debug(f"ODE solution mismatch: {explanation}")
            logger.debug(f"  System: {system_answer}")
            logger.debug(f"  Expected: {expected_answer}")

        return is_correct


def run_ode_benchmark(
    use_existing: bool = True,
    use_synthetic: bool = True,
    limit: Optional[int] = None,
    resume: bool = True,
    **kwargs
) -> List[BenchmarkResult]:
    """
    Convenience function to run ODE benchmark.

    Args:
        use_existing: Include existing problems
        use_synthetic: Include synthetic problems
        limit: Maximum number of problems (None for all)
        resume: Resume from checkpoint if available
        **kwargs: Additional arguments

    Returns:
        List of BenchmarkResult objects

    Examples:
        # Run 1000 synthetic problems
        results = run_ode_benchmark(use_existing=False, limit=1000)

        # Run all problems
        results = run_ode_benchmark()
    """
    benchmark = ODEBenchmark(
        use_existing=use_existing,
        use_synthetic=use_synthetic,
        **kwargs
    )
    results = benchmark.run(limit=limit, resume=resume)
    benchmark.print_summary()
    return results


if __name__ == "__main__":
    # Example usage
    import sys

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    print(f"Running ODE benchmark (limit={limit})")
    results = run_ode_benchmark(limit=limit)
    print(f"\nCompleted {len(results)} problems")
