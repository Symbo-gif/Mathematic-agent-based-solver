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
FALLBACK TRACKER - SymPy Last Resort Monitoring
================================================

This module provides tracking and logging for solver fallback behavior.
It ensures transparency about when domain-specific solvers handle computation
vs when SymPy is used as a fallback.

ARCHITECTURE PRINCIPLES:
-----------------------
1. Log every computation with its resolution path
2. Track SymPy usage as "fallback" vs "intentional"
3. Provide statistics for optimization
4. Enable debugging of unexpected SymPy usage

USAGE:
-----
tracker = FallbackTracker()
with tracker.track("solve", "x**2 - 4", domain="algebra"):
    # Domain-specific solver attempt
    result = polynomial_solve(...)
    if result is None:
        tracker.mark_fallback("SymPy", reason="cubic formula not implemented")
        result = sp.solve(...)

# Get statistics
stats = tracker.get_statistics()
print(f"SymPy fallback rate: {stats['fallback_rate']:.1%}")

Reference:
---------
Second Opinion Analysis: "Strict fallback status tracking and logging"
"""

import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable
from threading import Lock
import json

logger = logging.getLogger('symbo_agentic_reasoners.fallback_tracker')


# =============================================================================
# SYMPY_DISABLED MODE
# =============================================================================
# When enabled, ANY attempt to fall back to SymPy will raise an exception.
# This enforces the "SymPy Last Resort" architecture by making fallbacks fail.
#
# Enable via:
#   - Environment variable: SYMPY_DISABLED=1
#   - Programmatic: enable_sympy_disabled_mode()
#   - Context manager: with sympy_disabled():
# =============================================================================

class SympyDisabledException(Exception):
    """
    Exception raised when SymPy fallback is attempted while SYMPY_DISABLED mode is active.

    This exception helps enforce the "SymPy Last Resort" architecture by preventing
    accidental fallbacks to SymPy. When this exception is raised, it indicates that
    a domain-specific solver should be implemented for the given operation.
    """

    def __init__(self, operation: str, reason: str, domain: Optional[str] = None):
        self.operation = operation
        self.reason = reason
        self.domain = domain
        domain_str = f" ({domain})" if domain else ""
        message = (
            f"SYMPY_DISABLED: SymPy fallback attempted for '{operation}'{domain_str}.\n"
            f"Reason: {reason}\n"
            f"A domain-specific solver should handle this computation."
        )
        super().__init__(message)


# Global configuration for SYMPY_DISABLED mode
_SYMPY_DISABLED: bool = os.environ.get('SYMPY_DISABLED', '').lower() in ('1', 'true', 'yes')


def is_sympy_disabled() -> bool:
    """Check if SYMPY_DISABLED mode is active."""
    return _SYMPY_DISABLED


def enable_sympy_disabled_mode():
    """
    Enable SYMPY_DISABLED mode globally.

    When enabled, any call to mark_fallback() with to_sympy=True will raise
    a SympyDisabledException instead of proceeding with the fallback.

    This is useful for:
    - Testing to ensure domain-specific solvers are used
    - Development to identify gaps in native algorithm coverage
    - Strict enforcement of the "SymPy Last Resort" architecture
    """
    global _SYMPY_DISABLED
    _SYMPY_DISABLED = True
    logger.warning("SYMPY_DISABLED mode ENABLED - SymPy fallbacks will raise exceptions")


def disable_sympy_disabled_mode():
    """Disable SYMPY_DISABLED mode, allowing SymPy fallbacks."""
    global _SYMPY_DISABLED
    _SYMPY_DISABLED = False
    logger.info("SYMPY_DISABLED mode disabled - SymPy fallbacks allowed")


@contextmanager
def sympy_disabled():
    """
    Context manager for temporarily enabling SYMPY_DISABLED mode.

    Usage:
        with sympy_disabled():
            # Any SymPy fallback in here will raise SympyDisabledException
            result = solver.solve(problem)

        # After the context, previous mode is restored
    """
    global _SYMPY_DISABLED
    previous = _SYMPY_DISABLED
    _SYMPY_DISABLED = True
    try:
        yield
    finally:
        _SYMPY_DISABLED = previous


class ResolutionMethod(Enum):
    """Classification of how a computation was resolved."""
    DOMAIN_SOLVER = auto()    # Solved by domain-specific algorithm
    DOMAIN_ALGORITHM = auto() # Solved by domain-specific algorithm (alias)
    SYMPY_FALLBACK = auto()   # Fell back to SymPy
    SYMPY_INTENTIONAL = auto()  # SymPy used intentionally (e.g., simplify)
    CACHED = auto()           # Result from cache
    FAILED = auto()           # Could not resolve
    PARTIAL = auto()          # Partially resolved


@dataclass
class ComputationRecord:
    """Record of a single computation attempt."""
    operation: str
    input_summary: str
    domain: Optional[str]
    specialist: Optional[str]
    method: ResolutionMethod
    fallback_reason: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            'operation': self.operation,
            'input_summary': self.input_summary[:100],  # Truncate long inputs
            'domain': self.domain,
            'specialist': self.specialist,
            'method': self.method.name,
            'fallback_reason': self.fallback_reason,
            'duration_ms': round(self.duration_ms, 2),
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
        }


class FallbackTracker:
    """
    Tracks and logs solver fallback behavior.

    Provides visibility into when domain-specific solvers are used vs
    when SymPy serves as a fallback. This is critical for the
    "SymPy Last Resort" architecture.

    STATISTICS:
    ----------
    - Total computations
    - Domain solver success rate
    - SymPy fallback rate
    - Average resolution time by method
    - Most common fallback reasons
    """

    def __init__(self, log_level: int = logging.INFO, max_records: int = 10000):
        """
        Initialize the fallback tracker.

        Args:
            log_level: Logging level for fallback events
            max_records: Maximum records to keep in memory (FIFO)
        """
        self.log_level = log_level
        self.max_records = max_records
        self.records: List[ComputationRecord] = []
        self._lock = Lock()

        # Statistics counters (thread-safe)
        self._stats = {
            'total': 0,
            'domain_solver': 0,
            'sympy_fallback': 0,
            'sympy_intentional': 0,
            'failed': 0,
            'cached': 0,
        }

        # Current tracking context (per-computation)
        self._current_operation: Optional[str] = None
        self._current_input: Optional[str] = None
        self._current_domain: Optional[str] = None
        self._current_specialist: Optional[str] = None
        self._start_time: Optional[float] = None
        self._method: ResolutionMethod = ResolutionMethod.DOMAIN_SOLVER
        self._fallback_reason: Optional[str] = None

    @contextmanager
    def track(self, operation: str, input_text: str,
              domain: Optional[str] = None, specialist: Optional[str] = None):
        """
        Context manager for tracking a computation.

        Usage:
            with tracker.track("solve", "x**2 - 4", domain="algebra"):
                result = solve(...)
                if fallback_needed:
                    tracker.mark_fallback("reason")

        Args:
            operation: Operation being performed (solve, diff, integrate, etc.)
            input_text: Input expression/problem
            domain: Mathematical domain
            specialist: Specialist agent handling the computation
        """
        self._current_operation = operation
        self._current_input = input_text
        self._current_domain = domain
        self._current_specialist = specialist
        self._start_time = time.perf_counter()
        self._method = ResolutionMethod.DOMAIN_SOLVER  # Assume success initially
        self._fallback_reason = None

        try:
            yield self
        except Exception as e:
            self._method = ResolutionMethod.FAILED
            self._fallback_reason = str(e)
            raise
        finally:
            self._record_computation()

    def mark_fallback(self, reason: str, to_sympy: bool = True):
        """
        Mark that the current computation fell back to SymPy.

        Call this within a track() context when domain solver fails
        and SymPy is used instead.

        Args:
            reason: Why the fallback occurred
            to_sympy: True if falling back to SymPy (default), False for other fallback

        Raises:
            SympyDisabledException: If SYMPY_DISABLED mode is active and to_sympy=True
        """
        # Check SYMPY_DISABLED mode BEFORE allowing fallback
        if to_sympy and _SYMPY_DISABLED:
            raise SympyDisabledException(
                operation=self._current_operation or "unknown",
                reason=reason,
                domain=self._current_domain
            )

        if to_sympy:
            self._method = ResolutionMethod.SYMPY_FALLBACK
        else:
            self._method = ResolutionMethod.PARTIAL
        self._fallback_reason = reason

        logger.log(self.log_level,
                  f"[FALLBACK] {self._current_operation} -> SymPy: {reason}")

    def mark_intentional_sympy(self, reason: str = "intentional"):
        """
        Mark that SymPy is being used intentionally (not as fallback).

        Use this for operations where SymPy is the appropriate choice,
        like simplification or certain symbolic manipulations.

        Args:
            reason: Why SymPy is the right choice
        """
        self._method = ResolutionMethod.SYMPY_INTENTIONAL
        self._fallback_reason = reason

    def mark_domain_success(self):
        """Mark that domain-specific solver succeeded."""
        self._method = ResolutionMethod.DOMAIN_SOLVER

    def mark_cached(self):
        """Mark that result came from cache."""
        self._method = ResolutionMethod.CACHED

    def mark_failed(self, reason: str):
        """Mark that computation failed entirely."""
        self._method = ResolutionMethod.FAILED
        self._fallback_reason = reason

    def _record_computation(self):
        """Record the completed computation."""
        duration_ms = (time.perf_counter() - self._start_time) * 1000 if self._start_time else 0

        record = ComputationRecord(
            operation=self._current_operation or "unknown",
            input_summary=self._current_input or "",
            domain=self._current_domain,
            specialist=self._current_specialist,
            method=self._method,
            fallback_reason=self._fallback_reason,
            duration_ms=duration_ms,
            success=self._method != ResolutionMethod.FAILED
        )

        with self._lock:
            # Add record (with FIFO eviction)
            self.records.append(record)
            if len(self.records) > self.max_records:
                self.records = self.records[-self.max_records:]

            # Update counters
            self._stats['total'] += 1
            if self._method == ResolutionMethod.DOMAIN_SOLVER:
                self._stats['domain_solver'] += 1
            elif self._method == ResolutionMethod.SYMPY_FALLBACK:
                self._stats['sympy_fallback'] += 1
            elif self._method == ResolutionMethod.SYMPY_INTENTIONAL:
                self._stats['sympy_intentional'] += 1
            elif self._method == ResolutionMethod.FAILED:
                self._stats['failed'] += 1
            elif self._method == ResolutionMethod.CACHED:
                self._stats['cached'] += 1

        # Log the record
        log_msg = f"[{self._method.name}] {self._current_operation}"
        if self._current_domain:
            log_msg += f" ({self._current_domain})"
        log_msg += f" in {duration_ms:.1f}ms"
        if self._fallback_reason:
            log_msg += f" - {self._fallback_reason}"

        logger.debug(log_msg)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about computation resolution.

        Returns:
            Dictionary with statistics including:
            - total: Total computations tracked
            - domain_solver_count: Resolved by domain solver
            - sympy_fallback_count: Fell back to SymPy
            - fallback_rate: Percentage falling back to SymPy
            - success_rate: Overall success rate
            - avg_duration_ms: Average computation time
            - fallback_reasons: Most common fallback reasons
        """
        with self._lock:
            total = self._stats['total']
            if total == 0:
                return {
                    'total': 0,
                    'domain_solver_count': 0,
                    'sympy_fallback_count': 0,
                    'fallback_rate': 0.0,
                    'success_rate': 0.0,
                    'avg_duration_ms': 0.0,
                    'fallback_reasons': {}
                }

            # Calculate rates
            domain_success = self._stats['domain_solver']
            sympy_fallback = self._stats['sympy_fallback']
            sympy_intentional = self._stats['sympy_intentional']
            failed = self._stats['failed']
            cached = self._stats['cached']

            fallback_rate = sympy_fallback / total if total > 0 else 0
            success_rate = (total - failed) / total if total > 0 else 0

            # Calculate average duration
            durations = [r.duration_ms for r in self.records]
            avg_duration = sum(durations) / len(durations) if durations else 0

            # Count fallback reasons
            fallback_reasons: Dict[str, int] = {}
            for record in self.records:
                if record.method == ResolutionMethod.SYMPY_FALLBACK and record.fallback_reason:
                    reason = record.fallback_reason
                    fallback_reasons[reason] = fallback_reasons.get(reason, 0) + 1

            # Sort by frequency
            fallback_reasons = dict(
                sorted(fallback_reasons.items(), key=lambda x: x[1], reverse=True)[:10]
            )

            return {
                'total': total,
                'domain_solver_count': domain_success,
                'sympy_fallback_count': sympy_fallback,
                'sympy_intentional_count': sympy_intentional,
                'failed_count': failed,
                'cached_count': cached,
                'fallback_rate': fallback_rate,
                'success_rate': success_rate,
                'avg_duration_ms': round(avg_duration, 2),
                'fallback_reasons': fallback_reasons
            }

    def get_recent_fallbacks(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the N most recent fallback records."""
        with self._lock:
            fallbacks = [
                r.to_dict() for r in self.records
                if r.method == ResolutionMethod.SYMPY_FALLBACK
            ]
            return fallbacks[-n:]

    def get_domain_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get breakdown of resolution methods by domain."""
        with self._lock:
            breakdown: Dict[str, Dict[str, int]] = {}

            for record in self.records:
                domain = record.domain or 'unknown'
                if domain not in breakdown:
                    breakdown[domain] = {
                        'total': 0,
                        'domain_solver': 0,
                        'sympy_fallback': 0,
                        'failed': 0
                    }

                breakdown[domain]['total'] += 1
                if record.method == ResolutionMethod.DOMAIN_SOLVER:
                    breakdown[domain]['domain_solver'] += 1
                elif record.method == ResolutionMethod.SYMPY_FALLBACK:
                    breakdown[domain]['sympy_fallback'] += 1
                elif record.method == ResolutionMethod.FAILED:
                    breakdown[domain]['failed'] += 1

            return breakdown

    def clear(self):
        """Clear all records and reset statistics."""
        with self._lock:
            self.records.clear()
            self._stats = {
                'total': 0,
                'domain_solver': 0,
                'sympy_fallback': 0,
                'sympy_intentional': 0,
                'failed': 0,
                'cached': 0,
            }

    def export_log(self, filepath: str):
        """Export records to JSON file for analysis."""
        with self._lock:
            data = {
                'statistics': self.get_statistics(),
                'domain_breakdown': self.get_domain_breakdown(),
                'records': [r.to_dict() for r in self.records]
            }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Global tracker instance (singleton pattern for convenience)
_global_tracker: Optional[FallbackTracker] = None


def get_tracker() -> FallbackTracker:
    """Get the global fallback tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = FallbackTracker()
    return _global_tracker


def track_computation(operation: str, input_text: str,
                      domain: Optional[str] = None,
                      specialist: Optional[str] = None):
    """
    Convenience decorator/context manager for tracking computations.

    Usage as context manager:
        with track_computation("solve", "x**2 - 4", domain="algebra") as tracker:
            result = solve(...)
            if fallback:
                tracker.mark_fallback("reason")

    Args:
        operation: Operation type
        input_text: Input expression
        domain: Mathematical domain
        specialist: Specialist agent
    """
    return get_tracker().track(operation, input_text, domain, specialist)


def log_fallback(reason: str):
    """Quick function to log a fallback in the current context."""
    tracker = get_tracker()
    tracker.mark_fallback(reason)


def get_fallback_statistics() -> Dict[str, Any]:
    """Get current fallback statistics."""
    return get_tracker().get_statistics()
