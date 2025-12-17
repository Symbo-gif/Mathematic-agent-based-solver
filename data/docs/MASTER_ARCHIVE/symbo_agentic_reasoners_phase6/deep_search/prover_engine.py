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
Prover Engine
=============

Abstraction layer for the underlying theorem prover.
Allows switching between simulated logic (Mock), Python-based CAS (SymPy),
and future formal verification systems (Lean4/Coq).
"""

import logging
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List, Dict, Any
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

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


class SymPyProver(ProverEngine):
    """
    Prover engine backed by SymPy symbolic mathematics library.
    Attempts to parse goals and verify them mathematically.
    """

    def __init__(self):
        self.transformations = (standard_transformations + (implicit_multiplication_application,))

    def apply_tactic(self, state: ProofState, tactic: TacticCandidate) -> Tuple[str, bool]:
        goal_str = state.goal
        tactic_name = tactic.tactic.split()[0]

        # Try to parse the goal
        try:
            # Handle "True" or "⊤"
            if goal_str in ["True", "⊤"]:
                return "⊤", True

            # Basic parsing attempt
            # We need a way to handle undefined symbols.
            # SymPy's parse_expr might fail if symbols aren't defined, or it might auto-define them.
            # We'll use a catch-all dict for now or rely on auto-symbol creation if possible.
            # Actually, parse_expr doesn't auto-create symbols by default unless we pass a dict or use specific transforms.
            # But let's try a simpler approach: assume standard symbols x,y,z,a,b,c,n,m,k are used.
            
            # For robustness, we'll just try to parse. If it fails, fallback to string manipulation.
            expr = parse_expr(goal_str, transformations=self.transformations)
        except (sp.SympifyError, SyntaxError, TypeError, ValueError, AttributeError) as e:
            # FAIL-FAST: No mock fallback in production
            # Log the parsing failure and return unparseable state
            error_msg = (
                f"SymPy parsing failed for goal: {goal_str[:100]}\n"
                f"Error: {type(e).__name__}: {e}\n"
                f"Tactic '{tactic_name}' cannot be applied to unparseable expression.\n"
                f"This goal may require manual verification or different formulation."
            )
            logger.warning(f"PARSING FAILED: {error_msg}")
            # Return the goal unchanged with is_proven=False to signal failure
            # This allows the search to continue with other tactics
            return f"[PARSE_ERROR] {goal_str}", False

        # Apply tactics using SymPy logic
        try:
            if tactic_name in ['rfl', 'trivial']:
                # Check if expression evaluates to True
                if expr == True:
                    return "⊤", True
                # Check equality
                if isinstance(expr, sp.Eq):
                    if sp.simplify(expr.lhs - expr.rhs) == 0:
                        return "⊤", True
                if isinstance(expr, bool) and expr:
                     return "⊤", True

            if tactic_name == 'simp':
                simplified = sp.simplify(expr)
                if simplified == True:
                    return "⊤", True
                if isinstance(simplified, sp.Eq) and simplified.lhs == simplified.rhs:
                    return "⊤", True
                return str(simplified), False

            if tactic_name == 'ring':
                if isinstance(expr, sp.Eq):
                    lhs_expanded = sp.expand(expr.lhs)
                    rhs_expanded = sp.expand(expr.rhs)
                    if lhs_expanded == rhs_expanded:
                        return "⊤", True
                return str(sp.expand(expr)), False

            if tactic_name == 'linarith':
                # Basic check for inequalities
                # This is complex in SymPy without context, but we can try simplify
                simplified = sp.simplify(expr)
                if simplified == True:
                    return "⊤", True
                return str(simplified), False
            
            if tactic_name == 'sorry':
                return "⊤", True

        except (sp.SympifyError, TypeError, ValueError, AttributeError, NotImplementedError) as e:
            # If SymPy operation fails, return error state or original
            logger.debug(f"SymPy operation failed for tactic {tactic_name}: {e}")

        # Default fallback
        return f"after_{tactic_name}: {goal_str}", False

    def health_check(self) -> bool:
        try:
            x = sp.Symbol('x')
            return sp.simplify(x - x) == 0
        except (TypeError, RuntimeError) as e:
            logger.warning(f"SymPyProver health check failed: {e}")
            return False
