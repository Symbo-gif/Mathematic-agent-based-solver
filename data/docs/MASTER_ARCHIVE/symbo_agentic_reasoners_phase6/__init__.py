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
Phase 6: The Mathematical Discovery Engine
============================================

Autonomous Mathematical Discovery Engine - 65-Agent Architecture
Phase 6 deploys 13 new agents organized into 5 specialized teams.

Teams:
1. Conjecture Generation Team (3 agents) - "The Theorist"
2. Deep Search Team (3 agents) - "The Explorer"
3. Algorithm Discovery Unit (3 agents) - "FunSearch Pattern"
4. Undecidability Navigator (2 agents) - "Boundary Watcher"
5. Formal Knowledge Integration (2 agents) - "The Archivist"

Core Objectives:
- Proactive Knowledge Synthesis: Evolve from reactive problem solving to autonomous conjecture generation
- Infinite Search Navigation: Deploy RL-guided search for open problems with unknown solution paths
- Algorithm Discovery: Find algorithms (functions) rather than just answers using FunSearch paradigm
- Undecidability Management: Protect system from Gödel/Turing limits with graceful mode-switching
- Knowledge Integration: Close evolutionary loop by auto-formalizing discoveries into axiom set

Reference Documentation:
- Phase 6 represents the transition from a Problem Solving Engine.docx
- Phase 6 must engineer the capacity for novel mathematical discovery.docx
- phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx
- Phase_6_Build_Order_Breakdown.md

Dependencies:
- Phase 5: ThoughtTraceHarvester, ComplexityGatekeeper, DistillationPipeline, EvolutionaryFlywheel
- Phase 1: Verification Core (Ax-Prover/Logic Checker)
- Phase 3: Knowledge Management Team (RAG infrastructure)
- Phase 0: OMDoc/OpenMath semantic substrate, FIPA-ACL messaging

Author: Phase 6 Discovery Engine Module
Hardware Target: AMD Ryzen 7 8700F, RTX 4060 (8GB VRAM), 32GB RAM
"""

__version__ = "1.0.0"
__phase__ = 6
__agent_count__ = 13
__total_system_agents__ = 65

from .phase6_system import Phase6System

__all__ = [
    'Phase6System',
    '__version__',
    '__phase__',
    '__agent_count__',
    '__total_system_agents__'
]
