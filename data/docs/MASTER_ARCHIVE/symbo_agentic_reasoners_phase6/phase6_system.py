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
Phase 6 System: The Mathematical Discovery Engine
===================================================

Complete integration of the 13-agent Discovery Engine architecture.
Transitions the system from Problem Solver to Discovery Engine.

Teams Integrated:
1. Conjecture Generation Team (3 agents) - "The Theorist"
2. Deep Search Team (3 agents) - "The Explorer"
3. Algorithm Discovery Unit (3 agents) - "FunSearch Pattern"
4. Undecidability Navigator (2 agents) - "Boundary Watcher"
5. Formal Knowledge Integration (2 agents) - "The Archivist"

Dependencies:
- Phase 5: ThoughtTraceHarvester, DistillationPipeline, EvolutionaryFlywheel
- Phase 1: Verification Core (Ax-Prover/Logic Checker)
- Phase 3: Knowledge Management Team (RAG infrastructure)
- Phase 0: OMDoc/OpenMath, FIPA-ACL

Reference Documentation:
- Phase 6 represents the transition from a Problem Solving Engine.docx
- Phase 6 must engineer the capacity for novel mathematical discovery.docx
- phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx
- Phase_6_Build_Order_Breakdown.md

Hardware Target: AMD Ryzen 7 8700F, RTX 4060 (8GB VRAM), 32GB RAM
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.phase6_system')
except ImportError:
    logger = logging.getLogger(__name__)


class MathematicalSearchError(Exception):
    """Error during mathematical search/proof attempt - expected failure mode"""
    pass


class SystemRuntimeError(Exception):
    """System-level runtime error - unexpected failure mode"""
    pass

# Team 1: Conjecture Generation
from .conjecture_generation import (
    SyntheticDataGenerator,
    PatternRecognizer,
    ConjectureFormalizer,
    CandidateConjecture,
    ConjectureStatus
)

# Team 2: Deep Search
from .deep_search import (
    PolicyNetwork,
    CriticNetwork,
    SearchTreeManager,
    ProofState,
    SearchResult,
    SymPyProver
)

# Team 3: Algorithm Discovery
from .algorithm_discovery import (
    CodeEvolutionaryProposer,
    SandboxEvaluator,
    HeuristicDistiller,
    ProblemSpecification,
    CodeCandidate
)

# Team 4: Undecidability Navigator
from .undecidability_navigator import (
    DecidabilityChecker,
    DecidabilityClass,
    InteractiveGuidanceLiaison,
    ProofStateSummary
)

# Team 5: Formal Knowledge Integration
from .formal_knowledge_integration import (
    AutoFormalizationPipeline,
    VectorDatabaseUpdater,
    FormalizedDiscovery
)


class SystemStatus(Enum):
    """Status of the Phase 6 system"""
    STOPPED = 'stopped'
    STARTING = 'starting'
    RUNNING = 'running'
    PAUSED = 'paused'
    ERROR = 'error'


@dataclass
class DiscoveryCycleResult:
    """Result of a discovery cycle"""
    cycle_id: str
    theorems_generated: int
    conjectures_filtered: int
    proofs_attempted: int
    proofs_succeeded: int
    discoveries_integrated: int
    time_elapsed_ms: float
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'cycle_id': self.cycle_id,
            'theorems_generated': self.theorems_generated,
            'conjectures_filtered': self.conjectures_filtered,
            'proofs_attempted': self.proofs_attempted,
            'proofs_succeeded': self.proofs_succeeded,
            'discoveries_integrated': self.discoveries_integrated,
            'time_elapsed_ms': self.time_elapsed_ms,
            'success_rate': self.proofs_succeeded / max(1, self.proofs_attempted) * 100,
            'errors': self.errors
        }


