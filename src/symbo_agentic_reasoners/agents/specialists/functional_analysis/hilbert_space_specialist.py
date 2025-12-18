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
Hilbert Space Specialist
=========================

Provides comprehensive Hilbert space operations:
- Inner product verification
- Orthogonality and projections
- Orthonormal bases
- Fourier series expansions
- Bessel's inequality and Parseval
- Projection theorem

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field


@dataclass
class InnerProductResult:
    """Result from inner product analysis."""
    is_inner_product: bool
    properties: List[str] = field(default_factory=list)
    counterexample: Optional[Dict[str, Any]] = None


@dataclass
class ProjectionResult:
    """Result from projection computation."""
    projection: np.ndarray
    distance: float
    coefficients: Optional[List[float]] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FourierResult:
    """Result from Fourier expansion."""
    coefficients: np.ndarray
    partial_sum: Callable[[float], float]
    parseval_lhs: float
    parseval_rhs: float
    details: Dict[str, Any] = field(default_factory=dict)


class HilbertSpaceSpecialist:
    """
    BDI Agent for Hilbert space analysis.

    Capabilities:
    - Inner product verification
    - Orthogonalization (Gram-Schmidt)
    - Projection theorem
    - Fourier expansions
    - Spectral analysis
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
        if "inner_product" in self.beliefs:
            self.desires.append("verify_inner_product")
        if "vectors" in self.beliefs and "orthonormalize" in self.beliefs:
            self.desires.append("gram_schmidt")
        if "subspace" in self.beliefs and "vector" in self.beliefs:
            self.desires.append("project")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "verify_inner_product":
            ip = self.beliefs.get("inner_product")
            samples = self.beliefs.get("samples", [])
            return {"result": self.verify_inner_product(ip, samples)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Inner Product ==========

    def verify_inner_product(
        self,
        ip: Callable[[np.ndarray, np.ndarray], complex],
        samples: List[np.ndarray],
        scalars: List[complex] = None
    ) -> InnerProductResult:
        """
        Verify inner product axioms.

        Axioms (complex case):
        1. <x, x> >= 0 and <x, x> = 0 iff x = 0
        2. <x, y> = conj(<y, x>) (conjugate symmetry)
        3. <ax + by, z> = a<x, z> + b<y, z> (linearity in first arg)

        Args:
            ip: Proposed inner product
            samples: Sample vectors
            scalars: Scalars to test linearity

        Returns:
            InnerProductResult
        """
        if scalars is None:
            scalars = [1, -1, 2, 1j, 1+1j]

        properties = []
        counterexample = None

        # Test positivity
        positive = True
        for x in samples:
            val = ip(x, x)
            if val.real < -self._epsilon or abs(val.imag) > self._epsilon:
                positive = False
                counterexample = {"axiom": "positivity", "x": x, "<x,x>": val}
                break

        if positive:
            properties.append("positive")

        # Test definiteness
        definite = True
        for x in samples:
            if abs(ip(x, x)) < self._epsilon and np.linalg.norm(x) > self._epsilon:
                definite = False
                counterexample = counterexample or {"axiom": "definiteness", "x": x}
                break

        if definite:
            properties.append("definite")

        # Test conjugate symmetry
        symmetric = True
        for x in samples:
            for y in samples:
                if abs(ip(x, y) - np.conj(ip(y, x))) > self._epsilon:
                    symmetric = False
                    counterexample = counterexample or {
                        "axiom": "conjugate_symmetry",
                        "x": x, "y": y,
                        "<x,y>": ip(x, y),
                        "conj(<y,x>)": np.conj(ip(y, x))
                    }
                    break

        if symmetric:
            properties.append("conjugate_symmetric")

        # Test linearity
        linear = True
        for x in samples:
            for y in samples:
                for z in samples:
                    for a in scalars:
                        for b in scalars:
                            lhs = ip(a * x + b * y, z)
                            rhs = a * ip(x, z) + b * ip(y, z)
                            if abs(lhs - rhs) > self._epsilon * (abs(rhs) + 1):
                                linear = False
                                counterexample = counterexample or {
                                    "axiom": "linearity",
                                    "a": a, "b": b,
                                    "lhs": lhs, "rhs": rhs
                                }
                                break

        if linear:
            properties.append("linear")

        is_inner_product = len(properties) == 4

        return InnerProductResult(
            is_inner_product=is_inner_product,
            properties=properties,
            counterexample=counterexample
        )

    @staticmethod
    def standard_inner_product(x: np.ndarray, y: np.ndarray) -> complex:
        """Standard inner product <x, y> = sum(x_i * conj(y_i))."""
        return np.vdot(y, x)  # numpy vdot conjugates first argument

    @staticmethod
    def weighted_inner_product(
        x: np.ndarray,
        y: np.ndarray,
        weights: np.ndarray
    ) -> complex:
        """Weighted inner product <x, y>_w = sum(w_i * x_i * conj(y_i))."""
        return np.sum(weights * x * np.conj(y))

    # ========== Orthogonality ==========

    def is_orthogonal(
        self,
        x: np.ndarray,
        y: np.ndarray,
        ip: Callable = None
    ) -> bool:
        """Check if x and y are orthogonal."""
        if ip is None:
            ip = self.standard_inner_product
        return abs(ip(x, y)) < self._epsilon

    def is_orthonormal_set(
        self,
        vectors: List[np.ndarray],
        ip: Callable = None
    ) -> Dict[str, Any]:
        """Check if vectors form an orthonormal set."""
        if ip is None:
            ip = self.standard_inner_product

        n = len(vectors)
        orthogonal = True
        normalized = True

        for i in range(n):
            # Check normalization
            if abs(ip(vectors[i], vectors[i]) - 1) > self._epsilon:
                normalized = False

            # Check orthogonality
            for j in range(i + 1, n):
                if abs(ip(vectors[i], vectors[j])) > self._epsilon:
                    orthogonal = False

        return {
            "is_orthonormal": orthogonal and normalized,
            "is_orthogonal": orthogonal,
            "is_normalized": normalized,
            "size": n
        }

    def gram_schmidt(
        self,
        vectors: List[np.ndarray],
        ip: Callable = None
    ) -> List[np.ndarray]:
        """
        Gram-Schmidt orthonormalization.

        Args:
            vectors: Input vectors
            ip: Inner product (default: standard)

        Returns:
            Orthonormal vectors
        """
        if ip is None:
            ip = self.standard_inner_product

        orthonormal = []

        for v in vectors:
            # Subtract projections onto previous vectors
            u = v.copy().astype(complex)

            for e in orthonormal:
                u = u - ip(v, e) * e

            # Normalize
            norm = np.sqrt(ip(u, u).real)

            if norm > self._epsilon:
                orthonormal.append(u / norm)

        return orthonormal

    # ========== Projections ==========

    def project_onto_vector(
        self,
        x: np.ndarray,
        v: np.ndarray,
        ip: Callable = None
    ) -> np.ndarray:
        """
        Project x onto the span of v.

        proj_v(x) = (<x, v> / <v, v>) * v
        """
        if ip is None:
            ip = self.standard_inner_product

        coeff = ip(x, v) / ip(v, v)
        return coeff * v

    def project_onto_subspace(
        self,
        x: np.ndarray,
        basis: List[np.ndarray],
        ip: Callable = None
    ) -> ProjectionResult:
        """
        Project x onto subspace spanned by basis.

        If basis is orthonormal: proj(x) = sum(<x, e_i> * e_i)

        Args:
            x: Vector to project
            basis: Orthonormal basis of subspace
            ip: Inner product

        Returns:
            ProjectionResult
        """
        if ip is None:
            ip = self.standard_inner_product

        # Orthonormalize basis first
        ortho_basis = self.gram_schmidt(basis, ip)

        projection = np.zeros_like(x, dtype=complex)
        coefficients = []

        for e in ortho_basis:
            coeff = ip(x, e)
            coefficients.append(coeff)
            projection += coeff * e

        projection = projection.real if np.allclose(projection.imag, 0) else projection
        distance = np.sqrt(ip(x - projection, x - projection).real)

        return ProjectionResult(
            projection=projection,
            distance=distance,
            coefficients=coefficients,
            details={"basis_size": len(ortho_basis)}
        )

    def orthogonal_complement(
        self,
        subspace_basis: List[np.ndarray],
        full_dim: int,
        ip: Callable = None
    ) -> List[np.ndarray]:
        """
        Find orthonormal basis for orthogonal complement.

        Args:
            subspace_basis: Basis of subspace
            full_dim: Dimension of full space
            ip: Inner product

        Returns:
            Orthonormal basis of complement
        """
        if ip is None:
            ip = self.standard_inner_product

        # Orthonormalize subspace basis
        ortho_sub = self.gram_schmidt(subspace_basis, ip)

        # Start with standard basis and orthogonalize
        complement = []

        for i in range(full_dim):
            e_i = np.zeros(full_dim)
            e_i[i] = 1.0

            # Subtract components in subspace
            v = e_i.copy().astype(complex)
            for u in ortho_sub:
                v = v - ip(e_i, u) * u

            # Check if linearly independent from existing complement
            for u in complement:
                v = v - ip(v, u) * u

            norm = np.sqrt(ip(v, v).real)
            if norm > self._epsilon:
                complement.append(v / norm)

        return complement

    # ========== Fourier Expansion ==========

    def fourier_coefficients(
        self,
        f: Callable[[float], float],
        n_terms: int,
        period: float = 2 * np.pi
    ) -> np.ndarray:
        """
        Compute Fourier coefficients.

        f(x) ~ a_0/2 + sum(a_n cos(nx) + b_n sin(nx))

        Returns coefficients as [a_0, a_1, b_1, a_2, b_2, ...]
        """
        L = period / 2
        n_points = 1000
        x = np.linspace(-L, L, n_points)
        dx = 2 * L / (n_points - 1)

        coeffs = []

        # a_0
        a_0 = (1/L) * sum(f(xi) * dx for xi in x)
        coeffs.append(a_0)

        for n in range(1, n_terms + 1):
            # a_n
            a_n = (1/L) * sum(f(xi) * np.cos(n * np.pi * xi / L) * dx for xi in x)
            # b_n
            b_n = (1/L) * sum(f(xi) * np.sin(n * np.pi * xi / L) * dx for xi in x)
            coeffs.extend([a_n, b_n])

        return np.array(coeffs)

    def fourier_series(
        self,
        f: Callable[[float], float],
        n_terms: int,
        period: float = 2 * np.pi
    ) -> FourierResult:
        """
        Compute Fourier series expansion and verify Parseval.

        Args:
            f: Function to expand
            n_terms: Number of terms
            period: Period of function

        Returns:
            FourierResult
        """
        L = period / 2
        coeffs = self.fourier_coefficients(f, n_terms, period)

        # Build partial sum function
        def partial_sum(x):
            """Perform partial sum operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.partial_sum(...)
            """
            result = coeffs[0] / 2
            for n in range(1, n_terms + 1):
                a_n = coeffs[2*n - 1]
                b_n = coeffs[2*n]
                result += a_n * np.cos(n * np.pi * x / L)
                result += b_n * np.sin(n * np.pi * x / L)
            return result

        # Parseval's theorem
        # (1/L) * integral(|f|^2) = a_0^2/2 + sum(a_n^2 + b_n^2)

        # Left side
        n_points = 1000
        x = np.linspace(-L, L, n_points)
        dx = 2 * L / (n_points - 1)
        parseval_lhs = (1/L) * sum(f(xi)**2 * dx for xi in x)

        # Right side
        parseval_rhs = coeffs[0]**2 / 2
        for n in range(1, n_terms + 1):
            parseval_rhs += coeffs[2*n - 1]**2 + coeffs[2*n]**2

        return FourierResult(
            coefficients=coeffs,
            partial_sum=partial_sum,
            parseval_lhs=parseval_lhs,
            parseval_rhs=parseval_rhs,
            details={
                "n_terms": n_terms,
                "parseval_error": abs(parseval_lhs - parseval_rhs)
            }
        )

    def bessel_inequality(
        self,
        x: np.ndarray,
        orthonormal_set: List[np.ndarray],
        ip: Callable = None
    ) -> Dict[str, Any]:
        """
        Verify Bessel's inequality.

        sum(|<x, e_n>|^2) <= ||x||^2

        Args:
            x: Vector
            orthonormal_set: Orthonormal vectors
            ip: Inner product

        Returns:
            Dictionary with Bessel check
        """
        if ip is None:
            ip = self.standard_inner_product

        # Left side: sum of squared coefficients
        lhs = sum(abs(ip(x, e))**2 for e in orthonormal_set)

        # Right side: squared norm
        rhs = ip(x, x).real

        return {
            "sum_squared_coefficients": lhs,
            "squared_norm": rhs,
            "bessel_holds": lhs <= rhs + self._epsilon,
            "equality": abs(lhs - rhs) < self._epsilon,  # Equality when complete
            "parseval_holds": abs(lhs - rhs) < 0.01 * rhs
        }

    # ========== Spectral Theory ==========

    def spectral_decomposition(
        self,
        A: np.ndarray
    ) -> Dict[str, Any]:
        """
        Spectral decomposition for self-adjoint operators.

        A = sum(lambda_i * P_i) where P_i are orthogonal projections.

        Args:
            A: Self-adjoint matrix

        Returns:
            Dictionary with spectral decomposition
        """
        # Check self-adjointness
        is_selfadjoint = np.allclose(A, A.conj().T)

        if not is_selfadjoint:
            return {
                "error": "Matrix not self-adjoint",
                "is_selfadjoint": False
            }

        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(A)

        # Build projection operators
        projections = []
        for i, lam in enumerate(eigenvalues):
            v = eigenvectors[:, i:i+1]
            P_i = v @ v.conj().T
            projections.append({"eigenvalue": lam, "projection": P_i})

        # Verify reconstruction
        A_reconstructed = sum(p["eigenvalue"] * p["projection"] for p in projections)
        reconstruction_error = np.linalg.norm(A - A_reconstructed)

        return {
            "is_selfadjoint": True,
            "eigenvalues": eigenvalues.tolist(),
            "eigenvectors": eigenvectors,
            "projections": projections,
            "reconstruction_error": reconstruction_error
        }

    def check_compact_operator(
        self,
        A: np.ndarray
    ) -> Dict[str, Any]:
        """
        Check properties of compact operator.

        For finite-dimensional spaces, all operators are compact.
        For infinite-dimensional, check if singular values go to 0.

        Args:
            A: Matrix representation

        Returns:
            Dictionary with compact operator analysis
        """
        # Singular value decomposition
        U, s, Vh = np.linalg.svd(A)

        # In finite dim, always compact
        is_compact = True

        # Spectral properties
        spectrum = np.linalg.eigvals(A)

        return {
            "is_compact": is_compact,
            "singular_values": s.tolist(),
            "rank": np.sum(s > self._epsilon),
            "spectrum": spectrum.tolist(),
            "spectral_radius": np.max(np.abs(spectrum)),
            "is_finite_rank": np.sum(s > self._epsilon) < len(s)
        }
