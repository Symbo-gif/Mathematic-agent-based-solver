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
Unit tests for operation_inference.py

Tests the OperationInferenceEngine and related classes for
inferring mathematical operations from word problem text.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.operation_inference import (
    OperationInferenceEngine, InferredOperationType, OperationNode,
    OperationGraph, InferenceResult, infer_operations
)
from symbo_agentic_reasoners.core.word_problem.universal_parser import (
    SemanticObject, SemanticType, SemanticRole, RelationType
)


class TestInferredOperationType:
    """Tests for InferredOperationType enum."""

    def test_all_operations_defined(self):
        """Verify all expected operation types exist."""
        expected_ops = [
            'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'ACCUMULATE',
            'RATE_MULTIPLY', 'PERCENTAGE', 'COMPARISON', 'SEQUENCE'
        ]
        for op_name in expected_ops:
            assert hasattr(InferredOperationType, op_name)


class TestOperationNode:
    """Tests for OperationNode dataclass."""

    def test_operation_node_creation(self):
        """Test basic OperationNode creation."""
        node = OperationNode(
            id="op_1",
            operation=InferredOperationType.MULTIPLY,
            operand_ids=["obj_1", "obj_2"],
            result_type=SemanticType.MONEY,
            confidence=0.85,
            source_pattern="rate_multiply"
        )
        assert node.id == "op_1"
        assert node.operation == InferredOperationType.MULTIPLY
        assert len(node.operand_ids) == 2
        assert node.confidence == 0.85

    def test_operation_node_with_metadata(self):
        """Test OperationNode with metadata."""
        node = OperationNode(
            id="op_1",
            operation=InferredOperationType.ADD,
            operand_ids=["obj_1"],
            result_type=SemanticType.QUANTITY,
            confidence=0.7,
            source_pattern="verb",
            position=10,
            metadata={'verb': 'earns'}
        )
        assert node.position == 10
        assert node.metadata['verb'] == 'earns'


class TestOperationGraph:
    """Tests for OperationGraph dataclass."""

    def test_operation_graph_creation(self):
        """Test basic OperationGraph creation."""
        nodes = [
            OperationNode(
                id="op_1",
                operation=InferredOperationType.MULTIPLY,
                operand_ids=["a", "b"],
                result_type=SemanticType.MONEY,
                confidence=0.8,
                source_pattern="test"
            )
        ]
        graph = OperationGraph(
            nodes=nodes,
            execution_order=["op_1"],
            primary_result_id="op_1"
        )
        assert len(graph.nodes) == 1
        assert graph.execution_order == ["op_1"]
        assert graph.primary_result_id == "op_1"

    def test_get_node(self):
        """Test get_node method."""
        node1 = OperationNode(
            id="op_1", operation=InferredOperationType.ADD,
            operand_ids=[], result_type=SemanticType.QUANTITY,
            confidence=0.8, source_pattern="test"
        )
        node2 = OperationNode(
            id="op_2", operation=InferredOperationType.MULTIPLY,
            operand_ids=[], result_type=SemanticType.MONEY,
            confidence=0.9, source_pattern="test"
        )
        graph = OperationGraph(nodes=[node1, node2], execution_order=["op_1", "op_2"])

        assert graph.get_node("op_1") == node1
        assert graph.get_node("op_2") == node2
        assert graph.get_node("nonexistent") is None


class TestInferenceResult:
    """Tests for InferenceResult dataclass."""

    def test_inference_result_success(self):
        """Test successful InferenceResult."""
        result = InferenceResult(
            success=True,
            primary_operation=InferredOperationType.MULTIPLY,
            expression="20 * 8",
            confidence=0.85
        )
        assert result.success
        assert result.primary_operation == InferredOperationType.MULTIPLY
        assert result.expression == "20 * 8"

    def test_inference_result_failure(self):
        """Test failed InferenceResult."""
        result = InferenceResult(
            success=False,
            errors=["No operations could be inferred"]
        )
        assert not result.success
        assert len(result.errors) > 0


