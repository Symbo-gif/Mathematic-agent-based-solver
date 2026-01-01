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
LINEAR SYSTEMS SPECIALIST (Tier 3)
==================================

Iterative methods for solving linear systems Ax = b.

CAPABILITIES:
------------
- Jacobi iteration
- Gauss-Seidel iteration
- Successive Over-Relaxation (SOR)
- Conjugate Gradient method
- GMRES (Generalized Minimal Residual)
- Preconditioned methods

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

logger = logging.getLogger('symbo_agentic_reasoners.specialists.linear_systems')


@dataclass
class LinearSystemResult:
    """Result of linear system solve."""
    x: List[float]  # Solution vector
    residual: float  # ||Ax - b||
    iterations: int
    converged: bool
    method: str


class LinearSystemsSpecialist(BDIAgent):
    """
    Linear Systems Specialist - Iterative Linear Solvers

    DIRECTIVE:
    ---------
    Provide robust iterative methods for solving large sparse
    linear systems Ax = b.

    OPERATIONS:
    ----------
    - solve: Solve linear system with auto-selected method
    - jacobi: Jacobi iteration
    - gauss_seidel: Gauss-Seidel iteration
    - sor: Successive Over-Relaxation
    - conjugate_gradient: CG for symmetric positive definite
    - gmres: GMRES for general matrices
    """

    def __init__(
        self,
        agent_id: str = "linear_systems_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "linear_systems_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {
            'systems_solved': 0,
            'iterations_total': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="iterative_linear_solver",
                    description="Iterative linear system solvers"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== UTILITY FUNCTIONS ====================

    def _mat_vec_mult(
        self,
        A: List[List[float]],
        x: List[float]
    ) -> List[float]:
        """Matrix-vector multiplication."""
        n = len(x)
        return [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]

    def _vec_dot(self, a: List[float], b: List[float]) -> float:
        """Vector dot product."""
        return sum(ai * bi for ai, bi in zip(a, b))

    def _vec_norm(self, x: List[float]) -> float:
        """Euclidean norm of vector."""
        return math.sqrt(sum(xi ** 2 for xi in x))

    def _vec_sub(self, a: List[float], b: List[float]) -> List[float]:
        """Vector subtraction."""
        return [ai - bi for ai, bi in zip(a, b)]

    def _vec_add(self, a: List[float], b: List[float]) -> List[float]:
        """Vector addition."""
        return [ai + bi for ai, bi in zip(a, b)]

    def _vec_scale(self, a: List[float], s: float) -> List[float]:
        """Scalar multiplication."""
        return [ai * s for ai in a]

    def _compute_residual(
        self,
        A: List[List[float]],
        x: List[float],
        b: List[float]
    ) -> float:
        """Compute residual ||Ax - b||."""
        Ax = self._mat_vec_mult(A, x)
        return self._vec_norm(self._vec_sub(Ax, b))

    # ==================== JACOBI ITERATION ====================

    def jacobi(
        self,
        A: List[List[float]],
        b: List[float],
        x0: Optional[List[float]] = None,
        tolerance: float = 1e-10,
        max_iterations: int = 1000,
    ) -> LinearSystemResult:
        """
        Jacobi iteration for solving Ax = b.

        Args:
            A: Coefficient matrix (must be diagonally dominant)
            b: Right-hand side vector
            x0: Initial guess (zeros if None)
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            LinearSystemResult
        """
        n = len(b)
        x = x0.copy() if x0 else [0.0] * n

        for iteration in range(max_iterations):
            x_new = [0.0] * n

            for i in range(n):
                sigma = sum(A[i][j] * x[j] for j in range(n) if j != i)
                if abs(A[i][i]) < 1e-15:
                    x_new[i] = x[i]
                else:
                    x_new[i] = (b[i] - sigma) / A[i][i]

            # Check convergence
            diff_norm = self._vec_norm(self._vec_sub(x_new, x))
            if diff_norm < tolerance:
                self._stats['systems_solved'] += 1
                self._stats['iterations_total'] += iteration + 1
                return LinearSystemResult(
                    x=x_new,
                    residual=self._compute_residual(A, x_new, b),
                    iterations=iteration + 1,
                    converged=True,
                    method='jacobi'
                )

            x = x_new

        self._stats['systems_solved'] += 1
        self._stats['iterations_total'] += max_iterations
        return LinearSystemResult(
            x=x,
            residual=self._compute_residual(A, x, b),
            iterations=max_iterations,
            converged=False,
            method='jacobi'
        )

    # ==================== GAUSS-SEIDEL ITERATION ====================

    def gauss_seidel(
        self,
        A: List[List[float]],
        b: List[float],
        x0: Optional[List[float]] = None,
        tolerance: float = 1e-10,
        max_iterations: int = 1000,
    ) -> LinearSystemResult:
        """
        Gauss-Seidel iteration for solving Ax = b.

        Uses updated values immediately (faster convergence than Jacobi).

        Args:
            A: Coefficient matrix
            b: Right-hand side vector
            x0: Initial guess
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            LinearSystemResult
        """
        n = len(b)
        x = x0.copy() if x0 else [0.0] * n

        for iteration in range(max_iterations):
            x_old = x.copy()

            for i in range(n):
                sigma = sum(A[i][j] * x[j] for j in range(n) if j != i)
                if abs(A[i][i]) < 1e-15:
                    continue
                x[i] = (b[i] - sigma) / A[i][i]

            # Check convergence
            diff_norm = self._vec_norm(self._vec_sub(x, x_old))
            if diff_norm < tolerance:
                self._stats['systems_solved'] += 1
                self._stats['iterations_total'] += iteration + 1
                return LinearSystemResult(
                    x=x,
                    residual=self._compute_residual(A, x, b),
                    iterations=iteration + 1,
                    converged=True,
                    method='gauss_seidel'
                )

        self._stats['systems_solved'] += 1
        self._stats['iterations_total'] += max_iterations
        return LinearSystemResult(
            x=x,
            residual=self._compute_residual(A, x, b),
            iterations=max_iterations,
            converged=False,
            method='gauss_seidel'
        )

    # ==================== SOR ITERATION ====================

    def sor(
        self,
        A: List[List[float]],
        b: List[float],
        omega: float = 1.5,
        x0: Optional[List[float]] = None,
        tolerance: float = 1e-10,
        max_iterations: int = 1000,
    ) -> LinearSystemResult:
        """
        Successive Over-Relaxation (SOR) for solving Ax = b.

        Args:
            A: Coefficient matrix
            b: Right-hand side vector
            omega: Relaxation parameter (1 < omega < 2 for overrelaxation)
            x0: Initial guess
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            LinearSystemResult
        """
        n = len(b)
        x = x0.copy() if x0 else [0.0] * n

        for iteration in range(max_iterations):
            x_old = x.copy()

            for i in range(n):
                sigma = sum(A[i][j] * x[j] for j in range(n) if j != i)
                if abs(A[i][i]) < 1e-15:
                    continue
                x_gs = (b[i] - sigma) / A[i][i]
                x[i] = (1 - omega) * x_old[i] + omega * x_gs

            # Check convergence
            diff_norm = self._vec_norm(self._vec_sub(x, x_old))
            if diff_norm < tolerance:
                self._stats['systems_solved'] += 1
                self._stats['iterations_total'] += iteration + 1
                return LinearSystemResult(
                    x=x,
                    residual=self._compute_residual(A, x, b),
                    iterations=iteration + 1,
                    converged=True,
                    method=f'sor_omega={omega}'
                )

        self._stats['systems_solved'] += 1
        self._stats['iterations_total'] += max_iterations
        return LinearSystemResult(
            x=x,
            residual=self._compute_residual(A, x, b),
            iterations=max_iterations,
            converged=False,
            method=f'sor_omega={omega}'
        )

    # ==================== CONJUGATE GRADIENT ====================

    def conjugate_gradient(
        self,
        A: List[List[float]],
        b: List[float],
        x0: Optional[List[float]] = None,
        tolerance: float = 1e-10,
        max_iterations: int = 1000,
    ) -> LinearSystemResult:
        """
        Conjugate Gradient method for symmetric positive definite A.

        Args:
            A: SPD coefficient matrix
            b: Right-hand side vector
            x0: Initial guess
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            LinearSystemResult
        """
        n = len(b)
        x = x0.copy() if x0 else [0.0] * n

        # Initial residual r = b - Ax
        Ax = self._mat_vec_mult(A, x)
        r = self._vec_sub(b, Ax)
        p = r.copy()

        rs_old = self._vec_dot(r, r)

        for iteration in range(max_iterations):
            if math.sqrt(rs_old) < tolerance:
                self._stats['systems_solved'] += 1
                self._stats['iterations_total'] += iteration
                return LinearSystemResult(
                    x=x,
                    residual=math.sqrt(rs_old),
                    iterations=iteration,
                    converged=True,
                    method='conjugate_gradient'
                )

            Ap = self._mat_vec_mult(A, p)
            pAp = self._vec_dot(p, Ap)

            if abs(pAp) < 1e-15:
                break

            alpha = rs_old / pAp

            # x = x + alpha * p
            x = self._vec_add(x, self._vec_scale(p, alpha))

            # r = r - alpha * Ap
            r = self._vec_sub(r, self._vec_scale(Ap, alpha))

            rs_new = self._vec_dot(r, r)

            # p = r + beta * p
            beta = rs_new / rs_old
            p = self._vec_add(r, self._vec_scale(p, beta))

            rs_old = rs_new

        self._stats['systems_solved'] += 1
        self._stats['iterations_total'] += max_iterations
        return LinearSystemResult(
            x=x,
            residual=self._compute_residual(A, x, b),
            iterations=max_iterations,
            converged=False,
            method='conjugate_gradient'
        )

    # ==================== GMRES ====================

    def gmres(
        self,
        A: List[List[float]],
        b: List[float],
        x0: Optional[List[float]] = None,
        tolerance: float = 1e-10,
        max_iterations: int = 100,
        restart: int = 30,
    ) -> LinearSystemResult:
        """
        GMRES (Generalized Minimal Residual) for general matrices.

        Args:
            A: Coefficient matrix
            b: Right-hand side vector
            x0: Initial guess
            tolerance: Convergence tolerance
            max_iterations: Maximum outer iterations
            restart: Krylov subspace size before restart

        Returns:
            LinearSystemResult
        """
        n = len(b)
        x = x0.copy() if x0 else [0.0] * n

        total_iterations = 0

        for outer in range(max_iterations):
            # Compute initial residual
            Ax = self._mat_vec_mult(A, x)
            r = self._vec_sub(b, Ax)
            r_norm = self._vec_norm(r)

            if r_norm < tolerance:
                self._stats['systems_solved'] += 1
                self._stats['iterations_total'] += total_iterations
                return LinearSystemResult(
                    x=x,
                    residual=r_norm,
                    iterations=total_iterations,
                    converged=True,
                    method='gmres'
                )

            # Arnoldi iteration
            V = [[0.0] * n for _ in range(restart + 1)]
            H = [[0.0] * restart for _ in range(restart + 1)]

            # v1 = r / ||r||
            V[0] = self._vec_scale(r, 1.0 / r_norm)

            # Givens rotations storage
            cs = [0.0] * restart
            sn = [0.0] * restart
            e1 = [r_norm] + [0.0] * restart

            for j in range(min(restart, n)):
                total_iterations += 1

                # w = A * v_j
                w = self._mat_vec_mult(A, V[j])

                # Gram-Schmidt orthogonalization
                for i in range(j + 1):
                    H[i][j] = self._vec_dot(w, V[i])
                    w = self._vec_sub(w, self._vec_scale(V[i], H[i][j]))

                H[j + 1][j] = self._vec_norm(w)

                if H[j + 1][j] > 1e-15:
                    V[j + 1] = self._vec_scale(w, 1.0 / H[j + 1][j])

                # Apply previous Givens rotations
                for i in range(j):
                    temp = cs[i] * H[i][j] + sn[i] * H[i + 1][j]
                    H[i + 1][j] = -sn[i] * H[i][j] + cs[i] * H[i + 1][j]
                    H[i][j] = temp

                # Compute new Givens rotation
                rho = math.sqrt(H[j][j] ** 2 + H[j + 1][j] ** 2)
                if rho > 1e-15:
                    cs[j] = H[j][j] / rho
                    sn[j] = H[j + 1][j] / rho
                else:
                    cs[j] = 1.0
                    sn[j] = 0.0

                H[j][j] = cs[j] * H[j][j] + sn[j] * H[j + 1][j]
                H[j + 1][j] = 0.0

                e1[j + 1] = -sn[j] * e1[j]
                e1[j] = cs[j] * e1[j]

                res_norm = abs(e1[j + 1])
                if res_norm < tolerance:
                    # Solve upper triangular system
                    y = self._back_substitute(H, e1, j + 1)

                    # Update solution
                    for i in range(j + 1):
                        x = self._vec_add(x, self._vec_scale(V[i], y[i]))

                    self._stats['systems_solved'] += 1
                    self._stats['iterations_total'] += total_iterations
                    return LinearSystemResult(
                        x=x,
                        residual=res_norm,
                        iterations=total_iterations,
                        converged=True,
                        method='gmres'
                    )

            # Solve upper triangular system
            y = self._back_substitute(H, e1, restart)

            # Update solution
            for i in range(restart):
                x = self._vec_add(x, self._vec_scale(V[i], y[i]))

        self._stats['systems_solved'] += 1
        self._stats['iterations_total'] += total_iterations
        return LinearSystemResult(
            x=x,
            residual=self._compute_residual(A, x, b),
            iterations=total_iterations,
            converged=False,
            method='gmres'
        )

    def _back_substitute(
        self,
        H: List[List[float]],
        e: List[float],
        k: int
    ) -> List[float]:
        """Solve upper triangular system Hy = e."""
        y = [0.0] * k
        for i in range(k - 1, -1, -1):
            y[i] = e[i]
            for j in range(i + 1, k):
                y[i] -= H[i][j] * y[j]
            if abs(H[i][i]) > 1e-15:
                y[i] /= H[i][i]
        return y

    # ==================== AUTO-SELECT METHOD ====================

    def solve(
        self,
        A: List[List[float]],
        b: List[float],
        x0: Optional[List[float]] = None,
        method: str = 'auto',
        tolerance: float = 1e-10,
        max_iterations: int = 1000,
    ) -> LinearSystemResult:
        """
        Solve linear system with auto-selected or specified method.

        Args:
            A: Coefficient matrix
            b: Right-hand side vector
            x0: Initial guess
            method: 'auto', 'jacobi', 'gauss_seidel', 'sor', 'cg', 'gmres'
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            LinearSystemResult
        """
        if method == 'jacobi':
            return self.jacobi(A, b, x0, tolerance, max_iterations)
        elif method == 'gauss_seidel':
            return self.gauss_seidel(A, b, x0, tolerance, max_iterations)
        elif method == 'sor':
            return self.sor(A, b, 1.5, x0, tolerance, max_iterations)
        elif method == 'cg' or method == 'conjugate_gradient':
            return self.conjugate_gradient(A, b, x0, tolerance, max_iterations)
        elif method == 'gmres':
            return self.gmres(A, b, x0, tolerance, max_iterations)
        elif method == 'auto':
            # Try CG first (fastest for SPD), fall back to GMRES
            result = self.conjugate_gradient(A, b, x0, tolerance, max_iterations)
            if result.converged:
                return result
            return self.gmres(A, b, x0, tolerance, max_iterations)
        else:
            return self.gauss_seidel(A, b, x0, tolerance, max_iterations)

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'solve':
            result = self.solve(**params)
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
                tags=['linear_system'], status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []
            for entry in entries:
                self.add_belief('pending_linear_system', entry, source='blackboard')

    def deliberate(self) -> List:
        """Generate intentions from beliefs."""
        new_intentions = []
        if self.has_belief('pending_linear_system'):
            task_belief = self.get_belief('pending_linear_system')
            if task_belief:
                intention = Intention(
                    goal="solve_linear_system",
                    plan=["analyze_matrix", "select_method", "solve", "post_results"],
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
        if action in ['analyze_matrix', 'select_method', 'solve']:
            intention.advance()
        elif action == 'post_results':
            intention.complete()


__all__ = [
    'LinearSystemsSpecialist',
    'LinearSystemResult',
]
