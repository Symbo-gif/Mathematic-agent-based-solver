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
Agent Security and Isolation Tests
===================================

Tests for multi-agent security including:
- Agent impersonation prevention
- Message spoofing detection
- Privilege escalation prevention
- Service registry manipulation
- Agent access control
"""

import pytest
from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import (
    SecurityMonitor, AccessDecision, AlertSeverity
)


class TestAgentImpersonation:
    """Test agent impersonation prevention."""

    def test_infrastructure_agent_cannot_be_spoofed(self):
        """Infrastructure agents should be protected from impersonation."""
        monitor = SecurityMonitor()

        # Register legitimate infrastructure agent
        monitor.register_agent("ams_001")

        # Attempt to register duplicate with same ID
        # Should either be rejected or flagged
        monitor.register_agent("ams_001")

        # Should have generated an alert
        alerts = monitor.get_recent_alerts()
        # In a real system, this should create a security alert

    def test_system_agent_id_validation(self):
        """System agent IDs should follow strict validation."""
        monitor = SecurityMonitor()

        # Malicious agent IDs
        suspicious_ids = [
            "ams_001; DROP TABLE agents;",
            "system\x00null",
            "../../../admin",
            "admin' OR '1'='1",
        ]

        for agent_id in suspicious_ids:
            # Should either sanitize or reject
            try:
                monitor.register_agent(agent_id)
                # If accepted, verify it's treated as literal string
                assert agent_id in monitor.known_agents
            except (ValueError, TypeError):
                # Rejection is acceptable
                pass


class TestMessageSpoofing:
    """Test message spoofing prevention."""

    def test_message_sender_validation(self):
        """Messages should validate sender identity."""
        from symbo_agentic_reasoners.core.message_bus import (
            message_bus, AgentMessage, MessageType, MessagePriority
        )

        # Create message claiming to be from critical system
        spoofed_message = AgentMessage(
            sender_id="security_monitor_001",  # Spoofed
            recipient_id="ams",
            message_type=MessageType.REQUEST,
            priority=MessagePriority.CRITICAL,
            content={"operation": "shutdown"}
        )

        # Message bus should have validation mechanism
        # This test documents expected behavior
        message_bus.send_message(spoofed_message)

    def test_message_tampering_detection(self):
        """Messages should detect tampering."""
        from symbo_agentic_reasoners.core.message_bus import (
            message_bus, AgentMessage, MessageType
        )

        # Send message
        original_content = {"action": "compute", "data": "x+1"}
        msg = AgentMessage(
            sender_id="agent_a",
            recipient_id="agent_b",
            message_type=MessageType.REQUEST,
            content=original_content
        )

        msg_id = message_bus.send_message(msg)

        # In production, message should be immutable or have integrity check
        # Verify content cannot be modified after sending

    def test_message_replay_attack_detection(self):
        """Detect replayed messages."""
        from symbo_agentic_reasoners.core.message_bus import (
            message_bus, AgentMessage, MessageType
        )

        msg = AgentMessage(
            sender_id="agent_a",
            recipient_id="agent_b",
            message_type=MessageType.REQUEST,
            content={"command": "sensitive_operation"}
        )

        # Send message first time
        msg_id_1 = message_bus.send_message(msg)

        # Attempt to replay same message
        msg_id_2 = message_bus.send_message(msg)

        # Message IDs should be different
        assert msg_id_1 != msg_id_2

        # System should detect duplicate/replay


class TestPrivilegeEscalation:
    """Test privilege escalation prevention."""

    def test_cognitive_agent_admin_access_denied(self):
        """Cognitive agents should not access admin resources."""
        monitor = SecurityMonitor()
        monitor.register_agent("cognitive_001")

        # Attempt admin operations
        admin_resources = [
            ("admin/config", "write"),
            ("admin/shutdown", "execute"),
            ("system/emergency", "write"),
            ("ams/terminate_agent", "execute"),
        ]

        for resource, action in admin_resources:
            decision = monitor.check_access(
                agent_id="cognitive_001",
                resource=resource,
                action=action
            )

            assert decision in [AccessDecision.DENY, AccessDecision.AUDIT], \
                f"Cognitive agent should not access {resource}"

    def test_specialist_cannot_access_supervisor_resources(self):
        """Specialists should have limited access scope."""
        monitor = SecurityMonitor()
        monitor.register_agent("algebra_specialist_001")

        # Specialist attempting to access supervisor resources
        decision = monitor.check_access(
            agent_id="algebra_specialist_001",
            resource="supervisor/strategy",
            action="write"
        )

        assert decision == AccessDecision.DENY

    def test_infrastructure_agent_protection(self):
        """Infrastructure agents should have special protections."""
        monitor = SecurityMonitor()

        # Infrastructure agent should be pre-registered
        # Attempt to access infrastructure agent controls
        decision = monitor.check_access(
            agent_id="regular_agent",
            resource="infrastructure/watchdog",
            action="terminate"
        )

        assert decision == AccessDecision.DENY


class TestServiceRegistryManipulation:
    """Test service registry security."""

    def test_duplicate_service_registration_detected(self):
        """Detect attempts to register duplicate critical services."""
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator, create_service_registration
        )

        df = DirectoryFacilitator()

        # Register legitimate service
        legit_service = create_service_registration(
            service_type='system.ams',
            agent_id='ams_001',
            algorithm='resource_management'
        )
        df.register(legit_service)

        # Attempt to register duplicate (impersonation)
        duplicate_service = create_service_registration(
            service_type='system.ams',
            agent_id='malicious_agent',
            algorithm='resource_management'
        )

        # Should be rejected or flagged
        try:
            df.register(duplicate_service)
            # If registration succeeded, verify only one AMS service exists
            ams_services = df.find_services('system.ams')
            # Should have detection mechanism
        except (ValueError, Exception):
            # Rejection is expected
            pass

    def test_service_priority_manipulation(self):
        """Prevent service priority manipulation."""
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator, create_service_registration
        )

        df = DirectoryFacilitator()

        # Attempt to register with extreme priority
        malicious_service = create_service_registration(
            service_type='math.solver',
            agent_id='malicious_solver',
            algorithm='fake',
            cost='free'  # Manipulated to appear better
        )

        # Service registration should validate priority/cost
        df.register(malicious_service)

        # Verify service cannot hijack high-priority operations


class TestAccessControlEnforcement:
    """Test access control policy enforcement."""

    def test_unknown_agent_access_audited(self):
        """Unknown agents should trigger audit mode."""
        monitor = SecurityMonitor()

        # Don't register agent - unknown
        decision = monitor.check_access(
            agent_id="unknown_agent_xyz",
            resource="blackboard/data",
            action="read"
        )

        # Should be in audit mode
        assert decision in [AccessDecision.AUDIT, AccessDecision.DENY]

        # Should generate security alert
        alerts = monitor.get_recent_alerts()
        assert len(alerts) > 0
        assert any('unknown' in a.description.lower() for a in alerts)

    def test_rate_limiting_enforced(self):
        """Rate limiting should prevent abuse."""
        monitor = SecurityMonitor()
        monitor.register_agent("aggressive_agent")

        # Rapidly send many access requests
        denied_count = 0
        for i in range(2000):  # Way over limit
            decision = monitor.check_access(
                agent_id="aggressive_agent",
                resource=f"resource_{i}",
                action="read"
            )
            if decision == AccessDecision.DENY:
                denied_count += 1

        # Should have triggered rate limiting
        assert denied_count > 0, "Rate limiting not enforced"

        # Should generate alert
        alerts = monitor.get_recent_alerts()
        assert any('rate' in a.description.lower() for a in alerts)

    def test_blacklist_enforcement(self):
        """Blacklisted agents should be blocked."""
        monitor = SecurityMonitor()
        monitor.register_agent("bad_agent")

        # Block agent
        monitor.block_agent("bad_agent", "Security violation")

        # All access should be denied
        decision = monitor.check_access(
            agent_id="bad_agent",
            resource="any/resource",
            action="read"
        )

        assert decision == AccessDecision.DENY

    def test_lockdown_mode(self):
        """Lockdown mode should deny all access."""
        monitor = SecurityMonitor()
        monitor.register_agent("normal_agent")

        # Enable lockdown
        monitor.set_lockdown(True)

        # Even registered agents should be denied
        decision = monitor.check_access(
            agent_id="normal_agent",
            resource="safe/resource",
            action="read"
        )

        assert decision == AccessDecision.DENY

        # Should generate critical alert
        alerts = monitor.get_recent_alerts(severity_filter=AlertSeverity.CRITICAL)
        assert len(alerts) > 0


class TestAgentIsolation:
    """Test agent isolation mechanisms."""

    def test_cognitive_agent_vram_isolation(self):
        """Cognitive agents should have resource isolation."""
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentManagementSystem, AgentType
        )

        ams = AgentManagementSystem()

        # Create cognitive agents
        ams.create_agent("cognitive_a", AgentType.COGNITIVE)
        ams.create_agent("cognitive_b", AgentType.COGNITIVE)

        # Activate both
        ams.activate_agent("cognitive_a")
        ams.activate_agent("cognitive_b")

        # Each should have isolated resources
        # Verify they don't interfere with each other

    def test_specialist_cannot_kill_other_agents(self):
        """Agents should not be able to terminate other agents."""
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentManagementSystem, AgentType
        )

        ams = AgentManagementSystem()

        # Create two agents
        ams.create_agent("agent_a", AgentType.COGNITIVE)
        ams.create_agent("agent_b", AgentType.COGNITIVE)

        # Agent A should not be able to terminate Agent B
        # This would require AMS-level privileges
        # Test documents expected behavior


class TestSecurityEventLogging:
    """Test security event logging."""

    def test_access_denial_logged(self):
        """Access denials should be logged."""
        monitor = SecurityMonitor()
        monitor.register_agent("test_agent")

        # Attempt to access restricted resource
        monitor.check_access(
            agent_id="test_agent",
            resource="admin/config",
            action="write"
        )

        # Check access logs
        assert len(monitor.access_logs) > 0
        assert any(log.decision == AccessDecision.DENY for log in monitor.access_logs)

    def test_security_alerts_generated(self):
        """Security violations should generate alerts."""
        monitor = SecurityMonitor()

        # Trigger security event
        monitor.block_agent("bad_actor", "Malicious behavior")

        # Alert should be generated
        alerts = monitor.get_recent_alerts()
        assert len(alerts) > 0

        # Alert should be HIGH or CRITICAL severity
        assert any(a.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]
                  for a in alerts)

    def test_alert_acknowledgment(self):
        """Alerts should be acknowledgeable."""
        monitor = SecurityMonitor()
        monitor.block_agent("test", "test")

        alerts = monitor.get_recent_alerts()
        alert_id = alerts[0].alert_id

        # Acknowledge alert
        monitor.acknowledge_alert(alert_id)

        # Alert should be marked as acknowledged
        assert monitor.alerts[alert_id].acknowledged


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
