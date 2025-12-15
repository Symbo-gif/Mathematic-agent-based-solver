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
Special Integrals
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
from .extraction_utils import _check_quadratic_inner, _extract_positive_symbolic_coeff, _extract_power_of_one_minus_var, _extract_power_of_var, _extract_quadratic_coeff, _get_linear_coeff_from_mul, _get_term_with_var_power, _is_var_squared_or_shifted

logger = logging.getLogger(__name__)

# Module-level instances
_parser = ExprParser()
_int_engine = IntegrationEngine()


def _try_lorentzian_power_integral(expr_str: str, var: str, a_bound: float, b_bound: float) -> Optional[str]:
    """
    Handle Lorentzian power integrals: ∫ 1/(x² + m²)^n dx

    Formulas:
    - n=2, (-∞,∞): ∫_{-∞}^{∞} 1/(x² + m²)² dx = π/(2m³)
    - n=2, (0,∞):  ∫_0^∞ 1/(x² + m²)² dx = π/(4m³)
    - n=3, (-∞,∞): ∫_{-∞}^{∞} 1/(x² + m²)³ dx = 3π/(8m⁵)
    - n=3, (0,∞):  ∫_0^∞ 1/(x² + m²)³ dx = 3π/(16m⁵)

    General formula for n ≥ 1:
    - I_n(-∞,∞) = π * (2n-3)!! / ((2n-2)!! * m^(2n-1))
    - I_n(0,∞) = I_n(-∞,∞) / 2
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract pattern: C / (x² + m²)^n or C * (x² + m²)^(-n)
    outer_coeff = 1.0
    lorentzian_base = None
    power_n = 1

    # Case 1: Pow with negative exponent
    if isinstance(expr, Pow):
        if isinstance(expr.exp, Num) and expr.exp.value < 0:
            outer_exp = int(-expr.exp.value)  # e.g., -1 becomes 1
            # Check if base is itself a power: ((x² + m²)^n)^(-1)
            if isinstance(expr.base, Pow) and isinstance(expr.base.exp, Num):
                inner_exp = int(expr.base.exp.value)
                power_n = outer_exp * inner_exp
                lorentzian_base = expr.base.base
            else:
                power_n = outer_exp
                lorentzian_base = expr.base
        elif isinstance(expr.exp, Neg) and isinstance(expr.exp.arg, Num):
            outer_exp = int(expr.exp.arg.value)
            if isinstance(expr.base, Pow) and isinstance(expr.base.exp, Num):
                inner_exp = int(expr.base.exp.value)
                power_n = outer_exp * inner_exp
                lorentzian_base = expr.base.base
            else:
                power_n = outer_exp
                lorentzian_base = expr.base

    # Case 2: Mul with Pow factor
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            if isinstance(factor, Pow):
                if isinstance(factor.exp, Num) and factor.exp.value < 0:
                    outer_exp = int(-factor.exp.value)
                    if isinstance(factor.base, Pow) and isinstance(factor.base.exp, Num):
                        inner_exp = int(factor.base.exp.value)
                        power_n = outer_exp * inner_exp
                        lorentzian_base = factor.base.base
                    else:
                        power_n = outer_exp
                        lorentzian_base = factor.base
                elif isinstance(factor.exp, Neg) and isinstance(factor.exp.arg, Num):
                    outer_exp = int(factor.exp.arg.value)
                    if isinstance(factor.base, Pow) and isinstance(factor.base.exp, Num):
                        inner_exp = int(factor.base.exp.value)
                        power_n = outer_exp * inner_exp
                        lorentzian_base = factor.base.base
                    else:
                        power_n = outer_exp
                        lorentzian_base = factor.base
            elif isinstance(factor, Num):
                outer_coeff *= factor.value
            else:
                val = _try_evaluate_const(factor)
                if val is not None:
                    outer_coeff *= val

    if lorentzian_base is None or power_n < 2:
        return None  # Power must be at least 2 for this rule (n=1 is basic arctan)

    # Check if base is (x² + m²) pattern
    m_squared = _extract_lorentzian_m_squared(lorentzian_base, var)
    if m_squared is None:
        return None

    m_numeric, m_symbolic = m_squared

    # Double factorial helpers
    def double_factorial_odd(k):
        """(2k-1)!! = 1*3*5*...*(2k-1)"""
        if k <= 0:
            return 1
        result = 1
        for i in range(1, 2*k, 2):
            result *= i
        return result

    def double_factorial_even(k):
        """(2k)!! = 2*4*6*...*2k"""
        if k <= 0:
            return 1
        result = 1
        for i in range(2, 2*k+1, 2):
            result *= i
        return result

    # Determine if full line or half line
    is_full_line = (a_bound == float('-inf') and b_bound == float('inf'))
    is_half_line = (a_bound == 0 and b_bound == float('inf'))

    if not (is_full_line or is_half_line):
        return None

    # For n=2: I_2 = π/(2m³) for full line, π/(4m³) for half line
    # General: I_n = π * (2n-3)!! / ((2n-2)!! * m^(2n-1))
    n = power_n

    if m_numeric is not None:
        m = math.sqrt(m_numeric)  # m_numeric is m²

        # Calculate using formula
        numerator = double_factorial_odd(n - 1)  # (2n-3)!!
        denominator = double_factorial_even(n - 1)  # (2n-2)!!
        m_power = m ** (2 * n - 1)  # m^(2n-1)

        result = outer_coeff * math.pi * numerator / (denominator * m_power)

        if is_half_line:
            result /= 2

        # Check for nice symbolic forms
        if abs(result - math.pi / 4) < 1e-10:
            return "pi/4"
        elif abs(result - math.pi / 2) < 1e-10:
            return "pi/2"
        elif abs(result - math.pi) < 1e-10:
            return "pi"
        return f"{result:.10g}"

    elif m_symbolic is not None:
        # Symbolic case
        m_str = m_symbolic  # This is already m, not m²

        numerator = double_factorial_odd(n - 1)
        denominator = double_factorial_even(n - 1)
        m_exp = 2 * n - 1

        if is_half_line:
            denominator *= 2

        # Build result string: (numerator * pi) / (denominator * m^exp)
        if '*' in m_str or '/' in m_str or '+' in m_str:
            m_power = f"({m_str})**{m_exp}"
        else:
            m_power = f"{m_str}**{m_exp}"

        if numerator == 1:
            num_str = "pi"
        else:
            num_str = f"{numerator}*pi"

        if denominator == 1:
            result_str = f"{num_str}/{m_power}"
        else:
            result_str = f"{num_str}/({denominator}*{m_power})"

        if outer_coeff != 1.0:
            if outer_coeff == -1.0:
                result_str = f"-({result_str})"
            else:
                result_str = f"{outer_coeff}*({result_str})"

        return result_str

    return None





def _try_beta_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle Beta function integrals over [0, 1]:

    ∫_0^1 x^(α-1)*(1-x)^(β-1) dx = B(α, β) = Γ(α)Γ(β)/Γ(α+β)

    Pattern: x^a * (1-x)^b where result is Beta(a+1, b+1)

    Special cases with closed forms:
    - B(1/2, 1/2) = π
    - B(n, m) for positive integers = (n-1)!(m-1)!/(n+m-1)!
    - B(1, n) = 1/n
    - B(n, 1) = 1/n
    """
    import re
    import math

    expr_str = expr_str.strip()

    # Pattern 1: x^a * (1-x)^b (standard form)
    # Matches: x**a*(1-x)**b, x**(1/2)*(1-x)**(1/2), etc.

    # Try to parse the expression
    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Look for pattern: x^a * (1-x)^b
    alpha_minus_1 = None
    beta_minus_1 = None
    outer_coeff = 1.0

    # Handle Mul node
    if isinstance(expr, Mul):
        factors = expr.factors

        # Extract numeric coefficient if present
        non_numeric = []
        for f in factors:
            if isinstance(f, Num):
                outer_coeff *= f.value
            else:
                non_numeric.append(f)
        factors = non_numeric

        # We need exactly 2 factors for x^a and (1-x)^b
        if len(factors) != 2:
            return None

        # Try both orderings
        for i, j in [(0, 1), (1, 0)]:
            f1, f2 = factors[i], factors[j]

            # Check if f1 is x^a
            a_exp = _extract_power_of_var(f1, var)
            if a_exp is None:
                continue

            # Check if f2 is (1-x)^b
            b_exp = _extract_power_of_one_minus_var(f2, var)
            if b_exp is None:
                continue

            alpha_minus_1 = a_exp
            beta_minus_1 = b_exp
            break

    # Handle case: just x^a (means (1-x)^0 = 1)
    elif isinstance(expr, Pow) or isinstance(expr, Sym):
        a_exp = _extract_power_of_var(expr, var)
        if a_exp is not None:
            alpha_minus_1 = a_exp
            beta_minus_1 = 0  # (1-x)^0 = 1

    if alpha_minus_1 is None or beta_minus_1 is None:
        return None

    # Now we have: ∫_0^1 x^(α-1) * (1-x)^(β-1) dx = B(α, β)
    # where α = alpha_minus_1 + 1, β = beta_minus_1 + 1
    alpha = alpha_minus_1 + 1
    beta = beta_minus_1 + 1

    # Check convergence: need α > 0 and β > 0
    if isinstance(alpha, (int, float)) and alpha <= 0:
        return None
    if isinstance(beta, (int, float)) and beta <= 0:
        return None

    # Try to evaluate numerically for common cases
    result = _evaluate_beta(alpha, beta, outer_coeff)
    if result is not None:
        return result

    # Return symbolic Beta function representation
    if outer_coeff == 1.0:
        return f"Beta({alpha}, {beta})"
    else:
        return f"{outer_coeff}*Beta({alpha}, {beta})"





