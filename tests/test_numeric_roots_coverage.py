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
Tests for Numeric Root Finding Module
=====================================

Comprehensive tests for Newton-Raphson, bisection, secant, and Brent's methods.
"""

import pytest
import math


class TestNewtonRaphson:
    """Tests for newton_raphson function."""

    def test_newton_raphson_quadratic(self):
        """Test Newton-Raphson on x^2 - 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        # x^2 - 4 has roots at +2 and -2
        coeffs = [1, 0, -4]
        root = newton_raphson(coeffs, x0=3.0)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_newton_raphson_cubic(self):
        """Test Newton-Raphson on x^3 - 8 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        coeffs = [1, 0, 0, -8]  # x^3 - 8
        root = newton_raphson(coeffs, x0=3.0)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_newton_raphson_linear(self):
        """Test Newton-Raphson on 2x - 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        coeffs = [2, -4]  # 2x - 4
        root = newton_raphson(coeffs, x0=0.0)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_newton_raphson_empty_coeffs(self):
        """Test Newton-Raphson with empty coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        result = newton_raphson([])
        assert result is None

    def test_newton_raphson_constant(self):
        """Test Newton-Raphson with constant polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        coeffs = [5]  # Constant 5, no roots
        result = newton_raphson(coeffs)
        assert result is None

    def test_newton_raphson_negative_start(self):
        """Test Newton-Raphson starting from negative x."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        coeffs = [1, 0, -4]
        root = newton_raphson(coeffs, x0=-3.0)
        assert root is not None
        assert abs(root + 2.0) < 1e-6  # Should find -2

    def test_newton_raphson_tolerance(self):
        """Test Newton-Raphson with different tolerance."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        coeffs = [1, 0, -2]  # x^2 - 2, root is sqrt(2)
        root = newton_raphson(coeffs, x0=2.0, tolerance=1e-15)
        assert root is not None
        assert abs(root - math.sqrt(2)) < 1e-10


class TestFindAllNumericRoots:
    """Tests for find_all_numeric_roots function."""

    def test_find_all_roots_quadratic(self):
        """Test finding all roots of x^2 - 4 = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            find_all_numeric_roots
        )
        coeffs = [1, 0, -4]
        roots = find_all_numeric_roots(coeffs)
        assert len(roots) == 2
        root_vals = sorted(roots)
        assert abs(root_vals[0] + 2.0) < 1e-6
        assert abs(root_vals[1] - 2.0) < 1e-6

    def test_find_all_roots_cubic(self):
        """Test finding all roots of (x-1)(x-2)(x-3) = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            find_all_numeric_roots
        )
        # x^3 - 6x^2 + 11x - 6
        coeffs = [1, -6, 11, -6]
        roots = find_all_numeric_roots(coeffs)
        assert len(roots) >= 1
        # At least one root should be near 1, 2, or 3

    def test_find_all_roots_empty(self):
        """Test with empty coefficients."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            find_all_numeric_roots
        )
        roots = find_all_numeric_roots([])
        assert roots == []

    def test_find_all_roots_single_coeff(self):
        """Test with single coefficient."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            find_all_numeric_roots
        )
        roots = find_all_numeric_roots([5])
        assert roots == []


