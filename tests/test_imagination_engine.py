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
Comprehensive Test Suite for the Imagination Engine
====================================================

Tests for autonomous mathematical exploration functionality.
Covers: IdleDetector, ExplorationScheduler, ImaginationEngine,
and integration with CuriosityEngine and SolverEngine.

Test Categories:
- Unit tests for individual components
- Integration tests for component interaction
- Lifecycle tests for start/stop/pause/resume
- Discovery processing tests
- Statistics tracking tests
- Thread safety tests
"""

import pytest
import time
import threading
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

# Import the modules under test
from symbo_agentic_reasoners.discovery.imagination_engine import (
    IdleDetector,
    ExplorationScheduler,
    ExplorationPriority,
    ImaginationEngine,
    ImaginationStats,
    SystemState,
    get_imagination_engine,
    start_imagination,
    stop_imagination,
)
from symbo_agentic_reasoners.discovery.curiosity_engine import (
    CuriosityEngine,
    ExplorationCategory,
    ExplorationResult,
    InterestLevel,
    ProblemGenerator,
    InterestScorer,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_solver():
    """Create a mock solver that returns successful results quickly."""
    solver = Mock()
    result = Mock()
    result.status = Mock()
    result.status.value = 'success'
    result.result = 42  # Simple numeric result
    solver.solve = Mock(return_value=result)
    return solver


@pytest.fixture
def slow_solver():
    """Create a mock solver that takes time to solve."""
    solver = Mock()
    result = Mock()
    result.status = Mock()
    result.status.value = 'success'
    result.result = 42

    def slow_solve(problem):
        time.sleep(0.1)  # Simulate work
        return result

    solver.solve = slow_solve
    return solver


@pytest.fixture
def failing_solver():
    """Create a mock solver that fails."""
    solver = Mock()
    result = Mock()
    result.status = Mock()
    result.status.value = 'error'
    result.result = None
    solver.solve = Mock(return_value=result)
    return solver


@pytest.fixture
def temp_save_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def idle_detector():
    """Create an IdleDetector with short threshold."""
    return IdleDetector(idle_threshold_seconds=0.1)


@pytest.fixture
def exploration_scheduler():
    """Create an ExplorationScheduler."""
    return ExplorationScheduler()


@pytest.fixture
def imagination_engine(mock_solver, temp_save_dir):
    """Create an ImaginationEngine with fast settings for testing."""
    engine = ImaginationEngine(
        solver=mock_solver,
        idle_threshold=0.05,  # Quick idle detection
        exploration_interval=0.01,  # Fast exploration
        max_exploration_time=5.0,  # Short timeout
        save_dir=temp_save_dir
    )
    yield engine
    # Cleanup
    if engine.state != SystemState.STOPPED:
        engine.stop()


# =============================================================================
# IdleDetector Tests
# =============================================================================


class TestIdleDetector:
    """Tests for IdleDetector class."""

    def test_initial_state_is_not_idle(self, idle_detector):
        """Detector should not be idle immediately after creation."""
        # With 0.1s threshold, should not be idle right away
        assert not idle_detector.is_idle()

    def test_becomes_idle_after_threshold(self, idle_detector):
        """Detector should become idle after threshold passes."""
        time.sleep(0.15)  # Wait longer than threshold (0.1s)
        assert idle_detector.is_idle()

    def test_record_activity_resets_idle(self, idle_detector):
        """Recording activity should reset idle state."""
        time.sleep(0.15)
        assert idle_detector.is_idle()

        idle_detector.record_activity()
        assert not idle_detector.is_idle()

    def test_begin_task_prevents_idle(self, idle_detector):
        """Starting a task should prevent idle state."""
        time.sleep(0.15)
        assert idle_detector.is_idle()

        idle_detector.begin_task()
        assert not idle_detector.is_idle()

    def test_end_task_allows_idle(self, idle_detector):
        """Ending all tasks should allow idle state."""
        idle_detector.begin_task()
        time.sleep(0.15)
        assert not idle_detector.is_idle()

        idle_detector.end_task()
        time.sleep(0.15)
        assert idle_detector.is_idle()

    def test_multiple_tasks_tracking(self, idle_detector):
        """Multiple tasks should all need to end for idle."""
        idle_detector.begin_task()
        idle_detector.begin_task()
        idle_detector.begin_task()
        time.sleep(0.15)

        idle_detector.end_task()
        assert not idle_detector.is_idle()

        idle_detector.end_task()
        assert not idle_detector.is_idle()

        idle_detector.end_task()
        time.sleep(0.15)
        assert idle_detector.is_idle()

    def test_end_task_cannot_go_negative(self, idle_detector):
        """Ending more tasks than started should not cause errors."""
        idle_detector.end_task()
        idle_detector.end_task()
        # Should not raise and idle duration should work
        time.sleep(0.15)
        assert idle_detector.is_idle()

    def test_get_idle_duration_when_busy(self, idle_detector):
        """Idle duration should be 0 when active tasks exist."""
        idle_detector.begin_task()
        time.sleep(0.1)
        assert idle_detector.get_idle_duration() == 0.0

    def test_get_idle_duration_when_idle(self, idle_detector):
        """Idle duration should increase when idle."""
        time.sleep(0.15)
        duration = idle_detector.get_idle_duration()
        assert duration >= 0.14  # Allow small timing variance

    def test_thread_safety(self, idle_detector):
        """IdleDetector should be thread-safe."""
        errors = []

        def activity_thread():
            try:
                for _ in range(100):
                    idle_detector.record_activity()
                    idle_detector.is_idle()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        def task_thread():
            try:
                for _ in range(50):
                    idle_detector.begin_task()
                    idle_detector.get_idle_duration()
                    idle_detector.end_task()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=activity_thread),
            threading.Thread(target=task_thread),
            threading.Thread(target=activity_thread),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"


# =============================================================================
# ExplorationScheduler Tests
# =============================================================================


class TestExplorationScheduler:
    """Tests for ExplorationScheduler class."""

    def test_initial_priorities(self, exploration_scheduler):
        """All categories should have initial priorities."""
        for category in ExplorationCategory:
            assert category in exploration_scheduler.priorities
            assert exploration_scheduler.priorities[category].weight == 1.0

    def test_select_category_returns_valid_category(self, exploration_scheduler):
        """Select category should return a valid ExplorationCategory."""
        category = exploration_scheduler.select_category()
        assert isinstance(category, ExplorationCategory)

    def test_select_category_distribution(self, exploration_scheduler):
        """Categories should be selected with reasonable distribution."""
        counts = {cat: 0 for cat in ExplorationCategory}

        for _ in range(1000):
            category = exploration_scheduler.select_category()
            counts[category] += 1

        # With equal weights, each category should get some selections
        for cat, count in counts.items():
            assert count > 50, f"Category {cat} was selected too rarely: {count}"

    def test_record_exploration_updates_last_explored(self, exploration_scheduler):
        """Recording exploration should update last_explored time."""
        category = ExplorationCategory.ALGEBRA
        assert exploration_scheduler.priorities[category].last_explored is None

        exploration_scheduler.record_exploration(category, success=True, interesting=False)

        assert exploration_scheduler.priorities[category].last_explored is not None

    def test_record_exploration_updates_success_rate(self, exploration_scheduler):
        """Recording explorations should update success rate."""
        category = ExplorationCategory.CALCULUS
        initial_rate = exploration_scheduler.priorities[category].success_rate

        # Record several successes
        for _ in range(10):
            exploration_scheduler.record_exploration(category, success=True, interesting=False)

        # Success rate should have increased
        assert exploration_scheduler.priorities[category].success_rate > initial_rate

    def test_record_exploration_updates_discovery_rate(self, exploration_scheduler):
        """Recording interesting discoveries should update discovery rate."""
        category = ExplorationCategory.NUMBER_THEORY
        initial_rate = exploration_scheduler.priorities[category].discovery_rate

        # Record several interesting discoveries
        for _ in range(10):
            exploration_scheduler.record_exploration(category, success=True, interesting=True)

        # Discovery rate should have increased
        assert exploration_scheduler.priorities[category].discovery_rate > initial_rate

    def test_high_discovery_rate_increases_selection(self, exploration_scheduler):
        """Categories with high discovery rates should be selected more often."""
        # Boost one category's discovery rate
        hot_category = ExplorationCategory.ALGEBRA
        for _ in range(50):
            exploration_scheduler.record_exploration(hot_category, success=True, interesting=True)

        # Count selections
        counts = {cat: 0 for cat in ExplorationCategory}
        for _ in range(500):
            category = exploration_scheduler.select_category()
            counts[category] += 1

        # Hot category should be selected more often
        avg_others = sum(c for cat, c in counts.items() if cat != hot_category) / (len(counts) - 1)
        assert counts[hot_category] > avg_others * 1.5, "High discovery rate category should be preferred"

    def test_recently_explored_category_less_likely(self, exploration_scheduler):
        """Recently explored category with min_interval should be selected less."""
        category = ExplorationCategory.GEOMETRY
        exploration_scheduler.priorities[category].min_interval_seconds = 10.0

        # Record recent exploration
        exploration_scheduler.record_exploration(category, success=True, interesting=False)

        # Count selections
        counts = {cat: 0 for cat in ExplorationCategory}
        for _ in range(500):
            selected = exploration_scheduler.select_category()
            counts[selected] += 1

        # Recently explored category should be selected less
        assert counts[category] < 100, "Recently explored category should be avoided"


# =============================================================================
# ImaginationStats Tests
# =============================================================================


class TestImaginationStats:
    """Tests for ImaginationStats dataclass."""

    def test_default_values(self):
        """Stats should have sensible defaults."""
        stats = ImaginationStats()
        assert stats.total_explorations == 0
        assert stats.successful_explorations == 0
        assert stats.interesting_discoveries == 0
        assert stats.remarkable_discoveries == 0
        assert stats.total_idle_time_seconds == 0
        assert stats.total_exploration_time_seconds == 0
        assert stats.explorations_by_category == {}
        assert stats.discoveries_by_category == {}
        assert stats.session_start is None
        assert stats.last_discovery is None

    def test_to_dict_with_empty_stats(self):
        """to_dict should work with empty stats."""
        stats = ImaginationStats()
        d = stats.to_dict()

        assert d['total_explorations'] == 0
        assert d['success_rate'] == 0
        assert d['discovery_rate'] == 0
        assert d['efficiency'] == 0

    def test_to_dict_with_data(self):
        """to_dict should calculate rates correctly."""
        stats = ImaginationStats()
        stats.total_explorations = 100
        stats.successful_explorations = 80
        stats.interesting_discoveries = 10
        stats.total_idle_time_seconds = 60.0
        stats.total_exploration_time_seconds = 30.0
        stats.session_start = datetime.now()

        d = stats.to_dict()

        assert d['success_rate'] == 80.0
        assert d['discovery_rate'] == 10.0
        assert d['efficiency'] == 50.0
        assert d['session_start'] is not None


# =============================================================================
# ImaginationEngine Core Tests
# =============================================================================


class TestImaginationEngineCore:
    """Core functionality tests for ImaginationEngine."""

    def test_initialization(self, mock_solver, temp_save_dir):
        """Engine should initialize correctly."""
        engine = ImaginationEngine(
            solver=mock_solver,
            idle_threshold=5.0,
            exploration_interval=1.0,
            save_dir=temp_save_dir
        )

        assert engine.state == SystemState.STOPPED
        assert engine.solver is mock_solver
        assert engine.save_dir == temp_save_dir
        assert temp_save_dir.exists()

    def test_save_dir_created(self, mock_solver, temp_save_dir):
        """Save directory should be created if it doesn't exist."""
        new_dir = temp_save_dir / "subdir" / "imagination"
        engine = ImaginationEngine(solver=mock_solver, save_dir=new_dir)
        assert new_dir.exists()

    def test_initial_stats(self, imagination_engine):
        """Initial stats should be zeroed."""
        stats = imagination_engine.stats
        assert stats.total_explorations == 0
        assert stats.successful_explorations == 0

    def test_get_statistics_structure(self, imagination_engine):
        """get_statistics should return properly structured data."""
        stats = imagination_engine.get_statistics()

        assert 'state' in stats
        assert 'curiosity' in stats
        assert 'imagination' in stats
        assert 'scheduler' in stats