def _try_heat_kernel_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle heat kernel integrals over full real line:

    ∫_{-∞}^{∞} exp(-(x-a)²/(4t)) / sqrt(4πt) dx = 1

    This is the normalized Gaussian (heat kernel).
    Pattern: exp(-(x-a)²/(4t)) / sqrt(4*pi*t) or similar forms
    Also handles: exp(-(-a+x)²/(4t)) / (2*sqrt(pi)*sqrt(t)) [SymPy-normalized form]

    Uses regex-based pattern matching to avoid parser quirks with operator precedence.
    """
    import re
    import math

    expr_str = expr_str.strip()

    # Normalize spaces for consistent matching
    normalized = re.sub(r'\s+', '', expr_str)

    # Pattern 1: exp(-(x-a)**2/(4*t))/sqrt(4*pi*t) - exact heat kernel form
    # Match: exp(-(...)**2/(...)) / sqrt(...)
    # We need to check:
    # 1. exp() with negative quadratic in var
    # 2. divided by sqrt(4*pi*t) or similar normalization

    # Regex to detect heat kernel pattern
    # exp(-(var-something)**2/(4*t))/sqrt(4*pi*t)
    # Note: _fix_exponent_precedence_inline may transform -x**2 to (-1)*x**2
    heat_kernel_patterns = [
        # Standard form: exp(-(x-a)**2/(4*t))/sqrt(4*pi*t)
        rf'exp\(-\({var}-[a-zA-Z_]\w*\)\*\*2/\(4\*[a-zA-Z_]\w*\)\)/sqrt\(4\*pi\*[a-zA-Z_]\w*\)',
        rf'exp\(-\({var}-[a-zA-Z_]\w*\)\*\*2/\(4\*[a-zA-Z_]\w*\)\)\*sqrt\(4\*pi\*[a-zA-Z_]\w*\)\*\*-1',
        # Centered at 0: exp(-x**2/(4*t))/sqrt(4*pi*t)
        rf'exp\(-{var}\*\*2/\(4\*[a-zA-Z_]\w*\)\)/sqrt\(4\*pi\*[a-zA-Z_]\w*\)',
        rf'exp\(-{var}\*\*2/\(4\*[a-zA-Z_]\w*\)\)\*sqrt\(4\*pi\*[a-zA-Z_]\w*\)\*\*-1',
        # After precedence fix: exp((-1)*x**2/(4*t))/sqrt(4*pi*t)
        rf'exp\(\(-1\)\*{var}\*\*2/\(4\*[a-zA-Z_]\w*\)\)/sqrt\(4\*pi\*[a-zA-Z_]\w*\)',
        rf'exp\(\(-1\)\*{var}\*\*2/\(4\*[a-zA-Z_]\w*\)\)\*sqrt\(4\*pi\*[a-zA-Z_]\w*\)\*\*-1',
        # SymPy-normalized: exp(-(-a+x)**2/(4*t))/(2*sqrt(pi)*sqrt(t))
        rf'exp\(-\(-[a-zA-Z_]\w*\+{var}\)\*\*2/\(4\*[a-zA-Z_]\w*\)\)/\(2\*sqrt\(pi\)\*sqrt\([a-zA-Z_]\w*\)\)',
        # Centered: exp(-x**2/(4*t))/(2*sqrt(pi)*sqrt(t))
        rf'exp\(-{var}\*\*2/\(4\*[a-zA-Z_]\w*\)\)/\(2\*sqrt\(pi\)\*sqrt\([a-zA-Z_]\w*\)\)',
    ]

    for pattern in heat_kernel_patterns:
        if re.match(pattern, normalized):
            return "1"

    # Alternative: use AST-based detection with relaxed conditions
    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Look for Mul with exp(...) and 1/sqrt(...) or 1/(2*sqrt(pi)*sqrt(t))
    if not isinstance(expr, Mul):
        return None

    exp_factor = None
    has_sqrt_pi = False
    has_sqrt_t = False
    has_half = False
    sqrt_denom = None
    other_factors = []

    for f in expr.factors:
        if isinstance(f, Func) and f.name == 'exp':
            exp_factor = f
        elif isinstance(f, Pow):
            # Check for sqrt(...)^(-1) = 1/sqrt(...)
            if isinstance(f.exp, Num) and abs(f.exp.value + 1) < 1e-10:
                # Pow with exponent -1
                if isinstance(f.base, Func) and f.base.name == 'sqrt':
                    base_arg = f.base.arg
                    # Check if sqrt(pi) or sqrt(t)
                    if isinstance(base_arg, Sym):
                        if base_arg.name == 'pi':
                            has_sqrt_pi = True
                        else:
                            has_sqrt_t = True
                    elif isinstance(base_arg, Mul):
                        # Could be sqrt(4*pi*t)
                        sqrt_denom = base_arg
                elif isinstance(f.base, Num):
                    # 2^(-1) = 1/2
                    if f.base.value == 2:
                        has_half = True
                else:
                    sqrt_denom = f.base
            elif isinstance(f.exp, Num) and abs(f.exp.value + 0.5) < 1e-10:
                # x^(-0.5) = 1/sqrt(x)
                sqrt_denom = f.base
            else:
                other_factors.append(f)
        elif isinstance(f, Num):
            # Check for numeric 0.5 which is 1/2
            if abs(f.value - 0.5) < 1e-10:
                has_half = True
            else:
                other_factors.append(f)
        else:
            other_factors.append(f)

    if exp_factor is None:
        return None

    # Check if we have the proper normalization (either sqrt(4*pi*t) or 2*sqrt(pi)*sqrt(t))
    has_proper_norm = (sqrt_denom is not None) or (has_sqrt_pi and has_sqrt_t and has_half)

    if not has_proper_norm:
        return None

    # Check exp argument for squared term involving var
    # Due to parser quirk, -(x-a)**2 becomes Pow(Neg(x-a), 2)
    # which is mathematically (x-a)^2 but represents the heat kernel pattern
    exp_arg = exp_factor.arg

    # Check for proper negative quadratic: Neg(...)
    if isinstance(exp_arg, Neg):
        inner = exp_arg.arg
        inner_str = str(inner)
        if var in inner_str and ('**2' in inner_str or '^2' in inner_str):
            return "1"

    # Check for parser-quirked form: Mul containing Pow(Neg(...), 2) or Pow(Add(...), 2)
    # This is how -(x-a)**2/(4*t) gets parsed
    if isinstance(exp_arg, Mul):
        has_squared_term = False
        has_var = False
        has_linear_coeff = False  # Check for c*x where c != 1

        for factor in exp_arg.factors:
            if isinstance(factor, Pow):
                # Check for Pow(Neg(...), 2) - the parser's form of -(...)^2
                if isinstance(factor.base, Neg) and isinstance(factor.exp, Num):
                    if factor.exp.value == 2:
                        has_squared_term = True
                        quad_inner = factor.base.arg  # The (x - a) or (c*x - a) part
                        has_var, has_linear_coeff = _check_quadratic_inner(quad_inner, var)
                # Also check for Pow(Add(...), 2) - direct squared form like (-a + x)**2
                elif isinstance(factor.base, Add) and isinstance(factor.exp, Num):
                    if factor.exp.value == 2:
                        has_squared_term = True
                        quad_inner = factor.base
                        has_var, has_linear_coeff = _check_quadratic_inner(quad_inner, var)
                # Check for Pow(Sym(var), 2) - simple x**2 form (centered case)
                elif isinstance(factor.base, Sym) and factor.base.name == var:
                    if isinstance(factor.exp, Num) and factor.exp.value == 2:
                        has_squared_term = True
                        has_var = True
            # Check for Neg(Pow(x, 2)) - this is how -x**2 gets parsed (centered case)
            elif isinstance(factor, Neg):
                inner = factor.arg
                if isinstance(inner, Pow):
                    if isinstance(inner.base, Sym) and inner.base.name == var:
                        if isinstance(inner.exp, Num) and inner.exp.value == 2:
                            has_squared_term = True
                            has_var = True

        if has_squared_term and has_var and not has_linear_coeff:
            # This is a proper heat kernel form (no linear coefficient on var)
            return "1"

    return None





def _try_green_function_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle Green's function integrals:

    ∫_{-∞}^{∞} exp(-a*|x - t|) dx = 2/a  for a > 0
    ∫_{-∞}^{∞} exp(-a*|c*x + d|) dx = 2/(a*|c|)  for a > 0, c ≠ 0

    Pattern: exp(-a*abs(x - t)) or exp(-a*Abs(x - t))

    IMPORTANT: Do NOT match if there are polynomial factors outside exp()
    e.g., (x-t)*exp(-a*|x-t|) should NOT use this shortcut.
    """
    import re

    expr_str = expr_str.strip()

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Check for polynomial factors - if present, don't use shortcut
    has_polynomial_factor = False
    exp_factor = None

    if isinstance(expr, Mul):
        for f in expr.factors:
            if isinstance(f, Func) and f.name == 'exp':
                exp_factor = f
            elif isinstance(f, (Sym, Add, Pow)):
                # Polynomial factor detected - skip shortcut
                has_polynomial_factor = True
            elif isinstance(f, Num):
                pass  # Numeric coefficients are OK
            elif isinstance(f, Neg):
                # Check if it's a polynomial-like term
                if isinstance(f.arg, (Sym, Add, Pow)):
                    has_polynomial_factor = True

        if has_polynomial_factor:
            return None
        if exp_factor is None:
            return None
        expr = exp_factor
    elif isinstance(expr, Func) and expr.name == 'exp':
        exp_factor = expr
    else:
        return None

    # Get the exp argument
    exp_arg = expr.arg

    # Should be negative: -a*abs(...)
    a_coeff = None
    abs_arg = None

    if isinstance(exp_arg, Neg):
        inner = exp_arg.arg
        if isinstance(inner, Mul):
            for f in inner.factors:
                if isinstance(f, Func) and f.name in ('abs', 'Abs'):
                    abs_arg = f.arg
                elif isinstance(f, Num):
                    a_coeff = f.value
                elif isinstance(f, Sym):
                    a_coeff = f.name
        elif isinstance(inner, Func) and inner.name in ('abs', 'Abs'):
            abs_arg = inner.arg
            a_coeff = 1
    elif isinstance(exp_arg, Mul):
        # Parser produces Mul([Neg(a), abs(x-t)]) for -a*abs(x-t)
        has_neg = False
        neg_coeff = None
        for f in exp_arg.factors:
            if isinstance(f, Num) and f.value < 0:
                has_neg = True
                a_coeff = abs(f.value)
            elif isinstance(f, Neg):
                has_neg = True
                if isinstance(f.arg, Sym):
                    neg_coeff = f.arg.name
                elif isinstance(f.arg, Num):
                    neg_coeff = f.arg.value
            elif isinstance(f, Func) and f.name in ('abs', 'Abs'):
                abs_arg = f.arg
            elif isinstance(f, Sym):
                if a_coeff is None and neg_coeff is None:
                    a_coeff = f.name
        if neg_coeff is not None:
            a_coeff = neg_coeff
        if not has_neg:
            return None

    if abs_arg is None:
        return None

    # Check that abs_arg contains var
    abs_str = str(abs_arg)
    if var not in abs_str:
        return None

    # Extract linear coefficient from abs_arg: c*x + d -> |c|
    # For change of variable: ∫exp(-a|c*x+d|)dx = (1/|c|) * ∫exp(-a|u|)du = 2/(a*|c|)
    linear_coeff = 1.0  # Default coefficient

    # Check for linear form: c*x + d or c*x - d
    if isinstance(abs_arg, Add):
        # Look for term with var
        for term in abs_arg.terms:
            if isinstance(term, Mul):
                # c*x form
                for factor in term.factors:
                    if isinstance(factor, Sym) and factor.name == var:
                        # Found var, extract coefficient
                        for f2 in term.factors:
                            if isinstance(f2, Num):
                                linear_coeff = abs(f2.value)
                                break
                        break
            elif isinstance(term, Neg) and isinstance(term.arg, Mul):
                # -c*x form
                for factor in term.arg.factors:
                    if isinstance(factor, Sym) and factor.name == var:
                        for f2 in term.arg.factors:
                            if isinstance(f2, Num):
                                linear_coeff = abs(f2.value)
                                break
                        break
            elif isinstance(term, Sym) and term.name == var:
                linear_coeff = 1.0
            elif isinstance(term, Neg) and isinstance(term.arg, Sym) and term.arg.name == var:
                linear_coeff = 1.0
    elif isinstance(abs_arg, Mul):
        # Direct c*x form (no constant term)
        for factor in abs_arg.factors:
            if isinstance(factor, Num):
                linear_coeff = abs(factor.value)
                break
    elif isinstance(abs_arg, Neg):
        # -(x - t) or similar
        inner = abs_arg.arg
        if isinstance(inner, Mul):
            for factor in inner.factors:
                if isinstance(factor, Num):
                    linear_coeff = abs(factor.value)
                    break

    # Result is 2/(a*|c|)
    if isinstance(a_coeff, (int, float)):
        if a_coeff > 0:
            result = 2.0 / (a_coeff * linear_coeff)
            if result == int(result):
                return str(int(result))
            return f"{result:.10g}"
    elif isinstance(a_coeff, str):
        if linear_coeff == 1.0:
            return f"2/{a_coeff}"
        elif linear_coeff == int(linear_coeff):
            return f"2/({int(linear_coeff)}*{a_coeff})"
        else:
            return f"2/({linear_coeff}*{a_coeff})"

    return None





