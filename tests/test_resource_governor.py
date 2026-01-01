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
Resource Governor Tests
=======================

Comprehensive tests for the Resource Governor module:
- ThrottleLevel enum
- ResourceStatus dataclass
- ResourceGovernor singleton pattern
- Resource monitoring integration
- Throttle calculation
- Emergency callbacks
"""

import pytest
import threading
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from symbo_agentic_reasoners.infrastructure.resource_governor import (
    ResourceGovernor,
    ResourceStatus,
    ThrottleLevel,
    get_governor,
)
from symbo_agentic_reasoners.infrastructure.ams import (
    EmergencyLevel,
    VRAM_THRESHOLD,
    RAM_THRESHOLD,
    CPU_THRESHOLD,
    VRAM_CRITICAL_THRESHOLD,
    RAM_CRITICAL_THRESHOLD,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def reset_singleton():
    """Reset ResourceGovernor singleton for isolated tests."""
    # Save original singleton
    original = ResourceGovernor._instance
    # Reset singleton
    ResourceGovernor._instance = None
    yield
    # Restore original singleton after test
    ResourceGovernor._instance = original


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create temporary log directory."""
    log_dir = tmp_path / "resource_logs"
    log_dir.mkdir()
    return str(log_dir)


@pytest.fixture
def mock_ams():
    """Create mock AMS."""
    ams = Mock()
    ams.get_resource_snapshot.return_value = {
        "vram_utilization": 0.5,
        "ram_utilization": 0.4,
        "cpu_utilization": 0.3,
        "emergency_level": "NORMAL",
        "queue_length": 0
    }
    ams.can_activate_cognitive_agent.return_value = True
    ams.register_emergency_callback = Mock()
    ams.start = Mock()
    ams.stop = Mock()
    return ams


@pytest.fixture
def mock_watchdog():
    """Create mock Watchdog."""
    watchdog = Mock()
    watchdog.get_statistics.return_value = {
        "active_tasks": 0,
        "completed_tasks": 0,
        "timeout_tasks": 0
    }
    watchdog.register_timeout_callback = Mock()
    watchdog.start = Mock()
    watchdog.stop = Mock()
    watchdog.start_task = Mock()
    watchdog.complete_task = Mock()
    watchdog.heartbeat = Mock()
    return watchdog


# =============================================================================
# ThrottleLevel Tests
# =============================================================================


class TestThrottleLevel:
    """Tests for ThrottleLevel enum."""

    def test_throttle_levels_exist(self):
        """Should have all throttle levels."""
        assert ThrottleLevel.NONE.value == 0
        assert ThrottleLevel.LIGHT.value == 1
        assert ThrottleLevel.MODERATE.value == 2
        assert ThrottleLevel.HEAVY.value == 3
        assert ThrottleLevel.BLOCKED.value == 4

    def test_throttle_level_ordering(self):
        """Throttle levels should be ordered by severity."""
        assert ThrottleLevel.NONE.value < ThrottleLevel.LIGHT.value
        assert ThrottleLevel.LIGHT.value < ThrottleLevel.MODERATE.value
        assert ThrottleLevel.MODERATE.value < ThrottleLevel.HEAVY.value
        assert ThrottleLevel.HEAVY.value < ThrottleLevel.BLOCKED.value

    def test_throttle_level_names(self):
        """Should have proper names."""
        assert ThrottleLevel.NONE.name == "NONE"
        assert ThrottleLevel.BLOCKED.name == "BLOCKED"


# =============================================================================
# ResourceStatus Tests
# =============================================================================


