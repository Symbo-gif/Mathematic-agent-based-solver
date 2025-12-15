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
Solver Engine - Direct Problem Solving Pipeline
=================================================

BACKWARD COMPATIBILITY LAYER
----------------------------

This file has been decomposed into the solver/ package for better maintainability.
All imports are preserved for backward compatibility.

Original: 1,698 lines (monolithic)
New: Modular solver/ package with 7 focused modules

Migration:
----------
OLD: from symbo_agentic_reasoners.core.solver_engine import SolverEngine
NEW: from symbo_agentic_reasoners.core.solver import SolverEngine

Both imports work identically. The new modular structure is:

solver/
├── __init__.py          - Public API exports
├── result.py            - SolveStatus, SolveResult
├── safety_checker.py    - Expression safety validation
├── router.py            - Specialist routing & lazy loading
├── cache_manager.py     - Result caching
├── solver_core.py       - SolverEngine class
├── specialized_solvers.py - Specialized solving functions
└── api.py               - get_solver_engine, solve

All functionality is preserved. This file simply re-exports from the new package.
"""

# Re-export everything from the new modular solver package
from symbo_agentic_reasoners.core.solver import (
    # Primary API
    SolverEngine,
    get_solver_engine,
    solve,
    solve_expression,

    # Result types
    SolveStatus,
    SolveResult,

    # Safety checks
    check_expression_safety,
    MAX_EXPRESSION_DEPTH,
    MAX_EXPRESSION_LENGTH,

    # Router (advanced)
    SpecialistRouter,
    get_specialist_key,
    create_specialist,

    # Cache (advanced)
    ResultCache,

    # Specialized solvers (advanced)
    solve_diophantine,
    solve_determinant,
    solve_limit_native,
    solve_nt_series,
    solve_sum_of_cubes,
    solve_quaternary_quadratic,
    solve_mordell_curve,
    bounded_diophantine_search_native,
    compute_determinant_native,
)

__all__ = [
    # Primary API
    'SolverEngine',
    'get_solver_engine',
    'solve',
    'solve_expression',

    # Result types
    'SolveStatus',
    'SolveResult',

    # Safety checks
    'check_expression_safety',
    'MAX_EXPRESSION_DEPTH',
    'MAX_EXPRESSION_LENGTH',

    # Router (advanced)
    'SpecialistRouter',
    'get_specialist_key',
    'create_specialist',

    # Cache (advanced)
    'ResultCache',

    # Specialized solvers (advanced)
    'solve_diophantine',
    'solve_determinant',
    'solve_limit_native',
    'solve_nt_series',
    'solve_sum_of_cubes',
    'solve_quaternary_quadratic',
    'solve_mordell_curve',
    'bounded_diophantine_search_native',
    'compute_determinant_native',
]

# Migration notice
import warnings

def _show_migration_notice():
    """Show one-time migration notice (non-intrusive)."""
    msg = (
        "solver_engine.py has been decomposed into solver/ package. "
        "Consider updating imports: "
        "from symbo_agentic_reasoners.core.solver import SolverEngine"
    )
    # Only show in debug mode
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(msg)

# Show notice on first import (debug level only)
_show_migration_notice()
