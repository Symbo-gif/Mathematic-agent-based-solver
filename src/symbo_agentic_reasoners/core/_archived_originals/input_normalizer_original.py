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
INPUT NORMALIZER - Universal Math Expression Preprocessor
==========================================================

Converts ANY mathematical input format into a canonical SymPy-compatible form.

This module handles:
- Unicode symbols (Greek letters, superscripts, fractions, operators)
- LaTeX notation
- Natural language expressions
- Copy-paste artifacts (smart quotes, invisible chars, wrong dashes)
- Common typos and variations
- Multi-line input

Usage:
    from symbo_agentic_reasoners.core.input_normalizer import normalize_input

    clean = normalize_input("2πr² + ½×base×height")
    # Returns: "2*pi*r**2 + (1/2)*base*height"
"""

import re
import unicodedata
from typing import Tuple, Optional, List, Dict
import logging

logger = logging.getLogger('symbo_agentic_reasoners.input_normalizer')


# =============================================================================
# UNICODE CONVERSION MAPS
# =============================================================================

# Greek letters → SymPy names (with spaces to prevent tokenization issues)
GREEK_MAP = {
    # Lowercase Greek
    'π': ' pi ', 'α': ' alpha ', 'β': ' beta ', 'γ': ' gamma ', 'δ': ' delta ',
    'ε': ' epsilon ', 'ζ': ' zeta ', 'η': ' eta ', 'θ': ' theta ',
    'ι': ' iota ', 'κ': ' kappa ', 'λ': ' lambda ', 'μ': ' mu ',
    'ν': ' nu ', 'ξ': ' xi ', 'ο': ' omicron ', 'ρ': ' rho ',
    'σ': ' sigma ', 'τ': ' tau ', 'υ': ' upsilon ', 'φ': ' phi ',
    'χ': ' chi ', 'ψ': ' psi ', 'ω': ' omega ',
    # Uppercase Greek (commonly used in math)
    'Α': ' Alpha ', 'Β': ' Beta ', 'Γ': ' Gamma ', 'Δ': ' Delta ',
    'Ε': ' Epsilon ', 'Ζ': ' Zeta ', 'Η': ' Eta ', 'Θ': ' Theta ',
    'Ι': ' Iota ', 'Κ': ' Kappa ', 'Λ': ' Lambda ', 'Μ': ' Mu ',
    'Ν': ' Nu ', 'Ξ': ' Xi ', 'Ο': ' Omicron ', 'Π': ' Pi ',
    'Ρ': ' Rho ', 'Σ': ' Sum ', 'Τ': ' Tau ', 'Υ': ' Upsilon ',
    'Φ': ' Phi ', 'Χ': ' Chi ', 'Ψ': ' Psi ', 'Ω': ' Omega ',
}

# Special math symbols
SYMBOL_MAP = {
    '∞': ' oo ',       # infinity
    '√': 'sqrt',       # square root
    '∛': 'cbrt',       # cube root
    '∜': 'root4',      # fourth root
    '∂': ' Derivative ',  # partial derivative (better mapping)
    '∫': ' Integral ', # integral
    '∑': ' Sum ',      # summation
    '∏': ' Product ',  # product
    'ℯ': ' E ',        # Euler's number (script e)
    '℮': ' E ',        # Estimated symbol (looks like e)
    'ⅈ': ' I ',        # Imaginary unit
    'ⅉ': ' I ',        # Alternative imaginary unit
    'ℕ': ' Naturals ', # Natural numbers
    'ℤ': ' Integers ', # Integers
    'ℚ': ' Rationals ',# Rationals
    'ℝ': ' Reals ',    # Reals
    'ℂ': ' Complexes ',# Complex
    '∅': ' EmptySet ', # Empty set
    '∈': ' in ',       # Element of
    '∉': ' not in ',   # Not element of
    '⊂': ' subset ',   # Subset (proper)
    '⊆': ' subseteq ', # Subset or equal
    '⊃': ' superset ', # Superset
    '⊇': ' superseteq ',# Superset or equal
    '∪': ' union ',    # Union
    '∩': ' intersect ',# Intersection
    '∖': ' setminus ', # Set difference
    '¬': ' Not ',      # Logical not
    '∧': ' And ',      # Logical and
    '∨': ' Or ',       # Logical or
    '⇒': ' Implies ',  # Implies
    '→': ' -> ',       # Arrow (also implies)
    '⇔': ' Equivalent ',# If and only if
    '↔': ' <-> ',      # Bidirectional arrow
    '∀': ' ForAll ',   # For all
    '∃': ' Exists ',   # Exists
    '∄': ' NotExists ',# Does not exist
    '∴': ' therefore ',# Therefore
    '∵': ' because ',  # Because
    '≡': ' equiv ',    # Equivalent/congruent
    '≢': ' not_equiv ',# Not equivalent
    '∝': ' proportional ', # Proportional to
    '‖': ' parallel ', # Parallel
    '⊥': ' perp ',     # Perpendicular
    '∠': ' angle ',    # Angle
    '△': ' triangle ', # Triangle
    '□': ' square ',   # Square
    '○': ' circle ',   # Circle
    # Vector calculus operators
    '∇': ' gradient ', # Nabla/gradient operator
    '×': '*',          # Cross product (also multiplication)
    '·': '*',          # Dot product (also multiplication)
    # Approximation and comparison
    '≈': ' approx ',   # Approximately equal
    '≅': ' congruent ',# Congruent
    '≪': ' << ',       # Much less than
    '≫': ' >> ',       # Much greater than
    '≤': ' <= ',       # Less than or equal
    '≥': ' >= ',       # Greater than or equal
    '≠': ' != ',       # Not equal
}

# Unicode superscripts → **n
SUPERSCRIPT_MAP = {
    '⁰': '**0', '¹': '**1', '²': '**2', '³': '**3', '⁴': '**4',
    '⁵': '**5', '⁶': '**6', '⁷': '**7', '⁸': '**8', '⁹': '**9',
    'ⁿ': '**n', 'ⁱ': '**i', 'ˣ': '**x', 'ʸ': '**y',
    '⁺': '+', '⁻': '-', '⁼': '=', '⁽': '(', '⁾': ')',
}

# Unicode subscripts → regular (for variable names like x₁ → x1)
SUBSCRIPT_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')',
    'ₐ': 'a', 'ₑ': 'e', 'ₒ': 'o', 'ₓ': 'x', 'ₕ': 'h',
    'ₖ': 'k', 'ₗ': 'l', 'ₘ': 'm', 'ₙ': 'n', 'ₚ': 'p',
    'ₛ': 's', 'ₜ': 't',
}

# Unicode fractions → rational expressions
FRACTION_MAP = {
    '½': '(1/2)', '⅓': '(1/3)', '¼': '(1/4)', '⅕': '(1/5)',
    '⅙': '(1/6)', '⅐': '(1/7)', '⅛': '(1/8)', '⅑': '(1/9)', '⅒': '(1/10)',
    '⅔': '(2/3)', '⅖': '(2/5)', '⅗': '(3/5)', '¾': '(3/4)',
    '⅘': '(4/5)', '⅚': '(5/6)', '⅜': '(3/8)', '⅝': '(5/8)', '⅞': '(7/8)',
    '⅟': '1/',  # Fraction numerator one
}

# Unicode operators → ASCII equivalents
OPERATOR_MAP = {
    # Multiplication
    '×': '*', '⋅': '*', '·': '*', '∗': '*', '✕': '*', '✖': '*',
    # Division
    '÷': '/', '∕': '/', '⁄': '/',
    # Plus/minus
    '±': '+/-', '∓': '-/+', '＋': '+', '－': '-',
    # Comparison
    '≤': '<=', '≥': '>=', '≠': '!=', '≈': '~=', '≅': '~=',
    '≪': '<<', '≫': '>>', '≲': '<=', '≳': '>=',
    # Arrows (for limits, mappings)
    '→': '->', '←': '<-', '↔': '<->', '⟶': '->', '⟵': '<-',
    '↦': '|->', '⟼': '|->',
    # Other
    '′': "'", '″': "''", '‴': "'''",  # Primes
    '°': ' degrees ',  # Degree
    '…': '...',  # Ellipsis
    '⋮': '...',  # Vertical ellipsis
    '⋯': '...',  # Horizontal ellipsis
}

# All types of dashes/minuses → regular hyphen-minus
DASH_CHARS = [
    '−',  # U+2212 MINUS SIGN
    '–',  # U+2013 EN DASH
    '—',  # U+2014 EM DASH
    '‒',  # U+2012 FIGURE DASH
    '―',  # U+2015 HORIZONTAL BAR
    '⁻',  # U+207B SUPERSCRIPT MINUS
    '₋',  # U+208B SUBSCRIPT MINUS
    '﹣', # U+FE63 SMALL HYPHEN-MINUS
    '－', # U+FF0D FULLWIDTH HYPHEN-MINUS
]

# Smart quotes → straight quotes
QUOTE_MAP = {
    '"': '"', '"': '"',  # Double curly quotes
    ''': "'", ''': "'",  # Single curly quotes
    '«': '"', '»': '"',  # Guillemets
    '‹': "'", '›': "'",  # Single guillemets
    '`': "'",            # Backtick
    '´': "'",            # Acute accent
}

# Invisible/problematic whitespace characters → space
INVISIBLE_CHARS = [
    '\u00a0',  # Non-breaking space
    '\u200b',  # Zero-width space
    '\u200c',  # Zero-width non-joiner
    '\u200d',  # Zero-width joiner
    '\ufeff',  # BOM / zero-width no-break space
    '\u2060',  # Word joiner
    '\u2028',  # Line separator
    '\u2029',  # Paragraph separator
    '\u202f',  # Narrow no-break space
    '\u205f',  # Medium mathematical space
    '\u3000',  # Ideographic space
    '\t',      # Tab → space
]


# =============================================================================
# COMMAND UNWRAPPING PATTERNS
# =============================================================================

# These patterns detect "solve(...)", "dsolve(...)", "grad(...)", etc.
# and restructure them for proper routing through the system.
# The key insight is that these are META-COMMANDS, not expressions.

# Command patterns: command(args) -> structured form
COMMAND_PATTERNS = {
    # solve(expr = 0, x) or solve(expr, x) -> solve equation for x
    'solve': re.compile(
        r'\bsolve\s*\(\s*(.+?)\s*,\s*(\w+)\s*(?:,\s*domain\s*=\s*(\w+))?\s*\)',
        re.IGNORECASE
    ),
    # solve([eq1, eq2, ...], [x, y, ...]) -> solve system of equations
    'solve_system': re.compile(
        r'\bsolve\s*\(\s*\[([^\]]+)\]\s*,\s*\[([^\]]+)\]\s*\)',
        re.IGNORECASE
    ),
    # dsolve(ode, y(x)) -> solve differential equation
    'dsolve': re.compile(
        r'\bdsolve\s*\(\s*(.+?)\s*,\s*(\w+)\s*\(\s*(\w+)\s*\)\s*\)',
        re.IGNORECASE
    ),
    # grad(f, [x, y]) or grad(f, [x, y, z]) -> gradient vector
    'grad': re.compile(
        r'\bgrad\s*\(\s*(.+?)\s*,\s*\[\s*(.+?)\s*\]\s*\)',
        re.IGNORECASE
    ),
    # grad(f) - simple form without explicit variable list (infer from expression)
    'grad_simple': re.compile(
        r'\bgrad(?:ient)?\s*\(\s*([^,\[\]]+?)\s*\)',
        re.IGNORECASE
    ),
    # gradient of f - natural language form
    'gradient_natural': re.compile(
        r'\bgradient\s+(?:of\s+)?(.+)',
        re.IGNORECASE
    ),
    # grad f - space-separated form
    'grad_space': re.compile(
        r'\bgrad\s+([^\[\]\(\)]+)',
        re.IGNORECASE
    ),
    # div([Fx, Fy, Fz], [x, y, z]) -> divergence
    'div': re.compile(
        r'\bdiv\s*\(\s*\[\s*(.+?)\s*\]\s*(?:,\s*\[\s*(.+?)\s*\])?\s*\)',
        re.IGNORECASE
    ),
    # curl([Fx, Fy, Fz], [x, y, z]) -> curl vector
    'curl': re.compile(
        r'\bcurl\s*\(\s*\[\s*(.+?)\s*\]\s*,\s*\[\s*(.+?)\s*\]\s*\)',
        re.IGNORECASE
    ),
    # diophantine(equation) -> solve for integer solutions
    'diophantine': re.compile(
        r'\bdiophantine\s*\(\s*(.+?)\s*\)',
        re.IGNORECASE
    ),
    # det(matrix) -> determinant
    'det': re.compile(
        r'\bdet\s*\(\s*(.+?)\s*\)',
        re.IGNORECASE
    ),
    # limit(expr, var, point) -> limit evaluation
    'limit': re.compile(
        r'\blimit\s*\(\s*(.+?)\s*,\s*(\w+)\s*,\s*([^)]+)\s*\)',
        re.IGNORECASE
    ),
}


# =============================================================================
# IMPLICIT MULTIPLICATION RECOVERY PATTERNS
# =============================================================================

# Patterns for detecting missing * in common cases
# These need to be applied carefully to avoid breaking function calls

# letter immediately followed by known function (no space) -> add *
# e.g., sigmasqrt(2pi) -> sigma*sqrt(2*pi)
# IMPORTANT: Must NOT match function prefixes like arc- in arctan, bi- in binomial, etc.
IMPLICIT_MUL_BEFORE_FUNC = [
    # Greek letters followed by function names: sigmasqrt -> sigma*sqrt, etc.
    (r'(sigma|alpha|beta|gamma|delta|epsilon|theta|phi|psi|omega|lambda|mu|tau|rho|nu|kappa)(sqrt|sin|cos|tan|exp|log|ln)\(', r'\1*\2('),
    # sigma followed by sqrt, sin, cos, etc.
    # Use negative lookbehind to avoid breaking function names
    (r'(?<![a-zA-Z])(\w)(?=sqrt\()', r'\1*'),  # Avoid single letter that's part of longer name
    (r'(?<!arc)(\w)(?=sin\()', r'\1*'),  # Avoid arcsin
    (r'(?<!arc)(\w)(?=cos\()', r'\1*'),  # Avoid arccos
    (r'(?<!arc)(\w)(?=tan\()', r'\1*'),  # Avoid arctan
    (r'(?<![a-zA-Z])(\w)(?=exp\()', r'\1*'),  # Avoid ...exp
    (r'(?<![a-zA-Z])(\w)(?=log\()', r'\1*'),  # Avoid ...log
    (r'(?<![a-zA-Z])(\w)(?=ln\()', r'\1*'),  # Avoid ...ln
]

# Function names that should NOT have * inserted before their parenthesis
# This is used in preprocess_function_notation() to protect function calls
PROTECTED_FUNCTIONS = {
    # Trig and inverse trig
    'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
    'arcsin', 'arccos', 'arctan', 'arcsec', 'arccsc', 'arccot',
    'asin', 'acos', 'atan', 'asec', 'acsc', 'acot',
    'sinh', 'cosh', 'tanh', 'sech', 'csch', 'coth',
    'arcsinh', 'arccosh', 'arctanh', 'arcsech', 'arccsch', 'arccoth',
    'asinh', 'acosh', 'atanh', 'asech', 'acsch', 'acoth',
    # Other functions
    'sqrt', 'cbrt', 'root', 'log', 'ln', 'exp', 'abs', 'Abs',
    # Special functions
    'Gamma', 'gamma', 'Beta', 'beta', 'psi', 'zeta', 'erf', 'erfc',
    'binomial', 'factorial', 'product', 'Product', 'sum', 'Sum',
    'digamma', 'polygamma', 'Ei', 'Si', 'Ci', 'li', 'Li',
    # Bessel and Airy functions
    'BesselJ', 'BesselY', 'BesselI', 'BesselK', 'besselj', 'bessely', 'besseli', 'besselk',
    'AiryAi', 'AiryBi', 'airyai', 'airybi', 'Ai', 'Bi',
    'hankel1', 'hankel2', 'jn', 'yn', 'spherical_jn', 'spherical_yn',
    # Other special functions
    'polylog', 'lerchphi', 'dirichlet_eta', 'Lambda', 'mu', 'phi', 'totient',
    'hermite', 'laguerre', 'legendre', 'chebyshev', 'jacobi',
    'H_n', 'M_X', 'P', 'E', 'Var', 'Cov', 'Phi',
    # Linear algebra
    'det', 'trace', 'rank', 'norm', 'eigenvals', 'eigenvects',
    'inverse', 'transpose', 'adjugate', 'diag', 'Matrix',
    # Calculus commands
    'diff', 'Derivative', 'integrate', 'Integral', 'limit', 'Limit',
    'solve', 'dsolve', 'nsolve', 'solveset',
    # Other math
    'gcd', 'lcm', 'Mod', 'floor', 'ceiling', 'round',
    'simplify', 'expand', 'factor', 'cancel', 'apart', 'together',
    # Distributions
    'Normal', 'Binomial', 'Poisson', 'Uniform', 'Exponential',
    # Physics
    'harmonic', 'HarmonicNumber',
}

# Number followed by identifier (coefficient) -> add *
# e.g., 2sigma^2 -> 2*sigma**2, 2pi -> 2*pi
IMPLICIT_MUL_COEFF = [
    # Number followed by Greek letter name
    (r'(\d)\s*(pi|alpha|beta|gamma|delta|epsilon|sigma|theta|phi|mu|omega|lambda|tau|rho|nu|kappa)\b', r'\1*\2'),
    # Number followed by letter (generic)
    (r'(\d)([a-zA-Z])', r'\1*\2'),
]

# Letter followed by Greek letter name -> add *
# e.g., momega -> m*omega, ksigma -> k*sigma
IMPLICIT_MUL_GREEK = [
    (r'\b([a-zA-Z])(?=(pi|alpha|beta|gamma|delta|epsilon|sigma|theta|phi|mu|omega|lambda|tau|rho|nu|kappa)\b)', r'\1*'),
]

# Variable followed by power digit -> exponent notation
# e.g., x2 -> x**2, y3 -> y**3, r2 -> r**2, R2 -> R**2, x4 -> x**4
# Applied AFTER function prefix patterns to get proper breaks
IMPLICIT_POWER_PATTERNS = [
    # Chained powers FIRST: x2y2 -> x**2*y**2, x2y2z2 -> x**2*y**2*z**2
    # Handle triple chain directly
    (r'\b([a-zA-Z])([2-9])([a-zA-Z])([2-9])([a-zA-Z])([2-9])\b', r'\1**\2*\3**\4*\5**\6'),
    # Handle double chain directly
    (r'\b([a-zA-Z])([2-9])([a-zA-Z])([2-9])\b', r'\1**\2*\3**\4'),
    # Coefficient-variable-power: ax2 -> a*x**2, by3 -> b*y**3
    # Extended to include uppercase and more digits (2-9)
    (r'([a-wA-W])([xyztrsuXYZTRSU])([2-9])(?![a-zA-Z0-9])', r'\1*\2**\3'),
    # Single variable followed by power digit: x2 -> x**2, R2 -> R**2
    # Extended to digits 2-9 for common power notation
    (r'\b([a-zA-Z])([2-9])(?![a-zA-Z0-9])', r'\1**\2'),
    # Handle cases like -ax2 -> -a*x**2 (negative coefficient)
    (r'(-[a-wA-W])([xyztrsuXYZTRSU])([2-9])(?![a-zA-Z0-9])', r'\1*\2**\3'),
    # Continuation pattern: **2y2 -> **2*y**2 (after partial conversion)
    (r'(\*\*[2-9])([a-zA-Z])([2-9])(?![a-zA-Z0-9])', r'\1*\2**\3'),
]


# =============================================================================
# MULTI-EXPRESSION SPLITTING
# =============================================================================

def split_multi_expressions(text: str) -> List[str]:
    """
    Split comma-separated expressions into individual problems.

    Handles cases like:
        "∫ x^2 dx, integrate x^2 dx, integrate(x^2, x)"
        -> ["∫ x^2 dx", "integrate x^2 dx", "integrate(x^2, x)"]

    Smart enough to NOT split inside function calls like integrate(x, (x, 0, 1))
    """
    if ',' not in text:
        return [text]

    # Track parentheses depth to avoid splitting inside function calls
    expressions = []
    current = []
    depth = 0

    for char in text:
        if char == '(':
            depth += 1
            current.append(char)
        elif char == ')':
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            # Top-level comma - split here
            expr = ''.join(current).strip()
            if expr:
                expressions.append(expr)
            current = []
        else:
            current.append(char)

    # Don't forget the last expression
    expr = ''.join(current).strip()
    if expr:
        expressions.append(expr)

    return expressions if expressions else [text]


def detect_multiple_problems(text: str) -> List[str]:
    """
    Detect and split multiple separate mathematical problems in input.

    Handles various input formats:
    - Newline-separated problems
    - Numbered lists (1. problem, 2. problem)
    - Bullet points (- problem, * problem, • problem)
    - Semicolon-separated problems
    - Comma-separated problems (delegates to split_multi_expressions)
    - Natural language separators ("and", "also", "then")

    Args:
        text: Input text possibly containing multiple problems

    Returns:
        List of individual problem strings

    Examples:
        "1. solve x^2 - 4 = 0\n2. integrate x dx"
        -> ["solve x^2 - 4 = 0", "integrate x dx"]

        "diff(sin(x), x); integrate(cos(x), x)"
        -> ["diff(sin(x), x)", "integrate(cos(x), x)"]

        "- find derivative of x^2\n- find integral of x"
        -> ["find derivative of x^2", "find integral of x"]
    """
    problems = []

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Step 1: Check for numbered list format (1. problem, 2. problem, etc.)
    numbered_pattern = r'(?:^|\n)\s*(\d+)\.\s*(.+?)(?=(?:\n\s*\d+\.|\n\n|\Z))'
    numbered_matches = re.findall(numbered_pattern, text, re.DOTALL)
    if len(numbered_matches) >= 2:
        # We have a numbered list with at least 2 items
        for _, problem in numbered_matches:
            clean_problem = problem.strip()
            if clean_problem:
                problems.append(clean_problem)
        return problems

    # Step 2: Check for bullet point format (-, *, •, ◦)
    bullet_pattern = r'(?:^|\n)\s*[-*•◦]\s*(.+?)(?=(?:\n\s*[-*•◦]|\n\n|\Z))'
    bullet_matches = re.findall(bullet_pattern, text, re.DOTALL)
    if len(bullet_matches) >= 2:
        for problem in bullet_matches:
            clean_problem = problem.strip()
            if clean_problem:
                problems.append(clean_problem)
        return problems

    # Step 3: Check for semicolon-separated problems (respecting parentheses)
    if ';' in text:
        semicolon_problems = _split_respecting_parens(text, ';')
        if len(semicolon_problems) >= 2:
            for problem in semicolon_problems:
                clean_problem = problem.strip()
                if clean_problem:
                    problems.append(clean_problem)
            return problems

    # Step 4: Check for newline-separated problems
    # Only split on newlines if each line looks like a complete mathematical expression
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    if len(non_empty_lines) >= 2:
        # Check if each line looks like a standalone math problem
        math_indicators = [
            r'\bintegrate\b', r'\bdiff\b', r'\bsolve\b', r'\blimit\b', r'\bsum\b',
            r'\bsimplify\b', r'\bfactor\b', r'\bexpand\b', r'\bevaluate\b',
            r'[∫∑∏∂∇]',  # Math symbols
            r'=',  # Equations
            r'\bwhat\s+is\b',  # Natural language queries
            r'\bfind\b', r'\bcalculate\b', r'\bcompute\b',
        ]

        all_look_like_problems = True
        for line in non_empty_lines:
            is_math_problem = any(re.search(pattern, line, re.IGNORECASE)
                                  for pattern in math_indicators)
            # Also accept if it's a pure mathematical expression
            is_math_expr = bool(re.match(r'^[\d\w\s\+\-\*/\^().\[\],=<>!]+$', line))
            if not (is_math_problem or is_math_expr):
                all_look_like_problems = False
                break

        if all_look_like_problems:
            return non_empty_lines

    # Step 5: Check for natural language separators
    # "solve x^2 = 4 and also find the derivative of x^3"
    nl_separators = [
        r'\s+and\s+(?:also\s+)?(?:then\s+)?',
        r'\s+then\s+',
        r'\s+also\s+',
        r'\.\s+(?:Also|Then|Next|Now)\s+',
    ]

    for separator in nl_separators:
        parts = re.split(separator, text, flags=re.IGNORECASE)
        if len(parts) >= 2:
            # Verify each part looks like a math problem
            valid_parts = []
            for part in parts:
                clean_part = part.strip().rstrip('.')
                if clean_part and len(clean_part) > 3:  # Avoid tiny fragments
                    valid_parts.append(clean_part)
            if len(valid_parts) >= 2:
                return valid_parts

    # Step 6: Fall back to comma-separated splitting
    comma_split = split_multi_expressions(text)
    if len(comma_split) >= 2:
        return comma_split

    # No multiple problems detected - return original as single item
    return [text.strip()]


def _split_respecting_parens(text: str, delimiter: str) -> List[str]:
    """
    Split text on delimiter while respecting parentheses/brackets.

    Args:
        text: Input text
        delimiter: Character to split on (e.g., ';' or ',')

    Returns:
        List of split segments
    """
    segments = []
    current = []
    depth = 0

    for char in text:
        if char in '([{':
            depth += 1
            current.append(char)
        elif char in ')]}':
            depth -= 1
            current.append(char)
        elif char == delimiter and depth == 0:
            segment = ''.join(current).strip()
            if segment:
                segments.append(segment)
            current = []
        else:
            current.append(char)

    # Don't forget the last segment
    segment = ''.join(current).strip()
    if segment:
        segments.append(segment)

    return segments if segments else [text]


def get_problem_count(text: str) -> int:
    """
    Get the number of separate problems detected in input.

    Useful for determining if multi-problem handling is needed.

    Args:
        text: Input text

    Returns:
        Number of detected problems
    """
    problems = detect_multiple_problems(text)
    return len(problems)


# =============================================================================
# EQUATION NORMALIZATION
# =============================================================================

def normalize_equation_equals(text: str) -> str:
    """
    Convert single = to Eq() format for equation contexts.

    This helps SymPy parse equations properly:
        x^2 - 4 = 0 -> Eq(x**2 - 4, 0)
        x + y = 5 -> Eq(x + y, 5)

    Only applies when the = appears to be an equation, not assignment.
    """
    # Check if this looks like an equation (has = but not ==, <=, >=, !=)
    if '=' not in text:
        return text

    # Already has ==, <=, >=, != - leave alone
    if '==' in text or '<=' in text or '>=' in text or '!=' in text:
        return text

    # Check if it's inside a solve() or similar command - handle differently
    if re.search(r'\b(solve|dsolve)\s*\(', text, re.IGNORECASE):
        # Inside solve context - convert = to ==
        # But only the equation part, not the whole thing
        # This is complex - for now, just replace = with == conservatively
        pass

    # Simple case: expr = expr -> Eq(expr, expr)
    match = re.match(r'^(.+?)\s*=\s*(.+)$', text)
    if match:
        lhs, rhs = match.groups()
        # Don't convert if lhs looks like a function definition
        if not re.match(r'^\w+\s*\(', lhs):
            return f'Eq({lhs.strip()}, {rhs.strip()})'

    return text


# =============================================================================
# VECTOR CALCULUS EXPANSION
# =============================================================================

def expand_vector_calculus(text: str) -> str:
    """
    Expand vector calculus operators to derivative expressions.

    grad(f, [x, y]) -> [diff(f, x), diff(f, y)]
    div([P, Q], [x, y]) -> diff(P, x) + diff(Q, y)
    curl([P, Q, R], [x, y, z]) -> [diff(R,y)-diff(Q,z), diff(P,z)-diff(R,x), diff(Q,x)-diff(P,y)]
    """
    result = text

    # Gradient: grad(f, [x, y, z]) -> [diff(f, x), diff(f, y), diff(f, z)]
    grad_match = COMMAND_PATTERNS['grad'].search(result)
    if grad_match:
        func = grad_match.group(1).strip()
        vars_str = grad_match.group(2).strip()
        variables = [v.strip() for v in vars_str.split(',')]
        grad_components = [f'diff({func}, {v})' for v in variables]
        grad_expr = '[' + ', '.join(grad_components) + ']'
        result = result[:grad_match.start()] + grad_expr + result[grad_match.end():]

    # Divergence: div([P, Q, R], [x, y, z]) -> diff(P, x) + diff(Q, y) + diff(R, z)
    div_match = COMMAND_PATTERNS['div'].search(result)
    if div_match:
        components_str = div_match.group(1).strip()
        vars_str = div_match.group(2)
        components = [c.strip() for c in components_str.split(',')]

        if vars_str:
            variables = [v.strip() for v in vars_str.split(',')]
        else:
            # Default variables x, y, z based on component count
            default_vars = ['x', 'y', 'z']
            variables = default_vars[:len(components)]

        div_terms = [f'diff({c}, {v})' for c, v in zip(components, variables)]
        div_expr = ' + '.join(div_terms)
        result = result[:div_match.start()] + div_expr + result[div_match.end():]

    # Curl: curl([P, Q, R], [x, y, z]) -> vector cross product with nabla
    curl_match = COMMAND_PATTERNS['curl'].search(result)
    if curl_match:
        components_str = curl_match.group(1).strip()
        vars_str = curl_match.group(2).strip()
        components = [c.strip() for c in components_str.split(',')]
        variables = [v.strip() for v in vars_str.split(',')]

        if len(components) == 3 and len(variables) == 3:
            P, Q, R = components
            x, y, z = variables
            curl_components = [
                f'diff({R}, {y}) - diff({Q}, {z})',
                f'diff({P}, {z}) - diff({R}, {x})',
                f'diff({Q}, {x}) - diff({P}, {y})'
            ]
            curl_expr = '[' + ', '.join(curl_components) + ']'
            result = result[:curl_match.start()] + curl_expr + result[curl_match.end():]

    return result


def unwrap_solve_command(text: str) -> Tuple[str, Optional[Dict]]:
    """
    Detect and unwrap solve() command syntax.

    Returns:
        (modified_text, metadata) where metadata contains:
        - 'command': 'solve'
        - 'equation': the equation to solve
        - 'variable': the variable to solve for
        - 'domain': optional domain constraint

    If no solve command found, returns (text, None)
    """
    solve_match = COMMAND_PATTERNS['solve'].search(text)
    if not solve_match:
        return text, None

    equation = solve_match.group(1).strip()
    variable = solve_match.group(2).strip()
    domain = solve_match.group(3)

    # Normalize equation (convert = to == if needed)
    if '=' in equation and '==' not in equation:
        equation = equation.replace('=', '==')

    metadata = {
        'command': 'solve',
        'equation': equation,
        'variable': variable,
        'domain': domain.strip() if domain else None,
        'original': text
    }

    # Return just the equation for processing
    return equation, metadata


# =============================================================================
# ENHANCED IMPLICIT MULTIPLICATION
# =============================================================================

def enhanced_implicit_multiplication(text: str) -> str:
    """
    More aggressive implicit multiplication insertion.

    Handles cases like:
        sigmasqrt(2pi) -> sigma*sqrt(2*pi)
        2sigma^2 -> 2*sigma**2
        xy -> x*y (when not a function name)
        x2 -> x**2 (variable followed by power digit)
        ax2 -> a*x**2 (coefficient-variable-power)
        R2 -> R**2, x4 -> x**4 (extended digits)
        momega -> m*omega (letter before Greek)
        x2y2 -> x**2*y**2 (chained powers)
    """
    result = text

    # Apply function prefix patterns FIRST: 2exp( -> 2*exp(, xexp( -> x*exp(
    # This creates breaks that allow power patterns to work correctly
    for pattern, replacement in IMPLICIT_MUL_BEFORE_FUNC:
        result = re.sub(pattern, replacement, result)

    # Apply Greek letter patterns: momega -> m*omega
    for pattern, replacement in IMPLICIT_MUL_GREEK:
        result = re.sub(pattern, replacement, result)

    # Apply power patterns iteratively to handle chained cases like x2y2
    # First pass: x2y2 -> x**2y2
    # Second pass: x**2y2 -> x**2*y**2
    for _ in range(3):  # Up to 3 iterations for deeply chained patterns
        prev = result
        for pattern, replacement in IMPLICIT_POWER_PATTERNS:
            result = re.sub(pattern, replacement, result)
        if result == prev:
            break  # No more changes

    # Apply coefficient patterns: 2sigma -> 2*sigma, 3x -> 3*x
    for pattern, replacement in IMPLICIT_MUL_COEFF:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Apply power patterns AGAIN after coefficient insertion
    # This handles cases like 3x2 -> 3*x2 -> 3*x**2
    for _ in range(2):
        prev = result
        for pattern, replacement in IMPLICIT_POWER_PATTERNS:
            result = re.sub(pattern, replacement, result)
        if result == prev:
            break

    # Adjacent identifiers that aren't known functions -> add *
    # e.g., "xy" -> "x*y" but "sin" stays "sin"
    known_functions = {
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
        'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh',
        'sqrt', 'cbrt', 'log', 'ln', 'exp', 'abs', 'Abs',
        'diff', 'integrate', 'limit', 'solve', 'factor', 'expand',
        'simplify', 'Sum', 'Product', 'Mod', 'gcd', 'lcm',
        'pi', 'alpha', 'beta', 'gamma', 'delta', 'epsilon',
        'sigma', 'theta', 'phi', 'mu', 'omega', 'lambda', 'tau',
        'det', 'trace', 'rank', 'norm', 'grad', 'div', 'curl',
        'Normal', 'Binomial', 'Poisson', 'pdf', 'cdf',
    }

    # This is conservative - only split 2-char sequences that aren't functions
    def add_mul_between_letters(match):
        seq = match.group(0)
        if seq.lower() in known_functions:
            return seq
        # Insert * between each letter
        return '*'.join(seq)

    # Only for 2-letter sequences that aren't functions
    # result = re.sub(r'\b([a-zA-Z])([a-zA-Z])\b(?!\s*\()', add_mul_between_letters, result)

    return result


def remove_spurious_multiplication(text: str) -> str:
    """
    Remove spurious * inserted before protected function names.

    This fixes cases where implicit multiplication broke function names:
    - binomial*(2*n, n) -> binomial(2*n, n)
    - zeta*(1 + 1/n) -> zeta(1 + 1/n)
    - arc*tan(x) -> arctan(x)
    - a*tan(x) -> atan(x) (when atan was original function)

    Must be called AFTER enhanced_implicit_multiplication.
    """
    result = text

    # Fix function*( -> function(
    for func in PROTECTED_FUNCTIONS:
        # Pattern: func*( -> func(
        pattern = rf'\b{func}\s*\*\s*\('
        replacement = f'{func}('
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Special case: arc*tan, arc*sin, arc*cos -> arctan, arcsin, arccos
    # This is the most common case where implicit multiplication breaks function names
    result = re.sub(r'\barc\s*\*\s*(sin|cos|tan|sec|csc|cot)(h?)\s*\(', r'arc\1\2(', result)

    # Fix a*tan, a*sin, a*cos -> atan, asin, acos
    # These are inverse trig functions that got split by implicit multiplication
    # We need to be careful - only fix when at word boundary (not like "ma*tan(x)")
    result = re.sub(r'(?<![a-zA-Z])a\s*\*\s*(sin|cos|tan|sec|csc|cot)(h?)\s*\(', r'a\1\2(', result)

    # Fix A*tan, A*sin, A*cos (uppercase)
    result = re.sub(r'(?<![a-zA-Z])A\s*\*\s*(sin|cos|tan|sec|csc|cot)(h?)\s*\(', r'A\1\2(', result)

    # Also fix a*tan when it should be arctan (at start of word)
    # Pattern: after non-letter or start, ar followed by c*tan -> arctan
    result = re.sub(r'(^|[^a-zA-Z])ar(c\s*\*\s*)(sin|cos|tan|sec|csc|cot)(h?)\s*\(', r'\1arc\3\4(', result)

    # Fix standalone arc*trig patterns that got split
    result = re.sub(r'\bArc\s*\*\s*(sin|cos|tan|sec|csc|cot)(h?)\s*\(', r'Arc\1\2(', result)

    # Fix ODE function notation inside diff() calls
    # Pattern: diff(y*(x), ...) -> diff(y(x), ...)
    # This handles the case where implicit multiplication incorrectly converts y(x) to y*(x)
    # in ODE prime notation conversions
    result = re.sub(r'diff\(([a-zA-Z])\s*\*\s*\(([a-zA-Z])\)', r'diff(\1(\2)', result)

    # Also fix in higher-order derivatives: diff(y*(x), x, 2) -> diff(y(x), x, 2)
    result = re.sub(r'diff\(([a-zA-Z])\s*\*\s*\(([a-zA-Z])\),', r'diff(\1(\2),', result)

    return result


# =============================================================================
# MODULAR ARITHMETIC PATTERNS
# =============================================================================

# These patterns convert congruence notation to SymPy Mod() calls
# Must be applied BEFORE implicit multiplication to avoid mangling "mod"
MODULAR_PATTERNS = [
    # a ≡ b (mod n) → Mod(a, n) - Mod(b, n) or congruence check
    # We convert to a format the number theory specialist can understand

    # Pattern: a≡b(mod n) or a≡b(modn) - with Unicode ≡
    (r'(\w+)\s*≡\s*(\w+)\s*\(\s*mod\s*(\w+)\s*\)', r'Mod(\1, \3) == Mod(\2, \3)'),

    # Pattern: a equiv b (mod n) - after ≡ is converted to equiv
    (r'(\w+)\s+equiv\s+(\w+)\s*\(\s*mod\s*(\w+)\s*\)', r'Mod(\1, \3) == Mod(\2, \3)'),

    # Pattern: a ≡ b mod n (without parentheses)
    (r'(\w+)\s*≡\s*(\w+)\s+mod\s+(\w+)', r'Mod(\1, \3) == Mod(\2, \3)'),

    # Pattern: a equiv b mod n
    (r'(\w+)\s+equiv\s+(\w+)\s+mod\s+(\w+)', r'Mod(\1, \3) == Mod(\2, \3)'),

    # Simple modulo: a mod n → Mod(a, n)
    (r'\b(\w+)\s+mod\s+(\w+)\b', r'Mod(\1, \2)'),

    # a (mod n) → Mod(a, n)
    (r'(\w+)\s*\(\s*mod\s*(\w+)\s*\)', r'Mod(\1, \2)'),
]


# =============================================================================
# NATURAL LANGUAGE PATTERNS
# =============================================================================

# Common word patterns → math expressions
WORD_PATTERNS = [
    # Powers
    (r'\bsquared\b', '**2'),
    (r'\bcubed\b', '**3'),
    (r'\bto the power of\s+(\d+)\b', r'**\1'),
    (r'\bto the (\d+)(?:st|nd|rd|th)?\s+power\b', r'**\1'),
    (r'\braised to\s+(\d+)\b', r'**\1'),

    # Roots (with optional "the")
    (r'\b(?:the\s+)?square root of\b', 'sqrt('),
    (r'\b(?:the\s+)?sqrt of\b', 'sqrt('),
    (r'\b(?:the\s+)?cube root of\b', 'cbrt('),
    (r'\b(?:the\s+)?(\d+)(?:st|nd|rd|th)? root of\b', r'root(\1,'),

    # Operations in words
    (r'\bplus\b', '+'),
    (r'\bminus\b', '-'),
    (r'\btimes\b', '*'),
    (r'\bmultiplied by\b', '*'),
    (r'\bdivided by\b', '/'),
    (r'\bover\b', '/'),
    # Note: Don't convert Mod (capital M) - that's the SymPy function
    # Only convert lowercase 'mod' when it's not followed by (
    (r'\bmod\b(?!\s*\()', '%'),
    (r'\bmodulo\b', '%'),

    # Equals
    (r'\bequals?\b', '='),
    (r'\bis equal to\b', '='),

    # Trig functions with degrees
    (r'\bsin(?:e)?\s+of\b', 'sin('),
    (r'\bcos(?:ine)?\s+of\b', 'cos('),
    (r'\btan(?:gent)?\s+of\b', 'tan('),

    # Logarithms
    (r'\blog base\s+(\d+)\s+of\b', r'log(\1,'),
    (r'\bnatural log(?:arithm)?\s+of\b', 'ln('),
    (r'\bln\s+of\b', 'ln('),
    (r'\blog\s+of\b', 'log('),

    # Absolute value
    (r'\babsolute value of\b', 'Abs('),
    (r'\babs\s+of\b', 'Abs('),

    # Factorial - keep factorial() as valid SymPy syntax
    # Only convert "n factorial" or "factorial of n" natural language patterns
    (r'(\d+)\s+factorial\b', r'factorial(\1)'),
    (r'\bfactorial\s+of\s+(\w+)\b', r'factorial(\1)'),

    # Fractions
    (r'\bone half\b', '(1/2)'),
    (r'\bone third\b', '(1/3)'),
    (r'\bone fourth\b', '(1/4)'),
    (r'\bone quarter\b', '(1/4)'),
    (r'\btwo thirds?\b', '(2/3)'),
    (r'\bthree fourths?\b', '(3/4)'),
    (r'\bthree quarters?\b', '(3/4)'),

    # Constants
    (r'\beuler\'?s?\s+number\b', ' E '),
    (r'\bpi\b', ' pi '),
    (r'\binfinity\b', ' oo '),
    (r'\binf\b', ' oo '),
]

# Function name variations → canonical names
FUNCTION_ALIASES = {
    # Trig
    'sine': 'sin', 'cosine': 'cos', 'tangent': 'tan',
    'secant': 'sec', 'cosecant': 'csc', 'cotangent': 'cot',
    'arcsine': 'asin', 'arccosine': 'acos', 'arctangent': 'atan',
    'arcsin': 'asin', 'arccos': 'acos', 'arctan': 'atan',
    # Hyperbolic
    'sinh': 'sinh', 'cosh': 'cosh', 'tanh': 'tanh',
    # Logs
    'logarithm': 'log', 'natural_log': 'ln',
    # Misc
    'squareroot': 'sqrt', 'square_root': 'sqrt',
    'cuberoot': 'cbrt', 'cube_root': 'cbrt',
    'absolute': 'Abs', 'abs': 'Abs',
    'exponential': 'exp',
    'ceiling': 'ceiling', 'ceil': 'ceiling',
    'floor': 'floor',
}


# =============================================================================
# CALCULUS NOTATION PATTERNS
# =============================================================================

# Derivative notation patterns → diff() calls
# Applied after copy-paste cleanup but before other processing
DERIVATIVE_PATTERNS = [
    # Leibniz notation: dy/dx, d²y/dx², df/dx
    (r'\bd(\w+)/d(\w+)\b', r'diff(\1, \2)'),
    (r'\bd\^?2(\w+)/d(\w+)\^?2\b', r'diff(\1, \2, 2)'),
    (r'\bd\^?3(\w+)/d(\w+)\^?3\b', r'diff(\1, \2, 3)'),

    # d/dx operator followed by expression in parentheses - MUST come first
    (r'\bd/d(\w+)\s*\(([^)]+)\)', r'diff(\2, \1)'),

    # d/dx operator followed by function call like sin(x), cos(x)
    (r'\bd/d(\w+)\s+(\w+)\s*\(([^)]+)\)', r'diff(\2(\3), \1)'),

    # d/dx followed by simple expression
    (r'\bd/d(\w+)\s+([a-zA-Z0-9_]+)', r'diff(\2, \1)'),

    # Prime notation: f'(x), f''(x), f'''(x) - with function call
    # Use non-greedy and capture the full function form
    (r"\b([a-zA-Z])''''\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2, 4)'),
    (r"\b([a-zA-Z])'''\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2, 3)'),
    (r"\b([a-zA-Z])''\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2, 2)'),
    (r"\b([a-zA-Z])'\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2)'),

    # Standalone prime: F', f'' (no parentheses) - assumes variable x
    (r"\b([a-zA-Z])''''(?![a-zA-Z0-9(])", r"diff(\1(x), x, 4)"),
    (r"\b([a-zA-Z])'''(?![a-zA-Z0-9(])", r"diff(\1(x), x, 3)"),
    (r"\b([a-zA-Z])''(?![a-zA-Z0-9(])", r"diff(\1(x), x, 2)"),
    (r"\b([a-zA-Z])'(?![a-zA-Z0-9(])", r"diff(\1(x), x)"),

    # Prime with numeric coefficient: 3y', 2y'', etc -> 3*diff(y(x), x)
    (r"(\d+)([a-zA-Z])''''(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x, 4)"),
    (r"(\d+)([a-zA-Z])'''(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x, 3)"),
    (r"(\d+)([a-zA-Z])''(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x, 2)"),
    (r"(\d+)([a-zA-Z])'(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x)"),

    # Prime with variable coefficient: xy', ay'', etc -> x*diff(y(x), x)
    (r"([a-zA-Z])([a-zA-Z])''''(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x, 4)"),
    (r"([a-zA-Z])([a-zA-Z])'''(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x, 3)"),
    (r"([a-zA-Z])([a-zA-Z])''(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x, 2)"),
    (r"([a-zA-Z])([a-zA-Z])'(?![a-zA-Z0-9(])", r"\1*diff(\2(x), x)"),
]

# Integral notation patterns → integrate() calls
INTEGRAL_PATTERNS = [
    # Definite integral with bounds: ∫_a^b f(x)dx or integrate from a to b
    # Pattern after cleanup: Integral a b f(x) dx
    (r'Integral\s+(\w+)\s+(\w+)\s+(.+?)\s+d(\w+)\b', r'integrate(\3, (\4, \1, \2))'),

    # Indefinite integral: ∫ f(x)dx - be careful with 'd' followed by variable
    (r'Integral\s+(.+?)\s+d(\w+)\b', r'integrate(\1, \2)'),

    # integrate f from a to b - handles signed bounds and infinity variants
    # Matches: integrate f from 0 to 1, from -infinity to infinity, from -1 to 2
    (r'\bintegrate\s+(.+?)\s+from\s+(-?(?:\w+|infinity))\s+to\s+(-?(?:\w+|infinity))\b', r'integrate(\1, (x, \2, \3))'),
]

# These patterns are applied separately for natural language integrals
# ORDER MATTERS - more specific patterns first!
INTEGRAL_NATURAL_PATTERNS = [
    # Natural language: integral of f(x) with respect to x (most specific first)
    (r'\bintegral\s+of\s+(.+?)\s+with\s+respect\s+to\s+(\w+)', r'integrate(\1, \2)'),

    # Natural language: integral of f(x) dx
    (r'\bintegral\s+of\s+(.+?)\s+d(\w+)\b', r'integrate(\1, \2)'),

    # Simple: integral f(x) dx (no 'of') - use negative lookahead to avoid matching 'of'
    (r'\bintegral\s+(?!of\s)(.+?)\s+d(\w+)\b', r'integrate(\1, \2)'),
]


# =============================================================================
# NORMALIZATION FUNCTIONS
# =============================================================================

def preprocess_prime_notation(text: str) -> str:
    """
    Convert prime notation to diff() BEFORE other processing.

    This handles f'(x), f## (x), F′(x) etc. and converts them to diff()
    calls before implicit multiplication can mangle them.

    Examples:
        f'(x) → diff(f(x), x)
        F′(x) → diff(F(x), x)
        g''(t) → diff(g(t), t, 2)
    """
    result = text

    # First normalize prime characters: ′ (U+2032) and ` → '
    result = result.replace('′', "'")
    result = result.replace('`', "'")
    result = result.replace('´', "'")  # Acute accent

    # Match patterns: letter followed by primes followed by (variable)
    # f''''(x) → diff(f(x), x, 4)
    # First handle cases where a letter precedes the function: xy'(x) → x*diff(y(x), x)
    result = re.sub(r"([a-zA-Z])([a-zA-Z])''''\s*\(\s*(\w+)\s*\)", r'\1*diff(\2(\3), \3, 4)', result)
    result = re.sub(r"([a-zA-Z])([a-zA-Z])'''\s*\(\s*(\w+)\s*\)", r'\1*diff(\2(\3), \3, 3)', result)
    result = re.sub(r"([a-zA-Z])([a-zA-Z])''\s*\(\s*(\w+)\s*\)", r'\1*diff(\2(\3), \3, 2)', result)
    result = re.sub(r"([a-zA-Z])([a-zA-Z])'\s*\(\s*(\w+)\s*\)", r'\1*diff(\2(\3), \3)', result)

    # Now handle normal patterns: use (?<![a-zA-Z]) to allow digit-prefixed like 3y'(x)
    result = re.sub(r"(?<![a-zA-Z])([a-zA-Z])''''\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2, 4)', result)
    result = re.sub(r"(?<![a-zA-Z])([a-zA-Z])'''\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2, 3)', result)
    result = re.sub(r"(?<![a-zA-Z])([a-zA-Z])''\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2, 2)', result)
    result = re.sub(r"(?<![a-zA-Z])([a-zA-Z])'\s*\(\s*(\w+)\s*\)", r'diff(\1(\2), \2)', result)

    # Standalone: F' or f'' without parentheses (assume x as variable)
    result = re.sub(r"\b([a-zA-Z])''''(?![a-zA-Z0-9('′])", r'diff(\1(x), x, 4)', result)
    result = re.sub(r"\b([a-zA-Z])'''(?![a-zA-Z0-9('′])", r'diff(\1(x), x, 3)', result)
    result = re.sub(r"\b([a-zA-Z])''(?![a-zA-Z0-9('′])", r'diff(\1(x), x, 2)', result)
    result = re.sub(r"\b([a-zA-Z])'(?![a-zA-Z0-9('′])", r'diff(\1(x), x)', result)

    return result


# =============================================================================
# PROBABILITY & STATISTICS NOTATION PREPROCESSING
# =============================================================================

def preprocess_probability_symbols(text: str) -> str:
    """
    Handle probability and statistics notation that conflicts with Python/SymPy.

    Key transformations:
    1. 'lambda' (Greek letter in probability) -> 'lamda' (avoid Python keyword)
    2. E[X] (expectation) -> Expectation(X)
    3. Var(X), Var[X] -> Variance(X)
    4. Cov(X,Y) -> Covariance(X,Y)
    5. P(X <= x) -> Probability(X <= x)

    IMPORTANT: This must be called BEFORE SymPy parsing to avoid SyntaxError.

    Mathematical context:
    - λ (lambda) is the standard symbol for Poisson rate parameter
    - E[X] is standard notation for expected value
    - These are fundamental probability notations, not isolated patches
    """
    result = text

    # 1. Handle 'lambda' keyword conflict
    # Only replace when used as a variable/parameter, not in lambdify() etc
    # Pattern: lambda followed by operators, parens, or as standalone
    result = re.sub(r'\blambda\b(?!\s*:|\s*\()', 'lamda', result)

    # 2. Handle E[X] expectation notation - convert to symbolic form
    # E[X] -> ExpectedValue_X (underscore prevents implicit multiplication)
    result = re.sub(r'\bE\[([^\]]+)\]', r'ExpectedValue_\1', result)

    # 3. Handle Var[X] notation - convert to symbolic form
    result = re.sub(r'\bVar\[([^\]]+)\]', r'Variance_\1', result)

    # 4. Handle Cov[X,Y] notation - convert to symbolic form
    result = re.sub(r'\bCov\[([^\],]+),\s*([^\]]+)\]', r'Covariance_\1_\2', result)

    # 5. Handle H_n (harmonic number) notation
    # H_n -> HarmonicNumber_n (symbolic form)
    result = re.sub(r'\bH_(\w+)\b', r'HarmonicNumber_\1', result)

    # 6. Handle gamma constant (Euler-Mascheroni) when standalone
    # Keep 'gamma' as is - SymPy recognizes it

    return result


def preprocess_matrix_notation(text: str) -> str:
    """
    Convert bracket matrix notation to explicit Matrix() wrapper for LA functions.

    Transformations:
    - det([[a,b],[c,d]]) -> det(Matrix([[a,b],[c,d]]))
    - inverse([[1,2],[3,4]]) -> inverse(Matrix([[1,2],[3,4]]))
    - eigenvals([[2,1],[1,2]]) -> eigenvals(Matrix([[2,1],[1,2]]))
    - rank([[...]]) -> rank(Matrix([[...]]))
    - trace([[...]]) -> trace(Matrix([[...]]))
    - det(diag(1,2,3)) -> det(Matrix([[1,0,0],[0,2,0],[0,0,3]]))

    Mathematical context:
    - Matrix operations require Matrix type in SymPy
    - Bracket notation is standard mathematical convention
    - This is a structural transformation, not a patch
    """
    result = text

    # First, expand diag() function to explicit diagonal matrix
    # diag(1,2,3,4) -> Matrix([[1,0,0,0],[0,2,0,0],[0,0,3,0],[0,0,0,4]])
    def expand_diag(match):
        args_str = match.group(1)
        # Parse the arguments
        args = [a.strip() for a in args_str.split(',')]
        n = len(args)
        if n == 0:
            return match.group(0)
        # Build diagonal matrix
        rows = []
        for i in range(n):
            row = ['0'] * n
            row[i] = args[i]
            rows.append('[' + ','.join(row) + ']')
        return 'Matrix([' + ','.join(rows) + '])'

    # Pattern for diag(a,b,c,...) not already inside Matrix
    diag_pattern = r'\bdiag\s*\(\s*([^()]+)\s*\)'
    result = re.sub(diag_pattern, expand_diag, result)

    # Functions that take matrix arguments
    matrix_funcs = ['det', 'inverse', 'eigenvals', 'eigenvects', 'rank', 'trace',
                    'norm', 'transpose', 'adjugate', 'cofactor']

    for func in matrix_funcs:
        # Pattern: func([[...]]) without Matrix wrapper
        # Use GREEDY matching to capture full matrix content
        # Match func( [ [content with possible nested brackets] ] )
        pattern = rf'\b{func}\s*\(\s*(?!Matrix)(\[\[.+\]\])\s*\)'

        def make_replacer(fn):
            def replacer(match):
                matrix_content = match.group(1)
                return f'{fn}(Matrix({matrix_content}))'
            return replacer

        # Apply replacement iteratively for nested cases
        prev = None
        while prev != result:
            prev = result
            result = re.sub(pattern, make_replacer(func), result, flags=re.DOTALL)

    return result


def preprocess_special_notations(text: str) -> str:
    """
    Handle special mathematical notations that need conversion.

    Transformations:
    - sqrt{...} -> sqrt(...) (LaTeX-style braces)
    - sqrt[n]{...} -> root(..., n) (n-th root)
    - int_a^b -> integrate(..., (x, a, b)) (informal integral notation)
    - <psi|H|psi> -> braket notation (quantum mechanics)

    Mathematical context:
    - These are standard notations from LaTeX and physics
    - Convert to SymPy-compatible forms
    """
    result = text

    # 1. sqrt{expr} -> sqrt(expr) (LaTeX-style braces to parens)
    result = re.sub(r'sqrt\{([^}]+)\}', r'sqrt(\1)', result)

    # 2. sqrt[n]{expr} -> root(expr, n) (n-th root)
    result = re.sub(r'sqrt\[(\w+)\]\{([^}]+)\}', r'root(\2, \1)', result)

    # 3. e** -> exp() for clearer parsing (e**x -> exp(x))
    # Only when 'e' is standalone (not part of another word)
    result = re.sub(r'\be\s*\*\*\s*\(([^)]+)\)', r'exp(\1)', result)
    result = re.sub(r'\be\s*\*\*\s*(\w+)', r'exp(\1)', result)

    # 4. Handle Dirac notation <psi|H|psi> -> symbolic representation
    # This is quantum mechanics bra-ket notation
    result = re.sub(r'<(\w+)\|([^|]+)\|(\w+)>', r'braket(\1, \2, \3)', result)

    return result


def cleanup_copypaste_artifacts(text: str) -> str:
    """
    Clean up artifacts from copy-pasting rendered math from web pages/PDFs.

    When math is rendered in HTML/PDF and then copied, subscripts and
    superscripts often appear on separate lines. This function reconstructs
    the original expression.

    Examples:
        'x\\n2\\n+ 3' (x² + 3 copy-pasted) → 'x**2 + 3'
        'f\\n′\\n(x)' (f′(x) copy-pasted) → "f'(x)"
        '∫\\na\\nb\\nf(x)dx' → '∫_a^b f(x)dx'
    """
    if '\n' not in text and '\r' not in text:
        return text  # No multiline, nothing to do

    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    if len(lines) <= 1:
        return text.strip()

    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for integral with bounds on next lines
        # Pattern: ∫ followed by lower bound, upper bound on separate lines
        if line in ('∫', 'Integral', '∫∫', '∫∫∫'):
            integral_sym = line
            # Look for bounds
            if i + 2 < len(lines):
                potential_lower = lines[i + 1]
                potential_upper = lines[i + 2]
                # Bounds are typically single chars/short expressions
                if len(potential_lower) <= 10 and len(potential_upper) <= 10:
                    # Check if they look like bounds (not operators or long expressions)
                    if not any(op in potential_lower for op in ['+', '-', '*', '/', '=']):
                        result.append(f'{integral_sym}_{{{potential_lower}}}^{{{potential_upper}}}')
                        i += 3
                        continue
            # No bounds found, just add integral
            result.append(integral_sym)
            i += 1
            continue

        # Check for prime notation on next line
        # Pattern: f followed by ′ or ' on next line, then (x)
        if i + 1 < len(lines) and lines[i + 1] in ("′", "'", "''", "'''", "′′", "′′′"):
            primes = lines[i + 1]
            # Convert Unicode primes to ASCII
            primes = primes.replace('′', "'")
            # Check if next line is function args
            if i + 2 < len(lines) and lines[i + 2].startswith('('):
                result.append(f"{line}{primes}{lines[i + 2]}")
                i += 3
                continue
            else:
                result.append(f"{line}{primes}")
                i += 2
                continue

        # Check for superscript on next line (single digit or small number)
        # Pattern: x followed by 2 → x**2
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            # If next line is just a number (likely a power)
            if next_line.isdigit() and len(next_line) <= 2:
                # Check it's not an operator before it
                if not line.endswith(('+', '-', '*', '/', '=')):
                    result.append(f"{line}**{next_line}")
                    i += 2
                    continue
            # If next line is 'n' or single letter (could be power)
            if len(next_line) == 1 and next_line.isalpha():
                # Could be x^n pattern - be conservative
                if len(line) == 1 and line.isalpha():
                    result.append(f"{line}**{next_line}")
                    i += 2
                    continue

        # Check for subscript pattern (variable followed by number)
        # Pattern: x followed by 1 where context suggests subscript (like x₁)
        # This is tricky - skip for now as it's less common

        # Default: just add the line
        result.append(line)
        i += 1

    # Join with spaces
    return ' '.join(result)


def normalize_unicode(text: str) -> str:
    """
    Convert all Unicode math symbols to ASCII equivalents.

    This is the first step - convert special characters before any parsing.
    """
    result = text

    # Apply all character maps
    for char, replacement in GREEK_MAP.items():
        result = result.replace(char, replacement)

    for char, replacement in SYMBOL_MAP.items():
        result = result.replace(char, replacement)

    for char, replacement in SUPERSCRIPT_MAP.items():
        result = result.replace(char, replacement)

    for char, replacement in SUBSCRIPT_MAP.items():
        result = result.replace(char, replacement)

    for char, replacement in FRACTION_MAP.items():
        result = result.replace(char, replacement)

    for char, replacement in OPERATOR_MAP.items():
        result = result.replace(char, replacement)

    # Dashes → hyphen-minus
    for dash in DASH_CHARS:
        result = result.replace(dash, '-')

    # Quotes → straight quotes
    for char, replacement in QUOTE_MAP.items():
        result = result.replace(char, replacement)

    # Invisible chars → space
    for char in INVISIBLE_CHARS:
        result = result.replace(char, ' ')

    return result


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace to single spaces.
    Also handles newlines (joins multi-line input).
    """
    # Replace newlines with spaces
    result = text.replace('\n', ' ').replace('\r', ' ')

    # Collapse multiple spaces
    result = ' '.join(result.split())

    return result.strip()


