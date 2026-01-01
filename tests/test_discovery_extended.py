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
Extended Discovery Module Tests
===============================

Additional tests to improve coverage for discovery modules.
"""

import pytest


# =============================================================================
# Exhaustive Enumerator Tests
# =============================================================================


class TestExhaustiveEnumerator:
    """Tests for ExhaustiveEnumerator."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            ExhaustiveEnumerator
        )
        assert ExhaustiveEnumerator is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            ExhaustiveEnumerator
        )
        enumerator = ExhaustiveEnumerator()
        assert enumerator is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            ExhaustiveEnumerator
        )
        enumerator = ExhaustiveEnumerator()
        assert hasattr(enumerator, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            ExhaustiveEnumerator
        )
        enumerator = ExhaustiveEnumerator()
        assert hasattr(enumerator, 'health_check')

    def test_get_statistics_returns_dict(self):
        """get_statistics should return dict."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            ExhaustiveEnumerator
        )
        enumerator = ExhaustiveEnumerator()
        stats = enumerator.get_statistics()
        assert isinstance(stats, dict)

    def test_health_check_exists(self):
        """health_check should exist."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            ExhaustiveEnumerator
        )
        enumerator = ExhaustiveEnumerator()
        assert hasattr(enumerator, 'health_check')


# =============================================================================
# Parallel Search Manager Tests
# =============================================================================


class TestParallelSearchManager:
    """Tests for ParallelSearchManager."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import (
            ParallelSearchManager
        )
        assert ParallelSearchManager is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import (
            ParallelSearchManager
        )
        manager = ParallelSearchManager()
        assert manager is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import (
            ParallelSearchManager
        )
        manager = ParallelSearchManager()
        assert hasattr(manager, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import (
            ParallelSearchManager
        )
        manager = ParallelSearchManager()
        assert hasattr(manager, 'health_check')


# =============================================================================
# Search Tree Manager Tests
# =============================================================================


class TestSearchTreeManager:
    """Tests for SearchTreeManager."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import (
            SearchTreeManager
        )
        assert SearchTreeManager is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import (
            SearchTreeManager
        )
        manager = SearchTreeManager()
        assert manager is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import (
            SearchTreeManager
        )
        manager = SearchTreeManager()
        assert hasattr(manager, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.deep_search.search_tree_manager import (
            SearchTreeManager
        )
        manager = SearchTreeManager()
        assert hasattr(manager, 'health_check')


# =============================================================================
# Boundary Explorer Tests
# =============================================================================


class TestBoundaryExplorer:
    """Tests for BoundaryExplorer."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryExplorer
        )
        assert BoundaryExplorer is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryExplorer
        )
        explorer = BoundaryExplorer()
        assert explorer is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryExplorer
        )
        explorer = BoundaryExplorer()
        assert hasattr(explorer, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryExplorer
        )
        explorer = BoundaryExplorer()
        assert hasattr(explorer, 'health_check')


# =============================================================================
# Heuristic Distiller Tests
# =============================================================================


class TestHeuristicDistiller:
    """Tests for HeuristicDistiller."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.algorithm.heuristic_distiller import (
            HeuristicDistiller
        )
        assert HeuristicDistiller is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.algorithm.heuristic_distiller import (
            HeuristicDistiller
        )
        distiller = HeuristicDistiller()
        assert distiller is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.algorithm.heuristic_distiller import (
            HeuristicDistiller
        )
        distiller = HeuristicDistiller()
        assert hasattr(distiller, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.algorithm.heuristic_distiller import (
            HeuristicDistiller
        )
        distiller = HeuristicDistiller()
        assert hasattr(distiller, 'health_check')


# =============================================================================
# Optimization Transformer Tests
# =============================================================================


class TestOptimizationTransformer:
    """Tests for OptimizationTransformer."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.algorithm.optimization_transformer import (
            OptimizationTransformer
        )
        assert OptimizationTransformer is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.algorithm.optimization_transformer import (
            OptimizationTransformer
        )
        transformer = OptimizationTransformer()
        assert transformer is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.algorithm.optimization_transformer import (
            OptimizationTransformer
        )
        transformer = OptimizationTransformer()
        assert hasattr(transformer, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.algorithm.optimization_transformer import (
            OptimizationTransformer
        )
        transformer = OptimizationTransformer()
        assert hasattr(transformer, 'health_check')


# =============================================================================
# Sandbox Evaluator Tests
# =============================================================================


class TestSandboxEvaluator:
    """Tests for SandboxEvaluator."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
            SandboxEvaluator
        )
        assert SandboxEvaluator is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
            SandboxEvaluator
        )
        evaluator = SandboxEvaluator()
        assert evaluator is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
            SandboxEvaluator
        )
        evaluator = SandboxEvaluator()
        assert hasattr(evaluator, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
            SandboxEvaluator
        )
        evaluator = SandboxEvaluator()
        assert hasattr(evaluator, 'health_check')


