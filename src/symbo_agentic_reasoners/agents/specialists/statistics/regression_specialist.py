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
REGRESSION SPECIALIST (Tier 3)
==============================

Statistical regression analysis.

CAPABILITIES:
------------
- Simple linear regression
- Multiple linear regression
- Polynomial regression
- Logistic regression
- R-squared and adjusted R-squared
- Confidence intervals

NO SYMPY - All mathematical operations use native implementations.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.regression')


@dataclass
class RegressionResult:
    """Result of regression analysis."""
    coefficients: List[float]  # [intercept, slope1, slope2, ...]
    r_squared: float
    adjusted_r_squared: float
    standard_errors: List[float]
    t_statistics: List[float]
    p_values: List[float]
    residuals: List[float]
    fitted_values: List[float]
    mse: float  # Mean squared error
    method: str


class RegressionSpecialist(BDIAgent):
    """
    Regression Specialist - Statistical Regression Analysis

    DIRECTIVE:
    ---------
    Provide regression analysis including linear, polynomial,
    and logistic regression.

    OPERATIONS:
    ----------
    - simple_linear_regression: y = a + bx
    - multiple_linear_regression: y = a + b1x1 + b2x2 + ...
    - polynomial_regression: y = a + bx + cx² + ...
    - logistic_regression: Classification via logistic function
    """

    def __init__(
        self,
        agent_id: str = "regression_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "regression_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'regressions': 0}

    def _register_services(self):
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="regression_analysis",
                description="Statistical regression analysis"
            ))

    # ==================== SIMPLE LINEAR REGRESSION ====================

    def simple_linear_regression(
        self,
        x: List[float],
        y: List[float],
    ) -> RegressionResult:
        """
        Simple linear regression: y = a + bx

        Uses ordinary least squares (OLS).
        """
        self._stats['regressions'] += 1

        n = len(x)
        if n != len(y) or n < 2:
            raise ValueError("x and y must have same length >= 2")

        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        # Calculate slope and intercept
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
        denominator = sum((xi - x_mean) ** 2 for xi in x)

        if denominator == 0:
            raise ValueError("All x values are identical")

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Fitted values and residuals
        fitted = [intercept + slope * xi for xi in x]
        residuals = [yi - fi for yi, fi in zip(y, fitted)]

        # R-squared
        ss_res = sum(r ** 2 for r in residuals)
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Adjusted R-squared
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - 2) if n > 2 else r_squared

        # MSE and standard errors
        mse = ss_res / (n - 2) if n > 2 else 0
        se_slope = math.sqrt(mse / denominator) if mse > 0 and denominator > 0 else 0
        se_intercept = math.sqrt(mse * (1/n + x_mean**2/denominator)) if mse > 0 else 0

        # T-statistics
        t_intercept = intercept / se_intercept if se_intercept > 0 else float('inf')
        t_slope = slope / se_slope if se_slope > 0 else float('inf')

        # P-values (approximate using t-distribution with n-2 df)
        p_intercept = self._t_distribution_p_value(abs(t_intercept), n - 2)
        p_slope = self._t_distribution_p_value(abs(t_slope), n - 2)

        return RegressionResult(
            coefficients=[intercept, slope],
            r_squared=r_squared,
            adjusted_r_squared=adj_r_squared,
            standard_errors=[se_intercept, se_slope],
            t_statistics=[t_intercept, t_slope],
            p_values=[p_intercept, p_slope],
            residuals=residuals,
            fitted_values=fitted,
            mse=mse,
            method='simple_linear'
        )

    def _t_distribution_p_value(self, t: float, df: int) -> float:
        """Approximate two-tailed p-value from t-distribution."""
        if df <= 0:
            return 1.0

        # Use approximation for large df
        if df > 30:
            # Approximate with normal distribution
            x = abs(t)
            return 2 * (1 - self._normal_cdf(x))

        # For smaller df, use rougher approximation
        x = df / (df + t * t)
        return x  # Very rough approximation

    def _normal_cdf(self, x: float) -> float:
        """Approximate standard normal CDF."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    # ==================== MULTIPLE LINEAR REGRESSION ====================

    def multiple_linear_regression(
        self,
        X: List[List[float]],  # Each row is a sample, each column is a feature
        y: List[float],
    ) -> RegressionResult:
        """
        Multiple linear regression: y = b0 + b1*x1 + b2*x2 + ...

        Uses ordinary least squares via normal equations.
        """
        self._stats['regressions'] += 1

        n = len(y)
        if n == 0 or len(X) != n:
            raise ValueError("Invalid input dimensions")

        # Add intercept column
        X_aug = [[1.0] + row for row in X]
        p = len(X_aug[0])  # Number of parameters

        # Solve normal equations: (X'X)β = X'y
        # β = (X'X)^(-1) X'y

        # Compute X'X
        XtX = [[sum(X_aug[i][j] * X_aug[i][k] for i in range(n))
                for k in range(p)] for j in range(p)]

        # Compute X'y
        Xty = [sum(X_aug[i][j] * y[i] for i in range(n)) for j in range(p)]

        # Solve using Gaussian elimination
        coefficients = self._solve_linear_system(XtX, Xty)

        if coefficients is None:
            raise ValueError("Matrix is singular - cannot solve")

        # Fitted values and residuals
        fitted = [sum(coefficients[j] * X_aug[i][j] for j in range(p))
                  for i in range(n)]
        residuals = [y[i] - fitted[i] for i in range(n)]

        # R-squared
        y_mean = sum(y) / n
        ss_res = sum(r ** 2 for r in residuals)
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Adjusted R-squared
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - p) if n > p else r_squared

        # MSE
        mse = ss_res / (n - p) if n > p else 0

        # Standard errors (diagonal of MSE * (X'X)^(-1))
        XtX_inv = self._matrix_inverse(XtX)
        if XtX_inv:
            standard_errors = [math.sqrt(mse * XtX_inv[j][j]) if XtX_inv[j][j] > 0 else 0
                              for j in range(p)]
        else:
            standard_errors = [0.0] * p

        # T-statistics and p-values
        t_statistics = [coefficients[j] / standard_errors[j]
                       if standard_errors[j] > 0 else float('inf')
                       for j in range(p)]
        p_values = [self._t_distribution_p_value(abs(t), n - p) for t in t_statistics]

        return RegressionResult(
            coefficients=coefficients,
            r_squared=r_squared,
            adjusted_r_squared=adj_r_squared,
            standard_errors=standard_errors,
            t_statistics=t_statistics,
            p_values=p_values,
            residuals=residuals,
            fitted_values=fitted,
            mse=mse,
            method='multiple_linear'
        )

    def _solve_linear_system(
        self,
        A: List[List[float]],
        b: List[float]
    ) -> Optional[List[float]]:
        """Solve Ax = b using Gaussian elimination with partial pivoting."""
        n = len(b)
        # Create augmented matrix
        aug = [row.copy() + [b[i]] for i, row in enumerate(A)]

        # Forward elimination with partial pivoting
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

    def _matrix_inverse(self, A: List[List[float]]) -> Optional[List[List[float]]]:
        """Compute matrix inverse using Gaussian elimination."""
        n = len(A)
        # Create augmented matrix [A | I]
        aug = [row.copy() + [1.0 if i == j else 0.0 for j in range(n)]
               for i, row in enumerate(A)]

        # Forward elimination
        for col in range(n):
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

    # ==================== POLYNOMIAL REGRESSION ====================

    def polynomial_regression(
        self,
        x: List[float],
        y: List[float],
        degree: int = 2,
    ) -> RegressionResult:
        """
        Polynomial regression: y = a0 + a1*x + a2*x² + ...

        Args:
            x: Independent variable values
            y: Dependent variable values
            degree: Polynomial degree

        Returns:
            RegressionResult with polynomial coefficients
        """
        self._stats['regressions'] += 1

        # Create design matrix with polynomial features
        X = [[xi ** d for d in range(1, degree + 1)] for xi in x]

        result = self.multiple_linear_regression(X, y)
        result.method = f'polynomial_degree_{degree}'

        return result

    # ==================== LOGISTIC REGRESSION ====================

    def logistic_regression(
        self,
        X: List[List[float]],
        y: List[int],  # Binary: 0 or 1
        learning_rate: float = 0.1,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        """
        Binary logistic regression using gradient descent.

        Args:
            X: Feature matrix (n_samples x n_features)
            y: Binary labels (0 or 1)
            learning_rate: Step size for gradient descent
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dict with coefficients, probabilities, accuracy
        """
        self._stats['regressions'] += 1

        n = len(y)
        if n == 0 or len(X) != n:
            raise ValueError("Invalid input dimensions")

        # Add intercept
        X_aug = [[1.0] + row for row in X]
        p = len(X_aug[0])

        # Initialize coefficients
        coefficients = [0.0] * p

        def sigmoid(z: float) -> float:
            if z < -500:
                return 0.0
            if z > 500:
                return 1.0
            return 1 / (1 + math.exp(-z))

        # Gradient descent
        for iteration in range(max_iterations):
            # Compute predictions
            z = [sum(coefficients[j] * X_aug[i][j] for j in range(p))
                 for i in range(n)]
            predictions = [sigmoid(zi) for zi in z]

            # Compute gradient
            gradient = [sum((predictions[i] - y[i]) * X_aug[i][j] for i in range(n)) / n
                       for j in range(p)]

            # Update coefficients
            new_coefficients = [coefficients[j] - learning_rate * gradient[j]
                               for j in range(p)]

            # Check convergence
            change = sum((new_coefficients[j] - coefficients[j]) ** 2 for j in range(p))
            if math.sqrt(change) < tolerance:
                coefficients = new_coefficients
                break

            coefficients = new_coefficients

        # Final predictions
        z = [sum(coefficients[j] * X_aug[i][j] for j in range(p))
             for i in range(n)]
        probabilities = [sigmoid(zi) for zi in z]
        predictions = [1 if p > 0.5 else 0 for p in probabilities]

        # Accuracy
        accuracy = sum(1 for pred, actual in zip(predictions, y) if pred == actual) / n

        return {
            'coefficients': coefficients,
            'probabilities': probabilities,
            'predictions': predictions,
            'accuracy': accuracy,
            'iterations': iteration + 1,
            'method': 'logistic'
        }

    # ==================== PREDICTION ====================

    def predict(
        self,
        result: RegressionResult,
        x_new: List[float],
    ) -> float:
        """Predict y for new x values using regression result."""
        if len(x_new) != len(result.coefficients) - 1:
            raise ValueError("x_new must have length equal to number of features")

        return result.coefficients[0] + sum(
            c * x for c, x in zip(result.coefficients[1:], x_new)
        )

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Perform process message operation.

        Args:
        message

        Returns:
        Result of the operation

        Example:
        >>> specialist = RegressionSpecialist()
        >>> result = specialist.process_message(...)
        # Returns result
        """
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'simple_linear_regression': lambda p: self.simple_linear_regression(**p),
            'multiple_linear_regression': lambda p: self.multiple_linear_regression(**p),
            'polynomial_regression': lambda p: self.polynomial_regression(**p),
            'logistic_regression': lambda p: self.logistic_regression(**p),
        }

        if action in handlers:
            result = handlers[action](params)
            return {'status': 'success', 'result': result}
        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Compute get stats using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = RegressionSpecialist()
        >>> result = specialist.get_stats()
        # Returns computed result

        """
        return dict(self._stats)

    def update_beliefs(self):
        """Perform update beliefs operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = RegressionSpecialist()
        >>> result = specialist.update_beliefs(...)
        # Returns result
        """
        pass

    def deliberate(self) -> List:
        """Perform deliberate operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = RegressionSpecialist()
        >>> result = specialist.deliberate(...)
        # Returns result
        """
        return []

    def execute_step(self, intention):
        """Perform execute step operation.

        Args:
        intention

        Returns:
        Result of the operation

        Example:
        >>> specialist = RegressionSpecialist()
        >>> result = specialist.execute_step(...)
        # Returns result
        """
        pass


__all__ = [
    'RegressionSpecialist',
    'RegressionResult',
]
