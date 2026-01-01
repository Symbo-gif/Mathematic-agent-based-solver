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
Meta-Learning Tests
===================

Comprehensive tests for Phase 4 Meta-Learning Team:
- SolutionTrace dataclass
- RoutingHeuristic dataclass
- ComplexityLevel enum
- PerformanceMonitor
- AgentSelectorOptimizer
- AdaptiveDispatcher
- MetaLearningTeam
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from symbo_agentic_reasoners.middleware.meta_learning import (
    SolutionTrace,
    RoutingHeuristic,
    ComplexityLevel,
    PerformanceMonitor,
    AgentSelectorOptimizer,
    AdaptiveDispatcher,
    MetaLearningTeam,
)


# =============================================================================
# SolutionTrace Tests
# =============================================================================


class TestSolutionTrace:
    """Tests for SolutionTrace dataclass."""

    def test_create_trace_defaults(self):
        """Should create trace with defaults."""
        trace = SolutionTrace()

        assert trace.trace_id.startswith('trace_')
        assert trace.conversation_id == ""
        assert trace.problem_type == "unknown"
        assert trace.problem_complexity == "medium"
        assert trace.agent_sequence == []
        assert trace.time_taken_ms == 0.0
        assert trace.success is False
        assert trace.timestamp is not None

    def test_create_trace_with_values(self):
        """Should create trace with provided values."""
        trace = SolutionTrace(
            conversation_id='conv_001',
            problem_type='integration',
            problem_complexity='high',
            agent_sequence=['agent_1', 'agent_2'],
            time_taken_ms=1500.0,
            token_count=500,
            success=True,
            verification_status='VERIFIED'
        )

        assert trace.conversation_id == 'conv_001'
        assert trace.problem_type == 'integration'
        assert trace.problem_complexity == 'high'
        assert len(trace.agent_sequence) == 2
        assert trace.time_taken_ms == 1500.0
        assert trace.token_count == 500
        assert trace.success is True
        assert trace.verification_status == 'VERIFIED'

    def test_to_dict(self):
        """Should convert to dictionary."""
        trace = SolutionTrace(
            conversation_id='conv_001',
            problem_type='algebra',
            success=True
        )

        d = trace.to_dict()

        assert isinstance(d, dict)
        assert d['conversation_id'] == 'conv_001'
        assert d['problem_type'] == 'algebra'
        assert d['success'] is True
        assert 'timestamp' in d
        assert 'trace_id' in d


# =============================================================================
# RoutingHeuristic Tests
# =============================================================================


class TestRoutingHeuristic:
    """Tests for RoutingHeuristic dataclass."""

    def test_create_heuristic(self):
        """Should create routing heuristic."""
        heuristic = RoutingHeuristic(
            agent_id='agent_001',
            problem_type='integration',
            weight=85.5,
            success_rate=0.9,
            avg_time_ms=1200.0,
            sample_size=50
        )

        assert heuristic.agent_id == 'agent_001'
        assert heuristic.problem_type == 'integration'
        assert heuristic.weight == 85.5
        assert heuristic.success_rate == 0.9
        assert heuristic.avg_time_ms == 1200.0
        assert heuristic.sample_size == 50
        assert heuristic.last_updated is not None


# =============================================================================
# ComplexityLevel Tests
# =============================================================================


class TestComplexityLevel:
    """Tests for ComplexityLevel enum."""

    def test_all_levels_exist(self):
        """All complexity levels should exist."""
        assert hasattr(ComplexityLevel, 'SIMPLE')
        assert hasattr(ComplexityLevel, 'STANDARD')
        assert hasattr(ComplexityLevel, 'COMPLEX')


# =============================================================================
# PerformanceMonitor Tests
# =============================================================================


