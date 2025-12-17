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
Differential Geometry Specialist
==================================

Provides comprehensive differential geometry operations:
- Metric tensors and line elements
- Christoffel symbols
- Riemann curvature tensor
- Ricci tensor and scalar curvature
- Geodesic equations
- Covariant derivatives

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field


@dataclass
class MetricTensor:
    """Metric tensor g_ij."""
    components: np.ndarray  # n x n matrix
    coordinates: List[str] = field(default_factory=lambda: ["x", "y"])
    inverse: Optional[np.ndarray] = None
    determinant: float = 0.0


@dataclass
class ChristoffelSymbols:
    """Christoffel symbols of the second kind Gamma^k_ij."""
    components: np.ndarray  # n x n x n tensor
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CurvatureResult:
    """Result from curvature computation."""
    riemann_tensor: Optional[np.ndarray] = None  # R^l_ijk
    ricci_tensor: Optional[np.ndarray] = None  # R_ij
    scalar_curvature: Optional[float] = None  # R
    gaussian_curvature: Optional[float] = None  # K (for 2D)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeodesicResult:
    """Result from geodesic computation."""
    path: np.ndarray  # N x dim array of points
    parameter_values: np.ndarray  # Parameter values
    length: float = 0.0
    is_closed: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


class DifferentialGeometrySpecialist:
    """
    BDI Agent for differential geometry computations.

    Capabilities:
    - Compute metric properties
    - Calculate Christoffel symbols
    - Riemann curvature tensor
    - Geodesic equations
    - Covariant derivatives
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._epsilon = 1e-10
        self._h = 1e-6  # Step for numerical derivatives

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "metric" in self.beliefs:
            self.desires.append("analyze_metric")
        if "compute_geodesic" in self.beliefs:
            self.desires.append("compute_geodesic")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "analyze_metric":
            metric = self.beliefs.get("metric")
            point = self.beliefs.get("point")
            return {"result": self.analyze_metric(metric, point)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Metric Tensor ==========

    def create_metric(
        self,
        components: Union[np.ndarray, Callable],
        coordinates: List[str] = None
    ) -> MetricTensor:
        """
        Create metric tensor.

        Args:
            components: n x n matrix or function returning matrix at point
            coordinates: Coordinate names

        Returns:
            MetricTensor
        """
        if callable(components):
            g = components(np.zeros(len(coordinates) if coordinates else 2))
        else:
            g = np.array(components, dtype=float)

        n = g.shape[0]
        if coordinates is None:
            coordinates = [f"x{i}" for i in range(n)]

        # Compute inverse
        g_inv = np.linalg.inv(g)

        # Compute determinant
        det = np.linalg.det(g)

        return MetricTensor(
            components=g,
            coordinates=coordinates,
            inverse=g_inv,
            determinant=det
        )

    def analyze_metric(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Comprehensive metric analysis at a point.

        Args:
            g: Function returning metric matrix at a point
            point: Point to analyze (default: origin)

        Returns:
            Dictionary with metric properties
        """
        if point is None:
            point = np.zeros(2)

        g_p = g(point)
        n = g_p.shape[0]

        # Basic properties
        det = np.linalg.det(g_p)
        eigenvalues = np.linalg.eigvalsh(g_p)
        signature = (np.sum(eigenvalues > 0), np.sum(eigenvalues < 0))

        is_riemannian = all(e > 0 for e in eigenvalues)
        is_lorentzian = signature == (n-1, 1) or signature == (1, n-1)

        # Compute Christoffel symbols
        christoffel = self.compute_christoffel(g, point)

        # Compute curvature for 2D case
        curvature = None
        if n == 2:
            curvature = self.gaussian_curvature(g, point)

        return {
            "metric_at_point": g_p,
            "determinant": det,
            "eigenvalues": eigenvalues.tolist(),
            "signature": signature,
            "is_riemannian": is_riemannian,
            "is_lorentzian": is_lorentzian,
            "christoffel_sample": christoffel.components[0, 0, :].tolist(),
            "gaussian_curvature": curvature
        }

    # ========== Christoffel Symbols ==========

    def compute_christoffel(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> ChristoffelSymbols:
        """
        Compute Christoffel symbols of the second kind.

        Gamma^k_ij = (1/2) g^{kl} (g_{li,j} + g_{lj,i} - g_{ij,l})

        Args:
            g: Metric function
            point: Point to compute at

        Returns:
            ChristoffelSymbols
        """
        g_p = g(point)
        n = g_p.shape[0]
        g_inv = np.linalg.inv(g_p)

        # Compute metric derivatives
        dg = np.zeros((n, n, n))  # dg[i,j,k] = dg_ij/dx^k

        for k in range(n):
            e_k = np.zeros(n)
            e_k[k] = self._h

            g_plus = g(point + e_k)
            g_minus = g(point - e_k)

            dg[:, :, k] = (g_plus - g_minus) / (2 * self._h)

        # Compute Christoffel symbols
        gamma = np.zeros((n, n, n))  # gamma[k,i,j] = Gamma^k_ij

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    for l in range(n):
                        gamma[k, i, j] += 0.5 * g_inv[k, l] * (
                            dg[l, j, i] + dg[l, i, j] - dg[i, j, l]
                        )

        return ChristoffelSymbols(
            components=gamma,
            details={"point": point.tolist()}
        )

    # ========== Curvature ==========

    def compute_riemann(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> np.ndarray:
        """
        Compute Riemann curvature tensor R^l_ijk.

        R^l_ijk = Gamma^l_jk,i - Gamma^l_ik,j
                  + Gamma^l_im * Gamma^m_jk - Gamma^l_jm * Gamma^m_ik

        Args:
            g: Metric function
            point: Point

        Returns:
            Riemann tensor (n x n x n x n)
        """
        g_p = g(point)
        n = g_p.shape[0]

        # Christoffel at point and derivatives
        gamma = self.compute_christoffel(g, point).components

        # Christoffel derivatives
        dgamma = np.zeros((n, n, n, n))  # dgamma[k,i,j,l] = dGamma^k_ij/dx^l

        for l in range(n):
            e_l = np.zeros(n)
            e_l[l] = self._h

            gamma_plus = self.compute_christoffel(g, point + e_l).components
            gamma_minus = self.compute_christoffel(g, point - e_l).components

            dgamma[:, :, :, l] = (gamma_plus - gamma_minus) / (2 * self._h)

        # Compute Riemann tensor
        R = np.zeros((n, n, n, n))  # R[l,i,j,k] = R^l_ijk

        for l in range(n):
            for i in range(n):
                for j in range(n):
                    for k in range(n):
                        # Derivative terms
                        R[l, i, j, k] = dgamma[l, j, k, i] - dgamma[l, i, k, j]

                        # Product terms
                        for m in range(n):
                            R[l, i, j, k] += (gamma[l, i, m] * gamma[m, j, k] -
                                              gamma[l, j, m] * gamma[m, i, k])

        return R

    def compute_ricci(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> np.ndarray:
        """
        Compute Ricci tensor R_ij = R^k_ikj.

        Args:
            g: Metric function
            point: Point

        Returns:
            Ricci tensor (n x n)
        """
        R = self.compute_riemann(g, point)
        n = R.shape[0]

        ricci = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    ricci[i, j] += R[k, i, k, j]

        return ricci

    def scalar_curvature(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> float:
        """
        Compute scalar curvature R = g^ij R_ij.

        Args:
            g: Metric function
            point: Point

        Returns:
            Scalar curvature
        """
        g_p = g(point)
        g_inv = np.linalg.inv(g_p)
        ricci = self.compute_ricci(g, point)

        return np.sum(g_inv * ricci)

    def gaussian_curvature(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> float:
        """
        Compute Gaussian curvature for 2D surfaces.

        K = R / 2 (for 2D Riemannian manifolds)

        Args:
            g: Metric function
            point: Point

        Returns:
            Gaussian curvature
        """
        g_p = g(point)
        if g_p.shape[0] != 2:
            raise ValueError("Gaussian curvature only defined for 2D")

        return self.scalar_curvature(g, point) / 2

    def full_curvature_analysis(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> CurvatureResult:
        """
        Complete curvature analysis.

        Args:
            g: Metric function
            point: Point

        Returns:
            CurvatureResult with all curvature quantities
        """
        g_p = g(point)
        n = g_p.shape[0]

        riemann = self.compute_riemann(g, point)
        ricci = self.compute_ricci(g, point)
        scalar = self.scalar_curvature(g, point)

        gaussian = None
        if n == 2:
            gaussian = scalar / 2

        return CurvatureResult(
            riemann_tensor=riemann,
            ricci_tensor=ricci,
            scalar_curvature=scalar,
            gaussian_curvature=gaussian,
            details={"dimension": n, "point": point.tolist()}
        )

    # ========== Geodesics ==========

    def geodesic_equation(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        x: np.ndarray,
        v: np.ndarray
    ) -> np.ndarray:
        """
        Compute geodesic acceleration.

        d²x^k/dt² = -Gamma^k_ij (dx^i/dt)(dx^j/dt)

        Args:
            g: Metric function
            x: Position
            v: Velocity (dx/dt)

        Returns:
            Acceleration (d²x/dt²)
        """
        gamma = self.compute_christoffel(g, x).components
        n = len(x)

        accel = np.zeros(n)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    accel[k] -= gamma[k, i, j] * v[i] * v[j]

        return accel

    def compute_geodesic(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        x0: np.ndarray,
        v0: np.ndarray,
        t_max: float = 1.0,
        n_steps: int = 1000
    ) -> GeodesicResult:
        """
        Compute geodesic starting from x0 with initial velocity v0.

        Uses RK4 integration.

        Args:
            g: Metric function
            x0: Initial position
            v0: Initial velocity
            t_max: Maximum parameter value
            n_steps: Integration steps

        Returns:
            GeodesicResult with path
        """
        n = len(x0)
        dt = t_max / n_steps

        # State: [x, v]
        x = x0.copy()
        v = v0.copy()

        path = [x.copy()]
        t_values = [0]

        for step in range(n_steps):
            # RK4 integration
            k1_x = v
            k1_v = self.geodesic_equation(g, x, v)

            k2_x = v + 0.5 * dt * k1_v
            k2_v = self.geodesic_equation(g, x + 0.5 * dt * k1_x, v + 0.5 * dt * k1_v)

            k3_x = v + 0.5 * dt * k2_v
            k3_v = self.geodesic_equation(g, x + 0.5 * dt * k2_x, v + 0.5 * dt * k2_v)

            k4_x = v + dt * k3_v
            k4_v = self.geodesic_equation(g, x + dt * k3_x, v + dt * k3_v)

            x = x + dt * (k1_x + 2*k2_x + 2*k3_x + k4_x) / 6
            v = v + dt * (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6

            path.append(x.copy())
            t_values.append((step + 1) * dt)

        path = np.array(path)
        t_values = np.array(t_values)

        # Compute arc length
        length = self._compute_arc_length(g, path)

        # Check if closed
        is_closed = np.linalg.norm(path[-1] - path[0]) < 0.01

        return GeodesicResult(
            path=path,
            parameter_values=t_values,
            length=length,
            is_closed=is_closed
        )

    def _compute_arc_length(
        self,
        g: Callable[[np.ndarray], np.ndarray],
        path: np.ndarray
    ) -> float:
        """Compute arc length of path using metric."""
        length = 0

        for i in range(len(path) - 1):
            x = path[i]
            dx = path[i + 1] - path[i]

            g_x = g(x)
            ds_squared = dx @ g_x @ dx

            if ds_squared > 0:
                length += np.sqrt(ds_squared)

        return length

    # ========== Covariant Derivatives ==========

    def covariant_derivative_vector(
        self,
        V: Callable[[np.ndarray], np.ndarray],
        g: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        direction_index: int
    ) -> np.ndarray:
        """
        Compute covariant derivative of vector field.

        (nabla_j V)^i = dV^i/dx^j + Gamma^i_jk V^k

        Args:
            V: Vector field function
            g: Metric function
            point: Point
            direction_index: Index j for nabla_j

        Returns:
            Covariant derivative components
        """
        n = len(point)
        gamma = self.compute_christoffel(g, point).components

        V_p = V(point)

        # Partial derivative
        e_j = np.zeros(n)
        e_j[direction_index] = self._h

        V_plus = V(point + e_j)
        V_minus = V(point - e_j)

        dV = (V_plus - V_minus) / (2 * self._h)

        # Add connection terms
        result = dV.copy()
        for i in range(n):
            for k in range(n):
                result[i] += gamma[i, direction_index, k] * V_p[k]

        return result

    def parallel_transport(
        self,
        V0: np.ndarray,
        g: Callable[[np.ndarray], np.ndarray],
        path: np.ndarray
    ) -> np.ndarray:
        """
        Parallel transport vector along path.

        dV^i/dt = -Gamma^i_jk V^j (dx^k/dt)

        Args:
            V0: Initial vector
            g: Metric function
            path: Path points

        Returns:
            Final transported vector
        """
        V = V0.copy()

        for i in range(len(path) - 1):
            x = path[i]
            dx = path[i + 1] - path[i]

            gamma = self.compute_christoffel(g, x).components
            n = len(V)

            dV = np.zeros(n)
            for m in range(n):
                for j in range(n):
                    for k in range(n):
                        dV[m] -= gamma[m, j, k] * V[j] * dx[k]

            V = V + dV

        return V

    # ========== Standard Metrics ==========

    @staticmethod
    def euclidean_metric(point: np.ndarray) -> np.ndarray:
        """Euclidean metric (identity)."""
        n = len(point)
        return np.eye(n)

    @staticmethod
    def sphere_metric(theta_phi: np.ndarray, R: float = 1.0) -> np.ndarray:
        """
        Metric on 2-sphere.

        ds² = R²(dθ² + sin²θ dφ²)

        Args:
            theta_phi: [theta, phi] coordinates
            R: Sphere radius

        Returns:
            2x2 metric tensor
        """
        theta = theta_phi[0]
        return R**2 * np.array([
            [1, 0],
            [0, np.sin(theta)**2]
        ])

    @staticmethod
    def hyperbolic_metric(x_y: np.ndarray) -> np.ndarray:
        """
        Poincaré half-plane metric.

        ds² = (dx² + dy²) / y²

        Args:
            x_y: [x, y] with y > 0

        Returns:
            2x2 metric tensor
        """
        y = max(x_y[1], 1e-10)
        return np.array([
            [1/y**2, 0],
            [0, 1/y**2]
        ])

    @staticmethod
    def schwarzschild_metric(r_theta: np.ndarray, M: float = 1.0) -> np.ndarray:
        """
        Schwarzschild metric (simplified 2D radial slice).

        Args:
            r_theta: [r, theta] coordinates
            M: Mass parameter

        Returns:
            2x2 metric tensor
        """
        r = max(r_theta[0], 2*M + 0.01)
        f = 1 - 2*M/r

        return np.array([
            [-f, 0],
            [0, r**2]
        ])
