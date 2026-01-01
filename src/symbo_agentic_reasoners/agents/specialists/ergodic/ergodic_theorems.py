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
ERGODIC THEOREMS SPECIALIST - Birkhoff, von Neumann, Mean Ergodic Theorem
==========================================================================

Manages tasks related to ergodic theorems: Birkhoff pointwise theorem,
von Neumann L² theorem, mean ergodic theorem, and maximal ergodic theorem.

CRITICAL ALGORITHMS:
-------------------
- Birkhoff Ergodic Theorem: Pointwise convergence (1/n)Σf(T^i x) → ∫f dμ
- von Neumann Ergodic Theorem: L² convergence of time averages
- Mean Ergodic Theorem: Convergence in mean
- Time Average: Compute (1/n)Σf(T^i x)
- Space Average: Compute ∫f dμ
- Maximal Ergodic Theorem: Maximal inequality
- Convergence Verification: Test pointwise/L²/mean convergence

WHY THIS MATTERS:
----------------
Ergodic theorems are fundamental to:
- Statistical mechanics (time average = space average)
- Probability theory on dynamical systems
- Foundations of ergodic theory
- Justification for Monte Carlo methods
- Long-term behavior analysis

CAPABILITIES:
------------
- Apply Birkhoff ergodic theorem (pointwise)
- Apply von Neumann theorem (L² convergence)
- Compute time averages along orbits
- Compute space averages with respect to measure
- Verify convergence (pointwise/L²/mean)
- Apply maximal ergodic theorem
- Mean ergodic theorem applications
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class ErgodicTheoremSpecialist(BDIAgent):
    """
    Ergodic Theorems Specialist - Birkhoff, von Neumann theorems

    DIRECTIVE:
    ---------
    Handle all ergodic theorem operations with emphasis on:
    - Birkhoff theorem (pointwise convergence)
    - von Neumann theorem (L² convergence)
    - Time vs space averages
    - Convergence verification

    KEY ALGORITHMS:
    --------------
    - Birkhoff: lim (1/n)Σf(T^i x) = ∫f dμ (a.e.)
    - von Neumann: L² convergence of Cesaro averages
    - Mean Ergodic: Convergence in L¹
    - Maximal: sup_n (1/n)Σf(T^i x) control

    OPERATIONS:
    ----------
    - apply_birkhoff_ergodic_theorem(transformation, function, initial_point)
    - apply_von_neumann_ergodic_theorem(transformation, function)
    - verify_pointwise_convergence(trajectory, time_average, space_average)
    - apply_mean_ergodic_theorem(transformation, function)
    - compute_time_average(trajectory, function)
    - compute_space_average(measure, function)
    - maximal_ergodic_theorem(transformation, function)
    """

    def __init__(self, agent_id='ergodic_theorems_specialist_001', df=None, blackboard=None):
        """
        Initialize Ergodic Theorems Specialist

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
        self.computation_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.ergodic.ergodic_theorems',
                agent_id=self.agent_id,
                algorithm='ergodic_theorems',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process ergodic theorems task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of ergodic theorems operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'birkhoff')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'birkhoff':
                return self._process_birkhoff(metadata)
            elif problem_type == 'von_neumann':
                return self._process_von_neumann(metadata)
            elif problem_type == 'verify_convergence':
                return self._process_verify_convergence(metadata)
            elif problem_type == 'mean_ergodic':
                return self._process_mean_ergodic(metadata)
            elif problem_type == 'time_average':
                return self._process_time_average(metadata)
            elif problem_type == 'space_average':
                return self._process_space_average(metadata)
            elif problem_type == 'maximal':
                return self._process_maximal(metadata)
            else:
                return self._process_birkhoff(metadata)

        except Exception as e:
            return {
                'operation': 'ergodic_theorems',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_birkhoff(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Birkhoff ergodic theorem application request"""
        transformation = metadata.get('transformation')
        function = metadata.get('function')
        initial_point = metadata.get('initial_point', 0.5)

        result = self.apply_birkhoff_ergodic_theorem(transformation, function, initial_point)
        return {
            'operation': 'apply_birkhoff_ergodic_theorem',
            **result
        }

    def _process_von_neumann(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process von Neumann ergodic theorem application request"""
        transformation = metadata.get('transformation')
        function = metadata.get('function')

        result = self.apply_von_neumann_ergodic_theorem(transformation, function)
        return {
            'operation': 'apply_von_neumann_ergodic_theorem',
            **result
        }

    def _process_verify_convergence(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process convergence verification request"""
        trajectory = metadata.get('trajectory')
        time_average = metadata.get('time_average')
        space_average = metadata.get('space_average')

        result = self.verify_pointwise_convergence(trajectory, time_average, space_average)
        return {
            'operation': 'verify_pointwise_convergence',
            **result
        }

    def _process_mean_ergodic(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process mean ergodic theorem application request"""
        transformation = metadata.get('transformation')
        function = metadata.get('function')

        result = self.apply_mean_ergodic_theorem(transformation, function)
        return {
            'operation': 'apply_mean_ergodic_theorem',
            **result
        }

    def _process_time_average(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process time average computation request"""
        trajectory = metadata.get('trajectory')
        function = metadata.get('function')

        result = self.compute_time_average(trajectory, function)
        return {
            'operation': 'compute_time_average',
            **result
        }

    def _process_space_average(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process space average computation request"""
        measure = metadata.get('measure')
        function = metadata.get('function')

        result = self.compute_space_average(measure, function)
        return {
            'operation': 'compute_space_average',
            **result
        }

    def _process_maximal(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process maximal ergodic theorem application request"""
        transformation = metadata.get('transformation')
        function = metadata.get('function')

        result = self.maximal_ergodic_theorem(transformation, function)
        return {
            'operation': 'maximal_ergodic_theorem',
            **result
        }

    def apply_birkhoff_ergodic_theorem(
        self,
        transformation: Optional[Callable] = None,
        function: Optional[Callable] = None,
        initial_point: float = 0.5,
        n_iterations: int = 10000
    ) -> Dict[str, Any]:
        """
        Apply Birkhoff ergodic theorem

        For ergodic transformation T and integrable f:
        lim_{n→∞} (1/n) Σ_{i=0}^{n-1} f(T^i(x)) = ∫f dμ  (almost everywhere)

        Args:
            transformation: Dynamical system T
            function: Observable function f
            initial_point: Starting point x
            n_iterations: Number of iterations

        Returns:
            Dict with time_average, space_average (estimated), convergence info
        """
        if transformation is None:
            # Default: doubling map (ergodic w.r.t. Lebesgue)
            transformation = lambda x: (2 * x) % 1.0

        if function is None:
            # Default: characteristic function of [0, 0.5)
            function = lambda x: 1.0 if x < 0.5 else 0.0

        # Simulate trajectory
        trajectory = [initial_point]
        current = initial_point

        for _ in range(n_iterations):
            current = transformation(current)
            trajectory.append(current)

        # Compute time average
        function_values = [function(point) for point in trajectory]
        time_average = sum(function_values) / len(function_values)

        # Estimate space average (via sampling or known measure)
        # For Lebesgue measure on [0,1), estimate by averaging over many initial points
        n_samples = 1000
        sample_points = np.random.random(n_samples)
        space_average = sum(function(p) for p in sample_points) / n_samples

        # Check convergence by windowing
        window_size = n_iterations // 10
        convergence_history = []

        for i in range(10):
            start = i * window_size
            end = start + window_size
            if end <= len(function_values):
                window_avg = sum(function_values[start:end]) / window_size
                convergence_history.append(window_avg)

        # Compute convergence error
        recent_avg = sum(function_values[-window_size:]) / window_size
        convergence_error = abs(recent_avg - space_average)

        return {
            'time_average': float(time_average),
            'space_average': float(space_average),
            'convergence_error': float(convergence_error),
            'n_iterations': n_iterations,
            'convergence_history': [float(x) for x in convergence_history],
            'explanation': f"Time average {time_average:.4f} converges to space average {space_average:.4f}",
            'theorem': 'Birkhoff: (1/n)Σf(T^i x) → ∫f dμ almost everywhere',
            'note': 'Pointwise convergence for almost every initial point'
        }

    def apply_von_neumann_ergodic_theorem(
        self,
        transformation: Optional[Callable] = None,
        function: Optional[Callable] = None,
        n_initial_points: int = 100,
        n_iterations: int = 1000
    ) -> Dict[str, Any]:
        """
        Apply von Neumann ergodic theorem (L² convergence)

        For ergodic T and f ∈ L²(μ):
        ||(1/n)Σ_{i=0}^{n-1} f∘T^i - ∫f dμ||_{L²} → 0

        Args:
            transformation: Dynamical system T
            function: Observable function f ∈ L²
            n_initial_points: Number of initial points for L² norm
            n_iterations: Number of iterations per point

        Returns:
            Dict with L2_error, convergence info, explanation
        """
        if transformation is None:
            transformation = lambda x: (2 * x) % 1.0

        if function is None:
            function = lambda x: 1.0 if x < 0.5 else 0.0

        # Sample initial points
        initial_points = np.random.random(n_initial_points)

        # Compute time averages for each initial point
        time_averages = []

        for x0 in initial_points:
            current = x0
            trajectory = [current]

            for _ in range(n_iterations):
                current = transformation(current)
                trajectory.append(current)

            function_values = [function(p) for p in trajectory]
            time_avg = sum(function_values) / len(function_values)
            time_averages.append(time_avg)

        time_averages = np.array(time_averages)

        # Estimate space average
        space_average = np.mean(time_averages)

        # Compute L² error
        l2_error = np.sqrt(np.mean((time_averages - space_average) ** 2))

        # Variance (should decrease as n → ∞)
        variance = np.var(time_averages)

        return {
            'l2_error': float(l2_error),
            'variance': float(variance),
            'space_average': float(space_average),
            'n_initial_points': n_initial_points,
            'n_iterations': n_iterations,
            'explanation': f"L² error {l2_error:.4f} measures convergence in mean square",
            'theorem': 'von Neumann: (1/n)Σf∘T^i converges to ∫f dμ in L²(μ)',
            'note': 'Stronger than pointwise (Birkhoff), weaker than uniform convergence'
        }

    def verify_pointwise_convergence(
        self,
        trajectory: Optional[List[float]] = None,
        time_average: Optional[float] = None,
        space_average: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Verify pointwise convergence of time average to space average

        Args:
            trajectory: Orbit points
            time_average: Computed time average
            space_average: Theoretical space average

        Returns:
            Dict with convergence verification, error bounds
        """
        if trajectory is None:
            # Generate sample trajectory
            transformation = lambda x: (2 * x) % 1.0
            function = lambda x: x

            current = 0.5
            trajectory = [current]
            for _ in range(1000):
                current = transformation(current)
                trajectory.append(current)

            # Compute averages
            time_average = sum(trajectory) / len(trajectory)
            space_average = 0.5  # ∫x dx over [0,1]

        if time_average is None or space_average is None:
            # Compute from trajectory
            time_average = sum(trajectory) / len(trajectory)
            space_average = 0.5  # Default for uniform on [0,1]

        # Check convergence
        convergence_error = abs(time_average - space_average)

        # Compute running averages to show convergence
        n = len(trajectory)
        running_averages = []
        cumsum = 0.0

        for i, val in enumerate(trajectory, 1):
            cumsum += val
            if i % (n // 10) == 0:  # Sample 10 points
                running_averages.append(cumsum / i)

        # Check if converging
        is_converging = len(running_averages) > 1 and \
                       abs(running_averages[-1] - space_average) < abs(running_averages[0] - space_average)

        return {
            'time_average': float(time_average),
            'space_average': float(space_average),
            'convergence_error': float(convergence_error),
            'is_converging': is_converging,
            'running_averages': [float(x) for x in running_averages],
            'n_points': len(trajectory),
            'explanation': f"Time average converges to space average (error: {convergence_error:.4f})",
            'convergence_criterion': 'lim_{n→∞} |(1/n)Σf(T^i x) - ∫f dμ| = 0'
        }

    def apply_mean_ergodic_theorem(
        self,
        transformation: Optional[Callable] = None,
        function: Optional[Callable] = None,
        n_samples: int = 1000,
        n_iterations: int = 500
    ) -> Dict[str, Any]:
        """
        Apply mean ergodic theorem (convergence in L¹)

        For ergodic T and f ∈ L¹(μ):
        ∫|(1/n)Σf∘T^i - ∫f dμ| dμ → 0

        Args:
            transformation: Dynamical system T
            function: Observable function f ∈ L¹
            n_samples: Number of sample points
            n_iterations: Number of iterations

        Returns:
            Dict with L1_error, convergence info
        """
        if transformation is None:
            transformation = lambda x: (2 * x) % 1.0

        if function is None:
            function = lambda x: np.sin(2 * np.pi * x)

        # Sample initial points
        initial_points = np.random.random(n_samples)

        # Compute time averages
        time_averages = []

        for x0 in initial_points:
            current = x0
            function_sum = 0.0

            for i in range(n_iterations):
                current = transformation(current)
                function_sum += function(current)

            time_avg = function_sum / n_iterations
            time_averages.append(time_avg)

        time_averages = np.array(time_averages)

        # Estimate space average
        space_average_samples = [function(p) for p in np.random.random(n_samples)]
        space_average = np.mean(space_average_samples)

        # Compute L¹ error (mean absolute deviation)
        l1_error = np.mean(np.abs(time_averages - space_average))

        return {
            'l1_error': float(l1_error),
            'space_average': float(space_average),
            'mean_time_average': float(np.mean(time_averages)),
            'n_samples': n_samples,
            'n_iterations': n_iterations,
            'explanation': f"L¹ error {l1_error:.4f} measures convergence in mean",
            'theorem': 'Mean Ergodic: ∫|(1/n)Σf∘T^i - ∫f dμ| dμ → 0',
            'hierarchy': 'L¹ convergence ⟸ L² convergence (von Neumann)'
        }

    def compute_time_average(
        self,
        trajectory: Optional[List[float]] = None,
        function: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Compute time average along trajectory

        Time average: (1/n) Σ_{i=0}^{n-1} f(x_i)

        Args:
            trajectory: Sequence of orbit points
            function: Observable function f

        Returns:
            Dict with time_average, computation details
        """
        if trajectory is None:
            # Generate sample trajectory
            transformation = lambda x: (2 * x) % 1.0
            current = 0.5
            trajectory = [current]
            for _ in range(1000):
                current = transformation(current)
                trajectory.append(current)

        if function is None:
            # Default: identity function
            function = lambda x: x

        # Compute time average
        function_values = [function(point) for point in trajectory]
        time_average = sum(function_values) / len(function_values)

        # Compute standard error
        variance = np.var(function_values)
        std_error = np.sqrt(variance / len(function_values))

        # Compute running average for convergence visualization
        running_avg = []
        cumsum = 0.0
        for i, val in enumerate(function_values, 1):
            cumsum += val
            if i % (len(function_values) // 10) == 0:
                running_avg.append(cumsum / i)

        return {
            'time_average': float(time_average),
            'std_error': float(std_error),
            'n_points': len(trajectory),
            'running_average': [float(x) for x in running_avg],
            'min_value': float(min(function_values)),
            'max_value': float(max(function_values)),
            'explanation': f"Time average: (1/{len(trajectory)})Σf(x_i) = {time_average:.4f}",
            'formula': '(1/n)Σ_{i=0}^{n-1} f(T^i(x))'
        }

    def compute_space_average(
        self,
        measure: Optional[Dict] = None,
        function: Optional[Callable] = None,
        n_samples: int = 10000
    ) -> Dict[str, Any]:
        """
        Compute space average with respect to measure

        Space average: ∫f(x) dμ(x)

        Args:
            measure: Probability measure (or None for Lebesgue)
            function: Observable function f
            n_samples: Number of samples for Monte Carlo integration

        Returns:
            Dict with space_average, estimation details
        """
        if function is None:
            function = lambda x: x

        # Sample according to measure
        if measure is None:
            # Lebesgue measure on [0,1)
            sample_points = np.random.random(n_samples)
        else:
            # Custom measure (simplified - assume uniform on intervals)
            sample_points = np.random.random(n_samples)

        # Compute average
        function_values = [function(p) for p in sample_points]
        space_average = sum(function_values) / len(function_values)

        # Estimate error (Monte Carlo)
        variance = np.var(function_values)
        monte_carlo_error = np.sqrt(variance / n_samples)

        return {
            'space_average': float(space_average),
            'monte_carlo_error': float(monte_carlo_error),
            'n_samples': n_samples,
            'confidence_interval': (
                float(space_average - 2 * monte_carlo_error),
                float(space_average + 2 * monte_carlo_error)
            ),
            'explanation': f"Space average: ∫f dμ ≈ {space_average:.4f} ± {monte_carlo_error:.4f}",
            'formula': '∫f(x) dμ(x)',
            'method': 'Monte Carlo integration'
        }

    def maximal_ergodic_theorem(
        self,
        transformation: Optional[Callable] = None,
        function: Optional[Callable] = None,
        initial_point: float = 0.5,
        n_iterations: int = 1000
    ) -> Dict[str, Any]:
        """
        Apply maximal ergodic theorem

        Maximal Ergodic Theorem: Control of maximal function
        M_n f(x) = max_{1≤k≤n} (1/k)Σ_{i=0}^{k-1} f(T^i(x))

        Args:
            transformation: Dynamical system T
            function: Observable function f
            initial_point: Starting point
            n_iterations: Number of iterations

        Returns:
            Dict with maximal_function, bounds, explanation
        """
        if transformation is None:
            transformation = lambda x: (2 * x) % 1.0

        if function is None:
            function = lambda x: x - 0.5  # Mean zero function

        # Generate trajectory
        current = initial_point
        trajectory = [current]

        for _ in range(n_iterations):
            current = transformation(current)
            trajectory.append(current)

        # Compute maximal function
        function_values = [function(p) for p in trajectory]

        maximal_values = []
        cumsum = 0.0

        for k in range(1, len(function_values) + 1):
            cumsum += function_values[k - 1]
            avg_k = cumsum / k

            if k == 1:
                max_so_far = avg_k
            else:
                max_so_far = max(max_so_far, avg_k)

            if k % 100 == 0:
                maximal_values.append(max_so_far)

        max_value = max(maximal_values) if maximal_values else 0.0

        # Theoretical bound (simplified)
        space_average = sum(function_values) / len(function_values)

        return {
            'maximal_value': float(max_value),
            'space_average': float(space_average),
            'maximal_function_samples': [float(x) for x in maximal_values],
            'n_iterations': n_iterations,
            'explanation': f"Maximal function M_n f(x) = {max_value:.4f}",
            'theorem': 'Maximal Ergodic: Controls sup_n (1/n)Σf(T^i x)',
            'inequality': 'μ({x: M_n f(x) > λ}) ≤ (1/λ)∫_{M_n f > λ} f dμ',
            'note': 'Key tool in proving Birkhoff ergodic theorem'
        }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new ergodic theorem problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Clear cache if too large
        if self.tasks_executed > 50 and len(self.computation_cache) > 20:
            intentions.append(Intention(
                action='clear_computation_cache',
                priority=1,
                description='Clear old computation cache'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'clear_computation_cache':
            if len(self.computation_cache) > 20:
                keys = list(self.computation_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.computation_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.computation_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
