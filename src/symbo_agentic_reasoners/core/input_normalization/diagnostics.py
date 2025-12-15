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
Input Diagnostics
=================

Provides detailed diagnostic messages for input parsing failures.
Instead of generic errors, this module analyzes the input and provides
specific, actionable error messages.
"""

import re
from typing import Dict, Any, Optional


class InputDiagnostic:
    """
    Provides detailed diagnostic messages for input parsing failures.

    Instead of generic "No expression to solve", this class analyzes the
    input and provides specific, actionable error messages.
    """

    # Patterns that indicate specific error categories
    MATRIX_MALFORMED = re.compile(r'\[\s*,|\,\s*\]|\[\s*\]')
    PROBABILITY_NOTATION = re.compile(
        r'\b(E|Var|Cov|Std)\s*\(\s*\w+\s*\)\s*(where|~|given)',
        re.IGNORECASE
    )
    DISTRIBUTION_NOTATION = re.compile(
        r'\b(Normal|Binomial|Poisson|Uniform|Exponential)\s*\(\s*[^)]*\)',
        re.IGNORECASE
    )
    ENGLISH_GLUE = re.compile(
        r'\b(where|such that|given that|for all|there exists)\b',
        re.IGNORECASE
    )
    UNSUPPORTED_COMMAND = re.compile(
        r'\b(eigenvals|eigenvects|det|trace|rank)\s*\(\s*\[',
        re.IGNORECASE
    )

    @classmethod
    def diagnose(cls, original_input: str, normalized: str,
                 parse_error: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze input and provide detailed diagnostic information.

        Args:
            original_input: The original user input
            normalized: The normalized form
            parse_error: Optional error message from parser

        Returns:
            Dictionary with:
            - 'category': Error category (e.g., 'matrix_syntax', 'probability')
            - 'message': User-friendly error message
            - 'suggestion': Suggested fix
            - 'details': Technical details for debugging
        """
        result = {
            'category': 'unknown',
            'message': 'Failed to parse expression',
            'suggestion': None,
            'details': parse_error,
            'original': original_input,
            'normalized': normalized
        }

        # Check for malformed matrix syntax
        if cls.MATRIX_MALFORMED.search(original_input):
            result['category'] = 'matrix_syntax'
            result['message'] = 'Matrix literal is malformed (empty or missing elements)'
            result['suggestion'] = (
                'Ensure matrix rows are fully specified. '
                'Example: [[1,2,3], [4,5,6], [7,8,9]]'
            )
            return result

        # Check for unsupported linear algebra command syntax
        if cls.UNSUPPORTED_COMMAND.search(original_input):
            match = cls.UNSUPPORTED_COMMAND.search(original_input)
            cmd = match.group(1) if match else 'command'
            result['category'] = 'linalg_syntax'
            result['message'] = f'Linear algebra function "{cmd}" requires proper matrix format'
            result['suggestion'] = (
                f'Use fully specified matrices. '
                f'Example: {cmd}([[1,2], [3,4]])'
            )
            return result

        # Check for probability/statistics English notation
        if cls.PROBABILITY_NOTATION.search(original_input):
            result['category'] = 'probability_notation'
            result['message'] = 'English probability notation is not yet supported'
            result['suggestion'] = (
                'Use explicit function notation instead. '
                'Example: Instead of "E(X^2) where X ~ Normal(0,1)", '
                'use "E(X**2, (X, Normal(0,1)))" or compute directly.'
            )
            return result

        # Check for distribution with English glue words
        if cls.DISTRIBUTION_NOTATION.search(original_input) and \
           cls.ENGLISH_GLUE.search(original_input):
            result['category'] = 'probability_english'
            result['message'] = 'Natural language probability expressions require explicit notation'
            result['suggestion'] = (
                'Remove English phrases like "where", "given that". '
                'Use: pdf(Normal(0, 1), x) or cdf(Normal(mu, sigma), x)'
            )
            return result

        # Check for English glue words that weren't processed
        if cls.ENGLISH_GLUE.search(normalized):
            match = cls.ENGLISH_GLUE.search(normalized)
            phrase = match.group(1) if match else 'phrase'
            result['category'] = 'english_phrase'
            result['message'] = f'English phrase "{phrase}" could not be converted to mathematical notation'
            result['suggestion'] = (
                'Rewrite using mathematical symbols. '
                'Examples: "for all x" → "ForAll(x, ...)", '
                '"there exists" → "Exists(x, ...)"'
            )
            return result

        # Check for missing multiplication (merged identifiers)
        merged_pattern = re.compile(r'[a-z]{5,}', re.IGNORECASE)
        if merged_pattern.search(normalized):
            match = merged_pattern.search(normalized)
            merged = match.group(0) if match else ''
            # Skip if it's a known function
            known = {'integrate', 'differentiate', 'simplify', 'expand',
                     'factor', 'sqrt', 'Normal', 'Binomial', 'Poisson'}
            if merged.lower() not in {k.lower() for k in known}:
                result['category'] = 'missing_multiplication'
                result['message'] = f'Possible missing multiplication in "{merged}"'
                result['suggestion'] = (
                    'Insert * between multiplied terms. '
                    f'Example: "{merged}" might be "{merged[0]}*{merged[1:]}..."'
                )
                return result

        # Check for assignment vs equation confusion
        if '=' in original_input and '==' not in original_input:
            if 'SympifyError' in str(parse_error) or 'assignment' in str(parse_error).lower():
                result['category'] = 'equation_syntax'
                result['message'] = 'Expression contains "=" which may be interpreted as assignment'
                result['suggestion'] = (
                    'For equations, use Eq(lhs, rhs) or == instead of =. '
                    'Example: Eq(x**2 - 4, 0) or x**2 - 4 == 0'
                )
                return result

        # Check for prime notation issues
        if "'" in original_input and 'unterminated' in str(parse_error).lower():
            result['category'] = 'prime_notation'
            result['message'] = 'Prime notation (derivative) was not properly converted'
            result['suggestion'] = (
                "Use diff() notation instead. "
                "Example: y'(x) → diff(y(x), x), y''(x) → diff(y(x), x, 2)"
            )
            return result

        # Generic fallback with helpful context
        result['category'] = 'parse_error'
        result['message'] = 'Expression could not be parsed'
        if parse_error:
            # Extract meaningful part of error
            if 'sympify' in parse_error.lower():
                result['suggestion'] = (
                    'Check for: missing multiplication (*), '
                    'unsupported notation, or typos in function names.'
                )
            elif 'type' in parse_error.lower():
                result['suggestion'] = (
                    'The expression type is not supported. '
                    'Try simplifying or breaking into smaller parts.'
                )

        return result

    @classmethod
    def format_error(cls, diagnostic: Dict[str, Any], verbose: bool = False) -> str:
        """
        Format a diagnostic result into a user-friendly error message.

        Args:
            diagnostic: Result from diagnose()
            verbose: Include technical details

        Returns:
            Formatted error message string
        """
        lines = [f"Error: {diagnostic['message']}"]

        if diagnostic.get('suggestion'):
            lines.append(f"Suggestion: {diagnostic['suggestion']}")

        if verbose and diagnostic.get('details'):
            lines.append(f"Technical: {diagnostic['details']}")

        return '\n'.join(lines)
