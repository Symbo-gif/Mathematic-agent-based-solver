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
