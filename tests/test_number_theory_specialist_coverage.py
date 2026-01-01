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
Tests for Number Theory Specialist Module
==========================================

Comprehensive tests for the NumberTheorySpecialist BDI agent.
"""

import pytest
from unittest.mock import MagicMock


class TestNumberTheorySpecialistInit:
    """Tests for NumberTheorySpecialist initialization."""

    def test_specialist_create(self):
        """Test creating number theory specialist."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()
        assert specialist.agent_id == 'numbertheory_specialist_001'
        assert specialist.tasks_executed == 0

    def test_specialist_custom_id(self):
        """Test creating with custom agent ID."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist(agent_id='custom_nt_001')
        assert specialist.agent_id == 'custom_nt_001'

    def test_specialist_with_df(self):
        """Test creating with directory facilitator."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        mock_df = MagicMock()
        specialist = NumberTheorySpecialist(df=mock_df)
        assert specialist.df is mock_df
        mock_df.register.assert_called_once()


class TestPrimalityTesting:
    """Tests for primality testing functionality."""

    def test_is_prime_small_prime(self):
        """Test primality of small primes."""
        from symbo_agentic_reasoners.core.number_theory_native import is_prime
        assert is_prime(2) is True
        assert is_prime(3) is True
        assert is_prime(5) is True
        assert is_prime(7) is True
        assert is_prime(11) is True
        assert is_prime(13) is True

    def test_is_prime_small_composite(self):
        """Test composites are not prime."""
        from symbo_agentic_reasoners.core.number_theory_native import is_prime
        assert is_prime(4) is False
        assert is_prime(6) is False
        assert is_prime(8) is False
        assert is_prime(9) is False
        assert is_prime(10) is False

    def test_is_prime_one(self):
        """Test 1 is not prime."""
        from symbo_agentic_reasoners.core.number_theory_native import is_prime
        assert is_prime(1) is False

    def test_is_prime_zero(self):
        """Test 0 is not prime."""
        from symbo_agentic_reasoners.core.number_theory_native import is_prime
        assert is_prime(0) is False

    def test_is_prime_large_prime(self):
        """Test larger primes."""
        from symbo_agentic_reasoners.core.number_theory_native import is_prime
        assert is_prime(97) is True
        assert is_prime(101) is True
        assert is_prime(127) is True


class TestFactorization:
    """Tests for integer factorization."""

    def test_factor_prime(self):
        """Test factoring a prime number."""
        from symbo_agentic_reasoners.core.number_theory_native import prime_factorization
        factors = prime_factorization(7)
        # Native implementation returns tuple of (prime, exponent) pairs
        if isinstance(factors, dict):
            assert factors == {7: 1}
        else:
            assert (7, 1) in factors

    def test_factor_composite(self):
        """Test factoring composite numbers."""
        from symbo_agentic_reasoners.core.number_theory_native import prime_factorization
        factors = prime_factorization(12)
        # 12 = 2^2 * 3
        if isinstance(factors, dict):
            assert factors == {2: 2, 3: 1}
        else:
            factors_list = list(factors)
            assert (2, 2) in factors_list
            assert (3, 1) in factors_list

    def test_factor_power_of_prime(self):
        """Test factoring powers of primes."""
        from symbo_agentic_reasoners.core.number_theory_native import prime_factorization
        factors = prime_factorization(8)  # 2^3
        if isinstance(factors, dict):
            assert factors == {2: 3}
        else:
            assert (2, 3) in list(factors)
        factors = prime_factorization(27)  # 3^3
        if isinstance(factors, dict):
            assert factors == {3: 3}
        else:
            assert (3, 3) in list(factors)

    def test_factor_one(self):
        """Test factoring 1."""
        from symbo_agentic_reasoners.core.number_theory_native import prime_factorization
        factors = prime_factorization(1)
        # 1 has no prime factors
        if isinstance(factors, dict):
            assert factors == {}
        else:
            assert len(list(factors)) == 0


