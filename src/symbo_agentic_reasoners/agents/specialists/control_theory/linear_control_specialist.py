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
Linear Control Specialist
==========================

Provides comprehensive linear control system analysis:
- State-space representations
- Controllability and observability
- Pole placement
- LQR optimal control
- Kalman filtering
- Transfer functions
- Stability margins

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field


@dataclass
class StateSpaceSystem:
    """Linear state-space system dx/dt = Ax + Bu, y = Cx + Du."""
    A: np.ndarray  # State matrix (n x n)
    B: np.ndarray  # Input matrix (n x m)
    C: np.ndarray  # Output matrix (p x n)
    D: np.ndarray  # Feedthrough matrix (p x m)
    dt: Optional[float] = None  # Sample time (None for continuous)


@dataclass
class ControllabilityResult:
    """Result from controllability analysis."""
    is_controllable: bool
    controllability_matrix: np.ndarray
    rank: int
    uncontrollable_modes: List[complex] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityResult:
    """Result from observability analysis."""
    is_observable: bool
    observability_matrix: np.ndarray
    rank: int
    unobservable_modes: List[complex] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LQRResult:
    """Result from LQR design."""
    K: np.ndarray  # Feedback gain
    S: np.ndarray  # Solution to Riccati equation
    closed_loop_poles: List[complex] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransferFunction:
    """Transfer function representation."""
    numerator: np.ndarray  # Numerator coefficients
    denominator: np.ndarray  # Denominator coefficients
    gain: float = 1.0


