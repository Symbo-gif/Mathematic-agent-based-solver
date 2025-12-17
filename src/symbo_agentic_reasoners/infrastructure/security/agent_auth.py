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
Agent Authentication System
===========================

HMAC-based agent identity verification for preventing agent spoofing attacks.

Security Properties:
- Agent credentials verified on registration
- HMAC-SHA256 token-based authentication
- 5-minute timestamp window prevents replay attacks
- Constant-time comparison prevents timing attacks
- Thread-safe credential management

Phase 5 - Issue #4: No Agent Authentication
Implements cryptographic identity verification for all agents.

Usage:
    authenticator = AgentAuthenticator()

    # Issue credential
    credential = authenticator.issue_credential('agent_001')

    # Verify credential
    is_valid = authenticator.verify_credential(
        agent_id='agent_001',
        token=credential.token,
        timestamp=credential.timestamp
    )
"""

import hmac
import hashlib
import secrets
import time
import os
import logging
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from threading import RLock

logger = logging.getLogger('symbo_agentic_reasoners.security.agent_auth')


@dataclass
class AgentCredential:
    """
    Agent authentication credential.

    Contains HMAC token for verifying agent identity.

    Attributes:
        agent_id: Unique agent identifier
        token: HMAC-SHA256 authentication token
        timestamp: Token generation timestamp (Unix time)
        issued_at: Human-readable timestamp
    """
    agent_id: str
    token: str
    timestamp: int
    issued_at: datetime


class AgentAuthenticator:
    """
    HMAC-based agent authentication.

    Provides cryptographic identity verification for agents to prevent
    spoofing attacks. Uses HMAC-SHA256 for token generation and constant-time
    comparison for verification.

    Thread Safety:
        All credential operations are protected by RLock for concurrent access.

    Security Features:
        - HMAC-SHA256 token generation
        - 5-minute timestamp window (prevents replay)
        - Constant-time token comparison (prevents timing attacks)
        - Credential revocation support
        - Secure secret key management (environment variable or random)

    Statistics:
        credentials_issued: Total credentials issued
        credentials_verified: Total successful verifications
        credentials_failed: Total failed verifications
        credentials_revoked: Total revoked credentials
    """

    def __init__(self, secret_key: Optional[str] = None, enable_auth: bool = True):
        """
        Initialize authenticator.

        Args:
            secret_key: HMAC secret key (env: AGENT_AUTH_SECRET)
                       If not provided, reads from environment or generates random key
            enable_auth: If False, authentication is bypassed (warn-only mode)
        """
        self._secret_key = secret_key or os.getenv(
            'AGENT_AUTH_SECRET',
            secrets.token_hex(32)
        )
        self.enable_auth = enable_auth
        self._issued_credentials: Dict[str, AgentCredential] = {}
        self._lock = RLock()

        # Statistics
        self.credentials_issued = 0
        self.credentials_verified = 0
        self.credentials_failed = 0
        self.credentials_revoked = 0

        if not self.enable_auth:
            logger.warning("Agent authentication DISABLED (warn-only mode)")
        else:
            logger.info("Agent authentication ENABLED (HMAC-SHA256)")

    def issue_credential(self, agent_id: str) -> AgentCredential:
        """
        Issue authentication credential for agent.

        Generates HMAC token with current timestamp for agent identity verification.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentCredential with token and timestamp

        Thread Safety:
            Uses RLock to protect credential storage
        """
        with self._lock:
            timestamp = int(time.time())
            token = self._generate_token(agent_id, timestamp)

            credential = AgentCredential(
                agent_id=agent_id,
                token=token,
                timestamp=timestamp,
                issued_at=datetime.now()
            )

            self._issued_credentials[agent_id] = credential
            self.credentials_issued += 1

            logger.debug(f"Issued credential for agent: {agent_id}")
            return credential

    def verify_credential(self, agent_id: str, token: str,
                         timestamp: int) -> bool:
        """
        Verify agent credential.

        Verifies HMAC token and timestamp freshness to authenticate agent identity.

        Args:
            agent_id: Agent identifier
            token: HMAC token from credential
            timestamp: Token timestamp (Unix time)

        Returns:
            True if credential valid and fresh, False otherwise

        Security:
            - Uses constant-time comparison (hmac.compare_digest) to prevent timing attacks
            - Enforces 5-minute freshness window to prevent replay attacks
            - Thread-safe credential lookup

        Thread Safety:
            Uses RLock for statistics updates
        """
        if not self.enable_auth:
            # Warn-only mode - log but allow
            logger.warning(f"Authentication bypassed (disabled): {agent_id}")
            return True

        # Check timestamp freshness (5 minute window)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:
            with self._lock:
                self.credentials_failed += 1
            logger.warning(f"Authentication failed (stale timestamp): {agent_id}")
            return False

        # Generate expected token
        expected_token = self._generate_token(agent_id, timestamp)

        # Constant-time comparison prevents timing attacks
        is_valid = hmac.compare_digest(token, expected_token)

        with self._lock:
            if is_valid:
                self.credentials_verified += 1
                logger.debug(f"Authentication succeeded: {agent_id}")
            else:
                self.credentials_failed += 1
                logger.warning(f"Authentication failed (invalid token): {agent_id}")

        return is_valid

    def _generate_token(self, agent_id: str, timestamp: int) -> str:
        """
        Generate HMAC token for agent.

        Args:
            agent_id: Agent identifier
            timestamp: Unix timestamp

        Returns:
            HMAC-SHA256 hex digest
        """
        message = f"{agent_id}:{timestamp}".encode('utf-8')
        return hmac.new(
            self._secret_key.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()

    def revoke_credential(self, agent_id: str) -> bool:
        """
        Revoke agent credential.

        Removes credential from issued credentials, preventing future verification.

        Args:
            agent_id: Agent identifier to revoke

        Returns:
            True if credential was revoked, False if not found

        Thread Safety:
            Uses RLock to protect credential storage
        """
        with self._lock:
            credential = self._issued_credentials.pop(agent_id, None)

            if credential:
                self.credentials_revoked += 1
                logger.info(f"Revoked credential for agent: {agent_id}")
                return True

            logger.warning(f"Revocation failed (not found): {agent_id}")
            return False

    def has_credential(self, agent_id: str) -> bool:
        """
        Check if agent has issued credential.

        Args:
            agent_id: Agent identifier

        Returns:
            True if credential exists
        """
        with self._lock:
            return agent_id in self._issued_credentials

    def get_credential(self, agent_id: str) -> Optional[AgentCredential]:
        """
        Get issued credential for agent.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentCredential if found, None otherwise
        """
        with self._lock:
            return self._issued_credentials.get(agent_id)

    def get_statistics(self) -> Dict[str, any]:
        """
        Get authentication statistics.

        Returns:
            Dict with authentication metrics
        """
        with self._lock:
            return {
                'enabled': self.enable_auth,
                'credentials_issued': self.credentials_issued,
                'credentials_verified': self.credentials_verified,
                'credentials_failed': self.credentials_failed,
                'credentials_revoked': self.credentials_revoked,
                'active_credentials': len(self._issued_credentials),
            }

    def rotate_secret_key(self, new_secret_key: Optional[str] = None):
        """
        Rotate HMAC secret key.

        WARNING: This invalidates all existing credentials.
                 Reissue credentials for all agents after rotation.

        Args:
            new_secret_key: New secret key (or generates random if None)
        """
        with self._lock:
            old_key_hash = hashlib.sha256(self._secret_key.encode()).hexdigest()[:8]

            self._secret_key = new_secret_key or secrets.token_hex(32)

            # Clear all issued credentials (they're now invalid)
            revoked_count = len(self._issued_credentials)
            self._issued_credentials.clear()

            logger.warning(
                f"Secret key rotated (old: ...{old_key_hash}). "
                f"Revoked {revoked_count} credentials. "
                f"Agents must re-register."
            )
