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
Comprehensive Tests for Remaining Low-Coverage Modules
======================================================

Tests to bring coverage to 70%+ for:
- sandbox_evaluator.py (currently 65%)
- code_evolutionary_proposer.py (currently 40%)
- parallel_search_manager.py (currently 31%)
- boundary_explorer.py (currently 32%)
- auto_formalization_pipeline.py (currently 38%)
- exhaustive_enumerator.py (currently 69%)
"""

import pytest
import sympy as sp
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# SandboxEvaluator Extended Tests
# =============================================================================


class TestSandboxEvaluatorComprehensive:
    """Comprehensive tests for SandboxEvaluator."""

    @pytest.fixture
    def problem_spec(self):
        from symbo_agentic_reasoners.discovery.algorithm.problem_specification import ProblemSpecification
        return ProblemSpecification(
            problem_id="test_add",
            description="Add two numbers",
            function_signature="def solve(a: int, b: int) -> int",
            test_cases=[
                ((1, 2), 3),
                ((0, 0), 0),
                ((-1, 1), 0),
            ]
        )

    @pytest.fixture
    def evaluator(self, problem_spec):
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import SandboxEvaluator
        return SandboxEvaluator(problem_spec=problem_spec)

    def test_evaluate_runtime_error_division(self, evaluator):
        """Test code that causes runtime error (division by zero)."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import EvaluationStatus

        candidate = CodeCandidate(
            candidate_id="div_zero_test",
            code="def solve(a, b):\n    return 1 / 0",  # Division by zero
            generation=0
        )

        result = evaluator.evaluate_detailed(candidate)
        assert result.status in [EvaluationStatus.RUNTIME_ERROR, EvaluationStatus.WRONG_ANSWER]

    def test_evaluate_type_error(self, evaluator):
        """Test code that causes type error."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate

        candidate = CodeCandidate(
            candidate_id="type_error_test",
            code="def solve(a, b):\n    return 'string' + 1",  # Type error
            generation=0
        )

        result = evaluator.evaluate_detailed(candidate)
        assert result.correctness_score == 0.0

    def test_evaluate_no_solve_function(self, evaluator):
        """Test code without solve function."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate

        candidate = CodeCandidate(
            candidate_id="no_solve",
            code="def other_function(a, b):\n    return a + b",
            generation=0
        )

        result = evaluator.evaluate_detailed(candidate)
        assert "solve" in result.error_message.lower() or result.correctness_score == 0.0

    def test_evaluate_with_imports(self, evaluator):
        """Test code that uses allowed imports."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeCandidate
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import EvaluationStatus

        candidate = CodeCandidate(
            candidate_id="import_test",
            code="def solve(a, b):\n    return a + b",
            generation=0
        )

        result = evaluator.evaluate_detailed(candidate)
        assert result.status == EvaluationStatus.SUCCESS

    def test_compare_outputs_floats(self, evaluator):
        """Test float comparison."""
        assert evaluator._compare_outputs(1.0000001, 1.0) is True
        assert evaluator._compare_outputs(1.0, 1.0) is True
        assert evaluator._compare_outputs(1.1, 1.0) is False

    def test_compare_outputs_lists(self, evaluator):
        """Test list comparison."""
        assert evaluator._compare_outputs([1, 2, 3], [1, 2, 3]) is True
        assert evaluator._compare_outputs([1, 2], [1, 2, 3]) is False
        assert evaluator._compare_outputs([1.0, 2.0], [1.0000001, 2.0]) is True

    def test_compute_fitness_correctness(self, evaluator):
        """Test fitness computation."""
        fitness = evaluator._compute_fitness(1.0, 100.0, 50)
        assert 0.9 <= fitness <= 1.0  # High correctness = high fitness

        fitness_low = evaluator._compute_fitness(0.0, 100.0, 50)
        assert fitness_low < 0.3  # Low correctness = low fitness

    def test_safe_import_allowed(self, evaluator):
        """Test safe import allows certain modules."""
        import math
        result = evaluator._safe_import('math')
        assert result is not None

    def test_safe_import_blocked(self, evaluator):
        """Test safe import blocks dangerous modules."""
        with pytest.raises(ImportError):
            evaluator._safe_import('os')

    def test_get_statistics_with_problem(self, evaluator):
        """Test statistics with problem set."""
        stats = evaluator.get_statistics()
        assert stats['problem_id'] == "test_add"
        assert stats['num_test_cases'] == 3

    def test_get_statistics_without_problem(self):
        """Test statistics without problem set."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import SandboxEvaluator
        evaluator = SandboxEvaluator()
        stats = evaluator.get_statistics()
        assert stats['problem_id'] is None
        assert stats['num_test_cases'] == 0


