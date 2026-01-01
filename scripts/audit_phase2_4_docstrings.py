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
Phase 2-4 Docstring Coverage Auditor
=====================================

Audits and reports missing docstrings in Phase 2-4 modules.
"""

import ast
from pathlib import Path
from typing import Dict, List, Tuple


# Phase 2-4 module paths
PHASE_MODULES = {
    'Phase 2 - Computability': [
        'computability/turing_completeness.py',
        'computability/recursion_theory.py',
        'computability/turing_degrees.py',
        'computability/complexity_theory.py',
        'computability/kolmogorov_complexity.py',
    ],
    'Phase 2 - Riemannian Geometry': [
        'riemannian/metric.py',
        'riemannian/curvature.py',
        'riemannian/geodesic.py',
        'riemannian/comparison.py',
        'riemannian/holonomy.py',
    ],
    'Phase 2 - Bayesian Decision': [
        'statistics/bayesian_decision/utility_theory.py',
        'statistics/bayesian_decision/decision_rules.py',
        'statistics/bayesian_decision/sequential_decision.py',
    ],
    'Phase 2 - Time Series': [
        'statistics/timeseries/arima.py',
        'statistics/timeseries/kalman_filter.py',
        'statistics/timeseries/spectral_analysis.py',
        'statistics/timeseries/nonlinear_timeseries.py',
    ],
    'Phase 3 - Algebraic Topology': [
        'algebraic_topology/homotopy.py',
        'algebraic_topology/homology.py',
        'algebraic_topology/cohomology.py',
        'algebraic_topology/fundamental_group.py',
        'algebraic_topology/spectral_sequences.py',
    ],
    'Phase 3 - Ergodic Theory': [
        'ergodic/invariant_measures.py',
        'ergodic/mixing.py',
        'ergodic/ergodic_theorems.py',
        'ergodic/dynamical_entropy.py',
    ],
    'Phase 3 - Geometric Measure Theory': [
        'geometric_measure/hausdorff_measure.py',
        'geometric_measure/rectifiability.py',
        'geometric_measure/currents.py',
        'geometric_measure/minimal_surfaces.py',
    ],
    'Phase 3 - Topological Data Analysis': [
        'tda/persistent_homology.py',
        'tda/simplicial_complex.py',
        'tda/mapper.py',
        'tda/topological_inference.py',
    ],
    'Phase 4 - Advanced Optimization': [
        'optimization/advanced/nonconvex.py',
        'optimization/advanced/global_optimization.py',
        'optimization/advanced/variational_calculus.py',
        'optimization/advanced/optimal_control.py',
        'optimization/advanced/game_theory.py',
        'optimization/advanced/multiobjective.py',
    ],
}


def analyze_file(filepath: Path) -> Tuple[int, int, List[str]]:
    """Analyze a single file for docstring coverage.

    Returns:
        (total_methods, documented_methods, missing_methods_list)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        return 0, 0, []

    total = 0
    documented = 0
    missing = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private methods starting with __
            if not node.name.startswith('__'):
                total += 1
                if ast.get_docstring(node):
                    documented += 1
                else:
                    missing.append(f"  Line {node.lineno}: {node.name}()")

    return total, documented, missing


def main():
    base_dir = Path('src/symbo_agentic_reasoners/agents/specialists')

    print("="*80)
    print("PHASE 2-4 DOCSTRING COVERAGE AUDIT")
    print("="*80)
    print()

    all_total = 0
    all_documented = 0
    files_needing_work = []

    for phase_name, modules in PHASE_MODULES.items():
        print(f"\n{phase_name}")
        print("-" * 80)

        phase_total = 0
        phase_documented = 0

        for module_path in modules:
            filepath = base_dir / module_path
            total, documented, missing = analyze_file(filepath)

            phase_total += total
            phase_documented += documented
            all_total += total
            all_documented += documented

            if total > 0:
                coverage = (documented / total * 100)
                status = "[OK]" if coverage == 100 else "[  ]"
                print(f"{status} {module_path:55s} {documented:3d}/{total:3d} ({coverage:5.1f}%)")

                if missing:
                    files_needing_work.append((module_path, missing))
                    for method in missing:
                        print(f"    {method}")

        if phase_total > 0:
            phase_coverage = (phase_documented / phase_total * 100)
            print(f"\n  Phase Total: {phase_documented}/{phase_total} ({phase_coverage:.1f}%)")

    print("\n" + "="*80)
    if all_total > 0:
        overall_coverage = (all_documented / all_total * 100)
        missing_count = all_total - all_documented
        print(f"OVERALL COVERAGE: {all_documented}/{all_total} ({overall_coverage:.1f}%) - {missing_count} missing")
    print("="*80)

    if files_needing_work:
        print(f"\n{len(files_needing_work)} files need docstrings")
        print("\nTo add docstrings, edit these files:")
        for filepath, _ in files_needing_work:
            print(f"  - {filepath}")
    else:
        print("\n[OK] All Phase 2-4 modules have complete docstring coverage!")


if __name__ == '__main__':
    main()