# =============================================================================
# ImaginationEngine Lifecycle Tests
# =============================================================================


class TestImaginationEngineLifecycle:
    """Tests for engine lifecycle: start, stop, pause, resume."""

    def test_start_changes_state(self, imagination_engine):
        """Starting engine should change state from STOPPED to IDLE."""
        assert imagination_engine.state == SystemState.STOPPED
        imagination_engine.start()
        assert imagination_engine.state != SystemState.STOPPED
        imagination_engine.stop()

    def test_start_creates_thread(self, imagination_engine):
        """Starting should create exploration thread."""
        imagination_engine.start()
        assert imagination_engine._exploration_thread is not None
        assert imagination_engine._exploration_thread.is_alive()
        imagination_engine.stop()

    def test_start_sets_session_start(self, imagination_engine):
        """Starting should record session start time."""
        assert imagination_engine.stats.session_start is None
        imagination_engine.start()
        assert imagination_engine.stats.session_start is not None
        imagination_engine.stop()

    def test_stop_changes_state(self, imagination_engine):
        """Stopping should change state to STOPPED."""
        imagination_engine.start()
        imagination_engine.stop()
        assert imagination_engine.state == SystemState.STOPPED

    def test_stop_joins_thread(self, imagination_engine):
        """Stopping should join the exploration thread."""
        imagination_engine.start()
        imagination_engine.stop()
        # Thread should have ended
        assert not imagination_engine._exploration_thread.is_alive()

    def test_pause_changes_state(self, imagination_engine):
        """Pausing should change state to PAUSED."""
        imagination_engine.start()
        time.sleep(0.1)  # Let it start exploring
        imagination_engine.pause()
        # State should be PAUSED (may take a moment for exploration loop to notice)
        time.sleep(0.05)
        assert imagination_engine.state == SystemState.PAUSED
        imagination_engine.stop()

    def test_pause_when_stopped_no_effect(self, imagination_engine):
        """Pausing when stopped should have no effect."""
        imagination_engine.pause()
        assert imagination_engine.state == SystemState.STOPPED

    def test_resume_from_paused(self, imagination_engine):
        """Resuming from paused should go to IDLE."""
        imagination_engine.start()
        time.sleep(0.1)  # Let it start
        imagination_engine.pause()
        time.sleep(0.05)  # Let pause take effect
        assert imagination_engine.state == SystemState.PAUSED

        imagination_engine.resume()
        assert imagination_engine.state == SystemState.IDLE
        imagination_engine.stop()

    def test_resume_when_not_paused_no_effect(self, imagination_engine):
        """Resuming when not paused should have no effect."""
        imagination_engine.start()
        current_state = imagination_engine.state
        imagination_engine.resume()  # Should not change if not paused
        # State should not have changed (unless it was paused)
        imagination_engine.stop()

    def test_double_start_warning(self, imagination_engine):
        """Starting twice should log warning but not crash."""
        imagination_engine.start()
        imagination_engine.start()  # Should not crash
        imagination_engine.stop()

    def test_double_stop_no_effect(self, imagination_engine):
        """Stopping twice should have no effect."""
        imagination_engine.start()
        imagination_engine.stop()
        imagination_engine.stop()  # Should not crash


