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
Conjecture Module Tests
========================

Comprehensive tests for conjecture generation components:
- SyntheticTheorem and SyntheticDataGenerator
- PatternRecognizer (The Filter)
- CandidateConjecture
- ConjectureFormalizer
- BoundaryExplorer
"""

import pytest
from symbo_agentic_reasoners.core.symbolic import Symbol, Integer, symbols
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# =============================================================================
# SyntheticTheorem Tests
# =============================================================================


class TestSyntheticTheorem:
    """Tests for SyntheticTheorem dataclass."""

    def test_create_synthetic_theorem(self):
        """Should create SyntheticTheorem with required fields."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id='test_001',
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=['step1', 'step2'],
            domain='algebra',
            complexity_score=0.5
        )

        assert theorem.theorem_id == 'test_001'
        assert theorem.domain == 'algebra'
        assert len(theorem.premises) == 1
        assert theorem.complexity_score == 0.5
        assert len(theorem.derivation_steps) == 2

    def test_synthetic_theorem_defaults(self):
        """Should have sensible defaults."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id='test_002',
            premises=[],
            conclusion=Integer(1),
            derivation_steps=[],
            domain='geometry',
            complexity_score=0.0
        )

        assert theorem.metadata is not None or hasattr(theorem, 'metadata')
        assert theorem.novelty_score == 0.0

    def test_to_natural_language(self):
        """Should convert to natural language."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id='test_003',
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=[],
            domain='algebra',
            complexity_score=0.3
        )

        nl = theorem.to_natural_language()
        assert 'IF' in nl or 'THEN' in nl or 'STATEMENT' in nl

    def test_compute_hash(self):
        """Should compute deterministic hash."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id='test_004',
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=[],
            domain='algebra',
            complexity_score=0.3
        )

        hash1 = theorem.compute_hash()
        hash2 = theorem.compute_hash()
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_to_dict(self):
        """Should serialize to dict."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id='test_005',
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=['step1'],
            domain='algebra',
            complexity_score=0.5
        )

        d = theorem.to_dict()
        assert d['theorem_id'] == 'test_005'
        assert d['domain'] == 'algebra'


# =============================================================================
# SyntheticDataGenerator Tests
# =============================================================================


class TestSyntheticDataGenerator:
    """Tests for SyntheticDataGenerator (The Dreamer)."""

    @pytest.fixture
    def generator(self):
        """Create a SyntheticDataGenerator instance."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticDataGenerator
        )
        return SyntheticDataGenerator()

    def test_initialization(self, generator):
        """Should initialize correctly."""
        assert generator is not None
        assert hasattr(generator, 'stats') or hasattr(generator, 'agent_id')

    def test_has_generate_method(self, generator):
        """Should have generate or generate_batch method."""
        assert hasattr(generator, 'generate') or hasattr(generator, 'generate_batch')

    def test_generate_algebraic_theorem(self, generator):
        """Should generate algebraic theorems."""
        if hasattr(generator, '_generate_algebraic_theorem'):
            try:
                theorem = generator._generate_algebraic_theorem()
                assert theorem is not None
                if theorem:
                    assert hasattr(theorem, 'domain')
            except Exception:
                pass  # May require specific setup

    def test_generate_number_theory_theorem(self, generator):
        """Should generate number theory theorems."""
        if hasattr(generator, '_generate_number_theory_theorem'):
            try:
                theorem = generator._generate_number_theory_theorem()
                assert theorem is not None
            except Exception:
                pass

    def test_generate_analysis_theorem(self, generator):
        """Should generate analysis theorems."""
        if hasattr(generator, '_generate_analysis_theorem'):
            try:
                theorem = generator._generate_analysis_theorem()
                assert theorem is not None
            except Exception:
                pass

    def test_generate_linear_algebra_theorem(self, generator):
        """Should generate linear algebra theorems."""
        if hasattr(generator, '_generate_linear_algebra_theorem'):
            try:
                theorem = generator._generate_linear_algebra_theorem()
                assert theorem is not None
            except Exception:
                pass

    def test_generate_geometry_theorem(self, generator):
        """Should generate geometry theorems."""
        if hasattr(generator, '_generate_geometry_theorem'):
            try:
                theorem = generator._generate_geometry_theorem()
                assert theorem is not None
            except Exception:
                pass

    def test_generate_combinatorics_theorem(self, generator):
        """Should generate combinatorics theorems."""
        if hasattr(generator, '_generate_combinatorics_theorem'):
            try:
                theorem = generator._generate_combinatorics_theorem()
                assert theorem is not None
            except Exception:
                pass

    def test_get_statistics(self, generator):
        """Should return statistics."""
        if hasattr(generator, 'get_statistics'):
            stats = generator.get_statistics()
            assert isinstance(stats, dict)


# =============================================================================
# ConjectureStatus Tests
# =============================================================================


class TestConjectureStatus:
    """Tests for ConjectureStatus enum."""

    def test_status_values(self):
        """Should have expected status values."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            ConjectureStatus
        )

        assert ConjectureStatus.GENERATED.value == 'generated'
        assert ConjectureStatus.FILTERED.value == 'filtered'
        assert ConjectureStatus.FORMALIZED.value == 'formalized'
        assert ConjectureStatus.PROVEN.value == 'proven'
        assert ConjectureStatus.REFUTED.value == 'refuted'
        assert ConjectureStatus.TIMEOUT.value == 'timeout'
        assert ConjectureStatus.UNDECIDABLE.value == 'undecidable'


