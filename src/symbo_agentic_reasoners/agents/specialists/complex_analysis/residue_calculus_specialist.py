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
Residue Calculus Specialist
============================

Provides comprehensive residue theorem operations:
- Residue computation at poles
- Contour integral evaluation via residue theorem
- Real integral evaluation using complex methods
- Winding number computation
- Argument principle applications

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class ContourType(Enum):
    """Types of integration contours."""
    CIRCLE = "circle"
    SEMICIRCLE_UPPER = "semicircle_upper"
    SEMICIRCLE_LOWER = "semicircle_lower"
    RECTANGLE = "rectangle"
    KEYHOLE = "keyhole"
    INDENTED = "indented"
    CUSTOM = "custom"


@dataclass
class Residue:
    """Residue at a pole."""
    point: complex
    value: complex
    order: int = 1
    method: str = "limit"


@dataclass
class ContourIntegralResult:
    """Result from contour integration."""
    value: complex
    method: str
    residues_used: List[Residue] = field(default_factory=list)
    poles_inside: List[complex] = field(default_factory=list)
    winding_numbers: Dict[complex, int] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RealIntegralResult:
    """Result from real integral via residues."""
    value: float
    original_integral: str
    method: str
    contour_used: ContourType
    residues_sum: complex
    details: Dict[str, Any] = field(default_factory=dict)


