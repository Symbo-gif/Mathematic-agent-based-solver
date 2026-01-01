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
Elementary Number Theory Module - Pure Python Implementation
============================================================

Provides native implementations of elementary number theory algorithms:
- Congruence solving (linear, quadratic, systems via CRT)
- Continued fractions (rational, quadratic irrationals)
- Pell equations (fundamental solutions, solution generation)
- Diophantine equations (linear, Pythagorean triples, sums of squares)
- Lifting the Exponent (LTE) lemma
- Multiplicative order and primitive roots

Part of the SYMBO_AGENTIC_REASONERS native computation engine.

NO SYMPY - Pure Python using existing number_theory_native.py functions.

REFERENCE:
---------
- Niven, I., Zuckerman, H. S., & Montgomery, H. L. (1991). An Introduction to the Theory of Numbers (5th ed.).
- Hardy, G. H., & Wright, E. M. (2008). An Introduction to the Theory of Numbers (6th ed.).
- Burton, D. M. (2010). Elementary Number Theory (7th ed.).
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Import from existing number theory native module
try:
    from symbo_agentic_reasoners.core.number_theory_native import (
        gcd, extended_gcd, mod_inverse, is_prime, prime_factorization,
        totient as euler_phi, mobius
    )
except ImportError:
    logger.warning("Could not import from number_theory_native, using fallback implementations")

    def gcd(a: int, b: int) -> int:
        """Fallback GCD."""
        while b:
            a, b = b, a % b
        return abs(a)

    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """Fallback extended GCD: returns (gcd, x, y) where ax + by = gcd."""
        if b == 0:
            return abs(a), 1 if a >= 0 else -1, 0

        old_r, r = a, b
        old_s, s = 1, 0
        old_t, t = 0, 1

        while r != 0:
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t

        return abs(old_r), old_s if old_r >= 0 else -old_s, old_t if old_r >= 0 else -old_t

    def mod_inverse(a: int, m: int) -> Optional[int]:
        """Fallback modular inverse."""
        g, x, _ = extended_gcd(a, m)
        if g != 1:
            return None
        return x % m

    def is_prime(n: int) -> bool:
        """Fallback primality test."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    def prime_factorization(n: int) -> Dict[int, int]:
        """Fallback prime factorization."""
        factors = {}
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors[d] = factors.get(d, 0) + 1
                n //= d
            d += 1
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        return factors

    def euler_phi(n: int) -> int:
        """Fallback Euler's totient."""
        result = n
        p = 2
        while p * p <= n:
            if n % p == 0:
                while n % p == 0:
                    n //= p
                result -= result // p
            p += 1
        if n > 1:
            result -= result // n
        return result

# =============================================================================
# CONGRUENCE SOLVING
# =============================================================================

