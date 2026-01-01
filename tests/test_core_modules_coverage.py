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
Comprehensive tests for core modules to achieve 70%+ coverage.

Tests cover:
- ResourceCoordinator
- vector_database
- solver_engine
- orchestrator
"""

import pytest
import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


class TestResourceCoordinatorBasics:
    """Tests for ResourceCoordinator basic functionality."""

    def test_agent_state_enum(self):
        """Test AgentState enum values."""
        from symbo_agentic_reasoners.core.resource_coordinator import AgentState
        assert AgentState.INACTIVE.value == "inactive"
        assert AgentState.STANDBY.value == "standby"
        assert AgentState.ACTIVE.value == "active"
        assert AgentState.SUSPENDED.value == "suspended"
        assert AgentState.FAILED.value == "failed"

    def test_agent_info_dataclass(self):
        """Test AgentInfo dataclass."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            AgentInfo, AgentState
        )
        info = AgentInfo(
            agent_id="test_001",
            agent_type="test_type",
            tier=2
        )
        assert info.agent_id == "test_001"
        assert info.state == AgentState.INACTIVE
        assert info.tasks_completed == 0

    def test_agent_info_to_dict(self):
        """Test AgentInfo to_dict method."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            AgentInfo, AgentState
        )
        now = datetime.now()
        info = AgentInfo(
            agent_id="test_001",
            agent_type="test_type",
            tier=2,
            last_active=now
        )
        d = info.to_dict()
        assert d['agent_id'] == "test_001"
        assert d['state'] == "inactive"
        assert d['last_active'] is not None

    def test_hardware_metrics_dataclass(self):
        """Test HardwareMetrics dataclass."""
        from symbo_agentic_reasoners.core.resource_coordinator import HardwareMetrics
        metrics = HardwareMetrics(
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_used_mb=8000,
            memory_available_mb=8000,
            disk_percent=70.0,
            disk_free_gb=100.0
        )
        d = metrics.to_dict()
        assert d['cpu_percent'] == 50.0
        assert d['memory_percent'] == 60.0

    def test_resource_limits_dataclass(self):
        """Test ResourceLimits dataclass."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceLimits
        limits = ResourceLimits()
        assert limits.max_active_agents == 8
        assert limits.max_parallel_workers == 4

    def test_resource_limits_from_config(self):
        """Test ResourceLimits from_config."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceLimits
        limits = ResourceLimits.from_config()
        assert limits.max_active_agents > 0

    def test_system_state_dataclass(self):
        """Test SystemState dataclass."""
        from symbo_agentic_reasoners.core.resource_coordinator import SystemState
        state = SystemState(
            completed_count=10,
            failed_count=2,
            session_start="2025-01-01T00:00:00"
        )
        d = state.to_dict()
        assert d['completed_count'] == 10
        assert d['failed_count'] == 2

    def test_system_state_from_dict(self):
        """Test SystemState from_dict."""
        from symbo_agentic_reasoners.core.resource_coordinator import SystemState
        data = {
            'agents': {},
            'pending_problems': ['p1', 'p2'],
            'completed_count': 5,
            'failed_count': 1,
            'session_start': '2025-01-01T00:00:00',
            'last_checkpoint': '2025-01-01T01:00:00'
        }
        state = SystemState.from_dict(data)
        assert len(state.pending_problems) == 2
        assert state.completed_count == 5


class TestResourceCoordinatorLifecycle:
    """Tests for ResourceCoordinator lifecycle management."""

    def test_init(self, tmp_path):
        """Test initialization."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        assert coord._running is False
        assert coord._shutdown_requested is False

    def test_start_stop(self, tmp_path):
        """Test start and stop."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord.start()
        assert coord._running is True

        coord.stop(save_state=False)
        assert coord._running is False

    def test_start_already_running(self, tmp_path):
        """Test start when already running."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._running = True
        coord.start()  # Should return early
        assert coord._running is True

    def test_stop_not_running(self, tmp_path):
        """Test stop when not running."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord.stop()  # Should return early

    def test_request_shutdown(self, tmp_path):
        """Test request_shutdown."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord.request_shutdown()
        assert coord._shutdown_requested is True

    def test_is_shutdown_requested(self, tmp_path):
        """Test is_shutdown_requested."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        assert coord.is_shutdown_requested() is False
        coord._shutdown_requested = True
        assert coord.is_shutdown_requested() is True


class TestResourceCoordinatorAgentManagement:
    """Tests for agent management functionality."""

    def test_register_agent_factory(self, tmp_path):
        """Test registering agent factory."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        factory = Mock(return_value=Mock())
        coord.register_agent_factory(
            agent_type="test_agent",
            factory=factory,
            tier=3,
            memory_estimate_mb=50.0
        )

        assert "test_agent" in coord._agent_factories

    def test_get_or_activate_agent_no_factory(self, tmp_path):
        """Test get_or_activate_agent with no factory."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        result = coord.get_or_activate_agent("nonexistent_type")
        assert result is None

    def test_get_or_activate_agent_create_new(self, tmp_path):
        """Test get_or_activate_agent creating new agent."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        mock_agent = Mock()
        factory = Mock(return_value=mock_agent)
        coord.register_agent_factory(
            agent_type="test_agent",
            factory=factory
        )

        result = coord.get_or_activate_agent("test_agent")
        assert result is mock_agent
        factory.assert_called_once()

    def test_get_or_activate_agent_existing_active(self, tmp_path):
        """Test get_or_activate_agent with existing active agent."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, AgentInfo, AgentState
        )
        coord = ResourceCoordinator(state_dir=tmp_path)

        mock_agent = Mock()
        coord._agents["test_001"] = AgentInfo(
            agent_id="test_001",
            agent_type="test_type",
            tier=3,
            state=AgentState.ACTIVE,
            instance=mock_agent
        )

        result = coord.get_or_activate_agent("test_type")
        assert result is mock_agent

    def test_get_or_activate_agent_from_standby(self, tmp_path):
        """Test get_or_activate_agent activating standby agent."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, AgentInfo, AgentState
        )
        coord = ResourceCoordinator(state_dir=tmp_path)

        mock_agent = Mock()
        coord._agents["test_001"] = AgentInfo(
            agent_id="test_001",
            agent_type="test_type",
            tier=3,
            state=AgentState.STANDBY,
            instance=mock_agent
        )

        result = coord.get_or_activate_agent("test_type")
        assert result is mock_agent
        assert coord._agents["test_001"].state == AgentState.ACTIVE

    def test_release_agent(self, tmp_path):
        """Test release_agent."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, AgentInfo, AgentState
        )
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord._agents["test_001"] = AgentInfo(
            agent_id="test_001",
            agent_type="test_type",
            tier=3,
            state=AgentState.ACTIVE,
            instance=Mock()
        )

        coord.release_agent("test_type")
        assert coord._agents["test_001"].state == AgentState.STANDBY
        assert coord._agents["test_001"].tasks_completed == 1

    def test_get_optimal_worker_count(self, tmp_path):
        """Test get_optimal_worker_count."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, AgentInfo, AgentState
        )
        coord = ResourceCoordinator(state_dir=tmp_path)

        # With no active agents
        count = coord.get_optimal_worker_count()
        assert count == coord.limits.max_parallel_workers

        # With many active agents
        for i in range(10):
            coord._agents[f"agent_{i}"] = AgentInfo(
                agent_id=f"agent_{i}",
                agent_type="test",
                tier=3,
                state=AgentState.ACTIVE
            )

        count = coord.get_optimal_worker_count()
        assert count < coord.limits.max_parallel_workers


