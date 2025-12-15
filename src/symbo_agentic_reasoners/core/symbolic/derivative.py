# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0
"""
Derivative - Symbolic Derivative Representation
================================================

This module provides the Derivative class for unevaluated derivatives.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
from typing import Set, Union
from .expr_types import Expr
from .symbol import Symbol


class Derivative(Expr):
    """Symbolic derivative."""

    def __init__(self, expr: Expr, var: Symbol):
        self.expr = expr
        self.var = var
        self._hash_cache = hash(('Derivative', hash(expr), hash(var)))

    def __repr__(self) -> str:
        return f"Derivative({self.expr!r}, {self.var!r})"

    def __str__(self) -> str:
        return f"d/d{self.var}({self.expr})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Derivative):
            return self.expr == other.expr and self.var == other.var
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self) -> Set[Symbol]:
        return self.expr.free_symbols | {self.var}

    def subs(self, *args_in, **kwargs) -> Expr:
        """Substitute symbols. Supports both subs({x: val}) and subs(x, val)."""
        if len(args_in) == 1 and isinstance(args_in[0], dict):
            substitutions = args_in[0]
        elif len(args_in) == 2:
            substitutions = {args_in[0]: args_in[1]}
        else:
            substitutions = kwargs
        return Derivative(self.expr.subs(substitutions), self.var)

    def diff(self, var: Symbol) -> Expr:
        return Derivative(self, var)

    def simplify(self) -> Expr:
        return self

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        return self

    def to_latex(self) -> str:
        return rf'\frac{{d}}{{d{self.var.to_latex()}}}\left({self.expr.to_latex()}\right)'


__all__ = [
    'Derivative',
]
