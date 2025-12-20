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
EXPLORATION LAYER - BASE EXPLORATION AGENT
==========================================

Abstract base class for all exploration agents.

Provides shared functionality for strategy exploration, scoring, and learning.
All exploration agents (Universal and Domain-specific) inherit from this class.

RESPONSIBILITIES:
----------------
1. Strategy scoring using multi-factor algorithm
2. Precondition filtering
3. Service registration with Directory Facilitator
4. BDI control loop for exploration deliberation

ARCHITECTURE:
------------
BaseExplorationAgent extends BDIAgent, implementing the standard BDI control
loop (perceive, deliberate, execute) specialized for strategy exploration.

REFERENCE:
---------
Implementation Plan: Phase 1, File 3
"""

from abc import abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Belief, Desire, Intention
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain
from symbo_agentic_reasoners.exploration.data_structures import (
    Strategy, ExplorationResult, StrategyRanking, ExplorationOutcome,
    hash_problem, estimate_complexity
)

logger = logging.getLogger('symbo_agentic_reasoners.exploration.base_explorer')


class BaseExplorationAgent(BDIAgent):
    """
    Abstract base class for exploration agents.

    Exploration agents search solution spaces, rank strategies, and learn
    from past attempts to improve problem-solving efficiency.

    All exploration agents follow the BDI (Belief-Desire-Intention) architecture
    and integrate with the learning system for continuous improvement.
    """

    def __init__(
        self,
        agent_id: str,
        domain: Optional[MathDomain] = None,
        directory_facilitator: Optional[Any] = None,
        blackboard: Optional[Any] = None,
        knowledge_team: Optional[Any] = None
    ):
        """
        Initialize exploration agent.

        Args:
            agent_id: Unique identifier for this agent
            domain: Mathematical domain (None for universal explorer)
            directory_facilitator: DF for service registration
            blackboard: Communication blackboard
            knowledge_team: Knowledge management team for learning
        """
        super().__init__(agent_id=agent_id)

        self.domain = domain
        self.df = directory_facilitator
        self.blackboard = blackboard
        self.knowledge_team = knowledge_team

        # Strategy library (populated by subclasses)
        self.strategy_library: List[Strategy] = []

        # Statistics
        self.strategies_suggested = 0
        self.strategies_scored = 0
        self.explorations_recorded = 0

        logger.info(f"[{self.agent_id}] Initialized exploration agent for domain: {domain}")

    # =======================================================================
    # ABSTRACT METHODS (must be implemented by subclasses)
    # =======================================================================

    @abstractmethod
    def suggest_strategies(
        self,
        problem: StructuredProblem,
        features: Dict[str, Any]
    ) -> List[Strategy]:
        """
        Suggest strategies for a given problem.

        This is the core method that domain-specific explorers implement
        to provide strategy recommendations based on their expertise.

        Args:
            problem: The structured problem to solve
            features: Extracted problem features

        Returns:
            List of potentially applicable strategies
        """
        pass

    # =======================================================================
    # STRATEGY SCORING
    # =======================================================================

    def score_strategy(
        self,
        strategy: Strategy,
        problem: StructuredProblem,
        past_explorations: List[ExplorationResult]
    ) -> float:
        """
        Multi-factor scoring of a strategy for a problem.

        SCORING FACTORS:
        ---------------
        1. Historical success rate (40%) - Strategy's overall success_rate
        2. Problem-strategy match (30%) - How well preconditions match
        3. Computational cost (20%) - Prefer low-cost strategies
        4. Recency boost (10%) - Recent successes boost confidence

        Args:
            strategy: Strategy to score
            problem: Problem being solved
            past_explorations: Historical exploration results

        Returns:
            Score in [0, 1] where higher is better
        """
        # Factor 1: Historical success rate (40%)
        domain_rate = strategy.success_rate

        # Factor 2: Problem-strategy match confidence (30%)
        match_confidence = strategy.matches_problem(problem)

        # Factor 3: Cost penalty (20%)
        # Prefer low-cost strategies when uncertain
        cost_multiplier = {'low': 1.0, 'medium': 0.8, 'high': 0.6}
        cost_factor = cost_multiplier.get(strategy.estimated_cost, 0.7)

        # Factor 4: Recency boost (10%)
        # Recent successes (last 30 days) increase confidence
        recent_threshold = datetime.now() - timedelta(days=30)
        recent_successes = [
            e for e in past_explorations
            if e.strategy.strategy_id == strategy.strategy_id
            and e.outcome == ExplorationOutcome.SUCCESS
            and e.timestamp >= recent_threshold
        ]
        recency_boost = min(len(recent_successes) * 0.05, 0.2)  # Max 20% boost

        # Weighted combination
        score = (
            domain_rate * 0.4 +
            match_confidence * 0.3 +
            cost_factor * 0.2 +
            recency_boost * 0.1
        )

        self.strategies_scored += 1

        logger.debug(
            f"[{self.agent_id}] Scored strategy '{strategy.name}': "
            f"{score:.3f} (domain={domain_rate:.2f}, match={match_confidence:.2f}, "
            f"cost={cost_factor:.2f}, recency={recency_boost:.2f})"
        )

        return max(0.0, min(1.0, score))  # Clamp to [0, 1]

    def score_strategies(
        self,
        strategies: List[Strategy],
        problem: StructuredProblem,
        past_explorations: List[ExplorationResult]
    ) -> List[Tuple[Strategy, float]]:
        """
        Score multiple strategies and return ranked list.

        Args:
            strategies: List of candidate strategies
            problem: Problem being solved
            past_explorations: Historical results

        Returns:
            List of (strategy, score) tuples, sorted by score descending
        """
        scored = [
            (strategy, self.score_strategy(strategy, problem, past_explorations))
            for strategy in strategies
        ]

        # Sort by score, descending
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)

        return ranked

    # =======================================================================
    # PRECONDITION FILTERING
    # =======================================================================

    def filter_by_preconditions(
        self,
        strategies: List[Strategy],
        problem: StructuredProblem,
        min_confidence: float = 0.3
    ) -> List[Strategy]:
        """
        Filter strategies based on precondition matching.

        Args:
            strategies: List of candidate strategies
            problem: Problem being solved
            min_confidence: Minimum match confidence threshold

        Returns:
            List of strategies with match_confidence >= min_confidence
        """
        filtered = []

        for strategy in strategies:
            confidence = strategy.matches_problem(problem)
            if confidence >= min_confidence:
                filtered.append(strategy)
                logger.debug(
                    f"[{self.agent_id}] Strategy '{strategy.name}' passed filter "
                    f"(confidence={confidence:.2f})"
                )
            else:
                logger.debug(
                    f"[{self.agent_id}] Strategy '{strategy.name}' filtered out "
                    f"(confidence={confidence:.2f} < {min_confidence})"
                )

        logger.info(
            f"[{self.agent_id}] Filtered {len(filtered)}/{len(strategies)} strategies "
            f"(threshold={min_confidence})"
        )

        return filtered

    # =======================================================================
    # SERVICE REGISTRATION
    # =======================================================================

    def register_with_df(self, service_type: str, **kwargs):
        """
        Register this agent's services with the Directory Facilitator.

        Args:
            service_type: Service type identifier (e.g., 'math.exploration.calculus')
            **kwargs: Additional service registration parameters
        """
        if self.df is None:
            logger.warning(f"[{self.agent_id}] No Directory Facilitator available for registration")
            return

        try:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import ServiceRegistration

            registration = ServiceRegistration(
                service_type=service_type,
                agent_id=self.agent_id,
                algorithm=kwargs.get('algorithm', 'strategy_exploration'),
                cost=kwargs.get('cost', 'low'),
                properties={'tier': '1.5', 'domain': self.domain.value if self.domain else 'universal'},
                instance=self
            )

            self.df.register(registration)
            logger.info(f"[{self.agent_id}] Registered service: {service_type}")

        except Exception as e:
            logger.error(f"[{self.agent_id}] Failed to register with DF: {e}")

    # =======================================================================
    # LEARNING INTEGRATION
    # =======================================================================

    def query_similar_explorations(
        self,
        problem: StructuredProblem,
        limit: int = 10
    ) -> List[ExplorationResult]:
        """
        Query knowledge management system for similar past explorations.

        Args:
            problem: Current problem
            limit: Maximum number of results to return

        Returns:
            List of similar exploration results
        """
        if self.knowledge_team is None:
            logger.debug(f"[{self.agent_id}] No knowledge team available")
            return []

        try:
            problem_sig = hash_problem(problem)
            results = self.knowledge_team.query_similar_explorations(problem_sig, limit=limit)

            logger.debug(
                f"[{self.agent_id}] Retrieved {len(results)} similar explorations "
                f"for problem signature {problem_sig}"
            )

            return results

        except Exception as e:
            logger.error(f"[{self.agent_id}] Error querying explorations: {e}")
            return []

    def record_exploration(
        self,
        strategy: Strategy,
        problem: StructuredProblem,
        outcome: ExplorationOutcome,
        execution_time: float = 0.0,
        error_type: Optional[str] = None,
        lessons_learned: Optional[List[str]] = None
    ):
        """
        Record an exploration result for learning.

        Args:
            strategy: Strategy that was explored
            problem: Problem being solved
            outcome: Result outcome
            execution_time: Time taken
            error_type: Classification of error if failed
            lessons_learned: Insights from this exploration
        """
        if self.knowledge_team is None:
            logger.debug(f"[{self.agent_id}] No knowledge team - exploration not recorded")
            return

        try:
            from symbo_agentic_reasoners.exploration.data_structures import ExplorationResult
            import uuid

            result = ExplorationResult(
                exploration_id=uuid.uuid4().hex,
                strategy=strategy,
                problem_signature=hash_problem(problem),
                outcome=outcome,
                execution_time=execution_time,
                error_type=error_type,
                lessons_learned=lessons_learned or []
            )

            self.knowledge_team.store_exploration_result(result)
            self.explorations_recorded += 1

            logger.info(
                f"[{self.agent_id}] Recorded {outcome.value} exploration: "
                f"strategy='{strategy.name}', time={execution_time:.2f}s"
            )

        except Exception as e:
            logger.error(f"[{self.agent_id}] Failed to record exploration: {e}")

    # =======================================================================
    # EXPLORATION BUDGET COMPUTATION
    # =======================================================================

    def compute_exploration_budget(
        self,
        problem: StructuredProblem,
        ranked_strategies: List[Tuple[Strategy, float]]
    ) -> int:
        """
        Determine how many strategies to try before falling back.

        Budget based on:
        - Problem complexity (complex = more budget)
        - Strategy confidence scores (high confidence = smaller budget)
        - Domain variance (high-variance domains = more exploration)

        Args:
            problem: Problem being solved
            ranked_strategies: Ranked strategy list

        Returns:
            Number of strategies to try (1-5)
        """
        # Base budget by complexity
        complexity = estimate_complexity(problem)
        base_budget = {'low': 1, 'medium': 2, 'high': 3}[complexity]

        # Adjust by top strategy confidence
        if ranked_strategies:
            top_confidence = ranked_strategies[0][1]
            if top_confidence >= 0.9:
                # Very confident - try fewer
                base_budget = max(1, base_budget - 1)
            elif top_confidence < 0.6:
                # Low confidence - try more
                base_budget = min(5, base_budget + 1)

        # Domain variance adjustment
        high_variance_domains = [
            MathDomain.CALCULUS,  # Many integration techniques
            MathDomain.LOGIC      # Many proof strategies
        ]

        if problem.domain in high_variance_domains:
            base_budget = min(5, base_budget + 1)

        logger.debug(
            f"[{self.agent_id}] Computed exploration budget: {base_budget} "
            f"(complexity={complexity}, domain={problem.domain.value})"
        )

        return base_budget

    # =======================================================================
    # BDI CONTROL LOOP METHODS
    # =======================================================================

    def deliberate(self) -> Optional[Intention]:
        """
        BDI deliberation process for exploration.

        Compares beliefs (known strategies, past results) against desires
        (finding optimal strategy) to form intentions (strategy recommendations).

        Returns:
            Intention representing strategy exploration plan
        """
        # Default implementation - subclasses can override
        if not self.desires:
            return None

        # Find highest-priority active desire
        for desire in sorted(self.desires, key=lambda d: d.priority, reverse=True):
            if desire.active:  # Fixed W-001: Use 'active' instead of 'achieved'
                # Form intention to explore strategies for this desire
                import uuid
                intention = Intention(
                    plan_id=f"explore_{desire.goal}_{uuid.uuid4().hex[:8]}",  # Fixed W-002: Use plan_id
                    target_desire=desire.goal,  # Fixed W-002: Use goal string, not Desire object
                    steps=['suggest_strategies', 'score_strategies', 'rank_strategies'],
                    current_step=0
                )
                return intention

        return None

    # =======================================================================
    # UTILITY METHODS
    # =======================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'agent_id': self.agent_id,
            'domain': self.domain.value if self.domain else 'universal',
            'strategies_in_library': len(self.strategy_library),
            'strategies_suggested': self.strategies_suggested,
            'strategies_scored': self.strategies_scored,
            'explorations_recorded': self.explorations_recorded
        }

    def __repr__(self) -> str:
        domain_str = self.domain.value if self.domain else 'Universal'
        return f"<{self.__class__.__name__} domain={domain_str} strategies={len(self.strategy_library)}>"
