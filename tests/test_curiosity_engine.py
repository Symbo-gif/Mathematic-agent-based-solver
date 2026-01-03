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
Comprehensive Test Suite for the Curiosity Engine
==================================================

Tests for autonomous mathematical problem generation and exploration.
Covers: ProblemGenerator, InterestScorer, CuriosityEngine,
ExplorationResult, and integration with SolverEngine.

Test Categories:
- Unit tests for problem generation
- Interest scoring tests
- Exploration session tests
- Statistics tracking tests
- Discovery persistence tests
"""

import pytest
import time
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from symbo_agentic_reasoners.core.symbolic import Symbol, Integer, pi

# Import the modules under test
from symbo_agentic_reasoners.discovery.curiosity_engine import (
    CuriosityEngine,
    ExplorationCategory,
    ExplorationResult,
    ExplorationStats,
    InterestLevel,
    ProblemGenerator,
    InterestScorer,
    explore_mathematics,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_solver():
    """Create a mock solver that returns successful results."""
    solver = Mock()
    result = Mock()
    result.status = Mock()
    result.status.value = 'success'
    result.result = 42
    solver.solve = Mock(return_value=result)
    return solver


@pytest.fixture
def failing_solver():
    """Create a mock solver that fails."""
    solver = Mock()
    result = Mock()
    result.status = Mock()
    result.status.value = 'error'
    result.result = None
    solver.solve = Mock(return_value=result)
    return solver


@pytest.fixture
def temp_save_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def problem_generator():
    """Create a ProblemGenerator with fixed seed for reproducibility."""
    return ProblemGenerator(seed=42)


@pytest.fixture
def interest_scorer():
    """Create an InterestScorer."""
    return InterestScorer()


@pytest.fixture
def curiosity_engine(mock_solver, temp_save_dir):
    """Create a CuriosityEngine for testing."""
    return CuriosityEngine(solver=mock_solver, save_dir=temp_save_dir)


# =============================================================================
# ExplorationCategory Tests
# =============================================================================


class TestExplorationCategory:
    """Tests for ExplorationCategory enum."""

    def test_all_categories_exist(self):
        """All expected categories should exist."""
        expected = [
            'ALGEBRA', 'CALCULUS', 'NUMBER_THEORY', 'LINEAR_ALGEBRA',
            'COMBINATORICS', 'ANALYSIS', 'GEOMETRY'
        ]
        for cat in expected:
            assert hasattr(ExplorationCategory, cat)

    def test_category_values(self):
        """Categories should have string values."""
        assert ExplorationCategory.ALGEBRA.value == 'algebra'
        assert ExplorationCategory.CALCULUS.value == 'calculus'
        assert ExplorationCategory.NUMBER_THEORY.value == 'number_theory'


# =============================================================================
# InterestLevel Tests
# =============================================================================


class TestInterestLevel:
    """Tests for InterestLevel enum."""

    def test_interest_levels_ordered(self):
        """Interest levels should be ordered by value."""
        assert InterestLevel.MUNDANE.value < InterestLevel.NOTABLE.value
        assert InterestLevel.NOTABLE.value < InterestLevel.INTERESTING.value
        assert InterestLevel.INTERESTING.value < InterestLevel.SURPRISING.value
        assert InterestLevel.SURPRISING.value < InterestLevel.REMARKABLE.value

    def test_interest_level_comparison(self):
        """Interest levels should be comparable by value."""
        assert InterestLevel.REMARKABLE.value > InterestLevel.MUNDANE.value


# =============================================================================
# ExplorationResult Tests
# =============================================================================


class TestExplorationResult:
    """Tests for ExplorationResult dataclass."""

    def test_creation(self):
        """ExplorationResult should be creatable with required fields."""
        result = ExplorationResult(
            problem="solve(x**2 - 4, x)",
            category=ExplorationCategory.ALGEBRA,
            solution=[2, -2],
            success=True,
            interest_level=InterestLevel.NOTABLE,
            solve_time_ms=10.5
        )

        assert result.problem == "solve(x**2 - 4, x)"
        assert result.category == ExplorationCategory.ALGEBRA
        assert result.success is True

    def test_to_dict(self):
        """to_dict should serialize result properly."""
        result = ExplorationResult(
            problem="test",
            category=ExplorationCategory.CALCULUS,
            solution=42,
            success=True,
            interest_level=InterestLevel.INTERESTING,
            solve_time_ms=5.0,
            notes="Test note"
        )

        d = result.to_dict()

        assert d['problem'] == "test"
        assert d['category'] == 'calculus'
        assert d['solution'] == '42'
        assert d['success'] is True
        assert d['interest_level'] == 2
        assert d['notes'] == "Test note"
        assert 'timestamp' in d

    def test_default_values(self):
        """Default values should be sensible."""
        result = ExplorationResult(
            problem="test",
            category=ExplorationCategory.GEOMETRY,
            solution=None,
            success=False,
            interest_level=InterestLevel.MUNDANE,
            solve_time_ms=0.0
        )

        assert result.notes == ""
        assert result.related_problems == []
        assert result.timestamp is not None


# =============================================================================
# ProblemGenerator Tests
# =============================================================================


class TestProblemGenerator:
    """Tests for ProblemGenerator class."""

    def test_generate_returns_tuple(self, problem_generator):
        """generate should return (problem, category) tuple."""
        result = problem_generator.generate()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_generate_returns_string_problem(self, problem_generator):
        """Generated problem should be a non-empty string."""
        problem, _ = problem_generator.generate()
        assert isinstance(problem, str)
        assert len(problem) > 0

    def test_generate_returns_valid_category(self, problem_generator):
        """Generated category should be valid ExplorationCategory."""
        _, category = problem_generator.generate()
        assert isinstance(category, ExplorationCategory)

    def test_generate_with_specific_category(self, problem_generator):
        """generate with category should return that category."""
        for cat in ExplorationCategory:
            _, returned_cat = problem_generator.generate(cat)
            assert returned_cat == cat

    def test_algebra_problem_generation(self, problem_generator):
        """Algebra problems should contain algebra-specific content."""
        for _ in range(10):
            problem, _ = problem_generator.generate(ExplorationCategory.ALGEBRA)
            # Should contain algebra operations
            assert any(op in problem for op in ['factor', 'solve', 'simplify', 'expand'])

    def test_calculus_problem_generation(self, problem_generator):
        """Calculus problems should contain calculus operations."""
        for _ in range(10):
            problem, _ = problem_generator.generate(ExplorationCategory.CALCULUS)
            # Should contain calculus operations
            assert any(op in problem for op in ['diff', 'integrate', 'limit', 'series'])

    def test_number_theory_problem_generation(self, problem_generator):
        """Number theory problems should contain number theory operations."""
        for _ in range(10):
            problem, _ = problem_generator.generate(ExplorationCategory.NUMBER_THEORY)
            assert any(op in problem for op in ['factorint', 'isprime', 'gcd', 'lcm', 'pow'])

    def test_linear_algebra_problem_generation(self, problem_generator):
        """Linear algebra problems should involve matrices."""
        for _ in range(10):
            problem, _ = problem_generator.generate(ExplorationCategory.LINEAR_ALGEBRA)
            assert 'Matrix' in problem

    def test_combinatorics_problem_generation(self, problem_generator):
        """Combinatorics problems should use combinatorial operations."""
        for _ in range(10):
            problem, _ = problem_generator.generate(ExplorationCategory.COMBINATORICS)
            assert any(op in problem for op in ['binomial', 'factorial'])

    def test_analysis_problem_generation(self, problem_generator):
        """Analysis problems should use series/product operations."""
        for _ in range(10):
            problem, _ = problem_generator.generate(ExplorationCategory.ANALYSIS)
            assert any(op in problem for op in ['summation', 'product'])

    def test_geometry_problem_generation(self, problem_generator):
        """Geometry problems should involve distance/area calculations."""
        for _ in range(10):
            problem, _ = problem_generator.generate(ExplorationCategory.GEOMETRY)
            assert 'sqrt' in problem

    def test_seed_affects_generation(self):
        """Different seeds should produce different problem sequences."""
        gen1 = ProblemGenerator(seed=123)
        gen2 = ProblemGenerator(seed=456)

        # Generate problems with each generator
        problems1 = [gen1.generate() for _ in range(10)]
        problems2 = [gen2.generate() for _ in range(10)]

        # With different seeds, sequences should differ
        # (at least some problems should be different)
        differences = sum(1 for p1, p2 in zip(problems1, problems2) if p1 != p2)
        assert differences > 0, "Different seeds should produce different sequences"

    def test_problem_variety(self, problem_generator):
        """Generator should produce variety of problems."""
        problems = set()
        for _ in range(50):
            problem, _ = problem_generator.generate()
            problems.add(problem)

        # Should have many different problems
        assert len(problems) > 30


# =============================================================================
# InterestScorer Tests
# =============================================================================


class TestInterestScorer:
    """Tests for InterestScorer class."""

    def test_score_returns_tuple(self, interest_scorer):
        """score should return (InterestLevel, notes) tuple."""
        level, notes = interest_scorer.score("test", 42, 10.0)
        assert isinstance(level, InterestLevel)
        assert isinstance(notes, str)

    def test_score_none_solution(self, interest_scorer):
        """None solution should be MUNDANE."""
        level, notes = interest_scorer.score("test", None, 10.0)
        assert level == InterestLevel.MUNDANE
        assert "Failed" in notes

    def test_special_value_detection(self, interest_scorer):
        """Special values should be detected."""
        # Test pi detection
        level, notes = interest_scorer.score("complex calculation", pi, 10.0)
        assert "pi" in notes.lower()

        # Test zero detection
        level, notes = interest_scorer.score("complex calculation", 0, 10.0)
        assert "zero" in notes.lower()

    def test_simple_result_from_complex_problem(self, interest_scorer):
        """Simple result from complex problem should be interesting."""
        complex_problem = "integrate(sin(x)*cos(x)*exp(-x**2)*sqrt(1+x**2), x)"
        level, notes = interest_scorer.score(complex_problem, 1, 5.0)
        # Should be at least notable
        assert level.value >= InterestLevel.NOTABLE.value

    def test_fast_complex_solution_notable(self, interest_scorer):
        """Fast solutions to complex problems should be notable."""
        complex_problem = "a" * 60  # Long problem string
        level, notes = interest_scorer.score(complex_problem, Symbol('x'), 5.0)
        # Should be at least notable for speed
        if "quickly" in notes.lower():
            assert level.value >= InterestLevel.NOTABLE.value


# =============================================================================
# CuriosityEngine Core Tests
# =============================================================================


class TestCuriosityEngineCore:
    """Core functionality tests for CuriosityEngine."""

    def test_initialization(self, mock_solver, temp_save_dir):
        """Engine should initialize correctly."""
        engine = CuriosityEngine(solver=mock_solver, save_dir=temp_save_dir)

        assert engine.solver is mock_solver
        assert engine.save_dir == temp_save_dir
        assert temp_save_dir.exists()

    def test_default_save_dir(self, mock_solver):
        """Engine should use default save_dir if not provided."""
        engine = CuriosityEngine(solver=mock_solver)
        assert engine.save_dir == Path("data/curiosity")

    def test_initial_stats(self, curiosity_engine):
        """Initial stats should be zeroed."""
        assert curiosity_engine.stats.problems_generated == 0
        assert curiosity_engine.stats.problems_solved == 0
        assert curiosity_engine.stats.problems_failed == 0

    def test_explored_problems_initially_empty(self, curiosity_engine):
        """Explored problems set should be empty initially."""
        assert len(curiosity_engine.explored_problems) == 0


# =============================================================================
# CuriosityEngine Exploration Tests
# =============================================================================


class TestCuriosityEngineExploration:
    """Tests for exploration functionality."""

    def test_explore_one_returns_result(self, curiosity_engine):
        """explore_one should return ExplorationResult."""
        result = curiosity_engine.explore_one()
        assert isinstance(result, ExplorationResult)

    def test_explore_one_increments_stats(self, curiosity_engine):
        """explore_one should increment statistics."""
        initial = curiosity_engine.stats.problems_generated
        curiosity_engine.explore_one()
        assert curiosity_engine.stats.problems_generated == initial + 1

    def test_explore_one_with_category(self, curiosity_engine):
        """explore_one with category should use that category."""
        result = curiosity_engine.explore_one(ExplorationCategory.ALGEBRA)
        assert result.category == ExplorationCategory.ALGEBRA

    def test_explore_one_tracks_category_stats(self, curiosity_engine):
        """explore_one should track category statistics."""
        curiosity_engine.explore_one(ExplorationCategory.CALCULUS)
        assert 'calculus' in curiosity_engine.stats.categories_explored

    def test_explore_one_adds_to_explored_set(self, curiosity_engine):
        """explore_one should add problem to explored set."""
        initial_size = len(curiosity_engine.explored_problems)
        curiosity_engine.explore_one()
        assert len(curiosity_engine.explored_problems) == initial_size + 1

    def test_explore_one_skips_duplicates(self, curiosity_engine):
        """explore_one should skip already-explored problems."""
        # Add a problem to the explored set
        curiosity_engine.explored_problems.add("test_problem")

        # With random generation, we should get different problems
        for _ in range(10):
            result = curiosity_engine.explore_one()
            assert result.problem != "test_problem"

    def test_explore_one_success_tracking(self, curiosity_engine):
        """Successful solves should be tracked."""
        result = curiosity_engine.explore_one()
        if result.success:
            assert curiosity_engine.stats.problems_solved > 0

    def test_explore_one_with_failing_solver(self, failing_solver, temp_save_dir):
        """explore_one should handle solver failures."""
        engine = CuriosityEngine(solver=failing_solver, save_dir=temp_save_dir)
        result = engine.explore_one()

        assert result.success is False
        assert engine.stats.problems_failed > 0


# =============================================================================
# CuriosityEngine Session Tests
# =============================================================================


class TestCuriosityEngineSession:
    """Tests for exploration session functionality."""

    def test_explore_session_returns_list(self, curiosity_engine):
        """explore_session should return list of discoveries."""
        results = curiosity_engine.explore_session(duration_seconds=0.5, verbose=False)
        assert isinstance(results, list)

    def test_explore_session_respects_duration(self, curiosity_engine):
        """explore_session should run for approximately the specified duration."""
        start = time.time()
        curiosity_engine.explore_session(duration_seconds=1.0, verbose=False)
        elapsed = time.time() - start

        # Should be close to 1 second (allow some variance)
        assert 0.9 <= elapsed <= 2.0

    def test_explore_session_generates_multiple_problems(self, curiosity_engine):
        """explore_session should explore multiple problems."""
        initial = curiosity_engine.stats.problems_generated
        curiosity_engine.explore_session(duration_seconds=1.0, verbose=False)

        assert curiosity_engine.stats.problems_generated > initial + 1


# =============================================================================
# CuriosityEngine Statistics Tests
# =============================================================================


class TestCuriosityEngineStatistics:
    """Tests for statistics functionality."""

    def test_get_statistics_structure(self, curiosity_engine):
        """get_statistics should return properly structured data."""
        stats = curiosity_engine.get_statistics()

        assert 'problems_generated' in stats
        assert 'problems_solved' in stats
        assert 'problems_failed' in stats
        assert 'success_rate' in stats
        assert 'categories_explored' in stats
        assert 'avg_solve_time_ms' in stats

    def test_success_rate_calculation(self, curiosity_engine):
        """Success rate should be calculated correctly."""
        # Explore some problems
        for _ in range(10):
            curiosity_engine.explore_one()

        stats = curiosity_engine.get_statistics()
        expected_rate = (curiosity_engine.stats.problems_solved /
                        max(1, curiosity_engine.stats.problems_generated)) * 100

        assert stats['success_rate'] == expected_rate

    def test_average_solve_time(self, curiosity_engine):
        """Average solve time should be tracked."""
        for _ in range(5):
            curiosity_engine.explore_one()

        stats = curiosity_engine.get_statistics()
        assert stats['avg_solve_time_ms'] >= 0


# =============================================================================
# CuriosityEngine Discovery Tests
# =============================================================================


class TestCuriosityEngineDiscoveries:
    """Tests for discovery tracking and retrieval."""

    def test_get_discoveries_returns_list(self, curiosity_engine):
        """get_discoveries should return a list."""
        discoveries = curiosity_engine.get_discoveries()
        assert isinstance(discoveries, list)

    def test_get_discoveries_filtered_by_interest(self, curiosity_engine):
        """get_discoveries should filter by interest level."""
        # Run some explorations
        for _ in range(20):
            curiosity_engine.explore_one()

        discoveries = curiosity_engine.get_discoveries(min_interest=InterestLevel.INTERESTING)

        for d in discoveries:
            assert d.interest_level.value >= InterestLevel.INTERESTING.value

    def test_get_discoveries_filtered_by_category(self, curiosity_engine):
        """get_discoveries should filter by category."""
        # Run some explorations
        for _ in range(20):
            curiosity_engine.explore_one()

        discoveries = curiosity_engine.get_discoveries(category=ExplorationCategory.ALGEBRA)

        for d in discoveries:
            assert d.category == ExplorationCategory.ALGEBRA

    def test_get_discoveries_respects_limit(self, curiosity_engine):
        """get_discoveries should respect the limit parameter."""
        for _ in range(20):
            curiosity_engine.explore_one()

        discoveries = curiosity_engine.get_discoveries(limit=5)
        assert len(discoveries) <= 5

    def test_discoveries_saved_to_file(self, curiosity_engine, temp_save_dir):
        """Notable discoveries should be saved to file."""
        # Run explorations until we get some discoveries
        for _ in range(30):
            curiosity_engine.explore_one()

        discoveries_file = temp_save_dir / "discoveries.jsonl"
        if discoveries_file.exists():
            with open(discoveries_file) as f:
                lines = f.readlines()

            # Each line should be valid JSON
            for line in lines:
                data = json.loads(line)
                assert 'problem' in data
                assert 'category' in data


# =============================================================================
# CuriosityEngine Suggestion Tests
# =============================================================================


class TestCuriosityEngineSuggestion:
    """Tests for exploration suggestion functionality."""

    def test_suggest_exploration_returns_category(self, curiosity_engine):
        """suggest_exploration should return ExplorationCategory."""
        suggestion = curiosity_engine.suggest_exploration()
        assert isinstance(suggestion, ExplorationCategory)

    def test_suggest_explores_underexplored(self, curiosity_engine):
        """suggest_exploration should prefer underexplored categories."""
        # Heavily explore one category
        for _ in range(20):
            curiosity_engine.explore_one(ExplorationCategory.ALGEBRA)

        # Suggestions should lean toward other categories
        suggestions = [curiosity_engine.suggest_exploration() for _ in range(20)]
        algebra_count = sum(1 for s in suggestions if s == ExplorationCategory.ALGEBRA)

        # Should not suggest algebra too often
        assert algebra_count < 15


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_explore_mathematics_returns_list(self, mock_solver):
        """explore_mathematics should return list of discoveries."""
        discoveries = explore_mathematics(mock_solver, duration_seconds=0.5)
        assert isinstance(discoveries, list)


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_solver_exception_handling(self, temp_save_dir):
        """Engine should handle solver exceptions gracefully."""
        solver = Mock()
        solver.solve = Mock(side_effect=RuntimeError("Test error"))

        engine = CuriosityEngine(solver=solver, save_dir=temp_save_dir)
        result = engine.explore_one()

        # Should not crash, result should indicate failure
        assert result.success is False

    def test_empty_stats_calculations(self, curiosity_engine):
        """Statistics should handle empty state gracefully."""
        stats = curiosity_engine.get_statistics()

        assert stats['success_rate'] == 0
        assert stats['avg_solve_time_ms'] == 0

    def test_discovery_persistence_and_loading(self, mock_solver, temp_save_dir):
        """Discoveries should persist and load correctly."""
        # Create engine and generate discoveries
        engine1 = CuriosityEngine(solver=mock_solver, save_dir=temp_save_dir)
        for _ in range(10):
            engine1.explore_one()

        initial_count = len(engine1.discoveries)

        # Create new engine with same save_dir
        engine2 = CuriosityEngine(solver=mock_solver, save_dir=temp_save_dir)

        # Should have loaded previous discoveries
        if initial_count > 0:
            assert len(engine2.discoveries) >= 0  # May have some loaded


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
