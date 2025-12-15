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
Series Specialist - Infinite Series Evaluation
===============================================

Evaluates infinite series and recognizes classic forms WITHOUT SymPy.

Recognizes:
- sum(1/n^2, n=1..inf) = pi^2/6 (Basel problem)
- sum(1/n^4, n=1..inf) = pi^4/90
- sum(1/n^6, n=1..inf) = pi^6/945
- sum((-1)^(n+1)/n, n=1..inf) = ln(2) (alternating harmonic)
- sum(1/n!, n=0..inf) = e
- sum((-1)^n/n!, n=0..inf) = 1/e
- sum(1/(2n+1)^2, n=0..inf) = pi^2/8
- sum((-1)^n/(2n+1), n=0..inf) = pi/4 (Leibniz formula)
- sum(r^n, n=0..inf) = 1/(1-r) for |r|<1 (geometric)
- sum(λ^n/n!, n=0..inf) = exp(λ) (exponential)

Uses native limit evaluation and pattern matching for pure mathematical reasoning.
"""

import re
import math
import logging
from typing import Union, Optional, Tuple
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func
from .expression_parser import ExprParser
from .calculus_utils import _evaluate_at_numeric
from .limit_specialist import native_limit

logger = logging.getLogger(__name__)

# Global parser instance
_parser = ExprParser()


def series_sum(expr_str: str, var: str = 'n', start: int = 1, end: Union[int, str] = 'inf') -> Tuple[bool, Optional[str], str]:
    """
    Evaluate infinite series and recognize classic forms.

    Recognizes:
    - sum(1/n^2, n=1..inf) = pi^2/6 (Basel problem)
    - sum(1/n^4, n=1..inf) = pi^4/90
    - sum(1/n^6, n=1..inf) = pi^6/945
    - sum((-1)^(n+1)/n, n=1..inf) = ln(2) (alternating harmonic)
    - sum(1/n!, n=0..inf) = e
    - sum((-1)^n/n!, n=0..inf) = 1/e
    - sum(1/(2n+1)^2, n=0..inf) = pi^2/8
    - sum((-1)^n/(2n+1), n=0..inf) = pi/4 (Leibniz formula)
    - sum(r^n, n=0..inf) = 1/(1-r) for |r|<1 (geometric)
    - sum(λ^n/n!, n=0..inf) = exp(λ) (exponential)

    Args:
        expr_str: The summand expression as a string (e.g., "1/n**2")
        var: The summation variable (default 'n')
        start: Starting index (default 1)
        end: Ending index, 'inf' for infinite series (default 'inf')

    Returns:
        Tuple of (success, result_string, method)
    """
    expr_str = expr_str.strip()
    is_infinite = (end == 'inf' or end == float('inf'))

    if not is_infinite:
        # For finite sums, we could compute numerically
        # For now, only handle infinite series
        return (False, None, 'series_not_supported')

    # Normalize the expression
    normalized = re.sub(r'\s+', '', expr_str)

    # ==========================================================================
    # STEP 1: n-th term divergence test (if lim a_n != 0, series diverges)
    # ==========================================================================
    div_reason = _check_nth_term_divergence_native(expr_str, var)
    if div_reason is not None:
        return (True, f"divergent ({div_reason})", "nth_term_test")

    # ==========================================================================
    # STEP 2: Geometric series recognition: r^n → 1/(1-r) for |r|<1
    # ==========================================================================
    geo_result = _try_geometric_series(expr_str, var, start)
    if geo_result is not None:
        return (True, geo_result[0], geo_result[1])

    # ==========================================================================
    # STEP 3: Exponential series: λ^n/n! → exp(λ)
    # ==========================================================================
    exp_result = _try_exp_series(expr_str, var, start)
    if exp_result is not None:
        return (True, exp_result[0], exp_result[1])

    # Classic series patterns
    # Basel problem: sum(1/n^2) = pi^2/6
    if start == 1:
        # 1/n^2 - multiple patterns to match various input forms
        basel_patterns = [
            rf'^1/{var}\*\*2$',           # 1/n**2
            rf'^{var}\*\*-2$',             # n**-2
            rf'^{var}\*\*\(-2\)$',         # n**(-2)
            rf'^1/\({var}\*\*2\)$',        # 1/(n**2)
        ]
        for pattern in basel_patterns:
            if re.match(pattern, normalized):
                return (True, "pi**2/6", "basel_problem")

        # 1/n^4
        zeta4_patterns = [
            rf'^1/{var}\*\*4$',
            rf'^{var}\*\*-4$',
            rf'^{var}\*\*\(-4\)$',
            rf'^1/\({var}\*\*4\)$',
        ]
        for pattern in zeta4_patterns:
            if re.match(pattern, normalized):
                return (True, "pi**4/90", "zeta_4")

        # 1/n^6
        zeta6_patterns = [
            rf'^1/{var}\*\*6$',
            rf'^{var}\*\*-6$',
            rf'^{var}\*\*\(-6\)$',
            rf'^1/\({var}\*\*6\)$',
        ]
        for pattern in zeta6_patterns:
            if re.match(pattern, normalized):
                return (True, "pi**6/945", "zeta_6")

        # 1/n^8
        zeta8_patterns = [
            rf'^1/{var}\*\*8$',
            rf'^{var}\*\*-8$',
            rf'^{var}\*\*\(-8\)$',
            rf'^1/\({var}\*\*8\)$',
        ]
        for pattern in zeta8_patterns:
            if re.match(pattern, normalized):
                return (True, "pi**8/9450", "zeta_8")

        # Alternating harmonic: (-1)^(n+1)/n = ln(2)
        alt_harm_patterns = [
            rf'^\(-1\)\*\*\({var}\+1\)/{var}$',
            rf'^\(-1\)\*\*\({var}\+1\)\*{var}\*\*-1$',
        ]
        for pattern in alt_harm_patterns:
            if re.match(pattern, normalized):
                return (True, "log(2)", "alternating_harmonic")

    # Starting from 0
    if start == 0:
        # 1/n! = e
        factorial_patterns = [
            rf'^1/factorial\({var}\)$',
            rf'^1/{var}!$',
            rf'^factorial\({var}\)\*\*-1$',
        ]
        for pattern in factorial_patterns:
            if re.match(pattern, normalized):
                return (True, "E", "taylor_e")

        # x^n/n! = e^x (exponential series)
        exp_series_patterns = [
            rf'^x\*\*{var}/factorial\({var}\)$',
            rf'^x\*\*{var}/{var}!$',
            rf'^\(x\)\*\*{var}/factorial\({var}\)$',
        ]
        for pattern in exp_series_patterns:
            if re.match(pattern, normalized):
                return (True, "exp(x)", "taylor_exp")

        # (-x)^n/n! = e^(-x)
        neg_exp_series_patterns = [
            rf'^\(-x\)\*\*{var}/factorial\({var}\)$',
            rf'^\(-x\)\*\*{var}/{var}!$',
            rf'^\(-1\)\*\*{var}\*x\*\*{var}/factorial\({var}\)$',
        ]
        for pattern in neg_exp_series_patterns:
            if re.match(pattern, normalized):
                return (True, "exp(-x)", "taylor_exp_neg")

        # (-1)^n/n! = 1/e
        alt_factorial_patterns = [
            rf'^\(-1\)\*\*{var}/factorial\({var}\)$',
            rf'^\(-1\)\*\*{var}/{var}!$',
        ]
        for pattern in alt_factorial_patterns:
            if re.match(pattern, normalized):
                return (True, "1/E", "taylor_inv_e")

        # x^n/n = -log(1-x) (log series, for |x| < 1)
        log_series_patterns = [
            rf'^x\*\*{var}/{var}$',
        ]
        for pattern in log_series_patterns:
            if re.match(pattern, normalized):
                return (True, "-log(1-x) for |x|<1", "taylor_log")

        # (-1)^(n+1)*x^n/n = log(1+x) (log series, for |x| < 1)
        alt_log_series_patterns = [
            rf'^\(-1\)\*\*\({var}\+1\)\*x\*\*{var}/{var}$',
        ]
        for pattern in alt_log_series_patterns:
            if re.match(pattern, normalized):
                return (True, "log(1+x) for |x|<1", "taylor_log_alt")

        # 1/(2n+1)^2 = pi^2/8
        odd_sq_patterns = [
            rf'^1/\(2\*{var}\+1\)\*\*2$',
            rf'^\(2\*{var}\+1\)\*\*-2$',
        ]
        for pattern in odd_sq_patterns:
            if re.match(pattern, normalized):
                return (True, "pi**2/8", "odd_squares")

        # (-1)^n/(2n+1) = pi/4 (Leibniz)
        leibniz_patterns = [
            rf'^\(-1\)\*\*{var}/\(2\*{var}\+1\)$',
            rf'^\(-1\)\*\*{var}\*\(2\*{var}\+1\)\*\*-1$',
        ]
        for pattern in leibniz_patterns:
            if re.match(pattern, normalized):
                return (True, "pi/4", "leibniz")

    # Try AST-based pattern matching for more complex forms
    try:
        expr = _parser.parse(expr_str)
        if expr is not None:
            # Check for 1/n^p pattern using AST
            if isinstance(expr, Pow):
                if isinstance(expr.base, Sym) and expr.base.name == var:
                    if isinstance(expr.exp, Num) and expr.exp.value < 0:
                        p = -expr.exp.value
                        if start == 1 and p == 2:
                            return (True, "pi**2/6", "basel_problem_ast")
                        elif start == 1 and p == 4:
                            return (True, "pi**4/90", "zeta_4_ast")
                        elif start == 1 and p == 6:
                            return (True, "pi**6/945", "zeta_6_ast")
                        elif start == 1 and p == 8:
                            return (True, "pi**8/9450", "zeta_8_ast")

            # Check for 1/var^p pattern (Mul with Pow)
            if isinstance(expr, Mul):
                for f in expr.factors:
                    if isinstance(f, Pow) and isinstance(f.exp, Num):
                        if isinstance(f.base, Sym) and f.base.name == var:
                            p = f.exp.value
                            if p < 0 and start == 1:
                                p_val = int(-p)
                                zeta_values = {2: "pi**2/6", 4: "pi**4/90", 6: "pi**6/945", 8: "pi**8/9450"}
                                if p_val in zeta_values:
                                    return (True, zeta_values[p_val], f"zeta_{p_val}_mul")

    except Exception:
        pass

    # For unrecognized series, return a symbolic SeriesSum object instead of error
    # This allows the system to gracefully handle unknown series without SymPy
    symbolic_form = f"SeriesSum({expr_str}, ({var}, {start}, {end}))"
    return (True, symbolic_form, 'series_symbolic')


def _check_nth_term_divergence(expr_str: str, var: str) -> Optional[str]:
    """
    Divergence test (n-th term test): If lim_{n->inf} a_n != 0, series diverges.

    This is a quick pre-check that catches obvious divergence cases.

    Returns:
        Divergence reason if test indicates divergence, None otherwise
    """
    normalized = expr_str.replace(' ', '')

    # Patterns where the term clearly doesn't go to 0
    divergence_patterns = [
        # Constants: sum(c) diverges for c != 0
        (rf'^-?\d+(?:\.\d+)?$', 'constant terms do not tend to 0'),
        # n / something small: n/log(n), n/sqrt(n)
        (rf'^{var}/(?:log|ln)\({var}\)$', 'n/log(n) -> infinity as n -> infinity'),
        # Polynomial growth: n, n^2, n^k
        (rf'^{var}(?:\*\*\d+)?$', 'polynomial terms grow without bound'),
        # Exponential growth: 2^n, e^n
        (rf'^\d+\*\*{var}$', 'exponential terms grow without bound'),
        # Factorial growth
        (rf'^factorial\({var}\)$', 'factorial terms grow without bound'),
        (rf'^{var}!$', 'factorial terms grow without bound'),
        # sin/cos of constant (not 0): sum(sin(1))
        (r'^(?:sin|cos)\(\d+(?:\.\d+)?\)$', 'constant oscillating terms do not tend to 0'),
    ]

    for pattern, reason in divergence_patterns:
        if re.match(pattern, normalized, re.IGNORECASE):
            return reason

    # Check for ratio that doesn't decay
    # n^k / n^m where k >= m
    power_ratio_pattern = rf'^{var}\*\*(\d+)/{var}\*\*(\d+)$'
    match = re.match(power_ratio_pattern, normalized)
    if match:
        k, m = int(match.group(1)), int(match.group(2))
        if k >= m:
            return f'n^{k}/n^{m} = n^{k-m} does not tend to 0'

    return None


def _check_nth_term_divergence_native(expr_str: str, var: str) -> Optional[str]:
    """
    Improved n-th term divergence test using native limit evaluation.

    NO SYMPY - Uses native_limit for pure mathematical reasoning.

    If lim_{n to infinity} a_n != 0, the series diverges.

    Returns:
        Divergence reason if limit != 0, None if limit = 0 (or inconclusive)
    """
    try:
        # Use native limit evaluation
        success, limit_val, method = native_limit(expr_str, var, 'inf')

        if success and limit_val is not None:
            limit_str = str(limit_val).lower().strip()

            # Check for non-zero limit
            if limit_str not in ('0', '0.0', 'none'):
                # Check for infinity
                if 'inf' in limit_str or 'oo' in limit_str:
                    return f"lim a_n = {limit_val} (terms grow without bound)"

                # Check for finite non-zero
                try:
                    limit_num = float(limit_val)
                    if abs(limit_num) > 1e-10:
                        return f"lim a_n = {limit_val} != 0 (n-th term test)"
                except ValueError:
                    # Symbolic non-zero result
                    if limit_str not in ('0', '0.0', 'none', 'dne'):
                        return f"lim a_n = {limit_val} != 0 (n-th term test)"

        # Try numerical evaluation at large n for cases native_limit doesn't handle
        try:
            ast = _parser.parse(expr_str)
            if ast is not None:
                val_1000 = _evaluate_at_numeric(ast, var, 1000)
                val_10000 = _evaluate_at_numeric(ast, var, 10000)
                val_100000 = _evaluate_at_numeric(ast, var, 100000)

                # If values are approaching a non-zero constant
                if abs(val_1000) > 0.01 and abs(val_10000) > 0.01 and abs(val_100000) > 0.01:
                    if abs(val_10000 - val_1000) < 0.1 and abs(val_100000 - val_10000) < 0.01:
                        approx_limit = val_100000
                        return f"lim a_n ~ {approx_limit:.4f} != 0 (n-th term test, numerical)"
        except Exception:
            pass

    except Exception:
        pass

    # Also run the pattern-based test as fallback
    return _check_nth_term_divergence(expr_str, var)


def _try_geometric_series(expr_str: str, var: str, start: int) -> Optional[Tuple[str, str]]:
    """
    Recognize geometric series: sum(r^n) or sum(a*r^n).

    For |r| < 1:
    - sum(r^n, n=0..inf) = 1/(1-r)
    - sum(r^n, n=1..inf) = r/(1-r)
    - sum(a*r^n, n=0..inf) = a/(1-r)

    Returns:
        (result_string, method) or None
    """
    normalized = expr_str.replace(' ', '')

    # Pattern 1: (fraction)^n like (1/2)**n
    frac_pattern = rf'^\((\d+)/(\d+)\)\*\*{var}$'
    match = re.match(frac_pattern, normalized)
    if match:
        num, den = int(match.group(1)), int(match.group(2))
        r = num / den
        if abs(r) < 1:
            if start == 0:
                result = 1 / (1 - r)
                return (str(result), "geometric_series")
            elif start == 1:
                result = r / (1 - r)
                return (str(result), "geometric_series")

    # Pattern 2: decimal^n like 0.5**n
    decimal_pattern = rf'^(\d*\.\d+)\*\*{var}$'
    match = re.match(decimal_pattern, normalized)
    if match:
        r = float(match.group(1))
        if abs(r) < 1:
            if start == 0:
                result = 1 / (1 - r)
                return (str(result), "geometric_series")
            elif start == 1:
                result = r / (1 - r)
                return (str(result), "geometric_series")

    # Pattern 3: Use native AST evaluation for more complex detection
    # NO SYMPY - Uses native evaluation for pure mathematical reasoning
    try:
        ast = _parser.parse(expr_str)
        if ast is not None:
            # Check if expression is of form a * r^n
            # Try to extract base by dividing consecutive terms
            a1 = _evaluate_at_numeric(ast, var, 0)
            a2 = _evaluate_at_numeric(ast, var, 1)
            if a1 != 0 and abs(a1) < 1e10 and abs(a2) < 1e10:
                r_val = a2 / a1
                # Verify it's geometric by checking a_3 / a_2
                a3 = _evaluate_at_numeric(ast, var, 2)
                if abs(a2) > 1e-10 and abs(a3 / a2 - r_val) < 1e-8:
                    # Confirmed geometric
                    if abs(r_val) < 1:
                        if start == 0:
                            result = a1 / (1 - r_val)
                            return (str(result), "geometric_series_native")
                        elif start == 1:
                            # sum from 1 to inf = (total from 0) - a_0
                            total = a1 / (1 - r_val)
                            result = total - a1
                            return (str(result), "geometric_series_native")

    except Exception:
        pass

    return None


def _try_exp_series(expr_str: str, var: str, start: int) -> Optional[Tuple[str, str]]:
    """
    Recognize exponential series: sum(λ^n/n!) = exp(λ).

    Patterns:
    - λ**n/factorial(n) → exp(λ)
    - λ**n/n! → exp(λ)
    - x**n/factorial(n) → exp(x)

    Returns:
        (result_string, method) or None
    """
    # Must start from 0 for standard exp series
    if start != 0:
        return None

    normalized = expr_str.replace(' ', '')

    # Pattern 1: number**n/factorial(n) - e.g., 5**n/factorial(n)
    num_exp_pattern = rf'^(\d+(?:\.\d+)?)\*\*{var}/factorial\({var}\)$'
    match = re.match(num_exp_pattern, normalized)
    if match:
        lam = float(match.group(1))
        return (f"exp({lam})", "exp_series")

    # Pattern 2: (number)**n/factorial(n) with parens
    num_exp_pattern2 = rf'^\((\d+(?:\.\d+)?)\)\*\*{var}/factorial\({var}\)$'
    match = re.match(num_exp_pattern2, normalized)
    if match:
        lam = float(match.group(1))
        return (f"exp({lam})", "exp_series")

    # Pattern 3: Use native evaluation for more robust detection
    # NO SYMPY - Uses native numerical evaluation for ratio test
    try:
        ast = _parser.parse(expr_str)
        if ast is not None:
            # For exp series λ^n/n!, the ratio a_{n+1}/a_n = λ/(n+1)
            # So a_{n+1}/a_n * (n+1) should be constant = λ
            ratios_times_n1 = []
            for n_val in [1, 2, 3, 4, 5]:
                try:
                    a_n = _evaluate_at_numeric(ast, var, n_val)
                    a_n1 = _evaluate_at_numeric(ast, var, n_val + 1)
                    if abs(a_n) > 1e-15:
                        ratio = a_n1 / a_n
                        lambda_candidate = ratio * (n_val + 1)
                        ratios_times_n1.append(lambda_candidate)
                except Exception:
                    pass

            # If all ratios_times_n1 are approximately equal, we found λ
            if len(ratios_times_n1) >= 3:
                avg_lambda = sum(ratios_times_n1) / len(ratios_times_n1)
                variance = sum((x - avg_lambda)**2 for x in ratios_times_n1) / len(ratios_times_n1)
                if variance < 0.01:  # Ratios are consistent
                    # This is exp(λ)
                    if abs(avg_lambda - round(avg_lambda)) < 1e-6:
                        lam = int(round(avg_lambda))
                    else:
                        lam = avg_lambda
                    return (f"exp({lam})", "exp_series_ratio_native")

    except Exception:
        pass

    return None


__all__ = [
    'series_sum',
]
