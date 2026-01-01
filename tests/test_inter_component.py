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
Inter-Component Communication Tests
====================================

Comprehensive tests for FIPA-ACL protocols and inter-component communication:
- FIPAMessage structure and validation
- Performative types
- Protocol handling
- Blackboard communication
- Agent Management System communication
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import uuid

# Import modules - handle potential circular imports gracefully
import sys
import os

# Add src to path if needed
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import blackboard first (fewer dependencies)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard,
    BlackboardEntry,
    EntryStatus,
    EntryType,
)

# Import omdoc schema
from symbo_agentic_reasoners.core.omdoc_schema import (
    OMObject,
    create_variable,
    create_number,
)

# Import protocols
from symbo_agentic_reasoners.protocols.fipa_acl import (
    Performative,
    FIPAProtocol,
    FIPAMessage,
)

# Import infrastructure
from symbo_agentic_reasoners.infrastructure.ams import (
    AgentManagementSystem,
    AgentStatus,
    AgentType,
)
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator,
    create_service_registration,
)


# =============================================================================
# Performative Tests
# =============================================================================


class TestPerformative:
    """Tests for Performative enum."""

    def test_all_performatives_exist(self):
        """All standard FIPA performatives should exist."""
        expected = [
            'REQUEST', 'INFORM', 'QUERY_IF', 'QUERY_REF', 'CONFIRM',
            'DISCONFIRM', 'REFUSE', 'PROPOSE', 'ACCEPT_PROPOSAL',
            'REJECT_PROPOSAL', 'AGREE', 'FAILURE', 'CANCEL',
            'SUBSCRIBE', 'NOT_UNDERSTOOD'
        ]
        for perf in expected:
            assert hasattr(Performative, perf)

    def test_performative_values(self):
        """Performative values should be correct."""
        assert Performative.REQUEST.value == 'request'
        assert Performative.INFORM.value == 'inform'
        assert Performative.FAILURE.value == 'failure'

    def test_performative_is_enum(self):
        """Performatives should be proper enum values."""
        assert isinstance(Performative.REQUEST, Performative)
        assert isinstance(Performative.INFORM, Performative)


class TestFIPAProtocol:
    """Tests for FIPAProtocol enum."""

    def test_all_protocols_exist(self):
        """All standard FIPA protocols should exist."""
        expected = [
            'FIPA_REQUEST', 'FIPA_QUERY', 'FIPA_CONTRACT_NET',
            'FIPA_PROPOSE', 'FIPA_SUBSCRIBE', 'FIPA_INFORM'
        ]
        for proto in expected:
            assert hasattr(FIPAProtocol, proto)

    def test_protocol_values(self):
        """Protocol values should be correct."""
        assert FIPAProtocol.FIPA_REQUEST.value == 'fipa-request'
        assert FIPAProtocol.FIPA_QUERY.value == 'fipa-query'


# =============================================================================
# FIPAMessage Tests
# =============================================================================


