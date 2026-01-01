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
UTILITY THEORY SPECIALIST (Tier 3)
==================================

Implements utility functions, expected utility theory, and risk preference modeling.
Handles von Neumann-Morgenstern axioms, certainty equivalents, and risk aversion measures.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from scipy.optimize import minimize_scalar, fsolve


class UtilityTheorySpecialist(BDIAgent):
    """
    Specialist for utility theory and expected utility calculations.

    Capabilities:
    - Construct utility functions from preferences
    - Compute expected utility
    - Calculate certainty equivalents
    - Measure risk aversion (Arrow-Pratt coefficients)
    - Verify von Neumann-Morgenstern axioms
    - Evaluate utility of wealth functions
    """

    def __init__(self, agent_id='utility_theory_specialist_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        self.utility_computations = 0
        self.risk_assessments = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.statistics.bayesian_decision.utility_theory',
                agent_id=self.agent_id,
                algorithm='expected_utility',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3',
                methods='expected_utility_certainty_equivalent_risk_aversion_vnm_axioms'
            ))

        print(f"[{self.agent_id}] Utility Theory Specialist initialized")
        print(f"  Methods: Expected utility, risk aversion, von Neumann-Morgenstern axioms")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for utility theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = (self.blackboard.query_entries(tags=['utility'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['expected_utility'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['risk_aversion'], status=EntryStatus.PENDING))

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
        """DELIBERATE: Create utility computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'expected_utility')

            steps = ['claim_task', 'parse_parameters', 'compute_utility', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'utility_{operation}_{task_id}',
                steps=steps,
                target_desire='utility_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        # Periodic belief update about utility function database
        if self.tasks_executed > 0 and self.tasks_executed % 30 == 0:
            intent = Intention(
                plan_id=f'update_utility_priors_{self.tasks_executed}',
                steps=['update_utility_database'],
                target_desire='maintain_knowledge',
                metadata={'trigger': 'periodic'}
            )
            new_intentions.append(intent)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform utility theory computations."""
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
                operation = metadata.get('operation', 'expected_utility')

                # Extract parameters based on operation
                params = {}
                if operation == 'expected_utility':
                    params['utilities'] = metadata.get('utilities', [0.0, 1.0])
                    params['probabilities'] = metadata.get('probabilities', [0.5, 0.5])
                elif operation == 'certainty_equivalent':
                    params['lottery'] = metadata.get('lottery', {'outcomes': [0, 100], 'probabilities': [0.5, 0.5]})
                    params['utility_type'] = metadata.get('utility_type', 'log')
                elif operation == 'risk_aversion':
                    params['utility_type'] = metadata.get('utility_type', 'log')
                    params['wealth'] = metadata.get('wealth', 50.0)
                elif operation == 'vnm_axioms':
                    params['preferences'] = metadata.get('preferences', [])

                intention.metadata['params'] = params
                intention.advance()

            elif action == 'compute_utility':
                operation = intention.metadata.get('operation')
                params = intention.metadata.get('params', {})

                result = None
                if operation == 'expected_utility':
                    result = self.compute_expected_utility(
                        params.get('utilities', []),
                        params.get('probabilities', [])
                    )
                elif operation == 'certainty_equivalent':
                    result = self.compute_certainty_equivalent(
                        params.get('lottery', {}),
                        params.get('utility_type', 'log')
                    )
                elif operation == 'risk_aversion':
                    result = self.measure_risk_aversion(
                        params.get('utility_type', 'log'),
                        params.get('wealth', 50.0)
                    )
                elif operation == 'vnm_axioms':
                    result = self.verify_von_neumann_morgenstern_axioms(
                        params.get('preferences', [])
                    )
                else:
                    # Default: compute expected utility
                    result = self.compute_expected_utility([0.0, 1.0], [0.5, 0.5])

                intention.metadata['result'] = result
                self.utility_computations += 1
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
                        ['utility', 'result', task_id],
                        EntryStatus.COMPLETED,
                        {'result': result, 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            elif action == 'update_utility_database':
                # Update belief about utility function patterns
                self.add_belief(
                    'utility_patterns_updated',
                    {'timestamp': self.tasks_executed, 'computations': self.utility_computations},
                    confidence=0.9,
                    source='self_monitoring'
                )
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[{self.agent_id}] Step {action} failed: {e}")
            # Mark as failed and complete intention
            while not intention.is_complete():
                intention.advance()

    def process(self, task_entry):
        """
        Process a utility theory task (legacy interface for supervisor compatibility).

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

        operation = metadata.get('operation', 'expected_utility')

        try:
            if operation == 'expected_utility':
                utilities = metadata.get('utilities', [0.0, 1.0])
                probabilities = metadata.get('probabilities', [0.5, 0.5])
                return self.compute_expected_utility(utilities, probabilities)
            elif operation == 'certainty_equivalent':
                lottery = metadata.get('lottery', {'outcomes': [0, 100], 'probabilities': [0.5, 0.5]})
                utility_type = metadata.get('utility_type', 'log')
                return self.compute_certainty_equivalent(lottery, utility_type)
            elif operation == 'risk_aversion':
                utility_type = metadata.get('utility_type', 'log')
                wealth = metadata.get('wealth', 50.0)
                return self.measure_risk_aversion(utility_type, wealth)
            else:
                return {'operation': operation, 'explanation': 'Utility theory computation'}
        except Exception as e:
            return {'error': str(e), 'operation': operation}

    # ==================== CORE COMPUTATIONAL METHODS ====================

    def compute_expected_utility(self, utilities: List[float], probabilities: List[float]) -> Dict[str, Any]:
        """
        Compute expected utility: EU = Σ p(s) × u(s)

        Args:
            utilities: List of utility values for each outcome
            probabilities: List of probabilities for each outcome

        Returns:
            Dict with expected utility value and breakdown

        Example:
            >>> result = agent.compute_expected_utility([0, 100], [0.3, 0.7])
            >>> result['expected_utility']  # 70.0
        """
        utilities = np.array(utilities)
        probabilities = np.array(probabilities)

        # Validate probabilities
        if not np.allclose(probabilities.sum(), 1.0, atol=1e-6):
            return {
                'error': 'Probabilities must sum to 1',
                'sum': float(probabilities.sum())
            }

        if np.any(probabilities < 0):
            return {'error': 'Probabilities must be non-negative'}

        if len(utilities) != len(probabilities):
            return {'error': 'Utilities and probabilities must have same length'}

        # Compute expected utility
        expected_utility = np.sum(probabilities * utilities)

        return {
            'expected_utility': float(expected_utility),
            'utilities': utilities.tolist(),
            'probabilities': probabilities.tolist(),
            'breakdown': [(float(p), float(u), float(p * u))
                         for p, u in zip(probabilities, utilities)]
        }

    def compute_utility_of_wealth(self, wealth: float, function_type: str = 'log',
                                   params: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Compute utility of wealth U(w) for various utility function types.

        Supported types:
        - 'log': U(w) = ln(w) [log utility]
        - 'sqrt': U(w) = √w [square root utility]
        - 'power': U(w) = w^γ / γ [power utility with CRRA γ]
        - 'exponential': U(w) = -exp(-αw) [exponential utility with risk aversion α]
        - 'quadratic': U(w) = w - βw² [quadratic utility]

        Args:
            wealth: Wealth level
            function_type: Type of utility function
            params: Parameters for utility function (e.g., {'gamma': 0.5} for power)

        Returns:
            Dict with utility value and function details
        """
        if wealth <= 0 and function_type in ['log', 'sqrt', 'power']:
            return {'error': f'{function_type} utility requires positive wealth', 'wealth': wealth}

        params = params or {}

        if function_type == 'log':
            utility = np.log(wealth)
            description = 'U(w) = ln(w)'

        elif function_type == 'sqrt':
            utility = np.sqrt(wealth)
            description = 'U(w) = √w'

        elif function_type == 'power':
            gamma = params.get('gamma', 0.5)
            if gamma == 1.0:
                utility = np.log(wealth)
                description = f'U(w) = ln(w) [γ=1 limit]'
            else:
                utility = (wealth ** gamma) / gamma
                description = f'U(w) = w^{gamma} / {gamma} [CRRA]'

        elif function_type == 'exponential':
            alpha = params.get('alpha', 0.01)
            utility = -np.exp(-alpha * wealth)
            description = f'U(w) = -exp(-{alpha}w) [CARA]'

        elif function_type == 'quadratic':
            beta = params.get('beta', 0.01)
            utility = wealth - beta * (wealth ** 2)
            description = f'U(w) = w - {beta}w²'

        else:
            return {'error': f'Unknown utility function type: {function_type}'}

        return {
            'utility': float(utility),
            'wealth': wealth,
            'function_type': function_type,
            'description': description,
            'parameters': params
        }

    def compute_certainty_equivalent(self, lottery: Dict[str, Any],
                                    utility_type: str = 'log') -> Dict[str, Any]:
        """
        Compute certainty equivalent CE: the certain amount with same utility as lottery.

        For utility function U, CE satisfies: U(CE) = E[U(X)]

        Args:
            lottery: Dict with 'outcomes' and 'probabilities'
            utility_type: Type of utility function ('log', 'sqrt', 'power', 'exponential')

        Returns:
            Dict with certainty equivalent value

        Example:
            >>> lottery = {'outcomes': [0, 100], 'probabilities': [0.5, 0.5]}
            >>> result = agent.compute_certainty_equivalent(lottery, 'log')
        """
        outcomes = np.array(lottery.get('outcomes', []))
        probabilities = np.array(lottery.get('probabilities', []))

        # Validate
        if len(outcomes) != len(probabilities):
            return {'error': 'Outcomes and probabilities must have same length'}

        if not np.allclose(probabilities.sum(), 1.0, atol=1e-6):
            return {'error': 'Probabilities must sum to 1'}

        # Handle edge cases for log/sqrt/power utilities with zero outcomes
        if utility_type in ['log', 'sqrt', 'power'] and np.any(outcomes <= 0):
            # For outcomes with probability at zero, use linear utility instead
            return {
                'error': f'{utility_type} utility requires positive outcomes',
                'suggestion': 'Use linear or exponential utility for non-positive outcomes'
            }

        # Compute expected utility of lottery
        utilities = []
        for outcome in outcomes:
            u_result = self.compute_utility_of_wealth(outcome, utility_type)
            if 'error' in u_result:
                return u_result
            utilities.append(u_result['utility'])

        expected_utility = np.sum(probabilities * np.array(utilities))

        # Find CE by inverting utility function
        if utility_type == 'log':
            ce = np.exp(expected_utility)
        elif utility_type == 'sqrt':
            ce = expected_utility ** 2
        elif utility_type == 'power':
            gamma = lottery.get('gamma', 0.5)
            if gamma == 1.0:
                ce = np.exp(expected_utility)
            else:
                ce = (gamma * expected_utility) ** (1.0 / gamma)
        elif utility_type == 'exponential':
            alpha = lottery.get('alpha', 0.01)
            ce = -np.log(-expected_utility) / alpha
        else:
            # Use numerical solver
            def equation(ce):
                """Equation to solve: u(ce) - E[u(X)] = 0."""
                u = self.compute_utility_of_wealth(ce, utility_type)
                return u.get('utility', 0) - expected_utility

            ce = fsolve(equation, np.mean(outcomes))[0]

        # Compute expected monetary value for comparison
        expected_value = np.sum(probabilities * outcomes)
        risk_premium = expected_value - ce

        return {
            'certainty_equivalent': float(ce),
            'expected_utility': float(expected_utility),
            'expected_value': float(expected_value),
            'risk_premium': float(risk_premium),
            'utility_type': utility_type,
            'lottery': lottery
        }

    def measure_risk_aversion(self, utility_type: str = 'log',
                             wealth: float = 50.0) -> Dict[str, Any]:
        """
        Measure risk aversion using Arrow-Pratt coefficient.

        Absolute risk aversion: A(w) = -U''(w) / U'(w)
        Relative risk aversion: R(w) = -w * U''(w) / U'(w)

        Args:
            utility_type: Type of utility function
            wealth: Wealth level at which to measure

        Returns:
            Dict with risk aversion measures
        """
        self.risk_assessments += 1

        if wealth <= 0 and utility_type in ['log', 'sqrt', 'power']:
            return {'error': 'Wealth must be positive for this utility type'}

        # Compute derivatives numerically
        h = 0.001 * wealth if wealth > 0 else 0.001

        u_w = self.compute_utility_of_wealth(wealth, utility_type)
        u_plus = self.compute_utility_of_wealth(wealth + h, utility_type)
        u_minus = self.compute_utility_of_wealth(wealth - h, utility_type)

        if any('error' in x for x in [u_w, u_plus, u_minus]):
            return {'error': 'Unable to compute utility derivatives'}

        # First derivative (marginal utility)
        u_prime = (u_plus['utility'] - u_minus['utility']) / (2 * h)

        # Second derivative
        u_double_prime = (u_plus['utility'] - 2 * u_w['utility'] + u_minus['utility']) / (h ** 2)

        # Arrow-Pratt measures
        if abs(u_prime) < 1e-10:
            return {'error': 'Zero marginal utility'}

        absolute_risk_aversion = -u_double_prime / u_prime
        relative_risk_aversion = -wealth * u_double_prime / u_prime if wealth != 0 else 0

        # Interpret risk attitude
        if absolute_risk_aversion > 0.001:
            attitude = 'risk_averse'
        elif absolute_risk_aversion < -0.001:
            attitude = 'risk_seeking'
        else:
            attitude = 'risk_neutral'

        return {
            'absolute_risk_aversion': float(absolute_risk_aversion),
            'relative_risk_aversion': float(relative_risk_aversion),
            'risk_attitude': attitude,
            'wealth': wealth,
            'utility_type': utility_type,
            'marginal_utility': float(u_prime)
        }

    def verify_von_neumann_morgenstern_axioms(self, preferences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify von Neumann-Morgenstern axioms for preference relation.

        VNM Axioms:
        1. Completeness: For any lotteries L1, L2, either L1 ≽ L2 or L2 ≽ L1
        2. Transitivity: If L1 ≽ L2 and L2 ≽ L3, then L1 ≽ L3
        3. Continuity: If L1 ≻ L2 ≻ L3, then ∃ α: L2 ~ αL1 + (1-α)L3
        4. Independence: If L1 ≻ L2, then αL1 + (1-α)L3 ≻ αL2 + (1-α)L3

        Args:
            preferences: List of preference statements, each with 'preferred', 'over'

        Returns:
            Dict with axiom verification results
        """
        violations = []

        # Extract preference relation
        pref_graph = {}  # lottery_id -> set of dominated lotteries
        for pref in preferences:
            l1 = pref.get('preferred')
            l2 = pref.get('over')
            if l1 not in pref_graph:
                pref_graph[l1] = set()
            pref_graph[l1].add(l2)

        # Check transitivity
        transitivity_holds = True
        for l1 in pref_graph:
            for l2 in pref_graph.get(l1, []):
                for l3 in pref_graph.get(l2, []):
                    if l3 not in pref_graph.get(l1, []):
                        transitivity_holds = False
                        violations.append({
                            'axiom': 'transitivity',
                            'issue': f'{l1} ≻ {l2} and {l2} ≻ {l3}, but not {l1} ≻ {l3}'
                        })

        # Check completeness (all pairs must be comparable)
        all_lotteries = set(pref_graph.keys())
        for pref in preferences:
            all_lotteries.add(pref.get('over'))

        completeness_holds = True
        for l1 in all_lotteries:
            for l2 in all_lotteries:
                if l1 != l2:
                    comparable = (l2 in pref_graph.get(l1, []) or
                                l1 in pref_graph.get(l2, []))
                    if not comparable:
                        completeness_holds = False
                        violations.append({
                            'axiom': 'completeness',
                            'issue': f'Lotteries {l1} and {l2} not comparable'
                        })

        # Note: Continuity and Independence require actual lottery specifications
        # which are not provided in simple preference lists

        all_axioms_hold = transitivity_holds and completeness_holds

        return {
            'vnm_axioms_satisfied': all_axioms_hold,
            'transitivity': transitivity_holds,
            'completeness': completeness_holds,
            'continuity': 'not_tested',
            'independence': 'not_tested',
            'violations': violations,
            'preference_count': len(preferences)
        }

    def construct_utility_function(self, preferences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construct utility function from preference data.

        Uses least squares fitting to find utility function that best represents preferences.

        Args:
            preferences: List of preference statements with outcomes

        Returns:
            Dict with utility function parameters
        """
        # Extract outcome-preference pairs
        outcomes = []
        preference_scores = []

        for i, pref in enumerate(preferences):
            if 'outcome' in pref and 'rank' in pref:
                outcomes.append(pref['outcome'])
                preference_scores.append(pref['rank'])

        if len(outcomes) < 2:
            return {'error': 'Insufficient data to construct utility function'}

        outcomes = np.array(outcomes)
        preference_scores = np.array(preference_scores)

        # Try fitting log utility
        if np.all(outcomes > 0):
            log_outcomes = np.log(outcomes)
            # Linear regression: rank = a + b * log(outcome)
            A = np.vstack([np.ones(len(log_outcomes)), log_outcomes]).T
            coeffs, residuals, _, _ = np.linalg.lstsq(A, preference_scores, rcond=None)

            return {
                'utility_type': 'log',
                'formula': f'U(w) = {coeffs[0]:.3f} + {coeffs[1]:.3f} * ln(w)',
                'coefficients': {'intercept': float(coeffs[0]), 'slope': float(coeffs[1])},
                'residual_sum_squares': float(residuals[0]) if len(residuals) > 0 else 0.0,
                'data_points': len(outcomes)
            }
        else:
            # Linear utility
            A = np.vstack([np.ones(len(outcomes)), outcomes]).T
            coeffs, residuals, _, _ = np.linalg.lstsq(A, preference_scores, rcond=None)

            return {
                'utility_type': 'linear',
                'formula': f'U(w) = {coeffs[0]:.3f} + {coeffs[1]:.3f} * w',
                'coefficients': {'intercept': float(coeffs[0]), 'slope': float(coeffs[1])},
                'residual_sum_squares': float(residuals[0]) if len(residuals) > 0 else 0.0,
                'data_points': len(outcomes)
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve agent statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'utility_computations': self.utility_computations,
            'risk_assessments': self.risk_assessments
        })
        return stats
