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
OPTIMAL CONTROL SPECIALIST (Tier 3)
====================================

Native Python implementation for optimal control theory.
Solves control problems using Pontryagin Maximum Principle, HJB equation,
and LQR/LQG methods.

NO SYMPY - Pure NumPy/SciPy implementation.

CAPABILITIES:
-------------
- Pontryagin Maximum Principle (necessary conditions)
- Hamilton-Jacobi-Bellman equation (value iteration)
- Linear Quadratic Regulator (LQR) - Riccati equation
- Linear Quadratic Gaussian (LQG) - optimal control with noise
- Bang-bang control (time-optimal control)
- Time-optimal control problems
- Reachability analysis (reachable sets)
- Controllability verification
- Value function computation (dynamic programming)

THEORY:
-------
Control System: dx/dt = f(x, u, t)
Cost Functional: J = ∫ L(x, u, t) dt + φ(x(T))
Optimal Control: u*(t) minimizes J

PMP: Hamiltonian H = L + λ^T f, with ∂H/∂u = 0 and λ' = -∂H/∂x
HJB: -∂V/∂t = min_u [L(x, u) + (∂V/∂x)^T f(x, u)]
LQR: Minimize ∫ (x^T Q x + u^T R u) dt, closed-form via Riccati

EXAMPLES:
---------
- Double integrator: minimize time to reach target (bang-bang)
- Inverted pendulum: stabilize with minimum energy (LQR)
- Rocket landing: minimize fuel consumption
- Portfolio optimization: maximize expected utility
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple
from scipy.integrate import solve_ivp, odeint
from scipy.optimize import minimize, linprog
from scipy.linalg import solve_continuous_are, solve_discrete_are

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

logger = logging.getLogger('symbo_agentic_reasoners.specialists.optimal_control')


