from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
import uuid
import time
import hmac
import hashlib
import json
import os
from enum import Enum


class MessageType(Enum):
    REQUEST = 'request'
    RESPONSE = 'response'
    BROADCAST = 'broadcast'
    NOTIFICATION = 'notification'


class MessagePriority(Enum):
    CRITICAL = -1
    URGENT = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class MessageStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class MessageDirection(Enum):
    TO_SPECIALIST = 'to_specialist'
    TO_SUPERVISOR = 'to_supervisor'
    BIDIRECTIONAL = 'bidirectional'


@dataclass
class AgentMessage:
    # Required fields (no defaults) must come first
    sender_id: str
    recipient_id: str
    message_type: MessageType
    content: Dict[str, Any]
    # Fields with defaults
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    status: MessageStatus = MessageStatus.PENDING
    direction: MessageDirection = MessageDirection.BIDIRECTIONAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    # Security: HMAC signature for message integrity
    signature: Optional[str] = None

    def get_signable_data(self) -> str:
        """Get canonical string representation for signing."""
        # Include all security-relevant fields in deterministic order
        data = {
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type.value,
            'content': self.content,
            'message_id': self.message_id,
            'timestamp': self.timestamp,
        }
        return json.dumps(data, sort_keys=True, separators=(',', ':'))


class MessageIntegrityError(Exception):
    """Raised when message HMAC verification fails."""
    pass