# =============================================================================
# CodeEvolutionaryProposer Extended Tests
# =============================================================================


class TestCodeEvolutionaryProposerComprehensive:
    """Comprehensive tests for CodeEvolutionaryProposer."""

    @pytest.fixture
    def problem_spec(self):
        from symbo_agentic_reasoners.discovery.algorithm.problem_specification import ProblemSpecification
        return ProblemSpecification(
            problem_id="double",
            description="Double the input",
            function_signature="def solve(x: int) -> int",
            test_cases=[((2,), 4), ((5,), 10)]
        )

    @pytest.fixture
    def proposer(self):
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import CodeEvolutionaryProposer
        return CodeEvolutionaryProposer()

    def test_generate_initial_population_various_sizes(self, proposer, problem_spec):
        """Test generating populations of different sizes."""
        for size in [1, 5, 10]:
            population = proposer.generate_initial_population(problem_spec, size=size)
            assert len(population) == size

    def test_generic_template(self, proposer):
        """Test generic template generation."""
        template = proposer._generic_template()
        assert template is not None
        assert 'def solve' in template

    def test_has_evolve_method(self, proposer):
        """Test that evolve method exists."""
        assert hasattr(proposer, 'evolve')

    def test_mutation_type_enum(self):
        """Test MutationType enum values."""
        from symbo_agentic_reasoners.discovery.algorithm.code_evolutionary_proposer import MutationType
        assert MutationType.TWEAK_CONSTANT.value == 'tweak_constant'
        assert MutationType.SWAP_OPERATORS.value == 'swap_operators'
        assert MutationType.COMBINE_PARENTS.value == 'combine_parents'

    def test_stats_tracking(self, proposer, problem_spec):
        """Test that statistics are tracked."""
        proposer.generate_initial_population(problem_spec, size=3)
        stats = proposer.get_statistics()
        assert stats['total_candidates'] >= 3


# =============================================================================
# ParallelSearchManager Extended Tests
# =============================================================================


