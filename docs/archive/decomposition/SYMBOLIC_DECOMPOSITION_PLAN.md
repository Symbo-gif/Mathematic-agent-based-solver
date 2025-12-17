# Native Symbolic Mathematics Decomposition Plan

## Executive Summary

This document provides a detailed plan to decompose `native_symbolic.py` (2,276 lines) from a monolithic file into a modular supervisor-specialist architecture following the proven pattern established in the `calculus/` package.

**Complexity Assessment**: MODERATE
- **Current Structure**: Single monolithic file
- **Target Structure**: Modular package with 8-10 specialist modules
- **Migration Risk**: LOW (clear separation of concerns, well-defined interfaces)
- **Backward Compatibility**: CRITICAL (must maintain identical public API)

---

## Script Analysis: native_symbolic.py

### Current Structure Issues

1. **Single Responsibility Violation**: One file handles 7 distinct domains:
   - Base expression classes and type system (lines 39-355)
   - Atomic expressions: Symbol, Integer, Float, Rational (lines 357-719)
   - Composite expressions: Add, Mul, Pow (lines 721-1324)
   - Mathematical functions (Sin, Cos, Tan, Exp, Log, etc.) (lines 1326-1564)
   - Expression parsing (Lexer, Parser) (lines 1566-1925)
   - Convenience/utility functions (lines 1927-2067)
   - SymPy compatibility layer (lines 2069-2276)

2. **Testing Complexity**: Monolithic structure requires complex mocking
   - Parser changes can break simplification
   - Type system changes affect all operations
   - No isolated testing of simplification rules

3. **Change Frequency Conflicts**: Different parts evolve at different rates:
   - Core types (stable) mixed with parsing logic (frequently updated)
   - Simplification rules (frequently extended) mixed with base classes (rarely changed)

4. **Difficult to Extend**:
   - Adding new functions requires modifying multiple sections
   - Pattern matching rules scattered throughout
   - No clear extension points for custom operators

### Functional Analysis

#### Line-by-Line Breakdown

| Lines | Component | Responsibility | Size | Complexity |
|-------|-----------|---------------|------|------------|
| 39-355 | Base Expression System | Abstract base class, type properties, operators | 317 | HIGH |
| 357-443 | Symbol | Symbolic variables | 87 | LOW |
| 444-548 | Integer | Integer numbers | 105 | LOW |
| 550-623 | Float | Floating point numbers | 74 | LOW |
| 624-719 | Rational | Rational numbers (fractions) | 96 | LOW |
| 721-961 | Add | Addition/subtraction operations | 241 | VERY HIGH |
| 963-1162 | Mul | Multiplication/division operations | 200 | VERY HIGH |
| 1164-1324 | Pow | Power/exponentiation operations | 161 | HIGH |
| 1326-1564 | Functions | Sin, Cos, Tan, Exp, Log, Sqrt, Abs, Sign | 239 | MEDIUM |
| 1566-1662 | Lexer | Tokenization of mathematical strings | 97 | MEDIUM |
| 1700-1838 | Parser | Recursive descent parser | 139 | HIGH |
| 1840-1906 | Generic Functions | Unknown function handling, derivatives | 67 | LOW |
| 1908-1934 | Parsing API | parse_expr, sympify wrappers | 27 | LOW |
| 1936-2067 | Convenience Functions | symbols, diff, simplify, expand, factor | 132 | MEDIUM |
| 2069-2276 | SymPy Compatibility | Stubs and compatibility layer | 208 | LOW |

#### Dependency Graph

```
Base Expression (Expr)
  ├── Atomic Types (Symbol, Integer, Float, Rational)
  │   └── Used by: Composite types, Functions, Parser
  │
  ├── Composite Types (Add, Mul, Pow)
  │   ├── Depends on: Atomic types, simplification rules
  │   └── Used by: Functions, Parser, Convenience functions
  │
  ├── Functions (Sin, Cos, Tan, etc.)
  │   ├── Depends on: Composite types
  │   └── Used by: Parser
  │
  ├── Parsing System (Lexer, Parser)
  │   ├── Depends on: All expression types
  │   └── Used by: Public API
  │
  ├── Simplification Engine
  │   ├── Distributed across: Add, Mul, Pow
  │   ├── Implements: Pattern matching, rule application
  │   └── Uses: Pythagorean identity, like-term combining, power laws
  │
  └── Public API (symbols, diff, simplify, expand, factor)
      └── Depends on: All components
```

