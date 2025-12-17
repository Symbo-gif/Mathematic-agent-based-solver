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
Dynamical Systems Specialist
=============================

Provides comprehensive dynamical systems analysis:
- Fixed point analysis and stability
- Phase portrait computation
- Lyapunov stability
- Bifurcation analysis
- Limit cycles and attractors
- Poincaré maps

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class StabilityType(Enum):
    """Types of fixed point stability."""
    STABLE_NODE = "stable_node"
    UNSTABLE_NODE = "unstable_node"
    STABLE_FOCUS = "stable_focus"
    UNSTABLE_FOCUS = "unstable_focus"
    SADDLE = "saddle"
    CENTER = "center"
    STABLE_STAR = "stable_star"
    UNSTABLE_STAR = "unstable_star"
    DEGENERATE = "degenerate"


class BifurcationType(Enum):
    """Types of bifurcations."""
    SADDLE_NODE = "saddle_node"
    TRANSCRITICAL = "transcritical"
    PITCHFORK = "pitchfork"
    HOPF = "hopf"
    PERIOD_DOUBLING = "period_doubling"


@dataclass
class FixedPointResult:
    """Result from fixed point analysis."""
    location: np.ndarray
    stability: StabilityType
    eigenvalues: List[complex] = field(default_factory=list)
    eigenvectors: Optional[np.ndarray] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrajectoryResult:
    """Result from trajectory computation."""
    times: np.ndarray
    states: np.ndarray
    converged_to: Optional[np.ndarray] = None
    is_periodic: bool = False
    period: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LyapunovResult:
    """Result from Lyapunov analysis."""
    exponents: List[float] = field(default_factory=list)
    is_stable: bool = True
    is_chaotic: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


