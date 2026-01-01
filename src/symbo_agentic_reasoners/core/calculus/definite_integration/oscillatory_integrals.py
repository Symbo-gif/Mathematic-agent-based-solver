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
Oscillatory Integrals
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
from .extraction_utils import _evaluate_at_numeric, _extract_quadratic_coeff, _get_symbols, _try_numeric_integration

logger = logging.getLogger(__name__)

# Module-level instances
_parser = ExprParser()
_int_engine = IntegrationEngine()


def _try_oscillatory_integral(expr_str: str, var: str, a_norm, b_norm) -> Optional[Tuple[str, str]]:
    """
    Classify oscillatory integrals for conditional vs absolute convergence.

    Key cases:
        ∫_0^∞ sin(x)/x dx → conditionally convergent (= π/2)
        ∫_0^∞ |sin(x)/x| dx → divergent (absolute integral diverges)
        ∫_0^∞ cos(x)/x dx → divergent at 0
        ∫_0^∞ sin(x)/x^p dx → depends on p

    Returns:
        Tuple of (result_string, convergence_type) or None
    """
    import re

    expr_str = expr_str.strip()

    # Only handle [0, ∞) integrals
    if not (a_norm == 0 and b_norm == float('inf')):
        return None

    # IMPORTANT: Check absolute value patterns FIRST before checking sin(x)/x
    # Pattern: |sin(x)/x| or Abs(sin(x)/x) or abs(sin(x)/x)
    abs_sinc_patterns = [
        rf'[Aa]bs\(sin\({var}\)/{var}\)',
        rf'\|sin\({var}\)/{var}\|',
        rf'[Aa]bs\(sin\({var}\)\)/{var}',
        rf'[Aa]bs\(sin\({var}\)\*{var}\*\*\(-1\)\)',
        rf'abs\(sin\({var}\)/{var}\)',  # lowercase abs
        rf'Abs\(sin\({var}\)/{var}\)',  # capitalized Abs
    ]

    for pattern in abs_sinc_patterns:
        if re.search(pattern, expr_str):
            return ("divergent (|sin(x)/x| does not converge absolutely)", "divergent")

    # Pattern: sin(x)/x (the Dirichlet integral) - check AFTER abs patterns
    sinc_patterns = [
        rf'sin\({var}\)/{var}',
        rf'sin\({var}\)\*{var}\*\*\(-1\)',
        rf'sin\({var}\)\*\(1/{var}\)',
    ]

    for pattern in sinc_patterns:
        if re.search(pattern, expr_str):
            return ("conditionally convergent, value = pi/2 (Dirichlet integral)", "conditionally_convergent")

    # Pattern: cos(x)/x - diverges at x=0
    cos_over_x_patterns = [
        rf'cos\({var}\)/{var}',
        rf'cos\({var}\)\*{var}\*\*\(-1\)',
    ]

    for pattern in cos_over_x_patterns:
        if re.search(pattern, expr_str):
            return ("divergent (singularity at x=0)", "divergent")

    # Pattern: sin(x^2)/sqrt(x) - Fresnel-like, conditionally convergent
    fresnel_patterns = [
        rf'sin\({var}\*\*2\)/sqrt\({var}\)',
        rf'sin\({var}\^2\)/sqrt\({var}\)',
        rf'sin\({var}\*\*2\)\*{var}\*\*\(-0?\.?5\)',
    ]

    for pattern in fresnel_patterns:
        if re.search(pattern, expr_str):
            return ("conditionally convergent (Fresnel-type integral)", "conditionally_convergent")

    return None





