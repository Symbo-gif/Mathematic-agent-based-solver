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
        """Get all free symbols in the function and its arguments.

        Recursively collects all Symbol objects that appear in this
        function's arguments.

        Returns:
            Set of Symbol objects appearing in the expression

        Example:
            >>> x, y = Symbol('x'), Symbol('y')
            >>> f = Sin(x**2 + y)
            >>> f.free_symbols
            {x, y}
        """
        return set().union(*(a.free_symbols for a in self.args))

    def subs(self, *args_in, **kwargs) -> Expr:
        """Substitute symbols with values or expressions.

        Supports multiple calling conventions for flexibility:
        - subs({symbol: value}) - Dictionary mapping
        - subs(symbol, value) - Positional arguments
        - subs(symbol=value) - Keyword arguments

        Args:
            *args_in: Either a dict {symbol: value} or (symbol, value) pair
            **kwargs: Keyword argument form of substitutions

        Returns:
            New function expression with substitutions applied

        Example:
            >>> from symbo_agentic_reasoners.core.symbolic import Symbol
            >>> x = Symbol('x')
            >>> f = Sin(x)
            >>> f.subs(x, 2)
            sin(2)
            >>> f.subs({x: Symbol('y')})
            sin(y)
        """
        if len(args_in) == 1 and isinstance(args_in[0], dict):
            substitutions = args_in[0]
        elif len(args_in) == 2:
            substitutions = {args_in[0]: args_in[1]}
        else:
            substitutions = kwargs
        return type(self)(*(a.subs(substitutions) for a in self.args))

    def simplify(self) -> Expr:
        """Simplify the function by simplifying its arguments.

        Recursively simplifies all arguments to the function and
        reconstructs the function with simplified arguments.

        Returns:
            Simplified function expression

        Example:
            >>> from symbo_agentic_reasoners.core.symbolic import Symbol
            >>> x = Symbol('x')
            >>> f = Sin(Add(x, Integer(0)))
            >>> f.simplify()
            sin(x)
        """
        return type(self)(*(a.simplify() for a in self.args))


class Sin(Function):
    """Sine function.

    Represents sin(x) in symbolic form. Supports differentiation,
    numerical evaluation, and LaTeX output.
    """
    name = "sin"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative of sin(f) with respect to var.

        Uses chain rule: d/dx sin(f(x)) = cos(f(x)) * f'(x)

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> from symbo_agentic_reasoners.core.symbolic import Symbol
            >>> x = Symbol('x')
            >>> Sin(x**2).diff(x)
            2*x*cos(x**2)
        """
        # d/dx sin(f) = cos(f) * f'
        return Mul(Cos(self.args[0]), self.args[0].diff(var)).simplify()

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
                >>> Sin(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.sin(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Sin(Symbol('x')).to_latex()
                '\\sin\\left(x\\right)'

                """
        return rf'\sin\left({self.args[0].to_latex()}\right)'


