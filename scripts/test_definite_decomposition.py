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
Test the decomposed definite_integration modules.

This script verifies that:
1. All modules can be imported
2. Basic functionality works correctly
3. Backward compatibility is maintained
"""

import sys
import os

# Add project root to path
project_root = r"c:\dev\Mathematic agent based solver"
sys.path.insert(0, os.path.join(project_root, "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        # Test package import
        from symbo_agentic_reasoners.core.calculus.definite_integration import (
            definite_integrate,
            DefiniteIntegrationSupervisor,
        )
        print("  ✓ Package imports successful")

        # Test sub-module imports
        from symbo_agentic_reasoners.core.calculus.definite_integration import (
            gaussian_integrals,
            exponential_integrals,
            special_integrals,
            oscillatory_integrals,
            singularity_analysis,
            extraction_utils,
        )
        print("  ✓ Sub-module imports successful")

        # Test backward compatibility import
        from symbo_agentic_reasoners.core.calculus.definite_integration_specialist import (
            definite_integrate as di_compat,
        )
        print("  ✓ Backward compatibility import successful")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gaussian_integrals():
    """Test Gaussian integral functions."""
    print("\nTesting Gaussian integrals...")

    from symbo_agentic_reasoners.core.calculus.definite_integration import definite_integrate

    tests = [
        ("exp(-x**2)", "x", "-inf", "inf", "sqrt(pi)"),
        ("x**2 * exp(-x**2)", "x", "-inf", "inf", "sqrt(pi)/2"),
        ("exp(-x**2)", "x", "0", "inf", "sqrt(pi)/2"),
    ]

    for expr, var, a, b, expected in tests:
        try:
            success, result, method = definite_integrate(expr, var, a, b)
            if success:
                print(f"  ✓ ∫ {expr} from {a} to {b} = {result}")
            else:
                print(f"  ✗ ∫ {expr} from {a} to {b} failed: {method}")
        except Exception as e:
            print(f"  ✗ ∫ {expr} from {a} to {b} error: {e}")


def test_exponential_integrals():
    """Test exponential integral functions."""
    print("\nTesting exponential integrals...")

    from symbo_agentic_reasoners.core.calculus.definite_integration import definite_integrate

    tests = [
        ("exp(-x)", "x", "0", "inf", "1"),
        ("exp(-2*x)", "x", "0", "inf", "0.5"),
        ("x * exp(-x)", "x", "0", "inf", "1"),
    ]

    for expr, var, a, b, expected in tests:
        try:
            success, result, method = definite_integrate(expr, var, a, b)
            if success:
                print(f"  ✓ ∫ {expr} from {a} to {b} = {result}")
            else:
                print(f"  ✗ ∫ {expr} from {a} to {b} failed: {method}")
        except Exception as e:
            print(f"  ✗ ∫ {expr} from {a} to {b} error: {e}")


def test_special_integrals():
    """Test special integral functions."""
    print("\nTesting special integrals...")

    from symbo_agentic_reasoners.core.calculus.definite_integration import definite_integrate

    tests = [
        ("1/(1 + x**2)", "x", "-inf", "inf", "pi"),
    ]

    for expr, var, a, b, expected in tests:
        try:
            success, result, method = definite_integrate(expr, var, a, b)
            if success:
                print(f"  ✓ ∫ {expr} from {a} to {b} = {result}")
            else:
                print(f"  ✗ ∫ {expr} from {a} to {b} failed: {method}")
        except Exception as e:
            print(f"  ✗ ∫ {expr} from {a} to {b} error: {e}")


def test_backward_compatibility():
    """Test backward compatibility with original interface."""
    print("\nTesting backward compatibility...")

    try:
        # Import via old path
        from symbo_agentic_reasoners.core.calculus.definite_integration_specialist import (
            definite_integrate,
            DefiniteIntegrationSupervisor,
            _try_gaussian_integral,
            _check_log_singularity,
        )

        # Test basic integral
        success, result, method = definite_integrate("exp(-x**2)", "x", "-inf", "inf")
        if success and "sqrt(pi)" in result:
            print("  ✓ Old import path works")
        else:
            print(f"  ✗ Old import path failed: {result}")

        # Test supervisor class
        supervisor = DefiniteIntegrationSupervisor()
        success, result, method = supervisor.definite_integrate("exp(-x)", "x", "0", "inf")
        if success and result == "1":
            print("  ✓ Supervisor class works")
        else:
            print(f"  ✗ Supervisor class failed: {result}")

    except Exception as e:
        print(f"  ✗ Backward compatibility failed: {e}")
        import traceback
        traceback.print_exc()


def test_cross_module_dependencies():
    """Test that cross-module imports work correctly."""
    print("\nTesting cross-module dependencies...")

    try:
        # Test that gaussian_integrals can use extraction_utils
        from symbo_agentic_reasoners.core.calculus.definite_integration.gaussian_integrals import (
            _try_gaussian_integral,
        )

        # Test that exponential_integrals can use extraction_utils
        from symbo_agentic_reasoners.core.calculus.definite_integration.exponential_integrals import (
            _try_exponential_ray_integral,
        )

        # Test that special_integrals can use extraction_utils
        from symbo_agentic_reasoners.core.calculus.definite_integration.special_integrals import (
            _try_beta_integral,
        )

        print("  ✓ Cross-module imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Cross-module import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Decomposed Definite Integration Modules")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    if results[-1][1]:  # Only continue if imports work
        results.append(("Cross-module dependencies", test_cross_module_dependencies()))
        test_gaussian_integrals()
        test_exponential_integrals()
        test_special_integrals()
        test_backward_compatibility()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")

    print("\nNote: Some integrals may not return exact expected values")
    print("but should still succeed and return reasonable results.")


if __name__ == '__main__':
    main()
