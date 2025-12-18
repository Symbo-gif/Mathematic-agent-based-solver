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
        self.args = (self.lhs, self.rhs)

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
        """Get all free symbols from both sides of the equation.

        Returns:
            Union of free symbols from lhs and rhs
        """
        return self.lhs.free_symbols | self.rhs.free_symbols

    def subs(self, *args, **kwargs):
        """Substitute symbols with values or expressions.

                Recursively substitutes symbols throughout the expression.
                Supports dict, positional, and keyword argument forms.

                Args:

                Returns:
                    New expression with substitutions applied

                Example:
                    >>> x, y = Symbol('x'), Symbol('y')
                >>> expr.subs(x, y)
                # Returns expression with x replaced by y

                """
        if len(args) == 1 and isinstance(args[0], dict):
            substitutions = args[0]
        elif len(args) == 2:
            substitutions = {args[0]: args[1]}
        else:
            substitutions = kwargs
        return Eq(self.lhs.subs(substitutions), self.rhs.subs(substitutions))

    def diff(self, var):
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx eq(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Eq(x**2).diff(x)
                # Returns derivative expression

                """
        return Eq(self.lhs.diff(var), self.rhs.diff(var))

    def evalf(self, n=15):
        """Numerically evaluate the expression.

                Evaluates the function numerically if all arguments are numeric.
                Returns symbolic form if evaluation fails.

                Args:
                    n: [Description needed]

                Returns:
                    Numerical value (float) if evaluable, otherwise symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Eq(2).evalf()
                # Returns numerical result

                """
        return Eq(self.lhs.evalf(n), self.rhs.evalf(n))

    def simplify(self):
        """Simplify the expression algebraically.

                Applies simplification rules specific to eq.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Eq(Integer(0)).simplify()
                # Returns simplified form

                """
        return Eq(self.lhs.simplify(), self.rhs.simplify())

    def to_latex(self):
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Eq(Symbol('x')).to_latex()
                '\\eq\\left(x\\right)'

                """
        return f"{self.lhs.to_latex()} = {self.rhs.to_latex()}"


class Implies(Expr):
    """Logical implication class representing A → B (replaces sympy.Implies)."""

    def __init__(self, antecedent, consequent):
        self.antecedent = _ensure_expr(antecedent)
        self.consequent = _ensure_expr(consequent)
        self.args = (self.antecedent, self.consequent)

    def __repr__(self):
        return f"Implies({self.antecedent}, {self.consequent})"

    def __str__(self):
        return f"{self.antecedent} → {self.consequent}"

    def __eq__(self, other):
        if isinstance(other, Implies):
            return self.antecedent == other.antecedent and self.consequent == other.consequent
        return False

    def __hash__(self):
        return hash((type(self).__name__, hash(self.antecedent), hash(self.consequent)))

    @property
    def free_symbols(self) -> Set[Symbol]:
        """Get all free symbols from antecedent and consequent.

        Returns:
            Union of free symbols from both parts of implication
        """
        return self.antecedent.free_symbols | self.consequent.free_symbols

    def subs(self, *args, **kwargs):
        """Substitute symbols with values or expressions.

                Recursively substitutes symbols throughout the expression.
                Supports dict, positional, and keyword argument forms.

                Args:

                Returns:
                    New expression with substitutions applied

                Example:
                    >>> x, y = Symbol('x'), Symbol('y')
                >>> expr.subs(x, y)
                # Returns expression with x replaced by y

                """
        if len(args) == 1 and isinstance(args[0], dict):
            substitutions = args[0]
        elif len(args) == 2:
            substitutions = {args[0]: args[1]}
        else:
            substitutions = kwargs
        return Implies(
            self.antecedent.subs(substitutions),
            self.consequent.subs(substitutions)
        )

    def to_latex(self):
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Implies(Symbol('x')).to_latex()
                '\\implies\\left(x\\right)'

                """
        return f"{self.antecedent.to_latex()} \\Rightarrow {self.consequent.to_latex()}"


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
    'Implies',
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
