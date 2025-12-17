# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
100 LLM Killer Equations - Mathematical Problems That Expose LLM Weaknesses
============================================================================

This module contains 100 carefully selected mathematical equations that are
notoriously difficult for Large Language Models (LLMs) to solve correctly.

Each equation is annotated with:
- Expression in parseable format
- Expected answer
- Reason for LLM failure
- Difficulty rating (1-10)

These equations target specific failure modes:
- Insufficient domain knowledge
- Procedural errors in multi-step derivations
- Symbolic manipulation mistakes
- Difficulty recognizing problem types
- Boundary condition handling
- Complex number domain confusion
- Asymptotic analysis errors
"""

# =============================================================================
# CATEGORY 1: SYMBOLIC INTEGRATION (20 equations)
# =============================================================================

SYMBOLIC_INTEGRATION = [
    # Non-Elementary Integrals (5)
    {
        "id": 1,
        "expr": "integrate(exp(-x**2), (x, -oo, oo))",
        "answer": "sqrt(pi)",
        "why_fails": "Requires polar coordinate trick or recognizing Gaussian integral; LLMs try term-by-term",
        "difficulty": 7,
        "tags": ["gaussian", "special-function", "improper"]
    },
    {
        "id": 2,
        "expr": "integrate(exp(-x**2), (x, 0, 1))",
        "answer": "sqrt(pi)*erf(1)/2",
        "why_fails": "Must recognize antiderivative is non-elementary erf(x); LLMs hallucinate closed forms",
        "difficulty": 8,
        "tags": ["error-function", "non-elementary"]
    },
    {
        "id": 3,
        "expr": "integrate(sin(x)/x, (x, 0, oo))",
        "answer": "pi/2",
        "why_fails": "Removable singularity at x=0; requires contour integration or Si(x) knowledge",
        "difficulty": 8,
        "tags": ["sine-integral", "improper", "singularity"]
    },
    {
        "id": 4,
        "expr": "integrate(sin(x**2), (x, 0, oo))",
        "answer": "sqrt(pi/8)",
        "why_fails": "Fresnel integral S(∞) = 1/2; LLMs confuse with regular sine integral",
        "difficulty": 9,
        "tags": ["fresnel", "special-function"]
    },
    {
        "id": 5,
        "expr": "integrate(cos(x**2), (x, 0, oo))",
        "answer": "sqrt(pi/8)",
        "why_fails": "Fresnel integral C(∞) = 1/2; LLMs give different values for S vs C",
        "difficulty": 9,
        "tags": ["fresnel", "special-function"]
    },

    # Elliptic Integrals (5)
    {
        "id": 6,
        "expr": "integrate(1/sqrt((1 - x**2)*(1 - k**2*x**2)), (x, 0, 1))",
        "answer": "K(k)",
        "why_fails": "Don't recognize canonical elliptic integral form; confuse with arcsin",
        "difficulty": 9,
        "tags": ["elliptic", "complete-elliptic-first-kind"]
    },
    {
        "id": 7,
        "expr": "integrate(sqrt(1 - k**2*x**2)/sqrt(1 - x**2), (x, 0, 1))",
        "answer": "E(k)",
        "why_fails": "Complete elliptic integral second kind; miss distinction from K(k)",
        "difficulty": 9,
        "tags": ["elliptic", "complete-elliptic-second-kind"]
    },
    {
        "id": 8,
        "expr": "integrate(sqrt(1 - (1 - b**2/a**2)*sin(t)**2), (t, 0, pi/2))",
        "answer": "E(sqrt(1 - b**2/a**2))",
        "why_fails": "Arc length of ellipse leads to elliptic integral; LLMs give wrong approximations",
        "difficulty": 8,
        "tags": ["elliptic", "arc-length", "geometry"]
    },
    {
        "id": 9,
        "expr": "integrate(1/sqrt(cos(theta) - cos(theta_0)), (theta, 0, theta_0))",
        "answer": "4*K(sin(theta_0/2))/sqrt(2*g/l)",
        "why_fails": "Pendulum period requires half-angle substitution to elliptic form",
        "difficulty": 9,
        "tags": ["elliptic", "physics", "pendulum"]
    },
    {
        "id": 10,
        "expr": "integrate(1/sqrt((1 - x**2)*(1 - m*x**2)), (x, 0, z))",
        "answer": "F(arcsin(z), m)",
        "why_fails": "Incomplete elliptic integral; LLMs confuse F and K notation",
        "difficulty": 9,
        "tags": ["elliptic", "incomplete-elliptic"]
    },

    # Improper Integrals with Singularities (5)
    {
        "id": 11,
        "expr": "integrate(log(x)/(1 + x), (x, 0, 1))",
        "answer": "-pi**2/12",
        "why_fails": "Singularity at x=0; connection to dilogarithm and zeta(2) missed",
        "difficulty": 8,
        "tags": ["logarithmic", "singularity", "polylogarithm"]
    },
    {
        "id": 12,
        "expr": "integrate(log(x)*log(1 - x), (x, 0, 1))",
        "answer": "2 - pi**2/6",
        "why_fails": "Integration by parts leads to Li_2(1) = zeta(2); LLMs lose boundary terms",
        "difficulty": 9,
        "tags": ["logarithmic", "polylogarithm", "zeta"]
    },
    {
        "id": 13,
        "expr": "integrate(sin(x)/x, (x, -oo, oo))",
        "answer": "pi",
        "why_fails": "Principal value interpretation; LLMs confuse with (0,∞) case",
        "difficulty": 7,
        "tags": ["principal-value", "improper"]
    },
    {
        "id": 14,
        "expr": "integrate(log(sin(x)), (x, 0, pi/2))",
        "answer": "-pi*log(2)/2",
        "why_fails": "Singularity at x=0; requires Fourier series or complex analysis",
        "difficulty": 9,
        "tags": ["logarithmic", "trigonometric", "singularity"]
    },
    {
        "id": 15,
        "expr": "integrate(log(tan(x)), (x, 0, pi/4))",
        "answer": "-G",
        "why_fails": "Result is Catalan's constant; LLMs don't recognize this transcendental",
        "difficulty": 10,
        "tags": ["logarithmic", "catalan", "transcendental"]
    },

    # Rational Functions with Special Structure (5)
    {
        "id": 16,
        "expr": "integrate(1/(x**4 + 1), (x, -oo, oo))",
        "answer": "pi/sqrt(2)",
        "why_fails": "Requires residue theorem with complex poles at e^(iπ/4) etc; wrong contour",
        "difficulty": 8,
        "tags": ["residue", "complex-analysis", "rational"]
    },
    {
        "id": 17,
        "expr": "integrate(1/((x**2 + 1)**3), (x, -oo, oo))",
        "answer": "3*pi/8",
        "why_fails": "Third-order pole requires derivative of residue formula; LLMs use simple pole",
        "difficulty": 8,
        "tags": ["residue", "higher-order-pole"]
    },
    {
        "id": 18,
        "expr": "integrate(1/(x**6 + 1), (x, -oo, oo))",
        "answer": "2*pi/3",
        "why_fails": "Six roots of unity; must select correct three in upper half-plane",
        "difficulty": 8,
        "tags": ["residue", "roots-of-unity"]
    },
    {
        "id": 19,
        "expr": "integrate(x**2*exp(-x)/(1 + x), (x, 0, oo))",
        "answer": "Ei(-1)*exp(1) + exp(-1) - 1",
        "why_fails": "No elementary antiderivative; requires exponential integral Ei(x)",
        "difficulty": 9,
        "tags": ["exponential-integral", "non-elementary"]
    },
    {
        "id": 20,
        "expr": "integrate(log(x)**2/(x**2 + 1), (x, 0, oo))",
        "answer": "pi**3/8",
        "why_fails": "Involves polylogarithms in intermediate steps; LLMs miss pi^3 scaling",
        "difficulty": 9,
        "tags": ["logarithmic", "polylogarithm"]
    },
]

# =============================================================================
# CATEGORY 2: LIMITS (15 equations)
# =============================================================================

LIMITS = [
    # Indeterminate Form 0/0 (5)
    {
        "id": 21,
        "expr": "limit((exp(x) - exp(-x) - 2*x)/(x - sin(x)), x, 0)",
        "answer": "2",
        "why_fails": "Requires 3+ applications of L'Hopital; LLMs lose track or stop early",
        "difficulty": 7,
        "tags": ["lhopital", "0/0", "multiple-applications"]
    },
    {
        "id": 22,
        "expr": "limit((x - tan(x))/(x - sin(x)), x, 0)",
        "answer": "-2",
        "why_fails": "Negative answer surprises models; often get +2 or 0",
        "difficulty": 8,
        "tags": ["lhopital", "0/0", "sign-error"]
    },
    {
        "id": 23,
        "expr": "limit((exp(sin(x)) - exp(x))/x**3, x, 0)",
        "answer": "-1/6",
        "why_fails": "L'Hopital messy; Taylor series more elegant but LLMs miss this approach",
        "difficulty": 8,
        "tags": ["taylor-series", "0/0"]
    },
    {
        "id": 24,
        "expr": "limit((1 - cos(x)*cos(2*x))/x**2, x, 0)",
        "answer": "5/2",
        "why_fails": "Product of cosines; careful tracking of x^2 coefficients needed",
        "difficulty": 7,
        "tags": ["trigonometric", "0/0"]
    },
    {
        "id": 25,
        "expr": "limit((tan(x) - sin(x))/(sin(x) - x), x, 0)",
        "answer": "-1",
        "why_fails": "Both parts ~x^3/6; careful sign analysis required",
        "difficulty": 7,
        "tags": ["trigonometric", "0/0", "sign-error"]
    },

    # Indeterminate Form ∞ - ∞ (3)
    {
        "id": 26,
        "expr": "limit(x - x*exp(1/x), x, oo)",
        "answer": "-1",
        "why_fails": "Factor x and Taylor expand exp(1/x); LLMs don't see factorization",
        "difficulty": 8,
        "tags": ["inf-inf", "taylor-series"]
    },
    {
        "id": 27,
        "expr": "limit(x**2*(sqrt(1 + 1/x) - 1 - 1/(2*x)), x, oo)",
        "answer": "-1/8",
        "why_fails": "Second-order Taylor needed; first-order cancels but LLMs stop there",
        "difficulty": 8,
        "tags": ["inf-inf", "taylor-series", "second-order"]
    },
    {
        "id": 28,
        "expr": "limit(x*(pi/2 - arctan(x)), x, oo)",
        "answer": "1",
        "why_fails": "Substitution u=1/x helps; LLMs try L'Hopital directly and fail",
        "difficulty": 7,
        "tags": ["inf-inf", "inverse-trig"]
    },

    # Indeterminate Form 1^∞ (4)
    {
        "id": 29,
        "expr": "limit((1 + sin(x)/x)**(x**2), x, oo)",
        "answer": "sqrt(e)",
        "why_fails": "Rewrite as exp(x^2*log(1 + sin(x)/x)); LLMs miss 1/2 in exponent",
        "difficulty": 8,
        "tags": ["1^inf", "exponential-form"]
    },
    {
        "id": 30,
        "expr": "limit((cos(x))**(1/sin(x)**2), x, 0)",
        "answer": "1/sqrt(e)",
        "why_fails": "log(cos(x)) ~ -x^2/2 combining with 1/sin^2(x) ~ 1/x^2; mishandle log expansion",
        "difficulty": 9,
        "tags": ["1^inf", "trigonometric", "logarithmic"]
    },
    {
        "id": 31,
        "expr": "limit((x/(x + 1))**x, x, oo)",
        "answer": "1/e",
        "why_fails": "(1 - 1/(x+1))^x form; LLMs confuse with (1 + 1/x)^x = e",
        "difficulty": 7,
        "tags": ["1^inf", "exponential"]
    },
    {
        "id": 32,
        "expr": "limit((1 + 1/x + 1/x**2)**(x**2), x, oo)",
        "answer": "sqrt(e)",
        "why_fails": "Second term 1/x^2 contributes; x^2 amplifies it giving 1/2 in exponent",
        "difficulty": 8,
        "tags": ["1^inf", "correction-term"]
    },

    # Indeterminate Form 0^0 (3)
    {
        "id": 33,
        "expr": "limit(x**x, x, 0, '+')",
        "answer": "1",
        "why_fails": "Rewrite as exp(x*log(x)); x*log(x) → 0 but LLMs say undefined or 0",
        "difficulty": 6,
        "tags": ["0^0", "logarithmic"]
    },
    {
        "id": 34,
        "expr": "limit(x**(x**x), x, 0, '+')",
        "answer": "0",
        "why_fails": "Outer exponent x^x → 1 but x^1 → 0; order of limits critical",
        "difficulty": 9,
        "tags": ["0^0", "nested", "order-dependent"]
    },
    {
        "id": 35,
        "expr": "limit((1/x)**sin(x), x, 0, '+')",
        "answer": "1",
        "why_fails": "sin(x) → 0 faster than log(1/x) → ∞ giving exp(0) = 1; LLMs say ∞ or 0",
        "difficulty": 8,
        "tags": ["0^0", "rates"]
    },
]

# =============================================================================
# CATEGORY 3: DIFFERENTIAL EQUATIONS (15 equations)
# =============================================================================

DIFFERENTIAL_EQUATIONS = [
    # Bernoulli Equations (3)
    {
        "id": 36,
        "expr": "dsolve(diff(y(x), x) + y(x) - y(x)**2, y(x))",
        "answer": "y(x) = 1/(1 - C*exp(-x))",
        "why_fails": "Requires v = y^(-1) substitution; LLMs miss or misapply transformation",
        "difficulty": 7,
        "tags": ["bernoulli", "substitution"]
    },
    {
        "id": 37,
        "expr": "dsolve(diff(y(x), x) - y(x)/x + y(x)**3/x**2, y(x))",
        "answer": "y(x) = x/sqrt(C*x**2 + 2)",
        "why_fails": "Variable coefficient plus nonlinear; confuse with separable",
        "difficulty": 8,
        "tags": ["bernoulli", "variable-coefficient"]
    },
    {
        "id": 38,
        "expr": "dsolve(diff(y(x), x) + y(x)*tan(x) - y(x)**2*sec(x), y(x))",
        "answer": "Complex solution with integrating factor",
        "why_fails": "Combo of integrating factor and Bernoulli; LLMs apply only one technique",
        "difficulty": 8,
        "tags": ["bernoulli", "integrating-factor", "trigonometric"]
    },

    # Riccati Equations (3)
    {
        "id": 39,
        "expr": "dsolve(diff(y(x), x) - y(x)**2 - x**2, y(x))",
        "answer": "Involves Bessel functions",
        "why_fails": "Riccati generally non-elementary; this one needs Bessel knowledge",
        "difficulty": 9,
        "tags": ["riccati", "bessel", "non-elementary"]
    },
    {
        "id": 40,
        "expr": "dsolve(diff(y(x), x) - 2*y(x)/x + y(x)**2 - 1/x**2, y(x))",
        "answer": "Reducible if particular solution y_p = 1/x known",
        "why_fails": "Requires guessing y_p = 1/x then y = y_p + 1/v substitution",
        "difficulty": 9,
        "tags": ["riccati", "particular-solution"]
    },
    {
        "id": 41,
        "expr": "dsolve(x*diff(y(x), x) + y(x)**2 - a*x, y(x))",
        "answer": "Related to Airy functions",
        "why_fails": "Riccati-to-second-order gives Airy equation; LLMs miss connection",
        "difficulty": 10,
        "tags": ["riccati", "airy", "transformation"]
    },

    # Exact Equations (3)
    {
        "id": 42,
        "expr": "dsolve((2*x*y(x) + y(x)**2) + (x**2 + 2*x*y(x))*diff(y(x), x), y(x))",
        "answer": "x**2*y + x*y**2 = C",
        "why_fails": "Must verify M_y = N_x; LLMs skip verification or integrate wrong",
        "difficulty": 7,
        "tags": ["exact", "implicit"]
    },
    {
        "id": 43,
        "expr": "dsolve((2*x + y(x)) + x*diff(y(x), x), y(x))",
        "answer": "Requires integrating factor",
        "why_fails": "Not exact initially; must find µ(x) or µ(y) first",
        "difficulty": 8,
        "tags": ["exact", "integrating-factor"]
    },
    {
        "id": 44,
        "expr": "dsolve(x*diff(y(x), x) - y(x) + x*sqrt(x**2 + y(x)**2), y(x))",
        "answer": "Easier in polar coordinates",
        "why_fails": "Cartesian complicated; polar substitution simplifies but LLMs don't try",
        "difficulty": 9,
        "tags": ["exact", "polar-coordinates"]
    },

    # Systems of ODEs (3)
    {
        "id": 45,
        "expr": "dsolve([diff(x(t), t) - 2*x(t) + y(t), diff(y(t), t) + x(t) - 2*y(t)], [x(t), y(t)])",
        "answer": "Eigenvalue/eigenvector solution",
        "why_fails": "Matrix methods required; eigenvalues may be complex",
        "difficulty": 7,
        "tags": ["system", "linear", "eigenvalue"]
    },
    {
        "id": 46,
        "expr": "dsolve([diff(x(t), t) - x(t)*(1 - y(t)), diff(y(t), t) - y(t)*(x(t) - 1)], [x(t), y(t)])",
        "answer": "No closed-form; equilibria at (0,0), (1,1)",
        "why_fails": "Nonlinear Lotka-Volterra; LLMs hallucinate closed forms",
        "difficulty": 10,
        "tags": ["system", "nonlinear", "predator-prey"]
    },
    {
        "id": 47,
        "expr": "x'(t) = A*x(t) where A is matrix",
        "answer": "x(t) = exp(A*t)*x(0)",
        "why_fails": "Matrix exponential confused with element-wise exponential",
        "difficulty": 8,
        "tags": ["system", "matrix-exponential"]
    },

    # PDEs (3)
    {
        "id": 48,
        "expr": "diff(u(x,t), t) - alpha*diff(u(x,t), x, 2) = 0 with u(0,t)=0, u(L,t)=0, u(x,0)=f(x)",
        "answer": "u = Sum(A_n*sin(nπx/L)*exp(-α(nπ/L)^2*t))",
        "why_fails": "Separation of variables + Fourier series; LLMs give generic form without coefficients",
        "difficulty": 8,
        "tags": ["pde", "heat-equation", "fourier"]
    },
    {
        "id": 49,
        "expr": "diff(u(x,t), t, 2) - c**2*diff(u(x,t), x, 2) = 0",
        "answer": "u(x,t) = f(x - c*t) + g(x + c*t)",
        "why_fails": "d'Alembert solution known but boundary conditions application struggles",
        "difficulty": 7,
        "tags": ["pde", "wave-equation", "dalembert"]
    },
    {
        "id": 50,
        "expr": "diff(u(r,theta), r, 2) + (1/r)*diff(u(r,theta), r) + (1/r**2)*diff(u(r,theta), theta, 2) = 0",
        "answer": "Bessel function solution",
        "why_fails": "Polar Laplacian separation gives Bessel equation for r; LLMs miss form",
        "difficulty": 9,
        "tags": ["pde", "laplace", "bessel", "polar"]
    },
]

# =============================================================================
# CATEGORY 4: NUMBER THEORY & DIOPHANTINE (15 equations)
# =============================================================================

NUMBER_THEORY_DIOPHANTINE = [
    # Pell Equations (3)
    {
        "id": 51,
        "expr": "diophantine(x**2 - 2*y**2 - 1)",
        "answer": "Fundamental (3,2); recursion x_{n+1}=3x_n+4y_n, y_{n+1}=2x_n+3y_n",
        "why_fails": "Continued fraction method not encoded; give one solution not all",
        "difficulty": 8,
        "tags": ["pell", "recursive"]
    },
    {
        "id": 52,
        "expr": "diophantine(x**2 - 3*y**2 + 1)",
        "answer": "No solutions (negative Pell)",
        "why_fails": "Don't know solvability conditions for negative Pell",
        "difficulty": 9,
        "tags": ["pell", "negative-pell", "no-solution"]
    },
    {
        "id": 53,
        "expr": "diophantine(x**2 - 61*y**2 - 1)",
        "answer": "Fundamental: (1766319049, 226153980)",
        "why_fails": "Smallest solution enormous for D=61; LLMs give up or wrong",
        "difficulty": 10,
        "tags": ["pell", "large-solution"]
    },

    # Mordell Curves (3)
    {
        "id": 54,
        "expr": "diophantine(y**2 - x**3 - 1)",
        "answer": "Only (0,±1), (-1,0)",
        "why_fails": "Finite set hard to prove complete; LLMs miss or claim infinite",
        "difficulty": 9,
        "tags": ["mordell", "elliptic-curve", "finite"]
    },
    {
        "id": 55,
        "expr": "diophantine(y**2 - x**3 - 17)",
        "answer": "(2,±1), (4,±9), (8,±23), (43,±282), ...",
        "why_fails": "Non-trivial rank; no systematic search algorithm in LLMs",
        "difficulty": 10,
        "tags": ["mordell", "elliptic-curve", "rank"]
    },
    {
        "id": 56,
        "expr": "solve([a**3 + b**3 - 1729, c**3 + d**3 - 1729], [a,b,c,d], domain=ZZ)",
        "answer": "1^3+12^3 = 9^3+10^3 = 1729",
        "why_fails": "Ramanujan taxicab; know culturally but can't derive systematically",
        "difficulty": 7,
        "tags": ["sum-of-cubes", "ramanujan", "cultural"]
    },

    # Modular Arithmetic (3)
    {
        "id": 57,
        "expr": "solve([Mod(x, 3) - 2, Mod(x, 5) - 3, Mod(x, 7) - 2], x)",
        "answer": "x ≡ 23 (mod 105)",
        "why_fails": "CRT requires backtracking; arithmetic errors or forget mod operations",
        "difficulty": 6,
        "tags": ["crt", "modular"]
    },
    {
        "id": 58,
        "expr": "discrete_log(3, 2, 65537)",
        "answer": "Find x: 2^x ≡ 3 (mod 65537)",
        "why_fails": "No efficient classical algorithm; LLMs hallucinate",
        "difficulty": 10,
        "tags": ["discrete-log", "hard-problem"]
    },
    {
        "id": 59,
        "expr": "solve(Mod(x**2, 1009) - 2, x)",
        "answer": "x ≡ ±356 (mod 1009)",
        "why_fails": "Tonelli-Shanks algorithm not learned well; wrong or incomplete",
        "difficulty": 9,
        "tags": ["quadratic-residue", "tonelli-shanks"]
    },

    # Partition Functions (3)
    {
        "id": 60,
        "expr": "partition(100)",
        "answer": "190569292",
        "why_fails": "Exact partition needs recursion/generating functions; use wrong formula",
        "difficulty": 7,
        "tags": ["partition", "combinatorics"]
    },
    {
        "id": 61,
        "expr": "Partitions of 50 using only odd numbers",
        "answer": "3658470 (same as distinct partitions)",
        "why_fails": "Odd-only = distinct identity subtle; compute wrong type",
        "difficulty": 8,
        "tags": ["partition", "restricted", "identity"]
    },
    {
        "id": 62,
        "expr": "Mod(partition(5*n + 4), 5)",
        "answer": "Always 0 (Ramanujan congruence)",
        "why_fails": "Famous result but LLMs don't connect to modular forms",
        "difficulty": 9,
        "tags": ["partition", "congruence", "ramanujan"]
    },

    # Sum of Powers (3)
    {
        "id": 63,
        "expr": "Minimal g(4) in Waring's problem",
        "answer": "g(4) = 19",
        "why_fails": "Specific Waring values not memorized; confuse g(k) with G(k)",
        "difficulty": 8,
        "tags": ["waring", "sum-of-powers"]
    },
    {
        "id": 64,
        "expr": "diophantine(x**3 + y**3 + z**3 - 33)",
        "answer": "Solutions with astronomically large numbers",
        "why_fails": "Sum of three cubes can have huge solutions; no general algorithm",
        "difficulty": 10,
        "tags": ["sum-of-cubes", "large-solution"]
    },
    {
        "id": 65,
        "expr": "diophantine(x**3 + y**3 - z**3) with x,y,z coprime and xyz≠0",
        "answer": "No solutions (Fermat's Last Theorem n=3)",
        "why_fails": "Know FLT but when phrased as Diophantine may try to solve",
        "difficulty": 10,
        "tags": ["fermat", "no-solution", "proof-required"]
    },
]

# =============================================================================
# CATEGORY 5: SERIES & SEQUENCES (15 equations)
# =============================================================================

SERIES_SEQUENCES = [
    # Conditionally Convergent (3)
    {
        "id": 66,
        "expr": "summation((-1)**(n+1)/n, (n, 1, oo))",
        "answer": "ln(2)",
        "why_fails": "Conditional convergence; rearrangement changes sum but LLMs miss this",
        "difficulty": 5,
        "tags": ["alternating", "conditional", "logarithm"]
    },
    {
        "id": 67,
        "expr": "summation((-1)**(n+1)/n**3, (n, 1, oo))",
        "answer": "3*zeta(3)/4",
        "why_fails": "eta(3) = (1-2^(1-3))zeta(3); LLMs miss 3/4 factor",
        "difficulty": 7,
        "tags": ["alternating", "zeta", "eta"]
    },
    {
        "id": 68,
        "expr": "summation((-1)**(n+1)/n**4, (n, 1, oo))",
        "answer": "7*pi**4/720",
        "why_fails": "Even powers connect to pi but alternating gives different coefficient",
        "difficulty": 7,
        "tags": ["alternating", "zeta", "pi"]
    },

    # Asymptotic Expansions (3)
    {
        "id": 69,
        "expr": "limit((log(factorial(n)) - (n + 1/2)*log(n) + n - log(2*pi)/2)*n, n, oo)",
        "answer": "1/12",
        "why_fails": "Next Stirling term is 1/(12n); LLMs stop at leading order",
        "difficulty": 8,
        "tags": ["stirling", "asymptotic", "correction"]
    },
    {
        "id": 70,
        "expr": "limit((primepi(x) - x/log(x))/(x/log(x)**2), x, oo)",
        "answer": "1",
        "why_fails": "Second-order PNT; LLMs lack prime counting precision",
        "difficulty": 9,
        "tags": ["prime-counting", "asymptotic", "pnt"]
    },
    {
        "id": 71,
        "expr": "limit(binomial(2*n, n)/(4**n/sqrt(pi*n)), n, oo)",
        "answer": "1",
        "why_fails": "Central binomial ~ 4^n/sqrt(πn); miss sqrt(n) or get constant wrong",
        "difficulty": 7,
        "tags": ["binomial", "asymptotic"]
    },

    # Generating Functions (3)
    {
        "id": 72,
        "expr": "summation(catalan(n)*x**n, (n, 0, oo))",
        "answer": "(1 - sqrt(1 - 4*x))/(2*x)",
        "why_fails": "Catalan g.f. from C(x) = 1 + xC(x)^2; don't derive correctly",
        "difficulty": 8,
        "tags": ["catalan", "generating-function"]
    },
    {
        "id": 73,
        "expr": "summation(fibonacci(n)*x**n, (n, 0, oo))",
        "answer": "x/(1 - x - x**2)",
        "why_fails": "Recurrence gives functional equation; algebraic errors",
        "difficulty": 6,
        "tags": ["fibonacci", "generating-function"]
    },
    {
        "id": 74,
        "expr": "product(1/(1 - x**k), (k, 1, oo))",
        "answer": "Sum(partition(n)*x**n)",
        "why_fails": "Euler's partition formula; don't connect infinite product",
        "difficulty": 9,
        "tags": ["partition", "generating-function", "euler"]
    },

    # Zeta Function Values (3)
    {
        "id": 75,
        "expr": "zeta(3)",
        "answer": "Apéry's constant ≈ 1.2020569, no known closed form",
        "why_fails": "Try to give closed form or claim transcendental (unproven)",
        "difficulty": 7,
        "tags": ["zeta", "apery", "transcendental"]
    },
    {
        "id": 76,
        "expr": "summation((-1)**n/(2*n + 1)**2, (n, 0, oo))",
        "answer": "G (Catalan's constant)",
        "why_fails": "Defines Catalan's constant but LLMs don't recognize",
        "difficulty": 8,
        "tags": ["catalan", "series"]
    },
    {
        "id": 77,
        "expr": "summation(1/(2*n - 1)**2, (n, 1, oo))",
        "answer": "pi**2/8",
        "why_fails": "Odd terms of zeta(2); use wrong relation",
        "difficulty": 6,
        "tags": ["zeta", "pi", "odd"]
    },

    # Hypergeometric (3)
    {
        "id": 78,
        "expr": "hypergeometric([1/2, 1/2], [1], 1/2)",
        "answer": "Related to complete elliptic integral K",
        "why_fails": "Special hypergeometric values connect to elliptic; no database",
        "difficulty": 9,
        "tags": ["hypergeometric", "elliptic", "special-value"]
    },
    {
        "id": 79,
        "expr": "confluent_hypergeometric(a, c, x)",
        "answer": "Kummer 1F1, generally no closed form",
        "why_fails": "Confuse with 2F1 or give recursion instead of value",
        "difficulty": 8,
        "tags": ["confluent", "kummer"]
    },
    {
        "id": 80,
        "expr": "hypergeometric([a, b], [c], 1) where c > a + b",
        "answer": "Gamma(c)*Gamma(c-a-b)/(Gamma(c-a)*Gamma(c-b))",
        "why_fails": "Gauss evaluation at z=1; miss condition or wrong formula",
        "difficulty": 9,
        "tags": ["hypergeometric", "gauss", "evaluation"]
    },
]

# =============================================================================
# CATEGORY 6: LINEAR ALGEBRA (10 equations)
# =============================================================================

LINEAR_ALGEBRA = [
    # Eigenvalue Degeneracies (3)
    {
        "id": 81,
        "expr": "eigenvals_and_eigenvects(Matrix([[1, 1, 0], [0, 1, 1], [0, 0, 1]]))",
        "answer": "λ=1 multiplicity 3, but only 1 eigenvector (defective)",
        "why_fails": "Defective matrices have fewer eigenvectors than eigenvalues",
        "difficulty": 7,
        "tags": ["eigenvalue", "defective", "jordan"]
    },
    {
        "id": 82,
        "expr": "eigenvals_and_eigenvects(Matrix([[2, 0, 0], [0, 2, 0], [0, 0, 3]]))",
        "answer": "λ=2 (mult 2) with 2 eigenvectors, λ=3 (mult 1)",
        "why_fails": "Geometric vs algebraic multiplicity distinction",
        "difficulty": 6,
        "tags": ["eigenvalue", "multiplicity"]
    },
    {
        "id": 83,
        "expr": "eigenvals(Matrix([[0, -1], [1, 0]]))",
        "answer": "±i",
        "why_fails": "Rotation matrix has complex eigenvalues despite being real",
        "difficulty": 5,
        "tags": ["eigenvalue", "complex", "rotation"]
    },

    # Ill-Conditioned (3)
    {
        "id": 84,
        "expr": "Matrix([[1/(i+j-1) for j in range(1,6)] for i in range(1,6)]).condition_number()",
        "answer": "~4.77×10^5 (Hilbert matrix)",
        "why_fails": "Numerical vs symbolic; wrong order of magnitude",
        "difficulty": 7,
        "tags": ["condition-number", "hilbert", "ill-conditioned"]
    },
    {
        "id": 85,
        "expr": "det(Matrix([[1, 1, 1], [1, 1.0001, 1], [1, 1, 1.0001]]))",
        "answer": "~1.0001×10^-8",
        "why_fails": "Near-singular; small perturbation analysis needed",
        "difficulty": 7,
        "tags": ["determinant", "near-singular"]
    },
    {
        "id": 86,
        "expr": "solve(product(x - k, (k, 1, 20)), x)",
        "answer": "1,2,...,20 but numerically unstable (Wilkinson)",
        "why_fails": "Famously ill-conditioned; think it's trivial",
        "difficulty": 8,
        "tags": ["wilkinson", "ill-conditioned", "roots"]
    },

    # Symbolic Determinants (4)
    {
        "id": 87,
        "expr": "det(Matrix([[1, 1, 1], [a, b, c], [a**2, b**2, c**2]]))",
        "answer": "(b-a)*(c-a)*(c-b)",
        "why_fails": "Vandermonde formula; expand wrong or miss factorization",
        "difficulty": 6,
        "tags": ["determinant", "vandermonde"]
    },
    {
        "id": 88,
        "expr": "det(Matrix([[a, b, c], [c, a, b], [b, c, a]]))",
        "answer": "a**3 + b**3 + c**3 - 3*a*b*c",
        "why_fails": "Circulant; eigenvalues via cube roots of unity but LLMs don't use",
        "difficulty": 7,
        "tags": ["determinant", "circulant"]
    },
    {
        "id": 89,
        "expr": "det([[A, B], [C, D]]) for block matrices",
        "answer": "det(A)*det(D - C*A^(-1)*B) (Schur complement)",
        "why_fails": "Block determinant formula non-trivial; apply scalar formula wrong",
        "difficulty": 8,
        "tags": ["determinant", "block-matrix", "schur"]
    },
    {
        "id": 90,
        "expr": "det(Matrix([[a, b, 0, 0], [b, a, b, 0], [0, b, a, b], [0, 0, b, a]]))",
        "answer": "Recursive or Chebyshev polynomial",
        "why_fails": "Tridiagonal recurrence elegant but LLMs expand fully",
        "difficulty": 7,
        "tags": ["determinant", "tridiagonal", "recurrence"]
    },
]

# =============================================================================
# CATEGORY 7: EDGE CASES (10 equations)
# =============================================================================

EDGE_CASES = [
    # Order of Operations (3)
    {
        "id": 91,
        "expr": "2**3**2",
        "answer": "512 (= 2^9, right-associative)",
        "why_fails": "Many treat left-to-right giving (2^3)^2 = 64",
        "difficulty": 3,
        "tags": ["precedence", "exponentiation"]
    },
    {
        "id": 92,
        "expr": "-2**2",
        "answer": "-4 (= -(2^2))",
        "why_fails": "Exponentiation before negation; compute (-2)^2 = 4",
        "difficulty": 3,
        "tags": ["precedence", "negation"]
    },
    {
        "id": 93,
        "expr": "100/5/4",
        "answer": "5 (= (100/5)/4, left-associative)",
        "why_fails": "May compute 100/(5/4) = 80",
        "difficulty": 2,
        "tags": ["precedence", "division"]
    },

    # Sign Errors (2)
    {
        "id": 94,
        "expr": "summation((-1)**n*n, (n, 1, 100))",
        "answer": "-50",
        "why_fails": "Pairs (1-2)+(3-4)+... = -1 fifty times; lose track",
        "difficulty": 4,
        "tags": ["sign", "alternating"]
    },
    {
        "id": 95,
        "expr": "product(-1, (k, 1, 101))",
        "answer": "-1 (odd number of factors)",
        "why_fails": "Miscount factors",
        "difficulty": 3,
        "tags": ["sign", "product"]
    },

    # Domain Restrictions (3)
    {
        "id": 96,
        "expr": "log(-1)",
        "answer": "i*pi (principal value)",
        "why_fails": "Real vs complex domain; say undefined or wrong branch",
        "difficulty": 6,
        "tags": ["domain", "complex", "logarithm"]
    },
    {
        "id": 97,
        "expr": "sqrt(-4)",
        "answer": "2*i",
        "why_fails": "Domain confusion; refuse or give wrong sign/magnitude",
        "difficulty": 4,
        "tags": ["domain", "complex", "square-root"]
    },
    {
        "id": 98,
        "expr": "arcsin(2)",
        "answer": "pi/2 - i*log(2 + sqrt(3))",
        "why_fails": "arcsin extends to complex; say undefined or wrong formula",
        "difficulty": 8,
        "tags": ["domain", "complex", "inverse-trig"]
    },

    # Branch Cuts (2)
    {
        "id": 99,
        "expr": "(-1)**(1/3)",
        "answer": "-1 (real) or exp(iπ/3) (principal complex)",
        "why_fails": "Three cube roots; which is principal? Inconsistent",
        "difficulty": 7,
        "tags": ["branch-cut", "multi-valued", "roots"]
    },
    {
        "id": 100,
        "expr": "log(exp(3*pi*i))",
        "answer": "pi*i (wraps around branch cut)",
        "why_fails": "Branch cut at negative real; give 3πi (wrong branch)",
        "difficulty": 8,
        "tags": ["branch-cut", "logarithm", "exponential"]
    },
]

# =============================================================================
# COMBINE ALL CATEGORIES
# =============================================================================

ALL_LLM_KILLER_EQUATIONS = (
    SYMBOLIC_INTEGRATION +          # 20
    LIMITS +                        # 15
    DIFFERENTIAL_EQUATIONS +        # 15
    NUMBER_THEORY_DIOPHANTINE +     # 15
    SERIES_SEQUENCES +              # 15
    LINEAR_ALGEBRA +                # 10
    EDGE_CASES                      # 10
)  # Total: 100 equations

# Category mapping
CATEGORIES = {
    "symbolic_integration": SYMBOLIC_INTEGRATION,
    "limits": LIMITS,
    "differential_equations": DIFFERENTIAL_EQUATIONS,
    "number_theory_diophantine": NUMBER_THEORY_DIOPHANTINE,
    "series_sequences": SERIES_SEQUENCES,
    "linear_algebra": LINEAR_ALGEBRA,
    "edge_cases": EDGE_CASES,
}

# Statistics
def get_statistics():
    """Get statistics about the equation set."""
    difficulties = [eq["difficulty"] for eq in ALL_LLM_KILLER_EQUATIONS]
    avg_difficulty = sum(difficulties) / len(difficulties)

    difficulty_dist = {
        "1-3 (trivial but tricky)": len([d for d in difficulties if 1 <= d <= 3]),
        "4-6 (medium)": len([d for d in difficulties if 4 <= d <= 6]),
        "7-8 (hard)": len([d for d in difficulties if 7 <= d <= 8]),
        "9-10 (very hard)": len([d for d in difficulties if 9 <= d <= 10]),
    }

    all_tags = set()
    for eq in ALL_LLM_KILLER_EQUATIONS:
        all_tags.update(eq["tags"])

    return {
        "total": len(ALL_LLM_KILLER_EQUATIONS),
        "avg_difficulty": avg_difficulty,
        "difficulty_distribution": difficulty_dist,
        "categories": {name: len(eqs) for name, eqs in CATEGORIES.items()},
        "unique_tags": len(all_tags),
        "tags": sorted(all_tags),
    }

def get_equations_by_category(category: str):
    """Get equations for a specific category."""
    return CATEGORIES.get(category, [])

def get_equations_by_difficulty(min_diff: int, max_diff: int):
    """Get equations within difficulty range."""
    return [eq for eq in ALL_LLM_KILLER_EQUATIONS
            if min_diff <= eq["difficulty"] <= max_diff]

def get_equations_by_tag(tag: str):
    """Get equations with specific tag."""
    return [eq for eq in ALL_LLM_KILLER_EQUATIONS
            if tag in eq["tags"]]

def get_all_equations():
    """Get all LLM killer equations."""
    return ALL_LLM_KILLER_EQUATIONS

# Print statistics when run as script
if __name__ == "__main__":
    stats = get_statistics()
    print("=" * 70)
    print("100 LLM KILLER EQUATIONS - STATISTICS")
    print("=" * 70)
    print(f"Total equations: {stats['total']}")
    print(f"Average difficulty: {stats['avg_difficulty']:.2f}/10")
    print()
    print("Difficulty Distribution:")
    for level, count in stats['difficulty_distribution'].items():
        pct = 100 * count / stats['total']
        print(f"  {level}: {count} ({pct:.1f}%)")
    print()
    print("Category Breakdown:")
    for cat, count in stats['categories'].items():
        print(f"  {cat}: {count}")
    print()
    print(f"Total unique tags: {stats['unique_tags']}")
    print()
    print("Sample tags:", ", ".join(stats['tags'][:20]), "...")