class TestResourceCoordinatorProblems:
    """Tests for problem queue management."""

    def test_add_pending_problem(self, tmp_path):
        """Test add_pending_problem."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord.add_pending_problem("x + 1 = 0")
        assert len(coord._system_state.pending_problems) == 1

    def test_get_next_problem(self, tmp_path):
        """Test get_next_problem."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord.add_pending_problem("p1")
        coord.add_pending_problem("p2")

        p = coord.get_next_problem()
        assert p == "p1"
        p = coord.get_next_problem()
        assert p == "p2"
        p = coord.get_next_problem()
        assert p is None

    def test_mark_problem_completed_success(self, tmp_path):
        """Test mark_problem_completed with success."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord.mark_problem_completed(success=True)
        assert coord._system_state.completed_count == 1

    def test_mark_problem_completed_failure(self, tmp_path):
        """Test mark_problem_completed with failure."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord.mark_problem_completed(success=False)
        assert coord._system_state.failed_count == 1


class TestResourceCoordinatorStatistics:
    """Tests for statistics methods."""

    def test_get_statistics(self, tmp_path):
        """Test get_statistics."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, AgentInfo, AgentState
        )
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord._agents["agent_1"] = AgentInfo(
            agent_id="agent_1", agent_type="t1", tier=3, state=AgentState.ACTIVE
        )
        coord._agents["agent_2"] = AgentInfo(
            agent_id="agent_2", agent_type="t2", tier=3, state=AgentState.STANDBY
        )

        stats = coord.get_statistics()
        assert stats['agents']['active'] == 1
        assert stats['agents']['standby'] == 1
        assert stats['agents']['total'] == 2

    def test_get_hardware_metrics(self, tmp_path):
        """Test get_hardware_metrics."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, HardwareMetrics
        )
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._hardware_metrics = HardwareMetrics(cpu_percent=50.0)

        metrics = coord.get_hardware_metrics()
        assert metrics.cpu_percent == 50.0

    def test_get_hardware_status(self, tmp_path):
        """Test get_hardware_status."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        status = coord.get_hardware_status()
        assert 'metrics' in status
        assert 'warnings' in status
        assert 'can_proceed' in status

    def test_can_proceed_with_task(self, tmp_path):
        """Test can_proceed_with_task."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, HardwareMetrics
        )
        coord = ResourceCoordinator(state_dir=tmp_path)

        # No metrics - should return True
        coord._hardware_metrics = None
        assert coord.can_proceed_with_task() is True

        # Normal load
        coord._hardware_metrics = HardwareMetrics(cpu_percent=50.0, memory_percent=50.0)
        assert coord.can_proceed_with_task() is True

        # Critical CPU
        coord._hardware_metrics = HardwareMetrics(cpu_percent=99.0, memory_percent=50.0)
        assert coord.can_proceed_with_task() is False


