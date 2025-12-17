#!/usr/bin/env python3
"""
50 "Edgiest Edge" Mathematical Stress Tests
============================================
These are at the boundary of what CAS/LLMs typically handle.
Tests: asymptotic expansions, multi-parameter limits, Diophantine/NT reasoning,
symbolic recognition of special functions.

NOTE: Many of these are NOT expected to simplify nicely - they test edge cases.
"""

import sys
import os
import time
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from symbo_agentic_reasoners.core.solver_engine import get_solver_engine, SolveStatus


def run_edgiest_tests():
    """Run all 50 edgiest edge tests."""

    solver = get_solver_engine()

    # 50 "Edgiest Edge" tests
    tests = [
        # 1-15: Extreme Asymptotics / Stokes-ish Behavior
        ("limit((Gamma(x + a)/Gamma(x) - x**a) / (x**(a-1)), x, oo)", "Gamma ratio asymptotic correction"),
        ("limit((log(Gamma(x)) - (x - 1/2)*log(x) + x - 1/2*log(2*pi)), x, oo)", "Stirling remainder"),
        ("limit((zeta(1 + 1/x) - x - gamma), x, oo)", "Zeta pole correction"),
        ("limit((log(zeta(1 + 1/x)) - log(x)), x, oo)", "Log zeta asymptotic"),
        ("limit((x*log(log(x)))/log(x), x, oo)", "Nested log growth"),
        ("limit((log(log(log(x))))/log(log(x)), x, oo)", "Triple nested log"),
        ("limit((Ei(x) - gamma - log(abs(x)) - x - x**2/4)/x**3, x, 0)", "Ei small arg Taylor"),
        ("limit((erf(x) - 2*x/sqrt(pi) + 2*x**3/(3*sqrt(pi)))/x**5, x, 0)", "erf Taylor remainder"),
        ("limit((BesselJ(0,x) - sqrt(2/(pi*x))*cos(x - pi/4)), x, oo)", "Bessel J0 asymptotic diff"),
        ("limit((BesselY(0,x) - sqrt(2/(pi*x))*sin(x - pi/4)), x, oo)", "Bessel Y0 asymptotic diff"),
        ("limit((Ai(x) - 1/(2*sqrt(pi))*x**(-1/4)*exp(-2*x**(3/2)/3)), x, oo)", "Airy Ai asymptotic diff"),
        ("limit((Bi(x) - 1/sqrt(pi)*x**(-1/4)*exp(2*x**(3/2)/3)), x, oo)", "Airy Bi asymptotic diff"),
        ("limit((log(Gamma(x+1)) - (x+1/2)*log(x) + x - 1/2*log(2*pi)), x, oo)", "Log-Gamma Stirling"),
        ("limit((factorial(n) - sqrt(2*pi*n)*(n/E)**n)/((n/E)**n*sqrt(n)), n, oo)", "Stirling correction ratio"),
        ("limit((log(Gamma(n+1)) - (n*log(n) - n + 1/2*log(2*pi*n))), n, oo)", "Log factorial Stirling"),

        # 16-25: Wild Series / Products Near Known Frontiers
        ("summation(((-1)**n * log(n))/n, (n,2,oo))", "Alt log series"),
        ("summation(((-1)**n * log(n))/sqrt(n), (n,2,oo))", "Alt log/sqrt series"),
        ("summation((mu(n)*log(n))/n, (n,2,oo))", "Mobius log series"),
        ("summation(mu(n)/n, (n,1,oo))", "Prime number theorem form"),
        ("summation(Lambda(n)/n**s, (n,2,oo))", "von Mangoldt Dirichlet"),
        ("summation((H_n - log(n) - gamma)/n, (n,1,oo))", "Harmonic correction sum"),
        ("summation(((-1)**n * (H_n - log(n) - gamma)), (n,1,oo))", "Alt harmonic correction"),
        ("summation(((-1)**n)/(n*(log(n))*(log(log(n)))), (n,3,oo))", "Nested log alt series"),
        ("summation(1/(n*(log(n))*(log(log(n))**2)), (n,3,oo))", "Nested log convergent"),
        ("product((1 - 1/p**2), (p, primes))", "Euler product for zeta(2)"),

        # 26-35: Ugly Integrals & Transform-Type Expressions
        ("integrate(log(1 - x)/x, (x,0,1))", "Dilog at 1"),
        ("integrate(log(1 + x)/x, (x,0,1))", "Alt dilog"),
        ("integrate(log(x)/(1 + x), (x,0,1))", "Log/(1+x) integral"),
        ("integrate((log(x))**2/(1 + x), (x,0,1))", "Log^2/(1+x) integral"),
        ("integrate(log(sin(x)), (x,0,pi))", "Log-sin over [0,pi]"),
        ("integrate(log(sin(x)), (x,0,pi/2))", "Log-sin over [0,pi/2]"),
        ("integrate((x - floor(x) - 1/2)/x**2, (x,1,oo))", "Fractional part integral"),
        ("integrate(sin(x**2), (x,0,oo))", "Fresnel sine"),
        ("integrate(cos(x**2), (x,0,oo))", "Fresnel cosine"),
        ("integrate(exp(-x**2)*(cos(2*x) - 1), (x,0,oo))", "Gaussian oscillatory"),

        # 36-43: More Integrals and Special Cases
        ("integrate((sin(x)/x)**3, (x,0,oo))", "Sinc^3 integral"),
        ("integrate((sin(x)/x)*exp(-epsilon*x), (x,0,oo))", "Damped sinc (epsilon>0)"),
        ("integrate(x**(s-1)/(1 - x), (x,0,1))", "Analytic continuation"),
        ("integrate(x**(s-1)/(1 + x), (x,0,oo))", "Beta function form"),
        ("integrate(exp(-x**2) * hermite(n, x) * hermite(m, x), (x,-oo,oo))", "Hermite orthogonality"),

        # 41-48: Diophantine / NT at the Edge
        ("diophantine(x**3 + y**3 + z**3 - 33)", "Sum of 3 cubes = 33"),
        ("diophantine(x**3 + y**3 + z**3 - 42)", "Sum of 3 cubes = 42"),
        ("diophantine(x**3 + y**3 + z**3 - 114)", "Sum of 3 cubes = 114"),
        ("diophantine(x**2 + y**2 + z**2 - 3*w**2)", "Quaternary quadratic"),
        ("diophantine(x**4 + y**4 + z**4 - w**4)", "Sum of 4th powers"),
        ("diophantine(x**2 - 5*y**2 - 920)", "Generalized Pell"),
        ("diophantine(3*x**2 - 7*y**2 + 2*x - 5*y - 11)", "Mixed quadratic"),
        ("diophantine(2*x**2 + 3*y**2 + 5*z**2 - 7*w**2 - 1)", "Quaternary mixed"),

        # 49-50: Pathological / Very Symbolic
        ("limit((x**x * exp(-x**2) * sqrt(x)), x, oo)", "x^x * e^(-x^2) * sqrt(x)"),
        ("limit((Ai(x) + I*Bi(x))/exp(2*x**(3/2)/3), x, oo)", "Complex Airy asymptotic"),
    ]

    print("=" * 70)
    print("50 EDGIEST EDGE MATHEMATICAL STRESS TESTS")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print()

    passed = 0
    failed = 0
    errors = []
    results_detail = []

    for i, (expr, description) in enumerate(tests, 1):
        print(f"[{i:2d}/50] {description[:50]:<50}", end=" ")

        try:
            start = time.time()
            result = solver.solve(expr)
            elapsed = time.time() - start

            status = result.status.name if hasattr(result, 'status') else str(result.status)
            result_str = str(result.result) if result.result else "None"

            # Determine if it's a meaningful result
            is_error = False
            if status == "ERROR" or status == "FAILURE":
                is_error = True
            elif "error" in result_str.lower() or "failed" in result_str.lower():
                is_error = True
            elif result_str == "None" or result_str == "":
                is_error = True
            elif "NotImplementedError" in result_str:
                is_error = True

            if is_error:
                print(f"FAIL ({elapsed:.2f}s)")
                failed += 1
                errors.append((i, expr, description, result_str[:100]))
            else:
                print(f"PASS ({elapsed:.2f}s)")
                passed += 1

            results_detail.append({
                'idx': i,
                'expr': expr,
                'desc': description,
                'status': status,
                'result': result_str[:200],
                'time': elapsed
            })

        except Exception as e:
            print(f"ERROR: {str(e)[:40]}")
            failed += 1
            errors.append((i, expr, description, str(e)[:100]))
            results_detail.append({
                'idx': i,
                'expr': expr,
                'desc': description,
                'status': 'EXCEPTION',
                'result': str(e)[:200],
                'time': 0
            })

    print()
    print("=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} passed ({100*passed/len(tests):.1f}%)")
    print(f"         {failed}/{len(tests)} failed")
    print("=" * 70)

    if errors:
        print("\nFAILED TESTS:")
        print("-" * 70)
        for idx, expr, desc, err in errors:
            print(f"[{idx}] {desc}")
            print(f"    Expr: {expr[:60]}...")
            print(f"    Error: {err}")
            print()

    # Categorize by type
    categories = {
        "Asymptotic Limits (1-15)": (1, 15),
        "Wild Series/Products (16-25)": (16, 25),
        "Ugly Integrals (26-40)": (26, 40),
        "Diophantine/NT (41-48)": (41, 48),
        "Pathological (49-50)": (49, 50)
    }

    print("\nBY CATEGORY:")
    print("-" * 70)
    for cat_name, (start_idx, end_idx) in categories.items():
        cat_passed = sum(1 for r in results_detail
                        if start_idx <= r['idx'] <= end_idx and r['status'] not in ['ERROR', 'FAILURE', 'EXCEPTION']
                        and 'error' not in r['result'].lower() and r['result'] != 'None')
        cat_total = end_idx - start_idx + 1
        print(f"  {cat_name}: {cat_passed}/{cat_total} ({100*cat_passed/cat_total:.1f}%)")

    return passed, len(tests)


if __name__ == "__main__":
    passed, total = run_edgiest_tests()
    sys.exit(0 if passed == total else 1)
