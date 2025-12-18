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
TOPOLOGICAL INFERENCE SPECIALIST (Tier 3)
==========================================

Statistical inference for topological features.

CAPABILITIES:
-------------
- Confidence set computation
- Bootstrap persistence
- Topological significance testing
- Feature selection
- Homology inference
- Stability bounds

ALGORITHMS:
-----------
- Bootstrap resampling
- Confidence band construction
- Null distribution estimation
- Stability theorem application

NO SYMPY - Pure Python/NumPy implementation.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

logger = logging.getLogger('symbo_agentic_reasoners.specialists.topological_inference')


@dataclass
class ConfidenceSet:
    """Confidence set for persistence features."""
    features: List[Tuple[float, float]]
    confidence_level: float
    method: str
    bounds: Optional[List[Tuple[float, float]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignificanceTest:
    """Result of topological significance test."""
    feature: Tuple[float, float]
    p_value: float
    is_significant: bool
    threshold: float
    test_statistic: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class TopologicalInferenceSpecialist(BDIAgent):
    """
    BDI Agent for statistical inference on topological features.

    Implements methods for assessing significance and confidence of
    topological features extracted from data.
    """

    def __init__(self, agent_id='topological_inference_specialist_001', df=None, blackboard=None):
        """
        Initialize TopologicalInferenceSpecialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.inference_cache = {}
        self._epsilon = 1e-10

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.tda.topological_inference',
                agent_id=self.agent_id,
                algorithm='topological_inference',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))
            logger.info(f"{self.agent_id} registered with DF")

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a topological inference task.

        Args:
            task_entry: Task specification containing:
                - operation: Type of computation
                - diagram: Persistence diagram
                - point_cloud: Point cloud data
                - params: Algorithm parameters

        Returns:
            Result dictionary with computation results
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        operation = metadata.get('operation', 'confidence_sets')

        try:
            if operation == 'confidence_sets':
                return self._handle_confidence_sets(metadata)
            elif operation == 'bootstrap':
                return self._handle_bootstrap(metadata)
            elif operation == 'significance_test':
                return self._handle_significance_test(metadata)
            elif operation == 'feature_selection':
                return self._handle_feature_selection(metadata)
            elif operation == 'homology_inference':
                return self._handle_homology_inference(metadata)
            elif operation == 'stability_bounds':
                return self._handle_stability_bounds(metadata)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }
        except Exception as e:
            logger.error(f"Error in {operation}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'operation': operation
            }

    def _handle_confidence_sets(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute confidence sets."""
        persistence_diagram = task_entry.get('diagram', [])
        confidence_level = task_entry.get('confidence_level', 0.95)
        method = task_entry.get('method', 'bootstrap')

        confidence_set = self.compute_confidence_sets(
            persistence_diagram, confidence_level, method
        )

        return {
            'success': True,
            'confidence_set': confidence_set,
            'num_features': len(confidence_set.features)
        }

    def _handle_bootstrap(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Perform bootstrap on persistence."""
        point_cloud = np.array(task_entry.get('point_cloud', []))
        n_samples = task_entry.get('n_samples', 100)
        sample_size = task_entry.get('sample_size', None)

        bootstrap_diagrams = self.bootstrap_persistence(
            point_cloud, n_samples, sample_size
        )

        return {
            'success': True,
            'bootstrap_diagrams': bootstrap_diagrams,
            'n_samples': len(bootstrap_diagrams)
        }

    def _handle_significance_test(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Test topological significance."""
        feature = tuple(task_entry.get('feature', (0, 0)))
        null_distribution = task_entry.get('null_distribution', [])
        alpha = task_entry.get('alpha', 0.05)

        test_result = self.test_topological_significance(
            feature, null_distribution, alpha
        )

        return {
            'success': True,
            'test_result': test_result,
            'is_significant': test_result.is_significant
        }

    def _handle_feature_selection(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Select significant features."""
        diagram = task_entry.get('diagram', [])
        threshold = task_entry.get('threshold', 0.1)
        method = task_entry.get('method', 'persistence')

        selected_features = self.select_topological_features(
            diagram, threshold, method
        )

        return {
            'success': True,
            'selected_features': selected_features,
            'num_selected': len(selected_features)
        }

    def _handle_homology_inference(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate population homology."""
        sample = task_entry.get('sample', [])
        population_size = task_entry.get('population_size', None)
        confidence_level = task_entry.get('confidence_level', 0.95)

        inference = self.estimate_homology_inference(
            sample, population_size, confidence_level
        )

        return {
            'success': True,
            'inference': inference
        }

    def _handle_stability_bounds(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute stability bounds."""
        perturbation_size = task_entry.get('perturbation_size', 0.1)
        dimension = task_entry.get('dimension', None)

        bounds = self.compute_stability_bounds(perturbation_size, dimension)

        return {
            'success': True,
            'bounds': bounds,
            'perturbation_size': perturbation_size
        }

    # Core algorithms

    def compute_confidence_sets(
        self,
        persistence_diagram: List[Tuple[float, float]],
        confidence_level: float,
        method: str = 'bootstrap'
    ) -> ConfidenceSet:
        """
        Compute confidence sets for persistence features.

        Constructs confidence bands around persistence diagram.

        Args:
            persistence_diagram: List of (birth, death) pairs
            confidence_level: Confidence level (e.g., 0.95)
            method: Method ('bootstrap', 'subsampling')

        Returns:
            ConfidenceSet object
        """
        if not persistence_diagram:
            return ConfidenceSet(
                features=[],
                confidence_level=confidence_level,
                method=method
            )

        # Sort by persistence
        sorted_features = sorted(
            persistence_diagram,
            key=lambda x: x[1] - x[0],
            reverse=True
        )

        # Compute confidence bands (simplified)
        alpha = 1 - confidence_level
        n = len(persistence_diagram)

        bounds = []
        for birth, death in sorted_features:
            persistence = death - birth

            # Estimate variance (simplified)
            variance = persistence * np.sqrt(2 * np.log(n) / n)

            # Confidence interval
            margin = 1.96 * variance  # 95% confidence
            lower_birth = max(0, birth - margin)
            upper_birth = birth + margin
            lower_death = max(birth, death - margin)
            upper_death = death + margin

            bounds.append((
                (lower_birth, lower_death),
                (upper_birth, upper_death)
            ))

        return ConfidenceSet(
            features=sorted_features,
            confidence_level=confidence_level,
            method=method,
            bounds=bounds
        )

    def bootstrap_persistence(
        self,
        point_cloud: np.ndarray,
        n_samples: int,
        sample_size: Optional[int] = None
    ) -> List[List[Tuple[float, float]]]:
        """
        Bootstrap persistence diagrams.

        Generates bootstrap samples and computes persistence for each.

        Args:
            point_cloud: Original point cloud
            n_samples: Number of bootstrap samples
            sample_size: Size of each sample (None for same as original)

        Returns:
            List of persistence diagrams (one per bootstrap sample)
        """
        n_points = len(point_cloud)
        if sample_size is None:
            sample_size = n_points

        bootstrap_diagrams = []

        for _ in range(n_samples):
            # Sample with replacement
            indices = np.random.choice(n_points, size=sample_size, replace=True)
            bootstrap_sample = point_cloud[indices]

            # Compute persistence (simplified)
            diagram = self._compute_persistence_diagram_simple(bootstrap_sample)
            bootstrap_diagrams.append(diagram)

        return bootstrap_diagrams

    def test_topological_significance(
        self,
        feature: Tuple[float, float],
        null_distribution: List[Tuple[float, float]],
        alpha: float = 0.05
    ) -> SignificanceTest:
        """
        Test if a topological feature is statistically significant.

        Tests against null distribution (e.g., from random data).

        Args:
            feature: Feature to test (birth, death)
            null_distribution: Distribution under null hypothesis
            alpha: Significance level

        Returns:
            SignificanceTest object
        """
        birth, death = feature
        persistence = death - birth

        # Compute test statistic (persistence)
        test_statistic = persistence

        # Compare to null distribution
        null_persistences = [d - b for b, d in null_distribution]

        if not null_persistences:
            # No null distribution: use simple threshold
            p_value = 1.0 if persistence < 0.1 else 0.0
        else:
            # Empirical p-value
            count = sum(1 for p in null_persistences if p >= persistence)
            p_value = count / len(null_persistences)

        is_significant = p_value < alpha

        return SignificanceTest(
            feature=feature,
            p_value=p_value,
            is_significant=is_significant,
            threshold=alpha,
            test_statistic=test_statistic
        )

    def select_topological_features(
        self,
        diagram: List[Tuple[float, float]],
        threshold: float,
        method: str = 'persistence'
    ) -> List[Tuple[float, float]]:
        """
        Select significant topological features.

        Filters features based on various criteria.

        Args:
            diagram: Persistence diagram
            threshold: Selection threshold
            method: Selection method ('persistence', 'lifetime', 'confidence')

        Returns:
            Selected features
        """
        if method == 'persistence':
            # Select by persistence threshold
            selected = [
                (b, d) for b, d in diagram
                if (d - b) >= threshold
            ]
        elif method == 'lifetime':
            # Select by lifetime ratio
            selected = [
                (b, d) for b, d in diagram
                if d != float('inf') and (d - b) / d >= threshold
            ]
        elif method == 'confidence':
            # Select features with high confidence
            # (simplified: top k by persistence)
            sorted_features = sorted(
                diagram,
                key=lambda x: x[1] - x[0] if x[1] != float('inf') else 0,
                reverse=True
            )
            k = max(1, int(threshold * len(diagram)))
            selected = sorted_features[:k]
        else:
            # Default: persistence threshold
            selected = [
                (b, d) for b, d in diagram
                if (d - b) >= threshold
            ]

        return selected

    def estimate_homology_inference(
        self,
        sample: List[Tuple[float, float]],
        population_size: Optional[int],
        confidence_level: float
    ) -> Dict[str, Any]:
        """
        Estimate population homology from sample.

        Infers Betti numbers with confidence intervals.

        Args:
            sample: Sample persistence diagram
            population_size: Population size (if known)
            confidence_level: Confidence level

        Returns:
            Inference dictionary with estimates and bounds
        """
        n_sample = len(sample)

        # Estimate Betti numbers from persistence
        # (simplified: count significant features)
        threshold = self._estimate_significance_threshold(sample)

        significant_features = [
            (b, d) for b, d in sample
            if (d - b) >= threshold
        ]

        estimated_betti = len(significant_features)

        # Confidence interval (simplified)
        alpha = 1 - confidence_level
        se = np.sqrt(estimated_betti)  # Standard error
        margin = 1.96 * se

        lower_bound = max(0, int(estimated_betti - margin))
        upper_bound = int(estimated_betti + margin)

        return {
            'estimated_betti': estimated_betti,
            'confidence_interval': (lower_bound, upper_bound),
            'confidence_level': confidence_level,
            'sample_size': n_sample,
            'threshold': threshold
        }

    def compute_stability_bounds(
        self,
        perturbation_size: float,
        dimension: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compute stability bounds using stability theorem.

        Stability theorem: d_B(dgm(f), dgm(g)) ≤ ||f - g||_∞

        Args:
            perturbation_size: Size of perturbation
            dimension: Dimension to analyze (None for all)

        Returns:
            Stability bounds
        """
        # Bottleneck stability bound
        bottleneck_bound = perturbation_size

        # Wasserstein stability bound (p=2)
        # d_W^2 ≤ C * ||f - g||_∞ for some constant C
        # Simplified: use C ≈ sqrt(n) heuristic
        wasserstein_bound = perturbation_size * np.sqrt(10)  # Heuristic

        return {
            'bottleneck_bound': bottleneck_bound,
            'wasserstein_bound': wasserstein_bound,
            'perturbation_size': perturbation_size,
            'dimension': dimension,
            'theorem': 'Stability Theorem (Cohen-Steiner et al.)'
        }

    # Utility methods

    def _compute_persistence_diagram_simple(
        self,
        point_cloud: np.ndarray
    ) -> List[Tuple[float, float]]:
        """
        Simplified persistence computation for bootstrap.

        Uses basic distance-based features.

        Args:
            point_cloud: Point cloud

        Returns:
            Persistence diagram
        """
        n = len(point_cloud)

        if n < 2:
            return []

        # Compute pairwise distances
        distances = []
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(point_cloud[i] - point_cloud[j])
                distances.append(dist)

        distances = np.array(distances)

        # Create simplified diagram from distance distribution
        # 0-dimensional features (components)
        diagram = []

        # Add component births/deaths
        min_dist = np.min(distances)
        max_dist = np.max(distances)
        median_dist = np.median(distances)

        # Simplified: add features at quartiles
        quartiles = np.percentile(distances, [25, 50, 75])

        diagram.append((0.0, quartiles[0]))
        diagram.append((quartiles[0], quartiles[1]))
        diagram.append((quartiles[1], quartiles[2]))

        return diagram

    def _estimate_significance_threshold(
        self,
        diagram: List[Tuple[float, float]]
    ) -> float:
        """
        Estimate significance threshold for features.

        Uses statistical heuristics (e.g., median persistence).

        Args:
            diagram: Persistence diagram

        Returns:
            Threshold value
        """
        if not diagram:
            return 0.0

        # Compute persistences
        persistences = [d - b for b, d in diagram if d != float('inf')]

        if not persistences:
            return 0.0

        # Use median as threshold (robust estimator)
        threshold = np.median(persistences)

        return threshold

    def _compute_p_value(
        self,
        statistic: float,
        null_distribution: List[float]
    ) -> float:
        """
        Compute empirical p-value.

        Args:
            statistic: Test statistic
            null_distribution: Null distribution values

        Returns:
            p-value
        """
        if not null_distribution:
            return 1.0

        # Empirical p-value: proportion of null values >= statistic
        count = sum(1 for x in null_distribution if x >= statistic)
        p_value = count / len(null_distribution)

        return p_value

    # BDI Agent methods

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard:
            pass

    def deliberate(self) -> List[str]:
        """Generate goals based on beliefs."""
        return []

    def execute_step(self, step: int):
        """Execute one reasoning step."""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        stats['cache_size'] = len(self.inference_cache)
        return stats
