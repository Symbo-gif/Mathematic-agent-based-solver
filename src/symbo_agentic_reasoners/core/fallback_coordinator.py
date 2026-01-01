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
FALLBACK COORDINATOR - SymPy Last Resort Central Control
=========================================================

This module provides centralized coordination for the "SymPy Last Resort"
architecture. It manages the fallback chain, coordinates between domain
algorithms and SymPy, and provides unified reporting.

ARCHITECTURE OVERVIEW:
---------------------
1. Domain algorithms are ALWAYS tried first
2. SymPy is used ONLY as a fallback (last resort)
3. All fallbacks are tracked and reported
4. Specialists register their domain capabilities
5. Coordinator provides unified statistics and optimization hints

USAGE:
-----
coordinator = FallbackCoordinator()

# Register domain solvers
coordinator.register_domain_solver(
    domain="algebra",
    operation="solve",
    solver=polynomial_specialist.domain_solver,
    priority=1
)

# Execute with fallback
result = coordinator.execute_with_fallback(
    operation="solve",
    domain="algebra",
    input_data={"expr": "x**2 - 4", "var": "x"},
    sympy_fallback=lambda: sp.solve(x**2 - 4, x)
)

Reference:
---------
Second Opinion Analysis: "Add explicit fallback coordinator"
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum, auto
from threading import Lock
from datetime import datetime

from symbo_agentic_reasoners.core.fallback_tracker import (
    FallbackTracker, get_tracker, ResolutionMethod
)

logger = logging.getLogger('symbo_agentic_reasoners.fallback_coordinator')


class FallbackStrategy(Enum):
    """Strategy for handling fallbacks."""
    DOMAIN_FIRST = auto()      # Try domain, then SymPy (default)
    SYMPY_ONLY = auto()        # Only use SymPy (for intentional use)
    DOMAIN_ONLY = auto()       # Only use domain (fail if not supported)
    PARALLEL = auto()          # Try both, compare results (verification mode)


@dataclass
class DomainSolver:
    """Registration record for a domain-specific solver."""
    domain: str
    operation: str
    solver: Callable[..., Tuple[bool, Any, str]]
    priority: int = 0
    description: str = ""
    enabled: bool = True


@dataclass
class FallbackResult:
    """Result of a fallback-aware computation."""
    success: bool
    result: Any
    method: ResolutionMethod
    solver_used: str
    duration_ms: float
    fallback_reason: Optional[str] = None
    domain_attempted: bool = False
    sympy_attempted: bool = False
    error: Optional[str] = None


