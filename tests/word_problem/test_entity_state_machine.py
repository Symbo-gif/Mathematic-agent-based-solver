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
Unit tests for entity_state_machine.py

Tests the EntityStateMachine and related classes for tracking
entity values over time in word problems.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.entity_state_machine import (
    EntityStateMachine, EntityState, OperationType, Timeline, track_entities
)


class TestOperationType:
    """Tests for OperationType enum."""

    def test_all_operations_defined(self):
        """Verify all expected operation types exist."""
        expected_ops = [
            'INITIAL', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE',
            'TRANSFER_OUT', 'TRANSFER_IN', 'SET', 'PERCENT_OF'
        ]
        for op_name in expected_ops:
            assert hasattr(OperationType, op_name)


class TestEntityState:
    """Tests for EntityState dataclass."""

    def test_entity_state_creation(self):
        """Test basic EntityState creation."""
        state = EntityState(
            entity_name="John",
            value=100.0,
            timestamp=0,
            operation=OperationType.INITIAL,
            expression_part="100"
        )
        assert state.entity_name == "John"
        assert state.value == 100.0
        assert state.timestamp == 0
        assert state.operation == OperationType.INITIAL

    def test_entity_state_with_operand(self):
        """Test EntityState with operand."""
        state = EntityState(
            entity_name="John",
            value=70.0,
            timestamp=1,
            operation=OperationType.SUBTRACT,
            operand=30.0,
            expression_part=" - 30"
        )
        assert state.operand == 30.0
        assert state.operation == OperationType.SUBTRACT

    def test_entity_state_describe_initial(self):
        """Test describe() for INITIAL operation."""
        state = EntityState(
            entity_name="John",
            value=100.0,
            timestamp=0,
            operation=OperationType.INITIAL,
            expression_part="100"
        )
        desc = state.describe()
        assert "John" in desc
        assert "100" in desc or "starts" in desc.lower()

    def test_entity_state_describe_add(self):
        """Test describe() for ADD operation."""
        state = EntityState(
            entity_name="John",
            value=150.0,
            timestamp=1,
            operation=OperationType.ADD,
            operand=50.0,
            expression_part=" + 50"
        )
        desc = state.describe()
        assert "John" in desc
        assert "50" in desc or "gains" in desc.lower()

    def test_entity_state_describe_subtract(self):
        """Test describe() for SUBTRACT operation."""
        state = EntityState(
            entity_name="John",
            value=70.0,
            timestamp=1,
            operation=OperationType.SUBTRACT,
            operand=30.0,
            expression_part=" - 30"
        )
        desc = state.describe()
        assert "John" in desc
        assert "30" in desc or "loses" in desc.lower()


class TestTimeline:
    """Tests for Timeline dataclass."""

    def test_timeline_creation(self):
        """Test basic Timeline creation."""
        timeline = Timeline()
        assert len(timeline.events) == 0

    def test_add_event(self):
        """Test adding events to timeline."""
        timeline = Timeline()
        state = EntityState(
            entity_name="John",
            value=100.0,
            timestamp=0,
            operation=OperationType.INITIAL,
            expression_part="100"
        )
        timeline.add_event(0, "John", state)
        assert len(timeline.events) == 1

    def test_events_sorted_by_timestamp(self):
        """Test that events are sorted by timestamp."""
        timeline = Timeline()
        state1 = EntityState("A", 10, 2, OperationType.ADD, expression_part="")
        state2 = EntityState("B", 20, 1, OperationType.ADD, expression_part="")
        state3 = EntityState("C", 30, 3, OperationType.ADD, expression_part="")

        timeline.add_event(2, "A", state1)
        timeline.add_event(1, "B", state2)
        timeline.add_event(3, "C", state3)

        timestamps = [e[0] for e in timeline.events]
        assert timestamps == [1, 2, 3]

    def test_get_events_at(self):
        """Test getting events at specific timestamp."""
        timeline = Timeline()
        state1 = EntityState("A", 10, 1, OperationType.ADD, expression_part="")
        state2 = EntityState("B", 20, 1, OperationType.ADD, expression_part="")
        state3 = EntityState("C", 30, 2, OperationType.ADD, expression_part="")

        timeline.add_event(1, "A", state1)
        timeline.add_event(1, "B", state2)
        timeline.add_event(2, "C", state3)

        events_at_1 = timeline.get_events_at(1)
        assert len(events_at_1) == 2

    def test_get_entity_events(self):
        """Test getting events for specific entity."""
        timeline = Timeline()
        state1 = EntityState("John", 100, 0, OperationType.INITIAL, expression_part="")
        state2 = EntityState("John", 70, 1, OperationType.SUBTRACT, expression_part="")
        state3 = EntityState("Mary", 50, 0, OperationType.INITIAL, expression_part="")

        timeline.add_event(0, "John", state1)
        timeline.add_event(1, "John", state2)
        timeline.add_event(0, "Mary", state3)

        john_events = timeline.get_entity_events("John")
        assert len(john_events) == 2


