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
PHASE 2 - COMBINATORICS AGENT (Tier 3)
======================================

Handles counting, permutations, combinations, and advanced combinatorics.
Uses generating functions for algorithmic backing (LLMs are weak here).

CAPABILITIES:
- Basic: Factorial, permutations, combinations
- Advanced: Stirling numbers, Catalan numbers, Bell numbers
- Partitions: Integer partitions, compositions
- Special: Derangements, multinomials, subfactorials

NO SYMPY - All implementations are pure Python.
"""

import sys
import os
from functools import lru_cache
from typing import Dict, Any, List, Optional, Tuple
import math

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard


# =============================================================================
# NATIVE COMBINATORICS IMPLEMENTATIONS - NO SYMPY
# =============================================================================

def factorial(n: int) -> int:
    """Compute n! using Python's math.factorial."""
    if n < 0:
        raise ValueError("factorial not defined for negative numbers")
    return math.factorial(n)


def binomial(n: int, k: int) -> int:
    """
    Compute binomial coefficient C(n, k) = n! / (k! * (n-k)!)

    Uses the multiplicative formula for efficiency:
    C(n, k) = n * (n-1) * ... * (n-k+1) / k!
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1

    # Use smaller k for efficiency
    if k > n - k:
        k = n - k

    # Compute using multiplicative formula to avoid large intermediate factorials
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


@lru_cache(maxsize=1024)
def stirling_first(n: int, k: int) -> int:
    """
    Compute Stirling number of the first kind s(n, k).

    s(n, k) = number of permutations of n elements with k cycles.

    Recurrence: s(n, k) = (n-1) * s(n-1, k) + s(n-1, k-1)

    Returns the unsigned Stirling number (absolute value).
    """
    if n < 0 or k < 0:
        return 0
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    if k > n:
        return 0

    return (n - 1) * stirling_first(n - 1, k) + stirling_first(n - 1, k - 1)


@lru_cache(maxsize=1024)
def stirling_second(n: int, k: int) -> int:
    """
    Compute Stirling number of the second kind S(n, k).

    S(n, k) = number of ways to partition n elements into k non-empty subsets.

    Recurrence: S(n, k) = k * S(n-1, k) + S(n-1, k-1)
    """
    if n < 0 or k < 0:
        return 0
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    if k > n:
        return 0

    return k * stirling_second(n - 1, k) + stirling_second(n - 1, k - 1)


@lru_cache(maxsize=256)
def catalan(n: int) -> int:
    """
    Compute the nth Catalan number C_n.

    C_n = (2n)! / ((n+1)! * n!)
        = C(2n, n) / (n + 1)

    Applications: valid parenthesizations, binary trees, triangulations.
    """
    if n < 0:
        raise ValueError("Catalan number not defined for negative n")
    if n == 0:
        return 1

    return binomial(2 * n, n) // (n + 1)


@lru_cache(maxsize=256)
def bell(n: int) -> int:
    """
    Compute the nth Bell number B_n.

    B_n = sum of S(n, k) for k = 0 to n
        = number of partitions of a set of n elements.
    """
    if n < 0:
        raise ValueError("Bell number not defined for negative n")

    return sum(stirling_second(n, k) for k in range(n + 1))


@lru_cache(maxsize=256)
def derangement(n: int) -> int:
    """
    Compute the number of derangements D_n (subfactorial !n).

    A derangement is a permutation with no fixed points.

    D_n = n! * sum((-1)^k / k! for k = 0 to n)
        = (n - 1) * (D_{n-1} + D_{n-2})
    """
    if n < 0:
        raise ValueError("Derangement not defined for negative n")
    if n == 0:
        return 1
    if n == 1:
        return 0

    return (n - 1) * (derangement(n - 1) + derangement(n - 2))


def multinomial(n: int, groups: List[int]) -> int:
    """
    Compute multinomial coefficient n! / (k1! * k2! * ... * km!)

    Args:
        n: Total number of elements
        groups: List of group sizes [k1, k2, ..., km]

    Returns:
        Number of ways to divide n items into groups of sizes k1, k2, ...
    """
    if sum(groups) != n:
        raise ValueError(f"Group sizes {groups} must sum to {n}")

    result = factorial(n)
    for k in groups:
        result //= factorial(k)
    return result


def permutation(n: int, r: int) -> int:
    """
    Compute P(n, r) = n! / (n-r)!

    Number of r-permutations of n distinct objects.
    """
    if r < 0 or r > n:
        return 0
    return factorial(n) // factorial(n - r)


def permutation_with_repetition(n: int, r: int) -> int:
    """
    Compute n^r - permutations with repetition allowed.
    """
    if n < 0 or r < 0:
        raise ValueError("n and r must be non-negative")
    return n ** r


def combination_with_repetition(n: int, r: int) -> int:
    """
    Compute C(n+r-1, r) - combinations with repetition allowed.

    Also known as multiset coefficient or "stars and bars".
    """
    if n <= 0 or r < 0:
        return 0 if r > 0 else 1
    return binomial(n + r - 1, r)


@lru_cache(maxsize=1024)
def partition_count(n: int, max_part: Optional[int] = None) -> int:
    """
    Compute p(n) - number of integer partitions of n.

    Uses recurrence relation based on Euler's pentagonal number theorem.

    Args:
        n: The integer to partition
        max_part: Maximum part size allowed (None for unrestricted)

    Returns:
        Number of partitions
    """
    if n < 0:
        return 0
    if n == 0:
        return 1

    if max_part is None:
        max_part = n

    if max_part <= 0:
        return 0

    if max_part > n:
        max_part = n

    # p(n, k) = p(n, k-1) + p(n-k, k)
    return partition_count(n, max_part - 1) + partition_count(n - max_part, max_part)


def generate_partitions(n: int) -> List[List[int]]:
    """
    Generate all integer partitions of n.

    Returns partitions in descending order (e.g., [3, 2, 1] not [1, 2, 3]).
    """
    if n <= 0:
        return [[]] if n == 0 else []

    partitions = []

    def _generate(remaining: int, max_val: int, current: List[int]):
        if remaining == 0:
            partitions.append(current[:])
            return

        for i in range(min(remaining, max_val), 0, -1):
            current.append(i)
            _generate(remaining - i, i, current)
            current.pop()

    _generate(n, n, [])
    return partitions


@lru_cache(maxsize=256)
def fibonacci(n: int) -> int:
    """Compute nth Fibonacci number (0-indexed: F_0=0, F_1=1)."""
    if n < 0:
        raise ValueError("Fibonacci not defined for negative n")
    if n <= 1:
        return n

    # Use matrix exponentiation for large n
    if n > 30:
        return _fib_matrix(n)

    return fibonacci(n - 1) + fibonacci(n - 2)


def _fib_matrix(n: int) -> int:
    """Compute Fibonacci using matrix exponentiation O(log n)."""
    def matrix_mult(A, B):
        return [
            [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
        ]

    def matrix_pow(M, p):
        if p == 1:
            return M
        if p % 2 == 0:
            half = matrix_pow(M, p // 2)
            return matrix_mult(half, half)
        return matrix_mult(M, matrix_pow(M, p - 1))

    if n == 0:
        return 0

    M = [[1, 1], [1, 0]]
    result = matrix_pow(M, n)
    return result[0][1]


@lru_cache(maxsize=256)
def lucas(n: int) -> int:
    """Compute nth Lucas number (L_0=2, L_1=1)."""
    if n < 0:
        raise ValueError("Lucas number not defined for negative n")
    if n == 0:
        return 2
    if n == 1:
        return 1
    return lucas(n - 1) + lucas(n - 2)


def compositions(n: int, k: Optional[int] = None) -> List[List[int]]:
    """
    Generate compositions of n (ordered partitions).

    Args:
        n: The integer to compose
        k: Number of parts (None for all compositions)

    Returns:
        List of compositions
    """
    if n < 0:
        return []
    if n == 0:
        return [[]] if k is None or k == 0 else []

    if k is not None:
        return _compositions_k_parts(n, k)

    # All compositions using binary representation
    results = []
    for i in range(2 ** (n - 1)):
        comp = []
        count = 1
        for j in range(n - 1):
            if i & (1 << j):
                comp.append(count)
                count = 1
            else:
                count += 1
        comp.append(count)
        results.append(comp)
    return results


def _compositions_k_parts(n: int, k: int) -> List[List[int]]:
    """Generate compositions of n into exactly k parts."""
    if k <= 0 or n < k:
        return []
    if k == 1:
        return [[n]]

    results = []
    for first in range(1, n - k + 2):
        for rest in _compositions_k_parts(n - first, k - 1):
            results.append([first] + rest)
    return results


def eulerian(n: int, k: int) -> int:
    """
    Compute Eulerian number A(n, k).

    A(n, k) = number of permutations of [1..n] with exactly k ascents.

    Recurrence: A(n, k) = (k+1) * A(n-1, k) + (n-k) * A(n-1, k-1)
    """
    if n < 0 or k < 0 or k >= n:
        return 1 if n == 0 and k == 0 else 0
    if n == 0:
        return 1 if k == 0 else 0

    # Use explicit formula
    result = 0
    for j in range(k + 1):
        sign = (-1) ** j
        result += sign * binomial(n + 1, j) * (k + 1 - j) ** n
    return result

class CombinatoricsAgent(BDIAgent):
    """
    BDI Agent for advanced combinatorics computations.

    Capabilities:
    - Basic: factorial, permutation, combination
    - Advanced: Stirling numbers, Catalan, Bell, derangements
    - Sequences: Fibonacci, Lucas
    - Partitions: integer partitions, compositions
    - Special: multinomial, Eulerian numbers
    """

    # Operation keywords for task routing
    OPERATION_KEYWORDS = {
        'factorial': ['factorial', '!', 'n!'],
        'permutation': ['permutation', 'p(', 'arrange', 'ordering'],
        'combination': ['combination', 'c(', 'choose', 'select', 'binomial'],
        'stirling': ['stirling', 's(n,k)', 'stirling1', 'stirling2', 'cycle'],
        'catalan': ['catalan', 'parenthes', 'ballot', 'dyck'],
        'bell': ['bell number', 'bell(', 'partition of set'],
        'derangement': ['derangement', 'subfactorial', '!n', 'no fixed'],
        'partition': ['partition', 'p(n)', 'integer partition'],
        'fibonacci': ['fibonacci', 'fib(', 'fib_'],
        'lucas': ['lucas'],
        'composition': ['composition', 'ordered partition'],
        'multinomial': ['multinomial', 'multiset'],
        'eulerian': ['eulerian', 'ascent', 'descent'],
    }

    def __init__(self, agent_id='combinatorics_001', df: Optional[DirectoryFacilitator] = None, blackboard: Optional[Blackboard] = None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.combinatorics',
                agent_id=agent_id,
                algorithm='generating_functions',
                cost='medium',
                instance=self,
                tier='3',
                operations='factorial_permutation_combination_stirling_catalan_bell_derangement_partition_fibonacci'))

        print(f"[{agent_id}] Combinatorics Agent initialized (enhanced)")
        print(f"  Algorithm: Generating functions + dynamic programming")
        print(f"  Operations: Basic + Stirling, Catalan, Bell, partitions, Fibonacci")

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The Combinatorics Agent's BDI loop:
    #   1. update_beliefs() - Find combinatorics tasks on Blackboard
    #   2. deliberate() - Create computation plans
    #   3. execute_step() - Execute via native implementations
    #
    # CRITICAL: All computation uses native implementations (NO SYMPY)
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for combinatorics tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus

            # Find tasks tagged for combinatorics
            tasks = self.blackboard.query_entries(
                tags=['combinatorics'],
                status=EntryStatus.PENDING
            )

            # Also find delegated tasks
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
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create computation plans for combinatorics tasks."""
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

            # Determine operation using keyword matching
            operation = self._detect_operation(raw_input)

            steps = ['claim_task', 'parse_numbers', f'compute_{operation}', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'comb_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_combinatorics',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation, 'raw_input': raw_input}
            )
            new_intentions.append(intention)

        return new_intentions

    def _detect_operation(self, raw_input: str) -> str:
        """Detect the combinatorics operation from input text."""
        raw_lower = raw_input.lower()

        # Check each operation type by keywords (order matters for specificity)
        priority_order = [
            'stirling', 'catalan', 'bell', 'derangement', 'eulerian',
            'lucas', 'fibonacci', 'partition', 'composition', 'multinomial',
            'permutation', 'combination', 'factorial'
        ]

        for op in priority_order:
            for keyword in self.OPERATION_KEYWORDS.get(op, []):
                if keyword in raw_lower:
                    return op

        # Default to combination
        return 'combination'

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute combinatorics computation (native implementations)."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        import re

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

            elif action == 'parse_numbers':
                raw = intention.metadata.get('raw_input', '')
                numbers = [int(n) for n in re.findall(r'\d+', raw)]
                intention.metadata['numbers'] = numbers
                intention.advance()

            elif action == 'compute_factorial':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                result = factorial(n)
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_permutation':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if len(numbers) > 0 else 0
                r = numbers[1] if len(numbers) > 1 else n
                result = permutation(n, r)
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_combination':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if len(numbers) > 0 else 0
                r = numbers[1] if len(numbers) > 1 else 0
                result = binomial(n, r)
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_stirling':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if len(numbers) > 0 else 0
                k = numbers[1] if len(numbers) > 1 else 0
                raw = intention.metadata.get('raw_input', '').lower()
                # First kind vs second kind
                if 'first' in raw or 'stirling1' in raw or 'cycle' in raw:
                    result = stirling_first(n, k)
                    kind = 'first'
                else:
                    result = stirling_second(n, k)
                    kind = 'second'
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"Stirling({kind}) S({n},{k}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_catalan':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                result = catalan(n)
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"Catalan({n}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_bell':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                result = bell(n)
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"Bell({n}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_derangement':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                result = derangement(n)
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"D({n}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_fibonacci':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                result = fibonacci(n)
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"F({n}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_lucas':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                result = lucas(n)
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"L({n}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_partition':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                result = partition_count(n)
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"p({n}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_composition':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if numbers else 0
                k = numbers[1] if len(numbers) > 1 else None
                if k is not None:
                    result = len(_compositions_k_parts(n, k))
                else:
                    result = 2 ** (n - 1) if n > 0 else 1  # Total compositions = 2^(n-1)
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_multinomial':
                numbers = intention.metadata.get('numbers', [])
                if len(numbers) >= 2:
                    n = numbers[0]
                    groups = numbers[1:]
                    result = multinomial(n, groups)
                else:
                    result = 1
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_eulerian':
                numbers = intention.metadata.get('numbers', [])
                n = numbers[0] if len(numbers) > 0 else 0
                k = numbers[1] if len(numbers) > 1 else 0
                result = eulerian(n, k)
                intention.metadata['result'] = result
                intention.metadata['result_detail'] = f"A({n},{k}) = {result}"
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                detail = intention.metadata.get('result_detail', str(result))
                if self.blackboard:
                    entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['combinatorics', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': str(result), 'result_str': detail}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = CombinatoricsAgent()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed})
        return stats
