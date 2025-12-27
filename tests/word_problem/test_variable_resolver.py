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
Unit tests for variable_resolver.py

Tests IntermediateVariable, VariableResolver, and StepExecutor classes
for tracking and resolving intermediate computation results.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.variable_resolver import (
    IntermediateVariable, EntityReference, VariableResolver, StepExecutor
)
from symbo_agentic_reasoners.core.word_problem.problem_decomposition import (
    SubProblem, DecompositionGraph
)


class TestIntermediateVariable:
    """Tests for IntermediateVariable dataclass."""

    def test_variable_creation(self):
        """Test basic variable creation."""
        var = IntermediateVariable(
            name='v1',
            value=10.0,
            source_step='s1',
            description='initial apples'
        )
        assert var.name == 'v1'
        assert var.value == 10.0
        assert var.source_step == 's1'

    def test_is_computed_true(self):
        """Test is_computed returns true when value set."""
        var = IntermediateVariable(name='v1', value=5.0)
        assert var.is_computed()

    def test_is_computed_false(self):
        """Test is_computed returns false when value not set."""
        var = IntermediateVariable(name='v1')
        assert not var.is_computed()

    def test_as_str_integer(self):
        """Test as_str for integer values."""
        var = IntermediateVariable(name='v1', value=10.0)
        assert var.as_str() == '10'

    def test_as_str_decimal(self):
        """Test as_str for decimal values."""
        var = IntermediateVariable(name='v1', value=10.5)
        assert var.as_str() == '10.5'

    def test_as_str_uncomputed(self):
        """Test as_str for uncomputed variable."""
        var = IntermediateVariable(name='v1')
        assert var.as_str() == 'v1'


class TestEntityReference:
    """Tests for EntityReference dataclass."""

    def test_entity_reference_creation(self):
        """Test basic entity reference creation."""
        entity = EntityReference(
            name='John',
            pronouns=['he', 'him'],
            last_value_var='v1',
            position=5
        )
        assert entity.name == 'John'
        assert 'he' in entity.pronouns
        assert entity.last_value_var == 'v1'


