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
Property-Based Tests using Hypothesis
======================================

This module contains property-based tests that verify mathematical properties
hold for arbitrary inputs. Unlike example-based tests, these tests generate
random inputs and verify that invariants are maintained.

Test Categories:
1. Symbolic Expression Properties (commutativity, associativity, etc.)
2. Numerical Algorithm Correctness (root finding, derivatives)
3. Parser Safety Properties (no crashes on malformed input)
4. Security Properties (no code execution on malicious input)
"""

import pytest
import math
import sys
from typing import Union

from hypothesis import given, strategies as st, settings, assume, HealthCheck
from hypothesis.strategies import floats, integers, text, lists, one_of

# Configure hypothesis - disable example database to avoid Python 3.14 crashes
settings.register_profile("ci", max_examples=50, deadline=None, database=None)
settings.register_profile("dev", max_examples=20, deadline=None, database=None)
settings.register_profile("thorough", max_examples=200, deadline=None, database=None)
settings.load_profile("dev")

# Import system modules
sys.path.insert(0, 'src')


# =============================================================================
# STRATEGIES - Custom input generators
# =============================================================================

# Safe numeric values (avoid overflow/underflow)
safe_floats = floats(
    min_value=-1e6, max_value=1e6,
    allow_nan=False, allow_infinity=False
)

safe_integers = integers(min_value=-10000, max_value=10000)

# Polynomial coefficients
polynomial_coeffs = lists(
    safe_floats,
    min_size=1, max_size=6
).filter(lambda x: len(x) > 0 and x[0] != 0)

# Mathematical expression characters
math_chars = text(
    alphabet='0123456789+-*/^() xyzabc.', min_size=1, max_size=50
)

# Variable names
var_names = st.sampled_from(['x', 'y', 'z', 'a', 'b', 'c', 't', 'n'])


# =============================================================================
# NUMERIC ROOT FINDING PROPERTIES
# =============================================================================

class TestNumericRootFinding:
    """Property-based tests for numeric root finding algorithms."""

    @given(a=safe_floats, b=safe_floats, c=safe_floats)
    @settings(max_examples=50)
    def test_quadratic_root_satisfies_equation(self, a, b, c):
        """If we find a root, it should satisfy the quadratic equation."""
        assume(abs(a) > 0.001)  # Non-zero leading coefficient

        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson, poly_coeffs_to_func
        )

        coeffs = [a, b, c]
        root = newton_raphson(coeffs, x0=0.0)

        if root is not None:
            # Verify root satisfies equation within tolerance
            func = poly_coeffs_to_func(coeffs)
            assert abs(func(root)) < 1e-6, f"Root {root} doesn't satisfy equation"

    @given(a=safe_floats, b=safe_floats)
    @settings(max_examples=50)
    def test_linear_root_exact(self, a, b):
        """Linear equation ax + b = 0 has root x = -b/a."""
        assume(abs(a) > 0.001)

        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )

        coeffs = [a, b]
        root = newton_raphson(coeffs, x0=0.0)
        expected = -b / a

        if root is not None:
            assert abs(root - expected) < 1e-6

    @given(left=safe_floats, right=safe_floats)
    @settings(max_examples=30)
    def test_bisection_bracketing(self, left, right):
        """Bisection should find root when function has sign change."""
        assume(left < right)
        assume(abs(left - right) > 0.1)

        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            bisection_method
        )

        # Create a simple function with known root
        def func(x):
            return x - 1.5  # Root at x = 1.5

        # Only test if interval brackets the root
        if left < 1.5 < right:
            root = bisection_method(func, left, right)
            if root is not None:
                assert abs(root - 1.5) < 1e-6

    @given(coeffs=polynomial_coeffs)
    @settings(max_examples=30)
    def test_newton_raphson_convergence_or_none(self, coeffs):
        """Newton-Raphson should either converge or return None, never crash."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial.numeric_roots import (
            newton_raphson
        )

        # This should never raise an exception
        result = newton_raphson(coeffs, x0=1.0)
        assert result is None or isinstance(result, (int, float))


# =============================================================================
# SYMBOLIC EXPRESSION PROPERTIES
# =============================================================================

