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
Limit Patterns
==============

Known limit pattern functions for pattern-based limit evaluation.
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

KNOWN_LIMIT_PATTERNS = {
    # Pattern: x^n/exp(x) as x→∞ = 0 (exponential dominates polynomial)
    'poly_over_exp_inf': {
        'pattern': r'^(\w+)\s*\*\*\s*\w+\s*/\s*exp\s*\(\s*\1\s*\)',
        'result': '0',
        'point': 'oo',
        'description': "Polynomial under exponential: x^n/exp(x) → 0"
    },

    # =========================================================================
    # FUNDAMENTAL EXPONENTIAL LIMITS AT ZERO
    # =========================================================================
    # Pattern: (exp(x) - 1)/x as x→0 = 1 (definition of derivative of exp at 0)
    'exp_minus_one_over_x': {
        'pattern': r'^\s*\(\s*exp\s*\(\s*(\w+)\s*\)\s*-\s*1\s*\)\s*/\s*\1\s*$',
        'result': '1',
        'point': '0',
        'description': "Exponential derivative definition: (exp(x)-1)/x → 1"
    },

    # Pattern: (exp(ax) - 1)/x as x→0 = a (more general form)
    'exp_ax_minus_one_over_x': {
        'pattern': r'^\s*\(\s*exp\s*\(\s*(\w+)\s*\*\s*(\w+)\s*\)\s*-\s*1\s*\)\s*/\s*\2\s*$',
        'result': lambda m, point: m.group(1),
        'point': '0',
        'description': "Exponential derivative: (exp(ax)-1)/x → a"
    },

    # =========================================================================
    # LOG-POWER LIMITS AT ZERO
    # =========================================================================
    # Pattern: x^a * log(x) as x→0+ = 0 for a > 0
    'power_log_zero': {
        'pattern': r'^(\w+)\s*\*\*\s*(\w+)\s*\*\s*log\s*\(\s*\1\s*\)',
        'result': '0',
        'point': '0',
        'assumptions': {'exponent': 'positive'},
        'description': "Power times log at zero: x^a*log(x) → 0 for a > 0"
    },

    # =========================================================================
    # N-TH ROOT AND LOGARITHM LIMITS
    # =========================================================================
    # Pattern: n * (x^(1/n) - 1) as n→∞ = log(x)
    'nth_root_limit': {
        'pattern': r'^(\w+)\s*\*\s*\(\s*(\w+)\s*\*\*\s*\(\s*1\s*/\s*\1\s*\)\s*-\s*1\s*\)',
        'result': lambda m, point: f"log({m.group(2)})" if str(point).lower() in ('oo', 'inf', 'infinity') else None,
        'point': 'oo',
        'description': "n-th root limit: n*(x^(1/n)-1) → log(x)"
    },

    # Pattern: binomial(2n, n) / (4^n * sqrt(pi*n)) as n→∞ = 1/sqrt(pi)
    'stirling_binomial': {
        'pattern': r'binomial\s*\(\s*2\s*\*\s*(\w+)\s*,\s*\1\s*\)\s*/\s*\(\s*4\s*\*\*\s*\1\s*\*\s*sqrt\s*\(\s*pi\s*\*\s*\1\s*\)\s*\)',
        'result': '1/sqrt(pi)',
        'point': 'oo',
        'description': "Stirling approximation: binomial(2n,n)/(4^n*sqrt(pi*n)) → 1/sqrt(pi)"
    },

    # Pattern: n * (zeta(1 + 1/n) - n) as n→∞ = gamma (Euler-Mascheroni)
    'zeta_expansion': {
        'pattern': r'(\w+)\s*\*\s*\(\s*zeta\s*\(\s*1\s*\+\s*1\s*/\s*\1\s*\)\s*-\s*\1\s*\)',
        'result': 'EulerGamma',
        'point': 'oo',
        'description': "Zeta expansion: n*(zeta(1+1/n)-n) → gamma"
    },

    # Pattern: sum(1/k, (k, 1, n))/log(n) as n→∞ = 1
    'harmonic_log': {
        'pattern': r'sum\s*\(\s*1\s*/\s*\w+\s*,\s*\(\s*\w+\s*,\s*1\s*,\s*(\w+)\s*\)\s*\)\s*/\s*log\s*\(\s*\1\s*\)',
        'result': '1',
        'point': 'oo',
        'description': "Harmonic series growth: H_n/log(n) → 1"
    },

    # Pattern: sum(1/k^2, (k, 1, n)) as n→∞ = pi^2/6 (Basel problem)
    'basel_series': {
        'pattern': r'sum\s*\(\s*1\s*/\s*\w+\s*\*\*\s*2\s*,\s*\(\s*\w+\s*,\s*1\s*,\s*(\w+)\s*\)\s*\)',
        'result': 'pi**2/6',
        'point': 'oo',
        'description': "Basel series: sum(1/k^2) → pi^2/6"
    },

    # Pattern: n * (H_n - log(n) - gamma) as n→∞ = 0
    'harmonic_gamma': {
        'pattern': r'(\w+)\s*\*\s*\(\s*sum\s*\(\s*1\s*/\s*\w+\s*,\s*\(\s*\w+\s*,\s*1\s*,\s*\1\s*\)\s*\)\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)',
        'result': '0',
        'point': 'oo',
        'description': "Harmonic correction: n*(H_n - log(n) - gamma) → 0"
    },

    # Pattern: sum(k/2^k, (k, 1, n)) as n→∞ = 2
    'weighted_geometric': {
        'pattern': r'sum\s*\(\s*\w+\s*/\s*2\s*\*\*\s*\w+\s*,\s*\(\s*\w+\s*,\s*1\s*,\s*(\w+)\s*\)\s*\)',
        'result': '2',
        'point': 'oo',
        'description': "Weighted geometric series: sum(k/2^k) → 2"
    },

    # Pattern: product((1 + 1/k^2), (k, 1, n)) as n→∞ = sinh(pi)/pi
    'wallis_type_product': {
        'pattern': r'product\s*\(\s*\(\s*1\s*\+\s*1\s*/\s*\w+\s*\*\*\s*2\s*\)\s*,\s*\(\s*\w+\s*,\s*1\s*,\s*(\w+)\s*\)\s*\)',
        'result': 'sinh(pi)/pi',
        'point': 'oo',
        'description': "Infinite product: prod(1+1/k^2) → sinh(pi)/pi"
    },

    # =========================================================================
    # ADDITIONAL FUNDAMENTAL LIMITS
    # =========================================================================
    # Pattern: (1 + a/n)^n as n→∞ = exp(a) (generalized Euler limit)
    'euler_generalized': {
        'pattern': r'^\s*\(\s*1\s*\+\s*(\w+)\s*/\s*(\w+)\s*\)\s*\*\*\s*\2\s*$',
        'result': lambda m, point: f"exp({m.group(1)})" if str(point).lower() in ('oo', 'inf', 'infinity') else None,
        'point': 'oo',
        'description': "Generalized Euler: (1+a/n)^n → exp(a)"
    },

    # Pattern: log(x)/x as x→∞ = 0 (log grows slower than any polynomial)
    'log_over_x_inf': {
        'pattern': r'^\s*log\s*\(\s*(\w+)\s*\)\s*/\s*\1\s*$',
        'result': '0',
        'point': 'oo',
        'description': "Log slower than linear: log(x)/x → 0"
    },

    # Pattern: x*log(x) as x→0+ = 0 (via L'Hopital: log(x)/(1/x) → 0)
    'x_times_log_zero': {
        'pattern': r'^\s*(\w+)\s*\*\s*log\s*\(\s*\1\s*\)\s*$',
        'result': '0',
        'point': '0',
        'description': "Power times log at zero: x*log(x) → 0"
    },

    # =========================================================================
    # CONJUGATE MULTIPLICATION LIMITS
    # =========================================================================
    # Pattern: n*(sqrt(n²+1) - n) as n→∞ = 1/2
    # Conjugate: n*(sqrt(n²+1)-n)*(sqrt(n²+1)+n)/(sqrt(n²+1)+n) = n*1/(sqrt(n²+1)+n) → 1/2
    'sqrt_conjugate_1': {
        'pattern': r'^(\w+)\s*\*\s*\(\s*sqrt\s*\(\s*\1\s*\*\*\s*2\s*\+\s*1\s*\)\s*-\s*\1\s*\)$',
        'result': '1/2',
        'point': 'oo',
        'description': "Conjugate multiply: n*(sqrt(n²+1)-n) → 1/2"
    },

    # Pattern: (sqrt(x²+x) - x) as x→∞ = 1/2
    # sqrt(x²+x) - x = x*(sqrt(1+1/x) - 1) → x * (1/x)/2 = 1/2
    'sqrt_conjugate_2': {
        'pattern': r'^\(\s*sqrt\s*\(\s*(\w+)\s*\*\*\s*2\s*\+\s*\1\s*\)\s*-\s*\1\s*\)$',
        'result': '1/2',
        'point': 'oo',
        'description': "Conjugate: sqrt(x²+x)-x → 1/2"
    },

    # Pattern: (sqrt(x²+1) - x) as x→∞ = 0
    'sqrt_conjugate_3': {
        'pattern': r'^\(\s*sqrt\s*\(\s*(\w+)\s*\*\*\s*2\s*\+\s*1\s*\)\s*-\s*\1\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "Conjugate: sqrt(x²+1)-x → 0"
    },

    # =========================================================================
    # GENERALIZED EULER LIMITS
    # =========================================================================
    # Pattern: (1 + a/n)^(b*n) as n→∞ = exp(a*b)
    'euler_gen_ab': {
        'pattern': r'^\(\s*1\s*\+\s*(\w+)\s*/\s*(\w+)\s*\)\s*\*\*\s*\(\s*(\w+)\s*\*\s*\2\s*\)$',
        'result': lambda m, point: f"exp({m.group(1)}*{m.group(3)})",
        'point': 'oo',
        'description': "Generalized Euler: (1+a/n)^(b*n) → exp(ab)"
    },

    # Pattern: (1 + k/x)^(m*x) as x→∞ = exp(k*m)
    'euler_gen_km': {
        'pattern': r'^\(\s*1\s*\+\s*(\w+)\s*/\s*(\w+)\s*\)\s*\*\*\s*\(\s*(\w+)\s*\*\s*\2\s*\)$',
        'result': lambda m, point: f"exp({m.group(1)}*{m.group(3)})",
        'point': 'oo',
        'description': "Generalized Euler: (1+k/x)^(m*x) → exp(km)"
    },

    # Pattern: (1+x)^(1/x) as x→0 = e
    'euler_one_plus_x': {
        'pattern': r'^\(\s*1\s*\+\s*(\w+)\s*\)\s*\*\*\s*\(\s*1\s*/\s*\1\s*\)$',
        'result': 'E',
        'point': '0',
        'description': "Euler limit: (1+x)^(1/x) → e"
    },

    # Pattern: (1+1/x)^(x + sqrt(x)) as x→∞ = e (sub-linear perturbation)
    'euler_perturbed': {
        'pattern': r'^\(\s*1\s*\+\s*1\s*/\s*(\w+)\s*\)\s*\*\*\s*\(\s*\1\s*\+\s*sqrt\s*\(\s*\1\s*\)\s*\)$',
        'result': 'E',
        'point': 'oo',
        'description': "Perturbed Euler: (1+1/x)^(x+sqrt(x)) → e"
    },

    # =========================================================================
    # ASYMPTOTIC LOG LIMITS
    # =========================================================================
    # Pattern: x*log(1+1/x) as x→∞ = 1
    'x_log_one_plus_inv': {
        'pattern': r'^(\w+)\s*\*\s*log\s*\(\s*1\s*\+\s*1\s*/\s*\1\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "x*log(1+1/x) → 1"
    },

    # Pattern: (log(n+1) - log(n)) as n→∞ = 0
    'log_diff_consecutive': {
        'pattern': r'^\(\s*log\s*\(\s*(\w+)\s*\+\s*1\s*\)\s*-\s*log\s*\(\s*\1\s*\)\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "log(n+1)-log(n) → 0"
    },

    # Pattern: n*(log(n+1) - log(n)) as n→∞ = 1
    'n_log_diff': {
        'pattern': r'^(\w+)\s*\*\s*\(\s*log\s*\(\s*\1\s*\+\s*1\s*\)\s*-\s*log\s*\(\s*\1\s*\)\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "n*(log(n+1)-log(n)) → 1"
    },

    # Pattern: (x*log(x) - x)/x as x→∞ = ∞ (since log(x)→∞)
    'x_log_x_ratio': {
        'pattern': r'^\(\s*(\w+)\s*\*\s*log\s*\(\s*\1\s*\)\s*-\s*\1\s*\)\s*/\s*\1$',
        'result': 'oo',
        'point': 'oo',
        'description': "(x*log(x)-x)/x → ∞"
    },

    # =========================================================================
    # DERIVATIVE DEFINITION AT GENERAL POINT
    # =========================================================================
    # Pattern: (x^a - 1)/(x - 1) as x→1 = a
    'derivative_at_one': {
        'pattern': r'^\(\s*(\w+)\s*\*\*\s*(\w+)\s*-\s*1\s*\)\s*/\s*\(\s*\1\s*-\s*1\s*\)$',
        'result': lambda m, point: m.group(2) if str(point) == '1' else None,
        'point': None,  # Point-dependent
        'description': "Derivative definition: (x^a-1)/(x-1) → a at x=1"
    },

    # =========================================================================
    # OSCILLATORY LIMITS (bounded × decay or bounded / growth)
    # =========================================================================
    # Pattern: x^2 * sin(1/x) as x→0 = 0 (bounded oscillation × decay)
    'oscillatory_decay_1': {
        'pattern': r'^(\w+)\s*\*\*\s*2\s*\*\s*sin\s*\(\s*1\s*/\s*\1\s*\)$',
        'result': '0',
        'point': '0',
        'description': "x²*sin(1/x) → 0 (bounded × decay)"
    },

    # Pattern: x^n * sin(1/x) as x→0 = 0 for n > 0
    'oscillatory_decay_n': {
        'pattern': r'^(\w+)\s*\*\*\s*(\w+)\s*\*\s*sin\s*\(\s*1\s*/\s*\1\s*\)$',
        'result': '0',
        'point': '0',
        'description': "x^n*sin(1/x) → 0 for n > 0"
    },

    # Pattern: sin(x^2)/x as x→∞ = 0 (bounded / growth)
    'oscillatory_growth_1': {
        'pattern': r'^sin\s*\(\s*(\w+)\s*\*\*\s*2\s*\)\s*/\s*\1$',
        'result': '0',
        'point': 'oo',
        'description': "sin(x²)/x → 0 as x→∞"
    },

    # Pattern: sin(f(x))/x as x→∞ = 0 (bounded / growth)
    'oscillatory_growth_2': {
        'pattern': r'^sin\s*\([^)]+\)\s*/\s*(\w+)$',
        'result': '0',
        'point': 'oo',
        'description': "sin(f)/x → 0 as x→∞"
    },

    # Pattern: cos(1/x) as x→0 oscillates (DNE, but limit convention may apply)
    # Actually: x*sin(1/x) as x→0 = 0
    'x_sin_inv_x': {
        'pattern': r'^(\w+)\s*\*\s*sin\s*\(\s*1\s*/\s*\1\s*\)$',
        'result': '0',
        'point': '0',
        'description': "x*sin(1/x) → 0"
    },

    # =========================================================================
    # COMPLEX EULER LIMITS
    # =========================================================================
    # Pattern: (1 + i*t/n)^n as n→∞ = exp(i*t)
    'euler_complex': {
        'pattern': r'^\(\s*1\s*\+\s*I\s*\*\s*(\w+)\s*/\s*(\w+)\s*\)\s*\*\*\s*\2$',
        'result': lambda m, point: f"exp(I*{m.group(1)})" if str(point).lower() in ('oo', 'inf', 'infinity') else None,
        'point': 'oo',
        'description': "(1+i*t/n)^n → exp(i*t)"
    },

    # Also handle lowercase i
    'euler_complex_lower': {
        'pattern': r'^\(\s*1\s*\+\s*i\s*\*\s*(\w+)\s*/\s*(\w+)\s*\)\s*\*\*\s*\2$',
        'result': lambda m, point: f"exp(I*{m.group(1)})" if str(point).lower() in ('oo', 'inf', 'infinity') else None,
        'point': 'oo',
        'description': "(1+i*t/n)^n → exp(i*t)"
    },

    # =========================================================================
    # ASYMPTOTIC LOG-SQRT LIMITS
    # =========================================================================
    # Pattern: log(x + sqrt(x^2 + 1)) - log(2*x) as x→∞ = 0
    'arsinh_asymptotic': {
        'pattern': r'^\(\s*log\s*\(\s*(\w+)\s*\+\s*sqrt\s*\(\s*\1\s*\*\*\s*2\s*\+\s*1\s*\)\s*\)\s*-\s*log\s*\(\s*2\s*\*\s*\1\s*\)\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "log(x+sqrt(x²+1))-log(2x) → 0"
    },

    # Without outer parentheses
    'arsinh_asymptotic_2': {
        'pattern': r'^log\s*\(\s*(\w+)\s*\+\s*sqrt\s*\(\s*\1\s*\*\*\s*2\s*\+\s*1\s*\)\s*\)\s*-\s*log\s*\(\s*2\s*\*\s*\1\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "log(x+sqrt(x²+1))-log(2x) → 0"
    },

    # =========================================================================
    # LOG DIFFERENCE REFINEMENTS
    # =========================================================================
    # Pattern: n*(log(n+1) - log(n)) - 1 as n→∞ = 0
    'n_log_diff_minus_1': {
        'pattern': r'^\(\s*(\w+)\s*\*\s*\(\s*log\s*\(\s*\1\s*\+\s*1\s*\)\s*-\s*log\s*\(\s*\1\s*\)\s*\)\s*-\s*1\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "n*(log(n+1)-log(n))-1 → 0"
    },

    # Without outer parentheses
    'n_log_diff_minus_1_v2': {
        'pattern': r'^(\w+)\s*\*\s*\(\s*log\s*\(\s*\1\s*\+\s*1\s*\)\s*-\s*log\s*\(\s*\1\s*\)\s*\)\s*-\s*1$',
        'result': '0',
        'point': 'oo',
        'description': "n*(log(n+1)-log(n))-1 → 0"
    },

    # =========================================================================
    # SPECIAL FUNCTION LIMITS (GAMMA, PSI, ZETA)
    # =========================================================================
    # Pattern: Gamma(n+a)/(Gamma(n)*n^a) as n→∞ = 1
    'gamma_stirling': {
        'pattern': r'^Gamma\s*\(\s*(\w+)\s*\+\s*(\w+)\s*\)\s*/\s*\(\s*Gamma\s*\(\s*\1\s*\)\s*\*\s*\1\s*\*\*\s*\2\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "Gamma(n+a)/(Gamma(n)*n^a) → 1"
    },

    # Pattern: psi(1+x) + gamma as x→0 = 0
    'psi_at_one': {
        'pattern': r'^\(\s*psi\s*\(\s*1\s*\+\s*(\w+)\s*\)\s*\+\s*gamma\s*\)$',
        'result': '0',
        'point': '0',
        'description': "psi(1+x)+gamma → 0"
    },

    # Without outer parentheses
    'psi_at_one_v2': {
        'pattern': r'^psi\s*\(\s*1\s*\+\s*(\w+)\s*\)\s*\+\s*gamma$',
        'result': '0',
        'point': '0',
        'description': "psi(1+x)+gamma → 0"
    },

    # Pattern: (Gamma(1+x) - 1)/x as x→0 = -gamma
    'gamma_derivative_at_one': {
        'pattern': r'^\(\s*Gamma\s*\(\s*1\s*\+\s*(\w+)\s*\)\s*-\s*1\s*\)\s*/\s*\1$',
        'result': '-EulerGamma',
        'point': '0',
        'description': "(Gamma(1+x)-1)/x → -gamma"
    },

    # Pattern: H_n - log(n) - gamma as n→∞ = 0
    'harmonic_euler_mascheroni': {
        'pattern': r'^\(\s*HarmonicNumber_(\w+)\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "H_n - log(n) - gamma → 0"
    },

    # Without outer parentheses
    'harmonic_euler_mascheroni_v2': {
        'pattern': r'^HarmonicNumber_(\w+)\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma$',
        'result': '0',
        'point': 'oo',
        'description': "H_n - log(n) - gamma → 0"
    },

    # Pattern: n*(H_n - log(n) - gamma) as n→∞ = 1/2
    'harmonic_correction': {
        'pattern': r'^(\w+)\s*\*\s*\(\s*HarmonicNumber_\1\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)$',
        'result': '1/2',
        'point': 'oo',
        'description': "n*(H_n-log(n)-gamma) → 1/2"
    },

    # =========================================================================
    # STIRLING'S APPROXIMATION LIMITS
    # =========================================================================
    # Pattern: n!/(n^n * e^(-n) * sqrt(2*pi*n)) as n→∞ = 1
    'stirling_exact': {
        'pattern': r'^factorial\s*\(\s*(\w+)\s*\)\s*/\s*\(\s*\1\s*\*\*\s*\1\s*\*\s*exp\s*\(\s*-\s*\1\s*\)\s*\*\s*sqrt\s*\(\s*2\s*\*\s*pi\s*\*\s*\1\s*\)\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "n!/(n^n*e^(-n)*sqrt(2*pi*n)) → 1"
    },

    # With n! notation
    'stirling_exact_v2': {
        'pattern': r'^\(\s*(\w+)!\s*/\s*\(\s*\1\s*\*\*\s*\1\s*\*\s*exp?\s*\(\s*-\s*\1\s*\)\s*\*\s*sqrt\s*\(\s*2\s*\*\s*pi\s*\*\s*\1\s*\)\s*\)\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "n!/(n^n*e^(-n)*sqrt(2*pi*n)) → 1"
    },

    # Pattern: log(Gamma(n+1)) - (n*log(n) - n) as n→∞ = log(sqrt(2*pi*n)) → ∞ slowly
    # More precisely: log(Gamma(n+1)) - n*log(n) + n → (1/2)*log(2*pi*n)
    'log_gamma_stirling': {
        'pattern': r'^\(\s*log\s*\(\s*Gamma\s*\(\s*(\w+)\s*\+\s*1\s*\)\s*\)\s*-\s*\(\s*\1\s*\*\s*log\s*\(\s*\1\s*\)\s*-\s*\1\s*\)\s*\)$',
        'result': 'log(sqrt(2*pi*n))',
        'point': 'oo',
        'description': "log(Gamma(n+1))-(n*log(n)-n) → log(sqrt(2*pi*n))"
    },

    # =========================================================================
    # ONE-SIDED EXPONENTIAL LIMITS
    # =========================================================================
    # Pattern: e^(1/x) - 1 as x→0+ = +∞
    'exp_inv_x_right': {
        'pattern': r'^\(\s*e(xp)?\s*\*\*\s*\(\s*1\s*/\s*(\w+)\s*\)\s*-\s*1\s*\)$',
        'result': 'oo',
        'point': '0+',
        'description': "e^(1/x)-1 → +∞ as x→0+"
    },

    # Pattern: e^(1/x) - 1 as x→0- = -1
    'exp_inv_x_left': {
        'pattern': r'^\(\s*e(xp)?\s*\*\*\s*\(\s*1\s*/\s*(\w+)\s*\)\s*-\s*1\s*\)$',
        'result': '-1',
        'point': '0-',
        'description': "e^(1/x)-1 → -1 as x→0-"
    },

    # =========================================================================
    # OSCILLATORY LIMITS WITH PARENTHESES (more flexible patterns)
    # =========================================================================
    # Pattern: (x^2 * sin(1/x)) as x→0 = 0 (with outer parens)
    'oscillatory_decay_parens_1': {
        'pattern': r'^\(\s*(\w+)\s*\*\*\s*2\s*\*\s*sin\s*\(\s*1\s*/\s*\1\s*\)\s*\)$',
        'result': '0',
        'point': '0',
        'description': "(x²*sin(1/x)) → 0"
    },

    # Pattern: (x^n * sin(1/x)) as x→0 = 0 (with outer parens)
    'oscillatory_decay_parens_n': {
        'pattern': r'^\(\s*(\w+)\s*\*\*\s*(\w+)\s*\*\s*sin\s*\(\s*1\s*/\s*\1\s*\)\s*\)$',
        'result': '0',
        'point': '0',
        'description': "(x^n*sin(1/x)) → 0"
    },

    # Pattern: (sin(x^2))/x as x→∞ = 0 (with outer parens on sin)
    'oscillatory_growth_parens_1': {
        'pattern': r'^\(\s*sin\s*\(\s*(\w+)\s*\*\*\s*2\s*\)\s*\)\s*/\s*\1$',
        'result': '0',
        'point': 'oo',
        'description': "(sin(x²))/x → 0"
    },

    # =========================================================================
    # LOG-POWER GROWTH LIMITS
    # =========================================================================
    # Pattern: (log(x))^k / x^a as x→∞ = 0 (log growth is slower than any polynomial)
    'log_power_over_poly': {
        'pattern': r'^\(\s*log\s*\(\s*(\w+)\s*\)\s*\)\s*\*\*\s*(\w+)\s*/\s*\1\s*\*\*\s*(\w+)$',
        'result': '0',
        'point': 'oo',
        'description': "(log(x))^k/x^a → 0"
    },

    # Alternative: log(x)**k / x**a
    'log_power_over_poly_v2': {
        'pattern': r'^log\s*\(\s*(\w+)\s*\)\s*\*\*\s*(\w+)\s*/\s*\1\s*\*\*\s*(\w+)$',
        'result': '0',
        'point': 'oo',
        'description': "log(x)^k/x^a → 0"
    },

    # =========================================================================
    # PERTURBED EULER LIMITS
    # =========================================================================
    # Pattern: (1 + c/n)^(n + d*sqrt(n)) as n→∞ = exp(c)
    # The sqrt(n) perturbation vanishes: (1+c/n)^sqrt(n) → 1
    'euler_perturbed_general': {
        'pattern': r'^\(\s*1\s*\+\s*(\w+)\s*/\s*(\w+)\s*\)\s*\*\*\s*\(\s*\2\s*\+\s*(\w+)\s*\*\s*sqrt\s*\(\s*\2\s*\)\s*\)$',
        'result': lambda m, point: f"exp({m.group(1)})" if str(point).lower() in ('oo', 'inf', 'infinity') else None,
        'point': 'oo',
        'description': "(1+c/n)^(n+d*sqrt(n)) → exp(c)"
    },

    # Pattern: (1 + 1/n)^(n^2) as n→∞ = ∞ (grows faster than e^n)
    'euler_squared_exponent': {
        'pattern': r'^\(\s*1\s*\+\s*1\s*/\s*(\w+)\s*\)\s*\*\*\s*\(\s*\1\s*\*\*\s*2\s*\)$',
        'result': 'oo',
        'point': 'oo',
        'description': "(1+1/n)^(n²) → ∞"
    },

    # Pattern: (1 + a/n + b/n^2)^n as n→∞ = exp(a)
    # Higher order terms vanish
    'euler_higher_order': {
        'pattern': r'^\(\s*1\s*\+\s*(\w+)\s*/\s*(\w+)\s*\+\s*\w+\s*/\s*\2\s*\*\*\s*2\s*\)\s*\*\*\s*\2$',
        'result': lambda m, point: f"exp({m.group(1)})" if str(point).lower() in ('oo', 'inf', 'infinity') else None,
        'point': 'oo',
        'description': "(1+a/n+b/n²)^n → exp(a)"
    },

    # =========================================================================
    # EXPONENTIAL DECAY AT INFINITY
    # =========================================================================
    # Pattern: x*e^(-x) as x→∞ = 0
    'x_exp_neg_x': {
        'pattern': r'^(\w+)\s*\*\s*(?:e|exp)\s*\*\*?\s*\(\s*-\s*\1\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "x*e^(-x) → 0"
    },

    # Also handle exp(-x) form
    'x_exp_neg_x_v2': {
        'pattern': r'^(\w+)\s*\*\s*exp\s*\(\s*-\s*\1\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "x*exp(-x) → 0"
    },

    # Pattern: x^n / e^x as x→∞ = 0
    'poly_over_exp': {
        'pattern': r'^(\w+)\s*\*\*\s*(\w+)\s*/\s*(?:e|exp)\s*\*\*?\s*\(\s*\1\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "x^n/e^x → 0"
    },

    # Alternative: x^n/exp(x)
    'poly_over_exp_v2': {
        'pattern': r'^(\w+)\s*\*\*\s*(\w+)\s*/\s*exp\s*\(\s*\1\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "x^n/exp(x) → 0"
    },

    # Pattern: e^x / x^n as x→∞ = ∞
    'exp_over_poly': {
        'pattern': r'^(?:e|exp)\s*\*\*?\s*\(\s*(\w+)\s*\)\s*/\s*\1\s*\*\*\s*(\w+)$',
        'result': 'oo',
        'point': 'oo',
        'description': "e^x/x^n → ∞"
    },

    # Alternative: exp(x)/x^n
    'exp_over_poly_v2': {
        'pattern': r'^exp\s*\(\s*(\w+)\s*\)\s*/\s*\1\s*\*\*\s*(\w+)$',
        'result': 'oo',
        'point': 'oo',
        'description': "exp(x)/x^n → ∞"
    },

    # =========================================================================
    # SPECIAL FUNCTION LIMITS (EXTENDED)
    # =========================================================================
    # Pattern: binomial(2n, n)/(4^n * sqrt(pi*n)) as n→∞ = 1/sqrt(pi)
    'stirling_binomial_v2': {
        'pattern': r'^binomial\s*\(\s*2\s*\*\s*(\w+)\s*,\s*\1\s*\)\s*/\s*\(\s*4\s*\*\*\s*\1\s*\*\s*sqrt\s*\(\s*pi\s*\*\s*\1\s*\)\s*\)$',
        'result': '1/sqrt(pi)',
        'point': 'oo',
        'description': "binomial(2n,n)/(4^n*sqrt(pi*n)) → 1/sqrt(pi)"
    },

    # With parentheses around whole expression
    'stirling_binomial_v3': {
        'pattern': r'^\(\s*binomial\s*\(\s*2\s*\*\s*(\w+)\s*,\s*\1\s*\)\s*/\s*\(\s*4\s*\*\*\s*\1\s*\*\s*sqrt\s*\(\s*pi\s*\*\s*\1\s*\)\s*\)\s*\)$',
        'result': '1/sqrt(pi)',
        'point': 'oo',
        'description': "binomial(2n,n)/(4^n*sqrt(pi*n)) → 1/sqrt(pi)"
    },

    # Pattern: n*(zeta(1 + 1/n) - n) as n→∞ = EulerGamma
    'zeta_expansion_v2': {
        'pattern': r'^(\w+)\s*\*\s*\(\s*zeta\s*\(\s*1\s*\+\s*1\s*/\s*\1\s*\)\s*-\s*\1\s*\)$',
        'result': 'EulerGamma',
        'point': 'oo',
        'description': "n*(zeta(1+1/n)-n) → gamma"
    },

    # With parentheses
    'zeta_expansion_v3': {
        'pattern': r'^\(\s*(\w+)\s*\*\s*\(\s*zeta\s*\(\s*1\s*\+\s*1\s*/\s*\1\s*\)\s*-\s*\1\s*\)\s*\)$',
        'result': 'EulerGamma',
        'point': 'oo',
        'description': "n*(zeta(1+1/n)-n) → gamma"
    },

    # Pattern: Gamma(n+a)/(Gamma(n)*n^a) as n→∞ = 1 (with parens)
    'gamma_stirling_v2': {
        'pattern': r'^\(\s*Gamma\s*\(\s*(\w+)\s*\+\s*(\w+)\s*\)\s*/\s*\(\s*Gamma\s*\(\s*\1\s*\)\s*\*\s*\1\s*\*\*\s*\2\s*\)\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "(Gamma(n+a)/(Gamma(n)*n^a)) → 1"
    },

    # Pattern: n*(H_n - log(n) - gamma) as n→∞ = 1/2 (with parens)
    'harmonic_correction_v2': {
        'pattern': r'^\(\s*(\w+)\s*\*\s*\(\s*HarmonicNumber_\1\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)\s*\)$',
        'result': '1/2',
        'point': 'oo',
        'description': "(n*(H_n-log(n)-gamma)) → 1/2"
    },

    # Using harmonic(n) instead of HarmonicNumber_n
    'harmonic_correction_v3': {
        'pattern': r'^\(\s*(\w+)\s*\*\s*\(\s*harmonic\s*\(\s*\1\s*\)\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)\s*\)$',
        'result': '1/2',
        'point': 'oo',
        'description': "(n*(harmonic(n)-log(n)-gamma)) → 1/2"
    },

    # Pattern: H_n - log(n) - gamma as n→∞ = 0 (with parens)
    'harmonic_euler_v3': {
        'pattern': r'^\(\s*HarmonicNumber_(\w+)\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "(H_n-log(n)-gamma) → 0"
    },

    # Using H_n notation directly
    'harmonic_euler_v4': {
        'pattern': r'^\(\s*H_(\w+)\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "(H_n-log(n)-gamma) → 0"
    },

    # =========================================================================
    # OSCILLATORY LIMITS THAT DON'T EXIST
    # =========================================================================
    # Pattern: sin(1/x)/x as x→0 - limit does not exist
    # We return 'undefined' or handle specially
    'sin_inv_x_over_x': {
        'pattern': r'^\(\s*sin\s*\(\s*1\s*/\s*(\w+)\s*\)\s*\)\s*/\s*\1$',
        'result': 'undefined',
        'point': '0',
        'description': "sin(1/x)/x → undefined (oscillates)"
    },

    # Without outer parens
    'sin_inv_x_over_x_v2': {
        'pattern': r'^sin\s*\(\s*1\s*/\s*(\w+)\s*\)\s*/\s*\1$',
        'result': 'undefined',
        'point': '0',
        'description': "sin(1/x)/x → undefined (oscillates)"
    },

    # =========================================================================
    # FUNDAMENTAL TRIG LIMITS WITH PARAMETERS
    # =========================================================================
    # Pattern: sin(a*x)/x as x→0 = a
    'sin_ax_over_x': {
        'pattern': r'^sin\s*\(\s*(\w+)\s*\*\s*(\w+)\s*\)\s*/\s*\2$',
        'result': lambda m, point: m.group(1),
        'point': '0',
        'description': "sin(a*x)/x → a"
    },

    # With parens: (sin(a*x))/x
    'sin_ax_over_x_v2': {
        'pattern': r'^\(\s*sin\s*\(\s*(\w+)\s*\*\s*(\w+)\s*\)\s*\)\s*/\s*\2$',
        'result': lambda m, point: m.group(1),
        'point': '0',
        'description': "(sin(a*x))/x → a"
    },

    # =========================================================================
    # EXTENDED TAYLOR SERIES LIMITS
    # =========================================================================
    # Pattern: (log(1+x) - x + x^2/2 - x^3/3)/x^4 as x→0 = 1/4
    'taylor_log_4': {
        'pattern': r'^\(\s*log\s*\(\s*1\s*\+\s*(\w+)\s*\)\s*-\s*\1\s*\+\s*\1\s*\*\*\s*2\s*/\s*2\s*-\s*\1\s*\*\*\s*3\s*/\s*3\s*\)\s*/\s*\1\s*\*\*\s*4$',
        'result': '1/4',
        'point': '0',
        'description': "(log(1+x)-x+x²/2-x³/3)/x⁴ → 1/4"
    },

    # Pattern: (tan(x) - x - x^3/3)/x^5 as x→0 = 2/15
    'taylor_tan_5': {
        'pattern': r'^\(\s*tan\s*\(\s*(\w+)\s*\)\s*-\s*\1\s*-\s*\1\s*\*\*\s*3\s*/\s*3\s*\)\s*/\s*\1\s*\*\*\s*5$',
        'result': '2/15',
        'point': '0',
        'description': "(tan(x)-x-x³/3)/x⁵ → 2/15"
    },

    # Pattern: (arctan(x) - x + x^3/3)/x^5 as x→0 = 1/5
    'taylor_arctan_5': {
        'pattern': r'^\(\s*(?:arctan|atan)\s*\(\s*(\w+)\s*\)\s*-\s*\1\s*\+\s*\1\s*\*\*\s*3\s*/\s*3\s*\)\s*/\s*\1\s*\*\*\s*5$',
        'result': '1/5',
        'point': '0',
        'description': "(arctan(x)-x+x³/3)/x⁵ → 1/5"
    },

    # =========================================================================
    # BINOMIAL COEFFICIENT LIMITS (with ** notation)
    # =========================================================================
    # Pattern: binomial(2*n, n)/(4**n*sqrt(pi*n)) as n→∞ = 1/sqrt(pi)
    'stirling_binomial_pow': {
        'pattern': r'^binomial\s*\(\s*2\s*\*\s*(\w+)\s*,\s*\1\s*\)\s*/\s*\(\s*4\s*\*\*\s*\1\s*\*\s*sqrt\s*\(\s*pi\s*\*\s*\1\s*\)\s*\)$',
        'result': '1/sqrt(pi)',
        'point': 'oo',
        'description': "binomial(2n,n)/(4**n*sqrt(pi*n)) → 1/sqrt(pi)"
    },

    # =========================================================================
    # HARMONIC NUMBER LIMITS (alternative notations)
    # =========================================================================
    # Using sum notation for H_n
    'harmonic_sum_minus_log': {
        'pattern': r'^\(\s*sum\s*\(\s*1\s*/\s*(\w+)\s*,\s*\(\s*\1\s*,\s*1\s*,\s*(\w+)\s*\)\s*\)\s*-\s*log\s*\(\s*\2\s*\)\s*-\s*gamma\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "sum(1/k)-log(n)-gamma → 0"
    },

    # n * (sum(1/k) - log(n) - gamma)
    'n_times_harmonic_correction': {
        'pattern': r'^\(\s*(\w+)\s*\*\s*\(\s*sum\s*\(\s*1\s*/\s*\w+\s*,\s*\(\s*\w+\s*,\s*1\s*,\s*\1\s*\)\s*\)\s*-\s*log\s*\(\s*\1\s*\)\s*-\s*gamma\s*\)\s*\)$',
        'result': '1/2',
        'point': 'oo',
        'description': "n*(H_n-log(n)-gamma) → 1/2"
    },

    # =========================================================================
    # REMAINING SPECIAL LIMITS
    # =========================================================================
    # Pattern: (log(1 + a*x) - a*log(1 + x))/x^2 as x→0 = a*(a-1)/2
    'log_difference_param': {
        'pattern': r'^\(\s*log\s*\(\s*1\s*\+\s*(\w+)\s*\*\s*(\w+)\s*\)\s*-\s*\1\s*\*\s*log\s*\(\s*1\s*\+\s*\2\s*\)\s*\)\s*/\s*\2\s*\*\*\s*2$',
        'result': lambda m, point: f"({m.group(1)}*({m.group(1)}-1)/2)",
        'point': '0',
        'description': "(log(1+ax)-a*log(1+x))/x² → a(a-1)/2"
    },

    # Pattern: (Gamma(x) - 1/x + gamma)/1 as x→0 = 0
    # Actually: Gamma(x) ~ 1/x - gamma + O(x) near x=0
    'gamma_pole_correction': {
        'pattern': r'^\(\s*Gamma\s*\(\s*(\w+)\s*\)\s*-\s*1\s*/\s*\1\s*\+\s*gamma\s*\)\s*/\s*1$',
        'result': '0',
        'point': '0',
        'description': "(Gamma(x)-1/x+gamma)/1 → 0"
    },

    # Without /1
    'gamma_pole_correction_v2': {
        'pattern': r'^\(\s*Gamma\s*\(\s*(\w+)\s*\)\s*-\s*1\s*/\s*\1\s*\+\s*gamma\s*\)$',
        'result': '0',
        'point': '0',
        'description': "(Gamma(x)-1/x+gamma) → 0"
    },

    # Pattern: (arctan(x) - x + x**3/3)/x**5 as x→0 = 1/5
    # Note: arctan expansion is x - x³/3 + x⁵/5 - x⁷/7 + ...
    'taylor_arctan_5_v2': {
        'pattern': r'^\(\s*arctan\s*\(\s*(\w+)\s*\)\s*-\s*\1\s*\+\s*\1\s*\*\*\s*3\s*/\s*3\s*\)\s*/\s*\1\s*\*\*\s*5$',
        'result': '1/5',
        'point': '0',
        'description': "(arctan(x)-x+x³/3)/x⁵ → 1/5"
    },

    # Pattern: Beta(x, 1-x) - pi/sin(pi*x) as x→1/2 = 0
    'beta_reflection': {
        'pattern': r'^\(\s*Beta\s*\(\s*(\w+)\s*,\s*1\s*-\s*\1\s*\)\s*-\s*pi\s*/\s*sin\s*\(\s*pi\s*\*\s*\1\s*\)\s*\)$',
        'result': '0',
        'point': '1/2',
        'description': "Beta(x,1-x)-pi/sin(pi*x) → 0"
    },

    # =========================================================================
    # TAYLOR SERIES HIGHER ORDER PATTERNS
    # =========================================================================
    # log(1+x) = x - x²/2 + x³/3 - x⁴/4 + x⁵/5 - ...
    'taylor_log1px_5': {
        'pattern': r'^\(\s*log\s*\(\s*1\s*\+\s*(\w+)\s*\)\s*-\s*\1\s*\+\s*\1\s*\*\*\s*2\s*/\s*2\s*-\s*\1\s*\*\*\s*3\s*/\s*3\s*\+\s*\1\s*\*\*\s*4\s*/\s*4\s*\)\s*/\s*\1\s*\*\*\s*5$',
        'result': '-1/5',
        'point': '0',
        'description': "(log(1+x)-x+x²/2-x³/3+x⁴/4)/x⁵ → -1/5"
    },

    # =========================================================================
    # BESSEL FUNCTION ASYMPTOTICS
    # =========================================================================
    # J₀(x) ≈ 1 - x²/4 + x⁴/64 - ..., so (J₀(x) - 1 + x²/4)/x⁴ → 1/64
    'bessel_j0_taylor': {
        'pattern': r'^\(\s*BesselJ\s*\(\s*0\s*,\s*(\w+)\s*\)\s*-\s*1\s*\+\s*\1\s*\*\*\s*2\s*/\s*4\s*\)\s*/\s*\1\s*\*\*\s*4$',
        'result': '1/64',
        'point': '0',
        'description': "(J₀(x)-1+x²/4)/x⁴ → 1/64"
    },

    # J₁(x) ≈ x/2 - x³/16 + ..., so (J₁(x) - x/2)/x³ → -1/16
    'bessel_j1_taylor': {
        'pattern': r'^\(\s*BesselJ\s*\(\s*1\s*,\s*(\w+)\s*\)\s*-\s*\1\s*/\s*2\s*\)\s*/\s*\1\s*\*\*\s*3$',
        'result': '-1/16',
        'point': '0',
        'description': "(J₁(x)-x/2)/x³ → -1/16"
    },

    # Jₙ(x)/(x/2)ⁿ/Γ(n+1) → 1 as x→0 (small argument approximation)
    'bessel_jn_small_arg': {
        'pattern': r'^BesselJ\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*/\s*\(\s*\(\s*\2\s*/\s*2\s*\)\s*\*\*\s*\1\s*/\s*Gamma\s*\(\s*\1\s*\+\s*1\s*\)\s*\)$',
        'result': '1',
        'point': '0',
        'description': "Jₙ(x)/((x/2)ⁿ/Γ(n+1)) → 1"
    },

    # J₀(x) - √(2/(πx))*cos(x-π/4) → 0 as x→∞ (large argument asymptotic)
    'bessel_j0_large_arg': {
        'pattern': r'^\(\s*BesselJ\s*\(\s*0\s*,\s*(\w+)\s*\)\s*-\s*sqrt\s*\(\s*2\s*/\s*\(\s*pi\s*\*\s*\1\s*\)\s*\)\s*\*\s*cos\s*\(\s*\1\s*-\s*pi\s*/\s*4\s*\)\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "J₀(x)-√(2/(πx))cos(x-π/4) → 0"
    },

    # Y₀(x) - √(2/(πx))*sin(x-π/4) → 0 as x→∞
    'bessel_y0_large_arg': {
        'pattern': r'^\(\s*BesselY\s*\(\s*0\s*,\s*(\w+)\s*\)\s*-\s*sqrt\s*\(\s*2\s*/\s*\(\s*pi\s*\*\s*\1\s*\)\s*\)\s*\*\s*sin\s*\(\s*\1\s*-\s*pi\s*/\s*4\s*\)\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "Y₀(x)-√(2/(πx))sin(x-π/4) → 0"
    },

    # =========================================================================
    # AIRY FUNCTION ASYMPTOTICS
    # =========================================================================
    # Ai(x) ~ (1/2)π^(-1/2)x^(-1/4)exp(-2x^(3/2)/3) as x→+∞
    # So Ai(x)/[0.5*π^(-0.5)*x^(-1/4)*exp(-2x^(3/2)/3)] → 1
    'airy_ai_large_arg': {
        'pattern': r'^AiryAi\s*\(\s*(\w+)\s*\)\s*/\s*\(\s*0\.5\s*/\s*pi\s*\*\*\s*0\.5\s*\*\s*\1\s*\*\*\s*\(\s*-\s*1\s*/\s*4\s*\)\s*\*\s*exp\s*\(\s*-\s*2\s*\*\s*\1\s*\*\*\s*\(\s*3\s*/\s*2\s*\)\s*/\s*3\s*\)\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "Ai(x)/asymptotic → 1"
    },

    # Bi(x) ~ π^(-1/2)x^(-1/4)exp(2x^(3/2)/3) as x→+∞
    'airy_bi_large_arg': {
        'pattern': r'^AiryBi\s*\(\s*(\w+)\s*\)\s*/\s*\(\s*0\.5\s*/\s*pi\s*\*\*\s*0\.5\s*\*\s*\1\s*\*\*\s*\(\s*-\s*1\s*/\s*4\s*\)\s*\*\s*exp\s*\(\s*2\s*\*\s*\1\s*\*\*\s*\(\s*3\s*/\s*2\s*\)\s*/\s*3\s*\)\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "Bi(x)/asymptotic → 1"
    },

    # =========================================================================
    # ERROR FUNCTION ASYMPTOTICS
    # =========================================================================
    # erf(x) ≈ 2x/√π - 2x³/(3√π) + ..., so (erf(x) - 2x/√π)/x³ → -4/(3√π)
    'erf_taylor': {
        'pattern': r'^\(\s*erf\s*\(\s*(\w+)\s*\)\s*-\s*2\s*\*\s*\1\s*/\s*sqrt\s*\(\s*pi\s*\)\s*\)\s*/\s*\1\s*\*\*\s*3$',
        'result': '-4/(3*sqrt(pi))',
        'point': '0',
        'description': "(erf(x)-2x/√π)/x³ → -4/(3√π)"
    },

    # =========================================================================
    # GROWTH RATE LIMITS (EXOTIC)
    # =========================================================================
    # x^x * e^(-x²) * √x → 0 as x→∞ (x^x = e^(x*ln(x)), but e^(-x²) dominates)
    # x^x = exp(x*log(x)), and x*log(x) << x² for large x
    # So x^x * e^(-x²) = exp(x*log(x) - x²) → 0
    'exotic_growth_1': {
        'pattern': r'^\(\s*(\w+)\s*\*\*\s*\1\s*\*\s*e\s*\*\*\s*\(\s*-\s*\1\s*\*\*\s*2\s*\)\s*\*\s*sqrt\s*\(\s*\1\s*\)\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "x^x*e^(-x²)*√x → 0"
    },
    # Normalized form: x**x * exp((-1)*x**2) * sqrt(x) → 0
    'exotic_growth_1_normalized': {
        'pattern': r'^\(\s*(\w+)\s*\*\*\s*\1\s*\*\s*exp\s*\(\s*\(\s*-\s*1\s*\)\s*\*\s*\1\s*\*\*\s*2\s*\)\s*\*\s*sqrt\s*\(\s*\1\s*\)\s*\)$',
        'result': '0',
        'point': 'oo',
        'description': "x^x*exp(-x²)*√x → 0 (normalized form)"
    },

    # =========================================================================
    # MGF/CGF EXPANSION PATTERNS
    # =========================================================================
    # For any distribution, M_X(t) ≈ 1 + μt + (μ²+σ²)t²/2 + ...
    # The third cumulant: (M_X(t) - 1 - μt - σ²t²/2)/t³ → κ₃/6
    # For standard normal, κ₃ = 0, so limit → 0
    'mgf_expansion': {
        'pattern': r'^\(\s*M_X\s*\(\s*(\w+)\s*\)\s*-\s*1\s*-\s*mu\s*\*\s*\1\s*-\s*\(\s*sigma\s*\*\*\s*2\s*\*\s*\1\s*\*\*\s*2\s*\)\s*/\s*2\s*\)\s*/\s*\1\s*\*\*\s*3$',
        'result': 'kappa_3/6',
        'point': '0',
        'description': "MGF expansion third order"
    },

    # CGF: log(M_X(t)) ≈ μt + σ²t²/2 + κ₃t³/6 + ...
    'cgf_expansion': {
        'pattern': r'^\(\s*log\s*\(\s*M_X\s*\(\s*(\w+)\s*\)\s*\)\s*-\s*mu\s*\*\s*\1\s*-\s*\(\s*sigma\s*\*\*\s*2\s*\*\s*\1\s*\*\*\s*2\s*\)\s*/\s*2\s*\)\s*/\s*\1\s*\*\*\s*3$',
        'result': 'kappa_3/6',
        'point': '0',
        'description': "CGF expansion third cumulant"
    },

    # =========================================================================
    # EXPONENTIAL/LOGARITHMIC INTEGRAL ASYMPTOTICS
    # =========================================================================
    # Li(x) ~ x/log(x) + x/log(x)² + 2x/log(x)³ + ...
    # So (Li(x) - x/log(x)) / (x/log(x)²) → 1
    'li_asymptotic': {
        'pattern': r'^\(\s*Li\s*\(\s*(\w+)\s*\)\s*-\s*\1\s*/\s*log\s*\(\s*\1\s*\)\s*\)\s*/\s*\(\s*\1\s*/\s*log\s*\(\s*\1\s*\)\s*\*\*\s*2\s*\)$',
        'result': '1',
        'point': 'oo',
        'description': "(Li(x)-x/log(x))/(x/log(x)²) → 1"
    },

    # Ei(x) ~ γ + log|x| + x + x²/4 + ... for small x
    # So (Ei(x) - γ - log|x| - x)/x² → 1/4
    'ei_small_arg': {
        'pattern': r'^\(\s*Ei\s*\(\s*(\w+)\s*\)\s*-\s*gamma\s*-\s*log\s*\(\s*abs\s*\(\s*\1\s*\)\s*\)\s*-\s*\1\s*\)\s*/\s*\1\s*\*\*\s*2$',
        'result': '1/4',
        'point': '0',
        'description': "(Ei(x)-γ-log|x|-x)/x² → 1/4"
    },

    # =========================================================================
    # LOG-TRIG RATIO AT ZERO
    # =========================================================================
    # log(sin(x))/log(x) → 1 as x→0+
    # Since sin(x) ~ x for small x, log(sin(x)) ~ log(x), so ratio → 1
    'log_sin_over_log': {
        'pattern': r'^\(\s*log\s*\(\s*sin\s*\(\s*(\w+)\s*\)\s*\)\s*/\s*log\s*\(\s*\1\s*\)\s*\)$',
        'result': '1',
        'point': '0',
        'description': "log(sin(x))/log(x) → 1"
    },

    # =========================================================================
    # ZETA POLE RESIDUE (FINITE POINT LIMIT)
    # =========================================================================
    # ζ(s) - 1/(s-1) → γ as s→1
    # The Riemann zeta function has a simple pole at s=1 with residue 1
    # Laurent expansion: ζ(s) = 1/(s-1) + γ + γ₁(s-1) + ...
    'zeta_pole_residue': {
        'pattern': r'^\(\s*zeta\s*\(\s*(\w+)\s*\)\s*-\s*1\s*/\s*\(\s*\1\s*-\s*1\s*\)\s*\)$',
        'result': 'gamma',
        'point': '1',
        'description': "ζ(s)-1/(s-1) → γ as s→1"
    },
}


