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
Exponential Integrals
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

# Cross-module imports
from .extraction_utils import _extract_quadratic_coeff, _try_evaluate_const_times_var_squared

logger = logging.getLogger(__name__)

# Module-level instances
_parser = ExprParser()
_int_engine = IntegrationEngine()


def _try_exponential_ray_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle exponential ray integrals: ∫_0^∞ exp(±a*x) dx

    Formulas:
    - ∫_0^∞ exp(-a*x) dx = 1/a  (for a > 0, converges)
    - ∫_0^∞ exp(a*x) dx = divergent (for a > 0)
    - ∫_0^∞ C*exp(-a*x) dx = C/a

    Also handles:
    - exp(-x) → 1
    - exp(-2*x) → 1/2
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract pattern: C * exp(a*x) where a may be negative (converges) or positive (diverges)
    coeff = 1.0
    exp_part = None

    if isinstance(expr, Func) and expr.name == 'exp':
        exp_part = expr
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'exp':
                exp_part = factor
            elif isinstance(factor, Num):
                coeff *= factor.value
            elif isinstance(factor, Pow):
                val = _try_evaluate_const(factor)
                if val is not None:
                    coeff *= val
                else:
                    return None  # Non-constant coefficient
            elif isinstance(factor, Sym) and factor.name != var:
                # Symbolic coefficient - can't evaluate
                return None
            else:
                return None
    else:
        return None

    if exp_part is None:
        return None

    # Extract the linear coefficient from exp(a*x)
    # We need to identify if it's exp(-a*x) (converges) or exp(a*x) (diverges)
    exp_arg = exp_part.arg
    linear_coeff = _extract_linear_coeff(exp_arg, var)

    if linear_coeff is None:
        # Try symbolic extraction
        symbolic_linear = _extract_symbolic_linear_coeff(exp_arg, var)
        if symbolic_linear is not None:
            sign, sym_coeff = symbolic_linear
            if sign < 0:
                # Converges: ∫_0^∞ exp(-a*x) dx = 1/a
                if sym_coeff == "1":
                    result = "1"
                else:
                    result = f"1/{sym_coeff}"
                if coeff != 1.0:
                    result = f"{coeff}*({result})"
                return result
            else:
                # Diverges: ∫_0^∞ exp(a*x) dx
                return "divergent (integral to +∞)"
        return None

    # Numeric case
    if linear_coeff < 0:
        # exp(-|a|*x) converges
        a = -linear_coeff  # a > 0
        result = coeff / a
        if abs(result - 1.0) < 1e-10:
            return "1"
        elif abs(result - 0.5) < 1e-10:
            return "1/2"
        return f"{result:.10g}"
    elif linear_coeff > 0:
        # exp(a*x) diverges for x → ∞
        return "divergent (integral to +∞)"
    else:
        # linear_coeff == 0 means exp(0) = 1, integral of 1 from 0 to ∞ diverges
        return "divergent (integral to +∞)"





