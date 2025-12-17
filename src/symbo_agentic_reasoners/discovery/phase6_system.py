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
Phase 6 System: The Mathematical Discovery Engine (Simplified)
"""
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.discovery.phase6_system')

class SystemStatus(Enum):
    STOPPED = 'stopped'
    STARTING = 'starting'
    RUNNING = 'running'
    PAUSED = 'paused'
    ERROR = 'error'

# Import from discovery submodules
from symbo_agentic_reasoners.discovery.conjecture import (
    SyntheticDataGenerator, PatternRecognizer, ConjectureFormalizer,
    CandidateConjecture, ConjectureStatus
)
from symbo_agentic_reasoners.discovery.deep_search import (
    PolicyNetwork, CriticNetwork, SearchTreeManager, SymPyProver,
    ProofState, SearchResult, ProverEngine
)
from symbo_agentic_reasoners.discovery.algorithm import (
    CodeEvolutionaryProposer, SandboxEvaluator, HeuristicDistiller,
    ProblemSpecification, CodeCandidate
)
from symbo_agentic_reasoners.discovery.undecidability import (
    DecidabilityChecker, DecidabilityClass, InteractiveGuidanceLiaison, ProofStateSummary
)
from symbo_agentic_reasoners.discovery.formal import (
    AutoFormalizationPipeline, VectorDatabaseUpdater, FormalizedDiscovery
)


@dataclass
class DiscoveryCycleResult:
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
    """Phase 6: The Mathematical Discovery Engine"""

    def __init__(
        self,
        phase5_system=None,
        verification_core=None,
        knowledge_base=None,
        guidance_callback: Callable = None,
        synthetic_data_generator: Optional[SyntheticDataGenerator] = None,
        pattern_recognizer: Optional[PatternRecognizer] = None,
        conjecture_formalizer: Optional[ConjectureFormalizer] = None,
        policy_network: Optional[PolicyNetwork] = None,
        critic_network: Optional[CriticNetwork] = None,
        prover_engine: Optional[Any] = None,
        search_tree_manager: Optional[SearchTreeManager] = None,
        code_evolutionary_proposer: Optional[CodeEvolutionaryProposer] = None,
        sandbox_evaluator: Optional[SandboxEvaluator] = None,
        heuristic_distiller: Optional[HeuristicDistiller] = None,
        decidability_checker: Optional[DecidabilityChecker] = None,
        interactive_guidance_liaison: Optional[InteractiveGuidanceLiaison] = None,
        auto_formalization_pipeline: Optional[AutoFormalizationPipeline] = None,
        vector_database_updater: Optional[VectorDatabaseUpdater] = None
    ):
        self.phase5 = phase5_system
        self.verification_core = verification_core
        self.knowledge_base = knowledge_base
        self._status = SystemStatus.STOPPED
        self.started_at: Optional[datetime] = None
        self.cycle_count = 0

        # Team 1: Conjecture Generation
        self.synthetic_data_generator = synthetic_data_generator or SyntheticDataGenerator()
        self.pattern_recognizer = pattern_recognizer or PatternRecognizer(knowledge_base=knowledge_base)
        self.conjecture_formalizer = conjecture_formalizer or ConjectureFormalizer()

        # Team 2: Deep Search
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

        # Team 3: Algorithm Discovery
        self.code_evolutionary_proposer = code_evolutionary_proposer or CodeEvolutionaryProposer()
        self.sandbox_evaluator = sandbox_evaluator or SandboxEvaluator()
        self.heuristic_distiller = heuristic_distiller or HeuristicDistiller()

        # Team 4: Undecidability Navigator
        self.decidability_checker = decidability_checker or DecidabilityChecker()
        self.interactive_guidance_liaison = interactive_guidance_liaison or InteractiveGuidanceLiaison(
            notification_callback=guidance_callback
        )

        # Team 5: Formal Knowledge Integration
        self.auto_formalization_pipeline = auto_formalization_pipeline or AutoFormalizationPipeline(
            verification_core=verification_core
        )
        self.vector_database_updater = vector_database_updater or VectorDatabaseUpdater()

        self.stats = {
            'discovery_cycles': 0,
            'total_theorems_generated': 0,
            'total_proofs_found': 0,
            'algorithms_discovered': 0,
            'discoveries_integrated': 0,
        }

    @property
    def status(self) -> str:
        return self._status.value

    def start(self):
        if self._status == SystemStatus.RUNNING:
            return
        self._status = SystemStatus.STARTING
        self.started_at = datetime.now()
        self._status = SystemStatus.RUNNING

    def shutdown(self):
        self._status = SystemStatus.STOPPED

    def health_check(self) -> Dict[str, bool]:
        # Call all component health checks including prover
        prover_health = self.prover_engine.health_check() if hasattr(self.prover_engine, 'health_check') else True
        return {
            'overall': self._status == SystemStatus.RUNNING,
            'conjecture_generation': self.synthetic_data_generator.health_check(),
            'deep_search': self.policy_network.health_check() and prover_health,
            'algorithm_discovery': self.code_evolutionary_proposer.health_check(),
            'undecidability_navigator': self.decidability_checker.health_check(),
            'formal_knowledge_integration': self.auto_formalization_pipeline.health_check()
        }

    def get_statistics(self) -> Dict[str, Any]:
        return {'system': {'status': self.status, **self.stats}}
