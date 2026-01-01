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
Tests for Message HMAC Security
================================

Comprehensive tests for HMAC signing and verification in the message bus.
"""

import pytest
import time
import json
import copy


class TestAgentMessageSignature:
    """Tests for AgentMessage signature functionality."""

    def test_get_signable_data_deterministic(self):
        """Signable data should be deterministic for same message."""
        from symbo_agentic_reasoners.core.message_bus import (
            AgentMessage, MessageType
        )
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        data1 = msg.get_signable_data()
        data2 = msg.get_signable_data()
        assert data1 == data2

    def test_get_signable_data_different_for_different_messages(self):
        """Different messages should have different signable data."""
        from symbo_agentic_reasoners.core.message_bus import (
            AgentMessage, MessageType
        )
        msg1 = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test1'}
        )
        msg2 = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test2'}
        )
        assert msg1.get_signable_data() != msg2.get_signable_data()

    def test_signable_data_includes_sender(self):
        """Signable data should include sender_id."""
        from symbo_agentic_reasoners.core.message_bus import (
            AgentMessage, MessageType
        )
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        data = msg.get_signable_data()
        parsed = json.loads(data)
        assert parsed['sender_id'] == 'agent_1'

    def test_signable_data_includes_recipient(self):
        """Signable data should include recipient_id."""
        from symbo_agentic_reasoners.core.message_bus import (
            AgentMessage, MessageType
        )
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        data = msg.get_signable_data()
        parsed = json.loads(data)
        assert parsed['recipient_id'] == 'agent_2'

    def test_signature_field_default_none(self):
        """Signature should be None by default."""
        from symbo_agentic_reasoners.core.message_bus import (
            AgentMessage, MessageType
        )
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        assert msg.signature is None


class TestMessageBusHMAC:
    """Tests for MessageBus HMAC functionality."""

    def test_sign_message_returns_hex_string(self):
        """Sign message should return hex string."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        signature = bus._sign_message(msg)
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex = 64 chars

    def test_sign_message_deterministic(self):
        """Same message should produce same signature."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'},
            message_id='fixed_id',
            timestamp=1234567890.0
        )
        sig1 = bus._sign_message(msg)
        sig2 = bus._sign_message(msg)
        assert sig1 == sig2

    def test_different_keys_different_signatures(self):
        """Different keys should produce different signatures."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus1 = MessageBus(secret_key=b'key1')
        bus2 = MessageBus(secret_key=b'key2')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'},
            message_id='fixed_id',
            timestamp=1234567890.0
        )
        sig1 = bus1._sign_message(msg)
        sig2 = bus2._sign_message(msg)
        assert sig1 != sig2

    def test_verify_valid_signature(self):
        """Valid signature should verify."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        msg.signature = bus._sign_message(msg)
        assert bus._verify_message(msg) is True

    def test_verify_invalid_signature(self):
        """Invalid signature should not verify."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        msg.signature = 'invalid_signature'
        assert bus._verify_message(msg) is False

    def test_verify_missing_signature(self):
        """Missing signature should not verify."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        assert bus._verify_message(msg) is False

    def test_verify_tampered_content(self):
        """Tampered content should not verify."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        msg.signature = bus._sign_message(msg)
        # Tamper with content
        msg.content = {'task': 'tampered'}
        assert bus._verify_message(msg) is False

    def test_verify_tampered_sender(self):
        """Tampered sender should not verify."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        msg.signature = bus._sign_message(msg)
        # Tamper with sender
        msg.sender_id = 'malicious_agent'
        assert bus._verify_message(msg) is False


class TestReplayProtection:
    """Tests for replay attack protection."""

    def test_check_replay_new_message(self):
        """New message should not be detected as replay."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        assert bus._check_replay(msg) is False

    def test_check_replay_seen_message(self):
        """Seen message ID should be detected as replay."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'},
            message_id='duplicate_id'
        )
        # Record the message ID
        bus._seen_message_ids['duplicate_id'] = time.time()
        assert bus._check_replay(msg) is True

    def test_check_replay_old_timestamp(self):
        """Message with old timestamp should be detected as replay."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'},
            timestamp=time.time() - 600  # 10 minutes old
        )
        assert bus._check_replay(msg) is True

    def test_check_replay_recent_timestamp(self):
        """Message with recent timestamp should not be detected as replay."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'},
            timestamp=time.time() - 60  # 1 minute old
        )
        assert bus._check_replay(msg) is False


class TestSendMessageSigning:
    """Tests for automatic message signing on send."""

    def test_send_message_adds_signature(self):
        """send_message should add signature to message."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        bus.send_message(msg)
        assert msg.signature is not None
        assert len(msg.signature) == 64

    def test_send_message_signature_verifies(self):
        """Signature added by send_message should verify."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        bus.send_message(msg)
        assert bus._verify_message(msg) is True

    def test_send_message_updates_timestamp(self):
        """send_message should update timestamp."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        old_time = time.time() - 100
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'},
            timestamp=old_time
        )
        bus.send_message(msg)
        assert msg.timestamp > old_time


