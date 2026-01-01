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
Native Symbolic Mathematics Engine - Modular Supervisor-Specialist Architecture
================================================================================

This package provides pure Python symbolic mathematics WITHOUT SymPy dependency.
It has been decomposed from a monolithic 2,276-line file into a modular
supervisor-specialist architecture for better maintainability and testability.

Public API (Backward Compatible):
----------------------------------
```python
from symbo_agentic_reasoners.core.symbolic import (
    # Type system
    Expr, Symbol, Integer, Float, Rational,
    Add, Mul, Pow, Function,

    # Functions
    Sin, Cos, Tan, Exp, Log, Sqrt, Abs, Sign,
    sin, cos, tan, exp, log, sqrt,

    # Parsing
    parse_expr, sympify, symbols,

    # Operations
    diff, simplify, expand, factor,

    # Constants
    pi, E, I, oo,

    # Compatibility
    Eq, SympifyError,
)

x, y = symbols('x y')
expr = x**2 + 2*x*y + y**2
expanded = expand((x + y)**2)
derivative = diff(expr, x)
```

Advanced API (Specialist Access):
----------------------------------
```python
from symbo_agentic_reasoners.core.symbolic import SymbolicSupervisor

supervisor = SymbolicSupervisor()
supervisor.simplification_engine.expand_expression(expr)
```

Architecture:
-------------
- symbolic_supervisor.py: Main coordinator (routing & delegation)
- type_system.py: Base Expr, Symbol, Integer, Float, Rational
- composite_operations.py: Add, Mul, Pow
- simplification_engine.py: Simplification rules and strategies
- function_library.py: Sin, Cos, Exp, Log, etc.
- expression_parser.py: String → AST parser
- convenience_api.py: High-level API functions
- sympy_compatibility.py: SymPy compatibility layer
- utils/: Constants and validation

Migration Status:
-----------------
COMPLETE: All functionality extracted from native_symbolic.py
The original file now serves as a backward compatibility wrapper.
See native_symbolic.py for migration details.
"""

# Primary public API (backward compatible with native_symbolic.py)
from .symbolic_supervisor import (
    SymbolicSupervisor,
    get_supervisor,
)

# Type system
from .type_system import (
    Expr,
    Symbol,
    Integer,
    Float,
    Rational,
    _ensure_expr,
)

# Composite operations
from .composite_operations import (
    Add,
    Mul,
    Pow,
)

# Function library
from .function_library import (
    Function,
    Sin, Cos, Tan,
    Exp, Log, Sqrt,
    Abs, Sign,
    GenericFunction,
    Derivative,
)

# Convenience API
from .convenience_api import (
    symbols,
    diff,
    simplify,
    expand,
    factor,
)

# Parsing
from .expression_parser import (
    parse_expr,
    sympify,
    Lexer,
    Parser,
)

# SymPy compatibility
from .sympy_compatibility import (
    Eq,
    SympifyError,
    pi, E, I, oo,
    sin, cos, tan, exp, log, sqrt,
    preorder_traversal,
    together,
    fraction,
    arg,
    expand_complex,
    solve,
    groebner,
    core,
)

# Utils
from .utils.constants import MathConstant
from .utils.validation import (
    MAX_EXPRESSION_DEPTH,
    MAX_EXPRESSION_LENGTH,
    MAX_TERM_COUNT,
    check_expression_depth,
    check_expression_length,
    check_term_count,
    validate_expression,
)


__all__ = [
    # Supervisor
    'SymbolicSupervisor',
    'get_supervisor',

    # Type system
    'Expr', 'Symbol', 'Integer', 'Float', 'Rational',
    'Add', 'Mul', 'Pow', 'Function',
    '_ensure_expr',

    # Functions
    'Sin', 'Cos', 'Tan', 'Exp', 'Log', 'Sqrt', 'Abs', 'Sign',
    'GenericFunction', 'Derivative',
    'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',

    # Operations
    'symbols', 'diff', 'simplify', 'expand', 'factor',

    # Parsing
    'parse_expr', 'sympify', 'Lexer', 'Parser',

    # Compatibility
    'Eq', 'SympifyError',
    'preorder_traversal', 'together', 'fraction',
    'arg', 'expand_complex', 'solve', 'groebner', 'core',

    # Constants
    'pi', 'E', 'I', 'oo',
    'MathConstant',

    # Validation
    'MAX_EXPRESSION_DEPTH',
    'MAX_EXPRESSION_LENGTH',
    'MAX_TERM_COUNT',
    'check_expression_depth',
    'check_expression_length',
    'check_term_count',
    'validate_expression',
]

# Version info
__version__ = '2.0.0-alpha'  # Major version bump due to architecture change
__architecture__ = 'supervisor-specialist'
__migration_status__ = 'complete'
__original_file__ = 'native_symbolic.py (2,276 lines)'
__migration_date__ = '2025-12-15'
