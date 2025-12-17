# Input Preprocessing & Error Diagnostics Guide

**Version:** 1.0
**Date:** 2025-12-10
**Module:** `symbo_agentic_reasoners.core.input_normalizer`

---

## Overview

The input normalizer is the first stage of the SYMBO math processing pipeline. It converts diverse mathematical input formats into a canonical SymPy-compatible form, handling:

- Unicode symbols (Greek letters, superscripts, special operators)
- LaTeX notation
- Natural language expressions
- Copy-paste artifacts
- Calculus notation (derivatives, integrals)
- Vector calculus operators
- ODE prime notation

---

## Quick Start

```python
from symbo_agentic_reasoners.core.input_normalizer import (
    normalize_input,
    validate_normalized,
    InputDiagnostic,
    split_multi_expressions
)

# Basic normalization
result = normalize_input("2πr²")
# Returns: "2*pi*r**2"

# Validate output
is_valid, error = validate_normalized(result)

# Get diagnostic for failed parse
if not is_valid:
    diag = InputDiagnostic.diagnose(original, result, error)
    print(InputDiagnostic.format_error(diag))
```

---

## Feature Reference

### 1. Vector Calculus Operators

The system expands `grad`, `div`, and `curl` into explicit derivative expressions.

| Input | Output |
|-------|--------|
| `grad(f, [x, y])` | `[diff(f, x), diff(f, y)]` |
| `grad(x**2 + y**2, [x, y])` | `[diff(x**2 + y**2, x), diff(x**2 + y**2, y)]` |
| `div([P, Q], [x, y])` | `diff(P, x) + diff(Q, y)` |
| `div([x*y, y*z, z*x], [x, y, z])` | `diff(x*y, x) + diff(y*z, y) + diff(z*x, z)` |
| `curl([P, Q, R], [x, y, z])` | `[diff(R,y)-diff(Q,z), diff(P,z)-diff(R,x), diff(Q,x)-diff(P,y)]` |

**Usage:**
```python
from symbo_agentic_reasoners.core.input_normalizer import expand_vector_calculus

result = expand_vector_calculus("grad(x**2 + y**2, [x, y])")
# "[diff(x**2 + y**2, x), diff(x**2 + y**2, y)]"
```

---

### 2. Prime Notation (ODE Derivatives)

Converts calculus prime notation to SymPy `diff()` calls.

| Input | Output |
|-------|--------|
| `y'(x)` | `diff(y(x), x)` |
| `y''(x)` | `diff(y(x), x, 2)` |
| `y'''(x)` | `diff(y(x), x, 3)` |
| `3y'(x)` | `3*diff(y(x), x)` |
| `xy'(x)` | `x*diff(y(x), x)` |
| `y''(x) - 3y'(x) + 2y(x) = 0` | `diff(y(x), x, 2) - 3*diff(y(x), x) + 2*y(x) = 0` |

**Supported prime characters:**
- ASCII apostrophe: `'`
- Unicode prime: `′` (U+2032)
- Backtick: `` ` ``
- Acute accent: `´`

**Usage:**
```python
from symbo_agentic_reasoners.core.input_normalizer import preprocess_prime_notation

result = preprocess_prime_notation("y''(x) + y(x) = 0")
# "diff(y(x), x, 2) + y(x) = 0"
```

---

### 3. Implicit Multiplication

Automatically inserts `*` where multiplication is implied.

| Pattern | Example | Result |
|---------|---------|--------|
| Number + letter | `2x` | `2*x` |
| Number + Greek | `2pi`, `2sigma` | `2*pi`, `2*sigma` |
| Number + parenthesis | `2(x+1)` | `2*(x+1)` |
| Adjacent parentheses | `(x)(y)` | `(x)*(y)` |
| Letter + function | `sigmasqrt(2pi)` | `sigma*sqrt(2*pi)` |

**Usage:**
```python
from symbo_agentic_reasoners.core.input_normalizer import (
    add_implicit_multiplication,
    enhanced_implicit_multiplication
)

# Enhanced handles special cases like sigmasqrt
result = enhanced_implicit_multiplication("sigmasqrt(2pi)")
# "sigma*sqrt(2*pi)"

