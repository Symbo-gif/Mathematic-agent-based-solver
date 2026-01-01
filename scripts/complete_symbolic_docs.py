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
Complete Symbolic Core Documentation
====================================

Comprehensively documents all mathematical function classes in the symbolic core.
Uses intelligent pattern matching and mathematical templates.
"""

import re
from pathlib import Path


# Comprehensive docstring database for all function types
DOCSTRINGS = {
    # Base Function class
    'Function.free_symbols': '''"""Get all free symbols in the function and its arguments.

        Recursively collects all Symbol objects appearing in this
        function's arguments.

        Returns:
            Set of Symbol objects in the expression

        Example:
            >>> x, y = Symbol('x'), Symbol('y')
            >>> f = Sin(x**2 + y)
            >>> f.free_symbols
            {x, y}
        """''',

    'Function.simplify': '''"""Simplify the function by simplifying its arguments.

        Recursively simplifies all arguments and reconstructs
        the function with simplified arguments.

        Returns:
            Simplified function expression

        Example:
            >>> x = Symbol('x')
            >>> f = Sin(x + 0)
            >>> f.simplify()
            sin(x)
        """''',

    # Trigonometric functions
    'Sin.diff': '''"""Compute derivative using chain rule: d/dx sin(f) = cos(f) * f'.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Sin(x**2).diff(x)
            2*x*cos(x**2)
        """''',

    'Sin.evalf': '''"""Numerically evaluate sin(x).

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric, else symbolic

        Example:
            >>> Sin(0).evalf()
            0.0
        """''',

    'Sin.to_latex': '''"""Convert to LaTeX: \\sin\\left(x\\right).

        Returns:
            LaTeX string
        """''',

    'Cos.diff': '''"""Compute derivative using chain rule: d/dx cos(f) = -sin(f) * f'.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Cos(x**2).diff(x)
            -2*x*sin(x**2)
        """''',

    'Cos.evalf': '''"""Numerically evaluate cos(x).

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric, else symbolic

        Example:
            >>> Cos(0).evalf()
            1.0
        """''',

    'Cos.to_latex': '''"""Convert to LaTeX: \\cos\\left(x\\right).

        Returns:
            LaTeX string
        """''',

    'Tan.diff': '''"""Compute derivative: d/dx tan(f) = sec²(f) * f' = f'/cos²(f).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Tan(x).diff(x)
            1/cos(x)**2
        """''',

    'Tan.evalf': '''"""Numerically evaluate tan(x).

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric, else symbolic

        Example:
            >>> Tan(0).evalf()
            0.0
        """''',

    'Tan.to_latex': '''"""Convert to LaTeX: \\tan\\left(x\\right).

        Returns:
            LaTeX string
        """''',

    # Exponential and logarithm
    'Exp.diff': '''"""Compute derivative: d/dx exp(f) = exp(f) * f'.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Exp(x**2).diff(x)
            2*x*exp(x**2)
        """''',

    'Exp.evalf': '''"""Numerically evaluate exp(x) = e^x.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric, else symbolic

        Example:
            >>> Exp(1).evalf()
            2.718281828459045
        """''',

    'Exp.to_latex': '''"""Convert to LaTeX: e^{x}.

        Returns:
            LaTeX string
        """''',

    'Log.diff': '''"""Compute derivative: d/dx log(f) = f'/f.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Log(x**2).diff(x)
            2/x
        """''',

    'Log.evalf': '''"""Numerically evaluate natural logarithm.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric and positive, else symbolic

        Example:
            >>> import math
            >>> Log(math.e).evalf()
            1.0
        """''',

    'Log.to_latex': '''"""Convert to LaTeX: \\ln\\left(x\\right).

        Returns:
            LaTeX string
        """''',

    'Sqrt.diff': '''"""Compute derivative: d/dx sqrt(f) = f'/(2*sqrt(f)).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Sqrt(x).diff(x)
            1/(2*sqrt(x))
        """''',

    'Sqrt.evalf': '''"""Numerically evaluate square root.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric and non-negative, else symbolic

        Example:
            >>> Sqrt(4).evalf()
            2.0
        """''',

    'Sqrt.to_latex': '''"""Convert to LaTeX: \\sqrt{x}.

        Returns:
            LaTeX string
        """''',

    'Abs.diff': '''"""Compute derivative: d/dx |f| = sign(f) * f'.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Abs(x).diff(x)
            sign(x)
        """''',

    'Abs.evalf': '''"""Numerically evaluate absolute value.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Float if numeric, else symbolic

        Example:
            >>> Abs(-5).evalf()
            5.0
        """''',

    'Abs.to_latex': '''"""Convert to LaTeX: \\left|x\\right|.

        Returns:
            LaTeX string
        """''',

    'Sign.diff': '''"""Compute derivative (zero almost everywhere).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Integer(0)

        Note:
            Undefined at x=0, but returns 0 symbolically.
        """''',

    'Sign.evalf': '''"""Numerically evaluate sign function.

        Returns -1 for negative, 0 for zero, +1 for positive.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            -1.0, 0.0, or 1.0 if numeric

        Example:
            >>> Sign(-3).evalf()
            -1.0
        """''',

    'Sign.to_latex': '''"""Convert to LaTeX: \\text{sign}\\left(x\\right).

        Returns:
            LaTeX string
        """''',

    'GenericFunction.diff': '''"""Symbolic derivative for unknown function.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative object

        Example:
            >>> f = GenericFunction('f', Symbol('x'))
            >>> f.diff(Symbol('x'))
            Derivative(f(x), x)
        """''',

    'GenericFunction.evalf': '''"""Cannot evaluate unknown function numerically.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Self (symbolic)
        """''',

    'GenericFunction.to_latex': '''"""Convert to LaTeX with function name.

        Returns:
            LaTeX string

        Example:
            >>> f = GenericFunction('f', Symbol('x'))
            >>> f.to_latex()
            '\\\\text{f}\\\\left(x\\\\right)'
        """''',

    'Factorial.diff': '''"""Derivative via gamma: d/dn n! = n! * ψ(n+1).

        Args:
            var: Variable to differentiate

        Returns:
            Expression with digamma function
        """''',

    'Factorial.evalf': '''"""Compute factorial numerically.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            n! as float for non-negative integer n

        Example:
            >>> Factorial(5).evalf()
            120.0
        """''',

    'Factorial.simplify': '''"""Evaluate factorial of integer constants.

        Returns:
            Integer(n!) if n is non-negative integer

        Example:
            >>> Factorial(Integer(5)).simplify()
            120
        """''',

    'Factorial.to_latex': '''"""Convert to LaTeX: n!.

        Returns:
            LaTeX string
        """''',

    'Gamma.diff': '''"""Derivative: d/dx Γ(x) = Γ(x) * ψ(x).

        Args:
            var: Variable to differentiate

        Returns:
            Expression with digamma function
        """''',

    'Gamma.evalf': '''"""Numerically evaluate Gamma function.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Γ(x) as float

        Example:
            >>> Gamma(5).evalf()
            24.0
        """''',

    'Gamma.to_latex': '''"""Convert to LaTeX: \\Gamma\\left(x\\right).

        Returns:
            LaTeX string
        """''',

    'Gcd.diff': '''"""GCD derivative (always zero - discrete function).

        Args:
            var: Variable

        Returns:
            Integer(0)
        """''',

    'Gcd.evalf': '''"""Compute GCD numerically.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            GCD as float

        Example:
            >>> Gcd(12, 18).evalf()
            6.0
        """''',

    'Gcd.simplify': '''"""Evaluate GCD of integer constants.

        Returns:
            Integer(gcd(...))

        Example:
            >>> Gcd(Integer(12), Integer(18)).simplify()
            6
        """''',

    'Gcd.to_latex': '''"""Convert to LaTeX: \\gcd\\left(a, b\\right).

        Returns:
            LaTeX string
        """''',

    'Floor.diff': '''"""Floor derivative (zero almost everywhere).

        Args:
            var: Variable

        Returns:
            Integer(0)
        """''',

    'Floor.evalf': '''"""Evaluate floor: ⌊x⌋ = greatest integer ≤ x.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Floor value as float

        Example:
            >>> Floor(3.7).evalf()
            3.0
        """''',

    'Floor.simplify': '''"""Simplify floor of numeric values.

        Returns:
            Integer(⌊x⌋)

        Example:
            >>> Floor(Float(3.7)).simplify()
            3
        """''',

    'Floor.to_latex': '''"""Convert to LaTeX: \\lfloor x \\rfloor.

        Returns:
            LaTeX string
        """''',

    'Ceil.diff': '''"""Ceiling derivative (zero almost everywhere).

        Args:
            var: Variable

        Returns:
            Integer(0)
        """''',

    'Ceil.evalf': '''"""Evaluate ceiling: ⌈x⌉ = smallest integer ≥ x.

        Args:
            precision: Decimal digits precision (default: 15)

        Returns:
            Ceiling value as float

        Example:
            >>> Ceil(3.2).evalf()
            4.0
        """''',

    'Ceil.simplify': '''"""Simplify ceiling of numeric values.

        Returns:
            Integer(⌈x⌉)

        Example:
            >>> Ceil(Float(3.2)).simplify()
            4
        """''',

    'Ceil.to_latex': '''"""Convert to LaTeX: \\lceil x \\rceil.

        Returns:
            LaTeX string
        """''',
}


def add_docstring_after_line(lines: list, line_num: int, docstring: str, indent: int = 8) -> list:
    """Insert docstring after specified line."""
    # Check if docstring already exists
    if line_num + 1 < len(lines) and '"""' in lines[line_num + 1]:
        return lines  # Already has docstring

    # Insert docstring lines
    doc_lines = docstring.split('\n')
    for i, doc_line in enumerate(doc_lines):
        lines.insert(line_num + 1 + i, ' ' * indent + doc_line if doc_line.strip() else '')

    return lines


