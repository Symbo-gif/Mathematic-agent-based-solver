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
INVARIANT MEASURES SPECIALIST - Existence, uniqueness, ergodicity verification
=================================================================================

Manages tasks related to invariant measures, Krylov-Bogoliubov theorem, ergodicity,
and Poincare recurrence.

CRITICAL ALGORITHMS:
-------------------
- Invariant Measure Verification: Check μ(T⁻¹A) = μ(A)
- Krylov-Bogoliubov Construction: Construct invariant measure
- Ergodicity Test: Check if only trivial invariant sets exist
- Poincare Recurrence: Verify recurrence theorem
- Probability on Orbits: Compute orbit distribution

WHY THIS MATTERS:
----------------
Invariant measures are fundamental to:
- Understanding long-term behavior of dynamical systems
- Ergodic theory and statistical mechanics
- Probability theory on dynamical systems
- Foundations of ergodic theorems

CAPABILITIES:
------------
- Verify invariant measures for transformations
- Construct invariant measures using Krylov-Bogoliubov
- Test ergodicity of measures
- Apply Poincare recurrence theorem
- Compute probability distributions on orbits
- Check uniqueness of invariant measures
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class InvariantMeasureSpecialist(BDIAgent):
    """
    Invariant Measures Specialist - Existence, uniqueness, ergodicity verification

    DIRECTIVE:
    ---------
    Handle all invariant measure operations with emphasis on:
    - Invariant measure verification
    - Krylov-Bogoliubov measure construction
    - Ergodicity testing
    - Poincare recurrence application

    KEY ALGORITHMS:
    --------------
    - Verify Invariance: Check μ(T⁻¹A) = μ(A)
    - KB Construction: Build invariant measure via Cesaro averages
    - Ergodicity Test: Check if ergodic
    - Recurrence: Apply Poincare recurrence theorem

    OPERATIONS:
    ----------
    - verify_invariant_measure(transformation, measure)
    - compute_krylov_bogoliubov_measure(transformation)
    - check_ergodicity(transformation, measure)
    - verify_uniqueness(transformation)
    - compute_probability_on_orbit(transformation, initial_point, set_A)
    - apply_poincare_recurrence(transformation, set_A)
    """

    def __init__(self, agent_id='invariant_measures_specialist_001', df=None, blackboard=None):
        """
        Initialize Invariant Measures Specialist

        Args:
            agent_id: Unique identifier for this agent
            df: Directory Facilitator instance
            blackboard: Shared blackboard instance
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_tasks = []
        self.measure_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.ergodic.invariant_measures',
                agent_id=self.agent_id,
                algorithm='invariant_measures',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process invariant measures task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of invariant measures operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'verify_invariant')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'verify_invariant':
                return self._process_verify_invariant(metadata)
            elif problem_type == 'krylov_bogoliubov':
                return self._process_krylov_bogoliubov(metadata)
            elif problem_type == 'check_ergodicity':
                return self._process_check_ergodicity(metadata)
            elif problem_type == 'verify_uniqueness':
                return self._process_verify_uniqueness(metadata)
            elif problem_type == 'orbit_probability':
                return self._process_orbit_probability(metadata)
            elif problem_type == 'poincare_recurrence':
                return self._process_poincare_recurrence(metadata)
            else:
                return self._process_verify_invariant(metadata)

        except Exception as e:
            return {
                'operation': 'invariant_measures',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_verify_invariant(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process invariant measure verification request"""
        transformation = metadata.get('transformation')
        measure = metadata.get('measure')

        result = self.verify_invariant_measure(transformation, measure)
        return {
            'operation': 'verify_invariant_measure',
            **result
        }

    def _process_krylov_bogoliubov(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Krylov-Bogoliubov measure construction request"""
        transformation = metadata.get('transformation')
        initial_point = metadata.get('initial_point', 0.5)

        result = self.compute_krylov_bogoliubov_measure(transformation, initial_point)
        return {
            'operation': 'krylov_bogoliubov_measure',
            **result
        }

    def _process_check_ergodicity(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process ergodicity check request"""
        transformation = metadata.get('transformation')
        measure = metadata.get('measure')

        result = self.check_ergodicity(transformation, measure)
        return {
            'operation': 'check_ergodicity',
            **result
        }

    def _process_verify_uniqueness(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process uniqueness verification request"""
        transformation = metadata.get('transformation')

        result = self.verify_uniqueness(transformation)
        return {
            'operation': 'verify_uniqueness',
            **result
        }

    def _process_orbit_probability(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process orbit probability computation request"""
        transformation = metadata.get('transformation')
        initial_point = metadata.get('initial_point', 0.5)
        set_A = metadata.get('set_A', (0.0, 0.5))

        result = self.compute_probability_on_orbit(transformation, initial_point, set_A)
        return {
            'operation': 'orbit_probability',
            **result
        }

    def _process_poincare_recurrence(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Poincare recurrence application request"""
        transformation = metadata.get('transformation')
        set_A = metadata.get('set_A', (0.0, 0.5))

        result = self.apply_poincare_recurrence(transformation, set_A)
        return {
            'operation': 'poincare_recurrence',
            **result
        }

    def verify_invariant_measure(
        self,
        transformation: Optional[Callable] = None,
        measure: Optional[Dict[str, float]] = None,
        n_samples: int = 10000
    ) -> Dict[str, Any]:
        """
        Verify if measure is invariant under transformation

        A measure μ is invariant if μ(T⁻¹A) = μ(A) for all measurable sets A.
        We verify this numerically by checking if distribution is preserved.

        Args:
            transformation: Dynamical system T: X → X
            measure: Dictionary mapping intervals to probabilities
            n_samples: Number of samples for verification

        Returns:
            Dict with is_invariant, error, explanation
        """
        if transformation is None:
            # Default: doubling map on [0,1)
            transformation = lambda x: (2 * x) % 1.0

        if measure is None:
            # Default: Lebesgue measure on [0,1)
            measure = {(0.0, 1.0): 1.0}

        # Sample points according to measure
        points = self._sample_from_measure(measure, n_samples)

        # Apply transformation
        transformed_points = np.array([transformation(p) for p in points])

        # Check if distribution is preserved
        errors = []
        for interval, prob in measure.items():
            a, b = interval

            # Count points in interval before transformation
            in_interval_before = np.sum((points >= a) & (points < b))
            empirical_prob_before = in_interval_before / n_samples

            # Count points in interval after transformation
            in_interval_after = np.sum((transformed_points >= a) & (transformed_points < b))
            empirical_prob_after = in_interval_after / n_samples

            # Compute error
            error = abs(empirical_prob_after - prob)
            errors.append(error)

        max_error = max(errors) if errors else 0.0
        is_invariant = max_error < 0.05  # Tolerance for numerical verification

        return {
            'is_invariant': is_invariant,
            'max_error': float(max_error),
            'n_samples': n_samples,
            'measure': str(measure),
            'explanation': f"Measure is {'invariant' if is_invariant else 'NOT invariant'} (max error: {max_error:.4f})",
            'definition': 'μ(T⁻¹A) = μ(A) for all measurable sets A'
        }

    def compute_krylov_bogoliubov_measure(
        self,
        transformation: Optional[Callable] = None,
        initial_point: float = 0.5,
        n_iterations: int = 10000
    ) -> Dict[str, Any]:
        """
        Construct invariant measure using Krylov-Bogoliubov theorem

        KB Theorem: Every continuous map on a compact metric space
        admits at least one invariant probability measure.

        Construction: μ_n = (1/n) Σ_{i=0}^{n-1} δ_{T^i(x)}

        Args:
            transformation: Continuous map T: X → X
            initial_point: Starting point x₀
            n_iterations: Number of iterations for Cesaro average

        Returns:
            Dict with measure (histogram), convergence info, explanation
        """
        if transformation is None:
            # Default: tent map
            transformation = lambda x: 2*x if x < 0.5 else 2*(1-x)

        # Generate orbit
        orbit = [initial_point]
        current = initial_point

        for _ in range(n_iterations):
            current = transformation(current)
            orbit.append(current)

        orbit = np.array(orbit)

        # Construct empirical measure via histogram
        n_bins = 50
        hist, bin_edges = np.histogram(orbit, bins=n_bins, range=(0.0, 1.0), density=True)
        hist = hist / n_bins  # Normalize to probability

        # Verify invariance by comparing successive windows
        window1 = orbit[:n_iterations//2]
        window2 = orbit[n_iterations//2:]

        hist1, _ = np.histogram(window1, bins=n_bins, range=(0.0, 1.0), density=True)
        hist2, _ = np.histogram(window2, bins=n_bins, range=(0.0, 1.0), density=True)

        convergence_error = np.mean(np.abs(hist1 - hist2))

        return {
            'measure_histogram': hist.tolist(),
            'bin_edges': bin_edges.tolist(),
            'n_iterations': n_iterations,
            'convergence_error': float(convergence_error),
            'explanation': 'Krylov-Bogoliubov: Cesaro average (1/n)Σδ_{T^i(x)} converges to invariant measure',
            'theorem': 'Every continuous map on compact metric space has invariant measure',
            'convergence': 'Weak-* convergence of empirical measures'
        }

    def check_ergodicity(
        self,
        transformation: Optional[Callable] = None,
        measure: Optional[Dict[str, float]] = None,
        n_test_sets: int = 10,
        n_samples: int = 5000
    ) -> Dict[str, Any]:
        """
        Check if transformation is ergodic with respect to measure

        Ergodic: A set A is invariant (T⁻¹A = A) ⟹ μ(A) ∈ {0, 1}
        Equivalently: Only trivial invariant sets (measure 0 or 1)

        Args:
            transformation: Dynamical system T
            measure: Invariant measure μ
            n_test_sets: Number of test sets to check
            n_samples: Sample size for verification

        Returns:
            Dict with is_ergodic, test results, explanation
        """
        if transformation is None:
            # Default: doubling map (ergodic w.r.t. Lebesgue)
            transformation = lambda x: (2 * x) % 1.0

        # Sample initial points
        points = np.random.random(n_samples)

        # Test several candidate invariant sets
        test_results = []

        for i in range(n_test_sets):
            # Create random test set
            a = np.random.random()
            b = a + np.random.random() * (1.0 - a)
            test_set = (a, b)

            # Check if set is approximately invariant
            in_set = (points >= a) & (points < b)
            initial_measure = np.mean(in_set)

            # Apply transformation and check
            transformed = np.array([transformation(p) for p in points])
            in_set_after = (transformed >= a) & (transformed < b)
            transformed_measure = np.mean(in_set_after)

            # Check if approximately invariant
            is_invariant = abs(initial_measure - transformed_measure) < 0.05

            # If invariant, check if trivial (measure 0 or 1)
            is_trivial = initial_measure < 0.05 or initial_measure > 0.95

            test_results.append({
                'set': test_set,
                'measure': float(initial_measure),
                'is_invariant': is_invariant,
                'is_trivial': is_trivial
            })

        # Ergodic if all invariant sets are trivial
        invariant_sets = [t for t in test_results if t['is_invariant']]
        non_trivial_invariant = [t for t in invariant_sets if not t['is_trivial']]

        is_ergodic = len(non_trivial_invariant) == 0

        return {
            'is_ergodic': is_ergodic,
            'test_results': test_results[:3],  # Show first 3
            'n_invariant_sets_found': len(invariant_sets),
            'n_non_trivial_invariant': len(non_trivial_invariant),
            'explanation': f"System is {'ergodic' if is_ergodic else 'NOT ergodic'} (no non-trivial invariant sets)",
            'definition': 'Ergodic: T⁻¹A = A ⟹ μ(A) ∈ {0,1}',
            'consequence': 'Ergodic ⟹ time average = space average (Birkhoff theorem)'
        }

    def verify_uniqueness(
        self,
        transformation: Optional[Callable] = None,
        n_initial_points: int = 10,
        n_iterations: int = 5000
    ) -> Dict[str, Any]:
        """
        Check uniqueness of invariant measure

        Tests if different initial points converge to same invariant measure
        (Krylov-Bogoliubov guarantees existence, not uniqueness)

        Args:
            transformation: Dynamical system T
            n_initial_points: Number of different starting points
            n_iterations: Iterations per starting point

        Returns:
            Dict with is_unique, measures, explanation
        """
        if transformation is None:
            # Default: tent map (unique invariant measure)
            transformation = lambda x: 2*x if x < 0.5 else 2*(1-x)

        # Compute measures from different initial points
        measures = []

        for i in range(n_initial_points):
            initial = i / n_initial_points

            # Generate orbit
            orbit = [initial]
            current = initial
            for _ in range(n_iterations):
                current = transformation(current)
                orbit.append(current)

            # Compute empirical measure
            hist, _ = np.histogram(orbit, bins=20, range=(0.0, 1.0), density=True)
            measures.append(hist / 20)

        # Compare all measures
        measures = np.array(measures)
        mean_measure = np.mean(measures, axis=0)

        # Compute variation between measures
        max_variation = np.max([np.max(np.abs(m - mean_measure)) for m in measures])

        is_unique = max_variation < 0.1  # Tolerance

        return {
            'is_unique': is_unique,
            'max_variation': float(max_variation),
            'n_initial_points': n_initial_points,
            'mean_measure': mean_measure.tolist(),
            'explanation': f"Invariant measure is {'unique' if is_unique else 'NOT unique'} (variation: {max_variation:.4f})",
            'note': 'Krylov-Bogoliubov guarantees existence, not uniqueness',
            'uniqueness_condition': 'Ergodicity + uniqueness ⟹ unique ergodic measure'
        }

    def compute_probability_on_orbit(
        self,
        transformation: Optional[Callable] = None,
        initial_point: float = 0.5,
        set_A: Tuple[float, float] = (0.0, 0.5),
        n_iterations: int = 10000
    ) -> Dict[str, Any]:
        """
        Compute probability that orbit visits set A

        For ergodic systems with invariant measure μ:
        (# visits to A) / n → μ(A) as n → ∞

        Args:
            transformation: Dynamical system T
            initial_point: Starting point x₀
            set_A: Measurable set [a, b)
            n_iterations: Number of iterations

        Returns:
            Dict with empirical_probability, convergence info
        """
        if transformation is None:
            transformation = lambda x: (2 * x) % 1.0

        a, b = set_A

        # Generate orbit
        current = initial_point
        visits = 0
        visit_history = []

        for i in range(n_iterations):
            current = transformation(current)

            if a <= current < b:
                visits += 1

            # Track convergence
            if i > 0 and i % 1000 == 0:
                visit_history.append(visits / (i + 1))

        empirical_prob = visits / n_iterations

        # For Lebesgue measure on [0,1), theoretical prob = b - a
        theoretical_prob = b - a
        error = abs(empirical_prob - theoretical_prob)

        return {
            'empirical_probability': float(empirical_prob),
            'theoretical_probability': float(theoretical_prob),
            'error': float(error),
            'n_iterations': n_iterations,
            'visits': visits,
            'set_A': set_A,
            'convergence_history': visit_history,
            'explanation': f"Orbit visits set A with probability {empirical_prob:.4f}",
            'ergodic_theorem': 'For ergodic systems: (visits to A)/n → μ(A)'
        }

    def apply_poincare_recurrence(
        self,
        transformation: Optional[Callable] = None,
        set_A: Tuple[float, float] = (0.4, 0.6),
        initial_point: Optional[float] = None,
        max_iterations: int = 100000
    ) -> Dict[str, Any]:
        """
        Apply Poincare recurrence theorem

        Theorem: For measure-preserving T on finite measure space,
        almost every point returns arbitrarily close to its initial position infinitely often.

        Args:
            transformation: Measure-preserving transformation T
            set_A: Measurable set with μ(A) > 0
            initial_point: Starting point in A (or random if None)
            max_iterations: Maximum iterations to find recurrence

        Returns:
            Dict with recurrence_time, returns_found, explanation
        """
        if transformation is None:
            # Default: rotation (all points recur)
            alpha = (np.sqrt(5) - 1) / 2  # Irrational rotation
            transformation = lambda x: (x + alpha) % 1.0

        a, b = set_A

        if initial_point is None:
            # Start in set A
            initial_point = (a + b) / 2

        # Track orbit and recurrences
        current = initial_point
        recurrence_times = []
        epsilon = (b - a) / 10  # Recurrence tolerance

        for i in range(1, max_iterations):
            current = transformation(current)

            # Check if returned to neighborhood of initial point
            if abs(current - initial_point) < epsilon:
                recurrence_times.append(i)

                if len(recurrence_times) >= 5:  # Found enough recurrences
                    break

        return {
            'recurrence_times': recurrence_times[:5],
            'returns_found': len(recurrence_times),
            'first_return_time': recurrence_times[0] if recurrence_times else None,
            'set_A': set_A,
            'initial_point': initial_point,
            'explanation': f"Point returned to neighborhood {len(recurrence_times)} times",
            'theorem': 'Poincare Recurrence: Almost every point returns infinitely often',
            'note': 'Return time depends on measure of neighborhood'
        }

    def _sample_from_measure(self, measure: Dict[Tuple[float, float], float], n: int) -> np.ndarray:
        """Sample points according to probability measure"""
        points = []

        for interval, prob in measure.items():
            a, b = interval
            n_samples = int(n * prob)
            samples = np.random.uniform(a, b, n_samples)
            points.extend(samples)

        # Fill remaining if rounding lost samples
        while len(points) < n:
            # Sample from first interval
            interval = list(measure.keys())[0]
            a, b = interval
            points.append(np.random.uniform(a, b))

        return np.array(points[:n])

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new invariant measure problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Clear cache if too many measures stored
        if self.tasks_executed > 50 and len(self.measure_cache) > 20:
            intentions.append(Intention(
                action='update_measure_cache',
                priority=1,
                description='Clear old cached measures'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'update_measure_cache':
            # Keep only recent cache entries
            if len(self.measure_cache) > 20:
                keys = list(self.measure_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.measure_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.measure_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
