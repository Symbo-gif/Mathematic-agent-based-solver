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
Calculus Utilities
==================

Shared utility functions used across calculus specialists.

Functions:
- _get_symbols: Extract all symbol names from an expression
- _evaluate_at_numeric: Numerically evaluate expression at a point
- _try_evaluate_const: Try to evaluate expression as a constant
- _simplify_output: Clean up output string representation
- _contains_var: Check if expression contains a variable
- _subtract_one, _add_one: Arithmetic helpers
"""

import re
import math
import logging
from typing import Optional, Set
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func

logger = logging.getLogger(__name__)

def _get_symbols(expr: Expr) -> set:
    """Get all symbol names in an expression."""
    symbols = set()

    if isinstance(expr, Sym):
        symbols.add(expr.name)
    elif isinstance(expr, Num):
        pass
    elif isinstance(expr, Neg):
        symbols.update(_get_symbols(expr.arg))
    elif isinstance(expr, Add):
        for term in expr.terms:
            symbols.update(_get_symbols(term))
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            symbols.update(_get_symbols(factor))
    elif isinstance(expr, Pow):
        symbols.update(_get_symbols(expr.base))
        symbols.update(_get_symbols(expr.exp))
    elif isinstance(expr, Func):
        symbols.update(_get_symbols(expr.arg))

    return symbols


def _evaluate_at_numeric(expr: Expr, var: str, value: float) -> float:
    """Evaluate expression at a numeric value - returns float or raises."""
    import math

    if isinstance(expr, Num):
        return float(expr.value)
    elif isinstance(expr, Sym):
        if expr.name == var:
            return value
        else:
            raise ValueError(f"Unknown symbol: {expr.name}")
    elif isinstance(expr, Neg):
        return -_evaluate_at_numeric(expr.arg, var, value)
    elif isinstance(expr, Add):
        return sum(_evaluate_at_numeric(t, var, value) for t in expr.terms)
    elif isinstance(expr, Mul):
        result = 1.0
        for f in expr.factors:
            result *= _evaluate_at_numeric(f, var, value)
        return result
    elif isinstance(expr, Pow):
        # Handle special case: (-x)**n when n is even integer
        # Parser sometimes interprets -x**n as (-x)**n, but user means -(x**n)
        # For numeric evaluation, (-x)**n = (-1)**n * x**n
        # If n is even: (-x)**n = x**n
        # If n is odd: (-x)**n = -(x**n)
        base = _evaluate_at_numeric(expr.base, var, value)
        exp = _evaluate_at_numeric(expr.exp, var, value)
        try:
            return base ** exp
        except (ValueError, OverflowError):
            # Handle negative base with non-integer exponent
            if base < 0 and exp != int(exp):
                raise ValueError(f"Cannot compute {base}**{exp} (negative base with non-integer exponent)")
            raise
    elif isinstance(expr, Func):
        arg = _evaluate_at_numeric(expr.arg, var, value)
        func_map = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'exp': math.exp, 'ln': math.log, 'log': math.log,
            'sqrt': math.sqrt, 'abs': abs, 'Abs': abs,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
        }
        if expr.name in func_map:
            return func_map[expr.name](arg)
        raise ValueError(f"Unknown function: {expr.name}")
    else:
        raise ValueError(f"Cannot evaluate: {type(expr)}")



def _try_evaluate_const(expr: Expr) -> Optional[float]:
    """Try to evaluate an expression as a constant."""
    import math

    if isinstance(expr, Num):
        return float(expr.value)
    elif isinstance(expr, Neg):
        inner = _try_evaluate_const(expr.arg)
        return -inner if inner is not None else None
    elif isinstance(expr, Mul):
        result = 1.0
        for factor in expr.factors:
            val = _try_evaluate_const(factor)
            if val is None:
                return None
            result *= val
        return result
    elif isinstance(expr, Add):
        result = 0.0
        for term in expr.terms:
            val = _try_evaluate_const(term)
            if val is None:
                return None
            result += val
        return result
    elif isinstance(expr, Pow):
        base_val = _try_evaluate_const(expr.base)
        exp_val = _try_evaluate_const(expr.exp)
        if base_val is not None and exp_val is not None:
            return base_val ** exp_val
        return None
    elif isinstance(expr, Func):
        if expr.name == 'sqrt':
            arg_val = _try_evaluate_const(expr.arg)
            if arg_val is not None:
                return math.sqrt(arg_val)
        elif expr.name == 'pi':
            return math.pi
    elif isinstance(expr, Sym):
        if expr.name == 'pi':
            return math.pi
        elif expr.name == 'e' or expr.name == 'E':
            return math.e
    return None



def _simplify_output(s: str) -> str:
    """Clean up output string."""
    # FIRST: Convert x**-1 to (1/x) BEFORE other cleanup
    # This must happen first so 1* removal doesn't break **-1
    def fix_negative_one_power(match):
        """Perform fix negative one power operation.

        Args:
        match: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.fix_negative_one_power(...)
        """
        var = match.group(1)
        return f"(1/{var})"

    s = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\*\*-1\b', fix_negative_one_power, s)

    # Remove 1* prefix (but not after ** or inside numbers)
    s = re.sub(r'(?<!\*)\b1\*', '', s)
    # Remove *1 suffix
    s = re.sub(r'\*1\b', '', s)
    # Clean up **1
    s = re.sub(r'\*\*1\b', '', s)
    # Clean up 0 + or + 0 (but not 0.5 + or + 0.5)
    s = re.sub(r'(?<![.\d])0 \+ ', '', s)
    s = re.sub(r' \+ 0(?![.\d])', '', s)
    # Clean up double negatives
    s = re.sub(r'--', '', s)

    # Fix patterns like x*(1/a) to x/a
    s = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\*\(1/([a-zA-Z_][a-zA-Z0-9_]*)\)', r'\1/\2', s)

    # Clean up (1/a)* prefix to be clearer: (1/a)*atan(...) → atan(...)/a
    def fix_one_over_times(match):
        """Perform fix one over times operation.

        Args:
        match: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.fix_one_over_times(...)
        """
        denom = match.group(1)
        rest = match.group(2)
        return f"{rest}/{denom}"

    s = re.sub(r'\(1/([a-zA-Z_][a-zA-Z0-9_]*)\)\*([a-zA-Z_][a-zA-Z0-9_]*\([^)]+\))', fix_one_over_times, s)

    return s



def _contains_var(expr: Expr, var: str) -> bool:
    """Check if expression contains the variable."""
    if isinstance(expr, Num):
        return False
    if isinstance(expr, Sym):
        return expr.name == var
    if isinstance(expr, Neg):
        return _contains_var(expr.arg, var)
    if isinstance(expr, Add):
        return any(_contains_var(t, var) for t in expr.terms)
    if isinstance(expr, Mul):
        return any(_contains_var(f, var) for f in expr.factors)
    if isinstance(expr, Pow):
        return _contains_var(expr.base, var) or _contains_var(expr.exp, var)
    if isinstance(expr, Func):
        return _contains_var(expr.arg, var)
    return False


def _subtract_one(expr: Expr) -> Expr:
    """Subtract 1 from expression (for power rule)."""
    from .ast_types import add, Num
    if isinstance(expr, Num):
        return Num(expr.value - 1)
    return add(expr, Num(-1))


def _add_one(expr: Expr) -> Expr:
    """Add 1 to expression."""
    from .ast_types import add, Num
    if isinstance(expr, Num):
        return Num(expr.value + 1)
    return add(expr, Num(1))


def native_trig_simplify(expr_str: str) -> str:
    """
    Native trigonometric simplification for integer multiples of π.

    Rules:
        sin(n*π) = 0 for integer n
        cos(n*π) = (-1)^n for integer n
        sin(n*π)^2 = 0
        cos(n*π)^2 = 1
        sin(π/2 + n*π) = (-1)^n
        cos(π/2 + n*π) = 0

    This avoids SymPy for simple trig identities.

    Args:
        expr_str: Expression to simplify

    Returns:
        Simplified expression string
    """
    result = expr_str

    # sin(pi*n) or sin(n*pi) → 0 (for integer n)
    # Pattern matches sin(pi*n), sin(n*pi), sin(pi*integer)
    sin_pi_n_patterns = [
        r'sin\(pi\*[a-zA-Z_]\w*\)',  # sin(pi*n)
        r'sin\([a-zA-Z_]\w*\*pi\)',  # sin(n*pi)
        r'sin\(pi\)',                 # sin(pi)
        r'sin\(2\*pi\)',              # sin(2*pi)
        r'sin\(3\*pi\)',              # sin(3*pi)
        r'sin\(-pi\)',                # sin(-pi)
        r'sin\(-\d+\*pi\)',           # sin(-n*pi)
        r'sin\(\d+\*pi\)',            # sin(n*pi) where n is digit
    ]

    for pattern in sin_pi_n_patterns:
        result = re.sub(pattern, '0', result)

    # sin(pi*n)**2 → 0
    sin_sq_patterns = [
        r'sin\(pi\*[a-zA-Z_]\w*\)\*\*2',
        r'sin\([a-zA-Z_]\w*\*pi\)\*\*2',
        r'sin\(\d+\*pi\)\*\*2',
        r'sin\(pi\)\*\*2',
    ]

    for pattern in sin_sq_patterns:
        result = re.sub(pattern, '0', result)

    # sin(pi*n/2)**2 - depends on parity of n
    # For general n: sin(pi*n/2) = 0 when n is even, ±1 when n is odd
    # sin(pi*n/2)**2 = 0 when n is even, 1 when n is odd
    # Using identity: sin²(x) = (1 - cos(2x))/2
    # sin(pi*n/2)**2 = (1 - cos(pi*n))/2 = (1 - (-1)^n)/2
    # This is a valid symbolic simplification

    # Handle sin(pi/2) = 1, so sin(pi/2)**2 = 1
    result = re.sub(r'sin\(pi/2\)\*\*2', '1', result)

    # sin(pi*n/2)**2 → (1 - (-1)**n)/2 (parity-dependent form)
    # This is bounded [0,1] and equals 0 for even n, 1 for odd n
    sin_half_pi_n_sq_patterns = [
        (r'sin\(pi\*([a-zA-Z_]\w*)/2\)\*\*2', r'(1 - (-1)**\1)/2'),  # sin(pi*n/2)**2
        (r'sin\(([a-zA-Z_]\w*)\*pi/2\)\*\*2', r'(1 - (-1)**\1)/2'),  # sin(n*pi/2)**2
    ]
    for pattern, replacement in sin_half_pi_n_sq_patterns:
        result = re.sub(pattern, replacement, result)

    # sin(3*pi/2) = -1, so sin(3*pi/2)**2 = 1
    result = re.sub(r'sin\(3\*pi/2\)\*\*2', '1', result)

    # cos(pi) = -1, cos(2*pi) = 1, etc.
    result = re.sub(r'cos\(pi\)', '(-1)', result)
    result = re.sub(r'cos\(2\*pi\)', '1', result)
    result = re.sub(r'cos\(-pi\)', '(-1)', result)

    # cos(2*pi*n) = 1 for any integer n (full rotations)
    cos_2pi_n_patterns = [
        r'cos\(2\*pi\*[a-zA-Z_]\w*\)',  # cos(2*pi*n)
        r'cos\([a-zA-Z_]\w*\*2\*pi\)',  # cos(n*2*pi)
    ]
    for pattern in cos_2pi_n_patterns:
        result = re.sub(pattern, '1', result)

    # cos(pi*n)**2 → 1 (since cos(nπ) = ±1)
    cos_sq_patterns = [
        r'cos\(pi\*[a-zA-Z_]\w*\)\*\*2',
        r'cos\([a-zA-Z_]\w*\*pi\)\*\*2',
        r'cos\(\d+\*pi\)\*\*2',
        r'cos\(pi\)\*\*2',
    ]

    for pattern in cos_sq_patterns:
        result = re.sub(pattern, '1', result)

    # sin(pi/2) = 1, cos(pi/2) = 0
    result = re.sub(r'sin\(pi/2\)', '1', result)
    result = re.sub(r'cos\(pi/2\)', '0', result)

    # tan(pi*n) = 0 for integer n (where defined)
    tan_pi_n_patterns = [
        r'tan\(pi\*[a-zA-Z_]\w*\)',
        r'tan\([a-zA-Z_]\w*\*pi\)',
        r'tan\(\d+\*pi\)',
        r'tan\(pi\)',
    ]

    for pattern in tan_pi_n_patterns:
        result = re.sub(pattern, '0', result)

    # Clean up: 0**2 → 0, 1**2 → 1
    result = re.sub(r'0\*\*2', '0', result)
    result = re.sub(r'1\*\*2', '1', result)

    # Clean up multiplication by 0
    result = re.sub(r'\*0(?!\d)', '*0', result)  # Keep *0 for now, could simplify more

    return result
