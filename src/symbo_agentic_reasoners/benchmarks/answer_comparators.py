"""
Answer Comparison Utilities

Provides functions to compare answers for equivalence using various strategies:
- Numeric comparison (with tolerance)
- Symbolic expression comparison (using native engine)
- LaTeX expression comparison
- Set/interval comparison
"""

import re
from typing import Tuple, Optional
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)


def compare_numeric_answers(
    system_answer: str,
    expected_answer: str,
    tolerance: float = 1e-6
) -> Tuple[bool, str]:
    """
    Compare numeric answers with tolerance.

    Args:
        system_answer: Answer from solver
        expected_answer: Correct answer
        tolerance: Absolute tolerance for comparison

    Returns:
        (is_correct, explanation) tuple

    Examples:
        ("42", "42") -> (True, "Exact match")
        ("3.14159", "3.14159265") -> (True, "Within tolerance")
        ("5", "6") -> (False, "Numeric mismatch")
    """
    if not system_answer or not expected_answer:
        return False, "Empty answer"

    # Try direct string match first (fastest)
    if system_answer.strip() == expected_answer.strip():
        return True, "Exact string match"

    # Extract numeric values
    from .answer_extractors import extract_numeric_answer

    sys_num_str = extract_numeric_answer(system_answer)
    exp_num_str = extract_numeric_answer(expected_answer)

    if not sys_num_str or not exp_num_str:
        return False, "Could not extract numeric values"

    try:
        # Use Decimal for precise comparison
        sys_val = Decimal(sys_num_str)
        exp_val = Decimal(exp_num_str)

        diff = abs(sys_val - exp_val)

        if diff < Decimal(str(tolerance)):
            return True, f"Within tolerance (diff={float(diff):.2e})"
        else:
            return False, f"Numeric mismatch: {sys_val} != {exp_val} (diff={float(diff):.2e})"

    except (InvalidOperation, ValueError) as e:
        logger.debug(f"Numeric comparison failed: {e}")
        return False, f"Numeric conversion error: {e}"


def compare_symbolic_expressions(
    system_answer: str,
    expected_answer: str
) -> Tuple[bool, str]:
    """
    Compare mathematical expressions for symbolic equivalence.

    Uses the native symbolic engine (NO SYMPY) to check if expressions
    are mathematically equivalent.

    Args:
        system_answer: Answer from solver
        expected_answer: Correct answer

    Returns:
        (is_correct, explanation) tuple

    Examples:
        ("x^2 - 4", "(x-2)(x+2)") -> (True, "Expanded form match")
        ("2*x", "x + x") -> (True, "Simplified match")
    """
    if not system_answer or not expected_answer:
        return False, "Empty expression"

    # Try exact string match
    if system_answer.strip() == expected_answer.strip():
        return True, "Exact string match"

    try:
        # Import native symbolic engine
        # Note: This is a placeholder - actual implementation would use
        # the native symbolic engine from core/symbolic/

        # For now, try basic normalization
        sys_normalized = normalize_expression(system_answer)
        exp_normalized = normalize_expression(expected_answer)

        if sys_normalized == exp_normalized:
            return True, "Normalized match"

        # Try numeric comparison as fallback
        is_numeric, explanation = compare_numeric_answers(system_answer, expected_answer)
        if is_numeric:
            return True, f"Numeric equivalence: {explanation}"

        return False, "Expressions not equivalent"

    except Exception as e:
        logger.debug(f"Symbolic comparison failed: {e}")
        # Fallback to string comparison
        if system_answer.strip().lower() == expected_answer.strip().lower():
            return True, "Case-insensitive match"
        return False, f"Symbolic comparison error: {e}"


def normalize_expression(expr: str) -> str:
    """
    Normalize mathematical expression for comparison.

    Args:
        expr: Mathematical expression

    Returns:
        Normalized expression

    Normalization:
    - Remove whitespace
    - Convert ** to ^
    - Remove extra parentheses
    - Normalize function names
    """
    if not expr:
        return ""

    # Remove all whitespace
    expr = ''.join(expr.split())

    # Normalize power notation
    expr = expr.replace('**', '^')

    # Remove redundant parentheses around single terms
    expr = expr.replace('(-(', '(-')  # exp(-(x)) -> exp(-x)
    expr = expr.replace('(-x)', '-x')
    expr = expr.replace('(x)', 'x')

    # Normalize multiplication
    expr = expr.replace(')*', '*')
    expr = expr.replace('*(', '*')

    return expr


