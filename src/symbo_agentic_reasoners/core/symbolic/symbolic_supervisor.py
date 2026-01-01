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
Symbolic Supervisor - Main Coordinator for Symbolic Operations
===============================================================

This supervisor orchestrates symbolic operations by delegating to specialist modules.
It follows the supervisor-specialist pattern from the calculus package.

Architecture:
-------------
┌─────────────────────────────────────┐
│      Symbolic Supervisor            │
│  (Routing & Coordination Logic)     │
└──────────────┬──────────────────────┘
               │
               ├─ Type System (atomic types)
               ├─ Composite Operations (Add, Mul, Pow)
               ├─ Simplification Engine (rules)
               ├─ Function Library (Sin, Cos, etc.)
               ├─ Expression Parser (string → AST)
               ├─ Convenience API (symbols, diff, simplify)
               └─ SymPy Compatibility (stubs)

Delegation Flow:
---------------
1. User Request → Supervisor
2. Supervisor → Parser (if string input)
3. Supervisor → Appropriate Module
4. Module → Result
5. Supervisor → Formatted Output
"""

import logging
from typing import Union, Tuple, Any

logger = logging.getLogger(__name__)


class SymbolicSupervisor:
    """
    Main supervisor for coordinating symbolic mathematics operations.

    This supervisor follows the supervisor-specialist pattern:
    - Each module is loaded lazily to improve startup time
    - Supervisor routes operations to appropriate modules
    - Modules focus solely on their domain
    - Supervisor handles coordination and error handling

    Attributes:
        parser: Expression parser (string → AST) - lazy loaded
        type_system: Type system module - lazy loaded
        simplification_engine: Simplification rules - lazy loaded
        function_library: Mathematical functions - lazy loaded
        convenience_api: High-level API functions - lazy loaded
        sympy_compat: SymPy compatibility layer - lazy loaded
    """

    def __init__(self):
        """Initialize supervisor with lazy-loaded modules."""
        # Lazy-load modules to improve startup time
        self._parser = None
        self._type_system = None
        self._simplification_engine = None
        self._function_library = None
        self._convenience_api = None
        self._sympy_compat = None

    @property
    def parser(self):
        """Lazy-load expression parser."""
        if self._parser is None:
            from . import expression_parser
            self._parser = expression_parser
        return self._parser

    @property
    def type_system(self):
        """Lazy-load type system."""
        if self._type_system is None:
            from . import type_system
            self._type_system = type_system
        return self._type_system

    @property
    def simplification_engine(self):
        """Lazy-load simplification engine."""
        if self._simplification_engine is None:
            from . import simplification_engine
            self._simplification_engine = simplification_engine
        return self._simplification_engine

    @property
    def function_library(self):
        """Lazy-load function library."""
        if self._function_library is None:
            from . import function_library
            self._function_library = function_library
        return self._function_library

    @property
    def convenience_api(self):
        """Lazy-load convenience API."""
        if self._convenience_api is None:
            from . import convenience_api
            self._convenience_api = convenience_api
        return self._convenience_api

    @property
    def sympy_compat(self):
        """Lazy-load SymPy compatibility layer."""
        if self._sympy_compat is None:
            from . import sympy_compatibility
            self._sympy_compat = sympy_compatibility
        return self._sympy_compat

    # =========================================================================
    # PUBLIC API METHODS
    # =========================================================================

    def parse(self, text: str):
        """Parse string expression to Expr."""
        return self.parser.parse_expr(text)

    def sympify(self, obj: Any):
        """Convert object to Expr."""
        return self.parser.sympify(obj)

    def symbols(self, names: str, **assumptions):
        """Create symbols from string."""
        return self.convenience_api.symbols(names, **assumptions)

    def diff(self, expr, var, n: int = 1):
        """Differentiate expression."""
        return self.convenience_api.diff(expr, var, n)

    def simplify(self, expr):
        """Simplify expression."""
        return self.convenience_api.simplify(expr)

    def expand(self, expr):
        """Expand expression."""
        return self.convenience_api.expand(expr)

    def factor(self, expr):
        """Factor expression."""
        return self.convenience_api.factor(expr)


# =============================================================================
# GLOBAL SINGLETON INSTANCE
# =============================================================================

_supervisor_instance = None


def get_supervisor() -> SymbolicSupervisor:
    """Get global supervisor instance (singleton pattern)."""
    global _supervisor_instance
    if _supervisor_instance is None:
        _supervisor_instance = SymbolicSupervisor()
    return _supervisor_instance


# =============================================================================
# PUBLIC API FUNCTIONS (delegate to supervisor)
# =============================================================================

def parse_expr(text: str):
    """Parse mathematical expression string."""
    return get_supervisor().parse(text)


def sympify(obj: Any):
    """Convert object to Expr."""
    return get_supervisor().sympify(obj)


def symbols(names: str, **assumptions):
    """Create symbols from string."""
    return get_supervisor().symbols(names, **assumptions)


def diff(expr, var, n: int = 1):
    """Differentiate expression."""
    return get_supervisor().diff(expr, var, n)


def simplify(expr):
    """Simplify expression."""
    return get_supervisor().simplify(expr)


def expand(expr):
    """Expand expression."""
    return get_supervisor().expand(expr)


def factor(expr):
    """Factor expression."""
    return get_supervisor().factor(expr)


__all__ = [
    'SymbolicSupervisor',
    'get_supervisor',
    'parse_expr',
    'sympify',
    'symbols',
    'diff',
    'simplify',
    'expand',
    'factor',
]
