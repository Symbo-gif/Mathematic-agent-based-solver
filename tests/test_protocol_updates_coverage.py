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
Tests for Protocol Updates Module
==================================

Comprehensive tests for the Phase 4 integration components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestConflictDetector:
    """Tests for ConflictDetector class."""

    def test_init_default_tolerance(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        assert detector.tolerance == 1e-6
        assert detector.conflicts_detected == 0

    def test_init_custom_tolerance(self):
        """Test custom tolerance initialization."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector(tolerance=0.01)
        assert detector.tolerance == 0.01

    def test_check_results_empty_list(self):
        """Test check_results with empty list."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        assert detector.check_results([]) is False

    def test_check_results_single_result(self):
        """Test check_results with single result."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [{'agent_id': 'a1', 'result': 'x^2'}]
        assert detector.check_results(results) is False

    def test_check_results_same_values_no_conflict(self):
        """Test check_results with same values (no conflict)."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'agent_id': 'a1', 'result': 'x^2'},
            {'agent_id': 'a2', 'result': 'x^2'}
        ]
        assert detector.check_results(results) is False

    def test_check_results_different_values_conflict(self):
        """Test check_results with different values (conflict)."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'agent_id': 'a1', 'result': 'x^2'},
            {'agent_id': 'a2', 'result': 'x^3'}
        ]
        assert detector.check_results(results) is True
        assert detector.conflicts_detected == 1

    def test_check_results_numerical_within_tolerance(self):
        """Test numerical values within tolerance (no conflict)."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector(tolerance=1e-6)
        results = [
            {'agent_id': 'a1', 'result': 3.14159265},
            {'agent_id': 'a2', 'result': 3.14159266}
        ]
        assert detector.check_results(results) is False

    def test_check_results_numerical_outside_tolerance(self):
        """Test numerical values outside tolerance (conflict)."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector(tolerance=1e-6)
        results = [
            {'agent_id': 'a1', 'result': 3.14},
            {'agent_id': 'a2', 'result': 3.15}
        ]
        assert detector.check_results(results) is True

    def test_check_results_none_values(self):
        """Test check_results with None values."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'agent_id': 'a1', 'result': None},
            {'agent_id': 'a2', 'result': None}
        ]
        assert detector.check_results(results) is False

    def test_check_results_one_none_one_value(self):
        """Test check_results with one None and one value."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'agent_id': 'a1', 'result': None},
            {'agent_id': 'a2', 'result': 'x^2'}
        ]
        # Only one non-None value, so no conflict comparison possible
        assert detector.check_results(results) is False

    def test_check_results_multiple_agents(self):
        """Test check_results with multiple agents."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'agent_id': 'a1', 'result': 42},
            {'agent_id': 'a2', 'result': 42},
            {'agent_id': 'a3', 'result': 43}  # Different
        ]
        assert detector.check_results(results) is True

    def test_values_conflict_same_string(self):
        """Test _values_conflict with same strings."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        assert detector._values_conflict("hello", "hello") is False

    def test_values_conflict_string_case_insensitive(self):
        """Test _values_conflict with different case strings."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        # Strings are compared case-insensitively
        assert detector._values_conflict("HELLO", "hello") is False

    def test_values_conflict_string_with_whitespace(self):
        """Test _values_conflict with strings that differ in whitespace."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        assert detector._values_conflict("  hello  ", "hello") is False

    def test_values_conflict_different_strings(self):
        """Test _values_conflict with different strings."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        assert detector._values_conflict("hello", "world") is True

    def test_values_conflict_different_types(self):
        """Test _values_conflict with different types."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        assert detector._values_conflict([1, 2], {'a': 1}) is True

    def test_analyze_conflict(self):
        """Test analyze_conflict method."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'agent_id': 'a1', 'result': 'x^2'},
            {'agent_id': 'a2', 'result': 'x^3'}
        ]
        analysis = detector.analyze_conflict(results)

        assert analysis['conflict_detected'] is True
        assert analysis['num_results'] == 2
        assert analysis['results'] == results
        assert analysis['requires_resolution'] is True
        assert 'conflict_type' in analysis

    def test_classify_conflict_type_mismatch(self):
        """Test _classify_conflict with type mismatch."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'result': 42},
            {'result': 'forty-two'}
        ]
        assert detector._classify_conflict(results) == 'TYPE_MISMATCH'

    def test_classify_conflict_numerical_disagreement(self):
        """Test _classify_conflict with numerical values."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'result': 3.14},
            {'result': 3.15}
        ]
        assert detector._classify_conflict(results) == 'NUMERICAL_DISAGREEMENT'

    def test_classify_conflict_value_disagreement(self):
        """Test _classify_conflict with non-numerical same-type values."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        detector = ConflictDetector()
        results = [
            {'result': 'x^2'},
            {'result': 'x^3'}
        ]
        assert detector._classify_conflict(results) == 'VALUE_DISAGREEMENT'


class TestOrchestratorPhase4Update:
    """Tests for OrchestratorPhase4Update class."""

    def test_init_default(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        assert update.orchestrator is mock_orchestrator
        assert update.conflict_resolution_team is None
        assert update.failure_analysis_team is None
        assert update.meta_learning_team is None
        assert update.appellate_active is True
        assert update.appellate_invocations == 0
        assert update.conflicts_resolved == 0
        assert update.failures_recovered == 0
        assert update.routing_updates == 0

    def test_init_with_all_teams(self):
        """Test initialization with all teams."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_conflict_team = Mock()
        mock_failure_team = Mock()
        mock_meta_team = Mock()

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            conflict_resolution_team=mock_conflict_team,
            failure_analysis_team=mock_failure_team,
            meta_learning_team=mock_meta_team
        )

        assert update.conflict_resolution_team is mock_conflict_team
        assert update.failure_analysis_team is mock_failure_team
        assert update.meta_learning_team is mock_meta_team

    def test_invoke_agent(self):
        """Test _invoke_agent returns placeholder result."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        result = update._invoke_agent('agent1', 'problem')

        assert 'result' in result
        assert 'method' in result
        assert 'confidence' in result

    def test_select_best_result_empty(self):
        """Test _select_best_result with empty results."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        result = update._select_best_result([])

        assert result['result'] is None
        assert result['status'] == 'NO_RESULTS'

    def test_select_best_result_single(self):
        """Test _select_best_result with single result."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        results = [{'agent_id': 'a1', 'result': 42, 'confidence': 0.9, 'method': 'calc'}]
        result = update._select_best_result(results)

        assert result['result'] == 42
        assert result['status'] == 'SUCCESS'
        assert result['agent_id'] == 'a1'
        assert result['confidence'] == 0.9

    def test_select_best_result_multiple_by_confidence(self):
        """Test _select_best_result selects highest confidence."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        results = [
            {'agent_id': 'a1', 'result': 42, 'confidence': 0.5},
            {'agent_id': 'a2', 'result': 43, 'confidence': 0.9},
            {'agent_id': 'a3', 'result': 44, 'confidence': 0.7}
        ]
        result = update._select_best_result(results)

        assert result['result'] == 43
        assert result['agent_id'] == 'a2'

    def test_resolve_conflict_no_team(self):
        """Test _resolve_conflict without conflict resolution team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        results = [{'result': 42}, {'result': 43}]
        result = update._resolve_conflict('problem', results)

        assert result['status'] == 'CONFLICT_UNRESOLVED'
        assert update.appellate_invocations == 1

    def test_resolve_conflict_with_team(self):
        """Test _resolve_conflict with conflict resolution team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_conflict_team = Mock()
        mock_ruling = Mock()
        mock_ruling.winner_result = 42
        mock_conflict_team.resolve_conflict.return_value = mock_ruling

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            conflict_resolution_team=mock_conflict_team
        )

        results = [{'result': 42}, {'result': 43}]
        result = update._resolve_conflict('problem', results)

        assert result['status'] == 'CONFLICT_RESOLVED'
        assert result['result'] == 42
        assert update.conflicts_resolved == 1

    def test_resolve_conflict_team_raises_exception(self):
        """Test _resolve_conflict when team raises exception."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_conflict_team = Mock()
        mock_conflict_team.resolve_conflict.side_effect = Exception("Team error")

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            conflict_resolution_team=mock_conflict_team
        )

        results = [{'result': 42}, {'result': 43}]
        result = update._resolve_conflict('problem', results)

        assert result['status'] == 'RESOLUTION_FAILED'

    def test_handle_agent_failure_no_team(self):
        """Test _handle_agent_failure without failure analysis team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        # Should not raise
        update._handle_agent_failure('agent1', 'problem', 'error message')
        assert update.failures_recovered == 0

    def test_handle_agent_failure_with_team(self):
        """Test _handle_agent_failure with failure analysis team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_failure_team = Mock()
        mock_failure_team.handle_failure.return_value = {'recovery_plan': ['step1', 'step2']}

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            failure_analysis_team=mock_failure_team
        )

        update._handle_agent_failure('agent1', 'problem', 'error message')

        assert update.failures_recovered == 1
        mock_failure_team.handle_failure.assert_called_once()

    def test_handle_agent_failure_team_raises_exception(self):
        """Test _handle_agent_failure when team raises exception."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_failure_team = Mock()
        mock_failure_team.handle_failure.side_effect = Exception("Analysis error")

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            failure_analysis_team=mock_failure_team
        )

        # Should not raise
        update._handle_agent_failure('agent1', 'problem', 'error message')
        assert update.failures_recovered == 0

    def test_update_routing_from_meta_learning_no_team(self):
        """Test update_routing_from_meta_learning without meta-learning team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        # Should not raise
        update.update_routing_from_meta_learning()
        assert update.routing_updates == 0

    def test_update_routing_from_meta_learning_with_team(self):
        """Test update_routing_from_meta_learning with meta-learning team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_meta_team = Mock()
        mock_meta_team.run_batch_optimization.return_value = {
            'tables_updated': 5,
            'insights_generated': 3
        }

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            meta_learning_team=mock_meta_team
        )

        update.update_routing_from_meta_learning()

        assert update.routing_updates == 1
        mock_meta_team.run_batch_optimization.assert_called_once()

    def test_update_routing_team_raises_exception(self):
        """Test update_routing_from_meta_learning when team raises exception."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_meta_team = Mock()
        mock_meta_team.run_batch_optimization.side_effect = Exception("Optimization error")

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            meta_learning_team=mock_meta_team
        )

        # Should not raise
        update.update_routing_from_meta_learning()
        assert update.routing_updates == 0

    def test_get_team_recommendation_no_team(self):
        """Test get_team_recommendation without meta-learning team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        result = update.get_team_recommendation({'domain': 'algebra'})

        assert result['team_size'] == 6
        assert result['complexity_level'] == 'STANDARD'

    def test_get_team_recommendation_with_team(self):
        """Test get_team_recommendation with meta-learning team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_meta_team = Mock()
        mock_meta_team.get_team_recommendation.return_value = {
            'team_size': 8,
            'complexity_level': 'HIGH'
        }

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            meta_learning_team=mock_meta_team
        )

        result = update.get_team_recommendation({'domain': 'calculus'})

        assert result['team_size'] == 8
        assert result['complexity_level'] == 'HIGH'

    def test_get_team_recommendation_team_raises_exception(self):
        """Test get_team_recommendation when team raises exception."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_meta_team = Mock()
        mock_meta_team.get_team_recommendation.side_effect = Exception("Recommendation error")

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            meta_learning_team=mock_meta_team
        )

        result = update.get_team_recommendation({'domain': 'algebra'})

        # Should return default
        assert result['team_size'] == 6
        assert result['complexity_level'] == 'STANDARD'

    def test_accept_result(self):
        """Test accept_result method."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        result = update.accept_result({'value': 42})

        assert result == {'value': 42}

    def test_get_statistics(self):
        """Test get_statistics method."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        stats = update.get_statistics()

        assert 'appellate_invocations' in stats
        assert 'conflicts_resolved' in stats
        assert 'failures_recovered' in stats
        assert 'routing_updates' in stats
        assert 'conflicts_detected' in stats


