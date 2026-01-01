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
BDI Agent Tests
===============

Comprehensive tests for the BDI Agent cognitive architecture:
- Belief, Desire, Intention dataclasses
- BDIAgent base class
- BDI control loop
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from symbo_agentic_reasoners.core.bdi_agent import (
    BDIAgent,
    Belief,
    Desire,
    Intention,
)


# =============================================================================
# Belief Tests
# =============================================================================


class TestBelief:
    """Tests for Belief dataclass."""

    def test_create_belief(self):
        """Should create belief with required fields."""
        belief = Belief(
            predicate="problem_type",
            content="polynomial_equation",
            confidence=0.9,
            source="observation"
        )

        assert belief.predicate == "problem_type"
        assert belief.content == "polynomial_equation"
        assert belief.confidence == 0.9
        assert belief.source == "observation"

    def test_belief_defaults(self):
        """Should have sensible defaults."""
        belief = Belief(
            predicate="test",
            content="value"
        )

        assert belief.confidence == 1.0
        assert belief.source == "observation"
        assert belief.timestamp is not None

    def test_belief_with_omdoc_content(self):
        """Should accept complex content."""
        belief = Belief(
            predicate="expression",
            content={"operator": "plus", "operands": ["x", "y"]},
            confidence=0.8,
            source="inference"
        )

        assert belief.content["operator"] == "plus"

    def test_belief_repr(self):
        """Should have readable repr."""
        belief = Belief(
            predicate="type",
            content="integral",
            confidence=0.75,
            source="inference"
        )

        r = repr(belief)
        assert "Belief" in r
        assert "type" in r
        assert "0.75" in r

    def test_belief_repr_long_content(self):
        """Should truncate long content in repr."""
        belief = Belief(
            predicate="long",
            content="x" * 100,
            confidence=1.0
        )

        r = repr(belief)
        assert "..." in r


# =============================================================================
# Desire Tests
# =============================================================================


class TestDesire:
    """Tests for Desire dataclass."""

    def test_create_desire(self):
        """Should create desire with required fields."""
        desire = Desire(
            goal="solve_integral",
            priority=9
        )

        assert desire.goal == "solve_integral"
        assert desire.priority == 9

    def test_desire_defaults(self):
        """Should have sensible defaults."""
        desire = Desire(
            goal="test"
        )

        assert desire.priority == 5
        assert desire.active is True
        assert desire.success_condition is None
        assert desire.deadline is None

    def test_desire_with_success_condition(self):
        """Should accept success condition."""
        desire = Desire(
            goal="verify_proof",
            success_condition={"status": "verified"},
            priority=7
        )

        assert desire.success_condition["status"] == "verified"

    def test_desire_with_deadline(self):
        """Should accept deadline."""
        deadline = datetime(2025, 12, 31)
        desire = Desire(
            goal="urgent_task",
            priority=10,
            deadline=deadline
        )

        assert desire.deadline == deadline

    def test_desire_repr(self):
        """Should have readable repr."""
        desire = Desire(
            goal="factorize",
            priority=8,
            active=True
        )

        r = repr(desire)
        assert "Desire" in r
        assert "factorize" in r
        assert "8" in r
        assert "active" in r

    def test_desire_inactive_repr(self):
        """Should show inactive status."""
        desire = Desire(
            goal="test",
            active=False
        )

        r = repr(desire)
        assert "inactive" in r


# =============================================================================
# Intention Tests
# =============================================================================


