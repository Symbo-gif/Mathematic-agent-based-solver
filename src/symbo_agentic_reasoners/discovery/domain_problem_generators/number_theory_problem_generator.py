# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Number Theory Problem Generator - Research-level problems"""

import random
from typing import Dict, Any

class NumberTheoryProblemGenerator:
    """Generate number theory problems for autonomous exploration."""

    def __init__(self):
        """Initialize number theory problem generator with problem counter."""
        self.problem_count = 0

    def generate_problem(self, difficulty: int = None) -> Dict[str, Any]:
        """Generate random number theory problem.

        Args:
            difficulty: Difficulty level (1-4), random if None
                - Level 1: Linear Diophantine, basic modular arithmetic
                - Level 2: Pell's equation, CRT, primality tests
                - Level 3: Sum of squares, quadratic residues
                - Level 4: Generalized Pell, Carmichael numbers

        Returns:
            Dict with problem type, equation/task, and method

        Example:
            >>> gen = NumberTheoryProblemGenerator()
            >>> problem = gen.generate_problem(difficulty=2)
            >>> problem['type'] in ['pells_equation', 'crt', 'primality_test']
            True
        """
        if difficulty is None:
            difficulty = random.randint(1, 4)

        generators = [
            lambda d: self._diophantine_problem(d),
            lambda d: self._modular_arithmetic(d),
            lambda d: self._prime_problem(d),
            lambda d: self._factorization_challenge(d)
        ]

        problem = random.choice(generators)(difficulty)
        problem['difficulty'] = difficulty
        problem['problem_id'] = f'NT_{self.problem_count:04d}'
        self.problem_count += 1
        return problem

    def _diophantine_problem(self, difficulty: int) -> Dict[str, Any]:
        """Generate Diophantine equation problem.

        Args:
            difficulty: Level 1-4 (linear → generalized Pell)

        Returns:
            Dict with equation, type, and solution method
        """
        if difficulty == 1:
            a, b, c = random.randint(1, 10), random.randint(1, 10), random.randint(1, 50)
            return {'type': 'linear_diophantine', 'equation': f'{a}x + {b}y = {c}', 'method': 'extended_euclidean'}
        elif difficulty == 2:
            d = random.choice([2, 3, 5, 7, 11, 13])
            return {'type': 'pells_equation', 'equation': f'x² - {d}y² = 1', 'D': d, 'method': 'continued_fractions'}
        elif difficulty == 3:
            n = random.randint(10, 100)
            return {'type': 'sum_of_squares', 'problem': f'Express {n} as sum of two squares', 'n': n}
        else:
            # Research-level: generalized Pell
            d, k = random.choice([2, 3, 5, 7]), random.choice([1, 2, 4])
            return {'type': 'generalized_pell', 'equation': f'x² - {d}y² = {k}', 'difficulty': 'research'}

    def _modular_arithmetic(self, difficulty: int) -> Dict[str, Any]:
        """Generate modular arithmetic problem.

        Args:
            difficulty: Level 1-4 (CRT → quadratic residues)

        Returns:
            Dict with congruence system or residue problem
        """
        if difficulty <= 2:
            remainders = [random.randint(0, 9) for _ in range(3)]
            moduli = [3, 4, 5]
            return {'type': 'crt', 'system': list(zip(remainders, moduli)), 'method': 'chinese_remainder'}
        else:
            # Quadratic residues research
            p = random.choice([7, 11, 13, 17, 19, 23])
            a = random.randint(1, p-1)
            return {'type': 'quadratic_residue', 'problem': f'x² ≡ {a} (mod {p})', 'method': 'tonelli_shanks'}

    def _prime_problem(self, difficulty: int) -> Dict[str, Any]:
        """Generate primality or pseudoprime problem.

        Args:
            difficulty: Level 1-4 (Miller-Rabin → Carmichael numbers)

        Returns:
            Dict with n and primality test method
        """
        if difficulty <= 2:
            n = random.randint(100, 1000)
            return {'type': 'primality_test', 'n': n, 'method': 'miller_rabin'}
        else:
            # Carmichael number detection (research-level pseudoprimes)
            carmichael_candidates = [561, 1105, 1729, 2465, 2821]
            n = random.choice(carmichael_candidates)
            return {'type': 'carmichael_detection', 'n': n, 'challenge': 'pseudoprime_analysis'}

    def _factorization_challenge(self, difficulty: int) -> Dict[str, Any]:
        """Generate integer factorization problem.

        Args:
            difficulty: Level 1-4 (semiprimes → smooth factorization)

        Returns:
            Dict with n and factorization method
        """
        if difficulty <= 2:
            # Semiprime
            p1 = random.choice([13, 17, 19, 23, 29])
            p2 = random.choice([31, 37, 41, 43, 47])
            return {'type': 'factor_semiprime', 'n': p1 * p2, 'method': 'pollard_rho'}
        else:
            # Research: factorization with smooth p-1
            return {'type': 'smooth_factor', 'challenge': 'B-smooth detection', 'method': 'pollard_p_minus_1'}


def generate_number_theory_problem(difficulty=None):
    gen = NumberTheoryProblemGenerator()
    return gen.generate_problem(difficulty)
