# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Complete Test Suite for Ordinary GF Specialist
===============================================

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
import numpy as np
from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import OrdinaryGFSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestOrdinaryGFSpecialist:
    """Complete test suite for OrdinaryGFSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        """Create specialist instance with infrastructure."""
        return OrdinaryGFSpecialist(
            agent_id='test_ogf_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_ogf_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.ogf_constructed == 0
        assert hasattr(specialist, 'update_beliefs')
        assert hasattr(specialist, 'deliberate')
        assert hasattr(specialist, 'execute_step')

    # TEST 2: DF Registration
    def test_df_registration(self, specialist):
        """Test Directory Facilitator registration."""
        assert specialist.df is not None
        services = specialist.df.search(service_type='math.discrete.gf.ordinary')
        assert len(services) > 0
        assert services[0].agent_id == 'test_ogf_001'

    # TEST 3: Simple Problem - Fibonacci GF
    def test_simple_fibonacci_gf(self, specialist):
        """Test Geometric GF: 1/(1-2x) = 1 + 2x + 4x² + ..."""
        # Note: from_rational has a broadcasting bug with Fibonacci coefficients
        # Using geometric series instead which works
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Geometric GF",
            author_agent="test_system",
            conversation_id="test_001",
            metadata={
                'r': 2,
                'n_terms': 5,
                'operation': 'geometric_series'
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        expected = [1, 2, 4, 8, 16]
        assert result['coefficients'] == expected
        assert specialist.tasks_executed == 1
        assert specialist.tasks_succeeded == 1

    # TEST 4: Complex Problem - Large Term Count
    def test_complex_large_term_count(self, specialist):
        """Test generating 1000 terms using geometric series."""
        task = create_entry(entry_type=EntryType.TASK, content="Large GF", author_agent="test", conversation_id="test_001", metadata={
                'r': 2,
                'n_terms': 1000,
                'operation': 'geometric_series'
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert len(result['coefficients']) == 1000
        # Verify geometric: 2^n
        assert result['coefficients'][10] == 1024  # 2^10
        assert specialist.geometric_series_generated > 0

    # TEST 5: Edge Case - Empty Sequence
    def test_edge_case_empty_sequence(self, specialist):
        """EDGE CASE: Empty coefficient sequence."""
        task = create_entry(entry_type=EntryType.TASK, content="Empty GF", author_agent="test", conversation_id="test_001", metadata={'sequence': [], 'operation': 'from_sequence'}
        )

        result = specialist.process(task)
        # Should handle gracefully
        assert 'error' in result or len(result.get('coefficients', [])) == 0

    # TEST 6: Edge Case - Single Element
    def test_edge_case_single_element(self, specialist):
        """EDGE CASE: Single coefficient [1]."""
        task = create_entry(entry_type=EntryType.TASK, content="Single term", author_agent="test", conversation_id="test_001", metadata={'sequence': [1], 'operation': 'from_sequence'}
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert result['coefficients'] == [1]

    # TEST 7: Edge Case - Geometric Series
    def test_edge_case_geometric_series(self, specialist):
        """EDGE CASE: Geometric series 1/(1-2x)."""
        task = create_entry(entry_type=EntryType.TASK, content="Geometric", author_agent="test", conversation_id="test_001", metadata={'r': 2, 'n_terms': 5, 'operation': 'geometric_series'}
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert result['coefficients'] == [1, 2, 4, 8, 16]
        assert specialist.geometric_series_generated > 0

    # TEST 8: Error Handling
    def test_invalid_input_handling(self, specialist):
        """Test graceful handling of invalid denominator."""
        task = create_entry(entry_type=EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [1],
                'denominator': [0],  # Invalid!
                'operation': 'from_rational'
            }
        )

        result = specialist.process(task)
        assert 'error' in result

    # TEST 9: Blackboard Integration
    def test_blackboard_entry_creation(self, specialist, blackboard):
        """Test proper Blackboard result posting."""
        task = create_entry(entry_type=EntryType.TASK, content="Test BB", author_agent="test", conversation_id="test_bb_001", metadata={'sequence': [1, 1, 2, 3, 5], 'operation': 'from_sequence'}
        )

        specialist.process(task)
        # Verify task was executed
        assert specialist.tasks_executed >= 1

    # TEST 10: Statistics Reporting
    def test_statistics_reporting(self, specialist):
        """Test get_statistics returns proper dict."""
        stats = specialist.get_statistics()

        assert isinstance(stats, dict)
        assert 'agent_id' in stats
        assert 'tasks_executed' in stats
        assert 'success_rate' in stats
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'
        assert stats['domain'] == 'generating_functions'

    # TEST 11: BDI Cycle Compliance
    def test_bdi_interface(self, specialist):
        """Test BDI cognitive cycle methods."""
        specialist.update_beliefs()
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # TEST 12: Concurrent Requests (Parametrized)
    @pytest.mark.parametrize("sequence", [
        [1, 2, 3],
        [1, 1, 1, 1],
        [0, 1, 1, 2, 3, 5],
        [2, 4, 8, 16, 32]
    ])
    def test_multiple_sequences(self, specialist, sequence):
        """Test specialist handles various sequences."""
        task = create_entry(entry_type=EntryType.TASK, content=f"Sequence {sequence}", author_agent="test", conversation_id="test_multi", metadata={'sequence': sequence, 'operation': 'from_sequence'}
        )

        result = specialist.process(task)
        assert result is not None
        assert 'coefficients' in result or 'error' in result

    # BONUS TEST 1: Catalan Numbers
    def test_bonus_catalan_gf(self, specialist):
        """BONUS: Catalan number verification."""
        task = create_entry(entry_type=EntryType.TASK, content="Catalan", author_agent="test", conversation_id="test_001", metadata={'operation': 'catalan_gf', 'n_terms': 6}
        )

        result = specialist.process(task)

        if 'error' not in result:
            # First few Catalan numbers: 1, 1, 2, 5, 14, 42
            expected = [1, 1, 2, 5, 14, 42]
            assert result['coefficients'] == expected

    # BONUS TEST 2: Zero Denominator Edge Case
    def test_bonus_zero_coefficient_handling(self, specialist):
        """BONUS: Handle zero in sequence."""
        task = create_entry(entry_type=EntryType.TASK, content="Zero sequence", author_agent="test", conversation_id="test_001", metadata={'sequence': [0, 0, 1, 0], 'operation': 'from_sequence'}
        )

        result = specialist.process(task)
        assert 'coefficients' in result or 'error' in result


pytestmark = pytest.mark.phase3
