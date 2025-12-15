# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0
"""
Simplification Operations - simplify, expand, factor
=====================================================

This module provides expression simplification and manipulation functions.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import re as _re
from typing import Union
from .expr_types import Expr
from .numeric_types import Integer
from .operations import Add, Mul, Pow
from .functions import Function


def simplify(expr: Union[Expr, str]) -> Expr:
    """
    Simplify expression.

    This replaces sympy.simplify.
    """
    from .parsing import parse_expr
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return expr.simplify()


def expand(expr: Union[Expr, str]) -> Expr:
    """
    Expand expression (polynomial expansion).

    This replaces sympy.expand.

    Handles:
    - (a + b)**n -> binomial expansion
    - (a + b) * (c + d) -> distribution
    - Nested expansions
    """
    from .parsing import parse_expr

    if isinstance(expr, str):
        expr = parse_expr(expr)

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


def factor(expr: Union[Expr, str]) -> Expr:
    """
    Factor expression.

    Handles:
    - Difference of squares: a² - b² = (a-b)(a+b)
    - Simple quadratics with rational roots
    """
    from .parsing import parse_expr

    # Convert to string if needed
    if isinstance(expr, Expr):
        expr_str = str(expr)
    else:
        expr_str = str(expr)
        expr = parse_expr(expr_str)

    # Normalize the string for factor_polynomial
    # Remove spaces and clean up patterns like "1*1" -> "1", " - " -> "-"
    normalized = expr_str.replace(' ', '')
    normalized = _re.sub(r'(\d+)\*1\b', r'\1', normalized)  # 1*1 -> 1
    normalized = _re.sub(r'\b1\*(\d+)', r'\1', normalized)  # 1*n -> n
    normalized = _re.sub(r'-1\*1', '-1', normalized)  # -1*1 -> -1
    normalized = _re.sub(r'--', '+', normalized)  # -- -> +

    # Reorder to standard form: put highest power term first
    # Pattern: -n+x**2 -> x**2-n (difference of squares form)
    dos_match = _re.match(r'^-(\d+)\+(\w+)\*\*2$', normalized)
    if dos_match:
        n, var = dos_match.groups()
        normalized = f"{var}**2-{n}"

    # Pattern: n+x**2 -> x**2+n (sum form)
    sum_match = _re.match(r'^(\d+)\+(\w+)\*\*2$', normalized)
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


def together(expr: Union[Expr, str]) -> Expr:
    """Combine fractions (stub - returns expr as-is)."""
    from .parsing import parse_expr
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return expr


def fraction(expr: Union[Expr, str]) -> tuple:
    """Extract numerator and denominator (stub)."""
    from .parsing import parse_expr
    if isinstance(expr, str):
        expr = parse_expr(expr)
    # Simple case - return (expr, 1) for now
    return (expr, Integer(1))


def expand_complex(expr: Union[Expr, str]) -> Expr:
    """Expand complex expression (stub - returns expr as-is)."""
    from .parsing import parse_expr
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return expr


__all__ = [
    'simplify',
    'expand',
    'factor',
    'together',
    'fraction',
    'expand_complex',
]
