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
FINITE FIELDS SUPERVISOR (Tier 2)
=================================

Routes finite field theory tasks to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

ROUTING STRATEGY:
----------------
Finite Fields:
- Prime Fields: GF(p) operations, modular arithmetic in prime fields
- Extension Fields: GF(p^n) construction, polynomial representation
- Irreducible Polynomials: Testing, finding, primitive polynomials
- Field Arithmetic: Addition, multiplication, inverse, exponentiation
- Minimal Polynomials: Frobenius map, conjugates, minimal poly computation
- Field Isomorphisms: Isomorphism detection, automorphism groups
- Galois Theory: Splitting fields, Galois correspondence, fixed fields

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import EntryStatus, EntryType, create_entry

logger = logging.getLogger(__name__)


class FiniteFieldsSupervisor(BDIAgent):
    """
    Supervisor for finite fields domain.

    Routes to 7 specialists:
    - PrimeFieldSpecialist: GF(p) construction, primitive elements
    - ExtensionFieldSpecialist: GF(p^n) construction, element representation
    - IrreduciblePolynomialSpecialist: Irreducibility testing, poly finding
    - FieldArithmeticSpecialist: Field operations (+, ×, inverse, exp)
    - MinimalPolynomialSpecialist: Minimal poly, Frobenius, conjugates
    - FieldIsomorphismSpecialist: Isomorphisms, automorphisms, fixed fields
    - GaloisTheorySpecialist: Splitting fields, Galois correspondence

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing (priority ordered, most specific first)
    GALOIS_THEORY_KW = ['splitting field', 'galois correspondence', 'galois group',
                        'fixed field', 'normal closure', 'separable', 'intermediate field',
                        'subfield lattice', 'field tower']

    ISOMORPHISM_KW = ['field isomorphism', 'isomorphic fields', 'automorphism',
                      'automorphism group', 'fixed field', 'orbit', 'conjugation',
                      'field equivalence']

    MINIMAL_POLY_KW = ['minimal polynomial', 'frobenius', 'frobenius map',
                       'conjugate', 'conjugacy class', 'normal basis',
                       'trace', 'norm']

    FIELD_ARITHMETIC_KW = ['field multiplication', 'field addition', 'field inverse',
                           'field exponent', 'discrete log', 'element order',
                           'multiply in gf', 'add in gf', 'invert in gf']

    IRREDUCIBLE_KW = ['irreducible polynomial', 'irreducible', 'primitive polynomial',
                      'factorize polynomial', 'polynomial factorization', 'rabin test',
                      'find irreducible', 'test irreducibility']

    EXTENSION_FIELD_KW = ['extension field', 'gf(p^n)', 'galois field', 'field extension',
                          'construct gf', 'polynomial basis', 'subfield', 'degree of extension',
                          'extension degree']

    PRIME_FIELD_KW = ['prime field', 'gf(p)', 'field of order p', 'modulo prime',
                      'primitive element', 'generator', 'multiplicative group',
                      'finite field order']

    def __init__(self, agent_id: str = 'finite_fields_supervisor_001',
                 df=None, blackboard=None):
        """
        Initialize Finite Fields Supervisor.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator reference
            blackboard: Shared blackboard reference
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.prime_field_routes = 0
        self.extension_field_routes = 0
        self.irreducible_routes = 0
        self.field_arithmetic_routes = 0
        self.minimal_poly_routes = 0
        self.isomorphism_routes = 0
        self.galois_theory_routes = 0

        # Lazy-loaded specialists
        self._prime_field_specialist = None
        self._extension_field_specialist = None
        self._irreducible_polynomial_specialist = None
        self._field_arithmetic_specialist = None
        self._minimal_polynomial_specialist = None
        self._field_isomorphism_specialist = None
        self._galois_theory_specialist = None

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register supervisor with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.finite_fields',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='minimal',
            instance=self,
            type='supervisor',
            tier='2',
            domain='finite_fields',
            capabilities='prime_extension_irreducible_arithmetic_minimal_isomorphism_galois'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as finite fields supervisor")

    # ========================================
    # Lazy-Loaded Specialists
    # ========================================

    @property
    def prime_field_specialist(self):
        """Lazy load Prime Field Specialist."""
        if self._prime_field_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields import PrimeFieldSpecialist
            self._prime_field_specialist = PrimeFieldSpecialist(
                agent_id='prime_field_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._prime_field_specialist

    @property
    def extension_field_specialist(self):
        """Lazy load Extension Field Specialist."""
        if self._extension_field_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields import ExtensionFieldSpecialist
            self._extension_field_specialist = ExtensionFieldSpecialist(
                agent_id='extension_field_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._extension_field_specialist

    @property
    def irreducible_polynomial_specialist(self):
        """Lazy load Irreducible Polynomial Specialist."""
        if self._irreducible_polynomial_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields import IrreduciblePolynomialSpecialist
            self._irreducible_polynomial_specialist = IrreduciblePolynomialSpecialist(
                agent_id='irreducible_polynomial_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._irreducible_polynomial_specialist

    @property
    def field_arithmetic_specialist(self):
        """Lazy load Field Arithmetic Specialist."""
        if self._field_arithmetic_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields import FieldArithmeticSpecialist
            self._field_arithmetic_specialist = FieldArithmeticSpecialist(
                agent_id='field_arithmetic_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._field_arithmetic_specialist

    @property
    def minimal_polynomial_specialist(self):
        """Lazy load Minimal Polynomial Specialist."""
        if self._minimal_polynomial_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields import MinimalPolynomialSpecialist
            self._minimal_polynomial_specialist = MinimalPolynomialSpecialist(
                agent_id='minimal_polynomial_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._minimal_polynomial_specialist

    @property
    def field_isomorphism_specialist(self):
        """Lazy load Field Isomorphism Specialist."""
        if self._field_isomorphism_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields import FieldIsomorphismSpecialist
            self._field_isomorphism_specialist = FieldIsomorphismSpecialist(
                agent_id='field_isomorphism_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._field_isomorphism_specialist

    @property
    def galois_theory_specialist(self):
        """Lazy load Galois Theory Specialist."""
        if self._galois_theory_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields import GaloisTheorySpecialist
            self._galois_theory_specialist = GaloisTheorySpecialist(
                agent_id='galois_theory_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._galois_theory_specialist

    # ========================================
    # Routing Logic
    # ========================================

    def _determine_specialist(self, operation: str) -> str:
        """
        Determine which specialist should handle the operation.

        Args:
            operation: Problem description/operation string (lowercase)

        Returns:
            Specialist type string
        """
        operation_lower = operation.lower()

        # Priority order: most specific first
        if any(kw in operation_lower for kw in self.GALOIS_THEORY_KW):
            return 'galois_theory'

        if any(kw in operation_lower for kw in self.ISOMORPHISM_KW):
            return 'isomorphism'

        if any(kw in operation_lower for kw in self.MINIMAL_POLY_KW):
            return 'minimal_polynomial'

        if any(kw in operation_lower for kw in self.FIELD_ARITHMETIC_KW):
            return 'field_arithmetic'

        if any(kw in operation_lower for kw in self.IRREDUCIBLE_KW):
            return 'irreducible'

        if any(kw in operation_lower for kw in self.EXTENSION_FIELD_KW):
            return 'extension_field'

        if any(kw in operation_lower for kw in self.PRIME_FIELD_KW):
            return 'prime_field'

        # Default to prime field for basic GF operations
        return 'prime_field'

    def _get_specialist(self, specialist_type: str):
        """
        Get specialist instance by type.

        Args:
            specialist_type: Type of specialist

        Returns:
            Specialist instance
        """
        specialists = {
            'prime_field': self.prime_field_specialist,
            'extension_field': self.extension_field_specialist,
            'irreducible': self.irreducible_polynomial_specialist,
            'field_arithmetic': self.field_arithmetic_specialist,
            'minimal_polynomial': self.minimal_polynomial_specialist,
            'isomorphism': self.field_isomorphism_specialist,
            'galois_theory': self.galois_theory_specialist,
        }
        return specialists.get(specialist_type, self.prime_field_specialist)

    def _update_routing_stats(self, specialist_type: str):
        """Update routing statistics."""
        if specialist_type == 'prime_field':
            self.prime_field_routes += 1
        elif specialist_type == 'extension_field':
            self.extension_field_routes += 1
        elif specialist_type == 'irreducible':
            self.irreducible_routes += 1
        elif specialist_type == 'field_arithmetic':
            self.field_arithmetic_routes += 1
        elif specialist_type == 'minimal_polynomial':
            self.minimal_poly_routes += 1
        elif specialist_type == 'isomorphism':
            self.isomorphism_routes += 1
        elif specialist_type == 'galois_theory':
            self.galois_theory_routes += 1

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """
        Route task to appropriate specialist.

        Args:
            task_entry: Task entry from blackboard

        Returns:
            Result from specialist
        """
        self.tasks_routed += 1

        try:
            # Extract operation from task
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
                operation = metadata.get('operation', '')
                if not operation:
                    operation = str(task_entry.content) if hasattr(task_entry, 'content') else ''
            else:
                operation = str(task_entry)

            # Determine and get specialist
            specialist_type = self._determine_specialist(operation)
            specialist = self._get_specialist(specialist_type)
            self._update_routing_stats(specialist_type)

            logger.info(f"[{self.agent_id}] Routing to {specialist_type} specialist")

            # Delegate to specialist
            result = specialist.process(task_entry)

            if result and (isinstance(result, dict) and result.get('success', False) or
                          hasattr(result, 'status') and result.status == EntryStatus.COMPLETED):
                self.tasks_completed += 1
            else:
                self.tasks_failed += 1

            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] Routing failed: {e}")
            return {'success': False, 'error': str(e)}

    # ========================================
    # BDI Interface
    # ========================================

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for finite field tasks."""
        if not self.blackboard:
            return

        # Query for pending finite field tasks
        entries = self.blackboard.query_entries(
            tags=['finite_field', 'galois_field', 'gf'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_ff_task_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')
                logger.debug(f"[{self.agent_id}] Added belief: {belief_key}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing intentions from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_ff_task_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            # Skip if already processing
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Create routing intention
            intention = Intention(
                goal=f'route_ff_task_{task_id}',
                plan=['claim_task', 'determine_specialist', 'route', 'post_result'],
                priority=5,
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of routing plan."""
        action = intention.get_current_action()

        if action == 'claim_task':
            task_id = intention.metadata.get('task_id')
            self.add_belief(f'claimed_task_{task_id}', True, confidence=1.0)
            intention.advance()

        elif action == 'determine_specialist':
            task_entry = intention.metadata.get('task_entry')
            operation = ''
            if hasattr(task_entry, 'metadata') and task_entry.metadata:
                operation = task_entry.metadata.get('operation', '')
            if not operation and hasattr(task_entry, 'content'):
                operation = str(task_entry.content)

            specialist_type = self._determine_specialist(operation)
            intention.metadata['specialist_type'] = specialist_type
            intention.advance()

        elif action == 'route':
            task_entry = intention.metadata.get('task_entry')
            specialist_type = intention.metadata.get('specialist_type', 'prime_field')
            specialist = self._get_specialist(specialist_type)
            self._update_routing_stats(specialist_type)
            self.tasks_routed += 1

            try:
                result = specialist.process(task_entry)
                intention.metadata['result'] = result
                self.tasks_completed += 1
            except Exception as e:
                intention.metadata['result'] = {'success': False, 'error': str(e)}
                self.tasks_failed += 1

            intention.advance()

        elif action == 'post_result':
            result = intention.metadata.get('result')
            if self.blackboard and result:
                if hasattr(result, 'entry_type'):
                    self.blackboard.post(result)
            intention.complete()

    # ========================================
    # Statistics
    # ========================================

    def get_stats(self) -> Dict[str, int]:
        """Return routing statistics."""
        return {
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'prime_field_routes': self.prime_field_routes,
            'extension_field_routes': self.extension_field_routes,
            'irreducible_routes': self.irreducible_routes,
            'field_arithmetic_routes': self.field_arithmetic_routes,
            'minimal_poly_routes': self.minimal_poly_routes,
            'isomorphism_routes': self.isomorphism_routes,
            'galois_theory_routes': self.galois_theory_routes,
        }
