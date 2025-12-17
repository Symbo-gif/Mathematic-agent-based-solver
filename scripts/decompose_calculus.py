#!/usr/bin/env python3
"""
Script to decompose native_calculus.py into specialist modules.

This script extracts different components from the monolithic native_calculus.py
and creates a supervisor-specialist agent architecture.
"""

import re
import os
from pathlib import Path


def extract_lines(source_file: Path, start_line: int, end_line: int) -> list[str]:
    """Extract lines from source file (1-indexed inclusive)."""
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines[start_line-1:end_line]


def find_class_boundaries(source_file: Path, class_name: str) -> tuple[int, int]:
    """Find start and end lines for a class definition."""
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start = None
    indent_level = None

    for i, line in enumerate(lines, 1):
        if start is None:
            if re.match(rf'^class {class_name}[:(]', line):
                start = i
                # Find the indent of the first method/attribute
                for j in range(i, len(lines)):
                    if lines[j].strip() and not lines[j].strip().startswith('#') and not lines[j].strip().startswith('"""'):
                        if lines[j].startswith('    '):
                            indent_level = 4
                            break
        elif start is not None:
            # Check if we've left the class (new top-level definition)
            if line.strip() and not line.startswith(' ') and not line.strip().startswith('#'):
                return start, i - 1

    return start, len(lines) if start else None


def find_function_boundaries(source_file: Path, func_name: str) -> list[tuple[int, int]]:
    """Find start and end lines for all occurrences of a function."""
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    occurrences = []
    start = None
    base_indent = None

    for i, line in enumerate(lines, 1):
        if start is None:
            if re.match(rf'^def {func_name}\(', line):
                start = i
                base_indent = 0
            elif re.match(rf'^    def {func_name}\(', line):
                start = i
                base_indent = 4
        elif start is not None:
            # Check if we've reached next function/class at same indent
            stripped = line.lstrip()
            if stripped:
                current_indent = len(line) - len(stripped)
                if current_indent == base_indent and (stripped.startswith('def ') or stripped.startswith('class ')):
                    occurrences.append((start, i - 1))
                    start = None
                    base_indent = None

    if start is not None:
        occurrences.append((start, len(lines)))

    return occurrences


def main():
    base_dir = Path(r"C:\dev\Mathematic agent based solver")
    source_file = base_dir / "src" / "symbo_agentic_reasoners" / "core" / "native_calculus.py"
    target_dir = base_dir / "src" / "symbo_agentic_reasoners" / "core" / "calculus"

    # Read the entire source file
    with open(source_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    print(f"Total lines in source: {len(all_lines)}")

    # Find class boundaries
    classes_to_extract = {
        'DifferentiationEngine': (360, 544),  # Approximate
        'IntegrationEngine': (550, 2183),
        'LimitEngine': (2188, 3273),
        'ExprParser': (3277, 3442),
    }

    for class_name, (start_guess, end_guess) in classes_to_extract.items():
        print(f"\n{class_name}: lines {start_guess}-{end_guess} (~{end_guess-start_guess} lines)")


if __name__ == "__main__":
    main()
