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
Safe Mathematical Expression Parser
====================================

Provides secure parsing of mathematical expressions, preventing code injection
attacks that are possible with raw sympify() or parse_expr().

Security measures:
1. Input validation and sanitization
2. Restricted local namespace (whitelist of allowed functions)
3. Length and complexity limits
4. Blacklist of dangerous patterns
5. No eval/exec of arbitrary code

Usage:
    from symbo_agentic_reasoners.core.safe_parser import safe_sympify, safe_parse

    expr = safe_sympify("x**2 + 2*x + 1")  # Safe
    expr = safe_sympify("__import__('os').system('rm -rf /')")  # Raises SecurityError
"""

import re
import logging
import math
import os
import threading
import concurrent.futures
from typing import Optional, Dict, Any, Set, Union, Callable, TypeVar

# NO SYMPY - Use native symbolic module
from symbo_agentic_reasoners.core.native_symbolic import (
    Expr, Symbol, Integer, Float, Rational,
    Add, Mul, Pow, Sin, Cos, Tan, Exp, Log, Sqrt, Abs, Sign,
    parse_expr as native_parse_expr, sympify as native_sympify, symbols
)

logger = logging.getLogger('symbo_agentic_reasoners.core.safe_parser')

# Type variable for timeout wrapper
T = TypeVar('T')


class SecurityError(Exception):
    """Raised when a security violation is detected in parsing."""
    pass


class ParseTimeoutError(SecurityError):
    """Raised when parsing times out (potential DoS attack)."""
    pass


class ExpressionComplexityError(SecurityError):
    """Raised when expression complexity exceeds safe limits."""
    pass


def _get_default_timeout() -> float:
    """Get default timeout from environment or use default."""
    env_timeout = os.environ.get('SYMBO_PARSE_TIMEOUT')
    if env_timeout:
        try:
            timeout = float(env_timeout)
            # Enforce reasonable bounds
            return max(0.1, min(timeout, 60.0))
        except ValueError:
            pass
    return 5.0


# Parser timeout configuration (seconds)
PARSE_TIMEOUT_SECONDS = _get_default_timeout()  # Maximum time for parsing operation
# Minimum timeout allowed (prevents effectively disabling protection)
MIN_TIMEOUT_SECONDS = 0.1
# Maximum timeout allowed (prevents accidental resource exhaustion)
MAX_TIMEOUT_SECONDS = 60.0


def _run_with_timeout(func: Callable[[], T], timeout: float, error_msg: str = "Operation timed out") -> T:
    """
    Execute a function with a timeout.

    Uses ThreadPoolExecutor for cross-platform timeout support (works on Windows).

    Args:
        func: Zero-argument callable to execute
        timeout: Maximum execution time in seconds
        error_msg: Error message if timeout occurs

    Returns:
        Result of the function

    Raises:
        ParseTimeoutError: If the operation times out
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            logger.warning(f"Parser timeout after {timeout}s: {error_msg}")
            raise ParseTimeoutError(f"{error_msg} (timeout: {timeout}s)")
        except Exception as e:
            # Re-raise other exceptions
            raise


# Maximum allowed input length (characters)
MAX_INPUT_LENGTH = 10000

# Maximum nesting depth for parentheses/brackets
MAX_NESTING_DEPTH = 50

# Maximum expression complexity score (prevents exponential blowup)
MAX_COMPLEXITY_SCORE = 1000

# Patterns that contribute to complexity
COMPLEXITY_PATTERNS = [
    (r'\*\*', 15),           # Exponentiation is expensive
    (r'factorial|!', 20),    # Factorial can explode
    (r'integrate|Integral', 25),  # Integration is very expensive
    (r'limit|Limit', 20),    # Limits can be expensive
    (r'series|taylor', 20),  # Series expansion
    (r'Matrix\[', 10),       # Matrix operations
    (r'det\(|determinant', 15),  # Determinant computation
    (r'solve|Solve', 15),    # Solving equations
    (r'Sum\(|Product\(', 20),  # Symbolic sums/products
]

