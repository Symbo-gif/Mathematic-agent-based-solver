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
Orchestration Native Fallback Engine
=====================================

Provides native computation fallbacks when no specialized agents are available.

NO SYMPY - All implementations use pure Python for mathematical reasoning.

Responsibilities:
- Domain-specific fallback routing (algebra, geometry, linalg, stats, discrete)
- Native equation solving (linear, quadratic)
- Geometry/trigonometry computations
- Linear algebra operations (determinant, eigenvalues, inverse, rank)
- Statistical calculations (mean, median, variance, std dev)
- Discrete math operations (factorial, combinations, permutations, primes)
"""

import logging
import re
import math
import ast
import copy
from fractions import Fraction
from typing import Optional

from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.native_fallback')


class NativeFallbackEngine:
    """
    Native computation fallback engine.

    Provides basic computational capabilities when no specialized
    agents are available. Uses pure Python implementations (NO SYMPY).

    All methods implement mathematical reasoning using:
    - Standard library: math, re, ast, copy, fractions
    - Native symbolic system: core.native_symbolic
    - Native calculus system: core.calculus

    Statistics:
        fallback_count: Number of times fallback was invoked
    """

    def __init__(self):
        """Initialize native fallback engine."""
        self.fallback_count = 0

    def compute_fallback(self, structured: StructuredProblem, operation: str) -> Optional[str]:
        """
        Direct native computation as fallback when no specialist available.

        NO SYMPY - Uses native_symbolic and native_calculus for pure mathematical reasoning.

        Args:
            structured: The structured problem to solve
            operation: Operation type (derivative, integral, solve, etc.)

        Returns:
            Result string or None if computation failed
        """
        try:
            from symbo_agentic_reasoners.core.native_symbolic import (
                parse_expr, sympify, symbols, diff as native_diff, simplify as native_simplify
            )
            from symbo_agentic_reasoners.core.calculus import (
                differentiate, integrate
            )

            self.fallback_count += 1

            raw_input = structured.raw_input.lower()
            domain = structured.domain.value.lower() if structured.domain else 'algebra'

            # Domain-specific fallbacks
            if domain in ['geometry', 'trigonometry']:
                return self._geometry_fallback(structured, raw_input)
            elif domain in ['linearalgebra', 'linear_algebra', 'linalg']:
                return self._linalg_fallback(structured, raw_input)
            elif domain in ['statistics', 'stats']:
                return self._stats_fallback(structured, raw_input)
            elif domain in ['discretemath', 'discrete_math', 'discrete']:
                return self._discrete_fallback(structured, raw_input)

            # Extract expression from raw input
            raw = structured.raw_input
            # Remove operation keywords from raw input
            for op_kw in ['diff', 'differentiate', 'derivative', 'integrate', 'integral',
                          'factor', 'expand', 'simplify', 'solve', 'compute']:
                raw = raw.replace(op_kw, '').strip()

            # Try to parse the expression using native parser
            try:
                expr = parse_expr(raw)
            except Exception:
                # If parsing fails, return None
                return None

            variable = structured.metadata.get('variable', 'x')

            if operation in ['derivative', 'diff', 'differentiate']:
                success, result, _ = differentiate(raw, variable)
                if success and result:
                    return result
                # Fallback to native_symbolic diff
                var_sym = symbols(variable)
                result = native_diff(expr, var_sym)
                return str(result) if result is not None else None

            elif operation in ['integral', 'integrate']:
                success, result, _ = integrate(raw, variable)
                if success and result:
                    return result
                return None

            elif operation in ['factor', 'expand', 'simplify']:
                # Use native simplify for these operations
                result = native_simplify(expr)
                return str(result) if result is not None else None

            elif operation == 'solve':
                # For solve, try to extract and solve equation
                # Native implementation: basic algebraic solving
                return self._native_solve(raw, variable)

            elif operation == 'compute':
                # Try to evaluate numeric expressions
                try:
                    result = native_simplify(expr)
                    result_str = str(result)
                    # Try to convert to number if possible
                    try:
                        val = result.evalf()
                        if isinstance(val, (int, float)):
                            if float(val) == int(float(val)):
                                return str(int(float(val)))
                            return str(val)
                    except Exception:
                        pass
                    return result_str
                except Exception:
                    return str(expr)
            else:
                result = native_simplify(expr)
                return str(result) if result is not None else None

        except Exception as e:
            logger.warning(f"Native fallback failed: {e}")
            return None

    def _native_solve(self, expr_str: str, var: str) -> Optional[str]:
        """
        Native algebraic equation solver without SymPy.

        Supports:
        - Linear equations: ax + b = 0
        - Quadratic equations: ax^2 + bx + c = 0 (real and complex roots)

        Args:
            expr_str: Expression string to solve
            var: Variable to solve for

        Returns:
            Solution string or None if unsolvable
        """
        # Try to parse as equation: expr = 0 or expr1 = expr2
        if '=' in expr_str:
            parts = expr_str.split('=')
            if len(parts) == 2:
                # Solve: left = right => left - right = 0
                expr_str = f"({parts[0].strip()}) - ({parts[1].strip()})"

        # Try linear equation: ax + b = 0 => x = -b/a
        linear_pattern = rf'(-?\d*\.?\d*)\s*\*?\s*{var}\s*([+-]\s*\d+\.?\d*)?'
        match = re.match(linear_pattern, expr_str.replace(' ', ''))
        if match:
            a_str = match.group(1) or '1'
            b_str = match.group(2) or '0'
            try:
                a = float(a_str) if a_str else 1.0
                b = float(b_str.replace(' ', '')) if b_str else 0.0
                if a != 0:
                    solution = -b / a
                    if solution == int(solution):
                        return str(int(solution))
                    return str(solution)
            except ValueError:
                pass

        # Try quadratic: ax^2 + bx + c = 0
        quad_pattern = rf'(-?\d*\.?\d*)\s*\*?\s*{var}\s*\*\*\s*2\s*([+-]\s*\d*\.?\d*\s*\*?\s*{var})?\s*([+-]\s*\d+\.?\d*)?'
        match = re.match(quad_pattern, expr_str.replace(' ', ''))
        if match:
            try:
                a = float(match.group(1) or '1')
                b_part = match.group(2) or '0'
                b = float(re.sub(rf'\*?{var}', '', b_part.replace(' ', ''))) if b_part and b_part.strip() else 0.0
                c = float(match.group(3).replace(' ', '') if match.group(3) else '0')

                if a != 0:
                    discriminant = b * b - 4 * a * c
                    if discriminant >= 0:
                        sqrt_disc = math.sqrt(discriminant)
                        x1 = (-b + sqrt_disc) / (2 * a)
                        x2 = (-b - sqrt_disc) / (2 * a)
                        if x1 == x2:
                            return f"[{x1}]"
                        return f"[{x1}, {x2}]"
                    else:
                        # Complex roots
                        real_part = -b / (2 * a)
                        imag_part = math.sqrt(-discriminant) / (2 * a)
                        return f"[{real_part} + {imag_part}*I, {real_part} - {imag_part}*I]"
            except (ValueError, ZeroDivisionError):
                pass

        return None

    def _geometry_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """
        Geometry/Trigonometry fallback using native math.

        NO SYMPY - Uses pure Python mathematical reasoning.

        Supports:
        - Trigonometric functions (sin, cos, tan) with degrees
        - Exact values for common angles (0°, 30°, 45°, 60°, 90°, etc.)
        - Area calculations (triangle, circle, rectangle, square)

        Args:
            structured: Problem structure
            raw_input: Lowercased raw input string

        Returns:
            Result string or None if computation failed
        """
        try:
            # Trigonometry with degrees
            if 'degree' in raw_input:
                # Extract angle value
                match = re.search(r'(\d+)\s*degree', raw_input)
                if match:
                    angle_deg = int(match.group(1))
                    angle_rad = math.pi * angle_deg / 180

                    # Common exact values lookup
                    exact_values = {
                        0: {'sin': '0', 'cos': '1', 'tan': '0'},
                        30: {'sin': '1/2', 'cos': 'sqrt(3)/2', 'tan': 'sqrt(3)/3'},
                        45: {'sin': 'sqrt(2)/2', 'cos': 'sqrt(2)/2', 'tan': '1'},
                        60: {'sin': 'sqrt(3)/2', 'cos': '1/2', 'tan': 'sqrt(3)'},
                        90: {'sin': '1', 'cos': '0', 'tan': 'undefined'},
                        120: {'sin': 'sqrt(3)/2', 'cos': '-1/2', 'tan': '-sqrt(3)'},
                        135: {'sin': 'sqrt(2)/2', 'cos': '-sqrt(2)/2', 'tan': '-1'},
                        150: {'sin': '1/2', 'cos': '-sqrt(3)/2', 'tan': '-sqrt(3)/3'},
                        180: {'sin': '0', 'cos': '-1', 'tan': '0'},
                    }

                    if angle_deg in exact_values:
                        if 'sin' in raw_input:
                            return exact_values[angle_deg]['sin']
                        elif 'cos' in raw_input:
                            return exact_values[angle_deg]['cos']
                        elif 'tan' in raw_input:
                            return exact_values[angle_deg]['tan']
                    else:
                        # Use numerical computation for other angles
                        if 'sin' in raw_input:
                            return str(math.sin(angle_rad))
                        elif 'cos' in raw_input:
                            return str(math.cos(angle_rad))
                        elif 'tan' in raw_input:
                            if abs(math.cos(angle_rad)) < 1e-10:
                                return 'undefined'
                            return str(math.tan(angle_rad))

            # Area calculations
            if 'area' in raw_input:
                if 'triangle' in raw_input:
                    # Extract base and height
                    base_match = re.search(r'base\s*[=:]?\s*(\d+(?:\.\d+)?)', raw_input)
                    height_match = re.search(r'height\s*[=:]?\s*(\d+(?:\.\d+)?)', raw_input)
                    if base_match and height_match:
                        base = float(base_match.group(1))
                        height = float(height_match.group(1))
                        return str(0.5 * base * height)
                elif 'circle' in raw_input:
                    radius_match = re.search(r'radius\s*[=:]?\s*(\d+(?:\.\d+)?)', raw_input)
                    if radius_match:
                        r = float(radius_match.group(1))
                        result = math.pi * r**2
                        return f"pi*{r**2}" if r**2 == int(r**2) else str(result)
                elif 'rectangle' in raw_input or 'square' in raw_input:
                    # Try to extract dimensions
                    nums = re.findall(r'(\d+(?:\.\d+)?)', raw_input)
                    if len(nums) >= 2:
                        return str(float(nums[0]) * float(nums[1]))
                    elif len(nums) == 1:
                        return str(float(nums[0]) ** 2)

            # Basic trig functions (without degrees) - use native simplify
            try:
                from symbo_agentic_reasoners.core.native_symbolic import parse_expr, simplify
                expr = parse_expr(structured.raw_input)
                return str(simplify(expr))
            except Exception:
                pass

            return None
        except Exception as e:
            logger.warning(f"Geometry fallback failed: {e}")
            return None

    def _linalg_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """
        Linear Algebra fallback using native matrix operations.

        NO SYMPY - Uses pure Python matrix reasoning.

        Supports:
        - Determinant (any size, Laplace expansion)
        - Eigenvalues (2x2 only, characteristic polynomial)
        - Inverse (2x2 only)
        - Transpose (any size)
        - Trace (any size)
        - Rank (any size, Gaussian elimination)

        Args:
            structured: Problem structure
            raw_input: Lowercased raw input string

        Returns:
            Result string or None if computation failed
        """
        try:
            # Extract matrix from input
            matrix_match = re.search(r'\[\[.*?\]\]', raw_input.replace(' ', ''))
            if matrix_match:
                try:
                    matrix_list = ast.literal_eval(matrix_match.group())

                    # Convert to list of lists if needed
                    if not isinstance(matrix_list[0], list):
                        matrix_list = [matrix_list]

                    n_rows = len(matrix_list)
                    n_cols = len(matrix_list[0]) if n_rows > 0 else 0

                    if 'determinant' in raw_input or 'det' in raw_input:
                        det = self._native_determinant(matrix_list)
                        return str(det)
                    elif 'eigenvalue' in raw_input:
                        # For 2x2 matrices only (native implementation)
                        eigenvals = self._native_eigenvalues_2x2(matrix_list)
                        return str(eigenvals) if eigenvals else None
                    elif 'inverse' in raw_input:
                        inv = self._native_inverse(matrix_list)
                        return str(inv) if inv else None
                    elif 'transpose' in raw_input:
                        transposed = [[matrix_list[j][i] for j in range(n_rows)] for i in range(n_cols)]
                        return str(transposed)
                    elif 'trace' in raw_input:
                        if n_rows == n_cols:
                            trace = sum(matrix_list[i][i] for i in range(n_rows))
                            return str(trace)
                    elif 'rank' in raw_input:
                        rank = self._native_matrix_rank(matrix_list)
                        return str(rank)
                    else:
                        return str(matrix_list)
                except Exception:
                    pass

            return None
        except Exception as e:
            logger.warning(f"Linear algebra fallback failed: {e}")
            return None

    def _native_determinant(self, matrix: list) -> Optional[float]:
        """
        Calculate determinant using native Python (Laplace expansion).

        Args:
            matrix: Square matrix as list of lists

        Returns:
            Determinant value or None if not square
        """
        n = len(matrix)
        if n == 0:
            return None
        if n != len(matrix[0]):
            return None  # Not square

        if n == 1:
            return matrix[0][0]
        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

        # Laplace expansion along first row
        det = 0
        for j in range(n):
            minor = [[matrix[i][k] for k in range(n) if k != j] for i in range(1, n)]
            cofactor = ((-1) ** j) * self._native_determinant(minor)
            det += matrix[0][j] * cofactor

        return det

    def _native_eigenvalues_2x2(self, matrix: list) -> Optional[list]:
        """
        Calculate eigenvalues for 2x2 matrix using characteristic polynomial.

        Solves: det(A - λI) = 0
        => λ^2 - (a+d)λ + (ad-bc) = 0

        Args:
            matrix: 2x2 matrix as [[a,b],[c,d]]

        Returns:
            List of eigenvalues (real or complex strings) or None if not 2x2
        """
        if len(matrix) != 2 or len(matrix[0]) != 2:
            return None

        a, b = matrix[0]
        c, d = matrix[1]

        # Characteristic polynomial: lambda^2 - (a+d)*lambda + (ad - bc) = 0
        trace = a + d
        det = a * d - b * c

        discriminant = trace * trace - 4 * det

        if discriminant >= 0:
            sqrt_disc = math.sqrt(discriminant)
            lambda1 = (trace + sqrt_disc) / 2
            lambda2 = (trace - sqrt_disc) / 2
            return [lambda1, lambda2]
        else:
            # Complex eigenvalues
            real = trace / 2
            imag = math.sqrt(-discriminant) / 2
            return [f"{real} + {imag}*I", f"{real} - {imag}*I"]

    def _native_inverse(self, matrix: list) -> Optional[list]:
        """
        Calculate inverse for 2x2 matrix (native implementation).

        Uses formula: A^(-1) = (1/det(A)) * [[d, -b], [-c, a]]

        Args:
            matrix: 2x2 matrix as [[a,b],[c,d]]

        Returns:
            Inverse matrix or None if singular or not 2x2
        """
        if len(matrix) != 2 or len(matrix[0]) != 2:
            return None

        a, b = matrix[0]
        c, d = matrix[1]

        det = a * d - b * c
        if det == 0:
            return None

        return [[d/det, -b/det], [-c/det, a/det]]

    def _native_matrix_rank(self, matrix: list) -> int:
        """
        Calculate rank using Gaussian elimination.

        Args:
            matrix: Matrix as list of lists

        Returns:
            Rank (number of linearly independent rows)
        """
        # Make a copy to avoid modifying original
        m = copy.deepcopy(matrix)
        n_rows = len(m)
        n_cols = len(m[0]) if n_rows > 0 else 0

        rank = 0
        for col in range(min(n_rows, n_cols)):
            # Find pivot
            pivot_row = None
            for row in range(rank, n_rows):
                if abs(m[row][col]) > 1e-10:
                    pivot_row = row
                    break

            if pivot_row is None:
                continue

            # Swap rows
            m[rank], m[pivot_row] = m[pivot_row], m[rank]

            # Eliminate
            for row in range(rank + 1, n_rows):
                if abs(m[rank][col]) > 1e-10:
                    factor = m[row][col] / m[rank][col]
                    for j in range(col, n_cols):
                        m[row][j] -= factor * m[rank][j]

            rank += 1

        return rank

    def _stats_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """
        Statistics fallback using native Python math.

        NO SYMPY - Uses pure Python for statistical calculations.

        Supports:
        - Mean/average
        - Median
        - Standard deviation
        - Variance
        - Sum, min, max

        Args:
            structured: Problem structure
            raw_input: Lowercased raw input string

        Returns:
            Result string or None if computation failed
        """
        try:
            # Extract list of numbers
            list_match = re.search(r'\[[\d\s,\.]+\]', raw_input)
            if list_match:
                try:
                    data = ast.literal_eval(list_match.group())

                    if 'mean' in raw_input or 'average' in raw_input:
                        result = sum(data) / len(data)
                        # Try to represent as fraction for exact results
                        if result == int(result):
                            return str(int(result))
                        try:
                            frac = Fraction(result).limit_denominator(1000)
                            if abs(float(frac) - result) < 1e-10:
                                return str(frac)
                        except Exception:
                            pass
                        return str(result)

                    elif 'median' in raw_input:
                        sorted_data = sorted(data)
                        n = len(sorted_data)
                        if n % 2 == 0:
                            return str((sorted_data[n//2 - 1] + sorted_data[n//2]) / 2)
                        else:
                            return str(sorted_data[n//2])

                    elif 'standard deviation' in raw_input or 'std' in raw_input:
                        mean = sum(data) / len(data)
                        variance = sum((x - mean)**2 for x in data) / len(data)
                        return str(math.sqrt(variance))

                    elif 'variance' in raw_input:
                        mean = sum(data) / len(data)
                        variance = sum((x - mean)**2 for x in data) / len(data)
                        return str(variance)

                    elif 'sum' in raw_input:
                        return str(sum(data))

                    elif 'min' in raw_input:
                        return str(min(data))

                    elif 'max' in raw_input:
                        return str(max(data))

                except Exception:
                    pass

            return None
        except Exception as e:
            logger.warning(f"Statistics fallback failed: {e}")
            return None

    def _discrete_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """
        Discrete Math fallback using native Python math.

        NO SYMPY - Uses pure Python for combinatorics and number theory.

        Supports:
        - Factorial
        - Combinations (n choose k)
        - Permutations (n permute k)
        - GCD, LCM
        - Primality testing

        Args:
            structured: Problem structure
            raw_input: Lowercased raw input string

        Returns:
            Result string or None if computation failed
        """
        try:
            # Factorial
            if 'factorial' in raw_input or '!' in raw_input:
                match = re.search(r'(\d+)\s*(?:factorial|!)', raw_input)
                if match:
                    n = int(match.group(1))
                    return str(math.factorial(n))

            # Combinations (n choose k) - binomial coefficient
            if 'choose' in raw_input or 'combination' in raw_input or 'C(' in raw_input:
                match = re.search(r'(\d+)\s*choose\s*(\d+)', raw_input)
                if match:
                    n, k = int(match.group(1)), int(match.group(2))
                    return str(math.comb(n, k))
                # Try C(n,k) format
                match = re.search(r'C\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', raw_input)
                if match:
                    n, k = int(match.group(1)), int(match.group(2))
                    return str(math.comb(n, k))

            # Permutations
            if 'permutation' in raw_input or 'P(' in raw_input:
                match = re.search(r'P\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', raw_input)
                if match:
                    n, k = int(match.group(1)), int(match.group(2))
                    return str(math.perm(n, k))

            # GCD/LCM
            if 'gcd' in raw_input:
                nums = re.findall(r'\d+', raw_input)
                if len(nums) >= 2:
                    return str(math.gcd(int(nums[0]), int(nums[1])))

            if 'lcm' in raw_input:
                nums = re.findall(r'\d+', raw_input)
                if len(nums) >= 2:
                    return str(math.lcm(int(nums[0]), int(nums[1])))

            # Prime check
            if 'prime' in raw_input:
                match = re.search(r'(\d+)', raw_input)
                if match:
                    n = int(match.group(1))
                    return str(self._is_prime(n))

            return None
        except Exception as e:
            logger.warning(f"Discrete math fallback failed: {e}")
            return None

    def _is_prime(self, n: int) -> bool:
        """
        Check if n is prime using native Python.

        Uses trial division up to sqrt(n).

        Args:
            n: Number to test

        Returns:
            True if n is prime, False otherwise
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
