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

"""SEPARATION THEOREM SPECIALIST - Hyperplane separation"""

import logging
import numpy as np
from typing import Any, Dict, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.convex_analysis import (
    separating_hyperplane, supporting_hyperplane, project_onto_convex_set
)

logger = logging.getLogger(__name__)


class SeparationTheoremSpecialist(BDIAgent):
    """Separation Theorem Specialist - Separating/Supporting Hyperplanes"""

    def __init__(self, agent_id='separation_theorem_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.separations_computed = 0

        if df:
            df.register(create_service_registration(
                service_type='math.convexity.separation',
                agent_id=agent_id, algorithm='hyperplane_separation',
                cost='medium', instance=self, tier='3'
            ))

    def update_beliefs(self):
        if self.blackboard:
            try:
                for task in self.blackboard.query_entries(tags=['separation'], status=EntryStatus.PENDING):
                    if not self.has_belief(f'p_{task.entry_id}'):
                        self.add_belief(f'p_{task.entry_id}', task, 1.0)
            except:
                pass

    def deliberate(self):
        return [Intention(f'sep_{b.content.entry_id}', ['separate'], 'separation', {'t': b.content})
                for p, b in self.beliefs.items() if p.startswith('p_')]

    def execute_step(self, intention):
        if intention.get_current_action() == 'separate':
            task = intention.metadata['t']
            meta = task.metadata if hasattr(task, 'metadata') else {}
            operation = meta.get('operation', 'separating')

            try:
                if operation == 'separating':
                    A = np.array(meta.get('points_A', []))
                    B = np.array(meta.get('points_B', []))
                    result = separating_hyperplane(A, B)
                elif operation == 'supporting':
                    points = np.array(meta['points'])
                    direction = np.array(meta['direction'])
                    result = supporting_hyperplane(points, direction)
                elif operation == 'projection':
                    x = np.array(meta['x'])
                    points = np.array(meta['points'])
                    result = {'projection': project_onto_convex_set(x, points).tolist()}
                else:
                    result = {'error': 'Unknown operation'}

                if 'error' not in result:
                    self.separations_computed += 1
                    self.tasks_succeeded += 1
            except Exception as e:
                result = {'error': str(e)}

            self.tasks_executed += 1
            if self.blackboard:
                self.blackboard.post(create_entry(EntryType.PARTIAL_RESULT, str(result),
                                                 self.agent_id, tags=['separation'],
                                                 status=EntryStatus.COMPLETED))
            intention.advance()

    def process(self, task_entry):
        meta = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = meta.get('operation', 'separating')
        try:
            if operation == 'separating':
                return separating_hyperplane(np.array(meta['points_A']), np.array(meta['points_B']))
            elif operation == 'supporting':
                return supporting_hyperplane(np.array(meta['points']), np.array(meta['direction']))
            return {'projection': project_onto_convex_set(np.array(meta['x']), np.array(meta['points'])).tolist()}
        except Exception as e:
            return {'error': str(e)}

    def get_statistics(self):
        return {'tasks_executed': self.tasks_executed, 'separations_computed': self.separations_computed}