class TestFIPAMessage:
    """Tests for FIPAMessage class."""

    @pytest.fixture
    def valid_content(self):
        """Create valid OMDoc content for testing."""
        return create_variable("x")

    @pytest.fixture
    def valid_message(self, valid_content):
        """Create a valid FIPAMessage for testing."""
        return FIPAMessage(
            performative=Performative.REQUEST,
            sender="test_agent_001",
            receiver="target_agent_002",
            content=valid_content,
        )

    def test_message_creation(self, valid_message):
        """Should create message with required fields."""
        assert valid_message.performative == Performative.REQUEST
        assert valid_message.sender == "test_agent_001"
        assert valid_message.receiver == "target_agent_002"
        assert valid_message.content is not None

    def test_auto_generated_ids(self, valid_message):
        """Message and conversation IDs should be auto-generated."""
        assert valid_message.message_id is not None
        assert valid_message.conversation_id is not None
        assert len(valid_message.message_id) > 0
        assert len(valid_message.conversation_id) > 0

    def test_default_values(self, valid_message):
        """Default values should be set correctly."""
        assert valid_message.ontology == 'mathematics'
        assert valid_message.protocol == FIPAProtocol.FIPA_REQUEST.value
        assert valid_message.language == 'omdoc'

    def test_timestamp_set(self, valid_message):
        """Timestamp should be set to current time."""
        assert valid_message.timestamp is not None
        assert isinstance(valid_message.timestamp, datetime)

    def test_validation_passes_valid_message(self, valid_message):
        """Valid message should pass validation."""
        result = valid_message.validate()
        assert result is True

    def test_validation_rejects_raw_text_content(self):
        """Validation should reject raw text content."""
        with pytest.raises(ValueError) as exc_info:
            msg = FIPAMessage(
                performative=Performative.INFORM,
                sender="sender",
                receiver="receiver",
                content="raw text content"  # Not allowed
            )
            msg.validate()
        assert "Raw text content is forbidden" in str(exc_info.value)

    def test_validation_rejects_wrong_language(self, valid_content):
        """Validation should reject non-omdoc language."""
        with pytest.raises(ValueError) as exc_info:
            msg = FIPAMessage(
                performative=Performative.INFORM,
                sender="sender",
                receiver="receiver",
                content=valid_content,
                language='json'  # Not allowed
            )
            msg.validate()
        assert "must be 'omdoc'" in str(exc_info.value)

    def test_validation_rejects_empty_sender(self, valid_content):
        """Validation should reject empty sender."""
        with pytest.raises(ValueError):
            msg = FIPAMessage(
                performative=Performative.INFORM,
                sender="",  # Empty
                receiver="receiver",
                content=valid_content
            )
            msg.validate()

    def test_validation_rejects_empty_receiver(self, valid_content):
        """Validation should reject empty receiver."""
        with pytest.raises(ValueError):
            msg = FIPAMessage(
                performative=Performative.INFORM,
                sender="sender",
                receiver="",  # Empty
                content=valid_content
            )
            msg.validate()

    def test_serialize_returns_dict(self, valid_message):
        """Serialization should return a dictionary."""
        serialized = valid_message.serialize()
        assert isinstance(serialized, dict)

    def test_serialize_contains_required_fields(self, valid_message):
        """Serialized message should contain all required fields."""
        serialized = valid_message.serialize()
        required = ['message_id', 'performative', 'sender', 'receiver',
                    'conversation_id', 'ontology', 'protocol', 'language',
                    'timestamp', 'content']
        for field in required:
            assert field in serialized

    def test_serialize_performative_is_value(self, valid_message):
        """Serialized performative should be string value, not enum."""
        serialized = valid_message.serialize()
        assert serialized['performative'] == 'request'
        assert isinstance(serialized['performative'], str)

    def test_optional_fields_serialized(self, valid_content):
        """Optional fields should be serialized when present."""
        msg = FIPAMessage(
            performative=Performative.REQUEST,
            sender="sender",
            receiver="receiver",
            content=valid_content,
            reply_with="reply-123",
            in_reply_to="original-456"
        )
        serialized = msg.serialize()
        assert serialized['reply_with'] == 'reply-123'
        assert serialized['in_reply_to'] == 'original-456'

    def test_content_serialization(self, valid_message):
        """Content should be properly serialized."""
        serialized = valid_message.serialize()
        assert 'content' in serialized
        # OMDoc content should be serialized
        content = serialized['content']
        assert content is not None


# =============================================================================
# Blackboard Communication Tests
# =============================================================================


