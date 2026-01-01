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
Message Queue Bounds Tests
===========================

Phase 5 - Issue #6: Bounded message queue tests.

Tests size and TTL limits to prevent memory exhaustion DoS.
"""

import pytest
import time
from unittest.mock import Mock

from symbo_agentic_reasoners.infrastructure.acc import (
    BoundedMessageQueue, MessageEnvelope
)
from symbo_agentic_reasoners.protocols.fipa_acl import FIPAMessage, Performative


class TestBoundedMessageQueue:
    """Test BoundedMessageQueue class."""

    def test_queue_initialization(self):
        """Test queue initializes with correct defaults."""
        queue = BoundedMessageQueue()
        assert queue.max_size == 1000
        assert queue.ttl_seconds == 3600
        assert queue.size() == 0

    def test_enqueue_dequeue(self):
        """Test basic enqueue/dequeue operations."""
        queue = BoundedMessageQueue(max_size=10)
        envelope = Mock(spec=MessageEnvelope)

        # Enqueue
        result = queue.enqueue(envelope)
        assert result is True
        assert queue.size() == 1

        # Dequeue
        dequeued = queue.dequeue()
        assert dequeued == envelope
        assert queue.size() == 0

    def test_size_limit_enforced(self):
        """Test queue rejects messages when full."""
        queue = BoundedMessageQueue(max_size=3)

        # Fill queue
        for i in range(3):
            envelope = Mock(spec=MessageEnvelope)
            assert queue.enqueue(envelope) is True

        # Try to add 4th message - should fail
        envelope4 = Mock(spec=MessageEnvelope)
        result = queue.enqueue(envelope4)

        assert result is False
        assert queue.size() == 3
        assert queue._dropped_count == 1

    def test_ttl_expiration(self):
        """Test messages expire after TTL."""
        queue = BoundedMessageQueue(max_size=10, ttl_seconds=1)
        envelope = Mock(spec=MessageEnvelope)

        # Enqueue
        queue.enqueue(envelope)
        assert queue.size() == 1

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert queue.size() == 0
        assert queue._expired_count == 1

    def test_peek_without_removal(self):
        """Test peek doesn't remove message."""
        queue = BoundedMessageQueue()
        envelope = Mock(spec=MessageEnvelope)

        queue.enqueue(envelope)

        # Peek
        peeked = queue.peek()
        assert peeked == envelope
        assert queue.size() == 1  # Still there

    def test_queue_stats(self):
        """Test queue statistics reporting."""
        queue = BoundedMessageQueue(max_size=5, ttl_seconds=60)

        # Add some messages
        for _ in range(3):
            queue.enqueue(Mock(spec=MessageEnvelope))

        stats = queue.get_stats()

        assert stats['size'] == 3
        assert stats['max_size'] == 5
        assert stats['ttl_seconds'] == 60
        assert stats['utilization'] == 0.6  # 3/5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
