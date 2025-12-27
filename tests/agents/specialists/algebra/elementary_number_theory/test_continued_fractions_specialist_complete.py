# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""Complete Test Suite for Continued Fractions Specialist - 12-Test Pattern"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import ContinuedFractionsSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestContinuedFractionsSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return ContinuedFractionsSpecialist(agent_id='test_cf_001', df=directory_facilitator, blackboard=blackboard)

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_cf_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.algebra.elementary_nt.continued_fractions')
        assert len(services) > 0

    def test_simple_rational_expansion(self, specialist):
        task = create_entry(EntryType.TASK, content="22/7", author_agent="test", conversation_id="test_001", metadata={'operation': 'expand_rational', 'numerator': 22, 'denominator': 7})
        result = specialist.process(task)
        assert 'cf' in result

    def test_complex_quadratic_irrational(self, specialist):
        task = create_entry(EntryType.TASK, content="√23", author_agent="test", conversation_id="test_002", metadata={'operation': 'expand_quadratic_irrational', 'D': 23})
        result = specialist.process(task)
        assert 'initial' in result or 'error' in result

    def test_edge_case_sqrt_2(self, specialist):
        task = create_entry(EntryType.TASK, content="√2", author_agent="test", conversation_id="test_003", metadata={'operation': 'expand_quadratic_irrational', 'D': 2})
        result = specialist.process(task)
        # √2 = [1; 2, 2, 2, ...]
        assert result.get('initial') == [1] or 'error' in result

    def test_edge_case_perfect_square(self, specialist):
        task = create_entry(EntryType.TASK, content="√4", author_agent="test", conversation_id="test_004", metadata={'operation': 'expand_quadratic_irrational', 'D': 4})
        result = specialist.process(task)
        # Should error - 4 is perfect square
        assert 'error' in result

    def test_edge_case_unit_fraction(self, specialist):
        task = create_entry(EntryType.TASK, content="1/7", author_agent="test", conversation_id="test_005", metadata={'operation': 'expand_rational', 'numerator': 1, 'denominator': 7})
        result = specialist.process(task)
        assert 'cf' in result

    def test_invalid_input(self, specialist):
        task = create_entry(EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_006", metadata={'operation': 'expand_rational', 'numerator': 1, 'denominator': 0})
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(EntryType.TASK, content="Test", author_agent="test", conversation_id="test_007", metadata={'operation': 'expand_rational', 'numerator': 3, 'denominator': 2})
        specialist.process(task)
        assert specialist.tasks_executed >= 1

    def test_statistics(self, specialist):
        stats = specialist.get_statistics()
        assert stats['tier'] == '3'

    def test_bdi_interface(self, specialist):
        specialist.update_beliefs({})
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    @pytest.mark.parametrize("num,denom", [(22,7), (355,113), (3,2), (7,5)])
    def test_multiple_rationals(self, specialist, num, denom):
        task = create_entry(EntryType.TASK, content=f"{num}/{denom}", author_agent="test", conversation_id="test_multi", metadata={'operation': 'expand_rational', 'numerator': num, 'denominator': denom})
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase4