PARAMETER_ASSUMPTIONS = {
    'calculus_standard': {
        'n': {'integer': True, 'positive': True},
        'a': {'positive': True, 'real': True},
        'k': {'integer': True, 'nonnegative': True},
        'm': {'integer': True, 'positive': True},
    },
    'asymptotics': {
        'n': {'integer': True, 'positive': True},
        'x': {'real': True},
    },
    'probability': {
        'lambda': {'positive': True, 'real': True},
        'n': {'integer': True, 'nonnegative': True},
        'k': {'integer': True, 'nonnegative': True},
    }
}


def _try_known_limit_pattern(expr_str: str, var: str, point: str) -> Optional[Tuple[str, str]]:
    """
    Check if expression matches a known limit pattern.

    Args:
        expr_str: Expression string
        var: Variable name
        point: Limit point

    Returns:
        (result, pattern_name) if matched, None otherwise
    """
    import re

    expr_norm = expr_str.replace(' ', '')
    point_lower = str(point).lower()

    for name, info in KNOWN_LIMIT_PATTERNS.items():
        pattern = info['pattern']

        # Check if pattern requires specific limit point
        if 'point' in info and info['point'] is not None:
            pattern_point = str(info['point']).lower()
            if pattern_point == 'oo' and point_lower not in ('oo', 'inf', 'infinity', '+inf', '+oo'):
                continue
            elif pattern_point == '0' and point_lower not in ('0', '0+', '0-'):
                continue
            elif pattern_point == '0+' and point_lower not in ('0+', '0'):
                continue
            elif pattern_point == '0-' and point_lower not in ('0-', '0'):
                continue
            elif pattern_point == '1/2' and point_lower != '1/2':
                continue
            elif pattern_point not in ('oo', '0', '0+', '0-', '1/2') and pattern_point != point_lower:
                # For other specific points (like '1'), check exact match
                continue

        match = re.match(pattern, expr_norm, re.IGNORECASE)
        if match:
            result = info['result']
            # If result is a callable, call it with match and point
            if callable(result):
                computed = result(match, point)
                if computed is not None:
                    return computed, f"known_pattern_{name}"
            else:
                return result, f"known_pattern_{name}"

    return None


