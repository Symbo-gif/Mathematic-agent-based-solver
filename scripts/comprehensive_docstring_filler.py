#!/usr/bin/env python3
"""
Comprehensive Docstring Filler
================================

Finds and documents ALL undocumented methods regardless of type.
Handles properties, helpers, BDI methods, nested classes, etc.

Usage:
    python scripts/comprehensive_docstring_filler.py <file>
    python scripts/comprehensive_docstring_filler.py --directory <dir> --recursive
    python scripts/comprehensive_docstring_filler.py --all  # Process entire codebase
"""

import ast
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


class ComprehensiveDocstringFiller:
    """Generates docstrings for ANY undocumented method/property/class."""

    # BDI lifecycle method templates
    BDI_TEMPLATES = {
        'update_beliefs': '''"""Update agent beliefs based on new information (BDI lifecycle).

        Processes incoming messages and updates internal belief state.
        Part of the Belief-Desire-Intention agent architecture.

        Example:
            >>> agent.update_beliefs()
        """''',
        'deliberate': '''"""Select next action based on beliefs and desires (BDI lifecycle).

        Analyzes current beliefs to determine best course of action.
        Part of the Belief-Desire-Intention agent architecture.

        Example:
            >>> agent.deliberate()
        """''',
        'execute_step': '''"""Execute one step of the agent's plan (BDI lifecycle).

        Performs the currently planned action.
        Part of the Belief-Desire-Intention agent architecture.

        Example:
            >>> agent.execute_step()
        """''',
        'process_message': '''"""Process incoming message and route to appropriate handler.

        Args:
            message: Incoming message from another agent or system

        Returns:
            Processing result or None

        Example:
            >>> result = agent.process_message(msg)
        """''',
        'get_stats': '''"""Retrieve agent statistics.

        Returns:
            dict: Agent statistics including solve count, success rate, etc.

        Example:
            >>> stats = agent.get_stats()
        """''',
        'get_statistics': '''"""Retrieve agent statistics.

        Returns:
            dict: Agent statistics including solve count, success rate, etc.

        Example:
            >>> stats = agent.get_statistics()
        """''',
    }

    # Common patterns
    PATTERN_TEMPLATES = {
        'property': '''"""Property: {name}.

        Returns:
            {return_desc}
        """''',
        'helper': '''"""Helper method: {name}.

        {description}

        Returns:
            Result of the operation
        """''',
        'compute': '''"""Compute {what}.

        Args:
            {args}

        Returns:
            Computed result

        Example:
            >>> result = obj.{method_name}(...)
        """''',
        'check': '''"""Check {what}.

        Args:
            {args}

        Returns:
            bool: True if check passes, False otherwise

        Example:
            >>> if obj.{method_name}(...):
            ...     print("Check passed")
        """''',
        'is': '''"""Check if {what}.

        Returns:
            bool: True if condition holds, False otherwise

        Example:
            >>> obj.{method_name}
            True
        """''',
    }

    @staticmethod
    def generate_docstring(node: ast.FunctionDef, class_name: str = '') -> str:
        """Generate appropriate docstring based on method type and name.

        Args:
            node: AST node for the method
            class_name: Name of containing class

        Returns:
            Generated docstring
        """
        method_name = node.name
        args = [arg.arg for arg in node.args.args if arg.arg != 'self']

        # Check if it's a BDI lifecycle method
        if method_name in ComprehensiveDocstringFiller.BDI_TEMPLATES:
            return ComprehensiveDocstringFiller.BDI_TEMPLATES[method_name]

        # Check if it's a property
        is_property = any(isinstance(dec, ast.Name) and dec.id == 'property' for dec in node.decorator_list)
        if is_property:
            name_readable = method_name.replace('_', ' ')
            return_desc = f"{name_readable.capitalize()} value"
            return f'''"""Property: {name_readable}.

        Returns:
            {return_desc}
        """'''

        # Check method name patterns
        if method_name.startswith('compute_'):
            what = method_name.replace('compute_', '').replace('_', ' ')
            args_str = '\n            '.join([f'{arg}: Parameter for computation' for arg in args])
            return f'''"""Compute {what}.

        Args:
            {args_str if args else 'No arguments'}

        Returns:
            Computed result

        Example:
            >>> result = {class_name.lower() if class_name else 'obj'}.{method_name}(...)
        """'''

        if method_name.startswith('is_'):
            what = method_name.replace('is_', '').replace('_', ' ')
            return f'''"""Check if {what}.

        Returns:
            bool: True if condition holds, False otherwise

        Example:
            >>> obj.{method_name}
            True
        """'''

        if method_name.startswith('get_'):
            what = method_name.replace('get_', '').replace('_', ' ')
            return f'''"""Get {what}.

        Returns:
            {what.capitalize()} value or data

        Example:
            >>> result = obj.{method_name}()
        """'''

        if method_name.startswith('check_') or method_name.startswith('verify_'):
            prefix = 'check_' if 'check' in method_name else 'verify_'
            what = method_name.replace(prefix, '').replace('_', ' ')
            args_str = '\n            '.join([f'{arg}: Parameter to {prefix[:-1]}' for arg in args])
            return f'''"""{'Check' if 'check' in method_name else 'Verify'} {what}.

        Args:
            {args_str if args else 'No arguments'}

        Returns:
            bool: True if {prefix[:-1]} passes, False otherwise

        Example:
            >>> if obj.{method_name}(...):
            ...     print("Validation passed")
        """'''

        if method_name.startswith('find_') or method_name.startswith('search_'):
            prefix = 'find_' if 'find' in method_name else 'search_'
            what = method_name.replace(prefix, '').replace('_', ' ')
            return f'''"""{'Find' if 'find' in method_name else 'Search for'} {what}.

        Returns:
            Found result or None

        Example:
            >>> result = obj.{method_name}(...)
        """'''

        # Generic fallback
        readable_name = method_name.replace('_', ' ')
        args_str = '\n            '.join([f'{arg}: Description needed' for arg in args])
        return f'''"""Perform {readable_name} operation.

        Args:
            {args_str if args else 'No arguments'}

        Returns:
            Result of the operation

        Example:
            >>> result = obj.{method_name}(...)
        """'''

    @staticmethod
    def insert_docstring(source: str, node: ast.FunctionDef, docstring: str) -> str:
        """Insert docstring into method.

        Args:
            source: Full source code
            node: Function node
            docstring: Docstring to insert

        Returns:
            Modified source code
        """
        lines = source.split('\n')
        # Function starts at node.lineno (1-indexed)
        func_line = node.lineno - 1  # Convert to 0-indexed

        # Find the first line of the function body
        insert_line = func_line
        while insert_line < len(lines) and ':' not in lines[insert_line]:
            insert_line += 1
        insert_line += 1  # Move past ':'

        # Skip blank lines
        while insert_line < len(lines) and not lines[insert_line].strip():
            insert_line += 1

        # Get indentation
        if insert_line < len(lines):
            indent = len(lines[insert_line]) - len(lines[insert_line].lstrip())
        else:
            indent = 8

        # Insert docstring
        docstring_lines = docstring.strip().split('\n')
        for line in reversed(docstring_lines):
            if line.strip():
                lines.insert(insert_line, ' ' * indent + line.strip())
            else:
                lines.insert(insert_line, '')

        return '\n'.join(lines)


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Process file and add all missing docstrings.

    Args:
        filepath: Path to Python file
        dry_run: Report only, don't modify

    Returns:
        Number of docstrings added
    """
    print(f"\nProcessing: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source, str(filepath))
    except SyntaxError as e:
        print(f"  [ERROR] Syntax error: {e}")
        return 0

    modifications = []

    # Walk the entire AST tree
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # Include ALL methods (even private ones if they're complex)
                    if ast.get_docstring(item) is None:
                        # Skip double-underscore methods (dunder)
                        if item.name.startswith('__') and item.name.endswith('__'):
                            continue
                        docstring = ComprehensiveDocstringFiller.generate_docstring(item, class_name)
                        modifications.append((item.lineno, item.name, class_name, docstring, item))

        # Also handle module-level functions
        elif isinstance(node, ast.FunctionDef):
            if ast.get_docstring(node) is None:
                if not (node.name.startswith('__') and node.name.endswith('__')):
                    docstring = ComprehensiveDocstringFiller.generate_docstring(node, '')
                    modifications.append((node.lineno, node.name, '', docstring, node))

    if not modifications:
        print(f"  [OK] All methods already documented!")
        return 0

    print(f"  Found {len(modifications)} methods to document:")
    for line_no, method_name, class_name, _, _ in modifications[:10]:  # Show first 10
        prefix = f"{class_name}." if class_name else ""
        print(f"    Line {line_no}: {prefix}{method_name}()")
    if len(modifications) > 10:
        print(f"    ... and {len(modifications) - 10} more")

    if dry_run:
        print(f"  [DRY RUN] Would add {len(modifications)} docstrings")
        return len(modifications)

    # Apply modifications (bottom to top)
    modified_source = source
    for line_no, method_name, class_name, docstring, node in reversed(modifications):
        modified_source = ComprehensiveDocstringFiller.insert_docstring(
            modified_source, node, docstring
        )

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified_source)

    print(f"  [DONE] Added {len(modifications)} docstrings")
    return len(modifications)


def main():
    parser = argparse.ArgumentParser(description='Comprehensively document all methods')
    parser.add_argument('path', nargs='?', help='File to process')
    parser.add_argument('--directory', '-d', help='Directory to process')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursive')
    parser.add_argument('--dry-run', action='store_true', help='Report only')
    parser.add_argument('--all', action='store_true', help='Process entire codebase')

    args = parser.parse_args()

    total_added = 0

    if args.all:
        # Process entire symbo_agentic_reasoners directory
        base_dir = Path('src/symbo_agentic_reasoners')
        for filepath in sorted(base_dir.glob('**/*.py')):
            if '__pycache__' not in str(filepath):
                added = process_file(filepath, dry_run=args.dry_run)
                total_added += added

    elif args.directory:
        directory = Path(args.directory)
        pattern = '**/*.py' if args.recursive else '*.py'
        for filepath in sorted(directory.glob(pattern)):
            if filepath.is_file() and '__pycache__' not in str(filepath):
                added = process_file(filepath, dry_run=args.dry_run)
                total_added += added

    elif args.path:
        filepath = Path(args.path)
        total_added = process_file(filepath, dry_run=args.dry_run)
    else:
        parser.print_help()

    if total_added > 0 or args.all or args.directory:
        print(f"\n{'=' * 70}")
        print(f"TOTAL DOCSTRINGS {'WOULD BE ' if args.dry_run else ''}ADDED: {total_added}")


if __name__ == '__main__':
    main()
