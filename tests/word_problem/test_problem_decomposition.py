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
Unit tests for problem_decomposition.py

Tests SubProblem, DecompositionGraph, and ProblemDecomposer classes
for multi-step word problem decomposition.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.problem_decomposition import (
    SubProblem, DecompositionGraph, ProblemDecomposer
)
from symbo_agentic_reasoners.core.word_problem.structure_detectors import StructureType


class TestSubProblem:
    """Tests for SubProblem dataclass."""

    def test_sub_problem_creation(self):
        """Test basic SubProblem creation."""
        sp = SubProblem(
            id='s1',
            text='has 10 apples',
            operation='initial',
            operands=['10'],
            result_variable='v1',
            position=0
        )
        assert sp.id == 's1'
        assert sp.operation == 'initial'
        assert sp.operands == ['10']
        assert sp.result_variable == 'v1'

    def test_sub_problem_dependencies(self):
        """Test SubProblem with dependencies."""
        sp = SubProblem(
            id='s2',
            text='eats 3',
            operation='subtract',
            operands=['v1', '3'],
            result_variable='v2',
            dependencies=['s1'],
            position=1
        )
        assert sp.dependencies == ['s1']

    def test_get_literal_operands(self):
        """Test extraction of literal numeric operands."""
        sp = SubProblem(
            id='s1',
            text='test',
            operation='add',
            operands=['v1', '5', '3'],
            result_variable='v2'
        )
        literals = sp.get_literal_operands()
        assert 5.0 in literals
        assert 3.0 in literals
        assert len(literals) == 2

    def test_get_variable_operands(self):
        """Test extraction of variable reference operands."""
        sp = SubProblem(
            id='s1',
            text='test',
            operation='add',
            operands=['v1', '5', 'v2'],
            result_variable='v3'
        )
        vars = sp.get_variable_operands()
        assert 'v1' in vars
        assert 'v2' in vars
        assert len(vars) == 2


