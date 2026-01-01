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

"""SUBGRADIENT SPECIALIST - Non-smooth optimization"""

import logging
import numpy as np
from typing import Any, Dict, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.convex_analysis import compute_subgradient, subdifferential_l1

logger = logging.getLogger(__name__)


class SubgradientSpecialist(BDIAgent):
    """Subgradient Specialist - Subdifferential Computation"""

    def __init__(self, agent_id='subgradient_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.subgrads_computed = 0

        if df:
            df.register(create_service_registration(
                service_type='math.convexity.subgradients',
                agent_id=agent_id, algorithm='finite_diff_subdifferential',
                cost='low', instance=self, tier='3'
            ))

    def update_beliefs(self):
        if self.blackboard:
            try:
                for task in self.blackboard.query_entries(tags=['subgradient'], status=EntryStatus.PENDING):
                    if not self.has_belief(f'p_{task.entry_id}'):
                        self.add_belief(f'p_{task.entry_id}', task, 1.0)
            except:
                pass

    def deliberate(self):
        return [Intention(f'sg_{b.content.entry_id}', ['compute'], 'subgrad', {'t': b.content})
                for p, b in self.beliefs.items() if p.startswith('p_')]

    def execute_step(self, intention):
        if intention.get_current_action() == 'compute':
            task = intention.metadata['t']
            meta = task.metadata if hasattr(task, 'metadata') else {}
            try:
                if meta.get('function') == 'l1':
                    result = {'subgradients': [sg.tolist() for sg in subdifferential_l1(np.array(meta['x']))]}
                else:
                    f = meta.get('f', lambda x: np.linalg.norm(x, 1))
                    x = np.array(meta.get('x', []))
                    subgrad = compute_subgradient(f, x, method=meta.get('method', 'finite_diff'))
                    result = {'subgradient': subgrad.tolist()}
                self.subgrads_computed += 1
                self.tasks_succeeded += 1
            except Exception as e:
                result = {'error': str(e)}

            self.tasks_executed += 1
            if self.blackboard:
                self.blackboard.post(create_entry(EntryType.PARTIAL_RESULT, str(result),
                                                 self.agent_id, tags=['subgradient'],
                                                 status=EntryStatus.COMPLETED))
            intention.advance()

    def process(self, task_entry):
        meta = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        try:
            if meta.get('function') == 'l1':
                return {'subgradients': [sg.tolist() for sg in subdifferential_l1(np.array(meta['x']))]}
            f = meta.get('f', lambda x: np.linalg.norm(x, 1))
            x = np.array(meta.get('x', []))
            return {'subgradient': compute_subgradient(f, x).tolist()}
        except Exception as e:
            return {'error': str(e)}

    def get_statistics(self):
        return {'tasks_executed': self.tasks_executed, 'subgrads_computed': self.subgrads_computed}
