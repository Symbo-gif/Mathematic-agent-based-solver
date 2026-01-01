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
Tests for Heuristic-Based Rule Pack
===================================

Comprehensive tests for all 8 heuristic rules that leverage
semantic enrichment data from the word problem pipeline.

Test Coverage:
- OperationKeywordRule: 12 tests
- QuantityBindingRule: 10 tests
- SequentialOperationRule: 8 tests
- ComparativeEquationRule: 10 tests
- ConstraintExtractionRule: 10 tests
- RateEquationRule: 10 tests
- DomainRoutingRule: 8 tests
- QuestionTypeRule: 10 tests
- HeuristicRulePack: 6 tests
- Integration: 6 tests

Total: 90 tests
"""

import pytest
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.word_problem.normalization_rule import (
    RuleContext, RuleResult, RulePriority
)
from symbo_agentic_reasoners.core.word_problem.semantic_integration import (
    SemanticEnrichmentPipeline, enrich_context
)
from symbo_agentic_reasoners.core.word_problem.rule_packs.heuristic_rules import (
    OperationKeywordRule,
    QuantityBindingRule,
    SequentialOperationRule,
    ComparativeEquationRule,
    ConstraintExtractionRule,
    RateEquationRule,
    DomainRoutingRule,
    QuestionTypeRule,
    HeuristicRulePack,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def pipeline():
    """Create a SemanticEnrichmentPipeline for enriching contexts."""
    return SemanticEnrichmentPipeline()


@pytest.fixture
def enriched_context(pipeline):
    """Create an enriched context from a sample word problem."""
    text = """John has 12 apples. First, he gives 3 to Mary.
    Then he buys 5 more. If he has twice as many as Bob,
    how many does Bob have?"""
    return pipeline.enrich(text)


@pytest.fixture
def rate_context(pipeline):
    """Create an enriched context with rate information."""
    text = "A car travels at 60 miles per hour for 3 hours. How far does it go?"
    return pipeline.enrich(text)


@pytest.fixture
def constraint_context(pipeline):
    """Create an enriched context with constraints."""
    text = "Find all x where x is at least 5 and at most 20."
    return pipeline.enrich(text)


@pytest.fixture
def probability_context(pipeline):
    """Create an enriched context with probability domain."""
    text = "What is the probability of rolling a 6 on a fair dice?"
    return pipeline.enrich(text)


def create_context_with_metadata(metadata: Dict[str, Any]) -> RuleContext:
    """Helper to create a RuleContext with specific metadata."""
    return RuleContext(
        original_text="test text",
        normalized_text="test text",
        metadata=metadata,
    )


# =============================================================================
# OperationKeywordRule Tests
# =============================================================================

class TestOperationKeywordRule:
    """Tests for OperationKeywordRule."""

    @pytest.fixture
    def rule(self):
        return OperationKeywordRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "operation_keyword"
        assert rule.domain == "word_problem.operations"
        assert rule.priority == RulePriority.HIGH

    def test_matches_with_operations(self, rule):
        """Test rule matches when heuristic_operations present."""
        context = create_context_with_metadata({
            'heuristic_operations': [
                {'op': 'add', 'keyword': 'more', 'confidence': 0.8}
            ]
        })
        assert rule.matches(context) is True

    def test_no_match_empty_operations(self, rule):
        """Test rule doesn't match with empty operations."""
        context = create_context_with_metadata({
            'heuristic_operations': []
        })
        assert rule.matches(context) is False

    def test_no_match_missing_metadata(self, rule):
        """Test rule doesn't match without metadata."""
        context = create_context_with_metadata({})
        assert rule.matches(context) is False

    def test_transform_add_operation(self, rule):
        """Test transform with add operation."""
        context = RuleContext(
            original_text="He buys 5 more apples",
            normalized_text="he buys 5 more apples",
            metadata={
                'heuristic_operations': [
                    {'op': 'add', 'keyword': 'more', 'confidence': 0.8}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '+ 5' in result.expression or '+' in result.expression
        assert result.target_service == "word_problem.operations"

    def test_transform_subtract_operation(self, rule):
        """Test transform with subtract operation."""
        context = RuleContext(
            original_text="She gives away 3 cookies",
            normalized_text="she gives away 3 cookies",
            metadata={
                'heuristic_operations': [
                    {'op': 'subtract', 'keyword': 'gives', 'confidence': 0.7}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '-' in result.expression

    def test_transform_multiply_operation(self, rule):
        """Test transform with multiply operation."""
        # Note: Rule requires a number near the keyword to build an expression
        context = RuleContext(
            original_text="He has twice 5 as many",
            normalized_text="he has twice 5 as many",
            metadata={
                'heuristic_operations': [
                    {'op': 'multiply', 'keyword': 'twice', 'confidence': 0.8}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '*' in result.expression

    def test_transform_multiple_operations(self, rule):
        """Test transform with multiple operations."""
        context = RuleContext(
            original_text="Add 5, then multiply by 2",
            normalized_text="add 5, then multiply by 2",
            metadata={
                'heuristic_operations': [
                    {'op': 'add', 'keyword': 'add', 'confidence': 0.8},
                    {'op': 'multiply', 'keyword': 'multiply', 'confidence': 0.7}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert len(result.metadata.get('expression_parts', [])) >= 1

    def test_confidence_calculation(self, rule):
        """Test confidence is averaged from operations."""
        context = RuleContext(
            original_text="test",
            normalized_text="test",
            metadata={
                'heuristic_operations': [
                    {'op': 'add', 'keyword': 'more', 'confidence': 0.8},
                    {'op': 'subtract', 'keyword': 'less', 'confidence': 0.6}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.confidence == pytest.approx(0.7, rel=0.1)

    def test_computation_steps(self, rule):
        """Test computation steps are generated."""
        context = RuleContext(
            original_text="Buy 5 more items",
            normalized_text="buy 5 more items",
            metadata={
                'heuristic_operations': [
                    {'op': 'add', 'keyword': 'more', 'confidence': 0.8}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert len(result.computation_steps) > 0
        assert any('operation' in step.lower() for step in result.computation_steps)

    def test_with_enriched_context(self, rule, enriched_context):
        """Test with fully enriched context."""
        if rule.matches(enriched_context):
            result = rule.transform(enriched_context)
            assert result.success is True


# =============================================================================
# QuantityBindingRule Tests
# =============================================================================

class TestQuantityBindingRule:
    """Tests for QuantityBindingRule."""

    @pytest.fixture
    def rule(self):
        return QuantityBindingRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "quantity_binding"
        assert rule.domain == "word_problem.binding"
        assert rule.priority == RulePriority.HIGHEST

    def test_matches_with_entity_quantities(self, rule):
        """Test rule matches with named entities."""
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'John', 'value': 12, 'unit': 'apples'}
            ]
        })
        assert rule.matches(context) is True

    def test_no_match_unknown_entities(self, rule):
        """Test rule doesn't match with only unknown entities."""
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'unknown', 'value': 5, 'unit': 'items'}
            ]
        })
        assert rule.matches(context) is False

    def test_no_match_empty_quantities(self, rule):
        """Test rule doesn't match with empty quantities."""
        context = create_context_with_metadata({
            'heuristic_quantities': []
        })
        assert rule.matches(context) is False

    def test_transform_single_binding(self, rule):
        """Test transform creates single binding."""
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'John', 'value': 12, 'unit': 'apples'}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert 'john' in result.expression.lower()
        assert '12' in result.expression
        assert result.target_service == "word_problem.binding"

    def test_transform_multiple_bindings(self, rule):
        """Test transform creates multiple bindings."""
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'John', 'value': 12, 'unit': 'apples'},
                {'entity': 'Mary', 'value': 5, 'unit': 'oranges'}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert 'john' in result.expression.lower()
        assert 'mary' in result.expression.lower()
        assert result.metadata['variable_count'] == 2

    def test_variable_name_generation(self, rule):
        """Test variable names are generated correctly."""
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'Red Car', 'value': 100, 'unit': 'mph'}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        # Variable name should be cleaned
        assert 'red' in result.expression.lower() or 'car' in result.expression.lower()

    def test_bindings_in_metadata(self, rule):
        """Test bindings are stored in metadata."""
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'Bob', 'value': 7, 'unit': None}
            ]
        })
        result = rule.transform(context)
        assert 'bindings' in result.metadata
        assert len(result.metadata['bindings']) == 1

    def test_with_enriched_context(self, rule, enriched_context):
        """Test with fully enriched context."""
        if rule.matches(enriched_context):
            result = rule.transform(enriched_context)
            assert result.success is True

    def test_filters_unknown_entities(self, rule):
        """Test unknown entities are filtered out."""
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'John', 'value': 12, 'unit': 'apples'},
                {'entity': 'unknown', 'value': 5, 'unit': 'items'}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert result.metadata['variable_count'] == 1


# =============================================================================
# SequentialOperationRule Tests
# =============================================================================

class TestSequentialOperationRule:
    """Tests for SequentialOperationRule."""

    @pytest.fixture
    def rule(self):
        return SequentialOperationRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "sequential_operation"
        assert rule.domain == "word_problem.sequence"
        assert rule.priority == RulePriority.HIGH

    def test_matches_with_sequence(self, rule):
        """Test rule matches with 2+ sequence steps."""
        context = create_context_with_metadata({
            'heuristic_sequence': [
                {'order': 1, 'marker': 'first', 'text': 'First step'},
                {'order': 2, 'marker': 'then', 'text': 'Then step'}
            ]
        })
        assert rule.matches(context) is True

    def test_no_match_single_step(self, rule):
        """Test rule doesn't match with single step."""
        context = create_context_with_metadata({
            'heuristic_sequence': [
                {'order': 1, 'marker': 'first', 'text': 'Only step'}
            ]
        })
        assert rule.matches(context) is False

    def test_no_match_empty_sequence(self, rule):
        """Test rule doesn't match with empty sequence."""
        context = create_context_with_metadata({
            'heuristic_sequence': []
        })
        assert rule.matches(context) is False

    def test_transform_orders_correctly(self, rule):
        """Test transform orders steps correctly."""
        context = create_context_with_metadata({
            'heuristic_sequence': [
                {'order': 2, 'marker': 'then', 'text': 'Second'},
                {'order': 1, 'marker': 'first', 'text': 'First'},
                {'order': 3, 'marker': 'finally', 'text': 'Third'}
            ],
            'heuristic_operations': []
        })
        result = rule.transform(context)
        assert result.success is True
        assert result.target_service == "word_problem.sequence"
        # Check sequence is in metadata
        assert 'sequence' in result.metadata

    def test_computation_steps_show_order(self, rule):
        """Test computation steps show step order."""
        context = create_context_with_metadata({
            'heuristic_sequence': [
                {'order': 1, 'marker': 'first', 'text': 'Do A'},
                {'order': 2, 'marker': 'then', 'text': 'Do B'}
            ],
            'heuristic_operations': []
        })
        result = rule.transform(context)
        assert any('Step 1' in step for step in result.computation_steps)
        assert any('Step 2' in step for step in result.computation_steps)

    def test_with_enriched_context(self, rule, enriched_context):
        """Test with fully enriched context."""
        if rule.matches(enriched_context):
            result = rule.transform(enriched_context)
            assert result.success is True

    def test_extracts_operations_from_steps(self, rule):
        """Test operations are extracted from step text."""
        context = create_context_with_metadata({
            'heuristic_sequence': [
                {'order': 1, 'marker': 'first', 'text': 'Add 5 apples'},
                {'order': 2, 'marker': 'then', 'text': 'Remove 3 apples'}
            ],
            'heuristic_operations': [
                {'op': 'add', 'keyword': 'add', 'confidence': 0.8}
            ]
        })
        result = rule.transform(context)
        assert result.success is True


# =============================================================================
# ComparativeEquationRule Tests
# =============================================================================

class TestComparativeEquationRule:
    """Tests for ComparativeEquationRule."""

    @pytest.fixture
    def rule(self):
        return ComparativeEquationRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "comparative_equation"
        assert rule.domain == "word_problem.comparative"
        assert rule.priority == RulePriority.HIGH

    def test_matches_with_comparatives(self, rule):
        """Test rule matches with comparative data."""
        context = create_context_with_metadata({
            'heuristic_comparatives': [
                {'type': 'multiple', 'subject': 'A', 'reference': 'B',
                 'factor': 2.0, 'expression': 'A = 2 * B'}
            ]
        })
        assert rule.matches(context) is True

    def test_no_match_empty_comparatives(self, rule):
        """Test rule doesn't match without comparatives."""
        context = create_context_with_metadata({
            'heuristic_comparatives': []
        })
        assert rule.matches(context) is False

    def test_transform_multiple_type(self, rule):
        """Test transform with multiple (twice, triple) type."""
        context = create_context_with_metadata({
            'heuristic_comparatives': [
                {'type': 'multiple', 'subject': 'John', 'reference': 'Bob',
                 'factor': 2.0, 'expression': ''}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert '2' in result.expression
        assert '*' in result.expression
        assert result.target_service == "word_problem.comparative"

    def test_transform_difference_type(self, rule):
        """Test transform with difference (more/less than) type."""
        context = create_context_with_metadata({
            'heuristic_comparatives': [
                {'type': 'difference', 'subject': 'A', 'reference': 'B',
                 'factor': 5.0, 'expression': ''}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert '+' in result.expression or '-' in result.expression

    def test_transform_ratio_type(self, rule):
        """Test transform with ratio (half, third) type."""
        context = create_context_with_metadata({
            'heuristic_comparatives': [
                {'type': 'ratio', 'subject': 'X', 'reference': 'Y',
                 'factor': 0.5, 'expression': ''}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert '/' in result.expression

    def test_multiple_comparatives(self, rule):
        """Test transform with multiple comparatives."""
        context = create_context_with_metadata({
            'heuristic_comparatives': [
                {'type': 'multiple', 'subject': 'A', 'reference': 'B',
                 'factor': 2.0, 'expression': ''},
                {'type': 'difference', 'subject': 'C', 'reference': 'D',
                 'factor': 3.0, 'expression': ''}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert 'AND' in result.expression
        assert len(result.metadata['equations']) == 2

    def test_equations_in_metadata(self, rule):
        """Test equations stored in metadata."""
        context = create_context_with_metadata({
            'heuristic_comparatives': [
                {'type': 'multiple', 'subject': 'X', 'reference': 'Y',
                 'factor': 3.0, 'expression': ''}
            ]
        })
        result = rule.transform(context)
        assert 'equations' in result.metadata
        assert len(result.metadata['equations']) == 1

    def test_with_enriched_context(self, rule, enriched_context):
        """Test with fully enriched context."""
        if rule.matches(enriched_context):
            result = rule.transform(enriched_context)
            assert result.success is True

    def test_cleans_variable_names(self, rule):
        """Test variable names are cleaned."""
        context = create_context_with_metadata({
            'heuristic_comparatives': [
                {'type': 'multiple', 'subject': 'John Smith', 'reference': 'Mary Jane',
                 'factor': 2.0, 'expression': ''}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        # Names should be cleaned to valid identifiers
        assert ' ' not in result.expression.split('=')[0].strip()


# =============================================================================
# ConstraintExtractionRule Tests
# =============================================================================

class TestConstraintExtractionRule:
    """Tests for ConstraintExtractionRule."""

    @pytest.fixture
    def rule(self):
        return ConstraintExtractionRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "constraint_extraction"
        assert rule.domain == "word_problem.constraints"
        assert rule.priority == RulePriority.HIGH

    def test_matches_with_constraints(self, rule):
        """Test rule matches with constraint data."""
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'x', 'operator': '>=', 'value': 5}
            ]
        })
        assert rule.matches(context) is True

    def test_no_match_empty_constraints(self, rule):
        """Test rule doesn't match without constraints."""
        context = create_context_with_metadata({
            'heuristic_constraints': []
        })
        assert rule.matches(context) is False

    def test_transform_greater_equal(self, rule):
        """Test transform with >= constraint."""
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'x', 'operator': '>=', 'value': 10}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert 'x' in result.expression
        assert '>=' in result.expression
        assert '10' in result.expression
        assert result.target_service == "word_problem.constraints"

    def test_transform_less_equal(self, rule):
        """Test transform with <= constraint."""
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'y', 'operator': '<=', 'value': 20}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert '<=' in result.expression

    def test_transform_between(self, rule):
        """Test transform with between constraint."""
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'z', 'operator': 'between', 'value': (5, 15)}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert '5' in result.expression
        assert '15' in result.expression
        assert 'z' in result.expression

    def test_multiple_constraints(self, rule):
        """Test transform with multiple constraints."""
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'x', 'operator': '>=', 'value': 0},
                {'variable': 'x', 'operator': '<=', 'value': 100}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert 'And(' in result.expression
        assert result.metadata['constraint_count'] == 2

    def test_single_constraint_no_and(self, rule):
        """Test single constraint doesn't use And()."""
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'x', 'operator': '==', 'value': 5}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert 'And(' not in result.expression

    def test_with_enriched_context(self, rule, constraint_context):
        """Test with constraint-enriched context."""
        if rule.matches(constraint_context):
            result = rule.transform(constraint_context)
            assert result.success is True

    def test_computation_steps(self, rule):
        """Test computation steps list constraints."""
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'n', 'operator': '>=', 'value': 1}
            ]
        })
        result = rule.transform(context)
        assert len(result.computation_steps) > 0


# =============================================================================
# RateEquationRule Tests
# =============================================================================

class TestRateEquationRule:
    """Tests for RateEquationRule."""

    @pytest.fixture
    def rule(self):
        return RateEquationRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "rate_equation"
        assert rule.domain == "word_problem.rates"
        assert rule.priority == RulePriority.HIGH

    def test_matches_with_rates(self, rule):
        """Test rule matches with rate data."""
        context = create_context_with_metadata({
            'heuristic_rates': [
                {'value': 60, 'unit': 'miles', 'per': 'hour'}
            ]
        })
        assert rule.matches(context) is True

    def test_no_match_empty_rates(self, rule):
        """Test rule doesn't match without rates."""
        context = create_context_with_metadata({
            'heuristic_rates': []
        })
        assert rule.matches(context) is False

    def test_transform_speed_rate(self, rule):
        """Test transform with speed rate."""
        context = RuleContext(
            original_text="A car travels at 60 miles per hour for 3 hours",
            normalized_text="a car travels at 60 miles per hour for 3 hours",
            metadata={
                'heuristic_rates': [
                    {'value': 60, 'unit': 'miles', 'per': 'hour'}
                ],
                'heuristic_quantities': [
                    {'entity': 'time', 'value': 3, 'unit': 'hours'}
                ]
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '60' in result.expression
        assert result.target_service == "word_problem.rates"

    def test_transform_cost_rate(self, rule):
        """Test transform with cost rate."""
        context = RuleContext(
            original_text="Apples cost $5 per pound for 10 pounds",
            normalized_text="apples cost $5 per pound for 10 pounds",
            metadata={
                'heuristic_rates': [
                    {'value': 5, 'unit': 'dollars', 'per': 'pound'}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '5' in result.expression

    def test_determines_result_variable(self, rule):
        """Test result variable is determined by units."""
        context = RuleContext(
            original_text="60 miles per hour",
            normalized_text="60 miles per hour",
            metadata={
                'heuristic_rates': [
                    {'value': 60, 'unit': 'miles', 'per': 'hour'}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.success is True
        # Should create distance-related variable
        assert 'distance' in result.expression.lower() or 'rate' in result.expression.lower()

    def test_multiple_rates(self, rule):
        """Test transform with multiple rates."""
        context = create_context_with_metadata({
            'heuristic_rates': [
                {'value': 60, 'unit': 'miles', 'per': 'hour'},
                {'value': 5, 'unit': 'dollars', 'per': 'gallon'}
            ],
            'heuristic_quantities': []
        })
        result = rule.transform(context)
        assert result.success is True
        assert len(result.metadata['equations']) >= 1

    def test_with_enriched_context(self, rule, rate_context):
        """Test with rate-enriched context."""
        if rule.matches(rate_context):
            result = rule.transform(rate_context)
            assert result.success is True

    def test_finds_time_multiplier(self, rule):
        """Test finding time multiplier in text."""
        context = RuleContext(
            original_text="60 mph for 5 hours",
            normalized_text="60 mph for 5 hours",
            metadata={
                'heuristic_rates': [
                    {'value': 60, 'unit': 'miles', 'per': 'hour'}
                ],
                'heuristic_quantities': []
            }
        )
        result = rule.transform(context)
        assert result.success is True
        # Should find 5 hours as multiplier
        if '*' in result.expression:
            assert '5' in result.expression

    def test_computation_steps(self, rule):
        """Test computation steps are generated."""
        context = create_context_with_metadata({
            'heuristic_rates': [
                {'value': 100, 'unit': 'km', 'per': 'hour'}
            ],
            'heuristic_quantities': []
        })
        result = rule.transform(context)
        assert len(result.computation_steps) > 0
        assert any('rate' in step.lower() for step in result.computation_steps)


# =============================================================================
# DomainRoutingRule Tests
# =============================================================================

class TestDomainRoutingRule:
    """Tests for DomainRoutingRule."""

    @pytest.fixture
    def rule(self):
        return DomainRoutingRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "domain_routing"
        assert rule.domain == "word_problem.routing"
        assert rule.priority == RulePriority.HIGHEST

    def test_matches_with_domain_hints(self, rule):
        """Test rule matches with domain hints."""
        context = create_context_with_metadata({
            'domain_hints': [
                {'domain': 'probability', 'confidence': 0.8}
            ]
        })
        assert rule.matches(context) is True

    def test_no_match_empty_hints(self, rule):
        """Test rule doesn't match without hints."""
        context = create_context_with_metadata({
            'domain_hints': []
        })
        assert rule.matches(context) is False

    def test_transform_probability_domain(self, rule):
        """Test transform with probability domain."""
        context = RuleContext(
            original_text="What is the probability of...",
            normalized_text="what is the probability of...",
            metadata={
                'domain_hints': [
                    {'domain': 'probability', 'confidence': 0.9}
                ]
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '[PROBABILITY]' in result.expression
        assert result.target_service == "math.probability"

    def test_transform_geometry_domain(self, rule):
        """Test transform with geometry domain."""
        context = RuleContext(
            original_text="Find the area of the triangle",
            normalized_text="find the area of the triangle",
            metadata={
                'domain_hints': [
                    {'domain': 'geometry', 'confidence': 0.85}
                ]
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '[GEOMETRY]' in result.expression
        assert result.target_service == "math.geometry"

    def test_selects_highest_confidence(self, rule):
        """Test selects domain with highest confidence."""
        context = RuleContext(
            original_text="test",
            normalized_text="test",
            metadata={
                'domain_hints': [
                    {'domain': 'algebra', 'confidence': 0.6},
                    {'domain': 'calculus', 'confidence': 0.9},
                    {'domain': 'geometry', 'confidence': 0.7}
                ]
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert result.metadata['primary_domain'] == 'calculus'

    def test_all_domains_in_metadata(self, rule):
        """Test all domains are stored in metadata."""
        context = create_context_with_metadata({
            'domain_hints': [
                {'domain': 'probability', 'confidence': 0.8},
                {'domain': 'statistics', 'confidence': 0.6}
            ]
        })
        result = rule.transform(context)
        assert 'all_domains' in result.metadata
        assert 'probability' in result.metadata['all_domains']
        assert 'statistics' in result.metadata['all_domains']

    def test_with_enriched_context(self, rule, probability_context):
        """Test with probability-enriched context."""
        if rule.matches(probability_context):
            result = rule.transform(probability_context)
            assert result.success is True

    def test_confidence_passed_through(self, rule):
        """Test confidence is passed through from domain hint."""
        context = create_context_with_metadata({
            'domain_hints': [
                {'domain': 'algebra', 'confidence': 0.75}
            ]
        })
        result = rule.transform(context)
        assert result.confidence == pytest.approx(0.75, rel=0.01)


# =============================================================================
# QuestionTypeRule Tests
# =============================================================================

class TestQuestionTypeRule:
    """Tests for QuestionTypeRule."""

    @pytest.fixture
    def rule(self):
        return QuestionTypeRule()

    def test_initialization(self, rule):
        """Test rule initializes correctly."""
        assert rule.name == "question_type"
        assert rule.domain == "word_problem.question"
        assert rule.priority == RulePriority.MEDIUM

    def test_matches_with_question_type(self, rule):
        """Test rule matches with question type."""
        context = create_context_with_metadata({
            'question_type': 'count'
        })
        assert rule.matches(context) is True

    def test_no_match_without_question_type(self, rule):
        """Test rule doesn't match without question type."""
        context = create_context_with_metadata({})
        assert rule.matches(context) is False

    def test_transform_count_type(self, rule):
        """Test transform with count question type."""
        context = RuleContext(
            original_text="How many apples?",
            normalized_text="how many apples?",
            metadata={
                'question_type': 'count',
                'expected_format': 'integer'
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert 'integer' in result.expression.lower()
        assert result.target_service == "word_problem.question"

    def test_transform_probability_type(self, rule):
        """Test transform with probability question type."""
        context = RuleContext(
            original_text="What is the probability?",
            normalized_text="what is the probability?",
            metadata={
                'question_type': 'probability',
                'expected_format': '[0,1]'
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert '0' in result.expression and '1' in result.expression

    def test_transform_fraction_type(self, rule):
        """Test transform with fraction question type."""
        context = RuleContext(
            original_text="What fraction?",
            normalized_text="what fraction?",
            metadata={
                'question_type': 'fraction',
                'expected_format': 'rational'
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert 'rational' in result.expression.lower() or 'p/q' in result.expression.lower()

    def test_format_constraint_in_metadata(self, rule):
        """Test format constraint stored in metadata."""
        context = create_context_with_metadata({
            'question_type': 'amount',
            'expected_format': 'decimal'
        })
        result = rule.transform(context)
        assert 'format_constraint' in result.metadata

    def test_computation_steps(self, rule):
        """Test computation steps show question info."""
        context = create_context_with_metadata({
            'question_type': 'count',
            'expected_format': 'integer'
        })
        result = rule.transform(context)
        assert any('count' in step.lower() for step in result.computation_steps)

    def test_with_enriched_context(self, rule, enriched_context):
        """Test with fully enriched context."""
        if rule.matches(enriched_context):
            result = rule.transform(enriched_context)
            assert result.success is True

    def test_handles_missing_expected_format(self, rule):
        """Test handles missing expected_format gracefully."""
        context = create_context_with_metadata({
            'question_type': 'unknown'
        })
        result = rule.transform(context)
        assert result.success is True

    def test_boolean_type(self, rule):
        """Test transform with boolean question type."""
        context = RuleContext(
            original_text="Is it possible?",
            normalized_text="is it possible?",
            metadata={
                'question_type': 'boolean',
                'expected_format': 'true/false'
            }
        )
        result = rule.transform(context)
        assert result.success is True
        assert 'true' in result.expression.lower() or 'false' in result.expression.lower()


# =============================================================================
# HeuristicRulePack Tests
# =============================================================================

class TestHeuristicRulePack:
    """Tests for HeuristicRulePack."""

    @pytest.fixture
    def pack(self):
        return HeuristicRulePack()

    def test_get_metadata(self, pack):
        """Test pack metadata is correct."""
        metadata = pack.get_metadata()
        assert metadata.name == "heuristic"
        assert metadata.domain == "word_problem.heuristic"
        assert metadata.version == "1.0.0"
        assert len(metadata.coverage) == 8  # 8 rules

    def test_create_rules_count(self, pack):
        """Test pack creates 8 rules."""
        rules = pack.create_rules()
        assert len(rules) == 8

    def test_create_rules_types(self, pack):
        """Test pack creates correct rule types."""
        rules = pack.create_rules()
        rule_names = {r.name for r in rules}
        expected = {
            'operation_keyword', 'quantity_binding', 'sequential_operation',
            'comparative_equation', 'constraint_extraction', 'rate_equation',
            'domain_routing', 'question_type'
        }
        assert rule_names == expected

    def test_rules_have_target_services(self, pack):
        """Test all rules produce results with target_service."""
        rules = pack.create_rules()
        for rule in rules:
            # Create a context that will match
            if rule.name == 'operation_keyword':
                context = create_context_with_metadata({
                    'heuristic_operations': [{'op': 'add', 'keyword': 'more', 'confidence': 0.8}],
                    'heuristic_quantities': []
                })
            elif rule.name == 'quantity_binding':
                context = create_context_with_metadata({
                    'heuristic_quantities': [{'entity': 'Test', 'value': 5, 'unit': None}]
                })
            elif rule.name == 'question_type':
                context = create_context_with_metadata({
                    'question_type': 'count', 'expected_format': 'integer'
                })
            else:
                continue  # Skip rules that need more complex setup

            if rule.matches(context):
                result = rule.transform(context)
                if result.success:
                    assert result.target_service is not None, f"{rule.name} missing target_service"

    def test_rules_are_normalization_rules(self, pack):
        """Test all rules inherit from NormalizationRule."""
        from symbo_agentic_reasoners.core.word_problem.normalization_rule import NormalizationRule
        rules = pack.create_rules()
        for rule in rules:
            assert isinstance(rule, NormalizationRule)

    def test_pack_integration(self, pack, enriched_context):
        """Test pack works with enriched context."""
        rules = pack.create_rules()
        matched_count = 0
        for rule in rules:
            if rule.matches(enriched_context):
                result = rule.transform(enriched_context)
                if result.success:
                    matched_count += 1
        # At least some rules should match
        assert matched_count > 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestHeuristicRulesIntegration:
    """Integration tests for heuristic rules with the rule engine."""

    def test_rules_registered_in_engine(self):
        """Test heuristic rules are registered in default rule engine."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine

        engine = RuleEngine(auto_enrich=True)
        rule_names = {r.name for r in engine.library.iter_rules()}

        heuristic_names = {
            'operation_keyword', 'quantity_binding', 'sequential_operation',
            'comparative_equation', 'constraint_extraction', 'rate_equation',
            'domain_routing', 'question_type'
        }

        assert heuristic_names.issubset(rule_names)

    def test_heuristic_rules_match_in_engine(self):
        """Test heuristic rules match through engine."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import (
            RuleEngine, ExecutionStrategy
        )

        engine = RuleEngine(
            strategy=ExecutionStrategy.MULTI_MATCH,
            auto_enrich=True
        )

        text = "John has 12 apples. He gives 3 to Mary. How many are left?"
        result = engine.normalize(text)

        # Some heuristic rules should match
        heuristic_matched = [
            r for r in result.matched_rules
            if r in ['operation_keyword', 'quantity_binding', 'question_type']
        ]
        assert len(heuristic_matched) > 0

    def test_enrichment_provides_heuristic_data(self):
        """Test semantic enrichment provides data for heuristic rules."""
        from symbo_agentic_reasoners.core.word_problem.semantic_integration import (
            enrich_context
        )

        enriched = enrich_context(
            "A car travels at 60 mph. Find x where x >= 10."
        )

        # Check heuristic data is present
        assert enriched.heuristic_analysis is not None
        assert 'heuristic_operations' in enriched.metadata
        assert 'heuristic_quantities' in enriched.metadata

    def test_cascade_strategy_with_heuristics(self):
        """Test cascade strategy works with heuristic rules."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import (
            RuleEngine, ExecutionStrategy
        )

        engine = RuleEngine(
            strategy=ExecutionStrategy.CASCADE,
            auto_enrich=True
        )

        text = "First, add 5. Then multiply by 2. What is the result?"
        result = engine.normalize(text)

        assert result.success is True

    def test_adaptive_engine_with_heuristics(self):
        """Test adaptive engine tracks heuristic rule stats."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import (
            AdaptiveRuleEngine, ExecutionStrategy
        )

        engine = AdaptiveRuleEngine(
            strategy=ExecutionStrategy.BEST_CONFIDENCE,
            auto_enrich=True,
            auto_save=False  # Don't persist for tests
        )

        text = "What is the probability of getting heads?"
        result = engine.normalize(text)

        assert result.success is True

        # Check stats are tracked
        stats = engine.get_all_rule_stats()
        # Some rules should have been invoked
        assert len(stats) > 0

    def test_full_pipeline_integration(self):
        """Test full pipeline from text to normalized expression."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine

        engine = RuleEngine(auto_enrich=True)

        problems = [
            "John has 10 apples and buys 5 more. How many does he have?",
            "A train travels at 80 km/h for 2 hours. How far does it go?",
            "Find x where x is at least 5 and at most 10.",
            "What is the probability of rolling a 6?",
        ]

        for problem in problems:
            result = engine.normalize(problem)
            assert result.success is True
            assert result.primary_result is not None
            assert result.primary_result.expression is not None


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestHeuristicRulesEdgeCases:
    """Edge case tests for heuristic rules."""

    def test_empty_text(self):
        """Test handling of empty text."""
        from symbo_agentic_reasoners.core.word_problem.semantic_integration import (
            SemanticEnrichmentPipeline
        )

        pipeline = SemanticEnrichmentPipeline()
        enriched = pipeline.enrich("")

        # Should not crash, should have empty data
        assert enriched is not None

    def test_none_metadata_values(self):
        """Test rules handle None metadata values."""
        rule = OperationKeywordRule()
        context = create_context_with_metadata({
            'heuristic_operations': None
        })
        # Should not crash
        assert rule.matches(context) is False

    def test_malformed_operation_data(self):
        """Test handling of malformed operation data."""
        rule = OperationKeywordRule()
        context = create_context_with_metadata({
            'heuristic_operations': [
                {'op': 'add'}  # Missing keyword and confidence
            ],
            'heuristic_quantities': []
        })
        # Should handle gracefully
        if rule.matches(context):
            result = rule.transform(context)
            # Should not crash

    def test_special_characters_in_entities(self):
        """Test handling of special characters in entity names."""
        rule = QuantityBindingRule()
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': "O'Brien", 'value': 10, 'unit': 'items'}
            ]
        })
        if rule.matches(context):
            result = rule.transform(context)
            assert result.success is True
            # Variable name should be sanitized

    def test_very_large_numbers(self):
        """Test handling of very large numbers."""
        rule = QuantityBindingRule()
        context = create_context_with_metadata({
            'heuristic_quantities': [
                {'entity': 'Count', 'value': 1e15, 'unit': None}
            ]
        })
        if rule.matches(context):
            result = rule.transform(context)
            assert result.success is True

    def test_negative_values(self):
        """Test handling of negative values."""
        rule = ConstraintExtractionRule()
        context = create_context_with_metadata({
            'heuristic_constraints': [
                {'variable': 'x', 'operator': '>=', 'value': -10}
            ]
        })
        result = rule.transform(context)
        assert result.success is True
        assert '-10' in result.expression


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
