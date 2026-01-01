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
Tests for new domain agents: Geometry, Physics, and Logic
"""

import pytest
import math


class TestGeometryDomain:
    """Test geometry specialists and supervisor."""

    def test_euclidean_triangle_properties(self):
        """Test Euclidean geometry triangle calculations."""
        from symbo_agentic_reasoners.agents.specialists.geometry.euclidean_specialist import EuclideanGeometrySpecialist

        specialist = EuclideanGeometrySpecialist()

        # Test triangle from 3 points (right triangle)
        result = specialist.process({
            'operation': 'triangle',
            'p1': (0, 0), 'p2': (3, 0), 'p3': (0, 4)
        })

        assert 'area' in result
        assert result['area'] == 6.0  # 1/2 * 3 * 4
        assert result['is_right'] == True

    def test_euclidean_triangle_area(self):
        """Test simple triangle area formula."""
        from symbo_agentic_reasoners.agents.specialists.geometry.euclidean_specialist import EuclideanGeometrySpecialist

        specialist = EuclideanGeometrySpecialist()
        result = specialist.process({
            'operation': 'triangle_area',
            'base': 10, 'height': 5
        })

        assert result['area'] == 25.0

    def test_euclidean_circle(self):
        """Test circle properties."""
        from symbo_agentic_reasoners.agents.specialists.geometry.euclidean_specialist import EuclideanGeometrySpecialist

        specialist = EuclideanGeometrySpecialist()
        result = specialist.process({
            'operation': 'circle',
            'center': (0, 0), 'radius': 5
        })

        assert 'area' in result
        assert abs(result['area'] - 25 * math.pi) < 0.01

    def test_analytic_line_from_points(self):
        """Test analytic geometry line calculations."""
        from symbo_agentic_reasoners.agents.specialists.geometry.analytic_specialist import AnalyticGeometrySpecialist

        specialist = AnalyticGeometrySpecialist()
        result = specialist.process({
            'operation': 'line',
            'p1': (0, 0), 'p2': (2, 4)
        })

        assert result['slope'] == 2.0
        assert result['y_intercept'] == 0.0

    def test_transformation_rotation(self):
        """Test geometric transformation."""
        from symbo_agentic_reasoners.agents.specialists.geometry.transformation_specialist import TransformationSpecialist

        specialist = TransformationSpecialist()
        result = specialist.process({
            'operation': 'rotate',
            'point': (1, 0),
            'angle': math.pi / 2  # 90 degrees
        })

        assert abs(result['x'] - 0) < 0.001
        assert abs(result['y'] - 1) < 0.001

    def test_trigonometry_law_of_cosines(self):
        """Test law of cosines."""
        from symbo_agentic_reasoners.agents.specialists.geometry.trigonometry_specialist import TrigonometrySpecialist

        specialist = TrigonometrySpecialist()
        # Right triangle 3-4-5
        result = specialist.process({
            'operation': 'law_of_cosines',
            'a': 3, 'b': 4, 'C': math.pi / 2
        })

        assert abs(result['c'] - 5) < 0.001

    def test_geometry_supervisor_routing(self):
        """Test supervisor routes to correct specialist."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import GeometrySupervisor
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

        supervisor = GeometrySupervisor()

        # The geometry supervisor expects a blackboard entry format
        # Test the internal _analyze_task method directly for routing logic
        class MockEntry:
            def __init__(self, raw_input):
                self.metadata = {'raw_input': raw_input}

        # Triangle should route to euclidean
        result = supervisor._analyze_task(MockEntry('Calculate triangle area'))
        assert 'euclidean' in result['service_type']

        # Line/slope should route to analytic
        result = supervisor._analyze_task(MockEntry('Find slope of line'))
        assert 'analytic' in result['service_type']

        # Rotation should route to transformations
        result = supervisor._analyze_task(MockEntry('Rotate point by quarter turn'))
        assert 'transformation' in result['service_type']

        # Sin/cos should route to trigonometry
        result = supervisor._analyze_task(MockEntry('Calculate sin(45 degrees)'))
        assert 'trigonometry' in result['service_type']


