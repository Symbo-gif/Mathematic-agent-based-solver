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
RECURRENCE RELATION VIA GF SPECIALIST (Tier 3)
===============================================

Handles solving recurrence relations using generating function methods.

CAPABILITIES:
------------
- solve_linear: Solve linear recurrence aₙ = c₁a_{n-1} + ... + cₖa_{n-k}
- fibonacci: Specialized Fibonacci solver
- general_recurrence: Arbitrary order linear recurrence
- characteristic_gf: Build characteristic generating function

FORMULATION:
-----------
Linear recurrence: aₙ = c₁a_{n-1} + c₂a_{n-2} + ... + cₖa_{n-k}
Characteristic GF: A(x) = (numerator) / (1 - c₁x - c₂x² - ... - cₖxᵏ)

ALGORITHMIC BACKING:
-------------------
Native generating_functions engine (core/generating_functions.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Wilf, H. S. (2006). Generatingfunctionology, Chapter 2.
- Graham et al. (1994). Concrete Mathematics, Chapter 7.
"""

import logging
from typing import Any, Dict, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.generating_functions import (
    solve_recurrence_via_gf, fibonacci_gf
)

logger = logging.getLogger(__name__)


class RecurrenceGFSpecialist(BDIAgent):
    """
    Recurrence via GF Specialist - Solve Linear Recurrences

    DIRECTIVE:
    ---------
    Solve linear recurrence relations using generating function techniques.

    OPERATIONS:
    ----------
    - solve_linear: Solve aₙ = c₁a_{n-1} + ... + cₖa_{n-k}
    - fibonacci_gf: Fibonacci sequence via GF
    - compute_term: Compute specific term aₙ
    - generate_sequence: Generate sequence up to index n

    FORMULATION:
    -----------
    Linear recurrence: aₙ = c₁a_{n-1} + c₂a_{n-2} + ... + cₖa_{n-k}

    GF method:
    1. Form A(x) = (numerator) / (1 - c₁x - c₂x² - ... - cₖxᵏ)
    2. Extract [xⁿ]A(x) via series expansion

    REFERENCE:
    ---------
    - Wilf (2006), Chapter 2: Recurrence Relations
    - Graham et al. (1994), Concrete Mathematics
    """

    def __init__(
        self,
        agent_id: str = 'recurrence_gf_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Recurrence GF Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.recurrences_solved = 0
        self.fibonacci_computed = 0
        self.terms_computed = 0
        self.sequences_generated = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.discrete.gf.recurrence',
            agent_id=self.agent_id,
            algorithm='recurrence_via_gf',
            cost='low',
            instance=self,
            tier='3',
            operations='solve_linear_fibonacci_term_sequence'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.discrete.gf.recurrence")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for recurrence GF tasks."""
        if not self.blackboard:
            return

        try:
            recurrence_tasks = self.blackboard.query_entries(
                tags=['recurrence', 'recurrence_gf', 'fibonacci'],
                status=EntryStatus.PENDING
            )

            for task in recurrence_tasks:
                belief_key = f'pending_recurrence_{task.entry_id}'

                if self.has_belief(f'completed_{task.entry_id}'):
                    continue

                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans for pending recurrence tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_recurrence_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'solve_linear')

            intention = Intention(
                plan_id=f'recurrence_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='solve_recurrence',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan for recurrence task {task_id} ({operation})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the recurrence solving plan."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        logger.debug(f"[{self.agent_id}] Executing: {action} for task {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task_id)
            elif action == 'parse_input':
                self._execute_parse_input(intention, task)
            elif action == 'compute':
                self._execute_compute(intention)
            elif action == 'verify':
                self._execute_verify(intention)
            elif action == 'post_result':
                self._execute_post_result(intention, task)
            else:
                logger.warning(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_failure(intention, task, str(e))

    def _execute_claim_task(self, intention: Intention, task_id: str):
        """Claim task as IN_PROGRESS."""
        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
        intention.advance()

    def _execute_parse_input(self, intention: Intention, task: Any):
        """Parse and validate input parameters."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}

        parsed_data = {
            'operation': intention.metadata.get('operation', 'solve_linear'),
            'coefficients': metadata.get('coefficients', [1, 1]),  # Default: Fibonacci
            'initial_values': metadata.get('initial_values', metadata.get('initials', [0, 1])),
            'n': metadata.get('n', 10),
            'max_terms': metadata.get('max_terms', 1000),
            'n_terms': metadata.get('n_terms', 10)
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Solve recurrence using GF method."""
        parsed_data = intention.metadata.get('parsed_data', {})
        operation = parsed_data['operation']

        try:
            if operation == 'solve_linear':
                coefficients = parsed_data['coefficients']
                initial_values = parsed_data['initial_values']
                n = parsed_data['n']
                max_terms = parsed_data['max_terms']

                term = solve_recurrence_via_gf(coefficients, initial_values, n, max_terms)

                result = {
                    'term': float(term),
                    'n': n,
                    'coefficients': coefficients,
                    'initial_values': initial_values,
                    'operation': 'solve_linear',
                    'formula': f'a_n = {" + ".join(f"{c}*a_{{n-{i+1}}}" for i, c in enumerate(coefficients))}'
                }
                self.recurrences_solved += 1
                self.terms_computed += 1

            elif operation == 'fibonacci_gf':
                n_terms = parsed_data['n_terms']
                gf = fibonacci_gf(n_terms)

                result = {
                    'coefficients': gf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'operation': 'fibonacci_gf',
                    'formula': 'x/(1-x-x²)'
                }
                self.fibonacci_computed += 1

            elif operation == 'fibonacci_term':
                n = parsed_data['n']
                term = solve_recurrence_via_gf([1, 1], [0, 1], n)

                result = {
                    'fibonacci_n': int(term),
                    'n': n,
                    'operation': 'fibonacci_term'
                }
                self.fibonacci_computed += 1
                self.terms_computed += 1

            elif operation == 'generate_sequence':
                coefficients = parsed_data['coefficients']
                initial_values = parsed_data['initial_values']
                n_terms = parsed_data['n_terms']

                sequence = []
                for i in range(n_terms):
                    term = solve_recurrence_via_gf(coefficients, initial_values, i)
                    sequence.append(float(term))

                result = {
                    'sequence': sequence,
                    'n_terms': n_terms,
                    'coefficients': coefficients,
                    'initial_values': initial_values,
                    'operation': 'generate_sequence'
                }
                self.sequences_generated += 1

            else:
                raise ValueError(f"Unknown recurrence operation: {operation}")

            result['method'] = 'recurrence_gf'
            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"Recurrence solving failed: {e}")

    def _execute_verify(self, intention: Intention):
        """Verify result validity."""
        result = intention.metadata.get('result', {})

        if 'sequence' in result:
            if not isinstance(result['sequence'], list):
                raise ValueError("Sequence must be a list")

        intention.advance()

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result to Blackboard."""
        result = intention.metadata.get('result', {})
        task_id = intention.metadata.get('task_id')

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'recurrence',
                tags=['recurrence_gf', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_recurrence_{task_id}')
        self.add_belief(f'completed_{task_id}', result)

        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"Recurrence solving failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'recurrence_gf', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        self.remove_belief(f'pending_recurrence_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Synchronous API for recurrence solving.

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Result dictionary with computed term or sequence
        """
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'solve_linear')

        try:
            if operation == 'solve_linear':
                coefficients = metadata.get('coefficients', [1, 1])
                initial_values = metadata.get('initial_values', [0, 1])
                n = metadata.get('n', 10)

                term = solve_recurrence_via_gf(coefficients, initial_values, n)

                result = {
                    'term': float(term),
                    'n': n,
                    'method': 'recurrence_gf'
                }
                self.recurrences_solved += 1

            elif operation == 'fibonacci_term':
                n = metadata.get('n', 10)
                term = solve_recurrence_via_gf([1, 1], [0, 1], n)

                result = {
                    'fibonacci_n': int(term),
                    'n': n,
                    'method': 'fibonacci_gf'
                }
                self.fibonacci_computed += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'recurrence_gf'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'recurrences_solved': self.recurrences_solved,
            'fibonacci_computed': self.fibonacci_computed,
            'terms_computed': self.terms_computed,
            'sequences_generated': self.sequences_generated,
            'tier': '3',
            'type': 'specialist',
            'domain': 'generating_functions'
        })
        return stats


if __name__ == "__main__":
    """Test Recurrence GF Specialist"""
    print("=" * 80)
    print("RECURRENCE GF SPECIALIST TEST")
    print("=" * 80)
    print()

    specialist = RecurrenceGFSpecialist()
    print()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    # Test 1: Fibonacci F(10)
    print("Test 1: Fibonacci F(10)")
    task1 = MockTask({
        'operation': 'fibonacci_term',
        'n': 10
    })
    result1 = specialist.process(task1)
    print(f"  F(10) = {result1['fibonacci_n']}")
    print(f"  Expected: 55")
    print()

    # Test 2: Custom recurrence
    print("Test 2: a_n = 2*a_{n-1} + a_{n-2}, a_0=1, a_1=1, find a_5")
    task2 = MockTask({
        'operation': 'solve_linear',
        'coefficients': [2, 1],
        'initial_values': [1, 1],
        'n': 5
    })
    result2 = specialist.process(task2)
    print(f"  a_5 = {result2['term']}")
    print()

    # Statistics
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
