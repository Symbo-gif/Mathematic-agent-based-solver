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
Pattern Applier
===============

Applies various mathematical pattern transformations:
- Modular arithmetic patterns (congruence notation)
- Derivative patterns (Leibniz, prime, operator notation)
- Integral patterns (symbol and natural language)
- Natural language word patterns
"""

import re
from typing import List, Tuple


# =============================================================================
# MODULAR ARITHMETIC PATTERNS
# =============================================================================

# These patterns convert congruence notation to SymPy Mod() calls
# Must be applied BEFORE implicit multiplication to avoid mangling "mod"
MODULAR_PATTERNS: List[Tuple[str, str]] = [
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
# DERIVATIVE PATTERNS
# =============================================================================

# Derivative notation patterns → diff() calls
# Applied after copy-paste cleanup but before other processing
DERIVATIVE_PATTERNS: List[Tuple[str, str]] = [
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


# =============================================================================
# INTEGRAL PATTERNS
# =============================================================================

# Integral notation patterns → integrate() calls
INTEGRAL_PATTERNS: List[Tuple[str, str]] = [
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
INTEGRAL_NATURAL_PATTERNS: List[Tuple[str, str]] = [
    # Natural language: integral of f(x) with respect to x (most specific first)
    (r'\bintegral\s+of\s+(.+?)\s+with\s+respect\s+to\s+(\w+)', r'integrate(\1, \2)'),

    # Natural language: integral of f(x) dx
    (r'\bintegral\s+of\s+(.+?)\s+d(\w+)\b', r'integrate(\1, \2)'),

    # Simple: integral f(x) dx (no 'of') - use negative lookahead to avoid matching 'of'
    (r'\bintegral\s+(?!of\s)(.+?)\s+d(\w+)\b', r'integrate(\1, \2)'),
]


# =============================================================================
# NATURAL LANGUAGE PATTERNS
# =============================================================================

# Common word patterns → math expressions
WORD_PATTERNS: List[Tuple[str, str]] = [
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


# =============================================================================
# PATTERN APPLICATION FUNCTIONS
# =============================================================================

def apply_modular_patterns(text: str) -> str:
    """
    Convert modular arithmetic notation to SymPy Mod() calls.

    This MUST be called BEFORE implicit multiplication is applied,
    otherwise 'mod' gets split into m*o*d.

    Examples:
        a≡b(mod n) → Mod(a, n) == Mod(b, n)
        ax≡b(modn) → Mod(ax, n) == Mod(b, n)
        5 mod 3 → Mod(5, 3)

    Args:
        text: Input text

    Returns:
        Text with modular patterns applied
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

    Args:
        text: Input text

    Returns:
        Text with derivative patterns applied
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

    Args:
        text: Input text

    Returns:
        Text with integral patterns applied
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

    Args:
        text: Input text

    Returns:
        Text with word patterns applied
    """
    result = text

    for pattern, replacement in WORD_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Clean up space after function open parens: "sqrt( x)" → "sqrt(x)"
    result = re.sub(r'(\w+\()\s+', r'\1', result)

    return result
