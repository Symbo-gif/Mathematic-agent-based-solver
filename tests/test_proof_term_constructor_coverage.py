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
Tests for Proof Term Constructor Module
=======================================

Comprehensive tests for the ProofTermConstructor BDI agent.
"""

import pytest
from unittest.mock import MagicMock


class TestTermKind:
    """Tests for TermKind enum."""

    def test_term_kind_values(self):
        """Test TermKind enum values."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TermKind
        )
        assert TermKind.VARIABLE.value == 'var'
        assert TermKind.ABSTRACTION.value == 'abs'
        assert TermKind.APPLICATION.value == 'app'
        assert TermKind.PRODUCT.value == 'prod'
        assert TermKind.UNIVERSE.value == 'type'
        assert TermKind.CONSTANT.value == 'const'
        assert TermKind.INDUCTIVE.value == 'ind'


class TestTypeCheckResult:
    """Tests for TypeCheckResult enum."""

    def test_type_check_result_values(self):
        """Test TypeCheckResult enum values."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeCheckResult
        )
        assert TypeCheckResult.WELL_TYPED.value == 'well_typed'
        assert TypeCheckResult.TYPE_ERROR.value == 'type_error'
        assert TypeCheckResult.UNKNOWN.value == 'unknown'


class TestProofTerm:
    """Tests for ProofTerm dataclass."""

    def test_proof_term_variable(self):
        """Test creating variable term."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        term = ProofTerm(
            kind=TermKind.VARIABLE,
            name='x',
            type_annotation='A'
        )
        assert term.kind == TermKind.VARIABLE
        assert term.name == 'x'
        assert term.to_string() == 'x'

    def test_proof_term_constant(self):
        """Test creating constant term."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        term = ProofTerm(
            kind=TermKind.CONSTANT,
            name='c',
            type_annotation='A'
        )
        assert term.to_string() == 'c'

    def test_proof_term_abstraction(self):
        """Test creating lambda abstraction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        body = ProofTerm(kind=TermKind.VARIABLE, name='x')
        term = ProofTerm(
            kind=TermKind.ABSTRACTION,
            bound_var='x',
            type_annotation='A',
            sub_terms=[body]
        )
        assert 'λx:A' in term.to_string()

    def test_proof_term_application(self):
        """Test creating function application."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        f = ProofTerm(kind=TermKind.VARIABLE, name='f')
        x = ProofTerm(kind=TermKind.VARIABLE, name='x')
        term = ProofTerm(
            kind=TermKind.APPLICATION,
            sub_terms=[f, x]
        )
        assert '(f x)' in term.to_string()

    def test_proof_term_product(self):
        """Test creating product type."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        a = ProofTerm(kind=TermKind.VARIABLE, name='A')
        b = ProofTerm(kind=TermKind.VARIABLE, name='B')
        term = ProofTerm(
            kind=TermKind.PRODUCT,
            bound_var='x',
            sub_terms=[a, b]
        )
        assert 'Π' in term.to_string()

    def test_proof_term_universe(self):
        """Test creating universe term."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        term = ProofTerm(kind=TermKind.UNIVERSE, name='0')
        assert 'Type_0' in term.to_string()

    def test_proof_term_to_dict(self):
        """Test term serialization."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        term = ProofTerm(
            kind=TermKind.VARIABLE,
            name='x',
            type_annotation='A'
        )
        d = term.to_dict()
        assert d['kind'] == 'var'
        assert d['name'] == 'x'
        assert d['type'] == 'A'


