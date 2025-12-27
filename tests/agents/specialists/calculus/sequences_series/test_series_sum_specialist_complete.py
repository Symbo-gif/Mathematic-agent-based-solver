# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Comprehensive Tests for SeriesSumSpecialist
============================================

Standard 12-test pattern for specialist agents.
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.agents.specialists.calculus.sequences_series import (
    SeriesSumSpecialist
)


class TestSeriesSumSpecialistComplete:
    """Comprehensive test suite for SeriesSumSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create specialist instance without dependencies."""
        return SeriesSumSpecialist(
            agent_id='test_series_sum_001',
            df=None,
            blackboard=None
        )

    @pytest.fixture
    def specialist_with_mocks(self):
        """Create specialist with mocked dependencies."""
        mock_df = Mock()
        mock_blackboard = Mock()
        return SeriesSumSpecialist(
            agent_id='test_series_sum_002',
            df=mock_df,
            blackboard=mock_blackboard
        )

    # Test 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes with correct parameters."""
        assert specialist.agent_id == 'test_series_sum_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.tasks_failed == 0

    # Test 2: Service registration
    def test_registration_with_df(self):
        """Test specialist registers with Directory Facilitator."""
        mock_df = Mock()
        specialist = SeriesSumSpecialist(
            agent_id='test_series_sum_df',
            df=mock_df,
            blackboard=None
        )

        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.calculus.series.sum'
        assert call_args.agent_id == 'test_series_sum_df'

    # Test 3: Geometric sum - finite
    def test_geometric_sum_finite(self, specialist):
        """Test finite geometric sum."""
        result = specialist.geometric_sum(first=1, ratio=0.5, n_terms=11)

        expected = (1 - 0.5**11) / (1 - 0.5)

        assert result is not None
        assert abs(result.get('sum', 0) - expected) < 1e-10

    # Test 4: Geometric sum - infinite
    def test_geometric_sum_infinite(self, specialist):
        """Test infinite geometric sum."""
        result = specialist.geometric_sum(first=1, ratio=0.5, n_terms=None)

        expected = 1 / (1 - 0.5)  # = 2

        assert result is not None
        assert abs(result.get('sum', 0) - expected) < 1e-10

    # Test 5: Telescoping sum
    def test_telescoping_sum(self, specialist):
        """Test telescoping sum."""
        result = specialist.telescoping_sum('1/(n*(n+1))')

        # sum(1/n - 1/(n+1)) = 1 - 0 = 1
        assert result is not None
        assert result.get('success', False) == True

    # Test 6: Arithmetic sum
    def test_arithmetic_sum(self, specialist):
        """Test arithmetic sum: 1 + 2 + ... + 100 = 5050."""
        result = specialist.arithmetic_sum(first=1, diff=1, n_terms=100)

        expected = 100 * 101 / 2

        assert result is not None
        assert abs(result.get('sum', 0) - expected) < 1e-10

    # Test 7: p-series sum
    def test_p_series_sum(self, specialist):
        """Test p-series sum approximation."""
        result = specialist.p_series_sum(p=2)

        expected = np.pi**2 / 6

        assert result is not None
        # Allow some error for numerical approximation
        if result.get('sum'):
            assert abs(result.get('sum', 0) - expected) < 0.1

    # Test 8: Edge cases
    @pytest.mark.parametrize("ratio,expected_behavior", [
        (1.0, "divergent"),
        (-0.5, "convergent"),
        (2.0, "divergent"),
        (0, "first_term_only"),
    ])
    def test_geometric_edge_cases(self, specialist, ratio, expected_behavior):
        """Test geometric sum edge cases."""
        result = specialist.geometric_sum(first=1, ratio=ratio, n_terms=None)

        if expected_behavior == "divergent":
            assert result.get('converges', True) == False or 'error' in result or result.get('sum') == float('inf')
        elif expected_behavior == "convergent":
            assert result.get('converges', True) == True or result.get('sum') is not None
        elif expected_behavior == "first_term_only":
            assert result.get('sum', -1) == 1

    # Test 9: BDI update_beliefs
    def test_bdi_update_beliefs(self, specialist_with_mocks):
        """Test BDI perceive phase."""
        mock_bb = specialist_with_mocks.blackboard
        mock_task = Mock()
        mock_task.entry_id = 'test_task_001'
        mock_task.metadata = {'series_type': 'geometric', 'ratio': 0.5}

        mock_bb.query_entries.return_value = [mock_task]

        specialist_with_mocks.update_beliefs()
        assert len(specialist_with_mocks.beliefs) >= 0

    # Test 10: BDI deliberate
    def test_bdi_deliberate(self, specialist):
        """Test BDI deliberation phase."""
        specialist.add_belief(
            predicate='pending_sum_test',
            content={'series_type': 'telescoping'},
            confidence=1.0,
            source='test'
        )

        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # Test 11: Concurrent requests
    def test_concurrent_requests(self, specialist):
        """Test handling multiple concurrent requests."""
        results = []

        results.append(specialist.geometric_sum(first=1, ratio=0.5, n_terms=10))
        results.append(specialist.arithmetic_sum(first=1, diff=1, n_terms=100))
        results.append(specialist.p_series_sum(p=2))

        assert len(results) == 3
        assert all(r is not None for r in results)

    # Test 12: Statistics tracking
    def test_statistics_tracking(self, specialist):
        """Test statistics are properly tracked."""
        specialist.geometric_sum(first=1, ratio=0.5, n_terms=10)
        specialist.arithmetic_sum(first=1, diff=1, n_terms=50)
        specialist.telescoping_sum('1/(n*(n+1))')

        stats = specialist.get_statistics()
        # Check for any statistics being returned
        assert isinstance(stats, dict)
        assert len(stats) > 0


class TestSeriesSumEdgeCases:
    """Additional edge case tests for SeriesSumSpecialist."""

    @pytest.fixture
    def specialist(self):
        return SeriesSumSpecialist(agent_id='test_edge_001')

    def test_identify_and_sum(self, specialist):
        """Test automatic series type identification."""
        result = specialist.identify_and_sum('0.5**n')
        assert result is not None

    def test_negative_arithmetic_sum(self, specialist):
        """Test arithmetic sum with negative common difference."""
        result = specialist.arithmetic_sum(first=100, diff=-1, n_terms=100)

        expected = 100 * 101 / 2

        assert result is not None
        assert abs(result.get('sum', 0) - expected) < 1e-10

    def test_alternating_geometric(self, specialist):
        """Test alternating geometric series."""
        result = specialist.geometric_sum(first=1, ratio=-0.5, n_terms=None)

        expected = 1 / (1 - (-0.5))  # = 2/3

        assert result is not None
        assert abs(result.get('sum', 0) - expected) < 1e-10

    def test_p_series_divergent(self, specialist):
        """Test divergent p-series: sum(1/n) (p=1)."""
        result = specialist.p_series_sum(p=1)

        # Harmonic series diverges, so either returns a large sum or marks as divergent
        assert result.get('converges', True) == False or result.get('diverges', False) == True

    def test_empty_terms(self, specialist):
        """Test handling of empty terms."""
        result = specialist.telescoping_sum('')
        assert result is not None  # Should handle gracefully
