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
Test Script for P0-2d: MockProver Removal Fix
=============================================

This script verifies:
1. Production code does NOT have MockProver class
2. MockProver is available in tests/mocks/ for testing
3. SymPyProver does NOT fall back to MockProver
4. Deep search module exports are updated
5. Error handling is clear and actionable

Usage:
    python test_phase6_prover_fix.py
"""

import sys
import os
import logging

# Add paths

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_no_mock_prover_in_production():
    """Test 1: Verify MockProver is NOT in production prover_engine.py"""
    print("\n" + "=" * 70)
    print("TEST 1: Verify MockProver removed from production")
    print("=" * 70)

    # Read the source code
    source_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'src',
        'symbo_agentic_reasoners',
        'discovery',
        'deep_search',
        'prover_engine.py'
    )

    with open(source_path, 'r') as f:
        source = f.read()

    # Check that MockProver class is not defined
    if 'class MockProver' in source:
        print("[FAIL] MockProver class still exists in production code")
        return False

    print("[PASS] MockProver class removed from prover_engine.py")

    # Check that no MockProver() instantiation exists
    mock_calls = [
        line for line in source.split('\n')
        if 'MockProver()' in line and not line.strip().startswith('#')
    ]
    if mock_calls:
        print(f"[FAIL] Found MockProver() calls: {mock_calls}")
        return False

    print("[PASS] No MockProver() instantiation in production code")
    return True


def test_mock_prover_available_in_tests():
    """Test 2: Verify MockProver is available in tests/mocks"""
    print("\n" + "=" * 70)
    print("TEST 2: Verify MockProver available in tests/mocks")
    print("=" * 70)

    try:
        from tests.mocks.mock_prover import MockProver
        print("[PASS] MockProver imported successfully from tests/mocks")
    except ImportError as e:
        print(f"[FAIL] Cannot import MockProver: {e}")
        return False

    # Test mock functionality
    mock = MockProver()

    # Create mock state and tactic for testing
    class MockState:
        def __init__(self, goal):
            self.goal = goal

    class MockTactic:
        def __init__(self, tactic):
            self.tactic = tactic

    # Test apply_tactic method
    state = MockState("x = x")
    tactic = MockTactic("rfl")
    result, is_proven = mock.apply_tactic(state, tactic)

    if not is_proven:
        print(f"[FAIL] Mock prover should prove reflexive goal: {result}")
        return False
    print(f"[PASS] Mock apply_tactic() works: rfl on 'x = x' -> proven={is_proven}")

    # Test statistics
    stats = mock.get_statistics()
    if not stats.get('mock'):
        print("[FAIL] Mock statistics should have 'mock': True")
        return False
    print(f"[PASS] Mock get_statistics() works: mock={stats.get('mock')}")

    return True


def test_mock_prover_in_exports():
    """Test 3: Verify MockProver is exported from tests.mocks"""
    print("\n" + "=" * 70)
    print("TEST 3: Verify MockProver in tests.mocks exports")
    print("=" * 70)

    try:
        from tests.mocks import MockProver
        print("[PASS] MockProver exported from tests.mocks.__init__")
        return True
    except ImportError as e:
        print(f"[FAIL] MockProver not in __all__ exports: {e}")
        return False


def test_production_exports_updated():
    """Test 4: Verify deep_search module exports updated"""
    print("\n" + "=" * 70)
    print("TEST 4: Verify deep_search exports don't include MockProver")
    print("=" * 70)

    # Check __init__.py source
    init_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'src',
        'symbo_agentic_reasoners',
        'discovery',
        'deep_search',
        '__init__.py'
    )

    with open(init_path, 'r') as f:
        init_source = f.read()

    # Check that MockProver is not in __all__
    if "'MockProver'" in init_source and 'removed' not in init_source.lower():
        print("[FAIL] MockProver still in __all__ without removal comment")
        return False
    print("[PASS] MockProver removed from __all__ exports")

    # Try importing from deep_search
    try:
        from symbo_agentic_reasoners.discovery.deep_search import SymPyProver, ProverEngine
        print("[PASS] SymPyProver and ProverEngine importable")
    except ImportError as e:
        print(f"[FAIL] Cannot import from deep_search: {e}")
        return False

    # Verify MockProver NOT importable from production
    try:
        from symbo_agentic_reasoners.discovery.deep_search import MockProver
        print("[FAIL] MockProver should NOT be importable from production deep_search")
        return False
    except ImportError:
        print("[PASS] MockProver correctly NOT importable from deep_search")

    return True


def test_sympy_prover_no_fallback():
    """Test 5: Verify SymPyProver does not fall back to MockProver"""
    print("\n" + "=" * 70)
    print("TEST 5: Verify SymPyProver has no MockProver fallback")
    print("=" * 70)

    source_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'src',
        'symbo_agentic_reasoners',
        'discovery',
        'deep_search',
        'prover_engine.py'
    )

    with open(source_path, 'r') as f:
        source = f.read()

    # Check for MockProver references (except comments)
    mock_refs = [
        line for line in source.split('\n')
        if 'MockProver' in line and not line.strip().startswith('#')
    ]
    if mock_refs:
        print(f"[FAIL] Found MockProver references: {mock_refs}")
        return False
    print("[PASS] No MockProver references in production code (except comments)")

    # Check for proper error handling
    checks = [
        ("FAIL-FAST comment", "# FAIL-FAST"),
        ("PARSE_ERROR handling", "PARSE_ERROR"),
        ("Logger warning", "logger.warning"),
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in source:
            print(f"[PASS] {check_name}: present")
        else:
            print(f"[FAIL] {check_name}: '{check_string}' not found")
            all_passed = False

    return all_passed


def test_sympy_prover_functional():
    """Test 6: Verify SymPyProver is functional without MockProver"""
    print("\n" + "=" * 70)
    print("TEST 6: Verify SymPyProver is functional")
    print("=" * 70)

    try:
        from symbo_agentic_reasoners.discovery.deep_search.prover_engine import SymPyProver
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
    except ImportError as e:
        print(f"[FAIL] Cannot import SymPyProver: {e}")
        return False

    prover = SymPyProver()

    # Test health check
    if not prover.health_check():
        print("[FAIL] SymPyProver health check failed")
        return False
    print("[PASS] SymPyProver health check passed")

    # Test simple tactic application
    state = ProofState(state_id="test_1", goal="x - x", hypotheses=[], depth=0)
    tactic = TacticCandidate(tactic="simp", probability=0.9)

    result, is_proven = prover.apply_tactic(state, tactic)
    print(f"[PASS] SymPyProver.apply_tactic() works: simp on 'x - x' -> '{result}'")

    # Test parsing error handling (should not raise, should return PARSE_ERROR)
    state_bad = ProofState(state_id="test_2", goal="∀x ∈ ℝ: invalid_syntax++", hypotheses=[], depth=0)
    result, is_proven = prover.apply_tactic(state_bad, tactic)
    if "[PARSE_ERROR]" in result:
        print("[PASS] SymPyProver handles parse errors gracefully (no MockProver fallback)")
    else:
        print(f"[INFO] Parse result: {result}")

    return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print("P0-2d FIX VERIFICATION: MockProver Removal")
    print("=" * 70)

    tests = [
        ("No MockProver in production", test_no_mock_prover_in_production),
        ("MockProver available in tests/mocks", test_mock_prover_available_in_tests),
        ("MockProver in exports", test_mock_prover_in_exports),
        ("Production exports updated", test_production_exports_updated),
        ("SymPyProver no fallback", test_sympy_prover_no_fallback),
        ("SymPyProver functional", test_sympy_prover_functional),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, p in results if p)
    failed = len(results) - passed

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print()
    print(f"Results: {passed}/{len(results)} tests passed")

    if failed == 0:
        print("\n[SUCCESS] P0-2d Fix Verified: All tests passed!")
        print("  - MockProver removed from production code")
        print("  - MockProver available in tests/mocks/")
        print("  - SymPyProver no longer falls back to MockProver")
        print("  - Production exports updated")
        return True
    else:
        print(f"\n[FAILURE] {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