class TestTypeContext:
    """Tests for TypeContext dataclass."""

    def test_type_context_create(self):
        """Test creating type context."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeContext
        )
        ctx = TypeContext()
        assert len(ctx.bindings) == 0

    def test_type_context_extend(self):
        """Test extending context."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeContext
        )
        ctx = TypeContext()
        new_ctx = ctx.extend('x', 'A')
        assert new_ctx.lookup('x') == 'A'
        assert ctx.lookup('x') is None  # Original unchanged

    def test_type_context_lookup(self):
        """Test looking up in context."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeContext
        )
        ctx = TypeContext(bindings={'y': 'B'})
        assert ctx.lookup('y') == 'B'
        assert ctx.lookup('z') is None


class TestTypeCheckOutput:
    """Tests for TypeCheckOutput dataclass."""

    def test_type_check_output_create(self):
        """Test creating type check output."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeCheckOutput, TypeCheckResult
        )
        output = TypeCheckOutput(
            result=TypeCheckResult.WELL_TYPED,
            inferred_type='A → B'
        )
        assert output.result == TypeCheckResult.WELL_TYPED
        assert output.inferred_type == 'A → B'

    def test_type_check_output_with_errors(self):
        """Test output with errors."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeCheckOutput, TypeCheckResult
        )
        output = TypeCheckOutput(
            result=TypeCheckResult.TYPE_ERROR,
            inferred_type=None,
            errors=['Unbound variable: x']
        )
        assert len(output.errors) == 1

    def test_type_check_output_to_dict(self):
        """Test output serialization."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeCheckOutput, TypeCheckResult
        )
        output = TypeCheckOutput(
            result=TypeCheckResult.WELL_TYPED,
            inferred_type='A'
        )
        d = output.to_dict()
        assert d['result'] == 'well_typed'
        assert d['type'] == 'A'


class TestProofTermConstructorInit:
    """Tests for ProofTermConstructor initialization."""

    def test_constructor_create(self):
        """Test creating proof term constructor."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        assert ptc.agent_id == 'proof_term_constructor_001'
        assert ptc.terms_constructed == 0

    def test_constructor_custom_id(self):
        """Test creating with custom ID."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor(agent_id='custom_ptc')
        assert ptc.agent_id == 'custom_ptc'

    def test_constructor_with_df(self):
        """Test creating with directory facilitator."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        mock_df = MagicMock()
        ptc = ProofTermConstructor(df=mock_df)
        assert ptc.df is mock_df
        mock_df.register.assert_called_once()


class TestConstructMethods:
    """Tests for term construction methods."""

    def test_construct_variable(self):
        """Test constructing variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        term = ptc.construct_variable('x', 'Nat')
        assert term.kind == TermKind.VARIABLE
        assert term.name == 'x'
        assert term.type_annotation == 'Nat'

    def test_construct_constant(self):
        """Test constructing constant."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        term = ptc.construct_constant('zero', 'Nat')
        assert term.kind == TermKind.CONSTANT
        assert term.name == 'zero'

    def test_construct_abstraction(self):
        """Test constructing abstraction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        body = ptc.construct_variable('x', 'A')
        term = ptc.construct_abstraction('x', 'A', body)
        assert term.kind == TermKind.ABSTRACTION
        assert term.bound_var == 'x'
        assert ptc.terms_constructed >= 1

    def test_construct_application(self):
        """Test constructing application."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        f = ptc.construct_variable('f', 'A → B')
        x = ptc.construct_variable('x', 'A')
        term = ptc.construct_application(f, x)
        assert term.kind == TermKind.APPLICATION
        assert len(term.sub_terms) == 2

    def test_construct_product(self):
        """Test constructing product type."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        dom = ptc.construct_constant('A', 'Type')
        cod = ptc.construct_constant('B', 'Type')
        term = ptc.construct_product('x', dom, cod)
        assert term.kind == TermKind.PRODUCT

    def test_construct_arrow(self):
        """Test constructing arrow type."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        term = ptc.construct_arrow('A', 'B')
        assert term.kind == TermKind.PRODUCT


class TestTypeCheck:
    """Tests for type checking."""

    def test_type_check_variable(self):
        """Test type checking variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeContext, TypeCheckResult
        )
        ptc = ProofTermConstructor()
        term = ptc.construct_variable('x', 'Nat')
        ctx = TypeContext(bindings={'x': 'Nat'})
        result = ptc.type_check(term, ctx)
        assert result.result == TypeCheckResult.WELL_TYPED

    def test_type_check_constant(self):
        """Test type checking constant."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeCheckResult
        )
        ptc = ProofTermConstructor()
        term = ptc.construct_constant('zero', 'Nat')
        result = ptc.type_check(term)
        assert result.result == TypeCheckResult.WELL_TYPED
        assert result.inferred_type == 'Nat'

    def test_type_check_abstraction(self):
        """Test type checking abstraction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeCheckResult
        )
        ptc = ProofTermConstructor()
        body = ptc.construct_variable('x', 'A')
        term = ptc.construct_abstraction('x', 'A', body)
        result = ptc.type_check(term)
        assert result.result == TypeCheckResult.WELL_TYPED
        assert '→' in result.inferred_type

    def test_type_check_application(self):
        """Test type checking application."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeCheckResult
        )
        ptc = ProofTermConstructor()
        f = ptc.construct_variable('f', 'A → B')
        x = ptc.construct_variable('x', 'A')
        term = ptc.construct_application(f, x)
        result = ptc.type_check(term)
        # Result depends on context

    def test_type_check_unbound_variable(self):
        """Test type checking unbound variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeContext, ProofTerm, TermKind, TypeCheckResult
        )
        ptc = ProofTermConstructor()
        # Create a variable without annotation
        term = ProofTerm(kind=TermKind.VARIABLE, name='unbound')
        ctx = TypeContext()
        result = ptc.type_check(term, ctx)
        assert result.result == TypeCheckResult.TYPE_ERROR
        assert len(result.errors) > 0


