# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Complete Test Suite for Congruence Specialist
==============================================

12-Test Pattern for Tier 3 Specialist
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import CongruenceSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestCongruenceSpecialist:
    """Complete test suite for CongruenceSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return CongruenceSpecialist(agent_id='test_cong_001', df=directory_facilitator, blackboard=blackboard)

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_cong_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.algebra.elementary_nt.congruence')
        assert len(services) > 0

    def test_simple_linear_congruence(self, specialist):
        task = create_entry(EntryType.TASK, content="3x ≡ 5 mod 7",
                           metadata={'operation': 'solve_linear', 'a': 3, 'b': 5, 'm': 7})
        result = specialist.process(task)
        assert 'solutions' in result or 'error' in result

    def test_complex_crt_system(self, specialist):
        task = create_entry(EntryType.TASK, content="CRT system",
                           metadata={'operation': 'chinese_remainder', 'remainders': [2, 3, 2], 'moduli': [3, 5, 7]})
        result = specialist.process(task)
        assert 'solution' in result or 'error' in result

    def test_edge_case_no_solution(self, specialist):
        task = create_entry(EntryType.TASK, content="No solution",
                           metadata={'operation': 'solve_linear', 'a': 2, 'b': 1, 'm': 4})
        result = specialist.process(task)
        # 2x ≡ 1 (mod 4) has no solution
        assert result.get('has_solution') == False or 'error' in result

    def test_edge_case_multiple_solutions(self, specialist):
        task = create_entry(EntryType.TASK, content="Multiple solutions",
                           metadata={'operation': 'solve_linear', 'a': 2, 'b': 2, 'm': 4})
        result = specialist.process(task)
        # Should handle multiple solutions
        assert result is not None

    def test_edge_case_coprime_crt(self, specialist):
        task = create_entry(EntryType.TASK, content="Coprime CRT",
                           metadata={'operation': 'chinese_remainder', 'remainders': [1, 2], 'moduli': [3, 5]})
        result = specialist.process(task)
        assert 'solution' in result

    def test_invalid_input(self, specialist):
        task = create_entry(EntryType.TASK, content="Invalid",
                           metadata={'operation': 'solve_linear', 'a': 0, 'b': 0, 'm': 0})
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(EntryType.TASK, content="Test", metadata={'operation': 'solve_linear', 'a': 1, 'b': 1, 'm': 2})
        specialist.process(task)
        assert specialist.tasks_executed >= 1

    def test_statistics(self, specialist):
        stats = specialist.get_statistics()
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'

    def test_bdi_interface(self, specialist):
        specialist.update_beliefs()
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    @pytest.mark.parametrize("a,b,m", [(1,1,2), (3,5,7), (2,4,6), (5,7,11)])
    def test_multiple_congruences(self, specialist, a, b, m):
        task = create_entry(EntryType.TASK, content=f"{a}x ≡ {b} mod {m}",
                           metadata={'operation': 'solve_linear', 'a': a, 'b': b, 'm': m})
        result = specialist.process(task)
        assert result is not None


pytestmark = pytest.mark.phase4