class TestProcessWithConflictDetection:
    """Tests for process_with_conflict_detection method."""

    def test_process_no_agents(self):
        """Test processing with no agents."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        result = update.process_with_conflict_detection('problem', [])

        assert result['status'] == 'NO_RESULTS'

    def test_process_single_agent_success(self):
        """Test processing with single agent that succeeds."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        # Mock _invoke_agent to return a result
        update._invoke_agent = Mock(return_value={'result': 42, 'method': 'calc', 'confidence': 0.9})

        result = update.process_with_conflict_detection('problem', ['agent1'])

        assert result['status'] == 'SUCCESS'
        assert result['result'] == 42

    def test_process_agent_fails_no_failure_team(self):
        """Test processing when agent fails without failure team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        # Mock _invoke_agent to raise an exception
        update._invoke_agent = Mock(side_effect=Exception("Agent failed"))

        result = update.process_with_conflict_detection('problem', ['agent1'])

        assert result['status'] == 'NO_RESULTS'

    def test_process_agent_fails_with_failure_team(self):
        """Test processing when agent fails with failure team."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        mock_failure_team = Mock()
        mock_failure_team.handle_failure.return_value = {'recovery_plan': ['step1']}

        update = OrchestratorPhase4Update(
            orchestrator=mock_orchestrator,
            failure_analysis_team=mock_failure_team
        )

        # Mock _invoke_agent to raise an exception
        update._invoke_agent = Mock(side_effect=Exception("Agent failed"))

        result = update.process_with_conflict_detection('problem', ['agent1'])

        # Failure should be handled
        mock_failure_team.handle_failure.assert_called_once()

    def test_process_multiple_agents_no_conflict(self):
        """Test processing multiple agents without conflict."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        # Mock _invoke_agent to return same results
        def invoke_side_effect(agent_id, problem):
            return {'result': 42, 'method': 'calc', 'confidence': 0.8}

        update._invoke_agent = Mock(side_effect=invoke_side_effect)

        result = update.process_with_conflict_detection('problem', ['agent1', 'agent2'])

        assert result['status'] == 'SUCCESS'
        assert result['result'] == 42

    def test_process_multiple_agents_with_conflict(self):
        """Test processing multiple agents with conflict."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        mock_orchestrator = Mock()
        update = OrchestratorPhase4Update(orchestrator=mock_orchestrator)

        # Mock _invoke_agent to return different results
        call_count = [0]
        def invoke_side_effect(agent_id, problem):
            call_count[0] += 1
            return {'result': 40 + call_count[0], 'method': 'calc', 'confidence': 0.8}

        update._invoke_agent = Mock(side_effect=invoke_side_effect)

        result = update.process_with_conflict_detection('problem', ['agent1', 'agent2'])

        # Conflict should be detected and handled (but no resolution team)
        assert result['status'] == 'CONFLICT_UNRESOLVED'


class TestModuleFunctions:
    """Tests for module-level functions and imports."""

    def test_module_imports(self):
        """Test that module imports correctly."""
        from symbo_agentic_reasoners.integration import protocol_updates
        assert protocol_updates is not None

    def test_conflict_detector_export(self):
        """Test ConflictDetector is accessible."""
        from symbo_agentic_reasoners.integration.protocol_updates import ConflictDetector
        assert ConflictDetector is not None

    def test_orchestrator_phase4_update_export(self):
        """Test OrchestratorPhase4Update is accessible."""
        from symbo_agentic_reasoners.integration.protocol_updates import OrchestratorPhase4Update
        assert OrchestratorPhase4Update is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
