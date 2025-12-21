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
FINITE FIELDS CORE MODULE - Pure Python Implementation
======================================================

Native implementations of finite field algorithms:
- Prime field GF(p) operations
- Extension field GF(p^n) construction
- Polynomial arithmetic over GF(p)
- Irreducibility testing (Rabin algorithm)
- Minimal polynomial computation
- Frobenius endomorphism

Part of the SYMBO_AGENTIC_REASONERS native computation engine.

NO SYMPY - Pure Python using core/number_theory_native.py functions.

REFERENCE:
---------
- Lidl, R., & Niederreiter, H. (1997). Finite Fields (2nd ed.). Cambridge University Press.
- Shoup, V. (2005). A Computational Introduction to Number Theory and Algebra. Cambridge University Press.
- Cohen, H. (1993). A Course in Computational Algebraic Number Theory. Springer.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

# Import from existing number theory native module
try:
    from symbo_agentic_reasoners.core.number_theory_native import (
        gcd, extended_gcd, is_prime, mod_inverse, prime_factorization
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


# ========================================
# GF(p) - Prime Field Elements
# ========================================

class GFpElement:
    """
    Element of a prime field GF(p).

    Represents an integer modulo a prime p.
    """

    def __init__(self, value: int, p: int):
        """
        Initialize GF(p) element.

        Args:
            value: Integer value
            p: Prime modulus

        Raises:
            ValueError: If p is not prime
        """
        if not is_prime(p):
            raise ValueError(f"Modulus {p} must be prime for GF(p)")

        self.p = p
        self.value = value % p

    def __add__(self, other: 'GFpElement') -> 'GFpElement':
        """Add two elements."""
        if self.p != other.p:
            raise ValueError("Cannot add elements from different fields")
        return GFpElement((self.value + other.value) % self.p, self.p)

    def __sub__(self, other: 'GFpElement') -> 'GFpElement':
        """Subtract two elements."""
        if self.p != other.p:
            raise ValueError("Cannot subtract elements from different fields")
        return GFpElement((self.value - other.value) % self.p, self.p)

    def __mul__(self, other: 'GFpElement') -> 'GFpElement':
        """Multiply two elements."""
        if self.p != other.p:
            raise ValueError("Cannot multiply elements from different fields")
        return GFpElement((self.value * other.value) % self.p, self.p)

    def __truediv__(self, other: 'GFpElement') -> 'GFpElement':
        """Divide by another element (multiply by inverse)."""
        if self.p != other.p:
            raise ValueError("Cannot divide elements from different fields")
        return self * other.inverse()

    def __pow__(self, exp: int) -> 'GFpElement':
        """Exponentiation using repeated squaring."""
        if exp < 0:
            return self.inverse() ** (-exp)

        result = GFpElement(1, self.p)
        base = GFpElement(self.value, self.p)

        while exp > 0:
            if exp % 2 == 1:
                result = result * base
            base = base * base
            exp //= 2

        return result

    def inverse(self) -> 'GFpElement':
        """Compute multiplicative inverse."""
        if self.value == 0:
            raise ValueError("Cannot compute inverse of zero element")

        inv = mod_inverse(self.value, self.p)
        if inv is None:
            raise ValueError(f"No inverse for {self.value} mod {self.p}")

        return GFpElement(inv, self.p)

    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, GFpElement):
            return False
        return self.p == other.p and self.value == other.value

    def __repr__(self) -> str:
        return f"GFpElement({self.value}, p={self.p})"

    def __str__(self) -> str:
        return f"{self.value} (mod {self.p})"


# ========================================
# Polynomial Operations over GF(p)
# ========================================

def polynomial_add(a: List[int], b: List[int], p: int) -> List[int]:
    """
    Add two polynomials over GF(p).

    Args:
        a: Coefficients of first polynomial [a0, a1, ..., an]
        b: Coefficients of second polynomial
        p: Prime modulus

    Returns:
        Coefficients of sum polynomial
    """
    max_len = max(len(a), len(b))
    a_padded = a + [0] * (max_len - len(a))
    b_padded = b + [0] * (max_len - len(b))

    result = [(a_padded[i] + b_padded[i]) % p for i in range(max_len)]

    # Remove leading zeros
    while len(result) > 1 and result[-1] == 0:
        result.pop()

    return result


