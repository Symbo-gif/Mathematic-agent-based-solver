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
University-Level Mathematics Benchmark Runner

Comprehensive university mathematics benchmark spanning undergraduate through
graduate level problems across 35 mathematical domains.

Total: 1,000 problems (400 undergraduate, 400 graduate, 200 advanced/research)
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging

from .base_benchmark import BaseBenchmark, BenchmarkResult
from .answer_comparators import compare_answers

logger = logging.getLogger(__name__)


class UniversityBenchmark(BaseBenchmark):
    """
    University-Level Mathematics benchmark runner.

    Dataset characteristics:
    - 1,000 total problems
    - 3 tiers: Undergraduate (300-400 level), Graduate (500-600), Advanced (700+)
    - 35 domains: Abstract algebra, topology, analysis, number theory, geometry, etc.
    - Answer types: Proofs, computations, constructions, counterexamples
    - Verification: Ax-Prover for formal proofs, symbolic/numeric for computations
    """

    TIERS = [
        "undergraduate_300",  # 300-400 level
        "graduate_500",       # 500-600 level
        "advanced_700"        # 700+ level, research-adjacent
    ]

    DOMAINS = [
        "abstract_algebra", "real_analysis", "complex_analysis", "topology",
        "number_theory", "geometry", "logic", "discrete_math",
        "category_theory", "stochastic_processes", "functional_analysis",
        # ... (35 total domains)
    ]

    def __init__(
        self,
        data_dir: str = "data/benchmarks/university",
        tier_filter: Optional[str] = None,
        domain_filter: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize University benchmark.

        Args:
            data_dir: Directory containing university problem files
            tier_filter: Filter by tier ("undergraduate_300", "graduate_500", "advanced_700")
            domain_filter: Filter by domain (e.g., "abstract_algebra")
            **kwargs: Additional arguments for BaseBenchmark
        """
        super().__init__(name="university", timeout_seconds=120, **kwargs)
        self.data_dir = Path(data_dir)
        self.tier_filter = tier_filter
        self.domain_filter = domain_filter

    def load_problems(self) -> List[Dict[str, Any]]:
        """
        Load university problems from JSON files.

        Expected JSON format:
        {
          "problems": [
            {
              "problem_id": "UNIV_ALG_001",
              "tier": "undergraduate_300",
              "domain": "abstract_algebra",
              "subdomain": "group_theory",
              "difficulty": 7,
              "problem_text": "Prove that...",
              "solution_type": "proof",
              "correct_answer": "proof text or symbolic answer",
              "verification_method": "ax_prover",
              "source": "Dummit_Foote_3ed_p145_ex23",
              "prerequisites": ["sylow_theorems"],
              "estimated_time_minutes": 20
            },
            ...
          ]
        }

        Returns:
            List of problem dictionaries
        """
        logger.info(f"Loading university problems from {self.data_dir}...")

        problem_file = self.data_dir / "university_problems_v1.json"

        if not problem_file.exists():
            logger.error(
                f"University problems file not found: {problem_file}\n"
                f"This file needs to be manually curated from textbooks, "
                f"qualifying exams, and competition problems."
            )
            raise FileNotFoundError(f"University problem file not found: {problem_file}")

        with open(problem_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        problems_data = data.get('problems', [])
        logger.info(f"Loaded {len(problems_data)} university problems")

        # Filter by tier and domain
        if self.tier_filter:
            problems_data = [p for p in problems_data if p.get('tier') == self.tier_filter]
            logger.info(f"Filtered to {len(problems_data)} problems in tier {self.tier_filter}")

        if self.domain_filter:
            problems_data = [p for p in problems_data if p.get('domain') == self.domain_filter]
            logger.info(f"Filtered to {len(problems_data)} problems in domain {self.domain_filter}")

        # Convert to standard format
        problems = []
        for p in problems_data:
            problems.append({
                'problem_id': p['problem_id'],
                'problem_text': p['problem_text'],
                'expected_answer': p['correct_answer'],
                'category': f"{p['domain']}_{p.get('subdomain', 'general')}",
                'difficulty': p.get('difficulty', 7),
                'metadata': {
                    'dataset': 'university',
                    'tier': p.get('tier', 'unknown'),
                    'domain': p.get('domain', 'unknown'),
                    'subdomain': p.get('subdomain', 'unknown'),
                    'solution_type': p.get('solution_type', 'computation'),
                    'verification_method': p.get('verification_method', 'symbolic'),
                    'source': p.get('source', 'unknown'),
                    'prerequisites': p.get('prerequisites', []),
                    'estimated_time_minutes': p.get('estimated_time_minutes', 20)
                }
            })

        logger.info(f"Total university problems loaded: {len(problems)}")
        return problems

    def extract_answer(self, raw_answer: Any) -> str:
        """Extract answer from university problem format"""
        return str(raw_answer).strip()

    def compare_answers(self, system_answer: str, expected_answer: str) -> bool:
        """
        Compare answers using verification method from metadata.

        For proofs: Use Ax-Prover if available
        For computations: Use symbolic/numeric comparison

        Args:
            system_answer: Answer from solver
            expected_answer: Expected answer

        Returns:
            True if answers match
        """
        # Use auto strategy (comprehensive comparison)
        is_correct, explanation = compare_answers(
            system_answer,
            expected_answer,
            comparison_strategy="auto"
        )

        if not is_correct:
            logger.debug(f"University problem answer mismatch: {explanation}")
            logger.debug(f"  System: {system_answer}")
            logger.debug(f"  Expected: {expected_answer}")

        return is_correct


def run_university_benchmark(
    tier: Optional[str] = None,
    domain: Optional[str] = None,
    limit: Optional[int] = None,
    resume: bool = True,
    **kwargs
) -> List[BenchmarkResult]:
    """
    Convenience function to run University benchmark.

    Args:
        tier: Filter by tier ("undergraduate_300", "graduate_500", "advanced_700")
        domain: Filter by domain (e.g., "abstract_algebra")
        limit: Maximum number of problems (None for all)
        **kwargs: Additional arguments

    Returns:
        List of BenchmarkResult objects

    Examples:
        # Run all problems
        results = run_university_benchmark()

        # Run only undergraduate problems
        results = run_university_benchmark(tier="undergraduate_300")

        # Run abstract algebra problems
        results = run_university_benchmark(domain="abstract_algebra")

        # Run first 100 graduate problems
        results = run_university_benchmark(tier="graduate_500", limit=100)
    """
    benchmark = UniversityBenchmark(
        tier_filter=tier,
        domain_filter=domain,
        **kwargs
    )
    results = benchmark.run(limit=limit, resume=resume)
    benchmark.print_summary()
    return results


if __name__ == "__main__":
    # Example usage
    import sys

    tier = sys.argv[1] if len(sys.argv) > 1 else None
    domain = sys.argv[2] if len(sys.argv) > 2 else None
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None

    print(f"Running University benchmark (tier={tier}, domain={domain}, limit={limit})")
    results = run_university_benchmark(tier=tier, domain=domain, limit=limit)
    print(f"\nCompleted {len(results)} problems")
