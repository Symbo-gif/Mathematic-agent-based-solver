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
Mock Prover for Testing
=======================

This mock prover is ONLY for testing purposes.
It should NEVER be used in production code.

Usage in tests:
    from tests.mocks.mock_prover import MockProver

    prover = MockProver()
    result, is_proven = prover.apply_tactic(state, tactic)
"""

import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger('symbo_agentic_reasoners.tests.mocks.prover')


class MockProver:
    """
    Simulated prover using string heuristics for testing.

    WARNING: This is for TESTING ONLY. Production code should use
    SymPyProver or other real prover implementations.

    This mock simulates tactic application using simple string heuristics,
    allowing testing of the proof search infrastructure without requiring
    actual theorem proving capabilities.
    """

    def __init__(self):
        """Initialize mock prover"""
        self.tactics_applied = 0
        self.proofs_completed = 0
        logger.warning("MockProver initialized - FOR TESTING ONLY")

    def apply_tactic(self, state, tactic) -> Tuple[str, bool]:
        """
        Apply a tactic to a proof state (mock implementation).

        Args:
            state: Current proof state (ProofState object)
            tactic: Tactic to apply (TacticCandidate object)

        Returns:
            Tuple of (new_goal_string, is_proven_boolean)
        """
        self.tactics_applied += 1
        goal = state.goal
        tactic_name = tactic.tactic.split()[0]

        # Simulate tactic effects using string heuristics
        if tactic_name in ['rfl', 'trivial']:
            if '=' in goal and self._is_reflexive(goal):
                self.proofs_completed += 1
                return "⊤", True

        if tactic_name == 'simp':
            new_goal = f"[simp] {goal}"
            return new_goal, False

        if tactic_name == 'ring':
            if self._looks_algebraic(goal):
                self.proofs_completed += 1
                return "⊤", True

        if tactic_name in ['linarith', 'omega']:
            if self._looks_linear(goal):
                self.proofs_completed += 1
                return "⊤", True

        if tactic_name == 'intro':
            if '∀' in goal or 'forall' in goal.lower():
                new_goal = goal.replace('∀', '', 1).replace('forall', '', 1)
                return new_goal.strip(), False

        if tactic_name == 'constructor':
            if '∧' in goal or 'and' in goal.lower():
                return f"subgoal_1 of {goal[:30]}...", False

        if tactic_name == 'induction':
            return f"base_case of {goal[:30]}...", False

        if tactic_name == 'sorry':
            self.proofs_completed += 1
            return "⊤", True

        return f"after_{tactic_name}: {goal[:50]}...", False

    def _is_reflexive(self, goal: str) -> bool:
        """Check if goal is reflexive (x = x)"""
        if '=' not in goal:
            return False
        parts = goal.split('=')
        if len(parts) == 2:
            return parts[0].strip() == parts[1].strip()
        return False

    def _looks_algebraic(self, goal: str) -> bool:
        """Check if goal looks like an algebraic expression"""
        return '=' in goal and any(op in goal for op in ['+', '*', '-', '^'])

    def _looks_linear(self, goal: str) -> bool:
        """Check if goal looks like a linear arithmetic expression"""
        return any(op in goal for op in ['<', '>', '≤', '≥']) or \
               (all(c in '0123456789+-*()=<>xyz ' for c in goal.lower()))

    def health_check(self) -> bool:
        """Mock health check - always returns True"""
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get mock prover statistics"""
        return {
            'tactics_applied': self.tactics_applied,
            'proofs_completed': self.proofs_completed,
            'mock': True,
            'warning': 'This is a mock prover - not real theorem proving'
        }

    def __repr__(self) -> str:
        return "MockProver(TESTING ONLY)"

    def __str__(self) -> str:
        return "Mock Prover for testing (WARNING: NOT FOR PRODUCTION USE)"
