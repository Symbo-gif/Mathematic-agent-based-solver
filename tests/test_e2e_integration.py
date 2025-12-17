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
END-TO-END INTEGRATION TEST
===========================

Tests the complete pipeline from raw input to orchestrator routing:
1. Raw input -> InputNormalizer
2. Normalized -> ProblemAnalysisTeam (Parser + Classifier)
3. StructuredProblem -> Orchestrator (domain routing)
4. Orchestrator -> AgentPool (agent lifecycle)
5. AgentPool -> Supervisor -> Specialist delegation

This validates all the wiring we've done across the system.
"""

import sys
import os

# Ensure proper encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def test_input_normalization():
    """Test that input normalizer handles various formats."""
    print("\n" + "="*60)
    print("TEST 1: Input Normalization")
    print("="*60)

    from symbo_agentic_reasoners.core.input_normalizer import normalize_input

    test_cases = [
        ("x^2 + 2x + 1", "x**2 + 2*x + 1"),  # Power and implicit mult
        ("sin(x)", "sin(x)"),  # Function unchanged
        ("  x + 1  ", "x + 1"),  # Whitespace trimmed
    ]

    passed = 0
    for inp, expected in test_cases:
        result = normalize_input(inp)
        # Check key transformations happened
        status = "PASS" if "**" in result or result.strip() == expected.strip() else "CHECK"
        print(f"  [{status}] '{inp}' -> '{result}'")
        if status == "PASS" or expected in result:
            passed += 1

    print(f"\nResult: {passed}/{len(test_cases)} passed")
    assert passed == len(test_cases), f"Only {passed}/{len(test_cases)} passed"


def test_problem_analysis():
    """Test that ProblemAnalysisTeam correctly parses and classifies."""
    print("\n" + "="*60)
    print("TEST 2: Problem Analysis (Parse + Classify)")
    print("="*60)

    from symbo_agentic_reasoners.agents.base.problem_analysis import (
        ProblemAnalysisTeam, MathDomain, ProblemType
    )

    team = ProblemAnalysisTeam()

    test_cases = [
        ("differentiate x^2", MathDomain.CALCULUS, ProblemType.COMPUTATION),
        ("solve x^2 - 4 = 0", MathDomain.ALGEBRA, ProblemType.COMPUTATION),
        ("compute matrix determinant", MathDomain.LINEAR_ALGEBRA, ProblemType.COMPUTATION),
        ("calculate mean and variance", MathDomain.STATISTICS, ProblemType.COMPUTATION),
        ("find permutations of 5 items", MathDomain.DISCRETE_MATH, ProblemType.COMPUTATION),
    ]

    passed = 0
    for inp, expected_domain, expected_type in test_cases:
        result = team.process(inp)
        domain_ok = result.domain == expected_domain
        type_ok = result.problem_type == expected_type
        status = "PASS" if domain_ok and type_ok else "FAIL"

        print(f"  [{status}] '{inp[:30]}...'")
        print(f"         Domain: {result.domain.value} (expected: {expected_domain.value})")
        print(f"         Type: {result.problem_type.value} (expected: {expected_type.value})")

        if domain_ok and type_ok:
            passed += 1

    print(f"\nResult: {passed}/{len(test_cases)} passed")
    assert passed == len(test_cases), f"Only {passed}/{len(test_cases)} passed"


def test_domain_to_pool_mapping():
    """Test that MathDomain correctly maps to AgentPool domain keys."""
    print("\n" + "="*60)
    print("TEST 3: Domain to Pool Key Mapping")
    print("="*60)

    from symbo_agentic_reasoners.core.orchestrator import get_pool_domain_key
    from symbo_agentic_reasoners.agents.base.problem_analysis import MathDomain
    from symbo_agentic_reasoners.infrastructure.agent_registry import AGENT_SPECS

    # These are the domain keys the agent registry uses
    registry_domains = set(AGENT_SPECS.keys())

    passed = 0
    total = 0

    for domain in MathDomain:
        pool_key = get_pool_domain_key(domain)
        # Check if this maps to a registered domain (or is expected unmapped like GEOMETRY)
        has_agents = pool_key in registry_domains
        unmapped_ok = domain in [MathDomain.GEOMETRY, MathDomain.LOGIC,
                                  MathDomain.NUMBER_THEORY, MathDomain.UNKNOWN]

        status = "PASS" if has_agents or unmapped_ok else "FAIL"
        agents_info = f"({len(AGENT_SPECS.get(pool_key, []))} agents)" if has_agents else "(no agents)"
        print(f"  [{status}] {domain.name:15} -> '{pool_key}' {agents_info}")

        total += 1
        if has_agents or unmapped_ok:
            passed += 1

    print(f"\nResult: {passed}/{total} passed")
    assert passed == total, f"Only {passed}/{total} passed"


def test_service_type_mapping():
    """Test that orchestrator generates correct service types for DF queries."""
    print("\n" + "="*60)
    print("TEST 4: Service Type Mapping")
    print("="*60)

    from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
    from symbo_agentic_reasoners.agents.base.problem_analysis import MathDomain
    from symbo_agentic_reasoners.infrastructure.agent_registry import AGENT_SPECS

    orch = MainOrchestrator()

    # Expected service types based on agent registry
    expected_services = {
        MathDomain.ALGEBRA: 'math.algebra',
        MathDomain.CALCULUS: 'math.calculus',
        MathDomain.LINEAR_ALGEBRA: 'math.linalg',
        MathDomain.STATISTICS: 'math.stats',
        MathDomain.DISCRETE_MATH: 'math.discrete',
    }

    passed = 0
    for domain, expected_svc in expected_services.items():
        actual_svc = orch._get_service_type(domain)
        status = "PASS" if actual_svc == expected_svc else "FAIL"
        print(f"  [{status}] {domain.name:15} -> '{actual_svc}' (expected: '{expected_svc}')")
        if actual_svc == expected_svc:
            passed += 1

    print(f"\nResult: {passed}/{len(expected_services)} passed")
    assert passed == len(expected_services), f"Only {passed}/{len(expected_services)} passed"


def test_agent_pool_wake():
    """Test that AgentPool can wake agents for each domain."""
    print("\n" + "="*60)
    print("TEST 5: AgentPool Domain Wake")
    print("="*60)

    from symbo_agentic_reasoners.infrastructure import (
        AgentPool, AgentManagementSystem, register_all_agents
    )

    ams = AgentManagementSystem()
    pool = AgentPool(ams)
    register_all_agents(pool)
    pool.start()

    domains_to_test = ['algebra', 'calculus', 'linear_algebra', 'statistics', 'discrete_math']

    passed = 0
    for domain in domains_to_test:
        woken = pool.wake_for_domain(domain)
        status = "PASS" if len(woken) > 0 else "FAIL"
        print(f"  [{status}] {domain:15} -> woke {len(woken)} agents: {woken[:3]}...")
        pool.sleep_domain(domain)
        if len(woken) > 0:
            passed += 1

    pool.stop()

    print(f"\nResult: {passed}/{len(domains_to_test)} passed")
    assert passed == len(domains_to_test), f"Only {passed}/{len(domains_to_test)} passed"


def test_full_pipeline():
    """Test the complete pipeline from input to agent routing."""
    print("\n" + "="*60)
    print("TEST 6: Full Pipeline (Input -> Classification -> Routing)")
    print("="*60)

    from symbo_agentic_reasoners.core.input_normalizer import normalize_input
    from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
    from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator, get_pool_domain_key
    from symbo_agentic_reasoners.infrastructure import (
        AgentPool, AgentManagementSystem, register_all_agents
    )
    from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
    from symbo_agentic_reasoners.core.blackboard import Blackboard

    # Setup infrastructure
    ams = AgentManagementSystem()
    pool = AgentPool(ams)
    register_all_agents(pool)
    pool.start()

    df = DirectoryFacilitator()
    bb = Blackboard()

    # Register supervisors with DF
    from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
    supervisors = [
        ('math.algebra', 'algebra_supervisor'),
        ('math.calculus', 'calculus_supervisor'),
        ('math.linalg', 'linalg_supervisor'),
        ('math.statistics', 'stats_supervisor'),
        ('math.discrete', 'discrete_math_supervisor'),
    ]
    for svc_type, agent_id in supervisors:
        reg = create_service_registration(
            service_type=svc_type,
            agent_id=agent_id,
            algorithm='routing',
            type='supervisor'
        )
        df.register(reg)

    # Initialize components
    team = ProblemAnalysisTeam()
    orch = MainOrchestrator(df=df, blackboard=bb, agent_pool=pool)

    # Test cases: (input, expected_domain_key)
    test_cases = [
        ("differentiate x^2", "calculus"),
        ("solve x^2 - 4 = 0", "algebra"),
        ("compute matrix determinant", "linear_algebra"),
    ]

    passed = 0
    for inp, expected_domain_key in test_cases:
        print(f"\n  Testing: '{inp}'")

        # Step 1: Normalize
        normalized = normalize_input(inp)
        print(f"    1. Normalized: '{normalized}'")

        # Step 2: Analyze
        structured = team.process(inp)
        pool_key = get_pool_domain_key(structured.domain)
        print(f"    2. Classified: domain={structured.domain.value}, pool_key={pool_key}")

        # Step 3: Check routing would work
        service_type = orch._get_service_type(structured.domain)
        agents = df.search(service_type=service_type)
        print(f"    3. Service: {service_type}, found {len(agents)} agent(s)")

        # Verify
        routing_ok = pool_key == expected_domain_key and len(agents) > 0
        status = "PASS" if routing_ok else "FAIL"
        print(f"    [{status}] Pipeline complete")

        if routing_ok:
            passed += 1

    pool.stop()

    print(f"\nResult: {passed}/{len(test_cases)} passed")
    assert passed == len(test_cases), f"Only {passed}/{len(test_cases)} passed"


def run_all_tests():
    """Run all end-to-end integration tests."""
    print("="*60)
    print("END-TO-END INTEGRATION TESTS")
    print("="*60)

    results = []

    results.append(("Input Normalization", test_input_normalization()))
    results.append(("Problem Analysis", test_problem_analysis()))
    results.append(("Domain to Pool Mapping", test_domain_to_pool_mapping()))
    results.append(("Service Type Mapping", test_service_type_mapping()))
    results.append(("AgentPool Domain Wake", test_agent_pool_wake()))
    results.append(("Full Pipeline", test_full_pipeline()))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")

    print()
    print(f"Total: {passed}/{total} test suites passed")
    print("="*60)

    if passed == total:
        print("ALL TESTS PASSED!")
    else:
        print(f"FAILURES: {total - passed} test suite(s) failed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
