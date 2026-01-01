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
Domain Supervisor Tests
=======================

Comprehensive tests for Domain Supervisors (Tier 2):
- AlgebraSupervisor
- CalculusSupervisor
- Task routing logic
- Directory Facilitator integration
- Blackboard delegation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import uuid

from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import (
    AlgebraSupervisor,
)
from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import (
    CalculusSupervisor,
)
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator,
    create_service_registration,
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard,
    create_entry,
    EntryType,
    EntryStatus,
)


# =============================================================================
# AlgebraSupervisor Tests
# =============================================================================


class TestAlgebraSupervisorInitialization:
    """Tests for AlgebraSupervisor initialization."""

    def test_basic_initialization(self):
        """Should initialize with default agent_id."""
        supervisor = AlgebraSupervisor()

        assert supervisor.agent_id == 'algebra_supervisor_001'
        assert supervisor.tasks_routed == 0
        assert supervisor.tasks_completed == 0
        assert supervisor.tasks_failed == 0

    def test_custom_agent_id(self):
        """Should accept custom agent_id."""
        supervisor = AlgebraSupervisor(agent_id='custom_algebra')

        assert supervisor.agent_id == 'custom_algebra'

    def test_initialization_with_df(self):
        """Should register with Directory Facilitator."""
        df = DirectoryFacilitator()
        supervisor = AlgebraSupervisor(df=df)

        assert supervisor.df is df
        # Should have registered service
        services = df.search(service_type='math.algebra')
        assert len(services) >= 1
        assert any(s.agent_id == 'algebra_supervisor_001' for s in services)

    def test_initialization_with_blackboard(self):
        """Should accept Blackboard instance."""
        bb = Blackboard()
        supervisor = AlgebraSupervisor(blackboard=bb)

        assert supervisor.blackboard is bb

    def test_full_initialization(self):
        """Should initialize with all components."""
        df = DirectoryFacilitator()
        bb = Blackboard()

        supervisor = AlgebraSupervisor(
            agent_id='full_algebra_sup',
            df=df,
            blackboard=bb
        )

        assert supervisor.agent_id == 'full_algebra_sup'
        assert supervisor.df is df
        assert supervisor.blackboard is bb


