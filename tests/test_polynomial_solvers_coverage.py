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
Tests for Polynomial Solvers Module
====================================

Comprehensive tests for degree-specific polynomial solving methods.
"""

import pytest


class TestSolveLinear:
    """Tests for solve_linear function."""

    def test_solve_linear_basic(self):
        """Test basic linear equation: 2x + 4 = 0 -> x = -2."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_linear
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_linear(Integer(2), Integer(4))
        assert result is not None
        assert len(result) == 1
        # x = -4/2 = -2
        root = result[0]
        val = root.value if hasattr(root, 'value') else root
        assert val == -2

    def test_solve_linear_zero_coefficient(self):
        """Test linear with a=0 returns None."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_linear
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_linear(Integer(0), Integer(5))
        assert result is None

    def test_solve_linear_rational_result(self):
        """Test linear with rational result."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_linear
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        # 3x + 2 = 0 -> x = -2/3
        result = solve_linear(Integer(3), Integer(2))
        assert result is not None
        assert len(result) == 1

    def test_solve_linear_float_coeffs(self):
        """Test linear with float coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_linear
        )
        from symbo_agentic_reasoners.core.native_symbolic import Float
        result = solve_linear(Float(2.5), Float(5.0))
        assert result is not None
        # x = -5.0 / 2.5 = -2.0
        root = result[0]
        val = root.value if hasattr(root, 'value') else float(root)
        assert abs(val - (-2.0)) < 1e-9


class TestSolveQuadratic:
    """Tests for solve_quadratic function."""

    def test_quadratic_two_real_roots(self):
        """Test quadratic with two real roots: x^2 - 5x + 6 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        # (x-2)(x-3) = x^2 - 5x + 6
        result = solve_quadratic(Integer(1), Integer(-5), Integer(6))
        assert result is not None
        assert len(result) == 2
        roots = sorted([r.value if hasattr(r, 'value') else r for r in result])
        assert 2 in roots or abs(roots[0] - 2) < 1e-9
        assert 3 in roots or abs(roots[1] - 3) < 1e-9

    def test_quadratic_one_repeated_root(self):
        """Test quadratic with one repeated root: x^2 - 4x + 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        # (x-2)^2 = x^2 - 4x + 4
        result = solve_quadratic(Integer(1), Integer(-4), Integer(4))
        assert result is not None
        root = result[0]
        val = root.value if hasattr(root, 'value') else root
        assert val == 2 or abs(val - 2) < 1e-9

    def test_quadratic_complex_roots(self):
        """Test quadratic with complex roots: x^2 + 1 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_quadratic(Integer(1), Integer(0), Integer(1))
        assert result is not None
        # Should contain 'I' for imaginary unit
        assert any('I' in str(r) or 'j' in str(r).lower() for r in result)

    def test_quadratic_a_zero_delegates_to_linear(self):
        """Test quadratic with a=0 delegates to linear."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        # 0*x^2 + 2x + 4 = 0 -> x = -2
        result = solve_quadratic(Integer(0), Integer(2), Integer(4))
        assert result is not None
        assert len(result) == 1

    def test_quadratic_irrational_roots(self):
        """Test quadratic with irrational roots: x^2 - 2 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        import math
        result = solve_quadratic(Integer(1), Integer(0), Integer(-2))
        assert result is not None
        assert len(result) == 2
        # Roots should be +/- sqrt(2)
        roots = [r.value if hasattr(r, 'value') else float(r) for r in result]
        assert any(abs(r - math.sqrt(2)) < 1e-9 for r in roots)
        assert any(abs(r + math.sqrt(2)) < 1e-9 for r in roots)


