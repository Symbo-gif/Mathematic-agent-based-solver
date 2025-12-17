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
SYMBO_AGENTIC_REASONERS Phase 5: Production Optimization & Distillation
=====================================================

Phase 5 transforms the system from a "Self-Correcting System" (Phase 4)
into an "Adaptive Cognitive Engine" - the Apex System.

TRANSFORMATION:
--------------
Phase 4: "Self-Correcting System" - Dynamic, adaptive, evolutionary
Phase 5: "Adaptive Cognitive Engine" - Fast, deep, autonomous

TEAMS (6 New Agents):
--------------------
Distillation & Harvest Team (2 agents):
  - Provenance Logger: Captures thought traces
  - Student Model Trainer: Distills knowledge into fast model

Hybrid Deployment Team (2 agents):
  - Complexity Gatekeeper: Routes queries (Student vs Teacher)
  - Confidence Fallback: Escalates low-confidence results

Operational Hardening Team (2 agents):
  - User Simulator: Stress tests the system
  - Identity Manager: IAM for agents

CAPABILITIES:
------------
1. SPEED: Fast single model for ~90% of interactions (1/5th latency)
2. DEPTH: Instant unfold to 50-agent swarm for complex problems
3. TRAJECTORY: Autonomous updates based on MAS successes

REFERENCE:
---------
- Phase_5_Build_Order_Breakdown.md
- phase5_symbo_integration_architecture.py
"""

from symbo_agentic_reasoners_phase5.distillation.thought_trace_harvester import (
    ThoughtTraceHarvester,
    ThoughtTrace,
    VerificationStatus
)
from symbo_agentic_reasoners_phase5.distillation.distillation_pipeline import (
    DistillationPipeline,
    StudentModelTrainer
)
from symbo_agentic_reasoners_phase5.hybrid_deployment.complexity_gatekeeper import (
    ComplexityGatekeeper,
    QueryRoute
)
from symbo_agentic_reasoners_phase5.hybrid_deployment.confidence_fallback import (
    ConfidenceFallback,
    EscalationReason
)
from symbo_agentic_reasoners_phase5.hardening.user_simulator import (
    UserSimulator,
    SimulationResult
)
from symbo_agentic_reasoners_phase5.hardening.identity_manager import (
    IdentityManager,
    AgentIdentity,
    AccessLevel
)
from symbo_agentic_reasoners_phase5.evolution.evolutionary_flywheel import (
    EvolutionaryFlywheel,
    EvolutionCycle
)

__all__ = [
    # Distillation
    'ThoughtTraceHarvester',
    'ThoughtTrace',
    'VerificationStatus',
    'DistillationPipeline',
    'StudentModelTrainer',
    # Hybrid Deployment
    'ComplexityGatekeeper',
    'QueryRoute',
    'ConfidenceFallback',
    'EscalationReason',
    # Hardening
    'UserSimulator',
    'SimulationResult',
    'IdentityManager',
    'AgentIdentity',
    'AccessLevel',
    # Evolution
    'EvolutionaryFlywheel',
    'EvolutionCycle'
]
