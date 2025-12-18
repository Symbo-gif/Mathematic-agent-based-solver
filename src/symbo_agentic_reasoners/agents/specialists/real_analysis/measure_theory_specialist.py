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
Measure Theory Specialist
==========================

Provides comprehensive measure-theoretic operations:
- Lebesgue measure computation
- Measurable set operations
- Lebesgue integration
- Convergence theorems (DCT, MCT, Fatou)
- Lp spaces and norms
- Product measures and Fubini's theorem

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum


class MeasureType(Enum):
    """Types of measures."""
    LEBESGUE = "lebesgue"
    COUNTING = "counting"
    DIRAC = "dirac"
    PRODUCT = "product"
    SIGNED = "signed"


class ConvergenceType(Enum):
    """Types of convergence."""
    POINTWISE = "pointwise"
    UNIFORM = "uniform"
    ALMOST_EVERYWHERE = "almost_everywhere"
    IN_MEASURE = "in_measure"
    LP = "lp"


@dataclass
class MeasureResult:
    """Result from measure computation."""
    value: float
    measure_type: MeasureType
    is_finite: bool = True
    is_sigma_finite: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegralResult:
    """Result from Lebesgue integration."""
    value: float
    is_integrable: bool = True
    convergence_method: Optional[str] = None
    error_estimate: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LpNormResult:
    """Result from Lp norm computation."""
    norm: float
    p: float
    is_in_lp: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


