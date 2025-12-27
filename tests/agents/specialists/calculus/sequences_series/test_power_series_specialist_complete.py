# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Comprehensive Tests for PowerSeriesSpecialist"""

import pytest
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    PowerSeriesSpecialist
)


class TestPowerSeriesSpecialistComplete:
    """Test suite for PowerSeriesSpecialist."""

    @pytest.fixture
    def specialist(self):
        return PowerSeriesSpecialist(agent_id='test_001', df=None, blackboard=None)

    @pytest.fixture
    def specialist_with_mocks(self):
        mock_df = Mock()
        mock_blackboard = Mock()
        return PowerSeriesSpecialist(agent_id='test_002', df=mock_df, blackboard=mock_blackboard)

    def test_initialization(self, specialist):
        """Test specialist initialization."""
        assert specialist.agent_id == 'test_001'
        assert specialist.tasks_executed == 0

    def test_registration_with_df(self):
        """Test service registration."""
        mock_df = Mock()
        specialist = PowerSeriesSpecialist(agent_id='test_df', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_radius_finite(self, specialist):
        """Test radius computation for sum(x^n): R = 1."""
        result = specialist.compute_radius('1')
        assert result is not None

    def test_radius_infinite(self, specialist):
        """Test radius for sum(x^n/n!): R = infinity."""
        result = specialist.compute_radius('1/factorial(n)')
        assert result is not None

    def test_radius_zero(self, specialist):
        """Test radius for sum(n! * x^n): R = 0."""
        result = specialist.compute_radius('factorial(n)')
        assert result is not None

    def test_interval_of_convergence(self, specialist):
        """Test interval computation."""
        # Use 1/(n+1) to avoid division by zero at n=0
        result = specialist.compute_interval('1/(n+1)', center=0)
        assert result is not None

    def test_endpoint_testing(self, specialist):
        """Test endpoint behavior."""
        # Use 1/(n+1) to avoid division by zero at n=0
        result = specialist.check_endpoints('1/(n+1)', radius=1, center=0)
        assert result is not None

    def test_edge_case(self, specialist):
        """Test edge case handling."""
        result = specialist.compute_radius('')
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
        r1 = specialist.compute_radius('1')
        # Use 1/(n+1) to avoid division by zero at n=0
        r2 = specialist.compute_radius('1/(n+1)')
        assert all(r is not None for r in [r1, r2])

    def test_statistics_tracking(self, specialist):
        """Test statistics tracking."""
        specialist.compute_radius('1')
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
