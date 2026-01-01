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
SYMBO_AGENTIC_REASONERS Core Components
"""
from .omdoc_schema import OMObject, OMDocStatement, OMDocTheory, MathOperator, create_variable, create_number, create_operation
from .bdi_agent import BDIAgent, Belief, Desire, Intention
from .blackboard import Blackboard, BlackboardEntry, EntryStatus, EntryType, create_entry
from .resource_coordinator import (
    ResourceCoordinator, ResourceLimits, AgentState, HardwareMetrics,
    get_coordinator, shutdown_coordinator
)
from .solver_engine import (
    SolverEngine, SolveResult, SolveStatus,
    get_solver_engine, solve
)

__all__ = [
    # OMDoc
    "OMObject", "OMDocStatement", "OMDocTheory", "MathOperator",
    "create_variable", "create_number", "create_operation",
    # BDI
    "BDIAgent", "Belief", "Desire", "Intention",
    # Blackboard
    "Blackboard", "BlackboardEntry", "EntryStatus", "EntryType", "create_entry",
    # Resource Coordinator
    "ResourceCoordinator", "ResourceLimits", "AgentState", "HardwareMetrics",
    "get_coordinator", "shutdown_coordinator",
    # Solver Engine
    "SolverEngine", "SolveResult", "SolveStatus",
    "get_solver_engine", "solve"
]
