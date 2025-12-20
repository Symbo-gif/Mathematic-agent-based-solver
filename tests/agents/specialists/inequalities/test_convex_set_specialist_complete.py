# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Convex Set Specialist - 12-Test Pattern"""

import pytest
import numpy as np
from symbo_agentic_reasoners.agents.specialists.inequalities import ConvexSetSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestConvexSetSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return ConvexSetSpecialist(
            agent_id='test_convexset_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_convexset_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.convexity.set')
        assert len(services) > 0

    def test_simple_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Convex hull",
            author_agent="test",
            conversation_id="test_001",
            metadata={'points': [[0, 0], [1, 0], [0, 1], [0.5, 0.5]], 'operation': 'convex_hull'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_complex_problem(self, specialist):
        np.random.seed(42)
        points = np.random.randn(100, 2).tolist()
        task = create_entry(
            entry_type=EntryType.TASK,
            content="100 points",
            author_agent="test",
            conversation_id="test_002",
            metadata={'points': points, 'operation': 'convex_hull'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_collinear(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Collinear",
            author_agent="test",
            conversation_id="test_003",
            metadata={'points': [[0, 0], [1, 1], [2, 2], [3, 3]], 'operation': 'convex_hull'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_triangle(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Triangle",
            author_agent="test",
            conversation_id="test_004",
            metadata={'points': [[0, 0], [1, 0], [0, 1]], 'operation': 'convex_hull'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_single_point(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Single",
            author_agent="test",
            conversation_id="test_005",
            metadata={'points': [[1, 1]], 'operation': 'convex_hull'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_invalid_input(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            author_agent="test",
            conversation_id="test_006",
            metadata={'points': [], 'operation': 'convex_hull'}
        )
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test",
            author_agent="test",
            conversation_id="test_007",
            metadata={'points': [[0, 0], [1, 0], [0, 1]], 'operation': 'convex_hull'}
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

    @pytest.mark.parametrize("n_points", [3, 5, 10, 20])
    def test_multiple_point_counts(self, specialist, n_points):
        np.random.seed(42)
        points = np.random.randn(n_points, 2).tolist()
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"{n_points} points",
            author_agent="test",
            conversation_id="test_multi",
            metadata={'points': points, 'operation': 'convex_hull'}
        )
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase2
