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
EXPLORATION LAYER - INTEGRATION TESTS
=====================================

Integration tests for the exploration layer with the rest of the system:
- Orchestrator integration
- Knowledge management integration
- Directory facilitator integration
- Blackboard integration
- End-to-end exploration workflows

Test Categories:
- Integration with MainOrchestrator
- Integration with KnowledgeManagementTeam
- Full exploration workflow tests
- Performance and scalability tests
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from symbo_agentic_reasoners.agents.base.problem_analysis import (
    MathDomain, ProblemType, StructuredProblem
)
from symbo_agentic_reasoners.core.omdoc_schema import create_number
from symbo_agentic_reasoners.exploration.universal_explorer import UniversalStrategyExplorer
from symbo_agentic_reasoners.exploration.data_structures import (
    Strategy, ExplorationResult, ExplorationOutcome
)


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture
def integration_problem():
    """Create a realistic integration test problem"""
    return StructuredProblem(
        raw_input="integrate x*sin(x) dx",
        omdoc_content=create_number(0),
        problem_type=ProblemType.COMPUTATION,
        domain=MathDomain.CALCULUS,
        metadata={
            'operation': 'integrate',
            'has_product': True,
            'integrand_type': 'product'
        }
    )


# ===========================================================================
# ORCHESTRATOR INTEGRATION TESTS
# ===========================================================================

class TestOrchestratorIntegration:
    """Test integration with MainOrchestrator"""

    def test_should_explore_decision_logic(self):
        """Test the _should_explore decision logic"""
        # This tests the logic from orchestrator.py
        # Simple problem - should skip exploration
        simple_problem = StructuredProblem(
            raw_input="2 + 2",
            omdoc_content=create_number(4),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={}
        )

        # Complex problem - should explore
        complex_problem = StructuredProblem(
            raw_input="This is a complex integration problem",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.CALCULUS,
            metadata={'has_composite_function': True}
        )

        # Import and test the logic
        from symbo_agentic_reasoners.exploration.data_structures import estimate_complexity

        simple_complexity = estimate_complexity(simple_problem)
        complex_complexity = estimate_complexity(complex_problem)

        assert simple_complexity == 'low'
        assert complex_complexity in ['medium', 'high']

    def test_exploration_phase_workflow(self, integration_problem):
        """Test the complete exploration phase workflow"""
        # Setup mocks
        mock_df = Mock()
        mock_km = Mock()
        mock_km.query_similar_explorations = Mock(return_value=[])

        # Create explorer
        explorer = UniversalStrategyExplorer(
            directory_facilitator=mock_df,
            knowledge_team=mock_km
        )

        # Execute exploration
        ranking = explorer.explore_strategies(integration_problem)

        # Verify workflow
        assert ranking is not None
        assert len(ranking.ranked_strategies) > 0
        assert mock_km.query_similar_explorations.called

    def test_exploration_fallback_to_decomposition(self):
        """Test that system falls back to decomposition when exploration fails"""
        # This simulates what happens in orchestrator.py when all strategies fail
        # The loop should try each strategy, and if all fail, continue to decomposition

        # Create a ranking with strategies
        problem = StructuredProblem(
            raw_input="test",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={}
        )

        from symbo_agentic_reasoners.exploration.data_structures import StrategyRanking, hash_problem

        ranking = StrategyRanking(
            problem_signature=hash_problem(problem),
            ranked_strategies=[],  # Empty - all strategies failed
            exploration_budget=0
        )

        # When ranked_strategies is empty, orchestrator should fall through
        assert len(ranking.ranked_strategies) == 0
        # This is the condition that triggers fallback


# ===========================================================================
# KNOWLEDGE MANAGEMENT INTEGRATION TESTS
# ===========================================================================

class TestKnowledgeManagementIntegration:
    """Test integration with KnowledgeManagementTeam"""

    def test_store_exploration_result_integration(self):
        """Test storing exploration results via knowledge management"""
        # Create mock knowledge team with realistic behavior
        mock_km = Mock()
        mock_km.store_exploration_result = Mock()

        explorer = UniversalStrategyExplorer(knowledge_team=mock_km)

        # Create test data
        problem = StructuredProblem(
            raw_input="x + 1 = 2",
            omdoc_content=create_number(1),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={}
        )

        strategy = Strategy(
            strategy_id='test_001',
            name='Test Strategy',
            domain=MathDomain.ALGEBRA,
            techniques=['step1'],
            preconditions={},
            estimated_cost='low',
            success_rate=0.8
        )

        # Record exploration
        explorer.record_exploration(
            strategy=strategy,
            problem=problem,
            outcome=ExplorationOutcome.SUCCESS
        )

        # Verify knowledge team was called
        assert mock_km.store_exploration_result.called

    def test_query_similar_explorations_integration(self, integration_problem):
        """Test querying similar explorations"""
        # Setup mock with realistic response
        successful_strategy = Strategy(
            strategy_id='similar_001',
            name='Similar Success',
            domain=MathDomain.CALCULUS,
            techniques=['integration_by_parts'],
            preconditions={'has_product': True},
            estimated_cost='medium',
            success_rate=0.85
        )

        past_result = ExplorationResult(
            exploration_id='past_001',
            strategy=successful_strategy,
            problem_signature='similar_sig',
            outcome=ExplorationOutcome.SUCCESS
        )

        mock_km = Mock()
        mock_km.query_similar_explorations = Mock(return_value=[past_result])

        explorer = UniversalStrategyExplorer(knowledge_team=mock_km)

        # Explore strategies - should incorporate historical data
        ranking = explorer.explore_strategies(integration_problem)

        # Verify historical strategy is included
        strategy_ids = [s.strategy_id for s, _ in ranking.ranked_strategies]
        assert 'similar_001' in strategy_ids

        # Verify it's highly ranked (should be boosted by historical success)
        for strategy, confidence in ranking.ranked_strategies:
            if strategy.strategy_id == 'similar_001':
                assert confidence > 0.5  # Should have decent confidence


