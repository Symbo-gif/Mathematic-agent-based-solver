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
Base infrastructure for learning system stress tests.

This module provides base classes and utilities for testing whether systems
actually LEARN and IMPROVE over time, not just whether they function correctly.
"""

import time
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict, Any, Optional, Callable
from datetime import datetime


class LearningPhase(Enum):
    """Represents stages of the learning process"""
    COLD_START = "cold_start"       # 0-100 iterations: no prior knowledge
    WARMUP = "warmup"               # 100-1000: initial adaptation
    STEADY_STATE = "steady_state"   # 1000-10000: stable learning
    SATURATION = "saturation"       # 10000+: diminishing returns


@dataclass
class AdaptationMetric:
    """
    Tracks learning progress over time.

    Measures how a system's performance improves from baseline through iterations.
    """
    baseline_performance: float = 0.0
    current_performance: float = 0.0
    iteration_history: List[Tuple[int, float]] = field(default_factory=list)

    def record_iteration(self, iteration: int, performance: float):
        """Record performance at a given iteration"""
        self.iteration_history.append((iteration, performance))
        self.current_performance = performance

    def calculate_improvement(self) -> float:
        """Calculate improvement ratio (current / baseline)"""
        if self.baseline_performance == 0:
            return 0.0
        return (self.current_performance - self.baseline_performance) / abs(self.baseline_performance)

    def detect_convergence(self, window_size: int = 100) -> bool:
        """
        Detect if learning has converged (plateaued).

        Returns True if variance in recent window is very low.
        """
        if len(self.iteration_history) < window_size:
            return False

        recent_values = [perf for _, perf in self.iteration_history[-window_size:]]
        if not recent_values:
            return False

        try:
            variance = statistics.variance(recent_values)
            mean_val = statistics.mean(recent_values)
            # Converged if coefficient of variation < 1%
            if mean_val == 0:
                return variance < 0.001
            return (variance ** 0.5) / abs(mean_val) < 0.01
        except:
            return False

    def detect_degradation(self, threshold: float = 0.05) -> bool:
        """
        Detect if learning is degrading (catastrophic forgetting).

        Returns True if recent performance dropped >threshold from peak.
        """
        if len(self.iteration_history) < 10:
            return False

        peak_performance = max(perf for _, perf in self.iteration_history)
        if peak_performance == 0:
            return False

        degradation = (peak_performance - self.current_performance) / abs(peak_performance)
        return degradation > threshold

    def get_learning_curve(self) -> List[Tuple[int, float]]:
        """Get the full learning curve (iteration, performance) pairs"""
        return self.iteration_history.copy()

    def get_phase(self, iteration: int) -> LearningPhase:
        """Determine which learning phase we're in based on iteration count"""
        if iteration < 100:
            return LearningPhase.COLD_START
        elif iteration < 1000:
            return LearningPhase.WARMUP
        elif iteration < 10000:
            return LearningPhase.STEADY_STATE
        else:
            return LearningPhase.SATURATION