class TestPerformanceMonitor:
    """Tests for PerformanceMonitor agent."""

    @pytest.fixture
    def monitor(self):
        """Create monitor without infrastructure."""
        with patch('builtins.print'):
            return PerformanceMonitor()

    def test_initialization(self, monitor):
        """Should initialize with empty state."""
        assert monitor.blackboard is None
        assert monitor.vector_db is None
        assert monitor.active_traces == {}
        assert monitor.completed_traces == []
        assert monitor.traces_recorded == 0

    def test_initialization_with_infrastructure(self):
        """Should initialize with infrastructure."""
        bb = Mock()
        vdb = Mock()

        with patch('builtins.print'):
            monitor = PerformanceMonitor(blackboard=bb, vector_db=vdb)

        assert monitor.blackboard is bb
        assert monitor.vector_db is vdb

    def test_on_task_start(self, monitor):
        """Should create active trace for new task."""
        event = {
            'conversation_id': 'conv_001',
            'problem_type': 'integration',
            'complexity': 'high'
        }

        monitor.on_task_start(event)

        assert 'conv_001' in monitor.active_traces
        trace = monitor.active_traces['conv_001']
        assert trace['problem_type'] == 'integration'
        assert trace['problem_complexity'] == 'high'
        assert trace['agent_sequence'] == []

    def test_on_agent_invoked(self, monitor):
        """Should record agent invocation."""
        # Start task first
        monitor.on_task_start({
            'conversation_id': 'conv_001',
            'problem_type': 'algebra'
        })

        # Invoke agent
        monitor.on_agent_invoked({
            'conversation_id': 'conv_001',
            'agent_id': 'algebra_specialist_001',
            'input_tokens': 100,
            'vram_mb': 512.0
        })

        trace = monitor.active_traces['conv_001']
        assert 'algebra_specialist_001' in trace['agent_sequence']
        assert trace['token_count'] == 100
        assert 512.0 in trace['vram_readings']

    def test_on_agent_invoked_unknown_conversation(self, monitor):
        """Should handle unknown conversation gracefully."""
        # Should not raise
        monitor.on_agent_invoked({
            'conversation_id': 'unknown',
            'agent_id': 'agent_001'
        })

    def test_on_verification(self, monitor):
        """Should record verification status."""
        monitor.on_task_start({
            'conversation_id': 'conv_001',
            'problem_type': 'calculus'
        })

        monitor.on_verification({
            'conversation_id': 'conv_001',
            'status': 'VERIFIED'
        })

        trace = monitor.active_traces['conv_001']
        assert trace['verification_status'] == 'VERIFIED'
        assert trace['success'] is True

    def test_on_session_end(self, monitor):
        """Should complete trace and store it."""
        monitor.on_task_start({
            'conversation_id': 'conv_001',
            'problem_type': 'integration'
        })
        monitor.on_agent_invoked({
            'conversation_id': 'conv_001',
            'agent_id': 'agent_1'
        })
        monitor.on_verification({
            'conversation_id': 'conv_001',
            'status': 'VERIFIED'
        })

        result = monitor.on_session_end({'conversation_id': 'conv_001'})

        assert result is not None
        assert isinstance(result, SolutionTrace)
        assert result.success is True
        assert 'conv_001' not in monitor.active_traces
        assert monitor.traces_recorded == 1
        assert monitor.successful_traces == 1

    def test_on_session_end_failed(self, monitor):
        """Should track failed traces."""
        monitor.on_task_start({
            'conversation_id': 'conv_001',
            'problem_type': 'algebra'
        })
        monitor.on_verification({
            'conversation_id': 'conv_001',
            'status': 'FAILED'
        })

        result = monitor.on_session_end({'conversation_id': 'conv_001'})

        assert result.success is False
        assert monitor.failed_traces == 1

    def test_on_session_end_unknown_conversation(self, monitor):
        """Should return None for unknown conversation."""
        result = monitor.on_session_end({'conversation_id': 'unknown'})

        assert result is None

    def test_get_recent_traces(self, monitor):
        """Should return recent traces."""
        # Create some completed traces
        for i in range(5):
            monitor.on_task_start({
                'conversation_id': f'conv_{i}',
                'problem_type': 'algebra' if i % 2 == 0 else 'calculus'
            })
            monitor.on_session_end({'conversation_id': f'conv_{i}'})

        traces = monitor.get_recent_traces()
        assert len(traces) == 5

        # Filter by problem type
        algebra_traces = monitor.get_recent_traces(problem_type='algebra')
        assert len(algebra_traces) == 3

    def test_get_statistics(self, monitor):
        """Should return statistics."""
        monitor.on_task_start({
            'conversation_id': 'conv_001',
            'problem_type': 'algebra'
        })
        monitor.on_verification({
            'conversation_id': 'conv_001',
            'status': 'VERIFIED'
        })
        monitor.on_session_end({'conversation_id': 'conv_001'})

        stats = monitor.get_statistics()

        assert isinstance(stats, dict)
        assert stats['traces_recorded'] == 1
        assert stats['successful_traces'] == 1
        assert stats['success_rate'] == 100.0


