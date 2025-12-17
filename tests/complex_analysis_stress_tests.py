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
Complex Analysis Stress Tests - 50 BRUTAL Research-Level Problems
==================================================================

These tests are designed to BREAK the Complex Analysis domain specialists:
- AnalyticFunctionsSpecialist
- ResidueCalculusSpecialist
- ConformalMappingSpecialist
- ContourIntegrationSpecialist

Each test targets specific weaknesses in numerical complex analysis:
- Essential singularities with wild oscillatory behavior
- High-order pole residue computation (catastrophic cancellation)
- Nearly-degenerate Mobius transformations
- Schwarz-Christoffel near-parallel edge instability
- Branch cut crossing and multi-sheet Riemann surfaces
- Argument principle for clustered zeros
- Natural boundary analytic continuation
- Cauchy-Riemann verification at irregular points
- Self-intersecting and fractal-like contours
- Multiply connected domain conformal mapping

DIFFICULTY LEVELS:
- brutal: Will stress most implementations
- extreme: Requires careful numerical handling
- pathological: Edge cases from research mathematics
"""

import numpy as np
from typing import Dict, List, Any

# =============================================================================
# CATEGORY 1: LAURENT SERIES AT ESSENTIAL SINGULARITIES (10 tests)
# =============================================================================

LAURENT_ESSENTIAL_SINGULARITY_TESTS = [
    {
        "test_id": "CPLX_001",
        "category": "laurent_series",
        "input": "Laurent series of exp(1/z) at z=0, extract coefficients a_{-10} through a_{10}",
        "expected": "a_n = 1/n! for n >= 0, a_{-n} = 1/n! for principal part (sum over all integers)",
        "difficulty": "brutal",
        "rationale": "exp(1/z) has an essential singularity with infinitely many negative-power terms. "
                    "The coefficients 1/n! decay factorially but numerical contour integration struggles "
                    "with the wild oscillations near z=0. The function takes every complex value "
                    "infinitely often in any punctured neighborhood (Picard's Great Theorem)."
    },
    {
        "test_id": "CPLX_002",
        "category": "laurent_series",
        "input": "Laurent series of sin(1/z) at z=0, verify Casorati-Weierstrass behavior",
        "expected": "Essential singularity with coefficients from sin power series: sum((-1)^n / (2n+1)! * z^{-(2n+1)})",
        "difficulty": "extreme",
        "rationale": "sin(1/z) oscillates infinitely often as z->0 along any path. Numerical Laurent "
                    "coefficient extraction via contour integration gives catastrophically wrong results "
                    "for small radii due to the density theorem - the function comes arbitrarily close to "
                    "every complex value."
    },
    {
        "test_id": "CPLX_003",
        "category": "laurent_series",
        "input": "Laurent series of z*exp(1/z^2) at z=0, determine singularity type and principal part order",
        "expected": "Essential singularity (infinite principal part), leading behavior exp(1/z^2) dominates",
        "difficulty": "extreme",
        "rationale": "The composition exp(1/z^2) creates a double-speed essential singularity. "
                    "The z factor doesn't change the essential nature. Coefficient extraction requires "
                    "integration over contours that must avoid the violent oscillations near z=0."
    },
    {
        "test_id": "CPLX_004",
        "category": "laurent_series",
        "input": "Laurent series of exp(1/z) * cos(1/z) at z=0",
        "expected": "Product of two essential singularities gives essential singularity with Cauchy-product coefficients",
        "difficulty": "pathological",
        "rationale": "The product of two essential singularities creates interference patterns in the "
                    "oscillations. The Cauchy product of the two Laurent series requires computing "
                    "infinitely many convolution terms. Numerically intractable near z=0."
    },
    {
        "test_id": "CPLX_005",
        "category": "laurent_series",
        "input": "Laurent series of exp(z + 1/z) at z=0 (Bessel function generating function)",
        "expected": "sum_{n=-infty}^{infty} I_n(2) * z^n where I_n are modified Bessel functions",
        "difficulty": "pathological",
        "rationale": "This is the generating function for modified Bessel functions. The coefficients are "
                    "I_n(2), which require careful computation. Essential singularity at z=0 combined "
                    "with entire function exp(z) creates a mixed behavior that confuses pole detection."
    },
    {
        "test_id": "CPLX_006",
        "category": "laurent_series",
        "input": "Laurent series of 1/(exp(1/z) - 1) near z=0",
        "expected": "Poles at z = 1/(2*pi*i*n) for all nonzero integers n, essential singularity at z=0",
        "difficulty": "pathological",
        "rationale": "This function has infinitely many poles accumulating at z=0, making z=0 a non-isolated "
                    "singularity (not even essential in the usual sense). Laurent series doesn't exist in "
                    "any punctured disk around 0. Tests whether the system correctly identifies this."
    },
    {
        "test_id": "CPLX_007",
        "category": "laurent_series",
        "input": "Determine Laurent series radius of convergence for z*tan(1/z) at z=0",
        "expected": "Inner radius = 0, outer radius = 2/pi (nearest pole of tan at 1/(pi/2))",
        "difficulty": "brutal",
        "rationale": "tan(1/z) has poles at z = 2/(pi*(2n+1)) accumulating at z=0. The Laurent series "
                    "converges in an annulus whose inner radius is 0 (essential singularity) and outer "
                    "radius is the distance to the nearest pole."
    },
    {
        "test_id": "CPLX_008",
        "category": "laurent_series",
        "input": "Laurent series of (z^2 - 1)*exp(1/(z-1)) at z=1",
        "expected": "a_{-n} = (-1)^n/n! multiplied by (z-1) factor, essential singularity softened by zero",
        "difficulty": "extreme",
        "rationale": "The factor (z-1) in (z^2-1) = (z-1)(z+1) partially cancels the singularity, "
                    "but exp(1/(z-1)) still has an essential singularity. The interplay between the "
                    "zero and essential singularity requires careful analysis."
    },
    {
        "test_id": "CPLX_009",
        "category": "laurent_series",
        "input": "Laurent series of exp(1/z)/z^10 at z=0",
        "expected": "Coefficients shifted: a_{n-10} where exp(1/z) = sum a_n z^n",
        "difficulty": "brutal",
        "rationale": "Multiplying by z^{-10} shifts all coefficients but doesn't change the essential "
                    "nature. The principal part now starts at z^{-10} from the exp(1/z) constant term, "
                    "but the full principal part extends to -infinity."
    },
    {
        "test_id": "CPLX_010",
        "category": "laurent_series",
        "input": "Laurent series of log(1 + exp(1/z)) at z=0, principal branch",
        "expected": "Essential singularity with branch point complications from log",
        "difficulty": "pathological",
        "rationale": "Composition of log with an essential singularity creates multi-sheet Riemann surface "
                    "behavior. The argument of log oscillates through all values infinitely often, "
                    "crossing branch cuts repeatedly. Numerical series extraction is essentially impossible."
    },
]

# =============================================================================
# CATEGORY 2: RESIDUE COMPUTATION WITH HIGH-ORDER POLES (10 tests)
# =============================================================================

RESIDUE_HIGH_ORDER_POLE_TESTS = [
    {
        "test_id": "CPLX_011",
        "category": "residue_calculus",
        "input": "Compute Res(1/(z-i)^15, z=i)",
        "expected": "0 (residue of 1/(z-a)^n is 0 for n > 1)",
        "difficulty": "brutal",
        "rationale": "For a pure pole 1/(z-a)^n, the residue (coefficient of (z-a)^{-1}) is 0 for n > 1. "
                    "However, the derivative formula Res = lim (1/(n-1)!) d^{n-1}/dz^{n-1}[(z-a)^n f(z)] "
                    "involves computing the 14th derivative, which is catastrophically ill-conditioned numerically."
    },
    {
        "test_id": "CPLX_012",
        "category": "residue_calculus",
        "input": "Compute Res(exp(z)/(z^12), z=0)",
        "expected": "1/11! = 1/39916800 (coefficient of z^11 in exp(z))",
        "difficulty": "extreme",
        "rationale": "For pole of order 12, residue = (1/11!) * d^11/dz^11[z^12 * exp(z)/z^12]|_{z=0} "
                    "= (1/11!) * d^11/dz^11[exp(z)]|_{z=0} = 1/11!. Numerical 11th derivatives accumulate "
                    "massive roundoff errors."
    },
    {
        "test_id": "CPLX_013",
        "category": "residue_calculus",
        "input": "Compute Res(sin(z)/(z^20), z=0)",
        "expected": "Coefficient of z^19 in sin(z) = (-1)^9/19! = -1/19!",
        "difficulty": "pathological",
        "rationale": "sin(z)/z^20 has a pole of order 19 (since sin(z) ~ z - z^3/6 + ...). "
                    "The residue is the coefficient of z^19 in sin(z), which is (-1)^9/19!. "
                    "Computing 18 numerical derivatives destroys all significant figures."
    },
    {
        "test_id": "CPLX_014",
        "category": "residue_calculus",
        "input": "Compute Res(1/((z-1)^5 * (z+1)^5), z=1)",
        "expected": "Use partial fractions or derivative formula for order-5 pole",
        "difficulty": "brutal",
        "rationale": "Fifth-order pole requires fourth derivative computation. The presence of another "
                    "fifth-order pole at z=-1 complicates both numerical and symbolic approaches. "
                    "Partial fractions give 10 terms, each with potential cancellation."
    },
    {
        "test_id": "CPLX_015",
        "category": "residue_calculus",
        "input": "Compute Res(z^100/((z-1)^101), z=1)",
        "expected": "Binomial coefficient C(100, 100) = 1 from Taylor expansion of z^100 at z=1",
        "difficulty": "pathological",
        "rationale": "Pole of order 101 with z^100 in numerator. The residue involves 100th derivative "
                    "of (z-1)^101 * z^100/(z-1)^101 = z^100, which is just z^100. The 100th derivative "
                    "at z=1 requires expanding (1+(z-1))^100 = sum C(100,k)(z-1)^k."
    },
    {
        "test_id": "CPLX_016",
        "category": "residue_calculus",
        "input": "Compute sum of residues of tan(z)/z^8 in |z| < 5",
        "expected": "Residue at z=0 plus residues at z = +/- pi/2, +/- 3*pi/2",
        "difficulty": "extreme",
        "rationale": "tan(z) has simple poles at z = (2n+1)*pi/2. Combined with z^8 in denominator, "
                    "we get a pole of order 8 at z=0 (since tan(z) ~ z near 0). Computing all residues "
                    "and their sum tests both high-order and simple pole algorithms."
    },
    {
        "test_id": "CPLX_017",
        "category": "residue_calculus",
        "input": "Compute Res(1/(sin(z)^10), z=0)",
        "expected": "Coefficient of z^9 in 1/sin(z)^10, involves Bernoulli numbers",
        "difficulty": "pathological",
        "rationale": "sin(z)^10 has a zero of order 10 at z=0, so 1/sin(z)^10 has a pole of order 10. "
                    "The Laurent coefficients involve complicated combinations of Bernoulli numbers. "
                    "Both derivative formula and contour integration fail numerically."
    },
    {
        "test_id": "CPLX_018",
        "category": "residue_calculus",
        "input": "Compute Res((z^2 + 1)^6 / (z^2 - 1)^7, z=1)",
        "expected": "Seventh-order pole, requires 6th derivative of (z-1)^7 * f(z)",
        "difficulty": "extreme",
        "rationale": "The numerator (z^2+1)^6 is a polynomial of degree 12, the denominator has "
                    "seventh-order poles at z=+/-1. Near z=1, we need 6th derivative of "
                    "((z-1)^7 * (z^2+1)^6) / ((z-1)^7(z+1)^7) evaluated at z=1."
    },
    {
        "test_id": "CPLX_019",
        "category": "residue_calculus",
        "input": "Compute Res(cot(z)^6, z=0)",
        "expected": "Sixth power of simple pole gives pole of order 6, coefficient involves Bernoulli",
        "difficulty": "brutal",
        "rationale": "cot(z) = cos(z)/sin(z) has a simple pole at z=0. The sixth power has a pole "
                    "of order 6. The residue calculation involves the Laurent series of cot(z) "
                    "raised to the sixth power - a combinatorial nightmare."
    },
    {
        "test_id": "CPLX_020",
        "category": "residue_calculus",
        "input": "Compute Res(Gamma(z) * Gamma(1-z), z=n) for integer n, verify with Euler reflection",
        "expected": "Res = (-1)^n / n! at positive integers, pole structure from pi/sin(pi*z)",
        "difficulty": "brutal",
        "rationale": "By Euler reflection, Gamma(z)*Gamma(1-z) = pi/sin(pi*z), which has simple poles "
                    "at all integers with residues (-1)^n/pi * pi = (-1)^n. Tests special function "
                    "pole detection against closed-form result."
    },
]

# =============================================================================
# CATEGORY 3: MOBIUS TRANSFORMATIONS WITH PATHOLOGICAL FIXED POINTS (5 tests)
# =============================================================================

MOBIUS_FIXED_POINT_TESTS = [
    {
        "test_id": "CPLX_021",
        "category": "conformal_mapping",
        "input": "Mobius transformation with fixed points at z = (1 +/- 1e-15*i), map z=0 to w=1",
        "expected": "Nearly coincident fixed points cause numerical instability in conjugacy to translation",
        "difficulty": "extreme",
        "rationale": "When two fixed points z1, z2 are nearly equal, the Mobius transformation is nearly "
                    "a translation (parabolic). The conjugacy phi that makes phi^{-1} o T o phi = z + c "
                    "becomes extremely ill-conditioned. Small errors in fixed point computation cause "
                    "large errors in the transformation matrix."
    },
    {
        "test_id": "CPLX_022",
        "category": "conformal_mapping",
        "input": "Construct Mobius map from (0, 1, infinity) to (1e-16, 1+1e-16, infinity-1e-16i)",
        "expected": "Nearly identity transformation with severe numerical precision requirements",
        "difficulty": "pathological",
        "rationale": "The three-point construction requires solving a system where the differences between "
                    "source and target points are at machine epsilon scale. The resulting transformation "
                    "coefficients have relative errors of O(1) despite the map being nearly identity."
    },
    {
        "test_id": "CPLX_023",
        "category": "conformal_mapping",
        "input": "Compose 100 Mobius transformations T_k(z) = (z + 1/k) / (z*1/k + 1), verify result",
        "expected": "Composition is still Mobius; accumulated numerical error in 2x2 matrix multiplication",
        "difficulty": "brutal",
        "rationale": "Each T_k is a disk automorphism. The 2x2 matrix representation accumulates error "
                    "through 100 multiplications. The determinant should remain 1, but numerical "
                    "drift causes the result to not preserve the unit circle."
    },
    {
        "test_id": "CPLX_024",
        "category": "conformal_mapping",
        "input": "Find Mobius automorphism of unit disk with multiplier exp(2*pi*i*(1+sqrt(5))/2) at z=0",
        "expected": "Irrational rotation by golden angle; orbit is dense in unit circle",
        "difficulty": "brutal",
        "rationale": "The golden angle rotation never returns to its starting point. Verifying properties "
                    "like angle-preservation requires testing on a dense set of points, but finite "
                    "sampling always misses the dense orbit structure."
    },
    {
        "test_id": "CPLX_025",
        "category": "conformal_mapping",
        "input": "Mobius transformation determinant normalization: (a,b,c,d) = (1e100, 1e100, 1e-100, 1e-100)",
        "expected": "ad - bc = 1e0, but floating point gives overflow/underflow in naive computation",
        "difficulty": "extreme",
        "rationale": "The determinant ad-bc involves catastrophic cancellation when a,d are huge and b,c "
                    "are tiny. Standard IEEE 754 arithmetic gives infinity - infinity = NaN. Proper "
                    "implementation requires logarithmic scaling or extended precision."
    },
]

# =============================================================================
# CATEGORY 4: SCHWARZ-CHRISTOFFEL FOR PATHOLOGICAL POLYGONS (5 tests)
# =============================================================================

SCHWARZ_CHRISTOFFEL_TESTS = [
    {
        "test_id": "CPLX_026",
        "category": "conformal_mapping",
        "input": "SC mapping to rectangle with aspect ratio 1000:1 (nearly degenerate strip)",
        "expected": "Prevertex parameters cluster near 0 and 1, causing numerical integration failure",
        "difficulty": "pathological",
        "rationale": "For extreme aspect ratios, the Schwarz-Christoffel prevertices on the real line "
                    "cluster together. The integrand (z-x1)^{-1/2}(z-x2)^{-1/2}... has near-coincident "
                    "branch points, making numerical integration impossible near these points."
    },
    {
        "test_id": "CPLX_027",
        "category": "conformal_mapping",
        "input": "SC mapping to L-shaped polygon with interior angle 3*pi/2 at the corner",
        "expected": "Exponent beta = 3/2 - 1 = 1/2 gives integrable singularity but slow convergence",
        "difficulty": "brutal",
        "rationale": "The reflex angle (3*pi/2) creates a branch point in the SC integrand with exponent 1/2. "
                    "The square-root singularity is integrable but requires specialized quadrature. "
                    "Standard trapezoidal rule gives O(1/sqrt(N)) convergence instead of O(1/N^2)."
    },
    {
        "test_id": "CPLX_028",
        "category": "conformal_mapping",
        "input": "SC mapping to regular 100-gon with interior angles 98*pi/100",
        "expected": "100 prevertices, nearly uniform but parameter problem is highly nonlinear",
        "difficulty": "extreme",
        "rationale": "Finding the 100 prevertex positions requires solving a 97-dimensional nonlinear "
                    "system (three can be fixed). The Jacobian of this system is ill-conditioned for "
                    "nearly-circular polygons where the solution is close to a singularity of the mapping."
    },
    {
        "test_id": "CPLX_029",
        "category": "conformal_mapping",
        "input": "SC mapping to triangle with angles pi*(1 - 1e-8), pi*(1e-8), pi*(1e-8 - epsilon)",
        "expected": "Nearly-degenerate triangle, two angles approach 0, one approaches pi",
        "difficulty": "pathological",
        "rationale": "This 'sliver' triangle has angles summing to pi but two angles are effectively 0. "
                    "The SC exponents are beta ~ -1 + 1e-8, 1e-8 - 1, 1e-8 - 1. The near-logarithmic "
                    "singularities (beta ~ -1) cause the integral to diverge logarithmically."
    },
    {
        "test_id": "CPLX_030",
        "category": "conformal_mapping",
        "input": "SC mapping to polygon with two parallel sides separated by distance 1e-10",
        "expected": "Nearly-degenerate channel region, conformal modulus approaches infinity",
        "difficulty": "pathological",
        "rationale": "When two sides are nearly parallel and close together, the polygon degenerates to a "
                    "slit. The conformal module of the resulting region diverges, and the prevertex "
                    "parameter problem becomes singular. The mapping approaches a Koebe slit mapping."
    },
]

# =============================================================================
# CATEGORY 5: CONTOUR INTEGRALS AROUND BRANCH CUTS (5 tests)
# =============================================================================

BRANCH_CUT_CONTOUR_TESTS = [
    {
        "test_id": "CPLX_031",
        "category": "contour_integration",
        "input": "Integral of sqrt(z)/(z^2 + 1) around keyhole contour, branch cut on positive real axis",
        "expected": "2*pi*i * (Res at i * contribution from branch cut discontinuity)",
        "difficulty": "brutal",
        "rationale": "The integrand is multi-valued due to sqrt(z). The keyhole contour goes around the "
                    "branch cut, picking up the discontinuity sqrt(z)|_{upper} - sqrt(z)|_{lower} = 2i*sqrt(x) "
                    "for x > 0. The pole at z=i contributes 2*pi*i * sqrt(i)/(2i)."
    },
    {
        "test_id": "CPLX_032",
        "category": "contour_integration",
        "input": "Integral of log(z)/(z^2 + 1) around unit circle (crosses branch cut)",
        "expected": "Result depends on how contour crosses branch cut; discontinuity contributes",
        "difficulty": "extreme",
        "rationale": "The unit circle crosses the negative real axis (standard branch cut for log). "
                    "As the contour crosses, log jumps by 2*pi*i. The integral is NOT just 2*pi*i*Res "
                    "but includes the branch cut contribution. Many implementations get this wrong."
    },
    {
        "test_id": "CPLX_033",
        "category": "contour_integration",
        "input": "Integral of z^{1/3} / (z - 1) around |z| = 2, branch cut from 0 to -infinity",
        "expected": "Include contributions from pole at z=1 and branch point handling",
        "difficulty": "brutal",
        "rationale": "z^{1/3} has a branch point at z=0. With branch cut on negative real axis, the "
                    "function is single-valued in |z| < 2 minus the cut. The contour doesn't cross "
                    "the cut, so standard residue theorem applies: 2*pi*i * 1^{1/3} = 2*pi*i."
    },
    {
        "test_id": "CPLX_034",
        "category": "contour_integration",
        "input": "Integral of sqrt((z-1)(z+1)) / z around |z| = 2",
        "expected": "Branch cut from -1 to 1, contour encloses cut, requires dogbone/Pochhammer",
        "difficulty": "pathological",
        "rationale": "sqrt((z-1)(z+1)) = sqrt(z^2-1) has branch points at z = +/- 1 with a cut between them. "
                    "The |z|=2 contour encloses both branch points. The integral requires deforming to "
                    "a dogbone contour around the cut, and the answer involves complete elliptic integrals."
    },
    {
        "test_id": "CPLX_035",
        "category": "contour_integration",
        "input": "Integral of (log(z))^3 / (z^2 + 1) along real axis from 0 to infinity",
        "expected": "Use keyhole contour, branch cut contributions are crucial",
        "difficulty": "extreme",
        "rationale": "Converting the real integral to a contour integral requires a keyhole around the "
                    "branch cut [0, infinity). The (log z)^3 creates a third-order discontinuity across "
                    "the cut. The calculation involves pi^3 and pi*log^2 terms from expansion."
    },
]

# =============================================================================
# CATEGORY 6: ARGUMENT PRINCIPLE FOR CLUSTERED ZEROS (5 tests)
# =============================================================================

ARGUMENT_PRINCIPLE_TESTS = [
    {
        "test_id": "CPLX_036",
        "category": "residue_calculus",
        "input": "Count zeros of z^20 - 1 + 1e-15*z in |z| < 1.1 using argument principle",
        "expected": "20 zeros (roots of unity perturbed), argument principle should give N - P = 20",
        "difficulty": "brutal",
        "rationale": "The polynomial z^20 - 1 + epsilon*z has 20 zeros near the 20th roots of unity. "
                    "The tiny perturbation shifts zeros by O(epsilon^{1/20}). Detecting all 20 via "
                    "winding number requires very fine contour sampling since zeros are closely spaced."
    },
    {
        "test_id": "CPLX_037",
        "category": "residue_calculus",
        "input": "Count zeros of exp(z) - 1 - z - z^2/2 in |z| < 10 using argument principle",
        "expected": "Infinitely many zeros! (Actually finite in bounded region)",
        "difficulty": "extreme",
        "rationale": "exp(z) - 1 - z - z^2/2 = z^3/6 + z^4/24 + ... has a triple zero at z=0. "
                    "For large |z|, exp(z) dominates in Re(z) > 0 and is small in Re(z) < 0. "
                    "The number of zeros in |z| < 10 requires careful argument principle application."
    },
    {
        "test_id": "CPLX_038",
        "category": "residue_calculus",
        "input": "Count zeros of sin(100*z) in the square [0,1] x [0,1] using argument principle",
        "expected": "Approximately 100/pi * sqrt(2) zeros; need rectangular contour integration",
        "difficulty": "brutal",
        "rationale": "sin(100*z) has zeros at z = n*pi/100 for integer n. In the square [0,1]^2, "
                    "we need zeros with real and imaginary parts in [0,1]. For real z, there are "
                    "about 100/pi ~ 31 zeros in [0,1]. The rectangular contour argument principle "
                    "must handle the rapid oscillation of sin(100*z)."
    },
    {
        "test_id": "CPLX_039",
        "category": "residue_calculus",
        "input": "Count zeros minus poles of tan(z)/sin(2*z) in |z| < 5",
        "expected": "tan(z) poles at (2n+1)*pi/2, sin(2z) zeros at n*pi/2; net count requires care",
        "difficulty": "extreme",
        "rationale": "tan(z) = sin(z)/cos(z) has poles where cos(z) = 0. sin(2*z) = 2*sin(z)*cos(z). "
                    "So tan(z)/sin(2*z) = 1/(2*sin(z)*cos^2(z)). This has poles at zeros of sin and cos, "
                    "but with different orders. The argument principle must account for all multiplicities."
    },
    {
        "test_id": "CPLX_040",
        "category": "residue_calculus",
        "input": "Count zeros of Riemann zeta in critical strip 0 < Re(s) < 1, 0 < Im(s) < 100",
        "expected": "Approximately 29 zeros on critical line (by Riemann-von Mangoldt formula)",
        "difficulty": "pathological",
        "rationale": "The zeta function zeros on the critical line are the subject of the Riemann Hypothesis. "
                    "Counting zeros uses N(T) ~ (T/2*pi)*log(T/2*pi) - T/2*pi + O(log T). For T=100, "
                    "N(100) ~ 29. Verifying this numerically requires high-precision zeta evaluation."
    },
]

# =============================================================================
# CATEGORY 7: ANALYTIC CONTINUATION ACROSS NATURAL BOUNDARIES (5 tests)
# =============================================================================

ANALYTIC_CONTINUATION_TESTS = [
    {
        "test_id": "CPLX_041",
        "category": "analytic_functions",
        "input": "Analytically continue sum_{n=0}^infinity z^{2^n} beyond unit disk",
        "expected": "IMPOSSIBLE - unit circle is natural boundary (Hadamard gap theorem)",
        "difficulty": "pathological",
        "rationale": "The lacunary series with gaps 2^n satisfies Hadamard's gap theorem: if a_n != 0 "
                    "only for n = n_k with n_{k+1}/n_k > 1 + epsilon, then the circle of convergence "
                    "is a natural boundary. No analytic continuation exists across |z| = 1."
    },
    {
        "test_id": "CPLX_042",
        "category": "analytic_functions",
        "input": "Analytically continue sum_{n=1}^infinity z^n / n! from |z| < 1 to all of C",
        "expected": "exp(z) - 1, entire function, continuation is trivial",
        "difficulty": "brutal",
        "rationale": "This series converges everywhere, so 'continuation' is just re-summing. However, "
                    "numerical continuation via power series chaining accumulates errors. The test is "
                    "whether the system recognizes this as exp(z) - 1 and uses the entire extension."
    },
    {
        "test_id": "CPLX_043",
        "category": "analytic_functions",
        "input": "Analytically continue sqrt(z) from Re(z) > 0 to Re(z) < 0 along path through upper half-plane",
        "expected": "sqrt(z) = i*sqrt(|z|) for z on negative real axis (approached from above)",
        "difficulty": "extreme",
        "rationale": "sqrt(z) is multi-valued. Continuing along a path through Im(z) > 0 gives a different "
                    "value than continuing through Im(z) < 0. The system must track the branch and give "
                    "sqrt(-1) = +i (not -i) when approaching from above."
    },
    {
        "test_id": "CPLX_044",
        "category": "analytic_functions",
        "input": "Continue modular lambda function from upper half-plane through cusp at infinity",
        "expected": "lambda(tau) -> 0 as tau -> i*infinity, continuation involves modular group",
        "difficulty": "pathological",
        "rationale": "The modular lambda function has natural boundary at the real axis (except cusps). "
                    "Continuing through the cusp at infinity to another fundamental domain requires "
                    "applying modular transformations. This is a classic example of functional equations "
                    "enabling continuation beyond natural boundaries."
    },
    {
        "test_id": "CPLX_045",
        "category": "analytic_functions",
        "input": "Analytically continue sum_{n=1}^infinity (-1)^n * z^n / n along path crossing unit circle",
        "expected": "-log(1+z), but crossing |z|=1 requires path not through z=-1",
        "difficulty": "brutal",
        "rationale": "This is the Taylor series for -log(1+z) around z=0. The function has a branch "
                    "point at z=-1 and is analytic in C minus (-infinity, -1]. Continuation across "
                    "|z|=1 is possible except through z=-1. Path dependence must be tracked."
    },
]

# =============================================================================
# CATEGORY 8: CAUCHY-RIEMANN AT NON-DIFFERENTIABLE POINTS (5 tests)
# =============================================================================

CAUCHY_RIEMANN_EDGE_TESTS = [
    {
        "test_id": "CPLX_046",
        "category": "analytic_functions",
        "input": "Verify Cauchy-Riemann for f(z) = |z|^2 at z = 0 only",
        "expected": "C-R satisfied at z=0 but f is not analytic (not differentiable elsewhere)",
        "difficulty": "brutal",
        "rationale": "f(z) = |z|^2 = x^2 + y^2 satisfies u_x = 2x = v_y = 0 and u_y = 2y = -v_x = 0 "
                    "only at the origin. This is a classic counterexample: satisfying C-R at a point "
                    "is not sufficient for analyticity. The system must detect this pathology."
    },
    {
        "test_id": "CPLX_047",
        "category": "analytic_functions",
        "input": "Verify Cauchy-Riemann for f(z) = z*conj(z)^2 / |z|^3 for z != 0, f(0) = 0",
        "expected": "C-R satisfied at z=0 but function is not even continuous at 0",
        "difficulty": "extreme",
        "rationale": "This function approaches different limits along different paths to 0. "
                    "It is not continuous at 0, let alone differentiable. But formally computing "
                    "u_x, u_y, v_x, v_y at z=0 via limits gives 0 = 0 for both C-R equations. "
                    "Pure C-R checking fails to detect this pathology."
    },
    {
        "test_id": "CPLX_048",
        "category": "analytic_functions",
        "input": "Verify Cauchy-Riemann for f(z) = exp(-1/z^4) for z != 0, f(0) = 0",
        "expected": "C^infinity at z=0 but not analytic! All derivatives are 0 at z=0",
        "difficulty": "pathological",
        "rationale": "This function is C^infinity (infinitely differentiable as a real function) "
                    "but not analytic at z=0. The Taylor series at z=0 is identically 0, but the "
                    "function is not 0. This is a complex analogue of the real function e^{-1/x^2}. "
                    "The system should identify this as C^infinity but not holomorphic."
    },
    {
        "test_id": "CPLX_049",
        "category": "analytic_functions",
        "input": "Verify analyticity of f(z) = sum_{n=1}^N z^n * exp(-n*|z|^2) as N -> infinity",
        "expected": "Each partial sum is C^infinity but not analytic; limit is worse",
        "difficulty": "extreme",
        "rationale": "Each term z^n * exp(-n*|z|^2) involves |z|^2 = z*conj(z), making it non-analytic. "
                    "The sum is C^infinity but nowhere analytic. Testing C-R numerically appears to "
                    "pass due to smooth behavior, but the function contains conj(z) dependence."
    },
    {
        "test_id": "CPLX_050",
        "category": "analytic_functions",
        "input": "Verify analyticity of real-analytic function u(x,y) = x^3 - 3*x*y^2 + harmonic conjugate",
        "expected": "u is harmonic, conjugate is v = 3*x^2*y - y^3, f = u + i*v = z^3 is analytic",
        "difficulty": "brutal",
        "rationale": "Starting from the real part u = Re(z^3), we must find the harmonic conjugate v "
                    "satisfying C-R. The conjugate is unique up to a constant. Verifying that "
                    "u + i*v = z^3 requires symbolic manipulation. Numerical verification must handle "
                    "the polynomial growth at large |z|."
    },
]

# =============================================================================
# COMBINE ALL TESTS
# =============================================================================

COMPLEX_ANALYSIS_STRESS_TESTS = (
    LAURENT_ESSENTIAL_SINGULARITY_TESTS +    # 10 tests (CPLX_001-010)
    RESIDUE_HIGH_ORDER_POLE_TESTS +          # 10 tests (CPLX_011-020)
    MOBIUS_FIXED_POINT_TESTS +               # 5 tests  (CPLX_021-025)
    SCHWARZ_CHRISTOFFEL_TESTS +              # 5 tests  (CPLX_026-030)
    BRANCH_CUT_CONTOUR_TESTS +               # 5 tests  (CPLX_031-035)
    ARGUMENT_PRINCIPLE_TESTS +               # 5 tests  (CPLX_036-040)
    ANALYTIC_CONTINUATION_TESTS +            # 5 tests  (CPLX_041-045)
    CAUCHY_RIEMANN_EDGE_TESTS                # 5 tests  (CPLX_046-050)
)  # Total: 50 tests

# Category mapping for analysis
CATEGORIES = {
    "laurent_series": LAURENT_ESSENTIAL_SINGULARITY_TESTS,
    "residue_calculus": RESIDUE_HIGH_ORDER_POLE_TESTS + ARGUMENT_PRINCIPLE_TESTS,
    "conformal_mapping": MOBIUS_FIXED_POINT_TESTS + SCHWARZ_CHRISTOFFEL_TESTS,
    "contour_integration": BRANCH_CUT_CONTOUR_TESTS,
    "analytic_functions": ANALYTIC_CONTINUATION_TESTS + CAUCHY_RIEMANN_EDGE_TESTS,
}

# Difficulty distribution
DIFFICULTY_COUNTS = {
    "brutal": sum(1 for t in COMPLEX_ANALYSIS_STRESS_TESTS if t["difficulty"] == "brutal"),
    "extreme": sum(1 for t in COMPLEX_ANALYSIS_STRESS_TESTS if t["difficulty"] == "extreme"),
    "pathological": sum(1 for t in COMPLEX_ANALYSIS_STRESS_TESTS if t["difficulty"] == "pathological"),
}

# Specialist targeting
SPECIALIST_TARGETS = {
    "AnalyticFunctionsSpecialist": [
        t for t in COMPLEX_ANALYSIS_STRESS_TESTS
        if t["category"] in ["laurent_series", "analytic_functions"]
    ],
    "ResidueCalculusSpecialist": [
        t for t in COMPLEX_ANALYSIS_STRESS_TESTS
        if t["category"] == "residue_calculus"
    ],
    "ConformalMappingSpecialist": [
        t for t in COMPLEX_ANALYSIS_STRESS_TESTS
        if t["category"] == "conformal_mapping"
    ],
    "ContourIntegrationSpecialist": [
        t for t in COMPLEX_ANALYSIS_STRESS_TESTS
        if t["category"] == "contour_integration"
    ],
}


def get_all_tests() -> List[Dict[str, Any]]:
    """Return all 50 complex analysis stress tests."""
    return COMPLEX_ANALYSIS_STRESS_TESTS


def get_tests_by_category(category: str) -> List[Dict[str, Any]]:
    """Get tests for a specific category."""
    return CATEGORIES.get(category, [])


def get_tests_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Get tests at a specific difficulty level."""
    return [t for t in COMPLEX_ANALYSIS_STRESS_TESTS if t["difficulty"] == difficulty]


def get_tests_for_specialist(specialist_name: str) -> List[Dict[str, Any]]:
    """Get tests targeting a specific specialist."""
    return SPECIALIST_TARGETS.get(specialist_name, [])


def print_test_summary():
    """Print summary statistics for the test suite."""
    print("=" * 70)
    print("COMPLEX ANALYSIS STRESS TEST SUITE - SUMMARY")
    print("=" * 70)
    print(f"\nTotal tests: {len(COMPLEX_ANALYSIS_STRESS_TESTS)}")
    print(f"\nDifficulty distribution:")
    for diff, count in DIFFICULTY_COUNTS.items():
        print(f"  {diff}: {count} tests")
    print(f"\nCategory distribution:")
    for cat, tests in CATEGORIES.items():
        print(f"  {cat}: {len(tests)} tests")
    print(f"\nSpecialist targeting:")
    for spec, tests in SPECIALIST_TARGETS.items():
        print(f"  {spec}: {len(tests)} tests")
    print("=" * 70)


if __name__ == "__main__":
    print_test_summary()
    print("\nSample test (CPLX_001):")
    print(COMPLEX_ANALYSIS_STRESS_TESTS[0])
