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
BROWNIAN MOTION SPECIALIST (Tier 3)
=====================================

Handles Brownian motion / Wiener process computations.

Capabilities:
------------
- Brownian motion properties (variance, expectation, quadratic variation)
- First passage time distributions
- Path generation and simulation
- Reflection principle
- Scaled Brownian motion with drift

NO SYMPY - Pure native implementation using NumPy.
"""

import numpy as np
from typing import Dict, Any, List, Optional
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import (
    create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class BrownianMotionSpecialist(BDIAgent):
    """
    Brownian Motion Specialist - Tier 3

    CAPABILITIES:
    ------------
    - Compute E[W(t)], Var[W(t)], E[W(t)^2]
    - Generate Brownian motion paths
    - First passage time calculations
    - Reflection principle applications
    - Brownian motion with drift: dX_t = μ dt + σ dW_t

    NATIVE IMPLEMENTATION:
    ---------------------
    - Uses NumPy for numerical computations
    - NO SYMPY dependencies
    - Pure Python probability distributions
    """

    def __init__(
        self,
        agent_id: str = 'brownian_motion_specialist_001',
        df=None,
        blackboard=None
    ):
        """
        Initialize Brownian Motion Specialist

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared workspace for task coordination
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.paths_generated = 0
        self.properties_computed = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Brownian Motion Specialist initialized")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.stochastic.brownian',
            agent_id=self.agent_id,
            algorithm='brownian_motion',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            capabilities='wiener_process_first_passage_time_reflection_principle'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.stochastic.brownian")

    def process(self, task_entry):
        """
        Process Brownian motion task

        Args:
            task_entry: Task from blackboard

        Returns:
            Result entry
        """
        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'compute_properties')
            raw_input = metadata.get('raw_input', '')

            logger.info(f"[{self.agent_id}] Processing: {operation}")
            logger.info(f"  Input: {raw_input[:100]}")

            # Compute based on operation
            result = self._compute_brownian_operation(raw_input, operation, metadata)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, operation)

            self.tasks_succeeded += 1
            return result_entry

        except Exception as e:
            logger.error(f"[{self.agent_id}] Error: {e}")
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _compute_brownian_operation(self, raw_input: str, operation: str, metadata: Dict) -> Dict[str, Any]:
        """
        Compute Brownian motion properties

        Args:
            raw_input: Raw input string
            operation: Operation type
            metadata: Additional parameters

        Returns:
            Result dictionary
        """
        # Extract parameters from input
        t = metadata.get('t', 1.0)  # Time parameter
        mu = metadata.get('mu', 0.0)  # Drift
        sigma = metadata.get('sigma', 1.0)  # Volatility
        n_steps = metadata.get('n_steps', 1000)  # Path steps
        n_paths = metadata.get('n_paths', 1)  # Number of paths

        # Parse operation from input
        if 'e[w' in raw_input.lower() or 'expectation' in raw_input.lower():
            return self._compute_expectation(t, mu, sigma)
        elif 'var[w' in raw_input.lower() or 'variance' in raw_input.lower():
            return self._compute_variance(t, sigma)
        elif 'e[w^2' in raw_input.lower() or 'e[w(t)^2' in raw_input.lower():
            return self._compute_second_moment(t, mu, sigma)
        elif 'path' in raw_input.lower() or 'simulate' in raw_input.lower():
            return self._generate_path(t, mu, sigma, n_steps)
        elif 'first passage' in raw_input.lower():
            barrier = metadata.get('barrier', 1.0)
            return self._first_passage_time(barrier, mu, sigma, n_steps)
        else:
            # Default: compute all basic properties
            return self._compute_all_properties(t, mu, sigma)

    def _compute_expectation(self, t: float, mu: float, sigma: float) -> Dict[str, Any]:
        """
        Compute E[W(t)] for Brownian motion with drift.

        For standard Brownian motion (μ=0): E[W(t)] = 0 for all t ≥ 0.
        With drift μ: dX_t = μ dt + σ dW_t, then E[X(t)] = μt.

        Mathematical Foundation:
            Standard BM: E[W(t)] = E[W(0)] + E[∫₀ᵗ dW_s] = 0
            With drift: E[X(t)] = X(0) + E[∫₀ᵗ μ ds] + E[∫₀ᵗ σ dW_s] = μt

        Args:
            t (float): Time parameter, must be non-negative
            mu (float): Drift coefficient (expected rate of change)
            sigma (float): Volatility coefficient (not used for expectation)

        Returns:
            Dict[str, Any]: Result dictionary containing:
                - operation (str): 'expectation'
                - t (float): Time parameter
                - mu (float): Drift coefficient
                - sigma (float): Volatility coefficient
                - E[X(t)] (float): Computed expectation = μt
                - explanation (str): Human-readable result

        Example:
            >>> specialist = BrownianMotionSpecialist()
            >>> result = specialist._compute_expectation(t=2.0, mu=0.5, sigma=1.0)
            >>> result['E[X(t)]']
            1.0
        """
        self.properties_computed += 1

        expectation = mu * t

        return {
            'operation': 'expectation',
            't': t,
            'mu': mu,
            'sigma': sigma,
            'E[X(t)]': expectation,
            'explanation': f'E[X(t)] = μ·t = {mu}·{t} = {expectation}' if mu != 0
                          else f'E[W(t)] = 0 (standard Brownian motion)'
        }

    def _compute_variance(self, t: float, sigma: float) -> Dict[str, Any]:
        """
        Compute Var[W(t)] for Brownian motion.

        The variance of Brownian motion grows linearly with time: Var[W(t)] = σ²t.
        This is a fundamental property arising from independent increments.

        Mathematical Foundation:
            For Brownian motion with volatility σ:
            Var[X(t)] = E[(X(t) - E[X(t)])²] = E[X(t)²] - E[X(t)]² = σ²t

        Args:
            t (float): Time parameter, must be non-negative
            sigma (float): Volatility coefficient (diffusion rate)

        Returns:
            Dict[str, Any]: Result dictionary containing:
                - operation (str): 'variance'
                - t (float): Time parameter
                - sigma (float): Volatility coefficient
                - Var[X(t)] (float): Computed variance = σ²t
                - Std[X(t)] (float): Standard deviation = σ√t
                - explanation (str): Human-readable formula

        Example:
            >>> specialist = BrownianMotionSpecialist()
            >>> result = specialist._compute_variance(t=2.0, sigma=1.0)
            >>> result['Var[X(t)]']
            2.0

        Notes:
            - Standard deviation grows as √t, not linearly
            - Volatility σ scales both drift and diffusion
        """
        self.properties_computed += 1

        variance = sigma**2 * t
        std_dev = sigma * np.sqrt(t)

        return {
            'operation': 'variance',
            't': t,
            'sigma': sigma,
            'Var[X(t)]': variance,
            'Std[X(t)]': std_dev,
            'explanation': f'Var[X(t)] = σ²·t = {sigma}²·{t} = {variance}'
        }

    def _compute_second_moment(self, t: float, mu: float, sigma: float) -> Dict[str, Any]:
        """
        Compute E[W(t)²] for Brownian motion

        For standard Brownian: E[W(t)²] = t
        With drift: E[X(t)²] = Var[X(t)] + E[X(t)]² = σ²t + μ²t²

        Args:
            t: Time
            mu: Drift
            sigma: Volatility

        Returns:
            Result dict
        """
        self.properties_computed += 1

        variance = sigma**2 * t
        expectation = mu * t
        second_moment = variance + expectation**2

        return {
            'operation': 'second_moment',
            't': t,
            'mu': mu,
            'sigma': sigma,
            'E[X(t)^2]': second_moment,
            'E[X(t)]': expectation,
            'Var[X(t)]': variance,
            'explanation': f'E[X(t)²] = Var + E² = {variance} + {expectation}² = {second_moment}'
        }

    def _generate_path(self, T: float, mu: float, sigma: float, n_steps: int) -> Dict[str, Any]:
        """
        Generate a Brownian motion path using Euler discretization.

        Simulates the SDE: dX_t = μ dt + σ dW_t
        Discretization scheme: X(t+Δt) = X(t) + μΔt + σ√Δt·Z,  Z ~ N(0,1)

        Mathematical Foundation:
            The Wiener process increment dW_t ~ N(0, dt) is approximated by √Δt·Z
            where Z ~ N(0,1) is a standard normal random variable.

        Args:
            T (float): Final time, must be positive
            mu (float): Drift coefficient (expected rate of change)
            sigma (float): Volatility coefficient (diffusion rate)
            n_steps (int): Number of discrete time steps (higher = more accurate)

        Returns:
            Dict[str, Any]: Result dictionary containing:
                - operation (str): 'generate_path'
                - T (float): Final time
                - mu, sigma (float): Drift and volatility
                - n_steps (int): Number of steps
                - times (List[float]): Time grid [0, Δt, 2Δt, ..., T]
                - path (List[float]): Simulated path X(t)
                - final_value (float): X(T)
                - explanation (str): Description of parameters

        Example:
            >>> specialist = BrownianMotionSpecialist()
            >>> result = specialist._generate_path(T=1.0, mu=0.1, sigma=0.2, n_steps=100)
            >>> len(result['path'])
            101
            >>> result['times'][-1]
            1.0

        Notes:
            - Uses Euler-Maruyama scheme (order 0.5 strong convergence)
            - For more accurate simulations, increase n_steps
            - Complexity: O(n_steps)
        """
        self.paths_generated += 1

        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)
        dW = np.random.normal(0, np.sqrt(dt), n_steps)

        # Generate path: X(t+dt) = X(t) + mu*dt + sigma*dW
        increments = mu * dt + sigma * dW
        X = np.zeros(n_steps + 1)
        X[1:] = np.cumsum(increments)

        return {
            'operation': 'generate_path',
            'T': T,
            'mu': mu,
            'sigma': sigma,
            'n_steps': n_steps,
            'times': t.tolist(),
            'path': X.tolist(),
            'final_value': float(X[-1]),
            'explanation': f'Generated Brownian path with drift μ={mu}, σ={sigma} over [0,{T}]'
        }

    def _first_passage_time(self, barrier: float, mu: float, sigma: float, n_steps: int) -> Dict[str, Any]:
        """
        Estimate first passage time to barrier via simulation

        τ = inf{t ≥ 0 : X(t) ≥ barrier}

        Args:
            barrier: Level to hit
            mu: Drift
            sigma: Volatility
            n_steps: Number of simulations

        Returns:
            Result dict with FPT estimate
        """
        # Simulate many paths and record first passage times
        n_simulations = min(n_steps, 1000)
        T_max = 10.0  # Maximum time to simulate
        dt = 0.01

        passage_times = []

        for _ in range(n_simulations):
            X = 0.0
            t = 0.0

            while t < T_max:
                dW = np.random.normal(0, np.sqrt(dt))
                X += mu * dt + sigma * dW
                t += dt

                if X >= barrier:
                    passage_times.append(t)
                    break

        if passage_times:
            mean_fpt = np.mean(passage_times)
            std_fpt = np.std(passage_times)
            hit_rate = len(passage_times) / n_simulations
        else:
            mean_fpt = None
            std_fpt = None
            hit_rate = 0.0

        return {
            'operation': 'first_passage_time',
            'barrier': barrier,
            'mu': mu,
            'sigma': sigma,
            'mean_FPT': mean_fpt,
            'std_FPT': std_fpt,
            'hit_rate': hit_rate,
            'n_simulations': n_simulations,
            'explanation': f'Estimated first passage time to {barrier}: mean={mean_fpt}, hit rate={hit_rate}'
        }

    def _compute_all_properties(self, t: float, mu: float, sigma: float) -> Dict[str, Any]:
        """
        Compute all basic Brownian motion properties

        Args:
            t: Time
            mu: Drift
            sigma: Volatility

        Returns:
            Result dict with all properties
        """
        expectation = mu * t
        variance = sigma**2 * t
        second_moment = variance + expectation**2
        std_dev = sigma * np.sqrt(t)

        return {
            'operation': 'all_properties',
            't': t,
            'mu': mu,
            'sigma': sigma,
            'E[X(t)]': expectation,
            'Var[X(t)]': variance,
            'Std[X(t)]': std_dev,
            'E[X(t)^2]': second_moment,
            'explanation': 'Computed all Brownian motion properties'
        }

    def _create_result_entry(self, task_entry, result: Dict, operation: str):
        """Create successful result entry"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id,
            tags=['brownian', 'result', task_entry.conversation_id],
            status=EntryStatus.COMPLETED,
            metadata={
                'result': result,
                'operation': operation,
                'algorithm': 'brownian_motion'
            }
        )

        self.blackboard.post(result_entry)
        return result_entry

    def _create_error_entry(self, task_entry, error_msg: str):
        """Create error entry"""
        if not self.blackboard:
            return {'error': error_msg}

        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id,
            tags=['error'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    def update_beliefs(self):
        """PERCEIVE: Query Blackboard for Brownian motion tasks"""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(
                tags=['brownian'],
                status=EntryStatus.PENDING
            )

            for task in tasks:
                belief_key = f'pending_brownian_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create computation intentions"""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_brownian_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            steps = ['claim_task', 'parse_input', 'compute', 'verify', 'post']

            intention = Intention(
                plan_id=f'compute_{task_id}',
                steps=steps,
                target_desire='solve_brownian_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task
                }
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one computation step"""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        try:
            if action == 'claim_task':
                self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
                intention.advance()

            elif action == 'parse_input':
                # Input already parsed in process()
                intention.advance()

            elif action == 'compute':
                result = self.process(task)
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'verify':
                # Result verification (basic)
                result = intention.metadata.get('result')
                if result and 'error' not in result.metadata:
                    intention.advance()
                else:
                    intention.mark_failed()

            elif action == 'post':
                intention.mark_completed()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Execute step error: {e}")
            intention.mark_failed()

    def get_statistics(self) -> Dict[str, Any]:
        """Return specialist statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'paths_generated': self.paths_generated,
            'properties_computed': self.properties_computed,
            'algorithm': 'brownian_motion'
        })
        return stats


if __name__ == "__main__":
    # Quick test
    agent = BrownianMotionSpecialist()
    print(f"\nAgent initialized: {agent.agent_id}")
    print(f"Statistics: {agent.get_statistics()}")

    # Test computation
    result = agent._compute_second_moment(t=1.0, mu=0.0, sigma=1.0)
    print(f"\nTest result (E[W(1)²]): {result}")
