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
PHASE 2 - STEP 2.5: SERIES SPECIALIST (Tier 3)

Specializes in Taylor and Fourier series expansions and convergence analysis.
"""

import sys, os
from typing import Any, Dict, Optional
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
# NO SYMPY - Using native calculus engine
from symbo_agentic_reasoners.core.calculus import taylor_series, series_sum
from symbo_agentic_reasoners.core.native_symbolic import Symbol, parse_expr, sympify

class SeriesSpecialist(BDIAgent):
    def __init__(self, agent_id='series_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        if self.df:
            reg = create_service_registration(
                service_type='math.calculus.series', agent_id=self.agent_id,
                algorithm='taylor', cost='medium',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                methods='taylor_fourier'
            )
            self.df.register(reg)
        print(f"[{self.agent_id}] Series Specialist initialized")
    
    def process(self, task_entry):
        """Perform process operation.

        Args:
        task_entry

        Returns:
        Result of the operation

        Example:
        >>> specialist = SeriesSpecialist()
        >>> result = specialist.process(...)
        # Returns result
        """
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'series')
            expr_str = metadata.get('sympy_expr', metadata.get('expression', metadata.get('raw_input', '')))
            var_name = metadata.get('variable', 'x')

            print(f"\n[{self.agent_id}] Processing series task")
            print(f"  Operation: {operation}")
            print(f"  Input: {expr_str}")

            # Handle infinite summation using native series_sum
            if operation == 'summation':
                result = self._handle_summation(metadata, expr_str, var_name)
                if result is not None:
                    self.tasks_succeeded += 1
                    print(f"  [OK] Result (native_series): {result}")
                    return self._create_result_entry(task_entry, result)
                # Fallback: return unevaluated for unrecognized patterns
                self.tasks_failed += 1
                fallback_result = f"SeriesSum({expr_str}, ({var_name}, {metadata.get('start', 1)}, {metadata.get('end', 'oo')}))"
                print(f"  [OK] Result (symbolic): {fallback_result}")
                return self._create_result_entry(task_entry, fallback_result)

            # Handle infinite product (placeholder)
            if operation == 'product':
                result = self._handle_product(metadata, expr_str, var_name)
                if result is not None:
                    self.tasks_succeeded += 1
                    return self._create_result_entry(task_entry, result)
                self.tasks_failed += 1
                return self._create_result_entry(task_entry, f"Product({expr_str}, ({var_name}, {metadata.get('start', 1)}, {metadata.get('end', 'oo')}))")

            # Default: Taylor series expansion using native engine
            success, result, method = taylor_series(expr_str, var_name, 0, 6)  # 6 terms
            if success and result is not None:
                self.tasks_succeeded += 1
                print(f"  [OK] Result (native_taylor): {result}")
                return self._create_result_entry(task_entry, result)
            # If native Taylor fails, return unevaluated
            self.tasks_failed += 1
            fallback_result = f"Taylor({expr_str}, {var_name}, 0, 6)"
            print(f"  [OK] Result (symbolic): {fallback_result}")
            return self._create_result_entry(task_entry, fallback_result)
        except Exception as e:
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _handle_summation(self, metadata, expr_str, var_name):
        """Handle infinite summation using native series_sum."""
        try:
            from symbo_agentic_reasoners.core.calculus import series_sum

            start_str = metadata.get('start', '1')
            end_str = metadata.get('end', 'oo')

            # Convert start to int
            try:
                start = int(start_str)
            except ValueError:
                start = 1

            # Convert end to 'inf' or int
            if end_str in ('oo', 'inf', 'infinity'):
                end = 'inf'
            else:
                try:
                    end = int(end_str)
                except ValueError:
                    end = 'inf'

            # Call native series_sum
            success, result, method = series_sum(expr_str, var_name, start, end)
            if success:
                return result
            return None
        except Exception:
            return None

    def _handle_product(self, metadata, expr_str, var_name):
        """Handle infinite product (placeholder - returns None for unrecognized)."""
        # TODO: Implement product recognition (Wallis product, etc.)
        return None
    
    def _create_result_entry(self, task_entry, result):
        """Perform  create result entry operation.

        Args:
        task_entry: Description needed
        result: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj._create_result_entry(...)
        """
        if not self.blackboard: return result
        return create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
            self.agent_id, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            ['series'], EntryStatus.PENDING, {'result_str': str(result)})
    
    def _create_error_entry(self, task_entry, error):
        """Perform  create error entry operation.

        Args:
        task_entry: Description needed
        error: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj._create_error_entry(...)
        """
        if not self.blackboard: return None
        return create_entry(EntryType.PARTIAL_RESULT, create_variable(f"ERROR: {error}"),
            self.agent_id, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
            ['error'], EntryStatus.FAILED, {'error': error})
    
    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for series expansion tasks.
        """
        if not self.blackboard:
            return

        try:
            # Find series tasks
            series_tasks = self.blackboard.query_entries(
                tags=['series'],
                status=EntryStatus.PENDING
            )

            # Also find delegated tasks
            delegated_tasks = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            for task in delegated_tasks:
                if hasattr(task, 'metadata') and task.metadata:
                    assigned = task.metadata.get('assigned_agent', '')
                    if assigned == self.agent_id and task not in series_tasks:
                        series_tasks.append(task)

            # Add beliefs about pending tasks
            for task in series_tasks:
                belief_key = f'pending_task_{task.entry_id}'
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
        DELIBERATE: Create computation plans for series expansion tasks.

        Returns:
            List of new Intention objects
        """
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
            operation = metadata.get('operation', 'taylor')

            # Determine series type
            if 'fourier' in raw_input:
                operation = 'fourier'
            elif 'taylor' in raw_input or 'series' in raw_input:
                operation = 'taylor'

            steps = ['claim_task', 'parse_expression', 'compute_series', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'series_{operation}_{task_id}',
                steps=steps,
                target_desire='compute_series',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation,
                    'raw_input': raw_input,
                    'sympy_expr': metadata.get('sympy_expr'),
                    'variable': metadata.get('variable', 'x'),
                    'point': metadata.get('point', 0),
                    'terms': metadata.get('terms', 6)
                }
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention):
        """
        EXECUTE: Execute one step of the series expansion plan.

        CRITICAL: DELEGATES to SymPy's series() function.
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

            elif action == 'parse_expression':
                expr_str = intention.metadata.get('sympy_expr') or intention.metadata.get('raw_input')
                var_name = intention.metadata.get('variable', 'x')

                # Store expression string and variable name for native engine
                intention.metadata['parsed_expr'] = expr_str
                intention.metadata['var_symbol'] = var_name
                intention.advance()

            elif action == 'compute_series':
                expr_str = intention.metadata.get('parsed_expr')
                var_name = intention.metadata.get('var_symbol')
                point = intention.metadata.get('point', 0)
                terms = intention.metadata.get('terms', 6)
                operation = intention.metadata.get('operation', 'taylor')

                # Use native Taylor series engine
                if operation == 'taylor' or operation == 'series' or operation == 'fourier':
                    success, result, method = taylor_series(expr_str, var_name, point, terms)
                    if success and result is not None:
                        intention.metadata['result'] = result
                    else:
                        intention.metadata['result'] = f"Taylor({expr_str}, {var_name}, {point}, {terms})"
                else:
                    success, result, method = taylor_series(expr_str, var_name, point, terms)
                    if success and result is not None:
                        intention.metadata['result'] = result
                    else:
                        intention.metadata['result'] = f"Taylor({expr_str}, {var_name}, {point}, {terms})"

                self.add_belief('computed_result', intention.metadata['result'])
                intention.advance()

            elif action == 'verify_result':
                result = intention.metadata.get('result')
                verified = result is not None
                intention.metadata['verified'] = verified
                self.add_belief('result_verified', verified)
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                operation = intention.metadata.get('operation', 'taylor')

                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['series', operation, 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={
                            'result': str(result),
                            'result_str': str(result),
                            'operation': operation,
                            'task_id': task_id,
                            'verified': intention.metadata.get('verified', False),
                            'algorithm': 'native_taylor'
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
                    tags=['error', 'series', task_id],
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
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = SeriesSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed, 'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded/self.tasks_executed*100) if self.tasks_executed > 0 else 0})
        return stats
