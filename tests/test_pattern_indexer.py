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
Pattern Indexer Tests
=====================

Comprehensive tests for the PatternIndexer agent:
- Initialization and configuration
- Pattern indexing
- Similarity search
- LSH indexing
- BDI interface
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.middleware.pattern_indexer import (
    PatternIndexer,
    PatternType,
    SolutionPattern,
    PatternMatch,
)
from symbo_agentic_reasoners.core.blackboard import Blackboard
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def indexer():
    """Create a PatternIndexer instance."""
    return PatternIndexer()


@pytest.fixture
def indexer_with_infrastructure():
    """Create PatternIndexer with blackboard and DF."""
    bb = Blackboard()
    df = DirectoryFacilitator()
    return PatternIndexer(blackboard=bb, df=df)


# =============================================================================
# PatternType Enum Tests
# =============================================================================


class TestPatternType:
    """Tests for PatternType enum."""

    def test_pattern_types_exist(self):
        """PatternType should have expected values."""
        assert hasattr(PatternType, 'ALGEBRAIC')
        assert hasattr(PatternType, 'CALCULUS')
        assert hasattr(PatternType, 'GEOMETRIC')
        assert hasattr(PatternType, 'COMBINATORIAL')
        assert hasattr(PatternType, 'PROOF')
        assert hasattr(PatternType, 'TRANSFORM')
        assert hasattr(PatternType, 'UNKNOWN')

    def test_pattern_type_values(self):
        """PatternType values should be strings."""
        assert PatternType.ALGEBRAIC.value == "algebraic"
        assert PatternType.CALCULUS.value == "calculus"
        assert PatternType.PROOF.value == "proof"


# =============================================================================
# SolutionPattern Tests
# =============================================================================


class TestSolutionPattern:
    """Tests for SolutionPattern dataclass."""

    def test_create_pattern(self):
        """Should create a pattern with required fields."""
        pattern = SolutionPattern(
            pattern_id="test_pattern",
            name="Test Pattern",
            pattern_type=PatternType.ALGEBRAIC,
            structure="x + y = y + x"
        )
        assert pattern.pattern_id == "test_pattern"
        assert pattern.name == "Test Pattern"
        assert pattern.pattern_type == PatternType.ALGEBRAIC
        assert pattern.structure == "x + y = y + x"

    def test_pattern_defaults(self):
        """Should have sensible defaults."""
        pattern = SolutionPattern(
            pattern_id="test",
            name="Test",
            pattern_type=PatternType.UNKNOWN,
            structure="test"
        )
        assert pattern.usage_count == 0
        assert pattern.success_rate == 1.0
        assert pattern.prerequisites == []
        assert pattern.examples == []
        assert pattern.embedding is None

    def test_pattern_to_dict(self):
        """to_dict should return dictionary representation."""
        pattern = SolutionPattern(
            pattern_id="test",
            name="Test Pattern",
            pattern_type=PatternType.CALCULUS,
            structure="d/dx(x^2) = 2x",
            usage_count=5,
            success_rate=0.9
        )
        d = pattern.to_dict()

        assert d['pattern_id'] == "test"
        assert d['name'] == "Test Pattern"
        assert d['type'] == "calculus"
        assert d['usage_count'] == 5
        assert d['success_rate'] == 0.9


# =============================================================================
# PatternMatch Tests
# =============================================================================


class TestPatternMatch:
    """Tests for PatternMatch dataclass."""

    def test_create_match(self):
        """Should create a pattern match."""
        pattern = SolutionPattern(
            pattern_id="test",
            name="Test",
            pattern_type=PatternType.ALGEBRAIC,
            structure="test"
        )
        match = PatternMatch(
            pattern=pattern,
            similarity_score=0.85,
            relevance_reason="High similarity"
        )

        assert match.pattern is pattern
        assert match.similarity_score == 0.85
        assert match.relevance_reason == "High similarity"

    def test_match_to_dict(self):
        """to_dict should return dictionary."""
        pattern = SolutionPattern(
            pattern_id="test",
            name="Test",
            pattern_type=PatternType.ALGEBRAIC,
            structure="test"
        )
        match = PatternMatch(
            pattern=pattern,
            similarity_score=0.75,
            relevance_reason="Matching terms"
        )

        d = match.to_dict()
        assert d['pattern_id'] == "test"
        assert d['name'] == "Test"
        assert d['similarity'] == 0.75
        assert d['reason'] == "Matching terms"


