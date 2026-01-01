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
Security Monitor Tests
======================

Comprehensive tests for the Security Monitor module:
- AlertSeverity enum
- AccessDecision enum
- AnomalyType enum
- AccessLog dataclass
- SecurityAlert dataclass
- AccessPolicy dataclass
- SecurityMonitor BDI agent
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import (
    SecurityMonitor,
    AlertSeverity,
    AccessDecision,
    AnomalyType,
    AccessLog,
    SecurityAlert,
    AccessPolicy,
)


# =============================================================================
# AlertSeverity Tests
# =============================================================================


class TestAlertSeverity:
    """Tests for AlertSeverity enum."""

    def test_alert_severities_exist(self):
        """Should have all severity levels."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"

    def test_alert_severity_count(self):
        """Should have correct number of severities."""
        assert len(AlertSeverity) == 5


# =============================================================================
# AccessDecision Tests
# =============================================================================


class TestAccessDecision:
    """Tests for AccessDecision enum."""

    def test_access_decisions_exist(self):
        """Should have all decision types."""
        assert AccessDecision.ALLOW.value == "allow"
        assert AccessDecision.DENY.value == "deny"
        assert AccessDecision.AUDIT.value == "audit"
        assert AccessDecision.CHALLENGE.value == "challenge"

    def test_access_decision_count(self):
        """Should have correct number of decisions."""
        assert len(AccessDecision) == 4


# =============================================================================
# AnomalyType Tests
# =============================================================================


class TestAnomalyType:
    """Tests for AnomalyType enum."""

    def test_anomaly_types_exist(self):
        """Should have all anomaly types."""
        assert AnomalyType.RATE_LIMIT.value == "rate_limit"
        assert AnomalyType.UNUSUAL_PATTERN.value == "unusual_pattern"
        assert AnomalyType.PRIVILEGE_ESCALATION.value == "privilege_escalation"
        assert AnomalyType.DATA_EXFILTRATION.value == "data_exfiltration"
        assert AnomalyType.UNKNOWN_AGENT.value == "unknown_agent"

    def test_anomaly_type_count(self):
        """Should have correct number of types."""
        assert len(AnomalyType) == 5


# =============================================================================
# AccessLog Tests
# =============================================================================


class TestAccessLog:
    """Tests for AccessLog dataclass."""

    def test_create_access_log(self):
        """Should create log with all fields."""
        log = AccessLog(
            timestamp=datetime.now(),
            agent_id="agent_001",
            resource="blackboard/data",
            action="read",
            decision=AccessDecision.ALLOW
        )

        assert log.agent_id == "agent_001"
        assert log.resource == "blackboard/data"
        assert log.action == "read"
        assert log.decision == AccessDecision.ALLOW

    def test_access_log_default_metadata(self):
        """Should default metadata to empty dict."""
        log = AccessLog(
            timestamp=datetime.now(),
            agent_id="agent",
            resource="res",
            action="act",
            decision=AccessDecision.DENY
        )

        assert log.metadata == {}

    def test_access_log_with_metadata(self):
        """Should accept metadata."""
        log = AccessLog(
            timestamp=datetime.now(),
            agent_id="agent",
            resource="res",
            action="act",
            decision=AccessDecision.AUDIT,
            metadata={"ip": "127.0.0.1", "reason": "unknown agent"}
        )

        assert log.metadata["ip"] == "127.0.0.1"

    def test_access_log_to_dict(self):
        """Should convert to dictionary."""
        ts = datetime.now()
        log = AccessLog(
            timestamp=ts,
            agent_id="agent_123",
            resource="admin/config",
            action="write",
            decision=AccessDecision.DENY
        )

        d = log.to_dict()

        assert d["timestamp"] == ts.isoformat()
        assert d["agent_id"] == "agent_123"
        assert d["resource"] == "admin/config"
        assert d["action"] == "write"
        assert d["decision"] == "deny"


# =============================================================================
# SecurityAlert Tests
# =============================================================================


class TestSecurityAlert:
    """Tests for SecurityAlert dataclass."""

    def test_create_security_alert(self):
        """Should create alert with all fields."""
        alert = SecurityAlert(
            alert_id="alert_001",
            timestamp=datetime.now(),
            severity=AlertSeverity.HIGH,
            anomaly_type=AnomalyType.RATE_LIMIT,
            agent_id="agent_suspect",
            description="Rate limit exceeded",
            recommended_action="Throttle requests"
        )

        assert alert.alert_id == "alert_001"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.anomaly_type == AnomalyType.RATE_LIMIT
        assert alert.agent_id == "agent_suspect"
        assert alert.description == "Rate limit exceeded"
        assert alert.recommended_action == "Throttle requests"

    def test_security_alert_default_acknowledged(self):
        """Should default acknowledged to False."""
        alert = SecurityAlert(
            alert_id="alert",
            timestamp=datetime.now(),
            severity=AlertSeverity.LOW,
            anomaly_type=AnomalyType.UNKNOWN_AGENT,
            agent_id="agent",
            description="desc",
            recommended_action="action"
        )

        assert alert.acknowledged is False

    def test_security_alert_none_agent(self):
        """Should allow None agent_id."""
        alert = SecurityAlert(
            alert_id="system_alert",
            timestamp=datetime.now(),
            severity=AlertSeverity.CRITICAL,
            anomaly_type=AnomalyType.UNUSUAL_PATTERN,
            agent_id=None,
            description="System lockdown",
            recommended_action="Investigate"
        )

        assert alert.agent_id is None

    def test_security_alert_to_dict(self):
        """Should convert to dictionary."""
        ts = datetime.now()
        alert = SecurityAlert(
            alert_id="a123",
            timestamp=ts,
            severity=AlertSeverity.MEDIUM,
            anomaly_type=AnomalyType.DATA_EXFILTRATION,
            agent_id="agent_007",
            description="Unusual data access",
            recommended_action="Review"
        )

        d = alert.to_dict()

        assert d["alert_id"] == "a123"
        assert d["timestamp"] == ts.isoformat()
        assert d["severity"] == "medium"
        assert d["type"] == "data_exfiltration"
        assert d["agent"] == "agent_007"
        assert d["description"] == "Unusual data access"
        assert d["action"] == "Review"


# =============================================================================
# AccessPolicy Tests
# =============================================================================


class TestAccessPolicy:
    """Tests for AccessPolicy dataclass."""

    def test_create_access_policy(self):
        """Should create policy with all fields."""
        policy = AccessPolicy(
            policy_id="policy_001",
            agent_pattern="admin.*",
            resource_pattern="config/.*",
            allowed_actions={"read", "write"},
            max_rate_per_minute=50,
            enabled=True
        )

        assert policy.policy_id == "policy_001"
        assert policy.agent_pattern == "admin.*"
        assert policy.resource_pattern == "config/.*"
        assert policy.allowed_actions == {"read", "write"}
        assert policy.max_rate_per_minute == 50
        assert policy.enabled is True

    def test_access_policy_defaults(self):
        """Should have sensible defaults."""
        policy = AccessPolicy(
            policy_id="default",
            agent_pattern=".*",
            resource_pattern=".*",
            allowed_actions={"read"}
        )

        assert policy.max_rate_per_minute == 100
        assert policy.enabled is True

    def test_access_policy_to_dict(self):
        """Should convert to dictionary."""
        policy = AccessPolicy(
            policy_id="test_policy",
            agent_pattern="test.*",
            resource_pattern="test/.*",
            allowed_actions={"read", "execute"},
            max_rate_per_minute=200
        )

        d = policy.to_dict()

        assert d["policy_id"] == "test_policy"
        assert d["agent_pattern"] == "test.*"
        assert d["resource_pattern"] == "test/.*"
        assert set(d["actions"]) == {"read", "execute"}
        assert d["rate_limit"] == 200


# =============================================================================
# SecurityMonitor Initialization Tests
# =============================================================================


class TestSecurityMonitorInit:
    """Tests for SecurityMonitor initialization."""

    def test_basic_initialization(self):
        """Should initialize with defaults."""
        monitor = SecurityMonitor()

        assert monitor.agent_id == 'security_monitor_001'
        assert monitor.lockdown_mode is False
        assert monitor.df is None
        assert monitor.blackboard is None
        assert len(monitor.policies) >= 3  # Default policies

    def test_custom_initialization(self):
        """Should accept custom parameters."""
        df = Mock()
        bb = Mock()
        monitor = SecurityMonitor(
            agent_id='custom_monitor',
            df=df,
            blackboard=bb,
            lockdown_mode=True
        )

        assert monitor.agent_id == 'custom_monitor'
        assert monitor.lockdown_mode is True
        assert monitor.df is df
        assert monitor.blackboard is bb

    def test_statistics_initialized(self):
        """Should initialize statistics to zero."""
        monitor = SecurityMonitor()

        assert monitor.tasks_executed == 0
        assert monitor.tasks_succeeded == 0
        assert monitor.tasks_failed == 0
        assert monitor.access_checks == 0
        assert monitor.access_denials == 0
        assert monitor.alerts_generated == 0

    def test_default_policies_loaded(self):
        """Should load default policies."""
        monitor = SecurityMonitor()

        assert "default_allow" in monitor.policies
        assert "blackboard_access" in monitor.policies
        assert "admin_restrict" in monitor.policies

    def test_registers_with_df(self):
        """Should register with Directory Facilitator."""
        df = Mock()
        df.register = Mock()

        monitor = SecurityMonitor(df=df)

        df.register.assert_called_once()


# =============================================================================
# SecurityMonitor Agent Registration Tests
# =============================================================================


class TestAgentRegistration:
    """Tests for agent registration."""

    def test_register_agent(self):
        """Should register agent as known."""
        monitor = SecurityMonitor()

        monitor.register_agent("agent_001")

        assert "agent_001" in monitor.known_agents

    def test_register_multiple_agents(self):
        """Should register multiple agents."""
        monitor = SecurityMonitor()

        monitor.register_agent("agent_001")
        monitor.register_agent("agent_002")
        monitor.register_agent("agent_003")

        assert len(monitor.known_agents) == 3


# =============================================================================
# SecurityMonitor Access Check Tests
# =============================================================================


class TestAccessCheck:
    """Tests for check_access method."""

    @pytest.fixture
    def monitor(self):
        """Create monitor with registered agent."""
        m = SecurityMonitor()
        m.register_agent("known_agent")
        return m

    def test_check_access_known_agent_allowed(self, monitor):
        """Should allow known agent with valid action."""
        decision = monitor.check_access("known_agent", "blackboard/data", "read")

        assert decision == AccessDecision.ALLOW
        assert monitor.access_checks == 1

    def test_check_access_unknown_agent_audit(self, monitor):
        """Should audit unknown agent."""
        decision = monitor.check_access("unknown_agent", "data", "read")

        assert decision == AccessDecision.AUDIT
        assert monitor.alerts_generated >= 1

    def test_check_access_blocked_agent_deny(self, monitor):
        """Should deny blocked agent."""
        monitor.blocked_agents.add("blocked_agent")

        decision = monitor.check_access("blocked_agent", "any", "read")

        assert decision == AccessDecision.DENY
        assert monitor.access_denials >= 1

    def test_check_access_lockdown_mode_deny(self, monitor):
        """Should deny all in lockdown mode."""
        monitor.lockdown_mode = True

        decision = monitor.check_access("known_agent", "data", "read")

        assert decision == AccessDecision.DENY

    def test_check_access_increments_counters(self, monitor):
        """Should increment statistics counters."""
        monitor.check_access("known_agent", "data", "read")

        assert monitor.tasks_executed == 1
        assert monitor.access_checks == 1

    def test_check_access_logs_attempt(self, monitor):
        """Should log access attempt."""
        initial_logs = len(monitor.access_logs)

        monitor.check_access("known_agent", "resource", "read")

        assert len(monitor.access_logs) == initial_logs + 1


# =============================================================================
# SecurityMonitor Rate Limiting Tests
# =============================================================================


class TestRateLimiting:
    """Tests for rate limiting."""

    def test_rate_limit_allows_normal_traffic(self):
        """Should allow requests within rate limit."""
        monitor = SecurityMonitor()
        monitor.register_agent("agent")

        # Make a few requests
        for _ in range(5):
            result = monitor._check_rate_limit("agent")
            assert result is True

    def test_rate_limit_denies_excessive_traffic(self):
        """Should deny requests exceeding rate limit."""
        monitor = SecurityMonitor()
        monitor.register_agent("agent")

        # Set a very low rate limit
        monitor.policies["default_allow"].max_rate_per_minute = 3

        # Make requests up to limit
        for _ in range(3):
            monitor._check_rate_limit("agent")

        # Next request should be denied
        result = monitor._check_rate_limit("agent")
        assert result is False

    def test_rate_limit_cleans_old_entries(self):
        """Should clean old entries from rate counter."""
        monitor = SecurityMonitor()

        # Add old entries
        old_time = datetime.now() - timedelta(minutes=2)
        monitor.rate_counters["agent"] = [old_time, old_time]

        # Check rate limit (should clean old entries)
        monitor._check_rate_limit("agent")

        # Old entries should be removed
        assert len(monitor.rate_counters["agent"]) == 1


# =============================================================================
# SecurityMonitor Alert Tests
# =============================================================================


class TestAlerts:
    """Tests for alert functionality."""

    def test_create_alert(self):
        """Should create and store alert."""
        monitor = SecurityMonitor()

        alert_id = monitor._create_alert(
            AnomalyType.RATE_LIMIT,
            AlertSeverity.MEDIUM,
            "agent_001",
            "Rate limit exceeded",
            "Throttle requests"
        )

        assert alert_id in monitor.alerts
        assert monitor.alerts_generated == 1

    def test_get_recent_alerts(self):
        """Should return recent alerts."""
        monitor = SecurityMonitor()

        # Create some alerts
        monitor._create_alert(
            AnomalyType.UNKNOWN_AGENT,
            AlertSeverity.LOW,
            "agent_1",
            "Unknown agent",
            "Verify"
        )
        monitor._create_alert(
            AnomalyType.RATE_LIMIT,
            AlertSeverity.HIGH,
            "agent_2",
            "Rate exceeded",
            "Throttle"
        )

        alerts = monitor.get_recent_alerts()

        assert len(alerts) == 2

    def test_get_recent_alerts_with_filter(self):
        """Should filter by severity."""
        monitor = SecurityMonitor()

        monitor._create_alert(
            AnomalyType.UNKNOWN_AGENT,
            AlertSeverity.LOW,
            "agent_1",
            "Low alert",
            "Action"
        )
        monitor._create_alert(
            AnomalyType.RATE_LIMIT,
            AlertSeverity.HIGH,
            "agent_2",
            "High alert",
            "Action"
        )

        alerts = monitor.get_recent_alerts(severity_filter=AlertSeverity.HIGH)

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.HIGH

    def test_get_recent_alerts_with_limit(self):
        """Should respect limit."""
        monitor = SecurityMonitor()

        # Create many alerts
        for i in range(10):
            monitor._create_alert(
                AnomalyType.UNKNOWN_AGENT,
                AlertSeverity.LOW,
                f"agent_{i}",
                f"Alert {i}",
                "Action"
            )

        alerts = monitor.get_recent_alerts(limit=5)

        assert len(alerts) == 5

    def test_acknowledge_alert(self):
        """Should acknowledge alert."""
        monitor = SecurityMonitor()

        alert_id = monitor._create_alert(
            AnomalyType.UNKNOWN_AGENT,
            AlertSeverity.MEDIUM,
            "agent",
            "Test",
            "Action"
        )

        assert monitor.alerts[alert_id].acknowledged is False

        monitor.acknowledge_alert(alert_id)

        assert monitor.alerts[alert_id].acknowledged is True


# =============================================================================
# SecurityMonitor Block/Unblock Tests
# =============================================================================


class TestBlockUnblock:
    """Tests for blocking/unblocking agents."""

    def test_block_agent(self):
        """Should block agent."""
        monitor = SecurityMonitor()

        monitor.block_agent("bad_actor", "Suspicious behavior")

        assert "bad_actor" in monitor.blocked_agents
        assert monitor.alerts_generated >= 1

    def test_blocked_agent_denied_access(self):
        """Blocked agent should be denied access."""
        monitor = SecurityMonitor()
        monitor.register_agent("agent")
        monitor.block_agent("agent", "Test")

        decision = monitor.check_access("agent", "resource", "read")

        assert decision == AccessDecision.DENY

    def test_unblock_agent(self):
        """Should unblock agent."""
        monitor = SecurityMonitor()
        monitor.blocked_agents.add("agent")

        monitor.unblock_agent("agent")

        assert "agent" not in monitor.blocked_agents

    def test_unblock_nonexistent_agent(self):
        """Should handle unblocking nonexistent agent."""
        monitor = SecurityMonitor()

        # Should not raise
        monitor.unblock_agent("nonexistent")


# =============================================================================
# SecurityMonitor Lockdown Tests
# =============================================================================


class TestLockdown:
    """Tests for lockdown mode."""

    def test_set_lockdown_enabled(self):
        """Should enable lockdown."""
        monitor = SecurityMonitor()

        monitor.set_lockdown(True)

        assert monitor.lockdown_mode is True
        assert monitor.alerts_generated >= 1  # Should create critical alert

    def test_set_lockdown_disabled(self):
        """Should disable lockdown."""
        monitor = SecurityMonitor(lockdown_mode=True)

        monitor.set_lockdown(False)

        assert monitor.lockdown_mode is False

    def test_lockdown_denies_all(self):
        """Lockdown should deny all access."""
        monitor = SecurityMonitor()
        monitor.register_agent("trusted_agent")
        monitor.set_lockdown(True)

        decision = monitor.check_access("trusted_agent", "any", "read")

        assert decision == AccessDecision.DENY


# =============================================================================
# SecurityMonitor Process Tests
# =============================================================================


class TestProcess:
    """Tests for process method."""

    @pytest.fixture
    def monitor(self):
        """Create monitor with mock blackboard."""
        bb = Mock()
        bb.post = Mock()
        m = SecurityMonitor(blackboard=bb)
        m.register_agent("known_agent")
        return m

    def test_process_status_operation(self, monitor):
        """Should handle status operation."""
        task_entry = Mock()
        task_entry.metadata = {'operation': 'status'}

        result = monitor.process(task_entry)

        assert 'lockdown_mode' in result.metadata

    def test_process_check_access_operation(self, monitor):
        """Should handle check_access operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'check_access',
            'agent_id': 'known_agent',
            'resource': 'data',
            'action': 'read'
        }

        result = monitor.process(task_entry)

        assert 'decision' in result.metadata

    def test_process_register_agent_operation(self, monitor):
        """Should handle register_agent operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'register_agent',
            'agent_id': 'new_agent'
        }

        result = monitor.process(task_entry)

        assert result.metadata['registered'] == 'new_agent'
        assert 'new_agent' in monitor.known_agents

    def test_process_block_agent_operation(self, monitor):
        """Should handle block_agent operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'block_agent',
            'agent_id': 'bad_agent',
            'reason': 'Testing'
        }

        result = monitor.process(task_entry)

        assert result.metadata['blocked'] == 'bad_agent'
        assert 'bad_agent' in monitor.blocked_agents

    def test_process_get_alerts_operation(self, monitor):
        """Should handle get_alerts operation."""
        # Create an alert first
        monitor._create_alert(
            AnomalyType.UNKNOWN_AGENT,
            AlertSeverity.LOW,
            "agent",
            "Test",
            "Action"
        )

        task_entry = Mock()
        task_entry.metadata = {'operation': 'get_alerts'}

        result = monitor.process(task_entry)

        assert 'alerts' in result.metadata
        assert 'count' in result.metadata

    def test_process_lockdown_operation(self, monitor):
        """Should handle lockdown operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'lockdown',
            'enabled': True
        }

        result = monitor.process(task_entry)

        assert result.metadata['lockdown'] is True
        assert monitor.lockdown_mode is True

    def test_process_unknown_operation(self, monitor):
        """Should handle unknown operation."""
        task_entry = Mock()
        task_entry.metadata = {'operation': 'unknown_op'}

        result = monitor.process(task_entry)

        assert 'error' in result.metadata

    def test_process_without_blackboard(self):
        """Should work without blackboard."""
        monitor = SecurityMonitor(blackboard=None)
        task_entry = Mock()
        task_entry.metadata = {'operation': 'status'}

        result = monitor.process(task_entry)

        assert isinstance(result, dict)


# =============================================================================
# SecurityMonitor BDI Interface Tests
# =============================================================================


class TestBDIInterface:
    """Tests for BDI interface methods."""

    def test_update_beliefs(self):
        """update_beliefs should not raise."""
        monitor = SecurityMonitor()
        monitor.update_beliefs()  # Should not raise

    def test_deliberate(self):
        """deliberate should return list."""
        monitor = SecurityMonitor()
        result = monitor.deliberate()

        assert isinstance(result, list)

    def test_execute_step(self):
        """execute_step should not raise."""
        monitor = SecurityMonitor()
        intention = Mock()

        monitor.execute_step(intention)  # Should not raise


# =============================================================================
# SecurityMonitor Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for statistics methods."""

    def test_get_statistics(self):
        """Should return statistics dict."""
        monitor = SecurityMonitor()

        stats = monitor.get_statistics()

        assert isinstance(stats, dict)
        assert 'tasks_executed' in stats
        assert 'tasks_succeeded' in stats
        assert 'tasks_failed' in stats
        assert 'access_checks' in stats
        assert 'access_denials' in stats
        assert 'denial_rate' in stats
        assert 'alerts_generated' in stats
        assert 'lockdown_mode' in stats

    def test_statistics_after_access_checks(self):
        """Should track statistics after access checks."""
        monitor = SecurityMonitor()
        monitor.register_agent("agent")

        monitor.check_access("agent", "resource", "read")
        monitor.check_access("unknown", "resource", "read")

        stats = monitor.get_statistics()
        assert stats['access_checks'] == 2


