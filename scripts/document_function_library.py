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
Batch Documentation for function_library.py
============================================

Adds comprehensive, mathematically rigorous docstrings to all
mathematical function classes (trig, exponential, etc.).
"""

# Complete docstring additions for all functions
FUNCTION_DOCSTRINGS = {
    'Cos.diff': '''"""Compute derivative of cos(f) with respect to var.

        Uses chain rule: d/dx cos(f(x)) = -sin(f(x)) * f'(x)

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Cos(x**2).diff(x)
            -2*x*sin(x**2)
        """''',

    'Cos.evalf': '''"""Numerically evaluate cos(x) to floating-point.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Cos(0).evalf()
            1.0
            >>> Cos(math.pi).evalf()
            -1.0
        """''',

    'Cos.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> Cos(Symbol('x')).to_latex()
            '\\\\cos\\\\left(x\\\\right)'
        """''',

    'Tan.diff': '''"""Compute derivative of tan(f) with respect to var.

        Uses chain rule: d/dx tan(f(x)) = sec²(f(x)) * f'(x) = f'(x)/cos²(f(x))

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Tan(x).diff(x)
            1/cos(x)**2
        """''',

    'Tan.evalf': '''"""Numerically evaluate tan(x) to floating-point.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Tan(0).evalf()
            0.0
            >>> Tan(math.pi/4).evalf()
            1.0
        """''',

    'Tan.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> Tan(Symbol('x')).to_latex()
            '\\\\tan\\\\left(x\\\\right)'
        """''',

    'Exp.diff': '''"""Compute derivative of exp(f) with respect to var.

        Uses chain rule: d/dx exp(f(x)) = exp(f(x)) * f'(x)

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Exp(x**2).diff(x)
            2*x*exp(x**2)
        """''',

    'Exp.evalf': '''"""Numerically evaluate exp(x) to floating-point.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Exp(0).evalf()
            1.0
            >>> Exp(1).evalf()
            2.718281828459045
        """''',

    'Exp.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> x = Symbol('x')
            >>> Exp(x).to_latex()
            'e^{x}'
        """''',

    'Log.diff': '''"""Compute derivative of log(f) with respect to var.

        Uses chain rule: d/dx log(f(x)) = f'(x)/f(x)

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Log(x**2).diff(x)
            2/x
        """''',

    'Log.evalf': '''"""Numerically evaluate natural log to floating-point.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Log(1).evalf()
            0.0
            >>> Log(math.e).evalf()
            1.0
        """''',

    'Log.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> x = Symbol('x')
            >>> Log(x).to_latex()
            '\\\\ln\\\\left(x\\\\right)'
        """''',

    'Sqrt.diff': '''"""Compute derivative of sqrt(f) with respect to var.

        Uses chain rule: d/dx sqrt(f(x)) = f'(x)/(2*sqrt(f(x)))

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Sqrt(x).diff(x)
            1/(2*sqrt(x))
        """''',

    'Sqrt.evalf': '''"""Numerically evaluate square root to floating-point.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Sqrt(4).evalf()
            2.0
            >>> Sqrt(2).evalf()
            1.4142135623730951
        """''',

    'Sqrt.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> x = Symbol('x')
            >>> Sqrt(x).to_latex()
            '\\\\sqrt{x}'
        """''',

    'Abs.diff': '''"""Compute derivative of |f| with respect to var.

        Uses: d/dx |f(x)| = sign(f(x)) * f'(x)

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression

        Example:
            >>> x = Symbol('x')
            >>> Abs(x).diff(x)
            sign(x)
        """''',

    'Abs.evalf': '''"""Numerically evaluate absolute value to floating-point.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Numerical value (float) or symbolic expression

        Example:
            >>> Abs(-5).evalf()
            5.0
        """''',

    'Abs.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> x = Symbol('x')
            >>> Abs(x).to_latex()
            '\\\\left|x\\\\right|'
        """''',

    'Sign.diff': '''"""Compute derivative of sign function.

        The derivative is 0 almost everywhere (undefined at 0).

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Integer(0) expression

        Note:
            Derivative is undefined at x=0, but returns 0 for symbolic purposes.
        """''',

    'Sign.evalf': '''"""Numerically evaluate sign function.

        Returns -1 for negative, 0 for zero, +1 for positive.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            -1.0, 0.0, or 1.0 if numeric, else symbolic expression

        Example:
            >>> Sign(-5).evalf()
            -1.0
            >>> Sign(3).evalf()
            1.0
        """''',

    'Sign.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string for mathematical typesetting

        Example:
            >>> x = Symbol('x')
            >>> Sign(x).to_latex()
            '\\\\text{sign}\\\\left(x\\\\right)'
        """''',

    'GenericFunction.diff': '''"""Compute symbolic derivative for unknown function.

        Returns a Derivative object since the function form is unknown.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative(self, var) expression

        Example:
            >>> f = GenericFunction('f', Symbol('x'))
            >>> f.diff(Symbol('x'))
            Derivative(f(x), x)
        """''',

    'GenericFunction.evalf': '''"""Return symbolic form (cannot evaluate unknown function).

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Self (symbolic expression)

        Note:
            Generic functions cannot be numerically evaluated.
        """''',

    'GenericFunction.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string with function name and arguments

        Example:
            >>> f = GenericFunction('f', Symbol('x'))
            >>> f.to_latex()
            '\\\\text{f}\\\\left(x\\\\right)'
        """''',

    'Factorial.diff': '''"""Compute derivative of factorial via gamma function.

        Uses: d/dn n! = n! * ψ(n+1) where ψ is the digamma function.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression using digamma function

        Note:
            Factorial is typically defined for non-negative integers,
            but extended via gamma function: n! = Γ(n+1)
        """''',

    'Factorial.evalf': '''"""Numerically evaluate factorial.

        Computes n! for non-negative integer n.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            n! as float if n is non-negative integer, else symbolic

        Example:
            >>> Factorial(5).evalf()
            120.0
            >>> Factorial(10).evalf()
            3628800.0
        """''',

    'Factorial.simplify': '''"""Simplify factorial of integer to its value.

        Evaluates n! if argument is a non-negative integer.

        Returns:
            Integer(n!) if argument is Integer, else self

        Example:
            >>> Factorial(Integer(5)).simplify()
            120
        """''',

    'Factorial.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string with factorial notation

        Example:
            >>> x = Symbol('x')
            >>> Factorial(x).to_latex()
            'x!'
        """''',

    'Gamma.diff': '''"""Compute derivative of Gamma function.

        Uses: d/dx Γ(x) = Γ(x) * ψ(x) where ψ is the digamma function.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative expression using digamma function

        Note:
            Gamma function generalizes factorial: Γ(n) = (n-1)!
        """''',

    'Gamma.evalf': '''"""Numerically evaluate Gamma function.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Γ(x) as float if numeric, else symbolic

        Example:
            >>> Gamma(5).evalf()
            24.0
            >>> Gamma(0.5).evalf()
            1.7724538509055159  # sqrt(pi)
        """''',

    'Gamma.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string with Gamma notation

        Example:
            >>> x = Symbol('x')
            >>> Gamma(x).to_latex()
            '\\\\Gamma\\\\left(x\\\\right)'
        """''',

    'Gcd.diff': '''"""Compute derivative of GCD (always zero).

        GCD operates on integers and is not differentiable.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Integer(0)

        Note:
            GCD is a discrete function defined only for integers.
        """''',

    'Gcd.evalf': '''"""Numerically evaluate GCD of integers.

        Computes greatest common divisor using Euclidean algorithm.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            GCD as float if all args are integers, else symbolic

        Example:
            >>> Gcd(12, 18).evalf()
            6.0
            >>> Gcd(35, 49, 14).evalf()
            7.0
        """''',

    'Gcd.simplify': '''"""Simplify GCD of integer constants.

        Evaluates GCD if all arguments are Integer objects.

        Returns:
            Integer(gcd(...)) if all args are integers, else self

        Example:
            >>> Gcd(Integer(12), Integer(18)).simplify()
            6
        """''',

    'Gcd.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string with gcd notation

        Example:
            >>> Gcd(Symbol('a'), Symbol('b')).to_latex()
            '\\\\gcd\\\\left(a, b\\\\right)'
        """''',

    'Floor.diff': '''"""Compute derivative of floor function (zero almost everywhere).

        Floor function has zero derivative except at integer points
        where it's undefined.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Integer(0)

        Note:
            Derivative is undefined at integer values but returns 0 symbolically.
        """''',

    'Floor.evalf': '''"""Numerically evaluate floor function.

        Computes ⌊x⌋ = greatest integer ≤ x.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Floor value as float if numeric, else symbolic

        Example:
            >>> Floor(3.7).evalf()
            3.0
            >>> Floor(-2.3).evalf()
            -3.0
        """''',

    'Floor.simplify': '''"""Simplify floor of numeric values.

        Evaluates floor if argument is Integer or Float.

        Returns:
            Integer(⌊x⌋) if argument is numeric, else self

        Example:
            >>> Floor(Float(3.7)).simplify()
            3
        """''',

    'Floor.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string with floor notation

        Example:
            >>> Floor(Symbol('x')).to_latex()
            '\\\\lfloor x \\\\rfloor'
        """''',

    'Ceil.diff': '''"""Compute derivative of ceiling function (zero almost everywhere).

        Ceiling function has zero derivative except at integer points
        where it's undefined.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Integer(0)

        Note:
            Derivative is undefined at integer values but returns 0 symbolically.
        """''',

    'Ceil.evalf': '''"""Numerically evaluate ceiling function.

        Computes ⌈x⌉ = smallest integer ≥ x.

        Args:
            precision: Number of decimal digits (default: 15)

        Returns:
            Ceiling value as float if numeric, else symbolic

        Example:
            >>> Ceil(3.2).evalf()
            4.0
            >>> Ceil(-2.7).evalf()
            -2.0
        """''',

    'Ceil.simplify': '''"""Simplify ceiling of numeric values.

        Evaluates ceiling if argument is Integer or Float.

        Returns:
            Integer(⌈x⌉) if argument is numeric, else self

        Example:
            >>> Ceil(Float(3.2)).simplify()
            4
        """''',

    'Ceil.to_latex': '''"""Convert to LaTeX representation.

        Returns:
            LaTeX string with ceiling notation

        Example:
            >>> Ceil(Symbol('x')).to_latex()
            '\\\\lceil x \\\\rceil'
        """''',
}


def add_docstrings_to_file(filepath: str):
    """Add all missing docstrings to function_library.py."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Process each docstring addition
    for key, docstring in FUNCTION_DOCSTRINGS.items():
        class_name, method_name = key.split('.')

        # Find the method definition
        pattern = rf'(class {class_name}\(Function\):.*?)(    def {method_name}\([^)]*\):)(.*?)(\n        [a-z#])'

        def replace_func(match):
            before_class = match.group(1)
            def_line = match.group(2)
            method_body_start = match.group(3)
            next_line = match.group(4)

            # Check if docstring already exists
            if '"""' in method_body_start:
                return match.group(0)

            # Insert docstring after def line
            return f'{before_class}{def_line}\n{docstring}{method_body_start}{next_line}'

        content = re.sub(pattern, replace_func, content, flags=re.DOTALL)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Added {len(FUNCTION_DOCSTRINGS)} docstrings to {filepath}")


if __name__ == '__main__':
    import sys
    import re

    if len(sys.argv) > 1:
        add_docstrings_to_file(sys.argv[1])
    else:
        add_docstrings_to_file('src/symbo_agentic_reasoners/core/symbolic/function_library.py')
        print("Done!")