class Cos(Function):
    """Cosine function."""
    name = "cos"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx cos(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Cos(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx cos(f) = -sin(f) * f'
        return Mul(Integer(-1), Sin(self.args[0]), self.args[0].diff(var)).simplify()

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
                >>> Cos(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.cos(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Cos(Symbol('x')).to_latex()
                '\\cos\\left(x\\right)'

                """
        return rf'\cos\left({self.args[0].to_latex()}\right)'


class Tan(Function):
    """Tangent function."""
    name = "tan"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx tan(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Tan(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx tan(f) = sec²(f) * f' = f' / cos²(f)
        return Mul(
            Pow(Cos(self.args[0]), Integer(-2)),
            self.args[0].diff(var)
        ).simplify()

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
                >>> Tan(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.tan(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Tan(Symbol('x')).to_latex()
                '\\tan\\left(x\\right)'

                """
        return rf'\tan\left({self.args[0].to_latex()}\right)'


class Exp(Function):
    """Exponential function e^x."""
    name = "exp"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx exp(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Exp(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx e^f = e^f * f'
        return Mul(self, self.args[0].diff(var)).simplify()

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
                >>> Exp(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.exp(arg_val)
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Exp(Symbol('x')).to_latex()
                '\\exp\\left(x\\right)'

                """
        return rf'e^{{{self.args[0].to_latex()}}}'


class Log(Function):
    """Natural logarithm."""
    name = "log"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx log(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Log(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx ln(f) = f'/f
        return Mul(self.args[0].diff(var), Pow(self.args[0], Integer(-1))).simplify()

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
                >>> Log(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)) and arg_val > 0:
                return math.log(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Log(Symbol('x')).to_latex()
                '\\log\\left(x\\right)'

                """
        return rf'\ln\left({self.args[0].to_latex()}\right)'


class Sqrt(Function):
    """Square root."""
    name = "sqrt"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx sqrt(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Sqrt(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx sqrt(f) = f'/(2*sqrt(f))
        return Mul(
            self.args[0].diff(var),
            Pow(Mul(Integer(2), self), Integer(-1))
        ).simplify()

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
                >>> Sqrt(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)) and arg_val >= 0:
                return math.sqrt(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify the expression algebraically.

                Applies simplification rules specific to sqrt.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Sqrt(Integer(0)).simplify()
                # Returns simplified form

                """
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
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Sqrt(Symbol('x')).to_latex()
                '\\sqrt\\left(x\\right)'

                """
        return rf'\sqrt{{{self.args[0].to_latex()}}}'


class Abs(Function):
    """Absolute value."""
    name = "Abs"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx abs(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Abs(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx |f| = f'/|f| * f (sign function * derivative)
        return Mul(
            Sign(self.args[0]),
            self.args[0].diff(var)
        ).simplify()

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
                >>> Abs(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return abs(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Abs(Symbol('x')).to_latex()
                '\\abs\\left(x\\right)'

                """
        return rf'\left|{self.args[0].to_latex()}\right|'


class Sign(Function):
    """Sign function."""
    name = "sign"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx sign(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Sign(x**2).diff(x)
                # Returns derivative expression

                """
        return Integer(0)  # Derivative is 0 almost everywhere

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
                >>> Sign(2).evalf()
                # Returns numerical result

                """
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
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Sign(Symbol('x')).to_latex()
                '\\sign\\left(x\\right)'

                """
        return rf'\text{{sign}}\left({self.args[0].to_latex()}\right)'


class GenericFunction(Function):
    """Generic function for unknown function names."""

    def __init__(self, name: str, *args: Expr):
        self.name = name
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx genericfunction(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> GenericFunction(x**2).diff(x)
                # Returns derivative expression

                """
        # Return symbolic derivative
        from .derivative import Derivative
        return Derivative(self, var)

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
                >>> GenericFunction(2).evalf()
                # Returns numerical result

                """
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> GenericFunction(Symbol('x')).to_latex()
                '\\genericfunction\\left(x\\right)'

                """
        args_latex = ', '.join(a.to_latex() for a in self.args)
        return rf'\text{{{self.name}}}\left({args_latex}\right)'


# =============================================================================
# ADDITIONAL MATHEMATICAL FUNCTIONS
# =============================================================================

class Factorial(Function):
    """Factorial function n!"""
    name = "factorial"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx factorial(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Factorial(x**2).diff(x)
                # Returns derivative expression

                """
        # Factorial is only defined for non-negative integers
        # Derivative via gamma function: d/dn n! = n! * psi(n+1)
        # where psi is the digamma function
        return GenericFunction("digamma", Add(self.args[0], Integer(1)))

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
                >>> Factorial(2).evalf()
                # Returns numerical result

                """
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
        """Simplify the expression algebraically.

                Applies simplification rules specific to factorial.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Factorial(Integer(0)).simplify()
                # Returns simplified form

                """
        arg = self.args[0]
        if isinstance(arg, Integer) and arg.value >= 0:
            return Integer(math.factorial(arg.value))
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Factorial(Symbol('x')).to_latex()
                '\\factorial\\left(x\\right)'

                """
        return rf'{self.args[0].to_latex()}!'


class Gamma(Function):
    """Gamma function - generalized factorial."""
    name = "gamma"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx gamma(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Gamma(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx Gamma(x) = Gamma(x) * psi(x)
        return Mul(self, GenericFunction("digamma", self.args[0]))

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
                >>> Gamma(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.gamma(arg_val)
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Gamma(Symbol('x')).to_latex()
                '\\gamma\\left(x\\right)'

                """
        return rf'\Gamma\left({self.args[0].to_latex()}\right)'


class Gcd(Function):
    """Greatest common divisor of two integers."""
    name = "gcd"

    def __init__(self, *args: Expr):
        if len(args) < 2:
            raise ValueError("gcd requires at least 2 arguments")
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx gcd(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Gcd(x**2).diff(x)
                # Returns derivative expression

                """
        # GCD is not differentiable
        return Integer(0)

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
                >>> Gcd(2).evalf()
                # Returns numerical result

                """
        try:
            vals = [int(a.evalf(precision)) for a in self.args]
            result = vals[0]
            for v in vals[1:]:
                result = math.gcd(result, v)
            return float(result)
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify the expression algebraically.

                Applies simplification rules specific to gcd.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Gcd(Integer(0)).simplify()
                # Returns simplified form

                """
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
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Gcd(Symbol('x')).to_latex()
                '\\gcd\\left(x\\right)'

                """
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
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx lcm(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Lcm(x**2).diff(x)
                # Returns derivative expression

                """
        return Integer(0)

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
                >>> Lcm(2).evalf()
                # Returns numerical result

                """
        try:
            vals = [int(a.evalf(precision)) for a in self.args]
            result = vals[0]
            for v in vals[1:]:
                result = (result * v) // math.gcd(result, v)
            return float(result)
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify the expression algebraically.

                Applies simplification rules specific to lcm.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Lcm(Integer(0)).simplify()
                # Returns simplified form

                """
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
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Lcm(Symbol('x')).to_latex()
                '\\lcm\\left(x\\right)'

                """
        args_latex = ', '.join(a.to_latex() for a in self.args)
        return rf'\text{{lcm}}\left({args_latex}\right)'


class Floor(Function):
    """Floor function - greatest integer less than or equal to x."""
    name = "floor"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx floor(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Floor(x**2).diff(x)
                # Returns derivative expression

                """
        return Integer(0)  # Derivative is 0 almost everywhere

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
                >>> Floor(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return float(math.floor(arg_val))
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify the expression algebraically.

                Applies simplification rules specific to floor.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Floor(Integer(0)).simplify()
                # Returns simplified form

                """
        arg = self.args[0]
        if isinstance(arg, Integer):
            return arg
        if isinstance(arg, Float):
            return Integer(math.floor(arg.value))
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Floor(Symbol('x')).to_latex()
                '\\floor\\left(x\\right)'

                """
        return rf'\lfloor {self.args[0].to_latex()} \rfloor'


class Ceil(Function):
    """Ceiling function - smallest integer greater than or equal to x."""
    name = "ceil"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx ceil(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Ceil(x**2).diff(x)
                # Returns derivative expression

                """
        return Integer(0)

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
                >>> Ceil(2).evalf()
                # Returns numerical result

                """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return float(math.ceil(arg_val))
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify the expression algebraically.

                Applies simplification rules specific to ceil.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Ceil(Integer(0)).simplify()
                # Returns simplified form

                """
        arg = self.args[0]
        if isinstance(arg, Integer):
            return arg
        if isinstance(arg, Float):
            return Integer(math.ceil(arg.value))
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Ceil(Symbol('x')).to_latex()
                '\\ceil\\left(x\\right)'

                """
        return rf'\lceil {self.args[0].to_latex()} \rceil'


class Mod(Function):
    """Modulo function."""
    name = "mod"

    def __init__(self, *args: Expr):
        if len(args) != 2:
            raise ValueError("mod requires exactly 2 arguments")
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative with respect to variable.

                Applies differentiation rules using the chain rule.
                Implements: d/dx mod(f(x)) = [derivative formula]

                Args:
                    var: Variable to differentiate with respect to

                Returns:
                    Derivative expression as symbolic Expr

                Example:
                    >>> x = Symbol('x')
                >>> Mod(x**2).diff(x)
                # Returns derivative expression

                """
        # d/dx (f mod g) = f' (when g is constant)
        return self.args[0].diff(var)

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
                >>> Mod(2).evalf()
                # Returns numerical result

                """
        try:
            a_val = self.args[0].evalf(precision)
            b_val = self.args[1].evalf(precision)
            if isinstance(a_val, (int, float)) and isinstance(b_val, (int, float)):
                return a_val % b_val
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify the expression algebraically.

                Applies simplification rules specific to mod.
                May evaluate constants, cancel terms, or apply identities.

                Returns:
                    Simplified expression

                Example:
                    >>> Mod(Integer(0)).simplify()
                # Returns simplified form

                """
        a, b = self.args[0], self.args[1]
        if isinstance(a, Integer) and isinstance(b, Integer):
            return Integer(a.value % b.value)
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX representation.

                Generates LaTeX string for mathematical typesetting.
                Used for rendering in Jupyter notebooks, documentation, etc.

                Returns:
                    LaTeX string representation

                Example:
                    >>> Mod(Symbol('x')).to_latex()
                '\\mod\\left(x\\right)'

                """
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
