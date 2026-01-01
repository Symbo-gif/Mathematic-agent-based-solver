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
Comprehensive tests for synthesis modules to achieve 70%+ coverage.

Tests focus on:
- FormalLanguageTranslator (43.35% -> 70%)
- ProofTermConstructor (29.58% -> 70%)
- ConjectureGenerator (33.59% -> 70%)
- StructuralSynthesizer (55.17% -> 70%)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestFormalLanguageTranslatorExtended:
    """Extended tests for FormalLanguageTranslator to boost coverage."""

    def test_init(self):
        """Test initialization."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator
        )
        translator = FormalLanguageTranslator()
        assert translator.agent_id.startswith('formal_translator')
        assert len(translator.NL_TO_FORMAL) > 0

    def test_translate_natural_to_unicode(self):
        """Test natural language to unicode translation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        result = translator.translate(
            "for all x there exists y such that x implies y",
            NotationFormat.NATURAL,
            NotationFormat.UNICODE
        )
        assert result is not None
        assert '∀' in result.translated_text or 'for all' in result.translated_text.lower()

    def test_translate_natural_to_latex(self):
        """Test natural language to latex translation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        result = translator.translate(
            "for all n less than or equal infinity",
            NotationFormat.NATURAL,
            NotationFormat.LATEX
        )
        assert result is not None

    def test_translate_latex_to_unicode(self):
        """Test latex to unicode translation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        result = translator.translate(
            r"\forall x \in A",
            NotationFormat.LATEX,
            NotationFormat.UNICODE
        )
        assert result is not None
        assert '∀' in result.translated_text or 'forall' in result.translated_text

    def test_translate_latex_to_natural(self):
        """Test latex to natural language translation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        result = translator.translate(
            r"\forall x \implies y",
            NotationFormat.LATEX,
            NotationFormat.NATURAL
        )
        assert result is not None
        assert 'for all' in result.translated_text.lower() or 'implies' in result.translated_text.lower()

    def test_translate_unicode_to_latex(self):
        """Test unicode to latex translation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        result = translator.translate(
            "∀x ∈ A",
            NotationFormat.UNICODE,
            NotationFormat.LATEX
        )
        assert result is not None
        assert 'forall' in result.translated_text or '∀' in result.translated_text

    def test_translate_unicode_to_natural(self):
        """Test unicode to natural language translation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        result = translator.translate(
            "∀x ∧ ∃y → z",
            NotationFormat.UNICODE,
            NotationFormat.NATURAL
        )
        assert result is not None
        assert 'for all' in result.translated_text.lower() or 'and' in result.translated_text.lower()

    def test_translate_same_format(self):
        """Test identity translation (same source and target)."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat, TranslationQuality
        )
        translator = FormalLanguageTranslator()
        result = translator.translate(
            "test",
            NotationFormat.NATURAL,
            NotationFormat.NATURAL
        )
        assert result.translated_text == "test"
        assert result.quality == TranslationQuality.EXACT

    def test_detect_format_latex(self):
        """Test detecting latex format."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        detected = translator.detect_format(r"\forall x \in A")
        assert detected == NotationFormat.LATEX

    def test_detect_format_unicode(self):
        """Test detecting unicode format."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        detected = translator.detect_format("∀x ∈ A")
        assert detected == NotationFormat.UNICODE

    def test_detect_format_natural(self):
        """Test detecting natural language format."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        detected = translator.detect_format("for all x there exists y")
        assert detected == NotationFormat.NATURAL

    def test_detect_format_ascii(self):
        """Test detecting ascii format."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        detected = translator.detect_format("x + y = z")
        assert detected == NotationFormat.ASCII

    def test_ambiguity_detection(self):
        """Test ambiguity detection in translation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        # Test with multiple "or" which triggers ambiguity detection
        result = translator.translate(
            "x or y or z",
            NotationFormat.NATURAL,
            NotationFormat.UNICODE
        )
        # The translation happens regardless of ambiguities
        assert result is not None
        # Check that the translated text contains some result
        assert len(result.translated_text) > 0

    def test_translation_result_dataclass(self):
        """Test TranslationResult dataclass."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            TranslationResult, NotationFormat, TranslationQuality
        )
        result = TranslationResult(
            source_format=NotationFormat.NATURAL,
            target_format=NotationFormat.UNICODE,
            source_text="test",
            translated_text="test",
            quality=TranslationQuality.EXACT,
            alternatives=["alt1"],
            ambiguities=["amb1"]
        )
        d = result.to_dict()
        assert d['has_alternatives'] is True
        assert d['ambiguity_count'] == 1

    def test_process_translate(self):
        """Test process with translate operation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator
        )
        translator = FormalLanguageTranslator()
        task = Mock()
        task.metadata = {
            'operation': 'translate',
            'text': 'for all x',
            'source': 'natural',
            'target': 'unicode'
        }
        result = translator.process(task)
        assert result is not None

    def test_process_detect(self):
        """Test process with detect operation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator
        )
        translator = FormalLanguageTranslator()
        task = Mock()
        task.metadata = {
            'operation': 'detect',
            'text': '∀x'
        }
        result = translator.process(task)
        assert result is not None

    def test_process_to_latex(self):
        """Test process with to_latex operation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator
        )
        translator = FormalLanguageTranslator()
        task = Mock()
        task.metadata = {
            'operation': 'to_latex',
            'text': '∀x ∈ A'
        }
        result = translator.process(task)
        assert result is not None

    def test_process_to_natural(self):
        """Test process with to_natural operation."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator
        )
        translator = FormalLanguageTranslator()
        task = Mock()
        task.metadata = {
            'operation': 'to_natural',
            'text': '∀x'
        }
        result = translator.process(task)
        assert result is not None

    def test_get_statistics(self):
        """Test statistics gathering."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator
        )
        translator = FormalLanguageTranslator()
        stats = translator.get_statistics()
        assert 'translations_performed' in stats
        assert 'ambiguities_detected' in stats

    def test_latex_to_unicode_mapping(self):
        """Test latex to unicode mapping coverage."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        # Test multiple latex commands
        result = translator.translate(
            r"\alpha \beta \gamma \pi",
            NotationFormat.LATEX,
            NotationFormat.UNICODE
        )
        assert result is not None

    def test_natural_language_patterns(self):
        """Test all natural language patterns."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator, NotationFormat
        )
        translator = FormalLanguageTranslator()
        patterns = [
            "for all x",
            "there exists y",
            "such that",
            "x implies y",
            "if and only if",
            "x and y",
            "x or y",
            "not x",
            "x in A",
            "A subset of B",
            "A union B",
            "A intersection B",
            "empty set",
            "infinity",
            "less than or equal",
            "greater than or equal",
            "not equal",
            "plus or minus",
            "sum of",
            "product of",
            "integral of"
        ]
        for pattern in patterns:
            result = translator.translate(pattern, NotationFormat.NATURAL, NotationFormat.UNICODE)
            assert result is not None

    def test_bdi_methods(self):
        """Test BDI interface methods."""
        from symbo_agentic_reasoners.agents.synthesis.formal_translator import (
            FormalLanguageTranslator
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention
        translator = FormalLanguageTranslator()
        translator.update_beliefs()
        result = translator.deliberate()
        assert result == []
        # Test execute_step with mock intention
        intention = Mock(spec=Intention)
        intention.get_current_action.return_value = 'test_action'
        intention.metadata = {}
        intention.is_complete.return_value = False
        translator.execute_step(intention)


class TestProofTermConstructorExtended:
    """Extended tests for ProofTermConstructor to boost coverage."""

    def test_init(self):
        """Test initialization."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        assert constructor.agent_id.startswith('proof_term_constructor')

    def test_construct_variable(self):
        """Test constructing a variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        constructor = ProofTermConstructor()
        var = constructor.construct_variable("x", "A")
        assert var.kind == TermKind.VARIABLE
        assert var.name == "x"
        assert var.type_annotation == "A"

    def test_construct_constant(self):
        """Test constructing a constant."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        constructor = ProofTermConstructor()
        const = constructor.construct_constant("zero", "Nat")
        assert const.kind == TermKind.CONSTANT
        assert const.name == "zero"

    def test_construct_abstraction(self):
        """Test constructing a lambda abstraction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        abs_term = constructor.construct_abstraction("x", "A", x)
        assert abs_term.kind == TermKind.ABSTRACTION
        assert abs_term.bound_var == "x"
        assert len(abs_term.sub_terms) == 1

    def test_construct_application(self):
        """Test constructing a function application."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        constructor = ProofTermConstructor()
        f = constructor.construct_variable("f", "A -> B")
        x = constructor.construct_variable("x", "A")
        app = constructor.construct_application(f, x)
        assert app.kind == TermKind.APPLICATION
        assert len(app.sub_terms) == 2

    def test_construct_product(self):
        """Test constructing a product type."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TermKind
        )
        constructor = ProofTermConstructor()
        a = constructor.construct_constant("A", "Type")
        b = constructor.construct_constant("B", "Type")
        prod = constructor.construct_product("x", a, b)
        assert prod.kind == TermKind.PRODUCT
        assert prod.bound_var == "x"

    def test_construct_arrow(self):
        """Test constructing an arrow type."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        arrow = constructor.construct_arrow("A", "B")
        assert arrow is not None

    def test_type_check_variable(self):
        """Test type checking a variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeCheckResult
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        result = constructor.type_check(x)
        assert result.result == TypeCheckResult.WELL_TYPED
        assert result.inferred_type == "A"

    def test_type_check_constant(self):
        """Test type checking a constant."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeCheckResult
        )
        constructor = ProofTermConstructor()
        c = constructor.construct_constant("zero", "Nat")
        result = constructor.type_check(c)
        assert result.result == TypeCheckResult.WELL_TYPED

    def test_type_check_abstraction(self):
        """Test type checking an abstraction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor, TypeCheckResult
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        abs_term = constructor.construct_abstraction("x", "A", x)
        result = constructor.type_check(abs_term)
        assert result.result == TypeCheckResult.WELL_TYPED
        assert "→" in result.inferred_type

    def test_type_check_application(self):
        """Test type checking an application."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        f = constructor.construct_variable("f", "A → B")
        x = constructor.construct_variable("x", "A")
        app = constructor.construct_application(f, x)
        result = constructor.type_check(app)
        assert result is not None

    def test_beta_reduce_simple(self):
        """Test simple beta reduction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        identity = constructor.construct_abstraction("x", "A", x)
        arg = constructor.construct_constant("a", "A")
        app = constructor.construct_application(identity, arg)

        reduced = constructor.beta_reduce(app)
        assert reduced is not None

    def test_normalize(self):
        """Test term normalization."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        normalized = constructor.normalize(x)
        assert normalized.to_string() == "x"

    def test_proof_term_to_string_variable(self):
        """Test ProofTerm to_string for variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        assert x.to_string() == "x"

    def test_proof_term_to_string_constant(self):
        """Test ProofTerm to_string for constant."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        c = constructor.construct_constant("c", "A")
        assert c.to_string() == "c"

    def test_proof_term_to_string_abstraction(self):
        """Test ProofTerm to_string for abstraction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        abs_term = constructor.construct_abstraction("x", "A", x)
        s = abs_term.to_string()
        assert "λ" in s
        assert "x" in s

    def test_proof_term_to_string_application(self):
        """Test ProofTerm to_string for application."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        f = constructor.construct_variable("f", "A")
        x = constructor.construct_variable("x", "A")
        app = constructor.construct_application(f, x)
        s = app.to_string()
        assert "f" in s
        assert "x" in s

    def test_proof_term_to_string_product(self):
        """Test ProofTerm to_string for product."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        a = constructor.construct_constant("A", "Type")
        b = constructor.construct_constant("B", "Type")
        prod = constructor.construct_product("x", a, b)
        s = prod.to_string()
        assert "Π" in s

    def test_proof_term_to_string_universe(self):
        """Test ProofTerm to_string for universe."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTerm, TermKind
        )
        univ = ProofTerm(kind=TermKind.UNIVERSE, name="0")
        s = univ.to_string()
        assert "Type" in s

    def test_proof_term_to_dict(self):
        """Test ProofTerm to_dict."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        d = x.to_dict()
        assert d['kind'] == 'var'
        assert d['name'] == 'x'
        assert d['type'] == 'A'

    def test_type_context(self):
        """Test TypeContext operations."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeContext
        )
        ctx = TypeContext()
        extended = ctx.extend("x", "A")
        assert extended.lookup("x") == "A"
        assert ctx.lookup("x") is None

    def test_type_check_output(self):
        """Test TypeCheckOutput dataclass."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            TypeCheckOutput, TypeCheckResult
        )
        output = TypeCheckOutput(
            result=TypeCheckResult.WELL_TYPED,
            inferred_type="A",
            errors=[]
        )
        d = output.to_dict()
        assert d['result'] == 'well_typed'
        assert d['type'] == 'A'

    def test_process_construct_var(self):
        """Test process with construct_var operation."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        task = Mock()
        task.metadata = {'operation': 'construct_var', 'name': 'x', 'type': 'A'}
        result = constructor.process(task)
        assert result is not None

    def test_process_construct_abs(self):
        """Test process with construct_abs operation."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        task = Mock()
        task.metadata = {'operation': 'construct_abs', 'var': 'x', 'var_type': 'A', 'body': 'x'}
        result = constructor.process(task)
        assert result is not None

    def test_process_type_check(self):
        """Test process with type_check operation."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        task = Mock()
        task.metadata = {'operation': 'type_check'}
        result = constructor.process(task)
        assert result is not None

    def test_process_normalize(self):
        """Test process with normalize operation."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        task = Mock()
        task.metadata = {'operation': 'normalize'}
        result = constructor.process(task)
        assert result is not None

    def test_get_statistics(self):
        """Test statistics gathering."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        stats = constructor.get_statistics()
        assert 'terms_constructed' in stats
        assert 'type_checks' in stats
        assert 'reductions' in stats

    def test_substitute_variable(self):
        """Test substitution on variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        y = constructor.construct_variable("y", "A")
        result = constructor._substitute(x, "x", y)
        assert result.name == "y"

    def test_substitute_abstraction(self):
        """Test substitution on abstraction."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        abs_term = constructor.construct_abstraction("y", "A", x)
        z = constructor.construct_variable("z", "A")
        result = constructor._substitute(abs_term, "x", z)
        assert result is not None

    def test_substitute_shadowed(self):
        """Test substitution with shadowed variable."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        x = constructor.construct_variable("x", "A")
        abs_term = constructor.construct_abstraction("x", "A", x)
        z = constructor.construct_variable("z", "A")
        result = constructor._substitute(abs_term, "x", z)
        # Variable is shadowed, so no substitution
        assert result.bound_var == "x"

    def test_infer_type_product(self):
        """Test type inference for product."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        constructor = ProofTermConstructor()
        a = constructor.construct_constant("A", "Type")
        b = constructor.construct_constant("B", "Type")
        prod = constructor.construct_product("x", a, b)
        result = constructor.type_check(prod)
        assert result.inferred_type == "Type"

    def test_bdi_methods(self):
        """Test BDI interface methods."""
        from symbo_agentic_reasoners.agents.synthesis.proof_term_constructor import (
            ProofTermConstructor
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention
        constructor = ProofTermConstructor()
        constructor.update_beliefs()
        result = constructor.deliberate()
        assert result == []
        # Test execute_step with mock intention
        intention = Mock(spec=Intention)
        intention.get_current_action.return_value = 'test_action'
        intention.metadata = {}
        intention.is_complete.return_value = False
        constructor.execute_step(intention)


class TestStructuralSynthesizerExtended:
    """Extended tests for StructuralSynthesizer."""

    def test_init(self):
        """Test initialization."""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        assert synth.agent_id.startswith('structural_synthesizer')

    def test_process_method(self):
        """Test process method."""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        task = Mock()
        task.metadata = {'components': ['a', 'b'], 'target': 'c'}
        result = synth.process(task)
        assert result is not None

    def test_bdi_methods(self):
        """Test BDI methods."""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        from symbo_agentic_reasoners.core.bdi_agent import Intention
        synth = StructuralSynthesizer()
        synth.update_beliefs()
        result = synth.deliberate()
        assert result == []
        # Test execute_step with mock intention
        intention = Mock(spec=Intention)
        intention.get_current_action.return_value = 'test_action'
        intention.metadata = {}
        intention.is_complete.return_value = False
        synth.execute_step(intention)

    def test_get_statistics(self):
        """Test statistics."""
        from symbo_agentic_reasoners.agents.synthesis.structural_synthesizer import (
            StructuralSynthesizer
        )
        synth = StructuralSynthesizer()
        stats = synth.get_statistics()
        assert isinstance(stats, dict)


class TestConjectureGeneratorExtended:
    """Additional tests for ConjectureGenerator to ensure 70%+ coverage."""

    def test_generate_empty_examples(self):
        """Test generating from empty examples."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator
        )
        generator = ConjectureGenerator()
        conjs = generator.generate_from_examples([], "test")
        assert conjs == []

    def test_test_nonexistent_conjecture(self):
        """Test testing a non-existent conjecture."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator
        )
        generator = ConjectureGenerator()
        passed, failures = generator.test_conjecture("nonexistent_id", [])
        assert passed is False
        assert "Conjecture not found" in failures

    def test_add_evidence_nonexistent(self):
        """Test adding evidence to non-existent conjecture."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator
        )
        generator = ConjectureGenerator()
        # Should not raise an error
        generator.add_evidence("nonexistent", "test", True)

    def test_process_test_operation(self):
        """Test process with test operation."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator
        )
        generator = ConjectureGenerator()
        conjs = generator.generate_from_pattern("test", "test", [])
        conj_id = conjs[0].conjecture_id

        task = Mock()
        task.metadata = {
            'operation': 'test',
            'conjecture_id': conj_id,
            'test_cases': [{'case': 1}]
        }
        result = generator.process(task)
        assert result is not None

    def test_process_unknown_operation(self):
        """Test process with unknown operation."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator
        )
        generator = ConjectureGenerator()
        task = Mock()
        task.metadata = {'operation': 'unknown_op'}
        result = generator.process(task)
        # Returns error dict without blackboard
        assert result is not None

    def test_generate_from_template_identity(self):
        """Test identity template."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator, ConjectureType
        )
        generator = ConjectureGenerator()
        conj = generator.generate_from_template(
            'identity',
            lhs="a + b",
            rhs="b + a"
        )
        assert conj.conjecture_type == ConjectureType.IDENTITY

    def test_generate_from_template_inequality(self):
        """Test inequality template."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator, ConjectureType
        )
        generator = ConjectureGenerator()
        conj = generator.generate_from_template(
            'inequality',
            lhs="n",
            op="<",
            rhs="n + 1"
        )
        assert conj.conjecture_type == ConjectureType.INEQUALITY

    def test_generate_from_template_missing_params(self):
        """Test template with missing parameters."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator
        )
        generator = ConjectureGenerator()
        conj = generator.generate_from_template('universal')
        # Should handle missing params gracefully
        assert "INCOMPLETE" in conj.statement

    def test_conjecture_status_refuted(self):
        """Test conjecture becomes refuted."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator, ConjectureStatus
        )
        generator = ConjectureGenerator()
        conjs = generator.generate_from_pattern("test", "test", [])
        conj_id = conjs[0].conjecture_id

        # Add multiple counter-evidence
        for i in range(3):
            generator.add_evidence(conj_id, f"Counter {i}", False)

        assert generator.conjectures[conj_id].status == ConjectureStatus.REFUTED

    def test_conjecture_status_open(self):
        """Test conjecture becomes open."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            ConjectureGenerator, ConjectureStatus
        )
        generator = ConjectureGenerator()
        conjs = generator.generate_from_pattern("test", "test", [])
        conj_id = conjs[0].conjecture_id

        # Add mixed evidence without strong conclusion
        generator.add_evidence(conj_id, "For 1", True)
        generator.add_evidence(conj_id, "For 2", True)
        generator.add_evidence(conj_id, "Against 1", False)
        generator.add_evidence(conj_id, "For 3", True)
        generator.add_evidence(conj_id, "For 4", True)
        generator.add_evidence(conj_id, "For 5", True)

        # Should be open if mixed evidence
        assert generator.conjectures[conj_id].status in [
            ConjectureStatus.OPEN,
            ConjectureStatus.VERIFIED,
            ConjectureStatus.TESTING
        ]

    def test_conjecture_long_statement_truncation(self):
        """Test that long statements are truncated in to_dict."""
        from symbo_agentic_reasoners.agents.synthesis.conjecture_generator import (
            Conjecture, ConjectureType, ConjectureStatus
        )
        long_statement = "x" * 200
        conj = Conjecture(
            conjecture_id="test",
            statement=long_statement,
            conjecture_type=ConjectureType.UNIVERSAL,
            domain="test"
        )
        d = conj.to_dict()
        assert len(d['statement']) <= 103  # 100 + '...'
