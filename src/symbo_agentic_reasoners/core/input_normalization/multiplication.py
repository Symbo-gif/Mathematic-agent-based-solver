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
Multiplication Handler
======================

Handles implicit multiplication insertion and spurious multiplication removal.
Includes patterns for coefficients, Greek letters, powers, and function names.
"""

import re
from typing import Set


# =============================================================================
# IMPLICIT MULTIPLICATION PATTERNS
# =============================================================================

# Function names that should NOT have * inserted before their parenthesis
# This is used in preprocess_function_notation() to protect function calls
PROTECTED_FUNCTIONS: Set[str] = {
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

# Patterns for detecting missing * in common cases
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

    Args:
        text: Input text

    Returns:
        Text with implicit multiplication inserted
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
        """Perform add mul between letters operation.

        Args:
        match: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.add_mul_between_letters(...)
        """
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

    Args:
        text: Input text with potential spurious multiplication

    Returns:
        Text with spurious multiplication removed
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


def add_implicit_multiplication(text: str) -> str:
    """
    Add * for implicit multiplication.

    Examples:
        2x → 2*x
        2(x+1) → 2*(x+1)
        (x)(y) → (x)*(y)
        2pi → 2*pi
        pi r → pi*r

    Args:
        text: Input text

    Returns:
        Text with implicit multiplication added
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
