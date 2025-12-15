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
Differentiation Specialist
==========================

Pure Python symbolic differentiation engine implementing standard calculus rules.

Differentiation Rules:
- Constants: d/dx(c) = 0
- Power rule: d/dx(x^n) = n*x^(n-1)
- Sum rule: d/dx(f + g) = f' + g'
- Product rule: d/dx(f * g) = f'*g + f*g'
- Quotient rule: d/dx(f/g) = (f'*g - f*g') / g^2
- Chain rule: d/dx(f(g(x))) = f'(g(x)) * g'(x)
- Standard functions: sin, cos, tan, exp, ln, etc.
"""

import logging
from typing import Dict, Callable, List
from fractions import Fraction
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg

logger = logging.getLogger(__name__)

class DifferentiationEngine:
    """
    Pure Python symbolic differentiation engine.

    Implements standard differentiation rules without SymPy.
    """

    # Derivatives of standard functions
    FUNCTION_DERIVATIVES = {
        'sin': lambda x: Func('cos', x),
        'cos': lambda x: neg(Func('sin', x)),
        'tan': lambda x: power(Func('sec', x), Num(2)),
        'sec': lambda x: mul(Func('sec', x), Func('tan', x)),
        'csc': lambda x: neg(mul(Func('csc', x), Func('cot', x))),
        'cot': lambda x: neg(power(Func('csc', x), Num(2))),
        'exp': lambda x: Func('exp', x),
        'ln': lambda x: power(x, Num(-1)),
        'log': lambda x: power(x, Num(-1)),  # natural log
        'sqrt': lambda x: mul(Num(Fraction(1, 2)), power(x, Num(Fraction(-1, 2)))),
        'asin': lambda x: power(add(Num(1), neg(power(x, Num(2)))), Num(Fraction(-1, 2))),
        'acos': lambda x: neg(power(add(Num(1), neg(power(x, Num(2)))), Num(Fraction(-1, 2)))),
        'atan': lambda x: power(add(Num(1), power(x, Num(2))), Num(-1)),
        'sinh': lambda x: Func('cosh', x),
        'cosh': lambda x: Func('sinh', x),
        'tanh': lambda x: power(Func('sech', x), Num(2)),
    }

    def differentiate(self, expr: Expr, var: str) -> Expr:
        """
        Differentiate expression with respect to variable.

        Args:
            expr: Expression to differentiate
            var: Variable name (e.g., 'x')

        Returns:
            Derivative expression
        """
        return self._diff(expr, var)

    def _diff(self, expr: Expr, var: str) -> Expr:
        """Internal differentiation dispatcher."""

        # Constant: d/dx(c) = 0
        if isinstance(expr, Num):
            return Num(0)

        # Symbol: d/dx(x) = 1, d/dx(y) = 0
        if isinstance(expr, Sym):
            if expr.name == var:
                return Num(1)
            else:
                return Num(0)  # Treat other symbols as constants

        # Negation: d/dx(-f) = -f'
        if isinstance(expr, Neg):
            return neg(self._diff(expr.arg, var))

        # Sum: d/dx(f + g + ...) = f' + g' + ...
        if isinstance(expr, Add):
            return add(*[self._diff(t, var) for t in expr.terms])

        # Product: d/dx(f * g) = f'*g + f*g'
        # Extended: d/dx(f * g * h) = f'*g*h + f*g'*h + f*g*h'
        if isinstance(expr, Mul):
            return self._diff_product(expr.factors, var)

        # Power: d/dx(f^g)
        if isinstance(expr, Pow):
            return self._diff_power(expr, var)

        # Function: d/dx(f(g)) = f'(g) * g' (chain rule)
        if isinstance(expr, Func):
            return self._diff_func(expr, var)

        raise ValueError(f"Cannot differentiate expression type: {type(expr)}")

    def _diff_product(self, factors: List[Expr], var: str) -> Expr:
        """
        Differentiate a product using generalized product rule.

        d/dx(f1 * f2 * ... * fn) = sum over i of (fi' * product of fj for j != i)
        """
        if len(factors) == 1:
            return self._diff(factors[0], var)

        # f * g -> f'*g + f*g'
        if len(factors) == 2:
            f, g = factors
            f_prime = self._diff(f, var)
            g_prime = self._diff(g, var)
            return add(mul(f_prime, g), mul(f, g_prime))

        # Recursive: (f * rest)' = f' * rest + f * rest'
        f = factors[0]
        rest = Mul(factors[1:]) if len(factors) > 2 else factors[1]
        f_prime = self._diff(f, var)
        rest_prime = self._diff_product(factors[1:], var) if len(factors) > 2 else self._diff(factors[1], var)
        return add(mul(f_prime, rest), mul(f, rest_prime))

    def _diff_power(self, expr: Pow, var: str) -> Expr:
        """
        Differentiate power expression.

        Cases:
        1. x^n where n is constant: n*x^(n-1) (power rule)
        2. a^x where a is constant: a^x * ln(a) (exponential rule)
        3. f^g general case: f^g * (g' * ln(f) + g * f'/f) (logarithmic differentiation)
        """
        base, exp = expr.base, expr.exp

        base_has_var = self._contains_var(base, var)
        exp_has_var = self._contains_var(exp, var)

        # Case 1: x^n (power rule)
        if base_has_var and not exp_has_var:
            # d/dx(f^n) = n * f^(n-1) * f'
            f_prime = self._diff(base, var)
            n_minus_1 = self._subtract_one(exp)
            return mul(exp, power(base, n_minus_1), f_prime)

        # Case 2: a^x (exponential rule)
        if not base_has_var and exp_has_var:
            # d/dx(a^g) = a^g * ln(a) * g'
            g_prime = self._diff(exp, var)
            return mul(expr, Func('ln', base), g_prime)

        # Case 3: f^g (logarithmic differentiation)
        if base_has_var and exp_has_var:
            # d/dx(f^g) = f^g * (g' * ln(f) + g * f' / f)
            f_prime = self._diff(base, var)
            g_prime = self._diff(exp, var)
            term1 = mul(g_prime, Func('ln', base))
            term2 = mul(exp, f_prime, power(base, Num(-1)))
            return mul(expr, add(term1, term2))

        # Neither has variable - it's a constant
        return Num(0)

    def _diff_func(self, expr: Func, var: str) -> Expr:
        """
        Differentiate function using chain rule.

        d/dx(f(g(x))) = f'(g(x)) * g'(x)
        """
        fname = expr.name
        arg = expr.arg

        # Get derivative of outer function
        if fname in self.FUNCTION_DERIVATIVES:
            outer_deriv = self.FUNCTION_DERIVATIVES[fname](arg)
        else:
            # Unknown function - leave symbolic
            outer_deriv = Func(f"d{fname}", arg)

        # Get derivative of inner function (chain rule)
        inner_deriv = self._diff(arg, var)

        # Combine: f'(g) * g'
        return mul(outer_deriv, inner_deriv)

    def _contains_var(self, expr: Expr, var: str) -> bool:
        """Check if expression contains the variable."""
        if isinstance(expr, Num):
            return False
        if isinstance(expr, Sym):
            return expr.name == var
        if isinstance(expr, Neg):
            return self._contains_var(expr.arg, var)
        if isinstance(expr, Add):
            return any(self._contains_var(t, var) for t in expr.terms)
        if isinstance(expr, Mul):
            return any(self._contains_var(f, var) for f in expr.factors)
        if isinstance(expr, Pow):
            return self._contains_var(expr.base, var) or self._contains_var(expr.exp, var)
        if isinstance(expr, Func):
            return self._contains_var(expr.arg, var)
        return False

    def _subtract_one(self, expr: Expr) -> Expr:
        """Subtract 1 from expression (for power rule)."""
        if isinstance(expr, Num):
            return Num(expr.value - 1)
        return add(expr, Num(-1))

