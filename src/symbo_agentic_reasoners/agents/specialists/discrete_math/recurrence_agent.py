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
PHASE 2 - RECURRENCE RELATION AGENT (Tier 3)
=============================================

Solves recurrence relations analytically and numerically.

Capabilities:
- Linear homogeneous recurrences with constant coefficients
- Linear non-homogeneous recurrences
- Characteristic equation method
- Master theorem for divide-and-conquer
- Sequence recognition
- Recurrence finding from sequence
- Numerical iteration

NO SYMPY - All implementations are native Python.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Callable, Tuple
import math
import re
import logging

logger = logging.getLogger('symbo_agentic_reasoners.recurrence')


# =============================================================================
# NATIVE RECURRENCE SOLVER (NO SYMPY)
# =============================================================================

class RecurrenceSolver:
    """
    Native recurrence relation solver.

    Supports:
    - Linear homogeneous recurrences with constant coefficients
    - Linear non-homogeneous recurrences
    - Characteristic equation method
    - Master theorem
    - Numerical iteration
    """

    @staticmethod
    def solve_linear_homogeneous(
        coefficients: List[float],
        initial_values: List[float]
    ) -> Dict[str, Any]:
        """
        Solve linear homogeneous recurrence with constant coefficients.

        Method: Characteristic equation
        a_n = c_1*a_{n-1} + c_2*a_{n-2} + ... + c_k*a_{n-k}

        Args:
            coefficients: [c_1, c_2, ..., c_k]
            initial_values: [a_0, a_1, ..., a_{k-1}]

        Returns:
            Dictionary with solution info and closed_form function
        """
        k = len(coefficients)

        if k == 1:
            c = coefficients[0]
            a0 = initial_values[0]
            return {
                'type': 'first_order',
                'solution': f'a_n = {a0} * {c}^n',
                'closed_form': lambda n, c=c, a0=a0: a0 * (c ** n),
                'method': 'direct'
            }

        if k == 2:
            c1, c2 = coefficients
            discriminant = c1**2 + 4*c2

            if discriminant > 0:
                r1 = (c1 + math.sqrt(discriminant)) / 2
                r2 = (c1 - math.sqrt(discriminant)) / 2

                a0, a1 = initial_values[0], initial_values[1]
                if abs(r1 - r2) < 1e-10:
                    r = c1 / 2
                    A = a0
                    B = (a1 - a0*r) / r if r != 0 else a1
                    return {
                        'type': 'second_order_repeated',
                        'root': r,
                        'solution': f'a_n = ({A:.6f} + {B:.6f}*n) * ({r:.6f})^n',
                        'closed_form': lambda n, A=A, B=B, r=r: (A + B*n) * (r**n),
                        'method': 'characteristic_equation'
                    }

                A = (a1 - a0*r2) / (r1 - r2) if r1 != r2 else a0
                B = a0 - A

                return {
                    'type': 'second_order_distinct_real',
                    'roots': (r1, r2),
                    'solution': f'a_n = {A:.6f}*({r1:.6f})^n + {B:.6f}*({r2:.6f})^n',
                    'closed_form': lambda n, A=A, B=B, r1=r1, r2=r2: A * (r1**n) + B * (r2**n),
                    'method': 'characteristic_equation'
                }

            elif discriminant == 0:
                r = c1 / 2
                a0, a1 = initial_values[0], initial_values[1]
                A = a0
                B = (a1 - a0*r) / r if r != 0 else a1

                return {
                    'type': 'second_order_repeated',
                    'root': r,
                    'solution': f'a_n = ({A:.6f} + {B:.6f}*n) * ({r:.6f})^n',
                    'closed_form': lambda n, A=A, B=B, r=r: (A + B*n) * (r**n),
                    'method': 'characteristic_equation'
                }

            else:
                real_part = c1 / 2
                imag_part = math.sqrt(-discriminant) / 2
                r = math.sqrt(real_part**2 + imag_part**2)
                theta = math.atan2(imag_part, real_part)

                a0, a1 = initial_values[0], initial_values[1]
                A = a0
                B = (a1/r - A*math.cos(theta)) / math.sin(theta) if math.sin(theta) != 0 else 0

                return {
                    'type': 'second_order_complex',
                    'modulus': r,
                    'argument': theta,
                    'solution': f'a_n = ({r:.6f})^n * ({A:.6f}*cos({theta:.6f}*n) + {B:.6f}*sin({theta:.6f}*n))',
                    'closed_form': lambda n, A=A, B=B, r=r, theta=theta: (r**n) * (A*math.cos(theta*n) + B*math.sin(theta*n)),
                    'method': 'characteristic_equation'
                }

        return RecurrenceSolver.solve_numerically(coefficients, initial_values)

    @staticmethod
    def solve_numerically(
        coefficients: List[float],
        initial_values: List[float],
        n_terms: int = 100
    ) -> Dict[str, Any]:
        """Compute terms numerically via iteration."""
        k = len(coefficients)
        sequence = list(initial_values)

        for n in range(k, n_terms):
            next_term = sum(coefficients[i] * sequence[n-1-i] for i in range(k))
            sequence.append(next_term)

        return {
            'type': 'numerical',
            'sequence': sequence,
            'method': 'iteration',
            'closed_form': None
        }

    @staticmethod
    def solve_fibonacci_type(a: int, b: int, F0: int = 0, F1: int = 1) -> Dict[str, Any]:
        """
        Solve generalized Fibonacci: F_n = a*F_{n-1} + b*F_{n-2}

        Standard Fibonacci: a=1, b=1
        Lucas numbers: a=1, b=1, F0=2, F1=1
        Pell numbers: a=2, b=1
        """
        return RecurrenceSolver.solve_linear_homogeneous([a, b], [F0, F1])

    @staticmethod
    def solve_divide_and_conquer(
        a: int,
        b: int,
        f_n: str
    ) -> Dict[str, Any]:
        """
        Master theorem for T(n) = a*T(n/b) + f(n)

        Args:
            a: Number of subproblems
            b: Factor by which problem size shrinks
            f_n: Work at each level: 'n', 'n*log(n)', 'n^2', 'log(n)', '1'

        Returns:
            Complexity analysis
        """
        log_b_a = math.log(a) / math.log(b)

        if f_n == '1':
            c = 0
        elif f_n == 'log(n)':
            c = 0
        elif f_n == 'n':
            c = 1
        elif f_n == 'n*log(n)':
            c = 1
        elif f_n == 'n^2':
            c = 2
        else:
            c = 1

        if c < log_b_a - 0.001:
            complexity = f'Theta(n^{log_b_a:.4f})'
            case = 1
        elif abs(c - log_b_a) < 0.001:
            complexity = f'Theta(n^{c} * log(n))'
            case = 2
        else:
            complexity = f'Theta({f_n})'
            case = 3

        return {
            'recurrence': f'T(n) = {a}*T(n/{b}) + {f_n}',
            'log_b_a': log_b_a,
            'f_exponent': c,
            'master_theorem_case': case,
            'complexity': complexity,
            'method': 'master_theorem'
        }

    @staticmethod
    def recognize_known_sequence(sequence: List[int]) -> Optional[Dict[str, Any]]:
        """Recognize common sequences from first few terms."""
        known = {
            (0, 1, 1, 2, 3, 5, 8): {'name': 'Fibonacci', 'formula': 'F_n = F_{n-1} + F_{n-2}'},
            (2, 1, 3, 4, 7, 11): {'name': 'Lucas', 'formula': 'L_n = L_{n-1} + L_{n-2}'},
            (0, 1, 2, 5, 12, 29): {'name': 'Pell', 'formula': 'P_n = 2*P_{n-1} + P_{n-2}'},
            (1, 1, 2, 5, 14, 42): {'name': 'Catalan', 'formula': 'C_n = (2n)! / ((n+1)! * n!)'},
            (1, 2, 6, 24, 120, 720): {'name': 'Factorial', 'formula': 'n!'},
            (1, 1, 2, 4, 7, 13, 24): {'name': 'Tribonacci', 'formula': 'T_n = T_{n-1} + T_{n-2} + T_{n-3}'},
        }

        seq_tuple = tuple(sequence[:7]) if len(sequence) >= 7 else tuple(sequence)

        for pattern, info in known.items():
            if seq_tuple[:len(pattern)] == pattern[:len(seq_tuple)]:
                return info

        return None

    @staticmethod
    def find_recurrence(sequence: List[int], max_order: int = 5) -> Optional[Dict[str, Any]]:
        """
        Attempt to find a linear recurrence that generates the sequence.
        """
        n = len(sequence)

        for order in range(1, min(max_order + 1, n // 2)):
            A = []
            b = []
            for i in range(order, min(n, order + order + 5)):
                row = [sequence[i-1-j] for j in range(order)]
                A.append(row)
                b.append(sequence[i])

            try:
                coeffs = RecurrenceSolver._solve_linear_system(A, b)
                if coeffs:
                    valid = True
                    for i in range(order, n):
                        predicted = sum(coeffs[j] * sequence[i-1-j] for j in range(order))
                        if abs(predicted - sequence[i]) > 0.001:
                            valid = False
                            break

                    if valid:
                        return {
                            'order': order,
                            'coefficients': coeffs,
                            'formula': 'a_n = ' + ' + '.join(f'{c:.4f}*a_{{n-{j+1}}}' for j, c in enumerate(coeffs))
                        }
            except Exception:
                continue

        return None

    @staticmethod
    def _solve_linear_system(A: List[List[float]], b: List[float]) -> Optional[List[float]]:
        """Simple Gaussian elimination for square systems."""
        n = len(A)
        m = len(A[0]) if A else 0

        if n < m:
            return None

        aug = [row[:] + [b[i]] for i, row in enumerate(A[:m])]

        for i in range(m):
            max_row = i
            for k in range(i + 1, m):
                if abs(aug[k][i]) > abs(aug[max_row][i]):
                    max_row = k
            aug[i], aug[max_row] = aug[max_row], aug[i]

            if abs(aug[i][i]) < 1e-10:
                return None

            for k in range(i + 1, m):
                factor = aug[k][i] / aug[i][i]
                for j in range(i, m + 1):
                    aug[k][j] -= factor * aug[i][j]

        x = [0.0] * m
        for i in range(m - 1, -1, -1):
            x[i] = aug[i][m]
            for j in range(i + 1, m):
                x[i] -= aug[i][j] * x[j]
            x[i] /= aug[i][i]

        return x

    @staticmethod
    def compute_nth_term(
        coefficients: List[float],
        initial_values: List[float],
        n: int
    ) -> float:
        """Compute the n-th term of a recurrence."""
        if n < len(initial_values):
            return initial_values[n]

        solution = RecurrenceSolver.solve_linear_homogeneous(coefficients, initial_values)

        if solution.get('closed_form'):
            return solution['closed_form'](n)

        sequence = list(initial_values)
        k = len(coefficients)
        for i in range(k, n + 1):
            next_term = sum(coefficients[j] * sequence[i-1-j] for j in range(k))
            sequence.append(next_term)

        return sequence[n]


# =============================================================================
# RECURRENCE RELATION AGENT (Tier 3)
# =============================================================================

class RecurrenceRelationAgent(BDIAgent):
    """
    Recurrence Relation Specialist - Tier 3

    Handles:
    - Linear homogeneous recurrences (characteristic equation)
    - Fibonacci-type recurrences
    - Divide-and-conquer analysis (Master theorem)
    - Sequence recognition
    - Recurrence finding from sequence
    - Numerical iteration
    """

    def __init__(
        self,
        agent_id: str = 'recurrence_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.recurrence',
                agent_id=agent_id,
                algorithm='characteristic_equation',
                cost='medium',
                instance=self,
                tier='3',
                operations='solve_recurrence_master_theorem_sequence_analysis'
            ))

        logger.info(f"[{agent_id}] Recurrence Relation Agent initialized")
        logger.info(f"  Algorithm: Characteristic equation, Master theorem")
        logger.info(f"  Operations: Recurrence solving, sequence analysis")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for recurrence tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus

            tasks = self.blackboard.query_entries(
                tags=['recurrence', 'sequence'],
                status=EntryStatus.PENDING
            )

            delegated = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata:
                    if task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                        tasks.append(task)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if self.has_belief(f'claimed_task_{task.entry_id}'):
                    continue
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans for recurrence tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()

            operation = self._determine_operation(raw_input)

            steps = ['claim_task', 'parse_input', f'compute_{operation}', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'rec_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_recurrence',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation, 'raw_input': raw_input}
            )
            new_intentions.append(intention)

        return new_intentions

    def _determine_operation(self, raw_input: str) -> str:
        """Determine which recurrence operation to perform."""
        if 'master' in raw_input or 'divide' in raw_input and 'conquer' in raw_input:
            return 'master_theorem'
        elif 'fibonacci' in raw_input:
            return 'fibonacci'
        elif 'find' in raw_input and 'recurrence' in raw_input:
            return 'find_recurrence'
        elif 'recognize' in raw_input or 'identify' in raw_input:
            return 'recognize_sequence'
        elif 'nth term' in raw_input or 'n-th term' in raw_input:
            return 'nth_term'
        elif 'sequence' in raw_input:
            return 'generate_sequence'
        else:
            return 'solve_recurrence'

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute recurrence computation."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_input':
                raw = intention.metadata.get('raw_input', '')
                parsed = self._parse_recurrence_input(raw)
                intention.metadata.update(parsed)
                intention.advance()

            elif action.startswith('compute_'):
                operation = action.replace('compute_', '')
                result = self._compute_operation(operation, intention.metadata)
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    result_str = self._format_result(result)
                    entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(result_str),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['recurrence', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': result_str, 'result_str': result_str}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def _parse_recurrence_input(self, raw: str) -> Dict[str, Any]:
        """Parse recurrence relation input."""
        result = {'coefficients': [], 'initial_values': [], 'n': None}

        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', raw)]

        if 'fibonacci' in raw.lower():
            result['coefficients'] = [1, 1]
            result['initial_values'] = [0, 1]
        elif 'a_n' in raw.lower() or 'recurrence' in raw.lower():
            if len(numbers) >= 2:
                coeff_count = min(len(numbers) // 2, 5)
                result['coefficients'] = [int(n) for n in numbers[:coeff_count]]
                result['initial_values'] = [int(n) for n in numbers[coeff_count:coeff_count*2]]
        elif 'master' in raw.lower():
            if len(numbers) >= 2:
                result['a'] = int(numbers[0])
                result['b'] = int(numbers[1])
                if 'n^2' in raw:
                    result['f_n'] = 'n^2'
                elif 'n*log' in raw or 'n log' in raw:
                    result['f_n'] = 'n*log(n)'
                elif 'log' in raw:
                    result['f_n'] = 'log(n)'
                else:
                    result['f_n'] = 'n'
        else:
            result['sequence'] = [int(n) for n in numbers]

        if len(numbers) > 0 and result['n'] is None:
            match = re.search(r'n\s*=\s*(\d+)', raw)
            if match:
                result['n'] = int(match.group(1))

        return result

    def _compute_operation(self, operation: str, metadata: Dict[str, Any]) -> Any:
        """Execute the specified recurrence operation."""
        coefficients = metadata.get('coefficients', [1, 1])
        initial_values = metadata.get('initial_values', [0, 1])
        sequence = metadata.get('sequence', [])
        n = metadata.get('n')

        if operation == 'solve_recurrence':
            return RecurrenceSolver.solve_linear_homogeneous(coefficients, initial_values)
        elif operation == 'fibonacci':
            return RecurrenceSolver.solve_fibonacci_type(1, 1, 0, 1)
        elif operation == 'master_theorem':
            a = metadata.get('a', 2)
            b = metadata.get('b', 2)
            f_n = metadata.get('f_n', 'n')
            return RecurrenceSolver.solve_divide_and_conquer(a, b, f_n)
        elif operation == 'recognize_sequence':
            return RecurrenceSolver.recognize_known_sequence(sequence)
        elif operation == 'find_recurrence':
            return RecurrenceSolver.find_recurrence(sequence)
        elif operation == 'nth_term':
            if n is not None:
                return RecurrenceSolver.compute_nth_term(coefficients, initial_values, n)
            return None
        elif operation == 'generate_sequence':
            terms = metadata.get('n', 20)
            return RecurrenceSolver.solve_numerically(coefficients, initial_values, terms)
        else:
            return RecurrenceSolver.solve_linear_homogeneous(coefficients, initial_values)

    def _format_result(self, result: Any) -> str:
        """Format result for output."""
        if isinstance(result, dict):
            if 'solution' in result:
                return result['solution']
            elif 'complexity' in result:
                return f"Complexity: {result['complexity']} (Master Theorem Case {result.get('master_theorem_case', '?')})"
            elif 'name' in result:
                return f"Sequence: {result['name']}, Formula: {result['formula']}"
            elif 'formula' in result:
                return f"Recurrence: {result['formula']}"
            elif 'sequence' in result:
                return f"Sequence: {result['sequence'][:20]}"
            return str(result)
        return str(result)

    def process(self, task_entry) -> Any:
        """Direct invocation entry point for supervisor delegation."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()

            operation = self._determine_operation(raw_input)
            parsed = self._parse_recurrence_input(raw_input)
            result = self._compute_operation(operation, parsed)
            result_str = self._format_result(result)

            self.tasks_executed += 1

            return create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(result_str),
                author_agent=self.agent_id,
                conversation_id=getattr(task_entry, 'conversation_id', 'direct'),
                tags=['recurrence', 'result'],
                status=EntryStatus.COMPLETED,
                metadata={'result': result_str, 'result_str': result_str}
            )

        except Exception as e:
            logger.error(f"[{self.agent_id}] process error: {e}")
            return create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=f"Error: {e}",
                author_agent=self.agent_id,
                conversation_id=getattr(task_entry, 'conversation_id', 'direct'),
                tags=['recurrence', 'error'],
                status=EntryStatus.FAILED,
                metadata={'error': str(e)}
            )

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed})
        return stats
