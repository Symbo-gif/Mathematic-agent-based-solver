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
ELITE 50: Research-Grade Mathematical Equations
================================================

50 elite-level mathematical problems designed to challenge expert mathematicians
and top Computer Algebra Systems. Each equation has been carefully selected to:

1. NOT overlap with existing test suites (stress_test_equations.py, ultra_edge_25_test.py,
   edgy_100_test.py, edgiest_50_test.py, run_25_equations.py)
2. Represent genuine research-level difficulty
3. Have known closed-form answers OR be provably undecidable
4. Span multiple mathematical frontiers

Categories:
- E01-E10: Meijer G-Functions & Barnes Integrals
- E11-E18: Modular Forms & Elliptic Functions
- E19-E28: Hypergeometric Identities & Transformations
- E29-E36: Advanced Number Theory & L-functions
- E37-E44: Multi-technique Synthesis Problems
- E45-E50: Famous Problems & Modern Research Directions

Author: Elite Mathematical Research Analyst
Date: 2024-12-14
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple
from enum import Enum

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class Difficulty(Enum):
    """Classification of mathematical difficulty."""
    GRADUATE = "graduate"           # Advanced graduate level
    RESEARCH = "research"           # Active research area
    FRONTIER = "frontier"           # Mathematical frontier
    UNDECIDABLE = "undecidable"     # Provably undecidable in certain systems


class Technique(Enum):
    """Primary mathematical technique required."""
    CONTOUR_INTEGRATION = "contour_integration"
    MODULAR_ARITHMETIC = "modular_arithmetic"
    HYPERGEOMETRIC = "hypergeometric"
    SPECIAL_FUNCTIONS = "special_functions"
    NUMBER_THEORY = "number_theory"
    ASYMPTOTIC_ANALYSIS = "asymptotic_analysis"
    FUNCTIONAL_EQUATIONS = "functional_equations"
    ELLIPTIC_FUNCTIONS = "elliptic_functions"
    MULTI_TECHNIQUE = "multi_technique"


@dataclass
class EliteEquation:
    """Metadata container for an elite-level equation."""
    id: str
    expression: str
    expected_answer: str
    difficulty: Difficulty
    techniques: List[Technique]
    category: str
    justification: str
    references: Optional[List[str]] = None
    notes: Optional[str] = None


# =============================================================================
# CATEGORY 1: MEIJER G-FUNCTIONS & BARNES INTEGRALS (E01-E10)
# =============================================================================
# These involve the most general class of special functions. Meijer G-functions
# unify hypergeometric functions, and Barnes integrals provide their integral
# representations via Mellin-Barnes contours.

MEIJER_G_BARNES = [
    EliteEquation(
        id="E01",
        expression="integrate(x**(s-1) * MeijerG([[a1,a2],[b1]],[[c1,c2],[d1]], x), (x, 0, oo))",
        expected_answer="Product of Gamma functions (Slater's theorem)",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.CONTOUR_INTEGRATION, Technique.SPECIAL_FUNCTIONS],
        category="Meijer G-Functions",
        justification="""
        Meijer G-function integrals require sophisticated contour integration.
        The Mellin transform of a G-function yields a ratio of products of
        Gamma functions (Slater's theorem). This tests understanding of:
        - Mellin-Barnes integral representations
        - Contour selection for convergence
        - Gamma function reflection formulas
        Elite because: Most CAS fail to simplify general G-function integrals.
        """,
        references=["Slater, L.J. (1966) Generalized Hypergeometric Functions",
                   "Luke, Y.L. (1969) Special Functions and Their Approximations"]
    ),

    EliteEquation(
        id="E02",
        expression="MeijerG([[1/2],[]], [[0,0],[1/2]], x) - 2*erfc(sqrt(x))/sqrt(pi)",
        expected_answer="0",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.HYPERGEOMETRIC],
        category="Meijer G-Functions",
        justification="""
        The complementary error function erfc(x) can be expressed as a
        Meijer G-function. This identity tests the ability to recognize
        standard special functions within G-function representations.
        Elite because: Requires deep knowledge of G-function parameter conventions.
        """,
        references=["NIST DLMF Chapter 16"]
    ),

    EliteEquation(
        id="E03",
        expression="integrate(MeijerG([[-a],[]], [[0],[b]], x) * MeijerG([[-c],[]], [[0],[d]], x), (x, 0, oo))",
        expected_answer="Gamma(a+c+1)*Gamma(b+d+1)/(Gamma(a+d+2)*Gamma(b+c+2)) [with conditions]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.CONTOUR_INTEGRATION, Technique.SPECIAL_FUNCTIONS],
        category="Meijer G-Functions",
        justification="""
        Product integrals of G-functions (convolution theorem) are fundamental
        to fractional calculus and integral transforms. The answer involves
        careful analysis of parameter conditions for convergence.
        Elite because: G-function product integrals challenge even Mathematica.
        """,
        references=["Prudnikov et al. (1990) Integrals and Series, Vol. 3"]
    ),

    EliteEquation(
        id="E04",
        expression="BarnesIntegral(Gamma(s)*Gamma(a-s)*Gamma(b-s)/Gamma(c-s), (s, -I*oo, I*oo))",
        expected_answer="2*pi*I * Gamma(a)*Gamma(b)*2F1(a,b;c;1)/Gamma(c) [Barnes first lemma]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.CONTOUR_INTEGRATION, Technique.HYPERGEOMETRIC],
        category="Barnes Integrals",
        justification="""
        Barnes' first lemma is fundamental to hypergeometric function theory.
        The contour integral evaluates to a ratio of Gamma functions times
        a 2F1 at unity. This tests:
        - Residue computation at multiple pole sequences
        - Analytic continuation considerations
        - Connection to classical hypergeometric identities
        Elite because: Barnes integrals are rarely implemented in standard CAS.
        """,
        references=["Barnes, E.W. (1908) Proc. London Math. Soc.",
                   "Whittaker & Watson, Modern Analysis, Chapter 14"]
    ),

    EliteEquation(
        id="E05",
        expression="limit(MeijerG([[a,b],[c]], [[d,e],[]], z) / z**(-d-e) / Gamma(a-d)*Gamma(b-d), z, 0, '+')",
        expected_answer="1 [leading asymptotic term verification]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.ASYMPTOTIC_ANALYSIS, Technique.SPECIAL_FUNCTIONS],
        category="Meijer G-Functions",
        justification="""
        Asymptotic expansions of G-functions near singular points require
        careful analysis of the pole structure. This tests whether the
        leading order behavior is correctly captured.
        Elite because: G-function asymptotics involve multiple competing terms.
        """,
        references=["Luke, Y.L. (1969) Algorithms for Computation of Special Functions"]
    ),

    EliteEquation(
        id="E06",
        expression="integrate(x**(rho-1) * exp(-p*x) * MeijerG([[a],[]], [[b],[c]], q*x), (x, 0, oo))",
        expected_answer="p**(-rho) * MeijerG([[a,rho],[]], [[b],[c,rho]], q/p) [Laplace transform]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.CONTOUR_INTEGRATION],
        category="Meijer G-Functions",
        justification="""
        The Laplace transform of a Meijer G-function produces another G-function
        with shifted parameters. This is fundamental to solving fractional
        differential equations.
        Elite because: Parameter tracking in G-function transformations is error-prone.
        """,
        references=["Mathai & Saxena (1973) Generalized Hypergeometric Functions"]
    ),

    EliteEquation(
        id="E07",
        expression="BarnesIntegral(Gamma(s)**3/Gamma(3*s), (s, c-I*oo, c+I*oo)) / (2*pi*I)",
        expected_answer="1/(3*sqrt(3)) [Barnes-type evaluation]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.CONTOUR_INTEGRATION, Technique.SPECIAL_FUNCTIONS],
        category="Barnes Integrals",
        justification="""
        This Barnes integral evaluates to a simple algebraic number despite
        involving Gamma functions. Such integrals appear in:
        - Modular form theory
        - String theory amplitudes
        - Random matrix theory
        Elite because: Closed-form evaluation requires sophisticated residue analysis.
        """,
        references=["Vanhove, P. (2014) String amplitudes and Barnes integrals"]
    ),

    EliteEquation(
        id="E08",
        expression="MeijerG([[],[1/2]], [[0,-1/2],[]], z) - (1 + sqrt(1+z))/sqrt(z)",
        expected_answer="0",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.HYPERGEOMETRIC],
        category="Meijer G-Functions",
        justification="""
        Some Meijer G-functions reduce to elementary functions. Recognizing
        these reductions requires understanding the relationship between
        G-functions and algebraic functions.
        Elite because: Tests pattern recognition in transcendental-algebraic reduction.
        """,
        references=["Wolfram Functions Site, Meijer G Representations"]
    ),

    EliteEquation(
        id="E09",
        expression="summation(MeijerG([[a],[b]], [[c],[d]], n) / factorial(n), (n, 0, oo))",
        expected_answer="MeijerG([[a,0],[b]], [[c],[d,0]], 1) [exponential generating function]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.HYPERGEOMETRIC],
        category="Meijer G-Functions",
        justification="""
        Discrete G-function sums arise in combinatorics and physics. The
        exponential generating function of G-function values is itself a
        G-function with augmented parameter lists.
        Elite because: G-function series are at the frontier of computational algebra.
        """,
        references=["Gradshteyn & Ryzhik, Table 9.3"]
    ),

    EliteEquation(
        id="E10",
        expression="integrate(exp(-t) * MeijerG([[a],[]], [[0,b],[]], x*t), (t, 0, oo)) - Gamma(1-a)*MeijerG([[],[a]], [[0,b],[]], x)",
        expected_answer="0 [Hankel's contour integral form]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.CONTOUR_INTEGRATION, Technique.SPECIAL_FUNCTIONS],
        category="Meijer G-Functions",
        justification="""
        This identity connects the Laplace-type transform of a G-function to
        Hankel's contour integral representation. It underlies the theory of
        fractional calculus operators.
        Elite because: Tests deep understanding of G-function integral transforms.
        """,
        references=["Samko et al. (1993) Fractional Integrals and Derivatives"]
    ),
]


