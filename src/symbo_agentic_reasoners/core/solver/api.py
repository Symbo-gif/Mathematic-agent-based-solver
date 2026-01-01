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
Solver API
==========

Public API for the solver engine. Provides singleton access and convenience functions.
"""

from typing import Optional
from .solver_core import SolverEngine
from .result import SolveResult

# Singleton engine instance
_engine: Optional[SolverEngine] = None


def get_solver_engine(coordinator=None) -> SolverEngine:
    """
    Get or create the global solver engine.

    Args:
        coordinator: Optional ResourceCoordinator for hardware-aware scheduling

    Returns:
        SolverEngine instance (singleton)
    """
    global _engine
    if _engine is None:
        _engine = SolverEngine(resource_coordinator=coordinator)
    return _engine


def solve(problem: str) -> SolveResult:
    """
    Convenience function to solve a problem using the global engine.

    Args:
        problem: Natural language or mathematical expression

    Returns:
        SolveResult with solution or error
    """
    return get_solver_engine().solve(problem)


def solve_expression(expr_str: str, operation: str = 'compute', variable: str = 'x') -> SolveResult:
    """
    Convenience function to solve a direct expression using the global engine.

    Args:
        expr_str: SymPy-compatible expression string
        operation: Operation to perform (derivative, integral, solve, factor, etc.)
        variable: Variable for calculus operations

    Returns:
        SolveResult with solution
    """
    return get_solver_engine().solve_expression(expr_str, operation, variable)