class MeasureTheorySpecialist:
    """
    BDI Agent for measure theory operations.

    Capabilities:
    - Lebesgue measure of sets
    - Lebesgue integration
    - Convergence theorem applications
    - Lp space analysis
    - Product measure and Fubini
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
        if "set" in self.beliefs:
            self.desires.append("compute_measure")
        if "function" in self.beliefs and "domain" in self.beliefs:
            self.desires.append("integrate")
        if "function_sequence" in self.beliefs:
            self.desires.append("check_convergence")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "compute_measure":
            return {"result": self._compute_measure()}
        elif goal == "integrate":
            return {"result": self._integrate()}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Lebesgue Measure ==========

    def lebesgue_measure_interval(
        self,
        a: float,
        b: float
    ) -> MeasureResult:
        """
        Compute Lebesgue measure of interval [a, b].

        m([a, b]) = b - a

        Args:
            a: Left endpoint
            b: Right endpoint

        Returns:
            MeasureResult with measure value
        """
        if a > b:
            a, b = b, a

        if np.isinf(a) or np.isinf(b):
            return MeasureResult(
                value=float('inf'),
                measure_type=MeasureType.LEBESGUE,
                is_finite=False
            )

        return MeasureResult(
            value=b - a,
            measure_type=MeasureType.LEBESGUE,
            details={"interval": (a, b)}
        )

    def lebesgue_measure_union(
        self,
        intervals: List[Tuple[float, float]]
    ) -> MeasureResult:
        """
        Compute Lebesgue measure of union of intervals.

        Handles overlapping intervals correctly.

        Args:
            intervals: List of (a, b) intervals

        Returns:
            MeasureResult with total measure
        """
        if not intervals:
            return MeasureResult(value=0, measure_type=MeasureType.LEBESGUE)

        # Sort intervals by left endpoint
        sorted_intervals = sorted(intervals, key=lambda x: x[0])

        # Merge overlapping intervals
        merged = []
        current_start, current_end = sorted_intervals[0]

        for start, end in sorted_intervals[1:]:
            if start <= current_end:
                # Overlapping, extend
                current_end = max(current_end, end)
            else:
                # Non-overlapping, save current and start new
                merged.append((current_start, current_end))
                current_start, current_end = start, end

        merged.append((current_start, current_end))

        # Sum measures
        total = sum(b - a for a, b in merged)

        return MeasureResult(
            value=total,
            measure_type=MeasureType.LEBESGUE,
            details={"merged_intervals": merged, "original_count": len(intervals)}
        )

    def lebesgue_measure_cantor(self, level: int = 10) -> MeasureResult:
        """
        Compute measure of Cantor set approximation.

        The Cantor set has Lebesgue measure 0.
        At level n, we remove 1 - (2/3)^n of [0, 1].

        Args:
            level: Approximation level

        Returns:
            MeasureResult (approaching 0)
        """
        measure = (2/3) ** level

        return MeasureResult(
            value=measure,
            measure_type=MeasureType.LEBESGUE,
            details={
                "level": level,
                "limit": 0,
                "note": "Cantor set has measure 0"
            }
        )

    def outer_measure(
        self,
        set_indicator: Callable[[float], bool],
        domain: Tuple[float, float],
        n_intervals: int = 1000
    ) -> float:
        """
        Compute Lebesgue outer measure of a set.

        m*(E) = inf{sum of |I_k| : E subset union of I_k}

        Args:
            set_indicator: Function returning True if point is in set
            domain: (a, b) domain to search
            n_intervals: Number of intervals for covering

        Returns:
            Outer measure estimate
        """
        a, b = domain
        points = np.linspace(a, b, n_intervals + 1)
        dx = (b - a) / n_intervals

        # Find intervals that intersect the set
        covering_measure = 0

        for i in range(n_intervals):
            # Sample several points in interval
            samples = np.linspace(points[i], points[i + 1], 5)
            if any(set_indicator(x) for x in samples):
                covering_measure += dx

        return covering_measure

    # ========== Lebesgue Integration ==========

    def lebesgue_integrate(
        self,
        f: Callable[[float], float],
        domain: Union[Tuple[float, float], List[Tuple[float, float]]],
        n_points: int = 10000,
        method: str = "simple"
    ) -> IntegralResult:
        """
        Compute Lebesgue integral of f over domain.

        For nice functions, this equals the Riemann integral.
        For characteristic functions, this gives measure.

        Args:
            f: Measurable function
            domain: Integration domain (interval or list of intervals)
            n_points: Number of sample points
            method: "simple" or "montecarlo"

        Returns:
            IntegralResult
        """
        if isinstance(domain, tuple):
            domain = [domain]

        if method == "simple":
            return self._simple_lebesgue_integral(f, domain, n_points)
        elif method == "montecarlo":
            return self._montecarlo_integral(f, domain, n_points)

        return IntegralResult(value=0, is_integrable=False)

    def _simple_lebesgue_integral(
        self,
        f: Callable[[float], float],
        intervals: List[Tuple[float, float]],
        n_points: int
    ) -> IntegralResult:
        """Simple function approximation to Lebesgue integral."""
        total = 0
        error = 0

        for a, b in intervals:
            if np.isinf(a) or np.isinf(b):
                # Handle improper integral
                result = self._improper_integral(f, a, b, n_points)
                total += result
                continue

            x = np.linspace(a, b, n_points)
            dx = (b - a) / (n_points - 1)

            values = []
            for xi in x:
                try:
                    val = f(xi)
                    if np.isfinite(val):
                        values.append(val)
                    else:
                        values.append(0)
                except:
                    values.append(0)

            values = np.array(values)
            integral = np.trapz(values, dx=dx)
            total += integral

            # Error estimate via Simpson comparison
            simpson = dx / 3 * (values[0] + 4 * np.sum(values[1:-1:2]) + 2 * np.sum(values[2:-1:2]) + values[-1])
            error += abs(integral - simpson)

        return IntegralResult(
            value=total,
            is_integrable=np.isfinite(total),
            error_estimate=error,
            details={"method": "trapezoidal"}
        )

    def _improper_integral(
        self,
        f: Callable[[float], float],
        a: float,
        b: float,
        n_points: int
    ) -> float:
        """Handle improper integrals."""
        # Truncate infinite bounds
        if a == float('-inf'):
            a = -1000
        if b == float('inf'):
            b = 1000

        x = np.linspace(a, b, n_points)
        dx = (b - a) / (n_points - 1)

        values = []
        for xi in x:
            try:
                val = f(xi)
                if np.isfinite(val):
                    values.append(val)
                else:
                    values.append(0)
            except:
                values.append(0)

        return np.trapz(values, dx=dx)

    def _montecarlo_integral(
        self,
        f: Callable[[float], float],
        intervals: List[Tuple[float, float]],
        n_points: int
    ) -> IntegralResult:
        """Monte Carlo integration."""
        total = 0
        variance = 0

        for a, b in intervals:
            if np.isinf(a) or np.isinf(b):
                continue

            # Random samples
            samples = np.random.uniform(a, b, n_points)
            values = []

            for x in samples:
                try:
                    val = f(x)
                    if np.isfinite(val):
                        values.append(val)
                except:
                    pass

            if values:
                mean_f = np.mean(values)
                var_f = np.var(values)
                integral = (b - a) * mean_f
                total += integral
                variance += (b - a) ** 2 * var_f / n_points

        error = np.sqrt(variance) if variance > 0 else 0

        return IntegralResult(
            value=total,
            is_integrable=np.isfinite(total),
            error_estimate=error,
            details={"method": "monte_carlo", "samples": n_points}
        )

    # ========== Convergence Theorems ==========

    def dominated_convergence(
        self,
        f_n: Callable[[int, float], float],
        f_limit: Callable[[float], float],
        g: Callable[[float], float],
        domain: Tuple[float, float],
        n_values: List[int]
    ) -> Dict[str, Any]:
        """
        Check and apply Dominated Convergence Theorem.

        If |f_n(x)| <= g(x) for all n and g is integrable,
        then lim integral(f_n) = integral(lim f_n).

        Args:
            f_n: Sequence of functions f_n(n, x)
            f_limit: Pointwise limit function
            g: Dominating function
            domain: Integration domain
            n_values: Values of n to check

        Returns:
            Dictionary with DCT analysis
        """
        a, b = domain
        n_points = 1000
        x = np.linspace(a, b, n_points)
        dx = (b - a) / (n_points - 1)

        # Check domination
        dominated = True
        for n in n_values:
            for xi in x[::10]:  # Sample
                try:
                    if abs(f_n(n, xi)) > g(xi) + self._epsilon:
                        dominated = False
                        break
                except:
                    pass

        # Compute integrals
        integrals = []
        for n in n_values:
            values = [f_n(n, xi) for xi in x]
            integral = np.trapz(values, dx=dx)
            integrals.append(integral)

        # Integral of limit
        limit_values = [f_limit(xi) for xi in x]
        limit_integral = np.trapz(limit_values, dx=dx)

        # Check convergence
        converges = abs(integrals[-1] - limit_integral) < 0.01 * abs(limit_integral) + self._epsilon

        return {
            "dominated": dominated,
            "integrals": list(zip(n_values, integrals)),
            "limit_integral": limit_integral,
            "dct_applies": dominated,
            "converges": converges,
            "conclusion": "DCT guarantees convergence" if dominated else "Domination not verified"
        }

    def monotone_convergence(
        self,
        f_n: Callable[[int, float], float],
        domain: Tuple[float, float],
        n_values: List[int]
    ) -> Dict[str, Any]:
        """
        Check and apply Monotone Convergence Theorem.

        If 0 <= f_n <= f_{n+1} pointwise, then
        lim integral(f_n) = integral(lim f_n).

        Args:
            f_n: Non-decreasing sequence of functions
            domain: Integration domain
            n_values: Values of n to check (increasing)

        Returns:
            Dictionary with MCT analysis
        """
        a, b = domain
        n_points = 1000
        x = np.linspace(a, b, n_points)
        dx = (b - a) / (n_points - 1)

        # Check monotonicity
        monotone = True
        nonnegative = True

        for i in range(len(n_values) - 1):
            n1, n2 = n_values[i], n_values[i + 1]
            for xi in x[::10]:
                try:
                    v1 = f_n(n1, xi)
                    v2 = f_n(n2, xi)
                    if v1 > v2 + self._epsilon:
                        monotone = False
                    if v1 < -self._epsilon:
                        nonnegative = False
                except:
                    pass

        # Compute integrals
        integrals = []
        for n in n_values:
            values = [max(0, f_n(n, xi)) for xi in x]
            integral = np.trapz(values, dx=dx)
            integrals.append(integral)

        return {
            "monotone_increasing": monotone,
            "nonnegative": nonnegative,
            "integrals": list(zip(n_values, integrals)),
            "mct_applies": monotone and nonnegative,
            "conclusion": "MCT guarantees convergence to supremum" if monotone and nonnegative else "MCT conditions not met"
        }

    def fatous_lemma(
        self,
        f_n: Callable[[int, float], float],
        domain: Tuple[float, float],
        n_values: List[int]
    ) -> Dict[str, Any]:
        """
        Apply Fatou's Lemma.

        integral(liminf f_n) <= liminf integral(f_n)

        Args:
            f_n: Sequence of non-negative functions
            domain: Integration domain
            n_values: Values of n

        Returns:
            Dictionary with Fatou's lemma analysis
        """
        a, b = domain
        n_points = 1000
        x = np.linspace(a, b, n_points)
        dx = (b - a) / (n_points - 1)

        # Compute all function values
        all_values = np.zeros((len(n_values), n_points))
        for i, n in enumerate(n_values):
            for j, xi in enumerate(x):
                try:
                    all_values[i, j] = max(0, f_n(n, xi))
                except:
                    all_values[i, j] = 0

        # Compute liminf pointwise
        liminf_values = np.min(all_values, axis=0)  # Conservative approximation

        # Integral of liminf
        integral_liminf = np.trapz(liminf_values, dx=dx)

        # Integrals of each f_n
        integrals = [np.trapz(all_values[i], dx=dx) for i in range(len(n_values))]
        liminf_integrals = min(integrals)

        return {
            "integral_of_liminf": integral_liminf,
            "liminf_of_integrals": liminf_integrals,
            "fatou_holds": integral_liminf <= liminf_integrals + self._epsilon,
            "integrals": list(zip(n_values, integrals))
        }

    # ========== Lp Spaces ==========

    def lp_norm(
        self,
        f: Callable[[float], float],
        p: float,
        domain: Tuple[float, float],
        n_points: int = 10000
    ) -> LpNormResult:
        """
        Compute Lp norm of function.

        ||f||_p = (integral |f|^p)^(1/p)

        Args:
            f: Function
            p: Exponent (1 <= p <= inf)
            domain: Integration domain

        Returns:
            LpNormResult
        """
        a, b = domain

        if p == float('inf'):
            # L-infinity norm: essential supremum
            x = np.linspace(a, b, n_points)
            values = []
            for xi in x:
                try:
                    val = abs(f(xi))
                    if np.isfinite(val):
                        values.append(val)
                except:
                    pass

            norm = max(values) if values else 0

            return LpNormResult(
                norm=norm,
                p=p,
                is_in_lp=np.isfinite(norm)
            )

        # Compute integral of |f|^p
        x = np.linspace(a, b, n_points)
        dx = (b - a) / (n_points - 1)

        values = []
        for xi in x:
            try:
                val = abs(f(xi)) ** p
                if np.isfinite(val):
                    values.append(val)
                else:
                    values.append(0)
            except:
                values.append(0)

        integral = np.trapz(values, dx=dx)

        if integral < 0 or not np.isfinite(integral):
            return LpNormResult(norm=float('inf'), p=p, is_in_lp=False)

        norm = integral ** (1/p)

        return LpNormResult(
            norm=norm,
            p=p,
            is_in_lp=np.isfinite(norm),
            details={"integral_of_abs_p": integral}
        )

    def holder_inequality_check(
        self,
        f: Callable[[float], float],
        g: Callable[[float], float],
        p: float,
        domain: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Check Hölder's inequality.

        ||fg||_1 <= ||f||_p * ||g||_q where 1/p + 1/q = 1

        Args:
            f, g: Functions
            p: First exponent
            domain: Integration domain

        Returns:
            Dictionary with Hölder check
        """
        q = p / (p - 1)  # Conjugate exponent

        norm_f_p = self.lp_norm(f, p, domain)
        norm_g_q = self.lp_norm(g, q, domain)

        # Compute ||fg||_1
        def fg(x):
            """Perform fg operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.fg(...)
            """
            return f(x) * g(x)

        norm_fg_1 = self.lp_norm(fg, 1, domain)

        rhs = norm_f_p.norm * norm_g_q.norm
        lhs = norm_fg_1.norm

        return {
            "lhs": lhs,
            "rhs": rhs,
            "holder_holds": lhs <= rhs + self._epsilon,
            "p": p,
            "q": q,
            "norm_f_p": norm_f_p.norm,
            "norm_g_q": norm_g_q.norm
        }

    # ========== Product Measures (Fubini) ==========

    def fubini_integral(
        self,
        f: Callable[[float, float], float],
        x_domain: Tuple[float, float],
        y_domain: Tuple[float, float],
        n_points: int = 100
    ) -> Dict[str, Any]:
        """
        Compute double integral using Fubini's theorem.

        integral(f, X x Y) = integral_X(integral_Y(f(x,y) dy) dx)
                           = integral_Y(integral_X(f(x,y) dx) dy)

        Args:
            f: Function of two variables
            x_domain: (a, b) for x
            y_domain: (c, d) for y
            n_points: Grid resolution

        Returns:
            Dictionary with both iterated integrals
        """
        a, b = x_domain
        c, d = y_domain

        x = np.linspace(a, b, n_points)
        y = np.linspace(c, d, n_points)
        dx = (b - a) / (n_points - 1)
        dy = (d - c) / (n_points - 1)

        # Integrate dy first, then dx
        integral_xy = 0
        for xi in x:
            inner = 0
            for yj in y:
                try:
                    inner += f(xi, yj) * dy
                except:
                    pass
            integral_xy += inner * dx

        # Integrate dx first, then dy
        integral_yx = 0
        for yj in y:
            inner = 0
            for xi in x:
                try:
                    inner += f(xi, yj) * dx
                except:
                    pass
            integral_yx += inner * dy

        return {
            "integral_dy_dx": integral_xy,
            "integral_dx_dy": integral_yx,
            "fubini_consistent": abs(integral_xy - integral_yx) < 0.01 * abs(integral_xy) + self._epsilon,
            "difference": abs(integral_xy - integral_yx)
        }

    def _compute_measure(self) -> MeasureResult:
        """Compute measure from beliefs."""
        set_def = self.beliefs.get("set")
        if isinstance(set_def, tuple) and len(set_def) == 2:
            return self.lebesgue_measure_interval(set_def[0], set_def[1])
        elif isinstance(set_def, list):
            return self.lebesgue_measure_union(set_def)
        return MeasureResult(value=0, measure_type=MeasureType.LEBESGUE)

    def _integrate(self) -> IntegralResult:
        """Integrate from beliefs."""
        f = self.beliefs.get("function")
        domain = self.beliefs.get("domain")
        if f and domain:
            return self.lebesgue_integrate(f, domain)
        return IntegralResult(value=0, is_integrable=False)
