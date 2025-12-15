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
Singularity Analysis
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
from .extraction_utils import _evaluate_at_numeric, _get_symbols

logger = logging.getLogger(__name__)

# Module-level instances
_parser = ExprParser()
_int_engine = IntegrationEngine()


def _check_log_singularity(expr_str: str, var: str, a_norm, b_norm) -> Optional[str]:
    """
    Detect logarithmic singularities that cause numerical instability.

    Cases like ∫_0^1 e^{-x}/x dx have a log singularity at x=0.
    Instead of returning bad numerics, we return a clear status.

    Returns:
        Warning string if log singularity detected, None otherwise
    """
    import re

    # Only check for singularity at lower bound = 0
    if a_norm != 0:
        return None

    # Normalize expression for pattern matching
    expr_normalized = expr_str.strip().replace(' ', '')

    # Check for 1/x or x^(-1) factor without log compensation
    singular_patterns = [
        rf'/{var}(?!\*|\d)',  # /x not followed by * or digit (simple 1/x)
        rf'{var}\*\*\(-1\)',  # x**(-1)
        rf'{var}\*\*-1(?!\d)',  # x**-1 (without parens)
        rf'1/{var}(?!\*|\d)',  # 1/x
        rf'\({var}\)\*\*\(-1\)',  # (x)**(-1)
    ]

    has_singularity = any(re.search(p, expr_normalized) for p in singular_patterns)

    if not has_singularity:
        return None

    # Check if there's a compensating factor that makes it integrable
    # e.g., x * (1/x) = 1 is fine
    # But exp(-x)/x has a true log singularity

    # Patterns that indicate true log singularity (not removable)
    bad_patterns = [
        rf'exp\([^)]*\)/{var}',  # exp(...)/x
        rf'exp\([^)]*\)\*{var}\*\*\(-1\)',  # exp(...)*x^(-1)
        rf'exp\([^)]*\)\*{var}\*\*-1',  # exp(...)*x**-1
        rf'sin\([^)]*\)/{var}',  # sin(...)/x at x=0
        rf'cos\([^)]*\)/{var}',  # cos(...)/x at x=0
        rf'/{var}\*\*\d+(?!\d)',  # 1/x^n where n >= 1
        rf'1/{var}\*\*\d+',  # 1/x**n
    ]

    for pattern in bad_patterns:
        if re.search(pattern, expr_normalized):
            return f"logarithmic singularity at {var}=0 - numeric evaluation unstable"

    # Check for pure 1/x form (which diverges logarithmically as ∫ 1/x = ln(x))
    pure_inverse_patterns = [
        rf'^1/{var}$',  # exactly "1/x"
        rf'^{var}\*\*\(-1\)$',  # exactly "x**(-1)"
        rf'^{var}\*\*-1$',  # exactly "x**-1"
    ]
    for pattern in pure_inverse_patterns:
        if re.match(pattern, expr_normalized):
            return f"logarithmic singularity at {var}=0 - integral diverges (ln({var}) -> -inf)"

    # If we have singularity but no specific bad pattern matched,
    # still warn about potential instability for safety
    return f"potential singularity at {var}=0 - numeric evaluation may be unstable"





