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
AIME Benchmark Runner

American Invitational Mathematics Examination (AIME) problems.
Contains 60 problems from 2024 and 2025 (30 each year: AIME I + AIME II).

Note: AIME problems must be manually collected from Art of Problem Solving (AoPS)
or other sources as there is no public HuggingFace dataset.

Dataset format: JSON files in data/benchmarks/aime/
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging

from .base_benchmark import BaseBenchmark, BenchmarkResult
from .answer_extractors import extract_aime_answer
from .answer_comparators import compare_numeric_answers

logger = logging.getLogger(__name__)


class AIMEBenchmark(BaseBenchmark):
    """
    AIME (American Invitational Mathematics Examination) benchmark runner.

    Dataset characteristics:
    - 60 total problems (AIME 2024 I/II + AIME 2025 I/II)
    - Answer type: Integers from 0 to 999
    - Difficulty: Very high (competition mathematics)
    - Topics: Algebra, geometry, number theory, combinatorics
    """

    def __init__(
        self,
        data_dir: str = "data/benchmarks/aime",
        years: Optional[List[int]] = None,
        **kwargs
    ):
        """
        Initialize AIME benchmark.

        Args:
            data_dir: Directory containing AIME problem JSON files
            years: List of years to include (None for all available)
            **kwargs: Additional arguments for BaseBenchmark
        """
        super().__init__(name="aime", timeout_seconds=60, **kwargs)
        self.data_dir = Path(data_dir)
        self.years = years or [2024, 2025]

    def load_problems(self) -> List[Dict[str, Any]]:
        """
        Load AIME problems from JSON files.

        Expected JSON format:
        {
          "problems": [
            {
              "id": "AIME_2024_I_1",
              "year": 2024,
              "exam": "AIME I",
              "number": 1,
              "problem": "Problem text...",
              "answer": 123,
              "topics": ["combinatorics", "number_theory"],
              "difficulty": "medium"
            },
            ...
          ]
        }

        Returns:
            List of problem dictionaries
        """
        logger.info(f"Loading AIME problems from {self.data_dir}...")

        problems = []

        for year in self.years:
            problem_file = self.data_dir / f"aime_{year}.json"

            if not problem_file.exists():
                logger.warning(f"AIME {year} file not found: {problem_file}")
                logger.warning(
                    f"Please create {problem_file} with AIME problems. "
                    f"Problems can be collected from https://artofproblemsolving.com/wiki/index.php/AIME_Problems_and_Solutions"
                )
                continue

            try:
                with open(problem_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                year_problems = data.get('problems', [])
                logger.info(f"Loaded {len(year_problems)} problems from AIME {year}")

                # Convert to standard format
                for p in year_problems:
                    problems.append({
                        'problem_id': p.get('id', f"AIME_{year}_{p.get('number', 0)}"),
                        'problem_text': p['problem'],
                        'expected_answer': p['answer'],
                        'category': 'aime_' + p.get('exam', 'unknown').replace(' ', '_').lower(),
                        'difficulty': 9,  # AIME is always high difficulty
                        'metadata': {
                            'dataset': 'aime',
                            'year': p.get('year', year),
                            'exam': p.get('exam', 'Unknown'),
                            'number': p.get('number', 0),
                            'topics': p.get('topics', []),
                            'source_difficulty': p.get('difficulty', 'unknown')
                        }
                    })

            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error loading {problem_file}: {e}")
                continue

        if not problems:
            logger.error(
                "No AIME problems loaded! Please create problem files in "
                f"{self.data_dir}/ with format: aime_YEAR.json"
            )
            raise FileNotFoundError(f"No AIME problem files found in {self.data_dir}")

        logger.info(f"Total AIME problems loaded: {len(problems)}")
        return problems

    def extract_answer(self, raw_answer: Any) -> str:
        """
        Extract integer answer from AIME format.

        Args:
            raw_answer: Answer (integer 0-999 or string)

        Returns:
            Integer answer as string
        """
        return extract_aime_answer(raw_answer)

    def compare_answers(self, system_answer: str, expected_answer: str) -> bool:
        """
        Compare answers using exact integer matching.

        Args:
            system_answer: Answer from solver
            expected_answer: Expected answer (0-999)

        Returns:
            True if answers match exactly
        """
        # Extract expected answer
        expected = self.extract_answer(expected_answer)

        # AIME answers must match exactly (integers 0-999)
        # Use numeric comparison with zero tolerance
        is_correct, explanation = compare_numeric_answers(
            system_answer,
            expected,
            tolerance=0.0  # Exact match required
        )

        if not is_correct:
            logger.debug(f"Answer mismatch: {explanation}")
            logger.debug(f"  System: {system_answer}")
            logger.debug(f"  Expected: {expected}")

        return is_correct


def run_aime_benchmark(
    years: Optional[List[int]] = None,
    limit: Optional[int] = None,
    resume: bool = True,
    **kwargs
) -> List[BenchmarkResult]:
    """
    Convenience function to run AIME benchmark.

    Args:
        years: List of years to include (None for all)
        limit: Maximum number of problems (None for all)
        **kwargs: Additional arguments

    Returns:
        List of BenchmarkResult objects

    Examples:
        # Run all AIME problems (2024 + 2025)
        results = run_aime_benchmark()

        # Run only 2024 problems
        results = run_aime_benchmark(years=[2024])

        # Run first 10 problems
        results = run_aime_benchmark(limit=10)
    """
    benchmark = AIMEBenchmark(years=years, **kwargs)
    results = benchmark.run(limit=limit, resume=resume)
    benchmark.print_summary()
    return results


def create_aime_template(year: int, output_dir: str = "data/benchmarks/aime"):
    """
    Create a template JSON file for AIME problems.

    Args:
        year: Year for template (e.g., 2024)
        output_dir: Output directory

    Creates a template file with example structure for manual problem entry.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template = {
        "year": year,
        "description": f"AIME {year} Problems (I and II)",
        "problems": [
            {
                "id": f"AIME_{year}_I_1",
                "year": year,
                "exam": "AIME I",
                "number": 1,
                "problem": "Problem text goes here...",
                "answer": 123,
                "topics": ["combinatorics", "number_theory"],
                "difficulty": "medium",
                "source": "https://artofproblemsolving.com/wiki/index.php/..."
            },
            # Add more problems...
        ]
    }

    output_file = output_dir / f"aime_{year}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2)

    logger.info(f"Created template file: {output_file}")
    logger.info(
        f"Please fill in problems from: "
        f"https://artofproblemsolving.com/wiki/index.php/{year}_AIME_I_Problems"
    )


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "create-template":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else 2024
        print(f"Creating template for AIME {year}...")
        create_aime_template(year)
    else:
        years = [int(y) for y in sys.argv[1].split(',')] if len(sys.argv) > 1 else None
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

        print(f"Running AIME benchmark (years={years}, limit={limit})")
        results = run_aime_benchmark(years=years, limit=limit)
        print(f"\nCompleted {len(results)} problems")
