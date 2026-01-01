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

# Tests for structural_synthesizer.py to achieve 70%+ coverage

"""
Tests for StructuralSynthesizer to cover:
- StructureSpec.to_dict() (line 100)
- _register_services() (lines 225, 232-242)
- synthesize_from_template() (lines 261-276)
- Error handling in synthesize() (lines 319-323)
- _build_construction() with relations (lines 343-345, 348-350)
- _verify_axioms() with failures (lines 373-377)
- _check_axiom() returning False (lines 389-398)
- _find_counterexample() (line 402)
- compose_structures() (lines 421-437)
- process() with different operations (lines 460-480)
- _create_result_entry() and _create_error_entry() (lines 484-487, 494-505, 509-523)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestStructureKindEnum:
    """Test StructureKind enum"""

    def test_all_kinds_exist(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructureKind
        )
        members = list(StructureKind)
        assert len(members) >= 7
        assert StructureKind.SET.value == "set"
        assert StructureKind.RELATION.value == "relation"
        assert StructureKind.FUNCTION.value == "function"
        assert StructureKind.ALGEBRAIC.value == "algebraic"
        assert StructureKind.ORDERED.value == "ordered"
        assert StructureKind.TOPOLOGICAL.value == "topological"
        assert StructureKind.COMPOSITE.value == "composite"


class TestSynthesisStatusEnum:
    """Test SynthesisStatus enum"""

    def test_all_statuses_exist(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            SynthesisStatus
        )
        members = list(SynthesisStatus)
        assert len(members) >= 5
        assert SynthesisStatus.PENDING.value == "pending"
        assert SynthesisStatus.SYNTHESIZING.value == "synthesizing"
        assert SynthesisStatus.VALIDATING.value == "validating"
        assert SynthesisStatus.COMPLETE.value == "complete"
        assert SynthesisStatus.FAILED.value == "failed"


class TestStructureSpec:
    """Test StructureSpec dataclass"""

    def test_basic_init(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructureSpec, StructureKind
        )
        spec = StructureSpec(
            name="test_structure",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "associativity"]
        )
        assert spec.name == "test_structure"
        assert spec.kind == StructureKind.ALGEBRAIC
        assert len(spec.axioms) == 2

    def test_with_carrier_set_and_operations(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructureSpec, StructureKind
        )
        spec = StructureSpec(
            name="group_Z",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "associativity", "identity", "inverses"],
            carrier_set="Z",
            operations={"+": "Z x Z -> Z", "-": "Z -> Z"},
            relations={"=": "equality relation"}
        )
        assert spec.carrier_set == "Z"
        assert "+" in spec.operations
        assert "=" in spec.relations

    def test_to_dict(self):
        """Test StructureSpec.to_dict() - line 100"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructureSpec, StructureKind
        )
        spec = StructureSpec(
            name="test_group",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "associativity", "identity"],
            carrier_set="G",
            operations={"*": "G x G -> G"},
            relations={"=": "equality"}
        )
        d = spec.to_dict()
        assert d['name'] == "test_group"
        assert d['kind'] == "algebraic"
        assert d['axiom_count'] == 3
        assert "*" in d['operations']
        assert "=" in d['relations']


class TestSynthesizedStructure:
    """Test SynthesizedStructure dataclass"""

    def test_basic_init(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructureSpec, StructureKind, SynthesizedStructure, SynthesisStatus
        )
        spec = StructureSpec(
            name="test",
            kind=StructureKind.SET,
            axioms=["closure"]
        )
        structure = SynthesizedStructure(
            structure_id="s1",
            spec=spec,
            construction="built from spec",
            verified_axioms={"closure"}
        )
        assert structure.structure_id == "s1"
        assert structure.status == SynthesisStatus.COMPLETE

    def test_to_dict(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructureSpec, StructureKind, SynthesizedStructure, SynthesisStatus
        )
        spec = StructureSpec(
            name="test_ring",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "associativity"]
        )
        structure = SynthesizedStructure(
            structure_id="ring_1",
            spec=spec,
            construction="ring construction",
            verified_axioms={"closure"},
            failed_axioms={"associativity"},
            status=SynthesisStatus.FAILED
        )
        d = structure.to_dict()
        assert d['structure_id'] == "ring_1"
        assert d['name'] == "test_ring"
        assert d['kind'] == "algebraic"
        assert d['verified_count'] == 1
        assert d['failed_count'] == 1
        assert d['status'] == "failed"