class TestDecompositionGraph:
    """Tests for DecompositionGraph dataclass."""

    def test_graph_creation_simple(self):
        """Test simple graph creation."""
        sp1 = SubProblem(
            id='s1', text='start', operation='initial',
            operands=['10'], result_variable='v1', position=0
        )
        graph = DecompositionGraph(sub_problems={'s1': sp1})

        assert 's1' in graph.sub_problems
        assert 's1' in graph.root_ids
        assert 's1' in graph.terminal_ids
        assert graph.execution_order == ['s1']

    def test_graph_linear_chain(self):
        """Test linear chain dependency graph."""
        sp1 = SubProblem(
            id='s1', text='start', operation='initial',
            operands=['10'], result_variable='v1', position=0
        )
        sp2 = SubProblem(
            id='s2', text='subtract', operation='subtract',
            operands=['v1', '3'], result_variable='v2',
            dependencies=['s1'], position=1
        )
        sp3 = SubProblem(
            id='s3', text='add', operation='add',
            operands=['v2', '5'], result_variable='v3',
            dependencies=['s2'], position=2
        )

        graph = DecompositionGraph(sub_problems={'s1': sp1, 's2': sp2, 's3': sp3})

        assert graph.root_ids == ['s1']
        assert graph.terminal_ids == ['s3']
        assert graph.execution_order == ['s1', 's2', 's3']

    def test_graph_with_merge(self):
        """Test graph with merging branches."""
        sp1 = SubProblem(
            id='s1', text='tier1', operation='multiply',
            operands=['40', '10'], result_variable='v1', position=0
        )
        sp2 = SubProblem(
            id='s2', text='tier2', operation='multiply',
            operands=['10', '15'], result_variable='v2', position=1
        )
        sp3 = SubProblem(
            id='s3', text='total', operation='add',
            operands=['v1', 'v2'], result_variable='v3',
            dependencies=['s1', 's2'], position=2
        )

        graph = DecompositionGraph(sub_problems={'s1': sp1, 's2': sp2, 's3': sp3})

        assert set(graph.root_ids) == {'s1', 's2'}
        assert graph.terminal_ids == ['s3']

    def test_get_dependencies_for(self):
        """Test getting dependencies for a sub-problem."""
        sp1 = SubProblem(id='s1', text='', operation='initial',
                         operands=['10'], result_variable='v1')
        sp2 = SubProblem(id='s2', text='', operation='subtract',
                         operands=['v1', '3'], result_variable='v2',
                         dependencies=['s1'])

        graph = DecompositionGraph(sub_problems={'s1': sp1, 's2': sp2})
        deps = graph.get_dependencies_for('s2')

        assert len(deps) == 1
        assert deps[0].id == 's1'

    def test_get_dependents_of(self):
        """Test getting dependents of a sub-problem."""
        sp1 = SubProblem(id='s1', text='', operation='initial',
                         operands=['10'], result_variable='v1')
        sp2 = SubProblem(id='s2', text='', operation='subtract',
                         operands=['v1', '3'], result_variable='v2',
                         dependencies=['s1'])

        graph = DecompositionGraph(sub_problems={'s1': sp1, 's2': sp2})
        dependents = graph.get_dependents_of('s1')

        assert len(dependents) == 1
        assert dependents[0].id == 's2'

    def test_get_execution_chain(self):
        """Test getting execution chain."""
        sp1 = SubProblem(id='s1', text='', operation='initial',
                         operands=['10'], result_variable='v1')
        sp2 = SubProblem(id='s2', text='', operation='subtract',
                         operands=['v1', '3'], result_variable='v2',
                         dependencies=['s1'])

        graph = DecompositionGraph(sub_problems={'s1': sp1, 's2': sp2})
        chain = graph.get_execution_chain()

        assert len(chain) == 2
        assert chain[0].id == 's1'
        assert chain[1].id == 's2'

    def test_step_count(self):
        """Test step count."""
        sp1 = SubProblem(id='s1', text='', operation='initial',
                         operands=['10'], result_variable='v1')
        sp2 = SubProblem(id='s2', text='', operation='add',
                         operands=['v1', '5'], result_variable='v2',
                         dependencies=['s1'])

        graph = DecompositionGraph(sub_problems={'s1': sp1, 's2': sp2})
        assert graph.step_count() == 2

    def test_is_empty(self):
        """Test empty graph check."""
        empty_graph = DecompositionGraph(sub_problems={})
        assert empty_graph.is_empty()

        non_empty = DecompositionGraph(
            sub_problems={'s1': SubProblem(
                id='s1', text='', operation='initial',
                operands=['5'], result_variable='v1'
            )}
        )
        assert not non_empty.is_empty()


