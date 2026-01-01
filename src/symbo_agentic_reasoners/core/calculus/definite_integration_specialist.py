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
Definite Integration Specialist (Thin Wrapper)
===============================================

This module provides backward compatibility for the original definite_integration_specialist.py
interface. The actual implementation has been decomposed into focused sub-specialist modules
located in the definite_integration/ subdirectory:

Sub-specialists:
    - gaussian_integrals.py (~1,200 lines): Gaussian integral patterns
    - exponential_integrals.py (~600 lines): Exponential ray integrals
    - special_integrals.py (~800 lines): Beta, Gamma, Lorentzian, etc.
    - oscillatory_integrals.py (~400 lines): Fresnel, sinc, oscillatory patterns
    - singularity_analysis.py (~700 lines): Singularity detection and analysis
    - extraction_utils.py (~800 lines): Coefficient extraction utilities

Main exports (delegated to sub-specialists):
    - definite_integrate: Compute definite integrals with limits
    - _check_log_singularity: Detect logarithmic singularities
    - All other specialized functions are available through the definite_integration package

Architecture:
    The original 5,130-line monolithic module has been decomposed into 6 focused
    sub-specialist modules for better maintainability and separation of concerns.
    This thin wrapper maintains backward compatibility by re-exporting all public
    functions from the definite_integration package.

Usage:
    # Original usage still works:
    from .definite_integration_specialist import definite_integrate

    # New modular usage also available:
    from .definite_integration import definite_integrate
    from .definite_integration.gaussian_integrals import _try_gaussian_integral
"""

import logging
from typing import Optional, Tuple, Union

# Import everything from the definite_integration package
from .definite_integration import (
    # Main entry point
    definite_integrate,
    DefiniteIntegrationSupervisor,

    # Gaussian integrals
    _try_gaussian_integral,
    _try_gaussian_moment_integral,
    _try_half_gaussian_integral,
    _try_completion_square_gaussian,
    _try_gaussian_fourier_integral,
    _try_oscillatory_gaussian_integral,
    _try_linear_gaussian_full_line,
    _try_symbolic_gaussian_integral,
    _try_standard_normal_integral,

    # Exponential integrals
    _try_exponential_ray_integral,
    _try_exponential_ray_moments,
    _try_linear_exponential_ray,

    # Special integrals
    _try_lorentzian_power_integral,
    _try_beta_integral,
    _try_heat_kernel_integral,
    _try_green_function_integral,
    _try_gamma_power_integral,
    _try_semicircle_integral,

    # Oscillatory integrals
    _try_oscillatory_integral,
    _try_fresnel_cube_integral,
    _try_sinc_log_integral,
    _try_euler_gamma_integral,
    _check_oscillatory_divergence,
    _try_power_integral_convergence,
    _check_symmetry_integral,

    # Singularity analysis
    _check_log_singularity,
    _check_pole_singularity,
    _check_log_power_integral,
    _analyze_singularities,
    _evaluate_limit,
    _evaluate_at,

    # Extraction utilities
    _fix_exponent_precedence_inline,
    _try_numeric_integration,
)

# Import sub-modules for direct access
from .definite_integration import (
    gaussian_integrals,
    exponential_integrals,
    special_integrals,
    oscillatory_integrals,
    singularity_analysis,
    extraction_utils,
)

logger = logging.getLogger(__name__)

# Module-level docstring for backward compatibility
__doc__ += """

Definite Integration with Special Integral Patterns
====================================================

This module provides definite integration with support for special integral patterns:

Gaussian Integrals:
    - exp(-x²) over full line: √π
    - exp(-a*x²) over full line: √(π/a)
    - Gaussian moments: x^n * exp(-a*x²)
    - Half-line Gaussians: ∫_0^∞ exp(-a*x²) dx
    - Normalized Gaussian PDF: (1/√(2π))*exp(-x²/2)
    - Completion of square: exp(-a*x² + b*x)
    - Gaussian Fourier transforms: exp(-a*x²)*cos(k*x)

Exponential Integrals:
    - Exponential ray: ∫_0^∞ exp(-a*x) dx = 1/a
    - Exponential moments: ∫_0^∞ x^n * exp(-a*x) dx = n!/a^(n+1)
    - Polynomial × exponential: P(x)*exp(-a*x)