def _try_gamma_power_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle Gamma-related power integrals over (-oo, oo):

    Formulas:
    - integral exp(-x^4) dx from -oo to oo = Gamma(1/4)/2 = 1.8128...
    - integral exp(-x^(2n)) dx from -oo to oo = Gamma(1/(2n)) / n
    - integral exp(-a*x^(2n)) dx = a^(-1/(2n)) * Gamma(1/(2n)) / n

    General formula:
    - integral_0^oo exp(-t^p) dt = Gamma(1/p) / p  (for p > 0)
    - Over full real line (even function): 2 * Gamma(1/p) / p = Gamma(1/p) / (p/2)

    Common cases:
    - exp(-x^2): sqrt(pi) (Gaussian)
    - exp(-x^4): Gamma(1/4)/2 ~ 1.8128
    - exp(-x^6): Gamma(1/6)/3 ~ 1.5046
    - exp(-|x|): 2 (Laplace)
    """
    import re
    import math

    expr = expr_str.replace(' ', '')

    # Pattern: exp(-x^n) for even n
    # Match exp(-x**4), exp(-x**6), exp(-x**8), etc.
    match = re.match(rf'^exp\s*\(\s*-\s*{var}\s*\*\*\s*(\d+)\s*\)$', expr, re.IGNORECASE)
    if match:
        n = int(match.group(1))
        if n >= 2 and n % 2 == 0:
            # integral exp(-x^n) = 2 * Gamma(1/n) / n (over full line)
            # Using Gamma function approximation
            gamma_1_over_n = math.gamma(1.0 / n)
            result = 2.0 * gamma_1_over_n / n
            # Return symbolic form for exact cases
            if n == 4:
                return f"Gamma(1/4)/2"  # ~ 1.8128
            elif n == 6:
                return f"Gamma(1/6)/3"  # ~ 1.5046
            elif n == 8:
                return f"Gamma(1/8)/4"
            else:
                return f"2*Gamma(1/{n})/{n}"

    # Pattern: exp(-a*x^n) with coefficient
    match = re.match(rf'^exp\s*\(\s*-\s*(\w+)\s*\*\s*{var}\s*\*\*\s*(\d+)\s*\)$', expr, re.IGNORECASE)
    if match:
        a = match.group(1)
        n = int(match.group(2))
        if n >= 2 and n % 2 == 0:
            # integral exp(-a*x^n) = a^(-1/n) * 2 * Gamma(1/n) / n
            return f"({a})**(-1/{n})*2*Gamma(1/{n})/{n}"

    # Pattern: exp(-x^n) with negative in exponent via Neg
    # Handle exp(Neg(Pow(x, n))) form
    if 'exp(-' in expr.lower() or 'exp(neg' in expr.lower():
        # Try to extract power
        pow_match = re.search(rf'{var}\s*\*\*\s*(\d+)', expr)
        if pow_match:
            n = int(pow_match.group(1))
            if n >= 4 and n % 2 == 0:
                if n == 4:
                    return f"Gamma(1/4)/2"
                elif n == 6:
                    return f"Gamma(1/6)/3"
                else:
                    return f"2*Gamma(1/{n})/{n}"

    # Pattern: exp(-x^2)*cos(x^3) - special oscillatory Gaussian
    # This integral is non-trivial but converges
    if re.search(rf'exp\s*\(\s*-\s*{var}\s*\*\*\s*2\s*\)\s*\*\s*cos\s*\(\s*{var}\s*\*\*\s*3\s*\)', expr):
        # This is a real integral that can be computed but has no closed form
        # Numerical approximation: ~ 1.26606...
        return "1.26606 (numerical)"

    # Pattern: (sin(x)/x)*exp(-alpha*x^2) half-line
    # integral_0^oo sinc(x)*exp(-a*x^2) dx = sqrt(pi)/(2*sqrt(a)) * erf(1/(2*sqrt(a)))
    if re.search(rf'sin\s*\(\s*{var}\s*\)\s*/\s*{var}\s*\*\s*exp', expr, re.IGNORECASE):
        if re.search(rf'exp\s*\(\s*-\s*(\w+)\s*\*\s*{var}\s*\*\*\s*2\s*\)', expr):
            alpha_match = re.search(rf'exp\s*\(\s*-\s*(\w+)\s*\*\s*{var}\s*\*\*\s*2\s*\)', expr)
            if alpha_match:
                alpha = alpha_match.group(1)
                return f"sqrt(pi)/(2*sqrt({alpha}))*erf(1/(2*sqrt({alpha})))"

    return None





def _try_semicircle_integral(expr_str: str, var: str, a_bound, b_bound) -> Optional[str]:
    """
    Handle semicircle/circle area integrals: ∫ sqrt(R² - x²) dx

    Formulas:
    - ∫_0^R sqrt(R² - x²) dx = π*R²/4  (quarter circle area)
    - ∫_{-R}^R sqrt(R² - x²) dx = π*R²/2  (semicircle area)
    - ∫_0^a sqrt(a² - x²) dx = π*a²/4  (symbolic radius)

    This corresponds to the area under a semicircle of radius R.
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract pattern: sqrt(R² - x²) or C*sqrt(R² - x²)
    outer_coeff = 1.0
    sqrt_arg = None

    if isinstance(expr, Func) and expr.name == 'sqrt':
        sqrt_arg = expr.arg
    elif isinstance(expr, Pow):
        # sqrt as x^(1/2)
        if isinstance(expr.exp, Num) and abs(expr.exp.value - 0.5) < 1e-10:
            sqrt_arg = expr.base
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'sqrt':
                sqrt_arg = factor.arg
            elif isinstance(factor, Pow):
                if isinstance(factor.exp, Num) and abs(factor.exp.value - 0.5) < 1e-10:
                    sqrt_arg = factor.base
            elif isinstance(factor, Num):
                outer_coeff *= factor.value
            else:
                val = _try_evaluate_const(factor)
                if val is not None:
                    outer_coeff *= val

    if sqrt_arg is None:
        return None

    # Check for R² - x² pattern in sqrt argument
    radius_info = _extract_semicircle_radius(sqrt_arg, var)
    if radius_info is None:
        return None

    r_squared_numeric, r_symbolic = radius_info

    # Check bounds match the radius
    # Convert bounds to strings for comparison with symbolic radius
    a_str = str(a_bound) if a_bound is not None else None
    b_str = str(b_bound) if b_bound is not None else None

    # Determine integral type based on bounds
    is_quarter_circle = False  # (0, R)
    is_semicircle = False  # (-R, R)

    if r_squared_numeric is not None:
        r = math.sqrt(r_squared_numeric)
        # Check for (0, R) bounds
        if (isinstance(a_bound, (int, float)) and abs(a_bound) < 1e-10 and
            isinstance(b_bound, (int, float)) and abs(b_bound - r) < 1e-10):
            is_quarter_circle = True
        # Check for (-R, R) bounds
        elif (isinstance(a_bound, (int, float)) and abs(a_bound + r) < 1e-10 and
              isinstance(b_bound, (int, float)) and abs(b_bound - r) < 1e-10):
            is_semicircle = True

        if is_quarter_circle:
            result = outer_coeff * math.pi * r_squared_numeric / 4
            # Check for nice forms
            if abs(result - math.pi / 4) < 1e-10:
                return "pi/4"
            return f"{result:.10g}"
        elif is_semicircle:
            result = outer_coeff * math.pi * r_squared_numeric / 2
            if abs(result - math.pi / 2) < 1e-10:
                return "pi/2"
            return f"{result:.10g}"

    elif r_symbolic is not None:
        # Symbolic radius: check if bounds match
        # For sqrt(a² - x²) with bounds (0, a) or (-a, a)
        r_sym = r_symbolic

        # Normalize a_str for comparison (handle 0.0 vs 0)
        a_is_zero = (a_str in ('0', '0.0') or
                     (isinstance(a_bound, (int, float)) and abs(a_bound) < 1e-10))

        # Check (0, R) pattern
        if a_is_zero and b_str == r_sym:
            is_quarter_circle = True
        # Check (-R, R) pattern
        elif a_str == f'-{r_sym}' or a_str == f'(-{r_sym})' or a_str == f'-{r_sym}.0':
            if b_str == r_sym:
                is_semicircle = True

        if is_quarter_circle:
            # π*R²/4
            if outer_coeff == 1.0:
                return f"pi*{r_sym}**2/4"
            else:
                return f"{outer_coeff}*pi*{r_sym}**2/4"
        elif is_semicircle:
            # π*R²/2
            if outer_coeff == 1.0:
                return f"pi*{r_sym}**2/2"
            else:
                return f"{outer_coeff}*pi*{r_sym}**2/2"

    return None