class TestBisectionMethod:
    """Tests for bisection_method function."""

    def test_bisection_simple(self):
        """Test bisection on f(x) = x - 2."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            bisection_method
        )
        def f(x):
            return x - 2
        root = bisection_method(f, 0, 5)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_bisection_quadratic(self):
        """Test bisection on f(x) = x^2 - 4."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            bisection_method
        )
        def f(x):
            return x**2 - 4
        root = bisection_method(f, 0, 5)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_bisection_no_sign_change(self):
        """Test bisection when no sign change in interval."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            bisection_method
        )
        def f(x):
            return x**2 + 1  # Always positive
        root = bisection_method(f, 0, 5)
        assert root is None

    def test_bisection_root_at_endpoint(self):
        """Test bisection when root is at endpoint."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            bisection_method
        )
        def f(x):
            return x - 2
        root = bisection_method(f, 2, 5)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_bisection_exception_handling(self):
        """Test bisection with function that raises exception."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            bisection_method
        )
        def f(x):
            if x < 1:
                raise ValueError("Bad value")
            return x - 2
        root = bisection_method(f, 0, 5)
        assert root is None


class TestSecantMethod:
    """Tests for secant_method function."""

    def test_secant_simple(self):
        """Test secant method on f(x) = x - 2."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            secant_method
        )
        def f(x):
            return x - 2
        root = secant_method(f, 0, 5)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_secant_quadratic(self):
        """Test secant method on f(x) = x^2 - 4."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            secant_method
        )
        def f(x):
            return x**2 - 4
        root = secant_method(f, 1, 3)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_secant_same_values(self):
        """Test secant when f(x0) = f(x1)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            secant_method
        )
        def f(x):
            return (x - 2)**2  # Same value at symmetric points
        # Points where f(x0) = f(x1) will cause division issues
        root = secant_method(f, 0, 4)  # f(0) = f(4) = 4
        # May return None due to division by zero protection

    def test_secant_exception(self):
        """Test secant with function that raises exception."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            secant_method
        )
        def f(x):
            if x > 3:
                raise ValueError("Bad")
            return x - 2
        root = secant_method(f, 0, 5)
        assert root is None


class TestBrentMethod:
    """Tests for brent_method function."""

    def test_brent_simple(self):
        """Test Brent's method on f(x) = x - 2."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            brent_method
        )
        def f(x):
            return x - 2
        root = brent_method(f, 0, 5)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_brent_quadratic(self):
        """Test Brent's method on f(x) = x^2 - 4."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            brent_method
        )
        def f(x):
            return x**2 - 4
        root = brent_method(f, 0, 5)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_brent_no_sign_change(self):
        """Test Brent when no sign change."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            brent_method
        )
        def f(x):
            return x**2 + 1
        root = brent_method(f, 0, 5)
        assert root is None

    def test_brent_trig(self):
        """Test Brent's method on sin(x)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            brent_method
        )
        def f(x):
            return math.sin(x)
        root = brent_method(f, 2, 4)  # Root at pi
        assert root is not None
        assert abs(root - math.pi) < 1e-6

    def test_brent_swap_endpoints(self):
        """Test Brent's method with |f(a)| < |f(b)|."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            brent_method
        )
        def f(x):
            return x - 2
        root = brent_method(f, 1, 10)  # |f(1)| = 1 < |f(10)| = 8
        assert root is not None
        assert abs(root - 2.0) < 1e-6


class TestFindRoot:
    """Tests for find_root function."""

    def test_find_root_with_interval(self):
        """Test find_root with interval provided."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            find_root
        )
        def f(x):
            return x - 2
        root = find_root(f, interval=(0, 5))
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_find_root_without_interval(self):
        """Test find_root without interval (uses secant)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            find_root
        )
        def f(x):
            return x - 2
        root = find_root(f, initial_guess=1.0)
        assert root is not None
        assert abs(root - 2.0) < 1e-6

    def test_find_root_fallback_search(self):
        """Test find_root fallback to bisection search."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            find_root
        )
        def f(x):
            return x - 5
        root = find_root(f, initial_guess=0.0)
        assert root is not None
        assert abs(root - 5.0) < 1e-6


class TestPolyCoeffsToFunc:
    """Tests for poly_coeffs_to_func function."""

    def test_poly_func_linear(self):
        """Test converting linear polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            poly_coeffs_to_func
        )
        coeffs = [2, -4]  # 2x - 4
        f = poly_coeffs_to_func(coeffs)
        assert f(0) == -4
        assert f(2) == 0
        assert f(3) == 2

    def test_poly_func_quadratic(self):
        """Test converting quadratic polynomial."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            poly_coeffs_to_func
        )
        coeffs = [1, 0, -4]  # x^2 - 4
        f = poly_coeffs_to_func(coeffs)
        assert f(0) == -4
        assert f(2) == 0
        assert f(-2) == 0
        assert f(3) == 5


class TestModuleExports:
    """Tests for module exports."""

    def test_module_imports(self):
        """Test module can be imported."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial import numeric_roots
        assert numeric_roots is not None

    def test_all_functions_exported(self):
        """Test all functions are exported from package."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial import (
            newton_raphson,
            find_all_numeric_roots,
            bisection_method,
            secant_method,
            brent_method,
            find_root,
            poly_coeffs_to_func,
        )
        assert callable(newton_raphson)
        assert callable(find_all_numeric_roots)
        assert callable(bisection_method)
        assert callable(secant_method)
        assert callable(brent_method)
        assert callable(find_root)
        assert callable(poly_coeffs_to_func)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
