# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Function Library - Mathematical Functions
==========================================

Defines mathematical functions (Sin, Cos, Tan, Exp, Log, Sqrt, etc.).
NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import math
from typing import Set, Union
from .type_system import Expr, Symbol, Integer, _ensure_expr


# =============================================================================
# MATHEMATICAL FUNCTIONS
# =============================================================================

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

        Recursively collects all Symbol objects appearing in this
        function's arguments.

        Returns:
            Set of Symbol objects in the expression

        Example:
            >>> x, y = Symbol('x'), Symbol('y')
            >>> f = Sin(x**2 + y)
            >>> f.free_symbols
            {x, y}
        """
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
        """Simplify the function by simplifying its arguments.

        Recursively simplifies all arguments and reconstructs
        the function with simplified arguments.

        Returns:
            Simplified function expression

        Example:
            >>> x = Symbol('x')
            >>> f = Sin(x + 0)
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
            >>> x = Symbol('x')
            >>> Sin(x**2).diff(x)
            2*x*cos(x**2)
        """
        # d/dx sin(f) = cos(f) * f'
        from .composite_operations import Mul
        return Mul(Cos(self.args[0]), self.args[0].diff(var)).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate sin(x) to floating-point.

        Evaluates the function if the argument is numeric.
        Returns symbolic form if evaluation fails.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Sin(0).evalf()
            0.0
            >>> Sin(math.pi/2).evalf()
            1.0
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

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> x = Symbol('x')
            >>> Sin(x).to_latex()
            '\\\\sin\\\\left(x\\\\right)'
        """
        return rf'\sin\left({self.args[0].to_latex()}\right)'


class Cos(Function):
    """Cosine function.

    Represents cos(x) in symbolic form. Supports differentiation,
    numerical evaluation, and LaTeX output.
    """
    name = "cos"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative of cos(f) with respect to var.

        Uses chain rule: d/dx cos(f(x)) = -sin(f(x)) * f'(x)

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Cos(x**2).diff(x)
            -2*x*sin(x**2)
        """
        # d/dx cos(f) = -sin(f) * f'
        from .composite_operations import Mul
        return Mul(Integer(-1), Sin(self.args[0]), self.args[0].diff(var)).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate cos(x) to floating-point.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Cos(0).evalf()
            1.0
            >>> import math
            >>> Cos(math.pi).evalf()
            -1.0
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

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> Cos(Symbol('x')).to_latex()
            '\\\\cos\\\\left(x\\\\right)'
        """
        return rf'\cos\left({self.args[0].to_latex()}\right)'


class Tan(Function):
    """Tangent function.

    Represents tan(x) in symbolic form. Supports differentiation,
    numerical evaluation, and LaTeX output.
    """
    name = "tan"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative: d/dx tan(f) = sec²(f) * f' = f'/cos²(f).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Tan(x).diff(x)
            1/cos(x)**2
        """
        # d/dx tan(f) = sec²(f) * f' = f' / cos²(f)
        from .composite_operations import Mul, Pow
        return Mul(
            Pow(Cos(self.args[0]), Integer(-2)),
            self.args[0].diff(var)
        ).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate tan(x).

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric, else symbolic

        Example:
            >>> Tan(0).evalf()
            0.0
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.tan(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX: \\tan\\left(x\\right).

        Returns:
            LaTeX string

        Example:
            >>> Tan(Symbol('x')).to_latex()
            '\\\\tan\\\\left(x\\\\right)'
        """
        return rf'\tan\left({self.args[0].to_latex()}\right)'


class Exp(Function):
    """Exponential function e^x.

    Represents exp(x) = e^x in symbolic form.
    """
    name = "exp"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative: d/dx exp(f) = exp(f) * f'.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Exp(x**2).diff(x)
            2*x*exp(x**2)
        """
        # d/dx e^f = e^f * f'
        from .composite_operations import Mul
        return Mul(self, self.args[0].diff(var)).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate exp(x) = e^x.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            e^x as float if numeric

        Example:
            >>> Exp(1).evalf()
            2.718281828459045
            >>> Exp(0).evalf()
            1.0
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.exp(arg_val)
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX: e^{x}.

        Returns:
            LaTeX string

        Example:
            >>> Exp(Symbol('x')).to_latex()
            'e^{x}'
        """
        return rf'e^{{{self.args[0].to_latex()}}}'


