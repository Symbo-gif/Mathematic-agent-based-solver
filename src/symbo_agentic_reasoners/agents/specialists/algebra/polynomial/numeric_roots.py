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


def bisection_method(func, a: float, b: float,
                     tolerance: float = 1e-10, max_iterations: int = 100) -> Optional[float]:
    """
    Find a root using the bisection method (guaranteed convergence if root exists in [a,b]).

    The function must have opposite signs at a and b for this to work.

    Args:
        func: Function to find root of (callable)
        a: Left endpoint of interval
        b: Right endpoint of interval
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Approximate root, or None if no sign change or doesn't converge
    """
    try:
        fa = func(a)
        fb = func(b)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None

    # Check for sign change
    if fa * fb > 0:
        return None  # No guaranteed root in interval

    if abs(fa) < tolerance:
        return a
    if abs(fb) < tolerance:
        return b

    for _ in range(max_iterations):
        c = (a + b) / 2
        try:
            fc = func(c)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

        if abs(fc) < tolerance or (b - a) / 2 < tolerance:
            return c

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

    return (a + b) / 2  # Return best approximation


def secant_method(func, x0: float, x1: float,
                  tolerance: float = 1e-10, max_iterations: int = 100) -> Optional[float]:
    """
    Find a root using the secant method (derivative-free alternative to Newton-Raphson).

    x_{n+1} = x_n - f(x_n) * (x_n - x_{n-1}) / (f(x_n) - f(x_{n-1}))

    Args:
        func: Function to find root of (callable)
        x0: First initial guess
        x1: Second initial guess
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Approximate root, or None if doesn't converge
    """
    try:
        f0 = func(x0)
        f1 = func(x1)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None

    for _ in range(max_iterations):
        if abs(f1) < tolerance:
            return x1

        if abs(f1 - f0) < 1e-15:
            return None  # Would divide by zero

        try:
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

        if abs(x2 - x1) < tolerance:
            return x2

        x0, x1 = x1, x2
        f0 = f1
        try:
            f1 = func(x2)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

    return None


def brent_method(func, a: float, b: float,
                 tolerance: float = 1e-10, max_iterations: int = 100) -> Optional[float]:
    """
    Find a root using Brent's method (hybrid of bisection, secant, inverse quadratic).

    This is one of the most robust root-finding algorithms, combining:
    - Guaranteed convergence of bisection
    - Fast convergence of secant/inverse quadratic interpolation

    Args:
        func: Function to find root of (callable)
        a: Left endpoint of interval
        b: Right endpoint of interval
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Approximate root, or None if no sign change
    """
    try:
        fa = func(a)
        fb = func(b)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None

    # Check for sign change
    if fa * fb > 0:
        return None

    # Ensure |f(b)| <= |f(a)|
    if abs(fa) < abs(fb):
        a, b = b, a
        fa, fb = fb, fa

    c = a
    fc = fa
    d = b - a
    e = d
    mflag = True

    for _ in range(max_iterations):
        if abs(fb) < tolerance:
            return b

        if abs(b - a) < tolerance:
            return b

        # Inverse quadratic interpolation
        if fa != fc and fb != fc:
            try:
                s = (a * fb * fc) / ((fa - fb) * (fa - fc)) + \
                    (b * fa * fc) / ((fb - fa) * (fb - fc)) + \
                    (c * fa * fb) / ((fc - fa) * (fc - fb))
            except (ValueError, ZeroDivisionError, OverflowError):
                s = (a + b) / 2  # Fallback to bisection
        else:
            # Secant method
            if abs(fb - fa) < 1e-15:
                s = (a + b) / 2
            else:
                s = b - fb * (b - a) / (fb - fa)

        # Conditions to accept inverse quadratic or secant step
        bisection_step = False

        # Check if s is between (3a+b)/4 and b
        if not ((3 * a + b) / 4 < s < b or b < s < (3 * a + b) / 4):
            bisection_step = True
        elif mflag and abs(s - b) >= abs(b - c) / 2:
            bisection_step = True
        elif not mflag and abs(s - b) >= abs(c - d) / 2:
            bisection_step = True
        elif mflag and abs(b - c) < tolerance:
            bisection_step = True
        elif not mflag and abs(c - d) < tolerance:
            bisection_step = True

        if bisection_step:
            s = (a + b) / 2
            mflag = True
        else:
            mflag = False

        try:
            fs = func(s)
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

        d = c
        c = b
        fc = fb

        if fa * fs < 0:
            b = s
            fb = fs
        else:
            a = s
            fa = fs

        # Ensure |f(b)| <= |f(a)|
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa

    return b


def find_root(func, initial_guess: float = 1.0, interval: tuple = None,
              tolerance: float = 1e-10, max_iterations: int = 100) -> Optional[float]:
    """
    General-purpose root finder that tries multiple methods.

    This function automatically selects the best method based on available information:
    - If interval is provided and function has sign change: use Brent's method
    - Otherwise: try Newton-Raphson, then secant, then bisection with search

    Args:
        func: Function to find root of (callable)
        initial_guess: Starting point for iterative methods
        interval: Optional (a, b) tuple for bracketing methods
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Approximate root, or None if all methods fail
    """
    # If interval is provided, try Brent's method first
    if interval is not None:
        a, b = interval
        root = brent_method(func, a, b, tolerance, max_iterations)
        if root is not None:
            return root

    # Try secant method with two nearby starting points
    x0 = initial_guess
    x1 = initial_guess + 0.1
    root = secant_method(func, x0, x1, tolerance, max_iterations)
    if root is not None:
        return root

    # Try finding a bracketing interval via search
    for scale in [1, 2, 5, 10, 20, 50]:
        for offset in range(-10, 11):
            a = initial_guess + offset * scale / 10
            b = a + scale
            root = bisection_method(func, a, b, tolerance, max_iterations)
            if root is not None:
                return root

    return None


def poly_coeffs_to_func(coeffs: List[Any]):
    """
    Convert polynomial coefficients to a callable function.

    Args:
        coeffs: Polynomial coefficients [a_n, ..., a_0]

    Returns:
        Callable that evaluates the polynomial
    """
    float_coeffs = [float(c) for c in coeffs]

    def poly_func(x: float) -> float:
        """Perform poly func operation.

        Args:
        x: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.poly_func(...)
        """
        result = 0.0
        for c in float_coeffs:
            result = result * x + c
        return result

    return poly_func