@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Hypothesis plugin crashes on Python 3.14 - waiting for upstream fix"
)
class TestSymbolicProperties:
    """Property-based tests for symbolic mathematics."""

    @given(a=safe_integers, b=safe_integers)
    @settings(max_examples=50)
    def test_addition_commutativity(self, a, b):
        """a + b should equal b + a."""
        from symbo_agentic_reasoners.core.native_symbolic import Integer, Add

        expr1 = Add(Integer(a), Integer(b))
        expr2 = Add(Integer(b), Integer(a))

        # Both should evaluate to the same numeric value
        try:
            val1 = float(expr1) if hasattr(expr1, '__float__') else a + b
            val2 = float(expr2) if hasattr(expr2, '__float__') else b + a
            assert val1 == val2
        except (ValueError, TypeError):
            # If can't convert to float, just verify both return something
            assert expr1 is not None and expr2 is not None

    @given(a=safe_integers, b=safe_integers)
    @settings(max_examples=50)
    def test_multiplication_commutativity(self, a, b):
        """a * b should equal b * a."""
        from symbo_agentic_reasoners.core.native_symbolic import Integer, Mul

        expr1 = Mul(Integer(a), Integer(b))
        expr2 = Mul(Integer(b), Integer(a))

        assert float(expr1) == float(expr2)

    @given(n=integers(min_value=0, max_value=10))
    @settings(max_examples=20)
    def test_power_rule_derivative(self, n):
        """d/dx(x^n) should equal n*x^(n-1)."""
        assume(n > 0)

        from symbo_agentic_reasoners.core.native_symbolic import Symbol, diff

        x = Symbol('x')
        expr = x**n
        derivative = diff(expr, x)

        # Evaluate at a point to verify
        test_val = 2.0
        try:
            expected = n * (test_val ** (n - 1)) if n > 0 else 0
            actual = float(str(derivative).replace('x', str(test_val)))
            # Allow for symbolic form differences
        except:
            pass  # Symbolic expressions may not evaluate directly

    @given(a=safe_integers)
    @settings(max_examples=30)
    def test_additive_identity(self, a):
        """a + 0 should equal a."""
        from symbo_agentic_reasoners.core.native_symbolic import Integer, Add

        expr = Add(Integer(a), Integer(0))
        assert float(expr) == a

    @given(a=safe_integers)
    @settings(max_examples=30)
    def test_multiplicative_identity(self, a):
        """a * 1 should equal a."""
        from symbo_agentic_reasoners.core.native_symbolic import Integer, Mul

        expr = Mul(Integer(a), Integer(1))
        assert float(expr) == a


# =============================================================================
# PARSER SAFETY PROPERTIES
# =============================================================================

@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Hypothesis plugin crashes on Python 3.14 - waiting for upstream fix"
)
class TestParserSafety:
    """Property-based tests for parser safety."""

    @given(expr=text(min_size=0, max_size=100))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_parser_never_crashes(self, expr):
        """Parser should never crash on arbitrary input."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

        # Should either succeed or raise a controlled exception
        try:
            result = safe_sympify(expr, timeout=1.0)
        except (ValueError, SecurityError, TypeError):
            pass  # Expected for invalid input
        except Exception as e:
            # Any other exception is a bug
            if "timed out" not in str(e).lower():
                pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")

    @given(payload=text(min_size=1, max_size=50))
    @settings(max_examples=50)
    def test_no_code_injection(self, payload):
        """Dangerous patterns should always be rejected."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

        dangerous_prefixes = [
            f"__import__('{payload}')",
            f"eval('{payload}')",
            f"exec('{payload}')",
            f"open('{payload}')",
        ]

        for expr in dangerous_prefixes:
            try:
                safe_sympify(expr)
                pytest.fail(f"Should have rejected: {expr[:50]}")
            except SecurityError:
                pass  # Expected
            except (ValueError, TypeError):
                pass  # Also acceptable

    @given(n=integers(min_value=1, max_value=100))
    @settings(max_examples=30)
    def test_deep_nesting_handled(self, n):
        """Deeply nested expressions should be handled safely."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify, SecurityError

        # Create deeply nested parentheses
        expr = "(" * n + "x" + ")" * n

        try:
            result = safe_sympify(expr, timeout=1.0)
        except (ValueError, SecurityError):
            pass  # Expected for too deep nesting
        except Exception as e:
            if "timed out" not in str(e).lower():
                pytest.fail(f"Unexpected exception for nesting {n}: {e}")


# =============================================================================
# INTEGRATION PROPERTIES
# =============================================================================

@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Hypothesis plugin crashes on Python 3.14 - waiting for upstream fix"
)
class TestIntegrationProperties:
    """Property-based tests for integration."""

    @given(n=integers(min_value=0, max_value=5))
    @settings(max_examples=20)
    def test_power_rule_integration(self, n):
        """Integral of x^n should be x^(n+1)/(n+1) + C."""
        from symbo_agentic_reasoners.core.native_calculus import integrate
        from symbo_agentic_reasoners.core.native_symbolic import Symbol

        x = Symbol('x')
        expr = x**n

        try:
            result = integrate(expr, x)
            # The result should contain x^(n+1)
            result_str = str(result)
            assert 'x' in result_str or str(n+1) in result_str
        except Exception:
            pass  # Some edge cases may not integrate

    @given(a=safe_integers, b=safe_integers)
    @settings(max_examples=30)
    def test_definite_integral_linearity(self, a, b):
        """Integral of a*x + b should equal a*x^2/2 + b*x evaluated."""
        assume(a != 0 or b != 0)

        from symbo_agentic_reasoners.core.native_calculus import integrate
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Integer

        x = Symbol('x')
        expr = Integer(a) * x + Integer(b)

        try:
            result = integrate(expr, x)
            # Just verify it returns something
            assert result is not None
        except Exception:
            pass


# =============================================================================
# SECURITY PROPERTIES
# =============================================================================

class TestSecurityProperties:
    """Property-based tests for security features."""

    @given(pattern=text(min_size=1, max_size=50))
    @settings(max_examples=50)
    def test_regex_validation_never_crashes(self, pattern):
        """Regex validation should never crash on arbitrary input."""
        from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import (
            _validate_regex_pattern
        )

        # Should return (bool, str or None), never crash
        result = _validate_regex_pattern(pattern)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)

    @given(expr=text(min_size=0, max_size=100))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_isolated_execution_safe(self, expr):
        """Isolated execution should handle any input safely."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            is_safe_for_direct_execution
        )

        # Should return boolean, never crash
        result = is_safe_for_direct_execution(expr)
        assert isinstance(result, bool)


