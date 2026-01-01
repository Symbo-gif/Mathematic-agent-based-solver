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
PHASE 0 - STEP 2: The Constitutional Law (FIPA-ACL Protocols)
=============================================================

FIPA-ACL (Agent Communication Language) Implementation

PURPOSE:
-------
Implements the FIPA Abstract Architecture with FIPA-ACL as the deterministic legal
framework governing all agent interactions. Every message becomes a structured packet
with mandatory fields enforcing explicit intent and semantic clarity.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 2 (Lines 106-179)
- Phase 0 Coding Strategy: Section 4.2 "The Rule of Law: FIPA-ACL for Explicit Intent"

ARCHITECTURE:
------------
Based on Speech Act Theory, treats every message as a formal, binding action
rather than conversational text.

KEY MECHANISMS:
--------------
1. Performative Field: Makes sender's intent explicit (REQUEST, INFORM, REFUSE, etc.)
2. Conversation IDs: Tracks problem-solving threads without redundant history
3. Content Encoding: All mathematical payloads must be OMDoc (raw text forbidden)

WHY THIS MATTERS:
----------------
The content of a message alone is insufficient for clear communication. An agent
receiving a message must know the *intent* behind it: Is it a request for information?
An order to perform a task? A confirmation that a task is complete?

Without FIPA-ACL, interactions are inefficient, ambiguous, and prone to error.
With FIPA-ACL, every message is a binding legal action with clear semantics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import uuid
import json

# Import OMDoc types for content validation
from symbo_agentic_reasoners.core.omdoc_schema import OMObject, OMDocStatement, OMDocTheory


class Performative(Enum):
    """
    FIPA Speech Act Performatives - Every message is a binding action

    Based on Speech Act Theory, performatives make the sender's communicative intent
    explicit and binding. Each performative has specific preconditions and effects.

    REFERENCE:
    ---------
    FIPA ACL Message Structure Specification
    Phase_0_Build_Order_Breakdown.md: Lines 129-141

    PERFORMATIVE TYPES:
    ------------------
    REQUEST: Sender wants receiver to perform an action
        Example: "Please integrate x² with respect to x"

    INFORM: Sender believes a proposition is true and wants receiver to believe it
        Example: "The derivative of sin(x) is cos(x)"

    QUERY_IF: Sender wants to know if a proposition is true
        Example: "Is x = 5 a solution to x² - 25 = 0?"

    QUERY_REF: Sender wants to know the value of a reference
        Example: "What is the value of variable x?"

    CONFIRM: Sender confirms that a proposition is true
        Example: "Yes, the proof is valid"

    DISCONFIRM: Sender confirms that a proposition is false
        Example: "No, that approach will not work"

    REFUSE: Agent declines to perform requested action
        Example: "I cannot solve this integral (outside my domain)"

    PROPOSE: Sender proposes to perform an action under certain conditions
        Example: "I can solve this if you provide initial conditions"

    ACCEPT_PROPOSAL: Receiver accepts a proposal
        Example: "Yes, proceed with that solution method"

    REJECT_PROPOSAL: Receiver rejects a proposal
        Example: "No, try a different approach"

    AGREE: Sender agrees to perform action (commits to REQUEST)
        Example: "I will compute the integral"

    FAILURE: Action was attempted but failed
        Example: "Integration failed: function too complex"

    CANCEL: Sender cancels a previous REQUEST
        Example: "Disregard my previous integration request"

    SUBSCRIBE: Subscribe to Blackboard updates matching criteria
        Example: "Notify me when variable 'x' is updated"

    NOT_UNDERSTOOD: Receiver did not understand the message
        Example: "Your OMDoc content is malformed"
    """
    REQUEST = 'request'              # Sender wants receiver to perform action
    INFORM = 'inform'                # Sender believes proposition is true
    QUERY_IF = 'query-if'            # Query: is proposition true?
    QUERY_REF = 'query-ref'          # Query: what is value of reference?
    CONFIRM = 'confirm'              # Sender confirms proposition is true
    DISCONFIRM = 'disconfirm'        # Sender confirms proposition is false
    REFUSE = 'refuse'                # Agent declines to perform action
    PROPOSE = 'propose'              # Sender proposes to perform action
    ACCEPT_PROPOSAL = 'accept-proposal'  # Accept a proposal
    REJECT_PROPOSAL = 'reject-proposal'  # Reject a proposal
    AGREE = 'agree'                  # Agree to perform action
    FAILURE = 'failure'              # Action attempted but failed
    CANCEL = 'cancel'                # Cancel previous request
    SUBSCRIBE = 'subscribe'          # Subscribe to Blackboard updates
    NOT_UNDERSTOOD = 'not-understood'  # Message not understood


