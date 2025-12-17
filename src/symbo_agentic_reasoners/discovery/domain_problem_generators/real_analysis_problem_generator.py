# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Real Analysis Problem Generator"""

import random, numpy as np
from typing import Dict, Any

class RealAnalysisProblemGenerator:
    def __init__(self):
        self.problem_count = 0

    def generate_problem(self, difficulty=None) -> Dict[str, Any]:
        difficulty = difficulty or random.randint(1, 4)
        generators = [self._convergence, self._measure_theory, self._function_spaces]
        problem = random.choice(generators)(difficulty)
        problem.update({'difficulty': difficulty, 'problem_id': f'REAL_{self.problem_count:04d}'})
        self.problem_count += 1
        return problem

    def _convergence(self, d):
        if d <= 2:
            return {'type': 'series_convergence', 'series': 'Σ 1/n^p', 'p': random.uniform(0.5, 3), 'test': 'p-test'}
        else:
            return {'type': 'dominated_convergence', 'task': 'Verify DCT hypotheses', 'theorem': 'Lebesgue_DCT'}

    def _measure_theory(self, d):
        if d <= 2:
            return {'type': 'lebesgue_measure', 'set': '[0,1] ∪ [2,3]'}
        else:
            return {'type': 'cantor_set_measure', 'level': 10, 'expected': 0}

    def _function_spaces(self, d):
        if d <= 2:
            return {'type': 'lp_norm', 'function': 'f(x) = x²', 'p': 2, 'domain': (0, 1)}
        else:
            return {'type': 'sobolev_embedding', 'space': 'W^{1,2}', 'dimension': 1, 'theorem': 'Sobolev'}

def generate_real_analysis_problem(difficulty=None):
    return RealAnalysisProblemGenerator().generate_problem(difficulty)
