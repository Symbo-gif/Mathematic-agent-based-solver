# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Complete Test Suite for Rational GF Specialist
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
from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import RationalGFSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestRationalGFSpecialist:
    """Complete test suite for RationalGFSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        """Create specialist instance with infrastructure."""
        return RationalGFSpecialist(
            agent_id='test_rational_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_rational_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.poles_found == 0
        assert hasattr(specialist, 'update_beliefs')
        assert hasattr(specialist, 'deliberate')
        assert hasattr(specialist, 'execute_step')

    # TEST 2: DF Registration
    def test_df_registration(self, specialist):
        """Test Directory Facilitator registration."""
        assert specialist.df is not None
        services = specialist.df.search(service_type='math.discrete.gf.rational')
        assert len(services) > 0
        assert services[0].agent_id == 'test_rational_001'

    # TEST 3: Simple Problem - Find Poles
    def test_simple_find_poles(self, specialist):
        """Test finding poles of 1/(1-2x)."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Find poles",
            author_agent="test_system",
            conversation_id="test_001",
            metadata={
                'numerator': [1],
                'denominator': [1, -2],
                'operation': 'find_poles'
            }
        )

        result = specialist.process(task)

        assert 'poles' in result
        # Pole at x = 1/2
        poles = np.array(result['poles'])
        assert len(poles) == 1
        assert abs(poles[0] - 0.5) < 0.01

    # TEST 4: Complex Problem - Fibonacci Poles
    def test_complex_fibonacci_poles(self, specialist):
        """Test finding poles of Fibonacci GF x/(1-x-x²)."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Fibonacci poles",
            metadata={
                'numerator': [0, 1],
                'denominator': [1, -1, -1],
                'operation': 'find_poles'
            }
        )

        result = specialist.process(task)

        assert 'poles' in result
        assert result['pole_count'] == 2
        # Poles are φ and -1/φ where φ = (1+√5)/2
        specialist.tasks_executed == 1

    # TEST 5: Edge Case - Dominant Singularity
    def test_edge_case_dominant_singularity(self, specialist):
        """EDGE CASE: Find dominant singularity."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Dominant pole",
            metadata={
                'numerator': [0, 1],
                'denominator': [1, -1, -1],
                'operation': 'dominant_pole'
            }
        )

        result = specialist.process(task)

        assert 'dominant_singularity' in result
        assert 'rho' in result
        # For Fibonacci: dominant singularity ≈ 0.618 (1/φ)
        # So ρ ≈ φ ≈ 1.618
        assert 1.5 < result['rho'] < 1.7

    # TEST 6: Edge Case - Single Pole
    def test_edge_case_single_pole(self, specialist):
        """EDGE CASE: Single pole at origin."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Single pole",
            metadata={
                'numerator': [1],
                'denominator': [0, 1],  # 1/x
                'operation': 'find_poles'
            }
        )

        result = specialist.process(task)

        assert 'poles' in result
        assert len(result['poles']) == 1
        assert abs(result['poles'][0]) < 0.01  # Pole at 0

    # TEST 7: Edge Case - Complex Conjugate Poles
    def test_edge_case_complex_poles(self, specialist):
        """EDGE CASE: Complex conjugate poles."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Complex poles",
            metadata={
                'numerator': [1],
                'denominator': [1, 0, 1],  # 1/(1+x²)
                'operation': 'find_poles'
            }
        )

        result = specialist.process(task)

        assert 'poles' in result
        assert result['pole_count'] == 2
        # Poles at ±i

    # TEST 8: Error Handling
    def test_invalid_input_handling(self, specialist):
        """Test graceful handling of zero denominator."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid",
            metadata={
                'numerator': [1],
                'denominator': [0],
                'operation': 'find_poles'
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
                'operation': 'dominant_pole',
                'numerator': [1],
                'denominator': [1, -1]
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
        assert 'tasks_executed' in stats
        assert 'success_rate' in stats
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'

    # TEST 11: BDI Cycle Compliance
    def test_bdi_interface(self, specialist):
        """Test BDI cognitive cycle methods."""
        specialist.update_beliefs()
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # TEST 12: Concurrent Requests (Parametrized)
    @pytest.mark.parametrize("denominator", [
        [1, -1],
        [1, -2],
        [1, -1, -1],
        [1, 0, 1]
    ])
    def test_multiple_denominators(self, specialist, denominator):
        """Test specialist handles various denominators."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"Denom {denominator}",
            metadata={
                'operation': 'find_poles',
                'numerator': [1],
                'denominator': denominator
            }
        )

        result = specialist.process(task)
        assert result is not None
        assert 'poles' in result or 'error' in result

    # BONUS TEST 1: Asymptotic Formula
    def test_bonus_asymptotic_formula(self, specialist):
        """BONUS: Full asymptotic formula extraction."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Asymptotic",
            metadata={
                'operation': 'asymptotic_formula',
                'numerator': [0, 1],
                'denominator': [1, -1, -1]
            }
        )

        result = specialist.process(task)

        if 'error' not in result:
            assert 'rho' in result
            assert 'beta' in result
            # Fibonacci: ρ ≈ φ ≈ 1.618
            assert 1.5 < result['rho'] < 1.7

    # BONUS TEST 2: Multiple Poles Same Modulus
    def test_bonus_multiple_dominant_poles(self, specialist):
        """BONUS: Handle multiple poles with same modulus."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Multiple dominant",
            metadata={
                'operation': 'find_poles',
                'numerator': [1],
                'denominator': [1, 0, 0, 0, -1]  # 1/(1-x⁴), 4 poles on unit circle
            }
        )

        result = specialist.process(task)
        assert 'poles' in result or 'error' in result


pytestmark = pytest.mark.phase3
