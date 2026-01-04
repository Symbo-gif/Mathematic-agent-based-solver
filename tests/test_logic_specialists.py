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
Logic Specialist Tests
======================

Comprehensive tests for logic specialist agents:
- PredicateSpecialist
- ProofSpecialist
- PropositionalSpecialist
"""

import pytest
from unittest.mock import Mock, MagicMock


# =============================================================================
# PredicateSpecialist Tests
# =============================================================================


class TestPredicateLogicSpecialist:
    """Tests for PredicateLogicSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create PredicateLogicSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import (
            PredicateLogicSpecialist
        )
        return PredicateLogicSpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_has_execute_step_method(self, specialist):
        """Should have execute_step method."""
        assert hasattr(specialist, 'execute_step')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# ProofSpecialist Tests
# =============================================================================


class TestProofSpecialist:
    """Tests for ProofSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create ProofSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.logic.proof_specialist import (
            ProofSpecialist
        )
        return ProofSpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# PropositionalSpecialist Tests
# =============================================================================


class TestPropositionalLogicSpecialist:
    """Tests for PropositionalLogicSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create PropositionalLogicSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import (
            PropositionalLogicSpecialist
        )
        return PropositionalLogicSpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
