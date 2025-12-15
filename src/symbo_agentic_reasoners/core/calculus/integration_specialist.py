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
Integration Specialist
======================

Pure Python symbolic integration engine using pattern-based rules.

Integration Methods:
- Basic table lookup (sin, cos, exp, etc.)
- Power rule: ∫x^n dx = x^(n+1)/(n+1)
- Constant multiple rule: ∫c*f dx = c*∫f dx
- Sum rule: ∫(f+g) dx = ∫f dx + ∫g dx
- Integration by parts using LIATE rule
- Simple u-substitution patterns
- Trig power reduction (sin^n, cos^n)
- Partial fractions (limited)
"""

import logging
import math
import re
from typing import Optional, List, Tuple, Union, Dict, Any
from fractions import Fraction
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from .differentiation_specialist import DifferentiationEngine

logger = logging.getLogger(__name__)

# Import components from native_calculus for definite_integrate and helpers
# These will be imported when needed to avoid circular dependencies
try:
    from ..native_calculus import (
        _parser, _int_engine, _check_expression_safety,
        _fix_exponent_precedence_inline, _simplify_output,
        _evaluate_at, _evaluate_limit, _analyze_singularities,
        _check_symmetry_integral, _check_log_power_integral
    )
except ImportError:
    # Fallback if imports fail
    _parser = None
    _int_engine = None


def _try_evaluate_const(expr: Expr) -> Optional[float]:
    """Try to evaluate an expression as a constant."""
    if isinstance(expr, Num):
        return float(expr.value)
    elif isinstance(expr, Neg):
        inner = _try_evaluate_const(expr.arg)
        return -inner if inner is not None else None
    elif isinstance(expr, Mul):
        result = 1.0
        for factor in expr.factors:
            val = _try_evaluate_const(factor)
            if val is None:
                return None
            result *= val
        return result
    elif isinstance(expr, Add):
        result = 0.0
        for term in expr.terms:
            val = _try_evaluate_const(term)
            if val is None:
                return None
            result += val
        return result
    elif isinstance(expr, Pow):
        base_val = _try_evaluate_const(expr.base)
        exp_val = _try_evaluate_const(expr.exp)
        if base_val is not None and exp_val is not None:
            return base_val ** exp_val
    return None

class IntegrationEngine:
    """
    Pure Python symbolic integration engine.

    Implements pattern-based integration rules without SymPy.
    Returns None if integration cannot be performed.

    INTEGRATION METHODS:
    -------------------
    1. Basic table lookup (sin, cos, exp, etc.)
    2. Power rule (x^n -> x^(n+1)/(n+1))
    3. Constant multiple rule (c*f -> c*∫f)
    4. Sum rule (f+g -> ∫f + ∫g)
    5. Integration by parts (∫u dv = uv - ∫v du) using LIATE rule
    6. Simple u-substitution (limited patterns)
    """

    # Basic antiderivatives: f -> ∫f dx (as function of argument)
    BASIC_INTEGRALS = {
        'sin': lambda x: neg(Func('cos', x)),
        'cos': lambda x: Func('sin', x),
        'sec': lambda x: Func('ln', add(Func('sec', x), Func('tan', x))),
        'csc': lambda x: neg(Func('ln', add(Func('csc', x), Func('cot', x)))),
        'tan': lambda x: neg(Func('ln', Func('cos', x))),
        'cot': lambda x: Func('ln', Func('sin', x)),
        'exp': lambda x: Func('exp', x),
        'sinh': lambda x: Func('cosh', x),
        'cosh': lambda x: Func('sinh', x),
    }

    # LIATE priority for integration by parts (higher = choose as u first)
    # L = Logarithmic, I = Inverse trig, A = Algebraic, T = Trig, E = Exponential
    LIATE_PRIORITY = {
        'ln': 5, 'log': 5,  # Logarithmic
        'asin': 4, 'acos': 4, 'atan': 4, 'asec': 4, 'acsc': 4, 'acot': 4,  # Inverse trig
        # Algebraic (polynomials) = 3 (handled specially)
        'sin': 2, 'cos': 2, 'tan': 2, 'sec': 2, 'csc': 2, 'cot': 2,  # Trig
        'exp': 1, 'sinh': 1, 'cosh': 1, 'tanh': 1,  # Exponential
    }

    def integrate(self, expr: Expr, var: str) -> Optional[Expr]:
        """
        Integrate expression with respect to variable.

        Args:
            expr: Expression to integrate
            var: Variable name (e.g., 'x')

        Returns:
            Antiderivative expression, or None if cannot integrate
        """
        result = self._integrate(expr, var)
        if result is not None:
            logger.debug(f"[DOMAIN] Integrated {expr} to {result}")
        return result

    def _integrate(self, expr: Expr, var: str) -> Optional[Expr]:
        """Internal integration dispatcher."""

        # Constant: ∫c dx = c*x
        if isinstance(expr, Num):
            return mul(expr, Sym(var))

        # Symbol that IS the variable: ∫x dx = x^2/2
        if isinstance(expr, Sym):
            if expr.name == var:
                return mul(Num(Fraction(1, 2)), power(Sym(var), Num(2)))
            else:
                # Constant symbol: ∫a dx = a*x
                return mul(expr, Sym(var))

        # Negation: ∫(-f) dx = -∫f dx
        if isinstance(expr, Neg):
            inner = self._integrate(expr.arg, var)
            return neg(inner) if inner is not None else None

        # Sum: ∫(f + g) dx = ∫f dx + ∫g dx
        if isinstance(expr, Add):
            results = []
            for term in expr.terms:
                r = self._integrate(term, var)
                if r is None:
                    return None  # Cannot integrate one term
                results.append(r)
            return add(*results)

        # Product: check for coefficient * f pattern
        if isinstance(expr, Mul):
            return self._integrate_product(expr, var)

        # Power: ∫x^n dx = x^(n+1)/(n+1) for n ≠ -1
        if isinstance(expr, Pow):
            result = self._integrate_power(expr, var)
            if result is not None:
                return result
            # Try inverse sqrt integrals: 1/√(x²+a²), 1/√(a²-x²)
            result = self._try_inverse_sqrt_integral(expr, var)
            if result is not None:
                return result
            # Try partial fractions for 1/(something)
            result = self._try_partial_fractions(expr, var)
            if result is not None:
                return result

        # Function: check basic table
        if isinstance(expr, Func):
            return self._integrate_func(expr, var)

        return None  # Cannot integrate

    def _integrate_product(self, expr: Mul, var: str, depth: int = 0) -> Optional[Expr]:
        """
        Integrate a product.

        Handles:
        1. c * f(x) -> c * ∫f dx (constant multiple)
        2. u * dv -> uv - ∫v du (integration by parts with LIATE)

        Args:
            expr: Product expression
            var: Variable to integrate with respect to
            depth: Recursion depth to prevent infinite loops
        """
        # Limit recursion depth for integration by parts
        MAX_DEPTH = 3

        factors = expr.factors

        # Separate constants from variable-dependent parts
        constants = []
        variable_parts = []

        for f in factors:
            if not self._contains_var(f, var):
                constants.append(f)
            else:
                variable_parts.append(f)

        if not variable_parts:
            # All constant: ∫c dx = c*x
            return mul(*constants, Sym(var))

        if len(variable_parts) == 1:
            # c * f(x) -> c * ∫f dx
            inner = self._integrate(variable_parts[0], var)
            if inner is not None:
                return mul(*constants, inner) if constants else inner

        # Integration by parts: ∫u dv = uv - ∫v du
        if len(variable_parts) == 2 and depth < MAX_DEPTH:
            result = self._try_integration_by_parts(variable_parts[0], variable_parts[1], var, depth)
            if result is not None:
                return mul(*constants, result) if constants else result

        # Try inverse sqrt patterns: x/√(x²+a²), x/√(a²-x²)
        result = self._try_inverse_sqrt_integral(expr, var)
        if result is not None:
            return mul(*constants, result) if constants else result

        # Try partial fractions for quotients (e.g., x/(x^2+1))
        result = self._try_partial_fractions(expr, var)
        if result is not None:
            return mul(*constants, result) if constants else result

        # Multiple variable parts - cannot handle in general
        return None

    def _try_integration_by_parts(self, f1: Expr, f2: Expr, var: str, depth: int) -> Optional[Expr]:
        """
        Try integration by parts using LIATE rule.

        ∫u dv = uv - ∫v du

        LIATE rule determines which factor to choose as u:
        L = Logarithmic (ln, log) - priority 5
        I = Inverse trig (asin, acos, atan) - priority 4
        A = Algebraic (polynomials) - priority 3
        T = Trigonometric (sin, cos, tan) - priority 2
        E = Exponential (exp, e^x) - priority 1

        Choose the factor with HIGHER priority as u.
        """
        # Get LIATE priority for each factor
        p1 = self._get_liate_priority(f1, var)
        p2 = self._get_liate_priority(f2, var)

        # Choose u (higher priority) and dv (lower priority)
        if p1 >= p2:
            u, dv = f1, f2
        else:
            u, dv = f2, f1

        # Compute du = d(u)/dx
        diff_engine = DifferentiationEngine()
        du = diff_engine.differentiate(u, var)

        # Compute v = ∫dv dx
        v = self._integrate(dv, var)
        if v is None:
            # Can't integrate dv, try swapping u and dv
            u, dv = dv, u
            du = diff_engine.differentiate(u, var)
            v = self._integrate(dv, var)
            if v is None:
                return None

        # ∫u dv = u*v - ∫v*du
        uv = mul(u, v)

        # Compute ∫v*du
        v_du = mul(v, du)

        # Need to integrate v*du
        if isinstance(v_du, Mul):
            integral_v_du = self._integrate_product(v_du, var, depth + 1)
        else:
            integral_v_du = self._integrate(v_du, var)

        if integral_v_du is None:
            return None

        # Result: uv - ∫v du
        return add(uv, neg(integral_v_du))

    def _get_liate_priority(self, expr: Expr, var: str) -> int:
        """
        Get LIATE priority for expression.

        L = 5 (Logarithmic)
        I = 4 (Inverse trig)
        A = 3 (Algebraic/Polynomial)
        T = 2 (Trigonometric)
        E = 1 (Exponential)
        """
        # Functions have priority based on type
        if isinstance(expr, Func):
            fname = expr.name
            if fname in self.LIATE_PRIORITY:
                return self.LIATE_PRIORITY[fname]
            return 0

        # Algebraic expressions (polynomials, x^n, etc.)
        if isinstance(expr, (Sym, Pow)):
            # Check if it's purely algebraic (no transcendental functions)
            if self._is_algebraic(expr, var):
                return 3
            return 0

        if isinstance(expr, Num):
            return 0

        if isinstance(expr, Mul):
            # Product of expressions - take max priority
            return max(self._get_liate_priority(f, var) for f in expr.factors)

        if isinstance(expr, Add):
            # Sum - take max priority
            return max(self._get_liate_priority(t, var) for t in expr.terms)

        return 0

    def _is_algebraic(self, expr: Expr, var: str) -> bool:
        """Check if expression is purely algebraic (polynomial, rational)."""
        if isinstance(expr, Num):
            return True
        if isinstance(expr, Sym):
            return True  # Variables are algebraic
        if isinstance(expr, Neg):
            return self._is_algebraic(expr.arg, var)
        if isinstance(expr, Add):
            return all(self._is_algebraic(t, var) for t in expr.terms)
        if isinstance(expr, Mul):
            return all(self._is_algebraic(f, var) for f in expr.factors)
        if isinstance(expr, Pow):
            # x^n is algebraic if n is a number
            if isinstance(expr.exp, Num):
                return self._is_algebraic(expr.base, var)
            return False
        if isinstance(expr, Func):
            return False  # Functions like sin, exp are not algebraic
        return False

    def _integrate_power(self, expr: Pow, var: str) -> Optional[Expr]:
        """
        Integrate power expression.

        ∫x^n dx = x^(n+1)/(n+1) for n ≠ -1
        ∫x^(-1) dx = ln|x|
        ∫sin^n(x) dx, ∫cos^n(x) dx - use trig power identities
        """
        base, exp = expr.base, expr.exp

        # Check for trig powers first: sin^n(x), cos^n(x)
        if isinstance(base, Func) and base.name in ('sin', 'cos'):
            result = self._integrate_trig_power(expr, var)
            if result is not None:
                return result

        # Only handle x^n where base is the variable
        if isinstance(base, Sym) and base.name == var and not self._contains_var(exp, var):
            # Check for x^(-1) -> ln(x)
            if isinstance(exp, Num) and exp.value == -1:
                return Func('ln', Func('Abs', base))

            # Power rule: x^n -> x^(n+1)/(n+1)
            n_plus_1 = self._add_one(exp)
            return mul(power(Num(1), Num(-1)), power(base, n_plus_1), power(n_plus_1, Num(-1)))

        # Handle (f(x))^n where f is simple
        if not self._contains_var(exp, var):
            # Could use substitution, but skip for now
            pass

        return None

    def _integrate_func(self, expr: Func, var: str) -> Optional[Expr]:
        """
        Integrate standard functions.

        Uses table lookup for basic cases.
        Also handles special cases like ln(x) via integration by parts.
        """
        fname = expr.name
        arg = expr.arg

        # Only handle f(x) where arg is just the variable
        if isinstance(arg, Sym) and arg.name == var:
            if fname in self.BASIC_INTEGRALS:
                return self.BASIC_INTEGRALS[fname](arg)

            # Special case: ∫ln(x) dx = x*ln(x) - x
            # Derived via integration by parts: u = ln(x), dv = dx
            # du = 1/x dx, v = x
            # ∫ln(x) dx = x*ln(x) - ∫x*(1/x) dx = x*ln(x) - x
            if fname in ('ln', 'log'):
                x = Sym(var)
                # x*ln(x) - x
                return add(mul(x, expr), neg(x))

        # Handle f(ax) -> (1/a) * F(ax) using chain rule in reverse
        if isinstance(arg, Mul) and len(arg.factors) == 2:
            factors = arg.factors
            if isinstance(factors[0], Num) and isinstance(factors[1], Sym) and factors[1].name == var:
                coeff = factors[0].value
                if fname in self.BASIC_INTEGRALS:
                    F = self.BASIC_INTEGRALS[fname](arg)
                    return mul(Num(Fraction(1, coeff)), F)

                # Special case: ∫ln(ax) dx = x*ln(ax) - x
                if fname in ('ln', 'log'):
                    x = Sym(var)
                    return add(mul(x, expr), neg(x))

        return None

    def _integrate_trig_power(self, expr: Pow, var: str) -> Optional[Expr]:
        """
        Integrate trig powers like sin^n(x), cos^n(x) using identities.

        IDENTITIES USED:
        ---------------
        - sin²(x) = (1 - cos(2x))/2
        - cos²(x) = (1 + cos(2x))/2
        - sin²(x) + cos²(x) = 1
        - ∫sin^n(x) dx = -sin^(n-1)(x)cos(x)/n + (n-1)/n ∫sin^(n-2)(x) dx
        - ∫cos^n(x) dx = cos^(n-1)(x)sin(x)/n + (n-1)/n ∫cos^(n-2)(x) dx
        """
        base, exp = expr.base, expr.exp

        # Only handle trig^n where n is a positive integer
        if not isinstance(base, Func):
            return None
        if not isinstance(exp, Num) or not isinstance(exp.value, int) or exp.value < 2:
            return None

        fname = base.name
        arg = base.arg
        n = exp.value

        # Only handle sin^n(x) and cos^n(x) where arg is the variable
        if not isinstance(arg, Sym) or arg.name != var:
            return None

        if fname == 'sin':
            return self._integrate_sin_power(n, var)
        elif fname == 'cos':
            return self._integrate_cos_power(n, var)

        return None

    def _integrate_sin_power(self, n: int, var: str) -> Optional[Expr]:
        """
        Integrate sin^n(x) dx.

        For n=2: sin²(x) = (1 - cos(2x))/2
                 ∫sin²(x) dx = x/2 - sin(2x)/4

        For n even: use half-angle identity
        For n odd: use sin^(2k+1)(x) = sin(x)(1-cos²(x))^k then substitute u=cos(x)
        """
        x = Sym(var)

        if n == 2:
            # ∫sin²(x) dx = x/2 - sin(2x)/4
            return add(
                mul(Num(Fraction(1, 2)), x),
                neg(mul(Num(Fraction(1, 4)), Func('sin', mul(Num(2), x))))
            )

        if n == 3:
            # ∫sin³(x) dx = -cos(x) + cos³(x)/3
            return add(
                neg(Func('cos', x)),
                mul(Num(Fraction(1, 3)), power(Func('cos', x), Num(3)))
            )

        if n == 4:
            # ∫sin⁴(x) dx = 3x/8 - sin(2x)/4 + sin(4x)/32
            return add(
                mul(Num(Fraction(3, 8)), x),
                neg(mul(Num(Fraction(1, 4)), Func('sin', mul(Num(2), x)))),
                mul(Num(Fraction(1, 32)), Func('sin', mul(Num(4), x)))
            )

        # For higher powers, use reduction formula:
        # ∫sin^n(x) dx = -sin^(n-1)(x)cos(x)/n + (n-1)/n ∫sin^(n-2)(x) dx
        if n > 4 and n % 2 == 0:
            # Even power - reduce
            prev_int = self._integrate_sin_power(n - 2, var)
            if prev_int is None:
                return None
            return add(
                mul(Num(Fraction(-1, n)), power(Func('sin', x), Num(n - 1)), Func('cos', x)),
                mul(Num(Fraction(n - 1, n)), prev_int)
            )

        return None

    def _integrate_cos_power(self, n: int, var: str) -> Optional[Expr]:
        """
        Integrate cos^n(x) dx.

        For n=2: cos²(x) = (1 + cos(2x))/2
                 ∫cos²(x) dx = x/2 + sin(2x)/4

        For n even: use half-angle identity
        For n odd: use cos^(2k+1)(x) = cos(x)(1-sin²(x))^k then substitute u=sin(x)
        """
        x = Sym(var)

        if n == 2:
            # ∫cos²(x) dx = x/2 + sin(2x)/4
            return add(
                mul(Num(Fraction(1, 2)), x),
                mul(Num(Fraction(1, 4)), Func('sin', mul(Num(2), x)))
            )

        if n == 3:
            # ∫cos³(x) dx = sin(x) - sin³(x)/3
            return add(
                Func('sin', x),
                neg(mul(Num(Fraction(1, 3)), power(Func('sin', x), Num(3))))
            )

        if n == 4:
            # ∫cos⁴(x) dx = 3x/8 + sin(2x)/4 + sin(4x)/32
            return add(
                mul(Num(Fraction(3, 8)), x),
                mul(Num(Fraction(1, 4)), Func('sin', mul(Num(2), x))),
                mul(Num(Fraction(1, 32)), Func('sin', mul(Num(4), x)))
            )

        # For higher powers, use reduction formula:
        # ∫cos^n(x) dx = cos^(n-1)(x)sin(x)/n + (n-1)/n ∫cos^(n-2)(x) dx
        if n > 4 and n % 2 == 0:
            # Even power - reduce
            prev_int = self._integrate_cos_power(n - 2, var)
            if prev_int is None:
                return None
            return add(
                mul(Num(Fraction(1, n)), power(Func('cos', x), Num(n - 1)), Func('sin', x)),
                mul(Num(Fraction(n - 1, n)), prev_int)
            )

        return None

    # =========================================================================
    # PARTIAL FRACTIONS INTEGRATION
    # =========================================================================

    def _try_partial_fractions(self, expr: Expr, var: str) -> Optional[Expr]:
        """
        Try to integrate a rational function using partial fractions.

        SUPPORTED PATTERNS:
        ------------------
        1. A/(x - a) -> A*ln|x - a|
        2. A/(x - a)^n -> A/(1-n) * (x - a)^(1-n)  for n > 1
        3. 1/(x^2 + a^2) -> (1/a)*arctan(x/a)
        4. x/(x^2 + a^2) -> (1/2)*ln(x^2 + a^2)
        5. 1/(x^2 - a^2) -> (1/2a)*ln|(x-a)/(x+a)|
        6. A/(ax + b) -> (A/a)*ln|ax + b|

        For more complex cases, attempts coefficient matching for
        simple partial fraction decomposition.
        """
        # Check if this is a quotient (expressed as power with negative exponent)
        if isinstance(expr, Mul):
            # Look for pattern: numerator * denominator^(-1)
            result = self._try_integrate_quotient(expr, var)
            if result is not None:
                return result

        if isinstance(expr, Pow):
            # Check for 1/(something)
            if isinstance(expr.exp, Num) and expr.exp.value == -1:
                return self._integrate_reciprocal(expr.base, var)
            elif isinstance(expr.exp, Num) and expr.exp.value < 0:
                # A/(x-a)^n pattern
                return self._integrate_reciprocal_power(expr, var)

        return None

    def _try_integrate_quotient(self, expr: Mul, var: str) -> Optional[Expr]:
        """
        Try to integrate a quotient expressed as a Mul with negative power.

        Handles patterns like: A * (x - a)^(-1), x * (x^2 + 1)^(-1), etc.
        """
        # Separate factors into numerator parts and denominator parts
        numer_parts = []
        denom_parts = []

        for f in expr.factors:
            if isinstance(f, Pow) and isinstance(f.exp, Num) and f.exp.value < 0:
                # This is a 1/something^n term
                denom_parts.append((f.base, -f.exp.value))
            else:
                numer_parts.append(f)

        if not denom_parts:
            return None  # Not a quotient

        # For now, handle simple cases with single denominator
        if len(denom_parts) == 1:
            base, power_val = denom_parts[0]
            numer = mul(*numer_parts) if numer_parts else Num(1)

            # Case: constant / (linear)^n
            if not self._contains_var(numer, var):
                return self._integrate_const_over_polynomial(numer, base, power_val, var)

            # Case: x / (x^2 + a^2) -> (1/2) * ln(x^2 + a^2)
            if power_val == 1:
                result = self._try_log_derivative_pattern(numer, base, var)
                if result is not None:
                    return result

                # Case: x^2 / (x^4 + 1) - quartic with x² numerator
                result = self._try_x_squared_over_quartic_integral(numer, base, var)
                if result is not None:
                    return result

                # Case: (x^2 + 1) / (x^4 + 1) - quartic with x²+1 numerator
                result = self._try_x_sq_plus_one_over_quartic_integral(numer, base, var)
                if result is not None:
                    return result

                # Case: (x^2 - 1) / (x^4 + 1) - quartic with x²-1 numerator
                result = self._try_x_sq_minus_one_over_quartic_integral(numer, base, var)
                if result is not None:
                    return result

                # Case: x / (x^4 + 1) - single x numerator
                result = self._try_x_over_quartic_integral(numer, base, var)
                if result is not None:
                    return result

                # Case: x^3 / (x^4 + 1) - log derivative pattern
                result = self._try_x_cubed_over_quartic_integral(numer, base, var)
                if result is not None:
                    return result

        return None

    def _integrate_const_over_polynomial(self, const: Expr, denom: Expr, power: float, var: str) -> Optional[Expr]:
        """
        Integrate C / (polynomial)^n.

        Handles:
        - C/(x - a) -> C*ln|x - a|
        - C/(ax + b) -> (C/a)*ln|ax + b|
        - C/(x - a)^n -> C/(1-n) * (x - a)^(1-n)
        - C/(x^2 + a^2) -> (C/a)*arctan(x/a)
        """
        x = Sym(var)

        # Case 1: C/(x - a) or C/(ax + b) where power = 1
        if power == 1:
            # Check for linear: ax + b
            if isinstance(denom, Add) and len(denom.terms) == 2:
                # Try to identify ax + b
                coeff_x, const_term = self._extract_linear_coeffs(denom, var)
                if coeff_x is not None:
                    # ∫C/(ax + b) dx = (C/a) * ln|ax + b|
                    result_coeff = mul(const, power(Num(coeff_x), Num(-1)))
                    return mul(result_coeff, Func('ln', Func('Abs', denom)))

            # Check for just x
            if isinstance(denom, Sym) and denom.name == var:
                # ∫C/x dx = C * ln|x|
                return mul(const, Func('ln', Func('Abs', x)))

            # Check for (x - a) or (x + a) form
            if isinstance(denom, Add):
                result = self._try_ln_integral(const, denom, var)
                if result is not None:
                    return result

            # Check for x^2 + a^2 pattern
            arctan_result = self._try_arctan_integral(const, denom, var)
            if arctan_result is not None:
                return arctan_result

            # Check for x^4 + 1 pattern (quartic rational integral)
            quartic_result = self._try_quartic_plus_one_integral(const, denom, var)
            if quartic_result is not None:
                return quartic_result

        # Case 2: C/(x - a)^n where n > 1
        if power > 1 and isinstance(power, int):
            n = int(power)
            # Check for linear denominator
            if isinstance(denom, Sym) and denom.name == var:
                # ∫C/x^n dx = C * x^(1-n) / (1-n)
                new_exp = 1 - n
                return mul(const, Num(Fraction(1, new_exp)), power(x, Num(new_exp)))

            if isinstance(denom, Add):
                coeff_x, const_term = self._extract_linear_coeffs(denom, var)
                if coeff_x is not None and coeff_x == 1:
                    # ∫C/(x + b)^n dx = C * (x + b)^(1-n) / (1-n)
                    new_exp = 1 - n
                    return mul(const, Num(Fraction(1, new_exp)), power(denom, Num(new_exp)))

        return None

    def _extract_linear_coeffs(self, expr: Add, var: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Extract coefficients from linear expression ax + b.

        Returns (a, b) or (None, None) if not linear.
        """
        if len(expr.terms) != 2:
            return None, None

        coeff_x = None
        const_term = None

        for term in expr.terms:
            if isinstance(term, Sym) and term.name == var:
                coeff_x = 1
            elif isinstance(term, Num) and not self._contains_var(term, var):
                const_term = term.value
            elif isinstance(term, Mul):
                # Check for coefficient * x
                has_var = False
                coeff = 1
                for f in term.factors:
                    if isinstance(f, Sym) and f.name == var:
                        has_var = True
                    elif isinstance(f, Num):
                        coeff *= f.value
                if has_var:
                    coeff_x = coeff
                else:
                    const_term = coeff
            elif isinstance(term, Neg):
                if isinstance(term.arg, Sym) and term.arg.name == var:
                    coeff_x = -1
                elif isinstance(term.arg, Num):
                    const_term = -term.arg.value

        return coeff_x, const_term

    def _try_ln_integral(self, const: Expr, denom: Add, var: str) -> Optional[Expr]:
        """
        Try ∫C/(x + a) dx = C * ln|x + a|.
        """
        coeff_x, const_term = self._extract_linear_coeffs(denom, var)
        if coeff_x is not None:
            # ∫C/(ax + b) dx = (C/a) * ln|ax + b|
            if coeff_x != 0:
                result_coeff = mul(const, Num(Fraction(1, int(coeff_x)))) if coeff_x != 1 else const
                return mul(result_coeff, Func('ln', Func('Abs', denom)))
        return None

    def _try_arctan_integral(self, const: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Try ∫C/(αx² + β) dx = (C/sqrt(αβ)) * arctan(sqrt(α/β)*x).

        Handles:
        - ∫C/(x^2 + a^2) dx = (C/a) * arctan(x/a)
        - ∫C/(x^2 - a^2) dx = (C/2a) * ln|(x-a)/(x+a)|
        - ∫C/(b^2*x^2 + a^2) dx = (C/(ab)) * arctan((b/a)*x)
        - ∫C/(a^2*x^2 + a^2) dx = (C/a^2) * arctan(x)
        - Symbolic a: ∫1/(x^2 + a^2) dx = (1/a) * arctan(x/a)
        """
        x = Sym(var)

        # Look for αx² + β pattern (generalized)
        if isinstance(denom, Add) and len(denom.terms) == 2:
            x_squared_coeff = None  # The α in αx² (default 1)
            const_term = None       # The β (numeric constant)
            symbolic_const = None   # For symbolic a² case
            x_squared_coeff_sym = None  # For symbolic b² case

            for term in denom.terms:
                # Check for x² (coefficient 1)
                if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                    if isinstance(term.exp, Num) and term.exp.value == 2:
                        x_squared_coeff = 1.0

                # Check for b²x² (Mul with Pow(symbol,2) and Pow(x,2))
                elif isinstance(term, Mul):
                    has_x_squared = False
                    coeff_parts_num = []
                    coeff_parts_sym = []
                    for factor in term.factors:
                        if isinstance(factor, Pow):
                            if isinstance(factor.base, Sym) and factor.base.name == var:
                                if isinstance(factor.exp, Num) and factor.exp.value == 2:
                                    has_x_squared = True
                            elif isinstance(factor.base, Sym) and factor.base.name != var:
                                if isinstance(factor.exp, Num) and factor.exp.value == 2:
                                    coeff_parts_sym.append(factor.base.name)
                            elif isinstance(factor.base, Num):
                                val = _try_evaluate_const(factor)
                                if val is not None:
                                    coeff_parts_num.append(val)
                        elif isinstance(factor, Num):
                            coeff_parts_num.append(factor.value)
                        elif isinstance(factor, Sym) and factor.name != var:
                            coeff_parts_sym.append(factor.name)

                    if has_x_squared:
                        if coeff_parts_num:
                            x_squared_coeff = 1.0
                            for v in coeff_parts_num:
                                x_squared_coeff *= v
                        if coeff_parts_sym:
                            x_squared_coeff_sym = coeff_parts_sym

                # Check for numeric constant β
                elif isinstance(term, Num):
                    const_term = term.value
                elif isinstance(term, Neg) and isinstance(term.arg, Num):
                    const_term = -term.arg.value

                # Check for symbolic a² (Pow with symbol base and exponent 2)
                elif isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name != var:
                    if isinstance(term.exp, Num) and term.exp.value == 2:
                        symbolic_const = term.base.name  # The symbol 'a'

            # Case 1: Numeric coefficient on x² and numeric constant
            if x_squared_coeff is not None and const_term is not None:
                alpha = x_squared_coeff
                beta = const_term

                if beta > 0 and alpha > 0:
                    # ∫C/(αx² + β) dx = (C/sqrt(αβ)) * arctan(sqrt(α/β)*x)
                    coeff_val = 1.0 / math.sqrt(alpha * beta)
                    arg_coeff = math.sqrt(alpha / beta)

                    # Simplify for special cases
                    if abs(arg_coeff - 1.0) < 1e-10:
                        # α = β case: simplifies to (1/β)*atan(x)
                        return mul(const, Num(coeff_val), Func('atan', x))
                    else:
                        return mul(const, Num(coeff_val),
                                  Func('atan', mul(Num(arg_coeff), x)))
                elif beta < 0 and alpha > 0:
                    # ∫C/(αx² - |β|) dx - partial fractions needed
                    # For now, only handle α=1 case
                    if abs(alpha - 1.0) < 1e-10:
                        a_sq = -beta
                        a = math.sqrt(a_sq)
                        if a == int(a):
                            a = int(a)
                        coeff = Fraction(1, 2 * a) if isinstance(a, int) else 1 / (2 * a)
                        return mul(const, Num(coeff),
                                  add(Func('ln', Func('Abs', add(x, Num(-a)))),
                                      neg(Func('ln', Func('Abs', add(x, Num(a)))))))

            # Case 2: Symbolic b²x² + a² (both coefficients are symbolic)
            if x_squared_coeff_sym and symbolic_const:
                # ∫1/(b²x² + a²) dx = (1/(ab)) * arctan((b/a)*x)
                b_sym = Sym(x_squared_coeff_sym[0])
                a_sym = Sym(symbolic_const)
                # Result: (1/(a*b)) * atan((b/a)*x)
                one_over_ab = mul(power(a_sym, Num(-1)), power(b_sym, Num(-1)))
                b_over_a = mul(b_sym, power(a_sym, Num(-1)))
                return mul(const, one_over_ab, Func('atan', mul(b_over_a, x)))

            # Case 3: Numeric b²x² + symbolic a²
            if x_squared_coeff is not None and x_squared_coeff != 1.0 and symbolic_const:
                # ∫1/(α*x² + a²) dx = (1/(sqrt(α)*a)) * arctan((sqrt(α)/a)*x)
                sqrt_alpha = math.sqrt(x_squared_coeff)
                a_sym = Sym(symbolic_const)
                # Result: (1/(sqrt(α)*a)) * atan((sqrt(α)/a)*x)
                one_over_sqrt_alpha_a = mul(Num(1/sqrt_alpha), power(a_sym, Num(-1)))
                sqrt_alpha_over_a = mul(Num(sqrt_alpha), power(a_sym, Num(-1)))
                return mul(const, one_over_sqrt_alpha_a, Func('atan', mul(sqrt_alpha_over_a, x)))

            # Case 4: x² + symbolic a² (coefficient 1)
            if x_squared_coeff == 1.0 and symbolic_const is not None:
                # ∫C/(x^2 + a^2) dx = (C/a) * arctan(x/a)
                a_sym = Sym(symbolic_const)
                x_over_a = mul(x, power(a_sym, Num(-1)))
                one_over_a = power(a_sym, Num(-1))
                return mul(const, one_over_a, Func('atan', x_over_a))

        return None

    def _try_inverse_sqrt_integral(self, expr: Expr, var: str) -> Optional[Expr]:
        """
        Try integrals involving 1/√(quadratic).

        Handles:
        - ∫1/√(x² + a²) dx = arsinh(x/a) = ln(x + √(x² + a²))
        - ∫1/√(a² - x²) dx = arcsin(x/a)
        - ∫x/√(x² + a²) dx = √(x² + a²)
        - ∫x/√(x² - a²) dx = √(x² - a²)
        """
        x = Sym(var)

        # Pattern: (x² + a²)^(-1/2) or (a² - x²)^(-1/2)
        if isinstance(expr, Pow):
            base = expr.base
            exp = expr.exp

            # Check for power of -1/2
            is_neg_half = False
            if isinstance(exp, Num):
                exp_val = float(exp.value)
                if abs(exp_val - (-0.5)) < 1e-10:
                    is_neg_half = True
            elif isinstance(exp, Neg) and isinstance(exp.arg, Num):
                exp_val = float(exp.arg.value)
                if abs(exp_val - 0.5) < 1e-10:
                    is_neg_half = True

            if is_neg_half and isinstance(base, Add) and len(base.terms) == 2:
                x_squared = None
                const_term = None
                sign_of_x2 = 1  # +1 for x², -1 for -x²

                for term in base.terms:
                    if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                        if isinstance(term.exp, Num) and term.exp.value == 2:
                            x_squared = term
                            sign_of_x2 = 1
                    elif isinstance(term, Neg):
                        inner = term.arg
                        if isinstance(inner, Pow) and isinstance(inner.base, Sym) and inner.base.name == var:
                            if isinstance(inner.exp, Num) and inner.exp.value == 2:
                                x_squared = inner
                                sign_of_x2 = -1
                        elif isinstance(inner, Num):
                            const_term = -inner.value
                    elif isinstance(term, Num):
                        const_term = term.value

                if x_squared is not None and const_term is not None:
                    if sign_of_x2 == 1 and const_term > 0:
                        # ∫1/√(x² + a²) dx = ln(x + √(x² + a²))
                        # This is arsinh(x/a) but we return the log form
                        a_sq = const_term
                        sqrt_term = power(base, Num(Fraction(1, 2)))
                        return Func('ln', add(x, sqrt_term))

                    elif sign_of_x2 == -1 and const_term > 0:
                        # ∫1/√(a² - x²) dx = arcsin(x/a)
                        a = math.sqrt(const_term)
                        if a == int(a):
                            a = int(a)
                        return Func('asin', mul(x, Num(Fraction(1, a) if isinstance(a, int) else 1/a)))

        # Pattern: x * (x² + a²)^(-1/2) -> √(x² + a²)
        if isinstance(expr, Mul):
            factors = expr.factors
            x_factor = None
            sqrt_recip_factor = None

            for f in factors:
                if isinstance(f, Sym) and f.name == var:
                    x_factor = f
                elif isinstance(f, Pow):
                    base = f.base
                    exp = f.exp
                    is_neg_half = False
                    if isinstance(exp, Num) and abs(float(exp.value) - (-0.5)) < 1e-10:
                        is_neg_half = True
                    elif isinstance(exp, Neg) and isinstance(exp.arg, Num):
                        if abs(float(exp.arg.value) - 0.5) < 1e-10:
                            is_neg_half = True
                    if is_neg_half:
                        sqrt_recip_factor = f

            if x_factor is not None and sqrt_recip_factor is not None:
                base = sqrt_recip_factor.base
                if isinstance(base, Add) and len(base.terms) == 2:
                    # Check for x² + a² or x² - a²
                    x_sq = None
                    for term in base.terms:
                        if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                            if isinstance(term.exp, Num) and term.exp.value == 2:
                                x_sq = term
                    if x_sq is not None:
                        # ∫x/√(x² + a²) dx = √(x² + a²)
                        return power(base, Num(Fraction(1, 2)))

        return None

    def _try_quartic_plus_one_integral(self, const: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Try ∫C/(x^4 + 1) dx using the standard formula.

        The integral of 1/(x^4 + 1) is:
        (√2/8) * [ln((x² + √2·x + 1)/(x² - √2·x + 1)) + 2*arctan(√2·x + 1) + 2*arctan(√2·x - 1)]

        Which simplifies to:
        (√2/8) * ln((x² + √2·x + 1)/(x² - √2·x + 1)) + (√2/4) * [arctan(√2·x + 1) + arctan(√2·x - 1)]

        This can also be written as:
        (√2/8) * [ln(x² + √2·x + 1) - ln(x² - √2·x + 1) + 2*atan(√2·x + 1) + 2*atan(√2·x - 1)]
        """
        x = Sym(var)

        # Check for x^4 + 1 pattern
        if isinstance(denom, Add) and len(denom.terms) == 2:
            x_fourth_term = None
            const_term = None

            for term in denom.terms:
                if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                    if isinstance(term.exp, Num) and term.exp.value == 4:
                        x_fourth_term = term
                elif isinstance(term, Num) and term.value == 1:
                    const_term = 1

            if x_fourth_term is not None and const_term == 1:
                # ∫C/(x^4 + 1) dx
                # Result: C * (√2/8) * [ln((x² + √2·x + 1)/(x² - √2·x + 1)) + 2*atan(√2·x + 1) + 2*atan(√2·x - 1)]

                sqrt2 = math.sqrt(2)

                # Build quadratics: x² + √2·x + 1 and x² - √2·x + 1
                x_sq = power(x, Num(2))
                sqrt2_x = mul(Num(sqrt2), x)

                # q1 = x² + √2·x + 1
                q1 = add(x_sq, sqrt2_x, Num(1))
                # q2 = x² - √2·x + 1
                q2 = add(x_sq, neg(sqrt2_x), Num(1))

                # Logarithm part: (√2/8) * ln(q1/q2) = (√2/8) * [ln(q1) - ln(q2)]
                ln_coeff = sqrt2 / 8
                ln_part = mul(Num(ln_coeff), add(Func('ln', Func('Abs', q1)),
                                                  neg(Func('ln', Func('Abs', q2)))))

                # Arctan part: (√2/4) * [atan(√2·x + 1) + atan(√2·x - 1)]
                atan_coeff = sqrt2 / 4
                atan_arg1 = add(sqrt2_x, Num(1))   # √2·x + 1
                atan_arg2 = add(sqrt2_x, Num(-1))  # √2·x - 1
                atan_part = mul(Num(atan_coeff), add(Func('atan', atan_arg1),
                                                      Func('atan', atan_arg2)))

                # Combine: C * (ln_part + atan_part)
                result = add(ln_part, atan_part)

                # Apply constant multiplier
                if isinstance(const, Num) and const.value == 1:
                    return result
                else:
                    return mul(const, result)

        return None

    def _try_x_squared_over_quartic_integral(self, numer: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Try ∫x²/(x^4 + 1) dx or ∫C*x²/(x^4 + 1) dx using the standard formula.

        The integral of x²/(x^4 + 1) is:
        -(√2/8) * ln((x² + √2·x + 1)/(x² - √2·x + 1)) + (√2/4) * [arctan(√2·x + 1) + arctan(√2·x - 1)]

        Note: This differs from 1/(x⁴+1) by having NEGATIVE ln coefficient (vs positive).
        The arctan terms are the same (both positive).
        """
        x = Sym(var)

        # Check denominator for x^4 + 1 pattern
        if not (isinstance(denom, Add) and len(denom.terms) == 2):
            return None

        x_fourth_term = None
        denom_const_term = None
        for term in denom.terms:
            if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                if isinstance(term.exp, Num) and term.exp.value == 4:
                    x_fourth_term = term
            elif isinstance(term, Num) and term.value == 1:
                denom_const_term = 1

        if x_fourth_term is None or denom_const_term != 1:
            return None

        # Check numerator for x² or C*x² pattern
        coeff = None
        if isinstance(numer, Pow):
            # x²
            if (isinstance(numer.base, Sym) and numer.base.name == var and
                isinstance(numer.exp, Num) and numer.exp.value == 2):
                coeff = 1.0
        elif isinstance(numer, Mul):
            # C*x²
            num_coeff = 1.0
            found_x_sq = False
            for factor in numer.factors:
                if isinstance(factor, Num):
                    num_coeff *= factor.value
                elif isinstance(factor, Pow):
                    if (isinstance(factor.base, Sym) and factor.base.name == var and
                        isinstance(factor.exp, Num) and factor.exp.value == 2):
                        found_x_sq = True
                    else:
                        return None
                else:
                    return None
            if found_x_sq:
                coeff = num_coeff

        if coeff is None:
            return None

        # Build the result: C * [(√2/8) * ln(...) - (√2/4) * (atan(...) + atan(...))]
        sqrt2 = math.sqrt(2)

        # Build quadratics: x² + √2·x + 1 and x² - √2·x + 1
        x_sq = power(x, Num(2))
        sqrt2_x = mul(Num(sqrt2), x)

        # q1 = x² + √2·x + 1
        q1 = add(x_sq, sqrt2_x, Num(1))
        # q2 = x² - √2·x + 1
        q2 = add(x_sq, neg(sqrt2_x), Num(1))

        # Logarithm part: -(√2/8) * ln(q1/q2) = -(√2/8) * [ln(q1) - ln(q2)]
        # Note: NEGATIVE coefficient (opposite of 1/(x⁴+1))
        ln_coeff = -sqrt2 / 8
        ln_part = mul(Num(ln_coeff), add(Func('ln', Func('Abs', q1)),
                                          neg(Func('ln', Func('Abs', q2)))))

        # Arctan part: +(√2/4) * [atan(√2·x + 1) + atan(√2·x - 1)]
        # Note: POSITIVE coefficient (same as 1/(x⁴+1))
        atan_coeff = sqrt2 / 4
        atan_arg1 = add(sqrt2_x, Num(1))   # √2·x + 1
        atan_arg2 = add(sqrt2_x, Num(-1))  # √2·x - 1
        atan_part = mul(Num(atan_coeff), add(Func('atan', atan_arg1),
                                              Func('atan', atan_arg2)))

        # Combine: C * (ln_part + atan_part)
        result = add(ln_part, atan_part)

        # Apply coefficient
        if coeff != 1.0:
            result = mul(Num(coeff), result)

        return result

    def _try_x_sq_plus_one_over_quartic_integral(self, numer: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Try ∫(x²+1)/(x^4 + 1) dx or ∫C*(x²+1)/(x^4 + 1) dx using the standard formula.

        The integral of (x²+1)/(x^4 + 1) is simply:
        (√2/2) * [arctan(√2·x + 1) + arctan(√2·x - 1)]

        This elegant result comes from the fact that:
        - ∫1/(x⁴+1) dx has ln term with coeff +√2/8 and arctan terms with coeff +√2/4
        - ∫x²/(x⁴+1) dx has ln term with coeff -√2/8 and arctan terms with coeff +√2/4
        - Adding them: ln terms cancel, arctan terms add to √2/2
        """
        x = Sym(var)

        # Check denominator for x^4 + 1 pattern
        if not (isinstance(denom, Add) and len(denom.terms) == 2):
            return None

        x_fourth_term = None
        denom_const_term = None
        for term in denom.terms:
            if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                if isinstance(term.exp, Num) and term.exp.value == 4:
                    x_fourth_term = term
            elif isinstance(term, Num) and term.value == 1:
                denom_const_term = 1

        if x_fourth_term is None or denom_const_term != 1:
            return None

        # Check numerator for (x² + 1) or C*(x² + 1) pattern
        coeff = self._match_x_sq_plus_one(numer, var)
        if coeff is None:
            return None

        # Build the result: C * (√2/2) * [arctan(√2·x + 1) + arctan(√2·x - 1)]
        sqrt2 = math.sqrt(2)
        sqrt2_x = mul(Num(sqrt2), x)

        # Arctan arguments: √2·x + 1 and √2·x - 1
        atan_arg1 = add(sqrt2_x, Num(1))   # √2·x + 1
        atan_arg2 = add(sqrt2_x, Num(-1))  # √2·x - 1

        # Result: (√2/2) * [atan(√2·x + 1) + atan(√2·x - 1)]
        atan_coeff = sqrt2 / 2
        result = mul(Num(atan_coeff), add(Func('atan', atan_arg1),
                                          Func('atan', atan_arg2)))

        # Apply coefficient
        if coeff != 1.0:
            result = mul(Num(coeff), result)

        return result

    def _match_x_sq_plus_one(self, expr: Expr, var: str) -> Optional[float]:
        """
        Check if expr matches (x² + 1) or C*(x² + 1) pattern.
        Returns the coefficient C if matched, None otherwise.
        """
        # Direct (x² + 1) pattern
        if isinstance(expr, Add) and len(expr.terms) == 2:
            has_x_sq = False
            has_one = False
            for term in expr.terms:
                if isinstance(term, Num) and term.value == 1:
                    has_one = True
                elif isinstance(term, Pow):
                    if (isinstance(term.base, Sym) and term.base.name == var and
                        isinstance(term.exp, Num) and term.exp.value == 2):
                        has_x_sq = True
            if has_x_sq and has_one:
                return 1.0

        # C*(x² + 1) pattern via Mul
        if isinstance(expr, Mul):
            num_coeff = 1.0
            x_sq_plus_one = None
            for factor in expr.factors:
                if isinstance(factor, Num):
                    num_coeff *= factor.value
                elif isinstance(factor, Add) and len(factor.terms) == 2:
                    # Check if this is (x² + 1)
                    has_x_sq = False
                    has_one = False
                    for term in factor.terms:
                        if isinstance(term, Num) and term.value == 1:
                            has_one = True
                        elif isinstance(term, Pow):
                            if (isinstance(term.base, Sym) and term.base.name == var and
                                isinstance(term.exp, Num) and term.exp.value == 2):
                                has_x_sq = True
                    if has_x_sq and has_one:
                        x_sq_plus_one = factor
                    else:
                        return None
                else:
                    return None
            if x_sq_plus_one is not None:
                return num_coeff

        return None

    def _try_x_sq_minus_one_over_quartic_integral(self, numer: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Try ∫(x²-1)/(x^4 + 1) dx using the standard formula.

        The integral of (x²-1)/(x^4 + 1) is:
        -(√2/4) * ln((x² + √2·x + 1)/(x² - √2·x + 1))

        This is the negative of (x²+1)/(x⁴+1) formula (which has only arctan terms).
        Here the arctan terms cancel and we get only the ln term with negative coefficient.
        """
        x = Sym(var)

        # Check denominator for x^4 + 1 pattern
        if not (isinstance(denom, Add) and len(denom.terms) == 2):
            return None

        x_fourth_term = None
        denom_const_term = None
        for term in denom.terms:
            if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                if isinstance(term.exp, Num) and term.exp.value == 4:
                    x_fourth_term = term
            elif isinstance(term, Num) and term.value == 1:
                denom_const_term = 1

        if x_fourth_term is None or denom_const_term != 1:
            return None

        # Check numerator for (x² - 1) or C*(x² - 1) pattern
        coeff = self._match_x_sq_minus_one(numer, var)
        if coeff is None:
            return None

        # Build the result: C * -(√2/4) * ln((x² + √2·x + 1)/(x² - √2·x + 1))
        sqrt2 = math.sqrt(2)
        x_sq = power(x, Num(2))
        sqrt2_x = mul(Num(sqrt2), x)

        # q1 = x² + √2·x + 1, q2 = x² - √2·x + 1
        q1 = add(x_sq, sqrt2_x, Num(1))
        q2 = add(x_sq, neg(sqrt2_x), Num(1))

        # Result: -(√2/4) * [ln(q1) - ln(q2)] = (√2/4) * [ln(q2) - ln(q1)]
        ln_coeff = -sqrt2 / 4
        result = mul(Num(ln_coeff), add(Func('ln', Func('Abs', q1)),
                                        neg(Func('ln', Func('Abs', q2)))))

        if coeff != 1.0:
            result = mul(Num(coeff), result)

        return result

    def _match_x_sq_minus_one(self, expr: Expr, var: str) -> Optional[float]:
        """
        Check if expr matches (x² - 1), (1 - x²), or C*(x² - 1) pattern.
        Returns the coefficient C if matched, None otherwise.
        Note: (1 - x²) = -(x² - 1), so returns -1.0 for that case.
        """
        # Direct (x² - 1) pattern: Add with x² and -1
        if isinstance(expr, Add) and len(expr.terms) == 2:
            has_x_sq = False
            has_neg_one = False
            has_neg_x_sq = False  # For (1 - x²) pattern
            has_pos_one = False
            for term in expr.terms:
                if isinstance(term, Num) and term.value == -1:
                    has_neg_one = True
                elif isinstance(term, Num) and term.value == 1:
                    has_pos_one = True
                elif isinstance(term, Neg) and isinstance(term.arg, Num) and term.arg.value == 1:
                    has_neg_one = True
                elif isinstance(term, Pow):
                    if (isinstance(term.base, Sym) and term.base.name == var and
                        isinstance(term.exp, Num) and term.exp.value == 2):
                        has_x_sq = True
                elif isinstance(term, Neg) and isinstance(term.arg, Pow):
                    # -x² term for (1 - x²) pattern
                    inner = term.arg
                    if (isinstance(inner.base, Sym) and inner.base.name == var and
                        isinstance(inner.exp, Num) and inner.exp.value == 2):
                        has_neg_x_sq = True
            # (x² - 1) pattern
            if has_x_sq and has_neg_one:
                return 1.0
            # (1 - x²) pattern = -(x² - 1)
            if has_neg_x_sq and has_pos_one:
                return -1.0

        # C*(x² - 1) via Mul - similar to _match_x_sq_plus_one
        if isinstance(expr, Mul):
            num_coeff = 1.0
            x_sq_minus_one = None
            for factor in expr.factors:
                if isinstance(factor, Num):
                    num_coeff *= factor.value
                elif isinstance(factor, Add) and len(factor.terms) == 2:
                    has_x_sq = False
                    has_neg_one = False
                    for term in factor.terms:
                        if isinstance(term, Num) and term.value == -1:
                            has_neg_one = True
                        elif isinstance(term, Neg) and isinstance(term.arg, Num) and term.arg.value == 1:
                            has_neg_one = True
                        elif isinstance(term, Pow):
                            if (isinstance(term.base, Sym) and term.base.name == var and
                                isinstance(term.exp, Num) and term.exp.value == 2):
                                has_x_sq = True
                    if has_x_sq and has_neg_one:
                        x_sq_minus_one = factor
                    else:
                        return None
                else:
                    return None
            if x_sq_minus_one is not None:
                return num_coeff

        return None

    def _try_x_over_quartic_integral(self, numer: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Try ∫x/(x^4 + 1) dx using the formula: (1/2) * atan(x²)
        """
        x = Sym(var)

        # Check denominator for x^4 + 1 pattern
        if not (isinstance(denom, Add) and len(denom.terms) == 2):
            return None

        x_fourth_term = None
        denom_const_term = None
        for term in denom.terms:
            if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                if isinstance(term.exp, Num) and term.exp.value == 4:
                    x_fourth_term = term
            elif isinstance(term, Num) and term.value == 1:
                denom_const_term = 1

        if x_fourth_term is None or denom_const_term != 1:
            return None

        # Check numerator for x or C*x pattern
        coeff = self._match_single_x(numer, var)
        if coeff is None:
            return None

        # Result: C * (1/2) * atan(x²)
        x_sq = power(x, Num(2))
        result = mul(Num(0.5), Func('atan', x_sq))

        if coeff != 1.0:
            result = mul(Num(coeff), result)

        return result

    def _match_single_x(self, expr: Expr, var: str) -> Optional[float]:
        """Check if expr is x or C*x, return coefficient."""
        if isinstance(expr, Sym) and expr.name == var:
            return 1.0
        if isinstance(expr, Mul):
            coeff = 1.0
            found_x = False
            for factor in expr.factors:
                if isinstance(factor, Num):
                    coeff *= factor.value
                elif isinstance(factor, Sym) and factor.name == var:
                    found_x = True
                else:
                    return None
            if found_x:
                return coeff
        return None

    def _try_x_cubed_over_quartic_integral(self, numer: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Try ∫x³/(x^4 + 1) dx using the formula: (1/4) * ln(x⁴ + 1)

        This is the log-derivative pattern since d(x⁴+1)/dx = 4x³.
        """
        x = Sym(var)

        # Check denominator for x^4 + 1 pattern
        if not (isinstance(denom, Add) and len(denom.terms) == 2):
            return None

        x_fourth_term = None
        denom_const_term = None
        for term in denom.terms:
            if isinstance(term, Pow) and isinstance(term.base, Sym) and term.base.name == var:
                if isinstance(term.exp, Num) and term.exp.value == 4:
                    x_fourth_term = term
            elif isinstance(term, Num) and term.value == 1:
                denom_const_term = 1

        if x_fourth_term is None or denom_const_term != 1:
            return None

        # Check numerator for x³ or C*x³ pattern
        coeff = self._match_x_cubed(numer, var)
        if coeff is None:
            return None

        # Result: C * (1/4) * ln(x⁴ + 1)
        result = mul(Num(0.25), Func('ln', Func('Abs', denom)))

        if coeff != 1.0:
            result = mul(Num(coeff), result)

        return result

    def _match_x_cubed(self, expr: Expr, var: str) -> Optional[float]:
        """Check if expr is x³ or C*x³, return coefficient."""
        if isinstance(expr, Pow):
            if (isinstance(expr.base, Sym) and expr.base.name == var and
                isinstance(expr.exp, Num) and expr.exp.value == 3):
                return 1.0
        if isinstance(expr, Mul):
            coeff = 1.0
            found_x_cubed = False
            for factor in expr.factors:
                if isinstance(factor, Num):
                    coeff *= factor.value
                elif isinstance(factor, Pow):
                    if (isinstance(factor.base, Sym) and factor.base.name == var and
                        isinstance(factor.exp, Num) and factor.exp.value == 3):
                        found_x_cubed = True
                    else:
                        return None
                else:
                    return None
            if found_x_cubed:
                return coeff
        return None

    def _try_log_derivative_pattern(self, numer: Expr, denom: Expr, var: str) -> Optional[Expr]:
        """
        Check if numerator is derivative of denominator.

        If numer = d(denom)/dx, then ∫numer/denom dx = ln|denom|.

        Common cases:
        - x/(x^2 + a) -> (1/2)*ln(x^2 + a)
        - 2x/(x^2 + a) -> ln(x^2 + a)
        """
        diff_engine = DifferentiationEngine()
        denom_deriv = diff_engine.differentiate(denom, var)

        # Check if numerator equals derivative
        if self._exprs_equal(numer, denom_deriv):
            return Func('ln', Func('Abs', denom))

        # Check if numerator is a constant multiple of derivative
        # E.g., x is (1/2) * derivative of (x^2 + 1)
        ratio = self._try_get_ratio(numer, denom_deriv, var)
        if ratio is not None:
            return mul(Num(ratio), Func('ln', Func('Abs', denom)))

        return None

    def _exprs_equal(self, e1: Expr, e2: Expr) -> bool:
        """Check if two expressions are equal (simple structural equality)."""
        if type(e1) != type(e2):
            return False
        if isinstance(e1, Num):
            return e1.value == e2.value
        if isinstance(e1, Sym):
            return e1.name == e2.name
        if isinstance(e1, Add):
            return len(e1.terms) == len(e2.terms) and all(
                self._exprs_equal(t1, t2) for t1, t2 in zip(e1.terms, e2.terms)
            )
        if isinstance(e1, Mul):
            return len(e1.factors) == len(e2.factors) and all(
                self._exprs_equal(f1, f2) for f1, f2 in zip(e1.factors, e2.factors)
            )
        if isinstance(e1, Pow):
            return self._exprs_equal(e1.base, e2.base) and self._exprs_equal(e1.exp, e2.exp)
        if isinstance(e1, Neg):
            return self._exprs_equal(e1.arg, e2.arg)
        if isinstance(e1, Func):
            return e1.name == e2.name and self._exprs_equal(e1.arg, e2.arg)
        return False

    def _try_get_ratio(self, numer: Expr, deriv: Expr, var: str) -> Optional[Fraction]:
        """
        Try to find constant ratio c such that numer = c * deriv.

        Returns c as a Fraction if found, None otherwise.
        """
        # Simple case: both are single symbols or numbers
        if isinstance(numer, Sym) and isinstance(deriv, Mul):
            # E.g., numer = x, deriv = 2*x -> ratio = 1/2
            coeff = None
            sym_part = None
            for f in deriv.factors:
                if isinstance(f, Num):
                    coeff = f.value
                elif isinstance(f, Sym) and f.name == numer.name:
                    sym_part = f
            if coeff is not None and sym_part is not None:
                return Fraction(1, int(coeff)) if isinstance(coeff, int) else None

        # Both are Mul expressions
        if isinstance(numer, Mul) and isinstance(deriv, Mul):
            numer_coeff = 1
            deriv_coeff = 1
            numer_vars = []
            deriv_vars = []

            for f in numer.factors:
                if isinstance(f, Num):
                    numer_coeff *= f.value
                else:
                    numer_vars.append(f)

            for f in deriv.factors:
                if isinstance(f, Num):
                    deriv_coeff *= f.value
                else:
                    deriv_vars.append(f)

            # Check if variable parts are the same
            if len(numer_vars) == len(deriv_vars):
                all_match = all(
                    self._exprs_equal(v1, v2) for v1, v2 in zip(numer_vars, deriv_vars)
                )
                if all_match and deriv_coeff != 0:
                    ratio = numer_coeff / deriv_coeff
                    if isinstance(ratio, float) and ratio == int(ratio):
                        ratio = int(ratio)
                    if isinstance(ratio, int):
                        return Fraction(ratio)
                    elif isinstance(numer_coeff, int) and isinstance(deriv_coeff, int):
                        return Fraction(numer_coeff, deriv_coeff)

        return None

    def _integrate_reciprocal(self, base: Expr, var: str) -> Optional[Expr]:
        """
        Integrate 1/(base) where base is some expression.

        Dispatches to appropriate handler based on form of base.
        """
        x = Sym(var)

        # 1/x -> ln|x|
        if isinstance(base, Sym) and base.name == var:
            return Func('ln', Func('Abs', x))

        # 1/(x + a) -> ln|x + a|
        if isinstance(base, Add):
            coeff_x, const_term = self._extract_linear_coeffs(base, var)
            if coeff_x is not None:
                if coeff_x == 1:
                    return Func('ln', Func('Abs', base))
                else:
                    # 1/(ax + b) -> (1/a) * ln|ax + b|
                    return mul(Num(Fraction(1, int(coeff_x))), Func('ln', Func('Abs', base)))

            # Check for quadratic x^2 + a or x^2 - a
            result = self._try_arctan_integral(Num(1), base, var)
            if result is not None:
                return result

            # Check for quartic x^4 + 1 pattern
            result = self._try_quartic_plus_one_integral(Num(1), base, var)
            if result is not None:
                return result

        # 1/(x^n) -> x^(1-n)/(1-n)
        if isinstance(base, Pow):
            if isinstance(base.base, Sym) and base.base.name == var:
                if isinstance(base.exp, Num) and isinstance(base.exp.value, int) and base.exp.value >= 2:
                    n = base.exp.value
                    new_exp = 1 - n
                    return mul(Num(Fraction(1, new_exp)), power(x, Num(new_exp)))

            # 1/(linear^n) -> (linear)^(1-n)/(1-n)
            if isinstance(base.base, Add) and isinstance(base.exp, Num):
                n = base.exp.value
                if isinstance(n, int) and n >= 2:
                    linear = base.base
                    coeff_x, const_term = self._extract_linear_coeffs(linear, var)
                    if coeff_x == 1:
                        new_exp = 1 - n
                        return mul(Num(Fraction(1, new_exp)), power(linear, Num(new_exp)))
                    elif coeff_x is not None:
                        # 1/(ax + b)^n -> (1/a) * (ax + b)^(1-n)/(1-n)
                        new_exp = 1 - n
                        return mul(Num(Fraction(1, int(coeff_x))), Num(Fraction(1, new_exp)),
                                  power(linear, Num(new_exp)))

        return None

    def _integrate_reciprocal_power(self, expr: Pow, var: str) -> Optional[Expr]:
        """
        Integrate (base)^(-n) where n > 1.

        E.g., 1/(x-a)^2 -> -1/(x-a)
        """
        base = expr.base
        n = -expr.exp.value  # n is positive

        if not isinstance(n, int) and n != int(n):
            return None

        n = int(n)
        x = Sym(var)

        # (x)^(-n) -> x^(1-n)/(1-n)
        if isinstance(base, Sym) and base.name == var:
            new_exp = 1 - n
            return mul(Num(Fraction(1, new_exp)), power(x, Num(new_exp)))

        # (x + a)^(-n) -> (x + a)^(1-n)/(1-n)
        if isinstance(base, Add):
            coeff_x, const_term = self._extract_linear_coeffs(base, var)
            if coeff_x == 1:
                new_exp = 1 - n
                return mul(Num(Fraction(1, new_exp)), power(base, Num(new_exp)))
            elif coeff_x is not None:
                # (ax + b)^(-n) -> (1/a) * (ax + b)^(1-n)/(1-n)
                new_exp = 1 - n
                return mul(Num(Fraction(1, int(coeff_x))), Num(Fraction(1, new_exp)),
                          power(base, Num(new_exp)))

        return None

    def _contains_var(self, expr: Expr, var: str) -> bool:
        """Check if expression contains the variable."""
        if isinstance(expr, Num):
            return False
        if isinstance(expr, Sym):
            return expr.name == var
        if isinstance(expr, Neg):
            return self._contains_var(expr.arg, var)
        if isinstance(expr, Add):
            return any(self._contains_var(t, var) for t in expr.terms)
        if isinstance(expr, Mul):
            return any(self._contains_var(f, var) for f in expr.factors)
        if isinstance(expr, Pow):
            return self._contains_var(expr.base, var) or self._contains_var(expr.exp, var)
        if isinstance(expr, Func):
            return self._contains_var(expr.arg, var)
        return False

    def _add_one(self, expr: Expr) -> Expr:
        """Add 1 to expression."""
        if isinstance(expr, Num):
            return Num(expr.value + 1)
        return add(expr, Num(1))


# =============================================================================
# DEFINITE INTEGRATION FUNCTIONS (Extracted from native_calculus.py)
# =============================================================================

def definite_integrate(expr_str: str, var: str = 'x', a: Union[float, str] = None,
                       b: Union[float, str] = None) -> Tuple[bool, Optional[str], str]:
    """
    Compute definite integral with limits.

    Args:
        expr_str: Expression to integrate
        var: Variable to integrate with respect to
        a: Lower limit (number, 'inf', '-inf', or 'oo' for infinity)
        b: Upper limit (number, 'inf', '-inf', or 'oo' for infinity)

    Returns:
        (success, result_string, method)
        - success: True if integration succeeded
        - result_string: String representation of result
        - method: "native_calculus" or error description

    Special cases:
        - Gaussian integrals from -∞ to +∞ are handled analytically
        - ∫_{-∞}^{∞} exp(-x²) dx = √π
        - ∫_{-∞}^{∞} (1/√(2π)) exp(-x²/2) dx = 1 (normalized)
    """
    import math

    # Safety check to prevent DoS via deeply nested expressions
    is_safe, safety_error = _check_expression_safety(expr_str)
    if not is_safe:
        return False, None, f"expression_rejected: {safety_error}"

    try:
        # Fix exponent precedence: -x**n → (-1)*x**n
        # This ensures exp(-x**4) is correctly interpreted as exp(-(x**4))
        expr_str = _fix_exponent_precedence_inline(expr_str)

        # Normalize infinity and symbolic constant representations
        def normalize_bound(bound):
            if bound is None:
                return None
            if isinstance(bound, (int, float)):
                return float(bound)
            if isinstance(bound, str):
                bound_lower = bound.lower().strip()
                # Handle infinity representations
                if bound_lower in ('inf', 'oo', '+inf', '+oo', 'infinity'):
                    return float('inf')
                elif bound_lower in ('-inf', '-oo', '-infinity'):
                    return float('-inf')
                # Handle symbolic constants
                if bound_lower == 'pi':
                    return math.pi
                elif bound_lower == '-pi':
                    return -math.pi
                elif bound_lower == 'e':
                    return math.e
                # Try to evaluate symbolic expressions like 2*pi, pi/2, etc.
                try:
                    # Replace common constants with values for evaluation
                    eval_str = bound_lower.replace('pi', str(math.pi)).replace('e', str(math.e))
                    # Safe eval for simple arithmetic
                    import re
                    if re.match(r'^[\d\.\+\-\*/\(\)\s]+$', eval_str):
                        result = eval(eval_str)
                        return float(result)
                except:
                    pass
                # Try direct float conversion as last resort
                try:
                    return float(bound)
                except ValueError:
                    # Keep as symbolic - will return symbolic form
                    return bound
            return float(bound)

        a_norm = normalize_bound(a)
        b_norm = normalize_bound(b)

        # Check for symmetry rule (odd functions over symmetric bounds = 0)
        symmetry_result = _check_symmetry_integral(expr_str, var, a_norm, b_norm)
        if symmetry_result is not None:
            return True, symmetry_result, "native_calculus_symmetry"

        # Check for Gaussian integral over full real line
        if a_norm == float('-inf') and b_norm == float('inf'):
            # Try to match Gaussian pattern (basic Gaussian)
            gaussian_result = _try_gaussian_integral(expr_str, var)
            if gaussian_result is not None:
                return True, gaussian_result, "native_calculus"

            # Try Gaussian moments: x^n * exp(-a*x²)
            moment_result = _try_gaussian_moment_integral(expr_str, var)
            if moment_result is not None:
                return True, moment_result, "native_calculus"

            # Try polynomial × Gaussian with linearity: P(x)*exp(-a*x²)
            poly_gaussian_result = _try_linear_gaussian_full_line(expr_str, var)
            if poly_gaussian_result is not None:
                return True, poly_gaussian_result, "native_calculus"

            # Try completion-of-square Gaussian: exp(-a*x² + b*x)
            completion_result = _try_completion_square_gaussian(expr_str, var)
            if completion_result is not None:
                return True, completion_result, "native_calculus"

            # Try Gaussian Fourier transform: exp(-a*x²)*cos(k*x) or sin(k*x)
            fourier_result = _try_gaussian_fourier_integral(expr_str, var)
            if fourier_result is not None:
                return True, fourier_result, "native_calculus"

            # Try Gamma power integrals: exp(-x^4), exp(-x^6), etc.
            gamma_power_result = _try_gamma_power_integral(expr_str, var)
            if gamma_power_result is not None:
                return True, gamma_power_result, "native_calculus_gamma"

            # Try oscillatory Gaussian integrals: exp(-x^2)*cos(x^3), etc.
            osc_gaussian_result = _try_oscillatory_gaussian_integral(expr_str, var)
            if osc_gaussian_result is not None:
                return True, osc_gaussian_result, "native_calculus_oscillatory"

            # Try Lorentzian powers: 1/(x² + m²)^n
            lorentzian_result = _try_lorentzian_power_integral(expr_str, var, a_norm, b_norm)
            if lorentzian_result is not None:
                return True, lorentzian_result, "native_calculus"

            # Try heat kernel: ∫ exp(-(x-a)²/(4t))/sqrt(4πt) dx = 1
            heat_result = _try_heat_kernel_integral(expr_str, var)
            if heat_result is not None:
                return True, heat_result, "native_calculus"

            # Try Green's function: ∫ exp(-a*|x-t|) dx = 2/a
            green_result = _try_green_function_integral(expr_str, var)
            if green_result is not None:
                return True, green_result, "native_calculus"

            # Try oscillatory integrals: sin(x)/x, |sin(x)/x|, etc.
            osc_result = _try_oscillatory_integral(expr_str, var, a_norm, b_norm)
            if osc_result is not None:
                return True, osc_result[0], f"native_calculus_{osc_result[1]}"

        # Check for half-line Gaussian integrals (0 to ∞)
        if a_norm == 0 and b_norm == float('inf'):
            # Try Fresnel-cube integrals: cos(x³), sin(x³)
            fresnel_result = _try_fresnel_cube_integral(expr_str, var, a_norm, b_norm)
            if fresnel_result is not None:
                return True, fresnel_result, "native_calculus_fresnel"

            # Try sinc-log integral: (sin(x)/x)*log(x) = -gamma
            sinc_log_result = _try_sinc_log_integral(expr_str, var, a_norm, b_norm)
            if sinc_log_result is not None:
                return True, sinc_log_result, "native_calculus_euler_gamma"

            # Try Euler-gamma integral: (exp(-x) - 1/(1+x))/x = -gamma
            euler_gamma_result = _try_euler_gamma_integral(expr_str, var, a_norm, b_norm)
            if euler_gamma_result is not None:
                return True, euler_gamma_result, "native_calculus_euler_gamma"

            # Try oscillatory integrals first: sin(x)/x, |sin(x)/x|
            osc_result = _try_oscillatory_integral(expr_str, var, a_norm, b_norm)
            if osc_result is not None:
                return True, osc_result[0], f"native_calculus_{osc_result[1]}"

            # Try half-line Gaussian: ∫_0^∞ exp(-a*x²) dx = sqrt(π/a)/2
            half_gaussian_result = _try_half_gaussian_integral(expr_str, var)
            if half_gaussian_result is not None:
                return True, half_gaussian_result, "native_calculus"

            # Try standard normal PDF: ∫_0^∞ exp(-x²/2)/sqrt(2π) dx = 1/2
            normal_result = _try_standard_normal_integral(expr_str, var, a_norm, b_norm)
            if normal_result is not None:
                return True, normal_result, "native_calculus"

            # Try exponential ray: ∫_0^∞ exp(-a*x) dx = 1/a
            exp_ray_result = _try_exponential_ray_integral(expr_str, var)
            if exp_ray_result is not None:
                return True, exp_ray_result, "native_calculus"

            # Try exponential ray moments: ∫_0^∞ x^n * exp(-a*x) dx = n!/a^(n+1)
            ray_moment_result = _try_exponential_ray_moments(expr_str, var)
            if ray_moment_result is not None:
                return True, ray_moment_result, "native_calculus"

            # Try Lorentzian powers: 1/(x² + m²)^n
            lorentzian_result = _try_lorentzian_power_integral(expr_str, var, a_norm, b_norm)
            if lorentzian_result is not None:
                return True, lorentzian_result, "native_calculus"

        # Try normal tail integral: ∫_k^∞ exp(-x²/2)/sqrt(2π) dx for k > 0
        if isinstance(a_norm, (int, float)) and a_norm > 0 and b_norm == float('inf'):
            normal_tail_result = _try_standard_normal_integral(expr_str, var, a_norm, b_norm)
            if normal_tail_result is not None:
                return True, normal_tail_result, "native_calculus"

        # Try power integral convergence classification: x^(-p)
        # ∫_1^∞ x^(-p) dx: convergent if p > 1, divergent if p <= 1
        # ∫_0^1 x^(-q) dx: convergent if q < 1, divergent if q >= 1
        power_result = _try_power_integral_convergence(expr_str, var, a_norm, b_norm)
        if power_result is not None:
            return True, power_result[0], f"native_calculus_{power_result[1]}"

        # Try semicircle/circle area integrals: sqrt(R² - x²)
        semicircle_result = _try_semicircle_integral(expr_str, var, a, b)
        if semicircle_result is not None:
            return True, semicircle_result, "native_calculus"

        # Try linearity for polynomial × exp(-ax) integrals
        linear_exp_result = _try_linear_exponential_ray(expr_str, var, a_norm, b_norm)
        if linear_exp_result is not None:
            return True, linear_exp_result, "native_calculus"

        # Try Beta function integrals: ∫_0^1 x^(α-1)*(1-x)^(β-1) dx = B(α, β)
        if a_norm == 0 and b_norm == 1:
            beta_result = _try_beta_integral(expr_str, var)
            if beta_result is not None:
                return True, beta_result, "native_calculus"

        # For other definite integrals, try to compute antiderivative and apply FTC
        expr = _parser.parse(expr_str)
        if expr is None:
            return False, None, "parse_failed"

        antideriv = _int_engine.integrate(expr, var)
        if antideriv is None:
            # Check for pole singularity (interior or endpoint) before numeric fallback
            pole_sing = _check_pole_singularity(expr_str, var, a_norm, b_norm)
            if pole_sing is not None:
                return True, pole_sing, "pole_singularity_detected"

            # Check for log-power integrals: int_0^1 x^(-p) * log(x)^m dx
            log_power = _check_log_power_integral(expr_str, var, a_norm, b_norm)
            if log_power is not None:
                return True, log_power, "log_power_classified"

            # Check for logarithmic singularity before numeric fallback
            log_sing = _check_log_singularity(expr_str, var, a_norm, b_norm)
            if log_sing is not None:
                return False, log_sing, "log_singularity_detected"

            # Try numeric fallback if bounds are numeric and integrand has no free symbols
            numeric_result = _try_numeric_integration(expr_str, var, a_norm, b_norm)
            if numeric_result is not None:
                return True, numeric_result, "native_calculus_numeric"
            return False, None, "no_antiderivative"

        # If bounds are concrete numbers, we could evaluate
        # For now, return symbolic F(b) - F(a) form
        antideriv_str = _simplify_output(str(antideriv))

        # Try numerical evaluation with limit handling for infinite bounds
        # Only if both bounds are numeric (not symbolic like 'R')
        bounds_numeric = (
            a_norm is not None and b_norm is not None and
            isinstance(a_norm, (int, float)) and isinstance(b_norm, (int, float))
        )

        if bounds_numeric:
            try:
                # Comprehensive singularity analysis
                if math.isfinite(a_norm) and math.isfinite(b_norm):
                    sing_analysis = _analyze_singularities(antideriv, var, a_norm, b_norm)

                    # Interior singularities always cause divergence
                    if sing_analysis['interior']:
                        points = ', '.join(f'{var}={s}' for s in sing_analysis['interior'])
                        return True, f"divergent (interior singularities at {points})", "native_calculus"

                    # Endpoint singularities need limit evaluation
                    # (handled below via _evaluate_limit when direct eval fails)

                # Evaluate at upper bound (or limit for endpoint singularities)
                # For upper bound, approach from left (within the interval: '-')
                if math.isfinite(b_norm):
                    result_at_b = _evaluate_at(antideriv, var, b_norm)
                    # If direct evaluation fails, try limit from left (within interval)
                    if result_at_b is None:
                        result_at_b = _evaluate_limit(antideriv, var, b_norm, from_inside='-')
                else:
                    result_at_b = _evaluate_limit(antideriv, var, b_norm)

                # Evaluate at lower bound (or limit for endpoint singularities)
                # For lower bound, approach from right (within the interval: '+')
                if math.isfinite(a_norm):
                    result_at_a = _evaluate_at(antideriv, var, a_norm)
                    # If direct evaluation fails, try limit from right (within interval)
                    if result_at_a is None:
                        result_at_a = _evaluate_limit(antideriv, var, a_norm, from_inside='+')
                else:
                    result_at_a = _evaluate_limit(antideriv, var, a_norm)

                if result_at_b is not None and result_at_a is not None:
                    # Check for divergence (infinite limits)
                    if math.isinf(result_at_b) or math.isinf(result_at_a):
                        if math.isinf(result_at_b) and math.isinf(result_at_a):
                            # Both infinite - check if they're the same sign
                            if (result_at_b > 0) == (result_at_a > 0):
                                # Same sign - indeterminate (∞ - ∞)
                                return True, "indeterminate (∞ - ∞)", "native_calculus"
                            else:
                                # Different signs - divergent
                                return True, "divergent (→ ±∞)", "native_calculus"
                        elif math.isinf(result_at_b):
                            sign = "+" if result_at_b > 0 else "-"
                            return True, f"divergent (→ {sign}∞)", "native_calculus"
                        else:
                            sign = "-" if result_at_a > 0 else "+"
                            return True, f"divergent (→ {sign}∞)", "native_calculus"

                    result = result_at_b - result_at_a
                    return True, str(result), "native_calculus"
                else:
                    # Limit evaluation failed - check for oscillatory divergence
                    # For infinite bounds with oscillatory antiderivatives (sin, cos without decay)
                    if (math.isinf(b_norm) or math.isinf(a_norm)):
                        osc_result = _check_oscillatory_divergence(antideriv_str, var, a_norm, b_norm)
                        if osc_result is not None:
                            return True, osc_result, "native_calculus"
            except Exception as e:
                logger.debug(f"Definite integral evaluation failed: {e}")
                pass

        # Return symbolic form
        return True, f"[{antideriv_str}]_{a}^{b}", "native_calculus"

    except Exception as e:
        logger.debug(f"Native definite integration failed: {e}")
        return False, None, f"error: {e}"


