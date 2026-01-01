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
Solver Result Types
===================

Defines the status enum and result dataclass for solver operations.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class SolveStatus(Enum):
    """Status of a solve operation."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    NO_SPECIALIST = "no_specialist"


@dataclass
class SolveResult:
    """Result of a solve operation."""
    status: SolveStatus
    result: Optional[str] = None
    sympy_result: Optional[Any] = None
    problem_type: str = ""
    domain: str = ""
    operation: str = ""
    specialist_used: str = ""
    solve_time_ms: float = 0.0
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
            'specialist_used': self.specialist_used,
            'solve_time_ms': round(self.solve_time_ms, 2),
            'error': self.error
        }
