# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0
"""
Symbol - Symbolic Variables
============================

This module provides the Symbol class for symbolic variables.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
from typing import Set, Union
from .expr_types import Expr, MathConstant
from .numeric_types import Integer


class Symbol(Expr):
    """
    Symbolic variable.

    Replaces sympy.Symbol.
    """

    def __init__(self, name: str, **assumptions):
        self.name = name
        self.assumptions = assumptions
        self._hash_cache = hash(('Symbol', name))

    def __repr__(self) -> str:
        return f"Symbol('{self.name}')"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    def __lt__(self, other: 'Symbol') -> bool:
        if isinstance(other, Symbol):
            return self.name < other.name
        return NotImplemented

    @property
    def free_symbols(self) -> Set['Symbol']:
        """Get free symbols (returns a set containing only this symbol).

        Returns:
            Set containing only this Symbol instance
        """
        return {self}

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbol. Supports both subs({x: val}) and subs(x, val)."""
        if len(args) == 1 and isinstance(args[0], dict):
            substitutions = args[0]
        elif len(args) == 2:
            substitutions = {args[0]: args[1]}
        else:
            substitutions = kwargs
        return substitutions.get(self, self)

    def diff(self, var: 'Symbol') -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx symbol(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Symbol(x**2).diff(x)
                # Returns derivative expression

                """
        return Integer(1) if self == var else Integer(0)

    def simplify(self) -> Expr:
        """Simplify the expression algebraically.

                Applies simplification rules specific to symbol.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Symbol(Integer(0)).simplify()
                # Returns simplified form

                """
        return self

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate the expression.

                Evaluates the function numerically if all arguments are numeric.
                Returns symbolic form if evaluation fails.

                Args:
                    precision: Number of decimal digits for precision (default: 15)

                Returns:
                    Numerical value (float) if evaluable, otherwise symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Symbol(2).evalf()
                # Returns numerical result

                """
        # Check if this is a constant
        name_lower = self.name.lower()
        if name_lower == 'pi':
            return MathConstant.PI
        if name_lower == 'e':
            return MathConstant.E
        if name_lower in ('gamma', 'euler'):
            return MathConstant.GAMMA
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Symbol(Symbol('x')).to_latex()
                '\\symbol\\left(x\\right)'

                """
        # Greek letters and special symbols
        greek = {
            'alpha': r'\alpha', 'beta': r'\beta', 'gamma': r'\gamma',
            'delta': r'\delta', 'epsilon': r'\epsilon', 'zeta': r'\zeta',
            'eta': r'\eta', 'theta': r'\theta', 'iota': r'\iota',
            'kappa': r'\kappa', 'lambda': r'\lambda', 'mu': r'\mu',
            'nu': r'\nu', 'xi': r'\xi', 'pi': r'\pi', 'rho': r'\rho',
            'sigma': r'\sigma', 'tau': r'\tau', 'upsilon': r'\upsilon',
            'phi': r'\phi', 'chi': r'\chi', 'psi': r'\psi', 'omega': r'\omega',
            'Gamma': r'\Gamma', 'Delta': r'\Delta', 'Theta': r'\Theta',
            'Lambda': r'\Lambda', 'Xi': r'\Xi', 'Pi': r'\Pi',
            'Sigma': r'\Sigma', 'Phi': r'\Phi', 'Psi': r'\Psi', 'Omega': r'\Omega',
        }
        if self.name in greek:
            return greek[self.name]
        if len(self.name) > 1:
            return r'\text{' + self.name + '}'
        return self.name


__all__ = [
    'Symbol',
]
