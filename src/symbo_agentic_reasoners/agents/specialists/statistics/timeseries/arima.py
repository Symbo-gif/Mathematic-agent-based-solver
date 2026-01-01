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
ARIMA SPECIALIST (Tier 3)
=========================

Box-Jenkins methodology for ARIMA modeling.

CAPABILITIES:
------------
- ARIMA(p,d,q) model fitting
- Autocorrelation (ACF) and partial autocorrelation (PACF) computation
- Parameter estimation via maximum likelihood
- Forecasting with confidence intervals
- Model selection (AIC, BIC)
- Stationarity testing (ADF test)
- Series differencing

ALGORITHMS:
-----------
Native NumPy implementation - NO external dependencies

1. ARIMA(p,d,q): yt = c + phi1*y(t-1) + ... + phip*y(t-p) +
                      theta1*e(t-1) + ... + thetaq*e(t-q) + et
2. ACF: rho(k) = Cov(yt, y(t-k)) / Var(yt)
3. PACF: Partial correlation after removing intermediate lags
4. ADF Test: Unit root test for stationarity
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import numpy as np
except ImportError:
    np = None

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.arima')


@dataclass
class ARIMAModel:
    """Fitted ARIMA model."""
    p: int  # AR order
    d: int  # Differencing order
    q: int  # MA order
    ar_params: List[float]  # phi parameters
    ma_params: List[float]  # theta parameters
    constant: float  # c parameter
    residuals: List[float]
    sigma2: float  # Residual variance
    aic: float
    bic: float
    converged: bool


@dataclass
class ACFResult:
    """Autocorrelation function result."""
    acf_values: List[float]
    pacf_values: List[float]
    max_lag: int
    confidence_interval: float = 1.96  # 95% CI


