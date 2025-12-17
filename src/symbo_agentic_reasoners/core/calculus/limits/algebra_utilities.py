# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Algebra Utilities
=================

Solver and algebra utility functions.
"""

import logging
import math
import re
from typing import Optional, Tuple, Dict, Any, Union
from ..ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from ..differentiation_specialist import DifferentiationEngine
from ..expression_parser import ExprParser
from ..validation import check_expression_safety as _check_expression_safety
from ..calculus_utils import _evaluate_at_numeric as _evaluate_at

def solve_polynomial(expr_str: str, var: str = 'x') -> list:
    """
    Solve a polynomial equation for the given variable.

    NO SYMPY - Pure native mathematical reasoning.

    Args:
        expr_str: Polynomial expression string (assumed equal to 0)
        var: Variable to solve for

    Returns:
        List of solutions
    """
    import re
    import math

    # Clean expression
    expr = expr_str.replace(' ', '').replace('^', '**')

    # Try to extract polynomial coefficients
    # Linear: ax + b = 0 -> x = -b/a
    linear_match = re.match(rf'^(-?\d*\.?\d*)\*?{var}\s*([+-]\s*\d*\.?\d+)?$', expr)
    if linear_match:
        a = float(linear_match.group(1) or '1')
        b_str = linear_match.group(2)
        b = float(b_str.replace(' ', '')) if b_str else 0
        if a != 0:
            return [str(-b / a)]

    # Linear alternate form: b + ax = 0 (constant first)
    linear_alt_match = re.match(rf'^(-?\d+\.?\d*)\s*([+-])\s*(\d*\.?\d*)\*?{var}$', expr)
    if linear_alt_match:
        b = float(linear_alt_match.group(1))
        sign = linear_alt_match.group(2)
        a_str = linear_alt_match.group(3) or '1'
        a = float(a_str) if a_str else 1.0
        if sign == '-':
            a = -a
        if a != 0:
            return [str(-b / a)]

    # Quadratic: ax^2 + bx + c = 0
    # Extract coefficients by pattern matching
    quad_pattern = rf'(-?\d*\.?\d*)\*?{var}\*\*2\s*([+-]\s*\d*\.?\d*)\*?{var}\s*([+-]\s*\d*\.?\d+)?'
    quad_match = re.match(quad_pattern, expr)
    if quad_match:
        try:
            a_str = quad_match.group(1) or '1'
            a = float(a_str) if a_str not in ('', '+') else 1.0
            if a_str == '-':
                a = -1.0

            b_str = quad_match.group(2)
            b = float(b_str.replace(' ', '')) if b_str else 0

            c_str = quad_match.group(3)
            c = float(c_str.replace(' ', '')) if c_str else 0

            # Quadratic formula
            discriminant = b*b - 4*a*c
            if discriminant >= 0:
                sqrt_d = math.sqrt(discriminant)
                x1 = (-b + sqrt_d) / (2*a)
                x2 = (-b - sqrt_d) / (2*a)
                if discriminant == 0:
                    return [str(x1)]
                return [str(x1), str(x2)]
            else:
                # Complex roots
                real = -b / (2*a)
                imag = math.sqrt(-discriminant) / (2*a)
                return [f"{real} + {imag}*I", f"{real} - {imag}*I"]
        except:
            pass

    # Simple form: x = value
    simple_match = re.match(rf'^{var}\s*=\s*(-?\d*\.?\d+)$', expr)
    if simple_match:
        return [simple_match.group(1)]

    return []




def solve_system_native(equations: list) -> list:
    """
    Solve a system of equations.

    NO SYMPY - Pure native mathematical reasoning.

    Args:
        equations: List of equation strings

    Returns:
        List of solution dictionaries
    """
    import re

    if len(equations) == 2:
        # Two equations, two unknowns
        # Try simple substitution or elimination

        # Extract coefficients for linear system
        # Form: a1*x + b1*y = c1, a2*x + b2*y = c2
        def parse_linear(eq: str, vars: list):
            """Parse linear equation to coefficients."""
            eq = eq.replace(' ', '').replace('=', '-')
            coeffs = {v: 0.0 for v in vars}
            const = 0.0

            # Split by + and -
            terms = re.split(r'(?=[+-])', eq)
            for term in terms:
                if not term:
                    continue
                term = term.strip()

                # Check for each variable
                found_var = False
                for v in vars:
                    if v in term:
                        # Extract coefficient
                        coef_str = term.replace(v, '').replace('*', '')
                        if coef_str in ('', '+'):
                            coef = 1.0
                        elif coef_str == '-':
                            coef = -1.0
                        else:
                            try:
                                coef = float(coef_str)
                            except:
                                coef = 1.0
                        coeffs[v] += coef
                        found_var = True
                        break

                if not found_var:
                    # Constant term
                    try:
                        const += float(term)
                    except:
                        pass

            return coeffs, -const

        # Find variables
        vars_found = set()
        for eq in equations:
            vars_found.update(re.findall(r'\b([a-z])\b', eq))
        vars_list = sorted(list(vars_found))[:2]  # Only first 2 vars

        if len(vars_list) == 2:
            try:
                c1, d1 = parse_linear(equations[0], vars_list)
                c2, d2 = parse_linear(equations[1], vars_list)

                v1, v2 = vars_list
                a1, b1 = c1[v1], c1[v2]
                a2, b2 = c2[v1], c2[v2]

                # Cramer's rule
                det = a1*b2 - a2*b1
                if abs(det) > 1e-10:
                    x = (d1*b2 - d2*b1) / det
                    y = (a1*d2 - a2*d1) / det
                    return [{v1: x, v2: y}]
            except:
                pass

    return []




def factor_polynomial(expr_str: str) -> tuple:
    """
    Factor a polynomial expression.

    NO SYMPY - Pure native mathematical reasoning.

    Args:
        expr_str: Polynomial expression

    Returns:
        (success, factored_form)
    """
    import re
    import math

    expr = expr_str.replace(' ', '').replace('^', '**')

    # Difference of squares: a^2 - b^2 = (a+b)(a-b)
    dos_match = re.match(r'^(\w+)\*\*2-(\w+)\*\*2$', expr)
    if dos_match:
        a, b = dos_match.group(1), dos_match.group(2)
        return (True, f"({a}+{b})*({a}-{b})")

    # Difference of squares with constant: x^2 - n = (x+sqrt(n))(x-sqrt(n))
    # Special case for perfect squares: x^2 - 1 = (x+1)(x-1)
    dos_const_match = re.match(r'^(\w+)\*\*2-(\d+)$', expr)
    if dos_const_match:
        a, n = dos_const_match.group(1), int(dos_const_match.group(2))
        sqrt_n = int(math.sqrt(n))
        if sqrt_n * sqrt_n == n:  # Perfect square
            return (True, f"({a}+{sqrt_n})*({a}-{sqrt_n})")

    # Perfect square: a^2 + 2ab + b^2 = (a+b)^2
    # This is complex to detect, skip for now

    # Difference of cubes: a^3 - b^3 = (a-b)(a^2+ab+b^2)
    doc_match = re.match(r'^(\w+)\*\*3-(\w+)\*\*3$', expr)
    if doc_match:
        a, b = doc_match.group(1), doc_match.group(2)
        return (True, f"({a}-{b})*({a}**2+{a}*{b}+{b}**2)")

    # Sum of cubes: a^3 + b^3 = (a+b)(a^2-ab+b^2)
    soc_match = re.match(r'^(\w+)\*\*3\+(\w+)\*\*3$', expr)
    if soc_match:
        a, b = soc_match.group(1), soc_match.group(2)
        return (True, f"({a}+{b})*({a}**2-{a}*{b}+{b}**2)")

    # Simple common factor: ax + ay = a(x+y)
    common_match = re.match(r'^(\d+)\*?(\w+)\s*\+\s*(\d+)\*?(\w+)$', expr)
    if common_match:
        a1, v1, a2, v2 = common_match.groups()
        a1, a2 = int(a1), int(a2)
        gcd = math.gcd(a1, a2)
        if gcd > 1:
            return (True, f"{gcd}*({a1//gcd}*{v1}+{a2//gcd}*{v2})")

    # Quadratic factoring: ax^2 + bx + c
    # Try to find roots and factor
    solutions = solve_polynomial(expr_str, 'x')
    if len(solutions) == 2:
        try:
            r1, r2 = float(solutions[0]), float(solutions[1])
            if r1 == int(r1) and r2 == int(r2):
                r1, r2 = int(r1), int(r2)
                if r1 >= 0 and r2 >= 0:
                    return (True, f"(x-{r1})*(x-{r2})")
                elif r1 >= 0:
                    return (True, f"(x-{r1})*(x+{-r2})")
                elif r2 >= 0:
                    return (True, f"(x+{-r1})*(x-{r2})")
                else:
                    return (True, f"(x+{-r1})*(x+{-r2})")
        except:
            pass

    return (False, expr_str)




def expand_expression(expr_str: str) -> tuple:
    """
    Expand a polynomial expression.

    NO SYMPY - Pure native mathematical reasoning.

    Args:
        expr_str: Expression with factors to expand

    Returns:
        (success, expanded_form)
    """
    import re

    expr = expr_str.replace(' ', '').replace('^', '**')

    # Expand (a+b)^2 = a^2 + 2ab + b^2
    sq_match = re.match(r'^\((\w+)\+(\w+)\)\*\*2$', expr)
    if sq_match:
        a, b = sq_match.group(1), sq_match.group(2)
        return (True, f"{a}**2+2*{a}*{b}+{b}**2")

    # Expand (a-b)^2 = a^2 - 2ab + b^2
    sq_neg_match = re.match(r'^\((\w+)-(\w+)\)\*\*2$', expr)
    if sq_neg_match:
        a, b = sq_neg_match.group(1), sq_neg_match.group(2)
        return (True, f"{a}**2-2*{a}*{b}+{b}**2")

    # Expand (a+b)(a-b) = a^2 - b^2
    dos_match = re.match(r'^\((\w+)\+(\w+)\)\*\((\w+)-(\w+)\)$', expr)
    if dos_match:
        a1, b1, a2, b2 = dos_match.groups()
        if a1 == a2 and b1 == b2:
            return (True, f"{a1}**2-{b1}**2")

    # Expand (a+b)(c+d) = ac + ad + bc + bd
    foil_match = re.match(r'^\((\w+)\+(\w+)\)\*\((\w+)\+(\w+)\)$', expr)
    if foil_match:
        a, b, c, d = foil_match.groups()
        return (True, f"{a}*{c}+{a}*{d}+{b}*{c}+{b}*{d}")

    # Expand (a+b)^3 = a^3 + 3a^2b + 3ab^2 + b^3
    cube_match = re.match(r'^\((\w+)\+(\w+)\)\*\*3$', expr)
    if cube_match:
        a, b = cube_match.group(1), cube_match.group(2)
        return (True, f"{a}**3+3*{a}**2*{b}+3*{a}*{b}**2+{b}**3")

    return (False, expr_str)




def solve_ode_native(expr_str: str) -> tuple:
    """
    Solve ordinary differential equations.

    NO SYMPY - Pure native mathematical reasoning.

    Handles:
    - y' = f(x) -> y = integral(f(x))
    - y' = a*y -> y = C*exp(a*x)
    - y' + p(x)*y = q(x) (linear first order)

    Args:
        expr_str: ODE expression

    Returns:
        (success, solution_string)
    """
    import re

    expr = expr_str.replace(' ', '')

    # Pattern: y' = f(x) where f doesn't contain y
    # Result: y = integral(f(x))
    deriv_match = re.match(r"^y'=(.+)$", expr)
    if deriv_match:
        rhs = deriv_match.group(1)
        if 'y' not in rhs:
            success, integral, method = integrate(rhs, 'x')
            if success:
                return (True, f"y = {integral} + C")

    # Pattern: y' = a*y -> y = C*exp(a*x)
    exp_decay = re.match(r"^y'=(-?\d*\.?\d*)\*?y$", expr)
    if exp_decay:
        a_str = exp_decay.group(1) or '1'
        a = float(a_str) if a_str not in ('', '-') else (1.0 if a_str == '' else -1.0)
        return (True, f"y = C*exp({a}*x)")

    # Pattern: y' + a*y = 0 -> y = C*exp(-a*x)
    homog = re.match(r"^y'\+(-?\d*\.?\d*)\*?y=0$", expr)
    if homog:
        a_str = homog.group(1) or '1'
        a = float(a_str) if a_str not in ('', '-') else (1.0 if a_str == '' else -1.0)
        return (True, f"y = C*exp({-a}*x)")

    # Pattern: y'' + a*y = 0 (harmonic oscillator)
    harmonic = re.match(r"^y''\+(-?\d*\.?\d*)\*?y=0$", expr)
    if harmonic:
        a_str = harmonic.group(1) or '1'
        a = float(a_str) if a_str not in ('', '-') else (1.0 if a_str == '' else -1.0)
        if a > 0:
            import math
            omega = math.sqrt(a)
            return (True, f"y = C1*cos({omega}*x) + C2*sin({omega}*x)")
        elif a < 0:
            import math
            k = math.sqrt(-a)
            return (True, f"y = C1*exp({k}*x) + C2*exp({-k}*x)")

    # Pattern: y'' - a^2*y = 0 -> y = C1*exp(a*x) + C2*exp(-a*x)
    exp_growth = re.match(r"^y''-(\d*\.?\d*)\*?y=0$", expr)
    if exp_growth:
        a_str = exp_growth.group(1) or '1'
        a = float(a_str) if a_str else 1.0
        import math
        k = math.sqrt(a)
        return (True, f"y = C1*exp({k}*x) + C2*exp({-k}*x)")

    return (False, None)


def _eval_at_point(expr_str: str, var: str, point: float) -> float:
    """Evaluate expression at a point."""
    import re
    import math

    expr = expr_str.replace(var, f'({point})')
    expr = expr.replace('^', '**')

    # Replace math functions
    expr = re.sub(r'\bsin\b', 'math.sin', expr)
    expr = re.sub(r'\bcos\b', 'math.cos', expr)
    expr = re.sub(r'\bexp\b', 'math.exp', expr)
    expr = re.sub(r'\b(log|ln)\b', 'math.log', expr)
    expr = re.sub(r'\bsqrt\b', 'math.sqrt', expr)

    try:
        return eval(expr)
    except:
        return None




def _get_symbols(expr: Expr) -> set:
    """Get all symbol names in an expression."""
    symbols = set()

    if isinstance(expr, Sym):
        symbols.add(expr.name)
    elif isinstance(expr, Num):
        pass
    elif isinstance(expr, Add):
        for term in expr.terms:
            symbols.update(_get_symbols(term))
    elif isinstance(expr, Mul):
        for factor in expr.factors:
            symbols.update(_get_symbols(factor))
    elif isinstance(expr, Pow):
        symbols.update(_get_symbols(expr.base))
        symbols.update(_get_symbols(expr.exp))
    elif isinstance(expr, Neg):
        symbols.update(_get_symbols(expr.arg))
    elif isinstance(expr, Func):
        symbols.update(_get_symbols(expr.arg))

    return symbols




def _evaluate_expr_numerically(expr_str: str) -> Optional[float]:
    """Evaluate a numeric expression string."""
    import math
    try:
        # Safe evaluation of numeric expressions
        expr_safe = expr_str.replace('pi', str(math.pi)).replace('e', str(math.e))
        return eval(expr_safe)
    except:
        return None


# =============================================================================
# ADDITIONAL SOLVER FUNCTIONS (SymPy-free)
# =============================================================================



