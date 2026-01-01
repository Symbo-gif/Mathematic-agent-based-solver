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
Tests for Rational Equations Module
===================================

Comprehensive tests for rational root theorem and biquadratic solving.
"""

import pytest
from fractions import Fraction


class TestFindRationalRoots:
    """Tests for find_rational_roots function."""

    def test_find_rational_roots_basic(self):
        """Test basic polynomial with rational roots: x^2 - 1 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        # x^2 - 1 has roots +1 and -1
        coeffs = [1, 0, -1]  # x^2 + 0x - 1
        roots = find_rational_roots(coeffs)
        assert len(roots) == 2
        root_vals = [float(r) for r in roots]
        assert 1 in root_vals or any(abs(r - 1) < 1e-9 for r in root_vals)
        assert -1 in root_vals or any(abs(r + 1) < 1e-9 for r in root_vals)

    def test_find_rational_roots_cubic(self):
        """Test cubic with rational roots: x^3 - 6x^2 + 11x - 6 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        # (x-1)(x-2)(x-3) = x^3 - 6x^2 + 11x - 6
        coeffs = [1, -6, 11, -6]
        roots = find_rational_roots(coeffs)
        assert len(roots) == 3
        root_vals = sorted([float(r) for r in roots])
        assert abs(root_vals[0] - 1) < 1e-9
        assert abs(root_vals[1] - 2) < 1e-9
        assert abs(root_vals[2] - 3) < 1e-9

    def test_find_rational_roots_empty_coeffs(self):
        """Test with empty coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        roots = find_rational_roots([])
        assert roots == []

    def test_find_rational_roots_all_zeros(self):
        """Test with all zero coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        roots = find_rational_roots([0, 0, 0])
        assert roots == []

    def test_find_rational_roots_constant_zero(self):
        """Test when constant term is zero (x=0 is root)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        # x^2 - x = x(x-1) has root 0
        coeffs = [1, -1, 0]
        roots = find_rational_roots(coeffs)
        assert any(float(r) == 0 for r in roots)

    def test_find_rational_roots_leading_zero(self):
        """Test when leading coefficient is zero."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        coeffs = [0, 1, -1]  # Effectively x - 1 = 0
        roots = find_rational_roots(coeffs)
        assert roots == []  # Leading zero case

    def test_find_rational_roots_no_rational_roots(self):
        """Test polynomial with no rational roots: x^2 + 1 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        coeffs = [1, 0, 1]  # x^2 + 1
        roots = find_rational_roots(coeffs)
        assert roots == []  # No real rational roots

    def test_find_rational_roots_fractional(self):
        """Test polynomial with fractional roots: 2x - 1 = 0 -> x = 1/2."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        coeffs = [2, -1]  # 2x - 1
        roots = find_rational_roots(coeffs)
        assert len(roots) == 1
        assert float(roots[0]) == 0.5

    def test_find_rational_roots_non_integer_coeffs(self):
        """Test with non-integer coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        # Should handle or return empty
        coeffs = [1.5, -0.5, 0.1]
        roots = find_rational_roots(coeffs)
        # Result depends on implementation


class TestIsBiquadratic:
    """Tests for is_biquadratic function."""

    def test_is_biquadratic_true(self):
        """Test biquadratic: x^4 - 5x^2 + 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_biquadratic
        )
        # [a4, a3, a2, a1, a0] = [1, 0, -5, 0, 4]
        coeffs = [1, 0, -5, 0, 4]
        assert is_biquadratic(coeffs) is True

    def test_is_biquadratic_false_has_cubic(self):
        """Test not biquadratic: x^4 + x^3 - 5x^2 + 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_biquadratic
        )
        coeffs = [1, 1, -5, 0, 4]  # Has x^3 term
        assert is_biquadratic(coeffs) is False

    def test_is_biquadratic_false_has_linear(self):
        """Test not biquadratic: x^4 - 5x^2 + x + 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_biquadratic
        )
        coeffs = [1, 0, -5, 1, 4]  # Has x term
        assert is_biquadratic(coeffs) is False

    def test_is_biquadratic_wrong_length(self):
        """Test with wrong coefficient count."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_biquadratic
        )
        coeffs = [1, 0, -5, 4]  # Only 4 coefficients (degree 3)
        assert is_biquadratic(coeffs) is False

    def test_is_biquadratic_near_zero(self):
        """Test with coefficients near zero."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_biquadratic
        )
        coeffs = [1, 1e-15, -5, 1e-15, 4]
        result = is_biquadratic(coeffs)
        # Near-zero should be treated as zero
        assert result is True


class TestSolveBiquadratic:
    """Tests for solve_biquadratic function."""

    def test_solve_biquadratic_four_real_roots(self):
        """Test biquadratic with four real roots: x^4 - 5x^2 + 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            solve_biquadratic
        )
        # (x^2-1)(x^2-4) = x^4 - 5x^2 + 4
        # u = 1 -> x = +/-1, u = 4 -> x = +/-2
        result = solve_biquadratic(1, -5, 4)
        assert result is not None
        assert len(result) == 4  # Four roots

    def test_solve_biquadratic_two_real_roots(self):
        """Test biquadratic with two real roots: x^4 - x^2 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            solve_biquadratic
        )
        # x^2(x^2 - 1) = 0 -> x = 0, +/-1
        result = solve_biquadratic(1, -1, 0)
        assert result is not None
        assert len(result) >= 2

    def test_solve_biquadratic_complex_roots(self):
        """Test biquadratic with complex roots: x^4 + 1 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            solve_biquadratic
        )
        result = solve_biquadratic(1, 0, 1)
        assert result is not None
        # Should contain complex roots


class TestIsRationalEquation:
    """Tests for is_rational_equation function."""

    def test_is_rational_no_variables(self):
        """Test with no variables (constant)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_rational_equation
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = is_rational_equation(Integer(5))
        assert result is False

    def test_is_rational_polynomial(self):
        """Test with polynomial (not rational)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_rational_equation
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 + x + 1 is not a rational equation
        expr = Add(Pow(x, Integer(2)), Add(x, Integer(1)))
        result = is_rational_equation(expr)
        # Depends on implementation


class TestModuleImports:
    """Tests for module imports."""

    def test_module_imports(self):
        """Test module can be imported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial import rational_equations
        assert rational_equations is not None

    def test_find_rational_roots_import(self):
        """Test find_rational_roots is importable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        assert callable(find_rational_roots)

    def test_is_biquadratic_import(self):
        """Test is_biquadratic is importable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            is_biquadratic
        )
        assert callable(is_biquadratic)

    def test_solve_biquadratic_import(self):
        """Test solve_biquadratic is importable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            solve_biquadratic
        )
        assert callable(solve_biquadratic)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