def apply_modular_patterns(text: str) -> str:
    """
    Convert modular arithmetic notation to SymPy Mod() calls.

    This MUST be called BEFORE implicit multiplication is applied,
    otherwise 'mod' gets split into m*o*d.

    Examples:
        a≡b(mod n) → Mod(a, n) == Mod(b, n)
        ax≡b(modn) → Mod(ax, n) == Mod(b, n)
        5 mod 3 → Mod(5, 3)
    """
    result = text

    for pattern, replacement in MODULAR_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def apply_derivative_patterns(text: str) -> str:
    """
    Convert derivative notation to SymPy diff() calls.

    Handles:
        - Leibniz notation: dy/dx, d²y/dx²
        - Prime notation: f'(x), f''(x), f'''(x)
        - Operator notation: d/dx f(x)

    Examples:
        dy/dx → diff(y, x)
        f'(x) → diff(f(x), x)
        d/dx sin(x) → diff(sin(x), x)
    """
    result = text

    for pattern, replacement in DERIVATIVE_PATTERNS:
        result = re.sub(pattern, replacement, result)

    return result


def apply_integral_patterns(text: str) -> str:
    """
    Convert integral notation to SymPy integrate() calls.

    Handles:
        - Integral symbol: ∫ f(x)dx, ∫_a^b f(x)dx
        - Natural language: integral of f(x) dx
        - Bounds notation: integrate f from a to b

    Examples:
        ∫ x**2 dx → integrate(x**2, x)
        ∫_0^1 x dx → integrate(x, (x, 0, 1))
        integral of sin(x) dx → integrate(sin(x), x)
    """
    result = text

    # Apply natural language integral patterns FIRST (before symbol conversion)
    # This prevents "integral of x" from being matched by the generic "Integral" pattern
    for pattern, replacement in INTEGRAL_NATURAL_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Now convert symbol notation: ∫_{a}^{b} → Integral a b
    result = re.sub(r'∫_\{([^}]+)\}\^\{([^}]+)\}', r'Integral \1 \2 ', result)
    result = re.sub(r'∫_(\w+)\^(\w+)', r'Integral \1 \2 ', result)

    # Convert bare ∫ to Integral marker (using unique token to avoid confusion)
    result = result.replace('∫', '__INTEGRAL__ ')

    # Apply symbol-based integral patterns (case-sensitive for __INTEGRAL__)
    for pattern, replacement in INTEGRAL_PATTERNS:
        # Replace 'Integral' with '__INTEGRAL__' in pattern for symbol matching
        symbol_pattern = pattern.replace('Integral', '__INTEGRAL__')
        result = re.sub(symbol_pattern, replacement, result)

    # Clean up any remaining __INTEGRAL__ markers
    result = result.replace('__INTEGRAL__', 'Integral')

    return result


