"""
Number Theory Native Module - Pure Python Implementation
=========================================================

Provides SymPy-free number-theoretic functions for:
- Mobius function mu(n)
- Von Mangoldt function Lambda(n)
- Euler's totient phi(n)
- Divisor functions sigma_k(n)
- Prime generation and testing
- Number-theoretic series and products

Part of the SYMBO_AGENTIC_REASONERS native computation engine.
"""

import math
from typing import Dict, List, Tuple, Callable, Optional, Set, Union
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================

# Euler-Mascheroni constant (gamma)
EULER_GAMMA = 0.5772156649015328606065120900824024310421593359

# Stieltjes constants gamma_n (Laurent expansion of zeta at s=1)
STIELTJES_CONSTANTS = {
    0: 0.5772156649015328606065120900824024310421593359,   # gamma_0 = Euler-Mascheroni
    1: -0.0728158454836767248605863758749997190985211688,  # gamma_1
    2: -0.0096903631928723184845303860352125293590658061,  # gamma_2
    3: 0.0020538344203033458661600465427533842857158045,   # gamma_3
    4: 0.0023253700654673000574681701316138943914607673,   # gamma_4
    5: 0.0007933238173010627017533348774444448307315394,   # gamma_5
}

# Bernoulli numbers B_n for Stirling series
BERNOULLI_NUMBERS = {
    0: 1,
    1: -1/2,
    2: 1/6,
    4: -1/30,
    6: 1/42,
    8: -1/30,
    10: 5/66,
    12: -691/2730,
    14: 7/6,
    16: -3617/510,
    18: 43867/798,
    20: -174611/330,
}


# =============================================================================
# PRIME NUMBER FUNCTIONS
# =============================================================================

@lru_cache(maxsize=1)
def prime_sieve(limit: int = 100000) -> Tuple[int, ...]:
    """
    Sieve of Eratosthenes - generate all primes up to limit.

    Returns a tuple (hashable for caching) of primes.
    """
    if limit < 2:
        return ()

    # Boolean sieve
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False

    return tuple(i for i in range(2, limit + 1) if sieve[i])