# =============================================================================
# SecurityMonitor Log Management Tests
# =============================================================================


class TestLogManagement:
    """Tests for access log management."""

    def test_log_access(self):
        """Should log access attempts."""
        monitor = SecurityMonitor()

        monitor._log_access("agent", "resource", "read", AccessDecision.ALLOW)

        assert len(monitor.access_logs) == 1
        assert monitor.access_logs[0].agent_id == "agent"

    def test_log_trimming(self):
        """Should trim logs when exceeding max."""
        monitor = SecurityMonitor()
        monitor.max_log_entries = 5

        # Add more than max entries
        for i in range(10):
            monitor._log_access(f"agent_{i}", "res", "read", AccessDecision.ALLOW)

        assert len(monitor.access_logs) == 5


# =============================================================================
# Integration Tests
# =============================================================================


class TestSecurityMonitorIntegration:
    """Integration tests for SecurityMonitor."""

    def test_full_workflow(self):
        """Test complete security monitoring workflow."""
        monitor = SecurityMonitor()

        # Register agents
        monitor.register_agent("agent_001")
        monitor.register_agent("agent_002")

        # Check access for known agents
        decision1 = monitor.check_access("agent_001", "data", "read")
        assert decision1 == AccessDecision.ALLOW

        # Check access for unknown agent
        decision2 = monitor.check_access("unknown", "data", "read")
        assert decision2 == AccessDecision.AUDIT

        # Block an agent
        monitor.block_agent("agent_001", "Testing")

        # Verify blocked agent is denied
        decision3 = monitor.check_access("agent_001", "data", "read")
        assert decision3 == AccessDecision.DENY

        # Check alerts
        alerts = monitor.get_recent_alerts()
        assert len(alerts) >= 2  # At least unknown agent + block alert

        # Check statistics
        stats = monitor.get_statistics()
        assert stats['access_checks'] >= 3
        assert stats['access_denials'] >= 1


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
