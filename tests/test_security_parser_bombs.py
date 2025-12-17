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
Parser Bomb Tests
==================

Tests for malicious expressions designed to cause:
- Exponential complexity
- Memory exhaustion
- Stack overflow
- Infinite loops
- Timeout violations
"""

import pytest
import time
from symbo_agentic_reasoners.core.safe_parser import safe_parse


class TestComputationBombs:
    """Test expressions that cause exponential computational complexity."""

    @pytest.mark.timeout(5)
    def test_exponential_expansion_bomb(self):
        """Polynomial expansion bomb."""
        bomb = "(x + 1)**1000 * (x + 2)**1000"

        start = time.time()
        try:
            result = safe_parse(bomb)
            elapsed = time.time() - start
            assert elapsed < 5.0, f"Expansion took {elapsed}s"
        except (ValueError, MemoryError, TimeoutError):
            # Rejection or controlled failure is acceptable
            pass

    @pytest.mark.timeout(3)
    def test_factorial_bomb(self):
        """Large factorial computation.

        Native parser creates lazy GenericFunction representation without computing.
        This is correct behavior - the computation would only happen at evaluation.
        """
        import time
        start = time.time()
        try:
            result = safe_parse("factorial(100000)")
            elapsed = time.time() - start
            # If parsing succeeds quickly with lazy representation, that's acceptable
            assert elapsed < 1.0, f"Factorial parsing took {elapsed}s (should be instant)"
        except (ValueError, MemoryError, OverflowError, TimeoutError):
            # Rejection or controlled failure is also acceptable
            pass

    @pytest.mark.timeout(5)
    def test_nested_exponentiation(self):
        """Nested exponentiation causing exponential growth."""
        bomb = "x**(y**(z**5))"

        try:
            result = safe_parse(bomb)
            # If parsing succeeds, evaluation should be lazy
        except (ValueError, OverflowError):
            # Rejection is acceptable
            pass

    @pytest.mark.timeout(10)
    def test_polynomial_gcd_bomb(self):
        """GCD computation on large polynomials.

        Native parser creates lazy Gcd representation without computing.
        This is correct behavior - the computation would only happen at evaluation.
        """
        import time
        bomb = "gcd(x**500 - 1, x**499 - 1)"

        start = time.time()
        try:
            result = safe_parse(bomb)
            elapsed = time.time() - start
            # If parsing succeeds quickly with lazy representation, that's acceptable
            assert elapsed < 1.0, f"GCD parsing took {elapsed}s (should be instant)"
        except (ValueError, TimeoutError, NotImplementedError):
            # Rejection is also acceptable
            pass


class TestMemoryBombs:
    """Test expressions designed to consume excessive memory."""

    def test_large_polynomial_expansion(self):
        """Expand very large polynomial.

        Native parser creates lazy Pow representation without expanding.
        This is correct behavior - expansion would only happen at evaluation.
        """
        import time
        bomb = "(x + 1)**10000"

        start = time.time()
        try:
            result = safe_parse(bomb)
            elapsed = time.time() - start
            # If parsing succeeds quickly with lazy representation, that's acceptable
            assert elapsed < 1.0, f"Polynomial parsing took {elapsed}s (should be instant)"
        except (ValueError, MemoryError):
            # Rejection is also acceptable
            pass

    def test_matrix_size_bomb(self):
        """Create extremely large matrix.

        Lambda expressions are blocked by security filter as potential code injection.
        """
        from symbo_agentic_reasoners.core.safe_parser import SecurityError
        bomb = "Matrix(1000, 1000, lambda i,j: i+j)"

        with pytest.raises((ValueError, MemoryError, NotImplementedError, SecurityError)):
            safe_parse(bomb)

    def test_symbol_generation_bomb(self):
        """Generate huge number of symbols."""
        # Generate 10000 symbols: x0, x1, x2, ..., x9999
        bomb = "symbols('x0:10000')"

        with pytest.raises((ValueError, MemoryError)):
            safe_parse(bomb)

    def test_large_rational_number(self):
        """Create rational with huge numerator."""
        bomb = "Rational(10**10000, 1)"

        with pytest.raises((ValueError, MemoryError, OverflowError)):
            safe_parse(bomb)

    def test_string_repetition_bomb(self):
        """String/expression repetition bomb."""
        bomb = "x + " * 100000 + "1"

        with pytest.raises((ValueError, MemoryError)):
            safe_parse(bomb)


class TestStackOverflowAttacks:
    """Test deeply nested expressions that cause stack overflow."""

    def test_deeply_nested_parentheses(self):
        """Exceed maximum nesting depth."""
        depth = 100
        bomb = "(" * depth + "x" + ")" * depth

        with pytest.raises((ValueError, RecursionError)) as exc_info:
            safe_parse(bomb)

        # Should have a controlled error, not Python stack overflow
        assert "nesting" in str(exc_info.value).lower() or \
               "depth" in str(exc_info.value).lower()

    def test_deeply_nested_functions(self):
        """Nested function calls."""
        depth = 200
        bomb = "sin(" * depth + "x" + ")" * depth

        with pytest.raises((ValueError, RecursionError)):
            safe_parse(bomb)

    def test_nested_list_bomb(self):
        """Deeply nested list/matrix structures."""
        depth = 100
        bomb = "[" * depth + "1" + "]" * depth

        with pytest.raises((ValueError, RecursionError)):
            safe_parse(bomb)

    def test_recursive_expression_reference(self):
        """Self-referential expression (if possible)."""
        # This should be caught by parser
        bomb = "solve(x - solve(x, x), x)"

        try:
            safe_parse(bomb)
            # If it parses, it should not cause infinite recursion
        except (ValueError, RecursionError, NotImplementedError):
            # Rejection is fine
            pass


class TestInfiniteLoopTriggers:
    """Test expressions that might cause infinite loops."""

    @pytest.mark.timeout(10)
    def test_circular_substitution(self):
        """Circular substitution pattern."""
        # This should be detected and prevented
        bomb = "subs(x, y, subs(y, x, expr))"

        with pytest.raises((ValueError, TimeoutError, RecursionError)):
            safe_parse(bomb)

    @pytest.mark.timeout(10)
    def test_limit_with_oscillation(self):
        """Limit that oscillates infinitely.

        Acceptable outcomes:
        - Parse succeeds (returns unevaluated GenericFunction)
        - Raises controlled exception
        """
        bomb = "limit(sin(x)/x * x**x, x, oo)"

        try:
            result = safe_parse(bomb)
            # If parsing succeeds with unevaluated representation, that's acceptable
            assert result is not None
        except (ValueError, TimeoutError, NotImplementedError):
            # Rejection is also acceptable
            pass

    @pytest.mark.timeout(10)
    def test_non_convergent_series(self):
        """Series that doesn't converge."""
        bomb = "series(1/sin(x), x, 0, n=1000000)"

        with pytest.raises((ValueError, TimeoutError, MemoryError)):
            safe_parse(bomb)