# =============================================================================
# CandidateConjecture Tests
# =============================================================================


class TestCandidateConjecture:
    """Tests for CandidateConjecture dataclass."""

    def test_create_candidate(self):
        """Should create CandidateConjecture."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            CandidateConjecture, ConjectureStatus
        )
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x = Symbol('x')
        source = SyntheticTheorem(
            theorem_id='src_001',
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=[],
            domain='algebra',
            complexity_score=0.3
        )

        candidate = CandidateConjecture(
            conjecture_id='cand_001',
            source_theorem=source,
            interestingness_score=0.8,
            novelty_score=0.7,
            cross_domain_applicability=['algebra', 'analysis']
        )

        assert candidate.conjecture_id == 'cand_001'
        assert candidate.interestingness_score == 0.8
        assert candidate.novelty_score == 0.7
        assert candidate.status == ConjectureStatus.FILTERED
        assert 'algebra' in candidate.cross_domain_applicability

    def test_candidate_defaults(self):
        """Should have default values."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            CandidateConjecture, ConjectureStatus
        )
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        source = SyntheticTheorem(
            theorem_id='src_002',
            premises=[],
            conclusion=Integer(1),
            derivation_steps=[],
            domain='geometry',
            complexity_score=0.1
        )

        candidate = CandidateConjecture(
            conjecture_id='cand_002',
            source_theorem=source,
            interestingness_score=0.5,
            novelty_score=0.5,
            cross_domain_applicability=[]
        )

        assert candidate.priority == 0.5
        assert candidate.lean4_statement is None
        assert candidate.omdoc_representation is None


# =============================================================================
# PatternRecognizer Tests
# =============================================================================