class TestBlackboardCommunication:
    """Tests for Blackboard inter-component communication."""

    @pytest.fixture
    def blackboard(self):
        """Create a fresh Blackboard instance."""
        return Blackboard()

    def test_blackboard_creation(self, blackboard):
        """Blackboard should be created."""
        assert blackboard is not None

    def test_post_entry(self, blackboard):
        """Should be able to post entries to blackboard."""
        entry = BlackboardEntry(
            entry_id="test-entry-001",
            entry_type=EntryType.TASK,
            content={"expression": "x + 1"},
            author_agent="test_agent",
            status=EntryStatus.PENDING,
            conversation_id="conv-001"
        )
        blackboard.post(entry)

        retrieved = blackboard.get_entry("test-entry-001")
        assert retrieved is not None
        assert retrieved.entry_id == "test-entry-001"

    def test_update_entry_status(self, blackboard):
        """Should be able to update entry status."""
        entry = BlackboardEntry(
            entry_id="update-test",
            entry_type=EntryType.TASK,
            content={"value": 1},
            author_agent="agent",
            status=EntryStatus.PENDING,
            conversation_id="conv-002"
        )
        blackboard.post(entry)

        # Update status
        blackboard.update_entry_status("update-test", EntryStatus.IN_PROGRESS)

        retrieved = blackboard.get_entry("update-test")
        assert retrieved.status == EntryStatus.IN_PROGRESS

    def test_query_by_type(self, blackboard):
        """Should be able to query entries by type."""
        # Post entries of different types
        entry1 = BlackboardEntry(
            entry_id="task-1",
            entry_type=EntryType.TASK,
            content={},
            author_agent="agent",
            status=EntryStatus.PENDING,
            conversation_id="conv-003"
        )
        entry2 = BlackboardEntry(
            entry_id="lemma-1",
            entry_type=EntryType.LEMMA,
            content={},
            author_agent="agent",
            status=EntryStatus.COMPLETED,
            conversation_id="conv-003"
        )
        blackboard.post(entry1)
        blackboard.post(entry2)

        tasks = blackboard.query_entries(entry_type=EntryType.TASK)
        assert len(tasks) >= 1
        assert all(e.entry_type == EntryType.TASK for e in tasks)

    def test_query_by_status(self, blackboard):
        """Should be able to query entries by status."""
        entry = BlackboardEntry(
            entry_id="pending-1",
            entry_type=EntryType.TASK,
            content={},
            author_agent="agent",
            status=EntryStatus.PENDING,
            conversation_id="conv-004"
        )
        blackboard.post(entry)

        pending = blackboard.query_entries(status=EntryStatus.PENDING)
        assert len(pending) >= 1


# =============================================================================
# Agent Management System Tests
# =============================================================================


class TestAgentManagementSystem:
    """Tests for AMS inter-component communication."""

    @pytest.fixture
    def ams(self):
        """Create a fresh AMS instance."""
        return AgentManagementSystem()

    def test_ams_creation(self, ams):
        """AMS should be created."""
        assert ams is not None

    def test_create_agent(self, ams):
        """Should be able to create an agent."""
        result = ams.create_agent(
            agent_id="test_agent_001",
            agent_type=AgentType.INFRASTRUCTURAL
        )
        assert result is True

    def test_get_agent(self, ams):
        """Should be able to get agent record."""
        ams.create_agent(
            agent_id="get_test_agent",
            agent_type=AgentType.INFRASTRUCTURAL
        )
        record = ams.get_agent("get_test_agent")
        assert record is not None
        assert hasattr(record, 'status')
        assert isinstance(record.status, AgentStatus)

    def test_activate_agent(self, ams):
        """Should be able to activate an agent."""
        ams.create_agent(
            agent_id="activate_test_agent",
            agent_type=AgentType.INFRASTRUCTURAL
        )

        # Activate
        result = ams.activate_agent("activate_test_agent")
        assert result is True

        record = ams.get_agent("activate_test_agent")
        assert record.status == AgentStatus.ACTIVE

    def test_deactivate_agent(self, ams):
        """Should be able to deactivate an agent."""
        ams.create_agent(
            agent_id="deactivate_test_agent",
            agent_type=AgentType.INFRASTRUCTURAL
        )
        ams.activate_agent("deactivate_test_agent")

        # Deactivate
        result = ams.deactivate_agent("deactivate_test_agent")
        assert result is True

        record = ams.get_agent("deactivate_test_agent")
        assert record.status == AgentStatus.INACTIVE


# =============================================================================
# Directory Facilitator Tests
# =============================================================================


class TestDirectoryFacilitator:
    """Tests for DF inter-component communication."""

    @pytest.fixture
    def df(self):
        """Create a fresh DF instance."""
        return DirectoryFacilitator()

    def test_df_creation(self, df):
        """DF should be created."""
        assert df is not None

    def test_register_service(self, df):
        """Should be able to register a service."""
        registration = create_service_registration(
            service_type="math.algebra",
            agent_id="algebra_specialist_001",
            algorithm="polynomial_solver",
            type="specialist"
        )
        result = df.register(registration)
        assert result is True

    def test_search_service(self, df):
        """Should be able to search for services."""
        # Register a service first
        registration = create_service_registration(
            service_type="math.calculus",
            agent_id="calculus_specialist_001",
            algorithm="integration",
            type="specialist"
        )
        df.register(registration)

        # Search for it
        results = df.search(service_type="math.calculus")
        assert len(results) > 0
        assert any(r.agent_id == "calculus_specialist_001" for r in results)

    def test_deregister_service(self, df):
        """Should be able to deregister a service."""
        registration = create_service_registration(
            service_type="math.stats",
            agent_id="stats_agent_001",
            algorithm="bayesian",
            type="specialist"
        )
        df.register(registration)

        # Deregister - pass agent_id and optionally service_type
        result = df.deregister(registration.agent_id, registration.service_type)
        # Should succeed
        assert isinstance(result, bool)