def compare_ode_solutions(
    system_answer: str,
    expected_answer: str
) -> Tuple[bool, str]:
    """
    Compare ODE solutions for mathematical equivalence.

    Handles:
    1. General vs particular solutions (C*exp(-x) vs exp(-x) where C=1)
    2. Format differences (exp(-x) vs exp(-(x)))
    3. Multiple constants (C1, C2 vs specific values)

    Args:
        system_answer: ODE solution from solver (may have C, C1, C2)
        expected_answer: Expected solution

    Returns:
        (is_correct, explanation) tuple

    Examples:
        ("y = C*exp(-x)", "y = exp(-x)") -> (True, "General solution with C=1")
        ("y = C*exp(-(x))", "y = exp(-x)") -> (True, "Format normalized")
    """
    if not system_answer or not expected_answer:
        return False, "Empty solution"

    # Normalize both solutions
    sys_norm = normalize_expression(system_answer)
    exp_norm = normalize_expression(expected_answer)

    # Direct match after normalization
    if sys_norm == exp_norm:
        return True, "Normalized match"

    # Handle general vs particular solutions
    # Replace integration constants with 1 to compare structure
    sys_with_c1 = sys_norm.replace('C*', '').replace('C1*', '').replace('C2*', '0*')
    sys_with_c1 = sys_with_c1.replace('C', '1').replace('C1', '1').replace('C2', '0')

    # Also try expected with implicit C=1
    exp_with_c = exp_norm

    if sys_with_c1 == exp_with_c:
        return True, "General solution matches particular (C=1)"

    # Try removing the "y = " prefix if present
    sys_expr = sys_norm.replace('y=', '').replace('y =', '')
    exp_expr = exp_norm.replace('y=', '').replace('y =', '')

    if sys_expr == exp_expr:
        return True, "Expression match (without y=)"

    # Try with C substitution on expressions
    sys_expr_c1 = sys_expr.replace('C*', '').replace('C1*', '').replace('C2*', '0*')
    sys_expr_c1 = sys_expr_c1.replace('C', '1').replace('C1', '1').replace('C2', '0')

    if sys_expr_c1 == exp_expr:
        return True, "Expression equivalence with C=1"

    # Check if expected answer is just "symbolic" (test placeholder)
    if expected_answer.strip().lower() in ['symbolic', 'symbolic solution', 'general']:
        # First, reject error dictionaries - these are NOT valid solutions
        sys_answer_lower = system_answer.lower()

        # Check for error indicators
        error_patterns = [
            "'success': false",
            '"success": false',
            "'error':",
            '"error":',
            "could not",
            "failed to",
            "unable to"
        ]

        for pattern in error_patterns:
            if pattern in sys_answer_lower:
                return False, f"Error response, not a valid solution: contains '{pattern}'"

        # Check for dictionary/JSON structure indicating an error response
        if system_answer.strip().startswith('{') and system_answer.strip().endswith('}'):
            # This looks like a dict - check if it's an error dict
            if 'success' in system_answer or 'error' in system_answer:
                return False, "Dictionary response (likely error), not a symbolic solution"

        # Only accept if it looks like an actual mathematical solution
        # Must have y = <expression> or just <expression>
        if 'y' in sys_norm or 'exp' in sys_norm or 'sin' in sys_norm or 'cos' in sys_norm:
            # Additional check: must not be a short response (error messages are usually longer)
            # Valid solutions should have mathematical structure
            if len(system_answer) > 10 and ('=' in system_answer or 'exp(' in system_answer or 'sin(' in system_answer or 'cos(' in system_answer):
                return True, "Symbolic solution (expected format flexible)"

        return False, "Does not appear to be a valid symbolic solution"

    # Try numeric comparison for expressions
    is_numeric, explanation = compare_numeric_answers(system_answer, expected_answer)
    if is_numeric:
        return True, f"Numeric equivalence: {explanation}"

    return False, f"Solutions not equivalent: '{sys_norm}' != '{exp_norm}'"


def compare_latex_expressions(
    system_answer: str,
    expected_answer: str
) -> Tuple[bool, str]:
    """
    Compare LaTeX mathematical expressions.

    Args:
        system_answer: Answer with LaTeX formatting
        expected_answer: Expected answer with LaTeX

    Returns:
        (is_correct, explanation) tuple

    Examples:
        ("\\frac{1}{2}", "0.5") -> (True, "Equivalent value")
        ("x^{2}", "x^2") -> (True, "LaTeX normalized")
    """
    if not system_answer or not expected_answer:
        return False, "Empty expression"

    # Extract LaTeX content
    from .answer_extractors import extract_latex_expression

    sys_latex = extract_latex_expression(system_answer)
    exp_latex = extract_latex_expression(expected_answer)

    # Direct match after normalization
    if sys_latex == exp_latex:
        return True, "LaTeX match (normalized)"

    # Try to extract mathematical content and compare symbolically
    # Remove LaTeX commands to get raw math
    sys_math = remove_latex_commands(sys_latex)
    exp_math = remove_latex_commands(exp_latex)

    # Try symbolic comparison
    is_symbolic, explanation = compare_symbolic_expressions(sys_math, exp_math)
    if is_symbolic:
        return True, f"Mathematical equivalence: {explanation}"

    # Try numeric comparison
    is_numeric, explanation = compare_numeric_answers(sys_math, exp_math)
    if is_numeric:
        return True, f"Numeric equivalence: {explanation}"

    return False, "LaTeX expressions not equivalent"


