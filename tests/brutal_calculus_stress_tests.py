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
BRUTAL CALCULUS STRESS TESTS - 50 RESEARCH-LEVEL PROBLEMS
==========================================================

These tests are specifically designed to BREAK the calculus domain specialists:
- DifferentiationSpecialist
- IntegrationSpecialist
- LimitEvaluator
- ODESolutionSpecialist
- SeriesSpecialist
- FourierAnalysisSpecialist
- SpecialFunctionsSpecialist

Each test exploits known weaknesses in symbolic computation systems:
- Deep composition chains exceeding recursion limits
- Obscure substitution patterns not in standard tables
- Essential singularities with chaotic behavior
- Stiff ODEs requiring adaptive stepsize
- Slowly convergent series requiring acceleration
- Distributional Fourier transforms
- Branch cuts and multi-valued functions
- L'Hopital cascades requiring many iterations
- Oscillatory improper integrals (Riemann-Lebesgue)
- Path-dependent multivariable limits

DIFFICULTY LEVELS:
- brutal: Will likely fail or produce wrong answer
- extreme: Requires advanced techniques not commonly implemented
- pathological: Mathematically adversarial edge cases
"""

import math

# =============================================================================
# THE 50 BRUTAL CALCULUS STRESS TESTS
# =============================================================================

BRUTAL_CALCULUS_STRESS_TESTS = [
    # =========================================================================
    # CATEGORY 1: DEEPLY NESTED COMPOSITIONS (DIFFERENTIATION)
    # Tests 001-005: Chain rule stress tests with 10-25 nested functions
    # =========================================================================
    {
        "test_id": "CALC_001",
        "category": "nested_differentiation",
        "input": "d/dx[sin(cos(tan(exp(ln(sqrt(arctan(arcsin(arccos(x)))))))))]",
        "expected": "complex_chain_rule_expression",
        "difficulty": "brutal",
        "rationale": "10-level nested composition requiring 10 chained applications of the chain rule. Most symbolic engines will either hit recursion limits or produce unmanageably large expressions that fail to simplify."
    },
    {
        "test_id": "CALC_002",
        "category": "nested_differentiation",
        "input": "d/dx[exp(sin(cos(tan(sec(csc(cot(sinh(cosh(tanh(x)))))))))))]",
        "expected": "product_of_10_derivative_factors",
        "difficulty": "brutal",
        "rationale": "10 trig/hyperbolic functions nested. The chain rule produces a product of 10 terms, each involving derivatives of trig functions evaluated at nested arguments. Expression explosion is guaranteed."
    },
    {
        "test_id": "CALC_003",
        "category": "nested_differentiation",
        "input": "d/dx[ln(ln(ln(ln(ln(ln(ln(ln(ln(ln(x+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)]",
        "expected": "iterated_reciprocal_product",
        "difficulty": "extreme",
        "rationale": "10 nested logarithms with offsets. The derivative involves a product of 10 reciprocals of nested log expressions. Tests both recursion depth and symbolic simplification of log derivatives."
    },
    {
        "test_id": "CALC_004",
        "category": "nested_differentiation",
        "input": "d^20/dx^20[sin(sin(sin(sin(sin(x)))))]",
        "expected": "20th_derivative_of_5_nested_sines",
        "difficulty": "pathological",
        "rationale": "20th derivative of 5 nested sines. The Faa di Bruno formula for higher derivatives of compositions produces combinatorial explosion with Bell polynomials."
    },
    {
        "test_id": "CALC_005",
        "category": "nested_differentiation",
        "input": "d/dx[(x^(x^(x^(x^x))))]",
        "expected": "power_tower_derivative",
        "difficulty": "extreme",
        "rationale": "5-level power tower (tetration). Requires logarithmic differentiation applied recursively. The derivative involves the power tower itself multiplied by a sum of logarithmic terms."
    },

    # =========================================================================
    # CATEGORY 2: OBSCURE INTEGRATION SUBSTITUTIONS
    # Tests 006-012: Integrals requiring Weierstrass, Euler, and exotic methods
    # =========================================================================
    {
        "test_id": "CALC_006",
        "category": "obscure_integration",
        "input": "integrate(1/(2+cos(x)), x)",
        "expected": "(2/sqrt(3))*arctan(tan(x/2)/sqrt(3))",
        "difficulty": "brutal",
        "rationale": "Requires Weierstrass substitution t=tan(x/2). The resulting rational function integral is non-trivial. Most pattern-based integrators miss this."
    },
    {
        "test_id": "CALC_007",
        "category": "obscure_integration",
        "input": "integrate(sqrt(tan(x)), x)",
        "expected": "(1/sqrt(2))*(arctan((tan(x)-1)/(sqrt(2*tan(x)))) - arctanh((tan(x)+1)/(sqrt(2*tan(x)))))",
        "difficulty": "extreme",
        "rationale": "Requires substitution u=sqrt(tan(x)), then partial fractions on a quartic. One of the notorious integrals that breaks standard CAS systems."
    },
    {
        "test_id": "CALC_008",
        "category": "obscure_integration",
        "input": "integrate(x^x*(1+ln(x)), x)",
        "expected": "x^x + C",
        "difficulty": "brutal",
        "rationale": "Recognizing that d/dx[x^x] = x^x*(1+ln(x)) requires pattern matching on logarithmic derivatives. Most integrators fail to recognize this as a perfect derivative."
    },
    {
        "test_id": "CALC_009",
        "category": "obscure_integration",
        "input": "integrate(1/(x^5+1), x)",
        "expected": "partial_fractions_over_cyclotomic_roots",
        "difficulty": "extreme",
        "rationale": "Requires factoring x^5+1 over cyclotomic fields and partial fractions with 5th roots of unity. The result involves logarithms and arctangents with algebraic coefficients."
    },
    {
        "test_id": "CALC_010",
        "category": "obscure_integration",
        "input": "integrate(exp(-x^2)*erf(x), x)",
        "expected": "sqrt(pi)/2 * erf(x)^2 + C",
        "difficulty": "brutal",
        "rationale": "Requires recognizing the derivative of erf(x)^2 pattern. Special function integration is rarely implemented outside specialized CAS."
    },
    {
        "test_id": "CALC_011",
        "category": "obscure_integration",
        "input": "integrate(ln(ln(x))/x, x)",
        "expected": "ln(x)*ln(ln(x)) - li(x) + C",
        "difficulty": "extreme",
        "rationale": "Requires integration by parts and introduces the logarithmic integral li(x). Tests special function handling."
    },
    {
        "test_id": "CALC_012",
        "category": "obscure_integration",
        "input": "integrate(x^n*exp(-x), x, 0, inf)",
        "expected": "Gamma(n+1) = n!",
        "difficulty": "brutal",
        "rationale": "The defining integral for the Gamma function. Requires recognizing the pattern and applying Gamma function properties for symbolic n."
    },

    # =========================================================================
    # CATEGORY 3: ESSENTIAL SINGULARITIES
    # Tests 013-018: Limits at essential singularities with chaotic behavior
    # =========================================================================
    {
        "test_id": "CALC_013",
        "category": "essential_singularity",
        "input": "limit(exp(1/x)*sin(1/x), x, 0)",
        "expected": "does_not_exist",
        "difficulty": "brutal",
        "rationale": "Product of exponential growth and bounded oscillation at essential singularity. The limit does not exist (different limits along different paths)."
    },
    {
        "test_id": "CALC_014",
        "category": "essential_singularity",
        "input": "limit(x^x, x, 0, '+')",
        "expected": "1",
        "difficulty": "brutal",
        "rationale": "0^0 indeterminate form. Requires rewriting as exp(x*ln(x)) and evaluating lim x*ln(x) = 0. Tests handling of 0^0 convention."
    },
    {
        "test_id": "CALC_015",
        "category": "essential_singularity",
        "input": "limit(sin(exp(1/x^2)), x, 0)",
        "expected": "does_not_exist",
        "difficulty": "pathological",
        "rationale": "The argument exp(1/x^2) goes to infinity super-exponentially fast, causing sin to oscillate infinitely rapidly. Classic example of essential singularity chaos."
    },
    {
        "test_id": "CALC_016",
        "category": "essential_singularity",
        "input": "limit((1 + 1/x)^(x^2), x, inf)",
        "expected": "exp(inf) = inf",
        "difficulty": "extreme",
        "rationale": "Generalization of (1+1/x)^x -> e. Here the exponent is x^2, so the limit is exp(x) -> inf. Tests understanding of exponential limit asymptotics."
    },
    {
        "test_id": "CALC_017",
        "category": "essential_singularity",
        "input": "limit(x^(1/ln(x)), x, 0, '+')",
        "expected": "e",
        "difficulty": "brutal",
        "rationale": "Rewrite as exp(ln(x)/ln(x)) = exp(1) = e. The form 0^inf is deceptively simple but requires careful algebraic manipulation."
    },
    {
        "test_id": "CALC_018",
        "category": "essential_singularity",
        "input": "limit(exp(-1/x^2)/(x^100), x, 0)",
        "expected": "0",
        "difficulty": "pathological",
        "rationale": "Tests that exp(-1/x^2) decays faster than any polynomial x^(-n) grows. The exp beats x^100 term. Classical flat function example."
    },

    # =========================================================================
    # CATEGORY 4: STIFF ODEs REQUIRING ADAPTIVE METHODS
    # Tests 019-024: ODEs with vastly different timescales
    # =========================================================================
    {
        "test_id": "CALC_019",
        "category": "stiff_ode",
        "input": "y' = -1000*y + 3000 - 2000*exp(-x), y(0) = 0",
        "expected": "y = 3 - 0.998*exp(-1000*x) - 2.002*exp(-x)",
        "difficulty": "brutal",
        "rationale": "Classic stiff ODE with eigenvalues -1000 and -1. The fast transient e^(-1000x) decays 1000x faster than e^(-x). Standard RK4 requires tiny steps."
    },
    {
        "test_id": "CALC_020",
        "category": "stiff_ode",
        "input": "y'' + 1001*y' + 1000*y = 0, y(0)=1, y'(0)=-1",
        "expected": "y = (1/999)*(1000*exp(-x) - exp(-1000*x))",
        "difficulty": "extreme",
        "rationale": "Second-order stiff ODE. Characteristic roots -1 and -1000 require implicit methods for stability. Tests numerical ODE solver robustness."
    },
    {
        "test_id": "CALC_021",
        "category": "stiff_ode",
        "input": "y' = y^2 - y^3, y(0) = delta",
        "expected": "blowup_time_depends_on_delta",
        "difficulty": "pathological",
        "rationale": "Robertson problem simplified. Has stable equilibrium at y=1 but trajectory depends sensitively on initial condition. Tests bifurcation handling."
    },
    {
        "test_id": "CALC_022",
        "category": "stiff_ode",
        "input": "y' = -15*y, y(0) = 1, solve on [0, 1] with h=0.5",
        "expected": "unstable_with_explicit_euler",
        "difficulty": "brutal",
        "rationale": "Explicit Euler requires h < 2/15 for stability. With h=0.5, the method is unstable and blows up. Tests stability region awareness."
    },
    {
        "test_id": "CALC_023",
        "category": "stiff_ode",
        "input": "system: y1' = -0.04*y1 + 10^4*y2*y3, y2' = 0.04*y1 - 10^4*y2*y3 - 3*10^7*y2^2, y3' = 3*10^7*y2^2",
        "expected": "robertson_chemical_kinetics",
        "difficulty": "pathological",
        "rationale": "Robertson chemical kinetics problem. Stiffness ratio of 10^11. Standard benchmark for stiff ODE solvers. Explicit methods completely fail."
    },
    {
        "test_id": "CALC_024",
        "category": "stiff_ode",
        "input": "van_der_pol: y'' - mu*(1-y^2)*y' + y = 0, mu = 1000, y(0) = 2, y'(0) = 0",
        "expected": "relaxation_oscillation",
        "difficulty": "extreme",
        "rationale": "Van der Pol oscillator with extreme stiffness (mu=1000). Exhibits relaxation oscillations with sharp transitions. BDF methods required."
    },

    # =========================================================================
    # CATEGORY 5: SLOWLY CONVERGENT SERIES
    # Tests 025-030: Series requiring acceleration or special summation
    # =========================================================================
    {
        "test_id": "CALC_025",
        "category": "slow_series",
        "input": "sum((-1)^n/(2n+1), n=0..inf)",
        "expected": "pi/4",
        "difficulty": "brutal",
        "rationale": "Leibniz formula for pi/4. Converges as O(1/n), requiring millions of terms for 6 decimal places. Tests series acceleration (Euler transform)."
    },
    {
        "test_id": "CALC_026",
        "category": "slow_series",
        "input": "sum(1/(n^2*(n+1)^2), n=1..inf)",
        "expected": "pi^2/3 - 3",
        "difficulty": "extreme",
        "rationale": "Requires partial fractions and telescoping combined with Basel problem. The closed form is non-obvious and tests algebraic manipulation."
    },
    {
        "test_id": "CALC_027",
        "category": "slow_series",
        "input": "sum(1/(n*ln(n)^2), n=2..inf)",
        "expected": "finite but no closed form",
        "difficulty": "brutal",
        "rationale": "Converges by integral test but has no known closed form. Tests whether system can determine convergence without finding sum value."
    },
    {
        "test_id": "CALC_028",
        "category": "slow_series",
        "input": "sum(sin(n)/n, n=1..inf)",
        "expected": "(pi - 1)/2",
        "difficulty": "extreme",
        "rationale": "Fourier series evaluation at a point. Requires recognizing the series as the Fourier series of a sawtooth evaluated at x=1."
    },
    {
        "test_id": "CALC_029",
        "category": "slow_series",
        "input": "sum((-1)^n/(n^s), n=1..inf) for s=1.0001",
        "expected": "eta(1.0001) = (1-2^(1-s))*zeta(s)",
        "difficulty": "pathological",
        "rationale": "Dirichlet eta function near s=1. Converges extremely slowly (alternating harmonic series perturbation). Tests limit s->1 stability."
    },
    {
        "test_id": "CALC_030",
        "category": "slow_series",
        "input": "sum(1/prime(n), n=1..inf)",
        "expected": "divergent (slowly)",
        "difficulty": "pathological",
        "rationale": "Sum of reciprocals of primes diverges like ln(ln(n)). Tests whether system can detect this extremely slow divergence."
    },

    # =========================================================================
    # CATEGORY 6: DISTRIBUTIONAL FOURIER TRANSFORMS
    # Tests 031-035: Transforms of distributions and generalized functions
    # =========================================================================
    {
        "test_id": "CALC_031",
        "category": "fourier_distribution",
        "input": "fourier_transform(dirac_delta(x), x, k)",
        "expected": "1",
        "difficulty": "brutal",
        "rationale": "F[delta(x)] = 1. Requires distributional Fourier transform theory. Most numerical FFT implementations cannot handle this."
    },
    {
        "test_id": "CALC_032",
        "category": "fourier_distribution",
        "input": "fourier_transform(dirac_delta'(x), x, k)",
        "expected": "i*k",
        "difficulty": "extreme",
        "rationale": "Derivative of delta function. F[delta'(x)] = ik. Tests handling of distributional derivatives."
    },
    {
        "test_id": "CALC_033",
        "category": "fourier_distribution",
        "input": "fourier_transform(heaviside(x), x, k)",
        "expected": "pi*delta(k) + 1/(i*k)",
        "difficulty": "extreme",
        "rationale": "Fourier transform of step function involves both delta and principal value. Tests distribution theory implementation."
    },
    {
        "test_id": "CALC_034",
        "category": "fourier_distribution",
        "input": "fourier_transform(1/x, x, k)",
        "expected": "-i*pi*sign(k)",
        "difficulty": "brutal",
        "rationale": "Principal value distribution 1/x. The transform involves the sign function. Tests Cauchy principal value handling."
    },
    {
        "test_id": "CALC_035",
        "category": "fourier_distribution",
        "input": "fourier_transform(exp(i*omega*x), x, k)",
        "expected": "2*pi*delta(k - omega)",
        "difficulty": "brutal",
        "rationale": "Pure frequency maps to shifted delta. Fundamental result that most FFT implementations handle poorly due to finite sampling."
    },

    # =========================================================================
    # CATEGORY 7: SPECIAL FUNCTIONS AT BRANCH CUTS AND POLES
    # Tests 036-040: Special functions near their singularities
    # =========================================================================
    {
        "test_id": "CALC_036",
        "category": "special_function_singularity",
        "input": "gamma(-2.0000001)",
        "expected": "large_negative_approaching_pole",
        "difficulty": "brutal",
        "rationale": "Gamma function has poles at non-positive integers. Value near -2 tests pole handling and numerical stability."
    },
    {
        "test_id": "CALC_037",
        "category": "special_function_singularity",
        "input": "bessel_J(100, 50)",
        "expected": "requires_asymptotic_expansion",
        "difficulty": "extreme",
        "rationale": "Bessel function with order > argument requires backward recurrence or asymptotic expansion. Forward recurrence is numerically unstable."
    },
    {
        "test_id": "CALC_038",
        "category": "special_function_singularity",
        "input": "elliptic_K(0.9999999)",
        "expected": "large_approaching_infinity",
        "difficulty": "brutal",
        "rationale": "Complete elliptic integral K(m) -> infinity as m -> 1. Tests numerical handling near the logarithmic singularity."
    },
    {
        "test_id": "CALC_039",
        "category": "special_function_singularity",
        "input": "zeta(1 + 10^(-10))",
        "expected": "approximately 10^10 + euler_gamma",
        "difficulty": "pathological",
        "rationale": "Zeta function has pole at s=1 with residue 1. Near s=1, zeta(s) ~ 1/(s-1) + gamma. Tests Laurent expansion accuracy."
    },
    {
        "test_id": "CALC_040",
        "category": "special_function_singularity",
        "input": "polylog(2, exp(i*pi/3))",
        "expected": "Li_2(e^(i*pi/3)) = pi^2/36 + i*Cl_2(pi/3)",
        "difficulty": "extreme",
        "rationale": "Polylogarithm on unit circle involves Clausen function. Tests complex special function evaluation."
    },

    # =========================================================================
    # CATEGORY 8: L'HOPITAL CASCADES
    # Tests 041-044: Indeterminate forms requiring 10+ L'Hopital applications
    # =========================================================================
    {
        "test_id": "CALC_041",
        "category": "lhopital_cascade",
        "input": "limit((exp(x) - sum(x^k/k!, k=0..10)) / x^11, x, 0)",
        "expected": "1/11!",
        "difficulty": "brutal",
        "rationale": "Requires 11 L'Hopital applications to resolve 0/0 form. The Taylor remainder theorem gives the answer directly but L'Hopital must iterate."
    },
    {
        "test_id": "CALC_042",
        "category": "lhopital_cascade",
        "input": "limit((sin(x) - x + x^3/6 - x^5/120) / x^7, x, 0)",
        "expected": "1/5040",
        "difficulty": "extreme",
        "rationale": "Tests 7 applications of L'Hopital after removing known Taylor terms. The limit is the coefficient of x^7 in sin(x) Taylor series."
    },
    {
        "test_id": "CALC_043",
        "category": "lhopital_cascade",
        "input": "limit((1 - cos(sin(x))) / (x^2 * (1 - cos(x))), x, 0)",
        "expected": "1/2",
        "difficulty": "brutal",
        "rationale": "Nested trig functions create compound indeterminate form. Requires careful Taylor expansion or multiple L'Hopital iterations."
    },
    {
        "test_id": "CALC_044",
        "category": "lhopital_cascade",
        "input": "limit((arctan(x) - x + x^3/3 - x^5/5 + x^7/7 - x^9/9) / x^11, x, 0)",
        "expected": "1/11",
        "difficulty": "pathological",
        "rationale": "11 terms of arctan Taylor removed. Must compute 11th derivative accurately or apply L'Hopital 11 times."
    },

    # =========================================================================
    # CATEGORY 9: OSCILLATORY IMPROPER INTEGRALS
    # Tests 045-047: Integrals with oscillating integrands
    # =========================================================================
    {
        "test_id": "CALC_045",
        "category": "oscillatory_integral",
        "input": "integrate(sin(x^2), x, 0, inf)",
        "expected": "sqrt(pi/8)",
        "difficulty": "brutal",
        "rationale": "Fresnel integral. Conditionally convergent oscillatory integral requiring contour integration or stationary phase analysis."
    },
    {
        "test_id": "CALC_046",
        "category": "oscillatory_integral",
        "input": "integrate(sin(x)/x, x, 0, inf)",
        "expected": "pi/2",
        "difficulty": "extreme",
        "rationale": "Dirichlet integral. Conditionally convergent, not absolutely convergent. Classic test of improper integral evaluation."
    },
    {
        "test_id": "CALC_047",
        "category": "oscillatory_integral",
        "input": "integrate(exp(i*x^3), x, -inf, inf)",
        "expected": "2*pi/(3*Gamma(1/3))*exp(i*pi/6)",
        "difficulty": "pathological",
        "rationale": "Airy-type oscillatory integral. Requires steepest descent or stationary phase method. Tests complex contour handling."
    },

    # =========================================================================
    # CATEGORY 10: MULTIVARIABLE PATH-DEPENDENT LIMITS
    # Tests 048-050: Limits in R^n with path-dependent behavior
    # =========================================================================
    {
        "test_id": "CALC_048",
        "category": "multivariable_limit",
        "input": "limit((x*y)/(x^2 + y^2), (x,y), (0,0))",
        "expected": "does_not_exist (path_dependent)",
        "difficulty": "brutal",
        "rationale": "Along y=mx, limit = m/(1+m^2). Different paths give different limits. Classic example of path dependence."
    },
    {
        "test_id": "CALC_049",
        "category": "multivariable_limit",
        "input": "limit((x^2*y)/(x^4 + y^2), (x,y), (0,0))",
        "expected": "does_not_exist (parabolic_path)",
        "difficulty": "extreme",
        "rationale": "Limit is 0 along all straight lines y=mx, but 1/2 along y=x^2. Tests parabolic path analysis."
    },
    {
        "test_id": "CALC_050",
        "category": "multivariable_limit",
        "input": "limit((x^3*y - x*y^3)/(x^2 + y^2)^2, (x,y), (0,0))",
        "expected": "does_not_exist (polar_analysis)",
        "difficulty": "pathological",
        "rationale": "In polar: r*cos(theta)*sin(theta)*(cos^2-sin^2). Oscillates with theta as r->0. Tests polar coordinate limit analysis."
    },
]


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_tests_by_category(category: str):
    """Get all tests in a specific category."""
    return [t for t in BRUTAL_CALCULUS_STRESS_TESTS if t["category"] == category]


def get_tests_by_difficulty(difficulty: str):
    """Get all tests at a specific difficulty level."""
    return [t for t in BRUTAL_CALCULUS_STRESS_TESTS if t["difficulty"] == difficulty]


def get_test_by_id(test_id: str):
    """Get a specific test by ID."""
    for t in BRUTAL_CALCULUS_STRESS_TESTS:
        if t["test_id"] == test_id:
            return t
    return None


def get_category_summary():
    """Get summary of tests per category."""
    categories = {}
    for t in BRUTAL_CALCULUS_STRESS_TESTS:
        cat = t["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "brutal": 0, "extreme": 0, "pathological": 0}
        categories[cat]["count"] += 1
        categories[cat][t["difficulty"]] += 1
    return categories


def print_test_summary():
    """Print a formatted summary of all tests."""
    print("=" * 80)
    print("BRUTAL CALCULUS STRESS TESTS - SUMMARY")
    print("=" * 80)

    summary = get_category_summary()
    for cat, stats in summary.items():
        print(f"\n{cat.upper().replace('_', ' ')}")
        print(f"  Total: {stats['count']} tests")
        print(f"  Brutal: {stats['brutal']}, Extreme: {stats['extreme']}, Pathological: {stats['pathological']}")

    total = len(BRUTAL_CALCULUS_STRESS_TESTS)
    brutal = len([t for t in BRUTAL_CALCULUS_STRESS_TESTS if t["difficulty"] == "brutal"])
    extreme = len([t for t in BRUTAL_CALCULUS_STRESS_TESTS if t["difficulty"] == "extreme"])
    pathological = len([t for t in BRUTAL_CALCULUS_STRESS_TESTS if t["difficulty"] == "pathological"])

    print("\n" + "=" * 80)
    print(f"TOTAL: {total} tests ({brutal} brutal, {extreme} extreme, {pathological} pathological)")
    print("=" * 80)


# =============================================================================
# MAIN - DISPLAY TEST SUMMARY
# =============================================================================

if __name__ == "__main__":
    print_test_summary()

    print("\n\nSAMPLE TESTS BY CATEGORY:")
    print("-" * 80)

    categories = list(set(t["category"] for t in BRUTAL_CALCULUS_STRESS_TESTS))
    for cat in sorted(categories):
        tests = get_tests_by_category(cat)
        sample = tests[0]
        print(f"\n{cat.upper().replace('_', ' ')}: {sample['test_id']}")
        print(f"  Input: {sample['input'][:60]}...")
        print(f"  Difficulty: {sample['difficulty']}")
        print(f"  Rationale: {sample['rationale'][:80]}...")
