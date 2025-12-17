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
Tests for Rainbow Deployment Module
====================================

Comprehensive tests for the rainbow deployment traffic shifting module.
"""

import pytest
from unittest.mock import Mock, patch


class TestRainbowDeployment:
    """Tests for RainbowDeployment class."""

    def test_init(self):
        """Test RainbowDeployment initialization."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)
        assert rd.orchestrator is orchestrator
        assert rd.active_versions == {1: orchestrator}
        assert rd.traffic_distribution == {1: 1.0}
        assert rd.new_version is None

    def test_deploy_new_version(self):
        """Test deploying a new version."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        new_orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        version_id = rd.deploy_new_version(new_orchestrator)

        assert version_id == 2
        assert rd.new_version is new_orchestrator
        assert version_id in rd.active_versions
        assert rd.active_versions[version_id] is new_orchestrator
        assert rd.traffic_distribution[version_id] == 0.0

    def test_deploy_multiple_versions(self):
        """Test deploying multiple versions."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        # Deploy version 2
        v2 = rd.deploy_new_version(Mock())
        assert v2 == 2

        # Deploy version 3
        v3 = rd.deploy_new_version(Mock())
        assert v3 == 3

        assert len(rd.active_versions) == 3

    def test_shift_traffic_valid(self):
        """Test shifting traffic to a deployed version."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        new_orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        version_id = rd.deploy_new_version(new_orchestrator)
        distribution = rd.shift_traffic(version_id, 0.2)

        assert distribution[version_id] == 0.2
        assert distribution[1] == 0.8

    def test_shift_traffic_incremental(self):
        """Test shifting traffic incrementally."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        version_id = rd.deploy_new_version(Mock())

        # First shift works correctly
        rd.shift_traffic(version_id, 0.3)
        assert rd.traffic_distribution[version_id] == 0.3
        assert rd.traffic_distribution[1] == 0.7

    def test_shift_traffic_full_transition(self):
        """Test shifting all traffic in one go."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        version_id = rd.deploy_new_version(Mock())

        # Shift all traffic at once
        rd.shift_traffic(version_id, 1.0)
        assert rd.traffic_distribution[version_id] == 1.0
        assert rd.traffic_distribution[1] == 0.0

    def test_shift_traffic_invalid_version(self):
        """Test shifting traffic to non-existent version raises error."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        with pytest.raises(ValueError, match="not deployed"):
            rd.shift_traffic(999, 0.5)

    def test_shift_traffic_cap_at_available(self):
        """Test that traffic shift is capped at available traffic."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        version_id = rd.deploy_new_version(Mock())

        # Try to shift more than available (100%)
        rd.shift_traffic(version_id, 1.5)

        # Should cap at 1.0
        assert rd.traffic_distribution[version_id] == 1.0
        assert rd.traffic_distribution[1] == 0.0

    @patch('symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment.random')
    def test_route_request_to_main(self, mock_random):
        """Test routing request to main version."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        orchestrator.route_problem = Mock(return_value="result1")
        rd = RainbowDeployment(orchestrator)

        mock_random.random.return_value = 0.5

        result = rd.route_request("problem")
        assert result == "result1"
        orchestrator.route_problem.assert_called_once_with("problem")

    @patch('symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment.random')
    def test_route_request_to_new_version(self, mock_random):
        """Test routing request to new version based on traffic distribution."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        orchestrator.route_problem = Mock(return_value="old_result")
        new_orchestrator = Mock()
        new_orchestrator.route_problem = Mock(return_value="new_result")

        rd = RainbowDeployment(orchestrator)
        version_id = rd.deploy_new_version(new_orchestrator)
        rd.shift_traffic(version_id, 0.8)  # 80% to new version

        # Low random value should hit the old version (20%)
        mock_random.random.return_value = 0.1
        result = rd.route_request("problem")
        assert result == "old_result"

        # High random value should hit new version (80%)
        mock_random.random.return_value = 0.9
        result = rd.route_request("problem")
        assert result == "new_result"

    @patch('symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment.random')
    def test_route_request_fallback(self, mock_random):
        """Test route request fallback to main version."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        orchestrator.route_problem = Mock(return_value="fallback_result")
        rd = RainbowDeployment(orchestrator)

        # Random value at exactly 1.0 (edge case)
        mock_random.random.return_value = 1.0

        result = rd.route_request("problem")
        assert result == "fallback_result"

    def test_complete_deployment(self):
        """Test completing a deployment."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        # Deploy new version
        version_id = rd.deploy_new_version(Mock())

        # Complete deployment
        removed_count = rd.complete_deployment(version_id)

        # Version 1 is kept for rollback, so nothing removed
        assert removed_count == 0
        assert rd.traffic_distribution[version_id] == 1.0

    def test_complete_deployment_removes_old_versions(self):
        """Test that complete deployment removes old versions."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        # Deploy multiple versions
        v2 = rd.deploy_new_version(Mock())
        v3 = rd.deploy_new_version(Mock())
        v4 = rd.deploy_new_version(Mock())

        # Complete deployment to version 4
        removed_count = rd.complete_deployment(v4)

        # Versions 1 and 2 should be removed (keeping v3 for rollback)
        assert removed_count == 2
        assert 1 not in rd.active_versions
        assert 2 not in rd.active_versions
        assert 3 in rd.active_versions  # Kept for rollback
        assert 4 in rd.active_versions


class TestRainbowDeploymentEdgeCases:
    """Edge case tests for RainbowDeployment."""

    def test_zero_traffic_shift(self):
        """Test shifting zero traffic."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        version_id = rd.deploy_new_version(Mock())
        initial_dist = rd.traffic_distribution.copy()

        rd.shift_traffic(version_id, 0.0)

        # Distribution should be unchanged
        assert rd.traffic_distribution[1] == initial_dist[1]

    def test_full_traffic_shift(self):
        """Test shifting all traffic at once."""
        from symbo_agentic_reasoners.infrastructure.deployment.rainbow_deployment import (
            RainbowDeployment
        )
        orchestrator = Mock()
        rd = RainbowDeployment(orchestrator)

        version_id = rd.deploy_new_version(Mock())
        rd.shift_traffic(version_id, 1.0)

        assert rd.traffic_distribution[version_id] == 1.0
        assert rd.traffic_distribution[1] == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