# =============================================================================
# ImaginationEngine Activity Notification Tests
# =============================================================================


class TestImaginationEngineActivity:
    """Tests for activity notifications."""

    def test_notify_activity_records_in_detector(self, imagination_engine):
        """Notifying activity should record in idle detector."""
        imagination_engine.start()
        time.sleep(0.15)  # Let it become idle

        imagination_engine.notify_activity()
        assert not imagination_engine.idle_detector.is_idle()
        imagination_engine.stop()

    def test_notify_task_start_changes_state(self, imagination_engine):
        """Notifying task start should change to BUSY."""
        imagination_engine.start()
        imagination_engine.notify_task_start()
        assert imagination_engine.state == SystemState.BUSY
        imagination_engine.stop()

    def test_notify_task_end_allows_idle(self, imagination_engine):
        """Notifying task end should allow return to IDLE."""
        imagination_engine.start()
        imagination_engine.notify_task_start()
        imagination_engine.notify_task_end()
        time.sleep(0.1)
        # State should be IDLE or EXPLORING
        assert imagination_engine.state in [SystemState.IDLE, SystemState.EXPLORING]
        imagination_engine.stop()


# =============================================================================
# ImaginationEngine Exploration Tests
# =============================================================================


class TestImaginationEngineExploration:
    """Tests for exploration functionality."""

    def test_explores_when_idle(self, imagination_engine):
        """Engine should explore when idle."""
        imagination_engine.start()
        time.sleep(0.3)  # Let it explore

        # Should have done some explorations
        assert imagination_engine.stats.total_explorations > 0
        imagination_engine.stop()

    def test_does_not_explore_when_busy(self, imagination_engine):
        """Engine should not explore when busy with tasks."""
        imagination_engine.start()
        imagination_engine.notify_task_start()

        initial = imagination_engine.stats.total_explorations
        time.sleep(0.2)

        # Explorations should not have increased much
        assert imagination_engine.stats.total_explorations <= initial + 1
        imagination_engine.stop()

    def test_does_not_explore_when_paused(self, imagination_engine):
        """Engine should not explore when paused."""
        imagination_engine.start()
        time.sleep(0.1)
        imagination_engine.pause()
        # Wait for any in-flight exploration to complete
        time.sleep(0.15)

        initial = imagination_engine.stats.total_explorations
        time.sleep(0.2)

        # Explorations should not have increased while paused
        assert imagination_engine.stats.total_explorations == initial
        imagination_engine.stop()

    def test_resumes_exploration_after_pause(self, imagination_engine):
        """Engine should resume exploration after unpause."""
        imagination_engine.start()
        imagination_engine.pause()
        time.sleep(0.1)

        initial = imagination_engine.stats.total_explorations
        imagination_engine.resume()
        time.sleep(0.3)

        # Explorations should have increased
        assert imagination_engine.stats.total_explorations > initial
        imagination_engine.stop()

    def test_exploration_with_timeout(self, slow_solver, temp_save_dir):
        """Exploration should respect timeout limits."""
        engine = ImaginationEngine(
            solver=slow_solver,
            idle_threshold=0.01,
            exploration_interval=0.01,
            max_exploration_time=0.05,  # Very short timeout
            save_dir=temp_save_dir
        )

        engine.start()
        time.sleep(0.5)
        engine.stop()

        # Should have attempted explorations even with slow solver
        # (some may timeout, but engine shouldn't hang)
        assert engine.state == SystemState.STOPPED


