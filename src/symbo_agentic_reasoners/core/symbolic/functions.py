# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0
"""
Mathematical Functions - Sin, Cos, Tan, Exp, Log, Sqrt, etc.
=============================================================

This module provides mathematical function types for symbolic mathematics.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import math
from typing import Set, Union
from .expr_types import Expr
from .numeric_types import Integer, Float
from .operations import Mul, Pow, Add
from .symbol import Symbol


def _ensure_expr(obj):
    """Import and forward to utilities._ensure_expr to avoid circular imports."""
    from .utilities import _ensure_expr as util_ensure_expr
    return util_ensure_expr(obj)


class Function(Expr):
    """Base class for mathematical functions."""

    name: str = "f"

    def __init__(self, *args: Expr):
        self.args = tuple(_ensure_expr(a) for a in args)
        self._hash_cache = hash((self.name,) + tuple(hash(a) for a in self.args))

    def __repr__(self) -> str:
        return f"{self.name}({', '.join(repr(a) for a in self.args)})"

    def __str__(self) -> str:
        return f"{self.name}({', '.join(str(a) for a in self.args)})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.args == other.args
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self) -> Set[Symbol]:
        return set().union(*(a.free_symbols for a in self.args))

    def subs(self, *args_in, **kwargs) -> Expr:
        """Substitute symbols. Supports both subs({x: val}) and subs(x, val)."""
        if len(args_in) == 1 and isinstance(args_in[0], dict):
            substitutions = args_in[0]
        elif len(args_in) == 2:
            substitutions = {args_in[0]: args_in[1]}
        else:
            substitutions = kwargs
        return type(self)(*(a.subs(substitutions) for a in self.args))

    def simplify(self) -> Expr:
        return type(self)(*(a.simplify() for a in self.args))


class Sin(Function):
    """Sine function."""
    name = "sin"

    def diff(self, var: Symbol) -> Expr:
        # d/dx sin(f) = cos(f) * f'
        return Mul(Cos(self.args[0]), self.args[0].diff(var)).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.sin(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        return rf'\sin\left({self.args[0].to_latex()}\right)'


class Cos(Function):
    """Cosine function."""
    name = "cos"

    def diff(self, var: Symbol) -> Expr:
        # d/dx cos(f) = -sin(f) * f'
        return Mul(Integer(-1), Sin(self.args[0]), self.args[0].diff(var)).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.cos(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        return rf'\cos\left({self.args[0].to_latex()}\right)'


class Tan(Function):
    """Tangent function."""
    name = "tan"

    def diff(self, var: Symbol) -> Expr:
        # d/dx tan(f) = sec²(f) * f' = f' / cos²(f)
        return Mul(
            Pow(Cos(self.args[0]), Integer(-2)),
            self.args[0].diff(var)
        ).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.tan(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        return rf'\tan\left({self.args[0].to_latex()}\right)'


class Exp(Function):
    """Exponential function e^x."""
    name = "exp"

    def diff(self, var: Symbol) -> Expr:
        # d/dx e^f = e^f * f'
        return Mul(self, self.args[0].diff(var)).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.exp(arg_val)
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def to_latex(self) -> str:
        return rf'e^{{{self.args[0].to_latex()}}}'


class Log(Function):
    """Natural logarithm."""
    name = "log"

    def diff(self, var: Symbol) -> Expr:
        # d/dx ln(f) = f'/f
        return Mul(self.args[0].diff(var), Pow(self.args[0], Integer(-1))).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)) and arg_val > 0:
                return math.log(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        return rf'\ln\left({self.args[0].to_latex()}\right)'


class Sqrt(Function):
    """Square root."""
    name = "sqrt"

    def diff(self, var: Symbol) -> Expr:
        # d/dx sqrt(f) = f'/(2*sqrt(f))
        return Mul(
            self.args[0].diff(var),
            Pow(Mul(Integer(2), self), Integer(-1))
        ).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)) and arg_val >= 0:
                return math.sqrt(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        arg = self.args[0].simplify()
        # sqrt(0) = 0
        if arg.is_zero:
            return Integer(0)
        # sqrt(1) = 1
        if arg.is_one:
            return Integer(1)
        # sqrt(n²) = n for perfect squares
        if isinstance(arg, Integer) and arg.value >= 0:
            root = int(math.sqrt(arg.value))
            if root * root == arg.value:
                return Integer(root)
        return Sqrt(arg)

    def to_latex(self) -> str:
        return rf'\sqrt{{{self.args[0].to_latex()}}}'


class Abs(Function):
    """Absolute value."""
    name = "Abs"

    def diff(self, var: Symbol) -> Expr:
        # d/dx |f| = f'/|f| * f (sign function * derivative)
        return Mul(
            Sign(self.args[0]),
            self.args[0].diff(var)
        ).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return abs(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        return rf'\left|{self.args[0].to_latex()}\right|'


class Sign(Function):
    """Sign function."""
    name = "sign"

    def diff(self, var: Symbol) -> Expr:
        return Integer(0)  # Derivative is 0 almost everywhere

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                if arg_val > 0:
                    return 1.0
                elif arg_val < 0:
                    return -1.0
                return 0.0
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        return rf'\text{{sign}}\left({self.args[0].to_latex()}\right)'


class GenericFunction(Function):
    """Generic function for unknown function names."""

    def __init__(self, name: str, *args: Expr):
        self.name = name
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        # Return symbolic derivative
        from .derivative import Derivative
        return Derivative(self, var)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        return self

    def to_latex(self) -> str:
        args_latex = ', '.join(a.to_latex() for a in self.args)
        return rf'\text{{{self.name}}}\left({args_latex}\right)'


# Lowercase aliases for SymPy compatibility
sin = Sin
cos = Cos
tan = Tan
exp = Exp
log = Log
sqrt = Sqrt


__all__ = [
    'Function',
    'Sin', 'Cos', 'Tan',
    'Exp', 'Log', 'Sqrt',
    'Abs', 'Sign',
    'GenericFunction',
    'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',  # lowercase aliases
]