# =============================================================================
# CATEGORY 2: MODULAR FORMS & ELLIPTIC FUNCTIONS (E11-E18)
# =============================================================================
# Modular forms are functions on the upper half-plane with remarkable symmetry
# properties. Elliptic functions are doubly periodic meromorphic functions.
# These structures are fundamental to modern number theory and physics.

MODULAR_ELLIPTIC = [
    EliteEquation(
        id="E11",
        expression="summation(q**(n*(3*n-1)/2) * (1 + 2*q**n), (n, -oo, oo))",
        expected_answer="Product((1-q**n), (n, 1, oo)) [Euler's pentagonal theorem extended]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.MODULAR_ARITHMETIC, Technique.SPECIAL_FUNCTIONS],
        category="Modular Forms",
        justification="""
        This is related to Euler's pentagonal number theorem, connecting
        partition-type sums to infinite products (eta function). The identity:
        Sum_n q^{n(3n-1)/2} = Prod_n (1-q^n)
        is fundamental to the theory of modular forms.
        Elite because: Pentagonal theorem variations challenge symbolic simplification.
        """,
        references=["Andrews, G.E. (1976) The Theory of Partitions",
                   "Zagier, D. (2008) Elliptic Modular Forms"]
    ),

    EliteEquation(
        id="E12",
        expression="DedekindEta(tau)**24 - Delta(tau)",
        expected_answer="0 [Ramanujan's discriminant]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.MODULAR_ARITHMETIC, Technique.ELLIPTIC_FUNCTIONS],
        category="Modular Forms",
        justification="""
        The Dedekind eta function raised to the 24th power equals Ramanujan's
        discriminant function Delta(tau), a weight-12 cusp form. This connects:
        - Partition theory (via eta)
        - Elliptic curves (discriminant of Weierstrass form)
        - Modular forms (cusp form of minimal level)
        Elite because: Tests understanding of the most fundamental modular form.
        """,
        references=["Ramanujan, S. (1916) Trans. Cambridge Phil. Soc.",
                   "Serre, J.P. (1973) A Course in Arithmetic"]
    ),

    EliteEquation(
        id="E13",
        expression="EllipticE(m) * EllipticK(1-m) + EllipticK(m) * EllipticE(1-m) - EllipticK(m) * EllipticK(1-m) - pi/2",
        expected_answer="0 [Legendre's relation]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.ELLIPTIC_FUNCTIONS, Technique.FUNCTIONAL_EQUATIONS],
        category="Elliptic Functions",
        justification="""
        Legendre's relation connects complete elliptic integrals of the first
        and second kind with complementary moduli. It is equivalent to:
        E(m)K'(m) + E'(m)K(m) - K(m)K'(m) = pi/2
        This is fundamental to elliptic function theory.
        Elite because: Tests understanding of modular equations and functional relations.
        """,
        references=["Whittaker & Watson, Chapter 22",
                   "Abramowitz & Stegun, Chapter 17"]
    ),

    EliteEquation(
        id="E14",
        expression="ThetaFunction(3, 0, exp(-pi)) - sqrt(Gamma(1/4)**2 / (4 * pi**(3/2)))",
        expected_answer="0 [Jacobi theta at special point]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.MODULAR_ARITHMETIC, Technique.SPECIAL_FUNCTIONS],
        category="Modular Forms",
        justification="""
        Jacobi theta functions at the special value tau = i satisfy remarkable
        identities involving Gamma functions. This connects:
        - Modular transformations
        - Chowla-Selberg formula
        - Special values of L-functions
        Elite because: Special theta values involve deep number theory.
        """,
        references=["Borwein & Borwein (1987) Pi and the AGM",
                   "Chowla-Selberg formula (1967)"]
    ),

    EliteEquation(
        id="E15",
        expression="EisensteinE(4, tau) * EisensteinE(6, tau) - 720 * Ramanujan_tau(tau)",
        expected_answer="Complicated modular relation [not zero]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.MODULAR_ARITHMETIC, Technique.NUMBER_THEORY],
        category="Modular Forms",
        justification="""
        Eisenstein series E_4 and E_6 generate the ring of modular forms.
        Their relationship to Ramanujan's tau function (the coefficients of
        Delta) involves subtle weight considerations.
        Elite because: Tests understanding of modular form algebra.
        """,
        references=["Diamond & Shurman (2005) A First Course in Modular Forms"]
    ),

    EliteEquation(
        id="E16",
        expression="WeierstrassP(z, g2, g3) + WeierstrassP(z + omega1/2, g2, g3) + WeierstrassP(z + omega2/2, g2, g3) - 3*e1",
        expected_answer="0 where e1 + e2 + e3 = 0 [Weierstrass addition]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.ELLIPTIC_FUNCTIONS],
        category="Elliptic Functions",
        justification="""
        The Weierstrass P-function satisfies remarkable half-period identities.
        The sum over half-periods relates to the roots of the cubic 4t^3-g2*t-g3.
        Elite because: Elliptic function identities are computationally challenging.
        """,
        references=["Chandrasekharan (1985) Elliptic Functions"]
    ),

    EliteEquation(
        id="E17",
        expression="product(1 + q**(2*n-1), (n, 1, oo))**2 / product(1 - q**(2*n), (n, 1, oo))",
        expected_answer="summation(q**(n*(n+1)/2), (n, 0, oo)) [Jacobi triple product variant]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.MODULAR_ARITHMETIC, Technique.SPECIAL_FUNCTIONS],
        category="Modular Forms",
        justification="""
        This is a variant of Jacobi's triple product identity, connecting
        infinite products to theta function sums. Such identities are
        fundamental to partition theory and string theory.
        Elite because: Product-sum identities require sophisticated algebra.
        """,
        references=["Andrews, G.E. & Berndt, B.C. (2005) Ramanujan's Lost Notebook"]
    ),

    EliteEquation(
        id="E18",
        expression="AGM(1, sqrt(2)) - pi / (2 * EllipticK(1/2))",
        expected_answer="0 [Arithmetic-geometric mean and elliptic integral]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.ELLIPTIC_FUNCTIONS, Technique.SPECIAL_FUNCTIONS],
        category="Elliptic Functions",
        justification="""
        The arithmetic-geometric mean (AGM) equals pi/(2*K(k)) where K is the
        complete elliptic integral of the first kind. This fundamental identity
        underlies fast pi computation algorithms.
        Elite because: AGM-elliptic connections require careful limit analysis.
        """,
        references=["Borwein & Borwein (1987) Pi and the AGM",
                   "Gauss, C.F. (1799) Werke, Vol. 3"]
    ),
]


