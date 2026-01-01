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
INEQUALITIES & CONVEXITY SUPERVISOR (Tier 2)
============================================

Routes inequality and convexity problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

ROUTING STRATEGY:
----------------
Classical Inequalities:
- Cauchy-Schwarz: Inner products, correlations
- Hölder: Lp spaces, conjugate exponents
- Jensen: Convex functions, expectations
- Chebyshev: Probability bounds, sum inequalities
- Rearrangement: Ordering, majorization

Convex Analysis:
- Convex Sets: Convex hulls, extreme points
- Convex Functions: Convexity verification, tests
- Subgradients: Non-smooth optimization
- Separation: Hyperplanes, projections
- Proximal: Proximal operators, Moreau envelopes

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class InequalitiesConvexitySupervisor(BDIAgent):
    """
    Supervisor for inequalities and convexity domain.

    Routes to 10 specialists:
    - CauchySchwarzSpecialist: Inner product inequalities
    - HolderInequalitySpecialist: Lp norm inequalities
    - JensenInequalitySpecialist: Convex function inequalities
    - ChebyshevInequalitySpecialist: Probability and sum inequalities
    - RearrangementInequalitySpecialist: Ordering inequalities
    - ConvexSetSpecialist: Convex hull, extreme points
    - ConvexFunctionSpecialist: Convexity verification
    - SubgradientSpecialist: Non-smooth optimization
    - SeparationTheoremSpecialist: Hyperplane separation
    - ProximalOperatorSpecialist: Proximal mappings

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    CAUCHY_SCHWARZ_KW = ['cauchy', 'schwarz', 'inner product', 'dot product',
                         'correlation', 'cs inequality']
    HOLDER_KW = ['holder', 'hölder', 'conjugate exponent', 'lp space', 'lp norm',
                 'minkowski']
    JENSEN_KW = ['jensen', 'convex function inequality', 'weighted average',
                 'expectation inequality', 'log sum']
    CHEBYSHEV_KW = ['chebyshev', 'probability bound', 'variance', 'standard deviation',
                    'tail bound']
    REARRANGEMENT_KW = ['rearrangement', 'ordering', 'sort', 'majorization',
                        'karamata', 'hardy littlewood']

    CONVEX_SET_KW = ['convex set', 'convex hull', 'extreme point', 'polytope',
                     'vertex', 'convex combination']
    CONVEX_FUNC_KW = ['convex function', 'strictly convex', 'strongly convex',
                      'concave', 'convexity test', 'hessian']
    SUBGRADIENT_KW = ['subgradient', 'subdifferential', 'non-smooth', 'non smooth',
                      'optimality condition']
    SEPARATION_KW = ['separation', 'separating hyperplane', 'supporting hyperplane',
                     'projection', 'distance to set']
    PROXIMAL_KW = ['proximal', 'prox', 'moreau', 'proximal operator',
                   'soft threshold', 'shrinkage']

    def __init__(self, agent_id: str = 'inequalities_convexity_supervisor_001',
                 df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._cauchy_schwarz_specialist = None
        self._holder_specialist = None
        self._jensen_specialist = None
        self._chebyshev_specialist = None
        self._rearrangement_specialist = None
        self._convex_set_specialist = None
        self._convex_function_specialist = None
        self._subgradient_specialist = None
        self._separation_specialist = None
        self._proximal_specialist = None

        # Statistics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.inequalities_convexity',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='inequalities_convexity_routing'
            ))

        logger.info(f"[{agent_id}] Inequalities & Convexity Supervisor initialized")

    # =========================================================================
    # LAZY-LOADED SPECIALISTS
    # =========================================================================

    @property
    def cauchy_schwarz_specialist(self):
        """Lazy load Cauchy-Schwarz specialist."""
        if self._cauchy_schwarz_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import CauchySchwarzSpecialist
            self._cauchy_schwarz_specialist = CauchySchwarzSpecialist(
                agent_id='cauchy_schwarz_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._cauchy_schwarz_specialist

    @property
    def holder_specialist(self):
        """Lazy load Hölder inequality specialist."""
        if self._holder_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import HolderInequalitySpecialist
            self._holder_specialist = HolderInequalitySpecialist(
                agent_id='holder_inequality_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._holder_specialist

    @property
    def jensen_specialist(self):
        """Lazy load Jensen inequality specialist."""
        if self._jensen_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import JensenInequalitySpecialist
            self._jensen_specialist = JensenInequalitySpecialist(
                agent_id='jensen_inequality_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._jensen_specialist

    @property
    def chebyshev_specialist(self):
        """Lazy load Chebyshev inequality specialist."""
        if self._chebyshev_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import ChebyshevInequalitySpecialist
            self._chebyshev_specialist = ChebyshevInequalitySpecialist(
                agent_id='chebyshev_inequality_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._chebyshev_specialist

    @property
    def rearrangement_specialist(self):
        """Lazy load rearrangement inequality specialist."""
        if self._rearrangement_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import RearrangementInequalitySpecialist
            self._rearrangement_specialist = RearrangementInequalitySpecialist(
                agent_id='rearrangement_inequality_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._rearrangement_specialist

    @property
    def convex_set_specialist(self):
        """Lazy load convex set specialist."""
        if self._convex_set_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import ConvexSetSpecialist
            self._convex_set_specialist = ConvexSetSpecialist(
                agent_id='convex_set_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._convex_set_specialist

    @property
    def convex_function_specialist(self):
        """Lazy load convex function specialist."""
        if self._convex_function_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import ConvexFunctionSpecialist
            self._convex_function_specialist = ConvexFunctionSpecialist(
                agent_id='convex_function_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._convex_function_specialist

    @property
    def subgradient_specialist(self):
        """Lazy load subgradient specialist."""
        if self._subgradient_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import SubgradientSpecialist
            self._subgradient_specialist = SubgradientSpecialist(
                agent_id='subgradient_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._subgradient_specialist

    @property
    def separation_specialist(self):
        """Lazy load separation theorem specialist."""
        if self._separation_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import SeparationTheoremSpecialist
            self._separation_specialist = SeparationTheoremSpecialist(
                agent_id='separation_theorem_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._separation_specialist

    @property
    def proximal_specialist(self):
        """Lazy load proximal operator specialist."""
        if self._proximal_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.inequalities import ProximalOperatorSpecialist
            self._proximal_specialist = ProximalOperatorSpecialist(
                agent_id='proximal_operator_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._proximal_specialist

    # =========================================================================
    # ROUTING LOGIC
    # =========================================================================

    def _determine_specialist(self, task_entry: Any) -> str:
        """
        Determine which specialist should handle this task.

        Priority order (first match wins):
        1. Proximal operators (most specific)
        2. Separation theorems
        3. Subgradients
        4. Convex sets
        5. Convex functions
        6. Classical inequalities (Cauchy-Schwarz, Hölder, Jensen, Chebyshev, Rearrangement)

        Args:
            task_entry: Task to route

        Returns:
            Specialist name string
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        # Priority 1: Proximal operators (highly specific)
        if any(kw in raw_input for kw in self.PROXIMAL_KW):
            return 'proximal'

        # Priority 2: Separation theorems
        if any(kw in raw_input for kw in self.SEPARATION_KW):
            return 'separation'

        # Priority 3: Subgradients (for non-smooth optimization)
        if any(kw in raw_input for kw in self.SUBGRADIENT_KW):
            return 'subgradient'

        # Priority 4: Convex sets
        if any(kw in raw_input for kw in self.CONVEX_SET_KW):
            return 'convex_set'

        # Priority 5: Convex functions
        if any(kw in raw_input for kw in self.CONVEX_FUNC_KW):
            return 'convex_function'

        # Priority 6: Classical inequalities
        if any(kw in raw_input for kw in self.CAUCHY_SCHWARZ_KW):
            return 'cauchy_schwarz'

        if any(kw in raw_input for kw in self.HOLDER_KW):
            return 'holder'

        if any(kw in raw_input for kw in self.JENSEN_KW):
            return 'jensen'

        if any(kw in raw_input for kw in self.CHEBYSHEV_KW):
            return 'chebyshev'

        if any(kw in raw_input for kw in self.REARRANGEMENT_KW):
            return 'rearrangement'

        # Default: Convex function specialist (most general)
        logger.info(f"[{self.agent_id}] No specific match, defaulting to convex_function")
        return 'convex_function'

    def _get_specialist(self, specialist_name: str):
        """Get specialist instance by name."""
        specialist_map = {
            'cauchy_schwarz': self.cauchy_schwarz_specialist,
            'holder': self.holder_specialist,
            'jensen': self.jensen_specialist,
            'chebyshev': self.chebyshev_specialist,
            'rearrangement': self.rearrangement_specialist,
            'convex_set': self.convex_set_specialist,
            'convex_function': self.convex_function_specialist,
            'subgradient': self.subgradient_specialist,
            'separation': self.separation_specialist,
            'proximal': self.proximal_specialist
        }
        return specialist_map.get(specialist_name)

    # =========================================================================
    # BDI IMPLEMENTATION
    # =========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor for inequalities/convexity tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus

            tasks = self.blackboard.query_entries(tags=['inequalities'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['convexity'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['inequality'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['convex'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'routed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')

        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            target_specialist = self._determine_specialist(task)

            steps = ['route_task']
            intention = Intention(
                plan_id=f'route_inequality_{task_id}',
                steps=steps,
                target_desire='inequality_routing',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'target': target_specialist
                }
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Route task to specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target_name = intention.metadata.get('target')

            specialist = self._get_specialist(target_name)

            if specialist:
                try:
                    # Delegate to specialist
                    specialist.update_beliefs()
                    intentions = specialist.deliberate()

                    for spec_intention in intentions:
                        specialist.execute_step(spec_intention)

                    self.tasks_routed += 1
                    logger.info(f"[{self.agent_id}] Routed to {target_name}")

                    # Mark as routed
                    self.add_belief(f'routed_task_{task.entry_id}', True)

                except Exception as e:
                    logger.error(f"[{self.agent_id}] Routing error: {e}")
                    self.tasks_failed += 1
            else:
                logger.error(f"[{self.agent_id}] Unknown specialist: {target_name}")
                self.tasks_failed += 1

            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Get supervisor statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_completed / self.tasks_routed * 100)
                           if self.tasks_routed > 0 else 0.0,
            'tier': '2',
            'type': 'supervisor'
        }