class TestIntention:
    """Tests for Intention dataclass."""

    def test_create_intention(self):
        """Should create intention with required fields."""
        intention = Intention(
            plan_id="plan_001",
            steps=["step1", "step2", "step3"],
            target_desire="solve_integral"
        )

        assert intention.plan_id == "plan_001"
        assert len(intention.steps) == 3
        assert intention.target_desire == "solve_integral"

    def test_intention_defaults(self):
        """Should have sensible defaults."""
        intention = Intention(
            plan_id="test",
            steps=[],
            target_desire="goal"
        )

        assert intention.current_step == 0
        assert intention.committed is True
        assert intention.metadata == {}

    def test_intention_is_complete_empty(self):
        """Empty plan should be complete."""
        intention = Intention(
            plan_id="empty",
            steps=[],
            target_desire="goal"
        )

        assert intention.is_complete() is True

    def test_intention_is_complete_with_steps(self):
        """Plan with unexecuted steps should not be complete."""
        intention = Intention(
            plan_id="test",
            steps=["a", "b", "c"],
            target_desire="goal"
        )

        assert intention.is_complete() is False

    def test_intention_is_complete_after_execution(self):
        """Plan should be complete after all steps executed."""
        intention = Intention(
            plan_id="test",
            steps=["a", "b"],
            target_desire="goal",
            current_step=2
        )

        assert intention.is_complete() is True

    def test_intention_get_current_action(self):
        """Should get current action."""
        intention = Intention(
            plan_id="test",
            steps=["first", "second", "third"],
            target_desire="goal",
            current_step=1
        )

        action = intention.get_current_action()

        assert action == "second"

    def test_intention_get_current_action_complete(self):
        """Should return None when complete."""
        intention = Intention(
            plan_id="test",
            steps=["a"],
            target_desire="goal",
            current_step=1
        )

        assert intention.get_current_action() is None

    def test_intention_advance(self):
        """Should advance to next step."""
        intention = Intention(
            plan_id="test",
            steps=["a", "b", "c"],
            target_desire="goal"
        )

        assert intention.current_step == 0
        intention.advance()
        assert intention.current_step == 1
        intention.advance()
        assert intention.current_step == 2

    def test_intention_advance_when_complete(self):
        """Should not advance past end."""
        intention = Intention(
            plan_id="test",
            steps=["a"],
            target_desire="goal",
            current_step=1
        )

        intention.advance()

        # Should still be at step 1 (complete)
        assert intention.current_step == 1

    def test_intention_repr(self):
        """Should have readable repr."""
        intention = Intention(
            plan_id="plan_integration",
            steps=["a", "b", "c"],
            target_desire="solve"
        )

        r = repr(intention)
        assert "Intention" in r
        assert "plan_integration" in r
        assert "0/3" in r


# =============================================================================
# BDIAgent Concrete Implementation for Testing
# =============================================================================


class ConcreteBDIAgent(BDIAgent):
    """Concrete implementation for testing abstract BDIAgent."""

    def __init__(self, agent_id: str):
        self.update_beliefs_called = 0
        self.deliberate_called = 0
        self.execute_step_called = 0
        self.execute_step_intentions = []
        super().__init__(agent_id)

    def update_beliefs(self):
        """Test implementation."""
        self.update_beliefs_called += 1

    def deliberate(self):
        """Test implementation."""
        self.deliberate_called += 1
        return []  # No new intentions

    def execute_step(self, intention: Intention):
        """Test implementation."""
        self.execute_step_called += 1
        self.execute_step_intentions.append(intention)
        intention.advance()


# =============================================================================
# BDIAgent Tests
# =============================================================================


class TestBDIAgentInitialization:
    """Tests for BDIAgent initialization."""

    def test_basic_initialization(self):
        """Should initialize with agent_id."""
        agent = ConcreteBDIAgent(agent_id="test_agent")

        assert agent.agent_id == "test_agent"
        assert agent.running is False
        assert agent.cycle_count == 0

    def test_initialization_creates_empty_collections(self):
        """Should initialize with empty collections."""
        agent = ConcreteBDIAgent(agent_id="test")

        assert len(agent.beliefs) == 0
        assert len(agent.desires) == 0
        assert len(agent.intentions) == 0


class TestBDIAgentBeliefManagement:
    """Tests for belief management."""

    def test_add_belief_via_dict(self):
        """Should store beliefs in dict."""
        agent = ConcreteBDIAgent(agent_id="test")
        belief = Belief(predicate="test", content="value")

        agent.beliefs["test"] = belief

        assert "test" in agent.beliefs
        assert agent.beliefs["test"] is belief

    def test_update_belief(self):
        """Should update existing belief."""
        agent = ConcreteBDIAgent(agent_id="test")
        agent.beliefs["key"] = Belief(predicate="key", content="old")
        agent.beliefs["key"] = Belief(predicate="key", content="new")

        assert agent.beliefs["key"].content == "new"


class TestBDIAgentDesireManagement:
    """Tests for desire management."""

    def test_add_desire_to_list(self):
        """Should add desire to list."""
        agent = ConcreteBDIAgent(agent_id="test")
        desire = Desire(goal="test", priority=5)

        agent.desires.append(desire)

        assert len(agent.desires) == 1
        assert agent.desires[0] is desire


class TestBDIAgentIntentionManagement:
    """Tests for intention management."""

    def test_add_intention_to_list(self):
        """Should add intention to list."""
        agent = ConcreteBDIAgent(agent_id="test")
        intention = Intention(plan_id="p1", steps=["a"], target_desire="g1")

        agent.intentions.append(intention)

        assert len(agent.intentions) == 1

    def test_remove_intention(self):
        """Should remove intention from list."""
        agent = ConcreteBDIAgent(agent_id="test")
        intention = Intention(plan_id="p1", steps=["a"], target_desire="g1")
        agent.intentions.append(intention)

        agent.intentions.remove(intention)

        assert len(agent.intentions) == 0


