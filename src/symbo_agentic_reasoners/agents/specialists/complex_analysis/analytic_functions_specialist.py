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
Analytic Functions Specialist
==============================

Provides comprehensive complex analytic function operations:
- Cauchy-Riemann equation verification
- Analytic continuation
- Power series representation
- Singularity classification
- Laurent series expansion
- Zeros and poles detection

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class SingularityType(Enum):
    """Classification of singularities."""
    REMOVABLE = "removable"
    POLE = "pole"
    ESSENTIAL = "essential"
    BRANCH_POINT = "branch_point"
    REGULAR = "regular"  # Not a singularity


@dataclass
class AnalyticResult:
    """Result from analytic function analysis."""
    is_analytic: bool
    region: str  # Description of region of analyticity
    singularities: List[Dict[str, Any]] = field(default_factory=list)
    series_coefficients: Optional[List[complex]] = None
    radius_of_convergence: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CauchyRiemannResult:
    """Result from Cauchy-Riemann verification."""
    satisfies_cr: bool
    u_x: Optional[float] = None  # du/dx
    v_y: Optional[float] = None  # dv/dy
    u_y: Optional[float] = None  # du/dy
    v_x: Optional[float] = None  # dv/dx
    residual: float = 0.0
    details: str = ""


@dataclass
class LaurentSeries:
    """Laurent series representation."""
    center: complex
    coefficients: Dict[int, complex]  # n -> a_n for sum(a_n * (z-z0)^n)
    inner_radius: float  # Inner radius of annulus
    outer_radius: float  # Outer radius of annulus
    principal_part_order: int  # Highest negative power (pole order)


