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
BAYESIAN DECISION THEORY SUPERVISOR (Tier 2)
============================================

Routes Bayesian decision theory problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class BayesianDecisionTheorySupervisor(BDIAgent):
    """
    Supervisor for Bayesian decision theory domain.

    Routes to:
    - UtilityTheorySpecialist: Utility functions, risk aversion, expected utility
    - DecisionRulesSpecialist: Bayesian decision rules, minimax, admissibility
    - SequentialDecisionSpecialist: Sequential analysis, stopping rules, dynamic programming

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    UTILITY_KEYWORDS = ['utility', 'expected utility', 'risk aversion', 'certainty equivalent',
                       'von neumann', 'preference', 'risk premium', 'utility function']
    DECISION_KEYWORDS = ['decision rule', 'bayes rule', 'minimax', 'admissible', 'loss function',
                        'risk', 'posterior risk', 'prior', 'likelihood']
    SEQUENTIAL_KEYWORDS = ['sequential', 'stopping rule', 'dynamic programming', 'bellman',
                          'value function', 'policy', 'optimal stopping', 'sprt']

    def __init__(self, agent_id: str = 'bayesian_decision_theory_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._utility_specialist = None
        self._decision_rules_specialist = None
        self._sequential_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.statistics.bayesian_decision',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='utility_decision_rules_sequential_routing'
            ))

        logger.info(f"[{agent_id}] Bayesian Decision Theory Supervisor initialized")

    @property
    def utility_specialist(self):
        """Lazy load utility theory specialist."""
        if self._utility_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_decision.utility_theory import UtilityTheorySpecialist
            self._utility_specialist = UtilityTheorySpecialist(
                agent_id='utility_theory_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._utility_specialist

    @property
    def decision_rules_specialist(self):
        """Lazy load decision rules specialist."""
        if self._decision_rules_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_decision.decision_rules import DecisionRulesSpecialist
            self._decision_rules_specialist = DecisionRulesSpecialist(
                agent_id='decision_rules_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._decision_rules_specialist

    @property
    def sequential_specialist(self):
        """Lazy load sequential decision specialist."""
        if self._sequential_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_decision.sequential_decision import SequentialDecisionSpecialist
            self._sequential_specialist = SequentialDecisionSpecialist(
                agent_id='sequential_decision_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._sequential_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for Bayesian decision theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['bayesian_decision'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['utility_theory'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['decision_rules'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['sequential_decision'], status=EntryStatus.PENDING)

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
                plan_id=f'route_bayesian_decision_{task_id}',
                steps=steps,
                target_desire='bayesian_decision_routing',
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
        utility_ops = ['expected_utility', 'risk_aversion', 'certainty_equivalent', 'utility_function']
        decision_ops = ['bayes_rule', 'minimax', 'loss_function', 'posterior_risk', 'admissible']
        sequential_ops = ['stopping_rule', 'dynamic_programming', 'bellman', 'optimal_stopping', 'sprt']

        if operation in utility_ops:
            return 'utility'
        if operation in decision_ops:
            return 'decision_rules'
        if operation in sequential_ops:
            return 'sequential'

        # Check keywords
        utility_score = sum(1 for kw in self.UTILITY_KEYWORDS if kw in combined_text)
        decision_score = sum(1 for kw in self.DECISION_KEYWORDS if kw in combined_text)
        sequential_score = sum(1 for kw in self.SEQUENTIAL_KEYWORDS if kw in combined_text)

        scores = {
            'utility': utility_score,
            'decision_rules': decision_score,
            'sequential': sequential_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'utility'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'utility')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'utility':
                specialist = self.utility_specialist
            elif target == 'decision_rules':
                specialist = self.decision_rules_specialist
            else:
                specialist = self.sequential_specialist

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for Bayesian decision theory problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Route to appropriate specialist based on problem type
        if any(kw in problem_type for kw in ['utility', 'risk', 'preference']):
            return self.utility_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['decision_rule', 'bayes', 'minimax', 'loss']):
            return self.decision_rules_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['sequential', 'stopping', 'dynamic', 'bellman']):
            return self.sequential_specialist.solve(problem)

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['utility', 'decision_rules', 'sequential']
        }

        if self._utility_specialist:
            stats['utility_tasks'] = getattr(self._utility_specialist, 'tasks_executed', 0)
        if self._decision_rules_specialist:
            stats['decision_rules_tasks'] = getattr(self._decision_rules_specialist, 'tasks_executed', 0)
        if self._sequential_specialist:
            stats['sequential_tasks'] = getattr(self._sequential_specialist, 'tasks_executed', 0)

        return stats
