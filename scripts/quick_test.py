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
SYMBO_AGENTIC_REASONERS Quick Test
===============
Runs a quick sanity test to verify the system is working.

Usage:
    python scripts/quick_test.py [--phase N] [--all]

Options:
    --phase N    Test specific phase (0-6, default: 0)
    --all        Run all phases
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def parse_args():
    parser = argparse.ArgumentParser(description='Quick SYMBO_AGENTIC_REASONERS Test')
    parser.add_argument('--phase', type=int, default=0, choices=range(0, 7),
                        help='Phase to test (0-6, default: 0 for core)')
    parser.add_argument('--all', action='store_true', help='Run all phases')
    return parser.parse_args()


def test_phase0():
    """Quick test of Phase 0: Core Infrastructure"""
    print("Testing Phase 0: Core Infrastructure")
    print("-" * 40)

    try:
        from symbo_agentic_reasoners.core import OMObject, BDIAgent, Blackboard
        from symbo_agentic_reasoners.protocols import FIPAMessage

        # Test OMDoc - OMObject represents mathematical objects
        obj = OMObject(variable="x")
        print(f"  [OK] OMObject created: variable={obj.variable}")

        # Test Blackboard
        bb = Blackboard()
        print(f"  [OK] Blackboard created")

        # Test FIPA Message
        msg = FIPAMessage(
            performative="inform",
            sender="test",
            receiver="test2",
            content={"test": "data"}
        )
        print(f"  [OK] FIPAMessage created: {msg.performative}")

        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_phase1():
    """Quick test of Phase 1: Cognitive Chassis"""
    print("Testing Phase 1: Cognitive Chassis")
    print("-" * 40)

    try:
        from symbo_agentic_reasoners.core import SolverEngine, get_solver_engine

        # Test SolverEngine
        engine = get_solver_engine()
        print(f"  [OK] SolverEngine created: {type(engine).__name__}")

        # Test ResourceCoordinator
        from symbo_agentic_reasoners.core import ResourceCoordinator, get_coordinator
        coordinator = get_coordinator()
        print(f"  [OK] ResourceCoordinator created: {type(coordinator).__name__}")

        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_phase2():
    """Quick test of Phase 2: Mathematical Workforce"""
    print("Testing Phase 2: Mathematical Workforce")
    print("-" * 40)

    try:
        from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
        from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist

        # Test supervisor
        supervisor = AlgebraSupervisor()
        print(f"  [OK] AlgebraSupervisor created: {supervisor.agent_id}")

        # Test specialist
        specialist = DifferentiationSpecialist()
        print(f"  [OK] DifferentiationSpecialist created: {specialist.agent_id}")

        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_phase3():
    """Quick test of Phase 3: Meta-Cognitive Middleware"""
    print("Testing Phase 3: Meta-Cognitive Middleware")
    print("-" * 40)

    try:
        from symbo_agentic_reasoners.middleware.knowledge_management import (
            ContextExtractorAgent
        )
        from symbo_agentic_reasoners.middleware.precondition_validation import (
            DomainCheckerAgent, AssumptionValidatorAgent, EdgeCaseDetectorAgent
        )
        from symbo_agentic_reasoners.middleware.theorem_library import (
            TheoremLibraryManager
        )
        from symbo_agentic_reasoners.middleware.pattern_indexer import (
            PatternIndexer
        )
        from symbo_agentic_reasoners.core import Blackboard

        # Create a blackboard for agents that need it
        blackboard = Blackboard()
        print(f"  [OK] Blackboard created for middleware tests")

        # Test context extractor (requires blackboard)
        context_agent = ContextExtractorAgent(blackboard=blackboard)
        print(f"  [OK] ContextExtractorAgent created")

        # Test domain checker (no dependencies)
        domain_agent = DomainCheckerAgent()
        print(f"  [OK] DomainCheckerAgent created")

        # Test assumption validator (no dependencies)
        validator_agent = AssumptionValidatorAgent()
        print(f"  [OK] AssumptionValidatorAgent created")

        # Test edge case detector (no dependencies)
        edge_agent = EdgeCaseDetectorAgent()
        print(f"  [OK] EdgeCaseDetectorAgent created")

        # Test theorem library manager (no dependencies)
        theorem_manager = TheoremLibraryManager()
        print(f"  [OK] TheoremLibraryManager created")

        # Test pattern indexer (no dependencies)
        pattern_indexer = PatternIndexer()
        print(f"  [OK] PatternIndexer created")

        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_phase4():
    """Quick test of Phase 4: Dynamic Governance"""
    print("Testing Phase 4: Dynamic Governance")
    print("-" * 40)

    try:
        from symbo_agentic_reasoners.middleware.conflict_resolution import ConflictResolutionTeam
        from symbo_agentic_reasoners.middleware.failure_analysis import FailureAnalysisTeam

        # Test conflict resolution team
        cr_team = ConflictResolutionTeam()
        print(f"  [OK] ConflictResolutionTeam created")

        # Test failure analysis team
        fa_team = FailureAnalysisTeam()
        print(f"  [OK] FailureAnalysisTeam created")

        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_phase5():
    """Quick test of Phase 5: Production Optimization"""
    print("Testing Phase 5: Production Optimization")
    print("-" * 40)

    try:
        from symbo_agentic_reasoners.optimization.distillation.pipeline import DistillationPipeline
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm import SymboLLMAdapter
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel

        # Test distillation pipeline
        pipeline = DistillationPipeline()
        print(f"  [OK] DistillationPipeline created")

        # Test SymboLLM adapter
        adapter = SymboLLMAdapter()
        print(f"  [OK] SymboLLMAdapter created")

        # Test evolutionary flywheel
        flywheel = EvolutionaryFlywheel()
        print(f"  [OK] EvolutionaryFlywheel created")

        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_phase6():
    """Quick test of Phase 6: Discovery Engine"""
    print("Testing Phase 6: Discovery Engine")
    print("-" * 40)

    try:
        from symbo_agentic_reasoners.discovery import (
            ProblemGenerator, InterestScorer, ExplorationCategory
        )
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            ExhaustiveEnumerator, EnumerationSpace
        )

        # Test problem generator
        generator = ProblemGenerator()
        print(f"  [OK] ProblemGenerator created")

        # Test interest scorer
        scorer = InterestScorer()
        print(f"  [OK] InterestScorer created")

        # Test exhaustive enumerator
        enumerator = ExhaustiveEnumerator()
        print(f"  [OK] ExhaustiveEnumerator created")

        # Test enumeration space
        space = EnumerationSpace(
            space_id="test_space",
            dimensions={"x": [1, 2, 3], "y": ["a", "b"]}
        )
        print(f"  [OK] EnumerationSpace created: {space.space_id}")

        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    args = parse_args()

    print("=" * 50)
    print("SYMBO_AGENTIC_REASONERS Quick Test")
    print("=" * 50)
    print()

    test_functions = {
        0: test_phase0,
        1: test_phase1,
        2: test_phase2,
        3: test_phase3,
        4: test_phase4,
        5: test_phase5,
        6: test_phase6,
    }

    if args.all:
        # Run all phases
        results = {}
        for phase in range(7):
            print()
            try:
                results[phase] = test_functions[phase]()
            except Exception as e:
                print(f"  [ERROR] Phase {phase} failed: {e}")
                results[phase] = False

        print()
        print("=" * 50)
        print("Summary")
        print("=" * 50)
        for phase, success in results.items():
            status = "PASS" if success else "FAIL"
            print(f"  Phase {phase}: [{status}]")

        all_passed = all(results.values())
        return 0 if all_passed else 1

    else:
        # Run single phase
        try:
            success = test_functions[args.phase]()

            print()
            if success:
                print(f"[SUCCESS] Phase {args.phase} test passed!")
                return 0
            else:
                print(f"[WARNING] Phase {args.phase} test had issues")
                return 1

        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    sys.exit(main())