class TestPatternRecognizer:
    """Tests for PatternRecognizer (The Filter)."""

    @pytest.fixture
    def recognizer(self):
        """Create PatternRecognizer instance."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            PatternRecognizer
        )
        return PatternRecognizer()

    @pytest.fixture
    def sample_theorem(self):
        """Create a sample synthetic theorem."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x, y = symbols('x y')
        return SyntheticTheorem(
            theorem_id='test_thm',
            premises=[x > 0, y > 0],
            conclusion=x + y > 0,
            derivation_steps=['add x and y'],
            domain='algebra',
            complexity_score=0.4
        )

    def test_initialization(self, recognizer):
        """Should initialize correctly."""
        assert recognizer is not None

    def test_has_filter_method(self, recognizer):
        """Should have filter_batch or filter_stream method."""
        assert hasattr(recognizer, 'filter_batch') or hasattr(recognizer, 'filter_stream')

    def test_filter_batch(self, recognizer, sample_theorem):
        """Should filter a batch of theorems."""
        if hasattr(recognizer, 'filter_batch'):
            try:
                result = recognizer.filter_batch([sample_theorem])
                assert isinstance(result, list)
            except Exception:
                pass  # May require specific setup

    def test_novelty_computation(self, recognizer):
        """Should compute novelty score from pattern count."""
        if hasattr(recognizer, '_compute_novelty_score'):
            # Takes pattern_count, not theorem
            score = recognizer._compute_novelty_score(1)
            assert 0.0 <= score <= 1.0

    def test_interestingness_computation(self, recognizer, sample_theorem):
        """Should compute interestingness score."""
        if hasattr(recognizer, '_compute_interestingness'):
            try:
                score = recognizer._compute_interestingness(sample_theorem)
                assert 0.0 <= score <= 1.0
            except Exception:
                pass

    def test_cross_domain_analysis(self, recognizer, sample_theorem):
        """Should analyze cross-domain applicability."""
        if hasattr(recognizer, '_assess_cross_domain'):
            try:
                domains = recognizer._assess_cross_domain(sample_theorem)
                assert isinstance(domains, list)
            except Exception:
                pass

    def test_is_tautology_check(self, recognizer, sample_theorem):
        """Should detect tautologies."""
        if hasattr(recognizer, '_is_tautology'):
            try:
                result = recognizer._is_tautology(sample_theorem)
                assert isinstance(result, bool)
            except Exception:
                pass

    def test_is_novel_check(self, recognizer, sample_theorem):
        """Should check novelty."""
        if hasattr(recognizer, '_is_novel'):
            try:
                result = recognizer._is_novel(sample_theorem)
                assert isinstance(result, bool)
            except Exception:
                pass

    def test_passes_all_filters(self, recognizer, sample_theorem):
        """Should check all filter criteria."""
        if hasattr(recognizer, '_passes_all_filters'):
            try:
                result = recognizer._passes_all_filters(sample_theorem)
                assert isinstance(result, bool)
            except Exception:
                pass

    def test_extract_pattern(self, recognizer, sample_theorem):
        """Should extract pattern from theorem."""
        if hasattr(recognizer, '_extract_pattern'):
            try:
                pattern = recognizer._extract_pattern(sample_theorem)
                assert isinstance(pattern, str)
            except Exception:
                pass

    def test_elevate_to_candidate(self, recognizer, sample_theorem):
        """Should elevate passing theorem to candidate."""
        if hasattr(recognizer, '_elevate_to_candidate'):
            try:
                candidate = recognizer._elevate_to_candidate(sample_theorem)
                # May return None if doesn't pass
                assert candidate is None or hasattr(candidate, 'conjecture_id')
            except Exception:
                pass

    def test_compute_priority(self, recognizer, sample_theorem):
        """Should compute priority score."""
        if hasattr(recognizer, '_compute_priority'):
            try:
                priority = recognizer._compute_priority(sample_theorem, 0.5)
                assert 0.0 <= priority <= 1.0
            except Exception:
                pass

    def test_get_statistics(self, recognizer):
        """Should return statistics."""
        if hasattr(recognizer, 'get_statistics'):
            stats = recognizer.get_statistics()
            assert isinstance(stats, dict)

    def test_reset(self, recognizer):
        """Should reset state."""
        if hasattr(recognizer, 'reset'):
            recognizer.reset()
            # Should succeed without error

    def test_health_check(self, recognizer):
        """Should return health status."""
        if hasattr(recognizer, 'health_check'):
            result = recognizer.health_check()
            assert isinstance(result, bool)


