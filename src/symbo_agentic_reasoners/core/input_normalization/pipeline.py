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
Input Normalization Pipeline - Main Orchestrator
=================================================

This module orchestrates the full input normalization pipeline by combining
all specialist modules in the correct order. It follows the supervisor-specialist
pattern where each specialist handles a focused responsibility.

Pipeline Order:
---------------
1. Artifact cleanup (copy-paste artifacts)
2. Unicode normalization (Greek letters, symbols)
3. Whitespace normalization
4. Notation preprocessing (prime, probability, matrix)
5. Pattern application (derivative, integral, modular, word)
6. Vector calculus expansion
7. Operator normalization
8. Implicit multiplication
9. Function name/parens normalization
10. Exponent precedence fixes
11. Equation normalization
12. Parenthesis closing
13. Validation
"""

import logging
import re
from typing import Tuple, Optional, Dict, Any, List

from .artifact_cleaner import cleanup_copypaste_artifacts
from .unicode_handler import normalize_unicode
from .whitespace_handler import normalize_whitespace
from .notation_preprocessor import (
    preprocess_prime_notation,
    preprocess_probability_symbols,
    preprocess_matrix_notation,
    preprocess_special_notations,
)
from .pattern_applier import (
    apply_modular_patterns,
    apply_derivative_patterns,
    apply_integral_patterns,
    apply_word_patterns,
)
from .vector_calculus import expand_vector_calculus
from .operator_normalizer import normalize_operators
from .multiplication import (
    enhanced_implicit_multiplication,
    remove_spurious_multiplication,
)
from .function_handler import (
    normalize_function_names,
    add_function_parens,
)
from .exponent_handler import fix_exponent_precedence
from .equation_normalizer import (
    normalize_equation_equals,
    close_unclosed_parens,
)
from .validator import validate_normalized
from .diagnostics import InputDiagnostic

logger = logging.getLogger('symbo_agentic_reasoners.input_normalization.pipeline')


class InputNormalizationPipeline:
    """
    Main coordinator for input normalization operations.

    This pipeline orchestrates all normalization specialists to transform
    raw mathematical input into a standard format suitable for parsing.

    Attributes:
        add_multiplication: Whether to insert implicit multiplication
        close_parens: Whether to auto-close unclosed parentheses
        verbose: Whether to log transformation steps
    """

    def __init__(
        self,
        add_multiplication: bool = True,
        close_parens: bool = True,
        verbose: bool = False
    ):
        self.add_multiplication = add_multiplication
        self.close_parens = close_parens
        self.verbose = verbose

    def normalize(self, text: str) -> str:
        """
        Run the full normalization pipeline.

        Args:
            text: Raw mathematical input

        Returns:
            Normalized expression string
        """
        if not text or not text.strip():
            return ""

        result = text

        # Step 1: Artifact cleanup
        result = cleanup_copypaste_artifacts(result)
        if self.verbose:
            logger.debug(f"After artifact cleanup: {result}")

        # Step 2: Unicode normalization
        result = normalize_unicode(result)
        if self.verbose:
            logger.debug(f"After unicode normalization: {result}")

        # Step 3: Whitespace normalization
        result = normalize_whitespace(result)
        if self.verbose:
            logger.debug(f"After whitespace normalization: {result}")

        # Step 4: Notation preprocessing
        result = preprocess_prime_notation(result)
        result = preprocess_probability_symbols(result)
        result = preprocess_matrix_notation(result)
        result = preprocess_special_notations(result)
        if self.verbose:
            logger.debug(f"After notation preprocessing: {result}")

        # Step 5: Pattern application
        result = apply_derivative_patterns(result)
        result = apply_integral_patterns(result)
        result = apply_modular_patterns(result)
        result = apply_word_patterns(result)
        if self.verbose:
            logger.debug(f"After pattern application: {result}")

        # Step 6: Vector calculus expansion
        result = expand_vector_calculus(result)
        if self.verbose:
            logger.debug(f"After vector calculus expansion: {result}")

        # Step 7: Operator normalization
        result = normalize_operators(result)
        if self.verbose:
            logger.debug(f"After operator normalization: {result}")

        # Step 8: Implicit multiplication
        if self.add_multiplication:
            result = enhanced_implicit_multiplication(result)
            result = remove_spurious_multiplication(result)
            if self.verbose:
                logger.debug(f"After implicit multiplication: {result}")

        # Step 9: Function normalization
        result = normalize_function_names(result)
        result = add_function_parens(result)
        if self.verbose:
            logger.debug(f"After function normalization: {result}")

        # Step 10: Exponent precedence
        result = fix_exponent_precedence(result)
        if self.verbose:
            logger.debug(f"After exponent precedence fix: {result}")

        # Step 11: Equation normalization
        result = normalize_equation_equals(result)
        if self.verbose:
            logger.debug(f"After equation normalization: {result}")

        # Step 12: Parenthesis closing
        if self.close_parens:
            result = close_unclosed_parens(result)
            if self.verbose:
                logger.debug(f"After parenthesis closing: {result}")

        return result.strip()

    def normalize_and_validate(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """
        Normalize and validate the input.

        Args:
            text: Raw mathematical input

        Returns:
            (normalized_text, is_valid, error_message)
        """
        normalized = self.normalize(text)
        is_valid, error = validate_normalized(normalized)
        return normalized, is_valid, error

    def diagnose(self, text: str, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Get diagnostic information for failed normalization.

        Args:
            text: Original input
            error: Error message if available

        Returns:
            Diagnostic dictionary
        """
        normalized = self.normalize(text)
        diagnostic = InputDiagnostic()
        return diagnostic.diagnose(text, normalized, error)


