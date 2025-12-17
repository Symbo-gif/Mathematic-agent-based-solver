# 100 Mathematical Equations That Are Notoriously Difficult for LLMs

This document compiles 100 mathematical problems specifically chosen because they expose common LLM weaknesses. Each equation is annotated with:
- The problem in parseable format
- The correct answer
- Why LLMs typically fail
- Difficulty rating (1-10)

## Category 1: Symbolic Integration (20 equations)

### 1.1 Non-Elementary Integrals (5 equations)

**1. Gaussian Integral**
```
integrate(exp(-x**2), (x, -oo, oo))
```
- **Answer**: `sqrt(pi)`
- **Why LLMs fail**: Requires recognizing this as a special function; naive symbolic manipulation doesn't work. LLMs often try term-by-term integration or miss the polar coordinate trick.
- **Difficulty**: 7/10

**2. Error Function Integral**
```
integrate(exp(-x**2), (x, 0, 1))
```
- **Answer**: `sqrt(pi)*erf(1)/2`
- **Why LLMs fail**: Must recognize that the antiderivative is not elementary and express in terms of erf(x). LLMs often hallucinate a closed form.
- **Difficulty**: 8/10

**3. Sine Integral (Si)**
```
integrate(sin(x)/x, (x, 0, oo))
```
- **Answer**: `pi/2`
- **Why LLMs fail**: The integrand has a removable singularity at x=0. LLMs struggle with improper integrals requiring contour integration or special function knowledge.
- **Difficulty**: 8/10

**4. Fresnel Sine Integral**
```
integrate(sin(x**2), (x, 0, oo))
```
- **Answer**: `sqrt(pi/8)` or `(1/2)*sqrt(pi/2)`
- **Why LLMs fail**: Requires Fresnel integral S(infinity) = 1/2, often confused with regular sine integral. LLMs miss the quadratic argument significance.
- **Difficulty**: 9/10

**5. Fresnel Cosine Integral**
```
integrate(cos(x**2), (x, 0, oo))
```
- **Answer**: `sqrt(pi/8)` or `(1/2)*sqrt(pi/2)`
- **Why LLMs fail**: Same as Fresnel sine; requires knowledge of C(infinity) = 1/2. LLMs often give different values for S and C.
- **Difficulty**: 9/10

### 1.2 Elliptic Integrals (5 equations)

**6. Complete Elliptic Integral of First Kind**
```
integrate(1/sqrt((1 - x**2)*(1 - k**2*x**2)), (x, 0, 1))
```
- **Answer**: `K(k)` where K is the complete elliptic integral
- **Why LLMs fail**: Don't recognize the canonical form; attempt algebraic substitutions that lead nowhere. Often confuse with standard arcsin integral.
- **Difficulty**: 9/10

**7. Complete Elliptic Integral of Second Kind**
```
integrate(sqrt(1 - k**2*x**2)/sqrt(1 - x**2), (x, 0, 1))
```
- **Answer**: `E(k)` where E is the complete elliptic integral
- **Why LLMs fail**: Similar to K(k) but with square root in numerator. LLMs miss the distinction and provide wrong formulas.
- **Difficulty**: 9/10

**8. Arc Length of Ellipse (Quarter)**
```
integrate(sqrt(1 - (1 - b**2/a**2)*x**2), (x, 0, a))
```
- **Answer**: `a*E(sqrt(1 - b**2/a**2))` where E is elliptic integral
- **Why LLMs fail**: Arc length problems require recognizing elliptic integral form after substitution. LLMs give approximate or wrong answers.
- **Difficulty**: 8/10

**9. Pendulum Period Integral**
```
integrate(1/sqrt(cos(theta) - cos(theta_0)), (theta, 0, theta_0))
```
- **Answer**: Elliptic integral expression involving K(k)
- **Why LLMs fail**: Physics context confuses symbolic manipulation. Requires half-angle substitution leading to elliptic form.
- **Difficulty**: 9/10

**10. Jacobi Elliptic Function Inverse**
```
integrate(1/sqrt((1 - x**2)*(1 - m*x**2)), (x, 0, z))
```
- **Answer**: `F(arcsin(z), m)` incomplete elliptic integral
- **Why LLMs fail**: Similar to complete case but with variable upper limit. LLMs confuse F and K notation.
- **Difficulty**: 9/10

### 1.3 Improper Integrals with Singularities (5 equations)

**11. Logarithmic Singularity at 0**
```
integrate(log(x)/(1 + x), (x, 0, 1))
```
- **Answer**: `-pi**2/12`
- **Why LLMs fail**: Singularity at x=0 requires careful limiting process. LLMs miss the connection to dilogarithm and zeta values.
- **Difficulty**: 8/10

**12. Double Logarithm Product**
```
integrate(log(x)*log(1 - x), (x, 0, 1))
```
- **Answer**: `2 - pi**2/6`
- **Why LLMs fail**: Integration by parts leads to polylogarithm Li_2(1) = zeta(2). LLMs lose track of boundary terms.
- **Difficulty**: 9/10

