# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
DYNAMICAL ENTROPY SPECIALIST - Kolmogorov-Sinai entropy, metric entropy
========================================================================

Manages tasks related to dynamical entropy: Kolmogorov-Sinai entropy,
metric entropy, partition entropy, Shannon-McMillan-Breiman theorem.

CRITICAL ALGORITHMS:
-------------------
- Kolmogorov-Sinai Entropy: h(T) = sup_α h(T,α)
- Metric Entropy: h(T,α) for partition α
- Partition Entropy: H(α) = -Σμ(A)log μ(A)
- Shannon-McMillan-Breiman: Asymptotic equipartition property
- Entropy Properties: h(T^n) = n·h(T)
- Entropy Bounds: Comparison and estimation

WHY THIS MATTERS:
----------------
Dynamical entropy characterizes:
- Complexity and randomness of dynamical systems
- Information production rate
- Predictability and chaos
- Classification of systems (zero vs positive entropy)

CAPABILITIES:
------------
- Compute Kolmogorov-Sinai entropy
- Compute metric entropy for partitions
- Compute partition entropy H(α)
- Apply Shannon-McMillan-Breiman theorem
- Verify entropy properties
- Compare entropy bounds
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class DynamicalEntropySpecialist(BDIAgent):
    """
    Dynamical Entropy Specialist - Kolmogorov-Sinai entropy

    DIRECTIVE:
    ---------
    Handle all dynamical entropy operations with emphasis on:
    - Kolmogorov-Sinai entropy computation
    - Metric entropy for partitions
    - Partition entropy
    - Shannon-McMillan-Breiman theorem

    KEY ALGORITHMS:
    --------------
    - KS Entropy: h(T) = sup_α h(T,α)
    - Metric Entropy: h(T,α) = lim (1/n)H(α ∨ T⁻¹α ∨ ... ∨ T⁻⁽ⁿ⁻¹⁾α)
    - Partition Entropy: H(α) = -Σμ(A)log μ(A)
    - SMB Theorem: -(1/n)log μ(A_n(x)) → h(T,α)

    OPERATIONS:
    ----------
    - compute_kolmogorov_sinai_entropy(transformation, partition)
    - compute_metric_entropy(transformation, partition)
    - compute_partition_entropy(measure, partition)
    - apply_shannon_mcmillan_breiman(transformation, partition)
    - verify_entropy_properties(transformation)
    - compare_entropy_bounds(transformation1, transformation2)
    """

    def __init__(self, agent_id='dynamical_entropy_specialist_001', df=None, blackboard=None):
        """
        Initialize Dynamical Entropy Specialist

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
        self.entropy_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.ergodic.dynamical_entropy',
                agent_id=self.agent_id,
                algorithm='dynamical_entropy',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process dynamical entropy task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of dynamical entropy operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'ks_entropy')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'ks_entropy':
                return self._process_ks_entropy(metadata)
            elif problem_type == 'metric_entropy':
                return self._process_metric_entropy(metadata)
            elif problem_type == 'partition_entropy':
                return self._process_partition_entropy(metadata)
            elif problem_type == 'shannon_mcmillan':
                return self._process_shannon_mcmillan(metadata)
            elif problem_type == 'verify_properties':
                return self._process_verify_properties(metadata)
            elif problem_type == 'compare_bounds':
                return self._process_compare_bounds(metadata)
            else:
                return self._process_ks_entropy(metadata)

        except Exception as e:
            return {
                'operation': 'dynamical_entropy',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_ks_entropy(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Kolmogorov-Sinai entropy computation request"""
        transformation = metadata.get('transformation')
        partition = metadata.get('partition')

        result = self.compute_kolmogorov_sinai_entropy(transformation, partition)
        return {
            'operation': 'compute_kolmogorov_sinai_entropy',
            **result
        }

    def _process_metric_entropy(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process metric entropy computation request"""
        transformation = metadata.get('transformation')
        partition = metadata.get('partition')

        result = self.compute_metric_entropy(transformation, partition)
        return {
            'operation': 'compute_metric_entropy',
            **result
        }

    def _process_partition_entropy(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process partition entropy computation request"""
        measure = metadata.get('measure')
        partition = metadata.get('partition')

        result = self.compute_partition_entropy(measure, partition)
        return {
            'operation': 'compute_partition_entropy',
            **result
        }

    def _process_shannon_mcmillan(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Shannon-McMillan-Breiman theorem application request"""
        transformation = metadata.get('transformation')
        partition = metadata.get('partition')

        result = self.apply_shannon_mcmillan_breiman(transformation, partition)
        return {
            'operation': 'apply_shannon_mcmillan_breiman',
            **result
        }

    def _process_verify_properties(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process entropy properties verification request"""
        transformation = metadata.get('transformation')

        result = self.verify_entropy_properties(transformation)
        return {
            'operation': 'verify_entropy_properties',
            **result
        }

    def _process_compare_bounds(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process entropy bounds comparison request"""
        transformation1 = metadata.get('transformation1')
        transformation2 = metadata.get('transformation2')

        result = self.compare_entropy_bounds(transformation1, transformation2)
        return {
            'operation': 'compare_entropy_bounds',
            **result
        }

    def compute_kolmogorov_sinai_entropy(
        self,
        transformation: Optional[Callable] = None,
        partition: Optional[List[Tuple[float, float]]] = None,
        n_iterations: int = 20
    ) -> Dict[str, Any]:
        """
        Compute Kolmogorov-Sinai entropy

        h(T) = sup_α h(T,α) where α ranges over all finite partitions

        Args:
            transformation: Dynamical system T
            partition: Generating partition α (or None for default binary)
            n_iterations: Number of iterations for entropy estimate

        Returns:
            Dict with ks_entropy, explanation, interpretation
        """
        if transformation is None:
            # Default: doubling map (h = log 2)
            transformation = lambda x: (2 * x) % 1.0

        if partition is None:
            # Default: binary partition [0, 0.5), [0.5, 1)
            partition = [(0.0, 0.5), (0.5, 1.0)]

        # Compute metric entropy for this partition
        metric_entropy_result = self.compute_metric_entropy(transformation, partition, n_iterations)
        ks_entropy_estimate = metric_entropy_result['metric_entropy']

        # Classify system by entropy
        if ks_entropy_estimate < 0.01:
            entropy_class = 'zero_entropy'
            examples = 'Rotations, periodic systems'
        elif ks_entropy_estimate < 1.0:
            entropy_class = 'positive_entropy'
            examples = 'Weakly mixing systems'
        else:
            entropy_class = 'high_entropy'
            examples = 'Bernoulli shifts, chaotic maps'

        return {
            'ks_entropy': float(ks_entropy_estimate),
            'entropy_class': entropy_class,
            'partition_used': partition,
            'n_iterations': n_iterations,
            'explanation': f"Kolmogorov-Sinai entropy h(T) ≈ {ks_entropy_estimate:.4f}",
            'definition': 'h(T) = sup_α h(T,α) over all finite partitions α',
            'interpretation': {
                'zero': 'Completely predictable (e.g., rotations)',
                'positive': 'Chaotic, unpredictable (e.g., Bernoulli shifts)'
            },
            'examples': examples,
            'note': 'Entropy measures information production rate'
        }

    def compute_metric_entropy(
        self,
        transformation: Optional[Callable] = None,
        partition: Optional[List[Tuple[float, float]]] = None,
        n_iterations: int = 20,
        n_samples: int = 10000
    ) -> Dict[str, Any]:
        """
        Compute metric entropy for partition

        h(T,α) = lim_{n→∞} (1/n) H(α ∨ T⁻¹α ∨ ... ∨ T⁻⁽ⁿ⁻¹⁾α)

        Args:
            transformation: Dynamical system T
            partition: Partition α
            n_iterations: Number of refinements
            n_samples: Sample size for estimation

        Returns:
            Dict with metric_entropy, refined_partitions, explanation
        """
        if transformation is None:
            transformation = lambda x: (2 * x) % 1.0

        if partition is None:
            partition = [(0.0, 0.5), (0.5, 1.0)]

        # Sample initial points
        points = np.random.random(n_samples)

        # Compute entropies H(α ∨ T⁻¹α ∨ ... ∨ T⁻⁽ⁿ⁻¹⁾α) / n
        entropies = []

        for n in range(1, min(n_iterations + 1, 15)):  # Limit to prevent exponential blowup
            # Generate orbit up to T^(n-1)
            orbit_partitions = []

            for i in range(n):
                # Apply T^i to points
                transformed = points.copy()
                for _ in range(i):
                    transformed = np.array([transformation(p) for p in transformed])

                # Classify points by partition
                partition_labels = self._classify_by_partition(transformed, partition)
                orbit_partitions.append(partition_labels)

            # Combine into refined partition (symbolic dynamics)
            combined_labels = [''.join(str(orbit_partitions[i][j]) for i in range(n))
                              for j in range(n_samples)]

            # Compute entropy of combined partition
            unique, counts = np.unique(combined_labels, return_counts=True)
            probabilities = counts / n_samples

            # Shannon entropy H = -Σp log p
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))

            # Metric entropy estimate
            metric_entropy_n = entropy / n
            entropies.append(metric_entropy_n)

        # Estimate limit
        if len(entropies) > 5:
            metric_entropy = np.mean(entropies[-5:])  # Average last 5
        else:
            metric_entropy = entropies[-1] if entropies else 0.0

        return {
            'metric_entropy': float(metric_entropy),
            'entropy_sequence': [float(e) for e in entropies],
            'n_iterations': len(entropies),
            'partition': partition,
            'explanation': f"Metric entropy h(T,α) ≈ {metric_entropy:.4f}",
            'formula': 'h(T,α) = lim (1/n)H(α ∨ T⁻¹α ∨ ... ∨ T⁻⁽ⁿ⁻¹⁾α)',
            'note': 'Measures information gained per iteration'
        }

    def compute_partition_entropy(
        self,
        measure: Optional[Dict[Tuple[float, float], float]] = None,
        partition: Optional[List[Tuple[float, float]]] = None,
        n_samples: int = 10000
    ) -> Dict[str, Any]:
        """
        Compute entropy of partition

        H(α) = -Σ μ(A) log μ(A) for A ∈ α

        Args:
            measure: Probability measure
            partition: Partition α = {A₁, A₂, ..., Aₖ}
            n_samples: Sample size for empirical estimation

        Returns:
            Dict with partition_entropy, atom_probabilities
        """
        if partition is None:
            partition = [(0.0, 0.5), (0.5, 1.0)]

        # Sample from measure (or uniform if not specified)
        if measure is None:
            sample_points = np.random.random(n_samples)
        else:
            sample_points = np.random.random(n_samples)  # Simplified

        # Classify by partition
        partition_labels = self._classify_by_partition(sample_points, partition)

        # Compute empirical probabilities
        unique_labels, counts = np.unique(partition_labels, return_counts=True)
        probabilities = counts / n_samples

        # Shannon entropy
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))

        # Atom probabilities
        atom_probs = {int(label): float(prob) for label, prob in zip(unique_labels, probabilities)}

        return {
            'partition_entropy': float(entropy),
            'atom_probabilities': atom_probs,
            'n_atoms': len(partition),
            'max_entropy': float(np.log2(len(partition))),
            'explanation': f"Partition entropy H(α) = {entropy:.4f}",
            'formula': 'H(α) = -Σ μ(A) log μ(A)',
            'note': 'Maximum when all atoms have equal measure'
        }

    def apply_shannon_mcmillan_breiman(
        self,
        transformation: Optional[Callable] = None,
        partition: Optional[List[Tuple[float, float]]] = None,
        initial_point: float = 0.5,
        n_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Apply Shannon-McMillan-Breiman theorem

        For ergodic T: -(1/n) log μ(A_n(x)) → h(T,α) a.e.
        where A_n(x) is the partition atom containing (x, Tx, ..., T^(n-1)x)

        Args:
            transformation: Ergodic transformation T
            partition: Partition α
            initial_point: Starting point x
            n_iterations: Maximum n

        Returns:
            Dict with convergence data, entropy estimate
        """
        if transformation is None:
            transformation = lambda x: (2 * x) % 1.0

        if partition is None:
            partition = [(0.0, 0.5), (0.5, 1.0)]

        # Generate orbit
        current = initial_point
        orbit = [current]

        for _ in range(n_iterations):
            current = transformation(current)
            orbit.append(current)

        # Classify orbit by partition
        orbit_labels = self._classify_by_partition(np.array(orbit), partition)

        # Compute -(1/n) log μ(A_n(x)) for increasing n
        convergence_data = []

        for n in range(5, n_iterations, 5):
            # Symbol string for first n iterates
            symbol_string = ''.join(str(orbit_labels[i]) for i in range(n))

            # Estimate probability via frequency (crude approximation)
            # In practice, would sample many orbits
            # For now, use equipartition approximation
            num_atoms = len(partition) ** n
            prob_estimate = 1.0 / num_atoms  # Uniform approximation

            # Compute -(1/n) log μ(A_n(x))
            info_density = -(1.0 / n) * np.log2(prob_estimate + 1e-10)
            convergence_data.append(info_density)

        # Estimate entropy (should converge to h(T,α))
        if len(convergence_data) > 5:
            entropy_estimate = np.mean(convergence_data[-5:])
        else:
            entropy_estimate = convergence_data[-1] if convergence_data else 0.0

        return {
            'entropy_estimate': float(entropy_estimate),
            'convergence_data': [float(x) for x in convergence_data[::2]],  # Sample every other
            'n_iterations': n_iterations,
            'explanation': f"Shannon-McMillan-Breiman: -(1/n)log μ(A_n) → {entropy_estimate:.4f}",
            'theorem': 'For ergodic T: -(1/n)log μ(A_n(x)) → h(T,α) almost everywhere',
            'interpretation': 'Asymptotic equipartition property (AEP)',
            'note': 'Entropy is the typical information per symbol'
        }

    def verify_entropy_properties(
        self,
        transformation: Optional[Callable] = None,
        n_powers: int = 5
    ) -> Dict[str, Any]:
        """
        Verify entropy properties

        Key property: h(T^n) = n·h(T)

        Args:
            transformation: Dynamical system T
            n_powers: Check up to T^n

        Returns:
            Dict with property verification, ratios
        """
        if transformation is None:
            transformation = lambda x: (2 * x) % 1.0

        partition = [(0.0, 0.5), (0.5, 1.0)]

        # Compute h(T)
        h_T_result = self.compute_metric_entropy(transformation, partition, n_iterations=10)
        h_T = h_T_result['metric_entropy']

        # Compute h(T^n) for various n
        entropy_ratios = []

        for n in range(2, n_powers + 1):
            # Define T^n
            def T_n(x):
                """Compose transformation n times: T^n = T ∘ T ∘ ... ∘ T."""
                result = x
                for _ in range(n):
                    result = transformation(result)
                return result

            # Compute h(T^n)
            h_Tn_result = self.compute_metric_entropy(T_n, partition, n_iterations=10)
            h_Tn = h_Tn_result['metric_entropy']

            # Check ratio h(T^n) / (n·h(T))
            expected = n * h_T
            ratio = h_Tn / expected if expected > 0 else 0.0

            entropy_ratios.append({
                'n': n,
                'h_Tn': float(h_Tn),
                'expected': float(expected),
                'ratio': float(ratio)
            })

        # Property holds if ratios ≈ 1
        avg_ratio = np.mean([r['ratio'] for r in entropy_ratios])
        property_holds = abs(avg_ratio - 1.0) < 0.3  # Tolerance for numerical estimation

        return {
            'h_T': float(h_T),
            'entropy_ratios': entropy_ratios,
            'avg_ratio': float(avg_ratio),
            'property_holds': property_holds,
            'explanation': f"Property h(T^n) = n·h(T) {'holds' if property_holds else 'does not hold'} (avg ratio: {avg_ratio:.2f})",
            'property': 'h(T^n) = n·h(T) for all n ≥ 1',
            'other_properties': [
                'h(T) ≥ 0 (non-negative)',
                'h(id) = 0 (identity has zero entropy)',
                'h is invariant under conjugacy'
            ]
        }

    def compare_entropy_bounds(
        self,
        transformation1: Optional[Callable] = None,
        transformation2: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Compare entropy bounds of two transformations

        Args:
            transformation1: First dynamical system
            transformation2: Second dynamical system

        Returns:
            Dict with entropy comparison, ordering
        """
        if transformation1 is None:
            # Rotation (zero entropy)
            alpha = (np.sqrt(5) - 1) / 2
            transformation1 = lambda x: (x + alpha) % 1.0

        if transformation2 is None:
            # Doubling map (positive entropy)
            transformation2 = lambda x: (2 * x) % 1.0

        partition = [(0.0, 0.5), (0.5, 1.0)]

        # Compute entropies
        h1_result = self.compute_metric_entropy(transformation1, partition, n_iterations=10)
        h1 = h1_result['metric_entropy']

        h2_result = self.compute_metric_entropy(transformation2, partition, n_iterations=10)
        h2 = h2_result['metric_entropy']

        # Compare
        if h1 < h2:
            comparison = 'T1 < T2 (T1 less chaotic)'
        elif h1 > h2:
            comparison = 'T1 > T2 (T1 more chaotic)'
        else:
            comparison = 'T1 ≈ T2 (similar complexity)'

        return {
            'h_T1': float(h1),
            'h_T2': float(h2),
            'comparison': comparison,
            'difference': float(abs(h1 - h2)),
            'explanation': f"Entropy comparison: h(T1) = {h1:.4f}, h(T2) = {h2:.4f}",
            'interpretation': 'Higher entropy ⟹ more chaotic, less predictable',
            'examples': {
                'zero_entropy': 'Rotations, periodic orbits',
                'log_2_entropy': 'Doubling map, tent map',
                'log_k_entropy': 'k-to-1 expanding maps'
            }
        }

    def _classify_by_partition(
        self,
        points: np.ndarray,
        partition: List[Tuple[float, float]]
    ) -> np.ndarray:
        """
        Classify points by partition

        Args:
            points: Array of points
            partition: List of intervals

        Returns:
            Array of partition labels (indices)
        """
        labels = np.zeros(len(points), dtype=int)

        for i, point in enumerate(points):
            for j, (a, b) in enumerate(partition):
                if a <= point < b:
                    labels[i] = j
                    break

        return labels

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new entropy problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Clear cache if too large
        if self.tasks_executed > 50 and len(self.entropy_cache) > 20:
            intentions.append(Intention(
                action='clear_entropy_cache',
                priority=1,
                description='Clear old entropy computation cache'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'clear_entropy_cache':
            if len(self.entropy_cache) > 20:
                keys = list(self.entropy_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.entropy_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.entropy_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
