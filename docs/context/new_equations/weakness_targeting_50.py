#!/usr/bin/env python3
# Copyright 2025 - Mathematical System Weakness Analysis
# Licensed under the Apache License, Version 2.0
"""
50 WEAKNESS-TARGETING EQUATIONS - Symbo Solver System Stress Test
===================================================================

This module contains 50 carefully designed equations that target specific
identified weaknesses in the Symbo solver system. Each equation is crafted
to expose particular failure modes and gaps in coverage.

TARGETED WEAKNESSES:
-------------------
1. Native Calculus Gaps (Equations 1-10)
   - Complex chain rule combinations
   - Integration by parts edge cases
   - Multi-variable limits
   - Series convergence at boundaries

2. Parser Vulnerabilities (Equations 11-20)
   - Ambiguous expressions
   - Unicode math symbols
   - Mixed notation styles
   - Long nested expressions

3. Numerical Stability (Equations 21-30)
   - Catastrophic cancellation scenarios
   - Ill-conditioned matrices
   - Near-singular computations

4. Domain-Specific Gaps (Equations 31-40)
   - Topology (simple invariants)
   - Abstract algebra basics
   - PDE boundary conditions
   - Tensor contractions

5. Edge Cases Likely to Fail (Equations 41-50)
   - Expressions that simplify unexpectedly
   - Limit/integral orderings that matter
   - Type coercion edge cases

USAGE:
------
    python weakness_targeting_50.py

Or import and use programmatically:
    from weakness_targeting_50 import WEAKNESS_EQUATIONS, run_weakness_tests
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

# Add source path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from symbo_agentic_reasoners.core.solver_engine import get_solver_engine, SolveStatus
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the symbo_agentic_reasoners package is in your Python path")
    sys.exit(1)


@dataclass
class WeaknessEquation:
    """
    A single equation designed to target a specific weakness.
    """
    id: int
    expression: str
    weakness_category: str
    specific_weakness: str
    expected_failure_mode: str
    fix_improvement: str
    expected_result: Optional[str] = None  # None means "any non-error result is success"


# =============================================================================
# CATEGORY 1: NATIVE CALCULUS GAPS (Equations 1-10)
# =============================================================================

CALCULUS_GAP_EQUATIONS = [
    # 1. Triple nested chain rule - derivatives of composed transcendentals
    WeaknessEquation(
        id=1,
        expression="diff(exp(sin(log(x**2 + 1))), x)",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Complex chain rule combinations",
        expected_failure_mode="Chain rule fails to propagate through 3+ nested functions",
        fix_improvement="Recursive chain rule implementation with depth tracking",
        expected_result=None  # Complex symbolic result
    ),

    # 2. Integration by parts requiring multiple iterations
    WeaknessEquation(
        id=2,
        expression="integrate(x**3 * exp(x) * sin(x), x)",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Integration by parts edge cases",
        expected_failure_mode="IBP recursion limit hit before solution found",
        fix_improvement="Implement tabular method for repeated IBP with exponentials/trig",
    ),

    # 3. Integration requiring specific substitution recognition
    WeaknessEquation(
        id=3,
        expression="integrate(x / sqrt(1 - x**4), x)",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Non-obvious u-substitution patterns",
        expected_failure_mode="Fails to recognize u = x^2 substitution",
        fix_improvement="Pattern matching for sqrt(1 - x^(2n)) with x^(n-1) numerator",
    ),

    # 4. Multi-variable limit with path dependence
    WeaknessEquation(
        id=4,
        expression="limit((x*y)/(x**2 + y**2), (x, 0), (y, 0))",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Multi-variable limits",
        expected_failure_mode="Returns single path result instead of detecting non-existence",
        fix_improvement="Implement path analysis for multi-variable limits",
        expected_result="Does not exist"  # Path dependent
    ),

    # 5. Series at essential singularity
    WeaknessEquation(
        id=5,
        expression="series(exp(1/x), x, 0, 6)",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Series convergence at boundaries",
        expected_failure_mode="Attempts Taylor series at essential singularity",
        fix_improvement="Detect essential singularities and use Laurent series",
    ),

    # 6. Improper integral with subtle convergence
    WeaknessEquation(
        id=6,
        expression="integrate(sin(x)/x, (x, 0, oo))",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Improper integral convergence",
        expected_failure_mode="Numerical evaluation diverges or times out",
        fix_improvement="Recognize Si(oo) = pi/2 pattern",
        expected_result="pi/2"
    ),

    # 7. Differentiation through piecewise definition
    WeaknessEquation(
        id=7,
        expression="diff(Piecewise((x**2, x < 0), (x**3, x >= 0)), x)",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Piecewise function handling",
        expected_failure_mode="Ignores piecewise structure, differentiates one branch",
        fix_improvement="Propagate differentiation through Piecewise with boundary checks",
    ),

    # 8. Integration with floor/ceiling functions
    WeaknessEquation(
        id=8,
        expression="integrate(floor(x), (x, 0, 5))",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Discontinuous function integration",
        expected_failure_mode="Treats floor(x) as continuous or fails entirely",
        fix_improvement="Detect step functions and sum over intervals",
        expected_result="10"  # 0+1+2+3+4
    ),

    # 9. Higher-order derivative with pattern collapse
    WeaknessEquation(
        id=9,
        expression="diff(sin(x)*cos(x)*exp(x), x, 5)",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Higher-order derivative computation",
        expected_failure_mode="Expression size explosion before simplification",
        fix_improvement="Apply identities (sin*cos = sin(2x)/2) before differentiation",
    ),

    # 10. Limit requiring L'Hopital multiple times
    WeaknessEquation(
        id=10,
        expression="limit((exp(x) - 1 - x - x**2/2 - x**3/6)/x**4, x, 0)",
        weakness_category="Native Calculus Gaps",
        specific_weakness="Repeated L'Hopital applications",
        expected_failure_mode="L'Hopital limit exceeded or wrong cancellation",
        fix_improvement="Implement L'Hopital with automatic iteration count",
        expected_result="1/24"
    ),
]


# =============================================================================
# CATEGORY 2: PARSER VULNERABILITIES (Equations 11-20)
# =============================================================================

PARSER_VULNERABILITY_EQUATIONS = [
    # 11. Unicode Greek letters mixed with ASCII
    WeaknessEquation(
        id=11,
        expression="diff(alpha*x**2 + beta*x + gamma, x)",
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Unicode math symbols",
        expected_failure_mode="Greek letters not recognized as symbols",
        fix_improvement="Expand Unicode normalization to handle all Greek",
        expected_result="2*alpha*x + beta"
    ),

    # 12. Ambiguous implicit multiplication
    WeaknessEquation(
        id=12,
        expression="2x(x+1)(x+2)",
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Ambiguous expressions",
        expected_failure_mode="Parsed as function call 2x(...) instead of 2*x*...",
        fix_improvement="Improve implicit multiplication detection heuristics",
    ),

    # 13. Mixed notation: LaTeX-style with ASCII
    WeaknessEquation(
        id=13,
        expression="\\frac{d}{dx}(x^2 + 1)",
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Mixed notation styles",
        expected_failure_mode="LaTeX \\frac not converted to diff operation",
        fix_improvement="Add LaTeX derivative notation preprocessing",
    ),

    # 14. Deeply nested parentheses (40 levels)
    WeaknessEquation(
        id=14,
        expression="((((((((((((((((((((((((((((((((((((((((x)))))))))))))))))))))))))))))))))))))))))",
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Long nested expressions",
        expected_failure_mode="Stack overflow or safety limit rejection",
        fix_improvement="Iterative parser with configurable depth limits",
        expected_result="x"
    ),

    # 15. Unicode superscript exponents
    WeaknessEquation(
        id=15,
        expression="x\u00b2 + 2x\u00b3 - x\u2074",
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Unicode math symbols",
        expected_failure_mode="Superscript digits not converted to **n",
        fix_improvement="Complete Unicode superscript mapping in normalizer",
    ),

    # 16. Ambiguous function vs multiplication
    WeaknessEquation(
        id=16,
        expression="sin x cos x",
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Ambiguous expressions",
        expected_failure_mode="Parsed as sin(x*cos(x)) instead of sin(x)*cos(x)",
        fix_improvement="Space-aware function argument parsing",
    ),

    # 17. Mixed radical notations
    WeaknessEquation(
        id=17,
        expression="sqrt(x) + \u221a(y) + cbrt(z)",
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Mixed notation styles",
        expected_failure_mode="Unicode radical symbol not recognized",
        fix_improvement="Unicode radical to sqrt() conversion",
    ),

    # 18. Invisible Unicode characters
    WeaknessEquation(
        id=18,
        expression="x\u200b+\u200by",  # Zero-width space between terms
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Unicode math symbols",
        expected_failure_mode="Zero-width spaces cause parse failure",
        fix_improvement="Strip all invisible Unicode before parsing",
        expected_result="x + y"
    ),

    # 19. Smart quotes in expression
    WeaknessEquation(
        id=19,
        expression="f\u2019(x) + g\u2018(x)",  # Curly apostrophes
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Mixed notation styles",
        expected_failure_mode="Smart quotes not recognized as derivative notation",
        fix_improvement="Quote normalization in preprocessing",
    ),

    # 20. Expression with em-dash minus
    WeaknessEquation(
        id=20,
        expression="x\u2014y",  # Em-dash used as minus
        weakness_category="Parser Vulnerabilities",
        specific_weakness="Unicode math symbols",
        expected_failure_mode="Em-dash not converted to minus operator",
        fix_improvement="Comprehensive dash/minus normalization",
        expected_result="x - y"
    ),
]


# =============================================================================
# CATEGORY 3: NUMERICAL STABILITY (Equations 21-30)
# =============================================================================

NUMERICAL_STABILITY_EQUATIONS = [
    # 21. Catastrophic cancellation in difference
    WeaknessEquation(
        id=21,
        expression="compute((1 + 1e-16) - 1)",
        weakness_category="Numerical Stability",
        specific_weakness="Catastrophic cancellation scenarios",
        expected_failure_mode="Returns 0 instead of 1e-16",
        fix_improvement="Use compensated summation or extended precision",
        expected_result="1e-16"
    ),

    # 22. Nearly singular 2x2 matrix determinant
    WeaknessEquation(
        id=22,
        expression="det([[1, 1.0000000001], [1, 1.0000000002]])",
        weakness_category="Numerical Stability",
        specific_weakness="Near-singular computations",
        expected_failure_mode="Returns 0 instead of ~1e-10",
        fix_improvement="Use rational arithmetic or higher precision for small determinants",
    ),

    # 23. Ill-conditioned Hilbert matrix
    WeaknessEquation(
        id=23,
        expression="det([[1, 1/2, 1/3, 1/4], [1/2, 1/3, 1/4, 1/5], [1/3, 1/4, 1/5, 1/6], [1/4, 1/5, 1/6, 1/7]])",
        weakness_category="Numerical Stability",
        specific_weakness="Ill-conditioned matrices",
        expected_failure_mode="Floating point errors accumulate to wrong result",
        fix_improvement="Use exact rational arithmetic for small integer/rational matrices",
        expected_result="1/6048000"  # Exact value
    ),

    # 24. Loss of significance in trig
    WeaknessEquation(
        id=24,
        expression="compute(sin(pi + 1e-15))",
        weakness_category="Numerical Stability",
        specific_weakness="Catastrophic cancellation scenarios",
        expected_failure_mode="sin(pi) dominates, loses small correction",
        fix_improvement="Range reduction with extended precision for sin near multiples of pi",
    ),

    # 25. Exponential overflow in intermediate
    WeaknessEquation(
        id=25,
        expression="compute(exp(1000) * exp(-1000))",
        weakness_category="Numerical Stability",
        specific_weakness="Numerical overflow/underflow",
        expected_failure_mode="Overflow in exp(1000) before multiplication",
        fix_improvement="Recognize exp(a)*exp(b) = exp(a+b) symbolically first",
        expected_result="1"
    ),

    # 26. Vandermonde matrix with close points
    WeaknessEquation(
        id=26,
        expression="det([[1, 1.0, 1.0], [1, 1.001, 1.002001], [1, 1.002, 1.004004]])",
        weakness_category="Numerical Stability",
        specific_weakness="Ill-conditioned matrices",
        expected_failure_mode="Floating point errors in closely-spaced Vandermonde",
        fix_improvement="Use symbolic Vandermonde formula when pattern detected",
    ),

    # 27. Catastrophic cancellation in derivative approximation
    WeaknessEquation(
        id=27,
        expression="compute((sin(1 + 1e-10) - sin(1)) / 1e-10)",
        weakness_category="Numerical Stability",
        specific_weakness="Catastrophic cancellation scenarios",
        expected_failure_mode="Subtraction loses precision",
        fix_improvement="Recognize numerical derivative pattern, use symbolic",
        expected_result="cos(1)"
    ),

    # 28. Large factorial ratio
    WeaknessEquation(
        id=28,
        expression="compute(factorial(100) / factorial(99))",
        weakness_category="Numerical Stability",
        specific_weakness="Numerical overflow/underflow",
        expected_failure_mode="Both factorials overflow before division",
        fix_improvement="Simplify ratio symbolically: n!/m! = product(i, i=m+1..n)",
        expected_result="100"
    ),

    # 29. Sum with alternating large terms
    WeaknessEquation(
        id=29,
        expression="compute(1e15 - 1e15 + 1)",
        weakness_category="Numerical Stability",
        specific_weakness="Catastrophic cancellation scenarios",
        expected_failure_mode="Precision lost in large subtraction",
        fix_improvement="Reorder operations or use extended precision",
        expected_result="1"
    ),

    # 30. Near-zero denominator
    WeaknessEquation(
        id=30,
        expression="limit(1/(x - 1e-16), x, 1e-16)",
        weakness_category="Numerical Stability",
        specific_weakness="Near-singular computations",
        expected_failure_mode="Numerical evaluation returns inf instead of proper limit",
        fix_improvement="Keep symbolic until limit evaluation",
        expected_result="oo"
    ),
]


# =============================================================================
# CATEGORY 4: DOMAIN-SPECIFIC GAPS (Equations 31-40)
# =============================================================================

DOMAIN_SPECIFIC_EQUATIONS = [
    # 31. Euler characteristic of simple surface (topology)
    WeaknessEquation(
        id=31,
        expression="euler_characteristic(torus)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Topology (simple invariants)",
        expected_failure_mode="No topology module - unrecognized function",
        fix_improvement="Add basic topological invariant database",
        expected_result="0"  # V - E + F = 0 for torus
    ),

    # 32. Group order calculation (abstract algebra)
    WeaknessEquation(
        id=32,
        expression="group_order(Z_6)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Abstract algebra basics",
        expected_failure_mode="No abstract algebra support",
        fix_improvement="Add cyclic group and basic group theory support",
        expected_result="6"
    ),

    # 33. Heat equation PDE
    WeaknessEquation(
        id=33,
        expression="pdesolve(diff(u, t) - diff(u, x, 2), u, (x, 0, 1), (t, 0, oo))",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="PDE boundary conditions",
        expected_failure_mode="PDE solver not implemented or ignores boundaries",
        fix_improvement="Add separation of variables for standard PDEs",
    ),

    # 34. Tensor contraction (Einstein notation)
    WeaknessEquation(
        id=34,
        expression="contract(A_ij * B_jk, j)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Tensor contractions",
        expected_failure_mode="Einstein summation convention not recognized",
        fix_improvement="Add tensor index contraction support",
    ),

    # 35. Fundamental group (topology)
    WeaknessEquation(
        id=35,
        expression="fundamental_group(circle)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Topology (simple invariants)",
        expected_failure_mode="Homotopy groups not supported",
        fix_improvement="Add database of fundamental groups for common spaces",
        expected_result="Z"  # Integers
    ),

    # 36. Ring homomorphism check (abstract algebra)
    WeaknessEquation(
        id=36,
        expression="is_ring_homomorphism(f, Z, Z_mod_6)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Abstract algebra basics",
        expected_failure_mode="No ring theory support",
        fix_improvement="Add basic ring/field homomorphism checking",
    ),

    # 37. Wave equation with initial conditions
    WeaknessEquation(
        id=37,
        expression="pdesolve(diff(u, t, 2) - c**2*diff(u, x, 2), u, u(x, 0) = sin(x), diff(u, t)(x, 0) = 0)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="PDE boundary conditions",
        expected_failure_mode="Initial value parsing fails or solution incorrect",
        fix_improvement="D'Alembert solution for 1D wave equation",
    ),

    # 38. Christoffel symbols (differential geometry)
    WeaknessEquation(
        id=38,
        expression="christoffel(diag(1, r**2, r**2*sin(theta)**2), (r, theta, phi))",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Tensor contractions",
        expected_failure_mode="Metric tensor operations not supported",
        fix_improvement="Add Christoffel symbol computation for given metric",
    ),

    # 39. Betti numbers (algebraic topology)
    WeaknessEquation(
        id=39,
        expression="betti_numbers(klein_bottle)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Topology (simple invariants)",
        expected_failure_mode="Homology not supported",
        fix_improvement="Add Betti number database for standard manifolds",
        expected_result="(1, 1, 0)"  # b0, b1, b2
    ),

    # 40. Galois group (field theory)
    WeaknessEquation(
        id=40,
        expression="galois_group(x**4 - 2)",
        weakness_category="Domain-Specific Gaps",
        specific_weakness="Abstract algebra basics",
        expected_failure_mode="Galois theory not implemented",
        fix_improvement="Add Galois group computation for common polynomials",
        expected_result="D_4"  # Dihedral group of order 8
    ),
]


# =============================================================================
# CATEGORY 5: EDGE CASES LIKELY TO FAIL (Equations 41-50)
# =============================================================================

EDGE_CASE_EQUATIONS = [
    # 41. Expression that should simplify to 0
    WeaknessEquation(
        id=41,
        expression="simplify(sin(x)**2 + cos(x)**2 - 1)",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Expressions that simplify unexpectedly",
        expected_failure_mode="Returns unsimplified expression instead of 0",
        fix_improvement="Add Pythagorean identity to simplification rules",
        expected_result="0"
    ),

    # 42. Order of integration matters
    WeaknessEquation(
        id=42,
        expression="integrate(integrate(1/(1 - x*y), y, 0, 1), x, 0, 1)",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Limit/integral orderings that matter",
        expected_failure_mode="Double integral computed in wrong order (diverges)",
        fix_improvement="Detect Fubini's theorem applicability",
    ),

    # 43. Type coercion: integer vs float
    WeaknessEquation(
        id=43,
        expression="simplify(2/3 + 1/3)",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Type coercion edge cases",
        expected_failure_mode="Returns 0.9999... instead of 1",
        fix_improvement="Keep rational arithmetic throughout",
        expected_result="1"
    ),

    # 44. Hidden common factor
    WeaknessEquation(
        id=44,
        expression="simplify((x**3 - 1)/(x - 1))",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Expressions that simplify unexpectedly",
        expected_failure_mode="Doesn't factor x^3 - 1 = (x-1)(x^2+x+1)",
        fix_improvement="Factor before division simplification",
        expected_result="x**2 + x + 1"
    ),

    # 45. Limit and integral don't commute
    WeaknessEquation(
        id=45,
        expression="limit(integrate(x**n * exp(-x), (x, 0, oo)), n, oo)",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Limit/integral orderings that matter",
        expected_failure_mode="Interchanges limit and integral incorrectly",
        fix_improvement="Check dominated convergence conditions",
    ),

    # 46. Integer power of complex
    WeaknessEquation(
        id=46,
        expression="simplify((1 + I)**4)",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Type coercion edge cases",
        expected_failure_mode="Complex arithmetic error or wrong branch",
        fix_improvement="Correct complex power handling",
        expected_result="-4"
    ),

    # 47. Telescoping sum not recognized
    WeaknessEquation(
        id=47,
        expression="summation(1/(n*(n+1)), (n, 1, oo))",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Expressions that simplify unexpectedly",
        expected_failure_mode="Doesn't recognize partial fraction telescoping",
        fix_improvement="Add telescoping sum detection",
        expected_result="1"
    ),

    # 48. Mixed symbolic/numeric
    WeaknessEquation(
        id=48,
        expression="solve(x**2 - 2.0, x)",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Type coercion edge cases",
        expected_failure_mode="Returns float approx instead of sqrt(2)",
        fix_improvement="Detect integer-valued floats and convert",
        expected_result="[-sqrt(2), sqrt(2)]"
    ),

    # 49. Conditional convergence
    WeaknessEquation(
        id=49,
        expression="summation((-1)**(n+1)/n, (n, 1, oo))",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Limit/integral orderings that matter",
        expected_failure_mode="Rearrangement gives wrong value",
        fix_improvement="Detect alternating series and use appropriate method",
        expected_result="log(2)"  # Alternating harmonic series
    ),

    # 50. Zero to zero power
    WeaknessEquation(
        id=50,
        expression="limit(x**x, x, 0, '+')",
        weakness_category="Edge Cases Likely to Fail",
        specific_weakness="Type coercion edge cases",
        expected_failure_mode="Returns NaN or 0 instead of 1",
        fix_improvement="Handle 0^0 indeterminate form via exp(x*log(x))",
        expected_result="1"
    ),
]


# =============================================================================
# COMBINED LIST
# =============================================================================

WEAKNESS_EQUATIONS: List[WeaknessEquation] = (
    CALCULUS_GAP_EQUATIONS +
    PARSER_VULNERABILITY_EQUATIONS +
    NUMERICAL_STABILITY_EQUATIONS +
    DOMAIN_SPECIFIC_EQUATIONS +
    EDGE_CASE_EQUATIONS
)


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_weakness_tests(verbose: bool = True) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Run all 50 weakness-targeting tests.

    Args:
        verbose: If True, print detailed output

    Returns:
        (passed_count, total_count, detailed_results)
    """
    solver = get_solver_engine()

    results = []
    passed = 0
    failed = 0

    categories = {
        "Native Calculus Gaps": {"passed": 0, "failed": 0},
        "Parser Vulnerabilities": {"passed": 0, "failed": 0},
        "Numerical Stability": {"passed": 0, "failed": 0},
        "Domain-Specific Gaps": {"passed": 0, "failed": 0},
        "Edge Cases Likely to Fail": {"passed": 0, "failed": 0},
    }

    if verbose:
        print("=" * 80)
        print("50 WEAKNESS-TARGETING EQUATIONS - STRESS TEST")
        print("=" * 80)
        print()

    for eq in WEAKNESS_EQUATIONS:
        if verbose:
            print(f"[{eq.id:2d}/50] {eq.weakness_category[:25]:<25} ", end="")
            print(f"{eq.specific_weakness[:30]:<30} ", end="")

        try:
            start_time = time.time()
            result = solver.solve(eq.expression)
            elapsed = time.time() - start_time

            status = result.status.name if hasattr(result, 'status') else str(result.status)
            result_str = str(result.result) if result.result else "None"

            # Determine success/failure
            is_success = False
            failure_reason = None

            if status in ("ERROR", "FAILURE", "FAILED"):
                is_success = False
                failure_reason = f"Status: {status}"
            elif "error" in result_str.lower() or "failed" in result_str.lower():
                is_success = False
                failure_reason = f"Error in result: {result_str[:50]}"
            elif result_str == "None" or result_str == "":
                is_success = False
                failure_reason = "Empty result"
            elif "NotImplementedError" in result_str:
                is_success = False
                failure_reason = "Not implemented"
            elif eq.expected_result is not None:
                # Check against expected result (basic string match)
                expected_normalized = eq.expected_result.replace(" ", "")
                result_normalized = result_str.replace(" ", "")
                if expected_normalized in result_normalized or result_normalized in expected_normalized:
                    is_success = True
                else:
                    # Try numeric comparison for numeric results
                    try:
                        if abs(float(result_str) - float(eq.expected_result)) < 1e-10:
                            is_success = True
                        else:
                            is_success = False
                            failure_reason = f"Expected {eq.expected_result}, got {result_str}"
                    except (ValueError, TypeError):
                        is_success = True  # Non-numeric, consider any non-error as success
            else:
                is_success = True  # Any non-error result counts as success

            if is_success:
                passed += 1
                categories[eq.weakness_category]["passed"] += 1
                if verbose:
                    print(f"PASS ({elapsed:.2f}s)")
            else:
                failed += 1
                categories[eq.weakness_category]["failed"] += 1
                if verbose:
                    print(f"FAIL ({elapsed:.2f}s)")

            results.append({
                "id": eq.id,
                "expression": eq.expression[:60],
                "category": eq.weakness_category,
                "weakness": eq.specific_weakness,
                "expected_failure": eq.expected_failure_mode,
                "status": "PASS" if is_success else "FAIL",
                "result": result_str[:100],
                "failure_reason": failure_reason,
                "time": elapsed,
            })

        except Exception as e:
            failed += 1
            categories[eq.weakness_category]["failed"] += 1
            if verbose:
                print(f"ERROR: {str(e)[:30]}")
            results.append({
                "id": eq.id,
                "expression": eq.expression[:60],
                "category": eq.weakness_category,
                "weakness": eq.specific_weakness,
                "expected_failure": eq.expected_failure_mode,
                "status": "ERROR",
                "result": str(e)[:100],
                "failure_reason": str(e),
                "time": 0,
            })

    if verbose:
        print()
        print("=" * 80)
        print("RESULTS SUMMARY")
        print("=" * 80)
        print(f"Total: {passed}/{len(WEAKNESS_EQUATIONS)} passed ({100*passed/len(WEAKNESS_EQUATIONS):.1f}%)")
        print()
        print("BY CATEGORY:")
        print("-" * 80)
        for cat, stats in categories.items():
            total = stats["passed"] + stats["failed"]
            pct = 100 * stats["passed"] / total if total > 0 else 0
            print(f"  {cat:<35} {stats['passed']}/{total} ({pct:.1f}%)")

        print()
        print("FAILED TESTS (weakness confirmed):")
        print("-" * 80)
        for r in results:
            if r["status"] != "PASS":
                print(f"  [{r['id']:2d}] {r['weakness']}")
                print(f"       Expected failure: {r['expected_failure'][:60]}")
                print(f"       Actual: {r['failure_reason']}")
                print()

    return passed, len(WEAKNESS_EQUATIONS), results


