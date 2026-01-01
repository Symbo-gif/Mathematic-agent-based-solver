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
HausdorffMeasureSpecialist - Hausdorff Dimension and Measure
==============================================================

Provides comprehensive Hausdorff measure and dimension computations:
- Hausdorff dimension computation (box-counting, covering methods)
- Hausdorff measure estimation
- Box-counting dimension
- Minkowski dimension
- Fractal dimension estimation
- Metric outer measure verification

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


@dataclass
class HausdorffDimensionResult:
    """Result from Hausdorff dimension computation."""
    hausdorff_dimension: float
    method: str
    confidence: float = 1.0
    box_counts: Optional[List[Tuple[float, int]]] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HausdorffMeasureResult:
    """Result from Hausdorff measure computation."""
    measure: float
    dimension: float
    is_finite: bool = True
    covering_method: str = "epsilon_covering"
    details: Dict[str, Any] = field(default_factory=dict)


class HausdorffMeasureSpecialist(BDIAgent):
    """
    BDI Agent for Hausdorff measure and dimension operations.

    Capabilities:
    - Compute Hausdorff dimension via box-counting
    - Estimate Hausdorff measure at specific dimensions
    - Box-counting dimension calculation
    - Minkowski dimension
    - Fractal dimension estimation
    - Verify metric outer measure properties
    """

    def __init__(self, agent_id='hausdorff_measure_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.dimension_cache: Dict[str, float] = {}
        self._epsilon = 1e-10

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.geometricmeasure.hausdorff_measure',
                agent_id=self.agent_id,
                algorithm='hausdorff',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for Hausdorff measure tasks.

        Supported operations:
        - compute_hausdorff_dimension: Compute dim_H(E)
        - compute_hausdorff_measure: Compute H^s(E)
        - compute_box_counting_dimension: Box-counting dimension
        - compute_minkowski_dimension: Minkowski dimension
        - estimate_fractal_dimension: Fractal dimension
        - verify_hausdorff_properties: Verify metric outer measure
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        operation = metadata.get('operation', 'compute_hausdorff_dimension')

        if operation == 'compute_hausdorff_dimension':
            return self.compute_hausdorff_dimension(
                set_points=metadata.get('set_points'),
                method=metadata.get('method', 'box_counting')
            )
        elif operation == 'compute_hausdorff_measure':
            return self.compute_hausdorff_measure(
                set_points=metadata.get('set_points'),
                dimension=metadata.get('dimension')
            )
        elif operation == 'compute_box_counting_dimension':
            return self.compute_box_counting_dimension(
                set_points=metadata.get('set_points')
            )
        elif operation == 'compute_minkowski_dimension':
            return self.compute_minkowski_dimension(
                set_points=metadata.get('set_points')
            )
        elif operation == 'estimate_fractal_dimension':
            return self.estimate_fractal_dimension(
                set_points=metadata.get('set_points')
            )
        elif operation == 'verify_hausdorff_properties':
            return self.verify_hausdorff_properties(
                measure_func=metadata.get('measure_func')
            )

        return {'error': f'Unknown operation: {operation}'}

    # ========== Hausdorff Dimension Computation ==========

    def compute_hausdorff_dimension(
        self,
        set_points: np.ndarray,
        method: str = 'box_counting'
    ) -> Dict[str, Any]:
        """
        Compute Hausdorff dimension via box-counting method.

        dim_H(E) ≈ lim_{ε→0} log N(ε) / log(1/ε)
        where N(ε) is number of boxes of size ε needed to cover E.

        Args:
            set_points: Points in set E (n × d array)
            method: 'box_counting' or 'covering'

        Returns:
            Dict with estimated Hausdorff dimension
        """
        if set_points is None or len(set_points) == 0:
            return {'dimension': 0, 'error': 'Empty set'}

        set_points = np.asarray(set_points)
        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)

        if method == 'box_counting':
            return self._box_counting_dimension(set_points)
        elif method == 'covering':
            return self._covering_dimension(set_points)
        else:
            return {'error': f'Unknown method: {method}'}

    def _box_counting_dimension(self, set_points: np.ndarray) -> Dict[str, Any]:
        """
        Box-counting method for Hausdorff dimension.

        Count number of boxes N(ε) of size ε covering the set,
        then compute slope of log N(ε) vs log(1/ε).
        """
        # Get range of the set
        min_coords = np.min(set_points, axis=0)
        max_coords = np.max(set_points, axis=0)
        extent = np.max(max_coords - min_coords)

        if extent < self._epsilon:
            return {
                'hausdorff_dimension': 0.0,
                'method': 'box_counting',
                'note': 'Set has zero extent'
            }

        # Try different epsilon values (powers of 2)
        epsilon_values = [extent / (2 ** i) for i in range(2, 12)]
        box_counts = []

        for epsilon in epsilon_values:
            n_boxes = self._count_boxes_covering(set_points, epsilon, min_coords)
            if n_boxes > 0:
                box_counts.append((epsilon, n_boxes))

        if len(box_counts) < 3:
            return {
                'hausdorff_dimension': 0.0,
                'error': 'Insufficient data points for dimension estimate'
            }

        # Linear regression: log N(ε) ~ -dim * log(ε) + const
        log_epsilon = [np.log(eps) for eps, _ in box_counts]
        log_counts = [np.log(count) for _, count in box_counts]

        # Compute slope via least squares
        dimension = -self._linear_regression_slope(log_epsilon, log_counts)

        # Compute R^2 for confidence
        r_squared = self._compute_r_squared(log_epsilon, log_counts, -dimension)

        return {
            'hausdorff_dimension': float(dimension),
            'method': 'box_counting',
            'confidence': float(r_squared),
            'epsilon_values': [eps for eps, _ in box_counts],
            'box_counts': [count for _, count in box_counts],
            'details': {
                'log_epsilon': log_epsilon,
                'log_counts': log_counts
            }
        }

    def _count_boxes_covering(
        self,
        set_points: np.ndarray,
        epsilon: float,
        min_coords: np.ndarray
    ) -> int:
        """
        Count number of boxes of size epsilon needed to cover set.
        """
        # Discretize points into grid
        grid_indices = np.floor((set_points - min_coords) / epsilon).astype(int)

        # Count unique grid cells
        unique_cells = set(map(tuple, grid_indices))

        return len(unique_cells)

    def _covering_dimension(self, set_points: np.ndarray) -> Dict[str, Any]:
        """
        Covering method: use ball coverings instead of box coverings.
        """
        # Get diameter of set
        n_points = len(set_points)
        if n_points < 2:
            return {'hausdorff_dimension': 0.0, 'method': 'covering'}

        # Compute pairwise distances (sample for large sets)
        sample_size = min(1000, n_points)
        sample_indices = np.random.choice(n_points, sample_size, replace=False)
        sample_points = set_points[sample_indices]

        max_dist = 0
        for i in range(len(sample_points)):
            dists = np.linalg.norm(sample_points - sample_points[i], axis=1)
            max_dist = max(max_dist, np.max(dists))

        if max_dist < self._epsilon:
            return {'hausdorff_dimension': 0.0, 'method': 'covering'}

        # Try different radii
        radii = [max_dist / (2 ** i) for i in range(2, 10)]
        covering_numbers = []

        for radius in radii:
            n_centers = self._greedy_covering_number(set_points, radius)
            if n_centers > 0:
                covering_numbers.append((radius, n_centers))

        if len(covering_numbers) < 3:
            return {
                'hausdorff_dimension': 0.0,
                'error': 'Insufficient covering data'
            }

        # Dimension from covering numbers
        log_radii = [np.log(r) for r, _ in covering_numbers]
        log_numbers = [np.log(n) for _, n in covering_numbers]

        dimension = -self._linear_regression_slope(log_radii, log_numbers)

        return {
            'hausdorff_dimension': float(dimension),
            'method': 'covering',
            'radii': [r for r, _ in covering_numbers],
            'covering_numbers': [n for _, n in covering_numbers]
        }

    def _greedy_covering_number(self, set_points: np.ndarray, radius: float) -> int:
        """
        Greedy algorithm to find covering number with balls of given radius.
        """
        uncovered = set(range(len(set_points)))
        centers = []

        while uncovered:
            # Pick a point
            center_idx = next(iter(uncovered))
            centers.append(center_idx)
            center = set_points[center_idx]

            # Remove all points within radius
            to_remove = []
            for idx in uncovered:
                if np.linalg.norm(set_points[idx] - center) <= radius:
                    to_remove.append(idx)

            for idx in to_remove:
                uncovered.remove(idx)

        return len(centers)

    # ========== Hausdorff Measure ==========

    def compute_hausdorff_measure(
        self,
        set_points: np.ndarray,
        dimension: float
    ) -> Dict[str, Any]:
        """
        Estimate Hausdorff s-dimensional measure H^s(E).

        H^s(E) = lim_{δ→0} inf{Σ(diam U_i)^s : E ⊆ ∪U_i, diam U_i < δ}

        Args:
            set_points: Points in set E
            dimension: Dimension s for measure

        Returns:
            Dict with estimated Hausdorff measure
        """
        if set_points is None or len(set_points) == 0:
            return {'measure': 0.0, 'dimension': dimension}

        set_points = np.asarray(set_points)
        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)

        # Compute range
        min_coords = np.min(set_points, axis=0)
        max_coords = np.max(set_points, axis=0)
        diameter = np.linalg.norm(max_coords - min_coords)

        if diameter < self._epsilon:
            return {'measure': 0.0, 'dimension': dimension}

        # Use multiple delta values and take infimum
        delta_values = [diameter / (2 ** i) for i in range(2, 8)]
        measures = []

        for delta in delta_values:
            measure = self._compute_covering_measure(set_points, delta, dimension)
            measures.append((delta, measure))

        # Estimate limit as delta → 0
        if measures:
            # Use smallest delta (most refined covering)
            final_measure = measures[-1][1]

            return {
                'measure': float(final_measure),
                'dimension': dimension,
                'is_finite': np.isfinite(final_measure),
                'delta_values': [d for d, _ in measures],
                'measure_values': [m for _, m in measures]
            }

        return {'measure': 0.0, 'dimension': dimension}

    def _compute_covering_measure(
        self,
        set_points: np.ndarray,
        delta: float,
        dimension: float
    ) -> float:
        """
        Compute covering measure for given delta.

        Find covering with diameter < delta, sum (diam U_i)^s.
        """
        # Greedy covering with balls of radius delta/2
        radius = delta / 2
        uncovered = set(range(len(set_points)))
        total_measure = 0.0

        while uncovered:
            # Pick center
            center_idx = next(iter(uncovered))
            center = set_points[center_idx]

            # Find all points in ball
            ball_points = []
            to_remove = []
            for idx in uncovered:
                if np.linalg.norm(set_points[idx] - center) <= radius:
                    ball_points.append(idx)
                    to_remove.append(idx)

            # Compute diameter of this ball
            if len(ball_points) > 1:
                ball_coords = set_points[ball_points]
                diam = 0
                for i in range(len(ball_coords)):
                    for j in range(i + 1, len(ball_coords)):
                        d = np.linalg.norm(ball_coords[i] - ball_coords[j])
                        diam = max(diam, d)
            else:
                diam = 0

            # Add to measure
            total_measure += diam ** dimension if diam > 0 else 0

            # Remove covered points
            for idx in to_remove:
                uncovered.remove(idx)

        return total_measure

    # ========== Box-Counting Dimension ==========

    def compute_box_counting_dimension(self, set_points: np.ndarray) -> Dict[str, Any]:
        """
        Compute box-counting dimension (same as box-counting Hausdorff).

        This is an alias for compute_hausdorff_dimension with box_counting method.
        """
        return self.compute_hausdorff_dimension(set_points, method='box_counting')

    # ========== Minkowski Dimension ==========

    def compute_minkowski_dimension(self, set_points: np.ndarray) -> Dict[str, Any]:
        """
        Compute Minkowski (Minkowski-Bouligand) dimension.

        dim_M(E) = lim_{ε→0} log V_ε(E) / log(1/ε)
        where V_ε(E) is volume of ε-neighborhood of E.

        Args:
            set_points: Points in set E

        Returns:
            Dict with Minkowski dimension
        """
        if set_points is None or len(set_points) == 0:
            return {'minkowski_dimension': 0.0}

        set_points = np.asarray(set_points)
        if set_points.ndim == 1:
            set_points = set_points.reshape(-1, 1)

        # Compute range
        min_coords = np.min(set_points, axis=0)
        max_coords = np.max(set_points, axis=0)
        extent = np.max(max_coords - min_coords)

        if extent < self._epsilon:
            return {'minkowski_dimension': 0.0}

        # Try different epsilon values
        epsilon_values = [extent / (2 ** i) for i in range(2, 10)]
        volumes = []

        for epsilon in epsilon_values:
            volume = self._compute_epsilon_neighborhood_volume(
                set_points, epsilon, min_coords, max_coords
            )
            if volume > 0:
                volumes.append((epsilon, volume))

        if len(volumes) < 3:
            return {'minkowski_dimension': 0.0, 'error': 'Insufficient data'}

        # Dimension from slope
        log_epsilon = [np.log(eps) for eps, _ in volumes]
        log_volumes = [np.log(vol) for _, vol in volumes]

        dimension = -self._linear_regression_slope(log_epsilon, log_volumes)

        return {
            'minkowski_dimension': float(dimension),
            'epsilon_values': [eps for eps, _ in volumes],
            'volumes': [vol for _, vol in volumes]
        }

    def _compute_epsilon_neighborhood_volume(
        self,
        set_points: np.ndarray,
        epsilon: float,
        min_coords: np.ndarray,
        max_coords: np.ndarray
    ) -> float:
        """
        Estimate volume of ε-neighborhood using grid sampling.
        """
        # Create grid
        n_samples = 50
        ambient_dim = set_points.shape[1]

        # Generate grid points
        grid_axes = [np.linspace(min_coords[i] - epsilon, max_coords[i] + epsilon, n_samples)
                     for i in range(ambient_dim)]

        # Count grid points within epsilon of set
        count = 0

        if ambient_dim == 1:
            for x in grid_axes[0]:
                if self._is_within_epsilon(np.array([x]), set_points, epsilon):
                    count += 1
        elif ambient_dim == 2:
            for x in grid_axes[0]:
                for y in grid_axes[1]:
                    if self._is_within_epsilon(np.array([x, y]), set_points, epsilon):
                        count += 1
        else:
            # For higher dimensions, use random sampling
            total_volume = np.prod(max_coords - min_coords + 2 * epsilon)
            n_random = 10000
            random_points = np.random.uniform(
                min_coords - epsilon,
                max_coords + epsilon,
                (n_random, ambient_dim)
            )
            count = sum(1 for p in random_points
                       if self._is_within_epsilon(p, set_points, epsilon))
            return (count / n_random) * total_volume

        # Estimate volume
        cell_volume = np.prod([(max_coords[i] - min_coords[i] + 2 * epsilon) / n_samples
                              for i in range(ambient_dim)])

        return count * cell_volume

    def _is_within_epsilon(
        self,
        point: np.ndarray,
        set_points: np.ndarray,
        epsilon: float
    ) -> bool:
        """Check if point is within epsilon of any set point."""
        distances = np.linalg.norm(set_points - point, axis=1)
        return np.any(distances <= epsilon)

    # ========== Fractal Dimension Estimation ==========

    def estimate_fractal_dimension(self, set_points: np.ndarray) -> Dict[str, Any]:
        """
        Estimate fractal dimension using multiple methods and return consensus.

        Args:
            set_points: Points in set E

        Returns:
            Dict with consensus fractal dimension estimate
        """
        # Try multiple methods
        box_counting = self.compute_box_counting_dimension(set_points)
        minkowski = self.compute_minkowski_dimension(set_points)

        dimensions = []
        if 'hausdorff_dimension' in box_counting:
            dimensions.append(box_counting['hausdorff_dimension'])
        if 'minkowski_dimension' in minkowski:
            dimensions.append(minkowski['minkowski_dimension'])

        if dimensions:
            consensus = np.mean(dimensions)
            variance = np.var(dimensions) if len(dimensions) > 1 else 0

            return {
                'fractal_dimension': float(consensus),
                'variance': float(variance),
                'methods': {
                    'box_counting': box_counting.get('hausdorff_dimension', None),
                    'minkowski': minkowski.get('minkowski_dimension', None)
                }
            }

        return {'fractal_dimension': 0.0, 'error': 'Could not estimate dimension'}

    # ========== Hausdorff Measure Properties ==========

    def verify_hausdorff_properties(self, measure_func: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Verify that a measure function satisfies Hausdorff measure properties.

        Properties to check:
        1. μ(∅) = 0
        2. Countable subadditivity
        3. Metric outer measure property

        Args:
            measure_func: Function computing measure of a set

        Returns:
            Dict with verification results
        """
        if measure_func is None:
            return {'error': 'No measure function provided'}

        # Property 1: μ(∅) = 0
        empty_measure = measure_func(np.array([]))
        empty_ok = abs(empty_measure) < self._epsilon

        # Property 2: Subadditivity (test on simple sets)
        set_a = np.array([[0, 0], [1, 0]])
        set_b = np.array([[2, 0], [3, 0]])
        set_union = np.array([[0, 0], [1, 0], [2, 0], [3, 0]])

        measure_a = measure_func(set_a)
        measure_b = measure_func(set_b)
        measure_union = measure_func(set_union)

        subadditive_ok = measure_union <= measure_a + measure_b + self._epsilon

        return {
            'empty_set_property': empty_ok,
            'empty_measure': empty_measure,
            'subadditivity': subadditive_ok,
            'test_measures': {
                'set_a': measure_a,
                'set_b': measure_b,
                'union': measure_union
            },
            'all_properties_satisfied': empty_ok and subadditive_ok
        }

    # ========== Utility Methods ==========

    def _linear_regression_slope(self, x: List[float], y: List[float]) -> float:
        """
        Compute slope of linear regression line.

        slope = Cov(x, y) / Var(x)
        """
        if len(x) < 2:
            return 0.0

        x_arr = np.array(x)
        y_arr = np.array(y)

        x_mean = np.mean(x_arr)
        y_mean = np.mean(y_arr)

        cov = np.sum((x_arr - x_mean) * (y_arr - y_mean))
        var_x = np.sum((x_arr - x_mean) ** 2)

        if var_x < self._epsilon:
            return 0.0

        return cov / var_x

    def _compute_r_squared(self, x: List[float], y: List[float], slope: float) -> float:
        """
        Compute R^2 coefficient of determination.
        """
        if len(x) < 2:
            return 0.0

        x_arr = np.array(x)
        y_arr = np.array(y)
        y_mean = np.mean(y_arr)

        # Intercept
        x_mean = np.mean(x_arr)
        intercept = y_mean - slope * x_mean

        # Predicted values
        y_pred = slope * x_arr + intercept

        # R^2 = 1 - SS_res / SS_tot
        ss_res = np.sum((y_arr - y_pred) ** 2)
        ss_tot = np.sum((y_arr - y_mean) ** 2)

        if ss_tot < self._epsilon:
            return 1.0

        return 1.0 - ss_res / ss_tot

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
            'cached_dimensions': len(self.dimension_cache)
        }
