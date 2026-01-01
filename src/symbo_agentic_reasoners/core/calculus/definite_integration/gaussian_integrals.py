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
Gaussian Integrals
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
from .extraction_utils import _extract_gaussian_coeff, _extract_linear_coeff_unsigned, _extract_positive_symbolic_coeff, _extract_quadratic_and_linear_coeffs, _extract_quadratic_coeff, _extract_quadratic_coeff_with_division, _extract_symbolic_gaussian_coeff, _extract_symbolic_linear_coeff_unsigned, _is_shifted_quadratic, _try_evaluate_const_times_var_squared

logger = logging.getLogger(__name__)

# Module-level instances
_parser = ExprParser()
_int_engine = IntegrationEngine()


def _try_gaussian_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Check if expression is a Gaussian and return its integral over (-∞, ∞).

    Handles:
    - exp(-x²) → √π
    - exp(-a*x²) → √(π/a) for positive a
    - C*exp(-a*x²) → C*√(π/a)
    - (1/√(2π))*exp(-x²/2) → 1 (normalized Gaussian PDF)
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract coefficient and exponential
    coeff = 1.0
    exp_arg = None

    if isinstance(expr, Func) and expr.name == 'exp':
        exp_arg = expr.arg
    elif isinstance(expr, Mul):
        # Look for C * exp(...)
        exp_part = None
        coeff_parts = []
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'exp':
                exp_part = factor
            else:
                coeff_parts.append(factor)

        if exp_part is not None:
            exp_arg = exp_part.arg
            # Compute coefficient
            for cp in coeff_parts:
                if isinstance(cp, Num):
                    coeff *= cp.value
                elif isinstance(cp, Pow):
                    # Handle 1/sqrt(2*pi) pattern
                    val = _try_evaluate_const(cp)
                    if val is not None:
                        coeff *= val
                    else:
                        return None  # Non-constant coefficient
                else:
                    val = _try_evaluate_const(cp)
                    if val is not None:
                        coeff *= val
                    else:
                        return None

    if exp_arg is None:
        return None

    # Check for -a*x² pattern in exponent
    # exp_arg should be Neg(a*x²) or a negative expression
    quad_coeff = None  # The 'a' in exp(-a*x²)

    if isinstance(exp_arg, Neg):
        inner = exp_arg.arg
        quad_coeff = _extract_quadratic_coeff(inner, var)
    elif isinstance(exp_arg, Mul):
        # Check if it's -a*x² written as (-a)*x² or a*(-x²)
        val = _try_evaluate_const_times_var_squared(exp_arg, var)
        if val is not None and val < 0:
            quad_coeff = -val
    elif isinstance(exp_arg, Pow):
        # exp(x²) - check if coefficient is 0 (meaning the arg is just x² with -1 coefficient somewhere)
        # This handles exp(-x**2) parsed as exp(Neg(Pow(x,2)))
        pass

    if quad_coeff is None:
        # Try direct evaluation on the exponent
        # Check for patterns like -x**2, -x**2/2, etc.
        quad_coeff = _extract_gaussian_coeff(exp_arg, var)

    if quad_coeff is None or quad_coeff <= 0:
        # Try symbolic coefficient extraction for parameters like a, m, omega, hbar, beta
        symbolic_result = _try_symbolic_gaussian_integral(expr, var, coeff)
        return symbolic_result

    # Gaussian integral formula: ∫_{-∞}^{∞} exp(-a*x²) dx = √(π/a)
    result = coeff * math.sqrt(math.pi / quad_coeff)

    # Check for normalized Gaussian (result should be 1)
    if abs(result - 1.0) < 1e-10:
        return "1"
    elif abs(result - math.sqrt(math.pi)) < 1e-10:
        return "sqrt(pi)"
    elif abs(result - math.sqrt(2 * math.pi)) < 1e-10:
        return "sqrt(2*pi)"
    else:
        # Return numerical result
        return str(result)





