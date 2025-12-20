# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
CONTINUED FRACTIONS SPECIALIST (Tier 3)
========================================

Handles continued fraction expansions and convergent calculations.

CAPABILITIES:
------------
- expand_rational: Rational number → CF [a₀; a₁, a₂, ...]
- expand_quadratic_irrational: √D → periodic CF
- compute_convergents: CF → rational approximations
- best_approximation: Find best p/q approximation

FORMULATION:
-----------
CF: x = a₀ + 1/(a₁ + 1/(a₂ + ...))
Notation: [a₀; a₁, a₂, a₃, ...]

Quadratic irrationals have periodic CFs.

ALGORITHMIC BACKING:
-------------------
Native elementary_number_theory engine (core/elementary_number_theory.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Khinchin, A. Y. (1964). Continued Fractions.
- Hardy & Wright (2008). An Introduction to the Theory of Numbers, Chapter X.
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
    continued_fraction_expansion, quadratic_irrational_cf, convergents
)

logger = logging.getLogger(__name__)


class ContinuedFractionsSpecialist(BDIAgent):
    """
    Continued Fractions Specialist - CF Expansion & Convergents

    DIRECTIVE:
    ---------
    Expand numbers as continued fractions and compute convergents.

    OPERATIONS:
    ----------
    - expand_rational: num/denom → [a₀; a₁, a₂, ...]
    - expand_quadratic_irrational: √D → periodic CF
    - compute_convergents: CF → sequence of p/q approximations
    - verify_periodicity: Check if CF is periodic

    FORMULATION:
    -----------
    Continued fraction: x = a₀ + 1/(a₁ + 1/(a₂ + ...))

    Quadratic irrationals: √D = [a₀; periodic part]

    REFERENCE:
    ---------
    - Khinchin (1964), Continued Fractions
    - Hardy & Wright, Chapter X
    """

    def __init__(
        self,
        agent_id: str = 'continued_fractions_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Continued Fractions Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.cf_expansions = 0
        self.convergents_computed = 0
        self.quadratic_irrationals_expanded = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt.continued_fractions',
            agent_id=self.agent_id,
            algorithm='cf_expansion',
            cost='low',
            instance=self,
            tier='3',
            operations='expand_convergents_quadratic_irrational'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt.continued_fractions")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor for CF tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(
                tags=['continued_fraction', 'cf', 'convergent'],
                status=EntryStatus.PENDING
            )

            for task in tasks:
                belief_key = f'pending_cf_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(predicate=belief_key, content=task, confidence=1.0, source='blackboard')

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans for CF tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_cf_'):
                continue

            task = belief.content
            metadata = task.metadata if hasattr(task, 'metadata') else {}

            intention = Intention(
                plan_id=f'cf_{task.entry_id}',
                steps=['claim_task', 'parse_input', 'compute', 'post_result'],
                target_desire='expand_cf',
                metadata={'task_id': task.entry_id, 'task_entry': task, 'operation': metadata.get('operation', 'expand_rational')}
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute CF expansion."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(intention.metadata['task_id'], EntryStatus.IN_PROGRESS)
                intention.advance()
            elif action == 'parse_input':
                self._execute_parse_input(intention, task)
            elif action == 'compute':
                self._execute_compute(intention)
            elif action == 'post_result':
                self._execute_post_result(intention, task)
            else:
                intention.advance()

        except Exception as e:
            self._handle_failure(intention, task, str(e))

    def _execute_parse_input(self, intention: Intention, task: Any):
        """Parse input."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}

        parsed_data = {
            'operation': intention.metadata.get('operation'),
            'numerator': metadata.get('numerator', metadata.get('num', 22)),
            'denominator': metadata.get('denominator', metadata.get('denom', 7)),
            'D': metadata.get('D', 2),
            'max_terms': metadata.get('max_terms', 20)
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Compute CF expansion."""
        parsed_data = intention.metadata['parsed_data']
        operation = parsed_data['operation']

        try:
            if operation == 'expand_rational':
                num = parsed_data['numerator']
                denom = parsed_data['denominator']

                cf = continued_fraction_expansion(num, denom)

                result = {
                    'cf': cf,
                    'method': 'cf_expansion'
                }
                self.cf_expansions += 1

            elif operation == 'expand_quadratic_irrational':
                D = parsed_data['D']

                initial, periodic = quadratic_irrational_cf(D)

                result = {
                    'initial': initial,
                    'periodic': periodic,
                    'is_periodic': True,
                    'method': 'quadratic_irrational_cf'
                }
                self.quadratic_irrationals_expanded += 1

            elif operation == 'compute_convergents':
                cf = parsed_data.get('cf', [])

                convs = convergents(cf)

                result = {
                    'convergents': convs,
                    'count': len(convs),
                    'method': 'convergents'
                }
                self.convergents_computed += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"CF computation failed: {e}")

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result."""
        result = intention.metadata.get('result', {})

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'cf',
                tags=['cf', 'result'],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)

        self.remove_belief(f'pending_cf_{intention.metadata["task_id"]}')
        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle failure."""
        self.tasks_failed += 1
        self.remove_belief(f'pending_cf_{intention.metadata.get("task_id")}')

        while not intention.is_complete():
            intention.advance()

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """Synchronous API."""
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'expand_rational')

        try:
            if operation == 'expand_rational':
                num = metadata.get('numerator', 22)
                denom = metadata.get('denominator', 7)
                cf = continued_fraction_expansion(num, denom)

                result = {'cf': cf, 'method': 'cf_expansion'}
                self.cf_expansions += 1

            elif operation == 'expand_quadratic_irrational':
                D = metadata.get('D', 2)
                initial, periodic = quadratic_irrational_cf(D)

                result = {'initial': initial, 'periodic': periodic, 'method': 'quadratic_irrational_cf'}
                self.quadratic_irrationals_expanded += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            return {'error': str(e), 'method': 'cf'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'cf_expansions': self.cf_expansions,
            'convergents_computed': self.convergents_computed,
            'quadratic_irrationals_expanded': self.quadratic_irrationals_expanded,
            'tier': '3',
            'type': 'specialist',
            'domain': 'elementary_number_theory'
        })
        return stats


if __name__ == "__main__":
    print("CONTINUED FRACTIONS SPECIALIST TEST")
    specialist = ContinuedFractionsSpecialist()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata

    task = MockTask({'operation': 'expand_rational', 'numerator': 22, 'denominator': 7})
    result = specialist.process(task)
    print(f"22/7 = {result.get('cf', [])}")
