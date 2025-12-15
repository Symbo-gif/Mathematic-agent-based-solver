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
Rational Equation Handling
==========================

This module contains algorithms for:
- Rational root theorem for finding integer/rational roots
- Rational equation detection and clearing
- Biquadratic equations (special case of quartics)

These are domain-specific algorithms that don't require SymPy.
"""

from typing import Any, List, Optional, Tuple
from math import isqrt
from fractions import Fraction

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, Integer, Rational, Float
)
import symbo_agentic_reasoners.core.native_symbolic as sp


def find_rational_roots(coeffs: List[int]) -> List[Rational]:
    """
    Find rational roots using the Rational Root Theorem.

    If p(x) = a_n*x^n + ... + a_0 has a rational root p/q in lowest terms,
    then p divides a_0 and q divides a_n.

    Args:
        coeffs: Integer coefficients [a_n, a_{n-1}, ..., a_0]

    Returns:
        List of rational roots found (may be empty)
    """
    if not coeffs or all(c == 0 for c in coeffs):
        return []

    # Need integer coefficients
    try:
        int_coeffs = [int(c) for c in coeffs]
    except (TypeError, ValueError):
        return []

    a_n = int_coeffs[0]  # Leading coefficient
    a_0 = int_coeffs[-1]  # Constant term

    if a_n == 0 or a_0 == 0:
        # Handle special cases
        if a_0 == 0:
            # x=0 is a root, but we handle this separately
            return [Rational(0)]
        return []

    # Find divisors
    def divisors(n: int) -> List[int]:
        n = abs(n)
        if n == 0:
            return []
        divs = []
        for i in range(1, isqrt(n) + 1):
            if n % i == 0:
                divs.append(i)
                if i != n // i:
                    divs.append(n // i)
        return sorted(divs)

    p_divisors = divisors(a_0)
    q_divisors = divisors(a_n)

    # Test all possible p/q
    roots = []
    tested = set()

    for p in p_divisors:
        for q in q_divisors:
            for sign in [1, -1]:
                candidate = Rational(sign * p, q)
                if candidate in tested:
                    continue
                tested.add(candidate)

                # Evaluate polynomial at candidate
                result = 0
                x_power = 1
                for coeff in reversed(int_coeffs):
                    result += coeff * x_power
                    x_power *= candidate

                if result == 0:
                    roots.append(candidate)

    return roots


def is_rational_equation(expr) -> bool:
    """
    Check if expression contains fractions with polynomial denominators.

    Returns True if the expression has terms like 1/x, 2/(x-1), etc.
    """
    if not hasattr(expr, 'free_symbols') or not expr.free_symbols:
        return False

    # Check for Pow with negative exponent (represents division)
    for atom in expr.atoms():
        if hasattr(atom, 'is_Pow') and atom.is_Pow:
            if hasattr(atom.exp, 'is_negative') and atom.exp.is_negative:
                # Check if base contains variables
                if atom.base.free_symbols:
                    return True

    # Also check for Mul with negative powers
    if hasattr(expr, 'args'):
        for arg in sp.preorder_traversal(expr):
            if arg.is_Pow and arg.exp.is_number and arg.exp < 0:
                if arg.base.free_symbols:
                    return True

    return False


def clear_denominators(expr, var: Symbol) -> Tuple[Any, List[Any]]:
    """
    Clear denominators from a rational equation by multiplying by LCD.

    For equation like: 2/x + 3/(x-1) = 5
    - Find all denominator terms: [x, x-1]
    - Compute LCD (product for coprime denominators)
    - Multiply entire equation by LCD to get polynomial

    Args:
        expr: SymPy expression (equation - RHS, so it's f(x) = 0)
        var: Variable to solve for

    Returns:
        Tuple of (cleared_polynomial, list_of_denominators)
        where denominators are tracked to filter extraneous solutions
    """
    # Use SymPy's together() to get common denominator form first
    # This gives us numerator/denominator in a clean way
    together_expr = sp.together(expr)

    # If the result is a fraction (Mul with negative power), extract properly
    numer, denom = sp.fraction(together_expr)

    # If denominator is just 1, not a rational equation
    if denom == 1:
        return (expr, [])

    # Factor the denominator to find individual parts
    denom_factored = sp.factor(denom)

    # Collect unique denominator factors
    unique_denoms = []
    if denom_factored.is_Mul:
        for factor in denom_factored.args:
            # Skip pure numbers
            if factor.is_number:
                continue
            # Handle powers like (x-1)^2 -> just (x-1)
            if factor.is_Pow:
                base = factor.base
                if base.free_symbols and var in base.free_symbols:
                    if base not in unique_denoms:
                        unique_denoms.append(base)
            elif factor.free_symbols and var in factor.free_symbols:
                if factor not in unique_denoms:
                    unique_denoms.append(factor)
    else:
        # Single factor
        if denom_factored.is_Pow:
            base = denom_factored.base
            if base.free_symbols and var in base.free_symbols:
                unique_denoms.append(base)
        elif denom_factored.free_symbols and var in denom_factored.free_symbols:
            unique_denoms.append(denom_factored)

    # The numerator is already cleared - just expand it
    cleared = sp.expand(numer)

    return (cleared, unique_denoms)


def solve_rational_equation(expr, var: Symbol) -> Optional[List[Any]]:
    """
    Solve rational equation by clearing denominators.

    Steps:
    1. Clear denominators to get polynomial equation
    2. Solve the polynomial
    3. Filter out extraneous solutions (those making denominators zero)

    Args:
        expr: Rational equation expression (= 0)
        var: Variable to solve for

    Returns:
        List of valid solutions, or None if solving fails
    """
    # Import here to avoid circular dependency
    from .domain_solver import DomainPolynomialSolver

    # Clear denominators
    cleared_poly, denominators = clear_denominators(expr, var)

    if not denominators:
        # Not actually a rational equation
        return None

    # Solve the cleared polynomial
    success, solutions, method = DomainPolynomialSolver.try_domain_solve(cleared_poly, var)

    if not success or solutions is None:
        return None

    # Filter extraneous solutions
    valid_solutions = []
    for sol in solutions:
        is_valid = True
        for denom in denominators:
            # Check if this solution makes denominator zero
            denom_at_sol = denom.subs(var, sol)
            try:
                if sp.simplify(denom_at_sol) == 0:
                    is_valid = False
                    break
            except Exception:
                pass
        if is_valid:
            valid_solutions.append(sol)

    return valid_solutions if valid_solutions else None


def is_biquadratic(coeffs: List[Any]) -> bool:
    """
    Check if polynomial is biquadratic: ax⁴ + bx² + c = 0 (no x³ or x terms).

    Biquadratic form allows substitution u = x², reducing to quadratic.
    """
    if len(coeffs) != 5:  # degree 4 needs 5 coefficients
        return False
    # coeffs = [a₄, a₃, a₂, a₁, a₀]
    # Biquadratic means a₃ = 0 and a₁ = 0
    a3, a1 = coeffs[1], coeffs[3]
    try:
        a3_zero = (a3 == 0) or (hasattr(a3, 'is_zero') and a3.is_zero) or (abs(complex(a3)) < 1e-12)
        a1_zero = (a1 == 0) or (hasattr(a1, 'is_zero') and a1.is_zero) or (abs(complex(a1)) < 1e-12)
        return a3_zero and a1_zero
    except (TypeError, ValueError):
        return a3 == 0 and a1 == 0


def solve_biquadratic(a4: Any, a2: Any, a0: Any) -> Optional[List[Any]]:
    """
    Solve biquadratic equation: a₄x⁴ + a₂x² + a₀ = 0

    Substitution: u = x² transforms to a₄u² + a₂u + a₀ = 0
    Then x = ±√u for each u root.

    Args:
        a4: coefficient of x⁴
        a2: coefficient of x²
        a0: constant term

    Returns:
        List of solutions, or None if fails
    """
    # Import here to avoid circular dependency
    from .polynomial_solvers import solve_quadratic

    # Solve quadratic in u
    u_roots = solve_quadratic(a4, a2, a0)
    if u_roots is None:
        return None

    roots = []
    for u in u_roots:
        # x = ±√u
        sqrt_u = sp.sqrt(u)
        roots.append(sp.simplify(sqrt_u))
        roots.append(sp.simplify(-sqrt_u))

    return roots
