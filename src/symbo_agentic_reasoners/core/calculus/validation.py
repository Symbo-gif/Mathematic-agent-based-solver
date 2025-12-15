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
Expression Validation and Safety Checks
========================================

This module provides safety checks to prevent DoS attacks via
deeply nested or excessively long expressions.
"""

from typing import Tuple


# =============================================================================
# SAFETY LIMITS
# =============================================================================
MAX_EXPRESSION_DEPTH = 50  # Maximum nesting level for parentheses/functions
MAX_EXPRESSION_LENGTH = 10000  # Maximum expression length in characters


def check_expression_safety(expr: str) -> Tuple[bool, str]:
    """
    Check if expression is safe to process (not too deeply nested or too long).

    Args:
        expr: Expression string to validate

    Returns:
        (is_safe, error_message)
        - is_safe: True if expression passes safety checks
        - error_message: Empty string if safe, otherwise describes the issue
    """
    if len(expr) > MAX_EXPRESSION_LENGTH:
        return False, f"Expression too long ({len(expr)} chars, max {MAX_EXPRESSION_LENGTH})"

    # Count maximum nesting depth
    depth = 0
    max_depth = 0
    for char in expr:
        if char == '(':
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == ')':
            depth -= 1

    if max_depth > MAX_EXPRESSION_DEPTH:
        return False, f"Expression too deeply nested ({max_depth} levels, max {MAX_EXPRESSION_DEPTH})"

    return True, ""


# Backward compatibility alias
_check_expression_safety = check_expression_safety
