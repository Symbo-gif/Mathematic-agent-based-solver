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
Phase 5 Operational Hardening Team
===================================

Step 4 of Phase 5 Build Order:
- User Simulator (Stress Tester)
- Identity Manager (IAM Agent)

REFERENCE:
---------
Phase_5_Build_Order_Breakdown.md: Section 5
"""

from symbo_agentic_reasoners_phase5.hardening.user_simulator import (
    UserSimulator,
    SimulationResult
)
from symbo_agentic_reasoners_phase5.hardening.identity_manager import (
    IdentityManager,
    AgentIdentity,
    AccessLevel
)

__all__ = [
    'UserSimulator',
    'SimulationResult',
    'IdentityManager',
    'AgentIdentity',
    'AccessLevel'
]
