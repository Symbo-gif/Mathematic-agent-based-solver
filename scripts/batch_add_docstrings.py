#!/usr/bin/env python3
"""
Batch Docstring Addition Tool
==============================

Intelligently adds Google-style docstrings to methods based on patterns.
Recognizes common method patterns (diff, evalf, to_latex, etc.) and
generates appropriate domain-specific documentation.

Usage:
    python scripts/batch_add_docstrings.py src/symbo_agentic_reasoners/core/symbolic/functions.py
    python scripts/batch_add_docstrings.py --directory src/symbo_agentic_reasoners/core/symbolic/ --dry-run
"""

import ast
import argparse
from pathlib import Path
from typing import Dict, Optional
import re


class IntelligentDocstringGenerator:
    """Generates context-aware docstrings based on method patterns."""

    # Method pattern templates
    TEMPLATES = {
        'diff': {
            'brief': 'Compute derivative with respect to variable.',
            'description': 'Applies differentiation rules using the chain rule.\n        Implements: d/dx {func_name}(f(x)) = [derivative formula]',
            'args': {'var': 'Variable to differentiate with respect to'},
            'returns': 'Derivative expression as symbolic Expr',
            'example_class': 'Sin',
            'example': '>>> x = Symbol(\'x\')\n        >>> {class_name}(x**2).diff(x)\n        # Returns derivative expression'
        },
        'evalf': {
            'brief': 'Numerically evaluate the expression.',
            'description': 'Evaluates the function numerically if all arguments are numeric.\n        Returns symbolic form if evaluation fails.',
            'args': {'precision': 'Number of decimal digits for precision (default: 15)'},
            'returns': 'Numerical value (float) if evaluable, otherwise symbolic Expr',
            'example': '>>> x = Symbol(\'x\')\n        >>> {class_name}(2).evalf()\n        # Returns numerical result'
        },
        'to_latex': {
            'brief': 'Convert to LaTeX representation.',
            'description': 'Generates LaTeX string for mathematical typesetting.\n        Used for rendering in Jupyter notebooks, documentation, etc.',
            'returns': 'LaTeX string representation',
            'example': '>>> {class_name}(Symbol(\'x\')).to_latex()\n        \'\\\\{latex_name}\\\\left(x\\\\right)\''
        },
        'simplify': {
            'brief': 'Simplify the expression algebraically.',
            'description': 'Applies simplification rules specific to {func_name}.\n        May evaluate constants, cancel terms, or apply identities.',
            'returns': 'Simplified expression',
            'example': '>>> {class_name}(Integer(0)).simplify()\n        # Returns simplified form'
        },
        'subs': {
            'brief': 'Substitute symbols with values or expressions.',
            'description': 'Recursively substitutes symbols throughout the expression.\n        Supports dict, positional, and keyword argument forms.',
            'args': {'substitutions': 'Symbol-to-value mappings'},
            'returns': 'New expression with substitutions applied',
            'example': '>>> x, y = Symbol(\'x\'), Symbol(\'y\')\n        >>> expr.subs(x, y)\n        # Returns expression with x replaced by y'
        },
    }

    @staticmethod
    def generate_for_method(method_name: str, class_name: str, args: list) -> Optional[str]:
        """Generate intelligent docstring based on method name pattern.

        Args:
            method_name: Name of the method
            class_name: Name of containing class
            args: List of argument names

        Returns:
            Generated docstring or None if no pattern matched
        """
        # Check if method matches known pattern
        template = None
        for pattern, tmpl in IntelligentDocstringGenerator.TEMPLATES.items():
            if method_name == pattern or method_name.endswith(f'_{pattern}'):
                template = tmpl
                break

        if not template:
            return None

        # Build docstring
        lines = [f'"""{template["brief"]}']
        lines.append('')

        # Add description
        desc = template['description'].replace('{func_name}', class_name.lower())
        desc = desc.replace('{class_name}', class_name)
        lines.append(f'        {desc}')
        lines.append('')

        # Args section
        if 'args' in template:
            lines.append('        Args:')
            for arg_name in args:
                if arg_name in template['args']:
                    lines.append(f'            {arg_name}: {template["args"][arg_name]}')
                else:
                    lines.append(f'            {arg_name}: [Description needed]')
            lines.append('')

        # Returns section
        if 'returns' in template:
            lines.append('        Returns:')
            lines.append(f'            {template["returns"]}')
            lines.append('')

        # Example section
        if 'example' in template:
            lines.append('        Example:')
            example = template['example'].replace('{class_name}', class_name)
            if '{latex_name}' in example:
                latex_name = class_name.lower()
                example = example.replace('{latex_name}', latex_name)
            lines.append(f'            {example}')
            lines.append('')

        lines.append('        """')

        return '\n'.join(lines)

    @staticmethod
    def add_docstring_to_function(source: str, func_def_line: int, docstring: str) -> str:
        """Insert docstring into source code at the appropriate location.

        Args:
            source: Full source code as string
            func_def_line: Line number where function is defined (0-indexed for list)
            docstring: Docstring to insert

        Returns:
            Modified source code with docstring inserted
        """
        lines = source.split('\n')

        # Find the line after the function signature (skip decorators and def line)
        insert_line = func_def_line

        # Skip past the def line to the first line of the function body
        while insert_line < len(lines) and ':' not in lines[insert_line]:
            insert_line += 1
        insert_line += 1  # Move to line after the ':'

        # Check if there's already a docstring
        if insert_line < len(lines) and '"""' in lines[insert_line]:
            return source  # Already has docstring

        # Insert the docstring
        indent = len(lines[insert_line]) - len(lines[insert_line].lstrip()) if insert_line < len(lines) else 8
        docstring_lines = docstring.split('\n')

        # Insert from bottom to top to preserve line numbers
        for i, doc_line in enumerate(reversed(docstring_lines)):
            lines.insert(insert_line, ' ' * indent + doc_line if doc_line.strip() else '')

        return '\n'.join(lines)


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Process a single file and add missing docstrings.

    Args:
        filepath: Path to Python file
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

    modifications = []

    # Analyze the file
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if not item.name.startswith('__'):  # Skip dunder methods
                        if ast.get_docstring(item) is None:
                            args = [arg.arg for arg in item.args.args if arg.arg != 'self']
                            docstring = IntelligentDocstringGenerator.generate_for_method(
                                item.name, class_name, args
                            )
                            if docstring:
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
        modified_source = IntelligentDocstringGenerator.add_docstring_to_function(
            modified_source, line_no - 1, docstring
        )

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified_source)

    print(f"  [DONE] Added {len(modifications)} docstrings")
    return len(modifications)


def main():
    parser = argparse.ArgumentParser(description='Batch add docstrings to Python files')
    parser.add_argument('path', nargs='?', help='File or directory to process')
    parser.add_argument('--directory', '-d', help='Process all Python files in directory')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursive directory search')
    parser.add_argument('--dry-run', action='store_true', help='Report only, don\'t modify files')

    args = parser.parse_args()

    if args.directory:
        directory = Path(args.directory)
        pattern = '**/*.py' if args.recursive else '*.py'
        total_added = 0

        for filepath in sorted(directory.glob(pattern)):
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
