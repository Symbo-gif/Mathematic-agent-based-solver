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
Comprehensive tests for Physics Supervisor modules to achieve 75%+ coverage.

Tests cover:
- PhysicsEMSupervisor
- PhysicsMechanicsSupervisor
- PhysicsQuantumSupervisor
- PhysicsThermoSupervisor
"""

import pytest
from unittest.mock import Mock, MagicMock


class TestPhysicsEMSupervisor:
    """Tests for PhysicsEMSupervisor to achieve 75%+ coverage."""

    def test_init_without_df(self):
        """Test initialization without DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()
        assert supervisor.agent_id == 'em_supervisor_001'
        assert supervisor.df is None
        assert supervisor.blackboard is None
        assert supervisor.tasks_routed == 0

    def test_init_with_custom_id(self):
        """Test initialization with custom agent ID."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor(agent_id='custom_em_001')
        assert supervisor.agent_id == 'custom_em_001'

    def test_init_with_df(self):
        """Test initialization with DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        supervisor = PhysicsEMSupervisor(df=mock_df)
        assert supervisor.df is mock_df
        mock_df.register.assert_called_once()

    def test_init_with_blackboard(self):
        """Test initialization with Blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        from symbo_agentic_reasoners.core import Blackboard
        bb = Blackboard()
        supervisor = PhysicsEMSupervisor(blackboard=bb)
        assert supervisor.blackboard is bb

    def test_route_task_circuits(self):
        """Test routing to circuits specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()

        # Test various circuit keywords
        for keyword in ['circuit', 'resistor', 'ohm', 'kirchhoff']:
            task = {'problem': f'Calculate the {keyword} value'}
            assert supervisor.route_task(task) == 'physics.em.circuits'

        # Test in operation field
        task = {'operation': 'analyze series parallel circuit'}
        assert supervisor.route_task(task) == 'physics.em.circuits'

    def test_route_task_magnetism(self):
        """Test routing to magnetism specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()

        for keyword in ['magnetic', 'biot', 'faraday', 'induction']:
            task = {'problem': f'Solve the {keyword} problem'}
            assert supervisor.route_task(task) == 'physics.em.magnetism'

    def test_route_task_electrostatics(self):
        """Test routing to electrostatics specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()

        for keyword in ['charge', 'coulomb', 'electric field', 'capacitor']:
            task = {'problem': f'Calculate the {keyword}'}
            assert supervisor.route_task(task) == 'physics.em.electrostatics'

    def test_route_task_default(self):
        """Test default routing when no keywords match."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()
        task = {'problem': 'unknown physics problem'}
        assert supervisor.route_task(task) == 'physics.em.electrostatics'

    def test_process_without_df(self):
        """Test process method without DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()
        task = {'problem': 'Calculate circuit resistance'}
        result = supervisor.process(task)

        assert result['status'] == 'no_specialist'
        assert result['specialist_type'] == 'physics.em.circuits'
        assert supervisor.tasks_routed == 1

    def test_process_with_df_found(self):
        """Test process method with specialist found."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        mock_df.search = Mock(return_value=[{'agent_id': 'circuits_specialist_001'}])

        supervisor = PhysicsEMSupervisor(df=mock_df)
        task = {'problem': 'Calculate circuit resistance'}
        result = supervisor.process(task)

        assert result['status'] == 'routed'
        assert result['specialist_id'] == 'circuits_specialist_001'

    def test_process_with_df_not_found(self):
        """Test process method with no specialist found."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        mock_df.search = Mock(return_value=[])

        supervisor = PhysicsEMSupervisor(df=mock_df)
        task = {'problem': 'Calculate charge'}
        result = supervisor.process(task)

        assert result['status'] == 'no_specialist'

    def test_bdi_methods(self):
        """Test BDI interface methods."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()

        # These are no-op implementations
        supervisor.update_beliefs()
        result = supervisor.deliberate()
        assert result == []
        supervisor.execute_step(Mock())  # Should not raise

    def test_get_statistics(self):
        """Test statistics retrieval."""
        from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import (
            PhysicsEMSupervisor
        )
        supervisor = PhysicsEMSupervisor()
        supervisor.process({'problem': 'test'})
        supervisor.process({'problem': 'test2'})

        stats = supervisor.get_statistics()
        assert stats['tasks_routed'] == 2


class TestPhysicsMechanicsSupervisor:
    """Tests for PhysicsMechanicsSupervisor to achieve 75%+ coverage."""

    def test_init_without_df(self):
        """Test initialization without DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()
        assert supervisor.agent_id == 'mechanics_supervisor_001'
        assert supervisor.df is None
        assert supervisor.tasks_routed == 0

    def test_init_with_df(self):
        """Test initialization with DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        supervisor = PhysicsMechanicsSupervisor(df=mock_df)
        mock_df.register.assert_called_once()

    def test_route_task_energy(self):
        """Test routing to energy specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()

        for keyword in ['energy', 'work', 'kinetic', 'momentum', 'collision']:
            task = {'problem': f'Calculate the {keyword}'}
            assert supervisor.route_task(task) == 'physics.mechanics.energy'

    def test_route_task_dynamics(self):
        """Test routing to dynamics specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()

        for keyword in ['force', 'newton', 'friction', 'centripetal']:
            task = {'problem': f'Solve the {keyword} equation'}
            assert supervisor.route_task(task) == 'physics.mechanics.dynamics'

    def test_route_task_kinematics(self):
        """Test routing to kinematics specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()

        for keyword in ['velocity', 'acceleration', 'projectile', 'trajectory']:
            task = {'problem': f'Find the {keyword}'}
            assert supervisor.route_task(task) == 'physics.mechanics.kinematics'

    def test_route_task_default(self):
        """Test default routing."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()
        task = {'problem': 'unknown problem'}
        assert supervisor.route_task(task) == 'physics.mechanics.kinematics'

    def test_process_without_df(self):
        """Test process without DF."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()
        result = supervisor.process({'problem': 'force problem'})
        assert result['status'] == 'no_specialist'
        assert supervisor.tasks_routed == 1

    def test_process_with_df_found(self):
        """Test process with specialist found."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        mock_df.search = Mock(return_value=[{'agent_id': 'dynamics_001'}])

        supervisor = PhysicsMechanicsSupervisor(df=mock_df)
        result = supervisor.process({'problem': 'force calculation'})

        assert result['status'] == 'routed'
        assert result['specialist_id'] == 'dynamics_001'

    def test_bdi_methods(self):
        """Test BDI interface methods."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()
        supervisor.update_beliefs()
        assert supervisor.deliberate() == []
        supervisor.execute_step(Mock())

    def test_get_statistics(self):
        """Test statistics."""
        from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import (
            PhysicsMechanicsSupervisor
        )
        supervisor = PhysicsMechanicsSupervisor()
        supervisor.process({'problem': 'test'})
        stats = supervisor.get_statistics()
        assert stats['tasks_routed'] == 1