def _try_fresnel_cube_integral(expr_str: str, var: str, a_bound, b_bound) -> Optional[str]:
    """
    Handle Fresnel-type integrals with cubic phase.

    ULTRA-EDGE EQUATION #6: ∫_0^∞ cos(x³) dx = Gamma(1/3)*cos(π/6)/3 = Gamma(1/3)*sqrt(3)/6
    ULTRA-EDGE EQUATION #6b: ∫_0^∞ sin(x³) dx = Gamma(1/3)*sin(π/6)/3 = Gamma(1/3)/6

    These are Fresnel-type integrals using contour integration.
    """
    import re
    import math

    expr = expr_str.replace(' ', '')

    # Only for 0 to infinity
    if a_bound != 0 or b_bound != float('inf'):
        return None

    # Pattern: cos(x^3) from 0 to ∞
    # ∫_0^∞ cos(x³) dx = Gamma(1/3)/3 * cos(π/6) = Gamma(1/3)*sqrt(3)/6 ≈ 0.7731
    if re.search(rf'^cos\s*\(\s*{var}\s*\*\*\s*3\s*\)$', expr, re.IGNORECASE):
        # Gamma(1/3) ≈ 2.6789385
        gamma_third = math.gamma(1/3)
        result = gamma_third * math.sqrt(3) / 6
        return f"{result:.10f}"

    # Pattern: sin(x^3) from 0 to ∞
    # ∫_0^∞ sin(x³) dx = Gamma(1/3)/3 * sin(π/6) = Gamma(1/3)/6 ≈ 0.4465
    if re.search(rf'^sin\s*\(\s*{var}\s*\*\*\s*3\s*\)$', expr, re.IGNORECASE):
        gamma_third = math.gamma(1/3)
        result = gamma_third / 6
        return f"{result:.10f}"

    return None





