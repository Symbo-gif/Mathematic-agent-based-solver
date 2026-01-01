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
Docstring Example Validator
============================

Extracts and validates all docstring examples across the codebase.

Usage:
    python scripts/validate_docstring_examples.py
    python scripts/validate_docstring_examples.py --file <path>
"""

import ast
import argparse
import re
from pathlib import Path
from typing import List, Tuple


def extract_examples_from_docstring(docstring: str) -> List[str]:
    """Extract example code blocks from docstring.

    Args:
        docstring: Docstring text

    Returns:
        List of example code snippets
    """
    if not docstring:
        return []

    examples = []
    in_example = False
    current_example = []

    for line in docstring.split('\n'):
        line = line.strip()
        if 'Example:' in line or 'Examples:' in line:
            in_example = True
            continue
        if in_example:
            if line.startswith('>>>'):
                current_example.append(line[4:])  # Remove >>> prefix
            elif line.startswith('...'):
                current_example.append(line[4:])  # Remove ... prefix
            elif line and not line.startswith('#'):
                # End of example block
                if current_example:
                    examples.append('\n'.join(current_example))
                    current_example = []
                in_example = False

    # Add last example if exists
    if current_example:
        examples.append('\n'.join(current_example))

    return examples


def validate_example_syntax(example: str) -> Tuple[bool, str]:
    """Validate Python syntax of example code.

    Args:
        example: Python code string

    Returns:
        (is_valid, error_message)
    """
    try:
        compile(example, '<docstring>', 'exec')
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error: {e}"


def process_file(filepath: Path) -> Tuple[int, int, List[str]]:
    """Process file and validate all docstring examples.

    Args:
        filepath: Path to Python file

    Returns:
        (total_examples, valid_examples, errors)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source, str(filepath))
    except SyntaxError:
        return 0, 0, [f"File has syntax errors: {filepath}"]

    total_examples = 0
    valid_examples = 0
    errors = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node)
            if docstring:
                examples = extract_examples_from_docstring(docstring)
                for example in examples:
                    total_examples += 1
                    is_valid, error = validate_example_syntax(example)
                    if is_valid:
                        valid_examples += 1
                    else:
                        node_name = getattr(node, 'name', '<module>')
                        errors.append(f"{filepath}:{node.lineno} ({node_name}): {error}")

    return total_examples, valid_examples, errors


def main():
    parser = argparse.ArgumentParser(description='Validate docstring examples')
    parser.add_argument('--file', help='Validate single file')
    parser.add_argument('--directory', '-d', help='Validate directory')
    parser.add_argument('--recursive', '-r', action='store_true')

    args = parser.parse_args()

    total_examples = 0
    valid_examples = 0
    all_errors = []

    if args.file:
        t, v, errs = process_file(Path(args.file))
        total_examples += t
        valid_examples += v
        all_errors.extend(errs)
    elif args.directory:
        directory = Path(args.directory)
        pattern = '**/*.py' if args.recursive else '*.py'
        for filepath in sorted(directory.glob(pattern)):
            if '__pycache__' not in str(filepath):
                t, v, errs = process_file(filepath)
                total_examples += t
                valid_examples += v
                all_errors.extend(errs)
    else:
        # Default: validate entire codebase
        base_dir = Path('src/symbo_agentic_reasoners')
        for filepath in sorted(base_dir.glob('**/*.py')):
            if '__pycache__' not in str(filepath):
                t, v, errs = process_file(filepath)
                total_examples += t
                valid_examples += v
                all_errors.extend(errs)

    # Report results
    print("\n" + "=" * 70)
    print("DOCSTRING EXAMPLE VALIDATION REPORT")
    print("=" * 70)
    print(f"Total examples found: {total_examples}")
    print(f"Valid examples: {valid_examples}")
    print(f"Invalid examples: {len(all_errors)}")
    print(f"Success rate: {100.0 * valid_examples / total_examples if total_examples > 0 else 0:.1f}%")

    if all_errors:
        print("\nERRORS:")
        for error in all_errors[:20]:  # Show first 20
            print(f"  {error}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")
    else:
        print("\n[OK] All docstring examples have valid syntax!")


if __name__ == '__main__':
    main()