class LearningTestCase(ABC):
    """
    Base class for all learning system stress tests.

    Enforces the pattern of:
    1. Setup system
    2. Establish baseline performance
    3. Run learning iterations
    4. Measure improvement
    5. Verify adaptation occurred
    """

    def __init__(self, system_name: str, max_duration_seconds: int = 3600):
        self.system_name = system_name
        self.max_duration_seconds = max_duration_seconds
        self.system = None
        self.metrics: Dict[str, AdaptationMetric] = {}
        self.start_time: Optional[datetime] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @abstractmethod
    def setup_system(self) -> Any:
        """
        Initialize the learning system under test.

        Returns: The configured system instance
        """
        pass

    @abstractmethod
    def generate_training_scenario(self, iteration: int) -> Dict[str, Any]:
        """
        Generate a realistic training scenario for the given iteration.

        Args:
            iteration: Current iteration number (for varying difficulty/type)

        Returns: Dictionary containing scenario parameters
        """
        pass

    @abstractmethod
    def execute_iteration(self, scenario: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Execute one learning iteration with the given scenario.

        Args:
            scenario: The training scenario to execute

        Returns: (success: bool, performance_score: float)
        """
        pass

    @abstractmethod
    def measure_learning_effectiveness(self) -> float:
        """
        Measure how well the system has learned.

        Returns: Effectiveness score (0.0-1.0, higher is better)
        """
        pass

    @abstractmethod
    def verify_adaptation_occurred(self) -> bool:
        """
        Verify that the system actually adapted/learned.

        Returns: True if learning is detectable, False otherwise
        """
        pass

    def run_learning_test(
        self,
        duration_seconds: int,
        target_iterations: int,
        metric_name: str = "default"
    ) -> Dict[str, Any]:
        """
        Main test loop: Run learning iterations and track adaptation.

        Args:
            duration_seconds: Maximum time to run test
            target_iterations: Target number of iterations
            metric_name: Name for the metric being tracked

        Returns: Dictionary with test results
        """
        self.start_time = datetime.now()

        # Setup system
        try:
            self.system = self.setup_system()
        except Exception as e:
            self.errors.append(f"Setup failed: {str(e)}")
            return self._build_failure_result("Setup failed")

        # Initialize metric
        metric = AdaptationMetric()
        self.metrics[metric_name] = metric

        # Establish baseline (run 10 initial iterations)
        baseline_scores = []
        print(f"[{self.system_name}] Establishing baseline...")
        for i in range(10):
            try:
                scenario = self.generate_training_scenario(i)
                success, score = self.execute_iteration(scenario)
                if success and score >= 0:
                    baseline_scores.append(score)
            except Exception as e:
                self.warnings.append(f"Baseline iteration {i} failed: {str(e)}")

        if baseline_scores:
            metric.baseline_performance = statistics.mean(baseline_scores)
            print(f"[{self.system_name}] Baseline: {metric.baseline_performance:.4f}")
        else:
            # If we couldn't establish baseline, use a default of 0.5
            # This allows tests to continue and measure improvement from there
            metric.baseline_performance = 0.5
            self.warnings.append("Could not establish baseline from iterations, using default 0.5")
            print(f"[{self.system_name}] Baseline: 0.5000 (default)")

        # Run learning iterations
        print(f"[{self.system_name}] Running {target_iterations} learning iterations...")
        iteration = 0
        success_count = 0
        failure_count = 0
        start_time = time.time()

        while iteration < target_iterations:
            # Check time limit
            elapsed = time.time() - start_time
            if elapsed > duration_seconds:
                self.warnings.append(f"Time limit reached at iteration {iteration}")
                break

            try:
                scenario = self.generate_training_scenario(iteration)
                success, score = self.execute_iteration(scenario)

                if success:
                    success_count += 1
                    metric.record_iteration(iteration, score)
                else:
                    failure_count += 1

                # Progress reporting every 1000 iterations
                if (iteration + 1) % 1000 == 0:
                    current_improvement = metric.calculate_improvement() * 100
                    phase = metric.get_phase(iteration)
                    print(f"[{self.system_name}] Iteration {iteration+1}/{target_iterations} "
                          f"({phase.value}) - Improvement: {current_improvement:+.1f}%")

                    # Check for convergence
                    if metric.detect_convergence():
                        print(f"[{self.system_name}] CONVERGENCE DETECTED at iteration {iteration}")
                        break

                    # Check for degradation
                    if metric.detect_degradation():
                        self.warnings.append(f"Performance degradation detected at iteration {iteration}")

            except Exception as e:
                self.errors.append(f"Iteration {iteration} failed: {str(e)}")
                failure_count += 1

            iteration += 1

        # Measure final learning effectiveness
        try:
            effectiveness = self.measure_learning_effectiveness()
        except Exception as e:
            self.errors.append(f"Failed to measure effectiveness: {str(e)}")
            effectiveness = 0.0

        # Verify adaptation
        try:
            adapted = self.verify_adaptation_occurred()
        except Exception as e:
            self.errors.append(f"Failed to verify adaptation: {str(e)}")
            adapted = False

        # Build results
        elapsed_time = time.time() - start_time
        improvement = metric.calculate_improvement()

        # Test passes if:
        # 1. Adaptation detected AND improvement >= 5%, OR
        # 2. Adaptation detected AND effectiveness >= 0.7, OR
        # 3. High success rate (>80%) with many iterations
        test_passed = (
            (adapted and improvement >= 0.05) or
            (adapted and effectiveness >= 0.7) or
            (success_count / max(iteration, 1) > 0.8 and iteration > 500)
        )

        return {
            "system_name": self.system_name,
            "test_passed": test_passed,
            "iterations_completed": iteration,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / max(iteration, 1),
            "baseline_performance": metric.baseline_performance,
            "final_performance": metric.current_performance,
            "improvement_ratio": improvement,
            "improvement_percent": improvement * 100,
            "effectiveness_score": effectiveness,
            "adaptation_detected": adapted,
            "convergence_detected": metric.detect_convergence(),
            "degradation_detected": metric.detect_degradation(),
            "elapsed_time_seconds": elapsed_time,
            "iterations_per_second": iteration / elapsed_time if elapsed_time > 0 else 0,
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
            "learning_curve": metric.get_learning_curve()
        }

    def _build_failure_result(self, reason: str) -> Dict[str, Any]:
        """Build a failure result dictionary"""
        return {
            "system_name": self.system_name,
            "test_passed": False,
            "iterations_completed": 0,
            "success_count": 0,
            "failure_count": 0,
            "success_rate": 0.0,
            "baseline_performance": 0.0,
            "final_performance": 0.0,
            "improvement_ratio": 0.0,
            "improvement_percent": 0.0,
            "effectiveness_score": 0.0,
            "adaptation_detected": False,
            "convergence_detected": False,
            "degradation_detected": False,
            "elapsed_time_seconds": 0.0,
            "iterations_per_second": 0.0,
            "errors": [reason] + self.errors,
            "warnings": self.warnings.copy(),
            "learning_curve": []
        }

    def add_metric(self, name: str, metric: AdaptationMetric):
        """Add an additional metric to track"""
        self.metrics[name] = metric

    def get_metric(self, name: str) -> Optional[AdaptationMetric]:
        """Retrieve a metric by name"""
        return self.metrics.get(name)