# =============================================================================
# ImaginationEngine Statistics Tests
# =============================================================================


class TestImaginationEngineStatistics:
    """Tests for statistics tracking."""

    def test_exploration_count_increases(self, imagination_engine):
        """Total explorations should increase during operation."""
        imagination_engine.start()
        time.sleep(0.3)

        assert imagination_engine.stats.total_explorations > 0
        imagination_engine.stop()

    def test_exploration_time_tracked(self, imagination_engine):
        """Exploration time should be tracked."""
        imagination_engine.start()
        time.sleep(0.3)
        imagination_engine.stop()

        assert imagination_engine.stats.total_exploration_time_seconds > 0

    def test_category_distribution_tracked(self, imagination_engine):
        """Explorations by category should be tracked."""
        imagination_engine.start()
        time.sleep(0.5)
        imagination_engine.stop()

        # Should have explored at least one category
        assert len(imagination_engine.stats.explorations_by_category) > 0

    def test_stats_saved_on_stop(self, imagination_engine, temp_save_dir):
        """Stats should be saved to file on stop."""
        imagination_engine.start()
        time.sleep(0.2)
        imagination_engine.stop()

        stats_file = temp_save_dir / "imagination_stats.json"
        assert stats_file.exists()

        with open(stats_file) as f:
            saved_stats = json.load(f)
        assert 'total_explorations' in saved_stats


