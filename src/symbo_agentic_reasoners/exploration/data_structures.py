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
EXPLORATION LAYER - DATA STRUCTURES
===================================

Core data structures for the strategic exploration layer (Tier 1.5).

This module defines the fundamental types used by exploration agents to:
1. Represent solution strategies
2. Record exploration attempts and outcomes
3. Rank and prioritize strategies based on learning

REFERENCE:
---------
Implementation Plan: Imagination/Exploration Agents
Phase 1: Core Infrastructure
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
from datetime import datetime
import hashlib
import json

from symbo_agentic_reasoners.agents.base.problem_analysis import (
    MathDomain, StructuredProblem
)


# ===========================================================================
# EXPLORATION OUTCOMES
# ===========================================================================

class ExplorationOutcome(Enum):
    """
    Outcome classification for strategy exploration attempts.

    Used to track and learn from different types of results.
    """
    SUCCESS = 'success'                     # Strategy solved the problem
    FAILURE = 'failure'                     # Complete failure - wrong approach
    PARTIAL = 'partial'                     # Made progress but incomplete
    TIMEOUT = 'timeout'                     # Exceeded time budget
    PRECONDITION_FAILED = 'precondition_failed'  # Strategy not applicable
    ERROR = 'error'                         # Unexpected error during execution

    def is_successful(self) -> bool:
        """Check if outcome represents success"""
        return self == ExplorationOutcome.SUCCESS

    def is_actionable_failure(self) -> bool:
        """Check if failure provides learning value"""
        return self in [
            ExplorationOutcome.FAILURE,
            ExplorationOutcome.PARTIAL,
            ExplorationOutcome.PRECONDITION_FAILED
        ]


# ===========================================================================
# STRATEGY REPRESENTATION
# ===========================================================================

