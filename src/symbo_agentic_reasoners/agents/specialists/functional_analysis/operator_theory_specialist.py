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
Operator Theory Specialist
===========================

Provides comprehensive operator theory operations:
- Bounded and unbounded operators
- Spectrum analysis
- Resolvent computation
- Adjoint operators
- Normal, self-adjoint, unitary classifications
- Functional calculus

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum


class OperatorType(Enum):
    """Classification of operators."""
    NORMAL = "normal"
    SELFADJOINT = "self_adjoint"
    UNITARY = "unitary"
    POSITIVE = "positive"
    PROJECTION = "projection"
    NILPOTENT = "nilpotent"
    GENERAL = "general"


class SpectrumType(Enum):
    """Types of spectrum."""
    POINT = "point"  # Eigenvalues
    CONTINUOUS = "continuous"
    RESIDUAL = "residual"


@dataclass
class SpectrumResult:
    """Result from spectrum computation."""
    point_spectrum: List[complex] = field(default_factory=list)
    spectral_radius: float = 0.0
    is_bounded: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolventResult:
    """Result from resolvent computation."""
    resolvent: Optional[np.ndarray] = None
    is_in_resolvent_set: bool = True
    norm: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperatorClassification:
    """Classification of an operator."""
    types: List[OperatorType] = field(default_factory=list)
    properties: Dict[str, bool] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


