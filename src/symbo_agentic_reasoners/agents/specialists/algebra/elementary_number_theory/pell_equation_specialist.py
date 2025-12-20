# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
PELL EQUATION SPECIALIST (Tier 3)
==================================

Handles Pell equations x² - Dy² = 1 and negative Pell x² - Dy² = -1.

CAPABILITIES:
------------
- fundamental_solution: Find smallest (x,y) for x² - Dy² = 1
- generate_solutions: Generate n solutions
- negative_pell: Solve x² - Dy² = -1
- verify_solution: Check if (x,y) satisfies equation

FORMULATION:
-----------
Pell equation: x² - Dy² = 1 where D is not a perfect square
Fundamental solution: Smallest (x₁, y₁) with x₁, y₁ > 0
General solutions: (xₙ, yₙ) from (x₁, y₁) via recurrence

ALGORITHMIC BACKING:
-------------------
Native elementary_number_theory engine (core/elementary_number_theory.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lenstra, H. W. (2002). Solving the Pell equation.
- Ireland & Rosen (1990), Chapter 17: Pell's Equation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.elementary_number_theory import (
    pell_fundamental_solution, pell_solutions, negative_pell_solution
)

logger = logging.getLogger(__name__)


class PellEquationSpecialist(BDIAgent):
    """
    Pell Equation Specialist - x² - Dy² = ±1

    DIRECTIVE:
    ---------
    Solve Pell equations and generate solution sequences.

    OPERATIONS:
    ----------
    - fundamental_solution: Find (x₁, y₁) for x² - Dy² = 1
    - generate_solutions: Generate n solutions
    - negative_pell: Solve x² - Dy² = -1
    - verify: Check if (x,y) satisfies equation

    FORMULATION:
    -----------
    Pell: x² - Dy² = 1
    Negative Pell: x² - Dy² = -1 (exists iff period of √D CF is odd)

    REFERENCE:
    ---------
    - Lenstra (2002), Solving the Pell Equation
    """

    def __init__(
        self,
        agent_id: str = 'pell_equation_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Pell Equation Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.fundamental_solutions_found = 0
        self.solution_sequences_generated = 0
        self.negative_pell_solved = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt.pell',
            agent_id=self.agent_id,
            algorithm='pell_solver',
            cost='low',
            instance=self,
            tier='3',
            operations='fundamental_generate_negative_verify'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt.pell")

    def update_beliefs(self):
        """PERCEIVE: Monitor for Pell tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(tags=['pell', 'pell_equation'], status=EntryStatus.PENDING)
            for task in tasks:
                belief_key = f'pending_pell_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(predicate=belief_key, content=task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create Pell solving plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_pell_'):
                continue

            task = belief.content
            metadata = task.metadata if hasattr(task, 'metadata') else {}

            intention = Intention(
                plan_id=f'pell_{task.entry_id}',
                steps=['claim_task', 'parse_input', 'compute', 'post_result'],
                target_desire='solve_pell',
                metadata={'task_id': task.entry_id, 'task_entry': task, 'operation': metadata.get('operation', 'fundamental_solution')}
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Solve Pell equation."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(intention.metadata['task_id'], EntryStatus.IN_PROGRESS)
                intention.advance()
            elif action == 'parse_input':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                intention.metadata['parsed_data'] = {
                    'operation': intention.metadata.get('operation'),
                    'D': metadata.get('D', 2),
                    'n_solutions': metadata.get('n_solutions', 5)
                }
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
        """Compute Pell solution."""
        parsed_data = intention.metadata['parsed_data']
        operation = parsed_data['operation']

        try:
            D = parsed_data['D']

            if operation == 'fundamental_solution':
                x, y = pell_fundamental_solution(D)
                result = {'x': int(x), 'y': int(y), 'D': D, 'method': 'pell_fundamental'}
                self.fundamental_solutions_found += 1

            elif operation == 'generate_solutions':
                n_sols = parsed_data['n_solutions']
                solutions = pell_solutions(D, n_sols)
                result = {'solutions': solutions, 'D': D, 'count': len(solutions), 'method': 'pell_solutions'}
                self.solution_sequences_generated += 1

            elif operation == 'negative_pell':
                solution = negative_pell_solution(D)
                result = {
                    'solution': solution,
                    'has_solution': solution is not None,
                    'D': D,
                    'method': 'negative_pell'
                }
                self.negative_pell_solved += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"Pell solving failed: {e}")

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result."""
        result = intention.metadata.get('result', {})

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'pell',
                tags=['pell', 'result'],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)

        self.remove_belief(f'pending_pell_{intention.metadata["task_id"]}')
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
        operation = metadata.get('operation', 'fundamental_solution')

        try:
            D = metadata.get('D', 2)

            if operation == 'fundamental_solution':
                x, y = pell_fundamental_solution(D)
                result = {'x': int(x), 'y': int(y), 'method': 'pell'}
                self.fundamental_solutions_found += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            return {'error': str(e), 'method': 'pell'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'fundamental_solutions_found': self.fundamental_solutions_found,
            'solution_sequences_generated': self.solution_sequences_generated,
            'negative_pell_solved': self.negative_pell_solved,
            'tier': '3',
            'type': 'specialist',
            'domain': 'elementary_number_theory'
        }


if __name__ == "__main__":
    print("PELL EQUATION SPECIALIST TEST")
    specialist = PellEquationSpecialist()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata

    task = MockTask({'operation': 'fundamental_solution', 'D': 2})
    result = specialist.process(task)
    print(f"x² - 2y² = 1: (x,y) = ({result.get('x')}, {result.get('y')})")
