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
Exponent Handler
================

Fixes exponentiation precedence issues to ensure correct evaluation.
Standard mathematical convention: ** binds tighter than unary minus.
"""

import re


def fix_exponent_precedence(text: str) -> str:
    """
    Fix exponentiation precedence issues.

    Standard mathematical convention: ** binds tighter than unary minus.
    So -x**2 means -(x**2), not (-x)**2.

    But some parsers (including our native_calculus parser) interpret
    -x**2 as (-x)**2. This function rewrites problematic patterns to
    ensure correct evaluation.

    Transformations:
        -x**n → (-1)*x**n   (where n is any exponent)
        -a*x**n stays as is (already has explicit coefficient)

    This ensures that exp(-x**4) evaluates as exp(-(x**4)) = exp(-x^4)
    rather than exp((-x)**4) = exp(x^4).

    Args:
        text: Input text

    Returns:
        Text with exponent precedence fixed
    """
    # Pattern: -variable**exponent where the minus is a unary operator
    # Matches: -x**2, -y**4, -t**3, etc.
    # Does NOT match: a-x**2 (binary minus), -3*x**2 (already has coefficient)

    # Replace -var**exp with (-1)*var**exp
    # The lookbehind ensures we only match unary minus (after (, +, *, /, =, or start)
    result = re.sub(
        r'(?<=[(+*/=,\s])-([a-zA-Z_][a-zA-Z0-9_]*)\*\*',
        r'(-1)*\1**',
        text
    )

    # Also handle at start of string
    if result.startswith('-') and '**' in result:
        # Check if it's -var**something at the very start
        match = re.match(r'^-([a-zA-Z_][a-zA-Z0-9_]*)\*\*', result)
        if match:
            result = '(-1)*' + result[1:]

    return result
