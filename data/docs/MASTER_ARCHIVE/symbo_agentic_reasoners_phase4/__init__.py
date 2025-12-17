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
PHASE 4: DYNAMIC GOVERNANCE & RESILIENCE
==========================================

The Self-Correction Engine

TRANSFORMATION:
--------------
Phase 3: "Resilient Professional" - Robust, context-aware, strategic
Phase 4: "Self-Correcting System" - Dynamic, adaptive, evolutionary

PURPOSE:
-------
Phase 4 transforms the multi-agent collective from a Static Hierarchy into a
Dynamic Organism capable of self-correction, conflict resolution, and evolutionary
optimization.

THREE CRITICAL GAPS ADDRESSED:
-----------------------------
Gap 4: The Conflict Gap - Resolved by Conflict Resolution Team (3 agents)
Gap 5: The Reliability Gap - Resolved by Failure Analysis Team (3 agents)
Gap 6: The Evolution Gap - Resolved by Meta-Learning Team (3 agents)

PHASE 4 AGENT COUNT: 9 agents across 3 teams

TEAMS:
-----
1. Conflict Resolution Team ("The Supreme Court")
   - Debate Moderator: FMAD Protocol Implementation
   - Evidence Weigher: Hierarchy of Mathematical Truth
   - Consensus Builder: Expertise-weighted voting

2. Failure Analysis Team ("The Trauma Surgeons")
   - Error Classifier: Diagnostic interceptor
   - Root Cause Analyzer: Failure attribution
   - Alternative Path Generator: Plan B engine

3. Meta-Learning Team ("The Optimizer")
   - Performance Monitor: Black box recorder
   - Agent Selector Optimizer: AutoMaAS implementation
   - Adaptive Dispatcher: Dynamic scaling

DELIVERABLE:
-----------
A self-correcting system with:
- Resilience: Autonomous failure recovery
- Intelligence: Evidence-based conflict resolution
- Evolution: Continuous optimization from experience

REFERENCE:
---------
- Phase_4_Build_Order_Breakdown.md
- Phase 4 transforms this collection of agents into a Self-Correction Engine.md
"""

from .governance.conflict_resolution import (
    ConflictResolutionTeam,
    DebateModerator,
    EvidenceWeigher,
    ConsensusBuilder,
    EvidenceType,
    ConflictCase
)

from .failure_analysis.failure_analysis_team import (
    FailureAnalysisTeam,
    ErrorClassifier,
    RootCauseAnalyzer,
    AlternativePathGenerator,
    ErrorType,
    RemedyAction,
    FailureReport
)

from .meta_learning.meta_learning_team import (
    MetaLearningTeam,
    PerformanceMonitor,
    AgentSelectorOptimizer,
    AdaptiveDispatcher,
    SolutionTrace
)

from .integration.protocol_updates import (
    OrchestratorPhase4Update,
    ConflictResolutionError
)

from .phase4_system import Phase4System

__all__ = [
    # Main system
    'Phase4System',

    # Conflict Resolution Team
    'ConflictResolutionTeam',
    'DebateModerator',
    'EvidenceWeigher',
    'ConsensusBuilder',
    'EvidenceType',
    'ConflictCase',

    # Failure Analysis Team
    'FailureAnalysisTeam',
    'ErrorClassifier',
    'RootCauseAnalyzer',
    'AlternativePathGenerator',
    'ErrorType',
    'RemedyAction',
    'FailureReport',

    # Meta-Learning Team
    'MetaLearningTeam',
    'PerformanceMonitor',
    'AgentSelectorOptimizer',
    'AdaptiveDispatcher',
    'SolutionTrace',

    # Integration
    'OrchestratorPhase4Update',
    'ConflictResolutionError',
]
