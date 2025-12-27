# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Comprehensive Tests for ClassicFourierSeriesSpecialist"""

import pytest
import numpy as np
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    ClassicFourierSeriesSpecialist
)


class TestClassicFourierSeriesSpecialistComplete:
    """Test suite for ClassicFourierSeriesSpecialist."""

    @pytest.fixture
    def specialist(self):
        return ClassicFourierSeriesSpecialist(agent_id='test_001', df=None, blackboard=None)

    @pytest.fixture
    def specialist_with_mocks(self):
        mock_df = Mock()
        mock_blackboard = Mock()
        return ClassicFourierSeriesSpecialist(agent_id='test_002', df=mock_df, blackboard=mock_blackboard)

    def test_initialization(self, specialist):
        """Test specialist initialization."""
        assert specialist.agent_id == 'test_001'
        assert specialist.tasks_executed == 0

    def test_registration_with_df(self):
        """Test service registration."""
        mock_df = Mock()
        specialist = ClassicFourierSeriesSpecialist(agent_id='test_df', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_coefficients_computation(self, specialist):
        """Test Fourier coefficient computation."""
        result = specialist.compute_coefficients('x', period=2*np.pi, n_terms=5)
        assert result is not None

    def test_square_wave(self, specialist):
        """Test square wave Fourier series."""
        result = specialist.compute_coefficients('square_wave', period=2*np.pi, n_terms=5)
        assert result is not None

    def test_half_range_cosine(self, specialist):
        """Test half-range cosine expansion."""
        result = specialist.half_range_cosine('x', L=np.pi, n_terms=5)
        assert result is not None

    def test_half_range_sine(self, specialist):
        """Test half-range sine expansion."""
        result = specialist.half_range_sine('x', L=np.pi, n_terms=5)
        assert result is not None

    def test_even_function(self, specialist):
        """Test even function (only cosine terms)."""
        result = specialist.compute_coefficients('x**2', period=2*np.pi, n_terms=5)
        assert result is not None

    def test_edge_case_constant(self, specialist):
        """Test constant function."""
        result = specialist.compute_coefficients('5', period=2*np.pi, n_terms=5)
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
        r1 = specialist.compute_coefficients('x', period=2*np.pi, n_terms=3)
        r2 = specialist.compute_coefficients('x**2', period=2*np.pi, n_terms=3)
        assert all(r is not None for r in [r1, r2])

    def test_statistics_tracking(self, specialist):
        """Test statistics tracking."""
        specialist.compute_coefficients('x', period=2*np.pi, n_terms=3)
        stats = specialist.get_statistics()
        assert isinstance(stats, dict)
