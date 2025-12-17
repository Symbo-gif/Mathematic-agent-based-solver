# CAS Benchmark Test Suite - Specific Problems and Expected Results

**Purpose**: Concrete test cases for evaluating symbolic mathematics systems
**Date**: 2025-12-15

---

## 1. Integration Benchmark Suite

### 1.1 Level 1: Elementary (All Systems Should Pass)

| Problem | Expected Result | Difficulty | Notes |
|---------|----------------|------------|-------|
| ∫ x dx | x²/2 + C | Trivial | Power rule |
| ∫ x² dx | x³/3 + C | Trivial | Power rule |
| ∫ 1/x dx | ln\|x\| + C | Easy | Logarithm |
| ∫ e^x dx | e^x + C | Easy | Exponential |
| ∫ sin(x) dx | -cos(x) + C | Easy | Trigonometric |
| ∫ cos(x) dx | sin(x) + C | Easy | Trigonometric |
| ∫ sec²(x) dx | tan(x) + C | Easy | Trigonometric |
| ∫ 1/(1+x²) dx | arctan(x) + C | Easy | Inverse trig |
| ∫ 1/√(1-x²) dx | arcsin(x) + C | Easy | Inverse trig |
| ∫ 2x dx | x² + C | Trivial | Constant multiple |

**Expected Success Rate:**
- Mathematica/Maple: 100%
- SymPy: 100%
- Maxima: 100%
- Native (target): 100%

### 1.2 Level 2: Intermediate (Standard Techniques)

| Problem | Expected Result | Technique | Time (SymPy) |
|---------|----------------|-----------|--------------|
| ∫ x·e^x dx | xe^x - e^x + C | Integration by parts | ~100ms |
| ∫ x·sin(x) dx | sin(x) - x·cos(x) + C | Integration by parts | ~100ms |
| ∫ e^x·cos(x) dx | (e^x/2)(sin(x)+cos(x)) + C | Integration by parts (repeated) | ~200ms |
| ∫ x/(x²+1) dx | ln(x²+1)/2 + C | Substitution (u = x²+1) | ~50ms |
| ∫ sin(2x) dx | -cos(2x)/2 + C | Substitution (u = 2x) | ~50ms |
| ∫ tan(x) dx | -ln\|cos(x)\| + C or ln\|sec(x)\| + C | Rewrite as sin/cos | ~100ms |
| ∫ sec(x) dx | ln\|sec(x)+tan(x)\| + C | Multiply by (sec+tan)/(sec+tan) | ~150ms |
| ∫ x²·e^x dx | e^x(x² - 2x + 2) + C | Integration by parts (repeated) | ~200ms |
| ∫ ln(x) dx | x·ln(x) - x + C | Integration by parts | ~100ms |
| ∫ x·ln(x) dx | (x²/2)·ln(x) - x²/4 + C | Integration by parts | ~150ms |

**Expected Success Rate:**
- Mathematica/Maple: 100%
- SymPy: 95-100%
- Maxima: 95-100%
- Native (target): 80-90%

### 1.3 Level 3: Advanced (Trig Substitution, Special Techniques)

| Problem | Expected Result | Technique | Time (SymPy) |
|---------|----------------|-----------|--------------|
| ∫ √(a²-x²) dx | (x/2)√(a²-x²) + (a²/2)arcsin(x/a) + C | Trig substitution | ~500ms |
| ∫ 1/√(x²+a²) dx | ln\|x + √(x²+a²)\| + C | Trig substitution | ~300ms |
| ∫ 1/(x²-a²) dx | (1/2a)ln\|(x-a)/(x+a)\| + C | Partial fractions | ~200ms |
| ∫ x²/(x²+1)² dx | x/(2(x²+1)) + arctan(x)/2 + C | Trig substitution or reduction | ~400ms |
| ∫ sin³(x) dx | -cos(x) + cos³(x)/3 + C | Trig identity (sin²=1-cos²) | ~200ms |
| ∫ cos⁴(x) dx | 3x/8 + sin(2x)/4 + sin(4x)/32 + C | Power reduction | ~300ms |
| ∫ 1/(x·ln(x)) dx | ln\|ln(x)\| + C | Substitution (u = ln(x)) | ~100ms |
| ∫ e^(√x) dx | 2e^(√x)(√x - 1) + C | Substitution (u = √x) | ~200ms |
| ∫ x·√(x-1) dx | (2/5)(x-1)^(5/2) + (2/3)(x-1)^(3/2) + C | Substitution | ~200ms |
| ∫ 1/(e^x + 1) dx | x - ln(e^x + 1) + C | Multiply by e^(-x)/e^(-x) | ~150ms |

