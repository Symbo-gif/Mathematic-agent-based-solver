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
PHASE 0 - STEP 3: The Active Memory Architecture (Blackboard System)
===================================================================

Blackboard + Publish-Subscribe Mechanism

PURPOSE:
-------
Deploys a centralized Blackboard with Publish-Subscribe mechanism for active
collaboration. Enables agents to post partial results, subscribe to updates,
and work together in emergent parallel problem-solving.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 3 (Lines 180-249)
- Phase 0 Coding Strategy: Section 5.0 "The Public Memory: Building a Collective Consciousness"

ARCHITECTURE:
------------
The Blackboard serves as the dynamic workspace - the "shared brain" of the system.
Agents post entries and subscribe to updates matching specific tags, enabling
emergent collaborative problem-solving without explicit orchestration.

KEY MECHANISMS:
--------------
1. Blackboard Entries: Typed entries (task, lemma, partial_result, proof_step)
2. Publish-Subscribe: Agents subscribe to tags, get notified on matching posts
3. Entry Status: Tracks lifecycle (pending, in_progress, completed, failed, verified)
4. Hierarchical Structure: Entries can reference parent entries for problem decomposition

WHY THIS MATTERS:
----------------
For a collective to be truly intelligent, its members cannot be stateless entities
operating in a vacuum. The Blackboard enables collective consciousness - agents
contribute to and draw from a shared pool of knowledge, successes, and failures.

