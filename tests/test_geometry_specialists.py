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
Geometry Specialist Tests
=========================

Comprehensive tests for geometry specialist agents:
- AnalyticGeometrySpecialist
- EuclideanSpecialist
- TransformationSpecialist
- TrigonometrySpecialist
"""

import pytest
from unittest.mock import Mock, MagicMock


# =============================================================================
# AnalyticGeometrySpecialist Tests
# =============================================================================


class TestAnalyticGeometrySpecialist:
    """Tests for AnalyticGeometrySpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create AnalyticGeometrySpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.geometry.analytic_specialist import (
            AnalyticGeometrySpecialist
        )
        return AnalyticGeometrySpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# EuclideanSpecialist Tests
# =============================================================================


class TestEuclideanGeometrySpecialist:
    """Tests for EuclideanGeometrySpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create EuclideanGeometrySpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.geometry.euclidean_specialist import (
            EuclideanGeometrySpecialist
        )
        return EuclideanGeometrySpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# TransformationSpecialist Tests
# =============================================================================


class TestTransformationSpecialist:
    """Tests for TransformationSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create TransformationSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.geometry.transformation_specialist import (
            TransformationSpecialist
        )
        return TransformationSpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# TrigonometrySpecialist Tests
# =============================================================================


class TestTrigonometrySpecialist:
    """Tests for TrigonometrySpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create TrigonometrySpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.geometry.trigonometry_specialist import (
            TrigonometrySpecialist
        )
        return TrigonometrySpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