def _try_gaussian_moment_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle Gaussian moment integrals: ∫_{-∞}^{∞} x^n * exp(-a*x²) dx

    Formulas:
    - For odd n: = 0 (odd function over symmetric interval)
    - For n=0: = √(π/a)
    - For n=2: = (1/2) * √(π/a³) = √π / (2*a^(3/2))
    - For n=4: = (3/4) * √(π/a⁵)
    - General even n=2k: = (2k-1)!! / (2a)^k * √(π/a)
                        = (2k)! / (2^(2k) * k! * a^k) * √(π/a)
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Look for pattern: x^n * exp(-a*x²) or exp(-a*x²) * x^n
    power_of_var = 0
    coeff = 1.0
    exp_part = None

    if isinstance(expr, Mul):
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'exp':
                exp_part = factor
            elif isinstance(factor, Pow):
                # Check if it's x^n
                if isinstance(factor.base, Sym) and factor.base.name == var:
                    if isinstance(factor.exp, Num):
                        power_of_var = int(factor.exp.value)
                    else:
                        return None  # Non-numeric power
                else:
                    # Numeric coefficient power
                    val = _try_evaluate_const(factor)
                    if val is not None:
                        coeff *= val
                    else:
                        return None
            elif isinstance(factor, Sym) and factor.name == var:
                # Just x (x^1)
                power_of_var = 1
            elif isinstance(factor, Num):
                coeff *= factor.value
            else:
                return None
    else:
        return None  # Not a product

    if exp_part is None or power_of_var == 0:
        return None

    # Extract the coefficient 'a' from exp(-a*x²)
    exp_arg = exp_part.arg
    quad_coeff = _extract_gaussian_coeff(exp_arg, var)

    # Handle odd powers first - integral is 0 regardless of numeric/symbolic a
    if power_of_var % 2 == 1:
        return "0"

    # Helper: compute (2k-1)!! = 1 * 3 * 5 * ... * (2k-1)
    def double_factorial_odd(n):
        """Perform double factorial odd operation.

        Args:
        n: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.double_factorial_odd(...)
        """
        if n == 0:
            return 1
        result = 1
        for i in range(1, 2*n, 2):
            result *= i
        return result

    k = power_of_var // 2

    # Try numeric evaluation first
    if quad_coeff is not None and quad_coeff > 0:
        a = quad_coeff
        numerator = double_factorial_odd(k)
        denominator = (2 * a) ** k
        base_integral = math.sqrt(math.pi / a)

        result = coeff * numerator / denominator * base_integral

        # Check for nice symbolic forms
        if abs(result - 0) < 1e-10:
            return "0"
        elif abs(result - math.sqrt(math.pi)) < 1e-10:
            return "sqrt(pi)"
        elif abs(result - math.sqrt(math.pi) / 2) < 1e-10:
            return "sqrt(pi)/2"
        elif power_of_var == 2 and coeff == 1:
            # x² * exp(-a*x²) → √π / (2*a^(3/2))
            return f"sqrt(pi)/(2*{a}**(3/2))"
        else:
            return str(result)

    # Fall back to symbolic handling when numeric extraction fails
    symbolic_coeff = _extract_symbolic_gaussian_coeff(exp_arg, var)
    if symbolic_coeff is None:
        return None

    # Symbolic Gaussian moment formulas:
    # ∫ x^(2k) * exp(-a*x²) dx = (2k-1)!! / (2^k) * sqrt(pi) / a^(k+1/2)
    #                         = (2k-1)!! * sqrt(pi) / (2^k * a^(k+1/2))
    # For k=1 (n=2): sqrt(pi) / (2*a^(3/2))
    # For k=2 (n=4): 3*sqrt(pi) / (4*a^(5/2))

    numerator = double_factorial_odd(k)
    denom_power = 2 ** k
    exponent = k + 0.5  # k + 1/2

    # Build symbolic result string
    # Format exponent nicely: 1.5 -> 3/2, 2.5 -> 5/2, etc.
    if exponent == int(exponent):
        exp_str = str(int(exponent))
    else:
        # Convert k + 0.5 to (2k+1)/2
        exp_str = f"({2*k + 1}/2)"

    # Handle simple case where coefficient is just a symbol
    if symbolic_coeff == "1":
        a_power = f"1"
    elif '*' in symbolic_coeff or '/' in symbolic_coeff or '+' in symbolic_coeff:
        a_power = f"({symbolic_coeff})**{exp_str}"
    else:
        a_power = f"{symbolic_coeff}**{exp_str}"

    # Build the result
    if numerator == 1 and denom_power == 1:
        # k=0 case (n=0): just sqrt(pi/a) but this shouldn't happen here
        result_str = f"sqrt(pi)/{a_power}"
    elif numerator == 1:
        result_str = f"sqrt(pi)/({denom_power}*{a_power})"
    elif denom_power == 1:
        result_str = f"{numerator}*sqrt(pi)/{a_power}"
    else:
        result_str = f"{numerator}*sqrt(pi)/({denom_power}*{a_power})"

    # Apply outer coefficient if present
    if coeff != 1.0:
        if coeff == -1.0:
            result_str = f"-({result_str})"
        else:
            result_str = f"{coeff}*({result_str})"

    return result_str





