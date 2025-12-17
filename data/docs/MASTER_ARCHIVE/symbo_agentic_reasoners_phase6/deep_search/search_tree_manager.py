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