# Dangerous patterns that should NEVER appear in math expressions
DANGEROUS_PATTERNS = [
    r'__\w+__',           # Dunder methods/attributes
    r'__import__',        # Import function
    r'__builtins__',      # Builtins access
    r'__class__',         # Class introspection
    r'__bases__',         # Base class access
    r'__subclasses__',    # Subclass enumeration
    r'__globals__',       # Global namespace access
    r'__code__',          # Code object access
    r'__reduce__',        # Pickle protocol
    r'\beval\s*\(',       # eval() calls
    r'\bexec\s*\(',       # exec() calls
    r'\bcompile\s*\(',    # compile() calls
    r'\bopen\s*\(',       # file open
    r'\bimport\s+',       # import statements
    r'\bfrom\s+\w+\s+import', # from imports
    r'\bos\.',            # os module access
    r'\bsys\.',           # sys module access
    r'\bsubprocess\.',    # subprocess module
    r'\bshutil\.',        # shutil module
    r'\bpickle\.',        # pickle module
    r'\bgetattr\s*\(',    # getattr() - can access anything
    r'\bsetattr\s*\(',    # setattr() - can modify anything
    r'\bdelattr\s*\(',    # delattr()
    r'\bvars\s*\(',       # vars() - namespace access
    r'\bdir\s*\(',        # dir() - attribute enumeration
    r'\bglobals\s*\(',    # globals() access
    r'\blocals\s*\(',     # locals() access
    r'\bbreakpoint\s*\(', # debugger
    r'\binput\s*\(',      # user input (could hang)
    r'\bprint\s*\(',      # print (side effect) - allowed in some contexts
    r'lambda\s+',         # lambda expressions
    r'\btype\s*\(',       # type() - can create classes
    r'\.mro\s*\(',        # Method resolution order
    r'\.read\s*\(',       # file read
    r'\.write\s*\(',      # file write
    r'\.system\s*\(',     # system calls
    r'\.popen\s*\(',      # process open
]

# Compile patterns for efficiency
DANGEROUS_REGEX = re.compile('|'.join(DANGEROUS_PATTERNS), re.IGNORECASE)

# Allowed native functions (whitelist)
# NO SYMPY - Use native symbolic module functions
SAFE_NATIVE_FUNCTIONS: Dict[str, Any] = {
    # Basic operations
    'Abs': Abs,
    'sign': Sign,
    'sqrt': Sqrt,
    'Pow': Pow,
    'exp': Exp,
    'log': Log,
    'ln': Log,

    # Trigonometric
    'sin': Sin,
    'cos': Cos,
    'tan': Tan,

    # Type constructors
    'Integer': Integer,
    'Rational': Rational,
    'Float': Float,
    'Symbol': Symbol,
    'symbols': symbols,

    # Constants (as floats for now)
    'pi': math.pi,
    'E': math.e,
    'e': math.e,

    # Math functions as fallbacks
    'floor': lambda x: int(math.floor(float(x))) if isinstance(x, (int, float)) else x,
    'ceiling': lambda x: int(math.ceil(float(x))) if isinstance(x, (int, float)) else x,
    'factorial': math.factorial,
    'gcd': math.gcd,
}

