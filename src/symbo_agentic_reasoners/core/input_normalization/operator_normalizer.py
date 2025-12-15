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
Operator Normalizer
===================

Normalizes mathematical operators to standard forms.
Handles caret notation, double operators, and spacing around equals.
"""

import re


def normalize_operators(text: str) -> str:
    """
    Normalize operator notation.

    Transformations:
        ^ → ** (LaTeX/common notation to Python)
        ++ → + (double positive)
        -- → + (double negative = positive)
        +- → - (plus-minus)
        -+ → - (minus-plus)
        Adds spaces around = for equations

    Args:
        text: Input text

    Returns:
        Text with normalized operators
    """
    result = text

    # ^ → ** (LaTeX/common notation to Python)
    result = result.replace('^', '**')

    # Handle double operators like ++ or -- or **
    result = re.sub(r'\+\+', '+', result)
    result = re.sub(r'--', '+', result)  # Double negative = positive
    result = re.sub(r'\+-', '-', result)
    result = re.sub(r'-\+', '-', result)

    # Ensure spaces around = for equations (but not ==, <=, >=, !=)
    result = re.sub(r'(?<![<>=!])=(?!=)', ' = ', result)

    return result
