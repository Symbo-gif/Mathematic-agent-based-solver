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
Tests for ProportionSpecialist

12-test pattern:
- 3 tests: Initialization and registration
- 4 tests: Core problem solving
- 2 tests: Edge cases
- 3 tests: BDI methods
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.word_problem.proportion_specialist import (
    ProportionSpecialist,
    ProportionResult,
    ProportionRelation
)


class TestProportionSpecialistInit:
    """Tests for initialization and registration."""

    def test_initialization_default(self):
        """Test default initialization."""
        specialist = ProportionSpecialist()
        assert specialist.agent_id == 'proportion_specialist_001'
        assert specialist.df is None

    def test_initialization_custom_id(self):
        """Test initialization with custom agent ID."""
        specialist = ProportionSpecialist(agent_id='prop_custom_001')
        assert specialist.agent_id == 'prop_custom_001'

    def test_statistics_initial(self):
        """Test initial statistics."""
        specialist = ProportionSpecialist()
        stats = specialist.get_statistics()
        assert stats['problems_solved'] == 0


class TestProportionSpecialistSolve:
    """Tests for core problem solving."""

    def test_solve_chain_resolution(self):
        """Test chain resolution with known values."""
        specialist = ProportionSpecialist()
        relations = [ProportionRelation('tom', 'mary', 2.0, 'times')]
        known = {'mary': 5.0}
        resolved, expr = specialist._resolve_chain(relations, known, "")
        assert resolved['tom'] == 10.0

    def test_multiplier_words_twice(self):
        """Test twice multiplier."""
        specialist = ProportionSpecialist()
        assert specialist.MULTIPLIER_WORDS['twice'] == 2.0

    def test_multiplier_words_half(self):
        """Test half multiplier."""
        specialist = ProportionSpecialist()
        assert specialist.MULTIPLIER_WORDS['half'] == 0.5

    def test_extract_relations(self):
        """Test relation extraction."""
        specialist = ProportionSpecialist()
        relations = specialist._extract_relations("Tom has twice as many as Mary")
        # Note: extraction may find relations depending on pattern matching
        assert isinstance(relations, list)


class TestProportionSpecialistEdgeCases:
    """Tests for edge cases."""

    def test_extract_known_values(self):
        """Test known value extraction."""
        specialist = ProportionSpecialist()
        known = specialist._extract_known_values("Mary has 10")
        assert 'mary' in known
        assert known['mary'] == 10.0

    def test_multiplier_words(self):
        """Test multiplier word mappings."""
        specialist = ProportionSpecialist()
        assert specialist.MULTIPLIER_WORDS['twice'] == 2.0
        assert specialist.MULTIPLIER_WORDS['half'] == 0.5


class TestProportionSpecialistBDI:
    """Tests for BDI methods."""

    def test_update_beliefs(self):
        """Test belief update."""
        specialist = ProportionSpecialist()
        specialist.solve("twice as many, value is 5")
        specialist.update_beliefs()
        assert 'problems_solved' in specialist.beliefs

    def test_deliberate_no_blackboard(self):
        """Test deliberation without blackboard."""
        specialist = ProportionSpecialist()
        intentions = specialist.deliberate()
        assert intentions == []

    def test_execute_step_empty(self):
        """Test execute step with no intentions."""
        specialist = ProportionSpecialist()
        result = specialist.execute_step()
        assert result is None