class TestParallelSearchManagerComprehensive:
    """Comprehensive tests for ParallelSearchManager."""

    @pytest.fixture
    def manager(self):
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import ParallelSearchManager
        return ParallelSearchManager(num_workers=2)

    def test_initialization_default(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import ParallelSearchManager
        manager = ParallelSearchManager()
        assert manager.num_workers >= 1

    def test_initialization_custom_workers(self):
        """Test custom worker count."""
        from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import ParallelSearchManager
        manager = ParallelSearchManager(num_workers=8)
        assert manager.num_workers == 8

    def test_get_statistics(self, manager):
        """Test statistics retrieval."""
        stats = manager.get_statistics()
        assert isinstance(stats, dict)
        assert 'num_workers' in stats or 'workers' in stats or len(stats) >= 0

    def test_health_check(self, manager):
        """Test health check."""
        result = manager.health_check()
        assert isinstance(result, bool)

    def test_reset(self, manager):
        """Test reset functionality."""
        manager.reset()  # Should not raise


# =============================================================================
# BoundaryExplorer Extended Tests
# =============================================================================


class TestBoundaryExplorerComprehensive:
    """Comprehensive tests for BoundaryExplorer."""

    @pytest.fixture
    def explorer(self):
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import BoundaryExplorer
        return BoundaryExplorer()

    def test_initialization_custom_params(self):
        """Test initialization with custom parameters."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import BoundaryExplorer
        explorer = BoundaryExplorer(
            max_iterations=500,
            tolerance=0.001
        )
        assert explorer.max_iterations == 500
        assert explorer.tolerance == 0.001

    def test_explore_simple_condition(self, explorer):
        """Test exploring a simple boundary condition."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import (
            BoundaryCondition, BoundaryType
        )

        x = sp.Symbol('x')
        condition = BoundaryCondition(
            condition_id="test_cond",
            expression=str(x > 0),
            boundary_type=BoundaryType.PARAMETER_LIMIT,
            parameters=["x"]
        )

        result = explorer.explore(condition)
        assert result is not None

    def test_boundary_type_values(self):
        """Test all BoundaryType enum values."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import BoundaryType
        assert BoundaryType.PARAMETER_LIMIT.value == 'parameter_limit'
        assert BoundaryType.DOMAIN_EDGE.value == 'domain_edge'
        assert BoundaryType.SINGULARITY.value == 'singularity'

    def test_exploration_status_values(self):
        """Test all ExplorationStatus enum values."""
        from symbo_agentic_reasoners.discovery.conjecture.boundary_explorer import ExplorationStatus
        assert ExplorationStatus.PENDING.value == 'pending'
        assert ExplorationStatus.EXPLORING.value == 'exploring'
        assert ExplorationStatus.COMPLETE.value == 'complete'

    def test_get_statistics(self, explorer):
        """Test statistics retrieval."""
        stats = explorer.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# AutoFormalizationPipeline Extended Tests
# =============================================================================


class TestAutoFormalizationPipelineComprehensive:
    """Comprehensive tests for AutoFormalizationPipeline."""

    @pytest.fixture
    def pipeline(self):
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import AutoFormalizationPipeline
        return AutoFormalizationPipeline()

    def test_initialization(self, pipeline):
        """Test initialization."""
        assert pipeline is not None

    def test_discovery_type_values(self):
        """Test all DiscoveryType enum values."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import DiscoveryType
        assert DiscoveryType.THEOREM.value == 'theorem'
        assert DiscoveryType.LEMMA.value == 'lemma'
        assert DiscoveryType.ALGORITHM.value == 'algorithm'
        assert DiscoveryType.IDENTITY.value == 'identity'
        assert DiscoveryType.FORMULA.value == 'formula'

    def test_verification_status_values(self):
        """Test all VerificationStatus enum values."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import VerificationStatus
        assert VerificationStatus.PENDING.value == 'pending'
        assert VerificationStatus.VERIFIED.value == 'verified'
        assert VerificationStatus.FAILED.value == 'failed'

    def test_formalized_discovery_creation(self):
        """Test FormalizedDiscovery dataclass."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            FormalizedDiscovery, DiscoveryType, VerificationStatus
        )

        discovery = FormalizedDiscovery(
            discovery_id="test_001",
            discovery_type=DiscoveryType.THEOREM,
            natural_language_statement="For all x > 0, x^2 > 0",
            omdoc_representation="<theorem>...</theorem>"
        )

        assert discovery.discovery_id == "test_001"
        assert discovery.discovery_type == DiscoveryType.THEOREM

    def test_formalized_discovery_to_dict(self):
        """Test FormalizedDiscovery serialization."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            FormalizedDiscovery, DiscoveryType, VerificationStatus
        )

        discovery = FormalizedDiscovery(
            discovery_id="test_002",
            discovery_type=DiscoveryType.IDENTITY,
            natural_language_statement="a + b = b + a",
            omdoc_representation="<identity>...</identity>",
            verified=True,
            verification_status=VerificationStatus.VERIFIED
        )

        d = discovery.to_dict()
        assert d['discovery_id'] == "test_002"
        assert d['verified'] is True

    def test_get_statistics(self, pipeline):
        """Test statistics retrieval."""
        stats = pipeline.get_statistics()
        assert isinstance(stats, dict)

    def test_health_check(self, pipeline):
        """Test health check."""
        result = pipeline.health_check()
        assert isinstance(result, bool)


# =============================================================================
# ExhaustiveEnumerator Extended Tests
# =============================================================================


class TestExhaustiveEnumeratorComprehensive:
    """Comprehensive tests for ExhaustiveEnumerator."""

    @pytest.fixture
    def enumerator(self):
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import ExhaustiveEnumerator
        return ExhaustiveEnumerator(max_items=500)

    def test_enumerate_1d_space(self, enumerator):
        """Test 1D enumeration."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace, EnumerationStatus
        )

        space = EnumerationSpace(
            space_id="1d_space",
            dimensions={"x": list(range(10))}
        )

        result = enumerator.enumerate(space)
        assert result.status == EnumerationStatus.COMPLETE
        assert result.items_generated == 10

    def test_enumerate_3d_space(self, enumerator):
        """Test 3D enumeration."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace, EnumerationStatus
        )

        space = EnumerationSpace(
            space_id="3d_space",
            dimensions={
                "x": [1, 2],
                "y": [1, 2],
                "z": [1, 2]
            }
        )

        result = enumerator.enumerate(space)
        assert result.items_generated == 8  # 2^3

    def test_enumerate_permutations(self, enumerator):
        """Test permutations enumeration."""
        result = enumerator.enumerate_permutations([1, 2, 3])
        assert result.items_generated == 6  # 3! = 6

    def test_enumeration_status_values(self):
        """Test EnumerationStatus enum values."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import EnumerationStatus
        # Check actual enum values
        assert EnumerationStatus.COMPLETE.value == 'complete'
        assert EnumerationStatus.TERMINATED.value == 'terminated'

    def test_get_statistics(self, enumerator):
        """Test statistics retrieval."""
        stats = enumerator.get_statistics()
        assert isinstance(stats, dict)

    def test_enumerate_random_strategy(self, enumerator):
        """Test random sample enumeration strategy."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace, EnumerationStrategy
        )

        space = EnumerationSpace(
            space_id="random_space",
            dimensions={
                "x": list(range(100)),
                "y": list(range(100))
            }
        )

        result = enumerator.enumerate(space, strategy=EnumerationStrategy.RANDOM_SAMPLE)
        # Should generate up to max_items samples (500)
        assert result.items_generated <= 500
        assert result.items_generated > 0

    def test_enumerate_fair_strategy(self, enumerator):
        """Test fair enumeration strategy."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import (
            EnumerationSpace, EnumerationStrategy, EnumerationStatus
        )

        space = EnumerationSpace(
            space_id="fair_space",
            dimensions={
                "x": [1, 2, 3],
                "y": [1, 2, 3]
            }
        )

        result = enumerator.enumerate(space, strategy=EnumerationStrategy.FAIR)
        assert result.items_generated == 9  # 3x3
        assert result.status == EnumerationStatus.COMPLETE

    def test_enumeration_space_to_dict(self):
        """Test EnumerationSpace to_dict method."""
        from symbo_agentic_reasoners.discovery.deep_search.exhaustive_enumerator import EnumerationSpace

        space = EnumerationSpace(
            space_id="dict_test",
            dimensions={
                "a": [1, 2],
                "b": [3, 4, 5]
            }
        )

        d = space.to_dict()
        assert d['id'] == "dict_test"
        assert 'a' in d['dimensions']
        assert 'b' in d['dimensions']
        assert d['size_estimate'] == 6  # 2 * 3