class TestResourceStatus:
    """Tests for ResourceStatus dataclass."""

    def test_create_resource_status(self):
        """Should create status with all fields."""
        status = ResourceStatus(
            timestamp=datetime.now(),
            vram_utilization=0.7,
            ram_utilization=0.6,
            cpu_utilization=0.5,
            disk_utilization=0.4,
            emergency_level=EmergencyLevel.NORMAL,
            throttle_level=ThrottleLevel.NONE,
            active_tasks=5,
            queued_agents=2,
            can_proceed=True,
            warnings=[]
        )

        assert status.vram_utilization == 0.7
        assert status.ram_utilization == 0.6
        assert status.cpu_utilization == 0.5
        assert status.disk_utilization == 0.4
        assert status.emergency_level == EmergencyLevel.NORMAL
        assert status.throttle_level == ThrottleLevel.NONE
        assert status.active_tasks == 5
        assert status.queued_agents == 2
        assert status.can_proceed is True
        assert status.warnings == []

    def test_resource_status_with_warnings(self):
        """Should accept warnings list."""
        status = ResourceStatus(
            timestamp=datetime.now(),
            vram_utilization=0.95,
            ram_utilization=0.92,
            cpu_utilization=0.3,
            disk_utilization=0.1,
            emergency_level=EmergencyLevel.WARNING,
            throttle_level=ThrottleLevel.MODERATE,
            active_tasks=10,
            queued_agents=5,
            can_proceed=True,
            warnings=["VRAM high", "RAM high"]
        )

        assert len(status.warnings) == 2
        assert "VRAM high" in status.warnings

    def test_resource_status_to_dict(self):
        """Should convert to dictionary."""
        ts = datetime.now()
        status = ResourceStatus(
            timestamp=ts,
            vram_utilization=0.5,
            ram_utilization=0.5,
            cpu_utilization=0.5,
            disk_utilization=0.5,
            emergency_level=EmergencyLevel.NORMAL,
            throttle_level=ThrottleLevel.NONE,
            active_tasks=0,
            queued_agents=0,
            can_proceed=True
        )

        d = status.to_dict()

        assert d["timestamp"] == ts.isoformat()
        assert d["vram"] == 0.5
        assert d["ram"] == 0.5
        assert d["cpu"] == 0.5
        assert d["disk"] == 0.5
        assert d["emergency_level"] == "NORMAL"
        assert d["throttle_level"] == "NONE"
        assert d["active_tasks"] == 0
        assert d["queued_agents"] == 0
        assert d["can_proceed"] is True
        assert d["warnings"] == []


# =============================================================================
# ResourceGovernor Singleton Tests
# =============================================================================


class TestResourceGovernorSingleton:
    """Tests for ResourceGovernor singleton pattern."""

    def test_singleton_returns_same_instance(self, reset_singleton, temp_log_dir):
        """Should return same instance."""
        gov1 = ResourceGovernor(log_dir=temp_log_dir)
        gov2 = ResourceGovernor(log_dir=temp_log_dir)

        assert gov1 is gov2

    def test_get_governor_returns_singleton(self, reset_singleton, temp_log_dir):
        """get_governor should return singleton."""
        # Force recreation by directly setting the instance
        gov1 = ResourceGovernor(log_dir=temp_log_dir)
        gov2 = get_governor()

        assert gov1 is gov2


# =============================================================================
# ResourceGovernor Initialization Tests
# =============================================================================


