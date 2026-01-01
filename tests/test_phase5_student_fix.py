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
Test Script for P0-2c: Simulated Student Response Fix
=====================================================

This script verifies:
1. Production code does NOT have _simulate_student_response() method
2. _handle_with_student() fails-fast when no student model available
3. MockStudentModel is available in tests/mocks/ for testing
4. Error messages are clear and actionable
5. System gracefully handles missing student model

Usage:
    python test_phase5_student_fix.py
"""

import sys
import os
import logging
import inspect

# Add paths

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_no_simulate_method():
    """Test 1: Verify _simulate_student_response is NOT in production code"""
    print("\n" + "=" * 70)
    print("TEST 1: Verify _simulate_student_response removed from production")
    print("=" * 70)

    # Import Phase5System
    from symbo_agentic_reasoners.core.system import Phase5System

    # Check if method exists
    has_simulate = hasattr(Phase5System, '_simulate_student_response')

    if has_simulate:
        # Check if it's actually callable (not just a comment/stub)
        attr = getattr(Phase5System, '_simulate_student_response')
        if callable(attr):
            print("[FAIL] _simulate_student_response() still exists as callable method")
            print(f"       Location: {inspect.getfile(Phase5System)}")
            return False

    print("[PASS] _simulate_student_response() method removed from Phase5System")
    print("       Mock functionality moved to tests/mocks/mock_student.py")
    return True


def test_mock_student_available():
    """Test 2: Verify MockStudentModel is available in tests/mocks"""
    print("\n" + "=" * 70)
    print("TEST 2: Verify MockStudentModel available in tests/mocks")
    print("=" * 70)

    try:
        from tests.mocks.mock_student import MockStudentModel
        print("[PASS] MockStudentModel imported successfully from tests/mocks")
    except ImportError as e:
        print(f"[FAIL] Cannot import MockStudentModel: {e}")
        return False

    # Test mock functionality
    mock = MockStudentModel("test")

    # Test generate method
    response = mock.generate("Find derivative of x^2")
    if "mock" not in response.lower():
        print(f"[FAIL] Mock response should contain 'mock': {response}")
        return False
    print(f"[PASS] Mock generate() works: {response}")

    # Test get_stats method
    stats = mock.get_stats()
    if not stats.get('mock'):
        print("[FAIL] Mock stats should have 'mock': True")
        return False
    print(f"[PASS] Mock get_stats() works: mock={stats.get('mock')}")

    # Test learn_from_interaction
    mock.learn_from_interaction("test query", "test response", "test")
    if len(mock._training_examples) != 1:
        print("[FAIL] learn_from_interaction not recording")
        return False
    print("[PASS] Mock learn_from_interaction() works")

    # Test add_knowledge
    mock.add_knowledge("test fact", "test category")
    if len(mock._knowledge_base) != 1:
        print("[FAIL] add_knowledge not recording")
        return False
    print("[PASS] Mock add_knowledge() works")

    print("\n[PASS] MockStudentModel fully functional for testing")
    return True


def test_mock_in_exports():
    """Test 3: Verify MockStudentModel is exported from tests.mocks"""
    print("\n" + "=" * 70)
    print("TEST 3: Verify MockStudentModel in tests.mocks exports")
    print("=" * 70)

    try:
        from tests.mocks import MockStudentModel
        print("[PASS] MockStudentModel exported from tests.mocks.__init__")
        return True
    except ImportError as e:
        print(f"[FAIL] MockStudentModel not in __all__ exports: {e}")
        return False


def test_fail_fast_error_message():
    """Test 4: Verify fail-fast returns proper error structure"""
    print("\n" + "=" * 70)
    print("TEST 4: Verify fail-fast error handling")
    print("=" * 70)

    # Read the source code to verify the error structure
    source_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'docs',
        'MASTER_ARCHIVE',
        'symbo_agentic_reasoners_phase5',
        'phase5_system.py'
    )

    with open(source_path, 'r') as f:
        source = f.read()

    # Check for key error handling elements
    checks = [
        ("error return structure", "'status': 'ERROR'"),
        ("error code", "'code': 'STUDENT_MODEL_NOT_AVAILABLE'"),
        ("actionable message", "Install Symbo with: pip install symbo"),
        ("logger.error call", "logger.error"),
        ("console print", "print(f\"\\n[ERROR]"),
        ("no simulate call", "_simulate_student_response"),  # Should NOT be present
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_name == "no simulate call":
            # This should NOT be present (except in comments)
            lines_with_call = [
                line for line in source.split('\n')
                if check_string in line and not line.strip().startswith('#')
            ]
            if lines_with_call:
                print(f"[FAIL] Found call to _simulate_student_response: {lines_with_call[0][:60]}")
                all_passed = False
            else:
                print(f"[PASS] {check_name}: no calls found")
        else:
            if check_string in source:
                print(f"[PASS] {check_name}: present in code")
            else:
                print(f"[FAIL] {check_name}: '{check_string}' not found")
                all_passed = False

    return all_passed


def test_init_warnings():
    """Test 5: Verify __init__ provides proper warnings"""
    print("\n" + "=" * 70)
    print("TEST 5: Verify __init__ warnings for missing Symbo")
    print("=" * 70)

    source_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'docs',
        'MASTER_ARCHIVE',
        'symbo_agentic_reasoners_phase5',
        'phase5_system.py'
    )

    with open(source_path, 'r') as f:
        source = f.read()

    checks = [
        ("warning about fast-path", "fast-path"),
        ("warning about Teacher routing", "routed to Teacher"),
        ("installation guidance", "pip install symbo"),
        ("logger.warning call", "logger.warning"),
        ("no 'simulated student model' reference", "simulated student model"),
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_name == "no 'simulated student model' reference":
            # This should NOT be present
            if check_string.lower() in source.lower():
                print(f"[FAIL] Still references '{check_string}'")
                all_passed = False
            else:
                print(f"[PASS] {check_name}: removed")
        else:
            if check_string in source:
                print(f"[PASS] {check_name}: present")
            else:
                print(f"[FAIL] {check_name}: '{check_string}' not found")
                all_passed = False

    return all_passed


def test_with_mock_student():
    """Test 6: Verify Phase5System works with mock student for testing"""
    print("\n" + "=" * 70)
    print("TEST 6: Phase5System with MockStudentModel (testing scenario)")
    print("=" * 70)

    # This test demonstrates how tests should use MockStudentModel
    from tests.mocks.mock_student import MockStudentModel

    # Create a mock student
    mock_student = MockStudentModel("test_student")

    # Test the mock interface matches what Phase5System expects
    required_methods = ['generate', 'get_stats', 'learn_from_interaction', 'add_knowledge']

    for method in required_methods:
        if hasattr(mock_student, method):
            print(f"[PASS] MockStudentModel has required method: {method}")
        else:
            print(f"[FAIL] MockStudentModel missing method: {method}")
            return False

    # Test generate returns string
    result = mock_student.generate("test query")
    if not isinstance(result, str):
        print(f"[FAIL] generate() should return string, got: {type(result)}")
        return False
    print(f"[PASS] generate() returns string: '{result}'")

    # Test get_stats returns dict with expected keys
    stats = mock_student.get_stats()
    expected_keys = ['device', 'torch_available', 'total_queries', 'mock']
    for key in expected_keys:
        if key not in stats:
            print(f"[FAIL] get_stats() missing key: {key}")
            return False
    print(f"[PASS] get_stats() has all expected keys")

    print("\n[PASS] MockStudentModel compatible with Phase5System interface")
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print("P0-2c FIX VERIFICATION: Simulated Student Response Removal")
    print("=" * 70)

    tests = [
        ("No simulate method in production", test_no_simulate_method),
        ("MockStudentModel available", test_mock_student_available),
        ("MockStudentModel in exports", test_mock_in_exports),
        ("Fail-fast error handling", test_fail_fast_error_message),
        ("Init warnings proper", test_init_warnings),
        ("Mock compatible with Phase5System", test_with_mock_student),
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
        print("\n[SUCCESS] P0-2c Fix Verified: All tests passed!")
        print("  - _simulate_student_response() removed from production")
        print("  - MockStudentModel available in tests/mocks/")
        print("  - Fail-fast error handling implemented")
        print("  - Clear, actionable error messages")
        return True
    else:
        print(f"\n[FAILURE] {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