def apply_word_patterns(text: str) -> str:
    """
    Convert natural language math patterns to symbolic form.
    """
    result = text

    for pattern, replacement in WORD_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Clean up space after function open parens: "sqrt( x)" → "sqrt(x)"
    result = re.sub(r'(\w+\()\s+', r'\1', result)

    return result


def normalize_function_names(text: str) -> str:
    """
    Normalize function name variations to canonical forms.
    """
    result = text

    for alias, canonical in FUNCTION_ALIASES.items():
        # Word boundary to avoid partial matches
        pattern = r'\b' + re.escape(alias) + r'\b'
        result = re.sub(pattern, canonical, result, flags=re.IGNORECASE)

    return result


def add_implicit_multiplication(text: str) -> str:
    """
    Add * for implicit multiplication.

    Examples:
        2x → 2*x
        2(x+1) → 2*(x+1)
        (x)(y) → (x)*(y)
        2pi → 2*pi
        pi r → pi*r
    """
    result = text

    # Number followed by letter or (
    result = re.sub(r'(\d)\s*([a-zA-Z(])', r'\1*\2', result)

    # ) followed by ( or letter or number
    result = re.sub(r'\)\s*([a-zA-Z0-9(])', r')*\1', result)

    # Letter/word followed by ( - but NOT for functions (handled below)
    result = re.sub(r'([a-zA-Z])\s*\(', r'\1*(', result)

    # Word followed by single letter (e.g., "pi r" → "pi*r", "alpha x" → "alpha*x")
    # This catches Greek letter names followed by variables
    result = re.sub(r'\b(pi|alpha|beta|gamma|delta|epsilon|theta|phi|psi|omega|sigma|lambda|mu|tau)\s+([a-zA-Z])\b',
                   r'\1*\2', result, flags=re.IGNORECASE)

    # But undo for known functions
    known_functions = [
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
        'asin', 'acos', 'atan', 'asec', 'acsc', 'acot',
        'sinh', 'cosh', 'tanh', 'sech', 'csch', 'coth',
        'asinh', 'acosh', 'atanh',
        'sqrt', 'cbrt', 'root', 'root4',
        'log', 'ln', 'exp', 'log10', 'log2',
        'Abs', 'abs', 'sign', 'floor', 'ceiling', 'ceil',
        'factorial', 'gamma', 'Gamma',
        'diff', 'integrate', 'Integral', 'Derivative',
        'Sum', 'Product', 'limit', 'Limit',
        'solve', 'simplify', 'expand', 'factor',
        'Mod', 'mod', 'gcd', 'lcm',  # Modular arithmetic functions
        'pi', 'Pi', 'E', 'I', 'oo',
        'alpha', 'beta', 'gamma', 'delta', 'epsilon',
        'theta', 'phi', 'psi', 'omega', 'lambda', 'mu', 'sigma',
        'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon',
        'Theta', 'Phi', 'Psi', 'Omega', 'Lambda', 'Mu', 'Sigma',
        # Single letter function names (only uppercase, lowercase are usually variables)
        'F', 'G', 'H', 'U', 'V', 'W',
        'P', 'Q', 'R', 'S', 'T',  # Also common for functions
        'Y', 'X', 'Z',  # Uppercase versions as function names (rare)
        # Linear algebra functions
        'det', 'tr', 'trace', 'rank', 'dim', 'ker', 'im', 'span',
        'norm', 'adj', 'inv', 'transpose', 'diag',
        # Statistics/probability functions
        'Var', 'var', 'Cov', 'cov', 'Corr', 'corr', 'Std', 'std',
        'E', 'Prob', 'prob',  # E for expected value
        # Sequence functions
        'sum', 'prod', 'product',
        # Logic
        'ForAll', 'Exists', 'And', 'Or', 'Not', 'Implies',
    ]

    for func in known_functions:
        # Remove * between function name and (
        pattern = re.escape(func) + r'\*\('
        replacement = func + '('
        result = re.sub(pattern, replacement, result)

    return result


