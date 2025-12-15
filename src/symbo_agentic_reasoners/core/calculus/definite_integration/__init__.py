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
Definite Integration Sub-Specialists
=====================================

This package contains specialized modules for different types of definite integrals:

- gaussian_integrals: Gaussian integrals (full-line, half-line, moments)
- exponential_integrals: Exponential ray integrals and moments
- special_integrals: Beta, Gamma, Lorentzian, heat kernel, etc.
- oscillatory_integrals: Fresnel, sinc, oscillatory patterns
- singularity_analysis: Singularity detection and analysis
- extraction_utils: Coefficient extraction and utility functions

Main exports:
- definite_integrate: Main entry point for definite integration
- DefiniteIntegrationSupervisor: Router class for backward compatibility
"""

import logging
import math
from typing import Optional, Tuple, Union

# Import all sub-specialists
from . import gaussian_integrals
from . import exponential_integrals
from . import special_integrals
from . import oscillatory_integrals
from . import singularity_analysis
from . import extraction_utils

# Import key functions for direct access
from .gaussian_integrals import (
    _try_gaussian_integral,
    _try_gaussian_moment_integral,
    _try_half_gaussian_integral,
    _try_completion_square_gaussian,
    _try_gaussian_fourier_integral,
    _try_oscillatory_gaussian_integral,
    _try_linear_gaussian_full_line,
    _try_symbolic_gaussian_integral,
    _try_standard_normal_integral,
)

from .exponential_integrals import (
    _try_exponential_ray_integral,
    _try_exponential_ray_moments,
    _try_linear_exponential_ray,
)

from .special_integrals import (
    _try_lorentzian_power_integral,
    _try_beta_integral,
    _try_heat_kernel_integral,
    _try_green_function_integral,
    _try_gamma_power_integral,
    _try_semicircle_integral,
)

from .oscillatory_integrals import (
    _try_oscillatory_integral,
    _try_fresnel_cube_integral,
    _try_sinc_log_integral,
    _try_euler_gamma_integral,
    _check_oscillatory_divergence,
    _try_power_integral_convergence,
    _check_symmetry_integral,
)

from .singularity_analysis import (
    _check_log_singularity,
    _check_pole_singularity,
    _check_log_power_integral,
    _analyze_singularities,
    _evaluate_limit,
    _evaluate_at,
)

from .extraction_utils import (
    _fix_exponent_precedence_inline,
    _try_numeric_integration,
)

# Import from parent modules
from ..ast_types import Expr
from ..expression_parser import ExprParser
from ..validation import check_expression_safety as _check_expression_safety
from ..calculus_utils import _simplify_output
from ..integration_specialist import IntegrationEngine

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


def definite_integrate(expr_str: str, var: str = 'x', a: Union[float, str] = None,
                       b: Union[float, str] = None) -> Tuple[bool, Optional[str], str]:
    """
    Compute definite integral with limits.

    This is the main entry point that routes to appropriate sub-specialists.

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


class DefiniteIntegrationSupervisor:
    """
    Supervisor class for backward compatibility.

    Routes definite_integrate() calls to the appropriate sub-specialists.
    This class maintains the same interface as the original monolithic module.
    """

    def __init__(self):
        """Initialize the supervisor."""
        self.parser = ExprParser()
        self.int_engine = IntegrationEngine()

    def definite_integrate(self, expr_str: str, var: str = 'x',
                          a: Union[float, str] = None,
                          b: Union[float, str] = None) -> Tuple[bool, Optional[str], str]:
        """
        Compute definite integral with limits.

        This method simply delegates to the package-level definite_integrate function.
        """
        return definite_integrate(expr_str, var, a, b)


# Export main function and class
__all__ = [
    'definite_integrate',
    'DefiniteIntegrationSupervisor',
    # Sub-modules
    'gaussian_integrals',
    'exponential_integrals',
    'special_integrals',
    'oscillatory_integrals',
    'singularity_analysis',
    'extraction_utils',
    # Key functions
    '_try_gaussian_integral',
    '_try_exponential_ray_integral',
    '_try_lorentzian_power_integral',
    '_try_oscillatory_integral',
    '_check_log_singularity',
    '_check_pole_singularity',
]