#### Data Flow Analysis

```
String Input → Lexer → Tokens → Parser → AST → Simplification → Output
                                            ↓
                                    Type System (Expr, Symbol, etc.)
                                            ↓
                                    Operations (Add, Mul, Pow)
                                            ↓
                                    Simplification Rules
```

---

## Proposed Agent Team: Symbolic Mathematics

### Supervisor: symbolic-supervisor

**Purpose**: Route symbolic math operations to appropriate specialist engines
**Delegates to**:
- type-system-specialist
- simplification-specialist
- parsing-specialist
- function-specialist
- compatibility-specialist

**Decision Logic**:
```python
def process_operation(self, operation: str, expr: Any, **kwargs):
    """Route symbolic operations to specialists."""

    # Step 1: Ensure expression is parsed
    if isinstance(expr, str):
        expr = self.parsing_specialist.parse(expr)

    # Step 2: Route to appropriate specialist
    if operation == 'simplify':
        return self.simplification_specialist.simplify(expr)
    elif operation == 'expand':
        return self.simplification_specialist.expand(expr)
    elif operation == 'factor':
        return self.simplification_specialist.factor(expr)
    elif operation == 'diff':
        var = kwargs.get('var')
        return self.differentiation_specialist.differentiate(expr, var)
    elif operation == 'subs':
        substitutions = kwargs.get('substitutions')
        return expr.subs(substitutions)
    elif operation == 'evalf':
        precision = kwargs.get('precision', 15)
        return expr.evalf(precision)
    else:
        raise ValueError(f"Unknown operation: {operation}")
```

### Specialists

#### 1. type-system-specialist

**File**: `type_system.py`
**Lines to Extract**: 39-355, 357-719
**Purpose**: Core type hierarchy and atomic expressions
**Input**: Type construction requests
**Output**: Typed expression objects
**Key Functions**:
- Base `Expr` class with abstract methods
- Type-checking properties (is_Add, is_Mul, is_number, etc.)
- Operator overloading (__add__, __mul__, __pow__, etc.)
- Atomic types: `Symbol`, `Integer`, `Float`, `Rational`
- Type coercion: `_ensure_expr()`

**Interface**:
```python
class TypeSystem:
    """Manages the symbolic type hierarchy."""

    def create_symbol(self, name: str, **assumptions) -> Symbol:
        """Create a symbolic variable."""

    def create_number(self, value: Union[int, float, Fraction]) -> Expr:
        """Create appropriate numeric type (Integer/Float/Rational)."""

    def ensure_expr(self, obj: Any) -> Expr:
        """Convert Python objects to Expr."""

    def get_base_class(self) -> Type[Expr]:
        """Return the base Expr class."""
```

#### 2. composite-ops-specialist

**File**: `composite_operations.py`
**Lines to Extract**: 721-1324
**Purpose**: Composite expression types (Add, Mul, Pow)
**Input**: Expression components to combine
**Output**: Composite expression objects
**Key Functions**:
- `Add` class with simplification
- `Mul` class with simplification
- `Pow` class with simplification
- Operator-specific simplification rules

**Interface**:
```python
class CompositeOperations:
    """Manages composite expression construction."""

    def create_add(self, *args: Expr) -> Expr:
        """Create addition expression with auto-simplification."""

    def create_mul(self, *args: Expr) -> Expr:
        """Create multiplication expression with auto-simplification."""

    def create_pow(self, base: Expr, exp: Expr) -> Expr:
        """Create power expression with auto-simplification."""
```

#### 3. simplification-specialist

**File**: `simplification_engine.py`
**Lines to Extract**: Simplification logic from Add (779-923), Mul (1043-1098), Pow (1261-1295), plus expand (1980-2067), factor (2144-2192)
**Purpose**: Advanced simplification and transformation rules
**Input**: Expression to simplify
**Output**: Simplified expression
**Key Functions**:
- Pattern matching (Pythagorean identity)
- Like-term combining
- Power law application
- Expand (polynomial expansion)
- Factor (algebraic factorization)

**Interface**:
```python
class SimplificationEngine:
    """Advanced simplification strategies."""

    def simplify(self, expr: Expr) -> Expr:
        """Apply all simplification rules."""

    def expand(self, expr: Expr) -> Expr:
        """Expand polynomial expressions."""

    def factor(self, expr: Expr) -> Expr:
        """Factor algebraic expressions."""

    def combine_like_terms(self, terms: List[Expr]) -> Expr:
        """Combine terms with same base."""

    def apply_trig_identities(self, expr: Expr) -> Expr:
        """Apply trigonometric identities."""
```

