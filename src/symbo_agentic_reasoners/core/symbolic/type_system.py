# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0

"""
Type System for Symbolic Expressions
=====================================

Defines the base expression hierarchy and atomic types.
NO SYMPY DEPENDENCY - Pure Python implementation.

This module provides:
- Base Expr class with abstract methods
- Type-checking properties (is_Add, is_Mul, is_number, etc.)
- Operator overloading (__add__, __mul__, __pow__, etc.)
- Atomic types: Symbol, Integer, Float, Rational
- Type coercion: _ensure_expr()
"""

from __future__ import annotations
import math
from abc import ABC, abstractmethod
from typing import Set, Union, Optional, Any
from fractions import Fraction

from .utils.constants import MathConstant


# =============================================================================
# BASE EXPRESSION CLASS
# =============================================================================

class Expr(ABC):
    """
    Base class for all symbolic expressions.

    This is the foundation of the symbolic type system.
    All symbolic objects (numbers, symbols, operations) inherit from Expr.
    """

    _hash_cache: Optional[int] = None

    @abstractmethod
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """User-friendly string representation."""
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Structural equality comparison."""
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        pass

    @property
    @abstractmethod
    def free_symbols(self) -> Set['Symbol']:
        """Return set of free symbols in expression."""
        pass

    @abstractmethod
    def subs(self, *args, **kwargs) -> 'Expr':
        """Substitute symbols with expressions. Supports both subs({x: val}) and subs(x, val)."""
        pass

    @abstractmethod
    def diff(self, var: 'Symbol') -> 'Expr':
        """Differentiate with respect to variable."""
        pass

    @abstractmethod
    def simplify(self) -> 'Expr':
        """Simplify the expression."""
        pass

    @abstractmethod
    def evalf(self, precision: int = 15) -> Union[float, complex, 'Expr']:
        """Evaluate to floating point if possible."""
        pass

    @abstractmethod
    def to_latex(self) -> str:
        """Convert to LaTeX representation."""
        pass

    # Helper methods for traversal
    def atoms(self, *types) -> Set['Expr']:
        """
        Return set of atomic subexpressions.

        If types are specified, only return atoms of those types.
        Default returns all Symbol and Number atoms.
        """
        result = set()
        if not types:
            types = (Symbol, Integer, Float, Rational)

        if isinstance(self, types):
            result.add(self)

        args = self._get_args()
        for arg in args:
            if hasattr(arg, 'atoms'):
                result.update(arg.atoms(*types))
            elif isinstance(arg, types):
                result.add(arg)

        return result

    def _get_args(self) -> tuple:
        """Return arguments of this expression (internal method to avoid property conflicts)."""
        return getattr(self, 'args', ())

    def has(self, *patterns) -> bool:
        """
        Check if expression contains any of the given patterns (SymPy compatibility).

        Args:
            *patterns: Symbols, types, or expressions to search for

        Returns:
            True if any pattern is found in the expression
        """
        for pattern in patterns:
            if isinstance(pattern, Symbol):
                if pattern in self.free_symbols:
                    return True
            elif isinstance(pattern, type):
                if isinstance(self, pattern):
                    return True
                for arg in self._get_args():
                    if hasattr(arg, 'has') and arg.has(pattern):
                        return True
            elif isinstance(pattern, Expr):
                if self == pattern:
                    return True
                for arg in self._get_args():
                    if hasattr(arg, 'has') and arg.has(pattern):
                        return True
        return False

    def replace(self, pattern, replacement) -> 'Expr':
        """
        Replace pattern with replacement in expression (SymPy compatibility stub).
        """
        if self == pattern:
            return _ensure_expr(replacement)
        if hasattr(self, 'args') and self.args:
            new_args = tuple(
                arg.replace(pattern, replacement) if hasattr(arg, 'replace') else arg
                for arg in self.args
            )
            return type(self)(*new_args)
        return self

    # =========================================================================
    # TYPE-CHECKING PROPERTIES (SymPy compatibility)
    # =========================================================================
    @property
    def is_Pow(self) -> bool:
        """Check if this is a Pow expression."""
        from .composite_operations import Pow
        return isinstance(self, Pow)

    @property
    def is_Add(self) -> bool:
        """Check if this is an Add expression."""
        from .composite_operations import Add
        return isinstance(self, Add)

    @property
    def is_Mul(self) -> bool:
        """Check if this is a Mul expression."""
        from .composite_operations import Mul
        return isinstance(self, Mul)

    @property
    def is_Symbol(self) -> bool:
        """Check if this is a Symbol."""
        return isinstance(self, Symbol)

    @property
    def is_number(self) -> bool:
        """Check if this is a numeric value."""
        return isinstance(self, (Integer, Float, Rational))

    @property
    def is_integer(self) -> bool:
        """Check if this is an integer."""
        return isinstance(self, Integer)

    @property
    def is_rational(self) -> bool:
        """Check if this is a rational number."""
        return isinstance(self, (Integer, Rational))

    @property
    def is_real(self) -> bool:
        """Check if this is a real number."""
        return isinstance(self, (Integer, Float, Rational))

    @property
    def is_negative(self) -> bool:
        """Check if this expression is negative."""
        try:
            val = self.evalf()
            if isinstance(val, (int, float)):
                return val < 0
            return False
        except (TypeError, ValueError):
            return False

    @property
    def is_positive(self) -> bool:
        """Check if this expression is positive."""
        try:
            val = self.evalf()
            if isinstance(val, (int, float)):
                return val > 0
            return False
        except (TypeError, ValueError):
            return False

    @property
    def is_zero(self) -> bool:
        """Check if this expression is zero."""
        return False

    @property
    def is_one(self) -> bool:
        """Check if this expression is one."""
        return False

    # =========================================================================
    # OPERATOR OVERLOADING
    # =========================================================================
    def __add__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Add
        other = _ensure_expr(other)
        return Add(self, other).simplify()

    def __radd__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Add
        other = _ensure_expr(other)
        return Add(other, self).simplify()

    def __sub__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Add, Mul
        other = _ensure_expr(other)
        return Add(self, Mul(Integer(-1), other)).simplify()

    def __rsub__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Add, Mul
        other = _ensure_expr(other)
        return Add(other, Mul(Integer(-1), self)).simplify()

    def __mul__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Mul
        other = _ensure_expr(other)
        return Mul(self, other).simplify()

    def __rmul__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Mul
        other = _ensure_expr(other)
        return Mul(other, self).simplify()

    def __truediv__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Mul, Pow
        other = _ensure_expr(other)
        return Mul(self, Pow(other, Integer(-1))).simplify()

    def __rtruediv__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Mul, Pow
        other = _ensure_expr(other)
        return Mul(other, Pow(self, Integer(-1))).simplify()

    def __pow__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Pow
        other = _ensure_expr(other)
        return Pow(self, other).simplify()

    def __rpow__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .composite_operations import Pow
        other = _ensure_expr(other)
        return Pow(other, self).simplify()

    def __neg__(self) -> 'Expr':
        from .composite_operations import Mul
        return Mul(Integer(-1), self).simplify()

    def __pos__(self) -> 'Expr':
        return self


# =============================================================================
# ATOMIC EXPRESSIONS: Symbol, Integer, Float, Rational
# =============================================================================

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
        return Integer(1) if self == var else Integer(0)

    def simplify(self) -> Expr:
        return self

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        # Check if this is a constant
        if MathConstant.is_constant(self.name):
            return MathConstant.get_value(self.name)
        return self

    def to_latex(self) -> str:
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


class Integer(Expr):
    """
    Integer number.

    Replaces sympy.Integer.
    """

    def __init__(self, value: int):
        self.value = int(value)
        self._hash_cache = hash(('Integer', self.value))

    def __repr__(self) -> str:
        return f"Integer({self.value})"

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Integer):
            return self.value == other.value
        if isinstance(other, (int, float)):
            return self.value == other
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    def __int__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return float(self.value)

    def __lt__(self, other) -> bool:
        if isinstance(other, (Integer, Float, Rational)):
            return self.value < float(other.evalf())
        return self.value < other

    def __le__(self, other) -> bool:
        if isinstance(other, (Integer, Float, Rational)):
            return self.value <= float(other.evalf())
        return self.value <= other

    def __gt__(self, other) -> bool:
        if isinstance(other, (Integer, Float, Rational)):
            return self.value > float(other.evalf())
        return self.value > other

    def __ge__(self, other) -> bool:
        if isinstance(other, (Integer, Float, Rational)):
            return self.value >= float(other.evalf())
        return self.value >= other

    @property
    def free_symbols(self) -> Set[Symbol]:
        return set()

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbols (no-op for integers). Supports both subs({x: val}) and subs(x, val)."""
        return self

    def diff(self, var: Symbol) -> Expr:
        return Integer(0)

    def simplify(self) -> Expr:
        return self

    def evalf(self, precision: int = 15) -> float:
        return float(self.value)

    def to_latex(self) -> str:
        return str(self.value)

    @property
    def is_number(self) -> bool:
        return True

    @property
    def is_integer(self) -> bool:
        return True

    @property
    def is_rational(self) -> bool:
        return True

    @property
    def is_real(self) -> bool:
        return True

    @property
    def is_positive(self) -> bool:
        return self.value > 0

    @property
    def is_negative(self) -> bool:
        return self.value < 0

    @property
    def is_zero(self) -> bool:
        return self.value == 0

    @property
    def is_one(self) -> bool:
        return self.value == 1