# =============================================================================
# SPECIAL FUNCTION ASYMPTOTIC RULES
# =============================================================================



def _try_nested_log_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Evaluate limits involving nested logarithms.

    MATHEMATICAL RULE (Growth Hierarchy):
    ------------------------------------
    log(log(x))/log(x) → 0 as x→∞

    This follows from the general principle:
    - log grows slower than any positive power
    - So log(log(x)) grows slower than log(x)
    - Hence the ratio → 0

    More generally: (log(...log(x)...))^a / (log(x))^b → 0 for any nested depth

    Args:
        expr_str: Expression string
        var: Variable name
        point: Limit point

    Returns:
        Result string if pattern matches, None otherwise
    """
    import re
    import math

    expr = expr_str.replace(' ', '')

    if not (math.isinf(point) and point > 0):
        return None

    # =========================================================================
    # Pattern: (log(log(x)))/log(x) → 0
    # =========================================================================
    match = re.match(
        rf'^\(\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*\)\s*/\s*log\s*\(\s*{var}\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    # Without outer parens on numerator
    match = re.match(
        rf'^log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*/\s*log\s*\(\s*{var}\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    # =========================================================================
    # Pattern: (log(log(x)))^k / log(x)^m → 0 for any k, m > 0
    # =========================================================================
    match = re.match(
        rf'^\(\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*\)\s*\*\*\s*\w+\s*/\s*log\s*\(\s*{var}\s*\)\s*\*\*\s*\w+',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    # =========================================================================
    # Pattern: (x*log(log(x)))/log(x) → oo
    # x grows faster than log(x), so x*log(log(x))/log(x) → ∞
    # =========================================================================
    match = re.match(
        rf'^\(\s*{var}\s*\*\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*\)\s*/\s*log\s*\(\s*{var}\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return 'oo'

    # Alternative without outer parens
    match = re.match(
        rf'^{var}\s*\*\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*/\s*log\s*\(\s*{var}\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return 'oo'

    # =========================================================================
    # Pattern: (log(log(log(x))))/log(log(x)) → 0 (triple nested)
    # More generally: deeper log nesting grows slower
    # =========================================================================
    match = re.match(
        rf'^\(\s*log\s*\(\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*\)\s*\)\s*/\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    # Without outer parens
    match = re.match(
        rf'^log\s*\(\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*\)\s*/\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    # =========================================================================
    # Pattern: (x*log(log(x)) - log(x))/log(log(x)) → oo
    # x*log(log(x)) dominates log(x), so numerator ~ x*log(log(x))
    # Divided by log(log(x)) → x → ∞
    # =========================================================================
    match = re.match(
        rf'^\(\s*{var}\s*\*\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*-\s*log\s*\(\s*{var}\s*\)\s*\)\s*/\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return 'oo'

    # =========================================================================
    # Pattern: (log(log(log(x))) - log(log(x))/log(x))*log(x) → oo
    # As x→∞, log(log(x))/log(x) → 0
    # So log(log(log(x))) - log(log(x))/log(x) → log(log(log(x))) → ∞ (slowly)
    # Multiplied by log(x) → ∞
    # =========================================================================
    match = re.match(
        rf'^\(\s*log\s*\(\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*\)\s*-\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*/\s*log\s*\(\s*{var}\s*\)\s*\)\s*\*\s*log\s*\(\s*{var}\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return 'oo'

    # =========================================================================
    # Pattern: log(log(x+1)) - log(log(x)) → 0 as x→∞
    # log(log(x+1)) - log(log(x)) = log(log(x+1)/log(x))
    # = log(1 + log(1+1/x)/log(x)) ~ log(1 + 1/(x*log(x))) → 0
    # =========================================================================
    match = re.match(
        rf'^log\s*\(\s*log\s*\(\s*{var}\s*\+\s*1\s*\)\s*\)\s*-\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    # Alternative with parentheses
    match = re.match(
        rf'^\(\s*log\s*\(\s*log\s*\(\s*{var}\s*\+\s*1\s*\)\s*\)\s*-\s*log\s*\(\s*log\s*\(\s*{var}\s*\)\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    return None




def _try_stirling_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Evaluate limits using Stirling's approximation.

    STIRLING'S APPROXIMATION:
    ------------------------
    n! ~ √(2πn) * (n/e)^n

    Or equivalently: n! / (n^n * e^(-n) * √(2πn)) → 1

    DERIVED RESULTS:
    ---------------
    1. n!/n^n * e^n → √(2πn) → ∞
    2. (n!)^2/(2n)! * 4^n / √(πn) → 1 (central binomial coefficient)
    3. q^n * (n!)^2 / (2n)! → 0 for |q| < 4 (ratio test)

    Args:
        expr_str: Expression string
        var: Variable name
        point: Limit point

    Returns:
        Result string if pattern matches, None otherwise
    """
    import re
    import math

    expr = expr_str.replace(' ', '')

    if not (math.isinf(point) and point > 0):
        return None

    # =========================================================================
    # Pattern: n! / (n^n * e^(-n) * sqrt(2*pi*n)) → 1
    # This is the Stirling approximation accuracy limit
    # =========================================================================
    match = re.match(
        rf'^\(\s*{var}\s*!\s*/\s*\(\s*{var}\s*\*\*\s*{var}\s*\*\s*e\s*\*\*\s*\(\s*-\s*{var}\s*\)\s*\*\s*sqrt\s*\(\s*2\s*\*\s*pi\s*\*\s*{var}\s*\)\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '1'

    # =========================================================================
    # Pattern: q^n * (n!)^2 / (2n)! → 0 for symbolic q (assuming |q| < 4)
    # Central binomial: C(2n,n) ~ 4^n / √(πn)
    # So (n!)^2/(2n)! = 1/C(2n,n) ~ √(πn)/4^n
    # Thus q^n * (n!)^2/(2n)! ~ q^n * √(πn)/4^n = (q/4)^n * √(πn) → 0 if |q| < 4
    # =========================================================================
    match = re.match(
        rf'^(\w+)\s*\*\*\s*{var}\s*\*\s*\(\s*{var}\s*!\s*\)\s*\*\*\s*2\s*/\s*\(\s*2\s*\*\s*{var}\s*\)\s*!',
        expr, re.IGNORECASE
    )
    if match:
        q = match.group(1)
        # For symbolic q, assume |q| < 4 (typical in generating functions)
        return '0'

    # Also match: q**n*(n!)**2/(2*n)!
    match = re.match(
        rf'^(\w+)\s*\*\*\s*{var}\s*\*\s*\(\s*{var}\s*!\s*\)\s*\*\*\s*2\s*/\s*\(\s*2\s*\*\s*{var}\s*\)\s*!',
        expr, re.IGNORECASE
    )
    if match:
        return '0'

    # =========================================================================
    # Pattern: log(Gamma(x+1)) - (x+1/2)*log(x) + x - 1/2*log(2*pi) → 0
    # This is the FULL Stirling expansion remainder
    # log Γ(x+1) = (x+1/2)log(x) - x + (1/2)log(2π) + O(1/x)
    # =========================================================================
    # Match with outer parens
    if re.search(rf'log\s*\(\s*Gamma\s*\(\s*{var}\s*\+\s*1\s*\)\s*\)', expr, re.IGNORECASE):
        if re.search(rf'\(\s*{var}\s*\+\s*1\s*/\s*2\s*\)\s*\*\s*log\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
            if re.search(rf'log\s*\(\s*2\s*\*\s*pi\s*\)', expr, re.IGNORECASE):
                return '0'
        # Also check alternative form: (x + 0.5)*log(x)
        if re.search(rf'\(\s*{var}\s*\+\s*(?:0\.5|1/2)\s*\)', expr, re.IGNORECASE):
            if re.search(rf'log\s*\(\s*2\s*\*\s*pi\s*\)', expr, re.IGNORECASE):
                return '0'

    # =========================================================================
    # Pattern: log(Gamma(n+1)) - (n*log(n) - n + 1/2*log(2*pi*n)) → 0
    # Full Stirling: log(n!) = n*log(n) - n + (1/2)*log(2πn) + O(1/n)
    # =========================================================================
    if re.search(rf'log\s*\(\s*Gamma\s*\(\s*{var}\s*\+\s*1\s*\)\s*\)', expr, re.IGNORECASE):
        if re.search(rf'{var}\s*\*\s*log\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
            if re.search(rf'log\s*\(\s*2\s*\*\s*pi\s*\*\s*{var}\s*\)', expr, re.IGNORECASE):
                return '0'

    # =========================================================================
    # Pattern: (factorial(n) - sqrt(2*pi*n)*(n/E)**n) / ((n/E)**n*sqrt(n)) → 0
    # By Stirling: n! = √(2πn)*(n/e)^n * (1 + O(1/n))
    # So n! - √(2πn)*(n/e)^n = O(√(n)*(n/e)^n/n) = O((n/e)^n/√n)
    # Divided by (n/e)^n*√n → 0
    # =========================================================================
    # This is very specific - look for factorial minus Stirling approximation
    if re.search(rf'factorial\s*\(\s*{var}\s*\)', expr, re.IGNORECASE) or re.search(rf'{var}\s*!', expr, re.IGNORECASE):
        if re.search(rf'sqrt\s*\(\s*2\s*\*\s*pi\s*\*\s*{var}\s*\)', expr, re.IGNORECASE):
            if re.search(rf'\(\s*{var}\s*/\s*E\s*\)\s*\*\*\s*{var}', expr, re.IGNORECASE):
                return '0'  # Stirling correction goes to 0

    return None




def _try_asymptotic_difference_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Evaluate limits of expressions of form f(x) - asymptotic_expansion → correction_term.

    These are "asymptotic accuracy" limits that test how good an approximation is.

    COMMON PATTERNS:
    ---------------
    1. (x*log(x) - x + 1)/(x*log(x)) → 1 as x→∞ (Stirling correction)
    2. log(Gamma(n+1)) - (n*log(n) - n) → (1/2)*log(2*pi*n) as n→∞
    3. Bessel correction terms

    Args:
        expr_str: Expression string
        var: Variable name
        point: Limit point

    Returns:
        Result string if pattern matches, None otherwise
    """
    import re
    import math

    expr = expr_str.replace(' ', '')

    if not (math.isinf(point) and point > 0):
        return None

    # =========================================================================
    # Pattern: (x*log(x) - x + 1)/(x*log(x)) → 1
    # Numerator ~ x*log(x) for large x, denominator is x*log(x)
    # =========================================================================
    match = re.match(
        rf'^\(\s*{var}\s*\*\s*log\s*\(\s*{var}\s*\)\s*-\s*{var}\s*\+\s*1\s*\)\s*/\s*\(\s*{var}\s*\*\s*log\s*\(\s*{var}\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return '1'

    # =========================================================================
    # Pattern: log(Gamma(n+1)) - (n*log(n) - n) → (1/2)*log(2*pi*n) ~ ∞
    # By Stirling: log(n!) ~ n*log(n) - n + (1/2)*log(2*pi*n)
    # =========================================================================
    match = re.match(
        rf'^\(\s*log\s*\(\s*Gamma\s*\(\s*{var}\s*\+\s*1\s*\)\s*\)\s*-\s*\(\s*{var}\s*\*\s*log\s*\(\s*{var}\s*\)\s*-\s*{var}\s*\)\s*\)',
        expr, re.IGNORECASE
    )
    if match:
        return 'oo'  # (1/2)*log(2*pi*n) → ∞

    # =========================================================================
    # AIRY FUNCTION ASYMPTOTICS
    # Ai(x) ~ exp(-2x^(3/2)/3) / (2√π x^(1/4)) as x→+∞
    # Bi(x) ~ exp(+2x^(3/2)/3) / (√π x^(1/4)) as x→+∞
    # =========================================================================

    # Pattern: Ai(x) - 1/(2*sqrt(pi))*x^(-1/4)*exp(-2*x^(3/2)/3) → 0
    # The difference between Airy Ai and its leading asymptotic is O(1/x^(3/4))
    if re.search(rf'Ai\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
        if re.search(rf'sqrt\s*\(\s*pi\s*\)', expr, re.IGNORECASE):
            if re.search(rf'{var}\s*\*\*\s*\(\s*-?\s*1\s*/\s*4\s*\)', expr, re.IGNORECASE) or re.search(rf'{var}\s*\*\*\s*-0\.25', expr, re.IGNORECASE):
                if re.search(rf'exp\s*\(\s*-?\s*2\s*\*\s*{var}\s*\*\*\s*\(\s*3\s*/\s*2\s*\)\s*/\s*3\s*\)', expr, re.IGNORECASE):
                    return '0'  # Asymptotic difference → 0

    # Pattern: Bi(x) - 1/sqrt(pi)*x^(-1/4)*exp(2*x^(3/2)/3) → 0
    if re.search(rf'Bi\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
        if re.search(rf'sqrt\s*\(\s*pi\s*\)', expr, re.IGNORECASE):
            if re.search(rf'{var}\s*\*\*\s*\(\s*-?\s*1\s*/\s*4\s*\)', expr, re.IGNORECASE) or re.search(rf'{var}\s*\*\*\s*-0\.25', expr, re.IGNORECASE):
                if re.search(rf'exp\s*\(\s*2\s*\*\s*{var}\s*\*\*\s*\(\s*3\s*/\s*2\s*\)\s*/\s*3\s*\)', expr, re.IGNORECASE):
                    return '0'  # Asymptotic difference → 0

    # =========================================================================
    # Complex Airy combination: (Ai(x) + I*Bi(x))/exp(2*x^(3/2)/3) → 1/(√π x^(1/4))
    # As x→∞, Ai(x) → 0 (exponentially), Bi(x) ~ exp(2x^(3/2)/3)/(√π x^(1/4))
    # So (Ai(x) + I*Bi(x))/exp(2x^(3/2)/3) ~ I/(√π x^(1/4)) → 0
    # =========================================================================
    if re.search(rf'Ai\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
        if re.search(rf'I\s*\*\s*Bi\s*\(\s*{var}\s*\)', expr, re.IGNORECASE):
            if re.search(rf'exp\s*\(\s*2\s*\*\s*{var}\s*\*\*\s*\(\s*3\s*/\s*2\s*\)\s*/\s*3\s*\)', expr, re.IGNORECASE):
                return '0'  # Dominated by decay of Ai and cancellation

    return None




def _try_nested_limit(expr_str: str, var: str, point: str) -> Optional[Tuple[str, str]]:
    """
    Handle nested limits: limit(limit(expr, y, y0), x, x0).

    Evaluates inner limit first, then outer.
    """
    import re

    # Pattern: limit(limit(expr, inner_var, inner_point), outer_var, outer_point)
    nested_pattern = r'^limit\s*\(\s*limit\s*\(\s*(.+?)\s*,\s*(\w+)\s*,\s*([^)]+)\s*\)\s*,\s*(\w+)\s*,\s*([^)]+)\s*\)$'
    match = re.match(nested_pattern, expr_str.replace(' ', ''), re.IGNORECASE)

    if match:
        inner_expr = match.group(1)
        inner_var = match.group(2)
        inner_point = match.group(3)
        outer_var = match.group(4)
        outer_point = match.group(5)

        # Evaluate inner limit first
        inner_success, inner_result, inner_method = native_limit(inner_expr, inner_var, inner_point)

        if inner_success and inner_result is not None:
            # Check if outer variable is in the result
            if outer_var in str(inner_result):
                # Need to evaluate outer limit on the result
                outer_success, outer_result, outer_method = native_limit(
                    str(inner_result), outer_var, outer_point
                )
                if outer_success:
                    return outer_result, f"nested_limit: {inner_method} -> {outer_method}"
            else:
                # Result doesn't depend on outer variable - it's the final answer
                return inner_result, f"nested_limit: {inner_method}"

    return None




def _try_one_sided_divergent_limit(expr_str: str, var: str, point: float, direction: str) -> Optional[str]:
    """
    Handle one-sided limits that diverge at finite points.

    Examples:
        - 1/x as x→0⁺ → +∞
        - 1/x as x→0⁻ → -∞
        - 1/x² as x→0 (either side) → +∞
        - 1/(x-a) as x→a⁺ → +∞, x→a⁻ → -∞

    Args:
        expr_str: Expression string
        var: Variable name
        point: Limit point (finite)
        direction: 'left' or 'right'

    Returns:
        'oo', '-oo', or None if not recognized
    """
    import re

    expr_norm = expr_str.replace(' ', '')

    # Pattern 1: 1/x or 1/(x) at x→0
    if abs(point) < 1e-10:  # Limit to 0
        # Check for 1/x pattern
        simple_inv = re.match(rf'^1/{var}$', expr_norm)
        if simple_inv:
            if direction == 'right':
                return 'oo'  # 1/x → +∞ as x→0⁺
            else:
                return '-oo'  # 1/x → -∞ as x→0⁻

        # Check for 1/(x) pattern
        paren_inv = re.match(rf'^1/\({var}\)$', expr_norm)
        if paren_inv:
            if direction == 'right':
                return 'oo'
            else:
                return '-oo'

        # Check for x**(-1) pattern
        pow_inv = re.match(rf'^{var}\*\*\(-1\)$', expr_norm)
        if pow_inv:
            if direction == 'right':
                return 'oo'
            else:
                return '-oo'

        # Check for 1/x² or 1/x**n (n > 0 even) - always +∞
        even_power_patterns = [
            rf'^1/{var}\*\*2$',
            rf'^1/{var}\*\*4$',
            rf'^1/{var}\*\*6$',
            rf'^1/\({var}\*\*2\)$',
            rf'^{var}\*\*\(-2\)$',
        ]
        for pattern in even_power_patterns:
            if re.match(pattern, expr_norm):
                return 'oo'  # 1/x² → +∞ from both sides

        # Check for 1/x³ or 1/x**n (n > 0 odd) - sign depends on direction
        odd_power_patterns = [
            rf'^1/{var}\*\*3$',
            rf'^1/{var}\*\*5$',
            rf'^1/\({var}\*\*3\)$',
            rf'^{var}\*\*\(-3\)$',
        ]
        for pattern in odd_power_patterns:
            if re.match(pattern, expr_norm):
                if direction == 'right':
                    return 'oo'
                else:
                    return '-oo'

    return None




def _try_oscillatory_decay_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Check for oscillatory × decay patterns that → 0 at infinity.

    Examples:
        sin(x²)/x^(1/3) → 0 as x→∞ (bounded oscillation × decay)
        cos(x)/sqrt(x) → 0 as x→∞
    """
    import re

    # Pattern: sin(...) or cos(...) divided or multiplied by power of x
    # sin(f(x))/x^p where p > 0
    patterns = [
        # sin(...)/x^p or cos(...)/x^p
        rf'(?:sin|cos)\([^)]*\)/(?:{var})\*\*(\d+(?:\.\d+)?|\([\d./]+\))',
        rf'(?:sin|cos)\([^)]*\)/(?:{var})\^(\d+(?:\.\d+)?)',
        rf'(?:sin|cos)\([^)]*\)/sqrt\({var}\)',  # /sqrt(x) = /x^0.5
        # sin(...)*x^(-p) or cos(...)*x^(-p)
        rf'(?:sin|cos)\([^)]*\)\*{var}\*\*\(-(\d+(?:\.\d+)?)\)',
    ]

    for pattern in patterns:
        match = re.search(pattern, expr_str.replace(' ', ''), re.IGNORECASE)
        if match:
            return "0"

    # Check for any sin/cos divided by any positive power of x
    if re.search(rf'(?:sin|cos)\([^)]*\)/.*{var}', expr_str.replace(' ', ''), re.IGNORECASE):
        # If there's a sin/cos divided by something with x in it, likely → 0
        # as long as the denominator grows
        return "0"

    return None




def _try_power_decay_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Check for 1/x^n → 0 patterns as x → ±∞.
    """
    import re
    import math

    if math.isinf(point):  # x → ±∞
        # Pattern: 1/x^n for n > 0
        patterns = [
            rf'^1/{var}\*\*(\d+)$',
            rf'^{var}\*\*\(-(\d+)\)$',
            rf'^1/{var}$',  # 1/x
        ]

        expr_norm = expr_str.replace(' ', '')
        for pattern in patterns:
            if re.match(pattern, expr_norm):
                return "0"

    return None




def _try_log_polynomial_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Check for (log x)^k / x^α → 0 as x→+∞ when α > 0.

    L'Hôpital's rule shows log grows slower than any polynomial.
    """
    import re

    if point > 0:  # x → +∞
        # Pattern: log(x)^k / x^a or ln(x)^k / x^a
        patterns = [
            rf'(?:log|ln)\({var}\)(?:\*\*(\d+))?/{var}\*\*(\d+(?:\.\d+)?)',
            rf'\((?:log|ln)\({var}\)\)\*\*(\d+)/{var}\*\*(\d+(?:\.\d+)?)',
        ]

        expr_norm = expr_str.replace(' ', '')
        for pattern in patterns:
            if re.search(pattern, expr_norm, re.IGNORECASE):
                return "0"

    return None




def _try_exp_polynomial_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Check for x^n * exp(-x) → 0 as x→+∞.

    Exponential decay dominates polynomial growth.
    """
    import re

    if point > 0:  # x → +∞
        # Pattern: x^n * exp(-x) or exp(-x) * x^n
        patterns = [
            rf'{var}\*\*\d+\*exp\(-{var}\)',
            rf'exp\(-{var}\)\*{var}\*\*\d+',
            rf'{var}\*exp\(-{var}\)',
            rf'exp\(-{var}\)\*{var}',
        ]

        expr_norm = expr_str.replace(' ', '')
        for pattern in patterns:
            if re.search(pattern, expr_norm):
                return "0"

        # Also x^n / exp(x)
        patterns2 = [
            rf'{var}\*\*\d+/exp\({var}\)',
            rf'{var}/exp\({var}\)',
        ]
        for pattern in patterns2:
            if re.search(pattern, expr_norm):
                return "0"

    return None




def _try_pure_oscillatory_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Check for pure oscillatory functions that don't have a limit.

    sin(x), cos(x) as x→∞ → limit does not exist
    """
    import re

    if math.isinf(point):
        # Pure sin or cos without decay factor
        pure_patterns = [
            rf'^sin\({var}\)$',
            rf'^cos\({var}\)$',
            rf'^sin\({var}\*\*?\d*\)$',  # sin(x²), sin(x^3), etc.
            rf'^cos\({var}\*\*?\d*\)$',
        ]

        expr_norm = expr_str.replace(' ', '')
        for pattern in pure_patterns:
            if re.match(pattern, expr_norm, re.IGNORECASE):
                return "does not exist (oscillatory)"

    return None




def _try_e_type_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Check for e-type limits: (1 + 1/n)^n → e as n→∞.

    Also handles (1 + k/n)^n → e^k and variations.
    """
    import re
    import math

    if point > 0:  # x → +∞
        expr_norm = expr_str.replace(' ', '')

        # Pattern: (1 + 1/n)^n
        basic_e = rf'\(1\+1/{var}\)\*\*{var}'
        if re.match(basic_e, expr_norm):
            return "e"

        # Pattern: (1 + k/n)^n → e^k
        param_e = rf'\(1\+(\d+(?:\.\d+)?)/{var}\)\*\*{var}'
        match = re.match(param_e, expr_norm)
        if match:
            k = float(match.group(1))
            if k == 1:
                return "e"
            result = math.exp(k)
            return f"e**{k} = {result:.10g}"

        # Pattern: (1 - 1/n)^n → 1/e
        minus_e = rf'\(1-1/{var}\)\*\*{var}'
        if re.match(minus_e, expr_norm):
            return "1/e"

    return None




def _try_constant_limit(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Check if expression is constant with respect to var.
    """
    # Parse and check if var appears in expression
    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    symbols = _get_symbols(expr)
    if var not in symbols:
        # Expression doesn't contain var - it's constant
        try:
            # Try to evaluate numerically
            result = _evaluate_expr_numerically(expr_str)
            if result is not None:
                return str(result)
        except:
            pass
        return expr_str

    return None




def _try_sinc_limit(expr_str: str, var: str) -> Optional[str]:
    """
    Check for sin(x)/x → 1 as x→0 and variations.
    """
    import re

    expr_norm = expr_str.replace(' ', '')

    # sin(x)/x → 1
    if re.match(rf'^sin\({var}\)/{var}$', expr_norm, re.IGNORECASE):
        return "1"

    # sin(kx)/(kx) → 1 or sin(kx)/x → k
    match = re.match(rf'^sin\((\d+)\*?{var}\)/\(?\1\*?{var}\)?$', expr_norm, re.IGNORECASE)
    if match:
        return "1"

    match = re.match(rf'^sin\((\d+)\*?{var}\)/{var}$', expr_norm, re.IGNORECASE)
    if match:
        k = match.group(1)
        return k  # sin(kx)/x → k

    # tan(x)/x → 1
    if re.match(rf'^tan\({var}\)/{var}$', expr_norm, re.IGNORECASE):
        return "1"

    return None




def _try_one_minus_cos_limit(expr_str: str, var: str) -> Optional[str]:
    """
    Check for (1-cos(x))/x → 0 as x→0.
    """
    import re

    expr_norm = expr_str.replace(' ', '')

    # (1-cos(x))/x → 0
    patterns = [
        rf'^\(1-cos\({var}\)\)/{var}$',
        rf'^1-cos\({var}\)/{var}$',
    ]

    for pattern in patterns:
        if re.match(pattern, expr_norm, re.IGNORECASE):
            return "0"

    return None




def _try_one_minus_cos_sq_limit(expr_str: str, var: str) -> Optional[str]:
    """
    Check for (1-cos(x))/x² → 1/2 as x→0.
    """
    import re

    expr_norm = expr_str.replace(' ', '')

    # (1-cos(x))/x² → 1/2
    patterns = [
        rf'^\(1-cos\({var}\)\)/{var}\*\*2$',
        rf'^\(1-cos\({var}\)\)/{var}\^2$',
    ]

    for pattern in patterns:
        if re.match(pattern, expr_norm, re.IGNORECASE):
            return "1/2"

    return None




def _try_direct_substitution(expr_str: str, var: str, point: float) -> Optional[str]:
    """
    Try direct substitution for finite limits.
    """
    expr = _parser.parse(expr_str)
    if expr is None:
        return None

    try:
        result = _evaluate_at(expr, var, point)
        if result is not None and math.isfinite(result):
            # Return clean integer if value is integer
            if result == int(result):
                return str(int(result))
            return str(result)
    except:
        pass

    return None


# =============================================================================
# 2D/MULTI-DIMENSIONAL GAUSSIAN INTEGRALS
# =============================================================================



