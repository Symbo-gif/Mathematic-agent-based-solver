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
Rainbow Deployment System
=========================

Gradual traffic shifting for zero-downtime deployments.

Phase 5 - Issue #5: Security rollback triggers added.

Features:
- Gradual traffic shifting (0% → 100%)
- Multiple version management
- Security-triggered automatic rollback
- Alert-based deployment safety
"""

import random
import logging
from typing import Dict, Optional, List

logger = logging.getLogger('symbo_agentic_reasoners.deployment.rainbow')


class RainbowDeployment:
    """
    Rainbow deployment system with security rollback.

    Manages gradual traffic shifting between versions with automatic
    rollback on security alerts (Phase 5 - Issue #5).
    """

    def __init__(self, orchestrator, security_monitor=None):
        """
        Initialize rainbow deployment.

        Args:
            orchestrator: Initial orchestrator instance
            security_monitor: Optional SecurityMonitor for rollback triggers (Issue #5)
        """
        self.orchestrator = orchestrator
        self.active_versions = {1: orchestrator}
        self.traffic_distribution = {1: 1.0}  # All traffic to version 1 initially
        self.new_version = None
        self.previous_version = None  # Track for rollback

        # Phase 5 - Issue #5: Security rollback integration
        self.security_monitor = security_monitor
        self.security_rollback_enabled = True
        self.alert_threshold = 3  # Rollback after 3 high-severity alerts in 5 minutes
        self.rollback_time_window = 300  # 5 minutes

        # Statistics
        self.deployments_count = 0
        self.rollbacks_count = 0
        self.security_rollbacks_count = 0
        
    def deploy_new_version(self, new_orchestrator):
        """
        Deploy a new version without disrupting active sessions.

        Phase 5 - Issue #5: Tracks previous version for rollback.

        Args:
            new_orchestrator: New orchestrator instance to deploy

        Returns:
            Version ID assigned to new deployment
        """
        version_id = max(self.active_versions.keys()) + 1
        self.new_version = new_orchestrator
        self.active_versions[version_id] = new_orchestrator

        # Track previous version for rollback (Issue #5)
        self.previous_version = max(k for k in self.active_versions.keys() if k < version_id)

        # Start with 0% traffic to new version
        self.traffic_distribution[version_id] = 0.0
        self.traffic_distribution[self.previous_version] = 1.0

        self.deployments_count += 1
        logger.info(f"Deployed version {version_id} (previous: {self.previous_version})")

        return version_id
        
    def check_security_rollback(self) -> bool:
        """
        Check if security conditions require rollback.

        Phase 5 - Issue #5: Checks security monitor for high-severity alerts.

        Returns:
            True if rollback needed based on security alerts
        """
        if not self.security_rollback_enabled or not self.security_monitor:
            return False

        try:
            # Get recent high-severity alerts from security monitor
            if hasattr(self.security_monitor, 'get_recent_alerts'):
                alerts = self.security_monitor.get_recent_alerts(
                    severity='HIGH',
                    time_window=self.rollback_time_window
                )

                if len(alerts) >= self.alert_threshold:
                    logger.warning(
                        f"Security rollback triggered: {len(alerts)} HIGH alerts "
                        f"in last {self.rollback_time_window}s (threshold: {self.alert_threshold})"
                    )
                    return True

            # Check for critical alerts (immediate rollback)
            if hasattr(self.security_monitor, 'get_recent_alerts'):
                critical_alerts = self.security_monitor.get_recent_alerts(
                    severity='CRITICAL',
                    time_window=60  # Last minute only
                )

                if len(critical_alerts) > 0:
                    logger.error(
                        f"Security rollback triggered: {len(critical_alerts)} CRITICAL alerts detected"
                    )
                    return True

        except Exception as e:
            logger.error(f"Security rollback check failed: {e}")

        return False

    def rollback(self) -> bool:
        """
        Emergency rollback to previous stable version.

        Phase 5 - Issue #5: Automated rollback on security alerts.

        Returns:
            True if rollback successful
        """
        if self.previous_version is None:
            logger.error("Rollback failed: No previous version available")
            return False

        if self.previous_version not in self.active_versions:
            logger.error(f"Rollback failed: Previous version {self.previous_version} not active")
            return False

        logger.warning(f"ROLLBACK INITIATED: Reverting to version {self.previous_version}")

        # Shift all traffic to previous version
        for version_id in list(self.traffic_distribution.keys()):
            if version_id == self.previous_version:
                self.traffic_distribution[version_id] = 1.0
            else:
                self.traffic_distribution[version_id] = 0.0

        self.rollbacks_count += 1
        self.security_rollbacks_count += 1

        logger.warning(f"ROLLBACK COMPLETE: All traffic on version {self.previous_version}")

        # Alert security monitor
        if self.security_monitor and hasattr(self.security_monitor, 'add_alert'):
            try:
                self.security_monitor.add_alert(
                    alert_type='deployment_rollback',
                    severity='HIGH',
                    message=f"Emergency rollback to version {self.previous_version}",
                    agent_id='rainbow_deployment'
                )
            except Exception:
                pass  # Best effort alert

        return True

    def shift_traffic(self, version_id, percentage):
        """
        Gradually shift traffic to new version.

        Phase 5 - Issue #5: Checks security before shifting traffic.

        Args:
            version_id: Target version for traffic
            percentage: Percentage of traffic to shift

        Returns:
            Updated traffic distribution dict

        Security:
            Checks for security alerts before allowing traffic shift.
            Automatically rolls back if threshold exceeded.
        """
        # Phase 5 - Issue #5: Security check before traffic shift
        if self.check_security_rollback():
            logger.error("Security rollback required - aborting traffic shift")
            self.rollback()
            return self.traffic_distribution

        if version_id not in self.active_versions:
            raise ValueError(f"Version {version_id} not deployed")

        # Calculate how much to reduce from current main version
        current_main = max(k for k, v in self.traffic_distribution.items() if v > 0)
        reduction = min(percentage, self.traffic_distribution[current_main])

        # Update distribution
        self.traffic_distribution[current_main] -= reduction
        self.traffic_distribution[version_id] += reduction

        logger.info(
            f"Traffic shifted: version {current_main} ({self.traffic_distribution[current_main]:.1%}) → "
            f"version {version_id} ({self.traffic_distribution[version_id]:.1%})"
        )

        return self.traffic_distribution
        
    def route_request(self, problem):
        """Route request based on current traffic distribution"""
        # Determine which version to use based on traffic distribution
        rand_val = random.random()
        cumulative = 0.0
        
        for version_id, percentage in self.traffic_distribution.items():
            cumulative += percentage
            if rand_val < cumulative:
                return self.active_versions[version_id].route_problem(problem)
                
        # Fallback to main version
        main_version = max(k for k, v in self.traffic_distribution.items() if v > 0)
        return self.active_versions[main_version].route_problem(problem)
        
    def complete_deployment(self, version_id):
        """Complete deployment by shifting all traffic to new version"""
        # First shift remaining traffic
        self.shift_traffic(version_id, 1.0)
        
        # Remove old versions (keeping previous version for rollback)
        versions_to_remove = [
            v for v in self.active_versions.keys() 
            if v < version_id - 1
        ]
        
        for version in versions_to_remove:
            del self.active_versions[version]
            del self.traffic_distribution[version]

        logger.info(f"Deployment completed: removed {len(versions_to_remove)} old versions")

        return len(versions_to_remove)

    def get_statistics(self) -> Dict[str, any]:
        """
        Get deployment statistics.

        Phase 5 - Issue #5: Includes rollback metrics.

        Returns:
            Dictionary with deployment and security statistics
        """
        return {
            'active_versions': len(self.active_versions),
            'current_version': max(self.active_versions.keys()),
            'previous_version': self.previous_version,
            'traffic_distribution': dict(self.traffic_distribution),
            'deployments_count': self.deployments_count,
            'rollbacks_count': self.rollbacks_count,
            'security_rollbacks_count': self.security_rollbacks_count,
            'security_rollback_enabled': self.security_rollback_enabled,
            'alert_threshold': self.alert_threshold,
            'security_monitor_enabled': self.security_monitor is not None,
        }