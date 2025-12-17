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
Tests for Evolutionary Flywheel Module
=======================================

Comprehensive tests for the active learning loop system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestEvolutionPhase:
    """Tests for EvolutionPhase enum."""

    def test_collecting_phase(self):
        """Test COLLECTING phase exists."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionPhase
        assert EvolutionPhase.COLLECTING.value == "collecting"

    def test_training_phase(self):
        """Test TRAINING phase exists."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionPhase
        assert EvolutionPhase.TRAINING.value == "training"

    def test_validating_phase(self):
        """Test VALIDATING phase exists."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionPhase
        assert EvolutionPhase.VALIDATING.value == "validating"

    def test_deployed_phase(self):
        """Test DEPLOYED phase exists."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionPhase
        assert EvolutionPhase.DEPLOYED.value == "deployed"

    def test_monitoring_phase(self):
        """Test MONITORING phase exists."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionPhase
        assert EvolutionPhase.MONITORING.value == "monitoring"


class TestEvolutionCycle:
    """Tests for EvolutionCycle dataclass."""

    def test_evolution_cycle_creation(self):
        """Test creating an EvolutionCycle."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionCycle
        now = datetime.now()
        cycle = EvolutionCycle(
            cycle_id='test_cycle_001',
            started_at=now,
            completed_at=now,
            escalations_processed=10,
            training_examples=100,
            previous_escalation_rate=0.25,
            new_escalation_rate=0.20,
            improvement=0.05,
            status='completed'
        )

        assert cycle.cycle_id == 'test_cycle_001'
        assert cycle.escalations_processed == 10
        assert cycle.training_examples == 100
        assert cycle.previous_escalation_rate == 0.25
        assert cycle.new_escalation_rate == 0.20
        assert cycle.improvement == 0.05
        assert cycle.status == 'completed'

    def test_evolution_cycle_with_none_completed(self):
        """Test EvolutionCycle with None completed_at."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionCycle
        now = datetime.now()
        cycle = EvolutionCycle(
            cycle_id='test_cycle_002',
            started_at=now,
            completed_at=None,
            escalations_processed=5,
            training_examples=0,
            previous_escalation_rate=0.30,
            new_escalation_rate=0.30,
            improvement=0.0,
            status='in_progress'
        )

        assert cycle.completed_at is None
        assert cycle.status == 'in_progress'


class TestEvolutionaryFlywheel:
    """Tests for EvolutionaryFlywheel class."""

    def test_init_defaults(self):
        """Test initialization with defaults."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel, EvolutionPhase
        flywheel = EvolutionaryFlywheel()

        assert flywheel.harvester is None
        assert flywheel.distillation is None
        assert flywheel.escalation_threshold == 10
        assert flywheel.max_escalation_rate == 0.25
        assert flywheel.current_phase == EvolutionPhase.COLLECTING
        assert flywheel.escalation_count == 0
        assert flywheel.total_queries == 0

    def test_init_custom_threshold(self):
        """Test initialization with custom escalation threshold."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(escalation_threshold=20)
        assert flywheel.escalation_threshold == 20

    def test_init_custom_max_rate(self):
        """Test initialization with custom max escalation rate."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(max_escalation_rate=0.50)
        assert flywheel.max_escalation_rate == 0.50

    def test_init_with_harvester(self):
        """Test initialization with harvester."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        mock_harvester = Mock()
        flywheel = EvolutionaryFlywheel(harvester=mock_harvester)
        assert flywheel.harvester is mock_harvester

    def test_init_with_distillation(self):
        """Test initialization with distillation pipeline."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        mock_distillation = Mock()
        flywheel = EvolutionaryFlywheel(distillation=mock_distillation)
        assert flywheel.distillation is mock_distillation

    def test_default_constants(self):
        """Test default constants are defined."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        assert EvolutionaryFlywheel.DEFAULT_ESCALATION_THRESHOLD == 10
        assert EvolutionaryFlywheel.DEFAULT_MAX_ESCALATION_RATE == 0.25
        assert EvolutionaryFlywheel.DEFAULT_MIN_IMPROVEMENT == 0.05

    def test_record_query(self):
        """Test record_query increments total_queries."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        flywheel.record_query('student')
        assert flywheel.total_queries == 1

        flywheel.record_query('teacher')
        assert flywheel.total_queries == 2

    def test_record_escalation_basic(self):
        """Test record_escalation basic functionality."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        flywheel.record_escalation(
            query='solve x^2 = 4',
            student_confidence=0.3,
            teacher_result={'verified': True, 'result': 'x = 2'}
        )

        assert flywheel.escalation_count == 1
        assert flywheel.stats['total_escalations'] == 1
        assert len(flywheel.pending_escalations) == 1

    def test_record_escalation_updates_rate(self):
        """Test record_escalation updates escalation rate."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        # Record some queries first
        flywheel.total_queries = 10

        flywheel.record_escalation(
            query='prove theorem',
            student_confidence=0.2,
            teacher_result={'verified': True}
        )

        assert flywheel.stats['current_escalation_rate'] > 0

    def test_record_escalation_with_trace_id(self):
        """Test record_escalation with trace ID."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        mock_harvester = Mock()
        mock_trace = Mock()
        mock_trace.metadata = {}
        mock_harvester._get_trace.return_value = mock_trace

        flywheel = EvolutionaryFlywheel(harvester=mock_harvester)

        flywheel.record_escalation(
            query='integrate x^2',
            student_confidence=0.1,
            teacher_result={'verified': True},
            trace_id='trace_001'
        )

        # Trace should be marked as high priority
        mock_harvester._get_trace.assert_called_with('trace_001')
        assert mock_trace.metadata['escalated'] is True
        assert mock_trace.metadata['learning_priority'] == 'high'

    def test_record_escalation_triggers_evolution(self):
        """Test that record_escalation triggers evolution when threshold reached."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(escalation_threshold=2)

        flywheel.record_escalation('q1', 0.3, {'verified': True})
        assert flywheel.escalation_count == 1

        # This should trigger evolution
        flywheel.record_escalation('q2', 0.3, {'verified': True})

        # After evolution, count is reset
        assert flywheel.escalation_count == 0
        assert flywheel.stats['evolution_cycles'] == 1

    def test_should_evolve_threshold_not_reached(self):
        """Test should_evolve returns False when threshold not reached."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(escalation_threshold=10)
        flywheel.escalation_count = 5

        assert flywheel.should_evolve() is False

    def test_should_evolve_threshold_reached(self):
        """Test should_evolve returns True when threshold reached."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(escalation_threshold=10)
        flywheel.escalation_count = 10

        assert flywheel.should_evolve() is True

    def test_should_evolve_escalation_rate_high(self):
        """Test should_evolve returns True when escalation rate exceeds max."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(max_escalation_rate=0.25)
        flywheel.total_queries = 200
        flywheel.stats['current_escalation_rate'] = 0.30

        assert flywheel.should_evolve() is True

    def test_should_evolve_not_enough_queries(self):
        """Test should_evolve doesn't trigger on rate if not enough queries."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(max_escalation_rate=0.25)
        flywheel.total_queries = 50  # Less than 100
        flywheel.stats['current_escalation_rate'] = 0.30

        assert flywheel.should_evolve() is False  # Not enough queries

    def test_trigger_evolution_cycle_already_training(self):
        """Test _trigger_evolution_cycle does nothing if already training."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel, EvolutionPhase
        flywheel = EvolutionaryFlywheel()
        flywheel.current_phase = EvolutionPhase.TRAINING

        initial_cycle_count = flywheel.cycle_count
        flywheel._trigger_evolution_cycle()

        assert flywheel.cycle_count == initial_cycle_count  # No new cycle

    def test_trigger_evolution_cycle_with_distillation(self):
        """Test _trigger_evolution_cycle with distillation pipeline."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel, EvolutionPhase
        mock_distillation = Mock()
        mock_distillation.run_distillation.return_value = {'examples_trained': 50}

        flywheel = EvolutionaryFlywheel(distillation=mock_distillation)
        flywheel.escalation_count = 5

        flywheel._trigger_evolution_cycle()

        mock_distillation.run_distillation.assert_called_once_with(prioritize_escalated=True)
        assert flywheel.current_phase == EvolutionPhase.MONITORING
        assert flywheel.escalation_count == 0
        assert len(flywheel.evolution_cycles) == 1

    def test_trigger_evolution_cycle_without_distillation(self):
        """Test _trigger_evolution_cycle without distillation pipeline."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()
        flywheel.escalation_count = 5

        flywheel._trigger_evolution_cycle()

        assert len(flywheel.evolution_cycles) == 1
        assert flywheel.evolution_cycles[0].training_examples == 0

    def test_trigger_immediate_evolution(self):
        """Test trigger_immediate_evolution."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()
        flywheel.escalation_count = 3

        result = flywheel.trigger_immediate_evolution()

        assert result['triggered'] is True
        assert result['escalations_processed'] == 3
        assert result['cycle_id'] is not None

    def test_trigger_immediate_evolution_no_cycles(self):
        """Test trigger_immediate_evolution with no previous cycles."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        result = flywheel.trigger_immediate_evolution()

        assert result['triggered'] is True
        assert result['cycle_id'] is not None

    def test_update_escalation_rate_with_improvement(self):
        """Test update_escalation_rate with improvement."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        # Create an evolution cycle first
        flywheel._trigger_evolution_cycle()
        flywheel.evolution_cycles[-1].previous_escalation_rate = 0.25

        flywheel.update_escalation_rate(0.20)

        assert flywheel.stats['current_escalation_rate'] == 0.20
        assert flywheel.evolution_cycles[-1].improvement == pytest.approx(0.05)
        assert flywheel.stats['total_improvement'] == pytest.approx(0.05)

    def test_update_escalation_rate_no_cycles(self):
        """Test update_escalation_rate with no previous cycles."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        # Should not raise even without cycles
        flywheel.update_escalation_rate(0.15)

        assert flywheel.stats['current_escalation_rate'] == 0.15

    def test_update_escalation_rate_negative_improvement(self):
        """Test update_escalation_rate with worse performance."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        flywheel._trigger_evolution_cycle()
        flywheel.evolution_cycles[-1].previous_escalation_rate = 0.20

        flywheel.update_escalation_rate(0.25)  # Worse

        assert flywheel.evolution_cycles[-1].improvement == pytest.approx(-0.05)

    def test_get_evolution_metrics(self):
        """Test get_evolution_metrics returns expected structure."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        metrics = flywheel.get_evolution_metrics()

        assert 'total_cycles' in metrics
        assert 'current_phase' in metrics
        assert 'current_escalation_rate' in metrics
        assert 'baseline_escalation_rate' in metrics
        assert 'total_improvement' in metrics
        assert 'pending_escalations' in metrics
        assert 'escalation_count' in metrics
        assert 'escalation_threshold' in metrics
        assert 'recent_cycles' in metrics

    def test_get_evolution_metrics_with_cycles(self):
        """Test get_evolution_metrics with evolution cycles."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        # Create a few cycles
        flywheel._trigger_evolution_cycle()
        flywheel.current_phase = flywheel.current_phase.__class__.COLLECTING
        flywheel._trigger_evolution_cycle()

        metrics = flywheel.get_evolution_metrics()

        assert metrics['total_cycles'] == 2
        assert len(metrics['recent_cycles']) == 2

    def test_get_learning_insights_empty(self):
        """Test get_learning_insights with no data."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        insights = flywheel.get_learning_insights()

        assert isinstance(insights, list)

    def test_get_learning_insights_with_escalations(self):
        """Test get_learning_insights with pending escalations."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(escalation_threshold=100)  # High threshold to prevent evolution

        # Add various escalations
        flywheel.record_escalation('prove theorem A', 0.2, {'verified': True})
        flywheel.record_escalation('prove theorem B', 0.2, {'verified': True})
        flywheel.record_escalation('integrate x^2', 0.1, {'verified': True})

        insights = flywheel.get_learning_insights()

        # Should identify proof pattern
        assert any(i.get('category') == 'proof' for i in insights)

    def test_get_learning_insights_integration_pattern(self):
        """Test get_learning_insights identifies integration pattern."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(escalation_threshold=100)

        flywheel.record_escalation('integrate x', 0.2, {'verified': True})
        flywheel.record_escalation('integrate sin(x)', 0.2, {'verified': True})

        insights = flywheel.get_learning_insights()

        assert any(i.get('category') == 'integration' for i in insights)

    def test_get_learning_insights_solve_pattern(self):
        """Test get_learning_insights identifies equation pattern."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel(escalation_threshold=100)

        flywheel.record_escalation('solve x^2 = 4', 0.2, {'verified': True})
        flywheel.record_escalation('solve 2x + 1 = 0', 0.2, {'verified': True})

        insights = flywheel.get_learning_insights()

        assert any(i.get('category') == 'equation' for i in insights)

    def test_get_learning_insights_improvement_trend(self):
        """Test get_learning_insights detects improvement trend."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        # Create two cycles with increasing improvement
        flywheel._trigger_evolution_cycle()
        flywheel.evolution_cycles[-1].improvement = 0.05
        flywheel.current_phase = flywheel.current_phase.__class__.COLLECTING

        flywheel._trigger_evolution_cycle()
        flywheel.evolution_cycles[-1].improvement = 0.10

        insights = flywheel.get_learning_insights()

        assert any(i.get('type') == 'trend' for i in insights)

    def test_get_learning_insights_warning_trend(self):
        """Test get_learning_insights detects negative trend."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        # Create two cycles with declining performance
        flywheel._trigger_evolution_cycle()
        flywheel.evolution_cycles[-1].improvement = 0.05
        flywheel.current_phase = flywheel.current_phase.__class__.COLLECTING

        flywheel._trigger_evolution_cycle()
        flywheel.evolution_cycles[-1].improvement = -0.05  # Negative improvement

        insights = flywheel.get_learning_insights()

        assert any(i.get('type') == 'warning' for i in insights)

    def test_get_statistics(self):
        """Test get_statistics returns expected structure."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()

        stats = flywheel.get_statistics()

        assert 'total_escalations' in stats
        assert 'evolution_cycles' in stats
        assert 'total_improvement' in stats
        assert 'current_escalation_rate' in stats
        assert 'current_phase' in stats
        assert 'pending_count' in stats
        assert 'threshold' in stats
        assert 'queries_tracked' in stats

    def test_reset(self):
        """Test reset clears flywheel state."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel, EvolutionPhase
        flywheel = EvolutionaryFlywheel()

        # Add some state
        flywheel.escalation_count = 5
        flywheel.total_queries = 100
        flywheel.pending_escalations = [{'query': 'test'}]
        flywheel.current_phase = EvolutionPhase.TRAINING

        flywheel.reset()

        assert flywheel.escalation_count == 0
        assert flywheel.total_queries == 0
        assert flywheel.pending_escalations == []
        assert flywheel.current_phase == EvolutionPhase.COLLECTING


class TestModuleFunctions:
    """Tests for module-level functions and imports."""

    def test_module_imports(self):
        """Test that module imports correctly."""
        from symbo_agentic_reasoners.optimization import evolutionary_flywheel
        assert evolutionary_flywheel is not None

    def test_evolution_phase_export(self):
        """Test EvolutionPhase is accessible."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionPhase
        assert EvolutionPhase is not None

    def test_evolution_cycle_export(self):
        """Test EvolutionCycle is accessible."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionCycle
        assert EvolutionCycle is not None

    def test_evolutionary_flywheel_export(self):
        """Test EvolutionaryFlywheel is accessible."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        assert EvolutionaryFlywheel is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