class TestPhysicsMechanicsDomain:
    """Test physics mechanics specialists."""

    def test_kinematics_projectile(self):
        """Test projectile motion calculations."""
        from symbo_agentic_reasoners.agents.specialists.physics.mechanics.kinematics_specialist import KinematicsSpecialist

        specialist = KinematicsSpecialist()
        result = specialist.process({
            'operation': 'projectile',
            'v0': 20, 'angle': math.pi / 4, 'h0': 0
        })

        assert 'range' in result
        assert 'max_height' in result
        assert result['range'] > 0

    def test_kinematics_free_fall(self):
        """Test free fall calculations."""
        from symbo_agentic_reasoners.agents.specialists.physics.mechanics.kinematics_specialist import KinematicsSpecialist

        specialist = KinematicsSpecialist()
        result = specialist.process({
            'operation': 'free_fall',
            't': 2
        })

        assert abs(result['final_velocity'] - 19.62) < 0.1  # v = gt
        assert abs(result['height'] - 19.62) < 0.1  # h = 0.5*g*t^2

    def test_dynamics_friction(self):
        """Test friction force calculations."""
        from symbo_agentic_reasoners.agents.specialists.physics.mechanics.dynamics_specialist import DynamicsSpecialist

        specialist = DynamicsSpecialist()
        result = specialist.process({
            'operation': 'friction',
            'N': 100, 'mu': 0.3
        })

        assert result['friction_force'] == 30.0

    def test_energy_kinetic(self):
        """Test kinetic energy calculation."""
        from symbo_agentic_reasoners.agents.specialists.physics.mechanics.energy_specialist import EnergySpecialist

        specialist = EnergySpecialist()
        result = specialist.process({
            'operation': 'kinetic_energy',
            'm': 10, 'v': 5
        })

        assert result['KE'] == 125.0  # 0.5 * 10 * 25


class TestPhysicsEMDomain:
    """Test physics electromagnetism specialists."""

    def test_coulombs_law(self):
        """Test Coulomb's law calculation."""
        from symbo_agentic_reasoners.agents.specialists.physics.electromagnetism.electrostatics_specialist import ElectrostaticsSpecialist

        specialist = ElectrostaticsSpecialist()
        result = specialist.process({
            'operation': 'coulomb',
            'q1': 1e-6, 'q2': 1e-6, 'r': 0.1
        })

        assert 'force' in result
        assert result['force'] > 0

    def test_ohms_law(self):
        """Test Ohm's law calculation."""
        from symbo_agentic_reasoners.agents.specialists.physics.electromagnetism.circuits_specialist import CircuitsSpecialist

        specialist = CircuitsSpecialist()
        result = specialist.process({
            'operation': 'ohm',
            'V': 12, 'R': 4
        })

        assert result['I'] == 3.0

    def test_resistors_series(self):
        """Test series resistor combination."""
        from symbo_agentic_reasoners.agents.specialists.physics.electromagnetism.circuits_specialist import CircuitsSpecialist

        specialist = CircuitsSpecialist()
        result = specialist.process({
            'operation': 'series',
            'resistors': [10, 20, 30]
        })

        assert result['R_equivalent'] == 60

    def test_magnetic_field_wire(self):
        """Test magnetic field from wire."""
        from symbo_agentic_reasoners.agents.specialists.physics.electromagnetism.magnetism_specialist import MagnetismSpecialist

        specialist = MagnetismSpecialist()
        result = specialist.process({
            'operation': 'field_wire',
            'I': 5, 'r': 0.1
        })

        assert 'B' in result
        assert result['B'] > 0


