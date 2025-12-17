# Complex Integration / Risch Algorithm Enhancement Plan

## Executive Summary

**Current State:** 60/100 Advanced Integration score (35% expert success rate)
**Target State:** 80/100 Advanced Integration score (50%+ expert success rate)

This document provides a comprehensive technical plan for improving the native integration
capabilities in the Symbo Agentic Reasoners codebase WITHOUT introducing SymPy dependencies.

---

## 1. Current Implementation Analysis

### 1.1 What Currently Works (from `integration_specialist.py`)

The existing `NativeIntegration` class handles:

1. **Basic Integration Rules**
   - Power rule: `x^n -> x^(n+1)/(n+1)`
   - Constant rule: `c -> c*x`
   - Sum/difference rule (linearity)

2. **Transcendental Function Integration**
   - `sin(x) -> -cos(x)`
   - `cos(x) -> sin(x)`
   - `exp(x) -> exp(x)`
   - `1/x -> log(x)`

3. **Partial Fractions (Limited)**
   - Simple rational functions with linear denominators
   - `1/(ax+b)` patterns
   - Basic quadratic denominators `1/(x^2+a^2)`

4. **Pattern Matching**
   - Specific algebraic patterns
   - Some trigonometric products

### 1.2 Critical Gaps Identified

| Gap Category | Examples | Impact |
|-------------|----------|--------|
| **No u-substitution engine** | `sin(x^2)*2x`, `e^(3x)` | ~15% failure |
| **Incomplete partial fractions** | `(x^2+1)/(x^3-x)` | ~10% failure |
| **No integration by parts** | `x*e^x`, `x*sin(x)` | ~10% failure |
| **No trig substitutions** | `sqrt(1-x^2)`, `sqrt(x^2+1)` | ~8% failure |
| **No transcendental detection** | `e^(x^2)` (non-elementary) | ~7% failure |
| **No special function integrals** | `erf(x)`, `Ei(x)`, elliptic | ~10% failure |

---

## 2. Risch Algorithm Components Needed

### 2.1 Theoretical Foundation

The Risch algorithm determines whether an integral has a closed-form elementary solution.
Full implementation requires:

1. **Differential Field Extension Theory**
   - Transcendental extension towers (exp, log chains)
   - Algebraic extension handling

2. **Liouville's Theorem Application**
   - Detecting when integrals are non-elementary
   - Returning "no closed form" instead of failing

3. **Structure Theorems**
   - Polynomial and rational function handling
   - Logarithmic and exponential extensions

### 2.2 Practical Implementation Strategy

Rather than implementing full Risch (extremely complex), we propose a **tiered approach**:

```
Tier 1: Pattern-based heuristics (fastest, covers ~70% of cases)
Tier 2: Algorithmic methods (u-sub, parts, partial fractions)
Tier 3: Risch-lite detection (elementary vs non-elementary)
Tier 4: Special function recognition
```

---

## 3. Proposed Enhancements

### 3.1 Enhanced u-Substitution Engine

**File:** `src/symbo_agentic_reasoners/core/calculus/integration/u_substitution.py`

```python
class USubstitutionEngine:
    """
    Native u-substitution implementation for integration.

    Strategy:
    1. Identify composite functions f(g(x))
    2. Check if g'(x) appears as a factor
    3. Substitute u = g(x), du = g'(x)dx
    4. Integrate simpler form
    5. Back-substitute

    Patterns handled:
    - f(ax+b) * a          -> F(ax+b)/a
    - f(x^n) * nx^(n-1)    -> F(x^n)/n
    - f(e^x) * e^x         -> F(e^x)
    - f(sin(x)) * cos(x)   -> F(sin(x))
    - f(cos(x)) * (-sin(x)) -> F(cos(x))
    - f(tan(x)) * sec^2(x) -> F(tan(x))
    - f(log(x)) * (1/x)    -> F(log(x))
    """

    def find_substitution(self, expr, var):
        """Attempt to find a valid u-substitution."""
        # Implementation details...
        pass

    def apply_substitution(self, expr, u_expr, var):
        """Apply the u-substitution and integrate."""
        pass
```

**Expected Impact:** +8% success rate

### 3.2 Integration by Parts Module

**File:** `src/symbo_agentic_reasoners/core/calculus/integration/integration_by_parts.py`

