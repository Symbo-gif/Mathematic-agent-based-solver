# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
AGENT FACTORY
=============

Factory for creating and registering all agents in the system.
Provides a single entry point for spinning up the complete agent workforce.

Usage:
    from symbo_agentic_reasoners.infrastructure.agent_factory import AgentFactory

    factory = AgentFactory(df=phase0.df, blackboard=phase0.blackboard)
    agents = factory.create_all()
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger('symbo_agentic_reasoners.agent_factory')


class AgentFactory:
    """
    Factory for creating the complete agent workforce.

    Creates and registers:
    - Tier 2: Domain Supervisors (route to specialists)
    - Tier 3: Domain Specialists (perform actual computation)
    """

    def __init__(self, df, blackboard):
        """
        Initialize factory with infrastructure components.

        Args:
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        self.df = df
        self.blackboard = blackboard
        self.agents: Dict[str, Any] = {}

    def create_all(self) -> Dict[str, Any]:
        """
        Create all agents in the system.

        Returns:
            Dictionary of agent_id -> agent instance
        """
        self.create_supervisors()
        self.create_specialists()

        logger.info(f"AgentFactory: Created {len(self.agents)} agents")
        return self.agents

    def create_supervisors(self) -> Dict[str, Any]:
        """Create all Tier 2 domain supervisors."""
        supervisors = {}

        # Algebra Supervisor
        try:
            from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
            agent = AlgebraSupervisor(df=self.df, blackboard=self.blackboard)
            supervisors[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create AlgebraSupervisor: {e}")

        # Calculus Supervisor
        try:
            from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
            agent = CalculusSupervisor(df=self.df, blackboard=self.blackboard)
            supervisors[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create CalculusSupervisor: {e}")

        # Geometry Supervisor
        try:
            from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import GeometrySupervisor
            agent = GeometrySupervisor(df=self.df, blackboard=self.blackboard)
            supervisors[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create GeometrySupervisor: {e}")

        # Linear Algebra Supervisor
        try:
            from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import LinearAlgebraSupervisor
            agent = LinearAlgebraSupervisor(df=self.df, blackboard=self.blackboard)
            supervisors[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create LinearAlgebraSupervisor: {e}")

        # Statistics Supervisor
        try:
            from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import StatisticsSupervisor
            agent = StatisticsSupervisor(df=self.df, blackboard=self.blackboard)
            supervisors[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create StatisticsSupervisor: {e}")

        # Discrete Math Supervisor
        try:
            from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import DiscreteMathSupervisor
            agent = DiscreteMathSupervisor(df=self.df, blackboard=self.blackboard)
            supervisors[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create DiscreteMathSupervisor: {e}")

        # Elementary Number Theory Supervisor
        try:
            from symbo_agentic_reasoners.agents.supervisors.elementary_number_theory_supervisor import ElementaryNumberTheorySupervisor
            agent = ElementaryNumberTheorySupervisor(df=self.df, blackboard=self.blackboard)
            supervisors[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create ElementaryNumberTheorySupervisor: {e}")

        self.agents.update(supervisors)
        logger.info(f"Created {len(supervisors)} supervisors")
        return supervisors

    def create_specialists(self) -> Dict[str, Any]:
        """Create all Tier 3 domain specialists."""
        specialists = {}

        # === ALGEBRA SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import PolynomialSpecialist
            agent = PolynomialSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create PolynomialSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import ArithmeticSpecialist
            agent = ArithmeticSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create ArithmeticSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import NumberTheorySpecialist
            agent = NumberTheorySpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create NumberTheorySpecialist: {e}")

        # === CALCULUS SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist
            agent = DifferentiationSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create DifferentiationSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist
            agent = IntegrationSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create IntegrationSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.calculus.limit_specialist import LimitSpecialist
            agent = LimitSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create LimitSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.calculus.series_specialist import SeriesSpecialist
            agent = SeriesSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create SeriesSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.calculus.ode_specialist import ODESolutionSpecialist
            agent = ODESolutionSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create ODESolutionSpecialist: {e}")

        # === GEOMETRY SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.geometry.euclidean_specialist import EuclideanSpecialist
            agent = EuclideanSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create EuclideanSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.geometry.analytic_specialist import AnalyticSpecialist
            agent = AnalyticSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create AnalyticSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.geometry.trigonometry_specialist import TrigonometrySpecialist
            agent = TrigonometrySpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create TrigonometrySpecialist: {e}")

        # === LINEAR ALGEBRA SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.linear_algebra.matrix_ops_specialist import MatrixOpsSpecialist
            agent = MatrixOpsSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create MatrixOpsSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.linear_algebra.decomposition_specialist import DecompositionSpecialist
            agent = DecompositionSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create DecompositionSpecialist: {e}")

        # === STATISTICS SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.statistics.distribution_specialist import DistributionSpecialist
            agent = DistributionSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create DistributionSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_engine import BayesianEngine
            agent = BayesianEngine(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create BayesianEngine: {e}")

        # === DISCRETE MATH SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.combinatorics_agent import CombinatoricsAgent
            agent = CombinatoricsAgent(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create CombinatoricsAgent: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.graph_theory_agent import GraphTheoryAgent
            agent = GraphTheoryAgent(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create GraphTheoryAgent: {e}")

        # === GENERATING FUNCTIONS SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import OrdinaryGFSpecialist
            agent = OrdinaryGFSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create OrdinaryGFSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import ExponentialGFSpecialist
            agent = ExponentialGFSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create ExponentialGFSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import RationalGFSpecialist
            agent = RationalGFSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create RationalGFSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import RecurrenceGFSpecialist
            agent = RecurrenceGFSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create RecurrenceGFSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import BivariateGFSpecialist
            agent = BivariateGFSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create BivariateGFSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import GFCompositionSpecialist
            agent = GFCompositionSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create GFCompositionSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import AsymptoticExtractionSpecialist
            agent = AsymptoticExtractionSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create AsymptoticExtractionSpecialist: {e}")

        # === ELEMENTARY NUMBER THEORY SPECIALISTS ===
        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import CongruenceSpecialist
            agent = CongruenceSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create CongruenceSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import ContinuedFractionsSpecialist
            agent = ContinuedFractionsSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create ContinuedFractionsSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import PellEquationSpecialist
            agent = PellEquationSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create PellEquationSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import TonelliShanksSpecialist
            agent = TonelliShanksSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create TonelliShanksSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import LiftingTheExponentSpecialist
            agent = LiftingTheExponentSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create LiftingTheExponentSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import DiophantineBasicSpecialist
            agent = DiophantineBasicSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create DiophantineBasicSpecialist: {e}")

        try:
            from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import QuadraticResidueSpecialist
            agent = QuadraticResidueSpecialist(df=self.df, blackboard=self.blackboard)
            specialists[agent.agent_id] = agent
        except Exception as e:
            logger.warning(f"Failed to create QuadraticResidueSpecialist: {e}")

        self.agents.update(specialists)
        logger.info(f"Created {len(specialists)} specialists")
        return specialists

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def list_agents(self) -> List[str]:
        """List all created agent IDs."""
        return list(self.agents.keys())


def create_full_system(df, blackboard):
    """
    Convenience function to create complete agent system.

    Args:
        df: Directory Facilitator
        blackboard: Blackboard instance

    Returns:
        AgentFactory with all agents created
    """
    factory = AgentFactory(df=df, blackboard=blackboard)
    factory.create_all()
    return factory