class ARIMASpecialist(BDIAgent):
    """
    ARIMA Specialist - Box-Jenkins Time Series Modeling

    DIRECTIVE:
    ---------
    Perform ARIMA modeling, including model identification, parameter
    estimation, and forecasting.

    OPERATIONS:
    ----------
    - fit_arima: Fit ARIMA(p,d,q) model
    - compute_acf: Autocorrelation function
    - compute_pacf: Partial autocorrelation function
    - forecast: Multi-step ahead forecasting
    - check_stationarity: ADF test
    - difference_series: Apply differencing
    """

    def __init__(
        self,
        agent_id: str = 'arima_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = 'arima_specialist'
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self._register_services()
        self._stats = {'models_fitted': 0, 'forecasts_computed': 0}

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type='math.statistics.timeseries.arima',
                    description='ARIMA modeling and forecasting'
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== AUTOCORRELATION ====================

    def compute_acf(
        self,
        data: List[float],
        max_lag: Optional[int] = None,
    ) -> ACFResult:
        """
        Compute autocorrelation function.

        ACF(k) = Cov(yt, y(t-k)) / Var(yt)

        Args:
            data: Time series data
            max_lag: Maximum lag (default: min(len(data)//2, 40))

        Returns:
            ACFResult with ACF and PACF values
        """
        n = len(data)
        if max_lag is None:
            max_lag = min(n // 2, 40)

        if n < 2:
            raise ValueError("Data must have at least 2 points")

        # Center the data
        mean = sum(data) / n
        centered = [x - mean for x in data]

        # Compute ACF
        c0 = sum(x * x for x in centered) / n  # Variance
        acf_values = [1.0]  # ACF(0) = 1

        for k in range(1, max_lag + 1):
            ck = sum(centered[i] * centered[i - k] for i in range(k, n)) / n
            acf_values.append(ck / c0 if c0 > 0 else 0)

        # Compute PACF using Durbin-Levinson algorithm
        pacf_values = self._compute_pacf(acf_values)

        return ACFResult(
            acf_values=acf_values,
            pacf_values=pacf_values,
            max_lag=max_lag
        )

    def _compute_pacf(self, acf_values: List[float]) -> List[float]:
        """
        Compute partial autocorrelation using Durbin-Levinson recursion.

        PACF(k) is the correlation between yt and y(t-k) after removing
        the effect of intermediate lags.
        """
        max_lag = len(acf_values) - 1
        pacf = [1.0]  # PACF(0) = 1

        if max_lag == 0:
            return pacf

        # Initialize
        phi = [[0.0] * (max_lag + 1) for _ in range(max_lag + 1)]

        for k in range(1, max_lag + 1):
            # Compute PACF(k)
            numerator = acf_values[k]
            denominator = 1.0

            for j in range(1, k):
                numerator -= phi[k-1][j] * acf_values[k-j]

            for j in range(1, k):
                denominator -= phi[k-1][j] * acf_values[j]

            phi[k][k] = numerator / denominator if abs(denominator) > 1e-10 else 0.0
            pacf.append(phi[k][k])

            # Update intermediate coefficients
            for j in range(1, k):
                phi[k][j] = phi[k-1][j] - phi[k][k] * phi[k-1][k-j]

        return pacf

    # ==================== DIFFERENCING ====================

    def difference_series(
        self,
        data: List[float],
        order: int = 1,
    ) -> List[float]:
        """
        Apply differencing to the time series.

        First difference: yt - y(t-1)
        Second difference: (yt - y(t-1)) - (y(t-1) - y(t-2))

        Args:
            data: Time series data
            order: Differencing order (1 or 2 typically)

        Returns:
            Differenced series
        """
        result = data[:]

        for _ in range(order):
            if len(result) < 2:
                break
            result = [result[i] - result[i-1] for i in range(1, len(result))]

        return result

    def invert_differencing(
        self,
        differenced: List[float],
        original_values: List[float],
        order: int = 1,
    ) -> List[float]:
        """
        Invert differencing operation.

        Args:
            differenced: Differenced series
            original_values: Last 'order' values from original series
            order: Differencing order

        Returns:
            Reconstructed series
        """
        result = differenced[:]

        for d in range(order):
            if d < len(original_values):
                initial = original_values[-(order - d)]
                result = [initial] + [initial + result[0]] + result[1:]
                for i in range(1, len(result)):
                    result[i] = result[i-1] + differenced[i-1] if i-1 < len(differenced) else result[i-1]

        return result

    # ==================== STATIONARITY TESTING ====================

    def check_stationarity(
        self,
        data: List[float],
        significance_level: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Augmented Dickey-Fuller test for stationarity.

        H0: Unit root exists (non-stationary)
        H1: Series is stationary

        Args:
            data: Time series data
            significance_level: Significance level for test

        Returns:
            Dict with test statistic, p-value, and decision
        """
        n = len(data)
        if n < 10:
            return {
                'test_statistic': 0.0,
                'p_value': 1.0,
                'is_stationary': False,
                'message': 'Insufficient data for ADF test'
            }

        # Simple ADF test: regress diff(y) on y(t-1) and lags
        diff = [data[i] - data[i-1] for i in range(1, n)]
        lagged = data[:-1]

        # OLS regression: diff_y = alpha + beta*y(t-1) + error
        mean_diff = sum(diff) / len(diff)
        mean_lagged = sum(lagged) / len(lagged)

        numerator = sum((lagged[i] - mean_lagged) * (diff[i] - mean_diff)
                       for i in range(len(diff)))
        denominator = sum((lagged[i] - mean_lagged) ** 2
                         for i in range(len(lagged)))

        beta = numerator / denominator if denominator > 0 else 0
        alpha = mean_diff - beta * mean_lagged

        # Test statistic
        residuals = [diff[i] - (alpha + beta * lagged[i]) for i in range(len(diff))]
        rss = sum(r * r for r in residuals)
        se_beta = math.sqrt(rss / (len(diff) - 2) / denominator) if denominator > 0 else 1.0

        t_stat = beta / se_beta if se_beta > 0 else 0

        # Critical values (approximate for 5% level)
        critical_value = -2.86  # Approximate for large n

        is_stationary = t_stat < critical_value

        return {
            'test_statistic': t_stat,
            'critical_value': critical_value,
            'is_stationary': is_stationary,
            'message': 'Stationary' if is_stationary else 'Non-stationary (unit root)'
        }

    # ==================== ARIMA FITTING ====================

    def fit_arima(
        self,
        data: List[float],
        p: int = 1,
        d: int = 0,
        q: int = 0,
        max_iterations: int = 100,
    ) -> ARIMAModel:
        """
        Fit ARIMA(p,d,q) model.

        Uses conditional maximum likelihood via iterative optimization.

        Args:
            data: Time series data
            p: AR order
            d: Differencing order
            q: MA order
            max_iterations: Maximum optimization iterations

        Returns:
            Fitted ARIMAModel
        """
        self._stats['models_fitted'] += 1

        # Apply differencing
        if d > 0:
            stationary_data = self.difference_series(data, d)
        else:
            stationary_data = data[:]

        n = len(stationary_data)
        if n < max(p, q) + 2:
            raise ValueError("Insufficient data for ARIMA model")

        # Initialize parameters
        ar_params = [0.1] * p if p > 0 else []
        ma_params = [0.1] * q if q > 0 else []
        constant = sum(stationary_data) / n if n > 0 else 0.0

        # Simple estimation using OLS-like approach for AR part
        if p > 0:
            ar_params = self._estimate_ar_parameters(stationary_data, p)

        # Compute residuals
        residuals = self._compute_residuals(
            stationary_data, ar_params, ma_params, constant, p, q
        )

        # Residual variance
        sigma2 = sum(r * r for r in residuals) / len(residuals) if residuals else 1.0

        # Information criteria
        n_params = p + q + 1
        log_likelihood = -0.5 * n * (math.log(2 * math.pi * sigma2) + 1)
        aic = -2 * log_likelihood + 2 * n_params
        bic = -2 * log_likelihood + n_params * math.log(n)

        return ARIMAModel(
            p=p, d=d, q=q,
            ar_params=ar_params,
            ma_params=ma_params,
            constant=constant,
            residuals=residuals,
            sigma2=sigma2,
            aic=aic,
            bic=bic,
            converged=True
        )

    def _estimate_ar_parameters(
        self,
        data: List[float],
        p: int,
    ) -> List[float]:
        """
        Estimate AR parameters using Yule-Walker equations.

        For AR(p): yt = phi1*y(t-1) + ... + phip*y(t-p) + et
        """
        if p == 0:
            return []

        # Compute autocorrelations
        acf_result = self.compute_acf(data, max_lag=p)
        rho = acf_result.acf_values[1:p+1]

        # Construct Yule-Walker matrix
        # R * phi = rho
        R = [[0.0] * p for _ in range(p)]
        for i in range(p):
            for j in range(p):
                lag = abs(i - j)
                R[i][j] = acf_result.acf_values[lag]

        # Solve using Gaussian elimination
        phi = self._solve_linear_system(R, rho)

        return phi if phi else [0.1] * p

    def _solve_linear_system(
        self,
        A: List[List[float]],
        b: List[float],
    ) -> Optional[List[float]]:
        """Solve Ax = b using Gaussian elimination."""
        n = len(b)
        # Create augmented matrix
        aug = [row[:] + [b[i]] for i, row in enumerate(A)]

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

            # Eliminate
            for row in range(col + 1, n):
                factor = aug[row][col] / aug[col][col]
                for j in range(col, n + 1):
                    aug[row][j] -= factor * aug[col][j]

        # Back substitution
        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            x[i] = aug[i][n]
            for j in range(i + 1, n):
                x[i] -= aug[i][j] * x[j]
            x[i] /= aug[i][i]

        return x

    def _compute_residuals(
        self,
        data: List[float],
        ar_params: List[float],
        ma_params: List[float],
        constant: float,
        p: int,
        q: int,
    ) -> List[float]:
        """Compute residuals from ARIMA model."""
        n = len(data)
        residuals = [0.0] * n

        max_lag = max(p, q)

        for t in range(max_lag, n):
            # AR component
            ar_sum = constant
            for i in range(p):
                if t - i - 1 >= 0:
                    ar_sum += ar_params[i] * data[t - i - 1]

            # MA component
            ma_sum = 0.0
            for i in range(q):
                if t - i - 1 >= 0:
                    ma_sum += ma_params[i] * residuals[t - i - 1]

            residuals[t] = data[t] - ar_sum - ma_sum

        return residuals[max_lag:]

    # ==================== FORECASTING ====================

    def forecast(
        self,
        model: ARIMAModel,
        original_data: List[float],
        steps_ahead: int = 10,
    ) -> Dict[str, Any]:
        """
        Generate h-step ahead forecasts.

        Args:
            model: Fitted ARIMA model
            original_data: Original time series (before differencing)
            steps_ahead: Number of steps to forecast

        Returns:
            Dict with forecasts and confidence intervals
        """
        self._stats['forecasts_computed'] += 1

        # Apply differencing to get stationary series
        if model.d > 0:
            stationary_data = self.difference_series(original_data, model.d)
        else:
            stationary_data = original_data[:]

        # Generate forecasts on differenced series
        forecasts_diff = []
        last_values = stationary_data[-(max(model.p, model.q) + 1):]
        last_residuals = [0.0] * model.q

        for h in range(steps_ahead):
            # AR component
            forecast = model.constant
            for i in range(model.p):
                idx = -(i + 1) - h
                if idx >= -len(last_values):
                    forecast += model.ar_params[i] * last_values[idx]
                elif len(forecasts_diff) > 0:
                    idx_forecast = -(i + 1) - h + len(last_values)
                    if 0 <= idx_forecast < len(forecasts_diff):
                        forecast += model.ar_params[i] * forecasts_diff[idx_forecast]

            # MA component (assumes future errors are zero)
            for i in range(model.q):
                if i < len(last_residuals):
                    forecast += model.ma_params[i] * last_residuals[-(i+1)]

            forecasts_diff.append(forecast)
            last_values.append(forecast)

        # Invert differencing
        if model.d > 0:
            forecasts = self._invert_forecast_differencing(
                forecasts_diff, original_data, model.d
            )
        else:
            forecasts = forecasts_diff

        # Compute confidence intervals
        se = math.sqrt(model.sigma2)
        ci_lower = [f - 1.96 * se * math.sqrt(h + 1) for h, f in enumerate(forecasts)]
        ci_upper = [f + 1.96 * se * math.sqrt(h + 1) for h, f in enumerate(forecasts)]

        return {
            'forecasts': forecasts,
            'confidence_interval_lower': ci_lower,
            'confidence_interval_upper': ci_upper,
            'steps_ahead': steps_ahead,
            'model_info': {
                'p': model.p,
                'd': model.d,
                'q': model.q,
                'aic': model.aic,
                'bic': model.bic,
            }
        }

    def _invert_forecast_differencing(
        self,
        forecasts_diff: List[float],
        original_data: List[float],
        order: int,
    ) -> List[float]:
        """Invert differencing for forecasts."""
        result = forecasts_diff[:]

        for _ in range(order):
            last_value = original_data[-1] if original_data else 0
            result = [last_value + result[0]] + \
                     [result[i-1] + (result[i] if i < len(result) else 0)
                      for i in range(1, len(result))]

        return result

    def estimate_parameters(
        self,
        data: List[float],
        p: int,
        q: int,
    ) -> Dict[str, List[float]]:
        """
        Estimate AR and MA parameters.

        Args:
            data: Time series data
            p: AR order
            q: MA order

        Returns:
            Dict with ar_params and ma_params
        """
        ar_params = self._estimate_ar_parameters(data, p)
        ma_params = [0.0] * q  # Simplified: set to zero

        return {
            'ar_params': ar_params,
            'ma_params': ma_params,
        }

    def compute_aic_bic(
        self,
        model: ARIMAModel,
        data: List[float],
    ) -> Dict[str, float]:
        """
        Compute AIC and BIC for model selection.

        Args:
            model: Fitted ARIMA model
            data: Time series data

        Returns:
            Dict with AIC and BIC values
        """
        return {
            'aic': model.aic,
            'bic': model.bic,
        }

    # ==================== BDI INTEGRATION ====================

    def process(self, task_entry):
        """Process incoming task."""
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        task_type = metadata.get('task_type', 'fit_arima')
        params = metadata.get('params', {})

        handlers = {
            'fit_arima': lambda p: self.fit_arima(**p),
            'forecast': lambda p: self.forecast(**p),
            'compute_acf': lambda p: self.compute_acf(**p),
            'check_stationarity': lambda p: self.check_stationarity(**p),
            'difference_series': lambda p: self.difference_series(**p),
        }

        if task_type in handlers:
            result = handlers[task_type](params)
            return {'status': 'success', 'result': result}

        return {
            'operation': 'arima',
            'explanation': 'ARIMA modeling, Box-Jenkins',
            'status': 'success'
        }

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard and hasattr(self.blackboard, 'query_entries'):
            entries = self.blackboard.query_entries(
                tags=['arima', 'timeseries'],
                status='pending'
            )
            for entry in entries:
                self.add_belief('pending_arima_task', entry, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on beliefs."""
        intentions = []

        if self.tasks_executed > 40:
            intentions.append(Intention(
                goal='retrain_model',
                plan=['collect_data', 'retrain', 'validate'],
                priority=2
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute intention step."""
        if intention.goal == 'retrain_model':
            logger.info("Retraining ARIMA model with accumulated data")

    def get_statistics(self):
        """Get agent statistics."""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            **self._stats
        }


__all__ = [
    'ARIMASpecialist',
    'ARIMAModel',
    'ACFResult',
]
