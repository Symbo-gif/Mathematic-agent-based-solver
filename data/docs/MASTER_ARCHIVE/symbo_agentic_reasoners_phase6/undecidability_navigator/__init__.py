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
Undecidability Navigator - "Boundary Watcher"
===============================================

Phase 6, Step 4: Protecting Against the Hard Limits of Mathematics

As the system explores unknown territory, it will inevitably encounter
undecidable problems (Gödel's Incompleteness, Halting Problem). The
Undecidability Navigator protects the system from infinite loops and
resource exhaustion.

Key capabilities:
- Classifies problems *before* committing search resources
- Switches from "Solver Mode" to "Heuristic Search Mode" when walls are hit
- Provides Human-in-the-Loop interface for guidance

Agents:
1. DecidabilityChecker - Meta-analyst classifying theories by decidability
2. InteractiveGuidanceLiaison - Human-in-the-Loop interface for stuck states

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 4
Reference: Phase_6_Build_Order_Breakdown.md, Step 4
"""

from .decidability_checker import DecidabilityChecker, DecidabilityClass, DecidabilityAssessment
from .interactive_guidance_liaison import InteractiveGuidanceLiaison, ProofStateSummary, GuidanceRequest

__all__ = [
    'DecidabilityChecker',
    'DecidabilityClass',
    'DecidabilityAssessment',
    'InteractiveGuidanceLiaison',
    'ProofStateSummary',
    'GuidanceRequest'
]
