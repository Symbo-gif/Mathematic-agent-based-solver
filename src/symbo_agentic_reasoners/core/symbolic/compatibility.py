# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0
"""
SymPy Compatibility Layer
==========================

This module provides compatibility stubs for code expecting SymPy.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
from typing import Set, Union
from .expr_types import Expr
from .numeric_types import Integer


def _ensure_expr(obj):
    """Import and forward to utilities._ensure_expr to avoid circular imports."""
    from .utilities import _ensure_expr as util_ensure_expr
    return util_ensure_expr(obj)


class Eq(Expr):
    """Equation class representing lhs = rhs (replaces sympy.Eq)."""

    def __init__(self, lhs, rhs=None):
        self.lhs = _ensure_expr(lhs) if lhs is not None else Integer(0)
        self.rhs = _ensure_expr(rhs) if rhs is not None else Integer(0)

    def __repr__(self):
        return f"Eq({self.lhs}, {self.rhs})"

    def __str__(self):
        return f"{self.lhs} = {self.rhs}"

    def __eq__(self, other):
        if isinstance(other, Eq):
            return self.lhs == other.lhs and self.rhs == other.rhs
        return False

    def __hash__(self):
        return hash((type(self).__name__, hash(self.lhs), hash(self.rhs)))

    @property
    def free_symbols(self) -> Set:
        return self.lhs.free_symbols | self.rhs.free_symbols

    def subs(self, substitutions):
        return Eq(self.lhs.subs(substitutions), self.rhs.subs(substitutions))

    def diff(self, var):
        return Eq(self.lhs.diff(var), self.rhs.diff(var))

    def evalf(self, n=15):
        return Eq(self.lhs.evalf(n), self.rhs.evalf(n))

    def simplify(self):
        return Eq(self.lhs.simplify(), self.rhs.simplify())

    def to_latex(self):
        return f"{self.lhs.to_latex()} = {self.rhs.to_latex()}"


# Additional compatibility classes
class core:
    """Stub for sympy.core module."""
    class relational:
        Relational = Eq


__all__ = [
    'Eq',
    'core',
]