def _check_pole_singularity(expr_str: str, var: str, a_norm, b_norm) -> Optional[str]:
    """
    Detect pole singularities inside the integration interval.

    Cases like:
        - 1/(1-x²) over [-1,1] has poles at x=±1 (endpoints)
        - 1/(x²-1) over [0,2] has pole at x=1 (interior)
        - 1/(x*(1+x²)) over [-1,1] has pole at x=0 (interior)

    Returns:
        Warning string if pole singularity detected, None otherwise
    """
    import re
    import math

    if a_norm is None or b_norm is None:
        return None

    # Try to ensure numeric bounds
    try:
        a_val = float(a_norm) if not isinstance(a_norm, str) else None
        b_val = float(b_norm) if not isinstance(b_norm, str) else None
    except:
        return None

    if a_val is None or b_val is None:
        return None

    # Common pole patterns and their singularity locations
    pole_patterns = [
        # 1/(1 - x²) -> poles at x = ±1
        (r'1/\(1-{var}\*\*2\)', [1.0, -1.0]),
        (r'1/\(1-{var}\^2\)', [1.0, -1.0]),
        # 1/(x² - 1) -> poles at x = ±1
        (r'1/\({var}\*\*2-1\)', [1.0, -1.0]),
        (r'1/\({var}\^2-1\)', [1.0, -1.0]),
        # 1/(x² - a²) form
        (r'1/\({var}\*\*2-(\d+)\)', 'quadratic'),
        # 1/(x) -> pole at x = 0
        (r'1/{var}(?!\*|\d|\.)', [0.0]),
        # 1/(x - a) form
        (r'1/\({var}-(\d+(?:\.\d+)?)\)', 'linear'),
        # 1/(a - x) form
        (r'1/\((\d+(?:\.\d+)?)-{var}\)', 'linear_inv'),
        # x/(x² - 1) type
        (r'{var}/\({var}\*\*2-1\)', [1.0, -1.0]),
        # 1/((x-a)(x-b)) type via 1/(x² + bx + c)
        (r'1/\({var}\*\*2[+-]\d*\*?{var}[+-]\d+\)', 'general_quadratic'),
    ]

    poles_in_interval = []
    poles_at_endpoints = []

    for pattern_template, pole_info in pole_patterns:
        pattern = pattern_template.replace('{var}', var)
        match = re.search(pattern, expr_str.replace(' ', ''))

        if match:
            if isinstance(pole_info, list):
                # Fixed poles
                poles = pole_info
            elif pole_info == 'linear':
                # Pole at x = number
                try:
                    poles = [float(match.group(1))]
                except:
                    continue
            elif pole_info == 'linear_inv':
                # Pole at x = number (from a - x form)
                try:
                    poles = [float(match.group(1))]
                except:
                    continue
            elif pole_info == 'quadratic':
                # 1/(x² - c) has poles at ±sqrt(c)
                try:
                    c = float(match.group(1))
                    if c > 0:
                        poles = [math.sqrt(c), -math.sqrt(c)]
                    else:
                        continue
                except:
                    continue
            else:
                continue

            # Check each pole
            for pole in poles:
                # Is it strictly inside?
                if a_val < pole < b_val:
                    poles_in_interval.append(pole)
                # Is it at an endpoint?
                elif abs(pole - a_val) < 1e-10 or abs(pole - b_val) < 1e-10:
                    poles_at_endpoints.append(pole)

    # Report findings
    if poles_in_interval:
        points = ', '.join(f'{var}={p}' for p in sorted(set(poles_in_interval)))
        return f"divergent (interior pole singularities at {points})"

    if poles_at_endpoints:
        points = ', '.join(f'{var}={p}' for p in sorted(set(poles_at_endpoints)))
        return f"improper integral (endpoint singularities at {points}) - may diverge"

    return None





def _check_log_power_integral(expr_str: str, var: str, a_norm, b_norm) -> Optional[str]:
    """
    Classify log-power integrals: int_0^1 x^(-p) * (log x)^m dx.

    Rule: Converges iff p < 1 (independent of m).

    Returns:
        Classification string if pattern matches, None otherwise
    """
    import re
    import math

    if a_norm is None or b_norm is None:
        return None

    try:
        a_val = float(a_norm)
        b_val = float(b_norm)
    except:
        return None

    # Only apply for [0, 1] integrals
    if not (abs(a_val) < 1e-10 and abs(b_val - 1) < 1e-10):
        return None

    normalized = expr_str.replace(' ', '')

    # Pattern: (log(x))^m / x^p or x^(-p) * log(x)^m
    # Also handles: log(x)^m / x (p=1 implicit), (log(x))^m / x, log(x) / x
    patterns = [
        # (log(x))^m / x^p - with outer parens and explicit power
        (rf'\((?:log|ln)\({var}\)\)\*\*(\d+)/{var}\*\*(\d+(?:\.\d+)?)', 'both'),
        # (log(x))^m / x - with outer parens, p=1 implicit
        (rf'\((?:log|ln)\({var}\)\)\*\*(\d+)/{var}(?!\*)', 'log_only'),
        # log(x)^m / x^p - without outer parens, explicit power
        (rf'(?:log|ln)\({var}\)\*\*(\d+)/{var}\*\*(\d+(?:\.\d+)?)', 'both'),
        # log(x)^m / x - without outer parens, p=1 implicit
        (rf'(?:log|ln)\({var}\)\*\*(\d+)/{var}(?!\*)', 'log_only'),
        # log(x) / x^p - no log power (m=1)
        (rf'(?:log|ln)\({var}\)/{var}\*\*(\d+(?:\.\d+)?)', 'x_only'),
        # log(x) / x - both powers implicit (m=1, p=1)
        (rf'(?:log|ln)\({var}\)/{var}(?!\*)', 'none'),
        # x^(-p) * log(x)^m
        (rf'{var}\*\*-(\d+(?:\.\d+)?)\*(?:log|ln)\({var}\)(?:\*\*(\d+))?', 'both'),
        # x^(-p) * (log(x))^m
        (rf'{var}\*\*-(\d+(?:\.\d+)?)\*\((?:log|ln)\({var}\)\)(?:\*\*(\d+))?', 'both'),
    ]

    for pattern, group_type in patterns:
        match = re.search(pattern, normalized)
        if match:
            groups = match.groups()
            # Determine p based on pattern type
            if group_type == 'none':
                p = 1.0  # log(x)/x case
            elif group_type == 'log_only':
                p = 1.0  # log(x)^m/x case
            elif group_type == 'x_only':
                p = float(groups[0])  # log(x)/x^p case
            else:  # 'both'
                # Find the x power (last numeric group typically)
                for g in reversed(groups):
                    if g and g.replace('.', '').isdigit():
                        p = float(g)
                        break
                else:
                    p = 1.0

            if p >= 1:
                return f"divergent (log-power singularity: x^(-{p}) diverges at 0 for p >= 1)"
            else:
                return f"convergent (log-power integral: p={p} < 1)"

    return None





