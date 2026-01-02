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
Gaussian 2D
===========

2D Gaussian integral evaluation functions.
"""

import logging
import math
import re
from typing import Optional, Tuple, Dict, Any, Union
from ..ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from ..differentiation_specialist import DifferentiationEngine
from ..expression_parser import ExprParser
from ..validation import check_expression_safety as _check_expression_safety
from ..calculus_utils import _evaluate_at_numeric as _evaluate_at
from ..calculus_utils import _get_symbols, _evaluate_expr_numerically
from ..definite_integration import definite_integrate

logger = logging.getLogger(__name__)

# Module-level parser instance
_parser = ExprParser()

def _try_2d_gaussian_integral(expr_str: str, var1: str, var2: str,
                               a1: float, b1: float, a2: float, b2: float) -> Optional[str]:
    """
    Try to evaluate 2D Gaussian integrals analytically.

    Handles separable 2D Gaussians over R² (full real plane):
    - ∫∫ exp(-x² - y²)/(2π) dx dy = 1 (joint standard normal)
    - ∫∫ exp(-x² - y²) dx dy = π
    - ∫∫ exp(-a*x² - b*y²) dx dy = π/sqrt(a*b)

    Args:
        expr_str: Expression string
        var1, var2: Integration variables (e.g., 'x', 'y')
        a1, b1: Bounds for var1
        a2, b2: Bounds for var2

    Returns:
        Result string if recognized, None otherwise
    """
    import math
    import re

    # Only handle full R² integrals for now
    if not (a1 == float('-inf') and b1 == float('inf') and
            a2 == float('-inf') and b2 == float('inf')):
        return None

    # Normalize expression
    expr_norm = expr_str.replace(' ', '').replace('**', '^')

    # Pattern 1: exp(-x² - y²)/(2*pi) = 1 (2D standard normal PDF)
    # This is the joint PDF of two independent N(0,1) variables
    patterns_2d_normal = [
        # exp(-x^2 - y^2)/(2*pi)
        rf'exp\(-{var1}\^2-{var2}\^2\)/\(2\*pi\)',
        rf'exp\(-{var2}\^2-{var1}\^2\)/\(2\*pi\)',
        rf'exp\(-\({var1}\^2\+{var2}\^2\)\)/\(2\*pi\)',
        # (1/(2*pi))*exp(-x^2 - y^2)
        rf'\(1/\(2\*pi\)\)\*exp\(-{var1}\^2-{var2}\^2\)',
        rf'\(1/\(2\*pi\)\)\*exp\(-{var2}\^2-{var1}\^2\)',
        # exp(-(x^2 + y^2)/2)/(2*pi) - alternate form
        rf'exp\(-\({var1}\^2\+{var2}\^2\)/2\)/\(2\*pi\)',
    ]

    for pattern in patterns_2d_normal:
        if re.search(pattern, expr_norm, re.IGNORECASE):
            return "1"

    # Pattern 2: exp(-x² - y²) = π (unnormalized 2D Gaussian)
    patterns_unnorm = [
        rf'^exp\(-{var1}\^2-{var2}\^2\)$',
        rf'^exp\(-{var2}\^2-{var1}\^2\)$',
        rf'^exp\(-\({var1}\^2\+{var2}\^2\)\)$',
    ]

    for pattern in patterns_unnorm:
        if re.match(pattern, expr_norm, re.IGNORECASE):
            return "pi"

    # Pattern 3: exp(-a*x² - b*y²) = π/sqrt(a*b) with numeric coefficients
    # Match exp(-coef1*var1^2 - coef2*var2^2)
    general_pattern = rf'exp\(-(\d+(?:\.\d+)?)\*?{var1}\^2-(\d+(?:\.\d+)?)\*?{var2}\^2\)'
    match = re.match(general_pattern, expr_norm, re.IGNORECASE)
    if match:
        a_coef = float(match.group(1))
        b_coef = float(match.group(2))
        result = math.pi / math.sqrt(a_coef * b_coef)
        # Return symbolic form if it simplifies nicely
        if abs(a_coef - 1) < 1e-10 and abs(b_coef - 1) < 1e-10:
            return "pi"
        return f"pi/sqrt({a_coef}*{b_coef}) = {result:.10g}"

    # Pattern 4: exp(-x²/2 - y²/2)/(2*pi) = 1 (standard normal in standard form)
    patterns_standard_form = [
        rf'exp\(-{var1}\^2/2-{var2}\^2/2\)/\(2\*pi\)',
        rf'exp\(-\({var1}\^2\+{var2}\^2\)/2\)/\(2\*pi\)',
    ]

    for pattern in patterns_standard_form:
        if re.search(pattern, expr_norm, re.IGNORECASE):
            return "1"

    return None




def definite_integrate_2d(expr_str: str, var1: str, a1, b1,
                          var2: str, a2, b2) -> Tuple[bool, Optional[str], str]:
    """
    Compute double integral over rectangular region.

    ∫∫ f(x,y) dx dy over [a1,b1] × [a2,b2]

    For separable integrands f(x,y) = g(x)*h(y), computes:
        (∫ g(x) dx from a1 to b1) * (∫ h(y) dy from a2 to b2)

    Args:
        expr_str: Expression in both variables
        var1: First integration variable (inner)
        a1, b1: Bounds for var1
        var2: Second integration variable (outer)
        a2, b2: Bounds for var2

    Returns:
        (success, result_string, method)
    """
    import math

    # Normalize bounds
    def normalize_bound(bound):
        """Perform normalize bound operation.

        Args:
        bound: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.normalize_bound(...)
        """
        if bound is None:
            return None
        if isinstance(bound, (int, float)):
            return float(bound)
        if isinstance(bound, str):
            bound_lower = bound.lower().strip()
            if bound_lower in ('inf', 'oo', '+inf', '+oo', 'infinity'):
                return float('inf')
            elif bound_lower in ('-inf', '-oo', '-infinity'):
                return float('-inf')
            try:
                return float(bound)
            except ValueError:
                return bound
        return float(bound)

    a1_norm = normalize_bound(a1)
    b1_norm = normalize_bound(b1)
    a2_norm = normalize_bound(a2)
    b2_norm = normalize_bound(b2)

    # Try special 2D Gaussian patterns first
    gaussian_2d = _try_2d_gaussian_integral(expr_str, var1, var2,
                                             a1_norm, b1_norm, a2_norm, b2_norm)
    if gaussian_2d is not None:
        return True, gaussian_2d, "native_calculus_2d_gaussian"

    # Try separable integration: if f(x,y) = g(x)*h(y), integrate separately
    separable_result = _try_separable_2d_integral(expr_str, var1, a1_norm, b1_norm,
                                                   var2, a2_norm, b2_norm)
    if separable_result is not None:
        return True, separable_result, "native_calculus_2d_separable"

    # Fallback to iterated integration
    # First integrate with respect to var1, then var2
    success1, result1, method1 = definite_integrate(expr_str, var1, a1, b1)
    if not success1 or result1 is None:
        return False, None, f"inner_integral_failed: {method1}"

    # The result from inner integral may still contain var2
    # Now integrate with respect to var2
    success2, result2, method2 = definite_integrate(result1, var2, a2, b2)
    if not success2 or result2 is None:
        return False, None, f"outer_integral_failed: {method2}"

    return True, result2, "native_calculus_2d_iterated"




def _try_separable_2d_integral(expr_str: str, var1: str, a1: float, b1: float,
                                var2: str, a2: float, b2: float) -> Optional[str]:
    """
    Check if 2D integrand is separable: f(x,y) = g(x) * h(y).

    If separable, compute ∫g(x)dx * ∫h(y)dy.

    Returns:
        Product of 1D integrals if separable, None otherwise
    """
    import re
    import math

    # Parse into factors
    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    # Collect symbols in expression
    symbols = _get_symbols(expr)

    # Check if expression involves both variables
    if var1 not in symbols and var2 not in symbols:
        # Constant in both - just multiply by areas
        try:
            const = float(_evaluate_expr_numerically(expr_str))
            if math.isinf(a1) or math.isinf(b1) or math.isinf(a2) or math.isinf(b2):
                if const == 0:
                    return "0"
                return None  # Can't integrate constant over infinite domain
            area = (b1 - a1) * (b2 - a2)
            return str(const * area)
        except:
            return None

    # Try to factor expression into var1-only and var2-only parts
    # This is a simplified check - look for product structure
    if isinstance(expr, Mul):
        factors_var1 = []
        factors_var2 = []
        factors_const = []

        for factor in expr.factors:
            factor_symbols = _get_symbols(factor)
            if var1 in factor_symbols and var2 in factor_symbols:
                # Factor contains both variables - not separable
                return None
            elif var1 in factor_symbols:
                factors_var1.append(factor)
            elif var2 in factor_symbols:
                factors_var2.append(factor)
            else:
                factors_const.append(factor)

        if factors_var1 and factors_var2:
            # We have a separable form!
            # Reconstruct expressions for each variable
            expr1_str = str(mul(*factors_var1)) if len(factors_var1) > 1 else str(factors_var1[0])
            expr2_str = str(mul(*factors_var2)) if len(factors_var2) > 1 else str(factors_var2[0])
            const_str = str(mul(*factors_const)) if factors_const else "1"

            # Integrate each part
            success1, result1, _ = definite_integrate(expr1_str, var1, a1, b1)
            if not success1 or result1 is None:
                return None

            success2, result2, _ = definite_integrate(expr2_str, var2, a2, b2)
            if not success2 or result2 is None:
                return None

            # Multiply results
            try:
                val1 = float(result1) if result1.replace('.', '').replace('-', '').isdigit() else None
                val2 = float(result2) if result2.replace('.', '').replace('-', '').isdigit() else None
                const_val = float(const_str) if const_str.replace('.', '').replace('-', '').isdigit() else 1

                if val1 is not None and val2 is not None:
                    final = const_val * val1 * val2
                    return str(final)
                else:
                    # Return symbolic product
                    return f"({const_str})*({result1})*({result2})"
            except:
                return f"({const_str})*({result1})*({result2})"

    return None




