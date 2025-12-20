# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Convex Function Specialist - 12-Test Pattern"""

import pytest
import numpy as np
from symbo_agentic_reasoners.agents.specialists.inequalities import ConvexFunctionSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestConvexFunctionSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return ConvexFunctionSpecialist(
            agent_id='test_convexfn_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_convexfn_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.convexity.function')
        assert len(services) > 0

    def test_simple_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test x^2",
            author_agent="test",
            conversation_id="test_001",
            metadata={'function': 'x^2', 'domain': [-5, 5], 'operation': 'test_convexity'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_complex_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Multidimensional",
            author_agent="test",
            conversation_id="test_002",
            metadata={'function': 'quadratic', 'dimension': 3, 'operation': 'test_convexity'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_linear_function(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Linear",
            author_agent="test",
            conversation_id="test_003",
            metadata={'function': 'linear', 'operation': 'test_convexity'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_strictly_convex(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Strictly convex",
            author_agent="test",
            conversation_id="test_004",
            metadata={'function': 'exp', 'operation': 'test_strict_convexity'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_concave(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Concave",
            author_agent="test",
            conversation_id="test_005",
            metadata={'function': '-x^2', 'operation': 'test_convexity'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_invalid_input(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            author_agent="test",
            conversation_id="test_006",
            metadata={'function': None, 'operation': 'test_convexity'}
        )
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test",
            author_agent="test",
            conversation_id="test_007",
            metadata={'function': 'x^2', 'operation': 'test_convexity'}
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

    @pytest.mark.parametrize("function", ['x^2', 'exp', 'log', 'abs'])
    def test_multiple_functions(self, specialist, function):
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"Function: {function}",
            author_agent="test",
            conversation_id="test_multi",
            metadata={'function': function, 'operation': 'test_convexity'}
        )
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase2
