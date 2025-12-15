# Solver Package

Modular problem-solving pipeline for mathematical problems.

## Overview

This package provides a production-grade solver that directly dispatches problems to specialist agents, bypassing the full orchestrator's verification polling for immediate results.

**Original:** `solver_engine.py` (1,698 lines - monolithic)
**New:** Modular `solver/` package (8 focused modules)
**Migration Date:** 2025-12-15
**Backward Compatibility:** 100% maintained

## Architecture

```
solver/
├── __init__.py               - Public API exports
├── result.py                 - SolveStatus enum, SolveResult dataclass
├── safety_checker.py         - Expression safety validation
├── router.py                 - Specialist routing & lazy loading
├── cache_manager.py          - Result caching
├── solver_core.py            - SolverEngine class (main orchestrator)
├── specialized_solvers.py    - Specialized solving functions
└── api.py                    - get_solver_engine, solve functions
```

## Quick Start

### Basic Usage

```python
from symbo_agentic_reasoners.core.solver import solve

# Solve a problem
result = solve("differentiate x^2 + 3x")
print(result.result)  # "2*x + 3"
print(result.status)  # SolveStatus.SUCCESS
```

### Using the Engine Directly

```python
from symbo_agentic_reasoners.core.solver import get_solver_engine

engine = get_solver_engine()

# Solve natural language problem
result = engine.solve("integrate sin(x)")
print(result.result)

# Solve direct expression
result = engine.solve_expression("x**3", operation="derivative", variable="x")
print(result.result)  # "3*x**2"
```

### Advanced Features

```python
from symbo_agentic_reasoners.core.solver import (
    get_solver_engine,
    SolveStatus,
    check_expression_safety
)

engine = get_solver_engine()

# 1. Check expression safety
is_safe, error = check_expression_safety("x" * 20000)
if not is_safe:
    print(f"Rejected: {error}")

# 2. Environment variables
engine.set_variable("pi_squared", "pi**2")
result = engine.solve("pi_squared / 6")

# 3. Statistics
stats = engine.get_statistics()
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Avg solve time: {stats['avg_solve_time_ms']:.2f}ms")

# 4. Health check
health = engine.health_check()
if health['native_calculus']:
    print("Native calculus engine operational")
```

## Module Documentation

### result.py

Defines result types for solver operations.

```python
from symbo_agentic_reasoners.core.solver import SolveStatus, SolveResult

# Status enum
class SolveStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    NO_SPECIALIST = "no_specialist"

# Result dataclass
@dataclass
class SolveResult:
    status: SolveStatus
    result: Optional[str] = None
    problem_type: str = ""
    domain: str = ""
    operation: str = ""
    specialist_used: str = ""
    solve_time_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### safety_checker.py

Expression safety validation to prevent DoS attacks.

```python
from symbo_agentic_reasoners.core.solver import check_expression_safety

is_safe, error = check_expression_safety(expression)
if not is_safe:
    print(f"Expression rejected: {error}")

# Safety limits
MAX_EXPRESSION_DEPTH = 50      # Max nesting level
MAX_EXPRESSION_LENGTH = 10000  # Max length in chars
```

### router.py

Specialist routing with lazy loading.

```python
from symbo_agentic_reasoners.core.solver import SpecialistRouter, get_specialist_key

router = SpecialistRouter()

# Get specialist key
key = get_specialist_key(domain="calculus", operation="derivative")
# Returns: "calculus.diff"

# Get specialist (lazy loaded)
specialist = router.get_specialist(key)
```

**Supported Specialists:**
- `calculus.diff` - Differentiation
- `calculus.integrate` - Integration
- `calculus.ode` - Ordinary differential equations
- `calculus.series` - Series and summations
- `algebra.polynomial` - Polynomial operations
- `algebra.arithmetic` - Arithmetic operations
- `algebra.solve` - Equation solving

### cache_manager.py

Result caching for performance (placeholder).

```python
from symbo_agentic_reasoners.core.solver import ResultCache

cache = ResultCache(max_size=1000)

# Store result
cache.put(key="problem_hash", value=result)

# Retrieve result
cached = cache.get(key="problem_hash")

# Clear cache
cache.clear()
```

### solver_core.py

Main SolverEngine orchestrator.

```python
from symbo_agentic_reasoners.core.solver import SolverEngine

engine = SolverEngine(
    resource_coordinator=None,  # Optional ResourceCoordinator
    enable_timeouts=True        # Timeout protection
)

# Solve problem
result = engine.solve("differentiate x^2")

# Solve expression directly
result = engine.solve_expression("x**2", operation="derivative", variable="x")

# Environment management
engine.set_variable("a", "42")
env = engine.get_environment()
engine.clear_environment()

# Statistics
stats = engine.get_statistics()
# Returns: problems_solved, success_rate, avg_solve_time_ms, etc.

# Health check
health = engine.health_check()
# Returns: analysis_team, native_symbolic, native_calculus status
```

**Timeout Configuration:**
```python
# Default timeouts (seconds)
SolverEngine.DEFAULT_TIMEOUTS = {
    'derivative': 30,
    'integral': 90,
    'dsolve': 120,
    'ode': 120,
    'solve': 60,
    'limit': 60,
    'default': 60,
}
```

### specialized_solvers.py

Specialized solving functions for complex problems.

#### Diophantine Equations

```python
from symbo_agentic_reasoners.core.solver import solve_diophantine

# Solve diophantine equation
result = solve_diophantine("diophantine(x**3 + y**3 + z**3 - 27)", engine)