class MessageBus:
    # Default secret key (should be overridden in production)
    _DEFAULT_SECRET = b'symbo_agent_default_key_change_in_production'

    def __init__(self, secret_key: Optional[bytes] = None,
                 require_signatures: bool = True,
                 allow_unsigned: bool = False):
        """
        Initialize Message Bus.

        Phase 5 - Issue #7: Message integrity enforcement mandatory by default.

        Args:
            secret_key: HMAC secret key (env: SYMBO_MESSAGE_KEY)
            require_signatures: If True (default), signatures required (Issue #7)
            allow_unsigned: If False (default), reject unsigned messages (Issue #7)
        """
        self._handlers: Dict[str, List[Callable]] = {}
        self._message_queue: List[AgentMessage] = []
        self._message_store: Dict[str, AgentMessage] = {}
        # Security: use provided key or generate from environment/default
        self._secret_key = secret_key or self._get_secret_key()

        # Phase 5 - Issue #7: Mandatory signature verification
        self._require_signatures = require_signatures
        self._allow_unsigned = allow_unsigned

        # Track seen message IDs to prevent replay attacks
        self._seen_message_ids: Dict[str, float] = {}
        # Maximum age for message timestamps (5 minutes)
        self._max_message_age = 300.0

        # Statistics
        self.messages_signed = 0
        self.messages_verified = 0
        self.verification_failures = 0
        self.unsigned_messages_rejected = 0

    def _get_secret_key(self) -> bytes:
        """Get secret key from environment or use default."""
        env_key = os.environ.get('SYMBO_MESSAGE_KEY')
        if env_key:
            return env_key.encode('utf-8')
        return self._DEFAULT_SECRET

    def _sign_message(self, message: AgentMessage) -> str:
        """Generate HMAC-SHA256 signature for message."""
        data = message.get_signable_data().encode('utf-8')
        signature = hmac.new(self._secret_key, data, hashlib.sha256).hexdigest()
        return signature

    def _verify_message(self, message: AgentMessage) -> bool:
        """Verify message HMAC signature."""
        if message.signature is None:
            return False
        expected_signature = self._sign_message(message)
        return hmac.compare_digest(message.signature, expected_signature)

    def _check_replay(self, message: AgentMessage) -> bool:
        """Check if message is a replay attack."""
        # Check if message ID was already seen
        if message.message_id in self._seen_message_ids:
            return True
        # Check if message is too old
        current_time = time.time()
        if current_time - message.timestamp > self._max_message_age:
            return True
        # Clean up old entries (older than 2x max age)
        cleanup_threshold = current_time - (2 * self._max_message_age)
        self._seen_message_ids = {
            mid: ts for mid, ts in self._seen_message_ids.items()
            if ts > cleanup_threshold
        }
        return False

    def register_handler(self, agent_id: str, handler: Callable):
        """Perform register handler operation.

        Args:
        agent_id: Description needed
        handler: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.register_handler(...)
        """
        """Perform register handler operation.

        Args:
        agent_id: Description needed
        handler: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.register_handler(...)
        """
        if agent_id not in self._handlers:
            self._handlers[agent_id] = []
        self._handlers[agent_id].append(handler)

    def send_message(self, message: AgentMessage) -> str:
        """
        Send a message and return its message ID.

        Phase 5 - Issue #7: Signatures are now mandatory.

        Each send generates a unique message ID for tracking purposes,
        even if the same message object is sent multiple times.
        The message is signed with HMAC for integrity verification.

        Args:
            message: AgentMessage to send

        Returns:
            Message ID (UUID)

        Security:
            All messages are automatically signed with HMAC-SHA256.
        """
        # Generate new ID for each send to prevent replay attacks
        message.message_id = str(uuid.uuid4())
        message.timestamp = time.time()

        # Phase 5 - Issue #7: Sign the message (mandatory)
        message.signature = self._sign_message(message)
        self.messages_signed += 1

        self._message_store[message.message_id] = message
        self._message_queue.append(message)
        return message.message_id

    def process_messages(self):
        """
        Process queued messages with signature verification.

        Phase 5 - Issue #7: Mandatory signature verification enforced.
        """
        while self._message_queue:
            message = self._message_queue.pop(0)

            # Phase 5 - Issue #7: Enforce mandatory signature verification
            if self._require_signatures:
                # Check if message has signature
                if message.signature is None:
                    if not self._allow_unsigned:
                        # Reject unsigned messages
                        message.status = MessageStatus.FAILED
                        message.metadata['error'] = 'Message missing required signature (Issue #7)'
                        self.unsigned_messages_rejected += 1
                        continue

                # Verify signature
                if not self._verify_message(message):
                    message.status = MessageStatus.FAILED
                    message.metadata['error'] = 'HMAC signature verification failed'
                    self.verification_failures += 1
                    continue

                self.messages_verified += 1

                # Check for replay attacks
                if self._check_replay(message):
                    message.status = MessageStatus.FAILED
                    message.metadata['error'] = 'Replay attack detected'
                    self.verification_failures += 1
                    continue

                # Record message ID to prevent replay
                self._seen_message_ids[message.message_id] = message.timestamp

            message.status = MessageStatus.PROCESSING

            if message.recipient_id in self._handlers:
                """Get message status.

                Returns:
                Message status value or data

                Example:
                >>> result = obj.get_message_status()
                """
                for handler in self._handlers[message.recipient_id]:
                    try:
                        handler(message)
                        message.status = MessageStatus.COMPLETED
                    except Exception as e:
                        message.status = MessageStatus.FAILED
                        message.metadata['error'] = str(e)
                        # Add to retry queue based on priority
                        if message.priority != MessagePriority.LOW:
                            self._message_queue.append(message)

    def get_message_status(self, message_id: str) -> Optional[MessageStatus]:
        """Get message status.

        Returns:
        Message status value or data

        Example:
        >>> result = obj.get_message_status()
        """
        if message_id in self._message_store:
            return self._message_store[message_id].status
        return None

    def verify_message_integrity(self, message: AgentMessage) -> bool:
        """Public method to verify a message's integrity."""
        return self._verify_message(message)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get message bus statistics.

        Phase 5 - Issue #7: Includes message integrity metrics.

        Returns:
            Dictionary with message and security statistics
        """
        return {
            'total_messages': len(self._message_store),
            'queued_messages': len(self._message_queue),
            'handlers_registered': len(self._handlers),
            # Phase 5 - Issue #7: Message integrity statistics
            'require_signatures': self._require_signatures,
            'allow_unsigned': self._allow_unsigned,
            'messages_signed': self.messages_signed,
            'messages_verified': self.messages_verified,
            'verification_failures': self.verification_failures,
            'unsigned_messages_rejected': self.unsigned_messages_rejected,
            'seen_message_ids': len(self._seen_message_ids),
        }

# Global message bus instance (Phase 5 - Issue #7: signatures required)
message_bus = MessageBus(require_signatures=True, allow_unsigned=False)

# Exports for external use
__all__ = [
    'MessageType', 'MessagePriority', 'MessageStatus', 'MessageDirection',
    'AgentMessage', 'MessageBus', 'MessageIntegrityError', 'message_bus'
]