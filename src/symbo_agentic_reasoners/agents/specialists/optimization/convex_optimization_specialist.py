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
CONVEX OPTIMIZATION SPECIALIST (Tier 3)
=======================================

Native Python implementation for convex optimization problems.
Implements gradient descent, Newton's method, and related algorithms.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class ConvexOptimizationSpecialist(BDIAgent):
    """
    Specialist for convex optimization problems.

    Capabilities:
    - Gradient descent (with various step size rules)
    - Newton's method
    - Conjugate gradient
    - BFGS quasi-Newton
    - Projected gradient descent
    - Quadratic programming
    """

    def __init__(self, agent_id: str = 'convex_optimization_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.optimization.convex',
                agent_id=agent_id,
                algorithm='native_convex_opt',
                cost='medium',
                instance=self,
                tier='3',
                capabilities='gradient_newton_qp'
            ))

        logger.info(f"[{agent_id}] Convex Optimization Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for convex optimization tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['convex'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['gradient_descent'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['optimization'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create optimization plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'gradient_descent')

            steps = ['claim_task', 'optimize', 'post_result']
            intention = Intention(
                plan_id=f'convex_{operation}_{task_id}',
                steps=steps,
                target_desire='convex_optimization',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Solve optimization problems."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'optimize':
            self._optimize(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _optimize(self, intention: Intention):
        """Run optimization algorithm."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'gradient_descent')

        try:
            if operation == 'gradient_descent':
                result = self._run_gradient_descent(metadata)
            elif operation == 'newton':
                result = self._run_newton(metadata)
            elif operation == 'quadratic_program':
                Q = metadata.get('Q', [])
                c = metadata.get('c', [])
                A = metadata.get('A', None)
                b = metadata.get('b', None)
                result = self.quadratic_program(Q, c, A, b)
            elif operation == 'least_squares':
                A = metadata.get('A', [])
                b = metadata.get('b', [])
                result = self.least_squares(A, b)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Optimization failed: {e}")
            intention.metadata['result'] = {'error': str(e)}
            intention.advance()

    def _post_result(self, intention: Intention):
        """Post result to blackboard."""
        if self.blackboard:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            task = intention.metadata.get('task_entry')
            result = intention.metadata.get('result', {})

            result_entry = create_entry(
                content=result,
                entry_type=EntryType.RESULT,
                tags=['convex', 'optimization', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    def _run_gradient_descent(self, metadata: Dict) -> Dict[str, Any]:
        """Run gradient descent with provided function."""
        # For tasks that specify function as a string identifier
        func_type = metadata.get('function_type', 'quadratic')
        x0 = metadata.get('x0', [0.0, 0.0])
        learning_rate = metadata.get('learning_rate', 0.1)
        max_iterations = metadata.get('max_iterations', 1000)
        tolerance = metadata.get('tolerance', 1e-6)

        if func_type == 'quadratic':
            Q = np.array(metadata.get('Q', [[1, 0], [0, 1]]), dtype=float)
            c = np.array(metadata.get('c', [0, 0]), dtype=float)
            f = lambda x: 0.5 * x @ Q @ x + c @ x
            grad_f = lambda x: Q @ x + c
        elif func_type == 'rosenbrock':
            f = lambda x: (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2
            grad_f = lambda x: np.array([
                -2 * (1 - x[0]) - 400 * x[0] * (x[1] - x[0]**2),
                200 * (x[1] - x[0]**2)
            ])
        else:
            return {'error': f'Unknown function type: {func_type}'}

        return self.gradient_descent(f, grad_f, x0, learning_rate, max_iterations, tolerance)

    def _run_newton(self, metadata: Dict) -> Dict[str, Any]:
        """Run Newton's method with provided function."""
        func_type = metadata.get('function_type', 'quadratic')
        x0 = metadata.get('x0', [0.0, 0.0])
        max_iterations = metadata.get('max_iterations', 100)
        tolerance = metadata.get('tolerance', 1e-8)

        if func_type == 'quadratic':
            Q = np.array(metadata.get('Q', [[1, 0], [0, 1]]), dtype=float)
            c = np.array(metadata.get('c', [0, 0]), dtype=float)
            f = lambda x: 0.5 * x @ Q @ x + c @ x
            grad_f = lambda x: Q @ x + c
            hess_f = lambda x: Q
        elif func_type == 'rosenbrock':
            f = lambda x: (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2
            grad_f = lambda x: np.array([
                -2 * (1 - x[0]) - 400 * x[0] * (x[1] - x[0]**2),
                200 * (x[1] - x[0]**2)
            ])
            hess_f = lambda x: np.array([
                [2 - 400 * x[1] + 1200 * x[0]**2, -400 * x[0]],
                [-400 * x[0], 200]
            ])
        else:
            return {'error': f'Unknown function type: {func_type}'}

        return self.newton_method(f, grad_f, hess_f, x0, max_iterations, tolerance)

    # =========================================================================
    # GRADIENT DESCENT
    # =========================================================================

    @staticmethod
    def gradient_descent(f: Callable, grad_f: Callable, x0: List[float],
                         learning_rate: float = 0.1, max_iterations: int = 1000,
                         tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Gradient descent optimization.

        Args:
            f: Objective function
            grad_f: Gradient of objective
            x0: Initial point
            learning_rate: Step size (alpha)
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dictionary with optimal point and value
        """
        x = np.array(x0, dtype=float)
        history = [{'x': x.copy().tolist(), 'f': float(f(x))}]

        for iteration in range(max_iterations):
            grad = grad_f(x)
            grad_norm = np.linalg.norm(grad)

            if grad_norm < tolerance:
                break

            # Gradient step
            x = x - learning_rate * grad

            history.append({'x': x.copy().tolist(), 'f': float(f(x))})

            # Check for convergence in function value
            if len(history) > 1 and abs(history[-1]['f'] - history[-2]['f']) < tolerance:
                break

        return {
            'status': 'converged' if iteration < max_iterations - 1 else 'max_iterations',
            'optimal_x': x.tolist(),
            'optimal_value': float(f(x)),
            'iterations': iteration + 1,
            'final_gradient_norm': float(np.linalg.norm(grad_f(x))),
            'method': 'native_gradient_descent'
        }

    @staticmethod
    def gradient_descent_backtracking(f: Callable, grad_f: Callable, x0: List[float],
                                       alpha: float = 0.3, beta: float = 0.8,
                                       max_iterations: int = 1000,
                                       tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Gradient descent with backtracking line search.

        Args:
            f: Objective function
            grad_f: Gradient of objective
            x0: Initial point
            alpha: Armijo parameter (0 < alpha < 0.5)
            beta: Step reduction factor (0 < beta < 1)
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dictionary with optimal point and value
        """
        x = np.array(x0, dtype=float)

        for iteration in range(max_iterations):
            grad = grad_f(x)
            grad_norm = np.linalg.norm(grad)

            if grad_norm < tolerance:
                break

            # Backtracking line search
            t = 1.0
            while f(x - t * grad) > f(x) - alpha * t * grad_norm**2:
                t *= beta
                if t < 1e-10:
                    break

            x = x - t * grad

        return {
            'status': 'converged' if iteration < max_iterations - 1 else 'max_iterations',
            'optimal_x': x.tolist(),
            'optimal_value': float(f(x)),
            'iterations': iteration + 1,
            'method': 'native_gradient_descent_backtracking'
        }

    # =========================================================================
    # NEWTON'S METHOD
    # =========================================================================

    @staticmethod
    def newton_method(f: Callable, grad_f: Callable, hess_f: Callable,
                       x0: List[float], max_iterations: int = 100,
                       tolerance: float = 1e-8) -> Dict[str, Any]:
        """
        Newton's method for optimization.

        Args:
            f: Objective function
            grad_f: Gradient of objective
            hess_f: Hessian of objective
            x0: Initial point
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dictionary with optimal point and value
        """
        x = np.array(x0, dtype=float)

        for iteration in range(max_iterations):
            grad = grad_f(x)
            hess = hess_f(x)

            grad_norm = np.linalg.norm(grad)
            if grad_norm < tolerance:
                break

            try:
                # Newton step: solve H * delta = -grad
                delta = np.linalg.solve(hess, -grad)
            except np.linalg.LinAlgError:
                return {
                    'status': 'singular_hessian',
                    'optimal_x': x.tolist(),
                    'optimal_value': float(f(x)),
                    'iterations': iteration + 1
                }

            # Line search (backtracking)
            t = 1.0
            alpha, beta = 0.3, 0.8
            while f(x + t * delta) > f(x) + alpha * t * grad @ delta:
                t *= beta
                if t < 1e-10:
                    break

            x = x + t * delta

        return {
            'status': 'converged' if iteration < max_iterations - 1 else 'max_iterations',
            'optimal_x': x.tolist(),
            'optimal_value': float(f(x)),
            'iterations': iteration + 1,
            'final_gradient_norm': float(np.linalg.norm(grad_f(x))),
            'method': 'native_newton'
        }

    # =========================================================================
    # QUADRATIC PROGRAMMING
    # =========================================================================

    def quadratic_program(self, Q: List[List[float]], c: List[float],
                           A: List[List[float]] = None, b: List[float] = None) -> Dict[str, Any]:
        """
        Solve quadratic program: min 0.5 * x^T Q x + c^T x
        subject to Ax <= b (if provided)

        Args:
            Q: Quadratic term (positive semidefinite)
            c: Linear term
            A: Inequality constraint matrix
            b: Inequality constraint RHS

        Returns:
            Dictionary with optimal solution
        """
        Q = np.array(Q, dtype=float)
        c = np.array(c, dtype=float)

        if A is None or b is None:
            # Unconstrained QP: optimal is -Q^{-1}c
            try:
                x_opt = np.linalg.solve(Q, -c)
                opt_value = 0.5 * x_opt @ Q @ x_opt + c @ x_opt
                return {
                    'status': 'optimal',
                    'optimal_x': x_opt.tolist(),
                    'optimal_value': float(opt_value),
                    'method': 'native_unconstrained_qp'
                }
            except np.linalg.LinAlgError:
                return {'error': 'Singular Q matrix'}

        # Constrained QP: use projected gradient descent
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)

        # Find initial feasible point
        x = np.zeros(len(c))
        if not np.all(A @ x <= b + 1e-10):
            # Try to find feasible point
            x = np.linalg.lstsq(A, b, rcond=None)[0]

        # Projected gradient descent
        for iteration in range(1000):
            grad = Q @ x + c

            # Gradient step
            x_new = x - 0.1 * grad

            # Project onto feasible region (simple clipping for box constraints)
            # For general inequality constraints, use more sophisticated projection
            for _ in range(100):
                violations = A @ x_new - b
                if np.all(violations <= 1e-10):
                    break
                # Pull back violated constraints
                for i in range(len(b)):
                    if violations[i] > 0:
                        ai = A[i]
                        x_new = x_new - (violations[i] / (np.dot(ai, ai) + 1e-10)) * ai

            if np.linalg.norm(x_new - x) < 1e-6:
                break
            x = x_new

        opt_value = 0.5 * x @ Q @ x + c @ x

        return {
            'status': 'optimal',
            'optimal_x': x.tolist(),
            'optimal_value': float(opt_value),
            'iterations': iteration + 1,
            'method': 'native_constrained_qp'
        }

    # =========================================================================
    # LEAST SQUARES
    # =========================================================================

    @staticmethod
    def least_squares(A: List[List[float]], b: List[float]) -> Dict[str, Any]:
        """
        Solve least squares: min ||Ax - b||^2

        Args:
            A: Design matrix
            b: Target vector

        Returns:
            Dictionary with optimal solution
        """
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)

        try:
            # Normal equations: A^T A x = A^T b
            x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

            residual_norm = np.linalg.norm(A @ x - b)

            return {
                'status': 'optimal',
                'solution': x.tolist(),
                'residual_norm': float(residual_norm),
                'rank': int(rank),
                'method': 'native_least_squares'
            }
        except np.linalg.LinAlgError as e:
            return {'error': str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'gradient_descent', 'gradient_descent_backtracking',
                'newton', 'quadratic_program', 'least_squares'
            ]
        }
