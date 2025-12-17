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
Tests for Parser Timeout Hardening
===================================

Tests for timeout protection, complexity estimation, and DoS prevention
in the safe parser module.
"""

import pytest
import os
import time


class TestTimeoutBounds:
    """Tests for timeout enforcement."""

    def test_min_timeout_enforced(self):
        """Timeout below minimum should be raised to minimum."""
        from symbo_agentic_reasoners.core.safe_parser import (
            _enforce_timeout_bounds, MIN_TIMEOUT_SECONDS
        )
        result = _enforce_timeout_bounds(0.001)
        assert result == MIN_TIMEOUT_SECONDS

    def test_max_timeout_enforced(self):
        """Timeout above maximum should be lowered to maximum."""
        from symbo_agentic_reasoners.core.safe_parser import (
            _enforce_timeout_bounds, MAX_TIMEOUT_SECONDS
        )
        result = _enforce_timeout_bounds(1000.0)
        assert result == MAX_TIMEOUT_SECONDS

    def test_valid_timeout_unchanged(self):
        """Valid timeout should pass through unchanged."""
        from symbo_agentic_reasoners.core.safe_parser import _enforce_timeout_bounds
        result = _enforce_timeout_bounds(2.5)
        assert result == 2.5

    def test_default_timeout_from_env(self):
        """Default timeout should come from environment variable."""
        from symbo_agentic_reasoners.core.safe_parser import _get_default_timeout
        old_val = os.environ.get('SYMBO_PARSE_TIMEOUT')
        try:
            os.environ['SYMBO_PARSE_TIMEOUT'] = '3.5'
            result = _get_default_timeout()
            assert result == 3.5
        finally:
            if old_val:
                os.environ['SYMBO_PARSE_TIMEOUT'] = old_val
            else:
                os.environ.pop('SYMBO_PARSE_TIMEOUT', None)

    def test_env_timeout_clamped_to_max(self):
        """Environment timeout exceeding max should be clamped."""
        from symbo_agentic_reasoners.core.safe_parser import _get_default_timeout
        old_val = os.environ.get('SYMBO_PARSE_TIMEOUT')
        try:
            os.environ['SYMBO_PARSE_TIMEOUT'] = '100'
            result = _get_default_timeout()
            assert result == 60.0  # MAX_TIMEOUT_SECONDS
        finally:
            if old_val:
                os.environ['SYMBO_PARSE_TIMEOUT'] = old_val
            else:
                os.environ.pop('SYMBO_PARSE_TIMEOUT', None)

    def test_env_timeout_clamped_to_min(self):
        """Environment timeout below min should be clamped."""
        from symbo_agentic_reasoners.core.safe_parser import _get_default_timeout
        old_val = os.environ.get('SYMBO_PARSE_TIMEOUT')
        try:
            os.environ['SYMBO_PARSE_TIMEOUT'] = '0.01'
            result = _get_default_timeout()
            assert result == 0.1  # MIN_TIMEOUT_SECONDS
        finally:
            if old_val:
                os.environ['SYMBO_PARSE_TIMEOUT'] = old_val
            else:
                os.environ.pop('SYMBO_PARSE_TIMEOUT', None)

    def test_invalid_env_timeout_uses_default(self):
        """Invalid environment timeout should use default."""
        from symbo_agentic_reasoners.core.safe_parser import _get_default_timeout
        old_val = os.environ.get('SYMBO_PARSE_TIMEOUT')
        try:
            os.environ['SYMBO_PARSE_TIMEOUT'] = 'not_a_number'
            result = _get_default_timeout()
            assert result == 5.0  # Default
        finally:
            if old_val:
                os.environ['SYMBO_PARSE_TIMEOUT'] = old_val
            else:
                os.environ.pop('SYMBO_PARSE_TIMEOUT', None)


class TestComplexityEstimation:
    """Tests for expression complexity estimation."""

    def test_simple_expression_low_complexity(self):
        """Simple expressions should have low complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        score = _estimate_complexity("x + 1")
        assert score < 50

    def test_exponentiation_increases_complexity(self):
        """Exponentiation should increase complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        score_without = _estimate_complexity("x + y")
        score_with = _estimate_complexity("x**y")
        assert score_with > score_without

    def test_factorial_increases_complexity(self):
        """Factorial should significantly increase complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        score_without = _estimate_complexity("x + 1")
        score_with = _estimate_complexity("factorial(x)")
        assert score_with > score_without + 10

    def test_integration_very_high_complexity(self):
        """Integration should have very high complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        score = _estimate_complexity("integrate(sin(x), x)")
        assert score > 30

    def test_deep_nesting_increases_complexity(self):
        """Deep nesting should increase complexity quadratically."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        shallow = _estimate_complexity("((x))")
        deep = _estimate_complexity("((((((((x))))))))")
        assert deep > shallow * 2

    def test_tower_of_powers_high_complexity(self):
        """Tower of powers (x**y**z) should have high complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        single = _estimate_complexity("x**2")
        tower = _estimate_complexity("x**y**z")
        assert tower > single + 40

    def test_large_numbers_increase_complexity(self):
        """Large numbers should increase complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        small = _estimate_complexity("x + 1")
        large = _estimate_complexity("x + 12345678901234567890")
        assert large > small


