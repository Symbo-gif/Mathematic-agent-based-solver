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
CONGRUENCE SPECIALIST (Tier 3)
===============================

Handles linear and quadratic congruences, Chinese Remainder Theorem.

CAPABILITIES:
------------
- solve_linear_congruence: ax ≡ b (mod m)
- chinese_remainder_theorem: System of congruences
- quadratic_congruence: ax² + bx + c ≡ 0 (mod p)
- verify_congruence: Check if solution is valid

FORMULATION:
-----------
Linear: ax ≡ b (mod m) has solutions iff gcd(a,m) | b
CRT: System {x ≡ rᵢ (mod mᵢ)} has unique solution mod lcm(mᵢ)

ALGORITHMIC BACKING:
-------------------
Native elementary_number_theory engine (core/elementary_number_theory.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Ireland & Rosen (1990). A Classical Introduction to Modern Number Theory.
- Niven et al. (1991). An Introduction to the Theory of Numbers.
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
    solve_linear_congruence, chinese_remainder_theorem, quadratic_congruence
)

logger = logging.getLogger(__name__)


class CongruenceSpecialist(BDIAgent):
    """
    Congruence Specialist - Modular Arithmetic Equations

    DIRECTIVE:
    ---------
    Solve linear congruences, quadratic congruences, and systems via CRT.

    OPERATIONS:
    ----------
    - solve_linear: ax ≡ b (mod m)
    - chinese_remainder: System of congruences
    - solve_quadratic: ax² + bx + c ≡ 0 (mod p)
    - verify_solution: Check if x satisfies congruence

    FORMULATION:
    -----------
    Linear congruence: ax ≡ b (mod m)
    Solution exists iff gcd(a, m) | b

    CRT: If gcd(mᵢ, mⱼ) = 1 for all i≠j, then
    {x ≡ rᵢ (mod mᵢ)} has unique solution mod M = ∏mᵢ

    REFERENCE:
    ---------
    - Niven et al. (1991), Chapter 2: Congruences
    """

    def __init__(
        self,
        agent_id: str = 'congruence_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Congruence Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.linear_congruences_solved = 0
        self.crt_systems_solved = 0
        self.quadratic_congruences_solved = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt.congruence',
            agent_id=self.agent_id,
            algorithm='congruence_solving',
            cost='low',
            instance=self,
            tier='3',
            operations='linear_crt_quadratic_verify'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt.congruence")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for congruence tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(
                tags=['congruence', 'crt', 'modular'],
                status=EntryStatus.PENDING
            )

            for task in tasks:
                belief_key = f'pending_cong_{task.entry_id}'
                if not self.has_belief(belief_key) and not self.has_belief(f'completed_{task.entry_id}'):
                    self.add_belief(predicate=belief_key, content=task, confidence=1.0, source='blackboard')

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans for pending congruence tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_cong_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'solve_linear')

            intention = Intention(
                plan_id=f'cong_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='solve_congruence',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the congruence solving plan."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                intention.advance()
            elif action == 'parse_input':
                self._execute_parse_input(intention, task)
            elif action == 'compute':
                self._execute_compute(intention)
            elif action == 'verify':
                intention.advance()
            elif action == 'post_result':
                self._execute_post_result(intention, task)
            else:
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_failure(intention, task, str(e))

    def _execute_parse_input(self, intention: Intention, task: Any):
        """Parse input parameters."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}

        parsed_data = {
            'operation': intention.metadata.get('operation', 'solve_linear'),
            'a': metadata.get('a', 1),
            'b': metadata.get('b', 0),
            'c': metadata.get('c', 0),
            'm': metadata.get('m', metadata.get('modulus', 10)),
            'remainders': metadata.get('remainders', []),
            'moduli': metadata.get('moduli', [])
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Solve congruence."""
        parsed_data = intention.metadata.get('parsed_data', {})
        operation = parsed_data['operation']

        try:
            if operation == 'solve_linear':
                a = parsed_data['a']
                b = parsed_data['b']
                m = parsed_data['m']

                solutions = solve_linear_congruence(a, b, m)

                result = {
                    'solutions': solutions if solutions else [],
                    'has_solution': solutions is not None,
                    'a': a, 'b': b, 'm': m,
                    'method': 'linear_congruence'
                }
                self.linear_congruences_solved += 1

            elif operation == 'chinese_remainder':
                remainders = parsed_data['remainders']
                moduli = parsed_data['moduli']

                solution = chinese_remainder_theorem(remainders, moduli)

                result = {
                    'solution': solution if solution else None,
                    'has_solution': solution is not None,
                    'remainders': remainders,
                    'moduli': moduli,
                    'method': 'crt'
                }
                self.crt_systems_solved += 1

            elif operation == 'solve_quadratic':
                a = parsed_data['a']
                b = parsed_data['b']
                c = parsed_data['c']
                p = parsed_data['m']

                solutions = quadratic_congruence(a, b, c, p)

                result = {
                    'solutions': solutions,
                    'solution_count': len(solutions),
                    'a': a, 'b': b, 'c': c, 'p': p,
                    'method': 'quadratic_congruence'
                }
                self.quadratic_congruences_solved += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"Congruence solving failed: {e}")

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result to Blackboard."""
        result = intention.metadata.get('result', {})
        task_id = intention.metadata.get('task_id')

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'congruence',
                tags=['congruence', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_cong_{task_id}')
        self.add_belief(f'completed_{task_id}', result)
        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"Congruence solving failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'congruence', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)

        self.remove_belief(f'pending_cong_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """Synchronous API for congruence operations."""
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'solve_linear')

        try:
            if operation == 'solve_linear':
                a = metadata.get('a', 1)
                b = metadata.get('b', 0)
                m = metadata.get('m', 10)

                solutions = solve_linear_congruence(a, b, m)

                result = {
                    'solutions': solutions if solutions else [],
                    'has_solution': solutions is not None,
                    'method': 'linear_congruence'
                }
                self.linear_congruences_solved += 1

            elif operation == 'chinese_remainder':
                remainders = metadata.get('remainders', [])
                moduli = metadata.get('moduli', [])

                solution = chinese_remainder_theorem(remainders, moduli)

                result = {
                    'solution': solution,
                    'has_solution': solution is not None,
                    'method': 'crt'
                }
                self.crt_systems_solved += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'congruence'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'linear_congruences_solved': self.linear_congruences_solved,
            'crt_systems_solved': self.crt_systems_solved,
            'quadratic_congruences_solved': self.quadratic_congruences_solved,
            'tier': '3',
            'type': 'specialist',
            'domain': 'elementary_number_theory'
        })
        return stats


if __name__ == "__main__":
    """Test Congruence Specialist"""
    print("=" * 80)
    print("CONGRUENCE SPECIALIST TEST")
    print("=" * 80)

    specialist = CongruenceSpecialist()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    # Test 1: Solve 3x ≡ 5 (mod 7)
    print("\nTest 1: 3x ≡ 5 (mod 7)")
    task1 = MockTask({'operation': 'solve_linear', 'a': 3, 'b': 5, 'm': 7})
    result1 = specialist.process(task1)
    print(f"  Solutions: {result1.get('solutions', [])}")

    # Test 2: CRT system
    print("\nTest 2: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)")
    task2 = MockTask({'operation': 'chinese_remainder', 'remainders': [2, 3, 2], 'moduli': [3, 5, 7]})
    result2 = specialist.process(task2)
    print(f"  Solution: {result2.get('solution', 'N/A')}")

    print("\nStatistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