def _analyze_singularities(expr: Expr, var: str, a: float, b: float) -> Dict[str, Any]:
    """
    Comprehensive singularity analysis for an expression over an interval.

    Returns:
        Dictionary with:
        - 'interior': list of singularities strictly inside (a, b)
        - 'endpoints': list of singularities at a or b
        - 'type': 'none', 'interior', 'endpoint', or 'both'
        - 'message': Human-readable description
    """
    import math

    # Ensure a < b
    if a > b:
        a, b = b, a

    result = {
        'interior': [],
        'endpoints': [],
        'type': 'none',
        'message': ''
    }

    # Check for singularities by looking at the expression structure
    singularities = _find_potential_singularities(expr, var)

    for sing in singularities:
        is_singularity = False

        # First, try to evaluate at the exact singularity point
        try:
            at_sing = _evaluate_at(expr, var, sing)
            if at_sing is None or math.isinf(at_sing) or math.isnan(at_sing):
                is_singularity = True
        except:
            is_singularity = True

        # Also verify by checking values nearby
        if not is_singularity:
            try:
                eps = 1e-10
                left = _evaluate_at(expr, var, sing - eps)
                right = _evaluate_at(expr, var, sing + eps)
                if left is None or right is None:
                    is_singularity = True
                elif math.isinf(left) or math.isinf(right):
                    is_singularity = True
                elif abs(left) >= 1e9 or abs(right) >= 1e9:
                    is_singularity = True
            except:
                is_singularity = True

        if is_singularity:
            # Classify as interior or endpoint
            if a < sing < b:
                result['interior'].append(sing)
            elif abs(sing - a) < 1e-10 or abs(sing - b) < 1e-10:
                result['endpoints'].append(sing)

    # Determine overall type
    if result['interior'] and result['endpoints']:
        result['type'] = 'both'
    elif result['interior']:
        result['type'] = 'interior'
    elif result['endpoints']:
        result['type'] = 'endpoint'
    else:
        result['type'] = 'none'

    # Build message
    if result['type'] == 'none':
        result['message'] = 'no singularities'
    elif result['type'] == 'interior':
        points = ', '.join(f'{var}={s}' for s in result['interior'])
        result['message'] = f"divergent (interior singularities at {points})"
    elif result['type'] == 'endpoint':
        points = ', '.join(f'{var}={s}' for s in result['endpoints'])
        result['message'] = f"improper integral (endpoint singularities at {points})"
    else:
        int_points = ', '.join(f'{var}={s}' for s in result['interior'])
        end_points = ', '.join(f'{var}={s}' for s in result['endpoints'])
        result['message'] = f"divergent (interior: {int_points}; endpoints: {end_points})"

    return result





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