def add_function_parens(text: str) -> str:
    """
    Add parentheses to function calls without them.

    Examples:
        sqrt9 → sqrt(9)
        sin30 → sin(30)
        log10 → log(10)
    """
    # Pattern: function name followed by number (without paren)
    func_pattern = re.compile(
        r'\b(sqrt|cbrt|sin|cos|tan|sec|csc|cot|'
        r'asin|acos|atan|asec|acsc|acot|'
        r'sinh|cosh|tanh|'
        r'log|ln|exp|Abs|abs|sign|floor|ceiling|ceil)'
        r'(\d+\.?\d*)\b'
    )

    return func_pattern.sub(r'\1(\2)', text)


def normalize_operators(text: str) -> str:
    """
    Normalize operator notation.
    """
    result = text

    # ^ → ** (LaTeX/common notation to Python)
    result = result.replace('^', '**')

    # Handle double operators like ++ or -- or **
    result = re.sub(r'\+\+', '+', result)
    result = re.sub(r'--', '+', result)  # Double negative = positive
    result = re.sub(r'\+-', '-', result)
    result = re.sub(r'-\+', '-', result)

    # Ensure spaces around = for equations (but not ==, <=, >=, !=)
    result = re.sub(r'(?<![<>=!])=(?!=)', ' = ', result)

    return result


