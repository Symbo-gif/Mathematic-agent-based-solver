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
Docstring Analyzer
==================

Scans codebase for missing docstrings and generates coverage report.

Phase 7: Documentation coverage analysis tool.

Usage:
    python scripts/analyze_docstrings.py src/
    python scripts/analyze_docstrings.py src/ --output=docs/missing_docstrings.txt
    python scripts/analyze_docstrings.py src/ --priority=infrastructure
    python scripts/analyze_docstrings.py src/ --stats
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict


def analyze_file(filepath: Path) -> Tuple[List[Tuple[int, str, str]], int, int]:
    """
    Analyze Python file for missing docstrings.

    Args:
        filepath: Path to Python file

    Returns:
        Tuple of (missing_items, total_items, documented_items)
        where missing_items is list of (line_number, name, type)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError) as e:
        return [], 0, 0

    missing = []
    total_items = 0
    documented_items = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private functions (starting with _) unless in infrastructure
            if node.name.startswith('_') and 'infrastructure' not in str(filepath):
                continue

            total_items += 1
            docstring = ast.get_docstring(node)

            if not docstring:
                missing.append((node.lineno, node.name, 'function'))
            else:
                documented_items += 1

        elif isinstance(node, ast.ClassDef):
            # Always count classes
            total_items += 1
            docstring = ast.get_docstring(node)

            if not docstring:
                missing.append((node.lineno, node.name, 'class'))
            else:
                documented_items += 1

    return missing, total_items, documented_items


def scan_directory(directory: Path, priority: str = None) -> Dict:
    """
    Scan directory for missing docstrings.

    Args:
        directory: Directory to scan
        priority: Optional priority filter (infrastructure, supervisors, specialists)

    Returns:
        Dictionary with analysis results
    """
    results = {
        'files': [],
        'total_items': 0,
        'documented_items': 0,
        'missing_items': 0,
        'coverage_percent': 0.0,
        'by_module': defaultdict(lambda: {'total': 0, 'documented': 0, 'missing': []})
    }

    # Find all Python files
    python_files = list(directory.rglob('*.py'))

    # Apply priority filter
    if priority:
        if priority == 'infrastructure':
            python_files = [f for f in python_files if 'infrastructure' in str(f)]
        elif priority == 'supervisors':
            python_files = [f for f in python_files if 'supervisors' in str(f)]
        elif priority == 'specialists':
            python_files = [f for f in python_files if 'specialists' in str(f)]

    for filepath in python_files:
        missing, total, documented = analyze_file(filepath)

        if total > 0:
            module_name = str(filepath.relative_to(directory))

            results['files'].append({
                'path': str(filepath),
                'module': module_name,
                'total': total,
                'documented': documented,
                'missing': missing,
                'coverage': (documented / total * 100) if total > 0 else 0
            })

            results['total_items'] += total
            results['documented_items'] += documented
            results['missing_items'] += len(missing)

            # Track by module category
            if 'infrastructure' in module_name:
                category = 'infrastructure'
            elif 'supervisors' in module_name:
                category = 'supervisors'
            elif 'specialists' in module_name:
                category = 'specialists'
            elif 'core' in module_name:
                category = 'core'
            else:
                category = 'other'

            results['by_module'][category]['total'] += total
            results['by_module'][category]['documented'] += documented
            results['by_module'][category]['missing'].extend([(str(filepath), *item) for item in missing])

    # Calculate overall coverage
    if results['total_items'] > 0:
        results['coverage_percent'] = (results['documented_items'] / results['total_items']) * 100

    return results


def print_report(results: Dict, verbose: bool = False):
    """Print analysis report."""
    print("=" * 80)
    print("DOCSTRING COVERAGE REPORT")
    print("=" * 80)
    print()

    print(f"Total Functions/Classes: {results['total_items']}")
    print(f"Documented: {results['documented_items']}")
    print(f"Missing Docstrings: {results['missing_items']}")
    print(f"Coverage: {results['coverage_percent']:.1f}%")
    print()

    print("Coverage by Category:")
    print("-" * 80)

    for category, stats in sorted(results['by_module'].items()):
        if stats['total'] > 0:
            coverage = (stats['documented'] / stats['total']) * 100
            print(f"  {category:20} {stats['documented']:4}/{stats['total']:4} ({coverage:5.1f}%)")

    if verbose:
        print()
        print("Files with Missing Docstrings:")
        print("-" * 80)

        # Sort by coverage (worst first)
        sorted_files = sorted(results['files'], key=lambda x: x['coverage'])

        for file_info in sorted_files[:20]:  # Top 20 worst
            if file_info['missing']:
                print(f"\n{file_info['module']}")
                print(f"  Coverage: {file_info['coverage']:.1f}% ({file_info['documented']}/{file_info['total']})")
                print(f"  Missing: {len(file_info['missing'])} items")


def write_report(results: Dict, output_path: str):
    """Write analysis report to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Docstring Coverage Report\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total Items: {results['total_items']}\n")
        f.write(f"Documented: {results['documented_items']}\n")
        f.write(f"Missing: {results['missing_items']}\n")
        f.write(f"Coverage: {results['coverage_percent']:.1f}%\n\n")

        f.write("Missing Docstrings by File:\n")
        f.write("-" * 80 + "\n\n")

        for file_info in sorted(results['files'], key=lambda x: x['coverage']):
            if file_info['missing']:
                f.write(f"{file_info['module']}\n")
                f.write(f"  Coverage: {file_info['coverage']:.1f}%\n")
                for line, name, item_type in file_info['missing']:
                    f.write(f"    Line {line:4}: {item_type:8} {name}\n")
                f.write("\n")


def main():
    parser = argparse.ArgumentParser(description='Analyze docstring coverage')
    parser.add_argument('directory', type=str, help='Directory to analyze')
    parser.add_argument('--output', type=str, help='Output file for report')
    parser.add_argument('--priority', type=str, choices=['infrastructure', 'supervisors', 'specialists'],
                       help='Filter by priority category')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    directory = Path(args.directory)

    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"Analyzing docstrings in: {directory}")
    if args.priority:
        print(f"Priority filter: {args.priority}")
    print()

    results = scan_directory(directory, priority=args.priority)

    if args.stats or not args.output:
        print_report(results, verbose=args.verbose)

    if args.output:
        write_report(results, args.output)
        print(f"\nReport written to: {args.output}")


if __name__ == '__main__':
    main()
