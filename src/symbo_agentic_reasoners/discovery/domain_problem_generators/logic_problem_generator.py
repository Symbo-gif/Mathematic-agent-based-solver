# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Logic Problem Generator"""

import random
from typing import Dict, Any

class LogicProblemGenerator:
    """Generate logic problems for autonomous exploration."""

    def __init__(self):
        """Initialize logic problem generator with problem counter."""
        self.problem_count = 0

    def generate_problem(self, difficulty=None) -> Dict[str, Any]:
        """Generate random logic problem.

        Args:
            difficulty: Difficulty level (1-4), random if None
                - Level 1: Basic SAT, simple FOL formulas
                - Level 2: Complex SAT, unification
                - Level 3: Modal logic (T system), theorem proving
                - Level 4: Temporal logic (LTL), resolution refutation

        Returns:
            Dict with problem type, formula, and solving method

        Example:
            >>> gen = LogicProblemGenerator()
            >>> problem = gen.generate_problem(difficulty=2)
            >>> problem['type'] in ['sat', 'fol_formula', 'unification']
            True
        """
        difficulty = difficulty or random.randint(1, 4)
        generators = [self._propositional, self._predicate, self._modal, self._theorem_proving]
        problem = random.choice(generators)(difficulty)
        problem.update({'difficulty': difficulty, 'problem_id': f'LOGIC_{self.problem_count:04d}'})
        self.problem_count += 1
        return problem

    def _propositional(self, d):
        """Generate propositional logic problem.

        Args:
            d: Difficulty level 1-4 (simple SAT → complex SAT)

        Returns:
            Dict with SAT formula and task
        """
        if d <= 2:
            return {'type': 'sat', 'formula': '(A ∨ B) ∧ (~A ∨ C)', 'task': 'Find satisfying assignment'}
        else:
            return {'type': 'sat_complex', 'variables': random.randint(10, 20), 'clauses': random.randint(30, 50)}

    def _predicate(self, d):
        """Generate first-order logic problem.

        Args:
            d: Difficulty level 1-4 (FOL validity → unification)

        Returns:
            Dict with FOL formula or unification task
        """
        if d <= 2:
            return {'type': 'fol_formula', 'formula': '∀x. P(x) → Q(x)', 'task': 'Verify validity'}
        else:
            return {'type': 'unification', 'terms': ['P(f(x), g(y))', 'P(z, h(a))'], 'method': 'Robinson'}

    def _modal(self, d):
        """Generate modal or temporal logic problem.

        Args:
            d: Difficulty level 1-4 (modal K/T → temporal LTL/CTL)

        Returns:
            Dict with modal formula and verification system
        """
        if d <= 3:
            return {'type': 'modal_logic', 'formula': '□P → P', 'system': 'T', 'task': 'Verify in Kripke frame'}
        else:
            return {'type': 'temporal_logic', 'formula': 'G(request → F grant)', 'system': 'LTL'}

    def _theorem_proving(self, d):
        """Generate automated theorem proving problem.

        Args:
            d: Difficulty level 1-4 (natural deduction → resolution)

        Returns:
            Dict with theorem to prove and proof method
        """
        if d <= 2:
            return {'type': 'natural_deduction', 'prove': 'P → P', 'method': 'direct_proof'}
        else:
            return {'type': 'resolution', 'clauses': '[(P,Q), (~P,R), (~Q,~R)]', 'goal': 'False', 'method': 'refutation'}

def generate_logic_problem(difficulty=None):
    """Perform generate logic problem operation.

    Args:
    difficulty: Description needed

    Returns:
    Result of the operation

    Example:
    >>> result = obj.generate_logic_problem(...)
    """
    return LogicProblemGenerator().generate_problem(difficulty)
