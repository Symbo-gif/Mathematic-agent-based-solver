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
UNIFIED BRUTAL STRESS TEST RUNNER
==================================

Executes all 700 brutal stress tests across 14 mathematical domains
and generates a comprehensive failure report for diagnostic analysis.

Phase 1: Run all tests
Phase 2: Collect failures for diagnostic test generation
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "tests"))

import numpy as np


@dataclass
class TestResult:
    """Result of a single stress test execution."""
    test_id: str
    domain: str
    category: str
    passed: bool
    expected: Any
    actual: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    difficulty: str = "brutal"
    rationale: str = ""
    input_data: str = ""


class StressTestRunner:
    """
    Unified runner for all 700 brutal stress tests.
    """

    def __init__(self):
        self.results: List[TestResult] = []
        self.failures: List[TestResult] = []
        self.domain_stats: Dict[str, Dict[str, int]] = {}
        self.specialists = {}
        self._load_start_time = time.time()

    def load_specialists(self):
        """Lazy load all specialists needed for testing."""
        print("Loading specialists...")

        # Algebra specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.algebra import (
                ArithmeticSpecialist, PolynomialSpecialist, NumberTheorySpecialist
            )
            self.specialists['algebra'] = {
                'arithmetic': ArithmeticSpecialist(),
                'polynomial': PolynomialSpecialist(),
                'number_theory': NumberTheorySpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Algebra specialists: {e}")

        # Calculus specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.calculus import (
                DifferentiationSpecialist, IntegrationSpecialist, LimitEvaluator
            )
            self.specialists['calculus'] = {
                'differentiation': DifferentiationSpecialist(),
                'integration': IntegrationSpecialist(),
                'limits': LimitEvaluator()
            }
        except Exception as e:
            print(f"  [WARN] Calculus specialists: {e}")

        # Linear Algebra specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.linear_algebra import (
                MatrixOperationsSpecialist, DecompositionSpecialist
            )
            self.specialists['linalg'] = {
                'matrix_ops': MatrixOperationsSpecialist(),
                'decomposition': DecompositionSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Linear Algebra specialists: {e}")

        # Statistics specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.statistics import (
                DistributionSpecialist, BayesianInferenceEngine
            )
            self.specialists['statistics'] = {
                'distribution': DistributionSpecialist(),
                'bayesian': BayesianInferenceEngine()
            }
        except Exception as e:
            print(f"  [WARN] Statistics specialists: {e}")

        # Geometry specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.geometry import (
                EuclideanGeometrySpecialist, TrigonometrySpecialist
            )
            self.specialists['geometry'] = {
                'euclidean': EuclideanGeometrySpecialist(),
                'trigonometry': TrigonometrySpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Geometry specialists: {e}")

        # Physics specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.physics.mechanics import (
                KinematicsSpecialist, DynamicsSpecialist
            )
            self.specialists['physics'] = {
                'kinematics': KinematicsSpecialist(),
                'dynamics': DynamicsSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Physics specialists: {e}")

        # Logic specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.logic import (
                PropositionalLogicSpecialist, PredicateLogicSpecialist
            )
            self.specialists['logic'] = {
                'propositional': PropositionalLogicSpecialist(),
                'predicate': PredicateLogicSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Logic specialists: {e}")

        # Discrete Math specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math import (
                CombinatoricsAgent, GraphTheoryAgent
            )
            self.specialists['discrete_math'] = {
                'combinatorics': CombinatoricsAgent(),
                'graph_theory': GraphTheoryAgent()
            }
        except Exception as e:
            print(f"  [WARN] Discrete Math specialists: {e}")

        # Numerical specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.numerical import (
                NumericalMethodsSpecialist
            )
            self.specialists['numerical'] = {
                'numerical': NumericalMethodsSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Numerical specialists: {e}")

        # Complex Analysis specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.complex_analysis import (
                AnalyticFunctionsSpecialist, ResidueCalculusSpecialist
            )
            self.specialists['complex_analysis'] = {
                'analytic': AnalyticFunctionsSpecialist(),
                'residue': ResidueCalculusSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Complex Analysis specialists: {e}")

        # Real Analysis specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.real_analysis import (
                MeasureTheorySpecialist, SequencesSeriesSpecialist
            )
            self.specialists['real_analysis'] = {
                'measure': MeasureTheorySpecialist(),
                'sequences': SequencesSeriesSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Real Analysis specialists: {e}")

        # Functional Analysis specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.functional_analysis import (
                BanachSpaceSpecialist, HilbertSpaceSpecialist
            )
            self.specialists['functional_analysis'] = {
                'banach': BanachSpaceSpecialist(),
                'hilbert': HilbertSpaceSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Functional Analysis specialists: {e}")

        # Differential Geometry specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.differential_geometry import (
                CurvatureSpecialist, GeodesicSpecialist
            )
            self.specialists['diff_geometry'] = {
                'curvature': CurvatureSpecialist(),
                'geodesic': GeodesicSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Differential Geometry specialists: {e}")

        # Control Theory specialists
        try:
            from symbo_agentic_reasoners.agents.specialists.control_theory import (
                DynamicalSystemsSpecialist, LinearControlSpecialist
            )
            self.specialists['control_theory'] = {
                'dynamical': DynamicalSystemsSpecialist(),
                'linear_control': LinearControlSpecialist()
            }
        except Exception as e:
            print(f"  [WARN] Control Theory specialists: {e}")

        print(f"Loaded {len(self.specialists)} domain specialist groups in {time.time() - self._load_start_time:.2f}s")

    def load_all_tests(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all test definitions from all 14 test files."""
        all_tests = {}

        # Load Algebra tests
        try:
            from brutal_algebra_stress_tests import get_brutal_algebra_tests
            all_tests['algebra'] = get_brutal_algebra_tests()
        except Exception as e:
            print(f"  [WARN] Loading algebra tests: {e}")
            all_tests['algebra'] = []

        # Load Calculus tests (uses constant)
        try:
            from brutal_calculus_stress_tests import BRUTAL_CALCULUS_STRESS_TESTS
            all_tests['calculus'] = BRUTAL_CALCULUS_STRESS_TESTS
        except Exception as e:
            print(f"  [WARN] Loading calculus tests: {e}")
            all_tests['calculus'] = []

        # Load Linear Algebra tests (uses constant)
        try:
            from brutal_linalg_stress_tests import BRUTAL_LINALG_TESTS
            all_tests['linalg'] = BRUTAL_LINALG_TESTS
        except Exception as e:
            print(f"  [WARN] Loading linalg tests: {e}")
            all_tests['linalg'] = []

        # Load Statistics tests (uses constant)
        try:
            from brutal_statistics_stress_tests import BRUTAL_STATISTICS_TESTS
            all_tests['statistics'] = BRUTAL_STATISTICS_TESTS
        except Exception as e:
            print(f"  [WARN] Loading statistics tests: {e}")
            all_tests['statistics'] = []

        # Load Geometry tests
        try:
            from geometry_brutal_stress_tests import get_brutal_geometry_tests
            all_tests['geometry'] = get_brutal_geometry_tests()
        except Exception as e:
            print(f"  [WARN] Loading geometry tests: {e}")
            all_tests['geometry'] = []

        # Load Physics tests
        try:
            from brutal_physics_stress_tests import get_brutal_physics_tests
            all_tests['physics'] = get_brutal_physics_tests()
        except Exception as e:
            print(f"  [WARN] Loading physics tests: {e}")
            all_tests['physics'] = []

        # Load Logic tests (uses constant)
        try:
            from brutal_logic_stress_tests import BRUTAL_LOGIC_TESTS
            all_tests['logic'] = BRUTAL_LOGIC_TESTS
        except Exception as e:
            print(f"  [WARN] Loading logic tests: {e}")
            all_tests['logic'] = []

        # Load Discrete Math tests (uses constant)
        try:
            from discrete_math_brutal_stress_tests import DISCRETE_MATH_BRUTAL_TESTS
            all_tests['discrete_math'] = DISCRETE_MATH_BRUTAL_TESTS
        except Exception as e:
            print(f"  [WARN] Loading discrete math tests: {e}")
            all_tests['discrete_math'] = []

        # Load Numerical tests (uses constant)
        try:
            from brutal_numerical_stress_tests import BRUTAL_NUMERICAL_TESTS
            all_tests['numerical'] = BRUTAL_NUMERICAL_TESTS
        except Exception as e:
            print(f"  [WARN] Loading numerical tests: {e}")
            all_tests['numerical'] = []

        # Load Complex Analysis tests (module-level constants)
        try:
            import complex_analysis_stress_tests as cplx
            tests = []
            for attr in dir(cplx):
                if attr.endswith('_TESTS') and isinstance(getattr(cplx, attr), list):
                    tests.extend(getattr(cplx, attr))
            all_tests['complex_analysis'] = tests
        except Exception as e:
            print(f"  [WARN] Loading complex analysis tests: {e}")
            all_tests['complex_analysis'] = []

        # Load Real Analysis tests (uses constant)
        try:
            from real_analysis_brutal_stress_tests import REAL_ANALYSIS_BRUTAL_TESTS
            all_tests['real_analysis'] = REAL_ANALYSIS_BRUTAL_TESTS
        except Exception as e:
            print(f"  [WARN] Loading real analysis tests: {e}")
            all_tests['real_analysis'] = []

        # Load Functional Analysis tests (module-level constants)
        try:
            import functional_analysis_stress_tests as func
            tests = []
            for attr in dir(func):
                if attr.endswith('_TESTS') and isinstance(getattr(func, attr), list):
                    tests.extend(getattr(func, attr))
            all_tests['functional_analysis'] = tests
        except Exception as e:
            print(f"  [WARN] Loading functional analysis tests: {e}")
            all_tests['functional_analysis'] = []

        # Load Differential Geometry tests (module-level constants)
        try:
            import diff_geometry_topology_stress_tests as diff_geo
            tests = []
            for attr in dir(diff_geo):
                if attr.endswith('_TESTS') and isinstance(getattr(diff_geo, attr), list):
                    tests.extend(getattr(diff_geo, attr))
            all_tests['diff_geometry'] = tests
        except Exception as e:
            print(f"  [WARN] Loading diff geometry tests: {e}")
            all_tests['diff_geometry'] = []

        # Load Control Theory tests (module-level constants)
        try:
            import control_theory_stress_tests as ctrl
            if hasattr(ctrl, 'CONTROL_THEORY_STRESS_TESTS'):
                all_tests['control_theory'] = ctrl.CONTROL_THEORY_STRESS_TESTS
            else:
                tests = []
                for attr in dir(ctrl):
                    if attr.endswith('_TESTS') and isinstance(getattr(ctrl, attr), list):
                        tests.extend(getattr(ctrl, attr))
                all_tests['control_theory'] = tests
        except Exception as e:
            print(f"  [WARN] Loading control theory tests: {e}")
            all_tests['control_theory'] = []

        # Summary
        total = sum(len(tests) for tests in all_tests.values())
        print(f"\nLoaded {total} tests across {len(all_tests)} domains:")
        for domain, tests in all_tests.items():
            print(f"  {domain}: {len(tests)} tests")

        return all_tests

    def execute_test(self, test: Dict[str, Any], domain: str) -> TestResult:
        """Execute a single test using the solver engine."""
        test_id = test.get('test_id', 'UNKNOWN')
        category = test.get('category', 'general')
        expected = test.get('expected', None)
        difficulty = test.get('difficulty', 'brutal')
        rationale = test.get('rationale', '')
        input_data = test.get('input', '')

        start = time.time()

        try:
            # Import solver
            from symbo_agentic_reasoners.core.solver_engine import solve, SolveStatus

            # Parse input - handle both string and dict inputs
            if isinstance(input_data, dict):
                # Some tests have structured inputs
                expr = input_data.get('expression') or input_data.get('system') or str(input_data)
            else:
                expr = str(input_data)

            # Execute via solver engine
            result = solve(expr)

            if result.status == SolveStatus.SUCCESS:
                actual = result.result
                # Check if result matches expected
                passed = self._check_result(actual, expected)
                error = None if passed else f"Mismatch: expected {expected}, got {actual}"
            elif result.status == SolveStatus.PARTIAL:
                actual = result.result
                passed = self._check_result(actual, expected)
                error = None if passed else f"Partial result: {result.error}"
            else:
                actual = None
                passed = False
                error = f"Solver error: {result.error}"

        except Exception as e:
            actual = None
            passed = False
            error = f"{type(e).__name__}: {str(e)}"

        elapsed = time.time() - start

        return TestResult(
            test_id=test_id,
            domain=domain,
            category=category,
            passed=passed,
            expected=expected,
            actual=actual,
            error=error,
            execution_time=elapsed,
            difficulty=difficulty,
            rationale=rationale,
            input_data=str(input_data)[:500]
        )

    def _check_result(self, actual: Any, expected: Any) -> bool:
        """Check if actual result matches expected."""
        if expected is None:
            return actual is not None

        # Handle string descriptions (these are specification tests)
        if isinstance(expected, str):
            # If expected is a description, check for key terms in result
            exp_lower = str(expected).lower()
            act_str = str(actual).lower()

            # Check for exact match or containment
            if str(expected) == str(actual):
                return True

            # Check for numeric approximate match
            try:
                exp_val = float(expected)
                if isinstance(actual, (int, float, complex)):
                    return abs(float(actual) - exp_val) < 1e-6 * max(abs(exp_val), 1)
            except (ValueError, TypeError):
                pass

            # Check for key terms
            key_terms = ['converge', 'diverge', 'stable', 'unstable', 'singular',
                        'solution', 'root', 'zero', 'pole', 'branch']
            for term in key_terms:
                if term in exp_lower and term in act_str:
                    return True

            return False

        # Numeric comparison
        if isinstance(expected, (int, float)):
            try:
                return abs(float(actual) - float(expected)) < 1e-9 * max(abs(expected), 1)
            except (ValueError, TypeError):
                return False

        # Dict comparison
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                return False
            for key in expected:
                if key not in actual:
                    return False
                if not self._check_result(actual[key], expected[key]):
                    return False
            return True

        # List comparison
        if isinstance(expected, (list, tuple)):
            if not isinstance(actual, (list, tuple)):
                return False
            if len(expected) != len(actual):
                return False
            return all(self._check_result(a, e) for a, e in zip(actual, expected))

        # Default string comparison
        return str(actual) == str(expected)

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report."""
        print("\n" + "="*70)
        print("BRUTAL STRESS TEST RUNNER - Phase 1: Execute All Tests")
        print("="*70)

        # Load tests
        print("\nLoading test definitions...")
        all_tests = self.load_all_tests()

        # Load specialists
        self.load_specialists()

        # Execute tests
        print("\nExecuting tests...")
        total_tests = 0
        for domain, tests in all_tests.items():
            domain_passed = 0
            domain_failed = 0

            for test in tests:
                result = self.execute_test(test, domain)
                self.results.append(result)
                total_tests += 1

                if result.passed:
                    domain_passed += 1
                else:
                    domain_failed += 1
                    self.failures.append(result)

            self.domain_stats[domain] = {
                'total': len(tests),
                'passed': domain_passed,
                'failed': domain_failed,
                'pass_rate': domain_passed / len(tests) * 100 if tests else 0
            }

            status = "PASS" if domain_failed == 0 else "FAIL"
            print(f"  [{status}] {domain}: {domain_passed}/{len(tests)} passed")

        # Generate report
        report = self.generate_report()

        # Save report
        self.save_report(report)

        return report

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive failure report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(self.results),
                'total_passed': len(self.results) - len(self.failures),
                'total_failed': len(self.failures),
                'pass_rate': (len(self.results) - len(self.failures)) / len(self.results) * 100 if self.results else 0
            },
            'domain_stats': self.domain_stats,
            'failures_by_domain': self._group_failures_by_domain(),
            'failures_by_category': self._group_failures_by_category(),
            'all_failures': [self._result_to_dict(f) for f in self.failures]
        }

    def _group_failures_by_domain(self) -> Dict[str, List[Dict]]:
        """Group failures by domain for targeted fixing."""
        grouped = {}
        for f in self.failures:
            if f.domain not in grouped:
                grouped[f.domain] = []
            grouped[f.domain].append(self._result_to_dict(f))
        return grouped

    def _group_failures_by_category(self) -> Dict[str, List[Dict]]:
        """Group failures by category for pattern analysis."""
        grouped = {}
        for f in self.failures:
            if f.category not in grouped:
                grouped[f.category] = []
            grouped[f.category].append(self._result_to_dict(f))
        return grouped

    def _result_to_dict(self, result: TestResult) -> Dict:
        """Convert TestResult to serializable dict."""
        return {
            'test_id': result.test_id,
            'domain': result.domain,
            'category': result.category,
            'passed': result.passed,
            'expected': str(result.expected)[:500] if result.expected else None,
            'actual': str(result.actual)[:500] if result.actual else None,
            'error': result.error[:1000] if result.error else None,
            'execution_time': result.execution_time,
            'difficulty': result.difficulty,
            'rationale': result.rationale[:500] if result.rationale else '',
            'input_data': result.input_data[:500] if result.input_data else ''
        }

    def save_report(self, report: Dict[str, Any]):
        """Save report to JSON file."""
        output_path = PROJECT_ROOT / "tests" / "stress_test_report.json"
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nReport saved to: {output_path}")

        # Also print summary
        print("\n" + "="*70)
        print("STRESS TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['total_passed']}")
        print(f"Failed: {report['summary']['total_failed']}")
        print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
        print("\nDomain Breakdown:")
        for domain, stats in report['domain_stats'].items():
            print(f"  {domain}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.1f}%)")


def main():
    """Main entry point."""
    runner = StressTestRunner()
    report = runner.run_all_tests()

    # Count failures for Phase 2
    num_failures = len(report['all_failures'])
    print(f"\n{'='*70}")
    print(f"PHASE 2 REQUIRED: {num_failures} failures need diagnostic tests")
    print(f"  (20 diagnostic tests per failure = {num_failures * 20} total diagnostic tests)")
    print(f"{'='*70}")

    return report


if __name__ == "__main__":
    main()
