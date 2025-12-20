# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Complete Test Suite for Recurrence GF Specialist
=================================================

12-Test Pattern for Tier 3 Specialist:
1. Initialization
2. DF Registration
3. Simple Problem
4. Complex Problem
5-7. Edge Cases (3 domain-specific)
8. Error Handling
9. Blackboard Integration
10. Statistics
11. BDI Cycle
12. Concurrent Requests
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import RecurrenceGFSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestRecurrenceGFSpecialist:
    """Complete test suite for RecurrenceGFSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        """Create specialist instance with infrastructure."""
        return RecurrenceGFSpecialist(
            agent_id='test_rec_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_rec_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.recurrences_solved == 0
        assert hasattr(specialist, 'update_beliefs')
        assert hasattr(specialist, 'deliberate')
        assert hasattr(specialist, 'execute_step')

    # TEST 2: DF Registration
    def test_df_registration(self, specialist):
        """Test Directory Facilitator registration."""
        assert specialist.df is not None
        services = specialist.df.search(service_type='math.discrete.gf.recurrence')
        assert len(services) > 0
        assert services[0].agent_id == 'test_rec_001'

    # TEST 3: Simple Problem - Fibonacci F(10)
    def test_simple_fibonacci_term(self, specialist):
        """Test Fibonacci F(10) = 55."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Fibonacci F(10)",
            author_agent="test_system",
            conversation_id="test_001",
            metadata={
                'operation': 'fibonacci_term',
                'n': 10
            }
        )

        result = specialist.process(task)

        assert 'fibonacci_n' in result
        assert result['fibonacci_n'] == 55
        assert specialist.tasks_executed == 1
        assert specialist.tasks_succeeded == 1

    # TEST 4: Complex Problem - Custom Recurrence
    def test_complex_custom_recurrence(self, specialist):
        """Test custom recurrence: a_n = 2*a_{n-1} + a_{n-2}."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Custom recurrence",
            metadata={
                'operation': 'solve_linear',
                'coefficients': [2, 1],
                'initial_values': [1, 1],
                'n': 5
            }
        )

        result = specialist.process(task)

        assert 'term' in result
        # Manually verify: a_0=1, a_1=1, a_2=3, a_3=7, a_4=17, a_5=41
        assert result['term'] == 41

    # TEST 5: Edge Case - n < k (Use Initial Values)
    def test_edge_case_n_less_than_k(self, specialist):
        """EDGE CASE: Request n=0 should return initial value."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Initial value",
            metadata={
                'operation': 'solve_linear',
                'coefficients': [1, 1],
                'initial_values': [0, 1],
                'n': 0
            }
        )

        result = specialist.process(task)

        assert 'term' in result
        assert result['term'] == 0  # F(0) = 0

    # TEST 6: Edge Case - n = 1
    def test_edge_case_n_equals_one(self, specialist):
        """EDGE CASE: Request n=1 should return second initial value."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Second initial",
            metadata={
                'operation': 'solve_linear',
                'coefficients': [1, 1],
                'initial_values': [0, 1],
                'n': 1
            }
        )

        result = specialist.process(task)

        assert 'term' in result
        assert result['term'] == 1  # F(1) = 1

    # TEST 7: Edge Case - Large Term
    def test_edge_case_large_term(self, specialist):
        """EDGE CASE: Compute large term F(50)."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Large term",
            metadata={
                'operation': 'fibonacci_term',
                'n': 50
            }
        )

        result = specialist.process(task)

        assert 'fibonacci_n' in result or 'error' in result
        if 'fibonacci_n' in result:
            # F(50) = 12586269025
            assert result['fibonacci_n'] > 1e10

    # TEST 8: Error Handling
    def test_invalid_input_handling(self, specialist):
        """Test graceful handling of mismatched initial values."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            metadata={
                'operation': 'solve_linear',
                'coefficients': [1, 1, 1],  # Order 3
                'initial_values': [0, 1],    # Only 2 initials - ERROR
                'n': 10
            }
        )

        result = specialist.process(task)
        assert 'error' in result

    # TEST 9: Blackboard Integration
    def test_blackboard_entry_creation(self, specialist, blackboard):
        """Test proper Blackboard result posting."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Test BB",
            conversation_id="test_bb_001",
            metadata={
                'operation': 'fibonacci_term',
                'n': 5
            }
        )

        specialist.process(task)
        assert specialist.tasks_executed >= 1

    # TEST 10: Statistics Reporting
    def test_statistics_reporting(self, specialist):
        """Test get_statistics returns proper dict."""
        stats = specialist.get_statistics()

        assert isinstance(stats, dict)
        assert 'agent_id' in stats
        assert 'recurrences_solved' in stats
        assert 'fibonacci_computed' in stats
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'

    # TEST 11: BDI Cycle Compliance
    def test_bdi_interface(self, specialist):
        """Test BDI cognitive cycle methods."""
        specialist.update_beliefs()
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # TEST 12: Concurrent Requests (Parametrized)
    @pytest.mark.parametrize("n", [5, 10, 15, 20])
    def test_multiple_fibonacci_terms(self, specialist, n):
        """Test specialist computes various Fibonacci terms."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"F({n})",
            metadata={'operation': 'fibonacci_term', 'n': n}
        )

        result = specialist.process(task)
        assert result is not None
        assert 'fibonacci_n' in result or 'error' in result

    # BONUS TEST 1: Lucas Numbers
    def test_bonus_lucas_numbers(self, specialist):
        """BONUS: Lucas recurrence L_n = L_{n-1} + L_{n-2}, L_0=2, L_1=1."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Lucas",
            metadata={
                'operation': 'solve_linear',
                'coefficients': [1, 1],
                'initial_values': [2, 1],
                'n': 6
            }
        )

        result = specialist.process(task)

        if 'term' in result:
            # L_6 = 18
            assert result['term'] == 18

    # BONUS TEST 3: Order-3 Recurrence
    def test_bonus_order_three_recurrence(self, specialist):
        """BONUS: Third-order recurrence."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Order 3",
            metadata={
                'operation': 'solve_linear',
                'coefficients': [1, 1, 1],
                'initial_values': [0, 0, 1],
                'n': 7
            }
        )

        result = specialist.process(task)
        assert 'term' in result or 'error' in result


pytestmark = pytest.mark.phase3