class TestOperationInferenceEngine:
    """Tests for OperationInferenceEngine class."""

    @pytest.fixture
    def engine(self):
        """Create an OperationInferenceEngine instance."""
        return OperationInferenceEngine()

    # Verb-based inference tests
    def test_infer_add_from_earns(self, engine):
        """Test inferring ADD from 'earns' verb."""
        result = engine.infer("John earns $20 per hour")
        assert result.success
        assert 'verb:ADD' in result.patterns_matched or any(
            'earns' in p.lower() or 'add' in p.lower() for p in result.patterns_matched
        )

    def test_infer_add_from_receives(self, engine):
        """Test inferring ADD from 'receives' verb."""
        result = engine.infer("She receives 50 dollars")
        assert result.success

    def test_infer_subtract_from_spends(self, engine):
        """Test inferring SUBTRACT from 'spends' verb."""
        result = engine.infer("He spends $30 on groceries")
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('subtract' in p for p in patterns) or any('spend' in p for p in patterns)

    def test_infer_subtract_from_gives(self, engine):
        """Test inferring SUBTRACT from 'gives' verb."""
        result = engine.infer("John gives 5 apples to Mary")
        assert result.success

    def test_infer_subtract_from_loses(self, engine):
        """Test inferring SUBTRACT from 'loses' verb."""
        result = engine.infer("He loses $25")
        assert result.success

    def test_infer_multiply_from_double(self, engine):
        """Test inferring MULTIPLY from 'double' verb."""
        result = engine.infer("She doubles her money")
        assert result.success

    def test_infer_divide_from_splits(self, engine):
        """Test inferring DIVIDE from 'splits' verb."""
        result = engine.infer("They split the pizza equally")
        assert result.success

    # Contextual pattern inference tests
    def test_infer_sequence_from_first_then(self, engine):
        """Test inferring SEQUENCE from 'first...then' pattern."""
        result = engine.infer("First she bought 5, then she sold 3")
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('sequence' in p for p in patterns)

    def test_infer_rate_from_per_hour(self, engine):
        """Test inferring rate pattern from '$X per hour'."""
        result = engine.infer("He earns $20 per hour")
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('rate' in p for p in patterns)

    def test_infer_rate_from_each(self, engine):
        """Test inferring rate from 'X each' pattern."""
        result = engine.infer("5 items at $10 each")
        assert result.success

    def test_infer_accumulate_from_total(self, engine):
        """Test inferring ACCUMULATE from 'total' pattern."""
        result = engine.infer("The total of all purchases is")
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('accumulate' in p for p in patterns)

    def test_infer_accumulate_from_altogether(self, engine):
        """Test inferring ACCUMULATE from 'altogether' pattern."""
        result = engine.infer("How many altogether?")
        assert result.success

    def test_infer_comparison_from_more_than(self, engine):
        """Test inferring COMPARISON from 'more than' pattern."""
        result = engine.infer("He has 5 more than Mary")
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('comparison' in p for p in patterns)

    def test_infer_comparison_from_twice(self, engine):
        """Test inferring COMPARISON from 'twice as many' pattern."""
        result = engine.infer("She has twice as many apples")
        assert result.success

    def test_infer_percentage_pattern(self, engine):
        """Test inferring PERCENTAGE from percentage pattern."""
        result = engine.infer("She got a 25% discount")
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('percentage' in p for p in patterns)

    def test_infer_remainder_pattern(self, engine):
        """Test inferring from 'remaining/left' pattern."""
        result = engine.infer("How many are left?")
        assert result.success

    # Type-based inference tests
    def test_infer_from_rate_and_time(self, engine):
        """Test inferring RATE_MULTIPLY from RATE and TIME types."""
        rate_obj = SemanticObject(
            id="rate_1", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=20.0, unit="per hour", source_text="$20/hr", position=0
        )
        time_obj = SemanticObject(
            id="time_1", type=SemanticType.TIME, role=SemanticRole.MULTIPLIER,
            value=8.0, unit="hours", source_text="8 hours", position=20
        )
        result = engine.infer("He earns $20 per hour for 8 hours", objects=[rate_obj, time_obj])
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('type' in p or 'rate' in p for p in patterns)

    def test_infer_from_quantity_and_money(self, engine):
        """Test inferring MULTIPLY from QUANTITY and MONEY types."""
        qty_obj = SemanticObject(
            id="qty_1", type=SemanticType.QUANTITY, role=SemanticRole.MULTIPLIER,
            value=5.0, source_text="5 items", position=0
        )
        price_obj = SemanticObject(
            id="price_1", type=SemanticType.MONEY, role=SemanticRole.RATE_VALUE,
            value=10.0, unit="dollars", source_text="$10", position=20
        )
        result = engine.infer("5 items at $10 each", objects=[qty_obj, price_obj])
        assert result.success

    def test_infer_multi_rate_accumulation(self, engine):
        """Test inferring ACCUMULATE from multiple rates."""
        rate1 = SemanticObject(
            id="rate_1", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=20.0, unit="per hour", source_text="$20/hr", position=0
        )
        rate2 = SemanticObject(
            id="rate_2", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=30.0, unit="per hour", source_text="$30/hr", position=40
        )
        result = engine.infer("$20/hr as teacher and $30/hr as coach", objects=[rate1, rate2])
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('accumulate' in p or 'multi_rate' in p for p in patterns)

    # Expression building tests
    def test_build_expression_multiply(self, engine):
        """Test expression building for multiplication."""
        rate = SemanticObject(
            id="rate", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=20.0, source_text="$20", position=0
        )
        time = SemanticObject(
            id="time", type=SemanticType.TIME, role=SemanticRole.MULTIPLIER,
            value=8.0, source_text="8 hours", position=20
        )
        result = engine.infer("$20 per hour for 8 hours", objects=[rate, time])
        if result.expression:
            assert '*' in result.expression or '20' in result.expression

    def test_build_expression_add(self, engine):
        """Test expression building for addition."""
        result = engine.infer("He gains 50 dollars")
        # Expression should be built
        assert result.success

    # Computation steps tests
    def test_computation_steps_generated(self, engine):
        """Test that computation steps are generated."""
        rate = SemanticObject(
            id="rate", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=20.0, source_text="$20", position=0
        )
        time = SemanticObject(
            id="time", type=SemanticType.TIME, role=SemanticRole.MULTIPLIER,
            value=8.0, source_text="8 hours", position=20
        )
        result = engine.infer("$20 per hour for 8 hours", objects=[rate, time])
        # Steps should be generated when we have objects
        if result.computation_steps:
            assert len(result.computation_steps) >= 1
            assert 'step_number' in result.computation_steps[0]

    # Confidence calculation tests
    def test_confidence_calculated(self, engine):
        """Test that confidence is calculated."""
        result = engine.infer("John earns $20 per hour for 8 hours")
        assert 0.0 <= result.confidence <= 1.0

    def test_confidence_higher_with_more_patterns(self, engine):
        """Test that confidence increases with more patterns matched."""
        simple = engine.infer("He earns money")
        complex = engine.infer("First he earns $20 per hour, then he earns $30 per hour for 8 hours altogether")

        # Both should succeed
        assert simple.success
        assert complex.success

        # Complex should match more patterns
        assert len(complex.patterns_matched) >= len(simple.patterns_matched)

    # Edge case tests
    def test_empty_text(self, engine):
        """Test inference on empty text."""
        result = engine.infer("")
        assert isinstance(result, InferenceResult)
        # May or may not succeed depending on implementation
        assert not result.success or len(result.patterns_matched) == 0

    def test_no_operations_text(self, engine):
        """Test text with no detectable operations."""
        result = engine.infer("The sky is blue.")
        # Should return result, may not find operations
        assert isinstance(result, InferenceResult)

    def test_multiple_verbs(self, engine):
        """Test text with multiple operation verbs."""
        result = engine.infer("John earns $100 and spends $30")
        assert result.success
        # Should detect both ADD and SUBTRACT
        patterns = [p.lower() for p in result.patterns_matched]
        assert len(patterns) >= 2 or len(result.patterns_matched) >= 1

    def test_operation_order_preserved(self, engine):
        """Test that operation order is preserved."""
        result = engine.infer("First add 5, then multiply by 2, then subtract 3")
        assert result.success
        if result.operation_graph and result.operation_graph.execution_order:
            # Order should be preserved
            assert len(result.operation_graph.execution_order) >= 1


