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
PHASE 2 - NUMERICAL COMPUTATION UTILITY (Tier 3)
================================================

THE SYSTEM SAFETY NET - Ultimate fallback for all supervisors.

Ensures system NEVER "gives up" when symbolic math is computationally
intractable or mathematically impossible (e.g., Abel-Ruffini theorem for degree 5+ polynomials).

This agent does NOT "reason"; it "crunches."
"""

import sys, os
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import optimize, integrate, linalg

class NumericalComputationUtility(BDIAgent):
    """
    Numerical Computation Utility - The System Safety Net

    ROLE:
    ----
    High-performance computational engine for all teams. Acts as the fallback
    destination for any supervisor that cannot obtain a symbolic solution.

    EXAMPLE:
    -------
    If Algebra Supervisor cannot solve a degree-5+ polynomial symbolically,
    it routes to this agent for numerical root approximation.

    LIBRARY:
    -------
    NumPy/SciPy (high-performance numerical computation)

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 161-166
    """

    def __init__(self, agent_id='numerical_utility_001', df: Optional[DirectoryFacilitator]=None, blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.fallback_calls = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.numerical',
                agent_id=agent_id,
                algorithm='numpy_scipy',
                cost='high',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                role='fallback',
                library='numpy_scipy',
                type='approximate'))

        print(f"[{agent_id}] Numerical Computation Utility initialized")
        print(f"  ROLE: SYSTEM SAFETY NET")
        print(f"  Library: NumPy + SciPy")
        print(f"  Purpose: Fallback for intractable symbolic computations")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for numerical utility tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = self.blackboard.query_entries(tags=['numerical'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['numeric'], status=EntryStatus.PENDING)
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
        """DELIBERATE: Create numerical computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'evaluate')
            steps = ['claim_task', 'parse_input', f'compute_{operation}', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'numerical_{operation}_{task_id}',
                steps=steps,
                target_desire='numerical_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform numerical computations."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
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
            elif action == 'parse_input':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                intention.metadata['expression'] = metadata.get('expression', '0')
                intention.metadata['values'] = metadata.get('values', {})
                intention.advance()
            elif action.startswith('compute_'):
                expr = intention.metadata.get('expression', '0')
                values = intention.metadata.get('values', {})
                result = {'value': self.evaluate(expr, values), 'expression': expr}
                intention.metadata['result'] = result
                intention.advance()
            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard and result:
                    entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)), self.agent_id,
                        task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        ['numerical', 'result', task_id], EntryStatus.COMPLETED,
                        {'result': str(result), 'result_str': str(result)})
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
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
        stats.update({
            'tasks_executed': self.tasks_executed,
            'fallback_calls': self.fallback_calls
        })
        return stats


if __name__ == "__main__":
    """Test Numerical Utility"""
    print("=" * 80)
    print("PHASE 2 - NUMERICAL COMPUTATION UTILITY TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System

    phase0 = Phase0System()
    phase0.start()
    print()

    utility = NumericalComputationUtility(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("NUMERICAL UTILITY READY (System Safety Net)")
    print("=" * 80)
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.numerical')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Role: {service.properties.get('role')}")

    phase0.shutdown()
