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
Analyze failures in first-order linear nonhomogeneous ODE category.
Extract patterns and sample failed cases for debugging.
"""

import json
from collections import Counter
from pathlib import Path
import sys

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

def safe_print(text):
    """Print text safely, handling Unicode errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters
        print(text.encode('ascii', 'ignore').decode('ascii'))

def analyze_failures(results_file):
    """Analyze failed first-order linear nonhomogeneous ODEs."""

    with open(results_file, 'r') as f:
        data = json.load(f)

    # Filter for first_order_linear_nonhomogeneous failures
    failures = [
        r for r in data['results']
        if r.get('category') == 'first_order_linear_nonhomogeneous'
        and r.get('status') == 'incorrect'
    ]

    print(f"\n{'='*70}")
    print(f"FIRST-ORDER LINEAR NONHOMOGENEOUS FAILURE ANALYSIS")
    print(f"{'='*70}")
    print(f"Total failures: {len(failures)}")
    print(f"Total in category: {sum(1 for r in data['results'] if r.get('category') == 'first_order_linear_nonhomogeneous')}")
    print(f"Failure rate: {len(failures) / sum(1 for r in data['results'] if r.get('category') == 'first_order_linear_nonhomogeneous') * 100:.1f}%")

    # Sample 20 diverse failures
    print(f"\n{'='*70}")
    print(f"SAMPLE OF 20 FAILED CASES")
    print(f"{'='*70}")

    # Get evenly spaced samples
    step = len(failures) // 20 if len(failures) > 20 else 1
    samples = failures[::step][:20]

    for i, case in enumerate(samples, 1):
        print(f"\n--- Case {i} ---")
        print(f"Problem: {case['problem_text']}")
        print(f"Expected: {case.get('expected_answer', 'N/A')}")
        print(f"Got: {case.get('system_answer', 'N/A')}")
        if case.get('error_message'):
            print(f"Error: {case['error_message']}")

    # Analyze error patterns
    print(f"\n{'='*70}")
    print(f"ERROR PATTERN ANALYSIS")
    print(f"{'='*70}")

    error_types = Counter()
    for case in failures:
        if case.get('error_message'):
            error_types[case['error_message'][:100]] += 1  # First 100 chars of error
        else:
            # Check if result is empty/None
            result = case.get('system_answer', '')
            if not result or result == 'None' or result == 'null':
                error_types['Empty/None result'] += 1
            else:
                error_types['Wrong answer (has result)'] += 1

    print(f"\nTop error patterns:")
    for error, count in error_types.most_common(10):
        print(f"  {count:5d}x: {error}")

    # Check for specific patterns in the problems
    print(f"\n{'='*70}")
    print(f"PROBLEM PATTERN ANALYSIS")
    print(f"{'='*70}")

    # Look for common P(x) and Q(x) patterns
    patterns = {
        'polynomial_P': 0,
        'constant_P': 0,
        'trig_P': 0,
        'exp_P': 0,
        'polynomial_Q': 0,
        'constant_Q': 0,
        'trig_Q': 0,
        'exp_Q': 0,
    }

    for case in failures[:1000]:  # Analyze first 1000 to save time
        problem = case['problem_text']
        # Simple heuristic pattern detection
        if 'sin(' in problem or 'cos(' in problem:
            if 'dy/dx' in problem[:problem.find('=')] if '=' in problem else False:
                patterns['trig_P'] += 1
            patterns['trig_Q'] += 1
        if 'exp(' in problem or 'e^' in problem:
            patterns['exp_Q'] += 1
        if any(c in problem for c in ['x^2', 'x^3', 'x**2']):
            patterns['polynomial_Q'] += 1

    print(f"\nPattern frequencies (first 1000 failures):")
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {pattern}: {count}")

    # Save detailed failure report
    report_file = Path(results_file).parent / 'linear_nonhomog_failure_report.json'
    with open(report_file, 'w') as f:
        json.dump({
            'total_failures': len(failures),
            'sample_cases': samples[:20],
            'error_patterns': dict(error_types.most_common(20)),
            'pattern_analysis': patterns
        }, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Detailed report saved to: {report_file}")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    results_file = 'data/benchmarks/results/ode_suite_20251220_090238.json'
    analyze_failures(results_file)