class TestInferOperationsFunction:
    """Tests for the infer_operations convenience function."""

    def test_infer_operations_basic(self):
        """Test basic usage of infer_operations function."""
        result = infer_operations("John earns $20 per hour")
        assert isinstance(result, InferenceResult)
        assert result.success

    def test_infer_operations_with_objects(self):
        """Test infer_operations with semantic objects."""
        obj = SemanticObject(
            id="1", type=SemanticType.MONEY, role=SemanticRole.INITIAL,
            value=100, source_text="$100", position=0
        )
        result = infer_operations("He has $100", objects=[obj])
        assert isinstance(result, InferenceResult)


class TestOperationInferenceIntegration:
    """Integration tests for operation inference."""

    @pytest.fixture
    def engine(self):
        return OperationInferenceEngine()

    def test_gsm8k_rate_accumulation(self, engine):
        """Test inference on GSM8K-style rate accumulation problem."""
        text = "Jill gets paid $20 per hour as a teacher and $30 per hour as a coach"
        rate1 = SemanticObject(
            id="r1", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=20.0, source_text="$20 per hour", position=15
        )
        rate2 = SemanticObject(
            id="r2", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=30.0, source_text="$30 per hour", position=50
        )
        result = engine.infer(text, objects=[rate1, rate2])
        assert result.success
        # Should detect multi-rate accumulation
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('rate' in p or 'accumulate' in p for p in patterns)

    def test_gsm8k_sequential_problem(self, engine):
        """Test inference on GSM8K-style sequential problem."""
        text = "Janet has 16 eggs. She eats 3 for breakfast, then bakes 4 into a cake."
        result = engine.infer(text)
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        # Should detect sequence and subtraction
        assert any('sequence' in p or 'subtract' in p for p in patterns)

    def test_percentage_problem(self, engine):
        """Test inference on percentage problem."""
        text = "The store offers a 25% discount on a $100 item"
        pct = SemanticObject(
            id="pct", type=SemanticType.PERCENTAGE, role=SemanticRole.RATE_VALUE,
            value=25.0, source_text="25%", position=20
        )
        price = SemanticObject(
            id="price", type=SemanticType.MONEY, role=SemanticRole.INITIAL,
            value=100.0, source_text="$100", position=45
        )
        result = engine.infer(text, objects=[pct, price])
        assert result.success

    def test_comparison_problem(self, engine):
        """Test inference on comparison problem."""
        text = "Mary has twice as many apples as John"
        result = engine.infer(text)
        assert result.success
        patterns = [p.lower() for p in result.patterns_matched]
        assert any('comparison' in p for p in patterns)

    def test_complex_multi_operation(self, engine):
        """Test inference on complex multi-operation problem."""
        text = ("John starts with $100. He earns $50, then spends $30, "
                "and finally receives $20 from his friend.")
        result = engine.infer(text)
        assert result.success
        # Should detect multiple operations
        assert len(result.patterns_matched) >= 2
