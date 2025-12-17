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
AGENT REGISTRY - Central registration of all agents with AgentPool
===================================================================

This module provides lazy registration of all system agents. Agent classes
are imported only when needed (when wake_for_domain is called), keeping
startup fast and memory minimal.

USAGE:
------
    from symbo_agentic_reasoners.infrastructure import AgentPool, AgentManagementSystem
    from symbo_agentic_reasoners.infrastructure.agent_registry import register_all_agents

    ams = AgentManagementSystem()
    pool = AgentPool(ams)
    register_all_agents(pool)
    pool.start()
"""

from typing import Dict, List, Callable, Type, Any
import logging

from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool, AgentSpec
from symbo_agentic_reasoners.infrastructure.ams import AgentType

logger = logging.getLogger('symbo_agentic_reasoners.agent_registry')


# Lazy import functions - only load agent classes when needed
def _get_algebra_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
    return AlgebraSupervisor

def _get_calculus_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
    return CalculusSupervisor

def _get_linalg_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import LinearAlgebraSupervisor
    return LinearAlgebraSupervisor

def _get_stats_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import StatisticsSupervisor
    return StatisticsSupervisor

def _get_discrete_math_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import DiscreteMathSupervisor
    return DiscreteMathSupervisor

# Algebra specialists
def _get_arithmetic_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import ArithmeticSpecialist
    return ArithmeticSpecialist

def _get_polynomial_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import PolynomialSpecialist
    return PolynomialSpecialist

def _get_number_theory_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import NumberTheorySpecialist
    return NumberTheorySpecialist

def _get_equation_system_solver() -> Type:
    from symbo_agentic_reasoners.agents.specialists.algebra.equation_system_solver import EquationSystemSolver
    return EquationSystemSolver

# Calculus specialists
def _get_differentiation_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist
    return DifferentiationSpecialist

def _get_integration_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist
    return IntegrationSpecialist

def _get_limit_evaluator() -> Type:
    from symbo_agentic_reasoners.agents.specialists.calculus.limit_evaluator import LimitEvaluator
    return LimitEvaluator

def _get_ode_solver() -> Type:
    from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import ODESolver
    return ODESolver

def _get_series_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.calculus.series_specialist import SeriesSpecialist
    return SeriesSpecialist

# Linear algebra specialists
def _get_matrix_ops_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.linear_algebra.matrix_ops_specialist import MatrixOperationsSpecialist
    return MatrixOperationsSpecialist

def _get_decomposition_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.linear_algebra.decomposition_specialist import DecompositionSpecialist
    return DecompositionSpecialist

def _get_vector_space_analyst() -> Type:
    from symbo_agentic_reasoners.agents.specialists.linear_algebra.vector_space_analyst import VectorSpaceAnalyst
    return VectorSpaceAnalyst

# Statistics specialists
def _get_bayesian_engine() -> Type:
    from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_engine import BayesianInferenceEngine
    return BayesianInferenceEngine

def _get_distribution_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.statistics.distribution_specialist import DistributionSpecialist
    return DistributionSpecialist

def _get_frequentist_agent() -> Type:
    from symbo_agentic_reasoners.agents.specialists.statistics.frequentist_agent import FrequentistAgent
    return FrequentistAgent

# Discrete math specialists
def _get_combinatorics_agent() -> Type:
    from symbo_agentic_reasoners.agents.specialists.discrete_math.combinatorics_agent import CombinatoricsAgent
    return CombinatoricsAgent

def _get_graph_theory_agent() -> Type:
    from symbo_agentic_reasoners.agents.specialists.discrete_math.graph_theory_agent import GraphTheoryAgent
    return GraphTheoryAgent


# Geometry specialists
def _get_geometry_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import GeometrySupervisor
    return GeometrySupervisor

def _get_euclidean_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.geometry.euclidean_specialist import EuclideanGeometrySpecialist
    return EuclideanGeometrySpecialist

def _get_analytic_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.geometry.analytic_specialist import AnalyticGeometrySpecialist
    return AnalyticGeometrySpecialist

def _get_transformation_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.geometry.transformation_specialist import TransformationSpecialist
    return TransformationSpecialist

def _get_trigonometry_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.geometry.trigonometry_specialist import TrigonometrySpecialist
    return TrigonometrySpecialist


# Physics - Mechanics specialists
def _get_mechanics_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import PhysicsMechanicsSupervisor
    return PhysicsMechanicsSupervisor

def _get_kinematics_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.mechanics.kinematics_specialist import KinematicsSpecialist
    return KinematicsSpecialist

def _get_dynamics_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.mechanics.dynamics_specialist import DynamicsSpecialist
    return DynamicsSpecialist

def _get_energy_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.mechanics.energy_specialist import EnergySpecialist
    return EnergySpecialist


# Physics - Electromagnetism specialists
def _get_em_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor import PhysicsEMSupervisor
    return PhysicsEMSupervisor

def _get_electrostatics_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.electromagnetism.electrostatics_specialist import ElectrostaticsSpecialist
    return ElectrostaticsSpecialist

def _get_magnetism_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.electromagnetism.magnetism_specialist import MagnetismSpecialist
    return MagnetismSpecialist

def _get_circuits_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.electromagnetism.circuits_specialist import CircuitsSpecialist
    return CircuitsSpecialist


# Physics - Thermodynamics specialists
def _get_thermo_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor import PhysicsThermoSupervisor
    return PhysicsThermoSupervisor

def _get_heat_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.thermodynamics.heat_specialist import HeatTransferSpecialist
    return HeatTransferSpecialist

def _get_gas_laws_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.thermodynamics.gas_laws_specialist import GasLawsSpecialist
    return GasLawsSpecialist


# Physics - Quantum specialists
def _get_quantum_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor import PhysicsQuantumSupervisor
    return PhysicsQuantumSupervisor

def _get_wavefunction_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.quantum.wavefunction_specialist import WavefunctionSpecialist
    return WavefunctionSpecialist

def _get_operators_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.quantum.operators_specialist import OperatorsSpecialist
    return OperatorsSpecialist

def _get_systems_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.physics.quantum.systems_specialist import QuantumSystemsSpecialist
    return QuantumSystemsSpecialist


# Logic specialists
def _get_logic_supervisor() -> Type:
    from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import LogicSupervisor
    return LogicSupervisor

def _get_propositional_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import PropositionalLogicSpecialist
    return PropositionalLogicSpecialist

def _get_predicate_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import PredicateLogicSpecialist
    return PredicateLogicSpecialist

def _get_proof_specialist() -> Type:
    from symbo_agentic_reasoners.agents.specialists.logic.proof_specialist import ProofSpecialist
    return ProofSpecialist


class LazyAgentClass:
    """
    Wrapper that lazily loads an agent class on first access.

    This allows us to register specs without importing all agent modules,
    keeping startup fast and memory low.
    """
    def __init__(self, loader: Callable[[], Type]):
        self._loader = loader
        self._class = None

    def __call__(self, *args, **kwargs):
        if self._class is None:
            self._class = self._loader()
        return self._class(*args, **kwargs)

    @property
    def __name__(self):
        return self._loader.__name__.replace('_get_', '')


# Agent specifications organized by domain
AGENT_SPECS: Dict[str, List[AgentSpec]] = {
    'algebra': [
        AgentSpec(
            agent_id='algebra_supervisor',
            agent_class=LazyAgentClass(_get_algebra_supervisor),
            domain='algebra',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.algebra'],
            standby_timeout_seconds=600,  # 10 min for supervisors
        ),
        AgentSpec(
            agent_id='arithmetic_specialist',
            agent_class=LazyAgentClass(_get_arithmetic_specialist),
            domain='algebra',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.algebra.arithmetic'],
        ),
        AgentSpec(
            agent_id='polynomial_specialist',
            agent_class=LazyAgentClass(_get_polynomial_specialist),
            domain='algebra',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.algebra.polynomial'],
        ),
        AgentSpec(
            agent_id='number_theory_specialist',
            agent_class=LazyAgentClass(_get_number_theory_specialist),
            domain='algebra',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.algebra.numbertheory'],
        ),
        AgentSpec(
            agent_id='equation_system_solver',
            agent_class=LazyAgentClass(_get_equation_system_solver),
            domain='algebra',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.algebra.equations'],
        ),
    ],
    'calculus': [
        AgentSpec(
            agent_id='calculus_supervisor',
            agent_class=LazyAgentClass(_get_calculus_supervisor),
            domain='calculus',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.calculus'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='differentiation_specialist',
            agent_class=LazyAgentClass(_get_differentiation_specialist),
            domain='calculus',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.calculus.differentiation'],
        ),
        AgentSpec(
            agent_id='integration_specialist',
            agent_class=LazyAgentClass(_get_integration_specialist),
            domain='calculus',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.calculus.integration'],
        ),
        AgentSpec(
            agent_id='limit_evaluator',
            agent_class=LazyAgentClass(_get_limit_evaluator),
            domain='calculus',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.calculus.limits'],
        ),
        AgentSpec(
            agent_id='ode_solver',
            agent_class=LazyAgentClass(_get_ode_solver),
            domain='calculus',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.calculus.ode'],
        ),
        AgentSpec(
            agent_id='series_specialist',
            agent_class=LazyAgentClass(_get_series_specialist),
            domain='calculus',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.calculus.series'],
        ),
    ],
    'linear_algebra': [
        AgentSpec(
            agent_id='linalg_supervisor',
            agent_class=LazyAgentClass(_get_linalg_supervisor),
            domain='linear_algebra',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.linalg'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='matrix_ops_specialist',
            agent_class=LazyAgentClass(_get_matrix_ops_specialist),
            domain='linear_algebra',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.linalg.matrix'],
        ),
        AgentSpec(
            agent_id='decomposition_specialist',
            agent_class=LazyAgentClass(_get_decomposition_specialist),
            domain='linear_algebra',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.linalg.decomposition'],
        ),
        AgentSpec(
            agent_id='vector_space_analyst',
            agent_class=LazyAgentClass(_get_vector_space_analyst),
            domain='linear_algebra',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.linalg.vectorspace'],
        ),
    ],
    'statistics': [
        AgentSpec(
            agent_id='stats_supervisor',
            agent_class=LazyAgentClass(_get_stats_supervisor),
            domain='statistics',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.stats'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='bayesian_engine',
            agent_class=LazyAgentClass(_get_bayesian_engine),
            domain='statistics',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.stats.bayesian'],
        ),
        AgentSpec(
            agent_id='distribution_specialist',
            agent_class=LazyAgentClass(_get_distribution_specialist),
            domain='statistics',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.stats.distributions'],
        ),
        AgentSpec(
            agent_id='frequentist_agent',
            agent_class=LazyAgentClass(_get_frequentist_agent),
            domain='statistics',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.stats.frequentist'],
        ),
    ],
    'discrete_math': [
        AgentSpec(
            agent_id='discrete_math_supervisor',
            agent_class=LazyAgentClass(_get_discrete_math_supervisor),
            domain='discrete_math',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.discrete'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='combinatorics_agent',
            agent_class=LazyAgentClass(_get_combinatorics_agent),
            domain='discrete_math',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.discrete.combinatorics'],
        ),
        AgentSpec(
            agent_id='graph_theory_agent',
            agent_class=LazyAgentClass(_get_graph_theory_agent),
            domain='discrete_math',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.discrete.graphs'],
        ),
    ],
    'geometry': [
        AgentSpec(
            agent_id='geometry_supervisor',
            agent_class=LazyAgentClass(_get_geometry_supervisor),
            domain='geometry',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.geometry'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='euclidean_specialist',
            agent_class=LazyAgentClass(_get_euclidean_specialist),
            domain='geometry',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.geometry.euclidean'],
        ),
        AgentSpec(
            agent_id='analytic_specialist',
            agent_class=LazyAgentClass(_get_analytic_specialist),
            domain='geometry',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.geometry.analytic'],
        ),
        AgentSpec(
            agent_id='transformation_specialist',
            agent_class=LazyAgentClass(_get_transformation_specialist),
            domain='geometry',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.geometry.transformations'],
        ),
        AgentSpec(
            agent_id='trigonometry_specialist',
            agent_class=LazyAgentClass(_get_trigonometry_specialist),
            domain='geometry',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.geometry.trigonometry'],
        ),
    ],
    'physics_mechanics': [
        AgentSpec(
            agent_id='mechanics_supervisor',
            agent_class=LazyAgentClass(_get_mechanics_supervisor),
            domain='physics_mechanics',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.mechanics'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='kinematics_specialist',
            agent_class=LazyAgentClass(_get_kinematics_specialist),
            domain='physics_mechanics',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.mechanics.kinematics'],
        ),
        AgentSpec(
            agent_id='dynamics_specialist',
            agent_class=LazyAgentClass(_get_dynamics_specialist),
            domain='physics_mechanics',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.mechanics.dynamics'],
        ),
        AgentSpec(
            agent_id='energy_specialist',
            agent_class=LazyAgentClass(_get_energy_specialist),
            domain='physics_mechanics',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.mechanics.energy'],
        ),
    ],
    'physics_em': [
        AgentSpec(
            agent_id='em_supervisor',
            agent_class=LazyAgentClass(_get_em_supervisor),
            domain='physics_em',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.electromagnetism'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='electrostatics_specialist',
            agent_class=LazyAgentClass(_get_electrostatics_specialist),
            domain='physics_em',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.em.electrostatics'],
        ),
        AgentSpec(
            agent_id='magnetism_specialist',
            agent_class=LazyAgentClass(_get_magnetism_specialist),
            domain='physics_em',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.em.magnetism'],
        ),
        AgentSpec(
            agent_id='circuits_specialist',
            agent_class=LazyAgentClass(_get_circuits_specialist),
            domain='physics_em',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.em.circuits'],
        ),
    ],
    'physics_thermo': [
        AgentSpec(
            agent_id='thermo_supervisor',
            agent_class=LazyAgentClass(_get_thermo_supervisor),
            domain='physics_thermo',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.thermodynamics'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='heat_specialist',
            agent_class=LazyAgentClass(_get_heat_specialist),
            domain='physics_thermo',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.thermo.heat'],
        ),
        AgentSpec(
            agent_id='gas_laws_specialist',
            agent_class=LazyAgentClass(_get_gas_laws_specialist),
            domain='physics_thermo',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.thermo.gas'],
        ),
    ],
    'physics_quantum': [
        AgentSpec(
            agent_id='quantum_supervisor',
            agent_class=LazyAgentClass(_get_quantum_supervisor),
            domain='physics_quantum',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.quantum'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='wavefunction_specialist',
            agent_class=LazyAgentClass(_get_wavefunction_specialist),
            domain='physics_quantum',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.quantum.wavefunction'],
        ),
        AgentSpec(
            agent_id='operators_specialist',
            agent_class=LazyAgentClass(_get_operators_specialist),
            domain='physics_quantum',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.quantum.operators'],
        ),
        AgentSpec(
            agent_id='systems_specialist',
            agent_class=LazyAgentClass(_get_systems_specialist),
            domain='physics_quantum',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['physics.quantum.systems'],
        ),
    ],
    'logic': [
        AgentSpec(
            agent_id='logic_supervisor',
            agent_class=LazyAgentClass(_get_logic_supervisor),
            domain='logic',
            tier=2,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.logic'],
            standby_timeout_seconds=600,
        ),
        AgentSpec(
            agent_id='propositional_specialist',
            agent_class=LazyAgentClass(_get_propositional_specialist),
            domain='logic',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.logic.propositional'],
        ),
        AgentSpec(
            agent_id='predicate_specialist',
            agent_class=LazyAgentClass(_get_predicate_specialist),
            domain='logic',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.logic.predicate'],
        ),
        AgentSpec(
            agent_id='proof_specialist',
            agent_class=LazyAgentClass(_get_proof_specialist),
            domain='logic',
            tier=3,
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['math.logic.proof'],
        ),
    ],
}


def register_all_agents(pool: AgentPool, domains: List[str] = None) -> int:
    """
    Register all agent specs with the AgentPool.

    Args:
        pool: The AgentPool instance
        domains: Optional list of domains to register. If None, registers all.

    Returns:
        Number of agents registered
    """
    count = 0
    target_domains = domains or list(AGENT_SPECS.keys())

    for domain in target_domains:
        if domain not in AGENT_SPECS:
            logger.warning(f"Unknown domain: {domain}")
            continue

        for spec in AGENT_SPECS[domain]:
            if pool.register_spec(spec):
                count += 1
                logger.debug(f"Registered: {spec.agent_id}")
            else:
                logger.warning(f"Failed to register: {spec.agent_id}")

    logger.info(f"Registered {count} agents across {len(target_domains)} domains")
    return count


def register_domain(pool: AgentPool, domain: str) -> int:
    """
    Register agents for a specific domain.

    Args:
        pool: The AgentPool instance
        domain: Domain to register (e.g., 'algebra', 'calculus')

    Returns:
        Number of agents registered
    """
    return register_all_agents(pool, domains=[domain])


def get_domain_agents(domain: str) -> List[str]:
    """
    Get list of agent IDs for a domain.

    Args:
        domain: Domain name

    Returns:
        List of agent IDs
    """
    if domain not in AGENT_SPECS:
        return []
    return [spec.agent_id for spec in AGENT_SPECS[domain]]


def get_all_domains() -> List[str]:
    """Get list of all registered domains."""
    return list(AGENT_SPECS.keys())


if __name__ == "__main__":
    """Test agent registry"""
    print("=" * 60)
    print("AGENT REGISTRY TEST")
    print("=" * 60)
    print()

    print("Available domains:")
    for domain in get_all_domains():
        agents = get_domain_agents(domain)
        print(f"  {domain}: {len(agents)} agents")
        for aid in agents:
            print(f"    - {aid}")

    print()
    print("Testing registration with AgentPool...")

    from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem

    ams = AgentManagementSystem()
    pool = AgentPool(ams)

    count = register_all_agents(pool)
    print(f"Registered {count} agents")

    print()
    print("Pool statistics:")
    stats = pool.get_statistics()
    print(f"  Total registered: {stats['total_registered']}")
    print(f"  State distribution: {stats['state_distribution']}")
