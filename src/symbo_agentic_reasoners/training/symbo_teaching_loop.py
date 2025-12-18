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
SYMBO TEACHING LOOP - Agent-Teaching-SYMBO Integration
======================================================

This module wires together the solving pipeline and the distillation pipeline
to create a continuous learning loop where:

1. Agents solve problems and produce verified results
2. Verified solutions are captured as thought traces
3. Thought traces feed the distillation pipeline
4. The Student model learns from the Teacher's success

This implements the Phase 5 "Evolutionary Flywheel" where the system
continuously improves by learning from its own verified solutions.

ARCHITECTURE:
------------

    User Problem
         │
         ▼
    ┌─────────────┐
    │ Solver      │──────────┐
    │ Engine      │          │
    └─────────────┘          │
         │                   │
         ▼                   ▼
    ┌─────────────┐   ┌────────────┐
    │ Verified    │   │ Thought    │
    │ Result      │──>│ Trace      │
    └─────────────┘   │ Harvester  │
                      └────────────┘
                            │
                            ▼
                      ┌────────────┐
                      │ Distillation│
                      │ Pipeline   │
                      └────────────┘
                            │
                            ▼
                      ┌────────────┐
                      │ Student    │
                      │ Model      │
                      └────────────┘

USAGE:
-----
    from symbo_agentic_reasoners.training.symbo_teaching_loop import (
        SymboTeachingLoop, get_teaching_loop
    )

    # Get or create the global teaching loop
    loop = get_teaching_loop(solver_engine)

    # Solve a problem - automatically harvests trace if verified
    result = loop.solve_and_learn("integrate(x**2, x)")

    # Check learning statistics
    stats = loop.get_statistics()

    # Trigger distillation when ready
    loop.run_distillation()

REFERENCE:
---------
- Phase_5_Build_Order_Breakdown.md: Sections 2-3
- harvester.py: ThoughtTraceHarvester class
- distillation_pipeline.py: DistillationPipeline class
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger('symbo_agentic_reasoners.training.teaching_loop')


@dataclass
class LearningStatistics:
    """Statistics for the teaching loop"""
    problems_solved: int = 0
    solutions_verified: int = 0
    solutions_rejected: int = 0
    traces_harvested: int = 0
    distillation_runs: int = 0
    total_latency_ms: float = 0.0
    learning_events: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.learning_events is None:
            self.learning_events = []

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'problems_solved': self.problems_solved,
            'solutions_verified': self.solutions_verified,
            'solutions_rejected': self.solutions_rejected,
            'verification_rate': (
                self.solutions_verified / max(self.problems_solved, 1) * 100
            ),
            'traces_harvested': self.traces_harvested,
            'distillation_runs': self.distillation_runs,
            'avg_latency_ms': (
                self.total_latency_ms / max(self.problems_solved, 1)
            ),
            'recent_learning_events': self.learning_events[-10:]
        }


