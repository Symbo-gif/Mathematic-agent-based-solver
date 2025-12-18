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
CurvatureSpecialist - Riemannian Curvature Tensors
===================================================

Provides comprehensive Riemannian curvature computations:
- Christoffel symbols (connection coefficients)
- Riemann curvature tensor R^i_jkl
- Ricci tensor R_ij
- Scalar curvature R
- Sectional curvature K(π)
- Weyl conformal tensor (dimension >= 3)

NO SYMPY - Pure Python/NumPy implementation with numerical derivatives.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


@dataclass
class ChristoffelSymbols:
    """Christoffel symbols Γ^k_ij of the second kind."""
    components: np.ndarray  # Shape (n, n, n): components[k, i, j] = Γ^k_ij
    point: np.ndarray
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiemannTensor:
    """Riemann curvature tensor R^i_jkl."""
    components: np.ndarray  # Shape (n, n, n, n): components[i, j, k, l] = R^i_jkl
    point: np.ndarray
    dimension: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CurvatureAnalysis:
    """Complete curvature analysis."""
    riemann: Optional[np.ndarray] = None
    ricci: Optional[np.ndarray] = None
    scalar_curvature: Optional[float] = None
    sectional_curvatures: Optional[List[float]] = None
    weyl: Optional[np.ndarray] = None
    einstein_tensor: Optional[np.ndarray] = None
    details: Dict[str, Any] = field(default_factory=dict)


