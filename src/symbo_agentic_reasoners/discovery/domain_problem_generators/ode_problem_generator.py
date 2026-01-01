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
ODE Problem Generator
=====================

Generates research-level differential equation problems for autonomous exploration.

PROBLEM TYPES:
--------------
1. First-order ODEs (separable, exact, Bernoulli, Riccati)
2. Second-order ODEs (constant/variable coefficients, series solutions)
3. Systems of ODEs (linear, nonlinear, stability analysis)
4. Boundary value problems
5. Stiff systems and numerical challenges

DIFFICULTY SCALING:
-------------------
- Level 1: Standard textbook problems
- Level 2: Non-trivial coefficient functions
- Level 3: Singularities and special functions
- Level 4: Research-level (chaotic systems, exotic behavior)
"""

import random
import numpy as np
from typing import Dict, Any, List


class ODEProblemGenerator:
    """Generate differential equation problems for autonomous exploration."""

    def __init__(self, difficulty_range=(1, 4)):
        self.difficulty_min, self.difficulty_max = difficulty_range
        self.problem_count = 0

    def generate_problem(self, difficulty: int = None) -> Dict[str, Any]:
        """
        Generate random ODE problem.

        Args:
            difficulty: Difficulty level (1-4), random if None

        Returns:
            Dict with problem specification
        """
        if difficulty is None:
            difficulty = random.randint(self.difficulty_min, self.difficulty_max)

        problem_types = [
            self._generate_first_order,
            self._generate_second_order,
            self._generate_system,
            self._generate_series_solution,
            self._generate_bvp
        ]

        generator = random.choice(problem_types)
        problem = generator(difficulty)
        problem['difficulty'] = difficulty
        problem['problem_id'] = f'ODE_{self.problem_count:04d}'
        self.problem_count += 1

        return problem

    def _generate_first_order(self, difficulty: int) -> Dict[str, Any]:
        """Generate first-order ODE problems."""
        if difficulty == 1:
            # Standard separable
            return {
                'type': 'first_order_separable',
                'ode': "dy/dx = x*y",
                'initial_condition': {'x': 0, 'y': 1},
                'expected_solution': 'y = exp(x²/2)',
                'method': 'separation_of_variables'
            }
        elif difficulty == 2:
            # Bernoulli equation
            return {
                'type': 'first_order_bernoulli',
                'ode': f"dy/dx + y/x = y^2*x",
                'initial_condition': {'x': 1, 'y': 1},
                'n': 2,
                'method': 'bernoulli_substitution'
            }
        elif difficulty == 3:
            # Exact equation with interesting M, N
            return {
                'type': 'first_order_exact',
                'ode': "(2xy + y²)dx + (x² + 2xy)dy = 0",
                'method': 'exact_or_integrating_factor'
            }
        else:
            # Riccati with tricky particular solution
            return {
                'type': 'first_order_riccati',
                'ode': "dy/dx = 1 + x² - 2xy + y²",
                'particular_solution': 'y = x',
                'method': 'riccati_with_particular_solution'
            }

    def _generate_second_order(self, difficulty: int) -> Dict[str, Any]:
        """Generate second-order ODE problems."""
        if difficulty == 1:
            return {
                'type': 'second_order_constant_coeff',
                'ode': "y'' - 3y' + 2y = 0",
                'characteristic_roots': [1, 2],
                'method': 'characteristic_equation'
            }
        elif difficulty == 2:
            # Non-homogeneous
            return {
                'type': 'second_order_nonhomogeneous',
                'ode': "y'' + 4y = sin(x)",
                'method': 'undetermined_coefficients'
            }
        elif difficulty == 3:
            # Variable coefficients - Cauchy-Euler
            return {
                'type': 'cauchy_euler',
                'ode': "x²y'' + xy' - y = 0",
                'method': 'power_substitution'
            }
        else:
            # Bessel equation (requires series solution)
            order = random.randint(0, 3)
            return {
                'type': 'bessel_equation',
                'ode': f"x²y'' + xy' + (x² - {order}²)y = 0",
                'order': order,
                'method': 'frobenius_series',
                'solution_type': 'bessel_function'
            }

    def _generate_system(self, difficulty: int) -> Dict[str, Any]:
        """Generate system of ODEs."""
        if difficulty <= 2:
            # Simple 2x2 linear system
            eigenvalues = [random.choice([-2, -1, 1, 2]) for _ in range(2)]
            return {
                'type': 'linear_system_2x2',
                'system': 'dX/dt = AX',
                'eigenvalues': eigenvalues,
                'stability': 'stable' if all(e < 0 for e in eigenvalues) else 'unstable',
                'method': 'matrix_exponential'
            }
        elif difficulty == 3:
            # Nonlinear system - predator-prey
            return {
                'type': 'nonlinear_system',
                'system': ['dx/dt = ax - bxy', 'dy/dt = -cy + dxy'],
                'params': {'a': 1.0, 'b': 0.1, 'c': 1.5, 'd': 0.075},
                'analysis': 'phase_plane',
                'method': 'nullclines_and_stability'
            }
        else:
            # Chaotic system - Lorenz equations
            return {
                'type': 'chaotic_system',
                'system': ['dx/dt = σ(y - x)', 'dy/dt = x(ρ - z) - y', 'dz/dt = xy - βz'],
                'params': {'σ': 10, 'ρ': 28, 'β': 8/3},
                'behavior': 'chaotic_attractor',
                'method': 'numerical_rk4_adaptive'
            }

    def _generate_series_solution(self, difficulty: int) -> Dict[str, Any]:
        """Generate problems requiring series solutions."""
        if difficulty <= 2:
            return {
                'type': 'power_series',
                'ode': "y' = y",
                'expansion_point': 0,
                'method': 'power_series_ordinary_point'
            }
        else:
            # Legendre equation (regular singular point)
            n = random.randint(0, 4)
            return {
                'type': 'legendre_equation',
                'ode': f"(1-x²)y'' - 2xy' + {n}({n}+1)y = 0",
                'order': n,
                'method': 'frobenius_method',
                'solution': f'Legendre polynomial P_{n}(x)'
            }

    def _generate_bvp(self, difficulty: int) -> Dict[str, Any]:
        """Generate boundary value problems."""
        if difficulty <= 2:
            return {
                'type': 'bvp_simple',
                'ode': "y'' = -y",
                'boundary_conditions': {'y(0)': 0, 'y(π)': 0},
                'method': 'shooting_or_finite_difference'
            }
        else:
            # Eigenvalue problem (Sturm-Liouville)
            return {
                'type': 'sturm_liouville',
                'ode': "-(py')' + qy = λwy",
                'boundary_conditions': 'Dirichlet or Neumann',
                'method': 'eigenvalue_problem',
                'solution': 'eigenfunctions_and_eigenvalues'
            }


# Convenience function for curiosity engine
def generate_ode_problem(difficulty=None):
    """Generate ODE problem for curiosity engine."""
    generator = ODEProblemGenerator()
    return generator.generate_problem(difficulty)


if __name__ == "__main__":
    gen = ODEProblemGenerator()

    print("Sample ODE Problems:")
    for diff in [1, 2, 3, 4]:
        problem = gen.generate_problem(diff)
        print(f"\nDifficulty {diff}: {problem['type']}")
        print(f"  ODE: {problem.get('ode', problem.get('system'))}")
        print(f"  Method: {problem.get('method')}")
