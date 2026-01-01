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

import sys
import os
import traceback

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Phase 3
from symbo_agentic_reasoners.middleware.precondition_validation import (
    DomainCheckerAgent, AssumptionValidatorAgent, ConstraintPropagatorAgent, EdgeCaseDetectorAgent
)
from symbo_agentic_reasoners.middleware.knowledge_management import (
    ContextExtractorAgent, MemoryIndexerAgent, RetrievalSpecialistAgent
)
from symbo_agentic_reasoners.middleware.hypothesis_generation import (
    HypothesisGeneratorAgent, PathEvaluatorAgent, BacktrackingManagerAgent
)

# Phase 4
from symbo_agentic_reasoners.middleware.conflict_resolution import (
    DebateModerator, EvidenceWeigher, ConsensusBuilder
)
from symbo_agentic_reasoners.middleware.failure_analysis import (
    ErrorClassifier, RootCauseAnalyzer, AlternativePathGenerator
)
from symbo_agentic_reasoners.middleware.meta_learning import (
    AgentSelectorOptimizer, AdaptiveDispatcher, PerformanceMonitor
)

# Phase 5
from symbo_agentic_reasoners.optimization.distillation.pipeline import StudentModelTrainer
from symbo_agentic_reasoners.optimization.distillation.harvester import ThoughtTraceHarvester

# Phase 6
from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import PatternRecognizer
from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeEvolutionaryProposer
from symbo_agentic_reasoners.discovery.algorithm.heuristic_distiller import HeuristicDistiller
from symbo_agentic_reasoners.discovery.undecidability import DecidabilityChecker, InteractiveGuidanceLiaison
from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import AutoFormalizationPipeline
from symbo_agentic_reasoners.discovery.formal.vector_database_updater import VectorDatabaseUpdater

def verify_agent(agent_class, name, *args, **kwargs):
    try:
        print(f"Verifying {name}...", end=" ")
        agent = agent_class(*args, **kwargs)
        print("OK")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        # traceback.print_exc()
        return False

def verify_phase3():
    print("\n--- Phase 3 Verification ---")
    verify_agent(DomainCheckerAgent, "DomainCheckerAgent")
    verify_agent(AssumptionValidatorAgent, "AssumptionValidatorAgent")
    verify_agent(ConstraintPropagatorAgent, "ConstraintPropagatorAgent", blackboard=None)
    verify_agent(EdgeCaseDetectorAgent, "EdgeCaseDetectorAgent")
    
    verify_agent(ContextExtractorAgent, "ContextExtractorAgent", blackboard=None)
    verify_agent(MemoryIndexerAgent, "MemoryIndexerAgent", vector_db=None)
    verify_agent(RetrievalSpecialistAgent, "RetrievalSpecialistAgent", vector_db=None)
    
    verify_agent(HypothesisGeneratorAgent, "HypothesisGeneratorAgent")
    verify_agent(PathEvaluatorAgent, "PathEvaluatorAgent")
    verify_agent(BacktrackingManagerAgent, "BacktrackingManagerAgent", blackboard=None)

def verify_phase4():
    print("\n--- Phase 4 Verification ---")
    verify_agent(DebateModerator, "DebateModerator", blackboard=None)
    verify_agent(EvidenceWeigher, "EvidenceWeigher", blackboard=None)
    verify_agent(ConsensusBuilder, "ConsensusBuilder", blackboard=None)
    
    verify_agent(ErrorClassifier, "ErrorClassifier", blackboard=None)
    verify_agent(RootCauseAnalyzer, "RootCauseAnalyzer", blackboard=None)
    verify_agent(AlternativePathGenerator, "AlternativePathGenerator", blackboard=None)
    
    verify_agent(AgentSelectorOptimizer, "AgentSelectorOptimizer", blackboard=None)
    verify_agent(AdaptiveDispatcher, "AdaptiveDispatcher", blackboard=None)
    verify_agent(PerformanceMonitor, "PerformanceMonitor", blackboard=None)

def verify_phase5():
    print("\n--- Phase 5 Verification ---")
    verify_agent(StudentModelTrainer, "StudentModelTrainer", student_model=None)
    verify_agent(ThoughtTraceHarvester, "ThoughtTraceHarvester", blackboard=None)

def verify_phase6():
    print("\n--- Phase 6 Verification ---")
    verify_agent(PatternRecognizer, "PatternRecognizer")
    verify_agent(CodeEvolutionaryProposer, "CodeEvolutionaryProposer")
    verify_agent(HeuristicDistiller, "HeuristicDistiller")
    verify_agent(DecidabilityChecker, "DecidabilityChecker")
    verify_agent(InteractiveGuidanceLiaison, "InteractiveGuidanceLiaison")
    verify_agent(AutoFormalizationPipeline, "AutoFormalizationPipeline")
    verify_agent(VectorDatabaseUpdater, "VectorDatabaseUpdater")

if __name__ == "__main__":
    verify_phase3()
    verify_phase4()
    verify_phase5()
    verify_phase6()
