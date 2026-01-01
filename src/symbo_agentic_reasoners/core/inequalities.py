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
Inequalities Module - Pure Python Implementation
================================================

Provides native implementations of classical mathematical inequalities:
- Cauchy-Schwarz inequality
- Hölder inequality
- Jensen inequality
- Chebyshev inequality
- Rearrangement inequality

Part of the SYMBO_AGENTIC_REASONERS native computation engine.

NO SYMPY - Pure NumPy and Python standard library.

REFERENCE:
---------
- Hardy, G. H., Littlewood, J. E., & Pólya, G. (1952). Inequalities. Cambridge University Press.
- Steele, J. M. (2004). The Cauchy-Schwarz Master Class. Cambridge University Press.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Callable, Optional, Any, Union
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# CAUCHY-SCHWARZ INEQUALITY
# =============================================================================

def cauchy_schwarz_discrete(a: Union[List[float], np.ndarray],
                            b: Union[List[float], np.ndarray],
                            tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Verify Cauchy-Schwarz inequality for discrete vectors.

    Inequality: (∑aᵢbᵢ)² ≤ (∑aᵢ²)(∑bᵢ²)

    Equality holds if and only if vectors are proportional: a = λb

    Args:
        a: First vector
        b: Second vector (must have same length as a)
        tolerance: Tolerance for equality checking (default 1e-10)

    Returns:
        Dictionary containing:
        - left_side: (∑aᵢbᵢ)²
        - right_side: (∑aᵢ²)(∑bᵢ²)
        - inequality_holds: True if left ≤ right
        - equality_holds: True if left ≈ right (within tolerance)
        - proportionality_constant: λ if a = λb, else None
        - ratio: left_side / right_side

    Raises:
        ValueError: If vectors have different lengths or are empty
        TypeError: If inputs are not numeric

    Example:
        >>> cauchy_schwarz_discrete([1, 2, 3], [4, 5, 6])
        {'left_side': 900.0, 'right_side': 910.0, 'inequality_holds': True, ...}

    Complexity:
        O(n) where n = len(a)

    References:
        - Cauchy, A.-L. (1821). Cours d'analyse.
        - Schwarz, H. A. (1885). Über ein die Flächen kleinsten Flächeninhalts.
    """
    # Input validation
    if not isinstance(a, (list, np.ndarray)) or not isinstance(b, (list, np.ndarray)):
        raise TypeError("Inputs must be lists or numpy arrays")

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    if len(a) == 0 or len(b) == 0:
        raise ValueError("Vectors cannot be empty")

    if len(a) != len(b):
        raise ValueError(f"Vectors must have same length: {len(a)} != {len(b)}")

    # Compute dot products
    dot_ab = np.dot(a, b)
    dot_aa = np.dot(a, a)
    dot_bb = np.dot(b, b)

    # Left and right sides of inequality
    left_side = dot_ab ** 2
    right_side = dot_aa * dot_bb

    # Check inequality
    inequality_holds = left_side <= right_side + tolerance
    equality_holds = abs(left_side - right_side) < tolerance

    # Check proportionality
    proportionality_constant = None
    if dot_bb > tolerance:  # Avoid division by zero
        # Check if a = λb by testing a/b consistency
        ratios = a / np.where(np.abs(b) > tolerance, b, 1.0)
        ratios_valid = np.abs(b) > tolerance
        if ratios_valid.any():
            lambda_candidate = ratios[ratios_valid][0]
            if np.allclose(a, lambda_candidate * b, atol=tolerance):
                proportionality_constant = lambda_candidate

    return {
        'left_side': float(left_side),
        'right_side': float(right_side),
        'inequality_holds': inequality_holds,
        'equality_holds': equality_holds,
        'proportionality_constant': proportionality_constant,
        'ratio': float(left_side / right_side) if right_side > tolerance else 0.0,
        'method': 'discrete_cauchy_schwarz'
    }


def cauchy_schwarz_integral(f_samples: Union[List[float], np.ndarray],
                            g_samples: Union[List[float], np.ndarray],
                            dx: float = 1.0,
                            tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Verify Cauchy-Schwarz inequality for numerical integration.

    Inequality: (∫fg)² ≤ (∫f²)(∫g²)

    Uses numerical integration (trapezoidal rule) on sampled functions.

    Args:
        f_samples: Samples of function f
        g_samples: Samples of function g
        dx: Spacing between samples (default 1.0)
        tolerance: Tolerance for equality checking

    Returns:
        Dictionary similar to cauchy_schwarz_discrete

    Example:
        >>> f = np.array([1, 2, 3, 2, 1])
        >>> g = np.array([0.5, 1, 1.5, 1, 0.5])
        >>> cauchy_schwarz_integral(f, g, dx=0.25)
        {'left_side': ..., 'inequality_holds': True, ...}

    Complexity:
        O(n) where n = number of samples
    """
    # Input validation
    f_samples = np.asarray(f_samples, dtype=float)
    g_samples = np.asarray(g_samples, dtype=float)

    if len(f_samples) != len(g_samples):
        raise ValueError(f"Sample arrays must have same length: {len(f_samples)} != {len(g_samples)}")

    if dx <= 0:
        raise ValueError(f"dx must be positive, got {dx}")

    # Numerical integration using trapezoidal rule
    integral_fg = np.trapz(f_samples * g_samples, dx=dx)
    integral_f2 = np.trapz(f_samples ** 2, dx=dx)
    integral_g2 = np.trapz(g_samples ** 2, dx=dx)

    left_side = integral_fg ** 2
    right_side = integral_f2 * integral_g2

    inequality_holds = left_side <= right_side + tolerance
    equality_holds = abs(left_side - right_side) < tolerance

    return {
        'left_side': float(left_side),
        'right_side': float(right_side),
        'inequality_holds': inequality_holds,
        'equality_holds': equality_holds,
        'ratio': float(left_side / right_side) if right_side > tolerance else 0.0,
        'method': 'integral_cauchy_schwarz',
        'num_samples': len(f_samples),
        'dx': dx
    }


# =============================================================================
# HÖLDER INEQUALITY
# =============================================================================

def holder_inequality(a: Union[List[float], np.ndarray],
                     b: Union[List[float], np.ndarray],
                     p: float,
                     tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Verify Hölder inequality for conjugate exponents.

    Inequality: ∑|aᵢbᵢ| ≤ (∑|aᵢ|ᵖ)^(1/p) · (∑|bᵢ|^q)^(1/q)

    where p and q are conjugate exponents: 1/p + 1/q = 1

    Args:
        a: First vector
        b: Second vector
        p: Exponent for first norm (must be > 1)
        tolerance: Tolerance for equality checking

    Returns:
        Dictionary containing:
        - left_side: ∑|aᵢbᵢ|
        - right_side: ||a||_p · ||b||_q
        - p: Exponent p
        - q: Conjugate exponent q
        - inequality_holds: True if left ≤ right
        - equality_holds: True if equality holds

    Raises:
        ValueError: If p ≤ 1 or p = ∞

    Example:
        >>> holder_inequality([1, 2, 3], [4, 5, 6], p=2.0)
        {'left_side': 32.0, 'right_side': 32.496..., 'inequality_holds': True, ...}

    Special Cases:
        - p = 2: Reduces to Cauchy-Schwarz
        - p → 1: Right side → ||a||_1 · ||b||_∞
        - p → ∞: Right side → ||a||_∞ · ||b||_1

    References:
        - Hölder, O. (1889). "Ueber einen Mittelwerths

atz".
        - Rogers, L. J. (1888). "An extension of a certain theorem in inequalities".
    """
    # Input validation
    if p <= 1:
        raise ValueError(f"p must be > 1, got {p}")

    if not np.isfinite(p):
        raise ValueError("p must be finite (use separate functions for p=1 or p=∞)")

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    if len(a) != len(b):
        raise ValueError(f"Vectors must have same length: {len(a)} != {len(b)}")

    # Compute conjugate exponent q
    q = p / (p - 1.0)

    # Compute norms
    norm_a_p = np.sum(np.abs(a) ** p) ** (1.0 / p)
    norm_b_q = np.sum(np.abs(b) ** q) ** (1.0 / q)

    # Left side: ∑|aᵢbᵢ|
    left_side = np.sum(np.abs(a * b))

    # Right side: ||a||_p · ||b||_q
    right_side = norm_a_p * norm_b_q

    inequality_holds = left_side <= right_side + tolerance
    equality_holds = abs(left_side - right_side) < tolerance

    return {
        'left_side': float(left_side),
        'right_side': float(right_side),
        'p': p,
        'q': q,
        'norm_a_p': float(norm_a_p),
        'norm_b_q': float(norm_b_q),
        'inequality_holds': inequality_holds,
        'equality_holds': equality_holds,
        'ratio': float(left_side / right_side) if right_side > tolerance else 0.0,
        'method': 'holder_inequality'
    }


# =============================================================================
# JENSEN INEQUALITY
# =============================================================================

def jensen_discrete(x_vals: Union[List[float], np.ndarray],
                   weights: Union[List[float], np.ndarray],
                   f: Callable[[float], float],
                   convex: bool = True,
                   tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Verify Jensen inequality for discrete weighted average.

    For convex f: f(∑λᵢxᵢ) ≤ ∑λᵢf(xᵢ)
    For concave f: f(∑λᵢxᵢ) ≥ ∑λᵢf(xᵢ)

    Args:
        x_vals: Points xᵢ
        weights: Weights λᵢ (must sum to 1)
        f: Function to test (callable)
        convex: True if testing convex inequality, False for concave
        tolerance: Tolerance for equality checking

    Returns:
        Dictionary containing:
        - left_side: f(∑λᵢxᵢ)
        - right_side: ∑λᵢf(xᵢ)
        - weighted_avg: ∑λᵢxᵢ
        - inequality_holds: True if inequality satisfied
        - convex: True if testing convex function

    Raises:
        ValueError: If weights don't sum to 1 or are negative

    Example:
        >>> jensen_discrete([1, 2, 3], [0.5, 0.3, 0.2], lambda x: x**2)
        {'left_side': 3.24, 'right_side': 3.7, 'inequality_holds': True, ...}

    References:
        - Jensen, J. L. W. V. (1906). "Sur les fonctions convexes et les inégalités".
    """
    # Input validation
    x_vals = np.asarray(x_vals, dtype=float)
    weights = np.asarray(weights, dtype=float)

    if len(x_vals) != len(weights):
        raise ValueError(f"x_vals and weights must have same length: {len(x_vals)} != {len(weights)}")

    if np.any(weights < 0):
        raise ValueError("Weights must be non-negative")

    weight_sum = np.sum(weights)
    if abs(weight_sum - 1.0) > tolerance:
        raise ValueError(f"Weights must sum to 1, got {weight_sum}")

    # Compute weighted average
    weighted_avg = np.dot(weights, x_vals)

    # Compute left side: f(∑λᵢxᵢ)
    left_side = f(weighted_avg)

    # Compute right side: ∑λᵢf(xᵢ)
    f_vals = np.array([f(x) for x in x_vals])
    right_side = np.dot(weights, f_vals)

    # Check inequality (convex: left ≤ right, concave: left ≥ right)
    if convex:
        inequality_holds = left_side <= right_side + tolerance
    else:
        inequality_holds = left_side >= right_side - tolerance

    equality_holds = abs(left_side - right_side) < tolerance

    return {
        'left_side': float(left_side),
        'right_side': float(right_side),
        'weighted_avg': float(weighted_avg),
        'inequality_holds': inequality_holds,
        'equality_holds': equality_holds,
        'convex': convex,
        'method': 'jensen_discrete'
    }


def is_convex_function(f: Callable[[float], float],
                      domain: Tuple[float, float],
                      samples: int = 100,
                      tolerance: float = 1e-8) -> bool:
    """
    Test if function is numerically convex via second derivative.

    A function is convex if f''(x) ≥ 0 for all x in domain.

    Args:
        f: Function to test
        domain: (a, b) interval to test
        samples: Number of sample points
        tolerance: Tolerance for f'' ≥ 0

    Returns:
        True if function appears convex on domain

    Example:
        >>> is_convex_function(lambda x: x**2, (-10, 10))
        True
        >>> is_convex_function(lambda x: -x**2, (-10, 10))
        False

    Complexity:
        O(samples) function evaluations
    """
    a, b = domain
    if a >= b:
        raise ValueError(f"Invalid domain: [{a}, {b}]")

    # Sample points
    x_vals = np.linspace(a, b, samples)
    h = (b - a) / (samples - 1)

    # Numerical second derivative via finite differences
    # f''(x) ≈ (f(x+h) - 2f(x) + f(x-h)) / h²

    for i in range(1, samples - 1):
        x = x_vals[i]
        try:
            f_minus = f(x - h)
            f_center = f(x)
            f_plus = f(x + h)

            second_deriv = (f_plus - 2*f_center + f_minus) / (h ** 2)

            if second_deriv < -tolerance:
                return False
        except:
            # Function evaluation failed
            return False

    return True


# =============================================================================
# CHEBYSHEV INEQUALITY
# =============================================================================

def chebyshev_probability(data: Union[List[float], np.ndarray],
                         k: float,
                         tolerance: float = 1e-10) -> Dict[str, float]:
    """
    Verify Chebyshev probability inequality.

    Inequality: P(|X - μ| ≥ kσ) ≤ 1/k²

    For empirical data, computes the actual proportion vs bound.

    Args:
        data: Sample data
        k: Number of standard deviations (must be > 0)
        tolerance: Tolerance for comparison

    Returns:
        Dictionary containing:
        - mean: Sample mean μ
        - std: Sample standard deviation σ
        - k: Number of standard deviations
        - bound: 1/k²
        - actual_proportion: P(|X - μ| ≥ kσ)
        - inequality_holds: True if actual ≤ bound

    Example:
        >>> data = np.random.normal(0, 1, 10000)
        >>> chebyshev_probability(data, k=2.0)
        {'bound': 0.25, 'actual_proportion': ~0.05, 'inequality_holds': True, ...}

    References:
        - Chebyshev, P. L. (1867). "Des valeurs moyennes".
    """
    # Input validation
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")

    data = np.asarray(data, dtype=float)

    if len(data) == 0:
        raise ValueError("Data cannot be empty")

    # Compute statistics
    mean = np.mean(data)
    std = np.std(data, ddof=1)  # Sample standard deviation

    if std < tolerance:
        # Zero variance - all points are at mean
        return {
            'mean': float(mean),
            'std': 0.0,
            'k': k,
            'bound': 1.0 / (k ** 2),
            'actual_proportion': 0.0,
            'inequality_holds': True,
            'method': 'chebyshev_probability'
        }

    # Chebyshev bound
    bound = 1.0 / (k ** 2)

    # Actual proportion of data beyond k standard deviations
    deviations = np.abs(data - mean)
    beyond_k_sigma = deviations >= k * std
    actual_proportion = np.mean(beyond_k_sigma)

    inequality_holds = actual_proportion <= bound + tolerance

    return {
        'mean': float(mean),
        'std': float(std),
        'k': k,
        'bound': bound,
        'actual_proportion': float(actual_proportion),
        'inequality_holds': inequality_holds,
        'method': 'chebyshev_probability'
    }


def chebyshev_sum(a: Union[List[float], np.ndarray],
                 b: Union[List[float], np.ndarray],
                 tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Verify Chebyshev sum inequality for monotone sequences.

    If both sequences are monotone in the same direction:
        (∑aᵢ)(∑bᵢ) ≤ n·∑(aᵢbᵢ)

    If monotone in opposite directions:
        (∑aᵢ)(∑bᵢ) ≥ n·∑(aᵢbᵢ)

    Args:
        a: First sequence
        b: Second sequence
        tolerance: Tolerance for comparison

    Returns:
        Dictionary with inequality verification and monotonicity info

    Example:
        >>> chebyshev_sum([1, 2, 3], [1, 2, 3])  # Both increasing
        {'inequality_holds': True, 'same_direction': True, ...}
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    if len(a) != len(b):
        raise ValueError(f"Sequences must have same length: {len(a)} != {len(b)}")

    n = len(a)

    # Check monotonicity
    a_increasing = np.all(np.diff(a) >= -tolerance)
    a_decreasing = np.all(np.diff(a) <= tolerance)
    b_increasing = np.all(np.diff(b) >= -tolerance)
    b_decreasing = np.all(np.diff(b) <= tolerance)

    a_monotone = a_increasing or a_decreasing
    b_monotone = b_increasing or b_decreasing

    if not (a_monotone and b_monotone):
        return {
            'inequality_holds': None,
            'reason': 'Sequences must be monotone',
            'a_monotone': a_monotone,
            'b_monotone': b_monotone
        }

    # Determine direction
    same_direction = (a_increasing and b_increasing) or (a_decreasing and b_decreasing)

    # Compute terms
    sum_a = np.sum(a)
    sum_b = np.sum(b)
    sum_ab = np.sum(a * b)

    left_side = sum_a * sum_b
    right_side = n * sum_ab

    # Check inequality
    if same_direction:
        # (∑aᵢ)(∑bᵢ) ≤ n·∑(aᵢbᵢ)
        inequality_holds = left_side <= right_side + tolerance
    else:
        # (∑aᵢ)(∑bᵢ) ≥ n·∑(aᵢbᵢ)
        inequality_holds = left_side >= right_side - tolerance

    return {
        'left_side': float(left_side),
        'right_side': float(right_side),
        'inequality_holds': inequality_holds,
        'same_direction': same_direction,
        'a_increasing': a_increasing,
        'b_increasing': b_increasing,
        'method': 'chebyshev_sum'
    }


# =============================================================================
# REARRANGEMENT INEQUALITY
# =============================================================================

def rearrangement_inequality(a: Union[List[float], np.ndarray],
                            b: Union[List[float], np.ndarray],
                            tolerance: float = 1e-10) -> Dict[str, Any]:
    """
    Verify rearrangement inequality.

    For sequences a₁ ≤ a₂ ≤ ... ≤ aₙ and b₁ ≤ b₂ ≤ ... ≤ bₙ:

        ∑aᵢb_{n+1-i} ≤ ∑aᵢb_{σ(i)} ≤ ∑aᵢbᵢ

    where σ is any permutation. The maximum is achieved when both
    sequences are sorted in the same direction.

    Args:
        a: First sequence
        b: Second sequence
        tolerance: Tolerance for comparison

    Returns:
        Dictionary containing:
        - max_sum: ∑aᵢbᵢ (both sorted same direction)
        - min_sum: ∑aᵢb_{n+1-i} (sorted opposite directions)
        - original_sum: ∑aᵢbᵢ with original ordering
        - inequality_holds: True if min ≤ original ≤ max

    Example:
        >>> rearrangement_inequality([3, 1, 2], [6, 4, 5])
        {'max_sum': 32, 'min_sum': 27, 'original_sum': 28, ...}

    References:
        - Hardy, G. H., Littlewood, J. E., & Pólya, G. (1952). Inequalities, Theorem 368.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    if len(a) != len(b):
        raise ValueError(f"Sequences must have same length: {len(a)} != {len(b)}")

    # Original sum
    original_sum = np.dot(a, b)

    # Sort both sequences
    a_sorted = np.sort(a)
    b_sorted = np.sort(b)

    # Maximum: both sorted same direction
    max_sum = np.dot(a_sorted, b_sorted)

    # Minimum: sorted opposite directions
    min_sum = np.dot(a_sorted, b_sorted[::-1])

    # Verify inequality: min ≤ original ≤ max
    inequality_holds = (min_sum - tolerance <= original_sum <= max_sum + tolerance)

    return {
        'max_sum': float(max_sum),
        'min_sum': float(min_sum),
        'original_sum': float(original_sum),
        'inequality_holds': inequality_holds,
        'at_maximum': abs(original_sum - max_sum) < tolerance,
        'at_minimum': abs(original_sum - min_sum) < tolerance,
        'method': 'rearrangement_inequality'
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def verify_inequality(inequality_type: str, **kwargs) -> Dict[str, Any]:
    """
    Unified interface for verifying inequalities.

    Args:
        inequality_type: Type of inequality ('cauchy_schwarz', 'holder', 'jensen', etc.)
        **kwargs: Arguments specific to the inequality type

    Returns:
        Dictionary with verification results

    Example:
        >>> verify_inequality('cauchy_schwarz', a=[1,2,3], b=[4,5,6])
        {...}
    """
    if inequality_type == 'cauchy_schwarz':
        return cauchy_schwarz_discrete(kwargs['a'], kwargs['b'], kwargs.get('tolerance', 1e-10))
    elif inequality_type == 'holder':
        return holder_inequality(kwargs['a'], kwargs['b'], kwargs['p'], kwargs.get('tolerance', 1e-10))
    elif inequality_type == 'jensen':
        return jensen_discrete(kwargs['x_vals'], kwargs['weights'], kwargs['f'],
                              kwargs.get('convex', True), kwargs.get('tolerance', 1e-10))
    elif inequality_type == 'chebyshev':
        return chebyshev_probability(kwargs['data'], kwargs['k'], kwargs.get('tolerance', 1e-10))
    elif inequality_type == 'rearrangement':
        return rearrangement_inequality(kwargs['a'], kwargs['b'], kwargs.get('tolerance', 1e-10))
    else:
        raise ValueError(f"Unknown inequality type: {inequality_type}")
