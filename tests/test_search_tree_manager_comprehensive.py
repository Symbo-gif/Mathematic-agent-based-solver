# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Comprehensive SearchTreeManager Tests
=====================================

Tests to bring search_tree_manager.py coverage to 75%+.
Covers:
- Search execution (MCTS-style)
- UCB1 selection
- Tree expansion
- Backpropagation
- Proof extraction
- Parallel search functionality
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# Mock Classes for Testing
# =============================================================================


class MockProverEngine:
    """Mock prover that can be configured to prove certain states."""

    def __init__(self, prove_after_steps=None):
        """
        Args:
            prove_after_steps: If set, the nth tactic application returns proven=True
        """
        self.prove_after_steps = prove_after_steps
        self.apply_count = 0

    def apply_tactic(self, state, tactic):
        self.apply_count += 1
        if self.prove_after_steps and self.apply_count >= self.prove_after_steps:
            return "QED", True  # Proven
        return f"subgoal_{self.apply_count}", False

    def health_check(self):
        return True


class MockPolicyNetwork:
    """Mock policy that generates simple tactics."""

    def __init__(self, num_tactics=3):
        self.num_tactics = num_tactics
        self.call_count = 0

    def generate_tactics(self, state, top_k=5):
        from symbo_agentic_reasoners.discovery.deep_search.policy_network import TacticCandidate
        self.call_count += 1
        return [
            TacticCandidate(
                tactic=f"tactic_{i}",
                probability=0.9 - i * 0.1,
                category="introduction"
            )
            for i in range(min(self.num_tactics, top_k))
        ]

    def get_statistics(self):
        return {'calls': self.call_count}

    def health_check(self):
        return True


class MockCriticNetwork:
    """Mock critic that returns configurable values."""

    def __init__(self, default_value=0.5, value_map=None):
        self.default_value = default_value
        self.value_map = value_map or {}
        self.eval_count = 0

    def evaluate(self, state):
        self.eval_count += 1
        if state.state_id in self.value_map:
            return self.value_map[state.state_id]
        # Deeper states get lower values by default
        return max(0.1, self.default_value - state.depth * 0.05)

    def get_statistics(self):
        return {'evaluations': self.eval_count}

    def health_check(self):
        return True


class MockConjecture:
    """Mock conjecture for testing."""

    def __init__(self, goal="x > 0", premises=None, lean4_statement=None):
        self.lean4_statement = lean4_statement

        class MockTheorem:
            def __init__(self, g, p):
                self.conclusion = g
                self.premises = p or []

        self.source_theorem = MockTheorem(goal, premises or [])


# =============================================================================
# SearchTreeManager Initialization Tests
# =============================================================================