@dataclass
class Strategy:
    """
    Represents a solution strategy to be explored.

    A strategy encodes a high-level approach to solving a mathematical problem,
    including the sequence of techniques to apply, preconditions for applicability,
    and learned success metrics.

    FIELDS:
    ------
    strategy_id: Unique identifier (e.g., 'calc_001')
    name: Human-readable name (e.g., 'Substitution then Integration')
    domain: Mathematical domain this strategy applies to
    techniques: Ordered list of technique names to execute
    preconditions: Dict of conditions that must hold for strategy to apply
    estimated_cost: Resource cost ('low', 'medium', 'high')
    success_rate: Historical success probability [0, 1], updated via learning
    metadata: Additional strategy-specific information

    EXAMPLE:
    -------
    Strategy(
        strategy_id='calc_002',
        name='Substitution then Integration',
        domain=MathDomain.CALCULUS,
        techniques=['identify_substitution', 'apply_substitution', 'integrate_simplified'],
        preconditions={'operation': 'integrate', 'has_composite_function': True},
        estimated_cost='medium',
        success_rate=0.75
    )
    """
    strategy_id: str
    name: str
    domain: MathDomain
    techniques: List[str]
    preconditions: Dict[str, Any]
    estimated_cost: str = 'medium'  # 'low', 'medium', 'high'
    success_rate: float = 0.5       # Initial prior, updated via Bayesian learning
    metadata: Dict[str, Any] = field(default_factory=dict)

    def matches_problem(self, problem: StructuredProblem) -> float:
        """
        Compute confidence [0, 1] that strategy applies to problem.

        Checks preconditions against problem metadata and features.
        Returns a confidence score where:
        - 1.0: All preconditions perfectly matched
        - 0.5-0.9: Partial match or uncertain
        - 0.0: Preconditions clearly violated

        Args:
            problem: The structured problem to match against

        Returns:
            Confidence score [0, 1]
        """
        # Check domain match
        if self.domain != problem.domain and self.domain != MathDomain.UNKNOWN:
            # Allow cross-domain strategies but penalize
            domain_penalty = 0.3
        else:
            domain_penalty = 0.0

        # Check preconditions
        matched = 0
        total = len(self.preconditions)

        if total == 0:
            # No preconditions means always applicable
            return 1.0 - domain_penalty

        for key, expected_value in self.preconditions.items():
            actual_value = problem.metadata.get(key)

            if actual_value is None:
                # Unknown - assume possible match
                matched += 0.5
            elif isinstance(expected_value, list):
                # Check if actual value is in list
                if actual_value in expected_value:
                    matched += 1.0
                else:
                    matched += 0.0
            elif isinstance(expected_value, dict):
                # Handle range checks (e.g., {'max': 4})
                if 'max' in expected_value and isinstance(actual_value, (int, float)):
                    if actual_value <= expected_value['max']:
                        matched += 1.0
                    else:
                        matched += 0.0
                elif 'min' in expected_value and isinstance(actual_value, (int, float)):
                    if actual_value >= expected_value['min']:
                        matched += 1.0
                    else:
                        matched += 0.0
                else:
                    matched += 0.5  # Unknown comparison
            elif actual_value == expected_value:
                matched += 1.0
            else:
                matched += 0.0

        confidence = (matched / total) - domain_penalty
        return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

    def to_execution_plan(self) -> List[str]:
        """
        Convert strategy to concrete execution plan.

        Maps technique names to supervisor/specialist calls.

        Returns:
            List of technique names in execution order
        """
        return self.techniques.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for storage"""
        return {
            'strategy_id': self.strategy_id,
            'name': self.name,
            'domain': self.domain.value,
            'techniques': self.techniques,
            'preconditions': self.preconditions,
            'estimated_cost': self.estimated_cost,
            'success_rate': self.success_rate,
            'metadata': self.metadata
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Strategy':
        """Deserialize from dictionary"""
        return Strategy(
            strategy_id=data['strategy_id'],
            name=data['name'],
            domain=MathDomain(data['domain']),
            techniques=data['techniques'],
            preconditions=data['preconditions'],
            estimated_cost=data.get('estimated_cost', 'medium'),
            success_rate=data.get('success_rate', 0.5),
            metadata=data.get('metadata', {})
        )


# ===========================================================================
# EXPLORATION RESULT
# ===========================================================================

@dataclass
class ExplorationResult:
    """
    Records the result of exploring a strategy on a problem.

    This is the fundamental learning unit - each exploration attempt
    generates a result that is stored in the knowledge management system
    for future strategy ranking and pattern recognition.

    FIELDS:
    ------
    exploration_id: Unique ID for this exploration attempt
    strategy: The strategy that was explored
    problem_signature: Hash of problem characteristics (for similarity matching)
    outcome: Result classification (SUCCESS, FAILURE, etc.)
    execution_time: Time taken in seconds
    resource_cost: Normalized resource usage [0, 1]
    error_type: Failure classification if outcome is not SUCCESS
    partial_progress: Description of what was accomplished if PARTIAL
    lessons_learned: Insights extracted from this attempt
    timestamp: When exploration occurred

    LEARNING INTEGRATION:
    --------------------
    Results are stored in vector DB with embeddings based on:
    - Problem features (domain, operation, complexity)
    - Strategy techniques
    - Outcome type
    - Error patterns (if failed)

    This enables similarity-based retrieval: "What worked for similar problems?"
    """
    exploration_id: str
    strategy: Strategy
    problem_signature: str
    outcome: ExplorationOutcome
    execution_time: float = 0.0
    resource_cost: float = 0.0  # Normalized [0, 1]
    error_type: Optional[str] = None
    partial_progress: Optional[Dict[str, Any]] = None
    lessons_learned: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for vector DB storage"""
        return {
            'exploration_id': self.exploration_id,
            'strategy': self.strategy.to_dict(),
            'problem_signature': self.problem_signature,
            'outcome': self.outcome.value,
            'execution_time': self.execution_time,
            'resource_cost': self.resource_cost,
            'error_type': self.error_type,
            'partial_progress': self.partial_progress,
            'lessons_learned': self.lessons_learned,
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ExplorationResult':
        """Deserialize from dictionary"""
        return ExplorationResult(
            exploration_id=data['exploration_id'],
            strategy=Strategy.from_dict(data['strategy']),
            problem_signature=data['problem_signature'],
            outcome=ExplorationOutcome(data['outcome']),
            execution_time=data.get('execution_time', 0.0),
            resource_cost=data.get('resource_cost', 0.0),
            error_type=data.get('error_type'),
            partial_progress=data.get('partial_progress'),
            lessons_learned=data.get('lessons_learned', []),
            timestamp=datetime.fromisoformat(data['timestamp'])
        )

    def to_embedding_text(self) -> str:
        """
        Convert to text representation for vector embedding.

        This text is fed to the embedding model to create a vector representation
        for similarity-based retrieval in the knowledge management system.

        Returns:
            Text combining problem, strategy, and outcome information
        """
        parts = [
            f"Problem: {self.problem_signature}",
            f"Strategy: {self.strategy.name}",
            f"Domain: {self.strategy.domain.value}",
            f"Techniques: {', '.join(self.strategy.techniques)}",
            f"Outcome: {self.outcome.value}",
        ]

        if self.error_type:
            parts.append(f"Error: {self.error_type}")

        if self.lessons_learned:
            parts.append(f"Lessons: {'; '.join(self.lessons_learned)}")

        return " | ".join(parts)


# ===========================================================================
# STRATEGY RANKING
# ===========================================================================

@dataclass
class StrategyRanking:
    """
    Ranked list of strategies for a specific problem.

    Output of the exploration layer's strategy generation process.
    Contains strategies ordered by predicted success probability,
    along with metadata about the ranking decision.

    FIELDS:
    ------
    problem_signature: Hash identifying the problem being solved
    ranked_strategies: List of (Strategy, confidence_score) tuples
    exploration_budget: How many strategies to try before fallback
    estimated_solve_time: Predicted total time if all strategies tried
    reasoning: Human-readable explanation of ranking rationale

    USAGE:
    -----
    The MainOrchestrator iterates through ranked_strategies in order,
    trying each until one succeeds or the budget is exhausted.

    EXAMPLE:
    -------
    ranking = StrategyRanking(
        problem_signature='integrate_sin_composite_abc123',
        ranked_strategies=[
            (substitution_strategy, 0.85),
            (integration_by_parts, 0.62),
            (numerical_fallback, 0.95)
        ],
        exploration_budget=3,
        estimated_solve_time=4.5,
        reasoning="Substitution has 75% historical success on composite trig functions"
    )
    """
    problem_signature: str
    ranked_strategies: List[Tuple[Strategy, float]]  # (strategy, confidence_score)
    exploration_budget: int = 3
    estimated_solve_time: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_top_n(self, n: int) -> List[Tuple[Strategy, float]]:
        """Get top N strategies"""
        return self.ranked_strategies[:n]

    def get_by_threshold(self, threshold: float) -> List[Tuple[Strategy, float]]:
        """Get all strategies above confidence threshold"""
        return [(s, conf) for s, conf in self.ranked_strategies if conf >= threshold]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'problem_signature': self.problem_signature,
            'ranked_strategies': [
                (s.to_dict(), conf) for s, conf in self.ranked_strategies
            ],
            'exploration_budget': self.exploration_budget,
            'estimated_solve_time': self.estimated_solve_time,
            'reasoning': self.reasoning,
            'metadata': self.metadata
        }