class OptimalControlSpecialist(BDIAgent):
    """
    BDI Agent for optimal control problems.

    Applies Pontryagin Maximum Principle, HJB equation, and LQR/LQG methods
    to find optimal control policies.

    DIRECTIVE:
    ----------
    Find control u(t) that minimizes cost functional J subject to
    system dynamics dx/dt = f(x, u, t) and constraints.

    OPERATIONS:
    -----------
    - apply_pontryagin_maximum_principle: PMP necessary conditions
    - solve_hamilton_jacobi_bellman: HJB equation (value iteration)
    - solve_lqr_problem: Linear Quadratic Regulator
    - solve_lqg_problem: LQG with Gaussian noise
    - compute_bang_bang_control: Bang-bang control for time-optimal
    - solve_time_optimal_control: Minimum time control
    - compute_reachable_set: Forward reachability analysis
    - verify_controllability: Controllability matrix rank test
    - compute_value_function: Dynamic programming value function
    """

    def __init__(self, agent_id='optimal_control_specialist_001', df=None, blackboard=None):
        """Initialize Optimal Control Specialist."""
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.control_cache = {}

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.optimization.advanced.optimal_control',
                agent_id=self.agent_id,
                algorithm='optimal_control',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3',
                capabilities='pmp_hjb_lqr_lqg_bang_bang_reachability'
            ))

        logger.info(f"[{self.agent_id}] Optimal Control Specialist initialized")

    def process(self, task_entry):
        """Process optimal control task."""
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'lqr')

            if operation == 'lqr':
                result = self.solve_lqr_problem(
                    metadata.get('A'), metadata.get('B'),
                    metadata.get('Q'), metadata.get('R')
                )
            elif operation == 'pmp':
                result = self.apply_pontryagin_maximum_principle(
                    metadata.get('dynamics'),
                    metadata.get('cost'),
                    metadata.get('constraints')
                )
            elif operation == 'hjb':
                result = self.solve_hamilton_jacobi_bellman(
                    metadata.get('dynamics'),
                    metadata.get('cost'),
                    metadata.get('boundary')
                )
            elif operation == 'bang_bang':
                result = self.compute_bang_bang_control(
                    metadata.get('dynamics'),
                    metadata.get('constraints')
                )
            elif operation == 'controllability':
                result = self.verify_controllability(
                    metadata.get('A'),
                    metadata.get('B')
                )
            else:
                result = {'error': f'Unknown operation: {operation}'}

            if 'error' not in result:
                self.tasks_succeeded += 1
            else:
                self.tasks_failed += 1

            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] Task failed: {e}")
            return {'error': str(e)}

    # ========== PONTRYAGIN MAXIMUM PRINCIPLE ==========

    def apply_pontryagin_maximum_principle(
        self,
        dynamics: Callable[[np.ndarray, np.ndarray, float], np.ndarray],
        cost: Callable[[np.ndarray, np.ndarray, float], float],
        constraints: Dict[str, Any],
        t_span: Tuple[float, float] = (0, 10),
        n_iterations: int = 50
    ) -> Dict[str, Any]:
        """
        Apply Pontryagin Maximum Principle for optimal control.

        Necessary conditions:
        1. State equation: dx/dt = ∂H/∂λ = f(x, u, t)
        2. Costate equation: dλ/dt = -∂H/∂x
        3. Optimality: ∂H/∂u = 0 (or H minimized over u)
        4. Transversality: λ(T) = ∂φ/∂x|_{x(T)}

        where H = L(x, u, t) + λ^T f(x, u, t) is the Hamiltonian.

        Args:
            dynamics: f(x, u, t) - system dynamics
            cost: L(x, u, t) - running cost
            constraints: Initial/terminal conditions, control bounds
            t_span: Time interval [t_0, t_f]
            n_iterations: Iterations for costate convergence

        Returns:
            Dictionary with optimal trajectory and control
        """
        logger.info("Applying Pontryagin Maximum Principle")

        x0 = np.array(constraints.get('x0', [0.0, 0.0]))
        xf = constraints.get('xf', None)
        u_min = constraints.get('u_min', -10.0)
        u_max = constraints.get('u_max', 10.0)

        n_states = len(x0)
        t0, tf = t_span

        # Hamiltonian H = L + λ^T f
        def hamiltonian(x, u, lam, t):
            """Compute Hamiltonian."""
            return cost(x, u, t) + lam @ dynamics(x, u, t)

        # Optimal control from ∂H/∂u = 0 (unconstrained) or projection
        def optimal_control(x, lam, t):
            """
            Find u that minimizes H.
            For linear-quadratic: u* = -R^{-1} B^T λ
            For general: numerical minimization or projection
            """
            # Simple case: minimize over interval
            def H_u(u_val):
                """Hamiltonian as function of control u for minimization."""
                u_vec = np.array([u_val]) if np.isscalar(u_val) else u_val
                return hamiltonian(x, u_vec, lam, t)

            # Bounded minimization
            result = minimize(
                H_u,
                x0=np.zeros(1),
                method='L-BFGS-B',
                bounds=[(u_min, u_max)]
            )
            return result.x[0] if result.success else 0.0

        # Two-point boundary value problem (TPBVP)
        # Forward: x' = f(x, u*, t) with x(t0) = x0
        # Backward: λ' = -∂H/∂x with λ(tf) = terminal condition

        # Shooting method: guess λ(t0) and iterate
        lambda_guess = np.zeros(n_states)

        def shooting_error(lam0):
            """
            Solve forward with guessed costate, check terminal condition.
            """
            def ode_system(t, z):
                """
                Augmented system [x, λ].
                z = [x1, x2, ..., λ1, λ2, ...]
                """
                x = z[:n_states]
                lam = z[n_states:]

                # Optimal control at current state
                u_opt = optimal_control(x, lam, t)

                # State dynamics: dx/dt = f(x, u*, t)
                dx_dt = dynamics(x, u_opt, t)

                # Costate dynamics: dλ/dt = -∂H/∂x (numerical gradient)
                eps = 1e-6
                dlam_dt = np.zeros(n_states)
                for i in range(n_states):
                    x_plus = x.copy()
                    x_plus[i] += eps
                    x_minus = x.copy()
                    x_minus[i] -= eps

                    H_plus = hamiltonian(x_plus, u_opt, lam, t)
                    H_minus = hamiltonian(x_minus, u_opt, lam, t)

                    dlam_dt[i] = -(H_plus - H_minus) / (2 * eps)

                return np.concatenate([dx_dt, dlam_dt])

            # Initial condition: [x0, λ0]
            z0 = np.concatenate([x0, lam0])

            # Solve forward
            sol = solve_ivp(
                ode_system,
                t_span,
                z0,
                dense_output=True,
                max_step=(tf - t0) / 100
            )

            if not sol.success:
                return 1e6 * np.ones(n_states)

            # Terminal state
            z_final = sol.sol(tf)
            x_final = z_final[:n_states]

            # Error: x(tf) - xf (if terminal constraint specified)
            if xf is not None:
                return x_final - np.array(xf)
            else:
                # Free terminal state: λ(tf) = 0 (simplest transversality)
                lam_final = z_final[n_states:]
                return lam_final

        # Find λ0 via root finding (simplified: use optimization)
        result_opt = minimize(
            lambda lam: np.sum(shooting_error(lam)**2),
            x0=lambda_guess,
            method='Nelder-Mead',
            options={'maxiter': n_iterations}
        )

        lambda_opt = result_opt.x

        # Solve with optimal λ0
        def ode_system_optimal(t, z):
            """ODE system for optimal trajectory: [dx/dt, dλ/dt] with optimal control."""
            x = z[:n_states]
            lam = z[n_states:]
            u_opt = optimal_control(x, lam, t)

            dx_dt = dynamics(x, u_opt, t)

            # Costate
            eps = 1e-6
            dlam_dt = np.zeros(n_states)
            for i in range(n_states):
                x_plus = x.copy()
                x_plus[i] += eps
                x_minus = x.copy()
                x_minus[i] -= eps
                H_plus = hamiltonian(x_plus, u_opt, lam, t)
                H_minus = hamiltonian(x_minus, u_opt, lam, t)
                dlam_dt[i] = -(H_plus - H_minus) / (2 * eps)

            return np.concatenate([dx_dt, dlam_dt])

        z0_opt = np.concatenate([x0, lambda_opt])
        sol_opt = solve_ivp(
            ode_system_optimal,
            t_span,
            z0_opt,
            dense_output=True,
            max_step=(tf - t0) / 100
        )

        if not sol_opt.success:
            return {'error': 'PMP solution failed', 'message': sol_opt.message}

        # Extract trajectory
        t_grid = np.linspace(t0, tf, 100)
        z_trajectory = sol_opt.sol(t_grid)
        x_trajectory = z_trajectory[:n_states, :]
        lambda_trajectory = z_trajectory[n_states:, :]

        # Compute optimal controls
        u_trajectory = [
            optimal_control(x_trajectory[:, i], lambda_trajectory[:, i], t_grid[i])
            for i in range(len(t_grid))
        ]

        # Compute total cost
        total_cost = 0.0
        for i in range(len(t_grid) - 1):
            dt = t_grid[i + 1] - t_grid[i]
            x_i = x_trajectory[:, i]
            u_i = u_trajectory[i]
            total_cost += cost(x_i, u_i, t_grid[i]) * dt

        return {
            'success': True,
            't_grid': t_grid.tolist(),
            'x_trajectory': x_trajectory.tolist(),
            'u_trajectory': u_trajectory,
            'lambda_trajectory': lambda_trajectory.tolist(),
            'total_cost': float(total_cost),
            'initial_costate': lambda_opt.tolist(),
            'method': 'pontryagin_maximum_principle',
            'note': 'Necessary conditions: ∂H/∂u = 0, dx/dt = ∂H/∂λ, dλ/dt = -∂H/∂x'
        }

    # ========== HAMILTON-JACOBI-BELLMAN EQUATION ==========

    def solve_hamilton_jacobi_bellman(
        self,
        dynamics: Callable[[np.ndarray, np.ndarray], np.ndarray],
        cost: Callable[[np.ndarray, np.ndarray], float],
        boundary: Dict[str, Any],
        x_grid: np.ndarray = None,
        n_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Solve Hamilton-Jacobi-Bellman equation via value iteration.

        HJB equation: -∂V/∂t = min_u [L(x, u) + (∂V/∂x)^T f(x, u)]

        For infinite-horizon: 0 = min_u [L(x, u) + (∂V/∂x)^T f(x, u)]

        Value iteration: V_{k+1}(x) = min_u [L(x, u) + V_k(f(x, u))]

        Args:
            dynamics: f(x, u) - discrete-time dynamics
            cost: L(x, u) - stage cost
            boundary: Terminal cost, grid bounds
            x_grid: State space discretization
            n_iterations: Value iteration steps

        Returns:
            Dictionary with value function and optimal policy
        """
        logger.info("Solving Hamilton-Jacobi-Bellman via value iteration")

        # Default 1D grid
        if x_grid is None:
            x_min = boundary.get('x_min', -5.0)
            x_max = boundary.get('x_max', 5.0)
            n_grid = boundary.get('n_grid', 51)
            x_grid = np.linspace(x_min, x_max, n_grid)

        n_grid = len(x_grid)
        u_values = boundary.get('u_values', np.linspace(-1, 1, 11))

        # Initialize value function (terminal cost or zeros)
        V = boundary.get('terminal_cost', np.zeros(n_grid))

        # Policy storage
        policy = np.zeros(n_grid)

        # Value iteration
        for iteration in range(n_iterations):
            V_new = np.zeros(n_grid)

            for i, x in enumerate(x_grid):
                # Minimize over controls
                min_cost = float('inf')
                best_u = 0.0

                for u in u_values:
                    # Next state
                    x_next = dynamics(np.array([x]), np.array([u]))[0]

                    # Interpolate V(x_next) from grid
                    if x_next < x_grid[0]:
                        V_next = V[0]
                    elif x_next > x_grid[-1]:
                        V_next = V[-1]
                    else:
                        # Linear interpolation
                        V_next = np.interp(x_next, x_grid, V)

                    # Cost-to-go: L(x, u) + γ * V(x_next)
                    gamma = boundary.get('discount', 0.95)
                    cost_to_go = cost(np.array([x]), np.array([u])) + gamma * V_next

                    if cost_to_go < min_cost:
                        min_cost = cost_to_go
                        best_u = u

                V_new[i] = min_cost
                policy[i] = best_u

            # Check convergence
            if np.max(np.abs(V_new - V)) < 1e-6:
                logger.info(f"HJB converged at iteration {iteration}")
                V = V_new
                break

            V = V_new

        return {
            'success': True,
            'x_grid': x_grid.tolist(),
            'value_function': V.tolist(),
            'optimal_policy': policy.tolist(),
            'iterations': iteration + 1,
            'method': 'hamilton_jacobi_bellman_value_iteration',
            'note': 'Value function V(x) and optimal policy u*(x) = argmin_u [L + ∂V/∂x * f]'
        }

    # ========== LINEAR QUADRATIC REGULATOR (LQR) ==========

    def solve_lqr_problem(
        self,
        A: np.ndarray,
        B: np.ndarray,
        Q: np.ndarray,
        R: np.ndarray,
        N: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Solve Linear Quadratic Regulator problem.

        System: dx/dt = A*x + B*u
        Cost: J = ∫ (x^T Q x + u^T R u) dt

        Optimal control: u*(t) = -K*x(t)
        where K = R^{-1} B^T P

        P is solution to Continuous Algebraic Riccati Equation (CARE):
        A^T P + P A - P B R^{-1} B^T P + Q = 0

        Args:
            A: State matrix (n x n)
            B: Input matrix (n x m)
            Q: State cost matrix (n x n, positive semidefinite)
            R: Input cost matrix (m x m, positive definite)
            N: Cross term (optional, n x m)

        Returns:
            Dictionary with feedback gain K and Riccati solution P
        """
        logger.info("Solving LQR problem")

        A = np.array(A, dtype=float)
        B = np.array(B, dtype=float)
        Q = np.array(Q, dtype=float)
        R = np.array(R, dtype=float)

        if B.ndim == 1:
            B = B.reshape(-1, 1)

        if N is not None:
            N = np.array(N, dtype=float)
        else:
            N = np.zeros((A.shape[0], B.shape[1]))

        # Solve CARE
        try:
            P = solve_continuous_are(A, B, Q, R, e=None, s=N)
        except Exception as e:
            return {'error': f'CARE solution failed: {e}'}

        # Compute optimal gain K = R^{-1} (B^T P + N^T)
        K = np.linalg.solve(R, B.T @ P + N.T)

        # Closed-loop eigenvalues
        A_cl = A - B @ K
        eigenvalues = np.linalg.eigvals(A_cl)

        # Check stability (all real parts negative)
        is_stable = bool(np.all(np.real(eigenvalues) < 0))

        return {
            'success': True,
            'K': K.tolist(),
            'P': P.tolist(),
            'closed_loop_eigenvalues': eigenvalues.tolist(),
            'is_stable': is_stable,
            'method': 'lqr_continuous_are',
            'note': 'Optimal control: u = -K*x'
        }

    # ========== LINEAR QUADRATIC GAUSSIAN (LQG) ==========

    def solve_lqg_problem(
        self,
        A: np.ndarray,
        B: np.ndarray,
        C: np.ndarray,
        Q: np.ndarray,
        R: np.ndarray,
        W: np.ndarray,
        V: np.ndarray
    ) -> Dict[str, Any]:
        """
        Solve Linear Quadratic Gaussian (LQG) problem.

        System: dx/dt = A*x + B*u + w, y = C*x + v
        w ~ N(0, W): process noise
        v ~ N(0, V): measurement noise

        Cost: J = E[∫ (x^T Q x + u^T R u) dt]

        LQG = LQR (control) + Kalman Filter (estimation)
        Separation principle: design independently

        Args:
            A, B, C: System matrices
            Q, R: LQR cost matrices
            W: Process noise covariance
            V: Measurement noise covariance

        Returns:
            Dictionary with LQR gain K and Kalman gain L
        """
        logger.info("Solving LQG problem")

        A = np.array(A, dtype=float)
        B = np.array(B, dtype=float)
        C = np.array(C, dtype=float)
        Q = np.array(Q, dtype=float)
        R = np.array(R, dtype=float)
        W = np.array(W, dtype=float)
        V = np.array(V, dtype=float)

        if B.ndim == 1:
            B = B.reshape(-1, 1)
        if C.ndim == 1:
            C = C.reshape(1, -1)

        # Step 1: Solve LQR for control gain K
        try:
            P = solve_continuous_are(A, B, Q, R)
            K = np.linalg.solve(R, B.T @ P)
        except Exception as e:
            return {'error': f'LQR part failed: {e}'}

        # Step 2: Solve Kalman filter for observer gain L
        # Dual ARE: A^T Σ + Σ A - Σ C^T V^{-1} C Σ + W = 0
        try:
            Sigma = solve_continuous_are(A.T, C.T, W, V)
            L = Sigma @ C.T @ np.linalg.inv(V)
        except Exception as e:
            return {'error': f'Kalman filter part failed: {e}'}

        # Closed-loop controller: u = -K * x_hat
        # Observer: dx_hat/dt = (A - L*C)*x_hat + B*u + L*y

        # Compensator eigenvalues
        A_ctrl = A - B @ K
        A_obs = A - L @ C
        ctrl_eigenvalues = np.linalg.eigvals(A_ctrl)
        obs_eigenvalues = np.linalg.eigvals(A_obs)

        return {
            'success': True,
            'K': K.tolist(),
            'L': L.tolist(),
            'P': P.tolist(),
            'Sigma': Sigma.tolist(),
            'controller_eigenvalues': ctrl_eigenvalues.tolist(),
            'observer_eigenvalues': obs_eigenvalues.tolist(),
            'method': 'lqg_separation_principle',
            'note': 'LQG = LQR control + Kalman filter estimation'
        }

    # ========== BANG-BANG CONTROL ==========

    def compute_bang_bang_control(
        self,
        dynamics: Callable[[np.ndarray, np.ndarray], np.ndarray],
        constraints: Dict[str, Any],
        t_span: Tuple[float, float] = (0, 10),
        n_switches: int = 5
    ) -> Dict[str, Any]:
        """
        Compute bang-bang control for time-optimal problems.

        For linear systems, optimal control is bang-bang:
        u*(t) ∈ {u_min, u_max} (switching between extremes)

        Number of switches ≤ n-1 for n-dimensional system.

        Args:
            dynamics: System dynamics f(x, u)
            constraints: x0, xf, u_min, u_max
            t_span: Time interval
            n_switches: Maximum number of switches

        Returns:
            Dictionary with bang-bang control profile
        """
        logger.info("Computing bang-bang control")

        x0 = np.array(constraints.get('x0', [0.0, 0.0]))
        xf = np.array(constraints.get('xf', [1.0, 0.0]))
        u_min = constraints.get('u_min', -1.0)
        u_max = constraints.get('u_max', 1.0)

        t0, tf_max = t_span

        # Parameterize bang-bang: sequence of switching times
        # Control: u(t) = u_max if t in [t0, t1) ∪ [t2, t3) ..., else u_min

        def simulate_bang_bang(switch_times, initial_control):
            """
            Simulate system with bang-bang control.
            """
            switch_times = sorted([t0] + list(switch_times) + [tf_max])
            t_segments = [(switch_times[i], switch_times[i + 1]) for i in range(len(switch_times) - 1)]

            x_current = x0.copy()
            control_sequence = [initial_control]

            for i, (t_start, t_end) in enumerate(t_segments):
                u_segment = control_sequence[-1]

                # Integrate dynamics over segment
                def ode(t, x):
                    """ODE for state dynamics with constant control."""
                    return dynamics(x, np.array([u_segment]))

                sol = solve_ivp(ode, (t_start, t_end), x_current, dense_output=True)
                if sol.success:
                    x_current = sol.y[:, -1]
                else:
                    return None, None

                # Switch control
                control_sequence.append(u_max if u_segment == u_min else u_min)

            return x_current, control_sequence[:-1]

        # Optimize switch times to reach xf
        def objective(params):
            """Minimize error in reaching target."""
            switch_times = params[:n_switches]
            initial_control = u_max if params[n_switches] > 0 else u_min

            x_final, _ = simulate_bang_bang(switch_times, initial_control)

            if x_final is None:
                return 1e6

            return np.sum((x_final - xf)**2)

        # Initial guess
        switch_guess = np.linspace(t0, tf_max, n_switches + 2)[1:-1]
        initial_control_guess = 1.0

        result_opt = minimize(
            objective,
            x0=np.concatenate([switch_guess, [initial_control_guess]]),
            method='Nelder-Mead',
            options={'maxiter': 500}
        )

        # Extract optimal switches
        switch_times_opt = sorted(result_opt.x[:n_switches])
        initial_control_opt = u_max if result_opt.x[n_switches] > 0 else u_min

        x_final_opt, control_sequence_opt = simulate_bang_bang(switch_times_opt, initial_control_opt)

        return {
            'success': True,
            'switch_times': switch_times_opt.tolist(),
            'control_sequence': control_sequence_opt,
            'u_min': u_min,
            'u_max': u_max,
            'final_state': x_final_opt.tolist() if x_final_opt is not None else None,
            'error': float(result_opt.fun),
            'method': 'bang_bang_time_optimal',
            'note': 'Optimal control switches between extremal values u_min and u_max'
        }

    # ========== TIME-OPTIMAL CONTROL ==========

    def solve_time_optimal_control(
        self,
        dynamics: Callable[[np.ndarray, np.ndarray], np.ndarray],
        target: np.ndarray,
        constraints: Dict[str, Any],
        max_time: float = 20.0
    ) -> Dict[str, Any]:
        """
        Solve time-optimal control: minimize time T to reach target.

        Cost: J = T (minimize final time)
        System: dx/dt = f(x, u)
        Constraint: x(T) = x_target

        Often results in bang-bang control for linear systems.

        Args:
            dynamics: System dynamics f(x, u)
            target: Target state x_target
            constraints: x0, u_min, u_max
            max_time: Upper bound on time

        Returns:
            Dictionary with minimum time and control profile
        """
        logger.info("Solving time-optimal control")

        x0 = np.array(constraints.get('x0', [0.0, 0.0]))
        u_min = constraints.get('u_min', -1.0)
        u_max = constraints.get('u_max', 1.0)

        # Use bang-bang with time as variable
        def objective_time(params):
            """Minimize time + penalty for not reaching target."""
            tf = params[0]
            switch_times = params[1:]

            if tf <= 0 or tf > max_time:
                return 1e6

            # Simulate bang-bang
            switch_times = sorted([0.0] + list(switch_times) + [tf])
            t_segments = [(switch_times[i], switch_times[i + 1]) for i in range(len(switch_times) - 1)]

            x_current = x0.copy()
            control = u_max

            for t_start, t_end in t_segments:
                def ode(t, x):
                    """ODE for state dynamics with bang-bang control."""
                    return dynamics(x, np.array([control]))

                sol = solve_ivp(ode, (t_start, t_end), x_current, dense_output=True)
                if sol.success:
                    x_current = sol.y[:, -1]
                else:
                    return 1e6

                control = u_min if control == u_max else u_max

            # Objective: time + penalty
            distance_to_target = np.linalg.norm(x_current - target)
            return tf + 100 * distance_to_target

        # Optimize
        n_switches = 3
        initial_guess = np.concatenate([[max_time / 2], np.linspace(0, max_time / 2, n_switches + 2)[1:-1]])

        result_opt = minimize(
            objective_time,
            x0=initial_guess,
            method='Nelder-Mead',
            options={'maxiter': 500}
        )

        tf_opt = result_opt.x[0]

        return {
            'success': True,
            'optimal_time': float(tf_opt),
            'switch_times': result_opt.x[1:].tolist(),
            'method': 'time_optimal_bang_bang',
            'note': f'Minimum time to reach target: {tf_opt:.3f}'
        }

    # ========== REACHABILITY ANALYSIS ==========

    def compute_reachable_set(
        self,
        dynamics: Callable[[np.ndarray, np.ndarray], np.ndarray],
        initial_set: np.ndarray,
        time: float,
        control_bounds: Tuple[float, float] = (-1.0, 1.0),
        n_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Compute forward reachable set: states reachable from initial set
        under all admissible controls within time T.

        R(T) = {x(T) : x(0) ∈ X0, u(t) ∈ U for all t ∈ [0, T]}

        Args:
            dynamics: System dynamics f(x, u)
            initial_set: Initial states (n_init x n_dim)
            time: Time horizon T
            control_bounds: Admissible control set [u_min, u_max]
            n_samples: Number of control samples

        Returns:
            Dictionary with reachable set approximation
        """
        logger.info(f"Computing reachable set at time T={time}")

        u_min, u_max = control_bounds
        u_samples = np.linspace(u_min, u_max, n_samples)

        reachable_states = []

        for x0 in initial_set:
            for u_const in u_samples:
                # Simulate with constant control
                def ode(t, x):
                    """ODE for reachability analysis with constant control."""
                    return dynamics(x, np.array([u_const]))

                sol = solve_ivp(ode, (0, time), x0, dense_output=True)

                if sol.success:
                    x_final = sol.y[:, -1]
                    reachable_states.append(x_final)

        reachable_states = np.array(reachable_states)

        # Compute convex hull (approximate reachable set)
        from scipy.spatial import ConvexHull

        if len(reachable_states) > 2 and reachable_states.shape[1] == 2:
            try:
                hull = ConvexHull(reachable_states)
                hull_vertices = reachable_states[hull.vertices]
            except Exception:
                hull_vertices = reachable_states
        else:
            hull_vertices = reachable_states

        return {
            'success': True,
            'reachable_states': reachable_states.tolist(),
            'hull_vertices': hull_vertices.tolist() if hasattr(hull_vertices, 'tolist') else [],
            'n_samples': len(reachable_states),
            'time': time,
            'method': 'forward_reachability_sampling',
            'note': 'Approximation of reachable set via control sampling'
        }

    # ========== CONTROLLABILITY ==========

    def verify_controllability(
        self,
        A: np.ndarray,
        B: np.ndarray
    ) -> Dict[str, Any]:
        """
        Verify controllability of linear system dx/dt = Ax + Bu.

        System is controllable iff rank(C) = n, where
        C = [B, AB, A²B, ..., A^{n-1}B] is the controllability matrix.

        Args:
            A: State matrix (n x n)
            B: Input matrix (n x m)

        Returns:
            Dictionary with controllability result
        """
        logger.info("Verifying controllability")

        A = np.array(A, dtype=float)
        B = np.array(B, dtype=float)

        if B.ndim == 1:
            B = B.reshape(-1, 1)

        n = A.shape[0]
        m = B.shape[1]

        # Construct controllability matrix
        C = np.zeros((n, n * m))
        A_power = np.eye(n)

        for i in range(n):
            C[:, i * m:(i + 1) * m] = A_power @ B
            A_power = A_power @ A

        # Compute rank
        rank = np.linalg.matrix_rank(C)
        is_controllable = (rank == n)

        return {
            'success': True,
            'is_controllable': is_controllable,
            'controllability_matrix_rank': int(rank),
            'state_dimension': int(n),
            'controllability_matrix': C.tolist(),
            'method': 'controllability_rank_test',
            'note': 'System is controllable iff rank([B AB A²B ... A^{n-1}B]) = n'
        }

    # ========== VALUE FUNCTION COMPUTATION ==========

    def compute_value_function(
        self,
        dynamics: Callable[[np.ndarray, np.ndarray], np.ndarray],
        cost: Callable[[np.ndarray, np.ndarray], float],
        x_grid: np.ndarray,
        horizon: int = 100,
        discount: float = 0.95
    ) -> Dict[str, Any]:
        """
        Compute value function via dynamic programming.

        V_T(x) = 0 (terminal)
        V_k(x) = min_u [L(x, u) + γ * V_{k+1}(f(x, u))]

        Args:
            dynamics: f(x, u) - discrete dynamics
            cost: L(x, u) - stage cost
            x_grid: State space discretization
            horizon: Planning horizon T
            discount: Discount factor γ

        Returns:
            Dictionary with value function over time
        """
        logger.info(f"Computing value function with horizon T={horizon}")

        n_grid = len(x_grid)
        u_values = np.linspace(-1, 1, 11)

        # Value function storage: V[k, i] = V_k(x_i)
        V = np.zeros((horizon + 1, n_grid))

        # Backward induction
        for k in range(horizon - 1, -1, -1):
            for i, x in enumerate(x_grid):
                min_cost = float('inf')

                for u in u_values:
                    # Next state
                    x_next = dynamics(np.array([x]), np.array([u]))[0]

                    # Interpolate V_{k+1}(x_next)
                    V_next = np.interp(x_next, x_grid, V[k + 1])

                    # Cost-to-go
                    cost_to_go = cost(np.array([x]), np.array([u])) + discount * V_next

                    if cost_to_go < min_cost:
                        min_cost = cost_to_go

                V[k, i] = min_cost

        return {
            'success': True,
            'x_grid': x_grid.tolist(),
            'value_function': V.tolist(),
            'horizon': horizon,
            'discount': discount,
            'method': 'dynamic_programming_value_iteration',
            'note': 'V_k(x) = value function at stage k'
        }

    # ========== BDI METHODS ==========

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard:
            entries = self.blackboard.query_entries(
                tags=['optimal_control'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                self.add_belief('pending_control_task', entry, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """Generate intentions for optimal control tasks."""
        intentions = []

        if self.tasks_executed > 50:
            intentions.append(Intention('update_control_cache', priority=1))

        if self.has_belief('pending_control_task'):
            task_belief = self.get_belief('pending_control_task')
            if task_belief:
                intentions.append(Intention(
                    'solve_optimal_control',
                    priority=5,
                    context={'task': task_belief.content}
                ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute intention step."""
        if intention.action == 'update_control_cache':
            # Clear old cached controls
            if len(self.control_cache) > 100:
                self.control_cache.clear()
                logger.info(f"[{self.agent_id}] Cleared control cache")

    def get_statistics(self):
        """Return agent statistics."""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': f'{self.tasks_succeeded / max(self.tasks_executed, 1) * 100:.1f}%'
        }
