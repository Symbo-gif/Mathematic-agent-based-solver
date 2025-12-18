#!/usr/bin/env python3
"""
Specialized Docstring Adder for Symbolic Core
==============================================

Adds high-quality, pattern-aware docstrings to symbolic math functions.
Understands mathematical function patterns (trig, exp, log, etc.).
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


# Domain-specific templates for mathematical functions
MATH_FUNCTION_TEMPLATES = {
    'diff': {
        'Sin': '"""Compute derivative of sin(f) with respect to var.\n\n        Uses chain rule: d/dx sin(f(x)) = cos(f(x)) * f\'(x)\n\n        Args:\n            var: Variable to differentiate with respect to\n\n        Returns:\n            Derivative expression\n\n        Example:\n            >>> x = Symbol(\'x\')\n            >>> Sin(x**2).diff(x)\n            2*x*cos(x**2)\n        """',
        'Cos': '"""Compute derivative of cos(f) with respect to var.\n\n        Uses chain rule: d/dx cos(f(x)) = -sin(f(x)) * f\'(x)\n\n        Args:\n            var: Variable to differentiate with respect to\n\n        Returns:\n            Derivative expression\n\n        Example:\n            >>> x = Symbol(\'x\')\n            >>> Cos(x**2).diff(x)\n            -2*x*sin(x**2)\n        """',
        'Tan': '"""Compute derivative of tan(f) with respect to var.\n\n        Uses chain rule: d/dx tan(f(x)) = sec²(f(x)) * f\'(x) = f\'(x)/cos²(f(x))\n\n        Args:\n            var: Variable to differentiate with respect to\n\n        Returns:\n            Derivative expression\n\n        Example:\n            >>> x = Symbol(\'x\')\n            >>> Tan(x).diff(x)\n            1/cos(x)**2\n        """',
        'Exp': '"""Compute derivative of exp(f) with respect to var.\n\n        Uses chain rule: d/dx exp(f(x)) = exp(f(x)) * f\'(x)\n\n        Args:\n            var: Variable to differentiate with respect to\n\n        Returns:\n            Derivative expression\n\n        Example:\n            >>> x = Symbol(\'x\')\n            >>> Exp(x**2).diff(x)\n            2*x*exp(x**2)\n        """',
        'Log': '"""Compute derivative of log(f) with respect to var.\n\n        Uses chain rule: d/dx log(f(x)) = f\'(x)/f(x)\n\n        Args:\n            var: Variable to differentiate with respect to\n\n        Returns:\n            Derivative expression\n\n        Example:\n            >>> x = Symbol(\'x\')\n            >>> Log(x**2).diff(x)\n            2/x\n        """',
        'Sqrt': '"""Compute derivative of sqrt(f) with respect to var.\n\n        Uses chain rule: d/dx sqrt(f(x)) = f\'(x)/(2*sqrt(f(x)))\n\n        Args:\n            var: Variable to differentiate with respect to\n\n        Returns:\n            Derivative expression\n\n        Example:\n            >>> x = Symbol(\'x\')\n            >>> Sqrt(x**2).diff(x)\n            x/abs(x)\n        """',
    },
    'evalf': {
        '_default': '"""Numerically evaluate the expression.\n\n        Evaluates the function to a floating-point number if all\n        arguments are numeric. Returns symbolic form if evaluation fails.\n\n        Args:\n            precision: Number of decimal digits for precision (default: 15)\n\n        Returns:\n            Numerical value (float) if evaluable, otherwise symbolic Expr\n\n        Example:\n            >>> {class_name}(2.5).evalf()\n            # Returns numerical result\n        """'
    },
    'to_latex': {
        '_default': '"""Convert to LaTeX representation.\n\n        Generates LaTeX string for mathematical typesetting.\n        Used for rendering in Jupyter notebooks and documentation.\n\n        Returns:\n            LaTeX string representation\n\n        Example:\n            >>> x = Symbol(\'x\')\n            >>> {class_name}(x).to_latex()\n            # Returns LaTeX formatted string\n        """'
    },
    'simplify': {
        '_default': '"""Simplify the expression algebraically.\n\n        Applies domain-specific simplification rules:\n        - Evaluates constants\n        - Applies mathematical identities\n        - Reduces to simplest form\n\n        Returns:\n            Simplified expression\n\n        Example:\n            >>> {class_name}(...).simplify()\n            # Returns simplified form\n        """'
    }
}


