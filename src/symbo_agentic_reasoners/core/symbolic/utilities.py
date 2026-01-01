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
Utilities - Helper Functions and Constants
===========================================

This module provides utility functions and constants for symbolic mathematics.

NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import re
from fractions import Fraction
from typing import Union, Tuple, Any
from .expr_types import Expr
from .numeric_types import Integer, Float, Rational
from .symbol import Symbol


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
        from .parsing import parse_expr
        return parse_expr(obj)
    raise TypeError(f"Cannot convert {type(obj)} to Expr")


def symbols(names: str, **assumptions) -> Union[Symbol, Tuple[Symbol, ...]]:
    """
    Create multiple symbols from space or comma-separated string.

    This replaces sympy.symbols.
    """
    name_list = re.split(r'[,\s]+', names.strip())
    if len(name_list) == 1:
        return Symbol(name_list[0], **assumptions)
    return tuple(Symbol(n, **assumptions) for n in name_list)


def diff(expr: Union[Expr, str], var: Union[Symbol, str], n: int = 1) -> Expr:
    """
    Differentiate expression.

    This replaces sympy.diff.
    """
    from .parsing import parse_expr
    if isinstance(expr, str):
        expr = parse_expr(expr)
    if isinstance(var, str):
        var = Symbol(var)

    result = expr
    for _ in range(n):
        result = result.diff(var)
    return result.simplify()


def solve(expr: Union[Expr, str], var=None, dict=False):
    """
    Solve equation for variable (stub).

    Returns empty list or dict when full solution not available.
    """
    from .parsing import parse_expr
    if isinstance(expr, str):
        expr = parse_expr(expr)
    if dict:
        return []
    return []


def groebner(equations, variables, order='grlex'):
    """Groebner basis computation (stub - returns equations as-is)."""
    return equations


def arg(expr):
    """Complex argument (stub - returns 0)."""
    return Integer(0)


def preorder_traversal(expr):
    """Generator for preorder traversal of expression tree (stub)."""
    from .parsing import parse_expr
    if isinstance(expr, str):
        expr = parse_expr(expr)
    yield expr
    if hasattr(expr, 'args'):
        for arg in getattr(expr, 'args', []):
            yield from preorder_traversal(arg)


# Pre-defined symbols for common constants
pi = Symbol('pi')
E = Symbol('E')
I = Symbol('I')  # Imaginary unit
oo = Float(float('inf'))  # Infinity


__all__ = [
    '_ensure_expr',
    'symbols',
    'diff',
    'solve',
    'groebner',
    'arg',
    'preorder_traversal',
    'pi', 'E', 'I', 'oo',
]