class TestProblemDecomposer:
    """Tests for ProblemDecomposer class."""

    @pytest.fixture
    def decomposer(self):
        """Create a ProblemDecomposer instance."""
        return ProblemDecomposer()

    # Single-step decomposition tests
    def test_decompose_single_step(self, decomposer):
        """Test decomposition of single-step problem."""
        text = "What is 5 + 3?"
        graph = decomposer.decompose(text)

        assert graph.step_count() >= 1
        assert graph.structure_type == StructureType.SINGLE_STEP

    # Sequential chain decomposition tests
    def test_decompose_sequential_simple(self, decomposer):
        """Test simple sequential decomposition."""
        text = "John has 10 apples. He eats 3. Then he buys 5 more."
        graph = decomposer.decompose(text)

        assert graph.step_count() >= 2
        assert graph.structure_type == StructureType.SEQUENTIAL_CHAIN

    def test_decompose_sequential_dependencies(self, decomposer):
        """Test sequential dependencies are correct."""
        text = "She started with 100. Spent 30. Then earned 50."
        graph = decomposer.decompose(text)

        if graph.step_count() >= 2:
            # Verify chain structure
            for sp_id in graph.execution_order[1:]:
                sp = graph.sub_problems[sp_id]
                assert len(sp.dependencies) >= 1

    # Iterative rate decomposition tests
    def test_decompose_iterative_rate(self, decomposer):
        """Test iterative rate problem decomposition."""
        text = "He earns $50 per day for 5 days."
        graph = decomposer.decompose(text)

        assert graph.structure_type == StructureType.ITERATIVE_RATE
        # Should result in multiplication
        operations = [sp.operation for sp in graph.sub_problems.values()]
        assert 'multiply' in operations

    # Conditional tiered decomposition tests
    def test_decompose_conditional_tiered(self, decomposer):
        """Test conditional/tiered problem decomposition."""
        text = "He works 50 hours. First 40 hours at $10/hr, rest at $15/hr."
        graph = decomposer.decompose(text)

        assert graph.structure_type == StructureType.CONDITIONAL_TIERED
        # Should have multiple tiers plus merge
        assert graph.step_count() >= 2

    # Execution order tests
    def test_execution_order_valid(self, decomposer):
        """Test that execution order respects dependencies."""
        text = "Start with 20. Subtract 5. Add 10. Multiply by 2."
        graph = decomposer.decompose(text)

        # Build position map
        order_pos = {sp_id: i for i, sp_id in enumerate(graph.execution_order)}

        # Verify dependencies come before dependents
        for sp in graph.sub_problems.values():
            for dep_id in sp.dependencies:
                if dep_id in order_pos:
                    assert order_pos[dep_id] < order_pos[sp.id]

    # Operation detection tests
    def test_detect_operation_subtract(self, decomposer):
        """Test subtraction operation detection."""
        text = "He spent 50 dollars"
        op = decomposer._detect_operation(text)
        assert op == 'subtract'

    def test_detect_operation_add(self, decomposer):
        """Test addition operation detection."""
        text = "She earned 100 dollars"
        op = decomposer._detect_operation(text)
        assert op == 'add'

    def test_detect_operation_multiply(self, decomposer):
        """Test multiplication operation detection."""
        text = "5 times 10"
        op = decomposer._detect_operation(text)
        assert op == 'multiply'

    def test_detect_operation_initial(self, decomposer):
        """Test initial value operation detection."""
        text = "John has 15 apples"
        op = decomposer._detect_operation(text)
        assert op == 'initial'

    # Number extraction tests
    def test_extract_numbers(self, decomposer):
        """Test number extraction."""
        text = "He has 15 apples and $20.50"
        numbers = decomposer._extract_numbers(text)
        assert 15.0 in numbers
        assert 20.5 in numbers

    def test_extract_numbers_with_dollar(self, decomposer):
        """Test number extraction with dollar signs."""
        text = "Paid $100 and received $50"
        numbers = decomposer._extract_numbers(text)
        assert 100.0 in numbers
        assert 50.0 in numbers

    # Graph metadata tests
    def test_graph_has_metadata(self, decomposer):
        """Test that graph contains useful metadata."""
        text = "First he earned $100, then spent $30."
        graph = decomposer.decompose(text)

        assert 'original_text' in graph.metadata
        assert 'confidence' in graph.metadata


class TestProblemDecomposerEdgeCases:
    """Edge case tests for ProblemDecomposer."""

    @pytest.fixture
    def decomposer(self):
        return ProblemDecomposer()

    def test_empty_text(self, decomposer):
        """Test handling of empty text."""
        graph = decomposer.decompose("")
        assert graph.is_empty() or graph.step_count() == 1

    def test_no_numbers(self, decomposer):
        """Test handling of text without numbers."""
        text = "Solve the equation."
        graph = decomposer.decompose(text)
        # Should still produce a graph, even if minimal
        assert isinstance(graph, DecompositionGraph)

    def test_very_long_problem(self, decomposer):
        """Test handling of long problem text."""
        text = "John has 10 apples. " * 20 + "How many total?"
        graph = decomposer.decompose(text)
        assert isinstance(graph, DecompositionGraph)

    def test_unicode_text(self, decomposer):
        """Test handling of unicode characters."""
        text = "Maria has 5 apples. She gives away 2. ¿Cuántas quedan?"
        graph = decomposer.decompose(text)
        assert isinstance(graph, DecompositionGraph)
