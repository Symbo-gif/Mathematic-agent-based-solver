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
Tests for ArithmeticWordProblemSpecialist

12-test pattern:
- 3 tests: Initialization and registration
- 4 tests: Core problem solving
- 2 tests: Edge cases
- 3 tests: BDI methods
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.word_problem.arithmetic_word_problem_specialist import (
    ArithmeticWordProblemSpecialist,
    ArithmeticResult
)


class TestArithmeticWordProblemSpecialistInit:
    """Tests for initialization and registration."""

    def test_initialization_default(self):
        """Test default initialization."""
        specialist = ArithmeticWordProblemSpecialist()
        assert specialist.agent_id == 'arithmetic_word_problem_specialist_001'
        assert specialist.df is None
        assert specialist.blackboard is None
        assert specialist._problems_solved == 0

    def test_initialization_custom_id(self):
        """Test initialization with custom agent ID."""
        specialist = ArithmeticWordProblemSpecialist(agent_id='custom_arith_001')
        assert specialist.agent_id == 'custom_arith_001'

    def test_statistics_initial(self):
        """Test initial statistics are zero."""
        specialist = ArithmeticWordProblemSpecialist()
        stats = specialist.get_statistics()
        assert stats['problems_solved'] == 0
        assert stats['problems_succeeded'] == 0
        assert stats['problems_failed'] == 0


class TestArithmeticWordProblemSpecialistSolve:
    """Tests for core problem solving."""

    def test_solve_addition(self):
        """Test addition word problem."""
        specialist = ArithmeticWordProblemSpecialist()
        result = specialist.solve("John has 5 apples and Mary has 3 apples. How many apples altogether?")
        assert result.answer == 8.0
        assert 'add' in result.operations_inferred
        assert '+' in result.expression

    def test_solve_subtraction(self):
        """Test subtraction word problem."""
        specialist = ArithmeticWordProblemSpecialist()
        result = specialist.solve("Tom had 10 cookies and gave away 4. How many are left?")
        assert result.answer == 6.0
        assert 'subtract' in result.operations_inferred

    def test_solve_multiplication(self):
        """Test multiplication word problem."""
        specialist = ArithmeticWordProblemSpecialist()
        result = specialist.solve("There are 4 groups of 5 students each. What is the total?")
        assert result.answer == 20.0
        assert 'multiply' in result.operations_inferred

    def test_solve_division(self):
        """Test division word problem."""
        specialist = ArithmeticWordProblemSpecialist()
        result = specialist.solve("12 candies are divided equally among 3 children. How many each?")
        assert result.answer == 4.0
        assert 'divide' in result.operations_inferred


class TestArithmeticWordProblemSpecialistEdgeCases:
    """Tests for edge cases."""

    def test_single_number(self):
        """Test problem with single number."""
        specialist = ArithmeticWordProblemSpecialist()
        result = specialist.solve("John has 5 apples.")
        assert result.answer == 5.0
        assert result.confidence < 1.0

    def test_word_numbers(self):
        """Test extraction of word numbers."""
        specialist = ArithmeticWordProblemSpecialist()
        numbers = specialist._extract_numbers("I have five apples and three oranges")
        assert 5.0 in numbers
        assert 3.0 in numbers


class TestArithmeticWordProblemSpecialistBDI:
    """Tests for BDI methods."""

    def test_update_beliefs(self):
        """Test belief update after solving."""
        specialist = ArithmeticWordProblemSpecialist()
        specialist.solve("5 + 3 = ? How many total?")
        specialist.update_beliefs()
        assert 'problems_solved' in specialist.beliefs
        # Check that beliefs are updated (content may vary based on tracking)

    def test_deliberate_no_blackboard(self):
        """Test deliberation without blackboard."""
        specialist = ArithmeticWordProblemSpecialist()
        intentions = specialist.deliberate()
        assert intentions == []

    def test_execute_step_empty(self):
        """Test execute step with no intentions."""
        specialist = ArithmeticWordProblemSpecialist()
        result = specialist.execute_step()
        assert result is None
