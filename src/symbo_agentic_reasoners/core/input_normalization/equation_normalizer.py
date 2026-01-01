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
Equation Normalizer
===================

Handles normalization of equation syntax (equals signs) and parenthesis balancing.
"""

import re


def normalize_equation_equals(text: str) -> str:
    """
    Convert single = to Eq() format for equation contexts.

    This helps SymPy parse equations properly:
        x^2 - 4 = 0 -> Eq(x**2 - 4, 0)
        x + y = 5 -> Eq(x + y, 5)

    Only applies when the = appears to be an equation, not assignment.

    Args:
        text: Input text

    Returns:
        Text with equation equals normalized
    """
    # Check if this looks like an equation (has = but not ==, <=, >=, !=)
    if '=' not in text:
        return text

    # Already has ==, <=, >=, != - leave alone
    if '==' in text or '<=' in text or '>=' in text or '!=' in text:
        return text

    # Check if it's inside a solve() or similar command - handle differently
    if re.search(r'\b(solve|dsolve)\s*\(', text, re.IGNORECASE):
        # Inside solve context - convert = to ==
        # But only the equation part, not the whole thing
        # This is complex - for now, just replace = with == conservatively
        pass

    # Simple case: expr = expr -> Eq(expr, expr)
    match = re.match(r'^(.+?)\s*=\s*(.+)$', text)
    if match:
        lhs, rhs = match.groups()
        # Don't convert if lhs looks like a function definition
        if not re.match(r'^\w+\s*\(', lhs):
            return f'Eq({lhs.strip()}, {rhs.strip()})'

    return text


def close_unclosed_parens(text: str) -> str:
    """
    Attempt to close unclosed parentheses at the end.

    This is a heuristic for cases like "sqrt(9" → "sqrt(9)"

    Args:
        text: Input text

    Returns:
        Text with balanced parentheses
    """
    open_count = text.count('(') - text.count(')')
    if open_count > 0:
        text = text + ')' * open_count

    open_count = text.count('[') - text.count(']')
    if open_count > 0:
        text = text + ']' * open_count

    open_count = text.count('{') - text.count('}')
    if open_count > 0:
        text = text + '}' * open_count

    return text
