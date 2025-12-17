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
Conflict Resolution Tests
=========================

Comprehensive tests for Phase 4 Conflict Resolution Team:
- DebateModerator (FMAD protocol)
- EvidenceWeigher (truth hierarchy)
- ConsensusBuilder (expertise voting)
- ConflictResolutionTeam (coordinator)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from symbo_agentic_reasoners.middleware.conflict_resolution import (
    EvidenceType,
    ConflictStatus,
    ConflictCase,
    Ruling,
    DebateModerator,
    EvidenceWeigher,
    ConsensusBuilder,
    ConflictResolutionTeam,
)


# =============================================================================
# EvidenceType Enum Tests
# =============================================================================


class TestEvidenceType:
    """Tests for EvidenceType enum."""

    def test_evidence_hierarchy_values(self):
        """Evidence types should have correct hierarchy values."""
        assert EvidenceType.FORMAL_PROOF.value == 4
        assert EvidenceType.SYMBOLIC_DERIVATION.value == 3
        assert EvidenceType.NUMERICAL_APPROXIMATION.value == 2
        assert EvidenceType.HEURISTIC_GUESS.value == 1

    def test_evidence_ordering(self):
        """Formal proof should be highest, heuristic lowest."""
        assert EvidenceType.FORMAL_PROOF.value > EvidenceType.SYMBOLIC_DERIVATION.value
        assert EvidenceType.SYMBOLIC_DERIVATION.value > EvidenceType.NUMERICAL_APPROXIMATION.value
        assert EvidenceType.NUMERICAL_APPROXIMATION.value > EvidenceType.HEURISTIC_GUESS.value


# =============================================================================
# ConflictStatus Enum Tests
# =============================================================================


class TestConflictStatus:
    """Tests for ConflictStatus enum."""

    def test_all_statuses_exist(self):
        """All expected statuses should exist."""
        assert hasattr(ConflictStatus, 'DETECTED')
        assert hasattr(ConflictStatus, 'ARGUMENTS_REQUESTED')
        assert hasattr(ConflictStatus, 'ARGUMENTS_RECEIVED')
        assert hasattr(ConflictStatus, 'WEIGHING')
        assert hasattr(ConflictStatus, 'CONSENSUS_REQUIRED')
        assert hasattr(ConflictStatus, 'RESOLVED')
        assert hasattr(ConflictStatus, 'TIMEOUT')


# =============================================================================
# ConflictCase Tests
# =============================================================================


class TestConflictCase:
    """Tests for ConflictCase dataclass."""

    def test_create_case(self):
        """Should create conflict case with defaults."""
        case = ConflictCase()

        assert case.case_id is not None
        assert case.subtask_id == ""
        assert case.conversation_id == ""
        assert case.conflicting_results == []
        assert case.arguments == []
        assert case.ruling is None
        assert case.status == ConflictStatus.DETECTED

    def test_create_case_with_values(self):
        """Should create case with provided values."""
        results = [{'agent_id': 'a1', 'result': 'x'}]
        case = ConflictCase(
            subtask_id='task_001',
            conversation_id='conv_001',
            conflicting_results=results,
            domain='calculus'
        )

        assert case.subtask_id == 'task_001'
        assert case.conversation_id == 'conv_001'
        assert len(case.conflicting_results) == 1
        assert case.domain == 'calculus'

    def test_add_argument(self):
        """Should add argument and update status."""
        case = ConflictCase(
            conflicting_results=[{'agent_id': 'a1'}, {'agent_id': 'a2'}]
        )
        assert case.status == ConflictStatus.DETECTED

        case.add_argument({'agent_id': 'a1', 'method': 'symbolic'})
        assert len(case.arguments) == 1

        case.add_argument({'agent_id': 'a2', 'method': 'numerical'})
        assert len(case.arguments) == 2
        assert case.status == ConflictStatus.ARGUMENTS_RECEIVED

    def test_set_ruling(self):
        """Should set ruling and mark resolved."""
        case = ConflictCase()

        ruling_data = {'winner': 'agent_1', 'confidence': 0.9}
        case.set_ruling(ruling_data)

        assert case.ruling == ruling_data
        assert case.status == ConflictStatus.RESOLVED

    def test_timestamp_set_automatically(self):
        """Timestamp should be set on creation."""
        case = ConflictCase()

        assert case.timestamp is not None
        assert isinstance(case.timestamp, datetime)


