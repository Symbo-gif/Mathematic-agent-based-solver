#!/usr/bin/env python3
# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
SYMBO BENCHMARK - Regression Testing & Performance Tracking
============================================================

A CLI tool for running the Symbo stress test suite and tracking
improvements/regressions over time.

Commands:
    symbo-bench run         Run the full 640-equation suite
    symbo-bench diff        Compare two result files
    symbo-bench summary     Show summary of a result file
    symbo-bench targets     Show target pass rates by category

Usage:
    python scripts/symbo_bench.py run [--output results.json]
    python scripts/symbo_bench.py diff old.json new.json
    python scripts/symbo_bench.py summary results.json
    python scripts/symbo_bench.py targets
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


# Target pass rates by category (short-term goals)
TARGET_PASS_RATES = {
    'definite_integrals': 100.0,
    'indefinite_integrals': 100.0,
    'infinite_series': 100.0,
    'limits': 97.0,               # Target: 86% -> 97%
    'derivatives': 100.0,
    'differential_equations': 100.0,
    'linear_algebra': 98.0,       # Target: 98% -> 98%
    'number_theory': 98.0,        # Target: 94% -> 98%
    'probability_statistics': 95.0,  # Target: 80% -> 95%
    'physics_applied': 98.0,      # Target: 98% -> 98%
}


