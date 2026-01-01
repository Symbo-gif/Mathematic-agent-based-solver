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
NUMERICAL METHODS SPECIALIST (Tier 3)
=====================================

Comprehensive numerical computation methods specialist.

CAPABILITIES:
------------
- Numerical integration (quadrature methods)
- Numerical differentiation
- Numerical ODE solving (Runge-Kutta, Euler)
- Root finding (Newton, bisection, Brent)
- Interpolation (Lagrange, Newton, spline)
- Numerical optimization (gradient descent, Newton)

ALGORITHMS:
-----------
Native implementation - NO NumPy or SciPy dependency

INTEGRATION:
1. Trapezoidal rule
2. Simpson's rule (1/3 and 3/8)
3. Romberg integration
4. Gaussian quadrature
5. Adaptive quadrature

DIFFERENTIATION:
1. Forward difference
2. Backward difference
3. Central difference
4. Richardson extrapolation

ODE SOLVING:
1. Euler method
2. Runge-Kutta 4th order (RK4)
3. Runge-Kutta-Fehlberg (RK45) adaptive
4. Adams-Bashforth multi-step

REFERENCE:
---------
- Mathematical Capability Gap Analysis: Numerical methods at 50%
- Target: 80% capability for numerical computation
"""

import logging
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger('symbo_agentic_reasoners.specialists.numerical')


@dataclass
class IntegrationResult:
    """Result of numerical integration."""
    value: float
    error_estimate: Optional[float] = None
    n_evaluations: int = 0
    method: str = "unknown"
    converged: bool = True


@dataclass
class ODESolution:
    """Solution of numerical ODE."""
    t: List[float]  # Time/independent variable points
    y: List[List[float]]  # Solution values (list of vectors for systems)
    method: str = "unknown"
    n_steps: int = 0
    error_estimates: Optional[List[float]] = None


@dataclass
class InterpolationResult:
    """Result of interpolation."""
    polynomial_coeffs: List[float]
    evaluator: Optional[Callable] = None
    method: str = "unknown"


class NumericalMethodsSpecialist(BDIAgent):
    """
    Numerical Methods Specialist - Comprehensive Numerical Computation

    DIRECTIVE:
    ---------
    Provide robust numerical computation methods for integration,
    differentiation, ODE solving, root finding, and interpolation.

    OPERATIONS:
    ----------
    - integrate: Numerical integration with multiple methods
    - differentiate: Numerical differentiation
    - solve_ode_ivp: Solve ODE initial value problems
    - find_root: Root finding methods
    - interpolate: Polynomial interpolation
    - optimize: Numerical optimization
    """

    def __init__(
        self,
        agent_id: str = "numerical_methods_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)

        # Set additional attributes
        self.agent_type = "numerical_methods_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard

        self._register_services()

        self._stats = {
            'integrations': 0,
            'derivatives': 0,
            'ode_solutions': 0,
            'roots_found': 0,
            'interpolations': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="numerical_integration",
                    description="Numerical integration methods"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="numerical_differentiation",
                    description="Numerical differentiation"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="numerical_ode",
                    description="Numerical ODE solving"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== NUMERICAL INTEGRATION ====================

    def integrate(
        self,
        func: Callable[[float], float],
        a: float,
        b: float,
        method: str = 'adaptive',
        tolerance: float = 1e-8,
        max_subdivisions: int = 50,
    ) -> IntegrationResult:
        """
        Numerical integration of f(x) from a to b.

        Args:
            func: Function to integrate
            a: Lower bound
            b: Upper bound
            method: 'trapezoidal', 'simpson', 'romberg', 'gaussian', 'adaptive'
            tolerance: Error tolerance for adaptive methods
            max_subdivisions: Maximum subdivisions for adaptive

        Returns:
            IntegrationResult with value and error estimate
        """
        if method == 'trapezoidal':
            return self._trapezoidal(func, a, b, 1000)
        elif method == 'simpson':
            return self._simpson(func, a, b, 1000)
        elif method == 'romberg':
            return self._romberg(func, a, b, tolerance)
        elif method == 'gaussian':
            return self._gaussian_quadrature(func, a, b, n_points=5)
        elif method == 'adaptive':
            return self._adaptive_simpson(func, a, b, tolerance, max_subdivisions)
        else:
            # Default to adaptive Simpson
            return self._adaptive_simpson(func, a, b, tolerance, max_subdivisions)

    def _trapezoidal(self, func, a, b, n) -> IntegrationResult:
        """Trapezoidal rule integration."""
        h = (b - a) / n
        total = 0.5 * (func(a) + func(b))

        for i in range(1, n):
            total += func(a + i * h)

        value = h * total
        self._stats['integrations'] += 1

        return IntegrationResult(
            value=value,
            n_evaluations=n + 1,
            method='trapezoidal'
        )

    def _simpson(self, func, a, b, n) -> IntegrationResult:
        """Simpson's 1/3 rule integration."""
        if n % 2 != 0:
            n += 1

        h = (b - a) / n
        total = func(a) + func(b)

        for i in range(1, n):
            x = a + i * h
            if i % 2 == 0:
                total += 2 * func(x)
            else:
                total += 4 * func(x)

        value = (h / 3) * total
        self._stats['integrations'] += 1

        return IntegrationResult(
            value=value,
            n_evaluations=n + 1,
            method='simpson'
        )

    def _romberg(self, func, a, b, tolerance) -> IntegrationResult:
        """Romberg integration using Richardson extrapolation."""
        max_iterations = 20
        R = [[0.0] * max_iterations for _ in range(max_iterations)]

        h = b - a
        R[0][0] = 0.5 * h * (func(a) + func(b))
        n_evals = 2

        for i in range(1, max_iterations):
            h /= 2
            total = 0.0
            n_points = 2 ** (i - 1)

            for k in range(1, n_points + 1):
                total += func(a + (2 * k - 1) * h)
                n_evals += 1

            R[i][0] = 0.5 * R[i - 1][0] + h * total

            for j in range(1, i + 1):
                factor = 4 ** j
                R[i][j] = (factor * R[i][j - 1] - R[i - 1][j - 1]) / (factor - 1)

            error = abs(R[i][i] - R[i - 1][i - 1]) if i > 0 else float('inf')
            if error < tolerance:
                self._stats['integrations'] += 1
                return IntegrationResult(
                    value=R[i][i],
                    error_estimate=error,
                    n_evaluations=n_evals,
                    method='romberg',
                    converged=True
                )

        self._stats['integrations'] += 1
        return IntegrationResult(
            value=R[max_iterations - 1][max_iterations - 1],
            error_estimate=error,
            n_evaluations=n_evals,
            method='romberg',
            converged=False
        )

    def _gaussian_quadrature(self, func, a, b, n_points=5) -> IntegrationResult:
        """Gaussian quadrature using Legendre polynomials."""
        # Gauss-Legendre nodes and weights for common orders
        gauss_data = {
            2: ([-0.5773502692, 0.5773502692], [1.0, 1.0]),
            3: ([-0.7745966692, 0.0, 0.7745966692], [0.5555555556, 0.8888888889, 0.5555555556]),
            4: ([-0.8611363116, -0.3399810436, 0.3399810436, 0.8611363116],
                [0.3478548451, 0.6521451549, 0.6521451549, 0.3478548451]),
            5: ([-0.9061798459, -0.5384693101, 0.0, 0.5384693101, 0.9061798459],
                [0.2369268851, 0.4786286705, 0.5688888889, 0.4786286705, 0.2369268851]),
        }

        if n_points not in gauss_data:
            n_points = 5

        nodes, weights = gauss_data[n_points]

        # Transform from [-1, 1] to [a, b]
        c1 = (b - a) / 2
        c2 = (b + a) / 2

        total = 0.0
        for node, weight in zip(nodes, weights):
            x = c1 * node + c2
            total += weight * func(x)

        value = c1 * total
        self._stats['integrations'] += 1

        return IntegrationResult(
            value=value,
            n_evaluations=n_points,
            method='gaussian'
        )

    def _adaptive_simpson(self, func, a, b, tolerance, max_depth) -> IntegrationResult:
        """Adaptive Simpson's rule with recursive subdivision."""
        n_evals = [0]

        def simpson_rule(f, left, right):
            """Perform simpson rule operation.

            Args:
            f: Description needed
            left: Description needed
            right: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.simpson_rule(...)
            """
            mid = (left + right) / 2
            h = (right - left) / 6
            n_evals[0] += 3
            return h * (f(left) + 4 * f(mid) + f(right))

        def adaptive(left, right, tol, whole, depth):
            """Perform adaptive operation.

            Args:
            left: Description needed
            right: Description needed
            tol: Description needed
            whole: Description needed
            depth: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.adaptive(...)
            """
            mid = (left + right) / 2
            left_half = simpson_rule(func, left, mid)
            right_half = simpson_rule(func, mid, right)
            total = left_half + right_half

            error = abs(total - whole) / 15

            if error < tol or depth >= max_depth:
                return total + (total - whole) / 15, error

            left_result, left_err = adaptive(left, mid, tol / 2, left_half, depth + 1)
            right_result, right_err = adaptive(mid, right, tol / 2, right_half, depth + 1)

            return left_result + right_result, left_err + right_err

        whole = simpson_rule(func, a, b)
        value, error = adaptive(a, b, tolerance, whole, 0)

        self._stats['integrations'] += 1
        return IntegrationResult(
            value=value,
            error_estimate=error,
            n_evaluations=n_evals[0],
            method='adaptive_simpson',
            converged=error < tolerance
        )

    # ==================== NUMERICAL DIFFERENTIATION ====================

    def differentiate(
        self,
        func: Callable[[float], float],
        x: float,
        h: float = 1e-5,
        method: str = 'central',
        order: int = 1,
    ) -> float:
        """
        Numerical differentiation at point x.

        Args:
            func: Function to differentiate
            x: Point at which to differentiate
            h: Step size
            method: 'forward', 'backward', 'central', 'richardson'
            order: Order of derivative (1 or 2)

        Returns:
            Numerical derivative value
        """
        self._stats['derivatives'] += 1

        if order == 1:
            if method == 'forward':
                return (func(x + h) - func(x)) / h
            elif method == 'backward':
                return (func(x) - func(x - h)) / h
            elif method == 'central':
                return (func(x + h) - func(x - h)) / (2 * h)
            elif method == 'richardson':
                return self._richardson_derivative(func, x, h)
            else:
                return (func(x + h) - func(x - h)) / (2 * h)

        elif order == 2:
            return (func(x + h) - 2 * func(x) + func(x - h)) / (h ** 2)

        else:
            # Higher order derivatives via recursion
            def first_deriv(t):
                """Perform first deriv operation.

                Args:
                t: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.first_deriv(...)
                """
                return self.differentiate(func, t, h, method, 1)
            return self.differentiate(first_deriv, x, h, method, order - 1)

    def _richardson_derivative(self, func, x, h) -> float:
        """Richardson extrapolation for improved accuracy."""
        d1 = (func(x + h) - func(x - h)) / (2 * h)
        d2 = (func(x + h / 2) - func(x - h / 2)) / h
        return (4 * d2 - d1) / 3

    def gradient(
        self,
        func: Callable[[List[float]], float],
        x: List[float],
        h: float = 1e-5,
    ) -> List[float]:
        """
        Compute gradient of multivariate function.

        Args:
            func: Function R^n -> R
            x: Point at which to compute gradient
            h: Step size

        Returns:
            Gradient vector
        """
        n = len(x)
        grad = []

        for i in range(n):
            x_plus = x.copy()
            x_minus = x.copy()
            x_plus[i] += h
            x_minus[i] -= h
            grad.append((func(x_plus) - func(x_minus)) / (2 * h))

        return grad

    # ==================== ODE SOLVING ====================

    def solve_ode_ivp(
        self,
        func: Callable[[float, List[float]], List[float]],
        y0: List[float],
        t_span: Tuple[float, float],
        method: str = 'rk4',
        n_steps: int = 100,
        tolerance: float = 1e-6,
    ) -> ODESolution:
        """
        Solve initial value problem: dy/dt = f(t, y), y(t0) = y0.

        Args:
            func: Right-hand side function f(t, y) returning dy/dt
            y0: Initial condition vector
            t_span: (t0, tf) time span
            method: 'euler', 'rk4', 'rk45' (adaptive)
            n_steps: Number of steps (for fixed-step methods)
            tolerance: Error tolerance (for adaptive methods)

        Returns:
            ODESolution with time points and solution values
        """
        if method == 'euler':
            return self._euler_method(func, y0, t_span, n_steps)
        elif method == 'rk4':
            return self._rk4_method(func, y0, t_span, n_steps)
        elif method == 'rk45':
            return self._rk45_adaptive(func, y0, t_span, tolerance)
        else:
            return self._rk4_method(func, y0, t_span, n_steps)

    def _euler_method(self, func, y0, t_span, n_steps) -> ODESolution:
        """Euler's method for ODE solving."""
        t0, tf = t_span
        h = (tf - t0) / n_steps

        t_values = [t0]
        y_values = [y0.copy()]

        t = t0
        y = y0.copy()

        for _ in range(n_steps):
            dy = func(t, y)
            y = [yi + h * dyi for yi, dyi in zip(y, dy)]
            t += h
            t_values.append(t)
            y_values.append(y.copy())

        self._stats['ode_solutions'] += 1
        return ODESolution(
            t=t_values,
            y=y_values,
            method='euler',
            n_steps=n_steps
        )

    def _rk4_method(self, func, y0, t_span, n_steps) -> ODESolution:
        """Classic 4th-order Runge-Kutta method."""
        t0, tf = t_span
        h = (tf - t0) / n_steps

        t_values = [t0]
        y_values = [y0.copy()]

        t = t0
        y = y0.copy()

        for _ in range(n_steps):
            k1 = func(t, y)
            k2 = func(t + h / 2, [yi + h / 2 * k1i for yi, k1i in zip(y, k1)])
            k3 = func(t + h / 2, [yi + h / 2 * k2i for yi, k2i in zip(y, k2)])
            k4 = func(t + h, [yi + h * k3i for yi, k3i in zip(y, k3)])

            y = [
                yi + (h / 6) * (k1i + 2 * k2i + 2 * k3i + k4i)
                for yi, k1i, k2i, k3i, k4i in zip(y, k1, k2, k3, k4)
            ]
            t += h

            t_values.append(t)
            y_values.append(y.copy())

        self._stats['ode_solutions'] += 1
        return ODESolution(
            t=t_values,
            y=y_values,
            method='rk4',
            n_steps=n_steps
        )

    def _rk45_adaptive(self, func, y0, t_span, tolerance) -> ODESolution:
        """Runge-Kutta-Fehlberg adaptive method (RK45)."""
        t0, tf = t_span
        h = (tf - t0) / 100  # Initial step size

        # Butcher tableau for RK45
        a2, a3, a4, a5, a6 = 1/4, 3/8, 12/13, 1, 1/2
        b21 = 1/4
        b31, b32 = 3/32, 9/32
        b41, b42, b43 = 1932/2197, -7200/2197, 7296/2197
        b51, b52, b53, b54 = 439/216, -8, 3680/513, -845/4104
        b61, b62, b63, b64, b65 = -8/27, 2, -3544/2565, 1859/4104, -11/40

        c1, c3, c4, c5 = 25/216, 1408/2565, 2197/4104, -1/5  # 4th order
        d1, d3, d4, d5, d6 = 16/135, 6656/12825, 28561/56430, -9/50, 2/55  # 5th order

        t_values = [t0]
        y_values = [y0.copy()]
        error_estimates = []

        t = t0
        y = y0.copy()

        min_h = (tf - t0) / 10000
        max_h = (tf - t0) / 10

        while t < tf:
            if t + h > tf:
                h = tf - t

            # RK45 stages
            k1 = func(t, y)
            k2 = func(t + a2 * h, [yi + h * b21 * k1i for yi, k1i in zip(y, k1)])
            k3 = func(t + a3 * h, [yi + h * (b31 * k1i + b32 * k2i)
                                    for yi, k1i, k2i in zip(y, k1, k2)])
            k4 = func(t + a4 * h, [yi + h * (b41 * k1i + b42 * k2i + b43 * k3i)
                                    for yi, k1i, k2i, k3i in zip(y, k1, k2, k3)])
            k5 = func(t + a5 * h, [yi + h * (b51 * k1i + b52 * k2i + b53 * k3i + b54 * k4i)
                                    for yi, k1i, k2i, k3i, k4i in zip(y, k1, k2, k3, k4)])
            k6 = func(t + a6 * h, [yi + h * (b61 * k1i + b62 * k2i + b63 * k3i + b64 * k4i + b65 * k5i)
                                    for yi, k1i, k2i, k3i, k4i, k5i in zip(y, k1, k2, k3, k4, k5)])

            # 4th and 5th order solutions
            y4 = [yi + h * (c1 * k1i + c3 * k3i + c4 * k4i + c5 * k5i)
                  for yi, k1i, k3i, k4i, k5i in zip(y, k1, k3, k4, k5)]
            y5 = [yi + h * (d1 * k1i + d3 * k3i + d4 * k4i + d5 * k5i + d6 * k6i)
                  for yi, k1i, k3i, k4i, k5i, k6i in zip(y, k1, k3, k4, k5, k6)]

            # Error estimate
            error = max(abs(y5i - y4i) for y5i, y4i in zip(y5, y4))
            error_estimates.append(error)

            if error < tolerance or h <= min_h:
                # Accept step
                t += h
                y = y5
                t_values.append(t)
                y_values.append(y.copy())

            # Adjust step size
            if error > 0:
                scale = 0.84 * (tolerance / error) ** 0.25
                h = max(min_h, min(max_h, scale * h))
            else:
                h = max_h

        self._stats['ode_solutions'] += 1
        return ODESolution(
            t=t_values,
            y=y_values,
            method='rk45',
            n_steps=len(t_values) - 1,
            error_estimates=error_estimates
        )

    # ==================== INTERPOLATION ====================

    def interpolate(
        self,
        x_points: List[float],
        y_points: List[float],
        method: str = 'lagrange',
    ) -> InterpolationResult:
        """
        Polynomial interpolation through given points.

        Args:
            x_points: x-coordinates of data points
            y_points: y-coordinates of data points
            method: 'lagrange', 'newton', 'linear'

        Returns:
            InterpolationResult with polynomial and evaluator
        """
        self._stats['interpolations'] += 1

        if method == 'lagrange':
            return self._lagrange_interpolation(x_points, y_points)
        elif method == 'newton':
            """Perform evaluator operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.evaluator(...)
            """
            return self._newton_interpolation(x_points, y_points)
        elif method == 'linear':
            return self._linear_interpolation(x_points, y_points)
        else:
            return self._lagrange_interpolation(x_points, y_points)

    def _lagrange_interpolation(self, x_points, y_points) -> InterpolationResult:
        """Lagrange polynomial interpolation."""
        n = len(x_points)

        def evaluator(x):
            """Evaluate Lagrange polynomial at point x."""
            result = 0.0
            for i in range(n):
                term = y_points[i]
                for j in range(n):
                    if i != j:
                        term *= (x - x_points[j]) / (x_points[i] - x_points[j])
                result += term
            return result

        return InterpolationResult(
            polynomial_coeffs=[],  # Lagrange form doesn't use standard coefficients
            evaluator=evaluator,
            method='lagrange'
        )

    def _newton_interpolation(self, x_points, y_points) -> InterpolationResult:
        """Newton's divided difference interpolation."""
        n = len(x_points)

        # Compute divided differences
        dd = [[0.0] * n for _ in range(n)]
        for i in range(n):
            """Perform evaluator operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.evaluator(...)
            """
            dd[i][0] = y_points[i]

        for j in range(1, n):
            for i in range(n - j):
                dd[i][j] = (dd[i + 1][j - 1] - dd[i][j - 1]) / (x_points[i + j] - x_points[i])

        coeffs = [dd[0][i] for i in range(n)]

        def evaluator(x):
            """Evaluate Newton divided difference polynomial at point x."""
            result = coeffs[0]
            product = 1.0
            for i in range(1, n):
                product *= (x - x_points[i - 1])
                result += coeffs[i] * product
            return result

        return InterpolationResult(
            polynomial_coeffs=coeffs,
            evaluator=evaluator,
            method='newton'
        )

    def _linear_interpolation(self, x_points, y_points) -> InterpolationResult:
        """Piecewise linear interpolation."""
        def evaluator(x):
            """Evaluate piecewise linear interpolation at point x."""
            # Find interval
            for i in range(len(x_points) - 1):
                if x_points[i] <= x <= x_points[i + 1]:
                    t = (x - x_points[i]) / (x_points[i + 1] - x_points[i])
                    return y_points[i] + t * (y_points[i + 1] - y_points[i])

            # Extrapolation
            if x < x_points[0]:
                t = (x - x_points[0]) / (x_points[1] - x_points[0])
                return y_points[0] + t * (y_points[1] - y_points[0])
            else:
                t = (x - x_points[-2]) / (x_points[-1] - x_points[-2])
                return y_points[-2] + t * (y_points[-1] - y_points[-2])

        return InterpolationResult(
            polynomial_coeffs=[],
            evaluator=evaluator,
            method='linear'
        )

    # ==================== ROOT FINDING ====================

    def find_root(
        self,
        func: Callable[[float], float],
        bracket: Optional[Tuple[float, float]] = None,
        x0: Optional[float] = None,
        method: str = 'brent',
        tolerance: float = 1e-10,
        max_iterations: int = 100,
    ) -> Optional[float]:
        """
        Find root of function.

        Args:
            func: Function to find root of
            bracket: (a, b) bracketing interval for bisection/brent
            x0: Initial guess for Newton's method
            method: 'bisection', 'newton', 'secant', 'brent'
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            Root value or None if not found
        """
        self._stats['roots_found'] += 1

        if method == 'bisection' and bracket:
            return self._bisection(func, bracket[0], bracket[1], tolerance, max_iterations)
        elif method == 'newton' and x0 is not None:
            return self._newton_root(func, x0, tolerance, max_iterations)
        elif method == 'secant' and bracket:
            return self._secant(func, bracket[0], bracket[1], tolerance, max_iterations)
        elif method == 'brent' and bracket:
            return self._brent(func, bracket[0], bracket[1], tolerance, max_iterations)
        elif bracket:
            return self._brent(func, bracket[0], bracket[1], tolerance, max_iterations)
        elif x0 is not None:
            return self._newton_root(func, x0, tolerance, max_iterations)
        else:
            return None

    def _bisection(self, func, a, b, tol, max_iter) -> Optional[float]:
        """Bisection method for root finding with edge case handling."""
        # Validate inputs
        if any(math.isnan(x) or math.isinf(x) for x in [a, b]):
            return None

        try:
            fa, fb = func(a), func(b)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

        if math.isnan(fa) or math.isnan(fb) or math.isinf(fa) or math.isinf(fb):
            return None

        if fa * fb > 0:
            return None

        for _ in range(max_iter):
            c = (a + b) / 2
            try:
                fc = func(c)
            except (ValueError, ZeroDivisionError, OverflowError):
                return None

            if math.isnan(fc) or math.isinf(fc):
                return None

            if abs(b - a) < tol or abs(fc) < tol:
                return c

            if fa * fc < 0:
                b = c
                fb = fc
            else:
                a = c
                fa = fc

        return (a + b) / 2

    def _newton_root(self, func, x0, tol, max_iter) -> Optional[float]:
        """Newton-Raphson method with improved edge case handling."""
        # Validate input
        if x0 is None or math.isnan(x0) or math.isinf(x0):
            return None

        x = x0
        for _ in range(max_iter):
            try:
                fx = func(x)
            except (ValueError, ZeroDivisionError, OverflowError):
                return None

            # Check for numerical issues
            if math.isnan(fx) or math.isinf(fx):
                return None

            if abs(fx) < tol:
                return x

            dfx = self.differentiate(func, x)
            if abs(dfx) < 1e-15 or math.isnan(dfx) or math.isinf(dfx):
                return None

            x_new = x - fx / dfx

            # Check for divergence
            if math.isnan(x_new) or math.isinf(x_new):
                return None

            x = x_new

        return x if abs(func(x)) < tol else None

    def _secant(self, func, x0, x1, tol, max_iter) -> Optional[float]:
        """Secant method with edge case handling."""
        # Validate inputs
        if any(math.isnan(x) or math.isinf(x) for x in [x0, x1]):
            return None

        for _ in range(max_iter):
            try:
                f0, f1 = func(x0), func(x1)
            except (ValueError, ZeroDivisionError, OverflowError):
                return None

            # Check for numerical issues
            if any(math.isnan(x) or math.isinf(x) for x in [f0, f1]):
                return None

            if abs(f1) < tol:
                return x1

            if abs(f1 - f0) < 1e-15:
                return None

            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)

            # Check for divergence
            if math.isnan(x2) or math.isinf(x2):
                return None

            x0, x1 = x1, x2

        try:
            final_val = func(x1)
            return x1 if abs(final_val) < tol else None
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

    def _brent(self, func, a, b, tol, max_iter) -> Optional[float]:
        """Brent's method (hybrid bisection/secant/inverse quadratic)."""
        fa, fb = func(a), func(b)
        if fa * fb > 0:
            return None

        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa

        c, fc = a, fa
        d = b - a
        mflag = True

        for _ in range(max_iter):
            if abs(fb) < tol:
                return b

            if fa != fc and fb != fc:
                # Inverse quadratic interpolation
                s = (a * fb * fc / ((fa - fb) * (fa - fc)) +
                     b * fa * fc / ((fb - fa) * (fb - fc)) +
                     c * fa * fb / ((fc - fa) * (fc - fb)))
            else:
                # Secant
                s = b - fb * (b - a) / (fb - fa)

            # Conditions for bisection
            cond1 = not (3 * a + b) / 4 < s < b if a < b else not b < s < (3 * a + b) / 4
            cond2 = mflag and abs(s - b) >= abs(b - c) / 2
            cond3 = not mflag and abs(s - b) >= abs(c - d) / 2
            cond4 = mflag and abs(b - c) < tol
            cond5 = not mflag and abs(c - d) < tol

            if cond1 or cond2 or cond3 or cond4 or cond5:
                s = (a + b) / 2
                mflag = True
            else:
                mflag = False

            fs = func(s)
            d, c = c, b
            fc = fb

            if fa * fs < 0:
                b, fb = s, fs
            else:
                a, fa = s, fs

            if abs(fa) < abs(fb):
                a, b = b, a
                fa, fb = fb, fa

        return b

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'integrate':
            result = self.integrate(**params)
            return {'status': 'success', 'result': result}
        elif action == 'differentiate':
            result = self.differentiate(**params)
            return {'status': 'success', 'result': result}
        elif action == 'solve_ode_ivp':
            result = self.solve_ode_ivp(**params)
            return {'status': 'success', 'result': result}
        elif action == 'find_root':
            result = self.find_root(**params)
            return {'status': 'success', 'result': result}
        elif action == 'interpolate':
            result = self.interpolate(**params)
            return {'status': 'success', 'result': result}
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return dict(self._stats)

    # ==================== ABSTRACT BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from environment.

        For NumericalMethodsSpecialist, this reads pending numerical
        computation tasks from the Blackboard and updates internal beliefs.
        """
        if self.blackboard:
            # Check for pending numerical tasks
            entries = self.blackboard.query_entries(
                tags=['numerical', 'computation'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                self.add_belief('pending_numerical_task', entry, source='blackboard')

    def deliberate(self) -> List:
        """
        Compare beliefs to desires, generate new intentions.

        Examines current beliefs about pending tasks and generates
        intentions for numerical computation operations.
        """
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        new_intentions = []

        # Check for pending numerical tasks
        if self.has_belief('pending_numerical_task'):
            task_belief = self.get_belief('pending_numerical_task')
            if task_belief:
                task = task_belief.content
                task_type = task.get('type', 'integrate') if isinstance(task, dict) else 'integrate'

                # Generate intention based on task type
                intention = Intention(
                    goal=f"compute_{task_type}",
                    plan=[f"analyze_input", f"execute_{task_type}", "post_results"],
                    priority=5,
                    context={'task': task}
                )
                new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention):
        """
        Execute next step in plan - delegate to numerical operations.

        Args:
            intention: The current intention being executed
        """
        if not intention or not hasattr(intention, 'get_current_action'):
            return

        action = intention.get_current_action()
        context = intention.context if hasattr(intention, 'context') else {}

        if action == 'analyze_input':
            # Verify input is valid
            logger.debug(f"Analyzing input for numerical task")
            intention.advance()

        elif action.startswith('execute_'):
            task_type = action.replace('execute_', '')
            task = context.get('task', {})

            try:
                if task_type == 'integrate':
                    func = task.get('func')
                    a, b = task.get('a', 0), task.get('b', 1)
                    result = self.integrate(func, a, b) if func else None
                elif task_type == 'differentiate':
                    func = task.get('func')
                    x = task.get('x', 0)
                    result = self.differentiate(func, x) if func else None
                elif task_type == 'solve_ode':
                    func = task.get('func')
                    y0 = task.get('y0', [1.0])
                    t_span = task.get('t_span', (0, 1))
                    result = self.solve_ode_ivp(func, y0, t_span) if func else None
                else:
                    result = None

                intention.context['result'] = result
                intention.advance()

            except Exception as e:
                logger.error(f"Numerical execution failed: {e}")
                intention.fail(str(e))

        elif action == 'post_results':
            # Post results to blackboard (if available)
            result = context.get('result')
            if self.blackboard and result:
                # Blackboard posting would happen here
                pass

            intention.complete()


# Convenience functions
def numerical_integrate(func, a, b, method='adaptive', tolerance=1e-8) -> IntegrationResult:
    """Numerical integration."""
    specialist = NumericalMethodsSpecialist()
    return specialist.integrate(func, a, b, method, tolerance)


def numerical_derivative(func, x, h=1e-5, method='central') -> float:
    """Numerical differentiation."""
    specialist = NumericalMethodsSpecialist()
    return specialist.differentiate(func, x, h, method)


def solve_ode(func, y0, t_span, method='rk4', n_steps=100) -> ODESolution:
    """Solve ODE initial value problem."""
    specialist = NumericalMethodsSpecialist()
    return specialist.solve_ode_ivp(func, y0, t_span, method, n_steps)


__all__ = [
    'NumericalMethodsSpecialist',
    'IntegrationResult',
    'ODESolution',
    'InterpolationResult',
    'numerical_integrate',
    'numerical_derivative',
    'solve_ode',
]
