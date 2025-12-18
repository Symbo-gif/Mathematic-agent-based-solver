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
Conformal Mapping Specialist
==============================

Provides comprehensive conformal mapping operations:
- Möbius (Linear Fractional) transformations
- Schwarz-Christoffel mappings
- Common domain mappings
- Mapping composition and inversion
- Conformality verification

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class DomainType(Enum):
    """Standard domain types."""
    UNIT_DISK = "unit_disk"
    UPPER_HALF_PLANE = "upper_half_plane"
    RIGHT_HALF_PLANE = "right_half_plane"
    STRIP = "strip"
    WEDGE = "wedge"
    ANNULUS = "annulus"
    POLYGON = "polygon"
    RECTANGLE = "rectangle"
    CUSTOM = "custom"


@dataclass
class MobiusTransform:
    """Möbius transformation (az + b) / (cz + d)."""
    a: complex
    b: complex
    c: complex
    d: complex

    def __call__(self, z: complex) -> complex:
        """Apply transformation."""
        if abs(self.c * z + self.d) < 1e-15:
            return complex(float('inf'))
        return (self.a * z + self.b) / (self.c * z + self.d)

    def inverse(self) -> 'MobiusTransform':
        """Get inverse transformation."""
        # Inverse of (az+b)/(cz+d) is (dz-b)/(-cz+a)
        return MobiusTransform(self.d, -self.b, -self.c, self.a)

    def compose(self, other: 'MobiusTransform') -> 'MobiusTransform':
        """Compose with another Möbius transformation."""
        # (a1*((a2*z+b2)/(c2*z+d2)) + b1) / (c1*((a2*z+b2)/(c2*z+d2)) + d1)
        # = (a1*(a2*z+b2) + b1*(c2*z+d2)) / (c1*(a2*z+b2) + d1*(c2*z+d2))
        # = ((a1*a2+b1*c2)*z + (a1*b2+b1*d2)) / ((c1*a2+d1*c2)*z + (c1*b2+d1*d2))
        return MobiusTransform(
            self.a * other.a + self.b * other.c,
            self.a * other.b + self.b * other.d,
            self.c * other.a + self.d * other.c,
            self.c * other.b + self.d * other.d
        )

    @property
    def fixed_points(self) -> List[complex]:
        """Find fixed points where f(z) = z."""
        # (az+b)/(cz+d) = z => az+b = cz^2+dz => cz^2 + (d-a)z - b = 0
        if abs(self.c) < 1e-15:
            # Linear case: az + b = dz => z = b/(d-a)
            if abs(self.d - self.a) < 1e-15:
                return []  # No fixed points (or all points if a=d, b=0)
            return [self.b / (self.d - self.a)]

        # Quadratic case
        A, B, C = self.c, self.d - self.a, -self.b
        disc = B*B - 4*A*C

        if abs(disc) < 1e-15:
            return [-B / (2*A)]

        sqrt_disc = np.sqrt(disc)
        return [(-B + sqrt_disc) / (2*A), (-B - sqrt_disc) / (2*A)]

    @property
    def determinant(self) -> complex:
        """Compute ad - bc (normalization)."""
        return self.a * self.d - self.b * self.c

    def normalize(self) -> 'MobiusTransform':
        """Normalize so that ad - bc = 1."""
        det = self.determinant
        if abs(det) < 1e-15:
            return self
        sqrt_det = np.sqrt(det)
        return MobiusTransform(
            self.a / sqrt_det,
            self.b / sqrt_det,
            self.c / sqrt_det,
            self.d / sqrt_det
        )


@dataclass
class ConformalMapResult:
    """Result from conformal mapping."""
    mapping: Callable[[complex], complex]
    inverse: Optional[Callable[[complex], complex]] = None
    source_domain: DomainType = DomainType.CUSTOM
    target_domain: DomainType = DomainType.CUSTOM
    is_conformal: bool = True
    special_points: Dict[str, complex] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


