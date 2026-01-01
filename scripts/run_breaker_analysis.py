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
Run Algorithm Breaking Agent Analysis
=====================================

Uses the AlgorithmBreakingAgent to find vulnerabilities in key algorithms.
"""

import sys
import os
import math

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Direct import to avoid init cascade
import importlib.util
spec = importlib.util.spec_from_file_location(
    "algorithm_breaking_agent",
    os.path.join(src_path, "system_agents", "algorithm_breaking_agent.py")
)
breaking_agent_module = importlib.util.module_from_spec(spec)

# Mock the BDI imports for standalone use
class MockBDIAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.beliefs = {}
        self.intentions = []

    def has_belief(self, key):
        return key in self.beliefs

    def add_belief(self, key, value, **kwargs):
        self.beliefs[key] = value

    def remove_belief(self, key):
        if key in self.beliefs:
            del self.beliefs[key]

    def get_statistics(self):
        return {}

# Temporarily mock imports
import sys as sys_module
sys_module.modules['symbo_agentic_reasoners'] = type(sys_module)('symbo_agentic_reasoners')
sys_module.modules['symbo_agentic_reasoners.core'] = type(sys_module)('symbo_agentic_reasoners.core')
sys_module.modules['symbo_agentic_reasoners.core.bdi_agent'] = type(sys_module)('symbo_agentic_reasoners.core.bdi_agent')
sys_module.modules['symbo_agentic_reasoners.core.bdi_agent'].BDIAgent = MockBDIAgent
sys_module.modules['symbo_agentic_reasoners.core.bdi_agent'].Intention = type('Intention', (), {})
sys_module.modules['symbo_agentic_reasoners.infrastructure'] = type(sys_module)('symbo_agentic_reasoners.infrastructure')
sys_module.modules['symbo_agentic_reasoners.infrastructure.directory_facilitator'] = type(sys_module)('symbo_agentic_reasoners.infrastructure.directory_facilitator')
sys_module.modules['symbo_agentic_reasoners.infrastructure.directory_facilitator'].DirectoryFacilitator = None
sys_module.modules['symbo_agentic_reasoners.infrastructure.directory_facilitator'].create_service_registration = lambda **kwargs: None
sys_module.modules['symbo_agentic_reasoners.core.blackboard'] = type(sys_module)('symbo_agentic_reasoners.core.blackboard')
sys_module.modules['symbo_agentic_reasoners.core.blackboard'].Blackboard = None
sys_module.modules['symbo_agentic_reasoners.core.blackboard'].create_entry = lambda **kwargs: None
sys_module.modules['symbo_agentic_reasoners.core.blackboard'].EntryType = type('EntryType', (), {'PARTIAL_RESULT': 'partial'})
sys_module.modules['symbo_agentic_reasoners.core.blackboard'].EntryStatus = type('EntryStatus', (), {'PENDING': 'pending', 'IN_PROGRESS': 'in_progress', 'COMPLETED': 'completed'})

spec.loader.exec_module(breaking_agent_module)

AlgorithmBreakingAgent = breaking_agent_module.AlgorithmBreakingAgent
FuzzingCampaign = breaking_agent_module.FuzzingCampaign
AttackStrategy = breaking_agent_module.AttackStrategy


def test_target_factorial(n):
    """Basic factorial - target for testing."""
    if n < 0:
        raise ValueError("factorial not defined for negative numbers")
    if n <= 1:
        return 1
    return n * test_target_factorial(n - 1)


def test_target_binomial(n, k):
    """Binomial coefficient."""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def test_target_newton_raphson(f, x0, tol=1e-10, max_iter=100):
    """Newton-Raphson root finding."""
    h = 1e-8
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = (f(x + h) - f(x - h)) / (2 * h)
        if abs(dfx) < 1e-15:
            return None
        x = x - fx / dfx
    return x


def test_target_simpson(f, a, b, n=1000):
    """Simpson's rule integration."""
    if n % 2 != 0:
        n += 1
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        if i % 2 == 0:
            total += 2 * f(x)
        else:
            total += 4 * f(x)
    return (h / 3) * total


def test_target_horner_eval(coeffs, x):
    """Polynomial evaluation using Horner's method."""
    result = 0
    for c in reversed(coeffs):
        result = result * x + c
    return result


def test_target_gcd(a, b):
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return abs(a)


def test_target_bisection(f, a, b, tol=1e-10, max_iter=100):
    """Bisection root finding."""
    if f(a) * f(b) > 0:
        return None
    for _ in range(max_iter):
        c = (a + b) / 2
        if abs(b - a) < tol or abs(f(c)) < tol:
            return c
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
    return (a + b) / 2


def run_breaking_analysis():
    """Run the breaker agent against test targets."""
    print("=" * 60)
    print("ALGORITHM BREAKING AGENT - CODEBASE VULNERABILITY SCAN")
    print("=" * 60)
    print()

    # Initialize the breaker agent
    breaker = AlgorithmBreakingAgent(agent_id="codebase_scanner")

    # Define test targets
    targets = {
        'factorial': test_target_factorial,
        'binomial': lambda n: test_target_binomial(n, n // 2),
        'horner_eval': lambda x: test_target_horner_eval([1, 2, 3, 4, 5], x),
        'gcd': lambda n: test_target_gcd(n, 100),
    }

    all_results = {}

    # Run analysis on each target
    for name, func in targets.items():
        print(f"\n{'='*60}")
        print(f"ANALYZING: {name}")
        print("=" * 60)

        try:
            result = breaker.break_algorithm(func, name)
            all_results[name] = result

            print(f"\nResults for {name}:")
            print(f"  Inputs tested: {result.inputs_tested}")
            print(f"  Success rate: {result.success_rate:.1%}")
            print(f"  Vulnerabilities found: {len(result.vulnerabilities_found)}")

            if result.vulnerabilities_found:
                print(f"\n  Vulnerabilities:")
                for i, vuln in enumerate(result.vulnerabilities_found[:5], 1):
                    print(f"    {i}. [{vuln.severity.upper()}] {vuln.vulnerability_type.value}")
                    print(f"       Description: {vuln.description}")
                    print(f"       Input: {vuln.triggering_input}")
                    if vuln.recommendations:
                        print(f"       Fix: {vuln.recommendations[0]}")

        except Exception as e:
            print(f"  ERROR: Failed to analyze {name}: {e}")

    # Generate full report
    print("\n" + "=" * 60)
    print("FULL VULNERABILITY REPORT")
    print("=" * 60)
    print(breaker.generate_vulnerability_report())

    # Return stats
    stats = breaker.get_statistics()
    print("\n" + "=" * 60)
    print("FINAL STATISTICS")
    print("=" * 60)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    return all_results, stats


if __name__ == "__main__":
    results, stats = run_breaking_analysis()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_vulns = stats.get('vulnerabilities_found', 0)
    critical = stats.get('critical_vulnerabilities', 0)
    high = stats.get('high_vulnerabilities', 0)

    if critical > 0 or high > 0:
        print(f"  WARNING: Found {critical} critical and {high} high severity issues")
    elif total_vulns > 0:
        print(f"  Found {total_vulns} total vulnerabilities (non-critical)")
    else:
        print("  No vulnerabilities found - algorithms are robust!")
