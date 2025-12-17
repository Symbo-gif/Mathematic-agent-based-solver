#!/usr/bin/env python3
"""100 Research-level "Edgy" tests for advanced mathematical capabilities."""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.core.solver_engine import get_solver_engine, SolveStatus
from symbo_agentic_reasoners.core.resource_coordinator import get_coordinator

# Test equations by category
TESTS = {
    'asymptotic_limits': [
        # 1-25: Asymptotic / Exotic Limits
        "limit((Gamma(x + a)/Gamma(x)) / x**a, x, oo)",
        "limit((log(Gamma(x)) - (x - 1/2)*log(x) + x - 1/2*log(2*pi)), x, oo)",
        "limit((zeta(1 + 1/x) - x), x, oo)",
        "limit(q**n * (n!)**2 / (2*n)! , n, oo)",
        "limit((log(log(x)))/log(x), x, oo)",
        "limit((x**x * e**(-x**2) * sqrt(x)), x, oo)",
        "limit((log(1 + x) - x + x**2/2 - x**3/3 + x**4/4)/x**5, x, 0)",
        "limit((Li(x) - x/log(x))/ (x/log(x)**2), x, oo)",
        "limit((Ei(x) - gamma - log(abs(x)) - x)/x**2, x, 0)",
        "limit((BesselJ(0,x) - 1 + x**2/4)/x**4, x, 0)",
        "limit((BesselJ(1,x) - x/2)/x**3, x, 0)",
        "limit((erf(x) - 2*x/sqrt(pi))/x**3, x, 0)",
        "limit((log(sin(x))/log(x)), x, 0)",
        "limit((x*log(x) - x + 1)/(x*log(x)), x, oo)",
        "limit((x**(1/x) - 1)*x, x, oo)",
        "limit((x**(1/log(x)) - e), x, oo)",
        "limit((polylog(2,1 - 1/x) - pi**2/6 + (log(x))**2/2), x, oo)",
        "limit((zeta(s) - 1/(s-1)), s, 1)",
        "limit((sum(1/k - 1/(k + a), (k,1,n)) - log(1 + a/n))/1, n, oo)",
        "limit((sum(mu(k)/k, (k,1,n))), n, oo)",
        "limit((sum(Lambda(k)/k**s, (k,1,n)) + zeta_prime(s)/zeta(s)), n, oo)",
        "limit((sum(1/(k*log(k)), (k,2,n)) - log(log(n))), n, oo)",
        "limit((sum((-1)**k/k**2, (k,1,n)) + pi**2/12), n, oo)",
        "limit((product((1 + 1/k), (k,1,n))/ (C*n*e)), n, oo)",
    ],
    'nasty_series': [
        # 26-45: Nasty Series / Products
        "summation((-1)**n * log(n)/n, (n,2,oo))",
        "summation(mu(n)/n, (n,1,oo))",
        "summation(mu(n)/n**2, (n,1,oo))",
        "summation(Lambda(n)/n**s, (n,2,oo))",
        "summation(1/(n**2 * sin(1/n)), (n,1,oo))",
        "summation((sin(1/n))/n, (n,1,oo))",
        "summation(((-1)**n * sin(1/n))/n, (n,1,oo))",
        "summation(((-1)**n * log(n))/sqrt(n), (n,2,oo))",
        "summation(((-1)**n)/(sqrt(n)*log(n)), (n,2,oo))",
        "summation((H_n - log(n) - gamma)/n, (n,1,oo))",
        "summation(((-1)**n * (H_n - log(n) - gamma)), (n,1,oo))",
        "summation(((-1)**n)/ (n*(log(n))*(log(log(n)))), (n,3,oo))",
        "summation(1/(n*(log(n))*(log(log(n))**2)), (n,3,oo))",
        "summation(((-1)**n)/ (n*(log(n))**p), (n,2,oo))",
        "summation((q**(n**2)), (n,-oo,oo))",
        "product((1 - 1/p**2), (p, primes))",
        "product((1 - 1/p**s), (p, primes))",
        "summation((phi(n))/n**2, (n,1,oo))",
        "summation((phi(n))/n**3, (n,1,oo))",
        "summation(((-1)**n * phi(n))/n**2, (n,1,oo))",
    ],
    'tough_integrals': [
        # 46-65: Tough Integrals / Special Functions
        "integrate(x**(s-1)/(1 - x), (x,0,1))",
        "integrate(x**(s-1)/(1 + x), (x,0,oo))",
        "integrate(log(1 - x)/x, (x,0,1))",
        "integrate(log(1 + x)/x, (x,0,1))",
        "integrate(log(x)/(1 + x), (x,0,1))",
        "integrate((log(x))**2/(1 + x), (x,0,1))",
        "integrate(log(sin(x)), (x,0,pi))",
        "integrate(log(sin(x)), (x,0,pi/2))",
        "integrate((x - floor(x) - 1/2)/x**2, (x,1,oo))",
        "integrate(sin(x**2), (x,0,oo))",
        "integrate(cos(x**2), (x,0,oo))",
        "integrate(exp(-x**2)*(cos(2*x) - 1), (x,0,oo))",
        "integrate((sin(x)/x) * exp(-epsilon*x), (x,0,oo))",
        "integrate((sin(a*x))/(sinh(b*x)), (x,0,oo))",
        "integrate((x**2)/(e**x - 1), (x,0,oo))",
        "integrate((x**4)/(e**x - 1), (x,0,oo))",
        "integrate((log(x))**2 * e**(-x), (x,0,oo))",
        "integrate((log(x))/(1 + x**2), (x,0,oo))",
        "integrate(exp(-x**2) * H_n(x) * H_m(x), (x,-oo,oo))",
        "integrate((sin(x)/x)**3, (x,0,oo))",
    ],
    'diophantine_nt': [
        # 66-80: Diophantine / Number Theory Edge Cases
        "diophantine(x**2 - 5*y**2 - 920)",
        "diophantine(3*x**2 - 7*y**2 + 2*x - 5*y - 11)",
        "diophantine(x**2 + y**2 - 3*z**2)",
        "diophantine(x**3 + y**3 + z**3 - 33)",
        "diophantine(x**4 - y**4 - z**2)",
        "diophantine(6*x*y - x**2 - y**2 - 1)",
        "diophantine(a*x + b*y + c*z - d)",
        "diophantine(2*x**2 + 3*y**2 + 5*z**2 - 7*w**2 - 1)",
        "diophantine(x**2 - D*y**2 - 1)",
        "diophantine(x**2 - D*y**2 - N)",
        "diophantine(x**2 + y**2 + z**2 - 3*w**2)",
        "diophantine(5*x**2 - 3*y**2 + 7*z**2 - 11)",
        "diophantine(x**2 + x*y + y**2 - 7)",
        "diophantine(4*x**2 - 13*y**2 + 9)",
        "diophantine(x**3 - 2*y**3 - 1)",
    ],
    'probability_stats': [
        # 81-95: Probability / Statistics with Asymptotics (simplified)
        "limit((M_X(t) - 1 - mu*t - (sigma**2*t**2)/2)/t**3, t, 0)",
        "limit((log(M_X(t)) - mu*t - (sigma**2*t**2)/2)/t**3, t, 0)",
        "integrate(integrate(lambda_*mu*exp(-lambda_*x - mu*y), (x,0,oo)), (y,0,oo))",
        "summation(exp(-lambda_)*lambda_**k/factorial(k),(k,0,oo))",
        "integrate(x**2 * 1/(sqrt(2*pi))*exp(-x**2/2),(x,-oo,oo))",
        "integrate((x-mu)**3 * 1/(sqrt(2*pi)*sigma)*exp(-(x-mu)**2/(2*sigma**2)),(x,-oo,oo))",
        "integrate((x-mu)**4 * 1/(sqrt(2*pi)*sigma)*exp(-(x-mu)**2/(2*sigma**2)),(x,-oo,oo))",
        "integrate(x * 1/(sqrt(2*pi))*exp(-x**2/2),(x,-oo,oo))",
        "integrate(x**3 * 1/(sqrt(2*pi))*exp(-x**2/2),(x,-oo,oo))",
        "integrate(x**4 * 1/(sqrt(2*pi))*exp(-x**2/2),(x,-oo,oo))",
    ],
    'airy_bessel': [
        # 96-100: Mixed Airy/Bessel Asymptotics
        "limit(AiryAi(x)/(0.5/pi**0.5*x**(-1/4)*exp(-2*x**(3/2)/3)), x, oo)",
        "limit(AiryBi(x)/(0.5/pi**0.5*x**(-1/4)*exp(2*x**(3/2)/3)), x, oo)",
        "limit((BesselJ(0,x) - sqrt(2/(pi*x))*cos(x - pi/4)), x, oo)",
        "limit((BesselY(0,x) - sqrt(2/(pi*x))*sin(x - pi/4)), x, oo)",
        "limit(BesselJ(n,x)/((x/2)**n/Gamma(n+1)), x, 0)",
    ],
}