class TestPhysicsQuantumSupervisor:
    """Tests for PhysicsQuantumSupervisor to achieve 75%+ coverage."""

    def test_init_without_df(self):
        """Test initialization without DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()
        assert supervisor.agent_id == 'quantum_supervisor_001'
        assert supervisor.tasks_routed == 0

    def test_init_with_df(self):
        """Test initialization with DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        supervisor = PhysicsQuantumSupervisor(df=mock_df)
        mock_df.register.assert_called_once()

    def test_route_task_systems(self):
        """Test routing to systems specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()

        for keyword in ['hydrogen', 'atom', 'tunneling', 'orbital']:
            task = {'problem': f'Solve the {keyword} problem'}
            assert supervisor.route_task(task) == 'physics.quantum.systems'

    def test_route_task_operators(self):
        """Test routing to operators specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()

        for keyword in ['operator', 'spin', 'commutator', 'eigenvalue']:
            task = {'problem': f'Calculate the {keyword}'}
            assert supervisor.route_task(task) == 'physics.quantum.operators'

    def test_route_task_wavefunction(self):
        """Test routing to wavefunction specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()

        for keyword in ['wavefunction', 'probability', 'normalize', 'uncertainty']:
            task = {'problem': f'Find the {keyword}'}
            assert supervisor.route_task(task) == 'physics.quantum.wavefunction'

    def test_route_task_default(self):
        """Test default routing."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()
        task = {'problem': 'unknown quantum problem'}
        assert supervisor.route_task(task) == 'physics.quantum.wavefunction'

    def test_process_without_df(self):
        """Test process without DF."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()
        result = supervisor.process({'problem': 'hydrogen atom'})
        assert result['status'] == 'no_specialist'

    def test_process_with_df_found(self):
        """Test process with specialist found."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        mock_df.search = Mock(return_value=[{'agent_id': 'systems_001'}])

        supervisor = PhysicsQuantumSupervisor(df=mock_df)
        result = supervisor.process({'problem': 'hydrogen atom energy levels'})

        assert result['status'] == 'routed'

    def test_bdi_methods(self):
        """Test BDI interface methods."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()
        supervisor.update_beliefs()
        assert supervisor.deliberate() == []
        supervisor.execute_step(Mock())

    def test_get_statistics(self):
        """Test statistics."""
        from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import (
            PhysicsQuantumSupervisor
        )
        supervisor = PhysicsQuantumSupervisor()
        supervisor.process({'problem': 'test1'})
        supervisor.process({'problem': 'test2'})
        supervisor.process({'problem': 'test3'})
        stats = supervisor.get_statistics()
        assert stats['tasks_routed'] == 3


class TestPhysicsThermoSupervisor:
    """Tests for PhysicsThermoSupervisor to achieve 75%+ coverage."""

    def test_init_without_df(self):
        """Test initialization without DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()
        assert supervisor.agent_id == 'thermo_supervisor_001'
        assert supervisor.tasks_routed == 0

    def test_init_with_df(self):
        """Test initialization with DirectoryFacilitator."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        supervisor = PhysicsThermoSupervisor(df=mock_df)
        mock_df.register.assert_called_once()

    def test_init_with_blackboard(self):
        """Test initialization with Blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        from symbo_agentic_reasoners.core import Blackboard
        bb = Blackboard()
        supervisor = PhysicsThermoSupervisor(blackboard=bb)
        assert supervisor.blackboard is bb

    def test_route_task_gas(self):
        """Test routing to gas laws specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()

        for keyword in ['gas', 'pressure', 'isothermal', 'carnot', 'entropy']:
            task = {'problem': f'Calculate the {keyword}'}
            assert supervisor.route_task(task) == 'physics.thermo.gas'

    def test_route_task_heat(self):
        """Test routing to heat transfer specialist."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()

        for keyword in ['heat', 'conduction', 'radiation', 'temperature']:
            task = {'problem': f'Find the {keyword}'}
            assert supervisor.route_task(task) == 'physics.thermo.heat'

    def test_route_task_default(self):
        """Test default routing."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()
        task = {'problem': 'unknown thermo problem'}
        assert supervisor.route_task(task) == 'physics.thermo.heat'

    def test_route_task_operation_field(self):
        """Test routing using operation field."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()
        task = {'operation': 'calculate ideal gas volume'}
        assert supervisor.route_task(task) == 'physics.thermo.gas'

    def test_process_without_df(self):
        """Test process without DF."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()
        result = supervisor.process({'problem': 'heat transfer'})
        assert result['status'] == 'no_specialist'
        assert result['specialist_type'] == 'physics.thermo.heat'

    def test_process_with_df_found(self):
        """Test process with specialist found."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        mock_df.search = Mock(return_value=[{'agent_id': 'gas_laws_001'}])

        supervisor = PhysicsThermoSupervisor(df=mock_df)
        result = supervisor.process({'problem': 'ideal gas expansion'})

        assert result['status'] == 'routed'
        assert result['specialist_id'] == 'gas_laws_001'

    def test_process_with_df_not_found(self):
        """Test process with no specialist found."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        mock_df = Mock()
        mock_df.register = Mock()
        mock_df.search = Mock(return_value=[])

        supervisor = PhysicsThermoSupervisor(df=mock_df)
        result = supervisor.process({'problem': 'heat conduction'})

        assert result['status'] == 'no_specialist'

    def test_bdi_methods(self):
        """Test BDI interface methods."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()
        supervisor.update_beliefs()
        assert supervisor.deliberate() == []
        supervisor.execute_step(Mock())

    def test_get_statistics(self):
        """Test statistics retrieval."""
        from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import (
            PhysicsThermoSupervisor
        )
        supervisor = PhysicsThermoSupervisor()

        # Process multiple tasks
        for i in range(5):
            supervisor.process({'problem': f'test problem {i}'})

        stats = supervisor.get_statistics()
        assert stats['tasks_routed'] == 5
        assert 'agent_id' in stats
