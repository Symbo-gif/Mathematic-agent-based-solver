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
Sequences and Series Specialist
=================================

Provides comprehensive sequence and series analysis:
- Convergence tests
- Uniform convergence
- Power series analysis
- Cauchy sequences
- Limit superior/inferior
- Rearrangements

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class ConvergenceResult(Enum):
    """Result of convergence test."""
    CONVERGES = "converges"
    DIVERGES = "diverges"
    INCONCLUSIVE = "inconclusive"


@dataclass
class SequenceAnalysis:
    """Result from sequence analysis."""
    converges: bool
    limit: Optional[float] = None
    is_cauchy: bool = True
    is_bounded: bool = True
    is_monotone: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SeriesAnalysis:
    """Result from series analysis."""
    converges: ConvergenceResult
    sum_value: Optional[float] = None
    convergence_type: str = "unknown"  # absolute, conditional, divergent
    test_used: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UniformConvergenceResult:
    """Result from uniform convergence analysis."""
    converges_uniformly: bool
    converges_pointwise: bool = True
    supremum_norm_sequence: List[float] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class SequencesSeriesSpecialist:
    """
    BDI Agent for sequence and series analysis.

    Capabilities:
    - Convergence analysis
    - Multiple convergence tests
    - Uniform convergence
    - Power series radius
    - Limit computations
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._epsilon = 1e-12

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "sequence" in self.beliefs:
            self.desires.append("analyze_sequence")
        if "series" in self.beliefs:
            self.desires.append("analyze_series")
        if "function_sequence" in self.beliefs:
            self.desires.append("check_uniform_convergence")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "analyze_sequence":
            seq = self.beliefs.get("sequence")
            return {"result": self.analyze_sequence(seq)}
        elif goal == "analyze_series":
            series = self.beliefs.get("series")
            return {"result": self.analyze_series(series)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Sequence Analysis ==========

    def analyze_sequence(
        self,
        a: Callable[[int], float],
        n_terms: int = 1000
    ) -> SequenceAnalysis:
        """
        Comprehensive sequence analysis.

        Args:
            a: Sequence function a(n)
            n_terms: Number of terms to analyze

        Returns:
            SequenceAnalysis
        """
        # Generate terms
        terms = []
        for n in range(1, n_terms + 1):
            try:
                val = a(n)
                if np.isfinite(val):
                    terms.append(val)
                else:
                    terms.append(np.sign(val) * 1e100 if val != 0 else 0)
            except:
                break

        if len(terms) < 10:
            return SequenceAnalysis(converges=False, details={"error": "sequence_too_short"})

        terms = np.array(terms)

        # Check boundedness
        is_bounded = np.max(np.abs(terms)) < 1e10

        # Check monotonicity
        diffs = np.diff(terms)
        is_increasing = np.all(diffs >= -self._epsilon)
        is_decreasing = np.all(diffs <= self._epsilon)
        is_monotone = is_increasing or is_decreasing

        # Check Cauchy criterion
        is_cauchy = True
        tail = terms[-100:]
        for i in range(len(tail)):
            for j in range(i + 1, len(tail)):
                if abs(tail[i] - tail[j]) > 0.001:
                    is_cauchy = False
                    break

        # Estimate limit
        limit = None
        converges = False

        if is_cauchy:
            limit = np.mean(terms[-50:])
            converges = True

        # Monotone bounded => converges
        if is_monotone and is_bounded and not converges:
            limit = terms[-1]
            converges = True

        return SequenceAnalysis(
            converges=converges,
            limit=limit,
            is_cauchy=is_cauchy,
            is_bounded=is_bounded,
            is_monotone=is_monotone,
            details={
                "first_terms": list(terms[:5]),
                "last_terms": list(terms[-5:]),
                "monotone_type": "increasing" if is_increasing else ("decreasing" if is_decreasing else "neither")
            }
        )

    def limsup_liminf(
        self,
        a: Callable[[int], float],
        n_terms: int = 1000
    ) -> Dict[str, float]:
        """
        Compute limit superior and inferior.

        limsup a_n = lim_{n->inf} sup_{k>=n} a_k
        liminf a_n = lim_{n->inf} inf_{k>=n} a_k

        Args:
            a: Sequence function
            n_terms: Terms to compute

        Returns:
            Dictionary with limsup and liminf
        """
        terms = []
        for n in range(1, n_terms + 1):
            try:
                val = a(n)
                if np.isfinite(val):
                    terms.append(val)
            except:
                break

        if len(terms) < 10:
            return {"limsup": np.nan, "liminf": np.nan}

        # Compute running sup and inf from the tail
        sups = []
        infs = []

        for n in range(len(terms)):
            tail = terms[n:]
            sups.append(max(tail))
            infs.append(min(tail))

        limsup = min(sups[-100:])  # Limit of decreasing sequence
        liminf = max(infs[-100:])  # Limit of increasing sequence

        return {
            "limsup": limsup,
            "liminf": liminf,
            "converges": abs(limsup - liminf) < self._epsilon,
            "limit": (limsup + liminf) / 2 if abs(limsup - liminf) < self._epsilon else None
        }

    # ========== Series Convergence Tests ==========

    def analyze_series(
        self,
        a: Callable[[int], float],
        n_terms: int = 1000
    ) -> SeriesAnalysis:
        """
        Comprehensive series analysis using multiple tests.

        Args:
            a: Term function a(n) for sum of a(n)
            n_terms: Terms to analyze

        Returns:
            SeriesAnalysis
        """
        # Try multiple tests
        results = {}

        # Divergence test
        div_test = self.divergence_test(a, n_terms)
        results["divergence_test"] = div_test

        if div_test == ConvergenceResult.DIVERGES:
            return SeriesAnalysis(
                converges=ConvergenceResult.DIVERGES,
                test_used="divergence_test",
                details=results
            )

        # Ratio test
        ratio = self.ratio_test(a, n_terms)
        results["ratio_test"] = ratio

        if ratio != ConvergenceResult.INCONCLUSIVE:
            return SeriesAnalysis(
                converges=ratio,
                convergence_type="absolute" if ratio == ConvergenceResult.CONVERGES else "divergent",
                test_used="ratio_test",
                details=results
            )

        # Root test
        root = self.root_test(a, n_terms)
        results["root_test"] = root

        if root != ConvergenceResult.INCONCLUSIVE:
            return SeriesAnalysis(
                converges=root,
                convergence_type="absolute" if root == ConvergenceResult.CONVERGES else "divergent",
                test_used="root_test",
                details=results
            )

        # Comparison test (with 1/n^2)
        comparison = self.comparison_test(a, lambda n: 1/n**2, n_terms)
        results["comparison_test"] = comparison

        if comparison != ConvergenceResult.INCONCLUSIVE:
            return SeriesAnalysis(
                converges=comparison,
                test_used="comparison_test",
                details=results
            )

        # Alternating series test
        alt = self.alternating_series_test(a, n_terms)
        results["alternating_test"] = alt

        if alt == ConvergenceResult.CONVERGES:
            return SeriesAnalysis(
                converges=ConvergenceResult.CONVERGES,
                convergence_type="conditional",
                test_used="alternating_series_test",
                details=results
            )

        # Compute partial sums
        partial_sums = self._partial_sums(a, n_terms)
        if partial_sums:
            results["partial_sums"] = {
                "s_10": partial_sums[9] if len(partial_sums) > 9 else None,
                "s_100": partial_sums[99] if len(partial_sums) > 99 else None,
                "s_1000": partial_sums[-1] if len(partial_sums) >= 1000 else None
            }

        return SeriesAnalysis(
            converges=ConvergenceResult.INCONCLUSIVE,
            sum_value=partial_sums[-1] if partial_sums else None,
            test_used="inconclusive",
            details=results
        )

    def divergence_test(
        self,
        a: Callable[[int], float],
        n_terms: int = 100
    ) -> ConvergenceResult:
        """
        Divergence test: if lim a_n != 0, series diverges.

        Args:
            a: Term function
            n_terms: Terms to check

        Returns:
            ConvergenceResult
        """
        # Check if terms go to 0
        tail_terms = []
        for n in range(n_terms - 50, n_terms + 1):
            try:
                val = a(n)
                if np.isfinite(val):
                    tail_terms.append(abs(val))
            except:
                pass

        if not tail_terms:
            return ConvergenceResult.INCONCLUSIVE

        if max(tail_terms) > 0.001:
            return ConvergenceResult.DIVERGES

        return ConvergenceResult.INCONCLUSIVE

    def ratio_test(
        self,
        a: Callable[[int], float],
        n_terms: int = 100
    ) -> ConvergenceResult:
        """
        Ratio test: L = lim |a_{n+1}/a_n|.
        L < 1 => converges absolutely
        L > 1 => diverges
        L = 1 => inconclusive

        Args:
            a: Term function
            n_terms: Terms to analyze

        Returns:
            ConvergenceResult
        """
        ratios = []

        for n in range(n_terms - 50, n_terms):
            try:
                a_n = a(n)
                a_n1 = a(n + 1)

                if abs(a_n) > self._epsilon:
                    ratio = abs(a_n1 / a_n)
                    if np.isfinite(ratio):
                        ratios.append(ratio)
            except:
                pass

        if len(ratios) < 10:
            return ConvergenceResult.INCONCLUSIVE

        L = np.mean(ratios[-20:])

        if L < 1 - 0.01:
            return ConvergenceResult.CONVERGES
        elif L > 1 + 0.01:
            return ConvergenceResult.DIVERGES

        return ConvergenceResult.INCONCLUSIVE

    def root_test(
        self,
        a: Callable[[int], float],
        n_terms: int = 100
    ) -> ConvergenceResult:
        """
        Root test: L = limsup |a_n|^(1/n).
        L < 1 => converges absolutely
        L > 1 => diverges
        L = 1 => inconclusive

        Args:
            a: Term function
            n_terms: Terms to analyze

        Returns:
            ConvergenceResult
        """
        roots = []

        for n in range(max(1, n_terms - 50), n_terms + 1):
            try:
                a_n = abs(a(n))
                if a_n > 0:
                    root = a_n ** (1/n)
                    if np.isfinite(root):
                        roots.append(root)
            except:
                pass

        if len(roots) < 10:
            return ConvergenceResult.INCONCLUSIVE

        L = max(roots[-20:])  # limsup approximation

        if L < 1 - 0.01:
            return ConvergenceResult.CONVERGES
        elif L > 1 + 0.01:
            return ConvergenceResult.DIVERGES

        return ConvergenceResult.INCONCLUSIVE

    def comparison_test(
        self,
        a: Callable[[int], float],
        b: Callable[[int], float],
        n_terms: int = 100,
        b_converges: bool = True
    ) -> ConvergenceResult:
        """
        Comparison test with known series b.

        If 0 <= a_n <= b_n and sum(b_n) converges, then sum(a_n) converges.
        If a_n >= b_n >= 0 and sum(b_n) diverges, then sum(a_n) diverges.

        Args:
            a: Test series
            b: Comparison series
            n_terms: Terms to check
            b_converges: Whether sum(b_n) converges

        Returns:
            ConvergenceResult
        """
        for n in range(1, n_terms + 1):
            try:
                a_n = abs(a(n))
                b_n = abs(b(n))

                if b_converges:
                    if a_n > b_n + self._epsilon:
                        return ConvergenceResult.INCONCLUSIVE
                else:
                    if a_n < b_n - self._epsilon:
                        return ConvergenceResult.INCONCLUSIVE
            except:
                pass

        if b_converges:
            return ConvergenceResult.CONVERGES
        else:
            return ConvergenceResult.DIVERGES

    def alternating_series_test(
        self,
        a: Callable[[int], float],
        n_terms: int = 100
    ) -> ConvergenceResult:
        """
        Alternating series test (Leibniz).

        If a_n = (-1)^n * b_n where b_n >= 0, b_n decreasing, lim b_n = 0,
        then sum(a_n) converges.

        Args:
            a: Term function
            n_terms: Terms to check

        Returns:
            ConvergenceResult
        """
        # Check if alternating
        terms = []
        for n in range(1, min(n_terms, 50) + 1):
            try:
                terms.append(a(n))
            except:
                pass

        if len(terms) < 10:
            return ConvergenceResult.INCONCLUSIVE

        # Check sign alternation
        signs = [np.sign(t) for t in terms if t != 0]
        is_alternating = all(signs[i] * signs[i+1] < 0 for i in range(len(signs) - 1))

        if not is_alternating:
            return ConvergenceResult.INCONCLUSIVE

        # Check |a_n| is decreasing
        abs_terms = [abs(t) for t in terms]
        is_decreasing = all(abs_terms[i] >= abs_terms[i+1] - self._epsilon for i in range(len(abs_terms) - 1))

        # Check limit is 0
        tail = [abs(a(n)) for n in range(n_terms - 20, n_terms + 1)]
        goes_to_zero = max(tail) < 0.01

        if is_alternating and is_decreasing and goes_to_zero:
            return ConvergenceResult.CONVERGES

        return ConvergenceResult.INCONCLUSIVE

    def integral_test(
        self,
        a: Callable[[int], float],
        f: Callable[[float], float],
        n_terms: int = 1000
    ) -> ConvergenceResult:
        """
        Integral test: if f is positive decreasing and a_n = f(n),
        then sum(a_n) and integral(f, 1, inf) converge/diverge together.

        Args:
            a: Term function
            f: Continuous version
            n_terms: Upper limit for integral

        Returns:
            ConvergenceResult
        """
        # Approximate integral
        x = np.linspace(1, n_terms, n_terms * 10)
        dx = x[1] - x[0]

        integral = 0
        for xi in x:
            try:
                integral += f(xi) * dx
            except:
                pass

        # Compare with partial sum
        partial_sum = sum(a(n) for n in range(1, n_terms + 1))

        if np.isfinite(integral) and abs(integral) < 1e10:
            return ConvergenceResult.CONVERGES
        elif not np.isfinite(integral) or abs(integral) > 1e10:
            return ConvergenceResult.DIVERGES

        return ConvergenceResult.INCONCLUSIVE

    def _partial_sums(
        self,
        a: Callable[[int], float],
        n_terms: int
    ) -> List[float]:
        """Compute partial sums."""
        sums = []
        total = 0

        for n in range(1, n_terms + 1):
            try:
                total += a(n)
                sums.append(total)
            except:
                break

        return sums

    # ========== Uniform Convergence ==========

    def check_uniform_convergence(
        self,
        f_n: Callable[[int, float], float],
        f: Callable[[float], float],
        domain: Tuple[float, float],
        n_values: List[int],
        n_points: int = 100
    ) -> UniformConvergenceResult:
        """
        Check uniform convergence of function sequence.

        f_n -> f uniformly iff sup_x |f_n(x) - f(x)| -> 0.

        Args:
            f_n: Sequence of functions f_n(n, x)
            f: Limit function
            domain: Domain interval
            n_values: Values of n to test
            n_points: Sample points

        Returns:
            UniformConvergenceResult
        """
        a, b = domain
        x_vals = np.linspace(a, b, n_points)

        sup_norms = []

        for n in n_values:
            max_diff = 0
            for x in x_vals:
                try:
                    diff = abs(f_n(n, x) - f(x))
                    max_diff = max(max_diff, diff)
                except:
                    pass

            sup_norms.append(max_diff)

        # Check if sup norms go to 0
        converges_uniformly = sup_norms[-1] < 0.01 if sup_norms else False

        # Check pointwise convergence
        pointwise = True
        for x in x_vals[::10]:
            vals = []
            for n in n_values:
                try:
                    vals.append(f_n(n, x))
                except:
                    pass

            if vals:
                try:
                    limit = f(x)
                    if abs(vals[-1] - limit) > 0.1:
                        pointwise = False
                        break
                except:
                    pass

        return UniformConvergenceResult(
            converges_uniformly=converges_uniformly,
            converges_pointwise=pointwise,
            supremum_norm_sequence=sup_norms,
            details={
                "n_values": n_values,
                "final_sup_norm": sup_norms[-1] if sup_norms else None
            }
        )

    def weierstrass_m_test(
        self,
        f_n: Callable[[int, float], float],
        M: Callable[[int], float],
        domain: Tuple[float, float],
        n_terms: int = 100
    ) -> Dict[str, Any]:
        """
        Apply Weierstrass M-test for uniform convergence of series.

        If |f_n(x)| <= M_n for all x and sum(M_n) converges,
        then sum(f_n(x)) converges uniformly.

        Args:
            f_n: Function sequence
            M: Bounding sequence
            domain: Domain
            n_terms: Number of terms

        Returns:
            Dictionary with M-test results
        """
        a, b = domain
        x_samples = np.linspace(a, b, 50)

        # Check |f_n(x)| <= M_n
        bound_holds = True

        for n in range(1, min(n_terms, 50) + 1):
            M_n = M(n)
            for x in x_samples:
                try:
                    if abs(f_n(n, x)) > M_n + self._epsilon:
                        bound_holds = False
                        break
                except:
                    pass

        # Check if sum(M_n) converges
        M_sum = sum(M(n) for n in range(1, n_terms + 1))
        M_converges = np.isfinite(M_sum) and M_sum < 1e10

        uniform_convergence = bound_holds and M_converges

        return {
            "uniform_convergence": uniform_convergence,
            "bounds_hold": bound_holds,
            "M_series_converges": M_converges,
            "M_sum": M_sum
        }

    # ========== Power Series ==========

    def radius_of_convergence(
        self,
        a: Callable[[int], float],
        method: str = "ratio"
    ) -> Dict[str, Any]:
        """
        Compute radius of convergence for power series sum(a_n * x^n).

        R = 1 / limsup |a_n|^(1/n) (Cauchy-Hadamard)
        R = lim |a_n / a_{n+1}| (ratio, if limit exists)

        Args:
            a: Coefficient function
            method: "ratio" or "root"

        Returns:
            Dictionary with radius
        """
        if method == "ratio":
            ratios = []
            for n in range(1, 100):
                try:
                    a_n = abs(a(n))
                    a_n1 = abs(a(n + 1))

                    if a_n1 > self._epsilon:
                        ratios.append(a_n / a_n1)
                except:
                    pass

            if ratios:
                R = np.mean(ratios[-20:])
                return {"radius": R, "method": "ratio", "converged": np.std(ratios[-20:]) < 0.1}

        elif method == "root":
            roots = []
            for n in range(1, 100):
                try:
                    a_n = abs(a(n))
                    if a_n > 0:
                        roots.append(a_n ** (1/n))
                except:
                    pass

            if roots:
                limsup = max(roots[-20:])
                R = 1 / limsup if limsup > self._epsilon else float('inf')
                return {"radius": R, "method": "root", "limsup_root": limsup}

        return {"radius": None, "error": "Could not determine radius"}
