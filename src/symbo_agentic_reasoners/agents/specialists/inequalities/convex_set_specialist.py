# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""CONVEX SET SPECIALIST - Convex hull, extreme points, set operations"""

import logging
import numpy as np
from typing import Any, Dict, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.convex_analysis import convex_hull_2d, extreme_points_2d, is_convex_set

logger = logging.getLogger(__name__)


class ConvexSetSpecialist(BDIAgent):
    """Convex Set Specialist - Convex Hulls and Extreme Points"""

    def __init__(self, agent_id='convex_set_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.hulls_computed = 0

        if df:
            df.register(create_service_registration(
                service_type='math.convexity.sets',
                agent_id=agent_id, algorithm='graham_scan',
                cost='low', instance=self, tier='3',
                operations='convex_hull_extreme_points_verification'
            ))

    def update_beliefs(self):
        if self.blackboard:
            try:
                for task in self.blackboard.query_entries(tags=['convex_set'], status=EntryStatus.PENDING):
                    if not self.has_belief(f'p_{task.entry_id}'):
                        self.add_belief(f'p_{task.entry_id}', task, 1.0)
            except:
                pass

    def deliberate(self):
        return [Intention(f'cs_{b.content.entry_id}', ['compute'], 'convex_set', {'t': b.content})
                for p, b in self.beliefs.items() if p.startswith('p_')]

    def execute_step(self, intention):
        if intention.get_current_action() == 'compute':
            task = intention.metadata['t']
            meta = task.metadata if hasattr(task, 'metadata') else {}
            operation = meta.get('operation', 'convex_hull')

            try:
                points = np.array(meta.get('points', []), dtype=float)
                if operation == 'convex_hull':
                    result = {'hull': convex_hull_2d(points).tolist()}
                    self.hulls_computed += 1
                elif operation == 'extreme_points':
                    result = {'extreme_indices': extreme_points_2d(points)}
                elif operation == 'is_convex':
                    result = {'is_convex': is_convex_set(points)}
                else:
                    result = {'hull': convex_hull_2d(points).tolist()}
                self.tasks_succeeded += 1
            except Exception as e:
                result = {'error': str(e)}

            self.tasks_executed += 1
            if self.blackboard:
                self.blackboard.post(create_entry(EntryType.PARTIAL_RESULT, str(result),
                                                 self.agent_id, tags=['convex_set'],
                                                 status=EntryStatus.COMPLETED))
            intention.advance()

    def process(self, task_entry):
        meta = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = meta.get('operation', 'convex_hull')
        try:
            points = np.array(meta.get('points', []), dtype=float)
            if operation == 'convex_hull':
                return {'hull': convex_hull_2d(points).tolist()}
            elif operation == 'extreme_points':
                return {'extreme_indices': extreme_points_2d(points)}
            return {'is_convex': is_convex_set(points)}
        except Exception as e:
            return {'error': str(e)}

    def get_statistics(self):
        return {'tasks_executed': self.tasks_executed, 'hulls_computed': self.hulls_computed}
