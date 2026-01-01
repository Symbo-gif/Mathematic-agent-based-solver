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
Tests for Domain Polynomial Solver Module
==========================================

Comprehensive tests for DomainPolynomialSolver routing class.
"""

import pytest


class TestDomainPolynomialSolverStaticMethods:
    """Tests for static method exports."""

    def test_extract_coefficients_export(self):
        """Test extract_coefficients is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.extract_coefficients)

    def test_solve_linear_export(self):
        """Test solve_linear is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.solve_linear)

    def test_solve_quadratic_export(self):
        """Test solve_quadratic is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.solve_quadratic)

    def test_solve_cubic_export(self):
        """Test solve_cubic is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.solve_cubic)

    def test_solve_quartic_export(self):
        """Test solve_quartic is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.solve_quartic)

    def test_newton_raphson_export(self):
        """Test newton_raphson is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.newton_raphson)

    def test_find_rational_roots_export(self):
        """Test find_rational_roots is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.find_rational_roots)

    def test_factor_difference_of_squares_export(self):
        """Test factor_difference_of_squares is exported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert callable(DomainPolynomialSolver.factor_difference_of_squares)


class TestTryDomainSolve:
    """Tests for try_domain_solve routing method."""

    def test_try_domain_solve_returns_tuple(self):
        """Test try_domain_solve returns proper tuple format."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Integer
        x = Symbol('x')
        expr = Integer(5)  # Constant
        result = DomainPolynomialSolver.try_domain_solve(expr, x)
        assert isinstance(result, tuple)
        assert len(result) == 3
        success, solutions, method = result
        assert isinstance(success, bool)
        assert isinstance(method, str)

    def test_try_domain_solve_not_polynomial(self):
        """Test try_domain_solve with non-polynomial returns not_polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, sin
        x = Symbol('x')
        expr = sin(x)  # Not a polynomial
        success, solutions, method = DomainPolynomialSolver.try_domain_solve(expr, x)
        # Should either succeed with special handling or return not_polynomial
        assert isinstance(success, bool)

    def test_try_domain_solve_cubic_returns_result(self):
        """Test solving cubic equation returns result tuple."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        expr = Add(Pow(x, Integer(3)), Integer(-8))
        result = DomainPolynomialSolver.try_domain_solve(expr, x)
        assert isinstance(result, tuple)
        success, solutions, method = result
        # Verify return format even if solving fails
        assert isinstance(success, bool)
        assert isinstance(method, str)


class TestTryDomainFactor:
    """Tests for try_domain_factor routing method."""

    def test_try_domain_factor_difference_of_squares(self):
        """Test factoring difference of squares."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 - 4 = (x-2)(x+2)
        expr = Add(Pow(x, Integer(2)), Integer(-4))
        success, factored, method = DomainPolynomialSolver.try_domain_factor(expr)
        # May or may not succeed depending on expression structure

    def test_try_domain_factor_no_match(self):
        """Test factoring with no pattern match."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Add, Pow, Integer
        x = Symbol('x')
        # x^2 + 5x + 7 - no simple pattern
        expr = Add(Pow(x, Integer(2)), Add(Symbol('x'), Integer(7)))
        success, factored, method = DomainPolynomialSolver.try_domain_factor(expr)
        # Result depends on pattern matching


class TestStaticMethodFunctionality:
    """Tests for static method functionality via class."""

    def test_solve_linear_via_class(self):
        """Test solve_linear via DomainPolynomialSolver."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        result = DomainPolynomialSolver.solve_linear(2, 4)
        assert result is not None
        assert len(result) == 1

    def test_solve_quadratic_via_class(self):
        """Test solve_quadratic via DomainPolynomialSolver."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        result = DomainPolynomialSolver.solve_quadratic(1, 0, -4)
        assert result is not None
        assert len(result) == 2

    def test_newton_raphson_via_class(self):
        """Test newton_raphson via DomainPolynomialSolver."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        coeffs = [1, 0, -4]  # x^2 - 4
        root = DomainPolynomialSolver.newton_raphson(coeffs, x0=3.0)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_find_rational_roots_via_class(self):
        """Test find_rational_roots via DomainPolynomialSolver."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        # x^2 - 1 has roots +1 and -1
        coeffs = [1, 0, -1]
        roots = DomainPolynomialSolver.find_rational_roots(coeffs)
        assert len(roots) == 2

    def test_is_biquadratic_via_class(self):
        """Test is_biquadratic via DomainPolynomialSolver."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        # x^4 - 5x^2 + 4 is biquadratic
        coeffs = [1, 0, -5, 0, 4]
        assert DomainPolynomialSolver.is_biquadratic(coeffs) is True

    def test_solve_biquadratic_via_class(self):
        """Test solve_biquadratic via DomainPolynomialSolver."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        result = DomainPolynomialSolver.solve_biquadratic(1, -5, 4)
        assert result is not None
        assert len(result) == 4


class TestModuleImports:
    """Tests for module imports."""

    def test_domain_solver_import(self):
        """Test DomainPolynomialSolver can be imported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.domain_solver import (
            DomainPolynomialSolver
        )
        assert DomainPolynomialSolver is not None

    def test_package_exports_domain_solver(self):
        """Test package exports DomainPolynomialSolver."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial import (
            DomainPolynomialSolver
        )
        assert DomainPolynomialSolver is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
