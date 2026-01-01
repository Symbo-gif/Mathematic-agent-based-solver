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
GSM8K Benchmark Runner Script

Standalone script to run GSM8K benchmark.

Usage:
    python scripts/run_gsm8k.py                    # Run full test set
    python scripts/run_gsm8k.py --limit 100        # Run first 100 problems
    python scripts/run_gsm8k.py --split train      # Run on training set
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.benchmarks.gsm8k_benchmark import run_gsm8k_benchmark


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run GSM8K benchmark")
    parser.add_argument('--split', default='test', choices=['train', 'test', 'all'],
                       help="Dataset split")
    parser.add_argument('--limit', type=int, help="Limit number of problems")
    parser.add_argument('--no-resume', action='store_true',
                       help="Don't resume from checkpoint")

    args = parser.parse_args()

    print(f"Running GSM8K benchmark (split={args.split}, limit={args.limit})")
    print("="*80)

    results = run_gsm8k_benchmark(
        split=args.split,
        limit=args.limit,
        resume=not args.no_resume
    )

    print(f"\nCompleted {len(results)} problems")
    print(f"Results saved to: data/benchmarks/results/")


if __name__ == "__main__":
    main()
