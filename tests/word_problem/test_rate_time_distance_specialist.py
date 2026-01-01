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
Tests for RateTimeDistanceSpecialist

12-test pattern:
- 3 tests: Initialization and registration
- 4 tests: Core problem solving (d, r, t)
- 2 tests: Edge cases
- 3 tests: BDI methods
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.word_problem.rate_time_distance_specialist import (
    RateTimeDistanceSpecialist,
    RTDResult,
    RTDVariable
)


class TestRTDSpecialistInit:
    """Tests for initialization and registration."""

    def test_initialization_default(self):
        """Test default initialization."""
        specialist = RateTimeDistanceSpecialist()
        assert specialist.agent_id == 'rate_time_distance_specialist_001'
        assert specialist.df is None
        assert specialist.blackboard is None

    def test_initialization_custom_id(self):
        """Test initialization with custom agent ID."""
        specialist = RateTimeDistanceSpecialist(agent_id='rtd_custom_001')
        assert specialist.agent_id == 'rtd_custom_001'

    def test_statistics_initial(self):
        """Test initial statistics are zero."""
        specialist = RateTimeDistanceSpecialist()
        stats = specialist.get_statistics()
        assert stats['problems_solved'] == 0
        assert stats['problems_succeeded'] == 0


class TestRTDSpecialistSolve:
    """Tests for core problem solving."""

    def test_solve_find_distance(self):
        """Test finding distance with clear pattern."""
        specialist = RateTimeDistanceSpecialist()
        # Simple extraction test
        segment = specialist._simple_extraction("60 mph for 3 hours")
        assert segment.rate == 60.0
        assert segment.time == 3.0

    def test_solve_find_time_classification(self):
        """Test time variable identification."""
        specialist = RateTimeDistanceSpecialist()
        unknown = specialist._identify_unknown("How long does it take?")
        assert unknown == RTDVariable.TIME

    def test_solve_find_rate_classification(self):
        """Test rate variable identification."""
        specialist = RateTimeDistanceSpecialist()
        unknown = specialist._identify_unknown("How fast did it go?")
        assert unknown == RTDVariable.RATE

    def test_solve_with_direct_values(self):
        """Test solving with pre-populated segment."""
        specialist = RateTimeDistanceSpecialist()
        from symbo_agentic_reasoners.agents.specialists.word_problem.rate_time_distance_specialist import JourneySegment
        segment = JourneySegment(rate=60.0, time=2.0)
        answer, expr = specialist._solve_rtd([segment], RTDVariable.DISTANCE)
        assert answer == 120.0


class TestRTDSpecialistEdgeCases:
    """Tests for edge cases."""

    def test_identify_unknown_default(self):
        """Test default unknown identification."""
        specialist = RateTimeDistanceSpecialist()
        unknown = specialist._identify_unknown("Some problem without clear question")
        assert unknown == RTDVariable.DISTANCE  # Default

    def test_simple_extraction(self):
        """Test simple number extraction."""
        specialist = RateTimeDistanceSpecialist()
        segment = specialist._simple_extraction("60 mph for 2 hours")
        assert segment.rate == 60.0
        assert segment.time == 2.0


class TestRTDSpecialistBDI:
    """Tests for BDI methods."""

    def test_update_beliefs(self):
        """Test belief update."""
        specialist = RateTimeDistanceSpecialist()
        specialist._problems_solved = 1
        specialist.update_beliefs()
        assert 'problems_solved' in specialist.beliefs

    def test_deliberate_no_blackboard(self):
        """Test deliberation without blackboard."""
        specialist = RateTimeDistanceSpecialist()
        intentions = specialist.deliberate()
        assert intentions == []

    def test_execute_step_empty(self):
        """Test execute step with no intentions."""
        specialist = RateTimeDistanceSpecialist()
        result = specialist.execute_step()
        assert result is None
