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

"""
Deep Search Module Tests
========================

Comprehensive tests for deep search components:
- ProverEngine
- PolicyNetwork
- CriticNetwork
- SearchTreeManager
- SpectralPartitioner
"""

import pytest
import numpy as np
import sympy as sp
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# ProverEngine Tests
# =============================================================================


class TestProverEngine:
    """Tests for ProverEngine (abstract class)."""

    def test_prover_engine_is_abstract(self):
        """ProverEngine should be an abstract class."""
        from symbo_agentic_reasoners.discovery.deep_search.prover_engine import (
            ProverEngine
        )
        # Should not be instantiable
        with pytest.raises(TypeError):
            ProverEngine()

    def test_prover_engine_exists(self):
        """ProverEngine class should exist."""
        from symbo_agentic_reasoners.discovery.deep_search import prover_engine
        assert hasattr(prover_engine, 'ProverEngine')


# =============================================================================
# PolicyNetwork Tests
# =============================================================================


class TestPolicyNetwork:
    """Tests for PolicyNetwork."""

    @pytest.fixture
    def policy(self):
        """Create PolicyNetwork instance."""
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import (
            PolicyNetwork
        )
        return PolicyNetwork()

    def test_initialization(self, policy):
        """Should initialize correctly."""
        assert policy is not None

    def test_has_generate_tactics_method(self, policy):
        """Should have generate_tactics method."""
        assert hasattr(policy, 'generate_tactics')

    def test_has_get_statistics_method(self, policy):
        """Should have get_statistics method."""
        assert hasattr(policy, 'get_statistics')
        stats = policy.get_statistics()
        assert isinstance(stats, dict)

    def test_has_health_check_method(self, policy):
        """Should have health_check method."""
        assert hasattr(policy, 'health_check')
        result = policy.health_check()
        assert isinstance(result, bool)


# =============================================================================
# CriticNetwork Tests
# =============================================================================


class TestCriticNetwork:
    """Tests for CriticNetwork."""

    @pytest.fixture
    def critic(self):
        """Create CriticNetwork instance."""
        from symbo_agentic_reasoners.discovery.deep_search.critic_network import (
            CriticNetwork
        )
        return CriticNetwork()

    def test_initialization(self, critic):
        """Should initialize correctly."""
        assert critic is not None

    def test_has_evaluate_method(self, critic):
        """Should have evaluation method."""
        assert (hasattr(critic, 'evaluate') or
                hasattr(critic, 'forward') or
                hasattr(critic, 'get_value'))


# =============================================================================
# SpectralPartitioner Tests
# =============================================================================


class TestSpectralPartitioner:
    """Tests for SpectralPartitioner."""

    @pytest.fixture
    def partitioner(self):
        """Create SpectralPartitioner instance."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            SpectralPartitioner
        )
        return SpectralPartitioner()

    def test_initialization(self, partitioner):
        """Should initialize correctly."""
        assert partitioner is not None

    def test_has_partition_method(self, partitioner):
        """Should have partition method."""
        assert hasattr(partitioner, 'partition')

    def test_has_fit_method(self, partitioner):
        """Should have fit method."""
        assert hasattr(partitioner, 'fit')

    def test_has_get_spectral_gap(self, partitioner):
        """Should have get_spectral_gap method."""
        assert hasattr(partitioner, 'get_spectral_gap')


# =============================================================================
# SearchTreeManager Tests
# =============================================================================


class TestSearchTreeManager:
    """Tests for SearchTreeManager."""

    @pytest.fixture
    def tree_manager(self):
        """Create SearchTreeManager instance."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import (
            SearchTreeManager
        )
        return SearchTreeManager()

    def test_initialization(self, tree_manager):
        """Should initialize correctly."""
        assert tree_manager is not None

    def test_has_initialize_search_method(self, tree_manager):
        """Should have initialize_search method."""
        assert hasattr(tree_manager, 'initialize_search')

    def test_has_search_method(self, tree_manager):
        """Should have search method."""
        assert hasattr(tree_manager, 'search')

    def test_has_get_statistics_method(self, tree_manager):
        """Should have get_statistics method."""
        assert hasattr(tree_manager, 'get_statistics')
        stats = tree_manager.get_statistics()
        assert isinstance(stats, dict)

    def test_has_health_check_method(self, tree_manager):
        """Should have health_check method."""
        assert hasattr(tree_manager, 'health_check')
        result = tree_manager.health_check()
        assert isinstance(result, bool)


# =============================================================================
# Types Tests
# =============================================================================


class TestDeepSearchTypes:
    """Tests for deep search type definitions."""

    def test_proof_state_exists(self):
        """ProofState type should exist."""
        from symbo_agentic_reasoners.discovery.deep_search import types
        assert hasattr(types, 'ProofState')

    def test_search_result_exists(self):
        """SearchResult type should exist."""
        from symbo_agentic_reasoners.discovery.deep_search import types
        assert hasattr(types, 'SearchResult')

    def test_search_status_exists(self):
        """SearchStatus enum should exist."""
        from symbo_agentic_reasoners.discovery.deep_search import types
        assert hasattr(types, 'SearchStatus')

    def test_proof_state_creation(self):
        """Should create ProofState."""
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState

        state = ProofState(
            state_id='test_state',
            goal='x > 0',
            hypotheses=['x is positive'],
            depth=0
        )

        assert state.state_id == 'test_state'
        assert state.goal == 'x > 0'

    def test_proof_state_is_leaf(self):
        """Should check if ProofState is leaf."""
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState

        state = ProofState(
            state_id='leaf_state',
            goal='True',
            hypotheses=[],
            depth=1
        )

        # Call is_leaf method
        result = state.is_leaf()
        assert isinstance(result, bool)

    def test_proof_state_to_dict(self):
        """Should convert ProofState to dict."""
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState

        state = ProofState(
            state_id='dict_state',
            goal='x > 0',
            hypotheses=['x is positive'],
            depth=0
        )

        d = state.to_dict()
        assert isinstance(d, dict)
        assert d['state_id'] == 'dict_state'


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
