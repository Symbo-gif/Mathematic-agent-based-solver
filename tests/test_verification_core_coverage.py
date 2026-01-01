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
Tests for Verification Core Module
===================================

Comprehensive tests for the Phase 1 verification system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestLogicCheckerAgent:
    """Tests for LogicCheckerAgent class."""

    def test_init_default(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()
        assert agent.agent_id == 'logic_checker_001'
        assert agent.checks_performed == 0
        assert agent.violations_found == 0

    def test_init_custom_id(self):
        """Test custom agent ID initialization."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent(agent_id='custom_checker')
        assert agent.agent_id == 'custom_checker'

    def test_illegal_moves_constant(self):
        """Test ILLEGAL_MOVES constant exists and has expected values."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        assert 'division_by_zero' in LogicCheckerAgent.ILLEGAL_MOVES
        assert 'log_of_negative' in LogicCheckerAgent.ILLEGAL_MOVES
        assert 'sqrt_of_negative_real' in LogicCheckerAgent.ILLEGAL_MOVES
        assert 'undefined_limit' in LogicCheckerAgent.ILLEGAL_MOVES
        assert 'domain_violation' in LogicCheckerAgent.ILLEGAL_MOVES

    def test_check_valid_expression(self):
        """Test check with valid expression."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        is_valid, violations = agent.check('x**2 + 2*x + 1', {'operation': 'simplify'})

        assert is_valid is True
        assert violations == []
        assert agent.checks_performed == 1

    def test_check_expression_with_division(self):
        """Test check with expression containing division."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        # Division is allowed because _denominator_verified_nonzero returns True
        is_valid, violations = agent.check('1/x', {'operation': 'simplify'})

        assert is_valid is True  # Phase 1 is permissive
        assert agent.checks_performed == 1

    def test_check_expression_with_log(self):
        """Test check with log expression."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        # Log check is skipped in Phase 1
        is_valid, violations = agent.check('log(x)', {'operation': 'simplify'})

        assert is_valid is True
        assert agent.checks_performed == 1

    def test_check_expression_with_sqrt(self):
        """Test check with sqrt expression."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        # Sqrt check is skipped in Phase 1
        is_valid, violations = agent.check('sqrt(x)', {'operation': 'simplify'})

        assert is_valid is True

    def test_check_increments_counter(self):
        """Test that checks_performed counter increments."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        agent.check('x', {})
        agent.check('y', {})
        agent.check('z', {})

        assert agent.checks_performed == 3

    def test_has_division_true(self):
        """Test _has_division returns True for division."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        assert agent._has_division('1/x') is True
        assert agent._has_division('a/b + c/d') is True

    def test_has_division_false(self):
        """Test _has_division returns False when no division."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        assert agent._has_division('x**2') is False
        assert agent._has_division('x + y') is False

    def test_denominator_verified_nonzero(self):
        """Test _denominator_verified_nonzero returns True (Phase 1 permissive)."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()

        # Phase 1 is permissive - always returns True
        assert agent._denominator_verified_nonzero('1/x') is True
        assert agent._denominator_verified_nonzero('1/0') is True  # Still permissive

    def test_update_beliefs(self):
        """Test BDI update_beliefs method."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()
        # Should not raise
        agent.update_beliefs()

    def test_deliberate(self):
        """Test BDI deliberate method."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()
        intentions = agent.deliberate()
        assert intentions == []

    def test_execute_step(self):
        """Test BDI execute_step method."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        agent = LogicCheckerAgent()
        mock_intention = Mock()
        # Should not raise
        agent.execute_step(mock_intention)


class TestSimplifiedVerifierAgent:
    """Tests for SimplifiedVerifierAgent class."""

    def test_init_default(self):
        """Test default initialization without blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        assert agent.agent_id == 'simplified_verifier_001'
        assert agent.blackboard is None
        assert agent.logic_checker is not None
        assert agent.verifications_attempted == 0
        assert agent.verifications_succeeded == 0
        assert agent.verifications_failed == 0
        assert agent.subscription_id is None

    def test_init_custom_id(self):
        """Test custom agent ID initialization."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent(agent_id='custom_verifier')
        assert agent.agent_id == 'custom_verifier'

    def test_init_with_blackboard(self):
        """Test initialization with blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        assert agent.blackboard is mock_blackboard
        mock_blackboard.subscribe.assert_called_once()

    def test_subscribe_to_verification_requests_no_blackboard(self):
        """Test subscription when no blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()
        # Should not raise
        agent._subscribe_to_verification_requests()
        assert agent.subscription_id is None

    def test_subscribe_to_verification_requests_with_blackboard(self):
        """Test subscription with blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_456'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        assert agent.subscription_id == 'sub_456'
        mock_blackboard.subscribe.assert_called_with(
            agent_id=agent.agent_id,
            tags=['verification_needed'],
            callback=agent.on_candidate
        )

    def test_verify_result_derivative(self):
        """Test _verify_result for derivative operation."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        result = agent._verify_result('2*x', 'derivative', {})
        assert result is True

    def test_verify_result_integral(self):
        """Test _verify_result for integral operation."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        result = agent._verify_result('x**2/2', 'integral', {})
        assert result is True

    def test_verify_result_other_operation(self):
        """Test _verify_result for other operations."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        result = agent._verify_result('x + 1', 'simplify', {})
        assert result is True

    def test_verify_derivative_valid(self):
        """Test _verify_derivative with valid expression."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        result = agent._verify_derivative('2*x', {})
        assert result is True

    def test_verify_derivative_invalid(self):
        """Test _verify_derivative with invalid expression."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        # Unparseable expression
        result = agent._verify_derivative('((([[[', {})
        assert result is False

    def test_verify_integral_valid(self):
        """Test _verify_integral with valid expression."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        result = agent._verify_integral('x**2/2', {})
        assert result is True

    def test_verify_integral_invalid(self):
        """Test _verify_integral with invalid expression."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        # Unparseable expression
        result = agent._verify_integral('))))))', {})
        assert result is False

    def test_mark_as_verified_no_blackboard(self):
        """Test _mark_as_verified without blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()
        mock_entry = Mock()

        # Should not raise
        agent._mark_as_verified(mock_entry)

    def test_mark_as_verified_with_blackboard(self):
        """Test _mark_as_verified with blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryStatus
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        mock_entry = Mock()
        mock_entry.entry_id = 'test_entry_001'
        mock_entry.metadata = {}

        agent._mark_as_verified(mock_entry)

        assert mock_entry.status == EntryStatus.VERIFIED
        assert mock_entry.metadata['verified_by'] == agent.agent_id
        assert mock_entry.metadata['verification_status'] == 'VERIFIED'
        mock_blackboard.update_entry_status.assert_called_with(
            'test_entry_001', EntryStatus.VERIFIED
        )

    def test_mark_as_failed_no_blackboard(self):
        """Test _mark_as_failed without blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()
        mock_entry = Mock()

        # Should not raise
        agent._mark_as_failed(mock_entry, 'test reason')

    def test_mark_as_failed_with_blackboard_no_parent(self):
        """Test _mark_as_failed with blackboard but no parent entry."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryStatus
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        mock_entry = Mock()
        mock_entry.entry_id = 'test_entry_001'
        mock_entry.metadata = {}

        agent._mark_as_failed(mock_entry, 'verification failed')

        assert mock_entry.status == EntryStatus.FAILED
        assert mock_entry.metadata['verification_status'] == 'FAILED'
        assert mock_entry.metadata['verification_error'] == 'verification failed'

    def test_mark_as_failed_with_parent_entry(self):
        """Test _mark_as_failed with parent entry posts error flag."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryStatus
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        mock_entry = Mock()
        mock_entry.entry_id = 'test_entry_001'
        mock_entry.content = 'test content'
        mock_entry.conversation_id = 'conv_001'
        mock_entry.metadata = {'parent_entry': 'parent_001'}

        agent._mark_as_failed(mock_entry, 'verification failed')

        # Should post error flag to blackboard
        mock_blackboard.post.assert_called_once()

    def test_on_candidate_wrong_entry_type(self):
        """Test on_candidate ignores wrong entry type."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        agent = SimplifiedVerifierAgent()

        mock_entry = Mock()
        mock_entry.entry_type = EntryType.TASK  # Not PARTIAL_RESULT
        mock_entry.status = EntryStatus.PENDING

        agent.on_candidate(mock_entry)

        assert agent.verifications_attempted == 0

    def test_on_candidate_wrong_status(self):
        """Test on_candidate ignores wrong status."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        agent = SimplifiedVerifierAgent()

        mock_entry = Mock()
        mock_entry.entry_type = EntryType.PARTIAL_RESULT
        mock_entry.status = EntryStatus.VERIFIED  # Not PENDING

        agent.on_candidate(mock_entry)

        assert agent.verifications_attempted == 0

    def test_on_candidate_successful_verification(self):
        """Test on_candidate with successful verification."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        mock_entry = Mock()
        mock_entry.entry_type = EntryType.PARTIAL_RESULT
        mock_entry.status = EntryStatus.PENDING
        mock_entry.entry_id = 'entry_001'
        mock_entry.metadata = {
            'result_str': '2*x',
            'operation': 'derivative',
            'parent_entry': None
        }

        agent.on_candidate(mock_entry)

        assert agent.verifications_attempted == 1
        assert agent.verifications_succeeded == 1
        assert agent.verifications_failed == 0

    def test_on_candidate_failed_logic_check(self):
        """Test on_candidate with failed logic check."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        # Mock logic checker to fail
        agent.logic_checker.check = Mock(return_value=(False, ['division_by_zero']))

        mock_entry = Mock()
        mock_entry.entry_type = EntryType.PARTIAL_RESULT
        mock_entry.status = EntryStatus.PENDING
        mock_entry.entry_id = 'entry_001'
        mock_entry.metadata = {
            'result_str': '1/0',
            'operation': 'simplify'
        }

        agent.on_candidate(mock_entry)

        assert agent.verifications_attempted == 1
        assert agent.verifications_failed == 1

    def test_on_candidate_failed_verification(self):
        """Test on_candidate with failed computational verification."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        # Mock _verify_result to fail
        agent._verify_result = Mock(return_value=False)

        mock_entry = Mock()
        mock_entry.entry_type = EntryType.PARTIAL_RESULT
        mock_entry.status = EntryStatus.PENDING
        mock_entry.entry_id = 'entry_001'
        mock_entry.metadata = {
            'result_str': 'invalid',
            'operation': 'derivative'
        }

        agent.on_candidate(mock_entry)

        assert agent.verifications_failed == 1

    def test_on_candidate_exception_handling(self):
        """Test on_candidate handles exceptions gracefully."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        agent = SimplifiedVerifierAgent(blackboard=mock_blackboard)

        mock_entry = Mock()
        mock_entry.entry_type = EntryType.PARTIAL_RESULT
        mock_entry.status = EntryStatus.PENDING
        mock_entry.entry_id = 'entry_001'
        # Use a real dict to allow item assignment
        mock_entry.metadata = {
            'result_str': '(((invalid)))',  # Will be parsed but then fail verification
            'operation': 'derivative'
        }

        # Patch _verify_result to raise an exception
        with patch.object(agent, '_verify_result', side_effect=ValueError("Test error")):
            agent.on_candidate(mock_entry)

        assert agent.verifications_failed == 1

    def test_update_beliefs(self):
        """Test BDI update_beliefs method."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()
        # Should not raise
        agent.update_beliefs()

    def test_deliberate(self):
        """Test BDI deliberate method."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()
        intentions = agent.deliberate()
        assert intentions == []

    def test_execute_step(self):
        """Test BDI execute_step method."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()
        mock_intention = Mock()
        # Should not raise
        agent.execute_step(mock_intention)

    def test_get_statistics(self):
        """Test get_statistics method."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        # Simulate some work
        agent.verifications_attempted = 10
        agent.verifications_succeeded = 8
        agent.verifications_failed = 2

        stats = agent.get_statistics()

        assert stats['verifications_attempted'] == 10
        assert stats['verifications_succeeded'] == 8
        assert stats['verifications_failed'] == 2
        assert stats['success_rate'] == 80.0
        assert 'logic_checker' in stats

    def test_get_statistics_zero_attempts(self):
        """Test get_statistics with zero attempts."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        agent = SimplifiedVerifierAgent()

        stats = agent.get_statistics()

        assert stats['success_rate'] == 0


class TestVerificationCore:
    """Tests for VerificationCore class."""

    def test_init_no_blackboard(self):
        """Test initialization without blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import VerificationCore
        core = VerificationCore()

        assert core.verifier is not None
        assert core.verifier.blackboard is None
        assert core.verifier.logic_checker is not None

    def test_init_with_blackboard(self):
        """Test initialization with blackboard."""
        from symbo_agentic_reasoners.verification.verification_core import VerificationCore
        mock_blackboard = Mock()
        mock_blackboard.subscribe.return_value = 'sub_123'

        core = VerificationCore(blackboard=mock_blackboard)

        assert core.verifier.blackboard is mock_blackboard

    def test_verifier_has_logic_checker(self):
        """Test that VerificationCore's verifier has a logic checker."""
        from symbo_agentic_reasoners.verification.verification_core import VerificationCore
        core = VerificationCore()

        assert core.verifier.logic_checker is not None
        assert hasattr(core.verifier.logic_checker, 'check')


class TestModuleFunctions:
    """Tests for module-level functions and imports."""

    def test_module_imports(self):
        """Test that module imports correctly."""
        from symbo_agentic_reasoners.verification import verification_core
        assert verification_core is not None

    def test_logic_checker_agent_export(self):
        """Test LogicCheckerAgent is accessible."""
        from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent
        assert LogicCheckerAgent is not None

    def test_simplified_verifier_agent_export(self):
        """Test SimplifiedVerifierAgent is accessible."""
        from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent
        assert SimplifiedVerifierAgent is not None

    def test_verification_core_export(self):
        """Test VerificationCore is accessible."""
        from symbo_agentic_reasoners.verification.verification_core import VerificationCore
        assert VerificationCore is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
