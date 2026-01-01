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
Orchestration Data Structures
==============================

Data structures and utilities for the orchestration subsystem.
"""

from dataclasses import dataclass
from typing import Any, Optional
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain
from symbo_agentic_reasoners.core.blackboard import EntryStatus


class NoAgentAvailableError(Exception):
    """Raised when no agent is available for a task."""
    pass


# Mapping from MathDomain enum values to agent pool domain keys
# MathDomain uses PascalCase values, agent pool uses snake_case
DOMAIN_TO_POOL_KEY = {
    'Calculus': 'calculus',
    'Algebra': 'algebra',
    'LinearAlgebra': 'linear_algebra',
    'Geometry': 'geometry',
    'Logic': 'logic',
    'NumberTheory': 'number_theory',
    'Statistics': 'statistics',
    'DiscreteMath': 'discrete_math',
    # Physics domains
    'PhysicsMechanics': 'physics_mechanics',
    'PhysicsEM': 'physics_em',
    'PhysicsThermo': 'physics_thermo',
    'PhysicsQuantum': 'physics_quantum',
    'Unknown': 'unknown',
}


def get_pool_domain_key(math_domain: MathDomain) -> str:
    """
    Convert MathDomain enum to agent pool domain key.

    Args:
        math_domain: MathDomain enum value

    Returns:
        Snake_case domain key for agent pool/registry
    """
    return DOMAIN_TO_POOL_KEY.get(math_domain.value, math_domain.value.lower())


@dataclass
class Task:
    """
    Orchestrator task representation.

    Represents a task that needs to be executed by a specialist agent.
    """
    task_id: str
    structured_problem: StructuredProblem
    status: EntryStatus
    assigned_agent: Optional[str] = None
    blackboard_entry_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


__all__ = [
    'NoAgentAvailableError',
    'DOMAIN_TO_POOL_KEY',
    'get_pool_domain_key',
    'Task',
]