class TestBDIAgentControlLoop:
    """Tests for BDI control loop."""

    def test_stop(self):
        """Should set running to False."""
        agent = ConcreteBDIAgent(agent_id="test")
        agent.running = True

        agent.stop()

        assert agent.running is False

    def test_bdi_loop_calls_update_beliefs(self):
        """BDI loop should call update_beliefs."""
        agent = ConcreteBDIAgent(agent_id="test")

        # Run one cycle then stop
        def stop_after_one(*args):
            agent.stop()
            return []

        agent.deliberate = stop_after_one

        agent.bdi_loop()

        assert agent.update_beliefs_called > 0

    def test_bdi_loop_calls_deliberate(self):
        """BDI loop should call deliberate."""
        agent = ConcreteBDIAgent(agent_id="test")

        # Stop after first cycle
        def stop_after_one(*args):
            agent.stop()
            return []

        agent.deliberate = stop_after_one

        agent.bdi_loop()

        # deliberate was replaced, but original would have been called
        assert agent.running is False

    def test_bdi_loop_executes_intention(self):
        """BDI loop should execute intention steps."""
        agent = ConcreteBDIAgent(agent_id="test")
        intention = Intention(
            plan_id="test",
            steps=["step1"],
            target_desire="goal"
        )
        agent.intentions.append(intention)

        # Stop after one cycle
        original_deliberate = agent.deliberate

        def deliberate_then_stop():
            agent.stop()
            return original_deliberate()

        agent.deliberate = deliberate_then_stop

        agent.bdi_loop()

        assert agent.execute_step_called > 0

    def test_bdi_loop_increments_cycle_count(self):
        """BDI loop should increment cycle count."""
        agent = ConcreteBDIAgent(agent_id="test")

        # Run 3 cycles
        def stop_after_three():
            if agent.cycle_count >= 2:
                agent.stop()
            return []

        agent.deliberate = stop_after_three

        agent.bdi_loop()

        assert agent.cycle_count >= 2

    def test_bdi_loop_handles_exception(self):
        """BDI loop should continue after exception."""
        agent = ConcreteBDIAgent(agent_id="test")
        call_count = [0]

        def raise_then_stop():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("Test error")
            agent.stop()
            return []

        agent.deliberate = raise_then_stop

        # Should not raise
        agent.bdi_loop()

        assert call_count[0] >= 2


class TestBDIAgentIntentionCompletion:
    """Tests for intention completion handling."""

    def test_on_intention_complete_hook(self):
        """Should call on_intention_complete when intention finishes."""
        agent = ConcreteBDIAgent(agent_id="test")
        completed_intentions = []

        def track_completion(intention):
            completed_intentions.append(intention)

        agent.on_intention_complete = track_completion

        # Add intention that will complete in one step
        intention = Intention(
            plan_id="quick",
            steps=["only_step"],
            target_desire="goal"
        )
        agent.intentions.append(intention)

        # Run one cycle
        def stop_immediately():
            agent.stop()
            return []

        agent.deliberate = stop_immediately

        agent.bdi_loop()

        assert len(completed_intentions) == 1
        assert completed_intentions[0].plan_id == "quick"


class TestBDIAgentStatistics:
    """Tests for statistics tracking."""

    def test_get_statistics(self):
        """Should return statistics dict."""
        agent = ConcreteBDIAgent(agent_id="test")
        agent.beliefs["b1"] = Belief(predicate="p", content="c")
        agent.desires.append(Desire(goal="g"))

        stats = agent.get_statistics()

        assert isinstance(stats, dict)
        assert stats['agent_id'] == "test"
        assert stats['beliefs'] == 1
        assert stats['desires'] == 1
        assert stats['intentions'] == 0
        assert stats['cycles'] == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestBDIAgentIntegration:
    """Integration tests for BDI agent."""

    def test_full_bdi_workflow(self):
        """Test a complete BDI workflow."""
        agent = ConcreteBDIAgent(agent_id="integration_test")

        # Add beliefs
        agent.beliefs["x_value"] = Belief(
            predicate="x_value",
            content=5,
            confidence=1.0,
            source="observation"
        )

        # Add desires
        agent.desires.append(Desire(
            goal="compute_square",
            priority=10
        ))

        # Add intention
        agent.intentions.append(Intention(
            plan_id="plan_square",
            steps=["get_x", "compute", "store_result"],
            target_desire="compute_square"
        ))

        # Run a few cycles
        cycle_limit = [0]

        def limit_cycles():
            cycle_limit[0] += 1
            if cycle_limit[0] >= 3:
                agent.stop()
            return []

        agent.deliberate = limit_cycles

        agent.bdi_loop()

        # Verify state after execution
        stats = agent.get_statistics()
        assert stats['cycles'] >= 3
        assert agent.execute_step_called >= 3


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