def _try_exponential_ray_moments(expr_str: str, var: str) -> Optional[str]:
    """
    Handle exponential ray moment integrals: ∫_0^∞ x^n * exp(-a*x) dx

    Formula:
    - ∫_0^∞ x^n * exp(-a*x) dx = n! / a^(n+1) = Γ(n+1) / a^(n+1)

    Examples:
    - n=1: ∫_0^∞ x*exp(-a*x) dx = 1/a²
    - n=2: ∫_0^∞ x²*exp(-a*x) dx = 2/a³
    - n=3: ∫_0^∞ x³*exp(-a*x) dx = 6/a⁴
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract pattern: C * x^n * exp(-a*x)
    power_of_var = 0
    outer_coeff = 1.0
    exp_part = None

    if isinstance(expr, Mul):
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'exp':
                exp_part = factor
            elif isinstance(factor, Pow):
                if isinstance(factor.base, Sym) and factor.base.name == var:
                    if isinstance(factor.exp, Num):
                        power_of_var = int(factor.exp.value)
                    else:
                        return None
                else:
                    val = _try_evaluate_const(factor)
                    if val is not None:
                        outer_coeff *= val
                    else:
                        return None
            elif isinstance(factor, Sym) and factor.name == var:
                power_of_var = 1
            elif isinstance(factor, Num):
                outer_coeff *= factor.value
            else:
                return None
    else:
        return None

    if exp_part is None or power_of_var == 0:
        return None

    # Check exponent is -a*x (linear, negative)
    exp_arg = exp_part.arg
    linear_coeff = _extract_linear_coeff(exp_arg, var)
    symbolic_linear = None

    if linear_coeff is None:
        # Try symbolic
        result = _extract_symbolic_linear_coeff(exp_arg, var)
        if result is not None:
            sign, sym_coeff = result
            if sign < 0:
                symbolic_linear = sym_coeff
            else:
                return None  # Divergent
        else:
            return None
    elif linear_coeff >= 0:
        return None  # Divergent (need negative coefficient for convergence)

    # Calculate n!
    def factorial(n):
        """Perform factorial operation.

        Args:
        n: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.factorial(...)
        """
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n+1):
            result *= i
        return result

    n_factorial = factorial(power_of_var)

    if linear_coeff is not None:
        # Numeric case: n! / a^(n+1) where a = -linear_coeff
        a = -linear_coeff
        result = outer_coeff * n_factorial / (a ** (power_of_var + 1))

        # Format nicely
        if abs(result - round(result)) < 1e-10 and abs(result) < 1e10:
            return str(int(round(result)))
        return f"{result:.10g}"
    elif symbolic_linear is not None:
        # Symbolic case: n! / a^(n+1)
        a_str = symbolic_linear
        exp_power = power_of_var + 1

        if a_str == "1":
            a_power = "1"
        elif '*' in a_str or '/' in a_str:
            a_power = f"({a_str})**{exp_power}"
        else:
            a_power = f"{a_str}**{exp_power}"

        if n_factorial == 1:
            result_str = f"1/{a_power}"
        else:
            result_str = f"{n_factorial}/{a_power}"

        if outer_coeff != 1.0:
            if outer_coeff == -1.0:
                result_str = f"-({result_str})"
            else:
                result_str = f"{outer_coeff}*({result_str})"

        return result_str

    return None





def _try_linear_exponential_ray(expr_str: str, var: str, a_bound: float, b_bound: float) -> Optional[str]:
    """
    Handle polynomial × exp(-ax) integrals using linearity: ∫_0^∞ P(x)*exp(-ax) dx

    Decomposes polynomials into monomials and applies the gamma rule term-by-term:
    - ∫_0^∞ x^n*exp(-ax) dx = n!/a^(n+1)

    Examples:
    - ∫_0^∞ (x³ + 2x)*exp(-ax) dx = 6/a⁴ + 2/a²
    - ∫_0^∞ (x² + x + 1)*exp(-2x) dx = 2/8 + 1/4 + 1/2 = 1
    """
    import math

    # Only works for (0, ∞) bounds
    if not (a_bound == 0 and b_bound == float('inf')):
        return None

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Look for pattern: (polynomial) * exp(-ax) or Mul containing Add and exp
    polynomial_part = None
    exp_part = None
    outer_coeff = 1.0

    if isinstance(expr, Mul):
        add_terms = []
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'exp':
                exp_part = factor
            elif isinstance(factor, Add):
                polynomial_part = factor
            elif isinstance(factor, Num):
                outer_coeff *= factor.value
            elif isinstance(factor, Pow) or isinstance(factor, Sym):
                # Single term, not a sum - let the simpler handler deal with it
                return None
            else:
                val = _try_evaluate_const(factor)
                if val is not None:
                    outer_coeff *= val
                else:
                    return None

    if exp_part is None or polynomial_part is None:
        return None

    # Extract the coefficient 'a' from exp(-ax)
    exp_arg = exp_part.arg
    linear_coeff = _extract_linear_coeff(exp_arg, var)
    symbolic_a = None

    if linear_coeff is None:
        result = _extract_symbolic_linear_coeff(exp_arg, var)
        if result is not None:
            sign, sym_coeff = result
            if sign < 0:
                symbolic_a = sym_coeff
            else:
                return None  # Divergent
        else:
            return None
    elif linear_coeff >= 0:
        return None  # Divergent

    # Decompose polynomial into terms and apply gamma rule to each
    terms_results = []

    for term in polynomial_part.terms:
        term_result = _evaluate_monomial_exp_integral(term, var, linear_coeff, symbolic_a)
        if term_result is None:
            return None  # Can't handle this term
        terms_results.append(term_result)

    # Combine results
    if linear_coeff is not None:
        # Numeric case - sum the values
        total = sum(terms_results) * outer_coeff
        if abs(total - round(total)) < 1e-10 and abs(total) < 1e10:
            return str(int(round(total)))
        return f"{total:.10g}"
    else:
        # Symbolic case - combine strings
        result_str = " + ".join(terms_results)
        if outer_coeff != 1.0:
            result_str = f"{outer_coeff}*({result_str})"
        return result_str





def _evaluate_monomial_exp_integral(term: Expr, var: str, a_coeff: float, a_symbolic: str) -> Optional[any]:
    """
    Evaluate ∫_0^∞ C*x^n*exp(-ax) dx = C*n!/a^(n+1) for a single term.

    Returns:
        Numeric value if a_coeff is numeric, string if symbolic, or None if can't evaluate.
    """
    # Extract coefficient and power from term
    coeff = 1.0
    power = 0

    if isinstance(term, Num):
        # Constant term: C*exp(-ax) → C/a
        coeff = term.value
        power = 0
    elif isinstance(term, Sym) and term.name == var:
        # x term
        power = 1
    elif isinstance(term, Pow):
        if isinstance(term.base, Sym) and term.base.name == var:
            if isinstance(term.exp, Num):
                power = int(term.exp.value)
            else:
                return None
        else:
            # Constant power
            val = _try_evaluate_const(term)
            if val is not None:
                coeff = val
                power = 0
            else:
                return None
    elif isinstance(term, Mul):
        for factor in term.factors:
            if isinstance(factor, Num):
                coeff *= factor.value
            elif isinstance(factor, Sym) and factor.name == var:
                power = 1
            elif isinstance(factor, Pow):
                if isinstance(factor.base, Sym) and factor.base.name == var:
                    if isinstance(factor.exp, Num):
                        power = int(factor.exp.value)
                    else:
                        return None
                else:
                    val = _try_evaluate_const(factor)
                    if val is not None:
                        coeff *= val
                    else:
                        return None
            elif isinstance(factor, Neg):
                if isinstance(factor.arg, Num):
                    coeff *= -factor.arg.value
                else:
                    return None
            else:
                return None
    elif isinstance(term, Neg):
        inner_result = _evaluate_monomial_exp_integral(term.arg, var, a_coeff, a_symbolic)
        if inner_result is not None:
            if isinstance(inner_result, (int, float)):
                return -inner_result
            else:
                return f"-({inner_result})"
        return None
    else:
        return None

    # Calculate n!
    def factorial(n):
        """Perform factorial operation.

        Args:
        n: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.factorial(...)
        """
        if n <= 0:
            return 1
        result = 1
        for i in range(2, n+1):
            result *= i
        return result

    n_fact = factorial(power)

    if a_coeff is not None:
        # Numeric: C*n!/a^(n+1)
        a = -a_coeff  # a_coeff is negative for convergent integrals
        return coeff * n_fact / (a ** (power + 1))
    elif a_symbolic is not None:
        # Symbolic: build string
        a_str = a_symbolic
        exp_power = power + 1

        if coeff == 1.0 and n_fact == 1:
            return f"1/{a_str}**{exp_power}"
        elif coeff == 1.0:
            return f"{n_fact}/{a_str}**{exp_power}"
        elif n_fact == 1:
            return f"{coeff}/{a_str}**{exp_power}"
        else:
            return f"{coeff * n_fact}/{a_str}**{exp_power}"

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





