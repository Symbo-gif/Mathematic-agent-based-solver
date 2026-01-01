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
EXPLORATION LAYER - DATA STRUCTURES TESTS
=========================================

Comprehensive test suite for exploration data structures:
- Strategy
- ExplorationResult
- StrategyRanking
- ExplorationOutcome
- Utility functions

Test Categories:
- Unit tests for each data structure
- Serialization/deserialization tests
- Edge case tests
- Integration tests
"""

import pytest
from datetime import datetime, timedelta
from symbo_agentic_reasoners.agents.base.problem_analysis import (
    MathDomain, ProblemType, StructuredProblem
)
from symbo_agentic_reasoners.core.omdoc_schema import create_number
from symbo_agentic_reasoners.exploration.data_structures import (
    Strategy, ExplorationResult, StrategyRanking, ExplorationOutcome,
    hash_problem, estimate_complexity
)


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture
def simple_problem():
    """Create a simple algebraic problem"""
    return StructuredProblem(
        raw_input="x + 2 = 5",
        omdoc_content=create_number(3),
        problem_type=ProblemType.COMPUTATION,
        domain=MathDomain.ALGEBRA,
        metadata={'operation': 'solve', 'equation_type': 'linear'}
    )


@pytest.fixture
def complex_problem():
    """Create a complex calculus problem"""
    return StructuredProblem(
        raw_input="integrate sin(x^2 + 3x) * cos(x) dx",
        omdoc_content=create_number(0),
        problem_type=ProblemType.COMPUTATION,
        domain=MathDomain.CALCULUS,
        metadata={
            'operation': 'integrate',
            'has_composite_function': True,
            'has_product': True
        }
    )


@pytest.fixture
def sample_strategy():
    """Create a sample strategy"""
    return Strategy(
        strategy_id='test_001',
        name='Test Strategy',
        domain=MathDomain.ALGEBRA,
        techniques=['step1', 'step2', 'step3'],
        preconditions={'operation': 'solve', 'equation_type': 'linear'},
        estimated_cost='low',
        success_rate=0.8
    )


# ===========================================================================
# STRATEGY TESTS
# ===========================================================================

class TestStrategy:
    """Test Strategy dataclass functionality"""

    def test_strategy_creation(self, sample_strategy):
        """Test basic strategy creation"""
        assert sample_strategy.strategy_id == 'test_001'
        assert sample_strategy.name == 'Test Strategy'
        assert sample_strategy.domain == MathDomain.ALGEBRA
        assert len(sample_strategy.techniques) == 3
        assert sample_strategy.success_rate == 0.8

    def test_matches_problem_exact_match(self, sample_strategy, simple_problem):
        """Test strategy matching with exact precondition match"""
        confidence = sample_strategy.matches_problem(simple_problem)
        assert confidence == 1.0, "Exact match should return 1.0"

    def test_matches_problem_partial_match(self, simple_problem):
        """Test strategy matching with partial precondition match"""
        strategy = Strategy(
            strategy_id='test_002',
            name='Partial Match Strategy',
            domain=MathDomain.ALGEBRA,
            techniques=['step1'],
            preconditions={
                'operation': 'solve',
                'equation_type': 'quadratic'  # Doesn't match simple_problem
            },
            estimated_cost='medium',
            success_rate=0.5
        )
        confidence = strategy.matches_problem(simple_problem)
        assert confidence == 0.5, "Partial match should return 0.5"

    def test_matches_problem_domain_mismatch(self, sample_strategy, complex_problem):
        """Test strategy matching with domain mismatch"""
        # sample_strategy is ALGEBRA, complex_problem is CALCULUS
        confidence = sample_strategy.matches_problem(complex_problem)
        assert confidence < 1.0, "Domain mismatch should penalize confidence"

    def test_matches_problem_no_preconditions(self, simple_problem):
        """Test strategy with no preconditions (always applicable)"""
        strategy = Strategy(
            strategy_id='test_003',
            name='Universal Strategy',
            domain=MathDomain.ALGEBRA,
            techniques=['universal_step'],
            preconditions={},
            estimated_cost='high',
            success_rate=0.3
        )
        confidence = strategy.matches_problem(simple_problem)
        assert confidence == 1.0, "No preconditions means always applicable"

    def test_matches_problem_list_precondition(self, simple_problem):
        """Test strategy with list-based preconditions"""
        strategy = Strategy(
            strategy_id='test_004',
            name='List Precondition Strategy',
            domain=MathDomain.ALGEBRA,
            techniques=['step1'],
            preconditions={
                'operation': ['solve', 'simplify', 'factor']
            },
            estimated_cost='low',
            success_rate=0.7
        )
        confidence = strategy.matches_problem(simple_problem)
        assert confidence == 1.0, "operation='solve' is in the list"

    def test_matches_problem_range_precondition(self):
        """Test strategy with range-based preconditions"""
        problem = StructuredProblem(
            raw_input="x^3 + 2x^2 - x + 5 = 0",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={'degree': 3}
        )

        strategy = Strategy(
            strategy_id='test_005',
            name='Range Precondition Strategy',
            domain=MathDomain.ALGEBRA,
            techniques=['step1'],
            preconditions={'degree': {'max': 4}},
            estimated_cost='medium',
            success_rate=0.85
        )

        confidence = strategy.matches_problem(problem)
        assert confidence == 1.0, "degree=3 is <= max=4"

    def test_to_execution_plan(self, sample_strategy):
        """Test conversion to execution plan"""
        plan = sample_strategy.to_execution_plan()
        assert plan == ['step1', 'step2', 'step3']
        assert plan is not sample_strategy.techniques, "Should return a copy"

    def test_serialization(self, sample_strategy):
        """Test strategy serialization and deserialization"""
        # Serialize
        data = sample_strategy.to_dict()
        assert data['strategy_id'] == 'test_001'
        assert data['domain'] == 'Algebra'
        assert data['success_rate'] == 0.8

        # Deserialize
        restored = Strategy.from_dict(data)
        assert restored.strategy_id == sample_strategy.strategy_id
        assert restored.domain == sample_strategy.domain
        assert restored.success_rate == sample_strategy.success_rate


# ===========================================================================
# EXPLORATION RESULT TESTS
# ===========================================================================

class TestExplorationResult:
    """Test ExplorationResult dataclass functionality"""

    def test_exploration_result_creation(self, sample_strategy, simple_problem):
        """Test basic exploration result creation"""
        result = ExplorationResult(
            exploration_id='exp_001',
            strategy=sample_strategy,
            problem_signature=hash_problem(simple_problem),
            outcome=ExplorationOutcome.SUCCESS,
            execution_time=1.5,
            resource_cost=0.3
        )

        assert result.exploration_id == 'exp_001'
        assert result.strategy == sample_strategy
        assert result.outcome == ExplorationOutcome.SUCCESS
        assert result.execution_time == 1.5

    def test_exploration_outcome_is_successful(self):
        """Test ExplorationOutcome success checking"""
        assert ExplorationOutcome.SUCCESS.is_successful()
        assert not ExplorationOutcome.FAILURE.is_successful()
        assert not ExplorationOutcome.TIMEOUT.is_successful()

    def test_exploration_outcome_is_actionable_failure(self):
        """Test ExplorationOutcome actionable failure checking"""
        assert ExplorationOutcome.FAILURE.is_actionable_failure()
        assert ExplorationOutcome.PARTIAL.is_actionable_failure()
        assert ExplorationOutcome.PRECONDITION_FAILED.is_actionable_failure()
        assert not ExplorationOutcome.SUCCESS.is_actionable_failure()
        assert not ExplorationOutcome.ERROR.is_actionable_failure()

    def test_to_embedding_text(self, sample_strategy, simple_problem):
        """Test conversion to embedding text"""
        result = ExplorationResult(
            exploration_id='exp_002',
            strategy=sample_strategy,
            problem_signature=hash_problem(simple_problem),
            outcome=ExplorationOutcome.SUCCESS,
            lessons_learned=['Lesson 1', 'Lesson 2']
        )

        text = result.to_embedding_text()
        assert 'Test Strategy' in text
        assert 'success' in text.lower()  # outcome.value is lowercase
        assert 'Lesson 1' in text

    def test_serialization(self, sample_strategy, simple_problem):
        """Test exploration result serialization"""
        result = ExplorationResult(
            exploration_id='exp_003',
            strategy=sample_strategy,
            problem_signature=hash_problem(simple_problem),
            outcome=ExplorationOutcome.FAILURE,
            error_type='ValueError'
        )

        data = result.to_dict()
        assert data['exploration_id'] == 'exp_003'
        assert data['outcome'] == 'failure'
        assert data['error_type'] == 'ValueError'

        restored = ExplorationResult.from_dict(data)
        assert restored.exploration_id == result.exploration_id
        assert restored.outcome == result.outcome


# ===========================================================================
# STRATEGY RANKING TESTS
# ===========================================================================

class TestStrategyRanking:
    """Test StrategyRanking dataclass functionality"""

    def test_strategy_ranking_creation(self, sample_strategy, simple_problem):
        """Test basic strategy ranking creation"""
        ranking = StrategyRanking(
            problem_signature=hash_problem(simple_problem),
            ranked_strategies=[(sample_strategy, 0.95)],
            exploration_budget=3,
            estimated_solve_time=2.5,
            reasoning="High confidence match"
        )

        assert len(ranking.ranked_strategies) == 1
        assert ranking.exploration_budget == 3
        assert ranking.reasoning == "High confidence match"

    def test_get_top_n(self, simple_problem):
        """Test getting top N strategies"""
        strategies = [
            (Strategy('s1', 'Strategy 1', MathDomain.ALGEBRA, ['t1'], {}, 'low', 0.9), 0.9),
            (Strategy('s2', 'Strategy 2', MathDomain.ALGEBRA, ['t2'], {}, 'medium', 0.7), 0.7),
            (Strategy('s3', 'Strategy 3', MathDomain.ALGEBRA, ['t3'], {}, 'high', 0.5), 0.5),
        ]

        ranking = StrategyRanking(
            problem_signature=hash_problem(simple_problem),
            ranked_strategies=strategies,
            exploration_budget=3
        )

        top_2 = ranking.get_top_n(2)
        assert len(top_2) == 2
        assert top_2[0][1] == 0.9
        assert top_2[1][1] == 0.7

    def test_get_by_threshold(self, simple_problem):
        """Test getting strategies above confidence threshold"""
        strategies = [
            (Strategy('s1', 'Strategy 1', MathDomain.ALGEBRA, ['t1'], {}, 'low', 0.9), 0.9),
            (Strategy('s2', 'Strategy 2', MathDomain.ALGEBRA, ['t2'], {}, 'medium', 0.7), 0.7),
            (Strategy('s3', 'Strategy 3', MathDomain.ALGEBRA, ['t3'], {}, 'high', 0.5), 0.5),
        ]

        ranking = StrategyRanking(
            problem_signature=hash_problem(simple_problem),
            ranked_strategies=strategies,
            exploration_budget=3
        )

        high_confidence = ranking.get_by_threshold(0.75)
        assert len(high_confidence) == 1
        assert high_confidence[0][1] == 0.9


# ===========================================================================
# UTILITY FUNCTION TESTS
# ===========================================================================

class TestUtilityFunctions:
    """Test utility functions"""

    def test_hash_problem_consistent(self, simple_problem):
        """Test that hash_problem produces consistent hashes"""
        hash1 = hash_problem(simple_problem)
        hash2 = hash_problem(simple_problem)
        assert hash1 == hash2, "Same problem should produce same hash"

    def test_hash_problem_different(self, simple_problem, complex_problem):
        """Test that different problems produce different hashes"""
        hash1 = hash_problem(simple_problem)
        hash2 = hash_problem(complex_problem)
        assert hash1 != hash2, "Different problems should produce different hashes"

    def test_estimate_complexity_low(self, simple_problem):
        """Test complexity estimation for simple problems"""
        complexity = estimate_complexity(simple_problem)
        assert complexity == 'low'

    def test_estimate_complexity_high(self, complex_problem):
        """Test complexity estimation for complex problems"""
        # Make the problem even more complex
        complex_problem.metadata['has_nested_structure'] = True
        complex_problem.metadata['degree'] = 5

        complexity = estimate_complexity(complex_problem)
        assert complexity == 'high'

    def test_estimate_complexity_medium(self):
        """Test complexity estimation for medium problems"""
        problem = StructuredProblem(
            raw_input="This is a moderately complex problem with some structure",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={'degree': 3}
        )

        complexity = estimate_complexity(problem)
        assert complexity == 'medium'


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_strategy_empty_techniques(self):
        """Test strategy with empty techniques list"""
        strategy = Strategy(
            strategy_id='edge_001',
            name='Empty Techniques',
            domain=MathDomain.ALGEBRA,
            techniques=[],  # Edge case: empty list
            preconditions={},
            estimated_cost='low',
            success_rate=0.5
        )

        plan = strategy.to_execution_plan()
        assert plan == []

    def test_strategy_negative_success_rate(self):
        """Test strategy creation with invalid success rate (should be clamped)"""
        # Note: Current implementation doesn't validate, but it should
        strategy = Strategy(
            strategy_id='edge_002',
            name='Invalid Success Rate',
            domain=MathDomain.ALGEBRA,
            techniques=['step1'],
            preconditions={},
            estimated_cost='low',
            success_rate=-0.5  # Invalid
        )

        # This should ideally be validated/clamped
        assert strategy.success_rate == -0.5  # Current behavior

    def test_strategy_matches_problem_missing_metadata(self, sample_strategy):
        """Test strategy matching when problem metadata is incomplete"""
        problem = StructuredProblem(
            raw_input="incomplete problem",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={}  # Empty metadata
        )

        # Should handle gracefully with partial matches
        confidence = sample_strategy.matches_problem(problem)
        assert 0.0 <= confidence <= 1.0

    def test_exploration_result_with_very_long_lessons(self, sample_strategy, simple_problem):
        """Test exploration result with very long lessons_learned"""
        long_lessons = ['Lesson ' + 'x' * 1000 for _ in range(100)]

        result = ExplorationResult(
            exploration_id='edge_003',
            strategy=sample_strategy,
            problem_signature=hash_problem(simple_problem),
            outcome=ExplorationOutcome.SUCCESS,
            lessons_learned=long_lessons
        )

        # Should handle large lessons without issues
        assert len(result.lessons_learned) == 100

    def test_strategy_ranking_empty_list(self, simple_problem):
        """Test strategy ranking with no strategies"""
        ranking = StrategyRanking(
            problem_signature=hash_problem(simple_problem),
            ranked_strategies=[],  # Edge case: no strategies
            exploration_budget=0
        )

        assert ranking.get_top_n(5) == []
        assert ranking.get_by_threshold(0.5) == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
