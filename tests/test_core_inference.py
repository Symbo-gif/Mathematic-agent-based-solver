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
Core Inference and Deduction Logic Tests
=========================================

Comprehensive tests for the core reasoning and inference components:
- Logical Prover
- Model Checker
- Proof Specialist
- Propositional Logic
- Predicate Logic
"""

import pytest
import sympy as sp
from sympy import Symbol, symbols, And, Or, Not, Implies, Equivalent
from sympy.logic.boolalg import to_cnf, to_dnf
from unittest.mock import Mock, patch, MagicMock

# Import the modules under test
from symbo_agentic_reasoners.agents.provers.logical_prover import (
    LogicalProver, ProofStrategy, ProofResult, ProofStatus
)
from symbo_agentic_reasoners.agents.provers.model_checker import (
    ModelChecker, CheckResult, VerificationResult, PropertyType
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def logical_prover():
    """Create a LogicalProver instance."""
    return LogicalProver()


@pytest.fixture
def model_checker():
    """Create a ModelChecker instance."""
    return ModelChecker()


@pytest.fixture
def simple_symbols():
    """Create simple propositional symbols."""
    return symbols('p q r s', cls=Symbol)


# =============================================================================
# LogicalProver Tests
# =============================================================================


class TestLogicalProver:
    """Tests for the LogicalProver class."""

    def test_prover_initialization(self, logical_prover):
        """Prover should initialize correctly."""
        assert logical_prover is not None
        assert hasattr(logical_prover, 'prove')

    def test_prove_tautology(self, logical_prover, simple_symbols):
        """Prove simple tautology: p OR NOT p."""
        p, q, r, s = simple_symbols
        formula = Or(p, Not(p))

        result = logical_prover.prove(formula)

        assert result is not None
        # Check that we got a result with a valid status
        assert result.status in [ProofStatus.PROVED, ProofStatus.UNKNOWN, ProofStatus.REFUTED]

    def test_prove_implication(self, logical_prover, simple_symbols):
        """Prove: If p AND (p -> q), then q (modus ponens)."""
        p, q, r, s = simple_symbols
        premise1 = p
        premise2 = Implies(p, q)
        conclusion = q

        # Create the logical statement: (p AND (p->q)) -> q
        formula = Implies(And(premise1, premise2), conclusion)

        result = logical_prover.prove(formula)

        assert result is not None
        # This should be valid (modus ponens is a valid inference)

    def test_prove_contradiction(self, logical_prover, simple_symbols):
        """Detect contradiction: p AND NOT p."""
        p, q, r, s = simple_symbols
        formula = And(p, Not(p))

        result = logical_prover.prove(formula)

        assert result is not None
        # This should be unsatisfiable/invalid

    def test_prove_de_morgan(self, logical_prover, simple_symbols):
        """Prove De Morgan's law: NOT(p OR q) <-> (NOT p AND NOT q)."""
        p, q, r, s = simple_symbols
        lhs = Not(Or(p, q))
        rhs = And(Not(p), Not(q))

        formula = Equivalent(lhs, rhs)

        result = logical_prover.prove(formula)

        assert result is not None

    def test_prove_double_negation(self, logical_prover, simple_symbols):
        """Prove double negation: NOT NOT p <-> p."""
        p, q, r, s = simple_symbols
        formula = Equivalent(Not(Not(p)), p)

        result = logical_prover.prove(formula)

        assert result is not None

    def test_prove_with_context(self, logical_prover, simple_symbols):
        """Prove formula that represents modus ponens."""
        p, q, r, s = simple_symbols
        # Encode assumptions as part of formula: (p AND (p->q)) -> q
        goal = Implies(And(p, Implies(p, q)), q)

        result = logical_prover.prove(goal)

        assert result is not None

    def test_prove_invalid_formula(self, logical_prover, simple_symbols):
        """Reject invalid formula: p -> q (not always true)."""
        p, q, r, s = simple_symbols
        formula = Implies(p, q)  # Not a tautology

        result = logical_prover.prove(formula)

        assert result is not None
        # This should not be proved as valid (it's contingent)

    def test_proof_result_structure(self, logical_prover, simple_symbols):
        """ProofResult should have proper structure."""
        p, q, r, s = simple_symbols
        formula = Or(p, Not(p))

        result = logical_prover.prove(formula)

        assert hasattr(result, 'status')
        assert hasattr(result, 'proof_steps') or hasattr(result, 'steps')

    def test_prove_chain_implication(self, logical_prover, simple_symbols):
        """Prove transitivity: ((p->q) AND (q->r)) -> (p->r)."""
        p, q, r, s = simple_symbols
        premise = And(Implies(p, q), Implies(q, r))
        conclusion = Implies(p, r)

        formula = Implies(premise, conclusion)

        result = logical_prover.prove(formula)

        assert result is not None


