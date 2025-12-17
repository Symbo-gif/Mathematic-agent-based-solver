# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""
Failure Analysis Script - Categorize stress test failures
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Load failure report
report_path = Path(__file__).parent.parent / "tests" / "stress_test_report.json"
with open(report_path) as f:
    report = json.load(f)

# Failure categorization
categories = {
    'parser_function_missing': [],       # factorial(), gcd(), etc.
    'expression_not_evaluated': [],      # Raw expression returned
    'dict_input_not_handled': [],        # Dict inputs not converted
    'descriptive_expected': [],          # Expected is description not value
    'numeric_mismatch': [],              # Numeric computation wrong
    'solver_error': [],                  # Explicit solver errors
    'unknown': []
}

# Parse patterns
parser_missing_pattern = re.compile(r"Unexpected token|Failed to parse")
not_evaluated_pattern = re.compile(r"^\w+\(.*\)|^sum\(|^Fraction\(|^pow\(|^mod_")

for failure in report['all_failures']:
    error = failure.get('error', '') or ''
    actual = str(failure.get('actual', ''))
    expected = str(failure.get('expected', ''))
    input_data = failure.get('input_data', '')

    # Categorize
    if 'Parse failed' in error or 'dict' in error.lower():
        categories['dict_input_not_handled'].append(failure)
    elif parser_missing_pattern.search(error):
        categories['parser_function_missing'].append(failure)
    elif not_evaluated_pattern.match(actual):
        categories['expression_not_evaluated'].append(failure)
    elif expected in ['exact_integer_result', 'exists and verifiable', 'modular_exponentiation_result']:
        categories['descriptive_expected'].append(failure)
    elif 'Solver error' in error:
        categories['solver_error'].append(failure)
    elif 'Mismatch' in error:
        categories['numeric_mismatch'].append(failure)
    else:
        categories['unknown'].append(failure)

# Print summary
print("=" * 70)
print("FAILURE ANALYSIS REPORT")
print("=" * 70)
print(f"\nTotal failures: {len(report['all_failures'])}\n")

for cat, failures in sorted(categories.items(), key=lambda x: -len(x[1])):
    print(f"{cat}: {len(failures)} failures")
    if failures[:3]:
        print("  Examples:")
        for f in failures[:3]:
            error_text = str(f.get('error', ''))[:80].encode('ascii', 'ignore').decode('ascii')
            print(f"    - {f['test_id']}: {error_text}...")

print("\n" + "=" * 70)
print("MISSING PARSER FUNCTIONS")
print("=" * 70)

# Extract missing functions
missing_funcs = Counter()
for f in categories['parser_function_missing']:
    input_data = f.get('input_data', '')
    # Find function names
    funcs = re.findall(r'(\w+)\s*\(', input_data)
    for func in funcs:
        if func not in ['lambda', 'range', 'np', 'abs', 'min', 'max', 'len']:
            missing_funcs[func] += 1

for func, count in missing_funcs.most_common(20):
    print(f"  {func}: {count} occurrences")

print("\n" + "=" * 70)
print("DOMAIN BREAKDOWN")
print("=" * 70)

for domain, stats in report['domain_stats'].items():
    print(f"  {domain}: {stats['passed']}/{stats['total']} passed ({stats['pass_rate']:.1f}%)")

# Save categorized failures
output_path = Path(__file__).parent.parent / "tests" / "failure_categories.json"
output = {cat: [f['test_id'] for f in failures] for cat, failures in categories.items()}
output['counts'] = {cat: len(failures) for cat, failures in categories.items()}
output['missing_functions'] = dict(missing_funcs.most_common(30))

with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nCategorized failures saved to: {output_path}")
