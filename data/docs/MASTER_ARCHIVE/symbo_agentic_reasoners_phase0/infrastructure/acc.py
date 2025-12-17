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
PHASE 0 - STEP 4: The Bureaucratic Infrastructure Team - ACC
============================================================

Agent Communication Channel (ACC) - "The Postmaster"

PURPOSE:
-------
Guarantees routing of FIPA-ACL messages between agents. Responsible for queuing
messages for agents that are currently inactive or swapped out of VRAM, ensuring
no messages are lost in the "One-Model-At-A-Time" architecture.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 4 (Lines 250-264)
- Phase 0 Coding Strategy: Section 3.0 "The Civic Infrastructure"
- Phase 0_ Infrastructural Agents and Hardware Calibration: ACC description

AGENT TYPE:
----------
Transport/Routing Agent - Message passing infrastructure

ROLE & ANALOGY:
--------------
"Postmaster" - Delivers FIPA-ACL messages to their destinations. In the
"One-Model-At-A-Time" architecture, many agents are inactive (swapped out
of VRAM) at any given time. ACC queues messages for inactive agents and
delivers them when the agent becomes active.

WHY THIS MATTERS:
----------------
With limited VRAM, agents operate in a time-sliced manner. Agent A may send
a message to Agent B, but Agent B is not currently loaded. Without ACC,
the message would be lost. ACC ensures reliable message delivery in this
asynchronous, resource-constrained environment.

KEY OPERATIONS:
--------------
1. Send: Route message to destination agent
2. Queue: Store messages for inactive agents
3. Deliver: Deliver queued messages when agent activates
4. Broadcast: Send message to multiple recipients
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Set
from datetime import datetime
import threading
import uuid
from collections import deque

# Import FIPA-ACL types
from ..core.fipa_acl import FIPAMessage, Performative


@dataclass
class MessageEnvelope:
    """
    Internal wrapper for messages in transit

    Tracks message delivery status and metadata.

    FIELDS:
    ------
    - message: The FIPA-ACL message being delivered
    - envelope_id: Unique identifier for this envelope
    - queued_at: Timestamp when message was queued
    - delivered: Whether message has been delivered
    - delivered_at: Timestamp of delivery
    - attempts: Number of delivery attempts
    """
    message: FIPAMessage
    envelope_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    queued_at: datetime = field(default_factory=datetime.now)
    delivered: bool = False
    delivered_at: Optional[datetime] = None
    attempts: int = 0

    def __repr__(self) -> str:
        """Human-readable representation"""
        status = "delivered" if self.delivered else "pending"
        return (f"Envelope[{self.envelope_id[:8]}...] {status} "
                f"({self.message.sender} → {self.message.receiver})")