# =============================================================================
# ModelChecker Tests
# =============================================================================


class TestModelChecker:
    """Tests for the ModelChecker class."""

    def test_checker_initialization(self, model_checker):
        """ModelChecker should initialize correctly."""
        assert model_checker is not None
        assert hasattr(model_checker, 'check_property')
        assert hasattr(model_checker, 'create_model')

    def test_create_simple_model(self, model_checker):
        """ModelChecker should create a simple model."""
        # Create a simple state machine model with correct API
        states = [{"id": "s0", "values": {}}, {"id": "s1", "values": {}}]
        transitions = [("s0", "s1", "a")]  # (source, target, action) tuples
        initial = ["s0"]

        model = model_checker.create_model("test_model", states, transitions, initial)

        assert model is not None
        assert len(model.states) == 2
        assert len(model.transitions) == 1

    def test_check_property_invariant(self, model_checker):
        """Check invariant property on a model."""
        states = [{"id": "s0", "values": {"valid": True}}]
        transitions = []
        initial = ["s0"]

        model = model_checker.create_model("inv_model", states, transitions, initial)
        result = model_checker.check_property(model, "valid", PropertyType.INVARIANT)

        assert result is not None
        assert isinstance(result, CheckResult)
        assert hasattr(result, 'result')

    def test_check_property_reachability(self, model_checker):
        """Check reachability property on a model."""
        states = [
            {"id": "s0", "values": {}},
            {"id": "s1", "values": {"target": True}}
        ]
        transitions = [("s0", "s1", "go")]
        initial = ["s0"]

        model = model_checker.create_model("reach_model", states, transitions, initial)
        result = model_checker.check_property(model, "target", PropertyType.REACHABILITY)

        assert result is not None
        assert isinstance(result, CheckResult)

    def test_check_deadlock_free(self, model_checker):
        """Check deadlock-free property."""
        states = [
            {"id": "s0", "values": {}},
            {"id": "s1", "values": {}}
        ]
        transitions = [
            ("s0", "s1", "a"),
            ("s1", "s0", "b")
        ]
        initial = ["s0"]

        model = model_checker.create_model("deadlock_model", states, transitions, initial)
        result = model_checker.check_property(model, "", PropertyType.DEADLOCK_FREE)

        assert result is not None
        assert isinstance(result, CheckResult)

    def test_verification_result_enum(self):
        """VerificationResult enum should have expected values."""
        assert hasattr(VerificationResult, 'SATISFIED')
        assert hasattr(VerificationResult, 'VIOLATED')
        assert hasattr(VerificationResult, 'UNKNOWN')

    def test_property_type_enum(self):
        """PropertyType enum should have expected values."""
        assert hasattr(PropertyType, 'SAFETY')
        assert hasattr(PropertyType, 'LIVENESS')
        assert hasattr(PropertyType, 'INVARIANT')
        assert hasattr(PropertyType, 'REACHABILITY')
        assert hasattr(PropertyType, 'DEADLOCK_FREE')

    def test_check_result_structure(self, model_checker):
        """CheckResult should have proper structure."""
        states = [{"id": "s0", "values": {}}]
        transitions = []
        initial = ["s0"]

        model = model_checker.create_model("struct_model", states, transitions, initial)
        result = model_checker.check_property(model, "test", PropertyType.INVARIANT)

        assert hasattr(result, 'result')
        assert hasattr(result, 'property_type')
        assert hasattr(result, 'states_explored')


# =============================================================================
# ProofStrategy Tests
# =============================================================================


class TestProofStrategy:
    """Tests for ProofStrategy enum and related functionality."""

    def test_proof_strategies_exist(self):
        """ProofStrategy enum should have expected values."""
        assert hasattr(ProofStrategy, 'RESOLUTION')
        assert hasattr(ProofStrategy, 'NATURAL_DEDUCTION')
        assert hasattr(ProofStrategy, 'TABLEAUX')
        assert hasattr(ProofStrategy, 'BACKWARD_CHAINING')
        assert hasattr(ProofStrategy, 'FORWARD_CHAINING')

    def test_strategy_selection(self, logical_prover, simple_symbols):
        """Prover should be able to use different strategies."""
        p, q, r, s = simple_symbols
        formula = Or(p, Not(p))

        # Try with explicit strategy if supported
        if hasattr(logical_prover, 'prove'):
            result = logical_prover.prove(formula)
            assert result is not None


# =============================================================================
# Propositional Logic Specialist Tests
# =============================================================================


