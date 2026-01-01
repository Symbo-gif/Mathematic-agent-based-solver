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
Recursive ODE Fixer - Automated Test-and-Fix System

Analyzes ODE benchmark failures and implements targeted fixes
in a recursive loop until 100% accuracy or practical limit.
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple


class ODEFailureAnalyzer:
    """Analyzes ODE benchmark failures and suggests fixes"""

    def __init__(self, results_file: Path):
        """Load benchmark results"""
        with open(results_file, 'r') as f:
            self.data = json.load(f)
        self.results = self.data['results']
        self.failures = [r for r in self.results if r['status'] != 'correct']

    def analyze(self) -> Dict[str, Any]:
        """Comprehensive failure analysis"""
        analysis = {
            'total_problems': len(self.results),
            'correct': sum(1 for r in self.results if r['status'] == 'correct'),
            'incorrect': len(self.failures),
            'accuracy': sum(1 for r in self.results if r['status'] == 'correct') / len(self.results) * 100,
            'by_category': self._analyze_by_category(),
            'failure_patterns': self._analyze_failure_patterns(),
            'top_issues': self._identify_top_issues(),
            'sample_failures': self._get_sample_failures()
        }
        return analysis

    def _analyze_by_category(self) -> Dict[str, Dict[str, int]]:
        """Break down by ODE category"""
        by_cat = defaultdict(lambda: {'total': 0, 'correct': 0, 'incorrect': 0})

        for r in self.results:
            cat = r['category']
            by_cat[cat]['total'] += 1
            if r['status'] == 'correct':
                by_cat[cat]['correct'] += 1
            else:
                by_cat[cat]['incorrect'] += 1

        return dict(by_cat)

    def _analyze_failure_patterns(self) -> Dict[str, List[Dict]]:
        """Group failures by error pattern"""
        patterns = defaultdict(list)

        for f in self.failures:
            system_ans = str(f.get('system_answer', ''))

            # Classify error type
            if 'Could not integrate' in system_ans:
                if 'mu(x)*Q(x)' in system_ans:
                    pattern = 'linear_ode_integration_failure'
                elif 'separable' in system_ans.lower():
                    pattern = 'separable_integration_failure'
                else:
                    pattern = 'general_integration_failure'
            elif "'success': False" in system_ans or '"success": False' in system_ans:
                if 'exp' in system_ans and ('sin' in system_ans or 'cos' in system_ans):
                    pattern = 'exp_trig_pattern_match_failure'
                else:
                    pattern = 'algorithm_failure'
            elif system_ans.strip().startswith('{') and 'error' in system_ans:
                pattern = 'error_dict'
            else:
                pattern = 'answer_mismatch'

            patterns[pattern].append(f)

        return dict(patterns)

    def _identify_top_issues(self) -> List[Dict[str, Any]]:
        """Identify top issues by impact"""
        patterns = self._analyze_failure_patterns()

        issues = []
        for pattern, failures in patterns.items():
            # Analyze specific sub-patterns
            sub_analysis = self._analyze_sub_patterns(failures, pattern)

            issues.append({
                'pattern': pattern,
                'count': len(failures),
                'percentage': len(failures) / len(self.failures) * 100,
                'sub_patterns': sub_analysis,
                'sample': failures[:5] if failures else []
            })

        # Sort by count
        issues.sort(key=lambda x: x['count'], reverse=True)
        return issues

    def _analyze_sub_patterns(self, failures: List[Dict], pattern: str) -> Dict[str, int]:
        """Analyze sub-patterns within a failure type"""
        sub_patterns = Counter()

        if pattern == 'linear_ode_integration_failure':
            # Analyze Q(x) patterns
            for f in failures:
                problem = f['problem_text']
                if '=' in problem:
                    parts = problem.split('=')
                    if len(parts) == 2:
                        q_x = parts[1].strip()
                        if 'cos' in q_x:
                            sub_patterns['Q(x)=cos'] += 1
                        elif 'sin' in q_x:
                            sub_patterns['Q(x)=sin'] += 1
                        elif 'exp' in q_x and 'x**2' in q_x:
                            sub_patterns['Q(x)=exp(x^2)'] += 1
                        elif 'exp' in q_x:
                            sub_patterns['Q(x)=exp'] += 1
                        elif '/' in q_x:
                            sub_patterns['Q(x)=rational'] += 1

        elif pattern == 'separable_integration_failure':
            # Analyze g(y) patterns
            for f in failures:
                problem = f['problem_text']
                if 'sqrt(y)' in problem or 'sqrt' in problem:
                    sub_patterns['g(y)=sqrt(y)'] += 1
                elif '/y' in problem or '1/y' in problem:
                    sub_patterns['g(y)=1/y'] += 1
                elif 'y**2' in problem or 'y^2' in problem:
                    sub_patterns['g(y)=y^2'] += 1
                elif 'y**' in problem or 'y^' in problem:
                    sub_patterns['g(y)=y^n'] += 1

        elif pattern == 'exp_trig_pattern_match_failure':
            # Analyze why pattern didn't match
            for f in failures:
                system_ans = str(f.get('system_answer', ''))
                if 'ln(' in system_ans:
                    sub_patterns['exp(ln(...))'] += 1
                if '**2' in system_ans and 'exp' in system_ans:
                    sub_patterns['exp(x^2)'] += 1

        return dict(sub_patterns)

    def _get_sample_failures(self) -> Dict[str, List[Dict]]:
        """Get sample failures by pattern"""
        patterns = self._analyze_failure_patterns()
        samples = {}

        for pattern, failures in patterns.items():
            samples[pattern] = failures[:10]  # First 10 of each type

        return samples

    def print_analysis(self):
        """Print formatted analysis"""
        analysis = self.analyze()

        print("=" * 80)
        print("ODE BENCHMARK FAILURE ANALYSIS - ITERATION 1")
        print("=" * 80)
        print(f"\nOverall: {analysis['correct']}/{analysis['total_problems']} correct ({analysis['accuracy']:.2f}%)")
        print(f"Failures: {analysis['incorrect']} ({analysis['incorrect']/analysis['total_problems']*100:.2f}%)")
        print()

        # Category breakdown
        print("BY CATEGORY:")
        print("-" * 80)
        for cat, stats in sorted(analysis['by_category'].items(), key=lambda x: x[1]['correct']/x[1]['total'] if x[1]['total'] > 0 else 0):
            acc = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"  {cat:45s}: {stats['correct']:5d}/{stats['total']:5d} ({acc:6.2f}%)")
        print()

        # Top issues
        print("TOP FAILURE PATTERNS:")
        print("-" * 80)
        for i, issue in enumerate(analysis['top_issues'][:5], 1):
            print(f"\n{i}. {issue['pattern']:40s}: {issue['count']:5d} ({issue['percentage']:5.1f}% of failures)")
            if issue['sub_patterns']:
                print("   Sub-patterns:")
                for sub, count in sorted(issue['sub_patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"     - {sub:30s}: {count:5d}")

            # Sample
            if issue['sample']:
                print("   Sample:")
                for j, sample in enumerate(issue['sample'][:3], 1):
                    print(f"     {j}. {sample['problem_id']}: {sample['problem_text'][:60]}...")

        print("\n" + "=" * 80)

        return analysis

    def suggest_fixes(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest prioritized fixes based on analysis"""
        fixes = []

        for issue in analysis['top_issues'][:10]:
            pattern = issue['pattern']
            count = issue['count']

            if pattern == 'exp_trig_pattern_match_failure':
                fixes.append({
                    'priority': 'HIGH',
                    'issue': pattern,
                    'count': count,
                    'fix': 'Enhance exp×trig pattern matching to handle exp(ln(...)), exp(x^2) forms',
                    'file': 'exp_trig_integration_specialist.py',
                    'method': '_integrate_exp_trig',
                    'estimated_impact': f'+{count} problems'
                })

            elif pattern == 'separable_integration_failure':
                # Check sub-patterns
                if 'g(y)=sqrt(y)' in issue['sub_patterns']:
                    fixes.append({
                        'priority': 'HIGH',
                        'issue': 'separable_sqrt_y',
                        'count': issue['sub_patterns']['g(y)=sqrt(y)'],
                        'fix': 'Enhance integration engine to handle y^(-0.5) integration',
                        'file': 'integration_specialist.py',
                        'method': '_integrate_power',
                        'estimated_impact': f'+{issue["sub_patterns"]["g(y)=sqrt(y)"]} problems'
                    })

            elif pattern == 'linear_ode_integration_failure':
                # Check Q(x) patterns
                if 'Q(x)=cos' in issue['sub_patterns'] or 'Q(x)=sin' in issue['sub_patterns']:
                    cos_count = issue['sub_patterns'].get('Q(x)=cos', 0)
                    sin_count = issue['sub_patterns'].get('Q(x)=sin', 0)
                    total_trig = cos_count + sin_count

                    fixes.append({
                        'priority': 'CRITICAL',
                        'issue': 'exp_times_trig_not_matching',
                        'count': total_trig,
                        'fix': 'Debug why exp×trig patterns not matching in ODE context',
                        'file': 'exp_trig_integration_specialist.py',
                        'method': '_integrate_exp_trig',
                        'estimated_impact': f'+{total_trig} problems'
                    })

        # Sort by count (highest impact first)
        fixes.sort(key=lambda x: x['count'], reverse=True)
        return fixes


def main():
    """Main analysis and fix suggestion"""
    # Find latest results
    results_dir = Path("data/benchmarks/results")
    results_files = list(results_dir.glob("ode_suite_*.json"))

    if not results_files:
        print("No benchmark results found! Run benchmark first.")
        return

    latest_file = max(results_files, key=lambda p: p.stat().st_mtime)
    print(f"Analyzing: {latest_file}\n")

    analyzer = ODEFailureAnalyzer(latest_file)
    analysis = analyzer.print_analysis()

    # Suggest fixes
    print("\nRECOMMENDED FIXES (Prioritized by Impact):")
    print("=" * 80)

    fixes = analyzer.suggest_fixes(analysis)

    for i, fix in enumerate(fixes[:10], 1):
        print(f"\n{i}. [{fix['priority']}] {fix['issue']}")
        print(f"   Impact: {fix['count']} problems ({fix['estimated_impact']})")
        print(f"   Fix: {fix['fix']}")
        print(f"   File: {fix['file']}")
        print(f"   Method: {fix['method']}")

    print("\n" + "=" * 80)

    # Save analysis
    analysis_file = results_dir / f"failure_analysis_{latest_file.stem.split('_')[-1]}.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nDetailed analysis saved to: {analysis_file}")


if __name__ == "__main__":
    main()
