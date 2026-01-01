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
MATH Benchmark Runner

MATH dataset from Dan Hendrycks (competition mathematics).
Contains 12,500 problems across 7 categories.

Dataset: https://huggingface.co/datasets/hendrycks/competition_math
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .base_benchmark import BaseBenchmark, BenchmarkResult
from .answer_extractors import extract_math_boxed_answer
from .answer_comparators import compare_answers

logger = logging.getLogger(__name__)


class MATHBenchmark(BaseBenchmark):
    """
    MATH (Mathematics Aptitude Test of Heuristics) benchmark runner.

    Dataset characteristics:
    - 12,500 total problems (7,500 train + 5,000 test)
    - 7 categories: Algebra, Counting & Probability, Geometry, Intermediate Algebra,
      Number Theory, Prealgebra, Precalculus
    - 5 difficulty levels (1-5)
    - Answers format: LaTeX with \\boxed{} command
    """

    CATEGORIES = [
        "Algebra",
        "Counting & Probability",
        "Geometry",
        "Intermediate Algebra",
        "Number Theory",
        "Prealgebra",
        "Precalculus"
    ]

    def __init__(
        self,
        split: str = "test",
        category_filter: Optional[str] = None,
        cache_dir: str = "data/benchmarks/.cache",
        **kwargs
    ):
        """
        Initialize MATH benchmark.

        Args:
            split: Dataset split ("train", "test")
            category_filter: Filter by category (None for all)
            cache_dir: Directory for caching downloaded dataset
            **kwargs: Additional arguments for BaseBenchmark
        """
        super().__init__(name="math", timeout_seconds=30, **kwargs)
        self.split = split
        self.category_filter = category_filter
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_problems(self) -> List[Dict[str, Any]]:
        """
        Load MATH problems from HuggingFace datasets.

        Returns:
            List of problem dictionaries with:
            - problem_id: Unique identifier
            - problem_text: Problem statement (may contain LaTeX)
            - expected_answer: Solution text with \\boxed{} answer
            - category: One of 7 MATH categories
            - difficulty: Level 1-5
        """
        logger.info(f"Loading MATH dataset (split={self.split}, category={self.category_filter})...")

        try:
            from datasets import load_dataset

            # Load dataset
            # Try multiple possible dataset names
            dataset_names = [
                'lighteval/MATH',
                'hendrycks_math',
                'competition_math',
                'hendrycks/competition_math'
            ]

            dataset = None
            last_error = None
            for dataset_name in dataset_names:
                try:
                    dataset = load_dataset(
                        dataset_name,
                        cache_dir=str(self.cache_dir),
                        trust_remote_code=False
                    )
                    logger.info(f"Successfully loaded dataset: {dataset_name}")
                    break
                except Exception as e:
                    last_error = e
                    continue

            if dataset is None:
                raise RuntimeError(
                    f"Could not load MATH dataset. Tried: {dataset_names}. "
                    f"Last error: {last_error}"
                )

            # Select split
            problems_data = list(dataset[self.split])

            # Filter by category if specified
            if self.category_filter:
                problems_data = [
                    p for p in problems_data
                    if p['type'] == self.category_filter
                ]

            logger.info(f"Loaded {len(problems_data)} problems from MATH {self.split} split")

            # Convert to standard format
            problems = []
            for idx, item in enumerate(problems_data):
                problems.append({
                    'problem_id': f"math_{self.split}_{idx:04d}",
                    'problem_text': item['problem'],
                    'expected_answer': item['solution'],
                    'category': item['type'],
                    'difficulty': int(item['level'].split()[-1]) if 'level' in item else None,
                    'metadata': {
                        'dataset': 'math',
                        'split': self.split,
                        'index': idx,
                        'level': item.get('level', 'Unknown')
                    }
                })

            return problems

        except ImportError:
            logger.error(
                "datasets library not installed. "
                "Install with: pip install datasets"
            )
            raise

        except Exception as e:
            logger.error(f"Failed to load MATH dataset: {e}")
            raise

    def extract_answer(self, raw_answer: Any) -> str:
        """
        Extract answer from MATH LaTeX format.

        Args:
            raw_answer: Solution text with \\boxed{} answer

        Returns:
            Extracted answer (content inside \\boxed{})
        """
        return extract_math_boxed_answer(str(raw_answer))

    def compare_answers(self, system_answer: str, expected_answer: str) -> bool:
        """
        Compare answers using multiple strategies.

        Args:
            system_answer: Answer from solver
            expected_answer: Expected answer from dataset

        Returns:
            True if answers match
        """
        # Extract expected answer from \\boxed{} format
        expected = self.extract_answer(expected_answer)

        # Try multiple comparison strategies (auto mode)
        is_correct, explanation = compare_answers(
            system_answer,
            expected,
            comparison_strategy="auto"
        )

        if not is_correct:
            logger.debug(f"Answer mismatch: {explanation}")
            logger.debug(f"  System: {system_answer}")
            logger.debug(f"  Expected: {expected}")

        return is_correct


def run_math_benchmark(
    split: str = "test",
    category: Optional[str] = None,
    limit: Optional[int] = None,
    resume: bool = True,
    **kwargs
) -> List[BenchmarkResult]:
    """
    Convenience function to run MATH benchmark.

    Args:
        split: Dataset split ("train", "test")
        category: Filter by category (None for all)
        limit: Maximum number of problems (None for all)
        **kwargs: Additional arguments

    Returns:
        List of BenchmarkResult objects

    Examples:
        # Run on 100 test problems (all categories)
        results = run_math_benchmark(split="test", limit=100)

        # Run on full Algebra test set
        results = run_math_benchmark(split="test", category="Algebra")

        # Run on all test problems
        results = run_math_benchmark(split="test")
    """
    benchmark = MATHBenchmark(split=split, category_filter=category, **kwargs)
    results = benchmark.run(limit=limit, resume=resume)
    benchmark.print_summary()
    return results


if __name__ == "__main__":
    # Example usage
    import sys

    split = sys.argv[1] if len(sys.argv) > 1 else "test"
    category = sys.argv[2] if len(sys.argv) > 2 else None
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    print(f"Running MATH benchmark on {split} split (category={category}, limit={limit})")
    results = run_math_benchmark(split=split, category=category, limit=limit)
    print(f"\nCompleted {len(results)} problems")