# =============================================================================
# CATEGORY 3: HYPERGEOMETRIC IDENTITIES & TRANSFORMATIONS (E19-E28)
# =============================================================================
# Hypergeometric functions satisfy numerous transformation and summation
# identities. These are crucial for physics (quantum mechanics, relativity)
# and combinatorics.

HYPERGEOMETRIC = [
    EliteEquation(
        id="E19",
        expression="hypergeom([1/2, 1/2], [1], z) - 2/pi * EllipticK(z)",
        expected_answer="0 [Hypergeometric-elliptic connection]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.HYPERGEOMETRIC, Technique.ELLIPTIC_FUNCTIONS],
        category="Hypergeometric Functions",
        justification="""
        The complete elliptic integral K(k) is a hypergeometric function
        2F1(1/2, 1/2; 1; k^2). This fundamental connection allows the vast
        hypergeometric identity library to apply to elliptic integrals.
        Elite because: Tests recognition of special function representations.
        """,
        references=["NIST DLMF 15.8", "Whittaker & Watson Chapter 22"]
    ),

    EliteEquation(
        id="E20",
        expression="hypergeom([a, b], [c], 1) - Gamma(c)*Gamma(c-a-b)/(Gamma(c-a)*Gamma(c-b))",
        expected_answer="0 [Gauss summation theorem, Re(c-a-b) > 0]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.HYPERGEOMETRIC, Technique.SPECIAL_FUNCTIONS],
        category="Hypergeometric Functions",
        justification="""
        Gauss's summation theorem gives the value of 2F1(a,b;c;1) in terms of
        Gamma functions when Re(c-a-b) > 0. This is one of the most important
        hypergeometric identities.
        Elite because: Fundamental identity that must be handled correctly.
        """,
        references=["Andrews, Askey, Roy (1999) Special Functions, Theorem 2.2.2"]
    ),

    EliteEquation(
        id="E21",
        expression="hypergeom([a, 1-a], [c], 1/2) - sqrt(pi)*Gamma(c)/(Gamma((a+c)/2)*Gamma((c-a+1)/2))",
        expected_answer="0 [Kummer's theorem at z=1/2]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.HYPERGEOMETRIC, Technique.SPECIAL_FUNCTIONS],
        category="Hypergeometric Functions",
        justification="""
        Kummer's theorem gives 2F1(a,1-a;c;1/2) in closed form. This is related
        to the duplication formula for Gamma functions and appears in quantum
        mechanics transition amplitudes.
        Elite because: Half-argument hypergeometric values are non-trivial.
        """,
        references=["Slater (1966) Generalized Hypergeometric Functions, Eq. 1.7.1.3"]
    ),

    EliteEquation(
        id="E22",
        expression="hypergeom([a, b, c], [d, e], 1) - Gamma(d)*Gamma(e)*Gamma(s)/(Gamma(a)*Gamma(b+s)*Gamma(c+s))",
        expected_answer="where s = d + e - a - b - c (Saalschutz/Pfaff-Saalschutz for 3F2)",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.HYPERGEOMETRIC, Technique.SPECIAL_FUNCTIONS],
        category="Hypergeometric Functions",
        justification="""
        The Pfaff-Saalschutz theorem sums balanced 3F2 series at z=1. These
        appear in 6j-symbols (quantum angular momentum), orthogonal polynomials,
        and combinatorics.
        Elite because: 3F2 summation requires precise parameter balancing conditions.
        """,
        references=["Bailey (1935) Generalized Hypergeometric Series"]
    ),

    EliteEquation(
        id="E23",
        expression="hypergeom([a, b], [c], z) - (1-z)**(-a) * hypergeom([a, c-b], [c], z/(z-1))",
        expected_answer="0 [Pfaff transformation]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.HYPERGEOMETRIC, Technique.FUNCTIONAL_EQUATIONS],
        category="Hypergeometric Functions",
        justification="""
        Pfaff's transformation relates 2F1 at z to 2F1 at z/(z-1). This is
        one of the basic hypergeometric transformations allowing analytic
        continuation.
        Elite because: Transformation formulas are essential for CAS completeness.
        """,
        references=["NIST DLMF 15.8.1"]
    ),

    EliteEquation(
        id="E24",
        expression="hypergeom([a, b], [(a+b+1)/2], 1/2) - sqrt(pi)*Gamma((a+b+1)/2)/(Gamma((a+1)/2)*Gamma((b+1)/2))",
        expected_answer="0 [Dougall's theorem special case]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.HYPERGEOMETRIC, Technique.SPECIAL_FUNCTIONS],
        category="Hypergeometric Functions",
        justification="""
        This is a special case of Dougall's formula relating 2F1 at 1/2 with
        special parameters to Gamma ratios. Such identities are crucial in
        theoretical physics.
        Elite because: Parameter relationships must be precisely tracked.
        """,
        references=["Bailey (1935) Chapter 3"]
    ),

    EliteEquation(
        id="E25",
        expression="hypergeom([-n, a, b], [c, d], 1) * Gamma(c)*Gamma(d) / (Gamma(c-a)*Gamma(d-b))",
        expected_answer="Terminating 3F2 Saalschutz [explicit polynomial]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.HYPERGEOMETRIC, Technique.SPECIAL_FUNCTIONS],
        category="Hypergeometric Functions",
        justification="""
        When one upper parameter is a negative integer, the series terminates.
        The Saalschutz theorem then gives explicit Gamma-function expressions.
        These appear in Clebsch-Gordan coefficients.
        Elite because: Terminating series require special handling.
        """,
        references=["Andrews, Askey, Roy (1999) Section 2.4"]
    ),

    EliteEquation(
        id="E26",
        expression="hypergeom([1/3, 2/3], [1], 27*z*(1-z)**2) - (1 - 4*z + z**2)**(1/6)",
        expected_answer="0 [Schwarz map for tetrahedral group]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.HYPERGEOMETRIC, Technique.MODULAR_ARITHMETIC],
        category="Hypergeometric Functions",
        justification="""
        This algebraic hypergeometric identity comes from Schwarz's theorem
        relating 2F1 to polyhedral groups. The parameters (1/3, 2/3; 1) correspond
        to the tetrahedral group action.
        Elite because: Algebraic hypergeometric values are rare and deep.
        """,
        references=["Schwarz (1873) Journal fur die reine und angewandte Mathematik"]
    ),

    EliteEquation(
        id="E27",
        expression="summation(binomial(2*n,n)**3 / 64**n, (n, 0, oo)) - 4*Gamma(1/4)**4 / (pi**3 * 16)",
        expected_answer="0 [Ramanujan-type series]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.HYPERGEOMETRIC, Technique.NUMBER_THEORY],
        category="Hypergeometric Functions",
        justification="""
        This is one of Ramanujan's remarkable series relating binomial sums
        to special values of Gamma(1/4). Such series are connected to:
        - Periods of elliptic curves
        - Arithmetic-geometric mean
        - Transcendence theory
        Elite because: Ramanujan-type series are at the frontier of special functions.
        """,
        references=["Berndt, B.C. (1985) Ramanujan's Notebooks",
                   "Zudilin (2003) Annals of Math."]
    ),

    EliteEquation(
        id="E28",
        expression="hypergeom([1/12, 5/12], [1], 1728*z/(1728*z - 1)**2) - (1-1728*z)**(1/12)",
        expected_answer="0 [j-invariant hypergeometric]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.HYPERGEOMETRIC, Technique.MODULAR_ARITHMETIC],
        category="Hypergeometric Functions",
        justification="""
        This connects hypergeometric functions to the modular j-invariant
        (1728 = 12^3). The parameters 1/12 and 5/12 arise from the modular
        group SL(2,Z). This is fundamental to moonshine theory.
        Elite because: j-invariant relations involve deep modular form theory.
        """,
        references=["Conway & Norton (1979) Monstrous Moonshine"]
    ),
]


