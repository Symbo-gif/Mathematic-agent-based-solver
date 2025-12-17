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
MODULAR ARITHMETIC SPECIALIST (Tier 3)
======================================

Native Python implementation for modular arithmetic operations.
Foundation for cryptographic computations.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import math
import random
from typing import Dict, Any, List, Optional, Tuple

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class ModularArithmeticSpecialist(BDIAgent):
    """
    Specialist for modular arithmetic computations.

    Capabilities:
    - Modular exponentiation (fast)
    - Extended Euclidean algorithm
    - Modular inverse
    - Chinese Remainder Theorem
    - Primitive roots
    - Discrete logarithm (baby-step giant-step)
    - Miller-Rabin primality test
    """

    def __init__(self, agent_id: str = 'modular_arithmetic_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.cryptography.modular',
                agent_id=agent_id,
                algorithm='native_modular_arithmetic',
                cost='low',
                instance=self,
                tier='3',
                capabilities='mod_exp_inverse_crt_primality'
            ))

        logger.info(f"[{agent_id}] Modular Arithmetic Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for modular arithmetic tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['modular'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['mod_arithmetic'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create modular computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'mod_exp')

            steps = ['claim_task', 'compute_modular', 'post_result']
            intention = Intention(
                plan_id=f'modular_{operation}_{task_id}',
                steps=steps,
                target_desire='modular_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute modular operations."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_modular':
            self._compute_modular(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_modular(self, intention: Intention):
        """Compute the requested modular operation."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'mod_exp')

        try:
            if operation == 'mod_exp':
                base = metadata.get('base', 2)
                exp = metadata.get('exponent', 10)
                mod = metadata.get('modulus', 1000)
                result = self.modular_exponentiation(base, exp, mod)
            elif operation == 'mod_inverse':
                a = metadata.get('a', 3)
                m = metadata.get('modulus', 11)
                result = self.modular_inverse(a, m)
            elif operation == 'extended_gcd':
                a = metadata.get('a', 0)
                b = metadata.get('b', 0)
                result = self.extended_gcd(a, b)
            elif operation == 'crt':
                remainders = metadata.get('remainders', [])
                moduli = metadata.get('moduli', [])
                result = self.chinese_remainder_theorem(remainders, moduli)
            elif operation == 'primitive_root':
                p = metadata.get('prime', 7)
                result = self.find_primitive_root(p)
            elif operation == 'discrete_log':
                g = metadata.get('base', 2)
                h = metadata.get('value', 8)
                p = metadata.get('modulus', 11)
                result = self.discrete_logarithm_bsgs(g, h, p)
            elif operation == 'is_prime':
                n = metadata.get('n', 17)
                result = self.is_prime_miller_rabin(n)
            elif operation == 'euler_totient':
                n = metadata.get('n', 12)
                result = self.euler_totient(n)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Modular computation failed: {e}")
            intention.metadata['result'] = {'error': str(e)}
            intention.advance()

    def _post_result(self, intention: Intention):
        """Post result to blackboard."""
        if self.blackboard:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            task = intention.metadata.get('task_entry')
            result = intention.metadata.get('result', {})

            result_entry = create_entry(
                content=result,
                entry_type=EntryType.RESULT,
                tags=['modular', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # MODULAR EXPONENTIATION
    # =========================================================================

    @staticmethod
    def modular_exponentiation(base: int, exp: int, mod: int) -> Dict[str, Any]:
        """
        Compute base^exp mod mod using fast exponentiation (square-and-multiply).

        Args:
            base: Base value
            exp: Exponent (non-negative)
            mod: Modulus (positive)

        Returns:
            Dictionary with result
        """
        if mod <= 0:
            return {'error': 'Modulus must be positive'}
        if exp < 0:
            return {'error': 'Exponent must be non-negative'}

        if mod == 1:
            return {'result': 0, 'method': 'native_mod_exp'}

        result = 1
        base = base % mod

        while exp > 0:
            if exp & 1:  # If exp is odd
                result = (result * base) % mod
            exp >>= 1  # exp = exp // 2
            base = (base * base) % mod

        return {
            'result': result,
            'method': 'native_mod_exp'
        }

    # =========================================================================
    # EXTENDED EUCLIDEAN ALGORITHM
    # =========================================================================

    @staticmethod
    def extended_gcd(a: int, b: int) -> Dict[str, Any]:
        """
        Extended Euclidean algorithm.

        Finds gcd(a, b) and coefficients x, y such that ax + by = gcd(a, b).

        Args:
            a, b: Input integers

        Returns:
            Dictionary with gcd and Bezout coefficients
        """
        if a == 0 and b == 0:
            return {'gcd': 0, 'x': 0, 'y': 0, 'method': 'native_extended_gcd'}

        old_r, r = abs(a), abs(b)
        old_s, s = 1, 0
        old_t, t = 0, 1

        while r != 0:
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t

        # Adjust signs
        if a < 0:
            old_s = -old_s
        if b < 0:
            old_t = -old_t

        return {
            'gcd': old_r,
            'x': old_s,  # Coefficient for a
            'y': old_t,  # Coefficient for b
            'method': 'native_extended_gcd'
        }

    # =========================================================================
    # MODULAR INVERSE
    # =========================================================================

    @staticmethod
    def modular_inverse(a: int, m: int) -> Dict[str, Any]:
        """
        Compute modular inverse of a mod m.

        Args:
            a: Value to invert
            m: Modulus

        Returns:
            Dictionary with inverse (if exists) or error
        """
        if m <= 0:
            return {'error': 'Modulus must be positive'}

        a = a % m

        result = ModularArithmeticSpecialist.extended_gcd(a, m)
        gcd = result['gcd']

        if gcd != 1:
            return {
                'error': f'Inverse does not exist: gcd({a}, {m}) = {gcd} != 1',
                'gcd': gcd
            }

        inverse = result['x'] % m
        return {
            'inverse': inverse,
            'a': a,
            'modulus': m,
            'verification': (a * inverse) % m,
            'method': 'native_mod_inverse'
        }

    # =========================================================================
    # CHINESE REMAINDER THEOREM
    # =========================================================================

    @staticmethod
    def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Dict[str, Any]:
        """
        Solve system of congruences using CRT.

        x ≡ r_i (mod m_i) for all i

        Args:
            remainders: List of remainders r_i
            moduli: List of moduli m_i (must be pairwise coprime)

        Returns:
            Dictionary with solution
        """
        if len(remainders) != len(moduli):
            return {'error': 'Remainders and moduli must have same length'}

        if len(remainders) == 0:
            return {'error': 'Empty input'}

        # Check pairwise coprimality
        for i in range(len(moduli)):
            for j in range(i + 1, len(moduli)):
                gcd_result = ModularArithmeticSpecialist.extended_gcd(moduli[i], moduli[j])
                if gcd_result['gcd'] != 1:
                    return {
                        'error': f'Moduli {moduli[i]} and {moduli[j]} are not coprime'
                    }

        M = 1
        for m in moduli:
            M *= m

        x = 0
        for r, m in zip(remainders, moduli):
            M_i = M // m
            inv_result = ModularArithmeticSpecialist.modular_inverse(M_i, m)
            if 'error' in inv_result:
                return inv_result
            y_i = inv_result['inverse']
            x += r * M_i * y_i

        x = x % M

        return {
            'solution': x,
            'modulus': M,
            'method': 'native_crt'
        }

    # =========================================================================
    # EULER'S TOTIENT FUNCTION
    # =========================================================================

    @staticmethod
    def euler_totient(n: int) -> Dict[str, Any]:
        """
        Compute Euler's totient function phi(n).

        Args:
            n: Input integer (positive)

        Returns:
            Dictionary with totient value
        """
        if n <= 0:
            return {'error': 'Input must be positive'}

        if n == 1:
            return {'phi': 1, 'n': 1, 'method': 'native_totient'}

        result = n
        temp_n = n

        # Factor out 2s
        if temp_n % 2 == 0:
            result -= result // 2
            while temp_n % 2 == 0:
                temp_n //= 2

        # Check odd factors
        p = 3
        while p * p <= temp_n:
            if temp_n % p == 0:
                result -= result // p
                while temp_n % p == 0:
                    temp_n //= p
            p += 2

        # If temp_n is still greater than 1, it's a prime factor
        if temp_n > 1:
            result -= result // temp_n

        return {
            'phi': result,
            'n': n,
            'method': 'native_totient'
        }

    # =========================================================================
    # PRIMITIVE ROOT
    # =========================================================================

    @staticmethod
    def find_primitive_root(p: int) -> Dict[str, Any]:
        """
        Find a primitive root modulo p (p must be prime).

        Args:
            p: Prime modulus

        Returns:
            Dictionary with primitive root
        """
        if p < 2:
            return {'error': 'p must be at least 2'}

        if p == 2:
            return {'primitive_root': 1, 'prime': 2, 'method': 'native_primitive_root'}

        # Verify p is prime (quick check)
        prime_check = ModularArithmeticSpecialist.is_prime_miller_rabin(p)
        if not prime_check.get('is_prime', False):
            return {'error': f'{p} is not prime'}

        # phi(p) = p - 1 for prime p
        phi = p - 1

        # Find prime factors of phi
        factors = []
        n = phi
        d = 2
        while d * d <= n:
            if n % d == 0:
                factors.append(d)
                while n % d == 0:
                    n //= d
            d += 1
        if n > 1:
            factors.append(n)

        # Search for primitive root
        for g in range(2, p):
            is_primitive = True
            for factor in factors:
                exp_result = ModularArithmeticSpecialist.modular_exponentiation(g, phi // factor, p)
                if exp_result['result'] == 1:
                    is_primitive = False
                    break
            if is_primitive:
                return {
                    'primitive_root': g,
                    'prime': p,
                    'order': phi,
                    'method': 'native_primitive_root'
                }

        return {'error': 'No primitive root found'}

    # =========================================================================
    # DISCRETE LOGARITHM (Baby-step Giant-step)
    # =========================================================================

    @staticmethod
    def discrete_logarithm_bsgs(g: int, h: int, p: int) -> Dict[str, Any]:
        """
        Solve g^x ≡ h (mod p) using Baby-step Giant-step algorithm.

        Args:
            g: Base (generator)
            h: Value
            p: Prime modulus

        Returns:
            Dictionary with discrete logarithm x
        """
        if p <= 1:
            return {'error': 'Modulus must be > 1'}

        # Order is at most p-1 for prime p
        n = math.isqrt(p - 1) + 1

        # Baby step: compute g^j for j = 0, 1, ..., n-1
        baby_steps = {}
        power = 1
        for j in range(n):
            baby_steps[power] = j
            power = (power * g) % p

        # Compute g^(-n)
        inv_result = ModularArithmeticSpecialist.modular_inverse(power, p)
        if 'error' in inv_result:
            return inv_result
        g_inv_n = inv_result['inverse']

        # Giant step: check h * (g^-n)^i for i = 0, 1, ..., n-1
        gamma = h
        for i in range(n):
            if gamma in baby_steps:
                x = i * n + baby_steps[gamma]
                # Verify
                exp_result = ModularArithmeticSpecialist.modular_exponentiation(g, x, p)
                if exp_result['result'] == h % p:
                    return {
                        'discrete_log': x,
                        'base': g,
                        'value': h,
                        'modulus': p,
                        'method': 'native_bsgs'
                    }
            gamma = (gamma * g_inv_n) % p

        return {'error': 'No solution found (h may not be in subgroup generated by g)'}

    # =========================================================================
    # MILLER-RABIN PRIMALITY TEST
    # =========================================================================

    @staticmethod
    def is_prime_miller_rabin(n: int, k: int = 20) -> Dict[str, Any]:
        """
        Miller-Rabin probabilistic primality test.

        Args:
            n: Number to test
            k: Number of rounds (accuracy parameter)

        Returns:
            Dictionary with primality result
        """
        if n < 2:
            return {'is_prime': False, 'n': n, 'method': 'native_miller_rabin'}
        if n == 2:
            return {'is_prime': True, 'n': n, 'method': 'native_miller_rabin'}
        if n % 2 == 0:
            return {'is_prime': False, 'n': n, 'method': 'native_miller_rabin'}

        # Write n-1 = 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Deterministic witnesses for small n
        if n < 2047:
            witnesses = [2]
        elif n < 1373653:
            witnesses = [2, 3]
        elif n < 9080191:
            witnesses = [31, 73]
        elif n < 25326001:
            witnesses = [2, 3, 5]
        elif n < 3215031751:
            witnesses = [2, 3, 5, 7]
        else:
            # Use random witnesses
            witnesses = [random.randrange(2, n - 1) for _ in range(k)]

        for a in witnesses:
            if a >= n:
                continue

            exp_result = ModularArithmeticSpecialist.modular_exponentiation(a, d, n)
            x = exp_result['result']

            if x == 1 or x == n - 1:
                continue

            composite = True
            for _ in range(r - 1):
                x = (x * x) % n
                if x == n - 1:
                    composite = False
                    break

            if composite:
                return {'is_prime': False, 'n': n, 'method': 'native_miller_rabin'}

        return {'is_prime': True, 'n': n, 'method': 'native_miller_rabin', 'confidence': 'high'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'mod_exp', 'mod_inverse', 'extended_gcd', 'crt',
                'primitive_root', 'discrete_log', 'is_prime', 'euler_totient'
            ]
        }
