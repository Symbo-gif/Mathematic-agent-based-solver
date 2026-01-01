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
Symbolic Utils - Shared Utilities
==================================

Shared utility modules for symbolic mathematics.
"""

from .constants import MathConstant
from .validation import (
    MAX_EXPRESSION_DEPTH,
    MAX_EXPRESSION_LENGTH,
    MAX_TERM_COUNT,
    check_expression_depth,
    check_expression_length,
    check_term_count,
    validate_expression,
)

__all__ = [
    'MathConstant',
    'MAX_EXPRESSION_DEPTH',
    'MAX_EXPRESSION_LENGTH',
    'MAX_TERM_COUNT',
    'check_expression_depth',
    'check_expression_length',
    'check_term_count',
    'validate_expression',
]
