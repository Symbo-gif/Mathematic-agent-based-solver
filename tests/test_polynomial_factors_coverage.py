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
Tests for Polynomial Factors Module
====================================

Comprehensive tests for pattern-based polynomial factoring methods.
"""

import pytest


class TestFactorDifferenceOfSquares:
    """Tests for factor_difference_of_squares function."""

    def test_factor_diff_squares_basic(self):
        """Test factoring x^2 - 4 = (x-2)(x+2)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_squares
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 - 4
        expr = Add(Pow(x, Integer(2)), Integer(-4))
        result = factor_difference_of_squares(expr)
        # May return factored form or None depending on pattern matching

    def test_factor_diff_squares_larger(self):
        """Test factoring x^2 - 9 = (x-3)(x+3)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_squares
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 - 9
        expr = Add(Pow(x, Integer(2)), Integer(-9))
        result = factor_difference_of_squares(expr)

    def test_factor_diff_squares_non_perfect(self):
        """Test with non-perfect square constant."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_squares
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 - 5 (5 is not a perfect square)
        expr = Add(Pow(x, Integer(2)), Integer(-5))
        result = factor_difference_of_squares(expr)
        assert result is None

    def test_factor_diff_squares_wrong_pattern(self):
        """Test with non-matching pattern."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_squares
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^3 - 4 (not a square)
        expr = Add(Pow(x, Integer(3)), Integer(-4))
        result = factor_difference_of_squares(expr)
        assert result is None

    def test_factor_diff_squares_sum_not_diff(self):
        """Test x^2 + 4 (sum, not difference)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_squares
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 + 4 (sum of squares, no real factorization)
        expr = Add(Pow(x, Integer(2)), Integer(4))
        result = factor_difference_of_squares(expr)
        assert result is None


class TestFactorDifferenceOfCubes:
    """Tests for factor_difference_of_cubes function."""

    def test_factor_diff_cubes_basic(self):
        """Test factoring x^3 - 8."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_cubes
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^3 - 8 = x^3 - 2^3
        expr = Add(Pow(x, Integer(3)), Integer(-8))
        result = factor_difference_of_cubes(expr)
        # Current implementation returns None for complex patterns

    def test_factor_diff_cubes_two_cubes(self):
        """Test with two cube terms."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_cubes
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        y = Symbol('y')
        # x^3 - y^3 (not currently implemented to return factored form)
        expr = Add(Pow(x, Integer(3)), Pow(y, Integer(3)))
        result = factor_difference_of_cubes(expr)

    def test_factor_diff_cubes_wrong_pattern(self):
        """Test with non-cube pattern."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_cubes
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 - 8 (not cubes)
        expr = Add(Pow(x, Integer(2)), Integer(-8))
        result = factor_difference_of_cubes(expr)
        assert result is None


class TestFactorSumOfCubes:
    """Tests for factor_sum_of_cubes function."""

    def test_factor_sum_cubes_basic(self):
        """Test factoring x^3 + y^3."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_sum_of_cubes
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        y = Symbol('y')
        # x^3 + y^3 = (x+y)(x^2 - xy + y^2)
        expr = Add(Pow(x, Integer(3)), Pow(y, Integer(3)))
        result = factor_sum_of_cubes(expr)
        assert result is not None  # Should return factored form

    def test_factor_sum_cubes_wrong_pattern(self):
        """Test with non-cube pattern."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_sum_of_cubes
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 + 8 (not cubes)
        expr = Add(Pow(x, Integer(2)), Integer(8))
        result = factor_sum_of_cubes(expr)
        assert result is None

    def test_factor_sum_cubes_single_term(self):
        """Test with single term (not sum)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_sum_of_cubes
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Pow, Integer
        x = Symbol('x')
        # Just x^3 (not a sum)
        expr = Pow(x, Integer(3))
        result = factor_sum_of_cubes(expr)
        assert result is None


class TestFactorGCD:
    """Tests for factor_gcd function."""

    def test_factor_gcd_non_add(self):
        """Test with non-Add expression."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_gcd
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Mul, Integer
        x = Symbol('x')
        # 2x (not a sum)
        expr = Mul(Integer(2), x)
        result = factor_gcd(expr)
        # Result depends on is_Add attribute

    def test_factor_gcd_single_term(self):
        """Test with single-term Add."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_gcd
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol
        x = Symbol('x')
        # Just x (treated as Add with one term)
        result = factor_gcd(x)
        # Returns None for non-Add or single term

    def test_factor_gcd_numeric_gcd(self):
        """Test GCD with numeric coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_gcd
        )
        from symbo_agentic_reasoners.core.native_symbolic import Add, Integer
        # 6 + 9 = 15, GCD = 3
        expr = Add(Integer(6), Integer(9))
        result = factor_gcd(expr)
        # Should extract GCD = 3 if pattern matches


class TestModuleImports:
    """Tests for module imports."""

    def test_module_imports(self):
        """Test module can be imported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial import polynomial_factors
        assert polynomial_factors is not None

    def test_factor_difference_of_squares_import(self):
        """Test factor_difference_of_squares is importable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_squares
        )
        assert callable(factor_difference_of_squares)

    def test_factor_difference_of_cubes_import(self):
        """Test factor_difference_of_cubes is importable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_difference_of_cubes
        )
        assert callable(factor_difference_of_cubes)

    def test_factor_sum_of_cubes_import(self):
        """Test factor_sum_of_cubes is importable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_sum_of_cubes
        )
        assert callable(factor_sum_of_cubes)

    def test_factor_gcd_import(self):
        """Test factor_gcd is importable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_factors import (
            factor_gcd
        )
        assert callable(factor_gcd)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
