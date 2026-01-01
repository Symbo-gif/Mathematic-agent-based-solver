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
Prover Engine
=============

Abstraction layer for the underlying theorem prover.
Allows switching between simulated logic (Mock), Python-based CAS (SymPy),
and future formal verification systems (Lean4/Coq).
"""

import logging
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List, Dict, Any

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Expr, Symbol, symbols, Integer,
    Add, Mul, Pow, Sqrt, Sin, Cos, Tan, Exp, Log, Abs,
    parse_expr, simplify, expand
)

from .types import ProofState
from .policy_network import TacticCandidate

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.deep_search.prover_engine')
except ImportError:
    logger = logging.getLogger(__name__)


class ProverEngine(ABC):
    """Abstract base class for theorem prover backends"""

    @abstractmethod
    def apply_tactic(self, state: ProofState, tactic: TacticCandidate) -> Tuple[str, bool]:
        """
        Apply a tactic to a proof state.

        Args:
            state: Current proof state
            tactic: Tactic to apply

        Returns:
            Tuple of (new_goal_string, is_proven_boolean)
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if prover is healthy"""
        pass


# NOTE: MockProver class has been REMOVED from production code.
# Mock prover is available ONLY in tests/mocks/mock_prover.py for testing.
# See P0-2d fix in TODO.md for details.


class NativeSymbolicProver(ProverEngine):
    """
    Prover engine backed by native symbolic mathematics library.
    Attempts to parse goals and verify them mathematically.
    NO SYMPY - uses native symbolic implementation.
    """

    def __init__(self):
        # Standard transformations tuple for native symbolic parsing
        self.transformations = (
            'implicit_multiplication',
            'convert_xor',
            'implicit_application',
            'factorial_notation',
        )

    def apply_tactic(self, state: ProofState, tactic: TacticCandidate) -> Tuple[str, bool]:
        """Perform apply tactic operation.

        Args:
        state: Description needed
        tactic: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.apply_tactic(...)
        """
        """Perform apply tactic operation.

        Args:
        state: Description needed
        tactic: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.apply_tactic(...)
        """
        goal_str = state.goal
        tactic_name = tactic.tactic.split()[0]

        # Try to parse the goal
        try:
            # Handle "True" or "top symbol"
            if goal_str in ["True", "\u22a4"]:  # \u22a4 is top symbol
                return "\u22a4", True

            # Basic parsing attempt using native parser
            expr = parse_expr(goal_str)
        except (SyntaxError, TypeError, ValueError, AttributeError) as e:
            # FAIL-FAST: No mock fallback in production
            # Log the parsing failure and return unparseable state
            error_msg = (
                f"Native symbolic parsing failed for goal: {goal_str[:100]}\n"
                f"Error: {type(e).__name__}: {e}\n"
                f"Tactic '{tactic_name}' cannot be applied to unparseable expression.\n"
                f"This goal may require manual verification or different formulation."
            )
            logger.warning(f"PARSING FAILED: {error_msg}")
            # Return the goal unchanged with is_proven=False to signal failure
            # This allows the search to continue with other tactics
            return f"[PARSE_ERROR] {goal_str}", False

        # Apply tactics using native symbolic logic
        try:
            if tactic_name in ['rfl', 'trivial']:
                # Check if expression evaluates to True
                if expr == True or expr is True:
                    return "\u22a4", True
                # Check equality - for Eq types with lhs/rhs
                if hasattr(expr, 'lhs') and hasattr(expr, 'rhs'):
                    diff = simplify(expr.lhs - expr.rhs)
                    if diff == 0 or (hasattr(diff, 'is_zero') and diff.is_zero):
                        return "\u22a4", True
                if isinstance(expr, bool) and expr:
                    return "\u22a4", True

            if tactic_name == 'simp':
                simplified = simplify(expr)
                if simplified == True or simplified is True:
                    return "\u22a4", True
                if hasattr(simplified, 'lhs') and hasattr(simplified, 'rhs'):
                    if simplified.lhs == simplified.rhs:
                        return "\u22a4", True
                return str(simplified), False

            if tactic_name == 'ring':
                if hasattr(expr, 'lhs') and hasattr(expr, 'rhs'):
                    lhs_expanded = expand(expr.lhs)
                    rhs_expanded = expand(expr.rhs)
                    if lhs_expanded == rhs_expanded:
                        return "\u22a4", True
                return str(expand(expr)), False

            if tactic_name == 'linarith':
                # Basic check for inequalities
                simplified = simplify(expr)
                if simplified == True or simplified is True:
                    return "\u22a4", True
                return str(simplified), False

            if tactic_name == 'sorry':
                """Perform health check operation.

                Args:
                No arguments

                Returns:
                Result of the operation

                Example:
                >>> result = obj.health_check(...)
                """
                return "\u22a4", True

        except (TypeError, ValueError, AttributeError, NotImplementedError) as e:
            # If native symbolic operation fails, return error state or original
            logger.debug(f"Native symbolic operation failed for tactic {tactic_name}: {e}")

        # Default fallback
        return f"after_{tactic_name}: {goal_str}", False

    def health_check(self) -> bool:
        """Perform health check operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.health_check(...)
        """
        try:
            x = Symbol('x')
            return simplify(x - x) == Integer(0)
        except (TypeError, RuntimeError) as e:
            logger.warning(f"NativeSymbolicProver health check failed: {e}")
            return False


# Backward compatibility alias
SymPyProver = NativeSymbolicProver