```python
class IntegrationByPartsEngine:
    """
    Native integration by parts: integral(u dv) = uv - integral(v du)

    LIATE Rule for choosing u (in order of preference):
    - L: Logarithmic functions (log, ln)
    - I: Inverse trigonometric (arcsin, arctan, etc.)
    - A: Algebraic (polynomials, x^n)
    - T: Trigonometric (sin, cos, tan)
    - E: Exponential (e^x, a^x)

    Special patterns:
    - x^n * e^x    (tabular method)
    - x^n * sin(x) (tabular method)
    - x^n * cos(x) (tabular method)
    - log(x)       (parts with dv = dx)
    - arctan(x)    (parts with dv = dx)
    """

    def classify_term(self, expr):
        """Classify expression by LIATE priority."""
        pass

    def apply_parts(self, expr, var, depth=0, max_depth=5):
        """Apply integration by parts with recursion limit."""
        pass

    def tabular_method(self, polynomial, other_factor, var):
        """Efficient tabular integration for polynomial * transcendental."""
        pass
```

**Expected Impact:** +6% success rate

### 3.3 Complete Partial Fractions Decomposition

**File:** `src/symbo_agentic_reasoners/core/calculus/integration/partial_fractions.py`

```python
class PartialFractionDecomposer:
    """
    Full partial fraction decomposition for rational functions.

    Handles:
    1. Distinct linear factors: A/(x-a) + B/(x-b) + ...
    2. Repeated linear factors: A/(x-a) + B/(x-a)^2 + ...
    3. Irreducible quadratic factors: (Ax+B)/(x^2+px+q)
    4. Repeated quadratic factors

    Algorithm:
    1. Factor denominator (requires polynomial factoring)
    2. Set up partial fraction template
    3. Solve for coefficients (Heaviside cover-up or system solve)
    4. Integrate each term separately
    """

    def factor_polynomial(self, poly, var):
        """Factor polynomial into irreducible factors."""
        pass

    def decompose(self, numerator, denominator, var):
        """Decompose P(x)/Q(x) into partial fractions."""
        pass

    def integrate_linear_factor(self, A, a, n, var):
        """Integrate A/(x-a)^n."""
        pass

    def integrate_quadratic_factor(self, A, B, p, q, n, var):
        """Integrate (Ax+B)/(x^2+px+q)^n."""
        pass
```

**Expected Impact:** +5% success rate

### 3.4 Trigonometric Substitution Module

**File:** `src/symbo_agentic_reasoners/core/calculus/integration/trig_substitution.py`

```python
class TrigSubstitutionEngine:
    """
    Trigonometric substitutions for radical integrands.

    Standard Substitutions:
    1. sqrt(a^2 - x^2): x = a*sin(theta), dx = a*cos(theta)
    2. sqrt(x^2 + a^2): x = a*tan(theta), dx = a*sec^2(theta)
    3. sqrt(x^2 - a^2): x = a*sec(theta), dx = a*sec(theta)*tan(theta)

    Detection patterns:
    - sqrt(c - k*x^2)  -> Form 1
    - sqrt(c + k*x^2)  -> Form 2
    - sqrt(k*x^2 - c)  -> Form 3
    """

    def detect_radical_pattern(self, expr, var):
        """Identify which trig substitution applies."""
        pass

    def apply_trig_sub(self, expr, pattern_type, a, var):
        """Apply the substitution and simplify."""
        pass

    def back_substitute(self, result, pattern_type, a, var):
        """Convert back from theta to x."""
        pass
```

**Expected Impact:** +4% success rate

### 3.5 Elementary Function Detection (Risch-Lite)

**File:** `src/symbo_agentic_reasoners/core/calculus/integration/elementary_detection.py`

```python
class ElementaryFunctionDetector:
    """
    Detect whether an integral has an elementary antiderivative.

    Based on Liouville's theorem and known non-elementary integrals.

    Known Non-Elementary Integrals (return special function or 'non-elementary'):
    - e^(x^2)           -> erf(x) * sqrt(pi)/2
    - e^(-x^2)          -> erf(x) * sqrt(pi)/2
    - sin(x)/x          -> Si(x) (sine integral)
    - cos(x)/x          -> Ci(x) (cosine integral)
    - e^x/x             -> Ei(x) (exponential integral)
    - 1/log(x)          -> li(x) (logarithmic integral)
    - sin(x^2)          -> Fresnel S
    - cos(x^2)          -> Fresnel C
    - sqrt(1-k^2*sin^2) -> Elliptic E
    - 1/sqrt(1-k^2*sin^2) -> Elliptic F

    Detection Strategy:
    1. Check against known non-elementary patterns
    2. Analyze transcendental tower structure
    3. Apply simplified Risch decision procedure
    """

    NON_ELEMENTARY_PATTERNS = [
        (r'exp\([^)]*\*\*2\)', 'gaussian', 'erf'),
        (r'sin\([^)]*\)/[^)]*', 'sine_integral', 'Si'),
        (r'cos\([^)]*\)/[^)]*', 'cosine_integral', 'Ci'),
        # ... more patterns
    ]

    def is_elementary(self, expr, var):
        """Determine if integral has elementary antiderivative."""
        pass

    def suggest_special_function(self, expr, var):
        """Suggest appropriate special function representation."""
        pass
```

