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
Unicode Conversion Handler
===========================

Handles conversion of Unicode mathematical symbols to ASCII equivalents.
Includes Greek letters, special symbols, superscripts, subscripts, fractions,
operators, dashes, quotes, and invisible characters.
"""

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
# UNICODE NORMALIZATION FUNCTION
# =============================================================================

def normalize_unicode(text: str) -> str:
    """
    Convert all Unicode math symbols to ASCII equivalents.

    This is the first step - convert special characters before any parsing.

    Args:
        text: Input text with Unicode characters

    Returns:
        Text with all Unicode math symbols converted to ASCII
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