**Expected Success Rate:**
- Mathematica/Maple: 100%
- SymPy: 80-90%
- Maxima: 85-95%
- Native (target): 50-70%

### 1.4 Level 4: Expert (Risch Algorithm, Special Functions)

| Problem | Expected Result | Method | Notes |
|---------|----------------|--------|-------|
| ∫ e^(x²) dx | (√π/2)·erf(x) + C | Special function (error function) | Non-elementary |
| ∫ sin(x)/x dx | Si(x) + C | Special function (sine integral) | Non-elementary |
| ∫ e^x/x dx | Ei(x) + C | Special function (exponential integral) | Non-elementary |
| ∫ √(x³+1) dx | Requires elliptic integrals | Elliptic integral | Non-elementary |
| ∫ 1/√(x³+x²+x+1) dx | Elliptic integral of first kind | Elliptic integral | Very difficult |
| ∫ e^x/(e^(2x)+1) dx | arctan(e^x) + C | Substitution u=e^x | Requires insight |
| ∫ x·tan⁻¹(x) dx | ((x²+1)tan⁻¹(x) - x)/2 + C | Integration by parts | Complex |
| ∫ (x⁴+1)/(x⁵+x+1) dx | Requires Risch algorithm | Rational functions | Algorithmically hard |
| ∫ x^x dx | No elementary form | None exists | Fundamentally impossible |
| ∫ e^(-x²) dx | (√π/2)·erf(x) + C | Gaussian integral | Non-elementary |

**Expected Success Rate:**
- Mathematica: 85-95% (returns special functions)
- Maple: 85-90%
- SymPy: 60-70%
- Maxima: 65-75%
- Native (target): 20-40%

---

## 2. Differentiation Benchmark Suite

### 2.1 Basic Derivatives (All Systems: 100%)

| Problem | Expected Result | Rule |
|---------|----------------|------|
| d/dx (x²) | 2x | Power rule |
| d/dx (x^n) | n·x^(n-1) | Power rule |
| d/dx (e^x) | e^x | Exponential |
| d/dx (ln(x)) | 1/x | Logarithm |
| d/dx (sin(x)) | cos(x) | Trigonometric |
| d/dx (cos(x)) | -sin(x) | Trigonometric |
| d/dx (tan(x)) | sec²(x) | Trigonometric |
| d/dx (arcsin(x)) | 1/√(1-x²) | Inverse trig |
| d/dx (arctan(x)) | 1/(1+x²) | Inverse trig |
| d/dx (a·f(x)) | a·f'(x) | Constant multiple |

### 2.2 Product and Chain Rules

| Problem | Expected Result | Rule |
|---------|----------------|------|
| d/dx (x·sin(x)) | sin(x) + x·cos(x) | Product rule |
| d/dx (x²·e^x) | e^x(x² + 2x) | Product rule |
| d/dx (sin(x)·cos(x)) | cos²(x) - sin²(x) = cos(2x) | Product rule + simplification |
| d/dx (sin(x²)) | 2x·cos(x²) | Chain rule |
| d/dx (e^(x²)) | 2x·e^(x²) | Chain rule |
| d/dx (ln(x²+1)) | 2x/(x²+1) | Chain rule |
| d/dx (sin(cos(x))) | -sin(x)·cos(cos(x)) | Chain rule (nested) |
| d/dx (e^(sin(x))) | cos(x)·e^(sin(x)) | Chain rule |
| d/dx ((x²+1)^10) | 20x(x²+1)^9 | Chain rule (power) |
| d/dx (√(x²+1)) | x/√(x²+1) | Chain rule |

### 2.3 Quotient Rule