**13. Cauchy Principal Value**
```
integrate(sin(x)/x, (x, -oo, oo))
```
- **Answer**: `pi` (as principal value)
- **Why LLMs fail**: Must recognize this as principal value; naive evaluation gives undefined. LLMs confuse with (0, oo) case.
- **Difficulty**: 7/10

**14. Logarithm of Sine**
```
integrate(log(sin(x)), (x, 0, pi/2))
```
- **Answer**: `-pi*log(2)/2`
- **Why LLMs fail**: Singularity at x=0, requires Fourier series or complex analysis. LLMs rarely get the log(2) factor correct.
- **Difficulty**: 9/10

**15. Logarithm of Tangent**
```
integrate(log(tan(x)), (x, 0, pi/4))
```
- **Answer**: `-G` where G is Catalan's constant
- **Why LLMs fail**: Leads to Catalan's constant, a transcendental number LLMs don't recognize. Often give numerical approximations.
- **Difficulty**: 10/10

### 1.4 Rational Functions with Special Structure (5 equations)

**16. Residue with Complex Poles**
```
integrate(1/(x**4 + 1), (x, -oo, oo))
```
- **Answer**: `pi/sqrt(2)`
- **Why LLMs fail**: Requires residue theorem with complex poles at e^(i*pi/4), e^(3i*pi/4), etc. LLMs use wrong contour or miss poles.
- **Difficulty**: 8/10

**17. High-Order Pole**
```
integrate(1/((x**2 + 1)**3), (x, -oo, oo))
```
- **Answer**: `3*pi/8`
- **Why LLMs fail**: Third-order pole requires derivative of residue formula. LLMs misapply simple pole formula.
- **Difficulty**: 8/10

**18. Partial Fraction with Six Roots**
```
integrate(1/(x**6 + 1), (x, -oo, oo))
```
- **Answer**: `2*pi/3`
- **Why LLMs fail**: Six roots of unity involved; must select correct three in upper half-plane. LLMs get wrong combination.
- **Difficulty**: 8/10

**19. Rational Times Exponential**
```
integrate(x**2*exp(-x)/(1 + x), (x, 0, oo))
```
- **Answer**: Complex expression involving exponential integrals
- **Why LLMs fail**: No elementary antiderivative; requires series expansion or special functions. LLMs hallucinate closed forms.
- **Difficulty**: 9/10

**20. Rational Times Logarithm**
```
integrate(log(x)**2/(x**2 + 1), (x, 0, oo))
```
- **Answer**: `pi**3/8`
- **Why LLMs fail**: Involves zeta(3) and polylogarithms in intermediate steps. LLMs miss the pi^3 scaling.
- **Difficulty**: 9/10

## Category 2: Limits (15 equations)

### 2.1 Indeterminate Form 0/0 (5 equations)

**21. Multiple L'Hopital Applications**
```
limit((exp(x) - exp(-x) - 2*x)/(x - sin(x)), x, 0)
```
- **Answer**: `2`
- **Why LLMs fail**: Requires 3+ applications of L'Hopital's rule. LLMs lose track of derivative complexity or stop early.
- **Difficulty**: 7/10

**22. Trigonometric Trap**
```
limit((x - tan(x))/(x - sin(x)), x, 0)
```
- **Answer**: `-2`
- **Why LLMs fail**: Both numerator and denominator → 0, but negative answer surprises models. Often get +2 or 0.
- **Difficulty**: 8/10

**23. Taylor Series Required**
```
limit((exp(sin(x)) - exp(x))/x**3, x, 0)
```
- **Answer**: `-1/6`
- **Why LLMs fail**: L'Hopital becomes messy; Taylor series more elegant. LLMs either diverge with derivatives or miss the Taylor approach.
- **Difficulty**: 8/10

**24. Mixed Trig Forms**
```
limit((1 - cos(x)*cos(2*x))/x**2, x, 0)
```
- **Answer**: `5/2`
- **Why LLMs fail**: Product of cosines expands to sum; requires careful tracking of x^2 coefficients. LLMs make algebraic errors.
- **Difficulty**: 7/10

**25. Nested Trig**
```
limit((tan(x) - sin(x))/(sin(x) - x), x, 0)
```
- **Answer**: `-1`
- **Why LLMs fail**: Both parts are ~x^3/6, leading to careful sign analysis. LLMs miss the negative sign.
- **Difficulty**: 7/10

### 2.2 Indeterminate Form ∞ - ∞ (3 equations)

**26. Exponential Difference**
```
limit(x - x*exp(1/x), x, oo)
```
- **Answer**: `-1`
- **Why LLMs fail**: Both terms → ∞ but difference converges. Requires factoring x and Taylor expansion of exp(1/x).
- **Difficulty**: 8/10

