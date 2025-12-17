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
Metric Space Specialist
========================

Provides comprehensive metric space operations:
- Metric verification
- Open/closed set analysis
- Completeness and compactness
- Continuity verification
- Fixed point theorems
- Convergence analysis

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum


class TopologyType(Enum):
    """Types of topological properties."""
    OPEN = "open"
    CLOSED = "closed"
    COMPACT = "compact"
    CONNECTED = "connected"
    COMPLETE = "complete"


@dataclass
class MetricResult:
    """Result from metric analysis."""
    is_metric: bool
    properties: List[str] = field(default_factory=list)
    counterexample: Optional[Dict[str, Any]] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FixedPointResult:
    """Result from fixed point computation."""
    fixed_point: Optional[float]
    iterations: int = 0
    converged: bool = True
    contraction_constant: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContinuityResult:
    """Result from continuity analysis."""
    is_continuous: bool
    continuity_type: str = "pointwise"  # pointwise, uniform, lipschitz
    modulus: Optional[Callable[[float], float]] = None
    lipschitz_constant: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


class MetricSpaceSpecialist:
    """
    BDI Agent for metric space analysis.

    Capabilities:
    - Verify metric axioms
    - Analyze completeness
    - Check compactness
    - Continuity verification
    - Fixed point theorems
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._epsilon = 1e-10

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "metric" in self.beliefs:
            self.desires.append("verify_metric")
        if "function" in self.beliefs and "domain" in self.beliefs:
            self.desires.append("analyze_continuity")
        if "contraction" in self.beliefs:
            self.desires.append("find_fixed_point")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "verify_metric":
            d = self.beliefs.get("metric")
            samples = self.beliefs.get("samples", [])
            return {"result": self.verify_metric(d, samples)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Metric Verification ==========

    def verify_metric(
        self,
        d: Callable[[Any, Any], float],
        samples: List[Any]
    ) -> MetricResult:
        """
        Verify that d is a metric.

        Axioms:
        1. d(x, y) >= 0 (non-negativity)
        2. d(x, y) = 0 iff x = y (identity of indiscernibles)
        3. d(x, y) = d(y, x) (symmetry)
        4. d(x, z) <= d(x, y) + d(y, z) (triangle inequality)

        Args:
            d: Proposed metric function
            samples: Sample points to test

        Returns:
            MetricResult
        """
        properties = []
        counterexample = None

        # Test non-negativity
        nonneg = True
        for x in samples:
            for y in samples:
                if d(x, y) < -self._epsilon:
                    nonneg = False
                    counterexample = {"axiom": "non-negativity", "x": x, "y": y, "d(x,y)": d(x, y)}
                    break

        if nonneg:
            properties.append("non-negative")

        # Test identity
        identity = True
        for x in samples:
            if abs(d(x, x)) > self._epsilon:
                identity = False
                counterexample = counterexample or {"axiom": "identity", "x": x, "d(x,x)": d(x, x)}
                break

        if identity:
            properties.append("identity")

        # Test symmetry
        symmetric = True
        for x in samples:
            for y in samples:
                if abs(d(x, y) - d(y, x)) > self._epsilon:
                    symmetric = False
                    counterexample = counterexample or {"axiom": "symmetry", "x": x, "y": y}
                    break

        if symmetric:
            properties.append("symmetric")

        # Test triangle inequality
        triangle = True
        for x in samples:
            for y in samples:
                for z in samples:
                    if d(x, z) > d(x, y) + d(y, z) + self._epsilon:
                        triangle = False
                        counterexample = counterexample or {
                            "axiom": "triangle",
                            "x": x, "y": y, "z": z,
                            "d(x,z)": d(x, z),
                            "d(x,y)+d(y,z)": d(x, y) + d(y, z)
                        }
                        break

        if triangle:
            properties.append("triangle_inequality")

        is_metric = len(properties) == 4

        return MetricResult(
            is_metric=is_metric,
            properties=properties,
            counterexample=counterexample
        )

    # ========== Common Metrics ==========

    @staticmethod
    def euclidean_metric(x: np.ndarray, y: np.ndarray) -> float:
        """Euclidean metric d(x,y) = ||x - y||_2."""
        return np.linalg.norm(np.array(x) - np.array(y))

    @staticmethod
    def manhattan_metric(x: np.ndarray, y: np.ndarray) -> float:
        """Manhattan/taxicab metric d(x,y) = ||x - y||_1."""
        return np.sum(np.abs(np.array(x) - np.array(y)))

    @staticmethod
    def chebyshev_metric(x: np.ndarray, y: np.ndarray) -> float:
        """Chebyshev metric d(x,y) = ||x - y||_inf."""
        return np.max(np.abs(np.array(x) - np.array(y)))

    @staticmethod
    def discrete_metric(x: Any, y: Any) -> float:
        """Discrete metric: 0 if equal, 1 otherwise."""
        return 0.0 if x == y else 1.0

    @staticmethod
    def lp_metric(x: np.ndarray, y: np.ndarray, p: float) -> float:
        """Lp metric d(x,y) = ||x - y||_p."""
        return np.sum(np.abs(np.array(x) - np.array(y)) ** p) ** (1/p)

    # ========== Topological Properties ==========

    def is_open(
        self,
        set_indicator: Callable[[float], bool],
        d: Callable[[float, float], float],
        samples: List[float],
        epsilon: float = 0.01
    ) -> Dict[str, Any]:
        """
        Check if a set is open.

        A set U is open if for every x in U, there exists epsilon > 0
        such that B(x, epsilon) subset U.

        Args:
            set_indicator: Returns True if point is in set
            d: Metric function
            samples: Sample points
            epsilon: Ball radius to test

        Returns:
            Dictionary with openness analysis
        """
        points_in_set = [x for x in samples if set_indicator(x)]
        boundary_points = []

        for x in points_in_set:
            # Check if epsilon-ball is contained in set
            is_interior = True
            for y in samples:
                if d(x, y) < epsilon and not set_indicator(y):
                    is_interior = False
                    boundary_points.append(x)
                    break

        is_open = len(boundary_points) == 0

        return {
            "is_open": is_open,
            "points_in_set": len(points_in_set),
            "boundary_points_found": boundary_points[:5],  # Limit output
            "epsilon_tested": epsilon
        }

    def is_closed(
        self,
        set_indicator: Callable[[float], bool],
        samples: List[float]
    ) -> Dict[str, Any]:
        """
        Check if a set is closed (complement is open).

        Args:
            set_indicator: Returns True if point is in set
            samples: Sample points

        Returns:
            Dictionary with closedness analysis
        """
        # A set is closed iff it contains all its limit points
        # Approximate by checking if sequences converging to points stay in set

        points_in_set = [x for x in samples if set_indicator(x)]
        points_outside = [x for x in samples if not set_indicator(x)]

        # Check limit points
        missing_limits = []
        for x in points_outside:
            # Check if x is a limit of points in set
            nearby_in_set = [y for y in points_in_set if abs(x - y) < 0.1]
            if len(nearby_in_set) > 3:  # Likely a limit point
                missing_limits.append(x)

        is_closed = len(missing_limits) == 0

        return {
            "is_closed": is_closed,
            "points_in_set": len(points_in_set),
            "potential_missing_limits": missing_limits[:5]
        }

    def check_compactness(
        self,
        set_indicator: Callable[[float], bool],
        domain: Tuple[float, float],
        n_samples: int = 1000
    ) -> Dict[str, Any]:
        """
        Check compactness (Heine-Borel: closed and bounded in R^n).

        Args:
            set_indicator: Set membership function
            domain: Search domain
            n_samples: Number of samples

        Returns:
            Dictionary with compactness analysis
        """
        a, b = domain
        samples = np.linspace(a, b, n_samples)

        points_in_set = [x for x in samples if set_indicator(x)]

        if not points_in_set:
            return {"is_compact": True, "reason": "empty_set"}

        # Check boundedness
        is_bounded = min(points_in_set) > a + 0.01 or max(points_in_set) < b - 0.01

        # Check closedness (contains its limit points)
        closedness = self.is_closed(set_indicator, list(samples))

        is_compact = is_bounded and closedness["is_closed"]

        return {
            "is_compact": is_compact,
            "is_bounded": is_bounded,
            "is_closed": closedness["is_closed"],
            "bounds": (min(points_in_set), max(points_in_set)) if points_in_set else None
        }

    # ========== Completeness ==========

    def check_completeness(
        self,
        space_indicator: Callable[[float], bool],
        d: Callable[[float, float], float],
        cauchy_sequences: List[List[float]]
    ) -> Dict[str, Any]:
        """
        Check if space is complete (every Cauchy sequence converges).

        Args:
            space_indicator: Membership in space
            d: Metric
            cauchy_sequences: Test Cauchy sequences

        Returns:
            Dictionary with completeness analysis
        """
        non_convergent = []

        for seq in cauchy_sequences:
            # Check if Cauchy
            is_cauchy = True
            for i in range(len(seq) - 1):
                for j in range(i + 1, len(seq)):
                    if d(seq[i], seq[j]) > 1 / (min(i, j) + 1):
                        is_cauchy = False
                        break

            if not is_cauchy:
                continue

            # Check if limit is in space
            limit = seq[-1]  # Approximate limit
            if not space_indicator(limit):
                non_convergent.append({
                    "sequence_start": seq[:3],
                    "limit": limit,
                    "in_space": False
                })

        is_complete = len(non_convergent) == 0

        return {
            "is_complete": is_complete,
            "sequences_tested": len(cauchy_sequences),
            "non_convergent_examples": non_convergent[:3]
        }

    # ========== Continuity ==========

    def check_continuity(
        self,
        f: Callable[[float], float],
        domain: Tuple[float, float],
        n_points: int = 1000,
        delta: float = 0.01
    ) -> ContinuityResult:
        """
        Check continuity of function.

        Args:
            f: Function to check
            domain: Domain interval
            n_points: Number of test points
            delta: Neighborhood size

        Returns:
            ContinuityResult
        """
        a, b = domain
        samples = np.linspace(a, b, n_points)

        discontinuities = []

        for x in samples:
            # Check epsilon-delta continuity
            try:
                fx = f(x)
                # Sample nearby points
                for dx in [-delta, -delta/2, delta/2, delta]:
                    if a <= x + dx <= b:
                        fxdx = f(x + dx)
                        if abs(fxdx - fx) > 1:  # Large jump
                            discontinuities.append(x)
                            break
            except:
                discontinuities.append(x)

        is_continuous = len(discontinuities) == 0

        return ContinuityResult(
            is_continuous=is_continuous,
            continuity_type="pointwise" if is_continuous else "discontinuous",
            details={
                "discontinuities": discontinuities[:10],
                "tested_points": n_points
            }
        )

    def check_uniform_continuity(
        self,
        f: Callable[[float], float],
        domain: Tuple[float, float],
        epsilon: float = 0.1,
        n_points: int = 100
    ) -> ContinuityResult:
        """
        Check uniform continuity.

        f is uniformly continuous if for all epsilon > 0, there exists delta > 0
        such that |x - y| < delta implies |f(x) - f(y)| < epsilon for ALL x, y.

        Args:
            f: Function
            domain: Domain
            epsilon: Target precision
            n_points: Test points

        Returns:
            ContinuityResult
        """
        a, b = domain
        samples = np.linspace(a, b, n_points)

        # Find minimum delta that works for this epsilon
        min_delta = float('inf')

        for x in samples:
            for y in samples:
                if x != y:
                    try:
                        fx, fy = f(x), f(y)
                        if abs(fx - fy) < epsilon:
                            continue
                        # Need |x - y| >= delta for |f(x) - f(y)| >= epsilon
                        # So delta <= |x - y| for this pair
                        min_delta = min(min_delta, abs(x - y))
                    except:
                        pass

        is_uniform = min_delta > self._epsilon

        return ContinuityResult(
            is_continuous=is_uniform,
            continuity_type="uniform" if is_uniform else "not_uniform",
            details={
                "epsilon": epsilon,
                "min_delta_found": min_delta if min_delta < float('inf') else None
            }
        )

    def estimate_lipschitz_constant(
        self,
        f: Callable[[float], float],
        domain: Tuple[float, float],
        n_points: int = 1000
    ) -> ContinuityResult:
        """
        Estimate Lipschitz constant of f.

        |f(x) - f(y)| <= L * |x - y| for all x, y

        Args:
            f: Function
            domain: Domain
            n_points: Test points

        Returns:
            ContinuityResult with Lipschitz constant
        """
        a, b = domain
        samples = np.linspace(a, b, n_points)

        max_ratio = 0

        for i, x in enumerate(samples):
            for y in samples[i+1:]:
                try:
                    fx, fy = f(x), f(y)
                    ratio = abs(fx - fy) / abs(x - y)
                    max_ratio = max(max_ratio, ratio)
                except:
                    pass

        is_lipschitz = np.isfinite(max_ratio)

        return ContinuityResult(
            is_continuous=is_lipschitz,
            continuity_type="lipschitz" if is_lipschitz else "not_lipschitz",
            lipschitz_constant=max_ratio if is_lipschitz else None,
            details={"estimated_from": n_points}
        )

    # ========== Fixed Point Theorems ==========

    def banach_fixed_point(
        self,
        T: Callable[[float], float],
        x0: float,
        domain: Tuple[float, float],
        max_iter: int = 1000,
        tol: float = 1e-10
    ) -> FixedPointResult:
        """
        Find fixed point using Banach contraction principle.

        If T: X -> X is a contraction (|T(x) - T(y)| <= k|x - y| for k < 1),
        then T has a unique fixed point.

        Args:
            T: Contraction mapping
            x0: Initial point
            domain: Domain
            max_iter: Maximum iterations
            tol: Convergence tolerance

        Returns:
            FixedPointResult
        """
        # Estimate contraction constant
        a, b = domain
        samples = np.linspace(a, b, 100)
        max_ratio = 0

        for x in samples:
            for y in samples:
                if x != y:
                    try:
                        ratio = abs(T(x) - T(y)) / abs(x - y)
                        max_ratio = max(max_ratio, ratio)
                    except:
                        pass

        is_contraction = max_ratio < 1

        if not is_contraction:
            return FixedPointResult(
                fixed_point=None,
                converged=False,
                contraction_constant=max_ratio,
                details={"error": "Not a contraction", "estimated_k": max_ratio}
            )

        # Iterate to find fixed point
        x = x0
        for i in range(max_iter):
            try:
                x_new = T(x)

                if abs(x_new - x) < tol:
                    return FixedPointResult(
                        fixed_point=x_new,
                        iterations=i + 1,
                        converged=True,
                        contraction_constant=max_ratio
                    )

                x = x_new
            except:
                break

        return FixedPointResult(
            fixed_point=x,
            iterations=max_iter,
            converged=False,
            contraction_constant=max_ratio,
            details={"final_error": abs(T(x) - x)}
        )

    def brouwer_check(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        domain: List[Tuple[float, float]],
        n_samples: int = 1000
    ) -> Dict[str, Any]:
        """
        Check conditions for Brouwer fixed point theorem.

        If f: K -> K where K is compact and convex, then f has a fixed point.

        Args:
            f: Continuous function
            domain: Hypercube domain (compact convex in R^n)
            n_samples: Random samples

        Returns:
            Dictionary with Brouwer check
        """
        dim = len(domain)

        # Check if f maps domain into itself
        violations = 0

        for _ in range(n_samples):
            # Random point in domain
            x = np.array([np.random.uniform(a, b) for a, b in domain])

            try:
                fx = f(x)

                # Check if f(x) in domain
                for i, (a, b) in enumerate(domain):
                    if fx[i] < a - self._epsilon or fx[i] > b + self._epsilon:
                        violations += 1
                        break
            except:
                violations += 1

        maps_to_self = violations == 0

        return {
            "conditions_met": maps_to_self,
            "maps_domain_to_self": maps_to_self,
            "violations": violations,
            "samples_tested": n_samples,
            "conclusion": "Brouwer guarantees fixed point" if maps_to_self else "f may not map domain to itself"
        }