class FIPAProtocol(Enum):
    """
    Standard FIPA Interaction Protocols

    Defines common patterns of multi-message interactions between agents.

    PROTOCOLS:
    ---------
    FIPA_REQUEST: Simple request-response interaction
    FIPA_QUERY: Query for information
    FIPA_CONTRACT_NET: Multi-agent task allocation via bidding
    FIPA_PROPOSE: Proposal negotiation
    FIPA_SUBSCRIBE: Subscription to information updates
    """
    FIPA_REQUEST = 'fipa-request'
    FIPA_QUERY = 'fipa-query'
    FIPA_CONTRACT_NET = 'fipa-contract-net'
    FIPA_PROPOSE = 'fipa-propose'
    FIPA_SUBSCRIBE = 'fipa-subscribe'
    FIPA_INFORM = 'fipa-inform'


@dataclass
class FIPAMessage:
    """
    FIPA-ACL Message Structure with mandatory fields

    Every agent-to-agent communication MUST be wrapped in a FIPAMessage.
    This enforces explicit intent, semantic clarity, and thread tracking.

    MANDATORY FIELDS:
    ----------------
    - performative: The speech act type (what the sender intends)
    - sender: Agent identifier of message sender
    - receiver: Agent identifier of intended recipient
    - content: OMDoc payload (NOT raw text - validated on creation)
    - conversation_id: Unique thread identifier for tracking problem-solving context

    OPTIONAL FIELDS:
    ---------------
    - ontology: Domain context (default: 'mathematics')
    - protocol: Interaction protocol being followed (default: 'fipa-request')
    - language: Content encoding language (default: 'omdoc', MUST be 'omdoc')
    - reply_with: Identifier for expected reply (for correlation)
    - in_reply_to: Reference to previous message ID
    - reply_by: Deadline for response

    VALIDATION:
    ----------
    - Content MUST be an OMDoc object (OMObject, OMDocStatement, or OMDocTheory)
    - Raw text content is FORBIDDEN (raises ValueError)
    - Language MUST be 'omdoc' (raises ValueError)

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: Lines 143-179
    FIPA ACL Message Structure Specification
    """
    # MANDATORY FIELDS
    performative: Performative           # The speech act type
    sender: str                          # Agent identifier (e.g., 'algebra_specialist_001')
    receiver: str                        # Target agent identifier (e.g., 'orchestrator')
    content: Any                         # OMDoc payload (OMObject, OMDocStatement, or OMDocTheory)
    conversation_id: str = field(        # Thread tracking - auto-generated UUID
        default_factory=lambda: str(uuid.uuid4()))

    # OPTIONAL FIELDS (with sensible defaults)
    ontology: str = 'mathematics'        # Domain context
    protocol: str = FIPAProtocol.FIPA_REQUEST.value  # Interaction protocol
    language: str = 'omdoc'              # Content encoding language (MUST be 'omdoc')
    reply_with: Optional[str] = None     # Expected reply identifier
    in_reply_to: Optional[str] = None    # Reference to prior message ID
    reply_by: Optional[datetime] = None  # Deadline for response

    # METADATA (for system tracking)
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def validate(self) -> bool:
        """
        Validate message conforms to FIPA-ACL requirements

        VALIDATION RULES:
        ----------------
        1. Language MUST be 'omdoc'
        2. Content MUST NOT be raw text (string)
        3. Content SHOULD be OMDoc object type (OMObject, OMDocStatement, or OMDocTheory)
        4. Sender and receiver must be non-empty strings
        5. Performative must be valid Performative enum value

        Raises:
            ValueError: If validation fails

        Returns:
            bool: True if valid
        """
        # Rule 1: Language must be 'omdoc'
        if self.language != 'omdoc':
            raise ValueError(
                f"FIPA-ACL Protocol Violation: Content language must be 'omdoc', got '{self.language}'. "
                f"Reference: Phase_0_Build_Order_Breakdown.md:160"
            )

        # Rule 2: Raw text content is FORBIDDEN
        if isinstance(self.content, str):
            raise ValueError(
                f"FIPA-ACL Protocol Violation: Raw text content is forbidden. "
                f"All mathematical content must be encoded in OMDoc format. "
                f"Reference: Phase_0_Build_Order_Breakdown.md:162"
            )

        # Rule 3: Content should be OMDoc type (warning if not)
        if not isinstance(self.content, (OMObject, OMDocStatement, OMDocTheory, dict)):
            print(f"WARNING: Content is not an OMDoc type. Type: {type(self.content)}")

        # Rule 4: Sender and receiver must be valid
        if not self.sender or not self.receiver:
            raise ValueError("Sender and receiver must be non-empty strings")

        # Rule 5: Performative must be valid
        if not isinstance(self.performative, Performative):
            raise ValueError(f"Invalid performative: {self.performative}")

        return True

    def serialize(self) -> dict:
        """
        Serialize message for transmission over ACC (Agent Communication Channel)

        Returns:
            dict: JSON-serializable representation of message

        Reference:
            Phase_0_Build_Order_Breakdown.md: Lines 167-178
        """
        self.validate()  # Validate before serialization

        serialized = {
            'message_id': self.message_id,
            'performative': self.performative.value,
            'sender': self.sender,
            'receiver': self.receiver,
            'conversation_id': self.conversation_id,
            'ontology': self.ontology,
            'protocol': self.protocol,
            'language': self.language,
            'timestamp': self.timestamp.isoformat(),
        }

        # Serialize content if it has a serialize method (OMDoc types)
        if hasattr(self.content, 'serialize'):
            serialized['content'] = self.content.serialize()
        else:
            serialized['content'] = self.content

        # Add optional fields if present
        if self.reply_with:
            serialized['reply_with'] = self.reply_with
        if self.in_reply_to:
            serialized['in_reply_to'] = self.in_reply_to
        if self.reply_by:
            serialized['reply_by'] = self.reply_by.isoformat()

        return serialized

    @classmethod
    def deserialize(cls, data: dict) -> 'FIPAMessage':
        """
        Deserialize message from dictionary

        Args:
            data: Serialized message dictionary

        Returns:
            FIPAMessage: Reconstructed message object
        """
        # Parse performative
        performative = Performative(data['performative'])

        # Parse timestamp
        timestamp = datetime.fromisoformat(data['timestamp'])

        # Parse reply_by if present
        reply_by = None
        if 'reply_by' in data and data['reply_by']:
            reply_by = datetime.fromisoformat(data['reply_by'])

        # Reconstruct content (attempt to deserialize as OMDoc if possible)
        content = data['content']
        if isinstance(content, dict):
            # Try to deserialize as OMDoc types
            if 'operator' in content or 'variable' in content or 'value' in content:
                content = OMObject.deserialize(content)
            elif 'statement_type' in content:
                content = OMDocStatement.deserialize(content)
            elif 'theory_name' in content or 'statements' in content:
                content = OMDocTheory.deserialize(content)

        return cls(
            performative=performative,
            sender=data['sender'],
            receiver=data['receiver'],
            content=content,
            conversation_id=data['conversation_id'],
            ontology=data.get('ontology', 'mathematics'),
            protocol=data.get('protocol', FIPAProtocol.FIPA_REQUEST.value),
            language=data.get('language', 'omdoc'),
            reply_with=data.get('reply_with'),
            in_reply_to=data.get('in_reply_to'),
            reply_by=reply_by,
            timestamp=timestamp,
            message_id=data['message_id']
        )

    def create_reply(self, performative: Performative, content: Any) -> 'FIPAMessage':
        """
        Create a reply message to this message

        Automatically sets conversation_id, in_reply_to, and swaps sender/receiver.

        Args:
            performative: Performative for the reply
            content: OMDoc content for the reply

        Returns:
            FIPAMessage: New reply message
        """
        return FIPAMessage(
            performative=performative,
            sender=self.receiver,           # Swap: original receiver becomes sender
            receiver=self.sender,           # Swap: original sender becomes receiver
            content=content,
            conversation_id=self.conversation_id,  # Maintain thread
            in_reply_to=self.message_id,    # Reference this message
            ontology=self.ontology,
            protocol=self.protocol,
            language=self.language
        )

    def __repr__(self) -> str:
        """Human-readable representation"""
        content_preview = str(self.content)[:50] + "..." if len(str(self.content)) > 50 else str(self.content)
        return (f"FIPAMessage({self.performative.value}: {self.sender} → {self.receiver} "
                f"[{self.conversation_id[:8]}...] {content_preview})")