EXAMPLE USE CASE:
----------------
1. Orchestrator posts "task: solve_integral" entry
2. Integration Specialist subscribes to "task" tag
3. Integration Specialist posts "partial_result: needs_substitution" as child
4. Algebra Specialist (subscribed to "partial_result") gets notified
5. Algebra Specialist posts "lemma: substitution_u=sin(x)"
6. Integration Specialist retrieves lemma and completes integral
"""

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional, Set
from datetime import datetime
from enum import Enum
import logging
import threading
import uuid
import json

logger = logging.getLogger('symbo_agentic_reasoners.phase0.blackboard')

# Import OMDoc types for content
from symbo_agentic_reasoners.core.omdoc_schema import OMObject, OMDocStatement


class EntryStatus(Enum):
    """
    Lifecycle status of a Blackboard entry

    PENDING: Entry created, not yet being worked on
    IN_PROGRESS: Agent is actively working on this entry
    COMPLETED: Entry has been successfully completed
    FAILED: Attempt to complete entry failed
    VERIFIED: Entry has been verified by verification agent

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 202-208
    """
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    VERIFIED = 'verified'


class EntryType(Enum):
    """
    Types of Blackboard entries

    TASK: High-level problem to solve
    SUBTASK: Decomposed sub-problem
    LEMMA: Intermediate mathematical result
    PARTIAL_RESULT: Work-in-progress solution
    PROOF_STEP: Individual step in a proof
    VERIFICATION_REQUEST: Request for verification
    HYPOTHESIS: Conjecture or hypothesis to test
    """
    TASK = 'task'
    SUBTASK = 'subtask'
    LEMMA = 'lemma'
    PARTIAL_RESULT = 'partial_result'
    PROOF_STEP = 'proof_step'
    VERIFICATION_REQUEST = 'verification_request'
    HYPOTHESIS = 'hypothesis'


@dataclass
class BlackboardEntry:
    """
    Single entry on the Blackboard

    Represents a unit of work, knowledge, or result posted to the collective workspace.

    FIELDS:
    ------
    - entry_id: Unique identifier (auto-generated UUID)
    - entry_type: Type of entry (task, lemma, partial_result, etc.)
    - content: Mathematical content as OMDoc object
    - author_agent: Agent who posted this entry
    - status: Current lifecycle status
    - conversation_id: Link to FIPA-ACL conversation thread
    - tags: List of tags for subscription matching
    - parent_entry: Reference to parent entry (for hierarchical decomposition)
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update
    - metadata: Additional key-value pairs

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: Lines 210-221
    """
    entry_id: str
    entry_type: EntryType
    content: Any                     # OMDoc object (OMObject, OMDocStatement, etc.)
    author_agent: str                # Agent who posted
    status: EntryStatus
    conversation_id: str             # Link to FIPA-ACL conversation thread

    # Optional fields
    tags: List[str] = field(default_factory=list)  # For subscription matching
    parent_entry: Optional[str] = None  # For hierarchical problem decomposition
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_status(self, new_status: EntryStatus):
        """Update entry status and timestamp"""
        self.status = new_status
        self.updated_at = datetime.now()

    def add_tag(self, tag: str):
        """Add a tag to this entry"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def serialize(self) -> dict:
        """Serialize to JSON-compatible dictionary"""
        return {
            'entry_id': self.entry_id,
            'entry_type': self.entry_type.value,
            'content': self.content.serialize() if hasattr(self.content, 'serialize') else self.content,
            'author_agent': self.author_agent,
            'status': self.status.value,
            'conversation_id': self.conversation_id,
            'tags': self.tags,
            'parent_entry': self.parent_entry,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

    def __repr__(self) -> str:
        """Human-readable representation"""
        tags_str = f" tags={self.tags}" if self.tags else ""
        parent_str = f" parent={self.parent_entry[:8]}..." if self.parent_entry else ""
        return (f"Entry[{self.entry_id[:8]}...] {self.entry_type.value}:{self.status.value} "
                f"by {self.author_agent}{tags_str}{parent_str}")


@dataclass
class Subscription:
    """
    Agent subscription to Blackboard updates

    Agents subscribe to specific tags and receive notifications when
    matching entries are posted.

    FIELDS:
    ------
    - subscription_id: Unique identifier
    - agent_id: Subscribing agent identifier
    - tags: List of tags to match (OR logic)
    - callback: Function to call when matching entry is posted
    - active: Whether subscription is currently active
    """
    subscription_id: str
    agent_id: str
    tags: List[str]
    callback: Callable[[BlackboardEntry], None]
    active: bool = True


class Blackboard:
    """
    Centralized Blackboard with Publish-Subscribe mechanism

    The Blackboard is the shared workspace for active collaboration. Agents post
    entries containing partial results, lemmas, and failed attempts. Other agents
    subscribe to relevant updates and get notified when new entries match their interests.

    This enables emergent parallel problem-solving without explicit orchestration.

    THREAD SAFETY:
    -------------
    All operations are protected by a reentrant lock (threading.RLock) to ensure
    thread-safe access from multiple agents.

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: Lines 223-249
    """

    def __init__(self):
        """Initialize empty Blackboard"""
        self._entries: Dict[str, BlackboardEntry] = {}
        self._subscriptions: Dict[str, List[Subscription]] = {}  # tag -> subscriptions
        self._agent_subscriptions: Dict[str, List[str]] = {}  # agent_id -> subscription_ids
        self._lock = threading.RLock()

    def post(self, entry: BlackboardEntry) -> str:
        """
        Post entry to Blackboard and notify subscribers

        Args:
            entry: BlackboardEntry to post

        Returns:
            str: Entry ID of posted entry

        Reference:
            Phase_0_Build_Order_Breakdown.md: Lines 229-234
        """
        with self._lock:
            # Store entry
            self._entries[entry.entry_id] = entry

            # Notify subscribers
            self._notify_subscribers(entry)

            return entry.entry_id

    def subscribe(self, agent_id: str, tags: List[str],
                  callback: Callable[[BlackboardEntry], None]) -> str:
        """
        Subscribe to entries matching tags (FIPA-Subscribe pattern)

        When an entry is posted with a tag matching any of the subscription tags,
        the callback function will be invoked with the entry.

        Args:
            agent_id: Agent subscribing
            tags: List of tags to match (OR logic: matches any tag)
            callback: Function to call with matching entries

        Returns:
            str: Subscription ID (for later unsubscribe)

        Reference:
            Phase_0_Build_Order_Breakdown.md: Lines 236-242
        """
        with self._lock:
            subscription_id = str(uuid.uuid4())
            subscription = Subscription(
                subscription_id=subscription_id,
                agent_id=agent_id,
                tags=tags,
                callback=callback
            )

            # Index by each tag
            for tag in tags:
                if tag not in self._subscriptions:
                    self._subscriptions[tag] = []
                self._subscriptions[tag].append(subscription)

            # Track agent's subscriptions
            if agent_id not in self._agent_subscriptions:
                self._agent_subscriptions[agent_id] = []
            self._agent_subscriptions[agent_id].append(subscription_id)

            return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Cancel a subscription

        Args:
            subscription_id: Subscription to cancel

        Returns:
            bool: True if subscription was found and cancelled
        """
        with self._lock:
            # Find and deactivate subscription
            for tag, subscriptions in self._subscriptions.items():
                for sub in subscriptions:
                    if sub.subscription_id == subscription_id:
                        sub.active = False
                        return True
            return False

    def _notify_subscribers(self, entry: BlackboardEntry):
        """
        Notify all subscribers whose tags match entry

        Invokes callback functions for all active subscriptions matching
        any of the entry's tags.

        Args:
            entry: Entry that was just posted

        Reference:
            Phase_0_Build_Order_Breakdown.md: Lines 244-249
        """
        notified_subscriptions: Set[str] = set()  # Avoid duplicate notifications

        for tag in entry.tags:
            if tag in self._subscriptions:
                for subscription in self._subscriptions[tag]:
                    # Only notify once per subscription, even if multiple tags match
                    if (subscription.active and
                        subscription.subscription_id not in notified_subscriptions):
                        try:
                            subscription.callback(entry)
                            notified_subscriptions.add(subscription.subscription_id)
                        except Exception as e:
                            logger.warning(f"Subscription callback failed for {subscription.agent_id}: {type(e).__name__}: {e}")

    def get_entry(self, entry_id: str) -> Optional[BlackboardEntry]:
        """
        Retrieve entry by ID

        Args:
            entry_id: Entry identifier

        Returns:
            BlackboardEntry or None if not found
        """
        with self._lock:
            return self._entries.get(entry_id)

    def update_entry_status(self, entry_id: str, new_status: EntryStatus) -> bool:
        """
        Update status of an entry and notify subscribers

        Args:
            entry_id: Entry to update
            new_status: New status

        Returns:
            bool: True if entry was found and updated
        """
        with self._lock:
            if entry_id in self._entries:
                entry = self._entries[entry_id]
                entry.update_status(new_status)
                # Re-notify subscribers about status change
                self._notify_subscribers(entry)
                return True
            return False

    def query_entries(self, tags: Optional[List[str]] = None,
                     status: Optional[EntryStatus] = None,
                     entry_type: Optional[EntryType] = None,
                     author_agent: Optional[str] = None) -> List[BlackboardEntry]:
        """
        Query entries matching criteria

        Args:
            tags: Match entries with any of these tags (OR logic)
            status: Match entries with this status
            entry_type: Match entries of this type
            author_agent: Match entries by this agent

        Returns:
            List of matching BlackboardEntry objects
        """
        with self._lock:
            results = list(self._entries.values())

            # Filter by tags (OR logic)
            if tags:
                results = [e for e in results if any(t in e.tags for t in tags)]

            # Filter by status
            if status:
                results = [e for e in results if e.status == status]

            # Filter by entry type
            if entry_type:
                results = [e for e in results if e.entry_type == entry_type]

            # Filter by author
            if author_agent:
                results = [e for e in results if e.author_agent == author_agent]

            return results

    def get_children(self, parent_entry_id: str) -> List[BlackboardEntry]:
        """
        Get all child entries of a parent entry

        Useful for hierarchical problem decomposition where tasks spawn subtasks.

        Args:
            parent_entry_id: Parent entry ID

        Returns:
            List of child BlackboardEntry objects
        """
        with self._lock:
            return [e for e in self._entries.values() if e.parent_entry == parent_entry_id]

    def get_conversation_entries(self, conversation_id: str) -> List[BlackboardEntry]:
        """
        Get all entries belonging to a conversation thread

        Args:
            conversation_id: FIPA-ACL conversation ID

        Returns:
            List of BlackboardEntry objects in this conversation
        """
        with self._lock:
            return [e for e in self._entries.values() if e.conversation_id == conversation_id]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get Blackboard statistics

        Returns:
            Dictionary with statistics about entries and subscriptions
        """
        with self._lock:
            status_counts = {}
            for status in EntryStatus:
                status_counts[status.value] = len([e for e in self._entries.values() if e.status == status])

            type_counts = {}
            for entry_type in EntryType:
                type_counts[entry_type.value] = len([e for e in self._entries.values() if e.entry_type == entry_type])

            active_subscriptions = sum(
                len([s for s in subs if s.active])
                for subs in self._subscriptions.values()
            )

            return {
                'total_entries': len(self._entries),
                'status_distribution': status_counts,
                'type_distribution': type_counts,
                'total_subscriptions': active_subscriptions,
                'subscribed_agents': len(self._agent_subscriptions)
            }

    def clear(self):
        """Clear all entries (for testing)"""
        with self._lock:
            self._entries.clear()

    def __repr__(self) -> str:
        """Human-readable representation"""
        stats = self.get_statistics()
        return (f"Blackboard(entries={stats['total_entries']}, "
                f"subscriptions={stats['total_subscriptions']})")


# Helper function for creating entries

def create_entry(entry_type: EntryType, content: Any, author_agent: str,
                conversation_id: str, tags: List[str] = None,
                parent_entry: Optional[str] = None,
                metadata: Dict[str, Any] = None,
                status: EntryStatus = EntryStatus.PENDING) -> BlackboardEntry:
    """
    Helper function to create a BlackboardEntry

    Args:
        entry_type: Type of entry
        content: OMDoc content
        author_agent: Agent posting the entry
        conversation_id: FIPA-ACL conversation ID
        tags: Tags for subscription matching
        parent_entry: Parent entry ID (for hierarchy)
        metadata: Additional metadata
        status: Initial status (default: PENDING)

    Returns:
        BlackboardEntry ready to be posted
    """
    return BlackboardEntry(
        entry_id=str(uuid.uuid4()),
        entry_type=entry_type,
        content=content,
        author_agent=author_agent,
        status=status,
        conversation_id=conversation_id,
        tags=tags or [],
        parent_entry=parent_entry,
        metadata=metadata or {}
    )


if __name__ == "__main__":
    """Demonstration of Blackboard functionality"""
    print("=" * 80)
    print("PHASE 0 - STEP 3: Blackboard Active Memory Architecture")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.omdoc_schema import create_variable, create_operation, MathOperator

    # Create Blackboard
    blackboard = Blackboard()
    print(f"Initialized: {blackboard}")
    print()

    # Example 1: Post a task entry
    print("Example 1: Posting a task entry")
    task_content = create_operation(MathOperator.INT,
                                    create_operation(MathOperator.POWER,
                                                    create_variable('x'),
                                                    create_variable('2')),
                                    create_variable('x'))
    task_entry = create_entry(
        entry_type=EntryType.TASK,
        content=task_content,
        author_agent='orchestrator',
        conversation_id='conv_12345',
        tags=['integration', 'task', 'polynomial']
    )
    blackboard.post(task_entry)
    print(f"  Posted: {task_entry}")
    print()

    # Example 2: Subscribe to updates
    print("Example 2: Agent subscribes to 'integration' tag")
    notifications_received = []

    def integration_callback(entry: BlackboardEntry):
        notifications_received.append(entry)
        print(f"  📬 Integration Agent notified: {entry}")

    sub_id = blackboard.subscribe(
        agent_id='integration_specialist_001',
        tags=['integration'],
        callback=integration_callback
    )
    print(f"  Subscription created: {sub_id[:8]}...")
    print()

    # Example 3: Post another entry and trigger notification
    print("Example 3: Posting partial result triggers notification")
    partial_result = create_entry(
        entry_type=EntryType.PARTIAL_RESULT,
        content=create_variable('needs_substitution'),
        author_agent='integration_specialist_001',
        conversation_id='conv_12345',
        tags=['integration', 'partial_result'],
        parent_entry=task_entry.entry_id
    )
    blackboard.post(partial_result)
    print(f"  Notifications received: {len(notifications_received)}")
    print()

    # Example 4: Query entries
    print("Example 4: Query entries by tag")
    integration_entries = blackboard.query_entries(tags=['integration'])
    print(f"  Found {len(integration_entries)} entries with 'integration' tag:")
    for entry in integration_entries:
        print(f"    - {entry}")
    print()

    # Example 5: Statistics
    print("Example 5: Blackboard statistics")
    stats = blackboard.get_statistics()
    print(f"  {json.dumps(stats, indent=2)}")
    print()

    print("✓ Blackboard Active Memory Architecture implementation complete")
    print("  - Centralized workspace for collaboration ✓")
    print("  - Publish-Subscribe mechanism ✓")
    print("  - Entry status tracking ✓")
    print("  - Hierarchical problem decomposition ✓")