def close_unclosed_parens(text: str) -> str:
    """
    Attempt to close unclosed parentheses at the end.

    This is a heuristic for cases like "sqrt(9" → "sqrt(9)"
    """
    open_count = text.count('(') - text.count(')')
    if open_count > 0:
        text = text + ')' * open_count

    open_count = text.count('[') - text.count(']')
    if open_count > 0:
        text = text + ']' * open_count

    open_count = text.count('{') - text.count('}')
    if open_count > 0:
        text = text + '}' * open_count

    return text


def fix_exponent_precedence(text: str) -> str:
    """
    Fix exponentiation precedence issues.

    Standard mathematical convention: ** binds tighter than unary minus.
    So -x**2 means -(x**2), not (-x)**2.

    But some parsers (including our native_calculus parser) interpret
    -x**2 as (-x)**2. This function rewrites problematic patterns to
    ensure correct evaluation.

    Transformations:
        -x**n → (-1)*x**n   (where n is any exponent)
        -a*x**n stays as is (already has explicit coefficient)

    This ensures that exp(-x**4) evaluates as exp(-(x**4)) = exp(-x^4)
    rather than exp((-x)**4) = exp(x^4).
    """
    # Pattern: -variable**exponent where the minus is a unary operator
    # Matches: -x**2, -y**4, -t**3, etc.
    # Does NOT match: a-x**2 (binary minus), -3*x**2 (already has coefficient)

    # Replace -var**exp with (-1)*var**exp
    # The lookbehind ensures we only match unary minus (after (, +, *, /, =, or start)
    result = re.sub(
        r'(?<=[(+*/=,\s])-([a-zA-Z_][a-zA-Z0-9_]*)\*\*',
        r'(-1)*\1**',
        text
    )

    # Also handle at start of string
    if result.startswith('-') and '**' in result:
        # Check if it's -var**something at the very start
        match = re.match(r'^-([a-zA-Z_][a-zA-Z0-9_]*)\*\*', result)
        if match:
            result = '(-1)*' + result[1:]

    return result


