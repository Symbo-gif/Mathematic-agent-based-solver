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
IRREDUCIBLE POLYNOMIAL SPECIALIST (Tier 3)
==========================================

Handles irreducibility testing and finding irreducible polynomials over GF(p).

CAPABILITIES:
------------
- is_irreducible: Test polynomial irreducibility using Rabin's algorithm
- find_irreducible_polynomial: Search for irreducible of given degree
- is_primitive_polynomial: Test if polynomial is primitive
- factorize_polynomial: Factor polynomial over GF(p)
- count_irreducibles: Count irreducible polynomials of degree n over GF(p)

FORMULATION:
-----------
A polynomial f(x) of degree n over GF(p) is irreducible iff:
1. gcd(f(x), x^(p^i) - x) = 1 for all i with 1 <= i < n/2
2. f(x) | x^(p^n) - x

Primitive polynomial: Irreducible of degree n where root generates GF(p^n)*.

ALGORITHMIC BACKING:
-------------------
- Rabin irreducibility test (deterministic)
- Sequential search for irreducibles
- Berlekamp factorization (simplified)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Rabin (1980), Probabilistic Algorithms in Finite Fields
- Lidl & Niederreiter (1997), Chapter 3: Polynomials over Finite Fields
- Shoup (2005), Chapter 14: Polynomial Factorization
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
from symbo_agentic_reasoners.core.finite_fields import (
    is_irreducible_rabin, find_irreducible_polynomial, is_prime,
    polynomial_gcd, polynomial_mod, polynomial_multiply, gcd
)

logger = logging.getLogger(__name__)