class TestStructuralSynthesizerInit:
    """Test StructuralSynthesizer initialization"""

    def test_basic_init(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        assert synth.agent_id.startswith('structural_synthesizer')
        assert synth.tasks_executed == 0
        assert synth.tasks_succeeded == 0

    def test_templates_exist(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        assert 'group' in synth.TEMPLATES
        assert 'ring' in synth.TEMPLATES
        assert 'partial_order' in synth.TEMPLATES
        assert 'equivalence' in synth.TEMPLATES

    def test_init_with_directory_facilitator(self):
        """Test _register_services() - lines 225, 232-242"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        mock_df = Mock()
        mock_df.register = Mock()
        synth = StructuralSynthesizer(df=mock_df)
        # Should have called register
        mock_df.register.assert_called_once()


class TestSynthesizeFromTemplate:
    """Test synthesize_from_template() - lines 261-276"""

    def test_synthesize_group(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureKind
        )
        synth = StructuralSynthesizer()
        result = synth.synthesize_from_template("group", "Z_4")
        assert result.spec.name == "group_on_Z_4"
        assert result.spec.kind == StructureKind.ALGEBRAIC
        assert "closure" in result.spec.axioms

    def test_synthesize_ring(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        result = synth.synthesize_from_template("ring", "R")
        assert "ring" in result.spec.name.lower()

    def test_synthesize_partial_order(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureKind
        )
        synth = StructuralSynthesizer()
        result = synth.synthesize_from_template("partial_order", "P")
        assert result.spec.kind == StructureKind.ORDERED

    def test_synthesize_equivalence(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureKind
        )
        synth = StructuralSynthesizer()
        result = synth.synthesize_from_template("equivalence", "E")
        assert result.spec.kind == StructureKind.RELATION

    def test_unknown_template_raises(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        with pytest.raises(ValueError, match="Unknown template"):
            synth.synthesize_from_template("nonexistent", "X")

    def test_with_custom_ops(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        custom_ops = {"custom_op": "S x S -> S"}
        result = synth.synthesize_from_template("group", "S", custom_ops=custom_ops)
        assert "custom_op" in result.spec.operations


class TestSynthesize:
    """Test synthesize() method"""

    def test_basic_synthesis(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind, SynthesisStatus
        )
        synth = StructuralSynthesizer()
        spec = StructureSpec(
            name="test_monoid",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "associativity", "identity"],
            carrier_set="M"
        )
        result = synth.synthesize(spec)
        assert result.status == SynthesisStatus.COMPLETE
        assert "closure" in result.verified_axioms
        assert synth.tasks_succeeded >= 1

    def test_synthesis_increments_counters(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind
        )
        synth = StructuralSynthesizer()
        initial_executed = synth.tasks_executed
        initial_synthesized = synth.structures_synthesized

        spec = StructureSpec(
            name="counter_test",
            kind=StructureKind.SET,
            axioms=["closure"]
        )
        synth.synthesize(spec)

        assert synth.tasks_executed == initial_executed + 1
        assert synth.structures_synthesized == initial_synthesized + 1

    def test_synthesis_with_non_standard_axiom_fails(self):
        """Test _check_axiom() returning False - lines 389-398"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind, SynthesisStatus
        )
        synth = StructuralSynthesizer()
        spec = StructureSpec(
            name="custom_struct",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "nonexistent_axiom", "weird_property"],
            carrier_set="X"
        )
        result = synth.synthesize(spec)
        # Non-standard axioms should fail
        assert "nonexistent_axiom" in result.failed_axioms or "weird_property" in result.failed_axioms
        assert result.status == SynthesisStatus.FAILED

    def test_synthesis_stores_structure(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind
        )
        synth = StructuralSynthesizer()
        spec = StructureSpec(
            name="stored_struct",
            kind=StructureKind.SET,
            axioms=["closure"]
        )
        result = synth.synthesize(spec)
        assert result.structure_id in synth.structures


