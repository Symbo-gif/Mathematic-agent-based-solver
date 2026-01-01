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
ODE Benchmark Results Analysis Script

Analyzes the results from the 30,001 ODE benchmark run.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any


def load_results(results_file: str) -> Dict[str, Any]:
    """Load benchmark results from JSON file."""
    with open(results_file, 'r') as f:
        return json.load(f)


def analyze_results(results_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform comprehensive analysis of benchmark results."""

    results = results_data['results']

    # Overall statistics
    total = len(results)
    correct = sum(1 for r in results if r['status'] == 'correct')
    incorrect = sum(1 for r in results if r['status'] == 'incorrect')
    timeout = sum(1 for r in results if r['status'] == 'timeout')
    error = sum(1 for r in results if r['status'] == 'error')

    # Category breakdown
    by_category = defaultdict(lambda: {'total': 0, 'correct': 0, 'incorrect': 0})
    for r in results:
        cat = r['category']
        by_category[cat]['total'] += 1
        if r['status'] == 'correct':
            by_category[cat]['correct'] += 1
        else:
            by_category[cat]['incorrect'] += 1

    # Difficulty breakdown
    by_difficulty = defaultdict(lambda: {'total': 0, 'correct': 0})
    for r in results:
        diff = r.get('difficulty', 'unknown')
        by_difficulty[diff]['total'] += 1
        if r['status'] == 'correct':
            by_difficulty[diff]['correct'] += 1

    # Source breakdown (existing vs synthetic)
    by_source = defaultdict(lambda: {'total': 0, 'correct': 0})
    for r in results:
        source = r.get('metadata', {}).get('source', 'unknown')
        by_source[source]['total'] += 1
        if r['status'] == 'correct':
            by_source[source]['correct'] += 1

    # Time statistics
    times = [r['time_seconds'] for r in results]
    times.sort()
    avg_time = sum(times) / len(times)
    median_time = times[len(times)//2]
    p95_time = times[int(len(times)*0.95)]
    max_time = max(times)

    # Error analysis
    error_messages = Counter()
    false_positive_analysis = []  # Cases marked correct but might be wrong

    for r in results:
        if r['error_message']:
            error_messages[r['error_message']] += 1

        # Check for suspicious "correct" answers
        if r['status'] == 'correct':
            ans = r['system_answer']
            # Check if answer is error dict
            if isinstance(ans, str) and ('success\': False' in ans or 'error\':' in ans):
                false_positive_analysis.append({
                    'problem_id': r['problem_id'],
                    'problem_text': r['problem_text'],
                    'expected': r['expected_answer'],
                    'system': ans,
                    'category': r['category']
                })

    # Analyze first_order_separable failures (only 51.8% correct)
    separable_failures = [
        r for r in results
        if r['category'] == 'first_order_separable' and r['status'] == 'incorrect'
    ]

    # Sample of separable failures
    separable_samples = separable_failures[:10] if separable_failures else []

    return {
        'overall': {
            'total': total,
            'correct': correct,
            'incorrect': incorrect,
            'timeout': timeout,
            'error': error,
            'accuracy': correct / total * 100
        },
        'by_category': dict(by_category),
        'by_difficulty': dict(by_difficulty),
        'by_source': dict(by_source),
        'time_stats': {
            'average': avg_time,
            'median': median_time,
            'p95': p95_time,
            'max': max_time
        },
        'error_messages': dict(error_messages),
        'false_positive_count': len(false_positive_analysis),
        'false_positive_samples': false_positive_analysis[:5],
        'separable_failure_count': len(separable_failures),
        'separable_failure_samples': separable_samples
    }


def print_analysis(analysis: Dict[str, Any]):
    """Print formatted analysis report."""

    print("=" * 80)
    print("ODE BENCHMARK COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    print()

    # Overall stats
    overall = analysis['overall']
    print("OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total Problems:    {overall['total']:,}")
    print(f"Correct:           {overall['correct']:,} ({overall['accuracy']:.2f}%)")
    print(f"Incorrect:         {overall['incorrect']:,}")
    print(f"Timeout:           {overall['timeout']:,}")
    print(f"Error:             {overall['error']:,}")
    print()

    # Category breakdown
    print("CATEGORY BREAKDOWN")
    print("-" * 80)
    for cat, stats in sorted(analysis['by_category'].items()):
        accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"{cat:45s}: {stats['correct']:5d}/{stats['total']:5d} ({accuracy:6.2f}%)")
    print()

    # Source breakdown
    print("SOURCE BREAKDOWN")
    print("-" * 80)
    for source, stats in sorted(analysis['by_source'].items()):
        accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"{source:20s}: {stats['correct']:5d}/{stats['total']:5d} ({accuracy:6.2f}%)")
    print()

    # Time statistics
    print("TIME STATISTICS")
    print("-" * 80)
    time_stats = analysis['time_stats']
    print(f"Average:   {time_stats['average']:.4f}s")
    print(f"Median:    {time_stats['median']:.4f}s")
    print(f"P95:       {time_stats['p95']:.4f}s")
    print(f"Maximum:   {time_stats['max']:.4f}s")
    print()

    # False positives
    if analysis['false_positive_count'] > 0:
        print("SUSPICIOUS CORRECT ANSWERS (Error dicts marked as correct)")
        print("-" * 80)
        print(f"Found {analysis['false_positive_count']} suspicious cases")
        print("\nSample cases:")
        for idx, case in enumerate(analysis['false_positive_samples'], 1):
            print(f"\n{idx}. {case['problem_id']} ({case['category']})")
            print(f"   Problem: {case['problem_text']}")
            print(f"   Expected: {case['expected']}")
            # Encode to ASCII to avoid Unicode errors
            system_str = str(case['system'])[:100].encode('ascii', 'replace').decode('ascii')
            print(f"   System: {system_str}...")
        print()

    # Separable failures
    if analysis['separable_failure_count'] > 0:
        print("FIRST_ORDER_SEPARABLE FAILURES (51.8% accuracy)")
        print("-" * 80)
        print(f"Total failures: {analysis['separable_failure_count']:,}")
        print("\nSample failures:")
        for idx, case in enumerate(analysis['separable_failure_samples'], 1):
            print(f"\n{idx}. {case['problem_id']}")
            print(f"   Problem: {case['problem_text']}")
            print(f"   Expected: {case['expected_answer']}")
            print(f"   System: {case['system_answer'][:150]}")
        print()

    # Key insights
    print("=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)

    # Identify strengths
    strong_categories = [
        (cat, stats['correct']/stats['total']*100)
        for cat, stats in analysis['by_category'].items()
        if stats['total'] > 100 and stats['correct']/stats['total'] > 0.95
    ]

    if strong_categories:
        print("\nSTRONG CATEGORIES (>95% accuracy, >100 problems):")
        for cat, acc in sorted(strong_categories, key=lambda x: x[1], reverse=True):
            print(f"  - {cat}: {acc:.2f}%")

    # Identify weaknesses
    weak_categories = [
        (cat, stats['correct']/stats['total']*100, stats['total'])
        for cat, stats in analysis['by_category'].items()
        if stats['total'] > 100 and stats['correct']/stats['total'] < 0.80
    ]

    if weak_categories:
        print("\nWEAK CATEGORIES (<80% accuracy, >100 problems):")
        for cat, acc, total in sorted(weak_categories, key=lambda x: x[1]):
            print(f"  - {cat}: {acc:.2f}% ({total} problems)")

    print("\n" + "=" * 80)


def main():
    # Find latest results file
    results_dir = Path("data/benchmarks/results")
    results_files = list(results_dir.glob("ode_suite_*.json"))

    if not results_files:
        print("No ODE benchmark results found!")
        return

    latest_file = max(results_files, key=lambda p: p.stat().st_mtime)

    print(f"Analyzing: {latest_file}")
    print()

    # Load and analyze
    results_data = load_results(latest_file)
    analysis = analyze_results(results_data)

    # Print report
    print_analysis(analysis)

    # Save analysis to file
    analysis_file = results_dir / f"ode_analysis_{latest_file.stem.split('_')[-1]}.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nDetailed analysis saved to: {analysis_file}")


if __name__ == "__main__":
    main()