# =============================================================================
# AgentSelectorOptimizer Tests
# =============================================================================


class TestAgentSelectorOptimizer:
    """Tests for AgentSelectorOptimizer (AutoMaAS)."""

    @pytest.fixture
    def optimizer(self):
        """Create optimizer without infrastructure."""
        with patch('builtins.print'):
            return AgentSelectorOptimizer()

    def test_initialization(self, optimizer):
        """Should initialize with empty state."""
        assert optimizer.blackboard is None
        assert optimizer.routing_tables == {}
        assert optimizer.traces_analyzed == 0

    def test_analyze_trace(self, optimizer):
        """Should analyze trace and update stats."""
        trace = {
            'problem_type': 'integration',
            'agent_sequence': ['agent_1', 'agent_2'],
            'success': True,
            'time_taken_ms': 1000.0
        }

        optimizer.analyze_trace(trace)

        assert optimizer.traces_analyzed == 1
        assert 'integration' in optimizer.performance_stats
        assert 'agent_1' in optimizer.performance_stats['integration']
        assert 'agent_2' in optimizer.performance_stats['integration']

    def test_analyze_multiple_traces(self, optimizer):
        """Should accumulate statistics from multiple traces."""
        for i in range(10):
            trace = {
                'problem_type': 'algebra',
                'agent_sequence': ['algebra_agent'],
                'success': i % 3 != 0,  # 70% success
                'time_taken_ms': 500.0
            }
            optimizer.analyze_trace(trace)

        assert optimizer.traces_analyzed == 10
        stats = optimizer.performance_stats['algebra']['algebra_agent']
        assert len(stats) == 10

    def test_compute_routing_tables(self, optimizer):
        """Should compute routing tables from stats."""
        # Add some traces
        for i in range(50):
            optimizer.analyze_trace({
                'problem_type': 'calculus',
                'agent_sequence': ['symbolic_agent'],
                'success': True,
                'time_taken_ms': 800.0
            })

        tables = optimizer.compute_routing_tables()

        assert 'calculus' in tables
        assert 'symbolic_agent' in tables['calculus']
        assert tables['calculus']['symbolic_agent']['success_rate'] == 1.0
        assert optimizer.routing_updates == 1

    def test_compute_weight(self, optimizer):
        """Should compute routing weight correctly."""
        # High success, fast time, high confidence
        weight = optimizer._compute_weight(
            success_rate=0.9,
            avg_time=500.0,
            sample_size=50
        )
        assert weight > 80  # Should be high

        # Low success
        weight_low = optimizer._compute_weight(
            success_rate=0.2,
            avg_time=500.0,
            sample_size=50
        )
        assert weight_low < weight

    def test_get_pattern_insights(self, optimizer):
        """Should generate insights from patterns."""
        # Create clear pattern: agent_1 succeeds, agent_2 fails
        for i in range(20):
            optimizer.analyze_trace({
                'problem_type': 'optimization',
                'agent_sequence': ['agent_1'],
                'success': True,
                'time_taken_ms': 500.0
            })
            optimizer.analyze_trace({
                'problem_type': 'optimization',
                'agent_sequence': ['agent_2'],
                'success': False,
                'time_taken_ms': 500.0
            })

        optimizer.compute_routing_tables()
        insights = optimizer.get_pattern_insights()

        assert len(insights) > 0
        assert 'optimization' in insights[0]['problem_type']

    def test_get_best_agents(self, optimizer):
        """Should return best agents for problem type."""
        # Create data with clear ranking
        for i in range(20):
            optimizer.analyze_trace({
                'problem_type': 'algebra',
                'agent_sequence': ['best_agent'],
                'success': True,
                'time_taken_ms': 300.0
            })
            optimizer.analyze_trace({
                'problem_type': 'algebra',
                'agent_sequence': ['ok_agent'],
                'success': True,
                'time_taken_ms': 800.0
            })
            optimizer.analyze_trace({
                'problem_type': 'algebra',
                'agent_sequence': ['bad_agent'],
                'success': False,
                'time_taken_ms': 500.0
            })

        optimizer.compute_routing_tables()

        best = optimizer.get_best_agents('algebra', 2)
        assert 'best_agent' in best
        assert len(best) <= 2

    def test_get_best_agents_unknown_type(self, optimizer):
        """Should return empty for unknown problem type."""
        best = optimizer.get_best_agents('unknown_type', 3)
        assert best == []

    def test_get_statistics(self, optimizer):
        """Should return optimizer statistics."""
        stats = optimizer.get_statistics()

        assert isinstance(stats, dict)
        assert 'traces_analyzed' in stats
        assert 'routing_updates' in stats
        assert 'patterns_discovered' in stats