class Log(Function):
    """Natural logarithm.

    Represents ln(x) in symbolic form. Domain: x > 0.
    """
    name = "log"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative: d/dx log(f) = f'/f.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Log(x**2).diff(x)
            2/x
        """
        # d/dx ln(f) = f'/f
        from .composite_operations import Mul, Pow
        return Mul(self.args[0].diff(var), Pow(self.args[0], Integer(-1))).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate natural logarithm.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            ln(x) as float if x > 0, else symbolic

        Example:
            >>> import math
            >>> Log(math.e).evalf()
            1.0
            >>> Log(1).evalf()
            0.0
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)) and arg_val > 0:
                return math.log(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX: \\ln\\left(x\\right).

        Returns:
            LaTeX string

        Example:
            >>> Log(Symbol('x')).to_latex()
            '\\\\ln\\\\left(x\\\\right)'
        """
        return rf'\ln\left({self.args[0].to_latex()}\right)'


class Sqrt(Function):
    """Square root.

    Represents √x in symbolic form. Domain: x ≥ 0.
    """
    name = "sqrt"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative: d/dx sqrt(f) = f'/(2*sqrt(f)).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Sqrt(x).diff(x)
            1/(2*sqrt(x))
        """
        # d/dx sqrt(f) = f'/(2*sqrt(f))
        from .composite_operations import Mul, Pow
        return Mul(
            self.args[0].diff(var),
            Pow(Mul(Integer(2), self), Integer(-1))
        ).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate square root.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            √x as float if x ≥ 0, else symbolic

        Example:
            >>> Sqrt(4).evalf()
            2.0
            >>> Sqrt(2).evalf()
            1.4142135623730951
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)) and arg_val >= 0:
                return math.sqrt(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify square root using algebraic rules.

        Applies:
        - sqrt(0) = 0
        - sqrt(1) = 1
        - sqrt(n²) = n for perfect squares

        Returns:
            Simplified expression

        Example:
            >>> Sqrt(Integer(16)).simplify()
            4
            >>> Sqrt(Integer(0)).simplify()
            0
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
        """Convert to LaTeX: \\sqrt{x}.

        Returns:
            LaTeX string

        Example:
            >>> Sqrt(Symbol('x')).to_latex()
            '\\\\sqrt{x}'
        """
        return rf'\sqrt{{{self.args[0].to_latex()}}}'


class Abs(Function):
    """Absolute value.

    Represents |x| in symbolic form.
    """
    name = "Abs"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative: d/dx |f| = sign(f) * f'.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Abs(x).diff(x)
            sign(x)

        Note:
            Derivative undefined at x=0, but returns sign(x) symbolically.
        """
        # d/dx |f| = f'/|f| * f (sign function * derivative)
        from .composite_operations import Mul
        return Mul(
            Sign(self.args[0]),
            self.args[0].diff(var)
        ).simplify()

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate absolute value.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            |x| as float if numeric, else symbolic

        Example:
            >>> Abs(-5).evalf()
            5.0
            >>> Abs(3.7).evalf()
            3.7
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return abs(arg_val)
            return self
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX: \\left|x\\right|.

        Returns:
            LaTeX string

        Example:
            >>> Abs(Symbol('x')).to_latex()
            '\\\\left|x\\\\right|'
        """
        return rf'\left|{self.args[0].to_latex()}\right|'


class Sign(Function):
    """Sign function.

    Returns -1 for negative, 0 for zero, +1 for positive.
    """
    name = "sign"

    def diff(self, var: Symbol) -> Expr:
        """Compute derivative (zero almost everywhere).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Integer(0)

        Note:
            Derivative is undefined at x=0 but returns 0 symbolically.
        """
        return Integer(0)  # Derivative is 0 almost everywhere

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate sign function.

        Returns -1 for negative, 0 for zero, +1 for positive.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            -1.0, 0.0, or 1.0 if numeric, else symbolic

        Example:
            >>> Sign(-3).evalf()
            -1.0
            >>> Sign(0).evalf()
            0.0
            >>> Sign(5).evalf()
            1.0
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
        """Convert to LaTeX: \\text{sign}\\left(x\\right).

        Returns:
            LaTeX string

        Example:
            >>> Sign(Symbol('x')).to_latex()
            '\\\\text{sign}\\\\left(x\\\\right)'
        """
        return rf'\text{{sign}}\left({self.args[0].to_latex()}\right)'


class GenericFunction(Function):
    """Generic function for unknown function names.

    Used when function name is not recognized. Returns symbolic
    derivative and cannot be numerically evaluated.
    """

    def __init__(self, name: str, *args: Expr):
        self.name = name
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        """Return symbolic derivative for unknown function.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative object (symbolic)

        Example:
            >>> f = GenericFunction('f', Symbol('x'))
            >>> f.diff(Symbol('x'))
            Derivative(f(x), x)

        Note:
            Cannot compute explicit derivative for unknown functions.
        """
        # Return symbolic derivative
        return Derivative(self, var)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Cannot evaluate unknown function numerically.

        Args:
            precision: Decimal digits precision (ignored)

        Returns:
            Self (symbolic)

        Note:
            Generic functions cannot be numerically evaluated.
        """
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX with function name.

        Returns:
            LaTeX string

        Example:
            >>> f = GenericFunction('f', Symbol('x'))
            >>> f.to_latex()
            '\\\\text{f}\\\\left(x\\\\right)'
        """
        args_latex = ', '.join(a.to_latex() for a in self.args)
        return rf'\text{{{self.name}}}\left({args_latex}\right)'


class Derivative(Expr):
    """Symbolic derivative.

    Represents an unevaluated derivative d/dx f(x).
    Used when explicit differentiation rules are not available.
    """

    def __init__(self, expr: Expr, var: Symbol):
        """Initialize symbolic derivative.

        Args:
            expr: Expression to differentiate
            var: Variable to differentiate with respect to
        """
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
        """Get free symbols including the differentiation variable.

        Returns:
            Set containing symbols from expression and the variable
        """
        return self.expr.free_symbols | {self.var}

    def subs(self, *args_in, **kwargs) -> Expr:
        """Substitute symbols in the derivative.

        Substitutes symbols. Supports both subs({x: val}) and subs(x, val).

        Args:
            *args_in: Dictionary or positional substitution
            **kwargs: Keyword substitution

        Returns:
            Derivative with substitutions applied

        Example:
            >>> x, y = Symbol('x'), Symbol('y')
            >>> d = Derivative(x**2, x)
            >>> d.subs(x, y)
            Derivative(y**2, x)
        """
        if len(args_in) == 1 and isinstance(args_in[0], dict):
            substitutions = args_in[0]
        elif len(args_in) == 2:
            substitutions = {args_in[0]: args_in[1]}
        else:
            substitutions = kwargs
        return Derivative(self.expr.subs(substitutions), self.var)

    def diff(self, var: Symbol) -> Expr:
        """Take derivative of a derivative (higher-order).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Higher-order derivative

        Example:
            >>> x = Symbol('x')
            >>> d1 = Derivative(x**2, x)
            >>> d2 = d1.diff(x)  # Second derivative
        """
        return Derivative(self, var)

    def simplify(self) -> Expr:
        """Return self (cannot simplify unevaluated derivative).

        Returns:
            Self unchanged
        """
        return self

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Cannot numerically evaluate symbolic derivative.

        Args:
            precision: Decimal digits precision (ignored)

        Returns:
            Self (symbolic)
        """
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX: \\frac{d}{dx}f(x).

        Returns:
            LaTeX derivative notation

        Example:
            >>> x = Symbol('x')
            >>> Derivative(x**2, x).to_latex()
            '\\\\frac{d}{dx}\\\\left(x^{2}\\\\right)'
        """
        return rf'\frac{{d}}{{d{self.var.to_latex()}}}\left({self.expr.to_latex()}\right)'


# =============================================================================
# ADDITIONAL MATHEMATICAL FUNCTIONS
# =============================================================================

class Factorial(Function):
    """Factorial function n!

    Computes n! for non-negative integers.
    Extended via Gamma function: n! = Γ(n+1).
    """
    name = "factorial"

    def diff(self, var: Symbol) -> Expr:
        """Derivative via gamma: d/dn n! = n! * ψ(n+1).

        Args:
            var: Variable to differentiate

        Returns:
            Expression involving digamma function

        Note:
            Uses relation n! = Γ(n+1) and Γ'(x) = Γ(x)ψ(x).
        """
        return GenericFunction("digamma", self.args[0])

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Compute factorial numerically.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            n! as float for non-negative integer n

        Example:
            >>> Factorial(5).evalf()
            120.0
            >>> Factorial(10).evalf()
            3628800.0
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                n = int(arg_val)
                if n >= 0 and n == arg_val:
                    return float(math.factorial(n))
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def simplify(self) -> Expr:
        """Evaluate factorial of integer constants.

        Returns:
            Integer(n!) if n is non-negative integer, else self

        Example:
            >>> Factorial(Integer(5)).simplify()
            120
        """
        arg = self.args[0]
        if isinstance(arg, Integer) and arg.value >= 0:
            return Integer(math.factorial(arg.value))
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX: n!

        Returns:
            LaTeX string

        Example:
            >>> Factorial(Symbol('n')).to_latex()
            'n!'
        """
        return rf'{self.args[0].to_latex()}!'


