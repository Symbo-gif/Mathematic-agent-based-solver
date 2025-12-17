# Symbo Mathematical Equation Catalog

**Generated:** 2025-12-14
**Purpose:** Comprehensive catalog of ALL mathematical equations used for testing, documentation, and development across the Symbo codebase.

---

## Table of Contents

1. [Ultra-Edge Equations (25)](#ultra-edge-equations-25)
2. [Edgiest Edge Equations (50)](#edgiest-edge-equations-50)
3. [Edgy Research-Level Equations (100)](#edgy-research-level-equations-100)
4. [Quick 500-Equation Suite](#quick-500-equation-suite)
5. [Comprehensive Stress Test Equations](#comprehensive-stress-test-equations)
6. [Research-Grade Equations (600)](#research-grade-equations-600)
7. [E2E Domain-Specific Test Equations](#e2e-domain-specific-test-equations)
8. [SymPy-Free Native Equations (25)](#sympy-free-native-equations-25)

---

## Ultra-Edge Equations (25)

**Source:** `scripts/ultra_edge_25_test.py`
**Difficulty:** Extreme - At the boundary of CAS capabilities
**Purpose:** Higher-order asymptotics, special functions with correction terms, Diophantine edge cases

### Higher-Order Asymptotics (1-10)

| # | Equation | Description | Expected Result |
|---|----------|-------------|-----------------|
| 1 | `limit((log(Gamma(x)) - (x - 1/2)*log(x) + x - 1/2*log(2*pi) - 1/(12*x)) * x, x, oo)` | Stirling next correction * x | Next Stirling term |
| 2 | `limit((zeta(1 + 1/x) - x - gamma - 1/(2*x)) * x, x, oo)` | Zeta pole next correction * x | Stieltjes constant |
| 3 | `limit((Ei(x) - gamma - log(abs(x)) - x - x**2/4 - x**3/18)/x**4, x, 0)` | Ei 4th order Taylor | x^4 coefficient |
| 4 | `limit((erf(x) - 2*x/sqrt(pi) + 2*x**3/(3*sqrt(pi)) - 4*x**5/(15*sqrt(pi)))/x**7, x, 0)` | erf 7th order Taylor | x^7 coefficient |
| 5 | `limit((BesselJ(0,x) - sqrt(2/(pi*x))*cos(x - pi/4) + 1/(8*sqrt(2*pi)*x**(3/2))*sin(x - pi/4))*x**(5/2), x, oo)` | BesselJ0 2nd order asymp | 2nd order correction |
| 6 | `limit((BesselY(0,x) - sqrt(2/(pi*x))*sin(x - pi/4) - 1/(8*sqrt(2*pi)*x**(3/2))*cos(x - pi/4))*x**(5/2), x, oo)` | BesselY0 2nd order asymp | 2nd order correction |
| 7 | `limit((Ai(x) - 1/(2*sqrt(pi))*x**(-1/4)*exp(-2*x**(3/2)/3)*(1 - 5/(48*x**(3/2)))), x, oo)` | Airy Ai 2nd order asymp | 2nd order correction |
| 8 | `limit((Bi(x) - 1/sqrt(pi)*x**(-1/4)*exp(2*x**(3/2)/3)*(1 + 5/(48*x**(3/2)))), x, oo)` | Airy Bi 2nd order asymp | 2nd order correction |
| 9 | `limit((x*log(log(x)) - log(x))/log(log(x)), x, oo)` | Nested log difference ratio | ∞ |
| 10 | `limit((log(log(log(x))) - log(log(x))/log(x))*log(x), x, oo)` | Triple nested log product | Logarithmic behavior |

### Brutal Series/Products/NT Blends (11-16)

| # | Equation | Description | Expected Result |
|---|----------|-------------|-----------------|
| 11 | `summation(((-1)**n * log(n))/sqrt(n), (n,2,oo))` | Alt log/sqrt series | Convergent value |
| 12 | `summation(mu(n)*log(n)/n, (n,2,oo))` | Mobius log series | Related to PNT |
| 13 | `summation((H_n - log(n) - gamma)/n, (n,1,oo))` | Harmonic correction sum | Convergent |
| 14 | `summation(((-1)**n)/(n*(log(n))*(log(log(n)))), (n,3,oo))` | Nested log alt series | Convergent |
| 15 | `product((1 - 1/p**s), (p, primes))` | Euler product zeta | 1/ζ(s) |
| 16 | `summation(q**(n**2 + n), (n,-oo,oo))` | Theta-like series | Jacobi theta |

### Special Function Integrals (17-20)

| # | Equation | Description | Expected Result |
|---|----------|-------------|-----------------|
| 17 | `integrate(log(1 - x)/x, (x,0,1))` | Dilogarithm at 1 | -π²/6 |
| 18 | `integrate((log(x))**2/(1 + x), (x,0,1))` | Log²/(1+x) integral | π²/12 - (log 2)²/2 |
| 19 | `integrate((x - floor(x) - 1/2)/x**2, (x,1,oo))` | Fractional part integral | Related to γ |
| 20 | `integrate(exp(-x**2)*(cos(2*x) - 1), (x,0,oo))` | Gaussian oscillatory diff | Fourier-Gaussian |

### Diophantine Edge Cases (21-23)

| # | Equation | Description | Expected Result |
|---|----------|-------------|-----------------|
| 21 | `diophantine(x**3 + y**3 + z**3 - 33)` | Sum of 3 cubes = 33 | Integer solutions |
| 22 | `diophantine(2*x**2 + 3*y**2 + 5*z**2 - 7*w**2 - 1)` | Quaternary mixed | Integer solutions |
| 23 | `diophantine(x**4 + y**4 + z**4 - w**4)` | Sum of 4th powers | Known to have no nontrivial solutions |

### Mixed Asymptotic/Special-Function Hybrids (24-25)

| # | Equation | Description | Expected Result |
|---|----------|-------------|-----------------|
| 24 | `limit((Li(x) - x/log(x) - x/(log(x))**2)/(x/(log(x))**3), x, oo)` | Li 3rd order asymp | 6 |
| 25 | `limit((BesselJ(0,x) + I*BesselY(0,x))/(sqrt(2/(pi*x))*exp(I*(x - pi/4))), x, oo)` | Complex Bessel Hankel | 1 (Hankel function) |

---

## Edgiest Edge Equations (50)

**Source:** `scripts/edgiest_50_test.py`
**Difficulty:** Extreme edge cases
**Purpose:** Boundary testing for CAS/LLM capabilities

### Extreme Asymptotics / Stokes Behavior (1-15)

| # | Equation | Description |
|---|----------|-------------|
| 1 | `limit((Gamma(x + a)/Gamma(x) - x**a) / (x**(a-1)), x, oo)` | Gamma ratio asymptotic correction |
| 2 | `limit((log(Gamma(x)) - (x - 1/2)*log(x) + x - 1/2*log(2*pi)), x, oo)` | Stirling remainder |
| 3 | `limit((zeta(1 + 1/x) - x - gamma), x, oo)` | Zeta pole correction |
| 4 | `limit((log(zeta(1 + 1/x)) - log(x)), x, oo)` | Log zeta asymptotic |
| 5 | `limit((x*log(log(x)))/log(x), x, oo)` | Nested log growth |
| 6 | `limit((log(log(log(x))))/log(log(x)), x, oo)` | Triple nested log |
| 7 | `limit((Ei(x) - gamma - log(abs(x)) - x - x**2/4)/x**3, x, 0)` | Ei small arg Taylor |
| 8 | `limit((erf(x) - 2*x/sqrt(pi) + 2*x**3/(3*sqrt(pi)))/x**5, x, 0)` | erf Taylor remainder |
| 9 | `limit((BesselJ(0,x) - sqrt(2/(pi*x))*cos(x - pi/4)), x, oo)` | Bessel J0 asymptotic diff |
| 10 | `limit((BesselY(0,x) - sqrt(2/(pi*x))*sin(x - pi/4)), x, oo)` | Bessel Y0 asymptotic diff |
| 11 | `limit((Ai(x) - 1/(2*sqrt(pi))*x**(-1/4)*exp(-2*x**(3/2)/3)), x, oo)` | Airy Ai asymptotic diff |
| 12 | `limit((Bi(x) - 1/sqrt(pi)*x**(-1/4)*exp(2*x**(3/2)/3)), x, oo)` | Airy Bi asymptotic diff |
| 13 | `limit((log(Gamma(x+1)) - (x+1/2)*log(x) + x - 1/2*log(2*pi)), x, oo)` | Log-Gamma Stirling |
| 14 | `limit((factorial(n) - sqrt(2*pi*n)*(n/E)**n)/((n/E)**n*sqrt(n)), n, oo)` | Stirling correction ratio |
| 15 | `limit((log(Gamma(n+1)) - (n*log(n) - n + 1/2*log(2*pi*n))), n, oo)` | Log factorial Stirling |

### Wild Series/Products (16-25)

| # | Equation | Description |
|---|----------|-------------|
| 16 | `summation(((-1)**n * log(n))/n, (n,2,oo))` | Alt log series |
| 17 | `summation(((-1)**n * log(n))/sqrt(n), (n,2,oo))` | Alt log/sqrt series |
| 18 | `summation((mu(n)*log(n))/n, (n,2,oo))` | Mobius log series |
| 19 | `summation(mu(n)/n, (n,1,oo))` | Prime number theorem form |
| 20 | `summation(Lambda(n)/n**s, (n,2,oo))` | von Mangoldt Dirichlet |
| 21 | `summation((H_n - log(n) - gamma)/n, (n,1,oo))` | Harmonic correction sum |
| 22 | `summation(((-1)**n * (H_n - log(n) - gamma)), (n,1,oo))` | Alt harmonic correction |
| 23 | `summation(((-1)**n)/(n*(log(n))*(log(log(n)))), (n,3,oo))` | Nested log alt series |
| 24 | `summation(1/(n*(log(n))*(log(log(n))**2)), (n,3,oo))` | Nested log convergent |
| 25 | `product((1 - 1/p**2), (p, primes))` | Euler product for zeta(2) |

### Ugly Integrals (26-40)

| # | Equation | Description | Expected |
|---|----------|-------------|----------|
| 26 | `integrate(log(1 - x)/x, (x,0,1))` | Dilog at 1 | -π²/6 |
| 27 | `integrate(log(1 + x)/x, (x,0,1))` | Alt dilog | π²/12 |
| 28 | `integrate(log(x)/(1 + x), (x,0,1))` | Log/(1+x) integral | -π²/12 |
| 29 | `integrate((log(x))**2/(1 + x), (x,0,1))` | Log²/(1+x) integral | Complex |
| 30 | `integrate(log(sin(x)), (x,0,pi))` | Log-sin over [0,π] | -π log(2) |
| 31 | `integrate(log(sin(x)), (x,0,pi/2))` | Log-sin over [0,π/2] | -π log(2)/2 |
| 32 | `integrate((x - floor(x) - 1/2)/x**2, (x,1,oo))` | Fractional part integral | Related to γ |
| 33 | `integrate(sin(x**2), (x,0,oo))` | Fresnel sine | √(π/8) |
| 34 | `integrate(cos(x**2), (x,0,oo))` | Fresnel cosine | √(π/8) |
| 35 | `integrate(exp(-x**2)*(cos(2*x) - 1), (x,0,oo))` | Gaussian oscillatory | Fourier integral |
| 36 | `integrate((sin(x)/x)**3, (x,0,oo))` | Sinc³ integral | 3π/8 |
| 37 | `integrate((sin(x)/x)*exp(-epsilon*x), (x,0,oo))` | Damped sinc (ε>0) | arctan(1/ε) |
| 38 | `integrate(x**(s-1)/(1 - x), (x,0,1))` | Analytic continuation | Requires Re(s) > 0 |
| 39 | `integrate(x**(s-1)/(1 + x), (x,0,oo))` | Beta function form | π/sin(πs) |
| 40 | `integrate(exp(-x**2) * hermite(n, x) * hermite(m, x), (x,-oo,oo))` | Hermite orthogonality | δ_nm * 2^n * n! * √π |

### Diophantine/NT at the Edge (41-48)

| # | Equation | Description |
|---|----------|-------------|
| 41 | `diophantine(x**3 + y**3 + z**3 - 33)` | Sum of 3 cubes = 33 |
| 42 | `diophantine(x**3 + y**3 + z**3 - 42)` | Sum of 3 cubes = 42 |
| 43 | `diophantine(x**3 + y**3 + z**3 - 114)` | Sum of 3 cubes = 114 |
| 44 | `diophantine(x**2 + y**2 + z**2 - 3*w**2)` | Quaternary quadratic |
| 45 | `diophantine(x**4 + y**4 + z**4 - w**4)` | Sum of 4th powers |
| 46 | `diophantine(x**2 - 5*y**2 - 920)` | Generalized Pell |
| 47 | `diophantine(3*x**2 - 7*y**2 + 2*x - 5*y - 11)` | Mixed quadratic |
| 48 | `diophantine(2*x**2 + 3*y**2 + 5*z**2 - 7*w**2 - 1)` | Quaternary mixed |

### Pathological Cases (49-50)

| # | Equation | Description |
|---|----------|-------------|
| 49 | `limit((x**x * exp(-x**2) * sqrt(x)), x, oo)` | x^x * e^(-x²) * √x |
| 50 | `limit((Ai(x) + I*Bi(x))/exp(2*x**(3/2)/3), x, oo)` | Complex Airy asymptotic |

---

## Edgy Research-Level Equations (100)

**Source:** `scripts/edgy_100_test.py`
**Difficulty:** Research-level mathematics
**Purpose:** Advanced mathematical capability testing

### Categories

1. **Asymptotic Limits (25)** - Complex limit evaluations
2. **Nasty Series (20)** - Difficult series convergence
3. **Tough Integrals (20)** - Special function integrals
4. **Diophantine/NT (15)** - Number theory edge cases
5. **Probability/Stats (10)** - Moment generating functions
6. **Airy/Bessel (5)** - Mixed special functions

*(Full 100 equations available in source file)*

---

## Quick 500-Equation Suite

**Source:** `scripts/quick_500_test.py`
**Difficulty:** Mixed (Easy to Hard)
**Purpose:** Broad coverage testing across all domains

### Breakdown by Category

| Category | Count | Examples |
|----------|-------|----------|
| **Limits** | 78 | Taylor series, L'Hôpital, special functions |
| **Series** | 10 | Geometric, p-series, power series |
| **Integrals** | 10 | Gaussian, rational, trigonometric |
| **Derivatives** | 10 | Chain rule, product rule, higher order |
| **Linear Algebra** | 10 | Determinants, eigenvalues, matrix ops |
| **Probability** | 8 | Distributions, MGFs |
| **Physics** | 8 | Mechanics, waves, quantum |
| **Total** | ~134 | (Pattern continues to 500) |

### Sample Equations

**Limits:**
```
limit((sin(x) - x + x**3/6)/x**5, x, 0)
limit((1 + a/n)**(b*n), n, oo)
limit(n*(sqrt(n**2 + 1) - n), n, oo)
```

**Series:**
```
summation(1/n**p, (n,1,oo))
summation((-1)**n/n, (n,1,oo))
summation(n/2**n, (n,1,oo))
```

---

## Comprehensive Stress Test Equations

**Source:** `tests/test_comprehensive_stress.py`
**Purpose:** System-wide stress testing across all phases (0-6)

### Organized by Domain

#### Algebra Tests
- `factor(x**2 - 9)` → (x-3)(x+3)
- `factor(x**2 + 6*x + 9)` → (x+3)²
- `factor(x**3 - 6*x**2 + 11*x - 6)` → Cubic factorization
- `simplify((x**2 - 1)/(x - 1))` → x + 1
- `simplify(sin(x)**2 + cos(x)**2)` → 1
- `expand((x + 2)**3)` → x³ + 6x² + 12x + 8

#### Calculus Tests
- `diff(x**3 + 2*x**2 - 5*x + 1, x)` → 3x² + 4x - 5
- `diff(sin(x), x)` → cos(x)
- `diff(sin(x**2), x)` → 2x·cos(x²)
- `integrate(x**2, x)` → x³/3
- `integrate(sin(x), x)` → -cos(x)
- `integrate(x**2, (x, 0, 1))` → 1/3
- `limit(x**2, x, 2)` → 4
- `limit(sin(x)/x, x, 0)` → 1
- `limit((1 + 1/x)**x, x, oo)` → e

#### Linear Algebra Tests
- `Matrix([[1,2],[3,4]]).det()` → -2
- `Matrix([[1,2,3],[4,5,6],[7,8,9]]).det()` → 0
- `Matrix([[1,0,0],[0,2,0],[0,0,3]]).det()` → 6
- `Matrix([[1,2],[3,4]]) * Matrix([[5,6],[7,8]])` → [[19,22],[43,50]]

#### Number Theory Tests
- `isprime(17)` → True
- `isprime(15)` → False
- `factorint(12)` → {2: 2, 3: 1}
- `gcd(48, 18)` → 6
- `lcm(4, 6)` → 12
- `pow(3, 5, 7)` → 5

---

## Research-Grade Equations (600)

**Source:** `tests/stress_test_equations.py`
**Difficulty:** MIT Integration Bee, Putnam Competition level
**Purpose:** Research-level mathematical capability testing

### Category Breakdown

| Category | Count | Description |
|----------|-------|-------------|
| **Definite Integrals** | 100 | Gaussian, trig, log, rational functions |
| **Indefinite Integrals** | 50 | Basic, exponential, trig, radical |
| **Infinite Series** | 100 | Geometric, zeta, alternating, power |
| **Limits** | 100 | Basic, trig, exp, log, L'Hôpital |
| **Derivatives** | 50 | Chain, product, quotient, higher order |
| **Differential Equations** | 50 | 1st order, 2nd order, special ODEs |
| **Linear Algebra** | 50 | Determinants, eigenvalues, systems |
| **Number Theory** | 50 | GCD/LCM, modular, primes, Diophantine |
| **Probability/Statistics** | 50 | Combinatorics, distributions, MGFs |
| **Physics/Applied** | 50 | Mechanics, waves, E&M, thermo, QM |

### Sample High-Difficulty Equations

**Definite Integrals:**
```python
integrate(exp(-x**2), (x, -oo, oo))  # √π
integrate(x**2 * exp(-x**2), (x, -oo, oo))  # √π/2
integrate(sin(x)/x, (x, 0, oo))  # π/2
integrate(log(1 - x)/x, (x,0,1))  # -π²/6
integrate(log(sin(x)), (x,0,pi/2))  # -π·log(2)/2
```

**Infinite Series:**
```python
summation(1/n**2, (n, 1, oo))  # π²/6 (Basel problem)
summation((-1)**(n+1)/n**2, (n, 1, oo))  # π²/12
summation(1/(n*(n+1)), (n, 1, oo))  # 1 (telescoping)
summation(x**n/factorial(n), (n, 0, oo))  # e^x
```

**Limits:**
```python
limit((x**n - a**n)/(x - a), x, a)  # n·a^(n-1)
limit((1 + 1/n)**n, n, oo)  # e
limit(n! / (n/e)**n / sqrt(2*pi*n), n, oo)  # 1 (Stirling)
limit((H_n - log(n)), n, oo)  # γ (Euler-Mascheroni)
```

**Differential Equations:**
```python
dsolve(diff(y(x), x) - y(x), y(x))  # y = C·e^x
dsolve(diff(y(x), x, 2) + y(x), y(x))  # y = C₁·sin(x) + C₂·cos(x)
dsolve(diff(y(x), x, 2) + 2*diff(y(x), x) + y(x), y(x))  # Critical damping
```

---

## E2E Domain-Specific Test Equations

**Source:** `tests/test_e2e_domain_problems.py`
**Purpose:** End-to-end testing with known expected outputs

### Algebra Domain
- `factor(x**2 - 9)` → (x-3)(x+3)
- `factor(x**2 + 6*x + 9)` → (x+3)²
- `factor(x**3 - 6*x**2 + 11*x - 6)` → Roots at x=1,2,3
- `simplify((x**2 - 1)/(x - 1))` → x + 1
- `simplify(sin(x)**2 + cos(x)**2)` → 1
- `expand((x + 2)**3)` → x³ + 6x² + 12x + 8

### Calculus Domain
- `diff(x**3 + 2*x**2 - 5*x + 1, x)` → 3x² + 4x - 5
- `diff(sin(x), x)` → cos(x)
- `diff(sin(x**2), x)` → 2x·cos(x²)
- `diff(x*exp(x), x)` → (x+1)·e^x
- `integrate(x**2, x)` → x³/3 + C
- `integrate(sin(x), x)` → -cos(x) + C
- `integrate(x**2, (x, 0, 1))` → 1/3
- `limit(x**2, x, 2)` → 4
- `limit(sin(x)/x, x, 0)` → 1
- `limit((1 + 1/x)**x, x, oo)` → e ≈ 2.718

### Linear Algebra Domain
- `Matrix([[1,2],[3,4]]).det()` → -2
- `Matrix([[1,2,3],[4,5,6],[7,8,9]]).det()` → 0 (singular)
- `Matrix([[1,0,0],[0,2,0],[0,0,3]]).det()` → 6
- `Matrix([[1,2],[3,4]]) * Matrix([[5,6],[7,8]])` → [[19,22],[43,50]]
- `eigenvals(Matrix([[1,2],[2,1]]))` → [-1, 3]

### Number Theory Domain
- `isprime(17)` → True
- `isprime(15)` → False
- `factorint(12)` → {2: 2, 3: 1}
- `gcd(48, 18)` → 6
- `lcm(4, 6)` → 12
- `pow(3, 5, 7)` → 5 (modular exponentiation)

### Complex Numbers Domain
- `Abs(3 + 4*I)` → 5
- `I**2` → -1
- `exp(I*pi)` → -1 (Euler's formula)

### Statistics Domain
- `binomial(5, 2)` → 10
- `binomial(10, 0)` → 1
- Mean([1,2,3,4,5]) → 3
- Variance([1,2,3,4,5]) → 2
- `factorial(10) / factorial(7)` → 720 (permutations)

### Geometry Domain
- `sqrt(3**2 + 4**2)` → 5 (Pythagorean)
- `pi * 3**2` → 9π (circle area)
- Distance from (0,0) to (3,4) → 5
- `simplify(sin(x)**2 + cos(x)**2)` → 1
- `simplify(tan(x) - sin(x)/cos(x))` → 0

### Physics Domain
- KE = 0.5 * m * v² with m=2, v=3 → 9
- PE = m * g * h with m=5, g=10, h=2 → 100
- W = F * d with F=50, d=10 → 500
- v = d/t with d=100, t=10 → 10
- a = (v-u)/t with v=20, u=10, t=2 → 5
- V = I * R with I=2, R=5 → 10 (Ohm's law)

---

## SymPy-Free Native Equations (25)

**Source:** `scripts/run_25_equations.py`
**Purpose:** Test equations using native (SymPy-free) implementation
**Note:** These test the NO SYMPY philosophy of the Symbo project

### Asymptotics & Subtle Limits (1-8)

| # | Equation | Test Focus |
|---|----------|------------|
| 1 | `Gamma(x+1/2)/Gamma(x) - sqrt(x) - 1/(8*sqrt(x))` | Gamma ratio 3rd order correction |
| 2 | `log(Gamma(x)) - (x-1/2)*log(x) + x - log(2*pi)/2 - 1/(12*x)` | Log-Gamma 5th order Stirling |
| 3 | `(zeta(1+1/x) - x - gamma)*x` | Zeta Stieltjes constant |
| 4 | `(Li(x) - x/log(x) - x/log(x)**2 - 2*x/log(x)**3) / (x/log(x)**4)` | Li(x) 4th order → 6 |
| 5 | `log(log(x+1)) - log(log(x))` | Nested log diff → 0 |
| 6 | `(erf(x) - 2*x/sqrt(pi)) / x**3` | erf Taylor 5th order |
| 7 | `BesselJ(1,x) / (sqrt(2/(pi*x)) * cos(x - 3*pi/4))` | BesselJ normalization |
| 8 | `Ai(x) * 2*sqrt(pi)*x**(1/4)*exp(2*x**(3/2)/3)` | Airy Ai 3rd correction |

### Number-Theoretic Series (9-14)

| # | Test | Implementation |
|---|------|----------------|
| 9 | Alternating log series | `alternating_log_series(100)` |
| 10 | Möbius function μ(1-10) | `[mobius(n) for n in range(1,11)]` → [1,-1,-1,0,-1,1,-1,0,0,1] |
| 11 | von Mangoldt Λ(1-10) | `[mangoldt(n) for n in range(1,11)]` |
| 12 | Prime product (Euler) | `prime_product(lambda p: 1/(1-1/p**2))` → π²/6 |
| 13 | Euler totient φ(1-10) | `[totient(n) for n in range(1,11)]` → [1,1,2,2,4,2,6,4,6,4] |
| 14 | Möbius log squared | `evaluate_nt_series('mobius_log_squared')` |

### Special Integrals (15-19)

| # | Integral | Expected |
|---|----------|----------|
| 15 | `∫ exp(-x⁴) dx from -∞ to ∞` | Γ(1/4)/2 |
| 16 | `∫ exp(-x⁶) dx from -∞ to ∞` | Γ(1/6)/3 |
| 17 | `∫ exp(-x²)cos(x) dx from -∞ to ∞` | √π·exp(-1/4) |
| 18 | `∫ exp(-x²)cos(2x) dx from -∞ to ∞` | √π·exp(-1) |
| 19 | `∫ exp(-x²) dx from -∞ to ∞` | √π |

### Diophantine Equations (20-22)

| # | Equation | Type |
|---|----------|------|
| 20 | `x³ + y³ + z³ = 2` | Sum of three cubes |
| 21 | `x³ + y³ + z³ = 33` | Sum of three cubes |
| 22 | `x² + y² + z² + w² = 7` | Lagrange four squares |

### Probabilistic/Special (23-25)

| # | Test | Value |
|---|------|-------|
| 23 | Mill's ratio pattern | `P(N > x) * x * sqrt(2*pi) * exp(x²/2)` |
| 24 | Stieltjes γ₁ constant | -0.0728158454836767 |
| 25 | Euler-Mascheroni γ | 0.5772156649015329 |

---

## Summary Statistics

### Total Unique Equations

| Source | Count | Difficulty Level |
|--------|-------|-----------------|
| Ultra-Edge | 25 | Extreme |
| Edgiest Edge | 50 | Extreme |
| Edgy Research | 100 | Research |
| Quick 500 Suite | ~134 documented | Mixed |
| Comprehensive Stress | ~150 | Mixed |
| Research-Grade | 600 | Research/Putnam |
| E2E Domain Tests | ~100 | Mixed |
| Native SymPy-Free | 25 | Extreme |

**Estimated Total Unique Equations:** ~900-1000

### Coverage by Mathematical Domain

| Domain | Equation Count | Test Coverage |
|--------|---------------|---------------|
| **Limits & Asymptotics** | ~250 | Excellent |
| **Definite Integrals** | ~150 | Excellent |
| **Infinite Series** | ~150 | Excellent |
| **Derivatives** | ~75 | Good |
| **Differential Equations** | ~60 | Good |
| **Linear Algebra** | ~75 | Good |
| **Number Theory** | ~100 | Excellent |
| **Probability/Statistics** | ~60 | Good |
| **Physics/Applied** | ~60 | Good |
| **Special Functions** | ~100 | Excellent |
| **Diophantine Equations** | ~30 | Moderate |

### Difficulty Distribution

- **Trivial/Basic:** ~10% (e.g., 2+2, x², sin(0))
- **Moderate:** ~30% (e.g., basic calculus, simple integrals)
- **Advanced:** ~40% (e.g., special functions, ODEs)
- **Research/Extreme:** ~20% (e.g., asymptotics, edge cases)

---

## Notes on Equation Organization

### Naming Conventions
- **Limit equations:** `limit(expr, var, point)`
- **Integration:** `integrate(expr, var)` or `integrate(expr, (var, a, b))`
- **Series:** `summation(expr, (var, start, end))`
- **Products:** `product(expr, (var, range))`
- **Derivatives:** `diff(expr, var)` or `diff(expr, var, order)`
- **ODEs:** `dsolve(ode, func)`
- **Diophantine:** `diophantine(equation)`

### Special Function Coverage
- Gamma function (Γ)
- Riemann zeta (ζ)
- Exponential integral (Ei)
- Error function (erf)
- Bessel functions (J, Y)
- Airy functions (Ai, Bi)
- Logarithmic integral (Li)
- Harmonic numbers (H_n)
- Möbius function (μ)
- von Mangoldt function (Λ)
- Euler totient (φ)

### Edge Case Categories
1. **Asymptotic expansions** - Higher-order terms
2. **Nested functions** - log(log(log(x)))
3. **Number-theoretic series** - Prime-related sums
4. **Special integrals** - Gaussian, Fresnel, etc.
5. **Diophantine extremes** - Sum of cubes, 4th powers
6. **Pathological limits** - x^x, exp(-x²)

---

## Gaps Identified for Future Test Generation

Based on this comprehensive catalog, the following areas need more coverage:

### Underrepresented Domains
1. **Topology** - No topological invariants tested
2. **Group Theory** - Limited abstract algebra
3. **Complex Analysis** - Few contour integrals
4. **Fourier Analysis** - Limited transform testing
5. **Partial Differential Equations** - None tested
6. **Tensor Calculus** - No tensor operations
7. **Variational Calculus** - No Euler-Lagrange equations
8. **Numerical Analysis** - No root-finding algorithms

### Missing Edge Cases
1. **Symbolic parameters** - More tests with arbitrary constants
2. **Piecewise functions** - Limited testing
3. **Implicit functions** - Implicit differentiation gaps
4. **Parametric equations** - Minimal coverage
5. **Polar/Cylindrical/Spherical** - Coordinate transforms

### Recommended New Test Categories
1. **Contour Integration** - Residue theorem applications
2. **Transform Methods** - Laplace, Fourier, Z-transforms
3. **Green's Functions** - PDE solutions
4. **Orthogonal Polynomials** - Legendre, Chebyshev, Hermite
5. **Elliptic Integrals** - Complete and incomplete
6. **Hypergeometric Functions** - ₂F₁, Meijer G
7. **q-Analogs** - q-series and q-calculus

---

## Usage Guidelines

### For Test Generation
1. **Check this catalog first** before creating new test equations
2. **Avoid exact duplicates** across test suites
3. **Document expected results** when adding new equations
4. **Tag difficulty level** (Trivial/Moderate/Advanced/Research/Extreme)
5. **Specify domain** for proper categorization

### For Performance Testing
- Use Quick 500 Suite for broad coverage
- Use Ultra-Edge/Edgiest for stress testing
- Use Research-Grade for benchmarking against mathematical standards

### For Documentation
- E2E Domain Tests have verified expected outputs
- Use these as canonical examples in docs
- Reference specific equation numbers when reporting issues

---

**End of Equation Catalog**
*This is a living document. Update as new test suites are added.*