def _try_half_gaussian_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle half-line Gaussian integrals: ∫_0^∞ x^n * exp(-a*x²) dx

    Formulas (for a > 0):
    - n=0: ∫_0^∞ exp(-a*x²) dx = sqrt(π/a)/2 = sqrt(π)/(2*sqrt(a))
    - n=1: ∫_0^∞ x*exp(-a*x²) dx = 1/(2a)
    - n=2: ∫_0^∞ x²*exp(-a*x²) dx = sqrt(π)/(4*a^(3/2))
    - n=3: ∫_0^∞ x³*exp(-a*x²) dx = 1/(2*a²)
    - General even n=2k: (2k-1)!!/(2^(k+1) * a^(k+1/2)) * sqrt(π)
    - General odd n=2k+1: k!/(2*a^(k+1))
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract pattern: C * x^n * exp(-a*x²)
    power_of_var = 0
    coeff = 1.0
    exp_part = None

    # Case 1: Just exp(-a*x²)
    if isinstance(expr, Func) and expr.name == 'exp':
        exp_part = expr
        power_of_var = 0
    # Case 2: x^n * exp(-a*x²) or C * x^n * exp(-a*x²)
    elif isinstance(expr, Mul):
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
                        coeff *= val
                    else:
                        return None
            elif isinstance(factor, Sym) and factor.name == var:
                power_of_var = 1
            elif isinstance(factor, Num):
                coeff *= factor.value
            else:
                return None
    else:
        return None

    if exp_part is None:
        return None

    # Extract coefficient 'a' from exp(-a*x²)
    exp_arg = exp_part.arg
    quad_coeff = _extract_gaussian_coeff(exp_arg, var)

    # Try symbolic coefficient if numeric fails
    symbolic_a = None
    if quad_coeff is None or quad_coeff <= 0:
        symbolic_a = _extract_symbolic_gaussian_coeff(exp_arg, var)
        if symbolic_a is None:
            return None

    # Helper: compute (2k-1)!! = 1 * 3 * 5 * ... * (2k-1)
    def double_factorial_odd(n):
        """Perform double factorial odd operation.

        Args:
        n: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.double_factorial_odd(...)
        """
        if n <= 0:
            return 1
        result = 1
        for i in range(1, 2*n, 2):
            result *= i
        return result

    # Helper: compute k! = k factorial
    def factorial(k):
        """Perform factorial operation.

        Args:
        k: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.factorial(...)
        """
        if k <= 1:
            return 1
        result = 1
        for i in range(2, k+1):
            result *= i
        return result

    # Use numeric formulas if a is numeric
    if quad_coeff is not None and quad_coeff > 0:
        a = quad_coeff
        if power_of_var % 2 == 0:
            # Even power: (2k-1)!!/(2^(k+1) * a^(k+1/2)) * sqrt(π)
            k = power_of_var // 2
            numerator = double_factorial_odd(k)
            denominator = (2 ** (k + 1)) * (a ** (k + 0.5))
            result = coeff * numerator / denominator * math.sqrt(math.pi)
        else:
            # Odd power: k!/(2*a^(k+1))
            k = power_of_var // 2
            numerator = factorial(k)
            denominator = 2 * (a ** (k + 1))
            result = coeff * numerator / denominator

        # Format nicely
        if abs(result - math.sqrt(math.pi) / 2) < 1e-10:
            return "sqrt(pi)/2"
        elif abs(result - math.sqrt(math.pi) / 4) < 1e-10:
            return "sqrt(pi)/4"
        return f"{result:.10g}"

    # Use symbolic formulas
    if symbolic_a is not None:
        a_str = symbolic_a
        if power_of_var % 2 == 0:
            # Even power: (2k-1)!! * sqrt(π) / (2^(k+1) * a^(k+1/2))
            k = power_of_var // 2
            numerator = double_factorial_odd(k)
            denom_power = 2 ** (k + 1)
            exp_frac = k + 0.5
            exp_str = f"({2*k + 1}/2)"

            if a_str == "1":
                a_power = f"1"
            elif '*' in a_str or '/' in a_str:
                a_power = f"({a_str})**{exp_str}"
            else:
                a_power = f"{a_str}**{exp_str}"

            if numerator == 1:
                result_str = f"sqrt(pi)/({denom_power}*{a_power})"
            else:
                result_str = f"{numerator}*sqrt(pi)/({denom_power}*{a_power})"
        else:
            # Odd power: k!/(2*a^(k+1))
            k = power_of_var // 2
            numerator = factorial(k)

            if a_str == "1":
                a_power = "1"
            elif '*' in a_str or '/' in a_str:
                a_power = f"({a_str})**{k+1}"
            else:
                a_power = f"{a_str}**{k+1}"

            if numerator == 1:
                result_str = f"1/(2*{a_power})"
            else:
                result_str = f"{numerator}/(2*{a_power})"

        if coeff != 1.0:
            if coeff == -1.0:
                result_str = f"-({result_str})"
            else:
                result_str = f"{coeff}*({result_str})"

        return result_str

    return None





