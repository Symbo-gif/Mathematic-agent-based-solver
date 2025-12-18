#!/usr/bin/env python3
"""
Docstring Template Generator
=============================

Generates Google-style docstring templates for methods missing documentation.
Analyzes function signatures and creates boilerplate that requires manual completion.

Usage:
    python scripts/generate_docstring_templates.py <filepath>
    python scripts/generate_docstring_templates.py --directory src/symbo_agentic_reasoners/core/symbolic/
    python scripts/generate_docstring_templates.py --report  # Just report, don't generate
"""

import ast
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import sys


class DocstringGenerator:
    """Generates Google-style docstring templates from function signatures."""

    @staticmethod
    def generate_docstring(func_node: ast.FunctionDef, class_name: Optional[str] = None) -> str:
        """Generate a Google-style docstring template for a function.

        Args:
            func_node: AST node representing the function
            class_name: Name of containing class (if method)

        Returns:
            Formatted docstring template as a string
        """
        func_name = func_node.name
        args = func_node.args
        returns = func_node.returns

        # Extract argument names (skip 'self' for methods)
        arg_names = [arg.arg for arg in args.args if arg.arg != 'self']

        # Get return type annotation if available
        return_type = ast.unparse(returns) if returns else 'Any'

        # Build docstring
        lines = ['"""[BRIEF DESCRIPTION - TODO]']
        lines.append('')

        # Add detailed description placeholder
        if class_name:
            lines.append(f'    [Detailed description of what this {class_name} method does.]')
        else:
            lines.append('    [Detailed description of what this function does.]')
        lines.append('')

        # Args section
        if arg_names:
            lines.append('    Args:')
            for arg_name in arg_names:
                # Try to infer type from annotation
                arg_node = next((a for a in args.args if a.arg == arg_name), None)
                if arg_node and arg_node.annotation:
                    arg_type = ast.unparse(arg_node.annotation)
                    lines.append(f'        {arg_name}: [Description] (type: {arg_type})')
                else:
                    lines.append(f'        {arg_name}: [Description]')
            lines.append('')

        # Returns section
        if return_type and return_type != 'None':
            lines.append('    Returns:')
            lines.append(f'        [Description of return value] (type: {return_type})')
            lines.append('')

        # Raises section (common for mathematical operations)
        if func_name in ['diff', 'evalf', 'simplify', 'solve', 'compute', 'calculate']:
            lines.append('    Raises:')
            lines.append('        ValueError: [Conditions that raise ValueError]')
            lines.append('        TypeError: [Conditions that raise TypeError]')
            lines.append('')

        # Example section
        lines.append('    Example:')
        lines.append('        >>> # TODO: Add example')
        lines.append('        >>> pass')
        lines.append('')

        # Notes section for complex methods
        if len(arg_names) > 3 or func_name in ['integrate', 'differentiate', 'solve', 'prove']:
            lines.append('    Notes:')
            lines.append('        - Algorithm: [Describe algorithm used]')
            lines.append('        - Complexity: O([complexity])')
            lines.append('        - See Also: [Related methods]')
            lines.append('')

        lines.append('    """')

        # Indent appropriately (assuming method indentation)
        indent = '        ' if class_name else '    '
        return '\n'.join(indent + line if line else '' for line in lines)

    @staticmethod
    def analyze_file(filepath: Path) -> List[Tuple[int, str, str, Optional[str]]]:
        """Analyze a Python file for methods missing docstrings.

        Args:
            filepath: Path to Python file

        Returns:
            List of (line_no, func_name, class_name_or_none, generated_docstring)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content, str(filepath))
        except SyntaxError as e:
            print(f"Syntax error in {filepath}: {e}")
            return []

        missing = []

        # Properly traverse the AST tree
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                # Check methods in the class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith('__'):  # Skip dunder methods
                            if ast.get_docstring(item) is None:
                                docstring = DocstringGenerator.generate_docstring(item, class_name)
                                missing.append((item.lineno, item.name, class_name, docstring))
            elif isinstance(node, ast.FunctionDef):
                # Module-level function
                if not node.name.startswith('__') and not node.name.startswith('_'):
                    if ast.get_docstring(node) is None:
                        docstring = DocstringGenerator.generate_docstring(node, None)
                        missing.append((node.lineno, node.name, None, docstring))

        return missing

    @staticmethod
    def generate_report(directory: Path, recursive: bool = True) -> dict:
        """Generate a report of files needing docstrings.

        Args:
            directory: Directory to analyze
            recursive: Whether to search recursively

        Returns:
            Dictionary with file paths and missing count
        """
        pattern = '**/*.py' if recursive else '*.py'
        report = {}

        for filepath in directory.glob(pattern):
            if filepath.is_file():
                missing = DocstringGenerator.analyze_file(filepath)
                if missing:
                    rel_path = filepath.relative_to(directory.parent if directory.name != 'src' else directory)
                    report[str(rel_path)] = len(missing)

        return report


def main():
    parser = argparse.ArgumentParser(description='Generate docstring templates for Python files')
    parser.add_argument('path', nargs='?', help='File or directory to process')
    parser.add_argument('--directory', '-d', help='Process all Python files in directory')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursive directory search')
    parser.add_argument('--report', action='store_true', help='Generate report only, no templates')
    parser.add_argument('--output', '-o', help='Output file for templates (default: stdout)')

    args = parser.parse_args()

    if args.report:
        # Generate coverage report
        directory = Path(args.directory or args.path or 'src/symbo_agentic_reasoners')
        report = DocstringGenerator.generate_report(directory, recursive=args.recursive)

        print("=" * 70)
        print("DOCSTRING COVERAGE REPORT")
        print("=" * 70)
        print(f"\nDirectory: {directory}")
        print(f"Total files with missing docstrings: {len(report)}")
        print(f"\nFiles sorted by missing count:")
        print("-" * 70)

        for filepath, count in sorted(report.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {filepath}: {count} methods")

        total_missing = sum(report.values())
        print(f"\nTOTAL METHODS MISSING DOCSTRINGS: {total_missing}")
        return

    # Generate templates for specific file
    if args.directory:
        directory = Path(args.directory)
        for filepath in directory.glob('*.py'):
            print(f"\nProcessing: {filepath}")
            missing = DocstringGenerator.analyze_file(filepath)
            if missing:
                print(f"  Found {len(missing)} methods without docstrings")
                for line_no, func_name, class_name, docstring in missing:
                    context = f"{class_name}.{func_name}" if class_name else func_name
                    print(f"    Line {line_no}: {context}()")
    elif args.path:
        filepath = Path(args.path)
        missing = DocstringGenerator.analyze_file(filepath)

        if not missing:
            print(f"✅ {filepath}: All methods have docstrings!")
            return

        print(f"Found {len(missing)} methods without docstrings in {filepath}:")
        print("=" * 70)

        for line_no, func_name, class_name, docstring in missing:
            context = f"{class_name}.{func_name}" if class_name else func_name
            print(f"\nLine {line_no}: {context}()")
            print("-" * 70)
            print(docstring)
            print()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
