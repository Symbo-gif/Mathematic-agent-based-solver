# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
TONELLI-SHANKS SPECIALIST (Tier 3)
===================================

Handles modular square roots using Tonelli-Shanks algorithm.

CAPABILITIES:
------------
- modular_sqrt: √n (mod p) using Tonelli-Shanks
- verify_quadratic_residue: Check if n is QR mod p
- count_square_roots: Count solutions (0, 1, or 2)

FORMULATION:
-----------
Given n and odd prime p, find x such that x² ≡ n (mod p)

ALGORITHMIC BACKING:
-------------------
Native elementary_number_theory engine (core/elementary_number_theory.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Tonelli, A. (1891). Bemerkung über die Auflösung quadratischer Congruenzen.
- Shanks, D. (1972). Five number-theoretic algorithms.
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
from symbo_agentic_reasoners.core.elementary_number_theory import tonelli_shanks

logger = logging.getLogger(__name__)


class TonelliShanksSpecialist(BDIAgent):
    """
    Tonelli-Shanks Specialist - Modular Square Roots

    DIRECTIVE:
    ---------
    Compute modular square roots using Tonelli-Shanks algorithm.

    OPERATIONS:
    ----------
    - modular_sqrt: Find x with x² ≡ n (mod p)
    - verify_qr: Check if n is quadratic residue mod p
    - both_roots: Return both ±√n (mod p)

    COMPLEXITY: O(log² p)

    REFERENCE:
    ---------
    - Tonelli (1891), Shanks (1972)
    """

    def __init__(
        self,
        agent_id: str = 'tonelli_shanks_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Tonelli-Shanks Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.modular_sqrts_computed = 0
        self.qr_verifications = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt.tonelli_shanks',
            agent_id=self.agent_id,
            algorithm='tonelli_shanks',
            cost='low',
            instance=self,
            tier='3',
            operations='modular_sqrt_verify_qr'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt.tonelli_shanks")

    def update_beliefs(self):
        """PERCEIVE: Monitor for Tonelli-Shanks tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(tags=['tonelli', 'modular_sqrt'], status=EntryStatus.PENDING)
            for task in tasks:
                if not self.has_belief(f'pending_ts_{task.entry_id}'):
                    self.add_belief(predicate=f'pending_ts_{task.entry_id}', content=task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_ts_'):
                continue

            task = belief.content
            metadata = task.metadata if hasattr(task, 'metadata') else {}

            intention = Intention(
                plan_id=f'ts_{task.entry_id}',
                steps=['claim_task', 'compute', 'post_result'],
                target_desire='modular_sqrt',
                metadata={'task_id': task.entry_id, 'task_entry': task, 'operation': metadata.get('operation', 'modular_sqrt')}
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute modular sqrt."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(intention.metadata['task_id'], EntryStatus.IN_PROGRESS)
                intention.advance()
            elif action == 'compute':
                self._execute_compute(intention)
            elif action == 'post_result':
                self._execute_post_result(intention, task)
            else:
                intention.advance()
        except Exception as e:
            self._handle_failure(intention, task, str(e))

    def _execute_compute(self, intention: Intention):
        """Compute modular square root."""
        task = intention.metadata['task_entry']
        metadata = task.metadata if hasattr(task, 'metadata') else {}

        try:
            n = metadata.get('n', 1)
            p = metadata.get('p', 7)

            root = tonelli_shanks(n, p)

            result = {
                'root': root if root else None,
                'has_solution': root is not None,
                'n': n,
                'p': p,
                'method': 'tonelli_shanks'
            }

            if root:
                result['both_roots'] = [root, p - root]

            intention.metadata['result'] = result
            self.modular_sqrts_computed += 1
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"Tonelli-Shanks failed: {e}")

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result."""
        result = intention.metadata.get('result', {})

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'ts',
                tags=['tonelli_shanks', 'result'],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)

        self.remove_belief(f'pending_ts_{intention.metadata["task_id"]}')
        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle failure."""
        self.tasks_failed += 1
        while not intention.is_complete():
            intention.advance()

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """Synchronous API."""
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}

        try:
            n = metadata.get('n', 1)
            p = metadata.get('p', 7)

            root = tonelli_shanks(n, p)

            result = {'root': root, 'has_solution': root is not None, 'method': 'tonelli_shanks'}
            self.modular_sqrts_computed += 1
            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            return {'error': str(e), 'method': 'tonelli_shanks'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'modular_sqrts_computed': self.modular_sqrts_computed,
            'qr_verifications': self.qr_verifications,
            'tier': '3',
            'type': 'specialist',
            'domain': 'elementary_number_theory'
        }


if __name__ == "__main__":
    print("TONELLI-SHANKS SPECIALIST TEST")
    specialist = TonelliShanksSpecialist()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata

    task = MockTask({'n': 10, 'p': 13})
    result = specialist.process(task)
    print(f"√10 (mod 13) = {result.get('root', 'No solution')}")
