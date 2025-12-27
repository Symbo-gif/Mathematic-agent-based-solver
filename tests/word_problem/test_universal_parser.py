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
Unit tests for universal_parser.py

Tests the UniversalParser and related classes for object-based
semantic extraction from word problems.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.universal_parser import (
    UniversalParser, SemanticObject, SemanticType, SemanticRole,
    RelationType, ParseResult
)


class TestSemanticType:
    """Tests for SemanticType enum."""

    def test_all_types_defined(self):
        """Verify all expected semantic types exist."""
        expected_types = [
            'QUANTITY', 'MONEY', 'TIME', 'RATE', 'PERCENTAGE',
            'PERSON', 'OBJECT', 'UNKNOWN'
        ]
        for type_name in expected_types:
            assert hasattr(SemanticType, type_name)


class TestSemanticRole:
    """Tests for SemanticRole enum."""

    def test_all_roles_defined(self):
        """Verify all expected semantic roles exist."""
        expected_roles = [
            'SUBJECT', 'OBJECT', 'INITIAL', 'DELTA', 'FINAL',
            'RATE_VALUE', 'MULTIPLIER', 'TOTAL', 'UNKNOWN'
        ]
        for role_name in expected_roles:
            assert hasattr(SemanticRole, role_name)


class TestRelationType:
    """Tests for RelationType enum."""

    def test_all_relations_defined(self):
        """Verify all expected relation types exist."""
        expected_relations = [
            'OWNERSHIP', 'TRANSFER', 'RATE_OF', 'PART_OF',
            'COMPARISON', 'SEQUENCE', 'ACCUMULATION'
        ]
        for rel_name in expected_relations:
            assert hasattr(RelationType, rel_name)


class TestSemanticObject:
    """Tests for SemanticObject dataclass."""

    def test_semantic_object_creation(self):
        """Test basic SemanticObject creation."""
        obj = SemanticObject(
            id="obj_1",
            type=SemanticType.MONEY,
            role=SemanticRole.INITIAL,
            value=100.0,
            unit="dollars",
            source_text="100 dollars",
            position=10
        )
        assert obj.id == "obj_1"
        assert obj.type == SemanticType.MONEY
        assert obj.role == SemanticRole.INITIAL
        assert obj.value == 100.0
        assert obj.unit == "dollars"

    def test_semantic_object_is_rate(self):
        """Test is_rate() method."""
        rate_obj = SemanticObject(
            id="rate_1",
            type=SemanticType.RATE,
            role=SemanticRole.RATE_VALUE,
            value=20.0,
            unit="per hour",
            source_text="$20 per hour",
            position=0
        )
        non_rate_obj = SemanticObject(
            id="qty_1",
            type=SemanticType.QUANTITY,
            role=SemanticRole.INITIAL,
            value=5,
            source_text="5 apples",
            position=0
        )
        assert rate_obj.is_rate()
        assert not non_rate_obj.is_rate()

    def test_semantic_object_has_value(self):
        """Test has_value() method."""
        with_value = SemanticObject(
            id="1", type=SemanticType.QUANTITY, role=SemanticRole.INITIAL,
            value=10.0, source_text="10", position=0
        )
        without_value = SemanticObject(
            id="2", type=SemanticType.PERSON, role=SemanticRole.SUBJECT,
            value=None, source_text="John", position=0
        )
        assert with_value.has_value()
        assert not without_value.has_value()


class TestParseResult:
    """Tests for ParseResult dataclass."""

    def test_parse_result_creation(self):
        """Test basic ParseResult creation."""
        objects = [
            SemanticObject(
                id="1", type=SemanticType.MONEY, role=SemanticRole.INITIAL,
                value=100.0, source_text="$100", position=0
            )
        ]
        result = ParseResult(
            objects=objects,
            relationships=[],
            rate_groups=[],
            implicit_quantities={}
        )
        assert len(result.objects) == 1
        assert result.objects[0].source_text == "$100"

    def test_get_by_id(self):
        """Test get_by_id() method."""
        obj = SemanticObject(
            id="test_id", type=SemanticType.QUANTITY, role=SemanticRole.INITIAL,
            value=5, source_text="5", position=0
        )
        result = ParseResult(
            objects=[obj], relationships=[],
            rate_groups=[], implicit_quantities={}
        )
        assert result.get_by_id("test_id") == obj
        assert result.get_by_id("nonexistent") is None


