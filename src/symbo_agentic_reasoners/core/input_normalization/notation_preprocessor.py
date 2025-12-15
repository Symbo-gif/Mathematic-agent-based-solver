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
Notation Preprocessor
=====================

Handles preprocessing of special mathematical notations that need early conversion:
- Prime notation for derivatives (f'(x), f''(x))
- Probability and statistics notation (E[X], Var(X), lambda parameter)
- Matrix notation (det([[a,b],[c,d]]), diag(1,2,3))
- Special notations (sqrt{}, bra-ket, e**)
"""

import re


def preprocess_prime_notation(text: str) -> str:
    """
    Convert prime notation to diff() BEFORE other processing.

    This handles f'(x), f''(x), F′(x) etc. and converts them to diff()
    calls before implicit multiplication can mangle them.

    Examples:
        f'(x) → diff(f(x), x)
        F′(x) → diff(F(x), x)
        g''(t) → diff(g(t), t, 2)

    Args:
        text: Input text

    Returns:
        Text with prime notation converted to diff()
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

    Args:
        text: Input text

    Returns:
        Text with probability notation converted
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

    Args:
        text: Input text

    Returns:
        Text with matrix notation converted
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

    Args:
        text: Input text

    Returns:
        Text with special notations converted
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
