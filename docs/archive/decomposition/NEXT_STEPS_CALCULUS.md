# Next Steps: Completing Calculus Decomposition

## Quick Start Guide

You're continuing the decomposition of `native_calculus.py` (13,330 lines) into modular specialists.

**Current Status**: Foundation complete (8%), specialists need extraction (92%)

## What's Already Done ✅

### Foundation Modules (5 files, ~1,057 lines)
- `src/symbo_agentic_reasoners/core/calculus/ast_types.py` - AST node types
- `src/symbo_agentic_reasoners/core/calculus/validation.py` - Safety checks
- `src/symbo_agentic_reasoners/core/calculus/expression_parser.py` - String parser
- `src/symbo_agentic_reasoners/core/calculus/calculus_supervisor.py` - Main coordinator
- `src/symbo_agentic_reasoners/core/calculus/__init__.py` - Public API

### Documentation (3 files)
- `CALCULUS_DECOMPOSITION_PLAN.md` - Complete architecture blueprint
- `IMPLEMENTATION_GUIDE_CALCULUS.md` - Detailed extraction steps
- `CALCULUS_DECOMPOSITION_SUMMARY.md` - Progress report

### Tools (2 scripts)
- `scripts/extract_calculus_modules.py` - Automated extraction script
- `scripts/decompose_calculus.py` - Analysis helper

## What Needs to Be Done ⏳

### Remaining Specialists (6 files, ~12,273 lines)

| File | Lines | Priority | Complexity |
|------|-------|----------|------------|
| `calculus_utils.py` | ~1,000 | **HIGH** | Low (shared utilities) |
| `differentiation_specialist.py` | 185 | **HIGH** | Medium |
| `integration_specialist.py` | 1,633 | **HIGH** | High |
| `limit_specialist.py` | 4,748 | MEDIUM | Very High |
| `series_specialist.py` | 906 | MEDIUM | Medium |
| `special_integrals_specialist.py` | 3,539 | LOW | Very High |

## Immediate Action: Run Extraction Script

```bash
cd "C:\dev\Mathematic agent based solver"

# Run the automated extraction script
python scripts/extract_calculus_modules.py

# This will extract 4 files:
# - calculus_utils.py
# - differentiation_specialist.py
# - integration_specialist.py
# - limit_specialist.py
```

**Estimated Time**: 5 minutes to run, 30 minutes to verify and fix

## After Script Runs

### 1. Verify Generated Files
Check that imports are correct:
```python
# Each specialist should have:
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from .calculus_utils import _contains_var, _get_symbols, _evaluate_at_numeric
# etc.
```

### 2. Fix Common Issues
- **Circular imports**: Make sure utils don't import specialists
- **Missing functions**: Check for `self.` method calls that need conversion
- **Global variables**: Move `_parser` to local instances

### 3. Run Quick Test
```python
# Test each specialist individually
from symbo_agentic_reasoners.core.calculus.expression_parser import ExprParser
from symbo_agentic_reasoners.core.calculus.differentiation_specialist import DifferentiationEngine

parser = ExprParser()
engine = DifferentiationEngine()

expr = parser.parse("x**2")
result = engine.differentiate(expr, "x")
print(result)  # Should print: 2*x
```

## Manual Extraction (After Script)

### Step 1: Extract series_specialist.py

**Source**: Lines 8712-9618 in native_calculus.py

**Key functions to extract**:
```python
- series_sum(expr_str, var, start, end)
- _check_nth_term_divergence_sympy()
- _try_geometric_series()
- _try_exp_series()
- Plus ~15 pattern recognition functions
```

**Template**:
```python
# License header
# Module docstring
# Imports
from typing import Tuple, Optional, Union
import re
import logging

# Copy all functions from lines 8712-9618
# Update any internal function calls
```

### Step 2: Extract special_integrals_specialist.py

**Source**: Lines 5172-8711 in native_calculus.py

**This is the LARGEST specialist** (~3,500 lines). Extract in groups:

**Group 1: Gaussian family**
- `_try_completion_square_gaussian()`
- `_try_gaussian_integral()`
- `_try_gaussian_moment_integral()`
- `_try_half_gaussian_integral()`
- Plus coefficient extractors

**Group 2: Exponential integrals**
- `_try_exponential_ray_integral()`
- `_try_exponential_ray_moments()`

**Group 3: Special functions**
- `_try_gamma_power_integral()`
- `_try_fresnel_cube_integral()`
- `_try_mills_ratio_integral()`
- `_try_semicircle_integral()`

**Group 4: Lorentzian and Fourier**
- `_try_lorentzian_power_integral()`
- `_try_gaussian_fourier_integral()`

**Tip**: Extract one group at a time, test, then move to next group.

## Integration Testing

### Test File Template
Create `tests/test_calculus_specialists.py`:

