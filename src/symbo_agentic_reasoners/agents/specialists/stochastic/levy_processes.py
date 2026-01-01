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
LEVY PROCESS SPECIALIST (Tier 3)
Handles Levy processes and jump processes.
"""

import numpy as np
from typing import Dict, Any, List
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class LevyProcessSpecialist(BDIAgent):
    """Levy Process Specialist - Jump processes, compound Poisson"""

    def __init__(self, agent_id='levy_process_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        self.levy_processes_generated = 0
        if self.df:
            self._register_services()
        logger.info(f"[{self.agent_id}] Levy Process Specialist initialized")

    def _register_services(self):
        self.df.register(create_service_registration(
            service_type='math.stochastic.levy', agent_id=self.agent_id,
            algorithm='compound_poisson', cost='medium', instance=self,
            type='specialist', tier='3', capabilities='compound_poisson_jump_processes'
        ))

    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            result = self._generate_compound_poisson(
                lambda_rate=metadata.get('lambda_rate', 1.0),
                jump_mean=metadata.get('jump_mean', 0.0),
                jump_std=metadata.get('jump_std', 1.0),
                T=metadata.get('T', 1.0),
                n_steps=metadata.get('n_steps', 1000)
            )
            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result, 'compound_poisson')
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error: {e}")
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _generate_compound_poisson(self, lambda_rate, jump_mean, jump_std, T, n_steps):
        """Generate compound Poisson process"""
        self.levy_processes_generated += 1
        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)
        
        # Generate Poisson arrivals
        n_arrivals = np.random.poisson(lambda_rate * T)
        arrival_times = np.sort(np.random.uniform(0, T, n_arrivals))
        jump_sizes = np.random.normal(jump_mean, jump_std, n_arrivals)
        
        # Build path
        X = np.zeros(n_steps + 1)
        for i, ta in enumerate(arrival_times):
            idx = int(ta / dt)
            if idx < n_steps:
                X[idx:] += jump_sizes[i]
        
        return {
            'operation': 'compound_poisson',
            'lambda_rate': lambda_rate,
            'jump_mean': jump_mean,
            'jump_std': jump_std,
            'T': T,
            'n_arrivals': n_arrivals,
            'times': t.tolist(),
            'path': X.tolist(),
            'final_value': float(X[-1]),
            'explanation': f'Generated compound Poisson with rate {lambda_rate}, {n_arrivals} jumps'
        }

    def _create_result_entry(self, task_entry, result, operation):
        if not self.blackboard:
            return result
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
                           self.agent_id, task_entry.conversation_id,
                           ['levy', 'result'], EntryStatus.COMPLETED,
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
            tasks = self.blackboard.query_entries(tags=['levy'], status=EntryStatus.PENDING)
            for task in tasks:
                belief_key = f'pending_levy_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, 1.0, 'blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_levy_'):
                continue
            task = belief.content
            if any(i.metadata.get('task_id') == task.entry_id for i in self.intentions):
                continue
            new_intentions.append(Intention(
                f'solve_{task.entry_id}', ['claim', 'solve', 'post'],
                'solve_levy_task', {'task_id': task.entry_id, 'task_entry': task}
            ))
        return new_intentions

    def execute_step(self, intention: Intention):
        action = intention.get_current_action()
        if action == 'claim':
            intention.advance()
        elif action == 'solve':
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
            'levy_processes_generated': self.levy_processes_generated
        })
        return stats
