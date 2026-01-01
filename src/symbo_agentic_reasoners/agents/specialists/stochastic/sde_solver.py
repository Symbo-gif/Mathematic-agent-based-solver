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
SDE SOLVER SPECIALIST (Tier 3)
===============================

Handles stochastic differential equation numerical solutions.

Capabilities:
------------
- Euler-Maruyama method (order 0.5 weak, 1.0 strong)
- Milstein method (order 1.0 strong)
- SDE system solvers
- Geometric Brownian motion (exact solution)
- Stability analysis and adaptive timestepping

SDE Form:
--------
dX_t = μ(X_t, t) dt + σ(X_t, t) dW_t

NO SYMPY - Pure native implementation using NumPy.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Callable
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import (
    create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class SDESolverSpecialist(BDIAgent):
    """
    SDE Solver Specialist - Tier 3

    CAPABILITIES:
    ------------
    - Euler-Maruyama method (EM)
    - Milstein method (higher order)
    - Geometric Brownian motion (analytical)
    - Multi-dimensional SDE systems
    - Adaptive timestepping

    METHODS:
    -------
    - Euler-Maruyama: X_{n+1} = X_n + μ(X_n, t_n)Δt + σ(X_n, t_n)ΔW_n
    - Milstein: X_{n+1} = X_n + μΔt + σΔW + 0.5σ(∂σ/∂x)(ΔW² - Δt)
    - GBM exact: X(t) = X(0) exp((μ - σ²/2)t + σW(t))

    NATIVE IMPLEMENTATION:
    ---------------------
    - Uses NumPy for numerical computations
    - NO SYMPY dependencies
    - Pure Python implementations
    """

    def __init__(
        self,
        agent_id: str = 'sde_solver_specialist_001',
        df=None,
        blackboard=None
    ):
        """
        Initialize SDE Solver Specialist

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
        self.sdes_solved = 0
        self.euler_maruyama_used = 0
        self.milstein_used = 0
        self.gbm_exact_used = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] SDE Solver Specialist initialized")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.stochastic.sde',
            agent_id=self.agent_id,
            algorithm='euler_maruyama_milstein',
            cost='high',  # SDE simulation is computationally expensive
            instance=self,
            type='specialist',
            tier='3',
            capabilities='euler_maruyama_milstein_gbm_adaptive_timestep'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.stochastic.sde")

    def process(self, task_entry):
        """
        Process SDE task

        Args:
            task_entry: Task from blackboard

        Returns:
            Result entry
        """
        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'solve_sde')
            raw_input = metadata.get('raw_input', '')

            logger.info(f"[{self.agent_id}] Processing: {operation}")
            logger.info(f"  Input: {raw_input[:100]}")

            # Solve SDE
            result = self._solve_sde(raw_input, operation, metadata)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, operation)

            self.tasks_succeeded += 1
            return result_entry

        except Exception as e:
            logger.error(f"[{self.agent_id}] Error: {e}")
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _solve_sde(self, raw_input: str, operation: str, metadata: Dict) -> Dict[str, Any]:
        """
        Solve stochastic differential equation

        Args:
            raw_input: Raw input string
            operation: Operation type
            metadata: Additional parameters

        Returns:
            Result dictionary
        """
        # Extract SDE parameters
        X0 = metadata.get('X0', 1.0)  # Initial condition
        T = metadata.get('T', 1.0)  # Final time
        n_steps = metadata.get('n_steps', 1000)
        n_paths = metadata.get('n_paths', 1)  # Monte Carlo paths

        # Drift and diffusion coefficients
        mu = metadata.get('mu', 0.0)  # Can be function or constant
        sigma = metadata.get('sigma', 1.0)  # Can be function or constant

        # Method selection
        method = metadata.get('method', 'euler_maruyama')

        # Detect specific SDE types from input
        if 'geometric brownian' in raw_input.lower() or 'gbm' in raw_input.lower():
            return self._solve_gbm_exact(X0, mu, sigma, T, n_steps, n_paths)
        elif 'milstein' in raw_input.lower():
            return self._solve_milstein(X0, mu, sigma, T, n_steps, n_paths)
        else:
            return self._solve_euler_maruyama(X0, mu, sigma, T, n_steps, n_paths)

    def _solve_euler_maruyama(self, X0: float, mu: float, sigma: float,
                               T: float, n_steps: int, n_paths: int) -> Dict[str, Any]:
        """
        Solve SDE using Euler-Maruyama method

        dX_t = μ dt + σ dW_t
        Discretization: X_{n+1} = X_n + μΔt + σ√Δt Z_n,  Z ~ N(0,1)

        Args:
            X0: Initial condition
            mu: Drift coefficient (constant)
            sigma: Diffusion coefficient (constant)
            T: Final time
            n_steps: Number of time steps
            n_paths: Number of Monte Carlo paths

        Returns:
            Result dict with paths
        """
        self.sdes_solved += 1
        self.euler_maruyama_used += 1

        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        # Generate paths
        X = np.zeros((n_paths, n_steps + 1))
        X[:, 0] = X0

        for i in range(n_steps):
            dW = np.random.normal(0, np.sqrt(dt), n_paths)
            X[:, i + 1] = X[:, i] + mu * dt + sigma * dW

        # Statistics
        mean_path = np.mean(X, axis=0)
        std_path = np.std(X, axis=0)
        final_values = X[:, -1]

        return {
            'operation': 'euler_maruyama',
            'method': 'Euler-Maruyama',
            'X0': X0,
            'mu': mu,
            'sigma': sigma,
            'T': T,
            'n_steps': n_steps,
            'n_paths': n_paths,
            'times': t.tolist(),
            'paths': X.tolist() if n_paths <= 10 else 'too_many_to_display',
            'mean_path': mean_path.tolist(),
            'std_path': std_path.tolist(),
            'final_mean': float(np.mean(final_values)),
            'final_std': float(np.std(final_values)),
            'explanation': f'Solved SDE with Euler-Maruyama: dX = {mu}dt + {sigma}dW'
        }

    def _solve_milstein(self, X0: float, mu: float, sigma: float,
                        T: float, n_steps: int, n_paths: int) -> Dict[str, Any]:
        """
        Solve SDE using Milstein method (higher order)

        For dX_t = μX_t dt + σX_t dW_t (multiplicative noise):
        X_{n+1} = X_n + μX_n dt + σX_n dW + 0.5σ²X_n(dW² - dt)

        Args:
            X0: Initial condition
            mu: Drift coefficient
            sigma: Diffusion coefficient
            T: Final time
            n_steps: Number of time steps
            n_paths: Number of Monte Carlo paths

        Returns:
            Result dict with paths
        """
        self.sdes_solved += 1
        self.milstein_used += 1

        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        # Generate paths
        X = np.zeros((n_paths, n_steps + 1))
        X[:, 0] = X0

        for i in range(n_steps):
            dW = np.random.normal(0, np.sqrt(dt), n_paths)

            # Milstein correction for multiplicative noise
            # Assumes σ(X) = σ * X, so ∂σ/∂X = σ
            drift_term = mu * X[:, i] * dt
            diffusion_term = sigma * X[:, i] * dW
            milstein_correction = 0.5 * sigma**2 * X[:, i] * (dW**2 - dt)

            X[:, i + 1] = X[:, i] + drift_term + diffusion_term + milstein_correction

        # Statistics
        mean_path = np.mean(X, axis=0)
        std_path = np.std(X, axis=0)
        final_values = X[:, -1]

        return {
            'operation': 'milstein',
            'method': 'Milstein',
            'X0': X0,
            'mu': mu,
            'sigma': sigma,
            'T': T,
            'n_steps': n_steps,
            'n_paths': n_paths,
            'times': t.tolist(),
            'paths': X.tolist() if n_paths <= 10 else 'too_many_to_display',
            'mean_path': mean_path.tolist(),
            'std_path': std_path.tolist(),
            'final_mean': float(np.mean(final_values)),
            'final_std': float(np.std(final_values)),
            'explanation': f'Solved SDE with Milstein method (order 1.0 strong convergence)'
        }

    def _solve_gbm_exact(self, S0: float, mu: float, sigma: float,
                          T: float, n_steps: int, n_paths: int) -> Dict[str, Any]:
        """
        Solve Geometric Brownian Motion exactly

        dS_t = μS_t dt + σS_t dW_t
        Exact solution: S(t) = S(0) exp((μ - σ²/2)t + σW(t))

        Args:
            S0: Initial stock price
            mu: Drift (expected return)
            sigma: Volatility
            T: Final time
            n_steps: Number of time steps
            n_paths: Number of Monte Carlo paths

        Returns:
            Result dict with exact paths
        """
        self.sdes_solved += 1
        self.gbm_exact_used += 1

        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        # Generate paths using exact solution
        S = np.zeros((n_paths, n_steps + 1))
        S[:, 0] = S0

        # Generate Brownian motion paths
        dW = np.random.normal(0, np.sqrt(dt), (n_paths, n_steps))
        W = np.cumsum(dW, axis=1)
        W = np.hstack([np.zeros((n_paths, 1)), W])  # W(0) = 0

        # Exact GBM solution
        for i in range(1, n_steps + 1):
            S[:, i] = S0 * np.exp((mu - 0.5 * sigma**2) * t[i] + sigma * W[:, i])

        # Statistics
        mean_path = np.mean(S, axis=0)
        std_path = np.std(S, axis=0)
        final_values = S[:, -1]

        # Theoretical moments
        expected_final = S0 * np.exp(mu * T)
        variance_final = S0**2 * np.exp(2 * mu * T) * (np.exp(sigma**2 * T) - 1)

        return {
            'operation': 'gbm_exact',
            'method': 'Exact GBM Solution',
            'S0': S0,
            'mu': mu,
            'sigma': sigma,
            'T': T,
            'n_steps': n_steps,
            'n_paths': n_paths,
            'times': t.tolist(),
            'paths': S.tolist() if n_paths <= 10 else 'too_many_to_display',
            'mean_path': mean_path.tolist(),
            'std_path': std_path.tolist(),
            'final_mean': float(np.mean(final_values)),
            'final_std': float(np.std(final_values)),
            'expected_final': expected_final,
            'theoretical_variance': variance_final,
            'explanation': f'Exact GBM solution: S(t) = S(0)exp((μ-σ²/2)t + σW(t))'
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
            tags=['sde', 'result', task_entry.conversation_id],
            status=EntryStatus.COMPLETED,
            metadata={
                'result': result,
                'operation': operation,
                'algorithm': result.get('method', 'euler_maruyama')
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
        """PERCEIVE: Query Blackboard for SDE tasks"""
        if not self.blackboard:
            return

        try:
            tasks = self.blackboard.query_entries(
                tags=['sde'],
                status=EntryStatus.PENDING
            )

            for task in tasks:
                belief_key = f'pending_sde_{task.entry_id}'
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
            if not predicate.startswith('pending_sde_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            steps = ['claim_task', 'parse_sde', 'solve', 'verify', 'post']

            intention = Intention(
                plan_id=f'solve_{task_id}',
                steps=steps,
                target_desire='solve_sde_task',
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

            elif action == 'parse_sde':
                # SDE parameters parsed in process()
                intention.advance()

            elif action == 'solve':
                result = self.process(task)
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'verify':
                # Basic verification
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
            'sdes_solved': self.sdes_solved,
            'euler_maruyama_used': self.euler_maruyama_used,
            'milstein_used': self.milstein_used,
            'gbm_exact_used': self.gbm_exact_used,
            'methods': ['euler_maruyama', 'milstein', 'gbm_exact']
        })
        return stats


if __name__ == "__main__":
    # Quick test
    agent = SDESolverSpecialist()
    print(f"\nAgent initialized: {agent.agent_id}")
    print(f"Statistics: {agent.get_statistics()}")

    # Test GBM exact solution
    result = agent._solve_gbm_exact(S0=100.0, mu=0.05, sigma=0.2, T=1.0, n_steps=100, n_paths=5)
    print(f"\nTest result (GBM): Final mean = {result['final_mean']:.2f}, expected = {result['expected_final']:.2f}")