class AgentCommunicationChannel:
    """
    The "Postmaster" - Message routing infrastructure

    ACC is responsible for reliable message delivery in the asynchronous,
    resource-constrained environment where agents are frequently swapped in/out
    of VRAM.

    ARCHITECTURE:
    ------------
    - Message Queue: Per-agent message queues for inactive agents
    - Delivery Callbacks: Registered callbacks for active agents
    - Routing Table: Maps agent IDs to delivery mechanisms

    THREAD SAFETY:
    -------------
    All operations are protected by a reentrant lock (threading.RLock) to ensure
    thread-safe access from multiple threads.

    TYPICAL WORKFLOW:
    ----------------
    1. Agent A (active) sends message to Agent B (inactive):
       - ACC receives message via send()
       - ACC checks if Agent B is active (has registered callback)
       - Agent B is inactive, so ACC queues message

    2. AMS activates Agent B:
       - Agent B registers delivery callback with ACC
       - ACC delivers all queued messages to Agent B
       - Agent B processes messages

    3. Agent B sends reply to Agent A:
       - Agent A is still active, ACC delivers immediately via callback
    """

    def __init__(self):
        """Initialize Agent Communication Channel"""
        self._message_queues: Dict[str, deque[MessageEnvelope]] = {}  # agent_id -> queue
        self._delivery_callbacks: Dict[str, Callable[[FIPAMessage], None]] = {}  # agent_id -> callback
        self._sent_messages: Dict[str, MessageEnvelope] = {}  # message_id -> envelope
        self._lock = threading.RLock()
        self._message_history: List[MessageEnvelope] = []  # For auditing

    def register_agent(self, agent_id: str,
                      callback: Callable[[FIPAMessage], None]) -> int:
        """
        Register agent's message delivery callback

        When an agent becomes active, it registers a callback function.
        ACC will invoke this callback to deliver messages.

        Args:
            agent_id: Agent identifier
            callback: Function to call with incoming messages

        Returns:
            int: Number of queued messages delivered

        EXAMPLE:
        -------
        def my_message_handler(msg: FIPAMessage):
            print(f"Received: {msg}")

        acc.register_agent('algebra_001', my_message_handler)
        """
        with self._lock:
            # Register callback
            self._delivery_callbacks[agent_id] = callback

            # Deliver queued messages
            delivered_count = 0
            if agent_id in self._message_queues:
                queue = self._message_queues[agent_id]
                while queue:
                    envelope = queue.popleft()
                    try:
                        callback(envelope.message)
                        envelope.delivered = True
                        envelope.delivered_at = datetime.now()
                        delivered_count += 1
                    except Exception as e:
                        print(f"ACC: Delivery callback error for {agent_id}: {e}")
                        # Re-queue message
                        queue.appendleft(envelope)
                        break

            print(f"ACC: Agent {agent_id} registered, delivered {delivered_count} queued message(s)")
            return delivered_count

    def unregister_agent(self, agent_id: str):
        """
        Unregister agent's message delivery callback

        When an agent deactivates, it unregisters. Future messages will be queued.

        Args:
            agent_id: Agent identifier
        """
        with self._lock:
            if agent_id in self._delivery_callbacks:
                del self._delivery_callbacks[agent_id]
                print(f"ACC: Agent {agent_id} unregistered")

    def send(self, message: FIPAMessage) -> str:
        """
        Send message to destination agent

        If recipient is active (has registered callback), delivers immediately.
        Otherwise, queues message for later delivery.

        Args:
            message: FIPA-ACL message to send

        Returns:
            str: Envelope ID for tracking

        REFERENCE:
        ---------
        Phase_0_Build_Order_Breakdown.md: Lines 250-264
        """
        with self._lock:
            # Validate message
            message.validate()

            # Create envelope
            envelope = MessageEnvelope(message=message)
            self._sent_messages[message.message_id] = envelope
            self._message_history.append(envelope)

            receiver = message.receiver

            # Attempt immediate delivery if agent is active
            if receiver in self._delivery_callbacks:
                try:
                    self._delivery_callbacks[receiver](message)
                    envelope.delivered = True
                    envelope.delivered_at = datetime.now()
                    print(f"ACC: Delivered immediately to {receiver}")
                except Exception as e:
                    print(f"ACC: Immediate delivery failed: {e}, queuing message")
                    self._queue_message(receiver, envelope)
            else:
                # Queue for later delivery
                self._queue_message(receiver, envelope)

            return envelope.envelope_id

    def _queue_message(self, agent_id: str, envelope: MessageEnvelope):
        """
        Queue message for inactive agent

        Args:
            agent_id: Recipient agent identifier
            envelope: Message envelope to queue
        """
        if agent_id not in self._message_queues:
            self._message_queues[agent_id] = deque()

        self._message_queues[agent_id].append(envelope)
        envelope.attempts += 1
        print(f"ACC: Queued message for {agent_id} (queue size: {len(self._message_queues[agent_id])})")

    def broadcast(self, message: FIPAMessage, recipients: List[str]) -> List[str]:
        """
        Broadcast message to multiple recipients

        Creates a copy of the message for each recipient (with updated receiver field)
        and sends via normal send() mechanism.

        Args:
            message: Template message to broadcast
            recipients: List of recipient agent IDs

        Returns:
            List of envelope IDs
        """
        envelope_ids = []

        with self._lock:
            for recipient in recipients:
                # Create message copy with updated receiver
                broadcast_msg = FIPAMessage(
                    performative=message.performative,
                    sender=message.sender,
                    receiver=recipient,
                    content=message.content,
                    conversation_id=message.conversation_id,
                    ontology=message.ontology,
                    protocol=message.protocol,
                    language=message.language,
                    reply_with=message.reply_with,
                    in_reply_to=message.in_reply_to,
                    reply_by=message.reply_by
                )

                envelope_id = self.send(broadcast_msg)
                envelope_ids.append(envelope_id)

        print(f"ACC: Broadcast to {len(recipients)} recipient(s)")
        return envelope_ids

    def get_queue_size(self, agent_id: str) -> int:
        """
        Get number of queued messages for an agent

        Args:
            agent_id: Agent identifier

        Returns:
            int: Number of messages in queue
        """
        with self._lock:
            if agent_id in self._message_queues:
                return len(self._message_queues[agent_id])
            return 0

    def get_queued_messages(self, agent_id: str) -> List[FIPAMessage]:
        """
        Get queued messages for an agent (without removing from queue)

        Args:
            agent_id: Agent identifier

        Returns:
            List of FIPAMessage objects
        """
        with self._lock:
            if agent_id in self._message_queues:
                return [env.message for env in self._message_queues[agent_id]]
            return []

    def is_agent_active(self, agent_id: str) -> bool:
        """
        Check if agent has registered callback (is active)

        Args:
            agent_id: Agent identifier

        Returns:
            bool: True if agent is active
        """
        with self._lock:
            return agent_id in self._delivery_callbacks

    def get_message_status(self, message_id: str) -> Optional[MessageEnvelope]:
        """
        Get delivery status of a message

        Args:
            message_id: Message identifier

        Returns:
            MessageEnvelope or None if not found
        """
        with self._lock:
            return self._sent_messages.get(message_id)

    def get_conversation_messages(self, conversation_id: str) -> List[MessageEnvelope]:
        """
        Get all messages in a conversation thread

        Args:
            conversation_id: Conversation identifier

        Returns:
            List of MessageEnvelope objects
        """
        with self._lock:
            return [env for env in self._message_history
                   if env.message.conversation_id == conversation_id]

    def get_statistics(self) -> Dict[str, any]:
        """
        Get ACC statistics

        Returns:
            Dictionary with statistics about message delivery
        """
        with self._lock:
            total_queued = sum(len(q) for q in self._message_queues.values())
            active_agents = len(self._delivery_callbacks)

            delivered = len([e for e in self._message_history if e.delivered])
            pending = len([e for e in self._message_history if not e.delivered])

            queue_sizes = {
                agent_id: len(queue)
                for agent_id, queue in self._message_queues.items()
                if queue
            }

            return {
                'total_messages_sent': len(self._message_history),
                'delivered': delivered,
                'pending': pending,
                'total_queued': total_queued,
                'active_agents': active_agents,
                'agents_with_queued_messages': len(queue_sizes),
                'queue_sizes': queue_sizes
            }

    def clear_history(self):
        """Clear message history (for testing)"""
        with self._lock:
            self._message_history.clear()
            self._sent_messages.clear()

    def __repr__(self) -> str:
        """Human-readable representation"""
        stats = self.get_statistics()
        return (f"ACC(messages={stats['total_messages_sent']}, "
                f"delivered={stats['delivered']}, "
                f"pending={stats['pending']}, "
                f"active_agents={stats['active_agents']})")