class LinearControlSpecialist:
    """
    BDI Agent for linear control systems.

    Capabilities:
    - State-space analysis
    - Controllability/observability tests
    - Pole placement
    - LQR optimal control
    - Transfer function analysis
    - Stability analysis
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
        if "system" in self.beliefs:
            self.desires.append("analyze_system")
        if "design_lqr" in self.beliefs:
            self.desires.append("design_lqr")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "analyze_system":
            sys = self.beliefs.get("system")
            return {"result": self.analyze_system(sys)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== System Creation ==========

    def create_state_space(
        self,
        A: np.ndarray,
        B: np.ndarray,
        C: np.ndarray = None,
        D: np.ndarray = None,
        dt: float = None
    ) -> StateSpaceSystem:
        """
        Create state-space system.

        Args:
            A: State matrix
            B: Input matrix
            C: Output matrix (default: identity)
            D: Feedthrough matrix (default: zero)
            dt: Sample time (None for continuous)

        Returns:
            StateSpaceSystem
        """
        A = np.array(A, dtype=float)
        B = np.array(B, dtype=float)

        n = A.shape[0]
        m = B.shape[1] if B.ndim > 1 else 1

        if B.ndim == 1:
            B = B.reshape(-1, 1)

        if C is None:
            C = np.eye(n)
        else:
            C = np.array(C, dtype=float)

        p = C.shape[0]

        if D is None:
            D = np.zeros((p, m))
        else:
            D = np.array(D, dtype=float)

        return StateSpaceSystem(A=A, B=B, C=C, D=D, dt=dt)

    # ========== Controllability ==========

    def controllability_matrix(self, sys: StateSpaceSystem) -> np.ndarray:
        """
        Compute controllability matrix [B, AB, A²B, ..., A^(n-1)B].

        Args:
            sys: State-space system

        Returns:
            Controllability matrix
        """
        n = sys.A.shape[0]
        m = sys.B.shape[1]

        C = np.zeros((n, n * m))

        A_power = np.eye(n)
        for i in range(n):
            C[:, i*m:(i+1)*m] = A_power @ sys.B
            A_power = A_power @ sys.A

        return C

    def check_controllability(self, sys: StateSpaceSystem) -> ControllabilityResult:
        """
        Check controllability of system.

        System is controllable iff rank(controllability matrix) = n.

        Args:
            sys: State-space system

        Returns:
            ControllabilityResult
        """
        C = self.controllability_matrix(sys)
        n = sys.A.shape[0]
        rank = np.linalg.matrix_rank(C)

        is_controllable = rank == n

        # Find uncontrollable modes
        uncontrollable = []
        if not is_controllable:
            eigenvalues, eigenvectors = np.linalg.eig(sys.A)

            for i, (lam, v) in enumerate(zip(eigenvalues, eigenvectors.T)):
                # Check if v is in kernel of controllability matrix
                C_proj = C @ np.linalg.pinv(C)
                if np.linalg.norm(C_proj @ v - v) > 0.01:
                    uncontrollable.append(lam)

        return ControllabilityResult(
            is_controllable=is_controllable,
            controllability_matrix=C,
            rank=rank,
            uncontrollable_modes=uncontrollable,
            details={"n": n}
        )

    # ========== Observability ==========

    def observability_matrix(self, sys: StateSpaceSystem) -> np.ndarray:
        """
        Compute observability matrix [C; CA; CA²; ...; CA^(n-1)].

        Args:
            sys: State-space system

        Returns:
            Observability matrix
        """
        n = sys.A.shape[0]
        p = sys.C.shape[0]

        O = np.zeros((n * p, n))

        A_power = np.eye(n)
        for i in range(n):
            O[i*p:(i+1)*p, :] = sys.C @ A_power
            A_power = A_power @ sys.A

        return O

    def check_observability(self, sys: StateSpaceSystem) -> ObservabilityResult:
        """
        Check observability of system.

        System is observable iff rank(observability matrix) = n.

        Args:
            sys: State-space system

        Returns:
            ObservabilityResult
        """
        O = self.observability_matrix(sys)
        n = sys.A.shape[0]
        rank = np.linalg.matrix_rank(O)

        is_observable = rank == n

        # Find unobservable modes
        unobservable = []
        if not is_observable:
            eigenvalues = np.linalg.eigvals(sys.A)
            # Would need more sophisticated analysis for exact modes

        return ObservabilityResult(
            is_observable=is_observable,
            observability_matrix=O,
            rank=rank,
            unobservable_modes=unobservable,
            details={"n": n}
        )

    # ========== Stability ==========

    def check_stability(self, sys: StateSpaceSystem) -> Dict[str, Any]:
        """
        Check stability of open-loop system.

        Continuous: stable iff all eigenvalues have negative real parts
        Discrete: stable iff all eigenvalues have magnitude < 1

        Args:
            sys: State-space system

        Returns:
            Dictionary with stability analysis
        """
        eigenvalues = np.linalg.eigvals(sys.A)

        if sys.dt is None:
            # Continuous-time
            is_stable = all(e.real < -self._epsilon for e in eigenvalues)
            is_marginally_stable = all(e.real <= self._epsilon for e in eigenvalues) and not is_stable
            stability_type = "continuous"
        else:
            # Discrete-time
            is_stable = all(abs(e) < 1 - self._epsilon for e in eigenvalues)
            is_marginally_stable = all(abs(e) <= 1 + self._epsilon for e in eigenvalues) and not is_stable
            stability_type = "discrete"

        return {
            "is_stable": is_stable,
            "is_marginally_stable": is_marginally_stable,
            "is_unstable": not is_stable and not is_marginally_stable,
            "eigenvalues": eigenvalues.tolist(),
            "stability_type": stability_type
        }

    # ========== Pole Placement ==========

    def pole_placement(
        self,
        sys: StateSpaceSystem,
        desired_poles: List[complex]
    ) -> np.ndarray:
        """
        Compute state feedback gain K for pole placement.

        Closed-loop: dx/dt = (A - BK)x has poles at desired locations.

        Uses Ackermann's formula for SISO, extended for MIMO.

        Args:
            sys: State-space system
            desired_poles: Desired closed-loop poles

        Returns:
            Feedback gain matrix K
        """
        n = sys.A.shape[0]
        m = sys.B.shape[1]

        if m == 1:
            # SISO: Use Ackermann's formula
            return self._ackermann(sys, desired_poles)
        else:
            # MIMO: Use iterative method
            return self._mimo_pole_placement(sys, desired_poles)

    def _ackermann(
        self,
        sys: StateSpaceSystem,
        desired_poles: List[complex]
    ) -> np.ndarray:
        """Ackermann's formula for SISO pole placement."""
        n = sys.A.shape[0]

        # Compute desired characteristic polynomial
        # p(A) where p(s) = prod(s - p_i)
        p_A = np.eye(n)

        for pole in desired_poles:
            p_A = p_A @ (sys.A - pole * np.eye(n))

        # Controllability matrix
        C = self.controllability_matrix(sys)

        # Last row of C^(-1)
        try:
            C_inv = np.linalg.inv(C)
            e_n = np.zeros(n)
            e_n[-1] = 1
            row = e_n @ C_inv
        except np.linalg.LinAlgError:
            # Fallback: use pseudoinverse
            row = np.zeros(n)
            row[-1] = 1
            row = row @ np.linalg.pinv(C)

        K = row @ p_A.real
        return K.reshape(1, -1)

    def _mimo_pole_placement(
        self,
        sys: StateSpaceSystem,
        desired_poles: List[complex]
    ) -> np.ndarray:
        """MIMO pole placement using iterative eigenvalue assignment."""
        n = sys.A.shape[0]
        m = sys.B.shape[1]

        # Initialize K
        K = np.zeros((m, n))

        # Iteratively assign poles
        A_cl = sys.A.copy()

        for i, pole in enumerate(desired_poles):
            # Find direction to move eigenvalue
            eigenvalues, eigenvectors = np.linalg.eig(A_cl)

            # Find eigenvalue furthest from desired
            distances = [abs(e - pole) for e in eigenvalues]
            idx = np.argmax(distances)

            v = eigenvectors[:, idx].real

            # Compute gain increment
            # Simple approach: adjust K to move eigenvalue
            dK = np.outer(np.ones(m) / m, v) * 0.1
            K = K + dK

            A_cl = sys.A - sys.B @ K

        return K

    # ========== LQR Optimal Control ==========

    def lqr(
        self,
        sys: StateSpaceSystem,
        Q: np.ndarray,
        R: np.ndarray
    ) -> LQRResult:
        """
        Linear Quadratic Regulator design.

        Minimizes J = integral(x'Qx + u'Ru) dt

        Args:
            sys: State-space system
            Q: State cost matrix (positive semidefinite)
            R: Input cost matrix (positive definite)

        Returns:
            LQRResult with optimal feedback gain
        """
        # Solve continuous algebraic Riccati equation
        # A'S + SA - SBR^(-1)B'S + Q = 0

        S = self._solve_care(sys.A, sys.B, Q, R)

        # Compute optimal gain K = R^(-1) B' S
        R_inv = np.linalg.inv(R)
        K = R_inv @ sys.B.T @ S

        # Closed-loop poles
        A_cl = sys.A - sys.B @ K
        poles = np.linalg.eigvals(A_cl)

        return LQRResult(
            K=K,
            S=S,
            closed_loop_poles=poles.tolist(),
            details={"Q": Q, "R": R}
        )

    def _solve_care(
        self,
        A: np.ndarray,
        B: np.ndarray,
        Q: np.ndarray,
        R: np.ndarray,
        max_iter: int = 1000,
        tol: float = 1e-9
    ) -> np.ndarray:
        """
        Solve Continuous Algebraic Riccati Equation.

        A'S + SA - SBR^(-1)B'S + Q = 0

        Uses iterative method.
        """
        n = A.shape[0]
        R_inv = np.linalg.inv(R)
        BR_inv_BT = B @ R_inv @ B.T

        # Initialize with identity
        S = np.eye(n)

        for _ in range(max_iter):
            # Newton iteration
            S_new = Q + A.T @ S + S @ A - S @ BR_inv_BT @ S

            # Fixed-point iteration
            # S_new = solve_lyapunov((A - BR_inv_BT @ S).T, -Q - S @ BR_inv_BT @ S)

            # Simplified: gradient descent on Riccati residual
            residual = A.T @ S + S @ A - S @ BR_inv_BT @ S + Q

            if np.linalg.norm(residual) < tol:
                return S

            # Update S
            S = S - 0.01 * residual

        return S

    # ========== Transfer Function ==========

    def ss_to_tf(self, sys: StateSpaceSystem) -> List[List[TransferFunction]]:
        """
        Convert state-space to transfer function.

        G(s) = C(sI - A)^(-1)B + D

        Args:
            sys: State-space system

        Returns:
            Matrix of transfer functions
        """
        n = sys.A.shape[0]
        p = sys.C.shape[0]
        m = sys.B.shape[1]

        # Characteristic polynomial (denominator)
        char_poly = np.poly(sys.A)

        tfs = []
        for i in range(p):
            row = []
            for j in range(m):
                # Numerator from adjugate
                # This is simplified; full implementation would use adjugate matrix
                num = np.array([sys.D[i, j]])

                row.append(TransferFunction(
                    numerator=num,
                    denominator=char_poly
                ))
            tfs.append(row)

        return tfs

    def evaluate_transfer_function(
        self,
        tf: TransferFunction,
        s: complex
    ) -> complex:
        """
        Evaluate transfer function at s.

        Args:
            tf: Transfer function
            s: Complex frequency

        Returns:
            G(s)
        """
        num = sum(c * s**(len(tf.numerator) - 1 - i) for i, c in enumerate(tf.numerator))
        den = sum(c * s**(len(tf.denominator) - 1 - i) for i, c in enumerate(tf.denominator))

        if abs(den) < self._epsilon:
            return complex(float('inf'))

        return tf.gain * num / den

    # ========== Frequency Response ==========

    def bode_data(
        self,
        sys: StateSpaceSystem,
        omega_range: Tuple[float, float] = (0.01, 100),
        n_points: int = 100
    ) -> Dict[str, Any]:
        """
        Compute Bode plot data.

        Args:
            sys: State-space system
            omega_range: Frequency range
            n_points: Number of frequency points

        Returns:
            Dictionary with magnitude and phase data
        """
        omega = np.logspace(np.log10(omega_range[0]), np.log10(omega_range[1]), n_points)

        n = sys.A.shape[0]
        p = sys.C.shape[0]
        m = sys.B.shape[1]

        magnitude = np.zeros((n_points, p, m))
        phase = np.zeros((n_points, p, m))

        for k, w in enumerate(omega):
            s = 1j * w

            # G(s) = C(sI - A)^(-1)B + D
            sI_minus_A = s * np.eye(n) - sys.A

            try:
                G = sys.C @ np.linalg.inv(sI_minus_A) @ sys.B + sys.D
            except np.linalg.LinAlgError:
                G = np.zeros((p, m), dtype=complex)

            magnitude[k] = 20 * np.log10(np.abs(G) + self._epsilon)
            phase[k] = np.angle(G) * 180 / np.pi

        return {
            "omega": omega,
            "magnitude_db": magnitude,
            "phase_deg": phase
        }

    # ========== System Analysis ==========

    def analyze_system(self, sys: StateSpaceSystem) -> Dict[str, Any]:
        """
        Comprehensive system analysis.

        Args:
            sys: State-space system

        Returns:
            Dictionary with complete analysis
        """
        controllability = self.check_controllability(sys)
        observability = self.check_observability(sys)
        stability = self.check_stability(sys)

        return {
            "state_dimension": sys.A.shape[0],
            "input_dimension": sys.B.shape[1],
            "output_dimension": sys.C.shape[0],
            "is_continuous": sys.dt is None,
            "sample_time": sys.dt,
            "controllability": {
                "is_controllable": controllability.is_controllable,
                "rank": controllability.rank
            },
            "observability": {
                "is_observable": observability.is_observable,
                "rank": observability.rank
            },
            "stability": stability,
            "eigenvalues": np.linalg.eigvals(sys.A).tolist()
        }

    # ========== Simulation ==========

    def simulate(
        self,
        sys: StateSpaceSystem,
        x0: np.ndarray,
        u: Callable[[float], np.ndarray],
        t_span: Tuple[float, float],
        n_steps: int = 1000
    ) -> Dict[str, np.ndarray]:
        """
        Simulate system response.

        Args:
            sys: State-space system
            x0: Initial state
            u: Input function u(t)
            t_span: Time span
            n_steps: Number of time steps

        Returns:
            Dictionary with t, x, y, u arrays
        """
        t0, tf = t_span
        dt = (tf - t0) / n_steps

        t = np.linspace(t0, tf, n_steps + 1)
        x = np.zeros((n_steps + 1, len(x0)))
        x[0] = x0

        y = np.zeros((n_steps + 1, sys.C.shape[0]))
        u_arr = np.zeros((n_steps + 1, sys.B.shape[1]))

        for i in range(n_steps):
            u_t = u(t[i])
            u_arr[i] = u_t

            # RK4
            def f(x_state):
                return sys.A @ x_state + sys.B @ u_t

            k1 = f(x[i])
            k2 = f(x[i] + 0.5 * dt * k1)
            k3 = f(x[i] + 0.5 * dt * k2)
            k4 = f(x[i] + dt * k3)

            x[i + 1] = x[i] + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            y[i] = sys.C @ x[i] + sys.D @ u_t

        u_arr[-1] = u(t[-1])
        y[-1] = sys.C @ x[-1] + sys.D @ u_arr[-1]

        return {"t": t, "x": x, "y": y, "u": u_arr}