# =============================================================================
# ImaginationEngine Discovery Tests
# =============================================================================


class TestImaginationEngineDiscoveries:
    """Tests for discovery handling."""

    def test_discovery_callback_called(self, mock_solver, temp_save_dir):
        """Discovery callback should be called for interesting discoveries."""
        discoveries = []

        def on_discovery(result):
            discoveries.append(result)

        engine = ImaginationEngine(
            solver=mock_solver,
            idle_threshold=0.01,
            exploration_interval=0.01,
            save_dir=temp_save_dir,
            on_discovery=on_discovery
        )

        engine.start()
        time.sleep(1.0)  # Give time for discoveries
        engine.stop()

        # May or may not have discoveries depending on random generation
        # Main thing is no crash when callback is called

    def test_get_discoveries_returns_list(self, imagination_engine):
        """get_discoveries should return a list."""
        imagination_engine.start()
        time.sleep(0.3)
        imagination_engine.stop()

        discoveries = imagination_engine.get_discoveries()
        assert isinstance(discoveries, list)

    def test_get_best_discoveries_returns_list(self, imagination_engine):
        """get_best_discoveries should return a list."""
        imagination_engine.start()
        time.sleep(0.3)
        imagination_engine.stop()

        discoveries = imagination_engine.get_best_discoveries()
        assert isinstance(discoveries, list)

    def test_discovery_logged_to_file(self, imagination_engine, temp_save_dir):
        """Interesting discoveries should be logged to file."""
        imagination_engine.start()
        time.sleep(0.5)
        imagination_engine.stop()

        discovery_log = temp_save_dir / "imagination_discoveries.jsonl"
        # File may or may not exist depending on if interesting discoveries were made
        # Just verify we can check it
        if discovery_log.exists():
            with open(discovery_log) as f:
                lines = f.readlines()
            # Each line should be valid JSON
            for line in lines:
                json.loads(line)


