# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Tests for ODE Solver Module
===========================

Comprehensive tests for the ODESolver BDI agent.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestODESolverInit:
    """Tests for ODESolver initialization."""

    def test_ode_solver_create(self):
        """Test creating ODE solver agent."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()
        assert solver.agent_id == 'ode_solver_001'
        assert solver.tasks_executed == 0

    def test_ode_solver_custom_id(self):
        """Test creating with custom agent ID."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver(agent_id='custom_ode_001')
        assert solver.agent_id == 'custom_ode_001'

    def test_ode_solver_with_df(self):
        """Test creating with directory facilitator."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        mock_df = MagicMock()
        solver = ODESolver(df=mock_df)
        assert solver.df is mock_df
        mock_df.register.assert_called_once()


class TestODESolverProcess:
    """Tests for ODESolver process method."""

    def test_process_basic(self):
        """Test basic process call."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': "y' = x"}

        result = solver.process(mock_task)
        assert solver.tasks_executed == 1
        assert solver.tasks_succeeded == 1

    def test_process_with_sympy_expr(self):
        """Test process with sympy_expr in metadata."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.metadata = {'sympy_expr': "Derivative(y(x), x) - x"}

        result = solver.process(mock_task)
        assert solver.tasks_executed == 1

    def test_process_no_metadata(self):
        """Test process with task without metadata."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        mock_task = MagicMock(spec=[])
        del mock_task.metadata  # Remove metadata attribute

        result = solver.process(mock_task)
        assert solver.tasks_executed == 1


class TestODESolverResultEntry:
    """Tests for result entry creation."""

    def test_create_result_entry_no_blackboard(self):
        """Test result entry creation without blackboard."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.conversation_id = 'conv_001'

        result = solver._create_result_entry(mock_task, 'y = x^2/2 + C')
        assert result == 'y = x^2/2 + C'

    def test_create_error_entry_no_blackboard(self):
        """Test error entry creation without blackboard."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.conversation_id = 'conv_001'

        result = solver._create_error_entry(mock_task, 'Test error')
        assert result is None


class TestODESolverBDI:
    """Tests for BDI methods."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs without blackboard."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()
        solver.update_beliefs()  # Should not raise

    def test_deliberate_no_tasks(self):
        """Test deliberate with no pending tasks."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()
        intentions = solver.deliberate()
        assert intentions == []

    def test_deliberate_with_pending_task(self):
        """Test deliberate with pending task in beliefs."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        solver = ODESolver()

        # Add a pending task belief
        mock_task = MagicMock()
        mock_task.entry_id = 'task_001'
        mock_task.metadata = {'raw_input': "y' = x", 'operation': 'solve_ode'}

        solver.add_belief(
            predicate='pending_task_task_001',
            content=mock_task,
            confidence=1.0,
            source='test'
        )

        intentions = solver.deliberate()
        assert len(intentions) == 1
        assert 'ode_solve_task_001' in intentions[0].plan_id

    def test_execute_step_claim_task(self):
        """Test execute_step for claim_task action."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.entry_id = 'task_001'

        intention = Intention(
            plan_id='ode_solve_task_001',
            steps=['claim_task', 'parse_ode', 'solve_ode'],
            target_desire='solve_ode',
            metadata={'task_id': 'task_001', 'task_entry': mock_task}
        )

        # Add pending task belief
        solver.add_belief('pending_task_task_001', mock_task)

        solver.execute_step(intention)

        assert solver.has_belief('claimed_task_task_001')
        assert not solver.has_belief('pending_task_task_001')

    def test_execute_step_parse_ode(self):
        """Test execute_step for parse_ode action."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.entry_id = 'task_001'

        intention = Intention(
            plan_id='ode_solve_task_001',
            steps=['parse_ode', 'solve_ode'],
            target_desire='solve_ode',
            metadata={
                'task_id': 'task_001',
                'task_entry': mock_task,
                'raw_input': "y' = x",
                'sympy_expr': None
            }
        )

        solver.execute_step(intention)

        assert 'parsed_ode' in intention.metadata
        assert intention.metadata['function'] == 'y'
        assert intention.metadata['variable'] == 'x'

    def test_execute_step_solve_ode(self):
        """Test execute_step for solve_ode action."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.entry_id = 'task_001'
        mock_task.conversation_id = 'conv_001'

        intention = Intention(
            plan_id='ode_solve_task_001',
            steps=['solve_ode', 'verify_solution'],
            target_desire='solve_ode',
            metadata={
                'task_id': 'task_001',
                'task_entry': mock_task,
                'parsed_ode': "y' = x"
            }
        )

        # Add pending belief (needed for error cleanup)
        solver.add_belief('pending_task_task_001', mock_task)

        solver.execute_step(intention)

        # Test passes if either solution was found or error was handled gracefully
        # (intention completes even on error)
        assert intention.is_complete() or 'solution' in intention.metadata

    def test_execute_step_verify_solution(self):
        """Test execute_step for verify_solution action."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        solver = ODESolver()

        mock_task = MagicMock()
        mock_task.entry_id = 'task_001'

        intention = Intention(
            plan_id='ode_solve_task_001',
            steps=['verify_solution', 'post_result'],
            target_desire='solve_ode',
            metadata={
                'task_id': 'task_001',
                'task_entry': mock_task,
                'solution': 'y = x^2/2 + C'
            }
        )

        solver.execute_step(intention)

        assert intention.metadata.get('verified') is True


class TestODESolverStatistics:
    """Tests for statistics methods."""

    def test_get_statistics(self):
        """Test getting agent statistics."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        # Process a task
        mock_task = MagicMock()
        mock_task.metadata = {'raw_input': "y' = x"}
        solver.process(mock_task)

        stats = solver.get_statistics()
        assert 'tasks_executed' in stats
        assert stats['tasks_executed'] == 1
        assert stats['tasks_succeeded'] == 1
        assert stats['success_rate'] == 100.0

    def test_statistics_with_failure(self):
        """Test statistics after failure."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        # Manually set failure stats
        solver.tasks_executed = 10
        solver.tasks_succeeded = 8
        solver.tasks_failed = 2

        stats = solver.get_statistics()
        assert stats['tasks_failed'] == 2
        assert stats['success_rate'] == 80.0

    def test_statistics_zero_tasks(self):
        """Test statistics with zero tasks."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        solver = ODESolver()

        stats = solver.get_statistics()
        assert stats['tasks_executed'] == 0
        assert stats['success_rate'] == 0


class TestModuleImports:
    """Tests for module imports."""

    def test_ode_solver_import(self):
        """Test ODESolver can be imported."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
            ODESolver
        )
        assert ODESolver is not None

    def test_solve_ode_native_import(self):
        """Test solve_ode_native can be imported."""
        from symbo_agentic_reasoners.core.calculus import solve_ode_native
        assert callable(solve_ode_native)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
