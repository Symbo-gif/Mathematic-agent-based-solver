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
Test Script for P0-2e: Mock Embeddings Fix
==========================================

This script verifies:
1. VectorDatabaseUpdater requires embedding model or explicit allow_mock=True
2. _generate_embedding() fails fast without embedding model
3. _generate_query_embedding() fails fast without embedding model
4. Mock mode works when explicitly allowed
5. Error messages are clear and actionable

Usage:
    python test_mock_embeddings_fix.py
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


def test_fail_fast_without_model():
    """Test 1: Verify VectorDatabaseUpdater fails fast without embedding model"""
    print("\n" + "=" * 70)
    print("TEST 1: Verify fail-fast without embedding model")
    print("=" * 70)

    from symbo_agentic_reasoners.discovery.formal.vector_database_updater import (
        VectorDatabaseUpdater
    )
    from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
        FormalizedDiscovery, DiscoveryType
    )

    # Create updater without embedding model and without allow_mock
    updater = VectorDatabaseUpdater(
        embedding_model=None,
        allow_mock=False  # This is the default
    )

    # Create a test discovery
    discovery = FormalizedDiscovery(
        discovery_id="test_001",
        discovery_type=DiscoveryType.THEOREM,
        natural_language_statement="Test theorem statement",
        omdoc_representation="<theorem>Test</theorem>",
        lean4_code="theorem test : True := trivial",
        sympy_implementation="True",
        applicable_domains=["algebra"],
        verified=True
    )

    # Try to generate embedding - should raise RuntimeError
    try:
        updater._generate_embedding(discovery)
        print("[FAIL] Should have raised RuntimeError")
        return False
    except RuntimeError as e:
        error_str = str(e)
        if "sentence-transformers" in error_str and "allow_mock=True" in error_str:
            print("[PASS] _generate_embedding() raises RuntimeError with clear message")
            print(f"       Error includes: 'sentence-transformers', 'allow_mock=True'")
        else:
            print(f"[FAIL] Error message incomplete: {error_str}")
            return False

    # Try to generate query embedding - should also raise
    try:
        updater._generate_query_embedding("test query")
        print("[FAIL] Should have raised RuntimeError for query embedding")
        return False
    except RuntimeError as e:
        print("[PASS] _generate_query_embedding() raises RuntimeError")

    return True


def test_mock_mode_with_explicit_flag():
    """Test 2: Verify mock mode works when allow_mock=True"""
    print("\n" + "=" * 70)
    print("TEST 2: Verify mock mode with explicit allow_mock=True")
    print("=" * 70)

    from symbo_agentic_reasoners.discovery.formal.vector_database_updater import (
        VectorDatabaseUpdater
    )
    from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
        FormalizedDiscovery, DiscoveryType
    )

    # Create updater with allow_mock=True
    updater = VectorDatabaseUpdater(
        embedding_model=None,
        allow_mock=True  # Explicitly allow mock
    )

    # Create a test discovery
    discovery = FormalizedDiscovery(
        discovery_id="test_002",
        discovery_type=DiscoveryType.THEOREM,
        natural_language_statement="Test theorem statement",
        omdoc_representation="<theorem>Test</theorem>",
        lean4_code="theorem test : True := trivial",
        sympy_implementation="True",
        applicable_domains=["algebra"],
        verified=True
    )

    # Generate embedding - should work with warning
    try:
        embedding = updater._generate_embedding(discovery)
        if len(embedding) == updater.embedding_dim:
            print(f"[PASS] Mock embedding generated: {len(embedding)} dimensions")
        else:
            print(f"[FAIL] Wrong embedding dimension: {len(embedding)}")
            return False
    except RuntimeError as e:
        print(f"[FAIL] Should not raise in mock mode: {e}")
        return False

    # Generate query embedding - should also work
    try:
        query_embedding = updater._generate_query_embedding("test query")
        if len(query_embedding) == updater.embedding_dim:
            print(f"[PASS] Mock query embedding generated: {len(query_embedding)} dimensions")
        else:
            print(f"[FAIL] Wrong query embedding dimension")
            return False
    except RuntimeError as e:
        print(f"[FAIL] Should not raise for query in mock mode: {e}")
        return False

    return True


