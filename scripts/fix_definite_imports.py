"""
Fix imports in the decomposed definite_integration modules.
"""

import os
import re

TARGET_DIR = r"c:\dev\Mathematic agent based solver\src\symbo_agentic_reasoners\core\calculus\definite_integration"

# Map of which extraction_utils functions each module needs
MODULE_IMPORTS = {
    'gaussian_integrals.py': {
        'extraction_utils': [
            '_extract_gaussian_coeff',
            '_extract_quadratic_coeff',
            '_try_evaluate_const_times_var_squared',
            '_extract_symbolic_gaussian_coeff',
            '_extract_quadratic_and_linear_coeffs',
            '_extract_positive_symbolic_coeff',
            '_extract_quadratic_coeff_with_division',
            '_is_shifted_quadratic',
            '_extract_linear_coeff_unsigned',
            '_extract_symbolic_linear_coeff_unsigned',
        ],
    },
    'exponential_integrals.py': {
        'extraction_utils': [
            '_extract_quadratic_coeff',
            '_try_evaluate_const_times_var_squared',
        ],
    },
    'special_integrals.py': {
        'extraction_utils': [
            '_extract_quadratic_coeff',
            '_extract_positive_symbolic_coeff',
            '_extract_power_of_var',
            '_extract_power_of_one_minus_var',
            '_check_quadratic_inner',
            '_is_var_squared_or_shifted',
            '_get_linear_coeff_from_mul',
            '_get_term_with_var_power',
        ],
    },
    'oscillatory_integrals.py': {
        'extraction_utils': [
            '_try_numeric_integration',
            '_extract_quadratic_coeff',
            '_evaluate_at_numeric',
            '_get_symbols',
        ],
    },
    'singularity_analysis.py': {
        'extraction_utils': [
            '_get_symbols',
            '_evaluate_at_numeric',
        ],
    },
}

def add_imports_to_module(module_name):
    """Add appropriate imports from extraction_utils to a module."""
    filepath = os.path.join(TARGET_DIR, module_name)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if this module needs extraction_utils imports
    if module_name not in MODULE_IMPORTS:
        print(f"No imports needed for {module_name}")
        return

    imports_needed = MODULE_IMPORTS[module_name]

    # Build import statement
    import_lines = []
    for source_module, functions in imports_needed.items():
        if functions:
            func_list = ', '.join(sorted(functions))
            import_lines.append(f"from .{source_module} import {func_list}")

    # Find where to insert (after the IntegrationEngine import)
    pattern = r'(from \.\.integration_specialist import IntegrationEngine\n)'
    replacement = r'\1'
    if import_lines:
        replacement += '\n# Cross-module imports\n'
        replacement += '\n'.join(import_lines) + '\n'

    content_new = re.sub(pattern, replacement, content)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_new)

    print(f"Updated {module_name} with {len(import_lines)} import(s)")

def main():
    """Fix imports in all modules."""
    modules = [
        'gaussian_integrals.py',
        'exponential_integrals.py',
        'special_integrals.py',
        'oscillatory_integrals.py',
        'singularity_analysis.py',
        'extraction_utils.py',  # No cross-imports needed
    ]

    for module in modules:
        add_imports_to_module(module)

    print("\nImport fixes complete!")

if __name__ == '__main__':
    main()