class CurvatureSpecialist(BDIAgent):
    """
    BDI Agent for Riemannian curvature tensor computations.

    Capabilities:
    - Compute Christoffel symbols from metric
    - Calculate Riemann curvature tensor
    - Derive Ricci tensor and scalar curvature
    - Compute sectional curvatures
    - Calculate Weyl conformal tensor
    - Einstein tensor for general relativity
    """

    def __init__(self, agent_id='curvature_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_computations: List[str] = []
        self._epsilon = 1e-10
        self._h = 1e-6  # Numerical derivative step

        # Cache for expensive Christoffel computations
        self.christoffel_cache: Dict[str, ChristoffelSymbols] = {}

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.riemannian.curvature',
                agent_id=self.agent_id,
                algorithm='curvature',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for curvature computations.

        Supported operations:
        - compute_christoffel: Christoffel symbols from metric
        - compute_riemann: Riemann curvature tensor
        - compute_ricci: Ricci tensor
        - compute_scalar_curvature: Scalar curvature
        - compute_sectional_curvature: Sectional curvature for plane
        - compute_weyl: Weyl conformal tensor
        - full_curvature_analysis: Complete analysis
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        operation = metadata.get('operation', 'full_curvature_analysis')
        self.recent_computations.append(operation)

        if len(self.recent_computations) > 100:
            self.recent_computations = self.recent_computations[-100:]

        try:
            if operation == 'compute_christoffel':
                return self._handle_christoffel(metadata)
            elif operation == 'compute_riemann':
                return self._handle_riemann(metadata)
            elif operation == 'compute_ricci':
                return self._handle_ricci(metadata)
            elif operation == 'compute_scalar_curvature':
                return self._handle_scalar_curvature(metadata)
            elif operation == 'compute_sectional_curvature':
                return self._handle_sectional_curvature(metadata)
            elif operation == 'compute_weyl':
                return self._handle_weyl(metadata)
            elif operation == 'full_curvature_analysis':
                return self._handle_full_analysis(metadata)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}',
                    'supported_operations': [
                        'compute_christoffel', 'compute_riemann', 'compute_ricci',
                        'compute_scalar_curvature', 'compute_sectional_curvature',
                        'compute_weyl', 'full_curvature_analysis'
                    ]
                }
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation}

    def _handle_christoffel(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Christoffel symbol computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))

        christoffel = self.compute_christoffel_symbols(metric_fn, point)

        return {
            'success': True,
            'operation': 'compute_christoffel',
            'christoffel': christoffel.components.tolist(),
            'point': point.tolist(),
            'dimension': christoffel.components.shape[0]
        }

    def _handle_riemann(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Riemann tensor computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))

        riemann = self.compute_riemann_tensor(metric_fn, point)

        return {
            'success': True,
            'operation': 'compute_riemann',
            'riemann_tensor': riemann.components.tolist(),
            'point': point.tolist(),
            'dimension': riemann.dimension
        }

    def _handle_ricci(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Ricci tensor computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))

        ricci = self.compute_ricci_tensor(metric_fn, point)

        return {
            'success': True,
            'operation': 'compute_ricci',
            'ricci_tensor': ricci.tolist(),
            'point': point.tolist()
        }

    def _handle_scalar_curvature(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scalar curvature computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))

        scalar = self.compute_scalar_curvature(metric_fn, point)

        return {
            'success': True,
            'operation': 'compute_scalar_curvature',
            'scalar_curvature': float(scalar),
            'point': point.tolist()
        }

    def _handle_sectional_curvature(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sectional curvature computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))
        v1 = np.array(task_entry.get('tangent_vector_1'))
        v2 = np.array(task_entry.get('tangent_vector_2'))

        K = self.compute_sectional_curvature(metric_fn, point, v1, v2)

        return {
            'success': True,
            'operation': 'compute_sectional_curvature',
            'sectional_curvature': float(K),
            'point': point.tolist(),
            'plane_vectors': [v1.tolist(), v2.tolist()]
        }

    def _handle_weyl(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Weyl tensor computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0, 0]))  # Weyl requires dim >= 3

        weyl = self.compute_weyl_tensor(metric_fn, point)

        return {
            'success': True,
            'operation': 'compute_weyl',
            'weyl_tensor': weyl.tolist(),
            'point': point.tolist()
        }

    def _handle_full_analysis(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle full curvature analysis."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))

        analysis = self.full_curvature_analysis(metric_fn, point)

        return {
            'success': True,
            'operation': 'full_curvature_analysis',
            'scalar_curvature': analysis.scalar_curvature,
            'ricci_tensor': analysis.ricci.tolist() if analysis.ricci is not None else None,
            'details': analysis.details
        }

    # ========== Core Computational Methods ==========

    def compute_christoffel_symbols(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> ChristoffelSymbols:
        """
        Compute Christoffel symbols of the second kind.

        Γ^k_ij = (1/2) g^{kl} (∂_i g_jl + ∂_j g_il - ∂_l g_ij)

        Args:
            metric_fn: Function returning metric tensor at a point
            point: Point to compute at

        Returns:
            ChristoffelSymbols with components
        """
        g = metric_fn(point)
        n = g.shape[0]
        g_inv = np.linalg.inv(g)

        # Compute metric derivatives ∂_k g_ij
        dg = np.zeros((n, n, n))  # dg[i,j,k] = ∂_k g_ij

        for k in range(n):
            e_k = np.zeros(n)
            e_k[k] = self._h

            g_plus = metric_fn(point + e_k)
            g_minus = metric_fn(point - e_k)

            dg[:, :, k] = (g_plus - g_minus) / (2 * self._h)

        # Compute Christoffel symbols
        gamma = np.zeros((n, n, n))  # gamma[k,i,j] = Γ^k_ij

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    for l in range(n):
                        gamma[k, i, j] += 0.5 * g_inv[k, l] * (
                            dg[j, l, i] + dg[i, l, j] - dg[i, j, l]
                        )

        return ChristoffelSymbols(
            components=gamma,
            point=point.copy(),
            details={'dimension': n}
        )

    def compute_riemann_tensor(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> RiemannTensor:
        """
        Compute Riemann curvature tensor.

        R^i_jkl = ∂_k Γ^i_jl - ∂_l Γ^i_jk + Γ^i_mk Γ^m_jl - Γ^i_ml Γ^m_jk

        Args:
            metric_fn: Metric function
            point: Point

        Returns:
            RiemannTensor
        """
        n = len(point)
        gamma = self.compute_christoffel_symbols(metric_fn, point).components

        # Compute Christoffel derivatives ∂_l Γ^k_ij
        dgamma = np.zeros((n, n, n, n))  # dgamma[k,i,j,l] = ∂_l Γ^k_ij

        for l in range(n):
            e_l = np.zeros(n)
            e_l[l] = self._h

            gamma_plus = self.compute_christoffel_symbols(metric_fn, point + e_l).components
            gamma_minus = self.compute_christoffel_symbols(metric_fn, point - e_l).components

            dgamma[:, :, :, l] = (gamma_plus - gamma_minus) / (2 * self._h)

        # Compute Riemann tensor
        R = np.zeros((n, n, n, n))  # R[i,j,k,l] = R^i_jkl

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for l in range(n):
                        # Derivative terms
                        R[i, j, k, l] = dgamma[i, j, l, k] - dgamma[i, j, k, l]

                        # Product terms
                        for m in range(n):
                            R[i, j, k, l] += (
                                gamma[i, m, k] * gamma[m, j, l] -
                                gamma[i, m, l] * gamma[m, j, k]
                            )

        return RiemannTensor(
            components=R,
            point=point.copy(),
            dimension=n,
            details={'computed_via': 'christoffel_derivatives'}
        )

    def compute_ricci_tensor(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> np.ndarray:
        """
        Compute Ricci tensor by contracting Riemann tensor.

        R_ij = R^k_ikj (contraction on first and third indices)

        Args:
            metric_fn: Metric function
            point: Point

        Returns:
            Ricci tensor (n × n matrix)
        """
        R = self.compute_riemann_tensor(metric_fn, point).components
        n = R.shape[0]

        ricci = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    ricci[i, j] += R[k, i, k, j]

        return ricci

    def compute_scalar_curvature(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> float:
        """
        Compute scalar curvature.

        R = g^{ij} R_ij (trace of Ricci tensor)

        Args:
            metric_fn: Metric function
            point: Point

        Returns:
            Scalar curvature
        """
        g = metric_fn(point)
        g_inv = np.linalg.inv(g)
        ricci = self.compute_ricci_tensor(metric_fn, point)

        # Trace: R = g^ij R_ij
        return float(np.sum(g_inv * ricci))

    def compute_sectional_curvature(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        v1: np.ndarray,
        v2: np.ndarray
    ) -> float:
        """
        Compute sectional curvature for 2-plane spanned by v1, v2.

        K(v1, v2) = R(v1, v2, v2, v1) / (g(v1,v1)g(v2,v2) - g(v1,v2)^2)

        Args:
            metric_fn: Metric function
            point: Point
            v1: First tangent vector
            v2: Second tangent vector

        Returns:
            Sectional curvature K
        """
        g = metric_fn(point)
        R = self.compute_riemann_tensor(metric_fn, point).components
        n = len(point)

        # Compute R(v1, v2, v2, v1) = R^i_jkl v1^j v2^k v2^l v1_i
        # where v1_i = g_ij v1^j
        v1_lower = g @ v1
        v2_lower = g @ v2

        numerator = 0.0
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for l in range(n):
                        numerator += R[i, j, k, l] * v1_lower[i] * v1[j] * v2[k] * v2_lower[l]

        # Denominator: g(v1,v1)g(v2,v2) - g(v1,v2)^2
        g11 = v1 @ g @ v1
        g22 = v2 @ g @ v2
        g12 = v1 @ g @ v2

        denominator = g11 * g22 - g12**2

        if abs(denominator) < self._epsilon:
            return 0.0  # Degenerate plane

        return numerator / denominator

    def compute_weyl_tensor(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> np.ndarray:
        """
        Compute Weyl conformal tensor (dimension >= 3).

        C^i_jkl = R^i_jkl - 1/(n-2) (δ^i_k R_jl - δ^i_l R_jk + g_jl R^i_k - g_jk R^i_l)
                  + R/(n-1)(n-2) (δ^i_k g_jl - δ^i_l g_jk)

        Args:
            metric_fn: Metric function
            point: Point (dimension must be >= 3)

        Returns:
            Weyl tensor (n × n × n × n)
        """
        n = len(point)
        if n < 3:
            raise ValueError("Weyl tensor only defined for dimension >= 3")

        g = metric_fn(point)
        g_inv = np.linalg.inv(g)
        R_tensor = self.compute_riemann_tensor(metric_fn, point).components
        Ricci = self.compute_ricci_tensor(metric_fn, point)
        R_scalar = self.compute_scalar_curvature(metric_fn, point)

        # Raise Ricci index: R^i_j = g^{ik} R_kj
        Ricci_mixed = g_inv @ Ricci

        # Weyl tensor
        C = np.zeros((n, n, n, n))

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for l in range(n):
                        C[i, j, k, l] = R_tensor[i, j, k, l]

                        # Ricci correction terms
                        delta_ik = 1.0 if i == k else 0.0
                        delta_il = 1.0 if i == l else 0.0

                        C[i, j, k, l] -= (1.0 / (n - 2)) * (
                            delta_ik * Ricci[j, l] - delta_il * Ricci[j, k] +
                            g[j, l] * Ricci_mixed[i, k] - g[j, k] * Ricci_mixed[i, l]
                        )

                        # Scalar curvature correction
                        C[i, j, k, l] += (R_scalar / ((n - 1) * (n - 2))) * (
                            delta_ik * g[j, l] - delta_il * g[j, k]
                        )

        return C

    def compute_einstein_tensor(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> np.ndarray:
        """
        Compute Einstein tensor for general relativity.

        G_ij = R_ij - (1/2) R g_ij

        Args:
            metric_fn: Metric function
            point: Point

        Returns:
            Einstein tensor (n × n)
        """
        g = metric_fn(point)
        Ricci = self.compute_ricci_tensor(metric_fn, point)
        R_scalar = self.compute_scalar_curvature(metric_fn, point)

        return Ricci - 0.5 * R_scalar * g

    def full_curvature_analysis(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> CurvatureAnalysis:
        """
        Complete curvature analysis at a point.

        Args:
            metric_fn: Metric function
            point: Point

        Returns:
            CurvatureAnalysis with all curvature quantities
        """
        n = len(point)

        # Compute all curvature tensors
        riemann = self.compute_riemann_tensor(metric_fn, point).components
        ricci = self.compute_ricci_tensor(metric_fn, point)
        scalar = self.compute_scalar_curvature(metric_fn, point)
        einstein = self.compute_einstein_tensor(metric_fn, point)

        # Weyl tensor (if dimension >= 3)
        weyl = None
        if n >= 3:
            weyl = self.compute_weyl_tensor(metric_fn, point)

        # Sample sectional curvatures (coordinate planes)
        sectional_curvatures = []
        if n >= 2:
            for i in range(min(n, 3)):
                for j in range(i + 1, min(n, 3)):
                    v1 = np.zeros(n)
                    v2 = np.zeros(n)
                    v1[i] = 1.0
                    v2[j] = 1.0
                    K = self.compute_sectional_curvature(metric_fn, point, v1, v2)
                    sectional_curvatures.append(float(K))

        return CurvatureAnalysis(
            riemann=riemann,
            ricci=ricci,
            scalar_curvature=float(scalar),
            sectional_curvatures=sectional_curvatures,
            weyl=weyl,
            einstein_tensor=einstein,
            details={
                'dimension': n,
                'point': point.tolist(),
                'ricci_trace': float(scalar),
                'einstein_trace': float(np.trace(einstein))
            }
        )

    # ========== BDI Methods ==========

    def update_beliefs(self) -> None:
        """Update agent beliefs."""
        if hasattr(self, 'blackboard') and self.blackboard:
            self.blackboard.write(
                f'curvature_specialist_stats_{self.agent_id}',
                {
                    'tasks_executed': self.tasks_executed,
                    'recent_operations': self.recent_computations[-10:],
                    'cache_size': len(self.christoffel_cache)
                }
            )

    def deliberate(self) -> List[Intention]:
        """Determine intentions."""
        intentions = []

        # Cache management
        if len(self.christoffel_cache) > 50:
            intentions.append(Intention(
                action='clear_christoffel_cache',
                priority=1,
                params={'cache_size': len(self.christoffel_cache)}
            ))

        return intentions

    def execute_step(self, intention: Intention) -> None:
        """Execute BDI intention."""
        if intention.action == 'clear_christoffel_cache':
            # Keep only recent entries
            if len(self.christoffel_cache) > 25:
                keys = list(self.christoffel_cache.keys())
                for key in keys[:-25]:
                    del self.christoffel_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.christoffel_cache),
            'recent_operations': self.recent_computations[-5:]
        }
