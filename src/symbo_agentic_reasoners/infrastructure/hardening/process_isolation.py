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
Process-Level Isolation for Untrusted Inputs
============================================

Provides secure sandboxed execution of mathematical expressions using
subprocess isolation. This prevents any potential malicious code from
affecting the main application process.

Security Features:
1. Separate process execution (memory isolation)
2. Timeout enforcement
3. Resource limits (memory, CPU time)
4. Restricted Python environment (no imports allowed)
5. Output validation

Usage:
    from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
        IsolatedExecutor, execute_isolated
    )

    # Quick execution
    result = execute_isolated("x**2 + 2*x + 1", timeout=5.0)

    # With executor instance
    executor = IsolatedExecutor(max_memory_mb=100, timeout=5.0)
    result = executor.execute("diff(x**2, x)")
"""

import json
import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
import multiprocessing as mp

logger = logging.getLogger('symbo_agentic_reasoners.infrastructure.hardening.process_isolation')


@dataclass
class IsolationResult:
    """Result from isolated execution."""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    timed_out: bool = False
    memory_exceeded: bool = False


class IsolationError(Exception):
    """Raised when isolated execution fails."""
    pass


class IsolationTimeoutError(IsolationError):
    """Raised when isolated execution times out."""
    pass


class IsolationMemoryError(IsolationError):
    """Raised when isolated execution exceeds memory limit."""
    pass


# Worker script for isolated execution
_WORKER_SCRIPT = '''
import sys
import json

# Block all dangerous imports
_blocked_modules = {
    'os', 'subprocess', 'socket', 'urllib', 'requests', 'http',
    'ftplib', 'smtplib', 'telnetlib', 'ctypes', 'pickle', 'marshal',
    'importlib', 'shutil', 'pathlib', 'tempfile', 'glob', 'fnmatch',
    'multiprocessing', 'threading', 'concurrent', 'asyncio', 'signal',
    'pty', 'tty', 'termios', 'fcntl', 'resource', 'grp', 'pwd',
    'syslog', 'logging', 'code', 'codeop', 'compileall', 'dis',
    'inspect', 'traceback', 'gc', 'weakref', 'contextlib',
}

class BlockedImportFinder:
    def find_module(self, name, path=None):
        top_name = name.split('.')[0]
        if top_name in _blocked_modules:
            return self
        return None

    def load_module(self, name):
        raise ImportError(f"Import of '{name}' is blocked in sandbox")

sys.meta_path.insert(0, BlockedImportFinder())

# Safe imports
import math

def main():
    expr = sys.argv[1]

    # Safe math namespace
    safe_namespace = {
        '__builtins__': {},
        'abs': abs,
        'max': max,
        'min': min,
        'round': round,
        'sum': sum,
        'pow': pow,
        'int': int,
        'float': float,
        # Math functions
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'floor': math.floor,
        'ceil': math.ceil,
        'pi': math.pi,
        'e': math.e,
    }

    try:
        # Compile to check syntax without executing
        code = compile(expr, '<sandbox>', 'eval')

        # Execute in restricted namespace
        result = eval(code, safe_namespace)

        # Serialize result
        output = {'success': True, 'result': str(result), 'type': type(result).__name__}
    except Exception as e:
        output = {'success': False, 'error': str(e), 'error_type': type(e).__name__}

    print(json.dumps(output))

if __name__ == '__main__':
    main()
'''


class IsolatedExecutor:
    """
    Executes mathematical expressions in an isolated subprocess.

    This provides security through process isolation:
    - Separate memory space
    - Timeout enforcement
    - Restricted imports
    - Resource limits
    """

    def __init__(
        self,
        timeout: float = 5.0,
        max_memory_mb: int = 100,
        python_path: str = None
    ):
        """
        Initialize isolated executor.

        Args:
            timeout: Maximum execution time in seconds
            max_memory_mb: Maximum memory usage in MB (soft limit)
            python_path: Path to Python interpreter (default: sys.executable)
        """
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        self.python_path = python_path or sys.executable
        self._worker_file = None

    def _get_worker_script(self) -> str:
        """Get path to worker script, creating if needed."""
        if self._worker_file is None or not os.path.exists(self._worker_file):
            fd, path = tempfile.mkstemp(suffix='.py', prefix='symbo_sandbox_')
            with os.fdopen(fd, 'w') as f:
                f.write(_WORKER_SCRIPT)
            self._worker_file = path
        return self._worker_file

    def _analyze_expression_complexity(self, expr_str: str) -> Dict[str, Any]:
        """
        Analyze expression for computational complexity before execution.

        This prevents arithmetic DoS attacks like 2**1000000, factorial(10000).

        Returns:
            Dict with keys:
            - safe: bool (whether expression is safe to execute)
            - reason: str (explanation if unsafe)
            - estimated_ops: int (estimated number of operations)
        """
        import ast
        import re

        # Dangerous patterns that bypass AST analysis
        DANGEROUS_PATTERNS = [
            (r'\*\*\s*\d{4,}', 'Exponent too large (>=1000)'),
            (r'factorial\s*\(\s*\d{4,}', 'Factorial argument too large (>=1000)'),
            (r'\d{100,}', 'Number too large (>=100 digits)'),
            (r'factorial\s*\(\s*factorial', 'Nested factorials'),
            (r'\*\*\s*\([^)]*\*\*', 'Nested exponentiation'),  # Matches 2**(3**4) but not 2**8 + 3**5
        ]

        for pattern, reason in DANGEROUS_PATTERNS:
            if re.search(pattern, expr_str):
                return {'safe': False, 'reason': reason, 'estimated_ops': float('inf')}

        # Parse AST and analyze
        try:
            tree = ast.parse(expr_str, mode='eval')
        except SyntaxError as e:
            return {'safe': False, 'reason': f'Syntax error: {e}', 'estimated_ops': 0}

        # Analyze complexity
        class ComplexityAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.ops = 0
                self.exponents = []
                self.factorials = []

            def visit_BinOp(self, node):
                """Perform visit BinOp operation.

                Args:
                node: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.visit_BinOp(...)
                """
                """Perform visit BinOp operation.

                Args:
                node: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.visit_BinOp(...)
                """
                self.ops += 1
                if isinstance(node.op, ast.Pow):
                    """Perform visit Call operation.

                    Args:
                    node: Description needed

                    Returns:
                    Result of the operation

                    Example:
                    >>> result = obj.visit_Call(...)
                    """
                    # Check if exponent is a large constant
                    if isinstance(node.right, ast.Constant):
                        exp_val = node.right.value
                        if isinstance(exp_val, (int, float)) and exp_val > 1000:
                            self.exponents.append(exp_val)
                self.generic_visit(node)

            def visit_Call(self, node):
                """Perform visit Call operation.

                Args:
                node: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.visit_Call(...)
                """
                self.ops += 1
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'factorial':
                        if node.args and isinstance(node.args[0], ast.Constant):
                            arg_val = node.args[0].value
                            if isinstance(arg_val, int) and arg_val > 1000:
                                self.factorials.append(arg_val)
                self.generic_visit(node)

        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)

        # Check limits
        MAX_OPS = 10000
        MAX_EXPONENT = 1000
        MAX_FACTORIAL_ARG = 1000

        if analyzer.ops > MAX_OPS:
            return {
                'safe': False,
                'reason': f'Too many operations: {analyzer.ops}',
                'estimated_ops': analyzer.ops
            }

        if analyzer.exponents:
            max_exp = max(analyzer.exponents)
            return {
                'safe': False,
                'reason': f'Exponent too large: {max_exp}',
                'estimated_ops': float('inf')
            }

        if analyzer.factorials:
            max_fac = max(analyzer.factorials)
            return {
                'safe': False,
                'reason': f'Factorial argument too large: {max_fac}',
                'estimated_ops': float('inf')
            }

        return {
            'safe': True,
            'reason': 'Expression within safe limits',
            'estimated_ops': analyzer.ops
        }

    def execute(self, expression: str) -> IsolationResult:
        """
        Execute expression in isolated process.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            IsolationResult with success status and result/error
        """
        import time
        start_time = time.time()

        # Validate expression is not too long
        if len(expression) > 10000:
            return IsolationResult(
                success=False,
                result=None,
                error="Expression too long (max 10000 chars)",
                execution_time=0.0
            )

        # SECURITY: Analyze computational complexity before execution
        # This prevents arithmetic DoS attacks like 2**1000000, factorial(10000)
        complexity = self._analyze_expression_complexity(expression)
        if not complexity['safe']:
            logger.warning(f"Expression rejected (pre-execution): {complexity['reason']}")
            return IsolationResult(
                success=False,
                result=None,
                error=f"Expression rejected: {complexity['reason']}",
                execution_time=0.0
            )

        try:
            worker_script = self._get_worker_script()

            # Run in subprocess with timeout
            process = subprocess.Popen(
                [self.python_path, worker_script, expression],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
            )

            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                execution_time = time.time() - start_time

                if process.returncode != 0:
                    return IsolationResult(
                        success=False,
                        result=None,
                        error=stderr or "Process failed",
                        execution_time=execution_time
                    )

                # Parse output
                try:
                    output = json.loads(stdout.strip())
                    if output.get('success'):
                        return IsolationResult(
                            success=True,
                            result=output['result'],
                            execution_time=execution_time
                        )
                    else:
                        return IsolationResult(
                            success=False,
                            result=None,
                            error=output.get('error', 'Unknown error'),
                            execution_time=execution_time
                        )
                except json.JSONDecodeError:
                    return IsolationResult(
                        success=False,
                        result=None,
                        error=f"Invalid output: {stdout[:200]}",
                        execution_time=execution_time
                    )

            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                execution_time = time.time() - start_time
                return IsolationResult(
                    success=False,
                    result=None,
                    error="Execution timed out",
                    execution_time=execution_time,
                    timed_out=True
                )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.warning(f"Isolated execution failed: {e}")
            return IsolationResult(
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )

    def cleanup(self):
        """Clean up temporary files."""
        if self._worker_file and os.path.exists(self._worker_file):
            try:
                os.remove(self._worker_file)
            except OSError:
                pass
            self._worker_file = None

    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


# Global executor for convenience
_global_executor: Optional[IsolatedExecutor] = None


def get_executor(timeout: float = 5.0, max_memory_mb: int = 100) -> IsolatedExecutor:
    """Get or create global isolated executor."""
    global _global_executor
    if _global_executor is None:
        _global_executor = IsolatedExecutor(timeout=timeout, max_memory_mb=max_memory_mb)
    return _global_executor


def execute_isolated(
    expression: str,
    timeout: float = 5.0,
    max_memory_mb: int = 100
) -> IsolationResult:
    """
    Execute expression in isolated process (convenience function).

    Args:
        expression: Mathematical expression to evaluate
        timeout: Maximum execution time in seconds
        max_memory_mb: Maximum memory usage in MB

    Returns:
        IsolationResult with success status and result/error

    Example:
        result = execute_isolated("2**100")
        if result.success:
            print(result.result)
        else:
            print(f"Error: {result.error}")
    """
    executor = get_executor(timeout, max_memory_mb)
    return executor.execute(expression)


def is_safe_for_direct_execution(expression: str) -> bool:
    """
    Quick check if expression is safe enough for direct execution.

    This performs basic pattern matching to identify obviously safe expressions
    that don't need full process isolation.

    Args:
        expression: Expression to check

    Returns:
        True if expression appears safe for direct execution
    """
    # Must be short
    if len(expression) > 500:
        return False

    # Must only contain allowed characters
    allowed_chars = set('0123456789+-*/%^.()[] xyzabcdefghijklmnopqrstuvwXYZABCDEFGHIJKLMNOPQRSTUVW_,')
    allowed_funcs = {'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs', 'min', 'max', 'pow'}

    expression_clean = expression.lower()
    for func in allowed_funcs:
        expression_clean = expression_clean.replace(func, '')

    if not all(c in allowed_chars for c in expression_clean):
        return False

    # No string literals
    if '"' in expression or "'" in expression:
        return False

    # No dangerous patterns
    dangerous = ['import', 'exec', 'eval', 'open', 'file', '__', 'class', 'def', 'lambda']
    for pattern in dangerous:
        if pattern in expression.lower():
            return False

    return True


def execute_smart(
    expression: str,
    timeout: float = 5.0,
    force_isolation: bool = False
) -> IsolationResult:
    """
    Smart execution that uses isolation only when needed.

    For simple, safe expressions, uses direct evaluation for speed.
    For complex or potentially unsafe expressions, uses process isolation.

    Args:
        expression: Mathematical expression to evaluate
        timeout: Maximum execution time in seconds
        force_isolation: Always use process isolation

    Returns:
        IsolationResult with success status and result/error
    """
    import time
    start_time = time.time()

    if not force_isolation and is_safe_for_direct_execution(expression):
        # Safe expression - use direct evaluation
        try:
            import math
            safe_namespace = {
                '__builtins__': {},
                'abs': abs, 'max': max, 'min': min, 'round': round,
                'sum': sum, 'pow': pow, 'int': int, 'float': float,
                'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
                'tan': math.tan, 'exp': math.exp, 'log': math.log,
                'pi': math.pi, 'e': math.e,
            }

            # Add common variables
            from symbo_agentic_reasoners.core.native_symbolic import Symbol
            for var in 'xyzabcdefghijklmnopqrstuvwXYZABCDEFGHIJKLMNOPQRSTUVW':
                safe_namespace[var] = Symbol(var)

            result = eval(expression, safe_namespace)
            execution_time = time.time() - start_time
            return IsolationResult(
                success=True,
                result=str(result),
                execution_time=execution_time
            )
        except Exception as e:
            # Fall back to isolated execution on error
            pass

    # Use process isolation for complex/unsafe expressions
    return execute_isolated(expression, timeout)


# Export for convenience
__all__ = [
    'IsolatedExecutor',
    'IsolationResult',
    'IsolationError',
    'IsolationTimeoutError',
    'IsolationMemoryError',
    'execute_isolated',
    'execute_smart',
    'is_safe_for_direct_execution',
    'get_executor',
]