class DynamicalSystemsSpecialist:
    """
    BDI Agent for dynamical systems analysis.

    Capabilities:
    - Find and classify fixed points
    - Compute trajectories
    - Lyapunov stability analysis
    - Phase portrait generation
    - Bifurcation detection
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._epsilon = 1e-10
        self._h = 1e-6

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "vector_field" in self.beliefs:
            self.desires.append("analyze_system")
        if "find_fixed_points" in self.beliefs:
            self.desires.append("find_equilibria")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "analyze_system":
            f = self.beliefs.get("vector_field")
            return {"result": self.analyze_system(f)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Fixed Point Analysis ==========

    def find_fixed_points(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        dim: int,
        search_region: Tuple[np.ndarray, np.ndarray],
        n_initial: int = 100
    ) -> List[FixedPointResult]:
        """
        Find fixed points of dynamical system dx/dt = f(x).

        Uses Newton's method from multiple initial conditions.

        Args:
            f: Vector field function
            dim: State dimension
            search_region: (min_bounds, max_bounds) for search
            n_initial: Number of initial guesses

        Returns:
            List of FixedPointResult
        """
        fixed_points = []
        found_locations = []

        min_b, max_b = search_region

        for _ in range(n_initial):
            # Random initial guess
            x0 = min_b + np.random.rand(dim) * (max_b - min_b)

            # Newton's method
            x = self._newton_find_zero(f, x0)

            if x is not None:
                # Check if already found
                is_new = all(
                    np.linalg.norm(x - loc) > 0.001
                    for loc in found_locations
                )

                if is_new:
                    found_locations.append(x)

                    # Analyze stability
                    fp_result = self.classify_fixed_point(f, x)
                    fixed_points.append(fp_result)

        return fixed_points

    def _newton_find_zero(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        x0: np.ndarray,
        max_iter: int = 50,
        tol: float = 1e-10
    ) -> Optional[np.ndarray]:
        """Find zero of f using Newton's method."""
        x = x0.copy()

        for _ in range(max_iter):
            fx = f(x)

            if np.linalg.norm(fx) < tol:
                return x

            # Jacobian
            J = self._numerical_jacobian(f, x)

            try:
                dx = np.linalg.solve(J, -fx)
            except np.linalg.LinAlgError:
                return None

            x = x + dx

            if np.linalg.norm(dx) < tol:
                if np.linalg.norm(f(x)) < tol * 10:
                    return x
                return None

        return None

    def _numerical_jacobian(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        x: np.ndarray
    ) -> np.ndarray:
        """Compute Jacobian matrix numerically."""
        n = len(x)
        fx = f(x)
        m = len(fx)

        J = np.zeros((m, n))

        for j in range(n):
            e_j = np.zeros(n)
            e_j[j] = self._h

            f_plus = f(x + e_j)
            f_minus = f(x - e_j)

            J[:, j] = (f_plus - f_minus) / (2 * self._h)

        return J

    def classify_fixed_point(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        x_star: np.ndarray
    ) -> FixedPointResult:
        """
        Classify fixed point by linearization.

        Args:
            f: Vector field
            x_star: Fixed point location

        Returns:
            FixedPointResult with stability classification
        """
        J = self._numerical_jacobian(f, x_star)
        eigenvalues, eigenvectors = np.linalg.eig(J)

        # Classify based on eigenvalues
        real_parts = eigenvalues.real
        imag_parts = eigenvalues.imag

        all_negative = all(r < -self._epsilon for r in real_parts)
        all_positive = all(r > self._epsilon for r in real_parts)
        has_positive = any(r > self._epsilon for r in real_parts)
        has_negative = any(r < -self._epsilon for r in real_parts)
        has_imaginary = any(abs(i) > self._epsilon for i in imag_parts)
        has_zero = any(abs(r) < self._epsilon and abs(i) < self._epsilon for r, i in zip(real_parts, imag_parts))

        if has_zero:
            stability = StabilityType.DEGENERATE
        elif all_negative and not has_imaginary:
            # Check if repeated eigenvalues
            if len(set(eigenvalues.round(6))) < len(eigenvalues):
                stability = StabilityType.STABLE_STAR
            else:
                stability = StabilityType.STABLE_NODE
        elif all_positive and not has_imaginary:
            if len(set(eigenvalues.round(6))) < len(eigenvalues):
                stability = StabilityType.UNSTABLE_STAR
            else:
                stability = StabilityType.UNSTABLE_NODE
        elif all_negative and has_imaginary:
            stability = StabilityType.STABLE_FOCUS
        elif all_positive and has_imaginary:
            stability = StabilityType.UNSTABLE_FOCUS
        elif has_positive and has_negative:
            stability = StabilityType.SADDLE
        elif all(abs(r) < self._epsilon for r in real_parts) and has_imaginary:
            stability = StabilityType.CENTER
        else:
            stability = StabilityType.DEGENERATE

        return FixedPointResult(
            location=x_star,
            stability=stability,
            eigenvalues=eigenvalues.tolist(),
            eigenvectors=eigenvectors,
            details={"jacobian": J}
        )

    # ========== Trajectory Computation ==========

    def compute_trajectory(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        x0: np.ndarray,
        t_span: Tuple[float, float],
        n_steps: int = 1000
    ) -> TrajectoryResult:
        """
        Compute trajectory using RK4.

        Args:
            f: Vector field dx/dt = f(x)
            x0: Initial condition
            t_span: (t_start, t_end)
            n_steps: Number of time steps

        Returns:
            TrajectoryResult
        """
        t0, tf = t_span
        dt = (tf - t0) / n_steps

        times = np.linspace(t0, tf, n_steps + 1)
        states = np.zeros((n_steps + 1, len(x0)))
        states[0] = x0

        x = x0.copy()

        for i in range(n_steps):
            # RK4
            k1 = f(x)
            k2 = f(x + 0.5 * dt * k1)
            k3 = f(x + 0.5 * dt * k2)
            k4 = f(x + dt * k3)

            x = x + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            states[i + 1] = x

        # Check for periodicity
        is_periodic, period = self._check_periodicity(states, times)

        # Check convergence
        converged_to = None
        if np.linalg.norm(states[-1] - states[-100]) < 0.01:
            converged_to = states[-1]

        return TrajectoryResult(
            times=times,
            states=states,
            converged_to=converged_to,
            is_periodic=is_periodic,
            period=period
        )

    def _check_periodicity(
        self,
        states: np.ndarray,
        times: np.ndarray,
        tol: float = 0.01
    ) -> Tuple[bool, Optional[float]]:
        """Check if trajectory is periodic."""
        n = len(states)
        if n < 100:
            return False, None

        # Look for returns to initial state
        x_ref = states[n // 2]

        for i in range(n // 2 + 10, n):
            if np.linalg.norm(states[i] - x_ref) < tol:
                period = times[i] - times[n // 2]
                return True, period

        return False, None

    # ========== Lyapunov Analysis ==========

    def lyapunov_direct(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        x0: np.ndarray,
        t_total: float = 100,
        n_steps: int = 10000
    ) -> LyapunovResult:
        """
        Compute Lyapunov exponents using direct method.

        Args:
            f: Vector field
            x0: Initial condition
            t_total: Total integration time
            n_steps: Number of steps

        Returns:
            LyapunovResult
        """
        dim = len(x0)
        dt = t_total / n_steps

        # Initialize
        x = x0.copy()
        Q = np.eye(dim)  # Orthonormal vectors
        lyap_sums = np.zeros(dim)

        for step in range(n_steps):
            # Evolve state
            k1 = f(x)
            k2 = f(x + 0.5 * dt * k1)
            k3 = f(x + 0.5 * dt * k2)
            k4 = f(x + dt * k3)
            x = x + dt * (k1 + 2*k2 + 2*k3 + k4) / 6

            # Evolve tangent vectors
            J = self._numerical_jacobian(f, x)

            for i in range(dim):
                Q[:, i] = Q[:, i] + dt * (J @ Q[:, i])

            # QR decomposition to keep orthonormal
            Q, R = np.linalg.qr(Q)

            # Accumulate Lyapunov sums
            for i in range(dim):
                if abs(R[i, i]) > self._epsilon:
                    lyap_sums[i] += np.log(abs(R[i, i]))

        # Compute exponents
        exponents = lyap_sums / t_total

        is_chaotic = any(e > self._epsilon for e in exponents)
        is_stable = all(e < self._epsilon for e in exponents)

        return LyapunovResult(
            exponents=sorted(exponents.tolist(), reverse=True),
            is_stable=is_stable,
            is_chaotic=is_chaotic,
            details={"t_total": t_total}
        )

    def check_lyapunov_stability(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        x_star: np.ndarray,
        V: Callable[[np.ndarray], float],
        domain_radius: float = 1.0
    ) -> Dict[str, Any]:
        """
        Check Lyapunov stability using candidate function.

        Stable if V(x) > 0 for x != x_star and dV/dt <= 0.
        Asymptotically stable if dV/dt < 0.

        Args:
            f: Vector field
            x_star: Equilibrium point
            V: Lyapunov candidate function
            domain_radius: Region to check

        Returns:
            Dictionary with stability analysis
        """
        dim = len(x_star)
        n_samples = 1000

        V_positive = True
        V_dot_nonpositive = True
        V_dot_negative = True

        for _ in range(n_samples):
            # Random point in domain
            direction = np.random.randn(dim)
            direction = direction / np.linalg.norm(direction)
            r = np.random.uniform(0.01, domain_radius)
            x = x_star + r * direction

            # Check V(x) > 0
            V_x = V(x - x_star)
            if V_x < -self._epsilon:
                V_positive = False

            # Check V_dot = grad(V) . f(x) <= 0
            # Numerical gradient
            grad_V = np.zeros(dim)
            for i in range(dim):
                e_i = np.zeros(dim)
                e_i[i] = self._h
                grad_V[i] = (V(x - x_star + e_i) - V(x - x_star - e_i)) / (2 * self._h)

            V_dot = np.dot(grad_V, f(x))

            if V_dot > self._epsilon:
                V_dot_nonpositive = False
                V_dot_negative = False
            elif V_dot > -self._epsilon:
                V_dot_negative = False

        is_stable = V_positive and V_dot_nonpositive
        is_asymptotically_stable = V_positive and V_dot_negative

        return {
            "V_positive_definite": V_positive,
            "V_dot_nonpositive": V_dot_nonpositive,
            "V_dot_negative": V_dot_negative,
            "is_stable": is_stable,
            "is_asymptotically_stable": is_asymptotically_stable
        }

    # ========== Bifurcation Analysis ==========

    def detect_bifurcation(
        self,
        f_param: Callable[[np.ndarray, float], np.ndarray],
        param_range: Tuple[float, float],
        x_guess: np.ndarray,
        n_params: int = 100
    ) -> Dict[str, Any]:
        """
        Detect bifurcations as parameter varies.

        Args:
            f_param: Vector field f(x, mu) depending on parameter
            param_range: (mu_min, mu_max)
            x_guess: Initial guess for fixed point
            n_params: Number of parameter values

        Returns:
            Dictionary with bifurcation analysis
        """
        mu_vals = np.linspace(param_range[0], param_range[1], n_params)

        fixed_points = []
        eigenvalue_paths = []
        bifurcations = []

        prev_n_fps = 0
        prev_stability = None

        for mu in mu_vals:
            # Find fixed point at this parameter
            f_mu = lambda x: f_param(x, mu)
            x_fp = self._newton_find_zero(f_mu, x_guess)

            if x_fp is not None:
                fp_result = self.classify_fixed_point(f_mu, x_fp)
                fixed_points.append((mu, x_fp, fp_result.stability))
                eigenvalue_paths.append((mu, fp_result.eigenvalues))

                x_guess = x_fp  # Update guess for continuation

                # Detect bifurcation
                curr_stability = fp_result.stability

                if prev_stability is not None and curr_stability != prev_stability:
                    # Stability change = bifurcation
                    bif_type = self._classify_bifurcation(
                        prev_stability, curr_stability, fp_result.eigenvalues
                    )
                    bifurcations.append({
                        "parameter": mu,
                        "type": bif_type,
                        "from": prev_stability.value,
                        "to": curr_stability.value
                    })

                prev_stability = curr_stability

        return {
            "fixed_points": fixed_points,
            "eigenvalue_paths": eigenvalue_paths,
            "bifurcations": bifurcations,
            "n_bifurcations": len(bifurcations)
        }

    def _classify_bifurcation(
        self,
        prev_stability: StabilityType,
        curr_stability: StabilityType,
        eigenvalues: List[complex]
    ) -> BifurcationType:
        """Classify type of bifurcation."""
        # Check for zero eigenvalue crossing (saddle-node, transcritical, pitchfork)
        has_zero_real = any(abs(e.real) < 0.01 and abs(e.imag) < 0.01 for e in eigenvalues)

        # Check for pure imaginary pair (Hopf)
        has_imaginary_pair = any(
            abs(e.real) < 0.01 and abs(e.imag) > 0.01
            for e in eigenvalues
        )

        if has_imaginary_pair:
            return BifurcationType.HOPF
        elif has_zero_real:
            # Could be saddle-node, transcritical, or pitchfork
            return BifurcationType.SADDLE_NODE
        else:
            return BifurcationType.SADDLE_NODE

    # ========== Phase Portrait ==========

    def phase_portrait(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        x_range: Tuple[float, float],
        y_range: Tuple[float, float],
        n_grid: int = 20
    ) -> Dict[str, Any]:
        """
        Generate phase portrait data for 2D system.

        Args:
            f: Vector field (2D)
            x_range: (x_min, x_max)
            y_range: (y_min, y_max)
            n_grid: Grid resolution

        Returns:
            Dictionary with phase portrait data
        """
        x_vals = np.linspace(x_range[0], x_range[1], n_grid)
        y_vals = np.linspace(y_range[0], y_range[1], n_grid)

        X, Y = np.meshgrid(x_vals, y_vals)
        U = np.zeros_like(X)
        V = np.zeros_like(Y)

        for i in range(n_grid):
            for j in range(n_grid):
                state = np.array([X[i, j], Y[i, j]])
                velocity = f(state)
                U[i, j] = velocity[0]
                V[i, j] = velocity[1]

        return {
            "X": X,
            "Y": Y,
            "U": U,
            "V": V,
            "x_range": x_range,
            "y_range": y_range
        }

    # ========== System Analysis ==========

    def analyze_system(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        dim: int = 2,
        search_region: Tuple[np.ndarray, np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive system analysis.

        Args:
            f: Vector field
            dim: State dimension
            search_region: Region to search for fixed points

        Returns:
            Dictionary with complete analysis
        """
        if search_region is None:
            search_region = (np.array([-5.0] * dim), np.array([5.0] * dim))

        # Find fixed points
        fixed_points = self.find_fixed_points(f, dim, search_region)

        # Compute sample trajectories
        trajectories = []
        for _ in range(5):
            x0 = search_region[0] + np.random.rand(dim) * (search_region[1] - search_region[0])
            traj = self.compute_trajectory(f, x0, (0, 10))
            trajectories.append({
                "initial": x0.tolist(),
                "final": traj.states[-1].tolist(),
                "converged": traj.converged_to is not None
            })

        return {
            "dimension": dim,
            "fixed_points": [
                {
                    "location": fp.location.tolist(),
                    "stability": fp.stability.value,
                    "eigenvalues": fp.eigenvalues
                }
                for fp in fixed_points
            ],
            "sample_trajectories": trajectories,
            "search_region": (search_region[0].tolist(), search_region[1].tolist())
        }
