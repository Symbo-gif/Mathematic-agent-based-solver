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
Limits Package
==============

Modular limit evaluation system organized by specialization:

- limit_patterns: Known limit pattern matching
- asymptotic_rules: Special function asymptotics
- taylor_limits: Taylor series expansion
- algebra_utilities: Polynomial and algebra solvers
- gaussian_2d: 2D Gaussian integration

Main entry point: LimitEngine class
"""

import logging
import math
import re
from fractions import Fraction
from typing import Optional, Tuple, Dict, Any, Union
from ..ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from ..differentiation_specialist import DifferentiationEngine
from ..expression_parser import ExprParser
from ..validation import check_expression_safety as _check_expression_safety
from ..calculus_utils import _evaluate_at_numeric as _evaluate_at

# Import sub-modules
from . import limit_patterns
from . import asymptotic_rules
from . import taylor_limits
from . import algebra_utilities
from . import gaussian_2d

# Re-export key functions for backward compatibility
from .limit_patterns import (
    KNOWN_LIMIT_PATTERNS,
    PARAMETER_ASSUMPTIONS,
    _try_known_limit_pattern,
    _try_nested_log_limit,
    _try_stirling_limit,
    _try_asymptotic_difference_limit,
    _try_nested_limit,
    _try_one_sided_divergent_limit,
    _try_oscillatory_decay_limit,
    _try_power_decay_limit,
    _try_log_polynomial_limit,
    _try_exp_polynomial_limit,
    _try_pure_oscillatory_limit,
    _try_e_type_limit,
    _try_constant_limit,
    _try_sinc_limit,
    _try_one_minus_cos_limit,
    _try_one_minus_cos_sq_limit,
    _try_direct_substitution,
)

from .asymptotic_rules import (
    _try_special_function_asymptotic,
    _try_limit_with_assumptions,
)

from .taylor_limits import (
    _try_taylor_expansion_limit,
    taylor_series,
)

from .algebra_utilities import (
    solve_polynomial,
    solve_system_native,
    factor_polynomial,
    expand_expression,
    solve_ode_native,
    _eval_at_point,
    _get_symbols,
    _evaluate_expr_numerically,
)

from .gaussian_2d import (
    _try_2d_gaussian_integral,
    definite_integrate_2d,
    _try_separable_2d_integral,
)

logger = logging.getLogger(__name__)

# Global parser instance
_parser = ExprParser()

# Special mathematical constants
E = Sym('e')  # Euler's number


class LimitEngine:
    """
    Pure Python symbolic limit computation engine.

    Implements pattern-based limit evaluation without SymPy.
    Handles standard limit forms and L'Hôpital's rule for 0/0 and ∞/∞.

    STANDARD LIMIT FORMS:
    --------------------
    1. lim x→0 sin(x)/x = 1
    2. lim x→0 (e^x - 1)/x = 1
    3. lim x→0 (1 - cos(x))/x² = 1/2
    4. lim x→0 ln(1 + x)/x = 1
    5. lim x→0 (a^x - 1)/x = ln(a)
    6. lim x→∞ (1 + 1/x)^x = e
    7. lim x→0 tan(x)/x = 1
    8. lim x→0 arctan(x)/x = 1
    9. lim x→0 arcsin(x)/x = 1
    10. lim x→∞ polynomial ratio (leading coefficients)

    L'HÔPITAL'S RULE:
    ----------------
    For 0/0 or ∞/∞ indeterminate forms:
    lim f(x)/g(x) = lim f'(x)/g'(x)
    """

    # Maximum L'Hôpital iterations
    MAX_LHOPITAL_DEPTH = 5

    def __init__(self):
        self._diff_engine = DifferentiationEngine()

    def limit(self, expr: Expr, var: str, point: Union[float, str],
              direction: Optional[str] = None) -> Optional[Expr]:
        """
        Compute limit of expression as var approaches point.

        Args:
            expr: Expression to take limit of
            var: Variable approaching the point
            point: The limit point (number, 'inf', '-inf', or 'oo')
            direction: Optional direction for one-sided limits: '+', '-', 'right', 'left'

        Returns:
            Limit value as Expr, or None if cannot compute
        """
        # Normalize direction
        if direction in ('+', 'right', 'plus'):
            direction = '+'
        elif direction in ('-', 'left', 'minus'):
            direction = '-'

        # Normalize infinity notation
        if point in ('inf', 'oo', float('inf')):
            return self._limit_infinity(expr, var, positive=True)
        elif point in ('-inf', '-oo', float('-inf')):
            return self._limit_infinity(expr, var, positive=False)
        else:
            return self._limit_finite(expr, var, float(point), direction)

    def _limit_finite(self, expr: Expr, var: str, point: float,
                      direction: Optional[str] = None) -> Optional[Expr]:
        """Compute limit as x → a for finite a."""
        # Handle abs(x)/x and similar one-sided patterns
        if abs(point) < 1e-10:
            abs_result = self._try_abs_patterns(expr, var, direction)
            if abs_result is not None:
                return abs_result

        # Try direct substitution first
        value = self._substitute(expr, var, point)
        if value is not None and not self._is_indeterminate(value):
            return value

        # Check for standard limit forms at x → 0
        if abs(point) < 1e-10:
            result = self._try_standard_forms_zero(expr, var)
            if result is not None:
                return result

            # Try Taylor series expansion for higher-order limits
            result = self._try_taylor_expansion(expr, var)
            if result is not None:
                return result

        # Try L'Hôpital's rule for 0/0 form
        if isinstance(expr, Mul):
            result = self._try_lhopital(expr, var, point, depth=0)
            if result is not None:
                return result

        return None

    def _limit_infinity(self, expr: Expr, var: str, positive: bool = True) -> Optional[Expr]:
        """Compute limit as x → ±∞."""
        # Check for oscillatory patterns first
        result = self._try_oscillatory_limit(expr, var, positive)
        if result is not None:
            return result

        # For polynomial ratios, compare degrees
        if isinstance(expr, Mul):
            result = self._polynomial_ratio_limit(expr, var, positive)
            if result is not None:
                return result

        # Check for (1 + 1/x)^x → e pattern and x^(1/x) → 1
        if isinstance(expr, Pow):
            result = self._try_e_definition(expr, var, positive)
            if result is not None:
                return result

            # Check for x^(1/x) → 1
            result = self._try_root_power_limit(expr, var, positive)
            if result is not None:
                return result

        # Check for exp/polynomial domination
        result = self._try_exp_domination(expr, var, positive)
        if result is not None:
            return result

        # Check for log/polynomial growth comparison
        result = self._try_log_poly_limit(expr, var, positive)
        if result is not None:
            return result

        return None

    def _try_oscillatory_limit(self, expr: Expr, var: str, positive: bool) -> Optional[Expr]:
        """
        Handle limits involving oscillatory functions (sin, cos) at infinity.

        - sin(x), cos(x) → DNE (oscillatory)
        - sin(x)/x → 0 (bounded/unbounded)
        - (sin(x) + cos(x))/x → 0
        - (1 + sin(x))/x → 0
        """
        # Pure oscillatory: sin(x), cos(x) alone
        if isinstance(expr, Func) and expr.name in ('sin', 'cos'):
            if self._contains_var(expr.arg, var):
                return Sym('DNE')  # Does not exist (oscillatory)

        # Quotient with oscillatory numerator
        if isinstance(expr, Mul):
            has_oscillatory = False
            has_var_neg_power = False
            neg_power = 0

            for f in expr.factors:
                if isinstance(f, Func) and f.name in ('sin', 'cos'):
                    if self._contains_var(f.arg, var):
                        has_oscillatory = True
                elif isinstance(f, Add):
                    # Check if Add contains oscillatory terms
                    for t in f.terms:
                        if isinstance(t, Func) and t.name in ('sin', 'cos'):
                            if self._contains_var(t.arg, var):
                                has_oscillatory = True
                elif isinstance(f, Pow):
                    if isinstance(f.base, Sym) and f.base.name == var:
                        if isinstance(f.exp, Num) and f.exp.value < 0:
                            has_var_neg_power = True
                            neg_power = f.exp.value

            # bounded * (1/x^n) → 0 for n > 0
            if has_oscillatory and has_var_neg_power and neg_power < 0:
                return Num(0)

        return None

    def _try_root_power_limit(self, expr: Pow, var: str, positive: bool) -> Optional[Expr]:
        """
        Handle x^(1/x) type limits.

        - x^(1/x) → 1 as x → ∞
        - n^(1/n) → 1 as n → ∞
        """
        base, exp = expr.base, expr.exp

        # Check for x^(1/x) pattern
        # Base is x or n
        if isinstance(base, Sym) and base.name == var:
            # Exponent should be 1/x
            if isinstance(exp, Pow):
                if (isinstance(exp.base, Sym) and exp.base.name == var and
                    isinstance(exp.exp, Num) and exp.exp.value == -1):
                    return Num(1)
            elif isinstance(exp, Mul):
                # Check for 1 * x^(-1)
                has_x_neg1 = False
                coeff = 1
                for f in exp.factors:
                    if isinstance(f, Num):
                        coeff *= f.value
                    elif isinstance(f, Pow):
                        if (isinstance(f.base, Sym) and f.base.name == var and
                            isinstance(f.exp, Num) and f.exp.value == -1):
                            has_x_neg1 = True
                if has_x_neg1:
                    # x^(c/x) → 1 for any constant c
                    return Num(1)

        return None

    def _try_log_poly_limit(self, expr: Expr, var: str, positive: bool) -> Optional[Expr]:
        """
        Handle log vs polynomial growth comparisons at infinity.

        - log(x)/x^p → 0 for p > 0 (polynomial dominates log)
        - x^p/log(x) → ∞ for p > 0 (polynomial dominates log)
        - log(x)^n/x^p → 0 for p > 0 (polynomial dominates any power of log)
        """
        if not isinstance(expr, Mul):
            return None

        log_power = 0  # Power of log(x)
        poly_power = 0  # Power of x in denominator
        has_log = False
        has_poly_denom = False

        for f in expr.factors:
            # Check for log(x) or ln(x)
            if isinstance(f, Func) and f.name in ('log', 'ln'):
                if isinstance(f.arg, Sym) and f.arg.name == var:
                    has_log = True
                    log_power = 1
            # Check for log(x)^n
            elif isinstance(f, Pow):
                if isinstance(f.base, Func) and f.base.name in ('log', 'ln'):
                    if isinstance(f.base.arg, Sym) and f.base.arg.name == var:
                        if isinstance(f.exp, Num):
                            has_log = True
                            log_power = f.exp.value
                # Check for x^(-p) in denominator
                elif isinstance(f.base, Sym) and f.base.name == var:
                    if isinstance(f.exp, Num) and f.exp.value < 0:
                        has_poly_denom = True
                        poly_power = -f.exp.value
                # Handle nested Pow like x**0.1**-1 which means 1/(x**0.1)
                elif isinstance(f.base, Pow):
                    if isinstance(f.base.base, Sym) and f.base.base.name == var:
                        if isinstance(f.base.exp, Num) and isinstance(f.exp, Num):
                            # x**p**(-1) = 1/(x**p)
                            if f.exp.value == -1:
                                has_poly_denom = True
                                poly_power = f.base.exp.value

        # log(x)^n / x^p → 0 when p > 0
        if has_log and has_poly_denom and poly_power > 0:
            return Num(0)

        # Also check for x^p / log(x) → ∞
        if isinstance(expr, Mul):
            poly_numer_power = 0
            log_denom_power = 0
            has_log_denom = False
            has_poly_numer = False

            for f in expr.factors:
                if isinstance(f, Sym) and f.name == var:
                    has_poly_numer = True
                    poly_numer_power = 1
                elif isinstance(f, Pow):
                    if isinstance(f.base, Sym) and f.base.name == var:
                        if isinstance(f.exp, Num) and f.exp.value > 0:
                            has_poly_numer = True
                            poly_numer_power = f.exp.value
                    # Check for 1/log(x)
                    elif isinstance(f.base, Func) and f.base.name in ('log', 'ln'):
                        if isinstance(f.exp, Num) and f.exp.value == -1:
                            has_log_denom = True
                            log_denom_power = 1

            # x^p / log(x) → ∞
            if has_poly_numer and has_log_denom and poly_numer_power > 0:
                return Sym('oo')  # +∞

        return None

    def _try_standard_forms_zero(self, expr: Expr, var: str) -> Optional[Expr]:
        """
        Try standard limit forms as x → 0.

        Patterns:
        - sin(x)/x → 1
        - (e^x - 1)/x → 1
        - (1 - cos(x))/x² → 1/2
        - ln(1 + x)/x → 1
        - tan(x)/x → 1
        - arcsin(x)/x → 1
        - arctan(x)/x → 1
        """
        # Check for quotient pattern (Mul with negative power)
        if not isinstance(expr, Mul):
            return None

        numer_parts = []
        denom_parts = []

        for f in expr.factors:
            if isinstance(f, Pow) and isinstance(f.exp, Num) and f.exp.value < 0:
                denom_parts.append((f.base, -f.exp.value))
            else:
                numer_parts.append(f)

        if len(denom_parts) != 1 or len(numer_parts) != 1:
            return None

        numer = numer_parts[0]
        denom, denom_power = denom_parts[0]

        # sin(x)/x → 1
        if (isinstance(numer, Func) and numer.name == 'sin' and
            isinstance(numer.arg, Sym) and numer.arg.name == var and
            isinstance(denom, Sym) and denom.name == var and denom_power == 1):
            return Num(1)

        # tan(x)/x → 1
        if (isinstance(numer, Func) and numer.name == 'tan' and
            isinstance(numer.arg, Sym) and numer.arg.name == var and
            isinstance(denom, Sym) and denom.name == var and denom_power == 1):
            return Num(1)

        # arcsin(x)/x → 1
        if (isinstance(numer, Func) and numer.name == 'asin' and
            isinstance(numer.arg, Sym) and numer.arg.name == var and
            isinstance(denom, Sym) and denom.name == var and denom_power == 1):
            return Num(1)

        # arctan(x)/x → 1
        if (isinstance(numer, Func) and numer.name == 'atan' and
            isinstance(numer.arg, Sym) and numer.arg.name == var and
            isinstance(denom, Sym) and denom.name == var and denom_power == 1):
            return Num(1)

        # (e^x - 1)/x → 1
        if (isinstance(numer, Add) and len(numer.terms) == 2 and
            isinstance(denom, Sym) and denom.name == var and denom_power == 1):
            # Check for exp(x) - 1
            exp_term = None
            const_term = None
            for t in numer.terms:
                if isinstance(t, Func) and t.name == 'exp' and isinstance(t.arg, Sym) and t.arg.name == var:
                    exp_term = t
                elif isinstance(t, Neg) and isinstance(t.arg, Num) and t.arg.value == 1:
                    const_term = -1
                elif isinstance(t, Num):
                    const_term = t.value
            if exp_term is not None and const_term == -1:
                return Num(1)

        # (1 - cos(x))/x² → 1/2
        if (isinstance(numer, Add) and len(numer.terms) == 2 and
            isinstance(denom, Sym) and denom.name == var and denom_power == 2):
            # Check for 1 - cos(x)
            has_one = False
            has_neg_cos = False
            for t in numer.terms:
                if isinstance(t, Num) and t.value == 1:
                    has_one = True
                elif isinstance(t, Neg) and isinstance(t.arg, Func) and t.arg.name == 'cos':
                    if isinstance(t.arg.arg, Sym) and t.arg.arg.name == var:
                        has_neg_cos = True
            if has_one and has_neg_cos:
                return Num(Fraction(1, 2))

        # (exp(x) - 1 - x)/x² → 1/2
        # Parser may give exp(x) - (1 - x) = exp(x) - 1 + x, so check both forms
        # Also handle denom being Pow(x, 2) not just Sym(x)
        is_x_squared_denom = False
        if isinstance(denom, Sym) and denom.name == var and denom_power == 2:
            is_x_squared_denom = True
        elif isinstance(denom, Pow) and isinstance(denom.base, Sym) and denom.base.name == var:
            if isinstance(denom.exp, Num) and denom.exp.value == 2 and denom_power == 1:
                is_x_squared_denom = True

        if isinstance(numer, Add) and is_x_squared_denom:
            # Check for exp(x) - 1 - x pattern (may be parsed as exp(x) + Neg(Add(1, Neg(x))))
            exp_term = None
            other_terms = []
            for t in numer.terms:
                if isinstance(t, Func) and t.name == 'exp':
                    if isinstance(t.arg, Sym) and t.arg.name == var:
                        exp_term = t
                else:
                    other_terms.append(t)

            if exp_term is not None and len(other_terms) == 1:
                other = other_terms[0]
                # Check if other is -(1 - x) = -1 + x or -(1 + (-x)) = -1 - x
                if isinstance(other, Neg):
                    inner = other.arg
                    if isinstance(inner, Add) and len(inner.terms) == 2:
                        # Check for 1 - x or 1 + x
                        has_one = False
                        has_neg_x = False
                        has_x = False
                        for it in inner.terms:
                            if isinstance(it, Num) and it.value == 1:
                                has_one = True
                            elif isinstance(it, Neg) and isinstance(it.arg, Sym) and it.arg.name == var:
                                has_neg_x = True  # This is -x
                            elif isinstance(it, Sym) and it.name == var:
                                has_x = True  # This is x
                        # Parser gives -(1 - x) for input "exp(x) - 1 - x"
                        # has_one=True, has_neg_x=True -> user typed exp(x) - 1 - x, limit is 1/2
                        if has_one and has_neg_x:
                            return Num(Fraction(1, 2))
                        elif has_one and has_x:
                            # This is -(1 + x) = -1 - x, so numerator is exp(x) - 1 - x ✓
                            return Num(Fraction(1, 2))

        # ln(1 + x)/x → 1
        if (isinstance(numer, Func) and numer.name in ('ln', 'log') and
            isinstance(denom, Sym) and denom.name == var and denom_power == 1):
            # Check for ln(1 + x)
            arg = numer.arg
            if isinstance(arg, Add) and len(arg.terms) == 2:
                has_one = any(isinstance(t, Num) and t.value == 1 for t in arg.terms)
                has_x = any(isinstance(t, Sym) and t.name == var for t in arg.terms)
                if has_one and has_x:
                    return Num(1)

        return None

    def _try_lhopital(self, expr: Mul, var: str, point: float, depth: int) -> Optional[Expr]:
        """
        Apply L'Hôpital's rule for 0/0 indeterminate form.

        lim f(x)/g(x) = lim f'(x)/g'(x) when both f(a)=0 and g(a)=0
        """
        if depth >= self.MAX_LHOPITAL_DEPTH:
            return None

        # Separate numerator and denominator
        numer_parts = []
        denom_parts = []

        for f in expr.factors:
            if isinstance(f, Pow) and isinstance(f.exp, Num) and f.exp.value == -1:
                denom_parts.append(f.base)
            else:
                numer_parts.append(f)

        if len(denom_parts) != 1 or not numer_parts:
            return None

        numer = numer_parts[0] if len(numer_parts) == 1 else Mul(numer_parts)
        denom = denom_parts[0]

        # Check for 0/0 form
        numer_val = self._substitute(numer, var, point)
        denom_val = self._substitute(denom, var, point)

        if numer_val is None or denom_val is None:
            return None

        is_zero_zero = (self._is_zero(numer_val) and self._is_zero(denom_val))

        if not is_zero_zero:
            return None

        # Apply L'Hôpital: differentiate both
        numer_prime = self._diff_engine.differentiate(numer, var)
        denom_prime = self._diff_engine.differentiate(denom, var)

        # Try direct evaluation of f'/g'
        numer_prime_val = self._substitute(numer_prime, var, point)
        denom_prime_val = self._substitute(denom_prime, var, point)

        if numer_prime_val is not None and denom_prime_val is not None:
            if not self._is_zero(denom_prime_val):
                # Compute the ratio
                return self._divide(numer_prime_val, denom_prime_val)
            else:
                # Still 0/0, recurse
                new_expr = mul(numer_prime, power(denom_prime, Num(-1)))
                return self._try_lhopital(new_expr, var, point, depth + 1)

        return None

    def _try_e_definition(self, expr: Pow, var: str, positive: bool) -> Optional[Expr]:
        """
        Check for (1 + 1/x)^x → e pattern as x → ∞.

        Also handles: (1 + a/x)^(bx) → e^(ab)
        """
        base, exp = expr.base, expr.exp

        # Check if exponent contains x
        if not isinstance(exp, Sym) or exp.name != var:
            # Check for bx form
            if isinstance(exp, Mul):
                has_x = False
                coeff = 1
                for f in exp.factors:
                    if isinstance(f, Sym) and f.name == var:
                        has_x = True
                    elif isinstance(f, Num):
                        coeff = f.value
                if not has_x:
                    return None
                b = coeff
            else:
                return None
        else:
            b = 1

        # Check if base is 1 + a/x
        if isinstance(base, Add) and len(base.terms) == 2:
            has_one = False
            a = None
            for t in base.terms:
                if isinstance(t, Num) and t.value == 1:
                    has_one = True
                elif isinstance(t, Mul):
                    # Look for a/x = a * x^(-1)
                    for f in t.factors:
                        if isinstance(f, Num):
                            a = f.value
                        elif isinstance(f, Pow):
                            if (isinstance(f.base, Sym) and f.base.name == var and
                                isinstance(f.exp, Num) and f.exp.value == -1):
                                a = a or 1
                elif isinstance(t, Pow):
                    # Check for x^(-1)
                    if (isinstance(t.base, Sym) and t.base.name == var and
                        isinstance(t.exp, Num) and t.exp.value == -1):
                        a = 1

            if has_one and a is not None:
                # lim (1 + a/x)^(bx) = e^(ab)
                if a * b == 1:
                    return E
                else:
                    return Func('exp', Num(a * b))

        return None

    def _polynomial_ratio_limit(self, expr: Mul, var: str, positive: bool) -> Optional[Expr]:
        """
        Compute limit of polynomial ratio as x → ±∞.

        Compare leading degrees:
        - deg(numer) < deg(denom): → 0
        - deg(numer) > deg(denom): → ±∞
        - deg(numer) = deg(denom): → ratio of leading coefficients
        """
        # Separate numerator and denominator
        numer_parts = []
        denom_base = None

        for f in expr.factors:
            if isinstance(f, Pow) and isinstance(f.exp, Num) and f.exp.value == -1:
                denom_base = f.base
            else:
                numer_parts.append(f)

        if denom_base is None:
            return None

        numer = numer_parts[0] if len(numer_parts) == 1 else Mul(numer_parts)

        # Get degrees and leading coefficients
        numer_deg, numer_coeff = self._polynomial_info(numer, var)
        denom_deg, denom_coeff = self._polynomial_info(denom_base, var)

        if numer_deg is None or denom_deg is None:
            return None

        if numer_deg < denom_deg:
            return Num(0)
        elif numer_deg > denom_deg:
            # Infinity - direction depends on signs
            if positive:
                if numer_coeff * denom_coeff > 0:
                    return Sym('oo')  # +∞
                else:
                    return Neg(Sym('oo'))  # -∞
            return None
        else:
            # Equal degrees - ratio of coefficients
            return Num(Fraction(numer_coeff, denom_coeff) if isinstance(numer_coeff, int) and isinstance(denom_coeff, int) else numer_coeff / denom_coeff)

    def _polynomial_info(self, expr: Expr, var: str) -> Tuple[Optional[int], Optional[float]]:
        """
        Get degree and leading coefficient of polynomial.

        Returns (degree, leading_coefficient) or (None, None) if not polynomial.
        """
        # Single variable term
        if isinstance(expr, Sym):
            return (1, 1) if expr.name == var else (0, 1)

        # Constant
        if isinstance(expr, Num):
            return (0, expr.value)

        # x^n
        if isinstance(expr, Pow):
            if isinstance(expr.base, Sym) and expr.base.name == var:
                if isinstance(expr.exp, Num):
                    return (int(expr.exp.value), 1)
            return (None, None)

        # Sum - find highest degree term
        if isinstance(expr, Add):
            max_deg = -1
            lead_coeff = 0
            for t in expr.terms:
                deg, coeff = self._polynomial_info(t, var)
                if deg is None:
                    return (None, None)
                if deg > max_deg:
                    max_deg = deg
                    lead_coeff = coeff
                elif deg == max_deg:
                    lead_coeff += coeff
            return (max_deg, lead_coeff)

        # Product - sum degrees
        if isinstance(expr, Mul):
            total_deg = 0
            total_coeff = 1
            for f in expr.factors:
                deg, coeff = self._polynomial_info(f, var)
                if deg is None:
                    return (None, None)
                total_deg += deg
                total_coeff *= coeff
            return (total_deg, total_coeff)

        return (None, None)

    def _try_exp_domination(self, expr: Expr, var: str, positive: bool) -> Optional[Expr]:
        """Check for exponential domination patterns as x → ∞."""
        # e^x / polynomial → ∞
        # polynomial / e^x → 0
        if isinstance(expr, Mul):
            has_exp = False
            has_neg_exp = False

            for f in expr.factors:
                if isinstance(f, Func) and f.name == 'exp':
                    if self._contains_var(f.arg, var):
                        has_exp = True
                elif isinstance(f, Pow):
                    if isinstance(f.base, Func) and f.base.name == 'exp':
                        if isinstance(f.exp, Num) and f.exp.value < 0:
                            has_neg_exp = True

            if has_neg_exp and not has_exp:
                return Num(0)  # e^(-x) * polynomial → 0

        return None

    def _try_abs_patterns(self, expr: Expr, var: str, direction: Optional[str]) -> Optional[Expr]:
        """
        Handle limits involving absolute value at x → 0.

        Patterns:
        - abs(x)/x → 1 if dir='+', -1 if dir='-', DNE if no direction
        - x*abs(x) → 0 (continuous, doesn't need direction)
        - f(x)*abs(x)/x patterns
        """
        # Check for abs(x)/x pattern
        if isinstance(expr, Mul):
            has_abs_x = False
            has_x_neg1 = False
            other_factors = []

            for f in expr.factors:
                if isinstance(f, Func) and f.name == 'abs':
                    if isinstance(f.arg, Sym) and f.arg.name == var:
                        has_abs_x = True
                    else:
                        other_factors.append(f)
                elif isinstance(f, Pow):
                    if (isinstance(f.base, Sym) and f.base.name == var and
                        isinstance(f.exp, Num) and f.exp.value == -1):
                        has_x_neg1 = True
                    else:
                        other_factors.append(f)
                else:
                    other_factors.append(f)

            # abs(x)/x pattern
            if has_abs_x and has_x_neg1:
                if direction == '+':
                    base_result = Num(1)
                elif direction == '-':
                    base_result = Num(-1)
                else:
                    # Two-sided limit: left = -1, right = 1, so DNE
                    return Sym('DNE')

                # If there are other factors, multiply them at x=0
                if other_factors:
                    other_value = self._substitute(
                        other_factors[0] if len(other_factors) == 1 else Mul(other_factors),
                        var, 0.0
                    )
                    if other_value is not None and isinstance(other_value, Num):
                        return Num(base_result.value * other_value.value)
                return base_result

            # x * abs(x) pattern → 0
            if has_abs_x and not has_x_neg1:
                # Check for x factor
                for f in other_factors:
                    if isinstance(f, Sym) and f.name == var:
                        return Num(0)
                    if isinstance(f, Pow) and isinstance(f.base, Sym) and f.base.name == var:
                        if isinstance(f.exp, Num) and f.exp.value > 0:
                            return Num(0)

        return None

    def _try_taylor_expansion(self, expr: Expr, var: str) -> Optional[Expr]:
        """
        Use Taylor series expansions to evaluate limits at x → 0.

        Handles quotients where numerator and denominator can be expanded.
        Key expansions:
        - sin(x) = x - x³/6 + x⁵/120 - ...
        - cos(x) = 1 - x²/2 + x⁴/24 - ...
        - exp(x) = 1 + x + x²/2 + x³/6 + ...
        - log(1+x) = x - x²/2 + x³/3 - x⁴/4 + ...
        - tan(x) = x + x³/3 + 2x⁵/15 + ...
        """
        # Must be a quotient (Mul with negative power in denominator)
        if not isinstance(expr, Mul):
            return None

        # Separate numerator and denominator
        numer_parts = []
        denom_base = None
        denom_power = 1

        for f in expr.factors:
            if isinstance(f, Pow) and isinstance(f.exp, Num) and f.exp.value < 0:
                denom_base = f.base
                denom_power = -f.exp.value
            else:
                numer_parts.append(f)

        if denom_base is None:
            return None

        numer = numer_parts[0] if len(numer_parts) == 1 else Mul(numer_parts)

        # Get Taylor expansion of numerator
        numer_terms = self._get_taylor_terms(numer, var, max_order=8)
        if numer_terms is None:
            return None

        # Denominator should be x^n
        if not (isinstance(denom_base, Sym) and denom_base.name == var):
            # Check for power: x^n
            if isinstance(denom_base, Pow):
                if isinstance(denom_base.base, Sym) and denom_base.base.name == var:
                    if isinstance(denom_base.exp, Num):
                        denom_power *= denom_base.exp.value
                    else:
                        return None
                else:
                    return None
            else:
                return None

        # Convert denom_power to int
        denom_power = int(denom_power)

        # Find the coefficient of x^denom_power in numerator
        # The limit is that coefficient (since x^n / x^n = 1)
        if denom_power in numer_terms:
            coeff = numer_terms[denom_power]
            # Check that all lower powers are 0
            all_lower_zero = all(abs(numer_terms.get(k, 0)) < 1e-15 for k in range(denom_power))
            if all_lower_zero:
                return Num(Fraction(coeff).limit_denominator(10000) if isinstance(coeff, float) else coeff)

        return None

    def _get_taylor_terms(self, expr: Expr, var: str, max_order: int = 6) -> Optional[Dict[int, float]]:
        """
        Get Taylor series coefficients for an expression.

        Returns dict mapping power to coefficient: {0: c₀, 1: c₁, 2: c₂, ...}
        """
        # Handle Add: sum of terms
        if isinstance(expr, Add):
            result = {}
            for term in expr.terms:
                term_coeffs = self._get_taylor_terms(term, var, max_order)
                if term_coeffs is None:
                    return None
                for power, coeff in term_coeffs.items():
                    result[power] = result.get(power, 0) + coeff
            return result

        # Handle Neg
        if isinstance(expr, Neg):
            inner = self._get_taylor_terms(expr.arg, var, max_order)
            if inner is None:
                return None
            return {k: -v for k, v in inner.items()}

        # Handle Num (constant)
        if isinstance(expr, Num):
            return {0: expr.value}

        # Handle Sym (variable)
        if isinstance(expr, Sym):
            if expr.name == var:
                return {1: 1}
            else:
                return {0: 1}  # Other symbol treated as constant

        # Handle Pow: x^n
        if isinstance(expr, Pow):
            if isinstance(expr.base, Sym) and expr.base.name == var:
                if isinstance(expr.exp, Num):
                    n = int(expr.exp.value) if expr.exp.value == int(expr.exp.value) else None
                    if n is not None and n >= 0:
                        return {n: 1}
            # Handle coefficient * x^n
            if isinstance(expr.base, Sym) and expr.base.name == var:
                return None  # Non-integer power
            return None

        # Handle Mul: product of terms
        if isinstance(expr, Mul):
            # Extract coefficient and single Taylor-expandable term
            coeff = 1
            taylor_term = None
            power_of_x = 0

            for f in expr.factors:
                if isinstance(f, Num):
                    coeff *= f.value
                elif isinstance(f, Sym) and f.name == var:
                    power_of_x += 1
                elif isinstance(f, Pow):
                    if isinstance(f.base, Sym) and f.base.name == var and isinstance(f.exp, Num):
                        power_of_x += f.exp.value
                    else:
                        if taylor_term is not None:
                            return None  # Too complex
                        taylor_term = f
                elif isinstance(f, Func):
                    if taylor_term is not None:
                        return None  # Too complex
                    taylor_term = f
                elif isinstance(f, Add):
                    if taylor_term is not None:
                        return None
                    taylor_term = f
                else:
                    return None

            if taylor_term is not None:
                # Get Taylor expansion of the function term
                inner_terms = self._get_taylor_terms(taylor_term, var, max_order)
                if inner_terms is None:
                    return None
                # Multiply by x^power_of_x and coeff
                result = {}
                for p, c in inner_terms.items():
                    new_power = p + int(power_of_x)
                    if new_power <= max_order:
                        result[new_power] = c * coeff
                return result
            else:
                # Just coefficient * x^n
                return {int(power_of_x): coeff}

        # Handle Func: standard functions
        if isinstance(expr, Func):
            if isinstance(expr.arg, Sym) and expr.arg.name == var:
                return self._standard_taylor(expr.name, max_order)
            elif isinstance(expr.arg, Mul):
                # Handle f(a*x) case
                inner_coeff = 1
                for f in expr.arg.factors:
                    if isinstance(f, Num):
                        inner_coeff *= f.value
                    elif isinstance(f, Sym) and f.name == var:
                        pass  # This is x
                    else:
                        return None  # Too complex
                base_taylor = self._standard_taylor(expr.name, max_order)
                if base_taylor is None:
                    return None
                # For f(ax), coefficient of x^n is a^n * (coeff of x^n in f(x))
                return {k: v * (inner_coeff ** k) for k, v in base_taylor.items()}
            # Handle f(1 + x) for log
            elif isinstance(expr.arg, Add) and expr.name in ('ln', 'log'):
                # Check for 1 + x or 1 + ax
                terms = expr.arg.terms
                if len(terms) == 2:
                    has_one = False
                    x_coeff = 0
                    for t in terms:
                        if isinstance(t, Num) and t.value == 1:
                            has_one = True
                        elif isinstance(t, Sym) and t.name == var:
                            x_coeff = 1
                        elif isinstance(t, Mul):
                            for f in t.factors:
                                if isinstance(f, Num):
                                    x_coeff = f.value
                    if has_one and x_coeff != 0:
                        # log(1 + ax) = ax - (ax)²/2 + (ax)³/3 - ...
                        result = {}
                        for n in range(1, max_order + 1):
                            result[n] = ((-1) ** (n + 1)) * (x_coeff ** n) / n
                        return result

        return None

    def _standard_taylor(self, func_name: str, max_order: int = 6) -> Optional[Dict[int, float]]:
        """
        Return Taylor series coefficients for standard functions at x = 0.
        """
        import math

        if func_name == 'sin':
            # sin(x) = x - x³/6 + x⁵/120 - ...
            result = {}
            for n in range(max_order + 1):
                if n % 2 == 1:  # Only odd powers
                    k = n // 2
                    result[n] = ((-1) ** k) / math.factorial(n)
            return result

        elif func_name == 'cos':
            # cos(x) = 1 - x²/2 + x⁴/24 - ...
            result = {}
            for n in range(max_order + 1):
                if n % 2 == 0:  # Only even powers
                    k = n // 2
                    result[n] = ((-1) ** k) / math.factorial(n)
            return result

        elif func_name == 'exp':
            # exp(x) = 1 + x + x²/2 + x³/6 + ...
            result = {}
            for n in range(max_order + 1):
                result[n] = 1 / math.factorial(n)
            return result

        elif func_name in ('ln', 'log'):
            # log(1+x) = x - x²/2 + x³/3 - ... (this is for log(1+x), not log(x))
            # For log(x), we can't expand at 0
            result = {}
            for n in range(1, max_order + 1):
                result[n] = ((-1) ** (n + 1)) / n
            return result

        elif func_name == 'tan':
            # tan(x) = x + x³/3 + 2x⁵/15 + ...
            # Using Bernoulli numbers (complex), here are first few terms:
            return {1: 1, 3: 1/3, 5: 2/15}

        return None

    def _substitute(self, expr: Expr, var: str, value: float) -> Optional[Expr]:
        """
        Substitute variable with value in expression.
        """
        try:
            if isinstance(expr, Num):
                return expr
            elif isinstance(expr, Sym):
                if expr.name == var:
                    return Num(value)
                else:
                    return expr
            elif isinstance(expr, Add):
                terms = [self._substitute(t, var, value) for t in expr.terms]
                if all(isinstance(t, Num) for t in terms):
                    return Num(sum(t.value for t in terms))
                return Add(terms)
            elif isinstance(expr, Mul):
                factors = [self._substitute(f, var, value) for f in expr.factors]
                if all(isinstance(f, Num) for f in factors):
                    result = 1
                    for f in factors:
                        result *= f.value
                    return Num(result)
                return Mul(factors)
            elif isinstance(expr, Pow):
                base = self._substitute(expr.base, var, value)
                exp = self._substitute(expr.exp, var, value)
                if isinstance(base, Num) and isinstance(exp, Num):
                    try:
                        return Num(base.value ** exp.value)
                    except (ValueError, OverflowError):
                        return None
                return Pow(base, exp)
            elif isinstance(expr, Neg):
                arg = self._substitute(expr.arg, var, value)
                if isinstance(arg, Num):
                    return Num(-arg.value)
                return Neg(arg)
            elif isinstance(expr, Func):
                arg = self._substitute(expr.arg, var, value)
                if isinstance(arg, Num):
                    return self._eval_func(expr.name, arg.value)
                return Func(expr.name, arg)
            return None
        except:
            return None

    def _eval_func(self, name: str, value: float) -> Optional[Expr]:
        """Evaluate function at numeric value."""
        try:
            if name == 'sin':
                return Num(math.sin(value))
            elif name == 'cos':
                return Num(math.cos(value))
            elif name == 'tan':
                return Num(math.tan(value))
            elif name == 'exp':
                return Num(math.exp(value))
            elif name in ('ln', 'log'):
                if value > 0:
                    return Num(math.log(value))
            elif name == 'abs':
                return Num(abs(value))
            elif name == 'sqrt':
                if value >= 0:
                    return Num(math.sqrt(value))
            elif name == 'asin':
                if -1 <= value <= 1:
                    return Num(math.asin(value))
            elif name == 'atan':
                return Num(math.atan(value))
            return None
        except:
            return None

    def _is_indeterminate(self, expr: Expr) -> bool:
        """Check if expression is indeterminate form."""
        if isinstance(expr, Sym) and expr.name in ('nan', 'undefined', 'DNE'):
            return True
        return False

    def _is_zero(self, expr: Expr) -> bool:
        """Check if expression is zero."""
        if isinstance(expr, Num):
            return abs(expr.value) < 1e-10
        return False

    def _divide(self, numer: Expr, denom: Expr) -> Optional[Expr]:
        """Divide two expressions."""
        if isinstance(numer, Num) and isinstance(denom, Num):
            if abs(denom.value) < 1e-15:
                return None
            return Num(numer.value / denom.value)
        return mul(numer, power(denom, Num(-1)))

    def _contains_var(self, expr: Expr, var: str) -> bool:
        """Check if expression contains variable."""
        if isinstance(expr, Sym):
            return expr.name == var
        elif isinstance(expr, (Add, Mul)):
            children = expr.terms if isinstance(expr, Add) else expr.factors
            return any(self._contains_var(child, var) for child in children)
        elif isinstance(expr, Pow):
            return self._contains_var(expr.base, var) or self._contains_var(expr.exp, var)
        elif isinstance(expr, Neg):
            return self._contains_var(expr.arg, var)
        elif isinstance(expr, Func):
            return self._contains_var(expr.arg, var)
        return False


def native_limit(expr_str: str, var: str, point: str, direction: str = 'both') -> Tuple[bool, Optional[str], str]:
    """
    Native limit evaluation using pure Python implementation.

    This is the main entry point for limit evaluation, combining pattern matching,
    Taylor series, L'Hôpital's rule, and special function asymptotics.

    Args:
        expr_str: Expression string to evaluate limit of
        var: Variable name
        point: Limit point ('0', 'oo', 'inf', or numeric string)
        direction: Direction for one-sided limits ('both', 'left', 'right', '+', '-')

    Returns:
        (success, result_str, method) where:
        - success: True if limit was computed
        - result_str: String representation of limit value
        - method: Method used to compute limit
    """
    try:
        # Safety check
        if not _check_expression_safety(expr_str):
            return False, None, "unsafe_expression"

        # Normalize point notation
        point_normalized = point.lower().strip()
        if point_normalized in ('inf', 'infinity', '+inf', '+oo'):
            point_normalized = 'oo'
            numeric_point = float('inf')
        elif point_normalized in ('-inf', '-infinity', '-oo'):
            point_normalized = '-oo'
            numeric_point = float('-inf')
        else:
            try:
                numeric_point = float(point_normalized)
            except ValueError:
                return False, None, "invalid_point"

        # Try LimitEngine first (handles Expr-based computation)
        try:
            parsed = _parser.parse(expr_str)
            engine = LimitEngine()
            result = engine.limit(parsed, var, numeric_point, direction if direction != 'both' else None)
            if result is not None:
                # Convert result to string
                if isinstance(result, Num):
                    if isinstance(result.value, Fraction):
                        return True, str(result.value), "limit_engine"
                    return True, str(result.value), "limit_engine"
                elif isinstance(result, Sym):
                    return True, result.name, "limit_engine"
                return True, str(result), "limit_engine"
        except Exception as e:
            logger.debug(f"LimitEngine failed: {e}")

        # Try known patterns (string-based)
        pattern_result = _try_known_limit_pattern(expr_str, var, point_normalized)
        if pattern_result is not None:
            result, method = pattern_result
            return True, result, method

        # Try special function asymptotics
        if math.isinf(numeric_point):
            async_result = _try_special_function_asymptotic(expr_str, var, numeric_point)
            if async_result is not None:
                return True, async_result, "special_function_asymptotic"

        # Try Taylor expansion limit
        if abs(numeric_point) < 1e-10:
            taylor_result = _try_taylor_expansion_limit(expr_str, var)
            if taylor_result is not None:
                return True, taylor_result, "taylor_expansion"

        # Try nested log limit
        if math.isinf(numeric_point) and numeric_point > 0:
            nested_log_result = _try_nested_log_limit(expr_str, var, numeric_point)
            if nested_log_result is not None:
                return True, nested_log_result, "nested_log"

        # Try Stirling limit
        if math.isinf(numeric_point) and numeric_point > 0:
            stirling_result = _try_stirling_limit(expr_str, var, numeric_point)
            if stirling_result is not None:
                return True, stirling_result, "stirling"

        # Try asymptotic difference limit
        if math.isinf(numeric_point):
            diff_result = _try_asymptotic_difference_limit(expr_str, var, numeric_point)
            if diff_result is not None:
                return True, diff_result, "asymptotic_difference"

        # Try limit with assumptions
        assumption_result = _try_limit_with_assumptions(expr_str, var, point_normalized)
        if assumption_result is not None:
            result, method = assumption_result
            return True, result, method

        # Try one-sided divergent limit
        if direction != 'both':
            one_sided_result = _try_one_sided_divergent_limit(expr_str, var, numeric_point, direction)
            if one_sided_result is not None:
                return True, one_sided_result, "one_sided_divergent"

        # Try specialized pattern limits
        if math.isinf(numeric_point) and numeric_point > 0:
            # Try oscillatory decay
            osc_decay = _try_oscillatory_decay_limit(expr_str, var, numeric_point)
            if osc_decay is not None:
                return True, osc_decay, "oscillatory_decay"

            # Try power decay
            power_decay = _try_power_decay_limit(expr_str, var, numeric_point)
            if power_decay is not None:
                return True, power_decay, "power_decay"

            # Try log/polynomial
            log_poly = _try_log_polynomial_limit(expr_str, var, numeric_point)
            if log_poly is not None:
                return True, log_poly, "log_polynomial"

            # Try exp/polynomial
            exp_poly = _try_exp_polynomial_limit(expr_str, var, numeric_point)
            if exp_poly is not None:
                return True, exp_poly, "exp_polynomial"

            # Try pure oscillatory
            pure_osc = _try_pure_oscillatory_limit(expr_str, var, numeric_point)
            if pure_osc is not None:
                return True, pure_osc, "pure_oscillatory"

            # Try e-type limit
            e_type = _try_e_type_limit(expr_str, var, numeric_point)
            if e_type is not None:
                return True, e_type, "e_type"

        # Try constant limit
        const_result = _try_constant_limit(expr_str, var, numeric_point)
        if const_result is not None:
            return True, const_result, "constant"

        # Try direct substitution
        direct_result = _try_direct_substitution(expr_str, var, numeric_point)
        if direct_result is not None:
            return True, direct_result, "direct_substitution"

        # Try sinc limit (x→0)
        if abs(numeric_point) < 1e-10:
            sinc_result = _try_sinc_limit(expr_str, var)
            if sinc_result is not None:
                return True, sinc_result, "sinc"

            # Try one minus cos
            one_cos_result = _try_one_minus_cos_limit(expr_str, var)
            if one_cos_result is not None:
                return True, one_cos_result, "one_minus_cos"

            # Try one minus cos squared
            one_cos_sq_result = _try_one_minus_cos_sq_limit(expr_str, var)
            if one_cos_sq_result is not None:
                return True, one_cos_sq_result, "one_minus_cos_sq"

        return False, None, "no_method_found"

    except Exception as e:
        logger.error(f"Error in native_limit: {e}")
        return False, None, f"error: {str(e)}"


# Export main components
__all__ = [
    'LimitEngine',
    'native_limit',
    'KNOWN_LIMIT_PATTERNS',
    'PARAMETER_ASSUMPTIONS',
    'taylor_series',
    'solve_polynomial',
    'solve_system_native',
    'factor_polynomial',
    'expand_expression',
    'solve_ode_native',
    'definite_integrate_2d',
]
