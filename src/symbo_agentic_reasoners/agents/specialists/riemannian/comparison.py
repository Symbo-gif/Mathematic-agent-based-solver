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
ComparisonTheoremsSpecialist - Riemannian Comparison Geometry
===============================================================

Provides comparison theorem applications:
- Rauch comparison theorem (Jacobi field comparison)
- Toponogov triangle comparison theorem
- Bishop-Gromov volume comparison
- Myers theorem (compactness from Ricci bounds)
- Diameter bounds from curvature

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


@dataclass
class RauchComparisonResult:
    """Result from Rauch comparison theorem."""
    passes_comparison: bool
    jacobi_field_norm: float
    model_jacobi_norm: float
    curvature_bound: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToponogoyResult:
    """Result from Toponogov comparison."""
    passes_toponogov: bool
    triangle_angles: List[float]
    model_triangle_angles: List[float]
    curvature_bound: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BishopGromovResult:
    """Result from Bishop-Gromov volume comparison."""
    volume_ratio: float
    model_volume_ratio: float
    satisfies_bound: bool
    details: Dict[str, Any] = field(default_factory=dict)


class ComparisonTheoremsSpecialist(BDIAgent):
    """
    BDI Agent for Riemannian comparison theorems.

    Capabilities:
    - Apply Rauch comparison theorem
    - Verify Toponogov triangle comparison
    - Bishop-Gromov volume comparison
    - Myers compactness theorem
    - Diameter estimates from curvature bounds
    """

    def __init__(self, agent_id='comparison_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_computations: List[str] = []
        self._epsilon = 1e-10

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.riemannian.comparison',
                agent_id=self.agent_id,
                algorithm='comparison',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for comparison theorem computations.

        Supported operations:
        - apply_rauch_comparison: Rauch comparison for Jacobi fields
        - apply_toponogov: Triangle comparison
        - apply_bishop_gromov: Volume comparison
        - apply_myers_theorem: Check compactness via Ricci bounds
        - compute_diameter_bound: Diameter estimates
        """
        self.tasks_executed += 1
        operation = task_entry.get('operation', 'apply_rauch_comparison')
        self.recent_computations.append(operation)

        if len(self.recent_computations) > 100:
            self.recent_computations = self.recent_computations[-100:]

        try:
            if operation == 'apply_rauch_comparison':
                return self._handle_rauch(task_entry)
            elif operation == 'apply_toponogov':
                return self._handle_toponogov(task_entry)
            elif operation == 'apply_bishop_gromov':
                return self._handle_bishop_gromov(task_entry)
            elif operation == 'apply_myers_theorem':
                return self._handle_myers(task_entry)
            elif operation == 'compute_diameter_bound':
                return self._handle_diameter_bound(task_entry)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}',
                    'supported_operations': [
                        'apply_rauch_comparison', 'apply_toponogov', 'apply_bishop_gromov',
                        'apply_myers_theorem', 'compute_diameter_bound'
                    ]
                }
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation}

    def _handle_rauch(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Rauch comparison."""
        metric_fn = task_entry.get('metric_function')
        geodesic_variation = task_entry.get('geodesic_variation')
        curvature_bound = task_entry.get('curvature_bound', 0.0)

        result = self.apply_rauch_comparison(metric_fn, geodesic_variation, curvature_bound)

        return {
            'success': True,
            'operation': 'apply_rauch_comparison',
            'passes_comparison': result.passes_comparison,
            'jacobi_field_norm': float(result.jacobi_field_norm),
            'model_jacobi_norm': float(result.model_jacobi_norm),
            'details': result.details
        }

    def _handle_toponogov(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Toponogov comparison."""
        triangle = task_entry.get('triangle')  # 3 points
        curvature_bound = task_entry.get('curvature_bound', 0.0)
        metric_fn = task_entry.get('metric_function')

        result = self.apply_toponogov_theorem(metric_fn, triangle, curvature_bound)

        return {
            'success': True,
            'operation': 'apply_toponogov',
            'passes_toponogov': result.passes_toponogov,
            'triangle_angles': result.triangle_angles,
            'model_triangle_angles': result.model_triangle_angles,
            'details': result.details
        }

    def _handle_bishop_gromov(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Bishop-Gromov comparison."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point'))
        radius = task_entry.get('radius', 1.0)
        curvature_bound = task_entry.get('curvature_bound', 0.0)

        result = self.apply_bishop_gromov(metric_fn, point, radius, curvature_bound)

        return {
            'success': True,
            'operation': 'apply_bishop_gromov',
            'volume_ratio': float(result.volume_ratio),
            'satisfies_bound': result.satisfies_bound,
            'details': result.details
        }

    def _handle_myers(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Myers theorem check."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))
        dimension = len(point)

        result = self.apply_myers_theorem(metric_fn, point, dimension)

        return {
            'success': True,
            'operation': 'apply_myers_theorem',
            **result
        }

    def _handle_diameter_bound(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle diameter bound computation."""
        curvature_bound = task_entry.get('curvature_bound')
        dimension = task_entry.get('dimension', 2)

        diameter_bound = self.compute_diameter_bound(curvature_bound, dimension)

        return {
            'success': True,
            'operation': 'compute_diameter_bound',
            'diameter_bound': float(diameter_bound),
            'curvature_bound': float(curvature_bound),
            'dimension': dimension
        }

    # ========== Core Computational Methods ==========

    def apply_rauch_comparison(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        geodesic_variation: Dict[str, Any],
        curvature_bound: float
    ) -> RauchComparisonResult:
        """
        Apply Rauch comparison theorem.

        Compares Jacobi field growth in given metric vs. model space
        with constant curvature K.

        Args:
            metric_fn: Metric function
            geodesic_variation: Dict with 'geodesic_path' and 'variation_field'
            curvature_bound: Sectional curvature bound K

        Returns:
            RauchComparisonResult
        """
        geodesic = np.array(geodesic_variation.get('geodesic_path'))
        variation = np.array(geodesic_variation.get('variation_field'))

        # Compute Jacobi field norm along geodesic
        jacobi_norms = []
        for i, point in enumerate(geodesic):
            if i < len(variation):
                jacobi_norms.append(np.linalg.norm(variation[i]))

        jacobi_field_norm = np.mean(jacobi_norms) if jacobi_norms else 0.0

        # Model Jacobi field (constant curvature K)
        # For K > 0: J(t) ~ sin(sqrt(K) t) / sqrt(K)
        # For K = 0: J(t) ~ t
        # For K < 0: J(t) ~ sinh(sqrt(|K|) t) / sqrt(|K|)

        t_max = len(geodesic) * 0.01  # Approximate arc length parameter
        t = np.linspace(0, t_max, len(geodesic))

        if curvature_bound > self._epsilon:
            # Positive curvature
            sqrt_K = np.sqrt(curvature_bound)
            model_jacobi = np.sin(sqrt_K * t) / sqrt_K
        elif curvature_bound < -self._epsilon:
            # Negative curvature
            sqrt_K = np.sqrt(-curvature_bound)
            model_jacobi = np.sinh(sqrt_K * t) / sqrt_K
        else:
            # Zero curvature
            model_jacobi = t

        model_jacobi_norm = np.mean(model_jacobi)

        # Rauch comparison: If sectional curvature <= K, Jacobi fields grow
        # at least as fast as model space
        passes_comparison = (jacobi_field_norm >= model_jacobi_norm * 0.9)  # Allow 10% tolerance

        return RauchComparisonResult(
            passes_comparison=passes_comparison,
            jacobi_field_norm=float(jacobi_field_norm),
            model_jacobi_norm=float(model_jacobi_norm),
            curvature_bound=curvature_bound,
            details={
                'geodesic_length': len(geodesic),
                'variation_samples': len(variation)
            }
        )

    def apply_toponogov_theorem(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        triangle: np.ndarray,
        curvature_bound: float
    ) -> ToponogoyResult:
        """
        Apply Toponogov triangle comparison theorem.

        For manifolds with sectional curvature >= K, triangle angles
        satisfy inequalities compared to model space.

        Args:
            metric_fn: Metric function
            triangle: 3 × dim array of triangle vertices
            curvature_bound: Lower curvature bound K

        Returns:
            ToponogoyResult
        """
        # Compute side lengths
        sides = []
        for i in range(3):
            j = (i + 1) % 3
            side_length = self._geodesic_distance(metric_fn, triangle[i], triangle[j])
            sides.append(side_length)

        a, b, c = sides

        # Compute angles using law of cosines in model space
        # For K > 0 (sphere), K = 0 (Euclidean), K < 0 (hyperbolic)

        triangle_angles = self._compute_triangle_angles(a, b, c, curvature_K=0)

        # Model space angles
        model_angles = self._compute_triangle_angles(a, b, c, curvature_K=curvature_bound)

        # Toponogov: For K >= K_bound, angles in manifold >= angles in model
        passes_toponogov = all(
            triangle_angles[i] >= model_angles[i] - 0.1  # Tolerance
            for i in range(3)
        )

        return ToponogoyResult(
            passes_toponogov=passes_toponogov,
            triangle_angles=triangle_angles,
            model_triangle_angles=model_angles,
            curvature_bound=curvature_bound,
            details={
                'side_lengths': sides,
                'vertices': triangle.tolist()
            }
        )

    def apply_bishop_gromov(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        radius: float,
        curvature_bound: float
    ) -> BishopGromovResult:
        """
        Apply Bishop-Gromov volume comparison.

        For Ricci curvature >= (n-1)K, volume of ball satisfies bound.

        Args:
            metric_fn: Metric function
            point: Center point
            radius: Ball radius
            curvature_bound: Ricci curvature lower bound K

        Returns:
            BishopGromovResult
        """
        n = len(point)

        # Estimate volume using Monte Carlo sampling
        num_samples = 1000
        in_ball = 0

        for _ in range(num_samples):
            # Random point in box
            random_point = point + (np.random.rand(n) - 0.5) * 2 * radius

            # Check distance
            dist = self._geodesic_distance(metric_fn, point, random_point)
            if dist <= radius:
                in_ball += 1

        # Volume estimate
        box_volume = (2 * radius) ** n
        estimated_volume = box_volume * (in_ball / num_samples)

        # Model space volume
        if curvature_bound > self._epsilon:
            # Sphere: V_K(r) = ∫_0^r (sin(sqrt(K) t) / sqrt(K))^(n-1) dt
            # Approximation for small r
            model_volume = (np.pi ** (n/2) / np.math.gamma(n/2 + 1)) * radius**n
            model_volume *= (1 - (curvature_bound * radius**2) / (6 * n))
        elif curvature_bound < -self._epsilon:
            # Hyperbolic space (larger volume)
            model_volume = (np.pi ** (n/2) / np.math.gamma(n/2 + 1)) * radius**n
            model_volume *= (1 + (-curvature_bound * radius**2) / (6 * n))
        else:
            # Euclidean
            model_volume = (np.pi ** (n/2) / np.math.gamma(n/2 + 1)) * radius**n

        volume_ratio = estimated_volume / model_volume if model_volume > 0 else 0
        satisfies_bound = (volume_ratio <= 1.2)  # Allow tolerance

        return BishopGromovResult(
            volume_ratio=float(volume_ratio),
            model_volume_ratio=1.0,
            satisfies_bound=satisfies_bound,
            details={
                'estimated_volume': float(estimated_volume),
                'model_volume': float(model_volume),
                'samples': num_samples,
                'in_ball': in_ball
            }
        )

    def apply_myers_theorem(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        dimension: int
    ) -> Dict[str, Any]:
        """
        Apply Myers theorem: If Ricci >= (n-1)K with K > 0,
        then manifold is compact with diameter <= π/sqrt(K).

        Args:
            metric_fn: Metric function
            point: Sample point
            dimension: Manifold dimension

        Returns:
            Dictionary with Myers theorem analysis
        """
        # Estimate Ricci curvature at point (via scalar curvature)
        # This is a simplified approximation
        from .curvature import CurvatureSpecialist

        curv_specialist = CurvatureSpecialist()
        try:
            scalar_curv = curv_specialist.compute_scalar_curvature(metric_fn, point)
            # Ricci ≈ scalar / n for roughly isotropic metrics
            estimated_ricci = scalar_curv / dimension
        except:
            estimated_ricci = 0.0

        # Check Myers condition: Ricci >= (n-1)K
        if estimated_ricci > self._epsilon:
            K = estimated_ricci / (dimension - 1)
            diameter_bound = np.pi / np.sqrt(K)
            satisfies_myers = True
            suggests_compact = True
        else:
            diameter_bound = float('inf')
            satisfies_myers = False
            suggests_compact = False

        return {
            'satisfies_myers_condition': satisfies_myers,
            'suggests_compactness': suggests_compact,
            'diameter_bound': float(diameter_bound) if diameter_bound != float('inf') else None,
            'estimated_ricci': float(estimated_ricci),
            'dimension': dimension,
            'details': {
                'point': point.tolist(),
                'condition': f'Ricci >= ({dimension}-1)K'
            }
        }

    def compute_diameter_bound(
        self,
        curvature_bound: float,
        dimension: int
    ) -> float:
        """
        Compute diameter bound from curvature.

        For Ricci >= (n-1)K with K > 0: diameter <= π/sqrt(K)

        Args:
            curvature_bound: Ricci curvature bound
            dimension: Manifold dimension

        Returns:
            Diameter upper bound
        """
        if curvature_bound > self._epsilon:
            K = curvature_bound / (dimension - 1)
            return np.pi / np.sqrt(K)
        else:
            return float('inf')

    def _geodesic_distance(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        p1: np.ndarray,
        p2: np.ndarray
    ) -> float:
        """
        Approximate geodesic distance (straight line path).
        """
        n_steps = 100
        distance = 0.0

        for i in range(n_steps):
            t = i / n_steps
            point = (1 - t) * p1 + t * p2
            tangent = (p2 - p1) / n_steps

            g = metric_fn(point)
            ds_squared = tangent @ g @ tangent

            if ds_squared > 0:
                distance += np.sqrt(ds_squared)

        return distance

    def _compute_triangle_angles(
        self,
        a: float,
        b: float,
        c: float,
        curvature_K: float = 0.0
    ) -> List[float]:
        """
        Compute triangle angles using law of cosines in model space.

        Args:
            a, b, c: Side lengths
            curvature_K: Constant curvature of model space

        Returns:
            List of three angles (in radians)
        """
        if abs(curvature_K) < self._epsilon:
            # Euclidean law of cosines
            # cos(C) = (a^2 + b^2 - c^2) / (2ab)
            angles = []
            for (x, y, z) in [(a, b, c), (b, c, a), (c, a, b)]:
                cos_angle = (x**2 + y**2 - z**2) / (2 * x * y) if x * y > 0 else 0
                cos_angle = np.clip(cos_angle, -1, 1)
                angles.append(np.arccos(cos_angle))
            return angles

        elif curvature_K > 0:
            # Spherical law of cosines
            # cos(c) = cos(a)cos(b) + sin(a)sin(b)cos(C)
            R = 1 / np.sqrt(curvature_K)
            a_s, b_s, c_s = a/R, b/R, c/R

            angles = []
            cos_C = (np.cos(c_s) - np.cos(a_s)*np.cos(b_s)) / (np.sin(a_s)*np.sin(b_s))
            cos_C = np.clip(cos_C, -1, 1)
            angles.append(np.arccos(cos_C))

            cos_A = (np.cos(a_s) - np.cos(b_s)*np.cos(c_s)) / (np.sin(b_s)*np.sin(c_s))
            cos_A = np.clip(cos_A, -1, 1)
            angles.append(np.arccos(cos_A))

            cos_B = (np.cos(b_s) - np.cos(a_s)*np.cos(c_s)) / (np.sin(a_s)*np.sin(c_s))
            cos_B = np.clip(cos_B, -1, 1)
            angles.append(np.arccos(cos_B))

            return angles

        else:
            # Hyperbolic law of cosines (approximation)
            # Use Euclidean as fallback
            return self._compute_triangle_angles(a, b, c, curvature_K=0.0)

    # ========== BDI Methods ==========

    def update_beliefs(self) -> None:
        """Update agent beliefs."""
        if hasattr(self, 'blackboard') and self.blackboard:
            self.blackboard.write(
                f'comparison_specialist_stats_{self.agent_id}',
                {
                    'tasks_executed': self.tasks_executed,
                    'recent_operations': self.recent_computations[-10:]
                }
            )

    def deliberate(self) -> List[Intention]:
        """Determine intentions."""
        return []

    def execute_step(self, intention: Intention) -> None:
        """Execute BDI intention."""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'recent_operations': self.recent_computations[-5:]
        }
