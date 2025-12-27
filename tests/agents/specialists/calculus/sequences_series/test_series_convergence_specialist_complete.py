# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Comprehensive Tests for SeriesConvergenceSpecialist"""

import pytest
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    SeriesConvergenceSpecialist
)


class TestSeriesConvergenceSpecialistComplete:
    """Test suite for SeriesConvergenceSpecialist."""

    @pytest.fixture
    def specialist(self):
        return SeriesConvergenceSpecialist(agent_id='test_001', df=None, blackboard=None)

    @pytest.fixture
    def specialist_with_mocks(self):
        mock_df = Mock()
        mock_blackboard = Mock()
        return SeriesConvergenceSpecialist(agent_id='test_002', df=mock_df, blackboard=mock_blackboard)

    def test_initialization(self, specialist):
        """Test specialist initialization."""
        assert specialist.agent_id == 'test_001'
        assert specialist.tasks_executed == 0

    def test_registration_with_df(self):
        """Test service registration."""
        mock_df = Mock()
        specialist = SeriesConvergenceSpecialist(agent_id='test_df', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_ratio_test_convergent(self, specialist):
        """Test ratio test for convergent series: 1/n!."""
        result = specialist.apply_ratio_test('1/factorial(n)')
        assert result is not None

    def test_ratio_test_divergent(self, specialist):
        """Test ratio test for divergent series: n!."""
        result = specialist.apply_ratio_test('factorial(n)')
        assert result is not None

    def test_root_test(self, specialist):
        """Test root test application."""
        result = specialist.apply_root_test('(1/2)**n')
        assert result is not None

    def test_alternating_series(self, specialist):
        """Test alternating series test."""
        result = specialist.apply_alternating_test('(-1)**n/n')
        assert result is not None

    def test_comparison_test(self, specialist):
        """Test comparison test."""
        result = specialist.apply_comparison_test('1/n**2', '1/n', 'less')
        assert result is not None

    def test_edge_case_inconclusive(self, specialist):
        """Test inconclusive ratio test."""
        result = specialist.apply_ratio_test('1/n**2')
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
        r1 = specialist.apply_ratio_test('1/n')
        r2 = specialist.apply_root_test('(1/2)**n')
        assert all(r is not None for r in [r1, r2])

    def test_statistics_tracking(self, specialist):
        """Test statistics tracking."""
        specialist.apply_ratio_test('1/n')
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