**27. Square Root Difference**
```
limit(x**2*(sqrt(1 + 1/x) - 1 - 1/(2*x)), x, oo)
```
- **Answer**: `-1/8`
- **Why LLMs fail**: Second-order Taylor expansion needed; first-order cancels. LLMs stop after first-order.
- **Difficulty**: 8/10

**28. Inverse Trig Difference**
```
limit(x*(pi/2 - arctan(x)), x, oo)
```
- **Answer**: `1`
- **Why LLMs fail**: Substitution u=1/x helps, but LLMs try L'Hopital directly and get confused with derivatives.
- **Difficulty**: 7/10

### 2.3 Indeterminate Form 1^∞ (4 equations)

**29. Sine in Exponent**
```
limit((1 + sin(x)/x)**(x**2), x, oo)
```
- **Answer**: `e**(1/2)` or `sqrt(e)`
- **Why LLMs fail**: Must rewrite as exp(x^2 * log(1 + sin(x)/x)). LLMs miss the 1/2 factor in the exponential.
- **Difficulty**: 8/10

**30. Cosine to Reciprocal Power**
```
limit((cos(x))**(1/sin(x)**2), x, 0)
```
- **Answer**: `e**(-1/2)` or `1/sqrt(e)`
- **Why LLMs fail**: log(cos(x)) ~ -x^2/2, combining with 1/sin^2(x) ~ 1/x^2. LLMs mishandle log expansion.
- **Difficulty**: 9/10

**31. Rational Base to Large Power**
```
limit((x/(x + 1))**x, x, oo)
```
- **Answer**: `1/e`
- **Why LLMs fail**: (1 - 1/(x+1))^x form; LLMs confuse with (1 + 1/x)^x = e.
- **Difficulty**: 7/10

**32. Double Correction Term**
```
limit((1 + 1/x + 1/x**2)**(x**2), x, oo)
```
- **Answer**: `sqrt(e)` or `e**(1/2)`
- **Why LLMs fail**: Second term contributes to exponent; x^2 amplifies it. LLMs miss the 1/2 factor.
- **Difficulty**: 8/10

### 2.4 Indeterminate Form 0^0 (3 equations)

**33. X to the X**
```
limit(x**x, x, 0, '+')
```
- **Answer**: `1`
- **Why LLMs fail**: Must rewrite as exp(x*log(x)), then x*log(x) → 0. LLMs often say undefined or 0.
- **Difficulty**: 6/10

**34. Nested Exponential**
```
limit(x**(x**x), x, 0, '+')
```
- **Answer**: `0`
- **Why LLMs fail**: Outer exponent x^x → 1, but x^1 → 0. Requires careful order of limits. LLMs often get 1.
- **Difficulty**: 9/10

**35. Reciprocal to Sine Power**
```
limit((1/x)**sin(x), x, 0, '+')
```
- **Answer**: `1`
- **Why LLMs fail**: sin(x) → 0 faster than log(1/x) → ∞, giving exp(sin(x)*log(1/x)) → exp(0) = 1. LLMs say ∞ or 0.
- **Difficulty**: 8/10

## Category 3: Differential Equations (15 equations)

### 3.1 Bernoulli Equations (3 equations)

**36. Standard Bernoulli**
```
dsolve(diff(y(x), x) + y(x) - y(x)**2, y(x))
```
- **Answer**: `y(x) = 1/(1 - C*exp(-x))`
- **Why LLMs fail**: Requires v = y^(-1) substitution to linearize. LLMs miss the transformation or apply it incorrectly.
- **Difficulty**: 7/10

**37. Generalized Bernoulli**
```
dsolve(diff(y(x), x) - y(x)/x + y(x)**3/x**2, y(x))
```
- **Answer**: Complex form involving v = y^(-2)
- **Why LLMs fail**: Variable coefficient plus nonlinear term. LLMs confuse with separable or give up.
- **Difficulty**: 8/10

**38. Bernoulli with Trig**
```
dsolve(diff(y(x), x) + y(x)*tan(x) - y(x)**2*sec(x), y(x))
```
- **Answer**: Involves integrating factor and substitution
- **Why LLMs fail**: Combination of integrating factor method and Bernoulli substitution. LLMs apply only one technique.
- **Difficulty**: 8/10

### 3.2 Riccati Equations (3 equations)

**39. Standard Riccati**
```
dsolve(diff(y(x), x) - y(x)**2 - x**2, y(x))
```
- **Answer**: Involves Bessel functions
- **Why LLMs fail**: Riccati equations are generally non-elementary; this specific one requires Bessel function knowledge.
- **Difficulty**: 9/10

**40. Reducible Riccati**
```
dsolve(diff(y(x), x) - 2*y(x)/x + y(x)**2 - 1/x**2, y(x))
```
- **Answer**: Can be reduced if particular solution is known
- **Why LLMs fail**: Requires guessing particular solution y_p = 1/x, then substituting y = y_p + 1/v. LLMs don't guess.
- **Difficulty**: 9/10

