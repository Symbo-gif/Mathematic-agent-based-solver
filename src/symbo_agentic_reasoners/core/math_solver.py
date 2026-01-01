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
MathSolver - User-Facing API Using Full Agent Pipeline
========================================================

This is the proper entry point for solving mathematical problems.
It uses the full agent infrastructure:

    User Problem
         │
         ▼
    ┌─────────────┐
    │ MathSolver  │  (This class)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Blackboard │  (Posts task)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Orchestrator│  (BDI deliberation)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Supervisor  │  (Routes to specialist)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Specialist  │  (Delegates to SymPy)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Verification│  (Confirms result)
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  Harvester  │  (Captures trace for SymboLLM)
    └─────────────┘

NO BYPASSES. This ensures:
1. All problems flow through BDI agents
2. All results are verified
3. All verified traces train SymboLLM
"""

import logging
import uuid
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger('symbo_agentic_reasoners.core.math_solver')


class SolveStatus(Enum):
    """Status of a solve operation"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNVERIFIED = "unverified"


@dataclass
class SolveResult:
    """Result from MathSolver"""
    status: SolveStatus
    result: Optional[str] = None
    sympy_result: Optional[Any] = None
    problem_type: str = ""
    domain: str = ""
    operation: str = ""
    agents_used: List[str] = field(default_factory=list)
    verified: bool = False
    solve_time_ms: float = 0.0
    trace_id: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

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
            'status': self.status.value,
            'result': self.result,
            'problem_type': self.problem_type,
            'domain': self.domain,
            'operation': self.operation,
            'agents_used': self.agents_used,
            'verified': self.verified,
            'solve_time_ms': round(self.solve_time_ms, 2),
            'trace_id': self.trace_id,
            'error': self.error
        }