#### 4. function-specialist

**File**: `function_library.py`
**Lines to Extract**: 1326-1564, 1840-1906
**Purpose**: Mathematical function definitions
**Input**: Function name and arguments
**Output**: Function expression object
**Key Functions**:
- Base `Function` class
- Standard functions: Sin, Cos, Tan, Exp, Log, Sqrt, Abs, Sign
- Generic function support
- Derivative computation for each function

**Interface**:
```python
class FunctionLibrary:
    """Mathematical function registry."""

    FUNCTION_CLASSES = {
        'sin': Sin, 'cos': Cos, 'tan': Tan,
        'exp': Exp, 'log': Log, 'sqrt': Sqrt,
        'abs': Abs, 'sign': Sign,
    }

    def create_function(self, name: str, *args: Expr) -> Function:
        """Create function expression."""

    def register_function(self, name: str, func_class: Type[Function]):
        """Register custom function type."""

    def get_derivative(self, func: Function, var: Symbol) -> Expr:
        """Get derivative of function."""
```

#### 5. parsing-specialist

**File**: `expression_parser.py`
**Lines to Extract**: 1566-1838, 1908-1934
**Purpose**: Parse string expressions into AST
**Input**: String expression
**Output**: Expr object
**Key Functions**:
- Lexer (tokenization)
- Parser (recursive descent)
- parse_expr() API
- sympify() wrapper

**Interface**:
```python
class ExpressionParser:
    """Parse mathematical strings into expressions."""

    def parse(self, text: str) -> Expr:
        """Parse string expression to Expr."""

    def tokenize(self, text: str) -> List[Token]:
        """Tokenize expression string."""

    def sympify(self, obj: Any) -> Expr:
        """Convert object to Expr (compatibility)."""
```

#### 6. convenience-api-specialist

**File**: `convenience_api.py`
**Lines to Extract**: 1936-2067
**Purpose**: High-level convenience functions
**Input**: Various (depends on function)
**Output**: Processed expressions
**Key Functions**:
- symbols() - create multiple symbols
- diff() - differentiation wrapper
- simplify() - simplification wrapper
- expand() - expansion wrapper
- factor() - factorization wrapper

**Interface**:
```python
class ConvenienceAPI:
    """High-level user-facing functions."""

    def symbols(self, names: str, **assumptions) -> Union[Symbol, Tuple[Symbol, ...]]:
        """Create symbols from string."""

    def diff(self, expr: Union[Expr, str], var: Union[Symbol, str], n: int = 1) -> Expr:
        """Differentiate expression."""

    def simplify(self, expr: Union[Expr, str]) -> Expr:
        """Simplify expression."""
```

#### 7. sympy-compatibility-specialist

**File**: `sympy_compatibility.py`
**Lines to Extract**: 2069-2276
**Purpose**: SymPy API compatibility layer
**Input**: SymPy-style calls
**Output**: Native equivalents
**Key Functions**:
- Eq class (equations)
- Compatibility stubs (preorder_traversal, together, fraction, etc.)
- Constants (pi, E, I, oo)
- Module structure stubs (core.relational)

**Interface**:
```python
class SympyCompatibility:
    """SymPy API compatibility layer."""

    def create_equation(self, lhs: Expr, rhs: Expr = None) -> Eq:
        """Create equation object."""

    def get_constant(self, name: str) -> Expr:
        """Get mathematical constant."""

    def is_compatible_call(self, func_name: str) -> bool:
        """Check if function has SymPy compatibility."""
```

---

## File Structure

```
src/symbo_agentic_reasoners/core/symbolic/
├── __init__.py                          # Public API (backward compatible)
├── README.md                            # Documentation
├── symbolic_supervisor.py               # Main coordinator
│
├── type_system.py                       # Base Expr, Symbol, Integer, Float, Rational
├── composite_operations.py              # Add, Mul, Pow
├── simplification_engine.py             # Simplification rules and strategies
├── function_library.py                  # Sin, Cos, Exp, Log, etc.
├── expression_parser.py                 # Lexer, Parser
├── convenience_api.py                   # symbols(), diff(), simplify()
├── sympy_compatibility.py               # SymPy compatibility layer
│
└── utils/
    ├── __init__.py
    ├── constants.py                     # MathConstant, pi, E, I, oo
    └── validation.py                    # Expression safety checks
```

