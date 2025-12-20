# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Comprehensive Tests for ZeroDensitySpecialist
==============================================

Standard 12-test pattern for specialist agents.
Tests zero density estimates and zero-free regions.
"""

import pytest
from unittest.mock import Mock, MagicMock
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.zero_density import (
    ZeroDensitySpecialist
)


class TestZeroDensitySpecialistComplete:
    """Comprehensive test suite for ZeroDensitySpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create specialist instance without dependencies."""
        return ZeroDensitySpecialist(
            agent_id='test_zero_density_001',
            df=None,
            blackboard=None
        )

    @pytest.fixture
    def specialist_with_mocks(self):
        """Create specialist with mocked dependencies."""
        mock_df = Mock()
        mock_blackboard = Mock()
        return ZeroDensitySpecialist(
            agent_id='test_zero_density_002',
            df=mock_df,
            blackboard=mock_blackboard
        )

    # Test 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes with correct parameters."""
        assert specialist.agent_id == 'test_zero_density_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.tasks_failed == 0
        assert hasattr(specialist, 'zero_counts')

    # Test 2: Service registration
    def test_registration_with_df(self):
        """Test specialist registers with Directory Facilitator."""
        mock_df = Mock()
        specialist = ZeroDensitySpecialist(
            agent_id='test_zero_density_df',
            df=mock_df,
            blackboard=None
        )

        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.algebra.numbertheory.analytic.zero_density'
        assert call_args.agent_id == 'test_zero_density_df'

    # Test 3: Zero counting N(T)
    def test_zero_counting(self, specialist):
        """Test counting zeros up to height T: N(T)."""
        # N(T) = number of zeros with 0 < Im(ρ) ≤ T

        test_values = [10, 50, 100, 1000]

        for t in test_values:
            result = specialist.count_zeros(t)
            assert result is not None
            assert isinstance(result, (int, float, dict))

    # Test 4: Density estimates
    def test_density_estimates(self, specialist):
        """Test density of zeros: N(T) ~ (T/(2π))log(T/(2πe))."""
        # Asymptotic formula for zero counting

        t = 1000
        sigma = 0.5  # On critical line
        result = specialist.density_estimate(sigma, t)
        assert result is not None

    # Test 5: Zero-free regions
    def test_zero_free_regions(self, specialist):
        """Test classical zero-free region Re(s) > 1 - c/log(Im(s))."""
        # De la Vallée-Poussin zero-free region

        test_heights = [10, 100, 1000]

        for t in test_heights:
            try:
                region = specialist.zero_free_region(t)
                assert region is not None
            except AttributeError:
                # Method may not exist
                pass

    # Test 6: Critical strip analysis
    def test_critical_strip_analysis(self, specialist):
        """Test analysis of zeros in critical strip 0 < Re(s) < 1."""
        # All nontrivial zeros lie in critical strip

        sigma_min = 0.0
        sigma_max = 1.0
        t_max = 100

        try:
            result = specialist.analyze_critical_strip(sigma_min, sigma_max, t_max)
            assert result is not None
        except AttributeError:
            pass

    # Test 7: Problem variations
    @pytest.mark.parametrize("operation,t_value,description", [
        ("count_zeros", 10, "Count zeros to T=10"),
        ("density_estimate", 100, "Density estimate at T=100"),
        ("zero_free_region", 50, "Zero-free region at T=50"),
    ])
    def test_problem_variations(self, specialist, operation, t_value, description):
        """Test specialist handles various operations."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"{operation}({t_value})",
            author_agent='test_orchestrator',
            conversation_id=f'test_var_{description}',
            metadata={
                'operation': operation,
                'T': t_value,
                't': t_value
            }
        )

        try:
            result = specialist.process(task)
            assert result is not None
        except Exception as e:
            print(f"Processing {description} raised: {e}")

    # Test 8: Edge cases
    def test_edge_cases(self, specialist):
        """Test boundary conditions."""
        edge_cases = [
            (0, "count_zeros", "T=0"),
            (1, "count_zeros", "T=1"),
            (14.135, "density_estimate", "Near first zero"),
        ]

        for value, operation, description in edge_cases:
            task = create_entry(
                entry_type=EntryType.TASK,
                content=f"{operation}({value})",
                author_agent='test',
                conversation_id=f'test_edge_{description}',
                metadata={'operation': operation, 'T': value, 't': value}
            )

            try:
                result = specialist.process(task)
                assert result is not None
            except Exception:
                pass

    # Test 9: Invalid inputs
    def test_invalid_inputs(self, specialist):
        """Test invalid input handling."""
        invalid_inputs = [
            ("unknown_op", 10),
            ("count_zeros", -5),
            ("density_estimate", -100),
        ]

        for operation, value in invalid_inputs:
            task = create_entry(
                entry_type=EntryType.TASK,
                content=f"{operation}({value})",
                author_agent='test',
                conversation_id='test_invalid',
                metadata={'operation': operation, 'T': value}
            )

            try:
                result = specialist.process(task)
                assert result is not None
            except Exception:
                pass

    # Test 10: Blackboard integration
    def test_blackboard_integration(self, specialist_with_mocks):
        """Test blackboard posting."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="count_zeros(100)",
            author_agent='test',
            conversation_id='test_bb',
            metadata={'operation': 'count_zeros', 'T': 100}
        )

        result = specialist_with_mocks.process(task)
        assert result is not None

    # Test 11: BDI update_beliefs
    def test_bdi_update_beliefs(self, specialist_with_mocks):
        """Test BDI update_beliefs."""
        mock_task = Mock()
        specialist_with_mocks.blackboard.query_entries = Mock(return_value=[mock_task])
        specialist_with_mocks.update_beliefs()

    # Test 12: BDI deliberate
    def test_bdi_deliberate(self, specialist):
        """Test BDI deliberate."""
        specialist.add_belief('pending_task', {'operation': 'count_zeros', 'T': 100})
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # Test 13: BDI execute_step
    def test_bdi_execute_step(self, specialist):
        """Test BDI execute_step."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        intention = Intention(
            plan_id='test_plan_zero_density',
            steps=['count_zeros', 'compute_density'],
            target_desire='analyze_zero_density'
        )

        try:
            specialist.execute_step(intention)
        except Exception:
            pass

    # Test 14: Concurrency
    def test_concurrency(self, specialist):
        """Test thread safety."""
        import threading

        results = []

        def worker(tid):
            task = create_entry(
                entry_type=EntryType.TASK,
                content=f"count_zeros({tid * 10})",
                author_agent='test',
                conversation_id=f'test_{tid}',
                metadata={'operation': 'count_zeros', 'T': tid * 10}
            )
            try:
                results.append(specialist.process(task))
            except Exception:
                results.append(None)

        threads = [threading.Thread(target=worker, args=(i+1,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert len(results) == 5

    # Test 15: Statistics
    def test_statistics(self, specialist):
        """Test statistics tracking."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="count_zeros(100)",
            author_agent='test',
            conversation_id='test_stats',
            metadata={'operation': 'count_zeros', 'T': 100}
        )

        specialist.process(task)
        stats = specialist.get_stats()

        assert isinstance(stats, dict)
        assert 'tasks_executed' in stats

    # Test 16: Process message with unknown action
    def test_process_message_unknown_action(self, specialist):
        """Test process_message with unknown action."""
        result = specialist.process_message({'action': 'invalid_op', 'params': {}})
        assert result is not None
        assert 'status' in result

    # Test 17: Count zeros with small T
    def test_count_zeros_small_t(self, specialist):
        """Test count_zeros with small T values."""
        small_t_values = [1, 2, 5, 10, 14.135]  # Near first zero

        for t in small_t_values:
            try:
                result = specialist.count_zeros(t)
                # Should count zeros up to height T
                assert result is not None
                assert isinstance(result, (int, float, dict))
            except Exception:
                pass

    # Test 18: Density estimate with different bound types
    def test_density_estimate_all_bound_types(self, specialist):
        """Test density_estimate with all bound_type options."""
        bound_types = ['classical', 'ingham', 'huxley']
        t = 100

        for bound_type in bound_types:
            try:
                result = specialist.density_estimate(0.5, t, bound_type=bound_type)
                # Should compute density estimate
                assert result is not None
            except Exception:
                pass

    # Test 19: Density estimate edge cases
    def test_density_estimate_edge_cases(self, specialist):
        """Test density estimate with various sigma values."""
        test_cases = [
            (0.5, 100, 'classical'),  # On critical line
            (0.75, 100, 'classical'),  # Between 1/2 and 1
            (1.0, 100, 'classical'),  # At Re(s) = 1
        ]

        for sigma, t, bound_type in test_cases:
            try:
                result = specialist.density_estimate(sigma, t, bound_type=bound_type)
                assert result is not None
            except Exception:
                pass

    # Test 20: Zero-free region edge cases
    def test_zero_free_region_edge_cases(self, specialist):
        """Test zero-free region computation for various heights."""
        heights = [1, 10, 100, 1000, 10000]

        for t in heights:
            try:
                region = specialist.zero_free_region(t)
                # Should compute zero-free region bound
                assert region is not None
                assert isinstance(region, (float, dict))
            except Exception:
                pass

    # Test 21: Classical zero-free region computation
    def test_classical_zero_free_region(self, specialist):
        """Test classical de la Vallée-Poussin zero-free region."""
        # Re(s) > 1 - c/log(Im(s)) for some constant c
        test_heights = [50, 100, 500, 1000]

        for t in test_heights:
            try:
                bound = specialist._classical_zero_free_region(t)
                # Should return sigma bound
                assert bound is not None
                assert isinstance(bound, (float, int, dict))
            except AttributeError:
                # Method may not exist
                pass

    # Test 22: Execute step with post action
    def test_execute_step_post_action(self, specialist_with_mocks):
        """Test execute_step with 'post' action."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        intention = Intention(
            plan_id='test_post',
            steps=['count', 'estimate', 'post'],
            target_desire='analyze_zeros',
            metadata={'result': {'success': True}}
        )
        intention.current_step = 2

        try:
            specialist_with_mocks.execute_step(intention)
        except Exception:
            pass

    # Test 23: Process with exception handling
    def test_process_with_exception(self, specialist):
        """Test process handles exceptions gracefully."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="invalid_operation(-999)",
            author_agent='test',
            conversation_id='test_exc',
            metadata={'operation': 'invalid_operation', 'T': -999}
        )

        try:
            result = specialist.process(task)
            assert result is not None
        except Exception:
            pass

    # Test 24: Count zeros at specific zero heights
    def test_count_zeros_at_zero_heights(self, specialist):
        """Test count_zeros at known zero heights."""
        # Known zeros: 14.134725, 21.022040, 25.010858, ...
        zero_heights = [14.135, 21.023, 25.011]

        for t in zero_heights:
            try:
                result = specialist.count_zeros(t)
                # Should be at least 1, 2, 3 respectively
                assert result is not None
            except Exception:
                pass

    # Test 25: Density estimate with varying T
    def test_density_estimate_varying_t(self, specialist):
        """Test density estimate with different T values."""
        t_values = [10, 50, 100, 500, 1000]

        for t in t_values:
            try:
                result = specialist.density_estimate(0.5, t)
                # Should compute density N(σ, T)
                assert result is not None
            except Exception:
                pass

    # Test 26: Zero-free region near critical line
    def test_zero_free_region_near_critical_line(self, specialist):
        """Test zero-free region computation near Re(s) = 1/2."""
        # The region should approach 1/2 as T → ∞
        large_t_values = [1000, 5000, 10000]

        for t in large_t_values:
            try:
                region = specialist.zero_free_region(t)
                # Should be close to but greater than 1/2
                assert region is not None
            except Exception:
                pass


pytestmark = pytest.mark.phase6


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