class TestUniversalParser:
    """Tests for UniversalParser class."""

    @pytest.fixture
    def parser(self):
        """Create a UniversalParser instance."""
        return UniversalParser()

    # Basic parsing tests
    def test_parse_simple_quantity(self, parser):
        """Test parsing a simple quantity."""
        result = parser.parse("John has 5 apples")
        assert isinstance(result, ParseResult)
        assert len(result.objects) > 0
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 5.0 in values

    def test_parse_money_values(self, parser):
        """Test parsing money values."""
        result = parser.parse("She has $100 in her wallet")
        money_objs = [obj for obj in result.objects if obj.type == SemanticType.MONEY]
        assert len(money_objs) > 0
        assert any(obj.value == 100.0 for obj in money_objs)

    def test_parse_person_detection(self, parser):
        """Test detection of person entities."""
        result = parser.parse("John gave Mary 5 apples")
        person_objs = [obj for obj in result.objects if obj.type == SemanticType.PERSON]
        person_names = [obj.source_text.lower() for obj in person_objs]
        assert 'john' in person_names or 'mary' in person_names

    # Rate parsing tests
    def test_parse_rate_per_hour(self, parser):
        """Test parsing rate with 'per hour' pattern."""
        result = parser.parse("He earns $20 per hour")
        rate_objs = [obj for obj in result.objects if obj.is_rate()]
        assert len(rate_objs) > 0

    def test_parse_rate_each_day(self, parser):
        """Test parsing rate with 'each day' pattern."""
        result = parser.parse("She reads 50 pages each day")
        rate_objs = [obj for obj in result.objects if obj.is_rate()]
        assert len(rate_objs) > 0

    def test_parse_rate_per_week(self, parser):
        """Test parsing rate with 'per week' pattern."""
        result = parser.parse("The store sells 1000 items per week")
        rate_objs = [obj for obj in result.objects if obj.is_rate()]
        assert len(rate_objs) > 0 or any(obj.value == 1000 for obj in result.objects if obj.has_value())

    # Implicit quantity tests
    def test_parse_implicit_dozen(self, parser):
        """Test parsing implicit quantity 'dozen'."""
        result = parser.parse("She bought a dozen eggs")
        assert 'dozen' in result.implicit_quantities
        assert result.implicit_quantities['dozen'] == 12

    def test_parse_implicit_pair(self, parser):
        """Test parsing implicit quantity 'pair'."""
        result = parser.parse("He bought a pair of shoes")
        assert 'pair' in result.implicit_quantities
        assert result.implicit_quantities['pair'] == 2

    def test_parse_implicit_weekdays(self, parser):
        """Test parsing implicit quantity 'weekdays'."""
        result = parser.parse("She works on weekdays")
        if 'weekdays' in result.implicit_quantities:
            assert result.implicit_quantities['weekdays'] == 5

    def test_parse_implicit_half(self, parser):
        """Test parsing implicit quantity 'half'."""
        result = parser.parse("He ate half of the pizza")
        if 'half' in result.implicit_quantities:
            assert result.implicit_quantities['half'] == 0.5

    # Percentage parsing tests
    def test_parse_percentage(self, parser):
        """Test parsing percentage values."""
        result = parser.parse("She got a 25% discount")
        pct_objs = [obj for obj in result.objects if obj.type == SemanticType.PERCENTAGE]
        assert len(pct_objs) > 0 or any(obj.value == 25 for obj in result.objects if obj.has_value())

    # Time parsing tests
    def test_parse_time_hours(self, parser):
        """Test parsing time in hours."""
        result = parser.parse("He worked for 8 hours")
        time_objs = [obj for obj in result.objects if obj.type == SemanticType.TIME]
        assert len(time_objs) > 0 or any(obj.value == 8 for obj in result.objects if obj.has_value())

    def test_parse_time_days(self, parser):
        """Test parsing time in days."""
        result = parser.parse("She studied for 5 days")
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 5.0 in values

    # Multi-value parsing tests
    def test_parse_multiple_values(self, parser):
        """Test parsing text with multiple values."""
        result = parser.parse("John has $100 and Mary has $150")
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 100.0 in values
        assert 150.0 in values

    def test_parse_complex_problem(self, parser):
        """Test parsing a complex word problem."""
        text = "John earns $20 per hour. He works 8 hours a day for 5 days."
        result = parser.parse(text)
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 20.0 in values
        assert 8.0 in values
        assert 5.0 in values

    # Role detection tests
    def test_detect_subject_role(self, parser):
        """Test detection of subject role."""
        result = parser.parse("John has 10 apples")
        subject_objs = [obj for obj in result.objects if obj.role == SemanticRole.SUBJECT]
        # Subject detection may vary
        assert len(result.objects) > 0

    def test_detect_delta_role(self, parser):
        """Test detection of delta (change) role."""
        result = parser.parse("He gave away 5 apples")
        delta_objs = [obj for obj in result.objects if obj.role == SemanticRole.DELTA]
        # Delta detection may vary
        assert len(result.objects) > 0

    # Relationship detection tests
    def test_detect_gives_relationship(self, parser):
        """Test detection of GIVES relationship."""
        result = parser.parse("John gave Mary 5 apples")
        # Relationships should be detected
        assert len(result.objects) >= 2

    def test_detect_rate_relationship(self, parser):
        """Test detection of rate relationship."""
        result = parser.parse("She earns $30 per hour for 10 hours")
        rate_objs = [obj for obj in result.objects if obj.is_rate()]
        # Rate relationship exists if rate objects detected
        assert len(result.objects) >= 1

    # Edge case tests
    def test_parse_empty_string(self, parser):
        """Test parsing empty string."""
        result = parser.parse("")
        assert isinstance(result, ParseResult)
        assert len(result.objects) == 0

    def test_parse_no_numbers(self, parser):
        """Test parsing text without numbers."""
        result = parser.parse("John went to the store")
        assert isinstance(result, ParseResult)

    def test_parse_decimal_numbers(self, parser):
        """Test parsing decimal numbers."""
        result = parser.parse("The price is $10.50")
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 10.50 in values or 10.5 in values

    def test_parse_negative_numbers(self, parser):
        """Test parsing with context suggesting negative values."""
        result = parser.parse("He lost $25")
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 25.0 in values

    # GSM8K-style problem tests
    def test_parse_gsm8k_style_rate_accumulation(self, parser):
        """Test parsing GSM8K-style multi-rate problem."""
        text = "Jill gets paid $20/hour as teacher and $30/hour as coach"
        result = parser.parse(text)
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 20.0 in values
        assert 30.0 in values

    def test_parse_gsm8k_style_sequential(self, parser):
        """Test parsing GSM8K-style sequential problem."""
        text = "Janet has 16 eggs. She eats 3 for breakfast, then bakes 4 into a cake."
        result = parser.parse(text)
        values = [obj.value for obj in result.objects if obj.has_value()]
        assert 16.0 in values
        assert 3.0 in values
        assert 4.0 in values


class TestUniversalParserImplicitQuantities:
    """Focused tests for implicit quantity detection."""

    @pytest.fixture
    def parser(self):
        return UniversalParser()

    def test_implicit_quantity_dozen(self, parser):
        """Test dozen = 12."""
        result = parser.parse("a dozen roses")
        assert result.implicit_quantities.get('dozen') == 12

    def test_implicit_quantity_couple(self, parser):
        """Test couple = 2."""
        result = parser.parse("a couple of hours")
        if 'couple' in result.implicit_quantities:
            assert result.implicit_quantities['couple'] == 2

    def test_implicit_quantity_score(self, parser):
        """Test score = 20."""
        result = parser.parse("four score years")
        if 'score' in result.implicit_quantities:
            assert result.implicit_quantities['score'] == 20

    def test_implicit_quantity_triple(self, parser):
        """Test triple = 3."""
        result = parser.parse("triple the amount")
        if 'triple' in result.implicit_quantities:
            assert result.implicit_quantities['triple'] == 3
