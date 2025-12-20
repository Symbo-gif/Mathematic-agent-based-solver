# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""REARRANGEMENT INEQUALITY SPECIALIST - Ordering inequalities"""

import logging
import numpy as np
from typing import Any, Dict, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.inequalities import rearrangement_inequality

logger = logging.getLogger(__name__)


class RearrangementInequalitySpecialist(BDIAgent):
    """Rearrangement Inequality - Sort-and-Multiply Optimization"""

    def __init__(self, agent_id='rearrangement_inequality_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = 0

        if df:
            df.register(create_service_registration(
                service_type='math.inequalities.rearrangement',
                agent_id=agent_id, algorithm='native_rearrangement',
                cost='low', instance=self, tier='3'
            ))

    def update_beliefs(self):
        if self.blackboard:
            try:
                for task in self.blackboard.query_entries(tags=['rearrangement'], status=EntryStatus.PENDING):
                    if not self.has_belief(f'p_{task.entry_id}'):
                        self.add_belief(f'p_{task.entry_id}', task, confidence=1.0)
            except:
                pass

    def deliberate(self):
        return [Intention(f'r_{b.content.entry_id}', ['verify'], 'rearrange', {'t': b.content})
                for p, b in self.beliefs.items() if p.startswith('p_')]

    def execute_step(self, intention):
        if intention.get_current_action() == 'verify':
            task = intention.metadata['t']
            meta = task.metadata if hasattr(task, 'metadata') else {}
            try:
                result = rearrangement_inequality(meta.get('a', []), meta.get('b', []))
                self.tasks_succeeded += 1
            except Exception as e:
                result = {'error': str(e)}
            self.tasks_executed += 1
            if self.blackboard:
                self.blackboard.post(create_entry(EntryType.PARTIAL_RESULT,
                                                 str(result), self.agent_id,
                                                 tags=['rearrangement'], status=EntryStatus.COMPLETED))
            intention.advance()

    def process(self, task_entry):
        meta = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        try:
            return rearrangement_inequality(meta.get('a', []), meta.get('b', []))
        except Exception as e:
            return {'error': str(e)}

    def get_statistics(self):
        return {'tasks_executed': self.tasks_executed, 'tasks_succeeded': self.tasks_succeeded}
