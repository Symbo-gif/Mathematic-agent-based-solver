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
Unit tests for semantic_router.py

Tests the SemanticRouter class which routes word problems to rules
based on semantic object analysis (types, roles, operations, relationships).
"""

import pytest
from dataclasses import dataclass, field
from typing import List, Any, Optional, Dict, Tuple

from symbo_agentic_reasoners.core.word_problem.semantic_router import (
    SemanticRouter, RoutingResult, route_semantically
)
from symbo_agentic_reasoners.core.word_problem.universal_parser import (
    SemanticType, SemanticRole, RelationType, SemanticObject
)


# Helper function to create mock contexts
@dataclass
class MockRuleContext:
    """Mock context for testing."""
    original_text: str = ""
    semantic_objects: List[Any] = field(default_factory=list)
    inferred_operations: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def create_semantic_object(
    obj_id: str,
    sem_type: SemanticType,
    role: SemanticRole = SemanticRole.UNKNOWN,
    value: float = None,
    unit: str = None,
    relationships: List[Tuple[RelationType, str]] = None
) -> SemanticObject:
    """Create a SemanticObject for testing."""
    return SemanticObject(
        id=obj_id,
        type=sem_type,
        role=role,
        value=value,
        unit=unit,
        source_text=f"test_{obj_id}",
        position=0,
        relationships=relationships or []
    )


class TestSemanticRouterInit:
    """Tests for SemanticRouter initialization."""

    def test_router_initialization(self):
        """Test basic router initialization."""
        router = SemanticRouter()
        assert router is not None
        assert hasattr(router, 'TYPE_RULE_MAP')
        assert hasattr(router, 'ROLE_PATTERN_MAP')
        assert hasattr(router, 'OPERATION_RULE_MAP')

    def test_type_rule_map_defined(self):
        """Verify TYPE_RULE_MAP contains expected entries."""
        router = SemanticRouter()
        assert len(router.TYPE_RULE_MAP) > 0

        # Check rate+time mapping exists
        rate_time_key = frozenset({SemanticType.RATE, SemanticType.TIME})
        assert rate_time_key in router.TYPE_RULE_MAP

        # Check money+percentage mapping
        money_pct_key = frozenset({SemanticType.MONEY, SemanticType.PERCENTAGE})
        assert money_pct_key in router.TYPE_RULE_MAP

    def test_role_pattern_map_defined(self):
        """Verify ROLE_PATTERN_MAP contains expected entries."""
        router = SemanticRouter()
        assert len(router.ROLE_PATTERN_MAP) > 0

        # Check sequential pattern
        seq_key = frozenset({SemanticRole.INITIAL, SemanticRole.DELTA, SemanticRole.FINAL})
        assert seq_key in router.ROLE_PATTERN_MAP


class TestRoutingResult:
    """Tests for RoutingResult dataclass."""

    def test_routing_result_creation(self):
        """Test RoutingResult creation with all fields."""
        result = RoutingResult(
            prioritized_rules=['rule_a', 'rule_b'],
            confidence=0.85,
            matched_patterns=['types:(RATE, TIME)'],
            type_matches=[(SemanticType.RATE, SemanticType.TIME)],
            role_matches=[],
            operation_matches=['MULTIPLY']
        )
        assert len(result.prioritized_rules) == 2
        assert result.confidence == 0.85
        assert 'rule_a' in result.prioritized_rules


class TestTypeMatching:
    """Tests for semantic type matching."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_rate_time_matching(self, router):
        """Test matching RATE + TIME types."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.RATE, SemanticRole.RATE_VALUE, 20.0),
                create_semantic_object("2", SemanticType.TIME, SemanticRole.MULTIPLIER, 8.0)
            ]
        )
        result = router.route(context)
        assert result.success if hasattr(result, 'success') else len(result.prioritized_rules) > 0
        # Rate rules should be prioritized
        assert any('rate' in r.lower() for r in result.prioritized_rules[:3])

    def test_money_percentage_matching(self, router):
        """Test matching MONEY + PERCENTAGE types."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.MONEY, SemanticRole.INITIAL, 100.0),
                create_semantic_object("2", SemanticType.PERCENTAGE, SemanticRole.DELTA, 25.0)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Percentage rules should be prioritized
        assert any('percentage' in r.lower() for r in result.prioritized_rules[:3])

    def test_quantity_only_matching(self, router):
        """Test matching QUANTITY type only."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, SemanticRole.INITIAL, 10.0),
                create_semantic_object("2", SemanticType.QUANTITY, SemanticRole.DELTA, 5.0)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Sum/subtraction rules should appear
        assert any('sum' in r.lower() or 'subtraction' in r.lower()
                  for r in result.prioritized_rules[:5])

    def test_distance_time_matching(self, router):
        """Test matching DISTANCE + TIME types for physics problems."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.DISTANCE, value=120.0),
                create_semantic_object("2", SemanticType.TIME, value=2.0)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Distance/speed rules should be prioritized
        assert any('distance' in r.lower() or 'speed' in r.lower()
                  for r in result.prioritized_rules[:5])


