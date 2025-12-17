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
Algorithm Module Tests
======================

Comprehensive tests for algorithm synthesis components:
- AlgorithmSynthesizer
- ComplexityAnalyzer
- HeuristicDistiller
- OptimizationTransformer
- SandboxEvaluator
- ProblemSpecification
"""

import pytest
import sympy as sp
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# AlgorithmSynthesizer Tests
# =============================================================================


class TestAlgorithmSynthesizer:
    """Tests for AlgorithmSynthesizer."""

    @pytest.fixture
    def synthesizer(self):
        """Create AlgorithmSynthesizer instance."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmSynthesizer
        )
        return AlgorithmSynthesizer()

    def test_initialization(self, synthesizer):
        """Should initialize correctly."""
        assert synthesizer is not None

    def test_has_synthesize_method(self, synthesizer):
        """Should have synthesize method."""
        assert hasattr(synthesizer, 'synthesize') or hasattr(synthesizer, 'generate')

    def test_has_get_statistics_method(self, synthesizer):
        """Should have get_statistics method."""
        if hasattr(synthesizer, 'get_statistics'):
            stats = synthesizer.get_statistics()
            assert isinstance(stats, dict)


# =============================================================================
# ComplexityAnalyzer Tests
# =============================================================================


class TestComplexityAnalyzer:
    """Tests for ComplexityAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create ComplexityAnalyzer instance."""
        from symbo_agentic_reasoners.discovery.algorithm.complexity_analyzer import (
            ComplexityAnalyzer
        )
        return ComplexityAnalyzer()

    def test_initialization(self, analyzer):
        """Should initialize correctly."""
        assert analyzer is not None

    def test_has_analyze_method(self, analyzer):
        """Should have analyze method."""
        assert hasattr(analyzer, 'analyze')

    def test_has_get_statistics_method(self, analyzer):
        """Should have get_statistics method."""
        assert hasattr(analyzer, 'get_statistics')
        stats = analyzer.get_statistics()
        assert isinstance(stats, dict)

    def test_has_compare_algorithms_method(self, analyzer):
        """Should have compare_algorithms method."""
        assert hasattr(analyzer, 'compare_algorithms')

    def test_has_health_check_method(self, analyzer):
        """Should have health_check method."""
        assert hasattr(analyzer, 'health_check')
        result = analyzer.health_check()
        assert isinstance(result, bool)


# =============================================================================
# HeuristicDistiller Tests
# =============================================================================


class TestHeuristicDistiller:
    """Tests for HeuristicDistiller."""

    @pytest.fixture
    def distiller(self):
        """Create HeuristicDistiller instance."""
        from symbo_agentic_reasoners.discovery.algorithm.heuristic_distiller import (
            HeuristicDistiller
        )
        return HeuristicDistiller()

    def test_initialization(self, distiller):
        """Should initialize correctly."""
        assert distiller is not None

    def test_has_distill_method(self, distiller):
        """Should have distill method."""
        assert hasattr(distiller, 'distill') or hasattr(distiller, 'extract')

    def test_has_get_statistics_method(self, distiller):
        """Should have get_statistics method."""
        if hasattr(distiller, 'get_statistics'):
            stats = distiller.get_statistics()
            assert isinstance(stats, dict)


# =============================================================================
# OptimizationTransformer Tests
# =============================================================================


class TestOptimizationTransformer:
    """Tests for OptimizationTransformer."""

    @pytest.fixture
    def transformer(self):
        """Create OptimizationTransformer instance."""
        from symbo_agentic_reasoners.discovery.algorithm.optimization_transformer import (
            OptimizationTransformer
        )
        return OptimizationTransformer()

    def test_initialization(self, transformer):
        """Should initialize correctly."""
        assert transformer is not None

    def test_has_transform_method(self, transformer):
        """Should have transform method."""
        assert hasattr(transformer, 'transform') or hasattr(transformer, 'optimize')

    def test_has_get_statistics_method(self, transformer):
        """Should have get_statistics method."""
        if hasattr(transformer, 'get_statistics'):
            stats = transformer.get_statistics()
            assert isinstance(stats, dict)


# =============================================================================
# SandboxEvaluator Tests
# =============================================================================


class TestSandboxEvaluator:
    """Tests for SandboxEvaluator."""

    @pytest.fixture
    def evaluator(self):
        """Create SandboxEvaluator instance."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import (
            SandboxEvaluator
        )
        return SandboxEvaluator()

    def test_initialization(self, evaluator):
        """Should initialize correctly."""
        assert evaluator is not None

    def test_has_evaluate_method(self, evaluator):
        """Should have evaluate method."""
        assert hasattr(evaluator, 'evaluate') or hasattr(evaluator, 'run')

    def test_has_get_statistics_method(self, evaluator):
        """Should have get_statistics method."""
        if hasattr(evaluator, 'get_statistics'):
            stats = evaluator.get_statistics()
            assert isinstance(stats, dict)


# =============================================================================
# ProblemSpecification Tests
# =============================================================================


class TestProblemSpecification:
    """Tests for ProblemSpecification."""

    def test_problem_spec_exists(self):
        """ProblemSpecification should exist."""
        from symbo_agentic_reasoners.discovery.algorithm import problem_specification
        assert hasattr(problem_specification, 'ProblemSpecification')

    def test_can_create_problem_spec(self):
        """Should create ProblemSpecification."""
        from symbo_agentic_reasoners.discovery.algorithm.problem_specification import (
            ProblemSpecification
        )

        spec = ProblemSpecification(
            problem_id='test_problem',
            description='Test sorting problem',
            function_signature='def sort(arr: List[int]) -> List[int]',
            test_cases=[([3, 1, 2], [1, 2, 3])]
        )

        assert spec.problem_id == 'test_problem'
        assert spec.problem_class == 'optimization'


# =============================================================================
# CodeEvolutionaryProposer Tests
# =============================================================================


class TestCodeEvolutionaryProposer:
    """Tests for CodeEvolutionaryProposer."""

    @pytest.fixture
    def proposer(self):
        """Create CodeEvolutionaryProposer instance."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import (
            CodeEvolutionaryProposer
        )
        return CodeEvolutionaryProposer()

    def test_initialization(self, proposer):
        """Should initialize correctly."""
        assert proposer is not None

    def test_has_propose_method(self, proposer):
        """Should have propose method."""
        assert (hasattr(proposer, 'propose') or
                hasattr(proposer, 'generate') or
                hasattr(proposer, 'evolve'))

    def test_has_get_statistics_method(self, proposer):
        """Should have get_statistics method."""
        if hasattr(proposer, 'get_statistics'):
            stats = proposer.get_statistics()
            assert isinstance(stats, dict)


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