| Problem | Expected Result | Method |
|---------|----------------|--------|
| d/dx (x/sin(x)) | (sin(x) - x·cos(x))/sin²(x) | Quotient rule |
| d/dx (e^x/x) | e^x(x-1)/x² | Quotient rule |
| d/dx (ln(x)/x) | (1 - ln(x))/x² | Quotient rule |
| d/dx ((x²+1)/(x²-1)) | -4x/(x²-1)² | Quotient rule |
| d/dx (tan(x)) | sec²(x) | Quotient rule (sin/cos) |

### 2.4 Implicit Differentiation

| Problem | Given Relation | Expected dy/dx |
|---------|---------------|----------------|
| Circle | x² + y² = r² | -x/y |
| Ellipse | x²/a² + y²/b² = 1 | -(b²x)/(a²y) |
| Implicit poly | x³ + y³ = 6xy | (2y - x²)/(y² - 2x) |
| Exponential | e^(xy) = x + y | (1 - ye^(xy))/(xe^(xy) - 1) |

### 2.5 Higher-Order Derivatives

| Problem | Expected d²/dx² | Notes |
|---------|----------------|-------|
| y = x³ | 6x | Simple |
| y = sin(x) | -sin(x) | Trigonometric |
| y = e^x | e^x | Exponential |
| y = ln(x) | -1/x² | Logarithmic |
| y = x·e^x | e^x(x+2) | Product rule applied twice |

**Performance Target:**
- All derivatives: < 10ms (SymPy achieves 1-5ms)
- Complex derivatives: < 50ms

---

## 3. Polynomial Benchmark Suite

### 3.1 Polynomial Arithmetic

| Operation | Input | Expected Output | Time (SymPy) |
|-----------|-------|----------------|--------------|
| Add | (x²+2x+1) + (x²-2x+1) | 2x² + 2 | ~1ms |
| Subtract | (x²+2x+1) - (x²-2x+1) | 4x | ~1ms |
| Multiply | (x+1)(x-1) | x² - 1 | ~1ms |
| Multiply | (x+1)² | x² + 2x + 1 | ~1ms |
| Expand | (x+1)³ | x³ + 3x² + 3x + 1 | ~2ms |
| Expand | (x+y)⁴ | x⁴+4x³y+6x²y²+4xy³+y⁴ | ~5ms |

### 3.2 Polynomial Factorization

| Problem | Expected Result | Difficulty | Time (SymPy) |
|---------|----------------|------------|--------------|
| x² - 1 | (x-1)(x+1) | Trivial | ~5ms |
| x² + 2x + 1 | (x+1)² | Easy | ~5ms |
| x² - 5x + 6 | (x-2)(x-3) | Easy | ~10ms |
| x³ - 1 | (x-1)(x²+x+1) | Medium | ~20ms |
| x⁴ - 1 | (x-1)(x+1)(x²+1) | Medium | ~30ms |
| x⁴ + 4 | (x²+2x+2)(x²-2x+2) | Hard | ~100ms |
| x⁶ - 1 | (x-1)(x+1)(x²+x+1)(x²-x+1) | Hard | ~150ms |

### 3.3 GCD Computation

| Polynomials | Expected GCD | Time (SymPy) |
|------------|--------------|--------------|
| x²-1, x²+2x+1 | x+1 | ~10ms |
| x³-1, x²-1 | x-1 | ~15ms |
| x⁴-1, x³-1 | x-1 | ~20ms |

### 3.4 Polynomial Division

| Dividend | Divisor | Quotient | Remainder |
|----------|---------|----------|-----------|
| x³+1 | x+1 | x²-x+1 | 0 |
| x³+x²+1 | x+1 | x²+1 | 0 |
| x⁴+1 | x²+1 | x²+1 | -2x² |

---

## 4. Equation Solving Benchmark Suite

### 4.1 Linear Equations

| Equation | Solution | Method |
|----------|----------|--------|
| 2x + 3 = 7 | x = 2 | Algebraic |
| ax + b = 0 | x = -b/a | General form |
| 3x + 2y = 5, x - y = 1 | x=7/5, y=2/5 | System (2x2) |

### 4.2 Quadratic Equations

