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
Unit tests for SpectralPartitioner module.

Tests the diffusion map construction, spectral clustering,
and worker assignment functionality.
"""

import pytest
import numpy as np
from typing import Dict
from dataclasses import dataclass, field
from datetime import datetime


# Minimal ProofState for testing (avoid import issues)
@dataclass
class MockProofState:
    state_id: str
    goal: str = ""
    hypotheses: list = field(default_factory=list)
    depth: int = 0
    parent_id: str = None
    tactic_applied: str = None
    value_estimate: float = 0.5
    visit_count: int = 0
    children: list = field(default_factory=list)
    is_terminal: bool = False
    is_proven: bool = False

    def is_leaf(self) -> bool:
        return len(self.children) == 0


class TestStateGraph:
    """Tests for StateGraph class."""

    def test_empty_graph(self):
        """Empty graph should have zero nodes and edges."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph
        )

        graph = StateGraph()
        assert graph.num_nodes == 0
        assert graph.num_edges == 0

    def test_add_state(self):
        """Adding states should assign sequential indices."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph
        )

        graph = StateGraph()
        idx0 = graph.add_state("state_0")
        idx1 = graph.add_state("state_1")
        idx2 = graph.add_state("state_0")  # Duplicate

        assert idx0 == 0
        assert idx1 == 1
        assert idx2 == 0  # Same state returns same index
        assert graph.num_nodes == 2

    def test_add_edge(self):
        """Adding edges should create both nodes and edge."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph
        )

        graph = StateGraph()
        graph.add_edge("a", "b", 0.5)

        assert graph.num_nodes == 2
        assert graph.num_edges == 1

    def test_adjacency_matrix(self):
        """Adjacency matrix should be symmetric."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph
        )

        graph = StateGraph()
        graph.add_edge("a", "b", 1.0)
        graph.add_edge("b", "c", 1.0)

        A = graph.get_adjacency_matrix()

        # Should be symmetric
        assert (A - A.T).nnz == 0
        assert A.shape == (3, 3)

    def test_build_from_states(self):
        """Build graph from dict of ProofStates."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph
        )

        # Create a simple tree: root -> [child1, child2]
        states = {
            "root": MockProofState(
                state_id="root",
                children=["child1", "child2"],
                value_estimate=0.8
            ),
            "child1": MockProofState(
                state_id="child1",
                parent_id="root",
                value_estimate=0.6
            ),
            "child2": MockProofState(
                state_id="child2",
                parent_id="root",
                value_estimate=0.4
            )
        }

        graph = StateGraph().build_from_states(states)

        assert graph.num_nodes == 3
        assert graph.num_edges > 0  # At least parent-child edges


class TestDiffusionMap:
    """Tests for DiffusionMap class."""

    def test_small_graph(self):
        """Diffusion map should handle small graphs gracefully."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph, DiffusionMap
        )

        graph = StateGraph()
        graph.add_state("single")

        dm = DiffusionMap(n_components=2).fit(graph)
        coords = dm.get_coordinates()

        assert coords.shape[0] == 1

    def test_chain_graph(self):
        """Test on a simple chain graph."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph, DiffusionMap
        )

        # Create chain: 0 - 1 - 2 - 3 - 4
        graph = StateGraph()
        for i in range(4):
            graph.add_edge(f"node_{i}", f"node_{i+1}", 1.0)

        dm = DiffusionMap(n_components=3).fit(graph)
        coords = dm.get_coordinates()

        assert coords.shape[0] == 5  # 5 nodes
        assert coords.shape[1] <= 3  # Up to 3 components

    def test_spectral_gap(self):
        """Spectral gap should be between 0 and 1."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph, DiffusionMap
        )

        graph = StateGraph()
        for i in range(10):
            graph.add_edge(f"node_{i}", f"node_{(i+1) % 10}", 1.0)

        dm = DiffusionMap(n_components=5).fit(graph)
        gap = dm.spectral_gap

        assert 0.0 <= gap <= 1.0

    def test_fiedler_vector(self):
        """Fiedler vector should exist for non-trivial graphs."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph, DiffusionMap
        )

        graph = StateGraph()
        # Create two clusters connected by one edge
        for i in range(5):
            graph.add_edge(f"cluster1_{i}", f"cluster1_{(i+1) % 5}", 1.0)
        for i in range(5):
            graph.add_edge(f"cluster2_{i}", f"cluster2_{(i+1) % 5}", 1.0)
        graph.add_edge("cluster1_0", "cluster2_0", 0.1)  # Weak connection

        dm = DiffusionMap(n_components=5).fit(graph)
        fiedler = dm.get_fiedler_vector()

        assert fiedler is not None
        assert len(fiedler) == 10  # 10 nodes


