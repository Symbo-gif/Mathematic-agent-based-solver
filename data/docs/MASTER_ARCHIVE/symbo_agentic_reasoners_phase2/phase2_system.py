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
PHASE 2 SYSTEM INTEGRATION
==========================

Integrated Phase 2 system - Vertical Domain Expansion

This module brings together all Phase 2 components to create the
"Mathematical Workforce" - a hierarchical collective of specialized agents.

ARCHITECTURE:
------------
Builds on Phase 0 (Infrastructure) and Phase 1 (Cognitive Chassis) by adding:

TIER 2 SUPERVISORS:
  - Algebra Supervisor
  - Calculus Supervisor
  - Linear Algebra Supervisor
  - Statistics Supervisor

TIER 3 SPECIALISTS:
  Foundation Layer (Algebra):
    - Arithmetic Specialist
    - Polynomial Specialist
    - Number Theory Specialist

  Analysis Layer (Calculus):
    - Differentiation Specialist
    - Integration Specialist (Dual-Engine)
    - ODE Solver
    - Series Specialist

  Vector Layer (Linear Algebra):
    - Matrix Operations Specialist
    - Decomposition Specialist
    - Vector Space Analyst

  Logic Layer (Discrete Math):
    - Combinatorics Agent
    - Graph Theory Agent

  Uncertainty Layer (Statistics):
    - Distribution Specialist
    - Bayesian Inference Engine
    - Frequentist Agent

  Numerical Fallback:
    - Numerical Computation Utility

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Complete specification
- Phase 2 Coding Strategy: Vertical Domain Expansion