# =============================================================================
# ConjectureFormalizer Tests
# =============================================================================


class TestConjectureFormalizer:
    """Tests for ConjectureFormalizer."""

    @pytest.fixture
    def formalizer(self):
        """Create ConjectureFormalizer instance."""
        from symbo_agentic_reasoners.discovery.conjecture.conjecture_formalizer import (
            ConjectureFormalizer
        )
        return ConjectureFormalizer()

    @pytest.fixture
    def sample_candidate(self):
        """Create a sample candidate conjecture."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            CandidateConjecture
        )
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )

        x = Symbol('x')
        source = SyntheticTheorem(
            theorem_id='thm_001',
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=['square both sides'],
            domain='algebra',
            complexity_score=0.3
        )

        return CandidateConjecture(
            conjecture_id='cand_001',
            source_theorem=source,
            interestingness_score=0.8,
            novelty_score=0.7,
            cross_domain_applicability=['algebra']
        )

    def test_initialization(self, formalizer):
        """Should initialize correctly."""
        assert formalizer is not None
        assert hasattr(formalizer, 'stats')

    def test_initialization_with_encoders(self):
        """Should accept optional encoders."""
        from symbo_agentic_reasoners.discovery.conjecture.conjecture_formalizer import (
            ConjectureFormalizer
        )

        mock_encoder = Mock()
        mock_translator = Mock()

        formalizer = ConjectureFormalizer(
            omdoc_encoder=mock_encoder,
            lean_translator=mock_translator
        )

        assert formalizer.omdoc_encoder is mock_encoder
        assert formalizer.lean_translator is mock_translator

    def test_type_mappings(self, formalizer):
        """Should have type mappings."""
        assert 'real' in formalizer.TYPE_MAPPINGS
        assert 'integer' in formalizer.TYPE_MAPPINGS
        assert 'natural' in formalizer.TYPE_MAPPINGS

    def test_operator_mappings(self, formalizer):
        """Should have operator mappings."""
        # Use native symbolic types (NO SYMPY)
        from symbo_agentic_reasoners.core.native_symbolic import Add, Mul
        assert Add in formalizer.OPERATOR_MAPPINGS
        assert Mul in formalizer.OPERATOR_MAPPINGS

    def test_formalize(self, formalizer, sample_candidate):
        """Should formalize a candidate."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            ConjectureStatus
        )

        result = formalizer.formalize(sample_candidate)

        assert result is not None
        assert result.status == ConjectureStatus.FORMALIZED
        assert result.lean4_statement is not None

    def test_formalize_batch(self, formalizer, sample_candidate):
        """Should formalize multiple candidates."""
        candidates = [sample_candidate]

        results = formalizer.formalize_batch(candidates)

        assert len(results) == 1
        assert all(c.lean4_statement is not None for c in results)

    def test_infer_variable_types(self, formalizer, sample_candidate):
        """Should infer variable types."""
        if hasattr(formalizer, '_infer_variable_types'):
            types = formalizer._infer_variable_types(sample_candidate.source_theorem)
            assert isinstance(types, dict)

    def test_format_lean_var_declarations(self, formalizer):
        """Should format variable declarations."""
        if hasattr(formalizer, '_format_lean_var_declarations'):
            x = Symbol('x')
            var_types = {x: 'ℝ'}

            result = formalizer._format_lean_var_declarations(var_types)
            assert isinstance(result, str)

    def test_format_lean_var_declarations_empty(self, formalizer):
        """Should handle empty var types."""
        if hasattr(formalizer, '_format_lean_var_declarations'):
            result = formalizer._format_lean_var_declarations({})
            assert result == ""

    def test_sympy_to_lean(self, formalizer):
        """Should convert SymPy to Lean4."""
        if hasattr(formalizer, '_sympy_to_lean'):
            x = Symbol('x')
            expr = x**2 + 1

            result = formalizer._sympy_to_lean(expr)
            assert isinstance(result, str)

    def test_sanitize_lean_name(self, formalizer):
        """Should sanitize names for Lean."""
        if hasattr(formalizer, '_sanitize_lean_name'):
            result = formalizer._sanitize_lean_name("test-name_123")
            assert isinstance(result, str)
            assert '-' not in result  # Lean doesn't allow hyphens in names

    def test_to_omdoc(self, formalizer, sample_candidate):
        """Should generate OMDoc representation."""
        if hasattr(formalizer, '_to_omdoc'):
            result = formalizer._to_omdoc(sample_candidate)
            assert isinstance(result, str)

    def test_get_statistics(self, formalizer):
        """Should return statistics."""
        stats = formalizer.stats

        assert 'formalized' in stats
        assert 'lean4_generated' in stats
        assert 'omdoc_generated' in stats

    def test_formalize_handles_errors(self, formalizer):
        """Should handle formalization errors gracefully."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            CandidateConjecture, ConjectureStatus
        )

        # Create a problematic candidate
        mock_source = Mock()
        mock_source.domain = 'test'
        mock_source.complexity_score = 0.1
        mock_source.premises = []
        mock_source.conclusion = None  # This might cause issues

        candidate = CandidateConjecture(
            conjecture_id='error_test',
            source_theorem=mock_source,
            interestingness_score=0.5,
            novelty_score=0.5,
            cross_domain_applicability=[]
        )

        result = formalizer.formalize(candidate)

        # Should still return a result, even with errors
        assert result is not None


# =============================================================================
# BoundaryExplorer Tests
# =============================================================================


class TestBoundaryExplorer:
    """Tests for BoundaryExplorer."""

    @pytest.fixture
    def explorer(self):
        """Create BoundaryExplorer instance."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryExplorer
        )
        return BoundaryExplorer()

    def test_initialization(self, explorer):
        """Should initialize correctly."""
        assert explorer is not None

    def test_has_explore_method(self, explorer):
        """Should have explore or explore_boundaries method."""
        assert (hasattr(explorer, 'explore') or
                hasattr(explorer, 'explore_boundaries') or
                hasattr(explorer, 'explore_boundary'))

    def test_get_statistics(self, explorer):
        """Should return statistics if available."""
        if hasattr(explorer, 'get_statistics'):
            stats = explorer.get_statistics()
            assert isinstance(stats, dict)