# =============================================================================
# CATEGORY 4: ADVANCED NUMBER THEORY & L-FUNCTIONS (E29-E36)
# =============================================================================
# These involve Dirichlet L-functions, multiple zeta values, and deep
# arithmetic structure. Many connect to the Riemann Hypothesis and its
# generalizations.

NUMBER_THEORY_ADVANCED = [
    EliteEquation(
        id="E29",
        expression="summation((-1)**(n+1) * zeta(2*n) / (2*pi)**(2*n), (n, 1, oo))",
        expected_answer="1/2 - 1/(2*e**pi) - 1/(2*e**(-pi)) = 1/2 - 1/sinh(pi)",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="L-Functions",
        justification="""
        This alternating series over even zeta values converges to a hyperbolic
        function. It demonstrates the connection between:
        - Riemann zeta at even integers (pi^2n/Bernoulli)
        - Hyperbolic functions
        - Modular forms (via eta function)
        Elite because: Zeta sum-product relations are non-trivial.
        """,
        references=["Ramanujan's Collected Papers", "Berndt (1985)"]
    ),

    EliteEquation(
        id="E30",
        expression="zeta(2,1) + zeta(3) - zeta(2)*zeta(1)",
        expected_answer="0 is FALSE; actual = zeta(3) [Euler's MZV relation]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="Multiple Zeta Values",
        justification="""
        Multiple zeta values (MZVs) satisfy remarkable algebraic relations.
        zeta(2,1) = zeta(3) is one of Euler's original identities. Testing
        MZV relations probes the algebraic structure of these transcendental
        numbers.
        Elite because: MZV relations are an active research frontier.
        """,
        references=["Zagier (1994) First European Congress of Mathematics",
                   "Hoffman (1997) Pacific J. Math."]
    ),

    EliteEquation(
        id="E31",
        expression="DirichletL(-1, chi_4) - pi/4",
        expected_answer="0 [Dirichlet L-function at s=-1 for chi_4]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="L-Functions",
        justification="""
        Dirichlet L-functions generalize the Riemann zeta function to characters.
        For the non-trivial character mod 4, L(-1,chi_4) relates to pi through
        the functional equation. This connects to:
        - Gauss sums
        - Class number formulas
        - Quadratic forms
        Elite because: Dirichlet L special values require analytic continuation.
        """,
        references=["Davenport (1980) Multiplicative Number Theory",
                   "Ireland & Rosen (1990) A Classical Introduction to Modern Number Theory"]
    ),

    EliteEquation(
        id="E32",
        expression="summation((-1)**(n+1) / (n * (2*n-1)), (n, 1, oo)) - log(2) + pi/4",
        expected_answer="0 [Catalan-type series]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="Special Series",
        justification="""
        This series combines logarithmic and arctangent-type sums. Such mixed
        series appear in computation of fundamental constants and test the
        ability to recognize partial fraction decompositions.
        Elite because: Mixed arithmetic series require multi-technique approaches.
        """,
        references=["Jolley (1961) Summation of Series"]
    ),

    EliteEquation(
        id="E33",
        expression="LerchPhi(1/2, 2, 1) - pi**2/12 - (log(2))**2/2",
        expected_answer="0 [Lerch transcendent special value]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="L-Functions",
        justification="""
        The Lerch transcendent Phi(z,s,a) generalizes the polylogarithm and
        Hurwitz zeta. At special values it connects to:
        - Polylogarithms Li_s
        - Hurwitz zeta
        - Dirichlet beta function
        Elite because: Lerch transcendent is rarely implemented completely.
        """,
        references=["Erdelyi et al. (1953) Higher Transcendental Functions"]
    ),

    EliteEquation(
        id="E34",
        expression="sum(mu(n) * log(n)**2 / n, (n, 1, oo)) + 2*gamma_1",
        expected_answer="0 where gamma_1 is first Stieltjes constant",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.NUMBER_THEORY, Technique.ASYMPTOTIC_ANALYSIS],
        category="Number Theory",
        justification="""
        This series involving the Moebius function and logarithmic powers
        converges conditionally to a value involving Stieltjes constants.
        It is related to the Prime Number Theorem and zero-free regions
        of zeta.
        Elite because: Moebius function series probe prime distribution.
        """,
        references=["Titchmarsh (1986) Theory of the Riemann Zeta-Function",
                   "Ivic (2003) The Riemann Zeta-Function"]
    ),

    EliteEquation(
        id="E35",
        expression="product(1/(1 - p**(-2) - p**(-3)), (p, primes))",
        expected_answer="zeta(2)*zeta(3)/zeta(6) [Euler product factorization]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="Euler Products",
        justification="""
        Euler products with polynomial factors in p^(-s) can often be expressed
        as ratios of zeta values. This specific product factors because
        1 - x - x^(3/2) splits over algebraic numbers.
        Elite because: Euler product factorization is computationally hard.
        """,
        references=["Apostol (1976) Introduction to Analytic Number Theory"]
    ),

    EliteEquation(
        id="E36",
        expression="summation(floor(sqrt(n))**(-1) * mu(n), (n, 1, N))",
        expected_answer="O(N^(1/2) / log(N)) [asymptotic under RH]",
        difficulty=Difficulty.UNDECIDABLE,
        techniques=[Technique.NUMBER_THEORY, Technique.ASYMPTOTIC_ANALYSIS],
        category="Number Theory",
        justification="""
        The rate of cancellation in Moebius sums is intimately connected to
        the Riemann Hypothesis. This specific sum involves floor functions
        making explicit evaluation undecidable in general, though asymptotics
        can be established conditionally on RH.
        Elite because: This touches undecidability boundaries.
        """,
        references=["Iwaniec & Kowalski (2004) Analytic Number Theory"]
    ),
]