class TestRoleMatching:
    """Tests for semantic role pattern matching."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_sequential_pattern_matching(self, router):
        """Test matching INITIAL -> DELTA -> FINAL pattern."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, SemanticRole.INITIAL, 10.0),
                create_semantic_object("2", SemanticType.QUANTITY, SemanticRole.DELTA, -3.0),
                create_semantic_object("3", SemanticType.QUANTITY, SemanticRole.FINAL, 7.0)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Sequential rules should be matched
        assert any('sequential' in r.lower() for r in result.prioritized_rules[:5])

    def test_rate_multiplier_pattern(self, router):
        """Test matching RATE_VALUE + MULTIPLIER pattern."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.RATE, SemanticRole.RATE_VALUE, 15.0),
                create_semantic_object("2", SemanticType.TIME, SemanticRole.MULTIPLIER, 4.0)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Rate accumulation should be matched
        assert any('rate' in r.lower() for r in result.prioritized_rules[:3])

    def test_comparison_pattern(self, router):
        """Test matching COMPARAND + REFERENCE pattern."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, SemanticRole.COMPARAND, 15.0),
                create_semantic_object("2", SemanticType.QUANTITY, SemanticRole.REFERENCE, 5.0)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Comparison rules should be matched
        assert any('comparison' in r.lower() or 'twice' in r.lower() or 'relative' in r.lower()
                  for r in result.prioritized_rules[:5])


class TestOperationMatching:
    """Tests for inferred operation matching."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_multiply_operation(self, router):
        """Test matching MULTIPLY operation."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, value=5.0)
            ],
            inferred_operations=['MULTIPLY']
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        assert 'MULTIPLY' in result.operation_matches or any(
            'multiplication' in r.lower() for r in result.prioritized_rules[:3]
        )

    def test_add_operation(self, router):
        """Test matching ADD operation."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, value=5.0)
            ],
            inferred_operations=['ADD']
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        assert 'ADD' in result.operation_matches or any(
            'sum' in r.lower() or 'accumulation' in r.lower()
            for r in result.prioritized_rules[:5]
        )

    def test_rate_multiply_operation(self, router):
        """Test matching RATE_MULTIPLY operation."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.RATE, value=20.0)
            ],
            inferred_operations=['RATE_MULTIPLY']
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Rate accumulation should be prioritized
        assert any('rate' in r.lower() for r in result.prioritized_rules[:3])


class TestRelationshipMatching:
    """Tests for relationship type matching."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_rate_of_relationship(self, router):
        """Test matching RATE_OF relationship."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object(
                    "1", SemanticType.RATE, value=25.0,
                    relationships=[(RelationType.RATE_OF, "2")]
                ),
                create_semantic_object("2", SemanticType.TIME, value=4.0)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0

    def test_transfer_relationship(self, router):
        """Test matching TRANSFER relationship."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object(
                    "1", SemanticType.QUANTITY, value=10.0,
                    relationships=[(RelationType.TRANSFER, "2")]
                ),
                create_semantic_object("2", SemanticType.PERSON)
            ]
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0


class TestSpecialPatterns:
    """Tests for special high-confidence pattern detection."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_multiple_rates_boost(self, router):
        """Test boost for multiple rate objects."""
        context = MockRuleContext(
            original_text="John earns $20/hour teaching and $30/hour coaching",
            semantic_objects=[
                create_semantic_object("1", SemanticType.RATE, SemanticRole.RATE_VALUE, 20.0),
                create_semantic_object("2", SemanticType.RATE, SemanticRole.RATE_VALUE, 30.0)
            ],
            metadata={'original_text': "John earns $20/hour teaching and $30/hour coaching"}
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Rate accumulation should be highly prioritized
        assert 'rate_accumulation' in result.prioritized_rules[:3]

    def test_backward_inference_pattern(self, router):
        """Test detection of backward inference keywords."""
        context = MockRuleContext(
            original_text="How much did John start with?",
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, SemanticRole.FINAL, 15.0)
            ],
            metadata={'original_text': "How much did John start with?"}
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Backward inference should be detected
        assert 'backward_inference' in result.prioritized_rules[:5]

    def test_sequential_keyword_pattern(self, router):
        """Test detection of sequential keywords."""
        context = MockRuleContext(
            original_text="First John bought 5 apples, then he gave away 2",
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, SemanticRole.INITIAL, 5.0),
                create_semantic_object("2", SemanticType.QUANTITY, SemanticRole.DELTA, -2.0)
            ],
            metadata={'original_text': "First John bought 5 apples, then he gave away 2"}
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Sequential rules should be boosted
        assert any('sequential' in r.lower() for r in result.prioritized_rules[:5])

    def test_percentage_pattern(self, router):
        """Test detection of percentage patterns."""
        context = MockRuleContext(
            original_text="She got a 25% discount on the $100 item",
            semantic_objects=[
                create_semantic_object("1", SemanticType.PERCENTAGE, value=25.0),
                create_semantic_object("2", SemanticType.MONEY, value=100.0)
            ],
            metadata={'original_text': "She got a 25% discount on the $100 item"}
        )
        result = router.route(context)
        assert len(result.prioritized_rules) > 0
        # Percentage rules should be boosted
        assert any('percentage' in r.lower() for r in result.prioritized_rules[:3])


