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
Native Calculus Engine - Modular Supervisor-Specialist Architecture
====================================================================

This package provides pure Python symbolic calculus WITHOUT SymPy dependency.
It has been decomposed from a monolithic 13,330-line file into a modular
supervisor-specialist architecture for better maintainability and testability.

Public API (Backward Compatible):
----------------------------------
```python
from symbo_agentic_reasoners.core.calculus import differentiate, integrate, limit

# Differentiation
success, result, method = differentiate("x**2 + sin(x)", "x")
# result: "2*x + cos(x)"

# Integration
success, result, method = integrate("x**2", "x")
# result: "x**3/3"

# Limits
success, result, method = limit("sin(x)/x", "x", "0")
# result: "1"
```

Advanced API (Specialist Access):
----------------------------------
```python
from symbo_agentic_reasoners.core.calculus import CalculusSupervisor
from symbo_agentic_reasoners.core.calculus.ast_types import Expr, Num, Sym

supervisor = CalculusSupervisor()

# Access individual specialists
diff_result = supervisor.diff_specialist.differentiate(expr, "x")
int_result = supervisor.int_specialist.integrate(expr, "x")
limit_result = supervisor.limit_specialist.limit(expr, "x", "0")
```

Architecture:
-------------
- calculus_supervisor.py: Main coordinator (routing & delegation)
- ast_types.py: Internal AST representation (Num, Sym, Add, Mul, Pow, Func)
- expression_parser.py: String → AST parser
- validation.py: Safety checks (depth & length limits)
- calculus_utils.py: Shared utility functions (EXTRACTED)
- differentiation_specialist.py: Differentiation engine (EXTRACTED)
- integration_specialist.py: Integration engine (EXTRACTED)
- limit_specialist.py: Limit evaluation engine (EXTRACTED)
- vector_calculus.py: Vector calculus operations (EXTRACTED)
- series_specialist.py: Series summation (EXTRACTED)
- special_integrals_specialist.py: Special patterns (TODO)

Migration Status:
-----------------
EXTRACTED (complete):
- differentiation_specialist.py: Full differentiation engine
- integration_specialist.py: Indefinite integration engine
- limit_specialist.py: Limit evaluation engine with all special cases
- vector_calculus.py: gradient, divergence, curl
- series_specialist.py: series_sum with classic series patterns
- calculus_utils.py: native_trig_simplify, _evaluate_at_numeric, helpers
- definite_integration_specialist.py: definite_integrate + 61 helpers (4933 lines)

ALL EXTRACTIONS COMPLETE - native_calculus.py is no longer needed!
See CALCULUS_DECOMPOSITION_PLAN.md for full details.
"""

# Primary public API (backward compatible with native_calculus.py)
from .calculus_supervisor import (
    differentiate,
    integrate,
    limit,
    native_derivative,  # Alias
    CalculusSupervisor,
    get_supervisor,
)

# AST types for advanced users
from .ast_types import (
    Expr,
    Num,
    Sym,
    Add,
    Mul,
    Pow,
    Neg,
    Func,
    num,
    sym,
    add,
    mul,
    power,
    neg,
    func,
    PI,
    E,
)

# Parser for advanced users
from .expression_parser import ExprParser

# Validation for advanced users
from .validation import check_expression_safety, MAX_EXPRESSION_DEPTH, MAX_EXPRESSION_LENGTH

# Specialist engines for advanced users
from .differentiation_specialist import DifferentiationEngine
from .integration_specialist import IntegrationEngine
from .limit_specialist import LimitEngine

# Vector calculus operations
from .vector_calculus import gradient, divergence, curl

# Functions from limit_specialist.py
from .limit_specialist import (
    solve_polynomial,
    solve_system_native,
    factor_polynomial,
    expand_expression,
    taylor_series,
    solve_ode_native,
    definite_integrate_2d,
    native_limit,
    _try_limit_with_assumptions,
)

# Functions from series_specialist.py
from .series_specialist import series_sum

# Functions from calculus_utils.py
from .calculus_utils import native_trig_simplify

# Functions from definite_integration_specialist.py (EXTRACTED from native_calculus.py)
# These handle definite integration with special patterns and singularity detection
from .definite_integration_specialist import (
    definite_integrate,
    _check_log_singularity,
    _try_gamma_power_integral,
)


__all__ = [
    # Main API
    'differentiate',
    'integrate',
    'limit',
    'native_derivative',

    # Supervisor
    'CalculusSupervisor',
    'get_supervisor',

    # Specialist Engines
    'DifferentiationEngine',
    'IntegrationEngine',
    'LimitEngine',

    # Functions from limit_specialist.py
    'solve_polynomial',
    'solve_system_native',
    'factor_polynomial',
    'expand_expression',
    'taylor_series',
    'solve_ode_native',
    'definite_integrate_2d',
    'native_limit',
    '_try_limit_with_assumptions',

    # Vector calculus operations
    'gradient',
    'divergence',
    'curl',

    # Functions from series_specialist.py
    'series_sum',

    # Functions from calculus_utils.py
    'native_trig_simplify',

    # Functions from native_calculus.py (temporary fallback)
    'definite_integrate',
    '_check_log_singularity',

    # AST Types
    'Expr',
    'Num',
    'Sym',
    'Add',
    'Mul',
    'Pow',
    'Neg',
    'Func',

    # AST Constructors
    'num',
    'sym',
    'add',
    'mul',
    'power',
    'neg',
    'func',

    # Constants
    'PI',
    'E',

    # Parser
    'ExprParser',

    # Validation
    'check_expression_safety',
    'MAX_EXPRESSION_DEPTH',
    'MAX_EXPRESSION_LENGTH',
]

# Version info
__version__ = '2.0.0-alpha'  # Major version bump due to architecture change
__architecture__ = 'supervisor-specialist'
__migration_status__ = 'in_progress'