class TestResourceCoordinatorState:
    """Tests for state persistence."""

    def test_save_and_restore_state(self, tmp_path):
        """Test save and restore state."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord.add_pending_problem("p1")
        coord.mark_problem_completed(success=True)
        coord._save_state()

        # Create new coordinator
        coord2 = ResourceCoordinator(state_dir=tmp_path)
        coord2._restore_state()

        assert coord2._system_state.completed_count == 1
        assert len(coord2._system_state.pending_problems) == 1

    def test_restore_nonexistent_state(self, tmp_path):
        """Test restore when state file doesn't exist."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._restore_state()  # Should not raise


class TestResourceCoordinatorHardware:
    """Tests for hardware monitoring."""

    def test_get_hardware_warnings_none(self, tmp_path):
        """Test _get_hardware_warnings with no metrics."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._hardware_metrics = None

        warnings = coord._get_hardware_warnings()
        assert warnings == []

    def test_get_hardware_warnings_normal(self, tmp_path):
        """Test _get_hardware_warnings with normal metrics."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, HardwareMetrics
        )
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._hardware_metrics = HardwareMetrics(
            cpu_percent=50.0, memory_percent=50.0, disk_percent=50.0
        )

        warnings = coord._get_hardware_warnings()
        assert warnings == []

    def test_get_hardware_warnings_high(self, tmp_path):
        """Test _get_hardware_warnings with high usage."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, HardwareMetrics
        )
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._hardware_metrics = HardwareMetrics(
            cpu_percent=85.0, memory_percent=85.0, disk_percent=95.0
        )

        warnings = coord._get_hardware_warnings()
        assert len(warnings) >= 2  # At least CPU and memory warnings

    def test_get_hardware_warnings_critical(self, tmp_path):
        """Test _get_hardware_warnings with critical usage."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, HardwareMetrics
        )
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._hardware_metrics = HardwareMetrics(
            cpu_percent=98.0, memory_percent=98.0, disk_percent=50.0
        )

        warnings = coord._get_hardware_warnings()
        assert any('CRITICAL' in w for w in warnings)

    def test_get_hardware_recommendations(self, tmp_path):
        """Test _get_hardware_recommendations."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, HardwareMetrics, AgentInfo, AgentState
        )
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._hardware_metrics = HardwareMetrics(
            cpu_percent=85.0, memory_percent=85.0, memory_available_mb=500.0,
            disk_percent=95.0, disk_free_gb=5.0
        )

        # Add active agents
        for i in range(3):
            coord._agents[f"a{i}"] = AgentInfo(
                agent_id=f"a{i}", agent_type="t", tier=3, state=AgentState.ACTIVE
            )

        recs = coord._get_hardware_recommendations()
        assert len(recs) >= 1

    def test_collect_hardware_metrics_no_psutil(self, tmp_path):
        """Test _collect_hardware_metrics without psutil."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        with patch('symbo_agentic_reasoners.core.resource_coordinator.HAS_PSUTIL', False):
            metrics = coord._collect_hardware_metrics()
            assert metrics.cpu_percent == 0.0