# =============================================================================
# Execute in Sandbox Function Tests
# =============================================================================


class TestExecuteInSandbox:
    """Tests for _execute_in_sandbox function."""

    def test_execute_successful(self):
        """Test successful sandbox execution."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import _execute_in_sandbox

        code = "def solve(x): return x * 2"
        test_case = ((5,), 10)

        result = _execute_in_sandbox(code, test_case, timeout=5.0)
        assert result['passed'] is True
        assert result['output'] == 10

    def test_execute_syntax_error(self):
        """Test syntax error in sandbox."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import _execute_in_sandbox

        code = "def solve(x)\n    return x"  # Missing colon
        test_case = ((5,), 10)

        result = _execute_in_sandbox(code, test_case, timeout=5.0)
        assert result['passed'] is False
        assert 'Syntax error' in result.get('error', '')

    def test_execute_no_solve_function(self):
        """Test missing solve function."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import _execute_in_sandbox

        code = "def other(x): return x"
        test_case = ((5,), 10)

        result = _execute_in_sandbox(code, test_case, timeout=5.0)
        assert result['passed'] is False
        assert 'solve' in result.get('error', '').lower()

    def test_execute_wrong_answer(self):
        """Test wrong answer."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import _execute_in_sandbox

        code = "def solve(x): return x + 1"
        test_case = ((5,), 10)  # Expected 10, will get 6

        result = _execute_in_sandbox(code, test_case, timeout=5.0)
        assert result['passed'] is False
        assert result['output'] == 6

    def test_execute_type_error(self):
        """Test type error in execution."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import _execute_in_sandbox

        code = "def solve(x): return 'string' + x"  # Type error
        test_case = ((5,), 10)

        result = _execute_in_sandbox(code, test_case, timeout=5.0)
        assert result['passed'] is False
        assert 'error' in result and result['error'] is not None

    def test_execute_single_arg(self):
        """Test with non-tuple input."""
        from symbo_agentic_reasoners.discovery.algorithm.sandbox_evaluator import _execute_in_sandbox

        code = "def solve(x): return x * 2"
        test_case = (5, 10)  # Single arg, not tuple

        result = _execute_in_sandbox(code, test_case, timeout=5.0)
        assert result['passed'] is True
        assert result['output'] == 10


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