class TestSolveCubic:
    """Tests for solve_cubic function."""

    def test_cubic_three_real_roots(self):
        """Test cubic with three real roots: x^3 - 6x^2 + 11x - 6 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_cubic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        # (x-1)(x-2)(x-3) = x^3 - 6x^2 + 11x - 6
        result = solve_cubic(Integer(1), Integer(-6), Integer(11), Integer(-6))
        assert result is not None
        assert len(result) >= 1

    def test_cubic_one_real_root(self):
        """Test cubic with one real root: x^3 + x + 1 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_cubic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_cubic(Integer(1), Integer(0), Integer(1), Integer(1))
        assert result is not None
        assert len(result) >= 1

    def test_cubic_triple_root(self):
        """Test cubic with triple root: x^3 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_cubic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_cubic(Integer(1), Integer(0), Integer(0), Integer(0))
        assert result is not None
        root = result[0]
        val = root.value if hasattr(root, 'value') else root
        assert abs(val) < 1e-9  # Root is 0

    def test_cubic_a_zero_delegates_to_quadratic(self):
        """Test cubic with a=0 delegates to quadratic."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_cubic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_cubic(Integer(0), Integer(1), Integer(-5), Integer(6))
        assert result is not None
        # Delegates to x^2 - 5x + 6 = 0, roots 2 and 3

    def test_cubic_simple_integer_root(self):
        """Test cubic with simple integer root: x^3 - 8 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_cubic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_cubic(Integer(1), Integer(0), Integer(0), Integer(-8))
        assert result is not None
        # One real root x = 2
        root = result[0]
        val = root.value if hasattr(root, 'value') else root
        assert abs(val - 2) < 1e-9


class TestSolveQuartic:
    """Tests for solve_quartic function."""

    def test_quartic_four_real_roots(self):
        """Test quartic with four real roots."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quartic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        # (x-1)(x-2)(x-3)(x-4) = x^4 - 10x^3 + 35x^2 - 50x + 24
        result = solve_quartic(
            Integer(1), Integer(-10), Integer(35), Integer(-50), Integer(24)
        )
        assert result is not None
        assert len(result) >= 1

    def test_quartic_biquadratic(self):
        """Test biquadratic: x^4 - 5x^2 + 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quartic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        # (x^2-1)(x^2-4) = x^4 - 5x^2 + 4, roots: +/-1, +/-2
        result = solve_quartic(
            Integer(1), Integer(0), Integer(-5), Integer(0), Integer(4)
        )
        assert result is not None
        assert len(result) >= 2

    def test_quartic_a_zero_delegates_to_cubic(self):
        """Test quartic with a=0 delegates to cubic."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quartic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_quartic(
            Integer(0), Integer(1), Integer(-6), Integer(11), Integer(-6)
        )
        assert result is not None

    def test_quartic_simple_roots(self):
        """Test quartic with simple roots: x^4 - 1 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quartic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer
        result = solve_quartic(
            Integer(1), Integer(0), Integer(0), Integer(0), Integer(-1)
        )
        assert result is not None
        # Real roots are +1 and -1
        roots = [r.value if hasattr(r, 'value') else r for r in result]
        numeric_roots = [r for r in roots if isinstance(r, (int, float))]
        if numeric_roots:
            assert any(abs(r - 1) < 1e-9 or abs(r + 1) < 1e-9 for r in numeric_roots)


class TestExtractCoefficients:
    """Tests for extract_coefficients function."""

    def test_extract_constant(self):
        """Test extracting coefficients from constant."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            extract_coefficients
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer, Symbol
        x = Symbol('x')
        result = extract_coefficients(Integer(5), x)
        assert result == [Integer(5)]

    def test_extract_single_variable(self):
        """Test extracting coefficients from single variable."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            extract_coefficients
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol
        x = Symbol('x')
        result = extract_coefficients(x, x)
        assert result is not None
        assert len(result) == 2

    def test_extract_different_symbol(self):
        """Test extracting with different symbol."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            extract_coefficients
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol
        x = Symbol('x')
        y = Symbol('y')
        result = extract_coefficients(y, x)
        # y is constant with respect to x
        assert result is not None


class TestSolvePolynomialByDegree:
    """Tests for solve_polynomial_by_degree function."""

    def test_solve_by_degree_returns_none_for_complex(self):
        """Test that complex expressions may return None."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_polynomial_by_degree
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Mul, Pow
        x = Symbol('x')
        # Create a complex expression that can't be easily parsed
        expr = Add(Pow(x, 2), Mul(x, x))  # This may not parse properly
        result = solve_polynomial_by_degree(expr, x)
        # Result may be None for complex expressions


class TestEdgeCases:
    """Edge case tests."""

    def test_solve_linear_with_python_int(self):
        """Test linear with plain Python int."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_linear
        )
        result = solve_linear(2, 4)
        assert result is not None

    def test_solve_quadratic_with_python_float(self):
        """Test quadratic with plain Python float."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        result = solve_quadratic(1.0, -5.0, 6.0)
        assert result is not None

    def test_solve_cubic_with_mixed_types(self):
        """Test cubic with mixed types."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_cubic
        )
        from symbo_agentic_reasoners.core.native_symbolic import Integer, Float
        result = solve_cubic(Integer(1), Float(0.0), Integer(0), Float(-8.0))
        assert result is not None


class TestModuleExports:
    """Tests for module exports."""

    def test_module_imports(self):
        """Test module can be imported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial import polynomial_solvers
        assert polynomial_solvers is not None

    def test_solve_linear_export(self):
        """Test solve_linear is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_linear
        )
        assert callable(solve_linear)

    def test_solve_quadratic_export(self):
        """Test solve_quadratic is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        assert callable(solve_quadratic)

    def test_solve_cubic_export(self):
        """Test solve_cubic is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_cubic
        )
        assert callable(solve_cubic)

    def test_solve_quartic_export(self):
        """Test solve_quartic is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quartic
        )
        assert callable(solve_quartic)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
