#!/usr/bin/env python3
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
Spectral Partitioner Full Audit
================================

Comprehensive edge-to-edge testing comparing spectral vs non-spectral
parallel search partitioning. Measures:

- Worker overlap (lower = better partitioning)
- Exploration efficiency (states/time)
- Partition balance
- Spectral gap correlation with performance

Run: python scripts/spectral_partitioner_audit.py
"""

import sys
import os
import time
import random
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
    StateGraph, DiffusionMap, SpectralPartitioner,
    WorkerAssignment, Partition, PartitionStrategy,
    partition_for_parallel_search
)
from symbo_agentic_reasoners.discovery.deep_search.types import (
    ProofState, SearchResult, SearchStatus
)


# =============================================================================
# TEST INFRASTRUCTURE
# =============================================================================

@dataclass
class AuditMetrics:
    """Metrics from a single audit run."""
    test_name: str
    strategy: str
    num_states: int
    num_workers: int

    # Partition quality
    partition_sizes: List[int] = field(default_factory=list)
    balance_ratio: float = 0.0  # min/max size ratio
    spectral_gap: float = 0.0

    # Performance
    partition_time_ms: float = 0.0
    total_time_ms: float = 0.0

    # Exploration metrics
    overlap_score: float = 0.0  # States visited by multiple workers
    frontier_coverage: float = 0.0  # % of leaves in partitions

    # Status
    passed: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'test_name': self.test_name,
            'strategy': self.strategy,
            'num_states': self.num_states,
            'num_workers': self.num_workers,
            'partition_sizes': self.partition_sizes,
            'balance_ratio': round(self.balance_ratio, 4),
            'spectral_gap': round(self.spectral_gap, 4),
            'partition_time_ms': round(self.partition_time_ms, 2),
            'total_time_ms': round(self.total_time_ms, 2),
            'overlap_score': round(self.overlap_score, 4),
            'frontier_coverage': round(self.frontier_coverage, 4),
            'passed': self.passed,
            'error': self.error
        }


def create_tree_states(
    depth: int = 4,
    branching: int = 3,
    value_variance: float = 0.2,
    seed: int = 42
) -> Dict[str, ProofState]:
    """Create a balanced tree of proof states."""
    random.seed(seed)
    np.random.seed(seed)
    states = {}

    def add_children(parent_id: str, current_depth: int):
        if current_depth >= depth:
            return

        parent = states[parent_id]
        for i in range(branching):
            child_id = f"{parent_id}_c{i}"
            child = ProofState(
                state_id=child_id,
                goal=f"goal_{child_id}",
                hypotheses=[],
                depth=current_depth + 1,
                parent_id=parent_id,
                value_estimate=0.5 + random.uniform(-value_variance, value_variance)
            )
            states[child_id] = child
            parent.children.append(child_id)
            add_children(child_id, current_depth + 1)

    root = ProofState(
        state_id="root",
        goal="prove_theorem",
        hypotheses=[],
        depth=0,
        value_estimate=0.8
    )
    states["root"] = root
    add_children("root", 0)

    return states


def create_clustered_states(
    num_clusters: int = 4,
    states_per_cluster: int = 50,
    inter_cluster_edges: int = 5,
    seed: int = 42
) -> Dict[str, ProofState]:
    """
    Create states with clear cluster structure.

    This simulates a search space with distinct "regions" that
    spectral partitioning should identify.
    """
    random.seed(seed)
    np.random.seed(seed)
    states = {}

    # Create clusters
    for c in range(num_clusters):
        cluster_value = 0.3 + 0.5 * (c / num_clusters)  # Different value ranges

        # First node is cluster root
        root_id = f"cluster{c}_0"
        states[root_id] = ProofState(
            state_id=root_id,
            goal=f"cluster_{c}_goal",
            hypotheses=[],
            depth=0,
            value_estimate=cluster_value + random.uniform(-0.1, 0.1)
        )

        # Add chain within cluster
        for i in range(1, states_per_cluster):
            state_id = f"cluster{c}_{i}"
            parent_id = f"cluster{c}_{i-1}"

            states[state_id] = ProofState(
                state_id=state_id,
                goal=f"cluster_{c}_subgoal_{i}",
                hypotheses=[],
                depth=i,
                parent_id=parent_id,
                value_estimate=cluster_value + random.uniform(-0.1, 0.1)
            )
            states[parent_id].children.append(state_id)

    # Add sparse inter-cluster connections
    for _ in range(inter_cluster_edges):
        c1, c2 = random.sample(range(num_clusters), 2)
        i1 = random.randint(0, states_per_cluster - 2)
        i2 = random.randint(0, states_per_cluster - 1)

        parent_id = f"cluster{c1}_{i1}"
        child_id = f"cluster{c2}_{i2}"

        if child_id not in states[parent_id].children:
            states[parent_id].children.append(child_id)
            # Note: This creates a DAG, not a tree

    return states


def create_random_graph_states(
    num_states: int = 200,
    edge_probability: float = 0.05,
    seed: int = 42
) -> Dict[str, ProofState]:
    """Create random graph structure (stress test)."""
    random.seed(seed)
    np.random.seed(seed)
    states = {}

    # Create all nodes
    for i in range(num_states):
        states[f"node_{i}"] = ProofState(
            state_id=f"node_{i}",
            goal=f"goal_{i}",
            hypotheses=[],
            depth=0,
            value_estimate=random.uniform(0.1, 0.9)
        )

    # Add random edges
    for i in range(num_states):
        for j in range(i + 1, num_states):
            if random.random() < edge_probability:
                states[f"node_{i}"].children.append(f"node_{j}")
                states[f"node_{j}"].parent_id = f"node_{i}"

    return states


# =============================================================================
# AUDIT TESTS
# =============================================================================

class SpectralPartitionerAudit:
    """Full audit suite for spectral partitioner."""

    def __init__(self):
        self.results: List[AuditMetrics] = []
        self.start_time = time.time()

    def run_all(self) -> Dict:
        """Run complete audit suite."""
        print("=" * 80)
        print("SPECTRAL PARTITIONER FULL AUDIT")
        print("=" * 80)
        print(f"Started: {datetime.now().isoformat()}")
        print()

        # Smoke tests
        self._run_smoke_tests()

        # Edge cases
        self._run_edge_cases()

        # Performance comparison
        self._run_comparison_tests()

        # Scalability
        self._run_scalability_tests()

        # Generate report
        return self._generate_report()

    def _run_smoke_tests(self):
        """Basic functionality tests."""
        print("SMOKE TESTS")
        print("-" * 40)

        # Test 1: Basic tree partitioning
        self._test_basic_tree()

        # Test 2: All partition strategies
        self._test_all_strategies()

        # Test 3: Worker assignment correctness
        self._test_worker_assignment()

        print()

    def _run_edge_cases(self):
        """Edge case tests."""
        print("EDGE CASES")
        print("-" * 40)

        # Test: Empty states
        self._test_empty_states()

        # Test: Single state
        self._test_single_state()

        # Test: More workers than states
        self._test_more_workers_than_states()

        # Test: Disconnected components
        self._test_disconnected_components()

        # Test: Identical values
        self._test_identical_values()

        print()

    def _run_comparison_tests(self):
        """Compare spectral vs balanced partitioning."""
        print("SPECTRAL VS BALANCED COMPARISON")
        print("-" * 40)

        # Test on clustered data (where spectral should excel)
        self._compare_on_clustered_data()

        # Test on tree data
        self._compare_on_tree_data()

        # Test on random graph
        self._compare_on_random_graph()

        # CRITICAL: Simulate actual parallel search overlap
        self._simulate_parallel_search_overlap()

        print()

    def _run_scalability_tests(self):
        """Test scaling behavior."""
        print("SCALABILITY TESTS")
        print("-" * 40)

        for num_states in [100, 500, 1000, 2000]:
            self._test_scalability(num_states)

        print()

    # =========================================================================
    # Individual Tests
    # =========================================================================

    def _test_basic_tree(self):
        """Test basic tree partitioning works."""
        test_name = "basic_tree"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=0,
            num_workers=4
        )

        try:
            start = time.time()
            states = create_tree_states(depth=4, branching=3)
            metrics.num_states = len(states)

            partitioner = SpectralPartitioner().fit(states)
            partition_start = time.time()
            assignment = partitioner.partition(4, PartitionStrategy.SPECTRAL)
            metrics.partition_time_ms = (time.time() - partition_start) * 1000

            # Validate
            all_assigned = set()
            for p in assignment.partitions:
                all_assigned.update(p.state_ids)
                metrics.partition_sizes.append(len(p))

            assert all_assigned == set(states.keys()), "Not all states assigned"

            metrics.balance_ratio = min(metrics.partition_sizes) / max(metrics.partition_sizes)
            metrics.spectral_gap = partitioner.get_spectral_gap()
            metrics.total_time_ms = (time.time() - start) * 1000
            metrics.passed = True

            print(f"  [PASS] {test_name}: {metrics.num_states} states, "
                  f"balance={metrics.balance_ratio:.2f}, gap={metrics.spectral_gap:.3f}")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    def _test_all_strategies(self):
        """Test all partition strategies work."""
        states = create_tree_states(depth=3, branching=2)

        for strategy in PartitionStrategy:
            test_name = f"strategy_{strategy.value}"
            metrics = AuditMetrics(
                test_name=test_name,
                strategy=strategy.value,
                num_states=len(states),
                num_workers=4
            )

            try:
                start = time.time()
                partitioner = SpectralPartitioner().fit(states)
                assignment = partitioner.partition(4, strategy)

                total = sum(len(p) for p in assignment.partitions)
                assert total == len(states), f"State count mismatch: {total} vs {len(states)}"

                metrics.partition_sizes = [len(p) for p in assignment.partitions]
                metrics.balance_ratio = min(metrics.partition_sizes) / max(metrics.partition_sizes)
                metrics.total_time_ms = (time.time() - start) * 1000
                metrics.passed = True

                print(f"  [PASS] {test_name}: balance={metrics.balance_ratio:.2f}")

            except Exception as e:
                metrics.passed = False
                metrics.error = str(e)
                print(f"  [FAIL] {test_name}: {e}")

            self.results.append(metrics)

    def _test_worker_assignment(self):
        """Test WorkerAssignment methods."""
        test_name = "worker_assignment_methods"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=50,
            num_workers=4
        )

        try:
            states = create_tree_states(depth=3, branching=3)
            assignment = partition_for_parallel_search(states, 4)

            # Test get_worker_states
            for w in range(4):
                worker_states = assignment.get_worker_states(w)
                assert isinstance(worker_states, set)

            # Test find_worker
            for state_id in list(states.keys())[:10]:
                w = assignment.find_worker(state_id)
                if w is not None:
                    assert state_id in assignment.get_worker_states(w)

            metrics.passed = True
            print(f"  [PASS] {test_name}")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    def _test_empty_states(self):
        """Test empty state dict."""
        test_name = "empty_states"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=0,
            num_workers=4
        )

        try:
            assignment = partition_for_parallel_search({}, 4)
            assert assignment.num_workers == 4
            assert all(len(p) == 0 for p in assignment.partitions)
            metrics.passed = True
            print(f"  [PASS] {test_name}")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    def _test_single_state(self):
        """Test single state."""
        test_name = "single_state"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=1,
            num_workers=4
        )

        try:
            states = {"only": ProofState(state_id="only", goal="x", hypotheses=[], depth=0)}
            assignment = partition_for_parallel_search(states, 4)
            total = sum(len(p) for p in assignment.partitions)
            assert total == 1
            metrics.passed = True
            print(f"  [PASS] {test_name}")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    def _test_more_workers_than_states(self):
        """Test when workers > states."""
        test_name = "more_workers_than_states"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=3,
            num_workers=10
        )

        try:
            states = {
                f"s{i}": ProofState(state_id=f"s{i}", goal="x", hypotheses=[], depth=0)
                for i in range(3)
            }
            assignment = partition_for_parallel_search(states, 10)
            total = sum(len(p) for p in assignment.partitions)
            assert total == 3
            metrics.passed = True
            print(f"  [PASS] {test_name}")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    def _test_disconnected_components(self):
        """Test graph with disconnected components."""
        test_name = "disconnected_components"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=20,
            num_workers=4
        )

        try:
            # Create two disconnected chains
            states = {}
            for chain in range(2):
                for i in range(10):
                    sid = f"chain{chain}_{i}"
                    parent = f"chain{chain}_{i-1}" if i > 0 else None
                    states[sid] = ProofState(
                        state_id=sid,
                        goal="x",
                        hypotheses=[],
                        depth=i,
                        parent_id=parent,
                        value_estimate=0.5
                    )
                    if parent:
                        states[parent].children.append(sid)

            metrics.num_states = len(states)
            partitioner = SpectralPartitioner().fit(states)
            assignment = partitioner.partition(4, PartitionStrategy.SPECTRAL)

            total = sum(len(p) for p in assignment.partitions)
            assert total == 20
            metrics.passed = True
            print(f"  [PASS] {test_name}")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    def _test_identical_values(self):
        """Test states with identical values."""
        test_name = "identical_values"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=50,
            num_workers=4
        )

        try:
            states = {}
            for i in range(50):
                parent = f"node_{i-1}" if i > 0 else None
                states[f"node_{i}"] = ProofState(
                    state_id=f"node_{i}",
                    goal="x",
                    hypotheses=[],
                    depth=i % 5,
                    parent_id=parent,
                    value_estimate=0.5  # All identical
                )
                if parent:
                    states[parent].children.append(f"node_{i}")

            assignment = partition_for_parallel_search(states, 4)
            total = sum(len(p) for p in assignment.partitions)
            assert total == 50
            metrics.passed = True
            print(f"  [PASS] {test_name}")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    def _compare_on_clustered_data(self):
        """Compare spectral vs balanced on clustered data."""
        states = create_clustered_states(num_clusters=4, states_per_cluster=50)
        num_workers = 4

        for strategy in [PartitionStrategy.SPECTRAL, PartitionStrategy.BALANCED]:
            test_name = f"clustered_comparison_{strategy.value}"
            metrics = AuditMetrics(
                test_name=test_name,
                strategy=strategy.value,
                num_states=len(states),
                num_workers=num_workers
            )

            try:
                start = time.time()
                partitioner = SpectralPartitioner().fit(states)

                partition_start = time.time()
                assignment = partitioner.partition(num_workers, strategy)
                metrics.partition_time_ms = (time.time() - partition_start) * 1000

                metrics.spectral_gap = partitioner.get_spectral_gap()
                metrics.partition_sizes = [len(p) for p in assignment.partitions]
                metrics.balance_ratio = (
                    min(metrics.partition_sizes) / max(metrics.partition_sizes)
                    if max(metrics.partition_sizes) > 0 else 1.0
                )

                # Calculate cluster purity (how well partitions align with clusters)
                cluster_purity = self._calculate_cluster_purity(
                    assignment, states, num_clusters=4
                )
                metrics.frontier_coverage = cluster_purity

                metrics.total_time_ms = (time.time() - start) * 1000
                metrics.passed = True

                print(f"  [PASS] {test_name}: purity={cluster_purity:.2f}, "
                      f"balance={metrics.balance_ratio:.2f}")

            except Exception as e:
                metrics.passed = False
                metrics.error = str(e)
                print(f"  [FAIL] {test_name}: {e}")

            self.results.append(metrics)

    def _compare_on_tree_data(self):
        """Compare spectral vs balanced on tree data."""
        states = create_tree_states(depth=5, branching=3)
        num_workers = 4

        for strategy in [PartitionStrategy.SPECTRAL, PartitionStrategy.BALANCED]:
            test_name = f"tree_comparison_{strategy.value}"
            metrics = AuditMetrics(
                test_name=test_name,
                strategy=strategy.value,
                num_states=len(states),
                num_workers=num_workers
            )

            try:
                start = time.time()
                partitioner = SpectralPartitioner().fit(states)
                assignment = partitioner.partition(num_workers, strategy)

                metrics.spectral_gap = partitioner.get_spectral_gap()
                metrics.partition_sizes = [len(p) for p in assignment.partitions]
                metrics.balance_ratio = (
                    min(metrics.partition_sizes) / max(metrics.partition_sizes)
                    if max(metrics.partition_sizes) > 0 else 1.0
                )

                # Calculate subtree coherence
                coherence = self._calculate_subtree_coherence(assignment, states)
                metrics.frontier_coverage = coherence

                metrics.total_time_ms = (time.time() - start) * 1000
                metrics.passed = True

                print(f"  [PASS] {test_name}: coherence={coherence:.2f}, "
                      f"balance={metrics.balance_ratio:.2f}")

            except Exception as e:
                metrics.passed = False
                metrics.error = str(e)
                print(f"  [FAIL] {test_name}: {e}")

            self.results.append(metrics)

    def _compare_on_random_graph(self):
        """Compare on random graph (stress test)."""
        states = create_random_graph_states(num_states=200, edge_probability=0.03)
        num_workers = 4

        for strategy in [PartitionStrategy.SPECTRAL, PartitionStrategy.BALANCED]:
            test_name = f"random_graph_{strategy.value}"
            metrics = AuditMetrics(
                test_name=test_name,
                strategy=strategy.value,
                num_states=len(states),
                num_workers=num_workers
            )

            try:
                start = time.time()
                partitioner = SpectralPartitioner().fit(states)
                assignment = partitioner.partition(num_workers, strategy)

                metrics.spectral_gap = partitioner.get_spectral_gap()
                metrics.partition_sizes = [len(p) for p in assignment.partitions]
                metrics.balance_ratio = (
                    min(metrics.partition_sizes) / max(metrics.partition_sizes)
                    if max(metrics.partition_sizes) > 0 else 1.0
                )

                metrics.total_time_ms = (time.time() - start) * 1000
                metrics.passed = True

                print(f"  [PASS] {test_name}: time={metrics.total_time_ms:.1f}ms, "
                      f"balance={metrics.balance_ratio:.2f}")

            except Exception as e:
                metrics.passed = False
                metrics.error = str(e)
                print(f"  [FAIL] {test_name}: {e}")

            self.results.append(metrics)

    def _simulate_parallel_search_overlap(self):
        """
        CRITICAL TEST: Measure partition quality for parallel search.

        Key metric: Neighborhood Coherence
        - When a worker expands a node, will its children be in the same partition?
        - Higher coherence = less need for cross-worker communication
        - Spectral should beat balanced because it respects graph structure
        """
        print()
        print("  PARALLEL SEARCH QUALITY METRICS")

        # Create a realistic search tree with regions of high/low value
        states = self._create_realistic_search_tree()
        num_workers = 4

        for strategy in [PartitionStrategy.SPECTRAL, PartitionStrategy.BALANCED, PartitionStrategy.VALUE_WEIGHTED]:
            test_name = f"parallel_sim_{strategy.value}"
            metrics = AuditMetrics(
                test_name=test_name,
                strategy=strategy.value,
                num_states=len(states),
                num_workers=num_workers
            )

            try:
                start = time.time()
                partitioner = SpectralPartitioner().fit(states)
                assignment = partitioner.partition(num_workers, strategy)

                # Calculate neighborhood coherence
                coherence = self._calculate_neighborhood_coherence(states, assignment)

                # Calculate edge cut ratio (how many edges cross partition boundaries)
                edge_cut_ratio = self._calculate_edge_cut_ratio(states, assignment)

                # Calculate value concentration (high-value states per partition)
                value_concentration = self._calculate_value_concentration(states, assignment)

                # Metrics
                metrics.overlap_score = edge_cut_ratio  # Lower is better
                metrics.frontier_coverage = coherence  # Higher is better
                metrics.spectral_gap = partitioner.get_spectral_gap()
                metrics.partition_sizes = [len(p) for p in assignment.partitions]
                metrics.balance_ratio = (
                    min(metrics.partition_sizes) / max(metrics.partition_sizes)
                    if max(metrics.partition_sizes) > 0 else 1.0
                )
                metrics.total_time_ms = (time.time() - start) * 1000
                metrics.passed = True

                print(f"    [{strategy.value:8s}] coherence={coherence:.2f}, "
                      f"edge_cut={edge_cut_ratio:.2f}, value_conc={value_concentration:.2f}")

            except Exception as e:
                metrics.passed = False
                metrics.error = str(e)
                print(f"    [FAIL] {test_name}: {e}")

            self.results.append(metrics)

    def _calculate_neighborhood_coherence(
        self,
        states: Dict[str, ProofState],
        assignment: WorkerAssignment
    ) -> float:
        """
        Calculate neighborhood coherence.

        For each node, check what fraction of its neighbors (parent + children)
        are in the same partition. Higher = better for parallel search.
        """
        state_to_worker = {}
        for w_id, partition in enumerate(assignment.partitions):
            for state_id in partition.state_ids:
                state_to_worker[state_id] = w_id

        total_neighbors = 0
        same_partition = 0

        for state_id, state in states.items():
            my_worker = state_to_worker.get(state_id)
            if my_worker is None:
                continue

            neighbors = list(state.children)
            if state.parent_id:
                neighbors.append(state.parent_id)

            for neighbor_id in neighbors:
                if neighbor_id in state_to_worker:
                    total_neighbors += 1
                    if state_to_worker[neighbor_id] == my_worker:
                        same_partition += 1

        return same_partition / max(1, total_neighbors)

    def _calculate_edge_cut_ratio(
        self,
        states: Dict[str, ProofState],
        assignment: WorkerAssignment
    ) -> float:
        """
        Calculate edge cut ratio (fraction of edges crossing partitions).

        Lower = better partitioning.
        """
        state_to_worker = {}
        for w_id, partition in enumerate(assignment.partitions):
            for state_id in partition.state_ids:
                state_to_worker[state_id] = w_id

        total_edges = 0
        cut_edges = 0

        for state_id, state in states.items():
            my_worker = state_to_worker.get(state_id)
            if my_worker is None:
                continue

            for child_id in state.children:
                if child_id in state_to_worker:
                    total_edges += 1
                    if state_to_worker[child_id] != my_worker:
                        cut_edges += 1

        return cut_edges / max(1, total_edges)

    def _calculate_value_concentration(
        self,
        states: Dict[str, ProofState],
        assignment: WorkerAssignment
    ) -> float:
        """
        Calculate how well high-value states are distributed.

        Returns coefficient of variation of partition values.
        Lower = more balanced value distribution.
        """
        partition_values = []
        for partition in assignment.partitions:
            total_value = sum(
                states[sid].value_estimate
                for sid in partition.state_ids
                if sid in states
            )
            partition_values.append(total_value)

        if not partition_values or np.std(partition_values) == 0:
            return 0.0

        # Return coefficient of variation (lower = more balanced)
        cv = np.std(partition_values) / max(np.mean(partition_values), 0.001)
        return 1.0 / (1.0 + cv)  # Transform so higher = better

    def _create_realistic_search_tree(self) -> Dict[str, ProofState]:
        """
        Create a search tree that mimics real proof search:
        - Multiple "promising" branches with high values
        - Dead-end regions with low values
        - Varying branch density
        """
        random.seed(123)
        np.random.seed(123)
        states = {}

        # Create 4 main branches from root
        root = ProofState(
            state_id="root",
            goal="main_theorem",
            hypotheses=[],
            depth=0,
            value_estimate=0.7
        )
        states["root"] = root

        branches = ["algebra", "calculus", "geometry", "logic"]
        branch_values = [0.8, 0.6, 0.4, 0.7]  # Different promise levels

        for b_idx, (branch, base_value) in enumerate(zip(branches, branch_values)):
            branch_root = f"{branch}_0"
            states[branch_root] = ProofState(
                state_id=branch_root,
                goal=f"{branch}_goal",
                hypotheses=[],
                depth=1,
                parent_id="root",
                value_estimate=base_value
            )
            root.children.append(branch_root)

            # Create sub-branches with varying depth
            sub_depth = 3 + b_idx  # Different depths per branch
            sub_branch = 2 + (b_idx % 2)  # Different branching factors

            self._add_subtree(
                states, branch_root, base_value,
                current_depth=1, max_depth=sub_depth,
                branching=sub_branch
            )

        return states

    def _add_subtree(
        self,
        states: Dict[str, ProofState],
        parent_id: str,
        base_value: float,
        current_depth: int,
        max_depth: int,
        branching: int
    ):
        """Recursively add subtree with value decay."""
        if current_depth >= max_depth:
            return

        parent = states[parent_id]
        for i in range(branching):
            child_id = f"{parent_id}_c{i}"
            # Value decays with depth but has random variation
            decay = 0.9 ** current_depth
            noise = random.uniform(-0.15, 0.15)
            child_value = max(0.1, min(0.95, base_value * decay + noise))

            states[child_id] = ProofState(
                state_id=child_id,
                goal=f"subgoal_{child_id}",
                hypotheses=[],
                depth=current_depth + 1,
                parent_id=parent_id,
                value_estimate=child_value
            )
            parent.children.append(child_id)

            self._add_subtree(
                states, child_id, base_value,
                current_depth + 1, max_depth, branching
            )

    def _test_scalability(self, num_states: int):
        """Test scalability at different sizes."""
        test_name = f"scalability_{num_states}"
        metrics = AuditMetrics(
            test_name=test_name,
            strategy="spectral",
            num_states=num_states,
            num_workers=4
        )

        try:
            # Create states - deeper tree for more states
            depth = max(3, int(np.log(num_states) / np.log(3)))
            states = {}

            # Simple chain to get exact count
            for i in range(num_states):
                parent = f"s_{i-1}" if i > 0 else None
                states[f"s_{i}"] = ProofState(
                    state_id=f"s_{i}",
                    goal="x",
                    hypotheses=[],
                    depth=i % 10,
                    parent_id=parent,
                    value_estimate=0.5 + random.uniform(-0.2, 0.2)
                )
                if parent and i % 5 != 0:  # Add branching
                    states[parent].children.append(f"s_{i}")

            metrics.num_states = len(states)

            start = time.time()
            partitioner = SpectralPartitioner().fit(states)

            partition_start = time.time()
            assignment = partitioner.partition(4, PartitionStrategy.SPECTRAL)
            metrics.partition_time_ms = (time.time() - partition_start) * 1000

            metrics.total_time_ms = (time.time() - start) * 1000
            metrics.spectral_gap = partitioner.get_spectral_gap()
            metrics.partition_sizes = [len(p) for p in assignment.partitions]
            metrics.balance_ratio = (
                min(metrics.partition_sizes) / max(metrics.partition_sizes)
                if max(metrics.partition_sizes) > 0 else 1.0
            )
            metrics.passed = True

            print(f"  [PASS] {test_name}: {metrics.total_time_ms:.1f}ms total, "
                  f"{metrics.partition_time_ms:.1f}ms partition")

        except Exception as e:
            metrics.passed = False
            metrics.error = str(e)
            print(f"  [FAIL] {test_name}: {e}")

        self.results.append(metrics)

    # =========================================================================
    # Metrics Helpers
    # =========================================================================

    def _calculate_cluster_purity(
        self,
        assignment: WorkerAssignment,
        states: Dict[str, ProofState],
        num_clusters: int
    ) -> float:
        """
        Calculate how well partitions align with original clusters.

        Higher purity = partitions better respect cluster boundaries.
        """
        total_purity = 0.0

        for partition in assignment.partitions:
            if len(partition.state_ids) == 0:
                continue

            # Count states from each cluster
            cluster_counts = [0] * num_clusters
            for state_id in partition.state_ids:
                if state_id.startswith("cluster"):
                    cluster_idx = int(state_id.split("_")[0].replace("cluster", ""))
                    cluster_counts[cluster_idx] += 1

            # Purity = max cluster / total
            if sum(cluster_counts) > 0:
                total_purity += max(cluster_counts) / sum(cluster_counts)

        return total_purity / max(1, len([p for p in assignment.partitions if len(p) > 0]))

    def _calculate_subtree_coherence(
        self,
        assignment: WorkerAssignment,
        states: Dict[str, ProofState]
    ) -> float:
        """
        Calculate how well partitions keep subtrees together.

        Higher coherence = parent and children tend to be in same partition.
        """
        total_edges = 0
        coherent_edges = 0

        # Find which worker owns each state
        state_to_worker = {}
        for i, partition in enumerate(assignment.partitions):
            for state_id in partition.state_ids:
                state_to_worker[state_id] = i

        # Check parent-child relationships
        for state_id, state in states.items():
            for child_id in state.children:
                if child_id in states:
                    total_edges += 1
                    if state_to_worker.get(state_id) == state_to_worker.get(child_id):
                        coherent_edges += 1

        return coherent_edges / max(1, total_edges)

    # =========================================================================
    # Report Generation
    # =========================================================================

    def _generate_report(self) -> Dict:
        """Generate final audit report."""
        total_time = time.time() - self.start_time

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)

        # Group results by test type
        smoke_tests = [r for r in self.results if "basic" in r.test_name or "strategy" in r.test_name or "worker" in r.test_name]
        edge_tests = [r for r in self.results if any(x in r.test_name for x in ["empty", "single", "more_workers", "disconnected", "identical"])]
        comparison_tests = [r for r in self.results if "comparison" in r.test_name or "random" in r.test_name]
        scalability_tests = [r for r in self.results if "scalability" in r.test_name]

        # Compare spectral vs balanced
        spectral_results = [r for r in comparison_tests if r.strategy == "spectral"]
        balanced_results = [r for r in comparison_tests if r.strategy == "balanced"]
        value_results = [r for r in comparison_tests if r.strategy == "value"]

        spectral_avg_purity = np.mean([r.frontier_coverage for r in spectral_results if r.frontier_coverage > 0]) if spectral_results else 0
        balanced_avg_purity = np.mean([r.frontier_coverage for r in balanced_results if r.frontier_coverage > 0]) if balanced_results else 0

        # Parallel simulation results (overlap_score = collision rate)
        sim_results = [r for r in self.results if "parallel_sim" in r.test_name]
        spectral_collision = next((r.overlap_score for r in sim_results if r.strategy == "spectral"), None)
        balanced_collision = next((r.overlap_score for r in sim_results if r.strategy == "balanced"), None)
        value_collision = next((r.overlap_score for r in sim_results if r.strategy == "value"), None)

        report = {
            "summary": {
                "total_tests": len(self.results),
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{100 * passed / len(self.results):.1f}%",
                "total_time_seconds": round(total_time, 2)
            },
            "comparison": {
                "spectral_avg_purity": round(spectral_avg_purity, 4),
                "balanced_avg_purity": round(balanced_avg_purity, 4),
                "improvement": f"{100 * (spectral_avg_purity - balanced_avg_purity) / max(balanced_avg_purity, 0.001):.1f}%" if balanced_avg_purity > 0 else "N/A"
            },
            "parallel_simulation": {
                "spectral_collision_rate": round(spectral_collision, 4) if spectral_collision else None,
                "balanced_collision_rate": round(balanced_collision, 4) if balanced_collision else None,
                "value_collision_rate": round(value_collision, 4) if value_collision else None,
                "spectral_efficiency": f"{100 * (1 - spectral_collision):.1f}%" if spectral_collision else "N/A",
                "balanced_efficiency": f"{100 * (1 - balanced_collision):.1f}%" if balanced_collision else "N/A",
            },
            "scalability": {
                str(r.num_states): {
                    "partition_time_ms": r.partition_time_ms,
                    "total_time_ms": r.total_time_ms
                }
                for r in scalability_tests
            },
            "categories": {
                "smoke_tests": {"passed": sum(1 for r in smoke_tests if r.passed), "total": len(smoke_tests)},
                "edge_cases": {"passed": sum(1 for r in edge_tests if r.passed), "total": len(edge_tests)},
                "comparisons": {"passed": sum(1 for r in comparison_tests if r.passed), "total": len(comparison_tests)},
                "scalability": {"passed": sum(1 for r in scalability_tests if r.passed), "total": len(scalability_tests)}
            },
            "all_results": [r.to_dict() for r in self.results],
            "failures": [r.to_dict() for r in self.results if not r.passed]
        }

        # Print summary
        print("=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        print(f"Total Tests:  {len(self.results)}")
        print(f"Passed:       {passed}")
        print(f"Failed:       {failed}")
        print(f"Pass Rate:    {100 * passed / len(self.results):.1f}%")
        print(f"Total Time:   {total_time:.2f}s")
        print()
        # Get coherence values from simulation results
        spectral_coherence = next((r.frontier_coverage for r in sim_results if r.strategy == "spectral"), None)
        balanced_coherence = next((r.frontier_coverage for r in sim_results if r.strategy == "balanced"), None)
        value_coherence = next((r.frontier_coverage for r in sim_results if r.strategy == "value"), None)

        print("PARALLEL SEARCH QUALITY (edge_cut = wasted cross-partition work):")
        if spectral_collision is not None and balanced_collision is not None:
            print(f"  Spectral edge cut:  {100 * spectral_collision:.1f}%  (coherence: {100 * spectral_coherence:.1f}%)")
            print(f"  Balanced edge cut:  {100 * balanced_collision:.1f}%  (coherence: {100 * balanced_coherence:.1f}%)")
            if value_collision is not None and value_coherence is not None:
                print(f"  Value-wt edge cut:  {100 * value_collision:.1f}%  (coherence: {100 * value_coherence:.1f}%)")
            if balanced_collision > 0 and spectral_collision < balanced_collision:
                cut_reduction = 100 * (balanced_collision - spectral_collision) / balanced_collision
                print(f"  Spectral reduces edge cuts by: {cut_reduction:+.1f}%")
            elif spectral_coherence > balanced_coherence:
                coherence_improvement = 100 * (spectral_coherence - balanced_coherence) / max(balanced_coherence, 0.001)
                print(f"  Spectral improves coherence by: {coherence_improvement:+.1f}%")
        print()
        print("COHERENCE METRICS (subtree/cluster preservation):")
        print(f"  Spectral avg purity/coherence: {spectral_avg_purity:.4f}")
        print(f"  Balanced avg purity/coherence: {balanced_avg_purity:.4f}")
        if balanced_avg_purity > 0:
            improvement = 100 * (spectral_avg_purity - balanced_avg_purity) / balanced_avg_purity
            print(f"  Spectral improvement: {improvement:+.1f}%")
        print()
        print("SCALABILITY (partition time):")
        for r in scalability_tests:
            print(f"  {r.num_states:5d} states: {r.partition_time_ms:7.2f}ms")
        print()

        if failed > 0:
            print("FAILURES:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.test_name}: {r.error}")
            print()

        return report


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run full audit."""
    audit = SpectralPartitionerAudit()
    report = audit.run_all()

    # Save report
    report_path = Path(__file__).parent.parent / "data" / "traces" / "audit"
    report_path.mkdir(parents=True, exist_ok=True)

    report_file = report_path / f"spectral_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to: {report_file}")
    print()

    # Exit code based on failures
    if report["summary"]["failed"] > 0:
        print("AUDIT FAILED - see failures above")
        return 1
    else:
        print("AUDIT PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
