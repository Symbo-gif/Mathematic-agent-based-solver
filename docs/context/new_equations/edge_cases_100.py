#!/usr/bin/env python3
"""
100 Edge-Case Equations for Mathematical Solver Weakness Detection
===================================================================

This module contains 100 carefully designed edge-case equations that target
specific weaknesses in mathematical solvers, parsers, and symbolic computation
systems. Each equation is documented with:
  - The specific edge case being tested
  - Expected behavior (correct answer OR expected failure mode)
  - Rationale for why this edge case matters

Categories:
  1. Parser Edge Cases (1-20)
  2. Numerical Edge Cases (21-40)
  3. Symbolic Edge Cases (41-60)
  4. Computational Edge Cases (61-80)
  5. Type Confusion Cases (81-100)

Usage:
    python edge_cases_100.py

Author: Mathematical Research Analyst
Date: 2025-12-14
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple, Any
from enum import Enum

# Add the src directory to the path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


class EdgeCaseCategory(Enum):
    """Categories of edge cases."""
    PARSER = "parser"
    NUMERICAL = "numerical"
    SYMBOLIC = "symbolic"
    COMPUTATIONAL = "computational"
    TYPE_CONFUSION = "type_confusion"


@dataclass
class EdgeCaseEquation:
    """
    A single edge-case equation with full documentation.

    Attributes:
        id: Unique identifier (1-100)
        expression: The mathematical expression to test
        category: The type of edge case
        subcategory: More specific classification
        description: Human-readable description
        expected_result: What the correct answer should be (or "FAIL_GRACEFULLY")
        failure_mode: Expected failure mode if this is a "should fail" test
        rationale: Why this edge case matters for solver robustness
    """
    id: int
    expression: str
    category: EdgeCaseCategory
    subcategory: str
    description: str
    expected_result: str
    failure_mode: Optional[str]
    rationale: str


# =============================================================================
# EDGE CASE EQUATIONS DATABASE
# =============================================================================

EDGE_CASES: List[EdgeCaseEquation] = [

    # =========================================================================
    # CATEGORY 1: PARSER EDGE CASES (1-20)
    # =========================================================================

    # --- 1.1 Deeply Nested Parentheses (1-5) ---

    EdgeCaseEquation(
        id=1,
        expression="((((((((((x)))))))))))",
        category=EdgeCaseCategory.PARSER,
        subcategory="deeply_nested_parentheses",
        description="10 levels of nested parentheses around single variable",
        expected_result="x",
        failure_mode=None,
        rationale="Tests parser stack depth and ability to simplify trivial nesting. "
                  "Some parsers have hard-coded recursion limits or allocate O(n) stack frames."
    ),

    EdgeCaseEquation(
        id=2,
        expression="((((((((((1+((((((((((2)))))))))))))))))))))))",
        category=EdgeCaseCategory.PARSER,
        subcategory="deeply_nested_parentheses",
        description="20+ levels of mixed nested parentheses with addition",
        expected_result="3",
        failure_mode="RecursionError or StackOverflow",
        rationale="Extreme nesting tests AST construction limits. Production parsers "
                  "should handle this gracefully, not crash."
    ),

    EdgeCaseEquation(
        id=3,
        expression="(((((sin(((((cos(((((tan(((((x))))))))))))))))))))))",
        category=EdgeCaseCategory.PARSER,
        subcategory="deeply_nested_parentheses",
        description="Nested trig functions with excessive parentheses",
        expected_result="sin(cos(tan(x)))",
        failure_mode=None,
        rationale="Combines function call parsing with nesting. Tests that function "
                  "boundaries are correctly identified within deep nesting."
    ),

    EdgeCaseEquation(
        id=4,
        expression="((((((((((a+b)*(c+d))/(e+f))-((g*h)/(i+j)))+k)-l)*m)/n)+o)-p",
        category=EdgeCaseCategory.PARSER,
        subcategory="deeply_nested_parentheses",
        description="Complex arithmetic with multiple nested subexpressions",
        expected_result="SYMBOLIC",
        failure_mode=None,
        rationale="Real-world expressions often have complex nesting. Parser must "
                  "correctly preserve operator precedence through all levels."
    ),

    EdgeCaseEquation(
        id=5,
        expression="(" * 100 + "x" + ")" * 100,
        category=EdgeCaseCategory.PARSER,
        subcategory="deeply_nested_parentheses",
        description="100 levels of parentheses (stress test)",
        expected_result="x",
        failure_mode="RecursionError or FAIL_GRACEFULLY with depth limit",
        rationale="Extreme stress test for parser depth limits. Good solvers should "
                  "either handle this or fail gracefully with a clear error message."
    ),

    # --- 1.2 Unicode Mathematical Symbols (6-10) ---

    EdgeCaseEquation(
        id=6,
        expression="2*pi + e",
        category=EdgeCaseCategory.PARSER,
        subcategory="unicode_symbols",
        description="Greek letter pi as symbol (should interpret as constant)",
        expected_result="2*pi + e",
        failure_mode="Unknown symbol error",
        rationale="Unicode mathematical symbols are common in copy-paste from papers. "
                  "Parser should recognize standard mathematical Unicode."
    ),

    EdgeCaseEquation(
        id=7,
        expression="alpha + beta + gamma",
        category=EdgeCaseCategory.PARSER,
        subcategory="unicode_symbols",
        description="Multiple Greek letters as variables",
        expected_result="SYMBOLIC (sum of three symbols)",
        failure_mode="Encoding error",
        rationale="Greek letters are standard mathematical notation. Parser must "
                  "handle UTF-8/Unicode correctly."
    ),

    EdgeCaseEquation(
        id=8,
        expression="x^2 + y^2 = r^2",
        category=EdgeCaseCategory.PARSER,
        subcategory="unicode_symbols",
        description="Superscript digits (Unicode exponents)",
        expected_result="x**2 + y**2 = r**2",
        failure_mode="Parse error on superscript",
        rationale="Copy-paste from formatted documents often includes superscripts. "
                  "Robust parsers should normalize these to ** notation."
    ),

    EdgeCaseEquation(
        id=9,
        expression="integral(x^2, x, 0, infinity)",
        category=EdgeCaseCategory.PARSER,
        subcategory="unicode_symbols",
        description="Integral sign with infinity symbol",
        expected_result="DIVERGES or oo",
        failure_mode="Unicode parse error",
        rationale="Mathematical notation often uses symbols. This tests both "
                  "Unicode handling and recognition of infinity as a limit."
    ),

    EdgeCaseEquation(
        id=10,
        expression="sqrt(x) + root_3(y) + root_4(z)",
        category=EdgeCaseCategory.PARSER,
        subcategory="unicode_symbols",
        description="Various root symbols with subscripts",
        expected_result="sqrt(x) + y**(1/3) + z**(1/4)",
        failure_mode="Unknown symbol",
        rationale="Root symbols with indices are mathematically standard. "
                  "Parser should interpret subscripts as root indices."
    ),

    # --- 1.3 Ambiguous Notation (11-15) ---

    EdgeCaseEquation(
        id=11,
        expression="sin x^2",
        category=EdgeCaseCategory.PARSER,
        subcategory="ambiguous_notation",
        description="Ambiguous: sin(x)^2 or sin(x^2)?",
        expected_result="sin(x)**2 (standard convention)",
        failure_mode=None,
        rationale="This notation is genuinely ambiguous. Tests whether parser "
                  "follows standard conventions (sin^2 x means (sin x)^2)."
    ),

    EdgeCaseEquation(
        id=12,
        expression="log log x",
        category=EdgeCaseCategory.PARSER,
        subcategory="ambiguous_notation",
        description="Repeated function without parentheses",
        expected_result="log(log(x))",
        failure_mode="Parse error or misinterpretation",
        rationale="Missing parentheses in nested functions. Parser should either "
                  "reject or apply consistent associativity rules."
    ),

    EdgeCaseEquation(
        id=13,
        expression="2x + 3y",
        category=EdgeCaseCategory.PARSER,
        subcategory="ambiguous_notation",
        description="Implicit multiplication (no * symbol)",
        expected_result="2*x + 3*y",
        failure_mode="Unknown symbol '2x'",
        rationale="Implicit multiplication is standard in mathematics but not in "
                  "programming. Good math parsers should handle this."
    ),

    EdgeCaseEquation(
        id=14,
        expression="sin^2(x) + cos^2(x)",
        category=EdgeCaseCategory.PARSER,
        subcategory="ambiguous_notation",
        description="Power notation on function name",
        expected_result="1",
        failure_mode="Parse error on sin^2",
        rationale="This common notation (sin^2) places the exponent on the function "
                  "name, not the argument. Parser must recognize this idiom."
    ),

    EdgeCaseEquation(
        id=15,
        expression="f(x)(y)",
        category=EdgeCaseCategory.PARSER,
        subcategory="ambiguous_notation",
        description="Function returning function (currying notation)",
        expected_result="SYMBOLIC or function application",
        failure_mode="Double call parse error",
        rationale="Higher-order functions are valid in mathematics. This tests "
                  "whether the parser supports function composition/currying."
    ),

    # --- 1.4 Long Expressions (16-18) ---

    EdgeCaseEquation(
        id=16,
        expression=" + ".join([f"x_{i}" for i in range(100)]),
        category=EdgeCaseCategory.PARSER,
        subcategory="long_expressions",
        description="Sum of 100 distinct variables",
        expected_result="SYMBOLIC (sum of 100 terms)",
        failure_mode="Memory exhaustion or timeout",
        rationale="Large expressions test memory management and symbol table "
                  "scaling. This is common in generated expressions."
    ),

    EdgeCaseEquation(
        id=17,
        expression="*".join(["x" for _ in range(50)]),
        category=EdgeCaseCategory.PARSER,
        subcategory="long_expressions",
        description="Product of 50 x terms (x^50 written verbosely)",
        expected_result="x**50",
        failure_mode="Parser timeout or O(n^2) slowdown",
        rationale="Tests simplification of repeated multiplication. Good solvers "
                  "should recognize this pattern quickly."
    ),

    EdgeCaseEquation(
        id=18,
        expression="sin(" * 20 + "x" + ")" * 20,
        category=EdgeCaseCategory.PARSER,
        subcategory="long_expressions",
        description="20 nested sin functions",
        expected_result="sin(sin(sin(...sin(x)...)))",
        failure_mode="Stack overflow on evaluation",
        rationale="Deep function nesting tests both parsing and evaluation. "
                  "This may trigger numerical instability in evaluation."
    ),

    # --- 1.5 Function Name Edge Cases (19-20) ---

    EdgeCaseEquation(
        id=19,
        expression="Sin(x) + SIN(x) + sIn(x)",
        category=EdgeCaseCategory.PARSER,
        subcategory="function_names",
        description="Case variations of sin function",
        expected_result="3*sin(x) or error",
        failure_mode="Unknown function for wrong case",
        rationale="Tests case sensitivity policy. Mathematical notation is "
                  "traditionally case-insensitive for standard functions."
    ),

    EdgeCaseEquation(
        id=20,
        expression="arcsin(x) + asin(x) + sin^{-1}(x)",
        category=EdgeCaseCategory.PARSER,
        subcategory="function_names",
        description="Different notations for inverse sine",
        expected_result="3*asin(x)",
        failure_mode="Unknown function",
        rationale="Inverse trig has multiple common notations. Robust parsers "
                  "should recognize all standard variants."
    ),

    # =========================================================================
    # CATEGORY 2: NUMERICAL EDGE CASES (21-40)
    # =========================================================================

    # --- 2.1 Very Large/Small Numbers (21-25) ---

    EdgeCaseEquation(
        id=21,
        expression="10**308 + 1",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="large_numbers",
        description="Near IEEE 754 double max (1.8e308)",
        expected_result="10**308 + 1 (exact) or 1e308 (float)",
        failure_mode="Overflow to infinity",
        rationale="Tests whether solver uses arbitrary precision or floats. "
                  "10^308 is near float64 max; adding 1 tests precision loss."
    ),

    EdgeCaseEquation(
        id=22,
        expression="10**(-323)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="small_numbers",
        description="Near IEEE 754 double min subnormal",
        expected_result="10**(-323) (exact) or 1e-323 (subnormal)",
        failure_mode="Underflow to zero",
        rationale="Subnormal floats have reduced precision. Tests whether "
                  "solver handles graceful underflow or uses exact arithmetic."
    ),

    EdgeCaseEquation(
        id=23,
        expression="factorial(170)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="large_numbers",
        description="Factorial just within float64 range",
        expected_result="LARGE_INTEGER (exact) or ~7.26e306",
        failure_mode="Overflow",
        rationale="170! is the largest factorial representable in float64. "
                  "Tests factorial implementation limits."
    ),

    EdgeCaseEquation(
        id=24,
        expression="factorial(171)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="large_numbers",
        description="Factorial exceeding float64 range",
        expected_result="LARGE_INTEGER (exact) or oo (symbolic)",
        failure_mode="Overflow to inf",
        rationale="171! exceeds float64. Solver should use big integers or "
                  "return symbolic infinity."
    ),

    EdgeCaseEquation(
        id=25,
        expression="(10**100)**100",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="large_numbers",
        description="Googolplex-scale number",
        expected_result="10**10000",
        failure_mode="Memory exhaustion or overflow",
        rationale="Tests whether exponentiation is symbolic. Computing this "
                  "literally is impossible; must simplify symbolically."
    ),

    # --- 2.2 Precision Limits (26-30) ---

    EdgeCaseEquation(
        id=26,
        expression="0.1 + 0.2 - 0.3",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="precision",
        description="Classic floating-point representation error",
        expected_result="0 (exact) or ~5.55e-17 (float)",
        failure_mode=None,
        rationale="The famous 0.1+0.2!=0.3 in floats. Tests whether solver "
                  "uses exact rationals or float arithmetic."
    ),

    EdgeCaseEquation(
        id=27,
        expression="(1 + 1e-16) - 1",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="precision",
        description="Catastrophic cancellation near machine epsilon",
        expected_result="1e-16 (exact) or 0 (rounded)",
        failure_mode="Precision loss",
        rationale="Tests sensitivity to catastrophic cancellation. Machine "
                  "epsilon for float64 is ~2.2e-16."
    ),

    EdgeCaseEquation(
        id=28,
        expression="sqrt(2)**2 - 2",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="precision",
        description="Should be exactly zero but float gives error",
        expected_result="0 (symbolic) or ~4.44e-16 (float)",
        failure_mode=None,
        rationale="Tests symbolic vs numerical computation. Symbolic sqrt "
                  "should satisfy sqrt(2)^2 = 2 exactly."
    ),

    EdgeCaseEquation(
        id=29,
        expression="sin(pi)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="precision",
        description="Should be exactly zero",
        expected_result="0",
        failure_mode="Small nonzero value (~1.2e-16)",
        rationale="Tests recognition of exact values at special points. "
                  "Numerical evaluation gives nonzero due to pi approximation."
    ),

    EdgeCaseEquation(
        id=30,
        expression="exp(log(x)) - x",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="precision",
        description="Algebraic identity should simplify to zero",
        expected_result="0",
        failure_mode="Expression unchanged",
        rationale="Tests whether solver recognizes inverse function pairs. "
                  "This is a fundamental algebraic identity."
    ),

    # --- 2.3 Overflow/Underflow Scenarios (31-35) ---

    EdgeCaseEquation(
        id=31,
        expression="exp(1000)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="overflow",
        description="Exponential overflow",
        expected_result="e**1000 (symbolic) or oo (numeric)",
        failure_mode="Float overflow to inf",
        rationale="e^1000 >> float64 max. Tests symbolic preservation vs "
                  "numeric overflow handling."
    ),

    EdgeCaseEquation(
        id=32,
        expression="exp(-1000)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="underflow",
        description="Exponential underflow",
        expected_result="e**(-1000) (symbolic) or 0 (underflow)",
        failure_mode="Underflow to zero",
        rationale="e^-1000 << float64 min. Tests whether tiny values are "
                  "preserved symbolically or underflow."
    ),

    EdgeCaseEquation(
        id=33,
        expression="gamma(171.5)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="overflow",
        description="Gamma function near overflow boundary",
        expected_result="~5.04e307 (at limit of float64)",
        failure_mode="Overflow",
        rationale="Gamma function grows faster than exponential. Tests "
                  "special function overflow handling."
    ),

    EdgeCaseEquation(
        id=34,
        expression="binomial(1000, 500)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="overflow",
        description="Large binomial coefficient",
        expected_result="EXACT_LARGE_INTEGER (~2.7e299)",
        failure_mode="Overflow if using intermediate factorials",
        rationale="Tests binomial implementation. Naive factorial approach "
                  "overflows; good implementations use log-space or exact."
    ),

    EdgeCaseEquation(
        id=35,
        expression="2.0**1024",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="overflow",
        description="Exactly at float64 overflow boundary",
        expected_result="oo or 2**1024 (symbolic)",
        failure_mode="Overflow",
        rationale="2^1024 is exactly the overflow threshold for float64. "
                  "Tests boundary handling precision."
    ),

    # --- 2.4 NaN and Infinity Handling (36-40) ---

    EdgeCaseEquation(
        id=36,
        expression="0/0",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="nan_inf",
        description="Indeterminate form 0/0",
        expected_result="nan or UNDEFINED",
        failure_mode="Crash or uncaught exception",
        rationale="Classic indeterminate form. Solver must handle gracefully, "
                  "not crash. May return nan or raise controlled error."
    ),

    EdgeCaseEquation(
        id=37,
        expression="oo - oo",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="nan_inf",
        description="Indeterminate infinity subtraction",
        expected_result="nan or UNDEFINED",
        failure_mode="Crash",
        rationale="Infinity arithmetic requires special handling. This is "
                  "mathematically undefined, not zero."
    ),

    EdgeCaseEquation(
        id=38,
        expression="0 * oo",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="nan_inf",
        description="Indeterminate form 0 * infinity",
        expected_result="nan or UNDEFINED",
        failure_mode="0 or oo (incorrect)",
        rationale="0*oo is indeterminate. Tests whether infinity is handled "
                  "as a limit concept, not a simple large number."
    ),

    EdgeCaseEquation(
        id=39,
        expression="oo/oo",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="nan_inf",
        description="Indeterminate infinity division",
        expected_result="nan or UNDEFINED",
        failure_mode="1 (incorrect)",
        rationale="oo/oo is not 1. Tests proper indeterminate form handling."
    ),

    EdgeCaseEquation(
        id=40,
        expression="log(0)",
        category=EdgeCaseCategory.NUMERICAL,
        subcategory="nan_inf",
        description="Logarithm at singularity",
        expected_result="-oo or UNDEFINED",
        failure_mode="Crash or nan",
        rationale="log(0) = -infinity by limit. Tests singularity handling "
                  "at well-known special points."
    ),

    # =========================================================================
    # CATEGORY 3: SYMBOLIC EDGE CASES (41-60)
    # =========================================================================

    # --- 3.1 Division by Zero-Possible Expressions (41-45) ---

    EdgeCaseEquation(
        id=41,
        expression="1/(x - x)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="division_by_zero",
        description="Division by symbolically zero expression",
        expected_result="UNDEFINED or zoo (complex infinity)",
        failure_mode="1/0 error after simplification",
        rationale="Tests whether simplification happens before or after "
                  "division. x-x=0 should be detected."
    ),

    EdgeCaseEquation(
        id=42,
        expression="(x^2 - 1)/(x - 1)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="division_by_zero",
        description="Removable singularity at x=1",
        expected_result="x + 1 (with note: x != 1)",
        failure_mode="Loses domain restriction",
        rationale="This simplifies to x+1 but is undefined at x=1. Good "
                  "solvers track domain restrictions."
    ),

    EdgeCaseEquation(
        id=43,
        expression="limit((x^2 - 1)/(x - 1), x, 1)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="division_by_zero",
        description="Limit at removable singularity",
        expected_result="2",
        failure_mode="UNDEFINED or error",
        rationale="L'Hopital or factoring gives limit = 2. Tests limit "
                  "handling at removable singularities."
    ),

    EdgeCaseEquation(
        id=44,
        expression="1/sin(x) where x approaches 0",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="division_by_zero",
        description="Division by function approaching zero",
        expected_result="DIVERGES (pole)",
        failure_mode="Numeric error",
        rationale="1/sin(x) has a pole at x=0. Tests symbolic singularity "
                  "detection vs numeric instability."
    ),

    EdgeCaseEquation(
        id=45,
        expression="(sin(x) - x + x**3/6)/(x**5)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="division_by_zero",
        description="Taylor series residual ratio",
        expected_result="limit is -1/120 as x->0",
        failure_mode="0/0 indeterminate",
        rationale="Requires Taylor expansion to 5th order. Tests symbolic "
                  "series expansion capabilities."
    ),

    # --- 3.2 Square Roots of Negative Values (46-50) ---

    EdgeCaseEquation(
        id=46,
        expression="sqrt(-1)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="negative_sqrt",
        description="Square root of -1 (imaginary unit)",
        expected_result="I (imaginary unit)",
        failure_mode="Error or nan",
        rationale="Fundamental complex number. Tests whether solver supports "
                  "complex numbers or only reals."
    ),

    EdgeCaseEquation(
        id=47,
        expression="sqrt(x^2)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="negative_sqrt",
        description="Square root of square (sign ambiguity)",
        expected_result="|x| or Abs(x) (NOT just x)",
        failure_mode="x (incorrect for negative x)",
        rationale="sqrt(x^2) = |x|, not x. Tests awareness of branch cuts "
                  "and absolute value handling."
    ),

    EdgeCaseEquation(
        id=48,
        expression="sqrt(-x^2 - 1)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="negative_sqrt",
        description="Always-negative radicand",
        expected_result="I*sqrt(x^2 + 1)",
        failure_mode="Error for all real x",
        rationale="x^2+1 > 0 for all real x, so radicand is always negative. "
                  "Tests complex result in real-looking expression."
    ),

    EdgeCaseEquation(
        id=49,
        expression="(-8)**(1/3)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="negative_sqrt",
        description="Cube root of negative number",
        expected_result="-2 (real) or complex principal root",
        failure_mode="Error or complex when real expected",
        rationale="Odd roots of negatives are real. Tests branch cut choice "
                  "for fractional powers."
    ),

    EdgeCaseEquation(
        id=50,
        expression="sqrt(x) * sqrt(-x)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="negative_sqrt",
        description="Product of sqrt(x) and sqrt(-x)",
        expected_result="I*|x| or I*sqrt(-x^2)",
        failure_mode="sqrt(-x^2) without simplification",
        rationale="This product involves conflicting domain requirements. "
                  "Tests how solver handles impossible real evaluations."
    ),

    # --- 3.3 Logarithms Near Zero/Negative (51-55) ---

    EdgeCaseEquation(
        id=51,
        expression="log(-1)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="log_edge",
        description="Logarithm of -1",
        expected_result="I*pi",
        failure_mode="Error or undefined",
        rationale="log(-1) = I*pi by Euler's formula. Tests complex logarithm "
                  "support."
    ),

    EdgeCaseEquation(
        id=52,
        expression="log(exp(x)) - x",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="log_edge",
        description="Log-exp identity with branch considerations",
        expected_result="0 (for real x) or 2*pi*I*n (complex)",
        failure_mode="Not simplified",
        rationale="For real x, this is 0. For complex, branch cuts matter. "
                  "Tests inverse function simplification."
    ),

    EdgeCaseEquation(
        id=53,
        expression="log(x*y) - log(x) - log(y)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="log_edge",
        description="Log product rule (requires positive assumption)",
        expected_result="0 (if x,y > 0) or may not simplify",
        failure_mode="Blindly returns 0 without checking signs",
        rationale="Log product rule only holds for positive arguments. "
                  "Tests assumption tracking."
    ),

    EdgeCaseEquation(
        id=54,
        expression="limit(x * log(x), x, 0, '+')",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="log_edge",
        description="Indeterminate 0 * (-infinity) form",
        expected_result="0",
        failure_mode="UNDEFINED or incorrect",
        rationale="Classic L'Hopital problem: x*log(x) -> 0 as x -> 0+. "
                  "Tests limit handling of log singularity."
    ),

    EdgeCaseEquation(
        id=55,
        expression="log(0 + 0*I)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="log_edge",
        description="Logarithm of complex zero",
        expected_result="UNDEFINED (essential singularity)",
        failure_mode="Crash or -oo",
        rationale="Complex log(0) is undefined (no valid angle). Tests "
                  "complex singularity handling."
    ),

    # --- 3.4 Limits at Singularities (56-58) ---

    EdgeCaseEquation(
        id=56,
        expression="limit(1/x, x, 0)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="singularity_limits",
        description="Simple pole limit (two-sided)",
        expected_result="UNDEFINED (left limit -oo, right limit +oo)",
        failure_mode="oo or -oo (one-sided only)",
        rationale="Two-sided limit at pole doesn't exist. Tests whether "
                  "solver distinguishes one-sided vs two-sided limits."
    ),

    EdgeCaseEquation(
        id=57,
        expression="limit(sin(1/x), x, 0)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="singularity_limits",
        description="Essential singularity (oscillating)",
        expected_result="UNDEFINED (oscillates)",
        failure_mode="0 or any finite value",
        rationale="sin(1/x) oscillates infinitely fast as x->0. The limit "
                  "does not exist, not even infinity."
    ),

    EdgeCaseEquation(
        id=58,
        expression="limit(exp(-1/x^2), x, 0)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="singularity_limits",
        description="Smooth function with essential singularity at 0",
        expected_result="0 (from both sides)",
        failure_mode="Error or nonzero",
        rationale="This famous function is C-infinity but not analytic at 0. "
                  "All derivatives vanish. Tests smooth singularity limits."
    ),

    # --- 3.5 Branch Cut Handling (59-60) ---

    EdgeCaseEquation(
        id=59,
        expression="arg(-1 + 0.0001*I) - arg(-1 - 0.0001*I)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="branch_cuts",
        description="Argument function near negative real axis branch cut",
        expected_result="~2*pi (jump across cut)",
        failure_mode="~0 (ignoring branch cut)",
        rationale="The arg function has a branch cut on negative real axis. "
                  "Points just above and below give ~pi and ~-pi."
    ),

    EdgeCaseEquation(
        id=60,
        expression="sqrt(-1 + 0.0001) - sqrt(-1 - 0.0001)",
        category=EdgeCaseCategory.SYMBOLIC,
        subcategory="branch_cuts",
        description="Square root branch cut transition",
        expected_result="~2*I (discontinuity)",
        failure_mode="~0 (not recognizing branch)",
        rationale="sqrt has branch cut on negative reals. Tests numerical "
                  "stability near branch cuts."
    ),

    # =========================================================================
    # CATEGORY 4: COMPUTATIONAL EDGE CASES (61-80)
    # =========================================================================

    # --- 4.1 Infinite Loop / Non-Terminating Simplification (61-65) ---

    EdgeCaseEquation(
        id=61,
        expression="simplify(x + sin(x) - sin(x) + cos(x) - cos(x))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="simplification_loops",
        description="Trivial expression that should simplify immediately",
        expected_result="x",
        failure_mode="Infinite simplification loop",
        rationale="Tests whether simplification terminates on trivially "
                  "reducible expressions."
    ),

    EdgeCaseEquation(
        id=62,
        expression="expand((x + y + z)**20)",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="simplification_loops",
        description="Large polynomial expansion",
        expected_result="Polynomial with 1771 terms",
        failure_mode="Timeout or memory exhaustion",
        rationale="(x+y+z)^20 has C(22,2)=231... terms. Tests expansion "
                  "algorithm efficiency."
    ),

    EdgeCaseEquation(
        id=63,
        expression="factor(x**100 - 1)",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="simplification_loops",
        description="Cyclotomic polynomial factorization",
        expected_result="Product of cyclotomic factors",
        failure_mode="Timeout on large factorization",
        rationale="x^100-1 factors into cyclotomics. Tests factorization "
                  "algorithm for special forms."
    ),

    EdgeCaseEquation(
        id=64,
        expression="gcd(fibonacci(100), fibonacci(101))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="simplification_loops",
        description="GCD of consecutive Fibonacci numbers",
        expected_result="1 (always coprime)",
        failure_mode="Slow GCD on large numbers",
        rationale="Consecutive Fibonaccis are coprime. Tests whether solver "
                  "knows this property or computes naively."
    ),

    EdgeCaseEquation(
        id=65,
        expression="simplify(tan(x)**2 - sec(x)**2 + 1)",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="simplification_loops",
        description="Trig identity that should yield 0",
        expected_result="0",
        failure_mode="Doesn't recognize identity",
        rationale="tan^2 + 1 = sec^2 is a fundamental identity. Tests trig "
                  "simplification rules."
    ),

    # --- 4.2 Slow-Converging Series (66-70) ---

    EdgeCaseEquation(
        id=66,
        expression="summation((-1)**(n+1)/n, (n, 1, oo))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="slow_series",
        description="Alternating harmonic series (ln(2))",
        expected_result="log(2)",
        failure_mode="Timeout on numerical summation",
        rationale="Converges extremely slowly. Tests series recognition vs "
                  "naive summation."
    ),

    EdgeCaseEquation(
        id=67,
        expression="summation(1/n**2, (n, 1, oo))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="slow_series",
        description="Basel problem (pi^2/6)",
        expected_result="pi**2/6",
        failure_mode="Numerical approximation only",
        rationale="Famous result. Tests whether solver recognizes known "
                  "series values or just approximates."
    ),

    EdgeCaseEquation(
        id=68,
        expression="summation(1/(n*(n+1)), (n, 1, oo))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="slow_series",
        description="Telescoping series",
        expected_result="1",
        failure_mode="Doesn't recognize telescoping",
        rationale="Partial fractions give telescoping sum. Tests symbolic "
                  "series manipulation."
    ),

    EdgeCaseEquation(
        id=69,
        expression="product((1 - 1/n**2), (n, 2, oo))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="slow_series",
        description="Infinite product (Wallis-like)",
        expected_result="1/2",
        failure_mode="Diverges or wrong value",
        rationale="This product converges to 1/2. Tests infinite product "
                  "evaluation capabilities."
    ),

    EdgeCaseEquation(
        id=70,
        expression="summation(1/factorial(n), (n, 0, oo))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="slow_series",
        description="Exponential series at x=1",
        expected_result="e",
        failure_mode="Only approximation",
        rationale="Definition of e. Tests recognition of fundamental "
                  "series definitions."
    ),

    # --- 4.3 Numerically Unstable Calculations (71-75) ---

    EdgeCaseEquation(
        id=71,
        expression="(1 - cos(x))/x**2 where x = 1e-8",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="numerical_instability",
        description="Catastrophic cancellation in numerator",
        expected_result="~0.5",
        failure_mode="0 or huge error due to cancellation",
        rationale="cos(1e-8) ~ 1 - 5e-17, causing cancellation. Stable "
                  "calculation uses Taylor series."
    ),

    EdgeCaseEquation(
        id=72,
        expression="exp(x) - 1 where x = 1e-15",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="numerical_instability",
        description="expm1 situation - loss of precision",
        expected_result="~1e-15",
        failure_mode="0 (precision loss)",
        rationale="exp(1e-15) rounds to 1 in float64. Tests whether solver "
                  "uses expm1-like stable formulas."
    ),

    EdgeCaseEquation(
        id=73,
        expression="log(1 + x) where x = 1e-16",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="numerical_instability",
        description="log1p situation - precision loss",
        expected_result="~1e-16",
        failure_mode="0 (1+x rounds to 1)",
        rationale="Similar to expm1; 1+1e-16 rounds to 1. Tests log1p usage."
    ),

    EdgeCaseEquation(
        id=74,
        expression="sqrt(x**2 + 1) - x where x = 1e8",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="numerical_instability",
        description="Hyperbolic subtraction instability",
        expected_result="~5e-9",
        failure_mode="0 (cancellation)",
        rationale="sqrt(1e16 + 1) ~ 1e8, causing cancellation. Requires "
                  "rationalized form: 1/(sqrt(x^2+1)+x)."
    ),

    EdgeCaseEquation(
        id=75,
        expression="sin(x)/x where x = 1e-100",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="numerical_instability",
        description="sinc function at tiny argument",
        expected_result="1 (limit)",
        failure_mode="0/0 or nan",
        rationale="sinc(x) -> 1 as x -> 0. At 1e-100, float sin gives 0. "
                  "Tests special case handling."
    ),

    # --- 4.4 Memory-Intensive Expansions (76-80) ---

    EdgeCaseEquation(
        id=76,
        expression="expand((a+b+c+d+e+f+g+h+i+j)**10)",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="memory_intensive",
        description="10-variable polynomial expansion",
        expected_result="Polynomial with C(19,9)=92378 terms",
        failure_mode="Memory exhaustion",
        rationale="Multinomial expansion creates huge number of terms. Tests "
                  "memory management in symbolic computation."
    ),

    EdgeCaseEquation(
        id=77,
        expression="diff(sin(x)**100, x, 50)",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="memory_intensive",
        description="50th derivative of sin^100",
        expected_result="Complex expression in sin/cos",
        failure_mode="Exponential expression growth",
        rationale="Each differentiation can double expression size. Tests "
                  "derivative simplification to prevent blowup."
    ),

    EdgeCaseEquation(
        id=78,
        expression="taylor(exp(sin(x)), x, 0, 20)",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="memory_intensive",
        description="Taylor series of composition",
        expected_result="1 + x + x^2/2 - x^4/8 + ... (20 terms)",
        failure_mode="Slow composition of series",
        rationale="Composition of Taylor series requires convolution-like "
                  "computation. Tests efficiency."
    ),

    EdgeCaseEquation(
        id=79,
        expression="det(Matrix([[a,b,c,d,e],[f,g,h,i,j],[k,l,m,n,o],[p,q,r,s,t],[u,v,w,x,y]]))",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="memory_intensive",
        description="5x5 symbolic determinant",
        expected_result="120-term polynomial",
        failure_mode="Exponential expansion (5! = 120 terms minimum)",
        rationale="Symbolic determinant grows factorially. Tests Bareiss or "
                  "similar optimized algorithms."
    ),

    EdgeCaseEquation(
        id=80,
        expression="resultant(x**10 + a*x**5 + b, x**10 + c*x**5 + d, x)",
        category=EdgeCaseCategory.COMPUTATIONAL,
        subcategory="memory_intensive",
        description="Resultant of high-degree polynomials",
        expected_result="Polynomial in a,b,c,d",
        failure_mode="Huge intermediate expressions",
        rationale="Resultant computation can produce enormous intermediate "
                  "results. Tests polynomial algorithm efficiency."
    ),

    # =========================================================================
    # CATEGORY 5: TYPE CONFUSION CASES (81-100)
    # =========================================================================

    # --- 5.1 Mixed Real/Complex (81-85) ---

    EdgeCaseEquation(
        id=81,
        expression="sqrt(-1) + sqrt(-1)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="real_complex",
        description="Sum of imaginary units",
        expected_result="2*I",
        failure_mode="2*sqrt(-1) (unsimplified) or error",
        rationale="Tests whether complex arithmetic is properly unified. "
                  "Should recognize sqrt(-1) = I."
    ),

    EdgeCaseEquation(
        id=82,
        expression="re(exp(I*x))",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="real_complex",
        description="Real part of complex exponential",
        expected_result="cos(x)",
        failure_mode="Error or unsimplified",
        rationale="Euler's formula: exp(ix) = cos(x) + i*sin(x). Tests "
                  "complex decomposition."
    ),

    EdgeCaseEquation(
        id=83,
        expression="im(log(1 + I))",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="real_complex",
        description="Imaginary part of complex logarithm",
        expected_result="pi/4",
        failure_mode="Error or wrong branch",
        rationale="log(1+i) = ln(sqrt(2)) + i*pi/4. Tests complex log "
                  "decomposition."
    ),

    EdgeCaseEquation(
        id=84,
        expression="abs(3 + 4*I)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="real_complex",
        description="Absolute value of complex number",
        expected_result="5",
        failure_mode="Error or just 3+4",
        rationale="Classic 3-4-5 triangle. Tests complex magnitude "
                  "calculation."
    ),

    EdgeCaseEquation(
        id=85,
        expression="conjugate(a + b*I) * (a + b*I)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="real_complex",
        description="Complex number times conjugate",
        expected_result="a**2 + b**2",
        failure_mode="Unsimplified expression",
        rationale="z * conj(z) = |z|^2 is a fundamental identity. Tests "
                  "conjugate simplification."
    ),

    # --- 5.2 Integer vs Rational vs Float (86-90) ---

    EdgeCaseEquation(
        id=86,
        expression="1/3 + 1/3 + 1/3",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="int_rat_float",
        description="Sum of rationals that should be 1",
        expected_result="1 (exact)",
        failure_mode="0.999... or 1.0 (float)",
        rationale="Rational arithmetic should give exact 1, not a float. "
                  "Tests rational vs float distinction."
    ),

    EdgeCaseEquation(
        id=87,
        expression="22/7 - pi",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="int_rat_float",
        description="Rational approximation minus transcendental",
        expected_result="22/7 - pi (symbolic, ~0.00126)",
        failure_mode="0 (incorrect equality)",
        rationale="22/7 is NOT pi. Tests whether solver preserves symbolic "
                  "constants or converts to float."
    ),

    EdgeCaseEquation(
        id=88,
        expression="floor(2.999999999999999)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="int_rat_float",
        description="Floor of number very close to 3",
        expected_result="2 (exact float interpretation)",
        failure_mode="3 (rounded float)",
        rationale="2.999...9 (15 9s) may round to 3.0 in float64. Tests "
                  "floor/ceiling precision handling."
    ),

    EdgeCaseEquation(
        id=89,
        expression="mod(10, 3.0) - mod(10, 3)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="int_rat_float",
        description="Modulo with float vs integer divisor",
        expected_result="0",
        failure_mode="Small nonzero due to float",
        rationale="Tests whether mod preserves integer semantics when "
                  "arguments have different types."
    ),

    EdgeCaseEquation(
        id=90,
        expression="2**0.5 * 2**0.5",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="int_rat_float",
        description="Product of irrational powers",
        expected_result="2",
        failure_mode="2.0000000000000004 (float error)",
        rationale="2^0.5 * 2^0.5 = 2^1 = 2 exactly. Tests whether power "
                  "laws are applied symbolically."
    ),

    # --- 5.3 Symbolic vs Numeric Evaluation (91-95) ---

    EdgeCaseEquation(
        id=91,
        expression="limit(sin(x)/x, x, 0)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="symbolic_numeric",
        description="Classic limit requiring symbolic treatment",
        expected_result="1 (exact)",
        failure_mode="nan from 0/0",
        rationale="sin(x)/x -> 1 is fundamental. Numeric evaluation at x=0 "
                  "gives 0/0. Must use symbolic limits."
    ),

    EdgeCaseEquation(
        id=92,
        expression="N(pi, 50)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="symbolic_numeric",
        description="Numeric evaluation to 50 digits",
        expected_result="3.14159265358979323846264338327950288419716939937510",
        failure_mode="Only ~15 digits (float64 limit)",
        rationale="Tests arbitrary precision evaluation. Default float gives "
                  "only 15-17 significant digits."
    ),

    EdgeCaseEquation(
        id=93,
        expression="simplify(x**2 - 4) / simplify(x - 2)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="symbolic_numeric",
        description="Division of simplified expressions",
        expected_result="x + 2",
        failure_mode="(x^2-4)/(x-2) unsimplified",
        rationale="Tests whether simplify operates within larger expressions "
                  "or only at top level."
    ),

    EdgeCaseEquation(
        id=94,
        expression="solve(x**2 - 2, x)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="symbolic_numeric",
        description="Equation with irrational solutions",
        expected_result="[-sqrt(2), sqrt(2)]",
        failure_mode="[-1.414..., 1.414...] (numeric)",
        rationale="Solutions are irrational. Tests whether solve returns "
                  "symbolic or numeric results."
    ),

    EdgeCaseEquation(
        id=95,
        expression="integrate(1/(x**2 + 1), x)",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="symbolic_numeric",
        description="Integral with arctangent result",
        expected_result="atan(x) (+ C)",
        failure_mode="Numeric approximation",
        rationale="Antiderivative must be symbolic. Tests symbolic vs "
                  "numeric integration."
    ),

    # --- 5.4 Type Coercion Pitfalls (96-100) ---

    EdgeCaseEquation(
        id=96,
        expression="True + 1",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="type_coercion",
        description="Boolean in arithmetic context",
        expected_result="2 or TypeError",
        failure_mode="Inconsistent behavior",
        rationale="Python coerces True to 1. Tests whether math solver "
                  "follows same convention or rejects."
    ),

    EdgeCaseEquation(
        id=97,
        expression="'2' + 2",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="type_coercion",
        description="String-number addition",
        expected_result="TypeError or 4 (if parsed)",
        failure_mode="'22' (string concat)",
        rationale="Should either parse '2' as number or reject. Never "
                  "string concatenation in math context."
    ),

    EdgeCaseEquation(
        id=98,
        expression="[1, 2, 3] * 2",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="type_coercion",
        description="List times scalar",
        expected_result="[2, 4, 6] (elementwise) or [1,2,3,1,2,3]",
        failure_mode="Ambiguous interpretation",
        rationale="Python lists repeat; numpy arrays scale. Tests which "
                  "semantics the solver uses."
    ),

    EdgeCaseEquation(
        id=99,
        expression="Matrix([[1,2],[3,4]]) + 1",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="type_coercion",
        description="Matrix plus scalar",
        expected_result="[[2,3],[4,5]] or error",
        failure_mode="[[1+1,2],[3,4+1]] (diagonal only)",
        rationale="Some systems add scalar to all elements, some only to "
                  "diagonal. Tests broadcasting rules."
    ),

    EdgeCaseEquation(
        id=100,
        expression="sum([1, 2, 3]) + product([1, 2, 3])",
        category=EdgeCaseCategory.TYPE_CONFUSION,
        subcategory="type_coercion",
        description="List aggregation functions",
        expected_result="6 + 6 = 12",
        failure_mode="Error if sum/product don't accept lists",
        rationale="Tests whether sum() and product() handle Python lists "
                  "or require explicit conversion to symbolic."
    ),
]


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_edge_case_tests(verbose: bool = True) -> Tuple[int, int, List[dict]]:
    """
    Run all 100 edge case tests against the solver engine.

    Args:
        verbose: If True, print detailed output during execution

    Returns:
        (passed_count, total_count, detailed_results)
    """
    try:
        from symbo_agentic_reasoners.core.solver_engine import get_solver_engine
        solver = get_solver_engine()
    except ImportError as e:
        print(f"ERROR: Could not import solver engine: {e}")
        print("Make sure symbo_agentic_reasoners is installed and in PYTHONPATH")
        return 0, len(EDGE_CASES), []

    print("=" * 80)
    print("100 EDGE-CASE MATHEMATICAL SOLVER STRESS TESTS")
    print("=" * 80)
    print(f"Testing {len(EDGE_CASES)} edge cases across 5 categories\n")

    passed = 0
    failed = 0
    results = []

    # Group by category for reporting
    category_stats = {cat: {"passed": 0, "total": 0} for cat in EdgeCaseCategory}

    for eq in EDGE_CASES:
        category_stats[eq.category]["total"] += 1

        if verbose:
            print(f"[{eq.id:3d}/100] {eq.description[:55]:<55}", end=" ")

        try:
            start_time = time.time()
            result = solver.solve(eq.expression)
            elapsed = time.time() - start_time

            status = result.status.name if hasattr(result, 'status') else str(result.status)
            result_str = str(result.result) if result.result else "None"

            # Determine success/failure
            is_error = False
            if status in ["ERROR", "FAILURE"]:
                is_error = True
            elif "error" in result_str.lower() or "failed" in result_str.lower():
                is_error = True
            elif result_str == "None" or result_str == "":
                is_error = True
            elif "NotImplementedError" in result_str:
                is_error = True

            if is_error:
                if verbose:
                    print(f"FAIL ({elapsed:.2f}s)")
                failed += 1
            else:
                if verbose:
                    print(f"PASS ({elapsed:.2f}s)")
                passed += 1
                category_stats[eq.category]["passed"] += 1

            results.append({
                "id": eq.id,
                "expression": eq.expression[:50],
                "category": eq.category.value,
                "subcategory": eq.subcategory,
                "description": eq.description,
                "expected": eq.expected_result,
                "actual": result_str[:100],
                "status": status,
                "time": elapsed,
                "passed": not is_error
            })

        except Exception as e:
            if verbose:
                print(f"ERROR: {str(e)[:30]}")
            failed += 1
            results.append({
                "id": eq.id,
                "expression": eq.expression[:50],
                "category": eq.category.value,
                "subcategory": eq.subcategory,
                "description": eq.description,
                "expected": eq.expected_result,
                "actual": f"EXCEPTION: {str(e)[:80]}",
                "status": "EXCEPTION",
                "time": 0,
                "passed": False
            })

    # Print summary
    print()
    print("=" * 80)
    print(f"OVERALL RESULTS: {passed}/{len(EDGE_CASES)} passed ({100*passed/len(EDGE_CASES):.1f}%)")
    print("=" * 80)

    print("\nBY CATEGORY:")
    print("-" * 80)
    for cat in EdgeCaseCategory:
        stats = category_stats[cat]
        if stats["total"] > 0:
            pct = 100 * stats["passed"] / stats["total"]
            print(f"  {cat.value.upper():<20}: {stats['passed']:2d}/{stats['total']:2d} ({pct:5.1f}%)")

    # Print failures
    failures = [r for r in results if not r["passed"]]
    if failures and verbose:
        print("\nFAILED TESTS:")
        print("-" * 80)
        for f in failures[:20]:  # Limit to first 20
            print(f"[{f['id']:3d}] {f['description'][:60]}")
            print(f"      Category: {f['category']}/{f['subcategory']}")
            print(f"      Expected: {f['expected'][:60]}")
            print(f"      Actual:   {f['actual'][:60]}")
            print()
        if len(failures) > 20:
            print(f"      ... and {len(failures) - 20} more failures")

    return passed, len(EDGE_CASES), results


def get_equations_by_category(category: EdgeCaseCategory) -> List[EdgeCaseEquation]:
    """Get all equations in a specific category."""
    return [eq for eq in EDGE_CASES if eq.category == category]


def get_equation_by_id(eq_id: int) -> Optional[EdgeCaseEquation]:
    """Get a specific equation by ID."""
    for eq in EDGE_CASES:
        if eq.id == eq_id:
            return eq
    return None


def print_equation_details(eq_id: int) -> None:
    """Print detailed information about a specific edge case."""
    eq = get_equation_by_id(eq_id)
    if eq is None:
        print(f"No equation with ID {eq_id}")
        return

    print(f"\nEdge Case #{eq.id}")
    print("=" * 60)
    print(f"Category:     {eq.category.value}")
    print(f"Subcategory:  {eq.subcategory}")
    print(f"Description:  {eq.description}")
    print(f"\nExpression:")
    print(f"  {eq.expression}")
    print(f"\nExpected Result:")
    print(f"  {eq.expected_result}")
    if eq.failure_mode:
        print(f"\nExpected Failure Mode:")
        print(f"  {eq.failure_mode}")
    print(f"\nRationale:")
    print(f"  {eq.rationale}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run 100 edge-case mathematical solver tests")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    parser.add_argument("--category", "-c", type=str, help="Run only specific category")
    parser.add_argument("--id", "-i", type=int, help="Show details for specific test ID")
    parser.add_argument("--list", "-l", action="store_true", help="List all tests")

    args = parser.parse_args()

    if args.id:
        print_equation_details(args.id)
    elif args.list:
        print("ALL EDGE CASE EQUATIONS:")
        print("=" * 80)
        for eq in EDGE_CASES:
            print(f"[{eq.id:3d}] {eq.category.value:15s} | {eq.subcategory:25s} | {eq.description[:40]}")
    else:
        passed, total, _ = run_edge_case_tests(verbose=not args.quiet)
        sys.exit(0 if passed == total else 1)