class TestProcessMessagesVerification:
    """Tests for message verification during processing."""

    def test_process_valid_message(self):
        """Valid message should be processed."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType, MessageStatus
        )
        bus = MessageBus(secret_key=b'test_key')
        received = []

        def handler(msg):
            received.append(msg)

        bus.register_handler('agent_2', handler)

        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        bus.send_message(msg)
        bus.process_messages()

        assert len(received) == 1
        assert msg.status == MessageStatus.COMPLETED

    def test_process_invalid_signature_rejected(self):
        """Message with invalid signature should be rejected."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType, MessageStatus
        )
        bus = MessageBus(secret_key=b'test_key')
        received = []

        def handler(msg):
            received.append(msg)

        bus.register_handler('agent_2', handler)

        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        bus.send_message(msg)
        # Tamper with signature
        msg.signature = 'invalid'

        bus.process_messages()

        assert len(received) == 0
        assert msg.status == MessageStatus.FAILED
        assert 'HMAC' in msg.metadata.get('error', '')

    def test_verification_disabled(self):
        """With verification disabled, unsigned messages should process."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType, MessageStatus
        )
        bus = MessageBus(secret_key=b'test_key', verify_signatures=False)
        received = []

        def handler(msg):
            received.append(msg)

        bus.register_handler('agent_2', handler)

        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        # Don't sign the message
        bus._message_store[msg.message_id] = msg
        bus._message_queue.append(msg)

        bus.process_messages()

        assert len(received) == 1


class TestPublicVerification:
    """Tests for public verification method."""

    def test_verify_message_integrity_valid(self):
        """verify_message_integrity should return True for valid message."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        bus.send_message(msg)
        assert bus.verify_message_integrity(msg) is True

    def test_verify_message_integrity_invalid(self):
        """verify_message_integrity should return False for invalid message."""
        from symbo_agentic_reasoners.core.message_bus import (
            MessageBus, AgentMessage, MessageType
        )
        bus = MessageBus(secret_key=b'test_key')
        msg = AgentMessage(
            sender_id='agent_1',
            recipient_id='agent_2',
            message_type=MessageType.REQUEST,
            content={'task': 'test'}
        )
        msg.signature = 'bad_signature'
        assert bus.verify_message_integrity(msg) is False


class TestEnvironmentKeyLoading:
    """Tests for environment-based key loading."""

    def test_default_key_used(self):
        """Default key should be used when no env var set."""
        from symbo_agentic_reasoners.core.message_bus import MessageBus
        import os
        # Ensure env var is not set
        env_key = os.environ.pop('SYMBO_MESSAGE_KEY', None)
        try:
            bus = MessageBus()
            assert bus._secret_key == MessageBus._DEFAULT_SECRET
        finally:
            if env_key:
                os.environ['SYMBO_MESSAGE_KEY'] = env_key

    def test_env_key_used(self):
        """Environment key should be used when set."""
        from symbo_agentic_reasoners.core.message_bus import MessageBus
        import os
        old_key = os.environ.get('SYMBO_MESSAGE_KEY')
        try:
            os.environ['SYMBO_MESSAGE_KEY'] = 'env_test_key'
            bus = MessageBus()
            assert bus._secret_key == b'env_test_key'
        finally:
            if old_key:
                os.environ['SYMBO_MESSAGE_KEY'] = old_key
            else:
                os.environ.pop('SYMBO_MESSAGE_KEY', None)

    def test_explicit_key_overrides_env(self):
        """Explicit key should override environment key."""
        from symbo_agentic_reasoners.core.message_bus import MessageBus
        import os
        old_key = os.environ.get('SYMBO_MESSAGE_KEY')
        try:
            os.environ['SYMBO_MESSAGE_KEY'] = 'env_key'
            bus = MessageBus(secret_key=b'explicit_key')
            assert bus._secret_key == b'explicit_key'
        finally:
            if old_key:
                os.environ['SYMBO_MESSAGE_KEY'] = old_key
            else:
                os.environ.pop('SYMBO_MESSAGE_KEY', None)


class TestMessageIntegrityError:
    """Tests for MessageIntegrityError exception."""

    def test_exception_can_be_raised(self):
        """MessageIntegrityError should be raisable."""
        from symbo_agentic_reasoners.core.message_bus import MessageIntegrityError
        with pytest.raises(MessageIntegrityError):
            raise MessageIntegrityError("Test error")

    def test_exception_message(self):
        """MessageIntegrityError should preserve message."""
        from symbo_agentic_reasoners.core.message_bus import MessageIntegrityError
        try:
            raise MessageIntegrityError("Signature verification failed")
        except MessageIntegrityError as e:
            assert str(e) == "Signature verification failed"


class TestModuleExports:
    """Tests for module exports."""

    def test_message_integrity_error_exported(self):
        """MessageIntegrityError should be exported."""
        from symbo_agentic_reasoners.core.message_bus import MessageIntegrityError
        assert MessageIntegrityError is not None

    def test_all_exports_present(self):
        """All __all__ exports should be present."""
        from symbo_agentic_reasoners.core import message_bus as mb
        for name in mb.__all__:
            assert hasattr(mb, name), f"Missing export: {name}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