class FallbackCoordinator:
    """
    Central coordinator for the SymPy Last Resort architecture.

    This class provides:
    1. Registration of domain-specific solvers
    2. Unified execution with automatic fallback
    3. Strategy selection (domain-first, sympy-only, etc.)
    4. Comprehensive statistics and reporting
    5. Optimization hints based on fallback patterns

    DESIGN PRINCIPLES:
    -----------------
    - Domain algorithms are the PRIMARY choice
    - SymPy is the FALLBACK (last resort)
    - All operations are tracked for analysis
    - Clear separation between intentional and fallback SymPy use
    """

    def __init__(self, tracker: Optional[FallbackTracker] = None):
        """
        Initialize the fallback coordinator.

        Args:
            tracker: FallbackTracker instance (uses global if not provided)
        """
        self._tracker = tracker or get_tracker()
        self._lock = Lock()

        # Domain solver registry: {domain: {operation: [DomainSolver, ...]}}
        self._domain_solvers: Dict[str, Dict[str, List[DomainSolver]]] = {}

        # Statistics
        self._stats = {
            'total_executions': 0,
            'domain_successes': 0,
            'sympy_fallbacks': 0,
            'sympy_intentional': 0,
            'failures': 0,
        }

        # SymPy fallback function registry
        self._sympy_fallbacks: Dict[str, Dict[str, Callable]] = {}

        logger.info("[FallbackCoordinator] Initialized with SymPy Last Resort architecture")

    def register_domain_solver(
        self,
        domain: str,
        operation: str,
        solver: Callable[..., Tuple[bool, Any, str]],
        priority: int = 0,
        description: str = ""
    ):
        """
        Register a domain-specific solver.

        The solver should be a callable that returns:
            (success: bool, result: Any, method_name: str)

        Args:
            domain: Mathematical domain (algebra, calculus, etc.)
            operation: Operation type (solve, factor, differentiate, etc.)
            solver: Callable that attempts domain-specific solution
            priority: Higher priority solvers are tried first
            description: Human-readable description
        """
        with self._lock:
            if domain not in self._domain_solvers:
                self._domain_solvers[domain] = {}
            if operation not in self._domain_solvers[domain]:
                self._domain_solvers[domain][operation] = []

            solver_record = DomainSolver(
                domain=domain,
                operation=operation,
                solver=solver,
                priority=priority,
                description=description
            )

            self._domain_solvers[domain][operation].append(solver_record)
            # Sort by priority (highest first)
            self._domain_solvers[domain][operation].sort(
                key=lambda s: s.priority, reverse=True
            )

            logger.info(f"[FallbackCoordinator] Registered solver: {domain}.{operation} "
                       f"(priority={priority})")

    def register_sympy_fallback(
        self,
        domain: str,
        operation: str,
        fallback: Callable[..., Any]
    ):
        """
        Register a SymPy fallback function for a domain/operation.

        Args:
            domain: Mathematical domain
            operation: Operation type
            fallback: Callable that performs the operation using SymPy
        """
        with self._lock:
            if domain not in self._sympy_fallbacks:
                self._sympy_fallbacks[domain] = {}
            self._sympy_fallbacks[domain][operation] = fallback

            logger.debug(f"[FallbackCoordinator] Registered SymPy fallback: {domain}.{operation}")

    def execute_with_fallback(
        self,
        operation: str,
        domain: str,
        input_data: Dict[str, Any],
        sympy_fallback: Optional[Callable[[], Any]] = None,
        strategy: FallbackStrategy = FallbackStrategy.DOMAIN_FIRST,
        specialist: Optional[str] = None
    ) -> FallbackResult:
        """
        Execute an operation with automatic fallback handling.

        EXECUTION FLOW (DOMAIN_FIRST strategy):
        1. Get domain solvers for operation
        2. Try each solver by priority
        3. If all fail, use SymPy fallback
        4. Track and return result

        Args:
            operation: Operation to perform (solve, factor, etc.)
            domain: Mathematical domain
            input_data: Data for the operation
            sympy_fallback: Optional explicit SymPy fallback function
            strategy: Fallback strategy to use
            specialist: Name of calling specialist (for tracking)

        Returns:
            FallbackResult with success status, result, and metadata
        """
        import time
        start_time = time.perf_counter()

        # Track this execution
        input_summary = str(input_data)[:100]

        with self._tracker.track(operation, input_summary, domain, specialist):
            self._stats['total_executions'] += 1

            result = FallbackResult(
                success=False,
                result=None,
                method=ResolutionMethod.FAILED,
                solver_used="none",
                duration_ms=0,
                domain_attempted=False,
                sympy_attempted=False
            )

            # Strategy: SymPy only (intentional use)
            if strategy == FallbackStrategy.SYMPY_ONLY:
                return self._execute_sympy_intentional(
                    operation, domain, input_data, sympy_fallback, start_time
                )

            # Strategy: Domain only (no fallback)
            if strategy == FallbackStrategy.DOMAIN_ONLY:
                return self._execute_domain_only(
                    operation, domain, input_data, start_time
                )

            # Strategy: Domain first (default - SymPy Last Resort)
            # Try domain solvers first
            domain_result = self._try_domain_solvers(operation, domain, input_data)
            result.domain_attempted = True

            if domain_result[0]:  # Success
                self._stats['domain_successes'] += 1
                self._tracker.mark_domain_success()

                duration_ms = (time.perf_counter() - start_time) * 1000
                return FallbackResult(
                    success=True,
                    result=domain_result[1],
                    method=ResolutionMethod.DOMAIN_SOLVER,
                    solver_used=domain_result[2],
                    duration_ms=duration_ms,
                    domain_attempted=True,
                    sympy_attempted=False
                )

            # Domain failed - fall back to SymPy
            fallback_reason = domain_result[2] if len(domain_result) > 2 else "domain solver failed"
            self._tracker.mark_fallback(fallback_reason)

            return self._execute_sympy_fallback(
                operation, domain, input_data, sympy_fallback,
                fallback_reason, start_time
            )

    def _try_domain_solvers(
        self,
        operation: str,
        domain: str,
        input_data: Dict[str, Any]
    ) -> Tuple[bool, Any, str]:
        """Try all registered domain solvers for an operation."""

        with self._lock:
            solvers = self._domain_solvers.get(domain, {}).get(operation, [])

        if not solvers:
            return (False, None, "no domain solver registered")

        for solver in solvers:
            if not solver.enabled:
                continue

            try:
                success, result, method = solver.solver(**input_data)
                if success:
                    return (True, result, f"{domain}.{method}")
            except Exception as e:
                logger.debug(f"Domain solver {solver.description} failed: {e}")
                continue

        return (False, None, "all domain solvers failed")

    def _execute_sympy_fallback(
        self,
        operation: str,
        domain: str,
        input_data: Dict[str, Any],
        sympy_fallback: Optional[Callable],
        fallback_reason: str,
        start_time: float
    ) -> FallbackResult:
        """Execute SymPy as a fallback."""
        import time

        self._stats['sympy_fallbacks'] += 1

        # Get fallback function
        fallback_fn = sympy_fallback
        if fallback_fn is None:
            with self._lock:
                fallback_fn = self._sympy_fallbacks.get(domain, {}).get(operation)

        if fallback_fn is None:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._stats['failures'] += 1
            return FallbackResult(
                success=False,
                result=None,
                method=ResolutionMethod.FAILED,
                solver_used="none",
                duration_ms=duration_ms,
                fallback_reason="no SymPy fallback registered",
                domain_attempted=True,
                sympy_attempted=False,
                error="No fallback available"
            )

        try:
            # Execute SymPy fallback
            if callable(sympy_fallback):
                result = sympy_fallback()
            else:
                result = fallback_fn(**input_data)

            duration_ms = (time.perf_counter() - start_time) * 1000
            return FallbackResult(
                success=True,
                result=result,
                method=ResolutionMethod.SYMPY_FALLBACK,
                solver_used="sympy",
                duration_ms=duration_ms,
                fallback_reason=fallback_reason,
                domain_attempted=True,
                sympy_attempted=True
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._stats['failures'] += 1
            return FallbackResult(
                success=False,
                result=None,
                method=ResolutionMethod.FAILED,
                solver_used="sympy",
                duration_ms=duration_ms,
                fallback_reason=fallback_reason,
                domain_attempted=True,
                sympy_attempted=True,
                error=str(e)
            )

    def _execute_sympy_intentional(
        self,
        operation: str,
        domain: str,
        input_data: Dict[str, Any],
        sympy_fallback: Optional[Callable],
        start_time: float
    ) -> FallbackResult:
        """Execute SymPy intentionally (not as fallback)."""
        import time

        self._stats['sympy_intentional'] += 1
        self._tracker.mark_intentional_sympy(f"intentional {operation}")

        fallback_fn = sympy_fallback
        if fallback_fn is None:
            with self._lock:
                fallback_fn = self._sympy_fallbacks.get(domain, {}).get(operation)

        try:
            if callable(sympy_fallback):
                result = sympy_fallback()
            else:
                result = fallback_fn(**input_data) if fallback_fn else None

            duration_ms = (time.perf_counter() - start_time) * 1000
            return FallbackResult(
                success=result is not None,
                result=result,
                method=ResolutionMethod.SYMPY_INTENTIONAL,
                solver_used="sympy_intentional",
                duration_ms=duration_ms,
                domain_attempted=False,
                sympy_attempted=True
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._stats['failures'] += 1
            return FallbackResult(
                success=False,
                result=None,
                method=ResolutionMethod.FAILED,
                solver_used="sympy_intentional",
                duration_ms=duration_ms,
                domain_attempted=False,
                sympy_attempted=True,
                error=str(e)
            )

    def _execute_domain_only(
        self,
        operation: str,
        domain: str,
        input_data: Dict[str, Any],
        start_time: float
    ) -> FallbackResult:
        """Execute using domain solvers only (no fallback)."""
        import time

        domain_result = self._try_domain_solvers(operation, domain, input_data)
        duration_ms = (time.perf_counter() - start_time) * 1000

        if domain_result[0]:
            self._stats['domain_successes'] += 1
            self._tracker.mark_domain_success()
            return FallbackResult(
                success=True,
                result=domain_result[1],
                method=ResolutionMethod.DOMAIN_SOLVER,
                solver_used=domain_result[2],
                duration_ms=duration_ms,
                domain_attempted=True,
                sympy_attempted=False
            )
        else:
            self._stats['failures'] += 1
            self._tracker.mark_failed(domain_result[2])
            return FallbackResult(
                success=False,
                result=None,
                method=ResolutionMethod.FAILED,
                solver_used="none",
                duration_ms=duration_ms,
                domain_attempted=True,
                sympy_attempted=False,
                error=domain_result[2]
            )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive fallback statistics.

        Returns:
            Dictionary with execution counts, rates, and analysis
        """
        total = self._stats['total_executions']
        if total == 0:
            return {
                'total_executions': 0,
                'domain_success_rate': 0.0,
                'sympy_fallback_rate': 0.0,
                'failure_rate': 0.0,
                'registered_domains': [],
                'tracker_stats': self._tracker.get_statistics()
            }

        domain_rate = self._stats['domain_successes'] / total * 100
        fallback_rate = self._stats['sympy_fallbacks'] / total * 100
        failure_rate = self._stats['failures'] / total * 100

        with self._lock:
            registered_domains = list(self._domain_solvers.keys())
            solver_count = sum(
                len(ops)
                for domain_ops in self._domain_solvers.values()
                for ops in domain_ops.values()
            )

        return {
            'total_executions': total,
            'domain_successes': self._stats['domain_successes'],
            'sympy_fallbacks': self._stats['sympy_fallbacks'],
            'sympy_intentional': self._stats['sympy_intentional'],
            'failures': self._stats['failures'],
            'domain_success_rate': domain_rate,
            'sympy_fallback_rate': fallback_rate,
            'failure_rate': failure_rate,
            'registered_domains': registered_domains,
            'total_domain_solvers': solver_count,
            'tracker_stats': self._tracker.get_statistics()
        }

    def get_optimization_hints(self) -> List[str]:
        """
        Get optimization hints based on fallback patterns.

        Returns:
            List of suggestions for reducing SymPy fallbacks
        """
        hints = []
        tracker_stats = self._tracker.get_statistics()

        fallback_rate = tracker_stats.get('fallback_rate', 0)
        if fallback_rate > 0.5:
            hints.append(
                f"High fallback rate ({fallback_rate:.1%}): Consider implementing "
                "more domain-specific algorithms"
            )

        # Analyze common fallback reasons
        reasons = tracker_stats.get('fallback_reasons', {})
        for reason, count in list(reasons.items())[:3]:
            if count > 5:
                hints.append(
                    f"Frequent fallback reason '{reason}' ({count} times): "
                    "Consider implementing domain solver for this case"
                )

        # Check for domains without solvers
        with self._lock:
            for domain in self._sympy_fallbacks:
                if domain not in self._domain_solvers:
                    hints.append(
                        f"Domain '{domain}' has SymPy fallbacks but no domain solvers"
                    )

        if not hints:
            hints.append("Architecture is well-optimized: domain solvers are handling most cases")

        return hints

    def list_registered_solvers(self) -> Dict[str, Dict[str, List[str]]]:
        """List all registered domain solvers."""
        with self._lock:
            result = {}
            for domain, operations in self._domain_solvers.items():
                result[domain] = {}
                for operation, solvers in operations.items():
                    result[domain][operation] = [
                        f"{s.description} (priority={s.priority})"
                        for s in solvers
                    ]
            return result


# Global coordinator instance
_global_coordinator: Optional[FallbackCoordinator] = None


def get_coordinator() -> FallbackCoordinator:
    """Get the global fallback coordinator instance."""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = FallbackCoordinator()
    return _global_coordinator


def execute_with_fallback(
    operation: str,
    domain: str,
    input_data: Dict[str, Any],
    sympy_fallback: Optional[Callable[[], Any]] = None,
    strategy: FallbackStrategy = FallbackStrategy.DOMAIN_FIRST,
    specialist: Optional[str] = None
) -> FallbackResult:
    """
    Convenience function for executing with fallback using global coordinator.

    Args:
        operation: Operation to perform
        domain: Mathematical domain
        input_data: Input data dictionary
        sympy_fallback: SymPy fallback function
        strategy: Fallback strategy
        specialist: Name of calling specialist

    Returns:
        FallbackResult
    """
    return get_coordinator().execute_with_fallback(
        operation=operation,
        domain=domain,
        input_data=input_data,
        sympy_fallback=sympy_fallback,
        strategy=strategy,
        specialist=specialist
    )
