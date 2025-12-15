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
Polynomial Solvers - Degree-Specific Solving Methods
====================================================

This module contains degree-specific polynomial solving algorithms:
- Linear equations (degree 1)
- Quadratic formula (degree 2)
- Cardano's cubic formula (degree 3)
- Ferrari's quartic formula (degree 4)
- General polynomial solving by degree

These are domain-specific algorithms that don't require SymPy.
"""

from typing import Any, List, Optional
from math import gcd, isqrt

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, Integer, Rational, Float, Add, Mul, Pow
)


def extract_coefficients(expr, var: Symbol) -> Optional[List[Any]]:
    """
    Extract polynomial coefficients from a native expression.

    Returns list [a_n, a_{n-1}, ..., a_1, a_0] for a_n*x^n + ... + a_0
    Returns None if not a polynomial in the given variable.
    """
    try:
        # For native expressions, we need to manually extract coefficients
        # This is a simplified implementation for common polynomial forms
        if isinstance(expr, (int, float, Integer, Float, Rational)):
            return [expr]  # Constant polynomial

        if isinstance(expr, Symbol):
            if expr == var:
                return [Integer(1), Integer(0)]  # x = 1*x + 0
            else:
                return [expr]  # Different symbol, treat as constant

        # For more complex expressions, try to expand and collect terms
        # This is a basic implementation - full polynomial handling would need more work
        return None
    except Exception:
        return None


def solve_linear(a: Any, b: Any) -> Optional[List[Any]]:
    """
    Solve ax + b = 0 -> x = -b/a

    Args:
        a: coefficient of x
        b: constant term

    Returns:
        List with single solution, or None if a=0
    """
    from symbo_agentic_reasoners.core.number_theory_native import gcd as native_gcd

    # Handle native Integer/Float types
    a_val = a.value if hasattr(a, 'value') else a
    if a_val == 0:
        return None

    # Compute -b/a
    if isinstance(a, (Integer, Rational)) and isinstance(b, (Integer, Rational)):
        # Keep exact rational arithmetic
        if isinstance(a, Integer) and isinstance(b, Integer):
            a_num, b_num = a.value, b.value
            g = native_gcd(abs(b_num), abs(a_num))
            return [Rational(-b_num // g, a_num // g)]
        else:
            # Mixed types - use float division
            a_f = float(a.evalf()) if hasattr(a, 'evalf') else float(a)
            b_f = float(b.evalf()) if hasattr(b, 'evalf') else float(b)
            return [Float(-b_f / a_f)]
    else:
        return [-b / a]


def solve_quadratic(a: Any, b: Any, c: Any) -> Optional[List[Any]]:
    """
    Solve ax**2 + bx + c = 0 using the quadratic formula.

    x = (-b +/- sqrt(b**2 - 4ac)) / 2a

    Returns:
        List of solutions (may be symbolic with sqrt), or None if a=0
    """
    # Handle native Integer/Float types
    a_val = a.value if hasattr(a, 'value') else a
    if a_val == 0:
        # Not quadratic - delegate to linear
        return solve_linear(b, c)

    # Compute discriminant
    b_val = b.value if hasattr(b, 'value') else b
    c_val = c.value if hasattr(c, 'value') else c
    discriminant = b_val**2 - 4*a_val*c_val

    try:
        if discriminant == 0:
            # One repeated root
            root = -b_val / (2*a_val)
            if root == int(root):
                return [Integer(int(root))]
            return [Float(root)]

        if discriminant > 0:
            # Two real roots
            import math
            sqrt_disc = math.sqrt(discriminant)
            x1 = (-b_val + sqrt_disc) / (2*a_val)
            x2 = (-b_val - sqrt_disc) / (2*a_val)

            # Check if roots are integers
            results = []
            for x in [x1, x2]:
                if abs(x - round(x)) < 1e-10:
                    results.append(Integer(int(round(x))))
                else:
                    results.append(Float(x))
            return results
        else:
            # Complex roots - return as strings for now
            import math
            real_part = -b_val / (2*a_val)
            imag_part = math.sqrt(-discriminant) / (2*a_val)
            # Return symbolic representation
            return [f"{real_part} + {imag_part}*I", f"{real_part} - {imag_part}*I"]

    except Exception:
        return None


def solve_cubic(a: Any, b: Any, c: Any, d: Any) -> Optional[List[Any]]:
    """
    Solve ax**3 + bx**2 + cx + d = 0 using Cardano's formula.

    For depressed cubic t**3 + pt + q = 0:
    - Substitute x = t - b/(3a) to eliminate x**2 term
    - Then t = cbrt(-q/2 + sqrt(delta)) + cbrt(-q/2 - sqrt(delta))
    - Where delta = (q/2)**2 + (p/3)**3

    Returns:
        List of solutions, or None if a=0
    """
    import math

    a_val = a.value if hasattr(a, 'value') else a
    if a_val == 0:
        return solve_quadratic(b, c, d)

    try:
        # Extract numeric values
        b_val = b.value if hasattr(b, 'value') else b
        c_val = c.value if hasattr(c, 'value') else c
        d_val = d.value if hasattr(d, 'value') else d

        # Convert to depressed cubic: t**3 + pt + q = 0
        # Substitute x = t - b/(3a)
        p = (3*a_val*c_val - b_val**2) / (3*a_val**2)
        q = (2*b_val**3 - 9*a_val*b_val*c_val + 27*a_val**2*d_val) / (27*a_val**3)

        # Discriminant delta = (q/2)**2 + (p/3)**3
        discriminant = (q/2)**2 + (p/3)**3
        shift = -b_val / (3*a_val)

        # Cardano's formula
        if abs(discriminant) < 1e-12:
            # All roots are real, at least two are equal
            if abs(q) < 1e-12:
                # Triple root at 0 (before shift)
                root = shift
                if abs(root - round(root)) < 1e-10:
                    return [Integer(int(round(root)))]
                return [Float(root)]
            else:
                # One simple, one double root
                cbrt_val = (-q/2) ** (1/3) if q < 0 else -(q/2) ** (1/3)
                t1 = cbrt_val * 2
                t2 = -cbrt_val
                results = []
                for t in [t1, t2]:
                    x = t + shift
                    if abs(x - round(x)) < 1e-10:
                        results.append(Integer(int(round(x))))
                    else:
                        results.append(Float(x))
                return results

        if discriminant > 0:
            # One real root
            sqrt_disc = math.sqrt(discriminant)
            u_arg = -q/2 + sqrt_disc
            v_arg = -q/2 - sqrt_disc

            u = u_arg ** (1/3) if u_arg >= 0 else -((-u_arg) ** (1/3))
            v = v_arg ** (1/3) if v_arg >= 0 else -((-v_arg) ** (1/3))

            x1 = u + v + shift
            if abs(x1 - round(x1)) < 1e-10:
                return [Integer(int(round(x1)))]
            return [Float(x1)]
        else:
            # Three real roots (casus irreducibilis) - use trigonometric method
            r = math.sqrt(-p**3 / 27)
            theta = math.acos(-q / (2 * r))
            cbrt_r = r ** (1/3)

            results = []
            for k in range(3):
                t = 2 * cbrt_r * math.cos((theta + 2*math.pi*k) / 3)
                x = t + shift
                if abs(x - round(x)) < 1e-10:
                    results.append(Integer(int(round(x))))
                else:
                    results.append(Float(x))
            return results

    except Exception:
        return None


def solve_quartic(a: Any, b: Any, c: Any, d: Any, e: Any) -> Optional[List[Any]]:
    """
    Solve ax**4 + bx**3 + cx**2 + dx + e = 0 using Ferrari's method.

    Steps:
    1. Divide by a to get monic polynomial: x**4 + px**3 + qx**2 + rx + s = 0
    2. Substitute x = y - p/4 to get depressed quartic: y**4 + Py**2 + Qy + R = 0
    3. Solve resolvent cubic to find auxiliary value
    4. Reduce to two quadratics

    Returns:
        List of solutions, or None if a=0
    """
    import math

    a_val = a.value if hasattr(a, 'value') else a
    if a_val == 0:
        return solve_cubic(b, c, d, e)

    try:
        # Extract numeric values
        b_val = b.value if hasattr(b, 'value') else b
        c_val = c.value if hasattr(c, 'value') else c
        d_val = d.value if hasattr(d, 'value') else d
        e_val = e.value if hasattr(e, 'value') else e

        # Normalize to monic: x**4 + px**3 + qx**2 + rx + s = 0
        p = b_val / a_val
        q = c_val / a_val
        r = d_val / a_val
        s = e_val / a_val

        # Convert to depressed quartic y**4 + Py**2 + Qy + R = 0
        # where x = y - p/4
        P = q - 3*p**2/8
        Q = r - p*q/2 + p**3/8
        R = s - p*r/4 + p**2*q/16 - 3*p**4/256

        shift = -p/4

        # Use tolerance check for Q == 0
        Q_is_zero = abs(Q) < 1e-12
        if Q_is_zero:
            # Biquadratic: y**4 + Py**2 + R = 0
            # Let u = y**2, solve u**2 + Pu + R = 0
            u_roots = solve_quadratic(Integer(1), Float(P), Float(R))
            if u_roots is None:
                return None

            roots = []
            for u_root in u_roots:
                u_val = u_root.value if hasattr(u_root, 'value') else float(str(u_root).replace('*I', 'j').replace(' ', ''))
                if isinstance(u_val, complex) or u_val < 0:
                    continue  # Skip complex/negative u values
                # y = +/- sqrt(u)
                y1 = math.sqrt(u_val)
                y2 = -math.sqrt(u_val)
                for y in [y1, y2]:
                    x = y + shift
                    if abs(x - round(x)) < 1e-10:
                        roots.append(Integer(int(round(x))))
                    else:
                        roots.append(Float(x))
            return roots if roots else None

        # Resolvent cubic: 8m**3 + 8Pm**2 + (2P**2 - 8R)m - Q**2 = 0
        cubic_roots = solve_cubic(
            Integer(8), Float(8*P), Float(2*P**2 - 8*R), Float(-Q**2)
        )

        if cubic_roots is None or len(cubic_roots) == 0:
            return None

        # Take any real root (prefer real over complex)
        m = None
        for root in cubic_roots:
            r_val = root.value if hasattr(root, 'value') else root
            if isinstance(r_val, (int, float)) and not isinstance(r_val, complex):
                m = r_val
                break
        if m is None:
            m = cubic_roots[0].value if hasattr(cubic_roots[0], 'value') else cubic_roots[0]

        # Now factor using two quadratics
        val_2m_P = 2*m - P
        if val_2m_P <= 0:
            return None

        sqrt_2m_P = math.sqrt(val_2m_P)
        if abs(sqrt_2m_P) < 1e-12:
            return None

        half_Q_over_sqrt = Q / (2 * sqrt_2m_P)

        roots1 = solve_quadratic(
            Integer(1), Float(sqrt_2m_P), Float(m - half_Q_over_sqrt)
        )
        roots2 = solve_quadratic(
            Integer(1), Float(-sqrt_2m_P), Float(m + half_Q_over_sqrt)
        )

        all_roots = []
        for r in (roots1 or []):
            r_val = r.value if hasattr(r, 'value') else r
            if isinstance(r_val, (int, float)):
                x = r_val + shift
                if abs(x - round(x)) < 1e-10:
                    all_roots.append(Integer(int(round(x))))
                else:
                    all_roots.append(Float(x))
        for r in (roots2 or []):
            r_val = r.value if hasattr(r, 'value') else r
            if isinstance(r_val, (int, float)):
                x = r_val + shift
                if abs(x - round(x)) < 1e-10:
                    all_roots.append(Integer(int(round(x))))
                else:
                    all_roots.append(Float(x))

        return all_roots if all_roots else None

    except Exception:
        return None


def solve_polynomial_by_degree(expr, var: Symbol) -> Optional[List[Any]]:
    """
    Solve polynomial by degree, using the appropriate formula.

    - Degree 1: Linear formula
    - Degree 2: Quadratic formula
    - Degree 3: Cardano's cubic formula
    - Degree 4: Ferrari's quartic formula
    - Degree 5+: Try rational roots first, then numeric

    Args:
        expr: Native expression representing the polynomial
        var: Variable to solve for

    Returns:
        List of roots, or None if solving fails
    """
    from .rational_equations import find_rational_roots
    from .numeric_roots import find_all_numeric_roots

    coeffs = extract_coefficients(expr, var)
    if coeffs is None:
        return None

    degree = len(coeffs) - 1

    if degree == 1:
        return solve_linear(coeffs[0], coeffs[1])

    elif degree == 2:
        return solve_quadratic(coeffs[0], coeffs[1], coeffs[2])

    elif degree == 3:
        return solve_cubic(
            coeffs[0], coeffs[1], coeffs[2], coeffs[3]
        )

    elif degree == 4:
        return solve_quartic(
            coeffs[0], coeffs[1], coeffs[2], coeffs[3], coeffs[4]
        )

    else:
        # Degree 5+: No general formula exists (Abel-Ruffini theorem)
        # Try rational roots first
        try:
            int_coeffs = [int(c.value if hasattr(c, 'value') else c) for c in coeffs]
            rational_roots = find_rational_roots(int_coeffs)
            if rational_roots:
                return [Rational(r.p, r.q) if hasattr(r, 'p') else Integer(r) for r in rational_roots]
        except (TypeError, ValueError):
            pass

        # Fall back to numeric roots
        numeric_roots = find_all_numeric_roots(coeffs)
        if numeric_roots:
            return [Float(r) for r in numeric_roots]

        return None