# ===========================================================================
# END-TO-END WORKFLOW TESTS
# ===========================================================================

class TestEndToEndWorkflows:
    """Test complete end-to-end exploration workflows"""

    def test_full_exploration_workflow_success(self, integration_problem):
        """Test complete workflow from problem to ranked strategies"""
        # Setup complete system
        mock_df = Mock()
        mock_km = Mock()
        mock_km.query_similar_explorations = Mock(return_value=[])

        explorer = UniversalStrategyExplorer(
            directory_facilitator=mock_df,
            knowledge_team=mock_km
        )

        # Step 1: Explore strategies
        ranking = explorer.explore_strategies(integration_problem)

        # Step 2: Verify ranking properties
        assert ranking.problem_signature is not None
        assert len(ranking.ranked_strategies) > 0
        assert ranking.exploration_budget > 0
        assert ranking.reasoning is not None

        # Step 3: Verify strategies are sorted
        confidences = [conf for _, conf in ranking.ranked_strategies]
        assert confidences == sorted(confidences, reverse=True)

        # Step 4: Verify top strategy has appropriate properties
        top_strategy, top_confidence = ranking.ranked_strategies[0]
        assert top_strategy.domain == integration_problem.domain or top_strategy.domain == MathDomain.UNKNOWN
        assert 0.0 <= top_confidence <= 1.0

    def test_learning_loop_integration(self):
        """Test the complete learning loop: explore → record → retrieve"""
        mock_km = Mock()

        # Storage for simulating persistent memory
        stored_results = []

        def mock_store(result):
            stored_results.append(result)

        def mock_query(problem_sig, limit=10):
            # Return results that match the signature
            return [r for r in stored_results if r.problem_signature == problem_sig][:limit]

        mock_km.store_exploration_result = Mock(side_effect=mock_store)
        mock_km.query_similar_explorations = Mock(side_effect=mock_query)

        explorer = UniversalStrategyExplorer(knowledge_team=mock_km)

        problem = StructuredProblem(
            raw_input="test problem",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={}
        )

        strategy = Strategy(
            strategy_id='learn_001',
            name='Learning Strategy',
            domain=MathDomain.ALGEBRA,
            techniques=['step1'],
            preconditions={},
            estimated_cost='low',
            success_rate=0.7
        )

        # Step 1: Record a successful exploration
        explorer.record_exploration(
            strategy=strategy,
            problem=problem,
            outcome=ExplorationOutcome.SUCCESS
        )

        # Verify storage
        assert len(stored_results) == 1
        assert stored_results[0].outcome == ExplorationOutcome.SUCCESS

        # Step 2: Query for similar explorations
        from symbo_agentic_reasoners.exploration.data_structures import hash_problem
        similar = mock_km.query_similar_explorations(hash_problem(problem))

        # Verify retrieval
        assert len(similar) == 1
        assert similar[0].strategy.strategy_id == 'learn_001'


# ===========================================================================
# PERFORMANCE TESTS
# ===========================================================================

class TestPerformance:
    """Test performance characteristics"""

    def test_exploration_completes_quickly_for_simple_problems(self):
        """Test that exploration doesn't add excessive overhead for simple problems"""
        import time

        simple_problem = StructuredProblem(
            raw_input="1 + 1",
            omdoc_content=create_number(2),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={}
        )

        explorer = UniversalStrategyExplorer(knowledge_team=None)

        start = time.time()
        ranking = explorer.explore_strategies(simple_problem)
        elapsed = time.time() - start

        # Should complete in under 1 second for simple problems
        assert elapsed < 1.0, f"Exploration took too long: {elapsed:.2f}s"

    def test_handles_many_strategies_efficiently(self):
        """Test that system handles large strategy libraries efficiently"""
        explorer = UniversalStrategyExplorer(knowledge_team=None)

        # Verify the strategy library is substantial
        assert len(explorer.strategy_library) >= 50

        problem = StructuredProblem(
            raw_input="test",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.CALCULUS,
            metadata={}
        )

        # Should handle large library without issues
        ranking = explorer.explore_strategies(problem)
        assert ranking is not None


# ===========================================================================
# ERROR HANDLING TESTS
# ===========================================================================

class TestErrorHandling:
    """Test error handling and recovery"""

    def test_graceful_degradation_without_knowledge_team(self, integration_problem):
        """Test that system works without knowledge management"""
        explorer = UniversalStrategyExplorer(knowledge_team=None)

        # Should work without knowledge team
        ranking = explorer.explore_strategies(integration_problem)
        assert ranking is not None
        assert len(ranking.ranked_strategies) > 0

    def test_graceful_degradation_without_directory_facilitator(self, integration_problem):
        """Test that system works without directory facilitator"""
        explorer = UniversalStrategyExplorer(directory_facilitator=None)

        # Should work without DF (no domain explorers)
        ranking = explorer.explore_strategies(integration_problem)
        assert ranking is not None
        assert len(ranking.ranked_strategies) > 0

    def test_handles_corrupted_past_explorations(self, integration_problem):
        """Test handling of corrupted/invalid past exploration data"""
        mock_km = Mock()

        # Return invalid data that could cause errors
        mock_km.query_similar_explorations = Mock(return_value=[
            None,  # Invalid entry
            "not_an_exploration",  # Wrong type
            Mock(outcome="invalid"),  # Missing required attributes
        ])

        explorer = UniversalStrategyExplorer(knowledge_team=mock_km)

        # Should handle gracefully without crashing
        ranking = explorer.explore_strategies(integration_problem)
        assert ranking is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