### Module Dependencies

```
symbolic_supervisor
  ├── type_system (no dependencies)
  ├── composite_operations → type_system
  ├── simplification_engine → type_system, composite_operations
  ├── function_library → type_system, composite_operations
  ├── expression_parser → all above
  ├── convenience_api → all above
  └── sympy_compatibility → all above
```

---

## Migration Strategy

### Phase 1: Foundation (Week 1)
**Goal**: Extract stable, low-dependency components

1. **Create package structure**
   ```bash
   mkdir -p src/symbo_agentic_reasoners/core/symbolic/utils
   touch src/symbo_agentic_reasoners/core/symbolic/__init__.py
   touch src/symbo_agentic_reasoners/core/symbolic/README.md
   ```

2. **Extract constants and validation**
   - Create `utils/constants.py` (lines 39-53, 2247-2254)
   - Create `utils/validation.py` (new - add expression safety checks)
   - No dependencies, easy to test

3. **Extract type system**
   - Create `type_system.py` (lines 39-355, 357-719)
   - Includes: Expr base class, Symbol, Integer, Float, Rational
   - Only depends on constants
   - Test: Can create symbols and numbers

4. **Create supervisor skeleton**
   - Create `symbolic_supervisor.py` with basic routing
   - Implement lazy loading pattern from calculus
   - Test: Can route to type_system

### Phase 2: Core Operations (Week 2)
**Goal**: Extract composite operations and basic simplification

5. **Extract composite operations**
   - Create `composite_operations.py` (lines 721-1324)
   - Includes: Add, Mul, Pow classes
   - Depends on: type_system
   - Test: Can create and simplify composite expressions

6. **Extract simplification engine**
   - Create `simplification_engine.py`
   - Extract simplification logic from Add.simplify(), Mul.simplify(), Pow.simplify()
   - Extract expand() and factor() functions
   - Depends on: type_system, composite_operations
   - Test: Pattern matching, like-term combining, Pythagorean identity

### Phase 3: Functions and Parsing (Week 3)
**Goal**: Extract function library and expression parsing

7. **Extract function library**
   - Create `function_library.py` (lines 1326-1564, 1840-1906)
   - Includes: Function base class, Sin, Cos, Tan, Exp, Log, etc.
   - Depends on: type_system, composite_operations
   - Test: Function creation and differentiation

8. **Extract expression parser**
   - Create `expression_parser.py` (lines 1566-1838, 1908-1934)
   - Includes: Lexer, Parser, parse_expr(), sympify()
   - Depends on: ALL above (needs to construct all types)
   - Test: Parse complex expressions

### Phase 4: API and Compatibility (Week 4)
**Goal**: Complete migration with public API and compatibility layer

9. **Extract convenience API**
   - Create `convenience_api.py` (lines 1936-2067)
   - Includes: symbols(), diff(), simplify(), expand(), factor()
   - Depends on: ALL above
   - Test: High-level API functions

10. **Extract SymPy compatibility**
    - Create `sympy_compatibility.py` (lines 2069-2276)
    - Includes: Eq, stubs, constants
    - Depends on: ALL above
    - Test: SymPy-style code works

11. **Complete supervisor integration**
    - Wire all specialists into supervisor
    - Implement delegation logic
    - Test: End-to-end operations

12. **Public API finalization**
    - Complete `__init__.py` with backward-compatible exports
    - Ensure native_symbolic.py can be replaced
    - Test: All existing code works unchanged

---

## Testing Strategy

### Unit Tests (Per Specialist)

```python
# tests/test_symbolic_type_system.py
def test_symbol_creation():
    ts = TypeSystem()
    x = ts.create_symbol('x')
    assert x.name == 'x'
    assert x.free_symbols == {x}

def test_number_coercion():
    ts = TypeSystem()
    assert isinstance(ts.create_number(5), Integer)
    assert isinstance(ts.create_number(5.0), Integer)  # Simplifies
    assert isinstance(ts.create_number(5.5), Float)
```

```python
# tests/test_symbolic_simplification.py
def test_combine_like_terms():
    se = SimplificationEngine()
    # x + x = 2*x
    # 2*x + 3*x = 5*x

def test_pythagorean_identity():
    se = SimplificationEngine()
    # sin(x)**2 + cos(x)**2 = 1

def test_expand_polynomial():
    se = SimplificationEngine()
    # (x + 1)**2 = x**2 + 2*x + 1
```