class ResidueCalculusSpecialist:
    """
    BDI Agent for residue calculus operations.

    Capabilities:
    - Compute residues at simple and higher-order poles
    - Apply residue theorem to contour integrals
    - Evaluate real integrals using complex analysis
    - Compute winding numbers
    - Handle various contour types
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._epsilon = 1e-10

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "poles" in self.beliefs:
            self.desires.append("compute_residues")
        if "contour" in self.beliefs:
            self.desires.append("contour_integral")
        if "real_integral" in self.beliefs:
            self.desires.append("real_via_residues")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "compute_residues":
            f = self.beliefs.get("function")
            poles = self.beliefs.get("poles", [])
            residues = [self.compute_residue(f, p) for p in poles]
            return {"result": residues}
        elif goal == "contour_integral":
            return {"result": self._handle_contour_integral()}

        return {"status": "unknown_goal", "goal": goal}

    def compute_residue(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        order: Optional[int] = None
    ) -> Residue:
        """
        Compute residue of f at pole z0.

        For simple pole: Res(f, z0) = lim(z→z0) (z-z0)f(z)
        For pole of order n: Res(f, z0) = (1/(n-1)!) * lim(z→z0) d^(n-1)/dz^(n-1)[(z-z0)^n f(z)]

        Args:
            f: Complex function
            z0: Pole location
            order: Pole order (auto-detected if None)

        Returns:
            Residue object
        """
        # Auto-detect pole order if not provided
        if order is None:
            order = self._detect_pole_order(f, z0)

        if order == 0:
            # Not a pole
            return Residue(point=z0, value=0j, order=0, method="not_a_pole")

        if order == 1:
            # Simple pole: Res = lim(z→z0) (z-z0)f(z)
            residue = self._simple_pole_residue(f, z0)
            return Residue(point=z0, value=residue, order=1, method="simple_limit")

        # Higher order pole
        residue = self._higher_order_residue(f, z0, order)
        return Residue(point=z0, value=residue, order=order, method="derivative_formula")

    def _detect_pole_order(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        max_order: int = 10
    ) -> int:
        """Detect the order of pole at z0."""
        h = 1e-5

        for n in range(max_order + 1):
            # Test if (z-z0)^n * f(z) has a finite nonzero limit
            values = []
            for theta in [0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3]:
                z = z0 + h * np.exp(1j * theta)
                try:
                    val = (z - z0) ** n * f(z)
                    if np.isfinite(val.real) and np.isfinite(val.imag):
                        values.append(val)
                except:
                    pass

            if values:
                mean_val = np.mean(values)
                std_val = np.std(np.abs(values))

                # Check convergence to nonzero value
                if abs(mean_val) > 1e-10 and std_val < abs(mean_val) * 0.1:
                    return n

        return 0  # Not a pole or essential singularity

    def _simple_pole_residue(
        self,
        f: Callable[[complex], complex],
        z0: complex
    ) -> complex:
        """Compute residue at simple pole."""
        h_values = [1e-4, 1e-5, 1e-6]
        estimates = []

        for h in h_values:
            values = []
            for theta in np.linspace(0, 2*np.pi, 8, endpoint=False):
                z = z0 + h * np.exp(1j * theta)
                try:
                    val = (z - z0) * f(z)
                    if np.isfinite(val.real) and np.isfinite(val.imag):
                        values.append(val)
                except:
                    pass

            if values:
                estimates.append(np.mean(values))

        if estimates:
            return np.mean(estimates)
        return complex(np.nan, np.nan)

    def _higher_order_residue(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        order: int
    ) -> complex:
        """
        Compute residue at pole of order n.

        Res(f, z0) = (1/(n-1)!) * d^(n-1)/dz^(n-1)[(z-z0)^n f(z)] |_{z=z0}
        """
        def g(z):
            """Perform g operation.

            Args:
            z: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.g(...)
            """
            return (z - z0) ** order * f(z)

        # Compute (n-1)th derivative at z0
        h = 1e-4
        deriv = self._numerical_derivative(g, z0, order - 1, h)

        # Divide by (n-1)!
        factorial = 1
        for k in range(1, order):
            factorial *= k

        return deriv / factorial

    def _numerical_derivative(
        self,
        f: Callable[[complex], complex],
        z: complex,
        order: int,
        h: float
    ) -> complex:
        """Compute numerical derivative using central differences."""
        if order == 0:
            return f(z)

        if order == 1:
            return (f(z + h) - f(z - h)) / (2 * h)

        # Higher order via recursion
        return (
            self._numerical_derivative(f, z + h, order - 1, h) -
            self._numerical_derivative(f, z - h, order - 1, h)
        ) / (2 * h)

    def contour_integral_circle(
        self,
        f: Callable[[complex], complex],
        center: complex,
        radius: float,
        poles: Optional[List[complex]] = None,
        use_residue_theorem: bool = True
    ) -> ContourIntegralResult:
        """
        Compute contour integral around circle.

        By residue theorem: integral(f, C) = 2*pi*i * sum(Res(f, z_k) * n(C, z_k))

        Args:
            f: Complex function
            center: Circle center
            radius: Circle radius
            poles: Known poles (auto-detected if None)
            use_residue_theorem: Use residue theorem if True

        Returns:
            ContourIntegralResult
        """
        # Find poles inside contour
        if poles is None:
            poles = self._find_poles_in_region(f, center, radius)

        poles_inside = [p for p in poles if abs(p - center) < radius]

        if use_residue_theorem and poles_inside:
            # Compute residues and apply theorem
            residues = []
            total = 0j

            for pole in poles_inside:
                res = self.compute_residue(f, pole)
                residues.append(res)
                total += res.value

            result = 2j * np.pi * total

            return ContourIntegralResult(
                value=result,
                method="residue_theorem",
                residues_used=residues,
                poles_inside=poles_inside,
                winding_numbers={p: 1 for p in poles_inside}
            )

        # Direct numerical integration
        n_points = 1000
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        dtheta = 2 * np.pi / n_points

        integral = 0j
        for t in theta:
            z = center + radius * np.exp(1j * t)
            dz = 1j * radius * np.exp(1j * t)
            try:
                integral += f(z) * dz
            except:
                pass

        integral *= dtheta

        return ContourIntegralResult(
            value=integral,
            method="numerical",
            poles_inside=poles_inside
        )

    def _find_poles_in_region(
        self,
        f: Callable[[complex], complex],
        center: complex,
        radius: float,
        grid_size: int = 20
    ) -> List[complex]:
        """Find poles of f inside a circular region."""
        poles = []

        # Grid search
        for r in np.linspace(0, radius * 0.95, grid_size // 2):
            for theta in np.linspace(0, 2*np.pi, grid_size, endpoint=False):
                z = center + r * np.exp(1j * theta)
                try:
                    val = f(z)
                    if abs(val) > 1e10:
                        # Potential pole, refine
                        pole = self._refine_pole(f, z)
                        if pole is not None and abs(pole - center) < radius:
                            # Check if new
                            is_new = all(abs(pole - p) > 1e-6 for p in poles)
                            if is_new:
                                poles.append(pole)
                except (ZeroDivisionError, OverflowError):
                    pole = self._refine_pole(f, z)
                    if pole is not None and abs(pole - center) < radius:
                        is_new = all(abs(pole - p) > 1e-6 for p in poles)
                        if is_new:
                            poles.append(pole)

        return poles

    def _refine_pole(
        self,
        f: Callable[[complex], complex],
        z_approx: complex,
        max_iter: int = 20
    ) -> Optional[complex]:
        """Refine pole location using Newton's method on 1/f."""
        z = z_approx
        h = 1e-8

        for _ in range(max_iter):
            try:
                # Newton on g(z) = 1/f(z) to find its zeros
                g = 1 / f(z)
                g_prime = (1/f(z + h) - 1/f(z - h)) / (2 * h)

                if abs(g_prime) < 1e-15:
                    break

                z_new = z - g / g_prime

                if abs(z_new - z) < 1e-12:
                    return z_new

                z = z_new

            except:
                return z

        return z

    def winding_number(
        self,
        contour: Callable[[float], complex],
        point: complex,
        t_range: Tuple[float, float] = (0, 1)
    ) -> int:
        """
        Compute winding number of contour around point.

        n(C, z0) = (1/2*pi*i) * integral(1/(z-z0) dz, C)

        Args:
            contour: Parameterized contour gamma(t)
            point: Point to compute winding around
            t_range: Parameter range

        Returns:
            Winding number (integer)
        """
        t0, t1 = t_range
        n_points = 1000
        t_vals = np.linspace(t0, t1, n_points)
        dt = (t1 - t0) / n_points

        integral = 0j
        for i in range(len(t_vals) - 1):
            t = t_vals[i]
            z = contour(t)
            # Approximate dz/dt
            dz = (contour(t + dt/2) - contour(t - dt/2)) / dt

            try:
                integral += dz / (z - point)
            except:
                pass

        integral *= dt
        winding = integral / (2j * np.pi)

        # Should be an integer
        return int(round(winding.real))

    def real_integral_via_residues(
        self,
        integrand_str: str,
        f: Callable[[complex], complex],
        bounds: Tuple[float, float],
        poles: List[complex],
        contour_type: ContourType = ContourType.SEMICIRCLE_UPPER
    ) -> RealIntegralResult:
        """
        Evaluate real integral using residue theorem.

        Common techniques:
        - Semicircle in upper/lower half-plane for rational functions
        - Keyhole contour for branch cuts
        - Indented contour for poles on real axis

        Args:
            integrand_str: String description of integrand
            f: Complex extension of integrand
            bounds: Integration bounds (a, b) or (-inf, inf)
            poles: Known poles
            contour_type: Type of contour to use

        Returns:
            RealIntegralResult
        """
        a, b = bounds

        if contour_type == ContourType.SEMICIRCLE_UPPER:
            return self._semicircle_method(integrand_str, f, poles, upper=True)
        elif contour_type == ContourType.SEMICIRCLE_LOWER:
            return self._semicircle_method(integrand_str, f, poles, upper=False)
        elif contour_type == ContourType.KEYHOLE:
            return self._keyhole_method(integrand_str, f, poles, bounds)
        elif contour_type == ContourType.INDENTED:
            return self._indented_method(integrand_str, f, poles, bounds)

        # Default to direct numerical integration
        return self._direct_integration(integrand_str, f, bounds)

    def _semicircle_method(
        self,
        integrand_str: str,
        f: Callable[[complex], complex],
        poles: List[complex],
        upper: bool = True
    ) -> RealIntegralResult:
        """
        Semicircle contour for integrals from -inf to inf.

        For f(x) rational with deg(denom) >= deg(numer) + 2:
        integral(-inf, inf, f(x)dx) = 2*pi*i * sum(residues in upper half-plane)
        """
        # Filter poles in appropriate half-plane
        if upper:
            relevant_poles = [p for p in poles if p.imag > 0]
        else:
            relevant_poles = [p for p in poles if p.imag < 0]

        # Sum residues
        residues = []
        total_residue = 0j

        for pole in relevant_poles:
            res = self.compute_residue(f, pole)
            residues.append(res)
            total_residue += res.value

        # Apply residue theorem
        if upper:
            result = 2j * np.pi * total_residue
        else:
            result = -2j * np.pi * total_residue

        return RealIntegralResult(
            value=result.real,
            original_integral=integrand_str,
            method="semicircle_residue",
            contour_used=ContourType.SEMICIRCLE_UPPER if upper else ContourType.SEMICIRCLE_LOWER,
            residues_sum=total_residue,
            details={
                "poles_used": [r.point for r in residues],
                "residues": [(r.point, r.value) for r in residues]
            }
        )

    def _keyhole_method(
        self,
        integrand_str: str,
        f: Callable[[complex], complex],
        poles: List[complex],
        bounds: Tuple[float, float]
    ) -> RealIntegralResult:
        """
        Keyhole contour for branch cuts (typically along positive real axis).

        Used for integrals like integral(0, inf, x^a * f(x) dx) where a is not integer.
        """
        # This is a complex method that depends on the specific integrand
        # For now, provide numerical approximation

        a, b = bounds
        if b == float('inf'):
            b = 1000  # Truncate

        n_points = 10000
        x = np.linspace(a + 1e-10, b, n_points)
        dx = (b - a) / n_points

        integral = 0
        for xi in x:
            try:
                integral += f(xi).real * dx
            except:
                pass

        return RealIntegralResult(
            value=integral,
            original_integral=integrand_str,
            method="keyhole_numerical",
            contour_used=ContourType.KEYHOLE,
            residues_sum=0j,
            details={"note": "Numerical approximation used"}
        )

    def _indented_method(
        self,
        integrand_str: str,
        f: Callable[[complex], complex],
        poles: List[complex],
        bounds: Tuple[float, float]
    ) -> RealIntegralResult:
        """
        Indented contour for poles on the real axis.

        The contour makes small semicircular indentations around real poles.
        """
        real_poles = [p for p in poles if abs(p.imag) < 1e-10]
        upper_poles = [p for p in poles if p.imag > 0]

        # Contribution from upper half-plane poles
        residues = []
        total = 0j

        for pole in upper_poles:
            res = self.compute_residue(f, pole)
            residues.append(res)
            total += res.value

        # Contribution from real axis poles (half residue for each)
        for pole in real_poles:
            res = self.compute_residue(f, pole)
            residues.append(res)
            total += 0.5 * res.value  # Half because of semicircle indentation

        result = 2j * np.pi * total

        return RealIntegralResult(
            value=result.real,
            original_integral=integrand_str,
            method="indented_contour",
            contour_used=ContourType.INDENTED,
            residues_sum=total,
            details={
                "real_poles": real_poles,
                "upper_poles": upper_poles
            }
        )

    def _direct_integration(
        self,
        integrand_str: str,
        f: Callable[[complex], complex],
        bounds: Tuple[float, float]
    ) -> RealIntegralResult:
        """Direct numerical integration as fallback."""
        a, b = bounds

        if a == float('-inf'):
            a = -1000
        if b == float('inf'):
            b = 1000

        n_points = 10000
        x = np.linspace(a, b, n_points)
        dx = (b - a) / n_points

        integral = 0
        for xi in x:
            try:
                integral += f(xi).real * dx
            except:
                pass

        return RealIntegralResult(
            value=integral,
            original_integral=integrand_str,
            method="direct_numerical",
            contour_used=ContourType.CUSTOM,
            residues_sum=0j
        )

    def argument_principle(
        self,
        f: Callable[[complex], complex],
        contour: Callable[[float], complex],
        t_range: Tuple[float, float] = (0, 1)
    ) -> Dict[str, Any]:
        """
        Apply argument principle to count zeros and poles.

        (1/2*pi*i) * integral(f'/f, C) = Z - P

        where Z = number of zeros inside C, P = number of poles.

        Args:
            f: Meromorphic function
            contour: Parameterized contour
            t_range: Parameter range

        Returns:
            Dictionary with zeros minus poles count
        """
        t0, t1 = t_range
        n_points = 1000
        t_vals = np.linspace(t0, t1, n_points)
        dt = (t1 - t0) / n_points
        h = 1e-8

        integral = 0j
        for t in t_vals[:-1]:
            z = contour(t)
            dz = (contour(t + dt/2) - contour(t - dt/2)) / dt

            try:
                f_z = f(z)
                f_prime_z = (f(z + h) - f(z - h)) / (2 * h)

                if abs(f_z) > 1e-15:
                    integral += (f_prime_z / f_z) * dz
            except:
                pass

        integral *= dt
        Z_minus_P = integral / (2j * np.pi)

        return {
            "zeros_minus_poles": int(round(Z_minus_P.real)),
            "raw_integral": integral,
            "interpretation": f"Number of zeros minus poles inside contour: {int(round(Z_minus_P.real))}"
        }

    def _handle_contour_integral(self) -> ContourIntegralResult:
        """Handle contour integral from beliefs."""
        f = self.beliefs.get("function")
        contour = self.beliefs.get("contour")
        poles = self.beliefs.get("poles", [])

        if isinstance(contour, dict):
            if contour.get("type") == "circle":
                return self.contour_integral_circle(
                    f,
                    contour["center"],
                    contour["radius"],
                    poles
                )

        return ContourIntegralResult(
            value=complex(np.nan),
            method="unsupported_contour"
        )
