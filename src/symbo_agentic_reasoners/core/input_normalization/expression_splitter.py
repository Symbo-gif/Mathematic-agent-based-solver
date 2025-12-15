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
Expression Splitter
===================

Handles detection and splitting of multiple mathematical expressions/problems
in a single input. Supports various formats including comma-separated,
semicolon-separated, newline-separated, numbered lists, and bullet points.
"""

import re
from typing import List


def split_multi_expressions(text: str) -> List[str]:
    """
    Split comma-separated expressions into individual problems.

    Handles cases like:
        "∫ x^2 dx, integrate x^2 dx, integrate(x^2, x)"
        -> ["∫ x^2 dx", "integrate x^2 dx", "integrate(x^2, x)"]

    Smart enough to NOT split inside function calls like integrate(x, (x, 0, 1))

    Args:
        text: Input text possibly containing comma-separated expressions

    Returns:
        List of individual expressions
    """
    if ',' not in text:
        return [text]

    # Track parentheses depth to avoid splitting inside function calls
    expressions = []
    current = []
    depth = 0

    for char in text:
        if char == '(':
            depth += 1
            current.append(char)
        elif char == ')':
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            # Top-level comma - split here
            expr = ''.join(current).strip()
            if expr:
                expressions.append(expr)
            current = []
        else:
            current.append(char)

    # Don't forget the last expression
    expr = ''.join(current).strip()
    if expr:
        expressions.append(expr)

    return expressions if expressions else [text]


def _split_respecting_parens(text: str, delimiter: str) -> List[str]:
    """
    Split text on delimiter while respecting parentheses/brackets.

    Args:
        text: Input text
        delimiter: Character to split on (e.g., ';' or ',')

    Returns:
        List of split segments
    """
    segments = []
    current = []
    depth = 0

    for char in text:
        if char in '([{':
            depth += 1
            current.append(char)
        elif char in ')]}':
            depth -= 1
            current.append(char)
        elif char == delimiter and depth == 0:
            segment = ''.join(current).strip()
            if segment:
                segments.append(segment)
            current = []
        else:
            current.append(char)

    # Don't forget the last segment
    segment = ''.join(current).strip()
    if segment:
        segments.append(segment)

    return segments if segments else [text]


def detect_multiple_problems(text: str) -> List[str]:
    """
    Detect and split multiple separate mathematical problems in input.

    Handles various input formats:
    - Newline-separated problems
    - Numbered lists (1. problem, 2. problem)
    - Bullet points (- problem, * problem, • problem)
    - Semicolon-separated problems
    - Comma-separated problems (delegates to split_multi_expressions)
    - Natural language separators ("and", "also", "then")

    Args:
        text: Input text possibly containing multiple problems

    Returns:
        List of individual problem strings

    Examples:
        "1. solve x^2 - 4 = 0\n2. integrate x dx"
        -> ["solve x^2 - 4 = 0", "integrate x dx"]

        "diff(sin(x), x); integrate(cos(x), x)"
        -> ["diff(sin(x), x)", "integrate(cos(x), x)"]

        "- find derivative of x^2\n- find integral of x"
        -> ["find derivative of x^2", "find integral of x"]
    """
    problems = []

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Step 1: Check for numbered list format (1. problem, 2. problem, etc.)
    numbered_pattern = r'(?:^|\n)\s*(\d+)\.\s*(.+?)(?=(?:\n\s*\d+\.|\n\n|\Z))'
    numbered_matches = re.findall(numbered_pattern, text, re.DOTALL)
    if len(numbered_matches) >= 2:
        # We have a numbered list with at least 2 items
        for _, problem in numbered_matches:
            clean_problem = problem.strip()
            if clean_problem:
                problems.append(clean_problem)
        return problems

    # Step 2: Check for bullet point format (-, *, •, ◦)
    bullet_pattern = r'(?:^|\n)\s*[-*•◦]\s*(.+?)(?=(?:\n\s*[-*•◦]|\n\n|\Z))'
    bullet_matches = re.findall(bullet_pattern, text, re.DOTALL)
    if len(bullet_matches) >= 2:
        for problem in bullet_matches:
            clean_problem = problem.strip()
            if clean_problem:
                problems.append(clean_problem)
        return problems

    # Step 3: Check for semicolon-separated problems (respecting parentheses)
    if ';' in text:
        semicolon_problems = _split_respecting_parens(text, ';')
        if len(semicolon_problems) >= 2:
            for problem in semicolon_problems:
                clean_problem = problem.strip()
                if clean_problem:
                    problems.append(clean_problem)
            return problems

    # Step 4: Check for newline-separated problems
    # Only split on newlines if each line looks like a complete mathematical expression
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    if len(non_empty_lines) >= 2:
        # Check if each line looks like a standalone math problem
        math_indicators = [
            r'\bintegrate\b', r'\bdiff\b', r'\bsolve\b', r'\blimit\b', r'\bsum\b',
            r'\bsimplify\b', r'\bfactor\b', r'\bexpand\b', r'\bevaluate\b',
            r'[∫∑∏∂∇]',  # Math symbols
            r'=',  # Equations
            r'\bwhat\s+is\b',  # Natural language queries
            r'\bfind\b', r'\bcalculate\b', r'\bcompute\b',
        ]

        all_look_like_problems = True
        for line in non_empty_lines:
            is_math_problem = any(re.search(pattern, line, re.IGNORECASE)
                                  for pattern in math_indicators)
            # Also accept if it's a pure mathematical expression
            is_math_expr = bool(re.match(r'^[\d\w\s\+\-\*/\^().\[\],=<>!]+$', line))
            if not (is_math_problem or is_math_expr):
                all_look_like_problems = False
                break

        if all_look_like_problems:
            return non_empty_lines

    # Step 5: Check for natural language separators
    # "solve x^2 = 4 and also find the derivative of x^3"
    nl_separators = [
        r'\s+and\s+(?:also\s+)?(?:then\s+)?',
        r'\s+then\s+',
        r'\s+also\s+',
        r'\.\s+(?:Also|Then|Next|Now)\s+',
    ]

    for separator in nl_separators:
        parts = re.split(separator, text, flags=re.IGNORECASE)
        if len(parts) >= 2:
            # Verify each part looks like a math problem
            valid_parts = []
            for part in parts:
                clean_part = part.strip().rstrip('.')
                if clean_part and len(clean_part) > 3:  # Avoid tiny fragments
                    valid_parts.append(clean_part)
            if len(valid_parts) >= 2:
                return valid_parts

    # Step 6: Fall back to comma-separated splitting
    comma_split = split_multi_expressions(text)
    if len(comma_split) >= 2:
        return comma_split

    # No multiple problems detected - return original as single item
    return [text.strip()]


def get_problem_count(text: str) -> int:
    """
    Get the number of separate problems detected in input.

    Useful for determining if multi-problem handling is needed.

    Args:
        text: Input text

    Returns:
        Number of detected problems
    """
    problems = detect_multiple_problems(text)
    return len(problems)
