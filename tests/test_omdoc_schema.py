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
OMDoc Schema Tests
==================

Comprehensive tests for the OMDoc semantic substrate:
- MathOperator enum
- OMObject (Object Level)
- OMDocStatement (Statement Level)
- OMDocTheory (Theory Level)
- Serialization/Deserialization
- Builder utilities
"""

import pytest
import xml.etree.ElementTree as ET

from symbo_agentic_reasoners.core.omdoc_schema import (
    MathOperator,
    OMObject,
    OMDocStatement,
    OMDocTheory,
    create_variable,
    create_number,
    create_operation,
)


# =============================================================================
# MathOperator Enum Tests
# =============================================================================


class TestMathOperator:
    """Tests for MathOperator enum."""

    def test_arithmetic_operators_exist(self):
        """Arithmetic operators should exist."""
        assert hasattr(MathOperator, 'PLUS')
        assert hasattr(MathOperator, 'MINUS')
        assert hasattr(MathOperator, 'TIMES')
        assert hasattr(MathOperator, 'DIVIDE')
        assert hasattr(MathOperator, 'POWER')

    def test_calculus_operators_exist(self):
        """Calculus operators should exist."""
        assert hasattr(MathOperator, 'DIFF')
        assert hasattr(MathOperator, 'INT')
        assert hasattr(MathOperator, 'DEFINT')

    def test_transcendental_operators_exist(self):
        """Transcendental operators should exist."""
        assert hasattr(MathOperator, 'SIN')
        assert hasattr(MathOperator, 'COS')
        assert hasattr(MathOperator, 'TAN')
        assert hasattr(MathOperator, 'EXP')
        assert hasattr(MathOperator, 'LN')

    def test_logic_operators_exist(self):
        """Logic operators should exist."""
        assert hasattr(MathOperator, 'AND')
        assert hasattr(MathOperator, 'OR')
        assert hasattr(MathOperator, 'NOT')
        assert hasattr(MathOperator, 'IMPLIES')

    def test_relation_operators_exist(self):
        """Relation operators should exist."""
        assert hasattr(MathOperator, 'EQ')
        assert hasattr(MathOperator, 'LT')
        assert hasattr(MathOperator, 'GT')

    def test_operator_values_format(self):
        """Operator values should follow cd.name format."""
        for op in MathOperator:
            assert '.' in op.value
            parts = op.value.split('.')
            assert len(parts) == 2
            assert len(parts[0]) > 0
            assert len(parts[1]) > 0


# =============================================================================
# OMObject Tests
# =============================================================================


class TestOMObject:
    """Tests for OMObject class."""

    def test_create_variable(self):
        """Should create variable OMObject."""
        obj = OMObject(variable='x')

        assert obj.variable == 'x'
        assert obj.value is None
        assert obj.operator is None

    def test_create_integer_value(self):
        """Should create integer value OMObject."""
        obj = OMObject(value=42)

        assert obj.value == 42
        assert obj.variable is None
        assert obj.operator is None

    def test_create_float_value(self):
        """Should create float value OMObject."""
        obj = OMObject(value=3.14)

        assert obj.value == 3.14

    def test_create_string_value(self):
        """Should create string value OMObject."""
        obj = OMObject(value="hello")

        assert obj.value == "hello"

    def test_create_operation(self):
        """Should create operation OMObject."""
        x = OMObject(variable='x')
        two = OMObject(value=2)
        power = OMObject(
            operator=MathOperator.POWER,
            operands=[x, two]
        )

        assert power.operator == MathOperator.POWER
        assert len(power.operands) == 2

    def test_nested_operation(self):
        """Should create nested operations."""
        # Create x^2 + y
        x = OMObject(variable='x')
        two = OMObject(value=2)
        x_squared = OMObject(
            operator=MathOperator.POWER,
            operands=[x, two]
        )
        y = OMObject(variable='y')
        expr = OMObject(
            operator=MathOperator.PLUS,
            operands=[x_squared, y]
        )

        assert expr.operator == MathOperator.PLUS
        assert len(expr.operands) == 2
        assert expr.operands[0].operator == MathOperator.POWER


class TestOMObjectSerialization:
    """Tests for OMObject serialization."""

    def test_serialize_variable(self):
        """Should serialize variable."""
        obj = OMObject(variable='x')
        data = obj.serialize()

        assert data['variable'] == 'x'

    def test_serialize_value(self):
        """Should serialize value."""
        obj = OMObject(value=42)
        data = obj.serialize()

        assert data['value'] == 42

    def test_serialize_operation(self):
        """Should serialize operation."""
        x = OMObject(variable='x')
        y = OMObject(variable='y')
        plus = OMObject(
            operator=MathOperator.PLUS,
            operands=[x, y]
        )
        data = plus.serialize()

        assert data['operator'] == 'arith1.plus'
        assert len(data['operands']) == 2

    def test_deserialize_variable(self):
        """Should deserialize variable."""
        data = {'variable': 'x'}
        obj = OMObject.deserialize(data)

        assert obj.variable == 'x'

    def test_deserialize_value(self):
        """Should deserialize value."""
        data = {'value': 42}
        obj = OMObject.deserialize(data)

        assert obj.value == 42

    def test_deserialize_operation(self):
        """Should deserialize operation."""
        data = {
            'operator': 'arith1.plus',
            'operands': [
                {'variable': 'x'},
                {'value': 1}
            ]
        }
        obj = OMObject.deserialize(data)

        assert obj.operator == MathOperator.PLUS
        assert len(obj.operands) == 2
        assert obj.operands[0].variable == 'x'
        assert obj.operands[1].value == 1

    def test_roundtrip_serialization(self):
        """Serialize then deserialize should give equivalent object."""
        original = OMObject(
            operator=MathOperator.TIMES,
            operands=[
                OMObject(variable='x'),
                OMObject(value=5)
            ]
        )

        data = original.serialize()
        restored = OMObject.deserialize(data)

        assert restored.operator == original.operator
        assert len(restored.operands) == len(original.operands)

    def test_deserialize_invalid_raises(self):
        """Should raise on invalid data."""
        with pytest.raises(ValueError):
            OMObject.deserialize({})


class TestOMObjectXML:
    """Tests for OMObject XML serialization."""

    def test_variable_to_xml(self):
        """Variable should serialize to OMV element."""
        obj = OMObject(variable='x')
        xml = obj.to_openmath_xml()

        assert xml.tag == 'OMV'
        assert xml.get('name') == 'x'

    def test_integer_to_xml(self):
        """Integer should serialize to OMI element."""
        obj = OMObject(value=42)
        xml = obj.to_openmath_xml()

        assert xml.tag == 'OMI'
        assert xml.text == '42'

    def test_float_to_xml(self):
        """Float should serialize to OMF element."""
        obj = OMObject(value=3.14)
        xml = obj.to_openmath_xml()

        assert xml.tag == 'OMF'
        assert 'dec' in xml.attrib

    def test_string_to_xml(self):
        """String should serialize to OMSTR element."""
        obj = OMObject(value="hello")
        xml = obj.to_openmath_xml()

        assert xml.tag == 'OMSTR'
        assert xml.text == 'hello'

    def test_operation_to_xml(self):
        """Operation should serialize to OMA element."""
        obj = OMObject(
            operator=MathOperator.PLUS,
            operands=[
                OMObject(variable='x'),
                OMObject(value=1)
            ]
        )
        xml = obj.to_openmath_xml()

        assert xml.tag == 'OMA'
        # First child is OMS (operator symbol)
        assert xml[0].tag == 'OMS'
        assert xml[0].get('cd') == 'arith1'
        assert xml[0].get('name') == 'plus'

    def test_to_xml_string(self):
        """Should convert to XML string."""
        obj = OMObject(variable='x')
        xml_str = obj.to_xml_string()

        assert isinstance(xml_str, str)
        assert 'OMV' in xml_str
        assert 'name="x"' in xml_str

    def test_empty_object_raises(self):
        """Empty object should raise on XML conversion."""
        obj = OMObject()
        with pytest.raises(ValueError):
            obj.to_openmath_xml()


class TestOMObjectRepr:
    """Tests for OMObject string representation."""

    def test_variable_repr(self):
        """Variable should have Var() repr."""
        obj = OMObject(variable='x')
        assert repr(obj) == 'Var(x)'

    def test_value_repr(self):
        """Value should have Val() repr."""
        obj = OMObject(value=42)
        assert repr(obj) == 'Val(42)'

    def test_operator_repr(self):
        """Operator should have NAME() repr."""
        obj = OMObject(
            operator=MathOperator.PLUS,
            operands=[OMObject(variable='x'), OMObject(variable='y')]
        )
        assert 'PLUS' in repr(obj)

    def test_empty_repr(self):
        """Empty object should have empty repr."""
        obj = OMObject()
        assert 'empty' in repr(obj)


# =============================================================================
# OMDocStatement Tests
# =============================================================================


class TestOMDocStatement:
    """Tests for OMDocStatement class."""

    def test_create_theorem(self):
        """Should create theorem statement."""
        content = OMObject(variable='x')
        stmt = OMDocStatement(
            statement_type='theorem',
            name='TestTheorem',
            content=content,
            theory_context='TestTheory'
        )

        assert stmt.statement_type == 'theorem'
        assert stmt.name == 'TestTheorem'
        assert stmt.content is content
        assert stmt.theory_context == 'TestTheory'

    def test_create_definition(self):
        """Should create definition statement."""
        content = OMObject(value=0)
        stmt = OMDocStatement(
            statement_type='definition',
            name='Zero',
            content=content,
            theory_context='Arithmetic'
        )

        assert stmt.statement_type == 'definition'

    def test_statement_with_dependencies(self):
        """Should create statement with dependencies."""
        stmt = OMDocStatement(
            statement_type='lemma',
            name='Lemma1',
            content=OMObject(variable='x'),
            theory_context='Theory',
            dependencies=['Axiom1', 'Axiom2']
        )

        assert len(stmt.dependencies) == 2
        assert 'Axiom1' in stmt.dependencies

    def test_statement_with_metadata(self):
        """Should create statement with metadata."""
        stmt = OMDocStatement(
            statement_type='theorem',
            name='Famous',
            content=OMObject(variable='x'),
            theory_context='Theory',
            metadata={'author': 'Euler', 'year': '1750'}
        )

        assert stmt.metadata['author'] == 'Euler'

    def test_serialize_statement(self):
        """Should serialize statement."""
        stmt = OMDocStatement(
            statement_type='axiom',
            name='Axiom1',
            content=OMObject(variable='a'),
            theory_context='Logic'
        )

        data = stmt.serialize()

        assert data['statement_type'] == 'axiom'
        assert data['name'] == 'Axiom1'
        assert data['theory_context'] == 'Logic'
        assert 'content' in data

    def test_deserialize_statement(self):
        """Should deserialize statement."""
        data = {
            'statement_type': 'proof',
            'name': 'Proof1',
            'content': {'variable': 'p'},
            'theory_context': 'Logic',
            'dependencies': ['Theorem1'],
            'metadata': {'step': '1'}
        }

        stmt = OMDocStatement.deserialize(data)

        assert stmt.statement_type == 'proof'
        assert stmt.name == 'Proof1'
        assert stmt.content.variable == 'p'
        assert stmt.dependencies == ['Theorem1']

    def test_statement_repr(self):
        """Should have proper repr."""
        stmt = OMDocStatement(
            statement_type='theorem',
            name='Big',
            content=OMObject(variable='x'),
            theory_context='Analysis'
        )

        r = repr(stmt)
        assert 'THEOREM' in r
        assert 'Big' in r
        assert 'Analysis' in r


# =============================================================================
# OMDocTheory Tests
# =============================================================================


class TestOMDocTheory:
    """Tests for OMDocTheory class."""

    def test_create_theory(self):
        """Should create theory."""
        theory = OMDocTheory(name='Algebra')

        assert theory.name == 'Algebra'
        assert theory.imports == []
        assert theory.statements == []
        assert theory.symbols == {}

    def test_theory_with_imports(self):
        """Should create theory with imports."""
        theory = OMDocTheory(
            name='Calculus',
            imports=['RealAnalysis', 'Topology']
        )

        assert len(theory.imports) == 2
        assert 'RealAnalysis' in theory.imports

    def test_add_statement(self):
        """Should add statement to theory."""
        theory = OMDocTheory(name='Test')
        stmt = OMDocStatement(
            statement_type='theorem',
            name='T1',
            content=OMObject(variable='x'),
            theory_context='Test'
        )

        theory.add_statement(stmt)

        assert len(theory.statements) == 1
        assert theory.statements[0].name == 'T1'

    def test_add_statement_wrong_context_raises(self):
        """Should raise if statement has wrong context."""
        theory = OMDocTheory(name='Theory1')
        stmt = OMDocStatement(
            statement_type='theorem',
            name='T1',
            content=OMObject(variable='x'),
            theory_context='Theory2'  # Different from theory
        )

        with pytest.raises(ValueError):
            theory.add_statement(stmt)

    def test_add_symbol(self):
        """Should add symbol to theory."""
        theory = OMDocTheory(name='Constants')
        pi = OMObject(value=3.14159)

        theory.add_symbol('pi', pi)

        assert 'pi' in theory.symbols
        assert theory.symbols['pi'].value == 3.14159

    def test_serialize_theory(self):
        """Should serialize theory."""
        theory = OMDocTheory(
            name='Test',
            imports=['Base'],
            metadata={'version': '1.0'}
        )
        theory.add_symbol('x', OMObject(variable='x'))

        data = theory.serialize()

        assert data['name'] == 'Test'
        assert data['imports'] == ['Base']
        assert 'x' in data['symbols']
        assert data['metadata']['version'] == '1.0'

    def test_deserialize_theory(self):
        """Should deserialize theory."""
        data = {
            'name': 'Restored',
            'imports': ['Dep1'],
            'statements': [
                {
                    'statement_type': 'axiom',
                    'name': 'A1',
                    'content': {'variable': 'a'},
                    'theory_context': 'Restored'
                }
            ],
            'symbols': {'pi': {'value': 3.14}},
            'metadata': {}
        }

        theory = OMDocTheory.deserialize(data)

        assert theory.name == 'Restored'
        assert len(theory.statements) == 1
        assert 'pi' in theory.symbols

    def test_theory_repr(self):
        """Should have proper repr."""
        theory = OMDocTheory(
            name='Big',
            imports=['Small']
        )
        theory.add_symbol('x', OMObject(variable='x'))

        r = repr(theory)
        assert 'Big' in r
        assert 'symbols=1' in r
        assert 'Small' in r


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Tests for helper/factory functions."""

    def test_create_variable(self):
        """create_variable should return OMObject with variable."""
        obj = create_variable('x')

        assert isinstance(obj, OMObject)
        assert obj.variable == 'x'

    def test_create_number_int(self):
        """create_number should handle integers."""
        obj = create_number(42)

        assert isinstance(obj, OMObject)
        assert obj.value == 42

    def test_create_number_float(self):
        """create_number should handle floats."""
        obj = create_number(3.14)

        assert isinstance(obj, OMObject)
        assert obj.value == 3.14

    def test_create_operation(self):
        """create_operation should build operation OMObject."""
        x = create_variable('x')
        y = create_variable('y')
        plus = create_operation(MathOperator.PLUS, x, y)

        assert isinstance(plus, OMObject)
        assert plus.operator == MathOperator.PLUS
        assert len(plus.operands) == 2


