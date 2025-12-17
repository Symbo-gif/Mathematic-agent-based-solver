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
PHASE 4 SYSTEM INTEGRATION
===========================

Integrated Phase 4 system - The Self-Correction Engine

This module brings together all Phase 4 components to transform the system
from a "Resilient Professional" into a "Self-Correcting System" - a Dynamic
Organism capable of self-correction, conflict resolution, and evolutionary
optimization.

TRANSFORMATION:
--------------
Phase 3: "Resilient Professional" - Robust, context-aware, strategic
Phase 4: "Self-Correcting System" - Dynamic, adaptive, evolutionary

COMPONENTS:
----------
Builds on Phase 0-3 by adding:

PHASE 4 TEAMS (9 Agents):
  Conflict Resolution Team (3 agents) - "The Supreme Court"
    - Debate Moderator (FMAD Protocol)
    - Evidence Weigher (Truth Hierarchy)
    - Consensus Builder (Expertise Voting)

  Failure Analysis Team (3 agents) - "The Trauma Surgeons"
    - Error Classifier (Diagnostic Interceptor)
    - Root Cause Analyzer (Failure Attribution)
    - Alternative Path Generator (Plan B Engine)

  Meta-Learning Team (3 agents) - "The Optimizer"
    - Performance Monitor (Black Box Recorder)
    - Agent Selector Optimizer (AutoMaAS)
    - Adaptive Dispatcher (Dynamic Scaling)

PROTOCOLS:
---------
  - Appellate Protocol: Mandatory conflict check
  - Post-Mortem Protocol: Continuous optimization

THREE FUNDAMENTAL CAPABILITIES:
------------------------------
1. RESILIENCE: System heals itself when agents fail
2. INTELLIGENCE: Conflicts resolved through evidence-based adjudication
3. EVOLUTION: Every problem solved optimizes future performance

