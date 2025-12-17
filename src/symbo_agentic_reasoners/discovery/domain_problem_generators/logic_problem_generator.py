# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Logic Problem Generator"""

import random
from typing import Dict, Any

class LogicProblemGenerator:
    def __init__(self):
        self.problem_count = 0

    def generate_problem(self, difficulty=None) -> Dict[str, Any]:
        difficulty = difficulty or random.randint(1, 4)
        generators = [self._propositional, self._predicate, self._modal, self._theorem_proving]
        problem = random.choice(generators)(difficulty)
        problem.update({'difficulty': difficulty, 'problem_id': f'LOGIC_{self.problem_count:04d}'})
        self.problem_count += 1
        return problem

    def _propositional(self, d):
        if d <= 2:
            return {'type': 'sat', 'formula': '(A ∨ B) ∧ (~A ∨ C)', 'task': 'Find satisfying assignment'}
        else:
            return {'type': 'sat_complex', 'variables': random.randint(10, 20), 'clauses': random.randint(30, 50)}

    def _predicate(self, d):
        if d <= 2:
            return {'type': 'fol_formula', 'formula': '∀x. P(x) → Q(x)', 'task': 'Verify validity'}
        else:
            return {'type': 'unification', 'terms': ['P(f(x), g(y))', 'P(z, h(a))'], 'method': 'Robinson'}

    def _modal(self, d):
        if d <= 3:
            return {'type': 'modal_logic', 'formula': '□P → P', 'system': 'T', 'task': 'Verify in Kripke frame'}
        else:
            return {'type': 'temporal_logic', 'formula': 'G(request → F grant)', 'system': 'LTL'}

    def _theorem_proving(self, d):
        if d <= 2:
            return {'type': 'natural_deduction', 'prove': 'P → P', 'method': 'direct_proof'}
        else:
            return {'type': 'resolution', 'clauses': '[(P,Q), (~P,R), (~Q,~R)]', 'goal': 'False', 'method': 'refutation'}

def generate_logic_problem(difficulty=None):
    return LogicProblemGenerator().generate_problem(difficulty)