def polynomial_multiply(a: List[int], b: List[int], p: int) -> List[int]:
    """
    Multiply two polynomials over GF(p).

    Args:
        a: Coefficients of first polynomial
        b: Coefficients of second polynomial
        p: Prime modulus

    Returns:
        Coefficients of product polynomial
    """
    if not a or not b:
        return [0]

    result = [0] * (len(a) + len(b) - 1)

    for i in range(len(a)):
        for j in range(len(b)):
            result[i + j] = (result[i + j] + a[i] * b[j]) % p

    # Remove leading zeros
    while len(result) > 1 and result[-1] == 0:
        result.pop()

    return result


def polynomial_mod(dividend: List[int], divisor: List[int], p: int) -> List[int]:
    """
    Compute polynomial remainder: dividend mod divisor over GF(p).

    Args:
        dividend: Dividend polynomial coefficients
        divisor: Divisor polynomial coefficients
        p: Prime modulus

    Returns:
        Remainder polynomial coefficients
    """
    if not divisor or (len(divisor) == 1 and divisor[0] == 0):
        raise ValueError("Division by zero polynomial")

    remainder = list(dividend)

    while len(remainder) >= len(divisor) and remainder[-1] != 0:
        # Compute leading coefficient quotient
        coeff = (remainder[-1] * mod_inverse(divisor[-1], p)) % p

        # Subtract divisor * coeff * x^(deg_diff) from remainder
        deg_diff = len(remainder) - len(divisor)
        for i in range(len(divisor)):
            remainder[i + deg_diff] = (remainder[i + deg_diff] - coeff * divisor[i]) % p

        # Remove leading term
        remainder.pop()

    # Remove leading zeros
    while len(remainder) > 1 and remainder[-1] == 0:
        remainder.pop()

    if not remainder:
        return [0]

    return remainder


def polynomial_mult_mod(a: List[int], b: List[int], mod_poly: List[int], p: int) -> List[int]:
    """
    Multiply two polynomials and reduce modulo another polynomial over GF(p).

    Args:
        a: First polynomial coefficients
        b: Second polynomial coefficients
        mod_poly: Modulus polynomial (typically irreducible)
        p: Prime characteristic

    Returns:
        Product polynomial reduced mod mod_poly
    """
    product = polynomial_multiply(a, b, p)
    return polynomial_mod(product, mod_poly, p)


def polynomial_gcd(a: List[int], b: List[int], p: int) -> List[int]:
    """
    Compute GCD of two polynomials over GF(p) using Euclidean algorithm.

    Args:
        a: First polynomial
        b: Second polynomial
        p: Prime modulus

    Returns:
        Monic GCD polynomial
    """
    while b != [0] and b:
        a, b = b, polynomial_mod(a, b, p)

    # Make monic
    if a and a[-1] != 0:
        leading_inv = mod_inverse(a[-1], p)
        if leading_inv is not None:
            a = [(coeff * leading_inv) % p for coeff in a]

    return a if a else [1]


# ========================================
# Irreducibility Testing
# ========================================

