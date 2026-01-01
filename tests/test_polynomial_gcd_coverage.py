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
Tests for Polynomial GCD Module
================================

Comprehensive tests for polynomial GCD and resultant operations.
"""

import pytest


class TestPolynomialGCD:
    """Tests for polynomial_gcd function."""

    def test_gcd_same_polynomial(self):
        """Test GCD of polynomial with itself."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_gcd
        )
        p = [1.0, 2.0, 1.0]  # 1 + 2x + x^2 = (1+x)^2
        result = polynomial_gcd(p, p)
        assert len(result) > 0

    def test_gcd_constant_polynomial(self):
        """Test GCD with constant polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_gcd
        )
        p = [1.0, 2.0, 1.0]
        q = [3.0]  # constant 3
        result = polynomial_gcd(p, q)
        assert len(result) == 1  # GCD is a constant

    def test_gcd_zero_polynomial(self):
        """Test GCD with zero polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_gcd
        )
        p = [1.0, 2.0, 1.0]
        q = [0.0, 0.0, 0.0]
        result = polynomial_gcd(p, q)
        assert len(result) > 0

    def test_gcd_coprime_polynomials(self):
        """Test GCD of coprime polynomials."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_gcd
        )
        # x + 1 and x + 2 are coprime
        p = [1.0, 1.0]
        q = [2.0, 1.0]
        result = polynomial_gcd(p, q)
        # GCD should be 1 (constant)
        assert len(result) == 1

    def test_gcd_common_factor(self):
        """Test GCD with common factor."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_gcd
        )
        # (x+1)*(x+2) and (x+1)*(x+3)
        # Common factor is (x+1)
        p = [2.0, 3.0, 1.0]  # (x+1)(x+2) = x^2 + 3x + 2
        q = [3.0, 4.0, 1.0]  # (x+1)(x+3) = x^2 + 4x + 3
        result = polynomial_gcd(p, q)
        # Should be x+1 (monic)
        assert len(result) == 2

    def test_gcd_empty_polynomial(self):
        """Test GCD with empty polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_gcd
        )
        p = [1.0, 2.0]
        q = []
        result = polynomial_gcd(p, q)
        assert len(result) > 0


class TestPolynomialDivmod:
    """Tests for polynomial_divmod function."""

    def test_divmod_exact_division(self):
        """Test exact polynomial division."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_divmod
        )
        # (x^2 + 3x + 2) / (x + 1) = x + 2
        dividend = [2.0, 3.0, 1.0]
        divisor = [1.0, 1.0]
        quotient, remainder = polynomial_divmod(dividend, divisor)
        assert len(quotient) > 0
        # Remainder should be near zero
        assert all(abs(r) < 1e-9 for r in remainder)

    def test_divmod_with_remainder(self):
        """Test division with non-zero remainder."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_divmod
        )
        # (x^2 + 1) / (x + 1) = x - 1 + 2/(x+1)
        dividend = [1.0, 0.0, 1.0]  # x^2 + 1
        divisor = [1.0, 1.0]  # x + 1
        quotient, remainder = polynomial_divmod(dividend, divisor)
        assert len(quotient) == 2  # x - 1

    def test_divmod_divisor_higher_degree(self):
        """Test when divisor has higher degree than dividend."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_divmod
        )
        dividend = [1.0, 1.0]  # x + 1
        divisor = [1.0, 0.0, 1.0]  # x^2 + 1
        quotient, remainder = polynomial_divmod(dividend, divisor)
        assert quotient == [0.0]
        assert remainder == dividend

    def test_divmod_by_zero_polynomial(self):
        """Test division by zero polynomial raises error."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_divmod
        )
        dividend = [1.0, 2.0]
        divisor = [0.0, 0.0]
        with pytest.raises(ValueError, match="Division by zero"):
            polynomial_divmod(dividend, divisor)


class TestExtendedEuclidean:
    """Tests for extended_euclidean function."""

    def test_extended_euclidean_basic(self):
        """Test basic extended Euclidean algorithm."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            extended_euclidean
        )
        p = [1.0, 1.0]  # x + 1
        q = [2.0, 1.0]  # x + 2
        gcd, s, t = extended_euclidean(p, q)
        assert len(gcd) > 0
        assert len(s) > 0
        assert len(t) > 0

    def test_extended_euclidean_zero_q(self):
        """Test extended Euclidean with zero q."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            extended_euclidean
        )
        p = [1.0, 2.0, 1.0]
        q = [0.0]
        gcd, s, t = extended_euclidean(p, q)
        assert s == [1.0]
        assert t == [0.0]


class TestResultant:
    """Tests for resultant function."""

    def test_resultant_coprime(self):
        """Test resultant of coprime polynomials."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            resultant
        )
        # x + 1 and x + 2 have no common roots
        p = [1.0, 1.0]
        q = [2.0, 1.0]
        res = resultant(p, q)
        assert res != 0  # Non-zero for coprime

    def test_resultant_common_root(self):
        """Test resultant of polynomials with common root."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            resultant
        )
        # (x - 1) and (x^2 - 1) = (x-1)(x+1) share root x=1
        p = [-1.0, 1.0]  # x - 1
        q = [-1.0, 0.0, 1.0]  # x^2 - 1
        res = resultant(p, q)
        assert abs(res) < 1e-10  # Zero for common root

    def test_resultant_empty_polynomial(self):
        """Test resultant with empty polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            resultant
        )
        p = []
        q = [1.0, 1.0]
        res = resultant(p, q)
        assert res == 0.0

    def test_resultant_constants(self):
        """Test resultant of constant polynomials."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            resultant
        )
        p = [3.0]
        q = [5.0]
        res = resultant(p, q)
        assert res == 1.0  # Size 0 matrix -> det = 1


class TestSubresultantPRS:
    """Tests for subresultant_prs function."""

    def test_subresultant_basic(self):
        """Test basic subresultant PRS."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            subresultant_prs
        )
        p = [2.0, 3.0, 1.0]  # x^2 + 3x + 2
        q = [1.0, 1.0]  # x + 1
        sequence = subresultant_prs(p, q)
        assert len(sequence) >= 2
        assert sequence[0] == p
        assert sequence[1] == q

    def test_subresultant_zero_q(self):
        """Test subresultant PRS with zero q."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            subresultant_prs
        )
        p = [1.0, 2.0, 1.0]
        q = [0.0]
        sequence = subresultant_prs(p, q)
        assert len(sequence) == 2


class TestContentAndPrimitive:
    """Tests for content and primitive_part functions."""

    def test_content_integer_coeffs(self):
        """Test content with integer coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            content
        )
        # 6 + 9x + 3x^2 = 3(2 + 3x + x^2)
        poly = [6.0, 9.0, 3.0]
        cont = content(poly)
        assert abs(cont - 3.0) < 1e-9

    def test_content_empty_polynomial(self):
        """Test content of empty polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            content
        )
        cont = content([])
        assert cont == 1.0

    def test_primitive_part(self):
        """Test primitive part computation."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            primitive_part
        )
        # 6 + 9x + 3x^2 / content = 2 + 3x + x^2
        poly = [6.0, 9.0, 3.0]
        prim = primitive_part(poly)
        assert abs(prim[0] - 2.0) < 1e-9
        assert abs(prim[1] - 3.0) < 1e-9
        assert abs(prim[2] - 1.0) < 1e-9