# Standard handles basic cases
result = add_implicit_multiplication("2x + 3y")
# "2*x + 3*y"
```

**Known functions preserved:**
- Trig: `sin`, `cos`, `tan`, `sec`, `csc`, `cot`, etc.
- Calculus: `diff`, `integrate`, `limit`, `Sum`, `Product`
- Special: `sqrt`, `exp`, `log`, `ln`, `Abs`
- Greek: `pi`, `alpha`, `beta`, `gamma`, `sigma`, etc.
- ODE variables: `y`, `Y`, `x`, `X`, `z`, `Z`

---

### 4. Equation Normalization

Converts `=` to SymPy `Eq()` format for proper equation handling.

| Input | Output |
|-------|--------|
| `x^2 - 4 = 0` | `Eq(x**2 - 4, 0)` |
| `x + y = 5` | `Eq(x + y, 5)` |

**Preserved (not converted):**
- Already has `==`, `<=`, `>=`, `!=`
- Inside `solve()` or `dsolve()` commands

**Usage:**
```python
from symbo_agentic_reasoners.core.input_normalizer import normalize_equation_equals

result = normalize_equation_equals("x^2 - 4 = 0")
# "Eq(x**2 - 4, 0)"
```

---

### 5. Multi-Expression Splitting

Splits comma-separated expressions while respecting function call parentheses.

| Input | Output |
|-------|--------|
| `x^2, y^2, z^2` | `["x^2", "y^2", "z^2"]` |
| `integrate(x, (x, 0, 1)), diff(y, x)` | `["integrate(x, (x, 0, 1))", "diff(y, x)"]` |

**Usage:**
```python
from symbo_agentic_reasoners.core.input_normalizer import split_multi_expressions

expressions = split_multi_expressions("x^2, integrate(x, (x,0,1)), y^2")
# ["x^2", "integrate(x, (x,0,1))", "y^2"]
```

---

### 6. Command Patterns (Reference Only)

These patterns are defined but used by the routing layer:

| Command | Pattern | Purpose |
|---------|---------|---------|
| `solve(expr, x)` | Algebra equation solving |
| `dsolve(ode, y(x))` | Differential equation solving |
| `grad(f, [vars])` | Gradient computation |
| `div([F], [vars])` | Divergence computation |
| `curl([F], [vars])` | Curl computation |

---

## Error Diagnostics

The `InputDiagnostic` class provides detailed, user-friendly error messages.

### Error Categories

| Category | Description | Example Input |
|----------|-------------|---------------|
| `matrix_syntax` | Malformed matrix literals | `det([, ])`, `eigenvals([[1,2], ])` |
| `probability_notation` | English probability syntax | `E(X^2) where X ~ Normal(0,1)` |
| `probability_english` | Distribution with English glue | `X ~ Normal(0,1) where x > 0` |
| `english_phrase` | Unparseable English | `f(x) where x > 0` |
| `linalg_syntax` | Bad linear algebra command | `eigenvals([[1,2], ])` |
| `missing_multiplication` | Merged identifiers | `sigmaalpha` (should be `sigma*alpha`) |
| `equation_syntax` | Assignment vs equation | `x^2 = 4` with sympify error |
| `prime_notation` | Unconverted derivatives | `y'(x)` causing string error |
| `parse_error` | Generic fallback | Any other parse failure |

### Usage

```python
from symbo_agentic_reasoners.core.input_normalizer import InputDiagnostic

# Diagnose a failed parse
diagnostic = InputDiagnostic.diagnose(
    original_input="E(X^2) where X ~ Normal(0,1)",
    normalized="E(X**2) where X ~ Normal(0,1)",
    parse_error="SympifyError: could not parse..."
)

# diagnostic contains:
# {
#     'category': 'probability_notation',
#     'message': 'English probability notation is not yet supported',
#     'suggestion': 'Use explicit function notation instead...',
#     'details': 'SympifyError: could not parse...',
#     'original': 'E(X^2) where X ~ Normal(0,1)',
#     'normalized': 'E(X**2) where X ~ Normal(0,1)'
# }

# Format for display
error_text = InputDiagnostic.format_error(diagnostic)
# "Error: English probability notation is not yet supported
#  Suggestion: Use explicit function notation instead..."

# Verbose mode includes technical details
error_text = InputDiagnostic.format_error(diagnostic, verbose=True)
```