```python
import pytest
from symbo_agentic_reasoners.core.calculus import (
    differentiate,
    integrate,
    limit,
    CalculusSupervisor
)

class TestDifferentiation:
    def test_power_rule(self):
        success, result, method = differentiate("x**2", "x")
        assert success == True
        assert "2*x" in result

    def test_product_rule(self):
        success, result, method = differentiate("x*sin(x)", "x")
        assert success == True
        assert "sin(x)" in result and "cos(x)" in result

class TestIntegration:
    def test_power_rule(self):
        success, result, method = integrate("x**2", "x")
        assert success == True
        assert "x**3" in result

class TestLimits:
    def test_sinx_over_x(self):
        success, result, method = limit("sin(x)/x", "x", "0")
        assert success == True
        assert result == "1"

class TestSupervisor:
    def test_full_pipeline(self):
        supervisor = CalculusSupervisor()

        # Test each operation
        success1, _, _ = supervisor.differentiate("x**2", "x")
        success2, _, _ = supervisor.integrate("x", "x")
        success3, _, _ = supervisor.limit("(x-1)/(x-1)", "x", "1")

        assert all([success1, success2, success3])
```

Run tests:
```bash
pytest tests/test_calculus_specialists.py -v
```

## Update Imports in Main Code

### File: solver_engine.py

**Find**:
```python
from .native_calculus import differentiate, integrate, limit
```

**Replace with**:
```python
# New modular calculus engine
from .calculus import differentiate, integrate, limit
```

**Or use gradual migration**:
```python
try:
    from .calculus import differentiate, integrate, limit
except ImportError:
    # Fallback to old monolith during migration
    from .native_calculus import differentiate, integrate, limit
```

## Checklist Before Completion

- [ ] All 6 specialist files created and saved
- [ ] All imports verified and circular dependencies resolved
- [ ] Unit tests pass for each specialist
- [ ] Integration tests pass for full pipeline
- [ ] Performance benchmark shows <10% regression
- [ ] `solver_engine.py` imports updated
- [ ] All 13,330 lines accounted for
- [ ] Documentation updated (README.md, CHANGELOG.md)
- [ ] Original `native_calculus.py` marked as deprecated
- [ ] Git commit created with clear message

## Performance Verification

Run this benchmark:
```python
import time
from symbo_agentic_reasoners.core import native_calculus as old
from symbo_agentic_reasoners.core import calculus as new

test_expressions = [
    "x**2", "sin(x)", "x**3 + 2*x**2 + x", "cos(x)*sin(x)",
    "exp(x)", "ln(x)", "x*exp(x)", "sin(x)/x"
] * 100  # 800 total operations

# Old implementation
start = time.time()
for expr in test_expressions:
    old.differentiate(expr, "x")
old_time = time.time() - start

# New implementation
start = time.time()
for expr in test_expressions:
    new.differentiate(expr, "x")
new_time = time.time() - start

print(f"Old: {old_time:.3f}s")
print(f"New: {new_time:.3f}s")
print(f"Ratio: {new_time/old_time:.2f}x")
print(f"Acceptable: {new_time <= old_time * 1.10}")
```

## Troubleshooting

### Issue: Import Errors
**Symptom**: `ImportError: cannot import name 'XXX'`
**Fix**: Check that all dependencies are in the correct module. Use absolute imports from `.calculus`.

### Issue: Circular Import
**Symptom**: `ImportError: cannot import module (circular dependency)`
**Fix**: Ensure dependency order: ast_types → utils → specialists → supervisor

### Issue: Tests Fail
**Symptom**: Some calculus operations return wrong results
**Fix**: Compare line-by-line with original. Use `diff` tools. Check for missing helper functions.

### Issue: Performance Regression
**Symptom**: New implementation >10% slower
**Fix**:
1. Add lazy loading in supervisor
2. Cache specialist instances
3. Profile hot paths with `cProfile`

## When You're Done

1. **Create PR** with clear description
2. **Tag reviewers** familiar with calculus engine
3. **Run full test suite**: `pytest tests/ -v`
4. **Update documentation**:
   - README.md - Add section on new architecture
   - CHANGELOG.md - Add entry for v2.0.0
5. **Deprecate old file**:
   - Add deprecation warning to `native_calculus.py`
   - Point users to migration guide

## Questions?

Refer to:
- **Architecture details**: `CALCULUS_DECOMPOSITION_PLAN.md`
- **Step-by-step guide**: `IMPLEMENTATION_GUIDE_CALCULUS.md`
- **Progress report**: `CALCULUS_DECOMPOSITION_SUMMARY.md`

## Estimated Time Remaining

| Task | Time |
|------|------|
| Run extraction script + verify | 1 hour |
| Extract series_specialist.py | 2 hours |
| Extract special_integrals_specialist.py | 4 hours |
| Integration testing | 2 hours |
| Update imports | 30 min |
| Performance benchmarking | 1 hour |
| Documentation | 2 hours |
| **TOTAL** | **~12.5 hours** |

---

**Good Luck!**

The architecture is solid. The foundation is complete. The extraction tools are ready.
Just run the script, verify the output, and complete the two large specialists.

**Last Updated**: 2025-12-14
