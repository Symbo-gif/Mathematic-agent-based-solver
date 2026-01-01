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
ODE Benchmark Failure Analysis and Recursive Fix Script

Analyzes ODE benchmark results and identifies specific failure patterns
for targeted fixes.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any


def load_latest_results() -> Dict[str, Any]:
    """Load most recent ODE benchmark results"""
    results_dir = Path("data/benchmarks/results")
    results_files = list(results_dir.glob("ode_suite_*.json"))

    if not results_files:
        raise FileNotFoundError("No ODE benchmark results found!")

    latest_file = max(results_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading: {latest_file}")

    with open(latest_file, 'r') as f:
        return json.load(f)


def analyze_failures_by_pattern(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Group failures by error pattern"""
    failures = [r for r in results if r['status'] != 'correct']

    by_error = defaultdict(list)

    for failure in failures:
        # Extract error pattern
        error = failure.get('error_message', '')
        system_answer = str(failure.get('system_answer', ''))

        if 'Could not integrate' in system_answer:
            # Integration failure
            if 'mu(x)*Q(x)' in system_answer:
                pattern_key = 'linear_ode_integration_failure'
            elif 'separable' in system_answer.lower():
                pattern_key = 'separable_factorization_failure'
            else:
                pattern_key = 'general_integration_failure'
        elif 'success\': False' in system_answer or 'success": False' in system_answer:
            pattern_key = 'error_dict_returned'
        else:
            pattern_key = 'answer_mismatch'

        by_error[pattern_key].append(failure)

    return dict(by_error)


def analyze_linear_ode_failures(failures: List[Dict]) -> Dict[str, Any]:
    """Analyze linear ODE integration failures"""
    # Look for specific Q(x) patterns that fail
    q_patterns = defaultdict(int)

    for f in failures:
        problem = f['problem_text']
        # Extract Q(x) from dy/dx + P(x)*y = Q(x)
        if '=' in problem:
            parts = problem.split('=')
            if len(parts) == 2:
                q_x = parts[1].strip()
                if 'cos' in q_x:
                    q_patterns['cosine'] += 1
                elif 'sin' in q_x:
                    q_patterns['sine'] += 1
                elif 'exp' in q_x:
                    q_patterns['exponential'] += 1
                elif '/' in q_x:
                    q_patterns['rational'] += 1
                elif 'x' in q_x and '*x' not in q_x:
                    q_patterns['polynomial'] += 1

    return {
        'total': len(failures),
        'q_patterns': dict(q_patterns)
    }


def analyze_separable_failures(failures: List[Dict]) -> Dict[str, Any]:
    """Analyze separable ODE failures"""
    # Look for specific g(y) patterns that fail
    g_patterns = defaultdict(int)

    for f in failures:
        problem = f['problem_text']
        # Look for dy/dx = f(x)*g(y) patterns
        if '=' in problem:
            parts = problem.split('=')
            if len(parts) == 2:
                rhs = parts[1].strip()
                if 'sqrt(y)' in rhs or 'sqrt' in rhs:
                    g_patterns['sqrt(y)'] += 1
                elif '/y' in rhs or '1/y' in rhs:
                    g_patterns['1/y'] += 1
                elif 'y**2' in rhs or 'y^2' in rhs:
                    g_patterns['y^2'] += 1
                elif 'y**3' in rhs or 'y^3' in rhs:
                    g_patterns['y^n (n>=3)'] += 1

    return {
        'total': len(failures),
        'g_patterns': dict(g_patterns)
    }


def print_failure_analysis(results_data: Dict[str, Any]):
    """Print comprehensive failure analysis"""
    results = results_data['results']
    total = len(results)
    correct = sum(1 for r in results if r['status'] == 'correct')
    incorrect = total - correct

    print("=" * 80)
    print("ODE BENCHMARK FAILURE ANALYSIS")
    print("=" * 80)
    print(f"\nOverall: {correct}/{total} correct ({correct/total*100:.2f}%)")
    print(f"Failures: {incorrect} ({incorrect/total*100:.2f}%)")
    print()

    # Group by failure pattern
    failures_by_pattern = analyze_failures_by_pattern(results)

    print("FAILURES BY PATTERN:")
    print("-" * 80)
    for pattern, failures in sorted(failures_by_pattern.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {pattern:45s}: {len(failures):5d} ({len(failures)/incorrect*100:5.1f}% of failures)")

    print()

    # Analyze linear ODE failures
    if 'linear_ode_integration_failure' in failures_by_pattern:
        print("LINEAR ODE INTEGRATION FAILURES (DETAILED):")
        print("-" * 80)
        linear_analysis = analyze_linear_ode_failures(failures_by_pattern['linear_ode_integration_failure'])
        print(f"  Total: {linear_analysis['total']}")
        print(f"  Q(x) patterns:")
        for pattern, count in sorted(linear_analysis['q_patterns'].items(), key=lambda x: x[1], reverse=True):
            print(f"    - {pattern:20s}: {count:5d}")
        print()

    # Analyze separable failures
    if 'separable_factorization_failure' in failures_by_pattern:
        print("SEPARABLE ODE FAILURES (DETAILED):")
        print("-" * 80)
        sep_analysis = analyze_separable_failures(failures_by_pattern['separable_factorization_failure'])
        print(f"  Total: {sep_analysis['total']}")
        print(f"  g(y) patterns:")
        for pattern, count in sorted(sep_analysis['g_patterns'].items(), key=lambda x: x[1], reverse=True):
            print(f"    - {pattern:20s}: {count:5d}")
        print()

    # Sample failures
    print("SAMPLE FAILURES (First 10):")
    print("-" * 80)
    for i, (pattern, failures) in enumerate(list(failures_by_pattern.items())[:3]):
        print(f"\nPattern: {pattern}")
        for j, f in enumerate(failures[:3]):
            print(f"  {j+1}. {f['problem_id']}: {f['problem_text']}")
            print(f"     System: {str(f['system_answer'])[:100]}...")
        if i >= 2:
            break

    print("\n" + "=" * 80)


def main():
    results_data = load_latest_results()
    print_failure_analysis(results_data)


if __name__ == "__main__":
    main()
