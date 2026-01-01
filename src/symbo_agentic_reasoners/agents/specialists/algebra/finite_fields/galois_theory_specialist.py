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
GALOIS THEORY SPECIALIST (Tier 3)
==================================

Handles Galois-theoretic operations for finite fields.

CAPABILITIES:
------------
- splitting_field: Compute splitting field of polynomial
- galois_correspondence: Subgroups ↔ intermediate fields bijection
- normal_closure: Compute normal closure of extension
- is_separable: Check separability (always true for finite fields)
- intermediate_fields: Find all intermediate fields
- subfield_lattice: Construct subfield lattice

FORMULATION:
-----------
Splitting Field: Smallest field containing all roots of polynomial
Galois Correspondence: H ≤ Gal(E/F) ↔ Fix(H) = K with [E:K] = |H|
Normal Closure: For finite fields, always GF(p^{lcm of degrees})
Separability: All extensions of finite fields are separable

ALGORITHMIC BACKING:
-------------------
- Polynomial degree analysis for splitting fields
- Divisor enumeration for Galois correspondence
- LCM computation for normal closure

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lidl & Niederreiter (1997), Chapter 2: Galois Theory of Finite Fields
- Lang (2002), Algebra, Chapter VI: Galois Theory
- Jacobson (1989), Basic Algebra II, Chapter 8
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
    is_prime, is_irreducible_rabin, find_irreducible_polynomial
)

logger = logging.getLogger(__name__)