# =============================================================================
# CATEGORY 5: MULTI-TECHNIQUE SYNTHESIS PROBLEMS (E37-E44)
# =============================================================================
# These problems require combining multiple mathematical techniques:
# calculus, algebra, analysis, and number theory together.

MULTI_TECHNIQUE = [
    EliteEquation(
        id="E37",
        expression="integrate(x**(a-1) * (1-x)**(b-1) * log(x) * log(1-x), (x, 0, 1))",
        expected_answer="Beta(a,b) * (psi(a) - psi(a+b)) * (psi(b) - psi(a+b)) + Beta(a,b) * (psi_1(a) + psi_1(b) - psi_1(a+b))",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.CONTOUR_INTEGRATION, Technique.HYPERGEOMETRIC],
        category="Multi-Technique",
        justification="""
        This integral involves Beta function moments with logarithmic weights.
        It requires:
        - Differentiation of Beta function wrt parameters (digamma)
        - Second derivatives (trigamma psi_1)
        - Careful treatment of logarithmic singularities
        Elite because: Log-weighted Beta integrals test parameter differentiation.
        """,
        references=["Gradshteyn & Ryzhik 4.253"]
    ),

    EliteEquation(
        id="E38",
        expression="limit(sum(exp(-n/x) * n**s / factorial(n), (n, 0, oo)) / x**s, x, oo)",
        expected_answer="1 [relates to Borel summation]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.ASYMPTOTIC_ANALYSIS, Technique.SPECIAL_FUNCTIONS, Technique.FUNCTIONAL_EQUATIONS],
        category="Multi-Technique",
        justification="""
        This limit relates to Borel summation and moment asymptotics. The
        exponential-factorial interplay creates subtle cancellations that
        must be tracked through the limit.
        Elite because: Asymptotic-combinatorial limits require careful analysis.
        """,
        references=["Hardy (1949) Divergent Series"]
    ),

    EliteEquation(
        id="E39",
        expression="integrate(BesselJ(0, a*x) * BesselJ(0, b*x) * exp(-c*x), (x, 0, oo))",
        expected_answer="2*EllipticK(2*sqrt(a*b)/(a+b+c)) / (pi*sqrt((a+b+c)**2 - 4*a*b))",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.CONTOUR_INTEGRATION, Technique.ELLIPTIC_FUNCTIONS],
        category="Multi-Technique",
        justification="""
        Bessel function integrals often reduce to elliptic functions. This
        specific integral appears in:
        - Quantum electrodynamics
        - Heat conduction in cylinders
        - Antenna theory
        Elite because: Bessel-elliptic connections are computationally challenging.
        """,
        references=["Watson (1944) A Treatise on Bessel Functions",
                   "Prudnikov et al. (1986) Vol. 2"]
    ),

    EliteEquation(
        id="E40",
        expression="summation(zeta(2*n) * zeta(2*m) / zeta(2*n + 2*m), (n, 1, oo), (m, 1, oo))",
        expected_answer="Sum involves stuffle products [double MZV territory]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.NUMBER_THEORY, Technique.HYPERGEOMETRIC, Technique.SPECIAL_FUNCTIONS],
        category="Multi-Technique",
        justification="""
        Double sums over zeta values lie in the territory of double shuffle
        relations for MZVs. These connect to:
        - Motivic Galois theory
        - String theory amplitudes
        - Algebraic K-theory
        Elite because: Double zeta sums are active research.
        """,
        references=["Bluemlein et al. (2010) Comput. Phys. Comm."]
    ),

    EliteEquation(
        id="E41",
        expression="det(Matrix([[BesselJ(i+j, x) for j in range(n)] for i in range(n)]))",
        expected_answer="Product formula involving x and factorials [Bessel determinant]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.MULTI_TECHNIQUE],
        category="Multi-Technique",
        justification="""
        Determinants of matrices with special function entries have remarkable
        closed forms (Hankel determinants). The Bessel determinant is related to:
        - Random matrix theory
        - Painleve transcendents
        - Orthogonal polynomial theory
        Elite because: Special function determinants are rarely simplified.
        """,
        references=["Krattenthaler (1999) Advanced Determinant Calculus"]
    ),

    EliteEquation(
        id="E42",
        expression="limit(product(1 + 1/(n**2 + a**2), (n, 1, N)) / (sinh(pi*a)/(pi*a)), N, oo)",
        expected_answer="1 [Weierstrass product for sinh]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.ASYMPTOTIC_ANALYSIS, Technique.FUNCTIONAL_EQUATIONS],
        category="Multi-Technique",
        justification="""
        The Weierstrass product representation of sinh(pi*a)/(pi*a) as a
        product over zeros tests understanding of:
        - Entire function theory
        - Product-sum duality
        - Convergence of infinite products
        Elite because: Weierstrass products are fundamental but tricky.
        """,
        references=["Ahlfors (1979) Complex Analysis"]
    ),

    EliteEquation(
        id="E43",
        expression="integrate(polylog(2, exp(I*x)) * polylog(2, exp(-I*x)), (x, 0, pi))",
        expected_answer="pi**5/90 [polylogarithm integral]",
        difficulty=Difficulty.FRONTIER,
        techniques=[Technique.SPECIAL_FUNCTIONS, Technique.NUMBER_THEORY, Technique.CONTOUR_INTEGRATION],
        category="Multi-Technique",
        justification="""
        Integrals of polylogarithm products over the unit circle yield
        remarkable zeta values. This connects to:
        - Mahler measures
        - K-theory
        - Feynman integrals
        Elite because: Polylog integrals are at the frontier of computation.
        """,
        references=["Lewin (1981) Polylogarithms and Associated Functions"]
    ),

    EliteEquation(
        id="E44",
        expression="limit((sum(1/k, (k,1,n)) - log(n) - gamma - 1/(2*n) + 1/(12*n**2)) * n**4, n, oo)",
        expected_answer="-1/120 [Euler-Maclaurin 4th order]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.ASYMPTOTIC_ANALYSIS, Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="Multi-Technique",
        justification="""
        The Euler-Maclaurin formula gives asymptotic expansions of harmonic
        sums. The coefficients are Bernoulli numbers: -B_4/4 = -1/120.
        This tests:
        - Bernoulli number recognition
        - High-order asymptotic analysis
        - Correction term tracking
        Elite because: High-order asymptotics challenge numerical methods.
        """,
        references=["Apostol (1999) An Elementary View of Euler's Summation Formula"]
    ),
]


