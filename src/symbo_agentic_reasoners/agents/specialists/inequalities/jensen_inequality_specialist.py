# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
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
JENSEN INEQUALITY SPECIALIST (Tier 3)
=====================================

Verifies Jensen inequality for convex/concave functions.

CAPABILITIES:
- Discrete Jensen: f(∑λᵢxᵢ) ≤ ∑λᵢf(xᵢ) for convex f
- Convexity verification
- Weighted average handling

REFERENCE: Jensen, J. L. W. V. (1906)
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Callable

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
from symbo_agentic_reasoners.core.inequalities import jensen_discrete, is_convex_function

logger = logging.getLogger(__name__)


class JensenInequalitySpecialist(BDIAgent):
    """Jensen Inequality Specialist - Convex Function Inequalities"""

    def __init__(self, agent_id: str = 'jensen_inequality_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.inequalities.jensen',
                agent_id=agent_id,
                algorithm='native_jensen',
                cost='low',
                instance=self,
                tier='3'
            ))
        logger.info(f"[{agent_id}] Jensen Specialist initialized")

    def update_beliefs(self):
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['jensen'], status=EntryStatus.PENDING)
            for task in tasks:
                if not self.has_belief(f'pending_task_{task.entry_id}'):
                    self.add_belief(f'pending_task_{task.entry_id}', task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if predicate.startswith('pending_task_'):
                task_id = belief.content.entry_id
                if not any(i.metadata.get('task_id') == task_id for i in self.intentions):
                    new_intentions.append(Intention(
                        plan_id=f'jensen_{task_id}',
                        steps=['claim', 'verify', 'post'],
                        target_desire='verify_jensen',
                        metadata={'task_id': task_id, 'task_entry': belief.content}
                    ))
        return new_intentions

    def execute_step(self, intention: Intention):
        action = intention.get_current_action()
        try:
            if action == 'claim':
                if self.blackboard:
                    self.blackboard.update_entry_status(intention.metadata['task_id'], EntryStatus.IN_PROGRESS)
                intention.advance()
            elif action == 'verify':
                task = intention.metadata['task_entry']
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                x_vals = np.array(metadata.get('x_vals', []), dtype=float)
                weights = np.array(metadata.get('weights', []), dtype=float)

                # Simple test function if not provided
                f = metadata.get('function', lambda x: x**2)  # Default: convex quadratic
                convex = metadata.get('convex', True)

                result = jensen_discrete(x_vals, weights, f, convex=convex)
                intention.metadata['result'] = result
                intention.advance()
            elif action == 'post':
                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(intention.metadata['result'])),
                        author_agent=self.agent_id,
                        tags=['jensen', 'result'],
                        status=EntryStatus.COMPLETED,
                        metadata=intention.metadata['result']
                    )
                    self.blackboard.post(result_entry)
                self.tasks_succeeded += 1
                self.tasks_executed += 1
                intention.advance()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error: {e}")
            self.tasks_failed += 1
            self.tasks_executed += 1
            while not intention.is_complete():
                intention.advance()

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """Synchronous API."""
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        try:
            x_vals = np.array(metadata.get('x_vals', []), dtype=float)
            weights = np.array(metadata.get('weights', []), dtype=float)
            f = metadata.get('function', lambda x: x**2)
            result = jensen_discrete(x_vals, weights, f, convex=metadata.get('convex', True))
            self.tasks_executed += 1
            self.tasks_succeeded += 1
            return result
        except Exception as e:
            self.tasks_executed += 1
            self.tasks_failed += 1
            return {'error': str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100) if self.tasks_executed > 0 else 0.0
        }