class GaloisTheorySpecialist(BDIAgent):
    """
    Galois Theory Specialist - Splitting Fields and Correspondence

    DIRECTIVE:
    ---------
    Handle Galois-theoretic computations for finite field extensions.

    OPERATIONS:
    ----------
    - splitting_field: Compute splitting field of polynomial
    - galois_correspondence: Subfield lattice correspondence
    - normal_closure: Compute normal closure
    - is_separable: Check separability
    - intermediate_fields: Enumerate intermediate fields

    FORMULATION:
    -----------
    Every finite field extension is Galois (normal + separable).
    The Galois correspondence gives bijection between subgroups
    of Gal(E/F) and intermediate fields.

    REFERENCE:
    ---------
    - Lidl & Niederreiter (1997), Finite Fields, Chapter 2
    """

    def __init__(
        self,
        agent_id: str = 'galois_theory_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Galois Theory Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.splitting_fields_computed = 0
        self.correspondences_computed = 0
        self.normal_closures_computed = 0
        self.separability_checks = 0
        self.intermediate_fields_found = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.finite_fields.galois',
            agent_id=self.agent_id,
            algorithm='galois_theory',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            operations='splitting_correspondence_normal_separable'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as galois theory specialist")

    # ========================================
    # Core Operations
    # ========================================

    def splitting_field(
        self,
        poly_coeffs: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Compute splitting field of polynomial over GF(p).

        The splitting field is the smallest extension containing all roots.

        Args:
            poly_coeffs: Polynomial coefficients [a_0, a_1, ..., a_n]
            p: Prime characteristic

        Returns:
            Splitting field structure
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not poly_coeffs or all(c == 0 for c in poly_coeffs):
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        try:
            # Normalize polynomial
            poly_coeffs = [c % p for c in poly_coeffs]
            while poly_coeffs and poly_coeffs[-1] == 0:
                poly_coeffs.pop()

            if not poly_coeffs:
                return {'success': False, 'error': 'Polynomial cannot be zero'}

            degree = len(poly_coeffs) - 1

            if degree <= 1:
                self.splitting_fields_computed += 1
                return {
                    'success': True,
                    'splitting_field': f'GF({p})',
                    'extension_degree': 1,
                    'polynomial': poly_coeffs,
                    'reason': 'Linear polynomial splits in base field',
                    'method': 'degree_analysis'
                }

            # Factor polynomial to find degrees of irreducible factors
            factor_degrees = self._get_irreducible_factor_degrees(poly_coeffs, p)

            # Splitting field has degree = lcm of all factor degrees
            splitting_degree = self._lcm_list(factor_degrees)

            self.splitting_fields_computed += 1

            return {
                'success': True,
                'splitting_field': f'GF({p}^{splitting_degree})',
                'extension_degree': splitting_degree,
                'polynomial': poly_coeffs,
                'polynomial_degree': degree,
                'factor_degrees': factor_degrees,
                'galois_group_order': splitting_degree,
                'method': 'lcm_of_factor_degrees'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def galois_correspondence(
        self,
        p: int,
        n: int
    ) -> Dict[str, Any]:
        """
        Compute complete Galois correspondence for GF(p^n)/GF(p).

        Bijection: Subgroups of Gal(E/F) ↔ Intermediate fields F ⊆ K ⊆ E

        Args:
            p: Prime characteristic
            n: Extension degree

        Returns:
            Complete correspondence
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if n < 1:
            return {'success': False, 'error': f'n={n} must be positive'}

        try:
            # Gal(GF(p^n)/GF(p)) ≅ Z/nZ (cyclic)
            # Subgroups: <φ^d> for each d | n, with |<φ^d>| = n/d
            # Fixed field: Fix(<φ^d>) = GF(p^d)

            divisors = self._get_divisors(n)
            correspondence = []

            for d in divisors:
                subgroup_order = n // d
                correspondence.append({
                    'subgroup': f'<φ^{d}>',
                    'subgroup_order': subgroup_order,
                    'subgroup_index': d,
                    'fixed_field': f'GF({p}^{d})',
                    'fixed_degree': d,
                    'extension_over_fixed': n // d,
                    'generator_action': f'x ↦ x^{p**d}'
                })

            self.correspondences_computed += 1

            return {
                'success': True,
                'extension': f'GF({p}^{n})/GF({p})',
                'galois_group': f'Z/{n}Z',
                'galois_group_order': n,
                'correspondence': correspondence,
                'total_intermediate_fields': len(divisors),
                'is_abelian': True,
                'method': 'divisor_enumeration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def normal_closure(
        self,
        base_p: int,
        degrees: List[int]
    ) -> Dict[str, Any]:
        """
        Compute normal closure of composite extension.

        For GF(p^{d_1}), GF(p^{d_2}), ..., normal closure is GF(p^{lcm(d_i)}).

        Args:
            base_p: Prime characteristic
            degrees: Extension degrees of fields to join

        Returns:
            Normal closure structure
        """
        if not is_prime(base_p):
            return {'success': False, 'error': f'p={base_p} is not prime'}

        if not degrees:
            return {'success': False, 'error': 'Must provide at least one degree'}

        try:
            closure_degree = self._lcm_list(degrees)

            self.normal_closures_computed += 1

            return {
                'success': True,
                'normal_closure': f'GF({base_p}^{closure_degree})',
                'closure_degree': closure_degree,
                'input_degrees': degrees,
                'input_fields': [f'GF({base_p}^{d})' for d in degrees],
                'compositum_equals_closure': True,  # Always for finite fields
                'reason': 'LCM of extension degrees',
                'method': 'lcm_computation'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_separable(
        self,
        poly_coeffs: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Check if polynomial is separable over GF(p).

        Over finite fields, a polynomial is separable iff it is square-free.
        Note: All irreducible polynomials over finite fields are separable.

        Args:
            poly_coeffs: Polynomial coefficients
            p: Prime characteristic

        Returns:
            Separability result
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not poly_coeffs or all(c == 0 for c in poly_coeffs):
            return {'success': False, 'error': 'Polynomial cannot be zero'}

        try:
            poly_coeffs = [c % p for c in poly_coeffs]
            while poly_coeffs and poly_coeffs[-1] == 0:
                poly_coeffs.pop()

            # Compute derivative
            derivative = self._polynomial_derivative(poly_coeffs, p)

            # Polynomial is separable iff gcd(f, f') = 1
            gcd = self._polynomial_gcd(poly_coeffs, derivative, p)

            # Check if gcd is constant (just a scalar)
            is_sep = len(gcd) == 1 or (len(gcd) == 0)

            self.separability_checks += 1

            return {
                'success': True,
                'is_separable': is_sep,
                'polynomial': poly_coeffs,
                'derivative': derivative,
                'gcd_with_derivative': gcd,
                'reason': 'Square-free (gcd(f,f\') = 1)' if is_sep else 'Has repeated roots',
                'method': 'gcd_criterion'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def intermediate_fields(
        self,
        p: int,
        n: int
    ) -> Dict[str, Any]:
        """
        Find all intermediate fields between GF(p) and GF(p^n).

        Intermediate fields: GF(p^d) for all d | n.

        Args:
            p: Prime characteristic
            n: Extension degree

        Returns:
            List of all intermediate fields with containment relations
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if n < 1:
            return {'success': False, 'error': f'n={n} must be positive'}

        try:
            divisors = self._get_divisors(n)

            fields = []
            for d in divisors:
                field = {
                    'field': f'GF({p}^{d})',
                    'degree': d,
                    'order': p ** d,
                    'subfields': [f'GF({p}^{e})' for e in divisors if e < d and d % e == 0],
                    'superfields': [f'GF({p}^{e})' for e in divisors if e > d and e % d == 0],
                }
                fields.append(field)

            # Build containment lattice
            lattice = []
            for i, d1 in enumerate(divisors):
                for d2 in divisors:
                    if d1 < d2 and d2 % d1 == 0:
                        lattice.append({
                            'subfield': f'GF({p}^{d1})',
                            'extension': f'GF({p}^{d2})',
                            'relative_degree': d2 // d1
                        })

            self.intermediate_fields_found += 1

            return {
                'success': True,
                'base_field': f'GF({p})',
                'top_field': f'GF({p}^{n})',
                'intermediate_count': len(divisors),
                'fields': fields,
                'containment_lattice': lattice,
                'is_lattice_boolean': self._is_power_of_prime(n),
                'method': 'divisor_lattice'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def field_tower(
        self,
        p: int,
        degrees: List[int]
    ) -> Dict[str, Any]:
        """
        Analyze tower of field extensions GF(p) ⊆ GF(p^d1) ⊆ GF(p^d2) ⊆ ...

        Args:
            p: Prime characteristic
            degrees: Tower degrees (each must divide the next)

        Returns:
            Tower analysis
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not degrees:
            return {'success': False, 'error': 'Must provide tower degrees'}

        try:
            # Verify tower is valid (each degree divides the next)
            for i in range(len(degrees) - 1):
                if degrees[i + 1] % degrees[i] != 0:
                    return {
                        'success': False,
                        'error': f'Invalid tower: {degrees[i]} does not divide {degrees[i+1]}'
                    }

            tower = []
            prev_degree = 1

            for d in degrees:
                tower.append({
                    'field': f'GF({p}^{d})',
                    'absolute_degree': d,
                    'relative_degree': d // prev_degree,
                    'galois_group_over_base': f'Z/{d}Z',
                })
                prev_degree = d

            return {
                'success': True,
                'tower': tower,
                'base': f'GF({p})',
                'top': f'GF({p}^{degrees[-1]})',
                'total_degree': degrees[-1],
                'is_galois_tower': True,  # All finite field extensions are Galois
                'method': 'tower_analysis'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Helper Methods
    # ========================================

    def _gcd(self, a: int, b: int) -> int:
        """Compute gcd(a, b)."""
        while b:
            a, b = b, a % b
        return a

    def _lcm(self, a: int, b: int) -> int:
        """Compute lcm(a, b)."""
        return a * b // self._gcd(a, b)

    def _lcm_list(self, nums: List[int]) -> int:
        """Compute LCM of list of integers."""
        if not nums:
            return 1
        result = nums[0]
        for n in nums[1:]:
            result = self._lcm(result, n)
        return result

    def _get_divisors(self, n: int) -> List[int]:
        """Get all divisors of n."""
        divisors = []
        for i in range(1, int(n ** 0.5) + 1):
            if n % i == 0:
                divisors.append(i)
                if i != n // i:
                    divisors.append(n // i)
        return sorted(divisors)

    def _is_power_of_prime(self, n: int) -> bool:
        """Check if n = p^k for some prime p."""
        if n <= 1:
            return False

        # Find smallest prime factor
        d = 2
        while d * d <= n:
            if n % d == 0:
                # Check if n is a power of d
                while n % d == 0:
                    n //= d
                return n == 1
            d += 1
        return True  # n is prime = p^1

    def _polynomial_derivative(self, poly: List[int], p: int) -> List[int]:
        """Compute formal derivative of polynomial over GF(p)."""
        if len(poly) <= 1:
            return [0]

        deriv = []
        for i in range(1, len(poly)):
            deriv.append((i * poly[i]) % p)

        while deriv and deriv[-1] == 0:
            deriv.pop()

        return deriv if deriv else [0]

    def _polynomial_gcd(
        self,
        a: List[int],
        b: List[int],
        p: int
    ) -> List[int]:
        """Compute GCD of polynomials over GF(p)."""
        while b and not all(c == 0 for c in b):
            _, remainder = self._polynomial_divmod(a, b, p)
            a, b = b, remainder
        return a

    def _polynomial_divmod(
        self,
        dividend: List[int],
        divisor: List[int],
        p: int
    ) -> tuple:
        """Polynomial division with remainder."""
        if not divisor or all(c == 0 for c in divisor):
            raise ValueError("Division by zero")

        while divisor and divisor[-1] == 0:
            divisor.pop()
        while dividend and dividend[-1] == 0:
            dividend.pop()

        if not dividend:
            return [0], [0]

        if len(dividend) < len(divisor):
            return [0], list(dividend)

        dividend = list(dividend)
        divisor_deg = len(divisor) - 1
        dividend_deg = len(dividend) - 1

        quotient = [0] * (dividend_deg - divisor_deg + 1)
        lead_inv = pow(divisor[-1], p - 2, p)

        for i in range(dividend_deg, divisor_deg - 1, -1):
            if dividend[i] != 0:
                coeff = (dividend[i] * lead_inv) % p
                quotient[i - divisor_deg] = coeff
                for j in range(divisor_deg + 1):
                    dividend[i - divisor_deg + j] = (
                        dividend[i - divisor_deg + j] - coeff * divisor[j]
                    ) % p

        while quotient and quotient[-1] == 0:
            quotient.pop()
        while dividend and dividend[-1] == 0:
            dividend.pop()

        return quotient if quotient else [0], dividend if dividend else [0]

    def _get_irreducible_factor_degrees(
        self,
        poly: List[int],
        p: int
    ) -> List[int]:
        """Get degrees of irreducible factors of polynomial."""
        degrees = []
        n = len(poly) - 1

        if n <= 0:
            return [1]

        # Simple distinct-degree factorization
        f = list(poly)
        h = [0, 1]  # x

        for d in range(1, n + 1):
            if len(f) <= 1:
                break

            # h = h^p mod f
            h = self._polynomial_power_mod(h, p, f, p)

            # g = gcd(h - x, f)
            h_minus_x = list(h)
            if len(h_minus_x) >= 2:
                h_minus_x[1] = (h_minus_x[1] - 1) % p
            elif len(h_minus_x) == 1:
                h_minus_x.append(p - 1)
            else:
                h_minus_x = [0, p - 1]

            g = self._polynomial_gcd(h_minus_x, f, p)

            if len(g) > 1:
                # Number of irreducible factors of degree d
                num_factors = (len(g) - 1) // d
                for _ in range(num_factors):
                    degrees.append(d)

                # f = f / g
                f, _ = self._polynomial_divmod(f, g, p)

            if 2 * d > len(f) - 1 and len(f) > 1:
                degrees.append(len(f) - 1)
                break

        return degrees if degrees else [n]

    def _polynomial_power_mod(
        self,
        base: List[int],
        exp: int,
        mod: List[int],
        p: int
    ) -> List[int]:
        """Compute base^exp mod mod_poly."""
        if exp == 0:
            return [1]

        result = [1]
        current = list(base)

        while exp > 0:
            if exp & 1:
                result = self._polynomial_mult_mod(result, current, mod, p)
            current = self._polynomial_mult_mod(current, current, mod, p)
            exp >>= 1

        return result

    def _polynomial_mult_mod(
        self,
        a: List[int],
        b: List[int],
        mod: List[int],
        p: int
    ) -> List[int]:
        """Multiply polynomials and reduce mod."""
        # Multiply
        if not a or not b:
            return [0]

        result = [0] * (len(a) + len(b) - 1)
        for i, ai in enumerate(a):
            for j, bj in enumerate(b):
                result[i + j] = (result[i + j] + ai * bj) % p

        # Reduce
        _, remainder = self._polynomial_divmod(result, mod, p)
        return remainder

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process Galois theory task."""
        self.tasks_executed += 1

        try:
            # Extract metadata
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'galois_correspondence')
            p = metadata.get('p') or metadata.get('characteristic')
            n = metadata.get('n') or metadata.get('degree')
            poly = metadata.get('polynomial') or metadata.get('poly')
            degrees = metadata.get('degrees')

            # Route to appropriate method
            if operation in ['splitting', 'splitting_field']:
                result = self.splitting_field(poly, p)
            elif operation in ['correspondence', 'galois_correspondence']:
                result = self.galois_correspondence(p, n)
            elif operation in ['normal', 'normal_closure']:
                result = self.normal_closure(p, degrees)
            elif operation in ['separable', 'is_separable']:
                result = self.is_separable(poly, p)
            elif operation in ['intermediate', 'intermediate_fields']:
                result = self.intermediate_fields(p, n)
            elif operation in ['tower', 'field_tower']:
                result = self.field_tower(p, degrees)
            else:
                if p is not None and n is not None:
                    result = self.galois_correspondence(p, n)
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
                    ['finite_field', 'galois', 'splitting_field'],
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
        """PERCEIVE: Monitor blackboard for Galois theory tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['galois', 'splitting_field', 'galois_correspondence'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_galois_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_galois_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_galois_{task_id}',
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
            'splitting_fields_computed': self.splitting_fields_computed,
            'correspondences_computed': self.correspondences_computed,
            'normal_closures_computed': self.normal_closures_computed,
            'separability_checks': self.separability_checks,
            'intermediate_fields_found': self.intermediate_fields_found,
        }
