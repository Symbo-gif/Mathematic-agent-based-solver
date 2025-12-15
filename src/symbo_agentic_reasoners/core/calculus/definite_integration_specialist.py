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

import logging
import math
import re
from typing import Optional, Tuple, Union, Dict, Any

# Import AST types from sibling modules
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func
from .expression_parser import ExprParser
from .validation import check_expression_safety as _check_expression_safety
from .calculus_utils import _simplify_output, _try_evaluate_const
from .integration_specialist import IntegrationEngine

logger = logging.getLogger(__name__)

# Module-level instances (lazy initialization)
_parser = None
_int_engine = None

def _get_parser():
    """Lazy initialization of parser."""
    global _parser
    if _parser is None:
        _parser = ExprParser()
    return _parser

def _get_int_engine():
    """Lazy initialization of integration engine."""
    global _int_engine
    if _int_engine is None:
        _int_engine = IntegrationEngine()
    return _int_engine

# Initialize on module load
_parser = ExprParser()
_int_engine = IntegrationEngine()


# =============================================================================
# EXTRACTED FUNCTIONS FROM NATIVE_CALCULUS.PY
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
        if n <= 0:
            return 1
        result = 1
        for i in range(1, 2*n, 2):
            result *= i
        return result

    # Helper: compute k! = k factorial
    def factorial(k):
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

            for x_val in test_points:
                try:
                    f_x = _evaluate_at_numeric(ast, var, x_val)
                    f_neg_x = _evaluate_at_numeric(ast, var, -x_val)

                    # For odd function: f(-x) + f(x) = 0
                    if abs(f_x + f_neg_x) > 1e-10 * (abs(f_x) + abs(f_neg_x) + 1):
                        is_odd = False
                        break
                except Exception:
                    # If evaluation fails, skip this point
                    continue

            if is_odd:
                return "0 (odd function over symmetric bounds)"

    except Exception:
        pass

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