def solve_linear_congruence(a: int, b: int, m: int) -> Optional[List[int]]:
    """
    Solve linear congruence: ax ≡ b (mod m)

    Returns all solutions in [0, m) if solvable.

    Algorithm:
        gcd(a, m) must divide b for solutions to exist.
        If d = gcd(a, m) divides b, there are d solutions.

    Args:
        a: Coefficient
        b: Constant
        m: Modulus

    Returns:
        List of solutions in [0, m), or None if no solution

    Example:
        >>> solve_linear_congruence(3, 5, 7)
        [4]  # 3*4 ≡ 12 ≡ 5 (mod 7)
        >>> solve_linear_congruence(2, 3, 4)
        None  # No solution: gcd(2,4)=2 does not divide 3

    Complexity:
        O(log m) for extended GCD

    References:
        - Niven, Zuckerman, Montgomery, Section 2.2
    """
    if m <= 0:
        raise ValueError(f"Modulus must be positive, got {m}")

    a = a % m
    b = b % m

    d, x0, _ = extended_gcd(a, m)

    if b % d != 0:
        return None  # No solution

    # Particular solution
    x0 = (x0 * (b // d)) % m

    # General solution: x = x0 + k*(m/d) for k = 0, 1, ..., d-1
    solutions = [(x0 + k * (m // d)) % m for k in range(d)]

    return sorted(solutions)


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.

    Given: x ≡ a₁ (mod m₁), x ≡ a₂ (mod m₂), ..., x ≡ aₙ (mod mₙ)
    Find: x (mod M) where M = m₁·m₂·...·mₙ

    Requires: moduli pairwise coprime

    Args:
        remainders: List [a₁, a₂, ..., aₙ]
        moduli: List [m₁, m₂, ..., mₙ]

    Returns:
        Solution x in [0, M), or None if moduli not pairwise coprime

    Example:
        >>> chinese_remainder_theorem([2, 3, 2], [3, 5, 7])
        23  # x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)

    Complexity:
        O(n² log max(mᵢ))

    References:
        - Hardy & Wright, Section 5.3
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have same length")

    # Check pairwise coprimality
    n = len(moduli)
    for i in range(n):
        for j in range(i + 1, n):
            if gcd(moduli[i], moduli[j]) != 1:
                logger.warning(f"Moduli {moduli[i]} and {moduli[j]} are not coprime")
                return None

    # Compute M = product of all moduli
    M = 1
    for m in moduli:
        M *= m

    # CRT formula: x = Σ aᵢ·Mᵢ·yᵢ (mod M)
    # where Mᵢ = M/mᵢ and yᵢ is inverse of Mᵢ mod mᵢ
    x = 0

    for a_i, m_i in zip(remainders, moduli):
        M_i = M // m_i
        y_i = mod_inverse(M_i, m_i)

        if y_i is None:
            return None

        x += a_i * M_i * y_i

    return x % M


def quadratic_congruence(a: int, b: int, c: int, p: int) -> List[int]:
    """
    Solve quadratic congruence: ax² + bx + c ≡ 0 (mod p) for prime p.

    Uses Tonelli-Shanks algorithm for square roots modulo p.

    Args:
        a, b, c: Coefficients
        p: Prime modulus

    Returns:
        List of solutions in [0, p)

    Example:
        >>> quadratic_congruence(1, 0, -4, 7)  # x² ≡ 4 (mod 7)
        [2, 5]  # 2² ≡ 4, 5² ≡ 4 (mod 7)

    Complexity:
        O(log² p) for Tonelli-Shanks

    References:
        - Tonelli, A. (1891). "Bemerkung über die Auflösung quadratischer Congruenzen".
    """
    if not is_prime(p):
        raise ValueError(f"{p} must be prime")

    if a % p == 0:
        # Reduce to linear
        return solve_linear_congruence(b, -c, p) or []

    # Complete the square: a(x + b/2a)² ≡ b²/4a - c (mod p)
    # Simplified approach for a=1
    if a != 1:
        # Multiply through by inverse of a
        a_inv = mod_inverse(a, p)
        if a_inv is None:
            return []
        b = (b * a_inv) % p
        c = (c * a_inv) % p
        a = 1

    # Now solve: x² + bx + c ≡ 0 (mod p)
    # x = (-b ± √(b²-4c))/2
    discriminant = (b*b - 4*c) % p

    # Check if discriminant is quadratic residue
    if pow(discriminant, (p-1)//2, p) != 1 and discriminant % p != 0:
        return []  # No solutions

    # Find square root of discriminant
    sqrt_d = tonelli_shanks(discriminant, p)

    if sqrt_d is None:
        return []

    inv_2 = mod_inverse(2, p)
    if inv_2 is None:
        return []

    x1 = ((-b + sqrt_d) * inv_2) % p
    x2 = ((-b - sqrt_d) * inv_2) % p

    solutions = sorted(set([x1, x2]))
    return solutions


def tonelli_shanks(n: int, p: int) -> Optional[int]:
    """
    Find square root of n modulo prime p using Tonelli-Shanks algorithm.

    Args:
        n: Number to find square root of
        p: Prime modulus

    Returns:
        r such that r² ≡ n (mod p), or None if no solution

    Complexity:
        O(log² p)

    References:
        - Shanks, D. (1972). "Five Number-theoretic Algorithms".
    """
    n = n % p

    if n == 0:
        return 0

    # Check if n is quadratic residue
    if pow(n, (p-1)//2, p) != 1:
        return None

    # Find Q and S such that p - 1 = Q · 2^S with Q odd
    Q = p - 1
    S = 0
    while Q % 2 == 0:
        Q //= 2
        S += 1

    # Find quadratic non-residue z
    z = 2
    while pow(z, (p-1)//2, p) != p - 1:
        z += 1

    # Initialize
    M = S
    c = pow(z, Q, p)
    t = pow(n, Q, p)
    R = pow(n, (Q+1)//2, p)

    while True:
        if t == 0:
            return 0
        if t == 1:
            return R

        # Find least i such that t^(2^i) = 1
        i = 1
        temp = (t * t) % p
        while temp != 1:
            temp = (temp * temp) % p
            i += 1

        # Update values
        b = pow(c, 1 << (M - i - 1), p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p


# =============================================================================
# CONTINUED FRACTIONS
# =============================================================================

def continued_fraction_expansion(numerator: int, denominator: int,
                                 max_terms: int = 100) -> List[int]:
    """
    Compute continued fraction expansion of numerator/denominator.

    Representation: [a₀; a₁, a₂, a₃, ...] = a₀ + 1/(a₁ + 1/(a₂ + ...))

    Args:
        numerator: Numerator
        denominator: Denominator
        max_terms: Maximum number of terms

    Returns:
        List of continued fraction coefficients

    Example:
        >>> continued_fraction_expansion(22, 7)
        [3, 7]  # 22/7 = 3 + 1/7
        >>> continued_fraction_expansion(415, 93)
        [4, 2, 6, 7]  # Standard CF

    Complexity:
        O(log min(numerator, denominator))

    References:
        - Hardy & Wright, Chapter 10
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero")

    cf = []
    n, d = abs(numerator), abs(denominator)

    for _ in range(max_terms):
        if d == 0:
            break

        a = n // d
        cf.append(a)

        n, d = d, n - a * d

    # Handle negative fractions
    if (numerator < 0) != (denominator < 0):
        cf[0] = -cf[0] - 1
        if len(cf) > 1:
            cf[1] += 1

    return cf


def quadratic_irrational_cf(D: int, max_terms: int = 100) -> Tuple[List[int], List[int]]:
    """
    Compute continued fraction of √D for non-square D.

    Returns (initial_part, periodic_part) where:
    - √D = [a₀; periodic_part, periodic_part, ...]

    Algorithm: Lagrange's theorem - CF of √D is periodic.

    Args:
        D: Non-square positive integer
        max_terms: Maximum terms to compute

    Returns:
        Tuple of (initial part [a₀], periodic part)

    Example:
        >>> quadratic_irrational_cf(2)
        ([1], [2])  # √2 = [1; 2, 2, 2, ...]
        >>> quadratic_irrational_cf(23)
        ([4], [1, 3, 1, 8])  # √23 = [4; 1, 3, 1, 8, 1, 3, 1, 8, ...]

    Complexity:
        O(√D)

    References:
        - Lagrange, J.-L. (1770). "Additions au Mémoire sur la résolution des équations numériques".
    """
    if D <= 0:
        raise ValueError(f"D must be positive, got {D}")

    sqrt_D = int(D ** 0.5)
    if sqrt_D * sqrt_D == D:
        raise ValueError(f"D = {D} is a perfect square")

    # Initial term
    a0 = sqrt_D
    initial = [a0]

    # Generate periodic part
    m, d, a = 0, 1, a0
    seen = {}
    periodic = []

    for i in range(max_terms):
        m = d * a - m
        d = (D - m * m) // d
        a = (a0 + m) // d

        state = (m, d)
        if state in seen:
            # Found period
            period_start = seen[state]
            periodic = periodic[period_start:]
            break

        seen[state] = i
        periodic.append(a)

    return initial, periodic


def convergents(cf: List[int]) -> List[Tuple[int, int]]:
    """
    Compute convergents of continued fraction.

    Convergent Cₖ = pₖ/qₖ is the rational approximation using first k+1 terms.

    Recurrence:
        p₋₁ = 1,  p₀ = a₀,  pₖ = aₖ·p_{k-1} + p_{k-2}
        q₋₁ = 0,  q₀ = 1,   qₖ = aₖ·q_{k-1} + q_{k-2}

    Args:
        cf: Continued fraction [a₀, a₁, a₂, ...]

    Returns:
        List of convergents [(p₀/q₀), (p₁/q₁), ...]

    Example:
        >>> convergents([3, 7])
        [(3, 1), (22, 7)]

    Complexity:
        O(n) where n = len(cf)
    """
    if not cf:
        return []

    convergent_list = []

    p_prev2, p_prev1 = 1, cf[0]
    q_prev2, q_prev1 = 0, 1

    convergent_list.append((p_prev1, q_prev1))

    for i in range(1, len(cf)):
        a_i = cf[i]

        p_i = a_i * p_prev1 + p_prev2
        q_i = a_i * q_prev1 + q_prev2

        convergent_list.append((p_i, q_i))

        p_prev2, p_prev1 = p_prev1, p_i
        q_prev2, q_prev1 = q_prev1, q_i

    return convergent_list


# =============================================================================
# PELL EQUATIONS
# =============================================================================

def pell_fundamental_solution(D: int) -> Tuple[int, int]:
    """
    Find fundamental solution to Pell's equation: x² - Dy² = 1.

    Uses continued fraction method (Lagrange).

    Args:
        D: Non-square positive integer

    Returns:
        (x₁, y₁) = fundamental solution

    Example:
        >>> pell_fundamental_solution(2)
        (3, 2)  # 3² - 2·2² = 9 - 8 = 1
        >>> pell_fundamental_solution(5)
        (9, 4)  # 9² - 5·4² = 81 - 80 = 1

    Complexity:
        O(√D * period_length)

    References:
        - Hardy & Wright, Section 13.7
    """
    sqrt_D = int(D ** 0.5)
    if sqrt_D * sqrt_D == D:
        raise ValueError(f"D = {D} is a perfect square")

    initial, periodic = quadratic_irrational_cf(D)

    # Fundamental solution is convergent at period-1 (if period is odd)
    # or 2*period-1 (if period is even)
    period_length = len(periodic)

    # Build full CF up to appropriate length
    cf_full = initial + periodic

    if period_length % 2 == 1:
        # Odd period: use convergent at period-1
        cf_for_solution = cf_full[:1 + period_length - 1]
    else:
        # Even period: use convergent at 2*period-1
        cf_for_solution = cf_full[:1 + 2*period_length - 1]

    conv = convergents(cf_for_solution)
    x1, y1 = conv[-1]

    return x1, y1


def pell_solutions(D: int, n_solutions: int) -> List[Tuple[int, int]]:
    """
    Generate first n solutions to Pell's equation using recurrence.

    Given fundamental solution (x₁, y₁), subsequent solutions:
        xₙ + yₙ√D = (x₁ + y₁√D)ⁿ

    Args:
        D: Non-square positive integer
        n_solutions: Number of solutions to generate

    Returns:
        List of (xₙ, yₙ) solutions

    Example:
        >>> pell_solutions(2, 3)
        [(3, 2), (17, 12), (99, 70)]

    Complexity:
        O(n_solutions)
    """
    x1, y1 = pell_fundamental_solution(D)

    solutions = [(x1, y1)]

    for _ in range(1, n_solutions):
        # (xₙ₊₁, yₙ₊₁) = (x₁xₙ + Dy₁yₙ, x₁yₙ + y₁xₙ)
        xn, yn = solutions[-1]
        x_next = x1 * xn + D * y1 * yn
        y_next = x1 * yn + y1 * xn
        solutions.append((x_next, y_next))

    return solutions


def negative_pell_solution(D: int) -> Optional[Tuple[int, int]]:
    """
    Find solution to negative Pell equation: x² - Dy² = -1 (if exists).

    Solution exists iff period length of √D is odd.

    Args:
        D: Non-square positive integer

    Returns:
        (x, y) solution, or None if no solution exists

    Example:
        >>> negative_pell_solution(2)
        (1, 1)  # 1² - 2·1² = -1
        >>> negative_pell_solution(3)
        (2, 1)  # 2² - 3·1² = -1
        >>> negative_pell_solution(7)
        None  # No solution

    References:
        - Niven, Zuckerman, Montgomery, Section 7.8
    """
    initial, periodic = quadratic_irrational_cf(D)
    period_length = len(periodic)

    if period_length % 2 == 0:
        return None  # No solution when period is even

    # Solution is convergent at period-1
    cf_for_solution = initial + periodic[:-1]
    conv = convergents(cf_for_solution)
    x, y = conv[-1]

    # Verify
    if x*x - D*y*y == -1:
        return x, y

    return None


# =============================================================================
# DIOPHANTINE EQUATIONS
# =============================================================================

def solve_linear_diophantine(a: int, b: int, c: int) -> Optional[Tuple[int, int, int, int]]:
    """
    Solve linear Diophantine equation: ax + by = c.

    Returns particular solution and general solution parameters.

    Args:
        a, b, c: Coefficients

    Returns:
        (x₀, y₀, b/d, -a/d) where (x₀, y₀) is particular solution
        and general solution is x = x₀ + k(b/d), y = y₀ - k(a/d)
        Returns None if no solution (when gcd(a,b) does not divide c)

    Example:
        >>> solve_linear_diophantine(3, 5, 1)
        (2, -1, 5, -3)  # x = 2 + 5k, y = -1 - 3k

    Complexity:
        O(log min(a,b))
    """
    d = gcd(a, b)

    if c % d != 0:
        return None  # No solution

    # Use extended GCD to find particular solution
    _, x0, y0 = extended_gcd(a, b)

    # Scale to match c
    x0 *= c // d
    y0 *= c // d

    return x0, y0, b // d, -a // d


def pythagorean_triples(limit: int) -> List[Tuple[int, int, int]]:
    """
    Generate all primitive Pythagorean triples (a, b, c) with c ≤ limit.

    Uses parametrization: a = m²-n², b = 2mn, c = m²+n² for m > n > 0, gcd(m,n)=1.

    Args:
        limit: Maximum hypotenuse value

    Returns:
        List of (a, b, c) triples

    Example:
        >>> pythagorean_triples(15)
        [(3, 4, 5), (8, 6, 10), (5, 12, 13), (15, 8, 17)]

    Complexity:
        O(limit²)

    References:
        - Euclid's formula
    """
    triples = []

    for m in range(2, int(limit**0.5) + 1):
        for n in range(1, m):
            if gcd(m, n) != 1:
                continue

            if (m - n) % 2 == 0:
                continue  # m and n must have opposite parity

            a = m*m - n*n
            b = 2*m*n
            c = m*m + n*n

            if c > limit:
                break

            # Ensure a < b
            if a > b:
                a, b = b, a

            triples.append((a, b, c))

    return sorted(triples, key=lambda t: t[2])


# =============================================================================
# LIFTING THE EXPONENT (LTE)
# =============================================================================

def p_adic_valuation(n: int, p: int) -> int:
    """
    Compute p-adic valuation: vₚ(n) = max{k : p^k | n}.

    Args:
        n: Integer
        p: Prime

    Returns:
        Largest k such that p^k divides n

    Example:
        >>> p_adic_valuation(24, 2)
        3  # 24 = 2³ · 3
        >>> p_adic_valuation(100, 5)
        2  # 100 = 2² · 5²

    Complexity:
        O(log_p n)
    """
    if n == 0:
        return float('inf')

    n = abs(n)
    k = 0

    while n % p == 0:
        k += 1
        n //= p

    return k


def lte_valuation(a: int, b: int, n: int, p: int) -> int:
    """
    Compute vₚ(aⁿ - bⁿ) using Lifting the Exponent lemma.

    LTE Lemma (for p odd, p | a-b, p ∤ a, p ∤ b):
        vₚ(aⁿ - bⁿ) = vₚ(a - b) + vₚ(n)

    Args:
        a, b: Bases
        n: Exponent
        p: Prime

    Returns:
        vₚ(aⁿ - bⁿ)

    Example:
        >>> lte_valuation(10, 1, 5, 3)
        3  # v₃(10⁵ - 1⁵) = v₃(10-1) + v₃(5) = 2 + 1 = 3

    References:
        - Amir, M. (2014). "Lifting The Exponent Lemma (LTE)".
    """
    if p == 2:
        # Special case for p=2
        logger.warning("LTE for p=2 requires special handling")

    if p % 2 == 1:  # Odd prime
        # LTE: vₚ(aⁿ - bⁿ) = vₚ(a - b) + vₚ(n)
        return p_adic_valuation(a - b, p) + p_adic_valuation(n, p)
    else:
        # p=2 case is more complex
        return 0  # Placeholder


# =============================================================================
# MULTIPLICATIVE ORDER & PRIMITIVE ROOTS
# =============================================================================

def multiplicative_order(a: int, m: int) -> Optional[int]:
    """
    Compute multiplicative order of a modulo m: ord_m(a).

    ord_m(a) = smallest k > 0 such that a^k ≡ 1 (mod m).

    Args:
        a: Base
        m: Modulus

    Returns:
        ord_m(a), or None if gcd(a, m) ≠ 1

    Example:
        >>> multiplicative_order(2, 7)
        3  # 2³ ≡ 1 (mod 7)
        >>> multiplicative_order(3, 7)
        6  # 3^6 ≡ 1 (mod 7)

    Complexity:
        O(√φ(m))

    References:
        - Burton, Elementary Number Theory, Section 8.1
    """
    if gcd(a, m) != 1:
        return None  # Order undefined

    a = a % m
    phi_m = euler_phi(m)

    # Order divides φ(m)
    divisors = []
    for d in range(1, int(phi_m**0.5) + 1):
        if phi_m % d == 0:
            divisors.append(d)
            if d != phi_m // d:
                divisors.append(phi_m // d)

    divisors.sort()

    for d in divisors:
        if pow(a, d, m) == 1:
            return d

    return phi_m


def is_primitive_root(g: int, m: int) -> bool:
    """
    Test if g is a primitive root modulo m.

    g is a primitive root mod m if ord_m(g) = φ(m).

    Args:
        g: Candidate primitive root
        m: Modulus

    Returns:
        True if g is a primitive root mod m

    Example:
        >>> is_primitive_root(3, 7)
        True  # 3 generates (ℤ/7ℤ)*
        >>> is_primitive_root(2, 7)
        False  # 2³ ≡ 1 (mod 7), order 3 < φ(7)=6

    Complexity:
        O(√φ(m))
    """
    order = multiplicative_order(g, m)
    if order is None:
        return False

    return order == euler_phi(m)


def find_primitive_root(m: int) -> Optional[int]:
    """
    Find a primitive root modulo m (if exists).

    Primitive roots exist for m = 1, 2, 4, p^k, 2p^k (p odd prime).

    Args:
        m: Modulus

    Returns:
        Smallest primitive root, or None if none exist

    Example:
        >>> find_primitive_root(7)
        3  # Smallest primitive root mod 7
        >>> find_primitive_root(8)
        None  # No primitive roots mod 8

    Complexity:
        O(m · √φ(m)) in worst case
    """
    if not primitive_root_exists(m):
        return None

    for g in range(1, m):
        if is_primitive_root(g, m):
            return g

    return None


def primitive_root_exists(m: int) -> bool:
    """
    Check if primitive roots exist for modulus m.

    Primitive roots exist iff m ∈ {1, 2, 4, p^k, 2p^k} for odd prime p.

    Args:
        m: Modulus

    Returns:
        True if primitive roots exist

    Example:
        >>> primitive_root_exists(7)
        True  # 7 is prime
        >>> primitive_root_exists(8)
        False  # 8 = 2³ with 3 > 2

    References:
        - Gauss, Disquisitiones Arithmeticae, Article 92
    """
    if m <= 0:
        return False

    if m in (1, 2, 4):
        return True

    # Check if m = p^k for odd prime p
    if m % 2 != 0:
        factors = prime_factorization(m)
        if len(factors) == 1:
            return True  # m = p^k
        return False

    # Check if m = 2p^k for odd prime p
    if m % 2 == 0:
        m_odd = m // 2
        while m_odd % 2 == 0:
            m_odd //= 2

        if m_odd == m // 2:  # m was 2 * odd
            factors = prime_factorization(m_odd)
            if len(factors) == 1:
                return True

    return False
