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

"""Deep Search module"""
from .types import ProofState, SearchResult
from .prover_engine import ProverEngine, SymPyProver
from .policy_network import PolicyNetwork
from .critic_network import CriticNetwork
from .search_tree_manager import SearchTreeManager
from .exhaustive_enumerator import ExhaustiveEnumerator
from .parallel_search_manager import ParallelSearchManager
from .spectral_partitioner import (
    SpectralPartitioner,
    DiffusionMap,
    StateGraph,
    WorkerAssignment,
    Partition,
    PartitionStrategy,
    partition_for_parallel_search,
    AdaptivePartitionSelector,
    adaptive_partition
)

__all__ = [
    "ProofState", "SearchResult", "ProverEngine", "SymPyProver",
    "PolicyNetwork", "CriticNetwork", "SearchTreeManager",
    "ExhaustiveEnumerator", "ParallelSearchManager",
    "SpectralPartitioner", "DiffusionMap", "StateGraph",
    "WorkerAssignment", "Partition", "PartitionStrategy",
    "partition_for_parallel_search", "AdaptivePartitionSelector", "adaptive_partition"
]
