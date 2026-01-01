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
Contour Integration Specialist
================================

Provides comprehensive complex line integral operations:
- Path parameterization
- Numerical contour integration
- Standard contours (circles, rectangles, arcs)
- Path concatenation and manipulation
- Cauchy integral formula applications

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field


@dataclass
class Contour:
    """
    Parameterized contour in the complex plane.

    Represents gamma: [a, b] -> C
    """
    parametrization: Callable[[float], complex]
    t_start: float = 0.0
    t_end: float = 1.0
    name: str = "contour"
    is_closed: bool = False

    def __call__(self, t: float) -> complex:
        """Evaluate contour at parameter t."""
        return self.parametrization(t)

    def derivative(self, t: float, h: float = 1e-8) -> complex:
        """Compute dz/dt at parameter t."""
        return (self.parametrization(t + h) - self.parametrization(t - h)) / (2 * h)

    def reverse(self) -> 'Contour':
        """Return reversed contour."""
        def rev_param(t):
            """Perform rev param operation.

            Args:
            t: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.rev_param(...)
            """
            s = self.t_end - (t - self.t_start)
            return self.parametrization(s)

        return Contour(
            parametrization=rev_param,
            t_start=self.t_start,
            t_end=self.t_end,
            name=f"-{self.name}",
            is_closed=self.is_closed
        )


@dataclass
class ContourIntegralResult:
    """Result from contour integration."""
    value: complex
    error_estimate: float = 0.0
    n_evaluations: int = 0
    method: str = "trapezoidal"
    converged: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


