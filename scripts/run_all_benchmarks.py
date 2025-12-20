"""
Master Benchmark Runner

Orchestrates execution of all 5 benchmark suites:
1. GSM8K: 8,792 problems
2. MATH: 12,500 problems
3. AIME: 60 problems
4. ODE Suite: 52,000 problems
5. University: 1,000 problems

Total: 74,352 problems

Estimated runtime: 6-7 days continuous execution with 4 parallel workers
"""

import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.benchmarks import (
    GSM8KBenchmark,
    MATHBenchmark,
    AIMEBenchmark,
    ODEBenchmark,
    UniversityBenchmark
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/benchmarks/execution_logs/master_benchmark.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MasterBenchmarkRunner:
    """
    Orchestrates execution of all benchmark suites.

    Features:
    - Sequential execution of all 5 benchmarks
    - Progress tracking and ETA estimation
    - Checkpoint/resume for each benchmark
    - Aggregate results collection
    - Comprehensive summary report
    """

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.end_time = None

        # Ensure log directory exists
        log_dir = Path("data/benchmarks/execution_logs")
        log_dir.mkdir(parents=True, exist_ok=True)

    def run_all(
        self,
        skip_gsm8k: bool = False,
        skip_math: bool = False,
        skip_aime: bool = False,
        skip_ode: bool = False,
        skip_university: bool = False,
        limits: Dict[str, int] = None
    ):
        """
        Run all benchmarks sequentially.

        Args:
            skip_*: Skip specific benchmarks
            limits: Dict of benchmark_name -> problem_limit
        """
        self.start_time = datetime.now()
        limits = limits or {}

        logger.info("="*80)
        logger.info("MASTER BENCHMARK EXECUTION START")
        logger.info("="*80)
        logger.info(f"Start time: {self.start_time}")
        logger.info("")

        # Benchmark execution order (sorted by estimated time)
        benchmarks = [
            ("aime", AIMEBenchmark, 60, skip_aime, "AIME 2024/2025"),
            ("gsm8k", GSM8KBenchmark, 8792, skip_gsm8k, "GSM8K Full Dataset"),
            ("math", MATHBenchmark, 12500, skip_math, "MATH Competition"),
            ("university", UniversityBenchmark, 1000, skip_university, "University Level"),
            ("ode", ODEBenchmark, 52000, skip_ode, "ODE Test Suite"),
        ]

        total_problems = sum(count for _, _, count, skip, _ in benchmarks if not skip)
        completed = 0

        for idx, (name, benchmark_class, count, skip, description) in enumerate(benchmarks, 1):
            if skip:
                logger.info(f"[{idx}/5] Skipping {description}")
                continue

            logger.info("")
            logger.info(f"{'='*80}")
            logger.info(f"[{idx}/5] Starting {description} ({name.upper()})")
            logger.info(f"{'='*80}")

            # Create benchmark instance
            if name == "gsm8k":
                benchmark = benchmark_class(split="all")  # Full dataset
            elif name == "math":
                benchmark = benchmark_class(split="test")
            else:
                benchmark = benchmark_class()

            # Run benchmark
            limit = limits.get(name)
            try:
                results = benchmark.run(limit=limit, resume=True)
                self.results[name] = {
                    'benchmark': name,
                    'description': description,
                    'results': results,
                    'summary': benchmark.generate_summary()
                }

                # Update progress
                completed += len(results)
                progress = (completed / total_problems) * 100
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = completed / elapsed if elapsed > 0 else 0
                eta_seconds = (total_problems - completed) / rate if rate > 0 else 0
                eta = datetime.now() + timedelta(seconds=eta_seconds)

                logger.info(f"Progress: {completed}/{total_problems} ({progress:.1f}%)")
                logger.info(f"Rate: {rate:.2f} problems/second")
                logger.info(f"Estimated completion: {eta}")

            except Exception as e:
                logger.error(f"Error running {name} benchmark: {e}", exc_info=True)
                self.results[name] = {
                    'benchmark': name,
                    'description': description,
                    'error': str(e)
                }

        self.end_time = datetime.now()
        self.generate_master_summary()

    def generate_master_summary(self):
        """Generate comprehensive summary across all benchmarks"""
        logger.info("")
        logger.info("="*80)
        logger.info("MASTER BENCHMARK SUMMARY")
        logger.info("="*80)
        logger.info(f"Start time: {self.start_time}")
        logger.info(f"End time: {self.end_time}")
        logger.info(f"Total duration: {self.end_time - self.start_time}")
        logger.info("")

        total_problems = 0
        total_correct = 0
        total_time = 0

        for name, data in self.results.items():
            if 'error' in data:
                logger.info(f"{name.upper()}: ERROR - {data['error']}")
                continue

            summary = data['summary']
            logger.info(f"{name.upper()}:")
            logger.info(f"  Problems:   {summary.total_problems}")
            logger.info(f"  Correct:    {summary.correct} ({summary.accuracy:.1f}%)")
            logger.info(f"  Incorrect:  {summary.incorrect}")
            logger.info(f"  Timeout:    {summary.timeout}")
            logger.info(f"  Error:      {summary.error}")
            logger.info(f"  Time:       {summary.total_time_seconds/3600:.2f} hours")
            logger.info("")

            total_problems += summary.total_problems
            total_correct += summary.correct
            total_time += summary.total_time_seconds

        # Overall statistics
        overall_accuracy = (total_correct / total_problems * 100) if total_problems > 0 else 0

        logger.info("="*80)
        logger.info("OVERALL STATISTICS")
        logger.info("="*80)
        logger.info(f"Total Problems:     {total_problems}")
        logger.info(f"Total Correct:      {total_correct}")
        logger.info(f"Overall Accuracy:   {overall_accuracy:.2f}%")
        logger.info(f"Total Execution:    {total_time/3600:.2f} hours")
        logger.info("="*80)

        # Save summary to file
        summary_file = Path("data/benchmarks/results/master_summary.txt")
        with open(summary_file, 'w') as f:
            f.write(f"Master Benchmark Summary\n")
            f.write(f"{'='*80}\n")
            f.write(f"Execution: {self.start_time} to {self.end_time}\n")
            f.write(f"Duration: {self.end_time - self.start_time}\n\n")

            for name, data in self.results.items():
                if 'error' in data:
                    f.write(f"{name.upper()}: ERROR\n")
                    continue

                summary = data['summary']
                f.write(f"{name.upper()}:\n")
                f.write(f"  Total: {summary.total_problems}\n")
                f.write(f"  Correct: {summary.correct} ({summary.accuracy:.1f}%)\n")
                f.write(f"  Time: {summary.total_time_seconds/3600:.2f} hours\n\n")

            f.write(f"\nOverall: {total_correct}/{total_problems} ({overall_accuracy:.2f}%)\n")

        logger.info(f"Summary saved to: {summary_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run all mathematical benchmarks")
    parser.add_argument('--skip-gsm8k', action='store_true', help="Skip GSM8K")
    parser.add_argument('--skip-math', action='store_true', help="Skip MATH")
    parser.add_argument('--skip-aime', action='store_true', help="Skip AIME")
    parser.add_argument('--skip-ode', action='store_true', help="Skip ODE suite")
    parser.add_argument('--skip-university', action='store_true', help="Skip University")

    parser.add_argument('--limit-gsm8k', type=int, help="Limit GSM8K problems")
    parser.add_argument('--limit-math', type=int, help="Limit MATH problems")
    parser.add_argument('--limit-aime', type=int, help="Limit AIME problems")
    parser.add_argument('--limit-ode', type=int, help="Limit ODE problems")
    parser.add_argument('--limit-university', type=int, help="Limit University problems")

    args = parser.parse_args()

    limits = {}
    if args.limit_gsm8k:
        limits['gsm8k'] = args.limit_gsm8k
    if args.limit_math:
        limits['math'] = args.limit_math
    if args.limit_aime:
        limits['aime'] = args.limit_aime
    if args.limit_ode:
        limits['ode'] = args.limit_ode
    if args.limit_university:
        limits['university'] = args.limit_university

    runner = MasterBenchmarkRunner()
    runner.run_all(
        skip_gsm8k=args.skip_gsm8k,
        skip_math=args.skip_math,
        skip_aime=args.skip_aime,
        skip_ode=args.skip_ode,
        skip_university=args.skip_university,
        limits=limits
    )


if __name__ == "__main__":
    main()