def normalize_input(text: str,
                   add_multiplication: bool = True,
                   close_parens: bool = True,
                   verbose: bool = False) -> str:
    """
    Main normalization function - converts any math input to SymPy format.

    Args:
        text: Raw input text (can be Unicode, LaTeX, natural language, etc.)
        add_multiplication: Whether to add implicit * (e.g., 2x → 2*x)
        close_parens: Whether to auto-close unclosed parentheses
        verbose: If True, log each transformation step

    Returns:
        Normalized expression ready for SymPy parsing

    Examples:
        >>> normalize_input("2πr²")
        '2*pi*r**2'

        >>> normalize_input("½ × base × height")
        '(1/2)*base*height'

        >>> normalize_input("x squared plus 2x minus 3 equals 0")
        'x**2 + 2*x - 3 = 0'

        >>> normalize_input("√9 + ∛27")
        'sqrt(9) + cbrt(27)'
    """
    if not text:
        return ''

    result = text

    if verbose:
        logger.debug(f"Input: {repr(text)}")

    # Step 0: Clean up copy-paste artifacts FIRST
    # This reconstructs expressions that got split across lines when copied
    result = cleanup_copypaste_artifacts(result)
    if verbose:
        logger.debug(f"After copy-paste cleanup: {result}")

    # Step 0.2: Handle probability notation EARLY (before SymPy parsing)
    # - 'lambda' (Poisson rate) -> 'lamda' (avoid Python keyword)
    # - E[X], Var(X), Cov(X,Y) -> symbolic forms
    # - H_n -> harmonic(n)
    result = preprocess_probability_symbols(result)
    if verbose:
        logger.debug(f"After probability symbols: {result}")

    # Step 0.3: Handle matrix bracket notation
    # det([[a,b],[c,d]]) -> det(Matrix([[a,b],[c,d]]))
    result = preprocess_matrix_notation(result)
    if verbose:
        logger.debug(f"After matrix notation: {result}")

    # Step 0.4: Handle special notations (sqrt{}, bra-ket, etc.)
    result = preprocess_special_notations(result)
    if verbose:
        logger.debug(f"After special notations: {result}")

    # Step 0.5: Handle prime notation EARLY (before anything can mangle it)
    # f'(x) → diff(f(x), x), F′(x) → diff(F(x), x)
    result = preprocess_prime_notation(result)
    if verbose:
        logger.debug(f"After prime notation: {result}")

    # Step 1: Normalize whitespace (join remaining multi-line)
    result = normalize_whitespace(result)
    if verbose:
        logger.debug(f"After whitespace: {result}")

    # Step 2: Convert Unicode symbols to ASCII
    result = normalize_unicode(result)
    if verbose:
        logger.debug(f"After Unicode: {result}")

    # Step 3: Clean up whitespace again (Unicode replacement may add spaces)
    result = normalize_whitespace(result)

    # Step 3.5: Expand vector calculus operators EARLY
    # grad(f, [x,y]) → [diff(f,x), diff(f,y)], etc.
    result = expand_vector_calculus(result)
    if verbose:
        logger.debug(f"After vector calculus: {result}")

    # Step 3.6: Apply calculus patterns (before word patterns)
    # Derivative patterns: f'(x) → diff(f(x), x), dy/dx → diff(y, x)
    result = apply_derivative_patterns(result)
    if verbose:
        logger.debug(f"After derivative patterns: {result}")

    # Integral patterns: ∫f(x)dx → integrate(f(x), x)
    result = apply_integral_patterns(result)
    if verbose:
        logger.debug(f"After integral patterns: {result}")

    # Step 3.6: Apply modular arithmetic patterns
    # This must happen BEFORE word patterns convert "mod" to "%"
    result = apply_modular_patterns(result)
    if verbose:
        logger.debug(f"After modular patterns: {result}")

    # Step 4: Apply natural language patterns
    result = apply_word_patterns(result)
    if verbose:
        logger.debug(f"After word patterns: {result}")

    # Step 5: Normalize function names
    result = normalize_function_names(result)
    if verbose:
        logger.debug(f"After function names: {result}")

    # Step 6: Add function parentheses (sqrt9 → sqrt(9))
    result = add_function_parens(result)
    if verbose:
        logger.debug(f"After function parens: {result}")

    # Step 7: Normalize operators (^ → **)
    result = normalize_operators(result)
    if verbose:
        logger.debug(f"After operators: {result}")

    # Step 8: Add implicit multiplication
    if add_multiplication:
        # First apply enhanced patterns for cases like sigmasqrt(2pi) -> sigma*sqrt(2*pi)
        result = enhanced_implicit_multiplication(result)
        if verbose:
            logger.debug(f"After enhanced multiplication: {result}")
        # Then apply standard implicit multiplication
        result = add_implicit_multiplication(result)
        if verbose:
            logger.debug(f"After multiplication: {result}")
        # Fix any spurious * inserted before function names
        result = remove_spurious_multiplication(result)
        if verbose:
            logger.debug(f"After removing spurious multiplication: {result}")

    # Step 9: Close unclosed parens
    if close_parens:
        result = close_unclosed_parens(result)
        if verbose:
            logger.debug(f"After closing parens: {result}")

    # Step 9.5: Fix exponentiation precedence
    # Convert -x**n to (-1)*x**n to ensure correct precedence
    # Standard math convention: ** binds tighter than unary -, so -x**2 = -(x**2)
    # But some parsers interpret -x**2 as (-x)**2
    # This fix ensures correct evaluation by making it explicit
    result = fix_exponent_precedence(result)
    if verbose:
        logger.debug(f"After exponent precedence fix: {result}")

    # Step 10: Final whitespace cleanup
    result = normalize_whitespace(result)

    if verbose:
        logger.debug(f"Final: {result}")

    return result


def _extract_command_args(text: str, command: str) -> Optional[str]:
    """
    Extract the full argument string from a command call, handling nested parentheses.

    Example:
        _extract_command_args("expand((x+1)**3)", "expand") -> "(x+1)**3"
        _extract_command_args("factor(x**2 - 9)", "factor") -> "x**2 - 9"
        _extract_command_args("diff(sin(x), x)", "diff") -> "sin(x), x"

    Returns None if the command is not found or parentheses are unbalanced.
    """
    # Find command position
    cmd_pattern = re.compile(rf'\b{re.escape(command)}\s*\(', re.IGNORECASE)
    match = cmd_pattern.search(text)
    if not match:
        return None

    # Find the start of arguments (after the opening paren)
    start = match.end()

    # Track parentheses balance to find the matching close paren
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
        i += 1

    if depth != 0:
        return None  # Unbalanced

    # Extract content between opening and closing parens
    return text[start:i-1].strip()