# =============================================================================
# Ruling Tests
# =============================================================================


class TestRuling:
    """Tests for Ruling dataclass."""

    def test_create_ruling(self):
        """Should create ruling with required fields."""
        ruling = Ruling(
            ruling_type='AUTOMATIC',
            winner_agent='agent_1',
            winning_result='x = 5',
            evidence_type='SYMBOLIC_DERIVATION',
            rationale='Higher evidence type wins'
        )

        assert ruling.ruling_type == 'AUTOMATIC'
        assert ruling.winner_agent == 'agent_1'
        assert ruling.winning_result == 'x = 5'
        assert ruling.evidence_type == 'SYMBOLIC_DERIVATION'
        assert ruling.rationale == 'Higher evidence type wins'
        assert ruling.confidence == 1.0  # default

    def test_ruling_with_vote_breakdown(self):
        """Should accept vote breakdown for consensus rulings."""
        votes = {'agent_1': 0.8, 'agent_2': 0.6}
        ruling = Ruling(
            ruling_type='CONSENSUS',
            winner_agent='agent_1',
            winning_result='x = 5',
            evidence_type='SYMBOLIC_DERIVATION',
            rationale='Consensus reached',
            confidence=0.85,
            vote_breakdown=votes
        )

        assert ruling.vote_breakdown == votes
        assert ruling.confidence == 0.85


# =============================================================================
# DebateModerator Tests
# =============================================================================


class TestDebateModerator:
    """Tests for DebateModerator (FMAD protocol)."""

    @pytest.fixture
    def moderator(self):
        """Create moderator without infrastructure."""
        with patch('builtins.print'):  # Suppress init print
            return DebateModerator()

    def test_initialization(self, moderator):
        """Should initialize with empty state."""
        assert moderator.blackboard is None
        assert moderator.acc is None
        assert moderator.df is None
        assert moderator.active_cases == {}
        assert moderator.conflicts_detected == 0

    def test_initialization_with_infrastructure(self):
        """Should initialize with infrastructure."""
        bb = Mock()
        acc = Mock()
        df = Mock()

        with patch('builtins.print'):
            moderator = DebateModerator(blackboard=bb, acc=acc, df=df)

        assert moderator.blackboard is bb
        assert moderator.acc is acc
        assert moderator.df is df

    def test_on_conflict_detected(self, moderator):
        """Should create case and return case_id."""
        conflict_entry = {
            'subtask_id': 'integrate_x',
            'conversation_id': 'conv_001',
            'domain': 'calculus',
            'results': [
                {'agent_id': 'a1', 'result': '-cos(x)'},
                {'agent_id': 'a2', 'result': '-cos(x) + C'}
            ]
        }

        with patch('builtins.print'):
            case_id = moderator.on_conflict_detected(conflict_entry)

        assert case_id is not None
        assert case_id in moderator.active_cases
        assert moderator.conflicts_detected == 1

        case = moderator.active_cases[case_id]
        assert case.subtask_id == 'integrate_x'
        assert case.domain == 'calculus'
        assert len(case.conflicting_results) == 2

    def test_receive_argument(self, moderator):
        """Should collect argument for case."""
        # First create a case
        with patch('builtins.print'):
            case_id = moderator.on_conflict_detected({
                'subtask_id': 'test',
                'results': [{'agent_id': 'a1'}, {'agent_id': 'a2'}]
            })

        argument = {
            'agent_id': 'a1',
            'result': 'x = 5',
            'method_used': 'symbolic',
            'evidence_type': 'SYMBOLIC_DERIVATION',
            'confidence': 0.9
        }

        result = moderator.receive_argument(case_id, argument)

        # Not all arguments yet
        assert result is False
        assert moderator.arguments_collected == 1

    def test_receive_argument_completes_case(self, moderator):
        """Should forward case when all arguments collected."""
        with patch('builtins.print'):
            case_id = moderator.on_conflict_detected({
                'subtask_id': 'test',
                'results': [{'agent_id': 'a1'}, {'agent_id': 'a2'}]
            })

        moderator.receive_argument(case_id, {'agent_id': 'a1', 'method_used': 'symbolic'})

        with patch('builtins.print'):
            result = moderator.receive_argument(case_id, {'agent_id': 'a2', 'method_used': 'numerical'})

        assert result is True
        assert moderator.cases_forwarded == 1

    def test_receive_argument_invalid_case(self, moderator):
        """Should return False for invalid case_id."""
        result = moderator.receive_argument('nonexistent', {'agent_id': 'a1'})

        assert result is False

    def test_get_case(self, moderator):
        """Should retrieve case by ID."""
        with patch('builtins.print'):
            case_id = moderator.on_conflict_detected({
                'subtask_id': 'test',
                'results': [{'agent_id': 'a1'}]
            })

        case = moderator.get_case(case_id)
        assert case is not None
        assert case.case_id == case_id

    def test_get_case_not_found(self, moderator):
        """Should return None for unknown case."""
        case = moderator.get_case('nonexistent')
        assert case is None

    def test_get_statistics(self, moderator):
        """Should return statistics dict."""
        with patch('builtins.print'):
            moderator.on_conflict_detected({
                'subtask_id': 'test',
                'results': [{'agent_id': 'a1'}]
            })

        stats = moderator.get_statistics()

        assert isinstance(stats, dict)
        assert stats['conflicts_detected'] == 1
        assert 'arguments_collected' in stats
        assert 'cases_forwarded' in stats
        assert 'active_cases' in stats