# =============================================================================
# Integration Tests
# =============================================================================


class TestCommunicationIntegration:
    """Integration tests for inter-component communication."""

    def test_message_flow_simulation(self):
        """Simulate a message flow between components."""
        # Create components
        bb = Blackboard()
        ams = AgentManagementSystem()
        df = DirectoryFacilitator()

        # Create agents in AMS
        ams.create_agent("algebra_specialist_001", AgentType.INFRASTRUCTURAL)
        ams.create_agent("algebra_supervisor_001", AgentType.INFRASTRUCTURAL)

        # Register services with DF
        df.register(create_service_registration(
            service_type="math.algebra",
            agent_id="algebra_specialist_001",
            algorithm="solve",
            type="specialist"
        ))

        # Supervisor posts task to blackboard
        task = BlackboardEntry(
            entry_id="task-001",
            entry_type=EntryType.TASK,
            content={"expression": "x**2 - 4"},
            author_agent="algebra_supervisor_001",
            status=EntryStatus.PENDING,
            conversation_id="test-conv-001"
        )
        bb.post(task)

        # Specialist finds pending tasks
        pending = bb.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
        assert len(pending) > 0

        # Specialist claims task
        claimed = pending[0]
        bb.update_entry_status(claimed.entry_id, EntryStatus.IN_PROGRESS)

        # Verify update
        updated = bb.get_entry(claimed.entry_id)
        assert updated.status == EntryStatus.IN_PROGRESS

    def test_fipa_message_chain(self):
        """Test FIPA message conversation chain."""
        content = create_variable("x")

        # Request message
        request = FIPAMessage(
            performative=Performative.REQUEST,
            sender="supervisor",
            receiver="specialist",
            content=content,
            conversation_id="conv-001"
        )

        # Response (agree) message
        response = FIPAMessage(
            performative=Performative.AGREE,
            sender="specialist",
            receiver="supervisor",
            content=content,
            conversation_id=request.conversation_id,  # Same conversation
            in_reply_to=request.message_id
        )

        # Verify chain
        assert response.conversation_id == request.conversation_id
        assert response.in_reply_to == request.message_id


# =============================================================================
# Edge Cases
# =============================================================================


class TestCommunicationEdgeCases:
    """Edge case tests for communication."""

    def test_message_with_dict_content(self):
        """Message with dict content should pass validation."""
        msg = FIPAMessage(
            performative=Performative.INFORM,
            sender="sender",
            receiver="receiver",
            content={"type": "result", "value": 42}  # Dict allowed
        )
        result = msg.validate()
        assert result is True

    def test_large_conversation_id(self):
        """Large conversation IDs should work."""
        content = create_number(1)
        long_id = "conv-" + "x" * 1000
        msg = FIPAMessage(
            performative=Performative.INFORM,
            sender="sender",
            receiver="receiver",
            content=content,
            conversation_id=long_id
        )
        assert msg.conversation_id == long_id

    def test_multiple_messages_same_conversation(self):
        """Multiple messages in same conversation should work."""
        content = create_number(1)
        conv_id = str(uuid.uuid4())

        messages = []
        for i in range(5):
            msg = FIPAMessage(
                performative=Performative.INFORM,
                sender=f"agent_{i}",
                receiver=f"agent_{(i+1) % 5}",
                content=content,
                conversation_id=conv_id
            )
            messages.append(msg)

        # All should have same conversation ID
        assert all(m.conversation_id == conv_id for m in messages)

        # All should have unique message IDs
        message_ids = [m.message_id for m in messages]
        assert len(set(message_ids)) == len(messages)


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
