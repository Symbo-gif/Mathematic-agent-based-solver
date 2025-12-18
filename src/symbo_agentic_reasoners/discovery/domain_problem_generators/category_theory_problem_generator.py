# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Category Theory Problem Generator - Research-level problems"""

import random
from typing import Dict, Any

class CategoryTheoryProblemGenerator:
    """Generate category theory problems for autonomous exploration."""

    def __init__(self):
        """Initialize category theory problem generator with problem counter."""
        self.problem_count = 0

    def generate_problem(self, difficulty: int = None) -> Dict[str, Any]:
        """Generate random category theory problem.

        Args:
            difficulty: Difficulty level (1-4), random if None
                - Level 1: Basic morphism composition, functor verification
                - Level 2: Natural transformations, adjunction verification
                - Level 3: Yoneda lemma, representable functors
                - Level 4: Kan extensions, limits via universal properties

        Returns:
            Dict with problem type, specification, and theorem references

        Example:
            >>> gen = CategoryTheoryProblemGenerator()
            >>> problem = gen.generate_problem(difficulty=3)
            >>> problem['type']
            'yoneda_lemma'
        """
        if difficulty is None:
            difficulty = random.randint(1, 4)

        generators = [
            lambda d: self._morphism_problem(d),
            lambda d: self._functor_problem(d),
            lambda d: self._adjunction_problem(d),
            lambda d: self._universal_property(d)
        ]

        problem = random.choice(generators)(difficulty)
        problem['difficulty'] = difficulty
        problem['problem_id'] = f'CAT_{self.problem_count:04d}'
        self.problem_count += 1
        return problem

    def _morphism_problem(self, difficulty: int) -> Dict[str, Any]:
        """Generate morphism and composition problem.

        Args:
            difficulty: Level 1-4 (composition → isomorphism proofs)

        Returns:
            Dict with category, morphisms, and verification task
        """
        if difficulty <= 2:
            return {'type': 'morphism_composition', 'category': 'Set', 'task': 'Verify associativity'}
        else:
            return {'type': 'isomorphism_detection', 'objects': ['A', 'B'], 'task': 'Prove A ≅ B via morphisms'}

    def _functor_problem(self, difficulty: int) -> Dict[str, Any]:
        """Generate functor or natural transformation problem.

        Args:
            difficulty: Level 1-4 (functor verification → Yoneda lemma)

        Returns:
            Dict with functors, naturality conditions, and theorems
        """
        if difficulty == 1:
            return {'type': 'verify_functor', 'functor': 'Forgetful: Group → Set', 'axioms': ['identity', 'composition']}
        elif difficulty == 2:
            return {'type': 'natural_transformation', 'functors': ['F', 'G'], 'task': 'Verify naturality square'}
        elif difficulty == 3:
            return {'type': 'yoneda_lemma', 'task': 'Apply Yoneda: Nat(Hom(A,-), F) ≅ F(A)'}
        else:
            return {'type': 'representable_functor', 'functor': 'F: C → Set', 'task': 'Find representing object', 'theorem': 'Yoneda'}

    def _adjunction_problem(self, difficulty: int) -> Dict[str, Any]:
        """Generate adjunction problem.

        Args:
            difficulty: Level 1-4 (adjunction verification → Kan extensions)

        Returns:
            Dict with adjunction pair and verification requirements
        """
        if difficulty <= 2:
            adj = random.choice(['Free ⊣ Forgetful', '(-) ⊗ V ⊣ Hom(V, -)', '(-) × A ⊣ (-)^A'])
            return {'type': 'verify_adjunction', 'adjunction': adj, 'verify': ['unit', 'counit', 'triangles']}
        else:
            return {'type': 'kan_extension', 'task': 'Compute Lan_K F', 'method': 'colimit_over_comma_category'}

    def _universal_property(self, difficulty: int) -> Dict[str, Any]:
        """Generate universal property problem.

        Args:
            difficulty: Level 1-4 (products → general limits)

        Returns:
            Dict with universal construction task
        """
        if difficulty <= 2:
            return {'type': 'product', 'objects': ['A', 'B'], 'verify': 'universal_property_of_product'}
        else:
            return {'type': 'limit', 'diagram': 'general_diagram', 'task': 'Construct limit via universal property'}


def generate_category_theory_problem(difficulty=None):
    gen = CategoryTheoryProblemGenerator()
    return gen.generate_problem(difficulty)