---

## Full Normalization Pipeline

The `normalize_input()` function applies transformations in this order:

1. **Copy-paste artifact cleanup** - Reconstruct split expressions
2. **Prime notation preprocessing** - `y'(x)` → `diff(y(x), x)`
3. **Whitespace normalization** - Join multi-line, collapse spaces
4. **Unicode conversion** - Greek, symbols, fractions, operators
5. **Vector calculus expansion** - `grad`, `div`, `curl` → `diff`
6. **Derivative patterns** - Leibniz notation `dy/dx` → `diff`
7. **Integral patterns** - `∫ f dx` → `integrate(f, x)`
8. **Modular arithmetic** - `a ≡ b (mod n)` → `Mod()`
9. **Natural language patterns** - "squared" → `**2`
10. **Function name normalization** - "sine" → `sin`
11. **Function parentheses** - `sqrt9` → `sqrt(9)`
12. **Operator normalization** - `^` → `**`
13. **Enhanced implicit multiplication** - `sigmasqrt` → `sigma*sqrt`
14. **Standard implicit multiplication** - `2x` → `2*x`
15. **Parenthesis closing** - Balance unclosed brackets

**Options:**
```python
result = normalize_input(
    text,
    add_multiplication=True,  # Enable implicit multiplication
    close_parens=True,        # Auto-close unclosed brackets
    verbose=False             # Log each transformation step
)
```

---

## Integration Example

```python
from symbo_agentic_reasoners.core.input_normalizer import (
    normalize_input,
    validate_normalized,
    InputDiagnostic,
    split_multi_expressions
)

def process_user_input(raw_input: str):
    """Process raw user input with full error handling."""

    # Handle multiple expressions
    expressions = split_multi_expressions(raw_input)
    results = []

    for expr in expressions:
        # Normalize
        normalized = normalize_input(expr)

        # Validate
        is_valid, error = validate_normalized(normalized)

        if not is_valid:
            # Get detailed diagnostic
            diagnostic = InputDiagnostic.diagnose(expr, normalized, error)
            results.append({
                'status': 'error',
                'original': expr,
                'error': InputDiagnostic.format_error(diagnostic)
            })
        else:
            results.append({
                'status': 'ok',
                'original': expr,
                'normalized': normalized
            })

    return results

# Example usage
results = process_user_input("grad(x^2, [x, y]), y'(x) + y(x) = 0")
# [
#   {'status': 'ok', 'original': 'grad(x^2, [x, y])',
#    'normalized': '[diff(x**2, x), diff(x**2, y)]'},
#   {'status': 'ok', 'original': "y'(x) + y(x) = 0",
#    'normalized': 'Eq(diff(y(x), x) + y(x), 0)'}
# ]
```

---

## Testing

Run the preprocessing tests:

```bash
# All preprocessing tests
python -m pytest tests/test_critical_coverage.py::TestInputNormalizerPreprocessing -v

# Error diagnostic tests
python -m pytest tests/test_critical_coverage.py::TestInputDiagnostic -v

# Full test suite
python -m pytest tests/test_critical_coverage.py -v
```

---

## Limitations

1. **Not Supported (Yet):**
   - English probability notation: `E(X^2) where X ~ Normal(0,1)`
   - Complex set-builder notation: `{x : x > 0}`
   - Matrix operations with malformed literals

2. **Partial Support:**
   - `solve()` command unwrapping (patterns defined, routing WIP)
   - `dsolve()` for ODEs (patterns defined, routing WIP)

3. **Known Edge Cases:**
   - Two-letter variables like `xy` are NOT split (could be variable name)
   - Function names 5+ characters that aren't in known list may trigger warning

---

## Changelog

### v1.0 (2025-12-10)
- Added vector calculus expansion (`grad`, `div`, `curl`)
- Added enhanced implicit multiplication
- Added prime notation conversion for ODEs
- Added equation normalization
- Added multi-expression splitting
- Added `InputDiagnostic` class for error messages
- Added 23 new tests (16 preprocessing + 7 diagnostics)