def run_tests(verbose=False):
    """Run all tests and report results."""
    coordinator = get_coordinator()
    solver = get_solver_engine(coordinator)
    coordinator.start()

    results = {}
    failures = {}

    print("=" * 70)
    print("100 EDGY RESEARCH-LEVEL TEST SUITE")
    print("=" * 70)

    for category, tests in TESTS.items():
        passed = 0
        failed_list = []

        for test in tests:
            try:
                result = solver.solve(test)
                if result.status == SolveStatus.SUCCESS:
                    passed += 1
                    if verbose:
                        print(f"  [PASS] {test[:50]}...")
                else:
                    failed_list.append((test, result.error or result.result or "Unknown error"))
                    if verbose:
                        print(f"  [FAIL] {test[:50]}...")
            except Exception as e:
                failed_list.append((test, str(e)))
                if verbose:
                    print(f"  [ERR]  {test[:50]}...")

        total = len(tests)
        pct = (passed / total * 100) if total > 0 else 0

        results[category] = {'passed': passed, 'total': total, 'pct': pct}
        if failed_list:
            failures[category] = failed_list

        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"{category:20s} {passed:3d}/{total:3d} ({pct:5.1f}%) [{bar}]")

    # Overall
    total_passed = sum(r['passed'] for r in results.values())
    total_tests = sum(r['total'] for r in results.values())
    overall_pct = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print("=" * 70)
    print(f"{'OVERALL':20s} {total_passed:3d}/{total_tests:3d} ({overall_pct:5.1f}%)")
    print("=" * 70)

    # Show failures
    if failures:
        print("\nFAILURES BY CATEGORY:")
        print("-" * 70)
        for category, failed_list in failures.items():
            print(f"\n[{category.upper()}] ({len(failed_list)} failures)")
            for test, error in failed_list[:5]:  # Show first 5 per category
                short_test = test[:60] + "..." if len(test) > 60 else test
                short_error = str(error)[:50] + "..." if len(str(error)) > 50 else str(error)
                print(f"  - {short_test}")
                print(f"    Error: {short_error}")
            if len(failed_list) > 5:
                print(f"  ... and {len(failed_list) - 5} more")

    from symbo_agentic_reasoners.core.resource_coordinator import shutdown_coordinator
    shutdown_coordinator()
    return results, failures


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    run_tests(verbose=args.verbose)
