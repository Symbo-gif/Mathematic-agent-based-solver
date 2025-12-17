# Quick test of Algorithm Breaking Agent

import sys
import os
import math

# Simple inline implementation for quick testing
class QuickBreaker:
    """Simplified breaker for quick testing."""

    def __init__(self):
        self.vulns = []
        self.stats = {'tested': 0, 'failed': 0}

    def test_func(self, func, name, test_inputs):
        """Test a function with inputs."""
        print(f"\nTesting: {name}")
        print("-" * 40)

        for inp in test_inputs:
            self.stats['tested'] += 1
            try:
                result = func(inp)
                if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
                    print(f"  [VULN] Input {inp} -> {result}")
                    self.vulns.append((name, inp, result, "numerical"))
                    self.stats['failed'] += 1
            except RecursionError as e:
                print(f"  [CRITICAL] Input {inp} -> RecursionError")
                self.vulns.append((name, inp, str(e)[:50], "recursion"))
                self.stats['failed'] += 1
            except ZeroDivisionError as e:
                print(f"  [HIGH] Input {inp} -> ZeroDivisionError")
                self.vulns.append((name, inp, str(e), "divzero"))
                self.stats['failed'] += 1
            except OverflowError as e:
                print(f"  [HIGH] Input {inp} -> OverflowError")
                self.vulns.append((name, inp, str(e)[:50], "overflow"))
                self.stats['failed'] += 1
            except ValueError as e:
                # Often expected, but log it
                pass
            except Exception as e:
                print(f"  [MEDIUM] Input {inp} -> {type(e).__name__}: {str(e)[:30]}")
                self.vulns.append((name, inp, str(e)[:50], "other"))
                self.stats['failed'] += 1


def test_factorial(n):
    if n < 0:
        raise ValueError("negative")
    if n <= 1:
        return 1
    return n * test_factorial(n - 1)


def test_binomial(n, k=None):
    if k is None:
        k = n // 2
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def test_gcd(a, b=100):
    while b:
        a, b = b, a % b
    return abs(a)


def test_horner(x):
    coeffs = [1, 2, 3, 4, 5]
    result = 0
    for c in reversed(coeffs):
        result = result * x + c
    return result


def test_newton(x0):
    f = lambda x: x**2 - 2
    h = 1e-8
    x = x0
    for _ in range(100):
        fx = f(x)
        if abs(fx) < 1e-10:
            return x
        dfx = (f(x + h) - f(x - h)) / (2 * h)
        if abs(dfx) < 1e-15:
            return None
        x = x - fx / dfx
    return x


# Test inputs
EDGE_CASES = [
    0, 1, -1, 2, -2,
    float('inf'), float('-inf'),
    float('nan'),
    sys.float_info.max,
    sys.float_info.min,
    1e308, -1e308,
    1e-308, -1e-308,
    1000,  # RecursionError risk for factorial
]


def main():
    print("=" * 60)
    print("QUICK ALGORITHM BREAKER TEST")
    print("=" * 60)

    breaker = QuickBreaker()

    # Test each function
    breaker.test_func(test_factorial, "factorial", [0, 1, 5, 10, 100, 500, 1000, -1])
    breaker.test_func(lambda x: test_binomial(int(x) if isinstance(x, (int, float)) and not math.isnan(x) and not math.isinf(x) else 10),
                      "binomial", [0, 1, 10, 100, -1])
    breaker.test_func(test_gcd, "gcd", [0, 1, 100, 1000, -50, float('inf'), float('nan')])
    breaker.test_func(test_horner, "horner_eval", EDGE_CASES[:10])
    breaker.test_func(test_newton, "newton_raphson", [0.1, 1.0, 10.0, -1.0, 0.0, 100.0])

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total inputs tested: {breaker.stats['tested']}")
    print(f"Vulnerabilities found: {breaker.stats['failed']}")
    print(f"Success rate: {1 - breaker.stats['failed']/max(breaker.stats['tested'],1):.1%}")

    if breaker.vulns:
        print("\nVulnerabilities Detected:")
        for name, inp, output, vtype in breaker.vulns:
            print(f"  - {name}: input={inp}, type={vtype}")

    return breaker.vulns


if __name__ == "__main__":
    vulns = main()
    print(f"\nBreaker test complete. Found {len(vulns)} issues.")
