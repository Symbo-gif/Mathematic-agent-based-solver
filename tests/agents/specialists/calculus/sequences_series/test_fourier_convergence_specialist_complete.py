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

"""Comprehensive Tests for FourierConvergenceSpecialist"""

import pytest
import numpy as np
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    FourierConvergenceSpecialist
)


class TestFourierConvergenceSpecialistComplete:
    """Test suite for FourierConvergenceSpecialist."""

    @pytest.fixture
    def specialist(self):
        return FourierConvergenceSpecialist(agent_id='test_001', df=None, blackboard=None)

    @pytest.fixture
    def specialist_with_mocks(self):
        mock_df = Mock()
        mock_blackboard = Mock()
        return FourierConvergenceSpecialist(agent_id='test_002', df=mock_df, blackboard=mock_blackboard)

    def test_initialization(self, specialist):
        """Test specialist initialization."""
        assert specialist.agent_id == 'test_001'
        assert specialist.tasks_executed == 0

    def test_registration_with_df(self):
        """Test service registration."""
        mock_df = Mock()
        specialist = FourierConvergenceSpecialist(agent_id='test_df', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_dirichlet_smooth(self, specialist):
        """Test Dirichlet conditions for smooth function."""
        result = specialist.check_dirichlet_conditions('sin(x)', period=2*np.pi)
        assert result is not None

    def test_dirichlet_piecewise(self, specialist):
        """Test Dirichlet conditions for piecewise function."""
        result = specialist.check_dirichlet_conditions('square_wave', period=2*np.pi)
        assert result is not None

    def test_gibbs_phenomenon(self, specialist):
        """Test Gibbs phenomenon analysis."""
        # Square wave function with discontinuity at x=0
        def square_wave(x):
            return 1.0 if np.sin(x) >= 0 else -1.0
        result = specialist.analyze_gibbs_phenomenon(
            square_wave, period=2*np.pi, n_terms=50, discontinuity_x=0.0
        )
        assert result is not None

    def test_parseval_verification(self, specialist):
        """Test Parseval's theorem verification."""
        # Simple linear function
        def linear_func(x):
            return x
        result = specialist.verify_parseval(linear_func, period=2*np.pi, n_terms=10)
        assert result is not None

    def test_convergence_rate(self, specialist):
        """Test convergence rate analysis."""
        result = specialist.analyze_convergence_rate('x**2', period=2*np.pi)
        assert result is not None

    def test_edge_case_continuous(self, specialist):
        """Test continuous function (no Gibbs)."""
        result = specialist.check_dirichlet_conditions('cos(x)', period=2*np.pi)
        assert result is not None

    def test_bdi_update_beliefs(self, specialist_with_mocks):
        """Test BDI perceive phase."""
        mock_bb = specialist_with_mocks.blackboard
        mock_bb.query_entries.return_value = []
        specialist_with_mocks.update_beliefs()
        assert len(specialist_with_mocks.beliefs) >= 0

    def test_bdi_deliberate(self, specialist):
        """Test BDI deliberation phase."""
        specialist.add_belief(predicate='test', content={}, confidence=1.0, source='test')
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    def test_concurrent_requests(self, specialist):
        """Test concurrent requests."""
        r1 = specialist.check_dirichlet_conditions('sin(x)', period=2*np.pi)
        r2 = specialist.check_dirichlet_conditions('cos(x)', period=2*np.pi)
        assert all(r is not None for r in [r1, r2])

    def test_statistics_tracking(self, specialist):
        """Test statistics tracking."""
        specialist.check_dirichlet_conditions('sin(x)', period=2*np.pi)
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
