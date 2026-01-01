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
Specialist Docstring Generator
================================

Auto-generate domain-aware docstrings for specialist agent methods.
Recognizes specialist types and generates appropriate documentation.

Usage:
    python scripts/specialist_docstring_generator.py <file_path>
    python scripts/specialist_docstring_generator.py --directory <dir> --recursive
"""

import ast
import argparse
from pathlib import Path
from typing import Dict, Optional, List
import re


class SpecialistDocstringGenerator:
    """Generates domain-aware docstrings for specialist methods."""

    # Domain detection patterns
    DOMAIN_PATTERNS = {
        'geometry': ['geometry', 'euclidean', 'analytic', 'solid', 'computational', 'transformation', 'trigonometry'],
        'algebra': ['algebra', 'polynomial', 'equation', 'arithmetic', 'number_theory', 'group_ring'],
        'calculus': ['calculus', 'differentiation', 'integration', 'limit', 'series', 'ode', 'fourier', 'special_functions'],
        'linear_algebra': ['linalg', 'matrix', 'vector', 'decomposition', 'tensor'],
        'logic': ['logic', 'propositional', 'predicate', 'proof', 'modal', 'temporal', 'sat'],
        'discrete_math': ['discrete', 'combinatorics', 'graph_theory', 'set_theory', 'recurrence', 'boolean', 'automata'],
        'statistics': ['statistics', 'bayesian', 'distribution', 'frequentist', 'stochastic', 'regression', 'nonparametric'],
        'numerical': ['numerical', 'optimization', 'spline', 'linear_systems', 'pde', 'quadrature'],
        'physics': ['physics', 'mechanics', 'kinematics', 'dynamics', 'energy', 'electromagnetism', 'circuits', 'magnetism', 'quantum', 'thermodynamics', 'waves', 'optics'],
        'complex_analysis': ['complex_analysis', 'analytic_functions', 'conformal', 'contour', 'residue', 'elliptic_functions'],
        'real_analysis': ['real_analysis', 'measure_theory', 'metric_space', 'sequences_series', 'function_spaces'],
        'functional_analysis': ['functional_analysis', 'banach', 'hilbert', 'operator_theory'],
        'category_theory': ['category_theory', 'morphism', 'functor', 'adjunction', 'monoidal', 'universal'],
        'cryptography': ['cryptography', 'modular', 'asymmetric', 'hash'],
        'information_theory': ['information_theory', 'entropy', 'coding', 'channel'],
        'control_theory': ['control_theory', 'dynamical_systems', 'linear_control'],
        'optimization': ['optimization', 'linear_programming', 'convex', 'combinatorial'],
        'diff_geometry': ['diff_geometry', 'differential_geometry', 'topology'],
    }

    # Method type templates
    METHOD_TEMPLATES = {
        'solve': {
            'brief': 'Solve {problem_type} problem using {algorithm}.',
            'description': 'Implements {algorithm} algorithm for solving {problem_type} problems.\n        {details}',
            'args_default': {'problem': 'Problem specification or mathematical expression'},
            'returns': 'Solution with result, steps, and metadata',
            'example_prefix': 'Solve',
        },
        'compute': {
            'brief': 'Compute {quantity} using {formula}.',
            'description': 'Calculates {quantity} using the formula: {formula}.\n        {details}',
            'returns': 'Computed numerical or symbolic result',
            'example_prefix': 'Compute',
        },
        'verify': {
            'brief': 'Verify {property} holds for {object}.',
            'description': 'Checks whether {property} is satisfied.\n        {details}',
            'returns': 'True if property holds, False otherwise',
            'example_prefix': 'Verify',
        },
        'analyze': {
            'brief': 'Analyze {structure} and extract {properties}.',
            'description': 'Performs analysis of {structure} to determine {properties}.\n        {details}',
            'returns': 'Analysis results including extracted properties',
            'example_prefix': 'Analyze',
        },
        'evaluate': {
            'brief': 'Evaluate {expression} at given values.',
            'description': 'Evaluates the {expression} numerically or symbolically.\n        {details}',
            'returns': 'Evaluated result',
            'example_prefix': 'Evaluate',
        },
        'transform': {
            'brief': 'Transform {input} to {output}.',
            'description': 'Applies transformation from {input} to {output}.\n        {details}',
            'returns': 'Transformed result',
            'example_prefix': 'Transform',
        },
        'find': {
            'brief': 'Find {target} in {space}.',
            'description': 'Searches for {target} using {algorithm}.\n        {details}',
            'returns': 'Found result or None if not found',
            'example_prefix': 'Find',
        },
        'classify': {
            'brief': 'Classify {object} into {categories}.',
            'description': 'Determines the classification of {object}.\n        {details}',
            'returns': 'Classification result',
            'example_prefix': 'Classify',
        },
    }

    @staticmethod
    def detect_domain(filepath: str) -> str:
        """Detect the mathematical domain from file path."""
        filepath_lower = filepath.lower()
        for domain, patterns in SpecialistDocstringGenerator.DOMAIN_PATTERNS.items():
            if any(pattern in filepath_lower for pattern in patterns):
                return domain
        return 'general'

    @staticmethod
    def infer_method_type(method_name: str) -> Optional[str]:
        """Infer method type from name (solve, compute, verify, etc.)."""
        for method_type in SpecialistDocstringGenerator.METHOD_TEMPLATES.keys():
            if method_name.startswith(method_type):
                return method_type
        # Check for common patterns
        if any(x in method_name for x in ['calculate', 'get']):
            return 'compute'
        if 'check' in method_name or 'is_' in method_name:
            return 'verify'
        if 'test' in method_name:
            return 'verify'
        return None

    @staticmethod
    def generate_docstring(method_name: str, args: List[str], domain: str, class_name: str = '') -> str:
        """Generate intelligent docstring for specialist method.

        Args:
            method_name: Name of the method
            args: List of argument names
            domain: Mathematical domain
            class_name: Name of containing class

        Returns:
            Generated docstring string
        """
        method_type = SpecialistDocstringGenerator.infer_method_type(method_name)

        if not method_type:
            # Generic template for unknown patterns
            return f'''"""Perform {method_name.replace('_', ' ')} operation.

        Args:
            {': Description needed'.join(f'{arg}' for arg in args if arg != 'self')}

        Returns:
            Result of the operation

        Example:
            >>> specialist = {class_name}()
            >>> result = specialist.{method_name}(...)
            # Returns result
        """'''

        template = SpecialistDocstringGenerator.METHOD_TEMPLATES[method_type]

        # Extract descriptive parts from method name
        name_parts = method_name.replace(method_type + '_', '').split('_')
        descriptive_name = ' '.join(name_parts)

        # Generate brief description
        brief = template['brief'].format(
            problem_type=domain,
            algorithm='specialized algorithm',
            quantity=descriptive_name,
            formula='mathematical formula',
            property=descriptive_name,
            object='mathematical object',
            structure=descriptive_name,
            properties='key properties',
            expression=descriptive_name,
            input='input',
            output='output',
            target=descriptive_name,
            space='search space',
            categories='appropriate categories',
        )

        # Build full docstring
        lines = [f'"""{brief}']
        lines.append('')

        # Args section
        if args and len([a for a in args if a != 'self']) > 0:
            lines.append('        Args:')
            for arg in args:
                if arg == 'self':
                    continue
                if arg in template.get('args_default', {}):
                    lines.append(f'            {arg}: {template["args_default"][arg]}')
                else:
                    # Try to infer from name
                    arg_desc = arg.replace('_', ' ').capitalize()
                    lines.append(f'            {arg}: {arg_desc}')
            lines.append('')

        # Returns section
        lines.append('        Returns:')
        lines.append(f'            {template["returns"]}')
        lines.append('')

        # Example section
        lines.append('        Example:')
        lines.append(f'            >>> specialist = {class_name}()')
        example_args = ', '.join([f'{arg}=...' for arg in args if arg != 'self'][:2])  # First 2 args
        lines.append(f'            >>> result = specialist.{method_name}({example_args})')
        lines.append('            # Returns computed result')
        lines.append('')

        lines.append('        """')

        return '\n'.join(lines)

    @staticmethod
    def add_docstring_to_method(source: str, func_def_line: int, docstring: str) -> str:
        """Insert docstring into source code.

        Args:
            source: Full source code
            func_def_line: Line number of function definition (1-indexed)
            docstring: Docstring to insert

        Returns:
            Modified source code
        """
        lines = source.split('\n')

        # Find the line after the function signature
        insert_line = func_def_line - 1  # Convert to 0-indexed

        # Skip to the first line after the def statement
        while insert_line < len(lines) and ':' not in lines[insert_line]:
            insert_line += 1
        insert_line += 1  # Move past the ':'

        # Check if docstring already exists
        if insert_line < len(lines):
            stripped = lines[insert_line].strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                return source  # Already has docstring

        # Get indentation from the next line
        if insert_line < len(lines) and lines[insert_line].strip():
            indent = len(lines[insert_line]) - len(lines[insert_line].lstrip())
        else:
            indent = 8  # Default indentation

        # Split docstring into lines and indent
        docstring_lines = docstring.split('\n')
        indented_docstring_lines = []
        for i, line in enumerate(docstring_lines):
            if line.strip():
                indented_docstring_lines.append(' ' * indent + line.lstrip())
            else:
                indented_docstring_lines.append('')

        # Insert docstring lines
        for line in reversed(indented_docstring_lines):
            lines.insert(insert_line, line)

        return '\n'.join(lines)


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Process a specialist file and add missing docstrings.

    Args:
        filepath: Path to specialist file
        dry_run: If True, report only without modifying

    Returns:
        Number of docstrings added
    """
    print(f"\nProcessing: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source, str(filepath))
    except SyntaxError as e:
        print(f"  ❌ Syntax error: {e}")
        return 0

    # Detect domain from filepath
    domain = SpecialistDocstringGenerator.detect_domain(str(filepath))
    print(f"  Detected domain: {domain}")

    modifications = []

    # Find all methods in classes
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # Skip private methods and dunder methods
                    if item.name.startswith('_'):
                        continue
                    # Check if docstring exists
                    if ast.get_docstring(item) is None:
                        args = [arg.arg for arg in item.args.args]
                        docstring = SpecialistDocstringGenerator.generate_docstring(
                            item.name, args, domain, class_name
                        )
                        modifications.append((item.lineno, item.name, class_name, docstring))

    if not modifications:
        print(f"  [OK] All methods already documented!")
        return 0

    print(f"  Found {len(modifications)} methods to document:")
    for line_no, method_name, class_name, _ in modifications:
        print(f"    Line {line_no}: {class_name}.{method_name}()")

    if dry_run:
        print(f"  [DRY RUN] Would add {len(modifications)} docstrings")
        return len(modifications)

    # Apply modifications (from bottom to top to preserve line numbers)
    modified_source = source
    for line_no, method_name, class_name, docstring in reversed(modifications):
        modified_source = SpecialistDocstringGenerator.add_docstring_to_method(
            modified_source, line_no, docstring
        )

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified_source)

    print(f"  [DONE] Added {len(modifications)} docstrings")
    return len(modifications)


def main():
    parser = argparse.ArgumentParser(description='Generate domain-aware docstrings for specialist agents')
    parser.add_argument('path', nargs='?', help='File to process')
    parser.add_argument('--directory', '-d', help='Process all Python files in directory')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursive directory search')
    parser.add_argument('--dry-run', action='store_true', help='Report only, don\'t modify files')
    parser.add_argument('--filter', help='Filter files by condition (e.g., "missing_count <= 3")')

    args = parser.parse_args()

    if args.directory:
        directory = Path(args.directory)
        pattern = '**/*_specialist.py' if args.recursive else '*_specialist.py'

        # Also include *_agent.py files
        patterns = [pattern, pattern.replace('specialist', 'agent')]

        total_added = 0
        for pat in patterns:
            for filepath in sorted(directory.glob(pat)):
                if filepath.is_file() and '__pycache__' not in str(filepath):
                    added = process_file(filepath, dry_run=args.dry_run)
                    total_added += added

        print(f"\n{'=' * 70}")
        print(f"TOTAL DOCSTRINGS {'WOULD BE ' if args.dry_run else ''}ADDED: {total_added}")

    elif args.path:
        filepath = Path(args.path)
        process_file(filepath, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