# =============================================================================
# PatternIndexer Initialization Tests
# =============================================================================


class TestPatternIndexerInitialization:
    """Tests for PatternIndexer initialization."""

    def test_basic_initialization(self, indexer):
        """Should initialize with defaults."""
        assert indexer is not None
        assert indexer.agent_id == 'pattern_indexer_001'

    def test_custom_agent_id(self):
        """Should accept custom agent ID."""
        indexer = PatternIndexer(agent_id='custom_indexer')
        assert indexer.agent_id == 'custom_indexer'

    def test_initialization_with_blackboard(self):
        """Should initialize with blackboard."""
        bb = Blackboard()
        indexer = PatternIndexer(blackboard=bb)
        assert indexer.blackboard is bb

    def test_initialization_with_df(self):
        """Should initialize with directory facilitator."""
        df = DirectoryFacilitator()
        indexer = PatternIndexer(df=df)
        assert indexer.df is df

    def test_common_patterns_initialized(self, indexer):
        """Should initialize with common patterns."""
        patterns = indexer.list_patterns()
        assert len(patterns) > 0

        # Check for known patterns
        pattern_names = [p.name for p in patterns]
        assert "Quadratic Formula" in pattern_names
        assert "Integration by Parts" in pattern_names
        assert "Chain Rule" in pattern_names

    def test_statistics_initialized(self, indexer):
        """Should initialize statistics to zero."""
        assert indexer.tasks_executed >= 0
        assert indexer.patterns_indexed >= 0
        assert indexer.searches_performed == 0


# =============================================================================
# Pattern Indexing Tests
# =============================================================================


class TestPatternIndexing:
    """Tests for pattern indexing."""

    def test_index_pattern(self, indexer):
        """Should index a pattern."""
        pattern = SolutionPattern(
            pattern_id="custom_pattern",
            name="Custom Pattern",
            pattern_type=PatternType.ALGEBRAIC,
            structure="a + b = b + a"
        )

        pid = indexer.index_pattern(pattern)

        assert pid == "custom_pattern"
        assert pattern.pattern_id in indexer.patterns

    def test_indexed_pattern_has_embedding(self, indexer):
        """Indexed pattern should have embedding."""
        pattern = SolutionPattern(
            pattern_id="embed_test",
            name="Embedding Test",
            pattern_type=PatternType.CALCULUS,
            structure="test structure"
        )

        indexer.index_pattern(pattern)
        stored = indexer.get_pattern("embed_test")

        assert stored.embedding is not None

    def test_index_pattern_updates_lsh(self, indexer):
        """Should update LSH index."""
        initial_lsh_size = len(indexer.lsh_index)

        pattern = SolutionPattern(
            pattern_id="lsh_test",
            name="LSH Test",
            pattern_type=PatternType.PROOF,
            structure="proof by induction"
        )

        indexer.index_pattern(pattern)

        # LSH index should have entry for this pattern
        found = False
        for bucket in indexer.lsh_index.values():
            if "lsh_test" in bucket:
                found = True
                break
        assert found

    def test_index_increments_counter(self, indexer):
        """Should increment patterns_indexed counter."""
        initial = indexer.patterns_indexed

        pattern = SolutionPattern(
            pattern_id="counter_test",
            name="Counter Test",
            pattern_type=PatternType.UNKNOWN,
            structure="test"
        )

        indexer.index_pattern(pattern)

        assert indexer.patterns_indexed == initial + 1


# =============================================================================
# Pattern Search Tests
# =============================================================================