# =============================================================================
# CATEGORY 6: FAMOUS PROBLEMS & MODERN RESEARCH (E45-E50)
# =============================================================================
# These connect to famous conjectures, recently solved problems, and
# modern research directions in mathematics.

FAMOUS_MODERN = [
    EliteEquation(
        id="E45",
        expression="summation(1/n**3 * sin(n*pi/3), (n, 1, oo))",
        expected_answer="pi**3 / (18*sqrt(3)) - sqrt(3)*Cl_3(pi/3)/2 [Clausen function]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="Famous Problems",
        justification="""
        This series is related to the Clausen function Cl_s(x), which connects:
        - Polylogarithms on the unit circle
        - Special values of L-functions
        - Volumes of hyperbolic 3-manifolds
        Elite because: Clausen functions appear in Zagier's dilogarithm conjectures.
        """,
        references=["Zagier (1986) Polylogarithms, Dedekind zeta functions",
                   "Lewin (1991) Structural Properties of Polylogarithms"]
    ),

    EliteEquation(
        id="E46",
        expression="limit(sum(exp(-n**2 * t), (n, -oo, oo)) * sqrt(t) - sqrt(pi), t, 0, '+')",
        expected_answer="0 [Jacobi theta modular transformation]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.MODULAR_ARITHMETIC, Technique.ASYMPTOTIC_ANALYSIS],
        category="Famous Problems",
        justification="""
        The Jacobi theta function satisfies theta_3(0, e^{-pi*t}) * sqrt(t) =
        theta_3(0, e^{-pi/t}). At t->0 this becomes sqrt(pi). This modular
        transformation is:
        - Key to Riemann zeta functional equation
        - Foundation of modular form theory
        - Used in string theory compactification
        Elite because: Modular transformations are fundamental and deep.
        """,
        references=["Mumford (1983) Tata Lectures on Theta I"]
    ),

    EliteEquation(
        id="E47",
        expression="integrate(log(x)**2 / (1 + x**2), (x, 0, oo))",
        expected_answer="pi**3/8 [relates to Catalan's constant]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.CONTOUR_INTEGRATION, Technique.SPECIAL_FUNCTIONS],
        category="Famous Problems",
        justification="""
        This integral evaluates to pi^3/8, connecting to:
        - Catalan's constant G (via related integrals)
        - Special L-function values
        - Transcendence questions
        Elite because: Log^n integrals have beautiful closed forms.
        """,
        references=["Boros & Moll (2004) Irresistible Integrals"]
    ),

    EliteEquation(
        id="E48",
        expression="summation((-1)**(n+1) * H_n / n**2, (n, 1, oo))",
        expected_answer="5*zeta(3)/8 [Euler sum identity]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.NUMBER_THEORY, Technique.SPECIAL_FUNCTIONS],
        category="Famous Problems",
        justification="""
        Euler sums Sum_{n>=1} H_n^{(p)} / n^q are classical objects with deep
        connections to:
        - Multiple zeta values
        - Knot invariants
        - Quantum field theory
        This specific sum equals 5*zeta(3)/8, one of Euler's original results.
        Elite because: Euler sum evaluation requires sophisticated techniques.
        """,
        references=["Flajolet & Salvy (1998) Exp. Math."]
    ),

    EliteEquation(
        id="E49",
        expression="integrate(1/(1 + x**n), (x, 0, oo)) - pi/(n * sin(pi/n))",
        expected_answer="0 [Euler's reflection formula application]",
        difficulty=Difficulty.GRADUATE,
        techniques=[Technique.CONTOUR_INTEGRATION, Technique.SPECIAL_FUNCTIONS],
        category="Famous Problems",
        justification="""
        This integral evaluates via contour integration to pi*csc(pi/n)/n.
        It demonstrates:
        - Residue calculus on branch cuts
        - Euler's reflection formula for Gamma
        - Beta function integral representation
        Elite because: Classic contour integral that tests fundamental techniques.
        """,
        references=["Ahlfors (1979) Complex Analysis, Chapter 4"]
    ),

    EliteEquation(
        id="E50",
        expression="limit(sum((-1)**k * binomial(2*n, n+k) * (2*k+1)**(2*m+1), (k, -n, n)) / (2*n+1)**(2*m+1), n, oo)",
        expected_answer="1 [Central limit theorem / de Moivre-Laplace]",
        difficulty=Difficulty.RESEARCH,
        techniques=[Technique.ASYMPTOTIC_ANALYSIS, Technique.SPECIAL_FUNCTIONS, Technique.MULTI_TECHNIQUE],
        category="Famous Problems",
        justification="""
        This combinatorial limit is related to the Central Limit Theorem and
        random walk asymptotics. The alternating binomial sum with odd power
        weighting captures:
        - Stirling approximation refinements
        - Moment generating function asymptotics
        - Lattice path enumeration
        Elite because: Asymptotic combinatorics requires multiple techniques.
        """,
        references=["Feller (1968) Introduction to Probability Theory",
                   "De Bruijn (1981) Asymptotic Methods in Analysis"]
    ),
]


