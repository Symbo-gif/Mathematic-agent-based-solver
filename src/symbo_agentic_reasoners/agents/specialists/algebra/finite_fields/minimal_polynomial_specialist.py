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
MINIMAL POLYNOMIAL SPECIALIST (Tier 3)
======================================

Handles minimal polynomial computation and Frobenius-related operations.

CAPABILITIES:
------------
- minimal_polynomial: Compute minimal polynomial of field element
- frobenius_map: Apply Frobenius endomorphism x -> x^p
- conjugate_elements: Find all Frobenius conjugates
- is_normal_basis: Check if elements form a normal basis
- trace: Compute field trace Tr(a)
- norm: Compute field norm N(a)

FORMULATION:
-----------
Minimal polynomial: Monic polynomial m(x) of least degree with m(α) = 0
Frobenius: φ(α) = α^p is the generating automorphism of Gal(GF(p^n)/GF(p))
Conjugates: {α, α^p, α^{p^2}, ..., α^{p^{d-1}}} where d = degree of minimal poly
Trace: Tr(α) = α + α^p + ... + α^{p^{n-1}}
Norm: N(α) = α * α^p * ... * α^{p^{n-1}}

ALGORITHMIC BACKING:
-------------------
- Frobenius iteration for conjugates
- Product formula for minimal polynomial
- Trace and norm via Frobenius powers

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lidl & Niederreiter (1997), Chapter 2: Frobenius and Minimal Polynomials
- Shoup (2005), Chapter 14: Minimal Polynomials
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
    is_prime, polynomial_add, polynomial_multiply, polynomial_mult_mod,
    frobenius_map, minimal_polynomial as compute_min_poly
)

logger = logging.getLogger(__name__)


