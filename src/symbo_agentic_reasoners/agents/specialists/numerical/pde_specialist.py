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
PDE SPECIALIST (Tier 3)
=======================

Numerical methods for partial differential equations.

CAPABILITIES:
------------
- Heat equation (diffusion) - explicit/implicit
- Wave equation
- Laplace/Poisson equation
- Advection equation
- Finite difference methods
- Stability analysis

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

logger = logging.getLogger('symbo_agentic_reasoners.specialists.pde')


@dataclass
class PDESolution:
    """Solution of PDE."""
    u: List[List[float]]  # Solution grid u[time_step][space_point]
    x: List[float]  # Spatial grid
    t: List[float]  # Time grid
    method: str
    stable: bool
    pde_type: str


class PDESpecialist(BDIAgent):
    """
    PDE Specialist - Partial Differential Equations

    DIRECTIVE:
    ---------
    Provide numerical methods for solving common PDEs using
    finite difference methods.

    OPERATIONS:
    ----------
    - solve_heat: Solve heat/diffusion equation
    - solve_wave: Solve wave equation
    - solve_laplace: Solve Laplace equation (2D)
    - solve_poisson: Solve Poisson equation (2D)
    - solve_advection: Solve advection equation
    """

    def __init__(
        self,
        agent_id: str = "pde_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "pde_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {
            'pdes_solved': 0,
            'grid_points': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="pde_solver",
                    description="Partial differential equation solver"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== HEAT EQUATION ====================

    def solve_heat(
        self,
        initial_condition: Callable[[float], float],
        x_range: Tuple[float, float],
        t_range: Tuple[float, float],
        nx: int = 50,
        nt: int = 100,
        alpha: float = 1.0,
        method: str = 'explicit',
        boundary_left: float = 0.0,
        boundary_right: float = 0.0,
    ) -> PDESolution:
        """
        Solve the 1D heat equation: u_t = alpha * u_xx

        Args:
            initial_condition: u(x, 0) = f(x)
            x_range: (x_min, x_max)
            t_range: (t_start, t_end)
            nx: Number of spatial points
            nt: Number of time steps
            alpha: Thermal diffusivity
            method: 'explicit' (FTCS) or 'implicit' (Crank-Nicolson)
            boundary_left: u(x_min, t) = constant
            boundary_right: u(x_max, t) = constant

        Returns:
            PDESolution with solution grid
        """
        self._stats['pdes_solved'] += 1

        x_min, x_max = x_range
        t_start, t_end = t_range

        dx = (x_max - x_min) / (nx - 1)
        dt = (t_end - t_start) / (nt - 1)

        x = [x_min + i * dx for i in range(nx)]
        t = [t_start + n * dt for n in range(nt)]

        # Stability parameter
        r = alpha * dt / (dx ** 2)

        # Check stability for explicit method
        stable = True
        if method == 'explicit' and r > 0.5:
            logger.warning(f"Heat equation explicit method unstable: r = {r} > 0.5")
            stable = False

        # Initialize solution grid
        u = [[0.0] * nx for _ in range(nt)]

        # Set initial condition
        for i in range(nx):
            u[0][i] = initial_condition(x[i])

        # Apply boundary conditions
        for n in range(nt):
            u[n][0] = boundary_left
            u[n][-1] = boundary_right

        if method == 'explicit':
            self._heat_explicit(u, r, nx, nt)
        elif method == 'implicit' or method == 'crank_nicolson':
            self._heat_crank_nicolson(u, r, nx, nt)
        else:
            self._heat_explicit(u, r, nx, nt)

        self._stats['grid_points'] += nx * nt

        return PDESolution(
            u=u, x=x, t=t, method=f'heat_{method}',
            stable=stable, pde_type='heat'
        )

    def _heat_explicit(
        self,
        u: List[List[float]],
        r: float,
        nx: int,
        nt: int
    ):
        """Forward-Time Central-Space (FTCS) explicit scheme."""
        for n in range(nt - 1):
            for i in range(1, nx - 1):
                u[n + 1][i] = u[n][i] + r * (u[n][i + 1] - 2 * u[n][i] + u[n][i - 1])

    def _heat_crank_nicolson(
        self,
        u: List[List[float]],
        r: float,
        nx: int,
        nt: int
    ):
        """Crank-Nicolson implicit scheme (unconditionally stable)."""
        # Build tridiagonal system coefficients
        r_half = r / 2

        for n in range(nt - 1):
            # Set up tridiagonal system
            a = [-r_half] * nx
            b = [1 + r] * nx
            c = [-r_half] * nx
            d = [0.0] * nx

            # RHS from previous time step
            for i in range(1, nx - 1):
                d[i] = r_half * u[n][i - 1] + (1 - r) * u[n][i] + r_half * u[n][i + 1]

            # Boundary conditions
            b[0] = 1
            c[0] = 0
            d[0] = u[n + 1][0]

            a[nx - 1] = 0
            b[nx - 1] = 1
            d[nx - 1] = u[n + 1][nx - 1]

            # Solve using Thomas algorithm
            solution = self._thomas_algorithm(a, b, c, d)
            for i in range(nx):
                u[n + 1][i] = solution[i]

    def _thomas_algorithm(
        self,
        a: List[float],
        b: List[float],
        c: List[float],
        d: List[float]
    ) -> List[float]:
        """Thomas algorithm for tridiagonal systems."""
        n = len(d)
        c_prime = [0.0] * n
        d_prime = [0.0] * n
        x = [0.0] * n

        c_prime[0] = c[0] / b[0] if abs(b[0]) > 1e-15 else 0
        d_prime[0] = d[0] / b[0] if abs(b[0]) > 1e-15 else 0

        for i in range(1, n):
            denom = b[i] - a[i] * c_prime[i - 1]
            if abs(denom) < 1e-15:
                denom = 1e-15
            c_prime[i] = c[i] / denom if i < n - 1 else 0
            d_prime[i] = (d[i] - a[i] * d_prime[i - 1]) / denom

        x[n - 1] = d_prime[n - 1]
        for i in range(n - 2, -1, -1):
            x[i] = d_prime[i] - c_prime[i] * x[i + 1]

        return x

    # ==================== WAVE EQUATION ====================

    def solve_wave(
        self,
        initial_position: Callable[[float], float],
        initial_velocity: Callable[[float], float],
        x_range: Tuple[float, float],
        t_range: Tuple[float, float],
        nx: int = 50,
        nt: int = 100,
        c: float = 1.0,
        boundary_left: float = 0.0,
        boundary_right: float = 0.0,
    ) -> PDESolution:
        """
        Solve the 1D wave equation: u_tt = c^2 * u_xx

        Args:
            initial_position: u(x, 0)
            initial_velocity: u_t(x, 0)
            x_range: (x_min, x_max)
            t_range: (t_start, t_end)
            nx: Number of spatial points
            nt: Number of time steps
            c: Wave speed
            boundary_left: u(x_min, t) = constant
            boundary_right: u(x_max, t) = constant

        Returns:
            PDESolution with solution grid
        """
        self._stats['pdes_solved'] += 1

        x_min, x_max = x_range
        t_start, t_end = t_range

        dx = (x_max - x_min) / (nx - 1)
        dt = (t_end - t_start) / (nt - 1)

        x = [x_min + i * dx for i in range(nx)]
        t = [t_start + n * dt for n in range(nt)]

        # CFL condition
        r = (c * dt / dx) ** 2

        stable = r <= 1.0
        if not stable:
            logger.warning(f"Wave equation unstable: Courant number = {math.sqrt(r)} > 1")

        # Initialize solution grid
        u = [[0.0] * nx for _ in range(nt)]

        # Set initial position
        for i in range(nx):
            u[0][i] = initial_position(x[i])

        # Apply boundary conditions
        for n in range(nt):
            u[n][0] = boundary_left
            u[n][-1] = boundary_right

        # First time step using initial velocity
        for i in range(1, nx - 1):
            u[1][i] = (u[0][i] + dt * initial_velocity(x[i]) +
                       0.5 * r * (u[0][i + 1] - 2 * u[0][i] + u[0][i - 1]))

        # Subsequent time steps
        for n in range(1, nt - 1):
            for i in range(1, nx - 1):
                u[n + 1][i] = (2 * u[n][i] - u[n - 1][i] +
                              r * (u[n][i + 1] - 2 * u[n][i] + u[n][i - 1]))

        self._stats['grid_points'] += nx * nt

        return PDESolution(
            u=u, x=x, t=t, method='wave_explicit',
            stable=stable, pde_type='wave'
        )

    # ==================== LAPLACE EQUATION ====================

    def solve_laplace(
        self,
        x_range: Tuple[float, float],
        y_range: Tuple[float, float],
        nx: int = 30,
        ny: int = 30,
        boundary_conditions: Dict[str, Union[float, Callable[[float], float]]] = None,
        tolerance: float = 1e-6,
        max_iterations: int = 10000,
    ) -> Dict[str, Any]:
        """
        Solve 2D Laplace equation: u_xx + u_yy = 0

        Args:
            x_range: (x_min, x_max)
            y_range: (y_min, y_max)
            nx: Grid points in x
            ny: Grid points in y
            boundary_conditions: Dict with 'left', 'right', 'top', 'bottom'
            tolerance: Convergence tolerance
            max_iterations: Maximum Jacobi iterations

        Returns:
            Dict with solution grid, x, y arrays
        """
        self._stats['pdes_solved'] += 1

        if boundary_conditions is None:
            boundary_conditions = {
                'left': 0.0, 'right': 0.0, 'top': 100.0, 'bottom': 0.0
            }

        x_min, x_max = x_range
        y_min, y_max = y_range

        dx = (x_max - x_min) / (nx - 1)
        dy = (y_max - y_min) / (ny - 1)

        x = [x_min + i * dx for i in range(nx)]
        y = [y_min + j * dy for j in range(ny)]

        # Initialize solution grid
        u = [[0.0] * ny for _ in range(nx)]

        # Apply boundary conditions
        for i in range(nx):
            bc_bottom = boundary_conditions.get('bottom', 0.0)
            bc_top = boundary_conditions.get('top', 0.0)
            u[i][0] = bc_bottom(x[i]) if callable(bc_bottom) else bc_bottom
            u[i][ny - 1] = bc_top(x[i]) if callable(bc_top) else bc_top

        for j in range(ny):
            bc_left = boundary_conditions.get('left', 0.0)
            bc_right = boundary_conditions.get('right', 0.0)
            u[0][j] = bc_left(y[j]) if callable(bc_left) else bc_left
            u[nx - 1][j] = bc_right(y[j]) if callable(bc_right) else bc_right

        # Gauss-Seidel iteration
        converged = False
        for iteration in range(max_iterations):
            max_change = 0.0

            for i in range(1, nx - 1):
                for j in range(1, ny - 1):
                    u_old = u[i][j]
                    u[i][j] = 0.25 * (u[i + 1][j] + u[i - 1][j] +
                                       u[i][j + 1] + u[i][j - 1])
                    max_change = max(max_change, abs(u[i][j] - u_old))

            if max_change < tolerance:
                converged = True
                break

        self._stats['grid_points'] += nx * ny

        return {
            'u': u,
            'x': x,
            'y': y,
            'converged': converged,
            'iterations': iteration + 1,
            'method': 'laplace_gauss_seidel'
        }

    # ==================== POISSON EQUATION ====================

    def solve_poisson(
        self,
        source: Callable[[float, float], float],
        x_range: Tuple[float, float],
        y_range: Tuple[float, float],
        nx: int = 30,
        ny: int = 30,
        boundary_conditions: Dict[str, float] = None,
        tolerance: float = 1e-6,
        max_iterations: int = 10000,
    ) -> Dict[str, Any]:
        """
        Solve 2D Poisson equation: u_xx + u_yy = f(x,y)

        Args:
            source: Source function f(x, y)
            x_range: (x_min, x_max)
            y_range: (y_min, y_max)
            nx: Grid points in x
            ny: Grid points in y
            boundary_conditions: Dict with 'left', 'right', 'top', 'bottom'
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            Dict with solution grid, x, y arrays
        """
        self._stats['pdes_solved'] += 1

        if boundary_conditions is None:
            boundary_conditions = {
                'left': 0.0, 'right': 0.0, 'top': 0.0, 'bottom': 0.0
            }

        x_min, x_max = x_range
        y_min, y_max = y_range

        dx = (x_max - x_min) / (nx - 1)
        dy = (y_max - y_min) / (ny - 1)

        x = [x_min + i * dx for i in range(nx)]
        y = [y_min + j * dy for j in range(ny)]

        # Precompute source term
        f = [[source(x[i], y[j]) for j in range(ny)] for i in range(nx)]

        # Initialize solution grid
        u = [[0.0] * ny for _ in range(nx)]

        # Apply boundary conditions
        for i in range(nx):
            u[i][0] = boundary_conditions.get('bottom', 0.0)
            u[i][ny - 1] = boundary_conditions.get('top', 0.0)

        for j in range(ny):
            u[0][j] = boundary_conditions.get('left', 0.0)
            u[nx - 1][j] = boundary_conditions.get('right', 0.0)

        # Gauss-Seidel with source term
        h2 = dx * dy
        converged = False

        for iteration in range(max_iterations):
            max_change = 0.0

            for i in range(1, nx - 1):
                for j in range(1, ny - 1):
                    u_old = u[i][j]
                    u[i][j] = 0.25 * (u[i + 1][j] + u[i - 1][j] +
                                       u[i][j + 1] + u[i][j - 1] - h2 * f[i][j])
                    max_change = max(max_change, abs(u[i][j] - u_old))

            if max_change < tolerance:
                converged = True
                break

        self._stats['grid_points'] += nx * ny

        return {
            'u': u,
            'x': x,
            'y': y,
            'converged': converged,
            'iterations': iteration + 1,
            'method': 'poisson_gauss_seidel'
        }

    # ==================== ADVECTION EQUATION ====================

    def solve_advection(
        self,
        initial_condition: Callable[[float], float],
        x_range: Tuple[float, float],
        t_range: Tuple[float, float],
        nx: int = 100,
        nt: int = 100,
        velocity: float = 1.0,
        method: str = 'upwind',
    ) -> PDESolution:
        """
        Solve the 1D advection equation: u_t + v * u_x = 0

        Args:
            initial_condition: u(x, 0)
            x_range: (x_min, x_max)
            t_range: (t_start, t_end)
            nx: Number of spatial points
            nt: Number of time steps
            velocity: Advection velocity
            method: 'upwind', 'lax_wendroff', 'lax_friedrichs'

        Returns:
            PDESolution with solution grid
        """
        self._stats['pdes_solved'] += 1

        x_min, x_max = x_range
        t_start, t_end = t_range

        dx = (x_max - x_min) / (nx - 1)
        dt = (t_end - t_start) / (nt - 1)

        x = [x_min + i * dx for i in range(nx)]
        t = [t_start + n * dt for n in range(nt)]

        # CFL number
        c = velocity * dt / dx
        stable = abs(c) <= 1.0

        if not stable:
            logger.warning(f"Advection equation unstable: |CFL| = {abs(c)} > 1")

        # Initialize solution
        u = [[0.0] * nx for _ in range(nt)]

        for i in range(nx):
            u[0][i] = initial_condition(x[i])

        if method == 'upwind':
            self._advection_upwind(u, c, nx, nt, velocity)
        elif method == 'lax_wendroff':
            self._advection_lax_wendroff(u, c, nx, nt)
        elif method == 'lax_friedrichs':
            self._advection_lax_friedrichs(u, c, nx, nt)
        else:
            self._advection_upwind(u, c, nx, nt, velocity)

        self._stats['grid_points'] += nx * nt

        return PDESolution(
            u=u, x=x, t=t, method=f'advection_{method}',
            stable=stable, pde_type='advection'
        )

    def _advection_upwind(
        self,
        u: List[List[float]],
        c: float,
        nx: int,
        nt: int,
        velocity: float
    ):
        """First-order upwind scheme."""
        for n in range(nt - 1):
            for i in range(1, nx - 1):
                if velocity > 0:
                    u[n + 1][i] = u[n][i] - c * (u[n][i] - u[n][i - 1])
                else:
                    u[n + 1][i] = u[n][i] - c * (u[n][i + 1] - u[n][i])
            # Periodic boundary
            u[n + 1][0] = u[n + 1][nx - 2]
            u[n + 1][nx - 1] = u[n + 1][1]

    def _advection_lax_wendroff(
        self,
        u: List[List[float]],
        c: float,
        nx: int,
        nt: int
    ):
        """Second-order Lax-Wendroff scheme."""
        for n in range(nt - 1):
            for i in range(1, nx - 1):
                u[n + 1][i] = (u[n][i] - 0.5 * c * (u[n][i + 1] - u[n][i - 1]) +
                              0.5 * c ** 2 * (u[n][i + 1] - 2 * u[n][i] + u[n][i - 1]))
            # Periodic boundary
            u[n + 1][0] = u[n + 1][nx - 2]
            u[n + 1][nx - 1] = u[n + 1][1]

    def _advection_lax_friedrichs(
        self,
        u: List[List[float]],
        c: float,
        nx: int,
        nt: int
    ):
        """Lax-Friedrichs scheme (diffusive)."""
        for n in range(nt - 1):
            for i in range(1, nx - 1):
                u[n + 1][i] = (0.5 * (u[n][i + 1] + u[n][i - 1]) -
                              0.5 * c * (u[n][i + 1] - u[n][i - 1]))
            # Periodic boundary
            u[n + 1][0] = u[n + 1][nx - 2]
            u[n + 1][nx - 1] = u[n + 1][1]

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'solve_heat':
            result = self.solve_heat(**params)
            return {'status': 'success', 'result': result}
        elif action == 'solve_wave':
            result = self.solve_wave(**params)
            return {'status': 'success', 'result': result}
        elif action == 'solve_laplace':
            result = self.solve_laplace(**params)
            return {'status': 'success', 'result': result}
        elif action == 'solve_poisson':
            result = self.solve_poisson(**params)
            return {'status': 'success', 'result': result}
        elif action == 'solve_advection':
            result = self.solve_advection(**params)
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
                tags=['pde'], status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []
            for entry in entries:
                self.add_belief('pending_pde', entry, source='blackboard')

    def deliberate(self) -> List:
        """Generate intentions from beliefs."""
        new_intentions = []
        if self.has_belief('pending_pde'):
            task_belief = self.get_belief('pending_pde')
            if task_belief:
                intention = Intention(
                    goal="solve_pde",
                    plan=["classify_pde", "setup_grid", "solve", "post_results"],
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
        if action in ['classify_pde', 'setup_grid', 'solve']:
            intention.advance()
        elif action == 'post_results':
            intention.complete()


__all__ = [
    'PDESpecialist',
    'PDESolution',
]
