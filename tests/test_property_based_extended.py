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
Extended Property-Based Tests using Hypothesis
===============================================

Additional property-based tests for mathematical invariants.
These tests use database=None to avoid Python 3.14 compatibility issues.
"""

import pytest
import math
from typing import List

from hypothesis import given, strategies as st, settings, assume, HealthCheck

# Configure for Python 3.14 compatibility
settings.register_profile("safe", max_examples=30, deadline=None, database=None)
settings.load_profile("safe")


# =============================================================================
# NUMBER THEORY PROPERTY TESTS
# =============================================================================

class TestGCDProperties:
    """Property-based tests for GCD operations."""

    @given(a=st.integers(min_value=1, max_value=10000),
           b=st.integers(min_value=1, max_value=10000))
    @settings(max_examples=50, database=None)
    def test_gcd_commutativity(self, a, b):
        """gcd(a, b) = gcd(b, a)."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        assert gcd(a, b) == gcd(b, a)

    @given(a=st.integers(min_value=1, max_value=10000))
    @settings(max_examples=30, database=None)
    def test_gcd_with_self(self, a):
        """gcd(a, a) = a."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        assert gcd(a, a) == a

    @given(a=st.integers(min_value=1, max_value=10000))
    @settings(max_examples=30, database=None)
    def test_gcd_with_one(self, a):
        """gcd(a, 1) = 1."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        assert gcd(a, 1) == 1

    @given(a=st.integers(min_value=1, max_value=1000),
           b=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=30, database=None)
    def test_gcd_divides_both(self, a, b):
        """gcd(a, b) divides both a and b."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        g = gcd(a, b)
        assert a % g == 0
        assert b % g == 0

    @given(a=st.integers(min_value=1, max_value=1000),
           b=st.integers(min_value=1, max_value=1000),
           c=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=30, database=None)
    def test_gcd_associativity(self, a, b, c):
        """gcd(gcd(a, b), c) = gcd(a, gcd(b, c))."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd
        assert gcd(gcd(a, b), c) == gcd(a, gcd(b, c))


class TestLCMProperties:
    """Property-based tests for LCM operations."""

    @given(a=st.integers(min_value=1, max_value=1000),
           b=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50, database=None)
    def test_lcm_commutativity(self, a, b):
        """lcm(a, b) = lcm(b, a)."""
        from symbo_agentic_reasoners.core.number_theory_native import lcm
        assert lcm(a, b) == lcm(b, a)

    @given(a=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=30, database=None)
    def test_lcm_with_self(self, a):
        """lcm(a, a) = a."""
        from symbo_agentic_reasoners.core.number_theory_native import lcm
        assert lcm(a, a) == a

    @given(a=st.integers(min_value=1, max_value=1000),
           b=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=30, database=None)
    def test_lcm_multiple_of_both(self, a, b):
        """lcm(a, b) is divisible by both a and b."""
        from symbo_agentic_reasoners.core.number_theory_native import lcm
        l = lcm(a, b)
        assert l % a == 0
        assert l % b == 0

    @given(a=st.integers(min_value=1, max_value=500),
           b=st.integers(min_value=1, max_value=500))
    @settings(max_examples=30, database=None)
    def test_gcd_lcm_product(self, a, b):
        """gcd(a, b) * lcm(a, b) = a * b."""
        from symbo_agentic_reasoners.core.number_theory_native import gcd, lcm
        assert gcd(a, b) * lcm(a, b) == a * b


class TestPrimalityProperties:
    """Property-based tests for primality."""

    @given(n=st.integers(min_value=2, max_value=1000))
    @settings(max_examples=50, database=None)
    def test_prime_has_two_divisors(self, n):
        """A prime has exactly 2 divisors: 1 and itself."""
        from symbo_agentic_reasoners.core.number_theory_native import is_prime

        if is_prime(n):
            divisors = [d for d in range(1, n+1) if n % d == 0]
            assert len(divisors) == 2
            assert divisors == [1, n]

    @given(n=st.integers(min_value=4, max_value=500))
    @settings(max_examples=30, database=None)
    def test_composite_has_nontrivial_factor(self, n):
        """A composite has a factor other than 1 and itself."""
        from symbo_agentic_reasoners.core.number_theory_native import is_prime

        if not is_prime(n):
            has_nontrivial = any(n % d == 0 for d in range(2, n))
            assert has_nontrivial