class TestPatternSearch:
    """Tests for pattern search."""

    def test_search_returns_matches(self, indexer):
        """Search should return pattern matches."""
        matches = indexer.search_patterns("quadratic equation polynomial")

        assert isinstance(matches, list)
        assert len(matches) > 0
        assert all(isinstance(m, PatternMatch) for m in matches)

    def test_search_with_top_k(self, indexer):
        """Should respect top_k parameter."""
        matches = indexer.search_patterns("equation", top_k=2)

        assert len(matches) <= 2

    def test_search_with_pattern_type_filter(self, indexer):
        """Should filter by pattern type."""
        matches = indexer.search_patterns(
            "derivative",
            pattern_type=PatternType.CALCULUS
        )

        for match in matches:
            assert match.pattern.pattern_type == PatternType.CALCULUS

    def test_search_with_min_similarity(self, indexer):
        """Should respect minimum similarity threshold."""
        matches = indexer.search_patterns(
            "integration",
            min_similarity=0.5
        )

        for match in matches:
            assert match.similarity_score >= 0.5

    def test_search_results_sorted_by_similarity(self, indexer):
        """Results should be sorted by similarity descending."""
        matches = indexer.search_patterns("polynomial equation")

        if len(matches) >= 2:
            for i in range(len(matches) - 1):
                assert matches[i].similarity_score >= matches[i + 1].similarity_score

    def test_search_increments_counter(self, indexer):
        """Should increment searches_performed counter."""
        initial = indexer.searches_performed

        indexer.search_patterns("test query")

        assert indexer.searches_performed == initial + 1

    def test_search_empty_query(self, indexer):
        """Should handle empty query."""
        matches = indexer.search_patterns("")

        assert isinstance(matches, list)


# =============================================================================
# Embedding and Similarity Tests
# =============================================================================


class TestEmbeddingsAndSimilarity:
    """Tests for embedding computation and similarity."""

    def test_compute_embedding(self, indexer):
        """Should compute embedding for text."""
        embedding = indexer._compute_embedding("test text for embedding")

        assert embedding is not None
        assert len(embedding) == indexer.EMBEDDING_DIM

    def test_compute_similarity(self, indexer):
        """Should compute similarity between embeddings."""
        emb1 = indexer._compute_embedding("integration by parts")
        emb2 = indexer._compute_embedding("integration method parts")
        emb3 = indexer._compute_embedding("completely different topic")

        sim_similar = indexer._compute_similarity(emb1, emb2)
        sim_different = indexer._compute_similarity(emb1, emb3)

        # Similar texts should have higher similarity
        assert sim_similar > sim_different

    def test_compute_lsh_hash(self, indexer):
        """Should compute LSH hash for embedding."""
        embedding = indexer._compute_embedding("test")
        lsh_hash = indexer._compute_lsh_hash(embedding)

        assert isinstance(lsh_hash, int)


# =============================================================================
# Pattern Statistics Tests
# =============================================================================


class TestPatternStatistics:
    """Tests for pattern statistics."""

    def test_update_pattern_stats_success(self, indexer):
        """Should update pattern stats on success."""
        # Get a known pattern
        patterns = indexer.list_patterns()
        if patterns:
            pid = patterns[0].pattern_id
            initial_count = patterns[0].usage_count

            indexer.update_pattern_stats(pid, success=True)

            updated = indexer.get_pattern(pid)
            assert updated.usage_count == initial_count + 1

    def test_update_pattern_stats_failure(self, indexer):
        """Should update success rate on failure."""
        patterns = indexer.list_patterns()
        if patterns:
            pid = patterns[0].pattern_id

            # Update several times with failure
            for _ in range(5):
                indexer.update_pattern_stats(pid, success=False)

            updated = indexer.get_pattern(pid)
            # Success rate should decrease
            assert updated.success_rate < 1.0

    def test_update_nonexistent_pattern(self, indexer):
        """Should handle nonexistent pattern gracefully."""
        # Should not raise
        indexer.update_pattern_stats("nonexistent", success=True)


# =============================================================================
# Pattern Retrieval Tests
# =============================================================================


