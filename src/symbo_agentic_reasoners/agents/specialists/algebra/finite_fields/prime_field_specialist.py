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
PRIME FIELD SPECIALIST (Tier 3)
================================

Handles operations in prime fields GF(p).

CAPABILITIES:
------------
- create_prime_field: Construct GF(p) with validation
- field_element_inverse: Compute a^(-1) mod p
- primitive_element: Find generator of GF(p)*
- element_order: Compute multiplicative order
- verify_prime_field: Validate p is prime
- quadratic_residue: Check if a is quadratic residue mod p

FORMULATION:
-----------
GF(p) = Z/pZ = {0, 1, 2, ..., p-1}
Addition: (a + b) mod p
Multiplication: (a × b) mod p
Inverse: a^(-1) such that a × a^(-1) ≡ 1 (mod p) [Fermat: a^(p-2)]
Order: Smallest k > 0 such that a^k ≡ 1 (mod p)

ALGORITHMIC BACKING:
-------------------
Native finite_fields module (core/finite_fields.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lidl & Niederreiter (1997), Chapter 1: Structure of Finite Fields
- Shoup (2005), Chapter 11: Finite Fields
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
from symbo_agentic_reasoners.core.finite_fields import (
    GFpElement, is_prime, mod_inverse, gcd, prime_factorization
)

logger = logging.getLogger(__name__)


class PrimeFieldSpecialist(BDIAgent):
    """
    Prime Field Specialist - GF(p) Operations

    DIRECTIVE:
    ---------
    Handle all operations in prime fields GF(p) where p is prime.

    OPERATIONS:
    ----------
    - create_prime_field: Construct and validate GF(p)
    - field_element: Create element in GF(p)
    - inverse: Compute multiplicative inverse
    - primitive_element: Find generator of multiplicative group
    - element_order: Compute multiplicative order
    - is_quadratic_residue: Euler criterion test

    FORMULATION:
    -----------
    GF(p) is the unique field of order p (p prime).
    Multiplicative group GF(p)* is cyclic of order p-1.
    Primitive element generates all non-zero elements.

    REFERENCE:
    ---------
    - Lidl & Niederreiter (1997), Finite Fields, Chapter 1
    """

    def __init__(
        self,
        agent_id: str = 'prime_field_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Prime Field Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.prime_fields_created = 0
        self.elements_inverted = 0
        self.primitive_elements_found = 0
        self.order_computations = 0
        self.quadratic_residue_tests = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.finite_fields.prime_field',
            agent_id=self.agent_id,
            algorithm='prime_field_operations',
            cost='low',
            instance=self,
            type='specialist',
            tier='3',
            operations='create_inverse_primitive_order_residue'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as prime field specialist")

    # ========================================
    # Core Operations
    # ========================================

    def create_prime_field(self, p: int) -> Dict[str, Any]:
        """
        Construct prime field GF(p).

        Args:
            p: Prime number

        Returns:
            Field structure with metadata
        """
        if not isinstance(p, int) or p < 2:
            return {
                'success': False,
                'error': f'p={p} must be integer >= 2'
            }

        if not is_prime(p):
            return {
                'success': False,
                'error': f'p={p} is not prime'
            }

        self.prime_fields_created += 1

        return {
            'success': True,
            'field': {
                'p': p,
                'order': p,
                'characteristic': p,
                'type': 'prime_field',
                'multiplicative_group_order': p - 1,
                'is_prime_field': True
            },
            'method': 'prime_field_construction'
        }

    def field_element_inverse(self, a: int, p: int) -> Dict[str, Any]:
        """
        Compute multiplicative inverse of a in GF(p).

        Uses extended Euclidean algorithm (or Fermat's little theorem).

        Args:
            a: Element to invert (must be non-zero)
            p: Prime modulus

        Returns:
            Inverse a^(-1) mod p
        """
        if not is_prime(p):
            return {
                'success': False,
                'error': f'p={p} is not prime'
            }

        a = a % p
        if a == 0:
            return {
                'success': False,
                'error': 'Cannot compute inverse of zero'
            }

        inv = mod_inverse(a, p)
        if inv is None:
            return {
                'success': False,
                'error': f'No inverse for {a} mod {p}'
            }

        self.elements_inverted += 1

        return {
            'success': True,
            'inverse': inv,
            'verification': (a * inv) % p == 1,
            'method': 'extended_euclidean'
        }

    def primitive_element(self, p: int) -> Dict[str, Any]:
        """
        Find a primitive element (generator) of GF(p)*.

        A primitive element g generates all non-zero elements:
        GF(p)* = {g^0, g^1, g^2, ..., g^(p-2)}

        Args:
            p: Prime modulus

        Returns:
            Primitive element g
        """
        if not is_prime(p):
            return {
                'success': False,
                'error': f'p={p} is not prime'
            }

        if p == 2:
            self.primitive_elements_found += 1
            return {
                'success': True,
                'primitive_element': 1,
                'order': 1,
                'method': 'trivial_p=2'
            }

        # Find primitive element by checking candidates
        order = p - 1
        factorization = prime_factorization(order)
        # Handle both tuple of tuples and dict formats
        if isinstance(factorization, dict):
            prime_divs = list(factorization.keys())
        else:
            prime_divs = [pair[0] for pair in factorization]

        for g in range(2, p):
            is_primitive = True
            for q in prime_divs:
                # Check if g^((p-1)/q) ≡ 1 (mod p)
                if pow(g, order // q, p) == 1:
                    is_primitive = False
                    break

            if is_primitive:
                self.primitive_elements_found += 1
                return {
                    'success': True,
                    'primitive_element': g,
                    'order': order,
                    'method': 'exhaustive_search'
                }

        return {
            'success': False,
            'error': 'Could not find primitive element (unexpected)'
        }

    def element_order(self, a: int, p: int) -> Dict[str, Any]:
        """
        Compute multiplicative order of element a in GF(p)*.

        Order is smallest positive k such that a^k ≡ 1 (mod p).

        Args:
            a: Non-zero element
            p: Prime modulus

        Returns:
            Multiplicative order
        """
        if not is_prime(p):
            return {
                'success': False,
                'error': f'p={p} is not prime'
            }

        a = a % p
        if a == 0:
            return {
                'success': False,
                'error': 'Zero element has no multiplicative order'
            }

        if a == 1:
            self.order_computations += 1
            return {
                'success': True,
                'order': 1,
                'element': a,
                'modulus': p,
                'method': 'trivial'
            }

        # Order divides p-1 (Lagrange's theorem)
        max_order = p - 1
        divisors = self._get_divisors(max_order)

        for d in sorted(divisors):
            if pow(a, d, p) == 1:
                self.order_computations += 1
                return {
                    'success': True,
                    'order': d,
                    'element': a,
                    'modulus': p,
                    'is_primitive': d == max_order,
                    'method': 'divisor_search'
                }

        self.order_computations += 1
        return {
            'success': True,
            'order': max_order,
            'element': a,
            'modulus': p,
            'is_primitive': True,
            'method': 'divisor_search'
        }

    def is_quadratic_residue(self, a: int, p: int) -> Dict[str, Any]:
        """
        Check if a is a quadratic residue mod p using Euler's criterion.

        a is QR mod p iff a^((p-1)/2) ≡ 1 (mod p)

        Args:
            a: Element to test
            p: Odd prime modulus

        Returns:
            True if a is quadratic residue
        """
        if not is_prime(p):
            return {
                'success': False,
                'error': f'p={p} is not prime'
            }

        if p == 2:
            self.quadratic_residue_tests += 1
            return {
                'success': True,
                'is_quadratic_residue': True,
                'element': a % 2,
                'modulus': 2,
                'legendre_symbol': 0 if a % 2 == 0 else 1,
                'method': 'trivial_p=2'
            }

        a = a % p
        if a == 0:
            self.quadratic_residue_tests += 1
            return {
                'success': True,
                'is_quadratic_residue': True,
                'element': 0,
                'modulus': p,
                'legendre_symbol': 0,
                'method': 'zero_element'
            }

        # Euler's criterion
        euler = pow(a, (p - 1) // 2, p)
        is_qr = euler == 1

        self.quadratic_residue_tests += 1

        return {
            'success': True,
            'is_quadratic_residue': is_qr,
            'element': a,
            'modulus': p,
            'legendre_symbol': 1 if is_qr else -1,
            'method': 'euler_criterion'
        }

    def _get_divisors(self, n: int) -> List[int]:
        """Get all divisors of n."""
        divisors = []
        for i in range(1, int(n ** 0.5) + 1):
            if n % i == 0:
                divisors.append(i)
                if i != n // i:
                    divisors.append(n // i)
        return sorted(divisors)

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """
        Process prime field task.

        Args:
            task_entry: Task from blackboard or direct call

        Returns:
            Result entry or dictionary
        """
        self.tasks_executed += 1

        try:
            # Extract metadata
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'create_prime_field')
            p = metadata.get('p') or metadata.get('prime') or metadata.get('modulus')
            a = metadata.get('a') or metadata.get('element')

            # Route to appropriate method
            if operation in ['create', 'create_prime_field', 'construct']:
                result = self.create_prime_field(p)
            elif operation in ['inverse', 'invert', 'field_element_inverse']:
                result = self.field_element_inverse(a, p)
            elif operation in ['primitive', 'primitive_element', 'generator']:
                result = self.primitive_element(p)
            elif operation in ['order', 'element_order', 'multiplicative_order']:
                result = self.element_order(a, p)
            elif operation in ['quadratic_residue', 'is_qr', 'legendre']:
                result = self.is_quadratic_residue(a, p)
            else:
                # Default: try to interpret as create field
                if p is not None:
                    result = self.create_prime_field(p)
                else:
                    result = {
                        'success': False,
                        'error': f'Unknown operation: {operation}'
                    }

            if result.get('success', False):
                self.tasks_succeeded += 1
            else:
                self.tasks_failed += 1

            # Create blackboard entry if applicable
            if self.blackboard and hasattr(task_entry, 'conversation_id'):
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    str(result),
                    self.agent_id,
                    task_entry.conversation_id,
                    ['finite_field', 'prime_field', 'gf_p'],
                    EntryStatus.COMPLETED if result.get('success') else EntryStatus.FAILED,
                    {'result': result}
                )

            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] Task processing failed: {e}")
            return {'success': False, 'error': str(e)}

    # ========================================
    # BDI Interface
    # ========================================

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for prime field tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['prime_field', 'gf_p', 'finite_field'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_prime_field_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_prime_field_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_prime_field_{task_id}',
                plan=['claim', 'solve', 'post'],
                priority=5,
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Run one action from plan."""
        action = intention.get_current_action()

        if action == 'claim':
            intention.advance()

        elif action == 'solve':
            task_entry = intention.metadata.get('task_entry')
            result = self.process(task_entry)
            intention.metadata['result'] = result
            intention.advance()

        elif action == 'post':
            result = intention.metadata.get('result')
            if self.blackboard and result:
                if hasattr(result, 'entry_type'):
                    self.blackboard.post(result)
            intention.complete()

    # ========================================
    # Statistics
    # ========================================

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return {
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'prime_fields_created': self.prime_fields_created,
            'elements_inverted': self.elements_inverted,
            'primitive_elements_found': self.primitive_elements_found,
            'order_computations': self.order_computations,
            'quadratic_residue_tests': self.quadratic_residue_tests,
        }
