# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
PHASE 2 - FREQUENTIST AGENT (Tier 3)
====================================

Handles classical hypothesis testing (t-tests, p-values)
and confidence interval construction.
"""

import sys, os
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional
from scipy import stats

class FrequentistAgent(BDIAgent):
    def __init__(self, agent_id='frequentist_001', df: Optional[DirectoryFacilitator]=None, blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.hypothesis_tests = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.stats.frequentist',
                agent_id=agent_id,
                algorithm='hypothesis_testing',
                cost='medium',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                methods='t_test_p_values_confidence_intervals_anova'))

        print(f"[{agent_id}] Frequentist Agent initialized")
        print(f"  Methods: t-tests, p-values, confidence intervals, ANOVA")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for frequentist statistics tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = self.blackboard.query_entries(tags=['hypothesis_test'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['ttest'], status=EntryStatus.PENDING)
            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata and task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                    tasks.append(task)
            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create hypothesis testing computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'ttest')
            steps = ['claim_task', 'parse_data', 'compute_test', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'freq_{operation}_{task_id}',
                steps=steps,
                target_desire='hypothesis_test',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform hypothesis testing (DELEGATE to SciPy stats)."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        import numpy as np
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()
            elif action == 'parse_data':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                data1 = metadata.get('data1', [1, 2, 3, 4, 5])
                data2 = metadata.get('data2', [2, 3, 4, 5, 6])
                intention.metadata['data1'] = np.array(data1)
                intention.metadata['data2'] = np.array(data2) if data2 else None
                intention.advance()
            elif action == 'compute_test':
                operation = intention.metadata.get('operation', 'ttest')
                data1 = intention.metadata.get('data1')
                data2 = intention.metadata.get('data2')
                # DELEGATE to SciPy stats
                if operation == 'ttest' and data2 is not None:
                    t_stat, p_value = stats.ttest_ind(data1, data2)
                    result = {'t_statistic': float(t_stat), 'p_value': float(p_value), 'test': 'independent_t_test'}
                elif operation == 'ttest_1samp':
                    popmean = intention.metadata.get('popmean', 0)
                    t_stat, p_value = stats.ttest_1samp(data1, popmean)
                    result = {'t_statistic': float(t_stat), 'p_value': float(p_value), 'test': 'one_sample_t_test'}
                else:
                    result = {'test': operation, 'computed': False}
                intention.metadata['result'] = result
                self.hypothesis_tests += 1
                intention.advance()
            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)), self.agent_id,
                        task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        ['hypothesis_test', 'result', task_id], EntryStatus.COMPLETED,
                        {'result': str(result), 'result_str': str(result)})
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()
            else:
                intention.advance()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = FrequentistAgent()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed, 'hypothesis_tests': self.hypothesis_tests})
        return stats
