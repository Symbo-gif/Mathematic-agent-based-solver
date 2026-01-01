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
ODE Test Suite Generator

Generates comprehensive ODE (Ordinary Differential Equation) test suite.

Target: 52,000 problems
- Existing: ~500 from literature (manual collection)
- Synthetic: 51,500 systematically generated

ODE Types:
- First-order linear: 10,000
- First-order separable: 10,000
- First-order exact/Bernoulli/substitution: 5,000
- Second-order constant coefficients: 10,000
- Second-order variable coefficients: 5,000
- Systems of ODEs: 5,000
- Boundary value problems: 3,000
- Initial value problems: 3,500
"""

import json
import random
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ODEGenerator:
    """Systematic ODE problem generator"""

    def __init__(self, output_dir: str = "data/benchmarks/odes"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.problems = []

    def generate_first_order_linear(self, count: int = 10000) -> List[Dict]:
        """
        Generate first-order linear ODEs: y' + p(x)y = q(x)

        Examples:
        - y' + 2y = 0
        - y' + y = x
        - y' - 3y = e^x
        """
        logger.info(f"Generating {count} first-order linear ODEs...")
        problems = []

        # Coefficient patterns
        p_patterns = [
            lambda: random.randint(1, 10),  # Constant
            lambda: f"{random.randint(1, 5)}*x",  # Linear
            lambda: f"1/x",  # 1/x
            lambda: f"{random.randint(1, 3)}*x**2",  # Quadratic
        ]

        q_patterns = [
            lambda: 0,  # Homogeneous
            lambda: random.randint(1, 10),  # Constant
            lambda: f"x",  # x
            lambda: f"x**2",  # x^2
            lambda: f"exp(x)",  # e^x
            lambda: f"sin(x)",  # sin(x)
            lambda: f"cos(x)",  # cos(x)
        ]

        for i in range(count):
            p = random.choice(p_patterns)()
            q = random.choice(q_patterns)()

            # Create equation
            if q == 0:
                equation = f"dy/dx + ({p})*y = 0"
                ode_type = "first_order_linear_homogeneous"
            else:
                equation = f"dy/dx + ({p})*y = {q}"
                ode_type = "first_order_linear_nonhomogeneous"

            # Initial condition
            x0 = 0
            y0 = random.randint(1, 10)
            initial_condition = f"y({x0}) = {y0}"

            problems.append({
                'id': f"ODE_FOL_{i:05d}",
                'equation': equation,
                'type': ode_type,
                'order': 1,
                'initial_conditions': initial_condition,
                'difficulty_level': random.randint(2, 5),
                'solution': "symbolic",  # Will be computed by solver
                'metadata': {
                    'p_coefficient': str(p),
                    'q_function': str(q),
                    'method': 'integrating_factor'
                }
            })

        return problems

    def generate_first_order_separable(self, count: int = 10000) -> List[Dict]:
        """
        Generate separable ODEs: dy/dx = f(x)g(y)

        Examples:
        - dy/dx = x*y
        - dy/dx = y^2
        - dy/dx = (1 + x)/(1 + y)
        """
        logger.info(f"Generating {count} first-order separable ODEs...")
        problems = []

        f_patterns = [
            lambda: "x",
            lambda: "x**2",
            lambda: "1",
            lambda: "exp(x)",
            lambda: "sin(x)",
            lambda: f"{random.randint(1, 5)}*x",
        ]

        g_patterns = [
            lambda: "y",
            lambda: "y**2",
            lambda: "1/y",
            lambda: "sqrt(y)",
            lambda: f"{random.randint(1, 5)}*y",
        ]

        for i in range(count):
            f = random.choice(f_patterns)()
            g = random.choice(g_patterns)()

            equation = f"dy/dx = ({f})*({g})"

            # Initial condition
            x0 = 0
            y0 = random.randint(1, 5)
            initial_condition = f"y({x0}) = {y0}"

            problems.append({
                'id': f"ODE_FOS_{i:05d}",
                'equation': equation,
                'type': 'first_order_separable',
                'order': 1,
                'initial_conditions': initial_condition,
                'difficulty_level': random.randint(3, 6),
                'solution': "symbolic",
                'metadata': {
                    'f_function': f,
                    'g_function': g,
                    'method': 'separation_of_variables'
                }
            })

        return problems

    def generate_second_order_constant(self, count: int = 10000) -> List[Dict]:
        """
        Generate second-order constant coefficient ODEs: ay'' + by' + cy = f(x)

        Examples:
        - y'' + 4y' + 4y = 0
        - y'' - y = 0
        - y'' + y = sin(x)
        """
        logger.info(f"Generating {count} second-order constant coefficient ODEs...")
        problems = []

        for i in range(count):
            a = 1  # Leading coefficient always 1
            b = random.randint(-5, 5)
            c = random.randint(-10, 10)

            # Right-hand side
            rhs_options = [
                "0",  # Homogeneous
                str(random.randint(1, 10)),  # Constant
                "x",
                "exp(x)",
                f"{random.randint(1, 3)}*exp(x)",
                "sin(x)",
                "cos(x)",
                f"{random.randint(1, 3)}*sin(x)",
            ]

            rhs = random.choice(rhs_options)

            if rhs == "0":
                equation = f"d2y/dx2 + ({b})*dy/dx + ({c})*y = 0"
                ode_type = "second_order_constant_homogeneous"
            else:
                equation = f"d2y/dx2 + ({b})*dy/dx + ({c})*y = {rhs}"
                ode_type = "second_order_constant_nonhomogeneous"

            # Initial conditions
            x0 = 0
            y0 = random.randint(0, 5)
            yp0 = random.randint(-2, 2)
            initial_conditions = f"y({x0}) = {y0}, y'({x0}) = {yp0}"

            # Characteristic equation roots
            discriminant = b**2 - 4*a*c
            if discriminant > 0:
                root_type = "real_distinct"
            elif discriminant == 0:
                root_type = "real_repeated"
            else:
                root_type = "complex_conjugate"

            problems.append({
                'id': f"ODE_SOC_{i:05d}",
                'equation': equation,
                'type': ode_type,
                'order': 2,
                'initial_conditions': initial_conditions,
                'difficulty_level': random.randint(4, 7),
                'solution': "symbolic",
                'metadata': {
                    'a': a,
                    'b': b,
                    'c': c,
                    'rhs': rhs,
                    'discriminant': discriminant,
                    'root_type': root_type,
                    'method': 'characteristic_equation'
                }
            })

        return problems

    def generate_all(
        self,
        first_order_linear: int = 10000,
        first_order_separable: int = 10000,
        second_order_constant: int = 10000,
        other_types: int = 21500
    ):
        """Generate all ODE types"""

        # Generate each type
        self.problems.extend(self.generate_first_order_linear(first_order_linear))
        self.problems.extend(self.generate_first_order_separable(first_order_separable))
        self.problems.extend(self.generate_second_order_constant(second_order_constant))

        # Placeholder for other types (can be expanded)
        logger.info(f"Placeholder for {other_types} additional ODE types...")
        logger.info(f"Total problems generated: {len(self.problems)}")

    def save(self, chunk_size: int = 10000):
        """Save problems to JSON files in chunks"""
        logger.info(f"Saving {len(self.problems)} problems in chunks of {chunk_size}...")

        # Split into chunks
        chunks = [
            self.problems[i:i+chunk_size]
            for i in range(0, len(self.problems), chunk_size)
        ]

        for idx, chunk in enumerate(chunks):
            output_file = self.output_dir / f"synthetic_odes_part_{idx+1:02d}.json"

            data = {
                'metadata': {
                    'chunk': idx + 1,
                    'total_chunks': len(chunks),
                    'problems_in_chunk': len(chunk),
                    'total_problems': len(self.problems),
                    'generation_date': '2025-12-19',
                    'generator_version': '1.0'
                },
                'problems': chunk
            }

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved chunk {idx+1}/{len(chunks)}: {output_file}")

        logger.info(f"All {len(self.problems)} problems saved successfully!")


def create_existing_odes_template():
    """Create template for manually collected existing ODE problems"""
    output_file = Path("data/benchmarks/odes/existing_odes.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    template = {
        'metadata': {
            'source': 'Kamke Handbook, Textbooks, Literature',
            'total_problems': 0,
            'collection_date': '2025-12-19',
            'description': 'Classic ODE problems from mathematical literature'
        },
        'problems': [
            {
                'id': 'ODE_EXISTING_001',
                'equation': "dy/dx + y = 0",
                'type': 'first_order_linear_homogeneous',
                'order': 1,
                'initial_conditions': "y(0) = 1",
                'solution': "y = exp(-x)",
                'source': 'Kamke #1',
                'difficulty_level': 2,
                'metadata': {
                    'historical_significance': 'Classic exponential decay',
                    'applications': ['radioactive decay', 'cooling']
                }
            },
            # Add more existing problems here...
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(template, f, indent=2)

    logger.info(f"Created existing ODEs template: {output_file}")
    logger.info("Please fill in classic ODE problems from Kamke's Handbook and other sources")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate ODE test suite")
    parser.add_argument('--total', type=int, default=30000,
                       help="Total synthetic problems to generate")
    parser.add_argument('--chunk-size', type=int, default=10000,
                       help="Problems per file chunk")
    parser.add_argument('--create-template', action='store_true',
                       help="Create template for existing ODEs")

    args = parser.parse_args()

    if args.create_template:
        create_existing_odes_template()
        return

    # Generate synthetic ODEs
    generator = ODEGenerator()

    # Distribute across ODE types
    fol = min(10000, args.total // 3)
    fos = min(10000, args.total // 3)
    soc = min(10000, args.total // 3)
    other = max(0, args.total - fol - fos - soc)

    logger.info(f"Generating {args.total} total ODEs:")
    logger.info(f"  First-order linear: {fol}")
    logger.info(f"  First-order separable: {fos}")
    logger.info(f"  Second-order constant: {soc}")
    logger.info(f"  Other types: {other}")

    generator.generate_all(
        first_order_linear=fol,
        first_order_separable=fos,
        second_order_constant=soc,
        other_types=other
    )

    generator.save(chunk_size=args.chunk_size)

    logger.info("ODE test suite generation complete!")
    logger.info(f"Files saved to: {generator.output_dir}")


if __name__ == "__main__":
    main()
