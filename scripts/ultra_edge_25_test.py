#!/usr/bin/env python3
"""
25 "Ultra-Edge" Mathematical Stress Tests
==========================================
These are deliberately extreme: higher-order asymptotics, special
functions with correction terms, Diophantine edge cases, and tricky integrals.
Many are "formal targets" rather than things a CAS will fully simplify.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.core.solver_engine import get_solver_engine, SolveStatus


def run_ultra_edge_tests():
    """Run all 25 ultra-edge tests."""

    solver = get_solver_engine()

    # 25 "Ultra-Edge" tests with higher-order corrections
    tests = [
        # 1-10: Asymptotic & Stokes-Flavor Monsters (HIGHER ORDER)
        ("limit((log(Gamma(x)) - (x - 1/2)*log(x) + x - 1/2*log(2*pi) - 1/(12*x)) * x, x, oo)",
         "Stirling next correction * x"),
        ("limit((zeta(1 + 1/x) - x - gamma - 1/(2*x)) * x, x, oo)",
         "Zeta pole next correction * x"),
        ("limit((Ei(x) - gamma - log(abs(x)) - x - x**2/4 - x**3/18)/x**4, x, 0)",
         "Ei 4th order Taylor"),
        ("limit((erf(x) - 2*x/sqrt(pi) + 2*x**3/(3*sqrt(pi)) - 4*x**5/(15*sqrt(pi)))/x**7, x, 0)",
         "erf 7th order Taylor"),
        ("limit((BesselJ(0,x) - sqrt(2/(pi*x))*cos(x - pi/4) + 1/(8*sqrt(2*pi)*x**(3/2))*sin(x - pi/4))*x**(5/2), x, oo)",
         "BesselJ0 2nd order asymp"),
        ("limit((BesselY(0,x) - sqrt(2/(pi*x))*sin(x - pi/4) - 1/(8*sqrt(2*pi)*x**(3/2))*cos(x - pi/4))*x**(5/2), x, oo)",
         "BesselY0 2nd order asymp"),
        ("limit((Ai(x) - 1/(2*sqrt(pi))*x**(-1/4)*exp(-2*x**(3/2)/3)*(1 - 5/(48*x**(3/2)))), x, oo)",
         "Airy Ai 2nd order asymp"),
        ("limit((Bi(x) - 1/sqrt(pi)*x**(-1/4)*exp(2*x**(3/2)/3)*(1 + 5/(48*x**(3/2)))), x, oo)",
         "Airy Bi 2nd order asymp"),
        ("limit((x*log(log(x)) - log(x))/log(log(x)), x, oo)",
         "Nested log difference ratio"),
        ("limit((log(log(log(x))) - log(log(x))/log(x))*log(x), x, oo)",
         "Triple nested log product"),

        # 11-16: Brutal Series / Products / NT Blends
        ("summation(((-1)**n * log(n))/sqrt(n), (n,2,oo))",
         "Alt log/sqrt series"),
        ("summation(mu(n)*log(n)/n, (n,2,oo))",
         "Mobius log series"),
        ("summation((H_n - log(n) - gamma)/n, (n,1,oo))",
         "Harmonic correction sum"),
        ("summation(((-1)**n)/(n*(log(n))*(log(log(n)))), (n,3,oo))",
         "Nested log alt series"),
        ("product((1 - 1/p**s), (p, primes))",
         "Euler product zeta"),
        ("summation(q**(n**2 + n), (n,-oo,oo))",
         "Theta-like series"),

        # 17-20: Integrals That Want Special Functions
        ("integrate(log(1 - x)/x, (x,0,1))",
         "Dilogarithm at 1"),
        ("integrate((log(x))**2/(1 + x), (x,0,1))",
         "Log^2/(1+x) integral"),
        ("integrate((x - floor(x) - 1/2)/x**2, (x,1,oo))",
         "Fractional part integral"),
        ("integrate(exp(-x**2)*(cos(2*x) - 1), (x,0,oo))",
         "Gaussian oscillatory diff"),

        # 21-23: Diophantine "Fruit" Near the Edge
        ("diophantine(x**3 + y**3 + z**3 - 33)",
         "Sum of 3 cubes = 33"),
        ("diophantine(2*x**2 + 3*y**2 + 5*z**2 - 7*w**2 - 1)",
         "Quaternary mixed"),
        ("diophantine(x**4 + y**4 + z**4 - w**4)",
         "Sum of 4th powers"),

        # 24-25: Mixed Asymptotic / Special-Function Hybrids
        ("limit((Li(x) - x/log(x) - x/(log(x))**2)/(x/(log(x))**3), x, oo)",
         "Li 3rd order asymp"),
        ("limit((BesselJ(0,x) + I*BesselY(0,x))/(sqrt(2/(pi*x))*exp(I*(x - pi/4))), x, oo)",
         "Complex Bessel Hankel"),
    ]

    print("=" * 70)
    print("25 ULTRA-EDGE MATHEMATICAL STRESS TESTS")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print()

    passed = 0
    failed = 0
    errors = []
    results_detail = []

    for i, (expr, description) in enumerate(tests, 1):
        print(f"[{i:2d}/25] {description[:50]:<50}", end=" ")

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
            print(f"    Expr: {expr[:70]}...")
            print(f"    Error: {err}")
            print()

    # Categorize by type
    categories = {
        "Higher-Order Asymptotics (1-10)": (1, 10),
        "Series/Products/NT (11-16)": (11, 16),
        "Special Integrals (17-20)": (17, 20),
        "Diophantine (21-23)": (21, 23),
        "Hybrids (24-25)": (24, 25)
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
    passed, total = run_ultra_edge_tests()
    sys.exit(0 if passed == total else 1)