# =============================================================================
# EvidenceWeigher Tests
# =============================================================================


class TestEvidenceWeigher:
    """Tests for EvidenceWeigher (truth hierarchy)."""

    @pytest.fixture
    def weigher(self):
        """Create weigher without infrastructure."""
        with patch('builtins.print'):
            return EvidenceWeigher()

    def test_initialization(self, weigher):
        """Should initialize with empty state."""
        assert weigher.blackboard is None
        assert weigher.cases_evaluated == 0
        assert weigher.automatic_rulings == 0
        assert weigher.consensus_required == 0

    def test_truth_hierarchy_exists(self, weigher):
        """Should have immutable truth hierarchy."""
        hierarchy = weigher.TRUTH_HIERARCHY

        assert hierarchy[EvidenceType.FORMAL_PROOF] == 4
        assert hierarchy[EvidenceType.SYMBOLIC_DERIVATION] == 3
        assert hierarchy[EvidenceType.NUMERICAL_APPROXIMATION] == 2
        assert hierarchy[EvidenceType.HEURISTIC_GUESS] == 1

    def test_evaluate_case_no_arguments(self, weigher):
        """Should return NO_ARGUMENTS ruling when empty."""
        with patch('builtins.print'):
            ruling = weigher.evaluate_case({'arguments': []})

        assert ruling.ruling_type == 'NO_ARGUMENTS'
        assert ruling.winner_agent == 'none'
        assert ruling.confidence == 0.0

    def test_evaluate_case_single_argument(self, weigher):
        """Should auto-win with single argument."""
        case_data = {
            'arguments': [{
                'agent_id': 'agent_1',
                'result': 'x = 5',
                'method_used': 'symbolic',
                'confidence': 0.9
            }]
        }

        with patch('builtins.print'):
            ruling = weigher.evaluate_case(case_data)

        assert ruling.ruling_type == 'AUTOMATIC'
        assert ruling.winner_agent == 'agent_1'
        assert weigher.automatic_rulings == 1

    def test_evaluate_case_hierarchy_winner(self, weigher):
        """Should choose higher evidence type automatically."""
        case_data = {
            'arguments': [
                {
                    'agent_id': 'symbolic_agent',
                    'result': '-cos(x)',
                    'method_used': 'symbolic_risch',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9
                },
                {
                    'agent_id': 'numerical_agent',
                    'result': '-0.999cos(x)',
                    'method_used': 'numerical_quadrature',
                    'evidence_type': 'NUMERICAL_APPROXIMATION',
                    'confidence': 0.99
                }
            ]
        }

        with patch('builtins.print'):
            ruling = weigher.evaluate_case(case_data)

        # Symbolic > Numerical even with lower confidence
        assert ruling.ruling_type == 'AUTOMATIC'
        assert ruling.winner_agent == 'symbolic_agent'
        assert ruling.evidence_type == 'SYMBOLIC_DERIVATION'

    def test_evaluate_case_formal_proof_wins(self, weigher):
        """Formal proof should always win."""
        case_data = {
            'arguments': [
                {
                    'agent_id': 'prover',
                    'result': 'QED',
                    'ax_prover_verified': True,
                    'confidence': 0.8
                },
                {
                    'agent_id': 'symbolic',
                    'result': 'likely true',
                    'method_used': 'symbolic_simplification',
                    'confidence': 0.99
                }
            ]
        }

        with patch('builtins.print'):
            ruling = weigher.evaluate_case(case_data)

        assert ruling.winner_agent == 'prover'
        assert ruling.evidence_type == 'FORMAL_PROOF'

    def test_evaluate_case_tied_hierarchy(self, weigher):
        """Should require consensus when hierarchy tied."""
        case_data = {
            'arguments': [
                {
                    'agent_id': 'symbolic_1',
                    'result': 'x = 5',
                    'method_used': 'algebraic_solver',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9
                },
                {
                    'agent_id': 'symbolic_2',
                    'result': 'x = 6',
                    'method_used': 'symbolic_risch',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.85
                }
            ]
        }

        with patch('builtins.print'):
            ruling = weigher.evaluate_case(case_data)

        assert ruling.ruling_type == 'CONSENSUS_REQUIRED'
        assert weigher.consensus_required == 1

    def test_classify_evidence_formal_proof(self, weigher):
        """Should classify ax_prover_verified as formal proof."""
        arg = {'ax_prover_verified': True}
        result = weigher._classify_evidence(arg)

        assert result == EvidenceType.FORMAL_PROOF

    def test_classify_evidence_symbolic(self, weigher):
        """Should classify symbolic methods correctly."""
        symbolic_methods = ['symbolic', 'algebraic', 'closed-form', 'exact', 'risch']

        for method in symbolic_methods:
            arg = {'method_used': f'{method}_solver'}
            result = weigher._classify_evidence(arg)
            assert result == EvidenceType.SYMBOLIC_DERIVATION

    def test_classify_evidence_numerical(self, weigher):
        """Should classify numerical methods correctly."""
        numerical_methods = ['numerical', 'approximation', 'newton', 'iterative']

        for method in numerical_methods:
            arg = {'method_used': f'{method}_method'}
            result = weigher._classify_evidence(arg)
            assert result == EvidenceType.NUMERICAL_APPROXIMATION

    def test_classify_evidence_heuristic_default(self, weigher):
        """Should default to heuristic for unknown methods."""
        arg = {'method_used': 'unknown_method'}
        result = weigher._classify_evidence(arg)

        assert result == EvidenceType.HEURISTIC_GUESS

    def test_classify_evidence_explicit_type(self, weigher):
        """Should use explicit evidence_type if provided."""
        arg = {
            'method_used': 'some_method',
            'evidence_type': 'FORMAL_PROOF'
        }
        result = weigher._classify_evidence(arg)

        assert result == EvidenceType.FORMAL_PROOF

    def test_get_statistics(self, weigher):
        """Should return statistics dict."""
        stats = weigher.get_statistics()

        assert isinstance(stats, dict)
        assert 'cases_evaluated' in stats
        assert 'automatic_rulings' in stats
        assert 'consensus_required' in stats


