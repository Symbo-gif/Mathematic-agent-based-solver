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
NATIVE CALCULUS ENGINE - Backward Compatibility Layer
======================================================

DEPRECATED: This file has been decomposed into the modular calculus/ package.

For new code, import from calculus/ directly:
    from symbo_agentic_reasoners.core.calculus import differentiate, integrate, limit

This compatibility wrapper will remain indefinitely to support existing code.

Original File: 13,311 lines (decomposed on 2025-12-15)
New Architecture: Supervisor-Specialist pattern in calculus/ package

Migration Path:
---------------
```python
# OLD (still works - uses this compatibility layer)
from symbo_agentic_reasoners.core.native_calculus import differentiate, integrate

# NEW (recommended - direct import from modular package)
from symbo_agentic_reasoners.core.calculus import differentiate, integrate
```

Package Structure (new modular architecture):
----------------------------------------------
calculus/
├── __init__.py                          # Public API (backward compatible)
├── calculus_supervisor.py               # Main coordinator (routing & delegation)
├── ast_types.py                         # Internal AST representation
├── expression_parser.py                 # String → AST parser
├── validation.py                        # Safety checks (depth & length limits)
├── calculus_utils.py                    # Shared utility functions
├── differentiation_specialist.py        # Differentiation engine
├── integration_specialist.py            # Indefinite integration engine
├── definite_integration_specialist.py   # Definite integration engine (5,130 lines)
├── limit_specialist.py                  # Limit evaluation engine
├── vector_calculus.py                   # Vector calculus operations
└── series_specialist.py                 # Series summation
"""

import warnings

# Issue deprecation warning (can be disabled with warnings.filterwarnings)
warnings.warn(
    "native_calculus.py is a compatibility wrapper. "
    "For new code, use: from symbo_agentic_reasoners.core.calculus import ...",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the new modular calculus package
from .calculus import *

# Explicitly import __all__ to maintain the export list
from .calculus import __all__

# Additional exports for full backward compatibility
from .calculus import (
    # Main API
    differentiate,
    integrate,
    limit,
    native_derivative,

    # Supervisor
    CalculusSupervisor,
    get_supervisor,

    # Specialist Engines
    DifferentiationEngine,
    IntegrationEngine,
    LimitEngine,

    # AST types
    Expr,
    Num,
    Sym,
    Add,
    Mul,
    Pow,
    Neg,
    Func,

    # Definite integration
    definite_integrate,
    _check_log_singularity,
    _try_gamma_power_integral,

    # Vector calculus
    gradient,
    divergence,
    curl,

    # Series
    series_sum,

    # Utilities
    native_trig_simplify,
)

# Version info - mark as compatibility layer
__compatibility_layer__ = True
__migration_date__ = '2025-12-15'
__original_lines__ = 13311
__new_architecture__ = 'supervisor-specialist (calculus/ package)'
__deprecation_status__ = 'deprecated_but_maintained'