class AnalyticFunctionsSpecialist:
    """
    BDI Agent for complex analytic function analysis.

    Capabilities:
    - Verify Cauchy-Riemann equations
    - Classify singularities
    - Compute Laurent series
    - Find zeros and poles
    - Analytic continuation
    - Power series expansion
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._epsilon = 1e-8
        self._max_series_terms = 50

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "function" in self.beliefs:
            self.desires.append("analyze_analyticity")
        if "singularity_point" in self.beliefs:
            self.desires.append("classify_singularity")
        if "series_center" in self.beliefs:
            self.desires.append("compute_series")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "analyze_analyticity":
            f = self.beliefs.get("function")
            region = self.beliefs.get("region", "complex_plane")
            return {"result": self.check_analyticity(f, region)}
        elif goal == "classify_singularity":
            f = self.beliefs.get("function")
            z0 = self.beliefs.get("singularity_point")
            return {"result": self.classify_singularity(f, z0)}
        elif goal == "compute_series":
            f = self.beliefs.get("function")
            z0 = self.beliefs.get("series_center", 0)
            return {"result": self.laurent_series(f, z0)}

        return {"status": "unknown_goal", "goal": goal}

    def verify_cauchy_riemann(
        self,
        f: Callable[[complex], complex],
        z: complex,
        h: float = 1e-6
    ) -> CauchyRiemannResult:
        """
        Verify Cauchy-Riemann equations at a point.

        For f(z) = u(x,y) + i*v(x,y), the C-R equations are:
        - du/dx = dv/dy
        - du/dy = -dv/dx

        Args:
            f: Complex function
            z: Point to check
            h: Step size for numerical differentiation

        Returns:
            CauchyRiemannResult with partial derivatives and verification
        """
        x, y = z.real, z.imag

        try:
            # Compute function values
            f_z = f(z)
            f_x_plus = f(complex(x + h, y))
            f_x_minus = f(complex(x - h, y))
            f_y_plus = f(complex(x, y + h))
            f_y_minus = f(complex(x, y - h))

            # Extract u and v components
            u = lambda w: f(w).real
            v = lambda w: f(w).imag

            # Compute partial derivatives using central differences
            u_x = (f_x_plus.real - f_x_minus.real) / (2 * h)
            v_y = (f_y_plus.imag - f_y_minus.imag) / (2 * h)
            u_y = (f_y_plus.real - f_y_minus.real) / (2 * h)
            v_x = (f_x_plus.imag - f_x_minus.imag) / (2 * h)

            # Check Cauchy-Riemann equations
            residual1 = abs(u_x - v_y)
            residual2 = abs(u_y + v_x)
            total_residual = residual1 + residual2

            satisfies = total_residual < self._epsilon * 100

            return CauchyRiemannResult(
                satisfies_cr=satisfies,
                u_x=u_x,
                v_y=v_y,
                u_y=u_y,
                v_x=v_x,
                residual=total_residual,
                details=f"du/dx - dv/dy = {residual1:.2e}, du/dy + dv/dx = {residual2:.2e}"
            )

        except (ValueError, ZeroDivisionError, OverflowError) as e:
            return CauchyRiemannResult(
                satisfies_cr=False,
                residual=float('inf'),
                details=f"Error at z={z}: {str(e)}"
            )

    def classify_singularity(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        max_order: int = 10
    ) -> Tuple[SingularityType, Dict[str, Any]]:
        """
        Classify singularity of f at z0.

        Types:
        - Removable: lim(z->z0) f(z) exists and is finite
        - Pole of order n: lim(z->z0) (z-z0)^n * f(z) is finite and nonzero
        - Essential: Neither removable nor pole (Casorati-Weierstrass)
        - Branch point: Multi-valued behavior

        Args:
            f: Complex function
            z0: Point to classify
            max_order: Maximum pole order to check

        Returns:
            Tuple of (SingularityType, details dict)
        """
        details: Dict[str, Any] = {"point": z0}

        # Check if it's even a singularity
        try:
            f_z0 = f(z0)
            if np.isfinite(f_z0.real) and np.isfinite(f_z0.imag):
                return SingularityType.REGULAR, {"value": f_z0}
        except (ValueError, ZeroDivisionError, OverflowError):
            pass  # Confirmed singularity

        # Approach from multiple directions
        radii = [1e-3, 1e-4, 1e-5, 1e-6]
        angles = [0, np.pi/4, np.pi/2, np.pi, 3*np.pi/2]

        # Check for removable singularity
        limit_values = []
        for r in radii:
            for theta in angles:
                z = z0 + r * np.exp(1j * theta)
                try:
                    val = f(z)
                    if np.isfinite(val.real) and np.isfinite(val.imag):
                        limit_values.append(val)
                except:
                    pass

        if limit_values:
            # Check if values converge
            mean_val = np.mean(limit_values)
            std_val = np.std(limit_values)

            if std_val < abs(mean_val) * 0.01 + 1e-10:
                details["limit"] = mean_val
                return SingularityType.REMOVABLE, details

        # Check for pole
        for order in range(1, max_order + 1):
            products = []
            for r in radii:
                for theta in angles:
                    z = z0 + r * np.exp(1j * theta)
                    try:
                        val = f(z) * (z - z0) ** order
                        if np.isfinite(val.real) and np.isfinite(val.imag):
                            products.append(val)
                    except:
                        pass

            if products:
                mean_prod = np.mean(products)
                std_prod = np.std(products)

                # Check if products converge to nonzero value
                if std_prod < abs(mean_prod) * 0.1 + 1e-10 and abs(mean_prod) > 1e-10:
                    details["order"] = order
                    details["residue"] = mean_prod if order == 1 else None
                    details["leading_coefficient"] = mean_prod
                    return SingularityType.POLE, details

        # Check for branch point (multi-valued behavior)
        # Circle around z0 and check if f returns to same value
        circle_values = []
        n_points = 20
        r = 0.01
        for k in range(n_points + 1):
            theta = 2 * np.pi * k / n_points
            z = z0 + r * np.exp(1j * theta)
            try:
                circle_values.append(f(z))
            except:
                pass

        if len(circle_values) >= 2:
            # Check if start and end differ (branch cut detected)
            if abs(circle_values[0] - circle_values[-1]) > abs(circle_values[0]) * 0.1:
                details["branch_behavior"] = "monodromy_detected"
                return SingularityType.BRANCH_POINT, details

        # Default to essential singularity
        details["reason"] = "neither_removable_nor_pole"
        return SingularityType.ESSENTIAL, details

    def compute_residue(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        method: str = "laurent"
    ) -> complex:
        """
        Compute residue of f at z0.

        Methods:
        - "laurent": Extract a_{-1} from Laurent series
        - "limit": Use limit formula Res(f, z0) = lim(z->z0) (z-z0)*f(z) for simple poles
        - "derivative": For pole of order n, use derivative formula

        Args:
            f: Complex function
            z0: Pole location
            method: Computation method

        Returns:
            Residue value
        """
        if method == "limit":
            # For simple poles
            h = 1e-6
            values = []
            for theta in [0, np.pi/2, np.pi, 3*np.pi/2]:
                z = z0 + h * np.exp(1j * theta)
                try:
                    val = (z - z0) * f(z)
                    if np.isfinite(val.real) and np.isfinite(val.imag):
                        values.append(val)
                except:
                    pass

            if values:
                return np.mean(values)
            return complex(np.nan, np.nan)

        elif method == "laurent":
            # Get Laurent series and extract a_{-1}
            series = self.laurent_series(f, z0)
            return series.coefficients.get(-1, 0)

        elif method == "derivative":
            # First classify to get pole order
            sing_type, details = self.classify_singularity(f, z0)

            if sing_type != SingularityType.POLE:
                return complex(np.nan, np.nan)

            n = details.get("order", 1)

            if n == 1:
                return self.compute_residue(f, z0, method="limit")

            # For higher order poles:
            # Res(f, z0) = (1/(n-1)!) * lim(z->z0) d^(n-1)/dz^(n-1)[(z-z0)^n * f(z)]
            # Use numerical differentiation

            def g(z):
                return (z - z0) ** n * f(z)

            # Numerical (n-1)th derivative at z0
            h = 1e-4
            deriv = self._numerical_derivative(g, z0, n - 1, h)

            # Divide by (n-1)!
            factorial = 1
            for k in range(1, n):
                factorial *= k

            return deriv / factorial

        raise ValueError(f"Unknown method: {method}")

    def _numerical_derivative(
        self,
        f: Callable[[complex], complex],
        z: complex,
        order: int,
        h: float
    ) -> complex:
        """Compute numerical derivative of order n."""
        if order == 0:
            return f(z)

        if order == 1:
            return (f(z + h) - f(z - h)) / (2 * h)

        # Higher order: recursive central differences
        return (
            self._numerical_derivative(f, z + h, order - 1, h) -
            self._numerical_derivative(f, z - h, order - 1, h)
        ) / (2 * h)

    def laurent_series(
        self,
        f: Callable[[complex], complex],
        z0: complex,
        n_terms: int = 20,
        radius: float = 1.0
    ) -> LaurentSeries:
        """
        Compute Laurent series expansion around z0.

        f(z) = sum_{n=-infinity}^{infinity} a_n (z - z0)^n

        Coefficients computed via contour integration:
        a_n = (1/2*pi*i) * integral(f(z) / (z-z0)^(n+1), |z-z0|=r)

        Args:
            f: Complex function
            z0: Expansion center
            n_terms: Number of terms in each direction
            radius: Radius for contour integration

        Returns:
            LaurentSeries object
        """
        coefficients: Dict[int, complex] = {}

        # Use numerical contour integration
        n_points = 256
        theta = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        dtheta = 2 * np.pi / n_points

        # Compute coefficients a_n for n in [-n_terms, n_terms]
        for n in range(-n_terms, n_terms + 1):
            integral = 0j
            for t in theta:
                z = z0 + radius * np.exp(1j * t)
                dz = 1j * radius * np.exp(1j * t)
                try:
                    integrand = f(z) / (z - z0) ** (n + 1)
                    integral += integrand * dz
                except:
                    pass

            a_n = integral * dtheta / (2j * np.pi)

            if abs(a_n) > 1e-14:
                coefficients[n] = a_n

        # Determine principal part order (highest negative power)
        negative_powers = [n for n in coefficients.keys() if n < 0]
        principal_order = -min(negative_powers) if negative_powers else 0

        # Estimate radius of convergence
        positive_coeffs = [(n, abs(coefficients[n])) for n in coefficients if n > 0]
        if len(positive_coeffs) >= 2:
            # Root test: R = 1 / limsup |a_n|^(1/n)
            ratios = [abs(a) ** (1/n) for n, a in positive_coeffs if a > 0]
            if ratios:
                outer_radius = 1.0 / max(ratios) if max(ratios) > 0 else float('inf')
            else:
                outer_radius = float('inf')
        else:
            outer_radius = float('inf')

        return LaurentSeries(
            center=z0,
            coefficients=coefficients,
            inner_radius=0,  # Would need separate analysis
            outer_radius=min(outer_radius, 100),
            principal_part_order=principal_order
        )

    def power_series(
        self,
        f: Callable[[complex], complex],
        z0: complex = 0,
        n_terms: int = 20
    ) -> Tuple[List[complex], float]:
        """
        Compute Taylor/power series expansion.

        f(z) = sum_{n=0}^{infinity} a_n (z - z0)^n

        where a_n = f^(n)(z0) / n!

        Args:
            f: Analytic function
            z0: Expansion point
            n_terms: Number of terms

        Returns:
            Tuple of (coefficients list, radius of convergence)
        """
        coefficients = []
        h = 1e-4

        for n in range(n_terms):
            # Compute nth derivative at z0
            deriv = self._numerical_derivative(f, z0, n, h)

            # Divide by n!
            factorial = 1
            for k in range(1, n + 1):
                factorial *= k

            coefficients.append(deriv / factorial)

        # Estimate radius of convergence
        if len(coefficients) >= 2:
            nonzero = [(i, abs(c)) for i, c in enumerate(coefficients) if abs(c) > 1e-15 and i > 0]
            if nonzero:
                ratios = [abs(c) ** (1/n) for n, c in nonzero]
                radius = 1.0 / max(ratios) if max(ratios) > 0 else float('inf')
            else:
                radius = float('inf')
        else:
            radius = float('inf')

        return coefficients, min(radius, 100)

    def find_zeros(
        self,
        f: Callable[[complex], complex],
        region: Tuple[complex, complex],
        n_points: int = 20
    ) -> List[complex]:
        """
        Find zeros of f in rectangular region.

        Uses argument principle: number of zeros = (1/2*pi*i) * integral(f'/f, boundary)
        Then applies Newton's method to locate them.

        Args:
            f: Complex function
            region: (z_min, z_max) defining rectangle
            n_points: Grid resolution

        Returns:
            List of zeros
        """
        z_min, z_max = region
        x_min, x_max = z_min.real, z_max.real
        y_min, y_max = z_min.imag, z_max.imag

        # Grid search for approximate zeros
        candidates = []
        x_vals = np.linspace(x_min, x_max, n_points)
        y_vals = np.linspace(y_min, y_max, n_points)

        for x in x_vals:
            for y in y_vals:
                z = complex(x, y)
                try:
                    val = f(z)
                    if abs(val) < 1:
                        candidates.append(z)
                except:
                    pass

        # Refine with Newton's method
        zeros = []
        h = 1e-6

        for z0 in candidates:
            z = z0
            for _ in range(50):
                try:
                    fz = f(z)
                    if abs(fz) < 1e-12:
                        # Found a zero
                        # Check if it's new
                        is_new = all(abs(z - z_old) > 1e-8 for z_old in zeros)
                        if is_new:
                            zeros.append(z)
                        break

                    # Newton step: z_new = z - f(z)/f'(z)
                    fpz = (f(z + h) - f(z - h)) / (2 * h)
                    if abs(fpz) < 1e-15:
                        break

                    z_new = z - fz / fpz

                    if abs(z_new - z) < 1e-12:
                        if abs(f(z_new)) < 1e-10:
                            is_new = all(abs(z_new - z_old) > 1e-8 for z_old in zeros)
                            if is_new:
                                zeros.append(z_new)
                        break

                    z = z_new
                except:
                    break

        return zeros

    def check_analyticity(
        self,
        f: Callable[[complex], complex],
        region: Union[str, Tuple[complex, complex]] = "complex_plane",
        n_samples: int = 100
    ) -> AnalyticResult:
        """
        Check if function is analytic in given region.

        Tests Cauchy-Riemann equations at multiple points.

        Args:
            f: Complex function
            region: "complex_plane" or (z_min, z_max) rectangle
            n_samples: Number of test points

        Returns:
            AnalyticResult with analyticity information
        """
        if isinstance(region, str) and region == "complex_plane":
            # Sample in a large region
            test_points = [
                complex(x, y)
                for x in np.linspace(-10, 10, int(np.sqrt(n_samples)))
                for y in np.linspace(-10, 10, int(np.sqrt(n_samples)))
            ]
        else:
            z_min, z_max = region
            x_vals = np.linspace(z_min.real, z_max.real, int(np.sqrt(n_samples)))
            y_vals = np.linspace(z_min.imag, z_max.imag, int(np.sqrt(n_samples)))
            test_points = [complex(x, y) for x in x_vals for y in y_vals]

        singularities = []
        cr_failures = 0

        for z in test_points:
            cr_result = self.verify_cauchy_riemann(f, z)

            if not cr_result.satisfies_cr:
                cr_failures += 1

                # Check if it's a singularity
                sing_type, details = self.classify_singularity(f, z)
                if sing_type != SingularityType.REGULAR:
                    singularities.append({
                        "point": z,
                        "type": sing_type.value,
                        "details": details
                    })

        is_analytic = cr_failures == 0 or (cr_failures < len(test_points) * 0.1 and len(singularities) > 0)

        region_desc = "complex plane" if isinstance(region, str) else f"rectangle from {region[0]} to {region[1]}"

        return AnalyticResult(
            is_analytic=is_analytic,
            region=f"Analytic in {region_desc} except at isolated singularities" if singularities else f"Analytic in {region_desc}",
            singularities=singularities,
            details={
                "cr_failures": cr_failures,
                "total_points": len(test_points),
                "failure_rate": cr_failures / len(test_points) if test_points else 0
            }
        )

    def analytic_continuation(
        self,
        f: Callable[[complex], complex],
        z_start: complex,
        z_end: complex,
        n_steps: int = 100
    ) -> Tuple[complex, List[complex]]:
        """
        Perform analytic continuation along a path.

        Uses power series expansion at each step to continue
        the function beyond its original domain.

        Args:
            f: Initial function definition
            z_start: Starting point
            z_end: Ending point
            n_steps: Number of continuation steps

        Returns:
            Tuple of (final value, path of values)
        """
        path = np.linspace(z_start, z_end, n_steps)
        values = [f(z_start)]

        current_f = f
        current_center = z_start

        for i in range(1, n_steps):
            z = path[i]

            try:
                # Try direct evaluation first
                val = current_f(z)
                if np.isfinite(val.real) and np.isfinite(val.imag):
                    values.append(val)
                    continue
            except:
                pass

            # Need to use series continuation
            coeffs, radius = self.power_series(current_f, current_center, n_terms=15)

            # Evaluate series at z
            val = 0j
            for n, a_n in enumerate(coeffs):
                val += a_n * (z - current_center) ** n

            values.append(val)

            # Update center if we're getting close to boundary
            if abs(z - current_center) > 0.5 * radius:
                # Define new function from series
                new_coeffs = coeffs[:]
                new_center = current_center

                def make_series_func(c, cent):
                    return lambda w: sum(c[n] * (w - cent) ** n for n in range(len(c)))

                # Recenter at current point
                current_f = make_series_func(new_coeffs, new_center)
                current_center = z

        return values[-1], values