# =============================================================================
# Complexity Analyzer Tests
# =============================================================================


class TestComplexityAnalyzer:
    """Tests for ComplexityAnalyzer."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.algorithm.complexity_analyzer import (
            ComplexityAnalyzer
        )
        assert ComplexityAnalyzer is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.algorithm.complexity_analyzer import (
            ComplexityAnalyzer
        )
        analyzer = ComplexityAnalyzer()
        assert analyzer is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.algorithm.complexity_analyzer import (
            ComplexityAnalyzer
        )
        analyzer = ComplexityAnalyzer()
        assert hasattr(analyzer, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.algorithm.complexity_analyzer import (
            ComplexityAnalyzer
        )
        analyzer = ComplexityAnalyzer()
        assert hasattr(analyzer, 'health_check')


# =============================================================================
# Code Evolutionary Proposer Tests
# =============================================================================


class TestCodeEvolutionaryProposer:
    """Tests for CodeEvolutionaryProposer."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import (
            CodeEvolutionaryProposer
        )
        assert CodeEvolutionaryProposer is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import (
            CodeEvolutionaryProposer
        )
        proposer = CodeEvolutionaryProposer()
        assert proposer is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import (
            CodeEvolutionaryProposer
        )
        proposer = CodeEvolutionaryProposer()
        assert hasattr(proposer, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import (
            CodeEvolutionaryProposer
        )
        proposer = CodeEvolutionaryProposer()
        assert hasattr(proposer, 'health_check')


# =============================================================================
# Auto Formalization Pipeline Tests
# =============================================================================


class TestAutoFormalizationPipeline:
    """Tests for AutoFormalizationPipeline."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            AutoFormalizationPipeline
        )
        assert AutoFormalizationPipeline is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            AutoFormalizationPipeline
        )
        pipeline = AutoFormalizationPipeline()
        assert pipeline is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            AutoFormalizationPipeline
        )
        pipeline = AutoFormalizationPipeline()
        assert hasattr(pipeline, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            AutoFormalizationPipeline
        )
        pipeline = AutoFormalizationPipeline()
        assert hasattr(pipeline, 'health_check')


# =============================================================================
# Vector Database Updater Tests
# =============================================================================


class TestVectorDatabaseUpdater:
    """Tests for VectorDatabaseUpdater."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.discovery.formal.vector_database_updater import (
            VectorDatabaseUpdater
        )
        assert VectorDatabaseUpdater is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.discovery.formal.vector_database_updater import (
            VectorDatabaseUpdater
        )
        updater = VectorDatabaseUpdater()
        assert updater is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.discovery.formal.vector_database_updater import (
            VectorDatabaseUpdater
        )
        updater = VectorDatabaseUpdater()
        assert hasattr(updater, 'get_statistics')

    def test_has_health_check(self):
        """Should have health_check."""
        from symbo_agentic_reasoners.discovery.formal.vector_database_updater import (
            VectorDatabaseUpdater
        )
        updater = VectorDatabaseUpdater()
        assert hasattr(updater, 'health_check')


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
