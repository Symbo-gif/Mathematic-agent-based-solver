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
Limit Specialist (Thin Wrapper)
================================

This module provides backward compatibility by importing from the modular limits package.

The implementation has been decomposed into focused sub-specialists:
- limits/limit_patterns.py: Known limit pattern matching
- limits/asymptotic_rules.py: Special function asymptotics
- limits/taylor_limits.py: Taylor series expansion
- limits/algebra_utilities.py: Polynomial and algebra solvers
- limits/gaussian_2d.py: 2D Gaussian integration
- limits/__init__.py: LimitEngine and native_limit

All functionality is preserved with the same interface.
"""

# Import everything from the limits package
from .limits import (
    # Main classes and functions
    LimitEngine,
    native_limit,

    # Constants
    KNOWN_LIMIT_PATTERNS,
    PARAMETER_ASSUMPTIONS,

    # Pattern matching functions
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

    # Asymptotic rules
    _try_special_function_asymptotic,
    _try_limit_with_assumptions,

    # Taylor expansion
    _try_taylor_expansion_limit,
    taylor_series,

    # Algebra utilities
    solve_polynomial,
    solve_system_native,
    factor_polynomial,
    expand_expression,
    solve_ode_native,
    _eval_at_point,
    _get_symbols,
    _evaluate_expr_numerically,

    # Gaussian 2D integration
    _try_2d_gaussian_integral,
    definite_integrate_2d,
    _try_separable_2d_integral,
)

# Re-export for backward compatibility
__all__ = [
    'LimitEngine',
    'native_limit',
    'KNOWN_LIMIT_PATTERNS',
    'PARAMETER_ASSUMPTIONS',
    '_try_known_limit_pattern',
    '_try_nested_log_limit',
    '_try_stirling_limit',
    '_try_asymptotic_difference_limit',
    '_try_nested_limit',
    '_try_one_sided_divergent_limit',
    '_try_oscillatory_decay_limit',
    '_try_power_decay_limit',
    '_try_log_polynomial_limit',
    '_try_exp_polynomial_limit',
    '_try_pure_oscillatory_limit',
    '_try_e_type_limit',
    '_try_constant_limit',
    '_try_sinc_limit',
    '_try_one_minus_cos_limit',
    '_try_one_minus_cos_sq_limit',
    '_try_direct_substitution',
    '_try_special_function_asymptotic',
    '_try_limit_with_assumptions',
    '_try_taylor_expansion_limit',
    'taylor_series',
    'solve_polynomial',
    'solve_system_native',
    'factor_polynomial',
    'expand_expression',
    'solve_ode_native',
    '_eval_at_point',
    '_get_symbols',
    '_evaluate_expr_numerically',
    '_try_2d_gaussian_integral',
    'definite_integrate_2d',
    '_try_separable_2d_integral',
]