# =============================================================================
# AdaptiveDispatcher Tests
# =============================================================================


class TestAdaptiveDispatcher:
    """Tests for AdaptiveDispatcher agent."""

    @pytest.fixture
    def dispatcher(self):
        """Create dispatcher without infrastructure."""
        with patch('builtins.print'):
            return AdaptiveDispatcher()

    def test_initialization(self, dispatcher):
        """Should initialize with empty state."""
        assert dispatcher.blackboard is None
        assert dispatcher.optimizer is None
        assert dispatcher.orchestrator is None
        assert dispatcher.dispatches == 0

    def test_initialization_with_dependencies(self):
        """Should initialize with dependencies."""
        bb = Mock()
        opt = Mock()
        orch = Mock()

        with patch('builtins.print'):
            dispatcher = AdaptiveDispatcher(
                blackboard=bb,
                optimizer=opt,
                orchestrator=orch
            )

        assert dispatcher.blackboard is bb
        assert dispatcher.optimizer is opt
        assert dispatcher.orchestrator is orch

    def test_determine_team_size_simple(self, dispatcher):
        """Should return skeleton crew for simple problems."""
        context = {
            'problem_type': 'algebra',
            'simple_expression': True,
            'standard_form': True
        }

        size = dispatcher.determine_team_size(context)

        assert size == dispatcher.SKELETON_CREW_SIZE
        assert dispatcher.skeleton_crew_dispatches == 1

    def test_determine_team_size_complex(self, dispatcher):
        """Should return full team for complex problems."""
        context = {
            'problem_type': 'proof',
            'involves_proof': True,
            'multiple_steps': True,
            'novel_pattern': True
        }

        size = dispatcher.determine_team_size(context)

        assert size == dispatcher.FULL_DEBATE_SIZE
        assert dispatcher.full_team_dispatches == 1

    def test_determine_team_size_standard(self, dispatcher):
        """Should return standard team for medium complexity."""
        context = {
            'problem_type': 'calculus',
            'verification_required': True
        }

        size = dispatcher.determine_team_size(context)

        # Medium complexity should get standard team
        assert size in [dispatcher.SKELETON_CREW_SIZE,
                       dispatcher.STANDARD_TEAM_SIZE,
                       dispatcher.FULL_DEBATE_SIZE]

    def test_get_complexity_level_simple(self, dispatcher):
        """Should return SIMPLE for simple problems."""
        context = {
            'simple_expression': True,
            'standard_form': True,
            'similar_solved_recently': True
        }

        level = dispatcher.get_complexity_level(context)

        assert level == ComplexityLevel.SIMPLE

    def test_get_complexity_level_complex(self, dispatcher):
        """Should return COMPLEX for complex problems."""
        context = {
            'problem_type': 'proof',
            'involves_proof': True,
            'multiple_steps': True,
            'novel_pattern': True,
            'verification_required': True
        }

        level = dispatcher.get_complexity_level(context)

        assert level == ComplexityLevel.COMPLEX

    def test_estimate_complexity(self, dispatcher):
        """Should estimate complexity correctly."""
        # Simple problem
        simple = dispatcher._estimate_complexity({
            'simple_expression': True,
            'standard_form': True
        })
        assert simple < 0.4

        # Complex problem
        complex_ = dispatcher._estimate_complexity({
            'involves_proof': True,
            'novel_pattern': True,
            'multiple_steps': True
        })
        assert complex_ > 0.7

    def test_select_agents_with_optimizer(self):
        """Should use optimizer to select agents."""
        with patch('builtins.print'):
            opt = Mock()
            opt.get_best_agents.return_value = ['agent_1', 'agent_2', 'agent_3']
            dispatcher = AdaptiveDispatcher(optimizer=opt)

        agents = dispatcher.select_agents('algebra', 3)

        assert agents == ['agent_1', 'agent_2', 'agent_3']
        opt.get_best_agents.assert_called_once_with('algebra', 3)

    def test_select_agents_without_optimizer(self, dispatcher):
        """Should return empty list without optimizer."""
        agents = dispatcher.select_agents('algebra', 3)

        assert agents == []

    def test_update_orchestrator(self):
        """Should push routing to orchestrator."""
        with patch('builtins.print'):
            orch = Mock()
            orch.update_routing_heuristics = Mock()
            dispatcher = AdaptiveDispatcher(orchestrator=orch)

        tables = {'algebra': {'agent_1': {'weight': 80}}}
        dispatcher.update_orchestrator(tables)

        orch.update_routing_heuristics.assert_called_once_with(tables)
        assert dispatcher.routing_pushes == 1

    def test_get_statistics(self, dispatcher):
        """Should return dispatcher statistics."""
        # Make some dispatches
        dispatcher.determine_team_size({'simple_expression': True})
        dispatcher.determine_team_size({'involves_proof': True, 'novel_pattern': True})

        stats = dispatcher.get_statistics()

        assert isinstance(stats, dict)
        assert stats['total_dispatches'] == 2
        assert 'skeleton_crew_dispatches' in stats
        assert 'full_team_dispatches' in stats