class TestComplexityValidation:
    """Tests for complexity validation in parsing."""

    def test_simple_expression_passes(self):
        """Simple expressions should pass complexity check."""
        from symbo_agentic_reasoners.core.safe_parser import validate_input
        # Should not raise
        validate_input("x + y + z", check_complexity=True)

    def test_moderate_expression_passes(self):
        """Moderately complex expressions should pass."""
        from symbo_agentic_reasoners.core.safe_parser import validate_input
        # Should not raise
        validate_input("sin(x) + cos(y) + tan(z)", check_complexity=True)

    def test_very_complex_expression_rejected(self):
        """Very complex expressions should be rejected."""
        from symbo_agentic_reasoners.core.safe_parser import (
            validate_input, ExpressionComplexityError
        )
        # Build a pathologically complex expression (deep nesting triggers quadratic penalty)
        complex_expr = "(" * 35 + "x" + ")" * 35  # 35^2 = 1225 > 1000
        with pytest.raises(ExpressionComplexityError):
            validate_input(complex_expr, check_complexity=True)

    def test_complexity_check_can_be_disabled(self):
        """Complexity check should be disableable."""
        from symbo_agentic_reasoners.core.safe_parser import validate_input
        # Should not raise when check_complexity=False
        complex_expr = "integrate(" * 10 + "x" + ")" * 10
        validate_input(complex_expr, check_complexity=False)


class TestExpressionComplexityError:
    """Tests for ExpressionComplexityError exception."""

    def test_exception_inherits_security_error(self):
        """ExpressionComplexityError should inherit from SecurityError."""
        from symbo_agentic_reasoners.core.safe_parser import (
            ExpressionComplexityError, SecurityError
        )
        assert issubclass(ExpressionComplexityError, SecurityError)

    def test_exception_can_be_raised(self):
        """ExpressionComplexityError should be raisable."""
        from symbo_agentic_reasoners.core.safe_parser import ExpressionComplexityError
        with pytest.raises(ExpressionComplexityError):
            raise ExpressionComplexityError("Test")

    def test_exception_message(self):
        """Exception should preserve message."""
        from symbo_agentic_reasoners.core.safe_parser import ExpressionComplexityError
        try:
            raise ExpressionComplexityError("Too complex!")
        except ExpressionComplexityError as e:
            assert "complex" in str(e).lower()


class TestSafeSympifyTimeout:
    """Tests for safe_sympify timeout handling."""

    def test_timeout_parameter_accepted(self):
        """safe_sympify should accept timeout parameter."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify
        # Should not raise
        result = safe_sympify("x + 1", timeout=2.0)
        assert result is not None

    def test_very_small_timeout_clamped(self):
        """Very small timeout should be clamped to minimum."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify
        # Should not raise - timeout will be clamped
        result = safe_sympify("x + 1", timeout=0.001)
        assert result is not None

    def test_large_timeout_clamped(self):
        """Large timeout should be clamped to maximum."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify
        # Should not raise - timeout will be clamped
        result = safe_sympify("x + 1", timeout=1000.0)
        assert result is not None

    def test_complexity_check_default_true(self):
        """Complexity check should be enabled by default."""
        from symbo_agentic_reasoners.core.safe_parser import (
            safe_sympify, ExpressionComplexityError
        )
        # Deep nesting triggers quadratic penalty: 35^2 = 1225 > 1000
        complex_expr = "(" * 35 + "x" + ")" * 35
        with pytest.raises(ExpressionComplexityError):
            safe_sympify(complex_expr)

    def test_complexity_check_disabled(self):
        """Complexity check should be disableable."""
        from symbo_agentic_reasoners.core.safe_parser import safe_sympify
        # This would fail complexity check but we disable it
        # Note: it may still fail parsing, but not complexity
        try:
            safe_sympify("x**y**z", check_complexity=False)
        except Exception as e:
            # Should not be ExpressionComplexityError
            from symbo_agentic_reasoners.core.safe_parser import ExpressionComplexityError
            assert not isinstance(e, ExpressionComplexityError)


class TestSafeParseTimeout:
    """Tests for safe_parse timeout handling."""

    def test_timeout_parameter_accepted(self):
        """safe_parse should accept timeout parameter."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse
        result = safe_parse("x + y", timeout=2.0)
        assert result is not None

    def test_complexity_check_parameter(self):
        """safe_parse should accept check_complexity parameter."""
        from symbo_agentic_reasoners.core.safe_parser import safe_parse
        result = safe_parse("x**y**z", check_complexity=False)
        # May or may not succeed, but should not raise ComplexityError


