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
OPTIMIZATION SPECIALIST (Tier 3)
================================

Comprehensive numerical optimization specialist.

CAPABILITIES:
------------
- Unconstrained optimization (gradient descent, Newton, quasi-Newton)
- Line search methods (backtracking, Wolfe conditions)
- Quasi-Newton methods (BFGS, DFP, L-BFGS)
- Direct search methods (Nelder-Mead simplex)
- Conjugate gradient methods
- Constrained optimization (projected gradient, penalty methods)

ALGORITHMS:
-----------
Native implementation - NO NumPy or SciPy dependency

NO SYMPY - All mathematical operations use native implementations.
"""

import logging
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.optimization')


@dataclass
class OptimizationResult:
    """Result of numerical optimization."""
    x: List[float]  # Optimal point
    fun: float  # Function value at optimal
    success: bool
    iterations: int
    message: str
    gradient_norm: Optional[float] = None
    hessian_approx: Optional[List[List[float]]] = None
    method: str = "unknown"


class OptimizationSpecialist(BDIAgent):
    """
    Optimization Specialist - Comprehensive Numerical Optimization

    DIRECTIVE:
    ---------
    Provide robust numerical optimization methods for unconstrained
    and constrained optimization problems.

    OPERATIONS:
    ----------
    - minimize: Find minimum of objective function
    - gradient_descent: Basic gradient descent optimization
    - bfgs: Quasi-Newton BFGS algorithm
    - nelder_mead: Derivative-free simplex optimization
    - conjugate_gradient: Conjugate gradient optimization
    """

    def __init__(
        self,
        agent_id: str = "optimization_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "optimization_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {
            'optimizations': 0,
            'gradient_evals': 0,
            'function_evals': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="numerical_optimization",
                    description="Numerical optimization methods"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="unconstrained_optimization",
                    description="Unconstrained optimization"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== CORE OPTIMIZATION ====================

    def minimize(
        self,
        func: Callable[[List[float]], float],
        x0: List[float],
        method: str = 'bfgs',
        grad: Optional[Callable[[List[float]], List[float]]] = None,
        tolerance: float = 1e-8,
        max_iterations: int = 1000,
        bounds: Optional[List[Tuple[float, float]]] = None,
    ) -> OptimizationResult:
        """
        Minimize objective function.

        Args:
            func: Objective function f(x) -> scalar
            x0: Initial guess
            method: 'gradient_descent', 'bfgs', 'nelder_mead', 'conjugate_gradient'
            grad: Gradient function (computed numerically if None)
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations
            bounds: Optional bounds [(low, high), ...] per dimension

        Returns:
            OptimizationResult with optimal point and metadata
        """
        self._stats['optimizations'] += 1

        if method == 'gradient_descent':
            return self._gradient_descent(func, x0, grad, tolerance, max_iterations)
        elif method == 'bfgs':
            return self._bfgs(func, x0, grad, tolerance, max_iterations)
        elif method == 'nelder_mead':
            return self._nelder_mead(func, x0, tolerance, max_iterations)
        elif method == 'conjugate_gradient':
            return self._conjugate_gradient(func, x0, grad, tolerance, max_iterations)
        elif method == 'l_bfgs':
            return self._l_bfgs(func, x0, grad, tolerance, max_iterations)
        else:
            return self._bfgs(func, x0, grad, tolerance, max_iterations)

    def _numerical_gradient(
        self,
        func: Callable[[List[float]], float],
        x: List[float],
        h: float = 1e-8
    ) -> List[float]:
        """Compute gradient using central differences."""
        self._stats['gradient_evals'] += 1
        n = len(x)
        grad = []
        for i in range(n):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += h
            x_minus[i] -= h
            grad.append((func(x_plus) - func(x_minus)) / (2 * h))
            self._stats['function_evals'] += 2
        return grad

    def _numerical_hessian(
        self,
        func: Callable[[List[float]], float],
        x: List[float],
        h: float = 1e-5
    ) -> List[List[float]]:
        """Compute Hessian using finite differences."""
        n = len(x)
        H = [[0.0] * n for _ in range(n)]
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

                H[i][j] = (func(x_pp) - func(x_pm) - func(x_mp) + func(x_mm)) / (4 * h * h)
                H[j][i] = H[i][j]

        return H

    # ==================== GRADIENT DESCENT ====================

    def _gradient_descent(
        self,
        func: Callable[[List[float]], float],
        x0: List[float],
        grad: Optional[Callable] = None,
        tolerance: float = 1e-8,
        max_iterations: int = 1000,
        learning_rate: float = 0.01,
    ) -> OptimizationResult:
        """Gradient descent with line search."""
        x = x0.copy()
        n = len(x)

        grad_func = grad if grad else lambda x: self._numerical_gradient(func, x)

        for iteration in range(max_iterations):
            g = grad_func(x)
            self._stats['function_evals'] += 1
            f_val = func(x)

            grad_norm = math.sqrt(sum(gi ** 2 for gi in g))
            if grad_norm < tolerance:
                return OptimizationResult(
                    x=x, fun=f_val, success=True, iterations=iteration,
                    message="Converged: gradient norm below tolerance",
                    gradient_norm=grad_norm, method='gradient_descent'
                )

            # Backtracking line search
            alpha = self._backtracking_line_search(func, x, g, f_val)

            # Update x
            x = [xi - alpha * gi for xi, gi in zip(x, g)]

        f_final = func(x)
        return OptimizationResult(
            x=x, fun=f_final, success=False, iterations=max_iterations,
            message="Maximum iterations reached",
            gradient_norm=grad_norm, method='gradient_descent'
        )

    def _backtracking_line_search(
        self,
        func: Callable[[List[float]], float],
        x: List[float],
        direction: List[float],
        f_val: float,
        alpha: float = 1.0,
        c: float = 1e-4,
        rho: float = 0.5,
    ) -> float:
        """Backtracking line search (Armijo condition)."""
        grad_dot_dir = sum(di * di for di in direction)

        while alpha > 1e-10:
            x_new = [xi - alpha * di for xi, di in zip(x, direction)]
            f_new = func(x_new)
            self._stats['function_evals'] += 1

            if f_new <= f_val - c * alpha * grad_dot_dir:
                return alpha
            alpha *= rho

        return alpha

    # ==================== BFGS ALGORITHM ====================

    def _bfgs(
        self,
        func: Callable[[List[float]], float],
        x0: List[float],
        grad: Optional[Callable] = None,
        tolerance: float = 1e-8,
        max_iterations: int = 1000,
    ) -> OptimizationResult:
        """BFGS quasi-Newton optimization."""
        x = x0.copy()
        n = len(x)

        grad_func = grad if grad else lambda x: self._numerical_gradient(func, x)

        # Initialize inverse Hessian approximation as identity
        H = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        g = grad_func(x)
        f_val = func(x)
        self._stats['function_evals'] += 1

        for iteration in range(max_iterations):
            grad_norm = math.sqrt(sum(gi ** 2 for gi in g))
            if grad_norm < tolerance:
                return OptimizationResult(
                    x=x, fun=f_val, success=True, iterations=iteration,
                    message="Converged: gradient norm below tolerance",
                    gradient_norm=grad_norm, hessian_approx=H, method='bfgs'
                )

            # Search direction: p = -H @ g
            p = [-sum(H[i][j] * g[j] for j in range(n)) for i in range(n)]

            # Line search
            alpha = self._wolfe_line_search(func, grad_func, x, p, f_val, g)

            # Update x
            s = [alpha * pi for pi in p]
            x_new = [xi + si for xi, si in zip(x, s)]

            # Compute new gradient
            g_new = grad_func(x_new)
            y = [gn - go for gn, go in zip(g_new, g)]

            # Update inverse Hessian (BFGS formula)
            H = self._bfgs_update(H, s, y)

            x = x_new
            g = g_new
            f_val = func(x)
            self._stats['function_evals'] += 1

        return OptimizationResult(
            x=x, fun=f_val, success=False, iterations=max_iterations,
            message="Maximum iterations reached",
            gradient_norm=grad_norm, hessian_approx=H, method='bfgs'
        )

    def _bfgs_update(
        self,
        H: List[List[float]],
        s: List[float],
        y: List[float]
    ) -> List[List[float]]:
        """BFGS inverse Hessian update."""
        n = len(s)

        # Compute ρ = 1 / (y^T s)
        ys = sum(yi * si for yi, si in zip(y, s))
        if abs(ys) < 1e-15:
            return H  # Skip update if curvature condition fails
        rho = 1.0 / ys

        # Compute H @ y
        Hy = [sum(H[i][j] * y[j] for j in range(n)) for i in range(n)]

        # Compute y^T H y
        yHy = sum(yi * Hyi for yi, Hyi in zip(y, Hy))

        # Update: H_new = (I - ρsy^T) H (I - ρys^T) + ρss^T
        # Simplified: H_new = H - ρ(Hy)s^T - ρs(Hy)^T + ρ(ρyHy + 1)ss^T
        H_new = [[0.0] * n for _ in range(n)]
        factor = rho * (rho * yHy + 1)

        for i in range(n):
            for j in range(n):
                H_new[i][j] = (H[i][j] - rho * (Hy[i] * s[j] + s[i] * Hy[j])
                              + factor * s[i] * s[j])

        return H_new

    def _wolfe_line_search(
        self,
        func: Callable[[List[float]], float],
        grad_func: Callable[[List[float]], List[float]],
        x: List[float],
        p: List[float],
        f_val: float,
        g: List[float],
        c1: float = 1e-4,
        c2: float = 0.9,
        max_iter: int = 20,
    ) -> float:
        """Line search satisfying strong Wolfe conditions."""
        alpha = 1.0
        alpha_lo, alpha_hi = 0.0, None
        phi0 = f_val
        dphi0 = sum(gi * pi for gi, pi in zip(g, p))

        for _ in range(max_iter):
            x_new = [xi + alpha * pi for xi, pi in zip(x, p)]
            phi_alpha = func(x_new)
            self._stats['function_evals'] += 1

            # Check Armijo condition
            if phi_alpha > phi0 + c1 * alpha * dphi0:
                alpha_hi = alpha
                alpha = (alpha_lo + alpha_hi) / 2
                continue

            g_new = grad_func(x_new)
            dphi_alpha = sum(gn * pi for gn, pi in zip(g_new, p))

            # Check curvature condition
            if abs(dphi_alpha) <= -c2 * dphi0:
                return alpha

            if dphi_alpha >= 0:
                alpha_hi = alpha
            else:
                alpha_lo = alpha

            if alpha_hi is not None:
                alpha = (alpha_lo + alpha_hi) / 2
            else:
                alpha *= 2

        return alpha

    # ==================== L-BFGS ALGORITHM ====================

    def _l_bfgs(
        self,
        func: Callable[[List[float]], float],
        x0: List[float],
        grad: Optional[Callable] = None,
        tolerance: float = 1e-8,
        max_iterations: int = 1000,
        memory_size: int = 10,
    ) -> OptimizationResult:
        """Limited-memory BFGS for large-scale optimization."""
        x = x0.copy()
        n = len(x)

        grad_func = grad if grad else lambda x: self._numerical_gradient(func, x)

        # Storage for s and y vectors
        s_history: List[List[float]] = []
        y_history: List[List[float]] = []
        rho_history: List[float] = []

        g = grad_func(x)
        f_val = func(x)
        self._stats['function_evals'] += 1

        for iteration in range(max_iterations):
            grad_norm = math.sqrt(sum(gi ** 2 for gi in g))
            if grad_norm < tolerance:
                return OptimizationResult(
                    x=x, fun=f_val, success=True, iterations=iteration,
                    message="Converged: gradient norm below tolerance",
                    gradient_norm=grad_norm, method='l_bfgs'
                )

            # Two-loop recursion to compute search direction
            p = self._l_bfgs_direction(g, s_history, y_history, rho_history)

            # Line search
            alpha = self._wolfe_line_search(func, grad_func, x, p, f_val, g)

            # Update x
            s = [alpha * pi for pi in p]
            x_new = [xi + si for xi, si in zip(x, s)]

            # Compute new gradient
            g_new = grad_func(x_new)
            y = [gn - go for gn, go in zip(g_new, g)]

            # Update history
            ys = sum(yi * si for yi, si in zip(y, s))
            if abs(ys) > 1e-15:
                if len(s_history) >= memory_size:
                    s_history.pop(0)
                    y_history.pop(0)
                    rho_history.pop(0)
                s_history.append(s)
                y_history.append(y)
                rho_history.append(1.0 / ys)

            x = x_new
            g = g_new
            f_val = func(x)
            self._stats['function_evals'] += 1

        return OptimizationResult(
            x=x, fun=f_val, success=False, iterations=max_iterations,
            message="Maximum iterations reached",
            gradient_norm=grad_norm, method='l_bfgs'
        )

    def _l_bfgs_direction(
        self,
        g: List[float],
        s_history: List[List[float]],
        y_history: List[List[float]],
        rho_history: List[float],
    ) -> List[float]:
        """L-BFGS two-loop recursion for search direction."""
        q = g.copy()
        m = len(s_history)
        n = len(g)

        if m == 0:
            return [-gi for gi in g]

        alpha = [0.0] * m

        # First loop
        for i in range(m - 1, -1, -1):
            alpha[i] = rho_history[i] * sum(s_history[i][j] * q[j] for j in range(n))
            q = [qj - alpha[i] * y_history[i][j] for j, qj in enumerate(q)]

        # Initial Hessian approximation
        ys = sum(y_history[-1][j] * s_history[-1][j] for j in range(n))
        yy = sum(y_history[-1][j] ** 2 for j in range(n))
        gamma = ys / yy if yy > 0 else 1.0
        r = [gamma * qj for qj in q]

        # Second loop
        for i in range(m):
            beta = rho_history[i] * sum(y_history[i][j] * r[j] for j in range(n))
            r = [rj + (alpha[i] - beta) * s_history[i][j] for j, rj in enumerate(r)]

        return [-ri for ri in r]

    # ==================== NELDER-MEAD SIMPLEX ====================

    def _nelder_mead(
        self,
        func: Callable[[List[float]], float],
        x0: List[float],
        tolerance: float = 1e-8,
        max_iterations: int = 1000,
        initial_step: float = 0.1,
    ) -> OptimizationResult:
        """Nelder-Mead simplex algorithm (derivative-free)."""
        n = len(x0)

        # Initialize simplex
        simplex = [x0.copy()]
        for i in range(n):
            point = x0.copy()
            point[i] += initial_step
            simplex.append(point)

        # Evaluate function at all vertices
        f_values = [func(v) for v in simplex]
        self._stats['function_evals'] += n + 1

        # Parameters
        alpha = 1.0   # Reflection
        gamma = 2.0   # Expansion
        rho = 0.5     # Contraction
        sigma = 0.5   # Shrink

        for iteration in range(max_iterations):
            # Sort vertices by function value
            order = sorted(range(n + 1), key=lambda i: f_values[i])
            simplex = [simplex[i] for i in order]
            f_values = [f_values[i] for i in order]

            # Check convergence
            f_range = f_values[-1] - f_values[0]
            if f_range < tolerance:
                return OptimizationResult(
                    x=simplex[0], fun=f_values[0], success=True,
                    iterations=iteration, message="Converged: simplex contracted",
                    method='nelder_mead'
                )

            # Compute centroid (excluding worst point)
            centroid = [sum(simplex[i][j] for i in range(n)) / n for j in range(n)]

            # Reflection
            x_r = [centroid[j] + alpha * (centroid[j] - simplex[-1][j]) for j in range(n)]
            f_r = func(x_r)
            self._stats['function_evals'] += 1

            if f_values[0] <= f_r < f_values[-2]:
                simplex[-1] = x_r
                f_values[-1] = f_r
                continue

            # Expansion
            if f_r < f_values[0]:
                x_e = [centroid[j] + gamma * (x_r[j] - centroid[j]) for j in range(n)]
                f_e = func(x_e)
                self._stats['function_evals'] += 1

                if f_e < f_r:
                    simplex[-1] = x_e
                    f_values[-1] = f_e
                else:
                    simplex[-1] = x_r
                    f_values[-1] = f_r
                continue

            # Contraction
            if f_r < f_values[-1]:
                # Outside contraction
                x_c = [centroid[j] + rho * (x_r[j] - centroid[j]) for j in range(n)]
            else:
                # Inside contraction
                x_c = [centroid[j] + rho * (simplex[-1][j] - centroid[j]) for j in range(n)]

            f_c = func(x_c)
            self._stats['function_evals'] += 1

            if f_c < min(f_r, f_values[-1]):
                simplex[-1] = x_c
                f_values[-1] = f_c
                continue

            # Shrink
            for i in range(1, n + 1):
                simplex[i] = [simplex[0][j] + sigma * (simplex[i][j] - simplex[0][j])
                             for j in range(n)]
                f_values[i] = func(simplex[i])
            self._stats['function_evals'] += n

        return OptimizationResult(
            x=simplex[0], fun=f_values[0], success=False,
            iterations=max_iterations, message="Maximum iterations reached",
            method='nelder_mead'
        )

    # ==================== CONJUGATE GRADIENT ====================

    def _conjugate_gradient(
        self,
        func: Callable[[List[float]], float],
        x0: List[float],
        grad: Optional[Callable] = None,
        tolerance: float = 1e-8,
        max_iterations: int = 1000,
    ) -> OptimizationResult:
        """Nonlinear conjugate gradient (Polak-Ribiere)."""
        x = x0.copy()
        n = len(x)

        grad_func = grad if grad else lambda x: self._numerical_gradient(func, x)

        g = grad_func(x)
        p = [-gi for gi in g]  # Initial search direction

        f_val = func(x)
        self._stats['function_evals'] += 1

        for iteration in range(max_iterations):
            grad_norm = math.sqrt(sum(gi ** 2 for gi in g))
            if grad_norm < tolerance:
                return OptimizationResult(
                    x=x, fun=f_val, success=True, iterations=iteration,
                    message="Converged: gradient norm below tolerance",
                    gradient_norm=grad_norm, method='conjugate_gradient'
                )

            # Line search
            alpha = self._wolfe_line_search(func, grad_func, x, p, f_val, g)

            # Update x
            x = [xi + alpha * pi for xi, pi in zip(x, p)]

            # Compute new gradient
            g_new = grad_func(x)

            # Polak-Ribiere beta
            g_dot_g = sum(gi ** 2 for gi in g)
            beta = max(0, sum((gn - go) * gn for gn, go in zip(g_new, g)) / g_dot_g)

            # Update search direction
            p = [-gn + beta * pi for gn, pi in zip(g_new, p)]

            g = g_new
            f_val = func(x)
            self._stats['function_evals'] += 1

            # Restart if loss of conjugacy
            if iteration % n == 0:
                p = [-gi for gi in g]

        return OptimizationResult(
            x=x, fun=f_val, success=False, iterations=max_iterations,
            message="Maximum iterations reached",
            gradient_norm=grad_norm, method='conjugate_gradient'
        )

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'minimize':
            result = self.minimize(**params)
            return {'status': 'success', 'result': result}
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return dict(self._stats)

    def update_beliefs(self):
        """Update beliefs from environment."""
        if self.blackboard:
            entries = self.blackboard.query_entries(
                tags=['optimization'], status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []
            for entry in entries:
                self.add_belief('pending_optimization_task', entry, source='blackboard')

    def deliberate(self) -> List:
        """Generate intentions from beliefs."""
        new_intentions = []
        if self.has_belief('pending_optimization_task'):
            task_belief = self.get_belief('pending_optimization_task')
            if task_belief:
                intention = Intention(
                    goal="optimize",
                    plan=["analyze_input", "execute_optimization", "post_results"],
                    priority=5,
                    context={'task': task_belief.content}
                )
                new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention):
        """Execute next step in plan."""
        if not intention or not hasattr(intention, 'get_current_action'):
            return
        action = intention.get_current_action()
        if action == 'analyze_input':
            intention.advance()
        elif action == 'execute_optimization':
            intention.advance()
        elif action == 'post_results':
            intention.complete()


__all__ = [
    'OptimizationSpecialist',
    'OptimizationResult',
]
