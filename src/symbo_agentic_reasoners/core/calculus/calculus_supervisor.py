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
Calculus Supervisor - Main Coordinator for Calculus Operations
===============================================================

This supervisor orchestrates calculus operations by delegating to specialist agents.
It follows the supervisor-specialist pattern from LangChain, where each specialist
handles a focused responsibility and the supervisor manages routing and coordination.

Architecture:
------------
┌─────────────────────────────────────┐
│      Calculus Supervisor            │
│  (Routing & Coordination Logic)     │
└──────────────┬──────────────────────┘
               │
               ├─ Validation Specialist (safety checks)
               ├─ Expression Parser (string → AST)
               ├─ Differentiation Specialist (derivatives)
               ├─ Integration Specialist (antiderivatives)
               ├─ Limit Specialist (limits & L'Hôpital)
               ├─ Series Specialist (infinite series)
               └─ Special Integrals Specialist (special patterns)

Delegation Flow:
---------------
1. User Request → Supervisor
2. Supervisor → Validation (check safety)
3. Supervisor → Parser (parse to AST)
4. Supervisor → Appropriate Specialist
5. Specialist → Result
6. Supervisor → Formatted Output

This module will be fully implemented after all specialists are extracted.
Currently serves as an architectural placeholder and integration point.
"""

import logging
from typing import Tuple, Optional, Union

# Import validation, parser, and AST types from local modules
from .validation import check_expression_safety
from .expression_parser import ExprParser
from .ast_types import Expr

logger = logging.getLogger(__name__)


class CalculusSupervisor:
    """
    Main supervisor for coordinating calculus operations.

    This supervisor follows the LangChain supervisor-specialist pattern:
    - Each specialist is wrapped as a "tool" with a clear interface
    - Supervisor decides which specialist(s) to invoke based on operation type
    - Supervisor handles validation, parsing, formatting, and error handling
    - Specialists focus solely on their domain (diff, int, limit, series)

    Attributes:
        parser: Expression parser (string → AST)
        diff_specialist: Differentiation engine
        int_specialist: Integration engine
        limit_specialist: Limit evaluation engine
        series_specialist: Series summation engine
        special_int_specialist: Special integral pattern matcher
    """

    def __init__(self):
        """Initialize supervisor with all specialist agents."""
        # Parser (shared across all operations)
        self.parser = ExprParser()

        # Lazy-load specialists to improve startup time
        self._diff_specialist = None
        self._int_specialist = None
        self._limit_specialist = None
        self._series_specialist = None
        self._special_int_specialist = None

    @property
    def diff_specialist(self):
        """Lazy-load differentiation specialist."""
        if self._diff_specialist is None:
            from .differentiation_specialist import DifferentiationEngine
            self._diff_specialist = DifferentiationEngine()
        return self._diff_specialist

    @property
    def int_specialist(self):
        """Lazy-load integration specialist."""
        if self._int_specialist is None:
            from .integration_specialist import IntegrationEngine
            self._int_specialist = IntegrationEngine()
        return self._int_specialist

    @property
    def limit_specialist(self):
        """Lazy-load limit specialist."""
        if self._limit_specialist is None:
            from .limit_specialist import LimitEngine
            self._limit_specialist = LimitEngine()
        return self._limit_specialist

    def differentiate(self, expr_str: str, var: str = 'x') -> Tuple[bool, Optional[str], str]:
        """
        Differentiate expression with respect to variable.

        This is the main entry point for differentiation. It:
        1. Validates expression safety
        2. Parses string to AST
        3. Delegates to differentiation specialist
        4. Formats and returns result

        Args:
            expr_str: Expression to differentiate (e.g., "x**2 + sin(x)")
            var: Variable to differentiate with respect to (default: 'x')

        Returns:
            Tuple of (success, result_string, method):
            - success: True if differentiation succeeded
            - result_string: String representation of derivative
            - method: "native_calculus" or error description
        """
        # Step 1: Validate safety
        is_safe, safety_error = check_expression_safety(expr_str)
        if not is_safe:
            return False, None, f"expression_rejected: {safety_error}"

        # Step 2: Parse to AST
        try:
            expr = self.parser.parse(expr_str)
            if expr is None:
                return False, None, "parse_failed"
        except Exception as e:
            logger.debug(f"Parse failed for '{expr_str}': {e}")
            return False, None, f"parse_error: {e}"

        # Step 3: Delegate to specialist
        try:
            result = self.diff_specialist.differentiate(expr, var)
            result_str = str(result)

            # Step 4: Format and return
            result_str = self._simplify_output(result_str)
            return True, result_str, "native_calculus"

        except Exception as e:
            logger.debug(f"Differentiation failed: {e}")
            return False, None, f"error: {e}"

    def integrate(self, expr_str: str, var: str = 'x') -> Tuple[bool, Optional[str], str]:
        """
        Integrate expression with respect to variable.

        This is the main entry point for integration. It:
        1. Validates expression safety
        2. Parses string to AST
        3. Delegates to integration specialist
        4. Formats and returns result

        Args:
            expr_str: Expression to integrate (e.g., "x**2", "sin(x)")
            var: Variable to integrate with respect to (default: 'x')

        Returns:
            Tuple of (success, result_string, method):
            - success: True if integration succeeded
            - result_string: String representation of antiderivative
            - method: "native_calculus" or error description
        """
        # Step 1: Validate safety
        is_safe, safety_error = check_expression_safety(expr_str)
        if not is_safe:
            return False, None, f"expression_rejected: {safety_error}"

        # Step 2: Parse to AST
        try:
            expr = self.parser.parse(expr_str)
            if expr is None:
                return False, None, "parse_failed"
        except Exception as e:
            logger.debug(f"Parse failed for '{expr_str}': {e}")
            return False, None, f"parse_error: {e}"

        # Step 3: Delegate to specialist
        try:
            result = self.int_specialist.integrate(expr, var)
            if result is None:
                return False, None, "no_antiderivative"

            # Step 4: Format and return
            result_str = str(result)
            result_str = self._simplify_output(result_str)
            return True, result_str, "native_calculus"

        except Exception as e:
            logger.debug(f"Integration failed: {e}")
            return False, None, f"error: {e}"

    def limit(self, expr_str: str, var: str, point: str) -> Tuple[bool, Optional[str], str]:
        """
        Evaluate limit of expression as variable approaches point.

        This is the main entry point for limit evaluation. It:
        1. Validates expression safety
        2. Parses string to AST
        3. Delegates to limit specialist
        4. Formats and returns result

        Args:
            expr_str: Expression to take limit of
            var: Variable name
            point: Limit point (e.g., "0", "oo", "-oo", "2")

        Returns:
            Tuple of (success, result_string, method):
            - success: True if limit was computed
            - result_string: Limit value or description
            - method: Method used or error description
        """
        # Step 1: Validate safety
        is_safe, safety_error = check_expression_safety(expr_str)
        if not is_safe:
            return False, None, f"expression_rejected: {safety_error}"

        # Step 2: Parse to AST
        try:
            expr = self.parser.parse(expr_str)
            if expr is None:
                return False, None, "parse_failed"
        except Exception as e:
            logger.debug(f"Parse failed for '{expr_str}': {e}")
            return False, None, f"parse_error: {e}"

        # Step 3: Delegate to specialist
        try:
            result = self.limit_specialist.limit(expr, var, point)
            return True, str(result), "native_calculus"

        except Exception as e:
            logger.debug(f"Limit evaluation failed: {e}")
            return False, None, f"error: {e}"

    def _simplify_output(self, s: str) -> str:
        """
        Clean up output string representation.

        TODO: Move this to calculus_utils.py once extraction is complete.
        """
        import re

        # Convert x**-1 to (1/x)
        def fix_negative_one_power(match):
            """Perform fix negative one power operation.

            Args:
            match: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.fix_negative_one_power(...)
            """
            var = match.group(1)
            return f"(1/{var})"

        s = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\*\*-1\b', fix_negative_one_power, s)

        # Remove 1* prefix
        s = re.sub(r'(?<!\*)\b1\*', '', s)
        # Remove *1 suffix
        s = re.sub(r'\*1\b', '', s)
        # Clean up **1
        s = re.sub(r'\*\*1\b', '', s)
        # Clean up 0 + or + 0
        s = re.sub(r'(?<![.\d])0 \+ ', '', s)
        s = re.sub(r' \+ 0(?![.\d])', '', s)
        # Clean up double negatives
        s = re.sub(r'--', '', s)

        return s


# Global supervisor instance (lazy-initialized)
_supervisor = None


def get_supervisor() -> CalculusSupervisor:
    """Get or create the global supervisor instance."""
    global _supervisor
    if _supervisor is None:
        _supervisor = CalculusSupervisor()
    return _supervisor


# Public API functions (backward compatibility)

def differentiate(expr_str: str, var: str = 'x') -> Tuple[bool, Optional[str], str]:
    """
    Differentiate expression (public API).

    This function maintains backward compatibility with the original
    native_calculus.py module.
    """
    return get_supervisor().differentiate(expr_str, var)


def integrate(expr_str: str, var: str = 'x') -> Tuple[bool, Optional[str], str]:
    """
    Integrate expression (public API).

    This function maintains backward compatibility with the original
    native_calculus.py module.
    """
    return get_supervisor().integrate(expr_str, var)


def limit(expr_str: str, var: str, point: str) -> Tuple[bool, Optional[str], str]:
    """
    Evaluate limit (public API).

    This function maintains backward compatibility with the original
    native_calculus.py module.
    """
    return get_supervisor().limit(expr_str, var, point)


# Aliases
native_derivative = differentiate