**41. Riccati to Bessel**
```
dsolve(x*diff(y(x), x) + y(x)**2 - a*x, y(x))
```
- **Answer**: Related to Airy functions
- **Why LLMs fail**: Standard Riccati-to-second-order transformation leads to Airy equation. LLMs miss the connection.
- **Difficulty**: 10/10

### 3.3 Exact Equations (3 equations)

**42. Non-Obvious Exact Equation**
```
dsolve((2*x*y + y**2)*diff(y(x), x) + x**2 + 2*x*y(x), y(x))
```
- **Answer**: Implicit form F(x, y) = C
- **Why LLMs fail**: Must verify M_y = N_x (exactness condition), then integrate. LLMs skip verification or integrate incorrectly.
- **Difficulty**: 7/10

**43. Integrating Factor Needed**
```
dsolve((2*x + y)*dx + x*dy, y(x))
```
- **Answer**: Requires integrating factor µ(x) or µ(y)
- **Why LLMs fail**: Not exact initially; must find integrating factor. LLMs try to solve without checking exactness.
- **Difficulty**: 8/10

**44. Polar Coordinate Exact**
```
dsolve(x*diff(y(x), x) - y(x) + x*sqrt(x**2 + y(x)**2), y(x))
```
- **Answer**: Easier in polar coordinates
- **Why LLMs fail**: Looks complicated in Cartesian; polar substitution simplifies. LLMs don't recognize polar opportunity.
- **Difficulty**: 9/10

### 3.4 Systems of ODEs (3 equations)

**45. 2x2 Linear System**
```
dsolve([diff(x(t), t) - 2*x(t) + y(t), diff(y(t), t) + x(t) - 2*y(t)], [x(t), y(t)])
```
- **Answer**: Eigenvalue/eigenvector solution
- **Why LLMs fail**: Requires matrix methods; eigenvalues may be complex. LLMs confuse syntax or give incomplete solutions.
- **Difficulty**: 7/10

**46. Nonlinear Predator-Prey**
```
dsolve([diff(x(t), t) - x(t)*(1 - y(t)), diff(y(t), t) - y(t)*(x(t) - 1)], [x(t), y(t)])
```
- **Answer**: No closed-form solution; can find equilibria and stability
- **Why LLMs fail**: Nonlinear systems rarely have closed forms. LLMs hallucinate solutions or give equilibrium points without saying so.
- **Difficulty**: 10/10

**47. Matrix Exponential**
```
dsolve([diff(x(t), t) - A*x(t)], x(t))
```
- **Answer**: `x(t) = exp(A*t) * x(0)` where exp is matrix exponential
- **Why LLMs fail**: Matrix exponential not well-understood by LLMs; confuse with element-wise exponential.
- **Difficulty**: 8/10

### 3.5 Partial Differential Equations (3 equations)

**48. Heat Equation with Boundary Conditions**
```
pde: diff(u(x,t), t) - alpha*diff(u(x,t), x, 2) = 0, u(0,t) = 0, u(L,t) = 0, u(x,0) = f(x)
```
- **Answer**: Fourier series solution with sin(n*pi*x/L)*exp(-alpha*n^2*pi^2*t/L^2)
- **Why LLMs fail**: Requires separation of variables and Fourier series. LLMs give generic form without coefficients.
- **Difficulty**: 8/10

**49. Wave Equation**
```
pde: diff(u(x,t), t, 2) - c**2*diff(u(x,t), x, 2) = 0
```
- **Answer**: d'Alembert solution u(x,t) = f(x-ct) + g(x+ct)
- **Why LLMs fail**: Know the d'Alembert form but struggle with applying boundary conditions. Give incomplete solutions.
- **Difficulty**: 7/10

**50. Laplace Equation in Cylinder**
```
pde: diff(u(r,theta), r, 2) + (1/r)*diff(u(r,theta), r) + (1/r**2)*diff(u(r,theta), theta, 2) = 0
```
- **Answer**: Bessel function solutions
- **Why LLMs fail**: Polar Laplacian separation leads to Bessel equation for r-dependence. LLMs don't recognize Bessel form.
- **Difficulty**: 9/10

## Category 4: Number Theory & Diophantine (15 equations)

### 4.1 Pell Equations (3 equations)

**51. Classical Pell**
```
diophantine(x**2 - 2*y**2 - 1)
```
- **Answer**: Fundamental solution (3,2), then recursion x_{n+1} = 3x_n + 4y_n, y_{n+1} = 2x_n + 3y_n
- **Why LLMs fail**: Continued fraction method or recursive structure not encoded well. LLMs give one solution, not all.
- **Difficulty**: 8/10

**52. Negative Pell**
```
diophantine(x**2 - 3*y**2 + 1)
```
- **Answer**: No solutions (negative Pell for D=3 mod 4 with D≡3)
- **Why LLMs fail**: Don't know conditions for solvability of negative Pell. Give solutions that don't exist.
- **Difficulty**: 9/10