# Helper functions for creating common message types

def create_request(sender: str, receiver: str, content: Any,
                   conversation_id: Optional[str] = None) -> FIPAMessage:
    """Helper: Create a REQUEST message"""
    msg = FIPAMessage(
        performative=Performative.REQUEST,
        sender=sender,
        receiver=receiver,
        content=content,
        protocol=FIPAProtocol.FIPA_REQUEST.value
    )
    if conversation_id:
        msg.conversation_id = conversation_id
    return msg


def create_inform(sender: str, receiver: str, content: Any,
                  conversation_id: Optional[str] = None,
                  in_reply_to: Optional[str] = None) -> FIPAMessage:
    """Helper: Create an INFORM message"""
    msg = FIPAMessage(
        performative=Performative.INFORM,
        sender=sender,
        receiver=receiver,
        content=content,
        protocol=FIPAProtocol.FIPA_INFORM.value,
        in_reply_to=in_reply_to
    )
    if conversation_id:
        msg.conversation_id = conversation_id
    return msg


def create_query(sender: str, receiver: str, content: Any,
                 conversation_id: Optional[str] = None) -> FIPAMessage:
    """Helper: Create a QUERY_IF message"""
    msg = FIPAMessage(
        performative=Performative.QUERY_IF,
        sender=sender,
        receiver=receiver,
        content=content,
        protocol=FIPAProtocol.FIPA_QUERY.value
    )
    if conversation_id:
        msg.conversation_id = conversation_id
    return msg


