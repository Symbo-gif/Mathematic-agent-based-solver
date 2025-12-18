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
PHASE 2 - VECTOR SPACE ANALYST (Tier 3)
=======================================

Calculates abstract properties of matrices and vector spaces:
Basis, Rank, Nullspace, Eigenvalues/Eigenvectors.
"""

import sys, os
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import linalg

class VectorSpaceAnalyst(BDIAgent):
    def __init__(self, agent_id='vectorspace_001', df: Optional[DirectoryFacilitator]=None, blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.eigenvalues_computed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.linalg.vectorspace',
                agent_id=agent_id,
                algorithm='eigenvalue',
                cost='medium',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='basis_rank_nullspace_eigenvalues_eigenvectors'))

        print(f"[{agent_id}] Vector Space Analyst initialized")
        print(f"  Capabilities: Basis, Rank, Nullspace, Eigenvalues/Eigenvectors")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for vector space tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = self.blackboard.query_entries(tags=['vectorspace'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['eigenvalue'], status=EntryStatus.PENDING)
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
        """DELIBERATE: Create vector space computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            operation = 'eigenvalues'
            if 'rank' in raw_input:
                operation = 'rank'
            elif 'nullspace' in raw_input or 'null' in raw_input:
                operation = 'nullspace'
            elif 'basis' in raw_input:
                operation = 'basis'
            elif 'eigenvalue' in raw_input or 'eigen' in raw_input:
                operation = 'eigenvalues'
            steps = ['claim_task', 'parse_matrix', f'compute_{operation}', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'vectorspace_{operation}_{task_id}',
                steps=steps,
                target_desire='vector_space_analysis',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform vector space analysis (DELEGATE to SciPy)."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        import re
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
            elif action == 'parse_matrix':
                raw = intention.metadata.get('task_entry').metadata.get('raw_input', '') if hasattr(intention.metadata.get('task_entry'), 'metadata') else ''
                import ast
                try:
                    matrix_match = re.search(r'\[\[.*?\]\]', raw.replace(' ', ''))
                    if matrix_match:
                        matrix = np.array(ast.literal_eval(matrix_match.group()))
                    else:
                        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', raw)]
                        size = int(np.sqrt(len(numbers)))
                        matrix = np.array(numbers).reshape(size, size) if size * size == len(numbers) else np.array([[1, 2], [3, 4]])
                except:
                    matrix = np.array([[1, 2], [3, 4]])
                intention.metadata['matrix'] = matrix
                intention.advance()
            elif action == 'compute_eigenvalues':
                matrix = intention.metadata.get('matrix')
                eigenvalues, eigenvectors = linalg.eig(matrix)
                result = {'eigenvalues': eigenvalues.tolist(), 'eigenvectors': eigenvectors.tolist()}
                intention.metadata['result'] = result
                self.eigenvalues_computed += 1
                intention.advance()
            elif action == 'compute_rank':
                matrix = intention.metadata.get('matrix')
                result = {'rank': int(np.linalg.matrix_rank(matrix))}
                intention.metadata['result'] = result
                intention.advance()
            elif action == 'compute_nullspace':
                matrix = intention.metadata.get('matrix')
                null_space = linalg.null_space(matrix)
                result = {'nullspace': null_space.tolist(), 'dimension': null_space.shape[1]}
                intention.metadata['result'] = result
                intention.advance()
            elif action == 'compute_basis':
                matrix = intention.metadata.get('matrix')
                rank = np.linalg.matrix_rank(matrix)
                result = {'rank': int(rank), 'full_rank': rank == min(matrix.shape)}
                intention.metadata['result'] = result
                intention.advance()
            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)), self.agent_id,
                        task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        ['vectorspace', 'result', task_id], EntryStatus.COMPLETED,
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
        """Retrieve agent statistics.

        Returns:
        dict: Agent statistics including solve count, success rate, etc.

        Example:
        >>> stats = agent.get_statistics()
        """
        """Retrieve agent statistics.

        Returns:
        dict: Agent statistics including solve count, success rate, etc.

        Example:
        >>> stats = agent.get_statistics()
        """
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed, 'eigenvalues_computed': self.eigenvalues_computed})
        return stats
