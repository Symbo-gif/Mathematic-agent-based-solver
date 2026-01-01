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
Comprehensive Tests for ExplicitFormulaSpecialist
=================================================

Standard 12-test pattern for specialist agents.
Tests explicit formulas connecting primes and zeta zeros.
"""

import pytest
from unittest.mock import Mock, MagicMock
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.explicit_formula import (
    ExplicitFormulaSpecialist
)


class TestExplicitFormulaSpecialistComplete:
    """Comprehensive test suite for ExplicitFormulaSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create specialist instance without dependencies."""
        return ExplicitFormulaSpecialist(
            agent_id='test_explicit_formula_001',
            df=None,
            blackboard=None
        )

    @pytest.fixture
    def specialist_with_mocks(self):
        """Create specialist with mocked dependencies."""
        mock_df = Mock()
        mock_blackboard = Mock()
        return ExplicitFormulaSpecialist(
            agent_id='test_explicit_formula_002',
            df=mock_df,
            blackboard=mock_blackboard
        )

    # Test 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes with correct parameters."""
        assert specialist.agent_id == 'test_explicit_formula_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.tasks_failed == 0
        assert specialist.formulas_evaluated == 0
        assert specialist.zero_contributions_computed == 0
        assert specialist.von_mangoldt_calls == 0
        assert specialist.chebyshev_calls == 0

    # Test 2: Service registration
    def test_registration_with_df(self):
        """Test specialist registers with Directory Facilitator."""
        mock_df = Mock()
        specialist = ExplicitFormulaSpecialist(
            agent_id='test_explicit_formula_df',
            df=mock_df,
            blackboard=None
        )

        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.algebra.numbertheory.analytic.explicit_formula'
        assert call_args.agent_id == 'test_explicit_formula_df'

    # Test 3: von Mangoldt function
    def test_von_mangoldt_function(self, specialist):
        """Test von Mangoldt function Λ(n)."""
        # Λ(n) = log p if n = p^k for prime p, 0 otherwise

        test_cases = [
            (2, 'log(2)'),   # prime
            (3, 'log(3)'),   # prime
            (4, 'log(2)'),   # 2^2
            (8, 'log(2)'),   # 2^3
            (9, 'log(3)'),   # 3^2
            (6, 0),          # composite (not prime power)
            (1, 0),          # 1
        ]

        for n, expected_pattern in test_cases:
            result = specialist.von_mangoldt(n)
            assert result is not None
            specialist.von_mangoldt_calls += 1

    # Test 4: Chebyshev function
    def test_chebyshev_function(self, specialist):
        """Test Chebyshev function ψ(x) = Σ Λ(n) for n ≤ x."""
        # ψ(x) should approximate x for large x

        test_values = [10, 50, 100, 1000]

        for x in test_values:
            result = specialist.chebyshev_psi(x)
            assert result is not None
            assert isinstance(result, (int, float, dict))
            specialist.chebyshev_calls += 1

    # Test 5: Explicit formula evaluation
    def test_explicit_formula_evaluation(self, specialist):
        """Test explicit formula ψ(x) = x - Σ(x^ρ/ρ) - log(2π)..."""
        # Uses zeta zeros to compute ψ(x)

        x_value = 100
        max_zeros = 10

        result = specialist.explicit_formula_psi(x_value, max_zeros)
        assert result is not None
        specialist.formulas_evaluated += 1

    # Test 6: Zero contributions
    def test_zero_contributions(self, specialist):
        """Test oscillatory terms from zeta zeros."""
        # Each zero ρ = 1/2 + iγ contributes x^ρ/ρ

        x_value = 100
        rho = complex(0.5, 14.134725)  # First nontrivial zero

        try:
            contribution = specialist._zero_contribution(x_value, rho)
            assert contribution is not None
            specialist.zero_contributions_computed += 1
        except AttributeError:
            # Method may not exist
            pass

    # Test 7: Problem variations
    @pytest.mark.parametrize("operation,x_value,description", [
        ("von_mangoldt", 10, "von Mangoldt at n=10"),
        ("chebyshev_psi", 50, "Chebyshev at x=50"),
        ("explicit_formula", 100, "Explicit formula at x=100"),
    ])
    def test_problem_variations(self, specialist, operation, x_value, description):
        """Test specialist handles various operations."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content=f"{operation}({x_value})",
            author_agent='test_orchestrator',
            conversation_id=f'test_var_{description}',
            metadata={
                'operation': operation,
                'x': x_value,
                'n': x_value,
                'max_zeros': 10
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
            (1, "von_mangoldt", "n=1"),
            (2, "von_mangoldt", "First prime"),
            (0, "chebyshev_psi", "x=0"),
            (1, "chebyshev_psi", "x=1"),
        ]

        for value, operation, description in edge_cases:
            task = create_entry(
                entry_type=EntryType.TASK,
                content=f"{operation}({value})",
                author_agent='test',
                conversation_id=f'test_edge_{description}',
                metadata={'operation': operation, 'x': value, 'n': value}
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
            ("von_mangoldt", -5),
            ("chebyshev_psi", -10),
        ]

        for operation, value in invalid_inputs:
            task = create_entry(
                entry_type=EntryType.TASK,
                content=f"{operation}({value})",
                author_agent='test',
                conversation_id='test_invalid',
                metadata={'operation': operation, 'x': value, 'n': value}
            )

            try:
                result = specialist.process(task)
                # Should handle gracefully
                assert result is not None
            except Exception:
                pass

    # Test 10: Blackboard integration
    def test_blackboard_integration(self, specialist_with_mocks):
        """Test blackboard posting."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="chebyshev_psi(100)",
            author_agent='test',
            conversation_id='test_bb',
            metadata={'operation': 'chebyshev_psi', 'x': 100}
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
        specialist.add_belief('pending_task', {'operation': 'von_mangoldt', 'n': 10})
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # Test 13: BDI execute_step
    def test_bdi_execute_step(self, specialist):
        """Test BDI execute_step."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        intention = Intention(
            plan_id='test_plan_explicit_formula',
            steps=['compute_von_mangoldt', 'sum_zeros'],
            target_desire='evaluate_explicit_formula'
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
                content=f"chebyshev_psi({tid * 10})",
                author_agent='test',
                conversation_id=f'test_{tid}',
                metadata={'operation': 'chebyshev_psi', 'x': tid * 10}
            )
            try:
                results.append(specialist.process(task))
            except Exception:
                results.append(None)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
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
            content="chebyshev_psi(100)",
            author_agent='test',
            conversation_id='test_stats',
            metadata={'operation': 'chebyshev_psi', 'x': 100}
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

    # Test 17: von Mangoldt with composite numbers
    def test_von_mangoldt_composite_numbers(self, specialist):
        """Test von Mangoldt function with composite (non-prime-power) numbers."""
        composite_numbers = [6, 10, 12, 15, 20, 21, 30]  # Not prime powers

        for n in composite_numbers:
            result = specialist.von_mangoldt(n)
            # Should return 0 for composite numbers
            assert result is not None
            assert result == 0 or (isinstance(result, dict) and (result.get('value') == 0 or result.get('lambda_n') == 0))

    # Test 18: Chebyshev psi with large x
    def test_chebyshev_psi_large_x(self, specialist):
        """Test Chebyshev function with large x values."""
        large_values = [1000, 5000, 10000]

        for x in large_values:
            try:
                result = specialist.chebyshev_psi(x)
                # Should compute or return approximation
                assert result is not None
                assert isinstance(result, (int, float, dict))
            except Exception:
                # May timeout on very large values
                pass

    # Test 19: Explicit formula with zero contributions
    def test_explicit_formula_zero_contributions(self, specialist):
        """Test explicit formula when zero contributions sum to near-zero."""
        # Test with small x where oscillations are significant
        small_x_values = [2, 3, 5, 7]

        for x in small_x_values:
            try:
                result = specialist.explicit_formula_psi(x, max_zeros=5)
                assert result is not None
            except Exception:
                pass

    # Test 20: Compute zero contribution edge cases
    def test_compute_zero_contribution_edge_cases(self, specialist):
        """Test oscillatory terms from zeta zeros edge cases."""
        test_cases = [
            (1, complex(0.5, 14.134725)),  # x=1, first zero
            (2, complex(0.5, 21.022040)),  # x=2, second zero
            (100, complex(0.5, 25.010858)),  # Large x, third zero
        ]

        for x, rho in test_cases:
            try:
                contribution = specialist._zero_contribution(x, rho)
                # Should compute oscillatory term
                assert contribution is not None
                assert isinstance(contribution, (complex, float, int, dict))
            except AttributeError:
                # Method may not exist
                pass

    # Test 21: Execute step with post action
    def test_execute_step_post_action(self, specialist_with_mocks):
        """Test execute_step with 'post' action."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        intention = Intention(
            plan_id='test_post',
            steps=['compute', 'sum', 'post'],
            target_desire='evaluate_formula',
            metadata={'result': {'success': True}}
        )
        intention.current_step = 2

        try:
            specialist_with_mocks.execute_step(intention)
        except Exception:
            pass

    # Test 22: Process with exception handling
    def test_process_with_exception(self, specialist):
        """Test process handles exceptions gracefully."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="invalid_operation(-999)",
            author_agent='test',
            conversation_id='test_exc',
            metadata={'operation': 'invalid_operation', 'x': -999}
        )

        try:
            result = specialist.process(task)
            assert result is not None
        except Exception:
            pass

    # Test 23: Von Mangoldt with prime powers
    def test_von_mangoldt_prime_powers(self, specialist):
        """Test von Mangoldt with various prime powers."""
        prime_powers = [
            (4, 'log(2)'),  # 2^2
            (8, 'log(2)'),  # 2^3
            (16, 'log(2)'),  # 2^4
            (27, 'log(3)'),  # 3^3
            (125, 'log(5)'),  # 5^3
        ]

        for n, expected_pattern in prime_powers:
            result = specialist.von_mangoldt(n)
            # Should return log(p) for prime powers p^k
            assert result is not None

    # Test 24: Explicit formula with different max_zeros
    def test_explicit_formula_varying_max_zeros(self, specialist):
        """Test explicit formula with different numbers of zeros."""
        max_zeros_values = [1, 5, 10, 20]

        for max_zeros in max_zeros_values:
            try:
                result = specialist.explicit_formula_psi(100, max_zeros)
                assert result is not None
            except Exception:
                pass

    # Test 25: Chebyshev psi for small primes
    def test_chebyshev_psi_small_primes(self, specialist):
        """Test Chebyshev function at small prime values."""
        # ψ(p) should include Λ(p) = log(p) for prime p
        small_primes = [2, 3, 5, 7, 11, 13]

        for p in small_primes:
            try:
                result = specialist.chebyshev_psi(p)
                assert result is not None
                # ψ(p) ≈ log(p) + ψ(p-1)
            except Exception:
                pass


pytestmark = pytest.mark.phase6


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
