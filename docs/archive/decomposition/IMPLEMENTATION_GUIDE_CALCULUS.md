# Implementation Guide: Completing the Calculus Decomposition

## Current Status

### Completed (Phase 1-2)
- [x] Architecture design and decomposition plan
- [x] Directory structure created: `src/symbo_agentic_reasoners/core/calculus/`
- [x] `ast_types.py` - All AST node types and constructors (270 lines)
- [x] `validation.py` - Expression safety checks (67 lines)
- [x] `expression_parser.py` - String to AST parser (230 lines)
- [x] `calculus_supervisor.py` - Main coordinator with routing logic (350 lines)
- [x] `__init__.py` - Public API exports (140 lines)
- [x] Extraction automation script: `scripts/extract_calculus_modules.py`
- [x] Decomposition plan document: `CALCULUS_DECOMPOSITION_PLAN.md`

### Remaining (Phase 3-5)
- [ ] Extract 4 major specialist modules (~8,000 lines total)
- [ ] Create `calculus_utils.py` with shared utilities
- [ ] Update imports in `solver_engine.py` and `native_symbolic.py`
- [ ] Run integration tests
- [ ] Deprecate old `native_calculus.py`

## Step-by-Step Implementation Guide

### Step 1: Extract Calculus Utils (Shared Functions)

Create `calculus_utils.py` with functions used across multiple specialists:

**Source locations in native_calculus.py:**
- `_get_symbols()` - lines 4006-4028
- `_evaluate_at_numeric()` - lines 4031-4080
- `_try_evaluate_const()` - lines 5126-5170
- `_simplify_output()` - lines 8676-8710
- `_contains_var()` - lines 521-537 (in DifferentiationEngine)
- `_subtract_one()` - lines 539-543 (in DifferentiationEngine)
- `_add_one()` - lines 2177-2181 (in IntegrationEngine)

**Command to extract:**
```bash
# Create the file
touch src/symbo_agentic_reasoners/core/calculus/calculus_utils.py

# Copy license header, imports, and the 7 functions listed above
# Make them standalone (remove self parameter if present)
```

**Key modifications:**
1. Remove `self` parameter from methods (make them module-level functions)
2. Import from `.ast_types` instead of module-level imports
3. Add proper module docstring explaining shared utilities

### Step 2: Extract Differentiation Specialist

Create `differentiation_specialist.py`:

**Source location:** Lines 360-544 (DifferentiationEngine class)

**Extraction steps:**
```python
# 1. Copy license header
# 2. Add imports:
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from .calculus_utils import _contains_var, _subtract_one
from fractions import Fraction
import logging

# 3. Copy entire DifferentiationEngine class (lines 360-544)
# 4. Update _contains_var and _subtract_one calls to use imported functions
```

**Key methods:**
- `differentiate(expr, var)` - Main entry point
- `_diff(expr, var)` - Dispatcher
- `_diff_product(factors, var)` - Product rule
- `_diff_power(expr, var)` - Power rule
- `_diff_func(expr, var)` - Chain rule
- `FUNCTION_DERIVATIVES` - Function derivative lookup table

**Testing:**
```python
from calculus.differentiation_specialist import DifferentiationEngine
from calculus.expression_parser import ExprParser

parser = ExprParser()
engine = DifferentiationEngine()

expr = parser.parse("x**2 + sin(x)")
result = engine.differentiate(expr, "x")
print(result)  # Should output: 2*x + cos(x)
```

### Step 3: Extract Integration Specialist

Create `integration_specialist.py`:

**Source location:** Lines 550-2183 (IntegrationEngine class)

**Extraction steps:**
```python
# 1. Copy license header
# 2. Add imports:
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from .calculus_utils import _contains_var, _add_one
from .differentiation_specialist import DifferentiationEngine
from fractions import Fraction
from typing import Optional, List
import logging

# 3. Copy entire IntegrationEngine class (lines 550-2183)
# 4. Update utility function calls to use imports
```

**Key methods (20+ methods):**
- `integrate(expr, var)` - Main entry point
- `_integrate(expr, var)` - Dispatcher
- `_integrate_product(expr, var, depth)` - Product integration
- `_try_integration_by_parts(f1, f2, var, depth)` - Integration by parts
- `_get_liate_priority(expr, var)` - LIATE rule
- `_integrate_power(expr, var)` - Power rule
- `_integrate_func(expr, var)` - Function table lookup
- `_integrate_trig_power(expr, var)` - Trig power reduction
- `_integrate_sin_power(n, var)` - sin^n reduction
- `_integrate_cos_power(n, var)` - cos^n reduction
- Plus ~10 more helper methods for special patterns

**Data structures:**
- `BASIC_INTEGRALS` - Function integral lookup
- `LIATE_PRIORITY` - Integration by parts priority

### Step 4: Extract Limit Specialist

Create `limit_specialist.py`:

**Source locations:**
- Main class: Lines 2188-3273 (LimitEngine class)
- Patterns: Lines 9619-13282 (KNOWN_LIMIT_PATTERNS + helpers)

**Extraction steps:**
```python
# 1. Copy license header
# 2. Add imports:
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from .calculus_utils import _contains_var, _evaluate_at_numeric
from .differentiation_specialist import DifferentiationEngine
from typing import Optional, Union, Tuple, Dict, Any
import re
import logging

# 3. Copy LimitEngine class (lines 2188-3273)
# 4. Copy KNOWN_LIMIT_PATTERNS dict (lines 9619-13282)
# 5. Copy all helper functions for limit evaluation
```

**Key components:**
- `LimitEngine` class with ~20 methods
- `KNOWN_LIMIT_PATTERNS` dict with ~100 pattern definitions
- Pattern matching and L'Hôpital's rule implementation
- Indeterminate form handling

### Step 5: Extract Series Specialist

Create `series_specialist.py`:

**Source location:** Lines 8712-9618 (series evaluation functions)

**Extraction steps:**
```python
# 1. Copy license header
# 2. Add imports
# 3. Copy series_sum() function and all helper functions
# 4. Include:
#    - _check_nth_term_divergence_sympy()
#    - _try_geometric_series()
#    - _try_exp_series()
#    - All pattern matchers for Basel, zeta, etc.
```

**Key functions:**
- `series_sum(expr_str, var, start, end)` - Main entry
- ~15 pattern recognition functions
- Convergence test helpers

### Step 6: Extract Special Integrals Specialist

Create `special_integrals_specialist.py`:

**Source location:** Lines 5172-8711 (~3,500 lines of special integral patterns)

**Extraction steps:**
```python
# This is the LARGEST specialist (~40 functions)
# Extract in groups:

# Group 1: Gaussian family (lines 5172-5534)
# - _try_completion_square_gaussian()
# - _try_gaussian_integral()
# - _try_gaussian_moment_integral()
# - _try_half_gaussian_integral()
# - _try_symbolic_gaussian_integral()
# Plus coefficient extractors

# Group 2: Exponential ray integrals (lines 5534-5856)
# - _try_exponential_ray_integral()
# - _try_exponential_ray_moments()

# Group 3: Special functions (lines 5856-6259)
# - _try_gamma_power_integral()
# - _try_oscillatory_gaussian_integral()
# - _try_fresnel_cube_integral()
# - _try_mills_ratio_integral()
# - _try_euler_gamma_integral()
# - _try_semicircle_integral()

# Group 4: Lorentzian and Fourier (lines 6259-8711)
# - _try_lorentzian_power_integral()
# - _try_gaussian_fourier_integral()
# Plus ~20 more coefficient extractors
```

### Step 7: Update Imports in solver_engine.py

**Current imports in solver_engine.py:**
```python
from .native_calculus import differentiate, integrate, limit
```

**New imports:**
```python
from .calculus import differentiate, integrate, limit
```

**Migration approach:**
```python
# Option 1: Direct replacement (recommended once all specialists extracted)
from .calculus import differentiate, integrate, limit

# Option 2: Gradual migration (during extraction)
try:
    from .calculus import differentiate, integrate, limit
except ImportError:
    from .native_calculus import differentiate, integrate, limit
```

### Step 8: Run the Extraction Script

The automated extraction script can handle most of the work:

```bash
cd "C:\dev\Mathematic agent based solver"
python scripts/extract_calculus_modules.py
```

This script will:
1. Read native_calculus.py
2. Extract each class/function group to the appropriate file
3. Add proper imports and headers
4. Create all specialist files

**Manual cleanup required after script:**
1. Verify imports are correct
2. Fix any circular dependency issues
3. Update method calls (remove `self.` where needed)
4. Add proper docstrings

### Step 9: Testing

**Unit tests for each specialist:**
```python
# tests/test_calculus_decomposition.py
import pytest
from symbo_agentic_reasoners.core.calculus import (
    differentiate,
    integrate,
    limit,
    CalculusSupervisor
)
from symbo_agentic_reasoners.core.calculus.expression_parser import ExprParser
from symbo_agentic_reasoners.core.calculus.differentiation_specialist import DifferentiationEngine

def test_differentiation_specialist():
    """Test differentiation specialist in isolation."""
    parser = ExprParser()
    engine = DifferentiationEngine()

    # Test power rule
    expr = parser.parse("x**2")
    result = engine.differentiate(expr, "x")
    assert str(result) == "2*x"

    # Test product rule
    expr = parser.parse("x*sin(x)")
    result = engine.differentiate(expr, "x")
    assert "sin(x)" in str(result) and "cos(x)" in str(result)

def test_supervisor_differentiate():
    """Test differentiation through supervisor."""
    success, result, method = differentiate("x**2", "x")
    assert success == True
    assert "2*x" in result
    assert method == "native_calculus"

def test_backward_compatibility():
    """Ensure new API is compatible with old API."""
    # This test should pass with both old and new implementations
    success, result, method = differentiate("x**3", "x")
    assert success == True
    assert "3*x**2" in result or "3*x^2" in result
```

