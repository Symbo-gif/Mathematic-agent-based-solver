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
Theorem Library Manager Tests
=============================

Comprehensive tests for the TheoremLibraryManager agent:
- Initialization and configuration
- Theorem lookup
- Applicability checking
- Proof sketch generation
- BDI interface
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.middleware.theorem_library import (
    TheoremLibraryManager,
    MathDomain,
    ProofTechnique,
    Theorem,
    ProofSketch,
    ApplicabilityResult,
)
from symbo_agentic_reasoners.core.blackboard import Blackboard
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def manager():
    """Create a TheoremLibraryManager instance."""
    return TheoremLibraryManager()


@pytest.fixture
def manager_with_infrastructure():
    """Create manager with blackboard and DF."""
    bb = Blackboard()
    df = DirectoryFacilitator()
    return TheoremLibraryManager(blackboard=bb, df=df)


# =============================================================================
# MathDomain Enum Tests
# =============================================================================


class TestMathDomain:
    """Tests for MathDomain enum."""

    def test_math_domains_exist(self):
        """MathDomain should have expected values."""
        assert hasattr(MathDomain, 'ALGEBRA')
        assert hasattr(MathDomain, 'CALCULUS')
        assert hasattr(MathDomain, 'LINEAR_ALGEBRA')
        assert hasattr(MathDomain, 'NUMBER_THEORY')
        assert hasattr(MathDomain, 'TOPOLOGY')
        assert hasattr(MathDomain, 'ANALYSIS')
        assert hasattr(MathDomain, 'COMBINATORICS')
        assert hasattr(MathDomain, 'GEOMETRY')
        assert hasattr(MathDomain, 'LOGIC')
        assert hasattr(MathDomain, 'SET_THEORY')
        assert hasattr(MathDomain, 'GENERAL')

    def test_domain_values(self):
        """MathDomain values should be strings."""
        assert MathDomain.ALGEBRA.value == "algebra"
        assert MathDomain.CALCULUS.value == "calculus"
        assert MathDomain.LINEAR_ALGEBRA.value == "linear_algebra"


# =============================================================================
# ProofTechnique Enum Tests
# =============================================================================


class TestProofTechnique:
    """Tests for ProofTechnique enum."""

    def test_techniques_exist(self):
        """ProofTechnique should have expected values."""
        assert hasattr(ProofTechnique, 'DIRECT')
        assert hasattr(ProofTechnique, 'CONTRADICTION')
        assert hasattr(ProofTechnique, 'INDUCTION')
        assert hasattr(ProofTechnique, 'CONTRAPOSITIVE')
        assert hasattr(ProofTechnique, 'CONSTRUCTION')
        assert hasattr(ProofTechnique, 'EXHAUSTION')
        assert hasattr(ProofTechnique, 'PIGEONHOLE')
        assert hasattr(ProofTechnique, 'DIAGONAL')

    def test_technique_values(self):
        """ProofTechnique values should be strings."""
        assert ProofTechnique.DIRECT.value == "direct"
        assert ProofTechnique.CONTRADICTION.value == "contradiction"
        assert ProofTechnique.INDUCTION.value == "induction"


# =============================================================================
# Theorem Tests
# =============================================================================


class TestTheorem:
    """Tests for Theorem dataclass."""

    def test_create_theorem(self):
        """Should create a theorem with required fields."""
        theorem = Theorem(
            theorem_id="test_thm",
            name="Test Theorem",
            statement="For all x, P(x) holds",
            domain=MathDomain.ALGEBRA,
            hypotheses=["x is real"],
            conclusion="P(x)"
        )

        assert theorem.theorem_id == "test_thm"
        assert theorem.name == "Test Theorem"
        assert theorem.domain == MathDomain.ALGEBRA
        assert len(theorem.hypotheses) == 1

    def test_theorem_defaults(self):
        """Should have sensible defaults."""
        theorem = Theorem(
            theorem_id="test",
            name="Test",
            statement="test",
            domain=MathDomain.GENERAL,
            hypotheses=[],
            conclusion="test"
        )

        assert theorem.proof_technique == ProofTechnique.DIRECT
        assert theorem.dependencies == []
        assert theorem.applications == []
        assert theorem.difficulty == 5

    def test_theorem_to_dict(self):
        """to_dict should return dictionary."""
        theorem = Theorem(
            theorem_id="test",
            name="Test Theorem",
            statement="This is a test statement",
            domain=MathDomain.CALCULUS,
            hypotheses=["h1", "h2"],
            conclusion="conclusion",
            proof_technique=ProofTechnique.INDUCTION,
            difficulty=7
        )

        d = theorem.to_dict()

        assert d['theorem_id'] == "test"
        assert d['name'] == "Test Theorem"
        assert d['domain'] == "calculus"
        assert d['technique'] == "induction"
        assert d['difficulty'] == 7


