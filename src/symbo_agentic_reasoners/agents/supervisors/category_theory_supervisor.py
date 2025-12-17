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
CATEGORY THEORY SUPERVISOR (Tier 2)
===================================

Routes category theory problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class CategoryTheorySupervisor(BDIAgent):
    """
    Supervisor for category theory domain.

    Routes to:
    - MorphismSpecialist: Categories, morphisms, composition
    - FunctorSpecialist: Functors, natural transformations
    - UniversalPropertiesSpecialist: Products, limits, colimits

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    MORPHISM_KEYWORDS = ['morphism', 'composition', 'identity', 'isomorphism',
                         'monomorphism', 'epimorphism', 'endomorphism', 'automorphism',
                         'hom set', 'arrow', 'category']
    FUNCTOR_KEYWORDS = ['functor', 'natural transformation', 'covariant', 'contravariant',
                        'forgetful', 'free', 'representable', 'yoneda']
    UNIVERSAL_KEYWORDS = ['product', 'coproduct', 'equalizer', 'coequalizer',
                          'pullback', 'pushout', 'limit', 'colimit', 'terminal',
                          'initial', 'exponential', 'cartesian closed']

    def __init__(self, agent_id: str = 'category_theory_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._morphism_specialist = None
        self._functor_specialist = None
        self._universal_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.category_theory',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='morphism_functor_universal_routing'
            ))

        logger.info(f"[{agent_id}] Category Theory Supervisor initialized")

    @property
    def morphism_specialist(self):
        """Lazy load morphism specialist."""
        if self._morphism_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.category_theory import MorphismSpecialist
            self._morphism_specialist = MorphismSpecialist(
                agent_id='morphism_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._morphism_specialist

    @property
    def functor_specialist(self):
        """Lazy load functor specialist."""
        if self._functor_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.category_theory import FunctorSpecialist
            self._functor_specialist = FunctorSpecialist(
                agent_id='functor_specialist_001',
                df=self.df,
                blackboard=self.blackboard,
                morphism_specialist=self.morphism_specialist
            )
        return self._functor_specialist

    @property
    def universal_specialist(self):
        """Lazy load universal properties specialist."""
        if self._universal_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.category_theory import UniversalPropertiesSpecialist
            self._universal_specialist = UniversalPropertiesSpecialist(
                agent_id='universal_properties_specialist_001',
                df=self.df,
                blackboard=self.blackboard,
                morphism_specialist=self.morphism_specialist
            )
        return self._universal_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for category theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['category_theory'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['functor'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['morphism'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['universal'], status=EntryStatus.PENDING)

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
                plan_id=f'route_category_{task_id}',
                steps=steps,
                target_desire='category_theory_routing',
                metadata={'task_id': task_id, 'task_entry': task, 'target': target_specialist}
            )
            new_intentions.append(intention)
        return new_intentions

    def _determine_specialist(self, task) -> str:
        """Determine which specialist should handle this task."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        content = str(task.content).lower() if hasattr(task, 'content') else ''
        operation = metadata.get('operation', '').lower()

        combined_text = f"{content} {operation}"

        # Check explicit operations
        morphism_ops = ['compose', 'identity', 'classify', 'create_category', 'hom_set']
        functor_ops = ['functor', 'natural_transform', 'compose_functors', 'verify_functor']
        universal_ops = ['product', 'coproduct', 'equalizer', 'pullback', 'pushout',
                         'limit', 'colimit', 'terminal', 'initial', 'exponential']

        if operation in morphism_ops:
            return 'morphism'
        if operation in functor_ops:
            return 'functor'
        if operation in universal_ops:
            return 'universal'

        # Check keywords
        morphism_score = sum(1 for kw in self.MORPHISM_KEYWORDS if kw in combined_text)
        functor_score = sum(1 for kw in self.FUNCTOR_KEYWORDS if kw in combined_text)
        universal_score = sum(1 for kw in self.UNIVERSAL_KEYWORDS if kw in combined_text)

        scores = {
            'morphism': morphism_score,
            'functor': functor_score,
            'universal': universal_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'morphism'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'morphism')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'morphism':
                specialist = self.morphism_specialist
            elif target == 'functor':
                specialist = self.functor_specialist
            else:
                specialist = self.universal_specialist

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for category theory problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Morphism operations
        if problem_type == 'create_category':
            return self.morphism_specialist.create_category(
                problem.get('name'),
                problem.get('objects', []),
                problem.get('morphisms', [])
            )
        if problem_type == 'compose':
            return self.morphism_specialist.compose_morphisms(
                problem.get('category_name'),
                problem.get('g'),
                problem.get('f')
            )
        if problem_type == 'classify':
            return self.morphism_specialist.classify_morphism(
                problem.get('category_name'),
                problem.get('morphism_name')
            )
        if problem_type == 'hom_set':
            return self.morphism_specialist.get_hom_set(
                problem.get('category_name'),
                problem.get('source'),
                problem.get('target')
            )

        # Functor operations
        if problem_type == 'create_functor':
            return self.functor_specialist.create_functor(
                problem.get('name'),
                problem.get('source_category'),
                problem.get('target_category'),
                problem.get('object_map', {}),
                problem.get('morphism_map', {}),
                problem.get('is_contravariant', False)
            )
        if problem_type == 'compose_functors':
            return self.functor_specialist.compose_functors(
                problem.get('g'),
                problem.get('f')
            )
        if problem_type == 'natural_transformation':
            return self.functor_specialist.create_natural_transformation(
                problem.get('name'),
                problem.get('source_functor'),
                problem.get('target_functor'),
                problem.get('components', {})
            )
        if problem_type == 'identity_functor':
            return self.functor_specialist.create_identity_functor(
                problem.get('category_name')
            )

        # Universal property operations
        if problem_type == 'product':
            return self.universal_specialist.construct_product(
                problem.get('category_name'),
                problem.get('objects', [])
            )
        if problem_type == 'coproduct':
            return self.universal_specialist.construct_coproduct(
                problem.get('category_name'),
                problem.get('objects', [])
            )
        if problem_type == 'equalizer':
            return self.universal_specialist.construct_equalizer(
                problem.get('category_name'),
                problem.get('f'),
                problem.get('g')
            )
        if problem_type == 'pullback':
            return self.universal_specialist.construct_pullback(
                problem.get('category_name'),
                problem.get('f'),
                problem.get('g')
            )
        if problem_type == 'pushout':
            return self.universal_specialist.construct_pushout(
                problem.get('category_name'),
                problem.get('f'),
                problem.get('g')
            )
        if problem_type == 'terminal':
            return self.universal_specialist.find_terminal(
                problem.get('category_name')
            )
        if problem_type == 'initial':
            return self.universal_specialist.find_initial(
                problem.get('category_name')
            )
        if problem_type == 'limit':
            return self.universal_specialist.construct_limit(
                problem.get('category_name'),
                problem.get('diagram', {})
            )
        if problem_type == 'colimit':
            return self.universal_specialist.construct_colimit(
                problem.get('category_name'),
                problem.get('diagram', {})
            )

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['morphism', 'functor', 'universal']
        }

        if self._morphism_specialist:
            stats['morphism_tasks'] = self._morphism_specialist.tasks_executed
            stats['categories_defined'] = len(self._morphism_specialist.categories)
        if self._functor_specialist:
            stats['functor_tasks'] = self._functor_specialist.tasks_executed
            stats['functors_defined'] = len(self._functor_specialist.functors)
        if self._universal_specialist:
            stats['universal_tasks'] = self._universal_specialist.tasks_executed
            stats['constructions_defined'] = len(self._universal_specialist.constructions)

        return stats