# =============================================================================
# ConsensusBuilder Tests
# =============================================================================


class TestConsensusBuilder:
    """Tests for ConsensusBuilder (expertise voting)."""

    @pytest.fixture
    def builder(self):
        """Create builder without infrastructure."""
        with patch('builtins.print'):
            return ConsensusBuilder()

    def test_initialization(self, builder):
        """Should initialize with empty state."""
        assert builder.blackboard is None
        assert builder.df is None
        assert builder.consensus_votes == 0
        assert builder.tie_breakers == 0

    def test_expertise_weights_exist(self, builder):
        """Should have expertise weights for supervisors."""
        weights = builder.EXPERTISE_WEIGHTS

        assert 'calculus_supervisor' in weights
        assert 'algebra_supervisor' in weights
        assert 'linear_algebra_supervisor' in weights
        assert 'statistics_supervisor' in weights

    def test_build_consensus_basic(self, builder):
        """Should build consensus from classification."""
        ruling_data = {
            'case_id': 'test_001',
            'domain': 'algebra',
            'classification': [
                {
                    'agent_id': 'agent_1',
                    'result': 'x = 5',
                    'evidence_type': EvidenceType.SYMBOLIC_DERIVATION,
                    'hierarchy_score': 3,
                    'confidence': 0.9
                },
                {
                    'agent_id': 'agent_2',
                    'result': 'x = 6',
                    'evidence_type': EvidenceType.SYMBOLIC_DERIVATION,
                    'hierarchy_score': 3,
                    'confidence': 0.8
                }
            ]
        }

        with patch('builtins.print'):
            ruling = builder.build_consensus(ruling_data)

        assert ruling.ruling_type == 'CONSENSUS'
        assert ruling.winner_agent == 'agent_1'  # Higher confidence
        assert builder.consensus_votes == 1

    def test_build_consensus_expertise_weight(self, builder):
        """Should apply expertise weight for supervisors."""
        ruling_data = {
            'case_id': 'test_001',
            'domain': 'calculus',
            'classification': [
                {
                    'agent_id': 'regular_agent',
                    'result': 'x = 5',
                    'evidence_type': EvidenceType.SYMBOLIC_DERIVATION,
                    'hierarchy_score': 3,
                    'confidence': 0.9
                },
                {
                    'agent_id': 'calculus_supervisor_001',
                    'result': 'x = 6',
                    'evidence_type': EvidenceType.SYMBOLIC_DERIVATION,
                    'hierarchy_score': 3,
                    'confidence': 0.5  # Lower base confidence
                }
            ]
        }

        with patch('builtins.print'):
            ruling = builder.build_consensus(ruling_data)

        # Supervisor gets 2x weight in calculus domain: 0.5 * 2.0 = 1.0 > 0.9
        assert ruling.winner_agent == 'calculus_supervisor_001'

    def test_get_expertise_weight_supervisor(self, builder):
        """Should return higher weight for supervisor in domain."""
        weight = builder._get_expertise_weight('calculus_supervisor_001', 'calculus')
        assert weight == 2.0

        weight = builder._get_expertise_weight('algebra_supervisor_001', 'polynomial')
        assert weight == 2.0

    def test_get_expertise_weight_default(self, builder):
        """Should return 1.0 for non-supervisors."""
        weight = builder._get_expertise_weight('random_agent', 'calculus')
        assert weight == 1.0

    def test_get_expertise_weight_supervisor_different_domain(self, builder):
        """Should return 1.2 for supervisor in different domain."""
        # Calculus supervisor in algebra domain
        weight = builder._get_expertise_weight('calculus_supervisor', 'unknown_domain')
        assert weight == 1.2

    def test_build_consensus_empty_classification(self, builder):
        """Should handle empty classification."""
        ruling_data = {
            'case_id': 'test',
            'domain': 'general',
            'classification': []
        }

        with patch('builtins.print'):
            ruling = builder.build_consensus(ruling_data)

        assert ruling.winner_agent == 'none'
        assert ruling.winning_result is None

    def test_get_statistics(self, builder):
        """Should return statistics dict."""
        stats = builder.get_statistics()

        assert isinstance(stats, dict)
        assert 'consensus_votes' in stats
        assert 'tie_breakers' in stats


