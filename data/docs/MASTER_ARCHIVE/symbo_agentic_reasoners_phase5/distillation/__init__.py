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
Phase 5 Distillation & Harvest Team
====================================

Step 1 & 2 of Phase 5 Build Order:
- Thought Trace Harvester (Provenance Logger)
- Distillation Pipeline (Student Model Trainer)

REFERENCE:
---------
Phase_5_Build_Order_Breakdown.md: Sections 2 & 3
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

__all__ = [
    'ThoughtTraceHarvester',
    'ThoughtTrace',
    'VerificationStatus',
    'DistillationPipeline',
    'StudentModelTrainer'
]
