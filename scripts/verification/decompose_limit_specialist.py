#!/usr/bin/env python3
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
Script to decompose limit_specialist.py into focused sub-modules.
"""

import re
from pathlib import Path

# Define the source file
SOURCE_FILE = Path("src/symbo_agentic_reasoners/core/calculus/limit_specialist.py")
TARGET_DIR = Path("src/symbo_agentic_reasoners/core/calculus/limits")

# Create target directory if it doesn't exist
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# Read the entire file
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.splitlines(keepends=True)

# Copyright header (lines 0-12)
copyright_header = ''.join(lines[0:13])

# Module docstring template
def make_module_doc(title, description):
    return f'''"""
{title}
{'=' * len(title)}

{description}
"""

'''

# Extract imports (lines 29-37)
import_lines = ''.join(lines[29:38])

# Find all function definitions
func_pattern = re.compile(r'^(def |class )', re.MULTILINE)
matches = [(m.start(), m.group()) for m in func_pattern.finditer(content)]

# Helper to get function body
def extract_function(start_line, end_line):
    """Extract function from line range."""
    return ''.join(lines[start_line:end_line])

def find_function_end(start_idx, lines_list):
    """Find the end of a function definition."""
    indent_level = len(lines_list[start_idx]) - len(lines_list[start_idx].lstrip())
    for i in range(start_idx + 1, len(lines_list)):
        line = lines_list[i]
        if line.strip() and not line.startswith('#'):
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and (line.startswith('def ') or line.startswith('class ')):
                return i
    return len(lines_list)

# Map function line numbers
func_locations = {}
for i, line in enumerate(lines):
    if line.startswith('def ') or line.startswith('class '):
        func_name = re.match(r'(def |class )(\w+)', line).group(2)
        end_line = find_function_end(i, lines)
        func_locations[func_name] = (i, end_line)

print(f"Found {len(func_locations)} functions/classes")
print("Functions:", list(func_locations.keys())[:20])

# Extract KNOWN_LIMIT_PATTERNS (around lines 1415-2097)
# Find start and end of KNOWN_LIMIT_PATTERNS
patterns_start = None
patterns_end = None
for i, line in enumerate(lines):
    if 'KNOWN_LIMIT_PATTERNS' in line and '= {' in line:
        patterns_start = i
    if patterns_start and line.strip() == '}' and i > patterns_start + 10:
        patterns_end = i + 1
        break

if patterns_start and patterns_end:
    known_patterns = ''.join(lines[patterns_start:patterns_end])
    print(f"Found KNOWN_LIMIT_PATTERNS: lines {patterns_start}-{patterns_end}")
else:
    known_patterns = ""
    print("WARNING: Could not find KNOWN_LIMIT_PATTERNS")

# Extract PARAMETER_ASSUMPTIONS (around lines 2100-2116)
param_start = None
param_end = None
for i, line in enumerate(lines):
    if 'PARAMETER_ASSUMPTIONS' in line and '= {' in line:
        param_start = i
    if param_start and line.strip() == '}' and i > param_start + 5:
        param_end = i + 1
        break

if param_start and param_end:
    param_assumptions = ''.join(lines[param_start:param_end])
    print(f"Found PARAMETER_ASSUMPTIONS: lines {param_start}-{param_end}")
else:
    param_assumptions = ""

# Define module groupings
modules = {
    'limit_patterns.py': {
        'functions': [
            '_try_known_limit_pattern',
            '_try_nested_log_limit',
            '_try_stirling_limit',
            '_try_asymptotic_difference_limit',
            '_try_nested_limit',
            '_try_one_sided_divergent_limit',
            '_try_oscillatory_decay_limit',
            '_try_power_decay_limit',
            '_try_log_polynomial_limit',
            '_try_exp_polynomial_limit',
            '_try_pure_oscillatory_limit',
            '_try_e_type_limit',
            '_try_constant_limit',
            '_try_sinc_limit',
            '_try_one_minus_cos_limit',
            '_try_one_minus_cos_sq_limit',
            '_try_direct_substitution',
        ],
        'constants': [known_patterns, param_assumptions],
        'doc': 'Known limit pattern functions for pattern-based limit evaluation.'
    },
    'asymptotic_rules.py': {
        'functions': [
            '_try_special_function_asymptotic',
            '_try_limit_with_assumptions',
        ],
        'constants': [],
        'doc': 'Special function asymptotics and asymptotic expansion helpers.'
    },
    'taylor_limits.py': {
        'functions': [
            '_try_taylor_expansion_limit',
            'taylor_series',
        ],
        'constants': [],
        'doc': 'Taylor series expansion for limit evaluation.'
    },
    'algebra_utilities.py': {
        'functions': [
            'solve_polynomial',
            'solve_system_native',
            'factor_polynomial',
            'expand_expression',
            'solve_ode_native',
            '_eval_at_point',
            '_get_symbols',
            '_evaluate_expr_numerically',
        ],
        'constants': [],
        'doc': 'Solver and algebra utility functions.'
    },
    'gaussian_2d.py': {
        'functions': [
            '_try_2d_gaussian_integral',
            'definite_integrate_2d',
            '_try_separable_2d_integral',
        ],
        'constants': [],
        'doc': '2D Gaussian integral evaluation functions.'
    },
}

# Generate each module
for module_name, module_info in modules.items():
    print(f"\nGenerating {module_name}...")

    # Start with copyright and docstring
    module_content = copyright_header + '\n'
    module_content += make_module_doc(
        module_name.replace('.py', '').replace('_', ' ').title(),
        module_info['doc']
    )

    # Add imports
    module_content += import_lines + '\n'

    # Add constants if any
    for const in module_info['constants']:
        if const:
            module_content += const + '\n\n'

    # Add functions
    for func_name in module_info['functions']:
        if func_name in func_locations:
            start, end = func_locations[func_name]
            func_code = extract_function(start, end)
            module_content += func_code + '\n\n'
            print(f"  Added {func_name} (lines {start}-{end})")
        else:
            print(f"  WARNING: {func_name} not found!")

    # Write module file
    output_path = TARGET_DIR / module_name
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(module_content)
    print(f"  Wrote {output_path}")

print("\n=== Module generation complete ===")
print(f"Modules created in: {TARGET_DIR}")