class Float(Expr):
    """
    Floating point number.

    Replaces sympy.Float.
    """

    def __init__(self, value: float):
        self.value = float(value)
        self._hash_cache = hash(('Float', self.value))

    def __repr__(self) -> str:
        return f"Float({self.value})"

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Float, Integer)):
            return abs(self.value - float(other.value)) < 1e-15
        if isinstance(other, (int, float)):
            return abs(self.value - other) < 1e-15
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    def __float__(self) -> float:
        return self.value

    @property
    def free_symbols(self) -> Set[Symbol]:
        return set()

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbols (no-op for floats). Supports both subs({x: val}) and subs(x, val)."""
        return self

    def diff(self, var: Symbol) -> Expr:
        return Integer(0)

    def simplify(self) -> Expr:
        # Check if it's actually an integer
        if self.value == int(self.value):
            return Integer(int(self.value))
        return self

    def evalf(self, precision: int = 15) -> float:
        return self.value

    def to_latex(self) -> str:
        return str(self.value)

    @property
    def is_number(self) -> bool:
        return True

    @property
    def is_real(self) -> bool:
        return True

    @property
    def is_positive(self) -> bool:
        return self.value > 0

    @property
    def is_negative(self) -> bool:
        return self.value < 0

    @property
    def is_zero(self) -> bool:
        return abs(self.value) < 1e-15


class Rational(Expr):
    """
    Rational number (fraction).

    Replaces sympy.Rational.
    """

    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ZeroDivisionError("Denominator cannot be zero")
        # Normalize sign
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        # Reduce fraction
        g = math.gcd(abs(numerator), abs(denominator))
        self.p = numerator // g  # numerator
        self.q = denominator // g  # denominator
        self._hash_cache = hash(('Rational', self.p, self.q))

    def __repr__(self) -> str:
        if self.q == 1:
            return f"Integer({self.p})"
        return f"Rational({self.p}, {self.q})"

    def __str__(self) -> str:
        if self.q == 1:
            return str(self.p)
        return f"{self.p}/{self.q}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rational):
            return self.p == other.p and self.q == other.q
        if isinstance(other, Integer):
            return self.q == 1 and self.p == other.value
        if isinstance(other, (int, float)):
            return abs(self.p / self.q - other) < 1e-15
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    def __float__(self) -> float:
        return self.p / self.q

    @property
    def free_symbols(self) -> Set[Symbol]:
        return set()

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbols (no-op for rationals). Supports both subs({x: val}) and subs(x, val)."""
        return self

    def diff(self, var: Symbol) -> Expr:
        return Integer(0)

    def simplify(self) -> Expr:
        if self.q == 1:
            return Integer(self.p)
        return self

    def evalf(self, precision: int = 15) -> float:
        return self.p / self.q

    def to_latex(self) -> str:
        if self.q == 1:
            return str(self.p)
        return rf'\frac{{{self.p}}}{{{self.q}}}'

    @property
    def is_number(self) -> bool:
        return True

    @property
    def is_rational(self) -> bool:
        return True

    @property
    def is_real(self) -> bool:
        return True

    @property
    def is_integer(self) -> bool:
        return self.q == 1

    @property
    def is_positive(self) -> bool:
        return self.p > 0

    @property
    def is_negative(self) -> bool:
        return self.p < 0

    @property
    def is_zero(self) -> bool:
        return self.p == 0


# =============================================================================
# TYPE COERCION
# =============================================================================

def _ensure_expr(obj: Union[Expr, int, float, str, Fraction]) -> Expr:
    """Convert Python objects to Expr."""
    if isinstance(obj, Expr):
        return obj
    if isinstance(obj, bool):
        return Integer(1) if obj else Integer(0)
    if isinstance(obj, int):
        return Integer(obj)
    if isinstance(obj, float):
        if obj == int(obj):
            return Integer(int(obj))
        return Float(obj)
    if isinstance(obj, Fraction):
        return Rational(obj.numerator, obj.denominator)
    if isinstance(obj, str):
        # Lazy import to avoid circular dependency
        from .expression_parser import parse_expr
        return parse_expr(obj)
    raise TypeError(f"Cannot convert {type(obj)} to Expr")


__all__ = [
    'Expr',
    'Symbol',
    'Integer',
    'Float',
    'Rational',
    '_ensure_expr',
]