**Expected Impact:** +3% success rate (better error messages, fewer false failures)

### 3.6 Special Function Integration

**File:** `src/symbo_agentic_reasoners/core/calculus/integration/special_functions.py`

```python
class SpecialFunctionIntegrator:
    """
    Integration involving and producing special functions.

    Supported Special Functions:

    Error Function Family:
    - erf(x): integral(2/sqrt(pi) * e^(-t^2), (t, 0, x))
    - erfc(x): 1 - erf(x)
    - erfi(x): imaginary error function

    Exponential Integrals:
    - Ei(x): exponential integral
    - li(x): logarithmic integral (li(x) = Ei(log(x)))
    - Si(x): sine integral
    - Ci(x): cosine integral

    Fresnel Integrals:
    - FresnelS(x): integral(sin(t^2), (t, 0, x))
    - FresnelC(x): integral(cos(t^2), (t, 0, x))

    Gamma and Beta Functions:
    - gamma(a): integral(t^(a-1)*e^(-t), (t, 0, oo))
    - beta(a,b): integral(t^(a-1)*(1-t)^(b-1), (t, 0, 1))
    - digamma(x): d/dx log(gamma(x))

    Elliptic Integrals:
    - EllipticK(k): complete elliptic integral of first kind
    - EllipticE(k): complete elliptic integral of second kind
    - EllipticF(phi, k): incomplete elliptic integral of first kind
    - EllipticPi(n, k): complete elliptic integral of third kind

    Polylogarithms:
    - Li_n(x): polylogarithm of order n
    - dilog(x): Li_2(x) = dilogarithm
    """

    def integrate_with_special_functions(self, expr, var):
        """Attempt integration, returning special functions if needed."""
        pass

    def recognize_special_integral(self, expr, var):
        """Recognize integrals that produce special functions."""
        pass
```

**Expected Impact:** +5% success rate

---

## 4. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

1. **Create integration submodule structure:**
   ```
   core/calculus/integration/
   ├── __init__.py
   ├── u_substitution.py
   ├── integration_by_parts.py
   ├── partial_fractions.py
   ├── trig_substitution.py
   ├── elementary_detection.py
   ├── special_functions.py
   └── integration_coordinator.py
   ```

2. **Implement basic u-substitution patterns**
   - Linear substitution: u = ax + b
   - Power substitution: u = x^n
   - Chain rule detection

3. **Add comprehensive tests**
   - Unit tests for each pattern
   - Integration tests with existing specialist

### Phase 2: Core Algorithms (Week 3-4)

4. **Complete partial fractions:**
   - Polynomial factoring (real roots)
   - Linear factor decomposition
   - Quadratic factor decomposition

5. **Integration by parts:**
   - LIATE classification
   - Recursive application with depth limit
   - Tabular method for polynomials

6. **Trigonometric substitution:**
   - Pattern detection for sqrt forms
   - Forward/backward substitution

### Phase 3: Advanced Features (Week 5-6)

7. **Elementary function detection:**
   - Non-elementary pattern database
   - Liouville theorem approximation

8. **Special function support:**
   - Error function family
   - Exponential integrals
   - Basic elliptic integrals

9. **Integration coordinator:**
   - Strategy selection heuristics
   - Fallback chain management
   - Result verification

### Phase 4: Optimization and Testing (Week 7-8)

10. **Performance optimization:**
    - Caching for repeated patterns
    - Early bailout for non-integrable forms
    - Complexity budgeting

11. **Comprehensive testing:**
    - All 100 edge case equations
    - Elite research equations
    - Competition integral benchmarks

12. **Documentation and cleanup:**
    - API documentation
    - Example notebooks
    - Migration guide

---

## 5. Integration with Existing Architecture

### 5.1 Supervisor-Specialist Pattern

```python
# integration_coordinator.py
class IntegrationCoordinator:
    """
    Coordinator for the integration specialists.

    Routes integration requests to appropriate engines:
    1. Try direct pattern match (fastest)
    2. Try u-substitution
    3. Try integration by parts
    4. Try partial fractions (if rational)
    5. Try trig substitution (if has sqrt)
    6. Check if non-elementary
    7. Try special function representation
    8. Fall back to numerical approximation
    """

    def __init__(self):
        self.u_sub = USubstitutionEngine()
        self.parts = IntegrationByPartsEngine()
        self.partial_fractions = PartialFractionDecomposer()
        self.trig_sub = TrigSubstitutionEngine()
        self.elementary = ElementaryFunctionDetector()
        self.special = SpecialFunctionIntegrator()

    def integrate(self, expr, var, strategy='auto'):
        """Main integration entry point."""
        pass
```

### 5.2 Backward Compatibility

The new modules will be integrated via the existing `NativeIntegration` class:

