# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0

"""
SymPy Compatibility Layer
==========================

SymPy API compatibility stubs and constants.
NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
from typing import Set

from .type_system import Expr, Symbol, Integer, Float, _ensure_expr
from .expression_parser import parse_expr


# =============================================================================
# SYMPY COMPATIBILITY STUBS
# =============================================================================

class SympifyError(Exception):
    """Exception for parsing errors (replaces sympy.SympifyError)."""
    pass


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
    def free_symbols(self) -> Set[Symbol]:
        return self.lhs.free_symbols | self.rhs.free_symbols

    def subs(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], dict):
            substitutions = args[0]
        elif len(args) == 2:
            substitutions = {args[0]: args[1]}
        else:
            substitutions = kwargs
        return Eq(self.lhs.subs(substitutions), self.rhs.subs(substitutions))

    def diff(self, var):
        return Eq(self.lhs.diff(var), self.rhs.diff(var))

    def evalf(self, n=15):
        return Eq(self.lhs.evalf(n), self.rhs.evalf(n))

    def simplify(self):
        return Eq(self.lhs.simplify(), self.rhs.simplify())

    def to_latex(self):
        return f"{self.lhs.to_latex()} = {self.rhs.to_latex()}"


def preorder_traversal(expr):
    """Generator for preorder traversal of expression tree (stub)."""
    if isinstance(expr, str):
        expr = parse_expr(expr)
    yield expr
    if hasattr(expr, 'args'):
        for arg in getattr(expr, 'args', []):
            yield from preorder_traversal(arg)


def together(expr):
    """Combine fractions (stub - returns expr as-is)."""
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return expr


def fraction(expr):
    """Extract numerator and denominator (stub)."""
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return (expr, Integer(1))


def arg(expr):
    """Complex argument (stub - returns 0)."""
    return Integer(0)


def expand_complex(expr):
    """Expand complex expression (stub - returns expr as-is)."""
    if isinstance(expr, str):
        expr = parse_expr(expr)
    return expr


def solve(expr, var=None, dict=False):
    """
    Solve equation for variable (stub).

    Returns empty list or dict when full solution not available.
    """
    if isinstance(expr, str):
        expr = parse_expr(expr)
    if dict:
        return []
    return []


def groebner(equations, variables, order='grlex'):
    """Groebner basis computation (stub - returns equations as-is)."""
    return equations


# Additional compatibility classes
class core:
    """Stub for sympy.core module."""
    class relational:
        Relational = Eq


# =============================================================================
# SPECIAL CONSTANTS
# =============================================================================

# Pre-defined symbols for common constants
pi = Symbol('pi')
E = Symbol('E')
I = Symbol('I')  # Imaginary unit
oo = Float(float('inf'))  # Infinity


# =============================================================================
# FUNCTION ALIASES (lowercase)
# =============================================================================

from .function_library import Sin, Cos, Tan, Exp, Log, Sqrt

sin = Sin
cos = Cos
tan = Tan
exp = Exp
log = Log


def sqrt(x):
    """Square root function."""
    return Sqrt(x)


__all__ = [
    # Compatibility classes
    'Eq',
    'SympifyError',
    'core',

    # Compatibility functions
    'preorder_traversal',
    'together',
    'fraction',
    'arg',
    'expand_complex',
    'solve',
    'groebner',

    # Constants
    'pi', 'E', 'I', 'oo',

    # Function aliases
    'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',
]