class Phase6System:
    """
    Phase 6: The Mathematical Discovery Engine

    Complete integration of all 13 agents across 5 teams. Provides:
    - Autonomous conjecture generation and proving
    - Algorithm discovery via evolutionary code search
    - Decidability-aware search resource management
    - Knowledge integration with the Phase 2 workforce

    Usage:
        system = Phase6System()
        system.start()

        # Run discovery cycle
        result = system.run_discovery_cycle(num_theorems=100)

        # Run algorithm discovery
        heuristic = system.run_algorithm_discovery(problem_spec)

        system.shutdown()
    """

    def __init__(
        self,
        # External Dependencies
        phase5_system=None,
        verification_core=None,
        knowledge_base=None,
        guidance_callback: Callable = None,
        # Team 1: Conjecture Generation
        synthetic_data_generator: Optional[SyntheticDataGenerator] = None,
        pattern_recognizer: Optional[PatternRecognizer] = None,
        conjecture_formalizer: Optional[ConjectureFormalizer] = None,
        # Team 2: Deep Search
        policy_network: Optional[PolicyNetwork] = None,
        critic_network: Optional[CriticNetwork] = None,
        prover_engine: Optional[Any] = None,
        search_tree_manager: Optional[SearchTreeManager] = None,
        # Team 3: Algorithm Discovery
        code_evolutionary_proposer: Optional[CodeEvolutionaryProposer] = None,
        sandbox_evaluator: Optional[SandboxEvaluator] = None,
        heuristic_distiller: Optional[HeuristicDistiller] = None,
        # Team 4: Undecidability Navigator
        decidability_checker: Optional[DecidabilityChecker] = None,
        interactive_guidance_liaison: Optional[InteractiveGuidanceLiaison] = None,
        # Team 5: Formal Knowledge Integration
        auto_formalization_pipeline: Optional[AutoFormalizationPipeline] = None,
        vector_database_updater: Optional[VectorDatabaseUpdater] = None
    ):
        """
        Initialize the Phase 6 Discovery Engine.

        Args:
            phase5_system: Phase 5 system for distillation integration
            verification_core: Phase 1 verification core
            knowledge_base: Phase 3 knowledge base for RAG
            guidance_callback: Callback for human guidance requests
            [component_name]: Optional injected instance for any internal component
        """
        self.phase5 = phase5_system
        self.verification_core = verification_core
        self.knowledge_base = knowledge_base

        # System state
        self._status = SystemStatus.STOPPED
        self.started_at: Optional[datetime] = None
        self.cycle_count = 0

        # Initialize Team 1: Conjecture Generation
        self.synthetic_data_generator = synthetic_data_generator or SyntheticDataGenerator()
        self.pattern_recognizer = pattern_recognizer or PatternRecognizer(knowledge_base=knowledge_base)
        self.conjecture_formalizer = conjecture_formalizer or ConjectureFormalizer()

        # Initialize Team 2: Deep Search
        self.policy_network = policy_network or PolicyNetwork()
        self.critic_network = critic_network or CriticNetwork()
        self.prover_engine = prover_engine or SymPyProver()
        
        if search_tree_manager:
            self.search_tree_manager = search_tree_manager
        else:
            self.search_tree_manager = SearchTreeManager(
                policy_network=self.policy_network,
                critic_network=self.critic_network,
                prover_engine=self.prover_engine
            )

        # Initialize Team 3: Algorithm Discovery
        self.code_evolutionary_proposer = code_evolutionary_proposer or CodeEvolutionaryProposer()
        self.sandbox_evaluator = sandbox_evaluator or SandboxEvaluator()
        self.heuristic_distiller = heuristic_distiller or HeuristicDistiller()

        # Initialize Team 4: Undecidability Navigator
        self.decidability_checker = decidability_checker or DecidabilityChecker()
        self.interactive_guidance_liaison = interactive_guidance_liaison or InteractiveGuidanceLiaison(
            notification_callback=guidance_callback
        )

        # Initialize Team 5: Formal Knowledge Integration
        self.auto_formalization_pipeline = auto_formalization_pipeline or AutoFormalizationPipeline(
            verification_core=verification_core
        )
        self.vector_database_updater = vector_database_updater or VectorDatabaseUpdater()

        # Statistics
        self.stats = {
            'discovery_cycles': 0,
            'total_theorems_generated': 0,
            'total_proofs_found': 0,
            'algorithms_discovered': 0,
            'discoveries_integrated': 0,
            'undecidable_detected': 0,
            'human_guidance_requested': 0
        }

    @property
    def status(self) -> str:
        """Return status as string for compatibility"""
        return self._status.value

    @status.setter
    def status(self, value):
        """Set status from string or enum"""
        if isinstance(value, str):
            self._status = SystemStatus(value)
        else:
            self._status = value

    def start(self):
        """Start the Phase 6 system"""
        if self._status == SystemStatus.RUNNING:
            return

        self._status = SystemStatus.STARTING
        self.started_at = datetime.now()

        # Perform initialization checks
        try:
            self._initialize_components()
            self._status = SystemStatus.RUNNING
        except Exception as e:
            self._status = SystemStatus.ERROR
            raise RuntimeError(f"Failed to start Phase 6 system: {e}")

    def shutdown(self):
        """Shutdown the Phase 6 system"""
        self._status = SystemStatus.STOPPED

        # Reset components
        self.synthetic_data_generator.reset()
        self.pattern_recognizer.reset()
        self.search_tree_manager.reset()
        self.decidability_checker.reset()
        self.interactive_guidance_liaison.reset()
        self.auto_formalization_pipeline.reset()
        self.vector_database_updater.reset()

    def pause(self):
        """Pause the system"""
        if self._status == SystemStatus.RUNNING:
            self._status = SystemStatus.PAUSED

    def resume(self):
        """Resume the system"""
        if self._status == SystemStatus.PAUSED:
            self._status = SystemStatus.RUNNING

    def _initialize_components(self):
        """Initialize all components"""
        # Verify all components are healthy
        if not self.synthetic_data_generator.health_check():
            raise RuntimeError("SyntheticDataGenerator health check failed")
        if not self.policy_network.health_check():
            raise RuntimeError("PolicyNetwork health check failed")
        if not self.critic_network.health_check():
            raise RuntimeError("CriticNetwork health check failed")
        if not self.decidability_checker.health_check():
            raise RuntimeError("DecidabilityChecker health check failed")

    def run_discovery_cycle(
        self,
        num_theorems: int = 100,
        search_budget: int = 1000,
        max_candidates: int = None
    ) -> DiscoveryCycleResult:
        """
        Run a complete discovery cycle.

        Steps:
        1. Generate synthetic theorems
        2. Filter for interesting conjectures
        3. Assess decidability
        4. Attempt proofs with bounded search
        5. Integrate successful discoveries

        Args:
            num_theorems: Number of synthetic theorems to generate
            search_budget: MCTS simulation budget per proof attempt
            max_candidates: Maximum candidates to process (None for all)

        Returns:
            DiscoveryCycleResult with cycle statistics
        """
        if self._status != SystemStatus.RUNNING:
            raise RuntimeError("System not running. Call start() first.")

        # Input Validation
        if num_theorems <= 0:
            logger.warning(f"run_discovery_cycle called with num_theorems={num_theorems}. Returning empty result.")
            return DiscoveryCycleResult(
                cycle_id=f"cycle_{self.cycle_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                theorems_generated=0,
                conjectures_filtered=0,
                proofs_attempted=0,
                proofs_succeeded=0,
                discoveries_integrated=0,
                time_elapsed_ms=0,
                errors=["Invalid input: num_theorems must be positive"]
            )

        if search_budget <= 0:
             logger.warning(f"run_discovery_cycle called with search_budget={search_budget}. Using default budget of 10.")
             search_budget = 10

        self.cycle_count += 1
        self.stats['discovery_cycles'] += 1
        cycle_id = f"cycle_{self.cycle_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        start_time = time.time()
        result = DiscoveryCycleResult(
            cycle_id=cycle_id,
            theorems_generated=0,
            conjectures_filtered=0,
            proofs_attempted=0,
            proofs_succeeded=0,
            discoveries_integrated=0,
            time_elapsed_ms=0
        )

        try:
            # Step 1: Generate synthetic theorems
            theorem_stream = self.synthetic_data_generator.generate_stream(
                batch_size=max(1, num_theorems // 10), # Use smaller batches for responsiveness
                max_theorems=num_theorems
            )

            # Step 2: Filter for interesting conjectures
            # Use max_candidates if provided, otherwise limit by num_theorems (heuristic)
            filter_limit = max_candidates if max_candidates is not None else num_theorems
            
            candidate_stream = self.pattern_recognizer.filter_stream(
                theorem_stream,
                batch_size=max(1, num_theorems // 10),
                max_candidates=filter_limit
            )

            candidates = []
            for candidate in candidate_stream:
                candidates.append(candidate)
                result.theorems_generated += 1

                if filter_limit and len(candidates) >= filter_limit:
                    break

            result.conjectures_filtered = len(candidates)
            self.stats['total_theorems_generated'] += result.theorems_generated

            # Step 3-5: Process each candidate
            for candidate in candidates:
                try:
                    # Formalize
                    candidate = self.conjecture_formalizer.formalize(candidate)

                    # Assess decidability
                    assessment = self.decidability_checker.assess(candidate)

                    if assessment.decidability_class == DecidabilityClass.UNDECIDABLE:
                        self.stats['undecidable_detected'] += 1
                        continue

                    # Attempt proof with resource bounds
                    result.proofs_attempted += 1

                    self.search_tree_manager.initialize_search(candidate)
                    search_result = self.search_tree_manager.search(
                        num_simulations=search_budget,
                        timeout_ms=assessment.resource_bounds.get('timeout_seconds', 60) * 1000 if assessment.resource_bounds else 60000,
                        max_expansions=assessment.resource_bounds.get('max_expansions', 10000) if assessment.resource_bounds else 10000
                    )

                    if search_result.success:
                        result.proofs_succeeded += 1
                        self.stats['total_proofs_found'] += 1

                        # Integrate discovery
                        discovery = self.auto_formalization_pipeline.formalize_theorem(
                            candidate,
                            search_result.proof_steps
                        )
                        self.vector_database_updater.update(discovery)
                        result.discoveries_integrated += 1
                        self.stats['discoveries_integrated'] += 1

                except (ValueError, TypeError, KeyError) as e:
                    # Mathematical/search failure - expected, log at debug level
                    logger.debug(f"Search failure for candidate: {e}")
                    result.errors.append(f"search_failure: {e}")
                except (RuntimeError, AttributeError, ImportError) as e:
                    # System error - unexpected, log at warning level
                    logger.warning(f"System error processing candidate: {e}", exc_info=True)
                    result.errors.append(f"system_error: {e}")

        except (ValueError, TypeError) as e:
            # Data/generation errors
            logger.warning(f"Generation error in discovery cycle: {e}")
            result.errors.append(f"generation_error: {e}")
        except (RuntimeError, AttributeError, ImportError) as e:
            # System-level cycle error
            logger.error(f"System error in discovery cycle: {e}", exc_info=True)
            result.errors.append(f"cycle_system_error: {e}")

        result.time_elapsed_ms = (time.time() - start_time) * 1000
        return result

    def run_algorithm_discovery(
        self,
        problem_spec: ProblemSpecification,
        generations: int = 10,
        population_size: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Run FunSearch-style algorithm discovery.

        Args:
            problem_spec: Problem specification
            generations: Number of evolutionary generations
            population_size: Population size

        Returns:
            DistilledHeuristic dictionary if successful, None otherwise
        """
        if self._status != SystemStatus.RUNNING:
            raise RuntimeError("System not running. Call start() first.")

        # Configure components for this problem
        self.code_evolutionary_proposer.set_problem(problem_spec)
        self.sandbox_evaluator.set_problem(problem_spec)

        # Initialize population
        population = self.code_evolutionary_proposer.generate_initial_population(problem_spec, size=population_size)

        best_candidate = None
        best_fitness = 0.0

        for gen in range(generations):
            # Evaluate population
            for candidate in population:
                result = self.sandbox_evaluator.evaluate(candidate.code, problem_spec)
                if isinstance(result, dict) and 'fitness' in result:
                    candidate.fitness_score = result['fitness']

                if candidate.fitness_score > best_fitness:
                    best_fitness = candidate.fitness_score
                    best_candidate = candidate

            # Early termination
            if best_fitness >= 0.99:
                break

            # Evolve
            population = self.code_evolutionary_proposer.evolve(population)

        if best_candidate and best_fitness > 0.5:
            # Distill and integrate
            heuristic = self.heuristic_distiller.distill(best_candidate)

            discovery = self.auto_formalization_pipeline.formalize_algorithm(heuristic)
            self.vector_database_updater.update(discovery)

            self.stats['algorithms_discovered'] += 1
            self.stats['discoveries_integrated'] += 1

            return {
                'best_fitness': best_fitness,
                'generations_run': generations,
                'heuristic': heuristic.to_dict() if hasattr(heuristic, 'to_dict') else heuristic
            }

        return {'best_fitness': best_fitness, 'generations_run': generations, 'heuristic': None}

    def request_human_guidance(
        self,
        problem: CandidateConjecture,
        search_state: Dict[str, Any]
    ) -> ProofStateSummary:
        """
        Request human guidance for a stuck proof.

        Args:
            problem: The problem we're stuck on
            search_state: Current search state

        Returns:
            ProofStateSummary for the human
        """
        self.stats['human_guidance_requested'] += 1
        request = self.interactive_guidance_liaison.request_guidance(problem, search_state)
        return request.summary

    def provide_guidance(self, request_id: str, guidance: str) -> bool:
        """
        Provide guidance for a pending request.

        Args:
            request_id: ID of the guidance request
            guidance: Human's guidance

        Returns:
            True if guidance was accepted
        """
        return self.interactive_guidance_liaison.receive_guidance(request_id, guidance)

    def search_knowledge(
        self,
        query: str,
        top_k: int = 5
    ) -> List[FormalizedDiscovery]:
        """
        Search the knowledge base for relevant discoveries.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of relevant discoveries
        """
        results = self.vector_database_updater.search(query, top_k=top_k)
        return [discovery for discovery, score in results]

    def health_check(self) -> Dict[str, bool]:
        """Check health of all components"""
        # Team health aggregations
        conjecture_gen_health = (
            self.synthetic_data_generator.health_check() and
            self.pattern_recognizer.health_check() and
            self.conjecture_formalizer.health_check()
        )
        deep_search_health = (
            self.policy_network.health_check() and
            self.critic_network.health_check() and
            self.search_tree_manager.health_check()
        )
        algo_discovery_health = (
            self.code_evolutionary_proposer.health_check() and
            self.sandbox_evaluator.health_check() and
            self.heuristic_distiller.health_check()
        )
        undecidability_health = (
            self.decidability_checker.health_check() and
            self.interactive_guidance_liaison.health_check()
        )
        knowledge_health = (
            self.auto_formalization_pipeline.health_check() and
            self.vector_database_updater.health_check()
        )

        return {
            'overall': self._status == SystemStatus.RUNNING,
            'conjecture_generation': conjecture_gen_health,
            'deep_search': deep_search_health,
            'algorithm_discovery': algo_discovery_health,
            'undecidability_navigator': undecidability_health,
            'formal_knowledge_integration': knowledge_health
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'system': {
                'status': self.status,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'cycle_count': self.cycle_count,
                **self.stats
            },
            # Team 1: Conjecture Generation - individual agent stats
            'synthetic_data_generator': self.synthetic_data_generator.get_statistics(),
            'pattern_recognizer': self.pattern_recognizer.get_statistics(),
            'conjecture_formalizer': self.conjecture_formalizer.get_statistics(),
            # Team 2: Deep Search - individual agent stats
            'policy_network': self.policy_network.get_statistics(),
            'critic_network': self.critic_network.get_statistics(),
            'search_tree_manager': self.search_tree_manager.get_statistics(),
            # Team 3: Algorithm Discovery - individual agent stats
            'code_evolutionary_proposer': self.code_evolutionary_proposer.get_statistics(),
            'sandbox_evaluator': self.sandbox_evaluator.get_statistics(),
            'heuristic_distiller': self.heuristic_distiller.get_statistics(),
            # Team 4: Undecidability Navigator - individual agent stats
            'decidability_checker': self.decidability_checker.get_statistics(),
            'interactive_guidance_liaison': self.interactive_guidance_liaison.get_statistics(),
            # Team 5: Knowledge Integration - individual agent stats
            'auto_formalization_pipeline': self.auto_formalization_pipeline.get_statistics(),
            'vector_database_updater': self.vector_database_updater.get_statistics()
        }

    def get_pending_guidance_requests(self) -> List[ProofStateSummary]:
        """Get all pending human guidance requests"""
        requests = self.interactive_guidance_liaison.get_pending_requests()
        return [r.summary for r in requests]


def demo():
    """Demonstrate Phase 6 Discovery Engine"""
    print("=" * 70)
    print("PHASE 6: THE MATHEMATICAL DISCOVERY ENGINE")
    print("=" * 70)

    # Initialize and start
    system = Phase6System()
    system.start()
    print("\nSystem started successfully.")

    # Run discovery cycle
    print("\n[Running Discovery Cycle]")
    result = system.run_discovery_cycle(num_theorems=50, search_budget=100, max_candidates=5)

    print(f"\nCycle Results:")
    print(f"  Theorems generated: {result.theorems_generated}")
    print(f"  Candidates filtered: {result.conjectures_filtered}")
    print(f"  Proofs attempted: {result.proofs_attempted}")
    print(f"  Proofs succeeded: {result.proofs_succeeded}")
    print(f"  Discoveries integrated: {result.discoveries_integrated}")
    print(f"  Time: {result.time_elapsed_ms:.0f}ms")

    # Print statistics
    print("\n[System Statistics]")
    stats = system.get_statistics()
    print(f"  Discovery cycles: {stats['system']['discovery_cycles']}")
    print(f"  Total proofs found: {stats['system']['total_proofs_found']}")
    print(f"  Discoveries integrated: {stats['system']['discoveries_integrated']}")

    # Health check
    print("\n[Health Check]")
    health = system.health_check()
    for component, healthy in health.items():
        status = "[PASS]" if healthy else "[FAIL]"
        print(f"  {status} {component}")

    # Shutdown
    system.shutdown()
    print("\nSystem shutdown complete.")
    print("=" * 70)


if __name__ == "__main__":
    demo()