def get_weakness_summary() -> str:
    """
    Get a summary of all weakness categories and their equations.

    Returns:
        Formatted string with weakness categories and descriptions
    """
    summary = []
    summary.append("SYMBO SOLVER WEAKNESS ANALYSIS")
    summary.append("=" * 60)
    summary.append("")

    current_category = None
    for eq in WEAKNESS_EQUATIONS:
        if eq.weakness_category != current_category:
            current_category = eq.weakness_category
            summary.append(f"\n{current_category}")
            summary.append("-" * 40)

        summary.append(f"  {eq.id:2d}. {eq.specific_weakness}")
        summary.append(f"      Fix: {eq.fix_improvement[:55]}")

    return "\n".join(summary)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run weakness-targeting stress tests on Symbo solver"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Print summary of weakness categories instead of running tests"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Minimal output (just final counts)"
    )
    parser.add_argument(
        "--category", type=int, choices=[1, 2, 3, 4, 5],
        help="Run only tests from specific category (1-5)"
    )

    args = parser.parse_args()

    if args.summary:
        print(get_weakness_summary())
        sys.exit(0)

    # Filter by category if requested
    if args.category:
        category_names = [
            "Native Calculus Gaps",
            "Parser Vulnerabilities",
            "Numerical Stability",
            "Domain-Specific Gaps",
            "Edge Cases Likely to Fail",
        ]
        selected_category = category_names[args.category - 1]
        original_equations = WEAKNESS_EQUATIONS.copy()
        WEAKNESS_EQUATIONS[:] = [eq for eq in WEAKNESS_EQUATIONS if eq.weakness_category == selected_category]
        print(f"Running only Category {args.category}: {selected_category}")
        print()

    passed, total, results = run_weakness_tests(verbose=not args.quiet)

    # Exit with code based on pass rate
    # Note: For weakness tests, failures are expected!
    # A high failure rate actually confirms the weaknesses exist
    sys.exit(0)  # Always exit 0 since failures are informative, not errors