# =============================================================================
# ProofSketch Tests
# =============================================================================


class TestProofSketch:
    """Tests for ProofSketch dataclass."""

    def test_create_proof_sketch(self):
        """Should create a proof sketch."""
        sketch = ProofSketch(
            theorem_id="test",
            steps=["Step 1", "Step 2", "Step 3"],
            technique=ProofTechnique.DIRECT,
            key_lemmas=["Lemma 1"],
            estimated_difficulty=5
        )

        assert sketch.theorem_id == "test"
        assert len(sketch.steps) == 3
        assert sketch.technique == ProofTechnique.DIRECT
        assert sketch.estimated_difficulty == 5

    def test_proof_sketch_to_dict(self):
        """to_dict should return dictionary."""
        sketch = ProofSketch(
            theorem_id="test",
            steps=["Step 1", "Step 2"],
            technique=ProofTechnique.CONTRADICTION,
            key_lemmas=[],
            estimated_difficulty=6
        )

        d = sketch.to_dict()

        assert d['theorem_id'] == "test"
        assert d['step_count'] == 2
        assert d['technique'] == "contradiction"
        assert d['difficulty'] == 6


# =============================================================================
# ApplicabilityResult Tests
# =============================================================================


class TestApplicabilityResult:
    """Tests for ApplicabilityResult dataclass."""

    def test_create_applicability_result(self):
        """Should create applicability result."""
        theorem = Theorem(
            theorem_id="test",
            name="Test",
            statement="test",
            domain=MathDomain.ALGEBRA,
            hypotheses=["h1"],
            conclusion="c"
        )

        result = ApplicabilityResult(
            theorem=theorem,
            is_applicable=True,
            satisfaction_level=0.9,
            missing_hypotheses=[],
            matching_conditions=["h1"]
        )

        assert result.is_applicable is True
        assert result.satisfaction_level == 0.9

    def test_applicability_to_dict(self):
        """to_dict should return dictionary."""
        theorem = Theorem(
            theorem_id="test",
            name="Test",
            statement="test",
            domain=MathDomain.ALGEBRA,
            hypotheses=["h1"],
            conclusion="c"
        )

        result = ApplicabilityResult(
            theorem=theorem,
            is_applicable=False,
            satisfaction_level=0.3,
            missing_hypotheses=["h1"],
            matching_conditions=[]
        )

        d = result.to_dict()

        assert d['theorem_id'] == "test"
        assert d['is_applicable'] is False
        assert d['satisfaction'] == 0.3
        assert d['missing'] == ["h1"]


# =============================================================================
# TheoremLibraryManager Initialization Tests
# =============================================================================


class TestTheoremLibraryManagerInitialization:
    """Tests for TheoremLibraryManager initialization."""

    def test_basic_initialization(self, manager):
        """Should initialize with defaults."""
        assert manager is not None
        assert manager.agent_id == 'theorem_library_001'

    def test_custom_agent_id(self):
        """Should accept custom agent ID."""
        manager = TheoremLibraryManager(agent_id='custom_manager')
        assert manager.agent_id == 'custom_manager'

    def test_initialization_with_blackboard(self):
        """Should initialize with blackboard."""
        bb = Blackboard()
        manager = TheoremLibraryManager(blackboard=bb)
        assert manager.blackboard is bb

    def test_initialization_with_df(self):
        """Should initialize with directory facilitator."""
        df = DirectoryFacilitator()
        manager = TheoremLibraryManager(df=df)
        assert manager.df is df

    def test_foundational_theorems_initialized(self, manager):
        """Should initialize with foundational theorems."""
        assert len(manager.theorems) > 0

        # Check for known theorems
        assert 'fundamental_algebra' in manager.theorems
        assert 'fundamental_calculus' in manager.theorems
        assert 'mean_value_theorem' in manager.theorems
        assert 'quadratic_formula' in manager.theorems

    def test_domain_index_initialized(self, manager):
        """Should initialize domain index."""
        assert len(manager.domain_index) > 0
        assert MathDomain.CALCULUS in manager.domain_index
        assert len(manager.domain_index[MathDomain.CALCULUS]) > 0