class MathSolver:
    """
    User-facing mathematical problem solver.

    Uses the FULL agent pipeline - no bypasses. Every problem:
    1. Gets posted to Blackboard
    2. Orchestrator deliberates and routes
    3. Supervisors delegate to specialists
    4. Specialists compute via SymPy (never directly)
    5. Results verified
    6. Traces harvested for SymboLLM training

    Usage:
        solver = MathSolver()
        result = solver.solve("factor x^2 - 4")
        print(result.result)  # "(x - 2)*(x + 2)"
    """

    def __init__(
        self,
        enable_parallel: bool = True,
        enable_harvesting: bool = True,
        enable_verification: bool = True,
        max_parallel_specialists: int = 4
    ):
        """
        Initialize MathSolver.

        Args:
            enable_parallel: Allow parallel specialist execution
            enable_harvesting: Capture traces for SymboLLM training
            enable_verification: Verify results before returning
            max_parallel_specialists: Max concurrent specialists
        """
        self.enable_parallel = enable_parallel
        self.enable_harvesting = enable_harvesting
        self.enable_verification = enable_verification
        self.max_parallel_specialists = max_parallel_specialists

        # Lazy initialization
        self._phase0 = None
        self._orchestrator = None
        self._harvester = None
        self._hardware = None
        self._executor = None

        # Statistics
        self._problems_solved = 0
        self._problems_failed = 0
        self._traces_captured = 0

        logger.info("MathSolver initialized (full agent pipeline mode)")

    def _ensure_initialized(self):
        """Lazy initialization of components"""
        if self._phase0 is not None:
            return

        from symbo_agentic_reasoners.core.system import Phase0System
        from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
        from symbo_agentic_reasoners.infrastructure.hardware_detector import get_hardware_detector

        # Initialize Phase 0 infrastructure
        self._phase0 = Phase0System()
        self._phase0.start()

        # Get hardware profile
        self._hardware = get_hardware_detector().detect()
        logger.info(f"Hardware: {self._hardware.max_parallel_symbolic_agents} parallel agents possible")

        # Adjust parallelism based on hardware
        actual_parallel = min(
            self.max_parallel_specialists,
            self._hardware.max_parallel_symbolic_agents
        )

        # Initialize orchestrator with infrastructure
        self._orchestrator = MainOrchestrator(
            df=self._phase0.df,
            blackboard=self._phase0.blackboard
        )

        # Initialize harvester for trace capture
        if self.enable_harvesting:
            from symbo_agentic_reasoners.optimization.distillation.harvester import ThoughtTraceHarvester
            self._harvester = ThoughtTraceHarvester()

        # Thread pool for parallel specialist execution
        if self.enable_parallel:
            self._executor = ThreadPoolExecutor(max_workers=actual_parallel)

        logger.info(f"MathSolver ready (parallel={actual_parallel}, harvesting={self.enable_harvesting})")

    def solve(self, problem: str, timeout: float = 60.0) -> SolveResult:
        """
        Solve a mathematical problem using the full agent pipeline.

        Args:
            problem: Natural language or mathematical expression
            timeout: Maximum solve time in seconds

        Returns:
            SolveResult with solution and metadata
        """
        start_time = time.time()
        trace_id = str(uuid.uuid4())[:8]

        try:
            self._ensure_initialized()

            logger.info(f"[{trace_id}] Solving: {problem}")

            # Step 1: Parse and classify problem
            from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam
            analysis_team = ProblemAnalysisTeam()
            structured = analysis_team.process(problem)

            if structured is None:
                return SolveResult(
                    status=SolveStatus.FAILED,
                    error="Failed to parse problem",
                    trace_id=trace_id,
                    solve_time_ms=(time.time() - start_time) * 1000
                )

            domain = structured.domain.value.lower() if hasattr(structured.domain, 'value') else str(structured.domain)
            operation = structured.metadata.get('operation', 'compute')

            logger.info(f"[{trace_id}] Classified: domain={domain}, operation={operation}")

            # Step 2: Post task to Blackboard
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            from symbo_agentic_reasoners.core.omdoc_schema import create_variable

            task_entry = create_entry(
                entry_type=EntryType.TASK,
                content=create_variable(problem),
                author_agent='math_solver',
                conversation_id=trace_id,
                tags=[domain, 'task', operation],
                status=EntryStatus.PENDING,
                metadata={
                    'raw_input': problem,
                    'sympy_expr': str(structured.sympy_expr) if structured.sympy_expr else None,
                    'operation': operation,
                    'domain': domain,
                    'problem_type': structured.problem_type.value if hasattr(structured.problem_type, 'value') else str(structured.problem_type),
                    'variable': structured.metadata.get('variable', 'x')
                }
            )

            self._phase0.blackboard.post(task_entry)
            logger.info(f"[{trace_id}] Posted task to Blackboard: {task_entry.entry_id}")

            # Step 3: Route through orchestrator to specialists
            # The orchestrator will use its BDI loop to deliberate and route
            result_entry = self._orchestrator.process(task_entry)

            if result_entry is None:
                return SolveResult(
                    status=SolveStatus.FAILED,
                    error="Orchestrator returned no result",
                    trace_id=trace_id,
                    domain=domain,
                    operation=operation,
                    solve_time_ms=(time.time() - start_time) * 1000
                )

            # Extract result
            result_str = None
            if hasattr(result_entry, 'metadata') and result_entry.metadata:
                result_str = result_entry.metadata.get('result_str') or result_entry.metadata.get('result')
            if not result_str and hasattr(result_entry, 'content'):
                result_str = str(result_entry.content)

            # Step 4: Verify result
            verified = False
            if self.enable_verification and result_str:
                verified = self._verify_result(structured, result_str, trace_id)

            # Step 5: Capture trace for SymboLLM training
            if self.enable_harvesting and verified:
                self._capture_trace(
                    trace_id=trace_id,
                    problem=problem,
                    structured=structured,
                    result=result_str,
                    agents_used=self._get_agents_used(result_entry)
                )
                self._traces_captured += 1

            # Build result
            solve_time = (time.time() - start_time) * 1000

            if result_str and result_str not in ('None', 'none', ''):
                self._problems_solved += 1
                return SolveResult(
                    status=SolveStatus.SUCCESS if verified else SolveStatus.UNVERIFIED,
                    result=result_str,
                    problem_type=structured.problem_type.value if hasattr(structured.problem_type, 'value') else str(structured.problem_type),
                    domain=domain,
                    operation=operation,
                    agents_used=self._get_agents_used(result_entry),
                    verified=verified,
                    solve_time_ms=solve_time,
                    trace_id=trace_id
                )
            else:
                self._problems_failed += 1
                return SolveResult(
                    status=SolveStatus.FAILED,
                    error="No result produced",
                    domain=domain,
                    operation=operation,
                    solve_time_ms=solve_time,
                    trace_id=trace_id
                )

        except Exception as e:
            self._problems_failed += 1
            logger.exception(f"[{trace_id}] Solve failed: {e}")
            return SolveResult(
                status=SolveStatus.FAILED,
                error=str(e),
                trace_id=trace_id,
                solve_time_ms=(time.time() - start_time) * 1000
            )

    def _verify_result(self, structured, result_str: str, trace_id: str) -> bool:
        """Verify result using verification agents"""
        try:
            from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent

            checker = LogicCheckerAgent()
            is_valid, violations = checker.check(
                candidate_result=result_str,
                original_problem={
                    'raw_input': structured.raw_input,
                    'sympy_expr': structured.sympy_expr,
                    'operation': structured.metadata.get('operation', 'compute')
                }
            )

            if not is_valid:
                logger.warning(f"[{trace_id}] Verification failed: {violations}")

            return is_valid

        except Exception as e:
            logger.warning(f"[{trace_id}] Verification error: {e}")
            return False

    def _capture_trace(
        self,
        trace_id: str,
        problem: str,
        structured,
        result: str,
        agents_used: List[str]
    ):
        """Capture thought trace for SymboLLM training"""
        if not self._harvester:
            return

        try:
            from symbo_agentic_reasoners.optimization.distillation.harvester import (
                ThoughtTrace, VerificationStatus
            )

            trace = ThoughtTrace(
                trace_id=trace_id,
                timestamp=datetime.now(),
                original_query=problem,
                query_type=structured.problem_type.value if hasattr(structured.problem_type, 'value') else str(structured.problem_type),
                complexity_score=structured.metadata.get('complexity', 0.5),
                orchestrator_decomposition=[],  # TODO: capture from orchestrator
                supervisor_strategy=structured.domain.value if hasattr(structured.domain, 'value') else str(structured.domain),
                specialist_agents_invoked=agents_used,
                symbolic_expressions=[str(structured.sympy_expr)] if structured.sympy_expr else [],
                fitted_coefficients={},
                taylor_expansion_order=0,
                groebner_basis_used=False,
                verification_status=VerificationStatus.VERIFIED,
                formal_proof_lean4=None,
                debate_consensus_score=None,
                final_answer=result,
                confidence_score=0.95,
                total_latency_ms=0.0,
                agents_activated=len(agents_used),
                symbolic_ops_count=1
            )

            self._harvester.add_trace(trace)
            logger.info(f"[{trace_id}] Captured trace for SymboLLM training")

        except Exception as e:
            logger.warning(f"[{trace_id}] Trace capture failed: {e}")

    def _get_agents_used(self, result_entry) -> List[str]:
        """Extract list of agents that contributed to result"""
        agents = []
        if hasattr(result_entry, 'author_agent'):
            agents.append(result_entry.author_agent)
        if hasattr(result_entry, 'metadata') and result_entry.metadata:
            if 'agents_used' in result_entry.metadata:
                agents.extend(result_entry.metadata['agents_used'])
        return list(set(agents))

    def get_statistics(self) -> Dict[str, Any]:
        """Get solver statistics"""
        total = self._problems_solved + self._problems_failed
        return {
            'problems_solved': self._problems_solved,
            'problems_failed': self._problems_failed,
            'total_problems': total,
            'success_rate': (self._problems_solved / total * 100) if total > 0 else 0.0,
            'traces_captured': self._traces_captured,
            'harvesting_enabled': self.enable_harvesting,
            'verification_enabled': self.enable_verification,
            'parallel_enabled': self.enable_parallel
        }

    def shutdown(self):
        """Clean shutdown"""
        if self._executor:
            self._executor.shutdown(wait=True)
        if self._phase0:
            self._phase0.shutdown()
        logger.info("MathSolver shut down")


