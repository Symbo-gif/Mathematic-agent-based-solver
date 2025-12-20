# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Lifting the Exponent Specialist - 12-Test Pattern"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import LiftingTheExponentSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestLiftingTheExponentSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return LiftingTheExponentSpecialist(agent_id='test_lte_001', df=directory_facilitator, blackboard=blackboard)

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_lte_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.algebra.elementary_nt.lte')
        assert len(services) > 0

    def test_simple_valuation(self, specialist):
        task = create_entry(EntryType.TASK, content="v_2(24)", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': 24, 'p': 2})
        result = specialist.process(task)
        assert 'valuation' in result
        # v_2(24) = v_2(8*3) = 3
        assert result['valuation'] == 3

    def test_complex_large_number(self, specialist):
        task = create_entry(EntryType.TASK, content="v_5(625)", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': 625, 'p': 5})
        result = specialist.process(task)
        # v_5(625) = v_5(5^4) = 4
        assert result.get('valuation') == 4

    def test_edge_case_coprime(self, specialist):
        task = create_entry(EntryType.TASK, content="v_3(10)", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': 10, 'p': 3})
        result = specialist.process(task)
        # gcd(10, 3) = 1, so v_3(10) = 0
        assert result.get('valuation') == 0

    def test_edge_case_zero(self, specialist):
        task = create_entry(EntryType.TASK, content="v_2(0)", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': 0, 'p': 2})
        result = specialist.process(task)
        # v_p(0) = ∞ or error
        assert result is not None

    def test_edge_case_one(self, specialist):
        task = create_entry(EntryType.TASK, content="v_2(1)", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': 1, 'p': 2})
        result = specialist.process(task)
        # v_p(1) = 0 for any p
        assert result.get('valuation') == 0

    def test_invalid_input(self, specialist):
        task = create_entry(EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': 1, 'p': 0})
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(EntryType.TASK, content="Test", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': 8, 'p': 2})
        specialist.process(task)
        assert specialist.tasks_executed >= 1

    def test_statistics(self, specialist):
        stats = specialist.get_statistics()
        assert stats['tier'] == '3'

    def test_bdi_interface(self, specialist):
        specialist.update_beliefs()
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    @pytest.mark.parametrize("n,p", [(8,2), (27,3), (125,5), (100,2)])
    def test_multiple_valuations(self, specialist, n, p):
        task = create_entry(EntryType.TASK, content=f"v_{p}({n})", author_agent="test", conversation_id="test_001", metadata={'operation': 'p_adic_valuation', 'n': n, 'p': p})
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase4