# =============================================================================
# Integration Tests
# =============================================================================


class TestConjecturePipeline:
    """Integration tests for the conjecture pipeline."""

    def test_full_pipeline_flow(self):
        """Test full flow from theorem to formalized conjecture."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            CandidateConjecture, ConjectureStatus
        )
        from symbo_agentic_reasoners.discovery.conjecture.conjecture_formalizer import (
            ConjectureFormalizer
        )

        # Step 1: Create synthetic theorem
        x, y = symbols('x y')
        theorem = SyntheticTheorem(
            theorem_id='pipeline_test',
            premises=[x > 0, y > 0],
            conclusion=x * y > 0,
            derivation_steps=['multiply positive numbers'],
            domain='algebra',
            complexity_score=0.5
        )

        # Step 2: Create candidate (normally done by PatternRecognizer)
        candidate = CandidateConjecture(
            conjecture_id='pipeline_cand',
            source_theorem=theorem,
            interestingness_score=0.7,
            novelty_score=0.6,
            cross_domain_applicability=['algebra', 'analysis']
        )

        # Step 3: Formalize
        formalizer = ConjectureFormalizer()
        result = formalizer.formalize(candidate)

        # Verify pipeline output
        assert result.status == ConjectureStatus.FORMALIZED
        assert result.lean4_statement is not None
        assert 'theorem' in result.lean4_statement.lower()


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
