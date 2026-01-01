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
Discrete Math Specialists Package
==================================

Provides discrete mathematics specialists:
- CombinatoricsAgent: Permutations, combinations, partitions
- GraphTheoryAgent: Graph algorithms (BFS, DFS, shortest path, etc.)
- SetTheoryAgent: Set operations, relations, functions
- RecurrenceRelationAgent: Solving recurrence relations
- BooleanAlgebraAgent: Boolean minimization, Karnaugh maps
- FiniteAutomataAgent: DFA, NFA, regex to automata
"""

from .combinatorics_agent import CombinatoricsAgent
from .graph_theory_agent import GraphTheoryAgent
from .set_theory_agent import SetTheoryAgent
from .recurrence_agent import RecurrenceRelationAgent
from .boolean_algebra_agent import BooleanAlgebraAgent
from .finite_automata_agent import FiniteAutomataAgent

__all__ = [
    # Original agents
    "CombinatoricsAgent",
    "GraphTheoryAgent",
    # New agents
    "SetTheoryAgent",
    "RecurrenceRelationAgent",
    "BooleanAlgebraAgent",
    "FiniteAutomataAgent",
]
