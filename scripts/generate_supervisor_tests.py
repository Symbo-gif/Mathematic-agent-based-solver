#!/usr/bin/env python3
# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Supervisor Test Generator
=========================

Generates comprehensive test files for supervisor agents from template.

Phase 6 - Week 1: Automates creation of 20 supervisor test suites.

Usage:
    python scripts/generate_supervisor_tests.py --all
    python scripts/generate_supervisor_tests.py --supervisor AlgebraSupervisor
"""

import argparse
from pathlib import Path
from typing import List, Tuple

# Supervisor definitions: (class_name, module_path, domain, simple_problem, complex_problem)
SUPERVISORS = [
    # Core Mathematical Domains
    ('AlgebraSupervisor', 'algebra_supervisor', 'algebra',
     'solve x + 2 = 5', 'solve system: 2x + 3y = 10, x - y = 2'),

    ('CalculusSupervisor', 'calculus_supervisor', 'calculus',
     'derivative of x^2', 'integral of x*sin(x)*e^x'),

    ('LinearAlgebraSupervisor', 'linalg_supervisor', 'linear_algebra',
     'multiply matrices [[1,2],[3,4]] and [[5,6],[7,8]]', 'compute SVD of 3x3 matrix'),

    # Advanced Mathematics
    ('StatisticsSupervisor', 'stats_supervisor', 'statistics',
     'mean of [1,2,3,4,5]', 'linear regression on dataset with 100 points'),

    ('DiscreteMathSupervisor', 'discrete_math_supervisor', 'discrete_math',
     'compute 5!', 'find shortest path in graph with 20 nodes'),

    ('LogicSupervisor', 'logic_supervisor', 'logic',
     'evaluate (A AND B)', 'prove theorem using natural deduction'),

    ('GeometrySupervisor', 'geometry_supervisor', 'geometry',
     'distance from (0,0) to (3,4)', 'find intersection of two circles'),

    # Physics Domains
    ('PhysicsMechanicsSupervisor', 'physics_mechanics_supervisor', 'physics_mechanics',
     'F=ma with F=10, m=2', 'projectile motion with air resistance'),

    ('PhysicsEMSupervisor', 'physics_em_supervisor', 'physics_em',
     'Coulomb force between two charges', 'analyze RLC circuit'),

    ('PhysicsThermoSupervisor', 'physics_thermo_supervisor', 'physics_thermo',
     'Q = mcΔT', 'Carnot cycle efficiency'),

    ('PhysicsQuantumSupervisor', 'physics_quantum_supervisor', 'physics_quantum',
     'normalize wavefunction', 'solve Schrödinger equation for harmonic oscillator'),

    # Analysis Domains
    ('ComplexAnalysisSupervisor', 'complex_analysis_supervisor', 'complex_analysis',
     'is f(z)=z^2 analytic?', 'compute contour integral using residue theorem'),

    ('RealAnalysisSupervisor', 'real_analysis_supervisor', 'real_analysis',
     'does sequence 1/n converge?', 'prove uniform convergence of function series'),

    ('FunctionalAnalysisSupervisor', 'functional_analysis_supervisor', 'functional_analysis',
     'verify norm axioms', 'compute operator spectrum'),

    # Advanced Topics
    ('DiffGeometrySupervisor', 'diff_geometry_supervisor', 'differential_geometry',
     'compute metric tensor', 'find geodesics on surface'),

    ('ControlTheorySupervisor', 'control_theory_supervisor', 'control_theory',
     'analyze system stability', 'design LQR controller'),

    ('InformationTheorySupervisor', 'information_theory_supervisor', 'information_theory',
     'Shannon entropy of binary distribution', 'compute channel capacity'),

    ('CryptographySupervisor', 'cryptography_supervisor', 'cryptography',
     '2^10 mod 13', 'RSA key generation and encryption'),

    ('OptimizationSupervisor', 'optimization_supervisor', 'optimization',
     'minimize f(x) = x^2', 'solve linear program with simplex method'),

    ('CategoryTheorySupervisor', 'category_theory_supervisor', 'category_theory',
     'compose morphisms f and g', 'prove Yoneda lemma for specific category'),
]


def load_template() -> str:
    """Load the supervisor test template."""
    template_path = Path(__file__).parent.parent / 'tests' / 'agents' / 'supervisors' / 'supervisor_test_template.py'

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_test_file(supervisor: Tuple, template: str) -> Tuple[str, str]:
    """
    Generate test file from template.

    Args:
        supervisor: (name, module_path, domain, simple_problem, complex_problem)
        template: Template content

    Returns:
        (output_path, generated_content)
    """
    name, module_path, domain, simple_prob, complex_prob = supervisor

    # Replace placeholders
    content = template.replace('{{SUPERVISOR_NAME}}', name)
    content = content.replace('{{MODULE_PATH}}', module_path)
    content = content.replace('{{DOMAIN}}', domain)
    content = content.replace('{{SIMPLE_PROBLEM}}', simple_prob)
    content = content.replace('{{COMPLEX_PROBLEM}}', complex_prob)

    # Generate filename
    filename = f"test_{name.lower()}_complete.py"
    output_path = Path(__file__).parent.parent / 'tests' / 'agents' / 'supervisors' / filename

    return str(output_path), content


def generate_all_tests(supervisors: List[Tuple] = None, dry_run: bool = False):
    """Generate all supervisor tests."""
    if supervisors is None:
        supervisors = SUPERVISORS

    template = load_template()
    generated_count = 0
    total_loc = 0

    print(f"Generating {len(supervisors)} supervisor test files...")
    print()

    for supervisor in supervisors:
        name, module_path, domain, _, _ = supervisor

        output_path, content = generate_test_file(supervisor, template)

        if not dry_run:
            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

        loc = len(content.split('\n'))
        total_loc += loc
        generated_count += 1

        status = "[DRY RUN]" if dry_run else "[CREATED]"
        print(f"{status} {name:40} -> {Path(output_path).name}")
        print(f"         {loc} LOC, ~10 tests, domain: {domain}")

    print()
    print(f"Summary:")
    print(f"  Files generated: {generated_count}")
    print(f"  Total LOC: {total_loc:,}")
    print(f"  Estimated tests: {generated_count * 10}")
    print(f"  Average LOC/file: {total_loc // generated_count if generated_count > 0 else 0}")


def main():
    parser = argparse.ArgumentParser(description='Generate supervisor test files')
    parser.add_argument('--all', action='store_true', help='Generate all supervisor tests')
    parser.add_argument('--supervisor', type=str, help='Generate test for specific supervisor')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without creating files')
    parser.add_argument('--list', action='store_true', help='List all available supervisors')

    args = parser.parse_args()

    if args.list:
        print("Available supervisors:")
        for name, _, domain, _, _ in SUPERVISORS:
            print(f"  {domain:30} {name}")
        return

    if args.all:
        generate_all_tests(dry_run=args.dry_run)
    elif args.supervisor:
        filtered = [s for s in SUPERVISORS if s[0] == args.supervisor]
        if not filtered:
            print(f"Supervisor not found: {args.supervisor}")
            return
        generate_all_tests(filtered, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
