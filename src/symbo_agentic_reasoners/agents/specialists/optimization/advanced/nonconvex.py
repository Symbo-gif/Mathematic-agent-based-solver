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
NONCONVEX OPTIMIZATION SPECIALIST - Trust region, SQP, penalty methods
=====================================================================

Handles nonconvex optimization problems using advanced techniques.

CRITICAL ALGORITHMS:
-------------------
- Trust Region Method: Iterative trust region optimization
- Sequential Quadratic Programming (SQP): Constrained optimization via QP subproblems
- Penalty Methods: Exterior penalty approach
- Barrier Methods: Interior point via logarithmic barriers
- Augmented Lagrangian: ADMM and multiplier methods
- KKT Conditions: Karush-Kuhn-Tucker optimality verification
- Backtracking Line Search: Adaptive step size selection

WHY THIS MATTERS:
----------------
Nonconvex optimization is fundamental to:
- Machine learning (neural network training)
- Engineering design optimization
- Economic equilibrium computation
- Robotics trajectory planning
- Many real-world applications lack convexity

CAPABILITIES:
------------
- Solve nonconvex unconstrained problems
- Handle equality and inequality constraints
- Verify local optimality via KKT conditions
- Adaptive trust region sizing
- Sequential linearization methods

NO SYMPY - Pure NumPy/SciPy native implementation
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from scipy.optimize import minimize as scipy_minimize, LinearConstraint, NonlinearConstraint
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class NonconvexOptimizationSpecialist(BDIAgent):
    """
    Nonconvex Optimization Specialist - Trust region, SQP, penalty methods

    DIRECTIVE:
    ---------
    Handle all nonconvex optimization problems with emphasis on:
    - Trust region methods for local optimization
    - Sequential quadratic programming
    - Penalty and barrier methods
    - KKT condition verification

    KEY ALGORITHMS:
    --------------
    - Trust Region: Minimize quadratic model within trust region
    - SQP: Solve sequence of QP approximations
    - Penalty: Convert constraints to penalty terms
    - Augmented Lagrangian: Dual methods with multipliers

    OPERATIONS:
    ----------
    - trust_region_method(objective, x0, radius)
    - sequential_quadratic_programming(objective, constraints, x0)
    - penalty_method(objective, constraints, penalty_param)
    - barrier_method(objective, constraints, barrier_param)
    - augmented_lagrangian(objective, constraints, lambda0)
    - compute_kkt_conditions(objective, constraints, x)
    - line_search_backtracking(objective, x, direction)
    - check_local_optimum(objective, x, tolerance)
    """

    def __init__(self, agent_id='nonconvex_specialist_001', df=None, blackboard=None):
        """
        Initialize Nonconvex Optimization Specialist

        Args:
            agent_id: Unique identifier for this agent
            df: Directory Facilitator instance
            blackboard: Shared blackboard instance
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.optimization_cache = {}
        self.recent_tasks = []

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.optimization.advanced.nonconvex',
                agent_id=self.agent_id,
                algorithm='nonconvex',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process nonconvex optimization task

        Args:
            task_entry: Task entry with metadata

        Returns:
            Dictionary with optimization results
        """
        self.tasks_executed += 1
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'trust_region')

        try:
            if problem_type == 'trust_region':
                return self._handle_trust_region(metadata)
            elif problem_type == 'sqp':
                return self._handle_sqp(metadata)
            elif problem_type == 'penalty':
                return self._handle_penalty(metadata)
            elif problem_type == 'barrier':
                return self._handle_barrier(metadata)
            elif problem_type == 'augmented_lagrangian':
                return self._handle_augmented_lagrangian(metadata)
            elif problem_type == 'kkt_check':
                return self._handle_kkt_check(metadata)
            elif problem_type == 'line_search':
                return self._handle_line_search(metadata)
            elif problem_type == 'local_optimum':
                return self._handle_local_optimum(metadata)
            else:
                return {'operation': 'nonconvex', 'error': f'Unknown problem type: {problem_type}'}
        except Exception as e:
            return {'operation': 'nonconvex', 'error': str(e)}

    def _handle_trust_region(self, metadata: Dict) -> Dict[str, Any]:
        """Handle trust region optimization request"""
        objective = metadata.get('objective')
        x0 = np.array(metadata.get('x0', [0.0, 0.0]), dtype=float)
        initial_radius = metadata.get('radius', 1.0)
        max_iterations = metadata.get('max_iterations', 100)
        tolerance = metadata.get('tolerance', 1e-6)

        result = self.trust_region_method(objective, x0, initial_radius, max_iterations, tolerance)
        return {'operation': 'trust_region', 'result': result}

    def _handle_sqp(self, metadata: Dict) -> Dict[str, Any]:
        """Handle SQP request"""
        objective = metadata.get('objective')
        constraints = metadata.get('constraints', [])
        x0 = np.array(metadata.get('x0', [0.0, 0.0]), dtype=float)
        max_iterations = metadata.get('max_iterations', 100)
        tolerance = metadata.get('tolerance', 1e-6)

        result = self.sequential_quadratic_programming(objective, constraints, x0, max_iterations, tolerance)
        return {'operation': 'sqp', 'result': result}

    def _handle_penalty(self, metadata: Dict) -> Dict[str, Any]:
        """Handle penalty method request"""
        objective = metadata.get('objective')
        constraints = metadata.get('constraints', [])
        penalty_param = metadata.get('penalty_param', 10.0)
        x0 = np.array(metadata.get('x0', [0.0, 0.0]), dtype=float)

        result = self.penalty_method(objective, constraints, penalty_param, x0)
        return {'operation': 'penalty', 'result': result}

    def _handle_barrier(self, metadata: Dict) -> Dict[str, Any]:
        """Handle barrier method request"""
        objective = metadata.get('objective')
        constraints = metadata.get('constraints', [])
        barrier_param = metadata.get('barrier_param', 0.1)
        x0 = np.array(metadata.get('x0', [0.0, 0.0]), dtype=float)

        result = self.barrier_method(objective, constraints, barrier_param, x0)
        return {'operation': 'barrier', 'result': result}

    def _handle_augmented_lagrangian(self, metadata: Dict) -> Dict[str, Any]:
        """Handle augmented Lagrangian request"""
        objective = metadata.get('objective')
        constraints = metadata.get('constraints', [])
        lambda0 = metadata.get('lambda0', None)
        x0 = np.array(metadata.get('x0', [0.0, 0.0]), dtype=float)

        result = self.augmented_lagrangian(objective, constraints, lambda0, x0)
        return {'operation': 'augmented_lagrangian', 'result': result}

    def _handle_kkt_check(self, metadata: Dict) -> Dict[str, Any]:
        """Handle KKT condition check"""
        objective = metadata.get('objective')
        constraints = metadata.get('constraints', [])
        x = np.array(metadata.get('x'), dtype=float)
        tolerance = metadata.get('tolerance', 1e-6)

        result = self.compute_kkt_conditions(objective, constraints, x, tolerance)
        return {'operation': 'kkt_check', 'result': result}

    def _handle_line_search(self, metadata: Dict) -> Dict[str, Any]:
        """Handle line search request"""
        objective = metadata.get('objective')
        x = np.array(metadata.get('x'), dtype=float)
        direction = np.array(metadata.get('direction'), dtype=float)

        alpha = self.line_search_backtracking(objective, x, direction)
        return {'operation': 'line_search', 'alpha': float(alpha)}

    def _handle_local_optimum(self, metadata: Dict) -> Dict[str, Any]:
        """Handle local optimum verification"""
        objective = metadata.get('objective')
        x = np.array(metadata.get('x'), dtype=float)
        tolerance = metadata.get('tolerance', 1e-6)

        is_local_opt = self.check_local_optimum(objective, x, tolerance)
        return {'operation': 'local_optimum_check', 'is_local_optimum': is_local_opt}

    # =========================================================================
    # TRUST REGION METHOD
    # =========================================================================

    def trust_region_method(self, objective: Callable, x0: np.ndarray,
                           initial_radius: float = 1.0, max_iterations: int = 100,
                           tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Trust region method for nonconvex optimization

        Solves: min_d m(d) s.t. ||d|| <= Delta
        where m(d) = f + g^T d + 0.5 d^T H d (quadratic model)

        Args:
            objective: Objective function f(x)
            x0: Initial point
            initial_radius: Initial trust region radius Delta
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dictionary with optimal point, value, iterations
        """
        x = x0.copy()
        radius = initial_radius
        eta1, eta2 = 0.25, 0.75  # Trust region update thresholds

        for iteration in range(max_iterations):
            # Compute gradient and Hessian
            grad = self._numerical_gradient(objective, x)
            hess = self._numerical_hessian(objective, x)

            # Check convergence
            grad_norm = np.linalg.norm(grad)
            if grad_norm < tolerance:
                return {
                    'status': 'converged',
                    'optimal_x': x.tolist(),
                    'optimal_value': float(objective(x)),
                    'iterations': iteration,
                    'final_gradient_norm': float(grad_norm),
                    'method': 'trust_region'
                }

            # Solve trust region subproblem (Cauchy point approximation)
            # Exact: minimize m(d) s.t. ||d|| <= radius
            # Approximate: Use Cauchy point or dogleg method
            step = self._solve_trust_region_subproblem(grad, hess, radius)

            # Compute actual vs predicted reduction
            f_current = objective(x)
            f_trial = objective(x + step)
            actual_reduction = f_current - f_trial

            # Quadratic model prediction
            predicted_reduction = -(grad @ step + 0.5 * step @ hess @ step)

            # Compute reduction ratio
            rho = actual_reduction / (predicted_reduction + 1e-15)

            # Update trust region radius
            if rho < eta1:
                # Poor agreement - shrink radius
                radius *= 0.25
            elif rho > eta2 and np.linalg.norm(step) >= 0.9 * radius:
                # Good agreement and at boundary - expand radius
                radius *= 2.0

            # Accept or reject step
            if rho > 0.1:  # Accept step
                x = x + step

        return {
            'status': 'max_iterations',
            'optimal_x': x.tolist(),
            'optimal_value': float(objective(x)),
            'iterations': max_iterations,
            'final_gradient_norm': float(np.linalg.norm(self._numerical_gradient(objective, x))),
            'method': 'trust_region'
        }

    def _solve_trust_region_subproblem(self, grad: np.ndarray, hess: np.ndarray,
                                       radius: float) -> np.ndarray:
        """
        Solve trust region subproblem using Cauchy point

        Args:
            grad: Gradient vector
            hess: Hessian matrix
            radius: Trust region radius

        Returns:
            Step vector
        """
        # Cauchy point: minimize along steepest descent direction
        tau = 1.0
        g_norm_sq = grad @ grad
        g_H_g = grad @ hess @ grad

        if g_H_g > 0:
            tau = min(1.0, g_norm_sq ** 1.5 / (radius * g_H_g))

        # Cauchy step
        p_c = -tau * radius * grad / np.linalg.norm(grad)

        # Try Newton step if inside trust region
        try:
            p_newton = -np.linalg.solve(hess, grad)
            if np.linalg.norm(p_newton) <= radius:
                return p_newton
        except np.linalg.LinAlgError:
            pass

        return p_c

    # =========================================================================
    # SEQUENTIAL QUADRATIC PROGRAMMING (SQP)
    # =========================================================================

    def sequential_quadratic_programming(self, objective: Callable,
                                        constraints: List[Dict], x0: np.ndarray,
                                        max_iterations: int = 100,
                                        tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Sequential Quadratic Programming for constrained optimization

        Solves: min f(x) s.t. c_i(x) = 0, g_j(x) <= 0
        by solving sequence of QP subproblems

        Args:
            objective: Objective function f(x)
            constraints: List of constraint dicts {'type': 'eq'/'ineq', 'fun': callable}
            x0: Initial point
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dictionary with optimal point and status
        """
        # Convert constraints to scipy format
        scipy_constraints = []
        for constraint in constraints:
            if constraint['type'] == 'eq':
                scipy_constraints.append({'type': 'eq', 'fun': constraint['fun']})
            elif constraint['type'] == 'ineq':
                # SciPy uses >= 0 convention, so negate if necessary
                scipy_constraints.append({'type': 'ineq', 'fun': constraint['fun']})

        # Use SciPy's SLSQP (SQP implementation)
        result = scipy_minimize(objective, x0, method='SLSQP',
                               constraints=scipy_constraints,
                               options={'maxiter': max_iterations, 'ftol': tolerance})

        return {
            'status': 'converged' if result.success else 'failed',
            'optimal_x': result.x.tolist(),
            'optimal_value': float(result.fun),
            'iterations': result.nit if hasattr(result, 'nit') else max_iterations,
            'message': result.message,
            'method': 'sqp'
        }

    # =========================================================================
    # PENALTY METHOD
    # =========================================================================

    def penalty_method(self, objective: Callable, constraints: List[Dict],
                      penalty_param: float, x0: np.ndarray,
                      max_iterations: int = 100) -> Dict[str, Any]:
        """
        Penalty method for constrained optimization

        Converts: min f(x) s.t. c(x) = 0, g(x) <= 0
        To: min f(x) + rho * sum(c_i(x)^2) + rho * sum(max(0, g_j(x))^2)

        Args:
            objective: Objective function f(x)
            constraints: List of constraint dicts
            penalty_param: Penalty parameter rho (> 0)
            x0: Initial point
            max_iterations: Maximum iterations

        Returns:
            Dictionary with optimal point
        """
        def penalized_objective(x):
            """Objective with penalty terms"""
            obj_value = objective(x)
            penalty = 0.0

            for constraint in constraints:
                c_val = constraint['fun'](x)
                if constraint['type'] == 'eq':
                    # Equality: rho * c^2
                    penalty += penalty_param * c_val ** 2
                elif constraint['type'] == 'ineq':
                    # Inequality: rho * max(0, -g)^2 (assuming g >= 0)
                    penalty += penalty_param * max(0, -c_val) ** 2

            return obj_value + penalty

        # Minimize penalized objective
        result = scipy_minimize(penalized_objective, x0, method='BFGS',
                               options={'maxiter': max_iterations})

        return {
            'status': 'converged' if result.success else 'failed',
            'optimal_x': result.x.tolist(),
            'optimal_value': float(objective(result.x)),
            'penalized_value': float(result.fun),
            'method': 'penalty'
        }

    # =========================================================================
    # BARRIER METHOD
    # =========================================================================

    def barrier_method(self, objective: Callable, constraints: List[Dict],
                      barrier_param: float, x0: np.ndarray,
                      max_iterations: int = 100) -> Dict[str, Any]:
        """
        Barrier method for inequality-constrained optimization

        Uses logarithmic barrier: f(x) - mu * sum(log(g_j(x)))
        Requires interior point (all g_j(x) > 0)

        Args:
            objective: Objective function f(x)
            constraints: Inequality constraints g(x) >= 0
            barrier_param: Barrier parameter mu (> 0)
            x0: Initial interior point
            max_iterations: Maximum iterations

        Returns:
            Dictionary with optimal point
        """
        def barrier_objective(x):
            """Objective with log barrier"""
            obj_value = objective(x)
            barrier = 0.0

            for constraint in constraints:
                if constraint['type'] == 'ineq':
                    g_val = constraint['fun'](x)
                    if g_val <= 1e-10:
                        return 1e10  # Infeasible
                    barrier -= barrier_param * np.log(g_val)

            return obj_value + barrier

        # Minimize barrier objective
        result = scipy_minimize(barrier_objective, x0, method='BFGS',
                               options={'maxiter': max_iterations})

        return {
            'status': 'converged' if result.success else 'failed',
            'optimal_x': result.x.tolist(),
            'optimal_value': float(objective(result.x)),
            'barrier_value': float(result.fun),
            'method': 'barrier'
        }

    # =========================================================================
    # AUGMENTED LAGRANGIAN METHOD
    # =========================================================================

    def augmented_lagrangian(self, objective: Callable, constraints: List[Dict],
                            lambda0: Optional[np.ndarray], x0: np.ndarray,
                            rho: float = 10.0, max_outer: int = 20,
                            max_inner: int = 100) -> Dict[str, Any]:
        """
        Augmented Lagrangian method (ADMM-style)

        L(x, lambda, rho) = f(x) + lambda^T c(x) + (rho/2) ||c(x)||^2

        Args:
            objective: Objective function f(x)
            constraints: Equality constraints c(x) = 0
            lambda0: Initial Lagrange multipliers
            x0: Initial point
            rho: Penalty parameter
            max_outer: Maximum outer iterations (multiplier updates)
            max_inner: Maximum inner iterations (x minimization)

        Returns:
            Dictionary with optimal point and multipliers
        """
        x = x0.copy()
        n_constraints = len([c for c in constraints if c['type'] == 'eq'])
        lambda_k = lambda0 if lambda0 is not None else np.zeros(n_constraints)

        for outer_iter in range(max_outer):
            # Minimize augmented Lagrangian w.r.t. x
            def aug_lag(x_var):
                """Augmented Lagrangian: f(x) + λ·c(x) + (ρ/2)·c(x)²."""
                obj_val = objective(x_var)
                aug_term = 0.0

                idx = 0
                for constraint in constraints:
                    if constraint['type'] == 'eq':
                        c_val = constraint['fun'](x_var)
                        aug_term += lambda_k[idx] * c_val + (rho / 2) * c_val ** 2
                        idx += 1

                return obj_val + aug_term

            result = scipy_minimize(aug_lag, x, method='BFGS',
                                   options={'maxiter': max_inner})
            x = result.x

            # Update multipliers
            idx = 0
            for constraint in constraints:
                if constraint['type'] == 'eq':
                    c_val = constraint['fun'](x)
                    lambda_k[idx] += rho * c_val
                    idx += 1

            # Check convergence
            constraint_violation = sum(abs(constraint['fun'](x))
                                      for constraint in constraints
                                      if constraint['type'] == 'eq')
            if constraint_violation < 1e-6:
                break

        return {
            'status': 'converged' if outer_iter < max_outer - 1 else 'max_iterations',
            'optimal_x': x.tolist(),
            'optimal_value': float(objective(x)),
            'multipliers': lambda_k.tolist(),
            'outer_iterations': outer_iter + 1,
            'method': 'augmented_lagrangian'
        }

    # =========================================================================
    # KKT CONDITIONS
    # =========================================================================

    def compute_kkt_conditions(self, objective: Callable, constraints: List[Dict],
                              x: np.ndarray, tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Verify KKT (Karush-Kuhn-Tucker) optimality conditions

        KKT conditions for min f(x) s.t. c_i(x) = 0, g_j(x) >= 0:
        1. Stationarity: grad_f + sum(lambda_i grad_c_i) + sum(mu_j grad_g_j) = 0
        2. Primal feasibility: c_i(x) = 0, g_j(x) >= 0
        3. Dual feasibility: mu_j >= 0
        4. Complementarity: mu_j * g_j(x) = 0

        Args:
            objective: Objective function
            constraints: Constraint list
            x: Point to check
            tolerance: Tolerance for checks

        Returns:
            Dictionary with KKT satisfaction status
        """
        grad_f = self._numerical_gradient(objective, x)

        # Check primal feasibility
        eq_violations = []
        ineq_violations = []

        for constraint in constraints:
            c_val = constraint['fun'](x)
            if constraint['type'] == 'eq':
                eq_violations.append(abs(c_val))
            elif constraint['type'] == 'ineq':
                if c_val < -tolerance:
                    ineq_violations.append(abs(c_val))

        primal_feasible = (max(eq_violations, default=0) < tolerance and
                          len(ineq_violations) == 0)

        # Estimate Lagrange multipliers (simplified)
        # Full KKT check would require solving for multipliers
        stationarity_residual = np.linalg.norm(grad_f)

        return {
            'primal_feasible': primal_feasible,
            'stationarity_residual': float(stationarity_residual),
            'eq_constraint_violation': float(max(eq_violations, default=0)),
            'ineq_constraint_violation': float(max(ineq_violations, default=0)),
            'kkt_satisfied': primal_feasible and stationarity_residual < tolerance,
            'tolerance': tolerance
        }

    # =========================================================================
    # LINE SEARCH
    # =========================================================================

    def line_search_backtracking(self, objective: Callable, x: np.ndarray,
                                 direction: np.ndarray, alpha_init: float = 1.0,
                                 c: float = 1e-4, rho: float = 0.5) -> float:
        """
        Backtracking line search (Armijo rule)

        Find alpha s.t. f(x + alpha*d) <= f(x) + c*alpha*grad_f^T d

        Args:
            objective: Objective function
            x: Current point
            direction: Search direction
            alpha_init: Initial step size
            c: Armijo parameter (0 < c < 1)
            rho: Reduction factor (0 < rho < 1)

        Returns:
            Step size alpha
        """
        alpha = alpha_init
        f_x = objective(x)
        grad_f = self._numerical_gradient(objective, x)
        directional_derivative = grad_f @ direction

        max_backtracks = 30
        for _ in range(max_backtracks):
            x_new = x + alpha * direction
            f_new = objective(x_new)

            # Armijo condition
            if f_new <= f_x + c * alpha * directional_derivative:
                return alpha

            alpha *= rho

        return alpha  # Return last alpha even if not satisfied

    # =========================================================================
    # LOCAL OPTIMUM CHECK
    # =========================================================================

    def check_local_optimum(self, objective: Callable, x: np.ndarray,
                           tolerance: float = 1e-6) -> bool:
        """
        Check if x is a local optimum (unconstrained)

        Conditions:
        1. Gradient near zero: ||grad f(x)|| < tolerance
        2. Hessian positive semidefinite (local minimum)

        Args:
            objective: Objective function
            x: Point to check
            tolerance: Tolerance for gradient norm

        Returns:
            True if x appears to be local optimum
        """
        grad = self._numerical_gradient(objective, x)
        grad_norm = np.linalg.norm(grad)

        if grad_norm > tolerance:
            return False

        # Check Hessian positive semidefiniteness
        hess = self._numerical_hessian(objective, x)
        eigenvalues = np.linalg.eigvalsh(hess)

        # All eigenvalues >= -tolerance (allowing numerical error)
        return np.all(eigenvalues >= -tolerance)

    # =========================================================================
    # NUMERICAL DERIVATIVES
    # =========================================================================

    def _numerical_gradient(self, func: Callable, x: np.ndarray,
                           h: float = 1e-7) -> np.ndarray:
        """Compute gradient using central differences"""
        n = len(x)
        grad = np.zeros(n)

        for i in range(n):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += h
            x_minus[i] -= h
            grad[i] = (func(x_plus) - func(x_minus)) / (2 * h)

        return grad

    def _numerical_hessian(self, func: Callable, x: np.ndarray,
                          h: float = 1e-5) -> np.ndarray:
        """Compute Hessian using finite differences"""
        n = len(x)
        hess = np.zeros((n, n))
        f0 = func(x)

        for i in range(n):
            for j in range(i, n):
                x_pp = x.copy()
                x_pm = x.copy()
                x_mp = x.copy()
                x_mm = x.copy()

                x_pp[i] += h
                x_pp[j] += h
                x_pm[i] += h
                x_pm[j] -= h
                x_mp[i] -= h
                x_mp[j] += h
                x_mm[i] -= h
                x_mm[j] -= h

                hess[i, j] = (func(x_pp) - func(x_pm) - func(x_mp) + func(x_mm)) / (4 * h * h)
                hess[j, i] = hess[i, j]

        return hess

    # =========================================================================
    # BDI INTEGRATION
    # =========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for nonconvex optimization tasks"""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['nonconvex'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['trust_region'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['sqp'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception:
            pass

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create optimization plans"""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if already planning
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('problem_type', 'trust_region')

            steps = ['claim_task', 'optimize', 'post_result']
            intention = Intention(
                plan_id=f'nonconvex_{operation}_{task_id}',
                steps=steps,
                target_desire='nonconvex_optimization',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform optimization"""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'optimize':
            result = self.process(task)
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post_result':
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
                result = intention.metadata.get('result', {})

                result_entry = create_entry(
                    content=result,
                    entry_type=EntryType.RESULT,
                    tags=['nonconvex', 'optimization', 'result'],
                    metadata={'source_task': task.entry_id, 'agent': self.agent_id}
                )
                self.blackboard.post_entry(result_entry)
                self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

            intention.mark_completed()

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics"""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'trust_region', 'sqp', 'penalty', 'barrier',
                'augmented_lagrangian', 'kkt_check', 'line_search', 'local_optimum'
            ]
        }