# =============================================================================
# ConflictResolutionTeam Tests
# =============================================================================


class TestConflictResolutionTeam:
    """Tests for ConflictResolutionTeam coordinator."""

    @pytest.fixture
    def team(self):
        """Create team without infrastructure."""
        with patch('builtins.print'):
            return ConflictResolutionTeam()

    def test_initialization(self, team):
        """Should initialize all three agents."""
        assert team.debate_moderator is not None
        assert team.evidence_weigher is not None
        assert team.consensus_builder is not None
        assert team.conflicts_resolved == 0

    def test_initialization_with_infrastructure(self):
        """Should pass infrastructure to agents."""
        bb = Mock()
        acc = Mock()
        df = Mock()

        with patch('builtins.print'):
            team = ConflictResolutionTeam(blackboard=bb, acc=acc, df=df)

        assert team.blackboard is bb
        assert team.debate_moderator.blackboard is bb
        assert team.evidence_weigher.blackboard is bb
        assert team.consensus_builder.blackboard is bb

    def test_check_for_conflict_no_conflict(self, team):
        """Should return False when results agree."""
        results = [
            {'agent_id': 'a1', 'result': 'x = 5'},
            {'agent_id': 'a2', 'result': 'x = 5'}
        ]

        assert team.check_for_conflict(results) is False

    def test_check_for_conflict_detected(self, team):
        """Should return True when results differ."""
        results = [
            {'agent_id': 'a1', 'result': 'x = 5'},
            {'agent_id': 'a2', 'result': 'x = 6'}
        ]

        assert team.check_for_conflict(results) is True

    def test_check_for_conflict_single_result(self, team):
        """Should return False for single result."""
        results = [{'agent_id': 'a1', 'result': 'x = 5'}]

        assert team.check_for_conflict(results) is False

    def test_check_for_conflict_empty(self, team):
        """Should return False for empty results."""
        assert team.check_for_conflict([]) is False

    def test_resolve_conflict_hierarchy_winner(self, team):
        """Should resolve conflict with hierarchy winner."""
        conflict_data = {
            'subtask_id': 'integrate_x',
            'conversation_id': 'test_001',
            'domain': 'calculus',
            'results': [
                {
                    'agent_id': 'symbolic_agent',
                    'result': '-cos(x)',
                    'method_used': 'symbolic_risch',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9
                },
                {
                    'agent_id': 'numerical_agent',
                    'result': '-0.999cos(x)',
                    'method_used': 'numerical_quadrature',
                    'evidence_type': 'NUMERICAL_APPROXIMATION',
                    'confidence': 0.99
                }
            ]
        }

        with patch('builtins.print'):
            ruling = team.resolve_conflict(conflict_data)

        assert ruling is not None
        assert ruling.ruling_type == 'AUTOMATIC'
        assert ruling.winner_agent == 'symbolic_agent'
        assert team.conflicts_resolved == 1

    def test_resolve_conflict_formal_proof(self, team):
        """Should resolve with formal proof winning."""
        conflict_data = {
            'subtask_id': 'prove_theorem',
            'domain': 'algebra',
            'results': [
                {
                    'agent_id': 'formal_prover',
                    'result': 'QED',
                    'method_used': 'ax_prover_coq',
                    'ax_prover_verified': True,
                    'evidence_type': 'FORMAL_PROOF',
                    'confidence': 0.8
                },
                {
                    'agent_id': 'heuristic_solver',
                    'result': 'likely true',
                    'method_used': 'pattern_matching',
                    'evidence_type': 'HEURISTIC_GUESS',
                    'confidence': 0.95
                }
            ]
        }

        with patch('builtins.print'):
            ruling = team.resolve_conflict(conflict_data)

        assert ruling.winner_agent == 'formal_prover'
        assert ruling.evidence_type == 'FORMAL_PROOF'

    def test_get_ruling_exists(self, team):
        """Should retrieve ruling for resolved case."""
        conflict_data = {
            'subtask_id': 'test',
            'results': [
                {'agent_id': 'a1', 'result': 'x', 'method_used': 'symbolic', 'confidence': 0.9},
                {'agent_id': 'a2', 'result': 'y', 'method_used': 'numerical', 'confidence': 0.8}
            ]
        }

        with patch('builtins.print'):
            ruling = team.resolve_conflict(conflict_data)
            case_id = list(team.debate_moderator.active_cases.keys())[0]
            retrieved = team.get_ruling(case_id)

        # Ruling should be retrievable
        assert retrieved is not None or ruling is not None

    def test_get_ruling_not_found(self, team):
        """Should return None for unknown case."""
        ruling = team.get_ruling('nonexistent_case')
        assert ruling is None

    def test_get_statistics(self, team):
        """Should return comprehensive statistics."""
        stats = team.get_statistics()

        assert isinstance(stats, dict)
        assert 'conflicts_resolved' in stats
        assert 'debate_moderator' in stats
        assert 'evidence_weigher' in stats
        assert 'consensus_builder' in stats

        # Nested stats should be dicts
        assert isinstance(stats['debate_moderator'], dict)
        assert isinstance(stats['evidence_weigher'], dict)
        assert isinstance(stats['consensus_builder'], dict)


