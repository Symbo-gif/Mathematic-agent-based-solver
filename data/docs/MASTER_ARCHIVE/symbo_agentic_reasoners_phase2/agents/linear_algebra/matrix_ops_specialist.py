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
PHASE 2 - MATRIX OPERATIONS SPECIALIST (Tier 3)
===============================================

Handles fundamental matrix arithmetic and property calculations.
Operations: add, multiply, transpose, determinant, trace.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners_phase0.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners_phase0.memory.blackboard import Blackboard
from typing import Dict, Any, List, Optional
import numpy as np

class MatrixOperationsSpecialist(BDIAgent):
    def __init__(self, agent_id='matrix_ops_001', df: Optional[DirectoryFacilitator]=None, blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.linalg.ops',
                agent_id=agent_id,
                algorithm='numpy',
                cost='low',
                tier='3',
                operations='add_multiply_transpose_determinant_trace'))

        print(f"[{agent_id}] Matrix Operations Specialist initialized")
        print(f"  Library: NumPy")
        print(f"  Operations: Add, multiply, transpose, determinant, trace")

    def update_beliefs(self):
        """Update beliefs from environment (Placeholder)."""
        pass

    def deliberate(self) -> List[Intention]:
        """Deliberate on beliefs and desires (Placeholder)."""
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step (Placeholder)."""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed, 'tasks_succeeded': self.tasks_succeeded, 'tasks_failed': self.tasks_failed})
        return stats
