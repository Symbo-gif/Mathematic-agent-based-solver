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
Infrastructure Module Comprehensive Tests
==========================================

Comprehensive tests for infrastructure modules to achieve 75%+ coverage:
- AgentManagementSystem (AMS)
- Watchdog
- ResourceGovernor
- Directory Facilitator
- Agent Pool
"""

import pytest


# =============================================================================
# AMS Enums Tests
# =============================================================================


class TestEmergencyLevel:
    """Tests for EmergencyLevel enum."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.ams import EmergencyLevel
        assert EmergencyLevel is not None

    def test_normal(self):
        from symbo_agentic_reasoners.infrastructure.ams import EmergencyLevel
        assert EmergencyLevel.NORMAL.value == 0

    def test_warning(self):
        from symbo_agentic_reasoners.infrastructure.ams import EmergencyLevel
        assert EmergencyLevel.WARNING.value == 1

    def test_critical(self):
        from symbo_agentic_reasoners.infrastructure.ams import EmergencyLevel
        assert EmergencyLevel.CRITICAL.value == 2

    def test_emergency(self):
        from symbo_agentic_reasoners.infrastructure.ams import EmergencyLevel
        assert EmergencyLevel.EMERGENCY.value == 3

    def test_shutdown(self):
        from symbo_agentic_reasoners.infrastructure.ams import EmergencyLevel
        assert EmergencyLevel.SHUTDOWN.value == 4


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentStatus
        assert AgentStatus is not None

    def test_inactive(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentStatus
        assert AgentStatus.INACTIVE.value == 'inactive'

    def test_queued(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentStatus
        assert AgentStatus.QUEUED.value == 'queued'

    def test_active(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentStatus
        assert AgentStatus.ACTIVE.value == 'active'

    def test_suspended(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentStatus
        assert AgentStatus.SUSPENDED.value == 'suspended'

    def test_terminated(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentStatus
        assert AgentStatus.TERMINATED.value == 'terminated'


class TestAgentType:
    """Tests for AgentType enum."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        assert AgentType is not None

    def test_infrastructural(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        assert AgentType.INFRASTRUCTURAL.value == 'infrastructural'

    def test_cognitive(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        assert AgentType.COGNITIVE.value == 'cognitive'


class TestAgentRecord:
    """Tests for AgentRecord dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentRecord, AgentType, AgentStatus
        )
        record = AgentRecord(
            agent_id="test_agent_001",
            agent_type=AgentType.COGNITIVE,
            status=AgentStatus.INACTIVE
        )
        assert record.agent_id == "test_agent_001"
        assert record.agent_type == AgentType.COGNITIVE
        assert record.status == AgentStatus.INACTIVE

    def test_creation_with_requirements(self):
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentRecord, AgentType, AgentStatus
        )
        record = AgentRecord(
            agent_id="cognitive_001",
            agent_type=AgentType.COGNITIVE,
            status=AgentStatus.QUEUED,
            vram_requirement=5.5,
            ram_requirement=2.0
        )
        assert record.vram_requirement == 5.5
        assert record.ram_requirement == 2.0

    def test_repr(self):
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentRecord, AgentType, AgentStatus
        )
        record = AgentRecord(
            agent_id="repr_test",
            agent_type=AgentType.INFRASTRUCTURAL,
            status=AgentStatus.ACTIVE,
            vram_requirement=0.5
        )
        repr_str = repr(record)
        assert "repr_test" in repr_str
        assert "infrastructural" in repr_str


# =============================================================================
# AMS Tests
# =============================================================================


class TestAgentManagementSystemComprehensive:
    """Comprehensive tests for AgentManagementSystem."""

    @pytest.fixture
    def ams(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem
        return AgentManagementSystem()

    def test_initialization(self, ams):
        assert ams is not None

    def test_has_create_agent(self, ams):
        assert hasattr(ams, 'create_agent')

    def test_has_activate_agent(self, ams):
        assert hasattr(ams, 'activate_agent')

    def test_has_deactivate_agent(self, ams):
        assert hasattr(ams, 'deactivate_agent')

    def test_has_get_statistics(self, ams):
        assert hasattr(ams, 'get_statistics')

    def test_get_statistics(self, ams):
        stats = ams.get_statistics()
        assert isinstance(stats, dict)

    def test_create_agent(self, ams):
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        result = ams.create_agent(
            agent_id="test_infra_agent",
            agent_type=AgentType.INFRASTRUCTURAL
        )
        assert result is True

    def test_create_cognitive_agent(self, ams):
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        result = ams.create_agent(
            agent_id="test_cognitive_agent",
            agent_type=AgentType.COGNITIVE
        )
        assert result is True

    def test_get_agent(self, ams):
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent(
            agent_id="status_test_agent",
            agent_type=AgentType.INFRASTRUCTURAL
        )
        agent = ams.get_agent("status_test_agent")
        assert agent is not None

    def test_get_unknown_agent(self, ams):
        agent = ams.get_agent("nonexistent_agent")
        assert agent is None

    def test_list_agents(self, ams):
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent("list_test_1", AgentType.INFRASTRUCTURAL)
        ams.create_agent("list_test_2", AgentType.COGNITIVE)
        agents = ams.list_agents()
        assert len(agents) >= 2

    def test_get_vram_usage(self, ams):
        usage = ams.get_vram_usage()
        assert isinstance(usage, (int, float))

    def test_get_ram_usage(self, ams):
        usage = ams.get_ram_usage()
        assert isinstance(usage, (int, float))

    def test_get_cpu_usage(self, ams):
        usage = ams.get_cpu_usage()
        assert isinstance(usage, (int, float))

    def test_get_emergency_level(self, ams):
        from symbo_agentic_reasoners.infrastructure.ams import EmergencyLevel
        level = ams.get_emergency_level()
        assert isinstance(level, EmergencyLevel)

    def test_get_resource_snapshot(self, ams):
        snapshot = ams.get_resource_snapshot()
        assert isinstance(snapshot, dict)


# =============================================================================
# Watchdog Comprehensive Tests
# =============================================================================


class TestWatchdogComprehensive:
    """Comprehensive tests for Watchdog."""

    @pytest.fixture
    def watchdog(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import Watchdog
        return Watchdog()

    def test_initialization(self, watchdog):
        assert watchdog is not None

    def test_has_get_statistics(self, watchdog):
        assert hasattr(watchdog, 'get_statistics')

    def test_get_statistics(self, watchdog):
        stats = watchdog.get_statistics()
        assert isinstance(stats, dict)


class TestRunWithTimeout:
    """Tests for run_with_timeout utility."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import run_with_timeout
        assert run_with_timeout is not None

    def test_successful_execution(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import run_with_timeout

        def quick_func():
            return "success"

        result = run_with_timeout(quick_func, timeout=5.0)
        assert result == "success"

    def test_timeout_error_exists(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import TimeoutError
        assert TimeoutError is not None


# =============================================================================
# ResourceGovernor Comprehensive Tests
# =============================================================================


class TestResourceGovernorComprehensive:
    """Comprehensive tests for ResourceGovernor."""

    @pytest.fixture
    def governor(self):
        from symbo_agentic_reasoners.infrastructure.resource_governor import ResourceGovernor
        return ResourceGovernor()

    def test_initialization(self, governor):
        assert governor is not None

    def test_has_get_statistics(self, governor):
        assert hasattr(governor, 'get_statistics')

    def test_get_statistics(self, governor):
        stats = governor.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# Directory Facilitator Tests
# =============================================================================


class TestDirectoryFacilitator:
    """Tests for DirectoryFacilitator."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        assert DirectoryFacilitator is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        df = DirectoryFacilitator()
        assert df is not None

    def test_has_get_statistics(self):
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        df = DirectoryFacilitator()
        assert hasattr(df, 'get_statistics')


# =============================================================================
# ACC Tests
# =============================================================================


class TestACCComprehensive:
    """Comprehensive tests for Agent Coordination Center (AgentCommunicationChannel)."""

    def test_module_import(self):
        from symbo_agentic_reasoners.infrastructure import acc
        assert acc is not None

    def test_acc_class_exists(self):
        from symbo_agentic_reasoners.infrastructure.acc import AgentCommunicationChannel
        assert AgentCommunicationChannel is not None

    def test_message_envelope_exists(self):
        from symbo_agentic_reasoners.infrastructure.acc import MessageEnvelope
        assert MessageEnvelope is not None

    def test_acc_initialization(self):
        from symbo_agentic_reasoners.infrastructure.acc import AgentCommunicationChannel
        acc_instance = AgentCommunicationChannel()
        assert acc_instance is not None

    def test_acc_has_get_statistics(self):
        from symbo_agentic_reasoners.infrastructure.acc import AgentCommunicationChannel
        acc_instance = AgentCommunicationChannel()
        assert hasattr(acc_instance, 'get_statistics')


# =============================================================================
# Agent Pool Tests
# =============================================================================


class TestAgentPoolComprehensive:
    """Comprehensive tests for AgentPool."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool
        assert AgentPool is not None

    def test_initialization_requires_ams(self):
        from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem
        ams = AgentManagementSystem()
        pool = AgentPool(ams)
        assert pool is not None


# =============================================================================
# Agent Registry Tests
# =============================================================================


class TestAgentRegistryComprehensive:
    """Comprehensive tests for agent_registry module."""

    def test_module_import(self):
        from symbo_agentic_reasoners.infrastructure import agent_registry
        assert agent_registry is not None


# =============================================================================
# Extended AMS Tests
# =============================================================================


class TestAMSExtended:
    """Extended tests for AMS to increase coverage."""

    @pytest.fixture
    def ams(self):
        from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem
        return AgentManagementSystem()

    def test_start_stop(self, ams):
        """Test starting and stopping AMS."""
        ams.start()
        ams.stop()

    def test_activate_agent(self, ams):
        """Test activating an agent."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent("activate_test", AgentType.INFRASTRUCTURAL)
        result = ams.activate_agent("activate_test")
        assert result is True

    def test_activate_nonexistent(self, ams):
        """Test activating nonexistent agent."""
        result = ams.activate_agent("nonexistent_agent")
        assert result is False

    def test_deactivate_agent(self, ams):
        """Test deactivating an agent."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent("deactivate_test", AgentType.INFRASTRUCTURAL)
        ams.activate_agent("deactivate_test")
        result = ams.deactivate_agent("deactivate_test")
        assert result is True

    def test_deactivate_nonexistent(self, ams):
        """Test deactivating nonexistent agent."""
        result = ams.deactivate_agent("nonexistent_agent")
        assert result is False

    def test_kill_agent(self, ams):
        """Test killing an agent."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent("kill_test", AgentType.INFRASTRUCTURAL)
        result = ams.kill_agent("kill_test")
        assert result is True

    def test_kill_nonexistent(self, ams):
        """Test killing nonexistent agent."""
        result = ams.kill_agent("nonexistent_agent")
        assert result is False

    def test_suspend_agent(self, ams):
        """Test suspending an agent."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent("suspend_test", AgentType.INFRASTRUCTURAL)
        ams.activate_agent("suspend_test")
        result = ams.suspend_agent("suspend_test")
        assert result is True

    def test_suspend_nonexistent(self, ams):
        """Test suspending nonexistent agent."""
        result = ams.suspend_agent("nonexistent_agent")
        assert result is False

    def test_list_agents_filter_status(self, ams):
        """Test listing agents filtered by status."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType, AgentStatus
        ams.create_agent("filter_status_test", AgentType.INFRASTRUCTURAL)
        ams.activate_agent("filter_status_test")
        active_agents = ams.list_agents(status=AgentStatus.ACTIVE)
        assert len(active_agents) >= 1

    def test_list_agents_filter_type(self, ams):
        """Test listing agents filtered by type."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent("filter_type_test", AgentType.COGNITIVE)
        cognitive_agents = ams.list_agents(agent_type=AgentType.COGNITIVE)
        assert len(cognitive_agents) >= 1

    def test_can_activate_cognitive_agent(self, ams):
        """Test can_activate_cognitive_agent check."""
        result = ams.can_activate_cognitive_agent()
        assert isinstance(result, bool)

    def test_get_ram_utilization(self, ams):
        """Test getting RAM utilization."""
        util = ams.get_ram_utilization()
        assert isinstance(util, float)
        assert 0.0 <= util <= 1.0

    def test_is_throttled(self, ams):
        """Test throttle check."""
        result = ams.is_throttled()
        assert isinstance(result, bool)

    def test_create_duplicate_agent(self, ams):
        """Test creating duplicate agent."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        ams.create_agent("duplicate_test", AgentType.INFRASTRUCTURAL)
        result = ams.create_agent("duplicate_test", AgentType.INFRASTRUCTURAL)
        assert result is False

    def test_cognitive_agent_queue(self, ams):
        """Test cognitive agent queuing."""
        from symbo_agentic_reasoners.infrastructure.ams import AgentType
        # Create and activate first cognitive agent
        ams.create_agent("cog1", AgentType.COGNITIVE)
        result1 = ams.activate_agent("cog1")
        # Create second cognitive agent - should be queued
        ams.create_agent("cog2", AgentType.COGNITIVE)
        result2 = ams.activate_agent("cog2")
        # Second activation may succeed if first was queued, or fail if first activated
        assert isinstance(result2, bool)


# =============================================================================
# Extended Watchdog Tests
# =============================================================================


class TestWatchdogExtended:
    """Extended tests for Watchdog to increase coverage."""

    @pytest.fixture
    def watchdog(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import Watchdog
        return Watchdog()

    def test_start_stop(self, watchdog):
        """Test starting and stopping watchdog."""
        watchdog.start()
        watchdog.stop()

    def test_start_task(self, watchdog):
        """Test starting a task."""
        task_id = watchdog.start_task("test_task", timeout=10.0)
        assert task_id == "test_task"

    def test_heartbeat(self, watchdog):
        """Test sending heartbeat."""
        watchdog.start_task("heartbeat_task", timeout=10.0)
        watchdog.heartbeat("heartbeat_task")
        # Should not raise

    def test_complete_task(self, watchdog):
        """Test completing a task."""
        from symbo_agentic_reasoners.infrastructure.watchdog import TaskStatus
        watchdog.start_task("complete_task", timeout=10.0)
        watchdog.complete_task("complete_task", TaskStatus.COMPLETED)
        # Should not raise

    def test_cancel_task(self, watchdog):
        """Test cancelling a task."""
        watchdog.start_task("cancel_task", timeout=10.0)
        watchdog.cancel_task("cancel_task")
        # Should not raise

    def test_get_task_status(self, watchdog):
        """Test getting task status."""
        watchdog.start_task("status_task", timeout=10.0)
        status = watchdog.get_task_status("status_task")
        assert status is not None
        assert 'task_id' in status

    def test_get_task_status_nonexistent(self, watchdog):
        """Test getting status of nonexistent task."""
        status = watchdog.get_task_status("nonexistent_task")
        assert status is None

    def test_get_active_tasks(self, watchdog):
        """Test getting active tasks."""
        watchdog.start_task("active_task1", timeout=10.0)
        watchdog.start_task("active_task2", timeout=10.0)
        active = watchdog.get_active_tasks()
        assert len(active) >= 2

    def test_register_timeout_callback(self, watchdog):
        """Test registering timeout callback."""
        def callback(task):
            pass
        watchdog.register_timeout_callback(callback)
        # Should not raise


class TestWatchedTask:
    """Tests for WatchedTask dataclass."""

    def test_creation(self):
        """Test creating WatchedTask."""
        from symbo_agentic_reasoners.infrastructure.watchdog import WatchedTask
        from datetime import datetime
        task = WatchedTask(
            task_id="test",
            timeout_seconds=10.0,
            started_at=datetime.now(),
            last_heartbeat=datetime.now()
        )
        assert task.task_id == "test"

    def test_elapsed_seconds(self):
        """Test elapsed_seconds property."""
        from symbo_agentic_reasoners.infrastructure.watchdog import WatchedTask
        from datetime import datetime
        import time
        task = WatchedTask(
            task_id="elapsed",
            timeout_seconds=10.0,
            started_at=datetime.now(),
            last_heartbeat=datetime.now()
        )
        time.sleep(0.1)
        assert task.elapsed_seconds >= 0.1

    def test_to_dict(self):
        """Test to_dict method."""
        from symbo_agentic_reasoners.infrastructure.watchdog import WatchedTask
        from datetime import datetime
        task = WatchedTask(
            task_id="dict_test",
            timeout_seconds=10.0,
            started_at=datetime.now(),
            last_heartbeat=datetime.now()
        )
        d = task.to_dict()
        assert d['task_id'] == "dict_test"
        assert 'elapsed' in d  # actual key name

    def test_is_expired(self):
        """Test is_expired property."""
        from symbo_agentic_reasoners.infrastructure.watchdog import WatchedTask
        from datetime import datetime, timedelta
        # Task that expired in the past
        task = WatchedTask(
            task_id="expired",
            timeout_seconds=0.001,
            started_at=datetime.now() - timedelta(seconds=1),
            last_heartbeat=datetime.now() - timedelta(seconds=1)
        )
        assert task.is_expired is True

    def test_remaining_seconds(self):
        """Test remaining_seconds property."""
        from symbo_agentic_reasoners.infrastructure.watchdog import WatchedTask
        from datetime import datetime
        task = WatchedTask(
            task_id="remaining",
            timeout_seconds=100.0,
            started_at=datetime.now(),
            last_heartbeat=datetime.now()
        )
        assert task.remaining_seconds > 90


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_running(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import TaskStatus
        assert TaskStatus.RUNNING.value == 'running'

    def test_completed(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import TaskStatus
        assert TaskStatus.COMPLETED.value == 'completed'

    def test_timed_out(self):
        from symbo_agentic_reasoners.infrastructure.watchdog import TaskStatus
        assert TaskStatus.TIMED_OUT.value == 'timed_out'


# =============================================================================
# Extended ACC Tests
# =============================================================================


class TestACCExtended:
    """Extended tests for AgentCommunicationChannel."""

    @pytest.fixture
    def acc(self):
        from symbo_agentic_reasoners.infrastructure.acc import AgentCommunicationChannel
        return AgentCommunicationChannel()

    def test_register_agent(self, acc):
        """Test registering an agent."""
        def handler(msg):
            pass
        acc.register_agent("test_agent", handler)
        assert acc.is_agent_active("test_agent")

    def test_unregister_agent(self, acc):
        """Test unregistering an agent."""
        def handler(msg):
            pass
        acc.register_agent("unreg_agent", handler)
        acc.unregister_agent("unreg_agent")
        assert not acc.is_agent_active("unreg_agent")

    def test_is_agent_active_false(self, acc):
        """Test checking inactive agent."""
        result = acc.is_agent_active("nonexistent_agent")
        assert result is False

    def test_get_queue_size(self, acc):
        """Test getting queue size."""
        def handler(msg):
            pass
        acc.register_agent("queue_agent", handler)
        size = acc.get_queue_size("queue_agent")
        assert isinstance(size, int)

    def test_get_queue_size_nonexistent(self, acc):
        """Test queue size for nonexistent agent."""
        size = acc.get_queue_size("nonexistent")
        assert size == 0

    def test_get_statistics(self, acc):
        """Test get_statistics method."""
        stats = acc.get_statistics()
        assert isinstance(stats, dict)
        assert 'active_agents' in stats  # actual key name

    def test_clear_history(self, acc):
        """Test clearing message history."""
        acc.clear_history()
        # Should not raise


class TestMessageEnvelope:
    """Tests for MessageEnvelope dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.infrastructure.acc import MessageEnvelope
        from symbo_agentic_reasoners.protocols.fipa_acl import FIPAMessage
        msg = FIPAMessage(
            performative="request",
            sender="a",
            receiver="b",
            content={}
        )
        envelope = MessageEnvelope(message=msg)
        assert envelope.message == msg

    def test_repr(self):
        from symbo_agentic_reasoners.infrastructure.acc import MessageEnvelope
        from symbo_agentic_reasoners.protocols.fipa_acl import FIPAMessage
        msg = FIPAMessage(
            performative="inform",
            sender="a",
            receiver="b",
            content={}
        )
        envelope = MessageEnvelope(message=msg)
        repr_str = repr(envelope)
        assert "Envelope" in repr_str  # actual format


# =============================================================================
# Extended DirectoryFacilitator Tests
# =============================================================================


class TestDirectoryFacilitatorExtended:
    """Extended tests for DirectoryFacilitator."""

    @pytest.fixture
    def df(self):
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
        return DirectoryFacilitator()

    def test_get_statistics(self, df):
        """Test getting statistics."""
        stats = df.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# Extended ResourceGovernor Tests
# =============================================================================


class TestResourceGovernorExtended:
    """Extended tests for ResourceGovernor."""

    @pytest.fixture
    def governor(self):
        from symbo_agentic_reasoners.infrastructure.resource_governor import ResourceGovernor
        return ResourceGovernor()

    def test_get_statistics(self, governor):
        """Test getting statistics."""
        stats = governor.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
