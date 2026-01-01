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
Polynomial GCD and Resultant Operations
=======================================

NO SYMPY - Pure Python implementation.

Algorithms:
-----------
1. Euclidean Algorithm for polynomial GCD
2. Extended Euclidean Algorithm
3. Resultant computation
4. Subresultant PRS (Polynomial Remainder Sequence)
5. Content and primitive part extraction

These operations are critical for:
- Simplifying rational expressions
- Finding common roots
- Eliminating variables in polynomial systems
"""

from typing import List, Optional, Tuple
from math import gcd as int_gcd
from functools import reduce


def polynomial_gcd(
    p: List[float],
    q: List[float],
    tolerance: float = 1e-10
) -> List[float]:
    """
    Compute GCD of two polynomials using Euclidean algorithm.

    Polynomials are represented as coefficient lists [a0, a1, a2, ...]
    where p(x) = a0 + a1*x + a2*x^2 + ...

    Args:
        p: First polynomial coefficients (lowest degree first)
        q: Second polynomial coefficients (lowest degree first)
        tolerance: Coefficients below this are treated as zero

    Returns:
        GCD polynomial coefficients (monic)
    """
    # Normalize (remove trailing zeros)
    p = _normalize_poly(p, tolerance)
    q = _normalize_poly(q, tolerance)

    if not q or all(abs(c) < tolerance for c in q):
        return _make_monic(p, tolerance)
    if not p or all(abs(c) < tolerance for c in p):
        return _make_monic(q, tolerance)

    # Euclidean algorithm
    while q and any(abs(c) >= tolerance for c in q):
        _, r = polynomial_divmod(p, q, tolerance)
        p = q
        q = r

    return _make_monic(p, tolerance)


def polynomial_divmod(
    dividend: List[float],
    divisor: List[float],
    tolerance: float = 1e-10
) -> Tuple[List[float], List[float]]:
    """
    Polynomial division with remainder.

    Returns (quotient, remainder) such that:
    dividend = quotient * divisor + remainder

    Args:
        dividend: Dividend polynomial coefficients
        divisor: Divisor polynomial coefficients
        tolerance: Coefficients below this are treated as zero

    Returns:
        Tuple of (quotient coefficients, remainder coefficients)
    """
    dividend = _normalize_poly(dividend, tolerance)
    divisor = _normalize_poly(divisor, tolerance)

    if not divisor or all(abs(c) < tolerance for c in divisor):
        raise ValueError("Division by zero polynomial")

    deg_dividend = len(dividend) - 1
    deg_divisor = len(divisor) - 1

    if deg_dividend < deg_divisor:
        return [0.0], dividend.copy()

    quotient = [0.0] * (deg_dividend - deg_divisor + 1)
    remainder = dividend.copy()

    lead_divisor = divisor[-1]

    for i in range(deg_dividend - deg_divisor, -1, -1):
        if len(remainder) > i + deg_divisor:
            coeff = remainder[i + deg_divisor] / lead_divisor
            quotient[i] = coeff

            for j in range(deg_divisor + 1):
                if i + j < len(remainder):
                    remainder[i + j] -= coeff * divisor[j]

    # Truncate remainder to actual degree
    while len(remainder) > 1 and abs(remainder[-1]) < tolerance:
        remainder.pop()

    return quotient, remainder


def extended_euclidean(
    p: List[float],
    q: List[float],
    tolerance: float = 1e-10
) -> Tuple[List[float], List[float], List[float]]:
    """
    Extended Euclidean algorithm for polynomials.

    Finds gcd, s, t such that: s*p + t*q = gcd(p, q)

    Args:
        p: First polynomial
        q: Second polynomial
        tolerance: Zero tolerance

    Returns:
        Tuple (gcd, s, t) where s*p + t*q = gcd
    """
    p = _normalize_poly(p, tolerance)
    q = _normalize_poly(q, tolerance)

    if not q or all(abs(c) < tolerance for c in q):
        return _make_monic(p, tolerance), [1.0], [0.0]

    s0, s1 = [1.0], [0.0]
    t0, t1 = [0.0], [1.0]

    while q and any(abs(c) >= tolerance for c in q):
        quot, rem = polynomial_divmod(p, q, tolerance)

        # s_new = s0 - quot * s1
        # t_new = t0 - quot * t1
        s_new = polynomial_subtract(s0, polynomial_multiply(quot, s1))
        t_new = polynomial_subtract(t0, polynomial_multiply(quot, t1))

        p, q = q, rem
        s0, s1 = s1, s_new
        t0, t1 = t1, t_new

    gcd = _make_monic(p, tolerance)
    return gcd, s0, t0


def resultant(
    p: List[float],
    q: List[float]
) -> float:
    """
    Compute the resultant of two polynomials.

    The resultant is zero if and only if p and q have a common root.
    Uses Sylvester matrix determinant method.

    Args:
        p: First polynomial coefficients (lowest degree first)
        q: Second polynomial coefficients (lowest degree first)

    Returns:
        Resultant value (scalar)
    """
    p = _normalize_poly(p)
    q = _normalize_poly(q)

    m = len(p) - 1  # degree of p
    n = len(q) - 1  # degree of q

    if m < 0 or n < 0:
        return 0.0

    # Build Sylvester matrix (n+m) x (n+m)
    size = m + n
    if size == 0:
        return 1.0

    matrix = [[0.0] * size for _ in range(size)]

    # First n rows from p
    for i in range(n):
        for j in range(m + 1):
            if i + j < size:
                matrix[i][i + j] = p[m - j] if m - j >= 0 else 0.0

    # Next m rows from q
    for i in range(m):
        for j in range(n + 1):
            if i + j < size:
                matrix[n + i][i + j] = q[n - j] if n - j >= 0 else 0.0

    # Compute determinant
    return _determinant(matrix)


def subresultant_prs(
    p: List[float],
    q: List[float],
    tolerance: float = 1e-10
) -> List[List[float]]:
    """
    Compute the subresultant polynomial remainder sequence.

    More numerically stable than standard Euclidean algorithm.
    Used for GCD computation and resultant chains.

    Args:
        p: First polynomial
        q: Second polynomial
        tolerance: Zero tolerance

    Returns:
        List of polynomials in the PRS
    """
    p = _normalize_poly(p, tolerance)
    q = _normalize_poly(q, tolerance)

    sequence = [p, q]

    if not q or all(abs(c) < tolerance for c in q):
        return sequence

    delta = len(p) - len(q)
    psi = -1.0
    beta = (-1.0) ** (delta + 1)

    while q and any(abs(c) >= tolerance for c in q):
        _, r = polynomial_divmod(p, q, tolerance)

        if not r or all(abs(c) < tolerance for c in r):
            break

        # Scale remainder
        lead_q = q[-1]
        if abs(psi) > tolerance:
            r = [c / (beta * (psi ** delta)) for c in r]
        else:
            r = [c / beta for c in r]

        r = _normalize_poly(r, tolerance)
        sequence.append(r)

        # Update for next iteration
        delta_new = len(q) - len(r) if r else len(q)
        psi = lead_q ** delta / (psi ** (delta - 1)) if abs(psi) > tolerance and delta > 0 else lead_q
        beta = -lead_q * (psi ** delta_new)

        p, q = q, r
        delta = delta_new

    return sequence


def content(poly: List[float], tolerance: float = 1e-10) -> float:
    """
    Compute the content of a polynomial (GCD of all coefficients).

    Args:
        poly: Polynomial coefficients
        tolerance: Zero tolerance

    Returns:
        Content value
    """
    poly = _normalize_poly(poly, tolerance)

    if not poly:
        return 1.0

    # For integer coefficients, use exact GCD
    int_coeffs = []
    for c in poly:
        if abs(c) >= tolerance:
            # Scale to integers
            int_coeffs.append(int(round(c * 1e10)))

    if int_coeffs:
        result = reduce(int_gcd, int_coeffs)
        return result / 1e10

    return 1.0


def primitive_part(poly: List[float], tolerance: float = 1e-10) -> List[float]:
    """
    Compute the primitive part of a polynomial (poly / content(poly)).

    Args:
        poly: Polynomial coefficients
        tolerance: Zero tolerance

    Returns:
        Primitive part coefficients
    """
    cont = content(poly, tolerance)
    if abs(cont) < tolerance:
        return poly.copy()
    return [c / cont for c in poly]


def polynomial_multiply(p: List[float], q: List[float]) -> List[float]:
    """Multiply two polynomials."""
    if not p or not q:
        return [0.0]

    result = [0.0] * (len(p) + len(q) - 1)
    for i, pi in enumerate(p):
        for j, qj in enumerate(q):
            result[i + j] += pi * qj

    return result


def polynomial_subtract(p: List[float], q: List[float]) -> List[float]:
    """Subtract polynomials: p - q."""
    max_len = max(len(p), len(q))
    p = p + [0.0] * (max_len - len(p))
    q = q + [0.0] * (max_len - len(q))
    return [pi - qi for pi, qi in zip(p, q)]


def _normalize_poly(poly: List[float], tolerance: float = 1e-10) -> List[float]:
    """Remove trailing zeros from polynomial."""
    if not poly:
        return [0.0]

    result = poly.copy()
    while len(result) > 1 and abs(result[-1]) < tolerance:
        result.pop()

    return result


def _make_monic(poly: List[float], tolerance: float = 1e-10) -> List[float]:
    """Make polynomial monic (leading coefficient = 1)."""
    poly = _normalize_poly(poly, tolerance)
    if not poly or abs(poly[-1]) < tolerance:
        return poly

    lead = poly[-1]
    return [c / lead for c in poly]


def _determinant(matrix: List[List[float]]) -> float:
    """Compute determinant using LU decomposition."""
    n = len(matrix)
    if n == 0:
        return 1.0
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    # Create working copy
    m = [row.copy() for row in matrix]
    det = 1.0

    for col in range(n):
        # Find pivot
        max_row = col
        for row in range(col + 1, n):
            if abs(m[row][col]) > abs(m[max_row][col]):
                max_row = row

        if max_row != col:
            m[col], m[max_row] = m[max_row], m[col]
            det *= -1

        if abs(m[col][col]) < 1e-15:
            return 0.0

        det *= m[col][col]

        # Eliminate below
        for row in range(col + 1, n):
            factor = m[row][col] / m[col][col]
            for j in range(col, n):
                m[row][j] -= factor * m[col][j]

    return det


__all__ = [
    'polynomial_gcd',
    'polynomial_divmod',
    'extended_euclidean',
    'resultant',
    'subresultant_prs',
    'content',
    'primitive_part',
    'polynomial_multiply',
    'polynomial_subtract',
]
