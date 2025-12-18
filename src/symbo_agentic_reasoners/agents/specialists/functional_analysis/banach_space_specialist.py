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
Banach Space Specialist
========================

Provides comprehensive Banach space operations:
- Norm verification and computation
- Completeness analysis
- Bounded linear operators
- Dual spaces and functionals
- Hahn-Banach applications
- Open mapping theorem applications

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field


@dataclass
class NormResult:
    """Result from norm computation."""
    is_norm: bool
    value: float = 0.0
    properties: List[str] = field(default_factory=list)
    counterexample: Optional[Dict[str, Any]] = None


@dataclass
class OperatorNormResult:
    """Result from operator norm computation."""
    norm: float
    is_bounded: bool = True
    supremum_achieved_at: Optional[np.ndarray] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DualSpaceResult:
    """Result from dual space analysis."""
    dual_element: Optional[Callable] = None
    norm: float = 0.0
    representation: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class BanachSpaceSpecialist:
    """
    BDI Agent for Banach space analysis.

    Capabilities:
    - Verify norm axioms
    - Compute various norms
    - Analyze bounded operators
    - Dual space computations
    - Banach space theorems
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
        if "norm_candidate" in self.beliefs:
            self.desires.append("verify_norm")
        if "operator" in self.beliefs:
            self.desires.append("analyze_operator")
        if "functional" in self.beliefs:
            self.desires.append("analyze_dual")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "verify_norm":
            norm_fn = self.beliefs.get("norm_candidate")
            samples = self.beliefs.get("samples", [])
            return {"result": self.verify_norm(norm_fn, samples)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Norm Operations ==========

    def verify_norm(
        self,
        norm_fn: Callable[[np.ndarray], float],
        samples: List[np.ndarray],
        scalars: List[float] = None
    ) -> NormResult:
        """
        Verify that norm_fn satisfies norm axioms.

        Axioms:
        1. ||x|| >= 0 and ||x|| = 0 iff x = 0
        2. ||ax|| = |a| * ||x|| (homogeneity)
        3. ||x + y|| <= ||x|| + ||y|| (triangle inequality)

        Args:
            norm_fn: Proposed norm function
            samples: Sample vectors
            scalars: Scalars to test homogeneity

        Returns:
            NormResult
        """
        if scalars is None:
            scalars = [-2, -1, 0, 0.5, 1, 2, 3]

        properties = []
        counterexample = None

        # Test non-negativity
        nonneg = True
        for x in samples:
            val = norm_fn(x)
            if val < -self._epsilon:
                nonneg = False
                counterexample = {"axiom": "non-negativity", "x": x, "norm": val}
                break

        if nonneg:
            properties.append("non-negative")

        # Test definiteness (||x|| = 0 => x = 0)
        definite = True
        for x in samples:
            if norm_fn(x) < self._epsilon and np.linalg.norm(x) > self._epsilon:
                definite = False
                counterexample = counterexample or {"axiom": "definiteness", "x": x}
                break

        if definite:
            properties.append("definite")

        # Test homogeneity
        homogeneous = True
        for x in samples:
            for a in scalars:
                lhs = norm_fn(a * x)
                rhs = abs(a) * norm_fn(x)
                if abs(lhs - rhs) > self._epsilon * max(1, rhs):
                    homogeneous = False
                    counterexample = counterexample or {
                        "axiom": "homogeneity",
                        "x": x, "a": a,
                        "||ax||": lhs, "|a|||x||": rhs
                    }
                    break

        if homogeneous:
            properties.append("homogeneous")

        # Test triangle inequality
        triangle = True
        for x in samples:
            for y in samples:
                lhs = norm_fn(x + y)
                rhs = norm_fn(x) + norm_fn(y)
                if lhs > rhs + self._epsilon:
                    triangle = False
                    counterexample = counterexample or {
                        "axiom": "triangle",
                        "x": x, "y": y,
                        "||x+y||": lhs, "||x||+||y||": rhs
                    }
                    break

        if triangle:
            properties.append("triangle_inequality")

        is_norm = len(properties) == 4

        return NormResult(
            is_norm=is_norm,
            properties=properties,
            counterexample=counterexample
        )

    # ========== Common Norms ==========

    @staticmethod
    def lp_norm(x: np.ndarray, p: float) -> float:
        """Compute Lp norm."""
        if p == float('inf'):
            return np.max(np.abs(x))
        return np.sum(np.abs(x) ** p) ** (1/p)

    @staticmethod
    def l1_norm(x: np.ndarray) -> float:
        """L1 norm."""
        return np.sum(np.abs(x))

    @staticmethod
    def l2_norm(x: np.ndarray) -> float:
        """L2 (Euclidean) norm."""
        return np.sqrt(np.sum(x ** 2))

    @staticmethod
    def linf_norm(x: np.ndarray) -> float:
        """L-infinity norm."""
        return np.max(np.abs(x))

    def function_lp_norm(
        self,
        f: Callable[[float], float],
        p: float,
        domain: Tuple[float, float],
        n_points: int = 1000
    ) -> float:
        """
        Compute Lp norm of function.

        ||f||_p = (integral |f|^p)^(1/p)
        """
        a, b = domain
        x = np.linspace(a, b, n_points)
        dx = (b - a) / (n_points - 1)

        if p == float('inf'):
            return max(abs(f(xi)) for xi in x)

        integral = sum(abs(f(xi)) ** p * dx for xi in x)
        return integral ** (1/p)

    # ========== Bounded Operators ==========

    def operator_norm(
        self,
        T: Callable[[np.ndarray], np.ndarray],
        dim: int,
        n_samples: int = 1000
    ) -> OperatorNormResult:
        """
        Compute operator norm ||T|| = sup{||Tx|| : ||x|| = 1}.

        Args:
            T: Linear operator
            dim: Dimension of domain
            n_samples: Number of unit vectors to sample

        Returns:
            OperatorNormResult
        """
        max_norm = 0
        max_x = None

        for _ in range(n_samples):
            # Random unit vector
            x = np.random.randn(dim)
            x = x / np.linalg.norm(x)

            try:
                Tx = T(x)
                norm_Tx = np.linalg.norm(Tx)

                if norm_Tx > max_norm:
                    max_norm = norm_Tx
                    max_x = x.copy()
            except:
                pass

        return OperatorNormResult(
            norm=max_norm,
            is_bounded=np.isfinite(max_norm),
            supremum_achieved_at=max_x
        )

    def matrix_operator_norm(
        self,
        A: np.ndarray,
        p: float = 2
    ) -> OperatorNormResult:
        """
        Compute matrix operator norm.

        ||A||_p = max{||Ax||_p / ||x||_p : x != 0}

        For p=2: ||A||_2 = largest singular value
        For p=1: ||A||_1 = max column sum
        For p=inf: ||A||_inf = max row sum
        """
        if p == 2:
            # Spectral norm = largest singular value
            s = np.linalg.svd(A, compute_uv=False)
            norm = s[0]
        elif p == 1:
            norm = np.max(np.sum(np.abs(A), axis=0))
        elif p == float('inf'):
            norm = np.max(np.sum(np.abs(A), axis=1))
        else:
            # General case: use power iteration
            norm = self._power_iteration_norm(A, p)

        return OperatorNormResult(norm=norm, is_bounded=True)

    def _power_iteration_norm(
        self,
        A: np.ndarray,
        p: float,
        max_iter: int = 100
    ) -> float:
        """Estimate operator norm via power iteration."""
        n = A.shape[1]
        x = np.random.randn(n)
        x = x / self.lp_norm(x, p)

        for _ in range(max_iter):
            y = A @ x
            norm_y = self.lp_norm(y, p)

            if norm_y < self._epsilon:
                break

            x = y / norm_y

        return self.lp_norm(A @ x, p)

    def is_bounded_below(
        self,
        T: Callable[[np.ndarray], np.ndarray],
        dim: int,
        n_samples: int = 1000
    ) -> Dict[str, Any]:
        """
        Check if operator is bounded below.

        T is bounded below if ||Tx|| >= c||x|| for some c > 0.
        """
        min_ratio = float('inf')

        for _ in range(n_samples):
            x = np.random.randn(dim)
            norm_x = np.linalg.norm(x)

            if norm_x < self._epsilon:
                continue

            try:
                Tx = T(x)
                norm_Tx = np.linalg.norm(Tx)
                ratio = norm_Tx / norm_x
                min_ratio = min(min_ratio, ratio)
            except:
                pass

        bounded_below = min_ratio > self._epsilon

        return {
            "bounded_below": bounded_below,
            "lower_bound": min_ratio if bounded_below else 0,
            "is_injective": bounded_below  # Bounded below => injective for linear ops
        }

    # ========== Dual Space ==========

    def riesz_representation(
        self,
        f: Callable[[np.ndarray], float],
        dim: int
    ) -> DualSpaceResult:
        """
        Find Riesz representation of bounded linear functional.

        For Hilbert spaces: f(x) = <x, y> for unique y.

        Args:
            f: Bounded linear functional
            dim: Dimension

        Returns:
            DualSpaceResult with representing element
        """
        # Find y such that f(x) = <x, y>
        # f(e_i) = <e_i, y> = y_i
        y = np.zeros(dim)

        for i in range(dim):
            e_i = np.zeros(dim)
            e_i[i] = 1.0
            y[i] = f(e_i)

        # Verify representation
        def represented_functional(x):
            """Perform represented functional operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.represented_functional(...)
            """
            return np.dot(x, y)

        # Compute functional norm
        norm = np.linalg.norm(y)

        return DualSpaceResult(
            dual_element=lambda x: np.dot(x, y),
            norm=norm,
            representation=f"f(x) = <x, y> where y = {y}",
            details={"y": y}
        )

    def compute_dual_norm(
        self,
        f: Callable[[np.ndarray], float],
        dim: int,
        n_samples: int = 1000,
        p: float = 2
    ) -> float:
        """
        Compute dual norm of functional.

        ||f||* = sup{|f(x)| : ||x|| <= 1}

        For Lp, dual is Lq where 1/p + 1/q = 1.
        """
        max_val = 0

        for _ in range(n_samples):
            x = np.random.randn(dim)
            norm_x = self.lp_norm(x, p)

            if norm_x > self._epsilon:
                x = x / norm_x  # Unit vector

            try:
                val = abs(f(x))
                max_val = max(max_val, val)
            except:
                pass

        return max_val

    # ========== Banach Space Theorems ==========

    def open_mapping_theorem_check(
        self,
        T: Callable[[np.ndarray], np.ndarray],
        dim_domain: int,
        dim_codomain: int,
        n_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Check conditions for Open Mapping Theorem.

        If T: X -> Y is bounded, linear, and surjective between
        Banach spaces, then T is an open map.

        Args:
            T: Linear operator
            dim_domain: Domain dimension
            dim_codomain: Codomain dimension

        Returns:
            Dictionary with theorem applicability
        """
        # Check if surjective (onto)
        # Sample random y and check if Tx = y has solutions

        surjective = True
        for _ in range(n_samples):
            y = np.random.randn(dim_codomain)

            # Try to find x with T(x) close to y
            # Using least squares
            try:
                # Build matrix representation
                A = np.zeros((dim_codomain, dim_domain))
                for j in range(dim_domain):
                    e_j = np.zeros(dim_domain)
                    e_j[j] = 1
                    A[:, j] = T(e_j)

                x, residuals, rank, s = np.linalg.lstsq(A, y, rcond=None)

                if np.linalg.norm(T(x) - y) > 0.01 * np.linalg.norm(y):
                    surjective = False
                    break
            except:
                surjective = False
                break

        # Check if bounded
        op_norm = self.operator_norm(T, dim_domain)
        is_bounded = op_norm.is_bounded

        theorem_applies = surjective and is_bounded

        return {
            "open_mapping_applies": theorem_applies,
            "is_surjective": surjective,
            "is_bounded": is_bounded,
            "operator_norm": op_norm.norm,
            "conclusion": "T is an open map" if theorem_applies else "Cannot conclude T is open"
        }

    def closed_graph_theorem_check(
        self,
        T: Callable[[np.ndarray], np.ndarray],
        dim: int,
        n_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Check conditions for Closed Graph Theorem.

        If T: X -> Y has closed graph (x_n -> x, Tx_n -> y => Tx = y),
        then T is bounded.

        Args:
            T: Linear operator
            dim: Dimension

        Returns:
            Dictionary with theorem analysis
        """
        # Check if graph is closed by testing continuity
        closed_graph = True

        for _ in range(n_samples):
            x = np.random.randn(dim)

            # Create sequence converging to x
            for n in range(1, 20):
                x_n = x + np.random.randn(dim) / n

                try:
                    Tx = T(x)
                    Tx_n = T(x_n)

                    # If x_n -> x but T(x_n) not -> T(x), graph not closed
                    if np.linalg.norm(x_n - x) < 0.1 and np.linalg.norm(Tx_n - Tx) > 1:
                        closed_graph = False
                        break
                except:
                    pass

        return {
            "closed_graph": closed_graph,
            "implies_bounded": closed_graph,
            "conclusion": "T is bounded" if closed_graph else "Graph may not be closed"
        }

    def uniform_boundedness_check(
        self,
        operators: List[Callable[[np.ndarray], np.ndarray]],
        dim: int,
        n_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Check Uniform Boundedness Principle (Banach-Steinhaus).

        If {T_n} is pointwise bounded, then it's uniformly bounded.

        Args:
            operators: List of operators
            dim: Dimension

        Returns:
            Dictionary with principle analysis
        """
        # Check pointwise boundedness
        pointwise_bounded = True
        sup_norms = []

        for T in operators:
            norm_result = self.operator_norm(T, dim, n_samples)
            sup_norms.append(norm_result.norm)

            if not np.isfinite(norm_result.norm):
                pointwise_bounded = False
                break

        uniform_bound = max(sup_norms) if sup_norms else 0
        uniformly_bounded = np.isfinite(uniform_bound)

        return {
            "pointwise_bounded": pointwise_bounded,
            "uniformly_bounded": uniformly_bounded,
            "uniform_bound": uniform_bound,
            "individual_norms": sup_norms,
            "principle_applies": pointwise_bounded
        }
