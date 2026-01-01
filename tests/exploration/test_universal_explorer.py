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
EXPLORATION LAYER - UNIVERSAL EXPLORER TESTS
============================================

Comprehensive test suite for UniversalStrategyExplorer:
- Strategy generation and ranking
- Multi-factor scoring algorithm
- Learning integration
- Feature extraction
- Edge cases and error handling

Test Categories:
- Unit tests for strategy exploration
- Integration tests with knowledge management
- Performance tests
- Security tests
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from symbo_agentic_reasoners.agents.base.problem_analysis import (
    MathDomain, ProblemType, StructuredProblem
)
from symbo_agentic_reasoners.core.omdoc_schema import create_number
from symbo_agentic_reasoners.exploration.universal_explorer import UniversalStrategyExplorer
from symbo_agentic_reasoners.exploration.data_structures import (
    Strategy, ExplorationResult, ExplorationOutcome, hash_problem
)


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture
def mock_directory_facilitator():
    """Create mock directory facilitator"""
    df = Mock()
    df.search = Mock(return_value=[])
    df.register = Mock()
    return df


@pytest.fixture
def mock_knowledge_team():
    """Create mock knowledge management team"""
    km = Mock()
    km.query_similar_explorations = Mock(return_value=[])
    km.store_exploration_result = Mock()
    km.retrieve_successful_strategies = Mock(return_value=[])
    return km


@pytest.fixture
def mock_blackboard():
    """Create mock blackboard"""
    return Mock()


@pytest.fixture
def universal_explorer(mock_directory_facilitator, mock_knowledge_team, mock_blackboard):
    """Create UniversalStrategyExplorer instance"""
    return UniversalStrategyExplorer(
        agent_id='test_explorer_001',
        directory_facilitator=mock_directory_facilitator,
        blackboard=mock_blackboard,
        knowledge_team=mock_knowledge_team
    )


@pytest.fixture
def calculus_problem():
    """Create a calculus integration problem"""
    return StructuredProblem(
        raw_input="integrate sin(x) dx",
        omdoc_content=create_number(0),
        problem_type=ProblemType.COMPUTATION,
        domain=MathDomain.CALCULUS,
        metadata={
            'operation': 'integrate',
            'integrand_type': 'trigonometric',
            'has_composite_function': False
        }
    )


@pytest.fixture
def algebra_problem():
    """Create an algebra problem"""
    return StructuredProblem(
        raw_input="x^2 - 5x + 6 = 0",
        omdoc_content=create_number(0),
        problem_type=ProblemType.COMPUTATION,
        domain=MathDomain.ALGEBRA,
        metadata={
            'operation': 'solve',
            'equation_type': 'quadratic',
            'degree': 2
        }
    )


# ===========================================================================
# INITIALIZATION TESTS
# ===========================================================================

class TestInitialization:
    """Test UniversalStrategyExplorer initialization"""

    def test_initialization_with_all_dependencies(self, universal_explorer):
        """Test successful initialization with all dependencies"""
        assert universal_explorer.agent_id == 'test_explorer_001'
        assert universal_explorer.domain is None  # Universal has no specific domain
        assert len(universal_explorer.strategy_library) > 0
        assert universal_explorer.explorations_performed == 0

    def test_initialization_without_df(self, mock_knowledge_team, mock_blackboard):
        """Test initialization without directory facilitator"""
        explorer = UniversalStrategyExplorer(
            directory_facilitator=None,
            blackboard=mock_blackboard,
            knowledge_team=mock_knowledge_team
        )

        assert explorer.df is None
        # Should still initialize successfully

    def test_initialization_without_knowledge_team(self, mock_directory_facilitator, mock_blackboard):
        """Test initialization without knowledge management team"""
        explorer = UniversalStrategyExplorer(
            directory_facilitator=mock_directory_facilitator,
            blackboard=mock_blackboard,
            knowledge_team=None
        )

        assert explorer.knowledge_team is None
        # Should still initialize successfully


# ===========================================================================
# STRATEGY EXPLORATION TESTS
# ===========================================================================