# Sum of cubes
from symbo_agentic_reasoners.core.solver import solve_sum_of_cubes
solutions = solve_sum_of_cubes(target=8)
# Returns: {(2,0,0), (0,2,0), (0,0,2)}

# Quaternary quadratic
from symbo_agentic_reasoners.core.solver import solve_quaternary_quadratic
solutions = solve_quaternary_quadratic(coeffs=(4,5,6,-7), target=11)

# Mordell curve
from symbo_agentic_reasoners.core.solver import solve_mordell_curve
solutions = solve_mordell_curve(k=4)
```

#### Determinants

```python
from symbo_agentic_reasoners.core.solver import solve_determinant

# Matrix determinant
result = solve_determinant("det(Matrix([[1,2],[3,4]]))")

# Native computation
from symbo_agentic_reasoners.core.solver import compute_determinant_native
det = compute_determinant_native("[[1, 0], [0, 1]]")
# Returns: "(1)*(1) - (0)*(0)"
```

#### Limits

```python
from symbo_agentic_reasoners.core.solver import solve_limit_native

# Uses native limit engine (NO SYMPY)
result = solve_limit_native(structured_problem)
```

#### Number-Theoretic Series

```python
from symbo_agentic_reasoners.core.solver import solve_nt_series

# Mobius series
result = solve_nt_series("summation(mu(n)/(n*(log(n))^2), (n,2,oo))")

# Von Mangoldt series
result = solve_nt_series("summation((Lambda(n) - 1)/(n*log(n)), (n,2,oo))")

# Prime products
result = solve_nt_series("product((1 - 1/p^2)/(1 - 1/p)^2, (p, primes))")
```

### api.py

Public API and singleton management.

```python
from symbo_agentic_reasoners.core.solver import (
    get_solver_engine,
    solve,
    solve_expression
)

# Get singleton engine
engine = get_solver_engine(coordinator=None)

# Convenience solve function
result = solve("differentiate x^2")

# Convenience expression solve
result = solve_expression("x**2", operation="derivative", variable="x")
```

## Design Patterns

### Supervisor-Specialist Pattern
- `SolverEngine` supervises overall workflow
- `SpecialistRouter` delegates to specialists
- Specialists handle focused tasks

### Lazy Loading
- Specialists created on first use
- Reduces startup overhead
- Minimal memory footprint

### Singleton Pattern
- Global `_engine` instance
- `get_solver_engine()` ensures single instance
- Shared state management

### Strategy Pattern
- Different specialized solvers for different problem types
- Router selects appropriate strategy
- Fallback to native solver

## Backward Compatibility

### Legacy Import (STILL WORKS)
```python
from symbo_agentic_reasoners.core.solver_engine import (
    SolverEngine,
    solve
)
```

### New Modular Import (RECOMMENDED)
```python
from symbo_agentic_reasoners.core.solver import (
    SolverEngine,
    solve
)
```

Both imports work identically. The original `solver_engine.py` file now acts as a thin compatibility layer.

## NO SYMPY Philosophy

All solving uses native mathematical reasoning:
- Native symbolic module
- Native calculus package
- Native number theory
- Expression analyzer for special cases

No SymPy imports except in `safe_parser` (isolated for security).

## Examples

### Example 1: Basic Calculus

```python
from symbo_agentic_reasoners.core.solver import solve

# Differentiation
result = solve("differentiate sin(x) * cos(x)")
print(result.result)  # "cos(x)**2 - sin(x)**2"

# Integration
result = solve("integrate x**2")
print(result.result)  # "x**3/3"

# Limits
result = solve("limit of sin(x)/x as x approaches 0")
print(result.result)  # "1"
```

### Example 2: Equation Solving

```python
from symbo_agentic_reasoners.core.solver import get_solver_engine

engine = get_solver_engine()

# Polynomial equation
result = engine.solve_expression("x**2 - 4", operation="solve", variable="x")
print(result.result)  # "[-2, 2]"
```

### Example 3: Diophantine Equations

```python
from symbo_agentic_reasoners.core.solver import solve

# Sum of cubes
result = solve("diophantine(x**3 + y**3 + z**3 - 8)")
print(result.result)  # "{(2,0,0), (0,2,0), (0,0,2), ...}"
```

### Example 4: Multi-Step Problems

```python
from symbo_agentic_reasoners.core.solver import get_solver_engine

engine = get_solver_engine()

# Step 1: Store intermediate result
result1 = engine.solve("pi**2 / 6")
engine.set_variable("basel", result1.result)

# Step 2: Use stored variable
result2 = engine.solve("zeta(4) / basel**2")
print(result2.result)
```

## Testing

Run verification tests:
```bash
python verify_solver_decomposition.py
```

Run unit tests:
```bash
pytest tests/test_watchdog_integration.py -k solver
```

## Performance

- **Startup:** Lazy loading minimizes initialization time
- **Memory:** Specialists loaded on-demand
- **Timeouts:** Configurable per operation type
- **Caching:** Placeholder for future result caching

## Future Enhancements

1. **Cache Manager:**
   - LRU eviction policy
   - Time-based expiration
   - Persistent storage

2. **Specialized Solvers:**
   - Elliptic curve solver
   - Continued fraction solver
   - Padé approximation

3. **Performance:**
   - Parallel specialist loading
   - Result streaming
   - Incremental solving

4. **Monitoring:**
   - Detailed metrics
   - Specialist usage tracking
   - Error rate analysis

## Contributing

When adding new specialized solvers:

1. Add function to `specialized_solvers.py`
2. Export from `__init__.py`
3. Add routing logic to `router.py` if needed
4. Document in this README
5. Add tests

## License

Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs

Licensed under the Apache License, Version 2.0
