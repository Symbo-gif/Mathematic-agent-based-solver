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
CALCULUS EXPLORATION AGENT
===========================

Domain-specific exploration agent for calculus problems.

Maintains specialized knowledge about calculus strategies including:
- Integration techniques (Risch, substitution, by parts, numerical)
- Differentiation rules (power, chain, product, quotient)
- Limit evaluation (L'Hôpital, series expansion)
- Series analysis (Taylor, Fourier, convergence)

This agent provides expert recommendations for strategy selection
based on calculus-specific patterns and heuristics.
"""

from typing import List, Dict, Any, Optional
import logging

from symbo_agentic_reasoners.exploration.base_explorer import BaseExplorationAgent
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain
from symbo_agentic_reasoners.exploration.data_structures import Strategy
from symbo_agentic_reasoners.exploration import strategy_library

logger = logging.getLogger('symbo_agentic_reasoners.exploration.domain_explorers.calculus')


class CalculusExplorer(BaseExplorationAgent):
    """
    Calculus-specific exploration agent.

    Provides expert strategy recommendations for calculus problems including
    integration, differentiation, limits, and series.

    STRATEGY SELECTION HEURISTICS:
    ------------------------------
    - Integration: Prefer symbolic (Risch/substitution) over numerical when possible
    - Composite functions: Favor substitution or chain rule
    - Products: Consider integration by parts
    - Definite integrals: Numerical methods are reliable fallback
    - Limits: L'Hôpital for indeterminate forms, series for others
    """

    def __init__(
        self,
        agent_id: str = 'calculus_exploration_agent_001',
        directory_facilitator: Optional[Any] = None,
        blackboard: Optional[Any] = None,
        knowledge_team: Optional[Any] = None
    ):
        """
        Initialize calculus exploration agent.

        Args:
            agent_id: Unique identifier
            directory_facilitator: DF for service registration
            blackboard: Communication blackboard
            knowledge_team: Knowledge management for learning
        """
        super().__init__(
            agent_id=agent_id,
            domain=MathDomain.CALCULUS,
            directory_facilitator=directory_facilitator,
            blackboard=blackboard,
            knowledge_team=knowledge_team
        )

        # Load calculus-specific strategies
        self.strategy_library = strategy_library.CALCULUS_STRATEGIES

        # Register with DF
        if self.df:
            self.register_with_df(
                service_type='math.exploration.calculus',
                algorithm='domain_strategy_library',
                cost='low'
            )

        logger.info(
            f"[{self.agent_id}] Initialized with {len(self.strategy_library)} calculus strategies"
        )

    def suggest_strategies(
        self,
        problem: StructuredProblem,
        features: Dict[str, Any]
    ) -> List[Strategy]:
        """
        Suggest calculus strategies based on problem features.

        STRATEGY SELECTION LOGIC:
        ------------------------
        1. Identify operation (integrate, differentiate, limit, series)
        2. Apply domain heuristics
        3. Filter by preconditions
        4. Order by expected success

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

        # Filter strategies by operation
        if operation == 'integrate':
            candidates = self._suggest_integration_strategies(features)
        elif operation == 'differentiate':
            candidates = self._suggest_differentiation_strategies(features)
        elif operation == 'limit':
            candidates = self._suggest_limit_strategies(features)
        elif operation == 'series':
            candidates = self._suggest_series_strategies(features)
        else:
            # Fallback: all calculus strategies
            candidates = self.strategy_library

        # Filter by preconditions
        filtered = self.filter_by_preconditions(candidates, problem, min_confidence=0.2)

        self.strategies_suggested += len(filtered)

        logger.info(
            f"[{self.agent_id}] Suggested {len(filtered)} strategies for {operation}"
        )

        return filtered

    # =======================================================================
    # INTEGRATION STRATEGIES
    # =======================================================================

    def _suggest_integration_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest integration strategies based on problem features.

        HEURISTICS:
        ----------
        - Polynomial/rational/exponential: Try Risch algorithm
        - Composite function: Prefer substitution
        - Product: Consider integration by parts
        - Definite integral: Numerical quadrature is reliable
        - Unknown form: Try substitution then fallback to numerical

        Args:
            features: Problem features

        Returns:
            Ordered list of integration strategies
        """
        strategies = []

        # Check for composite functions
        has_composite = features.get('has_composite_function', False)

        # Check integrand type
        integrand_type = features.get('integrand_type')

        # Check if definite
        is_definite = features.get('definite_integral', False)

        # Strategy selection logic
        if has_composite:
            # Substitution is preferred for composite functions
            strategies.append(self._find_strategy('calc_002'))  # Substitution
            strategies.append(self._find_strategy('calc_001'))  # Risch as fallback

        elif integrand_type in ['polynomial', 'rational', 'exponential', 'logarithmic']:
            # Elementary integrands: Risch is powerful
            strategies.append(self._find_strategy('calc_001'))  # Risch

        elif features.get('has_product', False):
            # Products: Integration by parts
            strategies.append(self._find_strategy('calc_003'))  # By parts
            strategies.append(self._find_strategy('calc_002'))  # Substitution backup

        # Numerical fallback for definite integrals
        if is_definite:
            strategies.append(self._find_strategy('calc_004'))  # Numerical

        # Remove None values (strategies not found)
        strategies = [s for s in strategies if s is not None]

        # If no specific strategies, return all integration strategies
        if not strategies:
            strategies = [
                s for s in self.strategy_library
                if s.preconditions.get('operation') == 'integrate'
            ]

        return strategies

    # =======================================================================
    # DIFFERENTIATION STRATEGIES
    # =======================================================================

    def _suggest_differentiation_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest differentiation strategies.

        HEURISTICS:
        ----------
        - Polynomial: Power rule (simple and reliable)
        - Composite function: Chain rule
        - Product: Product rule
        - Quotient: Quotient rule

        Args:
            features: Problem features

        Returns:
            Ordered list of differentiation strategies
        """
        strategies = []

        expression_type = features.get('expression_type')
        has_composite = features.get('has_composite_function', False)
        has_product = features.get('has_product', False)

        if expression_type == 'polynomial':
            # Power rule for polynomials
            strategies.append(self._find_strategy('calc_005'))  # Power rule

        if has_composite:
            # Chain rule for compositions
            strategies.append(self._find_strategy('calc_006'))  # Chain rule

        # If no specific match, return all differentiation strategies
        if not strategies:
            strategies = [
                s for s in self.strategy_library
                if s.preconditions.get('operation') == 'differentiate'
            ]

        return [s for s in strategies if s is not None]

    # =======================================================================
    # LIMIT STRATEGIES
    # =======================================================================

    def _suggest_limit_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest limit evaluation strategies.

        HEURISTICS:
        ----------
        - Indeterminate forms (0/0, ∞/∞): L'Hôpital's rule
        - Other cases: Direct evaluation or series expansion

        Args:
            features: Problem features

        Returns:
            Ordered list of limit strategies
        """
        strategies = []

        indeterminate = features.get('indeterminate_form')

        if indeterminate in ['0/0', 'inf/inf']:
            # L'Hôpital for indeterminate forms
            strategies.append(self._find_strategy('calc_007'))  # L'Hôpital

        # Series expansion as alternative
        strategies.append(self._find_strategy('calc_008'))  # Taylor series

        return [s for s in strategies if s is not None]

    # =======================================================================
    # SERIES STRATEGIES
    # =======================================================================

    def _suggest_series_strategies(self, features: Dict[str, Any]) -> List[Strategy]:
        """
        Suggest series analysis strategies.

        Args:
            features: Problem features

        Returns:
            Ordered list of series strategies
        """
        strategies = []

        expansion_type = features.get('expansion_type')

        if expansion_type == 'taylor':
            strategies.append(self._find_strategy('calc_008'))  # Taylor series

        # Return all series strategies if no specific match
        if not strategies:
            strategies = [
                s for s in self.strategy_library
                if s.preconditions.get('operation') == 'series'
            ]

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
