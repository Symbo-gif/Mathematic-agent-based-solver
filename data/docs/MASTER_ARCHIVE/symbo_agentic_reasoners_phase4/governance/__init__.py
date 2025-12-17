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
CONFLICT RESOLUTION TEAM - "The Supreme Court"
===============================================

Phase 4 Governance: Evidence-Based Adjudication System

PURPOSE:
-------
Replaces random selection with structured, evidence-based adjudication
when agents produce conflicting results. Implements the FMAD (Feedback-based
Multi-Agent Debate) protocol.

WHY THIS MATTERS:
----------------
In a high-density ecosystem of 40-50 specialized agents, disagreements are
structurally inevitable. Without this team, the system either randomly selects
an answer (compromising accuracy), silently ignores conflicts (compromising
reliability), or crashes entirely (compromising availability).

AGENTS:
------
1. Debate Moderator - FMAD Protocol Implementation
2. Evidence Weigher - Hierarchy of Mathematical Truth
3. Consensus Builder - Expertise-weighted voting

REFERENCE:
---------
Phase_4_Build_Order_Breakdown.md: Step 1 (The Conflict Resolution Team)
"""

from .conflict_resolution import (
    ConflictResolutionTeam,
    DebateModerator,
    EvidenceWeigher,
    ConsensusBuilder,
    EvidenceType,
    ConflictCase
)

__all__ = [
    'ConflictResolutionTeam',
    'DebateModerator',
    'EvidenceWeigher',
    'ConsensusBuilder',
    'EvidenceType',
    'ConflictCase'
]
