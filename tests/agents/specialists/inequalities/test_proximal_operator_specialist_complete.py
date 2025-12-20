# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Proximal Operator Specialist - 12-Test Pattern"""

import pytest
import numpy as np
from symbo_agentic_reasoners.agents.specialists.inequalities import ProximalOperatorSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestProximalOperatorSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return ProximalOperatorSpecialist(
            agent_id='test_prox_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_prox_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.convexity.proximal')
        assert len(services) > 0

    def test_simple_problem(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Prox L1",
            author_agent="test",
            conversation_id="test_001",
            metadata={'function': 'l1', 'point': [2, -3, 1], 'lambda': 1, 'operation': 'prox'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_complex_problem(self, specialist):
        np.random.seed(42)
        point = np.random.randn(100).tolist()
        task = create_entry(
            entry_type=EntryType.TASK,
            content="High-dim",
            author_agent="test",
            conversation_id="test_002",
            metadata={'function': 'l1', 'point': point, 'lambda': 0.5, 'operation': 'prox'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_lambda_zero(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Lambda=0",
            author_agent="test",
            conversation_id="test_003",
            metadata={'function': 'l1', 'point': [1, 2, 3], 'lambda': 0, 'operation': 'prox'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_l2_prox(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="L2",
            author_agent="test",
            conversation_id="test_004",
            metadata={'function': 'l2', 'point': [3, 4], 'lambda': 1, 'operation': 'prox'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_edge_case_soft_threshold(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Soft threshold",
            author_agent="test",
            conversation_id="test_005",
            metadata={'function': 'l1', 'point': [2, -1, 0.5], 'lambda': 0.8, 'operation': 'prox'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_invalid_input(self, specialist):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            author_agent="test",
            conversation_id="test_006",
            metadata={'function': 'unknown', 'point': [1], 'operation': 'prox'}
        )
        result = specialist.process(task)
        assert result is not None

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test",
            author_agent="test",
            conversation_id="test_007",
            metadata={'function': 'l1', 'point': [1, 2], 'lambda': 1, 'operation': 'prox'}
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

    @pytest.mark.parametrize("lambda_val", [0.1, 0.5, 1.0, 2.0])
    def test_multiple_lambdas(self, specialist, lambda_val):
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"Lambda={lambda_val}",
            author_agent="test",
            conversation_id="test_multi",
            metadata={'function': 'l1', 'point': [3, -2, 1], 'lambda': lambda_val, 'operation': 'prox'}
        )
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase2
