# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""PROXIMAL OPERATOR SPECIALIST - Proximal mappings and Moreau envelopes"""

import logging
import numpy as np
from typing import Any, Dict, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.convex_analysis import proximal_l1, proximal_l2, proximal_indicator, moreau_envelope

logger = logging.getLogger(__name__)


class ProximalOperatorSpecialist(BDIAgent):
    """Proximal Operator Specialist - LASSO, Ridge, Projections"""

    def __init__(self, agent_id='proximal_operator_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.proximal_ops = 0

        if df:
            df.register(create_service_registration(
                service_type='math.convexity.proximal',
                agent_id=agent_id, algorithm='soft_threshold_shrinkage',
                cost='low', instance=self, tier='3',
                operations='prox_l1_prox_l2_projection_moreau'
            ))

    def update_beliefs(self):
        if self.blackboard:
            try:
                for task in self.blackboard.query_entries(tags=['proximal'], status=EntryStatus.PENDING):
                    if not self.has_belief(f'p_{task.entry_id}'):
                        self.add_belief(f'p_{task.entry_id}', task, 1.0)
            except:
                pass

    def deliberate(self):
        return [Intention(f'prox_{b.content.entry_id}', ['compute'], 'proximal', {'t': b.content})
                for p, b in self.beliefs.items() if p.startswith('p_')]

    def execute_step(self, intention):
        if intention.get_current_action() == 'compute':
            task = intention.metadata['t']
            meta = task.metadata if hasattr(task, 'metadata') else {}
            prox_type = meta.get('prox_type', 'l1')

            try:
                x = np.array(meta.get('x', []))
                lam = meta.get('lambda', 1.0)

                if prox_type == 'l1':
                    result = {'prox': proximal_l1(x, lam).tolist()}
                elif prox_type == 'l2':
                    result = {'prox': proximal_l2(x, lam).tolist()}
                elif prox_type == 'indicator':
                    convex_set = np.array(meta['convex_set'])
                    result = {'prox': proximal_indicator(x, convex_set).tolist()}
                elif prox_type == 'moreau':
                    f = meta['f']
                    result = {'moreau_value': moreau_envelope(f, x, lam)}
                else:
                    result = {'prox': proximal_l1(x, lam).tolist()}

                self.proximal_ops += 1
                self.tasks_succeeded += 1
            except Exception as e:
                result = {'error': str(e)}

            self.tasks_executed += 1
            if self.blackboard:
                self.blackboard.post(create_entry(EntryType.PARTIAL_RESULT, str(result),
                                                 self.agent_id, tags=['proximal'],
                                                 status=EntryStatus.COMPLETED))
            intention.advance()

    def process(self, task_entry):
        meta = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        try:
            x = np.array(meta.get('x', []))
            lam = meta.get('lambda', 1.0)
            prox_type = meta.get('prox_type', 'l1')

            if prox_type == 'l1':
                return {'prox': proximal_l1(x, lam).tolist()}
            elif prox_type == 'l2':
                return {'prox': proximal_l2(x, lam).tolist()}
            elif prox_type == 'indicator':
                return {'prox': proximal_indicator(x, np.array(meta['convex_set'])).tolist()}
            return {'prox': proximal_l1(x, lam).tolist()}
        except Exception as e:
            return {'error': str(e)}

    def get_statistics(self):
        return {'tasks_executed': self.tasks_executed, 'proximal_ops': self.proximal_ops}