```python
# tests/test_symbolic_parser.py
def test_parse_simple():
    parser = ExpressionParser()
    expr = parser.parse("x + 1")
    assert isinstance(expr, Add)

def test_parse_complex():
    parser = ExpressionParser()
    expr = parser.parse("sin(x**2 + 1)")
    assert isinstance(expr, Sin)
```

### Integration Tests

```python
# tests/test_symbolic_integration.py
def test_end_to_end_workflow():
    """Test full symbolic manipulation workflow."""
    supervisor = SymbolicSupervisor()

    # Parse expression
    expr = supervisor.parse("(x + 1)**2")

    # Expand
    expanded = supervisor.expand(expr)
    assert str(expanded) == "x**2 + 2*x + 1"

    # Differentiate
    derivative = supervisor.diff(expanded, 'x')
    assert str(derivative) == "2*x + 2"

    # Factor
    factored = supervisor.factor(derivative)
    assert str(factored) == "2*(x + 1)"
```

### Backward Compatibility Tests

```python
# tests/test_symbolic_backward_compat.py
def test_old_api_still_works():
    """Ensure code using old API continues to work."""
    from symbo_agentic_reasoners.core.symbolic import (
        Symbol, Integer, Add, Mul, Pow,
        parse_expr, symbols, diff, simplify, expand
    )

    x, y = symbols('x y')
    expr = x**2 + 2*x*y + y**2
    expanded = expand((x + y)**2)
    assert expr == expanded
```

---

## Public API Design

### `__init__.py` Structure

```python
"""
Native Symbolic Mathematics Engine - Modular Architecture
=========================================================

Pure Python symbolic mathematics WITHOUT SymPy dependency.
Decomposed from monolithic native_symbolic.py into supervisor-specialist architecture.

Public API (Backward Compatible):
----------------------------------
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

Advanced API (Specialist Access):
----------------------------------
from symbo_agentic_reasoners.core.symbolic import SymbolicSupervisor

supervisor = SymbolicSupervisor()
supervisor.type_system.create_symbol('x')
supervisor.simplification_engine.expand(expr)
"""

# Primary public API (backward compatible)
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

__all__ = [
    # Supervisor
    'SymbolicSupervisor',
    'get_supervisor',

    # Type system
    'Expr', 'Symbol', 'Integer', 'Float', 'Rational',
    'Add', 'Mul', 'Pow', 'Function',

    # Functions
    'Sin', 'Cos', 'Tan', 'Exp', 'Log', 'Sqrt', 'Abs', 'Sign',
    'sin', 'cos', 'tan', 'exp', 'log', 'sqrt',

    # Operations
    'symbols', 'diff', 'simplify', 'expand', 'factor',

    # Parsing
    'parse_expr', 'sympify',

    # Compatibility
    'Eq', 'SympifyError',
    'preorder_traversal', 'together', 'fraction',
    'arg', 'expand_complex', 'solve', 'groebner', 'core',

    # Constants
    'pi', 'E', 'I', 'oo',
]

__version__ = '2.0.0-alpha'
__architecture__ = 'supervisor-specialist'
```

---

## Supervisor Implementation Pattern

Following the calculus package pattern:

```python
# symbolic_supervisor.py

class SymbolicSupervisor:
    """
    Main coordinator for symbolic mathematics operations.

    Uses lazy loading to minimize startup time.
    Routes operations to appropriate specialists.
    """

    def __init__(self):
        # Lazy-loaded specialists
        self._type_system = None
        self._composite_ops = None
        self._simplification_engine = None
        self._function_library = None
        self._expression_parser = None
        self._convenience_api = None
        self._sympy_compatibility = None

    @property
    def type_system(self):
        """Lazy load type system specialist."""
        if self._type_system is None:
            from .type_system import TypeSystem
            self._type_system = TypeSystem()
        return self._type_system

    @property
    def simplification_engine(self):
        """Lazy load simplification specialist."""
        if self._simplification_engine is None:
            from .simplification_engine import SimplificationEngine
            self._simplification_engine = SimplificationEngine()
        return self._simplification_engine

    # ... similar for other specialists ...

    def parse(self, text: str):
        """Parse string expression."""
        return self.expression_parser.parse(text)

    def simplify(self, expr):
        """Simplify expression."""
        return self.simplification_engine.simplify(expr)

    def expand(self, expr):
        """Expand expression."""
        return self.simplification_engine.expand(expr)

    def diff(self, expr, var):
        """Differentiate expression."""
        return expr.diff(var)  # Delegates to expression's diff method


# Global singleton instance (like calculus package)
_supervisor_instance = None

def get_supervisor() -> SymbolicSupervisor:
    """Get global supervisor instance."""
    global _supervisor_instance
    if _supervisor_instance is None:
        _supervisor_instance = SymbolicSupervisor()
    return _supervisor_instance


# Public API functions delegate to supervisor
def parse_expr(text: str):
    """Parse mathematical expression string."""
    return get_supervisor().parse(text)

def simplify(expr):
    """Simplify expression."""
    return get_supervisor().simplify(expr)

def expand(expr):
    """Expand expression."""
    return get_supervisor().expand(expr)
```

