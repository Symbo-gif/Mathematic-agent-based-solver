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
Pilot Solver Tests
==================

Comprehensive tests for the Pilot Solver agent:
- Initialization and configuration
- SymPy execution wrapper
- Blackboard integration
- Service registration

NOTE: These tests are SKIPPED because the pilot_solver module has been
archived as part of the SymPy-free restructuring. The solvers/ directory
was moved to _archived_originals/restructured_out/.
"""

import pytest

# Skip all tests in this module - pilot_solver has been archived
pytestmark = pytest.mark.skip(reason="pilot_solver module has been archived - solvers/ moved to _archived_originals")

# Keep imports below for reference but they won't be executed
from symbo_agentic_reasoners.core.symbolic import Symbol, symbols, sin, cos, exp, sqrt
from unittest.mock import Mock, patch, MagicMock

from symbo_agentic_reasoners.core.blackboard import (
    Blackboard,
    BlackboardEntry,
    EntryType,
    EntryStatus,
)
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator,
)


# Mock PilotSolverAgent class for test collection (module is skipped)
class PilotSolverAgent:
    """Mock class to prevent collection errors - actual module is archived."""
    def __init__(self, agent_id='pilot_solver_001', blackboard=None, df=None):
        self.agent_id = agent_id
        self.blackboard = blackboard
        self.df = df


# =============================================================================
# Initialization Tests
# =============================================================================


class TestPilotSolverInitialization:
    """Tests for PilotSolverAgent initialization."""

    def test_basic_initialization(self):
        """Should initialize with default values."""
        solver = PilotSolverAgent()
        assert solver is not None
        assert solver.agent_id == 'pilot_solver_001'

    def test_custom_agent_id(self):
        """Should accept custom agent ID."""
        solver = PilotSolverAgent(agent_id='custom_solver_001')
        assert solver.agent_id == 'custom_solver_001'

    def test_initialization_with_blackboard(self):
        """Should initialize with blackboard."""
        bb = Blackboard()
        solver = PilotSolverAgent(blackboard=bb)
        assert solver.blackboard is bb

    def test_initialization_with_df(self):
        """Should initialize with directory facilitator."""
        df = DirectoryFacilitator()
        solver = PilotSolverAgent(df=df)
        assert solver.df is df

    def test_full_initialization(self):
        """Should initialize with all components."""
        bb = Blackboard()
        df = DirectoryFacilitator()
        solver = PilotSolverAgent(
            agent_id='test_solver',
            df=df,
            blackboard=bb
        )
        assert solver.agent_id == 'test_solver'
        assert solver.blackboard is bb
        assert solver.df is df


# =============================================================================
# Execution Tests
# =============================================================================


class TestPilotSolverExecution:
    """Tests for PilotSolverAgent execution."""

    @pytest.fixture
    def solver(self):
        """Create a PilotSolverAgent instance."""
        return PilotSolverAgent()

    def test_execute_derivative(self, solver):
        """Should execute derivative."""
        result = solver._execute('derivative', 'x**2', 'x')
        assert result is not None
        # d/dx(x^2) = 2x
        assert str(result) == '2*x'

    def test_execute_integral(self, solver):
        """Should execute integral."""
        result = solver._execute('integral', 'x', 'x')
        assert result is not None
        # integral of x dx = x^2/2
        assert 'x**2' in str(result)

    def test_execute_simplify(self, solver):
        """Should execute simplify."""
        result = solver._execute('simplify', 'x + x', 'x')
        assert result is not None
        # x + x = 2*x
        assert str(result) == '2*x'

    def test_execute_unknown_defaults_to_simplify(self, solver):
        """Unknown operation should default to simplify."""
        result = solver._execute('unknown_op', 'x + x', 'x')
        assert result is not None
        # Default simplify: x + x = 2*x
        assert str(result) == '2*x'

    def test_execute_expand(self, solver):
        """Should execute expand."""
        result = solver._execute('expand', '(x + 1)**2', 'x')
        assert result is not None
        # (x+1)^2 = x^2 + 2x + 1
        result_str = str(result)
        assert 'x**2' in result_str

    def test_execute_factor(self, solver):
        """Should execute factor."""
        result = solver._execute('factor', 'x**2 - 1', 'x')
        assert result is not None
        # x^2 - 1 = (x-1)(x+1)
        result_str = str(result)
        assert '(' in result_str

    def test_execute_with_trigonometric(self, solver):
        """Should handle trigonometric functions."""
        result = solver._execute('derivative', 'sin(x)', 'x')
        assert result is not None
        # d/dx(sin(x)) = cos(x)
        assert str(result) == 'cos(x)'


# =============================================================================
# OMDoc Conversion Tests
# =============================================================================


class TestSymPyToOMDoc:
    """Tests for SymPy to OMDoc conversion."""

    @pytest.fixture
    def solver(self):
        """Create a PilotSolverAgent instance."""
        return PilotSolverAgent()

    def test_convert_number(self, solver):
        """Should convert number to OMDoc."""
        # Commented out - sympy not imported (module archived)
        # result = solver._sympy_to_omdoc(sp.Integer(42))
        # assert result is not None
        pass

    def test_convert_symbol(self, solver):
        """Should convert symbol to OMDoc."""
        # Commented out - sympy not imported (module archived)
        # x = Symbol('x')
        # result = solver._sympy_to_omdoc(x)
        # assert result is not None
        pass

    def test_convert_expression(self, solver):
        """Should convert expression to OMDoc."""
        # Commented out - sympy not imported (module archived)
        # x = Symbol('x')
        # expr = x**2 + 2*x + 1
        # result = solver._sympy_to_omdoc(expr)
        # assert result is not None
        pass


# =============================================================================
# BDI Interface Tests
# =============================================================================


class TestPilotSolverBDI:
    """Tests for BDI interface methods."""

    @pytest.fixture
    def solver(self):
        """Create a PilotSolverAgent instance."""
        return PilotSolverAgent()

    def test_update_beliefs(self, solver):
        """update_beliefs should not raise."""
        solver.update_beliefs()

    def test_deliberate(self, solver):
        """deliberate should return list."""
        result = solver.deliberate()
        assert isinstance(result, list)

    def test_execute_step(self, solver):
        """execute_step should not raise."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention
        intention = Mock(spec=Intention)
        solver.execute_step(intention)

    def test_get_statistics(self, solver):
        """Should return statistics."""
        stats = solver.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# Integration Tests