class SymboTeachingLoop:
    """
    Integrates solver engine with distillation pipeline for continuous learning.

    This is the "Evolutionary Flywheel" from Phase 5 - a continuous improvement
    loop where verified solutions teach the Student model, which in turn reduces
    load on the full multi-agent system.

    FLYWHEEL STAGES:
    ---------------
    1. User submits problem
    2. Solver engine (Teacher) produces verified solution
    3. Solution captured as ThoughtTrace with reasoning chain
    4. ThoughtTrace added to Gold Standard corpus
    5. Periodically, DistillationPipeline trains Student on corpus
    6. Student handles routine problems, escalates hard ones to Teacher
    7. Escalated cases become high-priority training data
    8. Loop continues, Student improves over time
    """

    def __init__(
        self,
        solver_engine=None,
        harvester=None,
        distillation_pipeline=None,
        storage_path: Optional[Path] = None,
        auto_distill_threshold: int = 50,
        enable_auto_learning: bool = True
    ):
        """
        Initialize the SYMBO Teaching Loop.

        Args:
            solver_engine: SolverEngine instance (Teacher)
            harvester: ThoughtTraceHarvester instance
            distillation_pipeline: DistillationPipeline instance
            storage_path: Path for storing learning artifacts
            auto_distill_threshold: Run distillation after this many verified traces
            enable_auto_learning: If True, automatically harvest traces on solve
        """
        logger.info("Initializing SYMBO Teaching Loop")

        self.storage_path = storage_path or Path("data/teaching_loop")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Core components (lazy-loaded)
        self._solver = solver_engine
        self._harvester = harvester
        self._distillation = distillation_pipeline

        # Configuration
        self.auto_distill_threshold = auto_distill_threshold
        self.enable_auto_learning = enable_auto_learning

        # Statistics
        self.stats = LearningStatistics()

        # Track traces since last distillation
        self._traces_since_distillation = 0

        # Thread safety
        self._lock = threading.Lock()

        logger.info(f"Teaching loop initialized with auto_distill_threshold={auto_distill_threshold}")

    @property
    def solver(self):
        """Lazy-load solver engine"""
        if self._solver is None:
            try:
                from symbo_agentic_reasoners.core.solver_engine import get_solver_engine
                self._solver = get_solver_engine()
            except ImportError:
                logger.warning("Could not import solver_engine")
        return self._solver

    @property
    def harvester(self):
        """Lazy-load thought trace harvester"""
        if self._harvester is None:
            try:
                from symbo_agentic_reasoners.optimization.distillation.harvester import (
                    ThoughtTraceHarvester
                )
                self._harvester = ThoughtTraceHarvester(
                    storage_path=str(self.storage_path / "thought_traces")
                )
            except ImportError:
                logger.warning("Could not import ThoughtTraceHarvester")
        return self._harvester

    @property
    def distillation(self):
        """Lazy-load distillation pipeline"""
        if self._distillation is None:
            try:
                # Check if distillation_pipeline exists in expected locations
                try:
                    from symbo_agentic_reasoners.optimization.distillation.distillation_pipeline import (
                        DistillationPipeline
                    )
                except ImportError:
                    # Fallback to archive location
                    from data.docs.MASTER_ARCHIVE.symbo_agentic_reasoners_phase5.distillation.distillation_pipeline import (
                        DistillationPipeline
                    )

                self._distillation = DistillationPipeline(
                    trace_harvester=self.harvester,
                    min_traces_for_training=self.auto_distill_threshold
                )
            except ImportError as e:
                logger.warning(f"Could not import DistillationPipeline: {e}")
        return self._distillation

    def solve_and_learn(
        self,
        problem: str,
        capture_trace: bool = None
    ) -> Tuple[Any, bool]:
        """
        Solve a problem and optionally capture it as a learning trace.

        This is the main entry point for the teaching loop. It:
        1. Solves the problem using the solver engine
        2. If successful and verified, captures a thought trace
        3. Checks if auto-distillation should be triggered

        Args:
            problem: Mathematical problem to solve
            capture_trace: Override auto_learning setting

        Returns:
            Tuple of (solve_result, trace_captured)
        """
        if capture_trace is None:
            capture_trace = self.enable_auto_learning

        if self.solver is None:
            logger.error("No solver engine available")
            return None, False

        # Start timing
        start_time = time.time()

        # Solve the problem
        try:
            result = self.solver.solve(problem)
            elapsed_ms = (time.time() - start_time) * 1000
        except Exception as e:
            logger.error(f"Solve failed: {e}")
            self.stats.problems_solved += 1
            return None, False

        with self._lock:
            self.stats.problems_solved += 1
            self.stats.total_latency_ms += elapsed_ms

        # Determine if solution was verified/successful
        is_verified = False
        try:
            status_name = result.status.name if hasattr(result.status, 'name') else str(result.status)
            is_verified = status_name in ('SUCCESS', 'PARTIAL', 'VERIFIED')
        except AttributeError:
            is_verified = result is not None

        trace_captured = False

        if is_verified:
            with self._lock:
                self.stats.solutions_verified += 1

            # Capture thought trace if enabled
            if capture_trace and self.harvester is not None:
                trace_captured = self._capture_trace(problem, result, elapsed_ms)
        else:
            with self._lock:
                self.stats.solutions_rejected += 1

        # Check for auto-distillation
        if self._should_auto_distill():
            self._trigger_auto_distillation()

        return result, trace_captured

    def _capture_trace(
        self,
        problem: str,
        result: Any,
        latency_ms: float
    ) -> bool:
        """
        Capture a thought trace from a verified solution.

        Args:
            problem: The original problem
            result: The solve result
            latency_ms: Solve latency

        Returns:
            True if trace was captured
        """
        try:
            from symbo_agentic_reasoners.optimization.distillation.harvester import (
                ThoughtTrace, VerificationStatus
            )

            # Determine query type from result metadata
            query_type = "computation"
            if hasattr(result, 'specialist_used') and result.specialist_used:
                specialist = result.specialist_used.lower()
                if 'proof' in specialist or 'theorem' in specialist:
                    query_type = "proof"
                elif 'optim' in specialist:
                    query_type = "optimization"
                elif 'symbol' in specialist:
                    query_type = "symbolic"

            # Build trace
            trace = ThoughtTrace(
                trace_id=f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.stats.traces_harvested}",
                timestamp=datetime.now(),
                original_query=problem,
                query_type=query_type,
                complexity_score=0.5,  # Will be computed by harvester
                orchestrator_decomposition=[problem],
                supervisor_strategy=result.specialist_used if hasattr(result, 'specialist_used') else "direct",
                specialist_agents_invoked=[result.specialist_used] if hasattr(result, 'specialist_used') and result.specialist_used else [],
                symbolic_expressions=[str(result.result)] if hasattr(result, 'result') else [],
                fitted_coefficients={},
                taylor_expansion_order=0,
                groebner_basis_used=False,
                verification_status=VerificationStatus.VERIFIED,
                formal_proof_lean4=None,
                debate_consensus_score=None,
                final_answer=str(result.result) if hasattr(result, 'result') else str(result),
                confidence_score=0.9,
                total_latency_ms=latency_ms,
                agents_activated=1,
                symbolic_ops_count=1
            )

            # Add to harvester
            added = self.harvester.add_trace(trace)

            if added:
                with self._lock:
                    self.stats.traces_harvested += 1
                    self._traces_since_distillation += 1
                    self.stats.learning_events.append({
                        'timestamp': datetime.now().isoformat(),
                        'event': 'trace_captured',
                        'problem': problem[:50],
                        'query_type': query_type
                    })

                logger.debug(f"Captured trace for: {problem[:50]}...")
                return True

        except Exception as e:
            logger.error(f"Failed to capture trace: {e}")

        return False

    def _should_auto_distill(self) -> bool:
        """Check if auto-distillation should be triggered"""
        return (
            self._traces_since_distillation >= self.auto_distill_threshold and
            self.distillation is not None
        )

    def _trigger_auto_distillation(self):
        """Trigger automatic distillation in background"""
        def distill():
            """Perform distill operation.

            Args:
            No arguments

            Returns:
            Result of the operation

            Example:
            >>> result = obj.distill(...)
            """
            try:
                result = self.run_distillation()
                logger.info(f"Auto-distillation completed: {result.get('status')}")
            except Exception as e:
                logger.error(f"Auto-distillation failed: {e}")

        thread = threading.Thread(target=distill, daemon=True, name="AutoDistillation")
        thread.start()

        # Reset counter
        with self._lock:
            self._traces_since_distillation = 0

    def run_distillation(self, prioritize_escalated: bool = True) -> Dict[str, Any]:
        """
        Run the distillation pipeline manually.

        This trains the Student model on the accumulated Gold Standard corpus.

        Args:
            prioritize_escalated: Weight escalated traces higher (3x)

        Returns:
            Distillation result metrics
        """
        if self.distillation is None:
            return {"status": "error", "message": "No distillation pipeline available"}

        try:
            result = self.distillation.run_distillation(prioritize_escalated)

            with self._lock:
                self.stats.distillation_runs += 1
                self.stats.learning_events.append({
                    'timestamp': datetime.now().isoformat(),
                    'event': 'distillation',
                    'status': result.get('status'),
                    'examples_trained': result.get('examples_trained', 0)
                })

            return result

        except Exception as e:
            logger.error(f"Distillation failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        """Get teaching loop statistics"""
        with self._lock:
            stats = self.stats.to_dict()

        # Add component statistics
        if self.harvester:
            stats['harvester'] = self.harvester.get_statistics()

        if self.distillation:
            stats['distillation'] = self.distillation.get_statistics()

        stats['traces_since_last_distillation'] = self._traces_since_distillation
        stats['auto_distill_threshold'] = self.auto_distill_threshold

        return stats

    def get_learning_corpus_size(self) -> int:
        """Get the current size of the Gold Standard corpus"""
        if self.harvester:
            return len(self.harvester.verified_traces)
        return 0

    def is_ready_for_distillation(self) -> Tuple[bool, str]:
        """Check if the system is ready for distillation"""
        if self.harvester is None:
            return False, "No harvester available"

        corpus_size = self.get_learning_corpus_size()
        if corpus_size < self.auto_distill_threshold:
            return False, f"Need {self.auto_distill_threshold - corpus_size} more verified traces"

        return True, f"Ready with {corpus_size} verified traces"


# Global teaching loop instance
_teaching_loop: Optional[SymboTeachingLoop] = None
_loop_lock = threading.Lock()


def get_teaching_loop(solver_engine=None) -> SymboTeachingLoop:
    """
    Get or create the global SymboTeachingLoop instance.

    Args:
        solver_engine: Optional solver engine to use

    Returns:
        The global SymboTeachingLoop instance
    """
    global _teaching_loop

    with _loop_lock:
        if _teaching_loop is None:
            _teaching_loop = SymboTeachingLoop(solver_engine=solver_engine)
        return _teaching_loop


def solve_and_learn(problem: str) -> Tuple[Any, bool]:
    """
    Convenience function to solve and learn from a problem.

    Args:
        problem: Mathematical problem to solve

    Returns:
        Tuple of (solve_result, trace_captured)
    """
    loop = get_teaching_loop()
    return loop.solve_and_learn(problem)


if __name__ == "__main__":
    """Demo of the teaching loop"""
    print("=" * 70)
    print("SYMBO TEACHING LOOP DEMO")
    print("=" * 70)
    print()

    # Create teaching loop
    loop = SymboTeachingLoop(
        auto_distill_threshold=5,  # Low threshold for demo
        enable_auto_learning=True
    )

    # Demo problems
    problems = [
        "diff(x**2 + 3*x, x)",
        "integrate(sin(x), x)",
        "solve(x**2 - 4 = 0, x)",
        "limit(sin(x)/x, x, 0)",
        "factor(x**2 - 1)"
    ]

    print("Solving problems and capturing learning traces...")
    print()

    for problem in problems:
        print(f"Problem: {problem}")
        result, captured = loop.solve_and_learn(problem)

        if result:
            answer = result.result if hasattr(result, 'result') else str(result)
            status = "CAPTURED" if captured else "NOT CAPTURED"
            print(f"  -> Result: {answer}")
            print(f"  -> Trace: {status}")
        else:
            print(f"  -> FAILED")
        print()

    # Show statistics
    print("=" * 70)
    print("LEARNING STATISTICS")
    print("=" * 70)
    stats = loop.get_statistics()
    for key, value in stats.items():
        if not isinstance(value, (dict, list)):
            print(f"  {key}: {value}")

    print()
    ready, msg = loop.is_ready_for_distillation()
    print(f"Ready for distillation: {ready}")
    print(f"Status: {msg}")
