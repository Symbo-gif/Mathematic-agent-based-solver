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
ALGEBRAIC NUMBER THEORY SUPERVISOR (Tier 2)
===========================================

Routes algebraic number theory problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class AlgebraicNumberTheorySupervisor(BDIAgent):
    """
    Supervisor for algebraic number theory domain.

    Routes to:
    - NumberFieldsSpecialist: Quadratic fields, discriminant, ring of integers
    - IdealTheorySpecialist: Ideal class group, factorization of ideals
    - LocalFieldsSpecialist: p-adic valuation, Hensel's lemma
    - ClassFieldTheorySpecialist: Artin reciprocity, class field towers

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    NUMBER_FIELD_KEYWORDS = ['number field', 'quadratic field', 'discriminant', 'ring of integers',
                             'algebraic integer', 'field extension', 'minimal polynomial']
    IDEAL_KEYWORDS = ['ideal', 'prime ideal', 'class group', 'class number', 'factorization',
                      'minkowski bound', 'ideal norm', 'fractional ideal']
    LOCAL_KEYWORDS = ['p-adic', 'valuation', 'local field', 'hensel', 'completion',
                      'local-global', 'hasse principle']
    CLASS_FIELD_KEYWORDS = ['class field', 'artin', 'reciprocity', 'abelian extension',
                           'hilbert class field', 'ray class', 'conductor']

    def __init__(self, agent_id: str = 'algebraic_number_theory_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._number_fields_specialist = None
        self._ideal_specialist = None
        self._local_fields_specialist = None
        self._class_field_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.algebra.numbertheory.algebraic',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='number_fields_ideals_local_class_field_routing'
            ))

        logger.info(f"[{agent_id}] Algebraic Number Theory Supervisor initialized")

    @property
    def number_fields_specialist(self):
        """Lazy load number fields specialist."""
        if self._number_fields_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.algebraic.number_fields import NumberFieldsSpecialist
            self._number_fields_specialist = NumberFieldsSpecialist(
                agent_id='number_fields_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._number_fields_specialist

    @property
    def ideal_specialist(self):
        """Lazy load ideal theory specialist."""
        if self._ideal_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.algebraic.ideal_theory import IdealTheorySpecialist
            self._ideal_specialist = IdealTheorySpecialist(
                agent_id='ideal_theory_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._ideal_specialist

    @property
    def local_fields_specialist(self):
        """Lazy load local fields specialist."""
        if self._local_fields_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.algebraic.local_fields import LocalFieldsSpecialist
            self._local_fields_specialist = LocalFieldsSpecialist(
                agent_id='local_fields_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._local_fields_specialist

    @property
    def class_field_specialist(self):
        """Lazy load class field theory specialist."""
        if self._class_field_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.algebraic.class_field_theory import ClassFieldTheorySpecialist
            self._class_field_specialist = ClassFieldTheorySpecialist(
                agent_id='class_field_theory_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._class_field_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for algebraic number theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['algebraic_number_theory'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['number_field'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['ideal_theory'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['local_field'], status=EntryStatus.PENDING)

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
                plan_id=f'route_algebraic_nt_{task_id}',
                steps=steps,
                target_desire='algebraic_number_theory_routing',
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
        field_ops = ['discriminant', 'ring_of_integers', 'minimal_polynomial', 'field_extension']
        ideal_ops = ['class_number', 'ideal_factorization', 'minkowski_bound', 'ideal_norm']
        local_ops = ['p_adic', 'valuation', 'hensel', 'completion', 'hasse']
        class_field_ops = ['artin_reciprocity', 'hilbert_class_field', 'ray_class', 'conductor']

        if operation in field_ops:
            return 'number_fields'
        if operation in ideal_ops:
            return 'ideal'
        if operation in local_ops:
            return 'local'
        if operation in class_field_ops:
            return 'class_field'

        # Check keywords
        field_score = sum(1 for kw in self.NUMBER_FIELD_KEYWORDS if kw in combined_text)
        ideal_score = sum(1 for kw in self.IDEAL_KEYWORDS if kw in combined_text)
        local_score = sum(1 for kw in self.LOCAL_KEYWORDS if kw in combined_text)
        class_field_score = sum(1 for kw in self.CLASS_FIELD_KEYWORDS if kw in combined_text)

        scores = {
            'number_fields': field_score,
            'ideal': ideal_score,
            'local': local_score,
            'class_field': class_field_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'number_fields'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'number_fields')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'number_fields':
                specialist = self.number_fields_specialist
            elif target == 'ideal':
                specialist = self.ideal_specialist
            elif target == 'local':
                specialist = self.local_fields_specialist
            else:
                specialist = self.class_field_specialist

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for algebraic number theory problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Route to appropriate specialist based on problem type
        if any(kw in problem_type for kw in ['field', 'discriminant', 'ring', 'extension']):
            return self.number_fields_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['ideal', 'class', 'minkowski', 'factorization']):
            return self.ideal_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['p_adic', 'valuation', 'hensel', 'local', 'hasse']):
            return self.local_fields_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['artin', 'reciprocity', 'abelian', 'conductor']):
            return self.class_field_specialist.solve(problem)

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['number_fields', 'ideal', 'local', 'class_field']
        }

        if self._number_fields_specialist:
            stats['number_fields_tasks'] = getattr(self._number_fields_specialist, 'tasks_executed', 0)
        if self._ideal_specialist:
            stats['ideal_tasks'] = getattr(self._ideal_specialist, 'tasks_executed', 0)
        if self._local_fields_specialist:
            stats['local_tasks'] = getattr(self._local_fields_specialist, 'tasks_executed', 0)
        if self._class_field_specialist:
            stats['class_field_tasks'] = getattr(self._class_field_specialist, 'tasks_executed', 0)

        return stats