@lru_cache(maxsize=128)
def is_irreducible_rabin(poly_tuple: Tuple[int, ...], p: int) -> bool:
    """
    Test if polynomial is irreducible over GF(p) using Rabin's test.

    Rabin's Algorithm:
    1. Verify poly is square-free: gcd(f, f') = 1
    2. For each prime divisor q of n (degree):
       Check gcd(f(x), x^(p^(n/q)) - x) = 1
    3. Check f(x) divides (x^(p^n) - x)

    Args:
        poly_tuple: Polynomial coefficients as tuple (for caching)
        p: Prime modulus

    Returns:
        True if polynomial is irreducible, False otherwise
    """
    poly = list(poly_tuple)
    n = len(poly) - 1  # degree

    if n <= 0:
        return False
    if n == 1:
        return True  # Linear polynomials are always irreducible

    # Step 1: Check if square-free (gcd(f, f') = 1)
    derivative = polynomial_derivative(poly, p)
    g = polynomial_gcd(poly, derivative, p)
    if g != [1]:
        return False  # Not square-free

    # Step 2: For each prime divisor q of n, check gcd(f, x^(p^(n/q)) - x) = 1
    prime_divisors = get_prime_divisors(n)

    for q in prime_divisors:
        exp = p ** (n // q)
        # Compute x^exp mod poly
        x_power_mod = polynomial_power_mod([0, 1], exp, poly, p)
        # Compute x^exp - x
        x_power_minus_x = polynomial_add(x_power_mod, [0, -1], p)

        g = polynomial_gcd(poly, x_power_minus_x, p)
        if g != [1]:
            return False

    # Step 3: Check if f(x) divides (x^(p^n) - x)
    exp = p ** n
    x_power_mod = polynomial_power_mod([0, 1], exp, poly, p)
    x_power_minus_x = polynomial_add(x_power_mod, [0, -1], p)

    remainder = polynomial_mod(x_power_minus_x, poly, p)

    return remainder == [0]


def polynomial_derivative(poly: List[int], p: int) -> List[int]:
    """
    Compute derivative of polynomial over GF(p).

    d/dx (a_n x^n + ... + a_1 x + a_0) = n*a_n x^(n-1) + ... + a_1

    Args:
        poly: Polynomial coefficients
        p: Prime modulus

    Returns:
        Derivative polynomial
    """
    if len(poly) <= 1:
        return [0]

    derivative = [(i * poly[i]) % p for i in range(1, len(poly))]

    # Remove leading zeros
    while len(derivative) > 1 and derivative[-1] == 0:
        derivative.pop()

    return derivative if derivative else [0]


def get_prime_divisors(n: int) -> List[int]:
    """
    Get unique prime divisors of n.

    Args:
        n: Integer to factor

    Returns:
        List of prime divisors
    """
    if n <= 1:
        return []

    factors = prime_factorization(n)
    # prime_factorization returns tuple of (prime, exponent) pairs
    # e.g., ((2, 2), (3, 1)) for n=12
    return [p for p, _ in factors]


def polynomial_power_mod(poly: List[int], exp: int, mod_poly: List[int], p: int) -> List[int]:
    """
    Compute poly^exp mod mod_poly over GF(p) using repeated squaring.

    Args:
        poly: Base polynomial
        exp: Exponent
        mod_poly: Modulus polynomial
        p: Prime characteristic

    Returns:
        poly^exp reduced mod mod_poly
    """
    result = [1]  # Identity polynomial
    base = list(poly)

    while exp > 0:
        if exp % 2 == 1:
            result = polynomial_mult_mod(result, base, mod_poly, p)
        base = polynomial_mult_mod(base, base, mod_poly, p)
        exp //= 2

    return result


# ========================================
# Finding Irreducible Polynomials
# ========================================

def find_irreducible_polynomial(p: int, degree: int, primitive: bool = False) -> Optional[List[int]]:
    """
    Find an irreducible (optionally primitive) polynomial of given degree over GF(p).

    Args:
        p: Prime modulus
        degree: Degree of polynomial to find
        primitive: If True, find primitive polynomial (generates full multiplicative group)

    Returns:
        Coefficients of irreducible polynomial, or None if not found

    Raises:
        ValueError: If p is not prime or degree < 1
    """
    if not is_prime(p):
        raise ValueError(f"p={p} must be prime")
    if degree < 1:
        raise ValueError(f"degree={degree} must be positive")

    # For small cases, use brute force enumeration
    if degree <= 10 or (p == 2 and degree <= 20):
        return _brute_force_irreducible(p, degree, primitive)

    # For larger cases, use probabilistic search
    max_attempts = 1000
    for _ in range(max_attempts):
        candidate = _random_monic_polynomial(p, degree)
        if is_irreducible_rabin(tuple(candidate), p):
            if not primitive or is_primitive_polynomial(candidate, p):
                return candidate

    logger.warning(f"Failed to find irreducible polynomial of degree {degree} over GF({p})")
    return None


def _brute_force_irreducible(p: int, degree: int, primitive: bool = False) -> Optional[List[int]]:
    """
    Brute force search for irreducible polynomial.

    Enumerate all monic polynomials of given degree and test each.
    """
    # Monic polynomial: leading coefficient = 1
    # Need to enumerate all combinations of coefficients for lower degree terms
    num_coeffs = degree  # Don't include leading coefficient (always 1)
    total_combinations = p ** num_coeffs

    for i in range(total_combinations):
        # Generate coefficients
        coeffs = []
        val = i
        for _ in range(num_coeffs):
            coeffs.append(val % p)
            val //= p

        # Add leading coefficient
        coeffs.append(1)

        if is_irreducible_rabin(tuple(coeffs), p):
            if not primitive or is_primitive_polynomial(coeffs, p):
                return coeffs

    return None


def _random_monic_polynomial(p: int, degree: int) -> List[int]:
    """Generate random monic polynomial of given degree over GF(p)."""
    import random
    coeffs = [random.randint(0, p-1) for _ in range(degree)]
    coeffs.append(1)  # Monic (leading coefficient = 1)
    return coeffs


def is_primitive_polynomial(poly: List[int], p: int) -> bool:
    """
    Check if irreducible polynomial is primitive.

    A primitive polynomial of degree n over GF(p) is one that has
    a root that generates the multiplicative group GF(p^n)*.

    This is equivalent to checking that the polynomial has order p^n - 1.

    Args:
        poly: Irreducible polynomial coefficients
        p: Prime modulus

    Returns:
        True if polynomial is primitive
    """
    n = len(poly) - 1
    order = p ** n - 1

    # Check if x^order ≡ 1 (mod poly)
    x_order = polynomial_power_mod([0, 1], order, poly, p)
    if x_order != [1]:
        return False

    # Check that x^(order/q) ≢ 1 for all prime divisors q of order
    prime_divs = get_prime_divisors(order)

    for q in prime_divs:
        exp = order // q
        x_power = polynomial_power_mod([0, 1], exp, poly, p)
        if x_power == [1]:
            return False  # Order divides order/q, so not primitive

    return True


# ========================================
# GF(p^n) - Extension Field Elements
# ========================================

class GFpnElement:
    """
    Element of extension field GF(p^n).

    Represented as polynomial in GF(p)[x] / <irred_poly>.
    """

    def __init__(self, coeffs: List[int], p: int, irred_poly: List[int]):
        """
        Initialize GF(p^n) element.

        Args:
            coeffs: Polynomial coefficients [a0, a1, ..., a_{n-1}]
            p: Prime characteristic
            irred_poly: Irreducible polynomial defining the field
        """
        if not is_prime(p):
            raise ValueError(f"p={p} must be prime")

        self.p = p
        self.irred_poly = irred_poly
        self.n = len(irred_poly) - 1  # degree of extension

        # Reduce coefficients mod p and ensure correct length
        self.coeffs = [(c % p) for c in coeffs]

        # Reduce polynomial mod irred_poly
        if len(self.coeffs) >= len(irred_poly):
            self.coeffs = polynomial_mod(self.coeffs, irred_poly, p)

        # Pad to length n
        while len(self.coeffs) < self.n:
            self.coeffs.append(0)

    def __add__(self, other: 'GFpnElement') -> 'GFpnElement':
        """Add two elements."""
        self._check_compatible(other)
        result_coeffs = polynomial_add(self.coeffs, other.coeffs, self.p)
        return GFpnElement(result_coeffs, self.p, self.irred_poly)

    def __sub__(self, other: 'GFpnElement') -> 'GFpnElement':
        """Subtract two elements."""
        self._check_compatible(other)
        neg_other = [(-c) % self.p for c in other.coeffs]
        result_coeffs = polynomial_add(self.coeffs, neg_other, self.p)
        return GFpnElement(result_coeffs, self.p, self.irred_poly)

    def __mul__(self, other: 'GFpnElement') -> 'GFpnElement':
        """Multiply two elements."""
        self._check_compatible(other)
        result_coeffs = polynomial_mult_mod(self.coeffs, other.coeffs, self.irred_poly, self.p)
        return GFpnElement(result_coeffs, self.p, self.irred_poly)

    def __pow__(self, exp: int) -> 'GFpnElement':
        """Exponentiation using repeated squaring."""
        if exp < 0:
            return self.inverse() ** (-exp)

        result_coeffs = polynomial_power_mod(self.coeffs, exp, self.irred_poly, self.p)
        return GFpnElement(result_coeffs, self.p, self.irred_poly)

    def inverse(self) -> 'GFpnElement':
        """
        Compute multiplicative inverse using extended Euclidean algorithm for polynomials.
        """
        if self.coeffs == [0] * self.n:
            raise ValueError("Cannot compute inverse of zero element")

        inv_coeffs = polynomial_extended_gcd(self.coeffs, self.irred_poly, self.p)
        return GFpnElement(inv_coeffs, self.p, self.irred_poly)

    def __truediv__(self, other: 'GFpnElement') -> 'GFpnElement':
        """Divide by another element."""
        self._check_compatible(other)
        return self * other.inverse()

    def _check_compatible(self, other: 'GFpnElement'):
        """Check if two elements are from compatible fields."""
        if self.p != other.p or self.irred_poly != other.irred_poly:
            raise ValueError("Elements must be from the same extension field")

    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, GFpnElement):
            return False
        return (self.p == other.p and
                self.irred_poly == other.irred_poly and
                self.coeffs == other.coeffs)

    def __repr__(self) -> str:
        return f"GFpnElement({self.coeffs}, p={self.p}, irred_poly={self.irred_poly})"

    def __str__(self) -> str:
        """String representation as polynomial."""
        if not self.coeffs or all(c == 0 for c in self.coeffs):
            return "0"

        terms = []
        for i, coeff in enumerate(self.coeffs):
            if coeff != 0:
                if i == 0:
                    terms.append(str(coeff))
                elif i == 1:
                    terms.append(f"{coeff}*x" if coeff != 1 else "x")
                else:
                    terms.append(f"{coeff}*x^{i}" if coeff != 1 else f"x^{i}")

        return " + ".join(terms) if terms else "0"


