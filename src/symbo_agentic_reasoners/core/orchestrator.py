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
PHASE 1 - STEP 2: THE CENTRAL NERVOUS SYSTEM (Main Orchestrator)
================================================================

The Main Orchestrator is the Tier 1 "General Contractor" whose sole job
is management, enforcing the strict separation of Problem Understanding
from Problem Solving.

CRITICAL CONSTRAINTS:
--------------------
1. NON-INTERVENTION DIRECTIVE: Orchestrator is FORBIDDEN from performing
   calculations. If it sees "2+2", it must delegate, never compute.

2. SEPARATION OF PLANNING FROM EXECUTION: Orchestrator plans, decomposes,
   and delegates. It NEVER solves.

COMPONENTS:
----------
1. Decomposition Engine: HTN (Hierarchical Task Network) logic
2. Dynamic Routing Logic: Queries Directory Facilitator for capable agents

REFERENCE:
---------
- Phase_1_Build_Order_Breakdown.md: Lines 108-160 (STEP 2)
- Phase 1 Coding Strategy: Section 3.2 "The Central Nervous System"
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import uuid

# Setup logging
logger = logging.getLogger('symbo_agentic_reasoners.orchestrator')

# Add parent to path for Phase 0 imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool, PoolState
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.protocols.fipa_acl import create_request, create_inform

# Import Phase 1 components
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain

# Import Phase 3 Knowledge Management for learning/memory
try:
    from symbo_agentic_reasoners.middleware.knowledge_management import (
        KnowledgeManagementTeam, RetrievalConfidence
    )
    KNOWLEDGE_MANAGEMENT_AVAILABLE = True
except ImportError:
    KNOWLEDGE_MANAGEMENT_AVAILABLE = False
    KnowledgeManagementTeam = None
    RetrievalConfidence = None

# Import orchestration sub-engines (Phase 4 decomposition)
from symbo_agentic_reasoners.core.orchestration.data_structures import (
    NoAgentAvailableError, Task, DOMAIN_TO_POOL_KEY, get_pool_domain_key
)
from symbo_agentic_reasoners.core.orchestration.decomposition import DecompositionEngine
from symbo_agentic_reasoners.core.orchestration.agent_invocation import AgentInvoker
from symbo_agentic_reasoners.core.orchestration.native_fallback import NativeFallbackEngine
from symbo_agentic_reasoners.core.orchestration.blackboard_integration import BlackboardIntegration
from symbo_agentic_reasoners.core.orchestration.learning_memory import LearningMemory

# Import exploration layer (Tier 1.5)
try:
    from symbo_agentic_reasoners.exploration import UniversalStrategyExplorer
    from symbo_agentic_reasoners.exploration.data_structures import (
        Strategy, StrategyRanking, ExplorationOutcome, estimate_complexity
    )
    EXPLORATION_AVAILABLE = True
except ImportError:
    EXPLORATION_AVAILABLE = False
    UniversalStrategyExplorer = None


