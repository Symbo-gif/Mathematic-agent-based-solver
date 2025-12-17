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
PHASE 3 ORCHESTRATOR
====================

Updated Tier 1 Orchestrator with Meta-Cognitive Integration.

Implements the evolved control loop:
    Analyze -> Hypothesize -> Validate -> Solve

PROTOCOLS:
---------
1. Pre-Flight Check - Validation before delegation
2. Look-Before-You-Leap - Knowledge retrieval
3. Scouting - Hypothesis generation for complex problems

REFERENCE:
---------
Phase_3_Build_Order_Breakdown.md: Step 4
"""

from .phase3_orchestrator import (
    Phase3Orchestrator,
    ComplexityLevel,
    OrchestratorDecision
)

__all__ = [
    'Phase3Orchestrator',
    'ComplexityLevel',
    'OrchestratorDecision'
]