# Command extraction patterns
COMMAND_PATTERNS = {
    'solve': re.compile(r'^solve\s*\(\s*(.+?)\s*,\s*(\w+)\s*\)$', re.IGNORECASE),
    'diff': re.compile(r'^diff\s*\(\s*(.+?)\s*,\s*(\w+)\s*\)$', re.IGNORECASE),
    'integrate': re.compile(r'^integrate\s*\(\s*(.+?)\s*,\s*(\w+)\s*\)$', re.IGNORECASE),
    'limit': re.compile(r'^limit\s*\(\s*(.+?)\s*,\s*(\w+)\s*,\s*(.+?)\s*\)$', re.IGNORECASE),
    'simplify': re.compile(r'^simplify\s*\(\s*(.+?)\s*\)$', re.IGNORECASE),
    'expand': re.compile(r'^expand\s*\(\s*(.+?)\s*\)$', re.IGNORECASE),
    'factor': re.compile(r'^factor\s*\(\s*(.+?)\s*\)$', re.IGNORECASE),
    'series': re.compile(r'^series\s*\(\s*(.+?)\s*,\s*(\w+)\s*,\s*(.+?)\s*,\s*(\d+)\s*\)$', re.IGNORECASE),
    'dsolve': re.compile(r'^dsolve\s*\(\s*(.+?)\s*,\s*(\w+)\s*\)$', re.IGNORECASE),
}


def normalize_and_extract_command(
    text: str,
    add_multiplication: bool = True,
    close_parens: bool = True
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Normalize input and extract any command wrapper.

    Args:
        text: Raw mathematical input
        add_multiplication: Whether to add implicit multiplication
        close_parens: Whether to close unclosed parentheses

    Returns:
        (normalized_expression, command_metadata)
        command_metadata is None if no command was detected
    """
    if not text or not text.strip():
        return "", None

    text = text.strip()

    # Check for command wrappers
    for cmd_name, pattern in COMMAND_PATTERNS.items():
        match = pattern.match(text)
        if match:
            groups = match.groups()

            # Create pipeline for inner expression
            pipeline = InputNormalizationPipeline(
                add_multiplication=add_multiplication,
                close_parens=close_parens
            )

            if cmd_name == 'solve':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'solve',
                    'expression': expr,
                    'variable': groups[1],
                }
                return expr, metadata

            elif cmd_name == 'diff':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'diff',
                    'expression': expr,
                    'variable': groups[1],
                }
                return expr, metadata

            elif cmd_name == 'integrate':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'integrate',
                    'expression': expr,
                    'variable': groups[1],
                }
                return expr, metadata

            elif cmd_name == 'limit':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'limit',
                    'expression': expr,
                    'variable': groups[1],
                    'point': groups[2],
                }
                return expr, metadata

            elif cmd_name == 'simplify':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'simplify',
                    'expression': expr,
                }
                return expr, metadata

            elif cmd_name == 'expand':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'expand',
                    'expression': expr,
                }
                return expr, metadata

            elif cmd_name == 'factor':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'factor',
                    'expression': expr,
                }
                return expr, metadata

            elif cmd_name == 'series':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'series',
                    'expression': expr,
                    'variable': groups[1],
                    'point': groups[2],
                    'order': int(groups[3]),
                }
                return expr, metadata

            elif cmd_name == 'dsolve':
                expr = pipeline.normalize(groups[0])
                metadata = {
                    'command': 'dsolve',
                    'expression': expr,
                    'function': groups[1],
                }
                return expr, metadata

    # No command detected - just normalize
    pipeline = InputNormalizationPipeline(
        add_multiplication=add_multiplication,
        close_parens=close_parens
    )
    return pipeline.normalize(text), None


def normalize_input(
    text: str,
    add_multiplication: bool = True,
    close_parens: bool = True
) -> str:
    """
    Normalize mathematical input (main public API).

    Args:
        text: Raw mathematical input
        add_multiplication: Whether to add implicit multiplication
        close_parens: Whether to close unclosed parentheses

    Returns:
        Normalized expression string
    """
    pipeline = InputNormalizationPipeline(
        add_multiplication=add_multiplication,
        close_parens=close_parens
    )
    return pipeline.normalize(text)


def safe_normalize(text: str, default: str = "") -> str:
    """
    Safely normalize input, returning default on error.

    Args:
        text: Raw mathematical input
        default: Value to return on error

    Returns:
        Normalized expression or default
    """
    try:
        return normalize_input(text)
    except Exception as e:
        logger.warning(f"Normalization failed for '{text}': {e}")
        return default


__all__ = [
    'InputNormalizationPipeline',
    'normalize_input',
    'normalize_and_extract_command',
    'safe_normalize',
]