def test_allow_mock_attribute():
    """Test 3: Verify allow_mock attribute is properly set"""
    print("\n" + "=" * 70)
    print("TEST 3: Verify allow_mock attribute handling")
    print("=" * 70)

    from symbo_agentic_reasoners.discovery.formal.vector_database_updater import (
        VectorDatabaseUpdater
    )

    # Test default value
    updater_default = VectorDatabaseUpdater()
    if hasattr(updater_default, '_allow_mock') and updater_default._allow_mock == False:
        print("[PASS] Default allow_mock is False")
    else:
        print(f"[FAIL] Default allow_mock should be False, got: {getattr(updater_default, '_allow_mock', 'MISSING')}")
        return False

    # Test explicit True
    updater_mock = VectorDatabaseUpdater(allow_mock=True)
    if updater_mock._allow_mock == True:
        print("[PASS] allow_mock=True is correctly set")
    else:
        print("[FAIL] allow_mock=True not correctly set")
        return False

    # Test explicit False
    updater_no_mock = VectorDatabaseUpdater(allow_mock=False)
    if updater_no_mock._allow_mock == False:
        print("[PASS] allow_mock=False is correctly set")
    else:
        print("[FAIL] allow_mock=False not correctly set")
        return False

    return True


def test_code_structure():
    """Test 4: Verify code has proper fail-fast structure"""
    print("\n" + "=" * 70)
    print("TEST 4: Verify fail-fast code structure")
    print("=" * 70)

    source_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'src',
        'symbo_agentic_reasoners',
        'discovery',
        'formal',
        'vector_database_updater.py'
    )

    with open(source_path, 'r') as f:
        source = f.read()

    checks = [
        ("allow_mock parameter", "allow_mock: bool = False"),
        ("_allow_mock attribute", "self._allow_mock = allow_mock"),
        ("fail-fast comment", "# FAIL-FAST"),
        ("RuntimeError raise", "raise RuntimeError"),
        ("sentence-transformers message", "sentence-transformers"),
        ("logger.error call", "logger.error"),
        ("console print", 'print(f"\\n[ERROR]'),
        ("mock warning docstring", "TESTING ONLY"),
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in source:
            print(f"[PASS] {check_name}: present")
        else:
            print(f"[FAIL] {check_name}: '{check_string}' not found")
            all_passed = False

    return all_passed


def test_phase0_vector_db_already_fixed():
    """Test 5: Verify Phase 0 VectorDatabase already has fail-fast"""
    print("\n" + "=" * 70)
    print("TEST 5: Verify Phase 0 VectorDatabase fail-fast behavior")
    print("=" * 70)

    source_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'src',
        'symbo_agentic_reasoners',
        'core',
        'vector_database.py'
    )

    with open(source_path, 'r') as f:
        source = f.read()

    checks = [
        ("allow_mock parameter", "allow_mock: bool = False"),
        ("fail-fast in _generate_embedding", "sentence-transformers required for embeddings"),
        ("mock warning", "TESTING ONLY"),
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in source:
            print(f"[PASS] {check_name}: present")
        else:
            print(f"[FAIL] {check_name}: '{check_string}' not found")
            all_passed = False

    return all_passed


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print("P0-2e FIX VERIFICATION: Mock Embeddings Removal")
    print("=" * 70)

    tests = [
        ("Fail-fast without model", test_fail_fast_without_model),
        ("Mock mode with explicit flag", test_mock_mode_with_explicit_flag),
        ("allow_mock attribute handling", test_allow_mock_attribute),
        ("Fail-fast code structure", test_code_structure),
        ("Phase 0 VectorDatabase fixed", test_phase0_vector_db_already_fixed),
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
        print("\n[SUCCESS] P0-2e Fix Verified: All tests passed!")
        print("  - Mock embeddings require explicit allow_mock=True")
        print("  - Fail-fast behavior implemented")
        print("  - Clear, actionable error messages")
        print("  - Phase 0 and Phase 6 both fixed")
        return True
    else:
        print(f"\n[FAILURE] {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