def is_prime(n: int) -> bool:
    """
    Miller-Rabin primality test for integers.

    Deterministic for n < 3,317,044,064,679,887,385,961,981.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    if n < 9:
        return True
    if n % 3 == 0:
        return False

    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Witnesses to test (deterministic for n < 3,317,044,064,679,887,385,961,981)
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

    for a in witnesses:
        if a >= n:
            continue

        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


@lru_cache(maxsize=10000)
def prime_factorization(n: int) -> Tuple[Tuple[int, int], ...]:
    """
    Compute prime factorization of n.

    Returns tuple of (prime, exponent) pairs for hashability/caching.
    Example: prime_factorization(12) = ((2, 2), (3, 1)) meaning 2^2 * 3^1
    """
    if n < 1:
        return ()
    if n == 1:
        return ()

    factors = []
    d = 2

    while d * d <= n:
        exp = 0
        while n % d == 0:
            exp += 1
            n //= d
        if exp > 0:
            factors.append((d, exp))
        d += 1

    if n > 1:
        factors.append((n, 1))

    return tuple(factors)


def prime_factors(n: int) -> List[int]:
    """Return list of prime factors (without multiplicities)."""
    return [p for p, _ in prime_factorization(n)]


def divisors(n: int) -> List[int]:
    """Return all divisors of n in sorted order."""
    if n < 1:
        return []
    if n == 1:
        return [1]

    factors = prime_factorization(n)

    # Generate all divisors via Cartesian product of prime powers
    divs = [1]
    for p, e in factors:
        new_divs = []
        for d in divs:
            power = 1
            for _ in range(e + 1):
                new_divs.append(d * power)
                power *= p
        divs = new_divs

    return sorted(divs)


# =============================================================================
# CORE NUMBER-THEORETIC FUNCTIONS
# =============================================================================

@lru_cache(maxsize=10000)
def mobius(n: int) -> int:
    """
    Mobius function mu(n).

    Returns:
        0  if n has a squared prime factor
        1  if n is a product of an even number of distinct primes
       -1  if n is a product of an odd number of distinct primes

    Properties:
        - mu(1) = 1
        - sum_{d|n} mu(d) = 1 if n=1, else 0
        - Mobius inversion: if g(n) = sum_{d|n} f(d), then f(n) = sum_{d|n} mu(d)*g(n/d)
    """
    if n < 1:
        return 0
    if n == 1:
        return 1

    factors = prime_factorization(n)

    # Check for squared prime factors
    for _, exp in factors:
        if exp > 1:
            return 0

    # Count distinct prime factors
    num_primes = len(factors)
    return (-1) ** num_primes


@lru_cache(maxsize=10000)
def mangoldt(n: int) -> float:
    """
    Von Mangoldt function Lambda(n).

    Returns:
        log(p) if n = p^k for some prime p and k >= 1
        0      otherwise

    Properties:
        - sum_{d|n} Lambda(d) = log(n)
        - Useful in prime number theory: psi(x) = sum_{n<=x} Lambda(n) ~ x
    """
    if n < 1:
        return 0.0
    if n == 1:
        return 0.0

    factors = prime_factorization(n)

    # n must be a prime power (exactly one distinct prime factor)
    if len(factors) != 1:
        return 0.0

    p, _ = factors[0]
    return math.log(p)


@lru_cache(maxsize=10000)
def totient(n: int) -> int:
    """
    Euler's totient function phi(n).

    Returns the count of integers in [1, n] that are coprime to n.

    Formula: phi(n) = n * prod_{p|n} (1 - 1/p)

    Properties:
        - phi(1) = 1
        - phi(p) = p - 1 for prime p
        - phi(p^k) = p^(k-1) * (p - 1)
        - phi is multiplicative: phi(mn) = phi(m)*phi(n) if gcd(m,n) = 1
    """
    if n < 1:
        return 0
    if n == 1:
        return 1

    result = n
    factors = prime_factorization(n)

    for p, _ in factors:
        result = result // p * (p - 1)

    return result


@lru_cache(maxsize=10000)
def divisor_sigma(n: int, k: int = 1) -> int:
    """
    Divisor function sigma_k(n) = sum of k-th powers of divisors of n.

    Special cases:
        - sigma_0(n) = d(n) = number of divisors
        - sigma_1(n) = sigma(n) = sum of divisors
        - sigma_2(n) = sum of squares of divisors

    Formula: sigma_k(n) = prod_{p^a || n} (p^(k*(a+1)) - 1) / (p^k - 1)
    """
    if n < 1:
        return 0
    if n == 1:
        return 1

    factors = prime_factorization(n)
    result = 1

    for p, a in factors:
        if k == 0:
            result *= (a + 1)
        else:
            pk = p ** k
            result *= (pk ** (a + 1) - 1) // (pk - 1)

    return result


def liouville(n: int) -> int:
    """
    Liouville function lambda(n).

    Returns (-1)^Omega(n) where Omega(n) is the number of prime factors
    of n counted with multiplicity.

    Properties:
        - |lambda(n)| = 1 for all n >= 1
        - sum_{d|n} lambda(d) = 1 if n is a perfect square, else 0
    """
    if n < 1:
        return 0
    if n == 1:
        return 1

    factors = prime_factorization(n)
    omega = sum(exp for _, exp in factors)
    return (-1) ** omega


def omega(n: int) -> int:
    """
    omega(n) = number of distinct prime factors of n.
    """
    if n < 1:
        return 0
    return len(prime_factorization(n))


def big_omega(n: int) -> int:
    """
    Omega(n) = number of prime factors of n counted with multiplicity.
    """
    if n < 1:
        return 0
    return sum(exp for _, exp in prime_factorization(n))


# =============================================================================
# SERIES AND PRODUCT EVALUATION
# =============================================================================

def prime_product(func: Callable[[int], float], limit: int = 10000) -> float:
    """
    Evaluate product over primes: prod_{p <= limit} func(p).

    Args:
        func: Function to evaluate at each prime
        limit: Upper bound on primes to include

    Example:
        prime_product(lambda p: 1 - 1/p**2) = 6/pi^2 (Euler product for zeta(2))
    """
    primes = prime_sieve(limit)
    result = 1.0

    for p in primes:
        term = func(p)
        if term == 0:
            return 0.0
        result *= term

    return result


def number_theoretic_sum(
    func: Callable[[int], float],
    start: int,
    end: Union[int, float],
    max_terms: int = 100000
) -> Tuple[float, str]:
    """
    Evaluate sum_{n=start}^{end} func(n).

    Args:
        func: Function to sum (can use mobius, totient, etc.)
        start: Starting index
        end: Ending index (can be float('inf'))
        max_terms: Maximum terms to evaluate for infinite series

    Returns:
        (value, status) where status is 'exact', 'converged', or 'truncated'
    """
    if end == float('inf'):
        # Infinite series - check for convergence
        result = 0.0
        prev_result = float('inf')

        for n in range(start, start + max_terms):
            term = func(n)
            result += term

            # Check for convergence (relative change < 1e-12)
            if abs(result - prev_result) < abs(result) * 1e-12:
                return (result, 'converged')

            prev_result = result

        return (result, 'truncated')

    else:
        # Finite sum
        result = 0.0
        for n in range(start, int(end) + 1):
            result += func(n)
        return (result, 'exact')


def mobius_sum(f: Callable[[int], float], n: int) -> float:
    """
    Mobius inversion sum: sum_{d|n} mu(d) * f(n/d).

    If g(n) = sum_{d|n} f(d), this computes f(n) from g.
    """
    divs = divisors(n)
    return sum(mobius(d) * f(n // d) for d in divs)


def dirichlet_convolution(f: Callable[[int], float], g: Callable[[int], float], n: int) -> float:
    """
    Dirichlet convolution (f * g)(n) = sum_{d|n} f(d) * g(n/d).
    """
    divs = divisors(n)
    return sum(f(d) * g(n // d) for d in divs)


# =============================================================================
# SPECIAL SERIES PATTERNS
# =============================================================================

def evaluate_nt_series(series_type: str, params: Dict = None) -> Tuple[Optional[float], str]:
    """
    Evaluate known number-theoretic series patterns.

    Args:
        series_type: Type of series (e.g., 'mobius_log_squared', 'mangoldt_minus_1')
        params: Optional parameters for the series

    Returns:
        (value, method) or (None, 'not_recognized')
    """
    params = params or {}

    # sum_{n=2}^{oo} mu(n)/(n*(log(n))^2)
    # This series converges (Prime Number Theorem connection)
    if series_type == 'mobius_log_squared':
        def term(n):
            if n < 2:
                return 0.0
            return mobius(n) / (n * math.log(n) ** 2)

        result, status = number_theoretic_sum(term, 2, float('inf'), max_terms=50000)
        return (result, f'nt_series_{status}')

    # sum_{n=2}^{oo} mu(n)*log(n)/n^2
    # Related to derivative of 1/zeta(s) at s=2
    if series_type == 'mobius_log_over_nsq':
        def term(n):
            if n < 2:
                return 0.0
            return mobius(n) * math.log(n) / (n ** 2)

        result, status = number_theoretic_sum(term, 2, float('inf'), max_terms=50000)
        return (result, f'nt_series_{status}')

    # sum_{n=2}^{oo} (Lambda(n) - 1)/(n*log(n))
    if series_type == 'mangoldt_minus_1':
        def term(n):
            if n < 2:
                return 0.0
            lam = mangoldt(n)
            return (lam - 1) / (n * math.log(n))

        result, status = number_theoretic_sum(term, 2, float('inf'), max_terms=50000)
        return (result, f'nt_series_{status}')

    # sum_{n=1}^{oo} (phi(n) - 6n/pi^2)/n^3
    # phi(n) has average value 6n/pi^2
    if series_type == 'totient_deviation':
        pi_sq = math.pi ** 2
        def term(n):
            return (totient(n) - 6*n/pi_sq) / (n ** 3)

        result, status = number_theoretic_sum(term, 1, float('inf'), max_terms=50000)
        return (result, f'nt_series_{status}')

    # Euler product: prod_p (1 - 1/p^2)/(1 - 1/p)^2
    if series_type == 'euler_product_zeta_ratio':
        def factor(p):
            return (1 - 1/p**2) / (1 - 1/p)**2

        result = prime_product(factor, limit=50000)
        # This equals zeta(2)/zeta(1)^2 diverges, but the finite product converges
        return (result, 'prime_product_truncated')

    return (None, 'not_recognized')


# =============================================================================
# ALTERNATING SERIES WITH NT FLAVOR
# =============================================================================

def alternating_log_series(start: int = 3, max_terms: int = 100000) -> Tuple[float, str]:
    """
    Evaluate sum_{n=start}^{oo} ((-1)^n * log(n))/(n*(log(log(n)))^2).

    This is an alternating series with slow convergence.
    """
    result = 0.0
    prev_result = float('inf')

    for n in range(start, start + max_terms):
        try:
            log_n = math.log(n)
            log_log_n = math.log(log_n)
            if log_log_n <= 0:
                continue
            term = ((-1) ** n * log_n) / (n * log_log_n ** 2)
            result += term

            # Check convergence
            if abs(result - prev_result) < abs(result) * 1e-10:
                return (result, 'converged')
            prev_result = result
        except (ValueError, ZeroDivisionError):
            continue

    return (result, 'truncated')


# =============================================================================
# GCD, LCM, AND RELATED FUNCTIONS
# =============================================================================

def gcd(a: int, b: int) -> int:
    """Greatest common divisor using Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean algorithm.

    Returns (g, x, y) such that a*x + b*y = g = gcd(a, b).
    """
    if b == 0:
        return (a, 1, 0)

    g, x, y = extended_gcd(b, a % b)
    return (g, y, x - (a // b) * y)


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Modular multiplicative inverse of a mod m.

    Returns x such that (a * x) mod m = 1, or None if no inverse exists.
    """
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences: x = r_i (mod m_i).

    Requires moduli to be pairwise coprime.
    Returns the unique solution x in [0, M) where M = prod(moduli).
    """
    if len(remainders) != len(moduli):
        return None

    M = 1
    for m in moduli:
        M *= m

    result = 0
    for r, m in zip(remainders, moduli):
        Mi = M // m
        inv = mod_inverse(Mi, m)
        if inv is None:
            return None
        result += r * Mi * inv

    return result % M


# =============================================================================
# SPECIAL LIMITS AND ASYMPTOTICS
# =============================================================================

def chebyshev_theta(x: float) -> float:
    """
    Chebyshev theta function: theta(x) = sum_{p <= x} log(p).

    By PNT: theta(x) ~ x as x -> infinity.
    """
    primes = prime_sieve(int(x))
    return sum(math.log(p) for p in primes if p <= x)


def chebyshev_psi(x: float) -> float:
    """
    Chebyshev psi function: psi(x) = sum_{n <= x} Lambda(n).

    By PNT: psi(x) ~ x as x -> infinity.
    """
    return sum(mangoldt(n) for n in range(1, int(x) + 1))


def mertens_function(n: int) -> int:
    """
    Mertens function M(n) = sum_{k=1}^{n} mu(k).

    Known: M(n) = O(n^(1/2 + epsilon)) (equivalent to Riemann Hypothesis).
    """
    return sum(mobius(k) for k in range(1, n + 1))


def summatory_totient(n: int) -> int:
    """
    Summatory totient: Phi(n) = sum_{k=1}^{n} phi(k).

    Asymptotic: Phi(n) ~ 3n^2/pi^2.
    """
    return sum(totient(k) for k in range(1, n + 1))


# =============================================================================
# PATTERN DETECTION FOR SERIES
# =============================================================================

def detect_nt_series_pattern(expr_str: str) -> Tuple[Optional[str], Dict]:
    """
    Detect number-theoretic series patterns in expression string.

    Returns (series_type, params) or (None, {}) if not recognized.
    """
    import re

    expr = expr_str.replace(' ', '').lower()

    # Pattern: mu(n)/(n*(log(n))^2) or mobius(n)/(n*log(n)**2)
    if re.search(r'(mu|mobius)\(n\)/\(n\*(\(log\(n\)\)|log\(n\))\*\*2\)', expr):
        return ('mobius_log_squared', {})

    # Pattern: mu(n)*log(n)/n^2
    if re.search(r'(mu|mobius)\(n\)\*log\(n\)/n\*\*2', expr):
        return ('mobius_log_over_nsq', {})

    # Pattern: (Lambda(n) - 1)/(n*log(n))
    if re.search(r'\(lambda\(n\)-1\)/\(n\*log\(n\)\)', expr):
        return ('mangoldt_minus_1', {})

    # Pattern: (phi(n) - 6*n/pi^2)/n^3
    if re.search(r'\(phi\(n\)-.*\)/n\*\*3', expr):
        return ('totient_deviation', {})

    # Pattern: product over primes
    if 'product' in expr and 'prime' in expr:
        return ('euler_product_zeta_ratio', {})

    return (None, {})


# =============================================================================
# INTEGRATION WITH NATIVE CALCULUS
# =============================================================================

def evaluate_nt_limit(expr_str: str, var: str, point: str) -> Tuple[Optional[str], str]:
    """
    Evaluate limits involving number-theoretic functions.

    Handles patterns like:
        - sum_{n=1}^{N} phi(n) / N^2 -> 3/pi^2 as N -> oo
        - M(N)/sqrt(N) -> bounded (Mertens)
        - psi(N)/N -> 1 (Prime Number Theorem)
    """
    expr = expr_str.replace(' ', '').lower()

    # Summatory totient: Phi(N)/N^2 -> 3/pi^2
    if 'phi' in expr and '/n**2' in expr:
        return ('3/pi**2', 'summatory_totient_asymptotic')

    # Chebyshev psi: psi(N)/N -> 1
    if 'psi' in expr and '/n' in expr:
        return ('1', 'prime_number_theorem')

    # Chebyshev theta: theta(N)/N -> 1
    if 'theta' in expr and '/n' in expr:
        return ('1', 'prime_number_theorem')

    return (None, 'not_recognized')


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    'EULER_GAMMA',
    'STIELTJES_CONSTANTS',
    'BERNOULLI_NUMBERS',

    # Prime functions
    'prime_sieve',
    'is_prime',
    'prime_factorization',
    'prime_factors',
    'divisors',

    # Core NT functions
    'mobius',
    'mangoldt',
    'totient',
    'divisor_sigma',
    'liouville',
    'omega',
    'big_omega',

    # Series/Products
    'prime_product',
    'number_theoretic_sum',
    'mobius_sum',
    'dirichlet_convolution',
    'evaluate_nt_series',
    'alternating_log_series',

    # GCD/LCM
    'gcd',
    'lcm',
    'extended_gcd',
    'mod_inverse',
    'chinese_remainder_theorem',

    # Special functions
    'chebyshev_theta',
    'chebyshev_psi',
    'mertens_function',
    'summatory_totient',

    # Pattern detection
    'detect_nt_series_pattern',
    'evaluate_nt_limit',
]
