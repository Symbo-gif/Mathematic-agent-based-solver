"""
Analyze the integration patterns in failed linear nonhomogeneous ODEs
to see what types of integrals are failing.
"""

import json
import re
from collections import Counter

def classify_product(mu_p, q_x):
    """Classify the μ(x)*Q(x) product pattern"""
    product = f"{mu_p}*{q_x}"

    # Check for exp×trig
    if 'exp' in product and ('sin' in product or 'cos' in product):
        return 'exp_trig'

    # Check for exp×polynomial
    if 'exp' in product and any(x in product for x in ['x**', 'x^', '*x']):
        return 'exp_poly'

    # Check for exp×constant
    if 'exp' in product and not any(x in q_x for x in ['x', 'sin', 'cos', 'exp']):
        return 'exp_const'

    # Check for poly×trig
    if 'x' in product and ('sin' in product or 'cos' in product) and 'exp' not in product:
        return 'poly_trig'

    return 'other'

# Sample 100 failed linear nonhomogeneous cases
results_file = 'data/benchmarks/results/ode_suite_20251220_091707.json'

with open(results_file, 'r') as f:
    data = json.load(f)

failures = [
    r for r in data['results']
    if r.get('category') == 'first_order_linear_nonhomogeneous'
    and r.get('status') == 'incorrect'
]

print(f"Total failures: {len(failures)}")
print(f"\nAnalyzing first 100 failure patterns...")

patterns = Counter()
examples = {}

for i, case in enumerate(failures[:100]):
    problem = case['problem_text']

    # Extract P(x) and Q(x) from dy/dx + P(x)*y = Q(x)
    # Simple heuristic extraction
    if '=' in problem:
        lhs, rhs = problem.split('=')
        q_x = rhs.strip()

        # Extract P from LHS (very simplified)
        # Pattern: dy/dx + (...)y or dy/dx + ...*y
        p_match = re.search(r'\+\s*\(([^)]+)\)\s*\*?\s*y', lhs)
        if not p_match:
            p_match = re.search(r'\+\s*([^*]+)\*\s*y', lhs)

        if p_match:
            p_x = p_match.group(1).strip()

            # Simulate μ(x) = exp(∫P(x)dx)
            # For pattern classification, just use P(x) representation
            mu_p = f"exp(int({p_x}))"

            pattern_type = classify_product(mu_p, q_x)
            patterns[pattern_type] += 1

            if pattern_type not in examples:
                examples[pattern_type] = (problem, f"{mu_p}*{q_x}")

print(f"\n{'='*70}")
print("PATTERN DISTRIBUTION")
print(f"{'='*70}")
for pattern, count in patterns.most_common():
    pct = count / 100 * 100
    print(f"{pattern:20s}: {count:3d} ({pct:5.1f}%)")

print(f"\n{'='*70}")
print("EXAMPLE FOR EACH PATTERN")
print(f"{'='*70}")
for pattern, (prob, prod) in examples.items():
    print(f"\n{pattern}:")
    print(f"  Problem: {prob}")
    print(f"  Product: {prod}")
