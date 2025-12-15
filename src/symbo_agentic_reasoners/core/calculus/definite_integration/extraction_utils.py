# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Definite Integration Specialist
================================

Extracted from native_calculus.py (lines 3533-10500).

This module provides definite integration with special integral patterns:
- Gaussian integrals (full-line, half-line, moments)
- Exponential ray integrals
- Beta and Gamma function integrals
- Oscillatory integrals (Fresnel, sinc, etc.)
- Lorentzian and special function integrals
- Singularity detection and analysis

Main exports:
- definite_integrate: Compute definite integrals with limits
- _check_log_singularity: Detect logarithmic singularities
"""

"""
Extraction Utils
==================================================

Extracted from definite_integration_specialist.py
"""

import logging
import math
import re
from typing import Optional, Tuple, Union, Dict, Any, List

from ..ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func
from ..expression_parser import ExprParser
from ..validation import check_expression_safety as _check_expression_safety
from ..calculus_utils import _simplify_output, _try_evaluate_const
from ..integration_specialist import IntegrationEngine

logger = logging.getLogger(__name__)

# Module-level instances
_parser = ExprParser()
_int_engine = IntegrationEngine()


def _extract_gaussian_coeff(exp_arg: Expr, var: str) -> Optional[float]:
    """
    Extract the coefficient 'a' from Gaussian exponent patterns.

    Handles: -x², -x²/2, -a*x², -(x-b)², -a*(x-b)², etc.
    Returns 'a' such that exponent = -a*x² or -a*(x-b)² (for shifted Gaussians)
    """
    # Pattern: Pow(Neg(x), 2) = (-x)² - parser interprets -x**2 this way
    # Users typically mean -(x²) when writing -x**2, so treat (-x)² as -x² for Gaussians
    if isinstance(exp_arg, Pow):
        if (isinstance(exp_arg.base, Neg) and
            isinstance(exp_arg.base.arg, Sym) and exp_arg.base.arg.name == var and
            isinstance(exp_arg.exp, Num) and exp_arg.exp.value == 2):
            # (-x)² treated as -x² for Gaussian detection (user intent)
            return 1.0
        # Pattern: Pow(Neg(Add(x, c)), 2) = (-(x-b))² - shifted Gaussian
        # Since (-u)² = u², this represents -(x-b)² for user intent
        if (isinstance(exp_arg.base, Neg) and
            isinstance(exp_arg.exp, Num) and exp_arg.exp.value == 2):
            inner = exp_arg.base.arg
            # Check if inner is (x + c) or (x - c) pattern
            if isinstance(inner, Add) and len(inner.terms) == 2:
                has_var = any(
                    (isinstance(t, Sym) and t.name == var) or
                    (isinstance(t, Neg) and isinstance(t.arg, Sym) and t.arg.name == var)
                    for t in inner.terms
                )
                has_const = any(
                    isinstance(t, Num) or
                    (isinstance(t, Neg) and isinstance(t.arg, Num))
                    for t in inner.terms
                )
                if has_var and has_const:
                    # (-(x-b))² treated as -(x-b)² for Gaussian (user intent)
                    return 1.0

    # Pattern: Neg(x²) -> a=1
    if isinstance(exp_arg, Neg):
        inner = exp_arg.arg
        if isinstance(inner, Pow):
            if (isinstance(inner.base, Sym) and inner.base.name == var and
                isinstance(inner.exp, Num) and inner.exp.value == 2):
                return 1.0
        # Neg(a*x²) -> a
        coeff = _extract_quadratic_coeff(inner, var)
        if coeff is not None:
            return coeff
        # Neg(x²/2) -> a=0.5
        if isinstance(inner, Mul):
            result = _extract_quadratic_coeff_with_division(inner, var)
            if result is not None:
                return result

    # Pattern: Mul with negative coefficient or (-x)² factor
    if isinstance(exp_arg, Mul):
        # Could be (-1)*x², (-0.5)*x², -(x²)/2, or (-x)²/2
        coeff = 1.0
        found_var_squared = False
        is_negative_from_neg_x_squared = False

        for factor in exp_arg.factors:
            if isinstance(factor, Num):
                coeff *= factor.value
            elif isinstance(factor, Neg):
                if isinstance(factor.arg, Num):
                    coeff *= -factor.arg.value
                elif isinstance(factor.arg, Pow):
                    # Neg(x²) = -(x²)
                    inner_pow = factor.arg
                    if (isinstance(inner_pow.base, Sym) and inner_pow.base.name == var and
                        isinstance(inner_pow.exp, Num) and inner_pow.exp.value == 2):
                        found_var_squared = True
                        coeff *= -1  # Apply the negative
                    else:
                        return None
                else:
                    return None
            elif isinstance(factor, Pow):
                # Check for x², (-x)², (x-b)², or 1/divisor
                if (isinstance(factor.base, Sym) and factor.base.name == var and
                    isinstance(factor.exp, Num) and factor.exp.value == 2):
                    # x²
                    found_var_squared = True
                elif (isinstance(factor.base, Neg) and
                      isinstance(factor.base.arg, Sym) and factor.base.arg.name == var and
                      isinstance(factor.exp, Num) and factor.exp.value == 2):
                    # (-x)² - treat as -x² for Gaussian (user intent)
                    found_var_squared = True
                    is_negative_from_neg_x_squared = True
                elif _is_shifted_quadratic(factor, var):
                    # (x - b)² or (x + b)² - shifted Gaussian
                    found_var_squared = True
                elif isinstance(factor.exp, Num) and factor.exp.value == -1:
                    # Division: 1/something
                    divisor = _try_evaluate_const(factor.base)
                    if divisor is not None:
                        coeff /= divisor
                    else:
                        return None
                else:
                    return None
            else:
                return None

        if found_var_squared:
            # For (-x)² patterns, treat as negative exponent
            if is_negative_from_neg_x_squared:
                return coeff  # Already positive coeff * (-x)² treated as -coeff*x²
            elif coeff < 0:
                return -coeff  # Return positive 'a'

    return None





def _extract_quadratic_coeff(expr: Expr, var: str) -> Optional[float]:
    """Extract coefficient 'a' from a*x² or a*(x-b)² expression."""
    if isinstance(expr, Pow):
        # x² (coefficient = 1)
        if isinstance(expr.base, Sym) and expr.base.name == var:
            if isinstance(expr.exp, Num) and expr.exp.value == 2:
                return 1.0
        # (x - b)² or (x + b)² - shifted quadratic
        if _is_shifted_quadratic(expr, var):
            return 1.0
    elif isinstance(expr, Mul):
        # a*x² or a*(x-b)²
        coeff = 1.0
        found_var_squared = False
        for factor in expr.factors:
            if isinstance(factor, Num):
                coeff *= factor.value
            elif isinstance(factor, Pow):
                if (isinstance(factor.base, Sym) and factor.base.name == var and
                    isinstance(factor.exp, Num) and factor.exp.value == 2):
                    found_var_squared = True
                elif _is_shifted_quadratic(factor, var):
                    found_var_squared = True
                else:
                    return None
            else:
                return None
        if found_var_squared:
            return coeff
    return None





def _extract_quadratic_coeff_with_division(expr: Expr, var: str) -> Optional[float]:
    """Extract coefficient from x²/2 or similar patterns."""
    if isinstance(expr, Mul):
        coeff = 1.0
        found_var_squared = False
        for factor in expr.factors:
            if isinstance(factor, Num):
                coeff *= factor.value
            elif isinstance(factor, Pow):
                if (isinstance(factor.base, Sym) and factor.base.name == var and
                    isinstance(factor.exp, Num) and factor.exp.value == 2):
                    found_var_squared = True
                elif isinstance(factor.exp, Num) and factor.exp.value == -1:
                    # 1/divisor
                    if isinstance(factor.base, Num):
                        coeff /= factor.base.value
                    else:
                        return None
                else:
                    return None
            else:
                return None
        if found_var_squared:
            return coeff
    return None





def _extract_quadratic_and_linear_coeffs(exp_arg: Expr, var: str) -> Optional[tuple]:
    """
    Extract coefficients from -a*x² + b*x pattern.

    Returns:
        (a_numeric, b_numeric, a_symbolic, b_symbolic)
        - a_numeric/b_numeric are floats if coefficients are numeric
        - a_symbolic/b_symbolic are strings if coefficients are symbolic
        Returns None if pattern doesn't match.
    """
    # Collect terms: we need -a*x² and +b*x
    a_coeff_num = None
    b_coeff_num = None
    a_coeff_sym = None
    b_coeff_sym = None

    # Handle Add (sum of terms)
    if isinstance(exp_arg, Add):
        for term in exp_arg.terms:
            # Check for x² term
            quad_result = _get_term_with_var_power(term, var, 2)
            if quad_result is not None:
                coeff, is_numeric = quad_result
                if is_numeric:
                    if coeff < 0:
                        a_coeff_num = -coeff  # Store as positive
                    else:
                        return None  # Positive x² term means divergent
                else:
                    # For symbolic, need to handle negative coefficient
                    # -a*x² should give us 'a' not '-a'
                    coeff_str = str(coeff)
                    if coeff_str.startswith('-') or coeff_str.startswith('-('):
                        # Strip the negative sign
                        if coeff_str.startswith('-(') and coeff_str.endswith(')'):
                            a_coeff_sym = coeff_str[2:-1]  # Remove '-(' and ')'
                        elif coeff_str.startswith('-'):
                            a_coeff_sym = coeff_str[1:]
                        else:
                            a_coeff_sym = coeff_str
                    else:
                        return None  # Positive x² coefficient means divergent
                continue

            # Check for x term (linear)
            linear_result = _get_term_with_var_power(term, var, 1)
            if linear_result is not None:
                coeff, is_numeric = linear_result
                if is_numeric:
                    b_coeff_num = coeff
                else:
                    b_coeff_sym = coeff
                continue

        if a_coeff_num is not None or a_coeff_sym is not None:
            return (a_coeff_num, b_coeff_num, a_coeff_sym, b_coeff_sym)

    # Handle Neg wrapping an Add
    if isinstance(exp_arg, Neg) and isinstance(exp_arg.arg, Add):
        # -(...) form
        inner = exp_arg.arg
        for term in inner.terms:
            quad_result = _get_term_with_var_power(term, var, 2)
            if quad_result is not None:
                coeff, is_numeric = quad_result
                if is_numeric:
                    # Negation flips sign, so positive becomes negative which is what we want
                    a_coeff_num = coeff  # Store as positive (negation makes -a*x² become a*x²)
                else:
                    a_coeff_sym = coeff
                continue

            linear_result = _get_term_with_var_power(term, var, 1)
            if linear_result is not None:
                coeff, is_numeric = linear_result
                if is_numeric:
                    b_coeff_num = -coeff  # Negation flips
                else:
                    b_coeff_sym = f"-({coeff})"
                continue

        if a_coeff_num is not None or a_coeff_sym is not None:
            return (a_coeff_num, b_coeff_num, a_coeff_sym, b_coeff_sym)

    return None





def _extract_power_of_var(expr: Expr, var: str) -> Optional[Union[int, float, str]]:
    """
    Extract exponent if expr is var^n.
    Returns n if expr = var^n, None otherwise.
    """
    # x (which is x^1)
    if isinstance(expr, Sym) and expr.name == var:
        return 1

    # x^n
    if isinstance(expr, Pow):
        if isinstance(expr.base, Sym) and expr.base.name == var:
            if isinstance(expr.exp, Num):
                return expr.exp.value
            elif isinstance(expr.exp, Sym):
                return expr.exp.name  # symbolic exponent
            # Handle fractions like 1/2
            elif isinstance(expr.exp, Mul):
                # Try to evaluate
                exp_str = str(expr.exp)
                try:
                    return eval(exp_str.replace('^', '**'))
                except:
                    return exp_str

    return None





def _extract_power_of_one_minus_var(expr: Expr, var: str) -> Optional[Union[int, float, str]]:
    """
    Extract exponent if expr is (1-x)^n.
    Returns n if expr = (1-var)^n, None otherwise.
    """
    # (1-x) which is (1-x)^1
    if isinstance(expr, Add):
        # Check if it's 1 - x
        terms = expr.terms
        if len(terms) == 2:
            has_one = False
            has_neg_var = False
            for t in terms:
                if isinstance(t, Num) and t.value == 1:
                    has_one = True
                elif isinstance(t, Neg) and isinstance(t.arg, Sym) and t.arg.name == var:
                    has_neg_var = True
            if has_one and has_neg_var:
                return 1

    # (1-x)^n
    if isinstance(expr, Pow):
        base = expr.base
        # Check if base is (1-x)
        is_one_minus_x = False

        if isinstance(base, Add):
            terms = base.terms
            if len(terms) == 2:
                has_one = False
                has_neg_var = False
                for t in terms:
                    if isinstance(t, Num) and t.value == 1:
                        has_one = True
                    elif isinstance(t, Neg) and isinstance(t.arg, Sym) and t.arg.name == var:
                        has_neg_var = True
                    # Also handle -x represented differently
                    elif isinstance(t, Mul):
                        mfactors = t.factors
                        if len(mfactors) == 2:
                            if (isinstance(mfactors[0], Num) and mfactors[0].value == -1 and
                                isinstance(mfactors[1], Sym) and mfactors[1].name == var):
                                has_neg_var = True
                if has_one and has_neg_var:
                    is_one_minus_x = True

        if is_one_minus_x:
            if isinstance(expr.exp, Num):
                return expr.exp.value
            elif isinstance(expr.exp, Sym):
                return expr.exp.name
            elif isinstance(expr.exp, Mul):
                exp_str = str(expr.exp)
                try:
                    return eval(exp_str.replace('^', '**'))
                except:
                    return exp_str

    return None





def _extract_positive_symbolic_coeff(inner: Expr, var: str) -> Optional[str]:
    """
    Extract positive symbolic coefficient from expression like a*x² or a*(x-b)².

    Returns the coefficient 'a' as a string.
    """
    # Pattern: Pow(x, 2) alone - coefficient is 1
    if isinstance(inner, Pow):
        if _is_var_squared_or_shifted(inner, var):
            return "1"

    # Pattern: Mul with x² and other symbolic factors
    if isinstance(inner, Mul):
        coeff_parts = []
        found_var_squared = False
        divisor_parts = []

        for factor in inner.factors:
            if isinstance(factor, Pow):
                # Check for x² or (x-b)²
                if _is_var_squared_or_shifted(factor, var):
                    found_var_squared = True
                # Check for division: something^(-1)
                elif isinstance(factor.exp, Num) and factor.exp.value == -1:
                    divisor_parts.append(_expr_to_str(factor.base))
                elif isinstance(factor.exp, Neg) and isinstance(factor.exp.arg, Num) and factor.exp.arg.value == 1:
                    divisor_parts.append(_expr_to_str(factor.base))
                else:
                    # Other power - could be part of coefficient
                    coeff_parts.append(_expr_to_str(factor))
            elif isinstance(factor, Sym):
                # Symbol like a, m, omega, beta, hbar
                if factor.name != var:
                    coeff_parts.append(factor.name)
            elif isinstance(factor, Num):
                if factor.value != 1:
                    coeff_parts.append(str(factor.value))
            elif isinstance(factor, Mul):
                # Nested multiplication
                coeff_parts.append(_expr_to_str(factor))
            else:
                # Unknown factor - can't extract
                return None

        if found_var_squared:
            # Build coefficient string
            if not coeff_parts:
                numer = "1"
            elif len(coeff_parts) == 1:
                numer = coeff_parts[0]
            else:
                numer = "*".join(coeff_parts)

            if divisor_parts:
                denom = "*".join(divisor_parts) if len(divisor_parts) > 1 else divisor_parts[0]
                return f"({numer})/({denom})"
            else:
                return numer

    return None





def _extract_linear_coeff(exp_arg: Expr, var: str) -> Optional[float]:
    """
    Extract the coefficient 'a' from exp(a*x) pattern.
    Returns positive a for exp(a*x), negative a for exp(-a*x).
    """
    # Pattern: Sym(x) → coefficient is 1
    if isinstance(exp_arg, Sym) and exp_arg.name == var:
        return 1.0

    # Pattern: Neg(Sym(x)) → coefficient is -1
    if isinstance(exp_arg, Neg):
        if isinstance(exp_arg.arg, Sym) and exp_arg.arg.name == var:
            return -1.0
        # Neg(Mul(a, x)) → -a
        if isinstance(exp_arg.arg, Mul):
            coeff = _get_linear_coeff_from_mul(exp_arg.arg, var)
            if coeff is not None:
                return -coeff

    # Pattern: Mul(a, x) or Mul(-a, x) or Mul(a, Neg(x))
    if isinstance(exp_arg, Mul):
        return _get_linear_coeff_from_mul(exp_arg, var)

    return None





def _extract_linear_coeff_unsigned(expr: Expr, var: str) -> Optional[float]:
    """
    Extract the magnitude of coefficient from k*x pattern (for trig arguments).
    Returns the absolute value of the coefficient.
    """
    coeff = _extract_linear_coeff(expr, var)
    if coeff is not None:
        return abs(coeff)
    return None





def _extract_lorentzian_m_squared(base: Expr, var: str) -> Optional[tuple]:
    """
    Extract m² from (x² + m²) pattern.

    Returns:
        (m_squared_numeric, m_symbolic) - one will be None
    """
    # Pattern: Add([Pow(x,2), m²]) or Add([Pow(x,2), Pow(m,2)])
    if not isinstance(base, Add) or len(base.terms) != 2:
        return None

    x_squared_found = False
    m_squared_value = None
    m_symbolic = None

    for term in base.terms:
        # Check for x²
        if isinstance(term, Pow):
            if isinstance(term.base, Sym) and term.base.name == var:
                if isinstance(term.exp, Num) and term.exp.value == 2:
                    x_squared_found = True
                    continue

        # Check for numeric m²
        if isinstance(term, Num):
            m_squared_value = term.value
            continue

        # Check for symbolic m² (Pow(m, 2) or just m for m=m²)
        if isinstance(term, Pow):
            if isinstance(term.base, Sym) and term.base.name != var:
                if isinstance(term.exp, Num) and term.exp.value == 2:
                    m_symbolic = term.base.name  # Return m (not m²)
                    continue

        # Check for just a symbol (treated as m²)
        if isinstance(term, Sym) and term.name != var:
            # This is m², need to return sqrt(m²) = m
            # But we don't know if it's m or m², assume it's m² for pattern like x²+a²
            m_symbolic = f"sqrt({term.name})"  # Store as sqrt of the symbol
            continue

    if x_squared_found and (m_squared_value is not None or m_symbolic is not None):
        # For m_symbolic, if it came from Pow(m,2), it's already just m
        # If it came from a bare symbol, it's sqrt(symbol)
        return (m_squared_value, m_symbolic)

    return None





def _extract_semicircle_radius(sqrt_arg: Expr, var: str) -> Optional[tuple]:
    """
    Extract R² from (R² - x²) pattern.

    Returns:
        (r_squared_numeric, r_symbolic) - one will be None
    """
    # Pattern: Add([R², Neg(x²)]) or Add([R², Mul([-1, x²])])
    if not isinstance(sqrt_arg, Add):
        return None

    r_squared_value = None
    r_symbolic = None
    has_neg_x_squared = False

    for term in sqrt_arg.terms:
        # Check for -x²
        if isinstance(term, Neg):
            inner = term.arg
            if isinstance(inner, Pow):
                if isinstance(inner.base, Sym) and inner.base.name == var:
                    if isinstance(inner.exp, Num) and inner.exp.value == 2:
                        has_neg_x_squared = True
                        continue

        # Check for Mul with -1 and x²
        if isinstance(term, Mul):
            factors = term.factors
            has_neg = False
            has_var_sq = False
            for f in factors:
                if isinstance(f, Num) and f.value == -1:
                    has_neg = True
                elif isinstance(f, Neg) and isinstance(f.arg, Num) and f.arg.value == 1:
                    has_neg = True
                elif isinstance(f, Pow):
                    if isinstance(f.base, Sym) and f.base.name == var:
                        if isinstance(f.exp, Num) and f.exp.value == 2:
                            has_var_sq = True
            if has_neg and has_var_sq:
                has_neg_x_squared = True
                continue

        # Check for numeric R²
        if isinstance(term, Num):
            r_squared_value = term.value
            continue

        # Check for symbolic R² (Pow(R, 2))
        if isinstance(term, Pow):
            if isinstance(term.base, Sym) and term.base.name != var:
                if isinstance(term.exp, Num) and term.exp.value == 2:
                    r_symbolic = term.base.name
                    continue

    if has_neg_x_squared and (r_squared_value is not None or r_symbolic is not None):
        return (r_squared_value, r_symbolic)

    return None





def _extract_symbolic_gaussian_coeff(exp_arg: Expr, var: str) -> Optional[str]:
    """
    Extract symbolic coefficient from Gaussian exponent.

    Patterns handled:
    - Neg(a*x²) → "a"
    - Neg(Mul(m, omega, Pow(x,2), Pow(hbar,-1))) → "m*omega/hbar"
    - Neg(a*(x-x0)²) → "a"
    - Neg(Mul(beta, Pow(p,2), Pow(Mul(2,m),-1))) → "beta/(2*m)"

    Returns the coefficient as a string, or None if not matched.
    """
    # Pattern: Neg(something) - required for Gaussian (exponent must be negative)
    if not isinstance(exp_arg, Neg):
        # Check for multiplication with negative factor
        if isinstance(exp_arg, Mul):
            # Look for negative coefficient in multiplication
            neg_factor = None
            other_factors = []
            for factor in exp_arg.factors:
                if isinstance(factor, Neg):
                    neg_factor = factor.arg
                elif isinstance(factor, Num) and factor.value < 0:
                    neg_factor = Num(abs(factor.value))
                else:
                    other_factors.append(factor)

            if neg_factor is not None:
                # Reconstruct as Neg(positive_part)
                if isinstance(neg_factor, Num) and neg_factor.value == 1:
                    inner = Mul(other_factors) if len(other_factors) > 1 else other_factors[0] if other_factors else Num(1)
                else:
                    all_factors = [neg_factor] + other_factors
                    inner = Mul(all_factors) if len(all_factors) > 1 else all_factors[0]
                return _extract_positive_symbolic_coeff(inner, var)
        return None

    inner = exp_arg.arg

    return _extract_positive_symbolic_coeff(inner, var)





def _extract_symbolic_linear_coeff(exp_arg: Expr, var: str) -> Optional[tuple]:
    """
    Extract symbolic coefficient from exp(±a*x) pattern.
    Returns (sign, coefficient_string) where sign is -1 for negative (converges) or +1 for positive (diverges).
    """
    # Pattern: Neg(Mul(symbol, x)) → (-1, symbol)
    if isinstance(exp_arg, Neg):
        inner = exp_arg.arg
        if isinstance(inner, Sym) and inner.name == var:
            return (-1, "1")
        if isinstance(inner, Mul):
            coeff_parts = []
            has_var = False
            for factor in inner.factors:
                if isinstance(factor, Sym) and factor.name == var:
                    has_var = True
                elif isinstance(factor, Sym):
                    coeff_parts.append(factor.name)
                elif isinstance(factor, Num):
                    coeff_parts.append(str(factor.value))
                else:
                    return None
            if has_var and coeff_parts:
                return (-1, '*'.join(coeff_parts))

    # Pattern: Mul with negative factors
    if isinstance(exp_arg, Mul):
        coeff_parts = []
        has_var = False
        sign = 1

        for factor in exp_arg.factors:
            if isinstance(factor, Sym) and factor.name == var:
                has_var = True
            elif isinstance(factor, Neg):
                if isinstance(factor.arg, Sym) and factor.arg.name == var:
                    has_var = True
                    sign *= -1
                elif isinstance(factor.arg, Num):
                    coeff_parts.append(str(factor.arg.value))
                    sign *= -1
                elif isinstance(factor.arg, Sym):
                    coeff_parts.append(factor.arg.name)
                    sign *= -1
            elif isinstance(factor, Sym):
                coeff_parts.append(factor.name)
            elif isinstance(factor, Num):
                if factor.value < 0:
                    coeff_parts.append(str(-factor.value))
                    sign *= -1
                else:
                    coeff_parts.append(str(factor.value))
            else:
                return None

        if has_var and coeff_parts:
            return (sign, '*'.join(coeff_parts))
        elif has_var:
            return (sign, "1")

    return None





def _extract_symbolic_linear_coeff_unsigned(expr: Expr, var: str) -> Optional[str]:
    """
    Extract symbolic coefficient from k*x pattern (for trig arguments).
    Returns the coefficient string.
    """
    # Pattern: k*x or Mul(k, x)
    if isinstance(expr, Sym) and expr.name == var:
        return "1"

    if isinstance(expr, Mul):
        coeff_parts = []
        has_var = False

        for factor in expr.factors:
            if isinstance(factor, Sym) and factor.name == var:
                has_var = True
            elif isinstance(factor, Sym):
                coeff_parts.append(factor.name)
            elif isinstance(factor, Num):
                coeff_parts.append(str(abs(factor.value)))
            elif isinstance(factor, Neg):
                if isinstance(factor.arg, Sym):
                    if factor.arg.name == var:
                        has_var = True
                    else:
                        coeff_parts.append(factor.arg.name)
                elif isinstance(factor.arg, Num):
                    coeff_parts.append(str(factor.arg.value))
            else:
                return None

        if has_var and coeff_parts:
            return "*".join(coeff_parts)
        elif has_var:
            return "1"

    return None





def _check_quadratic_inner(quad_inner, var: str) -> tuple:
    """
    Check if a quadratic inner expression contains the variable with coefficient 1.
    Returns (has_var, has_linear_coeff) tuple.
    """
    has_var = False
    has_linear_coeff = False

    if isinstance(quad_inner, Add):
        for term in quad_inner.terms:
            if isinstance(term, Sym) and term.name == var:
                has_var = True
            elif isinstance(term, Neg) and isinstance(term.arg, Sym) and term.arg.name == var:
                has_var = True
            elif isinstance(term, Mul):
                # Check for c*x term
                for mf in term.factors:
                    if isinstance(mf, Sym) and mf.name == var:
                        has_var = True
                        # Check if there's a numeric coefficient != 1
                        for mf2 in term.factors:
                            if isinstance(mf2, Num) and abs(mf2.value) != 1:
                                has_linear_coeff = True
                        break
    elif isinstance(quad_inner, Sym) and quad_inner.name == var:
        has_var = True
    elif isinstance(quad_inner, Mul):
        # Direct c*x form without constant
        for mf in quad_inner.factors:
            if isinstance(mf, Sym) and mf.name == var:
                has_var = True
                for mf2 in quad_inner.factors:
                    if isinstance(mf2, Num) and abs(mf2.value) != 1:
                        has_linear_coeff = True
                break

    return has_var, has_linear_coeff





def _is_shifted_quadratic(expr: Expr, var: str) -> bool:
    """
    Check if expr is a shifted quadratic: (x - b)², (x + b)², or similar.

    Returns True if the expression is (linear_in_x)² where linear_in_x is
    an expression like (x - constant) or (x + constant).

    Also handles (-(x-b))² since (-u)² = u² for all u.
    """
    if not isinstance(expr, Pow):
        return False
    if not (isinstance(expr.exp, Num) and expr.exp.value == 2):
        return False

    base = expr.base

    # Handle (-(x-b))² pattern - parser produces Pow(Neg(Add(...)), 2) for -(x-1)**2
    # Since (-u)² = u², we can strip the Neg
    if isinstance(base, Neg):
        base = base.arg

    # Check for (x - b) or (x + b) patterns - base should be Add with x term and constant
    if isinstance(base, Add) and len(base.terms) == 2:
        has_var = False
        has_const = False
        for term in base.terms:
            if isinstance(term, Sym) and term.name == var:
                has_var = True
            elif isinstance(term, Neg) and isinstance(term.arg, Sym) and term.arg.name == var:
                has_var = True
            elif isinstance(term, Num):
                has_const = True
            elif isinstance(term, Neg) and isinstance(term.arg, Num):
                has_const = True
        return has_var and has_const

    return False





def _is_var_squared_or_shifted(expr: Expr, var: str) -> bool:
    """Check if expression is x² or (x-b)² or similar shifted quadratic."""
    if not isinstance(expr, Pow):
        return False
    if not (isinstance(expr.exp, Num) and expr.exp.value == 2):
        return False

    base = expr.base

    # Handle Neg wrapper: (-(x-b))² = (x-b)²
    if isinstance(base, Neg):
        base = base.arg

    # Direct x²
    if isinstance(base, Sym) and base.name == var:
        return True

    # Shifted: (x - b)², (x + b)², (x - x0)²
    if isinstance(base, Add):
        has_var = False
        for term in base.terms:
            if isinstance(term, Sym) and term.name == var:
                has_var = True
            elif isinstance(term, Neg) and isinstance(term.arg, Sym) and term.arg.name == var:
                has_var = True
        return has_var

    return False





def _try_evaluate_const_times_var_squared(expr: Expr, var: str) -> Optional[float]:
    """Try to evaluate expressions of form c*x² and return c."""
    if isinstance(expr, Mul):
        coeff = 1.0
        found_var_squared = False
        for factor in expr.factors:
            if isinstance(factor, Num):
                coeff *= factor.value
            elif isinstance(factor, Neg):
                inner_coeff = _try_evaluate_const(factor.arg)
                if inner_coeff is not None:
                    coeff *= -inner_coeff
                else:
                    return None
            elif isinstance(factor, Pow):
                if (isinstance(factor.base, Sym) and factor.base.name == var and
                    isinstance(factor.exp, Num) and factor.exp.value == 2):
                    found_var_squared = True
                else:
                    # Could be negative exponent (division)
                    return None
            else:
                return None
        if found_var_squared:
            return coeff
    return None





def _get_linear_coeff_from_mul(expr: Mul, var: str) -> Optional[float]:
    """Extract coefficient from a*x multiplication."""
    coeff = 1.0
    has_var = False

    for factor in expr.factors:
        if isinstance(factor, Sym) and factor.name == var:
            has_var = True
        elif isinstance(factor, Neg) and isinstance(factor.arg, Sym) and factor.arg.name == var:
            has_var = True
            coeff *= -1
        elif isinstance(factor, Num):
            coeff *= factor.value
        elif isinstance(factor, Neg) and isinstance(factor.arg, Num):
            coeff *= -factor.arg.value
        else:
            return None  # Complex factor

    return coeff if has_var else None





def _get_term_with_var_power(term: Expr, var: str, power: int) -> Optional[tuple]:
    """
    Check if term contains var^power and extract coefficient.

    Returns:
        (coefficient, is_numeric) or None
    """
    # Pattern: x^power
    if isinstance(term, Pow):
        if isinstance(term.base, Sym) and term.base.name == var:
            if isinstance(term.exp, Num) and int(term.exp.value) == power:
                return (1.0, True)

    # Pattern: x (for power=1)
    if power == 1 and isinstance(term, Sym) and term.name == var:
        return (1.0, True)

    # Pattern: Neg(x^power) or Neg(coeff*x^power)
    if isinstance(term, Neg):
        inner_result = _get_term_with_var_power(term.arg, var, power)
        if inner_result is not None:
            coeff, is_numeric = inner_result
            if is_numeric:
                return (-coeff, True)
            else:
                return (f"-({coeff})", False)

    # Pattern: coeff * x^power
    if isinstance(term, Mul):
        has_var_power = False
        numeric_coeff = 1.0
        symbolic_parts = []

        for factor in term.factors:
            # Check for x^power
            if isinstance(factor, Pow):
                if isinstance(factor.base, Sym) and factor.base.name == var:
                    if isinstance(factor.exp, Num) and int(factor.exp.value) == power:
                        has_var_power = True
                        continue
            # Check for x (power=1)
            if power == 1 and isinstance(factor, Sym) and factor.name == var:
                has_var_power = True
                continue
            # Numeric coefficient
            if isinstance(factor, Num):
                numeric_coeff *= factor.value
                continue
            if isinstance(factor, Neg) and isinstance(factor.arg, Num):
                numeric_coeff *= -factor.arg.value
                continue
            # Symbolic coefficient
            if isinstance(factor, Sym) and factor.name != var:
                symbolic_parts.append(factor.name)
                continue
            if isinstance(factor, Neg) and isinstance(factor.arg, Sym):
                numeric_coeff *= -1
                symbolic_parts.append(factor.arg.name)
                continue
            # Complex factor - bail
            return None

        if has_var_power:
            if symbolic_parts:
                if numeric_coeff != 1.0:
                    return (f"{numeric_coeff}*" + "*".join(symbolic_parts), False)
                return ("*".join(symbolic_parts), False)
            return (numeric_coeff, True)

    return None





def _expr_to_str(expr: Expr) -> str:
    """Convert expression to string representation."""
    if isinstance(expr, Num):
        return str(expr.value)
    elif isinstance(expr, Sym):
        return expr.name
    elif isinstance(expr, Neg):
        inner = _expr_to_str(expr.arg)
        return f"-({inner})"
    elif isinstance(expr, Add):
        terms = [_expr_to_str(t) for t in expr.terms]
        return " + ".join(terms)
    elif isinstance(expr, Mul):
        factors = [_expr_to_str(f) for f in expr.factors]
        return "*".join(factors)
    elif isinstance(expr, Pow):
        base = _expr_to_str(expr.base)
        exp = _expr_to_str(expr.exp)
        return f"({base})**({exp})"
    elif isinstance(expr, Func):
        arg = _expr_to_str(expr.arg)
        return f"{expr.name}({arg})"
    else:
        return str(expr)





def _get_symbols(expr: Expr) -> set:
    """Get all symbol names in an expression."""
    symbols = set()

    if isinstance(expr, Sym):
        symbols.add(expr.name)
    elif isinstance(expr, Num):
        pass
    elif isinstance(expr, Neg):
        symbols.update(_get_symbols(expr.arg))
    elif isinstance(expr, Add):
        for term in expr.terms:
            symbols.update(_get_symbols(term))
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            symbols.update(_get_symbols(factor))
    elif isinstance(expr, Pow):
        symbols.update(_get_symbols(expr.base))
        symbols.update(_get_symbols(expr.exp))
    elif isinstance(expr, Func):
        symbols.update(_get_symbols(expr.arg))

    return symbols





def _evaluate_at_numeric(expr: Expr, var: str, value: float) -> float:
    """Evaluate expression at a numeric value - returns float or raises."""
    import math

    if isinstance(expr, Num):
        return float(expr.value)
    elif isinstance(expr, Sym):
        if expr.name == var:
            return value
        else:
            raise ValueError(f"Unknown symbol: {expr.name}")
    elif isinstance(expr, Neg):
        return -_evaluate_at_numeric(expr.arg, var, value)
    elif isinstance(expr, Add):
        return sum(_evaluate_at_numeric(t, var, value) for t in expr.terms)
    elif isinstance(expr, Mul):
        result = 1.0
        for f in expr.factors:
            result *= _evaluate_at_numeric(f, var, value)
        return result
    elif isinstance(expr, Pow):
        # Handle special case: (-x)**n when n is even integer
        # Parser sometimes interprets -x**n as (-x)**n, but user means -(x**n)
        # For numeric evaluation, (-x)**n = (-1)**n * x**n
        # If n is even: (-x)**n = x**n
        # If n is odd: (-x)**n = -(x**n)
        base = _evaluate_at_numeric(expr.base, var, value)
        exp = _evaluate_at_numeric(expr.exp, var, value)
        try:
            return base ** exp
        except (ValueError, OverflowError):
            # Handle negative base with non-integer exponent
            if base < 0 and exp != int(exp):
                raise ValueError(f"Cannot compute {base}**{exp} (negative base with non-integer exponent)")
            raise
    elif isinstance(expr, Func):
        arg = _evaluate_at_numeric(expr.arg, var, value)
        func_map = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'exp': math.exp, 'ln': math.log, 'log': math.log,
            'sqrt': math.sqrt, 'abs': abs, 'Abs': abs,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
        }
        if expr.name in func_map:
            return func_map[expr.name](arg)
        raise ValueError(f"Unknown function: {expr.name}")
    else:
        raise ValueError(f"Cannot evaluate: {type(expr)}")





def _fix_exponent_precedence_inline(text: str) -> str:
    """
    Fix exponent precedence in expressions inline.

    Standard mathematical convention: ** binds tighter than unary minus.
    So -x**2 means -(x**2), not (-x)**2.

    This function converts -var**exp to (-1)*var**exp to ensure correct evaluation.
    """
    import re

    # Replace -var**exp with (-1)*var**exp
    # The lookbehind ensures we only match unary minus (after (, +, *, /, =, or start)
    result = re.sub(
        r'(?<=[(+*/=,\s])-([a-zA-Z_][a-zA-Z0-9_]*)\*\*',
        r'(-1)*\1**',
        text
    )

    # Also handle at start of string
    if result.startswith('-') and '**' in result:
        match = re.match(r'^-([a-zA-Z_][a-zA-Z0-9_]*)\*\*', result)
        if match:
            result = '(-1)*' + result[1:]

    return result





def _try_numeric_integration(expr_str: str, var: str, a: float, b: float) -> Optional[str]:
    """
    Try numeric integration using scipy when closed-form fails.

    Only works when:
    - Both bounds are numeric (not symbolic)
    - The integrand has no free symbols other than the integration variable
    - scipy is available

    Returns:
        String representation of numeric result, or None if numeric integration fails/unavailable
    """
    import math

    # Check bounds are numeric
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return None

    # Check for symbolic parameters in the integrand
    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Get all symbols in expression
    symbols = _get_symbols(expr)
    free_symbols = {s for s in symbols if s != var}

    if free_symbols:
        # Has symbolic parameters - can't do numeric integration
        logger.debug(f"Numeric integration skipped: symbolic parameters {free_symbols}")
        return None

    # Try scipy integration
    try:
        from scipy import integrate as scipy_integrate
    except ImportError:
        logger.debug("scipy not available for numeric integration")
        return None

    # Build evaluable function
    def f(x_val):
        return _evaluate_at_numeric(expr, var, x_val)

    try:
        # Handle infinite bounds
        if math.isinf(a) or math.isinf(b):
            # Use quad with infinite limits
            result, error = scipy_integrate.quad(f, a, b)
        else:
            result, error = scipy_integrate.quad(f, a, b)

        # Check for reasonable precision
        if abs(error) > abs(result) * 0.01 and abs(error) > 1e-10:
            logger.debug(f"Numeric integration error too large: {error}")
            return None

        # Format result nicely
        if abs(result) < 1e-15:
            return "0"

        # Check for common values
        import math
        if abs(result - math.pi) < 1e-10:
            return "pi"
        if abs(result - math.sqrt(math.pi)) < 1e-10:
            return "sqrt(pi)"
        if abs(result - math.sqrt(2 * math.pi)) < 1e-10:
            return "sqrt(2*pi)"
        if abs(result - math.e) < 1e-10:
            return "e"

        # Check for simple fractions of pi
        for denom in [2, 3, 4, 6]:
            if abs(result - math.pi / denom) < 1e-10:
                return f"pi/{denom}"

        # Return numeric value with reasonable precision
        if abs(result) > 1000 or (abs(result) < 0.001 and result != 0):
            return f"{result:.10e}"
        else:
            # Round to remove floating point noise
            return f"{result:.10g}"

    except Exception as e:
        logger.debug(f"Numeric integration failed: {e}")
        return None





def _find_potential_singularities(expr: Expr, var: str) -> List[float]:
    """
    Find potential singularity points for an expression.

    Returns list of x values where the expression might be undefined.
    """
    import math
    singularities = []

    if isinstance(expr, Pow):
        # Check for x^(-n) which has singularity at x=0
        if isinstance(expr.exp, Num):
            exp_val = float(expr.exp.value)
            if exp_val < 0:  # Negative exponent
                # Find zeros of the base
                base_zeros = _find_zeros(expr.base, var)
                singularities.extend(base_zeros)

    elif isinstance(expr, Mul):
        # Check each factor
        for factor in expr.factors:
            singularities.extend(_find_potential_singularities(factor, var))

    elif isinstance(expr, Add):
        # Check each term
        for term in expr.terms:
            singularities.extend(_find_potential_singularities(term, var))

    elif isinstance(expr, Neg):
        singularities.extend(_find_potential_singularities(expr.arg, var))

    elif isinstance(expr, Func):
        # ln(x), log(x) have singularity where argument is 0
        if expr.name in ('ln', 'log'):
            arg_zeros = _find_zeros(expr.arg, var)
            singularities.extend(arg_zeros)
        # tan(x) has singularities at pi/2 + n*pi
        elif expr.name == 'tan':
            # Just check x = pi/2, -pi/2, 3*pi/2, etc.
            for n in range(-5, 6):
                singularities.append(math.pi/2 + n * math.pi)

    return singularities





def _find_zeros(expr: Expr, var: str) -> List[float]:
    """
    Find zeros of an expression (handles basic and quadratic cases).

    Extended to handle:
    - x = 0
    - x + c = 0 -> x = -c
    - x² + c = 0 -> x = ±sqrt(-c) (if c < 0)
    - 1 - x² = 0 -> x = ±1
    - a - x² = 0 -> x = ±sqrt(a)
    - x² - a = 0 -> x = ±sqrt(a)
    - (x - a)(x - b) style products
    """
    import math

    # Most common: expr = x has zero at x=0
    if isinstance(expr, Sym) and expr.name == var:
        return [0.0]

    # Abs(x) has zero at x=0
    if isinstance(expr, Func) and expr.name == 'Abs':
        return _find_zeros(expr.arg, var)

    # Pow(x, n) has zero at x=0 for n > 0
    if isinstance(expr, Pow):
        if isinstance(expr.base, Sym) and expr.base.name == var:
            if isinstance(expr.exp, Num) and float(expr.exp.value) > 0:
                return [0.0]
        # Check for (x - a)^n
        if isinstance(expr.base, Add):
            zeros = _find_zeros(expr.base, var)
            return zeros

    # c*x has zero at x=0
    if isinstance(expr, Mul):
        # Collect zeros from all factors
        zeros = []
        for factor in expr.factors:
            factor_zeros = _find_zeros(factor, var)
            zeros.extend(factor_zeros)
        return zeros

    # Neg of something - find zeros of the inner expression
    if isinstance(expr, Neg):
        return _find_zeros(expr.arg, var)

    # Add expressions - handle linear and quadratic
    if isinstance(expr, Add):
        # Collect coefficients: a*x² + b*x + c
        a_coeff = 0  # coefficient of x²
        b_coeff = 0  # coefficient of x
        c_const = 0  # constant term

        for term in expr.terms:
            if isinstance(term, Num):
                c_const += float(term.value)
            elif isinstance(term, Sym) and term.name == var:
                b_coeff += 1
            elif isinstance(term, Neg):
                inner = term.arg
                if isinstance(inner, Num):
                    c_const -= float(inner.value)
                elif isinstance(inner, Sym) and inner.name == var:
                    b_coeff -= 1
                elif isinstance(inner, Pow):
                    # -x²
                    if isinstance(inner.base, Sym) and inner.base.name == var:
                        if isinstance(inner.exp, Num) and float(inner.exp.value) == 2:
                            a_coeff -= 1
                elif isinstance(inner, Mul):
                    # -k*x² or -k*x
                    coeff_val = 1
                    is_x = False
                    is_x2 = False
                    for f in inner.factors:
                        if isinstance(f, Num):
                            coeff_val *= float(f.value)
                        elif isinstance(f, Sym) and f.name == var:
                            is_x = True
                        elif isinstance(f, Pow):
                            if isinstance(f.base, Sym) and f.base.name == var:
                                if isinstance(f.exp, Num) and float(f.exp.value) == 2:
                                    is_x2 = True
                    if is_x2:
                        a_coeff -= coeff_val
                    elif is_x:
                        b_coeff -= coeff_val
            elif isinstance(term, Pow):
                # x² or x^n
                if isinstance(term.base, Sym) and term.base.name == var:
                    if isinstance(term.exp, Num) and float(term.exp.value) == 2:
                        a_coeff += 1
            elif isinstance(term, Mul):
                # k*x² or k*x
                coeff_val = 1
                is_x = False
                is_x2 = False
                for f in term.factors:
                    if isinstance(f, Num):
                        coeff_val *= float(f.value)
                    elif isinstance(f, Sym) and f.name == var:
                        is_x = True
                    elif isinstance(f, Pow):
                        if isinstance(f.base, Sym) and f.base.name == var:
                            if isinstance(f.exp, Num) and float(f.exp.value) == 2:
                                is_x2 = True
                if is_x2:
                    a_coeff += coeff_val
                elif is_x:
                    b_coeff += coeff_val

        # Now solve based on what we found
        if a_coeff != 0:
            # Quadratic: a*x² + b*x + c = 0
            discriminant = b_coeff**2 - 4*a_coeff*c_const
            if discriminant >= 0:
                sqrt_disc = math.sqrt(discriminant)
                x1 = (-b_coeff + sqrt_disc) / (2*a_coeff)
                x2 = (-b_coeff - sqrt_disc) / (2*a_coeff)
                if abs(x1 - x2) < 1e-10:
                    return [x1]
                return [x1, x2]
            return []  # Complex roots
        elif b_coeff != 0:
            # Linear: b*x + c = 0
            return [-c_const / b_coeff]
        else:
            # Constant - no zeros unless it's zero
            return []

    return []





