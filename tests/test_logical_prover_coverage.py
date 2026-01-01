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
Tests for Logical Prover Module
================================

Comprehensive tests for the LogicalProver BDI agent and proof structures.
"""

import pytest
from unittest.mock import MagicMock


class TestProofStatus:
    """Tests for ProofStatus enum."""

    def test_proof_status_values(self):
        """Test ProofStatus enum values."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import ProofStatus
        assert ProofStatus.PENDING.value == 'pending'
        assert ProofStatus.IN_PROGRESS.value == 'in_progress'
        assert ProofStatus.PROVED.value == 'proved'
        assert ProofStatus.REFUTED.value == 'refuted'
        assert ProofStatus.TIMEOUT.value == 'timeout'
        assert ProofStatus.UNKNOWN.value == 'unknown'


class TestProofStrategy:
    """Tests for ProofStrategy enum."""

    def test_proof_strategy_values(self):
        """Test ProofStrategy enum values."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import ProofStrategy
        assert ProofStrategy.RESOLUTION.value == 'resolution'
        assert ProofStrategy.NATURAL_DEDUCTION.value == 'natural_deduction'
        assert ProofStrategy.TABLEAUX.value == 'tableaux'
        assert ProofStrategy.BACKWARD_CHAINING.value == 'backward_chaining'
        assert ProofStrategy.FORWARD_CHAINING.value == 'forward_chaining'


class TestFormula:
    """Tests for Formula dataclass."""

    def test_formula_create(self):
        """Test creating a formula."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import Formula
        f = Formula(text='P -> Q')
        assert f.text == 'P -> Q'
        assert f.negated is False
        assert f.connective is None

    def test_formula_negated(self):
        """Test creating negated formula."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import Formula
        f = Formula(text='P', negated=True)
        assert f.negated is True
        assert str(f) == '¬P'

    def test_formula_with_connective(self):
        """Test formula with connective."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import Formula
        f = Formula(text='P and Q', connective='and')
        assert f.connective == 'and'

    def test_formula_to_dict(self):
        """Test formula serialization."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import Formula
        f = Formula(text='P -> Q', connective='implies')
        d = f.to_dict()
        assert d['text'] == 'P -> Q'
        assert d['connective'] == 'implies'
        assert d['negated'] is False

    def test_formula_str_not_negated(self):
        """Test string representation of non-negated formula."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import Formula
        f = Formula(text='P')
        assert str(f) == 'P'


class TestProofStep:
    """Tests for ProofStep dataclass."""

    def test_proof_step_create(self):
        """Test creating a proof step."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import (
            ProofStep, Formula
        )
        f = Formula(text='P')
        step = ProofStep(
            step_number=1,
            formula=f,
            justification='Assumption'
        )
        assert step.step_number == 1
        assert step.justification == 'Assumption'
        assert step.premises == []

    def test_proof_step_with_premises(self):
        """Test proof step with premises."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import (
            ProofStep, Formula
        )
        f = Formula(text='Q')
        step = ProofStep(
            step_number=3,
            formula=f,
            justification='Modus Ponens',
            premises=[1, 2]
        )
        assert step.premises == [1, 2]

    def test_proof_step_to_dict(self):
        """Test proof step serialization."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import (
            ProofStep, Formula
        )
        f = Formula(text='P -> Q')
        step = ProofStep(
            step_number=1,
            formula=f,
            justification='Given',
            premises=[]
        )
        d = step.to_dict()
        assert d['step'] == 1
        assert d['formula'] == 'P -> Q'
        assert d['justification'] == 'Given'


class TestProofResult:
    """Tests for ProofResult dataclass."""

    def test_proof_result_proved(self):
        """Test successful proof result."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import (
            ProofResult, ProofStatus, ProofStrategy
        )
        result = ProofResult(
            status=ProofStatus.PROVED,
            goal='P -> P',
            steps=[],
            strategy_used=ProofStrategy.RESOLUTION
        )
        assert result.status == ProofStatus.PROVED
        assert result.goal == 'P -> P'

    def test_proof_result_refuted(self):
        """Test refuted proof result with countermodel."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import (
            ProofResult, ProofStatus, ProofStrategy
        )
        result = ProofResult(
            status=ProofStatus.REFUTED,
            goal='P',
            steps=[],
            strategy_used=ProofStrategy.TABLEAUX,
            countermodel={'P': False}
        )
        assert result.status == ProofStatus.REFUTED
        assert result.countermodel == {'P': False}

    def test_proof_result_to_dict(self):
        """Test proof result serialization."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import (
            ProofResult, ProofStatus, ProofStrategy
        )
        result = ProofResult(
            status=ProofStatus.PROVED,
            goal='Q',
            steps=[],
            strategy_used=ProofStrategy.NATURAL_DEDUCTION,
            time_ms=100
        )
        d = result.to_dict()
        assert d['status'] == 'proved'
        assert d['goal'] == 'Q'
        assert d['strategy'] == 'natural_deduction'
        assert d['time_ms'] == 100
        assert d['has_countermodel'] is False


class TestLogicalProverInit:
    """Tests for LogicalProver initialization."""

    def test_prover_create(self):
        """Test creating logical prover."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import LogicalProver
        prover = LogicalProver()
        assert prover.agent_id == 'logical_prover_001'

    def test_prover_custom_id(self):
        """Test creating with custom agent ID."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import LogicalProver
        prover = LogicalProver(agent_id='custom_prover')
        assert prover.agent_id == 'custom_prover'

    def test_prover_with_df(self):
        """Test creating with directory facilitator."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import LogicalProver
        mock_df = MagicMock()
        prover = LogicalProver(df=mock_df)
        assert prover.df is mock_df


class TestLogicalProverBDI:
    """Tests for BDI methods."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs without blackboard."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import LogicalProver
        prover = LogicalProver()
        prover.update_beliefs()  # Should not raise

    def test_deliberate_no_tasks(self):
        """Test deliberate with no pending tasks."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import LogicalProver
        prover = LogicalProver()
        intentions = prover.deliberate()
        assert intentions == []

    def test_get_statistics(self):
        """Test getting agent statistics."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import LogicalProver
        prover = LogicalProver()
        stats = prover.get_statistics()
        assert 'proofs_attempted' in stats or 'tasks_executed' in stats


class TestModuleImports:
    """Tests for module imports."""

    def test_logical_prover_import(self):
        """Test LogicalProver can be imported."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import LogicalProver
        assert LogicalProver is not None

    def test_formula_import(self):
        """Test Formula can be imported."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import Formula
        assert Formula is not None

    def test_proof_step_import(self):
        """Test ProofStep can be imported."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import ProofStep
        assert ProofStep is not None

    def test_proof_result_import(self):
        """Test ProofResult can be imported."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import ProofResult
        assert ProofResult is not None

    def test_enums_import(self):
        """Test enums can be imported."""
        from symbo_agentic_reasoners.agents.provers.logical_prover import (
            ProofStatus, ProofStrategy
        )
        assert ProofStatus is not None
        assert ProofStrategy is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
