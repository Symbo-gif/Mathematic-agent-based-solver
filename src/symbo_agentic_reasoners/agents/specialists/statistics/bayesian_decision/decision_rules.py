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
DECISION RULES SPECIALIST (Tier 3)
==================================

Implements Bayesian decision theory, minimax rules, and admissibility analysis.
Handles Bayes risk computation, optimal decision rules, and complete class theorems.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from scipy.optimize import minimize, differential_evolution


class DecisionRulesSpecialist(BDIAgent):
    """
    Specialist for Bayesian decision rules and minimax theory.

    Capabilities:
    - Compute Bayes risk for decision rules
    - Find minimax decision rules
    - Check admissibility of decision rules
    - Find optimal Bayes rules
    - Compute posterior risk
    - Analyze complete class of decision rules
    """

    def __init__(self, agent_id='decision_rules_specialist_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        self.bayes_computations = 0
        self.minimax_computations = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.statistics.bayesian_decision.decision_rules',
                agent_id=self.agent_id,
                algorithm='bayes_minimax',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3',
                methods='bayes_risk_minimax_admissibility_optimal_rules'
            ))

        print(f"[{self.agent_id}] Decision Rules Specialist initialized")
        print(f"  Methods: Bayes risk, minimax rules, admissibility")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for decision rule tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = (self.blackboard.query_entries(tags=['decision_rule'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['bayes_risk'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['minimax'], status=EntryStatus.PENDING))

            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if (hasattr(task, 'metadata') and task.metadata and
                    task.metadata.get('assigned_agent') == self.agent_id and task not in tasks):
                    tasks.append(task)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if (not self.has_belief(f'claimed_task_{task.entry_id}') and
                    not self.has_belief(belief_key)):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create decision rule computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'bayes_risk')

            steps = ['claim_task', 'parse_parameters', 'compute_rule', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'decision_{operation}_{task_id}',
                steps=steps,
                target_desire='decision_rule_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        # Periodic belief update about decision patterns
        if self.tasks_executed > 0 and self.tasks_executed % 25 == 0:
            intent = Intention(
                plan_id=f'update_decision_patterns_{self.tasks_executed}',
                steps=['update_pattern_database'],
                target_desire='maintain_knowledge',
                metadata={'trigger': 'periodic'}
            )
            new_intentions.append(intent)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform decision rule computations."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_parameters':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                operation = metadata.get('operation', 'bayes_risk')

                params = {}
                if operation == 'bayes_risk':
                    params['loss_matrix'] = metadata.get('loss_matrix', [[0, 1], [1, 0]])
                    params['prior'] = metadata.get('prior', [0.5, 0.5])
                elif operation == 'minimax':
                    params['loss_matrix'] = metadata.get('loss_matrix', [[0, 1], [1, 0]])
                elif operation == 'admissibility':
                    params['decision_rule'] = metadata.get('decision_rule', lambda x: 0)
                    params['loss_matrix'] = metadata.get('loss_matrix', [[0, 1], [1, 0]])

                intention.metadata['params'] = params
                intention.advance()

            elif action == 'compute_rule':
                operation = intention.metadata.get('operation')
                params = intention.metadata.get('params', {})

                result = None
                if operation == 'bayes_risk':
                    result = self.compute_bayes_risk(
                        params.get('loss_matrix', [[0, 1], [1, 0]]),
                        params.get('prior', [0.5, 0.5])
                    )
                elif operation == 'minimax':
                    result = self.compute_minimax_rule(
                        params.get('loss_matrix', [[0, 1], [1, 0]])
                    )
                elif operation == 'admissibility':
                    result = self.check_admissibility(
                        params.get('decision_rule'),
                        params.get('loss_matrix', [[0, 1], [1, 0]])
                    )
                else:
                    result = {'operation': operation, 'status': 'not_implemented'}

                intention.metadata['result'] = result
                intention.advance()

            elif action == 'verify_result':
                result = intention.metadata.get('result')
                verified = result is not None and 'error' not in result
                intention.metadata['verified'] = verified
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(
                        EntryType.PARTIAL_RESULT,
                        create_variable(str(result)),
                        self.agent_id,
                        task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        ['decision_rule', 'result', task_id],
                        EntryStatus.COMPLETED,
                        {'result': result, 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            elif action == 'update_pattern_database':
                self.add_belief(
                    'decision_patterns_updated',
                    {'timestamp': self.tasks_executed, 'bayes': self.bayes_computations,
                     'minimax': self.minimax_computations},
                    confidence=0.9,
                    source='self_monitoring'
                )
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def process(self, task_entry):
        """
        Process a decision rule task (legacy interface for supervisor compatibility).

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Dict with computation result
        """
        self.tasks_executed += 1
        metadata = task_entry.get('metadata', {}) if isinstance(task_entry, dict) else {}
        operation = metadata.get('operation', 'bayes_risk')

        try:
            if operation == 'bayes_risk':
                loss_matrix = metadata.get('loss_matrix', [[0, 1], [1, 0]])
                prior = metadata.get('prior', [0.5, 0.5])
                return self.compute_bayes_risk(loss_matrix, prior)
            elif operation == 'minimax':
                loss_matrix = metadata.get('loss_matrix', [[0, 1], [1, 0]])
                return self.compute_minimax_rule(loss_matrix)
            else:
                return {'operation': operation, 'explanation': 'Decision rules computation'}
        except Exception as e:
            return {'error': str(e), 'operation': operation}

    # ==================== CORE COMPUTATIONAL METHODS ====================

    def compute_bayes_risk(self, loss_matrix: List[List[float]],
                          prior: List[float]) -> Dict[str, Any]:
        """
        Compute Bayes risk for a decision rule.

        Bayes risk: r(π, δ) = Σ_θ R(θ, δ) π(θ)
        where R(θ, δ) is the risk function and π(θ) is the prior.

        Args:
            loss_matrix: L[i][j] = loss when state is i, action is j
            prior: Prior distribution π(θ) over states

        Returns:
            Dict with Bayes risk and optimal decision rule

        Example:
            >>> loss = [[0, 1], [1, 0]]  # 0-1 loss
            >>> prior = [0.3, 0.7]
            >>> result = agent.compute_bayes_risk(loss, prior)
        """
        self.bayes_computations += 1

        loss_matrix = np.array(loss_matrix)
        prior = np.array(prior)

        # Validate
        if not np.allclose(prior.sum(), 1.0, atol=1e-6):
            return {'error': 'Prior must sum to 1', 'sum': float(prior.sum())}

        if np.any(prior < 0):
            return {'error': 'Prior must be non-negative'}

        n_states, n_actions = loss_matrix.shape

        if len(prior) != n_states:
            return {'error': f'Prior length {len(prior)} must match states {n_states}'}

        # Compute expected loss for each action
        expected_losses = []
        for action in range(n_actions):
            expected_loss = np.sum(prior * loss_matrix[:, action])
            expected_losses.append(expected_loss)

        # Optimal Bayes action minimizes expected loss
        optimal_action = int(np.argmin(expected_losses))
        bayes_risk = float(expected_losses[optimal_action])

        # Compute risk function R(θ, δ) for optimal rule
        risk_function = loss_matrix[:, optimal_action].tolist()

        return {
            'bayes_risk': bayes_risk,
            'optimal_action': optimal_action,
            'expected_losses': [float(x) for x in expected_losses],
            'risk_function': risk_function,
            'prior': prior.tolist(),
            'loss_matrix': loss_matrix.tolist()
        }

    def compute_minimax_rule(self, loss_matrix: List[List[float]]) -> Dict[str, Any]:
        """
        Compute minimax decision rule.

        Minimax rule: δ* = argmin_δ max_θ R(θ, δ)
        Minimizes worst-case risk over all states.

        Args:
            loss_matrix: L[i][j] = loss when state is i, action is j

        Returns:
            Dict with minimax action and worst-case risk

        Example:
            >>> loss = [[0, 1], [2, 0]]
            >>> result = agent.compute_minimax_rule(loss)
        """
        self.minimax_computations += 1

        loss_matrix = np.array(loss_matrix)
        n_states, n_actions = loss_matrix.shape

        # For pure strategies (deterministic rules)
        max_risks = []
        for action in range(n_actions):
            max_risk = np.max(loss_matrix[:, action])
            max_risks.append(max_risk)

        minimax_action = int(np.argmin(max_risks))
        minimax_risk = float(max_risks[minimax_action])

        # Also consider randomized strategies (mixed minimax)
        # Solve: min_p max_θ Σ_a p(a) L(θ, a)
        # This is a linear programming problem
        def worst_case_risk(action_probs):
            """Compute worst-case risk for randomized strategy."""
            expected_losses_per_state = loss_matrix @ action_probs
            return np.max(expected_losses_per_state)

        # Optimize over probability simplex
        from scipy.optimize import minimize

        # Constraint: probabilities sum to 1
        constraints = {'type': 'eq', 'fun': lambda p: np.sum(p) - 1}
        bounds = [(0, 1) for _ in range(n_actions)]
        initial_guess = np.ones(n_actions) / n_actions

        result = minimize(
            worst_case_risk,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if result.success:
            mixed_minimax_risk = float(result.fun)
            mixed_strategy = result.x.tolist()
        else:
            mixed_minimax_risk = minimax_risk
            mixed_strategy = [1.0 if i == minimax_action else 0.0 for i in range(n_actions)]

        return {
            'minimax_action': minimax_action,
            'minimax_risk': minimax_risk,
            'max_risks_per_action': [float(x) for x in max_risks],
            'mixed_minimax_risk': mixed_minimax_risk,
            'mixed_strategy': [float(x) for x in mixed_strategy],
            'loss_matrix': loss_matrix.tolist()
        }

    def check_admissibility(self, decision_rule: Callable[[Any], int],
                           loss_matrix: List[List[float]],
                           n_samples: int = 100) -> Dict[str, Any]:
        """
        Check if a decision rule is admissible.

        A rule δ is admissible if there is no rule δ' such that:
        R(θ, δ') ≤ R(θ, δ) for all θ, with strict inequality for some θ.

        Args:
            decision_rule: Function mapping observations to actions
            loss_matrix: L[i][j] = loss when state is i, action is j
            n_samples: Number of samples to test

        Returns:
            Dict with admissibility status

        Note:
            This is a heuristic check. Full admissibility requires checking all possible rules.
        """
        loss_matrix = np.array(loss_matrix)
        n_states, n_actions = loss_matrix.shape

        # Compute risk function for given rule
        # For simplicity, assume rule is deterministic per state
        try:
            rule_actions = [decision_rule(theta) for theta in range(n_states)]
        except:
            # If rule doesn't accept state indices, use default
            rule_actions = [0] * n_states

        rule_risk = np.array([loss_matrix[theta, action]
                             for theta, action in enumerate(rule_actions)])

        # Check if any other pure strategy dominates
        is_admissible = True
        dominating_actions = []

        for action in range(n_actions):
            action_risk = loss_matrix[:, action]

            # Check if this action dominates the rule
            if (np.all(action_risk <= rule_risk) and
                np.any(action_risk < rule_risk)):
                is_admissible = False
                dominating_actions.append({
                    'action': int(action),
                    'risk': action_risk.tolist(),
                    'improvement': (rule_risk - action_risk).tolist()
                })

        return {
            'is_admissible': is_admissible,
            'rule_risk': rule_risk.tolist(),
            'dominating_actions': dominating_actions,
            'n_states': n_states,
            'n_actions': n_actions
        }

    def find_bayes_rule(self, loss_matrix: List[List[float]],
                       prior: List[float]) -> Dict[str, Any]:
        """
        Find optimal Bayes rule for given prior and loss function.

        The Bayes rule minimizes expected loss with respect to the prior.

        Args:
            loss_matrix: L[i][j] = loss when state is i, action is j
            prior: Prior distribution over states

        Returns:
            Dict with optimal Bayes rule
        """
        # This is essentially the same as compute_bayes_risk
        result = self.compute_bayes_risk(loss_matrix, prior)

        # Add rule specification
        if 'error' not in result:
            optimal_action = result['optimal_action']
            result['bayes_rule'] = {
                'type': 'constant',
                'action': optimal_action,
                'description': f'Always choose action {optimal_action}'
            }

        return result

    def compute_posterior_risk(self, loss_matrix: List[List[float]],
                              posterior: List[float]) -> Dict[str, Any]:
        """
        Compute posterior expected loss for each action.

        Given posterior distribution p(θ|x), compute:
        ρ(a|x) = Σ_θ L(θ, a) p(θ|x)

        Optimal action: a* = argmin_a ρ(a|x)

        Args:
            loss_matrix: L[i][j] = loss when state is i, action is j
            posterior: Posterior distribution p(θ|x)

        Returns:
            Dict with posterior risks and optimal action
        """
        loss_matrix = np.array(loss_matrix)
        posterior = np.array(posterior)

        # Validate posterior
        if not np.allclose(posterior.sum(), 1.0, atol=1e-6):
            return {'error': 'Posterior must sum to 1', 'sum': float(posterior.sum())}

        n_states, n_actions = loss_matrix.shape

        if len(posterior) != n_states:
            return {'error': f'Posterior length {len(posterior)} must match states {n_states}'}

        # Compute posterior risk for each action
        posterior_risks = []
        for action in range(n_actions):
            risk = np.sum(posterior * loss_matrix[:, action])
            posterior_risks.append(float(risk))

        optimal_action = int(np.argmin(posterior_risks))
        min_risk = posterior_risks[optimal_action]

        return {
            'posterior_risks': posterior_risks,
            'optimal_action': optimal_action,
            'minimum_risk': min_risk,
            'posterior': posterior.tolist()
        }

    def determine_complete_class(self, loss_matrix: List[List[float]],
                                 prior_grid: Optional[List[List[float]]] = None) -> Dict[str, Any]:
        """
        Determine complete class of decision rules.

        A class of rules is complete if for any rule outside the class,
        there exists a rule in the class that dominates it.

        For finite action spaces, the complete class consists of:
        - All Bayes rules (for various priors)
        - All admissible rules

        Args:
            loss_matrix: L[i][j] = loss when state is i, action is j
            prior_grid: Grid of priors to test (optional)

        Returns:
            Dict with complete class characterization
        """
        loss_matrix = np.array(loss_matrix)
        n_states, n_actions = loss_matrix.shape

        # Generate grid of priors if not provided
        if prior_grid is None:
            n_grid = 10
            if n_states == 2:
                prior_grid = [[p, 1-p] for p in np.linspace(0, 1, n_grid)]
            else:
                # Use random priors for higher dimensions
                prior_grid = []
                for _ in range(n_grid ** 2):
                    p = np.random.dirichlet(np.ones(n_states))
                    prior_grid.append(p.tolist())

        # Find Bayes rules for each prior
        bayes_rules = []
        bayes_actions = set()

        for prior in prior_grid:
            result = self.find_bayes_rule(loss_matrix, prior)
            if 'error' not in result:
                action = result['optimal_action']
                bayes_actions.add(action)
                bayes_rules.append({
                    'prior': prior,
                    'action': action,
                    'risk': result['bayes_risk']
                })

        # Check admissibility of all pure strategies
        admissible_actions = []
        for action in range(n_actions):
            rule = lambda x, a=action: a
            result = self.check_admissibility(rule, loss_matrix)
            if result['is_admissible']:
                admissible_actions.append(action)

        # Complete class consists of Bayes and admissible rules
        complete_class_actions = sorted(bayes_actions.union(set(admissible_actions)))

        return {
            'complete_class_actions': complete_class_actions,
            'bayes_actions': sorted(bayes_actions),
            'admissible_actions': admissible_actions,
            'n_bayes_rules_tested': len(bayes_rules),
            'is_complete': len(complete_class_actions) >= len(admissible_actions),
            'bayes_rules_sample': bayes_rules[:5]  # First 5 for brevity
        }

    def compute_regret(self, loss_matrix: List[List[float]],
                      action: int) -> Dict[str, Any]:
        """
        Compute regret for choosing a given action.

        Regret: R(θ, a) = L(θ, a) - min_a' L(θ, a')

        Args:
            loss_matrix: L[i][j] = loss when state is i, action is j
            action: Action to evaluate

        Returns:
            Dict with regret values per state
        """
        loss_matrix = np.array(loss_matrix)
        n_states, n_actions = loss_matrix.shape

        if action >= n_actions:
            return {'error': f'Action {action} out of range [0, {n_actions-1}]'}

        # Compute minimum loss for each state
        min_losses = np.min(loss_matrix, axis=1)

        # Compute regret for given action
        action_losses = loss_matrix[:, action]
        regrets = action_losses - min_losses

        max_regret = float(np.max(regrets))
        avg_regret = float(np.mean(regrets))

        return {
            'regrets': regrets.tolist(),
            'max_regret': max_regret,
            'average_regret': avg_regret,
            'action': action,
            'losses': action_losses.tolist(),
            'optimal_losses': min_losses.tolist()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve agent statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'bayes_computations': self.bayes_computations,
            'minimax_computations': self.minimax_computations
        })
        return stats