def _evaluate_limit(expr: Expr, var: str, limit_point: float, from_inside: str = None) -> Optional[float]:
    """
    Evaluate limit of expression as variable approaches a point.

    Uses numerical approximation at values approaching the point combined with
    algebraic understanding of common limit patterns.

    Args:
        expr: Expression to evaluate limit of
        var: Variable name
        limit_point: The limit point (can be finite or infinity)
        from_inside: Direction to approach from for finite limits
                     '+' (from right), '-' (from left), or None (try direct first)

    Returns:
        Limit value if computable (including +/-inf for divergence), None otherwise
    """
    import math

    if not math.isinf(limit_point):
        # For finite limits, first try direct evaluation
        direct_result = _evaluate_at(expr, var, limit_point)
        if direct_result is not None and math.isfinite(direct_result):
            return direct_result

        # Direct evaluation failed - try approaching the point
        # This handles endpoint singularities like atanh(x) at x=1
        epsilon_values = [0.1, 0.01, 0.001, 0.0001, 0.00001]

        # Determine approach direction
        if from_inside == '+':
            test_points = [limit_point + eps for eps in epsilon_values]
        elif from_inside == '-':
            test_points = [limit_point - eps for eps in epsilon_values]
        else:
            # Try from right first (common for singularities at interval endpoints)
            test_points = [limit_point - eps for eps in epsilon_values]

        results = []
        for pt in test_points:
            try:
                result = _evaluate_at(expr, var, pt)
                if result is not None and not math.isnan(result):
                    results.append(result)
            except:
                pass

        if len(results) >= 3:
            # Check if values are diverging (growing unboundedly)
            if all(abs(results[i+1]) > abs(results[i]) * 1.5 for i in range(len(results)-1) if abs(results[i]) > 1e-10):
                # Divergent - return appropriate infinity
                return float('inf') if results[-1] > 0 else float('-inf')

            # Check if growing but more slowly (logarithmic singularities)
            if all(abs(results[i+1]) > abs(results[i]) for i in range(len(results)-1)):
                if abs(results[-1]) > 100 or abs(results[-1]) > 10 * abs(results[0]):
                    return float('inf') if results[-1] > 0 else float('-inf')

            # Check if converging to finite value
            if max(abs(results[-1] - results[-2]), abs(results[-2] - results[-3])) < 0.01:
                return results[-1]

        return None

    # For limits at infinity, use numerical approximation with multiple large values
    # to detect convergence
    sign = 1 if limit_point > 0 else -1
    test_values = [100 * sign, 1000 * sign, 10000 * sign, 100000 * sign]

    results = []
    for val in test_values:
        try:
            result = _evaluate_at(expr, var, float(val))
            if result is not None and not math.isnan(result) and math.isfinite(result):
                results.append(result)
        except:
            pass

    if len(results) < 3:
        return None

    # Check for convergence - values should be getting closer to a limit
    # Check if the sequence appears to converge
    diffs = [abs(results[i+1] - results[i]) for i in range(len(results)-1)]

    # If differences are decreasing and the last value is stable
    if all(d < 0.01 for d in diffs[-2:]):
        # Converged - return the last value
        return results[-1]

    # Check for divergence to infinity (handles both exponential and logarithmic growth)
    # Method 1: Values growing by ratio > 1.5 (exponential growth)
    if all(abs(results[i+1]) > abs(results[i]) * 1.5 for i in range(len(results)-1)):
        if results[-1] > 0:
            return float('inf')
        else:
            return float('-inf')

    # Method 2: Monotonic growth with increasing values (catches logarithmic growth)
    # If values are monotonically increasing and the last value is large enough
    if all(results[i+1] > results[i] for i in range(len(results)-1)):
        # Check if the growth continues without leveling off
        # Compare growth rate: if (f(10000) - f(1000)) > 0.5*(f(1000) - f(100))
        # this suggests continued unbounded growth
        if len(results) >= 3:
            growth1 = results[1] - results[0]
            growth2 = results[2] - results[1]
            growth3 = results[3] - results[2] if len(results) > 3 else growth2
            # If growth continues (doesn't diminish to near-zero), it's divergent
            if growth3 > 0.1 and abs(results[-1]) > 10:
                return float('inf')

    # Method 3: Monotonic decrease to negative infinity
    if all(results[i+1] < results[i] for i in range(len(results)-1)):
        if len(results) >= 3:
            growth3 = results[-2] - results[-1]
            if growth3 > 0.1 and results[-1] < -10:
                return float('-inf')

    # If values oscillate but stay bounded, check if they bracket a value
    if max(results) - min(results) < 0.1:
        return sum(results) / len(results)

    return None





def _evaluate_at(expr: Expr, var: str, value: float) -> Optional[float]:
    """Evaluate expression at a specific variable value."""
    import math

    if isinstance(expr, Num):
        return float(expr.value)
    elif isinstance(expr, Sym):
        if expr.name == var:
            return value
        elif expr.name == 'pi':
            return math.pi
        elif expr.name in ('e', 'E'):
            return math.e
        return None  # Unknown symbol
    elif isinstance(expr, Neg):
        inner = _evaluate_at(expr.arg, var, value)
        return -inner if inner is not None else None
    elif isinstance(expr, Add):
        result = 0.0
        for term in expr.terms:
            val = _evaluate_at(term, var, value)
            if val is None:
                return None
            result += val
        return result
    elif isinstance(expr, Mul):
        result = 1.0
        for factor in expr.factors:
            val = _evaluate_at(factor, var, value)
            if val is None:
                return None
            result *= val
        return result
    elif isinstance(expr, Pow):
        base_val = _evaluate_at(expr.base, var, value)
        exp_val = _evaluate_at(expr.exp, var, value)
        if base_val is not None and exp_val is not None:
            try:
                return base_val ** exp_val
            except:
                return None
        return None
    elif isinstance(expr, Func):
        arg_val = _evaluate_at(expr.arg, var, value)
        if arg_val is None:
            return None
        func_map = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'exp': math.exp, 'ln': math.log, 'log': math.log,
            'sqrt': math.sqrt, 'abs': abs, 'Abs': abs,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
        }
        if expr.name in func_map:
            try:
                return func_map[expr.name](arg_val)
            except:
                return None
    return None