class TestEntityStateMachine:
    """Tests for EntityStateMachine class."""

    @pytest.fixture
    def machine(self):
        """Create an EntityStateMachine instance."""
        return EntityStateMachine()

    # Initial state tests
    def test_set_initial_state(self, machine):
        """Test setting initial state."""
        state = machine.set_initial_state("John", 100.0, "dollars")
        assert state.entity_name == "John"
        assert state.value == 100.0
        assert machine.get_current_value("John") == 100.0

    def test_set_initial_state_multiple_entities(self, machine):
        """Test setting initial state for multiple entities."""
        machine.set_initial_state("John", 100.0)
        machine.set_initial_state("Mary", 150.0)

        assert machine.get_current_value("John") == 100.0
        assert machine.get_current_value("Mary") == 150.0

    def test_get_all_entities(self, machine):
        """Test getting all entity names."""
        machine.set_initial_state("John", 100.0)
        machine.set_initial_state("Mary", 150.0)
        machine.set_initial_state("Tom", 75.0)

        entities = machine.get_all_entities()
        assert len(entities) == 3
        assert "John" in entities
        assert "Mary" in entities
        assert "Tom" in entities

    # Apply operation tests
    def test_apply_add_operation(self, machine):
        """Test applying addition operation."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "add", 50.0)

        assert machine.get_current_value("John") == 150.0

    def test_apply_subtract_operation(self, machine):
        """Test applying subtraction operation."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "subtract", 30.0)

        assert machine.get_current_value("John") == 70.0

    def test_apply_multiply_operation(self, machine):
        """Test applying multiplication operation."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "multiply", 2.0)

        assert machine.get_current_value("John") == 200.0

    def test_apply_divide_operation(self, machine):
        """Test applying division operation."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "divide", 4.0)

        assert machine.get_current_value("John") == 25.0

    def test_apply_divide_by_zero(self, machine):
        """Test that division by zero raises error."""
        machine.set_initial_state("John", 100.0)
        with pytest.raises(ValueError):
            machine.apply_operation("John", "divide", 0.0)

    def test_apply_set_operation(self, machine):
        """Test applying SET operation."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "set", 50.0)

        assert machine.get_current_value("John") == 50.0

    def test_apply_percent_of_operation(self, machine):
        """Test applying PERCENT_OF operation."""
        machine.set_initial_state("John", 200.0)
        machine.apply_operation("John", "percent_of", 25.0)

        assert machine.get_current_value("John") == 50.0  # 25% of 200

    def test_apply_operation_with_enum(self, machine):
        """Test applying operation with OperationType enum."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", OperationType.ADD, 25.0)

        assert machine.get_current_value("John") == 125.0

    def test_apply_operation_unknown_entity(self, machine):
        """Test applying operation to unknown entity raises error."""
        with pytest.raises(ValueError):
            machine.apply_operation("Unknown", "add", 10.0)

    # Sequential operations tests
    def test_sequential_operations(self, machine):
        """Test sequence of operations."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "subtract", 30.0)  # 70
        machine.apply_operation("John", "add", 50.0)       # 120
        machine.apply_operation("John", "multiply", 2.0)   # 240

        assert machine.get_current_value("John") == 240.0

    # Expression building tests
    def test_get_expression_initial(self, machine):
        """Test expression for initial state only."""
        machine.set_initial_state("John", 100.0)
        expr = machine.get_expression("John")
        assert "100" in expr

    def test_get_expression_with_operations(self, machine):
        """Test expression with operations."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "subtract", 30.0)
        machine.apply_operation("John", "add", 50.0)

        expr = machine.get_expression("John")
        assert "100" in expr
        assert "30" in expr
        assert "50" in expr

    def test_get_expression_parenthesized(self, machine):
        """Test parenthesized expression."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "add", 50.0)

        expr = machine.get_expression("John", parenthesize=True)
        assert "(" in expr and ")" in expr

    # State history tests
    def test_get_state_history(self, machine):
        """Test getting state history."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "subtract", 30.0)
        machine.apply_operation("John", "add", 50.0)

        history = machine.get_state_history("John")
        assert len(history) == 3
        assert history[0].value == 100.0
        assert history[1].value == 70.0
        assert history[2].value == 120.0

    def test_get_current_state(self, machine):
        """Test getting current state."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "subtract", 30.0)

        state = machine.get_current_state("John")
        assert state.value == 70.0
        assert state.operation == OperationType.SUBTRACT

    # Reference resolution tests
    def test_resolve_reference_half(self, machine):
        """Test resolving 'half' reference."""
        machine.set_initial_state("John", 100.0)
        entity, value = machine.resolve_reference("half of that")

        assert entity == "John"
        assert value == 50.0

    def test_resolve_reference_twice(self, machine):
        """Test resolving 'twice' reference."""
        machine.set_initial_state("John", 100.0)
        entity, value = machine.resolve_reference("twice as much")

        assert entity == "John"
        assert value == 200.0

    def test_resolve_reference_quarter(self, machine):
        """Test resolving 'quarter' reference."""
        machine.set_initial_state("John", 100.0)
        entity, value = machine.resolve_reference("a quarter")

        assert entity == "John"
        assert value == 25.0

    def test_resolve_reference_that(self, machine):
        """Test resolving 'that' reference."""
        machine.set_initial_state("John", 100.0)
        entity, value = machine.resolve_reference("that amount")

        assert entity == "John"
        assert value == 100.0

    # Total and combined tests
    def test_get_total_for_entity(self, machine):
        """Test getting total for entity."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "add", 50.0)

        total = machine.get_total_for_entity("John")
        assert total == 150.0

    def test_get_combined_total(self, machine):
        """Test getting combined total across entities."""
        machine.set_initial_state("John", 100.0)
        machine.set_initial_state("Mary", 150.0)
        machine.set_initial_state("Tom", 75.0)

        total = machine.get_combined_total()
        assert total == 325.0

    def test_get_combined_total_subset(self, machine):
        """Test getting combined total for subset of entities."""
        machine.set_initial_state("John", 100.0)
        machine.set_initial_state("Mary", 150.0)
        machine.set_initial_state("Tom", 75.0)

        total = machine.get_combined_total(["John", "Mary"])
        assert total == 250.0

    # Clone and rollback tests
    def test_clone(self, machine):
        """Test cloning the state machine."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "add", 50.0)

        clone = machine.clone()

        # Original and clone should have same state
        assert clone.get_current_value("John") == 150.0

        # Modifying clone should not affect original
        clone.apply_operation("John", "add", 25.0)
        assert clone.get_current_value("John") == 175.0
        assert machine.get_current_value("John") == 150.0

    def test_rollback_to(self, machine):
        """Test rollback to timestamp."""
        machine.set_initial_state("John", 100.0)  # timestamp 0
        machine.apply_operation("John", "subtract", 30.0)  # timestamp 1
        machine.apply_operation("John", "add", 50.0)  # timestamp 2
        machine.apply_operation("John", "multiply", 2.0)  # timestamp 3

        # Rollback to timestamp 1
        machine.rollback_to(1)

        # Should only have states up to timestamp 1
        history = machine.get_state_history("John")
        assert len(history) == 2
        assert machine.get_current_value("John") == 70.0

    # Backward inference tests
    def test_backward_inference_subtract(self, machine):
        """Test backward inference with subtraction."""
        # Final value is 70, after subtracting 30
        # Initial should be 100
        operations = [('subtract', 30)]
        initial = machine.backward_inference("John", 70.0, operations)
        assert initial == 100.0

    def test_backward_inference_add(self, machine):
        """Test backward inference with addition."""
        # Final value is 120, after adding 50
        # Initial should be 70
        operations = [('add', 50)]
        initial = machine.backward_inference("John", 120.0, operations)
        assert initial == 70.0

    def test_backward_inference_multiple(self, machine):
        """Test backward inference with multiple operations."""
        # 100 - 30 + 50 = 120
        # So from 120, reverse: -50 + 30 = 100
        operations = [('subtract', 30), ('add', 50)]
        initial = machine.backward_inference("John", 120.0, operations)
        assert initial == 100.0

    def test_backward_inference_multiply(self, machine):
        """Test backward inference with multiplication."""
        # Final value is 200, after multiplying by 2
        # Initial should be 100
        operations = [('multiply', 2)]
        initial = machine.backward_inference("John", 200.0, operations)
        assert initial == 100.0

    # Computation steps tests
    def test_build_computation_steps(self, machine):
        """Test building computation steps."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "subtract", 30.0)
        machine.apply_operation("John", "add", 50.0)

        steps = machine.build_computation_steps("John")
        assert len(steps) == 3
        assert steps[0]['step_number'] == 1
        assert steps[0]['operation'] == 'initial'
        assert steps[1]['operation'] == 'subtract'
        assert steps[2]['operation'] == 'add'

    # Timeline tests
    def test_get_timeline(self, machine):
        """Test getting the timeline."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "add", 50.0)

        timeline = machine.get_timeline()
        assert isinstance(timeline, Timeline)
        assert len(timeline.events) >= 2

    # Transfer tests
    def test_transfer_out(self, machine):
        """Test transfer out operation."""
        machine.set_initial_state("John", 100.0)
        machine.set_initial_state("Mary", 50.0)

        machine.apply_operation("John", "transfer_out", 30.0, source_entity="Mary")

        # John should have 70 (100 - 30)
        assert machine.get_current_value("John") == 70.0
        # Mary should have 80 (50 + 30)
        assert machine.get_current_value("Mary") == 80.0


class TestTrackEntitiesFunction:
    """Tests for the track_entities convenience function."""

    def test_track_entities_returns_machine(self):
        """Test that track_entities returns EntityStateMachine."""
        machine = track_entities("John has 10 apples")
        assert isinstance(machine, EntityStateMachine)


class TestEntityStateMachineEdgeCases:
    """Edge case tests for EntityStateMachine."""

    @pytest.fixture
    def machine(self):
        return EntityStateMachine()

    def test_get_current_value_unknown_entity(self, machine):
        """Test getting value for unknown entity."""
        assert machine.get_current_value("Unknown") is None

    def test_get_current_state_unknown_entity(self, machine):
        """Test getting state for unknown entity."""
        assert machine.get_current_state("Unknown") is None

    def test_get_expression_empty_entity(self, machine):
        """Test getting expression for empty entity."""
        expr = machine.get_expression("Unknown")
        assert expr == ""

    def test_resolve_reference_no_entities(self, machine):
        """Test resolving reference with no entities."""
        entity, value = machine.resolve_reference("half")
        assert entity is None
        assert value is None

    def test_negative_result(self, machine):
        """Test operation resulting in negative value."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "subtract", 150.0)
        assert machine.get_current_value("John") == -50.0

    def test_decimal_operations(self, machine):
        """Test operations with decimal values."""
        machine.set_initial_state("John", 100.0)
        machine.apply_operation("John", "multiply", 1.5)
        assert machine.get_current_value("John") == 150.0

    def test_zero_initial_value(self, machine):
        """Test starting with zero."""
        machine.set_initial_state("John", 0.0)
        machine.apply_operation("John", "add", 50.0)
        assert machine.get_current_value("John") == 50.0
