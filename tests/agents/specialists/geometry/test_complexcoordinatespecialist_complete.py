# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
COMPLEX COORDINATE SPECIALIST TESTS
====================================

Comprehensive test suite for ComplexCoordinateSpecialist with 12-test pattern.
"""

import pytest
import numpy as np
from unittest.mock import Mock
import math

from symbo_agentic_reasoners.agents.specialists.geometry.complex_coordinate_specialist import (
    ComplexCoordinateSpecialist
)


class TestComplexCoordinateSpecialistComplete:
    """Comprehensive tests for ComplexCoordinateSpecialist."""

    @pytest.fixture
    def specialist(self):
        return ComplexCoordinateSpecialist(agent_id='test_complex_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_complex_001'
        assert specialist.service_type == 'math.geometry.complex'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'point_to_complex'}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist):
        """Test point to complex conversion."""
        request = {'operation': 'point_to_complex', 'point': [3, 4]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['results']['modulus'] == 5.0

    def test_complex_problem_solving(self, specialist):
        """Test Mobius transformation."""
        # w = (z + 1) / (z - 1) maps 0 to -1
        request = {
            'operation': 'mobius_transform',
            'a': [1, 0], 'b': [1, 0], 'c': [1, 0], 'd': [-1, 0],
            'point': [0, 0]
        }
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_invalid_input_handling(self, specialist):
        # Degenerate Mobius (ad - bc = 0)
        request = {
            'operation': 'mobius_transform',
            'a': [1, 0], 'b': [0, 0], 'c': [1, 0], 'd': [0, 0],
            'point': [1, 0]
        }
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        # Circle inversion at center
        request = {'operation': 'circle_inversion', 'center': [0, 0], 'radius': 1, 'point': [0.001, 0]}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist):
        specialist.process_request({'operation': 'point_to_complex', 'point': [1, 2]})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'cross_ratio'})
        assert specialist.beliefs.get('operation') == 'cross_ratio'

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'cross_ratio'}
        desires = specialist.deliberate()
        assert 'execute_cross_ratio' in desires

    def test_bdi_execute_step(self, specialist):
        specialist.beliefs = {'operation': 'point_to_complex', 'point': [1, 0]}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_rotation_around_point(self, specialist):
        """Test rotation in complex plane."""
        request = {
            'operation': 'rotate_around_point',
            'point': [1, 0],
            'center': [0, 0],
            'angle': math.pi / 2
        }
        result = specialist.process_request(request)
        assert result['success'] is True
        rotated = result['rotated_points']
        assert abs(rotated[0] - 0.0) < 1e-10
        assert abs(rotated[1] - 1.0) < 1e-10

    def test_cross_ratio(self, specialist):
        """Test cross ratio (real iff concyclic)."""
        # Four points on unit circle
        points = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        request = {'operation': 'cross_ratio', 'points': points}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_real'] is True

    def test_concyclic_check(self, specialist):
        """Test concyclic check."""
        points = [[0, 0], [1, 0], [1, 1], [0, 1]]  # Square vertices
        request = {'operation': 'concyclic_check', 'points': points}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_circle_through_points(self, specialist):
        """Test finding circle through 3 points."""
        points = [[0, 0], [1, 0], [0, 1]]
        request = {'operation': 'find_circle_through_points', 'points': points}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 'center' in result
        assert 'radius' in result
