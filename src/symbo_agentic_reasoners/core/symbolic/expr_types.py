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
Base Expression Types - Core Symbolic Mathematics
==================================================

This module provides the base Expr class and helper functions for the
native symbolic mathematics engine.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Set, Union, Any, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from .type_system import Symbol

logger = logging.getLogger('symbo_agentic_reasoners.symbolic.expr_types')


class Expr(ABC):
    """
    Base class for all symbolic expressions.

    This replaces sympy.Expr with a pure Python implementation.
    """

    _hash_cache: Optional[int] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
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

    def atoms(self, *types) -> Set['Expr']:
        """
        Return set of atomic subexpressions (replaces sympy atoms method).

        If types are specified, only return atoms of those types.
        Default returns all Symbol and Number atoms.
        """
        result = set()
        # Import here to avoid circular dependency
        from .numeric_types import Integer, Float, Rational
        from .symbol import Symbol

        # Default to Symbol and Number types if none specified
        if not types:
            types = (Symbol, Integer, Float, Rational)

        # Check if this expression is an atom
        if isinstance(self, types):
            result.add(self)

        # Recursively gather from args if present
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
        from .symbol import Symbol

        for pattern in patterns:
            # If pattern is a Symbol, check if it's in free_symbols
            if isinstance(pattern, Symbol):
                if pattern in self.free_symbols:
                    return True
            # If pattern is a type, check if any subexpression is that type
            elif isinstance(pattern, type):
                if isinstance(self, pattern):
                    return True
                for arg in self._get_args():
                    if hasattr(arg, 'has') and arg.has(pattern):
                        return True
            # If pattern is an expression, check for equality
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
        # Simple implementation - for full compatibility would need pattern matching
        if self == pattern:
            from .utilities import _ensure_expr
            return _ensure_expr(replacement)
        # Recursively apply to args
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
        from .operations import Pow
        return isinstance(self, Pow)

    @property
    def is_Add(self) -> bool:
        """Check if this is an Add expression."""
        from .operations import Add
        return isinstance(self, Add)

    @property
    def is_Mul(self) -> bool:
        """Check if this is a Mul expression."""
        from .operations import Mul
        return isinstance(self, Mul)

    @property
    def is_Symbol(self) -> bool:
        """Check if this is a Symbol."""
        from .symbol import Symbol
        return isinstance(self, Symbol)

    @property
    def is_number(self) -> bool:
        """Check if this is a numeric value."""
        from .numeric_types import Integer, Float, Rational
        return isinstance(self, (Integer, Float, Rational))

    @property
    def is_integer(self) -> bool:
        """Check if this is an integer."""
        from .numeric_types import Integer
        return isinstance(self, Integer)

    @property
    def is_rational(self) -> bool:
        """Check if this is a rational number."""
        from .numeric_types import Integer, Rational
        return isinstance(self, (Integer, Rational))

    @property
    def is_real(self) -> bool:
        """Check if this is a real number."""
        from .numeric_types import Integer, Float, Rational
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
        """Check if this expression is zero (sympy compatibility property).

        Returns:
            False (base implementation, overridden in Integer)
        """
        return False

    @property
    def is_one(self) -> bool:
        """Check if this expression is one (sympy compatibility property).

        Returns:
            False (base implementation, overridden in Integer)
        """
        return False

    # =========================================================================
    # OPERATOR OVERLOADS
    # =========================================================================
    def __add__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Add
        other = _ensure_expr(other)
        return Add(self, other).simplify()

    def __radd__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Add
        other = _ensure_expr(other)
        return Add(other, self).simplify()

    def __sub__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Add, Mul
        from .numeric_types import Integer
        other = _ensure_expr(other)
        return Add(self, Mul(Integer(-1), other)).simplify()

    def __rsub__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Add, Mul
        from .numeric_types import Integer
        other = _ensure_expr(other)
        return Add(other, Mul(Integer(-1), self)).simplify()

    def __mul__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Mul
        other = _ensure_expr(other)
        return Mul(self, other).simplify()

    def __rmul__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Mul
        other = _ensure_expr(other)
        return Mul(other, self).simplify()

    def __truediv__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Mul, Pow
        from .numeric_types import Integer
        other = _ensure_expr(other)
        return Mul(self, Pow(other, Integer(-1))).simplify()

    def __rtruediv__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Mul, Pow
        from .numeric_types import Integer
        other = _ensure_expr(other)
        return Mul(other, Pow(self, Integer(-1))).simplify()

    def __pow__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Pow
        other = _ensure_expr(other)
        return Pow(self, other).simplify()

    def __rpow__(self, other: Union['Expr', int, float]) -> 'Expr':
        from .utilities import _ensure_expr
        from .operations import Pow
        other = _ensure_expr(other)
        return Pow(other, self).simplify()

    def __neg__(self) -> 'Expr':
        from .operations import Mul
        from .numeric_types import Integer
        return Mul(Integer(-1), self).simplify()

    def __pos__(self) -> 'Expr':
        return self


class MathConstant:
    """Mathematical constants with known values."""
    PI = 3.141592653589793
    E = 2.718281828459045
    GAMMA = 0.5772156649015329  # Euler-Mascheroni
    PHI = 1.618033988749895  # Golden ratio

    @staticmethod
    def is_constant(name: str) -> bool:
        """Check if a name represents a mathematical constant.

        Args:
            name: Symbol name to check

        Returns:
            True if name is a recognized constant (pi, e, euler, gamma, phi, i)

        Example:
            >>> MathConstant.is_constant('pi')
            True
            >>> MathConstant.is_constant('x')
            False
        """
        return name.lower() in ('pi', 'e', 'euler', 'gamma', 'phi', 'i')


__all__ = [
    'Expr',
    'MathConstant',
]