# ===========================================================================
# UTILITY FUNCTIONS
# ===========================================================================

def hash_problem(problem: StructuredProblem) -> str:
    """
    Generate a signature hash for a problem.

    Creates a stable hash based on problem characteristics for:
    - Similarity matching in knowledge retrieval
    - Identifying duplicate problems
    - Grouping related problems in learning

    Args:
        problem: The structured problem to hash

    Returns:
        Hex string hash (e.g., 'a3f9c2d8...')
    """
    # Combine key problem features
    features = {
        'domain': problem.domain.value,
        'type': problem.problem_type.value,
        'operation': problem.metadata.get('operation', 'unknown'),
        'input': problem.raw_input[:100]  # Truncate for stability
    }

    # Sort keys for deterministic hashing
    feature_str = json.dumps(features, sort_keys=True)
    return hashlib.sha256(feature_str.encode()).hexdigest()[:16]


def estimate_complexity(problem: StructuredProblem) -> str:
    """
    Estimate problem complexity ('low', 'medium', 'high').

    Heuristic based on:
    - Input length
    - Nested structure depth
    - Domain-specific complexity indicators

    Args:
        problem: The structured problem

    Returns:
        Complexity estimate: 'low', 'medium', or 'high'
    """
    # Basic heuristic - can be enhanced with more sophisticated analysis
    input_len = len(problem.raw_input)

    # Check for complexity indicators in metadata
    has_nested = problem.metadata.get('has_nested_structure', False)
    degree = problem.metadata.get('degree', 1)

    if input_len < 50 and not has_nested and degree <= 2:
        return 'low'
    elif input_len < 150 and degree <= 4:
        return 'medium'
    else:
        return 'high'
