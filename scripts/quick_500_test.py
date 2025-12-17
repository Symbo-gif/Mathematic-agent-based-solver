#!/usr/bin/env python3
"""Quick test runner for 500-equation suite to identify failures."""

import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.core.solver_engine import get_solver_engine, SolveStatus
from symbo_agentic_reasoners.core.resource_coordinator import get_coordinator

# Test equations by category
TESTS = {
    'limits': [
        "limit((sin(x) - x + x**3/6)/x**5, x, 0)",
        "limit((1 + a/n)**(b*n), n, oo)",
        "limit(n*(sqrt(n**2 + 1) - n), n, oo)",
        "limit((log(1 + x) - x + x**2/2)/x**3, x, 0)",
        "limit((e**x - 1 - x - x**2/2)/x**3, x, 0)",
        "limit((tan(x) - x)/x**3, x, 0)",
        "limit((x - sin(x))/x**3, x, 0)",
        "limit((1 - cos(x) + x**2/2)/x**4, x, 0)",
        "limit((x**x - 1)/x, x, 0)",
        "limit((1 + 1/x)**(x + sqrt(x)), x, oo)",
        "limit(x**a * log(x), x, 0)",
        "limit((x**n - a**n)/(x - a), x, a)",
        "limit((log(1 + x))/x, x, 0)",
        "limit((log(x + sqrt(x**2 + 1)) - log(2*x)), x, oo)",
        "limit((sqrt(x**2 + x) - x), x, oo)",
        "limit(x*log(1 + 1/x), x, oo)",
        "limit((x*log(x) - x)/x, x, oo)",
        "limit((x**a - 1)/(x - 1), x, 1)",
        "limit((log(1 + x) - sin(x))/x**3, x, 0)",
        "limit((e**(2*x) - 1 - 2*x)/x**2, x, 0)",
        "limit((1 + x)**(1/x), x, 0)",
        "limit((1 + k/x)**(m*x), x, oo)",
        "limit((log(n + 1) - log(n)), n, oo)",
        "limit((n*(log(n + 1) - log(n)) - 1), n, oo)",
        "limit((x**2 * sin(1/x)), x, 0)",
        "limit((sin(1/x))/x, x, 0)",
        "limit((sin(x**2))/x, x, oo)",
        "limit(x*e**(-x), x, oo)",
        "limit(x**n/e**x, x, oo)",
        "limit(e**x/x**n, x, oo)",
        "limit((log(x))**k/x**a, x, oo)",
        "limit(n*(sqrt(n**2+1) - n), n, oo)",
        "limit((1 + c/n)**(n + d*sqrt(n)), n, oo)",
        "limit((1 + 1/n)**(n**2), n, oo)",
        "limit((1 + a/n + b/n**2)**n, n, oo)",
        "limit((n! / (n**n * e**(-n)*sqrt(2*pi*n))), n, oo)",
        "limit(binomial(2*n, n)/(4**n*sqrt(pi*n)), n, oo)",
        "limit(n*(zeta(1 + 1/n) - n), n, oo)",
        "limit(sum(1/k, (k,1,n))/log(n), n, oo)",
        "limit(sum(1/k**2, (k,1,n)), n, oo)",
        "limit(n*(sum(1/k, (k,1,n)) - log(n) - gamma), n, oo)",
        "limit(sum(k/2**k, (k,1,n)), n, oo)",
        "limit(product(1 + 1/k**2, (k,1,n)), n, oo)",
        "limit((Gamma(n + a)/(Gamma(n)*n**a)), n, oo)",
        "limit((psi(1 + x) + gamma), x, 0)",
        "limit((n*(H_n - log(n) - gamma)), n, oo)",
        "limit((H_n - log(n) - gamma), n, oo)",
        "limit((1 - cos(x))/x**2, x, 0)",
        "limit((sin(a*x))/x, x, 0)",
        "limit((e**(1/x) - 1), x, 0, dir='+')",
        "limit((e**(1/x) - 1), x, 0, dir='-')",
        "limit((log(1 + x) - x + x**2/2 - x**3/3)/x**4, x, 0)",
        "limit((tan(x) - x - x**3/3)/x**5, x, 0)",
        "limit((arctan(x) - x + x**3/3)/x**5, x, 0)",
        "limit((sqrt(1 + x) - 1 - x/2)/x**2, x, 0)",
        "limit((sqrt(1 + x) - sqrt(1 - x))/x, x, 0)",
        "limit((log(1 + a*x) - a*log(1 + x))/x**2, x, 0)",
        "limit((sin(x) - x*cos(x))/x**3, x, 0)",
        "limit((Gamma(1 + x) - 1)/x, x, 0)",
        "limit((Gamma(x) - 1/x + gamma)/1, x, 0)",
        "limit((log(Gamma(n+1)) - (n*log(n) - n)), n, oo)",
        "limit((Beta(x,1-x) - pi/sin(pi*x)), x, 1/2)",
    ],
    'series': [
        "summation(1/n, (n,1,oo))",
        "summation(1/n**p, (n,1,oo))",
        "summation((-1)**n/n, (n,1,oo))",
        "summation(n/2**n, (n,1,oo))",
        "summation(n**2/2**n, (n,1,oo))",
        "summation(1/(n*(n+1)), (n,1,oo))",
        "summation(z**n/n, (n,1,oo))",
        "summation(z**n, (n,0,oo))",
        "summation(z**n/factorial(n), (n,0,oo))",
        "summation(x**(2*n)/(factorial(2*n)), (n,0,oo))",
    ],
    'integrals': [
        "integrate(exp(-x**2), (x, -oo, oo))",
        "integrate(1/(1 + x**2), (x, -oo, oo))",
        "integrate(x/(1 + x**4), (x, 0, oo))",
        "integrate(sin(x)/x, (x, 0, oo))",
        "integrate(log(x), (x, 0, 1))",
        "integrate(x**2 * exp(-x**2), (x, -oo, oo))",
        "integrate(1/sqrt(1 - x**2), (x, 0, 1))",
        "integrate(sqrt(1 - x**2), (x, 0, 1))",
        "integrate(exp(-x)*sin(x), (x, 0, oo))",
        "integrate(exp(-x)*cos(x), (x, 0, oo))",
    ],
    'derivatives': [
        "diff(log(Gamma(x)), x)",
        "diff(Gamma(x), x)",
        "diff(x**x, x)",
        "diff(x**x**x, x)",
        "diff(log(log(x)), x)",
        "diff(arctan(x)/x, x)",
        "diff(x*log(x) - x, x)",
        "diff(sin(x**2), x)",
        "diff(exp(-x**2), x)",
        "diff(exp(-x**2 - y**2), x)",
    ],
    'linear_algebra': [
        "det(eye(n))",
        "det(diag(1,2,3,4))",
        "det([[1,2],[3,4]])",
        "det([[a,b],[c,d]])",
        "rank([[1,2,3],[2,4,6],[1,1,1]])",
        "eigenvals([[2,1],[1,2]])",
        "inverse([[1,2],[3,4]])",
        "trace([[1,2],[3,4]])",
        "norm(Matrix([[x,y]]))",
        "diophantine(x**2 - y**3 - 1)",
    ],
    'probability': [
        "exp(-lamda)*lamda**k/factorial(k)",
        "binomial(n,k)*p**k*(1-p)**(n-k)",
        "1/(sqrt(2*pi)*sigma)*exp(-(x-mu)**2/(2*sigma**2))",
        "exp(lamda*(exp(t) - 1))",
        "(1 - p + p*exp(t))**n",
        "integrate(lamda*exp(-lamda*x),(x,0,oo))",
        "summation(exp(-lamda)*lamda**k/factorial(k),(k,0,oo))",
        "summation(binomial(n,k)*p**k*(1-p)**(n-k),(k,0,n))",
    ],
    'physics': [
        "exp(-gamma*t)*cos(omega_d*t)",
        "integrate(exp(-gamma*t)*cos(omega*t),(t,0,oo))",
        "diff(exp(-gamma*t)*cos(omega_d*t), t)",
        "m*diff(x(t),t,2) + c*diff(x(t),t) + k*x(t)",
        "integrate(exp(-x**2 - y**2), (x, -oo, oo), (y, -oo, oo))",
        "integrate(exp(-(x**2 + y**2 + z**2)), (x, -oo, oo), (y, -oo, oo), (z, -oo, oo))",
        "limit((1 + i*t/n)**n, n, oo)",
        "integrate(exp(i*k*x)*exp(-x**2), (x,-oo,oo))",
    ],
}


def run_tests():
    """Run all tests and report results."""
    coordinator = get_coordinator()
    solver = get_solver_engine(coordinator)
    coordinator.start()

    results = {}
    failures = {}

    print("=" * 70)
    print("500-EQUATION TEST SUITE")
    print("=" * 70)

    for category, tests in TESTS.items():
        passed = 0
        failed_list = []

        for test in tests:
            try:
                result = solver.solve(test)
                if result.status == SolveStatus.SUCCESS:
                    passed += 1
                else:
                    failed_list.append((test, result.error or "Unknown error"))
            except Exception as e:
                failed_list.append((test, str(e)))

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
                short_test = test[:50] + "..." if len(test) > 50 else test
                short_error = error[:40] + "..." if len(error) > 40 else error
                print(f"  - {short_test}")
                print(f"    Error: {short_error}")
            if len(failed_list) > 5:
                print(f"  ... and {len(failed_list) - 5} more")

    from symbo_agentic_reasoners.core.resource_coordinator import shutdown_coordinator
    shutdown_coordinator()
    return results, failures


if __name__ == '__main__':
    run_tests()
