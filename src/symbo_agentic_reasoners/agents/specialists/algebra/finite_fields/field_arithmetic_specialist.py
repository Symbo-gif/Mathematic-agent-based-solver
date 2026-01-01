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
FIELD ARITHMETIC SPECIALIST (Tier 3)
=====================================

Handles arithmetic operations in finite fields GF(p^n).

CAPABILITIES:
------------
- add: Field element addition (coefficient-wise mod p)
- multiply: Field element multiplication with reduction
- inverse: Multiplicative inverse via extended GCD
- power: Fast exponentiation
- discrete_log: Baby-step giant-step algorithm

FORMULATION:
-----------
Addition: (a + b) mod p for each coefficient
Multiplication: Polynomial multiplication followed by reduction mod f(x)
Inverse: Extended Euclidean algorithm for polynomials
Power: Square-and-multiply algorithm
Discrete Log: Baby-step giant-step O(sqrt(|G|))

ALGORITHMIC BACKING:
-------------------
- Extended GCD for polynomial inversion
- Square-and-multiply for exponentiation
- Baby-step giant-step for discrete log

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Shoup (2005), Chapter 11-12: Finite Field Arithmetic
- Lidl & Niederreiter (1997), Chapter 1: Finite Field Operations
"""

import logging
import math
from typing import Any, Dict, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.finite_fields import (
    GFpnElement, is_prime, polynomial_add, polynomial_multiply,
    polynomial_mod, polynomial_mult_mod
)

logger = logging.getLogger(__name__)


class FieldArithmeticSpecialist(BDIAgent):
    """
    Field Arithmetic Specialist - GF(p^n) Operations

    DIRECTIVE:
    ---------
    Handle arithmetic operations in extension fields GF(p^n).

    OPERATIONS:
    ----------
    - add: Coefficient-wise addition mod p
    - multiply: Polynomial multiplication with reduction
    - inverse: Extended GCD for polynomials
    - power: Fast exponentiation
    - discrete_log: Baby-step giant-step

    FORMULATION:
    -----------
    All operations performed in quotient ring GF(p)[x]/<f(x)>.
    Elements represented as polynomials of degree < n.

    REFERENCE:
    ---------
    - Shoup (2005), Computational Number Theory, Chapter 11
    """

    def __init__(
        self,
        agent_id: str = 'field_arithmetic_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Field Arithmetic Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.additions_performed = 0
        self.multiplications_performed = 0
        self.inversions_performed = 0
        self.exponentiations_performed = 0
        self.discrete_logs_solved = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.finite_fields.arithmetic',
            agent_id=self.agent_id,
            algorithm='field_arithmetic',
            cost='low',
            instance=self,
            type='specialist',
            tier='3',
            operations='add_multiply_inverse_power_dlog'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as field arithmetic specialist")

    # ========================================
    # Core Operations
    # ========================================

    def add_elements(
        self,
        a: List[int],
        b: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Add two field elements in GF(p^n).

        Coefficient-wise addition modulo p.

        Args:
            a: First element coefficients [a_0, a_1, ..., a_{n-1}]
            b: Second element coefficients
            p: Prime characteristic

        Returns:
            Sum a + b
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        try:
            result = polynomial_add(a, b, p)
            self.additions_performed += 1

            return {
                'success': True,
                'result': result,
                'operand_a': a,
                'operand_b': b,
                'characteristic': p,
                'method': 'coefficient_addition'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def subtract_elements(
        self,
        a: List[int],
        b: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Subtract two field elements: a - b in GF(p^n).

        Args:
            a: First element coefficients
            b: Second element coefficients
            p: Prime characteristic

        Returns:
            Difference a - b
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        try:
            # Negate b: -b = (p - b_i) for each coefficient
            neg_b = [(-c) % p for c in b]
            result = polynomial_add(a, neg_b, p)
            self.additions_performed += 1

            return {
                'success': True,
                'result': result,
                'operand_a': a,
                'operand_b': b,
                'characteristic': p,
                'method': 'coefficient_subtraction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def multiply_elements(
        self,
        a: List[int],
        b: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Multiply two field elements in GF(p^n).

        Polynomial multiplication followed by reduction modulo f(x).

        Args:
            a: First element coefficients
            b: Second element coefficients
            irred_poly: Irreducible polynomial defining field
            p: Prime characteristic

        Returns:
            Product a * b
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        try:
            result = polynomial_mult_mod(a, b, irred_poly, p)
            self.multiplications_performed += 1

            return {
                'success': True,
                'result': result,
                'operand_a': a,
                'operand_b': b,
                'irred_poly': irred_poly,
                'characteristic': p,
                'method': 'polynomial_multiplication_reduction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def invert_element(
        self,
        a: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Compute multiplicative inverse of element in GF(p^n).

        Uses extended GCD algorithm for polynomials.

        Args:
            a: Element coefficients (non-zero)
            irred_poly: Irreducible polynomial
            p: Prime characteristic

        Returns:
            Inverse a^(-1) such that a * a^(-1) = 1
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        # Check for zero element
        if not a or all(c == 0 for c in a):
            return {'success': False, 'error': 'Cannot invert zero element'}

        try:
            # Extended GCD: gcd(a, f) = 1 since f irreducible
            # Find u such that a*u ≡ 1 (mod f)
            inv = self._polynomial_extended_gcd_inverse(a, irred_poly, p)

            if inv is None:
                return {'success': False, 'error': 'Element has no inverse'}

            self.inversions_performed += 1

            # Verify: a * inv ≡ 1 (mod f)
            verification = polynomial_mult_mod(a, inv, irred_poly, p)

            return {
                'success': True,
                'inverse': inv,
                'element': a,
                'verification': verification == [1],
                'irred_poly': irred_poly,
                'method': 'extended_euclidean'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def power_element(
        self,
        a: List[int],
        exp: int,
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Compute a^exp in GF(p^n).

        Uses square-and-multiply algorithm.

        Args:
            a: Base element coefficients
            exp: Exponent (can be negative)
            irred_poly: Irreducible polynomial
            p: Prime characteristic

        Returns:
            Power a^exp
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        # Handle zero base
        if not a or all(c == 0 for c in a):
            if exp <= 0:
                return {'success': False, 'error': 'Zero to non-positive power undefined'}
            return {
                'success': True,
                'result': [0],
                'base': a,
                'exponent': exp,
                'method': 'zero_base'
            }

        try:
            # Handle negative exponent: a^(-n) = (a^(-1))^n
            if exp < 0:
                inv_result = self.invert_element(a, irred_poly, p)
                if not inv_result['success']:
                    return inv_result
                a = inv_result['inverse']
                exp = -exp

            # Handle exp = 0
            if exp == 0:
                return {
                    'success': True,
                    'result': [1],
                    'base': a,
                    'exponent': 0,
                    'method': 'identity'
                }

            # Square-and-multiply
            result = self._square_and_multiply(a, exp, irred_poly, p)
            self.exponentiations_performed += 1

            return {
                'success': True,
                'result': result,
                'base': a,
                'exponent': exp,
                'irred_poly': irred_poly,
                'method': 'square_and_multiply'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def discrete_log(
        self,
        elem: List[int],
        base: List[int],
        irred_poly: List[int],
        p: int,
        order: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compute discrete logarithm: find x such that base^x = elem.

        Uses baby-step giant-step algorithm with O(sqrt(n)) time and space.

        Args:
            elem: Target element
            base: Generator/base element
            irred_poly: Irreducible polynomial
            p: Prime characteristic
            order: Known order of base (optional, computes if not given)

        Returns:
            Discrete log x
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        # Check for trivial cases
        if not elem or all(c == 0 for c in elem):
            return {'success': False, 'error': 'Cannot compute log of zero'}

        if not base or all(c == 0 for c in base):
            return {'success': False, 'error': 'Base cannot be zero'}

        try:
            n = len(irred_poly) - 1  # Extension degree

            # Default order is group order p^n - 1
            if order is None:
                order = p ** n - 1

            # Security limit
            if order > 10**12:
                return {
                    'success': False,
                    'error': 'Order too large for discrete log computation'
                }

            # Baby-step giant-step
            m = int(math.ceil(math.sqrt(order)))

            # Baby steps: build table of base^j for j = 0, 1, ..., m-1
            baby_steps = {}
            current = [1]  # Identity

            for j in range(m):
                key = tuple(current)
                if key not in baby_steps:
                    baby_steps[key] = j
                current = polynomial_mult_mod(current, base, irred_poly, p)

            # Compute base^(-m)
            base_m = self._square_and_multiply(base, m, irred_poly, p)
            base_neg_m = self._polynomial_extended_gcd_inverse(base_m, irred_poly, p)

            if base_neg_m is None:
                return {'success': False, 'error': 'Could not compute inverse for BSGS'}

            # Giant steps: check elem * base^(-im) for i = 0, 1, ..., m-1
            gamma = list(elem)
            for i in range(m):
                key = tuple(gamma)
                if key in baby_steps:
                    j = baby_steps[key]
                    x = i * m + j

                    self.discrete_logs_solved += 1

                    return {
                        'success': True,
                        'discrete_log': x,
                        'element': elem,
                        'base': base,
                        'verification_power': x,
                        'method': 'baby_step_giant_step'
                    }

                gamma = polynomial_mult_mod(gamma, base_neg_m, irred_poly, p)

            return {
                'success': False,
                'error': 'Discrete log not found (element not in subgroup?)'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def element_order(
        self,
        a: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Compute multiplicative order of element in GF(p^n)*.

        Order is smallest positive k such that a^k = 1.

        Args:
            a: Element coefficients
            irred_poly: Irreducible polynomial
            p: Prime characteristic

        Returns:
            Multiplicative order
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not a or all(c == 0 for c in a):
            return {'success': False, 'error': 'Zero element has no order'}

        try:
            n = len(irred_poly) - 1
            group_order = p ** n - 1

            # Get divisors of group order
            divisors = self._get_divisors(group_order)

            for d in sorted(divisors):
                power = self._square_and_multiply(a, d, irred_poly, p)
                if power == [1]:
                    return {
                        'success': True,
                        'order': d,
                        'element': a,
                        'group_order': group_order,
                        'is_primitive': d == group_order,
                        'method': 'divisor_search'
                    }

            return {
                'success': True,
                'order': group_order,
                'element': a,
                'group_order': group_order,
                'is_primitive': True,
                'method': 'divisor_search'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Helper Methods
    # ========================================

    def _square_and_multiply(
        self,
        base: List[int],
        exp: int,
        irred_poly: List[int],
        p: int
    ) -> List[int]:
        """Square-and-multiply exponentiation."""
        if exp == 0:
            return [1]

        result = [1]
        current = list(base)

        while exp > 0:
            if exp & 1:
                result = polynomial_mult_mod(result, current, irred_poly, p)
            current = polynomial_mult_mod(current, current, irred_poly, p)
            exp >>= 1

        return result

    def _polynomial_extended_gcd_inverse(
        self,
        a: List[int],
        f: List[int],
        p: int
    ) -> Optional[List[int]]:
        """
        Compute inverse of a modulo f using extended GCD.

        Returns u such that a*u ≡ 1 (mod f).
        """
        # Extended Euclidean algorithm for polynomials
        r_prev, r_curr = list(f), list(a)
        s_prev, s_curr = [0], [1]

        while r_curr and not all(c == 0 for c in r_curr):
            # Compute quotient and remainder
            q, r_next = self._polynomial_divmod(r_prev, r_curr, p)

            # Update
            s_next = polynomial_add(
                s_prev,
                [(-c) % p for c in polynomial_multiply(q, s_curr, p)],
                p
            )

            r_prev, r_curr = r_curr, r_next
            s_prev, s_curr = s_curr, s_next

        # r_prev should be constant (gcd = 1 for irreducible f)
        while r_prev and r_prev[-1] == 0:
            r_prev.pop()

        if len(r_prev) != 1 or r_prev[0] == 0:
            return None

        # Normalize: inverse = s_prev / r_prev[0]
        gcd_inv = pow(r_prev[0], p - 2, p)
        inverse = [(c * gcd_inv) % p for c in s_prev]

        # Reduce modulo f
        inverse = polynomial_mod(inverse, f, p)

        return inverse

    def _polynomial_divmod(
        self,
        dividend: List[int],
        divisor: List[int],
        p: int
    ) -> tuple:
        """Polynomial division with quotient and remainder."""
        if not divisor or all(c == 0 for c in divisor):
            raise ValueError("Division by zero polynomial")

        # Normalize
        while divisor and divisor[-1] == 0:
            divisor.pop()
        while dividend and dividend[-1] == 0:
            dividend.pop()

        if not dividend:
            return [0], [0]

        if len(dividend) < len(divisor):
            return [0], list(dividend)

        dividend = list(dividend)
        divisor_degree = len(divisor) - 1
        dividend_degree = len(dividend) - 1

        quotient = [0] * (dividend_degree - divisor_degree + 1)
        divisor_lead_inv = pow(divisor[-1], p - 2, p)

        for i in range(dividend_degree, divisor_degree - 1, -1):
            if dividend[i] != 0:
                coeff = (dividend[i] * divisor_lead_inv) % p
                quotient[i - divisor_degree] = coeff
                for j in range(divisor_degree + 1):
                    dividend[i - divisor_degree + j] = (
                        dividend[i - divisor_degree + j] - coeff * divisor[j]
                    ) % p

        # Clean up
        while quotient and quotient[-1] == 0:
            quotient.pop()
        while dividend and dividend[-1] == 0:
            dividend.pop()

        return quotient if quotient else [0], dividend if dividend else [0]

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
        """Process field arithmetic task."""
        self.tasks_executed += 1

        try:
            # Extract metadata
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'multiply')
            a = metadata.get('a') or metadata.get('element_a')
            b = metadata.get('b') or metadata.get('element_b')
            elem = metadata.get('elem') or metadata.get('element') or a
            base = metadata.get('base')
            exp = metadata.get('exp') or metadata.get('exponent')
            p = metadata.get('p') or metadata.get('characteristic')
            irred_poly = metadata.get('irred_poly') or metadata.get('irreducible')

            # Route to appropriate method
            if operation in ['add', 'addition', 'sum']:
                result = self.add_elements(a, b, p)
            elif operation in ['subtract', 'subtraction', 'difference']:
                result = self.subtract_elements(a, b, p)
            elif operation in ['multiply', 'multiplication', 'product']:
                result = self.multiply_elements(a, b, irred_poly, p)
            elif operation in ['inverse', 'invert']:
                result = self.invert_element(elem, irred_poly, p)
            elif operation in ['power', 'exponent', 'exp']:
                result = self.power_element(elem, exp, irred_poly, p)
            elif operation in ['discrete_log', 'dlog', 'log']:
                result = self.discrete_log(elem, base, irred_poly, p)
            elif operation in ['order', 'element_order']:
                result = self.element_order(elem, irred_poly, p)
            else:
                result = {'success': False, 'error': f'Unknown operation: {operation}'}

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
                    ['finite_field', 'arithmetic', 'gf_pn'],
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
        """PERCEIVE: Monitor blackboard for arithmetic tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['field_arithmetic', 'gf_arithmetic', 'field_operation'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_arith_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_arith_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_arith_{task_id}',
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
            if self.blackboard and result and hasattr(result, 'entry_type'):
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
            'additions_performed': self.additions_performed,
            'multiplications_performed': self.multiplications_performed,
            'inversions_performed': self.inversions_performed,
            'exponentiations_performed': self.exponentiations_performed,
            'discrete_logs_solved': self.discrete_logs_solved,
        }
