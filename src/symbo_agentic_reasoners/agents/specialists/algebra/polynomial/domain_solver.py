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
Domain Polynomial Solver - Routing Class
========================================

This module contains the DomainPolynomialSolver class that routes
polynomial operations to the appropriate sub-specialists.

This implements the "SymPy Last Resort" architecture:
1. Try domain-specific algorithms FIRST
2. Only fall back to SymPy when domain algorithms can't handle the case
3. Track all fallbacks for optimization analysis
"""

from typing import Any, List, Optional, Tuple

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import Symbol, Float
import symbo_agentic_reasoners.core.native_symbolic as sp

# Import all sub-specialist modules
from .polynomial_solvers import (
    extract_coefficients,
    solve_linear,
    solve_quadratic,
    solve_cubic,
    solve_quartic,
    solve_polynomial_by_degree
)

from .polynomial_factors import (
    factor_difference_of_squares,
    factor_difference_of_cubes,
    factor_sum_of_cubes,
    factor_gcd
)

from .numeric_roots import (
    newton_raphson,
    find_all_numeric_roots
)

from .rational_equations import (
    find_rational_roots,
    is_rational_equation,
    clear_denominators,
    solve_rational_equation,
    is_biquadratic,
    solve_biquadratic
)


class DomainPolynomialSolver:
    """
    Domain-specific polynomial algorithms that don't require SymPy.

    This class implements classical polynomial algorithms:
    - Quadratic formula
    - Rational root theorem
    - Pattern-based factoring (difference of squares, cubes, etc.)
    - GCD coefficient extraction

    These are tried FIRST. NO SYMPY is used.
    """

    # =========================================================================
    # STATIC METHODS - Re-export from sub-specialists
    # =========================================================================

    # Coefficient extraction
    extract_coefficients = staticmethod(extract_coefficients)

    # Degree-specific solving
    solve_linear = staticmethod(solve_linear)
    solve_quadratic = staticmethod(solve_quadratic)
    solve_cubic = staticmethod(solve_cubic)
    solve_quartic = staticmethod(solve_quartic)
    solve_polynomial_by_degree = staticmethod(solve_polynomial_by_degree)

    # Numeric root finding
    newton_raphson = staticmethod(newton_raphson)
    find_all_numeric_roots = staticmethod(find_all_numeric_roots)

    # Rational roots
    find_rational_roots = staticmethod(find_rational_roots)

    # Factoring
    factor_difference_of_squares = staticmethod(factor_difference_of_squares)
    factor_difference_of_cubes = staticmethod(factor_difference_of_cubes)
    factor_sum_of_cubes = staticmethod(factor_sum_of_cubes)
    factor_gcd = staticmethod(factor_gcd)

    # Rational equations
    is_rational_equation = staticmethod(is_rational_equation)
    clear_denominators = staticmethod(clear_denominators)
    solve_rational_equation = staticmethod(solve_rational_equation)

    # Biquadratic
    is_biquadratic = staticmethod(is_biquadratic)
    solve_biquadratic = staticmethod(solve_biquadratic)

    # =========================================================================
    # ROUTING METHODS
    # =========================================================================

    @classmethod
    def try_domain_solve(cls, expr, var: Symbol) -> Tuple[bool, Optional[List[Any]], str]:
        """
        Attempt to solve polynomial using domain algorithms.

        Args:
            expr: SymPy expression (polynomial = 0)
            var: Variable to solve for

        Returns:
            Tuple of (success: bool, solutions: Optional[List], method: str)
            - success: True if domain algorithm succeeded
            - solutions: List of solutions, or None if failed
            - method: Name of method used (for logging)
        """
        # CHECK FOR RATIONAL EQUATION FIRST
        # Rational equations like 2/x + 3/(x-1) = 5 need special handling
        if cls.is_rational_equation(expr):
            result = cls.solve_rational_equation(expr, var)
            if result is not None:
                return (True, result, "rational_equation_clearing")

        coeffs = cls.extract_coefficients(expr, var)

        if coeffs is None:
            return (False, None, "not_polynomial")

        degree = len(coeffs) - 1

        # Try based on degree
        if degree == 1:
            # Linear: ax + b = 0
            result = cls.solve_linear(coeffs[0], coeffs[1])
            if result is not None:
                return (True, result, "linear_formula")

        elif degree == 2:
            # Quadratic: ax² + bx + c = 0
            result = cls.solve_quadratic(coeffs[0], coeffs[1], coeffs[2])
            if result is not None:
                return (True, result, "quadratic_formula")

        elif degree == 3:
            # First try rational roots (faster for integer coefficients)
            try:
                int_coeffs = [int(c) for c in coeffs if c.is_number]
                if len(int_coeffs) == len(coeffs):
                    roots = cls.find_rational_roots(int_coeffs)
                    if roots and len(roots) == degree:
                        return (True, [r for r in roots], "rational_root_theorem")
            except Exception:
                pass

            # Fall back to Cardano's cubic formula
            result = cls.solve_cubic(coeffs[0], coeffs[1], coeffs[2], coeffs[3])
            if result is not None:
                return (True, result, "cardano_cubic")

        elif degree == 4:
            # First try rational roots (faster for integer coefficients)
            try:
                int_coeffs = [int(c) for c in coeffs if c.is_number]
                if len(int_coeffs) == len(coeffs):
                    roots = cls.find_rational_roots(int_coeffs)
                    if roots and len(roots) == degree:
                        return (True, [r for r in roots], "rational_root_theorem")
            except Exception:
                pass

            # Check for biquadratic: x⁴ + ax² + b = 0 (no x³ or x terms)
            if cls.is_biquadratic(coeffs):
                # coeffs = [a₄, a₃, a₂, a₁, a₀] with a₃ = a₁ = 0
                result = cls.solve_biquadratic(coeffs[0], coeffs[2], coeffs[4])
                if result is not None:
                    return (True, result, "biquadratic_substitution")

            # Fall back to Ferrari's quartic formula
            result = cls.solve_quartic(
                coeffs[0], coeffs[1], coeffs[2], coeffs[3], coeffs[4]
            )
            if result is not None:
                return (True, result, "ferrari_quartic")

        else:
            # Degree 5+: No general formula exists (Abel-Ruffini theorem)
            # Try rational roots first
            try:
                int_coeffs = [int(c) for c in coeffs if c.is_number]
                if len(int_coeffs) == len(coeffs):
                    roots = cls.find_rational_roots(int_coeffs)
                    if roots:
                        return (True, [r for r in roots], "rational_root_theorem")
            except Exception:
                pass

            # Fall back to Newton-Raphson numeric roots
            numeric_roots = cls.find_all_numeric_roots(coeffs)
            if numeric_roots:
                return (True, [Float(r) for r in numeric_roots], "newton_raphson")

        # No domain algorithm succeeded
        return (False, None, "no_match")

    @classmethod
    def try_domain_factor(cls, expr) -> Tuple[bool, Optional[Any], str]:
        """
        Attempt to factor polynomial using domain algorithms.

        Args:
            expr: SymPy expression to factor

        Returns:
            Tuple of (success: bool, factored: Optional, method: str)
        """
        # Try difference of squares
        result = cls.factor_difference_of_squares(expr)
        if result is not None:
            return (True, result, "difference_of_squares")

        # Try difference of cubes
        result = cls.factor_difference_of_cubes(expr)
        if result is not None:
            return (True, result, "difference_of_cubes")

        # Try sum of cubes
        result = cls.factor_sum_of_cubes(expr)
        if result is not None:
            return (True, result, "sum_of_cubes")

        # Try GCD factoring
        result = cls.factor_gcd(expr)
        if result is not None:
            gcd_factor, remaining = result
            return (True, gcd_factor * remaining, "gcd_factoring")

        return (False, None, "no_match")