class TestRunWithTimeout:
    """Tests for the _run_with_timeout helper."""

    def test_fast_function_succeeds(self):
        """Fast function should complete within timeout."""
        from symbo_agentic_reasoners.core.safe_parser import _run_with_timeout
        result = _run_with_timeout(lambda: 42, timeout=1.0)
        assert result == 42

    def test_function_exception_propagated(self):
        """Exceptions from function should be propagated."""
        from symbo_agentic_reasoners.core.safe_parser import _run_with_timeout

        def raise_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            _run_with_timeout(raise_error, timeout=1.0)


class TestParseTimeoutError:
    """Tests for ParseTimeoutError exception."""

    def test_exception_inherits_security_error(self):
        """ParseTimeoutError should inherit from SecurityError."""
        from symbo_agentic_reasoners.core.safe_parser import (
            ParseTimeoutError, SecurityError
        )
        assert issubclass(ParseTimeoutError, SecurityError)

    def test_exception_message_includes_timeout(self):
        """Exception message should include timeout info."""
        from symbo_agentic_reasoners.core.safe_parser import ParseTimeoutError
        try:
            raise ParseTimeoutError("Operation timed out (timeout: 5.0s)")
        except ParseTimeoutError as e:
            assert "timeout" in str(e).lower()


class TestComplexityPatterns:
    """Tests for complexity pattern weights."""

    def test_matrix_operations_moderate(self):
        """Matrix operations should have moderate complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        score = _estimate_complexity("Matrix[[1,2],[3,4]]")
        assert 10 <= score < 100

    def test_solve_moderate_complexity(self):
        """Solve operations should have moderate complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        score = _estimate_complexity("solve(x**2 - 4, x)")
        assert score > 20

    def test_sum_product_high_complexity(self):
        """Sum/Product operations should have high complexity."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        score = _estimate_complexity("Sum(x**n, (n, 1, 100))")
        assert score > 25

    def test_multiple_patterns_additive(self):
        """Multiple complexity patterns should be additive."""
        from symbo_agentic_reasoners.core.safe_parser import _estimate_complexity
        single = _estimate_complexity("integrate(x)")
        double = _estimate_complexity("integrate(integrate(x))")
        assert double > single * 1.5


class TestModuleConstants:
    """Tests for module constants."""

    def test_min_timeout_positive(self):
        """MIN_TIMEOUT_SECONDS should be positive."""
        from symbo_agentic_reasoners.core.safe_parser import MIN_TIMEOUT_SECONDS
        assert MIN_TIMEOUT_SECONDS > 0

    def test_max_timeout_reasonable(self):
        """MAX_TIMEOUT_SECONDS should be reasonable (not too long)."""
        from symbo_agentic_reasoners.core.safe_parser import MAX_TIMEOUT_SECONDS
        assert MAX_TIMEOUT_SECONDS <= 300  # 5 minutes max

    def test_max_complexity_positive(self):
        """MAX_COMPLEXITY_SCORE should be positive."""
        from symbo_agentic_reasoners.core.safe_parser import MAX_COMPLEXITY_SCORE
        assert MAX_COMPLEXITY_SCORE > 0

    def test_complexity_patterns_exist(self):
        """COMPLEXITY_PATTERNS should have entries."""
        from symbo_agentic_reasoners.core.safe_parser import COMPLEXITY_PATTERNS
        assert len(COMPLEXITY_PATTERNS) > 0
        for pattern, weight in COMPLEXITY_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(weight, int)
            assert weight > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
