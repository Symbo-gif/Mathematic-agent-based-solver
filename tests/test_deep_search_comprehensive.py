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
Deep Search Module Comprehensive Tests
======================================

Tests for deep_search modules to achieve 75%+ coverage:
- ProofState, SearchResult, SearchStatus (types)
- SymPyProver (prover_engine)
- PolicyNetwork, TacticCandidate
- CriticNetwork
- SearchTreeManager
- ExhaustiveEnumerator
- ParallelSearchManager
- SpectralPartitioner
"""

import pytest
import sympy as sp


# =============================================================================
# Types Tests
# =============================================================================


class TestSearchStatus:
    """Tests for SearchStatus enum."""

    def test_active(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus
        assert SearchStatus.ACTIVE.value == 'active'

    def test_completed(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus
        assert SearchStatus.COMPLETED.value == 'completed'

    def test_timeout(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus
        assert SearchStatus.TIMEOUT.value == 'timeout'

    def test_resource_limit(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus
        assert SearchStatus.RESOURCE_LIMIT.value == 'resource_limit'

    def test_undecidable(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus
        assert SearchStatus.UNDECIDABLE.value == 'undecidable'


class TestProofState:
    """Tests for ProofState dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="state_001",
            goal="x > 0",
            hypotheses=["x is real"],
            depth=0
        )
        assert state.state_id == "state_001"
        assert state.goal == "x > 0"
        assert state.depth == 0

    def test_default_values(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="state_002",
            goal="x = x",
            hypotheses=[],
            depth=1
        )
        assert state.parent_id is None
        assert state.tactic_applied is None
        assert state.value_estimate == 0.5
        assert state.visit_count == 0
        assert state.children == []
        assert state.is_terminal is False
        assert state.is_proven is False

    def test_is_leaf_true(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="state_003",
            goal="True",
            hypotheses=[],
            depth=0,
            children=[]
        )
        assert state.is_leaf() is True

    def test_is_leaf_false(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="state_004",
            goal="x > 0",
            hypotheses=[],
            depth=0,
            children=["state_005", "state_006"]
        )
        assert state.is_leaf() is False

    def test_to_dict(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="state_005",
            goal="x + y = y + x",
            hypotheses=["x real", "y real"],
            depth=2,
            parent_id="state_002",
            tactic_applied="ring",
            value_estimate=0.8,
            visit_count=5,
            is_proven=True
        )
        d = state.to_dict()
        assert d['state_id'] == "state_005"
        assert d['goal'] == "x + y = y + x"
        assert d['depth'] == 2
        assert d['value_estimate'] == 0.8
        assert d['is_proven'] is True


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import (
            SearchResult, SearchStatus
        )
        result = SearchResult(
            success=True,
            proof_steps=["simp", "ring", "rfl"],
            states_explored=100,
            max_depth_reached=5,
            time_elapsed_ms=1500.0,
            status=SearchStatus.COMPLETED
        )
        assert result.success is True
        assert len(result.proof_steps) == 3
        assert result.states_explored == 100

    def test_to_dict(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import (
            SearchResult, SearchStatus
        )
        result = SearchResult(
            success=False,
            proof_steps=[],
            states_explored=500,
            max_depth_reached=10,
            time_elapsed_ms=30000.0,
            status=SearchStatus.TIMEOUT,
            value_at_root=0.3
        )
        d = result.to_dict()
        assert d['success'] is False
        assert d['proof_length'] == 0
        assert d['states_explored'] == 500
        assert d['status'] == 'timeout'
        assert d['value_at_root'] == 0.3


# =============================================================================
# ProverEngine Tests
# =============================================================================


class TestSymPyProver:
    """Tests for SymPyProver class."""

    @pytest.fixture
    def prover(self):
        from symbo_agentic_reasoners.discovery.deep_search.prover_engine import SymPyProver
        return SymPyProver()

    @pytest.fixture
    def proof_state(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        return ProofState(
            state_id="test_state",
            goal="x + 1 = 1 + x",
            hypotheses=[],
            depth=0
        )

    @pytest.fixture
    def tactic_simp(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        return TacticCandidate(tactic="simp", probability=0.9)

    @pytest.fixture
    def tactic_ring(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        return TacticCandidate(tactic="ring", probability=0.8)

    @pytest.fixture
    def tactic_rfl(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        return TacticCandidate(tactic="rfl", probability=0.7)

    def test_initialization(self, prover):
        assert prover is not None
        assert prover.transformations is not None

    def test_health_check(self, prover):
        result = prover.health_check()
        assert result is True

    def test_apply_simp_tactic(self, prover, proof_state, tactic_simp):
        new_goal, is_proven = prover.apply_tactic(proof_state, tactic_simp)
        # Result depends on SymPy parsing
        assert isinstance(new_goal, str)
        assert isinstance(is_proven, bool)

    def test_apply_ring_tactic(self, prover, proof_state, tactic_ring):
        new_goal, is_proven = prover.apply_tactic(proof_state, tactic_ring)
        assert isinstance(new_goal, str)
        assert isinstance(is_proven, bool)

    def test_apply_rfl_on_true(self, prover, tactic_rfl):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="true_state",
            goal="True",
            hypotheses=[],
            depth=0
        )
        new_goal, is_proven = prover.apply_tactic(state, tactic_rfl)
        assert is_proven is True
        assert new_goal == "⊤"

    def test_apply_sorry_tactic(self, prover):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        # Use simple parseable goal
        state = ProofState(
            state_id="simple_state",
            goal="x + y",
            hypotheses=[],
            depth=0
        )
        tactic = TacticCandidate(tactic="sorry", probability=0.1)
        new_goal, is_proven = prover.apply_tactic(state, tactic)
        assert is_proven is True
        assert new_goal == "⊤"

    def test_apply_linarith_tactic(self, prover):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        state = ProofState(
            state_id="ineq_state",
            goal="x + 1 > x",
            hypotheses=[],
            depth=0
        )
        tactic = TacticCandidate(tactic="linarith", probability=0.6)
        new_goal, is_proven = prover.apply_tactic(state, tactic)
        assert isinstance(new_goal, str)
        assert isinstance(is_proven, bool)

    def test_apply_trivial_tactic(self, prover, proof_state):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        tactic = TacticCandidate(tactic="trivial", probability=0.5)
        new_goal, is_proven = prover.apply_tactic(proof_state, tactic)
        assert isinstance(new_goal, str)
        assert isinstance(is_proven, bool)

    def test_unparseable_goal(self, prover, tactic_simp):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="unparseable",
            goal="∀x.P(x) → Q(x)",  # Complex logic that SymPy can't parse
            hypotheses=[],
            depth=0
        )
        new_goal, is_proven = prover.apply_tactic(state, tactic_simp)
        assert "[PARSE_ERROR]" in new_goal
        assert is_proven is False


# =============================================================================
# PolicyNetwork Tests
# =============================================================================


class TestTacticCandidate:
    """Tests for TacticCandidate dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        tc = TacticCandidate(tactic="simp", probability=0.9)
        assert tc.tactic == "simp"
        assert tc.probability == 0.9

    def test_with_category(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import (
            TacticCandidate, TacticCategory
        )
        tc = TacticCandidate(
            tactic="ring",
            probability=0.8,
            category=TacticCategory.REWRITING
        )
        assert tc.category == TacticCategory.REWRITING


class TestPolicyNetwork:
    """Tests for PolicyNetwork class."""

    @pytest.fixture
    def network(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import PolicyNetwork
        return PolicyNetwork()

    def test_initialization(self, network):
        assert network is not None

    def test_has_get_statistics(self, network):
        assert hasattr(network, 'get_statistics')

    def test_get_statistics(self, network):
        stats = network.get_statistics()
        assert isinstance(stats, dict)

    def test_has_health_check(self, network):
        assert hasattr(network, 'health_check')

    def test_health_check(self, network):
        result = network.health_check()
        assert isinstance(result, bool)


# =============================================================================
# CriticNetwork Tests
# =============================================================================


class TestCriticNetwork:
    """Tests for CriticNetwork class."""

    @pytest.fixture
    def critic(self):
        from symbo_agentic_reasoners.discovery.deep_search.critic_network import CriticNetwork
        return CriticNetwork()

    def test_initialization(self, critic):
        assert critic is not None

    def test_has_get_statistics(self, critic):
        assert hasattr(critic, 'get_statistics')

    def test_get_statistics(self, critic):
        stats = critic.get_statistics()
        assert isinstance(stats, dict)

    def test_has_health_check(self, critic):
        assert hasattr(critic, 'health_check')

    def test_health_check(self, critic):
        result = critic.health_check()
        assert isinstance(result, bool)


# =============================================================================
# SearchTreeManager Tests
# =============================================================================


class TestSearchTreeManagerComprehensive:
    """Comprehensive tests for SearchTreeManager class."""

    @pytest.fixture
    def manager(self):
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        return SearchTreeManager()

    def test_initialization(self, manager):
        assert manager is not None

    def test_has_get_statistics(self, manager):
        assert hasattr(manager, 'get_statistics')

    def test_get_statistics(self, manager):
        stats = manager.get_statistics()
        assert isinstance(stats, dict)

    def test_has_health_check(self, manager):
        assert hasattr(manager, 'health_check')

    def test_health_check(self, manager):
        result = manager.health_check()
        assert isinstance(result, bool)


# =============================================================================
# ExhaustiveEnumerator Tests
# =============================================================================


class TestExhaustiveEnumeratorComprehensive:
    """Comprehensive tests for ExhaustiveEnumerator class."""

    @pytest.fixture
    def enumerator(self):
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import ExhaustiveEnumerator
        return ExhaustiveEnumerator()

    def test_initialization(self, enumerator):
        assert enumerator is not None

    def test_has_get_statistics(self, enumerator):
        assert hasattr(enumerator, 'get_statistics')

    def test_get_statistics(self, enumerator):
        stats = enumerator.get_statistics()
        assert isinstance(stats, dict)

    def test_has_health_check(self, enumerator):
        assert hasattr(enumerator, 'health_check')

    def test_health_check(self, enumerator):
        result = enumerator.health_check()
        assert isinstance(result, bool)


# =============================================================================
# ParallelSearchManager Tests
# =============================================================================


class TestParallelSearchManagerComprehensive:
    """Comprehensive tests for ParallelSearchManager class."""

    @pytest.fixture
    def manager(self):
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import ParallelSearchManager
        return ParallelSearchManager()

    def test_initialization(self, manager):
        assert manager is not None

    def test_has_get_statistics(self, manager):
        assert hasattr(manager, 'get_statistics')

    def test_get_statistics(self, manager):
        stats = manager.get_statistics()
        assert isinstance(stats, dict)

    def test_has_health_check(self, manager):
        assert hasattr(manager, 'health_check')

    def test_health_check(self, manager):
        result = manager.health_check()
        assert isinstance(result, bool)


# =============================================================================
# SpectralPartitioner Tests
# =============================================================================


class TestSpectralPartitioner:
    """Tests for SpectralPartitioner class."""

    @pytest.fixture
    def partitioner(self):
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import SpectralPartitioner
        return SpectralPartitioner()

    def test_initialization(self, partitioner):
        assert partitioner is not None

    def test_is_importable(self):
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import SpectralPartitioner
        assert SpectralPartitioner is not None


# =============================================================================
# Extended SymPyProver Tests
# =============================================================================


class TestSymPyProverExtended:
    """Extended tests for SymPyProver."""

    @pytest.fixture
    def prover(self):
        from symbo_agentic_reasoners.discovery.deep_search.prover_engine import SymPyProver
        return SymPyProver()

    def test_has_transformations(self, prover):
        """Should have transformations attribute."""
        assert hasattr(prover, 'transformations')

    def test_transformations_is_tuple(self, prover):
        """Transformations should be a tuple."""
        assert isinstance(prover.transformations, tuple)


# =============================================================================
# Extended PolicyNetwork Tests
# =============================================================================


class TestPolicyNetworkExtended:
    """Extended tests for PolicyNetwork."""

    @pytest.fixture
    def network(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import PolicyNetwork
        return PolicyNetwork()

    def test_has_generate_tactics(self, network):
        """Should have generate_tactics method."""
        assert hasattr(network, 'generate_tactics')

    def test_has_reset(self, network):
        """Should have reset method."""
        assert hasattr(network, 'reset')


class TestTacticCategory:
    """Tests for TacticCategory enum."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCategory
        assert TacticCategory is not None

    def test_has_values(self):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCategory
        # Should have at least one category
        values = list(TacticCategory)
        assert len(values) > 0


# =============================================================================
# Extended CriticNetwork Tests
# =============================================================================


class TestCriticNetworkExtended:
    """Extended tests for CriticNetwork."""

    @pytest.fixture
    def critic(self):
        from symbo_agentic_reasoners.discovery.deep_search.critic_network import CriticNetwork
        return CriticNetwork()

    def test_has_evaluate(self, critic):
        """Should have evaluate method."""
        assert hasattr(critic, 'evaluate')


# =============================================================================
# Extended SearchTreeManager Tests
# =============================================================================


class TestSearchTreeManagerExtended:
    """Extended tests for SearchTreeManager."""

    @pytest.fixture
    def manager(self):
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        return SearchTreeManager()

    def test_has_reset(self, manager):
        """Should have reset method."""
        assert hasattr(manager, 'reset')


# =============================================================================
# Extended ExhaustiveEnumerator Tests
# =============================================================================


class TestExhaustiveEnumeratorExtended:
    """Extended tests for ExhaustiveEnumerator."""

    @pytest.fixture
    def enumerator(self):
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import ExhaustiveEnumerator
        return ExhaustiveEnumerator()

    def test_has_enumerate(self, enumerator):
        """Should have enumerate method."""
        assert hasattr(enumerator, 'enumerate')


# =============================================================================
# Extended SpectralPartitioner Tests
# =============================================================================


class TestSpectralPartitionerExtended:
    """Extended tests for SpectralPartitioner."""

    @pytest.fixture
    def partitioner(self):
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import SpectralPartitioner
        return SpectralPartitioner()

    def test_has_partition(self, partitioner):
        """Should have partition method."""
        assert hasattr(partitioner, 'partition')

    def test_has_fit(self, partitioner):
        """Should have fit method."""
        assert hasattr(partitioner, 'fit')


# =============================================================================
# ProofState Extended Tests
# =============================================================================


class TestProofStateExtended:
    """Extended tests for ProofState."""

    def test_with_parent(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="child",
            goal="x = y",
            hypotheses=[],
            depth=1,
            parent_id="parent"
        )
        assert state.parent_id == "parent"

    def test_with_tactic(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState
        state = ProofState(
            state_id="tactic_test",
            goal="x = y",
            hypotheses=[],
            depth=1,
            tactic_applied="rewrite"
        )
        assert state.tactic_applied == "rewrite"


# =============================================================================
# SearchResult Extended Tests
# =============================================================================


class TestSearchResultExtended:
    """Extended tests for SearchResult."""

    def test_with_value_at_root(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchResult, SearchStatus
        result = SearchResult(
            success=False,
            proof_steps=[],
            states_explored=100,
            max_depth_reached=5,
            time_elapsed_ms=5000.0,
            status=SearchStatus.RESOURCE_LIMIT,
            value_at_root=0.3
        )
        assert result.value_at_root == 0.3

    def test_to_dict_includes_all_fields(self):
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchResult, SearchStatus
        result = SearchResult(
            success=True,
            proof_steps=["step1", "step2"],
            states_explored=50,
            max_depth_reached=3,
            time_elapsed_ms=2500.0,
            status=SearchStatus.COMPLETED
        )
        d = result.to_dict()
        assert 'success' in d
        assert 'proof_length' in d
        assert 'states_explored' in d
        assert 'status' in d


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
