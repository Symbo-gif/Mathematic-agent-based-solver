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
Calculus Specialist Tests
=========================

Comprehensive tests for calculus specialist agents:
- SeriesSpecialist
- IntegrationSpecialist
- LimitEvaluator
- ODESolver
- DifferentiationSpecialist
"""

import pytest
import sympy as sp


# =============================================================================
# SeriesSpecialist Tests
# =============================================================================


class TestSeriesSpecialist:
    """Tests for SeriesSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create SeriesSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.calculus.series_specialist import (
            SeriesSpecialist
        )
        return SeriesSpecialist()

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
# IntegrationSpecialist Tests
# =============================================================================


class TestIntegrationSpecialist:
    """Tests for IntegrationSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create IntegrationSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import (
            IntegrationSpecialist
        )
        return IntegrationSpecialist()

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
# LimitEvaluator Tests
# =============================================================================


class TestLimitEvaluator:
    """Tests for LimitEvaluator."""

    @pytest.fixture
    def specialist(self):
        """Create LimitEvaluator instance."""
        from symbo_agentic_reasoners.agents.specialists.calculus.limit_evaluator import (
            LimitEvaluator
        )
        return LimitEvaluator()

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


class TestLimitEnums:
    """Tests for limit-related enums and data classes."""

    def test_limit_direction_enum(self):
        """LimitDirection enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.calculus.limit_evaluator import (
            LimitDirection
        )
        # Check it's an enum
        assert LimitDirection is not None
        assert len(list(LimitDirection)) > 0

    def test_indeterminate_form_enum(self):
        """IndeterminateForm enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.calculus.limit_evaluator import (
            IndeterminateForm
        )
        assert IndeterminateForm is not None
        assert len(list(IndeterminateForm)) > 0

    def test_lhopital_step_exists(self):
        """LHopitalStep class should exist."""
        from symbo_agentic_reasoners.agents.specialists.calculus.limit_evaluator import (
            LHopitalStep
        )
        assert LHopitalStep is not None

    def test_limit_result_exists(self):
        """LimitResult class should exist."""
        from symbo_agentic_reasoners.agents.specialists.calculus.limit_evaluator import (
            LimitResult
        )
        assert LimitResult is not None


# =============================================================================
# ODESolver Tests
# =============================================================================


class TestODESolver:
    """Tests for ODESolver."""

    @pytest.fixture
    def specialist(self):
        """Create ODESolver instance."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        return ODESolver()

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
# DifferentiationSpecialist Tests
# =============================================================================


class TestDifferentiationSpecialist:
    """Tests for DifferentiationSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create DifferentiationSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import (
            DifferentiationSpecialist
        )
        return DifferentiationSpecialist()

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