class ConformalMappingSpecialist:
    """
    BDI Agent for conformal mapping operations.

    Capabilities:
    - Construct Möbius transformations
    - Standard domain mappings
    - Schwarz-Christoffel for polygons
    - Verify conformality
    - Compose and invert mappings
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
        if "source_domain" in self.beliefs and "target_domain" in self.beliefs:
            self.desires.append("find_mapping")
        if "three_points_source" in self.beliefs:
            self.desires.append("mobius_from_points")
        if "polygon_vertices" in self.beliefs:
            self.desires.append("schwarz_christoffel")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "find_mapping":
            src = self.beliefs.get("source_domain")
            tgt = self.beliefs.get("target_domain")
            return {"result": self.standard_mapping(src, tgt)}
        elif goal == "mobius_from_points":
            src_pts = self.beliefs.get("three_points_source")
            tgt_pts = self.beliefs.get("three_points_target")
            return {"result": self.mobius_from_three_points(src_pts, tgt_pts)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Möbius Transformations ==========

    def mobius_from_three_points(
        self,
        source_points: Tuple[complex, complex, complex],
        target_points: Tuple[complex, complex, complex]
    ) -> MobiusTransform:
        """
        Construct Möbius transformation mapping three points to three points.

        Uses cross-ratio preservation: (z, z1; z2, z3) = (w, w1; w2, w3)

        Args:
            source_points: (z1, z2, z3) source points
            target_points: (w1, w2, w3) target points

        Returns:
            MobiusTransform that maps z_i to w_i
        """
        z1, z2, z3 = source_points
        w1, w2, w3 = target_points

        # Map to canonical form first: z1 -> 0, z2 -> 1, z3 -> inf
        # Then from canonical to targets

        # T1 maps z1->0, z2->1, z3->inf: T1(z) = (z-z1)(z2-z3) / ((z-z3)(z2-z1))
        # T2 maps 0->w1, 1->w2, inf->w3: T2(w) = (w3*(w2-w1)*w + w1*(w3-w2)) / ((w2-w1)*w + (w3-w2))

        # Handle infinity cases
        def handle_inf(val):
            """Perform handle inf operation.

            Args:
            val: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.handle_inf(...)
            """
            return complex(1e15) if val == complex(float('inf')) else val

        z1, z2, z3 = handle_inf(z1), handle_inf(z2), handle_inf(z3)
        w1, w2, w3 = handle_inf(w1), handle_inf(w2), handle_inf(w3)

        # Cross-ratio based construction
        # (w - w1)(w2 - w3) / ((w - w3)(w2 - w1)) = (z - z1)(z2 - z3) / ((z - z3)(z2 - z1))

        # Solve for w in terms of z
        # Let A = (z2 - z3), B = (z2 - z1), C = (w2 - w3), D = (w2 - w1)
        # (w - w1)/((w - w3) = (z - z1) * A * D / ((z - z3) * B * C)
        # Let k = A * D / (B * C)
        # w - w1 = k * (z - z1) * (w - w3) / (z - z3)
        # w(z - z3) - w1(z - z3) = k(z - z1)(w - w3)
        # w[(z - z3) - k(z - z1)] = w1(z - z3) - k*w3*(z - z1)
        # w = [w1(z - z3) - k*w3*(z - z1)] / [(z - z3) - k(z - z1)]

        A = z2 - z3
        B = z2 - z1
        C = w2 - w3
        D = w2 - w1

        if abs(B) < 1e-15 or abs(C) < 1e-15:
            # Degenerate case
            return MobiusTransform(1, 0, 0, 1)

        k = (A * D) / (B * C)

        # w = [w1(z - z3) - k*w3*(z - z1)] / [(z - z3) - k(z - z1)]
        # w = [w1*z - w1*z3 - k*w3*z + k*w3*z1] / [z - z3 - k*z + k*z1]
        # w = [(w1 - k*w3)*z + (-w1*z3 + k*w3*z1)] / [(1 - k)*z + (-z3 + k*z1)]

        a = w1 - k * w3
        b = -w1 * z3 + k * w3 * z1
        c = 1 - k
        d = -z3 + k * z1

        return MobiusTransform(a, b, c, d)

    def mobius_disk_to_disk(
        self,
        z0: complex
    ) -> MobiusTransform:
        """
        Möbius transformation mapping unit disk to itself with z0 -> 0.

        f(z) = (z - z0) / (1 - conj(z0)*z)

        Args:
            z0: Point to map to origin

        Returns:
            MobiusTransform preserving unit disk
        """
        return MobiusTransform(
            1, -z0,
            -np.conj(z0), 1
        )

    def mobius_half_plane_to_disk(self) -> MobiusTransform:
        """
        Cayley transform: upper half-plane to unit disk.

        f(z) = (z - i) / (z + i)
        """
        return MobiusTransform(1, -1j, 1, 1j)

    def mobius_disk_to_half_plane(self) -> MobiusTransform:
        """
        Inverse Cayley transform: unit disk to upper half-plane.

        f(z) = i(1 + z) / (1 - z)
        """
        return MobiusTransform(1j, 1j, -1, 1)

    # ========== Standard Domain Mappings ==========

    def standard_mapping(
        self,
        source: DomainType,
        target: DomainType
    ) -> ConformalMapResult:
        """
        Get standard conformal mapping between domains.

        Args:
            source: Source domain type
            target: Target domain type

        Returns:
            ConformalMapResult with mapping function
        """
        key = (source, target)

        mappings = {
            (DomainType.UPPER_HALF_PLANE, DomainType.UNIT_DISK): self._uhp_to_disk,
            (DomainType.UNIT_DISK, DomainType.UPPER_HALF_PLANE): self._disk_to_uhp,
            (DomainType.RIGHT_HALF_PLANE, DomainType.UNIT_DISK): self._rhp_to_disk,
            (DomainType.STRIP, DomainType.UPPER_HALF_PLANE): self._strip_to_uhp,
            (DomainType.WEDGE, DomainType.UPPER_HALF_PLANE): self._wedge_to_uhp,
        }

        if key in mappings:
            return mappings[key]()

        # Try to find composition
        if source != DomainType.UNIT_DISK and target != DomainType.UNIT_DISK:
            # Go through unit disk as intermediate
            map1 = self.standard_mapping(source, DomainType.UNIT_DISK)
            map2 = self.standard_mapping(DomainType.UNIT_DISK, target)

            if map1.mapping and map2.mapping:
                composed = lambda z: map2.mapping(map1.mapping(z))
                inv = None
                if map1.inverse and map2.inverse:
                    inv = lambda w: map1.inverse(map2.inverse(w))

                return ConformalMapResult(
                    mapping=composed,
                    inverse=inv,
                    source_domain=source,
                    target_domain=target,
                    details={"via": "unit_disk"}
                )

        return ConformalMapResult(
            mapping=lambda z: z,
            source_domain=source,
            target_domain=target,
            is_conformal=False,
            details={"error": "No mapping found"}
        )

    def _uhp_to_disk(self) -> ConformalMapResult:
        """Upper half-plane to unit disk (Cayley)."""
        mobius = self.mobius_half_plane_to_disk()
        return ConformalMapResult(
            mapping=mobius,
            inverse=mobius.inverse(),
            source_domain=DomainType.UPPER_HALF_PLANE,
            target_domain=DomainType.UNIT_DISK,
            special_points={"i": mobius(1j)}
        )

    def _disk_to_uhp(self) -> ConformalMapResult:
        """Unit disk to upper half-plane (inverse Cayley)."""
        mobius = self.mobius_disk_to_half_plane()
        return ConformalMapResult(
            mapping=mobius,
            inverse=mobius.inverse(),
            source_domain=DomainType.UNIT_DISK,
            target_domain=DomainType.UPPER_HALF_PLANE,
            special_points={"0": mobius(0)}
        )

    def _rhp_to_disk(self) -> ConformalMapResult:
        """Right half-plane to unit disk."""
        # f(z) = (z - 1) / (z + 1)
        mobius = MobiusTransform(1, -1, 1, 1)
        return ConformalMapResult(
            mapping=mobius,
            inverse=mobius.inverse(),
            source_domain=DomainType.RIGHT_HALF_PLANE,
            target_domain=DomainType.UNIT_DISK
        )

    def _strip_to_uhp(self) -> ConformalMapResult:
        """
        Horizontal strip {0 < Im(z) < pi} to upper half-plane.

        f(z) = exp(z)
        """
        def mapping(z):
            """Perform mapping operation.

            Args:
            z: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.mapping(...)
            """
            return np.exp(z)

        def inverse(w):
            """Perform inverse operation.

            Args:
            w: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.inverse(...)
            """
            return np.log(w)

        return ConformalMapResult(
            mapping=mapping,
            inverse=inverse,
            source_domain=DomainType.STRIP,
            target_domain=DomainType.UPPER_HALF_PLANE,
            details={"strip_height": np.pi}
        )

    def _wedge_to_uhp(self) -> ConformalMapResult:
        """
        Wedge {0 < arg(z) < alpha} to upper half-plane.

        f(z) = z^(pi/alpha)
        """
        alpha = self.beliefs.get("wedge_angle", np.pi/2)
        exponent = np.pi / alpha

        def mapping(z):
            """Perform mapping operation.

            Args:
            z: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.mapping(...)
            """
            return z ** exponent

        def inverse(w):
            """Perform inverse operation.

            Args:
            w: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.inverse(...)
            """
            return w ** (1/exponent)

        return ConformalMapResult(
            mapping=mapping,
            inverse=inverse,
            source_domain=DomainType.WEDGE,
            target_domain=DomainType.UPPER_HALF_PLANE,
            details={"wedge_angle": alpha, "exponent": exponent}
        )

    # ========== Schwarz-Christoffel ==========

    def schwarz_christoffel(
        self,
        polygon_vertices: List[complex],
        prevertices: Optional[List[float]] = None
    ) -> ConformalMapResult:
        """
        Schwarz-Christoffel mapping from upper half-plane to polygon.

        f(z) = A * integral(product((z - x_k)^(alpha_k - 1)), z) + B

        where x_k are prevertices on real axis and alpha_k*pi are interior angles.

        Args:
            polygon_vertices: Vertices of target polygon in order
            prevertices: Pre-images on real axis (auto-computed if None)

        Returns:
            ConformalMapResult with Schwarz-Christoffel mapping
        """
        n = len(polygon_vertices)
        vertices = np.array(polygon_vertices)

        # Compute interior angles
        angles = []
        for i in range(n):
            v_prev = vertices[(i - 1) % n]
            v_curr = vertices[i]
            v_next = vertices[(i + 1) % n]

            # Vectors
            e1 = v_prev - v_curr
            e2 = v_next - v_curr

            # Interior angle
            angle = np.angle(e2 / e1)
            if angle < 0:
                angle += 2 * np.pi
            angles.append(angle)

        # Exponents: beta_k = (alpha_k / pi) - 1 where alpha_k is interior angle
        betas = [(a / np.pi) - 1 for a in angles]

        # Default prevertices (equally spaced, simple case)
        if prevertices is None:
            prevertices = list(np.linspace(-1, 1, n))

        # Build the Schwarz-Christoffel integrand
        def sc_integrand(z):
            """Perform sc integrand operation.

            Args:
            z: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.sc_integrand(...)
            """
            prod = 1
            for k, xk in enumerate(prevertices):
                prod *= (z - xk) ** betas[k]
            return prod

        # Numerical integration for the mapping
        def sc_mapping(z):
            """Perform sc mapping operation.

            Args:
            z: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.sc_mapping(...)
            """
            # Integrate from 0 to z
            n_steps = 100
            if abs(z) < 1e-10:
                return vertices[0]

            path = np.linspace(0, z, n_steps)
            integral = 0j

            for i in range(len(path) - 1):
                dz = path[i + 1] - path[i]
                z_mid = (path[i] + path[i + 1]) / 2
                try:
                    integral += sc_integrand(z_mid) * dz
                except:
                    pass

            # Scale and translate to match vertices
            # This is a simplified version; full SC requires parameter fitting
            A = (vertices[1] - vertices[0]) / (sc_mapping_raw(prevertices[1]) - sc_mapping_raw(prevertices[0]) + 1e-10)
            B = vertices[0]

            return A * integral + B

        # Raw mapping without scaling
        def sc_mapping_raw(z):
            """Perform sc mapping raw operation.

            Args:
            z: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.sc_mapping_raw(...)
            """
            n_steps = 50
            if abs(z) < 1e-10:
                return 0j

            path = np.linspace(0, z, n_steps)
            integral = 0j

            for i in range(len(path) - 1):
                dz = path[i + 1] - path[i]
                z_mid = (path[i] + path[i + 1]) / 2
                try:
                    integral += sc_integrand(z_mid) * dz
                except:
                    pass

            return integral

        return ConformalMapResult(
            mapping=sc_mapping,
            inverse=None,  # SC inverse requires numerical inversion
            source_domain=DomainType.UPPER_HALF_PLANE,
            target_domain=DomainType.POLYGON,
            details={
                "vertices": polygon_vertices,
                "prevertices": prevertices,
                "interior_angles": angles,
                "betas": betas
            }
        )

    # ========== Verification ==========

    def verify_conformal(
        self,
        f: Callable[[complex], complex],
        z: complex,
        h: float = 1e-6
    ) -> Dict[str, Any]:
        """
        Verify that f is conformal at z (preserves angles and orientation).

        Conformal <=> f'(z) != 0 and f satisfies Cauchy-Riemann

        Args:
            f: Mapping function
            z: Point to verify
            h: Step size

        Returns:
            Dictionary with conformality verification
        """
        # Check derivative is nonzero
        f_prime = (f(z + h) - f(z - h)) / (2 * h)

        if abs(f_prime) < 1e-12:
            return {
                "is_conformal": False,
                "reason": "derivative_is_zero",
                "f_prime": f_prime
            }

        # Check Cauchy-Riemann
        x, y = z.real, z.imag

        f_z = f(z)
        f_xp = f(complex(x + h, y))
        f_xm = f(complex(x - h, y))
        f_yp = f(complex(x, y + h))
        f_ym = f(complex(x, y - h))

        u_x = (f_xp.real - f_xm.real) / (2 * h)
        v_y = (f_yp.imag - f_ym.imag) / (2 * h)
        u_y = (f_yp.real - f_ym.real) / (2 * h)
        v_x = (f_xp.imag - f_xm.imag) / (2 * h)

        cr1 = abs(u_x - v_y)
        cr2 = abs(u_y + v_x)

        is_conformal = cr1 < 1e-6 and cr2 < 1e-6 and abs(f_prime) > 1e-12

        # Compute scale factor (magnification)
        scale = abs(f_prime)

        # Compute rotation angle
        rotation = np.angle(f_prime)

        return {
            "is_conformal": is_conformal,
            "derivative": f_prime,
            "scale_factor": scale,
            "rotation_angle": rotation,
            "cauchy_riemann_residual": cr1 + cr2,
            "details": {
                "u_x": u_x, "v_y": v_y,
                "u_y": u_y, "v_x": v_x
            }
        }

    def jacobian(
        self,
        f: Callable[[complex], complex],
        z: complex,
        h: float = 1e-6
    ) -> np.ndarray:
        """
        Compute Jacobian matrix of f at z.

        For f = u + iv, J = [[u_x, u_y], [v_x, v_y]]

        Args:
            f: Complex function
            z: Point
            h: Step size

        Returns:
            2x2 Jacobian matrix
        """
        x, y = z.real, z.imag

        f_xp = f(complex(x + h, y))
        f_xm = f(complex(x - h, y))
        f_yp = f(complex(x, y + h))
        f_ym = f(complex(x, y - h))

        u_x = (f_xp.real - f_xm.real) / (2 * h)
        u_y = (f_yp.real - f_ym.real) / (2 * h)
        v_x = (f_xp.imag - f_xm.imag) / (2 * h)
        v_y = (f_yp.imag - f_ym.imag) / (2 * h)

        return np.array([[u_x, u_y], [v_x, v_y]])