def normalize_and_extract_command(text: str,
                                  add_multiplication: bool = True,
                                  close_parens: bool = True,
                                  verbose: bool = False) -> Tuple[str, Optional[Dict]]:
    """
    Normalize input AND extract command metadata if present.

    This function handles SymPy-style commands like:
    - solve(x**2 - 4, x) → extracts equation, variable, and command='solve'
    - dsolve(y''(x) + y(x), y(x)) → extracts ODE and function
    - diff(f(x), x) → extracts function and variable
    - integrate(x**2, x) → extracts integrand and variable

    Returns:
        (normalized_expr, command_metadata) where:
        - normalized_expr: The cleaned expression ready for processing
        - command_metadata: Dict with command info, or None if no command detected

    Example:
        >>> normalize_and_extract_command("solve(x**2 - 4, x)")
        ('x**2 - 4', {'command': 'solve', 'equation': 'x**2 - 4', 'variable': 'x'})

        >>> normalize_and_extract_command("2x + 3")
        ('2*x + 3', None)

    Reference:
        Second Opinion Analysis: "solve() wrapper breaking routing"
    """
    if not text:
        return '', None

    # First, check for command patterns BEFORE normalization
    # (so we don't mangle the command structure)
    text_stripped = text.strip()

    # Check for solve([equations], [vars]) system syntax FIRST
    # (before single solve, since system pattern is more specific)
    system_match = COMMAND_PATTERNS['solve_system'].search(text_stripped)
    if system_match:
        equations_str = system_match.group(1)
        vars_str = system_match.group(2)
        # Parse equations list
        equations = [eq.strip() for eq in equations_str.split(',')]
        variables = [v.strip() for v in vars_str.split(',')]
        # Normalize each equation
        normalized_eqs = []
        for eq in equations:
            normalized_eq = normalize_input(eq, add_multiplication=add_multiplication,
                                           close_parens=close_parens, verbose=verbose)
            normalized_eqs.append(normalized_eq)
        meta = {
            'command': 'solve_system',
            'equations': normalized_eqs,
            'variables': variables,
            'expression': str(normalized_eqs),
            'original': text_stripped
        }
        return str(normalized_eqs), meta

    # Check for solve() command (single equation)
    solve_expr, solve_meta = unwrap_solve_command(text_stripped)
    if solve_meta:
        # Normalize just the equation part
        normalized_eq = normalize_input(solve_meta['equation'],
                                        add_multiplication=add_multiplication,
                                        close_parens=close_parens,
                                        verbose=verbose)
        solve_meta['equation'] = normalized_eq
        solve_meta['normalized'] = normalized_eq
        return normalized_eq, solve_meta

    # Check for diff() command
    diff_match = re.match(r'diff\s*\(\s*(.+?)\s*,\s*([a-zA-Z_]\w*)\s*(?:,\s*(\d+))?\s*\)', text_stripped)
    if diff_match:
        expr = diff_match.group(1)
        var = diff_match.group(2)
        order = diff_match.group(3)
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'differentiate',
            'expression': normalized_expr,
            'variable': var,
            'order': int(order) if order else 1,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for double integral (2D) FIRST - most specific
    # Pattern: integrate(expr, (var1, lo1, hi1), (var2, lo2, hi2))
    int_2d_match = re.match(
        r'integrate\s*\(\s*(.+?)\s*,\s*\(\s*([a-zA-Z_]\w*)\s*,\s*([^,)]+)\s*,\s*([^)]+)\s*\)\s*,\s*\(\s*([a-zA-Z_]\w*)\s*,\s*([^,)]+)\s*,\s*([^)]+)\s*\)\s*\)',
        text_stripped
    )
    if int_2d_match:
        expr = int_2d_match.group(1)
        var1 = int_2d_match.group(2)
        lower1 = int_2d_match.group(3).strip()
        upper1 = int_2d_match.group(4).strip()
        var2 = int_2d_match.group(5)
        lower2 = int_2d_match.group(6).strip()
        upper2 = int_2d_match.group(7).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'integrate_2d',
            'expression': normalized_expr,
            'variable': var1,
            'variable2': var2,
            'lower_bound': lower1,
            'upper_bound': upper1,
            'lower_bound2': lower2,
            'upper_bound2': upper2,
            'is_definite': True,
            'is_2d': True,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for integrate() command - definite integral with bounds FIRST (more specific)
    # Pattern: integrate(expr, (var, lower, upper)) - handles oo, -oo, numbers
    int_def_match = re.match(
        r'integrate\s*\(\s*(.+?)\s*,\s*\(\s*([a-zA-Z_]\w*)\s*,\s*([^,)]+)\s*,\s*([^)]+)\s*\)\s*\)',
        text_stripped
    )
    if int_def_match:
        expr = int_def_match.group(1)
        var = int_def_match.group(2)
        lower = int_def_match.group(3).strip()
        upper = int_def_match.group(4).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'integrate',
            'expression': normalized_expr,
            'variable': var,
            'lower_bound': lower,
            'upper_bound': upper,
            'is_definite': True,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for integrate() command - indefinite integral
    int_match = re.match(r'integrate\s*\(\s*(.+?)\s*,\s*([a-zA-Z_]\w*)\s*\)', text_stripped)
    if int_match:
        expr = int_match.group(1)
        var = int_match.group(2)
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'integrate',
            'expression': normalized_expr,
            'variable': var,
            'is_definite': False,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for factor() command (uses balanced paren extraction)
    factor_args = _extract_command_args(text_stripped, 'factor')
    if factor_args is not None:
        normalized_expr = normalize_input(factor_args, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'factor',
            'expression': normalized_expr,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for expand() command (uses balanced paren extraction for nested parens)
    expand_args = _extract_command_args(text_stripped, 'expand')
    if expand_args is not None:
        normalized_expr = normalize_input(expand_args, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'expand',
            'expression': normalized_expr,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for simplify() command (uses balanced paren extraction)
    simplify_args = _extract_command_args(text_stripped, 'simplify')
    if simplify_args is not None:
        normalized_expr = normalize_input(simplify_args, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        # Check if this involves complex expressions (I, exp(I*...), (a+bI)^n)
        # These should route to native complex simplification
        is_complex = re.search(r'\bI\b|exp\s*\(\s*I|exp\s*\(\s*-\s*I', simplify_args)
        command = 'complex_simplify' if is_complex else 'simplify'
        meta = {
            'command': command,
            'expression': normalized_expr,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for limit() command - limit(expr, var, point) or limit(expr, var, point, dir)
    limit_match = re.match(
        r'limit\s*\(\s*(.+?)\s*,\s*([a-zA-Z_]\w*)\s*,\s*([^,)]+)\s*(?:,\s*([+-]?))?\s*\)',
        text_stripped
    )
    if limit_match:
        expr = limit_match.group(1)
        var = limit_match.group(2)
        point = limit_match.group(3).strip()
        direction = limit_match.group(4) if limit_match.group(4) else None
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        normalized_point = normalize_input(point, add_multiplication=add_multiplication,
                                           close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'limit',
            'expression': normalized_expr,
            'variable': var,
            'point': normalized_point,
            'direction': direction,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for diophantine() command - diophantine(equation)
    diophantine_match = re.match(r'diophantine\s*\(\s*(.+?)\s*\)', text_stripped, re.IGNORECASE)
    if diophantine_match:
        equation = diophantine_match.group(1)
        normalized_eq = normalize_input(equation, add_multiplication=add_multiplication,
                                        close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'diophantine',
            'expression': normalized_eq,
            'equation': normalized_eq,
            'original': text_stripped
        }
        return text_stripped, meta  # Return full command for special handling

    # Check for det() command - det(matrix_expr)
    det_match = re.match(r'det\s*\(\s*(.+?)\s*\)', text_stripped, re.IGNORECASE)
    if det_match:
        matrix_expr = det_match.group(1)
        normalized_expr = normalize_input(matrix_expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'det',
            'expression': normalized_expr,
            'original': text_stripped
        }
        return text_stripped, meta  # Return full command for special handling

    # Check for grad() command - grad(f, [x, y]) or grad(f, [x, y, z])
    grad_match = re.match(r'grad\s*\(\s*(.+?)\s*,\s*\[([^\]]+)\]\s*\)', text_stripped)
    if grad_match:
        expr = grad_match.group(1)
        vars_str = grad_match.group(2)
        vars_list = [v.strip() for v in vars_str.split(',')]
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        # Expand grad to list of derivatives
        expanded = expand_vector_calculus(text_stripped)
        meta = {
            'command': 'grad',
            'expression': normalized_expr,
            'variables': vars_list,
            'expanded': expanded,
            'original': text_stripped
        }
        return expanded, meta

    # Check for simple grad() - grad(expr) without explicit variable list
    # Infer variables from expression's free symbols
    grad_simple_match = re.match(r'grad(?:ient)?\s*\(\s*([^,\[\]]+?)\s*\)', text_stripped, re.IGNORECASE)
    if grad_simple_match:
        expr = grad_simple_match.group(1).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'grad',
            'expression': normalized_expr,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for "gradient of expr" natural language
    gradient_natural_match = re.match(r'gradient\s+(?:of\s+)?(.+)', text_stripped, re.IGNORECASE)
    if gradient_natural_match:
        expr = gradient_natural_match.group(1).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'grad',
            'expression': normalized_expr,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for "grad expr" space-separated form
    grad_space_match = re.match(r'grad\s+([^\[\]\(\)]+)', text_stripped, re.IGNORECASE)
    if grad_space_match:
        expr = grad_space_match.group(1).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'grad',
            'expression': normalized_expr,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for div() command - div([P, Q, R], [x, y, z])
    div_match = re.match(r'div\s*\(\s*\[([^\]]+)\]\s*(?:,\s*\[([^\]]+)\])?\s*\)', text_stripped)
    if div_match:
        components_str = div_match.group(1)
        vars_str = div_match.group(2) if div_match.group(2) else 'x, y, z'
        components = [c.strip() for c in components_str.split(',')]
        vars_list = [v.strip() for v in vars_str.split(',')]
        # Expand div to sum of derivatives
        expanded = expand_vector_calculus(text_stripped)
        meta = {
            'command': 'div',
            'components': components,
            'variables': vars_list,
            'expanded': expanded,
            'original': text_stripped
        }
        return expanded, meta

    # Check for curl() command - curl([P, Q, R], [x, y, z])
    curl_match = re.match(r'curl\s*\(\s*\[([^\]]+)\]\s*,\s*\[([^\]]+)\]\s*\)', text_stripped)
    if curl_match:
        components_str = curl_match.group(1)
        vars_str = curl_match.group(2)
        components = [c.strip() for c in components_str.split(',')]
        vars_list = [v.strip() for v in vars_str.split(',')]
        # Expand curl to component derivatives
        expanded = expand_vector_calculus(text_stripped)
        meta = {
            'command': 'curl',
            'components': components,
            'variables': vars_list,
            'expanded': expanded,
            'original': text_stripped
        }
        return expanded, meta

    # Check for abs() / Abs() command for complex modulus - abs(complex_expr)
    abs_match = re.match(r'(?:abs|Abs)\s*\(\s*(.+)\s*\)', text_stripped, re.IGNORECASE)
    if abs_match:
        expr = abs_match.group(1).strip()
        # Check if this looks like a complex expression (contains I or i as imaginary unit)
        if re.search(r'\bI\b|(?<![a-zA-Z])i(?![a-zA-Z])', expr):
            normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                              close_parens=close_parens, verbose=verbose)
            meta = {
                'command': 'complex_modulus',
                'expression': normalized_expr,
                'original': text_stripped
            }
            return normalized_expr, meta

    # Check for arg() command for complex argument - arg(complex_expr)
    arg_match = re.match(r'arg\s*\(\s*(.+)\s*\)', text_stripped)
    if arg_match:
        expr = arg_match.group(1).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'complex_argument',
            'expression': normalized_expr,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for summation/sum/Sum() command - multiple syntax patterns supported
    # Pattern 1: summation(1/n**2, (n, 1, oo)) - SymPy tuple syntax
    # Pattern 2: sum(1/n**2, n=1..oo) - Mathematica-style
    # Pattern 3: Sum(1/n**2, (n, 1, oo)) - SymPy capitalized

    # First try SymPy tuple syntax: summation|sum|Sum(expr, (var, start, end))
    sum_match = re.match(
        r'(?:summation|sum|Sum)\s*\(\s*(.+?)\s*,\s*\(\s*([a-zA-Z_]\w*)\s*,\s*([^,)]+)\s*,\s*([^)]+)\s*\)\s*\)',
        text_stripped
    )
    if sum_match:
        expr = sum_match.group(1)
        var = sum_match.group(2)
        start = sum_match.group(3).strip()
        end = sum_match.group(4).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'summation',
            'expression': normalized_expr,
            'variable': var,
            'start': start,
            'end': end,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Try Mathematica-style: sum(expr, var=start..end)
    sum_math_match = re.match(
        r'(?:summation|sum|Sum)\s*\(\s*(.+?)\s*,\s*([a-zA-Z_]\w*)\s*=\s*([^.]+)\s*\.\.\s*([^)]+)\s*\)',
        text_stripped
    )
    if sum_math_match:
        expr = sum_math_match.group(1)
        var = sum_math_match.group(2)
        start = sum_math_match.group(3).strip()
        end = sum_math_match.group(4).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'summation',
            'expression': normalized_expr,
            'variable': var,
            'start': start,
            'end': end,
            'original': text_stripped
        }
        return normalized_expr, meta

    # Check for product() command - product(expr, (var, start, end))
    # Pattern: product(n, (n, 1, 10))
    prod_match = re.match(
        r'product\s*\(\s*(.+?)\s*,\s*\(\s*([a-zA-Z_]\w*)\s*,\s*([^,)]+)\s*,\s*([^)]+)\s*\)\s*\)',
        text_stripped
    )
    if prod_match:
        expr = prod_match.group(1)
        var = prod_match.group(2)
        start = prod_match.group(3).strip()
        end = prod_match.group(4).strip()
        normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                          close_parens=close_parens, verbose=verbose)
        meta = {
            'command': 'product',
            'expression': normalized_expr,
            'variable': var,
            'start': start,
            'end': end,
            'original': text_stripped
        }
        return normalized_expr, meta

    # No command pattern detected - normalize and check again
    # This handles cases like "integrate f from a to b" which gets transformed
    # to "integrate(f, (x, a, b))" during normalization
    normalized = normalize_input(text, add_multiplication=add_multiplication,
                                 close_parens=close_parens, verbose=verbose)

    # If normalized form looks like a command, re-check patterns
    if normalized != text_stripped and normalized.startswith(('integrate(', 'diff(', 'solve(')):
        # Check for definite integrate() command after normalization
        int_def_match = re.match(
            r'integrate\s*\(\s*(.+?)\s*,\s*\(\s*([a-zA-Z_]\w*)\s*,\s*([^,)]+)\s*,\s*([^)]+)\s*\)\s*\)',
            normalized
        )
        if int_def_match:
            expr = int_def_match.group(1)
            var = int_def_match.group(2)
            lower = int_def_match.group(3).strip()
            upper = int_def_match.group(4).strip()
            # Normalize the expression part
            normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                              close_parens=close_parens, verbose=verbose)
            meta = {
                'command': 'integrate',
                'expression': normalized_expr,
                'variable': var,
                'lower_bound': lower,
                'upper_bound': upper,
                'is_definite': True,
                'original': text
            }
            return normalized_expr, meta

        # Check for indefinite integrate() command
        int_match = re.match(r'integrate\s*\(\s*(.+?)\s*,\s*([a-zA-Z_]\w*)\s*\)', normalized)
        if int_match:
            expr = int_match.group(1)
            var = int_match.group(2)
            normalized_expr = normalize_input(expr, add_multiplication=add_multiplication,
                                              close_parens=close_parens, verbose=verbose)
            meta = {
                'command': 'integrate',
                'expression': normalized_expr,
                'variable': var,
                'is_definite': False,
                'original': text
            }
            return normalized_expr, meta

    return normalized, None


def validate_normalized(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that normalized text is likely parseable.

    Returns:
        (is_valid, error_message)
    """
    if not text:
        return False, "Empty expression"

    # Check balanced parentheses
    if text.count('(') != text.count(')'):
        return False, f"Unbalanced parentheses: {text.count('(')} ( vs {text.count(')')} )"

    if text.count('[') != text.count(']'):
        return False, f"Unbalanced brackets: {text.count('[')} [ vs {text.count(']')} ]"

    if text.count('{') != text.count('}'):
        return False, f"Unbalanced braces: {text.count('{')} {{ vs {text.count('}')} }}"

    # Check for obviously bad patterns
    if re.search(r'[+\-*/^]{3,}', text):
        return False, "Multiple consecutive operators"

    if text.startswith(('*', '/', '^', '**')):
        return False, "Expression starts with operator"

    if re.search(r'[+\-*/^]\s*$', text) and not text.endswith('...'):
        return False, "Expression ends with operator"

    return True, None


# =============================================================================
# ENHANCED ERROR MESSAGES
# =============================================================================

class InputDiagnostic:
    """
    Provides detailed diagnostic messages for input parsing failures.

    Instead of generic "No expression to solve", this class analyzes the
    input and provides specific, actionable error messages.
    """

    # Patterns that indicate specific error categories
    MATRIX_MALFORMED = re.compile(r'\[\s*,|\,\s*\]|\[\s*\]')
    PROBABILITY_NOTATION = re.compile(
        r'\b(E|Var|Cov|Std)\s*\(\s*\w+\s*\)\s*(where|~|given)',
        re.IGNORECASE
    )
    DISTRIBUTION_NOTATION = re.compile(
        r'\b(Normal|Binomial|Poisson|Uniform|Exponential)\s*\(\s*[^)]*\)',
        re.IGNORECASE
    )
    ENGLISH_GLUE = re.compile(
        r'\b(where|such that|given that|for all|there exists)\b',
        re.IGNORECASE
    )
    UNSUPPORTED_COMMAND = re.compile(
        r'\b(eigenvals|eigenvects|det|trace|rank)\s*\(\s*\[',
        re.IGNORECASE
    )

    @classmethod
    def diagnose(cls, original_input: str, normalized: str,
                 parse_error: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze input and provide detailed diagnostic information.

        Args:
            original_input: The original user input
            normalized: The normalized form
            parse_error: Optional error message from parser

        Returns:
            Dictionary with:
            - 'category': Error category (e.g., 'matrix_syntax', 'probability')
            - 'message': User-friendly error message
            - 'suggestion': Suggested fix
            - 'details': Technical details for debugging
        """
        result = {
            'category': 'unknown',
            'message': 'Failed to parse expression',
            'suggestion': None,
            'details': parse_error,
            'original': original_input,
            'normalized': normalized
        }

        # Check for malformed matrix syntax
        if cls.MATRIX_MALFORMED.search(original_input):
            result['category'] = 'matrix_syntax'
            result['message'] = 'Matrix literal is malformed (empty or missing elements)'
            result['suggestion'] = (
                'Ensure matrix rows are fully specified. '
                'Example: [[1,2,3], [4,5,6], [7,8,9]]'
            )
            return result

        # Check for unsupported linear algebra command syntax
        if cls.UNSUPPORTED_COMMAND.search(original_input):
            match = cls.UNSUPPORTED_COMMAND.search(original_input)
            cmd = match.group(1) if match else 'command'
            result['category'] = 'linalg_syntax'
            result['message'] = f'Linear algebra function "{cmd}" requires proper matrix format'
            result['suggestion'] = (
                f'Use fully specified matrices. '
                f'Example: {cmd}([[1,2], [3,4]])'
            )
            return result

        # Check for probability/statistics English notation
        if cls.PROBABILITY_NOTATION.search(original_input):
            result['category'] = 'probability_notation'
            result['message'] = 'English probability notation is not yet supported'
            result['suggestion'] = (
                'Use explicit function notation instead. '
                'Example: Instead of "E(X^2) where X ~ Normal(0,1)", '
                'use "E(X**2, (X, Normal(0,1)))" or compute directly.'
            )
            return result

        # Check for distribution with English glue words
        if cls.DISTRIBUTION_NOTATION.search(original_input) and \
           cls.ENGLISH_GLUE.search(original_input):
            result['category'] = 'probability_english'
            result['message'] = 'Natural language probability expressions require explicit notation'
            result['suggestion'] = (
                'Remove English phrases like "where", "given that". '
                'Use: pdf(Normal(0, 1), x) or cdf(Normal(mu, sigma), x)'
            )
            return result

        # Check for English glue words that weren't processed
        if cls.ENGLISH_GLUE.search(normalized):
            match = cls.ENGLISH_GLUE.search(normalized)
            phrase = match.group(1) if match else 'phrase'
            result['category'] = 'english_phrase'
            result['message'] = f'English phrase "{phrase}" could not be converted to mathematical notation'
            result['suggestion'] = (
                'Rewrite using mathematical symbols. '
                'Examples: "for all x" → "ForAll(x, ...)", '
                '"there exists" → "Exists(x, ...)"'
            )
            return result

        # Check for missing multiplication (merged identifiers)
        merged_pattern = re.compile(r'[a-z]{5,}', re.IGNORECASE)
        if merged_pattern.search(normalized):
            match = merged_pattern.search(normalized)
            merged = match.group(0) if match else ''
            # Skip if it's a known function
            known = {'integrate', 'differentiate', 'simplify', 'expand',
                     'factor', 'sqrt', 'Normal', 'Binomial', 'Poisson'}
            if merged.lower() not in {k.lower() for k in known}:
                result['category'] = 'missing_multiplication'
                result['message'] = f'Possible missing multiplication in "{merged}"'
                result['suggestion'] = (
                    'Insert * between multiplied terms. '
                    f'Example: "{merged}" might be "{merged[0]}*{merged[1:]}..."'
                )
                return result

        # Check for assignment vs equation confusion
        if '=' in original_input and '==' not in original_input:
            if 'SympifyError' in str(parse_error) or 'assignment' in str(parse_error).lower():
                result['category'] = 'equation_syntax'
                result['message'] = 'Expression contains "=" which may be interpreted as assignment'
                result['suggestion'] = (
                    'For equations, use Eq(lhs, rhs) or == instead of =. '
                    'Example: Eq(x**2 - 4, 0) or x**2 - 4 == 0'
                )
                return result

        # Check for prime notation issues
        if "'" in original_input and 'unterminated' in str(parse_error).lower():
            result['category'] = 'prime_notation'
            result['message'] = 'Prime notation (derivative) was not properly converted'
            result['suggestion'] = (
                "Use diff() notation instead. "
                "Example: y'(x) → diff(y(x), x), y''(x) → diff(y(x), x, 2)"
            )
            return result

        # Generic fallback with helpful context
        result['category'] = 'parse_error'
        result['message'] = 'Expression could not be parsed'
        if parse_error:
            # Extract meaningful part of error
            if 'sympify' in parse_error.lower():
                result['suggestion'] = (
                    'Check for: missing multiplication (*), '
                    'unsupported notation, or typos in function names.'
                )
            elif 'type' in parse_error.lower():
                result['suggestion'] = (
                    'The expression type is not supported. '
                    'Try simplifying or breaking into smaller parts.'
                )

        return result

    @classmethod
    def format_error(cls, diagnostic: Dict[str, Any], verbose: bool = False) -> str:
        """
        Format a diagnostic result into a user-friendly error message.

        Args:
            diagnostic: Result from diagnose()
            verbose: Include technical details

        Returns:
            Formatted error message string
        """
        lines = [f"Error: {diagnostic['message']}"]

        if diagnostic.get('suggestion'):
            lines.append(f"Suggestion: {diagnostic['suggestion']}")

        if verbose and diagnostic.get('details'):
            lines.append(f"Technical: {diagnostic['details']}")

        return '\n'.join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def safe_normalize(text: str) -> Tuple[str, bool, Optional[str]]:
    """
    Normalize and validate in one call.

    Returns:
        (normalized_text, is_valid, error_message)
    """
    try:
        normalized = normalize_input(text)
        is_valid, error = validate_normalized(normalized)
        return normalized, is_valid, error
    except Exception as e:
        return text, False, str(e)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("INPUT NORMALIZER TEST")
    print("=" * 70)

    test_cases = [
        # Unicode Greek and symbols (using escape sequences for portability)
        ("2\u03c0r\u00b2", "Greek + superscript"),         # 2πr²
        ("\u00bd \u00d7 base \u00d7 height", "Fraction"),  # ½ × base × height
        ("x\u00b2 + y\u00b2", "Superscripts"),             # x² + y²
        ("\u221a9 + \u221b27", "Root symbols"),            # √9 + ∛27
        ("x\u2081 + x\u2082", "Subscripts"),               # x₁ + x₂
        ("5 \u2212 3", "Unicode minus"),                   # 5 − 3
        ("\u221e", "Infinity"),                            # ∞

        # Natural language
        ("x squared plus 2x minus 3", "Natural language"),
        ("the square root of 9", "Square root words"),
        ("2 times 3 plus 4", "Words for operations"),
        ("one half times base times height", "Fraction words"),

        # Common patterns
        ("sin30", "Function without parens"),
        ("2x + 3", "Implicit multiplication"),
        ("2(x+1)", "Number before paren"),
        ("(x)(y)", "Parens next to parens"),

        # Copy-paste artifacts
        ('\u201csmart quotes\u201d', "Smart quotes"),      # "smart quotes"
        ("5\u20133", "En dash as minus"),                  # 5–3
        ("2\u00a0+\u00a03", "Non-breaking spaces"),        # non-breaking spaces

        # Multi-line
        ("x^2\n+ 2x\n- 3", "Multi-line expression"),

        # LaTeX-ish
        ("x^2 + y^2 = z^2", "Caret notation"),

        # Modular arithmetic
        ("a\u2261b(mod n)", "Congruence Unicode"),     # a≡b(mod n)
        ("a equiv b (mod n)", "Congruence text"),
        ("ax\u2261b(modn)", "Congruence no spaces"),   # ax≡b(modn)
        ("5 mod 3", "Simple modulo"),
        ("17 mod 5", "Modulo numbers"),

        # Calculus - Derivatives
        ("dy/dx", "Leibniz notation"),
        ("df/dx", "Leibniz function"),
        ("d/dx sin(x)", "Operator notation"),
        ("d/dx (x^2)", "Operator with parens"),
        ("f'(x)", "Prime notation"),
        ("f''(x)", "Double prime"),
        ("F\u2032(x)", "Unicode prime"),               # F′(x)

        # Calculus - Integrals
        ("\u222b x dx", "Integral symbol"),            # ∫ x dx
        ("integral of x dx", "Natural integral"),
        ("integral of sin(x) dx", "Natural integral fn"),
        ("integrate x^2 from 0 to 1", "Definite integral"),

        # Copy-paste calculus artifacts
        ("x\n2", "Superscript on new line"),
        ("f\n\u2032\n(x)", "Prime on new line"),       # f′(x) split
        ("\u222b\na\nb\nf(x)dx", "Integral bounds on lines"),  # ∫_a^b f(x)dx

        # === NEW: Vector calculus (from second opinion review) ===
        ("grad(f, [x, y])", "Gradient 2D"),
        ("grad(x**2 + y**2, [x, y])", "Gradient expression"),
        ("div([P, Q], [x, y])", "Divergence 2D"),
        ("div([x*y, y*z, z*x], [x, y, z])", "Divergence 3D"),
        ("curl([P, Q, R], [x, y, z])", "Curl 3D"),

        # === NEW: Implicit multiplication edge cases ===
        ("sigmasqrt(2pi)", "sigma*sqrt pattern"),
        ("2sigma", "Coefficient pattern"),
        ("2pi", "Number-greek pattern"),
        ("exp(2x)", "Function with coeff"),

        # === NEW: Prime notation in ODE context ===
        ("y'(x) + y(x) = 0", "First-order ODE"),
        ("y''(x) - 3y'(x) + 2y(x) = 0", "Second-order ODE"),
    ]

    print()
    for expr, desc in test_cases:
        try:
            normalized = normalize_input(expr)
            is_valid, error = validate_normalized(normalized)
            status = "OK" if is_valid else f"WARN: {error}"
            # Safe print
            try:
                print(f"{desc:30} | {expr:25} -> {normalized:30} [{status}]")
            except UnicodeEncodeError:
                safe_expr = expr.encode('ascii', 'replace').decode('ascii')
                print(f"{desc:30} | {safe_expr:25} -> {normalized:30} [{status}]")
        except Exception as e:
            print(f"{desc:30} | ERROR: {e}")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
