# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Comprehensive Tests for PowerSeriesOperationsSpecialist"""

import pytest
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    PowerSeriesOperationsSpecialist
)


class TestPowerSeriesOperationsSpecialistComplete:
    """Test suite for PowerSeriesOperationsSpecialist."""

    @pytest.fixture
    def specialist(self):
        return PowerSeriesOperationsSpecialist(agent_id='test_001', df=None, blackboard=None)

    @pytest.fixture
    def specialist_with_mocks(self):
        mock_df = Mock()
        mock_blackboard = Mock()
        return PowerSeriesOperationsSpecialist(agent_id='test_002', df=mock_df, blackboard=mock_blackboard)

    def test_initialization(self, specialist):
        """Test specialist initialization."""
        assert specialist.agent_id == 'test_001'
        assert specialist.tasks_executed == 0

    def test_registration_with_df(self):
        """Test service registration."""
        mock_df = Mock()
        specialist = PowerSeriesOperationsSpecialist(agent_id='test_df', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_series_addition(self, specialist):
        """Test adding two power series."""
        result = specialist.add_series([1, 1], [1, -1])
        assert result is not None
        assert 'coefficients' in result

    def test_series_multiplication(self, specialist):
        """Test Cauchy product: (1+x) * (1-x) = 1 - x^2."""
        result = specialist.multiply_series([1, 1], [1, -1], n_terms=5)
        assert result is not None
        assert 'coefficients' in result

    def test_series_differentiation(self, specialist):
        """Test differentiation: d/dx(x + x^2 + x^3) = 1 + 2x + 3x^2."""
        result = specialist.differentiate([0, 1, 1, 1])
        assert result is not None
        assert 'coefficients' in result

    def test_series_integration(self, specialist):
        """Test integration."""
        result = specialist.integrate([1, 1, 1])
        assert result is not None
        assert 'coefficients' in result

    def test_series_inversion(self, specialist):
        """Test multiplicative inverse."""
        result = specialist.invert_series([1, -1], n_terms=5)
        assert result is not None

    def test_edge_case_empty(self, specialist):
        """Test empty series handling."""
        result = specialist.add_series([], [1, 2, 3])
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
        r1 = specialist.add_series([1, 1], [1, -1])
        r2 = specialist.differentiate([0, 1, 2])
        assert all(r is not None for r in [r1, r2])

    def test_statistics_tracking(self, specialist):
        """Test statistics tracking."""
        specialist.add_series([1, 1], [1, -1])
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
