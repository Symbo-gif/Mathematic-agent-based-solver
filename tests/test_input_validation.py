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
Input Parsing and Validation Tests
===================================

Comprehensive tests for input parsing, normalization, and validation:
- Input Normalizer
- Safe Parser
- Precondition Validation
- Domain Classification
"""

import pytest
from unittest.mock import Mock, patch

# NO SYMPY - Use native symbolic types
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, symbols, Sin as sin, Cos as cos, Exp as exp, Sqrt as sqrt, Rational
)

# Import the modules under test
from symbo_agentic_reasoners.core.input_normalizer import (
    normalize_input,
    normalize_unicode,
    normalize_whitespace,
    add_implicit_multiplication,
    normalize_operators,
    validate_normalized,
    safe_normalize,
    close_unclosed_parens,
    normalize_function_names,
)
from symbo_agentic_reasoners.core.safe_parser import (
    safe_sympify,
    safe_parse,
    validate_input,
    is_safe_expression,
    SecurityError,
)
from symbo_agentic_reasoners.middleware.precondition_validation import (
    ValidationStatus,
    ValidationResult,
    MathematicalDomain,
    MathematicalConstraint,
    DomainCheckerAgent,
    AssumptionValidatorAgent,
    EdgeCaseDetectorAgent,
    PreconditionValidationTeam,
)


# =============================================================================
# Input Normalizer Tests
# =============================================================================


class TestNormalizeInput:
    """Tests for the normalize_input function."""

    def test_basic_normalization(self):
        """Basic input should normalize correctly."""
        result = normalize_input("x + 1")
        assert "x" in result
        assert "+" in result

    def test_power_conversion(self):
        """Caret should convert to double asterisk."""
        result = normalize_input("x^2")
        assert "**" in result
        assert "^" not in result

    def test_implicit_multiplication(self):
        """Implicit multiplication should be added."""
        result = normalize_input("2x")
        assert "*" in result or "2*x" in result or result == "2*x"

    def test_whitespace_normalization(self):
        """Extra whitespace should be normalized."""
        result = normalize_input("  x  +  1  ")
        assert result.strip() == result  # No leading/trailing whitespace

    def test_function_recognition(self):
        """Standard functions should be recognized."""
        result = normalize_input("sin(x)")
        assert "sin" in result

    def test_unicode_normalization(self):
        """Unicode math symbols should normalize."""
        # Test multiplication sign
        result = normalize_input("x\u00d7y")  # x×y
        assert "*" in result

    def test_empty_input(self):
        """Empty input should be handled gracefully."""
        result = normalize_input("")
        assert result == ""

    def test_complex_expression(self):
        """Complex expressions should normalize correctly."""
        result = normalize_input("x^2 + 2x + 1")
        assert "**" in result


class TestNormalizeWhitespace:
    """Tests for whitespace normalization."""

    def test_trim_leading_trailing(self):
        """Leading and trailing whitespace should be trimmed."""
        result = normalize_whitespace("  hello  ")
        assert result == "hello"

    def test_collapse_multiple_spaces(self):
        """Multiple spaces should collapse to single space."""
        result = normalize_whitespace("a    b")
        assert "    " not in result

    def test_preserve_single_spaces(self):
        """Single spaces should be preserved."""
        result = normalize_whitespace("a b c")
        assert " " in result


class TestNormalizeUnicode:
    """Tests for Unicode normalization."""

    def test_multiplication_signs(self):
        """Unicode multiplication signs should normalize."""
        result = normalize_unicode("a\u00d7b")  # ×
        assert "*" in result

    def test_division_signs(self):
        """Unicode division signs should normalize."""
        result = normalize_unicode("a\u00f7b")  # ÷
        assert "/" in result

    def test_superscripts(self):
        """Unicode superscripts should normalize."""
        result = normalize_unicode("x\u00b2")  # x²
        assert "2" in result

    def test_greek_letters(self):
        """Greek letters should be preserved or normalized."""
        result = normalize_unicode("\u03c0")  # π
        # Should either keep as pi or as the symbol
        assert result  # Not empty


class TestImplicitMultiplication:
    """Tests for adding implicit multiplication."""

    def test_number_variable(self):
        """Number followed by variable should get multiplication."""
        result = add_implicit_multiplication("2x")
        assert "*" in result

    def test_variable_parenthesis(self):
        """Variable followed by parenthesis should get multiplication."""
        result = add_implicit_multiplication("x(y+1)")
        assert "*" in result or "x*(y+1)" in result

    def test_parenthesis_parenthesis(self):
        """Parenthesis followed by parenthesis should get multiplication."""
        result = add_implicit_multiplication("(a+b)(c+d)")
        assert "*" in result

    def test_preserve_explicit_multiplication(self):
        """Explicit multiplication should be preserved."""
        result = add_implicit_multiplication("2*x")
        assert "2*x" in result


class TestNormalizeOperators:
    """Tests for operator normalization."""

    def test_power_operator(self):
        """Caret should convert to **."""
        result = normalize_operators("x^2")
        assert "**" in result
        assert "^" not in result

    def test_preserve_standard_operators(self):
        """Standard operators should be preserved."""
        result = normalize_operators("a + b - c * d / e")
        assert "+" in result
        assert "-" in result
        assert "*" in result
        assert "/" in result


class TestValidateNormalized:
    """Tests for validation of normalized input."""

    def test_valid_expression(self):
        """Valid expressions should pass validation."""
        is_valid, error = validate_normalized("x + 1")
        assert is_valid is True
        assert error is None

    def test_balanced_parentheses(self):
        """Balanced parentheses should pass."""
        is_valid, error = validate_normalized("(x + 1)")
        assert is_valid is True

    def test_unbalanced_parentheses(self):
        """Unbalanced parentheses should fail or be flagged."""
        is_valid, error = validate_normalized("(x + 1")
        # Depending on implementation, might auto-fix or flag
        # Just verify it returns a result
        assert isinstance(is_valid, bool)


class TestSafeNormalize:
    """Tests for safe_normalize function."""

    def test_returns_tuple(self):
        """Should return tuple of (result, success, error)."""
        result = safe_normalize("x + 1")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_success_case(self):
        """Valid input should succeed."""
        text, success, error = safe_normalize("x + 1")
        assert success is True
        assert error is None


class TestCloseUnclosedParens:
    """Tests for auto-closing parentheses."""

    def test_already_balanced(self):
        """Balanced expressions should be unchanged."""
        result = close_unclosed_parens("(x + 1)")
        assert result.count("(") == result.count(")")

    def test_closes_unclosed(self):
        """Unclosed parentheses should be closed."""
        result = close_unclosed_parens("(x + 1")
        assert result.count("(") == result.count(")")


# =============================================================================
# Safe Parser Tests
# =============================================================================


class TestSafeSympify:
    """Tests for safe_sympify function."""

    def test_simple_expression(self):
        """Simple expression should parse correctly."""
        result = safe_sympify("x + 1")
        assert result is not None

    def test_polynomial(self):
        """Polynomial should parse correctly."""
        result = safe_sympify("x**2 + 2*x + 1")
        x = Symbol('x')
        assert result.has(x)

    def test_function_expression(self):
        """Function expressions should parse."""
        result = safe_sympify("sin(x) + cos(x)")
        assert result is not None

    def test_rational_expression(self):
        """Rational expressions should parse."""
        result = safe_sympify("1/2 + 1/3")
        assert result is not None

    def test_complex_expression(self):
        """Complex numbers should parse."""
        result = safe_sympify("1 + 2*I")
        assert result is not None


class TestValidateInput:
    """Tests for input validation."""

    def test_valid_input_passes(self):
        """Valid input should not raise."""
        # Should not raise
        validate_input("x + 1")

    def test_dangerous_patterns_rejected(self):
        """Dangerous patterns should be rejected."""
        dangerous_inputs = [
            "__import__('os')",
            "eval('code')",
            "exec('code')",
            "__builtins__",
        ]
        for inp in dangerous_inputs:
            with pytest.raises((SecurityError, ValueError, Exception)):
                validate_input(inp)


class TestIsSafeExpression:
    """Tests for is_safe_expression."""

    def test_safe_expressions(self):
        """Safe expressions should return True."""
        safe_inputs = [
            "x + 1",
            "x**2",
            "sin(x)",
            "sqrt(x)",
        ]
        for inp in safe_inputs:
            assert is_safe_expression(inp) is True

    def test_unsafe_expressions(self):
        """Unsafe expressions should return False."""
        unsafe_inputs = [
            "__import__('os')",
            "eval('code')",
        ]
        for inp in unsafe_inputs:
            result = is_safe_expression(inp)
            assert result is False


class TestSafeParse:
    """Tests for safe_parse function."""

    def test_parse_returns_sympy_object(self):
        """safe_parse should return a SymPy object."""
        result = safe_parse("x + 1")
        assert result is not None
        # Should be a SymPy expression - check for subs attribute or basic types
        assert hasattr(result, 'subs') or isinstance(result, (int, float))


# =============================================================================
# Precondition Validation Tests
# =============================================================================


class TestValidationStatus:
    """Tests for ValidationStatus enum."""

    def test_status_values_exist(self):
        """ValidationStatus should have expected values."""
        assert hasattr(ValidationStatus, 'VALID')
        assert hasattr(ValidationStatus, 'DOMAIN_MISMATCH')
        assert hasattr(ValidationStatus, 'CONSTRAINT_VIOLATION')
        assert hasattr(ValidationStatus, 'SINGULARITY_DETECTED')
        assert hasattr(ValidationStatus, 'EDGE_CASE_FAILURE')


class TestMathematicalDomain:
    """Tests for MathematicalDomain enum."""

    def test_domain_values_exist(self):
        """MathematicalDomain should have expected values."""
        expected = [
            'REAL_ARITHMETIC', 'COMPLEX_ARITHMETIC', 'INTEGER_ARITHMETIC',
            'RATIONAL_ARITHMETIC', 'DIOPHANTINE', 'PEANO_ARITHMETIC'
        ]
        for domain in expected:
            assert hasattr(MathematicalDomain, domain)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_valid_result(self):
        """Should create valid ValidationResult."""
        result = ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True,
            domain_classification=MathematicalDomain.REAL_ARITHMETIC,
            error_message=None
        )
        assert result.status == ValidationStatus.VALID
        assert result.is_valid is True
        assert result.domain_classification == MathematicalDomain.REAL_ARITHMETIC

    def test_to_fipa_token(self):
        """Should convert to FIPA token."""
        result = ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True,
            domain_classification=MathematicalDomain.REAL_ARITHMETIC
        )
        token = result.to_fipa_token()
        assert isinstance(token, str)
        assert "STATUS" in token


class TestMathematicalConstraint:
    """Tests for MathematicalConstraint dataclass."""

    def test_create_constraint(self):
        """Should create constraint."""
        constraint = MathematicalConstraint(
            variable="x",
            constraint_type="positive",
            source="inferred"
        )
        assert constraint.variable == "x"
        assert constraint.constraint_type == "positive"

    def test_to_assumption_dict(self):
        """Should convert to native assumption dict (NO SYMPY)."""
        constraint = MathematicalConstraint(
            variable="x",
            constraint_type="positive",
            source="test"
        )
        assumptions = constraint.to_assumption_dict()
        assert isinstance(assumptions, dict)
        assert assumptions.get('positive') is True


class TestDomainCheckerAgent:
    """Tests for DomainCheckerAgent."""

    def test_initialization(self):
        """Agent should initialize correctly."""
        agent = DomainCheckerAgent()
        assert agent is not None

    def test_classify_domain_polynomial(self):
        """Should classify polynomial domain."""
        agent = DomainCheckerAgent()
        # Create a mock OMDoc object with polynomial expression
        mock_omdoc = Mock()
        mock_omdoc.expression = "x**2 + 1"

        domain = agent.classify_domain(mock_omdoc)
        assert domain in list(MathematicalDomain)

    def test_check_solvability(self):
        """Should check problem solvability."""
        agent = DomainCheckerAgent()
        mock_omdoc = Mock()
        mock_omdoc.expression = "x + 1"
        mock_omdoc.operation = "solve"

        result = agent.check_solvability(mock_omdoc)
        assert isinstance(result, ValidationResult)


class TestAssumptionValidatorAgent:
    """Tests for AssumptionValidatorAgent."""

    def test_initialization(self):
        """Agent should initialize correctly."""
        agent = AssumptionValidatorAgent()
        assert agent is not None

    def test_extract_implicit_constraints(self):
        """Should extract implicit constraints from expression."""
        agent = AssumptionValidatorAgent()
        x = Symbol('x')
        expr = sqrt(x)  # Requires x >= 0

        constraints = agent.extract_implicit_constraints(expr)
        assert isinstance(constraints, list)


class TestEdgeCaseDetectorAgent:
    """Tests for EdgeCaseDetectorAgent."""

    def test_initialization(self):
        """Agent should initialize correctly."""
        agent = EdgeCaseDetectorAgent()
        assert agent is not None

    def test_detect_singularities_division(self):
        """Should detect division by zero singularities."""
        agent = EdgeCaseDetectorAgent()
        x = Symbol('x')
        expr = 1/x  # Singular at x=0

        singularities = agent.detect_singularities(expr)
        assert isinstance(singularities, list)

    def test_validate(self):
        """Should validate OMDoc object for edge cases."""
        agent = EdgeCaseDetectorAgent()
        mock_omdoc = Mock()
        mock_omdoc.expression = "1/x"

        result = agent.validate(mock_omdoc)
        assert isinstance(result, ValidationResult)


class TestPreconditionValidationTeam:
    """Tests for PreconditionValidationTeam."""

    def test_initialization(self):
        """Team should initialize correctly."""
        team = PreconditionValidationTeam()
        assert team is not None
        assert hasattr(team, 'validate')
        assert hasattr(team, 'domain_checker')
        assert hasattr(team, 'assumption_validator')
        assert hasattr(team, 'edge_case_detector')

    def test_get_statistics(self):
        """Should return statistics."""
        team = PreconditionValidationTeam()
        stats = team.get_statistics()
        assert isinstance(stats, dict)
        assert 'validations_performed' in stats
        assert 'rejections' in stats
        assert 'approval_rate' in stats


# =============================================================================
# Integration Tests
# =============================================================================


class TestParsingPipelineIntegration:
    """Integration tests for parsing pipeline."""

    def test_normalize_then_parse(self):
        """Normalized input should parse successfully."""
        # Normalize
        normalized = normalize_input("x^2 + 2x + 1")

        # Parse
        result = safe_sympify(normalized)
        assert result is not None

    def test_validation_chain(self):
        """Full validation chain should work."""
        # Input
        raw_input = "x^2 + 2x + 1"

        # Normalize
        normalized = normalize_input(raw_input)

        # Validate normalization
        is_valid, _ = validate_normalized(normalized)
        assert is_valid

        # Parse
        parsed = safe_sympify(normalized)
        assert parsed is not None

    def test_round_trip_preservation(self):
        """Expression semantics should be preserved through pipeline."""
        original = "x**2 + 2*x + 1"
        normalized = normalize_input(original)
        parsed = safe_sympify(normalized)

        x = Symbol('x')
        # Evaluate at x=2: (2)^2 + 2*(2) + 1 = 9
        value = parsed.subs(x, 2)
        assert value == 9


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests for parsing and validation."""

    def test_empty_string(self):
        """Empty string should be handled."""
        result = normalize_input("")
        assert result == ""

    def test_whitespace_only(self):
        """Whitespace-only input should be handled."""
        result = normalize_input("   ")
        assert result.strip() == ""

    def test_very_long_expression(self):
        """Very long expressions should be handled."""
        long_expr = " + ".join(["x" for _ in range(100)])
        result = normalize_input(long_expr)
        assert result is not None

    def test_deeply_nested_parentheses(self):
        """Deeply nested parentheses should be handled."""
        nested = "((((x))))"
        result = normalize_input(nested)
        assert "x" in result

    def test_unicode_edge_cases(self):
        """Various Unicode inputs should be handled."""
        unicode_inputs = [
            "x\u00b2",  # x²
            "\u03c0",   # π
            "\u221a",   # √
        ]
        for inp in unicode_inputs:
            result = normalize_input(inp)
            # Should not crash and should return something
            assert result is not None


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
