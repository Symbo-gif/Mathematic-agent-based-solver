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
ALGEBRA EXPLORATION AGENT
==========================

Domain-specific exploration agent for algebra problems.

Maintains specialized knowledge about algebra strategies including:
- Equation solving (linear, quadratic, polynomial, systems)
- Polynomial operations (factorization, division, roots)
- Simplification and manipulation
- Exponential and logarithmic equations

This agent provides expert recommendations based on equation types,
polynomial degrees, and algebraic structure patterns.
"""

from typing import List, Dict, Any, Optional
import logging

from symbo_agentic_reasoners.exploration.base_explorer import BaseExplorationAgent
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain
from symbo_agentic_reasoners.exploration.data_structures import Strategy
from symbo_agentic_reasoners.exploration import strategy_library

logger = logging.getLogger('symbo_agentic_reasoners.exploration.domain_explorers.algebra')


class AlgebraExplorer(BaseExplorationAgent):
    """
    Algebra-specific exploration agent.

    Provides expert strategy recommendations for algebra problems including
    equation solving, polynomial manipulation, and simplification.

    STRATEGY SELECTION HEURISTICS:
    ------------------------------
    - Quadratic equations: Quadratic formula is most reliable
    - High-degree polynomials: Try rational root theorem first
    - Linear systems: Gaussian elimination
    - Exponential equations: Logarithmic approach
    - Polynomial division: Long division algorithm
    """

    def __init__(
        self,
        agent_id: str = 'algebra_exploration_agent_001',
        directory_facilitator: Optional[Any] = None,
        blackboard: Optional[Any] = None,
        knowledge_team: Optional[Any] = None
    ):
        """
        Initialize algebra exploration agent.

        Args:
            agent_id: Unique identifier
            directory_facilitator: DF for service registration
            blackboard: Communication blackboard
            knowledge_team: Knowledge management for learning
        """
        super().__init__(
            agent_id=agent_id,
            domain=MathDomain.ALGEBRA,
            directory_facilitator=directory_facilitator,
            blackboard=blackboard,
            knowledge_team=knowledge_team
        )

        # Load algebra-specific strategies
        self.strategy_library = strategy_library.ALGEBRA_STRATEGIES

        # Register with DF
        if self.df:
            self.register_with_df(
                service_type='math.exploration.algebra',
                algorithm='domain_strategy_library',
                cost='low'
            )

        logger.info(
            f"[{self.agent_id}] Initialized with {len(self.strategy_library)} algebra strategies"
        )

    def suggest_strategies(
        self,
        problem: StructuredProblem,
        features: Dict[str, Any]
    ) -> List[Strategy]:
        """
        Suggest algebra strategies based on problem features.

        STRATEGY SELECTION LOGIC:
        ------------------------
        1. Identify operation (solve, factor, simplify, divide)
        2. Check equation/polynomial type
        3. Apply domain heuristics
        4. Filter by preconditions

        Args:
            problem: The structured problem
            features: Extracted problem features

        Returns:
            List of recommended strategies
        """
        operation = features.get('operation', 'unknown')

        logger.debug(
            f"[{self.agent_id}] Suggesting strategies for operation: {operation}"
        )

        # Strategy selection by operation
        if operation == 'solve':
            candidates = self._suggest_solve_strategies(features)
        elif operation == 'factor':
            candidates = self._suggest_factorization_strategies(features)
        elif operation == 'simplify':
            candidates = self._suggest_simplification_strategies(features)
        elif operation == 'divide':
            candidates = self._suggest_division_strategies(features)
        else:
            # Fallback: all algebra strategies
            candidates = self.strategy_library

        # Filter by preconditions
        filtered = self.filter_by_preconditions(candidates, problem, min_confidence=0.2)

        self.strategies_suggested += len(filtered)

        logger.info(
            f"[{self.agent_id}] Suggested {len(filtered)} strategies for {operation}"
        )

        return filtered

    # =======================================================================
    # EQUATION SOLVING STRATEGIES
    # =======================================================================

    def _suggest_solve_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest equation solving strategies.

        HEURISTICS:
        ----------
        - Quadratic: Quadratic formula (most reliable)
        - Linear system: Gaussian elimination
        - Exponential: Logarithmic approach
        - Polynomial with integer coefficients: Rational root theorem

        Args:
            features: Problem features

        Returns:
            Ordered list of solving strategies
        """
        strategies = []

        equation_type = features.get('equation_type')
        system_type = features.get('system_type')
        has_exponential = features.get('has_exponential', False)

        # Quadratic equations
        if equation_type == 'quadratic':
            strategies.append(self._find_strategy('alg_002'))  # Quadratic formula
            strategies.append(self._find_strategy('alg_003'))  # Completing the square

        # Linear systems
        elif system_type == 'linear':
            strategies.append(self._find_strategy('alg_004'))  # Gaussian elimination

        # Exponential equations
        elif has_exponential:
            strategies.append(self._find_strategy('alg_007'))  # Logarithmic method

        # Polynomial equations with integer coefficients
        elif features.get('coefficients_type') == 'integer':
            strategies.append(self._find_strategy('alg_005'))  # Rational root theorem

        # If no specific strategies, return all solving strategies
        if not strategies:
            strategies = [
                s for s in self.strategy_library
                if s.preconditions.get('operation') == 'solve'
            ]

        return [s for s in strategies if s is not None]

    # =======================================================================
    # FACTORIZATION STRATEGIES
    # =======================================================================

    def _suggest_factorization_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest polynomial factorization strategies.

        HEURISTICS:
        ----------
        - Polynomials up to degree 4: Direct factorization
        - Higher degrees: May require numerical methods or special techniques

        Args:
            features: Problem features

        Returns:
            Ordered list of factorization strategies
        """
        strategies = []

        expression_type = features.get('expression_type')
        degree = features.get('degree', 1)

        if expression_type == 'polynomial' and degree <= 4:
            strategies.append(self._find_strategy('alg_001'))  # Direct factorization

        return [s for s in strategies if s is not None]

    # =======================================================================
    # SIMPLIFICATION STRATEGIES
    # =======================================================================

    def _suggest_simplification_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest simplification strategies.

        HEURISTICS:
        ----------
        - Algebraic identities for polynomials and rationals
        - Combine like terms, factor common terms

        Args:
            features: Problem features

        Returns:
            Ordered list of simplification strategies
        """
        strategies = []

        expression_type = features.get('expression_type')

        if expression_type in ['polynomial', 'rational']:
            strategies.append(self._find_strategy('alg_008'))  # Algebraic identities

        return [s for s in strategies if s is not None]

    # =======================================================================
    # DIVISION STRATEGIES
    # =======================================================================

    def _suggest_division_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest polynomial division strategies.

        Args:
            features: Problem features

        Returns:
            Ordered list of division strategies
        """
        strategies = []

        expression_type = features.get('expression_type')

        if expression_type == 'polynomial':
            strategies.append(self._find_strategy('alg_006'))  # Polynomial long division

        return [s for s in strategies if s is not None]

    # =======================================================================
    # UTILITY METHODS
    # =======================================================================

    def _find_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """
        Find strategy by ID in library.

        Args:
            strategy_id: Strategy identifier

        Returns:
            Strategy object or None if not found
        """
        for strategy in self.strategy_library:
            if strategy.strategy_id == strategy_id:
                return strategy
        return None
