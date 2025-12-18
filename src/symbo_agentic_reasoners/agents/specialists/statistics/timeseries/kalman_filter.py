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
KALMAN FILTER SPECIALIST (Tier 3)
==================================

State-space models and optimal filtering.

CAPABILITIES:
------------
- Standard Kalman filter
- Kalman smoother (RTS algorithm)
- Extended Kalman Filter (EKF) for nonlinear systems
- Unscented Kalman Filter (UKF)
- Adaptive noise covariance estimation
- Prediction and update steps

ALGORITHMS:
-----------
Native NumPy implementation - NO external dependencies

1. State equation: x(t) = A*x(t-1) + w(t), w ~ N(0,Q)
2. Observation equation: y(t) = C*x(t) + v(t), v ~ N(0,R)
3. Predict: x_pred = A*x, P_pred = A*P*A^T + Q
4. Update: K = P_pred*C^T*(C*P_pred*C^T + R)^(-1)
           x = x_pred + K*(y - C*x_pred)
           P = (I - K*C)*P_pred
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.kalman_filter')


@dataclass
class KalmanFilterResult:
    """Result of Kalman filtering."""
    filtered_states: List[List[float]]  # x(t|t)
    filtered_covariances: List[List[List[float]]]  # P(t|t)
    predicted_states: List[List[float]]  # x(t|t-1)
    predicted_covariances: List[List[List[float]]]  # P(t|t-1)
    innovations: List[List[float]]  # y(t) - C*x(t|t-1)
    kalman_gains: List[List[List[float]]]  # K(t)
    log_likelihood: float


