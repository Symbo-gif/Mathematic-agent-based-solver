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
Tests for Algorithm Improvements
=================================

Tests for advanced algorithms: Pollard's rho, binary GCD, etc.
"""

import pytest
import math


class TestBinaryGCD:
    """Tests for binary GCD (Stein's algorithm)."""

    def test_basic_gcd(self):
        """Basic GCD computation."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        assert binary_gcd(12, 8) == 4
        assert binary_gcd(17, 13) == 1
        assert binary_gcd(100, 80) == 20

    def test_gcd_with_zero(self):
        """GCD with zero."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        assert binary_gcd(0, 5) == 5
        assert binary_gcd(5, 0) == 5
        assert binary_gcd(0, 0) == 0

    def test_gcd_negative(self):
        """GCD with negative numbers."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        assert binary_gcd(-12, 8) == 4
        assert binary_gcd(12, -8) == 4
        assert binary_gcd(-12, -8) == 4

    def test_gcd_coprime(self):
        """GCD of coprime numbers is 1."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        assert binary_gcd(7, 11) == 1
        assert binary_gcd(13, 17) == 1
        assert binary_gcd(97, 101) == 1

    def test_gcd_same_number(self):
        """GCD of a number with itself."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        assert binary_gcd(42, 42) == 42
        assert binary_gcd(1, 1) == 1

    def test_gcd_powers_of_two(self):
        """GCD of powers of two."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        assert binary_gcd(16, 32) == 16
        assert binary_gcd(64, 48) == 16

    def test_gcd_large_numbers(self):
        """GCD of large numbers."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        a = 2**31 - 1  # Mersenne prime
        b = 2**19 - 1  # Another Mersenne prime
        # Two Mersenne primes are coprime
        assert binary_gcd(a, b) == 1

    def test_gcd_matches_math_gcd(self):
        """Binary GCD should match math.gcd."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        import math
        test_pairs = [
            (1071, 462), (12345, 67890), (10000, 15000),
            (999999, 1000000), (2**20, 3**12)
        ]
        for a, b in test_pairs:
            assert binary_gcd(a, b) == math.gcd(a, b)


class TestPollardRho:
    """Tests for Pollard's rho algorithm."""

    def test_factor_small_composite(self):
        """Factor small composite numbers."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        # 15 = 3 * 5
        factor = pollard_rho(15)
        assert factor in [3, 5]

    def test_factor_semiprime(self):
        """Factor semi-prime (product of two primes)."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        # 143 = 11 * 13
        factor = pollard_rho(143)
        assert factor in [11, 13]

    def test_factor_large_semiprime(self):
        """Factor larger semi-prime."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        # 10403 = 101 * 103
        factor = pollard_rho(10403)
        assert factor in [101, 103]

    def test_prime_returns_itself(self):
        """Prime number returns itself."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        assert pollard_rho(17) == 17
        assert pollard_rho(97) == 97

    def test_even_number_returns_two(self):
        """Even number returns 2."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        assert pollard_rho(100) == 2
        assert pollard_rho(128) == 2

    def test_small_input(self):
        """Small inputs handled correctly."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        assert pollard_rho(0) is None
        assert pollard_rho(1) is None
        assert pollard_rho(2) == 2


class TestAdvancedFactorization:
    """Tests for advanced factorization."""

    def test_factor_small_number(self):
        """Factor small numbers."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        # 12 = 2^2 * 3
        factors = advanced_factorization(12)
        assert dict(factors) == {2: 2, 3: 1}

    def test_factor_prime(self):
        """Prime has single factor."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        factors = advanced_factorization(97)
        assert factors == ((97, 1),)

    def test_factor_prime_power(self):
        """Factor prime power."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        # 2^10 = 1024
        factors = advanced_factorization(1024)
        assert factors == ((2, 10),)

    def test_factor_semiprime(self):
        """Factor semi-prime."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        # 143 = 11 * 13
        factors = advanced_factorization(143)
        assert dict(factors) == {11: 1, 13: 1}

    def test_factor_large_semiprime(self):
        """Factor larger semi-prime."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        # 1000003 * 1000033 = 1000036000099
        n = 1000003 * 1000033
        factors = advanced_factorization(n)
        factor_dict = dict(factors)
        assert 1000003 in factor_dict
        assert 1000033 in factor_dict

    def test_factor_one(self):
        """Factor of 1 is empty."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        assert advanced_factorization(1) == ()

    def test_factor_zero(self):
        """Factor of 0 is empty."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        assert advanced_factorization(0) == ()

    def test_factors_multiply_to_original(self):
        """Product of factors equals original."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        test_numbers = [360, 1000, 12345, 99999, 2**15 * 3**5]
        for n in test_numbers:
            factors = advanced_factorization(n)
            product = 1
            for p, e in factors:
                product *= p ** e
            assert product == n


class TestGCDFunction:
    """Tests for the main gcd function using binary GCD."""

    def test_gcd_uses_binary_algorithm(self):
        """Verify gcd uses binary_gcd."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd, binary_gcd
        # Results should be identical
        pairs = [(12, 8), (100, 35), (2**20, 3**10)]
        for a, b in pairs:
            assert gcd(a, b) == binary_gcd(a, b)


class TestLCMWithBinaryGCD:
    """Tests for LCM using binary GCD."""

    def test_lcm_basic(self):
        """Basic LCM computation."""
        from symbo_agentic_reasoners.core.number_theory_native import lcm
        assert lcm(4, 6) == 12
        assert lcm(3, 5) == 15
        assert lcm(7, 11) == 77

    def test_lcm_with_zero(self):
        """LCM with zero is zero."""
        from symbo_agentic_reasoners.core.number_theory_native import lcm
        assert lcm(0, 5) == 0
        assert lcm(5, 0) == 0

    def test_lcm_gcd_product(self):
        """Verify gcd(a,b) * lcm(a,b) = a * b."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd, lcm
        pairs = [(12, 18), (100, 45), (17, 23)]
        for a, b in pairs:
            assert gcd(a, b) * lcm(a, b) == a * b


class TestNewExports:
    """Tests for new module exports."""

    def test_pollard_rho_exported(self):
        """pollard_rho should be exported."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        assert callable(pollard_rho)

    def test_advanced_factorization_exported(self):
        """advanced_factorization should be exported."""
        from symbo_agentic_reasoners.core.number_theory_native import advanced_factorization
        assert callable(advanced_factorization)

    def test_binary_gcd_exported(self):
        """binary_gcd should be exported."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        assert callable(binary_gcd)


class TestAlgorithmPerformance:
    """Tests for algorithm performance characteristics."""

    def test_binary_gcd_handles_large_numbers(self):
        """Binary GCD should handle very large numbers."""
        from symbo_agentic_reasoners.core.number_theory_native import binary_gcd
        a = 2**100
        b = 2**80
        result = binary_gcd(a, b)
        assert result == 2**80

    def test_pollard_rho_faster_than_trial_division(self):
        """Pollard's rho should find factor of semi-prime quickly."""
        from symbo_agentic_reasoners.core.number_theory_native import pollard_rho
        import time
        # A semi-prime with two ~6 digit primes
        n = 100003 * 100019  # = 10002200057
        start = time.time()
        factor = pollard_rho(n)
        elapsed = time.time() - start
        assert factor in [100003, 100019]
        assert elapsed < 1.0  # Should complete quickly


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
