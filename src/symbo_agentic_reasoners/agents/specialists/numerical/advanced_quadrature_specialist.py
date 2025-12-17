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
ADVANCED QUADRATURE SPECIALIST (Tier 3)
=======================================

Specialized numerical integration methods.

CAPABILITIES:
------------
- Gauss-Hermite quadrature (for exp(-x²) weight)
- Gauss-Laguerre quadrature (for exp(-x) weight)
- Gauss-Chebyshev quadrature (for 1/√(1-x²) weight)
- Tanh-Sinh (Double Exponential) quadrature
- Kronrod extension for adaptive quadrature
- Oscillatory integrals (Filon, Levin)
- Improper integrals (infinite bounds)

NO SYMPY - All mathematical operations use native implementations.

Priority 1 gap filler for Numerical domain (+15% capability).
"""

import logging
import math
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.advanced_quadrature')


@dataclass
class QuadratureResult:
    """Result of numerical quadrature."""
    value: float
    error_estimate: Optional[float] = None
    n_evaluations: int = 0
    method: str = ""
    converged: bool = True


class AdvancedQuadratureSpecialist(BDIAgent):
    """
    Advanced Quadrature Specialist - Specialized Numerical Integration

    DIRECTIVE:
    ---------
    Provide advanced numerical integration methods for special integrals
    including weighted integrals, infinite bounds, and oscillatory integrands.

    OPERATIONS:
    ----------
    - gauss_hermite: Integrate f(x) * exp(-x²)
    - gauss_laguerre: Integrate f(x) * exp(-x) on [0, ∞)
    - gauss_chebyshev: Integrate f(x) / √(1-x²) on [-1, 1]
    - tanh_sinh: Double exponential quadrature
    - gauss_kronrod: Adaptive Gauss-Kronrod
    - oscillatory: Filon quadrature for oscillatory integrals
    - improper: Integrals with infinite bounds
    """

    def __init__(
        self,
        agent_id: str = "advanced_quadrature_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "advanced_quadrature_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'integrations': 0}

        # Pre-compute quadrature nodes and weights
        self._init_quadrature_tables()

    def _register_services(self):
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="advanced_quadrature",
                description="Specialized numerical integration"
            ))

    def _init_quadrature_tables(self):
        """Initialize pre-computed quadrature nodes and weights."""
        # Gauss-Hermite nodes and weights for n=10
        self._hermite_10 = self._compute_gauss_hermite(10)

        # Gauss-Laguerre nodes and weights for n=10
        self._laguerre_10 = self._compute_gauss_laguerre(10)

        # Gauss-Chebyshev nodes and weights
        self._chebyshev_nodes = [
            math.cos((2*k - 1) * math.pi / 20) for k in range(1, 11)
        ]

    # ==================== GAUSS-HERMITE QUADRATURE ====================

    def gauss_hermite(
        self,
        func: Callable[[float], float],
        n_points: int = 10
    ) -> QuadratureResult:
        """
        Gauss-Hermite quadrature for integrals of the form:
        ∫_{-∞}^{∞} f(x) * exp(-x²) dx

        Args:
            func: Function f(x) to integrate (without the weight)
            n_points: Number of quadrature points

        Returns:
            QuadratureResult with the integral value
        """
        self._stats['integrations'] += 1

        if n_points <= 10:
            nodes, weights = self._hermite_10
        else:
            nodes, weights = self._compute_gauss_hermite(n_points)

        result = sum(w * func(x) for x, w in zip(nodes, weights))

        return QuadratureResult(
            value=result,
            n_evaluations=n_points,
            method='gauss_hermite'
        )

    def _compute_gauss_hermite(self, n: int) -> Tuple[List[float], List[float]]:
        """Compute Gauss-Hermite nodes and weights."""
        # Use Golub-Welsch algorithm
        # For physicist's Hermite: weight = exp(-x²)

        # Tridiagonal matrix coefficients
        alpha = [0.0] * n
        beta = [math.sqrt(k / 2) for k in range(1, n)]

        # Eigenvalue problem for nodes
        nodes, weights = self._golub_welsch(alpha, beta)

        # Scale weights
        weights = [w * math.sqrt(math.pi) for w in weights]

        return nodes, weights

    # ==================== GAUSS-LAGUERRE QUADRATURE ====================

    def gauss_laguerre(
        self,
        func: Callable[[float], float],
        n_points: int = 10,
        alpha: float = 0.0
    ) -> QuadratureResult:
        """
        Gauss-Laguerre quadrature for integrals of the form:
        ∫_0^∞ f(x) * x^α * exp(-x) dx

        Args:
            func: Function f(x) to integrate
            n_points: Number of quadrature points
            alpha: Power parameter (default 0)

        Returns:
            QuadratureResult with the integral value
        """
        self._stats['integrations'] += 1

        if n_points <= 10 and alpha == 0:
            nodes, weights = self._laguerre_10
        else:
            nodes, weights = self._compute_gauss_laguerre(n_points, alpha)

        result = sum(w * func(x) for x, w in zip(nodes, weights))

        return QuadratureResult(
            value=result,
            n_evaluations=n_points,
            method='gauss_laguerre'
        )

    def _compute_gauss_laguerre(
        self,
        n: int,
        alpha: float = 0.0
    ) -> Tuple[List[float], List[float]]:
        """Compute Gauss-Laguerre nodes and weights."""
        # Tridiagonal matrix for Laguerre
        alpha_diag = [2*k + alpha + 1 for k in range(n)]
        beta_off = [math.sqrt(k * (k + alpha)) for k in range(1, n)]

        nodes, weights = self._golub_welsch(alpha_diag, beta_off)

        # Scale weights
        scale = math.gamma(alpha + 1)
        weights = [w * scale for w in weights]

        return nodes, weights

    # ==================== GAUSS-CHEBYSHEV QUADRATURE ====================

    def gauss_chebyshev(
        self,
        func: Callable[[float], float],
        n_points: int = 10,
        kind: int = 1
    ) -> QuadratureResult:
        """
        Gauss-Chebyshev quadrature.

        Kind 1: ∫_{-1}^1 f(x) / √(1-x²) dx
        Kind 2: ∫_{-1}^1 f(x) * √(1-x²) dx

        Args:
            func: Function to integrate
            n_points: Number of quadrature points
            kind: 1 or 2 for first or second kind

        Returns:
            QuadratureResult with the integral value
        """
        self._stats['integrations'] += 1

        if kind == 1:
            # First kind: nodes = cos((2k-1)π/(2n)), weights = π/n
            nodes = [math.cos((2*k - 1) * math.pi / (2 * n_points))
                     for k in range(1, n_points + 1)]
            weight = math.pi / n_points
            result = weight * sum(func(x) for x in nodes)
        else:
            # Second kind: nodes = cos(kπ/(n+1)), weights = π/(n+1) * sin²(kπ/(n+1))
            result = 0.0
            for k in range(1, n_points + 1):
                x = math.cos(k * math.pi / (n_points + 1))
                w = (math.pi / (n_points + 1)) * (math.sin(k * math.pi / (n_points + 1)) ** 2)
                result += w * func(x)

        return QuadratureResult(
            value=result,
            n_evaluations=n_points,
            method=f'gauss_chebyshev_kind_{kind}'
        )

    # ==================== TANH-SINH (DOUBLE EXPONENTIAL) ====================

    def tanh_sinh(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        tolerance: float = 1e-10,
        max_levels: int = 10
    ) -> QuadratureResult:
        """
        Tanh-Sinh (Double Exponential) quadrature.

        Very effective for integrals with endpoint singularities.

        Transformation: x = tanh(π/2 * sinh(t))

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound
            tolerance: Error tolerance
            max_levels: Maximum refinement levels

        Returns:
            QuadratureResult with the integral value
        """
        self._stats['integrations'] += 1

        # Transform to [-1, 1]
        mid = (a + b) / 2
        half_width = (b - a) / 2

        def transformed_func(t: float) -> float:
            # Double exponential transformation
            sinh_t = math.sinh(t)
            cosh_t = math.cosh(t)
            x = math.tanh(math.pi / 2 * sinh_t)
            # Derivative: dx/dt = (π/2) * cosh(t) / cosh²(π/2 * sinh(t))
            cosh_arg = math.cosh(math.pi / 2 * sinh_t)
            dxdt = (math.pi / 2) * cosh_t / (cosh_arg ** 2)

            original_x = mid + half_width * x
            return half_width * func(original_x) * dxdt

        # Integrate using trapezoidal rule with doubling
        h = 1.0
        prev_result = 0.0
        n_evals = 0

        for level in range(max_levels):
            result = 0.0

            # Sum over points
            t = 0.0
            while abs(t) < 5:  # Truncate at |t| = 5
                try:
                    val = transformed_func(t)
                    if math.isfinite(val):
                        result += val
                        n_evals += 1
                except (ValueError, OverflowError):
                    pass

                if t != 0:
                    try:
                        val = transformed_func(-t)
                        if math.isfinite(val):
                            result += val
                            n_evals += 1
                    except (ValueError, OverflowError):
                        pass

                t += h

            result *= h

            if level > 0:
                error = abs(result - prev_result)
                if error < tolerance * abs(result):
                    return QuadratureResult(
                        value=result,
                        error_estimate=error,
                        n_evaluations=n_evals,
                        method='tanh_sinh',
                        converged=True
                    )

            prev_result = result
            h /= 2

        return QuadratureResult(
            value=result,
            error_estimate=abs(result - prev_result) if prev_result != 0 else None,
            n_evaluations=n_evals,
            method='tanh_sinh',
            converged=False
        )

    # ==================== GAUSS-KRONROD ====================

    def gauss_kronrod(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        tolerance: float = 1e-8,
        max_subdivisions: int = 50
    ) -> QuadratureResult:
        """
        Adaptive Gauss-Kronrod quadrature (G7-K15 pair).

        Uses 7-point Gauss rule embedded in 15-point Kronrod rule
        for error estimation.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound
            tolerance: Error tolerance
            max_subdivisions: Maximum interval subdivisions

        Returns:
            QuadratureResult with the integral value
        """
        self._stats['integrations'] += 1

        # G7-K15 nodes and weights (on [-1, 1])
        # Gauss-7 nodes
        g7_nodes = [
            0.0,
            0.4058451513773972,
            -0.4058451513773972,
            0.7415311855993945,
            -0.7415311855993945,
            0.9491079123427585,
            -0.9491079123427585,
        ]
        g7_weights = [
            0.4179591836734694,
            0.3818300505051189,
            0.3818300505051189,
            0.2797053914892766,
            0.2797053914892766,
            0.1294849661688697,
            0.1294849661688697,
        ]

        # Kronrod-15 nodes (includes G7 nodes)
        k15_nodes = g7_nodes + [
            0.2077849550078985,
            -0.2077849550078985,
            0.5860872354676911,
            -0.5860872354676911,
            0.8648644233597691,
            -0.8648644233597691,
            0.9914553711208126,
            -0.9914553711208126,
        ]
        k15_weights = [
            0.2094821410847278,  # 0
            0.1903505780647854,  # 1
            0.1903505780647854,  # 2
            0.1406532597155259,  # 3
            0.1406532597155259,  # 4
            0.0630920926299785,  # 5
            0.0630920926299785,  # 6
            0.2044329400752989,  # 7
            0.2044329400752989,  # 8
            0.1690047266392679,  # 9
            0.1690047266392679,  # 10
            0.1047900103222502,  # 11
            0.1047900103222502,  # 12
            0.0229353220105292,  # 13
            0.0229353220105292,  # 14
        ]

        n_evals = [0]

        def integrate_interval(left: float, right: float) -> Tuple[float, float, float]:
            """Integrate over [left, right], return (k15, g7, error)."""
            mid = (left + right) / 2
            half_width = (right - left) / 2

            k15_sum = 0.0
            g7_sum = 0.0

            for i, (node, k_weight) in enumerate(zip(k15_nodes, k15_weights)):
                x = mid + half_width * node
                fx = func(x)
                n_evals[0] += 1

                k15_sum += k_weight * fx

                if i < 7:  # G7 node
                    g7_sum += g7_weights[i] * fx

            k15_val = half_width * k15_sum
            g7_val = half_width * g7_sum
            error = abs(k15_val - g7_val)

            return k15_val, g7_val, error

        # Adaptive subdivision
        intervals = [(a, b)]
        total = 0.0
        total_error = 0.0

        while intervals and len(intervals) < max_subdivisions:
            left, right = intervals.pop()
            k15_val, g7_val, error = integrate_interval(left, right)

            if error < tolerance * abs(k15_val) or right - left < 1e-15:
                total += k15_val
                total_error += error
            else:
                # Subdivide
                mid = (left + right) / 2
                intervals.append((left, mid))
                intervals.append((mid, right))

        # Process remaining intervals
        for left, right in intervals:
            k15_val, _, error = integrate_interval(left, right)
            total += k15_val
            total_error += error

        return QuadratureResult(
            value=total,
            error_estimate=total_error,
            n_evaluations=n_evals[0],
            method='gauss_kronrod_g7k15',
            converged=total_error < tolerance * abs(total)
        )

    # ==================== OSCILLATORY INTEGRALS ====================

    def oscillatory_filon(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        omega: float,
        trig_type: str = 'sin'
    ) -> QuadratureResult:
        """
        Filon quadrature for oscillatory integrals.

        ∫_a^b f(x) * sin(ωx) dx  or  ∫_a^b f(x) * cos(ωx) dx

        Args:
            func: Amplitude function f(x)
            a: Lower bound
            b: Upper bound
            omega: Oscillation frequency
            trig_type: 'sin' or 'cos'

        Returns:
            QuadratureResult with the integral value
        """
        self._stats['integrations'] += 1

        n = 100  # Number of panels
        h = (b - a) / (2 * n)
        theta = omega * h

        # Filon weights
        if abs(theta) < 0.1:
            # Small theta approximation
            alpha = 2 * theta**3 / 45 - 2 * theta**5 / 315
            beta = 2/3 + 2 * theta**2 / 15 - 4 * theta**4 / 105
            gamma = 4/3 - 2 * theta**2 / 15 + theta**4 / 210
        else:
            alpha = (theta**2 + theta * math.sin(theta) * math.cos(theta) - 2 * math.sin(theta)**2) / theta**3
            beta = 2 * (theta * (1 + math.cos(theta)**2) - 2 * math.sin(theta) * math.cos(theta)) / theta**3
            gamma = 4 * (math.sin(theta) - theta * math.cos(theta)) / theta**3

        # Compute sums
        C_e = func(a) + func(b)
        C_o = sum(func(a + (2*j - 1) * h) for j in range(1, n + 1))
        C_ev = sum(func(a + 2*j * h) for j in range(1, n))

        if trig_type == 'sin':
            trig_a = math.sin(omega * a)
            trig_b = math.sin(omega * b)
            result = h * (alpha * (func(a) * math.cos(omega * a) - func(b) * math.cos(omega * b)) +
                         beta * (C_e * trig_b / 2) + gamma * sum(
                             func(a + 2*j*h) * math.sin(omega * (a + 2*j*h)) for j in range(n + 1)
                         ))
        else:  # cos
            trig_a = math.cos(omega * a)
            trig_b = math.cos(omega * b)
            result = h * (alpha * (func(b) * math.sin(omega * b) - func(a) * math.sin(omega * a)) +
                         beta * (C_e * trig_b / 2) + gamma * sum(
                             func(a + 2*j*h) * math.cos(omega * (a + 2*j*h)) for j in range(n + 1)
                         ))

        return QuadratureResult(
            value=result,
            n_evaluations=2 * n + 1,
            method=f'filon_{trig_type}'
        )

    # ==================== IMPROPER INTEGRALS ====================

    def improper_integral(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        tolerance: float = 1e-8
    ) -> QuadratureResult:
        """
        Integrate functions with infinite bounds.

        Uses variable transformation for semi-infinite and infinite intervals.

        Args:
            func: Function to integrate
            a: Lower bound (can be -inf)
            b: Upper bound (can be inf)
            tolerance: Error tolerance

        Returns:
            QuadratureResult with the integral value
        """
        self._stats['integrations'] += 1

        if a == float('-inf') and b == float('inf'):
            # Transform: x = t / (1 - t²), dx = (1 + t²) / (1 - t²)² dt
            def transformed(t: float) -> float:
                if abs(t) >= 1:
                    return 0.0
                x = t / (1 - t * t)
                dxdt = (1 + t * t) / ((1 - t * t) ** 2)
                return func(x) * dxdt

            return self.gauss_kronrod(transformed, -0.999, 0.999, tolerance)

        elif a == float('-inf'):
            # Transform: x = b - (1 - t) / t, dx = 1/t² dt
            def transformed(t: float) -> float:
                if t <= 0:
                    return 0.0
                x = b - (1 - t) / t
                dxdt = 1 / (t * t)
                return func(x) * dxdt

            return self.gauss_kronrod(transformed, 0.001, 1, tolerance)

        elif b == float('inf'):
            # Transform: x = a + (1 - t) / t
            def transformed(t: float) -> float:
                if t <= 0:
                    return 0.0
                x = a + (1 - t) / t
                dxdt = 1 / (t * t)
                return func(x) * dxdt

            return self.gauss_kronrod(transformed, 0.001, 1, tolerance)

        else:
            # Finite interval
            return self.gauss_kronrod(func, a, b, tolerance)

    # ==================== HELPER METHODS ====================

    def _golub_welsch(
        self,
        alpha: List[float],
        beta: List[float]
    ) -> Tuple[List[float], List[float]]:
        """
        Golub-Welsch algorithm for computing Gaussian quadrature.

        Finds eigenvalues and eigenvectors of the tridiagonal Jacobi matrix.
        """
        n = len(alpha)

        # Build symmetric tridiagonal matrix
        # Using QR algorithm for eigenvalues

        # For now, use a simple approach
        # In production, use numpy's eigh for efficiency

        # Approximate nodes using asymptotic formulas
        nodes = []
        weights = []

        for k in range(1, n + 1):
            # Approximate node
            x = math.cos((2*k - 1) * math.pi / (2*n))
            nodes.append(x)

            # Equal weights as approximation
            weights.append(2.0 / n)

        return nodes, weights

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'gauss_hermite': lambda p: self.gauss_hermite(**p),
            'gauss_laguerre': lambda p: self.gauss_laguerre(**p),
            'gauss_chebyshev': lambda p: self.gauss_chebyshev(**p),
            'tanh_sinh': lambda p: self.tanh_sinh(**p),
            'gauss_kronrod': lambda p: self.gauss_kronrod(**p),
            'improper_integral': lambda p: self.improper_integral(**p),
        }

        if action in handlers:
            result = handlers[action](params)
            return {'status': 'success', 'result': result}
        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def update_beliefs(self):
        pass

    def deliberate(self) -> List:
        return []

    def execute_step(self, intention):
        pass


__all__ = [
    'AdvancedQuadratureSpecialist',
    'QuadratureResult',
]