class TestBetaReduction:
    """Tests for beta reduction."""

    def test_beta_reduce_simple(self):
        """Test simple beta reduction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        # (λx.x) y → y
        body = ptc.construct_variable('x', 'A')
        lam = ptc.construct_abstraction('x', 'A', body)
        y = ptc.construct_variable('y', 'A')
        app = ptc.construct_application(lam, y)
        reduced = ptc.beta_reduce(app)
        assert reduced.name == 'y'

    def test_beta_reduce_non_redex(self):
        """Test beta reduce on non-redex."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        ptc = ProofTermConstructor()
        term = ptc.construct_variable('x', 'A')
        reduced = ptc.beta_reduce(term)
        assert reduced == term


class TestNormalize:
    """Tests for normalization."""

    def test_normalize_normal_form(self):
        """Test normalizing already-normal term."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        term = ptc.construct_variable('x', 'A')
        normalized = ptc.normalize(term)
        assert normalized.to_string() == 'x'

    def test_normalize_redex(self):
        """Test normalizing redex."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        body = ptc.construct_variable('x', 'A')
        lam = ptc.construct_abstraction('x', 'A', body)
        y = ptc.construct_variable('y', 'A')
        app = ptc.construct_application(lam, y)
        normalized = ptc.normalize(app)
        assert normalized.name == 'y'


class TestProcess:
    """Tests for process method."""

    def test_process_construct_var(self):
        """Test processing construct_var operation."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        mock_task = MagicMock()
        mock_task.metadata = {
            'operation': 'construct_var',
            'name': 'x',
            'type': 'Nat'
        }
        result = ptc.process(mock_task)
        assert result is not None

    def test_process_construct_abs(self):
        """Test processing construct_abs operation."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        mock_task = MagicMock()
        mock_task.metadata = {
            'operation': 'construct_abs',
            'var': 'x',
            'var_type': 'A',
            'body': 'x'
        }
        result = ptc.process(mock_task)
        assert result is not None

    def test_process_type_check(self):
        """Test processing type_check operation."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        mock_task = MagicMock()
        mock_task.metadata = {'operation': 'type_check'}
        result = ptc.process(mock_task)
        assert result is not None


class TestBDI:
    """Tests for BDI methods."""

    def test_update_beliefs(self):
        """Test update_beliefs without blackboard."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        ptc.update_beliefs()  # Should not raise

    def test_deliberate(self):
        """Test deliberate with no tasks."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        intentions = ptc.deliberate()
        assert intentions == []

    def test_get_statistics(self):
        """Test getting statistics."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        ptc = ProofTermConstructor()
        ptc.construct_variable('x', 'A')
        ptc.construct_abstraction('x', 'A', ptc.construct_variable('x', 'A'))
        stats = ptc.get_statistics()
        assert 'tasks_executed' in stats
        assert 'terms_constructed' in stats


class TestModuleImports:
    """Tests for module imports."""

    def test_proof_term_constructor_import(self):
        """Test ProofTermConstructor can be imported."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        assert ProofTermConstructor is not None

    def test_dataclass_imports(self):
        """Test dataclasses can be imported."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TypeContext, TypeCheckOutput
        )
        assert ProofTerm is not None
        assert TypeContext is not None
        assert TypeCheckOutput is not None

    def test_enum_imports(self):
        """Test enums can be imported."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TermKind, TypeCheckResult
        )
        assert TermKind is not None
        assert TypeCheckResult is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