# =============================================================================
# Integration Tests
# =============================================================================


class TestOMDocIntegration:
    """Integration tests for OMDoc system."""

    def test_build_polynomial_expression(self):
        """Build x^2 + 2x + 1."""
        x = create_variable('x')
        one = create_number(1)
        two = create_number(2)

        # x^2
        x_squared = create_operation(MathOperator.POWER, x, two)

        # 2x
        two_x = create_operation(MathOperator.TIMES, two, x)

        # x^2 + 2x
        partial = create_operation(MathOperator.PLUS, x_squared, two_x)

        # x^2 + 2x + 1
        full = create_operation(MathOperator.PLUS, partial, one)

        assert full.operator == MathOperator.PLUS

        # Can serialize/deserialize
        data = full.serialize()
        restored = OMObject.deserialize(data)
        assert restored.operator == MathOperator.PLUS

    def test_build_calculus_expression(self):
        """Build derivative of sin(x)."""
        x = create_variable('x')
        sin_x = create_operation(MathOperator.SIN, x)
        diff_sin = create_operation(MathOperator.DIFF, sin_x, x)

        assert diff_sin.operator == MathOperator.DIFF

    def test_full_theory_workflow(self):
        """Build a complete theory with statements."""
        theory = OMDocTheory(
            name='BasicAlgebra',
            imports=['Arithmetic'],
            metadata={'author': 'Test'}
        )

        # Add some symbols
        theory.add_symbol('zero', create_number(0))
        theory.add_symbol('one', create_number(1))

        # Create a statement
        x = create_variable('x')
        zero = create_number(0)
        identity = create_operation(MathOperator.PLUS, x, zero)

        stmt = OMDocStatement(
            statement_type='theorem',
            name='AdditionIdentity',
            content=create_operation(MathOperator.EQ, identity, x),
            theory_context='BasicAlgebra',
            dependencies=[],
            metadata={'name': 'Additive Identity'}
        )
        theory.add_statement(stmt)

        # Serialize and restore
        data = theory.serialize()
        restored = OMDocTheory.deserialize(data)

        assert restored.name == 'BasicAlgebra'
        assert len(restored.statements) == 1
        assert len(restored.symbols) == 2


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