# =============================================================================
# Add Theorem Tests
# =============================================================================


class TestAddTheorem:
    """Tests for adding theorems."""

    def test_add_theorem(self, manager):
        """Should add a theorem to the library."""
        theorem = Theorem(
            theorem_id="custom_theorem",
            name="Custom Theorem",
            statement="Custom statement",
            domain=MathDomain.ALGEBRA,
            hypotheses=["h1"],
            conclusion="c",
            keywords={"custom", "test"}
        )

        tid = manager.add_theorem(theorem)

        assert tid == "custom_theorem"
        assert "custom_theorem" in manager.theorems

    def test_add_theorem_updates_domain_index(self, manager):
        """Adding theorem should update domain index."""
        initial_count = len(manager.domain_index[MathDomain.GEOMETRY])

        theorem = Theorem(
            theorem_id="geometry_test",
            name="Geometry Theorem",
            statement="test",
            domain=MathDomain.GEOMETRY,
            hypotheses=[],
            conclusion="c"
        )

        manager.add_theorem(theorem)

        assert len(manager.domain_index[MathDomain.GEOMETRY]) == initial_count + 1

    def test_add_theorem_updates_keyword_index(self, manager):
        """Adding theorem should update keyword index."""
        theorem = Theorem(
            theorem_id="keyword_test",
            name="Keyword Test",
            statement="test",
            domain=MathDomain.ALGEBRA,
            hypotheses=[],
            conclusion="c",
            keywords={"unique_keyword", "another"}
        )

        manager.add_theorem(theorem)

        assert "unique_keyword" in manager.keyword_index
        assert "keyword_test" in manager.keyword_index["unique_keyword"]

    def test_add_theorem_updates_dependency_graph(self, manager):
        """Adding theorem should update dependency graph."""
        theorem = Theorem(
            theorem_id="dep_test",
            name="Dependency Test",
            statement="test",
            domain=MathDomain.CALCULUS,
            hypotheses=[],
            conclusion="c",
            dependencies=["fundamental_calculus"]
        )

        manager.add_theorem(theorem)

        assert "dep_test" in manager.dependency_graph
        assert "fundamental_calculus" in manager.dependency_graph["dep_test"]


# =============================================================================
# Theorem Lookup Tests
# =============================================================================


class TestTheoremLookup:
    """Tests for theorem lookup."""

    def test_lookup_all(self, manager):
        """Should return all theorems without filters."""
        theorems = manager.lookup_theorems()

        assert isinstance(theorems, list)
        assert len(theorems) > 0

    def test_lookup_by_domain(self, manager):
        """Should filter by domain."""
        theorems = manager.lookup_theorems(domain=MathDomain.CALCULUS)

        for theorem in theorems:
            assert theorem.domain == MathDomain.CALCULUS

    def test_lookup_by_query(self, manager):
        """Should filter by query text."""
        theorems = manager.lookup_theorems(query="derivative")

        assert len(theorems) > 0
        # Results should contain query term somewhere
        for t in theorems:
            text = (t.name + t.statement + " ".join(t.hypotheses)).lower()
            assert "derivative" in text

    def test_lookup_by_keywords(self, manager):
        """Should filter by keywords."""
        theorems = manager.lookup_theorems(keywords=["fundamental"])

        assert len(theorems) > 0

    def test_lookup_with_max_results(self, manager):
        """Should respect max_results parameter."""
        theorems = manager.lookup_theorems(max_results=2)

        assert len(theorems) <= 2

    def test_lookup_combined_filters(self, manager):
        """Should combine multiple filters."""
        theorems = manager.lookup_theorems(
            domain=MathDomain.CALCULUS,
            query="derivative"
        )

        for theorem in theorems:
            assert theorem.domain == MathDomain.CALCULUS

    def test_lookup_increments_counter(self, manager):
        """Should increment lookups_performed counter."""
        initial = manager.lookups_performed

        manager.lookup_theorems()

        assert manager.lookups_performed == initial + 1


