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
ELEMENTARY NUMBER THEORY SUPERVISOR (Tier 2)
=============================================

Routes elementary number theory tasks to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

ROUTING STRATEGY:
----------------
Elementary Number Theory:
- Congruences: Linear/quadratic congruences, Chinese Remainder Theorem
- Continued Fractions: CF expansion, convergents, quadratic irrationals
- Pell Equations: Fundamental solutions, negative Pell
- Tonelli-Shanks: Modular square roots
- Lifting the Exponent: LTE lemma, p-adic valuations
- Diophantine Equations: Linear Diophantine, Pythagorean triples
- Quadratic Residues: Legendre symbol, quadratic reciprocity

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


class ElementaryNumberTheorySupervisor(BDIAgent):
    """
    Supervisor for elementary number theory domain.

    Routes to 7 specialists:
    - CongruenceSpecialist: Linear/quadratic congruences, CRT
    - ContinuedFractionsSpecialist: CF expansion, convergents
    - PellEquationSpecialist: Fundamental solutions, solution generation
    - TonelliShanksSpecialist: Modular square roots
    - LiftingTheExponentSpecialist: LTE lemma, p-adic valuations
    - DiophantineBasicSpecialist: Linear Diophantine, Bezout
    - QuadraticResidueSpecialist: Legendre symbol, quadratic reciprocity

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing (priority ordered, most specific first)
    TONELLI_SHANKS_KW = ['tonelli', 'shanks', 'modular square root', 'sqrt mod',
                         'quadratic residue modulo', 'square root modulo prime']

    LIFTING_EXPONENT_KW = ['lte', 'lifting the exponent', 'p-adic valuation',
                           'v_p(', 'valuation', 'exponent lifting', 'p-adic']

    PELL_KW = ['pell', 'pell equation', 'x^2 - dy^2', 'fundamental solution',
               'negative pell', 'pell solver']

    CONTINUED_FRACTION_KW = ['continued fraction', 'cf expansion', 'convergent',
                             'periodic cf', 'quadratic irrational', 'cf convergent']

    QUADRATIC_RESIDUE_KW = ['quadratic residue', 'legendre symbol', 'jacobi symbol',
                            'quadratic reciprocity', 'euler criterion', 'legendre']

    CONGRUENCE_KW = ['congruence', ' mod ', 'modulo', 'chinese remainder', 'crt',
                     'linear congruence', 'quadratic congruence', 'system of congruences',
                     'solve mod']

    DIOPHANTINE_KW = ['diophantine', 'bezout', 'linear diophantine', 'integer solutions',
                      'pythagorean triple', 'ax + by = c', 'integer equation']

    def __init__(self, agent_id: str = 'elementary_nt_supervisor_001',
                 df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.congruence_routes = 0
        self.continued_fraction_routes = 0
        self.pell_routes = 0
        self.tonelli_shanks_routes = 0
        self.lte_routes = 0
        self.diophantine_routes = 0
        self.quadratic_residue_routes = 0

        # Lazy-loaded specialists
        self._congruence_specialist = None
        self._continued_fractions_specialist = None
        self._pell_equation_specialist = None
        self._tonelli_shanks_specialist = None
        self._lte_specialist = None
        self._diophantine_basic_specialist = None
        self._quadratic_residue_specialist = None

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.algebra.elementary_nt',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            instance=self,
            type='supervisor',
            domain='elementary_number_theory',
            tier='2'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.algebra.elementary_nt (supervisor)")

    # ==========================================================================
    # LAZY-LOADED SPECIALIST PROPERTIES
    # ==========================================================================

    @property
    def congruence_specialist(self):
        """Lazy load Congruence Specialist."""
        if self._congruence_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import CongruenceSpecialist
            self._congruence_specialist = CongruenceSpecialist(
                agent_id='congruence_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._congruence_specialist

    @property
    def continued_fractions_specialist(self):
        """Lazy load Continued Fractions Specialist."""
        if self._continued_fractions_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import ContinuedFractionsSpecialist
            self._continued_fractions_specialist = ContinuedFractionsSpecialist(
                agent_id='continued_fractions_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._continued_fractions_specialist

    @property
    def pell_equation_specialist(self):
        """Lazy load Pell Equation Specialist."""
        if self._pell_equation_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import PellEquationSpecialist
            self._pell_equation_specialist = PellEquationSpecialist(
                agent_id='pell_equation_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._pell_equation_specialist

    @property
    def tonelli_shanks_specialist(self):
        """Lazy load Tonelli-Shanks Specialist."""
        if self._tonelli_shanks_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import TonelliShanksSpecialist
            self._tonelli_shanks_specialist = TonelliShanksSpecialist(
                agent_id='tonelli_shanks_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._tonelli_shanks_specialist

    @property
    def lte_specialist(self):
        """Lazy load Lifting the Exponent Specialist."""
        if self._lte_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import LiftingTheExponentSpecialist
            self._lte_specialist = LiftingTheExponentSpecialist(
                agent_id='lte_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._lte_specialist

    @property
    def diophantine_basic_specialist(self):
        """Lazy load Diophantine Basic Specialist."""
        if self._diophantine_basic_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import DiophantineBasicSpecialist
            self._diophantine_basic_specialist = DiophantineBasicSpecialist(
                agent_id='diophantine_basic_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._diophantine_basic_specialist

    @property
    def quadratic_residue_specialist(self):
        """Lazy load Quadratic Residue Specialist."""
        if self._quadratic_residue_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import QuadraticResidueSpecialist
            self._quadratic_residue_specialist = QuadraticResidueSpecialist(
                agent_id='quadratic_residue_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._quadratic_residue_specialist

    def _determine_specialist(self, task_entry: Any) -> str:
        """
        Determine which specialist should handle the task.

        Priority order (first match wins):
        1. Tonelli-Shanks (most specific)
        2. Lifting the Exponent
        3. Pell Equations
        4. Continued Fractions
        5. Quadratic Residues
        6. Congruences
        7. Diophantine (default)
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        # Priority 1: Tonelli-Shanks
        if any(kw in raw_input for kw in self.TONELLI_SHANKS_KW):
            self.tonelli_shanks_routes += 1
            return 'tonelli_shanks'

        # Priority 2: Lifting the Exponent
        if any(kw in raw_input for kw in self.LIFTING_EXPONENT_KW):
            self.lte_routes += 1
            return 'lte'

        # Priority 3: Pell Equations
        if any(kw in raw_input for kw in self.PELL_KW):
            self.pell_routes += 1
            return 'pell'

        # Priority 4: Continued Fractions
        if any(kw in raw_input for kw in self.CONTINUED_FRACTION_KW):
            self.continued_fraction_routes += 1
            return 'continued_fractions'

        # Priority 5: Quadratic Residues
        if any(kw in raw_input for kw in self.QUADRATIC_RESIDUE_KW):
            self.quadratic_residue_routes += 1
            return 'quadratic_residue'

        # Priority 6: Congruences
        if any(kw in raw_input for kw in self.CONGRUENCE_KW):
            self.congruence_routes += 1
            return 'congruence'

        # Priority 7: Diophantine (default)
        self.diophantine_routes += 1
        return 'diophantine'

    def _get_specialist(self, specialist_name: str):
        """Get specialist instance by name."""
        specialist_map = {
            'congruence': self.congruence_specialist,
            'continued_fractions': self.continued_fractions_specialist,
            'pell': self.pell_equation_specialist,
            'tonelli_shanks': self.tonelli_shanks_specialist,
            'lte': self.lte_specialist,
            'diophantine': self.diophantine_basic_specialist,
            'quadratic_residue': self.quadratic_residue_specialist
        }
        return specialist_map.get(specialist_name)

    def process(self, task_entry: Any) -> Any:
        """Process elementary NT task by routing to specialist."""
        specialist_name = self._determine_specialist(task_entry)
        specialist = self._get_specialist(specialist_name)

        if specialist:
            self.tasks_routed += 1
            return specialist.process(task_entry)
        else:
            self.tasks_failed += 1
            return {'error': f'No specialist for {specialist_name}'}

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor for elementary NT tasks."""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(
                tags=['elementary_nt', 'congruence', 'pell'],
                status=EntryStatus.PENDING
            )

            for task in tasks:
                belief_key = f'pending_ent_{task.entry_id}'
                if not self.has_belief(belief_key) and not self.has_belief(f'routed_{task.entry_id}'):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_ent_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            specialist_name = self._determine_specialist(task)

            intention = Intention(
                plan_id=f'route_ent_{task_id}',
                steps=['route_to_specialist'],
                target_desire='route_elementary_nt_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'specialist_name': specialist_name
                }
            )

            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to specialist."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        specialist_name = intention.metadata.get('specialist_name')

        if action == 'route_to_specialist':
            specialist = self._get_specialist(specialist_name)
            if specialist:
                specialist.update_beliefs()
                intentions = specialist.deliberate()
                if intentions:
                    specialist.execute_step(intentions[0])
                self.tasks_completed += 1
            else:
                self.tasks_failed += 1

            self.remove_belief(f'pending_ent_{intention.metadata["task_id"]}')
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Get supervisor statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'congruence_routes': self.congruence_routes,
            'continued_fraction_routes': self.continued_fraction_routes,
            'pell_routes': self.pell_routes,
            'tonelli_shanks_routes': self.tonelli_shanks_routes,
            'lte_routes': self.lte_routes,
            'diophantine_routes': self.diophantine_routes,
            'quadratic_residue_routes': self.quadratic_residue_routes,
            'tier': '2',
            'type': 'supervisor',
            'domain': 'elementary_number_theory'
        })
        return stats


if __name__ == "__main__":
    """Test Elementary Number Theory Supervisor"""
    print("=" * 80)
    print("ELEMENTARY NUMBER THEORY SUPERVISOR TEST")
    print("=" * 80)

    supervisor = ElementaryNumberTheorySupervisor()

    class MockEntry:
        def __init__(self, raw_input):
            self.metadata = {'raw_input': raw_input}

    test_cases = [
        ("Solve 3x ≡ 5 mod 7", "congruence"),
        ("Find continued fraction of √23", "continued_fractions"),
        ("Solve Pell equation x² - 2y² = 1", "pell"),
        ("Find sqrt(7) mod 11 using Tonelli-Shanks", "tonelli_shanks"),
        ("Compute v_3(10^5 - 1) using LTE", "lte"),
        ("Solve 3x + 5y = 1", "diophantine"),
        ("Compute Legendre symbol (2/7)", "quadratic_residue")
    ]

    print("\nRouting decisions:")
    for test, expected in test_cases:
        decision = supervisor._determine_specialist(MockEntry(test))
        status = 'OK' if expected in decision else 'MISMATCH'
        print(f"  [{status}] \"{test[:40]}...\" -> {decision}")
