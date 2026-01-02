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
Deep Search Types
=================

Common data structures for the Deep Search Team.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SearchStatus(Enum):
    """Status of a search operation"""
    ACTIVE = 'active'
    COMPLETED = 'completed'
    TIMEOUT = 'timeout'
    RESOURCE_LIMIT = 'resource_limit'
    UNDECIDABLE = 'undecidable'


@dataclass
class ProofState:
    """
    Represents a state in the proof search tree.

    Attributes:
        state_id: Unique identifier
        goal: Current proof goal
        hypotheses: Available hypotheses
        depth: Depth in search tree
        parent_id: Parent state ID
        tactic_applied: Tactic that led to this state
        value_estimate: Critic's value estimate
        visit_count: Number of times visited (for UCB1)
        children: List of child state IDs
    """
    state_id: str
    goal: str
    hypotheses: List[str]
    depth: int
    parent_id: Optional[str] = None
    tactic_applied: Optional[str] = None
    value_estimate: float = 0.5
    visit_count: int = 0
    children: List[str] = field(default_factory=list)
    is_terminal: bool = False
    is_proven: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def is_leaf(self) -> bool:
        """Check if this is a leaf node"""
        return len(self.children) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'state_id': self.state_id,
            'goal': self.goal,
            'hypotheses': self.hypotheses,
            'depth': self.depth,
            'parent_id': self.parent_id,
            'tactic_applied': self.tactic_applied,
            'value_estimate': self.value_estimate,
            'visit_count': self.visit_count,
            'num_children': len(self.children),
            'is_terminal': self.is_terminal,
            'is_proven': self.is_proven
        }


@dataclass
class SearchResult:
    """
    Result of a proof search.

    Attributes:
        success: Whether proof was found
        proof_steps: List of tactics forming the proof
        states_explored: Number of states explored
        max_depth_reached: Maximum depth reached
        time_elapsed_ms: Time taken in milliseconds
        status: Search status
    """
    success: bool
    proof_steps: List[str]
    states_explored: int
    max_depth_reached: int
    time_elapsed_ms: float
    status: SearchStatus
    value_at_root: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'success': self.success,
            'proof_steps': self.proof_steps,
            'proof_length': len(self.proof_steps),
            'states_explored': self.states_explored,
            'max_depth_reached': self.max_depth_reached,
            'time_elapsed_ms': self.time_elapsed_ms,
            'status': self.status.value,
            'value_at_root': self.value_at_root
        }