def polynomial_extended_gcd(a: List[int], b: List[int], p: int) -> List[int]:
    """
    Extended Euclidean algorithm for polynomials over GF(p).

    Finds u such that a*u + b*v = gcd(a, b) (mod p).
    For irreducible b, gcd(a, b) = 1, so returns a^(-1) mod b.

    Args:
        a: First polynomial
        b: Second polynomial (typically irreducible)
        p: Prime modulus

    Returns:
        Polynomial u such that a*u ≡ 1 (mod b)
    """
    old_r, r = list(a), list(b)
    old_s, s = [1], [0]

    while r != [0]:
        # Compute quotient
        quotient = polynomial_divide(old_r, r, p)

        # Update r: old_r - quotient * r
        old_r, r = r, polynomial_add(old_r,
                                      [(-c) % p for c in polynomial_multiply(quotient, r, p)],
                                      p)

        # Update s: old_s - quotient * s
        old_s, s = s, polynomial_add(old_s,
                                      [(-c) % p for c in polynomial_multiply(quotient, s, p)],
                                      p)

    # Make result monic
    if old_r and old_r[-1] != 0:
        leading_inv = mod_inverse(old_r[-1], p)
        if leading_inv is not None:
            old_s = [(coeff * leading_inv) % p for coeff in old_s]

    return old_s if old_s else [1]