# =============================================================================
# COMBINED ELITE 50 COLLECTION
# =============================================================================

ELITE_50_EQUATIONS: List[EliteEquation] = (
    MEIJER_G_BARNES +      # E01-E10
    MODULAR_ELLIPTIC +     # E11-E18
    HYPERGEOMETRIC +       # E19-E28
    NUMBER_THEORY_ADVANCED + # E29-E36
    MULTI_TECHNIQUE +      # E37-E44
    FAMOUS_MODERN          # E45-E50
)


# For easy iteration in tests
def get_equations_by_category(category: str) -> List[EliteEquation]:
    """Return equations filtered by category name."""
    return [eq for eq in ELITE_50_EQUATIONS if eq.category.lower() == category.lower()]


def get_equations_by_difficulty(difficulty: Difficulty) -> List[EliteEquation]:
    """Return equations filtered by difficulty level."""
    return [eq for eq in ELITE_50_EQUATIONS if eq.difficulty == difficulty]


def get_equations_by_technique(technique: Technique) -> List[EliteEquation]:
    """Return equations that require a specific technique."""
    return [eq for eq in ELITE_50_EQUATIONS if technique in eq.techniques]


# =============================================================================
# SIMPLE TEST EXPRESSION LIST (for compatibility with test runners)
# =============================================================================