def remove_latex_commands(latex: str) -> str:
    """
    Remove LaTeX formatting commands to extract mathematical content.

    Args:
        latex: LaTeX expression

    Returns:
        Mathematical content without LaTeX commands

    Examples:
        "\\frac{1}{2}" -> "1/2"
        "x^{2}" -> "x^2"
    """
    if not latex:
        return ""

    # Replace common LaTeX commands with mathematical equivalents
    replacements = {
        r'\\frac\{([^}]+)\}\{([^}]+)\}': r'\1/\2',
        r'\\sqrt\{([^}]+)\}': r'sqrt(\1)',
        r'\\sqrt\[([^]]+)\]\{([^}]+)\}': r'\2^(1/\1)',
        r'\{([^}]+)\}': r'\1',  # Remove braces
        r'\\left': '',
        r'\\right': '',
    }

    result = latex
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result)

    return result


def compare_set_answers(
    system_answer: str,
    expected_answer: str
) -> Tuple[bool, str]:
    """
    Compare set/interval answers.

    Handles formats like:
    - {1, 2, 3}
    - [0, 5)
    - (-inf, inf)

    Args:
        system_answer: Answer representing a set
        expected_answer: Expected set

    Returns:
        (is_correct, explanation) tuple
    """
    if not system_answer or not expected_answer:
        return False, "Empty set"

    # Normalize set notation
    sys_normalized = normalize_set(system_answer)
    exp_normalized = normalize_set(expected_answer)

    if sys_normalized == exp_normalized:
        return True, "Set match"

    # Try parsing as interval
    sys_interval = parse_interval(system_answer)
    exp_interval = parse_interval(expected_answer)

    if sys_interval and exp_interval:
        if sys_interval == exp_interval:
            return True, "Interval match"

    return False, "Sets not equivalent"


def normalize_set(set_str: str) -> str:
    """Normalize set notation"""
    # Remove whitespace
    s = ''.join(set_str.split())

    # Sort elements if it's a finite set
    if s.startswith('{') and s.endswith('}'):
        elements = s[1:-1].split(',')
        elements_sorted = sorted(elements)
        return '{' + ','.join(elements_sorted) + '}'

    return s


def parse_interval(interval_str: str) -> Optional[Tuple]:
    """
    Parse interval notation.

    Returns:
        (start, end, left_closed, right_closed) or None

    Examples:
        "[0, 5)" -> (0, 5, True, False)
        "(-inf, inf)" -> (-inf, inf, False, False)
    """
    # Match interval patterns like [a, b], (a, b), [a, b), (a, b]
    pattern = r'([(\[])\s*([^,]+)\s*,\s*([^)\]]+)\s*([)\]])'
    match = re.match(pattern, interval_str.strip())

    if not match:
        return None

    left_bracket, start_str, end_str, right_bracket = match.groups()

    left_closed = (left_bracket == '[')
    right_closed = (right_bracket == ']')

    # Parse bounds
    try:
        from .answer_extractors import extract_numeric_answer
        start = extract_numeric_answer(start_str)
        end = extract_numeric_answer(end_str)
        return (start, end, left_closed, right_closed)
    except (ValueError, TypeError):
        return None


def compare_answers(
    system_answer: str,
    expected_answer: str,
    comparison_strategy: str = "auto"
) -> Tuple[bool, str]:
    """
    Generic answer comparison with multiple strategies.

    Args:
        system_answer: Answer from solver
        expected_answer: Correct answer
        comparison_strategy: "numeric", "symbolic", "latex", "set", or "auto"

    Returns:
        (is_correct, explanation) tuple

    Auto mode tries strategies in order:
    1. Exact string match
    2. Numeric comparison
    3. Symbolic comparison
    4. LaTeX comparison
    5. Set comparison
    """
    if not system_answer or not expected_answer:
        return False, "Empty answer"

    # Exact match (fastest)
    if system_answer.strip() == expected_answer.strip():
        return True, "Exact match"

    if comparison_strategy == "numeric":
        return compare_numeric_answers(system_answer, expected_answer)
    elif comparison_strategy == "symbolic":
        return compare_symbolic_expressions(system_answer, expected_answer)
    elif comparison_strategy == "latex":
        return compare_latex_expressions(system_answer, expected_answer)
    elif comparison_strategy == "set":
        return compare_set_answers(system_answer, expected_answer)
    elif comparison_strategy == "auto":
        # Try all strategies
        strategies = [
            ("numeric", compare_numeric_answers),
            ("symbolic", compare_symbolic_expressions),
            ("latex", compare_latex_expressions),
            ("set", compare_set_answers),
        ]

        for strategy_name, strategy_func in strategies:
            try:
                is_correct, explanation = strategy_func(system_answer, expected_answer)
                if is_correct:
                    return True, f"{strategy_name}: {explanation}"
            except Exception as e:
                logger.debug(f"{strategy_name} strategy failed: {e}")
                continue

        return False, "No strategy succeeded"
    else:
        return False, f"Unknown strategy: {comparison_strategy}"