def polynomial_divide(dividend: List[int], divisor: List[int], p: int) -> List[int]:
    """
    Divide two polynomials over GF(p), return quotient.

    Args:
        dividend: Dividend polynomial
        divisor: Divisor polynomial
        p: Prime modulus

    Returns:
        Quotient polynomial
    """
    if not divisor or (len(divisor) == 1 and divisor[0] == 0):
        raise ValueError("Division by zero polynomial")

    quotient = []
    remainder = list(dividend)

    while len(remainder) >= len(divisor) and remainder[-1] != 0:
        # Leading coefficient of quotient term
        coeff = (remainder[-1] * mod_inverse(divisor[-1], p)) % p
        quotient.append(coeff)

        # Subtract divisor * coeff * x^(deg_diff) from remainder
        deg_diff = len(remainder) - len(divisor)
        for i in range(len(divisor)):
            remainder[i + deg_diff] = (remainder[i + deg_diff] - coeff * divisor[i]) % p

        remainder.pop()

    quotient.reverse()
    return quotient if quotient else [0]


# ========================================
# Frobenius Endomorphism & Minimal Polynomials
# ========================================

def frobenius_map(elem: GFpnElement, p: int) -> GFpnElement:
    """
    Apply Frobenius endomorphism: α → α^p.

    The Frobenius map is linear over GF(p):
    (α + β)^p = α^p + β^p

    Args:
        elem: Element of GF(p^n)
        p: Prime characteristic

    Returns:
        elem^p in GF(p^n)
    """
    return elem ** p