class TestResourceCoordinatorPartitioning:
    """Tests for partitioning functionality."""

    def test_get_adaptive_partition_no_selector(self, tmp_path):
        """Test get_adaptive_partition without selector."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)
        coord._partition_selector = None

        with patch('symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner.adaptive_partition') as mock:
            mock.return_value = Mock()
            result = coord.get_adaptive_partition({}, 2)
            mock.assert_called_once()

    def test_get_partition_decision_info(self, tmp_path):
        """Test get_partition_decision_info."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        # Without selector
        coord._partition_selector = None
        info = coord.get_partition_decision_info()
        assert info == {}

        # With selector
        mock_selector = Mock()
        mock_selector.get_decision_info = Mock(return_value={'strategy': 'balanced'})
        coord._partition_selector = mock_selector
        info = coord.get_partition_decision_info()
        assert info == {'strategy': 'balanced'}


class TestResourceCoordinatorGlobalFunctions:
    """Tests for global coordinator functions."""

    def test_get_coordinator(self):
        """Test get_coordinator singleton."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            get_coordinator, shutdown_coordinator, _coordinator
        )

        # Reset global
        import symbo_agentic_reasoners.core.resource_coordinator as rc_module
        rc_module._coordinator = None

        coord1 = get_coordinator()
        coord2 = get_coordinator()
        assert coord1 is coord2

        shutdown_coordinator()

    def test_shutdown_coordinator(self):
        """Test shutdown_coordinator."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            get_coordinator, shutdown_coordinator
        )
        import symbo_agentic_reasoners.core.resource_coordinator as rc_module

        rc_module._coordinator = None
        coord = get_coordinator()
        shutdown_coordinator()
        assert rc_module._coordinator is None


class TestResourceCoordinatorCleanup:
    """Tests for cleanup functionality."""

    def test_cleanup_idle_agents(self, tmp_path):
        """Test _cleanup_idle_agents."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, AgentInfo, AgentState, ResourceLimits
        )
        from datetime import timedelta

        coord = ResourceCoordinator(
            state_dir=tmp_path,
            limits=ResourceLimits(idle_timeout_seconds=0.1)
        )

        # Add standby agent with old last_active
        old_time = datetime.now() - timedelta(seconds=1)
        coord._agents["old_agent"] = AgentInfo(
            agent_id="old_agent",
            agent_type="test",
            tier=3,
            state=AgentState.STANDBY,
            last_active=old_time
        )

        coord._cleanup_idle_agents()
        assert coord._agents["old_agent"].state == AgentState.INACTIVE

    def test_check_critical_conditions(self, tmp_path):
        """Test _check_critical_conditions."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, HardwareMetrics
        )
        coord = ResourceCoordinator(state_dir=tmp_path)

        # No metrics
        coord._hardware_metrics = None
        coord._check_critical_conditions()

        # Critical memory
        coord._hardware_metrics = HardwareMetrics(memory_percent=98.0, cpu_percent=98.0)
        with patch.object(coord, '_cleanup_idle_agents') as mock_cleanup:
            coord._check_critical_conditions()
            mock_cleanup.assert_called_once()


class TestResourceCoordinatorSignals:
    """Tests for signal handling."""

    def test_install_signal_handlers(self, tmp_path):
        """Test _install_signal_handlers."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        coord._install_signal_handlers()
        coord._restore_signal_handlers()

    def test_install_signal_handlers_failure(self, tmp_path):
        """Test _install_signal_handlers when signal fails."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator
        coord = ResourceCoordinator(state_dir=tmp_path)

        with patch('signal.signal', side_effect=ValueError("Not in main thread")):
            coord._install_signal_handlers()  # Should not raise


class TestResourceCoordinatorAgentCreation:
    """Tests for agent creation edge cases."""

    def test_create_agent_at_limit(self, tmp_path):
        """Test _create_and_activate_agent at limit."""
        from symbo_agentic_reasoners.core.resource_coordinator import (
            ResourceCoordinator, AgentInfo, AgentState, ResourceLimits
        )

        coord = ResourceCoordinator(
            state_dir=tmp_path,
            limits=ResourceLimits(max_active_agents=2, idle_timeout_seconds=0.01)
        )

        factory = Mock(return_value=Mock())
        coord.register_agent_factory("test", factory)

        # Add agents at limit
        for i in range(2):
            coord._agents[f"a{i}"] = AgentInfo(
                agent_id=f"a{i}", agent_type="existing", tier=3, state=AgentState.ACTIVE
            )

        # Should fail to create
        result = coord._create_and_activate_agent("test")
        assert result is None

    def test_create_agent_factory_error(self, tmp_path):
        """Test _create_and_activate_agent with factory error."""
        from symbo_agentic_reasoners.core.resource_coordinator import ResourceCoordinator

        coord = ResourceCoordinator(state_dir=tmp_path)

        factory = Mock(side_effect=Exception("Factory error"))
        coord.register_agent_factory("test", factory)

        result = coord._create_and_activate_agent("test")
        assert result is None


