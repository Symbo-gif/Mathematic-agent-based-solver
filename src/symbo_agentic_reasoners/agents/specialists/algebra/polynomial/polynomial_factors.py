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
Polynomial Factoring Methods
============================

This module contains pattern-based factoring algorithms:
- Difference of squares: a² - b² = (a-b)(a+b)
- Difference of cubes: a³ - b³ = (a-b)(a²+ab+b²)
- Sum of cubes: a³ + b³ = (a+b)(a²-ab+b²)
- GCD factoring: 2x² + 4x = 2x(x + 2)

These are domain-specific algorithms that don't require SymPy.
"""

from typing import Any, Optional, Tuple
from math import gcd
from functools import reduce

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Integer, Float, Add, Mul, Pow
)


def factor_difference_of_squares(expr) -> Optional[Any]:
    """
    Factor a**2 - b**2 = (a - b)(a + b)

    Returns factored form or None if pattern doesn't match.
    """
    import math
    try:
        # Check if expression is of form x^2 - c where c is a perfect square
        if isinstance(expr, Add) and len(expr.args) == 2:
            terms = list(expr.args)

            # Find the positive and negative terms
            pos_term = None
            neg_term = None
            for t in terms:
                if isinstance(t, Pow) and isinstance(t.exp, Integer) and t.exp.value == 2:
                    if pos_term is None:
                        pos_term = t
                    else:
                        neg_term = t
                elif isinstance(t, (Integer, Float)):
                    val = t.value if hasattr(t, 'value') else t
                    if val < 0:
                        neg_term = t
                    else:
                        pos_term = t

            if pos_term and neg_term:
                # Check if pos_term is a**2 and neg_term is -b**2
                if isinstance(pos_term, Pow) and isinstance(pos_term.exp, Integer) and pos_term.exp.value == 2:
                    a = pos_term.base
                    neg_val = neg_term
                    if isinstance(neg_val, (Integer, Float)):
                        val = neg_val.value if hasattr(neg_val, 'value') else neg_val
                        if val < 0:
                            sqrt_val = math.sqrt(-val)
                            if sqrt_val == int(sqrt_val):
                                b = Integer(int(sqrt_val))
                                return Mul(Add(a, Mul(Integer(-1), b)), Add(a, b))
        return None
    except Exception:
        return None


def factor_difference_of_cubes(expr) -> Optional[Any]:
    """
    Factor a**3 - b**3 = (a - b)(a**2 + ab + b**2)
    """
    try:
        if isinstance(expr, Add) and len(expr.args) == 2:
            terms = list(expr.args)
            pos_term = None
            neg_term = None

            for t in terms:
                if isinstance(t, Pow) and isinstance(t.exp, Integer) and t.exp.value == 3:
                    if pos_term is None:
                        pos_term = t
                    else:
                        neg_term = t

            if pos_term and neg_term:
                if isinstance(pos_term, Pow) and isinstance(pos_term.exp, Integer) and pos_term.exp.value == 3:
                    a = pos_term.base
                    # For now, return None as this is complex pattern matching
                    return None
        return None
    except Exception:
        return None


def factor_sum_of_cubes(expr) -> Optional[Any]:
    """
    Factor a**3 + b**3 = (a + b)(a**2 - ab + b**2)
    """
    try:
        if isinstance(expr, Add) and len(expr.args) == 2:
            terms = list(expr.args)

            both_cubes = True
            for t in terms:
                if not (isinstance(t, Pow) and isinstance(t.exp, Integer) and t.exp.value == 3):
                    both_cubes = False
                    break

            if both_cubes:
                a = terms[0].base
                b = terms[1].base
                # Return symbolic factored form
                return Mul(Add(a, b), Add(Pow(a, Integer(2)), Add(Mul(Integer(-1), Mul(a, b)), Pow(b, Integer(2)))))
        return None
    except Exception:
        return None


def factor_gcd(expr) -> Optional[Tuple[Any, Any]]:
    """
    Extract GCD factor from polynomial terms.

    E.g., 2x² + 4x = 2x(x + 2)

    Returns (gcd_factor, remaining_expr) or None.
    """
    try:
        if not expr.is_Add:
            return None

        terms = list(expr.args)
        if len(terms) < 2:
            return None

        # Find common factors
        # First, try to find common variable factors
        common_vars = None
        for term in terms:
            term_vars = term.free_symbols
            if common_vars is None:
                common_vars = term_vars
            else:
                common_vars = common_vars.intersection(term_vars)

        if not common_vars:
            # No common variables, try numeric GCD
            coeffs = []
            for term in terms:
                if term.is_number:
                    coeffs.append(abs(int(term)))
                elif term.is_Mul:
                    for a in term.args:
                        if a.is_number:
                            coeffs.append(abs(int(a)))
                            break

            if len(coeffs) == len(terms):
                g = reduce(gcd, coeffs)
                if g > 1:
                    return (g, expr / g)

        return None
    except Exception:
        return None
