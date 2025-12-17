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
PHASE 4 INTEGRATION - Protocol Updates
======================================

System Integration: Wiring Phase 4 Teams into Existing Hierarchy

PURPOSE:
-------
Phase 4 teams must be wired into the existing Phase 1/2/3 infrastructure
through two critical protocol updates to the Main Orchestrator.

PROTOCOLS:
---------
1. Appellate Protocol (4.1)
   - Mandatory conflict check before result acceptance
   - If CONFLICT_FLAG == true, delegate to Debate Moderator

2. Post-Mortem Protocol (4.2)
   - Trigger optimization after every session
   - Meta-Learning Team analyzes traces and updates routing

OUTCOME:
-------
The system is slightly smarter at the start of Day N+1 than it was at Day N,
implementing continuous evolutionary improvement.

REFERENCE:
---------
Phase_4_Build_Order_Breakdown.md: Step 4 (System Integration)
"""

from .protocol_updates import (
    OrchestratorPhase4Update,
    ConflictResolutionError
)

__all__ = [
    'OrchestratorPhase4Update',
    'ConflictResolutionError'
]