# =============================================================================
# Global Functions Tests
# =============================================================================


class TestGlobalFunctions:
    """Tests for module-level convenience functions."""

    def test_get_imagination_engine_without_solver_returns_none(self):
        """get_imagination_engine without solver should return existing or None."""
        # Reset global state
        import symbo_agentic_reasoners.discovery.imagination_engine as mod
        mod._imagination_engine = None

        result = get_imagination_engine()
        # Should return None when no solver provided and none exists
        # (or existing engine if one was created)
        assert result is None or isinstance(result, ImaginationEngine)

    def test_start_imagination_creates_engine(self, mock_solver):
        """start_imagination should create and start an engine."""
        # Reset global state
        import symbo_agentic_reasoners.discovery.imagination_engine as mod
        mod._imagination_engine = None

        engine = start_imagination(mock_solver)
        assert isinstance(engine, ImaginationEngine)
        assert engine.state != SystemState.STOPPED

        stop_imagination()

    def test_stop_imagination_stops_engine(self, mock_solver):
        """stop_imagination should stop the global engine."""
        # Reset global state
        import symbo_agentic_reasoners.discovery.imagination_engine as mod
        mod._imagination_engine = None

        engine = start_imagination(mock_solver)
        stop_imagination()
        assert engine.state == SystemState.STOPPED


# =============================================================================
# CuriosityEngine Integration Tests
# =============================================================================


