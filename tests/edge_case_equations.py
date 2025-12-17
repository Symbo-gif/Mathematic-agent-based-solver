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
Edge Case Equations - 100 Problems Targeting Solver Weaknesses
================================================================

These equations specifically target common failure modes in symbolic solvers:
- Boundary conditions and singularities
- Indeterminate forms requiring careful handling
- Near-zero numerical stability issues
- Branch cut and multi-valued function handling
- Parser and tokenizer edge cases
- Symbolic simplification traps
"""

# =============================================================================
# SINGULARITY AND REMOVABLE DISCONTINUITY CASES (20 equations)
# =============================================================================

SINGULARITY_EDGE_CASES = [
    # Removable singularities
    "limit((sin(x) - x + x**3/6) / x**5, x, 0)",  # -1/120
    "limit((exp(x) - 1 - x - x**2/2) / x**3, x, 0)",  # 1/6
    "limit((1 - cos(x)) / (x * sin(x)), x, 0)",  # 1/2
    "limit((arctan(x) - x + x**3/3) / x**5, x, 0)",  # 1/5
    "limit((sinh(x) - x) / (cosh(x) - 1 - x**2/2), x, 0)",  # 1/2

    # Essential singularities
    "limit(exp(-1/x**2) * x**(-100), x, 0, '+')",  # 0
    "limit(sin(1/x) * x, x, 0)",  # 0
    "limit(cos(1/x), x, 0)",  # does not exist
    "limit(exp(1/x) / exp(1/x**2), x, 0, '+')",  # 0
    "limit(x * sin(1/x) + x**2 * cos(1/x), x, 0)",  # 0

    # Branch point singularities
    "limit(sqrt(x**2 + 1) - abs(x), x, oo)",  # 0
    "limit(sqrt(x**2 + 1) - x, x, oo)",  # 0
    "limit(sqrt(x**2 + 1) - x, x, -oo)",  # does not exist as written
    "limit((sqrt(x**2 + x) - x), x, oo)",  # 1/2
    "limit((x + sqrt(x**2 - 1)) / (x - sqrt(x**2 - 1)), x, oo)",  # 1

    # Poles and asymptotic behavior
    "limit(tan(x) - sec(x), x, pi/2, '-')",  # 0
    "limit(cot(x) - csc(x), x, 0, '+')",  # 0
    "limit(1/sin(x) - 1/x, x, 0)",  # 0
    "limit((1/tan(x) - 1/x), x, 0)",  # 0
    "limit(x * (exp(1/x) - 1 - 1/x), x, oo)",  # 1/2
]

# =============================================================================
# INDETERMINATE FORMS AND L'HOPITAL STRESS TESTS (20 equations)
# =============================================================================

INDETERMINATE_EDGE_CASES = [
    # 0/0 requiring multiple applications
    "limit((exp(x) - exp(-x) - 2*x) / (x - sin(x)), x, 0)",  # 2
    "limit((x - tan(x)) / (x - sin(x)), x, 0)",  # -2
    "limit((tan(x) - sin(x)) / (sin(x) - x), x, 0)",  # -1
    "limit((1 - cos(x) * cos(2*x)) / x**2, x, 0)",  # 5/2
    "limit((exp(sin(x)) - exp(x)) / x**3, x, 0)",  # -1/6

    # oo - oo forms
    "limit(x - x * exp(1/x), x, oo)",  # -1
    "limit(x**2 * (sqrt(1 + 1/x) - 1 - 1/(2*x)), x, oo)",  # -1/8
    "limit(x * (pi/2 - arctan(x)), x, oo)",  # 1
    "limit(1/sin(x)**2 - 1/x**2, x, 0)",  # 1/3
    "limit(x * log(x) - (x-1) * log(x-1), x, 1)",  # 1

    # 0^0, oo^0, 1^oo forms
    "limit(x**(x**x), x, 0, '+')",  # 0
    "limit((1 + sin(x)/x)**(x**2), x, oo)",  # e^(1/2)
    "limit((cos(x))**(1/sin(x)**2), x, 0)",  # e^(-1/2)
    "limit((x/(x+1))**(x), x, oo)",  # 1/e
    "limit((1 + 1/x + 1/x**2)**(x**2), x, oo)",  # sqrt(e)

    # 0 * oo forms with oscillation
    "limit(x**n * exp(-x), x, oo)",  # 0 for all n
    "limit(log(x) / x**a, x, oo)",  # 0 for a > 0
    "limit(x**a * log(x), x, 0, '+')",  # 0 for a > 0
    "limit((1 - x) * tan(pi*x/2), x, 1, '-')",  # 2/pi
    "limit(sin(x) * log(sin(x)), x, 0, '+')",  # 0
]

# =============================================================================
# NUMERICAL PRECISION AND STABILITY EDGE CASES (15 equations)
# =============================================================================

NUMERICAL_EDGE_CASES = [
    # Near-cancellation issues
    "sqrt(1 + 1e-16) - 1",  # ~5e-17
    "(exp(1e-10) - 1) / 1e-10",  # ~1
    "log(1 + 1e-15) / 1e-15",  # ~1
    "sin(pi + 1e-14)",  # ~-1e-14
    "cos(pi/2 - 1e-14)",  # ~1e-14

    # Large/small number handling
    "factorial(170)",  # largest representable in float64
    "2**1024 - 1",  # near overflow
    "10**(-323)",  # near underflow
    "gamma(171.5)",  # very large
    "stirling_approx(1000)",  # asymptotic behavior

    # Rational approximation stress
    "rationalize(pi, 1e-10)",  # best rational approx
    "continued_fraction_convergent(e, 10)",  # 10th convergent
    "rationalize(sqrt(2), 1e-8)",  # ~577/408
    "rationalize(golden_ratio, 1e-6)",  # Fibonacci ratio
    "float_to_fraction(0.1)",  # exact binary representation
]

# =============================================================================
# PARSER AND TOKENIZER EDGE CASES (15 equations)
# =============================================================================

PARSER_EDGE_CASES = [
    # Operator precedence
    "2**3**2",  # = 512, not 64 (right associative)
    "-2**2",  # = -4, not 4
    "1/2/3",  # = 1/6, left associative
    "1 - 2 - 3",  # = -4, left associative
    "2 * 3 + 4 * 5",  # = 26

    # Parentheses and nesting
    "((((x))))",  # deep nesting
    "(a + b) * (c + d) * (e + f)",  # multiple groups
    "f(g(h(x)))",  # function nesting
    "sin(cos(tan(x)))",  # trig function nesting
    "log(log(log(x)))",  # iterated logs

    # Special character handling
    "x_1 + x_2 + x_3",  # subscripts
    "alpha + beta + gamma",  # Greek letters
    "x' + x''",  # primes
    "f^{(n)}(x)",  # notation variants
    "sum_{i=1}^{n} i",  # LaTeX-like notation
]

# =============================================================================
# SYMBOLIC SIMPLIFICATION TRAPS (15 equations)
# =============================================================================

SIMPLIFICATION_EDGE_CASES = [
    # Trig identities that may not simplify
    "sin(x)**2 + cos(x)**2 - 1",  # = 0
    "sin(2*x) - 2*sin(x)*cos(x)",  # = 0
    "cos(2*x) - cos(x)**2 + sin(x)**2",  # = 0
    "tan(x) - sin(x)/cos(x)",  # = 0
    "sin(x + y) - sin(x)*cos(y) - cos(x)*sin(y)",  # = 0

    # Log/exp simplifications
    "log(exp(x)) - x",  # = 0 (for real x)
    "exp(log(x)) - x",  # = x - x = 0 (for x > 0)
    "log(x*y) - log(x) - log(y)",  # = 0 (for x,y > 0)
    "log(x**n) - n*log(x)",  # = 0 (needs assumptions)
    "exp(a + b) - exp(a)*exp(b)",  # = 0

    # Algebraic simplifications
    "(x**2 - 1)/(x - 1) - (x + 1)",  # = 0 (for x != 1)
    "(x**3 - y**3)/(x - y) - (x**2 + x*y + y**2)",  # = 0
    "sqrt(x**2) - abs(x)",  # = 0
    "(sqrt(x) + sqrt(y))*(sqrt(x) - sqrt(y)) - (x - y)",  # = 0
    "((a + b)**2 - (a - b)**2) / (4*a*b) - 1",  # = 0
]

# =============================================================================
# MULTI-VALUED FUNCTION AND BRANCH CUT CASES (15 equations)
# =============================================================================

BRANCH_CUT_EDGE_CASES = [
    # Complex logarithm
    "log(-1)",  # I*pi (principal value)
    "log(-e)",  # 1 + I*pi
    "log(I)",  # I*pi/2
    "log(-I)",  # -I*pi/2
    "log(1 + I)",  # log(sqrt(2)) + I*pi/4

    # Complex powers
    "(-1)**(1/2)",  # I (principal root)
    "(-1)**(1/3)",  # -1 (real cube root) or complex
    "I**I",  # exp(-pi/2)
    "(-8)**(1/3)",  # -2 or 1 + I*sqrt(3)
    "(-1)**0.5",  # floating point handling

    # Inverse trig multi-valued
    "arcsin(2)",  # complex: pi/2 - I*log(2 + sqrt(3))
    "arccos(-2)",  # complex: pi + I*log(2 + sqrt(3))
    "arctan(I)",  # undefined (pole)
    "arcsin(sin(5*pi/4))",  # -pi/4, not 5*pi/4
    "arctan(tan(3*pi/4))",  # -pi/4, not 3*pi/4
]

# =============================================================================
# COMBINE ALL EDGE CASE EQUATIONS
# =============================================================================

ALL_EDGE_CASES = (
    SINGULARITY_EDGE_CASES +       # 20
    INDETERMINATE_EDGE_CASES +     # 20
    NUMERICAL_EDGE_CASES +         # 15
    PARSER_EDGE_CASES +            # 15
    SIMPLIFICATION_EDGE_CASES +    # 15
    BRANCH_CUT_EDGE_CASES          # 15
)  # Total: 100 equations

# Category mapping
CATEGORIES = {
    "singularity": SINGULARITY_EDGE_CASES,
    "indeterminate": INDETERMINATE_EDGE_CASES,
    "numerical": NUMERICAL_EDGE_CASES,
    "parser": PARSER_EDGE_CASES,
    "simplification": SIMPLIFICATION_EDGE_CASES,
    "branch_cut": BRANCH_CUT_EDGE_CASES,
}

# Difficulty rating for each category
DIFFICULTY_RATINGS = {
    "singularity": "high",
    "indeterminate": "high",
    "numerical": "medium",
    "parser": "low",
    "simplification": "medium",
    "branch_cut": "high",
}

def get_equations_by_category(category: str):
    """Get equations for a specific category."""
    return CATEGORIES.get(category, [])

def get_all_equations():
    """Get all edge case equations."""
    return ALL_EDGE_CASES

def get_difficulty_for_category(category: str):
    """Get difficulty rating for a category."""
    return DIFFICULTY_RATINGS.get(category, "unknown")
