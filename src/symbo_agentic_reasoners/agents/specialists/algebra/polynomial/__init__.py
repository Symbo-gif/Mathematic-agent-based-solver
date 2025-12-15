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
- numeric_roots: Newton-Raphson and multi-root finding
- rational_equations: Rational root theorem and rational equation clearing
- domain_solver: DomainPolynomialSolver routing class
- polynomial_agent: PolynomialSpecialist BDI agent

Main Exports:
- DomainPolynomialSolver: Domain-first polynomial solver class
- PolynomialSpecialist: BDI agent for polynomial operations
"""

# Import main classes for backward compatibility
from .domain_solver import DomainPolynomialSolver
from .polynomial_agent import PolynomialSpecialist

# Export main classes
__all__ = [
    'DomainPolynomialSolver',
    'PolynomialSpecialist',
]
