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
GF COMPOSITION SPECIALIST (Tier 3)
===================================

Handles generating function arithmetic and composition operations.

CAPABILITIES:
------------
- add: A(x) + B(x) coefficient-wise addition
- multiply: A(x) * B(x) convolution product
- hadamard: A(x) ⊙ B(x) term-by-term product
- derivative: A'(x) shift coefficients
- shift: x * A(x) prepend zero
- compose: A(B(x)) composition

FORMULATION:
-----------
Addition: (A+B)[n] = A[n] + B[n]
Convolution: (A*B)[n] = Σₖ A[k]·B[n-k]
Hadamard: (A⊙B)[n] = A[n]·B[n]

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
    GeneratingFunction, OrdinaryGF, convolve, hadamard_product
)

logger = logging.getLogger(__name__)


class GFCompositionSpecialist(BDIAgent):
    """
    GF Composition Specialist - GF Arithmetic Operations

    DIRECTIVE:
    ---------
    Perform arithmetic operations on generating functions.

    OPERATIONS:
    ----------
    - add_gfs: A(x) + B(x) coefficient addition
    - multiply_gfs: A(x) * B(x) convolution
    - hadamard: A(x) ⊙ B(x) term-by-term product
    - derivative: Compute A'(x)
    - shift: Compute x·A(x)
    - scalar_multiply: c·A(x)

    FORMULATION:
    -----------
    Addition: (A+B)(x) = Σ (aₙ+bₙ)xⁿ
    Multiplication: (A*B)(x) = Σ (Σₖ aₖbₙ₋ₖ)xⁿ
    Hadamard: (A⊙B)(x) = Σ aₙbₙxⁿ

    REFERENCE:
    ---------
    - Wilf (2006), Chapter 2: Operations on GFs
    """

    def __init__(
        self,
        agent_id: str = 'gf_composition_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize GF Composition Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.additions = 0
        self.multiplications = 0
        self.hadamard_products = 0
        self.derivatives = 0
        self.shifts = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.discrete.gf.composition',
            agent_id=self.agent_id,
            algorithm='gf_arithmetic',
            cost='low',
            instance=self,
            tier='3',
            operations='add_multiply_hadamard_derivative_shift'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.discrete.gf.composition")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for GF composition tasks."""
        if not self.blackboard:
            return

        try:
            composition_tasks = self.blackboard.query_entries(
                tags=['gf_composition', 'gf_operations', 'convolution'],
                status=EntryStatus.PENDING
            )

            for task in composition_tasks:
                belief_key = f'pending_comp_{task.entry_id}'

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
        """DELIBERATE: Create plans for pending composition tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_comp_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'add_gfs')

            intention = Intention(
                plan_id=f'comp_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='compose_gfs',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan for composition task {task_id} ({operation})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the GF composition plan."""
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
            'operation': intention.metadata.get('operation', 'add_gfs'),
            'gf_a': metadata.get('gf_a', [1]),
            'gf_b': metadata.get('gf_b', [1]),
            'scalar': metadata.get('scalar', 2)
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Perform GF composition operation."""
        parsed_data = intention.metadata.get('parsed_data', {})
        operation = parsed_data['operation']

        try:
            gf_a_coeffs = parsed_data['gf_a']
            gf_b_coeffs = parsed_data.get('gf_b', [])

            if operation == 'add_gfs':
                gf_a = OrdinaryGF(gf_a_coeffs)
                gf_b = OrdinaryGF(gf_b_coeffs)
                result_gf = gf_a + gf_b

                result = {
                    'coefficients': result_gf.coefficients.tolist(),
                    'operation': 'add',
                    'formula': 'A(x) + B(x)'
                }
                self.additions += 1

            elif operation == 'multiply_gfs':
                gf_a = OrdinaryGF(gf_a_coeffs)
                gf_b = OrdinaryGF(gf_b_coeffs)
                result_gf = gf_a * gf_b

                result = {
                    'coefficients': result_gf.coefficients.tolist(),
                    'operation': 'multiply',
                    'formula': 'A(x) * B(x)'
                }
                self.multiplications += 1

            elif operation == 'hadamard':
                hadamard_coeffs = hadamard_product(gf_a_coeffs, gf_b_coeffs)

                result = {
                    'coefficients': hadamard_coeffs,
                    'operation': 'hadamard',
                    'formula': 'A(x) ⊙ B(x)'
                }
                self.hadamard_products += 1

            elif operation == 'convolve':
                convolved = convolve(gf_a_coeffs, gf_b_coeffs)

                result = {
                    'coefficients': convolved,
                    'operation': 'convolve',
                    'formula': 'conv(A, B)'
                }
                self.multiplications += 1

            elif operation == 'derivative':
                # A'(x): shift coefficients and multiply by index
                derivative_coeffs = [i * gf_a_coeffs[i] for i in range(1, len(gf_a_coeffs))]

                result = {
                    'coefficients': derivative_coeffs,
                    'operation': 'derivative',
                    'formula': "A'(x)"
                }
                self.derivatives += 1

            elif operation == 'shift':
                # x*A(x): prepend zero
                shifted = [0] + gf_a_coeffs

                result = {
                    'coefficients': shifted,
                    'operation': 'shift',
                    'formula': 'x·A(x)'
                }
                self.shifts += 1

            elif operation == 'scalar_multiply':
                scalar = parsed_data['scalar']
                scaled = [scalar * c for c in gf_a_coeffs]

                result = {
                    'coefficients': scaled,
                    'scalar': scalar,
                    'operation': 'scalar_multiply',
                    'formula': f'{scalar}·A(x)'
                }

            else:
                raise ValueError(f"Unknown composition operation: {operation}")

            result['method'] = 'gf_composition'
            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"GF composition failed: {e}")

    def _execute_verify(self, intention: Intention):
        """Verify result validity."""
        result = intention.metadata.get('result', {})

        if 'coefficients' in result:
            if not isinstance(result['coefficients'], list):
                raise ValueError("Coefficients must be a list")

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
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'composition',
                tags=['gf_composition', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_comp_{task_id}')
        self.add_belief(f'completed_{task_id}', result)

        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"GF composition failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'gf_composition', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        self.remove_belief(f'pending_comp_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Synchronous API for GF composition operations.

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Result dictionary with composed GF coefficients
        """
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'add_gfs')

        try:
            gf_a = metadata.get('gf_a', [1])
            gf_b = metadata.get('gf_b', [1])

            if operation == 'add_gfs':
                gf_a_obj = OrdinaryGF(gf_a)
                gf_b_obj = OrdinaryGF(gf_b)
                result_gf = gf_a_obj + gf_b_obj

                result = {
                    'coefficients': result_gf.coefficients.tolist(),
                    'method': 'gf_add'
                }
                self.additions += 1

            elif operation == 'multiply_gfs':
                gf_a_obj = OrdinaryGF(gf_a)
                gf_b_obj = OrdinaryGF(gf_b)
                result_gf = gf_a_obj * gf_b_obj

                result = {
                    'coefficients': result_gf.coefficients.tolist(),
                    'method': 'gf_multiply'
                }
                self.multiplications += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'gf_composition'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'additions': self.additions,
            'multiplications': self.multiplications,
            'hadamard_products': self.hadamard_products,
            'derivatives': self.derivatives,
            'shifts': self.shifts,
            'tier': '3',
            'type': 'specialist',
            'domain': 'generating_functions'
        })
        return stats


if __name__ == "__main__":
    """Test GF Composition Specialist"""
    print("=" * 80)
    print("GF COMPOSITION SPECIALIST TEST")
    print("=" * 80)
    print()

    specialist = GFCompositionSpecialist()
    print()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    # Test 1: Addition
    print("Test 1: (1+x) + (1+x²) = 1 + x + x²")
    task1 = MockTask({'operation': 'add_gfs', 'gf_a': [1, 1], 'gf_b': [1, 0, 1]})
    result1 = specialist.process(task1)
    print(f"  Result: {result1['coefficients']}")
    print()

    # Test 2: Multiplication
    print("Test 2: (1+x) * (1+x²) = 1 + x + x² + x³")
    task2 = MockTask({'operation': 'multiply_gfs', 'gf_a': [1, 1], 'gf_b': [1, 0, 1]})
    result2 = specialist.process(task2)
    print(f"  Result: {result2['coefficients']}")
    print()

    # Statistics
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
