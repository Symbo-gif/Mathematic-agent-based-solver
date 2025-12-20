# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""CONVEX FUNCTION SPECIALIST - Convexity verification and testing"""

import logging
import numpy as np
from typing import Any, Dict, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.convex_analysis import (
    verify_convexity_first_order, verify_convexity_second_order,
    numerical_hessian, is_positive_semidefinite
)

logger = logging.getLogger(__name__)


class ConvexFunctionSpecialist(BDIAgent):
    """Convex Function Specialist - First/Second-Order Tests"""

    def __init__(self, agent_id='convex_function_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.convexity_tests = 0

        if df:
            df.register(create_service_registration(
                service_type='math.convexity.functions',
                agent_id=agent_id, algorithm='first_second_order_tests',
                cost='medium', instance=self, tier='3',
                operations='verify_convex_first_order_second_order_hessian_test'
            ))

    def update_beliefs(self):
        if self.blackboard:
            try:
                for task in self.blackboard.query_entries(tags=['convex_function'], status=EntryStatus.PENDING):
                    if not self.has_belief(f'p_{task.entry_id}'):
                        self.add_belief(f'p_{task.entry_id}', task, 1.0)
            except:
                pass

    def deliberate(self):
        return [Intention(f'cf_{b.content.entry_id}', ['test'], 'convex_func', {'t': b.content})
                for p, b in self.beliefs.items() if p.startswith('p_')]

    def execute_step(self, intention):
        if intention.get_current_action() == 'test':
            task = intention.metadata['t']
            meta = task.metadata if hasattr(task, 'metadata') else {}
            method = meta.get('method', 'second_order')

            try:
                if method == 'first_order':
                    result = verify_convexity_first_order(
                        meta['f'], meta['grad_f'], meta['x'], meta['y']
                    )
                elif method == 'second_order':
                    hess_f = meta.get('hess_f', lambda x: numerical_hessian(meta['f'], x))
                    result = verify_convexity_second_order(hess_f, meta['domain_points'])
                else:
                    result = {'error': 'Unknown method'}

                self.convexity_tests += 1
                self.tasks_succeeded += 1
            except Exception as e:
                result = {'error': str(e)}

            self.tasks_executed += 1
            intention.metadata['result'] = result
            if self.blackboard:
                self.blackboard.post(create_entry(EntryType.PARTIAL_RESULT, str(result),
                                                 self.agent_id, tags=['convex_function'],
                                                 status=EntryStatus.COMPLETED))
            intention.advance()

    def process(self, task_entry):
        meta = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        method = meta.get('method', 'second_order')
        try:
            if method == 'first_order':
                return verify_convexity_first_order(meta['f'], meta['grad_f'], meta['x'], meta['y'])
            hess_f = meta.get('hess_f', lambda x: numerical_hessian(meta['f'], x))
            return verify_convexity_second_order(hess_f, meta['domain_points'])
        except Exception as e:
            return {'error': str(e)}

    def get_statistics(self):
        return {'tasks_executed': self.tasks_executed, 'convexity_tests': self.convexity_tests}