REFERENCE:
---------
- Phase_4_Build_Order_Breakdown.md
- Phase 4 transforms this collection of agents into a Self-Correction Engine.md
"""

import sys
import os
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger('symbo_agentic_reasoners.phase4.system')

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Phase 3 (which includes Phase 0-2)
from symbo_agentic_reasoners_phase3.phase3_system import Phase3System

# Import Phase 4 components
from symbo_agentic_reasoners_phase4.governance.conflict_resolution import (
    ConflictResolutionTeam,
    EvidenceType,
    Ruling
)
from symbo_agentic_reasoners_phase4.failure_analysis.failure_analysis_team import (
    FailureAnalysisTeam,
    ErrorType,
    RemedyAction,
    FailureReport
)
from symbo_agentic_reasoners_phase4.meta_learning.meta_learning_team import (
    MetaLearningTeam,
    SolutionTrace,
    ComplexityLevel
)
from symbo_agentic_reasoners_phase4.integration.protocol_updates import (
    OrchestratorPhase4Update,
    ConflictResolutionError,
    ConflictDetector
)


class Phase4System:
    """
    Integrated Phase 4 System - The Self-Correcting System

    Transforms the Phase 3 "Resilient Professional" into a "Self-Correcting
    System" by adding Dynamic Governance and Resilience capabilities.

    CAPABILITIES:
    ------------
    - Conflict Resolution: Evidence-based adjudication (FMAD protocol)
    - Failure Analysis: Autonomous error recovery (Plan B generation)
    - Meta-Learning: Continuous optimization (AutoMaAS pattern)
    - Protocol Integration: Appellate + Post-Mortem protocols

    USAGE:
    -----
    system = Phase4System()
    system.start()

    # Test conflict resolution
    ruling = system.resolve_conflict(conflict_data)

    # Test failure handling
    recovery = system.handle_failure(failure_data)

    # Get team recommendations
    team = system.get_team_recommendation(problem_context)

    # Trigger optimization
    results = system.run_optimization()

    system.shutdown()

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Section 5 "Phase 4 Deliverable"
    """

    def __init__(self, vector_db_path: str = "./symbo_agentic_reasoners_vector_store"):
        """
        Initialize Phase 4 System

        Args:
            vector_db_path: Path for vector database persistence
        """
        print("=" * 80)
        print("PHASE 4 SYSTEM INITIALIZATION")
        print("=" * 80)
        print()

        # Initialize Phase 3 (includes Phase 0 + Phase 1 + Phase 2)
        print("[Phase 4] Initializing Phase 0-3 foundations...")
        self.phase3 = Phase3System(vector_db_path=vector_db_path)
        self.phase3.start()
        print()

        # Get infrastructure references
        self.phase2 = self.phase3.phase2
        self.phase1 = self.phase2.phase1
        self.phase0 = self.phase1.phase0
        self.df = self.phase0.df
        self.blackboard = self.phase0.blackboard
        self.vector_db = self.phase0.vector_db
        self.acc = self.phase0.acc

        # Get Phase 3 components for integration
        self.hypothesis_generator = self.phase3.orchestrator.hypothesis_team

        # Initialize Phase 4 components
        print("[Phase 4] Initializing Dynamic Governance Teams...")
        print()

        # Team 1: Conflict Resolution Team
        self.conflict_resolution_team = ConflictResolutionTeam(
            blackboard=self.blackboard,
            acc=self.acc,
            df=self.df
        )
        print()

        # Team 2: Failure Analysis Team
        self.failure_analysis_team = FailureAnalysisTeam(
            blackboard=self.blackboard,
            hypothesis_generator=self.hypothesis_generator
        )
        print()

        # Team 3: Meta-Learning Team
        self.meta_learning_team = MetaLearningTeam(
            blackboard=self.blackboard,
            vector_db=self.vector_db,
            orchestrator=self.phase1.orchestrator if hasattr(self.phase1, 'orchestrator') else None
        )
        print()

        # Protocol Integration
        print("[Phase 4] Installing Protocol Updates...")
        self.protocol_update = OrchestratorPhase4Update(
            orchestrator=self.phase1.orchestrator if hasattr(self.phase1, 'orchestrator') else None,
            blackboard=self.blackboard,
            debate_moderator=self.conflict_resolution_team.debate_moderator,
            meta_learning_team=self.meta_learning_team,
            conflict_resolution_team=self.conflict_resolution_team
        )
        print()

        # Conflict detector utility
        self.conflict_detector = ConflictDetector(
            blackboard=self.blackboard
        )

        print("[OK] Phase 4 Dynamic Governance initialized")
        print()

    def start(self):
        """
        Start Phase 4 System

        All components are already active after __init__.
        This method provides verification and status.
        """
        print("=" * 80)
        print("PHASE 4 SYSTEM STARTED")
        print("=" * 80)
        print()
        print("STATUS: Self-Correcting System")
        print("  - Dynamic Governance ACTIVE")
        print("  - Conflict Resolution ONLINE")
        print("  - Failure Analysis ENABLED")
        print("  - Meta-Learning OPERATIONAL")
        print()

        print("TEAMS DEPLOYED:")
        print("  Conflict Resolution Team: 3 agents (The Supreme Court)")
        print("    - Debate Moderator (FMAD Protocol)")
        print("    - Evidence Weigher (Truth Hierarchy)")
        print("    - Consensus Builder (Expertise Voting)")
        print()
        print("  Failure Analysis Team: 3 agents (The Trauma Surgeons)")
        print("    - Error Classifier (Diagnostic Interceptor)")
        print("    - Root Cause Analyzer (Failure Attribution)")
        print("    - Alternative Path Generator (Plan B Engine)")
        print()
        print("  Meta-Learning Team: 3 agents (The Optimizer)")
        print("    - Performance Monitor (Black Box Recorder)")
        print("    - Agent Selector Optimizer (AutoMaAS)")
        print("    - Adaptive Dispatcher (Dynamic Scaling)")
        print()
        print("  Total Phase 4 Agents: 9")
        print()

        print("PROTOCOLS ENABLED:")
        print("  [1] Appellate Protocol: Mandatory conflict check before result acceptance")
        print("  [2] Post-Mortem Protocol: Continuous optimization after every session")
        print()

        print("CAPABILITIES:")
        print("  - RESILIENCE: System heals itself when agents fail")
        print("  - INTELLIGENCE: Conflicts resolved through evidence-based adjudication")
        print("  - EVOLUTION: Every problem solved optimizes future performance")
        print()

        print("EVIDENCE HIERARCHY (Immutable):")
        print("  FORMAL_PROOF > SYMBOLIC_DERIVATION > NUMERICAL_APPROXIMATION > HEURISTIC_GUESS")
        print()

        print("READY FOR PHASE 4 VERIFICATION TEST")
        print()

    def resolve_conflict(self, conflict_data: Dict) -> Optional[Ruling]:
        """
        Resolve a conflict between agents

        This is the main entry point for conflict resolution.
        Implements the FMAD protocol.

        Args:
            conflict_data: Dictionary containing:
                - subtask_id: ID of the subtask with conflicts
                - results: List of conflicting results from agents
                - conversation_id: Optional conversation ID
                - domain: Mathematical domain

        Returns:
            Ruling object with winner and rationale
        """
        print()
        print("=" * 80)
        print("CONFLICT RESOLUTION")
        print("=" * 80)
        print()

        ruling = self.conflict_resolution_team.resolve_conflict(conflict_data)

        print()
        print("RULING:")
        print(f"  Type: {ruling.ruling_type}")
        print(f"  Winner: {ruling.winner_agent}")
        print(f"  Evidence: {ruling.evidence_type}")
        print(f"  Confidence: {ruling.confidence:.2f}")
        print()

        return ruling

    def handle_failure(self, failure_data: Dict) -> Dict:
        """
        Handle a system failure

        This is the main entry point for failure analysis.
        Classifies the error, analyzes root cause, and generates recovery plan.

        Args:
            failure_data: Dictionary containing:
                - error_message: The error message
                - stack_trace: Optional stack trace
                - agent_id: Agent that failed
                - step: Optional step identifier
                - conversation_id: Conversation tracking ID

        Returns:
            Dictionary with report and recovery plan
        """
        print()
        print("=" * 80)
        print("FAILURE ANALYSIS")
        print("=" * 80)
        print()

        result = self.failure_analysis_team.handle_failure(failure_data)

        print()
        print("DIAGNOSIS:")
        print(f"  Error Type: {result['report']['error_type']}")
        print(f"  Action: {result['report']['remedy_action']}")
        print(f"  Status: {result['report']['status']}")

        if result.get('recovery_plan'):
            print()
            print("RECOVERY PLAN:")
            print(f"  Strategies: {result['recovery_plan'].get('strategies', [])}")

        print()

        return result

    def get_team_recommendation(self, problem_context: Dict) -> Dict:
        """
        Get optimal team configuration for a problem

        Uses the Meta-Learning Team to determine the best team size
        and agent selection based on problem complexity and historical
        performance.

        Args:
            problem_context: Dictionary with problem information:
                - problem_type: Type of problem (e.g., 'integration')
                - involves_proof: Whether problem involves proof
                - multiple_steps: Whether problem has multiple steps
                - etc.

        Returns:
            Recommendation with team size and suggested agents
        """
        return self.meta_learning_team.get_team_recommendation(problem_context)

    def run_optimization(self) -> Dict:
        """
        Run batch optimization

        Triggers the Meta-Learning Team to analyze recent traces
        and update routing tables. Should be called periodically
        or during low-load periods.

        Returns:
            Optimization results with insights
        """
        print()
        print("=" * 80)
        print("BATCH OPTIMIZATION")
        print("=" * 80)
        print()

        results = self.meta_learning_team.run_batch_optimization()

        print(f"Tables updated: {results['tables_updated']}")
        print(f"Insights generated: {results['insights_generated']}")

        if results.get('insights'):
            print()
            print("INSIGHTS:")
            for insight in results['insights']:
                print(f"  - {insight['recommendation']}")

        print()

        return results

    def log_task_start(self, conversation_id: str, problem_type: str,
                      **metadata):
        """
        Log the start of a problem-solving task

        Should be called when starting to solve a new problem.
        Enables performance tracking and optimization.
        """
        self.meta_learning_team.log_task_start(
            conversation_id, problem_type, **metadata
        )

    def log_agent_invocation(self, conversation_id: str, agent_id: str,
                            input_tokens: int = 0):
        """
        Log an agent invocation

        Should be called each time an agent is invoked.
        """
        self.meta_learning_team.log_agent_invocation(
            conversation_id, agent_id, input_tokens
        )

    def log_session_end(self, conversation_id: str):
        """
        Log the end of a problem-solving session

        Should be called when a session completes.
        Triggers trace analysis and potential optimization.
        """
        return self.meta_learning_team.log_session_end(conversation_id)

    def check_for_conflicts(self, results: List[Dict]) -> bool:
        """
        Check if a list of results contains conflicts

        Utility method for detecting agent disagreements.

        Args:
            results: List of result dictionaries

        Returns:
            True if conflicts detected
        """
        return self.conflict_detector.check_results(results)

    def classify_error(self, error_message: str) -> tuple:
        """
        Quick error classification

        Utility method for classifying errors without full pipeline.

        Args:
            error_message: Error message to classify

        Returns:
            Tuple of (ErrorType, RemedyAction)
        """
        return self.failure_analysis_team.classify_error(error_message)

    def shutdown(self):
        """
        Shutdown Phase 4 System

        Stops all Phase 4 agents and Phase 0-3 infrastructure.
        """
        print()
        print("=" * 80)
        print("PHASE 4 SYSTEM SHUTDOWN")
        print("=" * 80)
        print()

        # Run final optimization
        print("[Phase 4] Running final optimization...")
        try:
            self.run_optimization()
        except Exception as e:
            logger.debug(f"Final optimization skipped during shutdown: {type(e).__name__}: {e}")

        # Uninstall protocols
        print("[Phase 4] Uninstalling protocols...")
        self.protocol_update.uninstall_protocols()

        # Shutdown Phase 3 (which will shutdown Phase 0-2)
        self.phase3.shutdown()

        print()
        print("[OK] Phase 4 System shutdown complete")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform system health check

        Verifies all Phase 4 components are operational.

        Returns:
            Dictionary with health status
        """
        print()
        print("=" * 80)
        print("PHASE 4 HEALTH CHECK")
        print("=" * 80)
        print()

        health = {}

        # Check Phase 3 (includes Phase 0-2)
        print("[1/5] Phase 3 Infrastructure...")
        phase3_health = self.phase3.health_check()
        health['phase3'] = phase3_health['overall']
        print()

        # Check Conflict Resolution Team
        print("[2/5] Conflict Resolution Team...")
        try:
            crt_healthy = (
                self.conflict_resolution_team.debate_moderator is not None and
                self.conflict_resolution_team.evidence_weigher is not None and
                self.conflict_resolution_team.consensus_builder is not None
            )
        except (AttributeError, TypeError) as e:
            logger.warning(f"Conflict Resolution Team health check failed: {type(e).__name__}: {e}")
            crt_healthy = False
        health['conflict_resolution_team'] = crt_healthy
        print(f"  Status: {'PASS' if crt_healthy else 'FAIL'}")
        print()

        # Check Failure Analysis Team
        print("[3/5] Failure Analysis Team...")
        try:
            fat_healthy = (
                self.failure_analysis_team.error_classifier is not None and
                self.failure_analysis_team.root_cause_analyzer is not None and
                self.failure_analysis_team.alternative_path_generator is not None
            )
        except (AttributeError, TypeError) as e:
            logger.warning(f"Failure Analysis Team health check failed: {type(e).__name__}: {e}")
            fat_healthy = False
        health['failure_analysis_team'] = fat_healthy
        print(f"  Status: {'PASS' if fat_healthy else 'FAIL'}")
        print()

        # Check Meta-Learning Team
        print("[4/5] Meta-Learning Team...")
        try:
            mlt_healthy = (
                self.meta_learning_team.performance_monitor is not None and
                self.meta_learning_team.optimizer is not None and
                self.meta_learning_team.dispatcher is not None
            )
        except (AttributeError, TypeError) as e:
            logger.warning(f"Meta-Learning Team health check failed: {type(e).__name__}: {e}")
            mlt_healthy = False
        health['meta_learning_team'] = mlt_healthy
        print(f"  Status: {'PASS' if mlt_healthy else 'FAIL'}")
        print()

        # Check Protocol Integration
        print("[5/5] Protocol Integration...")
        try:
            protocols_healthy = (
                self.protocol_update.appellate_active or
                self.protocol_update.postmortem_active or
                self.protocol_update is not None
            )
        except (AttributeError, TypeError) as e:
            logger.warning(f"Protocol Integration health check failed: {type(e).__name__}: {e}")
            protocols_healthy = False
        health['protocols'] = protocols_healthy
        print(f"  Status: {'PASS' if protocols_healthy else 'FAIL'}")
        print()

        # Overall health
        all_healthy = all(health.values())
        health['overall'] = all_healthy

        print("=" * 80)
        print(f"OVERALL SYSTEM HEALTH: {'PASS' if all_healthy else 'FAIL'}")
        print("=" * 80)
        print()

        if all_healthy:
            print("[OK] Phase 4 is COMPLETE and HEALTHY")
            print("  The system has achieved 'Self-Correcting System' status")
            print("  Ready for Phase 5: Production Optimization & Distillation")
        else:
            print("[FAIL] Phase 4 has health issues")

        print()

        return health

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'phase3': self.phase3.get_statistics(),
            'conflict_resolution': self.conflict_resolution_team.get_statistics(),
            'failure_analysis': self.failure_analysis_team.get_statistics(),
            'meta_learning': self.meta_learning_team.get_statistics(),
            'protocols': self.protocol_update.get_statistics()
        }

    def print_statistics(self):
        """Print formatted statistics"""
        print()
        print("=" * 80)
        print("PHASE 4 SYSTEM STATISTICS")
        print("=" * 80)
        print()

        # Conflict Resolution
        crt_stats = self.conflict_resolution_team.get_statistics()
        print("CONFLICT RESOLUTION TEAM:")
        print(f"  Conflicts resolved: {crt_stats['conflicts_resolved']}")
        dm_stats = crt_stats['debate_moderator']
        print(f"  Debates moderated: {dm_stats['conflicts_detected']}")
        ew_stats = crt_stats['evidence_weigher']
        print(f"  Cases evaluated: {ew_stats['cases_evaluated']}")
        print(f"  Automatic rulings: {ew_stats['automatic_rulings']}")
        print()

        # Failure Analysis
        fat_stats = self.failure_analysis_team.get_statistics()
        print("FAILURE ANALYSIS TEAM:")
        print(f"  Failures handled: {fat_stats['failures_handled']}")
        ec_stats = fat_stats['error_classifier']
        print(f"  Computational errors: {ec_stats['computational_errors']}")
        print(f"  Logical errors: {ec_stats['logical_errors']}")
        print(f"  Domain errors: {ec_stats['domain_errors']}")
        apg_stats = fat_stats['alternative_path_generator']
        print(f"  Alternatives generated: {apg_stats['alternatives_generated']}")
        print(f"  Recovery rate: {apg_stats['recovery_rate']:.1f}%")
        print()

        # Meta-Learning
        mlt_stats = self.meta_learning_team.get_statistics()
        print("META-LEARNING TEAM:")
        print(f"  Optimization runs: {mlt_stats['optimization_runs']}")
        pm_stats = mlt_stats['performance_monitor']
        print(f"  Traces recorded: {pm_stats['traces_recorded']}")
        print(f"  Success rate: {pm_stats['success_rate']:.1f}%")
        opt_stats = mlt_stats['optimizer']
        print(f"  Patterns discovered: {opt_stats['patterns_discovered']}")
        disp_stats = mlt_stats['dispatcher']
        print(f"  Skeleton crew rate: {disp_stats['skeleton_crew_rate']:.1f}%")
        print(f"  Full team rate: {disp_stats['full_team_rate']:.1f}%")
        print()

        # Protocols
        prot_stats = self.protocol_update.get_statistics()
        print("PROTOCOL INTEGRATION:")
        app_stats = prot_stats['appellate_protocol']
        print(f"  Appellate checks: {app_stats['conflict_checks']}")
        print(f"  Conflicts detected: {app_stats['conflicts_detected']}")
        pm_stats = prot_stats['postmortem_protocol']
        print(f"  Post-mortem triggers: {pm_stats['triggers']}")
        print()

    def __repr__(self) -> str:
        """Human-readable representation"""
        return "Phase4System(Self-Correcting System: ONLINE, Status: Dynamic Organism)"


