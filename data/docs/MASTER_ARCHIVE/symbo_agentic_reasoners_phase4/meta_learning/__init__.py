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
META-LEARNING TEAM - "The Optimizer"
=====================================

Phase 4 Governance: AutoMaAS Pattern Implementation

PURPOSE:
-------
Implements the AutoMaAS (Automated Multi-Agent System) pattern - capturing
process metadata from every solution, analyzing efficiency patterns, and
dynamically updating the Orchestrator's routing tables.

WHY THIS MATTERS:
----------------
Without the Meta-Learning Team, the system solves the 1000th cubic equation
with the same trial-and-error randomness as the first. This team creates a
continuous feedback loop from performance to planning.

AGENTS:
------
1. Performance Monitor - Black box recorder (logs solution traces)
2. Agent Selector Optimizer - AutoMaAS logic (computes routing heuristics)
3. Adaptive Dispatcher - Dynamic scaling controller

EXPECTED IMPACT:
---------------
- Optimizes cost-per-token by 10-15%
- Matches resource allocation to problem complexity
- Learns which agents succeed for which problem types

REFERENCE:
---------
Phase_4_Build_Order_Breakdown.md: Step 3 (The Meta-Learning Team)
"""

from .meta_learning_team import (
    MetaLearningTeam,
    PerformanceMonitor,
    AgentSelectorOptimizer,
    AdaptiveDispatcher,
    SolutionTrace
)

__all__ = [
    'MetaLearningTeam',
    'PerformanceMonitor',
    'AgentSelectorOptimizer',
    'AdaptiveDispatcher',
    'SolutionTrace'
]
