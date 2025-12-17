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
Search Tree Manager
====================

Agent 2.3 of the Deep Search Team

Manages the Product-Node search architecture. Tracks state of thousands
of parallel proof attempts, prioritizing "promising" branches (per Critic)
and suspending low-value paths.

Key Methods:
- MCTS-style expansion
- UCB1 selection
- Parallel proof state checkpointing

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 2
Reference: Phase_6_Build_Order_Breakdown.md, Step 2
"""

import math
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .policy_network import PolicyNetwork, TacticCandidate
from .critic_network import CriticNetwork
from .types import ProofState, SearchResult, SearchStatus
# NOTE: MockProver removed from production - use tests.mocks.MockProver for testing
from .prover_engine import ProverEngine, SymPyProver
from .spectral_partitioner import (
    SpectralPartitioner, WorkerAssignment, PartitionStrategy,
    partition_for_parallel_search
)


class SearchTreeManager:
    """
    Agent 2.3: Search Tree Manager - MCTS-style proof search

    Manages the Product-Node search architecture for automated
    theorem proving. Uses UCB1 for exploration-exploitation tradeoff
    and value estimates from CriticNetwork to prioritize branches.

    Key capabilities:
    - MCTS-style tree expansion
    - UCB1 node selection
    - Parallel proof state management
    - Checkpoint and resume functionality
    - Resource-bounded search

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    def __init__(
        self,
        policy_network: PolicyNetwork = None,
        critic_network: CriticNetwork = None,
        prover_engine: ProverEngine = None,
        exploration_constant: float = 1.4,
        max_depth: int = 50,
        prune_threshold: float = 0.05
    ):
        """
        Initialize the Search Tree Manager.

        Args:
            policy_network: PolicyNetwork for generating tactics
            critic_network: CriticNetwork for evaluating states
            prover_engine: Engine for applying tactics (SymPy, Mock, etc.)
            exploration_constant: UCB1 exploration constant (c_puct)
            max_depth: Maximum search depth
            prune_threshold: Prune states with value below this
        """
        self.policy = policy_network or PolicyNetwork()
        self.critic = critic_network or CriticNetwork()
        self.prover_engine = prover_engine or SymPyProver()
        self.c_puct = exploration_constant
        self.max_depth = max_depth
        self.prune_threshold = prune_threshold

        # Search tree storage
        self.states: Dict[str, ProofState] = {}
        self.root_id: Optional[str] = None

        # Statistics
        self.stats = {
            'total_searches': 0,
            'successful_proofs': 0,
            'total_expansions': 0,
            'total_simulations': 0,
            'max_depth_reached': 0,
            'states_pruned': 0,
            'average_proof_length': 0.0
        }
        self._proof_lengths = []

    def initialize_search(self, conjecture) -> str:
        """
        Initialize search tree with root state from conjecture.

        Args:
            conjecture: CandidateConjecture object

        Returns:
            Root state ID
        """
        # Clear previous search
        self.states.clear()

        # Extract goal and hypotheses from conjecture
        if hasattr(conjecture, 'lean4_statement'):
            goal = conjecture.lean4_statement or str(conjecture.source_theorem.conclusion)
        else:
            goal = str(conjecture)

        if hasattr(conjecture, 'source_theorem'):
            hypotheses = [str(p) for p in conjecture.source_theorem.premises]
        else:
            hypotheses = []

        # Create root state
        root_id = f"root_{uuid.uuid4().hex[:8]}"
        root_state = ProofState(
            state_id=root_id,
            goal=goal,
            hypotheses=hypotheses,
            depth=0
        )

        # Get initial value estimate
        root_state.value_estimate = self.critic.evaluate(root_state)

        self.states[root_id] = root_state
        self.root_id = root_id
        self.stats['total_searches'] += 1

        return root_id

    def search(
        self,
        num_simulations: int = 1000,
        timeout_ms: int = None,
        max_expansions: int = None
    ) -> SearchResult:
        """
        Run MCTS-style search for proof.

        Args:
            num_simulations: Number of MCTS simulations to run
            timeout_ms: Optional timeout in milliseconds
            max_expansions: Optional maximum expansions

        Returns:
            SearchResult with proof if found
        """
        start_time = time.time()
        expansions = 0

        for sim in range(num_simulations):
            # Check timeout
            if timeout_ms and (time.time() - start_time) * 1000 > timeout_ms:
                break

            # Check expansion limit
            if max_expansions and expansions >= max_expansions:
                break

            # Selection: traverse tree using UCB1
            leaf_id = self._select()

            if leaf_id is None:
                break

            leaf = self.states[leaf_id]

            # Check if proven
            if leaf.is_proven:
                return self._build_success_result(leaf_id, start_time)

            # Expansion: add new states
            if not leaf.is_terminal and leaf.depth < self.max_depth:
                child_ids = self._expand(leaf_id)
                expansions += len(child_ids)
                self.stats['total_expansions'] += len(child_ids)

                # Evaluate new states
                for child_id in child_ids:
                    child = self.states[child_id]
                    child.value_estimate = self.critic.evaluate(child)

                    # Check if any child is proven
                    if child.is_proven:
                        return self._build_success_result(child_id, start_time)

                    # Prune low-value states
                    if child.value_estimate < self.prune_threshold:
                        child.is_terminal = True
                        self.stats['states_pruned'] += 1

            # Backpropagation: update values up the tree
            self._backpropagate(leaf_id)

            self.stats['total_simulations'] += 1

        # Search complete without proof
        elapsed_ms = (time.time() - start_time) * 1000

        # Determine status
        if timeout_ms and elapsed_ms >= timeout_ms:
            status = SearchStatus.TIMEOUT
        elif max_expansions and expansions >= max_expansions:
            status = SearchStatus.RESOURCE_LIMIT
        else:
            status = SearchStatus.COMPLETED

        return SearchResult(
            success=False,
            proof_steps=[],
            states_explored=len(self.states),
            max_depth_reached=self._get_max_depth(),
            time_elapsed_ms=elapsed_ms,
            status=status,
            value_at_root=self.states[self.root_id].value_estimate if self.root_id else 0.5
        )

    def _select(self) -> Optional[str]:
        """Select leaf node using UCB1"""
        if self.root_id is None:
            return None

        current_id = self.root_id

        while True:
            state = self.states[current_id]

            # If leaf or terminal, return
            if state.is_leaf() or state.is_terminal:
                return current_id

            # UCB1 selection among children
            best_child = None
            best_score = -float('inf')

            for child_id in state.children:
                child = self.states[child_id]

                # Skip pruned/terminal children
                if child.is_terminal and not child.is_proven:
                    continue

                # UCB1 formula
                exploitation = child.value_estimate
                exploration = self.c_puct * math.sqrt(
                    math.log(state.visit_count + 1) / (child.visit_count + 1)
                )
                score = exploitation + exploration

                if score > best_score:
                    best_score = score
                    best_child = child_id

            if best_child is None:
                # All children are dead ends
                state.is_terminal = True
                return None

            current_id = best_child

    def _expand(self, state_id: str) -> List[str]:
        """Expand state with new children"""
        state = self.states[state_id]

        # Generate candidate tactics
        tactics = self.policy.generate_tactics(state, top_k=5)

        child_ids = []
        for tactic in tactics:
            child_id = f"{state_id}_{uuid.uuid4().hex[:6]}"

            # Apply tactic using ProverEngine
            new_goal, is_proven = self._apply_tactic(state, tactic)

            child_state = ProofState(
                state_id=child_id,
                goal=new_goal,
                hypotheses=state.hypotheses.copy(),
                depth=state.depth + 1,
                parent_id=state_id,
                tactic_applied=tactic.tactic,
                is_proven=is_proven,
                is_terminal=is_proven  # Terminal if proven
            )

            self.states[child_id] = child_state
            state.children.append(child_id)
            child_ids.append(child_id)

        # Update max depth
        if state.depth + 1 > self.stats['max_depth_reached']:
            self.stats['max_depth_reached'] = state.depth + 1

        return child_ids

    def _apply_tactic(self, state: ProofState, tactic: TacticCandidate) -> Tuple[str, bool]:
        """
        Apply a tactic to a proof state using the ProverEngine.
        """
        return self.prover_engine.apply_tactic(state, tactic)

    def _backpropagate(self, leaf_id: str):
        """Backpropagate value estimates up the tree"""
        current_id = leaf_id

        while current_id is not None:
            state = self.states[current_id]
            state.visit_count += 1

            # Update value based on children
            if state.children:
                child_values = [
                    self.states[c].value_estimate
                    for c in state.children
                    if not self.states[c].is_terminal or self.states[c].is_proven
                ]
                if child_values:
                    # Use max of children (optimistic)
                    state.value_estimate = max(child_values)

            current_id = state.parent_id

    def _build_success_result(self, proven_state_id: str, start_time: float) -> SearchResult:
        """Build success result by tracing back from proven state"""
        proof_steps = self._extract_proof(proven_state_id)

        elapsed_ms = (time.time() - start_time) * 1000

        self.stats['successful_proofs'] += 1
        self._proof_lengths.append(len(proof_steps))
        self.stats['average_proof_length'] = sum(self._proof_lengths) / len(self._proof_lengths)

        return SearchResult(
            success=True,
            proof_steps=proof_steps,
            states_explored=len(self.states),
            max_depth_reached=self._get_max_depth(),
            time_elapsed_ms=elapsed_ms,
            status=SearchStatus.COMPLETED,
            value_at_root=self.states[self.root_id].value_estimate if self.root_id else 1.0
        )

    def _extract_proof(self, success_state_id: str) -> List[str]:
        """Extract proof steps from successful path"""
        proof_steps = []
        current_id = success_state_id

        while current_id is not None:
            state = self.states[current_id]
            if state.tactic_applied:
                proof_steps.append(state.tactic_applied)
            current_id = state.parent_id

        proof_steps.reverse()
        return proof_steps

    def _get_max_depth(self) -> int:
        """Get maximum depth reached in current tree"""
        if not self.states:
            return 0
        return max(s.depth for s in self.states.values())

    def get_tree_summary(self) -> Dict[str, Any]:
        """Get summary of current search tree"""
        if not self.states:
            return {'empty': True}

        depths = [s.depth for s in self.states.values()]
        values = [s.value_estimate for s in self.states.values()]
        terminal_count = sum(1 for s in self.states.values() if s.is_terminal)
        proven_count = sum(1 for s in self.states.values() if s.is_proven)

        return {
            'total_states': len(self.states),
            'max_depth': max(depths),
            'avg_depth': sum(depths) / len(depths),
            'avg_value': sum(values) / len(values),
            'terminal_states': terminal_count,
            'proven_states': proven_count,
            'root_value': self.states[self.root_id].value_estimate if self.root_id else 0
        }

    def checkpoint(self) -> Dict[str, Any]:
        """Create checkpoint of current search state"""
        return {
            'root_id': self.root_id,
            'states': {sid: s.to_dict() for sid, s in self.states.items()},
            'stats': self.stats.copy()
        }

    def restore(self, checkpoint: Dict[str, Any]):
        """Restore search state from checkpoint"""
        self.root_id = checkpoint['root_id']
        self.stats = checkpoint['stats'].copy()

        self.states.clear()
        for sid, data in checkpoint['states'].items():
            self.states[sid] = ProofState(
                state_id=data['state_id'],
                goal=data['goal'],
                hypotheses=data['hypotheses'],
                depth=data['depth'],
                parent_id=data.get('parent_id'),
                tactic_applied=data.get('tactic_applied'),
                value_estimate=data.get('value_estimate', 0.5),
                visit_count=data.get('visit_count', 0),
                is_terminal=data.get('is_terminal', False),
                is_proven=data.get('is_proven', False)
            )

    def get_statistics(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            **self.stats,
            'current_tree_size': len(self.states),
            'policy_stats': self.policy.get_statistics(),
            'critic_stats': self.critic.get_statistics(),
            'prover_engine': self.prover_engine.__class__.__name__
        }

    def reset(self):
        """Reset manager state"""
        self.states.clear()
        self.root_id = None
        self._proof_lengths.clear()
        for key in ['total_expansions', 'total_simulations', 'max_depth_reached', 'states_pruned']:
            self.stats[key] = 0

    def health_check(self) -> bool:
        """Check if manager is healthy"""
        return (
            self.policy.health_check() and
            self.critic.health_check() and
            self.prover_engine.health_check()
        )

    # =========================================================================
    # SPECTRAL PARTITIONING FOR PARALLEL SEARCH
    # =========================================================================

    def get_worker_assignment(
        self,
        num_workers: int,
        strategy: PartitionStrategy = PartitionStrategy.SPECTRAL
    ) -> WorkerAssignment:
        """
        Partition current search tree for parallel workers.

        Uses spectral clustering (diffusion maps) to find non-overlapping
        regions of the search space. Each worker explores its assigned
        region, reducing redundant exploration by 10-30%.

        Args:
            num_workers: Number of parallel workers
            strategy: Partitioning strategy (SPECTRAL, BALANCED, VALUE_WEIGHTED)

        Returns:
            WorkerAssignment mapping state partitions to workers

        Example:
            assignment = manager.get_worker_assignment(4)
            for worker_id in range(4):
                frontier = assignment.get_worker_states(worker_id)
                # Worker explores only states in its partition
        """
        if len(self.states) < num_workers * 2:
            # Not enough states to partition meaningfully
            return self._fallback_assignment(num_workers)

        return partition_for_parallel_search(
            self.states,
            num_workers,
            strategy
        )

    def _fallback_assignment(self, num_workers: int) -> WorkerAssignment:
        """Simple round-robin assignment when tree is too small for spectral."""
        from .spectral_partitioner import Partition

        partitions = [Partition(i, set()) for i in range(num_workers)]
        for i, state_id in enumerate(self.states.keys()):
            partitions[i % num_workers].state_ids.add(state_id)

        return WorkerAssignment(num_workers=num_workers, partitions=partitions)

    def get_frontier_for_worker(
        self,
        worker_id: int,
        assignment: WorkerAssignment
    ) -> List[str]:
        """
        Get expandable frontier states for a specific worker.

        Returns leaf nodes within the worker's partition, sorted by value
        (highest first) for prioritized exploration.

        Args:
            worker_id: Worker index (0 to num_workers-1)
            assignment: WorkerAssignment from get_worker_assignment()

        Returns:
            List of state IDs to explore, ordered by priority
        """
        worker_states = assignment.get_worker_states(worker_id)

        # Find leaves within worker's partition
        frontier = []
        for state_id in worker_states:
            if state_id not in self.states:
                continue
            state = self.states[state_id]
            if state.is_leaf() and not state.is_terminal:
                frontier.append((state_id, state.value_estimate))

        # Sort by value (descending)
        frontier.sort(key=lambda x: -x[1])
        return [sid for sid, _ in frontier]

    def parallel_search_step(
        self,
        worker_id: int,
        assignment: WorkerAssignment,
        expansions_per_step: int = 5
    ) -> Tuple[List[str], bool]:
        """
        Execute one parallel search step for a worker.

        Each worker expands its highest-value frontier states within
        its assigned partition. Returns new state IDs and whether
        proof was found.

        Args:
            worker_id: Worker index
            assignment: Current worker assignment
            expansions_per_step: Max states to expand this step

        Returns:
            (new_state_ids, proof_found)
        """
        frontier = self.get_frontier_for_worker(worker_id, assignment)
        new_states = []
        proof_found = False

        for state_id in frontier[:expansions_per_step]:
            state = self.states[state_id]

            if state.depth >= self.max_depth:
                continue

            # Expand this state
            child_ids = self._expand(state_id)

            for child_id in child_ids:
                child = self.states[child_id]
                child.value_estimate = self.critic.evaluate(child)

                if child.is_proven:
                    proof_found = True

                if child.value_estimate < self.prune_threshold:
                    child.is_terminal = True
                    self.stats['states_pruned'] += 1

            new_states.extend(child_ids)
            self._backpropagate(state_id)

        return new_states, proof_found

    def recommend_worker_count(self) -> int:
        """
        Recommend number of workers based on tree structure.

        Uses spectral gap to estimate clusterability:
        - High gap (>0.3): Many distinct regions, use more workers
        - Low gap (<0.1): Homogeneous tree, fewer workers help

        Returns:
            Recommended worker count (1 to 16)
        """
        if len(self.states) < 20:
            return 1

        partitioner = SpectralPartitioner().fit(self.states)
        gap = partitioner.get_spectral_gap()

        # Heuristic: more workers for more clusterable trees
        if gap > 0.4:
            return min(16, len(self.states) // 50 + 4)
        elif gap > 0.2:
            return min(8, len(self.states) // 100 + 2)
        elif gap > 0.1:
            return min(4, len(self.states) // 200 + 1)
        else:
            return max(1, len(self.states) // 500)

    def get_partition_summary(self, assignment: WorkerAssignment) -> Dict[str, Any]:
        """
        Get summary statistics for a worker assignment.

        Useful for debugging and monitoring parallel search efficiency.
        """
        summaries = []
        for p in assignment.partitions:
            leaf_count = sum(
                1 for sid in p.state_ids
                if sid in self.states and self.states[sid].is_leaf()
            )
            summaries.append({
                'partition_id': p.partition_id,
                'size': len(p),
                'leaf_count': leaf_count,
                'total_value': p.total_value,
                'centroid': p.centroid_id
            })

        return {
            'num_workers': assignment.num_workers,
            'total_states': len(self.states),
            'partitions': summaries,
            'balance_ratio': min(len(p) for p in assignment.partitions) /
                            max(len(p) for p in assignment.partitions)
                            if assignment.partitions and max(len(p) for p in assignment.partitions) > 0
                            else 1.0
        }