PHASE 2 DEFINITION OF DONE:
---------------------------
"Fragile Genius" - Immense mathematical power, brittle architecture
"""

import sys
import os
from typing import Optional, Dict, Any

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from symbo_agentic_reasoners_phase0.phase0_system import Phase0System
from symbo_agentic_reasoners_phase1.phase1_system import Phase1System

# Import all Phase 2 Supervisors
from symbo_agentic_reasoners_phase2.supervisors.algebra_supervisor import AlgebraSupervisor
from symbo_agentic_reasoners_phase2.supervisors.calculus_supervisor import CalculusSupervisor
from symbo_agentic_reasoners_phase2.supervisors.linalg_supervisor import LinearAlgebraSupervisor
from symbo_agentic_reasoners_phase2.supervisors.stats_supervisor import StatisticsSupervisor

# Import Algebra Team
from symbo_agentic_reasoners_phase2.agents.algebra.arithmetic_specialist import ArithmeticSpecialist
from symbo_agentic_reasoners_phase2.agents.algebra.polynomial_specialist import PolynomialSpecialist
from symbo_agentic_reasoners_phase2.agents.algebra.number_theory_specialist import NumberTheorySpecialist

# Import Calculus Team
from symbo_agentic_reasoners_phase2.agents.calculus.differentiation_specialist import DifferentiationSpecialist
from symbo_agentic_reasoners_phase2.agents.calculus.integration_specialist import IntegrationSpecialist
from symbo_agentic_reasoners_phase2.agents.calculus.ode_solver import ODESolver
from symbo_agentic_reasoners_phase2.agents.calculus.series_specialist import SeriesSpecialist

# Import Linear Algebra Team
from symbo_agentic_reasoners_phase2.agents.linear_algebra.matrix_ops_specialist import MatrixOperationsSpecialist
from symbo_agentic_reasoners_phase2.agents.linear_algebra.decomposition_specialist import DecompositionSpecialist
from symbo_agentic_reasoners_phase2.agents.linear_algebra.vector_space_analyst import VectorSpaceAnalyst

# Import Discrete Math Team
from symbo_agentic_reasoners_phase2.agents.discrete_math.combinatorics_agent import CombinatoricsAgent
from symbo_agentic_reasoners_phase2.agents.discrete_math.graph_theory_agent import GraphTheoryAgent

# Import Statistics Team
from symbo_agentic_reasoners_phase2.agents.statistics.distribution_specialist import DistributionSpecialist
from symbo_agentic_reasoners_phase2.agents.statistics.bayesian_engine import BayesianInferenceEngine
from symbo_agentic_reasoners_phase2.agents.statistics.frequentist_agent import FrequentistAgent

# Import Numerical Fallback
from symbo_agentic_reasoners_phase2.agents.numerical.numerical_utility import NumericalComputationUtility


class Phase2System:
    """
    Integrated Phase 2 System - The Mathematical Workforce

    Expands the Phase 1 Cognitive Chassis into a fully operational
    mathematical workforce through domain decomposition.

    WORKFLOW:
    --------
    1. User provides problem
    2. Phase 1 Orchestrator routes to Phase 2 Supervisor
    3. Supervisor analyzes and routes to appropriate Specialist
    4. Specialist executes using algorithmic wrappers
    5. Result verified and returned

    USAGE:
    -----
    system = Phase2System()
    system.start()

    # System now has 18+ specialized mathematical agents
    # All registered with Directory Facilitator

    system.shutdown()

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Section 4 "Complete Agent Registry"
    """

    def __init__(self, vector_db_path: str = "./symbo_agentic_reasoners_vector_store"):
        """
        Initialize Phase 2 System

        Args:
            vector_db_path: Path for vector database persistence
        """
        print("=" * 80)
        print("PHASE 2 SYSTEM INITIALIZATION")
        print("=" * 80)
        print()

        # Initialize Phase 0 + Phase 1
        print("[Phase 2] Initializing Phase 0 + Phase 1 foundations...")
        self.phase1 = Phase1System(vector_db_path=vector_db_path)
        self.phase1.start()
        print()

        # Get Phase 0 infrastructure references
        self.phase0 = self.phase1.phase0
        self.df = self.phase0.df
        self.blackboard = self.phase0.blackboard

        # Initialize Phase 2 components
        print("[Phase 2] Initializing Mathematical Workforce...")
        print()

        # TIER 2 SUPERVISORS
        print("  [TIER 2 SUPERVISORS]")
        self.algebra_supervisor = AlgebraSupervisor(df=self.df, blackboard=self.blackboard)
        self.calculus_supervisor = CalculusSupervisor(df=self.df, blackboard=self.blackboard)
        self.linalg_supervisor = LinearAlgebraSupervisor(df=self.df, blackboard=self.blackboard)
        self.stats_supervisor = StatisticsSupervisor(df=self.df, blackboard=self.blackboard)
        print()

        # TIER 3 SPECIALISTS - Foundation Layer (Algebra)
        print("  [FOUNDATION LAYER - Algebra Team]")
        self.arithmetic_specialist = ArithmeticSpecialist(df=self.df, blackboard=self.blackboard, precision=50)
        self.polynomial_specialist = PolynomialSpecialist(df=self.df, blackboard=self.blackboard)
        self.numbertheory_specialist = NumberTheorySpecialist(df=self.df, blackboard=self.blackboard)
        print()

        # TIER 3 SPECIALISTS - Analysis Layer (Calculus)
        print("  [ANALYSIS LAYER - Calculus Team]")
        self.differentiation_specialist = DifferentiationSpecialist(df=self.df, blackboard=self.blackboard)
        self.integration_specialist = IntegrationSpecialist(df=self.df, blackboard=self.blackboard)
        self.ode_solver = ODESolver(df=self.df, blackboard=self.blackboard)
        self.series_specialist = SeriesSpecialist(df=self.df, blackboard=self.blackboard)
        print()

        # TIER 3 SPECIALISTS - Vector Layer (Linear Algebra)
        print("  [VECTOR LAYER - Linear Algebra Team]")
        self.matrix_ops = MatrixOperationsSpecialist(df=self.df, blackboard=self.blackboard)
        self.decomposition = DecompositionSpecialist(df=self.df, blackboard=self.blackboard)
        self.vectorspace = VectorSpaceAnalyst(df=self.df, blackboard=self.blackboard)
        print()

        # TIER 3 SPECIALISTS - Logic Layer (Discrete Math)
        print("  [LOGIC LAYER - Discrete Math Team]")
        self.combinatorics = CombinatoricsAgent(df=self.df, blackboard=self.blackboard)
        self.graphtheory = GraphTheoryAgent(df=self.df, blackboard=self.blackboard)
        print()

        # TIER 3 SPECIALISTS - Uncertainty Layer (Statistics)
        print("  [UNCERTAINTY LAYER - Statistics Team]")
        self.distribution = DistributionSpecialist(df=self.df, blackboard=self.blackboard)
        self.bayesian = BayesianInferenceEngine(df=self.df, blackboard=self.blackboard)
        self.frequentist = FrequentistAgent(df=self.df, blackboard=self.blackboard)
        print()

        # TIER 3 - Numerical Fallback
        print("  [NUMERICAL FALLBACK]")
        self.numerical_utility = NumericalComputationUtility(df=self.df, blackboard=self.blackboard)
        print()

        print("[OK] Phase 2 Mathematical Workforce initialized")
        print()

    def start(self):
        """
        Start Phase 2 System

        All agents are already registered with DF after __init__.
        This method provides verification.
        """
        print("=" * 80)
        print("PHASE 2 SYSTEM STARTED")
        print("=" * 80)
        print()
        print("STATUS: Fragile Genius")
        print("  - Immense mathematical power through algorithmic wrappers")
        print("  - Brittle architecture (precondition validation in Phase 3)")
        print()

        # Verify agent registration
        print("AGENT REGISTRY:")

        # Get all math services by searching for all known service types
        phase2_services = []
        service_types = [
            # Supervisors
            'math.algebra', 'math.calculus', 'math.linalg', 'math.stats',
            # Algebra Team
            'math.algebra.arithmetic', 'math.algebra.polynomial', 'math.algebra.numbertheory',
            # Calculus Team
            'math.calculus.diff', 'math.calculus.integration', 'math.calculus.ode', 'math.calculus.series',
            # Linear Algebra Team
            'math.linalg.ops', 'math.linalg.decomp', 'math.linalg.vectorspace',
            # Discrete Math Team
            'math.discrete.combinatorics', 'math.discrete.graphs',
            # Statistics Team
            'math.stats.distributions', 'math.stats.bayesian', 'math.stats.frequentist',
            # Numerical Fallback
            'math.numerical'
        ]
        for service_type in service_types:
            services = self.df.search(service_type=service_type)
            phase2_services.extend(services)

        print(f"  Total Phase 2 agents: {len(phase2_services)}")

        # Group by domain
        domains = {}
        for service in phase2_services:
            domain = service.service_type.split('.')[1] if '.' in service.service_type else 'other'
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(service)

        for domain, agents in sorted(domains.items()):
            print(f"\n  {domain.upper()} ({len(agents)} agents):")
            for agent in agents:
                tier = agent.properties.get('tier', '?') if hasattr(agent, 'properties') else '?'
                agent_type = agent.properties.get('type', 'specialist') if hasattr(agent, 'properties') else 'specialist'
                print(f"    [Tier {tier}] {agent.service_type}: {agent.agent_id} ({agent_type})")

        print()
        print("CAPABILITIES:")
        print("  - Algebra: Arbitrary-precision arithmetic, polynomials, number theory")
        print("  - Calculus: Differentiation, integration (dual-engine), ODEs, series")
        print("  - Linear Algebra: Matrix ops, decompositions (SVD/QR/LU), eigenvalues")
        print("  - Discrete Math: Combinatorics, graph algorithms")
        print("  - Statistics: Bayesian & Frequentist methods, distributions")
        print("  - Numerical: High-performance fallback for intractable problems")
        print()
        print("READY FOR PHASE 2 VERIFICATION TEST")
        print()

    def solve(self, problem: str) -> str:
        """
        Solve a mathematical problem using the Phase 2 workforce

        Delegates to Phase 1's solve method, which routes through the
        orchestrator to the appropriate Phase 2 specialist agents.

        Args:
            problem: Natural language mathematical problem

        Returns:
            Verified solution as string

        WORKFLOW:
        --------
        1. Problem Analysis Team (Phase 1) parses input
        2. Orchestrator routes to appropriate Phase 2 supervisor
        3. Supervisor delegates to specialist agent
        4. Specialist computes result
        5. Verification Core validates
        6. Returns verified result
        """
        return self.phase1.solve(problem)

    def shutdown(self):
        """
        Shutdown Phase 2 System

        Stops all Phase 2 agents and Phase 1 + Phase 0 infrastructure.
        """
        print()
        print("=" * 80)
        print("PHASE 2 SYSTEM SHUTDOWN")
        print("=" * 80)
        print()

        # Shutdown Phase 1 (which will shutdown Phase 0)
        self.phase1.shutdown()

        print()
        print("[OK] Phase 2 System shutdown complete")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform system health check

        Verifies all Phase 2 components are operational.

        Returns:
            Dictionary with health status
        """
        print()
        print("=" * 80)
        print("PHASE 2 HEALTH CHECK")
        print("=" * 80)
        print()

        health = {}

        # Check Phase 1
        print("[1/6] Phase 1 Infrastructure...")
        phase1_health = self.phase1.health_check()
        health['phase1'] = phase1_health['overall']
        print()

        # Check Tier 2 Supervisors
        print("[2/6] Tier 2 Supervisors...")
        supervisor_count = sum([
            len(self.df.search(service_type='math.algebra')),
            len(self.df.search(service_type='math.calculus')),
            len(self.df.search(service_type='math.linalg')),
            len(self.df.search(service_type='math.stats'))
        ])
        # Subtract 1 from calculus to account for pilot_solver
        supervisor_count -= 1
        supervisors_healthy = supervisor_count >= 4  # 4 supervisors expected
        health['supervisors'] = supervisors_healthy
        print(f"  Registered: {supervisor_count}/4 supervisors")
        print(f"  Status: {'PASS' if supervisors_healthy else 'FAIL'}")
        print()

        # Check Foundation Layer
        print("[3/6] Foundation Layer (Algebra)...")
        algebra_count = sum([
            len(self.df.search(service_type='math.algebra.arithmetic')),
            len(self.df.search(service_type='math.algebra.polynomial')),
            len(self.df.search(service_type='math.algebra.numbertheory'))
        ])
        algebra_healthy = algebra_count >= 3  # 3 specialists expected
        health['algebra'] = algebra_healthy
        print(f"  Registered: {algebra_count}/3 specialists")
        print(f"  Status: {'PASS' if algebra_healthy else 'FAIL'}")
        print()

        # Check Analysis Layer
        print("[4/6] Analysis Layer (Calculus)...")
        calculus_count = sum([
            len(self.df.search(service_type='math.calculus.diff')),
            len(self.df.search(service_type='math.calculus.integration')),
            len(self.df.search(service_type='math.calculus.ode')),
            len(self.df.search(service_type='math.calculus.series'))
        ])
        calculus_healthy = calculus_count >= 4  # 4 specialists expected
        health['calculus'] = calculus_healthy
        print(f"  Registered: {calculus_count}/4 specialists")
        print(f"  Status: {'PASS' if calculus_healthy else 'FAIL'}")
        print()

        # Check Vector Layer
        print("[5/6] Vector Layer (Linear Algebra)...")
        linalg_count = sum([
            len(self.df.search(service_type='math.linalg.ops')),
            len(self.df.search(service_type='math.linalg.decomp')),
            len(self.df.search(service_type='math.linalg.vectorspace'))
        ])
        linalg_healthy = linalg_count >= 3  # 3 specialists expected
        health['linalg'] = linalg_healthy
        print(f"  Registered: {linalg_count}/3 specialists")
        print(f"  Status: {'PASS' if linalg_healthy else 'FAIL'}")
        print()

        # Check Numerical Fallback
        print("[6/6] Numerical Fallback...")
        numerical_services = self.df.search(service_type='math.numerical')
        numerical_healthy = len(numerical_services) >= 1
        health['numerical'] = numerical_healthy
        print(f"  Registered: {len(numerical_services)}/1 utility")
        print(f"  Status: {'PASS' if numerical_healthy else 'FAIL'}")
        print()

        # Overall health
        all_healthy = all(health.values())
        health['overall'] = all_healthy

        print("=" * 80)
        print(f"OVERALL SYSTEM HEALTH: {'PASS' if all_healthy else 'FAIL'}")
        print("=" * 80)
        print()

        if all_healthy:
            print("[OK] Phase 2 is COMPLETE and HEALTHY")
            print("  The system has achieved \"Fragile Genius\" status")
            print("  Ready for complex mathematical problem solving")
        else:
            print("[FAIL] Phase 2 has health issues")

        print()

        return health

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'phase1': self.phase1.get_statistics(),
            'supervisors': {
                'algebra': self.algebra_supervisor.get_statistics(),
                'calculus': self.calculus_supervisor.get_statistics(),
                'linalg': self.linalg_supervisor.get_statistics(),
                'stats': self.stats_supervisor.get_statistics()
            },
            'specialists': {
                'arithmetic': self.arithmetic_specialist.get_statistics(),
                'polynomial': self.polynomial_specialist.get_statistics(),
                'numbertheory': self.numbertheory_specialist.get_statistics(),
                'differentiation': self.differentiation_specialist.get_statistics(),
                'integration': self.integration_specialist.get_statistics()
            }
        }

    def __repr__(self) -> str:
        """Human-readable representation"""
        return "Phase2System(Mathematical Workforce: ONLINE, Status: Fragile Genius)"


if __name__ == "__main__":
    """Demonstration of integrated Phase 2 system"""
    print()
    print("=" * 80)
    print("PHASE 2 SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize and start system
    system = Phase2System()
    system.start()

    # Perform health check
    health = system.health_check()

    if health['overall']:
        print()
        print("System healthy - Phase 2 complete!")
        print()
        print("To run Phase 2 verification test, execute:")
        print("  python tests/test_phase2.py")

    # Shutdown
    system.shutdown()

    print()
    print("=" * 80)
    print("PHASE 2 DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