class TestPolynomialArithmetic:
    """Tests for polynomial arithmetic functions."""

    def test_polynomial_multiply(self):
        """Test polynomial multiplication."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_multiply
        )
        # (x + 1) * (x + 2) = x^2 + 3x + 2
        p = [1.0, 1.0]
        q = [2.0, 1.0]
        result = polynomial_multiply(p, q)
        assert len(result) == 3
        assert abs(result[0] - 2.0) < 1e-9
        assert abs(result[1] - 3.0) < 1e-9
        assert abs(result[2] - 1.0) < 1e-9

    def test_polynomial_multiply_empty(self):
        """Test multiplication with empty polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_multiply
        )
        result = polynomial_multiply([], [1.0, 2.0])
        assert result == [0.0]

    def test_polynomial_subtract(self):
        """Test polynomial subtraction."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            polynomial_subtract
        )
        p = [3.0, 2.0, 1.0]
        q = [1.0, 1.0]
        result = polynomial_subtract(p, q)
        assert len(result) == 3
        assert abs(result[0] - 2.0) < 1e-9
        assert abs(result[1] - 1.0) < 1e-9


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_normalize_poly(self):
        """Test polynomial normalization."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            _normalize_poly
        )
        poly = [1.0, 2.0, 0.0, 0.0]
        result = _normalize_poly(poly)
        assert len(result) == 2
        assert result == [1.0, 2.0]

    def test_normalize_empty(self):
        """Test normalization of empty polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            _normalize_poly
        )
        result = _normalize_poly([])
        assert result == [0.0]

    def test_make_monic(self):
        """Test making polynomial monic."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            _make_monic
        )
        poly = [2.0, 4.0]  # 2 + 4x -> 0.5 + x
        result = _make_monic(poly)
        assert abs(result[-1] - 1.0) < 1e-9

    def test_determinant_2x2(self):
        """Test 2x2 determinant."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            _determinant
        )
        matrix = [[1.0, 2.0], [3.0, 4.0]]
        det = _determinant(matrix)
        assert abs(det - (-2.0)) < 1e-9

    def test_determinant_3x3(self):
        """Test 3x3 determinant."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            _determinant
        )
        matrix = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 10.0]]
        det = _determinant(matrix)
        # det = 1*(5*10-6*8) - 2*(4*10-6*7) + 3*(4*8-5*7)
        # = 1*(50-48) - 2*(40-42) + 3*(32-35)
        # = 2 + 4 - 9 = -3
        assert abs(det - (-3.0)) < 1e-9

    def test_determinant_empty(self):
        """Test empty matrix determinant."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            _determinant
        )
        det = _determinant([])
        assert det == 1.0

    def test_determinant_1x1(self):
        """Test 1x1 matrix determinant."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_gcd import (
            _determinant
        )
        det = _determinant([[5.0]])
        assert det == 5.0


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial import (
            polynomial_gcd,
            polynomial_divmod,
            extended_euclidean,
            resultant,
            subresultant_prs,
            content,
            primitive_part,
        )
        assert callable(polynomial_gcd)
        assert callable(polynomial_divmod)
        assert callable(extended_euclidean)
        assert callable(resultant)
        assert callable(subresultant_prs)
        assert callable(content)
        assert callable(primitive_part)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