# =============================================================================
# MetaLearningTeam Tests
# =============================================================================


class TestMetaLearningTeam:
    """Tests for MetaLearningTeam coordinator."""

    @pytest.fixture
    def team(self):
        """Create team without infrastructure."""
        with patch('builtins.print'):
            return MetaLearningTeam()

    def test_initialization(self, team):
        """Should initialize all three agents."""
        assert team.performance_monitor is not None
        assert team.optimizer is not None
        assert team.dispatcher is not None
        assert team.optimization_runs == 0

    def test_initialization_with_infrastructure(self):
        """Should pass infrastructure to agents."""
        bb = Mock()
        vdb = Mock()
        orch = Mock()

        with patch('builtins.print'):
            team = MetaLearningTeam(
                blackboard=bb,
                vector_db=vdb,
                orchestrator=orch
            )

        assert team.blackboard is bb
        assert team.performance_monitor.blackboard is bb
        assert team.optimizer.blackboard is bb

    def test_log_task_start(self, team):
        """Should delegate to performance monitor."""
        team.log_task_start('conv_001', 'integration', 'high')

        assert 'conv_001' in team.performance_monitor.active_traces

    def test_log_agent_invocation(self, team):
        """Should delegate to performance monitor."""
        team.log_task_start('conv_001', 'algebra')
        team.log_agent_invocation('conv_001', 'agent_1', 100, 512.0)

        trace = team.performance_monitor.active_traces['conv_001']
        assert 'agent_1' in trace['agent_sequence']

    def test_log_verification(self, team):
        """Should delegate to performance monitor."""
        team.log_task_start('conv_001', 'calculus')
        team.log_verification('conv_001', 'VERIFIED')

        trace = team.performance_monitor.active_traces['conv_001']
        assert trace['success'] is True

    def test_log_session_end(self, team):
        """Should complete trace and analyze."""
        team.log_task_start('conv_001', 'integration')
        team.log_agent_invocation('conv_001', 'agent_1')
        team.log_verification('conv_001', 'VERIFIED')

        result = team.log_session_end('conv_001')

        assert result is not None
        assert team.optimizer.traces_analyzed == 1

    def test_run_batch_optimization(self, team):
        """Should compute routing and generate insights."""
        # Create some traces
        for i in range(10):
            team.log_task_start(f'conv_{i}', 'algebra')
            team.log_agent_invocation(f'conv_{i}', 'agent_1')
            team.log_verification(f'conv_{i}', 'VERIFIED')
            team.log_session_end(f'conv_{i}')

        results = team.run_batch_optimization()

        assert team.optimization_runs == 1
        assert 'tables_updated' in results
        assert 'insights_generated' in results

    def test_get_team_recommendation(self, team):
        """Should return team recommendation."""
        context = {
            'problem_type': 'algebra',
            'simple_expression': True
        }

        rec = team.get_team_recommendation(context)

        assert 'team_size' in rec
        assert 'complexity_level' in rec
        assert 'suggested_agents' in rec
        assert 'rationale' in rec

    def test_get_team_recommendation_complex(self, team):
        """Should recommend larger team for complex problems."""
        simple_context = {
            'simple_expression': True,
            'standard_form': True
        }
        complex_context = {
            'problem_type': 'proof',
            'involves_proof': True,
            'multiple_steps': True,
            'novel_pattern': True
        }

        simple_rec = team.get_team_recommendation(simple_context)
        complex_rec = team.get_team_recommendation(complex_context)

        assert complex_rec['team_size'] > simple_rec['team_size']

    def test_get_statistics(self, team):
        """Should return comprehensive statistics."""
        stats = team.get_statistics()

        assert isinstance(stats, dict)
        assert 'optimization_runs' in stats
        assert 'performance_monitor' in stats
        assert 'optimizer' in stats
        assert 'dispatcher' in stats

        # Nested stats should be dicts
        assert isinstance(stats['performance_monitor'], dict)
        assert isinstance(stats['optimizer'], dict)
        assert isinstance(stats['dispatcher'], dict)