class Gamma(Function):
    """Gamma function - generalized factorial.

    Γ(n) = (n-1)! for positive integers.
    Extends factorial to real and complex numbers.
    """
    name = "gamma"

    def diff(self, var: Symbol) -> Expr:
        """Derivative: d/dx Γ(x) = Γ(x) * ψ(x).

        Args:
            var: Variable to differentiate

        Returns:
            Expression with digamma function ψ(x)

        Note:
            ψ(x) is the digamma function (logarithmic derivative of Gamma).
        """
        from .composite_operations import Mul
        return Mul(self, GenericFunction("digamma", self.args[0]))

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Numerically evaluate Gamma function.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Γ(x) as float

        Example:
            >>> Gamma(5).evalf()
            24.0
            >>> Gamma(0.5).evalf()
            1.7724538509055159  # sqrt(pi)
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return math.gamma(arg_val)
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def to_latex(self) -> str:
        """Convert to LaTeX: \\Gamma\\left(x\\right).

        Returns:
            LaTeX string

        Example:
            >>> Gamma(Symbol('x')).to_latex()
            '\\\\Gamma\\\\left(x\\\\right)'
        """
        return rf'\Gamma\left({self.args[0].to_latex()}\right)'


class Gcd(Function):
    """Greatest common divisor.

    Computes GCD of two or more integers using Euclidean algorithm.
    """
    name = "gcd"

    def __init__(self, *args: Expr):
        if len(args) < 2:
            raise ValueError("gcd requires at least 2 arguments")
        super().__init__(*args)

    def diff(self, var: Symbol) -> Expr:
        """GCD derivative (always zero - discrete function).

        Args:
            var: Variable

        Returns:
            Integer(0)

        Note:
            GCD is defined only for integers and is not differentiable.
        """
        return Integer(0)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Compute GCD numerically.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            GCD as float

        Example:
            >>> Gcd(12, 18).evalf()
            6.0
            >>> Gcd(35, 49, 14).evalf()
            7.0
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
        """Evaluate GCD of integer constants.

        Returns:
            Integer(gcd(...)) if all args are integers

        Example:
            >>> Gcd(Integer(12), Integer(18)).simplify()
            6
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
        """Convert to LaTeX: \\gcd\\left(a, b\\right).

        Returns:
            LaTeX string

        Example:
            >>> Gcd(Symbol('a'), Symbol('b')).to_latex()
            '\\\\gcd\\\\left(a, b\\\\right)'
        """
        args_latex = ', '.join(a.to_latex() for a in self.args)
        return rf'\gcd\left({args_latex}\right)'


class Floor(Function):
    """Floor function.

    Computes ⌊x⌋ = greatest integer ≤ x.
    """
    name = "floor"

    def diff(self, var: Symbol) -> Expr:
        """Floor derivative (zero almost everywhere).

        Args:
            var: Variable

        Returns:
            Integer(0)

        Note:
            Undefined at integer values, but returns 0 symbolically.
        """
        return Integer(0)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Evaluate floor: ⌊x⌋ = greatest integer ≤ x.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Floor value as float

        Example:
            >>> Floor(3.7).evalf()
            3.0
            >>> Floor(-2.3).evalf()
            -3.0
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return float(math.floor(arg_val))
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify floor of numeric values.

        Returns:
            Integer(⌊x⌋) if numeric

        Example:
            >>> Floor(Float(3.7)).simplify()
            3
        """
        arg = self.args[0]
        if isinstance(arg, Integer):
            return arg
        if isinstance(arg, Float):
            return Integer(math.floor(arg.value))
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX: \\lfloor x \\rfloor.

        Returns:
            LaTeX string

        Example:
            >>> Floor(Symbol('x')).to_latex()
            '\\\\lfloor x \\\\rfloor'
        """
        return rf'\lfloor {self.args[0].to_latex()} \rfloor'


class Ceil(Function):
    """Ceiling function.

    Computes ⌈x⌉ = smallest integer ≥ x.
    """
    name = "ceil"

    def diff(self, var: Symbol) -> Expr:
        """Ceiling derivative (zero almost everywhere).

        Args:
            var: Variable

        Returns:
            Integer(0)

        Note:
            Undefined at integer values, but returns 0 symbolically.
        """
        return Integer(0)

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        """Evaluate ceiling: ⌈x⌉ = smallest integer ≥ x.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Ceiling value as float

        Example:
            >>> Ceil(3.2).evalf()
            4.0
            >>> Ceil(-2.7).evalf()
            -2.0
        """
        try:
            arg_val = self.args[0].evalf(precision)
            if isinstance(arg_val, (int, float)):
                return float(math.ceil(arg_val))
            return self
        except (TypeError, ValueError):
            return self

    def simplify(self) -> Expr:
        """Simplify ceiling of numeric values.

        Returns:
            Integer(⌈x⌉) if numeric

        Example:
            >>> Ceil(Float(3.2)).simplify()
            4
        """
        arg = self.args[0]
        if isinstance(arg, Integer):
            return arg
        if isinstance(arg, Float):
            return Integer(math.ceil(arg.value))
        return self

    def to_latex(self) -> str:
        """Convert to LaTeX: \\lceil x \\rceil.

        Returns:
            LaTeX string

        Example:
            >>> Ceil(Symbol('x')).to_latex()
            '\\\\lceil x \\\\rceil'
        """
        return rf'\lceil {self.args[0].to_latex()} \rceil'


def Fraction(numerator, denominator=1):
    """
    Create a Rational from numerator and denominator.

    This is a wrapper function that handles Integer objects
    and converts them to Python ints before creating a Rational.

    Usage:
        Fraction(1, 2) -> Rational(1, 2) = 1/2
        Fraction(Integer(3), Integer(4)) -> Rational(3, 4) = 3/4
    """
    from .type_system import Rational

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
    'Factorial', 'Gamma', 'Gcd', 'Floor', 'Ceil',
    'GenericFunction',
    'Derivative',
    'Fraction',
]