class TestSpectralPartitioner:
    """Tests for SpectralPartitioner class."""

    def _create_tree_states(self, depth: int = 3, branching: int = 2) -> Dict[str, MockProofState]:
        """Create a balanced tree of states for testing."""
        states = {}

        def add_children(parent_id: str, current_depth: int):
            if current_depth >= depth:
                return

            parent = states[parent_id]
            for i in range(branching):
                child_id = f"{parent_id}_c{i}"
                child = MockProofState(
                    state_id=child_id,
                    parent_id=parent_id,
                    depth=current_depth + 1,
                    value_estimate=0.5 + np.random.uniform(-0.2, 0.2)
                )
                states[child_id] = child
                parent.children.append(child_id)
                add_children(child_id, current_depth + 1)

        # Create root
        root = MockProofState(state_id="root", depth=0, value_estimate=0.8)
        states["root"] = root
        add_children("root", 0)

        return states

    def test_empty_states(self):
        """Partitioner should handle empty state dict."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            SpectralPartitioner, PartitionStrategy
        )

        partitioner = SpectralPartitioner().fit({})
        assignment = partitioner.partition(4, PartitionStrategy.SPECTRAL)

        assert assignment.num_workers == 4
        assert len(assignment.partitions) == 4
        assert all(len(p) == 0 for p in assignment.partitions)

    def test_single_state(self):
        """Single state should go to first partition."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            SpectralPartitioner, PartitionStrategy
        )

        states = {"single": MockProofState(state_id="single")}
        partitioner = SpectralPartitioner().fit(states)
        assignment = partitioner.partition(4, PartitionStrategy.SPECTRAL)

        total_states = sum(len(p) for p in assignment.partitions)
        assert total_states == 1

    def test_partition_covers_all_states(self):
        """Partitions should cover all states exactly once."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            SpectralPartitioner, PartitionStrategy
        )

        states = self._create_tree_states(depth=4, branching=3)
        partitioner = SpectralPartitioner().fit(states)
        assignment = partitioner.partition(4, PartitionStrategy.SPECTRAL)

        # Collect all partitioned states
        all_partitioned = set()
        for p in assignment.partitions:
            # No overlap
            assert len(all_partitioned & p.state_ids) == 0
            all_partitioned.update(p.state_ids)

        # All states covered
        assert all_partitioned == set(states.keys())

    def test_partition_strategies(self):
        """All partition strategies should produce valid partitions."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            SpectralPartitioner, PartitionStrategy
        )

        states = self._create_tree_states(depth=3, branching=2)

        for strategy in PartitionStrategy:
            partitioner = SpectralPartitioner().fit(states)
            assignment = partitioner.partition(4, strategy)

            total_states = sum(len(p) for p in assignment.partitions)
            assert total_states == len(states), f"Strategy {strategy} failed"

    def test_worker_assignment_methods(self):
        """WorkerAssignment should provide correct state lookups."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            SpectralPartitioner, PartitionStrategy
        )

        states = self._create_tree_states(depth=3, branching=2)
        partitioner = SpectralPartitioner().fit(states)
        assignment = partitioner.partition(4, PartitionStrategy.SPECTRAL)

        # Test get_worker_states
        for worker_id in range(4):
            worker_states = assignment.get_worker_states(worker_id)
            assert isinstance(worker_states, set)

        # Test find_worker
        for state_id in list(states.keys())[:5]:
            worker_id = assignment.find_worker(state_id)
            if worker_id is not None:
                assert state_id in assignment.get_worker_states(worker_id)


class TestConvenienceFunction:
    """Tests for partition_for_parallel_search function."""

    def test_convenience_function(self):
        """Test the convenience function wrapper."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            partition_for_parallel_search
        )

        # Create simple states
        states = {
            f"state_{i}": MockProofState(
                state_id=f"state_{i}",
                value_estimate=0.5 + i * 0.05
            )
            for i in range(20)
        }

        assignment = partition_for_parallel_search(states, num_workers=4)

        assert assignment.num_workers == 4
        total = sum(len(p) for p in assignment.partitions)
        assert total == 20


class TestNumericalStability:
    """Tests for numerical edge cases."""

    def test_identical_values(self):
        """Handle states with identical value estimates."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            SpectralPartitioner
        )

        states = {
            f"state_{i}": MockProofState(
                state_id=f"state_{i}",
                value_estimate=0.5  # All identical
            )
            for i in range(20)
        }

        # Add edges
        for i in range(19):
            states[f"state_{i}"].children.append(f"state_{i+1}")
            states[f"state_{i+1}"].parent_id = f"state_{i}"

        partitioner = SpectralPartitioner().fit(states)
        assignment = partitioner.partition(4)

        # Should not crash
        assert assignment.num_workers == 4

    def test_disconnected_components(self):
        """Handle graphs with disconnected components."""
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            StateGraph, DiffusionMap
        )

        graph = StateGraph()

        # Component 1
        for i in range(5):
            graph.add_edge(f"comp1_{i}", f"comp1_{(i+1) % 5}", 1.0)

        # Component 2 (disconnected)
        for i in range(5):
            graph.add_edge(f"comp2_{i}", f"comp2_{(i+1) % 5}", 1.0)

        dm = DiffusionMap(n_components=5).fit(graph)

        # Should not crash
        coords = dm.get_coordinates()
        assert coords.shape[0] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
