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
ORDINARY GENERATING FUNCTION SPECIALIST (Tier 3)
================================================

Handles ordinary generating function construction and manipulation.

CAPABILITIES:
------------
- from_sequence: Build OGF from coefficient list
- geometric_series: Generate 1/(1-rx) = 1 + rx + r²x² + ...
- from_rational: P(x)/Q(x) → coefficients via long division
- evaluate_at: Compute A(x₀) for specific x₀

FORMULATION:
-----------
A(x) = Σₙ aₙxⁿ where {aₙ} is a sequence

ALGORITHMIC BACKING:
-------------------
Native generating_functions engine (core/generating_functions.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Wilf, H. S. (2006). Generatingfunctionology.
- Flajolet, P., & Sedgewick, R. (2009). Analytic Combinatorics.
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
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
from symbo_agentic_reasoners.core.generating_functions import (
    OrdinaryGF, fibonacci_gf, catalan_gf
)

logger = logging.getLogger(__name__)


class OrdinaryGFSpecialist(BDIAgent):
    """
    Ordinary Generating Function Specialist - OGF Construction & Manipulation

    DIRECTIVE:
    ---------
    Construct and manipulate ordinary generating functions A(x) = Σ aₙxⁿ.

    OPERATIONS:
    ----------
    - from_sequence: Build OGF from coefficient list [a₀, a₁, a₂, ...]
    - geometric_series: 1/(1-rx) geometric series
    - from_rational: Rational GF P(x)/Q(x) expansion
    - evaluate_at: Evaluate A(x₀) at specific point
    - fibonacci_gf: Fibonacci generating function
    - catalan_gf: Catalan numbers generating function

    FORMULATION:
    -----------
    OGF: A(x) = a₀ + a₁x + a₂x² + a₃x³ + ...

    REFERENCE:
    ---------
    - Wilf (2006), Chapter 1: Getting Started
    - Flajolet & Sedgewick (2009), Part A
    """

    def __init__(
        self,
        agent_id: str = 'ordinary_gf_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Ordinary GF Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.ogf_constructed = 0
        self.geometric_series_generated = 0
        self.rational_expansions = 0
        self.evaluations = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.discrete.gf.ordinary',
            agent_id=self.agent_id,
            algorithm='ordinary_gf_operations',
            cost='low',
            instance=self,
            tier='3',
            operations='from_sequence_geometric_rational_evaluate'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.discrete.gf.ordinary")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for OGF tasks."""
        if not self.blackboard:
            return

        try:
            # Query for OGF-related tasks
            ogf_tasks = self.blackboard.query_entries(
                tags=['ordinary_gf', 'ogf', 'gf'],
                status=EntryStatus.PENDING
            )

            for task in ogf_tasks:
                belief_key = f'pending_ogf_{task.entry_id}'

                # Skip if already processed
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
        """DELIBERATE: Create plans for pending OGF tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_ogf_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if intention already exists
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Extract operation type
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'from_sequence')

            intention = Intention(
                plan_id=f'ogf_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='solve_ogf_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan for OGF task {task_id} ({operation})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the OGF computation plan."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        operation = intention.metadata.get('operation')

        logger.debug(f"[{self.agent_id}] Executing: {action} for task {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task_id)
            elif action == 'parse_input':
                self._execute_parse_input(intention, task)
            elif action == 'compute':
                self._execute_compute(intention, operation)
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

        # Extract parameters based on operation
        operation = intention.metadata.get('operation', 'from_sequence')

        parsed_data = {
            'operation': operation,
            'sequence': metadata.get('sequence', metadata.get('coefficients', [])),
            'n_terms': metadata.get('n_terms', 10),
            'r': metadata.get('r', 1),
            'numerator': metadata.get('numerator', [1]),
            'denominator': metadata.get('denominator', [1]),
            'x': metadata.get('x', 0.5)
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention, operation: str):
        """Perform OGF computation."""
        parsed_data = intention.metadata.get('parsed_data', {})

        try:
            if operation == 'from_sequence':
                sequence = parsed_data['sequence']
                ogf = OrdinaryGF(sequence)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'length': len(ogf),
                    'operation': 'from_sequence'
                }
                self.ogf_constructed += 1

            elif operation == 'geometric_series':
                r = parsed_data['r']
                n_terms = parsed_data['n_terms']
                ogf = OrdinaryGF.geometric(r, n_terms)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'r': r,
                    'n_terms': n_terms,
                    'operation': 'geometric_series',
                    'formula': f'1/(1-{r}x)'
                }
                self.geometric_series_generated += 1

            elif operation == 'from_rational':
                numerator = parsed_data['numerator']
                denominator = parsed_data['denominator']
                n_terms = parsed_data['n_terms']
                ogf = OrdinaryGF.from_rational(numerator, denominator, n_terms)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'numerator': numerator,
                    'denominator': denominator,
                    'n_terms': n_terms,
                    'operation': 'from_rational'
                }
                self.rational_expansions += 1

            elif operation == 'evaluate_at':
                sequence = parsed_data['sequence']
                x = parsed_data['x']
                ogf = OrdinaryGF(sequence)
                value = ogf.evaluate(x)
                result = {
                    'value': float(value),
                    'x': x,
                    'operation': 'evaluate_at'
                }
                self.evaluations += 1

            elif operation == 'fibonacci_gf':
                n_terms = parsed_data['n_terms']
                ogf = fibonacci_gf(n_terms)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'operation': 'fibonacci_gf',
                    'formula': 'x/(1-x-x²)'
                }
                self.rational_expansions += 1

            elif operation == 'catalan_gf':
                n_terms = parsed_data['n_terms']
                ogf = catalan_gf(n_terms)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'operation': 'catalan_gf',
                    'formula': '(1 - sqrt(1-4x))/(2x)'
                }
                self.rational_expansions += 1

            else:
                raise ValueError(f"Unknown OGF operation: {operation}")

            result['method'] = 'ordinary_gf'
            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"OGF computation failed: {e}")

    def _execute_verify(self, intention: Intention):
        """Verify result validity."""
        result = intention.metadata.get('result', {})

        # Basic verification - check coefficients are valid
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
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'ogf',
                tags=['ordinary_gf', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_ogf_{task_id}')
        self.add_belief(f'completed_{task_id}', result)

        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"OGF computation failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'ordinary_gf', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        self.remove_belief(f'pending_ogf_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Synchronous API for OGF operations.

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Result dictionary with OGF coefficients and operation details
        """
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'from_sequence')

        try:
            if operation == 'from_sequence':
                sequence = metadata.get('sequence', metadata.get('coefficients', []))
                ogf = OrdinaryGF(sequence)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'length': len(ogf),
                    'method': 'ordinary_gf'
                }
                self.ogf_constructed += 1

            elif operation == 'geometric_series':
                r = metadata.get('r', 1)
                n_terms = metadata.get('n_terms', 10)
                ogf = OrdinaryGF.geometric(r, n_terms)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'r': r,
                    'n_terms': n_terms,
                    'method': 'geometric_ogf'
                }
                self.geometric_series_generated += 1

            elif operation == 'from_rational':
                numerator = metadata.get('numerator', [1])
                denominator = metadata.get('denominator', [1])
                n_terms = metadata.get('n_terms', 10)
                ogf = OrdinaryGF.from_rational(numerator, denominator, n_terms)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'method': 'rational_ogf'
                }
                self.rational_expansions += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'ordinary_gf'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'ogf_constructed': self.ogf_constructed,
            'geometric_series_generated': self.geometric_series_generated,
            'rational_expansions': self.rational_expansions,
            'evaluations': self.evaluations,
            'tier': '3',
            'type': 'specialist',
            'domain': 'generating_functions'
        })
        return stats


