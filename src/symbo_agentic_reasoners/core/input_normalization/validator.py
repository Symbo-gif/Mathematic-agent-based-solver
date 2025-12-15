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
Expression Validator
====================

Validates that normalized text is likely parseable.
Checks for balanced parentheses, bad operator patterns, etc.
"""

import re
from typing import Tuple, Optional


def validate_normalized(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that normalized text is likely parseable.

    Checks:
        - Non-empty expression
        - Balanced parentheses, brackets, braces
        - No multiple consecutive operators
        - No leading/trailing operators

    Args:
        text: Normalized text to validate

    Returns:
        (is_valid, error_message) tuple where error_message is None if valid
    """
    if not text:
        return False, "Empty expression"

    # Check balanced parentheses
    if text.count('(') != text.count(')'):
        return False, f"Unbalanced parentheses: {text.count('(')} ( vs {text.count(')')} )"

    if text.count('[') != text.count(']'):
        return False, f"Unbalanced brackets: {text.count('[')} [ vs {text.count(']')} ]"

    if text.count('{') != text.count('}'):
        return False, f"Unbalanced braces: {text.count('{')} {{ vs {text.count('}')} }}"

    # Check for obviously bad patterns
    if re.search(r'[+\-*/^]{3,}', text):
        return False, "Multiple consecutive operators"

    if text.startswith(('*', '/', '^', '**')):
        return False, "Expression starts with operator"

    if re.search(r'[+\-*/^]\s*$', text) and not text.endswith('...'):
        return False, "Expression ends with operator"

    return True, None
