# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
LIFTING THE EXPONENT SPECIALIST (Tier 3)
=========================================

Handles LTE lemma and p-adic valuations.

CAPABILITIES:
------------
- p_adic_valuation: v_p(n) = max k: p^k | n
- lte_valuation: v_p(a^n - b^n) for odd p
- lte_p_equals_2: Special case p=2
- valuation_product: v_p(ab) = v_p(a) + v_p(b)

FORMULATION:
-----------
LTE (odd p): If p | (a-b), p ∤ a, p ∤ b, then
v_p(a^n - b^n) = v_p(a - b) + v_p(n)

ALGORITHMIC BACKING:
-------------------
Native elementary_number_theory engine (core/elementary_number_theory.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Amir, A. (2011). Lifting the Exponent Lemma.
- Niven et al. (1991), Chapter 2.
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
from symbo_agentic_reasoners.core.elementary_number_theory import (
    p_adic_valuation, lte_valuation
)

logger = logging.getLogger(__name__)


class LiftingTheExponentSpecialist(BDIAgent):
    """
    Lifting the Exponent Specialist - LTE Lemma & p-adic Valuations

    DIRECTIVE:
    ---------
    Compute p-adic valuations and apply LTE lemma.

    OPERATIONS:
    ----------
    - p_adic_valuation: v_p(n)
    - lte_valuation: v_p(a^n - b^n)
    - verify_lte_conditions: Check LTE applicability

    FORMULATION:
    -----------
    v_p(n) = max{k : p^k | n}

    LTE: v_p(a^n - b^n) = v_p(a - b) + v_p(n) when p | (a-b)

    REFERENCE:
    ---------
    - LTE lemma for olympiad problems
    """

    def __init__(
        self,
        agent_id: str = 'lte_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize LTE Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.valuations_computed = 0
        self.lte_applications = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt.lte',
            agent_id=self.agent_id,
            algorithm='lte_lemma',
            cost='low',
            instance=self,
            tier='3',
            operations='valuation_lte'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt.lte")

    def update_beliefs(self):
        """PERCEIVE: Monitor for LTE tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(tags=['lte', 'valuation', 'p_adic'], status=EntryStatus.PENDING)
            for task in tasks:
                if not self.has_belief(f'pending_lte_{task.entry_id}'):
                    self.add_belief(predicate=f'pending_lte_{task.entry_id}', content=task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_lte_'):
                continue

            task = belief.content
            metadata = task.metadata if hasattr(task, 'metadata') else {}

            intention = Intention(
                plan_id=f'lte_{task.entry_id}',
                steps=['claim_task', 'compute', 'post_result'],
                target_desire='compute_valuation',
                metadata={'task_id': task.entry_id, 'task_entry': task, 'operation': metadata.get('operation', 'p_adic_valuation')}
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute valuation."""
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
        """Compute valuation or LTE."""
        task = intention.metadata['task_entry']
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = intention.metadata.get('operation', 'p_adic_valuation')

        try:
            if operation == 'p_adic_valuation':
                n = metadata.get('n', 1)
                p = metadata.get('p', 2)

                val = p_adic_valuation(n, p)

                result = {'valuation': val, 'n': n, 'p': p, 'method': 'p_adic_valuation'}
                self.valuations_computed += 1

            elif operation == 'lte_valuation':
                a = metadata.get('a', 1)
                b = metadata.get('b', 1)
                n = metadata.get('n', 1)
                p = metadata.get('p', 2)

                val = lte_valuation(a, b, n, p)

                result = {'valuation': val, 'a': a, 'b': b, 'n': n, 'p': p, 'method': 'lte'}
                self.lte_applications += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"LTE computation failed: {e}")

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result."""
        result = intention.metadata.get('result', {})

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'lte',
                tags=['lte', 'result'],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)

        self.remove_belief(f'pending_lte_{intention.metadata["task_id"]}')
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
        operation = metadata.get('operation', 'p_adic_valuation')

        try:
            if operation == 'p_adic_valuation':
                n = metadata.get('n', 1)
                p = metadata.get('p', 2)
                val = p_adic_valuation(n, p)

                result = {'valuation': val, 'method': 'p_adic_valuation'}
                self.valuations_computed += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            return {'error': str(e), 'method': 'lte'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'valuations_computed': self.valuations_computed,
            'lte_applications': self.lte_applications,
            'tier': '3',
            'type': 'specialist',
            'domain': 'elementary_number_theory'
        }


if __name__ == "__main__":
    print("LTE SPECIALIST TEST")
    specialist = LiftingTheExponentSpecialist()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata

    task = MockTask({'operation': 'p_adic_valuation', 'n': 24, 'p': 2})
    result = specialist.process(task)
    print(f"v_2(24) = {result.get('valuation', 'N/A')}")