Special Function Integrals:
    - Beta function: ∫_0^1 x^(α-1)*(1-x)^(β-1) dx
    - Gamma power: ∫_{-∞}^{∞} exp(-x^p) dx
    - Lorentzian powers: ∫ 1/(x² + m²)^n dx
    - Heat kernel: ∫ exp(-(x-a)²/(4t))/sqrt(4πt) dx
    - Green's function: ∫ exp(-a*|x-t|) dx
    - Semicircle area: ∫ sqrt(R² - x²) dx

Oscillatory Integrals:
    - Dirichlet integral: ∫_0^∞ sin(x)/x dx = π/2
    - Fresnel integrals: ∫_0^∞ cos(x³) dx, ∫_0^∞ sin(x³) dx
    - Sinc-log: ∫_0^∞ (sin(x)/x)*log(x) dx = -γ
    - Euler-gamma: ∫_0^∞ (exp(-x) - 1/(1+x))/x dx = -γ

Singularity Detection:
    - Logarithmic singularities: e^(-x)/x at x=0
    - Pole singularities: 1/(x-a) in integration domain
    - Interior vs endpoint singularities
    - Convergence classification for power integrals

Symbolic and Numeric Support:
    - Symbolic coefficients (a, m, ω, ħ, β, etc.)
    - Numeric evaluation via scipy when symbolic fails
    - Automatic limit evaluation for infinite bounds
    - Divergence detection (oscillatory, power law, exponential)

Examples:
    >>> definite_integrate('exp(-x**2)', 'x', '-inf', 'inf')
    (True, 'sqrt(pi)', 'native_calculus')

    >>> definite_integrate('x**2 * exp(-x**2)', 'x', '-inf', 'inf')
    (True, 'sqrt(pi)/2', 'native_calculus')

    >>> definite_integrate('exp(-x)', 'x', 0, 'inf')
    (True, '1', 'native_calculus')

    >>> definite_integrate('sin(x)/x', 'x', 0, 'inf')
    (True, 'pi/2', 'native_calculus_dirichlet')
"""

# Export all public functions and classes
__all__ = [
    # Main entry point
    'definite_integrate',
    'DefiniteIntegrationSupervisor',

    # Sub-modules
    'gaussian_integrals',
    'exponential_integrals',
    'special_integrals',
    'oscillatory_integrals',
    'singularity_analysis',
    'extraction_utils',

    # Gaussian integral functions
    '_try_gaussian_integral',
    '_try_gaussian_moment_integral',
    '_try_half_gaussian_integral',
    '_try_completion_square_gaussian',
    '_try_gaussian_fourier_integral',
    '_try_oscillatory_gaussian_integral',
    '_try_linear_gaussian_full_line',
    '_try_symbolic_gaussian_integral',
    '_try_standard_normal_integral',

    # Exponential integral functions
    '_try_exponential_ray_integral',
    '_try_exponential_ray_moments',
    '_try_linear_exponential_ray',

    # Special integral functions
    '_try_lorentzian_power_integral',
    '_try_beta_integral',
    '_try_heat_kernel_integral',
    '_try_green_function_integral',
    '_try_gamma_power_integral',
    '_try_semicircle_integral',

    # Oscillatory integral functions
    '_try_oscillatory_integral',
    '_try_fresnel_cube_integral',
    '_try_sinc_log_integral',
    '_try_euler_gamma_integral',
    '_check_oscillatory_divergence',
    '_try_power_integral_convergence',
    '_check_symmetry_integral',

    # Singularity analysis functions
    '_check_log_singularity',
    '_check_pole_singularity',
    '_check_log_power_integral',
    '_analyze_singularities',
    '_evaluate_limit',
    '_evaluate_at',

    # Utility functions
    '_fix_exponent_precedence_inline',
    '_try_numeric_integration',
]


# Convenience function for backward compatibility
def get_specialist():
    """
    Get a DefiniteIntegrationSupervisor instance.

    This function exists for backward compatibility with code that may have
    used a factory pattern to get the specialist.

    Returns:
        DefiniteIntegrationSupervisor: A new supervisor instance
    """
    return DefiniteIntegrationSupervisor()


# Log module initialization
logger.info("Definite Integration Specialist loaded (thin wrapper over decomposed sub-specialists)")
