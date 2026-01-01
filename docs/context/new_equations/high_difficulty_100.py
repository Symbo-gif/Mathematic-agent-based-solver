#!/usr/bin/env python3
# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
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
100 High-Difficulty Research-Level Mathematical Equations
==========================================================
Generated to fill coverage gaps across all mathematical domains.
Target difficulty: MIT Integration Bee / Putnam Competition level.

These equations are UNIQUE and do not duplicate any equations from:
- ultra_edge_25_test.py
- edgiest_50_test.py
- edgy_100_test.py
- stress_test_equations.py

Coverage spans:
- Complex Analysis (contour integrals, residue theorem)
- Fourier/Laplace transforms
- Orthogonal polynomials (Legendre, Chebyshev, Jacobi)
- Elliptic integrals and functions
- Hypergeometric functions
- Partial differential equations
- Advanced calculus (limits, series, integrals)
- Linear algebra (matrix exponentials, spectral theory)
- Number theory (advanced)
- Probability/Statistics (advanced)
- Physics applications (quantum, statistical mechanics)
"""

# =============================================================================
# EQUATION CATALOG - 100 HIGH-DIFFICULTY RESEARCH-LEVEL EQUATIONS
# =============================================================================

HIGH_DIFFICULTY_EQUATIONS = [
    # =========================================================================
    # SECTION 1: COMPLEX ANALYSIS (HD-001 to HD-010)
    # Contour integrals, residue theorem, Cauchy formulas
    # =========================================================================
    {
        "id": "HD-001",
        "equation": "contour_integral(exp(I*z)/(z**2 + 1), z, unit_circle)",
        "domain": "complex_analysis.contour_integrals",
        "difficulty": "research",
        "expected": "2*pi*I*exp(-1)/2",
        "notes": "Residue at z=i inside unit circle; fundamental contour integration"
    },
    {
        "id": "HD-002",
        "equation": "contour_integral(z**n/(z - a), z, circle(0, r))",
        "domain": "complex_analysis.cauchy",
        "difficulty": "research",
        "expected": "2*pi*I*a**n if |a| < r else 0",
        "notes": "Cauchy integral formula for z^n; tests branch conditions"
    },
    {
        "id": "HD-003",
        "equation": "residue(sin(z)/z**3, z, 0)",
        "domain": "complex_analysis.residues",
        "difficulty": "research",
        "expected": "-1/6",
        "notes": "Residue of sin(z)/z^3 at z=0 using Laurent expansion"
    },
    {
        "id": "HD-004",
        "equation": "contour_integral(1/(z**4 + 1), z, upper_half_plane)",
        "domain": "complex_analysis.contour_integrals",
        "difficulty": "research",
        "expected": "pi/sqrt(2)",
        "notes": "Integration over upper half-plane using residues at exp(I*pi/4), exp(3*I*pi/4)"
    },
    {
        "id": "HD-005",
        "equation": "contour_integral(log(z)/(z**2 + 1), z, keyhole_contour)",
        "domain": "complex_analysis.branch_cuts",
        "difficulty": "research",
        "expected": "0",
        "notes": "Keyhole contour for multivalued function; tests branch cut handling"
    },
    {
        "id": "HD-006",
        "equation": "contour_integral(exp(I*a*z)/(z**2 + b**2), z, upper_half_plane)",
        "domain": "complex_analysis.fourier_integrals",
        "difficulty": "research",
        "expected": "pi*exp(-a*b)/b for a > 0, b > 0",
        "notes": "Jordan's lemma application for Fourier-type integrals"
    },
    {
        "id": "HD-007",
        "equation": "residue(Gamma(z)*Gamma(1-z), z, n)",
        "domain": "complex_analysis.special_functions",
        "difficulty": "research",
        "expected": "(-1)**n for integer n",
        "notes": "Residues of reflection formula Gamma(z)Gamma(1-z) = pi/sin(pi*z)"
    },
    {
        "id": "HD-008",
        "equation": "contour_integral(z**(a-1)/(1+z), z, Hankel_contour)",
        "domain": "complex_analysis.hankel",
        "difficulty": "research",
        "expected": "pi/sin(pi*a)",
        "notes": "Hankel contour representation of pi*csc(pi*a)"
    },
    {
        "id": "HD-009",
        "equation": "sum_residues(cot(pi*z)/z**2, z, integers)",
        "domain": "complex_analysis.series",
        "difficulty": "research",
        "expected": "pi**2/3",
        "notes": "Derivation of zeta(2) = pi^2/6 via residue summation"
    },
    {
        "id": "HD-010",
        "equation": "contour_integral(exp(-z**2), z, Fresnel_contour)",
        "domain": "complex_analysis.fresnel",
        "difficulty": "research",
        "expected": "sqrt(pi)*(1 + I)/2",
        "notes": "Complex Gaussian integral along 45-degree ray"
    },

    # =========================================================================
    # SECTION 2: FOURIER AND LAPLACE TRANSFORMS (HD-011 to HD-020)
    # Transform pairs, convolutions, inverse transforms
    # =========================================================================
    {
        "id": "HD-011",
        "equation": "laplace_transform(t**n * exp(-a*t), t, s)",
        "domain": "transforms.laplace",
        "difficulty": "research",
        "expected": "factorial(n)/(s + a)**(n+1)",
        "notes": "Laplace transform of t^n * exp(-at); fundamental transform pair"
    },
    {
        "id": "HD-012",
        "equation": "inverse_laplace(1/(s**2 + omega**2), s, t)",
        "domain": "transforms.inverse_laplace",
        "difficulty": "research",
        "expected": "sin(omega*t)/omega",
        "notes": "Inverse Laplace transform yielding sinusoidal response"
    },
    {
        "id": "HD-013",
        "equation": "fourier_transform(exp(-a*abs(x)), x, k)",
        "domain": "transforms.fourier",
        "difficulty": "research",
        "expected": "2*a/(a**2 + k**2)",
        "notes": "Fourier transform of two-sided exponential (Lorentzian)"
    },
    {
        "id": "HD-014",
        "equation": "fourier_transform(1/(x**2 + a**2), x, k)",
        "domain": "transforms.fourier",
        "difficulty": "research",
        "expected": "pi*exp(-a*abs(k))/a",
        "notes": "Fourier transform of Lorentzian; yields exponential decay"
    },
    {
        "id": "HD-015",
        "equation": "laplace_transform(sin(omega*t)/t, t, s)",
        "domain": "transforms.laplace",
        "difficulty": "research",
        "expected": "arctan(omega/s)",
        "notes": "Laplace transform of sinc-like function"
    },
    {
        "id": "HD-016",
        "equation": "inverse_laplace(log(s)/s, s, t)",
        "domain": "transforms.inverse_laplace",
        "difficulty": "research",
        "expected": "-gamma - log(t)",
        "notes": "Inverse Laplace involving logarithm; yields Euler-Mascheroni"
    },
    {
        "id": "HD-017",
        "equation": "fourier_transform(Heaviside(x)*exp(-a*x)*sin(b*x), x, k)",
        "domain": "transforms.fourier",
        "difficulty": "research",
        "expected": "b/((a + I*k)**2 + b**2)",
        "notes": "One-sided damped sine Fourier transform"
    },
    {
        "id": "HD-018",
        "equation": "laplace_transform(BesselJ(0, a*t), t, s)",
        "domain": "transforms.laplace",
        "difficulty": "research",
        "expected": "1/sqrt(s**2 + a**2)",
        "notes": "Laplace transform of J_0(at); connects to special functions"
    },
    {
        "id": "HD-019",
        "equation": "mellin_transform(exp(-x), x, s)",
        "domain": "transforms.mellin",
        "difficulty": "research",
        "expected": "Gamma(s)",
        "notes": "Mellin transform defining the Gamma function"
    },
    {
        "id": "HD-020",
        "equation": "inverse_fourier((sin(k*a)/k), k, x)",
        "domain": "transforms.inverse_fourier",
        "difficulty": "research",
        "expected": "pi*rect(x/a)",
        "notes": "Inverse Fourier of sinc yields rectangular pulse"
    },

    # =========================================================================
    # SECTION 3: ORTHOGONAL POLYNOMIALS (HD-021 to HD-030)
    # Legendre, Chebyshev, Jacobi, Laguerre, Hermite
    # =========================================================================
    {
        "id": "HD-021",
        "equation": "integrate(Legendre(m, x)*Legendre(n, x), (x, -1, 1))",
        "domain": "orthogonal_polynomials.legendre",
        "difficulty": "research",
        "expected": "2/(2*n+1) if m == n else 0",
        "notes": "Legendre polynomial orthogonality relation"
    },
    {
        "id": "HD-022",
        "equation": "integrate(Chebyshev_T(m, x)*Chebyshev_T(n, x)/sqrt(1-x**2), (x, -1, 1))",
        "domain": "orthogonal_polynomials.chebyshev",
        "difficulty": "research",
        "expected": "pi if m == n == 0 else pi/2 if m == n else 0",
        "notes": "Chebyshev T polynomial orthogonality with weight 1/sqrt(1-x^2)"
    },
    {
        "id": "HD-023",
        "equation": "integrate(Chebyshev_U(m, x)*Chebyshev_U(n, x)*sqrt(1-x**2), (x, -1, 1))",
        "domain": "orthogonal_polynomials.chebyshev",
        "difficulty": "research",
        "expected": "pi/2 if m == n else 0",
        "notes": "Chebyshev U polynomial orthogonality with weight sqrt(1-x^2)"
    },
    {
        "id": "HD-024",
        "equation": "integrate(Laguerre(m, x)*Laguerre(n, x)*exp(-x), (x, 0, oo))",
        "domain": "orthogonal_polynomials.laguerre",
        "difficulty": "research",
        "expected": "1 if m == n else 0",
        "notes": "Laguerre polynomial orthogonality with exponential weight"
    },
    {
        "id": "HD-025",
        "equation": "integrate(Hermite(m, x)*Hermite(n, x)*exp(-x**2), (x, -oo, oo))",
        "domain": "orthogonal_polynomials.hermite",
        "difficulty": "research",
        "expected": "sqrt(pi)*2**n*factorial(n) if m == n else 0",
        "notes": "Hermite polynomial orthogonality (physicist's convention)"
    },
    {
        "id": "HD-026",
        "equation": "integrate(Jacobi(n, alpha, beta, x)*(1-x)**alpha*(1+x)**beta, (x, -1, 1))",
        "domain": "orthogonal_polynomials.jacobi",
        "difficulty": "research",
        "expected": "2**(alpha+beta+1)*Gamma(n+alpha+1)*Gamma(n+beta+1)/(factorial(n)*(2*n+alpha+beta+1)*Gamma(n+alpha+beta+1))",
        "notes": "Jacobi polynomial normalization integral"
    },
    {
        "id": "HD-027",
        "equation": "summation(Legendre(n, x)*t**n, (n, 0, oo))",
        "domain": "orthogonal_polynomials.generating_functions",
        "difficulty": "research",
        "expected": "1/sqrt(1 - 2*x*t + t**2)",
        "notes": "Generating function for Legendre polynomials"
    },
    {
        "id": "HD-028",
        "equation": "limit((1 - x**2)*diff(Legendre(n, x), x, 2) - 2*x*diff(Legendre(n, x), x) + n*(n+1)*Legendre(n, x), x, 0)",
        "domain": "orthogonal_polynomials.legendre",
        "difficulty": "research",
        "expected": "0",
        "notes": "Verification of Legendre differential equation"
    },
    {
        "id": "HD-029",
        "equation": "integrate(x*Legendre(n, x)*Legendre(n-1, x), (x, -1, 1))",
        "domain": "orthogonal_polynomials.recurrence",
        "difficulty": "research",
        "expected": "2*n/(4*n**2 - 1)",
        "notes": "Matrix element from Legendre recurrence relation"
    },
    {
        "id": "HD-030",
        "equation": "Legendre(n, cos(theta))",
        "domain": "orthogonal_polynomials.special_values",
        "difficulty": "research",
        "expected": "cos(n*arccos(cos(theta))) for Chebyshev relation",
        "notes": "Connection between Legendre and trigonometric functions"
    },

    # =========================================================================
    # SECTION 4: ELLIPTIC INTEGRALS AND FUNCTIONS (HD-031 to HD-040)
    # Complete/incomplete elliptic integrals, Jacobi functions
    # =========================================================================
    {
        "id": "HD-031",
        "equation": "elliptic_K(0)",
        "domain": "elliptic.complete",
        "difficulty": "research",
        "expected": "pi/2",
        "notes": "Complete elliptic integral of first kind at k=0"
    },
    {
        "id": "HD-032",
        "equation": "elliptic_E(0)",
        "domain": "elliptic.complete",
        "difficulty": "research",
        "expected": "pi/2",
        "notes": "Complete elliptic integral of second kind at k=0"
    },
    {
        "id": "HD-033",
        "equation": "elliptic_K(k)*elliptic_E(sqrt(1 - k**2)) + elliptic_E(k)*elliptic_K(sqrt(1 - k**2)) - elliptic_K(k)*elliptic_K(sqrt(1 - k**2))",
        "domain": "elliptic.legendre_relation",
        "difficulty": "research",
        "expected": "pi/2",
        "notes": "Legendre relation for complete elliptic integrals"
    },
    {
        "id": "HD-034",
        "equation": "integrate(1/sqrt((1 - t**2)*(1 - k**2*t**2)), (t, 0, x))",
        "domain": "elliptic.incomplete",
        "difficulty": "research",
        "expected": "elliptic_F(arcsin(x), k)",
        "notes": "Definition of incomplete elliptic integral of first kind"
    },
    {
        "id": "HD-035",
        "equation": "integrate(sqrt((1 - k**2*t**2)/(1 - t**2)), (t, 0, x))",
        "domain": "elliptic.incomplete",
        "difficulty": "research",
        "expected": "elliptic_E(arcsin(x), k)",
        "notes": "Definition of incomplete elliptic integral of second kind"
    },
    {
        "id": "HD-036",
        "equation": "diff(elliptic_K(k), k)",
        "domain": "elliptic.derivatives",
        "difficulty": "research",
        "expected": "(elliptic_E(k) - (1 - k**2)*elliptic_K(k))/(k*(1 - k**2))",
        "notes": "Derivative of complete elliptic integral K(k)"
    },
    {
        "id": "HD-037",
        "equation": "jacobi_sn(0, k)",
        "domain": "elliptic.jacobi",
        "difficulty": "research",
        "expected": "0",
        "notes": "Jacobi elliptic function sn at u=0"
    },
    {
        "id": "HD-038",
        "equation": "jacobi_cn(0, k)",
        "domain": "elliptic.jacobi",
        "difficulty": "research",
        "expected": "1",
        "notes": "Jacobi elliptic function cn at u=0"
    },
    {
        "id": "HD-039",
        "equation": "jacobi_sn(u, k)**2 + jacobi_cn(u, k)**2",
        "domain": "elliptic.jacobi_identities",
        "difficulty": "research",
        "expected": "1",
        "notes": "Fundamental Jacobi identity sn^2 + cn^2 = 1"
    },
    {
        "id": "HD-040",
        "equation": "integrate(1/sqrt(1 - k**2*sin(theta)**2), (theta, 0, pi/2))",
        "domain": "elliptic.complete",
        "difficulty": "research",
        "expected": "elliptic_K(k)",
        "notes": "Complete elliptic integral K via trigonometric form"
    },

    # =========================================================================
    # SECTION 5: HYPERGEOMETRIC FUNCTIONS (HD-041 to HD-050)
    # 2F1, generalized hypergeometric, confluent
    # =========================================================================
    {
        "id": "HD-041",
        "equation": "hypergeometric([a, b], [c], 1)",
        "domain": "hypergeometric.gauss",
        "difficulty": "research",
        "expected": "Gamma(c)*Gamma(c-a-b)/(Gamma(c-a)*Gamma(c-b)) for Re(c-a-b) > 0",
        "notes": "Gauss summation theorem for 2F1 at z=1"
    },
    {
        "id": "HD-042",
        "equation": "hypergeometric([1/2, 1/2], [1], z)",
        "domain": "hypergeometric.special",
        "difficulty": "research",
        "expected": "2*elliptic_K(sqrt(z))/pi",
        "notes": "Hypergeometric representation of complete elliptic integral"
    },
    {
        "id": "HD-043",
        "equation": "hypergeometric([-n, a], [b], 1)",
        "domain": "hypergeometric.chu_vandermonde",
        "difficulty": "research",
        "expected": "pochhammer(b-a, n)/pochhammer(b, n)",
        "notes": "Chu-Vandermonde identity for terminating 2F1"
    },
    {
        "id": "HD-044",
        "equation": "hypergeometric([a, b], [a + b + 1/2], 1/2)",
        "domain": "hypergeometric.kummer",
        "difficulty": "research",
        "expected": "Gamma(1/2)*Gamma(a + b + 1/2)/(Gamma(a + 1/2)*Gamma(b + 1/2))",
        "notes": "Kummer's quadratic transformation at z=1/2"
    },
    {
        "id": "HD-045",
        "equation": "confluent_hypergeometric(a, b, z)",
        "domain": "hypergeometric.confluent",
        "difficulty": "research",
        "expected": "1F1(a; b; z) via Kummer transformation",
        "notes": "Confluent hypergeometric 1F1 definition and properties"
    },
    {
        "id": "HD-046",
        "equation": "hypergeometric([1, 1], [2], -z)",
        "domain": "hypergeometric.logarithm",
        "difficulty": "research",
        "expected": "log(1 + z)/z",
        "notes": "Hypergeometric representation of logarithm"
    },
    {
        "id": "HD-047",
        "equation": "hypergeometric([1/2], [], z**2/4)",
        "domain": "hypergeometric.bessel",
        "difficulty": "research",
        "expected": "exp(z)",
        "notes": "Connection to Bessel functions via limiting cases"
    },
    {
        "id": "HD-048",
        "equation": "hypergeometric([a, 1-a], [c], (1-z)/2)",
        "domain": "hypergeometric.legendre",
        "difficulty": "research",
        "expected": "Legendre function P_{a-1}^{1-c}(z)",
        "notes": "Connection between hypergeometric and Legendre functions"
    },
    {
        "id": "HD-049",
        "equation": "diff(hypergeometric([a, b], [c], z), z)",
        "domain": "hypergeometric.derivatives",
        "difficulty": "research",
        "expected": "a*b/c * hypergeometric([a+1, b+1], [c+1], z)",
        "notes": "Differentiation formula for 2F1"
    },
    {
        "id": "HD-050",
        "equation": "hypergeometric([a], [b], z) - hypergeometric([a+1], [b], z)",
        "domain": "hypergeometric.contiguous",
        "difficulty": "research",
        "expected": "-z*a/(b*(b+1)) * hypergeometric([a+1], [b+2], z)",
        "notes": "Contiguous relations for 1F1"
    },

    # =========================================================================
    # SECTION 6: PARTIAL DIFFERENTIAL EQUATIONS (HD-051 to HD-060)
    # Heat, wave, Laplace, Schrodinger
    # =========================================================================
    {
        "id": "HD-051",
        "equation": "pdesolve(diff(u(x,t), t) - k*diff(u(x,t), x, 2), u(x,t))",
        "domain": "pde.heat",
        "difficulty": "research",
        "expected": "summation(c_n*sin(n*pi*x/L)*exp(-k*n**2*pi**2*t/L**2), (n, 1, oo))",
        "notes": "Heat equation solution via separation of variables"
    },
    {
        "id": "HD-052",
        "equation": "pdesolve(diff(u(x,t), t, 2) - c**2*diff(u(x,t), x, 2), u(x,t))",
        "domain": "pde.wave",
        "difficulty": "research",
        "expected": "f(x - c*t) + g(x + c*t)",
        "notes": "D'Alembert solution to 1D wave equation"
    },
    {
        "id": "HD-053",
        "equation": "pdesolve(diff(u(x,y), x, 2) + diff(u(x,y), y, 2), u(x,y))",
        "domain": "pde.laplace",
        "difficulty": "research",
        "expected": "harmonic function",
        "notes": "Laplace equation in 2D; mean value property"
    },
    {
        "id": "HD-054",
        "equation": "integrate(exp(-x**2/(4*k*t))/(2*sqrt(pi*k*t)), (x, -oo, oo))",
        "domain": "pde.heat_kernel",
        "difficulty": "research",
        "expected": "1",
        "notes": "Heat kernel normalization; fundamental solution"
    },
    {
        "id": "HD-055",
        "equation": "pdesolve(I*hbar*diff(psi(x,t), t) + hbar**2/(2*m)*diff(psi(x,t), x, 2), psi(x,t))",
        "domain": "pde.schrodinger",
        "difficulty": "research",
        "expected": "exp(I*(k*x - omega*t)) for free particle",
        "notes": "Free particle Schrodinger equation"
    },
    {
        "id": "HD-056",
        "equation": "green_function(diff(G, x, 2) + diff(G, y, 2) + delta(x - xi)*delta(y - eta))",
        "domain": "pde.greens_function",
        "difficulty": "research",
        "expected": "-1/(2*pi)*log(sqrt((x-xi)**2 + (y-eta)**2))",
        "notes": "2D Laplacian Green's function"
    },
    {
        "id": "HD-057",
        "equation": "pdesolve(diff(u, t) + u*diff(u, x), u(x,t))",
        "domain": "pde.burgers",
        "difficulty": "research",
        "expected": "implicit: x = u*t + f^{-1}(u)",
        "notes": "Inviscid Burgers equation by method of characteristics"
    },
    {
        "id": "HD-058",
        "equation": "pdesolve(diff(u, t) + c*diff(u, x) + d*diff(u, x, 3), u(x,t))",
        "domain": "pde.kdv",
        "difficulty": "research",
        "expected": "soliton solutions",
        "notes": "Linearized KdV equation; dispersive waves"
    },
    {
        "id": "HD-059",
        "equation": "laplacian_spherical(u(r, theta, phi))",
        "domain": "pde.spherical",
        "difficulty": "research",
        "expected": "1/r**2*diff(r**2*diff(u,r),r) + 1/(r**2*sin(theta))*diff(sin(theta)*diff(u,theta),theta) + 1/(r**2*sin(theta)**2)*diff(u,phi,2)",
        "notes": "Laplacian in spherical coordinates"
    },
    {
        "id": "HD-060",
        "equation": "pdesolve(diff(u, x, 2) + diff(u, y, 2) + lambda_*u, u(x,y))",
        "domain": "pde.helmholtz",
        "difficulty": "research",
        "expected": "exp(I*k*x)*exp(I*m*y) with k**2 + m**2 = lambda_",
        "notes": "Helmholtz equation; eigenvalue problem"
    },

    # =========================================================================
    # SECTION 7: ADVANCED CALCULUS - LIMITS AND SERIES (HD-061 to HD-070)
    # Unusual limits, exotic series, asymptotic analysis
    # =========================================================================
    {
        "id": "HD-061",
        "equation": "limit((1 + 1/x)**(x**2) / exp(x + 1/2), x, oo)",
        "domain": "calculus.limits",
        "difficulty": "research",
        "expected": "1/sqrt(e)",
        "notes": "Refined Stirling-type limit; second-order correction"
    },
    {
        "id": "HD-062",
        "equation": "summation(zeta(2*n)*x**(2*n), (n, 1, oo))",
        "domain": "calculus.series",
        "difficulty": "research",
        "expected": "(1 - pi*x*cot(pi*x))/2",
        "notes": "Generating function for even zeta values"
    },
    {
        "id": "HD-063",
        "equation": "limit((summation(1/k, (k, 1, n)) - log(n) - gamma)**(-1) / n, n, oo)",
        "domain": "calculus.limits",
        "difficulty": "research",
        "expected": "2",
        "notes": "Rate of convergence of harmonic series to log + gamma"
    },
    {
        "id": "HD-064",
        "equation": "summation((-1)**(n-1) * zeta(n) / n, (n, 2, oo))",
        "domain": "calculus.series",
        "difficulty": "research",
        "expected": "gamma",
        "notes": "Series representation of Euler-Mascheroni constant"
    },
    {
        "id": "HD-065",
        "equation": "limit(product(cos(x/2**n), (n, 1, N)) * 2**N, N, oo)",
        "domain": "calculus.products",
        "difficulty": "research",
        "expected": "sin(x)/x",
        "notes": "Vieta-like infinite product for sinc function"
    },
    {
        "id": "HD-066",
        "equation": "summation(1/(n**2 + a**2), (n, -oo, oo))",
        "domain": "calculus.series",
        "difficulty": "research",
        "expected": "pi*coth(pi*a)/a",
        "notes": "Symmetric sum via contour integration"
    },
    {
        "id": "HD-067",
        "equation": "limit((Gamma(x + 1)/Gamma(x + 1/2))**2 / x, x, oo)",
        "domain": "calculus.limits",
        "difficulty": "research",
        "expected": "1",
        "notes": "Gamma function ratio limit; Gautschi's inequality limit"
    },
    {
        "id": "HD-068",
        "equation": "summation((-1)**n/(2*n + 1)**3, (n, 0, oo))",
        "domain": "calculus.series",
        "difficulty": "research",
        "expected": "pi**3/32",
        "notes": "Dirichlet beta function beta(3)"
    },
    {
        "id": "HD-069",
        "equation": "limit(n**s * (zeta(s) - summation(1/k**s, (k, 1, n))), n, oo)",
        "domain": "calculus.limits",
        "difficulty": "research",
        "expected": "1/(s-1) for s > 1",
        "notes": "Remainder in partial sums of zeta function"
    },
    {
        "id": "HD-070",
        "equation": "summation(log(n)/n**2, (n, 2, oo))",
        "domain": "calculus.series",
        "difficulty": "research",
        "expected": "-zeta'(2) = pi**2*gamma/6 + zeta(2)*log(2*pi) - 12*log(A)",
        "notes": "Derivative of zeta at s=2; involves Glaisher-Kinkelin constant A"
    },

    # =========================================================================
    # SECTION 8: ADVANCED LINEAR ALGEBRA (HD-071 to HD-080)
    # Matrix exponentials, spectral theory, tensor products
    # =========================================================================
    {
        "id": "HD-071",
        "equation": "matrix_exponential(Matrix([[0, 1], [-1, 0]]) * t)",
        "domain": "linear_algebra.matrix_exp",
        "difficulty": "research",
        "expected": "Matrix([[cos(t), sin(t)], [-sin(t), cos(t)]])",
        "notes": "Matrix exponential of rotation generator; yields rotation matrix"
    },
    {
        "id": "HD-072",
        "equation": "matrix_exponential(Matrix([[a, b], [0, a]]) * t)",
        "domain": "linear_algebra.matrix_exp",
        "difficulty": "research",
        "expected": "exp(a*t) * Matrix([[1, b*t], [0, 1]])",
        "notes": "Matrix exponential of Jordan block"
    },
    {
        "id": "HD-073",
        "equation": "trace(matrix_exponential(A))",
        "domain": "linear_algebra.spectral",
        "difficulty": "research",
        "expected": "summation(exp(lambda_i), (i, 1, n)) where lambda_i are eigenvalues",
        "notes": "Trace of matrix exponential in terms of eigenvalues"
    },
    {
        "id": "HD-074",
        "equation": "det(matrix_exponential(A))",
        "domain": "linear_algebra.spectral",
        "difficulty": "research",
        "expected": "exp(trace(A))",
        "notes": "Determinant of matrix exponential; Jacobi's formula"
    },
    {
        "id": "HD-075",
        "equation": "sylvester_solve(A*X + X*B, C)",
        "domain": "linear_algebra.matrix_equations",
        "difficulty": "research",
        "expected": "X = integral(exp(-A*t)*C*exp(-B*t), (t, 0, oo)) if stable",
        "notes": "Sylvester equation solution via integral representation"
    },
    {
        "id": "HD-076",
        "equation": "kronecker_product(Matrix([[a, b], [c, d]]), Matrix([[1, 0], [0, 1]]))",
        "domain": "linear_algebra.tensor",
        "difficulty": "research",
        "expected": "Matrix([[a, 0, b, 0], [0, a, 0, b], [c, 0, d, 0], [0, c, 0, d]])",
        "notes": "Kronecker product with identity; block diagonal structure"
    },
    {
        "id": "HD-077",
        "equation": "spectral_radius(Matrix([[0, 1, 0], [0, 0, 1], [1, 0, 0]]))",
        "domain": "linear_algebra.spectral",
        "difficulty": "research",
        "expected": "1",
        "notes": "Spectral radius of cyclic permutation matrix"
    },
    {
        "id": "HD-078",
        "equation": "condition_number(Hilbert_matrix(n))",
        "domain": "linear_algebra.numerical",
        "difficulty": "research",
        "expected": "O(exp(3.5*n)) asymptotically",
        "notes": "Hilbert matrix is notoriously ill-conditioned"
    },
    {
        "id": "HD-079",
        "equation": "limit(Matrix([[1, 1/n], [0, 1]])**n, n, oo)",
        "domain": "linear_algebra.limits",
        "difficulty": "research",
        "expected": "Matrix([[1, 1], [0, 1]]) (does not converge to exp)",
        "notes": "Matrix power limit; contrast with (I + A/n)^n -> exp(A)"
    },
    {
        "id": "HD-080",
        "equation": "permanent(Matrix([[1, 1, 1], [1, 1, 1], [1, 1, 1]]))",
        "domain": "linear_algebra.permanent",
        "difficulty": "research",
        "expected": "6",
        "notes": "Permanent of all-ones matrix; n! for n x n"
    },

    # =========================================================================
    # SECTION 9: ADVANCED NUMBER THEORY (HD-081 to HD-088)
    # Modular forms, quadratic residues, continued fractions
    # =========================================================================
    {
        "id": "HD-081",
        "equation": "continued_fraction(sqrt(2))",
        "domain": "number_theory.continued_fractions",
        "difficulty": "research",
        "expected": "[1; 2, 2, 2, ...] (periodic)",
        "notes": "Continued fraction of sqrt(2); simplest periodic CF"
    },
    {
        "id": "HD-082",
        "equation": "continued_fraction(e)",
        "domain": "number_theory.continued_fractions",
        "difficulty": "research",
        "expected": "[2; 1, 2, 1, 1, 4, 1, 1, 6, ...] pattern",
        "notes": "Continued fraction of e; remarkable pattern"
    },
    {
        "id": "HD-083",
        "equation": "quadratic_residue_sum(p)",
        "domain": "number_theory.quadratic_residues",
        "difficulty": "research",
        "expected": "0 for odd prime p",
        "notes": "Sum of Legendre symbols (a/p) for a = 1 to p-1 is 0"
    },
    {
        "id": "HD-084",
        "equation": "dedekind_eta(tau)**24",
        "domain": "number_theory.modular_forms",
        "difficulty": "research",
        "expected": "Delta(tau) = (2*pi)**12 * q * product((1-q**n)**24, (n, 1, oo))",
        "notes": "Ramanujan's discriminant modular form"
    },
    {
        "id": "HD-085",
        "equation": "theta_3(0, q)**4 - theta_4(0, q)**4",
        "domain": "number_theory.theta_functions",
        "difficulty": "research",
        "expected": "theta_2(0, q)**4",
        "notes": "Jacobi theta function identity"
    },
    {
        "id": "HD-086",
        "equation": "summation(divisor_sigma(n)*q**n, (n, 1, oo))",
        "domain": "number_theory.modular_forms",
        "difficulty": "research",
        "expected": "q*diff(log(eta(tau)), tau) related",
        "notes": "Generating function for sum of divisors"
    },
    {
        "id": "HD-087",
        "equation": "mobius(n) * summation(floor(x/k), (k, 1, n))",
        "domain": "number_theory.mobius_inversion",
        "difficulty": "research",
        "expected": "n for n <= x",
        "notes": "Mobius inversion of floor sum"
    },
    {
        "id": "HD-088",
        "equation": "limit(summation(Lambda(n)/n, (n, 2, x)) - log(x), x, oo)",
        "domain": "number_theory.prime_number_theorem",
        "difficulty": "research",
        "expected": "-gamma - summation(log(p)/(p*(p-1)), (p, primes))",
        "notes": "Mertens constant from von Mangoldt function"
    },

    # =========================================================================
    # SECTION 10: PROBABILITY AND STATISTICAL MECHANICS (HD-089 to HD-095)
    # Advanced probability, random matrices, partition functions
    # =========================================================================
    {
        "id": "HD-089",
        "equation": "integrate(x**s * exp(-x), (x, 0, oo)) / Gamma(s+1)",
        "domain": "probability.gamma",
        "difficulty": "research",
        "expected": "1 (normalization of Gamma distribution)",
        "notes": "Gamma distribution integral with shape parameter s"
    },
    {
        "id": "HD-090",
        "equation": "characteristic_function(Normal(0, 1), t)",
        "domain": "probability.characteristic",
        "difficulty": "research",
        "expected": "exp(-t**2/2)",
        "notes": "Characteristic function of standard normal"
    },
    {
        "id": "HD-091",
        "equation": "E[max(X, Y)] where X, Y ~ Normal(0, 1) independent",
        "domain": "probability.order_statistics",
        "difficulty": "research",
        "expected": "1/sqrt(pi)",
        "notes": "Expected maximum of two standard normals"
    },
    {
        "id": "HD-092",
        "equation": "tracy_widom_distribution_limit(largest_eigenvalue(GUE(n)), n)",
        "domain": "probability.random_matrices",
        "difficulty": "research",
        "expected": "Tracy-Widom distribution F_2",
        "notes": "Limiting distribution of largest eigenvalue in GUE"
    },
    {
        "id": "HD-093",
        "equation": "partition_function(summation(exp(-beta*E_n), (n, 0, oo)))",
        "domain": "statistical_mechanics.partition",
        "difficulty": "research",
        "expected": "1/(1 - exp(-beta*hbar*omega)) for harmonic oscillator",
        "notes": "Quantum harmonic oscillator partition function"
    },
    {
        "id": "HD-094",
        "equation": "ising_partition(2D_square_lattice, T)",
        "domain": "statistical_mechanics.ising",
        "difficulty": "research",
        "expected": "Onsager solution: log(Z) ~ ...",
        "notes": "2D Ising model exact partition function (Onsager)"
    },
    {
        "id": "HD-095",
        "equation": "E[X*Y | X + Y = s] where X, Y ~ Poisson(lambda)",
        "domain": "probability.conditional",
        "difficulty": "research",
        "expected": "s*(s-1)/4 for large s",
        "notes": "Conditional expectation with Poisson variables"
    },

    # =========================================================================
    # SECTION 11: PHYSICS APPLICATIONS (HD-096 to HD-100)
    # Quantum mechanics, field theory, special relativity
    # =========================================================================
    {
        "id": "HD-096",
        "equation": "integrate(exp(-I*p*x/hbar)*psi(x), (x, -oo, oo))",
        "domain": "physics.quantum.fourier",
        "difficulty": "research",
        "expected": "phi(p) * sqrt(2*pi*hbar) (momentum space wavefunction)",
        "notes": "Fourier transform to momentum representation"
    },
    {
        "id": "HD-097",
        "equation": "commutator(x_operator, p_operator)",
        "domain": "physics.quantum.operators",
        "difficulty": "research",
        "expected": "I*hbar",
        "notes": "Canonical commutation relation [x, p] = i*hbar"
    },
    {
        "id": "HD-098",
        "equation": "path_integral(exp(I*S[x]/hbar), x(t))",
        "domain": "physics.quantum.path_integral",
        "difficulty": "research",
        "expected": "propagator K(x_f, t_f; x_i, t_i)",
        "notes": "Feynman path integral formulation of quantum mechanics"
    },
    {
        "id": "HD-099",
        "equation": "lorentz_transform(x, t, v)",
        "domain": "physics.relativity",
        "difficulty": "research",
        "expected": "x' = gamma*(x - v*t), t' = gamma*(t - v*x/c**2)",
        "notes": "Lorentz transformation with gamma = 1/sqrt(1 - v**2/c**2)"
    },
    {
        "id": "HD-100",
        "equation": "integrate(1/(exp(hbar*omega/(k*T)) - 1) * hbar*omega**3 / (pi**2*c**3), (omega, 0, oo))",
        "domain": "physics.statistical.blackbody",
        "difficulty": "research",
        "expected": "pi**2 * k**4 * T**4 / (15 * hbar**3 * c**3)",
        "notes": "Stefan-Boltzmann law from Planck distribution integration"
    },
]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_equations_by_domain(domain_prefix: str) -> list:
    """Filter equations by domain prefix (e.g., 'complex_analysis')."""
    return [eq for eq in HIGH_DIFFICULTY_EQUATIONS
            if eq["domain"].startswith(domain_prefix)]

def get_equations_by_difficulty(difficulty: str = "research") -> list:
    """Filter equations by difficulty level."""
    return [eq for eq in HIGH_DIFFICULTY_EQUATIONS
            if eq["difficulty"] == difficulty]

def get_equation_by_id(eq_id: str) -> dict:
    """Get a specific equation by its ID."""
    for eq in HIGH_DIFFICULTY_EQUATIONS:
        if eq["id"] == eq_id:
            return eq
    return None

def summarize_coverage() -> dict:
    """Summarize domain coverage."""
    domains = {}
    for eq in HIGH_DIFFICULTY_EQUATIONS:
        base_domain = eq["domain"].split(".")[0]
        domains[base_domain] = domains.get(base_domain, 0) + 1
    return domains


# =============================================================================
# DOMAIN CATEGORIES
# =============================================================================

DOMAIN_CATEGORIES = {
    "complex_analysis": {
        "range": "HD-001 to HD-010",
        "count": 10,
        "topics": ["contour integrals", "residues", "Cauchy formulas", "branch cuts"]
    },
    "transforms": {
        "range": "HD-011 to HD-020",
        "count": 10,
        "topics": ["Laplace transform", "Fourier transform", "Mellin transform", "inverse transforms"]
    },
    "orthogonal_polynomials": {
        "range": "HD-021 to HD-030",
        "count": 10,
        "topics": ["Legendre", "Chebyshev T/U", "Laguerre", "Hermite", "Jacobi"]
    },
    "elliptic": {
        "range": "HD-031 to HD-040",
        "count": 10,
        "topics": ["complete elliptic integrals", "incomplete elliptic integrals", "Jacobi functions"]
    },
    "hypergeometric": {
        "range": "HD-041 to HD-050",
        "count": 10,
        "topics": ["Gauss 2F1", "confluent 1F1", "summation theorems", "transformations"]
    },
    "pde": {
        "range": "HD-051 to HD-060",
        "count": 10,
        "topics": ["heat equation", "wave equation", "Laplace", "Schrodinger", "Green's functions"]
    },
    "calculus": {
        "range": "HD-061 to HD-070",
        "count": 10,
        "topics": ["exotic limits", "zeta values", "asymptotic series", "special constants"]
    },
    "linear_algebra": {
        "range": "HD-071 to HD-080",
        "count": 10,
        "topics": ["matrix exponential", "spectral theory", "Sylvester equation", "permanents"]
    },
    "number_theory": {
        "range": "HD-081 to HD-088",
        "count": 8,
        "topics": ["continued fractions", "modular forms", "theta functions", "Mobius inversion"]
    },
    "probability": {
        "range": "HD-089 to HD-095",
        "count": 7,
        "topics": ["characteristic functions", "random matrices", "partition functions", "Ising model"]
    },
    "physics": {
        "range": "HD-096 to HD-100",
        "count": 5,
        "topics": ["quantum mechanics", "path integrals", "Lorentz transform", "blackbody radiation"]
    },
}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("100 HIGH-DIFFICULTY RESEARCH-LEVEL EQUATIONS")
    print("=" * 70)
    print(f"\nTotal equations: {len(HIGH_DIFFICULTY_EQUATIONS)}")
    print("\nDomain coverage:")
    print("-" * 40)

    coverage = summarize_coverage()
    for domain, count in sorted(coverage.items(), key=lambda x: -x[1]):
        print(f"  {domain:25s}: {count:3d} equations")

    print("\n" + "-" * 40)
    print("Detailed categories:")
    for cat_name, cat_info in DOMAIN_CATEGORIES.items():
        print(f"\n  [{cat_name.upper()}] ({cat_info['count']} equations: {cat_info['range']})")
        print(f"    Topics: {', '.join(cat_info['topics'])}")

    print("\n" + "=" * 70)
    print("Equations ready for testing with native solver engine.")
    print("=" * 70)
