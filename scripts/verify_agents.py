import sys
import os
import traceback

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from symbo_agentic_reasoners.infrastructure.ams import AgentManagementSystem
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.infrastructure.acc import AgentCommunicationChannel

from symbo_agentic_reasoners.agents.base.problem_analysis import SyntaxParserAgent, StructureRecognizerAgent
from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
# NOTE: solvers/ directory has been archived - PilotSolverAgent no longer available
from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent, SimplifiedVerifierAgent

from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import PolynomialSpecialist
from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import ArithmeticSpecialist
from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist
from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist
from symbo_agentic_reasoners.agents.specialists.calculus.series_specialist import SeriesSpecialist
from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import ODESolver
from symbo_agentic_reasoners.agents.specialists.linear_algebra.matrix_ops_specialist import MatrixOperationsSpecialist
from symbo_agentic_reasoners.agents.specialists.linear_algebra.decomposition_specialist import DecompositionSpecialist
from symbo_agentic_reasoners.agents.specialists.linear_algebra.vector_space_analyst import VectorSpaceAnalyst
from symbo_agentic_reasoners.agents.specialists.statistics.distribution_specialist import DistributionSpecialist
from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_engine import BayesianInferenceEngine
from symbo_agentic_reasoners.agents.specialists.statistics.frequentist_agent import FrequentistAgent
from symbo_agentic_reasoners.agents.specialists.numerical.numerical_utility import NumericalComputationUtility

def verify_agent(agent_class, agent_id, *args, **kwargs):
    try:
        print(f"Verifying {agent_class.__name__}...", end=" ")
        agent = agent_class(agent_id, *args, **kwargs)
        print("OK")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        # traceback.print_exc()
        return False

def verify_phase0():
    print("\n--- Phase 0 Verification ---")
    try:
        print("Verifying AgentManagementSystem...", end=" ")
        ams = AgentManagementSystem()
        print("OK")
        
        # DF and ACC might need AMS or other args? 
        # Checking their __init__ signatures would be good, but assuming standard BDI or specific init.
        # DF init: (agent_id)
        verify_agent(DirectoryFacilitator, "df_001")
        verify_agent(AgentCommunicationChannel, "acc_001")
    except Exception as e:
        print(f"Phase 0 FAILED: {e}")

def verify_phase1():
    print("\n--- Phase 1 Verification ---")
    verify_agent(SyntaxParserAgent, "pa1_001")
    verify_agent(StructureRecognizerAgent, "pa2_001")
    verify_agent(MainOrchestrator, "cns1_001")
    # verify_agent(PilotSolverAgent, "ps1_001")  # ARCHIVED: solvers/ directory removed
    verify_agent(LogicCheckerAgent, "vc1_001")
    verify_agent(SimplifiedVerifierAgent, "vc2_001")

def verify_phase2():
    print("\n--- Phase 2 Verification ---")
    verify_agent(PolynomialSpecialist, "alg1_001")
    verify_agent(ArithmeticSpecialist, "alg2_001")
    verify_agent(DifferentiationSpecialist, "cal1_001")
    verify_agent(IntegrationSpecialist, "cal2_001")
    verify_agent(SeriesSpecialist, "cal4_001")
    verify_agent(ODESolver, "cal5_001")
    verify_agent(MatrixOperationsSpecialist, "la1_001")
    verify_agent(DecompositionSpecialist, "la2_001")
    verify_agent(VectorSpaceAnalyst, "la3_001")
    verify_agent(DistributionSpecialist, "prob1_001")
    verify_agent(BayesianInferenceEngine, "prob2_001")
    verify_agent(FrequentistAgent, "prob3_001")
    verify_agent(NumericalComputationUtility, "num1_001")

if __name__ == "__main__":
    verify_phase0()
    verify_phase1()
    verify_phase2()
