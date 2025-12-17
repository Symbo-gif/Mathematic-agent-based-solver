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
Polynomial Specialist Package
==============================

This package contains the decomposed polynomial specialist modules:

Sub-Specialists:
- polynomial_solvers: Degree-specific solving (linear, quadratic, cubic, quartic)
- polynomial_factors: Pattern-based factoring (difference of squares, cubes, GCD)
- numeric_roots: Newton-Raphson, bisection, secant, Brent's method root finding
- rational_equations: Rational root theorem and rational equation clearing
- domain_solver: DomainPolynomialSolver routing class
- polynomial_agent: PolynomialSpecialist BDI agent

Main Exports:
- DomainPolynomialSolver: Domain-first polynomial solver class
- PolynomialSpecialist: BDI agent for polynomial operations

Numeric Root Finding:
- newton_raphson: Newton-Raphson iteration
- bisection_method: Guaranteed convergence bracketing method
- secant_method: Derivative-free Newton alternative
- brent_method: Hybrid robust root finder (best general-purpose)
- find_root: Auto-selecting general root finder
- find_all_numeric_roots: Multi-root finder with deflation
"""

# Import main classes for backward compatibility
from .domain_solver import DomainPolynomialSolver
from .polynomial_agent import PolynomialSpecialist

# Import numeric root finding methods
from .numeric_roots import (
    newton_raphson,
    find_all_numeric_roots,
    bisection_method,
    secant_method,
    brent_method,
    find_root,
    poly_coeffs_to_func,
)

# Import polynomial GCD operations
from .polynomial_gcd import (
    polynomial_gcd,
    polynomial_divmod,
    extended_euclidean,
    resultant,
    subresultant_prs,
    content,
    primitive_part,
    polynomial_multiply,
    polynomial_subtract,
)

# Export main classes
__all__ = [
    'DomainPolynomialSolver',
    'PolynomialSpecialist',
    # Numeric root finding
    'newton_raphson',
    'find_all_numeric_roots',
    'bisection_method',
    'secant_method',
    'brent_method',
    'find_root',
    'poly_coeffs_to_func',
    # Polynomial GCD operations
    'polynomial_gcd',
    'polynomial_divmod',
    'extended_euclidean',
    'resultant',
    'subresultant_prs',
    'content',
    'primitive_part',
    'polynomial_multiply',
    'polynomial_subtract',
]