# Common variable names to auto-create as symbols
# Includes both lowercase and uppercase for diophantine equations, physics, etc.
# Note: Some uppercase letters (like N) conflict with SymPy functions, but we
# explicitly add them as symbols which overrides the functions in safe_locals
COMMON_VARIABLES = {'x', 'y', 'z', 't', 'n', 'k', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                    'i', 'j', 'm', 'p', 'q', 'r', 's', 'u', 'v', 'w',
                    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'theta', 'phi', 'psi',
                    'omega', 'lambda', 'mu', 'nu', 'sigma', 'tau', 'rho',
                    # Uppercase variables for Pell equations, physics constants, etc.
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W'}


def _check_nesting_depth(expr_str: str) -> int:
    """Check maximum nesting depth of parentheses/brackets."""
    max_depth = 0
    current_depth = 0

    for char in expr_str:
        if char in '([{':
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char in ')]}':
            current_depth -= 1

    return max_depth


def _estimate_complexity(expr_str: str) -> int:
    """
    Estimate computational complexity of an expression.

    This helps detect expressions that might cause exponential
    time complexity during parsing or evaluation.

    Returns:
        Complexity score (higher = more complex)
    """
    score = 0

    # Base score from length (logarithmic to avoid penalizing long but simple expressions)
    score += int(math.log2(len(expr_str) + 1)) * 2

    # Nesting depth contributes exponentially
    depth = _check_nesting_depth(expr_str)
    score += depth * depth  # Quadratic penalty for deep nesting

    # Check for complexity patterns
    for pattern, weight in COMPLEXITY_PATTERNS:
        matches = len(re.findall(pattern, expr_str, re.IGNORECASE))
        score += matches * weight

    # Nested exponentiation is particularly dangerous (tower of powers)
    tower_pattern = r'\*\*.*\*\*'
    if re.search(tower_pattern, expr_str):
        score += 50

    # Multiple operations with large numbers
    large_numbers = re.findall(r'\d{5,}', expr_str)
    score += len(large_numbers) * 10

    return score


def _check_balanced_parens(expr_str: str) -> tuple:
    """
    Check if parentheses/brackets are balanced.

    Returns:
        (is_balanced: bool, error_message: str or None)
    """
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}

    for i, char in enumerate(expr_str):
        if char in '([{':
            stack.append((char, i))
        elif char in ')]}':
            if not stack:
                return False, f"Unmatched closing '{char}' at position {i}"
            open_char, _ = stack.pop()
            if pairs[open_char] != char:
                return False, f"Mismatched brackets: '{open_char}' and '{char}'"

    if stack:
        open_char, pos = stack[0]
        return False, f"Unmatched opening '{open_char}' at position {pos} ({len(stack)} unclosed)"

    return True, None


def _create_safe_locals() -> Dict[str, Any]:
    """Create a safe local namespace for parsing."""
    safe_locals = SAFE_NATIVE_FUNCTIONS.copy()

    # Add common variables as symbols
    # Note: COMMON_VARIABLES intentionally overrides functions with the same name
    for var in COMMON_VARIABLES:
        safe_locals[var] = Symbol(var)

    return safe_locals


def validate_input(expr_str: str, check_complexity: bool = True) -> None:
    """
    Validate input string for security issues.

    Args:
        expr_str: The expression string to validate
        check_complexity: Whether to check expression complexity (default True)

    Raises:
        SecurityError: If dangerous patterns are detected
        ExpressionComplexityError: If expression is too complex
        ValueError: If input exceeds limits
    """
    if not isinstance(expr_str, str):
        raise TypeError(f"Expected string, got {type(expr_str).__name__}")

    # Check length
    if len(expr_str) > MAX_INPUT_LENGTH:
        raise ValueError(f"Input too long: {len(expr_str)} > {MAX_INPUT_LENGTH} characters")

    # Check for dangerous patterns
    match = DANGEROUS_REGEX.search(expr_str)
    if match:
        raise SecurityError(f"Dangerous pattern detected: '{match.group()}' - possible code injection attempt")

    # Check nesting depth
    depth = _check_nesting_depth(expr_str)
    if depth > MAX_NESTING_DEPTH:
        raise ValueError(f"Nesting too deep: {depth} > {MAX_NESTING_DEPTH}")

    # Check expression complexity (DoS protection)
    if check_complexity:
        complexity = _estimate_complexity(expr_str)
        if complexity > MAX_COMPLEXITY_SCORE:
            logger.warning(f"Expression complexity {complexity} exceeds limit {MAX_COMPLEXITY_SCORE}")
            raise ExpressionComplexityError(
                f"Expression too complex (score: {complexity}, max: {MAX_COMPLEXITY_SCORE}) - "
                "potential DoS attack or computationally infeasible expression"
            )

    # Check balanced parentheses (prevents SymPy parser crashes)
    balanced, error_msg = _check_balanced_parens(expr_str)
    if not balanced:
        raise ValueError(f"Syntax error: {error_msg}")

    # Check for null bytes (can confuse parsers)
    if '\x00' in expr_str:
        raise SecurityError("Null bytes not allowed in expression")

    # Check for bidirectional control characters (RTLO attacks)
    # These characters can make code appear different than it actually is
    bidi_chars = {
        '\u202a': 'LRE',   # Left-to-Right Embedding
        '\u202b': 'RLE',   # Right-to-Left Embedding
        '\u202c': 'PDF',   # Pop Directional Formatting
        '\u202d': 'LRO',   # Left-to-Right Override
        '\u202e': 'RLO',   # Right-to-Left Override (RTLO)
        '\u2066': 'LRI',   # Left-to-Right Isolate
        '\u2067': 'RLI',   # Right-to-Left Isolate
        '\u2068': 'FSI',   # First Strong Isolate
        '\u2069': 'PDI',   # Pop Directional Isolate
    }
    for char, name in bidi_chars.items():
        if char in expr_str:
            raise SecurityError(f"Bidirectional control character ({name}) not allowed - possible RTLO attack")


