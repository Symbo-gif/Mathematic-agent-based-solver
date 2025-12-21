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
EXTENSION FIELD SPECIALIST (Tier 3)
====================================

Handles construction and operations in extension fields GF(p^n).

CAPABILITIES:
------------
- construct_extension_field: Build GF(p^n) with irreducible polynomial
- element_to_polynomial: Convert element to polynomial representation
- detect_subfield: Find GF(p^d) as subfield of GF(p^n)
- degree: Return extension degree
- create_element: Create element from coefficients

FORMULATION:
-----------
GF(p^n) = GF(p)[x] / <f(x)> where f(x) is irreducible of degree n
Elements: a_0 + a_1*x + ... + a_{n-1}*x^{n-1} with a_i in GF(p)
Subfields: GF(p^d) is subfield of GF(p^n) iff d divides n

ALGORITHMIC BACKING:
-------------------
Native finite_fields module (core/finite_fields.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Lidl & Niederreiter (1997), Chapter 2: Extension Fields
- Shoup (2005), Chapter 14: Extension Fields
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
    GFpnElement, create_extension_field, find_irreducible_polynomial,
    is_irreducible_rabin, is_prime
)

logger = logging.getLogger(__name__)


class ExtensionFieldSpecialist(BDIAgent):
    """
    Extension Field Specialist - GF(p^n) Construction

    DIRECTIVE:
    ---------
    Handle construction and representation of extension fields GF(p^n).

    OPERATIONS:
    ----------
    - construct_extension_field: Build GF(p^n)
    - element_to_polynomial: Polynomial representation
    - detect_subfield: Find subfields
    - degree: Extension degree
    - create_element: Create field element

    FORMULATION:
    -----------
    GF(p^n) is unique field of order p^n.
    Constructed as quotient ring GF(p)[x]/<f(x)>.
    Contains GF(p^d) as subfield iff d | n.

    REFERENCE:
    ---------
    - Lidl & Niederreiter (1997), Finite Fields, Chapter 2
    """

    def __init__(
        self,
        agent_id: str = 'extension_field_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Extension Field Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.extension_fields_created = 0
        self.degree_computations = 0
        self.subfields_detected = 0
        self.basis_conversions = 0
        self.elements_created = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.finite_fields.extension',
            agent_id=self.agent_id,
            algorithm='extension_field_construction',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            operations='construct_element_subfield_degree_polynomial'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as extension field specialist")

    # ========================================
    # Core Operations
    # ========================================

    def construct_extension_field(
        self,
        p: int,
        n: int,
        irred_poly: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Construct extension field GF(p^n).

        Args:
            p: Prime characteristic
            n: Extension degree
            irred_poly: Optional irreducible polynomial (auto-find if None)

        Returns:
            Field structure with metadata
        """
        # Validate inputs
        if not isinstance(p, int) or p < 2:
            return {'success': False, 'error': f'p={p} must be integer >= 2'}

        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if not isinstance(n, int) or n < 1:
            return {'success': False, 'error': f'n={n} must be positive integer'}

        # Handle prime field case
        if n == 1:
            self.extension_fields_created += 1
            return {
                'success': True,
                'field': {
                    'p': p,
                    'n': 1,
                    'order': p,
                    'characteristic': p,
                    'irred_poly': [0, 1],  # x
                    'type': 'prime_field',
                    'is_extension': False
                },
                'method': 'trivial_extension'
            }

        try:
            # Find or validate irreducible polynomial
            if irred_poly is None:
                irred_poly = find_irreducible_polynomial(p, n)
                if irred_poly is None:
                    return {
                        'success': False,
                        'error': f'Could not find irreducible polynomial of degree {n} over GF({p})'
                    }
            else:
                # Validate provided polynomial
                if len(irred_poly) != n + 1:
                    return {
                        'success': False,
                        'error': f'Polynomial must have degree {n}, got {len(irred_poly) - 1}'
                    }
                if not is_irreducible_rabin(tuple(irred_poly), p):
                    return {
                        'success': False,
                        'error': 'Provided polynomial is not irreducible'
                    }

            self.extension_fields_created += 1

            return {
                'success': True,
                'field': {
                    'p': p,
                    'n': n,
                    'order': p ** n,
                    'characteristic': p,
                    'irred_poly': irred_poly,
                    'type': 'extension_field',
                    'is_extension': True,
                    'multiplicative_group_order': p ** n - 1
                },
                'method': 'polynomial_quotient_ring'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_element(
        self,
        coeffs: List[int],
        p: int,
        irred_poly: List[int]
    ) -> Dict[str, Any]:
        """
        Create element of GF(p^n) from coefficients.

        Args:
            coeffs: Polynomial coefficients [a_0, a_1, ..., a_{n-1}]
            p: Prime characteristic
            irred_poly: Irreducible polynomial defining field

        Returns:
            Field element
        """
        try:
            element = GFpnElement(coeffs, p, irred_poly)
            self.elements_created += 1

            return {
                'success': True,
                'element': {
                    'coeffs': element.coeffs,
                    'p': p,
                    'n': element.n,
                    'polynomial_repr': self._coeffs_to_poly_string(element.coeffs)
                },
                'method': 'direct_construction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def element_to_polynomial(self, coeffs: List[int]) -> Dict[str, Any]:
        """
        Convert coefficient list to polynomial string representation.

        Args:
            coeffs: Coefficients [a_0, a_1, ..., a_{n-1}]

        Returns:
            Polynomial string representation
        """
        self.basis_conversions += 1

        poly_str = self._coeffs_to_poly_string(coeffs)

        return {
            'success': True,
            'coefficients': coeffs,
            'polynomial': poly_str,
            'degree': len([c for c in coeffs if c != 0]) - 1 if any(c != 0 for c in coeffs) else -1,
            'method': 'coefficient_to_polynomial'
        }

    def detect_subfield(self, p: int, n: int, d: int) -> Dict[str, Any]:
        """
        Check if GF(p^d) is a subfield of GF(p^n).

        GF(p^d) is subfield of GF(p^n) iff d divides n.

        Args:
            p: Prime characteristic
            n: Larger field degree
            d: Potential subfield degree

        Returns:
            Subfield detection result
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        if d <= 0 or n <= 0:
            return {'success': False, 'error': 'Degrees must be positive'}

        is_subfield = n % d == 0

        self.subfields_detected += 1

        return {
            'success': True,
            'is_subfield': is_subfield,
            'parent_field': f'GF({p}^{n})',
            'subfield': f'GF({p}^{d})',
            'extension_degree': n // d if is_subfield else None,
            'reason': f'{d} divides {n}' if is_subfield else f'{d} does not divide {n}',
            'method': 'divisibility_check'
        }

    def get_subfields(self, p: int, n: int) -> Dict[str, Any]:
        """
        Find all subfields of GF(p^n).

        Args:
            p: Prime characteristic
            n: Field degree

        Returns:
            List of all subfields
        """
        if not is_prime(p):
            return {'success': False, 'error': f'p={p} is not prime'}

        divisors = []
        for d in range(1, n + 1):
            if n % d == 0:
                divisors.append(d)

        subfields = [{'degree': d, 'order': p ** d, 'field': f'GF({p}^{d})'} for d in divisors]

        return {
            'success': True,
            'parent_field': f'GF({p}^{n})',
            'subfields': subfields,
            'count': len(subfields),
            'method': 'divisor_enumeration'
        }

    def degree(self, field_structure: Dict) -> Dict[str, Any]:
        """
        Return extension degree of field.

        Args:
            field_structure: Field structure dictionary

        Returns:
            Degree information
        """
        self.degree_computations += 1

        n = field_structure.get('n', 1)
        p = field_structure.get('p', 2)

        return {
            'success': True,
            'degree': n,
            'characteristic': p,
            'order': p ** n,
            'method': 'direct_lookup'
        }

    def _coeffs_to_poly_string(self, coeffs: List[int]) -> str:
        """Convert coefficients to polynomial string."""
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

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process extension field task."""
        self.tasks_executed += 1

        try:
            # Extract metadata
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'construct_extension_field')
            p = metadata.get('p') or metadata.get('prime') or metadata.get('characteristic')
            n = metadata.get('n') or metadata.get('degree')
            d = metadata.get('d') or metadata.get('subfield_degree')
            coeffs = metadata.get('coeffs') or metadata.get('coefficients')
            irred_poly = metadata.get('irred_poly') or metadata.get('irreducible')

            # Route to appropriate method
            if operation in ['construct', 'construct_extension_field', 'create_field']:
                result = self.construct_extension_field(p, n, irred_poly)
            elif operation in ['element', 'create_element']:
                result = self.create_element(coeffs, p, irred_poly)
            elif operation in ['to_polynomial', 'element_to_polynomial']:
                result = self.element_to_polynomial(coeffs)
            elif operation in ['subfield', 'detect_subfield', 'is_subfield']:
                result = self.detect_subfield(p, n, d)
            elif operation in ['subfields', 'get_subfields', 'all_subfields']:
                result = self.get_subfields(p, n)
            elif operation in ['degree', 'extension_degree']:
                field_struct = metadata.get('field', {'p': p, 'n': n})
                result = self.degree(field_struct)
            else:
                # Default: construct field
                if p is not None and n is not None:
                    result = self.construct_extension_field(p, n, irred_poly)
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
                    ['finite_field', 'extension_field', 'gf_pn'],
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
        """PERCEIVE: Monitor blackboard for extension field tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['extension_field', 'gf_pn', 'galois_field'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_ext_field_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_ext_field_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_ext_field_{task_id}',
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
            'extension_fields_created': self.extension_fields_created,
            'degree_computations': self.degree_computations,
            'subfields_detected': self.subfields_detected,
            'basis_conversions': self.basis_conversions,
            'elements_created': self.elements_created,
        }
