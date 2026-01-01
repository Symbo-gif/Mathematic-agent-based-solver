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
Extract functions from definite_integration_specialist.py and organize into modules.
"""

import re

SOURCE_FILE = r"c:\dev\Mathematic agent based solver\src\symbo_agentic_reasoners\core\calculus\definite_integration_specialist.py"
TARGET_DIR = r"c:\dev\Mathematic agent based solver\src\symbo_agentic_reasoners\core\calculus\definite_integration"

# Function name to line ranges mapping (approximate - will extract until next function)
FUNCTION_GROUPS = {
    'gaussian_integrals.py': [
        '_try_gaussian_integral',
        '_try_gaussian_moment_integral',
        '_try_half_gaussian_integral',
        '_try_completion_square_gaussian',
        '_try_gaussian_fourier_integral',
        '_try_oscillatory_gaussian_integral',
        '_try_linear_gaussian_full_line',
        '_try_symbolic_gaussian_integral',
        '_extract_gaussian_coeff',
        '_extract_symbolic_gaussian_coeff',
        '_evaluate_gaussian_moment_term',
        '_try_standard_normal_integral',
    ],
    'exponential_integrals.py': [
        '_try_exponential_ray_integral',
        '_try_exponential_ray_moments',
        '_try_linear_exponential_ray',
        '_evaluate_monomial_exp_integral',
        '_extract_linear_coeff',
        '_extract_linear_coeff_unsigned',
        '_extract_symbolic_linear_coeff',
        '_extract_symbolic_linear_coeff_unsigned',
    ],
    'special_integrals.py': [
        '_try_lorentzian_power_integral',
        '_try_beta_integral',
        '_try_heat_kernel_integral',
        '_try_green_function_integral',
        '_try_gamma_power_integral',
        '_try_semicircle_integral',
        '_evaluate_beta',
        '_extract_lorentzian_m_squared',
        '_extract_semicircle_radius',
    ],
    'oscillatory_integrals.py': [
        '_try_oscillatory_integral',
        '_try_fresnel_cube_integral',
        '_try_sinc_log_integral',
        '_try_euler_gamma_integral',
        '_check_oscillatory_divergence',
        '_try_power_integral_convergence',
        '_check_symmetry_integral',
    ],
    'singularity_analysis.py': [
        '_check_log_singularity',
        '_check_pole_singularity',
        '_check_log_power_integral',
        '_analyze_singularities',
        '_find_potential_singularities',
        '_find_zeros',
        '_evaluate_limit',
        '_evaluate_at',
    ],
    'extraction_utils.py': [
        '_extract_gaussian_coeff',
        '_extract_quadratic_coeff',
        '_extract_quadratic_coeff_with_division',
        '_extract_quadratic_and_linear_coeffs',
        '_extract_power_of_var',
        '_extract_power_of_one_minus_var',
        '_extract_positive_symbolic_coeff',
        '_extract_linear_coeff',
        '_extract_linear_coeff_unsigned',
        '_extract_lorentzian_m_squared',
        '_extract_semicircle_radius',
        '_extract_symbolic_gaussian_coeff',
        '_extract_symbolic_linear_coeff',
        '_extract_symbolic_linear_coeff_unsigned',
        '_check_quadratic_inner',
        '_is_shifted_quadratic',
        '_is_var_squared_or_shifted',
        '_try_evaluate_const_times_var_squared',
        '_get_linear_coeff_from_mul',
        '_get_term_with_var_power',
        '_expr_to_str',
        '_get_symbols',
        '_evaluate_at_numeric',
        '_fix_exponent_precedence_inline',
        '_try_numeric_integration',
        '_find_potential_singularities',
        '_find_zeros',
    ],
}

def read_file():
    """Read the entire source file."""
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        return f.readlines()

def find_function_ranges(lines):
    """Find line ranges for each function."""
    function_starts = {}
    for i, line in enumerate(lines):
        match = re.match(r'^def\s+(\w+)\s*\(', line)
        if match:
            func_name = match.group(1)
            function_starts[func_name] = i

    # Sort by line number
    sorted_funcs = sorted(function_starts.items(), key=lambda x: x[1])

    # Create ranges (start to next function or end)
    function_ranges = {}
    for idx, (func_name, start_line) in enumerate(sorted_funcs):
        if idx + 1 < len(sorted_funcs):
            end_line = sorted_funcs[idx + 1][1]
        else:
            end_line = len(lines)
        function_ranges[func_name] = (start_line, end_line)

    return function_ranges

def extract_header(lines):
    """Extract the header (copyright, imports) up to first function."""
    header_lines = []
    for line in lines:
        if re.match(r'^def\s+', line):
            break
        header_lines.append(line)
    return header_lines

def create_module(module_name, func_names, lines, function_ranges, header):
    """Create a module file with extracted functions."""
    module_lines = []

    # Add header (copyright and docstring)
    for line in header[:33]:  # Up to imports
        module_lines.append(line)

    # Add module-specific docstring
    module_lines.append(f'"""\n')
    module_lines.append(f'{module_name.replace(".py", "").replace("_", " ").title()}\n')
    module_lines.append(f'{"=" * 50}\n')
    module_lines.append(f'\n')
    module_lines.append(f'Extracted from definite_integration_specialist.py\n')
    module_lines.append(f'"""\n\n')

    # Add imports
    module_lines.append('import logging\n')
    module_lines.append('import math\n')
    module_lines.append('import re\n')
    module_lines.append('from typing import Optional, Tuple, Union, Dict, Any, List\n')
    module_lines.append('\n')
    module_lines.append('from ..ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func\n')
    module_lines.append('from ..expression_parser import ExprParser\n')
    module_lines.append('from ..validation import check_expression_safety as _check_expression_safety\n')
    module_lines.append('from ..calculus_utils import _simplify_output, _try_evaluate_const\n')
    module_lines.append('from ..integration_specialist import IntegrationEngine\n')
    module_lines.append('\n')
    module_lines.append('logger = logging.getLogger(__name__)\n')
    module_lines.append('\n')
    module_lines.append('# Module-level instances\n')
    module_lines.append('_parser = ExprParser()\n')
    module_lines.append('_int_engine = IntegrationEngine()\n')
    module_lines.append('\n')
    module_lines.append('\n')

    # Extract each function
    for func_name in func_names:
        if func_name in function_ranges:
            start, end = function_ranges[func_name]
            module_lines.extend(lines[start:end])
            module_lines.append('\n')

    # Write to file
    output_path = f"{TARGET_DIR}\\{module_name}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(module_lines)

    print(f"Created {module_name} with {len(func_names)} functions")
    return len(module_lines)

def main():
    """Main extraction process."""
    lines = read_file()
    function_ranges = find_function_ranges(lines)
    header = extract_header(lines)

    print(f"Found {len(function_ranges)} functions total")
    print(f"Header has {len(header)} lines\n")

    # Create each module
    stats = {}
    for module_name, func_names in FUNCTION_GROUPS.items():
        line_count = create_module(module_name, func_names, lines, function_ranges, header)
        stats[module_name] = line_count

    print("\nModule Statistics:")
    for module, count in stats.items():
        print(f"  {module}: {count} lines")

    print(f"\nTotal lines extracted: {sum(stats.values())}")

if __name__ == '__main__':
    main()