# =============================================================================
# Applicability Check Tests
# =============================================================================


class TestApplicabilityCheck:
    """Tests for applicability checking."""

    def test_check_applicability_fully_satisfied(self, manager):
        """Should report high satisfaction when all hypotheses met."""
        # Use exact hypothesis text from the theorem
        result = manager.check_applicability(
            "mean_value_theorem",
            ["f continuous on [a,b]", "f differentiable on (a,b)"]
        )

        assert result.satisfaction_level >= 0.5
        assert result.is_applicable is True

    def test_check_applicability_partially_satisfied(self, manager):
        """Should report partial satisfaction."""
        result = manager.check_applicability(
            "mean_value_theorem",
            ["f is continuous"]  # Only partial match
        )

        assert isinstance(result, ApplicabilityResult)
        assert 0 <= result.satisfaction_level <= 1

    def test_check_applicability_not_satisfied(self, manager):
        """Should report low satisfaction when hypotheses not met."""
        result = manager.check_applicability(
            "mean_value_theorem",
            ["completely unrelated condition"]
        )

        # Should have missing hypotheses
        assert len(result.missing_hypotheses) > 0

    def test_check_applicability_unknown_theorem(self, manager):
        """Should raise error for unknown theorem."""
        with pytest.raises(ValueError):
            manager.check_applicability(
                "nonexistent_theorem",
                ["some condition"]
            )

    def test_check_applicability_empty_conditions(self, manager):
        """Should handle empty conditions."""
        result = manager.check_applicability(
            "quadratic_formula",
            []
        )

        assert isinstance(result, ApplicabilityResult)
        # Should have all hypotheses missing
        assert len(result.missing_hypotheses) > 0


# =============================================================================
# Proof Sketch Generation Tests
# =============================================================================


class TestProofSketchGeneration:
    """Tests for proof sketch generation."""

    def test_generate_proof_sketch(self, manager):
        """Should generate proof sketch."""
        sketch = manager.generate_proof_sketch("rolle_theorem")

        assert isinstance(sketch, ProofSketch)
        assert sketch.theorem_id == "rolle_theorem"
        assert len(sketch.steps) > 0

    def test_proof_sketch_technique(self, manager):
        """Sketch should reflect theorem's proof technique."""
        sketch = manager.generate_proof_sketch("rolle_theorem")

        # Rolle's theorem uses contradiction
        assert sketch.technique == ProofTechnique.CONTRADICTION

    def test_proof_sketch_induction(self, manager):
        """Should generate induction-style steps."""
        # Fundamental theorem of arithmetic uses induction
        sketch = manager.generate_proof_sketch("fundamental_arithmetic")

        assert sketch.technique == ProofTechnique.INDUCTION
        # Should mention base case
        assert any("base case" in step.lower() for step in sketch.steps)

    def test_proof_sketch_unknown_theorem(self, manager):
        """Should raise error for unknown theorem."""
        with pytest.raises(ValueError):
            manager.generate_proof_sketch("nonexistent_theorem")

    def test_proof_sketch_increments_counter(self, manager):
        """Should increment proofs_sketched counter."""
        initial = manager.proofs_sketched

        manager.generate_proof_sketch("quadratic_formula")

        assert manager.proofs_sketched == initial + 1


# =============================================================================
# Dependency Graph Tests
# =============================================================================


class TestDependencyGraph:
    """Tests for dependency graph."""

    def test_get_dependencies(self, manager):
        """Should get theorem dependencies."""
        # L'Hopital depends on mean value theorem
        deps = manager.get_dependencies("lhopital_rule")

        assert isinstance(deps, list)
        # Should include mean_value_theorem
        dep_ids = [d.theorem_id for d in deps]
        assert "mean_value_theorem" in dep_ids

    def test_get_dependencies_none(self, manager):
        """Should return empty for theorem with no deps."""
        deps = manager.get_dependencies("quadratic_formula")

        assert deps == []

    def test_get_dependencies_transitive(self, manager):
        """Should get transitive dependencies."""
        # MVT depends on Rolle, L'Hopital depends on MVT
        deps = manager.get_dependencies("lhopital_rule")

        # Should include both MVT and potentially Rolle
        dep_ids = [d.theorem_id for d in deps]
        assert "mean_value_theorem" in dep_ids