class TestGCDLCM:
    """Tests for GCD and LCM computation."""

    def test_gcd_simple(self):
        """Test simple GCD."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        assert gcd(12, 8) == 4
        assert gcd(15, 10) == 5
        assert gcd(17, 13) == 1  # Coprime

    def test_gcd_with_zero(self):
        """Test GCD with zero."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        assert gcd(5, 0) == 5
        assert gcd(0, 5) == 5

    def test_gcd_same_number(self):
        """Test GCD of number with itself."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        assert gcd(7, 7) == 7

    def test_lcm_simple(self):
        """Test simple LCM."""
        from symbo_agentic_reasoners.core.number_theory_native import lcm
        assert lcm(4, 6) == 12
        assert lcm(3, 5) == 15
        assert lcm(12, 8) == 24

    def test_lcm_with_one(self):
        """Test LCM with 1."""
        from symbo_agentic_reasoners.core.number_theory_native import lcm
        assert lcm(1, 7) == 7
        assert lcm(7, 1) == 7


class TestTotient:
    """Tests for Euler's totient function."""

    def test_totient_prime(self):
        """Test totient of prime is p-1."""
        from symbo_agentic_reasoners.core.number_theory_native import totient
        assert totient(7) == 6
        assert totient(11) == 10
        assert totient(13) == 12

    def test_totient_prime_power(self):
        """Test totient of prime powers."""
        from symbo_agentic_reasoners.core.number_theory_native import totient
        # phi(p^k) = p^k - p^(k-1) = p^(k-1) * (p-1)
        assert totient(4) == 2  # phi(2^2) = 2
        assert totient(8) == 4  # phi(2^3) = 4
        assert totient(9) == 6  # phi(3^2) = 6

    def test_totient_composite(self):
        """Test totient of composite numbers."""
        from symbo_agentic_reasoners.core.number_theory_native import totient
        assert totient(6) == 2   # phi(6) = phi(2)*phi(3) = 1*2 = 2
        assert totient(10) == 4  # phi(10) = phi(2)*phi(5) = 1*4 = 4
        assert totient(12) == 4  # phi(12) = 12*(1-1/2)*(1-1/3) = 4


class TestModularArithmetic:
    """Tests for modular arithmetic operations."""

    def test_mod_inverse_simple(self):
        """Test modular inverse."""
        from symbo_agentic_reasoners.core.number_theory_native import mod_inverse
        # 3 * 7 = 21 ≡ 1 (mod 10)
        assert mod_inverse(3, 10) == 7
        # 2 * 3 = 6 ≡ 1 (mod 5)
        assert mod_inverse(2, 5) == 3

    def test_mod_inverse_no_inverse(self):
        """Test when no modular inverse exists."""
        from symbo_agentic_reasoners.core.number_theory_native import mod_inverse
        # 2 has no inverse mod 4 (gcd(2,4) = 2 ≠ 1)
        result = mod_inverse(2, 4)
        assert result is None


class TestSpecialistProcess:
    """Tests for specialist process method."""

    def test_process_primality(self):
        """Test processing primality test task."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()

        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': 'is 7 prime', 'sympy_expr': '7'}

        result = specialist.process(mock_task)
        assert specialist.tasks_executed == 1

    def test_process_factorization(self):
        """Test processing factorization task."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()

        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': 'factor 12', 'sympy_expr': '12'}

        result = specialist.process(mock_task)
        assert specialist.tasks_executed == 1

    def test_process_gcd(self):
        """Test processing GCD task."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()

        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': 'gcd(12, 8)', 'sympy_expr': 'gcd(12, 8)'}

        result = specialist.process(mock_task)
        assert specialist.tasks_executed == 1

    def test_process_lcm(self):
        """Test processing LCM task."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()

        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': 'lcm(4, 6)', 'sympy_expr': 'lcm(4, 6)'}

        result = specialist.process(mock_task)
        assert specialist.tasks_executed == 1

    def test_process_modular(self):
        """Test processing modular arithmetic task."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()

        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': '17 mod 5', 'sympy_expr': 'Mod(17, 5)'}

        result = specialist.process(mock_task)
        assert specialist.tasks_executed == 1


class TestSpecialistBDI:
    """Tests for BDI methods."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs without blackboard."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()
        specialist.update_beliefs()  # Should not raise

    def test_deliberate_no_tasks(self):
        """Test deliberate with no pending tasks."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()
        intentions = specialist.deliberate()
        assert intentions == []

    def test_get_statistics(self):
        """Test getting agent statistics."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        specialist = NumberTheorySpecialist()

        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': 'is 7 prime'}
        specialist.process(mock_task)

        stats = specialist.get_statistics()
        assert 'tasks_executed' in stats
        assert stats['tasks_executed'] >= 1


class TestModuleImports:
    """Tests for module imports."""

    def test_specialist_import(self):
        """Test NumberTheorySpecialist can be imported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        assert NumberTheorySpecialist is not None

    def test_native_functions_import(self):
        """Test native number theory functions can be imported."""
        from symbo_agentic_reasoners.core.number_theory_native import (
            is_prime, prime_factorization, totient, gcd, lcm, mod_inverse
        )
        assert callable(is_prime)
        assert callable(prime_factorization)
        assert callable(totient)
        assert callable(gcd)
        assert callable(lcm)
        assert callable(mod_inverse)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
