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
Solve Result
============

Structured result type for all solver operations.
Provides consistent status reporting, error handling, and diagnostics.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import json


@dataclass
class SolveResult:
    """
    Structured result from a solve operation.

    All public API calls return this type to ensure consistent error handling
    and provide rich diagnostics for debugging.

    Attributes:
        status: "ok" for success, "timeout" for timeout, "error" for failure
        solution: The solution string (if successful)
        error: Error message (if failed)
        diagnostics: Additional information about the solve process

    Example:
        >>> result = solve_expression("x**2 - 4")
        >>> if result.status == "ok":
        ...     print(result.solution)
        >>> else:
        ...     print(f"Failed: {result.error}")
    """

    # Core result
    status: Literal["ok", "timeout", "error"]
    solution: Optional[str] = None
    error: Optional[str] = None

    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    # Timing
    solve_time_ms: float = 0.0

    # Original problem (for batch processing)
    problem: Optional[str] = None

    # Metadata
    domain: Optional[str] = None
    operation: Optional[str] = None
    specialist_used: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Check if the solve was successful."""
        return self.status == "ok"

    @property
    def is_timeout(self) -> bool:
        """Check if the solve timed out."""
        return self.status == "timeout"

    @property
    def is_error(self) -> bool:
        """Check if the solve encountered an error."""
        return self.status == "error"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for serialization.

        Returns:
            Dict containing all result fields
        """
        return {
            "status": self.status,
            "solution": self.solution,
            "error": self.error,
            "solve_time_ms": round(self.solve_time_ms, 2),
            "problem": self.problem,
            "domain": self.domain,
            "operation": self.operation,
            "specialist_used": self.specialist_used,
            "diagnostics": self.diagnostics,
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert result to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def success(
        cls,
        solution: str,
        problem: Optional[str] = None,
        solve_time_ms: float = 0.0,
        **kwargs
    ) -> "SolveResult":
        """
        Create a successful result.

        Args:
            solution: The solution string
            problem: Original problem (optional)
            solve_time_ms: Time taken to solve
            **kwargs: Additional diagnostics

        Returns:
            SolveResult with status="ok"
        """
        return cls(
            status="ok",
            solution=solution,
            problem=problem,
            solve_time_ms=solve_time_ms,
            diagnostics=kwargs.get("diagnostics", {}),
            domain=kwargs.get("domain"),
            operation=kwargs.get("operation"),
            specialist_used=kwargs.get("specialist_used"),
        )

    @classmethod
    def timeout(
        cls,
        problem: Optional[str] = None,
        timeout_sec: float = 0.0,
        **kwargs
    ) -> "SolveResult":
        """
        Create a timeout result.

        Args:
            problem: Original problem (optional)
            timeout_sec: Timeout value that was exceeded
            **kwargs: Additional diagnostics

        Returns:
            SolveResult with status="timeout"
        """
        return cls(
            status="timeout",
            error=f"Operation timed out after {timeout_sec:.1f} seconds",
            problem=problem,
            diagnostics={"timeout_sec": timeout_sec, **kwargs.get("diagnostics", {})},
        )

    @classmethod
    def failure(
        cls,
        error: str,
        problem: Optional[str] = None,
        solve_time_ms: float = 0.0,
        **kwargs
    ) -> "SolveResult":
        """
        Create a failure result.

        Args:
            error: Error message
            problem: Original problem (optional)
            solve_time_ms: Time taken before failure
            **kwargs: Additional diagnostics

        Returns:
            SolveResult with status="error"
        """
        return cls(
            status="error",
            error=error,
            problem=problem,
            solve_time_ms=solve_time_ms,
            diagnostics=kwargs.get("diagnostics", {}),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.status == "ok":
            return f"SolveResult(ok: {self.solution})"
        elif self.status == "timeout":
            return f"SolveResult(timeout: {self.error})"
        else:
            return f"SolveResult(error: {self.error})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"SolveResult(status={self.status!r}, solution={self.solution!r}, "
            f"error={self.error!r}, solve_time_ms={self.solve_time_ms:.2f})"
        )
