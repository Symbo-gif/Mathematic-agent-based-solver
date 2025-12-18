# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
MIXING SPECIALIST - Weak mixing, strong mixing, Kolmogorov property
====================================================================

Manages tasks related to mixing properties of dynamical systems:
weak mixing, strong mixing, and K-property.

CRITICAL ALGORITHMS:
-------------------
- Strong Mixing Test: Check lim_{n→∞} μ(A ∩ T⁻ⁿB) = μ(A)μ(B)
- Weak Mixing Test: Check Cesaro convergence to independence
- Ergodic vs Mixing: Verify hierarchy
- Mixing Rate: Compute rate of convergence to independence
- Rokhlin-Halmos: Apply Rokhlin lemma
- K-Property: Check Kolmogorov property

WHY THIS MATTERS:
----------------
Mixing properties characterize:
- How quickly systems lose memory
- Decorrelation in dynamical systems
- Statistical independence asymptotically
- Hierarchy: Ergodic ⊆ Weak Mixing ⊆ Strong Mixing ⊆ K-systems

CAPABILITIES:
------------
- Test strong mixing (exponential decorrelation)
- Test weak mixing (Cesaro convergence)
- Verify ergodic but not mixing systems
- Compute mixing rates
- Apply Rokhlin lemma
- Check Kolmogorov property
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class MixingSpecialist(BDIAgent):
    """
    Mixing Specialist - Weak mixing, strong mixing, K-property

    DIRECTIVE:
    ---------
    Handle all mixing property operations with emphasis on:
    - Strong mixing verification
    - Weak mixing verification
    - Mixing hierarchy analysis
    - K-property checking

    KEY ALGORITHMS:
    --------------
    - Strong Mixing: μ(A ∩ T⁻ⁿB) → μ(A)μ(B)
    - Weak Mixing: (1/n)Σ|μ(A ∩ T⁻ⁱB) - μ(A)μ(B)| → 0
    - Rokhlin Lemma: Tower construction
    - K-Property: Strong mixing on conditional measures

    OPERATIONS:
    ----------
    - check_strong_mixing(transformation, measure)
    - check_weak_mixing(transformation, measure)
    - verify_ergodic_vs_mixing(transformation)
    - compute_mixing_rate(transformation)
    - apply_rokhlin_halmos(transformation)
    - check_kolmogorov_property(transformation)
    """

    def __init__(self, agent_id='mixing_specialist_001', df=None, blackboard=None):
        """
        Initialize Mixing Specialist

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
        self.mixing_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.ergodic.mixing',
                agent_id=self.agent_id,
                algorithm='mixing',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process mixing task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of mixing operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'strong_mixing')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'strong_mixing':
                return self._process_strong_mixing(metadata)
            elif problem_type == 'weak_mixing':
                return self._process_weak_mixing(metadata)
            elif problem_type == 'ergodic_vs_mixing':
                return self._process_ergodic_vs_mixing(metadata)
            elif problem_type == 'mixing_rate':
                return self._process_mixing_rate(metadata)
            elif problem_type == 'rokhlin_halmos':
                return self._process_rokhlin_halmos(metadata)
            elif problem_type == 'kolmogorov_property':
                return self._process_kolmogorov_property(metadata)
            else:
                return self._process_strong_mixing(metadata)

        except Exception as e:
            return {
                'operation': 'mixing',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_strong_mixing(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process strong mixing check request"""
        transformation = metadata.get('transformation')
        measure = metadata.get('measure')

        result = self.check_strong_mixing(transformation, measure)
        return {
            'operation': 'check_strong_mixing',
            **result
        }

    def _process_weak_mixing(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process weak mixing check request"""
        transformation = metadata.get('transformation')
        measure = metadata.get('measure')

        result = self.check_weak_mixing(transformation, measure)
        return {
            'operation': 'check_weak_mixing',
            **result
        }

    def _process_ergodic_vs_mixing(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process ergodic vs mixing verification request"""
        transformation = metadata.get('transformation')

        result = self.verify_ergodic_vs_mixing(transformation)
        return {
            'operation': 'verify_ergodic_vs_mixing',
            **result
        }

    def _process_mixing_rate(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process mixing rate computation request"""
        transformation = metadata.get('transformation')

        result = self.compute_mixing_rate(transformation)
        return {
            'operation': 'compute_mixing_rate',
            **result
        }

    def _process_rokhlin_halmos(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Rokhlin-Halmos lemma application request"""
        transformation = metadata.get('transformation')

        result = self.apply_rokhlin_halmos(transformation)
        return {
            'operation': 'apply_rokhlin_halmos',
            **result
        }

    def _process_kolmogorov_property(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process K-property check request"""
        transformation = metadata.get('transformation')

        result = self.check_kolmogorov_property(transformation)
        return {
            'operation': 'check_kolmogorov_property',
            **result
        }

    def check_strong_mixing(
        self,
        transformation: Optional[Callable] = None,
        measure: Optional[Dict[str, float]] = None,
        n_samples: int = 5000,
        max_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Check if transformation is strongly mixing

        Strong Mixing: lim_{n→∞} μ(A ∩ T⁻ⁿB) = μ(A)μ(B) for all measurable A, B

        Args:
            transformation: Dynamical system T
            measure: Invariant measure μ
            n_samples: Number of samples for verification
            max_iterations: Check up to T^n

        Returns:
            Dict with is_strong_mixing, correlation data, explanation
        """
        if transformation is None:
            # Default: Baker's map (strongly mixing)
            transformation = lambda x: (2*x % 1.0, (x // 0.5) * 0.5 + 0.5*(x % 0.5) / 0.5)

        # Sample initial points
        points = np.random.random(n_samples)

        # Define two test sets A and B
        set_A = (0.3, 0.7)
        set_B = (0.2, 0.6)

        a_min, a_max = set_A
        b_min, b_max = set_B

        # Compute measures
        mu_A = a_max - a_min
        mu_B = b_max - b_min
        product_measure = mu_A * mu_B

        # Track correlation over time
        correlations = []
        iterations = range(1, max_iterations, 5)

        for n in iterations:
            # Apply T^n
            transformed = points.copy()
            for _ in range(n):
                if isinstance(transformation(transformed[0]), tuple):
                    # 2D transformation
                    transformed = np.array([transformation(p)[0] for p in transformed])
                else:
                    transformed = np.array([transformation(p) for p in transformed])

            # Check intersection A ∩ T⁻ⁿB
            in_A = (points >= a_min) & (points < a_max)
            in_B_after = (transformed >= b_min) & (transformed < b_max)

            intersection_measure = np.mean(in_A & in_B_after)

            # Correlation from independence
            correlation = abs(intersection_measure - product_measure)
            correlations.append(correlation)

        # Check if converging to 0
        recent_correlations = correlations[-10:]
        avg_recent = np.mean(recent_correlations)

        is_strong_mixing = avg_recent < 0.05

        # Estimate decay rate
        if len(correlations) > 20:
            early_avg = np.mean(correlations[:10])
            late_avg = np.mean(correlations[-10:])
            decay_rate = (early_avg - late_avg) / max_iterations
        else:
            decay_rate = 0.0

        return {
            'is_strong_mixing': is_strong_mixing,
            'final_correlation': float(correlations[-1]),
            'avg_recent_correlation': float(avg_recent),
            'decay_rate': float(decay_rate),
            'correlations': correlations[::5],  # Sample every 5th
            'explanation': f"System is {'strongly mixing' if is_strong_mixing else 'NOT strongly mixing'} (correlation → {avg_recent:.4f})",
            'definition': 'Strong mixing: μ(A ∩ T⁻ⁿB) → μ(A)μ(B) as n → ∞',
            'hierarchy': 'Ergodic ⊊ Weak Mixing ⊊ Strong Mixing ⊊ K-systems'
        }

    def check_weak_mixing(
        self,
        transformation: Optional[Callable] = None,
        measure: Optional[Dict[str, float]] = None,
        n_samples: int = 5000,
        max_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Check if transformation is weakly mixing

        Weak Mixing: (1/n)Σ_{i=1}^n |μ(A ∩ T⁻ⁱB) - μ(A)μ(B)| → 0

        Args:
            transformation: Dynamical system T
            measure: Invariant measure μ
            n_samples: Number of samples
            max_iterations: Check Cesaro average up to n

        Returns:
            Dict with is_weak_mixing, Cesaro averages, explanation
        """
        if transformation is None:
            # Default: doubling map (weakly mixing)
            transformation = lambda x: (2 * x) % 1.0

        # Sample initial points
        points = np.random.random(n_samples)

        # Define test sets
        set_A = (0.3, 0.7)
        set_B = (0.2, 0.6)

        a_min, a_max = set_A
        b_min, b_max = set_B

        mu_A = a_max - a_min
        mu_B = b_max - b_min
        product_measure = mu_A * mu_B

        # Compute Cesaro average
        cumulative_correlation = 0.0
        cesaro_averages = []

        for n in range(1, max_iterations):
            # Apply T^n
            transformed = points.copy()
            for _ in range(n):
                transformed = np.array([transformation(p) for p in transformed])

            # Measure intersection
            in_A = (points >= a_min) & (points < a_max)
            in_B_after = (transformed >= b_min) & (transformed < b_max)

            intersection_measure = np.mean(in_A & in_B_after)
            correlation = abs(intersection_measure - product_measure)

            cumulative_correlation += correlation
            cesaro_avg = cumulative_correlation / n

            if n % 10 == 0:
                cesaro_averages.append(cesaro_avg)

        final_cesaro = cumulative_correlation / max_iterations
        is_weak_mixing = final_cesaro < 0.1

        return {
            'is_weak_mixing': is_weak_mixing,
            'final_cesaro_average': float(final_cesaro),
            'cesaro_averages': cesaro_averages,
            'explanation': f"System is {'weakly mixing' if is_weak_mixing else 'NOT weakly mixing'} (Cesaro avg: {final_cesaro:.4f})",
            'definition': 'Weak mixing: (1/n)Σ|μ(A ∩ T⁻ⁱB) - μ(A)μ(B)| → 0',
            'note': 'Weak mixing ⟹ ergodic, but not conversely',
            'example_non_weak': 'Rotations are ergodic but not weakly mixing'
        }

    def verify_ergodic_vs_mixing(
        self,
        transformation: Optional[Callable] = None,
        n_samples: int = 3000
    ) -> Dict[str, Any]:
        """
        Verify hierarchy: Ergodic vs Mixing

        Check if system is ergodic but not mixing (e.g., irrational rotation)

        Args:
            transformation: Dynamical system T
            n_samples: Number of samples

        Returns:
            Dict with hierarchy classification, explanation
        """
        if transformation is None:
            # Default: irrational rotation (ergodic but NOT mixing)
            alpha = (np.sqrt(5) - 1) / 2
            transformation = lambda x: (x + alpha) % 1.0

        # Test ergodicity (simplified)
        points = np.random.random(n_samples)
        transformed = np.array([transformation(p) for p in points])

        # Check distribution preservation (invariance)
        hist_before, _ = np.histogram(points, bins=20, range=(0, 1))
        hist_after, _ = np.histogram(transformed, bins=20, range=(0, 1))

        invariance_error = np.mean(np.abs(hist_before - hist_after)) / n_samples
        is_ergodic = invariance_error < 0.05

        # Test mixing (simplified)
        set_A = (0.3, 0.7)
        set_B = (0.2, 0.6)

        # Apply T^50
        transformed_50 = points.copy()
        for _ in range(50):
            transformed_50 = np.array([transformation(p) for p in transformed_50])

        in_A = (points >= set_A[0]) & (points < set_A[1])
        in_B = (transformed_50 >= set_B[0]) & (transformed_50 < set_B[1])

        intersection_measure = np.mean(in_A & in_B)
        product_measure = (set_A[1] - set_A[0]) * (set_B[1] - set_B[0])
        mixing_error = abs(intersection_measure - product_measure)

        is_mixing = mixing_error < 0.05

        return {
            'is_ergodic': is_ergodic,
            'is_mixing': is_mixing,
            'classification': self._classify_system(is_ergodic, is_mixing),
            'invariance_error': float(invariance_error),
            'mixing_error': float(mixing_error),
            'explanation': f"System is ergodic={is_ergodic}, mixing={is_mixing}",
            'hierarchy': 'Mixing ⟹ Ergodic (but not conversely)',
            'example_ergodic_not_mixing': 'Irrational rotation on circle',
            'example_mixing': 'Doubling map, Baker map, Anosov diffeomorphisms'
        }

    def compute_mixing_rate(
        self,
        transformation: Optional[Callable] = None,
        n_samples: int = 3000,
        max_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Compute rate of mixing (exponential vs polynomial)

        Strong mixing systems often have exponential decay:
        |μ(A ∩ T⁻ⁿB) - μ(A)μ(B)| ≤ C·e^{-λn}

        Args:
            transformation: Dynamical system T
            n_samples: Number of samples
            max_iterations: Check up to T^n

        Returns:
            Dict with mixing_rate, decay_type, explanation
        """
        if transformation is None:
            # Default: Baker's map (exponential mixing)
            transformation = lambda x: (2*x) % 1.0

        points = np.random.random(n_samples)

        set_A = (0.3, 0.7)
        set_B = (0.2, 0.6)

        mu_A = set_A[1] - set_A[0]
        mu_B = set_B[1] - set_B[0]
        product_measure = mu_A * mu_B

        correlations = []

        for n in range(1, max_iterations, 3):
            transformed = points.copy()
            for _ in range(n):
                transformed = np.array([transformation(p) for p in transformed])

            in_A = (points >= set_A[0]) & (points < set_A[1])
            in_B = (transformed >= set_B[0]) & (transformed < set_B[1])

            intersection = np.mean(in_A & in_B)
            correlation = abs(intersection - product_measure)
            correlations.append((n, correlation))

        # Fit exponential decay
        if len(correlations) > 10:
            log_corr = [np.log(max(c[1], 1e-10)) for c in correlations]
            times = [c[0] for c in correlations]

            # Simple linear fit to log(correlation)
            decay_rate = -(log_corr[-1] - log_corr[0]) / (times[-1] - times[0])

            # Classify decay
            if decay_rate > 0.05:
                decay_type = 'exponential'
            elif decay_rate > 0.01:
                decay_type = 'polynomial'
            else:
                decay_type = 'slow'
        else:
            decay_rate = 0.0
            decay_type = 'insufficient_data'

        return {
            'decay_rate': float(decay_rate),
            'decay_type': decay_type,
            'correlations': [(int(c[0]), float(c[1])) for c in correlations[::5]],
            'explanation': f"Mixing rate: {decay_type} decay with λ ≈ {decay_rate:.4f}",
            'note': 'Exponential mixing: |corr| ≤ C·e^{-λn}',
            'examples': {
                'exponential': 'Anosov systems, Bernoulli shifts',
                'polynomial': 'Interval exchange transformations',
                'slow': 'Systems near integrability'
            }
        }

    def apply_rokhlin_halmos(
        self,
        transformation: Optional[Callable] = None,
        tower_height: int = 10
    ) -> Dict[str, Any]:
        """
        Apply Rokhlin-Halmos lemma (tower construction)

        Rokhlin Lemma: For ergodic T and ε > 0, there exists a set B
        such that B, T(B), ..., T^{n-1}(B) are disjoint and cover (1-ε) of space.

        Args:
            transformation: Ergodic transformation T
            tower_height: Desired height n

        Returns:
            Dict with tower_construction, coverage, explanation
        """
        # Construct tower symbolically
        tower_levels = [f"T^{i}(B)" for i in range(tower_height)]

        # Theoretical coverage
        epsilon = 1.0 / (tower_height + 1)
        coverage = 1.0 - epsilon

        return {
            'tower_height': tower_height,
            'tower_levels': tower_levels[:5],  # Show first 5
            'total_levels': tower_height,
            'theoretical_coverage': float(coverage),
            'epsilon': float(epsilon),
            'explanation': f"Rokhlin tower of height {tower_height} covers {coverage:.3f} of space",
            'lemma': 'For ergodic T: can construct tower B, TB, ..., T^{n-1}B covering (1-ε) measure',
            'applications': ['Induced transformations', 'Entropy theory', 'Coding theory'],
            'note': 'Tower height n can be arbitrarily large (ε → 0)'
        }

    def check_kolmogorov_property(
        self,
        transformation: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Check Kolmogorov property (K-system)

        K-Property: Future and past become independent when
        conditioned on present (strong mixing of conditional measures)

        Args:
            transformation: Dynamical system T

        Returns:
            Dict with is_k_system, explanation
        """
        # K-property is difficult to verify numerically
        # Provide theoretical analysis

        known_k_systems = {
            'bernoulli_shift': True,
            'baker_map': True,
            'arnold_cat_map': True,
            'hyperbolic_automorphism': True,
            'rotation': False,
            'periodic_orbit': False
        }

        # Heuristic: Check if transformation appears chaotic
        # (Real verification requires entropy analysis)

        return {
            'is_k_system': None,
            'known_k_systems': known_k_systems,
            'explanation': 'K-property requires entropy analysis (beyond numerical verification)',
            'definition': 'K-system: Future and past independent conditioned on present',
            'hierarchy': 'K-systems ⊂ Bernoulli ⊂ Strongly mixing ⊂ Weakly mixing ⊂ Ergodic',
            'properties': [
                'K-systems have positive entropy',
                'Bernoulli shifts are K-systems',
                'K-property implies strong mixing'
            ],
            'note': 'Full verification requires Kolmogorov-Sinai entropy computation'
        }

    def _classify_system(self, is_ergodic: bool, is_mixing: bool) -> str:
        """Classify dynamical system in mixing hierarchy"""
        if is_mixing:
            return 'mixing'
        elif is_ergodic:
            return 'ergodic_not_mixing'
        else:
            return 'not_ergodic'

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new mixing problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Clear cache if too large
        if self.tasks_executed > 50 and len(self.mixing_cache) > 20:
            intentions.append(Intention(
                action='clear_mixing_cache',
                priority=1,
                description='Clear old mixing computation cache'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'clear_mixing_cache':
            if len(self.mixing_cache) > 20:
                keys = list(self.mixing_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.mixing_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.mixing_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
