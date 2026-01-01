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
Comprehensive Docstring Coverage Report
========================================

Generates detailed coverage metrics for the entire codebase.
"""

import ast
from pathlib import Path
from typing import Dict, Tuple
import json


def analyze_directory(directory: Path) -> Dict:
    """Analyze a directory for docstring coverage.

    Returns dict with file paths and their coverage stats.
    """
    results = {}
    total_funcs = 0
    total_with_docs = 0

    for filepath in directory.rglob('*.py'):
        if '__pycache__' in str(filepath) or 'test' in str(filepath).lower():
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)

            funcs_in_file = 0
            docs_in_file = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private methods starting with __
                    if not node.name.startswith('__'):
                        funcs_in_file += 1
                        total_funcs += 1
                        if ast.get_docstring(node):
                            docs_in_file += 1
                            total_with_docs += 1

            if funcs_in_file > 0:
                coverage = (docs_in_file / funcs_in_file * 100)
                rel_path = str(filepath.relative_to(directory))
                results[rel_path] = {
                    'total': funcs_in_file,
                    'documented': docs_in_file,
                    'coverage': coverage,
                    'missing': funcs_in_file - docs_in_file
                }

        except (SyntaxError, UnicodeDecodeError):
            pass

    return results, total_funcs, total_with_docs


def main():
    base_dir = Path('src/symbo_agentic_reasoners')

    print("="*80)
    print("SYMBO AGENTIC REASONERS - DOCSTRING COVERAGE REPORT")
    print("="*80)
    print()

    # Analyze by subdirectory
    subdirs = {
        'Core Infrastructure': base_dir / 'core' / 'orchestration',
        'BDI Framework': base_dir / 'core' / 'bdi_agent.py',
        'Symbolic Core': base_dir / 'core' / 'symbolic',
        'Calculus Engine': base_dir / 'core' / 'calculus',
        'Infrastructure': base_dir / 'infrastructure',
        'Agents/Specialists': base_dir / 'agents' / 'specialists',
        'Agents/Supervisors': base_dir / 'agents' / 'supervisors',
        'Discovery': base_dir / 'discovery',
        'Middleware': base_dir / 'middleware',
    }

    all_results = {}
    grand_total = 0
    grand_documented = 0

    for name, path in subdirs.items():
        if not path.exists():
            continue

        if path.is_file():
            # Single file
            results, total, documented = analyze_directory(path.parent)
            file_result = {k: v for k, v in results.items() if path.name in k}
            if file_result:
                total = sum(f['total'] for f in file_result.values())
                documented = sum(f['documented'] for f in file_result.values())
        else:
            # Directory
            results, total, documented = analyze_directory(path)

        if total > 0:
            coverage = (documented / total * 100)
            missing = total - documented

            print(f"{name:25s}: {documented:4d}/{total:4d} ({coverage:5.1f}%) - {missing:3d} missing")

            all_results[name] = {
                'total': total,
                'documented': documented,
                'coverage': coverage,
                'missing': missing,
                'files': results
            }

            grand_total += total
            grand_documented += documented

    print("="*80)
    grand_coverage = (grand_documented / grand_total * 100) if grand_total > 0 else 100
    grand_missing = grand_total - grand_documented
    print(f"{'OVERALL':25s}: {grand_documented:4d}/{grand_total:4d} ({grand_coverage:5.1f}%) - {grand_missing:3d} missing")
    print("="*80)

    # Show worst offenders
    print("\nTOP 10 FILES NEEDING DOCUMENTATION:")
    print("-"*80)

    all_files = []
    for area_name, area_data in all_results.items():
        for file_path, file_data in area_data.get('files', {}).items():
            if file_data['missing'] > 0:
                all_files.append((file_path, file_data['missing'], file_data['coverage'], area_name))

    all_files.sort(key=lambda x: x[1], reverse=True)

    for i, (file_path, missing, coverage, area) in enumerate(all_files[:10], 1):
        print(f"{i:2d}. {file_path:60s} {missing:3d} methods ({coverage:5.1f}%)")

    # Save detailed report
    report_path = Path('data/docs/docstring_coverage_report.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nDetailed report saved to: {report_path}")
    print("\nRECOMMENDATIONS:")
    if grand_coverage < 90:
        print(f"  - Current coverage ({grand_coverage:.1f}%) is below 90% target")
        print(f"  - Focus on top 10 files ({sum(f[1] for f in all_files[:10])} methods)")
        print(f"  - Use scripts/batch_add_docstrings.py for automation")
    else:
        print(f"  - Excellent coverage! Focus on quality over quantity")


if __name__ == '__main__':
    main()