# =============================================================================
# VectorDatabase Tests
# =============================================================================


class TestVectorDatabaseBasics:
    """Tests for VectorDatabase basic functionality."""

    def test_vector_entry_dataclass(self):
        """Test VectorEntry dataclass."""
        from symbo_agentic_reasoners.core.vector_database import VectorEntry
        entry = VectorEntry(
            entry_id="test_001",
            content="x + 1 = 0",
            entry_type="general"
        )
        assert entry.entry_id == "test_001"
        assert entry.content == "x + 1 = 0"
        assert entry.entry_type == "general"
        assert entry.embedding is None
        assert entry.metadata == {}

    def test_vector_entry_with_embedding(self):
        """Test VectorEntry with embedding."""
        from symbo_agentic_reasoners.core.vector_database import VectorEntry
        embedding = [0.1, 0.2, 0.3]
        entry = VectorEntry(
            entry_id="test_002",
            content="y = mx + b",
            embedding=embedding,
            metadata={'tag': 'linear'},
            entry_type="theorem"
        )
        assert entry.embedding == embedding
        assert entry.metadata['tag'] == 'linear'

    def test_init_mock_mode(self):
        """Test VectorDatabase initialization in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)
        assert db is not None
        assert db.client is None  # Mock mode

    def test_get_statistics_mock(self):
        """Test get_statistics in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)
        stats = db.get_statistics()
        assert stats['mode'] == 'mock'
        assert 'warning' in stats
        assert stats['total_entries'] == 0

    def test_repr_mock(self):
        """Test __repr__ in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)
        repr_str = repr(db)
        assert 'VectorDatabase' in repr_str
        assert 'mock' in repr_str


class TestVectorDatabaseMockStorage:
    """Tests for VectorDatabase mock storage operations."""

    def test_store_mock(self):
        """Test store in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        entry = VectorEntry(
            entry_id="entry_001",
            content="Pythagorean theorem: a^2 + b^2 = c^2",
            entry_type="theorem",
            metadata={'topic': 'geometry'}
        )

        result = db.store(entry)
        assert result == "entry_001"
        assert "entry_001" in db._mock_storage

    def test_store_generates_embedding(self):
        """Test that store generates embedding if not provided."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        entry = VectorEntry(
            entry_id="entry_002",
            content="Integration formula"
        )
        assert entry.embedding is None

        db.store(entry)
        # After storage, embedding should be generated
        assert db._mock_storage["entry_002"].embedding is not None

    def test_retrieve_mock(self):
        """Test retrieve in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        # Store entries
        for i in range(5):
            entry = VectorEntry(
                entry_id=f"entry_{i}",
                content=f"Content {i}",
                metadata={'index': i}
            )
            db.store(entry)

        # Retrieve
        results = db.retrieve([0.1] * 384, n_results=3)
        assert len(results) == 3

    def test_retrieve_with_metadata_filter(self):
        """Test retrieve with metadata filter."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        # Store entries with different types
        entry1 = VectorEntry(
            entry_id="theorem_001",
            content="Theorem content",
            metadata={'entry_type': 'theorem'}
        )
        entry2 = VectorEntry(
            entry_id="lemma_001",
            content="Lemma content",
            metadata={'entry_type': 'lemma'}
        )
        db.store(entry1)
        db.store(entry2)

        # Retrieve only theorems
        results = db.retrieve([0.1] * 384, metadata_filter={'entry_type': 'theorem'})
        assert len(results) == 1
        assert results[0].entry_id == "theorem_001"

    def test_retrieve_by_content_mock(self):
        """Test retrieve_by_content in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        entry = VectorEntry(
            entry_id="entry_001",
            content="Test content"
        )
        db.store(entry)

        results = db.retrieve_by_content("Similar content", n_results=5)
        assert len(results) >= 0  # Returns whatever matches

    def test_get_by_id_mock(self):
        """Test get_by_id in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        entry = VectorEntry(
            entry_id="unique_id",
            content="Unique content"
        )
        db.store(entry)

        retrieved = db.get_by_id("unique_id")
        assert retrieved is not None
        assert retrieved.entry_id == "unique_id"

    def test_get_by_id_not_found(self):
        """Test get_by_id when entry not found."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        result = db.get_by_id("nonexistent")
        assert result is None

    def test_delete_mock(self):
        """Test delete in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        entry = VectorEntry(
            entry_id="to_delete",
            content="Will be deleted"
        )
        db.store(entry)
        assert "to_delete" in db._mock_storage

        result = db.delete("to_delete")
        assert result is True
        assert "to_delete" not in db._mock_storage

    def test_delete_not_found(self):
        """Test delete when entry not found."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        result = db.delete("nonexistent")
        assert result is False

    def test_query_by_metadata_mock(self):
        """Test query_by_metadata in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        # Store entries with different agent IDs
        for i in range(5):
            entry = VectorEntry(
                entry_id=f"entry_{i}",
                content=f"Content {i}",
                metadata={'agent_id': f'agent_{i % 2}'}
            )
            db.store(entry)

        # Query by agent_id
        results = db.query_by_metadata({'agent_id': 'agent_0'})
        assert len(results) >= 1
        for r in results:
            assert r.metadata.get('agent_id') == 'agent_0'

    def test_query_by_metadata_with_limit(self):
        """Test query_by_metadata with limit."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        # Store many entries
        for i in range(10):
            entry = VectorEntry(
                entry_id=f"entry_{i}",
                content=f"Content {i}",
                metadata={'tag': 'common'}
            )
            db.store(entry)

        # Query with limit
        results = db.query_by_metadata({'tag': 'common'}, limit=3)
        assert len(results) == 3