class TestStrategyExploration:
    """Test core strategy exploration functionality"""

    def test_explore_strategies_basic(self, universal_explorer, calculus_problem):
        """Test basic strategy exploration"""
        ranking = universal_explorer.explore_strategies(calculus_problem)

        assert ranking is not None
        assert ranking.problem_signature == hash_problem(calculus_problem)
        assert len(ranking.ranked_strategies) > 0
        assert ranking.exploration_budget >= 1

    def test_explore_strategies_with_historical_successes(
        self, universal_explorer, calculus_problem, mock_knowledge_team
    ):
        """Test exploration with historical successful strategies"""
        # Setup: Mock knowledge team returns successful strategies
        successful_strategy = Strategy(
            strategy_id='hist_001',
            name='Historical Success',
            domain=MathDomain.CALCULUS,
            techniques=['technique1'],
            preconditions={'operation': 'integrate'},
            estimated_cost='low',
            success_rate=0.95
        )

        past_exploration = ExplorationResult(
            exploration_id='past_001',
            strategy=successful_strategy,
            problem_signature='similar_sig',
            outcome=ExplorationOutcome.SUCCESS
        )

        mock_knowledge_team.query_similar_explorations.return_value = [past_exploration]

        ranking = universal_explorer.explore_strategies(calculus_problem)

        # Verify historical strategy is included and highly ranked
        strategy_ids = [s.strategy_id for s, _ in ranking.ranked_strategies]
        assert 'hist_001' in strategy_ids

    def test_explore_strategies_ranking_order(self, universal_explorer, calculus_problem):
        """Test that strategies are ranked by confidence (descending)"""
        ranking = universal_explorer.explore_strategies(calculus_problem)

        # Verify strategies are sorted by confidence
        confidences = [conf for _, conf in ranking.ranked_strategies]
        assert confidences == sorted(confidences, reverse=True)

    def test_explore_strategies_budget_computation(self, universal_explorer):
        """Test exploration budget computation"""
        # Simple problem should have smaller budget
        simple_problem = StructuredProblem(
            raw_input="2 + 2",
            omdoc_content=create_number(4),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={'operation': 'add'}
        )

        ranking = universal_explorer.explore_strategies(simple_problem)
        simple_budget = ranking.exploration_budget

        # Complex problem should have larger budget
        complex_problem = StructuredProblem(
            raw_input="This is a very complex problem " * 10,
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.CALCULUS,
            metadata={
                'operation': 'integrate',
                'has_composite_function': True,
                'has_nested_structure': True,
                'degree': 10
            }
        )

        ranking2 = universal_explorer.explore_strategies(complex_problem)
        complex_budget = ranking2.exploration_budget

        # Complex problems should generally have larger budgets
        assert complex_budget >= simple_budget


# ===========================================================================
# FEATURE EXTRACTION TESTS
# ===========================================================================

class TestFeatureExtraction:
    """Test problem feature extraction"""

    def test_extract_features_calculus(self, universal_explorer, calculus_problem):
        """Test feature extraction for calculus problems"""
        features = universal_explorer._extract_features(calculus_problem)

        assert features['domain'] == MathDomain.CALCULUS
        assert features['operation'] == 'integrate'
        assert 'has_composite_function' in features
        assert 'complexity' in features

    def test_extract_features_algebra(self, universal_explorer, algebra_problem):
        """Test feature extraction for algebra problems"""
        features = universal_explorer._extract_features(algebra_problem)

        assert features['domain'] == MathDomain.ALGEBRA
        assert features['operation'] == 'solve'
        assert features['equation_type'] == 'quadratic'
        assert features['degree'] == 2

    def test_extract_features_domain_specific(self, universal_explorer):
        """Test that domain-specific features are extracted correctly"""
        # Linear algebra problem
        linalg_problem = StructuredProblem(
            raw_input="Compute determinant of [[1,2],[3,4]]",
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.LINEAR_ALGEBRA,
            metadata={
                'operation': 'determinant',
                'matrix_size': 2
            }
        )

        features = universal_explorer._extract_features(linalg_problem)
        assert features['matrix_size'] == 2


# ===========================================================================
# DOMAIN EXPLORER INTEGRATION TESTS
# ===========================================================================

class TestDomainExplorerIntegration:
    """Test integration with domain-specific explorers"""

    def test_get_domain_explorer_caching(self, universal_explorer, mock_directory_facilitator):
        """Test that domain explorers are cached after first load"""
        # Setup: Mock DF returns a domain explorer
        mock_explorer = Mock()
        mock_registration = Mock()
        mock_registration.instance = mock_explorer
        mock_directory_facilitator.search.return_value = [mock_registration]

        # First call - should query DF
        explorer1 = universal_explorer._get_domain_explorer(MathDomain.CALCULUS)
        assert mock_directory_facilitator.search.call_count == 1

        # Second call - should use cache
        explorer2 = universal_explorer._get_domain_explorer(MathDomain.CALCULUS)
        assert mock_directory_facilitator.search.call_count == 1  # Not called again
        assert explorer1 is explorer2  # Same instance

    def test_get_domain_explorer_not_found(self, universal_explorer, mock_directory_facilitator):
        """Test handling when domain explorer is not found"""
        mock_directory_facilitator.search.return_value = []

        explorer = universal_explorer._get_domain_explorer(MathDomain.CALCULUS)
        assert explorer is None

    def test_get_domain_explorer_without_df(self):
        """Test domain explorer loading without directory facilitator"""
        explorer = UniversalStrategyExplorer(
            directory_facilitator=None,
            knowledge_team=None
        )

        result = explorer._get_domain_explorer(MathDomain.CALCULUS)
        assert result is None


# ===========================================================================
# UTILITY METHOD TESTS
# ===========================================================================

