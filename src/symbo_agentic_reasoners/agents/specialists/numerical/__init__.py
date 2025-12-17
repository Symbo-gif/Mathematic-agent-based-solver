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
Numerical Specialists Package
==============================

Provides comprehensive numerical computation specialists:
- NumericalMethodsSpecialist: Core numerical methods (integration, ODE, root finding)
- OptimizationSpecialist: Numerical optimization (BFGS, CG, Nelder-Mead)
- SplineSpecialist: Spline interpolation (cubic, Akima, PCHIP)
- LinearSystemsSpecialist: Iterative solvers (Jacobi, Gauss-Seidel, CG, GMRES)
- PDESpecialist: Partial differential equations (heat, wave, Laplace)

Key Features:
- Numerical integration (Simpson, Romberg, Gaussian, adaptive)
- Numerical differentiation (forward, central, Richardson)
- ODE solving (Euler, RK4, RK45 adaptive)
- Root finding (bisection, Newton, Brent)
- Interpolation (Lagrange, Newton, linear, spline)
- Optimization (gradient descent, BFGS, L-BFGS, Nelder-Mead, CG)
- Iterative linear solvers (Jacobi, Gauss-Seidel, SOR, CG, GMRES)
- PDE solvers (heat, wave, Laplace, Poisson, advection)
"""

from .numerical_methods_specialist import (
    NumericalMethodsSpecialist,
    IntegrationResult,
    ODESolution,
    InterpolationResult,
    numerical_integrate,
    numerical_derivative,
    solve_ode,
)

from .optimization_specialist import (
    OptimizationSpecialist,
    OptimizationResult,
)

from .spline_specialist import (
    SplineSpecialist,
    SplineResult,
)

from .linear_systems_specialist import (
    LinearSystemsSpecialist,
    LinearSystemResult,
)

from .pde_specialist import (
    PDESpecialist,
    PDESolution as PDESolutionResult,
)

from .advanced_quadrature_specialist import (
    AdvancedQuadratureSpecialist,
    QuadratureResult,
)

__all__ = [
    # Legacy
    "numerical_utility",
    # Core numerical methods
    "NumericalMethodsSpecialist",
    "IntegrationResult",
    "ODESolution",
    "InterpolationResult",
    "numerical_integrate",
    "numerical_derivative",
    "solve_ode",
    # Optimization
    "OptimizationSpecialist",
    "OptimizationResult",
    # Spline interpolation
    "SplineSpecialist",
    "SplineResult",
    # Linear systems
    "LinearSystemsSpecialist",
    "LinearSystemResult",
    # PDE solvers
    "PDESpecialist",
    "PDESolutionResult",
    # Advanced quadrature
    "AdvancedQuadratureSpecialist",
    "QuadratureResult",
]