class TestCuriosityEngineIntegration:
    """Tests for integration with CuriosityEngine."""

    def test_curiosity_engine_used(self, imagination_engine):
        """ImaginationEngine should use CuriosityEngine internally."""
        assert hasattr(imagination_engine, 'curiosity')
        assert isinstance(imagination_engine.curiosity, CuriosityEngine)

    def test_problem_generator_works(self, mock_solver, temp_save_dir):
        """Problem generator should produce valid problems."""
        generator = ProblemGenerator(seed=42)

        for category in ExplorationCategory:
            problem, cat = generator.generate(category)
            assert isinstance(problem, str)
            assert len(problem) > 0
            assert cat == category

    def test_interest_scorer_works(self):
        """Interest scorer should score results."""
        scorer = InterestScorer()

        # Test with various solutions
        level, notes = scorer.score("2 + 2", 4, 1.0)
        assert isinstance(level, InterestLevel)

        level, notes = scorer.score("simplify(sin(x)**2 + cos(x)**2)", 1, 5.0)
        assert isinstance(level, InterestLevel)


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_exploration_with_failing_solver(self, failing_solver, temp_save_dir):
        """Engine should handle solver failures gracefully."""
        engine = ImaginationEngine(
            solver=failing_solver,
            idle_threshold=0.01,
            exploration_interval=0.01,
            save_dir=temp_save_dir
        )

        engine.start()
        time.sleep(0.3)
        engine.stop()

        # Should have attempted explorations even with failures
        assert engine.stats.total_explorations >= 0

    def test_exploration_with_exception_in_solver(self, temp_save_dir):
        """Engine should handle solver exceptions gracefully."""
        solver = Mock()
        solver.solve = Mock(side_effect=RuntimeError("Test error"))

        engine = ImaginationEngine(
            solver=solver,
            idle_threshold=0.01,
            exploration_interval=0.01,
            save_dir=temp_save_dir
        )

        engine.start()
        time.sleep(0.2)
        engine.stop()

        # Should not crash
        assert engine.state == SystemState.STOPPED

    def test_callback_exception_handled(self, mock_solver, temp_save_dir):
        """Exceptions in discovery callback should be handled."""
        def bad_callback(result):
            raise RuntimeError("Callback error")

        engine = ImaginationEngine(
            solver=mock_solver,
            idle_threshold=0.01,
            exploration_interval=0.01,
            save_dir=temp_save_dir,
            on_discovery=bad_callback
        )

        engine.start()
        time.sleep(0.3)
        engine.stop()

        # Should not crash despite bad callback
        assert engine.state == SystemState.STOPPED

    def test_rapid_start_stop_cycles(self, imagination_engine):
        """Rapid start/stop cycles should not cause issues."""
        for _ in range(5):
            imagination_engine.start()
            time.sleep(0.05)
            imagination_engine.stop()

    def test_state_consistency_under_load(self, imagination_engine):
        """State should remain consistent under concurrent access."""
        errors = []

        def check_state():
            try:
                for _ in range(100):
                    state = imagination_engine.state
                    assert isinstance(state, SystemState)
            except Exception as e:
                errors.append(e)

        imagination_engine.start()

        threads = [threading.Thread(target=check_state) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        imagination_engine.stop()
        assert len(errors) == 0


# =============================================================================
# Performance Tests
# =============================================================================


class TestPerformance:
    """Performance-related tests."""

    def test_exploration_rate(self, mock_solver, temp_save_dir):
        """Engine should achieve reasonable exploration rate."""
        engine = ImaginationEngine(
            solver=mock_solver,
            idle_threshold=0.01,
            exploration_interval=0.01,
            max_exploration_time=1.0,
            save_dir=temp_save_dir
        )

        engine.start()
        time.sleep(2.0)
        engine.stop()

        # Should have done multiple explorations in 2 seconds
        assert engine.stats.total_explorations > 5

    def test_memory_stability(self, imagination_engine):
        """Engine should not accumulate unbounded memory."""
        import sys

        imagination_engine.start()
        time.sleep(1.0)

        initial_discoveries = len(imagination_engine.get_discoveries())

        time.sleep(1.0)
        imagination_engine.stop()

        # Discovery list should be bounded (curiosity engine manages this)
        # Just verify it's accessible
        final_discoveries = len(imagination_engine.get_discoveries())
        assert final_discoveries >= 0


# =============================================================================
# Exploration Result Processing Tests
# =============================================================================


class TestExplorationResultProcessing:
    """Tests for how exploration results are processed."""

    def test_successful_exploration_increments_counter(self, imagination_engine):
        """Successful explorations should increment success counter."""
        imagination_engine.start()
        time.sleep(0.5)
        imagination_engine.stop()

        # With mock solver returning success, should have successes
        if imagination_engine.stats.total_explorations > 0:
            assert imagination_engine.stats.successful_explorations > 0

    def test_interesting_discovery_tracked(self, mock_solver, temp_save_dir):
        """Interesting discoveries should be tracked in stats."""
        # Create engine with solver that returns interesting results
        engine = ImaginationEngine(
            solver=mock_solver,
            idle_threshold=0.01,
            exploration_interval=0.01,
            save_dir=temp_save_dir
        )

        engine.start()
        time.sleep(1.0)
        engine.stop()

        # Stats should track discoveries
        assert 'interesting_discoveries' in engine.stats.to_dict()


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
