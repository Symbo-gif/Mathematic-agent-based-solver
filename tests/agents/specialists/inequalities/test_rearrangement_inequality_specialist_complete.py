# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Rearrangement Inequality Specialist - 12-Test Pattern"""

import pytest
from symbo_agentic_reasoners.agents.specialists.inequalities import RearrangementInequalitySpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestRearrangementInequalitySpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return RearrangementInequalitySpecialist(
            agent_id='test_rearr_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_rearr_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.inequalities.rearrangement')
        assert len(services) > 0

    def test_simple_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Rearrangement",
            author_agent="test",
            conversation_id="test_001",
            metadata={'sequence_a': [1, 2, 3], 'sequence_b': [4, 5, 6]}
        )
        result = specialist.process(task)
        assert result is not None

    def test_complex_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Large",
            author_agent="test",
            conversation_id="test_002",
            metadata={'sequence_a': list(range(1, 51)), 'sequence_b': list(range(51, 101))}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_equal_sequences(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Equal",
            author_agent="test",
            conversation_id="test_003",
            metadata={'sequence_a': [2, 2, 2], 'sequence_b': [2, 2, 2]}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_reverse_order(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Reverse",
            author_agent="test",
            conversation_id="test_004",
            metadata={'sequence_a': [1, 2, 3], 'sequence_b': [6, 5, 4]}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_single_element(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Single",
            author_agent="test",
            conversation_id="test_005",
            metadata={'sequence_a': [5], 'sequence_b': [10]}
        )
        result = specialist.process(task)
        assert result is not None

    def test_invalid_input(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            author_agent="test",
            conversation_id="test_006",
            metadata={'sequence_a': [1, 2], 'sequence_b': [1, 2, 3]}
        )
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test",
            author_agent="test",
            conversation_id="test_007",
            metadata={'sequence_a': [1, 2], 'sequence_b': [3, 4]}
        )
        specialist.process(task)
        assert specialist.tasks_executed >= 1

    def test_statistics(self, specialist):
        stats = specialist.get_statistics()
        assert stats['tier'] == '3'

    def test_bdi_interface(self, specialist):
        specialist.update_beliefs()
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    @pytest.mark.parametrize("length", [2, 5, 10, 20])
    def test_multiple_lengths(self, specialist, length):
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"Length={length}",
            author_agent="test",
            conversation_id="test_multi",
            metadata={'sequence_a': list(range(length)), 'sequence_b': list(range(length, 2*length))}
        )
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase2