if __name__ == "__main__":
    """Test Ordinary GF Specialist"""
    print("=" * 80)
    print("ORDINARY GF SPECIALIST TEST")
    print("=" * 80)
    print()

    # Create specialist
    specialist = OrdinaryGFSpecialist()
    print()

    # Test 1: From sequence
    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    print("Test 1: From sequence [1, 1, 2, 3, 5, 8]")
    task1 = MockTask({'operation': 'from_sequence', 'sequence': [1, 1, 2, 3, 5, 8]})
    result1 = specialist.process(task1)
    print(f"  Result: {result1}")
    print()

    # Test 2: Geometric series
    print("Test 2: Geometric series 1/(1-2x), 10 terms")
    task2 = MockTask({'operation': 'geometric_series', 'r': 2, 'n_terms': 10})
    result2 = specialist.process(task2)
    print(f"  Result: {result2['coefficients']}")
    print()

    # Test 3: Rational GF (Fibonacci)
    print("Test 3: Fibonacci GF x/(1-x-x²), 10 terms")
    task3 = MockTask({
        'operation': 'from_rational',
        'numerator': [0, 1],
        'denominator': [1, -1, -1],
        'n_terms': 10
    })
    result3 = specialist.process(task3)
    print(f"  Result: {result3['coefficients']}")
    print()

    # Statistics
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
