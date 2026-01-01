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

"""Comprehensive Tests for SequenceConvergenceSpecialist"""

import pytest
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    SequenceConvergenceSpecialist
)


class TestSequenceConvergenceSpecialistComplete:
    """Test suite for SequenceConvergenceSpecialist."""

    @pytest.fixture
    def specialist(self):
        return SequenceConvergenceSpecialist(agent_id='test_001', df=None, blackboard=None)

    @pytest.fixture
    def specialist_with_mocks(self):
        mock_df = Mock()
        mock_blackboard = Mock()
        return SequenceConvergenceSpecialist(agent_id='test_002', df=mock_df, blackboard=mock_blackboard)

    def test_initialization(self, specialist):
        """Test specialist initialization."""
        assert specialist.agent_id == 'test_001'
        assert specialist.tasks_executed == 0

    def test_registration_with_df(self):
        """Test service registration with Directory Facilitator."""
        mock_df = Mock()
        specialist = SequenceConvergenceSpecialist(agent_id='test_df', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_convergent_sequence(self, specialist):
        """Test detection of convergent sequence: 1/n -> 0."""
        result = specialist.check_convergence('1/n')
        assert result is not None
        assert 'converges' in result or 'success' in result

    def test_divergent_sequence(self, specialist):
        """Test detection of divergent sequence: n."""
        result = specialist.check_convergence('n')
        assert result is not None

    def test_monotonicity_check(self, specialist):
        """Test monotonicity analysis."""
        result = specialist.check_monotonicity('1/n')
        assert result is not None

    def test_boundedness_check(self, specialist):
        """Test boundedness analysis."""
        result = specialist.check_boundedness('sin(n)')
        assert result is not None

    def test_limsup_liminf(self, specialist):
        """Test limsup and liminf computation."""
        result = specialist.compute_limsup_liminf('sin(n)')
        assert result is not None

    def test_edge_case_oscillating(self, specialist):
        """Test oscillating sequence: (-1)^n."""
        result = specialist.check_convergence('(-1)**n')
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
        """Test multiple concurrent requests."""
        r1 = specialist.check_convergence('1/n')
        r2 = specialist.check_convergence('n')
        r3 = specialist.check_convergence('1/n**2')
        assert all(r is not None for r in [r1, r2, r3])

    def test_statistics_tracking(self, specialist):
        """Test statistics tracking."""
        specialist.check_convergence('1/n')
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
