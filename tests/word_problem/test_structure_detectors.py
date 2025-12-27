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
Unit tests for structure_detectors.py

Tests the StructureDetector class that detects multi-step
problem structure types.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.structure_detectors import (
    StructureDetector, StructureType, StructureMatch, SegmentInfo
)


class TestStructureType:
    """Tests for StructureType enum."""

    def test_all_types_defined(self):
        """Verify all expected structure types exist."""
        expected_types = [
            'SINGLE_STEP', 'SEQUENTIAL_CHAIN', 'ITERATIVE_RATE',
            'CONDITIONAL_TIERED', 'RELATIONAL_CHAIN',
            'REMAINDER_PERCENTAGE', 'BACKWARD_INFERENCE'
        ]
        for type_name in expected_types:
            assert hasattr(StructureType, type_name)

    def test_type_values(self):
        """Test structure type string values."""
        assert StructureType.SINGLE_STEP.value == "single_step"
        assert StructureType.SEQUENTIAL_CHAIN.value == "sequential_chain"
        assert StructureType.ITERATIVE_RATE.value == "iterative_rate"


class TestStructureDetector:
    """Tests for StructureDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a StructureDetector instance."""
        return StructureDetector()

    # Single-step detection tests
    def test_detect_single_step_simple(self, detector):
        """Test detection of simple single-step problems."""
        text = "What is 5 + 3?"
        stype, confidence = detector.detect(text)
        assert stype == StructureType.SINGLE_STEP
        assert confidence > 0.7

    def test_detect_single_step_multiplication(self, detector):
        """Test single-step multiplication."""
        text = "Calculate 12 times 4."
        stype, confidence = detector.detect(text)
        # May be single-step or iterative depending on interpretation
        assert stype in [StructureType.SINGLE_STEP, StructureType.ITERATIVE_RATE]

    # Sequential chain detection tests
    def test_detect_sequential_first_then(self, detector):
        """Test sequential detection with 'first...then' pattern."""
        text = "John had 10 apples. First he ate 3, then he bought 5 more."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.SEQUENTIAL_CHAIN
        assert confidence > 0.5

    def test_detect_sequential_started_with(self, detector):
        """Test sequential with 'started with...then' pattern."""
        text = "She started with 100 dollars. Then she spent 30 and later earned 50."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.SEQUENTIAL_CHAIN
        assert confidence > 0.5

    def test_detect_sequential_ate_gave(self, detector):
        """Test sequential with action verb sequence."""
        text = "Tom has 12 cookies. He ate 4. Then gave 3 to his sister."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.SEQUENTIAL_CHAIN

    def test_detect_sequential_comma_then(self, detector):
        """Test sequential with comma-then pattern."""
        text = "Janet has 16 eggs. She eats 3, then bakes 4 into a cake."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.SEQUENTIAL_CHAIN

    # Iterative rate detection tests
    def test_detect_iterative_per_day(self, detector):
        """Test iterative rate with 'per day' pattern."""
        text = "He earns $50 per day for 5 days."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.ITERATIVE_RATE
        assert confidence > 0.5

    def test_detect_iterative_each_hour(self, detector):
        """Test iterative rate with 'each hour' pattern."""
        text = "The factory produces 100 units each hour. How many in 8 hours?"
        stype, confidence = detector.detect(text)
        assert stype == StructureType.ITERATIVE_RATE

    def test_detect_iterative_weekly(self, detector):
        """Test iterative rate with weekly pattern."""
        text = "She saves $200 every week for 12 weeks."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.ITERATIVE_RATE

    # Conditional tiered detection tests
    def test_detect_conditional_overtime(self, detector):
        """Test conditional with overtime pattern."""
        text = "He works 50 hours. First 40 hours at $10/hr, overtime at $15/hr."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.CONDITIONAL_TIERED
        assert confidence > 0.4

    def test_detect_conditional_first_rest(self, detector):
        """Test conditional with first/rest pattern."""
        text = "First 100 items cost $5 each. The rest cost $3 each."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.CONDITIONAL_TIERED

    # Relational chain detection tests
    def test_detect_relational_times_as_many(self, detector):
        """Test relational with 'times as many' pattern."""
        text = "Mary has 3 times as many apples as John. John has 4 apples."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.RELATIONAL_CHAIN
        assert confidence > 0.4

    def test_detect_relational_twice(self, detector):
        """Test relational with 'twice as much' pattern."""
        text = "Tom has twice as much money as Jane. Jane has $50."
        stype, confidence = detector.detect(text)
        assert stype == StructureType.RELATIONAL_CHAIN

    # Backward inference detection tests
    def test_detect_backward_has_left(self, detector):
        """Test backward inference with 'has X left' pattern."""
        text = "After spending some money, John has $25 left. He started with how much?"
        stype, confidence = detector.detect(text)
        assert stype == StructureType.BACKWARD_INFERENCE
        assert confidence > 0.4

    def test_detect_backward_ended_up(self, detector):
        """Test backward inference with 'ended up with' pattern."""
        text = "She ended up with 10 cookies after eating 5. How many did she start with?"
        stype, confidence = detector.detect(text)
        assert stype == StructureType.BACKWARD_INFERENCE

    # Segment boundary tests
    def test_get_segment_boundaries_single(self, detector):
        """Test segment boundaries for single-step problem."""
        text = "What is 5 + 3?"
        boundaries = detector.get_segment_boundaries(text, StructureType.SINGLE_STEP)
        assert len(boundaries) == 1
        assert boundaries[0] == (0, len(text))

    def test_get_segment_boundaries_sequential(self, detector):
        """Test segment boundaries for sequential problem."""
        text = "John has 10 apples. He ate 3. Then he bought 5."
        boundaries = detector.get_segment_boundaries(text, StructureType.SEQUENTIAL_CHAIN)
        assert len(boundaries) >= 2

    # Segment extraction tests
    def test_get_segments(self, detector):
        """Test full segment extraction."""
        text = "She has 20 dollars. She spends 5. Then earns 10 more."
        segments = detector.get_segments(text)
        assert len(segments) >= 2
        assert all(isinstance(s, SegmentInfo) for s in segments)

    def test_get_segments_operation_hints(self, detector):
        """Test operation hint detection in segments."""
        text = "Tom had 15 marbles. He lost 3. Then found 7 more."
        segments = detector.get_segments(text)
        operations = [s.operation_hint for s in segments if s.operation_hint]
        assert 'subtract' in operations or 'add' in operations

    # Detailed detection tests
    def test_detect_detailed(self, detector):
        """Test detailed structure detection."""
        text = "First he earned $100, then spent $30, later received $50."
        match = detector.detect_detailed(text)
        assert isinstance(match, StructureMatch)
        assert match.structure_type == StructureType.SEQUENTIAL_CHAIN
        assert match.confidence > 0
        assert len(match.segment_boundaries) > 0

    # Utility method tests
    def test_is_multi_step_true(self, detector):
        """Test multi-step detection returns true."""
        text = "He had 10. Spent 3. Then earned 5."
        assert detector.is_multi_step(text)

    def test_is_multi_step_false(self, detector):
        """Test multi-step detection returns false."""
        text = "What is 5 + 3?"
        assert not detector.is_multi_step(text)

    def test_get_step_keywords(self, detector):
        """Test extraction of step keywords."""
        text = "First she bought 5, then later sold 3."
        keywords = detector.get_step_keywords_in_text(text)
        assert 'first' in keywords or 'then' in keywords or 'later' in keywords


class TestStructureMatch:
    """Tests for StructureMatch dataclass."""

    def test_structure_match_creation(self):
        """Test StructureMatch creation."""
        match = StructureMatch(
            structure_type=StructureType.SEQUENTIAL_CHAIN,
            confidence=0.85,
            matched_patterns=['first.*then'],
            segment_boundaries=[(0, 20), (20, 40)]
        )
        assert match.structure_type == StructureType.SEQUENTIAL_CHAIN
        assert match.confidence == 0.85
        assert len(match.matched_patterns) == 1
        assert len(match.segment_boundaries) == 2


class TestSegmentInfo:
    """Tests for SegmentInfo dataclass."""

    def test_segment_info_creation(self):
        """Test SegmentInfo creation."""
        segment = SegmentInfo(
            start=0,
            end=20,
            text="He has 10 apples",
            operation_hint='initial',
            value=10.0
        )
        assert segment.start == 0
        assert segment.end == 20
        assert segment.operation_hint == 'initial'
        assert segment.value == 10.0

    def test_segment_info_optional_fields(self):
        """Test SegmentInfo with optional fields."""
        segment = SegmentInfo(start=0, end=10, text="test")
        assert segment.operation_hint is None
        assert segment.value is None