class OperatorTheorySpecialist:
    """
    BDI Agent for operator theory analysis.

    Capabilities:
    - Classify operators
    - Compute spectrum and resolvent
    - Adjoint operators
    - Functional calculus
    - Operator decompositions
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
        if "operator" in self.beliefs:
            self.desires.append("classify_operator")
        if "spectrum_point" in self.beliefs:
            self.desires.append("compute_resolvent")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "classify_operator":
            A = self.beliefs.get("operator")
            return {"result": self.classify_operator(A)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Operator Classification ==========

    def classify_operator(self, A: np.ndarray) -> OperatorClassification:
        """
        Classify operator by its properties.

        Args:
            A: Matrix representation

        Returns:
            OperatorClassification
        """
        types = []
        properties = {}

        n = A.shape[0]
        A_adj = A.conj().T

        # Check self-adjoint: A = A*
        is_selfadjoint = np.allclose(A, A_adj)
        properties["self_adjoint"] = is_selfadjoint
        if is_selfadjoint:
            types.append(OperatorType.SELFADJOINT)

        # Check normal: AA* = A*A
        AA_adj = A @ A_adj
        A_adj_A = A_adj @ A
        is_normal = np.allclose(AA_adj, A_adj_A)
        properties["normal"] = is_normal
        if is_normal and not is_selfadjoint:
            types.append(OperatorType.NORMAL)

        # Check unitary: A*A = AA* = I
        I = np.eye(n)
        is_unitary = np.allclose(A_adj @ A, I) and np.allclose(A @ A_adj, I)
        properties["unitary"] = is_unitary
        if is_unitary:
            types.append(OperatorType.UNITARY)

        # Check positive: <Ax, x> >= 0 for all x (for self-adjoint)
        is_positive = False
        if is_selfadjoint:
            eigenvalues = np.linalg.eigvalsh(A)
            is_positive = np.all(eigenvalues >= -self._epsilon)
            properties["positive"] = is_positive
            if is_positive:
                types.append(OperatorType.POSITIVE)

        # Check projection: A^2 = A
        is_projection = np.allclose(A @ A, A)
        properties["projection"] = is_projection
        if is_projection:
            types.append(OperatorType.PROJECTION)

        # Check nilpotent: A^k = 0 for some k
        is_nilpotent = False
        A_power = A.copy()
        for k in range(1, n + 1):
            if np.allclose(A_power, 0):
                is_nilpotent = True
                properties["nilpotent_index"] = k
                break
            A_power = A_power @ A
        properties["nilpotent"] = is_nilpotent
        if is_nilpotent:
            types.append(OperatorType.NILPOTENT)

        if not types:
            types.append(OperatorType.GENERAL)

        return OperatorClassification(
            types=types,
            properties=properties,
            details={"dimension": n}
        )

    # ========== Spectrum ==========

    def compute_spectrum(self, A: np.ndarray) -> SpectrumResult:
        """
        Compute spectrum of operator.

        For finite-dimensional, spectrum = eigenvalues.

        Args:
            A: Matrix representation

        Returns:
            SpectrumResult
        """
        eigenvalues = np.linalg.eigvals(A)

        spectral_radius = np.max(np.abs(eigenvalues))

        return SpectrumResult(
            point_spectrum=eigenvalues.tolist(),
            spectral_radius=spectral_radius,
            is_bounded=True,
            details={
                "dimension": A.shape[0],
                "multiplicity": self._compute_multiplicities(A, eigenvalues)
            }
        )

    def _compute_multiplicities(
        self,
        A: np.ndarray,
        eigenvalues: np.ndarray
    ) -> Dict[complex, int]:
        """Compute algebraic multiplicities of eigenvalues."""
        unique_eigs = []
        multiplicities = {}

        for lam in eigenvalues:
            # Check if already counted
            found = False
            for existing in unique_eigs:
                if abs(lam - existing) < self._epsilon:
                    multiplicities[existing] += 1
                    found = True
                    break

            if not found:
                unique_eigs.append(lam)
                multiplicities[lam] = 1

        return multiplicities

    def spectral_radius_formula(
        self,
        A: np.ndarray,
        n_powers: int = 20
    ) -> Dict[str, Any]:
        """
        Compute spectral radius using Gelfand formula.

        r(A) = lim ||A^n||^(1/n)

        Args:
            A: Matrix
            n_powers: Powers to compute

        Returns:
            Dictionary with spectral radius estimates
        """
        estimates = []

        A_power = A.copy()
        for n in range(1, n_powers + 1):
            norm = np.linalg.norm(A_power, 2)
            estimate = norm ** (1/n)
            estimates.append(estimate)
            A_power = A_power @ A

        # True spectral radius
        true_radius = np.max(np.abs(np.linalg.eigvals(A)))

        return {
            "gelfand_estimates": estimates,
            "converges_to": estimates[-1],
            "true_spectral_radius": true_radius,
            "error": abs(estimates[-1] - true_radius)
        }

    # ========== Resolvent ==========

    def compute_resolvent(
        self,
        A: np.ndarray,
        z: complex
    ) -> ResolventResult:
        """
        Compute resolvent R(z, A) = (zI - A)^(-1).

        z is in resolvent set iff (zI - A) is invertible.

        Args:
            A: Operator matrix
            z: Complex number

        Returns:
            ResolventResult
        """
        n = A.shape[0]
        zI_minus_A = z * np.eye(n) - A

        # Check if invertible
        det = np.linalg.det(zI_minus_A)

        if abs(det) < self._epsilon:
            return ResolventResult(
                resolvent=None,
                is_in_resolvent_set=False,
                details={"z_in_spectrum": True}
            )

        resolvent = np.linalg.inv(zI_minus_A)
        norm = np.linalg.norm(resolvent, 2)

        return ResolventResult(
            resolvent=resolvent,
            is_in_resolvent_set=True,
            norm=norm,
            details={"z": z, "determinant": det}
        )

    def resolvent_identity(
        self,
        A: np.ndarray,
        z1: complex,
        z2: complex
    ) -> Dict[str, Any]:
        """
        Verify first resolvent identity.

        R(z1) - R(z2) = (z2 - z1) * R(z1) * R(z2)

        Args:
            A: Operator
            z1, z2: Complex numbers in resolvent set

        Returns:
            Dictionary with verification
        """
        R1 = self.compute_resolvent(A, z1)
        R2 = self.compute_resolvent(A, z2)

        if not R1.is_in_resolvent_set or not R2.is_in_resolvent_set:
            return {"valid": False, "reason": "points_in_spectrum"}

        lhs = R1.resolvent - R2.resolvent
        rhs = (z2 - z1) * R1.resolvent @ R2.resolvent

        error = np.linalg.norm(lhs - rhs)

        return {
            "identity_holds": error < self._epsilon,
            "error": error,
            "z1": z1,
            "z2": z2
        }

    # ========== Adjoint Operators ==========

    def compute_adjoint(self, A: np.ndarray) -> np.ndarray:
        """Compute adjoint A* = conjugate transpose."""
        return A.conj().T

    def verify_adjoint(
        self,
        A: np.ndarray,
        A_star: np.ndarray,
        n_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Verify A* is adjoint of A.

        <Ax, y> = <x, A*y> for all x, y

        Args:
            A: Operator
            A_star: Proposed adjoint
            n_samples: Test samples

        Returns:
            Dictionary with verification
        """
        n = A.shape[0]
        max_error = 0

        for _ in range(n_samples):
            x = np.random.randn(n) + 1j * np.random.randn(n)
            y = np.random.randn(n) + 1j * np.random.randn(n)

            lhs = np.vdot(A @ x, y)
            rhs = np.vdot(x, A_star @ y)

            error = abs(lhs - rhs)
            max_error = max(max_error, error)

        is_adjoint = max_error < self._epsilon

        return {
            "is_adjoint": is_adjoint,
            "max_error": max_error,
            "samples_tested": n_samples
        }

    # ========== Functional Calculus ==========

    def apply_function(
        self,
        A: np.ndarray,
        f: Callable[[complex], complex]
    ) -> np.ndarray:
        """
        Apply function to operator via spectral decomposition.

        f(A) = sum(f(lambda_i) * P_i)

        Works for normal operators.

        Args:
            A: Normal operator
            f: Function to apply

        Returns:
            f(A) matrix
        """
        # Check if normal
        A_adj = A.conj().T
        if not np.allclose(A @ A_adj, A_adj @ A):
            # Use Taylor series as fallback
            return self._taylor_function(A, f)

        # Spectral decomposition for normal operators
        eigenvalues, eigenvectors = np.linalg.eig(A)

        n = A.shape[0]
        f_A = np.zeros((n, n), dtype=complex)

        for i, lam in enumerate(eigenvalues):
            v = eigenvectors[:, i:i+1]
            P_i = v @ v.conj().T
            f_A += f(lam) * P_i

        return f_A

    def _taylor_function(
        self,
        A: np.ndarray,
        f: Callable[[complex], complex],
        n_terms: int = 20
    ) -> np.ndarray:
        """Approximate f(A) via Taylor series."""
        # Estimate Taylor coefficients numerically
        h = 1e-6
        coeffs = []

        for k in range(n_terms):
            # k-th derivative at 0 / k!
            # Use finite differences
            c_k = self._nth_derivative(f, 0, k, h) / np.math.factorial(k)
            coeffs.append(c_k)

        # f(A) = sum(c_k * A^k)
        n = A.shape[0]
        f_A = np.zeros((n, n), dtype=complex)
        A_power = np.eye(n)

        for c_k in coeffs:
            f_A += c_k * A_power
            A_power = A_power @ A

        return f_A

    def _nth_derivative(
        self,
        f: Callable[[complex], complex],
        x: complex,
        n: int,
        h: float
    ) -> complex:
        """Compute n-th derivative numerically."""
        if n == 0:
            return f(x)

        # Use central differences recursively
        return (self._nth_derivative(f, x + h, n - 1, h) -
                self._nth_derivative(f, x - h, n - 1, h)) / (2 * h)

    def matrix_exponential(self, A: np.ndarray) -> np.ndarray:
        """
        Compute matrix exponential exp(A).

        Uses eigendecomposition for diagonalizable matrices.
        """
        return self.apply_function(A, np.exp)

    def matrix_logarithm(self, A: np.ndarray) -> np.ndarray:
        """
        Compute matrix logarithm log(A).

        Requires A to have positive eigenvalues.
        """
        eigenvalues = np.linalg.eigvals(A)
        if np.any(eigenvalues.real <= 0):
            raise ValueError("Matrix log requires positive eigenvalues")

        return self.apply_function(A, np.log)

    # ========== Decompositions ==========

    def polar_decomposition(self, A: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Compute polar decomposition A = U * P.

        U is unitary (or partial isometry), P is positive.

        Args:
            A: Matrix

        Returns:
            Dictionary with U and P
        """
        # A = U * sqrt(A* A)
        U, s, Vh = np.linalg.svd(A)

        # P = sqrt(A* A)
        P = Vh.conj().T @ np.diag(s) @ Vh

        # U from SVD
        U_polar = U @ Vh

        return {
            "U": U_polar,
            "P": P,
            "verification_error": np.linalg.norm(A - U_polar @ P)
        }

    def schur_decomposition(self, A: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Compute Schur decomposition A = Q T Q*.

        T is upper triangular, Q is unitary.

        Args:
            A: Matrix

        Returns:
            Dictionary with Q and T
        """
        from scipy.linalg import schur

        try:
            T, Q = schur(A, output='complex')
        except ImportError:
            # Fallback: use eigendecomposition
            eigenvalues, Q = np.linalg.eig(A)
            T = np.diag(eigenvalues)

        return {
            "Q": Q,
            "T": T,
            "eigenvalues": np.diag(T).tolist(),
            "verification_error": np.linalg.norm(A - Q @ T @ Q.conj().T)
        }

    # ========== Numerical Range ==========

    def numerical_range(
        self,
        A: np.ndarray,
        n_samples: int = 1000
    ) -> Dict[str, Any]:
        """
        Compute numerical range W(A) = {<Ax, x> : ||x|| = 1}.

        For finite-dimensional, W(A) is convex and contains spectrum.

        Args:
            A: Operator matrix
            n_samples: Unit vectors to sample

        Returns:
            Dictionary with numerical range information
        """
        n = A.shape[0]
        values = []

        for _ in range(n_samples):
            # Random unit vector
            x = np.random.randn(n) + 1j * np.random.randn(n)
            x = x / np.linalg.norm(x)

            # <Ax, x>
            val = np.vdot(A @ x, x)
            values.append(val)

        values = np.array(values)

        # Spectrum should be contained in numerical range
        spectrum = np.linalg.eigvals(A)

        return {
            "sample_points": values.tolist(),
            "min_real": np.min(values.real),
            "max_real": np.max(values.real),
            "min_imag": np.min(values.imag),
            "max_imag": np.max(values.imag),
            "spectrum": spectrum.tolist(),
            "spectrum_in_range": True  # Always true by Toeplitz-Hausdorff
        }
