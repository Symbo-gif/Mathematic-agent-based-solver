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
SEQUENTIAL DECISION SPECIALIST (Tier 3)
=======================================

Implements sequential decision theory: SPRT, optimal stopping, dynamic programming.
Handles multi-armed bandits, sequential probability ratio tests, and Bellman equations.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from scipy.stats import norm


class SequentialDecisionSpecialist(BDIAgent):
    """
    Specialist for sequential decision theory and dynamic programming.

    Capabilities:
    - Sequential Probability Ratio Test (SPRT)
    - Optimal stopping problems
    - Bellman equation solver
    - Wald bounds computation
    - Sequential policy evaluation
    - Value of information calculation
    - Multi-armed bandit strategies
    """

    def __init__(self, agent_id='sequential_decision_specialist_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        self.sprt_tests = 0
        self.stopping_problems = 0
        self.bellman_solves = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.statistics.bayesian_decision.sequential_decision',
                agent_id=self.agent_id,
                algorithm='sprt_optimal_stopping',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3',
                methods='sprt_optimal_stopping_bellman_voi_bandits'
            ))

        print(f"[{self.agent_id}] Sequential Decision Specialist initialized")
        print(f"  Methods: SPRT, optimal stopping, Bellman equations, bandits")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for sequential decision tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = (self.blackboard.query_entries(tags=['sprt'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['optimal_stopping'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['sequential'], status=EntryStatus.PENDING))

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
        """DELIBERATE: Create sequential decision computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'sprt')

            steps = ['claim_task', 'parse_parameters', 'compute_sequential', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'sequential_{operation}_{task_id}',
                steps=steps,
                target_desire='sequential_decision',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        # Periodic belief update about sequential patterns
        if self.tasks_executed > 0 and self.tasks_executed % 20 == 0:
            intent = Intention(
                plan_id=f'update_sequential_patterns_{self.tasks_executed}',
                steps=['update_pattern_database'],
                target_desire='maintain_knowledge',
                metadata={'trigger': 'periodic'}
            )
            new_intentions.append(intent)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform sequential decision computations."""
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
                operation = metadata.get('operation', 'sprt')

                params = {}
                if operation == 'sprt':
                    params['data'] = metadata.get('data', [0.5, 0.6, 0.7])
                    params['alpha'] = metadata.get('alpha', 0.05)
                    params['beta'] = metadata.get('beta', 0.05)
                elif operation == 'optimal_stopping':
                    params['values'] = metadata.get('values', [1, 2, 3, 2, 1])
                    params['discount'] = metadata.get('discount', 0.9)
                elif operation == 'bellman':
                    params['states'] = metadata.get('states', 5)
                    params['actions'] = metadata.get('actions', 2)

                intention.metadata['params'] = params
                intention.advance()

            elif action == 'compute_sequential':
                operation = intention.metadata.get('operation')
                params = intention.metadata.get('params', {})

                result = None
                if operation == 'sprt':
                    result = self.compute_sprt(
                        params.get('data', []),
                        params.get('alpha', 0.05),
                        params.get('beta', 0.05)
                    )
                elif operation == 'optimal_stopping':
                    result = self.compute_optimal_stopping_time(
                        params.get('values', []),
                        params.get('discount', 0.9)
                    )
                elif operation == 'bellman':
                    result = self.solve_bellman_equation(
                        params.get('states', 5),
                        params.get('actions', 2)
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
                        ['sequential_decision', 'result', task_id],
                        EntryStatus.COMPLETED,
                        {'result': result, 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            elif action == 'update_pattern_database':
                self.add_belief(
                    'sequential_patterns_updated',
                    {'timestamp': self.tasks_executed, 'sprt': self.sprt_tests,
                     'stopping': self.stopping_problems, 'bellman': self.bellman_solves},
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
        Process a sequential decision task (legacy interface for supervisor compatibility).

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Dict with computation result
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry.get('metadata', task_entry)

        operation = metadata.get('operation', 'sprt')

        try:
            if operation == 'sprt':
                data = metadata.get('data', [0.5, 0.6, 0.7])
                alpha = metadata.get('alpha', 0.05)
                beta = metadata.get('beta', 0.05)
                return self.compute_sprt(data, alpha, beta)
            elif operation == 'optimal_stopping':
                values = metadata.get('values', [1, 2, 3, 2, 1])
                discount = metadata.get('discount', 0.9)
                return self.compute_optimal_stopping_time(values, discount)
            else:
                return {'operation': operation, 'explanation': 'Sequential decision computation'}
        except Exception as e:
            return {'error': str(e), 'operation': operation}

    # ==================== CORE COMPUTATIONAL METHODS ====================

    def compute_sprt(self, data: List[float], alpha: float = 0.05, beta: float = 0.05,
                    h0_params: Optional[Dict] = None, h1_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Sequential Probability Ratio Test (Wald).

        Tests H0: θ = θ0 vs H1: θ = θ1 using sequential sampling.
        Stops when likelihood ratio crosses boundaries A or B.

        Args:
            data: Sequence of observations
            alpha: Type I error probability (false positive)
            beta: Type II error probability (false negative)
            h0_params: Parameters for H0 distribution (e.g., {'mu': 0, 'sigma': 1})
            h1_params: Parameters for H1 distribution (e.g., {'mu': 1, 'sigma': 1})

        Returns:
            Dict with SPRT decision and stopping time

        Example:
            >>> data = [0.5, 0.6, 0.7, 0.8, 0.9]
            >>> result = agent.compute_sprt(data, alpha=0.05, beta=0.05)
        """
        self.sprt_tests += 1

        if not data:
            return {'error': 'No data provided'}

        data = np.array(data)

        # Default: Normal distributions with known variance
        h0_params = h0_params or {'mu': 0.0, 'sigma': 1.0}
        h1_params = h1_params or {'mu': 1.0, 'sigma': 1.0}

        # Compute Wald bounds
        bounds = self.compute_wald_bounds(alpha, beta)
        A = bounds['lower_bound']
        B = bounds['upper_bound']

        # Compute log-likelihood ratio at each step
        log_likelihood_ratios = []
        cumulative_llr = 0.0

        mu0 = h0_params['mu']
        mu1 = h1_params['mu']
        sigma = h0_params['sigma']

        decision = 'continue'
        stopping_time = None

        for i, x in enumerate(data):
            # Log-likelihood ratio: log(L1(x) / L0(x))
            llr = ((x - mu0) ** 2 - (x - mu1) ** 2) / (2 * sigma ** 2)
            cumulative_llr += llr
            log_likelihood_ratios.append(float(cumulative_llr))

            # Check boundaries
            if cumulative_llr >= B:
                decision = 'reject_h0'
                stopping_time = i + 1
                break
            elif cumulative_llr <= A:
                decision = 'accept_h0'
                stopping_time = i + 1
                break

        if stopping_time is None:
            stopping_time = len(data)

        return {
            'decision': decision,
            'stopping_time': stopping_time,
            'log_likelihood_ratios': log_likelihood_ratios,
            'final_llr': float(cumulative_llr),
            'bounds': {'A': A, 'B': B},
            'alpha': alpha,
            'beta': beta,
            'h0_params': h0_params,
            'h1_params': h1_params
        }

    def compute_wald_bounds(self, alpha: float, beta: float) -> Dict[str, Any]:
        """
        Compute Wald bounds for SPRT.

        Lower bound A ≈ log(β / (1-α))
        Upper bound B ≈ log((1-β) / α)

        Args:
            alpha: Type I error probability
            beta: Type II error probability

        Returns:
            Dict with bounds A and B
        """
        if alpha <= 0 or alpha >= 1:
            return {'error': 'alpha must be in (0, 1)'}
        if beta <= 0 or beta >= 1:
            return {'error': 'beta must be in (0, 1)'}

        A = np.log(beta / (1 - alpha))
        B = np.log((1 - beta) / alpha)

        return {
            'lower_bound': float(A),
            'upper_bound': float(B),
            'alpha': alpha,
            'beta': beta
        }

    def compute_optimal_stopping_time(self, values: List[float],
                                     discount_factor: float = 0.9) -> Dict[str, Any]:
        """
        Solve optimal stopping problem using backward induction.

        Given sequence of values, find optimal time to stop to maximize
        expected discounted reward.

        V(t) = max{r(t), γ * E[V(t+1)]}

        Args:
            values: Sequence of potential rewards/values
            discount_factor: Discount factor γ ∈ [0, 1]

        Returns:
            Dict with optimal stopping time and value

        Example:
            >>> values = [1, 2, 3, 2, 1]
            >>> result = agent.compute_optimal_stopping_time(values, discount=0.9)
        """
        self.stopping_problems += 1

        if not values:
            return {'error': 'No values provided'}

        values = np.array(values)
        n = len(values)

        if discount_factor < 0 or discount_factor > 1:
            return {'error': 'Discount factor must be in [0, 1]'}

        # Backward induction
        V = np.zeros(n + 1)  # V[t] = value at time t
        stop_now = np.zeros(n, dtype=bool)

        # Terminal condition: V[n] = 0
        V[n] = 0

        # Backward induction
        for t in range(n - 1, -1, -1):
            # Value of stopping now
            stop_value = values[t]
            # Value of continuing
            continue_value = discount_factor * V[t + 1]

            if stop_value >= continue_value:
                V[t] = stop_value
                stop_now[t] = True
            else:
                V[t] = continue_value
                stop_now[t] = False

        # Find first stopping time
        optimal_stop_time = None
        for t in range(n):
            if stop_now[t]:
                optimal_stop_time = t
                break

        if optimal_stop_time is None:
            optimal_stop_time = n - 1  # Stop at last period

        return {
            'optimal_stopping_time': optimal_stop_time,
            'optimal_value': float(V[0]),
            'value_function': V[:n].tolist(),
            'stop_indicators': stop_now.tolist(),
            'realized_reward': float(values[optimal_stop_time]),
            'discount_factor': discount_factor
        }

    def solve_bellman_equation(self, states: int, actions: int,
                               rewards: Optional[np.ndarray] = None,
                               transitions: Optional[np.ndarray] = None,
                               discount: float = 0.9,
                               tolerance: float = 1e-6,
                               max_iter: int = 1000) -> Dict[str, Any]:
        """
        Solve Bellman equation using value iteration.

        V*(s) = max_a [R(s,a) + γ Σ P(s'|s,a) V*(s')]

        Args:
            states: Number of states
            actions: Number of actions
            rewards: R[s,a] reward matrix (states × actions)
            transitions: P[s,a,s'] transition probabilities (states × actions × states)
            discount: Discount factor γ
            tolerance: Convergence tolerance
            max_iter: Maximum iterations

        Returns:
            Dict with optimal value function and policy
        """
        self.bellman_solves += 1

        # Default: random MDP
        if rewards is None:
            rewards = np.random.randn(states, actions)

        if transitions is None:
            # Random transition probabilities
            transitions = np.random.rand(states, actions, states)
            # Normalize to probability distributions
            transitions = transitions / transitions.sum(axis=2, keepdims=True)

        # Value iteration
        V = np.zeros(states)
        policy = np.zeros(states, dtype=int)

        for iteration in range(max_iter):
            V_old = V.copy()

            # Update value function
            for s in range(states):
                # Compute Q(s, a) for all actions
                Q_values = []
                for a in range(actions):
                    q_sa = rewards[s, a] + discount * np.sum(transitions[s, a, :] * V_old)
                    Q_values.append(q_sa)

                # Bellman optimality: V(s) = max_a Q(s, a)
                V[s] = max(Q_values)
                policy[s] = int(np.argmax(Q_values))

            # Check convergence
            if np.max(np.abs(V - V_old)) < tolerance:
                break

        return {
            'value_function': V.tolist(),
            'optimal_policy': policy.tolist(),
            'converged': iteration < max_iter - 1,
            'iterations': iteration + 1,
            'states': states,
            'actions': actions,
            'discount': discount
        }

    def evaluate_sequential_policy(self, policy: List[int], data_sequence: List[Any],
                                   reward_function: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Evaluate performance of a sequential policy on data.

        Args:
            policy: Policy mapping (state/time) to actions
            data_sequence: Sequence of observations/states
            reward_function: Function computing reward for each (state, action) pair

        Returns:
            Dict with cumulative reward and performance metrics
        """
        if not data_sequence:
            return {'error': 'No data provided'}

        # Default reward: action equals observation
        if reward_function is None:
            reward_function = lambda s, a: 1.0 if s == a else 0.0

        cumulative_reward = 0.0
        rewards = []

        for t, state in enumerate(data_sequence):
            if t >= len(policy):
                action = policy[-1]  # Use last policy action
            else:
                action = policy[t]

            reward = reward_function(state, action)
            rewards.append(float(reward))
            cumulative_reward += reward

        return {
            'cumulative_reward': float(cumulative_reward),
            'average_reward': float(cumulative_reward / len(data_sequence)),
            'rewards': rewards,
            'policy_length': len(policy),
            'sequence_length': len(data_sequence)
        }

    def compute_value_of_information(self, prior: List[float],
                                    experiment_cost: float,
                                    likelihood_matrix: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Compute value of perfect information (VPI).

        VPI = E[V with info] - V without info - cost

        Args:
            prior: Prior distribution over states
            experiment_cost: Cost of conducting experiment
            likelihood_matrix: P(observation | state)

        Returns:
            Dict with value of information
        """
        prior = np.array(prior)
        n_states = len(prior)

        # Default: perfect information (identity likelihood)
        if likelihood_matrix is None:
            likelihood_matrix = np.eye(n_states)

        # Value without information: use prior
        # Assume utility is state index (for simplicity)
        value_without_info = np.sum(prior * np.arange(n_states))

        # Value with information: expected value after observing
        n_obs = likelihood_matrix.shape[1] if likelihood_matrix.ndim > 1 else n_states

        expected_value_with_info = 0.0
        for obs in range(n_obs):
            # Compute posterior given observation
            if likelihood_matrix.ndim == 1:
                likelihoods = likelihood_matrix
            else:
                likelihoods = likelihood_matrix[:, obs]

            # Bayes' theorem
            posterior = prior * likelihoods
            if posterior.sum() > 0:
                posterior = posterior / posterior.sum()
            else:
                posterior = prior

            # Value with this posterior
            value_with_obs = np.sum(posterior * np.arange(n_states))

            # Weight by probability of observation
            p_obs = np.sum(prior * likelihoods)
            expected_value_with_info += p_obs * value_with_obs

        vpi = expected_value_with_info - value_without_info - experiment_cost

        return {
            'value_of_information': float(vpi),
            'value_without_info': float(value_without_info),
            'value_with_info': float(expected_value_with_info),
            'experiment_cost': experiment_cost,
            'net_benefit': float(vpi)
        }

    def thompson_sampling_bandit(self, n_arms: int, n_rounds: int,
                                true_rewards: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Thompson sampling for multi-armed bandit problem.

        Bayesian approach: maintain posterior over each arm's reward,
        sample from posteriors, and choose arm with highest sample.

        Args:
            n_arms: Number of bandit arms
            n_rounds: Number of rounds to play
            true_rewards: True reward probabilities (for simulation)

        Returns:
            Dict with cumulative regret and arm selections
        """
        # Default: random true rewards
        if true_rewards is None:
            true_rewards = np.random.uniform(0.2, 0.8, n_arms)

        true_rewards = np.array(true_rewards)

        # Beta priors for each arm (initially uniform Beta(1,1))
        alpha = np.ones(n_arms)  # Successes + 1
        beta = np.ones(n_arms)   # Failures + 1

        arm_selections = []
        rewards_obtained = []
        cumulative_regret = 0.0
        regrets = []

        optimal_reward = np.max(true_rewards)

        for round_num in range(n_rounds):
            # Thompson sampling: sample from each arm's posterior
            samples = [np.random.beta(alpha[i], beta[i]) for i in range(n_arms)]

            # Choose arm with highest sample
            chosen_arm = int(np.argmax(samples))
            arm_selections.append(chosen_arm)

            # Simulate reward (Bernoulli trial)
            reward = 1 if np.random.random() < true_rewards[chosen_arm] else 0
            rewards_obtained.append(reward)

            # Update posterior
            if reward == 1:
                alpha[chosen_arm] += 1
            else:
                beta[chosen_arm] += 1

            # Compute regret
            regret = optimal_reward - true_rewards[chosen_arm]
            cumulative_regret += regret
            regrets.append(float(cumulative_regret))

        return {
            'cumulative_regret': float(cumulative_regret),
            'average_regret': float(cumulative_regret / n_rounds),
            'arm_selections': arm_selections,
            'total_reward': sum(rewards_obtained),
            'regrets': regrets,
            'posterior_means': [alpha[i] / (alpha[i] + beta[i]) for i in range(n_arms)],
            'true_rewards': true_rewards.tolist()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve agent statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'sprt_tests': self.sprt_tests,
            'stopping_problems': self.stopping_problems,
            'bellman_solves': self.bellman_solves
        })
        return stats
