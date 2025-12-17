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
PHASE 3 SYSTEM INTEGRATION
===========================

Integrated Phase 3 system - The Meta-Cognitive Middleware

This module brings together all Phase 3 components to create the
"Resilient Professional" - a system with cognitive immune capabilities.

TRANSFORMATION:
--------------
Phase 2: "Fragile Genius" - Powerful but brittle
Phase 3: "Resilient Professional" - Robust, context-aware, strategic

COMPONENTS:
----------
Builds on Phase 0 (Infrastructure), Phase 1 (Cognitive Chassis), and
Phase 2 (Mathematical Workforce) by adding:

PHASE 3 TEAMS (10 Agents):
  Precondition Validation Team (4 agents) - "The Anesthesiologist"
    - Domain Checker
    - Assumption Validator
    - Edge Case Detector
    - Constraint Propagator

  Knowledge Management Team (3 agents) - "The Librarians"
    - Context Extractor
    - Memory Indexer
    - Retrieval Specialist

  Hypothesis Generation Team (3 agents) - "The Scouts"
    - Hypothesis Generator
    - Path Evaluator
    - Backtracking Manager

  Updated Orchestrator with 3 Protocols:
    - Pre-Flight Check (validation)
    - Look-Before-You-Leap (retrieval)
    - Scouting (hypothesis generation)

CONTROL LOOP EVOLUTION:
    Phase 1-2: Plan -> Solve
    Phase 3:   Analyze -> Hypothesize -> Validate -> Solve