class TestPhysicsThermoDomain:
    """Test physics thermodynamics specialists."""

    def test_ideal_gas_law(self):
        """Test ideal gas law calculation."""
        from symbo_agentic_reasoners.agents.specialists.physics.thermodynamics.gas_laws_specialist import GasLawsSpecialist

        specialist = GasLawsSpecialist()
        result = specialist.process({
            'operation': 'ideal_gas',
            'n': 1, 'T': 273.15, 'V': 0.0224
        })

        assert 'P' in result
        # Should be approximately 1 atm (101325 Pa)
        assert abs(result['P'] - 101325) < 2000

    def test_heat_capacity(self):
        """Test heat capacity calculation."""
        from symbo_agentic_reasoners.agents.specialists.physics.thermodynamics.heat_specialist import HeatTransferSpecialist

        specialist = HeatTransferSpecialist()
        result = specialist.process({
            'operation': 'heat_capacity',
            'm': 1, 'c': 4186, 'dT': 10  # Water, 1kg, 10K rise
        })

        assert result['Q'] == 41860


class TestPhysicsQuantumDomain:
    """Test physics quantum mechanics specialists."""

    def test_hydrogen_energy_levels(self):
        """Test hydrogen atom energy levels."""
        from symbo_agentic_reasoners.agents.specialists.physics.quantum.systems_specialist import QuantumSystemsSpecialist

        specialist = QuantumSystemsSpecialist()
        result = specialist.process({
            'operation': 'hydrogen_energy',
            'n': 1
        })

        assert abs(result['energy_eV'] - (-13.6)) < 0.1

    def test_uncertainty_principle(self):
        """Test Heisenberg uncertainty calculation."""
        from symbo_agentic_reasoners.agents.specialists.physics.quantum.wavefunction_specialist import WavefunctionSpecialist

        specialist = WavefunctionSpecialist()
        result = specialist.process({
            'operation': 'uncertainty',
            'dx': 1e-10  # 1 Angstrom position uncertainty
        })

        assert 'min_momentum_uncertainty' in result
        assert result['min_momentum_uncertainty'] > 0

    def test_angular_momentum_eigenvalue(self):
        """Test angular momentum eigenvalues."""
        from symbo_agentic_reasoners.agents.specialists.physics.quantum.operators_specialist import OperatorsSpecialist

        specialist = OperatorsSpecialist()
        result = specialist.process({
            'operation': 'angular_momentum',
            'l': 2, 'm': 1
        })

        assert 'L_squared' in result
        assert 'L_z' in result
        assert result['num_m_states'] == 5  # 2*l+1


class TestLogicDomain:
    """Test logic specialists."""

    def test_truth_table(self):
        """Test truth table generation."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import PropositionalLogicSpecialist

        specialist = PropositionalLogicSpecialist()
        result = specialist.process({
            'operation': 'truth_table',
            'variables': ['P', 'Q'],
            'expression': 'P and Q'
        })

        assert 'truth_table' in result
        assert len(result['truth_table']) == 4  # 2^2 rows

    def test_tautology_check(self):
        """Test tautology detection."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import PropositionalLogicSpecialist

        specialist = PropositionalLogicSpecialist()

        # P or not P is a tautology
        result = specialist.process({
            'operation': 'tautology',
            'variables': ['P'],
            'expression': 'P or not P'
        })
        assert result['is_tautology'] == True

        # P and not P is not a tautology
        result = specialist.process({
            'operation': 'tautology',
            'variables': ['P'],
            'expression': 'P and not P'
        })
        assert result['is_tautology'] == False

    def test_contradiction_check(self):
        """Test contradiction detection."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import PropositionalLogicSpecialist

        specialist = PropositionalLogicSpecialist()
        result = specialist.process({
            'operation': 'contradiction',
            'variables': ['P'],
            'expression': 'P and not P'
        })

        assert result['is_contradiction'] == True

    def test_universal_quantification(self):
        """Test universal quantification."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import PredicateLogicSpecialist

        specialist = PredicateLogicSpecialist()
        result = specialist.process({
            'operation': 'forall',
            'domain': [1, 2, 3, 4, 5],
            'predicate': 'lambda x: x > 0'
        })

        assert result['forall'] == True

    def test_mathematical_induction(self):
        """Test induction proof verification."""
        from symbo_agentic_reasoners.agents.specialists.logic.proof_specialist import ProofSpecialist

        specialist = ProofSpecialist()
        result = specialist.process({
            'operation': 'induction',
            'base_case': {'n': 0, 'verified': True, 'work': 'P(0) holds'},
            'inductive_step': {'verified': True, 'work': 'P(k) -> P(k+1)'},
            'property': 'P'
        })

        assert result['proof_valid'] == True

    def test_logic_supervisor_routing(self):
        """Test logic supervisor routing."""
        from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import LogicSupervisor

        supervisor = LogicSupervisor()

        # Truth table should route to propositional
        result = supervisor.process({'problem': 'Generate truth table'})
        assert 'propositional' in result['specialist_type']

        # Proof should route to proof specialist
        result = supervisor.process({'problem': 'Prove by induction'})
        assert 'proof' in result['specialist_type']