def load_results(filepath: str) -> Dict[str, Any]:
    """Load benchmark results from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(results: Dict[str, Any], filepath: str):
    """Save benchmark results to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def calculate_stats(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate detailed statistics from results."""
    stats = {
        'total': len(results.get('results', [])),
        'success': 0,
        'failed': 0,
        'timeout': 0,
        'error': 0,
        'by_category': {},
        'pass_rate': 0.0,
        'latency_ms': {
            'mean': 0.0,
            'min': float('inf'),
            'max': 0.0,
            'p95': 0.0,
        }
    }

    # Collect data by category
    category_data: Dict[str, Dict] = {}
    latencies = []

    for result in results.get('results', []):
        status = result.get('status', 'error')
        category = result.get('category', 'unknown')
        time_ms = result.get('time_ms', 0)

        # Update overall stats
        if status == 'success':
            stats['success'] += 1
        elif status == 'timeout':
            stats['timeout'] += 1
        elif status == 'failed':
            stats['failed'] += 1
        else:
            stats['error'] += 1

        latencies.append(time_ms)

        # Update category stats
        if category not in category_data:
            category_data[category] = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'timeout': 0,
                'error': 0,
                'latencies': []
            }

        category_data[category]['total'] += 1
        category_data[category]['latencies'].append(time_ms)
        if status == 'success':
            category_data[category]['success'] += 1
        elif status == 'timeout':
            category_data[category]['timeout'] += 1
        elif status == 'failed':
            category_data[category]['failed'] += 1
        else:
            category_data[category]['error'] += 1

    # Calculate overall pass rate
    if stats['total'] > 0:
        stats['pass_rate'] = (stats['success'] / stats['total']) * 100

    # Calculate overall latency stats
    if latencies:
        latencies.sort()
        stats['latency_ms']['mean'] = sum(latencies) / len(latencies)
        stats['latency_ms']['min'] = min(latencies)
        stats['latency_ms']['max'] = max(latencies)
        p95_idx = int(len(latencies) * 0.95)
        stats['latency_ms']['p95'] = latencies[p95_idx] if p95_idx < len(latencies) else latencies[-1]

    # Calculate per-category stats
    for cat, data in category_data.items():
        cat_latencies = data['latencies']
        cat_latencies.sort()
        stats['by_category'][cat] = {
            'total': data['total'],
            'success': data['success'],
            'failed': data['failed'],
            'timeout': data['timeout'],
            'error': data['error'],
            'pass_rate': (data['success'] / data['total'] * 100) if data['total'] > 0 else 0,
            'latency_mean': sum(cat_latencies) / len(cat_latencies) if cat_latencies else 0,
            'latency_p95': cat_latencies[int(len(cat_latencies) * 0.95)] if cat_latencies else 0,
        }

    return stats


def diff_results(old_results: Dict, new_results: Dict) -> Dict[str, Any]:
    """
    Compare two benchmark runs and identify improvements/regressions.

    Returns:
        Dict with:
        - fixed: equations that now pass
        - regressed: equations that now fail
        - category_delta: per-category pass rate changes
    """
    old_map = {r['equation']: r for r in old_results.get('results', [])}
    new_map = {r['equation']: r for r in new_results.get('results', [])}

    fixed = []
    regressed = []

    all_equations = set(old_map.keys()) | set(new_map.keys())

    for eq in all_equations:
        old_status = old_map.get(eq, {}).get('status', 'missing')
        new_status = new_map.get(eq, {}).get('status', 'missing')

        if old_status != 'success' and new_status == 'success':
            fixed.append({
                'equation': eq,
                'old_status': old_status,
                'old_error': old_map.get(eq, {}).get('error'),
                'category': new_map.get(eq, {}).get('category', 'unknown')
            })
        elif old_status == 'success' and new_status != 'success':
            regressed.append({
                'equation': eq,
                'new_status': new_status,
                'new_error': new_map.get(eq, {}).get('error'),
                'category': old_map.get(eq, {}).get('category', 'unknown')
            })

    # Calculate per-category deltas
    old_stats = calculate_stats(old_results)
    new_stats = calculate_stats(new_results)

    category_delta = {}
    all_categories = set(old_stats['by_category'].keys()) | set(new_stats['by_category'].keys())

    for cat in all_categories:
        old_rate = old_stats['by_category'].get(cat, {}).get('pass_rate', 0)
        new_rate = new_stats['by_category'].get(cat, {}).get('pass_rate', 0)
        delta = new_rate - old_rate

        category_delta[cat] = {
            'old_rate': round(old_rate, 1),
            'new_rate': round(new_rate, 1),
            'delta': round(delta, 1),
            'improved': delta > 0,
            'regressed': delta < 0,
        }

    return {
        'fixed': fixed,
        'regressed': regressed,
        'category_delta': category_delta,
        'overall': {
            'old_pass_rate': round(old_stats['pass_rate'], 1),
            'new_pass_rate': round(new_stats['pass_rate'], 1),
            'delta': round(new_stats['pass_rate'] - old_stats['pass_rate'], 1),
            'fixed_count': len(fixed),
            'regressed_count': len(regressed),
        }
    }


def print_summary(stats: Dict[str, Any], show_failures: bool = False):
    """Print a formatted summary of benchmark results."""
    print("\n" + "=" * 70)
    print("SYMBO BENCHMARK SUMMARY")
    print("=" * 70)

    print(f"\nOverall: {stats['success']}/{stats['total']} passed ({stats['pass_rate']:.1f}%)")
    print(f"Failed: {stats['failed']} | Timeout: {stats['timeout']} | Error: {stats['error']}")

    print(f"\nLatency: mean={stats['latency_ms']['mean']:.1f}ms, "
          f"p95={stats['latency_ms']['p95']:.1f}ms, "
          f"max={stats['latency_ms']['max']:.1f}ms")

    print("\n" + "-" * 70)
    print("BY CATEGORY:")
    print("-" * 70)

    # Sort categories by pass rate (ascending, so worst first)
    sorted_cats = sorted(stats['by_category'].items(), key=lambda x: x[1]['pass_rate'])

    for cat, cat_stats in sorted_cats:
        target = TARGET_PASS_RATES.get(cat, 100.0)
        status = "OK" if cat_stats['pass_rate'] >= target else "BELOW TARGET"
        delta_to_target = cat_stats['pass_rate'] - target

        print(f"  {cat:25s}: {cat_stats['success']:3d}/{cat_stats['total']:3d} "
              f"({cat_stats['pass_rate']:5.1f}%) "
              f"[target: {target:.0f}%] {status}")

    print("=" * 70)


def print_diff(diff: Dict[str, Any]):
    """Print formatted diff between two benchmark runs."""
    print("\n" + "=" * 70)
    print("SYMBO BENCHMARK DIFF")
    print("=" * 70)

    overall = diff['overall']
    direction = "UP" if overall['delta'] > 0 else ("DOWN" if overall['delta'] < 0 else "SAME")

    print(f"\nOverall: {overall['old_pass_rate']:.1f}% -> {overall['new_pass_rate']:.1f}% "
          f"({'+' if overall['delta'] >= 0 else ''}{overall['delta']:.1f}% {direction})")
    print(f"Fixed: {overall['fixed_count']} | Regressed: {overall['regressed_count']}")

    # Category changes
    print("\n" + "-" * 70)
    print("CATEGORY CHANGES:")
    print("-" * 70)

    for cat, delta in sorted(diff['category_delta'].items()):
        if delta['delta'] != 0:
            direction = "+" if delta['delta'] > 0 else ""
            status = "IMPROVED" if delta['improved'] else ("REGRESSED" if delta['regressed'] else "")
            print(f"  {cat:25s}: {delta['old_rate']:.1f}% -> {delta['new_rate']:.1f}% "
                  f"({direction}{delta['delta']:.1f}%) {status}")

    # Fixed equations
    if diff['fixed']:
        print("\n" + "-" * 70)
        print(f"FIXED ({len(diff['fixed'])}):")
        print("-" * 70)
        for item in diff['fixed'][:20]:  # Show first 20
            print(f"  [{item['category']}] {item['equation'][:60]}")
        if len(diff['fixed']) > 20:
            print(f"  ... and {len(diff['fixed']) - 20} more")

    # Regressed equations
    if diff['regressed']:
        print("\n" + "-" * 70)
        print(f"REGRESSED ({len(diff['regressed'])}):")
        print("-" * 70)
        for item in diff['regressed']:
            print(f"  [{item['category']}] {item['equation'][:60]}")
            print(f"      Error: {item['new_error']}")

    print("=" * 70)


def print_targets():
    """Print target pass rates by category."""
    print("\n" + "=" * 70)
    print("SYMBO BENCHMARK TARGETS")
    print("=" * 70)
    print("\nThese are the short-term target pass rates for each category:")
    print("-" * 70)

    for cat, target in sorted(TARGET_PASS_RATES.items()):
        print(f"  {cat:25s}: {target:5.1f}%")

    print("=" * 70)


def cmd_run(args):
    """Run the stress test suite."""
    print("Running Symbo stress test suite...")

    # Try to import and run the stress test
    try:
        from data.stress_tests import stress_test_runner

        # Run the stress test
        results = stress_test_runner.run_stress_test()

        # Calculate stats
        stats = calculate_stats(results)

        # Print summary
        print_summary(stats)

        # Save results
        output_file = args.output
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/benchmarks/symbo_bench_{timestamp}.json"

        # Ensure directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_results(results, output_file)
        print(f"\nResults saved to: {output_file}")

    except ImportError as e:
        print(f"Error: Could not import stress test runner: {e}")
        print("Make sure you're running from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running stress test: {e}")
        sys.exit(1)


def cmd_diff(args):
    """Compare two benchmark result files."""
    try:
        old_results = load_results(args.old_file)
        new_results = load_results(args.new_file)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)

    diff = diff_results(old_results, new_results)
    print_diff(diff)

    # Return non-zero exit code if there are regressions
    if diff['regressed']:
        sys.exit(1)


def cmd_summary(args):
    """Show summary of a benchmark result file."""
    try:
        results = load_results(args.file)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)

    stats = calculate_stats(results)
    print_summary(stats, show_failures=args.failures)

    # Show failed equations if requested
    if args.failures:
        print("\n" + "-" * 70)
        print("FAILED EQUATIONS:")
        print("-" * 70)
        for result in results.get('results', []):
            if result.get('status') != 'success':
                print(f"  [{result.get('category', 'unknown')}] {result.get('equation', '')[:60]}")
                print(f"      Error: {result.get('error', 'Unknown')}")


def cmd_targets(args):
    """Show target pass rates."""
    print_targets()


def main():
    parser = argparse.ArgumentParser(
        description='Symbo Benchmark - Regression Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/symbo_bench.py run --output results.json
  python scripts/symbo_bench.py diff old.json new.json
  python scripts/symbo_bench.py summary results.json --failures
  python scripts/symbo_bench.py targets
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # run command
    run_parser = subparsers.add_parser('run', help='Run the stress test suite')
    run_parser.add_argument('--output', '-o', help='Output file for results (default: auto-generated)')
    run_parser.set_defaults(func=cmd_run)

    # diff command
    diff_parser = subparsers.add_parser('diff', help='Compare two result files')
    diff_parser.add_argument('old_file', help='Path to old/baseline results')
    diff_parser.add_argument('new_file', help='Path to new results')
    diff_parser.set_defaults(func=cmd_diff)

    # summary command
    summary_parser = subparsers.add_parser('summary', help='Show summary of results')
    summary_parser.add_argument('file', help='Path to results file')
    summary_parser.add_argument('--failures', '-f', action='store_true',
                                help='Show failed equations')
    summary_parser.set_defaults(func=cmd_summary)

    # targets command
    targets_parser = subparsers.add_parser('targets', help='Show target pass rates')
    targets_parser.set_defaults(func=cmd_targets)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