# =============================================================================


class TestPilotSolverIntegration:
    """Integration tests for PilotSolverAgent."""

    def test_full_pipeline(self):
        """Test full solve pipeline."""
        bb = Blackboard()
        df = DirectoryFacilitator()
        solver = PilotSolverAgent(blackboard=bb, df=df)

        # Execute a computation
        result = solver._execute('derivative', 'x**3', 'x')
        assert result is not None
        assert str(result) == '3*x**2'


# =============================================================================
# Edge Cases
# =============================================================================


class TestPilotSolverEdgeCases:
    """Edge case tests."""

    @pytest.fixture
    def solver(self):
        """Create a PilotSolverAgent instance."""
        return PilotSolverAgent()

    def test_empty_expression(self, solver):
        """Should handle empty expression."""
        try:
            result = solver._execute('simplify', '', 'x')
            # May return None or raise
        except Exception:
            pass  # Expected

    def test_complex_expression(self, solver):
        """Should handle complex expressions."""
        result = solver._execute(
            'simplify',
            'sin(x)**2 + cos(x)**2',
            'x'
        )
        assert result is not None
        # sin^2(x) + cos^2(x) = 1
        assert str(result) == '1'

    def test_multiple_variables(self, solver):
        """Should handle multiple variables."""
        result = solver._execute('derivative', 'x*y', 'x')
        assert result is not None
        # d/dx(x*y) = y
        assert str(result) == 'y'

    def test_numerical_expression(self, solver):
        """Should handle numerical expressions."""
        result = solver._execute('simplify', '2 + 2', 'x')
        assert result is not None
        assert result == 4


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
