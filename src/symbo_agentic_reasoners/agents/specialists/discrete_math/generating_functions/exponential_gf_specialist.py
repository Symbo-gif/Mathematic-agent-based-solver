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
EXPONENTIAL GENERATING FUNCTION SPECIALIST (Tier 3)
===================================================

Handles exponential generating function construction and labeled structures.

CAPABILITIES:
------------
- from_sequence: Build EGF from coefficient list
- exp_function: e^x = Σ xⁿ/n!
- derangements: Derangement numbers EGF
- stirling_egf: Stirling numbers via EGF method
- labeled_counting: Labeled combinatorial structures

FORMULATION:
-----------
A(x) = Σₙ aₙxⁿ/n! where {aₙ} counts labeled structures

ALGORITHMIC BACKING:
-------------------
Native generating_functions engine (core/generating_functions.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Wilf, H. S. (2006). Generatingfunctionology, Chapter 3.
- Flajolet, P., & Sedgewick, R. (2009). Analytic Combinatorics, Part B.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.generating_functions import (
    ExponentialGF, derangement_count, stirling_numbers_via_egf
)

logger = logging.getLogger(__name__)


class ExponentialGFSpecialist(BDIAgent):
    """
    Exponential Generating Function Specialist - EGF & Labeled Structures

    DIRECTIVE:
    ---------
    Construct and manipulate exponential generating functions A(x) = Σ aₙxⁿ/n!.
    Specialized for labeled combinatorial structures.

    OPERATIONS:
    ----------
    - from_sequence: Build EGF from coefficient list [a₀, a₁, a₂, ...]
    - exp_function: e^x exponential function
    - derangements: Derangement number EGF
    - stirling_egf: Stirling numbers of 1st/2nd kind
    - evaluate_at: Evaluate A(x₀) at specific point

    FORMULATION:
    -----------
    EGF: A(x) = a₀ + a₁x/1! + a₂x²/2! + a₃x³/3! + ...

    Used for counting labeled structures where order matters.

    REFERENCE:
    ---------
    - Wilf (2006), Chapter 3: Cards, Decks, and Hands
    - Flajolet & Sedgewick (2009), Part B: Labelled Structures
    """

    def __init__(
        self,
        agent_id: str = 'exponential_gf_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Exponential GF Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.egf_constructed = 0
        self.derangements_computed = 0
        self.stirling_computed = 0
        self.exp_generated = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.discrete.gf.exponential',
            agent_id=self.agent_id,
            algorithm='exponential_gf_operations',
            cost='low',
            instance=self,
            tier='3',
            operations='from_sequence_exp_derangements_stirling'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.discrete.gf.exponential")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for EGF tasks."""
        if not self.blackboard:
            return

        try:
            # Query for EGF-related tasks
            egf_tasks = self.blackboard.query_entries(
                tags=['exponential_gf', 'egf', 'labeled', 'derangement'],
                status=EntryStatus.PENDING
            )

            for task in egf_tasks:
                belief_key = f'pending_egf_{task.entry_id}'

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
        """DELIBERATE: Create plans for pending EGF tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_egf_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'from_sequence')

            intention = Intention(
                plan_id=f'egf_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='solve_egf_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan for EGF task {task_id} ({operation})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the EGF computation plan."""
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
        operation = intention.metadata.get('operation', 'from_sequence')

        parsed_data = {
            'operation': operation,
            'sequence': metadata.get('sequence', metadata.get('coefficients', [])),
            'n_terms': metadata.get('n_terms', 10),
            'n': metadata.get('n', 5),
            'kind': metadata.get('kind', 2),  # Stirling: 1 or 2
            'x': metadata.get('x', 0.5)
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Perform EGF computation."""
        parsed_data = intention.metadata.get('parsed_data', {})
        operation = parsed_data['operation']

        try:
            if operation == 'from_sequence':
                sequence = parsed_data['sequence']
                egf = ExponentialGF(sequence)
                result = {
                    'coefficients': egf.coefficients.tolist(),
                    'length': len(egf),
                    'operation': 'from_sequence'
                }
                self.egf_constructed += 1

            elif operation == 'exp_function':
                n_terms = parsed_data['n_terms']
                egf = ExponentialGF.exp(n_terms)
                result = {
                    'coefficients': egf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'operation': 'exp_function',
                    'formula': 'e^x'
                }
                self.exp_generated += 1

            elif operation == 'derangements':
                n_terms = parsed_data['n_terms']
                egf = ExponentialGF.derangements(n_terms)
                result = {
                    'coefficients': egf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'operation': 'derangements',
                    'formula': 'e^(-x)/(1-x)'
                }
                self.derangements_computed += 1

            elif operation == 'derangement_count':
                n = parsed_data['n']
                count = derangement_count(n)
                result = {
                    'count': int(count),
                    'n': n,
                    'operation': 'derangement_count',
                    'formula': f'!{n}'
                }
                self.derangements_computed += 1

            elif operation == 'stirling_egf':
                n = parsed_data['n']
                kind = parsed_data['kind']
                numbers = stirling_numbers_via_egf(n, kind)
                result = {
                    'stirling_numbers': numbers,
                    'n': n,
                    'kind': kind,
                    'operation': 'stirling_egf',
                    'type': 'first_kind' if kind == 1 else 'second_kind'
                }
                self.stirling_computed += 1

            elif operation == 'evaluate_at':
                sequence = parsed_data['sequence']
                x = parsed_data['x']
                egf = ExponentialGF(sequence)
                value = egf.evaluate(x)
                result = {
                    'value': float(value),
                    'x': x,
                    'operation': 'evaluate_at'
                }

            else:
                raise ValueError(f"Unknown EGF operation: {operation}")

            result['method'] = 'exponential_gf'
            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"EGF computation failed: {e}")

    def _execute_verify(self, intention: Intention):
        """Verify result validity."""
        result = intention.metadata.get('result', {})

        if 'coefficients' in result:
            coeffs = result['coefficients']
            if not isinstance(coeffs, list):
                raise ValueError("Coefficients must be a list")
            if len(coeffs) == 0:
                raise ValueError("Empty coefficient list")

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
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'egf',
                tags=['exponential_gf', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_egf_{task_id}')
        self.add_belief(f'completed_{task_id}', result)

        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"EGF computation failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'exponential_gf', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        self.remove_belief(f'pending_egf_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Synchronous API for EGF operations.

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Result dictionary with EGF coefficients and operation details
        """
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'from_sequence')

        try:
            if operation == 'from_sequence':
                sequence = metadata.get('sequence', metadata.get('coefficients', []))
                egf = ExponentialGF(sequence)
                result = {
                    'coefficients': egf.coefficients.tolist(),
                    'length': len(egf),
                    'method': 'exponential_gf'
                }
                self.egf_constructed += 1

            elif operation == 'derangements':
                n_terms = metadata.get('n_terms', 10)
                egf = ExponentialGF.derangements(n_terms)
                result = {
                    'coefficients': egf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'method': 'derangements_egf'
                }
                self.derangements_computed += 1

            elif operation == 'exp_function':
                n_terms = metadata.get('n_terms', 10)
                egf = ExponentialGF.exp(n_terms)
                result = {
                    'coefficients': egf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'method': 'exp_egf'
                }
                self.exp_generated += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'exponential_gf'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'egf_constructed': self.egf_constructed,
            'derangements_computed': self.derangements_computed,
            'stirling_computed': self.stirling_computed,
            'exp_generated': self.exp_generated,
            'tier': '3',
            'type': 'specialist',
            'domain': 'generating_functions'
        })
        return stats


if __name__ == "__main__":
    """Test Exponential GF Specialist"""
    print("=" * 80)
    print("EXPONENTIAL GF SPECIALIST TEST")
    print("=" * 80)
    print()

    specialist = ExponentialGFSpecialist()
    print()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    # Test 1: Derangements
    print("Test 1: Derangement numbers, 6 terms")
    task1 = MockTask({'operation': 'derangements', 'n_terms': 6})
    result1 = specialist.process(task1)
    print(f"  Result: {result1['coefficients']}")
    print(f"  Expected: [1, 0, 1, 2, 9, 44]")
    print()

    # Test 2: Exponential function
    print("Test 2: e^x, 5 terms")
    task2 = MockTask({'operation': 'exp_function', 'n_terms': 5})
    result2 = specialist.process(task2)
    print(f"  Result: {result2['coefficients']}")
    print()

    # Statistics
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
