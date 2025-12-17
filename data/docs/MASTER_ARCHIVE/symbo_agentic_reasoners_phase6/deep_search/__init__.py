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
Deep Search Team - "The Explorer"
===================================

Phase 6, Step 2: Addresses Navigating Infinite Search Spaces

This team implements a Product-Node Search Tree architecture as utilized
by AlphaProof, using Reinforcement Learning to guide search in high-complexity
domains like the IMO Grand Challenge.

Standard "Tree-of-Thoughts" reasoning (Phase 3) is insufficient for open problems
where the solution path is completely unknown.

Agents:
1. PolicyNetwork ("The Tactician") - Generates proof step probabilities
2. CriticNetwork ("The Evaluator") - Evaluates branch promise for pruning
3. SearchTreeManager - Manages parallel proof attempts with MCTS

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 2
Reference: Phase_6_Build_Order_Breakdown.md, Step 2
"""

from .policy_network import PolicyNetwork, TacticCandidate
from .critic_network import CriticNetwork
from .search_tree_manager import SearchTreeManager
from .types import ProofState, SearchResult, SearchStatus
# NOTE: MockProver has been removed from production exports.
# For testing, use: from tests.mocks import MockProver
from .prover_engine import ProverEngine, SymPyProver

__all__ = [
    'PolicyNetwork',
    'TacticCandidate',
    'CriticNetwork',
    'SearchTreeManager',
    'ProofState',
    'SearchResult',
    'SearchStatus',
    'ProverEngine',
    'SymPyProver',
    # MockProver removed - use tests.mocks.MockProver for testing
]