class TestDomainClassification:
    """Test domain classification with new domains."""

    def test_physics_mechanics_classification(self):
        """Test physics mechanics domain is classified correctly."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            ProblemAnalysisTeam, MathDomain
        )

        team = ProblemAnalysisTeam()
        result = team.process("Calculate the velocity after 5 seconds of free fall")
        assert result.domain == MathDomain.PHYSICS_MECHANICS

    def test_physics_em_classification(self):
        """Test physics EM domain is classified correctly."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            ProblemAnalysisTeam, MathDomain
        )

        team = ProblemAnalysisTeam()
        result = team.process("Find the electric field from a point charge")
        assert result.domain == MathDomain.PHYSICS_EM

    def test_geometry_classification(self):
        """Test geometry domain is classified correctly."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            ProblemAnalysisTeam, MathDomain
        )

        team = ProblemAnalysisTeam()
        result = team.process("Calculate the area of a triangle with base 5 and height 3")
        assert result.domain == MathDomain.GEOMETRY

    def test_logic_classification(self):
        """Test logic domain is classified correctly."""
        from symbo_agentic_reasoners.agents.base.problem_analysis import (
            ProblemAnalysisTeam, MathDomain
        )

        team = ProblemAnalysisTeam()
        result = team.process("Generate truth table for P implies Q")
        assert result.domain == MathDomain.LOGIC


class TestAgentRegistryNewDomains:
    """Test agent registry includes new domains."""

    def test_all_new_domains_registered(self):
        """Test all new domains are in the registry."""
        from symbo_agentic_reasoners.infrastructure.agent_registry import get_all_domains

        domains = get_all_domains()

        assert 'geometry' in domains
        assert 'physics_mechanics' in domains
        assert 'physics_em' in domains
        assert 'physics_thermo' in domains
        assert 'physics_quantum' in domains
        assert 'logic' in domains

    def test_correct_agent_counts(self):
        """Test each new domain has expected number of agents."""
        from symbo_agentic_reasoners.infrastructure.agent_registry import AGENT_SPECS

        assert len(AGENT_SPECS['geometry']) == 5  # supervisor + 4 specialists
        assert len(AGENT_SPECS['physics_mechanics']) == 4  # supervisor + 3 specialists
        assert len(AGENT_SPECS['physics_em']) == 4  # supervisor + 3 specialists
        assert len(AGENT_SPECS['physics_thermo']) == 3  # supervisor + 2 specialists
        assert len(AGENT_SPECS['physics_quantum']) == 4  # supervisor + 3 specialists
        assert len(AGENT_SPECS['logic']) == 4  # supervisor + 3 specialists

    def test_total_agent_count(self):
        """Test total agent count across all domains."""
        from symbo_agentic_reasoners.infrastructure.agent_registry import AGENT_SPECS

        total = sum(len(specs) for specs in AGENT_SPECS.values())
        # Original: algebra(5) + calculus(6) + linear_algebra(4) + statistics(4) + discrete_math(3) = 22
        # New: geometry(5) + physics_mechanics(4) + physics_em(4) + physics_thermo(3) + physics_quantum(4) + logic(4) = 24
        # Total = 46
        assert total == 46


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
