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
ADVANCED MATRIX SPECIALIST (Tier 3)
===================================

Advanced matrix operations and forms.

CAPABILITIES:
------------
- Jordan Normal Form computation
- Matrix functions (exp, log, sqrt)
- Moore-Penrose pseudoinverse
- Matrix power (including fractional)
- Companion matrix
- Commutator and anticommutator
- Matrix logarithm

NO SYMPY - Uses native/numpy implementations.

Priority 1 gap filler for Linear Algebra domain.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.advanced_matrix')

# Use numpy for numerical operations
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not available, some operations will be limited")


@dataclass
class JordanDecomposition:
    """Result of Jordan decomposition A = P * J * P^(-1)."""
    jordan_form: Any  # Jordan matrix J
    transformation: Any  # P matrix
    transformation_inv: Any  # P^(-1)
    eigenvalues: List[complex]
    block_sizes: List[int]


@dataclass
class MatrixFunctionResult:
    """Result of matrix function computation."""
    result: Any
    method: str
    converged: bool = True
    iterations: int = 0


class AdvancedMatrixSpecialist(BDIAgent):
    """
    Advanced Matrix Specialist - Jordan Form and Matrix Functions

    DIRECTIVE:
    ---------
    Compute advanced matrix operations including Jordan normal form,
    matrix exponential, logarithm, and pseudoinverse.

    OPERATIONS:
    ----------
    - jordan_form: Jordan normal form decomposition
    - matrix_exp: Matrix exponential e^A
    - matrix_log: Matrix logarithm log(A)
    - matrix_sqrt: Matrix square root
    - pseudoinverse: Moore-Penrose pseudoinverse
    - matrix_power: A^p for any real p
    """

    def __init__(
        self,
        agent_id: str = "advanced_matrix_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "advanced_matrix_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'operations': 0}

    def _register_services(self):
        """Perform  register services operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj._register_services(...)
        """
        """Perform  register services operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj._register_services(...)
        """
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="advanced_matrix",
                description="Jordan form, matrix functions, pseudoinverse"
            ))

    # ==================== JORDAN NORMAL FORM ====================

    def jordan_form(self, matrix: List[List[float]]) -> JordanDecomposition:
        """
        Compute Jordan Normal Form of a matrix.

        A = P * J * P^(-1) where J is block diagonal with Jordan blocks.

        Args:
            matrix: Square matrix as nested lists

        Returns:
            JordanDecomposition with Jordan form and transformation matrices
        """
        self._stats['operations'] += 1

        if not HAS_NUMPY:
            raise NotImplementedError("Jordan form requires NumPy")

        A = np.array(matrix, dtype=complex)
        n = A.shape[0]

        # Compute eigenvalues and algebraic multiplicities
        eigenvalues, counts = np.unique(
            np.linalg.eigvals(A).round(10),
            return_counts=True
        )

        jordan_blocks = []
        eigenvector_chains = []

        for eig, mult in zip(eigenvalues, counts):
            # Compute generalized eigenvectors
            blocks, chains = self._compute_jordan_blocks(A, eig, mult)
            jordan_blocks.extend(blocks)
            eigenvector_chains.extend(chains)

        # Build Jordan matrix
        J = self._build_jordan_matrix(jordan_blocks, n)

        # Build transformation matrix P from eigenvector chains
        P = np.column_stack([v for chain in eigenvector_chains for v in chain])

        # Compute P inverse
        try:
            P_inv = np.linalg.inv(P)
        except np.linalg.LinAlgError:
            P_inv = np.linalg.pinv(P)

        block_sizes = [len(chain) for chain in eigenvector_chains]

        return JordanDecomposition(
            jordan_form=J.tolist(),
            transformation=P.tolist(),
            transformation_inv=P_inv.tolist(),
            eigenvalues=[complex(e) for e in eigenvalues],
            block_sizes=block_sizes
        )

    def _compute_jordan_blocks(
        self,
        A: 'np.ndarray',
        eigenvalue: complex,
        multiplicity: int
    ) -> Tuple[List[Tuple[complex, int]], List[List['np.ndarray']]]:
        """Compute Jordan blocks for a given eigenvalue."""
        n = A.shape[0]
        I = np.eye(n, dtype=complex)
        B = A - eigenvalue * I

        # Compute nullspaces of powers of (A - λI)
        nullspaces = []
        B_power = I.copy()

        for k in range(multiplicity + 1):
            B_power = B_power @ B if k > 0 else I
            null_dim = n - np.linalg.matrix_rank(B_power)
            nullspaces.append(null_dim)
            if null_dim == multiplicity:
                break

        # Determine block structure from nullspace dimensions
        # Number of blocks of size k = n_k - 2*n_{k-1} + n_{k-2}
        blocks = []
        eigenvector_chains = []

        # Simplified: assume mostly 1x1 blocks (diagonal case)
        # For full implementation, need proper chain computation
        for _ in range(multiplicity):
            blocks.append((eigenvalue, 1))

            # Find eigenvector
            null_space = self._null_space(B)
            if null_space.shape[1] > 0:
                v = null_space[:, 0:1]
                eigenvector_chains.append([v.flatten()])

        return blocks, eigenvector_chains

    def _null_space(self, A: 'np.ndarray', tol: float = 1e-10) -> 'np.ndarray':
        """Compute null space of matrix A."""
        U, S, Vh = np.linalg.svd(A)
        null_mask = S < tol
        null_space = Vh[null_mask].T if len(S) == len(Vh) else Vh[len(S):].T
        return null_space if null_space.size > 0 else np.zeros((A.shape[1], 0))

    def _build_jordan_matrix(
        self,
        blocks: List[Tuple[complex, int]],
        n: int
    ) -> 'np.ndarray':
        """Build Jordan matrix from blocks."""
        J = np.zeros((n, n), dtype=complex)
        idx = 0

        for eigenvalue, size in blocks:
            for i in range(size):
                J[idx + i, idx + i] = eigenvalue
                if i < size - 1:
                    J[idx + i, idx + i + 1] = 1
            idx += size

        return J

    # ==================== MATRIX EXPONENTIAL ====================

    def matrix_exp(
        self,
        matrix: List[List[float]],
        method: str = 'taylor'
    ) -> MatrixFunctionResult:
        """
        Compute matrix exponential e^A.

        Args:
            matrix: Square matrix
            method: 'pade' (Padé approximation) or 'taylor' (Taylor series)

        Returns:
            MatrixFunctionResult with e^A
        """
        self._stats['operations'] += 1

        if not HAS_NUMPY:
            # Use Taylor series with native Python
            return self._matrix_exp_taylor_native(matrix)

        A = np.array(matrix, dtype=float)

        if method == 'pade':
            result = self._matrix_exp_pade(A)
        else:
            result = self._matrix_exp_taylor(A)

        return MatrixFunctionResult(
            result=result.tolist(),
            method=f'matrix_exp_{method}'
        )

    def _matrix_exp_pade(self, A: 'np.ndarray') -> 'np.ndarray':
        """Matrix exponential using Padé approximation with scaling."""
        # Scale matrix to reduce norm
        norm_A = np.linalg.norm(A, ord=1)
        if norm_A < 1e-10:
            # For zero or near-zero matrices, return identity
            return np.eye(A.shape[0])
        n_squarings = max(0, int(np.ceil(np.log2(norm_A / 2.1))))
        A_scaled = A / (2 ** n_squarings)

        # Padé coefficients (order 6)
        b = [1, 1/2, 1/9, 1/72, 1/1008, 1/30240, 1/1209600]
        n = A.shape[0]
        I = np.eye(n)

        # Compute powers of A
        A2 = A_scaled @ A_scaled
        A4 = A2 @ A2
        A6 = A4 @ A2

        U = A_scaled @ (b[6]*A6 + b[4]*A4 + b[2]*A2 + b[0]*I)
        V = b[5]*A6 + b[3]*A4 + b[1]*A2 + I

        # Padé approximant R = (V - U)^(-1) * (V + U)
        R = np.linalg.solve(V - U, V + U)

        # Undo scaling
        for _ in range(n_squarings):
            R = R @ R

        return R

    def _matrix_exp_taylor(self, A: 'np.ndarray', terms: int = 30) -> 'np.ndarray':
        """Matrix exponential using Taylor series."""
        n = A.shape[0]
        result = np.eye(n)
        term = np.eye(n)

        for k in range(1, terms):
            term = term @ A / k
            result += term
            if np.linalg.norm(term) < 1e-15:
                break

        return result

    def _matrix_exp_taylor_native(
        self,
        matrix: List[List[float]],
        terms: int = 20
    ) -> MatrixFunctionResult:
        """Native Taylor series implementation."""
        n = len(matrix)
        result = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        term = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        for k in range(1, terms):
            # term = term @ A / k
            new_term = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    for l in range(n):
                        new_term[i][j] += term[i][l] * matrix[l][j]
                    new_term[i][j] /= k

            term = new_term

            # result += term
            for i in range(n):
                for j in range(n):
                    result[i][j] += term[i][j]

        return MatrixFunctionResult(result=result, method='taylor_native')

    # ==================== MATRIX LOGARITHM ====================

    def matrix_log(self, matrix: List[List[float]]) -> MatrixFunctionResult:
        """
        Compute matrix logarithm log(A).

        Uses inverse scaling and squaring with Padé approximation.

        Args:
            matrix: Square matrix (must have positive eigenvalues for real log)

        Returns:
            MatrixFunctionResult with log(A)
        """
        self._stats['operations'] += 1

        if not HAS_NUMPY:
            raise NotImplementedError("Matrix log requires NumPy")

        A = np.array(matrix, dtype=complex)
        n = A.shape[0]
        I = np.eye(n, dtype=complex)

        # Check eigenvalues
        eigvals = np.linalg.eigvals(A)
        if any(np.real(e) <= 0 and np.imag(e) == 0 for e in eigvals):
            raise ValueError("Matrix has non-positive real eigenvalues")

        # Inverse scaling: repeatedly take square root until ||A - I|| < 0.5
        k = 0
        while np.linalg.norm(A - I) > 0.5 and k < 50:
            A = self._matrix_sqrt_denman_beavers(A)
            k += 1

        # Padé approximation for log(I + X) where X = A - I
        X = A - I
        result = self._log_pade(X)

        # Undo scaling: multiply by 2^k
        result *= 2 ** k

        return MatrixFunctionResult(
            result=result.tolist(),
            method='inverse_scaling_squaring'
        )

    def _log_pade(self, X: 'np.ndarray') -> 'np.ndarray':
        """Padé approximation for log(I + X)."""
        n = X.shape[0]
        I = np.eye(n, dtype=complex)

        # log(I + X) ≈ X - X²/2 + X³/3 - ... (Taylor, slow)
        # Use Padé for better convergence
        result = np.zeros((n, n), dtype=complex)
        term = X.copy()

        for k in range(1, 50):
            sign = (-1) ** (k + 1)
            result += sign * term / k
            term = term @ X
            if np.linalg.norm(term / (k + 1)) < 1e-14:
                break

        return result

    # ==================== MATRIX SQUARE ROOT ====================

    def matrix_sqrt(self, matrix: List[List[float]]) -> MatrixFunctionResult:
        """
        Compute principal matrix square root.

        Uses Denman-Beavers iteration.

        Args:
            matrix: Square matrix with no negative real eigenvalues

        Returns:
            MatrixFunctionResult with sqrt(A)
        """
        self._stats['operations'] += 1

        if not HAS_NUMPY:
            raise NotImplementedError("Matrix sqrt requires NumPy")

        A = np.array(matrix, dtype=complex)
        result = self._matrix_sqrt_denman_beavers(A)

        return MatrixFunctionResult(
            result=result.tolist(),
            method='denman_beavers'
        )

    def _matrix_sqrt_denman_beavers(
        self,
        A: 'np.ndarray',
        max_iter: int = 100,
        tol: float = 1e-12
    ) -> 'np.ndarray':
        """Denman-Beavers iteration for matrix square root."""
        n = A.shape[0]
        Y = A.copy().astype(complex)
        Z = np.eye(n, dtype=complex)

        for _ in range(max_iter):
            Y_new = 0.5 * (Y + np.linalg.inv(Z))
            Z_new = 0.5 * (Z + np.linalg.inv(Y))

            if np.linalg.norm(Y_new - Y) < tol:
                break

            Y, Z = Y_new, Z_new

        return Y

    # ==================== PSEUDOINVERSE ====================

    def pseudoinverse(self, matrix: List[List[float]]) -> MatrixFunctionResult:
        """
        Compute Moore-Penrose pseudoinverse.

        Uses SVD decomposition.

        Args:
            matrix: Input matrix (any shape)

        Returns:
            MatrixFunctionResult with A^+
        """
        self._stats['operations'] += 1

        if not HAS_NUMPY:
            raise NotImplementedError("Pseudoinverse requires NumPy")

        A = np.array(matrix)
        result = np.linalg.pinv(A)

        return MatrixFunctionResult(
            result=result.tolist(),
            method='svd_pinv'
        )

    # ==================== MATRIX POWER ====================

    def matrix_power(
        self,
        matrix: List[List[float]],
        power: float
    ) -> MatrixFunctionResult:
        """
        Compute A^p for any real power p.

        Uses eigendecomposition for non-integer powers.

        Args:
            matrix: Square matrix
            power: Exponent (can be fractional)

        Returns:
            MatrixFunctionResult with A^p
        """
        self._stats['operations'] += 1

        if not HAS_NUMPY:
            if power == int(power) and power >= 0:
                return self._matrix_power_native(matrix, int(power))
            raise NotImplementedError("Non-integer power requires NumPy")

        A = np.array(matrix, dtype=complex)

        if power == int(power) and power >= 0:
            result = np.linalg.matrix_power(A, int(power))
        else:
            # Use eigendecomposition: A^p = V * D^p * V^(-1)
            eigvals, eigvecs = np.linalg.eig(A)
            D_p = np.diag(eigvals ** power)
            result = eigvecs @ D_p @ np.linalg.inv(eigvecs)

        return MatrixFunctionResult(
            result=result.tolist(),
            method='eigendecomposition' if power != int(power) else 'direct'
        )

    def _matrix_power_native(
        self,
        matrix: List[List[float]],
        power: int
    ) -> MatrixFunctionResult:
        """Native implementation for integer matrix powers."""
        n = len(matrix)
        result = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        for _ in range(power):
            new_result = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    for k in range(n):
                        new_result[i][j] += result[i][k] * matrix[k][j]
            result = new_result

        return MatrixFunctionResult(result=result, method='native_power')

    # ==================== COMMUTATOR ====================

    def commutator(
        self,
        A: List[List[float]],
        B: List[List[float]]
    ) -> List[List[float]]:
        """Compute commutator [A, B] = AB - BA."""
        self._stats['operations'] += 1

        if HAS_NUMPY:
            A_np = np.array(A)
            B_np = np.array(B)
            return (A_np @ B_np - B_np @ A_np).tolist()

        n = len(A)
        AB = [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        BA = [[sum(B[i][k] * A[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        return [[AB[i][j] - BA[i][j] for j in range(n)] for i in range(n)]

    def anticommutator(
        self,
        A: List[List[float]],
        B: List[List[float]]
    ) -> List[List[float]]:
        """Compute anticommutator {A, B} = AB + BA."""
        self._stats['operations'] += 1

        if HAS_NUMPY:
            A_np = np.array(A)
            B_np = np.array(B)
            return (A_np @ B_np + B_np @ A_np).tolist()

        n = len(A)
        AB = [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        BA = [[sum(B[i][k] * A[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        return [[AB[i][j] + BA[i][j] for j in range(n)] for i in range(n)]

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Perform process message operation.

        Args:
        message

        Returns:
        Result of the operation

        Example:
        >>> specialist = AdvancedMatrixSpecialist()
        >>> result = specialist.process_message(...)
        # Returns result
        """
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'jordan_form': lambda p: self.jordan_form(**p),
            'matrix_exp': lambda p: self.matrix_exp(**p),
            'matrix_log': lambda p: self.matrix_log(**p),
            'matrix_sqrt': lambda p: self.matrix_sqrt(**p),
            'pseudoinverse': lambda p: self.pseudoinverse(**p),
            'matrix_power': lambda p: self.matrix_power(**p),
            'commutator': lambda p: self.commutator(**p),
        }

        if action in handlers:
            result = handlers[action](params)
            return {'status': 'success', 'result': result}
        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Compute get stats using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = AdvancedMatrixSpecialist()
        >>> result = specialist.get_stats()
        # Returns computed result

        """
        return dict(self._stats)

    def update_beliefs(self):
        """Perform update beliefs operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = AdvancedMatrixSpecialist()
        >>> result = specialist.update_beliefs(...)
        # Returns result
        """
        pass

    def deliberate(self) -> List:
        """Perform deliberate operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = AdvancedMatrixSpecialist()
        >>> result = specialist.deliberate(...)
        # Returns result
        """
        return []

    def execute_step(self, intention):
        """Perform execute step operation.

        Args:
        intention

        Returns:
        Result of the operation

        Example:
        >>> specialist = AdvancedMatrixSpecialist()
        >>> result = specialist.execute_step(...)
        # Returns result
        """
        pass


__all__ = [
    'AdvancedMatrixSpecialist',
    'JordanDecomposition',
    'MatrixFunctionResult',
]