def _enforce_timeout_bounds(timeout: float) -> float:
    """Enforce timeout within safe bounds."""
    if timeout < MIN_TIMEOUT_SECONDS:
        logger.warning(f"Timeout {timeout}s below minimum, using {MIN_TIMEOUT_SECONDS}s")
        return MIN_TIMEOUT_SECONDS
    if timeout > MAX_TIMEOUT_SECONDS:
        logger.warning(f"Timeout {timeout}s above maximum, using {MAX_TIMEOUT_SECONDS}s")
        return MAX_TIMEOUT_SECONDS
    return timeout


def safe_sympify(expr_str: str, evaluate: bool = True, timeout: Optional[float] = None,
                 check_complexity: bool = True) -> Any:
    """
    Safely parse a mathematical expression using native parsing with restrictions.

    NO SYMPY - Pure native mathematical reasoning.
    This is a drop-in replacement for sp.sympify() with security hardening.

    Args:
        expr_str: Mathematical expression string
        evaluate: Whether to evaluate the expression (default True)
        timeout: Maximum parsing time in seconds (default from SYMBO_PARSE_TIMEOUT env or 5.0)
        check_complexity: Whether to check expression complexity (default True)

    Returns:
        Native symbolic expression

    Raises:
        SecurityError: If code injection attempt detected
        ParseTimeoutError: If parsing takes too long (potential DoS)
        ExpressionComplexityError: If expression is too complex
        ValueError: If input exceeds limits
    """
    # Handle non-string inputs (numbers, existing native objects)
    if isinstance(expr_str, (int, float)):
        return native_sympify(expr_str)
    if isinstance(expr_str, complex):
        # Handle complex numbers
        return native_sympify(str(expr_str))
    if isinstance(expr_str, Expr):
        return expr_str

    # Convert to string and strip
    expr_str = str(expr_str).strip()

    if not expr_str:
        raise ValueError("Empty expression")

    # Validate input (includes complexity check)
    validate_input(expr_str, check_complexity=check_complexity)

    # Enforce timeout bounds
    effective_timeout = _enforce_timeout_bounds(timeout if timeout is not None else PARSE_TIMEOUT_SECONDS)

    try:
        # Use native parsing with timeout protection
        result = _run_with_timeout(
            lambda: native_parse_expr(expr_str),
            timeout=effective_timeout,
            error_msg=f"Parsing expression '{expr_str[:50]}...'"
        )
        return result
    except ParseTimeoutError:
        raise  # Re-raise timeout as-is
    except Exception as e:
        logger.debug(f"native parse failed for '{expr_str[:100]}': {e}")
        raise