class TestUtilityMethods:
    """Test utility methods"""

    def test_deduplicate_strategies(self, universal_explorer):
        """Test strategy deduplication"""
        s1 = Strategy('id1', 'S1', MathDomain.ALGEBRA, ['t1'], {}, 'low', 0.8)
        s2 = Strategy('id2', 'S2', MathDomain.ALGEBRA, ['t2'], {}, 'medium', 0.7)
        s3 = Strategy('id1', 'S1_duplicate', MathDomain.ALGEBRA, ['t3'], {}, 'high', 0.6)

        strategies = [s1, s2, s3]
        unique = universal_explorer._deduplicate_strategies(strategies)

        assert len(unique) == 2
        assert unique[0].strategy_id == 'id1'
        assert unique[1].strategy_id == 'id2'

    def test_explain_ranking_with_historical_success(self, universal_explorer):
        """Test ranking explanation generation"""
        strategy = Strategy('s1', 'Test Strategy', MathDomain.ALGEBRA, ['t1'], {}, 'low', 0.9)
        past_exploration = ExplorationResult(
            exploration_id='exp1',
            strategy=strategy,
            problem_signature='sig1',
            outcome=ExplorationOutcome.SUCCESS
        )

        ranked = [(strategy, 0.95)]
        explanation = universal_explorer._explain_ranking(ranked, [past_exploration], 3)

        assert 'Historical success' in explanation
        assert '0.95' in explanation

    def test_estimate_solve_time(self, universal_explorer):
        """Test solve time estimation"""
        strategies = [
            (Strategy('s1', 'S1', MathDomain.ALGEBRA, ['t1'], {}, 'low', 0.8), 0.9),
            (Strategy('s2', 'S2', MathDomain.ALGEBRA, ['t2'], {}, 'high', 0.7), 0.8),
        ]

        time = universal_explorer._estimate_solve_time(strategies)
        assert time > 0
        assert time == 0.5 + 5.0  # low + high costs


# ===========================================================================
# STATISTICS TESTS
# ===========================================================================

class TestStatistics:
    """Test statistics tracking"""

    def test_statistics_initial_state(self, universal_explorer):
        """Test initial statistics state"""
        stats = universal_explorer.get_statistics()

        assert stats['explorations_performed'] == 0
        assert stats['successful_explorations'] == 0
        assert stats['failed_explorations'] == 0
        assert stats['domain'] == 'universal'

    def test_statistics_after_exploration(self, universal_explorer, calculus_problem):
        """Test statistics tracking after exploration"""
        initial_count = universal_explorer.explorations_performed

        universal_explorer.explore_strategies(calculus_problem)

        assert universal_explorer.explorations_performed == initial_count + 1


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_explore_strategies_with_no_strategies(self, universal_explorer):
        """Test exploration when no strategies match"""
        # Create a problem in an unknown domain
        weird_problem = StructuredProblem(
            raw_input="weird problem",
            omdoc_content=create_number(0),
            problem_type=ProblemType.UNKNOWN,
            domain=MathDomain.UNKNOWN,
            metadata={}
        )

        ranking = universal_explorer.explore_strategies(weird_problem)

        # Should handle gracefully, returning some strategies even if not perfect matches
        assert ranking is not None
        assert isinstance(ranking.ranked_strategies, list)

    def test_explore_strategies_with_exception_in_feature_extraction(
        self, universal_explorer, calculus_problem
    ):
        """Test handling of exceptions during feature extraction"""
        with patch.object(universal_explorer, '_extract_features', side_effect=Exception("Test error")):
            # Should raise the exception (not handle silently)
            with pytest.raises(Exception):
                universal_explorer.explore_strategies(calculus_problem)

    def test_suggest_strategies_returns_all(self, universal_explorer, calculus_problem):
        """Test that suggest_strategies returns all strategies for universal explorer"""
        strategies = universal_explorer.suggest_strategies(calculus_problem, {})

        # Universal explorer returns entire library
        assert len(strategies) == len(universal_explorer.strategy_library)


# ===========================================================================
# SECURITY TESTS
# ===========================================================================

class TestSecurity:
    """Test security-related concerns"""

    def test_no_code_execution_in_strategy_matching(self, universal_explorer):
        """Test that strategy matching doesn't execute code from metadata"""
        # Malicious metadata that might contain code
        malicious_problem = StructuredProblem(
            raw_input="x = 1",
            omdoc_content=create_number(1),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={
                'operation': '__import__("os").system("echo hacked")',
                'malicious': 'eval("print(\'pwned\')")'
            }
        )

        # Should not execute any code
        ranking = universal_explorer.explore_strategies(malicious_problem)

        # Execution should complete safely
        assert ranking is not None

    def test_large_problem_handling(self, universal_explorer):
        """Test handling of very large problem inputs"""
        large_input = "x" * 1000000  # 1MB input string

        large_problem = StructuredProblem(
            raw_input=large_input,
            omdoc_content=create_number(0),
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA,
            metadata={}
        )

        # Should handle without crashing or excessive memory use
        ranking = universal_explorer.explore_strategies(large_problem)
        assert ranking is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