def minimal_polynomial(elem: GFpnElement, base_prime: int) -> List[int]:
    """
    Compute minimal polynomial of element over base field GF(base_prime).

    Algorithm:
    1. Compute Frobenius conjugates: α, α^p, α^(p^2), ..., α^(p^(k-1))
    2. Find smallest k such that α^(p^k) = α
    3. Minimal poly = product of (x - conjugate_i) over distinct conjugates

    Args:
        elem: Element of GF(p^n)
        base_prime: Prime p of base field GF(p)

    Returns:
        Coefficients of minimal polynomial over GF(p)
    """
    if base_prime != elem.p:
        raise ValueError("Base prime must match element's field characteristic")

    # Compute conjugates until we cycle back
    conjugates = [elem]
    current = frobenius_map(elem, base_prime)

    while current != elem:
        conjugates.append(current)
        current = frobenius_map(current, base_prime)

        if len(conjugates) > elem.n:
            # Safety check - should not exceed extension degree
            break

    # Build minimal polynomial as product of (x - conjugate_i)
    # Start with (x - conjugates[0])
    min_poly = [(-conjugates[0].coeffs[0]) % elem.p, 1]  # x - α₀

    for i in range(1, len(conjugates)):
        # Multiply by (x - conjugates[i])
        factor = [(-conjugates[i].coeffs[0]) % elem.p, 1]
        min_poly = polynomial_multiply(min_poly, factor, elem.p)

    return min_poly


# ========================================
# Utility Functions
# ========================================

def create_extension_field(p: int, n: int, irred_poly: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Create extension field GF(p^n) structure.

    Args:
        p: Prime characteristic
        n: Extension degree
        irred_poly: Optional irreducible polynomial (auto-find if None)

    Returns:
        Field structure dictionary with metadata
    """
    if not is_prime(p):
        raise ValueError(f"p={p} must be prime")
    if n < 1:
        raise ValueError(f"Extension degree n={n} must be positive")

    # Find irreducible polynomial if not provided
    if irred_poly is None:
        irred_poly = find_irreducible_polynomial(p, n)
        if irred_poly is None:
            raise ValueError(f"Could not find irreducible polynomial of degree {n} over GF({p})")
    else:
        # Verify provided polynomial is irreducible
        if not is_irreducible_rabin(tuple(irred_poly), p):
            raise ValueError("Provided polynomial is not irreducible")

    return {
        'p': p,
        'n': n,
        'order': p ** n,
        'irred_poly': irred_poly,
        'characteristic': p,
        'degree': n,
        'primitive': is_primitive_polynomial(irred_poly, p)
    }


def element_order(elem: GFpnElement) -> int:
    """
    Compute multiplicative order of non-zero element.

    Order of α is smallest positive integer k such that α^k = 1.

    Args:
        elem: Non-zero element of GF(p^n)

    Returns:
        Multiplicative order
    """
    if elem.coeffs == [0] * elem.n:
        raise ValueError("Zero element has no multiplicative order")

    max_order = elem.p ** elem.n - 1

    # Check divisors of max_order
    divisors = _get_divisors(max_order)

    for d in sorted(divisors):
        if (elem ** d).coeffs == [1] + [0] * (elem.n - 1):
            return d

    return max_order


def _get_divisors(n: int) -> List[int]:
    """Get all divisors of n."""
    divisors = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:
                divisors.append(n // i)
    return divisors
