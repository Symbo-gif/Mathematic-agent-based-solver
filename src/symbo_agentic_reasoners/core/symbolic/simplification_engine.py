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
Simplification Engine - Advanced Simplification Rules
======================================================

Advanced simplification and transformation rules.
NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import re
from typing import Union

from .type_system import Expr, Integer
from .composite_operations import Add, Mul, Pow
from .function_library import Function
from .expression_parser import parse_expr


def expand_expression(expr: Expr) -> Expr:
    """
    Expand expression (polynomial expansion).

    Handles:
    - (a + b)**n -> binomial expansion
    - (a + b) * (c + d) -> distribution
    - Nested expansions
    """
    def _expand_internal(e: Expr) -> Expr:
        """Recursively expand expression."""
        # Handle Pow with integer exponent and Add base: (a + b)**n
        if isinstance(e, Pow):
            base = _expand_internal(e.base)
            exp = e.exp

            # Check if exponent is a positive integer
            if isinstance(exp, Integer) and exp.value >= 2:
                n = exp.value
                if isinstance(base, Add):
                    # Binomial/multinomial expansion
                    result = base
                    for _ in range(n - 1):
                        result = _expand_mul(Mul(result, base))
                    return result
                else:
                    return Pow(base, exp)
            else:
                return Pow(base, exp)

        # Handle Mul: expand and distribute
        if isinstance(e, Mul):
            return _expand_mul(e)

        # Handle Add: expand each term
        if isinstance(e, Add):
            terms = [_expand_internal(arg) for arg in e.args]
            return Add(*terms).simplify()

        # Handle functions: expand arguments
        if isinstance(e, Function):
            expanded_args = [_expand_internal(arg) for arg in e.args]
            return type(e)(*expanded_args)

        return e

    def _expand_mul(mul_expr: Mul) -> Expr:
        """Expand a multiplication, distributing over addition."""
        args = list(mul_expr.args)
        if len(args) == 0:
            return Integer(1)
        if len(args) == 1:
            return _expand_internal(args[0])

        # Expand first two args
        left = _expand_internal(args[0])
        right = _expand_internal(args[1])

        # Distribute: (a + b) * (c + d) = ac + ad + bc + bd
        if isinstance(left, Add) and isinstance(right, Add):
            terms = []
            for l_term in left.args:
                for r_term in right.args:
                    terms.append(Mul(l_term, r_term).simplify())
            result = Add(*terms).simplify()
        elif isinstance(left, Add):
            terms = [Mul(l_term, right).simplify() for l_term in left.args]
            result = Add(*terms).simplify()
        elif isinstance(right, Add):
            terms = [Mul(left, r_term).simplify() for r_term in right.args]
            result = Add(*terms).simplify()
        else:
            result = Mul(left, right).simplify()

        # If more args remain, continue expanding
        if len(args) > 2:
            rest = Mul(*args[2:])
            return _expand_mul(Mul(result, rest))

        return result

    return _expand_internal(expr)


def factor_expression(expr: Union[Expr, str]) -> Expr:
    """
    Factor expression.

    Handles:
    - Difference of squares: a² - b² = (a-b)(a+b)
    - Simple quadratics with rational roots
    """
    # Convert to string if needed
    if isinstance(expr, Expr):
        expr_str = str(expr)
    else:
        expr_str = str(expr)
        expr = parse_expr(expr_str)

    # Normalize the string for factor_polynomial
    normalized = expr_str.replace(' ', '')
    normalized = re.sub(r'(\d+)\*1\b', r'\1', normalized)  # 1*1 -> 1
    normalized = re.sub(r'\b1\*(\d+)', r'\1', normalized)  # 1*n -> n
    normalized = re.sub(r'-1\*1', '-1', normalized)  # -1*1 -> -1
    normalized = re.sub(r'--', '+', normalized)  # -- -> +

    # Reorder to standard form
    dos_match = re.match(r'^-(\d+)\+(\w+)\*\*2$', normalized)
    if dos_match:
        n, var = dos_match.groups()
        normalized = f"{var}**2-{n}"

    sum_match = re.match(r'^(\d+)\+(\w+)\*\*2$', normalized)
    if sum_match:
        n, var = sum_match.groups()
        normalized = f"{var}**2+{n}"

    # Try to use native_calculus factor_polynomial
    try:
        from symbo_agentic_reasoners.core.calculus import factor_polynomial
        success, factored = factor_polynomial(normalized)
        if success:
            return parse_expr(factored)
    except Exception:
        pass

    # Fallback: return simplified expression
    return expr.simplify()


__all__ = [
    'expand_expression',
    'factor_expression',
]
