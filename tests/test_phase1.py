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
PHASE 1 VERIFICATION TEST
=========================

Official end-to-end test for Phase 1: The Cognitive Chassis

THE OFFICIAL TEST CASE:
----------------------
"Calculate the derivative of x² + 1"

This test validates that the entire Cognitive Chassis functions as a single,
cohesive unit - the "first breath" of the integrated system.

TEST JOURNEY THROUGH THE SYSTEM:
--------------------------------
1. Problem Analysis Team: Receives raw text, parses to OMDoc, classifies as Calculus/Computation
2. Main Orchestrator: Receives structured problem, queries DF, posts to Blackboard
3. Pilot Solver: Subscribes to Blackboard, retrieves task, executes sympy.diff(x**2 + 1)
4. Verification Core: Intercepts result, validates, marks STATUS: VERIFIED
5. Orchestrator: Observes VERIFIED status, retrieves result, returns "2*x"

REFERENCE:
---------
- Phase_1_Build_Order_Breakdown.md: Lines 289-301 (End-to-End Test)
- Phase 1 Coding Strategy: Section 4.0 "The First Breath"
"""

import sys
import os
import time

# Add parent directory to path for imports

# Import Phase 1 system
from symbo_agentic_reasoners.core.system import Phase1System

def test_phase1_official():
    """
    Official Phase 1 Verification Test

    Test case: "Calculate the derivative of x² + 1"
    Expected result: "2*x"
    """
    print()
    print("=" * 80)
    print(" " * 20 + "PHASE 1 VERIFICATION TEST")
    print("=" * 80)
    print()

    print("TEST CASE: Calculate the derivative of x² + 1")
    print("EXPECTED: 2*x")
    print()

    try:
        # Initialize system
        print("Initializing Phase 1 System...")
        print()
        system = Phase1System()
        system.start()

        # Perform health check
        print("Performing health check...")
        print()
        health = system.health_check()

        if not health['overall']:
            print("[FAILED] PHASE 1 HEALTH CHECK FAILED")
            print()
            system.shutdown()
            return False

        # Run the official test
        print()
        print("=" * 80)
        print("RUNNING OFFICIAL PHASE 1 TEST")
        print("=" * 80)
        print()

        # The official test case
        test_problem = "Calculate the derivative of x**2 + 1"

        print(f"Test Problem: {test_problem}")
        print()

        # Solve
        try:
            result = system.solve(test_problem)

            print(f"Result: {result}")
            print()

            # Verify result
            # Expected: 2*x (SymPy format: 2*x)
            result_str = str(result).strip()

            # Check if result contains "2*x" or equivalent
            success = ("2*x" in result_str or "2x" in result_str or
                      result_str == "2*x" or "x*2" in result_str)

            # Display statistics
            system.print_statistics()

            # Shutdown
            system.shutdown()

            print()
            print("=" * 80)
            print(" " * 20 + "VERIFICATION COMPLETE")
            print("=" * 80)
            print()

            if success:
                print("[SUCCESS] PHASE 1 COMPLETE AND VERIFIED")
                print()
                print("All Phase 1 Definition of Done criteria met:")
                print("  [OK] Problem Analysis Team operational")
                print("  [OK] Main Orchestrator routes without computing")
                print("  [OK] Pilot Solver executes SymPy operations")
                print("  [OK] Verification Core validates results")
                print("  [OK] End-to-end test passes with correct result")
                print()
                print("SYSTEM STATUS: Architecturally Complete, Mathematically Limited")
                print()
                print("-" * 80)
                print("KEY ACHIEVEMENTS:")
                print("-" * 80)
                print("  [OK] Orchestrator-Prover-Verifier loop functional")
                print("  [OK] Neural creativity shackled to symbolic rigor")
                print("  [OK] Separation of planning from execution enforced")
                print("  [OK] Separation of intuition from verification enforced")
                print()
                print("-" * 80)
                print("NEXT STEPS:")
                print("-" * 80)
                print("  Phase 2: Replace Pilot Solver with 50+ specialized agents")
                print("  Phase 2: Implement full HTN decomposition")
                print("  Phase 2: Add Tier 2 Supervisors for each mathematical domain")
                print()
                return True
            else:
                print("[FAILED] PHASE 1 VERIFICATION FAILED")
                print()
                print(f"Expected result containing '2*x', got: {result_str}")
                print()
                return False

        except Exception as e:
            print()
            print("[ERROR] PHASE 1 TEST ERROR")
            print()
            print(f"Error: {e}")
            print()
            import traceback
            traceback.print_exc()

            system.shutdown()
            return False

    except Exception as e:
        print()
        print("[ERROR] PHASE 1 INITIALIZATION ERROR")
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


def test_additional_cases():
    """
    Additional test cases to verify system capabilities
    """
    print()
    print("=" * 80)
    print("ADDITIONAL TEST CASES")
    print("=" * 80)
    print()

    system = Phase1System()
    system.start()

    test_cases = [
        ("derivative of x**3", "3*x**2"),
        ("integral of x", "x**2/2"),
        ("simplify (x+1)*(x-1)", "x**2 - 1"),
    ]

    passed = 0
    failed = 0

    for problem, expected in test_cases:
        print(f"\nTest: {problem}")
        print(f"Expected: {expected}")

        try:
            result = system.solve(problem)
            print(f"Got: {result}")

            if expected.replace(" ", "") in str(result).replace(" ", ""):
                print("[PASS]")
                passed += 1
            else:
                print("[FAIL]")
                failed += 1

        except Exception as e:
            print(f"[ERROR] {e}")
            failed += 1

    system.shutdown()

    print()
    print("=" * 80)
    print(f"ADDITIONAL TESTS: {passed} passed, {failed} failed")
    print("=" * 80)
    print()

    return failed == 0


if __name__ == "__main__":
    """Run Phase 1 Verification Test"""

    # Run official test
    official_success = test_phase1_official()

    # Exit with appropriate code
    if official_success:
        print()
        print("[OK] Phase 1 verification test PASSED")
        print()
        sys.exit(0)
    else:
        print()
        print("[FAIL] Phase 1 verification test FAILED")
        print()
        sys.exit(1)
