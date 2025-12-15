# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0
"""
Numeric Types - Integer, Float, Rational
=========================================

This module provides numeric expression types for the native symbolic
mathematics engine.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import math
from typing import Set, Union
from .expr_types import Expr


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
    def free_symbols(self) -> Set:
        return set()

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbols (no-op for integers). Supports both subs({x: val}) and subs(x, val)."""
        return self

    def diff(self, var) -> Expr:
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
    def free_symbols(self) -> Set:
        return set()

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbols (no-op for floats). Supports both subs({x: val}) and subs(x, val)."""
        return self

    def diff(self, var) -> Expr:
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
    def free_symbols(self) -> Set:
        return set()

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbols (no-op for rationals). Supports both subs({x: val}) and subs(x, val)."""
        return self

    def diff(self, var) -> Expr:
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


__all__ = [
    'Integer',
    'Float',
    'Rational',
]
