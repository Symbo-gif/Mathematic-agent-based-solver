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
PHASE 3: META-COGNITIVE MIDDLEWARE
===================================

The "Cognitive Immune System" - Resilience, Context, and Foresight

This phase transforms the system from a "Fragile Genius" (Phase 2) into a
"Resilient Professional" by addressing three critical gaps:

GAP 1: Search Gap (Hypothesis Generation Team)
    - Tree-of-Thoughts reasoning
    - Strategy generation and evaluation
    - Backtracking on failure

GAP 2: Memory Gap (Knowledge Management Team)
    - Context extraction and filtering
    - Long-term memory indexing
    - Retrieval-Augmented Generation (RAG)

GAP 3: Assumption Gap (Precondition Validation Team)
    - Domain checking for solvability
    - Constraint validation
    - Edge case detection
    - Constraint propagation

CONTROL LOOP EVOLUTION:
    Phase 1-2: Plan -> Solve
    Phase 3:   Analyze -> Hypothesize -> Validate -> Solve

REFERENCE:
---------
- Phase_3_Build_Order_Breakdown.md
- Phase 3 installs the _cognitive immune system_ that creates resilience.md
- Phase 3 is designated as the Meta-Cognitive Middleware implementation.md
"""

from .validation.precondition_validation import (
    PreconditionValidationTeam,
    DomainCheckerAgent,
    AssumptionValidatorAgent,
    EdgeCaseDetectorAgent,
    ConstraintPropagatorAgent,
    ValidationStatus,
    ValidationResult,
    MathematicalDomain,
    MathematicalConstraint
)

from .knowledge.knowledge_management import (
    KnowledgeManagementTeam,
    ContextExtractorAgent,
    MemoryIndexerAgent,
    RetrievalSpecialistAgent,
    RetrievalConfidence,
    RetrievalResult,
    ContextPacket
)

from .hypothesis.hypothesis_generation import (
    HypothesisGenerationTeam,
    HypothesisGeneratorAgent,
    PathEvaluatorAgent,
    BacktrackingManagerAgent,
    StrategyType,
    SolutionPlan,
    PlanStatus
)

from .orchestrator.phase3_orchestrator import (
    Phase3Orchestrator,
    ComplexityLevel,
    OrchestratorDecision
)

from .phase3_system import Phase3System

__all__ = [
    # Validation Team
    'PreconditionValidationTeam',
    'DomainCheckerAgent',
    'AssumptionValidatorAgent',
    'EdgeCaseDetectorAgent',
    'ConstraintPropagatorAgent',
    'ValidationStatus',
    'ValidationResult',
    'MathematicalDomain',
    'MathematicalConstraint',

    # Knowledge Management Team
    'KnowledgeManagementTeam',
    'ContextExtractorAgent',
    'MemoryIndexerAgent',
    'RetrievalSpecialistAgent',
    'RetrievalConfidence',
    'RetrievalResult',
    'ContextPacket',

    # Hypothesis Generation Team
    'HypothesisGenerationTeam',
    'HypothesisGeneratorAgent',
    'PathEvaluatorAgent',
    'BacktrackingManagerAgent',
    'StrategyType',
    'SolutionPlan',
    'PlanStatus',

    # Orchestrator
    'Phase3Orchestrator',
    'ComplexityLevel',
    'OrchestratorDecision',

    # System
    'Phase3System'
]