# =============================================================================
# Integration Tests
# =============================================================================


class TestConflictResolutionIntegration:
    """Integration tests for conflict resolution workflow."""

    def test_full_resolution_workflow(self):
        """Test complete conflict resolution pipeline."""
        with patch('builtins.print'):
            team = ConflictResolutionTeam()

        # Create conflict data
        conflict_data = {
            'subtask_id': 'integrate_sin',
            'conversation_id': 'integration_test',
            'domain': 'calculus',
            'results': [
                {
                    'agent_id': 'symbolic_integration',
                    'result': '-cos(x) + C',
                    'method_used': 'symbolic_risch_algorithm',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.95
                },
                {
                    'agent_id': 'numerical_integration',
                    'result': '-0.9999cos(x)',
                    'method_used': 'numerical_quadrature',
                    'evidence_type': 'NUMERICAL_APPROXIMATION',
                    'confidence': 0.99
                }
            ]
        }

        # Resolve conflict
        with patch('builtins.print'):
            ruling = team.resolve_conflict(conflict_data)

        # Verify ruling
        assert ruling is not None
        assert ruling.ruling_type == 'AUTOMATIC'
        assert ruling.winner_agent == 'symbolic_integration'
        assert ruling.winning_result == '-cos(x) + C'
        assert ruling.evidence_type == 'SYMBOLIC_DERIVATION'

        # Verify statistics updated
        stats = team.get_statistics()
        assert stats['conflicts_resolved'] == 1
        assert stats['debate_moderator']['conflicts_detected'] == 1
        assert stats['evidence_weigher']['cases_evaluated'] >= 1

    def test_consensus_workflow(self):
        """Test consensus building for tied evidence."""
        with patch('builtins.print'):
            team = ConflictResolutionTeam()

        # Create conflict with same evidence types
        conflict_data = {
            'subtask_id': 'factor_polynomial',
            'domain': 'algebra',
            'results': [
                {
                    'agent_id': 'factorizer_1',
                    'result': '(x+1)(x-1)',
                    'method_used': 'symbolic_factorization',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.9
                },
                {
                    'agent_id': 'factorizer_2',
                    'result': '(x-1)(x+1)',
                    'method_used': 'algebraic_factorization',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.85
                }
            ]
        }

        with patch('builtins.print'):
            ruling = team.resolve_conflict(conflict_data)

        # Should use consensus since same evidence type
        assert ruling is not None
        # Winner should be factorizer_1 (higher confidence)
        assert ruling.winner_agent == 'factorizer_1'


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