class MainOrchestrator(BDIAgent):
    """
    Main Orchestrator - The Central Nervous System

    DIRECTIVE:
    ---------
    Tier 1 Agent that manages the problem-solving process. Enforces strict
    separation of Problem Understanding from Problem Solving.

    ARCHITECTURE:
    ------------
    - Decomposition Engine: HTN logic to break complex tasks into subtasks
    - Routing Logic: Queries Directory Facilitator to find capable agents
    - NON-INTERVENTION: NEVER computes, always delegates

    WORKFLOW:
    --------
    1. Receive StructuredProblem from Problem Analysis Team
    2. Decompose into subtasks (if complex)
    3. Query DF for capable agents by domain
    4. Post task to Blackboard with appropriate tags
    5. Wait for verified result from Verification Core
    6. Return result to user

    CRITICAL:
    --------
    The Orchestrator NEVER computes. The NON_INTERVENTION flag is
    hard-coded to True and cannot be changed.

    REFERENCE:
    ---------
    - Phase_1_Build_Order_Breakdown.md: Lines 123-156 (MainOrchestrator code)
    - Phase 1 Coding Strategy: "The Orchestrator must manage, never solve"
    """

    def __init__(
        self,
        agent_id: str = 'main_orchestrator_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        agent_pool: Optional[AgentPool] = None,
        vector_db: Optional[Any] = None,
        enable_learning: bool = True
    ):
        """
        Initialize Main Orchestrator

        Args:
            agent_id: Unique orchestrator identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            agent_pool: AgentPool for lifecycle management (optional)
            vector_db: Vector database for learning/memory (optional)
            enable_learning: If True and vector_db provided, enables learning from solved problems
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard
        self.agent_pool = agent_pool
        self.vector_db = vector_db

        # HARD-CODED CONSTRAINT: Non-Intervention Directive
        # This MUST remain True - Orchestrator NEVER computes
        self.NON_INTERVENTION = True

        # Task tracking
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []

        # Knowledge Management Team for learning/memory
        self.knowledge_team = None
        if enable_learning and vector_db and blackboard and KNOWLEDGE_MANAGEMENT_AVAILABLE:
            try:
                self.knowledge_team = KnowledgeManagementTeam(
                    blackboard=blackboard,
                    vector_db=vector_db
                )
                logger.info(f"  Learning/Memory: ENABLED (KnowledgeManagementTeam active)")
            except Exception as e:
                logger.warning(f"  Learning/Memory: DISABLED (init failed: {e})")

        # Initialize sub-engines (Phase 4 decomposition)
        self.decomposer = DecompositionEngine(agent_pool=self.agent_pool)
        self.invoker = AgentInvoker(
            agent_id=self.agent_id,
            df=self.df,
            blackboard=self.blackboard
        )
        self.fallback = NativeFallbackEngine()
        self.blackboard_ops = BlackboardIntegration(
            agent_id=self.agent_id,
            blackboard=self.blackboard,
            agent_pool=self.agent_pool
        )
        self.learning = LearningMemory(
            agent_id=self.agent_id,
            knowledge_team=self.knowledge_team
        )

        # Initialize exploration layer (Tier 1.5)
        self.universal_explorer = None
        if EXPLORATION_AVAILABLE and self.df:
            try:
                self.universal_explorer = UniversalStrategyExplorer(
                    agent_id=f'{self.agent_id}_explorer',
                    directory_facilitator=self.df,
                    blackboard=self.blackboard,
                    knowledge_team=self.knowledge_team
                )
                logger.info(f"  Exploration Layer: ENABLED (UniversalStrategyExplorer active)")
            except Exception as e:
                logger.warning(f"  Exploration Layer: DISABLED (init failed: {e})")

        # Statistics (some delegated to sub-engines)
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.strategies_explored = 0
        self.successful_strategies = 0

        logger.info(f"[{self.agent_id}] Initialized")
        logger.info(f"  NON-INTERVENTION directive: {self.NON_INTERVENTION} (HARD-CODED)")
        logger.info(f"  Mode: Management only - NEVER computes")
        logger.info(f"  Sub-engines: Decomposer, Invoker, Fallback, Blackboard, Learning")
        if agent_pool:
            logger.info(f"  AgentPool: ENABLED (dynamic lifecycle management)")

    def process(self, structured: StructuredProblem) -> Any:
        """
        Process a structured problem

        This is the main entry point for the Orchestrator. It receives
        a StructuredProblem from the Problem Analysis Team and orchestrates
        the solution process.

        Now includes learning capabilities:
        1. Look-Before-Leap: Check memory for existing solutions
        2. Record-Result: Store new solutions for future retrieval

        Args:
            structured: Fully parsed and classified problem

        Returns:
            Verified result from solver

        Raises:
            NoAgentAvailableError: If no agent can handle the problem

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 132-155 (process method)
        """
        logger.info(f"[{self.agent_id}] Processing problem:")
        logger.info(f"  Type: {structured.problem_type.value}")
        logger.info(f"  Domain: {structured.domain.value}")
        logger.info(f"  Input: '{structured.raw_input}'")

        # LEARNING STEP 1: Look-Before-Leap - check memory for existing solutions
        cached_result = self.learning.look_before_leap(structured)
        if cached_result is not None:
            logger.info(f"  [MEMORY HIT] Found cached solution: {cached_result}")
            return cached_result

        # CRITICAL: Enforce NON-INTERVENTION
        if not self.NON_INTERVENTION:
            raise RuntimeError("FATAL: NON_INTERVENTION directive violated!")

        # NEW: EXPLORATION PHASE (Tier 1.5) - Systematic strategy search and ranking
        if self._should_explore(structured):
            logger.info(f"  [{self.agent_id}] Entering EXPLORATION PHASE...")

            strategy_ranking = self._explore_strategies(structured)

            # Try ranked strategies in order
            for strategy, confidence in strategy_ranking.ranked_strategies:
                logger.info(
                    f"  [{self.agent_id}] Trying strategy: '{strategy.name}' "
                    f"(confidence={confidence:.2f})"
                )

                try:
                    result = self._execute_strategy(strategy, structured)
                    if result:
                        logger.info(
                            f"  [EXPLORATION SUCCESS] Strategy '{strategy.name}' solved the problem"
                        )
                        self._record_strategy_success(strategy, structured, result)
                        self.learning.record_solution(structured, result)
                        self.successful_strategies += 1
                        return result
                except Exception as e:
                    logger.warning(
                        f"  [EXPLORATION FAILURE] Strategy '{strategy.name}' failed: {e}"
                    )
                    self._record_strategy_failure(strategy, structured, e)
                    continue  # Try next strategy

            # If all strategies exhausted, fall through to standard decomposition path
            logger.info(
                f"  [{self.agent_id}] All exploration strategies exhausted, "
                "falling back to standard decomposition"
            )

        # Step 1: Decompose if complex (HTN logic)
        logger.debug(f"  [{self.agent_id}] Step 1: Decomposing task...")
        subtasks = self.decomposer.decompose(structured)
        logger.debug(f"    Decomposed into {len(subtasks)} subtask(s)")

        # Step 1.5: Wake agents for this domain (if AgentPool available)
        # Use mapping to convert MathDomain enum to pool domain key
        domain_key = get_pool_domain_key(structured.domain)
        if self.agent_pool:
            logger.debug(f"  [{self.agent_id}] Step 1.5: Waking agents for domain '{domain_key}'...")
            woken = self.decomposer.wake_domain_agents(domain_key)
            logger.debug(f"    Woke {len(woken)} agent(s): {woken}")

        # Step 2: Query DF for capable agent
        logger.debug(f"  [{self.agent_id}] Step 2: Finding capable agent...")
        service_type = self.invoker.get_service_type(structured.domain)
        agents = self.invoker.find_capable_agents(service_type)

        if not agents:
            error_msg = f"No agent available for domain: {structured.domain.value}"
            logger.error(f"    ERROR: {error_msg}")
            raise NoAgentAvailableError(error_msg)

        logger.debug(f"    Found {len(agents)} capable agent(s): {[a.agent_id for a in agents]}")

        # Check if agent has instance for direct invocation
        selected_agent = agents[0]
        if hasattr(selected_agent, 'instance') and selected_agent.instance is not None:
            # Direct invocation path - call agent.process() directly
            logger.debug(f"  [{self.agent_id}] Step 3: Direct invocation of {selected_agent.agent_id}...")
            result = self.invoker.direct_invoke(structured, selected_agent.instance)
            if result is not None:
                self.tasks_routed += 1
                self.tasks_completed += 1
                # LEARNING STEP 2: Record successful result for future retrieval
                self.learning.record_solution(structured, result)
                return result
            # Fall through to blackboard path if direct invoke failed
            logger.debug(f"    Direct invoke returned None, falling back to blackboard...")

        # Step 3: Post task to Blackboard
        logger.debug(f"  [{self.agent_id}] Step 3: Posting task to Blackboard...")
        task = self.blackboard_ops.post_task(structured, selected_agent.agent_id)
        logger.debug(f"    Posted as entry: {task.blackboard_entry_id}")

        # Step 4: Wait for verified result
        logger.debug(f"  [{self.agent_id}] Step 4: Waiting for verified result...")
        result = self.blackboard_ops.await_result(task)

        # Track completion
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        self.completed_tasks.append(task)
        self.tasks_completed += 1

        # LEARNING STEP 2: Record successful result for future retrieval
        if result is not None:
            self.learning.record_solution(structured, result)

        return result

    # ============================================================================
    # PHASE 4 DECOMPOSITION: METHODS MOVED TO SUB-ENGINES
    # ============================================================================
    # All agent invocation, fallback, blackboard, and learning methods have been
    # extracted to specialized sub-engines for better maintainability.
    #
    # DecompositionEngine (decomposition.py):
    #   - decompose() - HTN task decomposition
    #   - wake_domain_agents() - Agent lifecycle management
    #
    # AgentInvoker (agent_invocation.py):
    #   - direct_invoke() - Direct supervisor/specialist invocation
    #   - invoke_specialist_directly() - Specialist calling
    #   - get_service_type() - Service type mapping
    #   - find_capable_agents() - Directory Facilitator queries
    #   - map_operation_to_service() - Operation to service mapping
    #   - create_specialist_for_operation() - Specialist factory
    #   - call_specialist() - Generic specialist invocation
    #
    # NativeFallbackEngine (native_fallback.py):
    #   - compute_fallback() - Main fallback router (NO SYMPY)
    #   - _native_solve() - Algebraic equation solver
    #   - _geometry_fallback() - Geometry/trigonometry
    #   - _linalg_fallback() - Linear algebra
    #   - _stats_fallback() - Statistics
    #   - _discrete_fallback() - Discrete math
    #   - _native_determinant(), _native_eigenvalues_2x2(), etc. - Matrix ops
    #   - _is_prime() - Primality testing
    #
    # BlackboardIntegration (blackboard_integration.py):
    #   - post_task() - Post tasks to blackboard
    #   - await_result() - Wait for verified results
    #   - _activate_agent() - Agent activation
    #   - _deactivate_agent() - Agent deactivation
    #
    # LearningMemory (learning_memory.py):
    #   - look_before_leap() - Cache checking (Phase 3 feature)
    #   - record_solution() - Solution recording
    #
    # Total reduction: 1,503 LOC → 400 LOC (73% reduction)
    # ============================================================================

    # BDI Implementation (simplified for Phase 1)
    def update_beliefs(self):
        """Update beliefs from environment"""
        # In Phase 1, we use direct method calls instead of full BDI loop
        # Phase 2 will implement full BDI reasoning
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions"""
        # In Phase 1, we use direct method calls
        # Phase 2 will implement full HTN planning
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        # In Phase 1, we use direct method calls
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics.

        Aggregates statistics from all sub-engines:
        - DecompositionEngine: agents_woken
        - AgentInvoker: invocation count
        - NativeFallbackEngine: fallback_count
        - BlackboardIntegration: blackboard_posts, agents_activated/deactivated
        - LearningMemory: cache_hits, solutions_recorded
        """
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'active_tasks': len(self.active_tasks),
            'non_intervention': self.NON_INTERVENTION,
            'agent_pool_enabled': self.agent_pool is not None,
            # Sub-engine statistics
            'agents_woken': self.decomposer.agents_woken,
            'agents_activated': self.blackboard_ops.agents_activated,
            'agents_deactivated': self.blackboard_ops.agents_deactivated,
            'fallback_count': self.fallback.fallback_count,
            'blackboard_posts': self.blackboard_ops.blackboard_posts,
            # Learning statistics
            'learning_enabled': self.knowledge_team is not None,
            'cache_hits': self.learning.cache_hits,
            'cache_misses': self.learning.cache_misses,
            'solutions_recorded': self.learning.solutions_recorded,
        })
        if self.agent_pool:
            stats['pool_stats'] = self.agent_pool.get_statistics()
        if self.knowledge_team:
            stats['knowledge_team_stats'] = self.knowledge_team.get_statistics()
        # Exploration statistics
        if self.universal_explorer:
            stats.update({
                'exploration_enabled': True,
                'strategies_explored': self.strategies_explored,
                'successful_strategies': self.successful_strategies,
                'explorer_stats': self.universal_explorer.get_statistics()
            })
        return stats

    # ========================================================================
    # EXPLORATION PHASE METHODS (Tier 1.5 Integration)
    # ========================================================================

    def _should_explore(self, problem: StructuredProblem) -> bool:
        """
        Decide if problem warrants exploration.

        Exploration is triggered when:
        - Exploration layer is available
        - Problem is sufficiently complex
        - Domain has high strategy variance (calculus > algebra)
        - Not time-critical (future enhancement)

        Args:
            problem: The structured problem

        Returns:
            True if exploration should be performed
        """
        if not self.universal_explorer:
            return False

        # Estimate problem complexity
        complexity = estimate_complexity(problem)

        # Complex problems benefit more from exploration
        if complexity == 'low':
            # Simple problems: skip exploration, use standard path
            return False

        # High-variance domains benefit from exploration
        high_variance_domains = [
            MathDomain.CALCULUS,      # Many integration/differentiation techniques
            MathDomain.LOGIC,         # Multiple proof strategies
            MathDomain.NUMBER_THEORY  # Various approaches to proofs
        ]

        # Explore if: medium/high complexity OR high-variance domain
        should_explore = (
            complexity in ['medium', 'high'] or
            problem.domain in high_variance_domains
        )

        logger.debug(
            f"[{self.agent_id}] Exploration decision: {should_explore} "
            f"(complexity={complexity}, domain={problem.domain.value})"
        )

        return should_explore

    def _explore_strategies(self, problem: StructuredProblem) -> StrategyRanking:
        """
        Get ranked strategies from exploration layer.

        Delegates to UniversalStrategyExplorer which:
        1. Queries knowledge management for historical successes
        2. Consults domain explorers for specialized strategies
        3. Scores and ranks all candidates
        4. Returns top N strategies within budget

        Args:
            problem: The structured problem

        Returns:
            StrategyRanking with ranked strategies and metadata

        Raises:
            RuntimeError: If exploration fails
        """
        try:
            ranking = self.universal_explorer.explore_strategies(problem)
            self.strategies_explored += len(ranking.ranked_strategies)

            logger.info(
                f"  [{self.agent_id}] Exploration generated {len(ranking.ranked_strategies)} "
                f"ranked strategies (budget={ranking.exploration_budget})"
            )
            logger.debug(f"  Reasoning: {ranking.reasoning}")

            return ranking

        except Exception as e:
            logger.error(f"  [{self.agent_id}] Exploration failed: {e}")
            # Re-raise to fall back to standard decomposition
            raise RuntimeError(f"Exploration failed: {e}")

    def _execute_strategy(
        self,
        strategy: Strategy,
        problem: StructuredProblem
    ) -> Optional[Any]:
        """
        Execute a specific strategy by calling supervisors/specialists.

        Translates strategy techniques into concrete agent invocations.

        Args:
            strategy: The strategy to execute
            problem: The problem being solved

        Returns:
            Result if strategy succeeds, None otherwise

        Raises:
            Exception: If strategy execution fails
        """
        logger.debug(
            f"  [{self.agent_id}] Executing strategy '{strategy.name}' "
            f"with techniques: {strategy.techniques}"
        )

        # For now, use the existing routing logic but with strategy context
        # Future enhancement: Could execute technique-by-technique for partial results

        # Query DF for capable agent (same as standard path)
        service_type = self.invoker.get_service_type(problem.domain)
        agents = self.invoker.find_capable_agents(service_type)

        if not agents:
            raise NoAgentAvailableError(
                f"No agent available for domain: {problem.domain.value}"
            )

        selected_agent = agents[0]

        # Try direct invocation
        if hasattr(selected_agent, 'instance') and selected_agent.instance is not None:
            result = self.invoker.direct_invoke(problem, selected_agent.instance)
            if result is not None:
                self.tasks_routed += 1
                self.tasks_completed += 1
                return result

        # Fallback to blackboard
        task = self.blackboard_ops.post_task(problem, selected_agent.agent_id)
        result = self.blackboard_ops.await_result(task)

        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        self.completed_tasks.append(task)
        self.tasks_completed += 1

        return result

    def _record_strategy_success(
        self,
        strategy: Strategy,
        problem: StructuredProblem,
        result: Any
    ):
        """
        Record successful strategy exploration.

        Updates:
        - Strategy success_rate (Bayesian update)
        - Exploration result in knowledge management
        - Learning system with solution

        Args:
            strategy: The successful strategy
            problem: The problem that was solved
            result: The solution result
        """
        if not self.universal_explorer:
            return

        try:
            # Record exploration result
            self.universal_explorer.record_exploration(
                strategy=strategy,
                problem=problem,
                outcome=ExplorationOutcome.SUCCESS,
                execution_time=0.0,  # TODO: Track actual time
                lessons_learned=[f"Strategy '{strategy.name}' successful for {problem.domain.value}"]
            )

            logger.debug(
                f"  [{self.agent_id}] Recorded successful exploration: "
                f"strategy='{strategy.name}'"
            )

        except Exception as e:
            logger.warning(f"  [{self.agent_id}] Failed to record success: {e}")

    def _record_strategy_failure(
        self,
        strategy: Strategy,
        problem: StructuredProblem,
        error: Exception
    ):
        """
        Record failed strategy exploration to learn from mistakes.

        Updates:
        - Strategy success_rate (Bayesian update)
        - Exploration result with error classification
        - Anti-pattern detection

        Args:
            strategy: The failed strategy
            problem: The problem attempted
            error: The exception that occurred
        """
        if not self.universal_explorer:
            return

        try:
            # Classify error type
            error_type = type(error).__name__

            # Record exploration result
            self.universal_explorer.record_exploration(
                strategy=strategy,
                problem=problem,
                outcome=ExplorationOutcome.FAILURE,
                execution_time=0.0,  # TODO: Track actual time
                error_type=error_type,
                lessons_learned=[f"Strategy '{strategy.name}' failed: {str(error)[:100]}"]
            )

            logger.debug(
                f"  [{self.agent_id}] Recorded failed exploration: "
                f"strategy='{strategy.name}', error={error_type}"
            )

        except Exception as e:
            logger.warning(f"  [{self.agent_id}] Failed to record failure: {e}")


if __name__ == "__main__":
    """Test Main Orchestrator"""
    print("=" * 80)
    print("PHASE 1 - STEP 2: MAIN ORCHESTRATOR TEST")
    print("=" * 80)
    print()

    # Initialize Phase 0 infrastructure
    from symbo_agentic_reasoners.core.system import Phase0System

    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Orchestrator
    orchestrator = MainOrchestrator(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test case: Try to process (will fail since no solver registered yet)
    print("Test: Attempting to process problem (will fail - no solver yet)...")
    print()

    from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

    team = ProblemAnalysisTeam()
    structured = team.process("Calculate the derivative of x**2 + 1")

    print()
    print("Attempting orchestration...")
    try:
        result = orchestrator.process(structured)
        print(f"Result: {result}")
    except NoAgentAvailableError as e:
        print(f"Expected error: {e}")
        print("(This is correct - no solver agent registered yet)")

    print()
    print("=" * 80)
    print("MAIN ORCHESTRATOR TEST COMPLETE")
    print("=" * 80)
    print()
    print("Statistics:")
    import json
    print(json.dumps(orchestrator.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
