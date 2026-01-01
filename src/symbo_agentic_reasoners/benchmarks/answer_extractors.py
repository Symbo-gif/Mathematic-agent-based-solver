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
Answer Extraction Utilities

Provides functions to extract answers from various dataset formats:
- GSM8K: Natural language with #### separator
- MATH: LaTeX with \boxed{} command
- AIME: Integer answers (0-999)
- Generic numeric extraction
"""

import re
from typing import Optional, List


def extract_numeric_answer(text: str) -> Optional[str]:
    """
    Extract numeric value from text.

    Args:
        text: Text containing numeric answer

    Returns:
        Extracted number as string, or None if not found

    Examples:
        "The answer is 42" -> "42"
        "x = 3.14159" -> "3.14159"
        "No numeric value" -> None
    """
    if not text:
        return None

    # Try to find numbers (including decimals, fractions, scientific notation)
    patterns = [
        r'-?\d+\.?\d*(?:[eE][+-]?\d+)?',  # Scientific notation
        r'-?\d+\/\d+',                     # Fractions
        r'-?\d+\.?\d*',                    # Regular decimals
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Return the last number found (usually the final answer)
            return matches[-1].strip()

    return None


def extract_gsm8k_answer(answer_text: str) -> str:
    """
    Extract answer from GSM8K format.

    GSM8K answers follow the format:
    "Step-by-step solution... #### FINAL_ANSWER"

    Args:
        answer_text: Full answer text from GSM8K dataset

    Returns:
        Extracted numeric answer

    Examples:
        "She sells 16-3=13 eggs. #### 13" -> "13"
        "Total is 5+7=12. #### 12" -> "12"
    """
    if not answer_text:
        return ""

    # Split on #### and get everything after
    if '####' in answer_text:
        parts = answer_text.split('####')
        if len(parts) > 1:
            # Get the part after ####, strip whitespace
            answer = parts[-1].strip()
            # Extract just the number (remove any trailing text)
            numeric = extract_numeric_answer(answer)
            return numeric if numeric else answer

    # Fallback: try to extract last number
    numeric = extract_numeric_answer(answer_text)
    return numeric if numeric else answer_text.strip()


def extract_math_boxed_answer(solution_text: str) -> str:
    """
    Extract answer from MATH dataset LaTeX format.

    MATH dataset answers are enclosed in \boxed{...} LaTeX command.

    Args:
        solution_text: Full solution text with LaTeX

    Returns:
        Extracted answer (without \boxed{} wrapper)

    Examples:
        "The solution is \boxed{42}" -> "42"
        "Therefore, x = \boxed{\frac{1}{2}}" -> "\frac{1}{2}"
        "Answer: \boxed{[2,5)}" -> "[2,5)"
    """
    if not solution_text:
        return ""

    # Pattern to match \boxed{content} including nested braces
    # This handles cases like \boxed{\frac{a}{b}}
    pattern = r'\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'

    matches = re.findall(pattern, solution_text)

    if matches:
        # Return the last boxed answer (final answer)
        answer = matches[-1].strip()

        # Remove any remaining LaTeX commands for simpler comparison
        # But keep the mathematical content
        return answer

    # Fallback: try to find answer at end of text
    lines = solution_text.strip().split('\n')
    if lines:
        last_line = lines[-1].strip()
        # Remove common prefixes
        for prefix in ['Answer:', 'Therefore,', 'Thus,', 'So,', 'Final answer:']:
            if last_line.startswith(prefix):
                last_line = last_line[len(prefix):].strip()
        return last_line

    return solution_text.strip()


def extract_aime_answer(answer: any) -> str:
    """
    Extract answer from AIME format.

    AIME answers are always integers from 0 to 999.

    Args:
        answer: Answer value (could be int, str, etc.)

    Returns:
        Integer answer as string

    Examples:
        "123" -> "123"
        123 -> "123"
        "The answer is 456" -> "456"
    """
    # If already an integer or integer string, return as string
    if isinstance(answer, int):
        return str(answer)

    if isinstance(answer, str):
        # Try to extract integer
        numeric = extract_numeric_answer(answer)
        if numeric:
            # Convert to int to remove decimals, then back to string
            try:
                return str(int(float(numeric)))
            except (ValueError, OverflowError):
                pass

        # Try direct conversion
        try:
            return str(int(answer))
        except (ValueError, TypeError):
            pass

    # Last resort: return as-is
    return str(answer).strip()


def extract_latex_expression(text: str) -> str:
    """
    Extract mathematical expression from LaTeX formatting.

    Normalizes LaTeX by removing display formatting while preserving
    mathematical content.

    Args:
        text: Text possibly containing LaTeX

    Returns:
        Normalized LaTeX expression

    Examples:
        r"\left(\frac{1}{2}\right)" -> r"(\frac{1}{2})"
        "x^{2}" -> "x^2"
    """
    if not text:
        return ""

    # Remove \left and \right
    text = text.replace('\\left', '').replace('\\right', '')

    # Remove unnecessary spacing commands
    text = text.replace('\\,', ' ').replace('\\!', '').replace('\\;', ' ')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_answer_from_text(text: str, dataset: str = 'generic') -> str:
    """
    Generic answer extraction with dataset-specific handling.

    Args:
        text: Answer text
        dataset: Dataset name ('gsm8k', 'math', 'aime', 'generic')

    Returns:
        Extracted answer

    Examples:
        extract_answer_from_text("#### 42", "gsm8k") -> "42"
        extract_answer_from_text("\boxed{17}", "math") -> "17"
        extract_answer_from_text("123", "aime") -> "123"
    """
    dataset = dataset.lower()

    if dataset == 'gsm8k':
        return extract_gsm8k_answer(text)
    elif dataset == 'math':
        return extract_math_boxed_answer(text)
    elif dataset == 'aime':
        return extract_aime_answer(text)
    else:
        # Generic: try numeric extraction
        numeric = extract_numeric_answer(text)
        return numeric if numeric else text.strip()


def clean_answer(answer: str) -> str:
    """
    Clean and normalize answer string for comparison.

    Args:
        answer: Raw answer string

    Returns:
        Cleaned answer

    Normalization steps:
    - Strip whitespace
    - Remove trailing punctuation
    - Normalize number formats
    - Remove dollar signs
    """
    if not answer:
        return ""

    # Strip whitespace
    answer = answer.strip()

    # Remove dollar signs (common in math problems)
    answer = answer.replace('$', '')

    # Remove trailing punctuation
    answer = answer.rstrip('.,;:!?')

    # Normalize spacing
    answer = re.sub(r'\s+', ' ', answer)

    return answer.strip()
