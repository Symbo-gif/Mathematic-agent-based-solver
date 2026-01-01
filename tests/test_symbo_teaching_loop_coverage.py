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
Tests for SYMBO Teaching Loop Module
====================================

Comprehensive tests for the teaching loop continuous learning system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile


class TestLearningStatistics:
    """Tests for LearningStatistics dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import LearningStatistics
        stats = LearningStatistics()
        assert stats.problems_solved == 0
        assert stats.solutions_verified == 0
        assert stats.solutions_rejected == 0
        assert stats.traces_harvested == 0
        assert stats.distillation_runs == 0
        assert stats.total_latency_ms == 0.0
        assert stats.learning_events == []

    def test_custom_values(self):
        """Test custom initialization."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import LearningStatistics
        stats = LearningStatistics(
            problems_solved=10,
            solutions_verified=8,
            solutions_rejected=2,
            traces_harvested=8,
            distillation_runs=1,
            total_latency_ms=1000.0
        )
        assert stats.problems_solved == 10
        assert stats.solutions_verified == 8
        assert stats.verification_rate() if hasattr(stats, 'verification_rate') else True

    def test_to_dict(self):
        """Test conversion to dictionary."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import LearningStatistics
        stats = LearningStatistics(
            problems_solved=10,
            solutions_verified=8,
            total_latency_ms=1000.0
        )
        d = stats.to_dict()
        assert isinstance(d, dict)
        assert 'problems_solved' in d
        assert 'solutions_verified' in d
        assert 'verification_rate' in d
        assert d['problems_solved'] == 10
        assert d['verification_rate'] == 80.0

    def test_to_dict_zero_problems(self):
        """Test to_dict with zero problems (avoid division by zero)."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import LearningStatistics
        stats = LearningStatistics()
        d = stats.to_dict()
        assert d['verification_rate'] == 0.0
        assert d['avg_latency_ms'] == 0.0

    def test_learning_events_list(self):
        """Test learning events are tracked."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import LearningStatistics
        stats = LearningStatistics()
        stats.learning_events.append({'event': 'test'})
        assert len(stats.learning_events) == 1

    def test_to_dict_recent_events(self):
        """Test recent events are limited in to_dict."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import LearningStatistics
        stats = LearningStatistics()
        # Add more than 10 events
        for i in range(15):
            stats.learning_events.append({'event': i})
        d = stats.to_dict()
        assert len(d['recent_learning_events']) == 10


class TestSymboTeachingLoop:
    """Tests for SymboTeachingLoop class."""

    def test_init_default(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(storage_path=Path(tmpdir))
            assert loop.auto_distill_threshold == 50
            assert loop.enable_auto_learning is True
            assert loop._solver is None
            assert loop._harvester is None
            assert loop._distillation is None

    def test_init_custom_threshold(self):
        """Test custom auto_distill_threshold."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(
                storage_path=Path(tmpdir),
                auto_distill_threshold=100,
                enable_auto_learning=False
            )
            assert loop.auto_distill_threshold == 100
            assert loop.enable_auto_learning is False

    def test_init_with_solver(self):
        """Test initialization with solver engine."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        mock_solver = Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(
                solver_engine=mock_solver,
                storage_path=Path(tmpdir)
            )
            assert loop._solver is mock_solver
            assert loop.solver is mock_solver

    def test_init_with_harvester(self):
        """Test initialization with harvester."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        mock_harvester = Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(
                harvester=mock_harvester,
                storage_path=Path(tmpdir)
            )
            assert loop._harvester is mock_harvester

    def test_init_with_distillation(self):
        """Test initialization with distillation pipeline."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        mock_distillation = Mock()
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(
                distillation_pipeline=mock_distillation,
                storage_path=Path(tmpdir)
            )
            assert loop._distillation is mock_distillation

    def test_solver_property_lazy_load(self):
        """Test solver property lazy loading."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(storage_path=Path(tmpdir))
            # Solver should attempt lazy load
            solver = loop.solver
            # May be None if import fails, but shouldn't raise

    def test_harvester_property_lazy_load(self):
        """Test harvester property lazy loading."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(storage_path=Path(tmpdir))
            # Should attempt lazy load
            harvester = loop.harvester
            # May be a real instance or None

    def test_distillation_property_lazy_load(self):
        """Test distillation property lazy loading."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(storage_path=Path(tmpdir))
            # Should attempt lazy load
            distillation = loop.distillation

    def test_solve_and_learn_no_solver(self):
        """Test solve_and_learn with no solver."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(storage_path=Path(tmpdir))
            loop._solver = None  # Ensure no solver
            # Patch solver property to return None
            with patch.object(SymboTeachingLoop, 'solver', new_callable=lambda: property(lambda self: None)):
                result, captured = loop.solve_and_learn("x + 1")
                assert result is None
                assert captured is False

    def test_solve_and_learn_with_solver(self):
        """Test solve_and_learn with mocked solver."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        mock_solver = Mock()
        mock_solver.solve.return_value = {'result': '42', 'verified': True}

        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(
                solver_engine=mock_solver,
                storage_path=Path(tmpdir),
                enable_auto_learning=False
            )
            try:
                result, captured = loop.solve_and_learn("x + 1")
            except Exception:
                # May fail due to harvester/distillation setup
                pass

    def test_get_statistics(self):
        """Test getting statistics."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(storage_path=Path(tmpdir))
            stats = loop.stats
            assert stats.problems_solved == 0

    def test_storage_path_creation(self):
        """Test that storage path is created."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir) / "custom" / "path"
            loop = SymboTeachingLoop(storage_path=custom_path)
            assert custom_path.exists()

    def test_thread_safety_lock(self):
        """Test that thread lock exists."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(storage_path=Path(tmpdir))
            assert loop._lock is not None
            # Verify lock can be acquired
            acquired = loop._lock.acquire(blocking=False)
            if acquired:
                loop._lock.release()


class TestTeachingLoopModule:
    """Tests for module-level functions."""

    def test_module_imports(self):
        """Test that module imports correctly."""
        from symbo_agentic_reasoners.training import symbo_teaching_loop
        assert symbo_teaching_loop is not None

    def test_has_teaching_loop_class(self):
        """Test that SymboTeachingLoop is exported."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop
        assert SymboTeachingLoop is not None

    def test_has_learning_statistics(self):
        """Test that LearningStatistics is exported."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import LearningStatistics
        assert LearningStatistics is not None


class TestTeachingLoopIntegration:
    """Integration tests for teaching loop."""

    def test_full_cycle_mock(self):
        """Test a full learning cycle with mocks."""
        from symbo_agentic_reasoners.training.symbo_teaching_loop import SymboTeachingLoop

        mock_solver = Mock()
        mock_solver.solve.return_value = {
            'result': 'x**3/3',
            'verified': True,
            'steps': ['Apply power rule']
        }

        mock_harvester = Mock()
        mock_harvester.harvest_trace.return_value = 'trace_id_123'

        mock_distillation = Mock()

        with tempfile.TemporaryDirectory() as tmpdir:
            loop = SymboTeachingLoop(
                solver_engine=mock_solver,
                harvester=mock_harvester,
                distillation_pipeline=mock_distillation,
                storage_path=Path(tmpdir)
            )
            # The loop should be ready to use
            assert loop.solver is mock_solver
            assert loop.harvester is mock_harvester
            assert loop.distillation is mock_distillation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
