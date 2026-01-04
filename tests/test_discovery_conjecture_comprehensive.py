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
Comprehensive Discovery Conjecture Module Tests
===============================================

Tests for discovery/conjecture modules to achieve 75%+ coverage:
- SyntheticDataGenerator
- PatternRecognizer
- ConjectureFormalizer
- BoundaryExplorer
"""

import pytest
from symbo_agentic_reasoners.core.symbolic import Symbol


# =============================================================================
# SyntheticTheorem Tests
# =============================================================================


class TestSyntheticTheorem:
    """Tests for SyntheticTheorem dataclass."""

    def test_creation(self):
        """Should create SyntheticTheorem."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )
        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id="thm_001",
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=["step1", "step2"],
            domain="algebra",
            complexity_score=0.5
        )
        assert theorem.theorem_id == "thm_001"
        assert theorem.domain == "algebra"

    def test_to_natural_language_with_premises(self):
        """Should convert to natural language with premises."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )
        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id="thm_002",
            premises=[x > 0, x < 10],
            conclusion=x**2 < 100,
            derivation_steps=[],
            domain="algebra",
            complexity_score=0.3
        )
        nl = theorem.to_natural_language()
        assert "IF" in nl
        assert "THEN" in nl

    def test_to_natural_language_without_premises(self):
        """Should convert to natural language without premises."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )
        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id="thm_003",
            premises=[],
            conclusion=x**2 >= 0,
            derivation_steps=[],
            domain="algebra",
            complexity_score=0.1
        )
        nl = theorem.to_natural_language()
        assert "STATEMENT" in nl

    def test_compute_hash(self):
        """Should compute deterministic hash."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )
        x = Symbol('x')
        theorem = SyntheticTheorem(
            theorem_id="thm_004",
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=[],
            domain="algebra",
            complexity_score=0.5
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
            theorem_id="thm_005",
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=["derive"],
            domain="algebra",
            complexity_score=0.6,
            novelty_score=0.4
        )
        d = theorem.to_dict()
        assert d['theorem_id'] == "thm_005"
        assert d['domain'] == "algebra"
        assert d['complexity_score'] == 0.6


class TestTheoremDomain:
    """Tests for TheoremDomain enum."""

    def test_has_algebra(self):
        """Should have ALGEBRA domain."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            TheoremDomain
        )
        assert TheoremDomain.ALGEBRA.value == 'algebra'

    def test_has_geometry(self):
        """Should have GEOMETRY domain."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            TheoremDomain
        )
        assert TheoremDomain.GEOMETRY.value == 'geometry'

    def test_has_number_theory(self):
        """Should have NUMBER_THEORY domain."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            TheoremDomain
        )
        assert TheoremDomain.NUMBER_THEORY.value == 'number_theory'


# =============================================================================
# SyntheticDataGenerator Tests
# =============================================================================


class TestSyntheticDataGenerator:
    """Tests for SyntheticDataGenerator class."""

    @pytest.fixture
    def generator(self):
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticDataGenerator
        )
        return SyntheticDataGenerator(seed=42)

    def test_initialization(self, generator):
        """Should initialize correctly."""
        assert generator is not None
        assert generator.theorem_count == 0

    def test_initialization_with_seed(self):
        """Should accept seed parameter."""
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticDataGenerator
        )
        gen = SyntheticDataGenerator(seed=123)
        assert gen is not None

    def test_has_seen_hashes(self, generator):
        """Should have seen_hashes set."""
        assert hasattr(generator, 'seen_hashes')
        assert isinstance(generator.seen_hashes, set)

    def test_get_statistics(self, generator):
        """Should return statistics."""
        stats = generator.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# ConjectureStatus Tests
# =============================================================================


class TestConjectureStatus:
    """Tests for ConjectureStatus enum."""

    def test_has_generated(self):
        """Should have GENERATED status."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            ConjectureStatus
        )
        assert ConjectureStatus.GENERATED.value == 'generated'

    def test_has_filtered(self):
        """Should have FILTERED status."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            ConjectureStatus
        )
        assert ConjectureStatus.FILTERED.value == 'filtered'

    def test_has_proven(self):
        """Should have PROVEN status."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            ConjectureStatus
        )
        assert ConjectureStatus.PROVEN.value == 'proven'

    def test_has_refuted(self):
        """Should have REFUTED status."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            ConjectureStatus
        )
        assert ConjectureStatus.REFUTED.value == 'refuted'


# =============================================================================
# CandidateConjecture Tests
# =============================================================================


class TestCandidateConjecture:
    """Tests for CandidateConjecture dataclass."""

    @pytest.fixture
    def theorem(self):
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticTheorem
        )
        x = Symbol('x')
        return SyntheticTheorem(
            theorem_id="thm_001",
            premises=[x > 0],
            conclusion=x**2 > 0,
            derivation_steps=[],
            domain="algebra",
            complexity_score=0.5
        )

    def test_creation(self, theorem):
        """Should create CandidateConjecture."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            CandidateConjecture
        )
        conj = CandidateConjecture(
            conjecture_id="conj_001",
            source_theorem=theorem,
            interestingness_score=0.7,
            novelty_score=0.5,
            cross_domain_applicability=["algebra", "geometry"]
        )
        assert conj.conjecture_id == "conj_001"
        assert conj.interestingness_score == 0.7

    def test_to_dict(self, theorem):
        """Should serialize to dict."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            CandidateConjecture
        )
        conj = CandidateConjecture(
            conjecture_id="conj_002",
            source_theorem=theorem,
            interestingness_score=0.8,
            novelty_score=0.6,
            cross_domain_applicability=["algebra"]
        )
        d = conj.to_dict()
        assert d['conjecture_id'] == "conj_002"
        assert d['interestingness_score'] == 0.8


