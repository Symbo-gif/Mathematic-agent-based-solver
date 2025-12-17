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
OPTIMIZATION SUPERVISOR (Tier 2)
================================

Routes optimization problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class OptimizationSupervisor(BDIAgent):
    """
    Supervisor for optimization domain.

    Routes to:
    - LinearProgrammingSpecialist: Simplex, LP problems
    - ConvexOptimizationSpecialist: Gradient descent, Newton, QP
    - CombinatorialOptimizationSpecialist: Knapsack, TSP, assignment

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    LP_KEYWORDS = ['simplex', 'linear program', 'lp', 'constraint', 'slack', 'dual']
    CONVEX_KEYWORDS = ['gradient', 'newton', 'convex', 'quadratic program', 'qp',
                       'least squares', 'descent', 'hessian']
    COMBINATORIAL_KEYWORDS = ['knapsack', 'tsp', 'traveling', 'assignment', 'hungarian',
                               'set cover', 'bin pack', 'greedy', 'combinatorial']

    def __init__(self, agent_id: str = 'optimization_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._lp_specialist = None
        self._convex_specialist = None
        self._combinatorial_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.optimization',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='lp_convex_combinatorial_routing'
            ))

        logger.info(f"[{agent_id}] Optimization Supervisor initialized")

    @property
    def lp_specialist(self):
        """Lazy load linear programming specialist."""
        if self._lp_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.optimization import LinearProgrammingSpecialist
            self._lp_specialist = LinearProgrammingSpecialist(
                agent_id='lp_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._lp_specialist

    @property
    def convex_specialist(self):
        """Lazy load convex optimization specialist."""
        if self._convex_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.optimization import ConvexOptimizationSpecialist
            self._convex_specialist = ConvexOptimizationSpecialist(
                agent_id='convex_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._convex_specialist

    @property
    def combinatorial_specialist(self):
        """Lazy load combinatorial optimization specialist."""
        if self._combinatorial_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.optimization import CombinatorialOptimizationSpecialist
            self._combinatorial_specialist = CombinatorialOptimizationSpecialist(
                agent_id='combinatorial_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._combinatorial_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for optimization tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['optimization'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['lp'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['convex'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['combinatorial'], status=EntryStatus.PENDING)

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
                plan_id=f'route_optimization_{task_id}',
                steps=steps,
                target_desire='optimization_routing',
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
        lp_ops = ['simplex', 'two_phase', 'sensitivity']
        convex_ops = ['gradient_descent', 'newton', 'quadratic_program', 'least_squares']
        combinatorial_ops = ['knapsack_01', 'knapsack_fractional', 'tsp_nearest_neighbor',
                             'tsp_2opt', 'assignment', 'set_cover', 'bin_packing']

        if operation in lp_ops:
            return 'lp'
        if operation in convex_ops:
            return 'convex'
        if operation in combinatorial_ops:
            return 'combinatorial'

        # Check keywords
        lp_score = sum(1 for kw in self.LP_KEYWORDS if kw in combined_text)
        convex_score = sum(1 for kw in self.CONVEX_KEYWORDS if kw in combined_text)
        combinatorial_score = sum(1 for kw in self.COMBINATORIAL_KEYWORDS if kw in combined_text)

        scores = {
            'lp': lp_score,
            'convex': convex_score,
            'combinatorial': combinatorial_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'convex'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'convex')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'lp':
                specialist = self.lp_specialist
            elif target == 'convex':
                specialist = self.convex_specialist
            else:
                specialist = self.combinatorial_specialist

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for optimization problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # LP operations
        if problem_type == 'simplex':
            return self.lp_specialist.simplex_solve(
                problem.get('objective', []),
                problem.get('constraints_lhs', []),
                problem.get('constraints_rhs', []),
                problem.get('maximize', True)
            )
        if problem_type == 'two_phase_simplex':
            return self.lp_specialist.two_phase_simplex(
                problem.get('objective', []),
                problem.get('constraints_lhs', []),
                problem.get('constraints_rhs', []),
                problem.get('maximize', True)
            )

        # Convex operations
        if problem_type == 'quadratic_program':
            return self.convex_specialist.quadratic_program(
                problem.get('Q', []),
                problem.get('c', []),
                problem.get('A'),
                problem.get('b')
            )
        if problem_type == 'least_squares':
            return self.convex_specialist.least_squares(
                problem.get('A', []),
                problem.get('b', [])
            )

        # Combinatorial operations
        if problem_type == 'knapsack_01':
            return self.combinatorial_specialist.knapsack_01(
                problem.get('weights', []),
                problem.get('values', []),
                problem.get('capacity', 0)
            )
        if problem_type == 'knapsack_fractional':
            return self.combinatorial_specialist.knapsack_fractional(
                problem.get('weights', []),
                problem.get('values', []),
                problem.get('capacity', 0)
            )
        if problem_type == 'tsp':
            return self.combinatorial_specialist.tsp_2opt(
                problem.get('distances', [])
            )
        if problem_type == 'assignment':
            return self.combinatorial_specialist.assignment_hungarian(
                problem.get('cost_matrix', [])
            )
        if problem_type == 'set_cover':
            return self.combinatorial_specialist.set_cover_greedy(
                problem.get('universe', []),
                problem.get('subsets', []),
                problem.get('costs')
            )
        if problem_type == 'bin_packing':
            return self.combinatorial_specialist.bin_packing_first_fit(
                problem.get('items', []),
                problem.get('bin_capacity', 0)
            )

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['lp', 'convex', 'combinatorial']
        }

        if self._lp_specialist:
            stats['lp_tasks'] = self._lp_specialist.tasks_executed
        if self._convex_specialist:
            stats['convex_tasks'] = self._convex_specialist.tasks_executed
        if self._combinatorial_specialist:
            stats['combinatorial_tasks'] = self._combinatorial_specialist.tasks_executed

        return stats