class TestPatternRetrieval:
    """Tests for pattern retrieval."""

    def test_get_pattern_exists(self, indexer):
        """Should get existing pattern."""
        patterns = indexer.list_patterns()
        if patterns:
            pid = patterns[0].pattern_id

            pattern = indexer.get_pattern(pid)

            assert pattern is not None
            assert pattern.pattern_id == pid

    def test_get_pattern_not_exists(self, indexer):
        """Should return None for nonexistent pattern."""
        pattern = indexer.get_pattern("nonexistent_pattern")

        assert pattern is None

    def test_list_patterns_all(self, indexer):
        """Should list all patterns."""
        patterns = indexer.list_patterns()

        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_list_patterns_by_type(self, indexer):
        """Should list patterns filtered by type."""
        patterns = indexer.list_patterns(pattern_type=PatternType.CALCULUS)

        for pattern in patterns:
            assert pattern.pattern_type == PatternType.CALCULUS


# =============================================================================
# BDI Interface Tests
# =============================================================================


class TestPatternIndexerBDI:
    """Tests for BDI interface."""

    def test_update_beliefs(self, indexer):
        """update_beliefs should not raise."""
        indexer.update_beliefs()

    def test_deliberate(self, indexer):
        """deliberate should return list."""
        result = indexer.deliberate()
        assert isinstance(result, list)

    def test_execute_step(self, indexer):
        """execute_step should not raise."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention
        intention = Mock(spec=Intention)
        indexer.execute_step(intention)

    def test_get_statistics(self, indexer):
        """Should return statistics dictionary."""
        stats = indexer.get_statistics()

        assert isinstance(stats, dict)
        assert 'tasks_executed' in stats
        assert 'patterns_indexed' in stats
        assert 'searches_performed' in stats
        assert 'lsh_hits' in stats
        assert 'linear_fallbacks' in stats


# =============================================================================
# Process Task Tests
# =============================================================================


class TestPatternIndexerProcess:
    """Tests for process method."""

    def test_process_search_operation(self, indexer_with_infrastructure):
        """Should process search operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'search',
            'query': 'integration',
            'top_k': 3
        }
        task_entry.conversation_id = 'test_conv'

        result = indexer_with_infrastructure.process(task_entry)

        assert result is not None

    def test_process_list_operation(self, indexer_with_infrastructure):
        """Should process list operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'list',
            'pattern_type': 'calculus'
        }
        task_entry.conversation_id = 'test_conv'

        result = indexer_with_infrastructure.process(task_entry)

        assert result is not None

    def test_process_unknown_operation(self, indexer_with_infrastructure):
        """Should handle unknown operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'unknown_op'
        }
        task_entry.conversation_id = 'test_conv'

        result = indexer_with_infrastructure.process(task_entry)

        assert result is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestPatternIndexerIntegration:
    """Integration tests for PatternIndexer."""

    def test_full_workflow(self):
        """Test complete pattern workflow."""
        bb = Blackboard()
        df = DirectoryFacilitator()
        indexer = PatternIndexer(blackboard=bb, df=df)

        # Index custom pattern
        custom = SolutionPattern(
            pattern_id="taylor_expansion",
            name="Taylor Series",
            pattern_type=PatternType.CALCULUS,
            structure="f(x) = sum(f^(n)(a)/n! * (x-a)^n)",
            prerequisites=["infinitely differentiable"]
        )
        indexer.index_pattern(custom)

        # Search for it
        matches = indexer.search_patterns("taylor series expansion")

        # Should find the custom pattern
        pattern_ids = [m.pattern.pattern_id for m in matches]
        assert "taylor_expansion" in pattern_ids

    def test_lsh_vs_linear_search(self):
        """Test that LSH search is used when possible."""
        indexer = PatternIndexer()

        # Perform several searches
        for _ in range(5):
            indexer.search_patterns("integration derivative calculus")

        stats = indexer.get_statistics()

        # Should have some combination of LSH hits and linear fallbacks
        assert stats['searches_performed'] == 5
        assert stats['lsh_hits'] + stats['linear_fallbacks'] == 5


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