| Equation | Solutions | Method |
|----------|-----------|--------|
| x² - 1 = 0 | x = ±1 | Factoring |
| x² + 2x + 1 = 0 | x = -1 (double root) | Perfect square |
| x² - 5x + 6 = 0 | x = 2, x = 3 | Factoring |
| x² + x + 1 = 0 | x = (-1 ± i√3)/2 | Quadratic formula (complex) |
| ax² + bx + c = 0 | x = (-b ± √(b²-4ac))/2a | General quadratic formula |

**Performance Target:** < 50ms per equation

### 4.3 Cubic Equations

| Equation | Solutions | Method |
|----------|-----------|--------|
| x³ - 1 = 0 | x = 1, (-1±i√3)/2 | Cubic formula |
| x³ - 3x² + 3x - 1 = 0 | x = 1 (triple root) | (x-1)³ |
| x³ + x² - x - 1 = 0 | x = -1, ±1 | Factoring |

**Note:** Cubic formulas are complex. Most systems use numerical methods for general cubics.

### 4.4 Quartic Equations (Degree 4)

| Equation | Method | Notes |
|----------|--------|-------|
| x⁴ - 1 = 0 | Factoring | x = ±1, ±i |
| x⁴ + x² + 1 = 0 | Substitution u=x² | Complex solutions |

**Note:** General quartic formula exists but is extremely complex. Most systems use it.

### 4.5 Transcendental Equations

| Equation | Solution Method | Notes |
|----------|----------------|-------|
| e^x = 2 | Numerical | x = ln(2) = 0.693... |
| sin(x) = 0.5 | Analytical + numerical | x = π/6 + 2πn, 5π/6 + 2πn |
| log(x) = 1 | Analytical | x = e |

**Expected:** Numerical methods for general transcendental equations

---

## 5. Simplification Benchmark Suite

### 5.1 Algebraic Simplification

| Expression | Simplified Form | Technique |
|------------|----------------|-----------|
| (x+1)(x-1) | x² - 1 | Expansion |
| x²-1 | (x-1)(x+1) | Factoring |
| x/x | 1 (x ≠ 0) | Cancellation |
| (x²+2x+1)/(x+1) | x+1 (x ≠ -1) | Factoring + cancellation |
| (x²-1)/(x-1) | x+1 (x ≠ 1) | Factoring + cancellation |

### 5.2 Trigonometric Simplification

| Expression | Simplified Form | Identity |
|------------|----------------|----------|
| sin²(x) + cos²(x) | 1 | Pythagorean identity |
| tan²(x) + 1 | sec²(x) | Pythagorean identity |
| sin(2x) | 2sin(x)cos(x) | Double angle |
| cos(2x) | cos²(x) - sin²(x) | Double angle |
| sin(x)cos(x) | sin(2x)/2 | Reverse double angle |

### 5.3 Exponential/Logarithmic Simplification

| Expression | Simplified Form | Rule |
|------------|----------------|------|
| e^ln(x) | x | Inverse |
| ln(e^x) | x | Inverse |
| ln(x) + ln(y) | ln(xy) | Log product |
| ln(x) - ln(y) | ln(x/y) | Log quotient |
| a·ln(x) | ln(x^a) | Log power |
| e^a · e^b | e^(a+b) | Exponent sum |

---

## 6. Performance Benchmark Data

### 6.1 Large Polynomial Operations

**Multiply two degree-100 polynomials (1000 iterations):**
- Mathematica: ~50ms total (0.05ms per op)
- Maple: ~60ms total
- SymPy: ~5000ms total (5ms per op)
- Native (target): ~2000ms total (2ms per op)

**Factor degree-10 polynomial:**
- Mathematica: ~5ms
- Maple: ~8ms
- SymPy: ~100ms
- Native (target): ~200ms

### 6.2 Integration Performance (100 problems)

**Easy integrals (Level 1):**
- Mathematica: ~100ms total
- SymPy: ~1000ms total
- Native (target): ~800ms total

**Medium integrals (Level 2):**
- Mathematica: ~500ms total
- SymPy: ~10,000ms total
- Native (target): ~15,000ms total

### 6.3 Memory Usage

**Store 1000 symbolic expressions:**
- Mathematica: ~5MB
- SymPy: ~50MB
- Native (target): ~25MB

---

## 7. Correctness Validation Tests

### 7.1 Integration Verification (Differentiate Result)

For each integral result, verify: d/dx(∫f(x)dx) = f(x)

