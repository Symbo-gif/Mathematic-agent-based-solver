# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Subgradient Specialist - 12-Test Pattern"""

import pytest
import numpy as np
from symbo_agentic_reasoners.agents.specialists.inequalities import SubgradientSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestSubgradientSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return SubgradientSpecialist(
            agent_id='test_subgrad_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_subgrad_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.convexity.subgradient')
        assert len(services) > 0

    def test_simple_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Subgradient",
            author_agent="test",
            conversation_id="test_001",
            metadata={'function': 'abs', 'point': [0], 'operation': 'compute_subgradient'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_complex_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="L1 norm",
            author_agent="test",
            conversation_id="test_002",
            metadata={'function': 'l1_norm', 'point': [0, 0, 0], 'operation': 'subdifferential'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_smooth_point(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Smooth",
            author_agent="test",
            conversation_id="test_003",
            metadata={'function': 'x^2', 'point': [2], 'operation': 'compute_subgradient'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_kink(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Kink at zero",
            author_agent="test",
            conversation_id="test_004",
            metadata={'function': 'abs', 'point': [0], 'operation': 'subdifferential'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_max_function(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Max",
            author_agent="test",
            conversation_id="test_005",
            metadata={'function': 'max', 'point': [1, 2], 'operation': 'subdifferential'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_invalid_input(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            author_agent="test",
            conversation_id="test_006",
            metadata={'function': None, 'operation': 'compute_subgradient'}
        )
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test",
            author_agent="test",
            conversation_id="test_007",
            metadata={'function': 'abs', 'point': [1], 'operation': 'compute_subgradient'}
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

    @pytest.mark.parametrize("function", ['abs', 'l1_norm', 'max', 'huber'])
    def test_multiple_functions(self, specialist, function):
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"{function}",
            author_agent="test",
            conversation_id="test_multi",
            metadata={'function': function, 'point': [0], 'operation': 'compute_subgradient'}
        )
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase2