class TestComplexityAmplification:
    """Test expressions that cause complexity amplification during processing."""

    @pytest.mark.timeout(10)
    def test_trigonometric_expansion_bomb(self):
        """Expanding high-power trigonometric expressions."""
        bomb = "expand(sin(x)**1000 + cos(x)**1000)"

        with pytest.raises((ValueError, TimeoutError, MemoryError)):
            safe_parse(bomb)

    @pytest.mark.timeout(10)
    def test_logarithm_expansion_bomb(self):
        """Logarithm expansion bomb."""
        bomb = "expand_log(log((x*y*z*w)**1000))"

        with pytest.raises((ValueError, TimeoutError, MemoryError, NotImplementedError)):
            safe_parse(bomb)

    @pytest.mark.timeout(10)
    def test_multinomial_expansion(self):
        """Multinomial expansion with many terms.

        Native parser creates lazy Pow representation without expanding.
        This is correct behavior - expansion would only happen at evaluation.
        """
        import time
        bomb = "(x + y + z + w + a + b + c)**50"

        start = time.time()
        try:
            result = safe_parse(bomb)
            elapsed = time.time() - start
            # If parsing succeeds quickly with lazy representation, that's acceptable
            assert elapsed < 1.0, f"Multinomial parsing took {elapsed}s (should be instant)"
        except (ValueError, TimeoutError, MemoryError):
            # Rejection is also acceptable
            pass


class TestDeterminantBombs:
    """Test determinant computation bombs."""

    @pytest.mark.timeout(20)
    def test_large_symbolic_matrix_determinant(self):
        """Determinant of large symbolic matrix."""
        # Determinant complexity is O(n!)
        bomb = "det(Matrix([[x**i*y**j for j in range(15)] for i in range(15)]))"

        with pytest.raises((ValueError, TimeoutError, MemoryError, NotImplementedError)):
            safe_parse(bomb)

    @pytest.mark.timeout(15)
    def test_complex_symbolic_determinant(self):
        """Determinant with complex symbolic entries."""
        bomb = "det(Matrix([[i*j*x + i*y + j*z for j in range(12)] for i in range(12)]))"

        with pytest.raises((ValueError, TimeoutError, MemoryError, NotImplementedError)):
            safe_parse(bomb)


