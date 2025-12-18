# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
MARTINGALE THEORY SPECIALIST (Tier 3)
Handles martingale properties, stopping times, optional sampling.
"""

import numpy as np
from typing import Dict, Any, List
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class MartingaleTheorySpecialist(BDIAgent):
    """Martingale Theory Specialist - Martingale properties, stopping times"""

    def __init__(self, agent_id='martingale_theory_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        self.martingale_tests_performed = 0
        if self.df:
            self._register_services()
        logger.info(f"[{self.agent_id}] Martingale Theory Specialist initialized")

    def _register_services(self):
        self.df.register(create_service_registration(
            service_type='math.stochastic.martingale', agent_id=self.agent_id,
            algorithm='martingale_tests', cost='medium', instance=self,
            type='specialist', tier='3', capabilities='martingale_test_stopping_times'
        ))

    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')

            if 'is martingale' in raw_input.lower() or 'verify martingale' in raw_input.lower():
                result = self._verify_martingale_property(
                    process_type=metadata.get('process_type', 'brownian'),
                    drift=metadata.get('drift', 0.0)
                )
            else:
                result = self._compute_stopping_time(
                    barrier=metadata.get('barrier', 1.0),
                    n_simulations=metadata.get('n_simulations', 1000)
                )

            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result, 'martingale_analysis')
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error: {e}")
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _verify_martingale_property(self, process_type, drift):
        """Verify if process is a martingale"""
        self.martingale_tests_performed += 1

        # Brownian motion with zero drift is a martingale
        is_martingale = (process_type == 'brownian' and drift == 0.0)

        return {
            'operation': 'verify_martingale',
            'process_type': process_type,
            'drift': drift,
            'is_martingale': is_martingale,
            'reason': 'E[X(t)|F(s)] = X(s) for all t >= s' if is_martingale else 'Drift breaks martingale property',
            'explanation': f'Process {"IS" if is_martingale else "IS NOT"} a martingale'
        }

    def _compute_stopping_time(self, barrier, n_simulations):
        """Compute stopping time statistics"""
        # Simulate Brownian motion until hitting barrier
        stopping_times = []
        dt = 0.01
        max_time = 100.0

        for _ in range(n_simulations):
            X, t = 0.0, 0.0
            while t < max_time:
                X += np.random.normal(0, np.sqrt(dt))
                t += dt
                if abs(X) >= barrier:
                    stopping_times.append(t)
                    break

        if stopping_times:
            mean_st = np.mean(stopping_times)
            std_st = np.std(stopping_times)
        else:
            mean_st, std_st = None, None

        return {
            'operation': 'stopping_time',
            'barrier': barrier,
            'n_simulations': n_simulations,
            'mean_stopping_time': mean_st,
            'std_stopping_time': std_st,
            'hit_rate': len(stopping_times) / n_simulations,
            'explanation': f'Stopping time to barrier {barrier}: mean = {mean_st}'
        }

    def _create_result_entry(self, task_entry, result, operation):
        if not self.blackboard:
            return result
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
                           self.agent_id, task_entry.conversation_id,
                           ['martingale', 'result'], EntryStatus.COMPLETED,
                           {'result': result, 'operation': operation})
        self.blackboard.post(entry)
        return entry

    def _create_error_entry(self, task_entry, error_msg):
        if not self.blackboard:
            return {'error': error_msg}
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(f"ERROR: {error_msg}"),
                           self.agent_id, task_entry.conversation_id,
                           ['error'], EntryStatus.FAILED, {'error': error_msg})
        self.blackboard.post(entry)
        return entry

    def update_beliefs(self):
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['martingale'], status=EntryStatus.PENDING)
            for task in tasks:
                belief_key = f'pending_martingale_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, 1.0, 'blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_martingale_'):
                continue
            task = belief.content
            if any(i.metadata.get('task_id') == task.entry_id for i in self.intentions):
                continue
            new_intentions.append(Intention(
                f'analyze_{task.entry_id}', ['claim', 'analyze', 'post'],
                'analyze_martingale', {'task_id': task.entry_id, 'task_entry': task}
            ))
        return new_intentions

    def execute_step(self, intention: Intention):
        action = intention.get_current_action()
        if action == 'claim':
            intention.advance()
        elif action == 'analyze':
            result = self.process(intention.metadata.get('task_entry'))
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post':
            intention.mark_completed()

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'martingale_tests_performed': self.martingale_tests_performed
        })
        return stats
