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
Solver Engine - Modular Problem Solving Pipeline
=================================================

Production-grade solver that directly dispatches problems to specialist agents,
bypassing the full orchestrator's verification polling for immediate results.

This provides a streamlined solve path:
    Raw Input -> Parse -> Classify -> Route -> Specialist -> Result

Architecture (Decomposed from 1,698-line monolithic solver_engine.py):
-----------------------------------------------------------------------

Package Structure:
- result.py: SolveStatus enum, SolveResult dataclass
- safety_checker.py: Expression safety validation (depth & length limits)
- router.py: Specialist routing and lazy loading
- cache_manager.py: Result caching (placeholder for future)
- solver_core.py: Main SolverEngine class (streamlined)
- specialized_solvers.py: Specialized solving functions (diophantine, determinant, etc.)
- api.py: Public API (get_solver_engine, solve functions)

Backward Compatibility:
-----------------------
All imports from the original solver_engine.py are preserved:

```python
# Original import (still works)
from symbo_agentic_reasoners.core.solver_engine import SolverEngine, solve

# New modular import (same functionality)
from symbo_agentic_reasoners.core.solver import SolverEngine, solve
```

Public API:
-----------
```python
from symbo_agentic_reasoners.core.solver import get_solver_engine, solve

# Get singleton engine
engine = get_solver_engine()

# Solve a problem
result = solve("differentiate x^2 + 3x")
print(result.result)  # "2*x + 3"
print(result.status)  # SolveStatus.SUCCESS

# Direct expression solving
result = engine.solve_expression("x**2 + 3*x", operation="derivative", variable="x")
```

Features:
---------
- Lazy loading of specialists (minimal resource usage)
- Timeout protection via Watchdog
- Expression safety checks (prevents DoS)
- Environment variable storage (for multi-step problems)
- Native mathematical reasoning (NO SYMPY)
- Health checks and statistics

Migration Status:
-----------------
COMPLETE: All components extracted and functional
- Core solver engine
- Specialist routing
- Safety validation
- Result types
- Public API preserved
"""

# Result types
from .result import SolveStatus, SolveResult

# Core engine
from .solver_core import SolverEngine

# Public API functions
from .api import get_solver_engine, solve, solve_expression

# Safety checks (for advanced users)
from .safety_checker import (
    check_expression_safety,
    MAX_EXPRESSION_DEPTH,
    MAX_EXPRESSION_LENGTH
)

# Router (for advanced users)
from .router import SpecialistRouter, get_specialist_key, create_specialist

# Cache manager (for advanced users)
from .cache_manager import ResultCache

# Specialized solvers (for advanced users)
from .specialized_solvers import (
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
    # Primary API (most commonly used)
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

# Version info
__version__ = '2.0.0'
__architecture__ = 'modular'
__migration_status__ = 'complete'
__original_file__ = 'solver_engine.py (1,698 lines)'
__decomposition_date__ = '2025-12-15'
