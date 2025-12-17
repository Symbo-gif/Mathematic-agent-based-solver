#!/usr/bin/env python
"""
Verification script for solver_engine.py decomposition.

Verifies:
1. All modules created
2. Imports work (no circular dependencies)
3. Backward compatibility maintained
4. Basic functionality works
"""

import sys
import os

def test_module_structure():
    """Test that all modules exist."""
    print("=" * 60)
    print("TEST 1: Module Structure")
    print("=" * 60)

    solver_dir = "src/symbo_agentic_reasoners/core/solver"
    expected_files = [
        "__init__.py",
        "result.py",
        "safety_checker.py",
        "router.py",
        "cache_manager.py",
        "solver_core.py",
        "specialized_solvers.py",
        "api.py"
    ]

    for filename in expected_files:
        path = os.path.join(solver_dir, filename)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  OK  {filename:30} ({size:,} bytes)")
        else:
            print(f"  FAIL  {filename:30} (NOT FOUND)")
            return False

    print("\nModule structure: PASS")
    return True


def test_imports():
    """Test that imports work without circular dependencies."""
    print("\n" + "=" * 60)
    print("TEST 2: Import Tests")
    print("=" * 60)

    try:
        # Test 1: Import solver package
        print("  Testing: from symbo_agentic_reasoners.core import solver")
        from symbo_agentic_reasoners.core import solver
        print("    OK")

        # Test 2: Import all components
        print("  Testing: Import all public APIs")
        from symbo_agentic_reasoners.core.solver import (
            SolverEngine, SolveStatus, SolveResult,
            get_solver_engine, solve, solve_expression,
            check_expression_safety, SpecialistRouter,
            ResultCache, solve_diophantine
        )
        print("    OK")

        # Test 3: Legacy import
        print("  Testing: Legacy import from solver_engine")
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine
        print("    OK")

        print("\nImport tests: PASS")
        return True

    except ImportError as e:
        print(f"    FAIL: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility with old imports."""
    print("\n" + "=" * 60)
    print("TEST 3: Backward Compatibility")
    print("=" * 60)

    try:
        # Old import style
        from symbo_agentic_reasoners.core.solver_engine import (
            SolverEngine,
            SolveStatus,
            SolveResult,
            get_solver_engine,
            solve
        )

        # Verify classes are correct
        assert SolveStatus.SUCCESS.value == "success"
        assert hasattr(SolverEngine, 'solve')
        assert hasattr(SolverEngine, 'solve_expression')
        assert callable(get_solver_engine)
        assert callable(solve)

        print("  Legacy imports work correctly")
        print("  All expected classes and functions present")
        print("\nBackward compatibility: PASS")
        return True

    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def test_functionality():
    """Test basic solver functionality."""
    print("\n" + "=" * 60)
    print("TEST 4: Functional Tests")
    print("=" * 60)

    try:
        from symbo_agentic_reasoners.core.solver import get_solver_engine, SolveStatus

        engine = get_solver_engine()
        print("  Created solver engine")

        # Test 1: Simple differentiation
        result = engine.solve_expression('x**2', operation='derivative', variable='x')
        assert result.status == SolveStatus.SUCCESS, f"Expected SUCCESS, got {result.status}"
        print(f"  Differentiation test: {result.result}")

        # Test 2: Safety check
        from symbo_agentic_reasoners.core.solver import check_expression_safety
        is_safe, error = check_expression_safety("x" * 20000)
        assert not is_safe, "Should reject long expressions"
        print(f"  Safety check test: Correctly rejected long expression")

        # Test 3: Statistics
        stats = engine.get_statistics()
        assert 'problems_solved' in stats
        assert 'success_rate' in stats
        print(f"  Statistics test: {stats['problems_solved']} problems solved")

        # Test 4: Health check
        health = engine.health_check()
        assert health['analysis_team'] == True
        assert health['native_symbolic'] == True
        print(f"  Health check test: All systems operational")

        print("\nFunctional tests: PASS")
        return True

    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specialized_solvers():
    """Test specialized solver functions."""
    print("\n" + "=" * 60)
    print("TEST 5: Specialized Solvers")
    print("=" * 60)

    try:
        from symbo_agentic_reasoners.core.solver import (
            solve_sum_of_cubes,
            compute_determinant_native,
            bounded_diophantine_search_native
        )

        # Test 1: Sum of cubes
        solutions = solve_sum_of_cubes(8)
        assert len(solutions) > 0, "Should find solutions for 8"
        print(f"  Sum of cubes (8): Found {len(solutions)} solutions")

        # Test 2: Determinant
        det = compute_determinant_native("[[1, 0], [0, 1]]")
        assert det is not None, "Should compute 2x2 determinant"
        print(f"  Determinant test: det(I_2) = {det}")

        print("\nSpecialized solvers: PASS")
        return True

    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("\nSOLVER DECOMPOSITION VERIFICATION")
    print("=" * 60)
    print("Verifying solver_engine.py -> solver/ package decomposition")
    print("=" * 60)

    tests = [
        ("Module Structure", test_module_structure),
        ("Imports", test_imports),
        ("Backward Compatibility", test_backward_compatibility),
        ("Basic Functionality", test_functionality),
        ("Specialized Solvers", test_specialized_solvers),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nUNEXPECTED ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {name:30} {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("OVERALL: ALL TESTS PASSED")
        print("Decomposition verified successfully!")
    else:
        print("OVERALL: SOME TESTS FAILED")
        print("Please review the failures above.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