class TestAlgebraSupervisorTaskAnalysis:
    """Tests for AlgebraSupervisor task analysis and routing."""

    @pytest.fixture
    def supervisor(self):
        """Create supervisor for testing."""
        return AlgebraSupervisor()

    def test_analyze_polynomial_solve(self, supervisor):
        """Should route polynomial solving to polynomial specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'solve x^2 + 2x + 1 = 0', 'operation': 'solve'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.polynomial'
        assert 'polynomial' in result['reason'].lower()

    def test_analyze_polynomial_roots(self, supervisor):
        """Should route roots finding to polynomial specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'find the roots of x^2 - 4', 'operation': 'roots'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.polynomial'

    def test_analyze_quadratic(self, supervisor):
        """Should route quadratic to polynomial specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'quadratic formula for ax^2 + bx + c', 'operation': 'solve'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.polynomial'

    def test_analyze_polynomial_factor(self, supervisor):
        """Should route polynomial factoring to polynomial specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'factor x^2 - 4', 'operation': 'factor'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.polynomial'

    def test_analyze_prime_factor(self, supervisor):
        """Should route integer factoring to number theory."""
        task = Mock()
        task.metadata = {'raw_input': 'find prime factors of 60', 'operation': 'factor'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.numbertheory'

    def test_analyze_gcd(self, supervisor):
        """Should route GCD to number theory."""
        task = Mock()
        task.metadata = {'raw_input': 'find gcd of 12 and 18', 'operation': 'gcd'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.numbertheory'

    def test_analyze_lcm(self, supervisor):
        """Should route LCM to number theory."""
        task = Mock()
        task.metadata = {'raw_input': 'find lcm of 4 and 6', 'operation': 'lcm'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.numbertheory'

    def test_analyze_modular(self, supervisor):
        """Should route modular arithmetic to number theory."""
        task = Mock()
        task.metadata = {'raw_input': '17 mod 5', 'operation': 'compute'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.numbertheory'

    def test_analyze_arithmetic_calculate(self, supervisor):
        """Should route calculation to arithmetic specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'calculate 2 + 3 * 4', 'operation': 'compute'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.arithmetic'

    def test_analyze_arithmetic_default(self, supervisor):
        """Should default to arithmetic for unrecognized tasks."""
        task = Mock()
        task.metadata = {'raw_input': 'some unknown task', 'operation': 'unknown'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.algebra.arithmetic'

    def test_analyze_missing_metadata(self, supervisor):
        """Should handle missing metadata."""
        task = Mock(spec=[])

        result = supervisor._analyze_task(task)

        assert 'service_type' in result
        assert 'reason' in result


class TestAlgebraSupervisorSpecialistFinding:
    """Tests for specialist discovery."""

    def test_find_specialists_with_df(self):
        """Should query DF for specialists."""
        df = Mock()
        df.search.return_value = [
            Mock(agent_id='arith_specialist_001'),
            Mock(agent_id='arith_specialist_002')
        ]
        supervisor = AlgebraSupervisor(df=df)

        specialists = supervisor._find_specialists('math.algebra.arithmetic')

        assert len(specialists) == 2
        df.search.assert_called_with(service_type='math.algebra.arithmetic')

    def test_find_specialists_without_df(self):
        """Should return empty list without DF."""
        supervisor = AlgebraSupervisor(df=None)

        specialists = supervisor._find_specialists('math.algebra.arithmetic')

        assert specialists == []


class TestAlgebraSupervisorDelegation:
    """Tests for task delegation."""

    @pytest.fixture
    def supervisor_with_bb(self):
        """Create supervisor with Blackboard."""
        bb = Blackboard()
        return AlgebraSupervisor(blackboard=bb)

    def test_delegate_creates_entry(self, supervisor_with_bb):
        """Should create delegated task entry."""
        task = Mock()
        task.metadata = {'raw_input': 'test task'}
        task.content = Mock()

        specialist = Mock()
        specialist.agent_id = 'test_specialist'

        routing = {
            'service_type': 'math.algebra.arithmetic',
            'reason': 'test routing'
        }

        result = supervisor_with_bb._delegate_to_specialist(task, specialist, routing)

        assert result is not None
        assert result.metadata['assigned_agent'] == 'test_specialist'
        assert result.metadata['delegated_by'] == 'algebra_supervisor_001'

    def test_delegate_without_blackboard(self):
        """Should return error without Blackboard."""
        supervisor = AlgebraSupervisor(blackboard=None)
        task = Mock()
        task.metadata = {}

        result = supervisor._delegate_to_specialist(task, Mock(), {})

        assert result is None


class TestAlgebraSupervisorProcess:
    """Tests for process method."""

    def test_process_routes_task(self):
        """Should analyze and route task."""
        df = Mock()
        specialist = Mock(agent_id='test_specialist')
        df.search.return_value = [specialist]

        bb = Blackboard()
        supervisor = AlgebraSupervisor(df=df, blackboard=bb)

        task = Mock()
        task.metadata = {'raw_input': 'solve x + 1 = 0'}
        task.content = Mock()

        result = supervisor.process(task)

        assert result is not None
        assert supervisor.tasks_routed == 1

    def test_process_no_specialist_available(self):
        """Should handle missing specialist."""
        df = Mock()
        df.search.return_value = []

        bb = Blackboard()
        supervisor = AlgebraSupervisor(df=df, blackboard=bb)

        task = Mock()
        task.metadata = {'raw_input': 'test'}
        task.content = Mock()

        result = supervisor.process(task)

        assert result.status == EntryStatus.FAILED
        assert supervisor.tasks_failed == 1


class TestAlgebraSupervisorBDI:
    """Tests for BDI interface."""

    def test_update_beliefs(self):
        """Should not raise."""
        supervisor = AlgebraSupervisor()
        supervisor.update_beliefs()

    def test_deliberate(self):
        """Should return list."""
        supervisor = AlgebraSupervisor()
        result = supervisor.deliberate()

        assert isinstance(result, list)

    def test_execute_step(self):
        """Should not raise."""
        supervisor = AlgebraSupervisor()
        intention = Mock()

        supervisor.execute_step(intention)

    def test_get_statistics(self):
        """Should return statistics dict."""
        supervisor = AlgebraSupervisor()
        supervisor.tasks_routed = 5
        supervisor.tasks_completed = 3
        supervisor.tasks_failed = 2

        stats = supervisor.get_statistics()

        assert stats['tasks_routed'] == 5
        assert stats['tasks_completed'] == 3
        assert stats['tasks_failed'] == 2


# =============================================================================
# CalculusSupervisor Tests
# =============================================================================


class TestCalculusSupervisorInitialization:
    """Tests for CalculusSupervisor initialization."""

    def test_basic_initialization(self):
        """Should initialize with default agent_id."""
        supervisor = CalculusSupervisor()

        assert supervisor.agent_id == 'calculus_supervisor_001'
        assert supervisor.tasks_routed == 0
        assert supervisor.symbolic_routes == 0
        assert supervisor.numerical_routes == 0

    def test_custom_agent_id(self):
        """Should accept custom agent_id."""
        supervisor = CalculusSupervisor(agent_id='custom_calculus')

        assert supervisor.agent_id == 'custom_calculus'

    def test_initialization_with_df(self):
        """Should register with Directory Facilitator."""
        df = DirectoryFacilitator()
        supervisor = CalculusSupervisor(df=df)

        assert supervisor.df is df
        services = df.search(service_type='math.calculus')
        assert len(services) >= 1

    def test_initialization_with_blackboard(self):
        """Should accept Blackboard instance."""
        bb = Blackboard()
        supervisor = CalculusSupervisor(blackboard=bb)

        assert supervisor.blackboard is bb


class TestCalculusSupervisorTaskAnalysis:
    """Tests for CalculusSupervisor task analysis and routing."""

    @pytest.fixture
    def supervisor(self):
        """Create supervisor for testing."""
        return CalculusSupervisor()

    def test_analyze_ode(self, supervisor):
        """Should route ODE to differential equation solver."""
        task = Mock()
        task.metadata = {'raw_input': 'solve the ODE dy/dx = x', 'operation': 'solve'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.ode'

    def test_analyze_pde(self, supervisor):
        """Should route PDE to differential equation solver."""
        task = Mock()
        task.metadata = {'raw_input': 'solve the PDE', 'operation': 'solve'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.ode'

    def test_analyze_differential_equation(self, supervisor):
        """Should route differential equation to ODE solver."""
        task = Mock()
        task.metadata = {'raw_input': 'solve differential equation', 'operation': 'solve'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.ode'

    def test_analyze_taylor_series(self, supervisor):
        """Should route Taylor series to series specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'find Taylor series of sin(x)', 'operation': 'expand'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.series'

    def test_analyze_fourier_series(self, supervisor):
        """Should route Fourier series to series specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'Fourier series expansion', 'operation': 'expand'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.series'

    def test_analyze_derivative(self, supervisor):
        """Should route derivative to differentiation specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'find derivative of x^2', 'operation': 'differentiate'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.diff'

    def test_analyze_gradient(self, supervisor):
        """Should route gradient to differentiation specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'compute gradient of f', 'operation': 'gradient'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.diff'

    def test_analyze_jacobian(self, supervisor):
        """Should route Jacobian to differentiation specialist."""
        task = Mock()
        task.metadata = {'raw_input': 'compute Jacobian matrix', 'operation': 'jacobian'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.diff'

    def test_analyze_exact_integration(self, supervisor):
        """Should route exact integration as symbolic."""
        task = Mock()
        task.metadata = {'raw_input': 'find the exact integral of x^2', 'operation': 'integrate'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.integration'
        assert result['engine'] == 'symbolic'

    def test_analyze_closed_form_integration(self, supervisor):
        """Should route closed form integration as symbolic."""
        task = Mock()
        # Note: 'antiderivative' contains 'derivative' which triggers diff routing first
        # Use 'integral' with 'closed form' for symbolic integration
        task.metadata = {'raw_input': 'find the integral in closed form of x^2', 'operation': 'integrate'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.integration'
        assert result['engine'] == 'symbolic'

    def test_analyze_approximate_integration(self, supervisor):
        """Should route approximate integration as numerical."""
        task = Mock()
        task.metadata = {'raw_input': 'approximate the integral of f(x)', 'operation': 'integrate'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.integration'
        assert result['engine'] == 'numerical'

    def test_analyze_area_integration(self, supervisor):
        """Should route area calculation as numerical."""
        task = Mock()
        task.metadata = {'raw_input': 'compute area under curve', 'operation': 'integrate'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.integration'
        assert result['engine'] == 'numerical'

    def test_analyze_default_integration(self, supervisor):
        """Should default to symbolic for plain integration."""
        task = Mock()
        task.metadata = {'raw_input': 'integrate x^3', 'operation': 'integrate'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.integration'
        assert result['engine'] == 'symbolic'

    def test_analyze_default_routing(self, supervisor):
        """Should default to differentiation for unrecognized tasks."""
        task = Mock()
        task.metadata = {'raw_input': 'unknown calculus task', 'operation': 'unknown'}

        result = supervisor._analyze_task(task)

        assert result['service_type'] == 'math.calculus.diff'


class TestCalculusSupervisorStatistics:
    """Tests for statistics tracking."""

    def test_symbolic_route_tracking(self):
        """Should track symbolic routes."""
        df = Mock()
        df.search.return_value = [Mock(agent_id='specialist')]
        bb = Blackboard()
        supervisor = CalculusSupervisor(df=df, blackboard=bb)

        task = Mock()
        task.metadata = {'raw_input': 'find exact integral'}
        task.content = Mock()

        supervisor.process(task)

        assert supervisor.symbolic_routes == 1

    def test_numerical_route_tracking(self):
        """Should track numerical routes."""
        df = Mock()
        df.search.return_value = [Mock(agent_id='specialist')]
        bb = Blackboard()
        supervisor = CalculusSupervisor(df=df, blackboard=bb)

        task = Mock()
        task.metadata = {'raw_input': 'approximate area under curve'}
        task.content = Mock()

        supervisor.process(task)

        assert supervisor.numerical_routes == 1

    def test_get_statistics_includes_routes(self):
        """Statistics should include route counts."""
        supervisor = CalculusSupervisor()
        supervisor.symbolic_routes = 10
        supervisor.numerical_routes = 5

        stats = supervisor.get_statistics()

        assert stats['symbolic_routes'] == 10
        assert stats['numerical_routes'] == 5


class TestCalculusSupervisorProcess:
    """Tests for process method."""

    def test_process_routes_task(self):
        """Should analyze and route task."""
        df = Mock()
        specialist = Mock(agent_id='diff_specialist')
        df.search.return_value = [specialist]

        bb = Blackboard()
        supervisor = CalculusSupervisor(df=df, blackboard=bb)

        task = Mock()
        task.metadata = {'raw_input': 'find derivative of x^2'}
        task.content = Mock()

        result = supervisor.process(task)

        assert result is not None
        assert supervisor.tasks_routed == 1

    def test_process_no_specialist_available(self):
        """Should handle missing specialist."""
        df = Mock()
        df.search.return_value = []

        bb = Blackboard()
        supervisor = CalculusSupervisor(df=df, blackboard=bb)

        task = Mock()
        task.metadata = {'raw_input': 'test'}
        task.content = Mock()

        result = supervisor.process(task)

        assert result.status == EntryStatus.FAILED
        assert supervisor.tasks_failed == 1


class TestCalculusSupervisorBDI:
    """Tests for BDI interface."""

    def test_update_beliefs(self):
        """Should not raise."""
        supervisor = CalculusSupervisor()
        supervisor.update_beliefs()

    def test_deliberate(self):
        """Should return list."""
        supervisor = CalculusSupervisor()
        result = supervisor.deliberate()

        assert isinstance(result, list)

    def test_execute_step(self):
        """Should not raise."""
        supervisor = CalculusSupervisor()
        intention = Mock()

        supervisor.execute_step(intention)


# =============================================================================
# Integration Tests
# =============================================================================


class TestSupervisorIntegration:
    """Integration tests for supervisors."""

    def test_algebra_supervisor_full_workflow(self):
        """Test complete algebra supervisor workflow."""
        df = DirectoryFacilitator()
        bb = Blackboard()

        supervisor = AlgebraSupervisor(
            agent_id='integration_algebra',
            df=df,
            blackboard=bb
        )

        # Register a mock specialist
        specialist_reg = create_service_registration(
            service_type='math.algebra.polynomial',
            agent_id='poly_specialist',
            algorithm='polynomial_ops'
        )
        df.register(specialist_reg)

        # Create task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=Mock(),
            author_agent='test',
            conversation_id='test_algebra_conv',
            metadata={'raw_input': 'solve x^2 + 1 = 0'}
        )

        # Process task
        result = supervisor.process(task)

        assert result is not None
        assert supervisor.tasks_routed == 1

    def test_calculus_supervisor_full_workflow(self):
        """Test complete calculus supervisor workflow."""
        df = DirectoryFacilitator()
        bb = Blackboard()

        supervisor = CalculusSupervisor(
            agent_id='integration_calculus',
            df=df,
            blackboard=bb
        )

        # Register a mock specialist
        specialist_reg = create_service_registration(
            service_type='math.calculus.diff',
            agent_id='diff_specialist',
            algorithm='differentiation'
        )
        df.register(specialist_reg)

        # Create task
        task = create_entry(
            entry_type=EntryType.TASK,
            content=Mock(),
            author_agent='test',
            conversation_id='test_calculus_conv',
            metadata={'raw_input': 'derivative of x^3'}
        )

        # Process task
        result = supervisor.process(task)

        assert result is not None
        assert supervisor.tasks_routed == 1

    def test_multiple_supervisors_coexist(self):
        """Multiple supervisors should work with same DF."""
        df = DirectoryFacilitator()
        bb = Blackboard()

        algebra_sup = AlgebraSupervisor(df=df, blackboard=bb)
        calculus_sup = CalculusSupervisor(df=df, blackboard=bb)

        # Both should be registered
        algebra_services = df.search(service_type='math.algebra')
        calculus_services = df.search(service_type='math.calculus')

        assert len(algebra_services) >= 1
        assert len(calculus_services) >= 1


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
