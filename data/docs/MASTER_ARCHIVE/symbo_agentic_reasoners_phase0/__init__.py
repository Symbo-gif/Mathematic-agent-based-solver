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
SYMBO_AGENTIC_REASONERS Phase 0: Autonomous Mathematical Discovery Engine - Foundational Infrastructure
====================================================================================

This package implements Phase 0 of the SYMBO_AGENTIC_REASONERS system: the foundational bedrock
upon which all future cognitive agents will be built.

PHASE 0 COMPLETION STATUS: COMPUTATIONALLY ALIVE, MATHEMATICALLY INERT
----------------------------------------------------------------------

At the conclusion of Phase 0, the system is fully operational but has not yet
solved a single mathematical problem. This is the intended outcome - we have
built the city, established the laws, and hired the managers, but the streets
are still empty of mathematical work.

PHASE 0 COMPONENTS:
------------------

STEP 1: Semantic Substrate (OMDoc/OpenMath)
  - omdoc_schema: Three-layer mathematical encoding (Object, Statement, Theory)
  - Eliminates natural language ambiguity in mathematical communication

STEP 2: Constitutional Law (FIPA-ACL Protocols)
  - fipa_acl: Speech act-based agent communication with explicit intent
  - Mandatory fields, conversation threading, OMDoc content enforcement

STEP 3: Active Memory Architecture
  - blackboard: Centralized workspace with publish-subscribe mechanism
  - vector_database: Long-term institutional memory for RAG capabilities

STEP 4: Bureaucratic Infrastructure Team (Silent Agents)
  - ams: Agent Management System - lifecycle and VRAM enforcement
  - directory_facilitator: Service registry for dynamic agent discovery
  - acc: Agent Communication Channel - message routing and queuing

STEP 5: Cognitive Blueprint
  - bdi_agent: Belief-Desire-Intention framework for deliberative agents

REFERENCE DOCUMENTATION:
-----------------------
- Phase_0_Build_Order_Breakdown.md
- Phase 0 Coding Strategy_ Architecting the Foundational Infrastructure for a Multi-Agent Collective.md
- Phase 0_ Infrastructural Agents and Hardware Calibration .md

VERSION: Phase 0.1.0
HARDWARE TARGET: AMD Ryzen 7 8700F, RTX 4060 (8GB VRAM), 32GB RAM
"""

__version__ = "0.1.0"
__phase__ = "Phase 0: Foundational Infrastructure"

# Core components
from .core.omdoc_schema import (
    OMObject,
    OMDocStatement,
    OMDocTheory,
    MathOperator,
    create_variable,
    create_number,
    create_operation
)

from .core.fipa_acl import (
    FIPAMessage,
    Performative,
    FIPAProtocol,
    create_request,
    create_inform,
    create_query,
    create_failure
)

from .core.bdi_agent import (
    BDIAgent,
    Belief,
    Desire,
    Intention
)

# Infrastructure agents
from .infrastructure.ams import (
    AgentManagementSystem,
    AgentRecord,
    AgentStatus,
    AgentType
)

from .infrastructure.directory_facilitator import (
    DirectoryFacilitator,
    ServiceRegistration,
    create_service_registration
)

from .infrastructure.acc import (
    AgentCommunicationChannel,
    MessageEnvelope
)

# Memory systems
from .memory.blackboard import (
    Blackboard,
    BlackboardEntry,
    EntryStatus,
    EntryType,
    create_entry
)

from .memory.vector_database import (
    VectorDatabase,
    VectorEntry,
    create_vector_entry
)

__all__ = [
    # Core - Semantic Substrate
    'OMObject',
    'OMDocStatement',
    'OMDocTheory',
    'MathOperator',
    'create_variable',
    'create_number',
    'create_operation',

    # Core - FIPA-ACL
    'FIPAMessage',
    'Performative',
    'FIPAProtocol',
    'create_request',
    'create_inform',
    'create_query',
    'create_failure',

    # Core - BDI
    'BDIAgent',
    'Belief',
    'Desire',
    'Intention',

    # Infrastructure
    'AgentManagementSystem',
    'AgentRecord',
    'AgentStatus',
    'AgentType',
    'DirectoryFacilitator',
    'ServiceRegistration',
    'create_service_registration',
    'AgentCommunicationChannel',
    'MessageEnvelope',

    # Memory
    'Blackboard',
    'BlackboardEntry',
    'EntryStatus',
    'EntryType',
    'create_entry',
    'VectorDatabase',
    'VectorEntry',
    'create_vector_entry',
]