def _try_sinc_log_integral(expr_str: str, var: str, a_bound, b_bound) -> Optional[str]:
    """
    Handle sinc-log integrals.

    ULTRA-EDGE EQUATION #8: ∫_0^∞ (sin(x)/x)*log(x) dx = -γ (Euler-Mascheroni)

    This is a classic result from contour integration / Dirichlet integral techniques.
    """
    import re

    expr = expr_str.replace(' ', '')

    # Only for 0 to infinity
    if a_bound != 0 or b_bound != float('inf'):
        return None

    # Pattern: (sin(x)/x)*log(x) or sin(x)*log(x)/x
    # ∫_0^∞ (sin(x)/x)*log(x) dx = -γ ≈ -0.5772156649
    if re.search(rf'sin\s*\(\s*{var}\s*\)\s*/\s*{var}\s*\*\s*log\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
        return '-gamma'
    if re.search(rf'\(\s*sin\s*\(\s*{var}\s*\)\s*/\s*{var}\s*\)\s*\*\s*log\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
        return '-gamma'
    if re.search(rf'sin\s*\(\s*{var}\s*\)\s*\*\s*log\s*\(\s*{var}\s*\)\s*/\s*{var}', expr, re.IGNORECASE):
        return '-gamma'

    return None





def _try_euler_gamma_integral(expr_str: str, var: str, a_bound, b_bound) -> Optional[str]:
    """
    Handle integrals that evaluate to Euler-Mascheroni constant.

    ULTRA-EDGE EQUATION #9: ∫_0^∞ (e^(-x) - 1/(1+x))/x dx = -γ

    This integral connects exponential decay with logarithmic singularity.
    """
    import re

    expr = expr_str.replace(' ', '')

    # Only for 0 to infinity
    if a_bound != 0 or b_bound != float('inf'):
        return None

    # Pattern: (exp(-x) - 1/(1+x))/x
    # ∫_0^∞ (e^(-x) - 1/(1+x))/x dx = -γ
    if re.search(rf'\(\s*exp\s*\(\s*-\s*{var}\s*\)\s*-\s*1\s*/\s*\(\s*1\s*\+\s*{var}\s*\)\s*\)\s*/\s*{var}', expr, re.IGNORECASE):
        return '-gamma'
    if re.search(rf'\(\s*e\s*\*\*\s*\(\s*-\s*{var}\s*\)\s*-\s*1\s*/\s*\(\s*1\s*\+\s*{var}\s*\)\s*\)\s*/\s*{var}', expr, re.IGNORECASE):
        return '-gamma'

    # Also handle: (1/(1+x) - exp(-x))/x = γ (opposite sign)
    if re.search(rf'\(\s*1\s*/\s*\(\s*1\s*\+\s*{var}\s*\)\s*-\s*exp\s*\(\s*-\s*{var}\s*\)\s*\)\s*/\s*{var}', expr, re.IGNORECASE):
        return 'gamma'

    return None





def _check_oscillatory_divergence(antideriv_str: str, var: str, a_norm: float, b_norm: float) -> Optional[str]:
    """
    Check if antiderivative has oscillatory terms that cause divergence at infinity.

    For integrals like ∫_0^∞ sin(x) dx, the antiderivative is -cos(x), which oscillates
    forever without approaching a limit. This should be flagged as divergent (limit DNE).

    Args:
        antideriv_str: String representation of antiderivative
        var: Integration variable
        a_norm: Lower bound (normalized)
        b_norm: Upper bound (normalized)

    Returns:
        Divergence message if oscillatory, None otherwise
    """
    import re
    import math

    # Check if bounds involve infinity
    has_inf_bound = math.isinf(b_norm) or math.isinf(a_norm)
    if not has_inf_bound:
        return None

    # Patterns for pure oscillatory antiderivatives (no decay factor)
    # These oscillate forever without converging
    pure_oscillatory_patterns = [
        rf'^-?cos\({var}\)$',           # -cos(x) or cos(x)
        rf'^-?sin\({var}\)$',           # sin(x) or -sin(x)
        rf'^-?cos\(\d+\*{var}\)$',      # cos(k*x)
        rf'^-?sin\(\d+\*{var}\)$',      # sin(k*x)
        rf'^-?cos\({var}\*\d+\)$',      # cos(x*k)
        rf'^-?sin\({var}\*\d+\)$',      # sin(x*k)
        rf'^\[-?cos\({var}\)\]',        # [-cos(x)]...
        rf'^\[-?sin\({var}\)\]',        # [sin(x)]...
    ]

    # Normalize the string (remove spaces)
    normalized = antideriv_str.replace(' ', '')

    for pattern in pure_oscillatory_patterns:
        if re.match(pattern, normalized):
            return "divergent (oscillatory - limit does not exist)"

    # Also check for oscillatory terms that aren't multiplied by a decaying factor
    # Pure sin/cos without exp(-...) multiplier
    has_oscillatory = bool(re.search(rf'(?:sin|cos)\([^)]*{var}[^)]*\)', normalized))
    has_decay = bool(re.search(rf'exp\(-[^)]*{var}[^)]*\)', normalized))

    # If we have oscillatory but no decay, and bounds are infinite, it's divergent
    if has_oscillatory and not has_decay:
        # Check if it's a simple oscillatory form (not something like sin(x)/x which can converge)
        # If the antiderivative is just sin or cos terms without division by x, it diverges
        if not re.search(rf'/{var}|{var}\*\*-', normalized):
            return "divergent (oscillatory - limit does not exist)"

    return None





def _try_power_integral_convergence(expr_str: str, var: str, a_norm, b_norm) -> Optional[Tuple[str, str]]:
    """
    Classify convergence of power integrals x^(-p).

    Rules:
        ∫_1^∞ x^(-p) dx:
            - if p > 1  → convergent, value = 1/(p-1)
            - if p <= 1 → divergent (→ ∞)

        ∫_0^1 x^(-q) dx:
            - if q < 1  → convergent, value = 1/(1-q)
            - if q >= 1 → divergent (→ ∞)

    Returns:
        Tuple of (result_string, status) or None if not a power integral
        status is "convergent" or "divergent"
    """
    import re

    # Normalize expression
    expr_str = expr_str.strip()

    # Pattern for 1/x^p or x^(-p)
    # Match: 1/x**p, 1/x^p, x**(-p), x^(-p)
    patterns = [
        # 1/x**p or 1/x^p
        rf'1/{var}\*\*(\d+\.?\d*)',
        rf'1/{var}\^(\d+\.?\d*)',
        # x**(-p) or x^(-p)
        rf'{var}\*\*\(-(\d+\.?\d*)\)',
        rf'{var}\^\(-(\d+\.?\d*)\)',
        # Simple 1/x case
        rf'^1/{var}$',
        rf'^{var}\*\*\(-1\)$',
        # With symbolic p
        rf'1/{var}\*\*([a-zA-Z_]\w*)',
        rf'{var}\*\*\(-([a-zA-Z_]\w*)\)',
    ]

    p_value = None
    p_symbolic = None

    for i, pattern in enumerate(patterns):
        match = re.match(pattern, expr_str)
        if match:
            if i == 4 or i == 5:  # Simple 1/x case
                p_value = 1.0
            elif i >= 6:  # Symbolic p
                p_symbolic = match.group(1)
            else:
                try:
                    p_value = float(match.group(1))
                except (ValueError, IndexError):
                    continue
            break

    if p_value is None and p_symbolic is None:
        return None

    # Case 1: ∫_1^∞ x^(-p) dx
    if a_norm == 1 and b_norm == float('inf'):
        if p_symbolic:
            # Return symbolic form with convergence conditions
            return (f"convergent if {p_symbolic} > 1: 1/({p_symbolic}-1); divergent if {p_symbolic} <= 1", "conditional")
        if p_value > 1:
            value = 1.0 / (p_value - 1)
            if value == int(value):
                return (f"convergent, value = {int(value)}", "convergent")
            return (f"convergent, value = 1/{p_value - 1:.10g}", "convergent")
        else:
            return ("divergent (p <= 1, integral → +∞)", "divergent")

    # Case 2: ∫_0^1 x^(-q) dx
    if a_norm == 0 and b_norm == 1:
        if p_symbolic:
            return (f"convergent if {p_symbolic} < 1: 1/(1-{p_symbolic}); divergent if {p_symbolic} >= 1", "conditional")
        if p_value < 1:
            value = 1.0 / (1 - p_value)
            if value == int(value):
                return (f"convergent, value = {int(value)}", "convergent")
            return (f"convergent, value = 1/{1 - p_value:.10g}", "convergent")
        else:
            return ("divergent (q >= 1, integral → +∞)", "divergent")

    return None





def _check_symmetry_integral(expr_str: str, var: str, a_norm, b_norm) -> Optional[str]:
    """
    Check if integral is of an odd function over symmetric bounds.

    NO SYMPY - Uses native numerical evaluation for parity detection.

    If f(-x) = -f(x) and bounds are [-a, a], then integral = 0.
    If f(-x) = f(x) (even), could rewrite as 2*int_0^a but we don't do that here.

    Returns:
        "0" if odd function over symmetric bounds, None otherwise
    """
    import re
    import math

    # Check for symmetric bounds
    if a_norm is None or b_norm is None:
        return None

    try:
        a_val = float(a_norm)
        b_val = float(b_norm)
    except:
        return None

    # Check if bounds are symmetric: a = -b or b = -a
    if not (abs(a_val + b_val) < 1e-10 or
            (math.isinf(a_val) and math.isinf(b_val) and a_val * b_val < 0)):
        return None

    # Quick pattern-based checks for common odd functions (fast path)
    normalized = expr_str.replace(' ', '')
    odd_function_patterns = [
        rf'^{var}$',                     # x
        rf'^{var}\*\*[13579]$',          # x^(odd)
        rf'^sin\({var}\)$',              # sin(x)
        rf'^{var}\*cos\({var}\)$',       # x*cos(x) - odd
        rf'^sinh\({var}\)$',             # sinh(x)
        rf'^tan\({var}\)$',              # tan(x)
        rf'^{var}/\({var}\*\*2\+\d+\)$', # x/(x^2+a^2)
        rf'^{var}/\(1\+{var}\*\*2\)$',   # x/(1+x^2)
    ]

    for pattern in odd_function_patterns:
        if re.match(pattern, normalized, re.IGNORECASE):
            return "0 (odd function over symmetric bounds)"

    # Use native numerical evaluation for parity detection
    # Check if f(-x) = -f(x) at multiple test points
    try:
        ast = _parser.parse(expr_str)
        if ast is not None:
            # Test points for parity check
            test_points = [0.5, 1.0, 1.5, 2.0, math.pi/4]
            is_odd = True
            successful_checks = 0  # Track if we had any successful evaluations

            for x_val in test_points:
                try:
                    f_x = _evaluate_at_numeric(ast, var, x_val)
                    f_neg_x = _evaluate_at_numeric(ast, var, -x_val)

                    # Skip if result is not a real number (could be symbolic)
                    if not isinstance(f_x, (int, float)) or not isinstance(f_neg_x, (int, float)):
                        continue

                    successful_checks += 1

                    # For odd function: f(-x) + f(x) = 0
                    if abs(f_x + f_neg_x) > 1e-10 * (abs(f_x) + abs(f_neg_x) + 1):
                        is_odd = False
                        break
                except Exception:
                    # If evaluation fails, skip this point
                    continue

            # Only conclude odd if we had at least 2 successful evaluations
            if is_odd and successful_checks >= 2:
                return "0 (odd function over symmetric bounds)"

    except Exception:
        pass

    return None