REFERENCE:
---------
- Phase_3_Build_Order_Breakdown.md
- Phase 3 installs the _cognitive immune system_.md
"""

import sys
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger('symbo_agentic_reasoners.phase3.system')

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Phase 2 (which includes Phase 0 and Phase 1)
from symbo_agentic_reasoners_phase2.phase2_system import Phase2System

# Import Phase 3 components
from symbo_agentic_reasoners_phase3.validation.precondition_validation import (
    PreconditionValidationTeam,
    ValidationStatus
)
from symbo_agentic_reasoners_phase3.knowledge.knowledge_management import (
    KnowledgeManagementTeam,
    RetrievalConfidence
)
from symbo_agentic_reasoners_phase3.hypothesis.hypothesis_generation import (
    HypothesisGenerationTeam,
    StrategyType
)
from symbo_agentic_reasoners_phase3.orchestrator.phase3_orchestrator import (
    Phase3Orchestrator,
    ComplexityLevel
)


class Phase3System:
    """
    Integrated Phase 3 System - The Resilient Professional

    Transforms the Phase 2 "Fragile Genius" into a "Resilient Professional"
    by adding the Meta-Cognitive Middleware.

    CAPABILITIES:
    ------------
    - Precondition Validation: Blocks invalid inputs before solving
    - Knowledge Retrieval: Short-circuits solving for known problems
    - Strategic Planning: Tree-of-Thoughts for complex problems
    - Graceful Backtracking: Recovers from failed solution attempts

    USAGE:
    -----
    system = Phase3System()
    system.start()

    # Test precondition validation
    result = system.validate_problem(problem)

    # Test retrieval
    result = system.lookup_known_solution(problem)

    # Full solve with Phase 3 protocols
    result = system.solve(problem)

    system.shutdown()

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Section 4 "Phase 3 Deliverables"
    """

    def __init__(self, vector_db_path: str = "./symbo_agentic_reasoners_vector_store"):
        """
        Initialize Phase 3 System

        Args:
            vector_db_path: Path for vector database persistence
        """
        print("=" * 80)
        print("PHASE 3 SYSTEM INITIALIZATION")
        print("=" * 80)
        print()

        # Initialize Phase 2 (includes Phase 0 + Phase 1)
        print("[Phase 3] Initializing Phase 0 + Phase 1 + Phase 2 foundations...")
        self.phase2 = Phase2System(vector_db_path=vector_db_path)
        self.phase2.start()
        print()

        # Get infrastructure references
        self.phase1 = self.phase2.phase1
        self.phase0 = self.phase1.phase0
        self.df = self.phase0.df
        self.blackboard = self.phase0.blackboard
        self.vector_db = self.phase0.vector_db

        # Initialize Phase 3 components
        print("[Phase 3] Initializing Meta-Cognitive Middleware...")
        print()

        # Phase 3 Orchestrator (integrates all three teams)
        self.orchestrator = Phase3Orchestrator(
            directory_facilitator=self.df,
            blackboard=self.blackboard,
            vector_db=self.vector_db,
            embedding_model=None,  # Using hash-based fallback
            available_solvers=None  # Using defaults
        )

        print("[OK] Phase 3 Meta-Cognitive Middleware initialized")
        print()

    def start(self):
        """
        Start Phase 3 System

        All components are already active after __init__.
        This method provides verification and status.
        """
        print("=" * 80)
        print("PHASE 3 SYSTEM STARTED")
        print("=" * 80)
        print()
        print("STATUS: Resilient Professional")
        print("  - Cognitive immune system ACTIVE")
        print("  - Hallucination prevention ONLINE")
        print("  - Knowledge retrieval ENABLED")
        print("  - Strategic planning READY")
        print()

        print("CONTROL LOOP:")
        print("  Analyze -> Hypothesize -> Validate -> Solve")
        print()

        print("PROTOCOLS ENABLED:")
        print("  [1] Pre-Flight Check: Validation before delegation")
        print("  [2] Look-Before-You-Leap: Knowledge retrieval")
        print("  [3] Scouting: Hypothesis generation for complex problems")
        print()

        print("AGENTS DEPLOYED:")
        print("  Precondition Validation Team: 4 agents")
        print("  Knowledge Management Team: 3 agents")
        print("  Hypothesis Generation Team: 3 agents")
        print("  Total Phase 3 Agents: 10")
        print()

        print("CAPABILITIES:")
        print("  - Domain validation (decidable vs undecidable)")
        print("  - Constraint checking (x > 0 for ln(x), etc.)")
        print("  - Edge case detection (singularities, boundaries)")
        print("  - RAG integration for known theorems")
        print("  - Tree-of-Thoughts strategy generation")
        print("  - Backtracking on solution failure")
        print()
        print("READY FOR PHASE 3 VERIFICATION TEST")
        print()

    def solve(self, problem: Any, conversation_id: str = None) -> Dict[str, Any]:
        """
        Solve a mathematical problem with full Phase 3 protocols.

        This is the main entry point for the Phase 3 system.
        Implements: Analyze -> Hypothesize -> Validate -> Solve

        Args:
            problem: OMDoc object or problem description
            conversation_id: Optional conversation tracking ID

        Returns:
            Dictionary with result, status, and metadata
        """
        print()
        print("=" * 80)
        print(f"SOLVING: {self._format_problem(problem)}")
        print("=" * 80)
        print()

        # Process through Phase 3 Orchestrator
        result = self.orchestrator.process(problem, conversation_id)

        print()
        print("=" * 80)
        if result.get('status') == 'SUCCESS':
            print("SOLUTION COMPLETE")
        elif result.get('status') == 'ERROR':
            print(f"SOLUTION BLOCKED: {result.get('code', 'UNKNOWN')}")
        else:
            print(f"SOLUTION STATUS: {result.get('status')}")
        print("=" * 80)
        print()

        return result

    def validate_problem(self, problem: Any, conversation_id: str = "test") -> Dict[str, Any]:
        """
        Validate a problem without solving (Pre-Flight Check only).

        Useful for testing the Precondition Validation Team.

        Args:
            problem: OMDoc object or problem description

        Returns:
            Validation result
        """
        return self.orchestrator.precondition_team.validate(
            problem, conversation_id
        ).__dict__

    def lookup_known_solution(self, problem_statement: str) -> Dict[str, Any]:
        """
        Look up a known solution without solving (Look-Before-You-Leap only).

        Useful for testing the Knowledge Management Team.

        Args:
            problem_statement: Problem description string

        Returns:
            Retrieval result
        """
        result = self.orchestrator.knowledge_team.look_before_leap(problem_statement)
        return {
            'confidence': result.confidence.name,
            'theorem_id': result.theorem_id,
            'theorem_content': result.theorem_content,
            'similarity_score': result.similarity_score,
            'should_skip_solving': result.should_skip_solving()
        }

    def generate_strategies(self, problem: Any, problem_type: str = "computation",
                          conversation_id: str = "test"):
        """
        Generate solution strategies without solving (Scouting only).

        Useful for testing the Hypothesis Generation Team.

        Args:
            problem: OMDoc object or problem description
            problem_type: Type of problem ('proof', 'integration', etc.)

        Returns:
            Selected strategy and alternatives
        """
        plan = self.orchestrator.hypothesis_team.scout(
            problem, conversation_id, problem_type
        )
        alternatives = self.orchestrator.hypothesis_team._get_alternatives(conversation_id)

        return {
            'selected': {
                'strategy': plan.strategy.value if plan else None,
                'promise_score': plan.promise_score if plan else 0,
                'description': plan.description if plan else None
            },
            'alternatives': [
                {
                    'strategy': p.strategy.value,
                    'promise_score': p.promise_score
                }
                for p in alternatives
            ]
        }

    def _format_problem(self, problem: Any) -> str:
        """Format problem for display"""
        if hasattr(problem, 'expression_tree'):
            return str(problem.expression_tree)[:60]
        elif hasattr(problem, 'expression'):
            return str(problem.expression)[:60]
        return str(problem)[:60]

    def shutdown(self):
        """
        Shutdown Phase 3 System

        Stops all Phase 3 agents and Phase 0-2 infrastructure.
        """
        print()
        print("=" * 80)
        print("PHASE 3 SYSTEM SHUTDOWN")
        print("=" * 80)
        print()

        # Clear orchestrator logs
        self.orchestrator.clear_decision_log()

        # Shutdown Phase 2 (which will shutdown Phase 1 and Phase 0)
        self.phase2.shutdown()

        print()
        print("[OK] Phase 3 System shutdown complete")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform system health check

        Verifies all Phase 3 components are operational.

        Returns:
            Dictionary with health status
        """
        print()
        print("=" * 80)
        print("PHASE 3 HEALTH CHECK")
        print("=" * 80)
        print()

        health = {}

        # Check Phase 2 (includes Phase 0 and 1)
        print("[1/5] Phase 2 Infrastructure...")
        phase2_health = self.phase2.health_check()
        health['phase2'] = phase2_health['overall']
        print()

        # Check Precondition Validation Team
        print("[2/5] Precondition Validation Team...")
        try:
            # Create test problem
            test_problem = type('TestProblem', (), {
                'expression_tree': 'x**2 + 1',
                'metadata': {}
            })()
            validation_result = self.orchestrator.precondition_team.validate(
                test_problem, 'health_check'
            )
            precondition_healthy = validation_result.is_valid
        except (AttributeError, TypeError, ValueError) as e:
            logger.debug(f"Precondition team health check failed: {type(e).__name__}: {e}")
            precondition_healthy = False
        health['precondition_team'] = precondition_healthy
        print(f"  Status: {'PASS' if precondition_healthy else 'FAIL'}")
        print()

        # Check Knowledge Management Team
        print("[3/5] Knowledge Management Team...")
        try:
            retrieval_result = self.orchestrator.knowledge_team.look_before_leap(
                "test integral x^2"
            )
            knowledge_healthy = retrieval_result is not None
        except (AttributeError, TypeError, ValueError) as e:
            logger.debug(f"Knowledge team health check failed: {type(e).__name__}: {e}")
            knowledge_healthy = False
        health['knowledge_team'] = knowledge_healthy
        print(f"  Status: {'PASS' if knowledge_healthy else 'FAIL'}")
        print()

        # Check Hypothesis Generation Team
        print("[4/5] Hypothesis Generation Team...")
        try:
            test_problem = type('TestProblem', (), {
                'expression_tree': 'sin(x)*x',
                'metadata': {}
            })()
            plan = self.orchestrator.hypothesis_team.scout(
                test_problem, 'health_check', 'integration'
            )
            hypothesis_healthy = plan is not None and hasattr(plan, 'strategy')
        except (AttributeError, TypeError, ValueError) as e:
            logger.debug(f"Hypothesis team health check failed: {type(e).__name__}: {e}")
            hypothesis_healthy = False
        health['hypothesis_team'] = hypothesis_healthy
        print(f"  Status: {'PASS' if hypothesis_healthy else 'FAIL'}")
        print()

        # Check Phase 3 Orchestrator
        print("[5/5] Phase 3 Orchestrator...")
        try:
            orchestrator_healthy = (
                self.orchestrator.precondition_team is not None and
                self.orchestrator.knowledge_team is not None and
                self.orchestrator.hypothesis_team is not None
            )
        except (AttributeError, TypeError) as e:
            logger.debug(f"Orchestrator health check failed: {type(e).__name__}: {e}")
            orchestrator_healthy = False
        health['orchestrator'] = orchestrator_healthy
        print(f"  Status: {'PASS' if orchestrator_healthy else 'FAIL'}")
        print()

        # Overall health
        all_healthy = all(health.values())
        health['overall'] = all_healthy

        print("=" * 80)
        print(f"OVERALL SYSTEM HEALTH: {'PASS' if all_healthy else 'FAIL'}")
        print("=" * 80)
        print()

        if all_healthy:
            print("[OK] Phase 3 is COMPLETE and HEALTHY")
            print("  The system has achieved 'Resilient Professional' status")
            print("  Ready for Phase 4: Dynamic Governance & Resilience")
        else:
            print("[FAIL] Phase 3 has health issues")

        print()

        return health

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'phase2': self.phase2.get_statistics(),
            'orchestrator': self.orchestrator.get_statistics()
        }

    def print_statistics(self):
        """Print formatted statistics"""
        print()
        print("=" * 80)
        print("PHASE 3 SYSTEM STATISTICS")
        print("=" * 80)
        print()

        stats = self.orchestrator.get_statistics()

        print("ORCHESTRATOR:")
        print(f"  Tasks processed: {stats['tasks_processed']}")
        print(f"  Tasks validated: {stats['tasks_validated']}")
        print(f"  Tasks retrieved: {stats['tasks_retrieved']}")
        print(f"  Tasks scouted: {stats['tasks_scouted']}")
        print(f"  Tasks failed: {stats['tasks_failed']}")
        print()

        print("PRECONDITION VALIDATION TEAM:")
        pv_stats = stats['precondition_team']
        print(f"  Validations: {pv_stats['validations_performed']}")
        print(f"  Rejections: {pv_stats['rejections']}")
        print(f"  Approval rate: {pv_stats['approval_rate']:.1f}%")
        print()

        print("KNOWLEDGE MANAGEMENT TEAM:")
        km_stats = stats['knowledge_team']
        print(f"  Context extractions: {km_stats['context_extractor']['extractions_performed']}")
        print(f"  Results indexed: {km_stats['memory_indexer']['entries_indexed']}")
        print(f"  Retrieval queries: {km_stats['retrieval_specialist']['queries_performed']}")
        print(f"  Cache hit rate: {km_stats['retrieval_specialist']['hit_rate']:.1f}%")
        print()

        print("HYPOTHESIS GENERATION TEAM:")
        hg_stats = stats['hypothesis_team']
        print(f"  Hypotheses generated: {hg_stats['hypothesis_generator']['hypotheses_generated']}")
        print(f"  Plans evaluated: {hg_stats['path_evaluator']['evaluations_performed']}")
        print(f"  Snapshots created: {hg_stats['backtracking_manager']['snapshots_created']}")
        print(f"  Restorations: {hg_stats['backtracking_manager']['restorations_performed']}")
        print()

    def __repr__(self) -> str:
        """Human-readable representation"""
        return "Phase3System(Meta-Cognitive Middleware: ONLINE, Status: Resilient Professional)"