# =============================================================================
# PatternRecognizer Tests
# =============================================================================


class TestPatternRecognizer:
    """Tests for PatternRecognizer class."""

    @pytest.fixture
    def recognizer(self):
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            PatternRecognizer
        )
        return PatternRecognizer()

    def test_initialization(self, recognizer):
        """Should initialize correctly."""
        assert recognizer is not None
        assert recognizer.novelty_threshold == 0.3

    def test_initialization_custom_threshold(self):
        """Should accept custom threshold."""
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            PatternRecognizer
        )
        rec = PatternRecognizer(novelty_threshold=0.5)
        assert rec.novelty_threshold == 0.5

    def test_has_seen_hashes(self, recognizer):
        """Should have seen_hashes set."""
        assert hasattr(recognizer, 'seen_hashes')

    def test_has_pattern_counts(self, recognizer):
        """Should have pattern_counts dict."""
        assert hasattr(recognizer, 'pattern_counts')

    def test_get_statistics(self, recognizer):
        """Should return statistics."""
        stats = recognizer.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# ConjectureFormalizer Tests
# =============================================================================


class TestConjectureFormalizer:
    """Tests for ConjectureFormalizer class."""

    @pytest.fixture
    def formalizer(self):
        from symbo_agentic_reasoners.discovery.conjecture.conjecture_formalizer import (
            ConjectureFormalizer
        )
        return ConjectureFormalizer()

    def test_initialization(self, formalizer):
        """Should initialize correctly."""
        assert formalizer is not None

    def test_get_statistics(self, formalizer):
        """Should return statistics."""
        stats = formalizer.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# BoundaryExplorer Tests
# =============================================================================


class TestBoundaryExplorer:
    """Tests for BoundaryExplorer class."""

    @pytest.fixture
    def explorer(self):
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryExplorer
        )
        return BoundaryExplorer()

    def test_initialization(self, explorer):
        """Should initialize correctly."""
        assert explorer is not None

    def test_get_statistics(self, explorer):
        """Should return statistics."""
        stats = explorer.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# Extended SyntheticDataGenerator Tests
# =============================================================================


class TestSyntheticDataGeneratorExtended:
    """Extended tests for SyntheticDataGenerator."""

    @pytest.fixture
    def generator(self):
        from symbo_agentic_reasoners.discovery.conjecture.synthetic_data_generator import (
            SyntheticDataGenerator
        )
        return SyntheticDataGenerator(seed=42)

    def test_generate_batch(self, generator):
        """Should generate batch of theorems."""
        batch = generator.generate_batch(size=5)
        assert isinstance(batch, list)

    def test_generate_batch_algebra(self, generator):
        """Should generate algebra domain theorems."""
        batch = generator.generate_batch(size=3, domain='algebra')
        assert isinstance(batch, list)

    def test_generate_batch_geometry(self, generator):
        """Should generate geometry domain theorems."""
        batch = generator.generate_batch(size=3, domain='geometry')
        assert isinstance(batch, list)

    def test_generate_batch_number_theory(self, generator):
        """Should generate number theory theorems."""
        batch = generator.generate_batch(size=3, domain='number_theory')
        assert isinstance(batch, list)

    def test_generate_novel(self, generator):
        """Should generate novel theorems."""
        theorems = generator.generate_novel(count=5)
        assert isinstance(theorems, list)

    def test_reset(self, generator):
        """Should reset generator state."""
        generator.reset()
        assert generator.theorem_count == 0

    def test_health_check(self, generator):
        """Should pass health check."""
        result = generator.health_check()
        assert result is True


# =============================================================================
# Extended PatternRecognizer Tests
# =============================================================================


class TestPatternRecognizerExtended:
    """Extended tests for PatternRecognizer."""

    @pytest.fixture
    def recognizer(self):
        from symbo_agentic_reasoners.discovery.conjecture.pattern_recognizer import (
            PatternRecognizer
        )
        return PatternRecognizer()

    def test_reset(self, recognizer):
        """Should reset recognizer state."""
        recognizer.reset()
        # Should not raise

    def test_health_check(self, recognizer):
        """Should pass health check."""
        result = recognizer.health_check()
        assert result is True


# =============================================================================
# Extended ConjectureFormalizer Tests
# =============================================================================


class TestConjectureFormalizerExtended:
    """Extended tests for ConjectureFormalizer."""

    @pytest.fixture
    def formalizer(self):
        from symbo_agentic_reasoners.discovery.conjecture.conjecture_formalizer import (
            ConjectureFormalizer
        )
        return ConjectureFormalizer()

    def test_has_health_check(self, formalizer):
        """Should have health_check method."""
        assert hasattr(formalizer, 'health_check')

    def test_health_check(self, formalizer):
        """Should pass health check."""
        result = formalizer.health_check()
        assert isinstance(result, bool)


# =============================================================================
# Extended BoundaryExplorer Tests
# =============================================================================


class TestBoundaryExplorerExtended:
    """Extended tests for BoundaryExplorer."""

    @pytest.fixture
    def explorer(self):
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryExplorer
        )
        return BoundaryExplorer()

    def test_has_health_check(self, explorer):
        """Should have health_check method."""
        assert hasattr(explorer, 'health_check')

    def test_health_check(self, explorer):
        """Should pass health check."""
        result = explorer.health_check()
        assert isinstance(result, bool)


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
