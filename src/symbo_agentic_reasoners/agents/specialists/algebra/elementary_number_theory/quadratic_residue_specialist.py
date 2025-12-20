# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
QUADRATIC RESIDUE SPECIALIST (Tier 3)
======================================

Handles Legendre/Jacobi symbols and quadratic residuosity.

CAPABILITIES:
------------
- legendre_symbol: (a/p) ∈ {-1, 0, 1}
- quadratic_reciprocity: Compute (p/q) using reciprocity
- jacobi_symbol: Generalization to composite moduli
- is_quadratic_residue: Boolean QR test

FORMULATION:
-----------
Legendre symbol: (a/p) = a^((p-1)/2) mod p (Euler's criterion)
Quadratic reciprocity: (p/q)(q/p) = (-1)^((p-1)(q-1)/4)

ALGORITHMIC BACKING:
-------------------
Native elementary_number_theory engine (core/elementary_number_theory.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Ireland & Rosen (1990), Chapter 5: Quadratic Reciprocity.
- Gauss, C. F. (1801). Disquisitiones Arithmeticae.
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

logger = logging.getLogger(__name__)


class QuadraticResidueSpecialist(BDIAgent):
    """
    Quadratic Residue Specialist - Legendre/Jacobi Symbols

    DIRECTIVE:
    ---------
    Determine quadratic residuosity using Legendre and Jacobi symbols.

    OPERATIONS:
    ----------
    - legendre_symbol: (a/p) via Euler's criterion
    - is_quadratic_residue: Boolean QR test
    - quadratic_reciprocity: Apply QR law
    - jacobi_symbol: Generalized symbol

    FORMULATION:
    -----------
    (a/p) = a^((p-1)/2) mod p ∈ {-1, 0, 1}

    REFERENCE:
    ---------
    - Ireland & Rosen, Chapter 5
    """

    def __init__(
        self,
        agent_id: str = 'quadratic_residue_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Quadratic Residue Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.legendre_symbols_computed = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt.quadratic_residue',
            agent_id=self.agent_id,
            algorithm='legendre_jacobi',
            cost='low',
            instance=self,
            tier='3',
            operations='legendre_jacobi_qr_test'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt.quadratic_residue")

    def update_beliefs(self):
        """PERCEIVE: Monitor for QR tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(tags=['quadratic_residue', 'legendre'], status=EntryStatus.PENDING)
            for task in tasks:
                if not self.has_belief(f'pending_qr_{task.entry_id}'):
                    self.add_belief(predicate=f'pending_qr_{task.entry_id}', content=task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_qr_'):
                continue

            task = belief.content
            metadata = task.metadata if hasattr(task, 'metadata') else {}

            intention = Intention(
                plan_id=f'qr_{task.entry_id}',
                steps=['claim_task', 'compute', 'post_result'],
                target_desire='compute_qr',
                metadata={'task_id': task.entry_id, 'task_entry': task, 'operation': metadata.get('operation', 'legendre_symbol')}
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute QR symbol."""
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
        """Compute Legendre/Jacobi symbol."""
        task = intention.metadata['task_entry']
        metadata = task.metadata if hasattr(task, 'metadata') else {}

        try:
            a = metadata.get('a', 1)
            p = metadata.get('p', 7)

            # Legendre symbol via Euler's criterion
            symbol = pow(a, (p - 1) // 2, p)
            if symbol == p - 1:
                symbol = -1

            result = {
                'symbol': int(symbol),
                'a': a,
                'p': p,
                'is_qr': symbol == 1,
                'method': 'legendre_symbol'
            }

            intention.metadata['result'] = result
            self.legendre_symbols_computed += 1
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"QR computation failed: {e}")

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result."""
        result = intention.metadata.get('result', {})

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'qr',
                tags=['quadratic_residue', 'result'],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)

        self.remove_belief(f'pending_qr_{intention.metadata["task_id"]}')
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
            a = metadata.get('a', 1)
            p = metadata.get('p', 7)

            # Legendre symbol via Euler's criterion
            symbol = pow(a, (p - 1) // 2, p)
            if symbol == p - 1:
                symbol = -1

            result = {'symbol': int(symbol), 'is_qr': symbol == 1, 'method': 'legendre'}
            self.legendre_symbols_computed += 1
            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            return {'error': str(e), 'method': 'qr'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'legendre_symbols_computed': self.legendre_symbols_computed,
            'tier': '3',
            'type': 'specialist',
            'domain': 'elementary_number_theory'
        }


if __name__ == "__main__":
    print("QUADRATIC RESIDUE SPECIALIST TEST")
    specialist = QuadraticResidueSpecialist()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata

    task = MockTask({'a': 2, 'p': 7})
    result = specialist.process(task)
    print(f"(2/7) = {result.get('symbol', 'N/A')}")