class TestIntegrationBombs:
    """Test integrals that are extremely expensive or impossible."""

    @pytest.mark.timeout(30)
    def test_fresnel_integral(self):
        """Fresnel integral (no elementary form).

        Acceptable outcomes:
        - Parse succeeds (returns unevaluated GenericFunction)
        - Raises controlled exception
        """
        bomb = "integrate(sin(x**2), x)"

        try:
            result = safe_parse(bomb)
            # If parsing succeeds with unevaluated representation, that's acceptable
            assert result is not None
        except (ValueError, TimeoutError, NotImplementedError):
            # Rejection is also acceptable
            pass

    @pytest.mark.timeout(30)
    def test_error_function_integral(self):
        """Error function integral.

        Acceptable outcomes:
        - Parse succeeds (returns unevaluated GenericFunction)
        - Raises controlled exception
        """
        bomb = "integrate(exp(x**2), x)"

        try:
            result = safe_parse(bomb)
            # If parsing succeeds with unevaluated representation, that's acceptable
            assert result is not None
        except (ValueError, TimeoutError, NotImplementedError):
            # Rejection is also acceptable
            pass

    @pytest.mark.timeout(30)
    def test_elliptic_integral(self):
        """Elliptic integral.

        Acceptable outcomes:
        - Parse succeeds (returns unevaluated GenericFunction)
        - Raises controlled exception
        """
        bomb = "integrate(1/sqrt(x**3 - x + 1), x)"

        try:
            result = safe_parse(bomb)
            # If parsing succeeds with unevaluated representation, that's acceptable
            assert result is not None
        except (ValueError, TimeoutError, NotImplementedError):
            # Rejection is also acceptable
            pass

    @pytest.mark.timeout(30)
    def test_high_degree_rational_integral(self):
        """High-degree rational function integration.

        Acceptable outcomes:
        - Parse succeeds (returns unevaluated GenericFunction)
        - Raises controlled exception
        """
        bomb = "integrate((x**100 + 1)/(x**100 + x + 1), x)"

        try:
            result = safe_parse(bomb)
            # If parsing succeeds with unevaluated representation, that's acceptable
            assert result is not None
        except (ValueError, TimeoutError, MemoryError):
            # Rejection is also acceptable
            pass


class TestRepeatedOperations:
    """Test repeated operations that amplify complexity."""

    @pytest.mark.timeout(10)
    def test_repeated_differentiation(self):
        """Differentiate many times."""
        expr = "(x**10 + x**9 + x**8)"
        for _ in range(50):
            expr = f"diff({expr}, x)"

        with pytest.raises((ValueError, TimeoutError, RecursionError)):
            safe_parse(expr)

    @pytest.mark.timeout(10)
    def test_repeated_expansion(self):
        """Expand repeatedly."""
        expr = "(x + 1)**10"
        for _ in range(10):
            expr = f"expand({expr}**2)"

        with pytest.raises((ValueError, TimeoutError, MemoryError)):
            safe_parse(expr)

    @pytest.mark.timeout(10)
    def test_repeated_simplification(self):
        """Simplify repeatedly."""
        expr = "((x + 1)*(x - 1))**5"
        for _ in range(100):
            expr = f"simplify({expr})"

        with pytest.raises((ValueError, TimeoutError, RecursionError)):
            safe_parse(expr)


class TestMixedComplexityBombs:
    """Test combinations of different complexity attacks."""

    @pytest.mark.timeout(15)
    def test_expansion_plus_factorial(self):
        """Combine expansion with factorial."""
        bomb = "expand((x + factorial(1000))**100)"

        with pytest.raises((ValueError, TimeoutError, MemoryError, OverflowError)):
            safe_parse(bomb)

    @pytest.mark.timeout(15)
    def test_nested_integration_differentiation(self):
        """Nested calculus operations.

        Acceptable outcomes:
        - Parse succeeds (returns unevaluated GenericFunction)
        - Raises controlled exception
        """
        bomb = "integrate(diff(sin(x**10), x)**10, x)"

        try:
            result = safe_parse(bomb)
            # If parsing succeeds with unevaluated representation, that's acceptable
            assert result is not None
        except (ValueError, TimeoutError, MemoryError):
            # Rejection is also acceptable
            pass

    @pytest.mark.timeout(15)
    def test_matrix_with_expansion(self):
        """Matrix with expansion in entries."""
        bomb = "det(Matrix([[expand((x+i)**100) for i in range(5)] for j in range(5)]))"

        with pytest.raises((ValueError, TimeoutError, MemoryError)):
            safe_parse(bomb)


class TestRegexDOS:
    """Test Regular Expression Denial of Service (ReDoS) attacks."""

    def test_catastrophic_backtracking_pattern(self):
        """Expression that causes catastrophic backtracking if regex-based."""
        # Pattern: (a+)+b
        bomb = "x" + "1" * 10000 + "2"

        # Should parse quickly or reject
        start = time.time()
        try:
            result = safe_parse(bomb)
            elapsed = time.time() - start
            assert elapsed < 1.0, f"ReDoS vulnerability: took {elapsed}s"
        except (ValueError, TimeoutError):
            elapsed = time.time() - start
            assert elapsed < 1.0, f"ReDoS vulnerability: rejection took {elapsed}s"

    def test_nested_quantifier_pattern(self):
        """Nested quantifiers in expression."""
        bomb = "(" + "a" * 5000 + ")+" + "b"

        start = time.time()
        try:
            safe_parse(bomb)
        except:
            pass
        elapsed = time.time() - start
        assert elapsed < 1.0, "Possible ReDoS vulnerability"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