class TestVariableResolver:
    """Tests for VariableResolver class."""

    @pytest.fixture
    def resolver(self):
        """Create a VariableResolver instance."""
        return VariableResolver()

    # Variable registration tests
    def test_register_variable(self, resolver):
        """Test registering a variable."""
        var = IntermediateVariable(name='v1', value=10.0, source_step='s1')
        resolver.register_variable(var)
        assert 'v1' in resolver.variables

    def test_get_variable(self, resolver):
        """Test getting a registered variable."""
        var = IntermediateVariable(name='v1', value=10.0)
        resolver.register_variable(var)

        retrieved = resolver.get_variable('v1')
        assert retrieved is not None
        assert retrieved.value == 10.0

    def test_get_variable_not_found(self, resolver):
        """Test getting non-existent variable."""
        assert resolver.get_variable('nonexistent') is None

    # Value operations tests
    def test_set_variable_value(self, resolver):
        """Test setting a variable value."""
        var = IntermediateVariable(name='v1')
        resolver.register_variable(var)
        resolver.set_variable_value('v1', 15.0)

        assert resolver.get_value('v1') == 15.0

    def test_set_variable_value_new(self, resolver):
        """Test setting value for new variable."""
        resolver.set_variable_value('v1', 20.0)
        assert resolver.get_value('v1') == 20.0

    def test_get_value_none(self, resolver):
        """Test getting value returns None for missing variable."""
        assert resolver.get_value('missing') is None

    # Substitution tests
    def test_substitute_values_simple(self, resolver):
        """Test simple value substitution."""
        resolver.set_variable_value('v1', 10.0)
        resolver.set_variable_value('v2', 5.0)

        expr = "v1 + v2"
        result = resolver.substitute_values(expr)
        assert result == "10 + 5"

    def test_substitute_values_expression(self, resolver):
        """Test substitution in complex expression."""
        resolver.set_variable_value('v1', 100.0)
        resolver.set_variable_value('v2', 30.0)
        resolver.set_variable_value('v3', 50.0)

        expr = "v1 - v2 + v3"
        result = resolver.substitute_values(expr)
        assert result == "100 - 30 + 50"

    def test_substitute_with_parentheses(self, resolver):
        """Test substitution with parentheses."""
        resolver.set_variable_value('v1', 10.0)

        expr = "v1 * 2"
        result = resolver.substitute_with_parentheses(expr)
        assert result == "(10) * 2"

    def test_substitute_preserves_uncomputed(self, resolver):
        """Test that uncomputed variables are preserved."""
        resolver.set_variable_value('v1', 10.0)
        # v2 is not set

        expr = "v1 + v2"
        result = resolver.substitute_values(expr)
        assert "10" in result
        assert "v2" in result

    # Reference resolution tests
    def test_resolve_direct_reference(self, resolver):
        """Test resolving direct variable reference."""
        resolver.set_variable_value('v1', 10.0)
        resolved = resolver.resolve_reference('v1')
        assert resolved == 'v1'

    def test_resolve_rest_reference(self, resolver):
        """Test resolving 'the rest' reference."""
        resolver.set_variable_value('v1', 10.0)
        resolver.set_variable_value('v2', 7.0)  # Last computed

        resolved = resolver.resolve_reference('the rest')
        assert resolved == 'v2'

    def test_resolve_remainder_reference(self, resolver):
        """Test resolving 'the remainder' reference."""
        resolver.set_variable_value('v1', 100.0)
        resolved = resolver.resolve_reference('the remainder')
        assert resolved == 'v1'

    # Entity registration tests
    def test_register_entity(self, resolver):
        """Test registering an entity."""
        entity = EntityReference(name='Mary', pronouns=['she'])
        resolver.register_entity(entity)
        assert 'Mary' in resolver.entities

    def test_resolve_entity_reference(self, resolver):
        """Test resolving entity name reference."""
        entity = EntityReference(name='apples', last_value_var='v1')
        resolver.register_entity(entity)
        resolver.set_variable_value('v1', 10.0)

        resolved = resolver.resolve_reference('how many apples')
        assert resolved == 'v1'

    # Utility method tests
    def test_get_all_values(self, resolver):
        """Test getting all computed values."""
        resolver.set_variable_value('v1', 10.0)
        resolver.set_variable_value('v2', 20.0)
        resolver.register_variable(IntermediateVariable(name='v3'))  # Uncomputed

        values = resolver.get_all_values()
        assert values == {'v1': 10.0, 'v2': 20.0}

    def test_get_computation_trace(self, resolver):
        """Test getting computation trace."""
        var1 = IntermediateVariable(name='v1', value=10.0, source_step='s1',
                                    description='initial')
        var2 = IntermediateVariable(name='v2', value=7.0, source_step='s2',
                                    description='after eating')
        resolver.register_variable(var1)
        resolver.register_variable(var2)

        trace = resolver.get_computation_trace()
        assert len(trace) == 2
        assert any(t[0] == 'v1' for t in trace)

    def test_reset(self, resolver):
        """Test resetting resolver state."""
        resolver.set_variable_value('v1', 10.0)
        resolver.reset()

        assert len(resolver.variables) == 0
        assert resolver.get_value('v1') is None

    def test_clear_values(self, resolver):
        """Test clearing values but keeping registrations."""
        var = IntermediateVariable(name='v1', value=10.0)
        resolver.register_variable(var)
        resolver.clear_values()

        assert 'v1' in resolver.variables
        assert resolver.get_value('v1') is None