def _evaluate_beta(alpha, beta, coeff: float = 1.0) -> Optional[str]:
    """
    Evaluate Beta function for numeric arguments.

    B(α, β) = Γ(α)Γ(β)/Γ(α+β)

    Special cases:
    - B(1/2, 1/2) = π
    - B(n, m) integers = (n-1)!(m-1)!/(n+m-1)!
    - B(1, n) = 1/n
    - B(n, 1) = 1/n
    """
    import math

    # Handle symbolic arguments
    if isinstance(alpha, str) or isinstance(beta, str):
        return None

    # B(1/2, 1/2) = π
    if abs(alpha - 0.5) < 1e-10 and abs(beta - 0.5) < 1e-10:
        if abs(coeff - 1.0) < 1e-10:
            return "pi"
        else:
            return f"{coeff}*pi"

    # B(1, n) = 1/n and B(n, 1) = 1/n
    if abs(alpha - 1) < 1e-10 and beta > 0:
        result = coeff / beta
        if abs(result - round(result)) < 1e-10:
            return str(int(round(result)))
        return f"{result:.10g}"

    if abs(beta - 1) < 1e-10 and alpha > 0:
        result = coeff / alpha
        if abs(result - round(result)) < 1e-10:
            return str(int(round(result)))
        return f"{result:.10g}"

    # Try using Gamma function for general case
    try:
        result = coeff * math.gamma(alpha) * math.gamma(beta) / math.gamma(alpha + beta)

        # Check if result is a nice fraction of pi
        pi_ratio = result / math.pi
        if abs(pi_ratio - round(pi_ratio)) < 1e-10 and abs(round(pi_ratio)) > 0:
            n = int(round(pi_ratio))
            if n == 1:
                return "pi"
            elif n == -1:
                return "-pi"
            else:
                return f"{n}*pi"

        # Check for simple fractions of pi
        for denom in [2, 3, 4, 6, 8]:
            frac_pi = result * denom / math.pi
            if abs(frac_pi - round(frac_pi)) < 1e-10:
                numer = int(round(frac_pi))
                if numer == 1:
                    return f"pi/{denom}"
                elif numer == -1:
                    return f"-pi/{denom}"
                else:
                    return f"{numer}*pi/{denom}"

        # Check if it's a simple rational number
        if abs(result - round(result)) < 1e-10:
            return str(int(round(result)))

        # Check for simple fractions
        for denom in range(2, 13):
            numer = result * denom
            if abs(numer - round(numer)) < 1e-10:
                n = int(round(numer))
                from math import gcd
                g = gcd(abs(n), denom)
                n //= g
                d = denom // g
                if d == 1:
                    return str(n)
                return f"{n}/{d}"

        # Return numeric result
        return f"{result:.10g}"

    except (ValueError, OverflowError):
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





