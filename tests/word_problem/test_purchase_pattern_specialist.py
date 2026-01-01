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
Tests for PurchasePatternSpecialist

12-test pattern:
- 3 tests: Initialization and registration
- 4 tests: Core problem solving
- 2 tests: Edge cases
- 3 tests: BDI methods
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.word_problem.purchase_pattern_specialist import (
    PurchasePatternSpecialist,
    PurchaseResult,
    PurchaseItem
)


class TestPurchasePatternSpecialistInit:
    """Tests for initialization and registration."""

    def test_initialization_default(self):
        """Test default initialization."""
        specialist = PurchasePatternSpecialist()
        assert specialist.agent_id == 'purchase_pattern_specialist_001'
        assert specialist.df is None

    def test_initialization_custom_id(self):
        """Test initialization with custom agent ID."""
        specialist = PurchasePatternSpecialist(agent_id='purchase_custom_001')
        assert specialist.agent_id == 'purchase_custom_001'

    def test_statistics_initial(self):
        """Test initial statistics."""
        specialist = PurchasePatternSpecialist()
        stats = specialist.get_statistics()
        assert stats['problems_solved'] == 0


class TestPurchasePatternSpecialistSolve:
    """Tests for core problem solving."""

    def test_solve_total_cost(self):
        """Test total cost calculation."""
        specialist = PurchasePatternSpecialist()
        result = specialist.solve("John buys 5 apples at $2 each. What is the total cost?")
        assert result.answer == 10.0
        assert result.problem_type == 'total_cost'

    def test_solve_with_dollar_sign(self):
        """Test problem with dollar sign."""
        specialist = PurchasePatternSpecialist()
        result = specialist.solve("Mary paid $3 for 6 oranges.")
        assert result.answer == 18.0

    def test_solve_change_calculation(self):
        """Test change calculation."""
        specialist = PurchasePatternSpecialist()
        result = specialist.solve("Tom buys 4 items at $3 each and pays $20. How much change?")
        assert result.answer == 8.0
        assert result.problem_type == 'change'

    def test_identify_problem_type(self):
        """Test problem type identification."""
        specialist = PurchasePatternSpecialist()
        assert specialist._identify_problem_type("total cost") == 'total_cost'
        # Change detection requires 'pay' keyword + 'change' keyword
        assert specialist._identify_problem_type("paid and got change back") == 'change'


class TestPurchasePatternSpecialistEdgeCases:
    """Tests for edge cases."""

    def test_extract_items_with_pattern(self):
        """Test item extraction."""
        specialist = PurchasePatternSpecialist()
        items = specialist._extract_items("5 apples at $2 each")
        assert len(items) >= 1
        assert items[0].quantity == 5.0 or items[0].unit_price == 2.0

    def test_simple_extraction(self):
        """Test simple extraction fallback."""
        specialist = PurchasePatternSpecialist()
        items = specialist._simple_extraction("$10 for 2 items")
        assert len(items) >= 1


class TestPurchasePatternSpecialistBDI:
    """Tests for BDI methods."""

    def test_update_beliefs(self):
        """Test belief update."""
        specialist = PurchasePatternSpecialist()
        specialist.solve("5 items at $2")
        specialist.update_beliefs()
        assert 'problems_solved' in specialist.beliefs

    def test_deliberate_no_blackboard(self):
        """Test deliberation without blackboard."""
        specialist = PurchasePatternSpecialist()
        intentions = specialist.deliberate()
        assert intentions == []

    def test_execute_step_empty(self):
        """Test execute step with no intentions."""
        specialist = PurchasePatternSpecialist()
        result = specialist.execute_step()
        assert result is None