```python
class NativeIntegration:
    """Enhanced integration with new capabilities."""

    def __init__(self):
        # Existing initialization
        self.coordinator = IntegrationCoordinator()  # NEW

    def integrate(self, expr, var):
        # Try existing patterns first (fast path)
        result = self._try_basic_integration(expr, var)
        if result:
            return result

        # Delegate to coordinator for advanced methods
        return self.coordinator.integrate(expr, var)
```

---

## 6. Success Metrics

### 6.1 Test Suite Targets

| Test Category | Current | Target | Improvement |
|---------------|---------|--------|-------------|
| Basic integrals | 90% | 95% | +5% |
| U-substitution | 40% | 80% | +40% |
| Integration by parts | 30% | 70% | +40% |
| Partial fractions | 50% | 85% | +35% |
| Trig substitution | 20% | 65% | +45% |
| Special functions | 10% | 50% | +40% |
| **Overall Expert** | **35%** | **50%+** | **+15%+** |

### 6.2 Performance Targets

- Simple integrals: < 10ms
- Complex u-substitution: < 100ms
- Full partial fractions: < 500ms
- Special function detection: < 200ms
- Worst case (all strategies): < 2000ms

---

## 7. Risk Assessment

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Polynomial factoring complexity | High | Medium | Limit to degree 4, use numerical roots |
| Integration by parts infinite loops | Medium | High | Strict depth limiting, pattern detection |
| False elementary detection | Medium | Medium | Conservative detection, manual overrides |
| Performance regression | Low | High | Comprehensive benchmarking, caching |

### 7.2 Scope Risks

- Full Risch algorithm is out of scope (too complex)
- Some special functions may need numerical evaluation
- Multivariate integration remains limited

---

## 8. Dependencies

### 8.1 Internal Dependencies

- `core/symbolic/`: Expression types and operations
- `core/calculus/`: Existing calculus infrastructure
- `agents/specialists/calculus/`: Specialist interface

### 8.2 No External Dependencies

**Critical:** All implementations must be pure Python with NO SymPy.
Standard library only: `math`, `cmath`, `fractions`, `functools`, `re`.

---

## 9. Appendix: Reference Integrals

### 9.1 U-Substitution Test Cases

```python
U_SUBSTITUTION_TESTS = [
    ("sin(x**2)*2*x", "x", "-cos(x**2)"),
    ("exp(3*x)*3", "x", "exp(3*x)"),
    ("cos(x)/sin(x)", "x", "log(abs(sin(x)))"),
    ("x/(x**2+1)", "x", "log(x**2+1)/2"),
    ("sec(x)**2*tan(x)", "x", "tan(x)**2/2"),
]
```

### 9.2 Integration by Parts Test Cases

```python
PARTS_TESTS = [
    ("x*exp(x)", "x", "(x-1)*exp(x)"),
    ("x*sin(x)", "x", "-x*cos(x) + sin(x)"),
    ("log(x)", "x", "x*log(x) - x"),
    ("x**2*exp(x)", "x", "(x**2-2*x+2)*exp(x)"),
    ("arctan(x)", "x", "x*arctan(x) - log(1+x**2)/2"),
]
```

### 9.3 Partial Fractions Test Cases

```python
PARTIAL_FRACTIONS_TESTS = [
    ("1/((x-1)*(x+1))", "x", "log(abs(x-1))/2 - log(abs(x+1))/2"),
    ("x/((x-1)**2)", "x", "log(abs(x-1)) + 1/(x-1)"),
    ("1/(x**2+1)", "x", "arctan(x)"),
    ("(2*x+3)/(x**2+x-2)", "x", "log(abs(x-1)) + log(abs(x+2))"),
]
```

### 9.4 Trig Substitution Test Cases

```python
TRIG_SUB_TESTS = [
    ("1/sqrt(1-x**2)", "x", "arcsin(x)"),
    ("sqrt(1-x**2)", "x", "(x*sqrt(1-x**2) + arcsin(x))/2"),
    ("1/sqrt(x**2+1)", "x", "log(x + sqrt(x**2+1))"),  # arcsinh
    ("1/(x**2+1)**(3/2)", "x", "x/sqrt(x**2+1)"),
]
```

---

## 10. Conclusion

This plan provides a structured approach to significantly improving the integration
capabilities of the Symbo Agentic Reasoners system. By implementing these enhancements
in phases, we can:

1. Achieve the target 50%+ expert-level success rate
2. Maintain the NO SYMPY philosophy
3. Provide clear feedback for non-elementary integrals
4. Support special function representations
5. Maintain backward compatibility with existing code

The tiered approach (pattern matching -> algorithmic methods -> detection ->
special functions) ensures optimal performance while maximizing coverage.

---

*Document Version: 1.0*
*Author: Mathematical Research Agent*
*Date: 2025-12-15*
*Status: Ready for Implementation Review*