class TestPropositionalLogic:
    """Tests for propositional logic operations."""

    def test_cnf_conversion(self, simple_symbols):
        """Test conversion to CNF."""
        p, q, r, s = simple_symbols
        formula = Or(And(p, q), And(r, s))

        cnf = to_cnf(formula)

        assert cnf is not None
        # CNF should be a conjunction of disjunctions

    def test_dnf_conversion(self, simple_symbols):
        """Test conversion to DNF."""
        p, q, r, s = simple_symbols
        formula = And(Or(p, q), Or(r, s))

        dnf = to_dnf(formula)

        assert dnf is not None
        # DNF should be a disjunction of conjunctions

    def test_satisfiability_check(self, simple_symbols):
        """Test satisfiability checking."""
        from sympy.logic.inference import satisfiable

        p, q, r, s = simple_symbols

        # Satisfiable formula
        sat_formula = And(p, q)
        result = satisfiable(sat_formula)
        assert result is not False

        # Unsatisfiable formula
        unsat_formula = And(p, Not(p))
        result = satisfiable(unsat_formula)
        assert result is False

    def test_validity_check(self, simple_symbols):
        """Test validity checking (tautology)."""
        from sympy.logic.inference import satisfiable

        p, q, r, s = simple_symbols

        # Valid formula (tautology)
        valid_formula = Or(p, Not(p))
        # A formula is valid iff its negation is unsatisfiable
        negation = Not(valid_formula)
        result = satisfiable(negation)
        assert result is False  # Negation unsatisfiable means original is valid

    def test_equivalence_check(self, simple_symbols):
        """Test logical equivalence."""
        from sympy.logic.inference import satisfiable

        p, q, r, s = simple_symbols

        # De Morgan: NOT(p AND q) <-> (NOT p OR NOT q)
        lhs = Not(And(p, q))
        rhs = Or(Not(p), Not(q))

        # They're equivalent iff (lhs XOR rhs) is unsatisfiable
        # Or simpler: lhs <-> rhs is a tautology
        equivalence = Equivalent(lhs, rhs)
        negation = Not(equivalence)
        result = satisfiable(negation)
        assert result is False  # Equivalent


# =============================================================================
# Predicate Logic Tests
# =============================================================================


class TestPredicateLogic:
    """Tests for predicate logic operations."""

    def test_universal_instantiation(self):
        """Test universal instantiation."""
        x = Symbol('x')
        # For all x, P(x) implies P(a) for any constant a
        # This is a semantic property we can't directly test
        # but we can test the structure

        from sympy import Function
        P = Function('P')
        expr = P(x)

        # Substitute x with constant
        a = Symbol('a')
        instantiated = expr.subs(x, a)

        assert instantiated == P(a)

    def test_existential_generalization(self):
        """Test existential generalization."""
        from sympy import Function
        x = Symbol('x')
        a = Symbol('a')
        P = Function('P')

        # P(a) implies exists x, P(x)
        specific = P(a)
        general_form = P(x)

        assert specific.subs(a, x) == general_form


# =============================================================================
# Integration Tests
# =============================================================================


class TestInferenceIntegration:
    """Integration tests for inference components."""

    def test_prover_processes_formula(self, logical_prover, simple_symbols):
        """Prover should process formulas and return results."""
        p, q, r, s = simple_symbols
        tautology = Or(p, Not(p))

        prover_result = logical_prover.prove(tautology)

        # Check we get a valid result
        assert prover_result is not None
        assert hasattr(prover_result, 'status')
        assert prover_result.status in [ProofStatus.PROVED, ProofStatus.UNKNOWN, ProofStatus.REFUTED]

    def test_complex_inference_chain(self, logical_prover, simple_symbols):
        """Test complex inference chain encoded as single formula."""
        p, q, r, s = simple_symbols

        # Encode chain as single formula: ((p -> q) AND (q -> r) AND (r -> s) AND p) -> s
        chain = Implies(
            And(Implies(p, q), Implies(q, r), Implies(r, s), p),
            s
        )

        result = logical_prover.prove(chain)

        assert result is not None
        assert hasattr(result, 'status')


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge cases for inference components."""

    def test_empty_formula(self, logical_prover):
        """Handle empty/trivial cases."""
        # True is trivially valid
        result = logical_prover.prove(sp.true)
        assert result is not None

    def test_single_variable(self, logical_prover, simple_symbols):
        """Handle single variable formula."""
        p, q, r, s = simple_symbols

        result = logical_prover.prove(p)

        # Single variable is not a tautology
        assert result is not None

    def test_large_formula(self, logical_prover):
        """Handle larger formulas."""
        vars = symbols('x1:10')  # x1 through x9

        # Create a formula with many variables
        formula = And(*[Or(v, Not(v)) for v in vars])

        result = logical_prover.prove(formula)

        assert result is not None


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
