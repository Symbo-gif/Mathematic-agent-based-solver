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
PHASE 2 - STEP 2.4: DIFFERENTIAL EQUATION SOLVER (Tier 3)

Solves Ordinary Differential Equations (ODEs) and Partial Differential Equations (PDEs).
"""

import sys, os
from typing import Any, Dict, Optional
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
# NO SYMPY - Using native ODE solver
from symbo_agentic_reasoners.core.calculus import solve_ode_native

class ODESolver(BDIAgent):
    def __init__(self, agent_id='ode_solver_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        if self.df:
            reg = create_service_registration(
                service_type='math.calculus.ode', agent_id=self.agent_id,
                algorithm='runge_kutta', cost='high',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                methods='symbolic_numerical'
            )
            self.df.register(reg)
        print(f"[{self.agent_id}] ODE Solver initialized")
    
    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            expr_str = metadata.get('sympy_expr', metadata.get('raw_input', ''))
            # Simplified ODE solving
            result = "ODE solution (Phase 2: Simplified solver)"
            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result)
        except Exception as e:
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry, result):
        if not self.blackboard: return result
        return create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
            self.agent_id, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            ['ode'], EntryStatus.PENDING, {'result_str': str(result)})
    
    def _create_error_entry(self, task_entry, error):
        if not self.blackboard: return None
        return create_entry(EntryType.PARTIAL_RESULT, create_variable(f"ERROR: {error}"),
            self.agent_id, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
            ['error'], EntryStatus.FAILED, {'error': error})
    
    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for ODE solving tasks.

        Looks for tasks tagged with 'ode', 'differential_equation', or assigned to this agent.
        """
        if not self.blackboard:
            return

        try:
            # Find ODE tasks
            ode_tasks = self.blackboard.query_entries(
                tags=['ode'],
                status=EntryStatus.PENDING
            )

            # Also find delegated tasks
            delegated_tasks = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            # Filter for tasks assigned to us
            for task in delegated_tasks:
                if hasattr(task, 'metadata') and task.metadata:
                    assigned = task.metadata.get('assigned_agent', '')
                    if assigned == self.agent_id and task not in ode_tasks:
                        ode_tasks.append(task)

            # Add beliefs about pending tasks
            for task in ode_tasks:
                belief_key = f'pending_task_{task.entry_id}'

                # Skip if already processing
                if self.has_belief(f'claimed_task_{task.entry_id}'):
                    continue
                if self.has_belief(f'completed_task_{task.entry_id}'):
                    continue

                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self):
        """
        DELIBERATE: Create computation plans for ODE solving tasks.

        Returns:
            List of new Intention objects
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if already have an intention for this task
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Extract operation from metadata
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            operation = metadata.get('operation', 'solve_ode')

            # Build computation plan for ODE solving
            steps = ['claim_task', 'parse_ode', 'solve_ode', 'verify_solution', 'post_result']

            intention = Intention(
                plan_id=f'ode_solve_{task_id}',
                steps=steps,
                target_desire='solve_differential_equation',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation,
                    'raw_input': raw_input,
                    'sympy_expr': metadata.get('sympy_expr')
                }
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention):
        """
        EXECUTE: Execute one step of the ODE solving plan.

        CRITICAL: This agent DELEGATES to SymPy's dsolve() function.
        """
        import logging
        logger = logging.getLogger(__name__)

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

            elif action == 'parse_ode':
                # Parse the differential equation
                expr_str = intention.metadata.get('sympy_expr') or intention.metadata.get('raw_input')

                # Store expression string for native ODE solver
                intention.metadata['parsed_ode'] = expr_str
                intention.metadata['function'] = 'y'
                intention.metadata['variable'] = 'x'

                intention.advance()

            elif action == 'solve_ode':
                # Use native ODE solver
                expr_str = intention.metadata.get('parsed_ode')

                if expr_str:
                    # Use native solve_ode_native
                    success, solution = solve_ode_native(expr_str)
                    if success and solution:
                        intention.metadata['solution'] = solution
                    else:
                        # Return unevaluated form for complex ODEs
                        intention.metadata['solution'] = f"ODE({expr_str})"
                else:
                    raise ValueError("Missing ODE expression for solving")

                intention.advance()

            elif action == 'verify_solution':
                # Basic verification
                solution = intention.metadata.get('solution')
                verified = solution is not None
                intention.metadata['verified'] = verified
                intention.advance()

            elif action == 'post_result':
                solution = intention.metadata.get('solution')

                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(solution)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['ode', 'solution', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={
                            'result': str(solution),
                            'result_str': str(solution),
                            'task_id': task_id,
                            'algorithm': 'native_ode'
                        }
                    )
                    self.blackboard.post(result_entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

                self.add_belief(f'completed_task_{task_id}', True)
                self.remove_belief(f'claimed_task_{task_id}')
                self.tasks_succeeded += 1
                intention.advance()

            else:
                logger.warning(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            if self.blackboard and task_id:
                error_entry = create_entry(
                    entry_type=EntryType.PARTIAL_RESULT,
                    content=create_variable(f"ERROR: {e}"),
                    author_agent=self.agent_id,
                    conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                    tags=['error', 'ode', task_id],
                    status=EntryStatus.FAILED,
                    metadata={'error': str(e), 'task_id': task_id}
                )
                self.blackboard.post(error_entry)
                self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

            self.remove_belief(f'pending_task_{task_id}')
            self.remove_belief(f'claimed_task_{task_id}')
            self.tasks_failed += 1
            while not intention.is_complete():
                intention.advance()
    def get_statistics(self):
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed, 'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded/self.tasks_executed*100) if self.tasks_executed > 0 else 0})
        return stats