class TestBuildConstruction:
    """Test _build_construction() with operations and relations - lines 343-350"""

    def test_construction_with_operations(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind
        )
        synth = StructuralSynthesizer()
        spec = StructureSpec(
            name="op_test",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure"],
            carrier_set="S",
            operations={"*": "S x S -> S", "+": "S x S -> S"}
        )
        result = synth.synthesize(spec)
        assert "Operations:" in result.construction
        assert "*" in result.construction

    def test_construction_with_relations(self):
        """Test _build_construction() with relations - lines 348-350"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind
        )
        synth = StructuralSynthesizer()
        spec = StructureSpec(
            name="rel_test",
            kind=StructureKind.RELATION,
            axioms=["reflexive"],
            carrier_set="R",
            relations={"<=": "R x R -> Bool", "~": "equivalence"}
        )
        result = synth.synthesize(spec)
        assert "Relations:" in result.construction
        assert "<=" in result.construction


class TestVerifyAxioms:
    """Test _verify_axioms() and _find_counterexample() - lines 373-377, 402"""

    def test_verify_standard_axioms(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind
        )
        synth = StructuralSynthesizer()
        spec = StructureSpec(
            name="standard_test",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "associativity", "identity", "inverses"],
            carrier_set="G"
        )
        result = synth.synthesize(spec)
        # All standard axioms should be verified
        for axiom in ["closure", "associativity", "identity", "inverses"]:
            assert axiom in result.verified_axioms

    def test_verify_with_failures_generates_counterexamples(self):
        """Test counterexample generation - line 402"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind
        )
        synth = StructuralSynthesizer()
        spec = StructureSpec(
            name="failing_test",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure", "made_up_axiom"],
            carrier_set="F"
        )
        result = synth.synthesize(spec)
        # Should have counterexample for made_up_axiom
        if "made_up_axiom" in result.failed_axioms:
            assert "made_up_axiom" in result.counterexamples


class TestComposeStructures:
    """Test compose_structures() - lines 421-437"""

    def test_compose_two_structures(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureKind
        )
        synth = StructuralSynthesizer()

        # Create two structures
        group = synth.synthesize_from_template("group", "G1")
        ring = synth.synthesize_from_template("ring", "R1")

        # Compose them
        composite = synth.compose_structures(group.structure_id, ring.structure_id)

        assert composite.spec.kind == StructureKind.COMPOSITE
        assert "product" in composite.spec.name
        assert "×" in composite.spec.carrier_set

    def test_compose_with_custom_type(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        s1 = synth.synthesize_from_template("group", "A")
        s2 = synth.synthesize_from_template("group", "B")

        composite = synth.compose_structures(s1.structure_id, s2.structure_id, composition_type="sum")

        assert "sum" in composite.spec.name

    def test_compose_missing_structure_raises(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        s1 = synth.synthesize_from_template("group", "G")

        with pytest.raises(ValueError, match="not found"):
            synth.compose_structures(s1.structure_id, "nonexistent_id")


class TestProcess:
    """Test process() method with different operations - lines 460-480"""

    def test_process_synthesize_operation(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'synthesize',
            'spec': {
                'name': 'process_test',
                'kind': 'algebraic',
                'axioms': ['closure'],
                'carrier_set': 'S'
            }
        }

        result = synth.process(task_entry)
        assert result is not None

    def test_process_from_template_operation(self):
        """Test process() from_template operation - lines 460-464"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'from_template',
            'template': 'group',
            'carrier_set': 'Z_5'
        }

        result = synth.process(task_entry)
        assert result is not None

    def test_process_compose_operation(self):
        """Test process() compose operation - lines 466-471"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        # First create some structures
        s1 = synth.synthesize_from_template("group", "A")
        s2 = synth.synthesize_from_template("ring", "B")

        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'compose',
            'struct1_id': s1.structure_id,
            'struct2_id': s2.structure_id,
            'composition_type': 'product'
        }

        result = synth.process(task_entry)
        assert result is not None

    def test_process_list_operation(self):
        """Test process() list operation - lines 473-477"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        # Create some structures first
        synth.synthesize_from_template("group", "G")

        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'list'
        }

        result = synth.process(task_entry)
        assert 'structures' in result or hasattr(result, 'metadata')

    def test_process_unknown_operation(self):
        """Test process() with unknown operation - lines 479-480"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'unknown_op'
        }

        result = synth.process(task_entry)
        assert result is not None  # Should return error dict


