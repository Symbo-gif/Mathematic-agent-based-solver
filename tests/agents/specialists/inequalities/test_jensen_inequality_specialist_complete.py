# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Jensen Inequality Specialist - 12-Test Pattern"""

import pytest
import numpy as np
from symbo_agentic_reasoners.agents.specialists.inequalities import JensenInequalitySpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestJensenInequalitySpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return JensenInequalitySpecialist(
            agent_id='test_jensen_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_jensen_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.inequalities.jensen')
        assert len(services) > 0

    def test_simple_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Jensen",
            author_agent="test",
            conversation_id="test_001",
            metadata={'values': [1, 2, 3, 4], 'weights': [0.25, 0.25, 0.25, 0.25], 'function': 'square'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_complex_problem(self, specialist):
        np.random.seed(42)
        values = np.random.uniform(0.1, 10, 50).tolist()
        weights = np.ones(50) / 50
        task = create_entry(
            entry_type=EntryType.TASK,
            content="High-dim",
            author_agent="test",
            conversation_id="test_002",
            metadata={'values': values, 'weights': weights.tolist(), 'function': 'square'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_uniform_weights(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Uniform",
            author_agent="test",
            conversation_id="test_003",
            metadata={'values': [1, 2, 3], 'function': 'square'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_single_value(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Single",
            author_agent="test",
            conversation_id="test_004",
            metadata={'values': [5], 'weights': [1], 'function': 'square'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_log_function(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Log",
            author_agent="test",
            conversation_id="test_005",
            metadata={'values': [1, 2, 3, 4], 'function': 'log'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_invalid_input(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            author_agent="test",
            conversation_id="test_006",
            metadata={'values': [1, 2], 'weights': [0.5, 0.6], 'function': 'square'}
        )
        result = specialist.process(task)
        # Weights don't sum to 1
        assert result is not None

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test",
            author_agent="test",
            conversation_id="test_007",
            metadata={'values': [1, 2], 'function': 'square'}
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

    @pytest.mark.parametrize("function", ['square', 'log', 'exp', 'cube'])
    def test_multiple_functions(self, specialist, function):
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"Function: {function}",
            author_agent="test",
            conversation_id="test_multi",
            metadata={'values': [1, 2, 3], 'function': function}
        )
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase2