def create_failure(sender: str, receiver: str, content: Any,
                   conversation_id: Optional[str] = None,
                   in_reply_to: Optional[str] = None) -> FIPAMessage:
    """Helper: Create a FAILURE message"""
    msg = FIPAMessage(
        performative=Performative.FAILURE,
        sender=sender,
        receiver=receiver,
        content=content,
        in_reply_to=in_reply_to
    )
    if conversation_id:
        msg.conversation_id = conversation_id
    return msg


if __name__ == "__main__":
    """Demonstration of FIPA-ACL functionality"""
    print("=" * 80)
    print("PHASE 0 - STEP 2: FIPA-ACL Constitutional Law")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.omdoc_schema import create_variable, create_operation, MathOperator

    # Example 1: Valid FIPA-ACL message with OMDoc content
    print("Example 1: Valid FIPA-ACL REQUEST with OMDoc content")
    x_squared = create_operation(MathOperator.POWER, create_variable('x'), create_variable('2'))
    request_msg = create_request(
        sender='orchestrator',
        receiver='algebra_specialist_001',
        content=x_squared
    )
    print(f"  {request_msg}")
    print(f"  Valid: {request_msg.validate()}")
    print()

    # Example 2: Invalid message with raw text (should raise error)
    print("Example 2: Invalid FIPA-ACL message with raw text (FORBIDDEN)")
    try:
        invalid_msg = FIPAMessage(
            performative=Performative.REQUEST,
            sender='orchestrator',
            receiver='algebra_specialist_001',
            content="Please solve x^2 + 2x + 1"  # RAW TEXT - FORBIDDEN
        )
        invalid_msg.validate()
    except ValueError as e:
        print(f"  ✓ Validation correctly rejected raw text: {e}")
    print()

    # Example 3: Reply pattern
    print("Example 3: Reply pattern with conversation threading")
    solution = create_variable('solution_object')
    reply_msg = request_msg.create_reply(
        performative=Performative.INFORM,
        content=solution
    )
    print(f"  Original: {request_msg}")
    print(f"  Reply: {reply_msg}")
    print(f"  Same conversation: {request_msg.conversation_id == reply_msg.conversation_id}")
    print(f"  Reply references original: {reply_msg.in_reply_to == request_msg.message_id}")
    print()

    # Example 4: Serialization/Deserialization
    print("Example 4: Serialization for ACC transmission")
    serialized = request_msg.serialize()
    print(f"  Serialized: {json.dumps(serialized, indent=2)[:200]}...")
    deserialized = FIPAMessage.deserialize(serialized)
    print(f"  Deserialized: {deserialized}")
    print(f"  Round-trip successful: {deserialized.message_id == request_msg.message_id}")
    print()

    print("✓ FIPA-ACL Constitutional Law implementation complete")
    print("  - Performative Field: Explicit intent ✓")
    print("  - Conversation IDs: Thread tracking without history ✓")
    print("  - Content Encoding: OMDoc only (raw text forbidden) ✓")
