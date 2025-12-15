# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0

"""
Convenience API - High-Level User Functions
============================================

High-level convenience functions for symbolic mathematics.
NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import re
from typing import Union, Tuple

from .type_system import Expr, Symbol
from .expression_parser import parse_expr


def symbols(names: str, **assumptions) -> Union[Symbol, Tuple[Symbol, ...]]:
    """
    Create multiple symbols from space or comma-separated string.

    This replaces sympy.symbols.
    """
    name_list = re.split(r'[,\s]+', names.strip())
    if len(name_list) == 1:
        return Symbol(name_list[0], **assumptions)
    return tuple(Symbol(n, **assumptions) for n in name_list)


def diff(expr: Union[Expr, str], var: Union[Symbol, str], n: int = 1) -> Expr:
    """
    Differentiate expression.

    This replaces sympy.diff.
    """
    if isinstance(expr, str):
        expr = parse_expr(expr)
    if isinstance(var, str):
        var = Symbol(var)

    result = expr
    for _ in range(n):
        result = result.diff(var)
    return result.simplify()


def simplify(expr: Union[Expr, str]) -> Expr:
    """
    Simplify expression.

    This replaces sympy.simplify.
    """
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return expr.simplify()


def expand(expr: Union[Expr, str]) -> Expr:
    """
    Expand expression (polynomial expansion).

    This replaces sympy.expand.
    """
    from .simplification_engine import expand_expression
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return expand_expression(expr)


def factor(expr: Union[Expr, str]) -> Expr:
    """
    Factor expression.

    This replaces sympy.factor.
    """
    from .simplification_engine import factor_expression
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return factor_expression(expr)


__all__ = [
    'symbols',
    'diff',
    'simplify',
    'expand',
    'factor',
]