**53. Generalized Pell**
```
diophantine(x**2 - 61*y**2 - 1)
```
- **Answer**: Fundamental solution is (1766319049, 226153980) - huge!
- **Why LLMs fail**: Smallest solution can be enormous for certain D. LLMs give up or provide wrong small solutions.
- **Difficulty**: 10/10

### 4.2 Mordell Curves (3 equations)

**54. Mordell Cubic**
```
diophantine(y**2 - x**3 - 1)
```
- **Answer**: Only solutions are (0,±1), (-1,0)
- **Why LLMs fail**: Finite solution set hard to prove completely. LLMs miss solutions or claim infinitely many.
- **Difficulty**: 9/10

**55. Mordell with Parameter**
```
diophantine(y**2 - x**3 - 17)
```
- **Answer**: Solutions include (2,±1), (4,±9), (8,±23), (43,±282), etc.
- **Why LLMs fail**: Non-trivial rank elliptic curve. LLMs don't have systematic search algorithm.
- **Difficulty**: 10/10

**56. Taxicab Number**
```
solve([a**3 + b**3 - 1729, c**3 + d**3 - 1729], [a,b,c,d], domain=ZZ)
```
- **Answer**: 1729 = 1^3 + 12^3 = 9^3 + 10^3
- **Why LLMs fail**: Ramanujan story famous but finding second representation requires search. LLMs know the answer culturally but can't derive it.
- **Difficulty**: 7/10

### 4.3 Modular Arithmetic (3 equations)

**57. Chinese Remainder Theorem**
```
solve([Mod(x, 3) - 2, Mod(x, 5) - 3, Mod(x, 7) - 2], x)
```
- **Answer**: x ≡ 23 (mod 105)
- **Why LLMs fail**: CRT algorithm requires backtracking substitutions. LLMs make arithmetic errors or forget mod operations.
- **Difficulty**: 6/10

**58. Discrete Logarithm**
```
discrete_log(3, 2, 65537)
```
- **Answer**: Find x such that 2^x ≡ 3 (mod 65537)
- **Why LLMs fail**: No efficient classical algorithm for general discrete log. LLMs hallucinate answers.
- **Difficulty**: 10/10

**59. Quadratic Residue**
```
solve(Mod(x**2, 1009) - 2, x)
```
- **Answer**: Tonelli-Shanks algorithm gives x ≡ ±356 (mod 1009)
- **Why LLMs fail**: Quadratic residue algorithm (Tonelli-Shanks) not well-learned. LLMs give wrong or incomplete solutions.
- **Difficulty**: 9/10

### 4.4 Partition Functions (3 equations)

**60. Partition Number**
```
partition(100)
```
- **Answer**: 190,569,292
- **Why LLMs fail**: Exact partition function requires recursion or generating functions. LLMs use wrong formulas or Hardy-Ramanujan approximation.
- **Difficulty**: 7/10

**61. Restricted Partition**
```
Sum of ways to partition 50 using only odd numbers
```
- **Answer**: Same as partition into distinct parts = 3,658,470
- **Why LLMs fail**: Identity between odd-only and distinct partitions subtle. LLMs compute wrong restricted partitions.
- **Difficulty**: 8/10

**62. Partition Congruence**
```
Mod(partition(5n + 4), 5)
```
- **Answer**: Always 0 (Ramanujan congruence)
- **Why LLMs fail**: Famous number theory result but LLMs don't connect partition function to modular forms.
- **Difficulty**: 9/10

### 4.5 Sum of Powers (3 equations)

**63. Waring's Problem for n=4**
```
Find minimal g(4) such that every integer is sum of at most g(4) fourth powers
```
- **Answer**: g(4) = 19
- **Why LLMs fail**: Waring's problem solved but LLMs don't know specific values. Often confuse g(k) with G(k).
- **Difficulty**: 8/10

**64. Sum of Three Cubes**
```
diophantine(x**3 + y**3 + z**3 - 33)
```
- **Answer**: (8,778,405,442,862,239)^3 + (-8,778,405,442,862,239)^3 + ... wait, actually 33 = 8866128975287528^3 + ...
- **Why LLMs fail**: Solutions can be astronomically large; no general algorithm. LLMs give up or wrong small attempts.
- **Difficulty**: 10/10

