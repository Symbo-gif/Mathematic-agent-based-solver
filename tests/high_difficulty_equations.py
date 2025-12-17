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
High-Difficulty Equations - 100 Advanced Problems Spanning All Domains
=======================================================================

These equations are significantly harder than standard textbook problems,
drawn from competition mathematics, advanced analysis, and research areas.
Each problem is solvable but requires sophisticated techniques.
"""

# =============================================================================
# ADVANCED CALCULUS (20 equations)
# =============================================================================

ADVANCED_CALCULUS = [
    # Complex contour-inspired real integrals
    "integrate(log(x)**2 / (1 + x**2), (x, 0, oo))",  # pi^3/8
    "integrate(x**a / (1 + x)**2, (x, 0, oo))",  # pi*a/sin(pi*a) for 0<a<1
    "integrate(log(1 + x**2) / x**2, (x, 0, oo))",  # pi
    "integrate(arctan(x) / x, (x, 0, 1))",  # Catalan's constant G
    "integrate(x / (exp(x) - 1), (x, 0, oo))",  # pi^2/6

    # Parametric and multivariate integrals
    "integrate(log(a**2 + x**2), (x, 0, 1))",  # parametric
    "integrate(exp(-x**2 - y**2) * x**2, (x, -oo, oo), (y, -oo, oo))",  # pi/2
    "integrate(1 / sqrt((x - a)*(b - x)), (x, a, b))",  # pi
    "integrate(sin(x**2) * cos(x**2), (x, 0, oo))",  # sqrt(pi/8)/2
    "integrate(1 / (1 + x**4)**2, (x, -oo, oo))",  # 3*pi/(8*sqrt(2))

    # Limits requiring advanced techniques
    "limit((1 + 1/n + 1/n**2)**n, n, oo)",  # e
    "limit(n * (n*sin(1/n) - 1), n, oo)",  # -1/6
    "limit((n!)**(1/n) / n, n, oo)",  # 1/e
    "limit(sum(1/k**2, (k, n, 2*n)), n, oo)",  # 0
    "limit(product(1 + 1/k**2, (k, 1, n))**(1/n), n, oo)",  # 1

    # Sophisticated derivatives
    "diff(integral(exp(-t**2), (t, 0, x)), x)",  # exp(-x^2)
    "diff(x**x**x, x)",  # triple tower
    "diff(arctan(tan(x)/sqrt(2)), x)",  # requires care at discontinuities
    "diff(log(gamma(x)), x)",  # digamma function psi(x)
    "diff(sum(x**n/n, (n, 1, oo)), x)",  # -1/(1-x) for |x|<1
]

# =============================================================================
# ADVANCED SERIES AND PRODUCTS (20 equations)
# =============================================================================

ADVANCED_SERIES = [
    # Euler sums and polylogarithms
    "summation(H_n / n**2, (n, 1, oo))",  # 2*zeta(3)
    "summation(H_n / n**3, (n, 1, oo))",  # pi^4/72
    "summation((-1)**(n+1) * H_n / n, (n, 1, oo))",  # pi^2/12 - log(2)^2/2
    "summation(1 / (n**2 * binomial(2*n, n)), (n, 1, oo))",  # pi^2/18
    "summation(zeta(2*n) / 2**(2*n), (n, 1, oo))",  # log(2) - 1/2

    # Products and infinite series
    "product(1 - 1/(4*n**2), (n, 1, oo))",  # 2/pi (Wallis)
    "product((n**2 + 1)/(n**2), (n, 1, oo))",  # sinh(pi)/pi
    "product(1 + (-1)**(n+1)/(2*n-1), (n, 1, oo))",  # sqrt(2)
    "summation(sin(n) / n, (n, 1, oo))",  # (pi - 1)/2
    "summation(cos(n) / n**2, (n, 1, oo))",  # pi^2/6 - pi/2 + 1/4

    # Alternating and conditional convergence
    "summation((-1)**n * log(n) / n, (n, 2, oo))",  # gamma*log(2) - log(2)^2/2
    "summation((-1)**(n+1) / (n * (n+1)), (n, 1, oo))",  # 2*log(2) - 1
    "summation(sin(n*x) / n, (n, 1, oo))",  # (pi - x)/2 for 0<x<2*pi
    "summation(cos(n*x) / n**2, (n, 1, oo))",  # x^2/4 - pi*x/2 + pi^2/6
    "summation(1 / (n * (n+1) * (n+2)), (n, 1, oo))",  # 1/4

    # Double sums and nested series
    "summation(summation(1/(m**2 + n**2), (n, 1, oo)), (m, 1, oo))",  # lattice sum
    "summation(1 / (n * 3**n), (n, 1, oo))",  # log(3/2)
    "summation(n**2 / 3**n, (n, 1, oo))",  # 3/2
    "summation(fib(n) / 2**n, (n, 1, oo))",  # 2
    "summation(fib(n) / 10**n, (n, 1, oo))",  # 10/89
]

# =============================================================================
# ADVANCED DIFFERENTIAL EQUATIONS (15 equations)
# =============================================================================

ADVANCED_ODE = [
    # Bessel, Legendre, and special function ODEs
    "dsolve(x**2*diff(y(x), x, 2) + x*diff(y(x), x) + (x**2 - n**2)*y(x), y(x))",  # Bessel
    "dsolve((1-x**2)*diff(y(x), x, 2) - 2*x*diff(y(x), x) + n*(n+1)*y(x), y(x))",  # Legendre
    "dsolve(x*diff(y(x), x, 2) + (c-x)*diff(y(x), x) - a*y(x), y(x))",  # Confluent hypergeometric
    "dsolve(diff(y(x), x, 2) + (2*n+1-x**2)*y(x), y(x))",  # Hermite oscillator
    "dsolve(diff(y(x), x, 2) - 6*y(x)**2 - x, y(x))",  # Painleve I

    # Nonlinear first-order ODEs
    "dsolve(diff(y(x), x) - y(x)**2 - x, y(x))",  # Riccati
    "dsolve(diff(y(x), x) - sqrt(x**2 + y(x)**2)/x, y(x))",  # homogeneous
    "dsolve(y(x)*diff(y(x), x) + x - sqrt(x**2 + y(x)**2), y(x))",  # reducible
    "dsolve((2*x*y(x) + 3)*diff(y(x), x) + y(x)**2 + 2, y(x))",  # exact check
    "dsolve(diff(y(x), x) + y(x)*tan(x) - y(x)**3*sec(x), y(x))",  # Bernoulli

    # Systems and higher-order
    "dsolve([diff(x(t), t) - y(t), diff(y(t), t) + x(t)], [x(t), y(t)])",  # oscillator
    "dsolve([diff(x(t), t) - x(t) - y(t), diff(y(t), t) + x(t) - y(t)], [x(t), y(t)])",  # spiral
    "dsolve(diff(y(x), x, 3) - 3*diff(y(x), x, 2) + 3*diff(y(x), x) - y(x), y(x))",  # triple root
    "dsolve(diff(y(x), x, 4) + 2*diff(y(x), x, 2) + y(x) - cos(x), y(x))",  # resonance
    "dsolve(x**3*diff(y(x), x, 3) + x**2*diff(y(x), x, 2) - 2*x*diff(y(x), x) + 2*y(x), y(x))",  # Euler
]

# =============================================================================
# ADVANCED LINEAR ALGEBRA (15 equations)
# =============================================================================

ADVANCED_LINEAR_ALGEBRA = [
    # Advanced matrix functions
    "exp(Matrix([[0, 1], [-1, 0]]))",  # rotation matrix exponential
    "log(Matrix([[1, 1], [0, 1]]))",  # matrix logarithm
    "Matrix([[1, 1], [1, 0]])**n",  # Fibonacci matrix
    "sqrt(Matrix([[4, 2], [2, 1]]))",  # matrix square root
    "sin(Matrix([[0, pi/2], [0, 0]]))",  # matrix sine

    # Spectral decomposition and SVD
    "singular_values(Matrix([[1, 2, 3], [4, 5, 6]]))",  # SVD
    "Matrix([[a, b], [b, c]]).diagonalize()",  # symmetric diagonalization
    "Matrix([[1, 2, 0], [2, 1, 2], [0, 2, 1]]).jordan_form()",  # Jordan blocks
    "pseudoinverse(Matrix([[1, 2], [3, 6]]))",  # Moore-Penrose
    "Matrix([[1, 2], [3, 4]]).exp()",  # matrix exponential

    # Advanced decompositions
    "schur_decomposition(Matrix([[0, 1, 0], [0, 0, 1], [1, 0, 0]]))",  # cyclic
    "polar_decomposition(Matrix([[1, 2], [3, 4]]))",  # A = UP
    "Matrix([[a, 0, b], [0, c, 0], [d, 0, e]]).permanent()",  # permanent
    "hadamard_product(Matrix([[1, 2], [3, 4]]), Matrix([[5, 6], [7, 8]]))",  # elementwise
    "kronecker_product(Matrix([[1, 0], [0, 1]]), Matrix([[a, b], [c, d]]))",  # tensor
]

# =============================================================================
# ADVANCED NUMBER THEORY (15 equations)
# =============================================================================

ADVANCED_NUMBER_THEORY = [
    # Analytic number theory
    "sum(mobius(d) * floor(n/d), (d, 1, n))",  # = 1
    "sum(euler_phi(d), (d | n))",  # = n (Gauss)
    "sum((-1)**(omega(n)), (n, 1, N))",  # Mertens function
    "product(1 - 1/p, (p, primes <= n))",  # ~ 1/(e^gamma * log(n))
    "sum(Lambda(n), (n, 1, x))",  # ~ x (prime number theorem)

    # Quadratic forms and residues
    "sum(legendre_symbol(n, p), (n, 1, p-1))",  # = 0
    "quadratic_residues(17)",  # quadratic residues mod 17
    "primitive_root(23)",  # generator of (Z/23Z)*
    "order(2, 17)",  # multiplicative order of 2 mod 17
    "continued_fraction(sqrt(7))",  # periodic CF

    # Partition and Ramanujan
    "partition(100)",  # p(100)
    "sum((-1)**k * partition(n - k*(3*k-1)/2), (k, -oo, oo))",  # Euler pentagonal
    "ramanujan_tau(12)",  # Ramanujan tau function
    "sum(sigma(k) * sigma(n-k), (k, 1, n-1))",  # convolution
    "modular_j(exp(2*pi*I/3))",  # j-invariant at cube root of unity
]

# =============================================================================
# ADVANCED PROBABILITY AND STATISTICS (15 equations)
# =============================================================================

ADVANCED_PROBABILITY = [
    # Characteristic functions and transforms
    "integrate(exp(I*t*x) * exp(-x**2/2)/sqrt(2*pi), (x, -oo, oo))",  # CF of N(0,1)
    "integrate(exp(I*t*x) * exp(-abs(x)), (x, -oo, oo))",  # CF of Laplace
    "laplace_transform(t**n * exp(-a*t), t, s)",  # n!/((s+a)^(n+1))
    "inverse_laplace_transform(1/(s**2 + a**2), s, t)",  # sin(a*t)/a
    "fourier_transform(exp(-a*abs(x)), x, k)",  # 2a/(a^2 + k^2)

    # Advanced distributions
    "integrate(x * (1-x) * x**(a-1) * (1-x)**(b-1) / Beta(a,b), (x, 0, 1))",  # E[X(1-X)] Beta
    "integrate(log(x) * x**(a-1) * exp(-x) / Gamma(a), (x, 0, oo))",  # E[log(X)] Gamma
    "kurtosis(chi_squared(k))",  # 12/k
    "mgf(poisson(lambda), t)",  # exp(lambda*(exp(t)-1))
    "cdf(normal(mu, sigma), x)",  # (1 + erf((x-mu)/(sigma*sqrt(2))))/2

    # Order statistics and extreme values
    "E[max(X_1, ..., X_n)]",  # for uniform(0,1): n/(n+1)
    "Var[X_(k)]",  # variance of k-th order statistic
    "limit(P(max(X_1,...,X_n) - log(n) <= x), n, oo)",  # Gumbel
    "integrate(n * x**(n-1) * (1 - x), (x, 0, 1))",  # E[1 - max] for uniform
    "correlation(X_(1), X_(n))",  # correlation of min and max
]

# =============================================================================
# COMBINE ALL HIGH-DIFFICULTY EQUATIONS
# =============================================================================

ALL_HIGH_DIFFICULTY = (
    ADVANCED_CALCULUS +           # 20
    ADVANCED_SERIES +             # 20
    ADVANCED_ODE +                # 15
    ADVANCED_LINEAR_ALGEBRA +     # 15
    ADVANCED_NUMBER_THEORY +      # 15
    ADVANCED_PROBABILITY          # 15
)  # Total: 100 equations

# Category mapping
CATEGORIES = {
    "advanced_calculus": ADVANCED_CALCULUS,
    "advanced_series": ADVANCED_SERIES,
    "advanced_ode": ADVANCED_ODE,
    "advanced_linear_algebra": ADVANCED_LINEAR_ALGEBRA,
    "advanced_number_theory": ADVANCED_NUMBER_THEORY,
    "advanced_probability": ADVANCED_PROBABILITY,
}

def get_equations_by_category(category: str):
    """Get equations for a specific category."""
    return CATEGORIES.get(category, [])

def get_all_equations():
    """Get all high-difficulty equations."""
    return ALL_HIGH_DIFFICULTY
