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
Expression Validation
=====================

Safety checks for symbolic expressions to prevent DoS attacks.
NO SYMPY DEPENDENCY - Pure Python implementation.
"""

import logging
from typing import Tuple

logger = logging.getLogger('symbo_agentic_reasoners.symbolic.validation')

# Safety limits
MAX_EXPRESSION_DEPTH = 100
MAX_EXPRESSION_LENGTH = 50000
MAX_TERM_COUNT = 1000


def check_expression_depth(expr, max_depth: int = MAX_EXPRESSION_DEPTH) -> Tuple[bool, str]:
    """
    Check if expression tree depth exceeds limit.

    Args:
        expr: Expression to check
        max_depth: Maximum allowed depth

    Returns:
        (is_safe, error_message)
    """
    def get_depth(e, current_depth=0):
        """Recursively compute expression tree depth."""
        if current_depth > max_depth:
            return current_depth
        if hasattr(e, 'args'):
            return max((get_depth(arg, current_depth + 1) for arg in e.args), default=current_depth)
        return current_depth

    depth = get_depth(expr)
    if depth > max_depth:
        return False, f"Expression too deeply nested (depth={depth}, max={max_depth})"
    return True, ""


def check_expression_length(expr_str: str, max_length: int = MAX_EXPRESSION_LENGTH) -> Tuple[bool, str]:
    """
    Check if expression string length exceeds limit.

    Args:
        expr_str: String representation
        max_length: Maximum allowed length

    Returns:
        (is_safe, error_message)
    """
    length = len(expr_str)
    if length > max_length:
        return False, f"Expression too long (length={length}, max={max_length})"
    return True, ""


def check_term_count(expr, max_terms: int = MAX_TERM_COUNT) -> Tuple[bool, str]:
    """
    Check if expression has too many terms.

    Args:
        expr: Expression to check
        max_terms: Maximum allowed terms

    Returns:
        (is_safe, error_message)
    """
    def count_terms(e):
        """Recursively count terms in expression tree."""
        if hasattr(e, 'args'):
            return sum(count_terms(arg) for arg in e.args)
        return 1

    term_count = count_terms(expr)
    if term_count > max_terms:
        return False, f"Too many terms (count={term_count}, max={max_terms})"
    return True, ""


def validate_expression(expr, expr_str: str = None) -> Tuple[bool, str]:
    """
    Comprehensive validation of expression.

    Args:
        expr: Expression object
        expr_str: String representation (optional)

    Returns:
        (is_safe, error_message)
    """
    # Check depth
    is_safe, error = check_expression_depth(expr)
    if not is_safe:
        return is_safe, error

    # Check term count
    is_safe, error = check_term_count(expr)
    if not is_safe:
        return is_safe, error

    # Check string length if provided
    if expr_str:
        is_safe, error = check_expression_length(expr_str)
        if not is_safe:
            return is_safe, error

    return True, ""


__all__ = [
    'MAX_EXPRESSION_DEPTH',
    'MAX_EXPRESSION_LENGTH',
    'MAX_TERM_COUNT',
    'check_expression_depth',
    'check_expression_length',
    'check_term_count',
    'validate_expression',
]
