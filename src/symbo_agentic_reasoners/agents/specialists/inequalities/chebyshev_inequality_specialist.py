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

"""CHEBYSHEV INEQUALITY SPECIALIST - Probability bounds and sum inequalities"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
from symbo_agentic_reasoners.core.inequalities import chebyshev_probability, chebyshev_sum

logger = logging.getLogger(__name__)


class ChebyshevInequalitySpecialist(BDIAgent):
    """Chebyshev Inequality Specialist - Probability and Sum Forms"""

    def __init__(self, agent_id='chebyshev_inequality_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.tasks_succeeded = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.inequalities.chebyshev',
                agent_id=agent_id,
                algorithm='native_chebyshev',
                cost='low',
                instance=self,
                tier='3'
            ))

    def update_beliefs(self):
        if self.blackboard:
            try:
                tasks = self.blackboard.query_entries(tags=['chebyshev'], status=EntryStatus.PENDING)
                for task in tasks:
                    if not self.has_belief(f'pending_{task.entry_id}'):
                        self.add_belief(f'pending_{task.entry_id}', task, confidence=1.0)
            except:
                pass

    def deliberate(self) -> List[Intention]:
        intentions = []
        for pred, belief in list(self.beliefs.items()):
            if pred.startswith('pending_'):
                intentions.append(Intention(
                    plan_id=f'cheb_{belief.content.entry_id}',
                    steps=['verify', 'post'],
                    target_desire='chebyshev',
                    metadata={'task': belief.content}
                ))
        return intentions

    def execute_step(self, intention: Intention):
        action = intention.get_current_action()
        if action == 'verify':
            task = intention.metadata['task']
            meta = task.metadata if hasattr(task, 'metadata') else {}
            try:
                if 'data' in meta:
                    result = chebyshev_probability(meta['data'], meta.get('k', 2.0))
                else:
                    result = chebyshev_sum(meta.get('a', []), meta.get('b', []))
                intention.metadata['result'] = result
                self.tasks_succeeded += 1
            except Exception as e:
                intention.metadata['result'] = {'error': str(e)}
            self.tasks_executed += 1
            intention.advance()
        elif action == 'post':
            if self.blackboard:
                self.blackboard.post(create_entry(
                    entry_type=EntryType.PARTIAL_RESULT,
                    content=create_variable(str(intention.metadata['result'])),
                    author_agent=self.agent_id,
                    tags=['chebyshev'],
                    status=EntryStatus.COMPLETED
                ))
            intention.advance()

    def process(self, task_entry: Any) -> Dict[str, Any]:
        meta = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        try:
            if 'data' in meta:
                return chebyshev_probability(meta['data'], meta.get('k', 2.0))
            return chebyshev_sum(meta.get('a', []), meta.get('b', []))
        except Exception as e:
            return {'error': str(e)}

    def get_statistics(self):
        return {'tasks_executed': self.tasks_executed, 'tasks_succeeded': self.tasks_succeeded}
