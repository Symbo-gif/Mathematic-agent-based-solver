# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0
"""
NATIVE SYMBOLIC MATHEMATICS ENGINE - Backward Compatibility Layer
==================================================================

DEPRECATED: This file has been decomposed into the modular symbolic/ package.

For new code, import from symbolic/ directly:
    from symbo_agentic_reasoners.core.symbolic import Symbol, Integer, parse_expr

This compatibility wrapper will remain indefinitely to support existing code.

Original File: 2,276 lines (decomposed on 2025-12-15)
New Architecture: Supervisor-Specialist pattern in symbolic/ package

This module provides:
- Expression representation (Expr, Symbol, Number, Add, Mul, Pow, Function)
- Expression parsing from strings
- Expression simplification
- Expression evaluation
- LaTeX/Unicode/String output
- Equation solving
- Pattern matching

NO SYMPY DEPENDENCY - This is a standalone mathematical reasoning engine.

Migration Path:
---------------
```python
# OLD (still works - uses this compatibility layer)
from symbo_agentic_reasoners.core.native_symbolic import Symbol, parse_expr

# NEW (recommended - direct import from modular package)
from symbo_agentic_reasoners.core.symbolic import Symbol, parse_expr
```

Package Structure (new modular architecture):
----------------------------------------------
symbolic/
├── __init__.py                     # Public API (backward compatible)
├── symbolic_supervisor.py          # Main coordinator (lazy loading)
├── type_system.py                  # Base Expr, Symbol, Integer, Float, Rational
├── composite_operations.py         # Add, Mul, Pow
├── simplification_engine.py        # Simplification rules
├── function_library.py             # Sin, Cos, Exp, Log, etc.
├── expression_parser.py            # Lexer, Parser
├── convenience_api.py              # symbols(), diff(), simplify()
├── sympy_compatibility.py          # SymPy compatibility layer
└── utils/
    ├── __init__.py
    ├── constants.py                # Mathematical constants
    └── validation.py               # Safety checks
"""

import warnings

# Issue deprecation warning (can be disabled with warnings.filterwarnings)
warnings.warn(
    "native_symbolic.py is a compatibility wrapper. "
    "For new code, use: from symbo_agentic_reasoners.core.symbolic import ...",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the new modular symbolic package
from .symbolic import *

# Explicitly import __all__ to maintain the export list
from .symbolic import __all__

# Version info - mark as compatibility layer
__compatibility_layer__ = True
__migration_date__ = '2025-12-15'
__original_lines__ = 2276
__new_architecture__ = 'supervisor-specialist (symbolic/ package)'
__deprecation_status__ = 'deprecated_but_maintained'