---

## Risk Mitigation

### Backward Compatibility Risks

**Risk**: Existing code breaks when importing from new location
**Mitigation**:
1. Keep `native_symbolic.py` as a thin wrapper that re-exports from `symbolic/`
2. Add deprecation warning in native_symbolic.py
3. Maintain 100% API compatibility
4. Extensive regression testing

**Implementation**:
```python
# native_symbolic.py (after migration)
"""
DEPRECATED: This module has been decomposed into symbolic/ package.
Please update imports to:
    from symbo_agentic_reasoners.core.symbolic import ...

This compatibility wrapper will be removed in v3.0.0
"""
import warnings
warnings.warn(
    "native_symbolic.py is deprecated. Use symbolic/ package instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from .symbolic import *
```

### Performance Risks

**Risk**: Lazy loading adds overhead
**Mitigation**:
1. Benchmark critical paths
2. Cache specialist instances
3. Profile startup time vs. operation time

**Acceptance Criteria**:
- Startup time: <100ms overhead
- Operation time: <5% slower than monolithic
- Memory: Similar or better (lazy loading helps)

### Testing Gaps

**Risk**: Missing test coverage during migration
**Mitigation**:
1. Write tests BEFORE extracting each module
2. Run full test suite after each extraction
3. Add integration tests for cross-module workflows

---

## Success Criteria

1. **Functional Correctness**:
   - All existing tests pass
   - New tests cover all specialists
   - Integration tests validate workflows

2. **Backward Compatibility**:
   - Old import paths work (with deprecation warning)
   - All public APIs unchanged
   - No behavior changes

3. **Code Quality**:
   - Each specialist <500 lines
   - Clear separation of concerns
   - Single responsibility per module
   - Well-documented interfaces

4. **Performance**:
   - Startup time within 100ms of baseline
   - Operation time within 5% of baseline
   - Memory usage similar or better

5. **Maintainability**:
   - Easy to add new functions
   - Easy to extend simplification rules
   - Clear extension points
   - Isolated testing

---

## Timeline

| Week | Phase | Deliverables | Testing |
|------|-------|--------------|---------|
| 1 | Foundation | type_system.py, constants.py, supervisor skeleton | Unit tests for types |
| 2 | Core Ops | composite_operations.py, simplification_engine.py | Unit tests for ops, integration tests |
| 3 | Functions | function_library.py, expression_parser.py | Unit tests for functions, parser tests |
| 4 | API | convenience_api.py, sympy_compatibility.py, __init__.py | Backward compat tests, full suite |

**Total Estimated Time**: 4 weeks
**Risk Buffer**: +1 week for unforeseen issues

---

## Next Steps

1. **Review and Approve** this decomposition plan
2. **Set up branch** for symbolic decomposition work
3. **Create test harness** to validate backward compatibility
4. **Begin Phase 1** extraction (type_system.py)
5. **Iterate** with regular checkpoints and testing

---

## References

- **Calculus Package**: `src/symbo_agentic_reasoners/core/calculus/`
- **Original File**: `src/symbo_agentic_reasoners/core/native_symbolic.py`
- **Implementation Guide**: See IMPLEMENTATION_GUIDE_SYMBOLIC.md (to be created)
- **Testing Strategy**: See tests/test_symbolic_*.py (to be created)

---

**Document Version**: 1.0
**Created**: 2025-12-15
**Status**: PROPOSAL - Awaiting Approval
