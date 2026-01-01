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
BRUTAL ALGEBRA STRESS TESTS - Research-Level Edge Cases
=========================================================

50 pathological test cases designed to BREAK the algebra domain specialists:
- ArithmeticSpecialist: Extreme precision arithmetic
- PolynomialSpecialist: High-degree sparse polynomials
- EquationSystemSolver: Near-singular systems, overdetermined systems
- NumberTheorySpecialist: Carmichael numbers, strong pseudoprimes
- GroupRingTheoryAgent: Large groups, pathological structures
- polynomial_gcd: Numerical instability, close roots

Each test targets a specific weakness that will likely cause failure.
"""

from typing import Dict, Any, List


def get_brutal_algebra_tests() -> List[Dict[str, Any]]:
    """
    Return 50 brutal stress tests for the Algebra domain.

    Returns:
        List of test dictionaries with keys:
        - test_id: Unique identifier (ALG_001-ALG_050)
        - category: Which specialist/component is targeted
        - input: The test input (expression, equation, etc.)
        - expected: Expected result or behavior
        - difficulty: brutal/extreme/pathological
        - rationale: Why this test is hard
    """

    tests = [
        # =======================================================================
        # CATEGORY 1: EXTREME PRECISION ARITHMETIC (ALG_001 - ALG_010)
        # Targets: ArithmeticSpecialist, mpmath precision limits
        # =======================================================================
        {
            "test_id": "ALG_001",
            "category": "ArithmeticSpecialist",
            "input": "2**10000 + 3**5000 - 7**3000",
            "expected": "exact_integer_result",
            "difficulty": "extreme",
            "rationale": "10000+ digit integers require arbitrary precision; tests Python int "
                        "overflow handling and whether mpmath is correctly configured. Result "
                        "has ~3011 digits."
        },
        {
            "test_id": "ALG_002",
            "category": "ArithmeticSpecialist",
            "input": "factorial(1000) / factorial(999)",
            "expected": "1000",
            "difficulty": "brutal",
            "rationale": "factorial(1000) has 2568 digits. Division must preserve exactness. "
                        "Common error: intermediate overflow or floating-point conversion."
        },
        {
            "test_id": "ALG_003",
            "category": "ArithmeticSpecialist",
            "input": "(10**500 + 1) * (10**500 - 1) - 10**1000 + 1",
            "expected": "0",
            "difficulty": "brutal",
            "rationale": "Tests (a+1)(a-1) = a^2 - 1 identity with 500-digit numbers. "
                        "Numerical error accumulation will give wrong result if not exact."
        },
        {
            "test_id": "ALG_004",
            "category": "ArithmeticSpecialist",
            "input": "gcd(2**2048 - 1, 2**2047 - 1)",
            "expected": "2**gcd(2048,2047) - 1 = 1",
            "difficulty": "extreme",
            "rationale": "Mersenne numbers GCD: gcd(2^a - 1, 2^b - 1) = 2^gcd(a,b) - 1. "
                        "Since gcd(2048,2047)=1, result is 1. Tests extended Euclidean on huge integers."
        },
        {
            "test_id": "ALG_005",
            "category": "ArithmeticSpecialist",
            "input": "Fraction(1, 10**100) + Fraction(1, 10**100 + 1)",
            "expected": "(2*10**100 + 1) / (10**100 * (10**100 + 1))",
            "difficulty": "extreme",
            "rationale": "Rational arithmetic with 100-digit denominators. Tests fraction reduction "
                        "with coprime denominators; numerator and denominator each ~200 digits."
        },
        {
            "test_id": "ALG_006",
            "category": "ArithmeticSpecialist",
            "input": "sum(1/Fraction(n, n+1) - 1/Fraction(n+1, n+2) for n in range(1, 10000))",
            "expected": "1/2 - 1/10001 = 9999/20002",
            "difficulty": "brutal",
            "rationale": "Telescoping series of 10000 rational terms. Tests fraction arithmetic "
                        "accumulation; naive implementation loses precision or takes forever."
        },
        {
            "test_id": "ALG_007",
            "category": "ArithmeticSpecialist",
            "input": "((2**1000)**2 - (2**1000 - 1)*(2**1000 + 1)) - 1",
            "expected": "0",
            "difficulty": "brutal",
            "rationale": "Tests difference of squares identity: a^2 - (a-1)(a+1) = 1. "
                        "With 300-digit numbers, floating point would give garbage."
        },
        {
            "test_id": "ALG_008",
            "category": "ArithmeticSpecialist",
            "input": "mod_inverse(3**500, 2**1000)",
            "expected": "exists and verifiable: x*3**500 = 1 (mod 2**1000)",
            "difficulty": "extreme",
            "rationale": "Modular inverse with 150-digit base and 300-digit modulus. "
                        "Tests extended Euclidean algorithm performance at scale."
        },
        {
            "test_id": "ALG_009",
            "category": "ArithmeticSpecialist",
            "input": "pow(7, 10**6, 10**12 + 39)",
            "expected": "modular_exponentiation_result",
            "difficulty": "brutal",
            "rationale": "Modular exponentiation with exponent 10^6 and 12-digit modulus. "
                        "Tests binary exponentiation; naive approach takes forever."
        },
        {
            "test_id": "ALG_010",
            "category": "ArithmeticSpecialist",
            "input": "(1 + sqrt(5))/2 - golden_ratio to 1000 decimal places",
            "expected": "0.0000... (1000 zeros)",
            "difficulty": "extreme",
            "rationale": "Tests symbolic simplification: phi = (1+sqrt(5))/2 is exact. "
                        "Evaluating to 1000 places and comparing requires mpmath precision tuning."
        },

        # =======================================================================
        # CATEGORY 2: POLYNOMIAL SPECIALIST STRESS (ALG_011 - ALG_020)
        # Targets: PolynomialSpecialist, polynomial_solvers, numeric_roots
        # =======================================================================
        {
            "test_id": "ALG_011",
            "category": "PolynomialSpecialist",
            "input": "x**100 - 1 = 0 (find all 100 roots)",
            "expected": "100 roots: e^(2*pi*i*k/100) for k=0..99",
            "difficulty": "extreme",
            "rationale": "Degree-100 polynomial with 100 complex roots on unit circle. "
                        "Tests root finding beyond degree-4 formulas; requires numeric methods."
        },
        {
            "test_id": "ALG_012",
            "category": "PolynomialSpecialist",
            "input": "x**100 + x**50 + 1 = 0",
            "expected": "roots related to primitive 150th roots of unity",
            "difficulty": "extreme",
            "rationale": "Sparse polynomial with only 3 terms but degree 100. "
                        "Standard root-finding struggles with sparse high-degree polynomials."
        },
        {
            "test_id": "ALG_013",
            "category": "PolynomialSpecialist",
            "input": "x**5 - x - 1 = 0",
            "expected": "no_closed_form (Abel-Ruffini theorem)",
            "difficulty": "pathological",
            "rationale": "Famous unsolvable quintic by radicals. Tests whether solver correctly "
                        "identifies no algebraic solution exists and falls back to numeric."
        },
        {
            "test_id": "ALG_014",
            "category": "PolynomialSpecialist",
            "input": "(x - 1/1000000)*(x - 1/1000001) = 0 expanded",
            "expected": "x = 1/1000000, x = 1/1000001",
            "difficulty": "pathological",
            "rationale": "Roots differ by ~10^-12; coefficient extraction loses precision. "
                        "Wilkinson's polynomial effect on rational roots."
        },
        {
            "test_id": "ALG_015",
            "category": "PolynomialSpecialist",
            "input": "product((x - k) for k in range(1, 21))",
            "expected": "roots: 1, 2, 3, ..., 20",
            "difficulty": "extreme",
            "rationale": "Wilkinson's polynomial (degree 20). Notorious for numerical instability; "
                        "tiny coefficient perturbations cause roots to become complex."
        },
        {
            "test_id": "ALG_016",
            "category": "PolynomialSpecialist",
            "input": "x**4 - 10*x**3 + 35*x**2 - 50*x + 24 (roots: 1,2,3,4)",
            "expected": "x = 1, 2, 3, 4",
            "difficulty": "brutal",
            "rationale": "Quartic with integer roots. Ferrari's method should work, but "
                        "floating-point intermediate calculations can give wrong answers."
        },
        {
            "test_id": "ALG_017",
            "category": "PolynomialSpecialist",
            "input": "x**3 - 2 = 0",
            "expected": "x = 2^(1/3), 2^(1/3)*omega, 2^(1/3)*omega^2",
            "difficulty": "brutal",
            "rationale": "Cube root of 2: one real, two complex roots. Tests Cardano's formula "
                        "with complex cube roots and correct handling of casus irreducibilis."
        },
        {
            "test_id": "ALG_018",
            "category": "PolynomialSpecialist",
            "input": "x**4 + 1 = 0",
            "expected": "x = e^(i*pi/4), e^(i*3*pi/4), e^(i*5*pi/4), e^(i*7*pi/4)",
            "difficulty": "brutal",
            "rationale": "No real roots; all 4 are complex 8th roots of unity. "
                        "Tests Ferrari's method when all roots are complex."
        },
        {
            "test_id": "ALG_019",
            "category": "PolynomialSpecialist",
            "input": "x**3 - 3*x**2 + 3*x - 1 = 0",
            "expected": "x = 1 (triple root)",
            "difficulty": "pathological",
            "rationale": "This is (x-1)^3 expanded. Multiple root detection is numerically unstable; "
                        "derivative and polynomial share root causing Newton-Raphson division by near-zero."
        },
        {
            "test_id": "ALG_020",
            "category": "PolynomialSpecialist",
            "input": "x**150 + 0*x**100 + 0*x**50 + 1 (sparse)",
            "expected": "roots_at_primitive_roots_of_unity",
            "difficulty": "extreme",
            "rationale": "Extremely sparse degree-150 polynomial (only 2 nonzero coefficients). "
                        "Standard algorithms allocate 150-term arrays for 2 terms."
        },

        # =======================================================================
        # CATEGORY 3: EQUATION SYSTEM SOLVER (ALG_021 - ALG_030)
        # Targets: EquationSystemSolver, linear/nonlinear systems
        # =======================================================================
        {
            "test_id": "ALG_021",
            "category": "EquationSystemSolver",
            "input": "50x50 Hilbert matrix system: H*x = b",
            "expected": "solution_exists_but_highly_unstable",
            "difficulty": "pathological",
            "rationale": "Hilbert matrix H[i,j] = 1/(i+j-1) is notorious for ill-conditioning. "
                        "50x50 Hilbert has condition number ~10^72; standard solve gives garbage."
        },
        {
            "test_id": "ALG_022",
            "category": "EquationSystemSolver",
            "input": "{x + 1e-15*y = 1, x + y = 2}",
            "expected": "x ~ 1, y ~ 1 (but catastrophically unstable)",
            "difficulty": "pathological",
            "rationale": "Near-singular 2x2 system. Determinant ~ 10^-15; Gaussian elimination "
                        "amplifies roundoff to make solution completely wrong."
        },
        {
            "test_id": "ALG_023",
            "category": "EquationSystemSolver",
            "input": "100 equations in 50 unknowns (overdetermined)",
            "expected": "least_squares_solution_or_inconsistent",
            "difficulty": "extreme",
            "rationale": "Overdetermined system with no exact solution. Tests whether solver "
                        "correctly identifies inconsistency or computes least-squares."
        },
        {
            "test_id": "ALG_024",
            "category": "EquationSystemSolver",
            "input": "5 equations in 10 unknowns (underdetermined)",
            "expected": "parametric_solution_with_5_free_variables",
            "difficulty": "brutal",
            "rationale": "Underdetermined system should give parametric solution. "
                        "Tests free variable identification and parametric form construction."
        },
        {
            "test_id": "ALG_025",
            "category": "EquationSystemSolver",
            "input": "{x^2 + y^2 = 1, x^2 + y^2 = 2}",
            "expected": "no_solution (inconsistent)",
            "difficulty": "brutal",
            "rationale": "Two circles with no intersection. Tests inconsistency detection "
                        "in nonlinear polynomial systems."
        },
        {
            "test_id": "ALG_026",
            "category": "EquationSystemSolver",
            "input": "{x^3 + y^3 + z^3 = k} for k = 33",
            "expected": "x=8866128975287528, y=-8778405442862239, z=-2736111468807040",
            "difficulty": "pathological",
            "rationale": "Sum of three cubes for 33 (solved 2019 after decades). Tests ability "
                        "to find integer solutions; brute force is infeasible."
        },
        {
            "test_id": "ALG_027",
            "category": "EquationSystemSolver",
            "input": "10x10 Vandermonde system with nodes 0.1, 0.2, ..., 1.0",
            "expected": "interpolation_coefficients",
            "difficulty": "extreme",
            "rationale": "Vandermonde matrix for polynomial interpolation is ill-conditioned "
                        "when nodes are close together (condition ~10^12 for these nodes)."
        },
        {
            "test_id": "ALG_028",
            "category": "EquationSystemSolver",
            "input": "{xy = 6, x + y = 5} (quadratic system)",
            "expected": "x=2,y=3 and x=3,y=2",
            "difficulty": "brutal",
            "rationale": "Simple quadratic system, but tests Groebner basis or resultant approach. "
                        "Naive substitution can miss solutions or introduce spurious ones."
        },
        {
            "test_id": "ALG_029",
            "category": "EquationSystemSolver",
            "input": "3x3 system with determinant = 10^-100",
            "expected": "solution_exists_but_precision_limited",
            "difficulty": "pathological",
            "rationale": "Matrix A with det(A) = 10^-100 is effectively singular. "
                        "Standard 64-bit floats see it as singular; arbitrary precision needed."
        },
        {
            "test_id": "ALG_030",
            "category": "EquationSystemSolver",
            "input": "{exp(x) + exp(y) = 4, exp(x)*exp(y) = 3}",
            "expected": "x = ln(3), y = ln(1) = 0 and symmetric",
            "difficulty": "brutal",
            "rationale": "Transcendental system disguised as algebraic (substitute u=e^x). "
                        "Tests classification and transformation to polynomial form."
        },

        # =======================================================================
        # CATEGORY 4: NUMBER THEORY SPECIALIST (ALG_031 - ALG_040)
        # Targets: NumberTheorySpecialist, primality, factorization
        # =======================================================================
        {
            "test_id": "ALG_031",
            "category": "NumberTheorySpecialist",
            "input": "is_prime(561) [Carmichael number]",
            "expected": "False (561 = 3*11*17 is composite)",
            "difficulty": "pathological",
            "rationale": "561 is first Carmichael number: passes Fermat test for ALL coprime bases. "
                        "Only Miller-Rabin with multiple witnesses detects it."
        },
        {
            "test_id": "ALG_032",
            "category": "NumberTheorySpecialist",
            "input": "is_prime(2047) [strong pseudoprime to base 2]",
            "expected": "False (2047 = 23*89)",
            "difficulty": "pathological",
            "rationale": "2047 is strong pseudoprime to base 2 but not to base 3. "
                        "Single-witness Miller-Rabin fails; needs multiple witnesses."
        },
        {
            "test_id": "ALG_033",
            "category": "NumberTheorySpecialist",
            "input": "is_prime(2^67 - 1)",
            "expected": "False (Mersenne 67 is composite: 193707721 * ...)",
            "difficulty": "extreme",
            "rationale": "Large Mersenne number that looks prime but isn't. "
                        "Tests primality for 20-digit numbers; historically fooled mathematicians."
        },
        {
            "test_id": "ALG_034",
            "category": "NumberTheorySpecialist",
            "input": "factor(2^64 + 1)",
            "expected": "274177 * 67280421310721",
            "difficulty": "extreme",
            "rationale": "Fermat number F_6 = 2^64 + 1. Factoring took centuries historically; "
                        "tests Pollard's rho and ECM on 19-digit semiprime."
        },
        {
            "test_id": "ALG_035",
            "category": "NumberTheorySpecialist",
            "input": "factor(RSA-100)",
            "expected": "known_factors_from_challenge",
            "difficulty": "pathological",
            "rationale": "RSA-100 is a 100-digit semiprime (factored 1991). Tests whether "
                        "factorization times out or succeeds with quadratic sieve."
        },
        {
            "test_id": "ALG_036",
            "category": "NumberTheorySpecialist",
            "input": "totient(10^12)",
            "expected": "exact_value",
            "difficulty": "extreme",
            "rationale": "Euler's totient of 10^12 requires factoring 2^12 * 5^12. "
                        "phi(10^12) = 10^12 * (1-1/2) * (1-1/5) = 4*10^11. Tests big totient."
        },
        {
            "test_id": "ALG_037",
            "category": "NumberTheorySpecialist",
            "input": "solve 17x = 1 (mod 10^18 + 7)",
            "expected": "modular_inverse_exists",
            "difficulty": "brutal",
            "rationale": "Modular inverse with 18-digit modulus. Extended Euclidean must run "
                        "on ~60 iterations with multi-word arithmetic."
        },
        {
            "test_id": "ALG_038",
            "category": "NumberTheorySpecialist",
            "input": "CRT: x = 2 (mod 10^9+7), x = 3 (mod 10^9+9), x = 5 (mod 998244353)",
            "expected": "unique_solution_mod_product",
            "difficulty": "brutal",
            "rationale": "Chinese Remainder Theorem with three large coprime moduli. "
                        "Product is ~10^27; solution requires arbitrary precision."
        },
        {
            "test_id": "ALG_039",
            "category": "NumberTheorySpecialist",
            "input": "divisor_sigma_0(10^15) = number of divisors",
            "expected": "exact_count",
            "difficulty": "extreme",
            "rationale": "sigma_0(10^15) = sigma_0(2^15 * 5^15) = 16 * 16 = 256. "
                        "Tests factorization of huge smooth number."
        },
        {
            "test_id": "ALG_040",
            "category": "NumberTheorySpecialist",
            "input": "solve x^2 = 2 (mod 10^9+7) [quadratic residue]",
            "expected": "solution_via_tonelli_shanks_or_none",
            "difficulty": "brutal",
            "rationale": "Quadratic residue modulo large prime. Tests Tonelli-Shanks or "
                        "Cipolla's algorithm for square roots mod p."
        },

        # =======================================================================
        # CATEGORY 5: POLYNOMIAL GCD & RESULTANTS (ALG_041 - ALG_045)
        # Targets: polynomial_gcd module, numerical stability
        # =======================================================================
        {
            "test_id": "ALG_041",
            "category": "polynomial_gcd",
            "input": "gcd((x-1)^10 * (x-2)^5, (x-1)^3 * (x-3)^7)",
            "expected": "(x-1)^3",
            "difficulty": "brutal",
            "rationale": "GCD with high-multiplicity roots. Euclidean algorithm on expanded "
                        "polynomials loses precision; subresultant PRS needed."
        },
        {
            "test_id": "ALG_042",
            "category": "polynomial_gcd",
            "input": "gcd(x^100 - 1, x^75 - 1)",
            "expected": "x^25 - 1",
            "difficulty": "extreme",
            "rationale": "gcd of degrees 100 and 75; result has degree gcd(100,75)=25. "
                        "Tests Euclidean algorithm on high-degree sparse polynomials."
        },
        {
            "test_id": "ALG_043",
            "category": "polynomial_gcd",
            "input": "resultant((x-1.0000000001)*(x-1.0000000002), (x-1.0000000001)*(x-2))",
            "expected": "near_zero (shared root at 1.0000000001)",
            "difficulty": "pathological",
            "rationale": "Polynomials share root at ~1+10^-10. Numerical resultant sees near-zero "
                        "but roundoff makes it nonzero. Classic GCD numerical instability."
        },
        {
            "test_id": "ALG_044",
            "category": "polynomial_gcd",
            "input": "resultant(x^50 + 1, x^50 - 1)",
            "expected": "2^50",
            "difficulty": "extreme",
            "rationale": "Resultant of x^50+1 and x^50-1 via Sylvester matrix (100x100). "
                        "Determinant computation with alternating signs causes cancellation."
        },
        {
            "test_id": "ALG_045",
            "category": "polynomial_gcd",
            "input": "content and primitive_part of 12x^10 + 18x^5 + 24",
            "expected": "content=6, primitive=2x^10 + 3x^5 + 4",
            "difficulty": "brutal",
            "rationale": "Content extraction from polynomial with large coefficients. "
                        "Tests integer GCD computation on coefficient list."
        },

        # =======================================================================
        # CATEGORY 6: GROUP/RING THEORY (ALG_046 - ALG_050)
        # Targets: GroupRingTheoryAgent, abstract algebra
        # =======================================================================
        {
            "test_id": "ALG_046",
            "category": "GroupRingTheoryAgent",
            "input": "order of symmetric group S_100",
            "expected": "100! = 9.33*10^157",
            "difficulty": "extreme",
            "rationale": "S_100 has 100! elements. Tests factorial computation and whether "
                        "group order is correctly computed without enumeration."
        },
        {
            "test_id": "ALG_047",
            "category": "GroupRingTheoryAgent",
            "input": "is S_5 isomorphic to A_5?",
            "expected": "False (orders differ: 120 vs 60)",
            "difficulty": "brutal",
            "rationale": "Quick isomorphism test via order comparison. But tests whether "
                        "group properties are correctly computed for comparison."
        },
        {
            "test_id": "ALG_048",
            "category": "GroupRingTheoryAgent",
            "input": "compute Z/10^12Z * Z/10^12Z * Z/10^12Z structure",
            "expected": "direct_product_of_cyclic_groups",
            "difficulty": "extreme",
            "rationale": "Direct product of three copies of Z/10^12Z. Tests abelian group "
                        "decomposition and primary decomposition theorem."
        },
        {
            "test_id": "ALG_049",
            "category": "GroupRingTheoryAgent",
            "input": "Groebner basis of <x^10 - y^10, y^10 - z^10, z^10 - 1>",
            "expected": "reduced_groebner_basis",
            "difficulty": "pathological",
            "rationale": "Groebner basis computation explodes in complexity. This ideal in "
                        "Z[x,y,z] requires careful monomial ordering and reduction."
        },
        {
            "test_id": "ALG_050",
            "category": "GroupRingTheoryAgent",
            "input": "find nilpotent elements in Z/100Z",
            "expected": "{0, 10, 20, 30, 40, 50, 60, 70, 80, 90} (multiples of 10 where 10^2=0)",
            "difficulty": "brutal",
            "rationale": "Nilpotent elements n satisfy n^k = 0 for some k. In Z/100Z, "
                        "10^2 = 100 = 0, so multiples of 10 are nilpotent. Tests ring structure."
        },
    ]

    return tests


def print_tests_summary():
    """Print a summary of all brutal tests."""
    tests = get_brutal_algebra_tests()

    print("=" * 80)
    print("BRUTAL ALGEBRA STRESS TESTS - 50 Research-Level Edge Cases")
    print("=" * 80)
    print()

    categories = {}
    difficulties = {"brutal": 0, "extreme": 0, "pathological": 0}

    for test in tests:
        cat = test["category"]
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[test["difficulty"]] += 1

    print("Tests by Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    print()
    print("Tests by Difficulty:")
    for diff, count in difficulties.items():
        print(f"  {diff}: {count}")

    print()
    print("=" * 80)
    print("Individual Tests:")
    print("=" * 80)

    for test in tests:
        print()
        print(f"[{test['test_id']}] {test['category']} - {test['difficulty'].upper()}")
        print(f"  Input: {test['input'][:60]}..." if len(test['input']) > 60 else f"  Input: {test['input']}")
        print(f"  Expected: {test['expected'][:50]}..." if len(test['expected']) > 50 else f"  Expected: {test['expected']}")
        print(f"  Rationale: {test['rationale'][:70]}...")


# Export for use by test runners
BRUTAL_ALGEBRA_TESTS = get_brutal_algebra_tests()


if __name__ == "__main__":
    print_tests_summary()
