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


# =============================================================================
# ADDITIONAL MATHEMATICAL FUNCTIONS
# =============================================================================

class Factorial(Function):
    """Factorial function n!"""
    name = "factorial"

    def diff(self, var: Symbol) -> Expr:
        # Factorial is only defined for non-negative integers
        # Derivative via gamma function: d/dn n! = n! * psi(n+1)
        # where psi is the digamma function
        return GenericFunction("digamma", Add(self.args[0], Integer(1)))

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                n = int(arg_val)
                if n >= 0 and n == arg_val:  # Non-negative integer
                    return float(math.factorial(n))
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def simplify(self) -> Expr:
        arg = self.args[0]
        if isinstance(arg, Integer) and arg.value >= 0:
            return Integer(math.factorial(arg.value))
        return self

    def to_latex(self) -> str:
        return rf'{self.args[0].to_latex()}!'


class Gamma(Function):
    """Gamma function - generalized factorial."""
    name = "gamma"

    def diff(self, var: Symbol) -> Expr:
        # d/dx Gamma(x) = Gamma(x) * psi(x)
        return Mul(self, GenericFunction("digamma", self.args[0]))

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.gamma(arg_val)
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def to_latex(self) -> str:
        return rf'\Gamma\left({self.args[0].to_latex()}\right)'


class Gcd(Function):
    """Greatest common divisor of two integers."""
    name = "gcd"

    def __init__(self, *args: Expr):
        if len(args) < 2:
            raise ValueError("gcd requires at least 2 arguments")
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        # GCD is not differentiable
        return Integer(0)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            vals = [int(a.evalf(precision)) for a in self.args]
            result = vals[0]
            for v in vals[1:]:
                result = math.gcd(result, v)
            return float(result)
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        try:
            vals = []
            for a in self.args:
                if isinstance(a, Integer):
                    vals.append(a.value)
                else:
                    return self
            result = vals[0]
            for v in vals[1:]:
                result = math.gcd(result, v)
            return Integer(result)
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        args_latex = ', '.join(a.to_latex() for a in self.args)
        return rf'\gcd\left({args_latex}\right)'


class Lcm(Function):
    """Least common multiple of two integers."""
    name = "lcm"

    def __init__(self, *args: Expr):
        if len(args) < 2:
            raise ValueError("lcm requires at least 2 arguments")
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        return Integer(0)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            vals = [int(a.evalf(precision)) for a in self.args]
            result = vals[0]
            for v in vals[1:]:
                result = (result * v) // math.gcd(result, v)
            return float(result)
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        try:
            vals = []
            for a in self.args:
                if isinstance(a, Integer):
                    vals.append(a.value)
                else:
                    return self
            result = vals[0]
            for v in vals[1:]:
                result = (result * v) // math.gcd(result, v)
            return Integer(result)
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        args_latex = ', '.join(a.to_latex() for a in self.args)
        return rf'\text{{lcm}}\left({args_latex}\right)'


class Floor(Function):
    """Floor function - greatest integer less than or equal to x."""
    name = "floor"

    def diff(self, var: Symbol) -> Expr:
        return Integer(0)  # Derivative is 0 almost everywhere

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return float(math.floor(arg_val))
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        arg = self.args[0]
        if isinstance(arg, Integer):
            return arg
        if isinstance(arg, Float):
            return Integer(math.floor(arg.value))
        return self

    def to_latex(self) -> str:
        return rf'\lfloor {self.args[0].to_latex()} \rfloor'


class Ceil(Function):
    """Ceiling function - smallest integer greater than or equal to x."""
    name = "ceil"

    def diff(self, var: Symbol) -> Expr:
        return Integer(0)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return float(math.ceil(arg_val))
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        arg = self.args[0]
        if isinstance(arg, Integer):
            return arg
        if isinstance(arg, Float):
            return Integer(math.ceil(arg.value))
        return self

    def to_latex(self) -> str:
        return rf'\lceil {self.args[0].to_latex()} \rceil'


class Mod(Function):
    """Modulo function."""
    name = "mod"

    def __init__(self, *args: Expr):
        if len(args) != 2:
            raise ValueError("mod requires exactly 2 arguments")
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        # d/dx (f mod g) = f' (when g is constant)
        return self.args[0].diff(var)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            a_val = self.args[0].evalf(precision)
            b_val = self.args[1].evalf(precision)
            if isinstance(a_val, (int, float)) and isinstance(b_val, (int, float)):
                return a_val % b_val
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        a, b = self.args[0], self.args[1]
        if isinstance(a, Integer) and isinstance(b, Integer):
            return Integer(a.value % b.value)
        return self

    def to_latex(self) -> str:
        return rf'{self.args[0].to_latex()} \mod {self.args[1].to_latex()}'


# Lowercase aliases for SymPy compatibility
sin = Sin
cos = Cos
tan = Tan
exp = Exp
log = Log
sqrt = Sqrt
factorial = Factorial
gamma = Gamma
gcd = Gcd
lcm = Lcm
floor = Floor
ceil = Ceil
mod = Mod


def Fraction(numerator, denominator=1):
    """
    Create a Rational from numerator and denominator.

    This is a wrapper function that handles Integer objects
    and converts them to Python ints before creating a Rational.

    Usage:
        Fraction(1, 2) -> Rational(1, 2) = 1/2
        Fraction(Integer(3), Integer(4)) -> Rational(3, 4) = 3/4
    """
    from .numeric_types import Rational

    # Extract integer values from Integer objects
    if isinstance(numerator, Integer):
        numerator = numerator.value
    elif hasattr(numerator, 'evalf'):
        try:
            numerator = int(numerator.evalf())
        except (TypeError, ValueError):
            pass

    if isinstance(denominator, Integer):
        denominator = denominator.value
    elif hasattr(denominator, 'evalf'):
        try:
            denominator = int(denominator.evalf())
        except (TypeError, ValueError):
            pass

    return Rational(int(numerator), int(denominator))


__all__ = [
    'Function',
    'Sin', 'Cos', 'Tan',
    'Exp', 'Log', 'Sqrt',
    'Abs', 'Sign',
    'Factorial', 'Gamma',
    'Gcd', 'Lcm',
    'Floor', 'Ceil', 'Mod',
    'GenericFunction',
    'Fraction',
    'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',  # lowercase aliases
    'factorial', 'gamma', 'gcd', 'lcm', 'floor', 'ceil', 'mod',
]
