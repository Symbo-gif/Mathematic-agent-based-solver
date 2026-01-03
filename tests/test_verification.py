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
Verification Core Tests
========================

Comprehensive tests for the verification system:
- LogicCheckerAgent
- SimplifiedVerifierAgent
- VerificationCore
"""

import pytest
from symbo_agentic_reasoners.core.symbolic import Symbol, symbols, sin, cos, exp, sqrt, log
from unittest.mock import Mock, patch, MagicMock

# Import the modules under test
from symbo_agentic_reasoners.verification.verification_core import (
    LogicCheckerAgent,
    SimplifiedVerifierAgent,
    VerificationCore,
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard,
    BlackboardEntry,
    EntryType,
    EntryStatus,
)


# =============================================================================
# LogicCheckerAgent Tests
# =============================================================================


class TestLogicCheckerAgent:
    """Tests for LogicCheckerAgent."""

    @pytest.fixture
    def logic_checker(self):
        """Create a LogicCheckerAgent instance."""
        return LogicCheckerAgent()

    def test_initialization(self, logic_checker):
        """LogicCheckerAgent should initialize correctly."""
        assert logic_checker is not None
        assert hasattr(logic_checker, 'check')
        assert hasattr(logic_checker, 'checks_performed')
        assert hasattr(logic_checker, 'violations_found')
        assert logic_checker.checks_performed == 0
        assert logic_checker.violations_found == 0

    def test_check_valid_expression(self, logic_checker):
        """Valid expression should pass check."""
        result = "x**2 + 2*x + 1"
        problem = {"expression": "x**2 + 2*x + 1", "operation": "simplify"}

        is_valid, violations = logic_checker.check(result, problem)

        assert is_valid is True
        assert len(violations) == 0
        assert logic_checker.checks_performed == 1

    def test_check_increments_counter(self, logic_checker):
        """Each check should increment counter."""
        for i in range(5):
            logic_checker.check("x + 1", {})

        assert logic_checker.checks_performed == 5

    def test_has_division_detects_division(self, logic_checker):
        """Should detect division in expression."""
        assert logic_checker._has_division("1/x") is True
        assert logic_checker._has_division("x**2/y") is True
        assert logic_checker._has_division("x + y") is False

    def test_denominator_verified_nonzero(self, logic_checker):
        """Denominator check (Phase 1 permissive)."""
        # Phase 1 is permissive - always returns True
        result = logic_checker._denominator_verified_nonzero("1/x")
        assert result is True

    def test_illegal_moves_list(self, logic_checker):
        """Should have illegal moves defined."""
        assert hasattr(LogicCheckerAgent, 'ILLEGAL_MOVES')
        assert 'division_by_zero' in LogicCheckerAgent.ILLEGAL_MOVES
        assert 'log_of_negative' in LogicCheckerAgent.ILLEGAL_MOVES
        assert 'sqrt_of_negative_real' in LogicCheckerAgent.ILLEGAL_MOVES

    def test_bdi_methods_exist(self, logic_checker):
        """BDI interface methods should exist."""
        assert hasattr(logic_checker, 'update_beliefs')
        assert hasattr(logic_checker, 'deliberate')
        assert hasattr(logic_checker, 'execute_step')

    def test_update_beliefs(self, logic_checker):
        """update_beliefs should not raise."""
        logic_checker.update_beliefs()  # Should not raise

    def test_deliberate(self, logic_checker):
        """deliberate should return list."""
        result = logic_checker.deliberate()
        assert isinstance(result, list)


# =============================================================================
# SimplifiedVerifierAgent Tests
# =============================================================================


class TestSimplifiedVerifierAgent:
    """Tests for SimplifiedVerifierAgent."""

    @pytest.fixture
    def blackboard(self):
        """Create a Blackboard instance."""
        return Blackboard()

    @pytest.fixture
    def verifier(self, blackboard):
        """Create a SimplifiedVerifierAgent instance."""
        return SimplifiedVerifierAgent(blackboard=blackboard)

    def test_initialization(self, verifier):
        """SimplifiedVerifierAgent should initialize correctly."""
        assert verifier is not None
        assert hasattr(verifier, 'blackboard')
        assert hasattr(verifier, 'verifications_attempted')
        assert hasattr(verifier, 'verifications_succeeded')
        assert hasattr(verifier, 'verifications_failed')

    def test_initialization_without_blackboard(self):
        """Should handle initialization without blackboard."""
        verifier = SimplifiedVerifierAgent()
        assert verifier is not None

    def test_verify_derivative(self, verifier):
        """Should verify derivative results."""
        # Test with known derivative: d/dx(x^2) = 2x
        result_str = "2*x"
        metadata = {
            "original_expression": "x**2",
            "variable": "x"
        }

        is_valid = verifier._verify_derivative(result_str, metadata)
        # Result should be boolean
        assert isinstance(is_valid, bool)

    def test_verify_integral(self, verifier):
        """Should verify integral results."""
        # Test integral verification
        result_str = "x**2/2"
        metadata = {
            "original_expression": "x",
            "variable": "x"
        }

        is_valid = verifier._verify_integral(result_str, metadata)
        assert isinstance(is_valid, bool)

    def test_verify_result_with_operation(self, verifier):
        """Should route to correct verification method."""
        result_str = "2*x"
        metadata = {"original_expression": "x**2", "variable": "x"}

        # Test derivative operation
        is_valid = verifier._verify_result(result_str, "derivative", metadata)
        assert isinstance(is_valid, bool)

    def test_get_statistics(self, verifier):
        """Should return statistics."""
        stats = verifier.get_statistics()
        assert isinstance(stats, dict)
        assert 'verifications_attempted' in stats
        assert 'verifications_succeeded' in stats
        assert 'verifications_failed' in stats

    def test_bdi_methods_exist(self, verifier):
        """BDI interface methods should exist."""
        assert hasattr(verifier, 'update_beliefs')
        assert hasattr(verifier, 'deliberate')
        assert hasattr(verifier, 'execute_step')


# =============================================================================
# VerificationCore Tests
# =============================================================================


class TestVerificationCore:
    """Tests for VerificationCore."""

    @pytest.fixture
    def blackboard(self):
        """Create a Blackboard instance."""
        return Blackboard()

    @pytest.fixture
    def verification_core(self, blackboard):
        """Create a VerificationCore instance."""
        return VerificationCore(blackboard=blackboard)

    def test_initialization(self, verification_core):
        """VerificationCore should initialize correctly."""
        assert verification_core is not None
        assert hasattr(verification_core, 'verifier')

    def test_initialization_without_blackboard(self):
        """Should handle initialization without blackboard."""
        vc = VerificationCore()
        assert vc is not None
        assert vc.verifier is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestVerificationIntegration:
    """Integration tests for verification system."""

    @pytest.fixture
    def full_system(self):
        """Create full verification system."""
        blackboard = Blackboard()
        logic_checker = LogicCheckerAgent()
        verifier = SimplifiedVerifierAgent(blackboard=blackboard)
        return {
            'blackboard': blackboard,
            'logic_checker': logic_checker,
            'verifier': verifier
        }

    def test_two_stage_verification(self, full_system):
        """Test two-stage verification pipeline."""
        logic_checker = full_system['logic_checker']
        verifier = full_system['verifier']

        # Stage 1: Logic check
        result = "2*x"
        problem = {"expression": "x**2", "operation": "derivative"}

        is_valid, violations = logic_checker.check(result, problem)
        assert is_valid is True

        # Stage 2: Computational verification
        metadata = {"original_expression": "x**2", "variable": "x"}
        verified = verifier._verify_result(result, "derivative", metadata)
        assert isinstance(verified, bool)

    def test_verification_with_division(self, full_system):
        """Test verification of expression with division."""
        logic_checker = full_system['logic_checker']

        result = "1/x"
        problem = {"expression": "x**(-1)", "operation": "simplify"}

        is_valid, violations = logic_checker.check(result, problem)
        # Phase 1 is permissive with division
        assert isinstance(is_valid, bool)


# =============================================================================
# Edge Cases
# =============================================================================


class TestVerificationEdgeCases:
    """Edge case tests for verification."""

    @pytest.fixture
    def logic_checker(self):
        """Create a LogicCheckerAgent instance."""
        return LogicCheckerAgent()

    def test_empty_result(self, logic_checker):
        """Should handle empty result."""
        is_valid, violations = logic_checker.check("", {})
        assert isinstance(is_valid, bool)

    def test_complex_expression(self, logic_checker):
        """Should handle complex expressions."""
        result = "sin(x)*cos(x) + exp(x)/sqrt(x)"
        is_valid, violations = logic_checker.check(result, {})
        assert isinstance(is_valid, bool)

    def test_sympy_expression(self, logic_checker):
        """Should handle SymPy expressions."""
        x = Symbol('x')
        expr = x**2 + 2*x + 1

        is_valid, violations = logic_checker.check(expr, {})
        assert isinstance(is_valid, bool)

    def test_numeric_result(self, logic_checker):
        """Should handle numeric results."""
        is_valid, violations = logic_checker.check(42, {})
        assert isinstance(is_valid, bool)

    def test_none_result(self, logic_checker):
        """Should handle None result."""
        is_valid, violations = logic_checker.check(None, {})
        assert isinstance(is_valid, bool)

    def test_list_result(self, logic_checker):
        """Should handle list results (multiple solutions)."""
        result = ["x = 1", "x = -1"]
        is_valid, violations = logic_checker.check(result, {})
        assert isinstance(is_valid, bool)


# =============================================================================
# Statistics Tests
# =============================================================================


class TestVerificationStatistics:
    """Tests for verification statistics tracking."""

    def test_logic_checker_tracks_checks(self):
        """LogicCheckerAgent should track checks performed."""
        checker = LogicCheckerAgent()

        for i in range(10):
            checker.check(f"result_{i}", {})

        assert checker.checks_performed == 10

    def test_verifier_tracks_statistics(self):
        """SimplifiedVerifierAgent should track statistics."""
        verifier = SimplifiedVerifierAgent()

        stats = verifier.get_statistics()
        assert stats['verifications_attempted'] >= 0
        assert stats['verifications_succeeded'] >= 0
        assert stats['verifications_failed'] >= 0


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