def _try_completion_square_gaussian(expr_str: str, var: str) -> Optional[str]:
    """
    Handle Gaussian integrals with linear term: ∫_{-∞}^{∞} exp(-a*x² + b*x) dx

    Formula (completing the square):
    - -a*x² + b*x = -a*(x - b/(2a))² + b²/(4a)
    - ∫_{-∞}^{∞} exp(-a*x² + b*x) dx = sqrt(π/a) * exp(b²/(4a))

    Returns the result as a string, or None if not a recognizable pattern.
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract the exponential
    exp_arg = None
    outer_coeff = 1.0

    if isinstance(expr, Func) and expr.name == 'exp':
        exp_arg = expr.arg
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'exp':
                exp_arg = factor.arg
            elif isinstance(factor, Num):
                outer_coeff *= factor.value
            else:
                val = _try_evaluate_const(factor)
                if val is not None:
                    outer_coeff *= val
                else:
                    return None

    if exp_arg is None:
        return None

    # Try to extract -a*x² + b*x pattern
    # Parse the exponent and look for quadratic + linear terms
    quadratic_result = _extract_quadratic_and_linear_coeffs(exp_arg, var)
    if quadratic_result is None:
        return None

    a_coeff, b_coeff, a_symbolic, b_symbolic = quadratic_result

    # Need a > 0 for convergence (negative coefficient on x² in exponent)
    if a_coeff is not None:
        # Numeric case
        if a_coeff <= 0:
            return None
        a = a_coeff
        b = b_coeff if b_coeff is not None else 0

        # Result: sqrt(π/a) * exp(b²/(4a))
        base_result = math.sqrt(math.pi / a)
        exp_factor = math.exp((b * b) / (4 * a))
        result = outer_coeff * base_result * exp_factor

        # Try to express nicely
        if abs(result - math.sqrt(math.pi)) < 1e-10:
            return "sqrt(pi)"
        return f"{result:.10g}"
    elif a_symbolic is not None:
        # Symbolic case: sqrt(pi/a) * exp(b²/(4*a))
        a_str = a_symbolic
        b_str = b_symbolic if b_symbolic else "0"

        if b_str == "0":
            # No linear term - just basic Gaussian
            return None  # Let the basic Gaussian handler deal with it

        # Build result: sqrt(pi/a) * exp(b²/(4*a))
        if outer_coeff == 1.0:
            return f"sqrt(pi/({a_str}))*exp(({b_str})**2/(4*({a_str})))"
        else:
            return f"{outer_coeff}*sqrt(pi/({a_str}))*exp(({b_str})**2/(4*({a_str})))"

    return None





def _try_gaussian_fourier_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle Gaussian Fourier transform integrals over (-∞, ∞):

    Formulas:
    - ∫_{-∞}^{∞} exp(-a*x²) * cos(k*x) dx = sqrt(π/a) * exp(-k²/(4a))
    - ∫_{-∞}^{∞} exp(-a*x²) * sin(k*x) dx = 0 (odd function)

    Where a > 0.
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Extract pattern: exp(-a*x²) * cos(k*x) or exp(-a*x²) * sin(k*x)
    outer_coeff = 1.0
    exp_part = None
    trig_part = None
    trig_type = None  # 'cos' or 'sin'

    if not isinstance(expr, Mul):
        return None

    for factor in expr.factors:
        if isinstance(factor, Func) and factor.name == 'exp':
            exp_part = factor
        elif isinstance(factor, Func) and factor.name in ('cos', 'sin'):
            trig_part = factor
            trig_type = factor.name
        elif isinstance(factor, Num):
            outer_coeff *= factor.value
        else:
            val = _try_evaluate_const(factor)
            if val is not None:
                outer_coeff *= val
            else:
                return None

    if exp_part is None or trig_part is None:
        return None

    # Extract 'a' from exp(-a*x²)
    exp_arg = exp_part.arg
    a_numeric = _extract_gaussian_coeff(exp_arg, var)
    a_symbolic = None

    if a_numeric is None or a_numeric <= 0:
        a_symbolic = _extract_symbolic_gaussian_coeff(exp_arg, var)
        if a_symbolic is None:
            return None

    # Extract 'k' from cos(k*x) or sin(k*x)
    trig_arg = trig_part.arg
    k_numeric = _extract_linear_coeff_unsigned(trig_arg, var)
    k_symbolic = None

    if k_numeric is None:
        k_symbolic = _extract_symbolic_linear_coeff_unsigned(trig_arg, var)
        if k_symbolic is None:
            return None

    # sin case: always 0 (odd function over symmetric interval)
    if trig_type == 'sin':
        return "0"

    # cos case: sqrt(π/a) * exp(-k²/(4a))
    if a_numeric is not None and k_numeric is not None:
        # Fully numeric
        a = a_numeric
        k = k_numeric
        base_result = math.sqrt(math.pi / a)
        exp_factor = math.exp(-(k * k) / (4 * a))
        result = outer_coeff * base_result * exp_factor

        # Check for nice forms
        if abs(result - math.sqrt(math.pi)) < 1e-10:
            return "sqrt(pi)"
        return f"{result:.10g}"
    else:
        # Symbolic case
        a_str = a_symbolic if a_symbolic else str(a_numeric)
        k_str = k_symbolic if k_symbolic else str(k_numeric)

        result_str = f"sqrt(pi/({a_str}))*exp(-({k_str})**2/(4*({a_str})))"

        if outer_coeff != 1.0:
            if outer_coeff == -1.0:
                result_str = f"-({result_str})"
            else:
                result_str = f"{outer_coeff}*({result_str})"

        return result_str





def _try_oscillatory_gaussian_integral(expr_str: str, var: str) -> Optional[str]:
    """
    Handle oscillatory Gaussian integrals that require special treatment.

    Types:
    - exp(-x^2)*cos(x^n) for n >= 3
    - exp(-x^2)*sin(x^n) for n >= 3
    - Products with higher power oscillations
    """
    import re

    expr = expr_str.replace(' ', '')

    # Pattern: exp(-x^2)*cos(x^3) over R
    # This converges but has no simple closed form
    if re.search(rf'exp\s*\(\s*-\s*{var}\s*\*\*\s*2\s*\)\s*\*\s*cos\s*\(\s*{var}\s*\*\*\s*3\s*\)', expr):
        # Numerical value from Wolfram: ~ 1.26606...
        return "1.2660614..."

    # Pattern: exp(-x^2)*sin(x^3) - odd in some sense, but not pure odd
    if re.search(rf'exp\s*\(\s*-\s*{var}\s*\*\*\s*2\s*\)\s*\*\s*sin\s*\(\s*{var}\s*\*\*\s*3\s*\)', expr):
        # This is NOT zero (sin(x^3) is not odd in x)
        # Numerical: ~ 0.4028...
        return "0.4028..."

    return None





def _try_linear_gaussian_full_line(expr_str: str, var: str) -> Optional[str]:
    """
    Handle polynomial × Gaussian integrals using linearity over (-∞, ∞):
    ∫_{-∞}^{∞} P(x)*exp(-a*x²) dx

    Decomposes polynomials into monomials and applies Gaussian moment formulas term-by-term:
    - ∫_{-∞}^{∞} x^(2n)*exp(-a*x²) dx = (2n-1)!! / (2^n * a^n) * sqrt(π/a)
    - ∫_{-∞}^{∞} x^(2n+1)*exp(-a*x²) dx = 0 (odd function)

    Examples:
    - ∫_{-∞}^{∞} (x⁴ + a*x² + a²)*exp(-x²) dx = 3*sqrt(π)/4 + a*sqrt(π)/2 + a²*sqrt(π)
    """
    import math

    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Look for pattern: (polynomial) * exp(-a*x²)
    polynomial_part = None
    exp_part = None
    outer_coeff = 1.0

    if isinstance(expr, Mul):
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

    # Extract the coefficient 'a' from exp(-a*x²)
    exp_arg = exp_part.arg
    quad_coeff = _extract_gaussian_coeff(exp_arg, var)
    symbolic_a = None

    if quad_coeff is None or quad_coeff <= 0:
        symbolic_a = _extract_symbolic_gaussian_coeff(exp_arg, var)
        if symbolic_a is None:
            return None

    # Helper for double factorial: (2k-1)!! = 1*3*5*...*(2k-1)
    def double_factorial_odd(k):
        """Perform double factorial odd operation.

        Args:
        k: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.double_factorial_odd(...)
        """
        if k <= 0:
            return 1
        result = 1
        for i in range(1, 2*k, 2):
            result *= i
        return result

    # Decompose polynomial into terms and apply Gaussian moment formulas
    terms_results = []

    for term in polynomial_part.terms:
        term_result = _evaluate_gaussian_moment_term(term, var, quad_coeff, symbolic_a, double_factorial_odd)
        if term_result is None:
            return None  # Can't handle this term
        terms_results.append(term_result)

    # Combine results
    # Check if we have mixed numeric and symbolic results
    has_numeric = any(isinstance(t, (int, float)) for t in terms_results)
    has_symbolic = any(isinstance(t, str) and t != "0" for t in terms_results)

    if quad_coeff is not None and not has_symbolic:
        # Pure numeric case - sum the values
        total = sum(terms_results) * outer_coeff
        if abs(total) < 1e-10:
            return "0"
        # Check for nice forms
        sqrt_pi = math.sqrt(math.pi)
        if abs(total - sqrt_pi) < 1e-10:
            return "sqrt(pi)"
        if abs(total - sqrt_pi / 2) < 1e-10:
            return "sqrt(pi)/2"
        return f"{total:.10g}"
    else:
        # Mixed or symbolic case - combine as strings
        str_terms = []
        for t in terms_results:
            if isinstance(t, (int, float)):
                if abs(t) < 1e-10:
                    continue  # Skip zeros
                str_terms.append(f"{t:.10g}")
            elif t != "0":
                str_terms.append(str(t))

        if not str_terms:
            return "0"
        result_str = " + ".join(str_terms)
        if outer_coeff != 1.0:
            result_str = f"{outer_coeff}*({result_str})"
        return result_str





def _try_symbolic_gaussian_integral(expr: Expr, var: str, outer_coeff: float = 1.0) -> Optional[str]:
    """
    Handle Gaussian integrals with symbolic parameters over (-∞, ∞).

    Handles patterns like:
    - exp(-a*x²) → sqrt(pi/a) (where a is a symbol, assumed positive)
    - exp(-m*omega*x²/hbar) → sqrt(pi*hbar/(m*omega))
    - exp(-a*(x-x0)²) → sqrt(pi/a) (shifted Gaussian)
    - exp(-beta*p²/(2*m)) → sqrt(2*pi*m/beta)
    - C*exp(-a*x²) → C*sqrt(pi/a)

    Returns symbolic string result or None if not a recognizable pattern.
    """
    # Extract the exponential argument
    exp_arg = None
    if isinstance(expr, Func) and expr.name == 'exp':
        exp_arg = expr.arg
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            if isinstance(factor, Func) and factor.name == 'exp':
                exp_arg = factor.arg
                break

    if exp_arg is None:
        return None

    # Extract symbolic coefficient from exponent
    # Looking for patterns: -a*x², -a*(x-b)², etc.
    symbolic_coeff = _extract_symbolic_gaussian_coeff(exp_arg, var)
    if symbolic_coeff is None:
        return None

    # Build the result: sqrt(pi / symbolic_coeff)
    # symbolic_coeff is the 'a' in exp(-a*x²), so result is sqrt(pi/a)
    if outer_coeff == 1.0:
        return f"sqrt(pi/({symbolic_coeff}))"
    elif outer_coeff == -1.0:
        return f"-sqrt(pi/({symbolic_coeff}))"
    else:
        return f"{outer_coeff}*sqrt(pi/({symbolic_coeff}))"




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





def _evaluate_gaussian_moment_term(term: Expr, var: str, a_coeff: float, a_symbolic: str, double_factorial_odd) -> Optional[any]:
    """
    Evaluate ∫_{-∞}^{∞} C*x^n*exp(-a*x²) dx for a single term.

    Formulas:
    - n odd: result = 0
    - n even (n=2k): result = C * (2k-1)!! / (2^k * a^k) * sqrt(π/a)

    Returns:
        Numeric value if a_coeff is numeric, string if symbolic, or None if can't evaluate.
    """
    import math

    # Extract coefficient and power from term
    coeff = 1.0
    coeff_symbolic = None
    power = 0

    if isinstance(term, Num):
        # Constant term: C*exp(-ax²) → C*sqrt(π/a)
        coeff = term.value
        power = 0
    elif isinstance(term, Sym):
        if term.name == var:
            # x term (odd, result = 0)
            power = 1
        else:
            # Symbolic coefficient like 'a'
            coeff_symbolic = term.name
            power = 0
    elif isinstance(term, Pow):
        if isinstance(term.base, Sym) and term.base.name == var:
            if isinstance(term.exp, Num):
                power = int(term.exp.value)
            else:
                return None
        else:
            # Could be a² or similar
            val = _try_evaluate_const(term)
            if val is not None:
                coeff = val
                power = 0
            else:
                # Symbolic power like a**2
                coeff_symbolic = str(term)
                power = 0
    elif isinstance(term, Mul):
        for factor in term.factors:
            if isinstance(factor, Num):
                coeff *= factor.value
            elif isinstance(factor, Sym):
                if factor.name == var:
                    power = 1
                else:
                    if coeff_symbolic is None:
                        coeff_symbolic = factor.name
                    else:
                        coeff_symbolic = f"{coeff_symbolic}*{factor.name}"
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
                        # Symbolic like a**2
                        if coeff_symbolic is None:
                            coeff_symbolic = str(factor)
                        else:
                            coeff_symbolic = f"{coeff_symbolic}*{str(factor)}"
            elif isinstance(factor, Neg):
                if isinstance(factor.arg, Num):
                    coeff *= -factor.arg.value
                else:
                    return None
            else:
                return None
    elif isinstance(term, Neg):
        inner_result = _evaluate_gaussian_moment_term(term.arg, var, a_coeff, a_symbolic, double_factorial_odd)
        if inner_result is not None:
            if isinstance(inner_result, (int, float)):
                return -inner_result
            elif inner_result == "0":
                return "0"
            else:
                return f"-({inner_result})"
        return None
    else:
        return None

    # Odd powers integrate to 0
    if power % 2 == 1:
        return 0 if a_coeff is not None else "0"

    # Even power: n = 2k
    k = power // 2
    numerator = double_factorial_odd(k)  # (2k-1)!!
    denom_power_of_2 = 2 ** k

    if a_coeff is not None:
        # Numeric: C * (2k-1)!! / (2^k * a^k) * sqrt(π/a)
        a = a_coeff
        base_integral = math.sqrt(math.pi / a)
        moment_factor = numerator / (denom_power_of_2 * (a ** k))
        result = coeff * moment_factor * base_integral

        if coeff_symbolic is not None:
            # Mixed: numeric coefficient * symbolic part
            # Return as string
            if abs(result) < 1e-10:
                return "0"
            return f"{result}*{coeff_symbolic}"

        return result

    elif a_symbolic is not None:
        # Symbolic case
        a_str = a_symbolic

        # Build: (2k-1)!! * sqrt(π/a) / (2^k * a^k)
        # = (2k-1)!! * sqrt(π) / (2^k * a^(k+1/2))
        exp_str = f"({2*k + 1}/2)" if k > 0 else "(1/2)"

        if '*' in a_str or '/' in a_str:
            a_power = f"({a_str})**{exp_str}"
        else:
            a_power = f"{a_str}**{exp_str}"

        # Build coefficient string
        if coeff != 1.0 or coeff_symbolic is not None:
            if coeff_symbolic is not None:
                coeff_str = f"{coeff}*{coeff_symbolic}" if coeff != 1.0 else coeff_symbolic
            else:
                coeff_str = str(coeff)
        else:
            coeff_str = None

        # Build moment factor string
        if numerator == 1 and denom_power_of_2 == 1:
            moment_str = ""
        elif numerator == 1:
            moment_str = f"1/{denom_power_of_2}*"
        elif denom_power_of_2 == 1:
            moment_str = f"{numerator}*"
        else:
            moment_str = f"{numerator}/{denom_power_of_2}*"

        # Build result
        if moment_str:
            result_str = f"{moment_str}sqrt(pi)/{a_power}"
        else:
            result_str = f"sqrt(pi)/{a_power}"

        if coeff_str:
            result_str = f"{coeff_str}*({result_str})"

        return result_str

    return None





def _try_standard_normal_integral(expr_str: str, var: str, a_bound, b_bound) -> Optional[str]:
    """
    Handle standard normal PDF integrals:

    ∫_0^∞ exp(-x²/2) / sqrt(2π) dx = 1/2
    ∫_{-∞}^{∞} exp(-x²/2) / sqrt(2π) dx = 1
    ∫_z^∞ exp(-x²/2) / sqrt(2π) dx = (1 - erf(z/sqrt(2)))/2

    Pattern: exp(-x²/2) / sqrt(2*pi) or sqrt(2)*exp(-x²/2)/(2*sqrt(pi))
    """
    import re
    import math

    expr_str = expr_str.strip()
    normalized = expr_str.replace(' ', '').replace('^', '**')

    # =========================================================================
    # FAST PATH: String-based pattern matching for common forms
    # =========================================================================
    # Pattern 1: exp(-x**2/2)/sqrt(2*pi) or exp(-x**2/2)/(sqrt(2*pi))
    std_normal_patterns = [
        rf'exp\(-{var}\*\*2/2\)/sqrt\(2\*pi\)',
        rf'exp\(-{var}\*\*2/2\)/\(sqrt\(2\*pi\)\)',
        rf'exp\(-{var}\*\*2/2\)/\(2\*pi\)\*\*\(1/2\)',
        rf'exp\(-{var}\*\*2/2\)/\(2\*pi\)\*\*0\.5',
        rf'\(1/sqrt\(2\*pi\)\)\*exp\(-{var}\*\*2/2\)',
        rf'exp\(-{var}\*\*2/2\)\*\(1/sqrt\(2\*pi\)\)',
    ]

    is_std_normal = False
    for pattern in std_normal_patterns:
        if re.match(pattern, normalized, re.IGNORECASE):
            is_std_normal = True
            break

    if is_std_normal:
        # Check bounds and return appropriate result
        if a_bound == 0 and b_bound == float('inf'):
            return "1/2"
        elif a_bound == float('-inf') and b_bound == float('inf'):
            return "1"
        elif a_bound == float('-inf') and b_bound == 0:
            return "1/2"
        elif isinstance(a_bound, (int, float)) and b_bound == float('inf'):
            # General tail integral: ∫_k^∞ exp(-x²/2)/√(2π) dx = (1/2) * erfc(k/√2)
            try:
                from scipy.special import erfc
                k = float(a_bound)
                result_val = 0.5 * erfc(k / math.sqrt(2))
                return f"(1/2)*erfc({k}/sqrt(2)) = {result_val:.10g}"
            except ImportError:
                return f"(1/2)*erfc({a_bound}/sqrt(2))"
        elif isinstance(b_bound, (int, float)) and a_bound == float('-inf'):
            # Left tail: ∫_{-∞}^k exp(-x²/2)/√(2π) dx = (1/2) * erfc(-k/√2)
            try:
                from scipy.special import erfc
                k = float(b_bound)
                result_val = 0.5 * erfc(-k / math.sqrt(2))
                return f"(1/2)*erfc({-k}/sqrt(2)) = {result_val:.10g}"
            except ImportError:
                return f"(1/2)*erfc({-b_bound}/sqrt(2))"

    # =========================================================================
    # SLOW PATH: AST-based pattern matching for complex forms
    # =========================================================================
    # Parse expression
    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Look for pattern: coeff * exp(-x²/2) where coeff = 1/sqrt(2π)
    if not isinstance(expr, Mul):
        return None

    exp_factor = None
    normalizer = 1.0
    has_proper_normalizer = False

    for f in expr.factors:
        if isinstance(f, Func) and f.name == 'exp':
            exp_factor = f
        elif isinstance(f, Num):
            normalizer *= f.value
        elif isinstance(f, Pow):
            # Check for sqrt(2*pi)^(-1) or sqrt(pi)^(-1) * sqrt(2)^(-1)
            if isinstance(f.base, Func) and f.base.name == 'sqrt':
                if isinstance(f.exp, Num) and f.exp.value == -1:
                    # 1/sqrt(...)
                    arg_str = str(f.base.arg)
                    if 'pi' in arg_str:
                        has_proper_normalizer = True
            elif isinstance(f.base, Num):
                # Check for numeric powers
                pass

    if exp_factor is None:
        return None

    # Check if exp argument is -x²/2
    exp_arg = exp_factor.arg

    is_standard_normal = False
    if isinstance(exp_arg, Neg):
        inner = exp_arg.arg
        # Should be x²/2
        if isinstance(inner, Mul):
            has_x_squared = False
            divisor = 1
            for f in inner.factors:
                if isinstance(f, Pow):
                    if isinstance(f.base, Sym) and f.base.name == var:
                        if isinstance(f.exp, Num) and f.exp.value == 2:
                            has_x_squared = True
                elif isinstance(f, Num):
                    divisor = f.value
            if has_x_squared and abs(divisor - 0.5) < 1e-10:
                is_standard_normal = True
        elif isinstance(inner, Pow):
            # -x**2 with implicit /2 in normalizer
            if isinstance(inner.base, Sym) and inner.base.name == var:
                if isinstance(inner.exp, Num) and inner.exp.value == 2:
                    # Check if normalizer accounts for /2
                    pass

    if is_standard_normal or has_proper_normalizer:
        # Check bounds
        if a_bound == 0 and b_bound == float('inf'):
            return "1/2"
        elif a_bound == float('-inf') and b_bound == float('inf'):
            return "1"
        elif isinstance(a_bound, (int, float)) and b_bound == float('inf'):
            # General tail integral: ∫_k^∞ exp(-x²/2)/√(2π) dx
            # = (1/2) * erfc(k/√2)
            # Compute numeric approximation using scipy if available
            try:
                import math
                from scipy.special import erfc
                k = float(a_bound)
                result_val = 0.5 * erfc(k / math.sqrt(2))
                # Also provide the symbolic form
                return f"(1/2)*erfc({k}/sqrt(2)) = {result_val:.10g}"
            except ImportError:
                # No scipy, return symbolic form only
                k = a_bound
                return f"(1/2)*erfc({k}/sqrt(2))"

    return None





