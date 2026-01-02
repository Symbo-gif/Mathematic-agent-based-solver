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
GSM8K Benchmark Runner

Grade School Math 8K dataset from OpenAI.
Contains 8,792 grade school math word problems (7,473 train + 1,319 test).

Dataset: https://huggingface.co/datasets/openai/gsm8k
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .base_benchmark import BaseBenchmark, BenchmarkResult
from .answer_extractors import extract_gsm8k_answer
from .answer_comparators import compare_numeric_answers

logger = logging.getLogger(__name__)


class GSM8KBenchmark(BaseBenchmark):
    """
    GSM8K (Grade School Math 8K) benchmark runner.

    Dataset characteristics:
    - 8,792 total problems (7,473 train + 1,319 test)
    - Natural language word problems
    - Answers format: "...reasoning... #### ANSWER"
    - Answer type: Numeric (integers and decimals)
    """

    def __init__(
        self,
        split: str = "test",
        cache_dir: str = "data/benchmarks/.cache",
        **kwargs
    ):
        """
        Initialize GSM8K benchmark.

        Args:
            split: Dataset split ("train", "test", or "all")
            cache_dir: Directory for caching downloaded dataset
            **kwargs: Additional arguments for BaseBenchmark
        """
        super().__init__(name="gsm8k", timeout_seconds=20, **kwargs)
        self.split = split
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.dataset = None

    def load_problems(self) -> List[Dict[str, Any]]:
        """
        Load GSM8K problems from HuggingFace datasets.

        Returns:
            List of problem dictionaries with:
            - problem_id: Unique identifier
            - problem_text: Question text
            - expected_answer: Answer with #### format
            - category: "word_problem"
        """
        logger.info(f"Loading GSM8K dataset (split={self.split})...")

        try:
            from datasets import load_dataset

            # Load dataset
            dataset = load_dataset(
                'openai/gsm8k',
                'main',
                cache_dir=str(self.cache_dir),
                trust_remote_code=False
            )

            # Select split
            if self.split == "all":
                problems_data = list(dataset['train']) + list(dataset['test'])
            else:
                problems_data = list(dataset[self.split])

            logger.info(f"Loaded {len(problems_data)} problems from GSM8K {self.split} split")

            # Convert to standard format
            problems = []
            for idx, item in enumerate(problems_data):
                problems.append({
                    'problem_id': f"gsm8k_{self.split}_{idx:04d}",
                    'problem_text': item['question'],
                    'expected_answer': item['answer'],
                    'category': 'word_problem',
                    'metadata': {
                        'dataset': 'gsm8k',
                        'split': self.split,
                        'index': idx
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
            logger.error(f"Failed to load GSM8K dataset: {e}")
            raise

    def extract_answer(self, raw_answer: Any) -> str:
        """
        Extract numeric answer from GSM8K format.

        Args:
            raw_answer: Answer string with #### separator

        Returns:
            Extracted numeric answer
        """
        return extract_gsm8k_answer(str(raw_answer))

    def compare_answers(self, system_answer: str, expected_answer: str) -> bool:
        """
        Compare answers using numeric comparison.

        Args:
            system_answer: Answer from solver
            expected_answer: Expected answer from dataset

        Returns:
            True if answers match within tolerance
        """
        # Extract expected answer from #### format
        expected = self.extract_answer(expected_answer)

        # Compare numerically
        is_correct, explanation = compare_numeric_answers(
            system_answer,
            expected,
            tolerance=1e-6
        )

        if not is_correct:
            logger.debug(f"Answer mismatch: {explanation}")
            logger.debug(f"  System: {system_answer}")
            logger.debug(f"  Expected: {expected}")

        return is_correct


def run_gsm8k_benchmark(
    split: str = "test",
    limit: Optional[int] = None,
    resume: bool = True,
    **kwargs
) -> List[BenchmarkResult]:
    """
    Convenience function to run GSM8K benchmark.

    Args:
        split: Dataset split ("train", "test", or "all")
        limit: Maximum number of problems (None for all)
        **kwargs: Additional arguments

    Returns:
        List of BenchmarkResult objects

    Examples:
        # Run on 100 test problems
        results = run_gsm8k_benchmark(split="test", limit=100)

        # Run on full test set
        results = run_gsm8k_benchmark(split="test")

        # Run on all 8,792 problems
        results = run_gsm8k_benchmark(split="all")
    """
    benchmark = GSM8KBenchmark(split=split, **kwargs)
    results = benchmark.run(limit=limit, resume=resume)
    benchmark.print_summary()
    return results


if __name__ == "__main__":
    # Example usage
    import sys

    split = sys.argv[1] if len(sys.argv) > 1 else "test"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    print(f"Running GSM8K benchmark on {split} split (limit={limit})")
    results = run_gsm8k_benchmark(split=split, limit=limit)
    print(f"\nCompleted {len(results)} problems")