class TestCombinedRouting:
    """Tests for combined type, role, and operation routing."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_rate_time_with_multiply_operation(self, router):
        """Test routing with type, role, and operation signals."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.RATE, SemanticRole.RATE_VALUE, 25.0),
                create_semantic_object("2", SemanticType.TIME, SemanticRole.MULTIPLIER, 8.0)
            ],
            inferred_operations=['RATE_MULTIPLY']
        )
        result = router.route(context)

        # Should have high confidence with multiple signals
        assert result.confidence >= 0.5

        # Rate accumulation should be top priority
        assert 'rate_accumulation' in result.prioritized_rules[:2]

        # Should have matches from multiple sources
        assert len(result.matched_patterns) >= 2


class TestEmptyContext:
    """Tests for edge cases with empty or minimal context."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_empty_semantic_objects(self, router):
        """Test routing with no semantic objects."""
        context = MockRuleContext(semantic_objects=[])
        result = router.route(context)
        assert result.confidence == 0.0
        assert len(result.prioritized_rules) == 0

    def test_no_matching_types(self, router):
        """Test routing with types that don't match any pattern."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.PERSON),
                create_semantic_object("2", SemanticType.OBJECT)
            ]
        )
        result = router.route(context)
        # Should still return a result, possibly empty or low confidence
        assert isinstance(result, RoutingResult)


class TestConvenienceFunction:
    """Tests for the route_semantically convenience function."""

    def test_route_semantically_basic(self):
        """Test the convenience function."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.RATE, SemanticRole.RATE_VALUE, 10.0),
                create_semantic_object("2", SemanticType.TIME, SemanticRole.MULTIPLIER, 5.0)
            ]
        )
        rules = route_semantically(context)
        assert isinstance(rules, list)
        assert len(rules) > 0


class TestRouteToNames:
    """Tests for route_to_names method."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_route_to_names(self, router):
        """Test route_to_names returns just names."""
        context = MockRuleContext(
            semantic_objects=[
                create_semantic_object("1", SemanticType.MONEY, value=50.0)
            ]
        )
        names = router.route_to_names(context)
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)


class TestGSM8KPatterns:
    """Tests for GSM8K-style problem patterns."""

    @pytest.fixture
    def router(self):
        return SemanticRouter()

    def test_multi_rate_accumulation(self, router):
        """Test GSM8K multi-rate pattern: different rates accumulated."""
        context = MockRuleContext(
            original_text="Jill gets paid $20 per hour to teach and $30 per hour to be a coach",
            semantic_objects=[
                create_semantic_object("1", SemanticType.RATE, SemanticRole.RATE_VALUE, 20.0),
                create_semantic_object("2", SemanticType.RATE, SemanticRole.RATE_VALUE, 30.0),
                create_semantic_object("3", SemanticType.TIME, SemanticRole.MULTIPLIER, 35.0)
            ],
            metadata={'original_text': "Jill gets paid $20 per hour to teach and $30 per hour to be a coach"}
        )
        result = router.route(context)
        assert 'rate_accumulation' in result.prioritized_rules[:2]

    def test_sequential_chain(self, router):
        """Test GSM8K sequential pattern: multi-step changes."""
        context = MockRuleContext(
            original_text="Janet has 16 eggs. She eats 3 for breakfast and bakes 4.",
            semantic_objects=[
                create_semantic_object("1", SemanticType.QUANTITY, SemanticRole.INITIAL, 16.0),
                create_semantic_object("2", SemanticType.QUANTITY, SemanticRole.DELTA, -3.0),
                create_semantic_object("3", SemanticType.QUANTITY, SemanticRole.DELTA, -4.0)
            ],
            metadata={'original_text': "Janet has 16 eggs. She eats 3 for breakfast and bakes 4."}
        )
        result = router.route(context)
        assert any('sequential' in r.lower() for r in result.prioritized_rules[:5])

    def test_percentage_cascade(self, router):
        """Test GSM8K percentage pattern: cascading percentages."""
        context = MockRuleContext(
            original_text="A store has a 20% off sale, then takes an additional 10% off.",
            semantic_objects=[
                create_semantic_object("1", SemanticType.PERCENTAGE, SemanticRole.DELTA, 20.0),
                create_semantic_object("2", SemanticType.PERCENTAGE, SemanticRole.DELTA, 10.0),
                create_semantic_object("3", SemanticType.MONEY, SemanticRole.INITIAL, 100.0)
            ],
            metadata={'original_text': "A store has a 20% off sale, then takes an additional 10% off."}
        )
        result = router.route(context)
        assert any('percentage' in r.lower() for r in result.prioritized_rules[:5])
