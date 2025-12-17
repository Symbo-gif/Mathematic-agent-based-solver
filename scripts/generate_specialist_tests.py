#!/usr/bin/env python3
# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Specialist Test Generator
=========================

Generates comprehensive test files for specialist agents from template.

Phase 6 - Week 1: Automates creation of 40+ specialist test suites.

Usage:
    python scripts/generate_specialist_tests.py --all
    python scripts/generate_specialist_tests.py --domain algebra
    python scripts/generate_specialist_tests.py --specialist ArithmeticSpecialist
"""

import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# Specialist definitions: (class_name, domain, module_path, service_type, simple_problem, complex_problem)
SPECIALISTS = [
    # Algebra (7)
    ('ArithmeticSpecialist', 'algebra', 'algebra.arithmetic_specialist', 'math.algebra.arithmetic',
     '2 + 2', '((12 * 5) + (8 / 2)) - 3'),
    ('PolynomialSpecialist', 'algebra', 'algebra.polynomial_specialist', 'math.algebra.polynomial',
     'x^2 + 2*x + 1', 'x^4 - 5*x^3 + 6*x^2 + 4*x - 8'),
    ('EquationSystemSolver', 'algebra', 'algebra.equation_system_solver', 'math.algebra.systems',
     'x + y = 5, x - y = 1', '2*x + 3*y + z = 10, x - y + 2*z = 5, 3*x + y - z = 8'),
    ('NumberTheorySpecialist', 'algebra', 'algebra.number_theory_specialist', 'math.algebra.numbertheory',
     'gcd(12, 8)', 'prime factorization of 1234567'),
    ('GroupRingTheoryAgent', 'algebra', 'algebra.group_ring_theory', 'math.algebra.structures',
     'Is Z_5 a group?', 'Find all subgroups of S_3'),

    # Calculus (8)
    ('DifferentiationSpecialist', 'calculus', 'calculus.differentiation_specialist', 'math.calculus.differentiation',
     'diff(x^2, x)', 'diff(x^3 * sin(x) * e^x, x)'),
    ('IntegrationSpecialist', 'calculus', 'calculus.integration_specialist', 'math.calculus.integration',
     'integrate(x^2, x)', 'integrate(x^2 * sin(x) * e^x, x)'),
    ('LimitEvaluator', 'calculus', 'calculus.limit_evaluator', 'math.calculus.limits',
     'limit(x^2, x, 0)', 'limit(sin(x)/x, x, 0)'),
    ('ODESolutionSpecialist', 'calculus', 'calculus.ode_specialist', 'math.calculus.ode',
     "dy/dx = y", "d²y/dx² + 4*dy/dx + 4*y = 0"),
    ('SeriesSpecialist', 'calculus', 'calculus.series_specialist', 'math.calculus.series',
     'Taylor series of e^x', 'Laurent series of 1/(z*(z-1))'),
    ('FourierAnalysisSpecialist', 'calculus', 'calculus.fourier_specialist', 'math.calculus.fourier',
     'Fourier transform of exp(-x^2)', 'FFT of [1, 2, 3, 4]'),
    ('SpecialFunctionsSpecialist', 'calculus', 'calculus.special_functions_specialist', 'math.calculus.special',
     'gamma(5)', 'bessel_j(0, 1.5)'),

    # Linear Algebra (5)
    ('MatrixOperationsSpecialist', 'linear_algebra', 'linear_algebra.matrix_ops_specialist', 'math.linalg.operations',
     '[[1,2],[3,4]] * [[5,6],[7,8]]', 'matrix_power([[1,2],[3,4]], 10)'),
    ('DecompositionSpecialist', 'linear_algebra', 'linear_algebra.decomposition_specialist', 'math.linalg.decomposition',
     'LU([[1,2],[3,4]])', 'SVD([[1,2,3],[4,5,6],[7,8,9]])'),
    ('VectorSpaceAnalyst', 'linear_algebra', 'linear_algebra.vector_space_analyst', 'math.linalg.vectorspace',
     'basis of span([1,0], [0,1])', 'orthogonal basis of [[1,1],[1,2]]'),

    # Geometry (6)
    ('EuclideanGeometrySpecialist', 'geometry', 'geometry.euclidean_specialist', 'math.geometry.euclidean',
     'distance from (0,0) to (3,4)', 'circle through points (0,0), (1,0), (0,1)'),
    ('TrigonometrySpecialist', 'geometry', 'geometry.trigonometry_specialist', 'math.geometry.trig',
     'sin(30 degrees)', 'solve sin(x) = 0.5 for 0 <= x <= 2*pi'),

    # Logic (6)
    ('PropositionalLogicSpecialist', 'logic', 'logic.propositional_specialist', 'math.logic.propositional',
     'A AND B', '(A OR B) AND (NOT A OR C)'),
    ('SATSolverSpecialist', 'logic', 'logic.sat_solver_specialist', 'math.logic.sat',
     '(A OR B) AND (NOT A OR NOT B)', 'complex CNF formula'),

    # Statistics (6)
    ('DistributionSpecialist', 'statistics', 'statistics.distribution_specialist', 'math.stats.distributions',
     'normal(mu=0, sigma=1)', 'binomial(n=10, p=0.5)'),
    ('RegressionSpecialist', 'statistics', 'statistics.regression_specialist', 'math.stats.regression',
     'linear regression: y = mx + b', 'polynomial regression degree 3'),

    # Physics (4)
    ('KinematicsSpecialist', 'physics', 'physics.mechanics.kinematics_specialist', 'math.physics.kinematics',
     'velocity from position x = t^2', 'acceleration of projectile'),
    ('DynamicsSpecialist', 'physics', 'physics.mechanics.dynamics_specialist', 'math.physics.dynamics',
     'F = ma with F=10, m=2', 'net force on object with multiple forces'),
]


def load_template() -> str:
    """Load the specialist test template."""
    template_path = Path(__file__).parent.parent / 'tests' / 'agents' / 'specialists' / 'test_template.py'

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_test_file(specialist: Tuple, template: str) -> Tuple[str, str]:
    """
    Generate test file from template.

    Args:
        specialist: (name, domain, module_path, service_type, simple_problem, complex_problem)
        template: Template content

    Returns:
        (output_path, generated_content)
    """
    name, domain, module_path, service_type, simple_prob, complex_prob = specialist

    # Replace placeholders
    content = template.replace('{{SPECIALIST_NAME}}', name)
    content = content.replace('{{DOMAIN}}', domain)
    content = content.replace('{{MODULE_PATH}}', module_path)
    content = content.replace('{{SERVICE_TYPE}}', service_type)
    content = content.replace('{{SIMPLE_PROBLEM}}', simple_prob)
    content = content.replace('{{COMPLEX_PROBLEM}}', complex_prob)

    # Generate filename
    filename = f"test_{name.lower()}_complete.py"
    output_path = Path(__file__).parent.parent / 'tests' / 'agents' / 'specialists' / domain / filename

    return str(output_path), content


def generate_all_tests(specialists: List[Tuple] = None, dry_run: bool = False):
    """Generate all specialist tests."""
    if specialists is None:
        specialists = SPECIALISTS

    template = load_template()
    generated_count = 0
    total_loc = 0

    print(f"Generating {len(specialists)} specialist test files...")
    print()

    for specialist in specialists:
        name, domain, _, _, _, _ = specialist

        output_path, content = generate_test_file(specialist, template)

        if not dry_run:
            # Create domain directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

        loc = len(content.split('\n'))
        total_loc += loc
        generated_count += 1

        status = "[DRY RUN]" if dry_run else "[CREATED]"
        print(f"{status} {name:40} -> {output_path}")
        print(f"         {loc} LOC, ~12 tests")

    print()
    print(f"Summary:")
    print(f"  Files generated: {generated_count}")
    print(f"  Total LOC: {total_loc:,}")
    print(f"  Estimated tests: {generated_count * 12}")
    print(f"  Average LOC/file: {total_loc // generated_count if generated_count > 0 else 0}")


def main():
    parser = argparse.ArgumentParser(description='Generate specialist test files')
    parser.add_argument('--all', action='store_true', help='Generate all specialist tests')
    parser.add_argument('--domain', type=str, help='Generate tests for specific domain')
    parser.add_argument('--specialist', type=str, help='Generate test for specific specialist')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without creating files')
    parser.add_argument('--list', action='store_true', help='List all available specialists')

    args = parser.parse_args()

    if args.list:
        print("Available specialists:")
        for name, domain, _, _, _, _ in SPECIALISTS:
            print(f"  {domain:20} {name}")
        return

    if args.all:
        generate_all_tests(dry_run=args.dry_run)
    elif args.domain:
        filtered = [s for s in SPECIALISTS if s[1] == args.domain]
        if not filtered:
            print(f"No specialists found for domain: {args.domain}")
            return
        generate_all_tests(filtered, dry_run=args.dry_run)
    elif args.specialist:
        filtered = [s for s in SPECIALISTS if s[0] == args.specialist]
        if not filtered:
            print(f"Specialist not found: {args.specialist}")
            return
        generate_all_tests(filtered, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