class TestStepExecutor:
    """Tests for StepExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create a StepExecutor instance."""
        return StepExecutor()

    # Basic operation tests
    def test_execute_add(self, executor):
        """Test addition execution."""
        result = executor.execute_step('add', ['10', '5'], 'v1')
        assert result == 15.0
        assert executor.resolver.get_value('v1') == 15.0

    def test_execute_subtract(self, executor):
        """Test subtraction execution."""
        result = executor.execute_step('subtract', ['20', '8'], 'v1')
        assert result == 12.0

    def test_execute_multiply(self, executor):
        """Test multiplication execution."""
        result = executor.execute_step('multiply', ['4', '6'], 'v1')
        assert result == 24.0

    def test_execute_divide(self, executor):
        """Test division execution."""
        result = executor.execute_step('divide', ['100', '4'], 'v1')
        assert result == 25.0

    def test_execute_divide_by_zero(self, executor):
        """Test division by zero handling."""
        result = executor.execute_step('divide', ['100', '0'], 'v1')
        assert result == float('inf')

    def test_execute_percentage(self, executor):
        """Test percentage execution."""
        result = executor.execute_step('percentage', ['200', '25'], 'v1')
        assert result == 50.0

    def test_execute_initial(self, executor):
        """Test initial value execution."""
        result = executor.execute_step('initial', ['42'], 'v1')
        assert result == 42.0

    # Variable reference tests
    def test_execute_with_variable_reference(self, executor):
        """Test execution with variable reference."""
        executor.execute_step('initial', ['100'], 'v1')
        result = executor.execute_step('subtract', ['v1', '30'], 'v2')
        assert result == 70.0

    def test_execute_chain(self, executor):
        """Test chained execution."""
        executor.execute_step('initial', ['50'], 'v1')
        executor.execute_step('add', ['v1', '25'], 'v2')
        result = executor.execute_step('multiply', ['v2', '2'], 'v3')
        assert result == 150.0

    # Multi-operand tests
    def test_execute_multi_add(self, executor):
        """Test addition with multiple operands."""
        result = executor.execute_step('add', ['10', '20', '30'], 'v1')
        assert result == 60.0

    def test_execute_multi_multiply(self, executor):
        """Test multiplication with multiple operands."""
        result = executor.execute_step('multiply', ['2', '3', '4'], 'v1')
        assert result == 24.0

    # Graph execution tests
    def test_execute_graph(self, executor):
        """Test executing a full decomposition graph."""
        sp1 = SubProblem(
            id='s1', text='', operation='initial',
            operands=['100'], result_variable='v1'
        )
        sp2 = SubProblem(
            id='s2', text='', operation='subtract',
            operands=['v1', '30'], result_variable='v2',
            dependencies=['s1']
        )
        sp3 = SubProblem(
            id='s3', text='', operation='add',
            operands=['v2', '50'], result_variable='v3',
            dependencies=['s2']
        )

        graph = DecompositionGraph(
            sub_problems={'s1': sp1, 's2': sp2, 's3': sp3}
        )

        results = executor.execute_graph(graph)

        assert results['v1'] == 100.0
        assert results['v2'] == 70.0
        assert results['v3'] == 120.0

    def test_get_final_result(self, executor):
        """Test getting final result from graph execution."""
        sp1 = SubProblem(
            id='s1', text='', operation='initial',
            operands=['20'], result_variable='v1'
        )
        sp2 = SubProblem(
            id='s2', text='', operation='multiply',
            operands=['v1', '5'], result_variable='v2',
            dependencies=['s1']
        )

        graph = DecompositionGraph(
            sub_problems={'s1': sp1, 's2': sp2}
        )

        executor.execute_graph(graph)
        final = executor.get_final_result(graph)

        assert final == 100.0

    # Error handling tests
    def test_execute_unknown_operation(self, executor):
        """Test handling of unknown operation."""
        result = executor.execute_step('unknown_op', ['10', '5'], 'v1')
        assert result is None

    def test_execute_invalid_operand(self, executor):
        """Test handling of invalid operand."""
        result = executor.execute_step('add', ['abc', '5'], 'v1')
        assert result is None

    def test_execute_missing_operands(self, executor):
        """Test handling of missing operands."""
        result = executor.execute_step('add', [], 'v1')
        assert result is None
