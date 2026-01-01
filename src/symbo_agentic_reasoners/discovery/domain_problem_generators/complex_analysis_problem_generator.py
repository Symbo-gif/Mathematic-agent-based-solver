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

"""Complex Analysis Problem Generator"""

import random, numpy as np
from typing import Dict, Any

class ComplexAnalysisProblemGenerator:
    """Generate complex analysis problems for autonomous exploration."""

    def __init__(self):
        """Initialize complex analysis problem generator with problem counter."""
        self.problem_count = 0

    def generate_problem(self, difficulty=None) -> Dict[str, Any]:
        """Generate random complex analysis problem.

        Args:
            difficulty: Difficulty level (1-4), random if None
                - Level 1: Basic Cauchy-Riemann, residue calculations
                - Level 2: Contour integrals, analytic continuation
                - Level 3: Hadamard factorization, elliptic integrals
                - Level 4: Weierstrass ℘-function, entire function order/type

        Returns:
            Dict with problem type, function, and method

        Example:
            >>> gen = ComplexAnalysisProblemGenerator()
            >>> problem = gen.generate_problem(difficulty=4)
            >>> problem['type'] in ['weierstrass_p', 'hadamard_factorization']
            True
        """
        difficulty = difficulty or random.randint(1, 4)
        generators = [self._residue_calc, self._analytic_functions, self._elliptic_functions]
        problem = random.choice(generators)(difficulty)
        problem.update({'difficulty': difficulty, 'problem_id': f'COMPLEX_{self.problem_count:04d}'})
        self.problem_count += 1
        return problem

    def _residue_calc(self, d):
        """Generate residue calculus problem.

        Args:
            d: Difficulty level 1-4 (residues → contour integrals)

        Returns:
            Dict with complex function and integration task
        """
        if d <= 2:
            return {'type': 'residue', 'function': '1/(z² - 1)', 'point': 'z = 1', 'method': 'residue_theorem'}
        else:
            return {'type': 'contour_integral', 'function': 'sin(z)/z³', 'contour': '|z| = 1'}

    def _analytic_functions(self, d):
        """Generate analytic function problem.

        Args:
            d: Difficulty level 1-4 (Cauchy-Riemann → Hadamard factorization)

        Returns:
            Dict with entire function analysis task
        """
        if d <= 2:
            return {'type': 'cauchy_riemann', 'function': 'f(z) = z²', 'verify': 'analyticity'}
        else:
            return {'type': 'hadamard_factorization', 'function': 'entire_function', 'task': 'Find order and type'}

    def _elliptic_functions(self, d):
        """Generate elliptic function problem.

        Args:
            d: Difficulty level 1-4 (elliptic integrals → Weierstrass ℘)

        Returns:
            Dict with elliptic integral or lattice function task
        """
        if d <= 3:
            return {'type': 'elliptic_integral', 'kind': random.choice([1, 2]), 'modulus': 0.5}
        else:
            return {'type': 'weierstrass_p', 'lattice': 'Λ = Z + Zi', 'task': 'Evaluate ℘(z)'}

def generate_complex_analysis_problem(difficulty=None):
    """Perform generate complex analysis problem operation.

    Args:
    difficulty: Description needed

    Returns:
    Result of the operation

    Example:
    >>> result = obj.generate_complex_analysis_problem(...)
    """
    return ComplexAnalysisProblemGenerator().generate_problem(difficulty)
