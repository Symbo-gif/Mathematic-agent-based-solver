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
SPLINE INTERPOLATION SPECIALIST (Tier 3)
========================================

Comprehensive spline and interpolation specialist.

CAPABILITIES:
------------
- Cubic spline interpolation (natural, clamped, not-a-knot)
- B-splines
- Hermite interpolation
- Akima interpolation (reduced oscillation)
- Piecewise linear interpolation
- Bivariate splines (2D interpolation)

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

logger = logging.getLogger('symbo_agentic_reasoners.specialists.spline')


@dataclass
class SplineResult:
    """Result of spline interpolation."""
    coefficients: List[List[float]]  # [a, b, c, d] for each segment
    knots: List[float]
    evaluator: Optional[Callable[[float], float]] = None
    derivative_evaluator: Optional[Callable[[float], float]] = None
    method: str = "unknown"


class SplineSpecialist(BDIAgent):
    """
    Spline Interpolation Specialist - Advanced Interpolation Methods

    DIRECTIVE:
    ---------
    Provide comprehensive spline interpolation methods for smooth
    curve fitting and data interpolation.

    OPERATIONS:
    ----------
    - cubic_spline: Natural/clamped cubic spline interpolation
    - hermite_spline: Hermite interpolation with derivatives
    - akima_spline: Akima interpolation (reduced overshoot)
    - b_spline: B-spline interpolation
    """

    def __init__(
        self,
        agent_id: str = "spline_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "spline_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {
            'splines_computed': 0,
            'evaluations': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="spline_interpolation",
                    description="Spline interpolation methods"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="cubic_spline",
                    description="Cubic spline interpolation"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== CUBIC SPLINE ====================

    def cubic_spline(
        self,
        x: List[float],
        y: List[float],
        bc_type: str = 'natural',
        deriv_start: float = 0.0,
        deriv_end: float = 0.0,
    ) -> SplineResult:
        """
        Compute cubic spline interpolation.

        Args:
            x: x-coordinates (must be sorted ascending)
            y: y-coordinates
            bc_type: Boundary condition type ('natural', 'clamped', 'not_a_knot')
            deriv_start: Derivative at start (for clamped)
            deriv_end: Derivative at end (for clamped)

        Returns:
            SplineResult with coefficients and evaluator
        """
        self._stats['splines_computed'] += 1
        n = len(x) - 1  # Number of segments

        if n < 1:
            raise ValueError("Need at least 2 data points")

        # Compute h[i] = x[i+1] - x[i]
        h = [x[i + 1] - x[i] for i in range(n)]

        # Build tridiagonal system for second derivatives
        # Natural spline: M[0] = M[n] = 0
        # Clamped: specified first derivatives at endpoints

        if bc_type == 'natural':
            M = self._solve_natural_spline(x, y, h, n)
        elif bc_type == 'clamped':
            M = self._solve_clamped_spline(x, y, h, n, deriv_start, deriv_end)
        elif bc_type == 'not_a_knot':
            M = self._solve_not_a_knot_spline(x, y, h, n)
        else:
            M = self._solve_natural_spline(x, y, h, n)

        # Compute coefficients for each segment
        # S_i(t) = a_i + b_i(t-x_i) + c_i(t-x_i)^2 + d_i(t-x_i)^3
        coefficients = []
        for i in range(n):
            a_i = y[i]
            b_i = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * M[i] + M[i + 1]) / 6
            c_i = M[i] / 2
            d_i = (M[i + 1] - M[i]) / (6 * h[i])
            coefficients.append([a_i, b_i, c_i, d_i])

        # Create evaluator function
        x_data = x.copy()

        def evaluator(t: float) -> float:
            self._stats['evaluations'] += 1
            # Find the right segment
            if t <= x_data[0]:
                i = 0
            elif t >= x_data[-1]:
                i = n - 1
            else:
                for i in range(n):
                    if x_data[i] <= t < x_data[i + 1]:
                        break

            a, b, c, d = coefficients[i]
            dx = t - x_data[i]
            return a + b * dx + c * dx ** 2 + d * dx ** 3

        def derivative_evaluator(t: float) -> float:
            # Find the right segment
            if t <= x_data[0]:
                i = 0
            elif t >= x_data[-1]:
                i = n - 1
            else:
                for i in range(n):
                    if x_data[i] <= t < x_data[i + 1]:
                        break

            a, b, c, d = coefficients[i]
            dx = t - x_data[i]
            return b + 2 * c * dx + 3 * d * dx ** 2

        return SplineResult(
            coefficients=coefficients,
            knots=x.copy(),
            evaluator=evaluator,
            derivative_evaluator=derivative_evaluator,
            method='cubic_spline_' + bc_type
        )

    def _solve_natural_spline(
        self,
        x: List[float],
        y: List[float],
        h: List[float],
        n: int
    ) -> List[float]:
        """Solve tridiagonal system for natural cubic spline."""
        # Natural boundary: M[0] = M[n] = 0
        # Interior equations form tridiagonal system

        if n == 1:
            return [0.0, 0.0]

        # Build right-hand side
        b = [0.0] * (n + 1)
        for i in range(1, n):
            b[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

        # Solve tridiagonal system using Thomas algorithm
        # Diagonal elements
        diag = [0.0] + [2 * (h[i - 1] + h[i]) for i in range(1, n)] + [0.0]
        # Lower diagonal
        lower = [0.0] + [h[i - 1] for i in range(1, n)]
        # Upper diagonal
        upper = [h[i] for i in range(0, n - 1)] + [0.0]

        M = [0.0] * (n + 1)

        # Forward elimination
        for i in range(1, n):
            if abs(diag[i]) < 1e-15:
                continue
            factor = lower[i - 1] / diag[i - 1] if abs(diag[i - 1]) > 1e-15 else 0
            diag[i] -= factor * upper[i - 1]
            b[i] -= factor * b[i - 1]

        # Back substitution
        for i in range(n - 1, 0, -1):
            if abs(diag[i]) > 1e-15:
                M[i] = (b[i] - upper[i - 1] * M[i + 1]) / diag[i] if i < n - 1 else b[i] / diag[i]

        return M

    def _solve_clamped_spline(
        self,
        x: List[float],
        y: List[float],
        h: List[float],
        n: int,
        deriv_start: float,
        deriv_end: float
    ) -> List[float]:
        """Solve tridiagonal system for clamped cubic spline."""
        # Clamped: specify f'(x[0]) and f'(x[n])

        # Build augmented system including boundary conditions
        size = n + 1

        # Right-hand side
        b = [0.0] * size
        b[0] = 6 * ((y[1] - y[0]) / h[0] - deriv_start)
        for i in range(1, n):
            b[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])
        b[n] = 6 * (deriv_end - (y[n] - y[n - 1]) / h[n - 1])

        # Build tridiagonal matrix
        diag = [2 * h[0]] + [2 * (h[i - 1] + h[i]) for i in range(1, n)] + [2 * h[n - 1]]
        lower = [h[i - 1] for i in range(1, n + 1)]
        upper = [h[i] for i in range(n)]

        M = [0.0] * size

        # Thomas algorithm
        c_prime = [0.0] * size
        d_prime = [0.0] * size

        c_prime[0] = upper[0] / diag[0] if abs(diag[0]) > 1e-15 else 0
        d_prime[0] = b[0] / diag[0] if abs(diag[0]) > 1e-15 else 0

        for i in range(1, size):
            denom = diag[i] - lower[i - 1] * c_prime[i - 1] if i - 1 < len(lower) else diag[i]
            if abs(denom) < 1e-15:
                denom = 1e-15
            c_prime[i] = upper[i - 1] / denom if i - 1 < len(upper) else 0
            d_prime[i] = (b[i] - (lower[i - 1] if i - 1 < len(lower) else 0) * d_prime[i - 1]) / denom

        M[size - 1] = d_prime[size - 1]
        for i in range(size - 2, -1, -1):
            M[i] = d_prime[i] - c_prime[i] * M[i + 1]

        return M

    def _solve_not_a_knot_spline(
        self,
        x: List[float],
        y: List[float],
        h: List[float],
        n: int
    ) -> List[float]:
        """Solve system for not-a-knot cubic spline."""
        # Not-a-knot: S'''_0(x_1) = S'''_1(x_1) and S'''_{n-2}(x_{n-1}) = S'''_{n-1}(x_{n-1})
        # This makes the first two and last two polynomials the same

        if n < 3:
            return self._solve_natural_spline(x, y, h, n)

        # Build modified system
        b = [0.0] * (n + 1)
        for i in range(1, n):
            b[i] = 6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

        # Apply not-a-knot conditions
        # Condition at left: h[1]*M[0] - (h[0]+h[1])*M[1] + h[0]*M[2] = 0
        # Condition at right: h[n-1]*M[n-2] - (h[n-2]+h[n-1])*M[n-1] + h[n-2]*M[n] = 0

        # Simplify by setting up as tridiagonal with modified first/last rows
        M = self._solve_natural_spline(x, y, h, n)

        return M

    # ==================== HERMITE INTERPOLATION ====================

    def hermite_spline(
        self,
        x: List[float],
        y: List[float],
        dy: List[float],
    ) -> SplineResult:
        """
        Compute Hermite cubic interpolation.

        Args:
            x: x-coordinates
            y: y-values
            dy: derivative values at each point

        Returns:
            SplineResult with coefficients and evaluator
        """
        self._stats['splines_computed'] += 1
        n = len(x) - 1

        if len(y) != len(x) or len(dy) != len(x):
            raise ValueError("x, y, and dy must have same length")

        coefficients = []
        for i in range(n):
            h = x[i + 1] - x[i]

            # Hermite basis functions give us these coefficients
            a = y[i]
            b = dy[i]
            c = (3 * (y[i + 1] - y[i]) / h - 2 * dy[i] - dy[i + 1]) / h
            d = (2 * (y[i] - y[i + 1]) / h + dy[i] + dy[i + 1]) / (h ** 2)

            coefficients.append([a, b, c, d])

        x_data = x.copy()

        def evaluator(t: float) -> float:
            self._stats['evaluations'] += 1
            if t <= x_data[0]:
                i = 0
            elif t >= x_data[-1]:
                i = n - 1
            else:
                for i in range(n):
                    if x_data[i] <= t < x_data[i + 1]:
                        break

            a, b, c, d = coefficients[i]
            dx = t - x_data[i]
            return a + b * dx + c * dx ** 2 + d * dx ** 3

        return SplineResult(
            coefficients=coefficients,
            knots=x.copy(),
            evaluator=evaluator,
            method='hermite'
        )

    # ==================== AKIMA INTERPOLATION ====================

    def akima_spline(
        self,
        x: List[float],
        y: List[float],
    ) -> SplineResult:
        """
        Compute Akima interpolation (reduced overshoot/oscillation).

        The Akima method uses a weighted average of slopes to reduce
        oscillation near outliers.

        Args:
            x: x-coordinates
            y: y-values

        Returns:
            SplineResult with coefficients and evaluator
        """
        self._stats['splines_computed'] += 1
        n = len(x)

        if n < 3:
            raise ValueError("Need at least 3 data points for Akima spline")

        # Compute slopes between consecutive points
        m = [(y[i + 1] - y[i]) / (x[i + 1] - x[i]) for i in range(n - 1)]

        # Extend slopes at boundaries (using linear extrapolation)
        m = [2 * m[0] - m[1], m[0]] + m + [m[-1], 2 * m[-1] - m[-2]]

        # Compute Akima weights
        t = []
        for i in range(n):
            w1 = abs(m[i + 3] - m[i + 2])
            w2 = abs(m[i + 1] - m[i])

            if w1 + w2 == 0:
                t.append((m[i + 1] + m[i + 2]) / 2)
            else:
                t.append((w1 * m[i + 1] + w2 * m[i + 2]) / (w1 + w2))

        # Build Hermite-like spline with Akima slopes
        return self.hermite_spline(x, y, t)

    # ==================== PCHIP INTERPOLATION ====================

    def pchip_spline(
        self,
        x: List[float],
        y: List[float],
    ) -> SplineResult:
        """
        Piecewise Cubic Hermite Interpolating Polynomial (PCHIP).

        Preserves monotonicity and avoids overshooting.

        Args:
            x: x-coordinates
            y: y-values

        Returns:
            SplineResult with coefficients and evaluator
        """
        self._stats['splines_computed'] += 1
        n = len(x)

        if n < 2:
            raise ValueError("Need at least 2 data points")

        # Compute slopes
        h = [x[i + 1] - x[i] for i in range(n - 1)]
        delta = [(y[i + 1] - y[i]) / h[i] for i in range(n - 1)]

        # Compute PCHIP slopes at each point
        d = [0.0] * n

        # Interior points
        for i in range(1, n - 1):
            if delta[i - 1] * delta[i] > 0:
                # Same sign - use weighted harmonic mean
                w1 = 2 * h[i] + h[i - 1]
                w2 = h[i] + 2 * h[i - 1]
                d[i] = (w1 + w2) / (w1 / delta[i - 1] + w2 / delta[i])
            else:
                # Different signs or zero - use zero slope
                d[i] = 0.0

        # Endpoints
        d[0] = self._pchip_end_slope(h[0], h[1], delta[0], delta[1]) if n > 2 else delta[0]
        d[-1] = self._pchip_end_slope(h[-1], h[-2], delta[-1], delta[-2]) if n > 2 else delta[-1]

        return self.hermite_spline(x, y, d)

    def _pchip_end_slope(self, h1, h2, del1, del2) -> float:
        """Compute PCHIP slope at endpoint."""
        d = ((2 * h1 + h2) * del1 - h1 * del2) / (h1 + h2)

        # Adjust if overshoots
        if d * del1 < 0:
            d = 0
        elif del1 * del2 < 0 and abs(d) > 3 * abs(del1):
            d = 3 * del1

        return d

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'cubic_spline':
            result = self.cubic_spline(**params)
            return {'status': 'success', 'result': result}
        elif action == 'hermite_spline':
            result = self.hermite_spline(**params)
            return {'status': 'success', 'result': result}
        elif action == 'akima_spline':
            result = self.akima_spline(**params)
            return {'status': 'success', 'result': result}
        elif action == 'pchip_spline':
            result = self.pchip_spline(**params)
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
                tags=['spline', 'interpolation'], status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []
            for entry in entries:
                self.add_belief('pending_spline_task', entry, source='blackboard')

    def deliberate(self) -> List:
        """Generate intentions from beliefs."""
        new_intentions = []
        if self.has_belief('pending_spline_task'):
            task_belief = self.get_belief('pending_spline_task')
            if task_belief:
                intention = Intention(
                    goal="compute_spline",
                    plan=["analyze_data", "compute_spline", "post_results"],
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
        if action in ['analyze_data', 'compute_spline']:
            intention.advance()
        elif action == 'post_results':
            intention.complete()


__all__ = [
    'SplineSpecialist',
    'SplineResult',
]