class MinimalPolynomialSpecialist(BDIAgent):
    """
    Minimal Polynomial Specialist - Frobenius and Conjugacy

    DIRECTIVE:
    ---------
    Handle minimal polynomial computation and Frobenius-related operations.

    OPERATIONS:
    ----------
    - minimal_polynomial: Compute minimal polynomial
    - frobenius: Apply Frobenius automorphism
    - conjugates: Find all Frobenius conjugates
    - trace: Field trace computation
    - norm: Field norm computation
    - is_normal_basis: Normal basis verification

    FORMULATION:
    -----------
    The Frobenius map φ: α → α^p generates Gal(GF(p^n)/GF(p)).
    Conjugacy class of α under Frobenius determines minimal polynomial.

    REFERENCE:
    ---------
    - Lidl & Niederreiter (1997), Finite Fields, Chapter 2
    """

    def __init__(
        self,
        agent_id: str = 'minimal_polynomial_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Minimal Polynomial Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.minimal_polys_computed = 0
        self.frobenius_applications = 0
        self.conjugates_found = 0
        self.traces_computed = 0
        self.norms_computed = 0
        self.normal_bases_checked = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.finite_fields.minimal_poly',
            agent_id=self.agent_id,
            algorithm='frobenius_minimal_polynomial',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            operations='minimal_frobenius_conjugates_trace_norm'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as minimal polynomial specialist")

    # ========================================
    # Core Operations
    # ========================================

    def compute_minimal_polynomial(
        self,
        elem: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Compute minimal polynomial of element over GF(p).

        The minimal polynomial is the monic polynomial of least degree
        that has elem as a root.

        Args:
            elem: Element coefficients
            irred_poly: Irreducible polynomial defining field
            p: Prime characteristic

        Returns:
            Minimal polynomial coefficients
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not elem or all(c == 0 for c in elem):
            # Zero element has minimal polynomial x
            return {
                'success': True,
                'minimal_polynomial': [0, 1],
                'degree': 1,
                'element': [0],
                'method': 'zero_element'
            }

        try:
            # Get conjugates under Frobenius
            conj_result = self.get_conjugates(elem, irred_poly, p)
            if not conj_result['success']:
                return conj_result

            conjugates = conj_result['conjugates']
            degree = len(conjugates)

            # Minimal polynomial = product of (x - conjugate) for all conjugates
            min_poly = [1]  # Start with 1

            for conj in conjugates:
                # Multiply by (x - conj) = x + (-conj)
                neg_conj = [(-c) % p for c in conj]
                # (a_0 + a_1*x + ...) * (x + c) = c*a_0 + (c*a_1 + a_0)*x + ...
                new_poly = [0] * (len(min_poly) + 1)

                for i, coeff in enumerate(min_poly):
                    # Add coeff * x^(i+1)
                    new_poly[i + 1] = (new_poly[i + 1] + coeff) % p
                    # Add coeff * (-conj_0)
                    for j, nc in enumerate(neg_conj):
                        if i + j < len(new_poly):
                            new_poly[i] = (new_poly[i] + coeff * nc) % p

                min_poly = new_poly

            # Clean up
            while min_poly and min_poly[-1] == 0:
                min_poly.pop()

            self.minimal_polys_computed += 1

            return {
                'success': True,
                'minimal_polynomial': min_poly,
                'degree': degree,
                'element': elem,
                'conjugates': conjugates,
                'divides_field_poly': True,  # Always true
                'method': 'conjugate_product'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def apply_frobenius(
        self,
        elem: List[int],
        irred_poly: List[int],
        p: int,
        power: int = 1
    ) -> Dict[str, Any]:
        """
        Apply Frobenius automorphism: elem -> elem^{p^power}.

        Args:
            elem: Element coefficients
            irred_poly: Irreducible polynomial
            p: Prime characteristic
            power: Frobenius power (default 1)

        Returns:
            Frobenius image
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if power < 0:
            return {'success': False, 'error': 'Frobenius power must be non-negative'}

        try:
            result = list(elem)

            for _ in range(power):
                result = self._frobenius_once(result, irred_poly, p)

            self.frobenius_applications += 1

            return {
                'success': True,
                'frobenius_image': result,
                'element': elem,
                'power': power,
                'characteristic': p,
                'method': 'frobenius_iteration'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_conjugates(
        self,
        elem: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Find all Frobenius conjugates of element.

        Conjugates are {α, α^p, α^{p^2}, ...} until cycle closes.

        Args:
            elem: Element coefficients
            irred_poly: Irreducible polynomial
            p: Prime characteristic

        Returns:
            List of all conjugates
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        try:
            n = len(irred_poly) - 1  # Extension degree
            conjugates = []
            current = list(elem)

            for _ in range(n):
                # Normalize for comparison
                normalized = self._normalize(current)
                conj_tuple = tuple(normalized)

                # Check if we've seen this conjugate
                if any(tuple(self._normalize(c)) == conj_tuple for c in conjugates):
                    break

                conjugates.append(normalized)
                current = self._frobenius_once(current, irred_poly, p)

            self.conjugates_found += 1

            return {
                'success': True,
                'conjugates': conjugates,
                'count': len(conjugates),
                'element': elem,
                'degree_over_base': len(conjugates),
                'method': 'frobenius_orbit'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def compute_trace(
        self,
        elem: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Compute field trace Tr_{GF(p^n)/GF(p)}(elem).

        Trace = sum of all Frobenius conjugates.

        Args:
            elem: Element coefficients
            irred_poly: Irreducible polynomial
            p: Prime characteristic

        Returns:
            Trace value (element of GF(p))
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        try:
            n = len(irred_poly) - 1

            # Trace = α + α^p + α^{p^2} + ... + α^{p^{n-1}}
            trace = [0] * n
            current = list(elem)

            for _ in range(n):
                trace = polynomial_add(trace, current, p)
                current = self._frobenius_once(current, irred_poly, p)

            # Trace should be in base field (just constant term)
            trace_value = trace[0] if trace else 0

            self.traces_computed += 1

            return {
                'success': True,
                'trace': trace_value,
                'element': elem,
                'extension_degree': n,
                'method': 'frobenius_sum'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def compute_norm(
        self,
        elem: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Compute field norm N_{GF(p^n)/GF(p)}(elem).

        Norm = product of all Frobenius conjugates.

        Args:
            elem: Element coefficients
            irred_poly: Irreducible polynomial
            p: Prime characteristic

        Returns:
            Norm value (element of GF(p))
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not elem or all(c == 0 for c in elem):
            return {
                'success': True,
                'norm': 0,
                'element': [0],
                'method': 'zero_element'
            }

        try:
            n = len(irred_poly) - 1

            # Norm = α * α^p * α^{p^2} * ... * α^{p^{n-1}}
            norm = list(elem)
            current = self._frobenius_once(elem, irred_poly, p)

            for _ in range(n - 1):
                norm = polynomial_mult_mod(norm, current, irred_poly, p)
                current = self._frobenius_once(current, irred_poly, p)

            # Norm should be in base field
            norm_value = norm[0] if norm else 0

            self.norms_computed += 1

            return {
                'success': True,
                'norm': norm_value,
                'element': elem,
                'extension_degree': n,
                'method': 'frobenius_product'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_normal_basis(
        self,
        elem: List[int],
        irred_poly: List[int],
        p: int
    ) -> Dict[str, Any]:
        """
        Check if element generates a normal basis.

        A normal basis is {α, α^p, α^{p^2}, ..., α^{p^{n-1}}} that spans GF(p^n).

        Args:
            elem: Element coefficients
            irred_poly: Irreducible polynomial
            p: Prime characteristic

        Returns:
            True if conjugates form a basis
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        try:
            n = len(irred_poly) - 1

            # Get all conjugates
            conj_result = self.get_conjugates(elem, irred_poly, p)
            if not conj_result['success']:
                return conj_result

            conjugates = conj_result['conjugates']

            # Must have exactly n conjugates
            if len(conjugates) != n:
                self.normal_bases_checked += 1
                return {
                    'success': True,
                    'is_normal_basis': False,
                    'element': elem,
                    'conjugate_count': len(conjugates),
                    'expected': n,
                    'reason': f'Only {len(conjugates)} conjugates, need {n}',
                    'method': 'conjugate_count'
                }

            # Check linear independence by computing determinant
            # Create matrix where rows are conjugate coefficient vectors
            matrix = [self._pad_to_length(c, n) for c in conjugates]
            det = self._determinant_mod_p(matrix, p)

            is_basis = det != 0
            self.normal_bases_checked += 1

            return {
                'success': True,
                'is_normal_basis': is_basis,
                'element': elem,
                'conjugates': conjugates,
                'determinant': det,
                'reason': 'Conjugates linearly independent' if is_basis else 'Conjugates linearly dependent',
                'method': 'linear_independence'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Helper Methods
    # ========================================

    def _frobenius_once(
        self,
        elem: List[int],
        irred_poly: List[int],
        p: int
    ) -> List[int]:
        """Apply Frobenius once: elem -> elem^p."""
        # Use square-and-multiply for elem^p
        if not elem or all(c == 0 for c in elem):
            return [0]

        result = [1]
        base = list(elem)
        exp = p

        while exp > 0:
            if exp & 1:
                result = polynomial_mult_mod(result, base, irred_poly, p)
            base = polynomial_mult_mod(base, base, irred_poly, p)
            exp >>= 1

        return result

    def _normalize(self, poly: List[int]) -> List[int]:
        """Remove trailing zeros from polynomial."""
        result = list(poly)
        while result and result[-1] == 0:
            result.pop()
        return result if result else [0]

    def _pad_to_length(self, poly: List[int], length: int) -> List[int]:
        """Pad polynomial to specified length."""
        result = list(poly)
        while len(result) < length:
            result.append(0)
        return result[:length]

    def _determinant_mod_p(self, matrix: List[List[int]], p: int) -> int:
        """Compute determinant of matrix modulo p using Gaussian elimination."""
        n = len(matrix)
        if n == 0:
            return 1

        # Copy matrix
        M = [[c % p for c in row] for row in matrix]

        det = 1
        for col in range(n):
            # Find pivot
            pivot_row = None
            for row in range(col, n):
                if M[row][col] != 0:
                    pivot_row = row
                    break

            if pivot_row is None:
                return 0  # Singular

            # Swap rows
            if pivot_row != col:
                M[col], M[pivot_row] = M[pivot_row], M[col]
                det = (-det) % p

            pivot = M[col][col]
            det = (det * pivot) % p
            pivot_inv = pow(pivot, p - 2, p)

            # Eliminate
            for row in range(col + 1, n):
                if M[row][col] != 0:
                    factor = (M[row][col] * pivot_inv) % p
                    for j in range(col, n):
                        M[row][j] = (M[row][j] - factor * M[col][j]) % p

        return det

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process minimal polynomial task."""
        self.tasks_executed += 1

        try:
            # Extract metadata
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'minimal_polynomial')
            elem = metadata.get('element') or metadata.get('elem') or metadata.get('coeffs')
            p = metadata.get('p') or metadata.get('characteristic')
            irred_poly = metadata.get('irred_poly') or metadata.get('irreducible')
            power = metadata.get('power', 1)

            # Route to appropriate method
            if operation in ['minimal', 'minimal_polynomial', 'min_poly']:
                result = self.compute_minimal_polynomial(elem, irred_poly, p)
            elif operation in ['frobenius', 'frob']:
                result = self.apply_frobenius(elem, irred_poly, p, power)
            elif operation in ['conjugates', 'conjugate', 'orbit']:
                result = self.get_conjugates(elem, irred_poly, p)
            elif operation in ['trace', 'tr']:
                result = self.compute_trace(elem, irred_poly, p)
            elif operation in ['norm', 'n']:
                result = self.compute_norm(elem, irred_poly, p)
            elif operation in ['normal_basis', 'is_normal', 'normal']:
                result = self.is_normal_basis(elem, irred_poly, p)
            else:
                if elem is not None and irred_poly is not None:
                    result = self.compute_minimal_polynomial(elem, irred_poly, p)
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
                    ['finite_field', 'minimal_polynomial', 'frobenius'],
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
        """PERCEIVE: Monitor blackboard for minimal polynomial tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['minimal_polynomial', 'frobenius', 'conjugate'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_minpoly_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_minpoly_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_minpoly_{task_id}',
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
            'minimal_polys_computed': self.minimal_polys_computed,
            'frobenius_applications': self.frobenius_applications,
            'conjugates_found': self.conjugates_found,
            'traces_computed': self.traces_computed,
            'norms_computed': self.norms_computed,
            'normal_bases_checked': self.normal_bases_checked,
        }