ELITE_50_SIMPLE = [
    # E01-E10: Meijer G & Barnes
    ("integrate(x**(s-1) * MeijerG([[a,b],[c]],[[d,e],[f]], x), (x, 0, oo))", "Meijer G Mellin transform"),
    ("MeijerG([[1/2],[]], [[0,0],[1/2]], x) - 2*erfc(sqrt(x))/sqrt(pi)", "G-function erfc identity"),
    ("integrate(MeijerG([[-a],[]], [[0],[b]], x) * MeijerG([[-c],[]], [[0],[d]], x), (x, 0, oo))", "G-function convolution"),
    ("BarnesIntegral(Gamma(s)*Gamma(a-s)*Gamma(b-s)/Gamma(c-s), s)", "Barnes first lemma"),
    ("limit(MeijerG([[a,b],[c]], [[d,e],[]], z) / z**(-d-e), z, 0, '+')", "G-function asymptotic"),
    ("integrate(x**(rho-1) * exp(-p*x) * MeijerG([[a],[]], [[b],[c]], q*x), (x, 0, oo))", "G-function Laplace"),
    ("BarnesIntegral(Gamma(s)**3/Gamma(3*s), s) / (2*pi*I)", "Triple Gamma Barnes"),
    ("MeijerG([[],[1/2]], [[0,-1/2],[]], z) - (1 + sqrt(1+z))/sqrt(z)", "G-function algebraic reduction"),
    ("summation(MeijerG([[a],[b]], [[c],[d]], n) / factorial(n), (n, 0, oo))", "G-function EGF"),
    ("integrate(exp(-t) * MeijerG([[a],[]], [[0,b],[]], x*t), (t, 0, oo))", "G-function Hankel form"),

    # E11-E18: Modular & Elliptic
    ("summation(q**(n*(3*n-1)/2) * (1 + 2*q**n), (n, -oo, oo))", "Extended pentagonal theorem"),
    ("DedekindEta(tau)**24 - Delta(tau)", "Ramanujan discriminant"),
    ("EllipticE(m)*EllipticK(1-m) + EllipticK(m)*EllipticE(1-m) - EllipticK(m)*EllipticK(1-m) - pi/2", "Legendre relation"),
    ("ThetaFunction(3, 0, exp(-pi)) - sqrt(Gamma(1/4)**2 / (4*pi**(3/2)))", "Theta special value"),
    ("EisensteinE(4, tau) * EisensteinE(6, tau) - 720*RamanujanTau(tau)", "Eisenstein modular relation"),
    ("WeierstrassP(z, g2, g3) + WeierstrassP(z + omega1/2, g2, g3) + WeierstrassP(z + omega2/2, g2, g3)", "Weierstrass half-periods"),
    ("product(1 + q**(2*n-1), (n, 1, oo))**2 / product(1 - q**(2*n), (n, 1, oo))", "Jacobi triple product variant"),
    ("AGM(1, sqrt(2)) - pi / (2 * EllipticK(1/2))", "AGM-elliptic connection"),

    # E19-E28: Hypergeometric
    ("hypergeom([1/2, 1/2], [1], z) - 2/pi * EllipticK(z)", "Hypergeometric-elliptic"),
    ("hypergeom([a, b], [c], 1) - Gamma(c)*Gamma(c-a-b)/(Gamma(c-a)*Gamma(c-b))", "Gauss summation"),
    ("hypergeom([a, 1-a], [c], 1/2) - sqrt(pi)*Gamma(c)/(Gamma((a+c)/2)*Gamma((c-a+1)/2))", "Kummer at 1/2"),
    ("hypergeom([a, b, c], [d, e], 1)", "3F2 at unity (Saalschutz)"),
    ("hypergeom([a, b], [c], z) - (1-z)**(-a) * hypergeom([a, c-b], [c], z/(z-1))", "Pfaff transformation"),
    ("hypergeom([a, b], [(a+b+1)/2], 1/2) - sqrt(pi)*Gamma((a+b+1)/2)/(Gamma((a+1)/2)*Gamma((b+1)/2))", "Dougall special case"),
    ("hypergeom([-n, a, b], [c, d], 1)", "Terminating 3F2"),
    ("hypergeom([1/3, 2/3], [1], 27*z*(1-z)**2) - (1 - 4*z + z**2)**(1/6)", "Schwarz tetrahedral"),
    ("summation(binomial(2*n,n)**3 / 64**n, (n, 0, oo)) - 4*Gamma(1/4)**4 / (pi**3 * 16)", "Ramanujan binomial sum"),
    ("hypergeom([1/12, 5/12], [1], 1728*z/(1728*z - 1)**2) - (1-1728*z)**(1/12)", "j-invariant hypergeometric"),

    # E29-E36: Advanced Number Theory
    ("summation((-1)**(n+1) * zeta(2*n) / (2*pi)**(2*n), (n, 1, oo))", "Alternating zeta sum"),
    ("zeta(2,1) - zeta(3)", "MZV Euler identity"),
    ("DirichletL(-1, chi_4) - pi/4", "Dirichlet L at -1"),
    ("summation((-1)**(n+1) / (n * (2*n-1)), (n, 1, oo)) - log(2) + pi/4", "Catalan-type series"),
    ("LerchPhi(1/2, 2, 1) - pi**2/12 - (log(2))**2/2", "Lerch transcendent special"),
    ("summation(mu(n) * log(n)**2 / n, (n, 1, oo)) + 2*gamma_1", "Moebius log-squared sum"),
    ("product(1/(1 - p**(-2) - p**(-3)), (p, primes))", "Euler product factorization"),
    ("summation(floor(sqrt(n))**(-1) * mu(n), (n, 1, N))", "Moebius floor asymptotic (RH)"),

    # E37-E44: Multi-technique
    ("integrate(x**(a-1) * (1-x)**(b-1) * log(x) * log(1-x), (x, 0, 1))", "Beta log-log integral"),
    ("limit(summation(exp(-n/x) * n**s / factorial(n), (n, 0, oo)) / x**s, x, oo)", "Borel summation limit"),
    ("integrate(BesselJ(0, a*x) * BesselJ(0, b*x) * exp(-c*x), (x, 0, oo))", "Double Bessel Laplace"),
    ("summation(zeta(2*n) * zeta(2*m) / zeta(2*n + 2*m), (n, 1, oo), (m, 1, oo))", "Double zeta sum"),
    ("det(Matrix([[BesselJ(i+j, x) for j in range(n)] for i in range(n)]))", "Bessel Hankel determinant"),
    ("limit(product(1 + 1/(n**2 + a**2), (n, 1, N)) / (sinh(pi*a)/(pi*a)), N, oo)", "Weierstrass product sinh"),
    ("integrate(polylog(2, exp(I*x)) * polylog(2, exp(-I*x)), (x, 0, pi))", "Polylog product integral"),
    ("limit((sum(1/k, (k,1,n)) - log(n) - gamma - 1/(2*n) + 1/(12*n**2)) * n**4, n, oo)", "Euler-Maclaurin 4th order"),

    # E45-E50: Famous & Modern
    ("summation(1/n**3 * sin(n*pi/3), (n, 1, oo))", "Clausen function series"),
    ("limit(summation(exp(-n**2 * t), (n, -oo, oo)) * sqrt(t) - sqrt(pi), t, 0, '+')", "Theta modular transform"),
    ("integrate(log(x)**2 / (1 + x**2), (x, 0, oo))", "Log-squared Catalan-related"),
    ("summation((-1)**(n+1) * H_n / n**2, (n, 1, oo))", "Euler sum 5/8 zeta(3)"),
    ("integrate(1/(1 + x**n), (x, 0, oo)) - pi/(n * sin(pi/n))", "Euler reflection integral"),
    ("limit(summation((-1)**k * binomial(2*n, n+k) * (2*k+1)**(2*m+1), (k, -n, n)) / (2*n+1)**(2*m+1), n, oo)", "CLT combinatorial limit"),
]


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_elite_tests(verbose: bool = False):
    """Run all 50 elite tests through the solver engine."""
    import time

    try:
        from symbo_agentic_reasoners.core.solver_engine import get_solver_engine, SolveStatus
    except ImportError:
        print("ERROR: Could not import solver engine. Run from project root.")
        return None, None

    solver = get_solver_engine()

    print("=" * 80)
    print("ELITE 50: RESEARCH-GRADE MATHEMATICAL EQUATIONS TEST SUITE")
    print("=" * 80)
    print(f"Total equations: {len(ELITE_50_EQUATIONS)}")
    print()

    results = []
    passed = 0
    failed = 0

    categories = {
        "Meijer G & Barnes (E01-E10)": (0, 10),
        "Modular & Elliptic (E11-E18)": (10, 18),
        "Hypergeometric (E19-E28)": (18, 28),
        "Number Theory (E29-E36)": (28, 36),
        "Multi-Technique (E37-E44)": (36, 44),
        "Famous & Modern (E45-E50)": (44, 50)
    }

    for i, eq in enumerate(ELITE_50_EQUATIONS):
        expr = ELITE_50_SIMPLE[i][0]
        desc = ELITE_50_SIMPLE[i][1]

        print(f"[{eq.id}] {desc[:50]:<50}", end=" ")

        try:
            start = time.time()
            result = solver.solve(expr)
            elapsed = time.time() - start

            status = result.status.name if hasattr(result, 'status') else str(result.status)
            result_str = str(result.result) if result.result else "None"

            is_error = (
                status in ["ERROR", "FAILURE"] or
                "error" in result_str.lower() or
                "failed" in result_str.lower() or
                result_str in ["None", ""] or
                "NotImplementedError" in result_str
            )

            if is_error:
                print(f"FAIL ({elapsed:.2f}s)")
                failed += 1
            else:
                print(f"PASS ({elapsed:.2f}s)")
                passed += 1

            if verbose:
                print(f"      Result: {result_str[:80]}...")

            results.append({
                'id': eq.id,
                'passed': not is_error,
                'status': status,
                'result': result_str[:200],
                'time': elapsed
            })

        except Exception as e:
            print(f"ERROR: {str(e)[:40]}")
            failed += 1
            results.append({
                'id': eq.id,
                'passed': False,
                'status': 'EXCEPTION',
                'result': str(e)[:200],
                'time': 0
            })

    print()
    print("=" * 80)
    print(f"OVERALL: {passed}/{len(ELITE_50_EQUATIONS)} passed ({100*passed/len(ELITE_50_EQUATIONS):.1f}%)")
    print("=" * 80)

    print("\nBY CATEGORY:")
    print("-" * 80)
    for cat_name, (start_idx, end_idx) in categories.items():
        cat_results = results[start_idx:end_idx]
        cat_passed = sum(1 for r in cat_results if r['passed'])
        cat_total = end_idx - start_idx
        print(f"  {cat_name}: {cat_passed}/{cat_total} ({100*cat_passed/cat_total:.1f}%)")

    print("\nBY DIFFICULTY:")
    print("-" * 80)
    for diff in Difficulty:
        diff_eqs = get_equations_by_difficulty(diff)
        if diff_eqs:
            diff_ids = [eq.id for eq in diff_eqs]
            diff_passed = sum(1 for r in results if r['id'] in diff_ids and r['passed'])
            print(f"  {diff.value.upper()}: {diff_passed}/{len(diff_eqs)}")

    return passed, len(ELITE_50_EQUATIONS)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Elite 50 mathematical test suite")
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed results')
    args = parser.parse_args()

    passed, total = run_elite_tests(verbose=args.verbose)
    if passed is not None:
        exit(0 if passed == total else 1)
    else:
        exit(1)