**65. Fermat's Last Theorem Case n=3**
```
diophantine(x**3 + y**3 - z**3) with x,y,z coprime and xyz ≠ 0
```
- **Answer**: No solutions (Fermat's Last Theorem)
- **Why LLMs fail**: Know FLT culturally but when phrased as Diophantine equation, may try to solve or give false solutions.
- **Difficulty**: 10/10 (requires proof, not computation)

## Category 5: Series & Sequences (15 equations)

### 5.1 Conditionally Convergent Series (3 equations)

**66. Alternating Harmonic**
```
summation((-1)**(n+1)/n, (n, 1, oo))
```
- **Answer**: `ln(2)`
- **Why LLMs fail**: Conditional convergence means rearrangement changes sum. LLMs may not verify convergence or get wrong value.
- **Difficulty**: 5/10

**67. Dirichlet Eta Function**
```
summation((-1)**(n+1)/n**3, (n, 1, oo))
```
- **Answer**: `3*zeta(3)/4` where zeta(3) ≈ 1.202
- **Why LLMs fail**: Connection to zeta function via eta(s) = (1-2^(1-s))zeta(s) subtle. LLMs miss the 3/4 factor.
- **Difficulty**: 7/10

**68. Alternating Zeta**
```
summation((-1)**(n+1)/n**4, (n, 1, oo))
```
- **Answer**: `7*pi**4/720`
- **Why LLMs fail**: Even powers connect to pi but alternating gives different coefficient. LLMs use wrong formula.
- **Difficulty**: 7/10

### 5.2 Asymptotic Expansions (3 equations)

**69. Stirling's Correction**
```
limit((log(factorial(n)) - (n + 1/2)*log(n) + n - log(2*pi)/2)*n, n, oo)
```
- **Answer**: `1/12`
- **Why LLMs fail**: Next term in Stirling series is 1/(12n). LLMs stop at leading order or get coefficient wrong.
- **Difficulty**: 8/10

**70. Prime Number Theorem Correction**
```
limit((primepi(x) - x/log(x))/(x/(log(x)**2)), x, oo)
```
- **Answer**: `1`
- **Why LLMs fail**: Second-order term in PNT is x/log(x)^2. LLMs don't have prime counting precision.
- **Difficulty**: 9/10

**71. Asymptotic of Central Binomial**
```
limit(binomial(2*n, n) / (4**n / sqrt(pi*n)), n, oo)
```
- **Answer**: `1`
- **Why LLMs fail**: Central binomial asymptotics ~ 4^n/sqrt(pi*n). LLMs miss sqrt(n) or get constant wrong.
- **Difficulty**: 7/10

### 5.3 Generating Functions (3 equations)

**72. Catalan Number Generating Function**
```
summation(catalan(n)*x**n, (n, 0, oo))
```
- **Answer**: `(1 - sqrt(1 - 4*x))/(2*x)`
- **Why LLMs fail**: Catalan g.f. satisfies functional equation C(x) = 1 + xC(x)^2. LLMs don't derive or recall correctly.
- **Difficulty**: 8/10

**73. Fibonacci Generating Function**
```
summation(fibonacci(n)*x**n, (n, 0, oo))
```
- **Answer**: `x/(1 - x - x**2)`
- **Why LLMs fail**: Recurrence F_n = F_{n-1} + F_{n-2} gives functional equation. LLMs make algebraic errors.
- **Difficulty**: 6/10

**74. Partition Generating Function**
```
product(1/(1 - x**k), (k, 1, oo))
```
- **Answer**: `Sum(partition(n)*x**n, (n, 0, oo))`
- **Why LLMs fail**: Infinite product relation to partitions non-obvious. LLMs don't connect Euler's formula.
- **Difficulty**: 9/10

### 5.4 Zeta Function Values (3 equations)

**75. Riemann Zeta at 3**
```
zeta(3)
```
- **Answer**: Apéry's constant ≈ 1.2020569..., no known closed form
- **Why LLMs fail**: LLMs try to give closed form like pi^3/something or claim it's transcendental (unproven).
- **Difficulty**: 7/10

**76. Dirichlet Beta at 2**
```
summation((-1)**n/(2*n + 1)**2, (n, 0, oo))
```
- **Answer**: `G` (Catalan's constant) ≈ 0.915965...
- **Why LLMs fail**: Catalan's constant defined this way but LLMs don't recognize or give wrong expressions.
- **Difficulty**: 8/10

**77. Basel Problem Generalization**
```
summation(1/(2*n - 1)**2, (n, 1, oo))
```
- **Answer**: `pi**2/8`
- **Why LLMs fail**: Related to zeta(2) but sum over odds only. LLMs use zeta(2) = pi^2/6 incorrectly.
- **Difficulty**: 6/10

### 5.5 Hypergeometric Series (3 equations)

**78. Gauss Hypergeometric**
```
hypergeometric([1/2, 1/2], [1], 1/2)
```
- **Answer**: `4*K(1/sqrt(2))/pi^2` where K is complete elliptic integral
- **Why LLMs fail**: Hypergeometric at special points connects to elliptic integrals. LLMs don't have this database.
- **Difficulty**: 9/10

**79. Confluent Hypergeometric**
```
confluent_hypergeometric(a, c, x)
```
- **Answer**: Kummer's function 1F1, no simple closed form generally
- **Why LLMs fail**: Confuse with regular hypergeometric or give recursive relations instead of closed form.
- **Difficulty**: 8/10

**80. Hypergeometric Identity**
```
hypergeometric([a, b], [c], 1) where c > a + b
```
- **Answer**: `Gamma(c)*Gamma(c - a - b)/(Gamma(c - a)*Gamma(c - b))`
- **Why LLMs fail**: Gauss evaluation theorem at z=1. LLMs miss the condition c > a+b or give wrong formula.
- **Difficulty**: 9/10

## Category 6: Linear Algebra (10 equations)

### 6.1 Eigenvalue Problems with Degeneracies (3 equations)

**81. Defective Matrix (Jordan Block)**
```
eigenvals_and_eigenvects(Matrix([[1, 1, 0], [0, 1, 1], [0, 0, 1]]))
```
- **Answer**: Eigenvalue 1 with multiplicity 3, but only one eigenvector
- **Why LLMs fail**: Defective matrices have fewer eigenvectors than eigenvalues. LLMs claim 3 eigenvectors.
- **Difficulty**: 7/10

**82. Repeated Eigenvalue with Full Basis**
```
eigenvals_and_eigenvects(Matrix([[2, 0, 0], [0, 2, 0], [0, 0, 3]]))
```
- **Answer**: Eigenvalue 2 (multiplicity 2) with 2 eigenvectors, eigenvalue 3 (multiplicity 1)
- **Why LLMs fail**: Must distinguish geometric vs algebraic multiplicity. LLMs confuse the two.
- **Difficulty**: 6/10

**83. Complex Eigenvalues**
```
eigenvals(Matrix([[0, -1], [1, 0]]))
```
- **Answer**: `±i`
- **Why LLMs fail**: Rotation matrix has complex eigenvalues even though real matrix. LLMs expect real values.
- **Difficulty**: 5/10

### 6.2 Ill-Conditioned Matrices (3 equations)

**84. Hilbert Matrix Condition Number**
```
Matrix([[1/(i+j-1) for j in range(1,6)] for i in range(1,6)]).condition_number()
```
- **Answer**: ~4.77 × 10^5 (extremely ill-conditioned)
- **Why LLMs fail**: Numerical evaluation differs from symbolic. LLMs give wrong order of magnitude.
- **Difficulty**: 7/10

**85. Near-Singular Determinant**
```
det(Matrix([[1, 1, 1], [1, 1.0001, 1], [1, 1, 1.0001]]))
```
- **Answer**: ~1.0001 × 10^-8 (near zero)
- **Why LLMs fail**: Small perturbation analysis required. LLMs use wrong precision or give 0.
- **Difficulty**: 7/10

**86. Wilkinson Polynomial Roots**
```
solve(product(x - k, (k, 1, 20)), x)
```
- **Answer**: Roots are 1,2,...,20 but numerically unstable
- **Why LLMs fail**: Wilkinson polynomial famously ill-conditioned; small coefficient changes move roots dramatically. LLMs think it's trivial.
- **Difficulty**: 8/10

### 6.3 Symbolic Determinants (4 equations)

**87. Vandermonde Determinant**
```
det(Matrix([[1, 1, 1], [a, b, c], [a**2, b**2, c**2]]))
```
- **Answer**: `(b - a)*(c - a)*(c - b)`
- **Why LLMs fail**: Famous formula but LLMs expand determinant incorrectly or miss factorization.
- **Difficulty**: 6/10

**88. Circulant Matrix**
```
det(Matrix([[a, b, c], [c, a, b], [b, c, a]]))
```
- **Answer**: `a**3 + b**3 + c**3 - 3*a*b*c`
- **Why LLMs fail**: Circulant eigenvalues involve cube roots of unity. LLMs don't use this shortcut.
- **Difficulty**: 7/10

**89. Block Matrix Determinant**
```
det(Matrix([[A, B], [C, D]]))
```
- **Answer**: `det(A)*det(D - C*A^(-1)*B)` if A invertible (Schur complement)
- **Why LLMs fail**: Block determinant formulas non-trivial. LLMs apply scalar formula incorrectly.
- **Difficulty**: 8/10

**90. Tridiagonal Determinant**
```
det(Matrix([[a, b, 0, 0], [b, a, b, 0], [0, b, a, b], [0, 0, b, a]]))
```
- **Answer**: Recursive formula or Chebyshev polynomial expression
- **Why LLMs fail**: Tridiagonal determinants have nice recurrence. LLMs expand fully instead.
- **Difficulty**: 7/10

## Category 7: Edge Cases (10 equations)

### 7.1 Order of Operations Traps (3 equations)

**91. Right Associative Exponentiation**
```
2**3**2
```
- **Answer**: `512` (= 2^(3^2) = 2^9)
- **Why LLMs fail**: Many programming languages and LLMs treat this left-to-right giving (2^3)^2 = 64.
- **Difficulty**: 3/10

**92. Negative Base Power**
```
-2**2
```
- **Answer**: `-4` (= -(2^2))
- **Why LLMs fail**: Exponentiation has higher precedence than negation. LLMs compute (-2)^2 = 4.
- **Difficulty**: 3/10

**93. Division Associativity**
```
100/5/4
```
- **Answer**: `5` (= (100/5)/4 = 20/4)
- **Why LLMs fail**: Division is left-associative. LLMs may compute 100/(5/4) = 80.
- **Difficulty**: 2/10

### 7.2 Sign Errors (2 equations)

**94. Alternating Sum Sign**
```
summation((-1)**n*n, (n, 1, 100))
```
- **Answer**: `-50`
- **Why LLMs fail**: Pairs (1-2) + (3-4) + ... = -1 repeated 50 times. LLMs lose track of signs.
- **Difficulty**: 4/10

**95. Product of Negatives**
```
product(-1, (k, 1, 101))
```
- **Answer**: `-1` (101 factors)
- **Why LLMs fail**: Odd number of negative factors gives negative result. LLMs miscount.
- **Difficulty**: 3/10

### 7.3 Domain Restrictions (3 equations)

**96. Log of Negative**
```
log(-1)
```
- **Answer**: `i*pi` (principal value in complex)
- **Why LLMs fail**: Real vs complex domain confusion. LLMs say undefined or give wrong branch.
- **Difficulty**: 6/10

**97. Square Root of Negative**
```
sqrt(-4)
```
- **Answer**: `2*i`
- **Why LLMs fail**: Same domain issue. Some LLMs refuse, others give wrong sign or magnitude.
- **Difficulty**: 4/10

**98. Inverse Trig Out of Domain**
```
arcsin(2)
```
- **Answer**: `pi/2 - i*log(2 + sqrt(3))` (complex)
- **Why LLMs fail**: arcsin extends to complex plane but LLMs say undefined or give wrong formula.
- **Difficulty**: 8/10

### 7.4 Branch Cut Issues (2 equations)

**99. Multi-Valued Power**
```
(-1)**(1/3)
```
- **Answer**: `-1` (real cube root) or `(1 + i*sqrt(3))/2` (principal complex)
- **Why LLMs fail**: Three cube roots but which is principal? LLMs give inconsistent answers.
- **Difficulty**: 7/10

**100. Logarithm Branch Cut**
```
log(exp(3*pi*i))
```
- **Answer**: `pi*i` (wraps around, principal branch gives -pi < Im ≤ pi)
- **Why LLMs fail**: Branch cut at negative real axis causes discontinuity. LLMs give 3*pi*i (wrong branch).
- **Difficulty**: 8/10

---

## Summary Statistics

- **Average Difficulty**: 7.4/10
- **Difficulty Distribution**:
  - 1-3: 3 equations (trivial but tricky)
  - 4-6: 11 equations (medium)
  - 7-8: 50 equations (hard)
  - 9-10: 36 equations (very hard / expert)

## Category Breakdown

1. **Symbolic Integration (20)**: Non-elementary, elliptic, improper integrals, rational functions
2. **Limits (15)**: All indeterminate forms, directional limits, nested limits
3. **Differential Equations (15)**: Bernoulli, Riccati, exact, systems, PDEs
4. **Number Theory & Diophantine (15)**: Pell, Mordell, modular arithmetic, partitions, sums of powers
5. **Series & Sequences (15)**: Conditional convergence, asymptotics, generating functions, zeta values, hypergeometric
6. **Linear Algebra (10)**: Degeneracies, ill-conditioning, symbolic determinants
7. **Edge Cases (10)**: Order of ops, signs, domains, branch cuts

## Common LLM Failure Modes

1. **Insufficient domain knowledge**: Special functions, transcendental numbers, advanced theorems
2. **Procedural errors**: Multi-step derivations lose track, incorrect substitutions
3. **Symbolic manipulation errors**: Algebraic mistakes, sign errors, missed factorizations
4. **Recognizing problem type**: Don't identify which technique to apply
5. **Boundary condition handling**: Improper integrals, directional limits, domain restrictions
6. **Numerical vs symbolic confusion**: Mixing approximate and exact computations
7. **Incomplete solutions**: Give one solution instead of all, or general form without specifics
8. **Cultural knowledge override**: Know famous results but can't derive them, or derive and get wrong answer
9. **Complex number handling**: Real/complex domain confusion, branch cuts, multi-valued functions
10. **Asymptotic analysis**: Stop at leading order, miss correction terms

## References

- Abramowitz & Stegun: Handbook of Mathematical Functions
- NIST DLMF: Digital Library of Mathematical Functions
- Putnam Competition Archives
- MIT Integration Bee Problems
- Gradshteyn & Ryzhik: Table of Integrals, Series, and Products
- OEIS: Online Encyclopedia of Integer Sequences
- Apostol: Introduction to Analytic Number Theory
- Clarkson: Painlevé Equations
- Flajolet & Sedgewick: Analytic Combinatorics

---

**Last Updated**: 2025-12-15
**Compiled by**: Claude Sonnet 4.5
**Purpose**: Mathematical reasoning benchmarking for LLMs and symbolic AI systems
