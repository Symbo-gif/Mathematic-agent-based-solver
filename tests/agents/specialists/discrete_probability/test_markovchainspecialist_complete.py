# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
MARKOV CHAIN SPECIALIST TESTS
==============================

Comprehensive test suite for MarkovChainSpecialist with 12-test pattern
plus extended tests for matrix operations and state classification.
"""

import pytest
import numpy as np
from unittest.mock import Mock

from symbo_agentic_reasoners.agents.specialists.discrete_probability.markov_chain_specialist import (
    MarkovChainSpecialist
)


class TestMarkovChainSpecialistComplete:
    """Comprehensive tests for MarkovChainSpecialist."""

    @pytest.fixture
    def specialist(self):
        return MarkovChainSpecialist(agent_id='test_markov_001')

    @pytest.fixture
    def mock_df(self):
        mock = Mock()
        mock.register_service = Mock(return_value=True)
        return mock

    @pytest.fixture
    def simple_chain(self):
        """Simple 2-state ergodic chain."""
        return [[0.7, 0.3], [0.4, 0.6]]

    @pytest.fixture
    def absorbing_chain(self):
        """Chain with absorbing states."""
        return [[1.0, 0.0, 0.0],
                [0.2, 0.5, 0.3],
                [0.0, 0.0, 1.0]]

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_markov_001'
        assert specialist.service_type == 'math.probability.discrete.markov'

    def test_df_registration(self, specialist, mock_df):
        result = specialist.register_with_df(mock_df)
        assert result is True

    def test_blackboard_entry_creation(self, specialist):
        problem = {'operation': 'validate_matrix', 'P': [[0.5, 0.5], [0.3, 0.7]]}
        entry = specialist.create_blackboard_entry(problem)
        assert entry['status'] == 'pending'

    def test_simple_problem_solving(self, specialist, simple_chain):
        """Test matrix validation."""
        request = {'operation': 'validate_matrix', 'P': simple_chain}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_valid'] is True

    def test_complex_problem_solving(self, specialist, simple_chain):
        """Test stationary distribution calculation."""
        request = {'operation': 'stationary_distribution', 'P': simple_chain}
        result = specialist.process_request(request)
        assert result['success'] is True
        pi = result['stationary_distribution']
        # Should sum to 1
        assert abs(sum(pi) - 1.0) < 1e-10

    def test_invalid_input_handling(self, specialist):
        # Non-stochastic matrix
        request = {'operation': 'validate_matrix', 'P': [[0.5, 0.3], [0.3, 0.7]]}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_valid'] is False

        # Non-square matrix
        request = {'operation': 'validate_matrix', 'P': [[0.5, 0.5], [0.3, 0.7], [0.2, 0.8]]}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_edge_cases(self, specialist):
        # Single state
        request = {'operation': 'validate_matrix', 'P': [[1.0]]}
        result = specialist.process_request(request)
        assert result['is_valid'] is True

        # Identity matrix (every state absorbing)
        request = {'operation': 'classify_states', 'P': [[1, 0], [0, 1]]}
        result = specialist.process_request(request)
        assert result['success'] is True

    def test_error_reporting(self, specialist):
        request = {'operation': 'unknown'}
        result = specialist.process_request(request)
        assert result['success'] is False

    def test_statistics_reporting(self, specialist, simple_chain):
        specialist.process_request({'operation': 'validate_matrix', 'P': simple_chain})
        stats = specialist.get_statistics()
        assert 'problems_solved' in stats or 'tasks_executed' in stats or 'statistics' in stats

    def test_bdi_update_beliefs(self, specialist):
        specialist.update_beliefs({'operation': 'n_step', 'n': 10})
        assert specialist.beliefs.get('n') == 10

    def test_bdi_deliberate(self, specialist):
        specialist.beliefs = {'operation': 'n_step'}
        desires = specialist.deliberate()
        assert 'execute_n_step' in desires

    def test_bdi_execute_step(self, specialist, simple_chain):
        specialist.beliefs = {'operation': 'validate_matrix', 'P': simple_chain}
        specialist.deliberate()
        result = specialist.execute_step()
        assert result is not None

    def test_n_step_transition(self, specialist, simple_chain):
        """Test n-step transition probabilities."""
        request = {'operation': 'n_step', 'P': simple_chain, 'n': 10}
        result = specialist.process_request(request)
        assert result['success'] is True
        P_n = np.array(result['P_n'])
        # Rows should sum to 1
        for row in P_n:
            assert abs(sum(row) - 1.0) < 1e-10

    def test_state_classification(self, specialist, absorbing_chain):
        """Test state classification."""
        request = {'operation': 'classify_states', 'P': absorbing_chain}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert 'absorbing' in result or 'transient' in result or 'recurrent' in result

    def test_ergodicity_check(self, specialist, simple_chain):
        """Test ergodicity verification."""
        request = {'operation': 'check_ergodic', 'P': simple_chain}
        result = specialist.process_request(request)
        assert result['success'] is True


class TestMarkovChainEdgeCases:
    """Extended edge case tests for Markov chains."""

    @pytest.fixture
    def specialist(self):
        return MarkovChainSpecialist()

    def test_periodic_chain(self, specialist):
        """Test periodic chain (no limiting distribution)."""
        # Period 2 chain
        P = [[0, 1], [1, 0]]
        request = {'operation': 'check_aperiodic', 'P': P}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_aperiodic'] is False

    def test_reducible_chain(self, specialist):
        """Test reducible chain."""
        P = [[0.5, 0.5, 0], [0.5, 0.5, 0], [0, 0, 1]]
        request = {'operation': 'check_irreducible', 'P': P}
        result = specialist.process_request(request)
        assert result['success'] is True
        assert result['is_irreducible'] is False