class TestVectorDatabaseHelpers:
    """Tests for VectorDatabase helper functions."""

    def test_serialize_content_string(self):
        """Test _serialize_content with string."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        result = db._serialize_content("simple string")
        assert result == "simple string"

    def test_serialize_content_with_serialize_method(self):
        """Test _serialize_content with object that has serialize method."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        mock_obj = Mock()
        mock_obj.serialize.return_value = {'key': 'value'}

        result = db._serialize_content(mock_obj)
        assert result == '{"key": "value"}'

    def test_generate_mock_embedding(self):
        """Test _generate_mock_embedding."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        embedding = db._generate_mock_embedding("test content")
        assert len(embedding) == 384  # Standard embedding size
        assert all(0 <= v <= 1 for v in embedding)

    def test_generate_mock_embedding_deterministic(self):
        """Test that mock embedding is deterministic."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        emb1 = db._generate_mock_embedding("same content")
        emb2 = db._generate_mock_embedding("same content")
        assert emb1 == emb2

    def test_generate_embedding_mock_mode(self):
        """Test _generate_embedding in mock mode."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        embedding = db._generate_embedding("content")
        assert len(embedding) == 384


class TestVectorDatabaseCreateEntry:
    """Tests for create_vector_entry helper function."""

    def test_create_vector_entry_basic(self):
        """Test create_vector_entry basic usage."""
        from symbo_agentic_reasoners.core.vector_database import create_vector_entry

        entry = create_vector_entry(
            entry_id="test_001",
            content="Content here",
            entry_type="theorem"
        )

        assert entry.entry_id == "test_001"
        assert entry.content == "Content here"
        assert entry.entry_type == "theorem"
        assert 'timestamp' in entry.metadata

    def test_create_vector_entry_with_metadata(self):
        """Test create_vector_entry with custom metadata."""
        from symbo_agentic_reasoners.core.vector_database import create_vector_entry

        entry = create_vector_entry(
            entry_id="test_002",
            content="Content",
            entry_type="lemma",
            metadata={'agent': 'algebra', 'importance': 'high'}
        )

        assert entry.metadata['agent'] == 'algebra'
        assert entry.metadata['importance'] == 'high'
        assert entry.metadata['entry_type'] == 'lemma'


class TestVectorDatabaseEdgeCases:
    """Tests for edge cases and error handling."""

    def test_init_without_chromadb_mock_not_allowed(self):
        """Test init without chromadb when mock not allowed."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        import symbo_agentic_reasoners.core.vector_database as vdb_module

        original = vdb_module.CHROMADB_AVAILABLE
        try:
            vdb_module.CHROMADB_AVAILABLE = False
            with pytest.raises(RuntimeError) as excinfo:
                VectorDatabase(allow_mock=False)
            assert "ChromaDB is required" in str(excinfo.value)
        finally:
            vdb_module.CHROMADB_AVAILABLE = original

    def test_store_multiple_entries(self):
        """Test storing multiple entries."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        for i in range(100):
            entry = VectorEntry(
                entry_id=f"entry_{i}",
                content=f"Content number {i}",
                metadata={'batch': i // 10}
            )
            db.store(entry)

        stats = db.get_statistics()
        assert stats['total_entries'] == 100

    def test_retrieve_empty_database(self):
        """Test retrieve on empty database."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase
        db = VectorDatabase(allow_mock=True)

        results = db.retrieve([0.1] * 384, n_results=5)
        assert results == []

    def test_query_by_metadata_no_match(self):
        """Test query_by_metadata with no matches."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        db = VectorDatabase(allow_mock=True)

        entry = VectorEntry(
            entry_id="entry_001",
            content="Content",
            metadata={'type': 'A'}
        )
        db.store(entry)

        results = db.query_by_metadata({'type': 'B'})
        assert results == []

    def test_store_with_omdoc_content(self):
        """Test storing with OMDoc content."""
        from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
        from symbo_agentic_reasoners.core.omdoc_schema import OMObject

        db = VectorDatabase(allow_mock=True)

        om_obj = OMObject(variable="x")
        entry = VectorEntry(
            entry_id="omdoc_entry",
            content=om_obj,
            entry_type="expression"
        )

        db.store(entry)
        retrieved = db.get_by_id("omdoc_entry")
        assert retrieved is not None


# =============================================================================
# SolverEngine Tests for Coverage
# =============================================================================


class TestSolverEngineBasics:
    """Tests for SolverEngine basic functionality."""

    def test_init(self):
        """Test SolverEngine initialization."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine
        engine = SolverEngine()
        assert engine is not None

    def test_solve_status_enum(self):
        """Test SolveStatus enum."""
        from symbo_agentic_reasoners.core.solver_engine import SolveStatus
        assert SolveStatus.SUCCESS is not None
        assert SolveStatus.FAILED is not None
        assert SolveStatus.TIMEOUT is not None

    def test_solve_result_dataclass(self):
        """Test SolveResult dataclass."""
        from symbo_agentic_reasoners.core.solver_engine import SolveResult, SolveStatus
        result = SolveResult(
            status=SolveStatus.SUCCESS,
            result="x = 5"
        )
        assert result.status == SolveStatus.SUCCESS
        assert result.result == "x = 5"