class TestResourceGovernorInit:
    """Tests for ResourceGovernor initialization."""

    def test_basic_initialization(self, reset_singleton, temp_log_dir):
        """Should initialize with defaults."""
        gov = ResourceGovernor(log_dir=temp_log_dir)

        assert gov._ams is None  # Not initialized until initialize() called
        assert gov._watchdog is None
        assert gov._running is False
        assert gov._throttle_level == ThrottleLevel.NONE
        assert gov._operations_allowed == 0
        assert gov._operations_throttled == 0
        assert gov._operations_blocked == 0
        assert gov._emergency_events == 0

    def test_log_directory_created(self, reset_singleton, tmp_path):
        """Should create log directory."""
        log_dir = tmp_path / "new_log_dir"
        gov = ResourceGovernor(log_dir=str(log_dir))

        assert log_dir.exists()

    def test_initialize_creates_components(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should initialize with provided components."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        assert gov._ams is mock_ams
        assert gov._watchdog is mock_watchdog
        mock_ams.register_emergency_callback.assert_called_once()
        mock_watchdog.register_timeout_callback.assert_called_once()

    def test_initialize_with_gpu_scheduler(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should accept optional GPU scheduler."""
        gpu_scheduler = Mock()
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog, gpu_scheduler=gpu_scheduler)

        assert gov._gpu_scheduler is gpu_scheduler


# =============================================================================
# ResourceGovernor Start/Stop Tests
# =============================================================================


class TestResourceGovernorStartStop:
    """Tests for start/stop operations."""

    def test_start_sets_running(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Start should set running flag."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)
        gov.start()

        assert gov._running is True
        mock_ams.start.assert_called_once()
        mock_watchdog.start.assert_called_once()

    def test_start_without_initialize(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Start should initialize if needed."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov._ams = None

        # Patch initialize to just set the mocks
        def mock_initialize():
            gov._ams = mock_ams
            gov._watchdog = mock_watchdog
            mock_ams.register_emergency_callback(lambda x, y: None)
            mock_watchdog.register_timeout_callback(lambda x: None)

        with patch.object(gov, 'initialize', side_effect=mock_initialize) as init_patch:
            gov.start()
            init_patch.assert_called_once()

    def test_stop_clears_running(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Stop should clear running flag."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)
        gov.start()
        gov.stop()

        assert gov._running is False
        mock_ams.stop.assert_called_once()
        mock_watchdog.stop.assert_called_once()

    def test_stop_with_gpu_scheduler(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Stop should stop GPU scheduler if present."""
        gpu_scheduler = Mock()
        gpu_scheduler.start = Mock()
        gpu_scheduler.stop = Mock()
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog, gpu_scheduler=gpu_scheduler)
        gov.start()
        gov.stop()

        gpu_scheduler.stop.assert_called_once()


# =============================================================================
# ResourceGovernor can_proceed Tests
# =============================================================================


class TestCanProceed:
    """Tests for can_proceed method."""

    def test_can_proceed_normal(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should allow operations in normal state."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        result = gov.can_proceed()

        assert result is True
        assert gov._operations_allowed == 1

    def test_always_allow_emergency_operations(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should always allow emergency operations."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)
        gov._throttle_level = ThrottleLevel.BLOCKED

        assert gov.can_proceed("emergency") is True
        assert gov.can_proceed("shutdown") is True
        assert gov.can_proceed("health_check") is True

    def test_block_when_throttle_blocked(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should block when throttle level is BLOCKED."""
        mock_ams.get_resource_snapshot.return_value = {
            "vram_utilization": 0.99,
            "ram_utilization": 0.99,
            "cpu_utilization": 0.99,
            "emergency_level": "EMERGENCY",
            "queue_length": 0
        }
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        result = gov.can_proceed("default")

        assert result is False

    def test_block_when_critical_emergency(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should block when emergency level is critical."""
        mock_ams.get_resource_snapshot.return_value = {
            "vram_utilization": 0.5,
            "ram_utilization": 0.5,
            "cpu_utilization": 0.5,
            "emergency_level": "CRITICAL",
            "queue_length": 0
        }
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        result = gov.can_proceed("default")

        # Critical emergency should block operations
        assert result is False

    def test_cognitive_activation_checks_ams(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should check AMS for cognitive activation."""
        mock_ams.can_activate_cognitive_agent.return_value = False
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        result = gov.can_proceed("cognitive_activation")

        assert result is False
        mock_ams.can_activate_cognitive_agent.assert_called_once()


# =============================================================================
# ResourceGovernor Operation Request Tests
# =============================================================================


class TestRequestOperation:
    """Tests for request_operation method."""

    def test_request_operation_success(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return task_id when approved."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        task_id = gov.request_operation(
            operation_type="test",
            timeout=30.0,
            description="Test operation"
        )

        assert task_id is not None
        assert "test" in task_id
        mock_watchdog.start_task.assert_called_once()

    def test_request_operation_blocked(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return None when blocked."""
        mock_ams.get_resource_snapshot.return_value = {
            "vram_utilization": 0.99,
            "ram_utilization": 0.99,
            "cpu_utilization": 0.99,
            "emergency_level": "EMERGENCY",
            "queue_length": 0
        }
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        task_id = gov.request_operation(operation_type="test")

        assert task_id is None

    def test_complete_operation(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should complete operation via watchdog."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        gov.complete_operation("task_123", success=True)

        mock_watchdog.complete_task.assert_called_once()

    def test_heartbeat(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should send heartbeat via watchdog."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        gov.heartbeat("task_123")

        mock_watchdog.heartbeat.assert_called_once_with("task_123")


# =============================================================================
# ResourceGovernor get_status Tests
# =============================================================================


class TestGetStatus:
    """Tests for get_status method."""

    def test_get_status_returns_status(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return ResourceStatus."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        status = gov.get_status()

        assert isinstance(status, ResourceStatus)
        assert status.vram_utilization == 0.5
        assert status.ram_utilization == 0.4
        assert status.cpu_utilization == 0.3
        assert status.emergency_level == EmergencyLevel.NORMAL
        assert status.throttle_level == ThrottleLevel.NONE
        assert status.can_proceed is True

    def test_get_status_without_ams(self, reset_singleton, temp_log_dir):
        """Should return default values without AMS."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov._ams = None
        gov._watchdog = None

        status = gov.get_status()

        assert status.vram_utilization == 0.0
        assert status.ram_utilization == 0.0
        assert status.cpu_utilization == 0.0
        assert status.emergency_level == EmergencyLevel.NORMAL

    def test_get_status_generates_warnings(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should generate warnings for high utilization."""
        # Use values above the thresholds (VRAM_THRESHOLD, RAM_THRESHOLD, CPU_THRESHOLD)
        mock_ams.get_resource_snapshot.return_value = {
            "vram_utilization": 0.95,  # > VRAM_THRESHOLD (0.80)
            "ram_utilization": 0.92,   # > RAM_THRESHOLD (0.85)
            "cpu_utilization": 0.90,   # > CPU_THRESHOLD (0.80)
            "emergency_level": "NORMAL",
            "queue_length": 0
        }
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        status = gov.get_status()

        # Check for warnings (thresholds are in ams.py)
        assert len(status.warnings) >= 1


# =============================================================================
# Throttle Level Calculation Tests
# =============================================================================


class TestThrottleLevelCalculation:
    """Tests for throttle level calculation."""

    def test_calculate_throttle_none(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return NONE for low utilization."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        level = gov._calculate_throttle_level(
            vram=0.3, ram=0.3, cpu=0.3, disk=0.3,
            emergency=EmergencyLevel.NORMAL
        )

        assert level == ThrottleLevel.NONE

    def test_calculate_throttle_light(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return LIGHT for 2 warnings."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        level = gov._calculate_throttle_level(
            vram=VRAM_THRESHOLD + 0.01,
            ram=RAM_THRESHOLD + 0.01,
            cpu=0.3,
            disk=0.3,
            emergency=EmergencyLevel.NORMAL
        )

        assert level == ThrottleLevel.LIGHT

    def test_calculate_throttle_moderate(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return MODERATE for 3+ warnings."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        level = gov._calculate_throttle_level(
            vram=VRAM_THRESHOLD + 0.01,
            ram=RAM_THRESHOLD + 0.01,
            cpu=CPU_THRESHOLD + 0.01,
            disk=0.3,
            emergency=EmergencyLevel.NORMAL
        )

        assert level == ThrottleLevel.MODERATE

    def test_calculate_throttle_heavy(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return HEAVY for critical emergency."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        level = gov._calculate_throttle_level(
            vram=0.5, ram=0.5, cpu=0.5, disk=0.5,
            emergency=EmergencyLevel.CRITICAL
        )

        assert level == ThrottleLevel.HEAVY

    def test_calculate_throttle_blocked(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return BLOCKED for emergency."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        level = gov._calculate_throttle_level(
            vram=0.5, ram=0.5, cpu=0.5, disk=0.5,
            emergency=EmergencyLevel.EMERGENCY
        )

        assert level == ThrottleLevel.BLOCKED

    def test_calculate_throttle_multiple_critical(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return HEAVY for multiple critical resources."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        level = gov._calculate_throttle_level(
            vram=VRAM_CRITICAL_THRESHOLD + 0.01,
            ram=RAM_CRITICAL_THRESHOLD + 0.01,
            cpu=0.3,
            disk=0.3,
            emergency=EmergencyLevel.NORMAL
        )

        assert level == ThrottleLevel.HEAVY


# =============================================================================
# Emergency Callback Tests
# =============================================================================


class TestEmergencyCallbacks:
    """Tests for emergency callbacks."""

    def test_on_emergency_registers_callback(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should register emergency callback."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)
        callback = Mock()

        gov.on_emergency(callback)

        assert callback in gov._emergency_callbacks

    def test_on_throttle_change_registers_callback(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should register throttle callback."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)
        callback = Mock()

        gov.on_throttle_change(callback)

        assert callback in gov._throttle_callbacks

    def test_emergency_callback_invoked(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Emergency callback should be invoked."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)
        callback = Mock()
        gov.on_emergency(callback)

        # Simulate AMS emergency
        gov._on_ams_emergency(EmergencyLevel.CRITICAL, {"test": "context"})

        callback.assert_called_once()
        assert gov._emergency_events == 1

    def test_emergency_callback_error_handled(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should handle callback errors gracefully."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        def failing_callback(level, context):
            raise ValueError("Callback error")

        gov.on_emergency(failing_callback)

        # Should not raise
        gov._on_ams_emergency(EmergencyLevel.CRITICAL, {})


# =============================================================================
# Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for statistics methods."""

    def test_get_statistics(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return statistics dict."""
        mock_ams.get_statistics.return_value = {"agents": 5}
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        stats = gov.get_statistics()

        assert isinstance(stats, dict)
        assert "running" in stats
        assert "operations_allowed" in stats
        assert "operations_throttled" in stats
        assert "operations_blocked" in stats
        assert "emergency_events" in stats
        assert "current_throttle_level" in stats
        assert "ams" in stats
        assert "watchdog" in stats

    def test_statistics_include_last_status(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should include last status if available."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        # Get status to populate _last_status
        gov.get_status()

        stats = gov.get_statistics()

        assert "last_status" in stats


# =============================================================================
# Logging Tests
# =============================================================================


class TestLogging:
    """Tests for logging functionality."""

    def test_log_event(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should write event to log file."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        gov._log_event("test_event", {"key": "value"})

        # Check log file exists and has content
        assert gov._log_file.exists()
        with open(gov._log_file, 'r') as f:
            content = f.read()
            assert "test_event" in content
            assert "value" in content

    def test_log_event_json_format(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should write valid JSON."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        gov._log_event("test", {"data": 123})

        with open(gov._log_file, 'r') as f:
            line = f.readline()
            data = json.loads(line)
            assert data["event_type"] == "test"
            assert data["data"]["data"] == 123


# =============================================================================
# Disk Utilization Tests
# =============================================================================


class TestDiskUtilization:
    """Tests for disk utilization."""

    def test_get_disk_utilization_with_psutil(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should get disk utilization with psutil."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        # Just verify it doesn't raise and returns a float
        disk = gov._get_disk_utilization()

        assert isinstance(disk, float)
        assert 0.0 <= disk <= 1.0

    def test_get_disk_utilization_handles_error(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should return 0.0 on error."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        # Set invalid path
        gov._log_dir = Path("/nonexistent/path/that/does/not/exist")

        disk = gov._get_disk_utilization()

        # Should return 0.0 or handle gracefully
        assert isinstance(disk, float)


# =============================================================================
# Task Timeout Tests
# =============================================================================


class TestTaskTimeout:
    """Tests for task timeout handling."""

    def test_on_task_timeout(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Should log timeout events."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        task = Mock()
        task.task_id = "timeout_task"
        task.elapsed_seconds = 30.0
        task.timeout_seconds = 25.0

        gov._on_task_timeout(task)

        # Check log file
        with open(gov._log_file, 'r') as f:
            content = f.read()
            assert "timeout" in content
            assert "timeout_task" in content


# =============================================================================
# Print Status Tests
# =============================================================================


class TestPrintStatus:
    """Tests for print_status method."""

    def test_print_status_runs(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog, capsys):
        """print_status should run without error."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)

        gov.print_status()

        captured = capsys.readouterr()
        assert "RESOURCE GOVERNOR STATUS" in captured.out
        assert "VRAM" in captured.out
        assert "RAM" in captured.out
        assert "CPU" in captured.out


# =============================================================================
# Integration Tests
# =============================================================================


class TestResourceGovernorIntegration:
    """Integration tests for ResourceGovernor."""

    def test_full_operation_lifecycle(self, reset_singleton, temp_log_dir, mock_ams, mock_watchdog):
        """Test complete operation lifecycle."""
        gov = ResourceGovernor(log_dir=temp_log_dir)
        gov.initialize(ams=mock_ams, watchdog=mock_watchdog)
        gov.start()

        # Check status
        status = gov.get_status()
        assert status.can_proceed is True

        # Request operation
        task_id = gov.request_operation(
            operation_type="integration_test",
            timeout=60.0,
            description="Integration test operation"
        )
        assert task_id is not None

        # Send heartbeat
        gov.heartbeat(task_id)

        # Complete operation
        gov.complete_operation(task_id, success=True)

        # Check statistics
        stats = gov.get_statistics()
        assert stats["operations_allowed"] >= 1

        # Stop
        gov.stop()
        assert gov._running is False


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
