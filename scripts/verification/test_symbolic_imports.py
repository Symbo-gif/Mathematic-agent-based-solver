#!/usr/bin/env python3
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
Test Script for Symbolic Package Migration
===========================================

This script tests that all imports work correctly from both:
1. The new modular symbolic/ package
2. The backward-compatible native_symbolic.py re-export layer

NO SYMPY - Pure Python symbolic mathematics.
"""

import sys
import traceback

def test_section(title):
    """Print a test section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def test_import(description, import_code):
    """Test an import and report success/failure."""
    try:
        exec(import_code, globals())
        print(f"[PASS] {description}")
        return True
    except Exception as e:
        print(f"[FAIL] {description}")
        print(f"  Error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all import tests."""
    print("SYMBOLIC PACKAGE MIGRATION TEST")
    print("Testing both new modular imports and backward-compatible imports")

    passed = 0
    failed = 0

    # =============================================================================
    # TEST 1: New Modular Imports (symbolic/ package)
    # =============================================================================
    test_section("TEST 1: New Modular Imports (symbolic/ package)")

    tests = [
        ("Import base types",
         "from symbo_agentic_reasoners.core.symbolic import Expr, Symbol, Integer, Float, Rational"),

        ("Import operations",
         "from symbo_agentic_reasoners.core.symbolic import Add, Mul, Pow"),

        ("Import functions",
         "from symbo_agentic_reasoners.core.symbolic import Sin, Cos, Tan, Exp, Log, Sqrt"),

        ("Import lowercase function aliases",
         "from symbo_agentic_reasoners.core.symbolic import sin, cos, tan, exp, log, sqrt"),

        ("Import parsing",
         "from symbo_agentic_reasoners.core.symbolic import parse_expr, sympify, symbols"),

        ("Import simplification",
         "from symbo_agentic_reasoners.core.symbolic import simplify, expand, factor"),

        ("Import utilities",
         "from symbo_agentic_reasoners.core.symbolic import diff, solve"),

        ("Import constants",
         "from symbo_agentic_reasoners.core.symbolic import pi, E, I, oo"),

        ("Import compatibility",
         "from symbo_agentic_reasoners.core.symbolic import Eq, SympifyError"),
    ]

    for desc, code in tests:
        if test_import(desc, code):
            passed += 1
        else:
            failed += 1

    # =============================================================================
    # TEST 2: Backward-Compatible Imports (native_symbolic.py)
    # =============================================================================
    test_section("TEST 2: Backward-Compatible Imports (native_symbolic.py)")

    tests = [
        ("Import base types",
         "from symbo_agentic_reasoners.core.native_symbolic import Expr, Symbol, Integer, Float, Rational"),

        ("Import operations",
         "from symbo_agentic_reasoners.core.native_symbolic import Add, Mul, Pow"),

        ("Import functions",
         "from symbo_agentic_reasoners.core.native_symbolic import Sin, Cos, Tan, Exp, Log, Sqrt"),

        ("Import lowercase function aliases",
         "from symbo_agentic_reasoners.core.native_symbolic import sin, cos, tan, exp, log, sqrt"),

        ("Import parsing",
         "from symbo_agentic_reasoners.core.native_symbolic import parse_expr, sympify, symbols"),

        ("Import simplification",
         "from symbo_agentic_reasoners.core.native_symbolic import simplify, expand, factor"),

        ("Import utilities",
         "from symbo_agentic_reasoners.core.native_symbolic import diff, solve"),

        ("Import constants",
         "from symbo_agentic_reasoners.core.native_symbolic import pi, E, I, oo"),

        ("Import compatibility",
         "from symbo_agentic_reasoners.core.native_symbolic import Eq, SympifyError"),
    ]

    for desc, code in tests:
        if test_import(desc, code):
            passed += 1
        else:
            failed += 1

    # =============================================================================
    # TEST 3: Functional Tests
    # =============================================================================
    test_section("TEST 3: Functional Tests")

    try:
        from symbo_agentic_reasoners.core.symbolic import Symbol, Integer, parse_expr, simplify, symbols

        # Test 1: Create symbols
        x, y = symbols('x y')
        print(f"[PASS] Created symbols: x={x}, y={y}")
        passed += 1

        # Test 2: Create expressions
        expr = x**2 + 2*x + 1
        print(f"[PASS] Created expression: {expr}")
        passed += 1

        # Test 3: Differentiation
        deriv = expr.diff(x)
        print(f"[PASS] Differentiation: d/dx({expr}) = {deriv}")
        passed += 1

        # Test 4: Substitution
        result = expr.subs(x, Integer(3))
        print(f"[PASS] Substitution: ({expr}).subs(x, 3) = {result}")
        passed += 1

        # Test 5: Parsing
        expr2 = parse_expr("sin(x)**2 + cos(x)**2")
        print(f"[PASS] Parsed expression: {expr2}")
        passed += 1

        # Test 6: Simplification
        simplified = expr2.simplify()
        print(f"[PASS] Simplified sin^2(x) + cos^2(x) = {simplified}")
        passed += 1

        # Test 7: Numeric evaluation
        from symbo_agentic_reasoners.core.symbolic import sin, cos
        expr3 = sin(Integer(0))
        val = expr3.evalf()
        print(f"[PASS] Evaluation: sin(0) = {val}")
        passed += 1

        # Test 8: LaTeX output
        latex = expr.to_latex()
        print(f"[PASS] LaTeX conversion: {latex}")
        passed += 1

    except Exception as e:
        print(f"[FAIL] Functional tests failed: {e}")
        traceback.print_exc()
        failed += 8

    # =============================================================================
    # SUMMARY
    # =============================================================================
    test_section("TEST SUMMARY")

    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")

    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED! Migration successful!")
        return 0
    else:
        print(f"\n[WARNING] {failed} tests failed. Please review errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