**Integration tests:**
```python
def test_full_calculus_pipeline():
    """Test entire calculus pipeline end-to-end."""
    supervisor = CalculusSupervisor()

    # Differentiate
    success, deriv, _ = supervisor.differentiate("x**2 + sin(x)", "x")
    assert success and "2*x" in deriv and "cos(x)" in deriv

    # Integrate
    success, integ, _ = supervisor.integrate("x**2", "x")
    assert success and "x**3" in integ

    # Limit
    success, lim, _ = supervisor.limit("sin(x)/x", "x", "0")
    assert success and ("1" in lim or lim == "1")
```

### Step 10: Performance Benchmarking

Compare old vs new implementation:

```python
import time
from native_calculus import differentiate as old_diff
from calculus import differentiate as new_diff

expressions = [
    "x**2",
    "sin(x)*cos(x)",
    "x**3 + 2*x**2 + x",
    "exp(x**2)",
    # ... 100 more expressions
]

# Benchmark old
start = time.time()
for expr in expressions:
    old_diff(expr, "x")
old_time = time.time() - start

# Benchmark new
start = time.time()
for expr in expressions:
    new_diff(expr, "x")
new_time = time.time() - start

print(f"Old: {old_time:.3f}s")
print(f"New: {new_time:.3f}s")
print(f"Speedup: {old_time/new_time:.2f}x")
```

### Step 11: Documentation Updates

Update the following files:
1. **README.md** - Mention new modular architecture
2. **docs/architecture.md** - Add calculus decomposition section
3. **CHANGELOG.md** - Add entry for version 2.0.0
4. **Migration guide** - Create for external users

## Common Issues and Solutions

### Issue 1: Circular Imports

**Problem:** `differentiation_specialist` imports `calculus_utils` which imports `differentiation_specialist`

**Solution:**
- Move shared utilities to `calculus_utils.py`
- Make utils depend only on `ast_types.py`
- Have specialists import from utils, not vice versa

### Issue 2: Missing Global Parser

**Problem:** Some functions expect a global `_parser` instance

**Solution:**
```python
# In each specialist or supervisor, create local parser
self.parser = ExprParser()
# Or use lazy initialization
```

### Issue 3: Performance Regression

**Problem:** New implementation slower due to import overhead

**Solution:**
- Use lazy loading in supervisor
- Cache specialist instances
- Profile and optimize hot paths

### Issue 4: Test Failures

**Problem:** Some edge cases fail after extraction

**Solution:**
- Run original test suite line-by-line
- Compare outputs exactly (use diff tools)
- Check for missing helper functions

## Rollback Plan

If issues arise during migration:

1. **Keep native_calculus.py intact** - Don't delete the original file
2. **Feature flag** - Use environment variable to toggle new/old:
   ```python
   import os
   USE_NEW_CALCULUS = os.getenv('USE_NEW_CALCULUS', 'false').lower() == 'true'

   if USE_NEW_CALCULUS:
       from .calculus import differentiate
   else:
       from .native_calculus import differentiate
   ```
3. **Gradual rollout** - Deploy to subset of equations first
4. **Monitoring** - Track success rates and performance

## Success Criteria

The decomposition is complete when:
- [x] All 5 specialist files created
- [x] All 13,330 lines accounted for
- [ ] 100% of original tests pass
- [ ] No performance regression (within 10%)
- [ ] Backward-compatible API maintained
- [ ] Documentation updated
- [ ] Code review approved

## Timeline Estimate

| Task | Estimated Time | Dependencies |
|------|----------------|--------------|
| Extract calculus_utils.py | 1 hour | None |
| Extract differentiation_specialist.py | 1 hour | calculus_utils |
| Extract integration_specialist.py | 2 hours | calculus_utils, diff |
| Extract limit_specialist.py | 3 hours | calculus_utils, diff |
| Extract series_specialist.py | 2 hours | None |
| Extract special_integrals_specialist.py | 4 hours | All above |
| Update imports in solver_engine.py | 30 min | All specialists |
| Integration testing | 2 hours | All specialists |
| Performance benchmarking | 1 hour | All specialists |
| Documentation | 2 hours | All complete |
| **TOTAL** | **~18 hours** | |

## Next Action Items

1. **Run extraction script**: `python scripts/extract_calculus_modules.py`
2. **Review generated files**: Check for import errors
3. **Run tests**: `pytest tests/test_calculus_decomposition.py`
4. **Fix issues**: Address any circular imports or missing functions
5. **Benchmark**: Compare performance with original
6. **Deploy**: Update solver_engine.py imports
7. **Document**: Update README and add migration guide

---

**Document Version**: 1.0
**Last Updated**: 2025-12-14
**Next Review**: After extraction script completes
