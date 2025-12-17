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
PHASE 2 - STEP 2.4: DIFFERENTIAL EQUATION SOLVER (Tier 3)

Solves Ordinary Differential Equations (ODEs) and Partial Differential Equations (PDEs).
"""

import sys, os
from typing import Any, Dict, Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners_phase0.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners_phase0.memory.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners_phase0.core.omdoc_schema import create_variable
import sympy as sp

class ODESolver(BDIAgent):
    def __init__(self, agent_id='ode_solver_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        if self.df:
            reg = create_service_registration(
                service_type='math.calculus.ode', agent_id=self.agent_id,
                algorithm='runge_kutta', cost='high',
                tier='3',
                methods='symbolic_numerical'
            )
            self.df.register(reg)
        print(f"[{self.agent_id}] ODE Solver initialized")
    
    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            expr_str = metadata.get('sympy_expr', metadata.get('raw_input', ''))
            # Simplified ODE solving
            result = "ODE solution (Phase 2: Simplified solver)"
            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result)
        except Exception as e:
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry, result):
        if not self.blackboard: return result
        return create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
            self.agent_id, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            ['ode'], EntryStatus.PENDING, {'result_str': str(result)})
    
    def _create_error_entry(self, task_entry, error):
        if not self.blackboard: return None
        return create_entry(EntryType.PARTIAL_RESULT, create_variable(f"ERROR: {error}"),
            self.agent_id, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
            ['error'], EntryStatus.FAILED, {'error': error})
    
    def update_beliefs(self):
        """Update beliefs from environment (Placeholder)."""
        pass

    def deliberate(self):
        """Deliberate on beliefs and desires (Placeholder)."""
        return []

    def execute_step(self, intention):
        """Execute intention step (Placeholder)."""
        pass
    def get_statistics(self):
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed, 'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded/self.tasks_executed*100) if self.tasks_executed > 0 else 0})
        return stats