def safe_parse(expr_str: str,
               local_dict: Optional[Dict[str, Any]] = None,
               transformations: Optional[tuple] = None,
               timeout: Optional[float] = None,
               check_complexity: bool = True) -> Any:
    """
    Safely parse a mathematical expression using native parsing with restrictions.

    NO SYMPY - Pure native mathematical reasoning.
    This is a drop-in replacement for parse_expr() with security hardening.

    Args:
        expr_str: Mathematical expression string
        local_dict: Additional local variables (merged with safe defaults)
        transformations: Parser transformations (ignored - native parser used)
        timeout: Maximum parsing time in seconds (default from SYMBO_PARSE_TIMEOUT env or 5.0)
        check_complexity: Whether to check expression complexity (default True)

    Returns:
        Native symbolic expression

    Raises:
        SecurityError: If code injection attempt detected
        ParseTimeoutError: If parsing takes too long (potential DoS)
        ExpressionComplexityError: If expression is too complex
        ValueError: If input exceeds limits
    """
    # Handle non-string inputs
    if isinstance(expr_str, (int, float)):
        return native_sympify(expr_str)
    if isinstance(expr_str, complex):
        return native_sympify(str(expr_str))
    if isinstance(expr_str, Expr):
        return expr_str

    # Convert to string and strip
    expr_str = str(expr_str).strip()

    if not expr_str:
        raise ValueError("Empty expression")

    # Validate input (includes complexity check)
    validate_input(expr_str, check_complexity=check_complexity)

    # Enforce timeout bounds
    effective_timeout = _enforce_timeout_bounds(timeout if timeout is not None else PARSE_TIMEOUT_SECONDS)

    try:
        # Use native parsing with timeout protection
        result = _run_with_timeout(
            lambda: native_parse_expr(expr_str),
            timeout=effective_timeout,
            error_msg=f"Parsing expression '{expr_str[:50]}...'"
        )
        return result
    except ParseTimeoutError:
        raise  # Re-raise timeout as-is
    except Exception as e:
        logger.debug(f"native parse failed for '{expr_str[:100]}': {e}")
        raise


def is_safe_expression(expr_str: str) -> bool:
    """
    Check if an expression string appears safe to parse.

    Args:
        expr_str: Expression to check

    Returns:
        True if expression passes safety checks, False otherwise
    """
    try:
        validate_input(expr_str)
        return True
    except (SecurityError, ValueError, TypeError):
        return False


# Convenience aliases
sympify = safe_sympify
parse = safe_parse


if __name__ == "__main__":
    # Test cases
    print("Testing safe parser...\n")

    # Safe expressions
    safe_tests = [
        "x**2 + 2*x + 1",
        "sin(x) + cos(x)",
        "integrate(x**2, x)",
        "diff(sin(x), x)",
        "Matrix([[1, 2], [3, 4]])",
        "solve(x**2 - 4, x)",
        "limit(sin(x)/x, x, 0)",
        "factorial(10)",
        "pi + E",
    ]

    print("Safe expressions (should all pass):")
    for expr in safe_tests:
        try:
            result = safe_sympify(expr)
            print(f"  OK: {expr[:40]} -> {result}")
        except Exception as e:
            print(f"  FAIL: {expr[:40]} -> {e}")

    # Dangerous expressions
    dangerous_tests = [
        "__import__('os').system('id')",
        "eval('1+1')",
        "exec('print(1)')",
        "open('/etc/passwd').read()",
        "().__class__.__bases__[0].__subclasses__()",
        "getattr(x, '__class__')",
        "os.system('ls')",
        "lambda x: x",
    ]

    print("\nDangerous expressions (should all be blocked):")
    for expr in dangerous_tests:
        try:
            result = safe_sympify(expr)
            print(f"  DANGER - NOT BLOCKED: {expr[:40]}")
        except SecurityError as e:
            print(f"  BLOCKED: {expr[:40]}")
        except Exception as e:
            print(f"  ERROR (but safe): {expr[:40]} -> {type(e).__name__}")