# =============================================================================
# Integration Tests
# =============================================================================


class TestMetaLearningIntegration:
    """Integration tests for meta-learning workflow."""

    def test_full_learning_workflow(self):
        """Test complete meta-learning pipeline."""
        with patch('builtins.print'):
            team = MetaLearningTeam()

        # Simulate multiple solution traces
        for i in range(20):
            conv_id = f'conv_{i}'

            # Start task
            team.log_task_start(conv_id, 'integration')

            # Invoke different agents with different success rates
            if i % 3 == 0:
                # Symbolic agent - lower success rate
                team.log_agent_invocation(conv_id, 'symbolic_agent', 100)
                team.log_verification(conv_id, 'FAILED' if i % 2 == 0 else 'VERIFIED')
            else:
                # Numerical agent - higher success rate
                team.log_agent_invocation(conv_id, 'numerical_agent', 50)
                team.log_verification(conv_id, 'VERIFIED')

            # Complete session
            team.log_session_end(conv_id)

        # Run optimization
        results = team.run_batch_optimization()

        # Verify learning occurred
        assert team.optimizer.traces_analyzed == 20
        assert results['tables_updated'] >= 1

        # Get statistics
        stats = team.get_statistics()
        assert stats['performance_monitor']['traces_recorded'] == 20

    def test_team_recommendation_adapts(self):
        """Test that recommendations adapt to learned patterns."""
        with patch('builtins.print'):
            team = MetaLearningTeam()

        # Train on successful algebra agent
        for i in range(30):
            team.log_task_start(f'conv_{i}', 'algebra')
            team.log_agent_invocation(f'conv_{i}', 'best_algebra_agent')
            team.log_verification(f'conv_{i}', 'VERIFIED')
            team.log_session_end(f'conv_{i}')

        # Optimize
        team.run_batch_optimization()

        # Get recommendation
        rec = team.get_team_recommendation({
            'problem_type': 'algebra'
        })

        # Should have recommendation
        assert rec['team_size'] > 0
        assert rec['complexity_level'] in ['SIMPLE', 'STANDARD', 'COMPLEX']

    def test_complexity_scaling(self):
        """Test that complexity correctly scales team size."""
        with patch('builtins.print'):
            team = MetaLearningTeam()

        test_cases = [
            ({'simple_expression': True, 'standard_form': True}, 'SIMPLE'),
            ({'verification_required': True}, 'STANDARD'),
            ({'involves_proof': True, 'novel_pattern': True, 'multiple_steps': True}, 'COMPLEX'),
        ]

        for context, expected_level in test_cases:
            rec = team.get_team_recommendation(context)
            # Verify complexity is correctly assessed
            assert rec['complexity_level'] in ['SIMPLE', 'STANDARD', 'COMPLEX']


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