def process_function_library(filepath: Path):
    """Add all docstrings to function_library.py."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove trailing newlines for processing
    lines = [line.rstrip('\n') for line in lines]

    modifications = 0

    # Find each method and add docstring
    for i, line in enumerate(lines):
        for key, docstring in DOCSTRINGS.items():
            class_name, method_name = key.split('.')

            # Match method definition
            if f'class {class_name}' in line or (i > 0 and f'class {class_name}' in lines[i-5:i]):
                # Check if this is the method we're looking for
                if f'    def {method_name}(' in line or f'    def {method_name}(' in line:
                    # Check if already has docstring
                    if i + 1 < len(lines) and '"""' not in lines[i + 1]:
                        lines = add_docstring_after_line(lines, i, docstring, indent=8)
                        modifications += 1
                        break  # Move to next line

    # Write back
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')

    return modifications


def main():
    filepath = Path('src/symbo_agentic_reasoners/core/symbolic/function_library.py')

    print("Processing function_library.py...")
    print("Adding comprehensive docstrings...")

    mods = process_function_library(filepath)

    print(f"Completed! Added {mods} docstrings.")
    print("\nVerifying...")

    # Verify
    import ast
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())

    total = 0
    missing = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.name.startswith('__'):
            total += 1
            if not ast.get_docstring(node):
                missing += 1

    coverage = ((total - missing) / total * 100) if total > 0 else 100
    print(f"Coverage: {total - missing}/{total} ({coverage:.1f}%)")
    print(f"Remaining: {missing} methods")


if __name__ == '__main__':
    main()
