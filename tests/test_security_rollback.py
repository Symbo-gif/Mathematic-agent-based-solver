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
Security Rollback Tests
=======================

Phase 5 - Issue #5: Security rollback trigger tests.

Tests automatic deployment rollback on security alerts.
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import RainbowDeployment


class TestSecurityRollback:
    """Test security-triggered rollback functionality."""

    def test_rollback_on_high_severity_alerts(self):
        """Test rollback triggers on multiple HIGH alerts."""
        # Create mock security monitor
        security_monitor = Mock()
        security_monitor.get_recent_alerts = Mock(return_value=[
            {'severity': 'HIGH', 'type': 'attack1'},
            {'severity': 'HIGH', 'type': 'attack2'},
            {'severity': 'HIGH', 'type': 'attack3'},
        ])

        deployment = RainbowDeployment(Mock(), security_monitor=security_monitor)
        deployment.previous_version = 1
        deployment.active_versions[2] = Mock()

        # Should trigger rollback
        assert deployment.check_security_rollback() is True

    def test_rollback_on_critical_alert(self):
        """Test immediate rollback on CRITICAL alert."""
        security_monitor = Mock()
        security_monitor.get_recent_alerts = Mock(side_effect=lambda severity, time_window: [
            {'severity': 'CRITICAL', 'type': 'critical_attack'}
        ] if severity == 'CRITICAL' else [])

        deployment = RainbowDeployment(Mock(), security_monitor=security_monitor)
        deployment.previous_version = 1

        # Should trigger rollback immediately
        assert deployment.check_security_rollback() is True

    def test_no_rollback_below_threshold(self):
        """Test no rollback when alerts below threshold."""
        security_monitor = Mock()
        security_monitor.get_recent_alerts = Mock(return_value=[
            {'severity': 'HIGH', 'type': 'alert1'},
        ])

        deployment = RainbowDeployment(Mock(), security_monitor=security_monitor)

        # Should not trigger (only 1 alert, threshold is 3)
        assert deployment.check_security_rollback() is False

    def test_rollback_execution(self):
        """Test rollback shifts all traffic to previous version."""
        deployment = RainbowDeployment(Mock())
        deployment.active_versions = {1: Mock(), 2: Mock()}
        deployment.traffic_distribution = {1: 0.3, 2: 0.7}
        deployment.previous_version = 1

        # Execute rollback
        result = deployment.rollback()

        assert result is True
        assert deployment.traffic_distribution[1] == 1.0
        assert deployment.traffic_distribution[2] == 0.0
        assert deployment.rollbacks_count == 1
        assert deployment.security_rollbacks_count == 1

    def test_shift_traffic_checks_security(self):
        """Test shift_traffic checks security before proceeding."""
        security_monitor = Mock()
        security_monitor.get_recent_alerts = Mock(return_value=[
            {'severity': 'HIGH'} for _ in range(3)
        ])

        deployment = RainbowDeployment(Mock(), security_monitor=security_monitor)
        deployment.active_versions = {1: Mock(), 2: Mock()}
        deployment.traffic_distribution = {1: 1.0, 2: 0.0}
        deployment.previous_version = 1

        # Should abort shift and rollback
        result = deployment.shift_traffic(2, 0.5)

        # Should remain at version 1
        assert deployment.traffic_distribution[1] == 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
