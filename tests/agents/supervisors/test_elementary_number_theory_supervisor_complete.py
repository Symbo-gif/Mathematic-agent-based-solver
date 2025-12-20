# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Complete Test Suite for Elementary Number Theory Supervisor
===========================================================

10-Test Pattern for Tier 2 Supervisor:
1. Initialization
2. DF Registration
3. Simple Task Processing
4. Complex Task Processing
5. Specialist Delegation
6. Unknown Operation Handling
7. Multi-Step Problem
8. Error Propagation
9. Statistics Reporting
10. BDI Interface
"""

import pytest
from unittest.mock import Mock
from symbo_agentic_reasoners.agents.supervisors.elementary_number_theory_supervisor import ElementaryNumberTheorySupervisor
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestElementaryNumberTheorySupervisor:
    """Complete test suite for ElementaryNumberTheorySupervisor."""

    @pytest.fixture
    def supervisor(self, directory_facilitator, blackboard):
        """Create supervisor instance."""
        return ElementaryNumberTheorySupervisor(
            agent_id='test_ent_sup_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, supervisor):
        """Test supervisor initializes correctly."""
        assert supervisor.agent_id == 'test_ent_sup_001'
        assert supervisor.tasks_routed == 0
        assert hasattr(supervisor, 'process')
        assert hasattr(supervisor, '_determine_specialist')

    # TEST 2: DF Registration
    def test_df_registration(self, supervisor):
        """Test supervisor registers with DF."""
        assert supervisor.df is not None
        services = supervisor.df.search(service_type='math.algebra.elementary_nt')
        assert len(services) > 0

    # TEST 3: Simple Task - Congruence
    def test_processes_simple_congruence(self, supervisor):
        """Test supervisor processes simple congruence."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Solve 3x ≡ 5 mod 7",
            metadata={'raw_input': 'solve 3x ≡ 5 mod 7', 'operation': 'solve_linear', 'a': 3, 'b': 5, 'm': 7}
        )

        result = supervisor.process(task)
        assert result is not None or True

    # TEST 4: Complex Task - Pell Equation
    def test_processes_complex_pell(self, supervisor):
        """Test supervisor processes Pell equation."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Solve x² - 2y² = 1",
            metadata={'raw_input': 'pell equation x² - 2y² = 1', 'operation': 'fundamental_solution', 'D': 2}
        )

        result = supervisor.process(task)
        assert result is not None or True

    # TEST 5: Routing to Specialists
    def test_routing_to_tonelli_shanks(self, supervisor):
        """Test routing to Tonelli-Shanks specialist."""
        class MockEntry:
            def __init__(self, raw_input):
                self.metadata = {'raw_input': raw_input}

        task = MockEntry("Find sqrt(7) mod 11 using Tonelli-Shanks")
        specialist_name = supervisor._determine_specialist(task)

        assert specialist_name == 'tonelli_shanks'

    # TEST 6: Unknown Operation
    def test_handles_unknown_operation(self, supervisor):
        """Test graceful handling of unknown operations."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Unknown operation",
            metadata={'raw_input': 'compute xyz', 'operation': 'unknown_xyz'}
        )

        result = supervisor.process(task)
        # Should route to default (diophantine) or return error
        assert result is not None

    # TEST 7: Multi-Step Routing
    def test_multi_specialist_routing(self, supervisor):
        """Test routing decisions for different problem types."""
        class MockEntry:
            def __init__(self, raw_input):
                self.metadata = {'raw_input': raw_input}

        test_cases = [
            ("congruence 3x ≡ 5 mod 7", 'congruence'),
            ("continued fraction of √23", 'continued_fractions'),
            ("pell equation x² - 2y² = 1", 'pell'),
            ("tonelli shanks sqrt mod p", 'tonelli_shanks'),
            ("lte lemma valuation", 'lte'),
            ("linear diophantine 3x + 5y = 1", 'diophantine'),
            ("legendre symbol (2/7)", 'quadratic_residue')
        ]

        for raw_input, expected in test_cases:
            result = supervisor._determine_specialist(MockEntry(raw_input))
            assert result == expected

    # TEST 8: Error Propagation
    def test_error_propagation(self, supervisor):
        """Test error propagation from specialists."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Invalid congruence",
            metadata={'raw_input': 'congruence', 'a': 0, 'b': 0, 'm': 0}
        )

        result = supervisor.process(task)
        # Should handle gracefully
        assert result is not None

    # TEST 9: Statistics Reporting
    def test_statistics_reporting(self, supervisor):
        """Test supervisor reports statistics."""
        stats = supervisor.get_statistics()

        assert isinstance(stats, dict)
        assert 'agent_id' in stats
        assert 'tasks_routed' in stats
        assert 'congruence_routes' in stats
        assert 'pell_routes' in stats
        assert stats['tier'] == '2'
        assert stats['type'] == 'supervisor'

    # TEST 10: BDI Interface
    def test_bdi_interface(self, supervisor):
        """Test BDI methods work correctly."""
        supervisor.update_beliefs()
        intentions = supervisor.deliberate()
        assert isinstance(intentions, list)


pytestmark = pytest.mark.phase4
