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
PHASE 1 SYSTEM INTEGRATION
===========================

Integrated Phase 1 system - The Cognitive Chassis

This module brings together all Phase 1 components to create the first
dynamic "heartbeat" of the multi-agent mathematical reasoning system.

COMPONENTS:
----------
1. Problem Analysis Team (Gatekeepers)
2. Main Orchestrator (Central Nervous System)
3. Pilot Solver (Symbolic Wrapper)
4. Verification Core (Immune System)

REFERENCE:
---------
- Phase 1 Coding Strategy: "The Cognitive Chassis"
- Phase_1_Build_Order_Breakdown.md: Complete system integration
"""

import sys
import os
from typing import Optional, Dict, Any

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from symbo_agentic_reasoners_phase0.phase0_system import Phase0System
from agents.problem_analysis import ProblemAnalysisTeam
from orchestrator.main_orchestrator import MainOrchestrator
from solvers.pilot_solver import PilotSolverAgent
from verification.verification_core import VerificationCore


class Phase1System:
    """
    Integrated Phase 1 System - The Cognitive Chassis

    Brings together all Phase 1 cognitive agents and Phase 0 infrastructure
    to create the first functional reasoning loop.

    ARCHITECTURE:
    ------------
    Phase 0 Infrastructure:
      - AMS (Agent Management System)
      - DF (Directory Facilitator)
      - ACC (Agent Communication Channel)
      - Blackboard (Active Memory)
      - Vector DB (Long-term Memory)

    Phase 1 Cognitive Chassis:
      - Problem Analysis Team (input sanitization)
      - Main Orchestrator (task management)
      - Pilot Solver (SymPy execution)
      - Verification Core (result verification)

    WORKFLOW:
    --------
    1. User provides natural language problem
    2. Problem Analysis Team parses and classifies
    3. Main Orchestrator decomposes and routes
    4. Pilot Solver executes symbolic computation
    5. Verification Core validates result
    6. Orchestrator returns verified result to user

    USAGE:
    -----
    system = Phase1System()
    system.start()

    result = system.solve("Calculate the derivative of x**2 + 1")
    print(f"Result: {result}")

    system.shutdown()

    REFERENCE:
    ---------
    Phase_1_Build_Order_Breakdown.md: Section 4 "Phase 1 Deliverables"
    """

    def __init__(self, vector_db_path: str = "./symbo_agentic_reasoners_vector_store"):
        """
        Initialize Phase 1 System

        Args:
            vector_db_path: Path for vector database persistence
        """
        print("=" * 80)
        print("PHASE 1 SYSTEM INITIALIZATION")
        print("=" * 80)
        print()

        # Initialize Phase 0 infrastructure
        print("[Phase 1] Initializing Phase 0 infrastructure...")
        self.phase0 = Phase0System(vector_db_path=vector_db_path)
        self.phase0.start()
        print()

        # Initialize Phase 1 components
        print("[Phase 1] Initializing Cognitive Chassis...")
        print()

        # 1. Problem Analysis Team (Gatekeepers)
        print("  [1/4] Problem Analysis Team (Gatekeepers)...")
        self.problem_analysis = ProblemAnalysisTeam()
        print()

        # 2. Main Orchestrator (Central Nervous System)
        print("  [2/4] Main Orchestrator (Central Nervous System)...")
        self.orchestrator = MainOrchestrator(
            df=self.phase0.df,
            blackboard=self.phase0.blackboard
        )
        print()

        # 3. Pilot Solver (Symbolic Wrapper)
        print("  [3/4] Pilot Solver (Tracer Bullet)...")
        self.pilot_solver = PilotSolverAgent(
            df=self.phase0.df,
            blackboard=self.phase0.blackboard
        )
        print()

        # 4. Verification Core (Immune System)
        print("  [4/4] Verification Core (Immune System)...")
        self.verification_core = VerificationCore(
            blackboard=self.phase0.blackboard
        )
        print()

        print("[OK] Phase 1 Cognitive Chassis initialized")
        print()

    def start(self):
        """
        Start Phase 1 System

        All components are already active after __init__.
        This method provides a clean start interface.
        """
        print("=" * 80)
        print("PHASE 1 SYSTEM STARTED")
        print("=" * 80)
        print()
        print("STATUS: Architecturally Complete, Mathematically Limited")
        print("  - Neural creativity shackled to symbolic rigor")
        print("  - Orchestrator-Prover-Verifier loop active")
        print("  - Hallucination prevention online")
        print()
        print("CAPABILITIES:")
        print("  - Calculus: derivatives, integrals (via SymPy)")
        print("  - Algebra: simplification, factorization, expansion")
        print()
        print("READY FOR PHASE 1 VERIFICATION TEST")
        print()

    def solve(self, problem: str) -> str:
        """
        Solve a mathematical problem

        This is the main entry point for the system. It orchestrates
        the complete problem-solving pipeline.

        Args:
            problem: Natural language mathematical problem

        Returns:
            Verified solution as string

        WORKFLOW:
        --------
        1. Problem Analysis Team sanitizes input
        2. Main Orchestrator routes to solver
        3. Pilot Solver computes result
        4. Verification Core validates
        5. Orchestrator returns verified result
        """
        print()
        print("=" * 80)
        print(f"SOLVING: {problem}")
        print("=" * 80)
        print()

        try:
            # Step 1: Parse and classify
            structured = self.problem_analysis.process(problem)
            print()

            # Step 2: Orchestrate solution
            result_omdoc = self.orchestrator.process(structured)
            print()

            # Extract result string from metadata
            # The result_omdoc is the verified OMDoc object
            # We need to convert it to a human-readable string

            print("=" * 80)
            print("SOLUTION COMPLETE")
            print("=" * 80)
            print()

            return str(result_omdoc)

        except Exception as e:
            print()
            print("=" * 80)
            print("SOLUTION FAILED")
            print("=" * 80)
            print(f"Error: {e}")
            print()
            raise

    def shutdown(self):
        """
        Shutdown Phase 1 System

        Stops all agents and infrastructure.
        """
        print()
        print("=" * 80)
        print("PHASE 1 SYSTEM SHUTDOWN")
        print("=" * 80)
        print()

        # Shutdown Phase 0 infrastructure (which deactivates all agents)
        self.phase0.shutdown()

        print()
        print("[OK] Phase 1 System shutdown complete")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform system health check

        Verifies all Phase 1 components are operational.

        Returns:
            Dictionary with health status
        """
        print()
        print("=" * 80)
        print("PHASE 1 HEALTH CHECK")
        print("=" * 80)
        print()

        health = {}

        # Check Phase 0 infrastructure
        print("[1/5] Phase 0 Infrastructure...")
        phase0_health = self.phase0.health_check()
        health['phase0'] = phase0_health['overall']
        print()

        # Check Problem Analysis Team
        print("[2/5] Problem Analysis Team...")
        try:
            test_structured = self.problem_analysis.process("test x**2")
            analysis_healthy = test_structured is not None
        except:
            analysis_healthy = False
        health['problem_analysis'] = analysis_healthy
        print(f"  Status: {'PASS' if analysis_healthy else 'FAIL'}")
        print()

        # Check Orchestrator
        print("[3/5] Main Orchestrator...")
        orchestrator_healthy = (
            self.orchestrator.NON_INTERVENTION and
            self.orchestrator.df is not None and
            self.orchestrator.blackboard is not None
        )
        health['orchestrator'] = orchestrator_healthy
        print(f"  NON-INTERVENTION: {self.orchestrator.NON_INTERVENTION}")
        print(f"  Status: {'PASS' if orchestrator_healthy else 'FAIL'}")
        print()

        # Check Pilot Solver
        print("[4/5] Pilot Solver...")
        services = self.phase0.df.search(service_type='math.calculus')
        solver_healthy = len(services) > 0
        health['pilot_solver'] = solver_healthy
        print(f"  Registered services: {len(services)}")
        print(f"  Status: {'PASS' if solver_healthy else 'FAIL'}")
        print()

        # Check Verification Core
        print("[5/5] Verification Core...")
        verification_healthy = (
            self.verification_core.verifier is not None and
            self.verification_core.verifier.logic_checker is not None
        )
        health['verification_core'] = verification_healthy
        print(f"  Status: {'PASS' if verification_healthy else 'FAIL'}")
        print()

        # Overall health
        all_healthy = all(health.values())
        health['overall'] = all_healthy

        print("=" * 80)
        print(f"OVERALL SYSTEM HEALTH: {'PASS' if all_healthy else 'FAIL'}")
        print("=" * 80)
        print()

        if all_healthy:
            print("[OK] Phase 1 is COMPLETE and HEALTHY")
            print("  The Cognitive Chassis is operational")
            print("  Ready for end-to-end verification test")
        else:
            print("[FAIL] Phase 1 has health issues")

        print()

        return health

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'phase0': self.phase0.get_statistics(),
            'orchestrator': self.orchestrator.get_statistics(),
            'pilot_solver': self.pilot_solver.get_statistics(),
            'verification_core': self.verification_core.verifier.get_statistics()
        }

    def print_statistics(self):
        """Print formatted statistics"""
        print()
        print("=" * 80)
        print("PHASE 1 SYSTEM STATISTICS")
        print("=" * 80)
        print()

        stats = self.get_statistics()

        print("ORCHESTRATOR:")
        print(f"  Tasks routed: {stats['orchestrator']['tasks_routed']}")
        print(f"  Tasks completed: {stats['orchestrator']['tasks_completed']}")
        print(f"  Tasks failed: {stats['orchestrator']['tasks_failed']}")
        print()

        print("PILOT SOLVER:")
        print(f"  Tasks executed: {stats['pilot_solver']['tasks_executed']}")
        print(f"  Success rate: {stats['pilot_solver']['success_rate']:.1f}%")
        print()

        print("VERIFICATION CORE:")
        print(f"  Verifications attempted: {stats['verification_core']['verifications_attempted']}")
        print(f"  Success rate: {stats['verification_core']['success_rate']:.1f}%")
        print()

    def __repr__(self) -> str:
        """Human-readable representation"""
        return "Phase1System(Cognitive Chassis: ONLINE)"


if __name__ == "__main__":
    """Demonstration of integrated Phase 1 system"""
    print()
    print("=" * 80)
    print("PHASE 1 SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize and start system
    system = Phase1System()
    system.start()

    # Perform health check
    health = system.health_check()

    if health['overall']:
        print()
        print("System healthy - ready for Phase 1 verification test!")
        print()
        print("To run the official Phase 1 verification test, execute:")
        print("  python tests/test_phase1.py")

    # Display statistics
    system.print_statistics()

    # Shutdown
    system.shutdown()

    print()
    print("=" * 80)
    print("PHASE 1 DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