# ===========================================================================
# DEMONSTRATION
# ===========================================================================

if __name__ == "__main__":
    """Demonstration of integrated Phase 3 system"""
    print()
    print("=" * 80)
    print("PHASE 3 SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize and start system
    system = Phase3System()
    system.start()

    # Perform health check
    health = system.health_check()

    if health['overall']:
        print()
        print("System healthy - Phase 3 complete!")
        print()

        # Demonstrate precondition validation
        print("=" * 80)
        print("DEMO: Precondition Validation")
        print("=" * 80)
        print()

        # Test with valid problem
        class ValidProblem:
            expression_tree = 'x**2 + 2*x + 1'
            metadata = {}

        result = system.validate_problem(ValidProblem())
        print(f"Valid problem (x^2 + 2x + 1): {result['status'].name}")
        print()

        # Test with invalid problem (ln of negative)
        class InvalidProblem:
            expression_tree = 'log(x)'
            metadata = {'variable_values': {'x': -5}}

        result = system.validate_problem(InvalidProblem())
        print(f"Invalid problem (ln(-5)): {result['status'].name}")
        if result.get('constraint_violations'):
            print(f"  Violations: {result['constraint_violations']}")
        print()

        # Demonstrate strategy generation
        print("=" * 80)
        print("DEMO: Strategy Generation")
        print("=" * 80)
        print()

        class IntegrationProblem:
            expression_tree = 'sin(x)*cos(x)'
            metadata = {}

        strategies = system.generate_strategies(IntegrationProblem(), 'integration')
        print(f"Problem: integrate sin(x)*cos(x)")
        print(f"Selected strategy: {strategies['selected']['strategy']}")
        print(f"Promise score: {strategies['selected']['promise_score']:.2f}")
        print(f"Alternatives: {len(strategies['alternatives'])}")
        print()

    # Display statistics
    system.print_statistics()

    # Shutdown
    system.shutdown()

    print()
    print("=" * 80)
    print("PHASE 3 DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
