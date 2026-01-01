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
CAUCHY-SCHWARZ SPECIALIST (Tier 3)
==================================

Verifies and applies the Cauchy-Schwarz inequality.

CAPABILITIES:
------------
- Discrete form: (∑aᵢbᵢ)² ≤ (∑aᵢ²)(∑bᵢ²)
- Integral form: (∫fg)² ≤ (∫f²)(∫g²)
- Matrix form: (x^T y)² ≤ (x^T x)(y^T y)
- Equality condition detection: a = λb
- High-dimensional verification

ALGORITHMIC BACKING:
-------------------
Native inequalities engine (core/inequalities.py)

NO SYMPY - Pure native mathematical reasoning.
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
from symbo_agentic_reasoners.core.inequalities import (
    cauchy_schwarz_discrete, cauchy_schwarz_integral
)

logger = logging.getLogger(__name__)


class CauchySchwarzSpecialist(BDIAgent):
    """
    Cauchy-Schwarz Inequality Specialist - Inner Product Inequalities

    DIRECTIVE:
    ---------
    Verify and apply Cauchy-Schwarz inequality in discrete and integral forms.

    OPERATIONS:
    ----------
    - verify_discrete: Verify discrete CS inequality
    - verify_integral: Verify integral CS inequality (numerical)
    - check_equality: Test for equality condition
    - compute_ratio: Compute left_side / right_side

    INEQUALITY:
    ----------
    (∑aᵢbᵢ)² ≤ (∑aᵢ²)(∑bᵢ²)

    Equality holds iff a = λb (proportional vectors)

    REFERENCE:
    ---------
    - Cauchy, A.-L. (1821). Cours d'analyse.
    - Schwarz, H. A. (1885). Über ein die Flächen kleinsten Flächeninhalts.
    - Steele, J. M. (2004). The Cauchy-Schwarz Master Class.
    """

    def __init__(
        self,
        agent_id: str = 'cauchy_schwarz_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Cauchy-Schwarz Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.inequalities_verified = 0
        self.equality_cases_detected = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Cauchy-Schwarz Specialist initialized")

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.inequalities.cauchy_schwarz',
            agent_id=self.agent_id,
            algorithm='native_cs_inequality',
            cost='low',
            instance=self,
            tier='3',
            operations='verify_discrete_verify_integral_equality_test'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.inequalities.cauchy_schwarz")

    # ======================================================================
    # BDI IMPLEMENTATION
    # ======================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for Cauchy-Schwarz tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus

            tasks = self.blackboard.query_entries(
                tags=['cauchy_schwarz'],
                status=EntryStatus.PENDING
            )
            tasks += self.blackboard.query_entries(
                tags=['cauchy'],
                status=EntryStatus.PENDING
            )
            tasks += self.blackboard.query_entries(
                tags=['cs_inequality'],
                status=EntryStatus.PENDING
            )

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create verification plans for Cauchy-Schwarz tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if already have intention
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Extract operation
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'verify_discrete')

            # Build step sequence
            steps = [
                'claim_task',
                'parse_vectors',
                'verify_inequality',
                'check_equality_condition',
                'post_result'
            ]

            intention = Intention(
                plan_id=f'cs_verify_{task_id}',
                steps=steps,
                target_desire='verify_cauchy_schwarz',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the verification plan."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task, task_id)
            elif action == 'parse_vectors':
                self._execute_parse_vectors(intention)
            elif action == 'verify_inequality':
                self._execute_verify_inequality(intention)
            elif action == 'check_equality_condition':
                self._execute_check_equality(intention)
            elif action == 'post_result':
                self._execute_post_result(intention, task)
        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_failure(intention, task, str(e))

    # ======================================================================
    # EXECUTION HELPERS
    # ======================================================================

    def _execute_claim_task(self, intention: Intention, task: Any, task_id: str):
        """Claim task on Blackboard."""
        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
        self.add_belief(f'claimed_task_{task_id}', True)
        intention.advance()

    def _execute_parse_vectors(self, intention: Intention):
        """Parse vector inputs from task."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}

        # Extract vectors a and b
        a = metadata.get('vector_a', metadata.get('a', []))
        b = metadata.get('vector_b', metadata.get('b', []))

        # Convert to numpy arrays
        try:
            a = np.array(a, dtype=float)
            b = np.array(b, dtype=float)
        except Exception as e:
            logger.error(f"[{self.agent_id}] Failed to parse vectors: {e}")
            intention.metadata['parse_error'] = str(e)
            intention.advance()
            return

        intention.metadata['vector_a'] = a
        intention.metadata['vector_b'] = b
        intention.advance()

    def _execute_verify_inequality(self, intention: Intention):
        """Verify Cauchy-Schwarz inequality."""
        a = intention.metadata.get('vector_a')
        b = intention.metadata.get('vector_b')
        operation = intention.metadata.get('operation', 'verify_discrete')

        if a is None or b is None:
            intention.metadata['result'] = {'error': 'Missing vectors'}
            intention.advance()
            return

        try:
            if operation in ['verify_discrete', 'default']:
                result = cauchy_schwarz_discrete(a, b)
            elif operation == 'verify_integral':
                # Use integral form with dx=1.0 for discretely sampled functions
                result = cauchy_schwarz_integral(a, b, dx=1.0)
            else:
                result = cauchy_schwarz_discrete(a, b)  # Default

            intention.metadata['result'] = result
            self.inequalities_verified += 1

        except Exception as e:
            logger.error(f"[{self.agent_id}] Verification failed: {e}")
            intention.metadata['result'] = {'error': str(e)}

        intention.advance()

    def _execute_check_equality(self, intention: Intention):
        """Check for equality condition."""
        result = intention.metadata.get('result', {})

        if 'equality_holds' in result and result['equality_holds']:
            self.equality_cases_detected += 1
            intention.metadata['equality_detected'] = True
        else:
            intention.metadata['equality_detected'] = False

        intention.advance()

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post verification result to Blackboard."""
        result = intention.metadata.get('result', {})
        task_id = intention.metadata.get('task_id')

        if self.blackboard and 'error' not in result:
            result_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(str(result)),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'default',
                tags=['cauchy_schwarz', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata={
                    'result': result,
                    'task_id': task_id,
                    'inequality_holds': result.get('inequality_holds', False),
                    'equality_holds': result.get('equality_holds', False)
                }
            )
            self.blackboard.post(result_entry)
            self.tasks_succeeded += 1
        else:
            self.tasks_failed += 1

        self.tasks_executed += 1
        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle task failure."""
        task_id = intention.metadata.get('task_id')
        self.tasks_failed += 1
        self.tasks_executed += 1

        if self.blackboard:
            error_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(f"Error: {error_msg}"),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'default',
                tags=['cauchy_schwarz', 'error', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)

        # Mark intention complete
        while not intention.is_complete():
            intention.advance()

    # ======================================================================
    # PUBLIC API
    # ======================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Process Cauchy-Schwarz verification task (synchronous API).

        Args:
            task_entry: Task with metadata containing vector_a and vector_b

        Returns:
            Verification result dictionary

        Example:
            >>> task = create_entry(
            ...     entry_type=EntryType.TASK,
            ...     content="Verify CS inequality",
            ...     metadata={'vector_a': [1, 2, 3], 'vector_b': [4, 5, 6]}
            ... )
            >>> result = specialist.process(task)
            >>> result['inequality_holds']
            True
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}

        a = metadata.get('vector_a', metadata.get('a', []))
        b = metadata.get('vector_b', metadata.get('b', []))
        operation = metadata.get('operation', 'verify_discrete')

        try:
            a = np.array(a, dtype=float)
            b = np.array(b, dtype=float)

            if operation == 'verify_integral':
                result = cauchy_schwarz_integral(a, b, dx=metadata.get('dx', 1.0))
            else:
                result = cauchy_schwarz_discrete(a, b)

            self.tasks_executed += 1
            self.tasks_succeeded += 1
            self.inequalities_verified += 1

            if result.get('equality_holds', False):
                self.equality_cases_detected += 1

            return result

        except Exception as e:
            logger.error(f"[{self.agent_id}] Processing error: {e}")
            self.tasks_executed += 1
            self.tasks_failed += 1
            return {'error': str(e), 'inequality_holds': None}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'inequalities_verified': self.inequalities_verified,
            'equality_cases_detected': self.equality_cases_detected,
            'tier': '3',
            'type': 'specialist',
            'domain': 'inequalities'
        }