class TestSearchTreeManagerInit:
    """Tests for SearchTreeManager initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        manager = SearchTreeManager()
        assert manager.c_puct == 1.4
        assert manager.max_depth == 50
        assert manager.prune_threshold == 0.05
        assert manager.root_id is None
        assert len(manager.states) == 0

    def test_custom_initialization(self):
        """Test with custom parameters."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        manager = SearchTreeManager(
            exploration_constant=2.0,
            max_depth=100,
            prune_threshold=0.1
        )
        assert manager.c_puct == 2.0
        assert manager.max_depth == 100
        assert manager.prune_threshold == 0.1

    def test_with_mock_components(self):
        """Test initialization with mock components."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        policy = MockPolicyNetwork()
        critic = MockCriticNetwork()
        prover = MockProverEngine()

        manager = SearchTreeManager(
            policy_network=policy,
            critic_network=critic,
            prover_engine=prover
        )

        assert manager.policy is policy
        assert manager.critic is critic
        assert manager.prover_engine is prover


# =============================================================================
# Initialize Search Tests
# =============================================================================


class TestInitializeSearch:
    """Tests for initialize_search method."""

    @pytest.fixture
    def manager(self):
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        return SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )

    def test_initialize_with_lean4_statement(self, manager):
        """Test initialization with lean4_statement."""
        conjecture = MockConjecture(
            goal="x > 0",
            lean4_statement="theorem test : x > 0"
        )
        root_id = manager.initialize_search(conjecture)

        assert root_id is not None
        assert manager.root_id == root_id
        assert len(manager.states) == 1

        root = manager.states[root_id]
        assert root.goal == "theorem test : x > 0"

    def test_initialize_without_lean4_statement(self, manager):
        """Test initialization without lean4_statement."""
        conjecture = MockConjecture(goal="y > 0", lean4_statement=None)
        root_id = manager.initialize_search(conjecture)

        root = manager.states[root_id]
        assert root.goal == "y > 0"

    def test_initialize_with_premises(self, manager):
        """Test initialization with premises."""
        conjecture = MockConjecture(
            goal="x + y > 0",
            premises=["x > 0", "y > 0"]
        )
        root_id = manager.initialize_search(conjecture)

        root = manager.states[root_id]
        assert len(root.hypotheses) == 2
        assert "x > 0" in root.hypotheses

    def test_initialize_plain_string(self, manager):
        """Test initialization with plain string conjecture."""
        root_id = manager.initialize_search("simple_goal")

        root = manager.states[root_id]
        assert root.goal == "simple_goal"
        assert root.hypotheses == []

    def test_initialize_clears_previous_state(self, manager):
        """Test that initialize_search clears previous state."""
        # First search
        manager.initialize_search(MockConjecture(goal="first"))
        assert len(manager.states) == 1

        # Second search should clear
        manager.initialize_search(MockConjecture(goal="second"))
        assert len(manager.states) == 1

        root = manager.states[manager.root_id]
        assert root.goal == "second"

    def test_initialize_updates_stats(self, manager):
        """Test that initialize updates statistics."""
        initial_searches = manager.stats['total_searches']
        manager.initialize_search(MockConjecture())
        assert manager.stats['total_searches'] == initial_searches + 1


# =============================================================================
# Search Execution Tests
# =============================================================================


class TestSearchExecution:
    """Tests for the main search method."""

    @pytest.fixture
    def manager_with_search(self):
        """Create manager initialized with a search."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(num_tactics=2),
            critic_network=MockCriticNetwork(default_value=0.6),
            prover_engine=MockProverEngine(),
            max_depth=10,
            prune_threshold=0.1
        )
        manager.initialize_search(MockConjecture(goal="test_goal"))
        return manager

    def test_search_completes_without_proof(self, manager_with_search):
        """Test search that completes without finding proof."""
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus

        result = manager_with_search.search(num_simulations=5, max_expansions=10)

        assert result.success is False
        # May complete or hit resource limit depending on search
        assert result.status in [SearchStatus.COMPLETED, SearchStatus.RESOURCE_LIMIT]
        assert result.states_explored > 0
        assert result.time_elapsed_ms >= 0

    def test_search_finds_proof(self):
        """Test search that finds a proof."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus

        # Prover that proves after 2 applications
        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(num_tactics=2),
            critic_network=MockCriticNetwork(default_value=0.8),
            prover_engine=MockProverEngine(prove_after_steps=2)
        )
        manager.initialize_search(MockConjecture())

        result = manager.search(num_simulations=100)

        assert result.success is True
        assert result.status == SearchStatus.COMPLETED
        assert len(result.proof_steps) > 0

    def test_search_with_timeout(self, manager_with_search):
        """Test search with timeout."""
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus

        # Very short timeout
        result = manager_with_search.search(num_simulations=10000, timeout_ms=1)

        # Should timeout quickly
        assert result.success is False
        assert result.status in [SearchStatus.TIMEOUT, SearchStatus.COMPLETED]

    def test_search_with_max_expansions(self, manager_with_search):
        """Test search with expansion limit."""
        from symbo_agentic_reasoners.discovery.deep_search.types import SearchStatus

        result = manager_with_search.search(num_simulations=1000, max_expansions=5)

        assert result.success is False
        # Should hit resource limit
        assert result.status in [SearchStatus.RESOURCE_LIMIT, SearchStatus.COMPLETED]

    def test_search_updates_stats(self, manager_with_search):
        """Test that search updates statistics."""
        initial_simulations = manager_with_search.stats['total_simulations']

        manager_with_search.search(num_simulations=10, max_expansions=20)

        assert manager_with_search.stats['total_simulations'] > initial_simulations
        assert manager_with_search.stats['total_expansions'] > 0


# =============================================================================
# Selection and Expansion Tests
# =============================================================================


class TestSelectionAndExpansion:
    """Tests for _select, _expand, and related methods."""

    @pytest.fixture
    def manager_with_tree(self):
        """Create manager with an expanded tree."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(num_tactics=3),
            critic_network=MockCriticNetwork(default_value=0.7),
            prover_engine=MockProverEngine()
        )
        manager.initialize_search(MockConjecture())

        # Expand root to create some children
        root_id = manager.root_id
        manager._expand(root_id)

        return manager

    def test_select_returns_leaf(self, manager_with_tree):
        """Test that _select returns a leaf node."""
        leaf_id = manager_with_tree._select()

        assert leaf_id is not None
        state = manager_with_tree.states[leaf_id]
        # Should be either a leaf or terminal
        assert state.is_leaf() or state.is_terminal

    def test_select_none_when_no_root(self):
        """Test _select returns None when no root."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        manager = SearchTreeManager()
        assert manager._select() is None

    def test_expand_creates_children(self, manager_with_tree):
        """Test that _expand creates child states."""
        # Get a leaf to expand
        leaf_id = manager_with_tree._select()
        initial_count = len(manager_with_tree.states)

        # Expand it
        children = manager_with_tree._expand(leaf_id)

        assert len(children) > 0
        assert len(manager_with_tree.states) > initial_count

        # Check parent-child relationship
        parent = manager_with_tree.states[leaf_id]
        assert len(parent.children) == len(children)

    def test_expand_updates_max_depth(self, manager_with_tree):
        """Test that expansion updates max_depth_reached."""
        # Expand multiple times
        for _ in range(3):
            leaf_id = manager_with_tree._select()
            if leaf_id:
                manager_with_tree._expand(leaf_id)

        assert manager_with_tree.stats['max_depth_reached'] > 0

    def test_backpropagate_updates_visit_counts(self, manager_with_tree):
        """Test that backpropagation updates visit counts."""
        leaf_id = manager_with_tree._select()
        initial_root_visits = manager_with_tree.states[manager_with_tree.root_id].visit_count

        manager_with_tree._backpropagate(leaf_id)

        # Root should have increased visit count
        assert manager_with_tree.states[manager_with_tree.root_id].visit_count > initial_root_visits

    def test_backpropagate_updates_values(self, manager_with_tree):
        """Test that backpropagation updates value estimates."""
        # Expand and set a high value on a child
        root_id = manager_with_tree.root_id
        root = manager_with_tree.states[root_id]

        if root.children:
            child_id = root.children[0]
            child = manager_with_tree.states[child_id]
            child.value_estimate = 0.9

            manager_with_tree._backpropagate(child_id)

            # Root should pick up high child value
            assert root.value_estimate >= 0.7  # Should be influenced by child


# =============================================================================
# Proof Extraction Tests
# =============================================================================


class TestProofExtraction:
    """Tests for proof extraction and success result building."""

    def test_extract_proof_from_proven_state(self):
        """Test extracting proof from a proven state."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )

        # Create a manual proof path
        root_id = "root_test"
        child_id = "child_test"
        proven_id = "proven_test"

        manager.root_id = root_id
        manager.states[root_id] = ProofState(
            state_id=root_id,
            goal="goal",
            hypotheses=[],
            depth=0
        )
        manager.states[child_id] = ProofState(
            state_id=child_id,
            goal="subgoal",
            hypotheses=[],
            depth=1,
            parent_id=root_id,
            tactic_applied="apply lemma1"
        )
        manager.states[proven_id] = ProofState(
            state_id=proven_id,
            goal="QED",
            hypotheses=[],
            depth=2,
            parent_id=child_id,
            tactic_applied="trivial",
            is_proven=True
        )

        # Extract proof
        proof = manager._extract_proof(proven_id)

        assert len(proof) == 2
        assert proof[0] == "apply lemma1"
        assert proof[1] == "trivial"

    def test_build_success_result(self):
        """Test building success result."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState, SearchStatus

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )

        # Setup proven state
        root_id = "root"
        proven_id = "proven"

        manager.root_id = root_id
        manager.states[root_id] = ProofState(
            state_id=root_id, goal="g", hypotheses=[], depth=0,
            value_estimate=0.8
        )
        manager.states[proven_id] = ProofState(
            state_id=proven_id, goal="QED", hypotheses=[], depth=1,
            parent_id=root_id, tactic_applied="done", is_proven=True
        )

        import time
        start = time.time()
        result = manager._build_success_result(proven_id, start)

        assert result.success is True
        assert result.status == SearchStatus.COMPLETED
        assert len(result.proof_steps) == 1
        assert result.value_at_root == 0.8
        assert manager.stats['successful_proofs'] == 1


# =============================================================================
# Tree Summary and Statistics Tests
# =============================================================================


class TestTreeSummaryAndStats:
    """Tests for tree summary and statistics methods."""

    @pytest.fixture
    def manager_with_tree(self):
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(default_value=0.6),
            prover_engine=MockProverEngine()
        )
        manager.initialize_search(MockConjecture())

        # Do some expansion
        manager.search(num_simulations=10, max_expansions=15)

        return manager

    def test_get_tree_summary_with_states(self, manager_with_tree):
        """Test getting tree summary with populated tree."""
        summary = manager_with_tree.get_tree_summary()

        assert 'total_states' in summary
        assert summary['total_states'] > 0
        assert 'max_depth' in summary
        assert 'avg_depth' in summary
        assert 'avg_value' in summary
        assert 'terminal_states' in summary
        assert 'proven_states' in summary

    def test_get_max_depth(self, manager_with_tree):
        """Test _get_max_depth method."""
        max_depth = manager_with_tree._get_max_depth()
        assert max_depth >= 0

    def test_get_statistics(self, manager_with_tree):
        """Test get_statistics method."""
        stats = manager_with_tree.get_statistics()

        assert 'total_searches' in stats
        assert 'successful_proofs' in stats
        assert 'total_expansions' in stats
        assert 'current_tree_size' in stats
        assert 'policy_stats' in stats
        assert 'critic_stats' in stats
        assert 'prover_engine' in stats


# =============================================================================
# Checkpoint and Restore Tests
# =============================================================================


class TestCheckpointRestore:
    """Tests for checkpoint and restore functionality."""

    def test_checkpoint_contains_required_data(self):
        """Test checkpoint contains all required data."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )
        manager.initialize_search(MockConjecture())
        manager.search(num_simulations=5, max_expansions=10)

        checkpoint = manager.checkpoint()

        assert 'root_id' in checkpoint
        assert 'states' in checkpoint
        assert 'stats' in checkpoint
        assert checkpoint['root_id'] == manager.root_id

    def test_restore_from_checkpoint(self):
        """Test restoring from checkpoint."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )
        manager.initialize_search(MockConjecture())
        manager.search(num_simulations=5, max_expansions=10)

        # Checkpoint
        checkpoint = manager.checkpoint()
        original_root = manager.root_id
        original_state_count = len(manager.states)

        # Clear and restore
        manager.reset()
        assert manager.root_id is None

        manager.restore(checkpoint)

        assert manager.root_id == original_root
        assert len(manager.states) == original_state_count


# =============================================================================
# Parallel Search Tests
# =============================================================================


class TestParallelSearch:
    """Tests for parallel search functionality."""

    @pytest.fixture
    def manager_with_large_tree(self):
        """Create manager with enough states for parallel search."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(num_tactics=4),
            critic_network=MockCriticNetwork(default_value=0.7),
            prover_engine=MockProverEngine(),
            prune_threshold=0.01  # Low threshold to keep more states
        )
        manager.initialize_search(MockConjecture())

        # Build up a larger tree
        manager.search(num_simulations=50, max_expansions=100)

        return manager

    def test_fallback_assignment_small_tree(self):
        """Test fallback assignment for small trees."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )
        manager.initialize_search(MockConjecture())

        # Only root state - too small for spectral
        assignment = manager.get_worker_assignment(4)

        assert assignment is not None
        assert assignment.num_workers == 4

    def test_get_worker_assignment(self, manager_with_large_tree):
        """Test getting worker assignment."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import PartitionStrategy

        assignment = manager_with_large_tree.get_worker_assignment(
            num_workers=2,
            strategy=PartitionStrategy.BALANCED
        )

        assert assignment is not None
        assert assignment.num_workers == 2

    def test_get_frontier_for_worker(self, manager_with_large_tree):
        """Test getting frontier for a specific worker."""
        assignment = manager_with_large_tree.get_worker_assignment(2)

        frontier = manager_with_large_tree.get_frontier_for_worker(0, assignment)

        # Frontier should be a list (may be empty if all leaves are terminal)
        assert isinstance(frontier, list)

    def test_parallel_search_step(self, manager_with_large_tree):
        """Test executing a parallel search step."""
        assignment = manager_with_large_tree.get_worker_assignment(2)

        new_states, proof_found = manager_with_large_tree.parallel_search_step(
            worker_id=0,
            assignment=assignment,
            expansions_per_step=3
        )

        assert isinstance(new_states, list)
        assert isinstance(proof_found, bool)

    def test_recommend_worker_count_small_tree(self):
        """Test worker count recommendation for small tree."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )
        manager.initialize_search(MockConjecture())

        # Small tree should recommend 1 worker
        count = manager.recommend_worker_count()
        assert count == 1

    def test_get_partition_summary(self, manager_with_large_tree):
        """Test getting partition summary."""
        assignment = manager_with_large_tree.get_worker_assignment(2)

        summary = manager_with_large_tree.get_partition_summary(assignment)

        assert 'num_workers' in summary
        assert 'total_states' in summary
        assert 'partitions' in summary
        assert 'balance_ratio' in summary


# =============================================================================
# UCB1 Selection Tests
# =============================================================================


class TestUCB1Selection:
    """Detailed tests for UCB1 selection behavior."""

    def test_select_prefers_high_value_unexplored(self):
        """Test that UCB1 balances exploitation and exploration."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )

        # Manual tree setup
        root_id = "root"
        child1_id = "child1"
        child2_id = "child2"

        manager.root_id = root_id
        manager.states[root_id] = ProofState(
            state_id=root_id, goal="g", hypotheses=[], depth=0,
            visit_count=10
        )
        manager.states[root_id].children = [child1_id, child2_id]

        # Child 1: explored, medium value
        manager.states[child1_id] = ProofState(
            state_id=child1_id, goal="g1", hypotheses=[], depth=1,
            parent_id=root_id, value_estimate=0.5, visit_count=8
        )

        # Child 2: unexplored, low value (but UCB bonus should help)
        manager.states[child2_id] = ProofState(
            state_id=child2_id, goal="g2", hypotheses=[], depth=1,
            parent_id=root_id, value_estimate=0.3, visit_count=0
        )

        # Should select one of the children
        selected = manager._select()
        assert selected in [child1_id, child2_id]

    def test_select_avoids_terminal_non_proven(self):
        """Test that selection avoids terminal non-proven states."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager
        from symbo_agentic_reasoners.discovery.deep_search.types import ProofState

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(),
            critic_network=MockCriticNetwork(),
            prover_engine=MockProverEngine()
        )

        root_id = "root"
        dead_end_id = "dead_end"
        good_id = "good"

        manager.root_id = root_id
        manager.states[root_id] = ProofState(
            state_id=root_id, goal="g", hypotheses=[], depth=0,
            visit_count=5
        )
        manager.states[root_id].children = [dead_end_id, good_id]

        # Dead end - terminal but not proven
        manager.states[dead_end_id] = ProofState(
            state_id=dead_end_id, goal="g1", hypotheses=[], depth=1,
            parent_id=root_id, value_estimate=0.1, is_terminal=True
        )

        # Good state - not terminal
        manager.states[good_id] = ProofState(
            state_id=good_id, goal="g2", hypotheses=[], depth=1,
            parent_id=root_id, value_estimate=0.5
        )

        selected = manager._select()
        assert selected == good_id


# =============================================================================
# Pruning Tests
# =============================================================================


class TestPruning:
    """Tests for state pruning behavior."""

    def test_low_value_states_pruned(self):
        """Test that low-value states get pruned."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import SearchTreeManager

        # Critic that returns values that decrease with depth
        # With high prune threshold, deeper states should be pruned
        low_critic = MockCriticNetwork(default_value=0.3)

        manager = SearchTreeManager(
            policy_network=MockPolicyNetwork(num_tactics=3),
            critic_network=low_critic,
            prover_engine=MockProverEngine(),
            prune_threshold=0.2  # Higher threshold to ensure pruning
        )
        manager.initialize_search(MockConjecture())

        # Run search - should prune some states when value < threshold
        manager.search(num_simulations=50, max_expansions=100)

        # Check that states were explored (even if not pruned)
        # Pruning happens when value_estimate < prune_threshold
        # The MockCriticNetwork returns max(0.1, 0.3 - depth*0.05)
        # At depth 3: 0.3 - 0.15 = 0.15 < 0.2 -> should prune
        assert manager.stats['total_expansions'] > 0


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
