# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Abstract Algebra Problem Generator - Research-level problems"""

import random
from typing import Dict, Any

class AlgebraProblemGenerator:
    """Generate abstract algebra problems for autonomous exploration."""

    def __init__(self):
        self.problem_count = 0

    def generate_problem(self, difficulty: int = None) -> Dict[str, Any]:
        if difficulty is None:
            difficulty = random.randint(1, 4)

        generators = [
            lambda d: self._group_theory_problem(d),
            lambda d: self._ring_theory_problem(d),
            lambda d: self._field_theory_problem(d),
            lambda d: self._galois_theory_problem(d)
        ]

        problem = random.choice(generators)(difficulty)
        problem['difficulty'] = difficulty
        problem['problem_id'] = f'ALGEBRA_{self.problem_count:04d}'
        self.problem_count += 1
        return problem

    def _group_theory_problem(self, difficulty: int) -> Dict[str, Any]:
        if difficulty == 1:
            n = random.choice([4, 6, 8, 10, 12])
            return {'type': 'find_subgroups', 'group': f'Z_{n}', 'task': 'Find all subgroups'}
        elif difficulty == 2:
            n = random.choice([6, 12, 20, 30])
            p = random.choice([2, 3, 5])
            return {'type': 'sylow_subgroups', 'group_order': n, 'prime': p, 'method': 'sylow_theorems'}
        elif difficulty == 3:
            return {'type': 'group_action', 'group': 'S_4', 'set': '{1,2,3,4}', 'task': 'Compute orbits and stabilizers'}
        else:
            # Research: composition series
            return {'type': 'composition_series', 'group': 'A_5', 'task': 'Determine composition factors', 'theorem': 'Jordan-Hölder'}

    def _ring_theory_problem(self, difficulty: int) -> Dict[str, Any]:
        if difficulty <= 2:
            ring = random.choice(['Z', 'Z[x]', 'Z[i]', 'Q[x]'])
            return {'type': 'ring_classification', 'ring': ring, 'classify_as': 'Euclidean/PID/UFD'}
        else:
            # Research: ideal structure
            return {'type': 'prime_ideals', 'ring': 'Z[√-5]', 'task': 'Find all prime ideals', 'challenge': 'non-UFD_ring'}

    def _field_theory_problem(self, difficulty: int) -> Dict[str, Any]:
        if difficulty <= 2:
            elements = ['√2', '√3', 'i', '∛2']
            element = random.choice(elements)
            return {'type': 'minimal_polynomial', 'element': element, 'base_field': 'Q'}
        else:
            polys = ['x² - 2', 'x³ - 2', 'x⁴ - 2']
            poly = random.choice(polys)
            return {'type': 'splitting_field', 'polynomial': poly, 'base_field': 'Q'}

    def _galois_theory_problem(self, difficulty: int) -> Dict[str, Any]:
        if difficulty <= 3:
            poly = random.choice(['x² - 2', 'x³ - 2', 'x⁴ - 2'])
            return {'type': 'galois_group', 'polynomial': poly, 'base_field': 'Q', 'method': 'automorphism_analysis'}
        else:
            # Research: Galois correspondence
            return {'type': 'galois_correspondence', 'extension': 'Q(∛2, ζ₃)/Q', 'task': 'Map subgroups to intermediate fields'}


def generate_algebra_problem(difficulty=None):
    gen = AlgebraProblemGenerator()
    return gen.generate_problem(difficulty)
