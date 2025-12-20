# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
DIOPHANTINE EQUATION SPECIALIST (Tier 3)
=========================================

Handles basic linear Diophantine equations and Pythagorean triples.

CAPABILITIES:
------------
- solve_linear_diophantine: ax + by = c
- pythagorean_triples: Generate a² + b² = c²
- verify_solution: Check if (x,y) satisfies equation
- parametric_solutions: General solution x = x₀ + kt

FORMULATION:
-----------
Linear Diophantine: ax + by = c
Solution exists iff gcd(a, b) | c
General solution: x = x₀ + (b/d)t, y = y₀ - (a/d)t where d = gcd(a,b)

ALGORITHMIC BACKING:
-------------------
Native elementary_number_theory engine (core/elementary_number_theory.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Niven et al. (1991), Chapter 2: Diophantine Equations.
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
    solve_linear_diophantine, pythagorean_triples
)

logger = logging.getLogger(__name__)


class DiophantineBasicSpecialist(BDIAgent):
    """
    Diophantine Equation Specialist - Linear Equations & Pythagorean Triples

    DIRECTIVE:
    ---------
    Solve basic Diophantine equations over integers.

    OPERATIONS:
    ----------
    - solve_linear: ax + by = c
    - pythagorean_triples: Generate a² + b² = c²
    - verify_solution: Check integer solution
    - parametric: General solution family

    FORMULATION:
    -----------
    Linear: ax + by = c has solutions iff gcd(a,b) | c

    REFERENCE:
    ---------
    - Niven et al., Chapter 2
    """

    def __init__(
        self,
        agent_id: str = 'diophantine_basic_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Diophantine Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.linear_diophantine_solved = 0
        self.pythagorean_triples_generated = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt.diophantine',
            agent_id=self.agent_id,
            algorithm='diophantine_solver',
            cost='low',
            instance=self,
            tier='3',
            operations='linear_pythagorean_verify'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt.diophantine")

    def update_beliefs(self):
        """PERCEIVE: Monitor for Diophantine tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(tags=['diophantine', 'integer_equation'], status=EntryStatus.PENDING)
            for task in tasks:
                if not self.has_belief(f'pending_dioph_{task.entry_id}'):
                    self.add_belief(predicate=f'pending_dioph_{task.entry_id}', content=task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_dioph_'):
                continue

            task = belief.content
            metadata = task.metadata if hasattr(task, 'metadata') else {}

            intention = Intention(
                plan_id=f'dioph_{task.entry_id}',
                steps=['claim_task', 'compute', 'post_result'],
                target_desire='solve_diophantine',
                metadata={'task_id': task.entry_id, 'task_entry': task, 'operation': metadata.get('operation', 'solve_linear')}
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Solve Diophantine equation."""
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
        """Compute Diophantine solution."""
        task = intention.metadata['task_entry']
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = intention.metadata.get('operation', 'solve_linear')

        try:
            if operation == 'solve_linear':
                a = metadata.get('a', 1)
                b = metadata.get('b', 1)
                c = metadata.get('c', 1)

                solution = solve_linear_diophantine(a, b, c)

                result = {
                    'solution': solution,
                    'has_solution': solution is not None,
                    'a': a, 'b': b, 'c': c,
                    'method': 'linear_diophantine'
                }
                self.linear_diophantine_solved += 1

            elif operation == 'pythagorean_triples':
                limit = metadata.get('limit', 100)

                triples = pythagorean_triples(limit)

                result = {
                    'triples': triples,
                    'count': len(triples),
                    'limit': limit,
                    'method': 'pythagorean_triples'
                }
                self.pythagorean_triples_generated += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"Diophantine solving failed: {e}")

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result."""
        result = intention.metadata.get('result', {})

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'dioph',
                tags=['diophantine', 'result'],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)

        self.remove_belief(f'pending_dioph_{intention.metadata["task_id"]}')
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
        operation = metadata.get('operation', 'solve_linear')

        try:
            if operation == 'solve_linear':
                a = metadata.get('a', 1)
                b = metadata.get('b', 1)
                c = metadata.get('c', 1)

                solution = solve_linear_diophantine(a, b, c)

                result = {'solution': solution, 'has_solution': solution is not None, 'method': 'diophantine'}
                self.linear_diophantine_solved += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            return {'error': str(e), 'method': 'diophantine'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'linear_diophantine_solved': self.linear_diophantine_solved,
            'pythagorean_triples_generated': self.pythagorean_triples_generated,
            'tier': '3',
            'type': 'specialist',
            'domain': 'elementary_number_theory'
        }


if __name__ == "__main__":
    print("DIOPHANTINE SPECIALIST TEST")
    specialist = DiophantineBasicSpecialist()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata

    task = MockTask({'operation': 'solve_linear', 'a': 3, 'b': 5, 'c': 1})
    result = specialist.process(task)
    print(f"3x + 5y = 1: {result.get('solution', 'N/A')}")