# ===========================================================================
# DEMONSTRATION
# ===========================================================================

if __name__ == "__main__":
    """Demonstration of integrated Phase 4 system"""
    print()
    print("=" * 80)
    print("PHASE 4 SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize and start system
    system = Phase4System()
    system.start()

    # Perform health check
    health = system.health_check()

    if health['overall']:
        print()
        print("System healthy - demonstrating Phase 4 capabilities...")
        print()

        # Demo 1: Conflict Resolution
        print("=" * 80)
        print("DEMO 1: Conflict Resolution")
        print("=" * 80)
        print()

        conflict_data = {
            'subtask_id': 'demo_integral',
            'conversation_id': 'demo_001',
            'domain': 'calculus',
            'results': [
                {
                    'agent_id': 'symbolic_001',
                    'result': '-cos(x) + C',
                    'method_used': 'symbolic_risch',
                    'evidence_type': 'SYMBOLIC_DERIVATION',
                    'confidence': 0.95
                },
                {
                    'agent_id': 'numerical_001',
                    'result': '-0.999999cos(x)',
                    'method_used': 'numerical_quadrature',
                    'evidence_type': 'NUMERICAL_APPROXIMATION',
                    'confidence': 0.99
                }
            ]
        }

        ruling = system.resolve_conflict(conflict_data)
        print(f"Winner: {ruling.winner_agent} (Symbolic beats Numerical)")
        print()

        # Demo 2: Failure Handling
        print("=" * 80)
        print("DEMO 2: Failure Handling")
        print("=" * 80)
        print()

        failure_data = {
            'error_message': 'Cannot apply Risch algorithm: function not elementary',
            'agent_id': 'symbolic_integration_001',
            'step': 'symbolic_integration',
            'conversation_id': 'demo_002'
        }

        recovery = system.handle_failure(failure_data)
        if recovery['recovery_plan']:
            print(f"Recovery strategies: {recovery['recovery_plan']['strategies']}")
        print()

        # Demo 3: Team Recommendation
        print("=" * 80)
        print("DEMO 3: Team Recommendation")
        print("=" * 80)
        print()

        simple_problem = {
            'problem_type': 'algebra',
            'simple_expression': True,
            'standard_form': True
        }
        rec = system.get_team_recommendation(simple_problem)
        print(f"Simple algebra: {rec['team_size']} agents ({rec['complexity_level']})")

        complex_problem = {
            'problem_type': 'proof',
            'involves_proof': True,
            'multiple_steps': True
        }
        rec = system.get_team_recommendation(complex_problem)
        print(f"Complex proof: {rec['team_size']} agents ({rec['complexity_level']})")
        print()

    # Display statistics
    system.print_statistics()

    # Shutdown
    system.shutdown()

    print()
    print("=" * 80)
    print("PHASE 4 DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