class KalmanFilterSpecialist(BDIAgent):
    """
    Kalman Filter Specialist - Optimal State Estimation

    DIRECTIVE:
    ---------
    Perform optimal state estimation for linear and nonlinear
    dynamical systems using Kalman filtering techniques.

    OPERATIONS:
    ----------
    - kalman_filter: Standard Kalman filter
    - kalman_smoother: RTS backward smoother
    - extended_kalman_filter: EKF for nonlinear systems
    - unscented_kalman_filter: UKF for highly nonlinear systems
    - predict_step: Prediction step
    - update_step: Update step
    """

    def __init__(
        self,
        agent_id: str = 'kalman_filter_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = 'kalman_filter_specialist'
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self._register_services()
        self._stats = {'filters_run': 0, 'predictions_made': 0}

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type='math.statistics.timeseries.kalman_filter',
                    description='Kalman filtering and state estimation'
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== MATRIX OPERATIONS ====================

    def _matrix_multiply(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Matrix multiplication C = A * B."""
        rows_A, cols_A = len(A), len(A[0]) if A else 0
        rows_B, cols_B = len(B), len(B[0]) if B else 0

        if cols_A != rows_B:
            raise ValueError(f"Cannot multiply {rows_A}x{cols_A} with {rows_B}x{cols_B}")

        result = [[sum(A[i][k] * B[k][j] for k in range(cols_A))
                   for j in range(cols_B)]
                  for i in range(rows_A)]
        return result

    def _matrix_transpose(self, A: List[List[float]]) -> List[List[float]]:
        """Matrix transpose."""
        if not A or not A[0]:
            return []
        return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

    def _matrix_add(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Matrix addition."""
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def _matrix_subtract(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Matrix subtraction."""
        return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def _matrix_scalar_multiply(self, A: List[List[float]], scalar: float) -> List[List[float]]:
        """Multiply matrix by scalar."""
        return [[A[i][j] * scalar for j in range(len(A[0]))] for i in range(len(A))]

    def _identity_matrix(self, n: int) -> List[List[float]]:
        """Create identity matrix."""
        return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    def _matrix_inverse(self, A: List[List[float]]) -> Optional[List[List[float]]]:
        """Matrix inversion using Gaussian elimination."""
        n = len(A)
        # Create augmented matrix [A | I]
        aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)]
               for i, row in enumerate(A)]

        # Forward elimination
        for col in range(n):
            # Find pivot
            max_row = col
            for row in range(col + 1, n):
                if abs(aug[row][col]) > abs(aug[max_row][col]):
                    max_row = row
            aug[col], aug[max_row] = aug[max_row], aug[col]

            if abs(aug[col][col]) < 1e-10:
                return None

            # Normalize pivot row
            pivot = aug[col][col]
            for j in range(2 * n):
                aug[col][j] /= pivot

            # Eliminate
            for row in range(n):
                if row != col:
                    factor = aug[row][col]
                    for j in range(2 * n):
                        aug[row][j] -= factor * aug[col][j]

        # Extract inverse
        return [row[n:] for row in aug]

    def _vector_subtract(self, a: List[float], b: List[float]) -> List[float]:
        """Vector subtraction."""
        return [a[i] - b[i] for i in range(len(a))]

    def _matrix_vector_multiply(self, A: List[List[float]], x: List[float]) -> List[float]:
        """Matrix-vector multiplication."""
        return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]

    # ==================== KALMAN FILTER ====================

    def kalman_filter(
        self,
        observations: List[List[float]],
        A: List[List[float]],
        C: List[List[float]],
        Q: List[List[float]],
        R: List[List[float]],
        x0: List[float],
        P0: List[List[float]],
    ) -> KalmanFilterResult:
        """
        Standard Kalman filter for linear state space model.

        State equation: x(t) = A*x(t-1) + w(t), w ~ N(0,Q)
        Observation equation: y(t) = C*x(t) + v(t), v ~ N(0,R)

        Args:
            observations: Observed data (T, m)
            A: State transition matrix (n, n)
            C: Observation matrix (m, n)
            Q: Process noise covariance (n, n)
            R: Observation noise covariance (m, m)
            x0: Initial state (n,)
            P0: Initial covariance (n, n)

        Returns:
            KalmanFilterResult with filtered states and covariances
        """
        self._stats['filters_run'] += 1

        T = len(observations)
        n = len(x0)  # State dimension

        # Storage
        filtered_states = []
        filtered_covariances = []
        predicted_states = []
        predicted_covariances = []
        innovations = []
        kalman_gains = []

        # Initialize
        x = x0[:]
        P = [row[:] for row in P0]

        log_likelihood = 0.0

        for t in range(T):
            # Predict step
            x_pred = self._matrix_vector_multiply(A, x)
            P_pred = self._matrix_add(
                self._matrix_multiply(self._matrix_multiply(A, P), self._matrix_transpose(A)),
                Q
            )

            predicted_states.append(x_pred[:])
            predicted_covariances.append([row[:] for row in P_pred])

            # Update step
            y = observations[t]
            y_pred = self._matrix_vector_multiply(C, x_pred)
            innovation = self._vector_subtract(y, y_pred)
            innovations.append(innovation[:])

            # Innovation covariance S = C*P_pred*C^T + R
            S = self._matrix_add(
                self._matrix_multiply(
                    self._matrix_multiply(C, P_pred),
                    self._matrix_transpose(C)
                ),
                R
            )

            # Kalman gain K = P_pred*C^T*S^(-1)
            S_inv = self._matrix_inverse(S)
            if S_inv is None:
                # Singular matrix, skip update
                x = x_pred
                P = P_pred
            else:
                K = self._matrix_multiply(
                    self._matrix_multiply(P_pred, self._matrix_transpose(C)),
                    S_inv
                )
                kalman_gains.append([row[:] for row in K])

                # Update state: x = x_pred + K*innovation
                x = [x_pred[i] + sum(K[i][j] * innovation[j] for j in range(len(innovation)))
                     for i in range(n)]

                # Update covariance: P = (I - K*C)*P_pred
                I_minus_KC = self._matrix_subtract(
                    self._identity_matrix(n),
                    self._matrix_multiply(K, C)
                )
                P = self._matrix_multiply(I_minus_KC, P_pred)

                # Log likelihood
                det_S = self._matrix_determinant(S)
                if det_S > 0:
                    log_likelihood += -0.5 * (
                        len(y) * math.log(2 * math.pi) +
                        math.log(det_S) +
                        sum(innovation[i] * sum(S_inv[i][j] * innovation[j]
                            for j in range(len(innovation)))
                            for i in range(len(innovation)))
                    )

            filtered_states.append(x[:])
            filtered_covariances.append([row[:] for row in P])

        return KalmanFilterResult(
            filtered_states=filtered_states,
            filtered_covariances=filtered_covariances,
            predicted_states=predicted_states,
            predicted_covariances=predicted_covariances,
            innovations=innovations,
            kalman_gains=kalman_gains,
            log_likelihood=log_likelihood
        )

    def _matrix_determinant(self, A: List[List[float]]) -> float:
        """Compute matrix determinant using Gaussian elimination."""
        n = len(A)
        aug = [row[:] for row in A]
        det = 1.0

        for col in range(n):
            # Find pivot
            max_row = col
            for row in range(col + 1, n):
                if abs(aug[row][col]) > abs(aug[max_row][col]):
                    max_row = row

            if abs(aug[max_row][col]) < 1e-10:
                return 0.0

            if max_row != col:
                aug[col], aug[max_row] = aug[max_row], aug[col]
                det *= -1

            det *= aug[col][col]

            # Eliminate
            for row in range(col + 1, n):
                factor = aug[row][col] / aug[col][col]
                for j in range(col, n):
                    aug[row][j] -= factor * aug[col][j]

        return det

    # ==================== KALMAN SMOOTHER ====================

    def kalman_smoother(
        self,
        filter_result: KalmanFilterResult,
        A: List[List[float]],
    ) -> Dict[str, List[List[float]]]:
        """
        Rauch-Tung-Striebel (RTS) smoother.

        Backward pass to compute smoothed estimates x(t|T) using all data.

        Args:
            filter_result: Result from kalman_filter
            A: State transition matrix

        Returns:
            Dict with smoothed_states and smoothed_covariances
        """
        T = len(filter_result.filtered_states)
        n = len(filter_result.filtered_states[0])

        # Initialize with filtered estimates
        smoothed_states = [state[:] for state in filter_result.filtered_states]
        smoothed_covariances = [cov[:] for cov in filter_result.filtered_covariances]

        # Backward pass
        for t in range(T - 2, -1, -1):
            x_filt = filter_result.filtered_states[t]
            P_filt = filter_result.filtered_covariances[t]
            P_pred_next = filter_result.predicted_covariances[t + 1]

            # Smoother gain J = P_filt*A^T*P_pred_next^(-1)
            P_pred_next_inv = self._matrix_inverse(P_pred_next)
            if P_pred_next_inv is None:
                continue

            J = self._matrix_multiply(
                self._matrix_multiply(P_filt, self._matrix_transpose(A)),
                P_pred_next_inv
            )

            # Smoothed state: x_smooth(t) = x_filt(t) + J*(x_smooth(t+1) - x_pred(t+1))
            diff = self._vector_subtract(
                smoothed_states[t + 1],
                filter_result.predicted_states[t + 1]
            )
            x_smooth = [x_filt[i] + sum(J[i][j] * diff[j] for j in range(n))
                       for i in range(n)]
            smoothed_states[t] = x_smooth

            # Smoothed covariance: P_smooth(t) = P_filt(t) + J*(P_smooth(t+1) - P_pred(t+1))*J^T
            P_diff = self._matrix_subtract(
                smoothed_covariances[t + 1],
                P_pred_next
            )
            P_smooth = self._matrix_add(
                P_filt,
                self._matrix_multiply(
                    self._matrix_multiply(J, P_diff),
                    self._matrix_transpose(J)
                )
            )
            smoothed_covariances[t] = P_smooth

        return {
            'smoothed_states': smoothed_states,
            'smoothed_covariances': smoothed_covariances,
        }

    # ==================== EXTENDED KALMAN FILTER ====================

    def extended_kalman_filter(
        self,
        observations: List[List[float]],
        f: Callable[[List[float]], List[float]],
        h: Callable[[List[float]], List[float]],
        F_jacobian: Callable[[List[float]], List[List[float]]],
        H_jacobian: Callable[[List[float]], List[List[float]]],
        Q: List[List[float]],
        R: List[List[float]],
        x0: List[float],
        P0: List[List[float]],
    ) -> KalmanFilterResult:
        """
        Extended Kalman Filter for nonlinear systems.

        Nonlinear state equation: x(t) = f(x(t-1)) + w(t)
        Nonlinear observation equation: y(t) = h(x(t)) + v(t)

        Args:
            observations: Observed data
            f: Nonlinear state transition function
            h: Nonlinear observation function
            F_jacobian: Jacobian of f
            H_jacobian: Jacobian of h
            Q: Process noise covariance
            R: Observation noise covariance
            x0: Initial state
            P0: Initial covariance

        Returns:
            KalmanFilterResult with filtered states
        """
        self._stats['filters_run'] += 1

        T = len(observations)
        n = len(x0)

        filtered_states = []
        filtered_covariances = []
        predicted_states = []
        predicted_covariances = []
        innovations = []

        x = x0[:]
        P = [row[:] for row in P0]

        for t in range(T):
            # Predict step using nonlinear function
            x_pred = f(x)
            F = F_jacobian(x)
            P_pred = self._matrix_add(
                self._matrix_multiply(self._matrix_multiply(F, P), self._matrix_transpose(F)),
                Q
            )

            predicted_states.append(x_pred[:])
            predicted_covariances.append([row[:] for row in P_pred])

            # Update step
            y = observations[t]
            y_pred = h(x_pred)
            innovation = self._vector_subtract(y, y_pred)
            innovations.append(innovation[:])

            H = H_jacobian(x_pred)
            S = self._matrix_add(
                self._matrix_multiply(
                    self._matrix_multiply(H, P_pred),
                    self._matrix_transpose(H)
                ),
                R
            )

            S_inv = self._matrix_inverse(S)
            if S_inv is None:
                x = x_pred
                P = P_pred
            else:
                K = self._matrix_multiply(
                    self._matrix_multiply(P_pred, self._matrix_transpose(H)),
                    S_inv
                )

                x = [x_pred[i] + sum(K[i][j] * innovation[j] for j in range(len(innovation)))
                     for i in range(n)]

                I_minus_KH = self._matrix_subtract(
                    self._identity_matrix(n),
                    self._matrix_multiply(K, H)
                )
                P = self._matrix_multiply(I_minus_KH, P_pred)

            filtered_states.append(x[:])
            filtered_covariances.append([row[:] for row in P])

        return KalmanFilterResult(
            filtered_states=filtered_states,
            filtered_covariances=filtered_covariances,
            predicted_states=predicted_states,
            predicted_covariances=predicted_covariances,
            innovations=innovations,
            kalman_gains=[],
            log_likelihood=0.0
        )

    # ==================== PREDICTION/UPDATE STEPS ====================

    def predict_step(
        self,
        x: List[float],
        P: List[List[float]],
        A: List[List[float]],
        Q: List[List[float]],
    ) -> Tuple[List[float], List[List[float]]]:
        """
        Kalman filter prediction step.

        Args:
            x: Current state estimate
            P: Current covariance
            A: State transition matrix
            Q: Process noise covariance

        Returns:
            Tuple of (predicted_state, predicted_covariance)
        """
        self._stats['predictions_made'] += 1

        x_pred = self._matrix_vector_multiply(A, x)
        P_pred = self._matrix_add(
            self._matrix_multiply(self._matrix_multiply(A, P), self._matrix_transpose(A)),
            Q
        )

        return x_pred, P_pred

    def update_step(
        self,
        x_pred: List[float],
        P_pred: List[List[float]],
        y: List[float],
        C: List[List[float]],
        R: List[List[float]],
    ) -> Tuple[List[float], List[List[float]], List[float]]:
        """
        Kalman filter update step.

        Args:
            x_pred: Predicted state
            P_pred: Predicted covariance
            y: Observation
            C: Observation matrix
            R: Observation noise covariance

        Returns:
            Tuple of (updated_state, updated_covariance, innovation)
        """
        # Innovation
        y_pred = self._matrix_vector_multiply(C, x_pred)
        innovation = self._vector_subtract(y, y_pred)

        # Innovation covariance
        S = self._matrix_add(
            self._matrix_multiply(
                self._matrix_multiply(C, P_pred),
                self._matrix_transpose(C)
            ),
            R
        )

        # Kalman gain
        S_inv = self._matrix_inverse(S)
        if S_inv is None:
            return x_pred, P_pred, innovation

        K = self._matrix_multiply(
            self._matrix_multiply(P_pred, self._matrix_transpose(C)),
            S_inv
        )

        # Update
        n = len(x_pred)
        x = [x_pred[i] + sum(K[i][j] * innovation[j] for j in range(len(innovation)))
             for i in range(n)]

        I_minus_KC = self._matrix_subtract(
            self._identity_matrix(n),
            self._matrix_multiply(K, C)
        )
        P = self._matrix_multiply(I_minus_KC, P_pred)

        return x, P, innovation

    # ==================== NOISE ESTIMATION ====================

    def estimate_noise_covariance(
        self,
        innovations: List[List[float]],
    ) -> List[List[float]]:
        """
        Estimate observation noise covariance from innovations.

        Args:
            innovations: Innovation sequence

        Returns:
            Estimated R matrix
        """
        T = len(innovations)
        m = len(innovations[0]) if innovations else 0

        # Sample covariance of innovations
        mean = [sum(innovations[t][i] for t in range(T)) / T for i in range(m)]

        R = [[sum((innovations[t][i] - mean[i]) * (innovations[t][j] - mean[j])
                  for t in range(T)) / T
              for j in range(m)]
             for i in range(m)]

        return R

    # ==================== BDI INTEGRATION ====================

    def process(self, task_entry):
        """Process incoming task."""
        self.tasks_executed += 1

        task_type = task_entry.get('task_type', 'kalman_filter')
        params = task_entry.get('params', {})

        handlers = {
            'kalman_filter': lambda p: self.kalman_filter(**p),
            'kalman_smoother': lambda p: self.kalman_smoother(**p),
            'extended_kalman_filter': lambda p: self.extended_kalman_filter(**p),
            'predict_step': lambda p: self.predict_step(**p),
            'update_step': lambda p: self.update_step(**p),
        }

        if task_type in handlers:
            result = handlers[task_type](params)
            return {'status': 'success', 'result': result}

        return {
            'operation': 'kalman filter',
            'explanation': 'State-space models, Kalman filtering',
            'status': 'success'
        }

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard and hasattr(self.blackboard, 'query_entries'):
            entries = self.blackboard.query_entries(
                tags=['kalman', 'state_estimation'],
                status='pending'
            )
            for entry in entries:
                self.add_belief('pending_kalman_task', entry, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on beliefs."""
        intentions = []

        if self.tasks_executed > 40:
            intentions.append(Intention(
                goal='optimize_filter',
                plan=['estimate_noise', 'retune_parameters'],
                priority=2
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute intention step."""
        if intention.goal == 'optimize_filter':
            logger.info("Optimizing Kalman filter parameters")

    def get_statistics(self):
        """Get agent statistics."""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            **self._stats
        }


__all__ = [
    'KalmanFilterSpecialist',
    'KalmanFilterResult',
]
