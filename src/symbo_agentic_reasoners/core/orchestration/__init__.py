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
Orchestration Module
====================

Decomposed orchestrator components for maintainability (Phase 4).

The Main Orchestrator has been refactored from a monolithic 1,503-line file
into 6 focused modules, each with a single clear responsibility:

1. **data_structures.py** (90 LOC)
   - Task, NoAgentAvailableError
   - Domain mappings (DOMAIN_TO_POOL_KEY, get_pool_domain_key)

2. **decomposition.py** (160 LOC)
   - HTN (Hierarchical Task Network) decomposition
   - Agent lifecycle management (wake, activate, deactivate)

3. **agent_invocation.py** (368 LOC)
   - Direct supervisor/specialist invocation
   - Service discovery via Directory Facilitator
   - Specialist factory pattern

4. **native_fallback.py** (676 LOC)
   - Native computation fallbacks (NO SYMPY)
   - Domain-specific fallbacks: algebra, geometry, linalg, stats, discrete
   - Pure Python implementations

5. **blackboard_integration.py** (270 LOC)
   - Blackboard task posting and result awaiting
   - Agent activation/deactivation during task execution

6. **learning_memory.py** (178 LOC)
   - Look-before-leap cache checking (Phase 3 feature)
   - Solution recording for future retrieval

**Total**: 1,742 LOC across 6 modules (avg 290 LOC/module, all <700 LOC)
**Orchestrator**: Reduced from 1,503 LOC → 450 LOC (70% reduction)

Architecture
------------
The orchestrator now acts as a pure coordinator, delegating all domain logic
to specialized sub-engines. This follows the Supervisor-Specialist pattern
used throughout the codebase.

Backward Compatibility
---------------------
All public APIs remain unchanged. Existing code importing from orchestrator.py
continues to work without modification.
"""

# Core data structures
from .data_structures import (
    NoAgentAvailableError,
    Task,
    DOMAIN_TO_POOL_KEY,
    get_pool_domain_key
)

# Sub-engines
from .decomposition import DecompositionEngine
from .agent_invocation import AgentInvoker
from .native_fallback import NativeFallbackEngine
from .blackboard_integration import BlackboardIntegration
from .learning_memory import LearningMemory

__all__ = [
    # Data structures
    'NoAgentAvailableError',
    'Task',
    'DOMAIN_TO_POOL_KEY',
    'get_pool_domain_key',
    # Sub-engines
    'DecompositionEngine',
    'AgentInvoker',
    'NativeFallbackEngine',
    'BlackboardIntegration',
    'LearningMemory',
]

__version__ = '1.0.0'
__author__ = 'Damien Davison & Michael Maillet, Recursive AI Devs'