# =============================================================================
# BDI Interface Tests
# =============================================================================


class TestTheoremLibraryBDI:
    """Tests for BDI interface."""

    def test_update_beliefs(self, manager):
        """update_beliefs should not raise."""
        manager.update_beliefs()

    def test_deliberate(self, manager):
        """deliberate should return list."""
        result = manager.deliberate()
        assert isinstance(result, list)

    def test_execute_step(self, manager):
        """execute_step should not raise."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention
        intention = Mock(spec=Intention)
        manager.execute_step(intention)

    def test_get_statistics(self, manager):
        """Should return statistics dictionary."""
        stats = manager.get_statistics()

        assert isinstance(stats, dict)
        assert 'tasks_executed' in stats
        assert 'theorems_stored' in stats
        assert 'domains_covered' in stats
        assert 'lookups_performed' in stats
        assert 'proofs_sketched' in stats


# =============================================================================
# Process Task Tests
# =============================================================================


class TestTheoremLibraryProcess:
    """Tests for process method."""

    def test_process_lookup_operation(self, manager_with_infrastructure):
        """Should process lookup operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'lookup',
            'domain': 'calculus'
        }
        task_entry.conversation_id = 'test_conv'

        result = manager_with_infrastructure.process(task_entry)

        assert result is not None

    def test_process_applicability_operation(self, manager_with_infrastructure):
        """Should process applicability operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'applicability',
            'theorem_id': 'quadratic_formula',
            'conditions': ['a is nonzero']
        }
        task_entry.conversation_id = 'test_conv'

        result = manager_with_infrastructure.process(task_entry)

        assert result is not None

    def test_process_proof_sketch_operation(self, manager_with_infrastructure):
        """Should process proof_sketch operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'proof_sketch',
            'theorem_id': 'rolle_theorem'
        }
        task_entry.conversation_id = 'test_conv'

        result = manager_with_infrastructure.process(task_entry)

        assert result is not None

    def test_process_dependencies_operation(self, manager_with_infrastructure):
        """Should process dependencies operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'dependencies',
            'theorem_id': 'lhopital_rule'
        }
        task_entry.conversation_id = 'test_conv'

        result = manager_with_infrastructure.process(task_entry)

        assert result is not None

    def test_process_unknown_operation(self, manager_with_infrastructure):
        """Should handle unknown operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'unknown_op'
        }
        task_entry.conversation_id = 'test_conv'

        result = manager_with_infrastructure.process(task_entry)

        assert result is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestTheoremLibraryIntegration:
    """Integration tests for TheoremLibraryManager."""

    def test_full_workflow(self):
        """Test complete theorem workflow."""
        bb = Blackboard()
        df = DirectoryFacilitator()
        manager = TheoremLibraryManager(blackboard=bb, df=df)

        # Add custom theorem
        custom = Theorem(
            theorem_id="custom_thm",
            name="Custom Theorem",
            statement="If A then B",
            domain=MathDomain.LOGIC,
            hypotheses=["A is true"],
            conclusion="B is true",
            keywords={"custom", "logic"}
        )
        manager.add_theorem(custom)

        # Lookup
        results = manager.lookup_theorems(
            domain=MathDomain.LOGIC,
            keywords=["custom"]
        )

        assert len(results) > 0
        assert any(t.theorem_id == "custom_thm" for t in results)

    def test_calculus_theorems_chain(self, manager):
        """Test calculus theorem dependency chain."""
        # L'Hopital -> MVT -> Rolle
        deps = manager.get_dependencies("lhopital_rule")

        # Should have MVT
        mvt_found = any(d.theorem_id == "mean_value_theorem" for d in deps)
        assert mvt_found

        # MVT's deps should include Rolle
        mvt_deps = manager.get_dependencies("mean_value_theorem")
        rolle_found = any(d.theorem_id == "rolle_theorem" for d in mvt_deps)
        assert rolle_found


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
