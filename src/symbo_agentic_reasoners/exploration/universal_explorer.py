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
EXPLORATION LAYER - UNIVERSAL STRATEGY EXPLORER
===============================================

Meta-level strategy orchestration and cross-domain pattern learning.

The UniversalStrategyExplorer is the primary exploration agent, coordinating
strategy generation and ranking for all problem types. It integrates:
- Historical learning from past explorations
- Domain-specific strategy recommendations
- Cross-domain pattern recognition
- Multi-factor strategy scoring and ranking

This is the main entry point for the exploration layer, called by the
MainOrchestrator when exploring solution spaces.

REFERENCE:
---------
Implementation Plan: Phase 1, File 4
"""

from typing import List, Dict, Any, Optional, Tuple
import logging

from symbo_agentic_reasoners.exploration.base_explorer import BaseExplorationAgent
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain
from symbo_agentic_reasoners.exploration.data_structures import (
    Strategy, ExplorationResult, StrategyRanking, ExplorationOutcome,
    hash_problem, estimate_complexity
)
from symbo_agentic_reasoners.exploration import strategy_library

logger = logging.getLogger('symbo_agentic_reasoners.exploration.universal_explorer')


class UniversalStrategyExplorer(BaseExplorationAgent):
    """
    Universal meta-level strategy exploration agent.

    RESPONSIBILITIES:
    ----------------
    1. Strategy generation from multiple sources:
       - Historical successes (80% weight)
       - Domain explorer suggestions (15% weight)
       - Strategy library fallback (5% weight)

    2. Multi-factor strategy scoring and ranking

    3. Cross-domain pattern learning:
       - Identify meta-patterns that work across domains
       - Learn anti-patterns (strategies that consistently fail together)

    4. Exploration budget optimization

    INTEGRATION:
    -----------
    - Called by MainOrchestrator after look-before-leap cache check
    - Delegates to domain explorers for specialized strategies
    - Queries KnowledgeManagementTeam for historical patterns
    - Registers with DirectoryFacilitator as 'math.exploration.universal'

    EXAMPLE USAGE:
    -------------
    ```python
    explorer = UniversalStrategyExplorer(
        agent_id='universal_strategy_explorer_001',
        directory_facilitator=df,
        knowledge_team=km_team
    )

    ranking = explorer.explore_strategies(problem)

    for strategy, confidence in ranking.ranked_strategies:
        print(f"Try: {strategy.name} (confidence={confidence:.2f})")
    ```
    """

    def __init__(
        self,
        agent_id: str = 'universal_strategy_explorer_001',
        directory_facilitator: Optional[Any] = None,
        blackboard: Optional[Any] = None,
        knowledge_team: Optional[Any] = None
    ):
        """
        Initialize universal strategy explorer.

        Args:
            agent_id: Unique identifier
            directory_facilitator: DF for service discovery
            blackboard: Communication blackboard
            knowledge_team: Knowledge management for learning
        """
        super().__init__(
            agent_id=agent_id,
            domain=None,  # Universal - no specific domain
            directory_facilitator=directory_facilitator,
            blackboard=blackboard,
            knowledge_team=knowledge_team
        )

        # Load universal strategy library
        self.strategy_library = strategy_library.get_all_strategies()

        # Domain explorer cache (lazy-loaded via DF)
        self.domain_explorers: Dict[MathDomain, Any] = {}

        # Statistics
        self.explorations_performed = 0
        self.successful_explorations = 0
        self.failed_explorations = 0

        # Register with DF
        if self.df:
            self.register_with_df(
                service_type='math.exploration.universal',
                algorithm='meta_strategy_learning',
                cost='low'
            )

        logger.info(
            f"[{self.agent_id}] Initialized with {len(self.strategy_library)} strategies"
        )

    # =======================================================================
    # MAIN EXPLORATION METHOD
    # =======================================================================

    def explore_strategies(self, problem: StructuredProblem) -> StrategyRanking:
        """
        Generate and rank strategies for a problem.

        This is the main entry point called by the MainOrchestrator.
        Implements the exploration algorithm from the implementation plan.

        ALGORITHM:
        ---------
        1. Characterize problem (extract features)
        2. Memory lookup (query similar explorations)
        3. Generate candidates from:
           - Historical successes (80% weight)
           - Domain explorer suggestions (15% weight)
           - Strategy library fallback (5% weight)
        4. Score each candidate (multi-factor scoring)
        5. Rank and return top N strategies

        Args:
            problem: The structured problem to solve

        Returns:
            StrategyRanking with ranked strategies and metadata
        """
        logger.info(
            f"[{self.agent_id}] Exploring strategies for problem: "
            f"domain={problem.domain.value}, type={problem.problem_type.value}"
        )

        # STEP 1: Characterize problem
        features = self._extract_features(problem)
        problem_sig = hash_problem(problem)

        logger.debug(f"[{self.agent_id}] Extracted features: {features}")

        # STEP 2: Memory lookup (learning integration)
        past_explorations = self.query_similar_explorations(problem)

        successful_strategies = [
            e.strategy for e in past_explorations
            if e.outcome == ExplorationOutcome.SUCCESS
        ]

        logger.info(
            f"[{self.agent_id}] Found {len(successful_strategies)} successful strategies "
            f"from {len(past_explorations)} past explorations"
        )

        # STEP 3: Generate candidates from multiple sources
        candidates = []

        # Source A: Historical successes (80% weight - highest priority)
        candidates.extend(successful_strategies)

        # Source B: Domain exploration agent suggestions (15% weight)
        domain_agent = self._get_domain_explorer(problem.domain)
        if domain_agent:
            try:
                domain_strategies = domain_agent.suggest_strategies(problem, features)
                candidates.extend(domain_strategies)
                logger.debug(
                    f"[{self.agent_id}] Domain explorer provided {len(domain_strategies)} strategies"
                )
            except Exception as e:
                logger.warning(f"[{self.agent_id}] Domain explorer failed: {e}")

        # Source C: Strategy library fallback (5% weight)
        library_strategies = strategy_library.get_strategies_for_features(features)
        candidates.extend(library_strategies)

        # Remove duplicates (by strategy_id)
        unique_candidates = self._deduplicate_strategies(candidates)

        logger.info(
            f"[{self.agent_id}] Generated {len(unique_candidates)} unique candidate strategies"
        )

        # STEP 4: Score each candidate
        scored = self.score_strategies(unique_candidates, problem, past_explorations)

        # STEP 5: Rank and compute budget
        budget = self.compute_exploration_budget(problem, scored)

        # Generate reasoning explanation
        reasoning = self._explain_ranking(scored, past_explorations, budget)

        # Estimate total solve time
        estimated_time = self._estimate_solve_time(scored[:budget])

        ranking = StrategyRanking(
            problem_signature=problem_sig,
            ranked_strategies=scored[:budget],
            exploration_budget=budget,
            estimated_solve_time=estimated_time,
            reasoning=reasoning,
            metadata={
                'total_candidates': len(unique_candidates),
                'historical_strategies': len(successful_strategies),
                'complexity': estimate_complexity(problem)
            }
        )

        self.explorations_performed += 1

        logger.info(
            f"[{self.agent_id}] Ranked {len(ranking.ranked_strategies)} strategies, "
            f"budget={budget}, estimated_time={estimated_time:.1f}s"
        )

        return ranking

    # =======================================================================
    # FEATURE EXTRACTION
    # =======================================================================

    def _extract_features(self, problem: StructuredProblem) -> Dict[str, Any]:
        """
        Extract relevant features from problem for strategy matching.

        Args:
            problem: The structured problem

        Returns:
            Dictionary of features
        """
        features = {
            'domain': problem.domain,
            'problem_type': problem.problem_type,
            'operation': problem.metadata.get('operation', 'unknown'),
            'complexity': estimate_complexity(problem),
        }

        # Domain-specific feature extraction
        if problem.domain == MathDomain.CALCULUS:
            features.update({
                'has_composite_function': problem.metadata.get('has_composite_function', False),
                'has_product': problem.metadata.get('has_product', False),
                'integrand_type': problem.metadata.get('integrand_type'),
                'definite_integral': problem.metadata.get('definite_integral', False),
            })

        elif problem.domain == MathDomain.ALGEBRA:
            features.update({
                'expression_type': problem.metadata.get('expression_type'),
                'equation_type': problem.metadata.get('equation_type'),
                'degree': problem.metadata.get('degree', 1),
                'coefficients_type': problem.metadata.get('coefficients_type'),
                'has_exponential': problem.metadata.get('has_exponential', False),
            })

        elif problem.domain == MathDomain.LINEAR_ALGEBRA:
            features.update({
                'matrix_size': problem.metadata.get('matrix_size'),
                'operand_type': problem.metadata.get('operand_type'),
                'decomposition_type': problem.metadata.get('decomposition_type'),
            })

        elif problem.domain == MathDomain.GEOMETRY:
            features.update({
                'shape': problem.metadata.get('shape'),
                'space_type': problem.metadata.get('space_type', 'euclidean'),
                'has_trigonometric': problem.metadata.get('has_trigonometric', False),
            })

        return features

    # =======================================================================
    # DOMAIN EXPLORER INTEGRATION
    # =======================================================================

    def _get_domain_explorer(self, domain: MathDomain) -> Optional[Any]:
        """
        Get domain-specific exploration agent via Directory Facilitator.

        Implements lazy loading with caching.

        Args:
            domain: Mathematical domain

        Returns:
            Domain explorer agent or None if not available
        """
        # Check cache first
        if domain in self.domain_explorers:
            return self.domain_explorers[domain]

        # Query DF for domain explorer
        if self.df is None:
            return None

        try:
            service_type = f'math.exploration.{domain.value.lower()}'
            agents = self.df.search(service_type)

            if agents:
                explorer = agents[0]  # Take first match
                # Cache for future use
                self.domain_explorers[domain] = explorer.instance if hasattr(explorer, 'instance') else explorer
                logger.debug(f"[{self.agent_id}] Loaded domain explorer for {domain.value}")
                return self.domain_explorers[domain]
            else:
                logger.debug(f"[{self.agent_id}] No domain explorer found for {domain.value}")
                return None

        except Exception as e:
            logger.error(f"[{self.agent_id}] Error loading domain explorer: {e}")
            return None

    # =======================================================================
    # UTILITY METHODS
    # =======================================================================

    def _deduplicate_strategies(self, strategies: List[Strategy]) -> List[Strategy]:
        """Remove duplicate strategies by strategy_id"""
        seen_ids = set()
        unique = []

        for strategy in strategies:
            if strategy.strategy_id not in seen_ids:
                seen_ids.add(strategy.strategy_id)
                unique.append(strategy)

        return unique

    def _explain_ranking(
        self,
        ranked: List[Tuple[Strategy, float]],
        past_explorations: List[ExplorationResult],
        budget: int
    ) -> str:
        """
        Generate human-readable explanation of strategy ranking.

        Args:
            ranked: Ranked strategy list
            past_explorations: Historical explorations
            budget: Exploration budget

        Returns:
            Explanation string
        """
        if not ranked:
            return "No applicable strategies found."

        top_strategy, top_score = ranked[0]

        # Determine ranking rationale
        if len(past_explorations) > 0 and any(
            e.strategy.strategy_id == top_strategy.strategy_id
            for e in past_explorations
        ):
            rationale = f"Historical success on similar problems (confidence={top_score:.2f})"
        elif top_score >= 0.8:
            rationale = f"Strong precondition match (confidence={top_score:.2f})"
        elif top_strategy.success_rate >= 0.9:
            rationale = f"High overall success rate ({top_strategy.success_rate:.0%})"
        else:
            rationale = f"Best available option (confidence={top_score:.2f})"

        explanation = (
            f"Recommending '{top_strategy.name}' as primary strategy. "
            f"{rationale}. "
            f"Exploring top {budget} strategies."
        )

        return explanation

    def _estimate_solve_time(self, ranked: List[Tuple[Strategy, float]]) -> float:
        """
        Estimate total time to try all ranked strategies.

        Args:
            ranked: Ranked strategy list

        Returns:
            Estimated time in seconds
        """
        # Rough time estimates by cost
        time_estimates = {
            'low': 0.5,
            'medium': 2.0,
            'high': 5.0
        }

        total_time = sum(
            time_estimates.get(strategy.estimated_cost, 2.0)
            for strategy, _ in ranked
        )

        return total_time

    # =======================================================================
    # REQUIRED ABSTRACT METHOD IMPLEMENTATION
    # =======================================================================

    def suggest_strategies(
        self,
        problem: StructuredProblem,
        features: Dict[str, Any]
    ) -> List[Strategy]:
        """
        Universal strategy suggestion (delegates to explore_strategies).

        Args:
            problem: The structured problem
            features: Extracted features

        Returns:
            List of suggested strategies
        """
        # For universal explorer, we return all strategies and let scoring handle ranking
        return self.strategy_library

    # =======================================================================
    # STATISTICS AND DEBUGGING
    # =======================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        base_stats = super().get_statistics()

        base_stats.update({
            'explorations_performed': self.explorations_performed,
            'successful_explorations': self.successful_explorations,
            'failed_explorations': self.failed_explorations,
            'success_rate': (
                self.successful_explorations / self.explorations_performed
                if self.explorations_performed > 0 else 0.0
            ),
            'domain_explorers_loaded': len(self.domain_explorers)
        })

        return base_stats

    def __repr__(self) -> str:
        return (
            f"<UniversalStrategyExplorer "
            f"strategies={len(self.strategy_library)} "
            f"explorations={self.explorations_performed}>"
        )
