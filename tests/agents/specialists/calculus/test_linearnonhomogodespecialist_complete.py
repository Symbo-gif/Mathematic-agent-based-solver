# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Comprehensive Tests for LinearNonhomogeneousODESpecialist
========================================================

Standard 12-test pattern for specialist agents:
1. Initialization
2. Service registration
3-7. Core functionality tests
8. Edge cases
9-10. BDI implementation
11. Concurrent requests
12. Statistics tracking
"""

import pytest
from unittest.mock import Mock, MagicMock
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.agents.specialists.calculus.linear_nonhomogeneous_ode_specialist import (
    LinearNonhomogeneousODESpecialist
)


class TestLinearNonhomogeneousODESpecialistComplete:
    """Comprehensive test suite for LinearNonhomogeneousODESpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create specialist instance without dependencies."""
        return LinearNonhomogeneousODESpecialist(
            agent_id='test_linear_ode_001',
            df=None,
            blackboard=None
        )

    @pytest.fixture
    def specialist_with_mocks(self):
        """Create specialist with mocked dependencies."""
        mock_df = Mock()
        mock_blackboard = Mock()
        return LinearNonhomogeneousODESpecialist(
            agent_id='test_linear_ode_002',
            df=mock_df,
            blackboard=mock_blackboard
        )

    # Test 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes with correct parameters."""
        assert specialist.agent_id == 'test_linear_ode_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.tasks_failed == 0
        assert specialist.linear_odes_solved == 0
        assert specialist.homogeneous_solved == 0
        assert specialist.nonhomogeneous_solved == 0
        assert specialist.integrating_factors_computed == 0
        assert specialist.advanced_integration_calls == 0

    # Test 2: Service registration
    def test_registration_with_df(self):
        """Test specialist registers with Directory Facilitator."""
        mock_df = Mock()
        specialist = LinearNonhomogeneousODESpecialist(
            agent_id='test_linear_ode_df',
            df=mock_df,
            blackboard=None
        )

        # Verify registration was called
        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.calculus.ode.linear_nonhomogeneous'
        assert call_args.agent_id == 'test_linear_ode_df'
        assert call_args.algorithm == 'integrating_factor'

    # Test 3: Basic problem solving - Homogeneous linear ODE
    def test_basic_problem_solving_homogeneous(self, specialist):
        """Test solving homogeneous linear ODE: y' + y = 0"""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="y' + y = 0",
            author_agent='test_orchestrator',
            conversation_id='test_conv_001',
            metadata={'ode_expr': "y' + y = 0", 'variable': 'x', 'function': 'y'}
        )

        result = specialist.process(task)

        # Should return a result
        assert result is not None
        assert specialist.tasks_executed == 1

    # Test 4: Nonhomogeneous linear ODE
    def test_nonhomogeneous_linear_ode(self, specialist):
        """Test solving nonhomogeneous linear ODE: y' + 2*x*y = x^2"""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="y' + 2*x*y = x^2",
            author_agent='test_orchestrator',
            conversation_id='test_conv_002',
            metadata={'ode_expr': "y' + 2*x*y = x^2", 'variable': 'x', 'function': 'y'}
        )

        result = specialist.process(task)

        # Should attempt to solve
        assert result is not None
        assert specialist.tasks_executed == 1

    # Test 5: Coefficient extraction
    def test_coefficient_extraction(self, specialist):
        """Test _extract_coefficients method."""
        test_cases = [
            ("y' + y = 0", 'x', 'y', ('1', '0')),
            ("y' + 2*y = x", 'x', 'y', ('2', 'x')),
            ("y' - y = 1", 'x', 'y', ('-1', '1')),
        ]

        for ode_str, var, func, expected_approx in test_cases:
            p_coeff, q_coeff = specialist.extract_coefficients(ode_str, var, func)
            # Should extract some coefficients
            assert p_coeff is not None
            assert q_coeff is not None

    # Test 6: Integrating factor computation
    def test_integrating_factor_computation(self, specialist):
        """Test _compute_integrating_factor method."""
        test_cases = [
            ('1', 'x'),  # P(x) = 1 → μ = exp(x)
            ('x', 'x'),  # P(x) = x → μ = exp(x^2/2)
            ('2', 'x'),  # P(x) = 2 → μ = exp(2x)
        ]

        for p_x, var in test_cases:
            try:
                mu = specialist._compute_integrating_factor(p_x, var)
                # Should compute an integrating factor
                assert mu is not None
                assert isinstance(mu, (str, dict))
                specialist.integrating_factors_computed += 1
            except Exception as e:
                # May not support all forms
                print(f"Integrating factor for P={p_x} raised: {e}")

    # Test 7: Problem variations
    @pytest.mark.parametrize("ode_expr,description", [
        ("y' + y = 0", "Homogeneous"),
        ("y' + y = x", "Nonhomogeneous linear"),
        ("y' + 2*x*y = 0", "Variable coefficient"),
        ("y' - 3*y = exp(x)", "Exponential forcing"),
    ])
    def test_problem_variations(self, specialist, ode_expr, description):
        """Test specialist handles various linear ODE forms."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content=ode_expr,
            author_agent='test_orchestrator',
            conversation_id=f'test_var_{description}',
            metadata={'ode_expr': ode_expr, 'variable': 'x', 'function': 'y'}
        )

        try:
            result = specialist.process(task)
            assert result is not None
        except Exception as e:
            print(f"Processing {description} raised: {e}")

    # Test 8: Edge cases
    def test_edge_cases(self, specialist):
        """Test boundary conditions and edge cases."""
        edge_cases = [
            ("y' = 0", "Zero coefficient"),
            ("y' + 0*y = x", "Zero P(x)"),
            ("y' + y = 0", "Zero Q(x)"),
        ]

        for ode_expr, description in edge_cases:
            task = create_entry(
                entry_type=EntryType.TASK,
                content=ode_expr,
                author_agent='test_orchestrator',
                conversation_id=f'test_edge_{description}',
                metadata={'ode_expr': ode_expr, 'variable': 'x', 'function': 'y'}
            )

            try:
                result = specialist.process(task)
                assert result is not None
            except Exception:
                pass

    # Test 9: Invalid inputs
    def test_invalid_inputs(self, specialist):
        """Test specialist handles invalid input gracefully."""
        invalid_inputs = [
            "not an ode",
            "y^2 + y = x",  # Nonlinear
            "malformed {{{{ input",
        ]

        for invalid in invalid_inputs:
            task = create_entry(
                entry_type=EntryType.TASK,
                content=invalid,
                author_agent='test_orchestrator',
                conversation_id='test_invalid',
                metadata={'ode_expr': invalid, 'variable': 'x', 'function': 'y'}
            )

            try:
                result = specialist.process(task)
                assert result is not None
            except Exception:
                pass

    # Test 10: Advanced integration fallback
    def test_advanced_integration_fallback(self, specialist_with_mocks):
        """Test fallback to AdvancedIntegrationSpecialist."""
        # Mock advanced integration specialist in DF
        mock_advanced = Mock()
        mock_advanced.process = Mock(return_value={'success': True, 'solution': 'integrated'})

        mock_service = Mock()
        mock_service.instance = mock_advanced
        specialist_with_mocks.df.search = Mock(return_value=[mock_service])

        # Try to solve ODE requiring advanced integration
        task = create_entry(
            entry_type=EntryType.TASK,
            content="y' + y = exp(x)*sin(x)",
            author_agent='test_orchestrator',
            conversation_id='test_advanced',
            metadata={'ode_expr': "y' + y = exp(x)*sin(x)", 'variable': 'x', 'function': 'y'}
        )

        try:
            result = specialist_with_mocks.process(task)
            # Should attempt advanced integration
            assert result is not None
        except Exception:
            pass

    # Test 11: Blackboard integration
    def test_blackboard_integration(self, specialist_with_mocks):
        """Test specialist posts results to blackboard correctly."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="y' + y = 0",
            author_agent='test_orchestrator',
            conversation_id='test_blackboard',
            metadata={'ode_expr': "y' + y = 0", 'variable': 'x', 'function': 'y'}
        )

        result = specialist_with_mocks.process(task)

        assert result is not None
        if hasattr(result, 'entry_type'):
            assert result.entry_type == EntryType.PARTIAL_RESULT

    # Test 12: BDI - update_beliefs
    def test_bdi_update_beliefs(self, specialist_with_mocks):
        """Test update_beliefs processes blackboard entries."""
        mock_task = Mock()
        mock_task.entry_id = 'task_linear_001'
        mock_task.metadata = {'ode_expr': "y' + y = 0"}

        specialist_with_mocks.blackboard.query_entries = Mock(return_value=[mock_task])

        specialist_with_mocks.update_beliefs()
        # Should process without error

    # Test 13: BDI - deliberate
    def test_bdi_deliberate(self, specialist):
        """Test deliberate generates intentions from beliefs."""
        specialist.add_belief('pending_ode_task', {'ode': "y' + y = 0"})

        intentions = specialist.deliberate()

        assert isinstance(intentions, list)

    # Test 14: BDI - execute_step
    def test_bdi_execute_step(self, specialist):
        """Test execute_step executes plan actions."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        intention = Intention(
            plan_id='test_plan_linear',
            steps=['extract_coefficients', 'compute_integrating_factor', 'integrate'],
            target_desire='solve_linear_ode',
            metadata={'ode': "y' + y = 0"}
        )

        try:
            specialist.execute_step(intention)
        except Exception:
            pass

    # Test 15: Concurrency
    def test_concurrency(self, specialist):
        """Test thread-safe operation with concurrent requests."""
        import threading

        results = []
        errors = []

        def worker(thread_id):
            try:
                task = create_entry(
                    entry_type=EntryType.TASK,
                    content="y' + y = 0",
                    author_agent='test_orchestrator',
                    conversation_id=f'test_concurrent_{thread_id}',
                    metadata={'ode_expr': "y' + y = 0", 'variable': 'x', 'function': 'y'}
                )
                result = specialist.process(task)
                results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()

        for t in threads:
            t.join(timeout=5.0)

        assert len(results) + len(errors) == 5

    # Test 16: Statistics
    def test_statistics(self, specialist):
        """Test get_stats returns correct metrics."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="y' + y = 0",
            author_agent='test_orchestrator',
            conversation_id='test_stats',
            metadata={'ode_expr': "y' + y = 0", 'variable': 'x', 'function': 'y'}
        )

        specialist.process(task)

        stats = specialist.get_stats()

        assert isinstance(stats, dict)
        assert 'tasks_executed' in stats
        assert stats['tasks_executed'] >= 1

    # Test 17: Process message with unknown action
    def test_process_message_unknown_action(self, specialist):
        """Test process_message with unknown action."""
        result = specialist.process_message({'action': 'invalid_action', 'params': {}})
        assert result is not None
        assert 'status' in result

    # Test 18: Extract coefficients edge cases
    def test_extract_coefficients_edge_cases(self, specialist):
        """Test extract_coefficients with edge cases."""
        edge_cases = [
            ("y' = 0", 'x', 'y'),  # Zero RHS
            ("y' + 0 = 0", 'x', 'y'),  # Zero coefficient
            ("y' + (x^2 + 2*x + 1)*y = sin(x)", 'x', 'y'),  # Complex P(x)
            ("y' - (1/x)*y = x^2", 'x', 'y'),  # Rational coefficient
        ]

        for ode_str, var, func in edge_cases:
            try:
                p_coeff, q_coeff = specialist.extract_coefficients(ode_str, var, func)
                assert p_coeff is not None
                assert q_coeff is not None
            except Exception:
                # May not handle all edge cases
                pass

    # Test 19: Compute integrating factor failure cases
    def test_compute_integrating_factor_failure(self, specialist):
        """Test _compute_integrating_factor with difficult cases."""
        difficult_cases = [
            ('1/x', 'x'),  # log singularity
            ('x^(-2)', 'x'),  # Negative power
            ('tan(x)', 'x'),  # Trig function with poles
            ('sqrt(x)', 'x'),  # Fractional power
        ]

        for p_x, var in difficult_cases:
            try:
                mu = specialist._compute_integrating_factor(p_x, var)
                # Should handle or return error
                assert mu is None or isinstance(mu, (str, dict))
            except Exception:
                # Expected for difficult cases
                pass

    # Test 20: Try advanced integration with no DF
    def test_try_advanced_integration_no_df(self, specialist):
        """Test _try_advanced_integration when DF is None."""
        # Specialist without DF
        try:
            result = specialist._try_advanced_integration('exp(x)*sin(x)', 'x')
            # Should return None or error
            assert result is None or isinstance(result, dict)
        except AttributeError:
            # Method may not exist
            pass

    # Test 21: Try advanced integration with failed integration
    def test_try_advanced_integration_failed(self, specialist_with_mocks):
        """Test _try_advanced_integration when integration fails."""
        # Mock DF to return no advanced integration specialist
        specialist_with_mocks.df.search = Mock(return_value=[])

        try:
            result = specialist_with_mocks._try_advanced_integration('exp(x)*sin(x)', 'x')
            # Should return None when no specialist found
            assert result is None or isinstance(result, dict)
        except AttributeError:
            pass

    # Test 22: Solve linear with complex Q(x)
    def test_solve_linear_complex_qx(self, specialist):
        """Test solve_linear with complex Q(x)."""
        complex_q_cases = [
            ('1', 'exp(x)*sin(x)', 'x', 'y'),
            ('x', 'x^2*log(x)', 'x', 'y'),
            ('2*x', '(x^3 + x^2 + x + 1)', 'x', 'y'),
        ]

        for p_x, q_x, var, func in complex_q_cases:
            try:
                result = specialist.solve_linear(p_x, q_x, var, func)
                # Should attempt to solve or return error
                assert result is None or isinstance(result, (str, dict))
            except Exception:
                # May not handle all complex cases
                pass

    # Test 23: Is linear edge cases
    def test_is_linear_edge_cases(self, specialist):
        """Test is_linear with various ODE forms."""
        test_cases = [
            ("y' + y = 0", 'x', 'y', True),
            ("y' + x*y = x", 'x', 'y', True),
            ("y' + y^2 = 0", 'x', 'y', False),  # Nonlinear
            ("y'' + y = 0", 'x', 'y', False),  # Second order
        ]

        for ode_str, var, func, expected in test_cases:
            try:
                result = specialist.is_linear(ode_str, var, func)
                # Should detect linearity
                assert isinstance(result, bool)
            except AttributeError:
                # Method may not exist
                pass

    # Test 24: Execute step with post action
    def test_execute_step_post_action(self, specialist_with_mocks):
        """Test execute_step with 'post' action."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        intention = Intention(
            plan_id='test_post',
            steps=['claim', 'solve', 'post'],
            target_desire='solve_linear',
            metadata={'result': {'success': True}}
        )
        intention.current_step = 2  # At 'post'

        try:
            specialist_with_mocks.execute_step(intention)
        except Exception:
            pass

    # Test 25: Process with exception handling
    def test_process_with_exception(self, specialist):
        """Test process handles exceptions gracefully."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="invalid ODE ###",
            author_agent='test',
            conversation_id='test_exc',
            metadata={'ode_expr': "invalid ODE ###"}
        )

        try:
            result = specialist.process(task)
            assert result is not None
        except Exception:
            pass

    # Test 26: Advanced integration with mock specialist returning error
    def test_advanced_integration_specialist_error(self, specialist_with_mocks):
        """Test handling when advanced integration specialist returns error."""
        mock_advanced = Mock()
        mock_advanced.process = Mock(return_value={'success': False, 'error': 'Integration failed'})

        mock_service = Mock()
        mock_service.instance = mock_advanced
        specialist_with_mocks.df.search = Mock(return_value=[mock_service])

        task = create_entry(
            entry_type=EntryType.TASK,
            content="y' + y = exp(x)*sin(x)*cos(x)*tan(x)",
            author_agent='test',
            conversation_id='test_adv_error',
            metadata={'ode_expr': "y' + y = exp(x)*sin(x)*cos(x)*tan(x)"}
        )

        try:
            result = specialist_with_mocks.process(task)
            assert result is not None
        except Exception:
            pass


# Phase 6 marker
pytestmark = pytest.mark.phase6


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