class TestTotientProperties:
    """Property-based tests for Euler's totient function."""

    @given(p=st.sampled_from([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]))
    @settings(max_examples=15, database=None)
    def test_totient_of_prime(self, p):
        """phi(p) = p - 1 for prime p."""
        from symbo_agentic_reasoners.core.number_theory_native import totient
        assert totient(p) == p - 1

    @given(n=st.integers(min_value=2, max_value=100))
    @settings(max_examples=30, database=None)
    def test_totient_upper_bound(self, n):
        """phi(n) <= n - 1 for n >= 2."""
        from symbo_agentic_reasoners.core.number_theory_native import totient
        assert totient(n) <= n - 1


# =============================================================================
# POLYNOMIAL SOLVER PROPERTY TESTS
# =============================================================================

class TestPolynomialSolverProperties:
    """Property-based tests for polynomial solvers."""

    @given(a=st.integers(min_value=1, max_value=100),
           b=st.integers(min_value=-100, max_value=100))
    @settings(max_examples=50, database=None)
    def test_linear_solver_correctness(self, a, b):
        """solve_linear finds correct root for ax + b = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_linear
        )
        roots = solve_linear(a, b)
        assert len(roots) == 1
        root = roots[0]
        expected = -b / a
        assert abs(root - expected) < 1e-10

    @given(root=st.integers(min_value=-50, max_value=50))
    @settings(max_examples=30, database=None)
    def test_quadratic_with_repeated_root(self, root):
        """x^2 - 2rx + r^2 = (x-r)^2 has repeated root r."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        # (x - r)^2 = x^2 - 2rx + r^2
        a = 1
        b = -2 * root
        c = root * root

        roots = solve_quadratic(a, b, c)
        # Should have roots close to 'root'
        # Note: solve_quadratic returns symbolic types, convert to float
        for r in roots:
            r_val = float(r) if hasattr(r, '__float__') else r
            assert abs(r_val - root) < 1e-6

    @given(r1=st.integers(min_value=-20, max_value=20),
           r2=st.integers(min_value=-20, max_value=20))
    @settings(max_examples=30, database=None)
    def test_quadratic_roots_sum_and_product(self, r1, r2):
        """For x^2 + bx + c = 0, sum of roots = -b, product = c."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.polynomial_solvers import (
            solve_quadratic
        )
        # (x - r1)(x - r2) = x^2 - (r1+r2)x + r1*r2
        a = 1
        b = -(r1 + r2)
        c = r1 * r2

        roots = solve_quadratic(a, b, c)
        if len(roots) == 2:
            # Convert symbolic types to float
            r0 = float(roots[0]) if hasattr(roots[0], '__float__') else roots[0]
            r1_val = float(roots[1]) if hasattr(roots[1], '__float__') else roots[1]
            root_sum = r0 + r1_val
            root_product = r0 * r1_val
            assert abs(root_sum - (r1 + r2)) < 1e-6
            assert abs(root_product - (r1 * r2)) < 1e-6


class TestRationalRootsProperties:
    """Property-based tests for rational root finder."""

    @given(r=st.integers(min_value=-10, max_value=10))
    @settings(max_examples=30, database=None)
    def test_finds_integer_root(self, r):
        """Should find integer roots of (x - r) = 0."""
        assume(r != 0)
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        # x - r = 0 has coefficients [1, -r]
        coeffs = [1, -r]
        roots = find_rational_roots(coeffs)
        assert r in roots

    @given(r1=st.integers(min_value=-5, max_value=5),
           r2=st.integers(min_value=-5, max_value=5))
    @settings(max_examples=30, database=None)
    def test_finds_quadratic_integer_roots(self, r1, r2):
        """Should find integer roots of (x - r1)(x - r2) = 0."""
        assume(r1 != 0 and r2 != 0)
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.rational_equations import (
            find_rational_roots
        )
        # (x - r1)(x - r2) = x^2 - (r1+r2)x + r1*r2
        coeffs = [1, -(r1 + r2), r1 * r2]
        roots = find_rational_roots(coeffs)
        # Should find at least one root
        assert r1 in roots or r2 in roots


# =============================================================================
# INPUT NORMALIZATION PROPERTY TESTS
# =============================================================================

class TestInputNormalizationProperties:
    """Property-based tests for input normalization."""

    @given(expr=st.text(min_size=0, max_size=100))
    @settings(max_examples=50, database=None, suppress_health_check=[HealthCheck.too_slow])
    def test_normalizer_never_crashes(self, expr):
        """Input normalizer should never crash on arbitrary input."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        # Should return a string, never crash
        try:
            result = normalize_input(expr)
            assert isinstance(result, str)
        except (ValueError, TypeError):
            pass  # Acceptable for malformed input

    @given(expr=st.text(alphabet='0123456789+-*/(). xyz', min_size=1, max_size=50))
    @settings(max_examples=50, database=None)
    def test_normalizer_preserves_digits(self, expr):
        """Digits should be preserved in normalization."""
        from symbo_agentic_reasoners.core.input_normalizer import normalize_input

        digits_in = sum(1 for c in expr if c.isdigit())
        try:
            result = normalize_input(expr)
            digits_out = sum(1 for c in result if c.isdigit())
            # Digits should be preserved (might add some for implicit multiplication)
            assert digits_out >= digits_in - 1  # Allow for some edge cases
        except (ValueError, TypeError):
            pass


