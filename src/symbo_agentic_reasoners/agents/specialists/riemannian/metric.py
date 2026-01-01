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
MetricTensorSpecialist - Riemannian Metric Operations
======================================================

Provides comprehensive Riemannian metric tensor analysis:
- Metric tensor computation and verification
- Signature classification (Riemannian, Lorentzian, pseudo-Riemannian)
- Distance and volume element computation
- Isometry verification
- Standard metrics (Euclidean, sphere, hyperbolic, etc.)

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


@dataclass
class MetricTensor:
    """Metric tensor g_ij with associated properties."""
    components: np.ndarray  # n x n symmetric matrix
    coordinates: List[str] = field(default_factory=list)
    inverse: Optional[np.ndarray] = None
    determinant: float = 0.0
    signature: Tuple[int, int] = (0, 0)  # (positive, negative) eigenvalues
    point: Optional[np.ndarray] = None


@dataclass
class IsometryResult:
    """Result from isometry verification."""
    is_isometry: bool
    transformation_matrix: Optional[np.ndarray] = None
    pullback_metric: Optional[np.ndarray] = None
    error_norm: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class MetricTensorSpecialist(BDIAgent):
    """
    BDI Agent for Riemannian metric tensor operations.

    Capabilities:
    - Compute metric tensor properties
    - Verify metric signature (Riemannian, Lorentzian)
    - Compute distances and angles
    - Calculate volume elements
    - Verify isometries and conformal maps
    - Standard metrics: Euclidean, sphere, hyperbolic, etc.
    """

    def __init__(self, agent_id='metric_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_computations: List[str] = []
        self._epsilon = 1e-10
        self._h = 1e-6  # Step for numerical derivatives

        # Cache for expensive computations
        self.metric_cache: Dict[str, MetricTensor] = {}

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.riemannian.metric',
                agent_id=self.agent_id,
                algorithm='metric',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for processing metric tensor tasks.

        Supported operations:
        - compute_metric: Create metric tensor at a point
        - verify_signature: Check metric signature
        - compute_distance: Distance between two points
        - check_isometry: Verify if transformation is isometry
        - compute_volume_element: Volume form
        - analyze_metric: Full metric analysis
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        operation = metadata.get('operation', 'analyze_metric')
        self.recent_computations.append(operation)

        # Keep only recent 100 computations
        if len(self.recent_computations) > 100:
            self.recent_computations = self.recent_computations[-100:]

        try:
            if operation == 'compute_metric':
                return self._handle_compute_metric(metadata)
            elif operation == 'verify_signature':
                return self._handle_verify_signature(metadata)
            elif operation == 'compute_distance':
                return self._handle_compute_distance(metadata)
            elif operation == 'check_isometry':
                return self._handle_check_isometry(metadata)
            elif operation == 'compute_volume_element':
                return self._handle_volume_element(metadata)
            elif operation == 'analyze_metric':
                return self._handle_analyze_metric(metadata)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}',
                    'supported_operations': [
                        'compute_metric', 'verify_signature', 'compute_distance',
                        'check_isometry', 'compute_volume_element', 'analyze_metric'
                    ]
                }
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation}

    def _handle_compute_metric(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute metric tensor at a point."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))
        coordinates = task_entry.get('coordinates', [f'x{i}' for i in range(len(point))])

        if metric_fn is None:
            # Default to Euclidean
            metric_fn = self.euclidean_metric

        metric = self.compute_metric_tensor(metric_fn, point, coordinates)

        return {
            'success': True,
            'operation': 'compute_metric',
            'metric_components': metric.components.tolist(),
            'inverse': metric.inverse.tolist() if metric.inverse is not None else None,
            'determinant': float(metric.determinant),
            'signature': metric.signature,
            'coordinates': metric.coordinates
        }

    def _handle_verify_signature(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Verify metric signature."""
        metric_components = np.array(task_entry.get('metric'))

        result = self.verify_signature(metric_components)

        return {
            'success': True,
            'operation': 'verify_signature',
            **result
        }

    def _handle_compute_distance(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute distance between two points."""
        metric_fn = task_entry.get('metric_function')
        point_a = np.array(task_entry.get('point_a'))
        point_b = np.array(task_entry.get('point_b'))

        distance = self.compute_distance(metric_fn, point_a, point_b)

        return {
            'success': True,
            'operation': 'compute_distance',
            'distance': float(distance),
            'point_a': point_a.tolist(),
            'point_b': point_b.tolist()
        }

    def _handle_check_isometry(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Check if transformation is an isometry."""
        metric_1_fn = task_entry.get('metric_1')
        metric_2_fn = task_entry.get('metric_2')
        transformation = task_entry.get('transformation')
        point = np.array(task_entry.get('point', [0, 0]))

        result = self.check_isometry(metric_1_fn, metric_2_fn, transformation, point)

        return {
            'success': True,
            'operation': 'check_isometry',
            'is_isometry': result.is_isometry,
            'error_norm': float(result.error_norm),
            'details': result.details
        }

    def _handle_volume_element(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute volume element."""
        metric_components = np.array(task_entry.get('metric'))

        volume_element = self.compute_volume_element(metric_components)

        return {
            'success': True,
            'operation': 'compute_volume_element',
            'volume_element': float(volume_element)
        }

    def _handle_analyze_metric(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive metric analysis."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))

        analysis = self.analyze_metric(metric_fn, point)

        return {
            'success': True,
            'operation': 'analyze_metric',
            **analysis
        }

    # ========== Core Computational Methods ==========

    def compute_metric_tensor(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        coordinates: Optional[List[str]] = None
    ) -> MetricTensor:
        """
        Compute metric tensor at a given point.

        Args:
            metric_fn: Function returning metric matrix g_ij at a point
            point: Point in manifold coordinates
            coordinates: Coordinate names

        Returns:
            MetricTensor with computed properties
        """
        # Evaluate metric at point
        g = metric_fn(point)
        n = g.shape[0]

        if coordinates is None:
            coordinates = [f'x{i}' for i in range(n)]

        # Verify symmetry
        if not np.allclose(g, g.T, atol=self._epsilon):
            raise ValueError("Metric tensor must be symmetric")

        # Compute determinant
        det = np.linalg.det(g)
        if abs(det) < self._epsilon:
            raise ValueError("Metric tensor is degenerate (det = 0)")

        # Compute inverse
        g_inv = np.linalg.inv(g)

        # Compute signature
        eigenvalues = np.linalg.eigvalsh(g)
        positive = np.sum(eigenvalues > self._epsilon)
        negative = np.sum(eigenvalues < -self._epsilon)
        signature = (positive, negative)

        return MetricTensor(
            components=g,
            coordinates=coordinates,
            inverse=g_inv,
            determinant=det,
            signature=signature,
            point=point.copy()
        )

    def verify_signature(self, metric: np.ndarray) -> Dict[str, Any]:
        """
        Verify metric signature and classify metric type.

        Args:
            metric: Metric tensor matrix

        Returns:
            Dictionary with signature classification
        """
        eigenvalues = np.linalg.eigvalsh(metric)
        n = len(eigenvalues)

        positive = np.sum(eigenvalues > self._epsilon)
        negative = np.sum(eigenvalues < -self._epsilon)
        zero = np.sum(np.abs(eigenvalues) <= self._epsilon)

        signature = (positive, negative)

        # Classify metric type
        is_riemannian = (positive == n and negative == 0)
        is_lorentzian = (signature == (n-1, 1) or signature == (1, n-1))
        is_degenerate = (zero > 0)

        metric_type = 'degenerate' if is_degenerate else (
            'Riemannian' if is_riemannian else (
                'Lorentzian' if is_lorentzian else 'pseudo-Riemannian'
            )
        )

        return {
            'signature': signature,
            'eigenvalues': eigenvalues.tolist(),
            'metric_type': metric_type,
            'is_riemannian': is_riemannian,
            'is_lorentzian': is_lorentzian,
            'is_degenerate': is_degenerate
        }

    def compute_distance(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point_a: np.ndarray,
        point_b: np.ndarray,
        n_steps: int = 100
    ) -> float:
        """
        Compute approximate distance between two points.

        Uses straight-line path in coordinate space and integrates
        arc length. For true geodesic distance, use GeodesicSpecialist.

        Args:
            metric_fn: Metric function
            point_a: Starting point
            point_b: Ending point
            n_steps: Number of integration steps

        Returns:
            Approximate distance
        """
        # Parametrize straight line path
        distance = 0.0

        for i in range(n_steps):
            t = i / n_steps
            point = (1 - t) * point_a + t * point_b

            # Tangent vector
            v = (point_b - point_a) / n_steps

            # Metric at point
            g = metric_fn(point)

            # ds^2 = g_ij v^i v^j
            ds_squared = v @ g @ v

            if ds_squared > 0:
                distance += np.sqrt(ds_squared)
            elif ds_squared < 0:
                # Lorentzian metric - return imaginary distance indication
                distance += np.sqrt(-ds_squared) * 1j

        return np.real(distance) if np.isreal(distance) else distance

    def check_isometry(
        self,
        metric_1: Callable[[np.ndarray], np.ndarray],
        metric_2: Callable[[np.ndarray], np.ndarray],
        transformation: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        tolerance: float = 1e-6
    ) -> IsometryResult:
        """
        Check if a transformation is an isometry.

        An isometry preserves the metric: phi^* g_2 = g_1

        Args:
            metric_1: First metric (domain)
            metric_2: Second metric (codomain)
            transformation: Map phi: M1 -> M2
            point: Point to verify at
            tolerance: Numerical tolerance

        Returns:
            IsometryResult
        """
        # Compute Jacobian of transformation
        n = len(point)
        jacobian = np.zeros((n, n))

        phi_p = transformation(point)

        for i in range(n):
            e_i = np.zeros(n)
            e_i[i] = self._h

            phi_plus = transformation(point + e_i)
            phi_minus = transformation(point - e_i)

            jacobian[:, i] = (phi_plus - phi_minus) / (2 * self._h)

        # Pullback metric: (phi^* g_2)_ij = J^k_i g_2_kl J^l_j
        g_1 = metric_1(point)
        g_2 = metric_2(phi_p)

        pullback = jacobian.T @ g_2 @ jacobian

        # Check if pullback equals original metric
        error = np.linalg.norm(pullback - g_1, ord='fro')
        is_isometry = (error < tolerance)

        return IsometryResult(
            is_isometry=is_isometry,
            transformation_matrix=jacobian,
            pullback_metric=pullback,
            error_norm=float(error),
            details={
                'metric_1': g_1.tolist(),
                'metric_2': g_2.tolist(),
                'pullback': pullback.tolist(),
                'point': point.tolist(),
                'image_point': phi_p.tolist()
            }
        )

    def compute_volume_element(self, metric: np.ndarray) -> float:
        """
        Compute volume element sqrt(|det(g)|).

        Args:
            metric: Metric tensor

        Returns:
            Volume element
        """
        det = np.linalg.det(metric)
        return np.sqrt(np.abs(det))

    def compute_angles(
        self,
        metric: np.ndarray,
        v1: np.ndarray,
        v2: np.ndarray
    ) -> float:
        """
        Compute angle between two tangent vectors.

        cos(theta) = g(v1, v2) / (||v1|| ||v2||)

        Args:
            metric: Metric tensor
            v1: First tangent vector
            v2: Second tangent vector

        Returns:
            Angle in radians
        """
        # Inner products
        g_v1_v2 = v1 @ metric @ v2
        g_v1_v1 = v1 @ metric @ v1
        g_v2_v2 = v2 @ metric @ v2

        # Magnitudes
        norm_v1 = np.sqrt(np.abs(g_v1_v1))
        norm_v2 = np.sqrt(np.abs(g_v2_v2))

        if norm_v1 < self._epsilon or norm_v2 < self._epsilon:
            return 0.0

        # Angle
        cos_theta = g_v1_v2 / (norm_v1 * norm_v2)
        cos_theta = np.clip(cos_theta, -1, 1)

        return np.arccos(cos_theta)

    def analyze_metric(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> Dict[str, Any]:
        """
        Comprehensive metric analysis at a point.

        Args:
            metric_fn: Metric function
            point: Point to analyze

        Returns:
            Complete analysis dictionary
        """
        metric = self.compute_metric_tensor(metric_fn, point)
        signature_info = self.verify_signature(metric.components)
        volume_elem = self.compute_volume_element(metric.components)

        # Compute principal curvatures (eigenvalues of shape operator)
        eigenvalues = np.linalg.eigvalsh(metric.components)

        return {
            'metric_tensor': metric.components.tolist(),
            'inverse_metric': metric.inverse.tolist(),
            'determinant': float(metric.determinant),
            'volume_element': float(volume_elem),
            'signature': metric.signature,
            'eigenvalues': eigenvalues.tolist(),
            'metric_type': signature_info['metric_type'],
            'is_riemannian': signature_info['is_riemannian'],
            'is_lorentzian': signature_info['is_lorentzian'],
            'point': point.tolist()
        }

    # ========== Standard Metrics ==========

    @staticmethod
    def euclidean_metric(point: np.ndarray) -> np.ndarray:
        """
        Euclidean metric (identity matrix).

        ds^2 = dx^2 + dy^2 + ... (flat metric)
        """
        n = len(point)
        return np.eye(n)

    @staticmethod
    def sphere_metric(theta_phi: np.ndarray, R: float = 1.0) -> np.ndarray:
        """
        Metric on 2-sphere of radius R.

        ds^2 = R^2(dtheta^2 + sin^2(theta) dphi^2)

        Args:
            theta_phi: [theta, phi] coordinates (0 <= theta <= pi)
            R: Sphere radius

        Returns:
            2x2 metric tensor
        """
        theta = theta_phi[0]
        return R**2 * np.array([
            [1, 0],
            [0, np.sin(theta)**2 + 1e-10]  # Regularize at poles
        ])

    @staticmethod
    def hyperbolic_metric(x_y: np.ndarray) -> np.ndarray:
        """
        Poincare half-plane metric (constant negative curvature).

        ds^2 = (dx^2 + dy^2) / y^2

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
    def minkowski_metric(point: np.ndarray) -> np.ndarray:
        """
        Minkowski metric for special relativity.

        ds^2 = -dt^2 + dx^2 + dy^2 + dz^2

        Returns:
            4x4 Lorentzian metric (-,+,+,+) signature
        """
        return np.diag([-1, 1, 1, 1])

    @staticmethod
    def schwarzschild_metric(r_theta: np.ndarray, M: float = 1.0) -> np.ndarray:
        """
        Schwarzschild metric (simplified 2D radial-angular slice).

        ds^2 = -(1 - 2M/r) dt^2 + (1 - 2M/r)^-1 dr^2

        Args:
            r_theta: [r, theta] coordinates
            M: Mass parameter

        Returns:
            2x2 metric tensor
        """
        r = max(r_theta[0], 2*M + 0.01)  # Avoid event horizon
        f = 1 - 2*M/r

        return np.array([
            [-f, 0],
            [0, r**2]
        ])

    # ========== BDI Methods ==========

    def update_beliefs(self) -> None:
        """Update agent beliefs based on computation history."""
        if hasattr(self, 'blackboard') and self.blackboard:
            self.blackboard.write(
                f'metric_specialist_stats_{self.agent_id}',
                {
                    'tasks_executed': self.tasks_executed,
                    'recent_operations': self.recent_computations[-10:],
                    'cache_size': len(self.metric_cache)
                }
            )

    def deliberate(self) -> List[Intention]:
        """Determine intentions based on current state."""
        intentions = []

        # Cache management
        if len(self.metric_cache) > 100:
            intentions.append(Intention(
                action='clear_cache',
                priority=1,
                params={'reason': 'cache_full'}
            ))

        # Performance optimization
        if self.tasks_executed > 100 and self.tasks_executed % 50 == 0:
            intentions.append(Intention(
                action='analyze_performance',
                priority=2,
                params={'tasks_executed': self.tasks_executed}
            ))

        return intentions

    def execute_step(self, intention: Intention) -> None:
        """Execute a single BDI intention."""
        if intention.action == 'clear_cache':
            # Keep only most recent 50 entries
            if len(self.metric_cache) > 50:
                keys = list(self.metric_cache.keys())
                for key in keys[:-50]:
                    del self.metric_cache[key]

        elif intention.action == 'analyze_performance':
            # Log performance metrics
            if hasattr(self, 'blackboard') and self.blackboard:
                self.blackboard.write(
                    f'performance_{self.agent_id}',
                    {
                        'total_tasks': self.tasks_executed,
                        'cache_hits': len(self.metric_cache),
                        'recent_ops': self.recent_computations[-20:]
                    }
                )

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.metric_cache),
            'recent_operations': self.recent_computations[-5:]
        }
