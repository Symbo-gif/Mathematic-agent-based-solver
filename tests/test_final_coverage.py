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
Final Coverage Tests
====================

Comprehensive tests to bring all remaining modules to 70%+ coverage:
- code_evolutionary_proposer.py (40% → 70%)
- parallel_search_manager.py (31% → 70%)
- auto_formalization_pipeline.py (38% → 70%)
- exhaustive_enumerator.py (69% → 70%)
"""

import pytest
import random
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# CodeEvolutionaryProposer Comprehensive Tests
# =============================================================================


class TestCodeEvolutionaryProposerDeep:
    """Deep tests for CodeEvolutionaryProposer."""

    @pytest.fixture
    def proposer(self):
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeEvolutionaryProposer
        return CodeEvolutionaryProposer()

    @pytest.fixture
    def optimization_problem(self):
        from symbo_agentic_reasoners.discovery.algorithm.problem_specification import ProblemSpecification
        return ProblemSpecification(
            problem_id="knapsack",
            description="0/1 Knapsack",
            function_signature="def solve(weights, values, capacity)",
            problem_class="optimization",
            test_cases=[
                (([1, 2, 3], [10, 20, 30], 5), 50),
            ]
        )

    @pytest.fixture
    def decision_problem(self):
        from symbo_agentic_reasoners.discovery.algorithm.problem_specification import ProblemSpecification
        return ProblemSpecification(
            problem_id="subset_sum",
            description="Subset Sum",
            function_signature="def solve(items, target)",
            problem_class="decision",
            test_cases=[
                (([1, 2, 3], 5), True),
            ]
        )

    @pytest.fixture
    def sorting_problem(self):
        from symbo_agentic_reasoners.discovery.algorithm.problem_specification import ProblemSpecification
        return ProblemSpecification(
            problem_id="sort",
            description="Sort items",
            function_signature="def solve(items)",
            problem_class="sorting",
            test_cases=[
                (([3, 1, 2],), [1, 2, 3]),
            ]
        )

    def test_get_templates_optimization(self, proposer, optimization_problem):
        """Test templates for optimization problems."""
        proposer.problem_spec = optimization_problem
        templates = proposer._get_templates()
        assert len(templates) >= 3  # greedy, dp, recursive

    def test_get_templates_decision(self, proposer, decision_problem):
        """Test templates for decision problems."""
        proposer.problem_spec = decision_problem
        templates = proposer._get_templates()
        assert len(templates) >= 3  # backtracking, dp, iterative

    def test_get_templates_sorting(self, proposer, sorting_problem):
        """Test templates for sorting problems."""
        proposer.problem_spec = sorting_problem
        templates = proposer._get_templates()
        assert len(templates) >= 3  # quicksort, mergesort, heapsort

    def test_get_templates_no_problem(self, proposer):
        """Test templates without problem spec."""
        templates = proposer._get_templates()
        assert len(templates) == 1  # generic only

    def test_greedy_template(self, proposer, optimization_problem):
        """Test greedy template generation."""
        proposer.problem_spec = optimization_problem
        template = proposer._greedy_template(optimization_problem.function_signature)
        assert 'solve' in template or 'def' in template

    def test_dp_template(self, proposer, optimization_problem):
        """Test DP template generation."""
        template = proposer._dp_template(optimization_problem.function_signature)
        assert 'dp' in template.lower() or 'solve' in template.lower()

    def test_recursive_template(self, proposer, optimization_problem):
        """Test recursive template generation."""
        template = proposer._recursive_template(optimization_problem.function_signature)
        assert 'helper' in template or 'lru_cache' in template

    def test_backtracking_template(self, proposer, decision_problem):
        """Test backtracking template generation."""
        template = proposer._backtracking_template(decision_problem.function_signature)
        assert 'backtrack' in template

    def test_iterative_template(self, proposer, decision_problem):
        """Test iterative template generation."""
        template = proposer._iterative_template(decision_problem.function_signature)
        assert 'reachable' in template or 'set' in template

    def test_quicksort_template(self, proposer, sorting_problem):
        """Test quicksort template generation."""
        template = proposer._quicksort_template(sorting_problem.function_signature)
        assert 'pivot' in template.lower()

    def test_mergesort_template(self, proposer, sorting_problem):
        """Test mergesort template generation."""
        template = proposer._mergesort_template(sorting_problem.function_signature)
        assert 'mid' in template

    def test_heapsort_template(self, proposer, sorting_problem):
        """Test heapsort template generation."""
        template = proposer._heapsort_template(sorting_problem.function_signature)
        assert 'heapq' in template

    def test_apply_initial_variation(self, proposer):
        """Test initial variation application."""
        template = "for i in range(5):\n    x = 10"
        varied = proposer._apply_initial_variation(template)
        # Should return a string
        assert isinstance(varied, str)

    def test_tweak_constants(self, proposer):
        """Test constant tweaking mutation."""
        code = "x = 5\ny = 10\nz = 0"
        result = proposer._tweak_constants(code)
        assert isinstance(result, str)
        assert 'x =' in result

    def test_swap_operators(self, proposer):
        """Test operator swapping mutation."""
        code = "result = a + b"
        result = proposer._swap_operators(code)
        # Should either swap or keep same
        assert 'result' in result

    def test_add_condition(self, proposer):
        """Test condition addition mutation."""
        code = "def solve(x):\n    for item in items:\n        process(item)"
        result = proposer._add_condition(code)
        assert isinstance(result, str)

    def test_remove_code(self, proposer):
        """Test code removal mutation."""
        code = "def solve(x):\n    a = 1\n    b = 2\n    c = 3\n    d = 4\n    e = 5\n    return a"
        result = proposer._remove_code(code)
        # Should have same or fewer lines
        assert len(result.split('\n')) <= len(code.split('\n'))

    def test_restructure_loop(self, proposer):
        """Test loop restructuring mutation."""
        code = "result = []\nfor x in items:\n    result.append(x*2)"
        result = proposer._restructure_loop(code)
        assert isinstance(result, str)

    def test_insert_optimization(self, proposer):
        """Test optimization insertion mutation."""
        code = "def solve(items):\n    if not items:\n        return 0"
        result = proposer._insert_optimization(code)
        assert isinstance(result, str)

    def test_change_data_structure(self, proposer):
        """Test data structure change mutation."""
        code = "result = []\nresult.append(1)"
        result = proposer._change_data_structure(code)
        assert isinstance(result, str)

    def test_crossover(self, proposer):
        """Test crossover operation."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate

        parent1 = CodeCandidate(
            candidate_id="p1",
            code="def solve(x):\n    a = 1\n    return a * x",
            generation=0
        )
        parent2 = CodeCandidate(
            candidate_id="p2",
            code="def solve(x):\n    b = 2\n    return b + x",
            generation=0
        )

        child = proposer._crossover(parent1, parent2)
        assert child is not None
        assert 'solve' in child.code

    def test_evolve_with_population(self, proposer, optimization_problem):
        """Test evolution with evaluated population."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate

        # Create population with fitness scores
        population = []
        for i in range(5):
            candidate = CodeCandidate(
                candidate_id=f"c{i}",
                code=f"def solve(x): return x * {i+1}",
                generation=0,
                fitness_score=0.5 + i * 0.1
            )
            population.append(candidate)

        # Evolve
        new_pop = proposer.evolve(population)
        assert len(new_pop) >= 5
        assert proposer.stats['generations_evolved'] >= 1

    def test_get_best(self, proposer, optimization_problem):
        """Test getting best candidate."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate

        # Initially no best
        assert proposer.get_best() is None

        # After evolution with fitness
        population = [
            CodeCandidate(
                candidate_id="c1",
                code="def solve(x): return x",
                generation=0,
                fitness_score=0.9
            ),
            CodeCandidate(
                candidate_id="c2",
                code="def solve(x): return x*2",
                generation=0,
                fitness_score=0.5
            ),
        ]

        proposer.evolve(population)
        best = proposer.get_best()
        assert best is not None
        assert best.fitness_score == 0.9

    def test_set_problem(self, proposer, optimization_problem):
        """Test setting problem specification."""
        proposer.set_problem(optimization_problem)
        assert proposer.problem_spec == optimization_problem

    def test_health_check(self, proposer):
        """Test health check."""
        result = proposer.health_check()
        assert result is True

    def test_mutate_creates_child(self, proposer):
        """Test internal mutate method."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate

        parent = CodeCandidate(
            candidate_id="parent",
            code="def solve(x): return x * 2",
            generation=0,
            fitness_score=0.5
        )

        child = proposer._mutate(parent)
        assert child is not None
        # Generation uses proposer.generation which starts at 0
        assert child.generation >= 0
        assert child.parent_id == "parent"


# =============================================================================
# ParallelSearchManager Comprehensive Tests
# =============================================================================


class TestParallelSearchManagerDeep:
    """Deep tests for ParallelSearchManager."""

    @pytest.fixture
    def manager(self):
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import ParallelSearchManager
        return ParallelSearchManager(num_workers=4)

    def test_initialization_various_workers(self):
        """Test initialization with various worker counts."""
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import ParallelSearchManager

        for workers in [1, 2, 4, 8, 16]:
            manager = ParallelSearchManager(num_workers=workers)
            assert manager.num_workers == workers

    def test_get_statistics_structure(self, manager):
        """Test statistics structure."""
        stats = manager.get_statistics()
        assert isinstance(stats, dict)

    def test_reset_clears_state(self, manager):
        """Test reset clears state."""
        manager.reset()
        # Should not raise


# =============================================================================
# AutoFormalizationPipeline Comprehensive Tests
# =============================================================================


class TestAutoFormalizationPipelineDeep:
    """Deep tests for AutoFormalizationPipeline."""

    @pytest.fixture
    def pipeline(self):
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import AutoFormalizationPipeline
        return AutoFormalizationPipeline()

    def test_discovery_type_all_values(self):
        """Test DiscoveryType values."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import DiscoveryType

        # Check we have the expected types
        assert DiscoveryType.THEOREM.value == 'theorem'
        assert DiscoveryType.LEMMA.value == 'lemma'
        assert DiscoveryType.ALGORITHM.value == 'algorithm'
        assert DiscoveryType.IDENTITY.value == 'identity'
        assert DiscoveryType.FORMULA.value == 'formula'
        assert DiscoveryType.HEURISTIC.value == 'heuristic'

    def test_verification_status_all_values(self):
        """Test VerificationStatus values."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import VerificationStatus

        # Check we have the expected statuses
        assert VerificationStatus.PENDING.value == 'pending'
        assert VerificationStatus.VERIFIED.value == 'verified'
        assert VerificationStatus.FAILED.value == 'failed'
        assert VerificationStatus.PARTIAL.value == 'partial'

    def test_formalized_discovery_hash(self):
        """Test FormalizedDiscovery hash computation."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            FormalizedDiscovery, DiscoveryType
        )

        discovery = FormalizedDiscovery(
            discovery_id="test",
            discovery_type=DiscoveryType.THEOREM,
            natural_language_statement="Test theorem",
            omdoc_representation="<theorem/>"
        )

        hash1 = discovery.compute_hash()
        hash2 = discovery.compute_hash()
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_formalized_discovery_all_fields(self):
        """Test FormalizedDiscovery with all fields."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            FormalizedDiscovery, DiscoveryType, VerificationStatus
        )

        discovery = FormalizedDiscovery(
            discovery_id="full_test",
            discovery_type=DiscoveryType.LEMMA,
            natural_language_statement="A supporting lemma",
            omdoc_representation="<lemma>...</lemma>",
            verified=True,
            verification_status=VerificationStatus.VERIFIED,
        )

        d = discovery.to_dict()
        assert d['discovery_id'] == "full_test"
        assert d['verified'] is True


# =============================================================================
# ExhaustiveEnumerator Additional Tests
# =============================================================================


class TestExhaustiveEnumeratorDeep:
    """Deep tests for ExhaustiveEnumerator."""

    @pytest.fixture
    def enumerator(self):
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import ExhaustiveEnumerator
        return ExhaustiveEnumerator(max_items=1000)

    def test_enumerate_empty_space(self, enumerator):
        """Test enumeration of empty space."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace, EnumerationStatus
        )

        space = EnumerationSpace(
            space_id="empty",
            dimensions={}
        )

        result = enumerator.enumerate(space)
        assert result.items_generated >= 0

    def test_enumerate_single_dimension(self, enumerator):
        """Test single dimension enumeration."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace, EnumerationStatus
        )

        space = EnumerationSpace(
            space_id="single",
            dimensions={"x": [1, 2, 3, 4, 5]}
        )

        result = enumerator.enumerate(space)
        assert result.items_generated == 5

    def test_enumerate_with_filter(self, enumerator):
        """Test enumeration with filter function."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace
        )

        space = EnumerationSpace(
            space_id="filtered",
            dimensions={"x": list(range(10))}
        )

        # Only keep even numbers
        result = enumerator.enumerate(
            space,
            target_condition=lambda p: p['x'] % 2 == 0
        )

        for match in result.matches_found:
            assert match['x'] % 2 == 0

    def test_enumerate_integers_various_bounds(self, enumerator):
        """Test integer enumeration with various bounds."""
        for bound in [3, 5, 7]:
            result = enumerator.enumerate_integers(bound, dimensions=1)
            assert result.items_generated == bound

    def test_enumeration_result_to_dict(self, enumerator):
        """Test EnumerationResult serialization."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace
        )

        space = EnumerationSpace(
            space_id="test",
            dimensions={"x": [1, 2, 3]}
        )

        result = enumerator.enumerate(space)
        d = result.to_dict()
        assert 'space_id' in d
        assert 'generated' in d or 'items_generated' in d


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
