# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Phase 5 Integration Tests
==========================

Integration tests for all Phase 5 security fixes working together.

Tests Issues #4-12 in realistic scenarios.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.infrastructure.security.agent_auth import AgentAuthenticator
from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem, AgentType
from symbo_agentic_reasoners.core.message_bus import MessageBus, AgentMessage, MessageType
from symbo_agentic_reasoners.infrastructure.acc import AgentCommunicationChannel, BoundedMessageQueue
from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import RainbowDeployment
from symbo_agentic_reasoners.infrastructure.watchdog import ResourceUsageTracker
from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import (
    BehavioralAnomalyDetector, ThreatPatternDatabase
)


class TestEndToEndSecurity:
    """Test end-to-end security scenarios."""

    def test_authenticated_agent_lifecycle(self):
        """Test complete agent lifecycle with authentication."""
        # Create AMS with authentication
        ams = AgentManagementSystem()

        # Issue credential
        cred = ams.issue_agent_credential('agent_001')

        # Create agent with valid authentication
        success = ams.create_agent(
            agent_id='agent_001',
            agent_type=AgentType.INFRASTRUCTURAL,
            auth_token=cred.token,
            auth_timestamp=cred.timestamp
        )

        assert success is True

        # Attempt with invalid credential should fail
        success = ams.create_agent(
            agent_id='agent_002',
            agent_type=AgentType.INFRASTRUCTURAL,
            auth_token='invalid_token',
            auth_timestamp=int(time.time())
        )

        assert success is False

    def test_message_integrity_end_to_end(self):
        """Test message integrity from send to receive."""
        bus = MessageBus(require_signatures=True, allow_unsigned=False)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'data': 'test'}
        )

        # Send (auto-signs)
        msg_id = bus.send_message(message)

        # Register handler
        received = []
        bus.register_handler('agent_002', lambda m: received.append(m))

        # Process (verifies)
        bus.process_messages()

        # Should be delivered
        assert len(received) == 1
        assert bus.messages_verified == 1

    def test_security_rollback_integration(self):
        """Test security monitor triggers deployment rollback."""
        security_monitor = Mock()
        security_monitor.get_recent_alerts = Mock(return_value=[
            {'severity': 'HIGH'} for _ in range(5)
        ])

        deployment = RainbowDeployment(Mock(), security_monitor=security_monitor)
        deployment.previous_version = 1
        deployment.active_versions = {1: Mock(), 2: Mock()}
        deployment.traffic_distribution = {1: 0.0, 2: 1.0}

        # Check should trigger rollback
        assert deployment.check_security_rollback() is True

        # Execute rollback
        deployment.rollback()

        # All traffic should be on version 1
        assert deployment.traffic_distribution[1] == 1.0

    def test_queue_bounds_prevent_dos(self):
        """Test bounded queues prevent memory exhaustion."""
        queue = BoundedMessageQueue(max_size=3, ttl_seconds=3600)

        # Fill queue
        for i in range(3):
            envelope = Mock()
            assert queue.enqueue(envelope) is True

        # 4th message should be dropped
        assert queue.enqueue(Mock()) is False
        assert queue._dropped_count == 1

    def test_resource_exhaustion_detection(self):
        """Test resource exhaustion detection."""
        tracker = ResourceUsageTracker()

        # Simulate sustained high CPU
        for _ in range(15):
            tracker.record_cpu(95.0)

        alert = tracker.detect_exhaustion()
        assert alert is not None

    def test_behavioral_anomaly_detection(self):
        """Test behavioral anomaly detection."""
        detector = BehavioralAnomalyDetector()

        # Simulate action spike
        for _ in range(25):
            anomalies = detector.detect_anomalies('agent_001', 'access', 'file.txt')

        # Should detect spike
        assert len(anomalies) > 0

    def test_threat_pattern_persistence(self):
        """Test threat patterns persist correctly."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            db = ThreatPatternDatabase(db_path=f"{tmpdir}/patterns.json")

            db.save_pattern({
                'alert_type': 'dos_attack',
                'agent_id': 'malicious_001',
                'severity': 'CRITICAL'
            })

            # Query
            matches = db.query_similar('dos_attack')
            assert len(matches) == 1


class TestPhase5ComprehensiveSecurity:
    """Comprehensive tests combining all Phase 5 fixes."""

    def test_all_systems_integrated(self):
        """Test all security systems work together."""
        # Create components
        ams = AgentManagementSystem()
        bus = MessageBus(require_signatures=True)
        acc = AgentCommunicationChannel(enable_signature_verification=True)
        detector = BehavioralAnomalyDetector()

        # Issue credential
        cred = ams.issue_agent_credential('agent_001')

        # Create authenticated agent
        success = ams.create_agent(
            'agent_001',
            AgentType.INFRASTRUCTURAL,
            auth_token=cred.token,
            auth_timestamp=cred.timestamp
        )

        assert success is True

        # Send signed message
        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )

        msg_id = bus.send_message(message)
        assert bus.messages_signed > 0

        # Detect behavior
        anomalies = detector.detect_anomalies('agent_001', 'send_message', 'agent_002')
        # Should work without errors

    def test_statistics_from_all_components(self):
        """Test statistics gathering from all security components."""
        ams = AgentManagementSystem()
        bus = MessageBus()
        acc = AgentCommunicationChannel()

        # Get stats
        ams_stats = ams.get_statistics()
        bus_stats = bus.get_statistics()

        # Should include security metrics
        assert 'authentication' in ams_stats
        assert 'require_signatures' in bus_stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
