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
Numeric Root Finding Methods
============================

This module contains numeric root-finding algorithms:
- Newton-Raphson iteration for finding single roots
- Multi-root finding using polynomial deflation

These are domain-specific algorithms that don't require SymPy.
"""

from typing import Any, List, Optional


def newton_raphson(coeffs: List[Any], x0: float = 1.0,
                   tolerance: float = 1e-10, max_iterations: int = 100) -> Optional[float]:
    """
    Find a numeric root using Newton-Raphson iteration.

    x_{n+1} = x_n - f(x_n) / f'(x_n)

    Args:
        coeffs: Polynomial coefficients [a_n, ..., a_0]
        x0: Initial guess
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Approximate root, or None if doesn't converge
    """
    if not coeffs:
        return None

    degree = len(coeffs) - 1
    if degree < 1:
        return None

    # Convert coefficients to floats
    try:
        float_coeffs = [float(c) for c in coeffs]
    except (TypeError, ValueError):
        return None

    def evaluate_poly(x: float) -> float:
        """Evaluate polynomial at x using Horner's method."""
        result = 0.0
        for c in float_coeffs:
            result = result * x + c
        return result

    def evaluate_derivative(x: float) -> float:
        """Evaluate derivative at x."""
        result = 0.0
        for i, c in enumerate(float_coeffs[:-1]):
            power = degree - i
            result = result * x + power * c
        return result

    x = x0
    for _ in range(max_iterations):
        fx = evaluate_poly(x)
        if abs(fx) < tolerance:
            return x

        fpx = evaluate_derivative(x)
        if abs(fpx) < 1e-15:  # Avoid division by zero
            # Try a different starting point
            x = x + 0.5
            continue

        x_new = x - fx / fpx
        if abs(x_new - x) < tolerance:
            return x_new
        x = x_new

    return None  # Did not converge


def find_all_numeric_roots(coeffs: List[Any], num_attempts: int = 20) -> List[float]:
    """
    Find all numeric roots by running Newton-Raphson from multiple starting points.

    Uses polynomial deflation after finding each root.

    Args:
        coeffs: Polynomial coefficients [a_n, ..., a_0]
        num_attempts: Number of initial guesses to try per root

    Returns:
        List of found numeric roots
    """
    if not coeffs or len(coeffs) < 2:
        return []

    roots = []
    current_coeffs = list(coeffs)
    degree = len(coeffs) - 1

    for _ in range(degree):
        found_root = None

        # Try multiple starting points
        for i in range(num_attempts):
            # Spread initial guesses across reasonable range
            x0 = (i - num_attempts // 2) * 0.5
            root = newton_raphson(current_coeffs, x0)
            if root is not None:
                found_root = root
                break

        if found_root is None:
            break

        roots.append(found_root)

        # Deflate polynomial: divide by (x - found_root)
        new_coeffs = []
        carry = 0.0
        for c in current_coeffs:
            new_val = float(c) + carry
            new_coeffs.append(new_val)
            carry = new_val * found_root

        current_coeffs = new_coeffs[:-1]  # Remove last (remainder)

        if len(current_coeffs) < 2:
            break

    return roots
