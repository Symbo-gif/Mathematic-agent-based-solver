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
RectifiabilitySpecialist - Rectifiable Sets and Tangent Spaces
================================================================

Provides comprehensive rectifiability analysis:
- Rectifiability checking (countable union of Lipschitz images)
- Density theorem applications
- Tangent measure computation
- Lipschitz image verification
- Approximate tangent space computation
- Countable rectifiability verification

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


@dataclass
class RectifiabilityResult:
    """Result from rectifiability check."""
    is_rectifiable: bool
    dimension: int
    confidence: float = 1.0
    tangent_spaces: Optional[List[np.ndarray]] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TangentMeasureResult:
    """Result from tangent measure computation."""
    tangent_directions: List[np.ndarray]
    densities: List[float]
    dimension: int
    point: np.ndarray
    details: Dict[str, Any] = field(default_factory=dict)


class RectifiabilitySpecialist(BDIAgent):
    """
    BDI Agent for rectifiability and tangent space operations.

    Capabilities:
    - Check if set is rectifiable (Lipschitz image)
    - Apply density theorems
    - Compute tangent measures
    - Verify Lipschitz mappings
    - Compute approximate tangent spaces
    - Check countable rectifiability
    """

    def __init__(self, agent_id='rectifiability_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.tangent_cache: Dict[str, np.ndarray] = {}
        self._epsilon = 1e-10

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.geometricmeasure.rectifiability',
                agent_id=self.agent_id,
                algorithm='rectifiability',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for rectifiability tasks.

        Supported operations:
        - check_rectifiability: Is set rectifiable?
        - apply_density_theorem: Apply density theorems
        - compute_tangent_measures: Tangent measures at point
        - verify_lipschitz_image: Is set a Lipschitz image?
        - compute_approximate_tangent_space: Approximate tangent space
        - check_countably_rectifiable: Countable union of Lipschitz images?
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        operation = metadata.get('operation', 'check_rectifiability')

        if operation == 'check_rectifiability':
            return self.check_rectifiability(
                set_points=metadata.get('set_points'),
                dimension=metadata.get('dimension')
            )
        elif operation == 'apply_density_theorem':
            return self.apply_density_theorem(
                set_points=metadata.get('set_points'),
                measure=metadata.get('measure')
            )
        elif operation == 'compute_tangent_measures':
            return self.compute_tangent_measures(
                set_points=metadata.get('set_points'),
                point=metadata.get('point')
            )
        elif operation == 'verify_lipschitz_image':
            return self.verify_lipschitz_image(
                mapping=metadata.get('mapping'),
                domain=metadata.get('domain')
            )
        elif operation == 'compute_approximate_tangent_space':
            return self.compute_approximate_tangent_space(
                set_points=metadata.get('set_points'),
                point=metadata.get('point')
            )
        elif operation == 'check_countably_rectifiable':
            return self.check_countably_rectifiable(
                set_points=metadata.get('set_points')
            )

        return {'error': f'Unknown operation: {operation}'}

    # ========== Rectifiability Checking ==========

    def check_rectifiability(
        self,
        set_points: np.ndarray,
        dimension: int
    ) -> Dict[str, Any]:
        """
        Check if set E is rectifiable.

        A set E ⊆ ℝⁿ is m-rectifiable if:
        E = E₀ ∪ ⋃ᵢ Eᵢ where H^m(E₀) = 0 and each Eᵢ is a Lipschitz image of ℝᵐ.

        Args:
            set_points: Points in set E
            dimension: Expected dimension m

        Returns:
            Dict with rectifiability analysis
        """
        if set_points is None or len(set_points) == 0:
            return {'is_rectifiable': False, 'error': 'Empty set'}

        set_points = np.asarray(set_points)
        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)

        ambient_dim = set_points.shape[1]

        if dimension > ambient_dim:
            return {
                'is_rectifiable': False,
                'error': f'Dimension {dimension} exceeds ambient dimension {ambient_dim}'
            }

        # Strategy: Check if set has consistent tangent spaces of dimension m
        # Sample points and compute approximate tangent spaces
        n_sample = min(100, len(set_points))
        sample_indices = np.random.choice(len(set_points), n_sample, replace=False)

        tangent_dimensions = []
        consistent_count = 0

        for idx in sample_indices:
            point = set_points[idx]
            tangent_result = self.compute_approximate_tangent_space(set_points, point)

            if 'tangent_basis' in tangent_result:
                tang_dim = len(tangent_result['tangent_basis'])
                tangent_dimensions.append(tang_dim)

                if tang_dim == dimension:
                    consistent_count += 1

        # Rectifiable if most points have consistent tangent dimension
        if tangent_dimensions:
            consistency_ratio = consistent_count / len(tangent_dimensions)
            is_rectifiable = consistency_ratio > 0.8

            return {
                'is_rectifiable': is_rectifiable,
                'dimension': dimension,
                'confidence': consistency_ratio,
                'tangent_dimension_histogram': {
                    d: tangent_dimensions.count(d) for d in set(tangent_dimensions)
                },
                'details': {
                    'consistent_points': consistent_count,
                    'total_sampled': len(tangent_dimensions)
                }
            }

        return {'is_rectifiable': False, 'error': 'Could not compute tangent spaces'}

    # ========== Density Theorem ==========

    def apply_density_theorem(
        self,
        set_points: np.ndarray,
        measure: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Apply density theorems to analyze set structure.

        For rectifiable sets, the density
        Θᵐ(μ, x) = lim_{r→0} μ(B(x,r)) / ωₘrᵐ
        exists at H^m-almost every point, where ωₘ is the volume of unit ball in ℝᵐ.

        Args:
            set_points: Points in set
            measure: Optional measure function

        Returns:
            Dict with density analysis
        """
        if set_points is None or len(set_points) == 0:
            return {'error': 'Empty set'}

        set_points = np.asarray(set_points)
        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)

        # Sample points and compute approximate densities
        n_sample = min(50, len(set_points))
        sample_indices = np.random.choice(len(set_points), n_sample, replace=False)

        densities = []
        radii = [0.1, 0.05, 0.025, 0.01]

        for idx in sample_indices:
            point = set_points[idx]

            # Compute density at different scales
            point_densities = []
            for r in radii:
                # Count points in ball B(point, r)
                distances = np.linalg.norm(set_points - point, axis=1)
                count = np.sum(distances <= r)

                # Estimate density (normalized by volume)
                m = set_points.shape[1]
                volume = self._ball_volume(m, r)
                density = count / volume if volume > 0 else 0
                point_densities.append(density)

            # Check if densities stabilize
            if len(point_densities) > 1:
                variation = np.std(point_densities) / (np.mean(point_densities) + self._epsilon)
                densities.append({
                    'point_index': idx,
                    'densities': point_densities,
                    'variation': variation,
                    'stable': variation < 0.5
                })

        # Count stable densities
        stable_count = sum(1 for d in densities if d['stable'])

        return {
            'density_analysis': densities,
            'stable_density_points': stable_count,
            'total_sampled': len(densities),
            'stability_ratio': stable_count / len(densities) if densities else 0,
            'conclusion': 'Set shows rectifiable behavior' if stable_count / len(densities) > 0.7 else 'Set may not be rectifiable'
        }

    def _ball_volume(self, dimension: int, radius: float) -> float:
        """
        Compute volume of m-dimensional ball of given radius.

        V_m(r) = π^(m/2) / Γ(m/2 + 1) * r^m
        """
        # Use approximation: Γ(n+1) = n! for integers, Γ(1/2) = √π
        if dimension == 1:
            return 2 * radius
        elif dimension == 2:
            return np.pi * radius ** 2
        elif dimension == 3:
            return (4/3) * np.pi * radius ** 3
        else:
            # General formula
            from math import gamma
            return (np.pi ** (dimension / 2)) / gamma(dimension / 2 + 1) * (radius ** dimension)

    # ========== Tangent Measures ==========

    def compute_tangent_measures(
        self,
        set_points: np.ndarray,
        point: np.ndarray
    ) -> Dict[str, Any]:
        """
        Compute tangent measures at a point.

        Tangent measures are obtained by "zooming in" at a point:
        μₓ,ᵣ(A) = μ(x + rA) / r^m

        Args:
            set_points: Points in set
            point: Point at which to compute tangent measure

        Returns:
            Dict with tangent measure information
        """
        if set_points is None or len(set_points) == 0:
            return {'error': 'Empty set'}

        set_points = np.asarray(set_points)
        point = np.asarray(point)

        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)
        if point.ndim == 0:
            point = point.reshape(-1)

        # Rescale set around point at different scales
        scales = [1.0, 0.5, 0.25, 0.1]
        rescaled_sets = []

        for scale in scales:
            # Translate and rescale
            rescaled = (set_points - point) / scale

            # Keep only nearby points
            distances = np.linalg.norm(rescaled, axis=1)
            mask = distances <= 1.0
            nearby = rescaled[mask]

            if len(nearby) > 10:
                rescaled_sets.append({
                    'scale': scale,
                    'points': nearby,
                    'count': len(nearby)
                })

        # Analyze convergence of rescaled sets
        if len(rescaled_sets) > 1:
            # Compute principal directions (PCA) on finest scale
            finest = rescaled_sets[-1]['points']
            tangent_basis = self._compute_pca_basis(finest)

            return {
                'tangent_basis': [v.tolist() for v in tangent_basis],
                'dimension': len(tangent_basis),
                'scales_analyzed': scales,
                'point': point.tolist(),
                'details': {
                    'counts_at_scales': [rs['count'] for rs in rescaled_sets]
                }
            }

        return {'error': 'Insufficient points near target point'}

    # ========== Lipschitz Image Verification ==========

    def verify_lipschitz_image(
        self,
        mapping: Callable[[np.ndarray], np.ndarray],
        domain: np.ndarray
    ) -> Dict[str, Any]:
        """
        Verify if a mapping is Lipschitz.

        A mapping f: A → B is Lipschitz if:
        |f(x) - f(y)| ≤ L|x - y| for all x, y ∈ A

        Args:
            mapping: Function f
            domain: Sample points in domain

        Returns:
            Dict with Lipschitz verification
        """
        if domain is None or len(domain) == 0:
            return {'is_lipschitz': False, 'error': 'Empty domain'}

        domain = np.asarray(domain)
        if domain.ndim == 1:
            domain = domain.reshape(-1, 1)

        # Sample pairs of points
        n_sample = min(100, len(domain))
        sample_indices = np.random.choice(len(domain), n_sample, replace=False)
        sample_points = domain[sample_indices]

        # Compute Lipschitz constants
        lipschitz_constants = []

        for i in range(len(sample_points)):
            for j in range(i + 1, len(sample_points)):
                x = sample_points[i]
                y = sample_points[j]

                try:
                    fx = mapping(x)
                    fy = mapping(y)

                    dist_domain = np.linalg.norm(x - y)
                    dist_image = np.linalg.norm(fx - fy)

                    if dist_domain > self._epsilon:
                        L = dist_image / dist_domain
                        lipschitz_constants.append(L)
                except:
                    pass

        if lipschitz_constants:
            L_max = max(lipschitz_constants)
            L_mean = np.mean(lipschitz_constants)
            L_std = np.std(lipschitz_constants)

            # Lipschitz if constants are bounded
            is_lipschitz = L_max < 1e6  # Practical bound

            return {
                'is_lipschitz': is_lipschitz,
                'lipschitz_constant': L_max,
                'mean_constant': L_mean,
                'std_constant': L_std,
                'samples_tested': len(lipschitz_constants),
                'details': {
                    'min_constant': min(lipschitz_constants),
                    'max_constant': L_max
                }
            }

        return {'is_lipschitz': False, 'error': 'Could not compute Lipschitz constants'}

    # ========== Approximate Tangent Space ==========

    def compute_approximate_tangent_space(
        self,
        set_points: np.ndarray,
        point: np.ndarray
    ) -> Dict[str, Any]:
        """
        Compute approximate tangent space at a point using PCA.

        The tangent space T_x E is the m-dimensional linear subspace
        that best approximates E near x.

        Args:
            set_points: Points in set
            point: Point at which to compute tangent space

        Returns:
            Dict with tangent space basis
        """
        if set_points is None or len(set_points) == 0:
            return {'error': 'Empty set'}

        set_points = np.asarray(set_points)
        point = np.asarray(point)

        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)
        if point.ndim == 0:
            point = point.reshape(-1)

        # Find nearby points
        distances = np.linalg.norm(set_points - point, axis=1)
        radius = np.percentile(distances, 10)  # Use 10th percentile as radius
        mask = distances <= radius

        nearby_points = set_points[mask]

        if len(nearby_points) < 3:
            return {'error': 'Insufficient nearby points'}

        # Center points
        centered = nearby_points - point

        # Compute tangent basis via PCA
        tangent_basis = self._compute_pca_basis(centered)

        return {
            'tangent_basis': [v.tolist() for v in tangent_basis],
            'dimension': len(tangent_basis),
            'point': point.tolist(),
            'radius': float(radius),
            'nearby_points': len(nearby_points)
        }

    def _compute_pca_basis(
        self,
        points: np.ndarray,
        variance_threshold: float = 0.01
    ) -> List[np.ndarray]:
        """
        Compute PCA basis vectors (principal directions).

        Keep only directions with significant variance.
        """
        if len(points) < 2:
            return []

        # Center points
        centered = points - np.mean(points, axis=0)

        # Compute covariance matrix
        cov = np.cov(centered.T)

        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov)

        # Sort by decreasing eigenvalue
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Keep only significant directions
        total_variance = np.sum(eigenvalues)
        if total_variance < self._epsilon:
            return []

        significant = []
        for i, val in enumerate(eigenvalues):
            if val / total_variance > variance_threshold:
                significant.append(eigenvectors[:, i])

        return significant

    # ========== Countable Rectifiability ==========

    def check_countably_rectifiable(self, set_points: np.ndarray) -> Dict[str, Any]:
        """
        Check if set is countably rectifiable.

        A set E is countably m-rectifiable if:
        E = E₀ ∪ ⋃ᵢ₌₁^∞ Eᵢ
        where H^m(E₀) = 0 and each Eᵢ is the image of a bounded subset
        of ℝᵐ under a Lipschitz map.

        Strategy: Try to partition set into regions with consistent
        tangent spaces.

        Args:
            set_points: Points in set

        Returns:
            Dict with countable rectifiability analysis
        """
        if set_points is None or len(set_points) == 0:
            return {'is_countably_rectifiable': False, 'error': 'Empty set'}

        set_points = np.asarray(set_points)
        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)

        # Sample points and cluster by tangent space
        n_sample = min(100, len(set_points))
        sample_indices = np.random.choice(len(set_points), n_sample, replace=False)

        tangent_spaces = []
        for idx in sample_indices:
            point = set_points[idx]
            result = self.compute_approximate_tangent_space(set_points, point)

            if 'tangent_basis' in result:
                tangent_spaces.append({
                    'point_index': idx,
                    'dimension': result['dimension'],
                    'basis': result['tangent_basis']
                })

        # Group by dimension
        dimension_groups = {}
        for ts in tangent_spaces:
            dim = ts['dimension']
            if dim not in dimension_groups:
                dimension_groups[dim] = []
            dimension_groups[dim].append(ts)

        # Countably rectifiable if we can partition into finite pieces
        # with consistent dimensions
        if dimension_groups:
            dominant_dimension = max(dimension_groups.keys(), key=lambda d: len(dimension_groups[d]))
            dominant_count = len(dimension_groups[dominant_dimension])
            coverage = dominant_count / len(tangent_spaces)

            is_countably_rectifiable = coverage > 0.85

            return {
                'is_countably_rectifiable': is_countably_rectifiable,
                'dominant_dimension': dominant_dimension,
                'coverage': coverage,
                'dimension_distribution': {
                    dim: len(dimension_groups[dim]) for dim in dimension_groups
                },
                'total_sampled': len(tangent_spaces)
            }

        return {'is_countably_rectifiable': False, 'error': 'Could not compute tangent spaces'}

    # ========== BDI Methods ==========

    def update_beliefs(self):
        """Update agent beliefs (BDI pattern)."""
        pass

    def deliberate(self):
        """Determine next actions (BDI pattern)."""
        return []

    def execute_step(self, i):
        """Execute reasoning step (BDI pattern)."""
        pass

    def get_statistics(self):
        """Get agent statistics."""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            'cached_tangents': len(self.tangent_cache)
        }
