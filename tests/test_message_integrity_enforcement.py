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
Message Integrity Enforcement Tests
===================================

Phase 5 - Issue #7: Message Integrity Verification Tests

Tests mandatory HMAC signature verification to prevent message tampering.

Test Categories:
1. Message signing (automatic on send)
2. Signature verification (mandatory on receive)
3. Replay attack prevention
4. Unsigned message rejection
5. Signature tampering detection
6. ACC integration
"""

import pytest
import time
from unittest.mock import Mock, patch

from symbo_agentic_reasoners.core.message_bus import (
    MessageBus, AgentMessage, MessageType, MessagePriority,
    MessageStatus, MessageIntegrityError
)
from symbo_agentic_reasoners.infrastructure.acc import (
    AgentCommunicationChannel
)
from symbo_agentic_reasoners.protocols.fipa_acl import (
    FIPAMessage, Performative
)


class TestMessageBusSignatures:
    """Test MessageBus signature enforcement."""

    def test_message_automatically_signed(self):
        """Test messages are automatically signed on send."""
        bus = MessageBus()

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )

        message_id = bus.send_message(message)

        # Verify message was signed
        stored_message = bus._message_store[message_id]
        assert stored_message.signature is not None
        assert len(stored_message.signature) == 64  # SHA256 hex digest
        assert bus.messages_signed == 1

    def test_signature_verification_success(self):
        """Test valid signatures pass verification."""
        bus = MessageBus(require_signatures=True, allow_unsigned=False)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )

        # Send and sign
        message_id = bus.send_message(message)

        # Register handler
        received_messages = []
        bus.register_handler('agent_002', lambda msg: received_messages.append(msg))

        # Process - should succeed
        bus.process_messages()

        assert len(received_messages) == 1
        assert bus.messages_verified == 1
        assert bus.verification_failures == 0

    def test_unsigned_message_rejected(self):
        """Test unsigned messages are rejected when required."""
        bus = MessageBus(require_signatures=True, allow_unsigned=False)

        # Create message without signature
        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )
        message.signature = None  # Remove signature

        # Add directly to queue (bypass send_message which auto-signs)
        bus._message_queue.append(message)

        # Register handler
        received_messages = []
        bus.register_handler('agent_002', lambda msg: received_messages.append(msg))

        # Process - should reject
        bus.process_messages()

        assert len(received_messages) == 0
        assert bus.unsigned_messages_rejected == 1
        assert message.status == MessageStatus.FAILED

    def test_tampered_signature_rejected(self):
        """Test messages with tampered signatures are rejected."""
        bus = MessageBus(require_signatures=True)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )

        # Send and sign
        bus.send_message(message)

        # Tamper with content after signing
        message.content['action'] = 'malicious_action'

        # Add to queue
        bus._message_queue.append(message)

        # Register handler
        received_messages = []
        bus.register_handler('agent_002', lambda msg: received_messages.append(msg))

        # Process - should reject
        bus.process_messages()

        assert len(received_messages) == 0
        assert bus.verification_failures >= 1

    def test_replay_attack_detected(self):
        """Test replay attacks are detected and blocked."""
        bus = MessageBus(require_signatures=True)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )

        # Send once
        bus.send_message(message)

        # Register handler
        received_messages = []
        bus.register_handler('agent_002', lambda msg: received_messages.append(msg))

        # Process first time - should succeed
        bus.process_messages()
        assert len(received_messages) == 1

        # Try to replay same message
        bus._message_queue.append(message)

        # Process again - should be rejected as replay
        bus.process_messages()

        # Should not have received second copy
        assert len(received_messages) == 1
        assert bus.verification_failures >= 1

    def test_expired_message_rejected(self):
        """Test messages older than 5 minutes are rejected."""
        bus = MessageBus(require_signatures=True)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )

        # Create message with old timestamp (10 minutes ago)
        old_timestamp = time.time() - 600
        message.timestamp = old_timestamp
        message.signature = bus._sign_message(message)

        bus._message_queue.append(message)

        # Register handler
        received_messages = []
        bus.register_handler('agent_002', lambda msg: received_messages.append(msg))

        # Process - should reject as too old
        bus.process_messages()

        assert len(received_messages) == 0

    def test_message_bus_statistics(self):
        """Test message bus reports integrity statistics."""
        bus = MessageBus(require_signatures=True)

        # Send several messages
        for i in range(3):
            message = AgentMessage(
                sender_id=f'agent_{i:03d}',
                recipient_id='agent_999',
                message_type=MessageType.REQUEST,
                content={'index': i}
            )
            bus.send_message(message)

        # Register handler and process
        bus.register_handler('agent_999', lambda msg: None)
        bus.process_messages()

        stats = bus.get_statistics()

        assert stats['messages_signed'] == 3
        assert stats['messages_verified'] == 3
        assert stats['require_signatures'] is True
        assert stats['allow_unsigned'] is False

    def test_signature_verification_can_be_disabled(self):
        """Test signature verification can be disabled for testing."""
        bus = MessageBus(require_signatures=False)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )
        message.signature = None  # No signature

        bus._message_queue.append(message)

        # Register handler
        received_messages = []
        bus.register_handler('agent_002', lambda msg: received_messages.append(msg))

        # Process - should succeed (verification disabled)
        bus.process_messages()

        assert len(received_messages) == 1


class TestACCIntegrity:
    """Test ACC message integrity integration."""

    def test_acc_has_signature_verification(self):
        """Test ACC initializes with signature verification."""
        acc = AgentCommunicationChannel(enable_signature_verification=True)

        assert acc._enable_signature_verification is True
        assert acc.signature_verifications == 0
        assert acc.signature_failures == 0

    def test_acc_verifies_message_integrity(self):
        """Test ACC verifies message integrity on send."""
        acc = AgentCommunicationChannel(enable_signature_verification=True)

        message = FIPAMessage(
            performative=Performative.REQUEST,
            sender='agent_001',
            receiver='agent_002',
            content={'action': 'test'}
        )

        # Send - should verify
        envelope_id = acc.send(message)

        assert envelope_id is not None
        assert acc.signature_verifications == 1

    def test_acc_rejects_invalid_message(self):
        """Test ACC rejects messages with missing required fields."""
        acc = AgentCommunicationChannel(enable_signature_verification=True)

        # Create invalid message (missing sender)
        message = FIPAMessage(
            performative=Performative.REQUEST,
            sender=None,  # Invalid
            receiver='agent_002',
            content={'action': 'test'}
        )

        # Send - should fail verification
        with pytest.raises(ValueError, match="Message integrity verification failed"):
            acc.send(message)

        assert acc.signature_failures == 1

    def test_acc_signature_verification_can_be_disabled(self):
        """Test ACC can disable verification for testing."""
        acc = AgentCommunicationChannel(enable_signature_verification=False)

        # Create message
        message = FIPAMessage(
            performative=Performative.REQUEST,
            sender='agent_001',
            receiver='agent_002',
            content={'action': 'test'}
        )

        # Send - should succeed without verification
        envelope_id = acc.send(message)

        assert envelope_id is not None
        assert acc.signature_verifications == 0  # Disabled


class TestIntegrityAttackScenarios:
    """Test that message integrity prevents attacks."""

    def test_prevents_message_tampering(self):
        """Test that tampering with message content is detected."""
        bus = MessageBus(require_signatures=True)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'amount': 100}
        )

        # Send and sign
        bus.send_message(message)

        # Malicious tampering: change amount after signing
        message.content['amount'] = 1000000

        bus._message_queue.append(message)

        # Try to process
        bus.register_handler('agent_002', lambda msg: None)
        bus.process_messages()

        # Should fail verification
        assert bus.verification_failures >= 1
        assert message.status == MessageStatus.FAILED

    def test_prevents_sender_spoofing(self):
        """Test that changing sender after signing is detected."""
        bus = MessageBus(require_signatures=True)

        message = AgentMessage(
            sender_id='agent_001',
            recipient_id='agent_002',
            message_type=MessageType.REQUEST,
            content={'action': 'test'}
        )

        # Send and sign
        bus.send_message(message)

        # Malicious spoofing: change sender after signing
        message.sender_id = 'admin_agent'

        bus._message_queue.append(message)

        # Try to process
        bus.register_handler('agent_002', lambda msg: None)
        bus.process_messages()

        # Should fail verification
        assert bus.verification_failures >= 1


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