class ContourIntegrationSpecialist:
    """
    BDI Agent for complex contour integration.

    Capabilities:
    - Build standard contours
    - Numerical integration along paths
    - Cauchy integral formula
    - Path manipulation (concatenation, subdivision)
    - Adaptive quadrature for contour integrals
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._default_n_points = 1000
        self._epsilon = 1e-12

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "function" in self.beliefs and "contour" in self.beliefs:
            self.desires.append("integrate")
        if "cauchy_point" in self.beliefs:
            self.desires.append("cauchy_formula")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "integrate":
            f = self.beliefs.get("function")
            contour = self.beliefs.get("contour")
            return {"result": self.integrate(f, contour)}
        elif goal == "cauchy_formula":
            f = self.beliefs.get("function")
            z0 = self.beliefs.get("cauchy_point")
            contour = self.beliefs.get("contour")
            n = self.beliefs.get("derivative_order", 0)
            return {"result": self.cauchy_integral_formula(f, z0, contour, n)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Contour Construction ==========

    def circle(
        self,
        center: complex = 0,
        radius: float = 1.0,
        orientation: int = 1
    ) -> Contour:
        """
        Create circular contour.

        Args:
            center: Circle center
            radius: Circle radius
            orientation: 1 for counterclockwise, -1 for clockwise

        Returns:
            Circular Contour
        """
        def param(t):
            """Perform param operation.

            Args:
            t: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.param(...)
            """
            theta = 2 * np.pi * t * orientation
            return center + radius * np.exp(1j * theta)

        return Contour(
            parametrization=param,
            t_start=0,
            t_end=1,
            name=f"circle(center={center}, r={radius})",
            is_closed=True
        )

    def arc(
        self,
        center: complex,
        radius: float,
        theta_start: float,
        theta_end: float
    ) -> Contour:
        """
        Create circular arc contour.

        Args:
            center: Arc center
            radius: Arc radius
            theta_start: Starting angle (radians)
            theta_end: Ending angle (radians)

        Returns:
            Arc Contour
        """
        def param(t):
            """Perform param operation.

            Args:
            t: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.param(...)
            """
            theta = theta_start + t * (theta_end - theta_start)
            return center + radius * np.exp(1j * theta)

        return Contour(
            parametrization=param,
            t_start=0,
            t_end=1,
            name=f"arc({theta_start} to {theta_end})",
            is_closed=False
        )

    def line_segment(
        self,
        z_start: complex,
        z_end: complex
    ) -> Contour:
        """
        Create line segment contour.

        Args:
            z_start: Starting point
            z_end: Ending point

        Returns:
            Line segment Contour
        """
        def param(t):
            """Perform param operation.

            Args:
            t: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.param(...)
            """
            return z_start + t * (z_end - z_start)

        return Contour(
            parametrization=param,
            t_start=0,
            t_end=1,
            name=f"line({z_start} to {z_end})",
            is_closed=False
        )

    def rectangle(
        self,
        z_min: complex,
        z_max: complex,
        orientation: int = 1
    ) -> Contour:
        """
        Create rectangular contour.

        Args:
            z_min: Bottom-left corner
            z_max: Top-right corner
            orientation: 1 for counterclockwise

        Returns:
            Rectangular Contour
        """
        x1, y1 = z_min.real, z_min.imag
        x2, y2 = z_max.real, z_max.imag

        corners = [
            complex(x1, y1),
            complex(x2, y1),
            complex(x2, y2),
            complex(x1, y2),
            complex(x1, y1)
        ]

        if orientation < 0:
            corners = corners[::-1]

        def param(t):
            """Perform param operation.

            Args:
            t: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.param(...)
            """
            # t in [0, 1] maps to 4 sides
            side = int(t * 4) % 4
            local_t = (t * 4) % 1

            z_start = corners[side]
            z_end = corners[side + 1]

            return z_start + local_t * (z_end - z_start)

        return Contour(
            parametrization=param,
            t_start=0,
            t_end=1,
            name=f"rectangle({z_min} to {z_max})",
            is_closed=True
        )

    def semicircle(
        self,
        center: complex,
        radius: float,
        upper: bool = True
    ) -> Contour:
        """
        Create semicircular contour (typically for real line integrals).

        Args:
            center: Center point on real axis
            radius: Semicircle radius
            upper: True for upper half-plane

        Returns:
            Semicircular Contour
        """
        theta_start = 0 if upper else np.pi
        theta_end = np.pi if upper else 2 * np.pi

        return self.arc(center, radius, theta_start, theta_end)

    def keyhole(
        self,
        outer_radius: float,
        inner_radius: float = 0.01,
        branch_angle: float = 0.01
    ) -> Contour:
        """
        Create keyhole contour for branch cuts.

        Consists of:
        - Large circle (outer)
        - Line above branch cut (going in)
        - Small circle around origin
        - Line below branch cut (going out)

        Args:
            outer_radius: Outer circle radius
            inner_radius: Inner circle radius
            branch_angle: Small angle for branch cut gap

        Returns:
            Keyhole Contour
        """
        def param(t):
            """Perform param operation.

            Args:
            t: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.param(...)
            """
            if t < 0.25:
                # Outer circle (counterclockwise from branch_angle to 2*pi - branch_angle)
                s = t / 0.25
                theta = branch_angle + s * (2*np.pi - 2*branch_angle)
                return outer_radius * np.exp(1j * theta)

            elif t < 0.5:
                # Line above cut (from outer to inner)
                s = (t - 0.25) / 0.25
                r = outer_radius - s * (outer_radius - inner_radius)
                return r * np.exp(1j * branch_angle)

            elif t < 0.75:
                # Inner circle (clockwise)
                s = (t - 0.5) / 0.25
                theta = branch_angle - s * (2*np.pi - 2*branch_angle)
                return inner_radius * np.exp(1j * theta)

            else:
                # Line below cut (from inner to outer)
                s = (t - 0.75) / 0.25
                r = inner_radius + s * (outer_radius - inner_radius)
                return r * np.exp(-1j * branch_angle)

        return Contour(
            parametrization=param,
            t_start=0,
            t_end=1,
            name=f"keyhole(R={outer_radius}, r={inner_radius})",
            is_closed=True
        )

    def concatenate(self, contours: List[Contour]) -> Contour:
        """
        Concatenate multiple contours into one.

        Args:
            contours: List of contours to concatenate

        Returns:
            Combined Contour
        """
        n = len(contours)
        if n == 0:
            raise ValueError("Empty contour list")
        if n == 1:
            return contours[0]

        def param(t):
            """Perform param operation.

            Args:
            t: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.param(...)
            """
            # Find which contour we're in
            idx = int(t * n) % n
            local_t = (t * n) % 1

            c = contours[idx]
            s = c.t_start + local_t * (c.t_end - c.t_start)
            return c.parametrization(s)

        names = " + ".join(c.name for c in contours)
        is_closed = (
            contours[-1].is_closed or
            abs(contours[-1](contours[-1].t_end) - contours[0](contours[0].t_start)) < 1e-10
        )

        return Contour(
            parametrization=param,
            t_start=0,
            t_end=1,
            name=names,
            is_closed=is_closed
        )

    # ========== Integration Methods ==========

    def integrate(
        self,
        f: Callable[[complex], complex],
        contour: Contour,
        n_points: Optional[int] = None,
        adaptive: bool = False,
        tol: float = 1e-8
    ) -> ContourIntegralResult:
        """
        Compute contour integral of f along contour.

        integral(f(z) dz, gamma) = integral(f(gamma(t)) * gamma'(t) dt, [a,b])

        Args:
            f: Complex function
            contour: Integration path
            n_points: Number of sample points
            adaptive: Use adaptive quadrature
            tol: Tolerance for adaptive method

        Returns:
            ContourIntegralResult
        """
        if n_points is None:
            n_points = self._default_n_points

        if adaptive:
            return self._adaptive_integrate(f, contour, tol)

        return self._trapezoidal_integrate(f, contour, n_points)

    def _trapezoidal_integrate(
        self,
        f: Callable[[complex], complex],
        contour: Contour,
        n_points: int
    ) -> ContourIntegralResult:
        """Trapezoidal rule integration."""
        t_vals = np.linspace(contour.t_start, contour.t_end, n_points)
        dt = (contour.t_end - contour.t_start) / (n_points - 1)

        integral = 0j
        n_evals = 0

        for i in range(len(t_vals) - 1):
            t = t_vals[i]
            t_next = t_vals[i + 1]
            t_mid = (t + t_next) / 2

            z = contour(t_mid)
            dz = contour.derivative(t_mid)

            try:
                integral += f(z) * dz * dt
                n_evals += 1
            except:
                pass

        # Error estimate from Richardson extrapolation (rough)
        half_result = self._simple_integrate(f, contour, n_points // 2)
        error = abs(integral - half_result)

        return ContourIntegralResult(
            value=integral,
            error_estimate=error,
            n_evaluations=n_evals,
            method="trapezoidal"
        )

    def _simple_integrate(
        self,
        f: Callable[[complex], complex],
        contour: Contour,
        n_points: int
    ) -> complex:
        """Simple trapezoidal integration (helper)."""
        t_vals = np.linspace(contour.t_start, contour.t_end, n_points)
        dt = (contour.t_end - contour.t_start) / (n_points - 1)

        integral = 0j
        for i in range(len(t_vals) - 1):
            t_mid = (t_vals[i] + t_vals[i + 1]) / 2
            z = contour(t_mid)
            dz = contour.derivative(t_mid)
            try:
                integral += f(z) * dz * dt
            except:
                pass

        return integral

    def _adaptive_integrate(
        self,
        f: Callable[[complex], complex],
        contour: Contour,
        tol: float,
        max_depth: int = 20
    ) -> ContourIntegralResult:
        """Adaptive integration using recursive bisection."""

        def integrate_segment(t0, t1, depth, f_vals_cache):
            """Integrate over [t0, t1] with adaptive refinement."""
            t_mid = (t0 + t1) / 2
            dt = t1 - t0

            # Get or compute function values
            if t0 not in f_vals_cache:
                z0 = contour(t0)
                dz0 = contour.derivative(t0)
                try:
                    f_vals_cache[t0] = f(z0) * dz0
                except:
                    f_vals_cache[t0] = 0j

            if t1 not in f_vals_cache:
                z1 = contour(t1)
                dz1 = contour.derivative(t1)
                try:
                    f_vals_cache[t1] = f(z1) * dz1
                except:
                    f_vals_cache[t1] = 0j

            if t_mid not in f_vals_cache:
                z_mid = contour(t_mid)
                dz_mid = contour.derivative(t_mid)
                try:
                    f_vals_cache[t_mid] = f(z_mid) * dz_mid
                except:
                    f_vals_cache[t_mid] = 0j

            # Trapezoidal estimate
            I_trap = (f_vals_cache[t0] + f_vals_cache[t1]) * dt / 2

            # Simpson estimate
            I_simp = (f_vals_cache[t0] + 4*f_vals_cache[t_mid] + f_vals_cache[t1]) * dt / 6

            error = abs(I_simp - I_trap)

            if error < tol * dt or depth >= max_depth:
                return I_simp, error, 3

            # Refine
            I_left, err_left, n_left = integrate_segment(t0, t_mid, depth + 1, f_vals_cache)
            I_right, err_right, n_right = integrate_segment(t_mid, t1, depth + 1, f_vals_cache)

            return I_left + I_right, err_left + err_right, n_left + n_right

        cache = {}
        result, error, n_evals = integrate_segment(
            contour.t_start, contour.t_end, 0, cache
        )

        return ContourIntegralResult(
            value=result,
            error_estimate=error,
            n_evaluations=n_evals,
            method="adaptive_simpson",
            converged=error < tol
        )

    # ========== Cauchy Integral Formula ==========

    def cauchy_integral_formula(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        contour: Contour,
        n: int = 0
    ) -> complex:
        """
        Apply Cauchy integral formula or its derivatives.

        f(z0) = (1/2*pi*i) * integral(f(z)/(z-z0), C)
        f^(n)(z0) = (n!/2*pi*i) * integral(f(z)/(z-z0)^(n+1), C)

        Args:
            f: Analytic function inside contour
            z0: Point inside contour
            contour: Closed contour containing z0
            n: Derivative order (0 for f(z0), 1 for f'(z0), etc.)

        Returns:
            f^(n)(z0)
        """
        def integrand(z):
            """Perform integrand operation.

            Args:
            z: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.integrand(...)
            """
            return f(z) / (z - z0) ** (n + 1)

        result = self.integrate(integrand, contour)

        # Multiply by n! / (2*pi*i)
        factorial = 1
        for k in range(1, n + 1):
            factorial *= k

        return result.value * factorial / (2j * np.pi)

    def cauchy_derivative(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        n: int,
        radius: float = 0.1
    ) -> complex:
        """
        Compute n-th derivative using Cauchy integral formula.

        f^(n)(z0) = (n!/2*pi*i) * integral(f(z)/(z-z0)^(n+1), |z-z0|=r)

        Args:
            f: Analytic function
            z0: Point
            n: Derivative order
            radius: Contour radius

        Returns:
            n-th derivative at z0
        """
        contour = self.circle(z0, radius)
        return self.cauchy_integral_formula(f, z0, contour, n)

    # ========== Morera's Theorem Check ==========

    def morera_check(
        self,
        f: Callable[[complex], complex],
        region: Tuple[complex, complex],
        n_triangles: int = 10
    ) -> Dict[str, Any]:
        """
        Check Morera's theorem: f is analytic iff integral over all triangles is 0.

        Args:
            f: Function to check
            region: (z_min, z_max) rectangular region
            n_triangles: Number of random triangles to test

        Returns:
            Dictionary with results
        """
        z_min, z_max = region
        x_range = (z_min.real, z_max.real)
        y_range = (z_min.imag, z_max.imag)

        integrals = []
        max_integral = 0

        for _ in range(n_triangles):
            # Random triangle
            points = [
                complex(
                    np.random.uniform(*x_range),
                    np.random.uniform(*y_range)
                )
                for _ in range(3)
            ]

            # Close the triangle
            triangle = self.concatenate([
                self.line_segment(points[0], points[1]),
                self.line_segment(points[1], points[2]),
                self.line_segment(points[2], points[0])
            ])

            result = self.integrate(f, triangle)
            integrals.append(abs(result.value))
            max_integral = max(max_integral, abs(result.value))

        is_analytic = max_integral < 1e-6

        return {
            "is_analytic": is_analytic,
            "max_triangle_integral": max_integral,
            "mean_integral": np.mean(integrals),
            "n_triangles_tested": n_triangles,
            "interpretation": "Function appears analytic" if is_analytic else "Function may not be analytic"
        }

    # ========== Arc Length ==========

    def arc_length(
        self,
        contour: Contour,
        n_points: int = 1000
    ) -> float:
        """
        Compute arc length of contour.

        L = integral(|gamma'(t)|, [a,b])

        Args:
            contour: Path
            n_points: Integration points

        Returns:
            Arc length
        """
        t_vals = np.linspace(contour.t_start, contour.t_end, n_points)
        dt = (contour.t_end - contour.t_start) / (n_points - 1)

        length = 0
        for t in t_vals[:-1]:
            dz = contour.derivative(t + dt/2)
            length += abs(dz) * dt

        return length
