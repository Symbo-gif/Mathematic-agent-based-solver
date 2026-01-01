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
Agent Authentication Security Tests
===================================

Phase 5 - Issue #4: Agent Authentication System Tests

Tests HMAC-based agent identity verification to prevent spoofing attacks.

Test Categories:
1. Token generation and verification
2. Timestamp freshness validation
3. Constant-time comparison (timing attack prevention)
4. Credential lifecycle (issue, verify, revoke)
5. AMS integration
6. Directory Facilitator integration
7. Attack simulation (invalid tokens, expired timestamps, spoofing)
"""

import pytest
import time
import hmac
import hashlib
from unittest.mock import Mock, patch

from symbo_agentic_reasoners.infrastructure.security.agent_auth import (
    AgentAuthenticator, AgentCredential
)
from symbo_agentic_reasoners.infrastructure.ams import (
    AgentManagementSystem, AgentType
)
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, ServiceRegistration
)


class TestAgentAuthenticator:
    """Test AgentAuthenticator class."""

    def test_authenticator_initialization(self):
        """Test authenticator initializes correctly."""
        auth = AgentAuthenticator()
        assert auth.enable_auth is True
        assert auth.credentials_issued == 0
        assert auth.credentials_verified == 0

    def test_authenticator_disabled_mode(self):
        """Test authenticator can be disabled (warn-only)."""
        auth = AgentAuthenticator(enable_auth=False)
        assert auth.enable_auth is False

        # Should always return True when disabled
        assert auth.verify_credential('agent_001', 'invalid_token', int(time.time()))

    def test_issue_credential(self):
        """Test credential issuance."""
        auth = AgentAuthenticator()
        credential = auth.issue_credential('agent_001')

        assert credential.agent_id == 'agent_001'
        assert len(credential.token) == 64  # SHA256 hex digest
        assert credential.timestamp > 0
        assert credential.issued_at is not None
        assert auth.credentials_issued == 1

    def test_verify_valid_credential(self):
        """Test verifying a valid credential."""
        auth = AgentAuthenticator()
        credential = auth.issue_credential('agent_001')

        is_valid = auth.verify_credential(
            'agent_001',
            credential.token,
            credential.timestamp
        )

        assert is_valid is True
        assert auth.credentials_verified == 1

    def test_verify_invalid_token(self):
        """Test verifying an invalid token fails."""
        auth = AgentAuthenticator()
        credential = auth.issue_credential('agent_001')

        # Use wrong token
        is_valid = auth.verify_credential(
            'agent_001',
            'invalid_token_' + credential.token[:32],
            credential.timestamp
        )

        assert is_valid is False
        assert auth.credentials_failed == 1

    def test_verify_expired_timestamp(self):
        """Test expired credentials are rejected."""
        auth = AgentAuthenticator()

        # Create credential with old timestamp (6 minutes ago)
        old_timestamp = int(time.time()) - 360
        credential = auth.issue_credential('agent_001')

        # Manually set old timestamp
        old_token = auth._generate_token('agent_001', old_timestamp)

        is_valid = auth.verify_credential('agent_001', old_token, old_timestamp)

        assert is_valid is False
        assert auth.credentials_failed == 1

    def test_verify_future_timestamp(self):
        """Test future timestamps are rejected."""
        auth = AgentAuthenticator()

        # Create credential with future timestamp (10 minutes ahead)
        future_timestamp = int(time.time()) + 600
        future_token = auth._generate_token('agent_001', future_timestamp)

        is_valid = auth.verify_credential('agent_001', future_token, future_timestamp)

        assert is_valid is False

    def test_verify_wrong_agent_id(self):
        """Test token for different agent fails."""
        auth = AgentAuthenticator()
        credential = auth.issue_credential('agent_001')

        # Try to use agent_001's token for agent_002
        is_valid = auth.verify_credential(
            'agent_002',
            credential.token,
            credential.timestamp
        )

        assert is_valid is False

    def test_revoke_credential(self):
        """Test credential revocation."""
        auth = AgentAuthenticator()
        credential = auth.issue_credential('agent_001')

        # Revoke
        revoked = auth.revoke_credential('agent_001')
        assert revoked is True
        assert auth.credentials_revoked == 1

        # Verify it's gone
        assert not auth.has_credential('agent_001')

    def test_revoke_nonexistent_credential(self):
        """Test revoking non-existent credential."""
        auth = AgentAuthenticator()

        revoked = auth.revoke_credential('agent_999')
        assert revoked is False

    def test_has_credential(self):
        """Test has_credential check."""
        auth = AgentAuthenticator()

        assert not auth.has_credential('agent_001')

        auth.issue_credential('agent_001')

        assert auth.has_credential('agent_001')

    def test_get_credential(self):
        """Test retrieving issued credential."""
        auth = AgentAuthenticator()
        credential = auth.issue_credential('agent_001')

        retrieved = auth.get_credential('agent_001')

        assert retrieved is not None
        assert retrieved.agent_id == 'agent_001'
        assert retrieved.token == credential.token

    def test_get_statistics(self):
        """Test statistics reporting."""
        auth = AgentAuthenticator()

        # Issue credentials
        auth.issue_credential('agent_001')
        auth.issue_credential('agent_002')

        # Verify one
        cred1 = auth.get_credential('agent_001')
        auth.verify_credential('agent_001', cred1.token, cred1.timestamp)

        # Fail verification
        auth.verify_credential('agent_002', 'invalid', int(time.time()))

        # Revoke one
        auth.revoke_credential('agent_001')

        stats = auth.get_statistics()

        assert stats['enabled'] is True
        assert stats['credentials_issued'] == 2
        assert stats['credentials_verified'] == 1
        assert stats['credentials_failed'] == 1
        assert stats['credentials_revoked'] == 1
        assert stats['active_credentials'] == 1  # Only agent_002 left

    def test_secret_key_rotation(self):
        """Test secret key rotation invalidates credentials."""
        auth = AgentAuthenticator()
        credential = auth.issue_credential('agent_001')

        # Rotate key
        auth.rotate_secret_key()

        # Old credential should no longer verify
        is_valid = auth.verify_credential(
            'agent_001',
            credential.token,
            credential.timestamp
        )

        assert is_valid is False
        assert not auth.has_credential('agent_001')

    def test_constant_time_comparison(self):
        """Test that comparison uses hmac.compare_digest."""
        auth = AgentAuthenticator()

        # Mock hmac.compare_digest to verify it's called
        with patch('hmac.compare_digest', return_value=True) as mock_compare:
            credential = auth.issue_credential('agent_001')
            auth.verify_credential('agent_001', credential.token, credential.timestamp)

            # Verify compare_digest was called
            assert mock_compare.called


class TestAMSAuthentication:
    """Test AMS integration with authentication."""

    def test_ams_has_authenticator(self):
        """Test AMS initializes with authenticator."""
        ams = AgentManagementSystem()
        assert hasattr(ams, 'authenticator')
        assert isinstance(ams.authenticator, AgentAuthenticator)

    def test_create_agent_without_auth(self):
        """Test agent creation without authentication (legacy mode)."""
        ams = AgentManagementSystem()

        # Should succeed without auth (backward compatible)
        success = ams.create_agent(
            agent_id='agent_001',
            agent_type=AgentType.INFRASTRUCTURAL
        )

        assert success is True

    def test_create_agent_with_valid_auth(self):
        """Test agent creation with valid authentication."""
        ams = AgentManagementSystem()

        # Issue credential
        credential = ams.issue_agent_credential('agent_001')

        # Create agent with authentication
        success = ams.create_agent(
            agent_id='agent_001',
            agent_type=AgentType.COGNITIVE,
            auth_token=credential.token,
            auth_timestamp=credential.timestamp
        )

        assert success is True

    def test_create_agent_with_invalid_auth(self):
        """Test agent creation fails with invalid authentication."""
        ams = AgentManagementSystem()

        # Try to create with invalid token
        success = ams.create_agent(
            agent_id='agent_001',
            agent_type=AgentType.COGNITIVE,
            auth_token='invalid_token_12345',
            auth_timestamp=int(time.time())
        )

        assert success is False

    def test_create_agent_with_expired_auth(self):
        """Test agent creation fails with expired credentials."""
        ams = AgentManagementSystem()

        # Create expired credential (10 minutes old)
        old_timestamp = int(time.time()) - 600
        old_token = ams.authenticator._generate_token('agent_001', old_timestamp)

        success = ams.create_agent(
            agent_id='agent_001',
            agent_type=AgentType.COGNITIVE,
            auth_token=old_token,
            auth_timestamp=old_timestamp
        )

        assert success is False

    def test_ams_statistics_include_auth(self):
        """Test AMS statistics include authentication metrics."""
        ams = AgentManagementSystem()

        # Issue and verify credentials
        cred = ams.issue_agent_credential('agent_001')
        ams.create_agent(
            'agent_001',
            AgentType.COGNITIVE,
            auth_token=cred.token,
            auth_timestamp=cred.timestamp
        )

        stats = ams.get_statistics()

        assert 'authentication' in stats
        assert stats['authentication']['credentials_issued'] >= 1


class TestDFAuthentication:
    """Test Directory Facilitator integration with authentication."""

    def test_df_has_authenticator(self):
        """Test DF initializes with authenticator."""
        df = DirectoryFacilitator()
        assert hasattr(df, 'authenticator')
        assert isinstance(df.authenticator, AgentAuthenticator)

    def test_register_service_without_auth(self):
        """Test service registration without authentication (legacy mode)."""
        df = DirectoryFacilitator()

        registration = ServiceRegistration(
            agent_id='agent_001',
            service_type='math.calculus',
            algorithm='symbolic',
            cost=1.0
        )

        # Should succeed without auth (backward compatible)
        success = df.register(registration)
        assert success is True

    def test_register_service_with_valid_auth(self):
        """Test service registration with valid authentication."""
        df = DirectoryFacilitator()

        # Issue credential
        credential = df.issue_agent_credential('agent_001')

        registration = ServiceRegistration(
            agent_id='agent_001',
            service_type='math.calculus',
            algorithm='symbolic',
            cost=1.0
        )

        # Register with authentication
        success = df.register(
            registration,
            auth_token=credential.token,
            auth_timestamp=credential.timestamp
        )

        assert success is True

    def test_register_service_with_invalid_auth(self):
        """Test service registration fails with invalid authentication."""
        df = DirectoryFacilitator()

        registration = ServiceRegistration(
            agent_id='agent_001',
            service_type='math.calculus',
            algorithm='symbolic',
            cost=1.0
        )

        # Try to register with invalid token
        success = df.register(
            registration,
            auth_token='invalid_token_12345',
            auth_timestamp=int(time.time())
        )

        assert success is False

    def test_df_statistics_include_auth(self):
        """Test DF statistics include authentication metrics."""
        df = DirectoryFacilitator()

        # Issue credential
        cred = df.issue_agent_credential('agent_001')

        stats = df.get_statistics()

        assert 'authentication' in stats
        assert stats['authentication']['credentials_issued'] >= 1


class TestAuthenticationAttackScenarios:
    """Test authentication prevents common attacks."""

    def test_prevents_token_replay(self):
        """Test that old tokens cannot be reused."""
        auth = AgentAuthenticator()

        # Issue credential
        cred1 = auth.issue_credential('agent_001')

        # Wait 1 second and issue new credential
        time.sleep(1)
        cred2 = auth.issue_credential('agent_001')

        # Old token should fail with new timestamp
        is_valid = auth.verify_credential(
            'agent_001',
            cred1.token,
            cred2.timestamp
        )

        assert is_valid is False

    def test_prevents_agent_spoofing(self):
        """Test that agents cannot spoof other agent identities."""
        auth = AgentAuthenticator()

        # Agent 001 gets credential
        cred_001 = auth.issue_credential('agent_001')

        # Agent 002 tries to use agent_001's token
        is_valid = auth.verify_credential(
            'agent_002',
            cred_001.token,
            cred_001.timestamp
        )

        assert is_valid is False

    def test_prevents_timestamp_manipulation(self):
        """Test that timestamp manipulation is detected."""
        auth = AgentAuthenticator()

        cred = auth.issue_credential('agent_001')

        # Try with manipulated timestamp
        fake_timestamp = cred.timestamp + 100

        is_valid = auth.verify_credential(
            'agent_001',
            cred.token,
            fake_timestamp
        )

        assert is_valid is False

    def test_token_forgery_prevention(self):
        """Test that forged tokens are rejected."""
        auth = AgentAuthenticator()

        # Try to forge a token
        current_time = int(time.time())
        forged_token = hmac.new(
            b'wrong_secret_key',
            f"agent_001:{current_time}".encode(),
            hashlib.sha256
        ).hexdigest()

        is_valid = auth.verify_credential('agent_001', forged_token, current_time)

        assert is_valid is False

    def test_ams_blocks_unauthenticated_agent(self):
        """Test AMS blocks agent with invalid authentication."""
        ams = AgentManagementSystem()

        # Try to create with invalid auth
        success = ams.create_agent(
            agent_id='malicious_agent',
            agent_type=AgentType.COGNITIVE,
            auth_token='forged_token',
            auth_timestamp=int(time.time())
        )

        assert success is False
        assert 'malicious_agent' not in ams._agents

    def test_df_blocks_unauthenticated_service(self):
        """Test DF blocks service registration with invalid authentication."""
        df = DirectoryFacilitator()

        registration = ServiceRegistration(
            agent_id='malicious_agent',
            service_type='math.calculus',
            algorithm='malicious',
            cost=0.0
        )

        # Try to register with invalid auth
        success = df.register(
            registration,
            auth_token='forged_token',
            auth_timestamp=int(time.time())
        )

        assert success is False
        assert 'math.calculus' not in df._services or \
               len(df._services.get('math.calculus', [])) == 0


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
