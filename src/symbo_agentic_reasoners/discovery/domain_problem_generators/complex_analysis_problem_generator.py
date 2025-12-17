# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complex Analysis Problem Generator"""

import random, numpy as np
from typing import Dict, Any

class ComplexAnalysisProblemGenerator:
    def __init__(self):
        self.problem_count = 0

    def generate_problem(self, difficulty=None) -> Dict[str, Any]:
        difficulty = difficulty or random.randint(1, 4)
        generators = [self._residue_calc, self._analytic_functions, self._elliptic_functions]
        problem = random.choice(generators)(difficulty)
        problem.update({'difficulty': difficulty, 'problem_id': f'COMPLEX_{self.problem_count:04d}'})
        self.problem_count += 1
        return problem

    def _residue_calc(self, d):
        if d <= 2:
            return {'type': 'residue', 'function': '1/(z² - 1)', 'point': 'z = 1', 'method': 'residue_theorem'}
        else:
            return {'type': 'contour_integral', 'function': 'sin(z)/z³', 'contour': '|z| = 1'}

    def _analytic_functions(self, d):
        if d <= 2:
            return {'type': 'cauchy_riemann', 'function': 'f(z) = z²', 'verify': 'analyticity'}
        else:
            return {'type': 'hadamard_factorization', 'function': 'entire_function', 'task': 'Find order and type'}

    def _elliptic_functions(self, d):
        if d <= 3:
            return {'type': 'elliptic_integral', 'kind': random.choice([1, 2]), 'modulus': 0.5}
        else:
            return {'type': 'weierstrass_p', 'lattice': 'Λ = Z + Zi', 'task': 'Evaluate ℘(z)'}

def generate_complex_analysis_problem(difficulty=None):
    return ComplexAnalysisProblemGenerator().generate_problem(difficulty)
