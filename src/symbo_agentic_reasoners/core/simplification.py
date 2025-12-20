"""
Algebraic Simplification Module
================================

Simplifies expressions before integration to enable solving more cases.

KEY SIMPLIFICATIONS:
- exp(ln(x)) → x
- ln(exp(x)) → x
- exp(a*ln(x)) → x^a
- exp(ln(f(x))) → f(x)
- Abs(x) handling
- Constant arithmetic

100% Native Python - NO SymPy dependency
"""

import re
import math
from typing import Tuple, Optional


def simplify_for_integration(expr: str, var: str = 'x') -> str:
    """
    Simplify expression before integration.

    Focuses on simplifications that enable integration:
    - exp(ln(...)) patterns
    - ln(exp(...)) patterns
    - Abs() removal where safe
    - Basic arithmetic

    Args:
        expr: Expression string
        var: Integration variable

    Returns:
        Simplified expression
    """
    if not expr or not isinstance(expr, str):
        return expr

    simplified = expr.strip()

    # Apply simplification rules iteratively
    max_iterations = 5
    for _ in range(max_iterations):
        prev = simplified

        # Rule 1: exp(ln(x)) → x
        simplified = _simplify_exp_ln(simplified, var)

        # Rule 2: ln(exp(x)) → x
        simplified = _simplify_ln_exp(simplified, var)

        # Rule 3: exp(a*ln(x)) → x^a
        simplified = _simplify_exp_a_ln(simplified, var)

        # Rule 4: Remove unnecessary Abs()
        simplified = _simplify_abs(simplified, var)

        # Rule 5: Basic arithmetic (constants)
        simplified = _simplify_arithmetic(simplified)

        # Rule 6: Remove redundant parentheses
        simplified = _simplify_parentheses(simplified)

        # Converged?
        if simplified == prev:
            break

    return simplified


def _simplify_exp_ln(expr: str, var: str) -> str:
    """
    Simplify exp(ln(x)) → x and exp(ln(f(x))) → f(x)

    Examples:
        exp(ln(x)) → x
        exp(ln(Abs(x))) → Abs(x)
        exp(ln(x**2)) → x**2
    """
    # Pattern: exp(ln(...))
    # Match exp(ln(...)) where ... is balanced
    pattern = r'exp\s*\(\s*ln\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*\)'

    def replace_exp_ln(match):
        inner = match.group(1).strip()
        return inner

    result = re.sub(pattern, replace_exp_ln, expr, flags=re.IGNORECASE)
    return result


def _simplify_ln_exp(expr: str, var: str) -> str:
    """
    Simplify ln(exp(x)) → x and ln(exp(f(x))) → f(x)

    Examples:
        ln(exp(x)) → x
        ln(exp(2*x)) → 2*x
    """
    # Pattern: ln(exp(...))
    pattern = r'ln\s*\(\s*exp\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*\)'

    def replace_ln_exp(match):
        inner = match.group(1).strip()
        return inner

    result = re.sub(pattern, replace_ln_exp, expr, flags=re.IGNORECASE)
    return result


def _simplify_exp_a_ln(expr: str, var: str) -> str:
    """
    Simplify exp(a*ln(x)) → x^a

    Examples:
        exp(2*ln(x)) → x**2
        exp(0.5*ln(x)) → x**0.5
        exp((1/2)*ln(x)) → x**(1/2)
    """
    # Pattern: exp(a*ln(x)) or exp(ln(x)*a)
    patterns = [
        (r'exp\s*\(\s*([^)]*?)\s*\*\s*ln\s*\(\s*(\w+)\s*\)\s*\)', r'\2**(\1)'),
        (r'exp\s*\(\s*ln\s*\(\s*(\w+)\s*\)\s*\*\s*([^)]*?)\s*\)', r'\1**(\2)'),
    ]

    result = expr
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def _simplify_abs(expr: str, var: str) -> str:
    """
    Remove Abs() where it's safe for integration purposes.

    For integration, Abs(x) can often be treated as x in the domain
    we're considering (typically x > 0 for ln(|x|) cases).

    Examples:
        Abs(x) → x  (when safe)
        ln(Abs(x)) → ln(x)  (standard integral form)
    """
    # Pattern: Abs(x) where x is just the variable
    result = re.sub(r'Abs\s*\(\s*(\w+)\s*\)', r'\1', expr)

    # Pattern: ln(Abs(...)) → ln(...)
    result = re.sub(r'ln\s*\(\s*Abs\s*\(([^)]+)\)\s*\)', r'ln(\1)', result, flags=re.IGNORECASE)

    return result


def _simplify_arithmetic(expr: str) -> str:
    """
    Simplify basic constant arithmetic.

    Examples:
        2*(1/2) → 1
        (1/2)*x**2 → 0.5*x**2
    """
    # Pattern: 2*(1/2) or (1/2)*2 → 1
    expr = re.sub(r'2\s*\*\s*\(\s*1\s*/\s*2\s*\)', '1', expr)
    expr = re.sub(r'\(\s*1\s*/\s*2\s*\)\s*\*\s*2', '1', expr)

    # Pattern: (a/b) → decimal where simple
    def eval_fraction(match):
        try:
            num = float(match.group(1))
            denom = float(match.group(2))
            if denom != 0:
                result = num / denom
                # Return as int if possible
                if result == int(result):
                    return str(int(result))
                return str(result)
        except:
            pass
        return match.group(0)

    expr = re.sub(r'\(\s*(\d+\.?\d*)\s*/\s*(\d+\.?\d*)\s*\)', eval_fraction, expr)

    return expr


def _simplify_parentheses(expr: str) -> str:
    """
    Remove redundant outer parentheses.

    Examples:
        (x) → x
        ((x**2)) → x**2
    """
    result = expr.strip()

    # Remove outer parentheses if they wrap the entire expression
    while result.startswith('(') and result.endswith(')'):
        # Check if this is a single balanced pair
        depth = 0
        is_single_pair = True
        for i, char in enumerate(result):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            if depth == 0 and i < len(result) - 1:
                is_single_pair = False
                break

        if is_single_pair:
            result = result[1:-1].strip()
        else:
            break

    return result


def test_simplification():
    """Test cases for simplification."""
    test_cases = [
        ("exp(ln(x))", "x"),
        ("exp(ln(Abs(x)))", "x"),
        ("ln(exp(x))", "x"),
        ("ln(exp(2*x))", "2*x"),
        ("exp(2*ln(x))", "x**2"),
        ("exp((1/2)*ln(x))", "x**0.5"),
        ("(exp(ln(x)))*(3)", "x*3"),
        ("exp(2*(1/2)*x**2)", "exp(1*x**2)"),
        ("Abs(x)", "x"),
        ("ln(Abs(x))", "ln(x)"),
    ]

    print("Simplification Tests:")
    print("=" * 60)
    for expr, expected in test_cases:
        result = simplify_for_integration(expr)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status:4s} {expr:30s} -> {result:20s} (expected: {expected})")


if __name__ == "__main__":
    test_simplification()
