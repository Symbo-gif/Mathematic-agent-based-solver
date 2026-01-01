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
Function Handler
================

Handles normalization of function names and automatic insertion of
parentheses for function calls without them.
"""

import re
from typing import Dict


# Function name variations → canonical names
FUNCTION_ALIASES: Dict[str, str] = {
    # Trig
    'sine': 'sin', 'cosine': 'cos', 'tangent': 'tan',
    'secant': 'sec', 'cosecant': 'csc', 'cotangent': 'cot',
    'arcsine': 'asin', 'arccosine': 'acos', 'arctangent': 'atan',
    'arcsin': 'asin', 'arccos': 'acos', 'arctan': 'atan',
    # Hyperbolic
    'sinh': 'sinh', 'cosh': 'cosh', 'tanh': 'tanh',
    # Logs
    'logarithm': 'log', 'natural_log': 'ln',
    # Misc
    'squareroot': 'sqrt', 'square_root': 'sqrt',
    'cuberoot': 'cbrt', 'cube_root': 'cbrt',
    'absolute': 'Abs', 'abs': 'Abs',
    'exponential': 'exp',
    'ceiling': 'ceiling', 'ceil': 'ceiling',
    'floor': 'floor',
}


def normalize_function_names(text: str) -> str:
    """
    Normalize function name variations to canonical forms.

    Args:
        text: Input text

    Returns:
        Text with normalized function names
    """
    result = text

    for alias, canonical in FUNCTION_ALIASES.items():
        # Word boundary to avoid partial matches
        pattern = r'\b' + re.escape(alias) + r'\b'
        result = re.sub(pattern, canonical, result, flags=re.IGNORECASE)

    return result


def add_function_parens(text: str) -> str:
    """
    Add parentheses to function calls without them.

    Examples:
        sqrt9 → sqrt(9)
        sin30 → sin(30)
        log10 → log(10)

    Args:
        text: Input text

    Returns:
        Text with function parentheses added
    """
    # Pattern: function name followed by number (without paren)
    func_pattern = re.compile(
        r'\b(sqrt|cbrt|sin|cos|tan|sec|csc|cot|'
        r'asin|acos|atan|asec|acsc|acot|'
        r'sinh|cosh|tanh|'
        r'log|ln|exp|Abs|abs|sign|floor|ceiling|ceil)'
        r'(\d+\.?\d*)\b'
    )

    return func_pattern.sub(r'\1(\2)', text)
