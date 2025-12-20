"""
ODE Suite Benchmark Runner Script

Standalone script to run ODE test suite benchmark.

Usage:
    python scripts/run_ode_suite.py                    # Run all ODE problems
    python scripts/run_ode_suite.py --limit 100        # Run first 100 problems
    python scripts/run_ode_suite.py --synthetic-only   # Run only synthetic
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.benchmarks.ode_benchmark import run_ode_benchmark


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run ODE test suite benchmark")
    parser.add_argument('--limit', type=int, help="Limit number of problems")
    parser.add_argument('--existing-only', action='store_true',
                       help="Run only existing problems")
    parser.add_argument('--synthetic-only', action='store_true',
                       help="Run only synthetic problems")
    parser.add_argument('--no-resume', action='store_true',
                       help="Don't resume from checkpoint")

    args = parser.parse_args()

    use_existing = not args.synthetic_only
    use_synthetic = not args.existing_only

    print(f"Running ODE benchmark (existing={use_existing}, synthetic={use_synthetic}, limit={args.limit})")
    print("="*80)

    results = run_ode_benchmark(
        use_existing=use_existing,
        use_synthetic=use_synthetic,
        limit=args.limit,
        resume=not args.no_resume
    )

    print(f"\nCompleted {len(results)} problems")
    print(f"Results saved to: data/benchmarks/results/")


if __name__ == "__main__":
    main()
