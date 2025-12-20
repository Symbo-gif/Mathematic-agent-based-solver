# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Separation Theorem Specialist - 12-Test Pattern"""

import pytest
import numpy as np
from symbo_agentic_reasoners.agents.specialists.inequalities import SeparationTheoremSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestSeparationTheoremSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return SeparationTheoremSpecialist(
            agent_id='test_sep_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_sep_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.convexity.separation')
        assert len(services) > 0

    def test_simple_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Separate sets",
            author_agent="test",
            conversation_id="test_001",
            metadata={'set_a': [[0, 0], [1, 0]], 'set_b': [[5, 5], [6, 6]], 'operation': 'find_hyperplane'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_complex_problem(self, specialist):
        np.random.seed(42)
        set_a = (np.random.randn(20, 2) - 2).tolist()
        set_b = (np.random.randn(20, 2) + 2).tolist()
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Large sets",
            author_agent="test",
            conversation_id="test_002",
            metadata={'set_a': set_a, 'set_b': set_b, 'operation': 'find_hyperplane'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_1d_separation(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="1D",
            author_agent="test",
            conversation_id="test_003",
            metadata={'set_a': [[1], [2]], 'set_b': [[5], [6]], 'operation': 'find_hyperplane'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_touching_sets(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Touching",
            author_agent="test",
            conversation_id="test_004",
            metadata={'set_a': [[0, 0]], 'set_b': [[1, 0]], 'operation': 'find_hyperplane'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_high_dimension(self, specialist):
        np.random.seed(42)
        set_a = (np.random.randn(10, 5) - 1).tolist()
        set_b = (np.random.randn(10, 5) + 1).tolist()
        task = create_entry(
            entry_type=EntryType.TASK,
            content="5D",
            author_agent="test",
            conversation_id="test_005",
            metadata={'set_a': set_a, 'set_b': set_b, 'operation': 'find_hyperplane'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_invalid_input(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            author_agent="test",
            conversation_id="test_006",
            metadata={'set_a': [], 'set_b': [[1, 1]], 'operation': 'find_hyperplane'}
        )
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test",
            author_agent="test",
            conversation_id="test_007",
            metadata={'set_a': [[0, 0]], 'set_b': [[2, 2]], 'operation': 'find_hyperplane'}
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

    @pytest.mark.parametrize("dim", [1, 2, 3, 5])
    def test_multiple_dimensions(self, specialist, dim):
        np.random.seed(42)
        set_a = (np.random.randn(5, dim) - 1).tolist()
        set_b = (np.random.randn(5, dim) + 1).tolist()
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"{dim}D",
            author_agent="test",
            conversation_id="test_multi",
            metadata={'set_a': set_a, 'set_b': set_b, 'operation': 'find_hyperplane'}
        )
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase2
