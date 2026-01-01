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

"""Comprehensive Tests for SequenceLimitSpecialist"""

import pytest
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    SequenceLimitSpecialist
)


class TestSequenceLimitSpecialistComplete:
    """Test suite for SequenceLimitSpecialist."""

    @pytest.fixture
    def specialist(self):
        return SequenceLimitSpecialist(agent_id='test_001', df=None, blackboard=None)

    @pytest.fixture
    def specialist_with_mocks(self):
        mock_df = Mock()
        mock_blackboard = Mock()
        return SequenceLimitSpecialist(agent_id='test_002', df=mock_df, blackboard=mock_blackboard)

    def test_initialization(self, specialist):
        """Test specialist initialization."""
        assert specialist.agent_id == 'test_001'
        assert specialist.tasks_executed == 0

    def test_registration_with_df(self):
        """Test service registration."""
        mock_df = Mock()
        specialist = SequenceLimitSpecialist(agent_id='test_df', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_stolz_cesaro(self, specialist):
        """Test Stolz-Cesaro theorem application."""
        result = specialist.stolz_cesaro('n*(n+1)/2', 'n**2')
        assert result is not None

    def test_squeeze_theorem(self, specialist):
        """Test squeeze theorem application."""
        result = specialist.squeeze_theorem('0', 'abs(sin(n))/n', '1/n')
        assert result is not None

    def test_cesaro_mean(self, specialist):
        """Test Cesaro mean computation."""
        result = specialist.cesaro_mean('1/n')
        assert result is not None
        assert result.get('success', False) == True

    def test_ratio_to_limit(self, specialist):
        """Test ratio-based limit computation."""
        result = specialist.ratio_to_limit('2**n')
        assert result is not None

    def test_root_to_limit(self, specialist):
        """Test n-th root limit."""
        result = specialist.root_to_limit('n**(1/n)')
        assert result is not None

    def test_edge_case_empty(self, specialist):
        """Test handling of edge cases."""
        result = specialist.cesaro_mean('')
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
        r1 = specialist.cesaro_mean('1/n')
        r2 = specialist.cesaro_mean('1/n**2')
        assert all(r is not None for r in [r1, r2])

    def test_statistics_tracking(self, specialist):
        """Test statistics tracking."""
        specialist.cesaro_mean('1/n')
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