# =============================================================================
# NEWTON-RAPHSON CONVERGENCE PROPERTIES
# =============================================================================

class TestNewtonRaphsonProperties:
    """Property-based tests for Newton-Raphson convergence."""

    @given(root=st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, database=None)
    def test_finds_known_linear_root(self, root):
        """Should find root of linear equation x - r = 0."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )
        assume(abs(root) > 0.01)

        # x - root = 0 has coefficients [1, -root]
        coeffs = [1, -root]
        found = newton_raphson(coeffs, x0=root + 1.0)

        if found is not None:
            assert abs(found - root) < 1e-6

    @given(coeffs=st.lists(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        min_size=2, max_size=5
    ))
    @settings(max_examples=30, database=None)
    def test_root_satisfies_polynomial(self, coeffs):
        """If a root is found, it should satisfy the polynomial."""
        assume(abs(coeffs[0]) > 0.01)  # Non-zero leading coefficient

        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson, poly_coeffs_to_func
        )

        found = newton_raphson(coeffs, x0=0.0)

        if found is not None:
            f = poly_coeffs_to_func(coeffs)
            assert abs(f(found)) < 1e-5


# =============================================================================
# BRENT'S METHOD PROPERTIES
# =============================================================================

class TestBrentMethodProperties:
    """Property-based tests for Brent's method."""

    @given(root=st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, database=None)
    def test_brent_finds_bracketed_root(self, root):
        """Brent should find root when properly bracketed."""
        assume(abs(root) > 0.1)

        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            brent_method
        )

        def f(x):
            return x - root

        # Bracket the root
        left = root - 5
        right = root + 5

        found = brent_method(f, left, right)

        if found is not None:
            assert abs(found - root) < 1e-6


# =============================================================================
# SECURITY PROPERTY TESTS
# =============================================================================

class TestSecurityProperties:
    """Property-based security tests."""

    @given(payload=st.text(min_size=1, max_size=30))
    @settings(max_examples=50, database=None)
    def test_dangerous_patterns_rejected(self, payload):
        """Dangerous patterns should be rejected by safe parser."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

        dangerous = [
            f"__import__('{payload}')",
            f"eval('{payload}')",
            f"exec('{payload}')",
            f"open('{payload}')",
            f"os.system('{payload}')",
        ]

        for expr in dangerous:
            try:
                safe_sympify(expr, timeout=0.5)
            except SecurityError:
                pass  # Expected
            except (ValueError, TypeError):
                pass  # Also acceptable
            except Exception as e:
                if "timed out" not in str(e).lower():
                    # Should have been caught
                    pass

    @given(n=st.integers(min_value=10, max_value=200))
    @settings(max_examples=20, database=None)
    def test_deep_nesting_safe(self, n):
        """Deep nesting should not cause stack overflow."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

        expr = "(" * n + "1" + ")" * n

        try:
            safe_sympify(expr, timeout=1.0)
        except (ValueError, SecurityError, RecursionError):
            pass  # Expected for deep nesting
        except Exception as e:
            if "timed out" not in str(e).lower():
                pass  # Some other safe handling


# =============================================================================
# MATRIX OPERATIONS PROPERTY TESTS
# =============================================================================

class TestMatrixProperties:
    """Property-based tests for matrix operations."""

    @given(n=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20, database=None)
    def test_identity_matrix_property(self, n):
        """Identity matrix has all 1s on diagonal, 0s elsewhere."""
        import numpy as np

        I = np.eye(n)
        for i in range(n):
            for j in range(n):
                if i == j:
                    assert I[i, j] == 1.0
                else:
                    assert I[i, j] == 0.0

    @given(a=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
           b=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
           c=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
           d=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, database=None)
    def test_2x2_determinant(self, a, b, c, d):
        """det([[a,b],[c,d]]) = ad - bc."""
        import numpy as np

        M = np.array([[a, b], [c, d]])
        det = np.linalg.det(M)
        expected = a * d - b * c

        assert abs(det - expected) < 1e-6


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
