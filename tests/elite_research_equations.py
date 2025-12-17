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
Elite Research-Grade Equations - 50 Competition and Research-Level Problems
=============================================================================

These equations represent the pinnacle of mathematical challenge:
- Putnam competition problems
- MIT Integration Bee finals
- IMO/IMC level problems
- Active research area problems
- Known difficult integrals from literature

Each problem requires deep insight, creative techniques, or novel approaches.
Many have only been solved in published papers or by elite mathematicians.
"""

# =============================================================================
# PUTNAM AND COMPETITION INTEGRALS (12 equations)
# =============================================================================

COMPETITION_INTEGRALS = [
    # Classic competition integrals
    "integrate(log(1 + x) * log(1 - x) / x, (x, 0, 1))",  # -pi^2/4 + 2*log(2)
    "integrate(arctan(x) * arctan(1/x) / x, (x, 0, 1))",  # 7*zeta(3)/8
    "integrate(log(x) * log(1 + x) * log(1 - x), (x, 0, 1))",  # complex polylog
    "integrate((log(x))^4 / (1 + x)^2, (x, 0, oo))",  # 7*pi^5/15
    "integrate(x^a * (1 - x)^b * log(x)^n, (x, 0, 1))",  # Beta function derivative

    # MIT Integration Bee style
    "integrate(sqrt(tan(x)), (x, 0, pi/2))",  # sqrt(2)*pi/2
    "integrate(sin(x)^sin(x), (x, 0, pi/2))",  # no closed form
    "integrate(log(tan(x)), (x, 0, pi/4))",  # -G (Catalan's constant)
    "integrate(x / sin(x), (x, 0, pi/2))",  # 2*G
    "integrate(sin(x)^4 * cos(x)^4, (x, 0, pi/2))",  # 3*pi/256

    # Improper integral challenges
    "integrate(sin(x^2) * cos(x^2), (x, 0, oo))",  # sqrt(pi/8)/2
    "integrate(exp(-x^4), (x, 0, oo))",  # Gamma(5/4)/4
]

# =============================================================================
# ANALYTIC NUMBER THEORY (10 equations)
# =============================================================================

ANALYTIC_NUMBER_THEORY = [
    # Riemann zeta and L-functions
    "zeta(3)",  # Apery's constant, irrational
    "sum((-1)^(n+1) / n^3, (n, 1, oo))",  # 3*zeta(3)/4
    "zeta(1/2 + 14.134725*I)",  # first non-trivial zero
    "L(1, chi_4)",  # Dirichlet L-function, = pi/4
    "sum(mu(n) / n, (n, 1, oo))",  # = 0 (prime number theorem)

    # Prime distribution
    "li(x) - pi(x)",  # logarithmic integral vs prime counting
    "sum(1/p, (p, primes <= x))",  # ~ log(log(x))
    "product(1 / (1 - 1/p^s), (p, primes))",  # = zeta(s)
    "sum(Lambda(n) / n^s, (n, 1, oo))",  # = -zeta'(s)/zeta(s)
    "sum(phi(n) / n^s, (n, 1, oo))",  # = zeta(s-1)/zeta(s)
]

# =============================================================================
# SPECIAL FUNCTIONS AND TRANSFORMS (10 equations)
# =============================================================================

SPECIAL_FUNCTIONS = [
    # Hypergeometric and confluent
    "2F1(1/2, 1/2; 1; 1/2)",  # = 4*K(1/sqrt(2))/pi^2
    "2F1(a, b; c; 1)",  # Gauss evaluation for c > a + b
    "1F1(a; c; x)",  # Kummer confluent hypergeometric
    "pFq([1, 1], [2], -1)",  # = log(2)
    "MeijerG([[a], [b]], [[c], [d]], x)",  # Meijer G-function

    # Elliptic integrals
    "K(k)",  # complete elliptic integral first kind
    "E(k)",  # complete elliptic integral second kind
    "F(phi, k)",  # incomplete elliptic integral first kind
    "Pi(n, k)",  # complete elliptic integral third kind
    "agm(1, sqrt(2))",  # arithmetic-geometric mean = pi/(2*K(1/sqrt(2)))
]

# =============================================================================
# ADVANCED DIFFERENTIAL EQUATIONS (8 equations)
# =============================================================================

ADVANCED_DE = [
    # Painleve transcendents
    "dsolve(diff(y, x, 2) - 6*y^2 - x, y(x))",  # Painleve I
    "dsolve(diff(y, x, 2) - 2*y^3 - x*y - alpha, y(x))",  # Painleve II
    "dsolve(x*diff(y, x, 2) - diff(y, x) + x*y^3, y(x))",  # Painleve III (special)
    "dsolve(2*y*diff(y, x, 2) - diff(y, x)^2 + 3*y^4, y(x))",  # Painleve IV related

    # Nonlinear wave equations
    "u_t + u*u_x + u_xxx = 0",  # KdV soliton
    "u_t + 6*u^2*u_x + u_xxx = 0",  # mKdV equation
    "i*psi_t + psi_xx + 2*|psi|^2*psi = 0",  # nonlinear Schrodinger
    "u_tt - u_xx + sin(u) = 0",  # sine-Gordon equation
]

# =============================================================================
# ADVANCED COMBINATORICS AND ASYMPTOTICS (10 equations)
# =============================================================================

COMBINATORICS_ASYMPTOTICS = [
    # Asymptotic expansions
    "asymptotic(n!, n, oo)",  # Stirling: sqrt(2*pi*n)*(n/e)^n
    "asymptotic(partition(n), n, oo)",  # Hardy-Ramanujan: exp(pi*sqrt(2n/3))/(4n*sqrt(3))
    "asymptotic(binomial(2n, n), n, oo)",  # 4^n / sqrt(pi*n)
    "asymptotic(catalan(n), n, oo)",  # 4^n / (sqrt(pi)*n^(3/2))
    "asymptotic(fibonacci(n), n, oo)",  # phi^n / sqrt(5)

    # Advanced generating functions
    "sum(fibonacci(n)^2 * x^n, (n, 0, oo))",  # (1 - x) / (1 - 3x + x^2)
    "sum(catalan(n) * x^n, (n, 0, oo))",  # (1 - sqrt(1 - 4x)) / (2x)
    "sum(partition(n) * q^n, (n, 0, oo))",  # prod(1/(1-q^k), k=1 to oo)
    "sum(bell(n) * x^n / n!, (n, 0, oo))",  # exp(exp(x) - 1)
    "sum(derangements(n) * x^n / n!, (n, 0, oo))",  # exp(-x) / (1 - x)
]

# =============================================================================
# COMBINE ALL ELITE EQUATIONS
# =============================================================================

ALL_ELITE_EQUATIONS = (
    COMPETITION_INTEGRALS +        # 12
    ANALYTIC_NUMBER_THEORY +       # 10
    SPECIAL_FUNCTIONS +            # 10
    ADVANCED_DE +                  # 8
    COMBINATORICS_ASYMPTOTICS      # 10
)  # Total: 50 equations

# Category mapping
CATEGORIES = {
    "competition_integrals": COMPETITION_INTEGRALS,
    "analytic_number_theory": ANALYTIC_NUMBER_THEORY,
    "special_functions": SPECIAL_FUNCTIONS,
    "advanced_de": ADVANCED_DE,
    "combinatorics_asymptotics": COMBINATORICS_ASYMPTOTICS,
}

# Research references for each category
RESEARCH_REFS = {
    "competition_integrals": [
        "Putnam Mathematical Competition",
        "MIT Integration Bee",
        "Table of Integrals, Gradshteyn & Ryzhik",
    ],
    "analytic_number_theory": [
        "Apostol - Introduction to Analytic Number Theory",
        "Edwards - Riemann's Zeta Function",
        "Iwaniec & Kowalski - Analytic Number Theory",
    ],
    "special_functions": [
        "NIST Digital Library of Mathematical Functions",
        "Abramowitz & Stegun - Handbook of Mathematical Functions",
        "Olver - Asymptotics and Special Functions",
    ],
    "advanced_de": [
        "Clarkson - Painleve Equations",
        "Ablowitz & Segur - Solitons and the Inverse Scattering Transform",
        "Ince - Ordinary Differential Equations",
    ],
    "combinatorics_asymptotics": [
        "Flajolet & Sedgewick - Analytic Combinatorics",
        "Hardy & Ramanujan - Asymptotic Formulae in Combinatory Analysis",
        "Wilf - generatingfunctionology",
    ],
}

def get_equations_by_category(category: str):
    """Get equations for a specific category."""
    return CATEGORIES.get(category, [])

def get_all_equations():
    """Get all elite research-grade equations."""
    return ALL_ELITE_EQUATIONS

def get_references_for_category(category: str):
    """Get research references for a category."""
    return RESEARCH_REFS.get(category, [])

def count_by_category():
    """Get equation count by category."""
    return {cat: len(eqs) for cat, eqs in CATEGORIES.items()}
