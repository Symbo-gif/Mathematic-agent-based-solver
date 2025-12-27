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
Tests for WordProblemSupervisor

12-test pattern:
- 3 tests: Initialization and registration
- 4 tests: Routing to specialists
- 2 tests: Edge cases and fallback
- 3 tests: BDI methods
"""

import pytest
from symbo_agentic_reasoners.agents.supervisors.word_problem_supervisor import (
    WordProblemSupervisor,
    SupervisorResult
)


class TestWordProblemSupervisorInit:
    """Tests for initialization and registration."""

    def test_initialization_default(self):
        """Test default initialization."""
        supervisor = WordProblemSupervisor()
        assert supervisor.agent_id == 'word_problem_supervisor_001'
        assert supervisor.df is None
        assert supervisor.blackboard is None

    def test_initialization_custom_id(self):
        """Test initialization with custom agent ID."""
        supervisor = WordProblemSupervisor(agent_id='wp_custom_001')
        assert supervisor.agent_id == 'wp_custom_001'

    def test_statistics_initial(self):
        """Test initial statistics."""
        supervisor = WordProblemSupervisor()
        stats = supervisor.get_statistics()
        assert stats['tasks_routed'] == 0
        assert stats['tasks_completed'] == 0


class TestWordProblemSupervisorRouting:
    """Tests for routing to specialists."""

    def test_route_to_arithmetic(self):
        """Test routing to arithmetic specialist."""
        supervisor = WordProblemSupervisor()
        result = supervisor.solve_word_problem("5 apples and 3 oranges. How many total?")
        assert result['success'] is True
        assert result['answer'] == 8.0

    def test_route_to_rtd(self):
        """Test routing classification to rate-time-distance specialist."""
        supervisor = WordProblemSupervisor()
        # Test that RTD keywords trigger RTD classification
        problem_type = supervisor._classify_problem("A car travels at 60 mph for 2 hours. How far?")
        assert problem_type == 'rate_time_distance'

    def test_route_to_purchase(self):
        """Test routing to purchase specialist."""
        supervisor = WordProblemSupervisor()
        result = supervisor.solve_word_problem("John buys 3 items at $4 each. Total cost?")
        assert result['success'] is True
        assert result['answer'] == 12.0
        assert result['specialist'] == 'purchase_pattern'

    def test_route_to_proportion(self):
        """Test routing proportion problems (may use pipeline or proportion specialist)."""
        supervisor = WordProblemSupervisor()
        result = supervisor.solve_word_problem("Tom has twice as many as Mary. Mary has 5.")
        assert result['success'] is True
        assert result['answer'] is not None
        # May be routed to reasoning_pipeline (for comparative) or proportion specialist
        assert result['specialist'] in ['proportion', 'reasoning_pipeline']


class TestWordProblemSupervisorEdgeCases:
    """Tests for edge cases and fallback."""

    def test_classify_problem_default(self):
        """Test default classification."""
        supervisor = WordProblemSupervisor()
        problem_type = supervisor._classify_problem("Some numbers 5 and 3")
        assert problem_type == 'arithmetic'  # Default fallback

    def test_fallback_to_arithmetic(self):
        """Test fallback mechanism."""
        supervisor = WordProblemSupervisor()
        # Force fallback by providing ambiguous problem
        result = supervisor._fallback_to_arithmetic("5 and 3 together")
        assert result.get('specialist') == 'arithmetic_fallback'


class TestWordProblemSupervisorBDI:
    """Tests for BDI methods."""

    def test_update_beliefs(self):
        """Test belief update after routing."""
        supervisor = WordProblemSupervisor()
        supervisor.solve_word_problem("5 + 3 total?")
        supervisor.update_beliefs()
        assert 'tasks_routed' in supervisor.beliefs

    def test_deliberate_no_blackboard(self):
        """Test deliberation without blackboard."""
        supervisor = WordProblemSupervisor()
        intentions = supervisor.deliberate()
        assert intentions == []

    def test_execute_step_empty(self):
        """Test execute step with no intentions."""
        supervisor = WordProblemSupervisor()
        result = supervisor.execute_step()
        assert result is None