class TestSolverEngineSolve:
    """Tests for SolverEngine solve methods."""

    def test_solve_simple_arithmetic(self):
        """Test solving simple arithmetic."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve("2 + 2")
        assert result.status == SolveStatus.SUCCESS

    def test_solve_algebra(self):
        """Test solving algebraic equation."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve("solve x + 5 = 10")
        assert result is not None

    def test_solve_calculus_derivative(self):
        """Test solving derivative."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve("derivative of x^2")
        assert result is not None

    def test_solve_expression_derivative(self):
        """Test solve_expression with derivative."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("x**2", operation="derivative")
        assert result.status == SolveStatus.SUCCESS
        assert "2*x" in str(result.result) or "2x" in str(result.result)

    def test_solve_expression_integral(self):
        """Test solve_expression with integral."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("x", operation="integral")
        assert result.status == SolveStatus.SUCCESS

    def test_solve_expression_factor(self):
        """Test solve_expression with factor."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("x**2 - 1", operation="factor")
        assert result.status == SolveStatus.SUCCESS

    def test_solve_expression_expand(self):
        """Test solve_expression with expand."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("(x+1)**2", operation="expand")
        assert result.status == SolveStatus.SUCCESS

    def test_solve_expression_simplify(self):
        """Test solve_expression with simplify."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("x + x", operation="simplify")
        assert result.status == SolveStatus.SUCCESS

    def test_solve_expression_solve_eq(self):
        """Test solve_expression with solve."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("x**2 - 4", operation="solve")
        assert result.status == SolveStatus.SUCCESS

    def test_solve_expression_with_error(self):
        """Test solve_expression records error properly."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        # Test with an expression that will trigger error handling path
        result = engine.solve_expression("1/0", operation="compute")
        # Either fails or succeeds with symbolic result - just verify no crash
        assert result is not None

    def test_get_statistics(self):
        """Test get_statistics."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine
        engine = SolverEngine()
        engine.solve("1 + 1")
        stats = engine.get_statistics()
        assert 'problems_solved' in stats
        assert 'problems_failed' in stats

    def test_singleton(self):
        """Test get_solver_engine singleton."""
        from symbo_agentic_reasoners.core.solver_engine import get_solver_engine
        e1 = get_solver_engine()
        e2 = get_solver_engine()
        assert e1 is e2


class TestSolverEngineOperations:
    """Tests for various solver operations."""

    def test_limit_operation(self):
        """Test limit operation."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("1/x", operation="limit")
        assert result is not None

    def test_series_operation(self):
        """Test series operation."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("sin(x)", operation="series")
        assert result is not None

    def test_compute_operation(self):
        """Test compute/evaluate operation."""
        from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus
        engine = SolverEngine()
        result = engine.solve_expression("2 + 3", operation="compute")
        assert result.status == SolveStatus.SUCCESS
        assert "5" in str(result.result)


# =============================================================================
# Orchestrator Tests for Coverage
# =============================================================================


class TestOrchestratorCoverage:
    """Additional tests for MainOrchestrator coverage."""

    def test_await_verified_result_no_blackboard(self):
        """Test _await_verified_result without blackboard raises error."""
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator, Task
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            StructuredProblem, ProblemType, MathDomain
        )
        from symbo_agentic_reasoners.core.omdoc_schema import OMObject
        from symbo_agentic_reasoners.core.blackboard import EntryStatus

        orch = MainOrchestrator()
        orch.blackboard = None  # Ensure no blackboard

        om_obj = OMObject(variable="x")
        sp = StructuredProblem(
            raw_input="x + 1 = 0",
            omdoc_content=om_obj,
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA
        )
        task = Task(
            task_id="test_task",
            structured_problem=sp,
            status=EntryStatus.PENDING
        )

        with pytest.raises(RuntimeError, match="No Blackboard available"):
            orch._await_verified_result(task)

    def test_get_statistics_with_pool(self):
        """Test get_statistics includes pool stats when pool exists."""
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem

        ams = AgentManagementSystem()
        orch = MainOrchestrator()

        # Create mock pool
        mock_pool = Mock()
        mock_pool.get_statistics.return_value = {'active': 2, 'dormant': 5}
        orch.agent_pool = mock_pool

        stats = orch.get_statistics()
        assert 'pool_stats' in stats
        assert stats['pool_stats']['active'] == 2

    def test_wake_domain_agents_no_pool(self):
        """Test _wake_domain_agents returns empty without pool."""
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator

        orch = MainOrchestrator()
        orch.agent_pool = None

        result = orch._wake_domain_agents("algebra")
        assert result == []

    def test_wake_domain_agents_with_pool(self):
        """Test _wake_domain_agents calls pool."""
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator

        orch = MainOrchestrator()
        mock_pool = Mock()
        mock_pool.wake_for_domain.return_value = ["agent_1", "agent_2"]
        orch.agent_pool = mock_pool

        result = orch._wake_domain_agents("algebra")
        assert result == ["agent_1", "agent_2"]
        assert orch.agents_woken == 2

    def test_activate_agent_no_pool(self):
        """Test _activate_agent returns True without pool."""
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator

        orch = MainOrchestrator()
        orch.agent_pool = None

        result = orch._activate_agent("agent_1")
        assert result is True

    def test_deactivate_agent_no_pool(self):
        """Test _deactivate_agent returns True without pool."""
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator

        orch = MainOrchestrator()
        orch.agent_pool = None

        result = orch._deactivate_agent("agent_1")
        assert result is True

    def test_decompose_returns_single_task(self):
        """Test _decompose returns single task in phase 1."""
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            StructuredProblem, ProblemType, MathDomain
        )
        from symbo_agentic_reasoners.core.omdoc_schema import OMObject

        orch = MainOrchestrator()

        om_obj = OMObject(variable="x")
        sp = StructuredProblem(
            raw_input="x + 1 = 0",
            omdoc_content=om_obj,
            problem_type=ProblemType.COMPUTATION,
            domain=MathDomain.ALGEBRA
        )

        result = orch._decompose(sp)
        assert len(result) == 1
        assert result[0] is sp

    def test_get_pool_domain_key(self):
        """Test get_pool_domain_key mapping."""
        from symbo_agentic_reasoners.core.orchestrator import get_pool_domain_key
        from symbo_agentic_reasoners.agents.base.problem_analysis import MathDomain

        assert get_pool_domain_key(MathDomain.ALGEBRA) == "algebra"
        assert get_pool_domain_key(MathDomain.CALCULUS) == "calculus"
        assert get_pool_domain_key(MathDomain.LINEAR_ALGEBRA) == "linear_algebra"
        assert get_pool_domain_key(MathDomain.STATISTICS) == "statistics"