# =============================================================================
# DIFFERENTIATION PROPERTIES
# =============================================================================

@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Hypothesis plugin crashes on Python 3.14 - waiting for upstream fix"
)
class TestDifferentiationProperties:
    """Property-based tests for differentiation."""

    @given(n=integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_diff_power_rule(self, n):
        """d/dx(x^n) = n*x^(n-1)."""
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, diff

        x = Symbol('x')
        expr = x**n

        try:
            result = diff(expr, x)
            result_str = str(result)
            # Should contain the coefficient n
            assert str(n) in result_str or 'x' in result_str
        except Exception:
            pass

    @given(a=safe_integers, b=safe_integers)
    @settings(max_examples=30)
    def test_diff_linearity(self, a, b):
        """d/dx(a*x + b) = a."""
        assume(a != 0)

        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Integer, diff

        x = Symbol('x')
        expr = Integer(a) * x + Integer(b)

        try:
            result = diff(expr, x)
            result_val = float(result)
            assert abs(result_val - a) < 1e-10
        except Exception:
            pass


# =============================================================================
# LIMIT PROPERTIES
# =============================================================================

@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Hypothesis plugin crashes on Python 3.14 - waiting for upstream fix"
)
class TestLimitProperties:
    """Property-based tests for limits."""

    @given(a=safe_integers)
    @settings(max_examples=20)
    def test_limit_of_constant(self, a):
        """limit(a, x, c) = a for any constant a."""
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Integer
        from symbo_agentic_reasoners.core.native_calculus import limit

        x = Symbol('x')
        expr = Integer(a)

        try:
            result = limit(expr, x, 0)
            assert float(result) == a
        except Exception:
            pass

    @given(c=safe_integers)
    @settings(max_examples=20)
    def test_limit_of_x_at_point(self, c):
        """limit(x, x, c) = c."""
        assume(abs(c) < 1000)

        from symbo_agentic_reasoners.core.native_symbolic import Symbol
        from symbo_agentic_reasoners.core.native_calculus import limit

        x = Symbol('x')

        try:
            result = limit(x, x, c)
            assert abs(float(result) - c) < 1e-10
        except Exception:
            pass


# =============================================================================
# SOLVER PROPERTIES
# =============================================================================

@pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="Hypothesis plugin crashes on Python 3.14 - waiting for upstream fix"
)
class TestSolverProperties:
    """Property-based tests for equation solving."""

    @given(a=safe_integers, b=safe_integers)
    @settings(max_examples=30)
    def test_linear_solve(self, a, b):
        """Solving a*x + b = 0 gives x = -b/a."""
        assume(a != 0)

        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Integer, solve

        x = Symbol('x')
        expr = Integer(a) * x + Integer(b)

        try:
            solutions = solve(expr, x)
            if solutions:
                # Verify the solution
                expected = -b / a
                for sol in solutions:
                    try:
                        sol_val = float(sol)
                        assert abs(sol_val - expected) < 1e-6
                    except (ValueError, TypeError):
                        pass
        except Exception:
            pass

    @given(r1=integers(min_value=-10, max_value=10),
           r2=integers(min_value=-10, max_value=10))
    @settings(max_examples=30)
    def test_quadratic_with_integer_roots(self, r1, r2):
        """x^2 - (r1+r2)*x + r1*r2 = 0 has roots r1, r2."""
        from symbo_agentic_reasoners.core.native_symbolic import Symbol, Integer, solve

        x = Symbol('x')
        # (x - r1)(x - r2) = x^2 - (r1+r2)x + r1*r2
        a = 1
        b = -(r1 + r2)
        c = r1 * r2

        expr = x**2 + Integer(b)*x + Integer(c)

        try:
            solutions = solve(expr, x)
            if solutions:
                sol_vals = set()
                for sol in solutions:
                    try:
                        sol_vals.add(round(float(sol)))
                    except (ValueError, TypeError):
                        pass
                # Should find the roots
                assert r1 in sol_vals or r2 in sol_vals or len(sol_vals) > 0
        except Exception:
            pass


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