def add_docstring_after_def(content: str, line_num: int, docstring: str) -> str:
    """Insert docstring after a function definition.

    Args:
        content: Full file content
        line_num: Line number of function def (0-indexed)
        docstring: Docstring to insert

    Returns:
        Modified content
    """
    lines = content.split('\n')

    # Find the colon ending the def line
    insert_index = line_num
    while insert_index < len(lines) and ':' not in lines[insert_index]:
        insert_index += 1
    insert_index += 1  # Insert after the def line

    # Determine indentation from the next non-empty line
    indent = 8  # Default for methods
    if insert_index < len(lines):
        next_line = lines[insert_index]
        if next_line.strip():
            indent = len(next_line) - len(next_line.lstrip())

    # Add docstring with proper indentation
    docstring_lines = docstring.split('\n')
    for i, line in enumerate(docstring_lines):
        lines.insert(insert_index + i, ' ' * indent + line if line.strip() else '')

    return '\n'.join(lines)


def process_symbolic_file(filepath: Path, dry_run: bool = False) -> int:
    """Process a symbolic core file and add intelligent docstrings.

    Args:
        filepath: Path to file
        dry_run: If True, report only

    Returns:
        Number of docstrings added
    """
    print(f"\nProcessing: {filepath.name}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all class definitions and their methods
    class_pattern = r'^class\s+(\w+)\(Function\):'
    method_pattern = r'^    def\s+(\w+)\([^)]*\):'

    current_class = None
    additions = []

    for i, line in enumerate(content.split('\n')):
        # Check for class definition
        class_match = re.match(class_pattern, line)
        if class_match:
            current_class = class_match.group(1)
            continue

        # Check for method definition
        method_match = re.match(method_pattern, line)
        if method_match and current_class:
            method_name = method_match.group(1)

            # Skip if already has docstring (check next non-empty line)
            next_lines = content.split('\n')[i+1:i+3]
            if any('"""' in l for l in next_lines):
                continue

            # Generate appropriate docstring
            docstring = None

            # Check for specific templates
            if method_name in MATH_FUNCTION_TEMPLATES:
                if current_class in MATH_FUNCTION_TEMPLATES[method_name]:
                    docstring = MATH_FUNCTION_TEMPLATES[method_name][current_class]
                elif '_default' in MATH_FUNCTION_TEMPLATES[method_name]:
                    template = MATH_FUNCTION_TEMPLATES[method_name]['_default']
                    docstring = template.replace('{class_name}', current_class)

            if docstring:
                additions.append((i, current_class, method_name, docstring))

    if not additions:
        print(f"  [OK] All methods already documented!")
        return 0

    print(f"  Found {len(additions)} methods to document:")
    for line_num, cls, method, _ in additions[:10]:
        print(f"    Line {line_num+1}: {cls}.{method}()")
    if len(additions) > 10:
        print(f"    ... and {len(additions)-10} more")

    if dry_run:
        print(f"  [DRY RUN] Would add {len(additions)} docstrings")
        return len(additions)

    # Apply modifications from bottom to top
    modified_content = content
    for line_num, cls, method, docstring in reversed(additions):
        modified_content = add_docstring_after_def(modified_content, line_num, docstring)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    print(f"  [DONE] Added {len(additions)} docstrings")
    return len(additions)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', help='Single file to process')
    parser.add_argument('--all', action='store_true', help='Process all symbolic core files')
    parser.add_argument('--dry-run', action='store_true', help='Report only')
    args = parser.parse_args()

    base_dir = Path('src/symbo_agentic_reasoners/core/symbolic')

    if args.all:
        files = [
            base_dir / 'function_library.py',
            base_dir / 'type_system.py',
            base_dir / 'numeric_types.py',
            base_dir / 'composite_operations.py',
        ]
        total = 0
        for f in files:
            if f.exists():
                total += process_symbolic_file(f, args.dry_run)
        print(f"\n{'='*70}")
        print(f"TOTAL DOCSTRINGS ADDED: {total}")
    elif args.file:
        process_symbolic_file(Path(args.file), args.dry_run)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