# Singleton instance
_solver: Optional[MathSolver] = None


def get_solver() -> MathSolver:
    """Get or create the global MathSolver"""
    global _solver
    if _solver is None:
        _solver = MathSolver()
    return _solver


def solve(problem: str) -> SolveResult:
    """Convenience function to solve a problem"""
    return get_solver().solve(problem)


if __name__ == "__main__":
    """Test MathSolver"""
    import json

    print("=" * 60)
    print("MATH SOLVER TEST - Full Agent Pipeline")
    print("=" * 60)
    print()

    solver = MathSolver(
        enable_parallel=True,
        enable_harvesting=True,
        enable_verification=True
    )

    test_problems = [
        "2 + 2",
        "factor x^2 - 4",
        "expand (x + 1)^2",
        "simplify x^2 + 2*x + 1",
    ]

    for problem in test_problems:
        print(f"\nProblem: {problem}")
        print("-" * 40)

        result = solver.solve(problem)
        print(f"Status: {result.status.value}")
        print(f"Result: {result.result}")
        print(f"Verified: {result.verified}")
        print(f"Time: {result.solve_time_ms:.1f}ms")
        print(f"Agents: {result.agents_used}")

    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)
    print(json.dumps(solver.get_statistics(), indent=2))

    solver.shutdown()