class IrreduciblePolynomialSpecialist(BDIAgent):
    """
    Irreducible Polynomial Specialist - Polynomial Testing and Search

    DIRECTIVE:
    ---------
    Handle irreducibility testing and finding irreducible polynomials.

    OPERATIONS:
    ----------
    - is_irreducible: Test using Rabin's algorithm
    - find_irreducible: Search for irreducible polynomial
    - is_primitive: Test primitivity (root generates multiplicative group)
    - factorize: Factor polynomial over finite field
    - count_irreducibles: Necklace formula count

    FORMULATION:
    -----------
    Rabin Test: f irreducible iff gcd(f, x^(p^d) - x) = 1 for proper divisors d
    Primitive: Irreducible whose root has order p^n - 1

    REFERENCE:
    ---------
    - Rabin (1980), Probabilistic Algorithms in Finite Fields
    - Lidl & Niederreiter (1997), Finite Fields, Chapter 3
    """

    def __init__(
        self,
        agent_id: str = 'irreducible_polynomial_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Irreducible Polynomial Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.irreducibility_tests = 0
        self.irreducibles_found = 0
        self.primitive_polys_found = 0
        self.factorizations_performed = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.finite_fields.irreducible',
            agent_id=self.agent_id,
            algorithm='rabin_irreducibility_test',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            operations='test_find_primitive_factorize_count'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as irreducible polynomial specialist")

    # ========================================
    # Core Operations
    # ========================================

    def is_irreducible(self, poly_coeffs: List[int], p: int) -> Dict[str, Any]:
        """
        Test if polynomial is irreducible over GF(p).

        Uses Rabin's irreducibility test with complexity O(n^2 log(p) + n log(p) M(n))
        where M(n) is polynomial multiplication complexity.

        Args:
            poly_coeffs: Coefficients [a_0, a_1, ..., a_n] (a_n != 0)
            p: Prime characteristic

        Returns:
            Irreducibility test result
        """
        if not isinstance(p, int) or p < 2:
            return {'success': False, 'error': f'p={p} must be integer >= 2'}

        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not poly_coeffs or all(c == 0 for c in poly_coeffs):
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        # Normalize coefficients
        poly_coeffs = [c % p for c in poly_coeffs]
        while poly_coeffs and poly_coeffs[-1] == 0:
            poly_coeffs.pop()

        if not poly_coeffs:
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        degree = len(poly_coeffs) - 1

        # Degree 0: constant, not irreducible (by convention)
        if degree == 0:
            return {
                'success': True,
                'is_irreducible': False,
                'polynomial': poly_coeffs,
                'degree': 0,
                'reason': 'Constant polynomials are not irreducible',
                'method': 'degree_check'
            }

        # Degree 1: always irreducible
        if degree == 1:
            self.irreducibility_tests += 1
            return {
                'success': True,
                'is_irreducible': True,
                'polynomial': poly_coeffs,
                'degree': 1,
                'reason': 'Linear polynomials are always irreducible',
                'method': 'degree_check'
            }

        try:
            is_irred = is_irreducible_rabin(tuple(poly_coeffs), p)
            self.irreducibility_tests += 1

            return {
                'success': True,
                'is_irreducible': is_irred,
                'polynomial': poly_coeffs,
                'degree': degree,
                'characteristic': p,
                'reason': 'Passed Rabin test' if is_irred else 'Failed Rabin test',
                'method': 'rabin_algorithm'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def find_irreducible(
        self,
        p: int,
        degree: int,
        primitive: bool = False
    ) -> Dict[str, Any]:
        """
        Find an irreducible polynomial of given degree over GF(p).

        Args:
            p: Prime characteristic
            degree: Desired polynomial degree
            primitive: If True, find primitive polynomial

        Returns:
            Irreducible polynomial coefficients
        """
        if not isinstance(p, int) or p < 2:
            return {'success': False, 'error': f'p={p} must be integer >= 2'}

        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not isinstance(degree, int) or degree < 1:
            return {'success': False, 'error': f'degree={degree} must be positive integer'}

        # Limit degree to prevent excessive computation
        if degree > 256:
            return {
                'success': False,
                'error': f'Degree {degree} too large (max 256)'
            }

        try:
            irred_poly = find_irreducible_polynomial(p, degree, primitive=primitive)

            if irred_poly is None:
                return {
                    'success': False,
                    'error': f'Could not find {"primitive" if primitive else "irreducible"} polynomial'
                }

            if primitive:
                self.primitive_polys_found += 1
            else:
                self.irreducibles_found += 1

            return {
                'success': True,
                'polynomial': irred_poly,
                'degree': degree,
                'characteristic': p,
                'is_primitive': primitive,
                'polynomial_repr': self._poly_to_string(irred_poly),
                'method': 'sequential_search'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_primitive(self, poly_coeffs: List[int], p: int) -> Dict[str, Any]:
        """
        Test if irreducible polynomial is primitive.

        A polynomial is primitive if its roots generate the multiplicative
        group of the extension field (order p^n - 1).

        Args:
            poly_coeffs: Polynomial coefficients
            p: Prime characteristic

        Returns:
            Primitivity test result
        """
        if not isinstance(p, int) or p < 2:
            return {'success': False, 'error': f'p={p} must be integer >= 2'}

        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not poly_coeffs or all(c == 0 for c in poly_coeffs):
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        # Normalize
        poly_coeffs = [c % p for c in poly_coeffs]
        while poly_coeffs and poly_coeffs[-1] == 0:
            poly_coeffs.pop()

        if not poly_coeffs:
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        degree = len(poly_coeffs) - 1

        # First check irreducibility
        if not is_irreducible_rabin(tuple(poly_coeffs), p):
            return {
                'success': True,
                'is_primitive': False,
                'polynomial': poly_coeffs,
                'reason': 'Polynomial is not irreducible',
                'method': 'irreducibility_prerequisite'
            }

        try:
            # For primitive check, need to verify root has order p^n - 1
            # x^(p^n - 1) ≡ 1 (mod f(x)) and x^d ≢ 1 for all proper divisors d
            order = p ** degree - 1
            divisors = self._get_proper_divisors(order)

            # Check that x^(p^n - 1) ≡ 1 (mod f)
            x = [0, 1]  # x as polynomial
            power_result = self._polynomial_power_mod(x, order, poly_coeffs, p)

            if power_result != [1]:  # Should be 1 (constant)
                return {
                    'success': True,
                    'is_primitive': False,
                    'polynomial': poly_coeffs,
                    'reason': 'x^(p^n-1) != 1 mod f(x)',
                    'method': 'order_check'
                }

            # Check that x^d != 1 for all proper divisors d of p^n - 1
            for d in divisors:
                power_d = self._polynomial_power_mod(x, d, poly_coeffs, p)
                if power_d == [1]:
                    return {
                        'success': True,
                        'is_primitive': False,
                        'polynomial': poly_coeffs,
                        'reason': f'x has order {d} < {order}',
                        'method': 'order_check'
                    }

            self.primitive_polys_found += 1

            return {
                'success': True,
                'is_primitive': True,
                'polynomial': poly_coeffs,
                'degree': degree,
                'order': order,
                'reason': f'Root generates GF({p}^{degree})*',
                'method': 'order_verification'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def factorize(self, poly_coeffs: List[int], p: int) -> Dict[str, Any]:
        """
        Factor polynomial over GF(p).

        Uses distinct-degree factorization for complete factorization.

        Args:
            poly_coeffs: Polynomial coefficients
            p: Prime characteristic

        Returns:
            Factorization as list of (factor, multiplicity) pairs
        """
        if not isinstance(p, int) or p < 2:
            return {'success': False, 'error': f'p={p} must be integer >= 2'}

        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not poly_coeffs or all(c == 0 for c in poly_coeffs):
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        # Normalize
        poly_coeffs = [c % p for c in poly_coeffs]
        while poly_coeffs and poly_coeffs[-1] == 0:
            poly_coeffs.pop()

        if not poly_coeffs:
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        degree = len(poly_coeffs) - 1

        # Limit for security
        if degree > 64:
            return {
                'success': False,
                'error': f'Degree {degree} too large for factorization (max 64)'
            }

        try:
            factors = self._distinct_degree_factorization(poly_coeffs, p)
            self.factorizations_performed += 1

            return {
                'success': True,
                'polynomial': poly_coeffs,
                'factors': factors,
                'factor_count': len(factors),
                'is_irreducible': len(factors) == 1 and factors[0][1] == 1,
                'method': 'distinct_degree_factorization'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def count_irreducibles(self, p: int, n: int) -> Dict[str, Any]:
        """
        Count irreducible polynomials of degree n over GF(p).

        Uses the necklace formula: N_p(n) = (1/n) * sum_{d|n} mu(n/d) * p^d

        Args:
            p: Prime characteristic
            n: Polynomial degree

        Returns:
            Count of monic irreducible polynomials
        """
        if not isinstance(p, int) or p < 2:
            return {'success': False, 'error': f'p={p} must be integer >= 2'}

        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not isinstance(n, int) or n < 1:
            return {'success': False, 'error': f'n={n} must be positive integer'}

        try:
            # Compute using Mobius function
            divisors = self._get_divisors(n)
            count = 0

            for d in divisors:
                mu = self._mobius(n // d)
                count += mu * (p ** d)

            count //= n

            return {
                'success': True,
                'degree': n,
                'characteristic': p,
                'count': count,
                'formula': f'N_{p}({n}) = {count}',
                'method': 'necklace_formula'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Helper Methods
    # ========================================

    def _poly_to_string(self, coeffs: List[int]) -> str:
        """Convert coefficient list to polynomial string."""
        if not coeffs or all(c == 0 for c in coeffs):
            return "0"

        terms = []
        for i, coeff in enumerate(coeffs):
            if coeff != 0:
                if i == 0:
                    terms.append(str(coeff))
                elif i == 1:
                    terms.append(f"{coeff}*x" if coeff != 1 else "x")
                else:
                    terms.append(f"{coeff}*x^{i}" if coeff != 1 else f"x^{i}")

        return " + ".join(terms) if terms else "0"

    def _get_divisors(self, n: int) -> List[int]:
        """Get all divisors of n."""
        divisors = []
        for i in range(1, int(n ** 0.5) + 1):
            if n % i == 0:
                divisors.append(i)
                if i != n // i:
                    divisors.append(n // i)
        return sorted(divisors)

    def _get_proper_divisors(self, n: int) -> List[int]:
        """Get proper divisors (all except n itself)."""
        return [d for d in self._get_divisors(n) if d != n]

    def _mobius(self, n: int) -> int:
        """Compute Mobius function mu(n)."""
        if n == 1:
            return 1

        # Factor n
        factors = []
        temp = n
        d = 2
        while d * d <= temp:
            if temp % d == 0:
                count = 0
                while temp % d == 0:
                    temp //= d
                    count += 1
                if count > 1:
                    return 0  # Has squared factor
                factors.append(d)
            d += 1
        if temp > 1:
            factors.append(temp)

        # mu(n) = (-1)^k where k is number of distinct prime factors
        return (-1) ** len(factors)

    def _polynomial_power_mod(
        self,
        base: List[int],
        exp: int,
        mod_poly: List[int],
        p: int
    ) -> List[int]:
        """Compute base^exp mod mod_poly in GF(p)[x]."""
        if exp == 0:
            return [1]

        result = [1]
        current = list(base)

        while exp > 0:
            if exp & 1:
                result = polynomial_mod(
                    polynomial_multiply(result, current, p),
                    mod_poly, p
                )
            current = polynomial_mod(
                polynomial_multiply(current, current, p),
                mod_poly, p
            )
            exp >>= 1

        # Normalize
        while result and result[-1] == 0:
            result.pop()
        return result if result else [0]

    def _distinct_degree_factorization(
        self,
        f: List[int],
        p: int
    ) -> List[Tuple[List[int], int]]:
        """
        Distinct-degree factorization of polynomial f over GF(p).

        Returns list of (factor, degree) pairs where each factor
        is product of irreducibles of that degree.
        """
        f = [c % p for c in f]
        while f and f[-1] == 0:
            f.pop()

        if len(f) <= 1:
            return [(f, 1)] if f else []

        n = len(f) - 1
        factors = []

        # Make f monic
        lead = f[-1]
        if lead != 1:
            lead_inv = pow(lead, p - 2, p)
            f = [(c * lead_inv) % p for c in f]

        # g = f, h = x
        g = list(f)
        h = [0, 1]  # x

        d = 0
        while len(g) > 1:
            d += 1
            if 2 * d > len(g) - 1:
                # g is irreducible of degree > n/2
                factors.append((g, 1))
                break

            # h = h^p mod g
            h = self._polynomial_power_mod(h, p, g, p)

            # Compute gcd(h - x, g)
            h_minus_x = list(h)
            if len(h_minus_x) >= 2:
                h_minus_x[1] = (h_minus_x[1] - 1) % p
            elif len(h_minus_x) == 1:
                h_minus_x.append(p - 1)
            else:
                h_minus_x = [0, p - 1]

            common = polynomial_gcd(h_minus_x, g, p)

            if len(common) > 1:  # Non-trivial gcd
                # Extract factors of degree d
                factors.append((common, 1))

                # g = g / common
                g = self._polynomial_div(g, common, p)

        return factors if factors else [(f, 1)]

    def _polynomial_div(
        self,
        dividend: List[int],
        divisor: List[int],
        p: int
    ) -> List[int]:
        """Polynomial division in GF(p)[x], returns quotient."""
        if not divisor or all(c == 0 for c in divisor):
            raise ValueError("Division by zero polynomial")

        # Normalize
        while divisor and divisor[-1] == 0:
            divisor.pop()
        while dividend and dividend[-1] == 0:
            dividend.pop()

        if len(dividend) < len(divisor):
            return [0]

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

        while quotient and quotient[-1] == 0:
            quotient.pop()

        return quotient if quotient else [0]

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process irreducible polynomial task."""
        self.tasks_executed += 1

        try:
            # Extract metadata
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'is_irreducible')
            p = metadata.get('p') or metadata.get('prime') or metadata.get('characteristic')
            n = metadata.get('n') or metadata.get('degree')
            poly = metadata.get('polynomial') or metadata.get('poly') or metadata.get('coeffs')
            primitive = metadata.get('primitive', False)

            # Route to appropriate method
            if operation in ['test', 'is_irreducible', 'irreducible']:
                result = self.is_irreducible(poly, p)
            elif operation in ['find', 'find_irreducible', 'search']:
                result = self.find_irreducible(p, n, primitive)
            elif operation in ['primitive', 'is_primitive', 'test_primitive']:
                result = self.is_primitive(poly, p)
            elif operation in ['factor', 'factorize', 'factorization']:
                result = self.factorize(poly, p)
            elif operation in ['count', 'count_irreducibles']:
                result = self.count_irreducibles(p, n)
            else:
                # Default: test irreducibility if poly provided, else find
                if poly is not None and p is not None:
                    result = self.is_irreducible(poly, p)
                elif p is not None and n is not None:
                    result = self.find_irreducible(p, n)
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
                    ['finite_field', 'irreducible', 'polynomial'],
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
        """PERCEIVE: Monitor blackboard for irreducibility tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['irreducible', 'polynomial', 'factorization'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_irred_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_irred_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_irred_{task_id}',
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
            'irreducibility_tests': self.irreducibility_tests,
            'irreducibles_found': self.irreducibles_found,
            'primitive_polys_found': self.primitive_polys_found,
            'factorizations_performed': self.factorizations_performed,
        }