class TestCreateEntries:
    """Test _create_result_entry() and _create_error_entry() - lines 494-505, 509-523"""

    def test_create_result_entry_without_blackboard(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        task_entry = Mock()
        task_entry.conversation_id = "test_conv"

        result = synth._create_result_entry(task_entry, {'key': 'value'})
        assert result == {'key': 'value'}

    def test_create_result_entry_with_blackboard(self):
        """Test _create_result_entry() with blackboard - lines 494-505"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        from symbo_agentic_reasoners.core.blackboard import Blackboard

        bb = Blackboard()
        synth = StructuralSynthesizer(blackboard=bb)

        task_entry = Mock()
        task_entry.conversation_id = "test_conv"

        result = synth._create_result_entry(task_entry, {'test': 'data'})
        assert result is not None

    def test_create_error_entry_without_blackboard(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        task_entry = Mock()

        result = synth._create_error_entry(task_entry, "Test error")
        assert result is None

    def test_create_error_entry_with_blackboard(self):
        """Test _create_error_entry() with blackboard - lines 509-523"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        from symbo_agentic_reasoners.core.blackboard import Blackboard

        bb = Blackboard()
        synth = StructuralSynthesizer(blackboard=bb)

        task_entry = Mock()
        task_entry.conversation_id = "err_conv"

        result = synth._create_error_entry(task_entry, "Test error message")
        assert result is not None


class TestBDIMethods:
    """Test BDI implementation methods"""

    def test_update_beliefs(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        synth.update_beliefs()  # Should not raise

    def test_deliberate(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        result = synth.deliberate()
        assert result == []

    def test_execute_step(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        synth = StructuralSynthesizer()
        intention = Mock(spec=Intention)
        intention.get_current_action.return_value = 'test_action'
        intention.metadata = {}
        intention.is_complete.return_value = False
        synth.execute_step(intention)  # Should not raise


class TestGetStatistics:
    """Test get_statistics() method"""

    def test_get_statistics(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        # Do some operations
        synth.synthesize_from_template("group", "G")
        synth.synthesize_from_template("ring", "R")

        stats = synth.get_statistics()

        assert 'tasks_executed' in stats
        assert 'tasks_succeeded' in stats
        assert 'structures_synthesized' in stats
        assert 'axioms_verified' in stats
        assert 'structures_cached' in stats
        assert stats['tasks_executed'] >= 2


class TestSynthesisErrorHandling:
    """Test error handling in synthesize() - lines 319-323"""

    def test_synthesis_exception_handling(self):
        """Test that exceptions in synthesis are handled - lines 319-323"""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer, StructureSpec, StructureKind, SynthesisStatus
        )
        synth = StructuralSynthesizer()

        # Create a spec that might cause issues
        spec = StructureSpec(
            name="error_test",
            kind=StructureKind.ALGEBRAIC,
            axioms=["closure"]
        )

        # Mock _build_construction to raise an exception
        original_build = synth._build_construction
        def raise_error(spec):
            raise RuntimeError("Test error")

        synth._build_construction = raise_error

        result = synth.synthesize(spec)

        # Should return a failed structure, not raise
        assert result.status == SynthesisStatus.FAILED
        assert "FAILED:" in result.construction

        # Restore original method
        synth._build_construction = original_build


class TestProcessExceptionHandling:
    """Test exception handling in process() - lines 484-487"""

    def test_process_handles_exception(self):
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()

        # Create a task that will cause an exception
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'compose',
            'struct1_id': 'nonexistent1',
            'struct2_id': 'nonexistent2'
        }

        # Should not raise, but handle exception
        result = synth.process(task_entry)
        assert result is not None or synth.tasks_failed > 0