if __name__ == "__main__":
    """Demonstration of ACC functionality"""
    print("=" * 80)
    print("PHASE 0 - STEP 4: Agent Communication Channel (ACC)")
    print("=" * 80)
    print()

    from ..core.fipa_acl import create_request, create_inform
    from ..core.omdoc_schema import create_variable, create_operation, MathOperator

    # Initialize ACC
    acc = AgentCommunicationChannel()
    print(f"Initialized: {acc}")
    print()

    # Example 1: Send message to inactive agent (gets queued)
    print("Example 1: Send message to inactive agent")
    problem = create_operation(MathOperator.INT,
                              create_operation(MathOperator.POWER,
                                             create_variable('x'),
                                             create_variable('2')),
                              create_variable('x'))
    msg1 = create_request(
        sender='orchestrator',
        receiver='integration_specialist_001',
        content=problem
    )
    envelope_id = acc.send(msg1)
    print(f"  Envelope ID: {envelope_id}")
    print(f"  {acc}")
    print()

    # Example 2: Register agent and receive queued messages
    print("Example 2: Agent activates and receives queued messages")
    received_messages = []

    def integration_callback(msg: FIPAMessage):
        received_messages.append(msg)
        print(f"  📬 Integration agent received: {msg.performative.value} from {msg.sender}")

    delivered = acc.register_agent('integration_specialist_001', integration_callback)
    print(f"  Delivered {delivered} queued message(s)")
    print(f"  {acc}")
    print()

    # Example 3: Send message to active agent (immediate delivery)
    print("Example 3: Send message to active agent (immediate delivery)")
    msg2 = create_request(
        sender='orchestrator',
        receiver='integration_specialist_001',
        content=create_variable('another_problem')
    )
    acc.send(msg2)
    print(f"  Total messages received by agent: {len(received_messages)}")
    print()

    # Example 4: Agent deactivates, messages get queued again
    print("Example 4: Agent deactivates, new messages get queued")
    acc.unregister_agent('integration_specialist_001')
    msg3 = create_request(
        sender='orchestrator',
        receiver='integration_specialist_001',
        content=create_variable('third_problem')
    )
    acc.send(msg3)
    queue_size = acc.get_queue_size('integration_specialist_001')
    print(f"  Queue size for integration_specialist_001: {queue_size}")
    print()

    # Example 5: Broadcast message
    print("Example 5: Broadcast message to multiple agents")

    # Register additional agents
    algebra_messages = []
    def algebra_callback(msg: FIPAMessage):
        algebra_messages.append(msg)
        print(f"  📬 Algebra agent received: {msg.performative.value}")

    calculus_messages = []
    def calculus_callback(msg: FIPAMessage):
        calculus_messages.append(msg)
        print(f"  📬 Calculus agent received: {msg.performative.value}")

    acc.register_agent('algebra_001', algebra_callback)
    acc.register_agent('calculus_001', calculus_callback)

    broadcast_msg = create_inform(
        sender='orchestrator',
        receiver='broadcast',  # Will be replaced per recipient
        content=create_variable('system_announcement')
    )
    acc.broadcast(broadcast_msg, ['algebra_001', 'calculus_001', 'integration_specialist_001'])
    print()

    # Example 6: Statistics
    print("Example 6: ACC Statistics")
    import json
    stats = acc.get_statistics()
    print(json.dumps(stats, indent=2))
    print()

    print("✓ Agent Communication Channel (ACC) implementation complete")
    print("  - Message routing ✓")
    print("  - Queuing for inactive agents ✓")
    print("  - Immediate delivery to active agents ✓")
    print("  - Broadcast messaging ✓")