**Example:**
- Computed: ∫ x·e^x dx = xe^x - e^x + C
- Verify: d/dx(xe^x - e^x) = e^x + xe^x - e^x = xe^x ✓

### 7.2 Numerical Verification

Compare symbolic result with numerical evaluation at test points.

**Example:**
- Symbolic: ∫₀¹ x² dx = 1/3
- Numerical: Simpson's rule or trapezoid rule ≈ 0.333...
- Match within tolerance: ✓

### 7.3 Known Value Tests

Use published tables (Gradshteyn & Ryzhik, CRC Standard Mathematical Tables).

**Example definite integrals:**
- ∫₀^∞ e^(-x²) dx = √π/2 = 0.886...
- ∫₀^(π/2) sin(x) dx = 1
- ∫₀^π sin²(x) dx = π/2

---

## 8. Stress Tests

### 8.1 Large Expression Handling

**Create deeply nested expression:**
```
f(x) = ((((x+1)²+1)²+1)²+1)²
```
- Expand fully
- Measure: time, memory, correctness

**Expected:**
- Mathematica: Handles depth 10+
- SymPy: Handles depth 8-10 (becomes slow)
- Native (target): Handle depth 5-7

### 8.2 Many Variables

**Multivariate polynomial:**
```
(x₁ + x₂ + ... + x₁₀)³
```
- Number of terms: 220 (from binomial coefficient)
- Measure expansion time and memory

### 8.3 High-Degree Polynomials

**Expand (x+1)^100:**
- 101 terms
- Coefficients up to C(100,50) ≈ 10²⁹
- Tests: bignum arithmetic, memory management

---

## 9. Real-World Application Tests

### 9.1 Physics Problems

**Kinematics:**
- Position: s(t) = ½at² + v₀t + s₀
- Velocity: v(t) = d/dt(s(t)) = at + v₀
- Acceleration: a(t) = d/dt(v(t)) = a

**Electromagnetic:**
- ∫ E·dl for electric potential
- ∫∫ B·dA for magnetic flux

### 9.2 Engineering Problems

**Beam deflection:**
- Moment: M(x) = integral of load
- Slope: dy/dx = integral of M/(EI)
- Deflection: y = integral of slope

### 9.3 Economics Problems

**Marginal cost/revenue:**
- Cost C(x), Revenue R(x)
- Marginal cost: MC = dC/dx
- Profit maximization: solve dP/dx = 0

---

## 10. Recommended Test Suite Implementation

### Phase 1: Core Functionality (Week 1-2)
- All Level 1 integration problems (10 tests)
- All basic derivatives (10 tests)
- Polynomial arithmetic (6 tests)
- Linear + quadratic equations (8 tests)
- **Target: 80% pass rate**

### Phase 2: Standard Techniques (Week 3-4)
- Level 2 integration (10 tests)
- Product/chain rule derivatives (10 tests)
- Polynomial factorization (7 tests)
- Cubic equations (3 tests)
- **Target: 70% pass rate**

### Phase 3: Advanced Features (Month 2)
- Level 3 integration (10 tests)
- Implicit differentiation (4 tests)
- Simplification suite (15 tests)
- **Target: 60% pass rate**

### Phase 4: Expert Level (Month 3+)
- Level 4 integration with special functions
- Large expression handling
- Stress tests
- **Target: 40% pass rate**

---

## 11. Benchmark Scoring System

### Overall CAS Capability Score

**Formula:**
```
Score = (L1_pass * 1.0 + L2_pass * 2.0 + L3_pass * 3.0 + L4_pass * 4.0) / Total_tests
```

**Interpretation:**
- Score 3.5-4.0: World-class (Mathematica, Maple)
- Score 2.5-3.5: Professional (SymPy, Maxima, SageMath)
- Score 1.5-2.5: Educational/Research (acceptable for learning)
- Score 0.5-1.5: Prototype (early development)
- Score < 0.5: Proof of concept

**Symbo Native Target:**
- Month 1: Score 1.0-1.5
- Month 3: Score 1.5-2.0
- Month 6: Score 2.0-2.5
- Year 1: Score 2.5-3.0 (with library fallback)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-15
**Purpose**: Concrete benchmarks for Symbo project evaluation
