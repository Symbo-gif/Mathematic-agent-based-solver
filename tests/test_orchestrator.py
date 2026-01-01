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
Main Orchestrator Tests
=======================

Comprehensive tests for the Main Orchestrator:
- Initialization and configuration
- Non-intervention directive
- Task decomposition
- Agent routing
- Blackboard integration
- BDI interface
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import uuid

from symbo_agentic_reasoners.core.orchestrator import (
    MainOrchestrator,
    Task,
    NoAgentAvailableError,
    get_pool_domain_key,
    DOMAIN_TO_POOL_KEY,
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard,
    EntryStatus,
    EntryType,
)
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator,
)
from symbo_agentic_reasoners.agents.base.problem_analysis import (
    StructuredProblem,
    MathDomain,
    ProblemType,
)


# =============================================================================
# Task Dataclass Tests
# =============================================================================


class TestTask:
    """Tests for Task dataclass."""

    def test_create_task(self):
        """Should create task with required fields."""
        problem = Mock(spec=StructuredProblem)
        task = Task(
            task_id="task_001",
            structured_problem=problem,
            status=EntryStatus.PENDING
        )

        assert task.task_id == "task_001"
        assert task.structured_problem is problem
        assert task.status == EntryStatus.PENDING

    def test_task_defaults(self):
        """Should have sensible defaults."""
        task = Task(
            task_id="task_002",
            structured_problem=Mock(),
            status=EntryStatus.PENDING
        )

        assert task.assigned_agent is None
        assert task.blackboard_entry_id is None
        assert task.result is None
        assert task.error is None

    def test_task_with_assignment(self):
        """Should accept agent assignment."""
        task = Task(
            task_id="task_003",
            structured_problem=Mock(),
            status=EntryStatus.IN_PROGRESS,
            assigned_agent="algebra_specialist_001"
        )

        assert task.assigned_agent == "algebra_specialist_001"


# =============================================================================
# Domain Key Mapping Tests
# =============================================================================


class TestDomainMapping:
    """Tests for domain key mapping."""

    def test_domain_to_pool_key_calculus(self):
        """Should map Calculus domain."""
        result = get_pool_domain_key(MathDomain.CALCULUS)
        assert result == 'calculus'

    def test_domain_to_pool_key_algebra(self):
        """Should map Algebra domain."""
        result = get_pool_domain_key(MathDomain.ALGEBRA)
        assert result == 'algebra'

    def test_domain_to_pool_key_linear_algebra(self):
        """Should map LinearAlgebra domain."""
        result = get_pool_domain_key(MathDomain.LINEAR_ALGEBRA)
        assert result == 'linear_algebra'

    def test_domain_to_pool_key_unknown(self):
        """Should handle unknown domain."""
        result = get_pool_domain_key(MathDomain.UNKNOWN)
        assert result == 'unknown'

    def test_domain_mapping_dict_exists(self):
        """DOMAIN_TO_POOL_KEY should exist with mappings."""
        assert 'Calculus' in DOMAIN_TO_POOL_KEY
        assert 'Algebra' in DOMAIN_TO_POOL_KEY
        assert 'LinearAlgebra' in DOMAIN_TO_POOL_KEY


# =============================================================================
# MainOrchestrator Initialization Tests
# =============================================================================


class TestOrchestratorInitialization:
    """Tests for MainOrchestrator initialization."""

    def test_basic_initialization(self):
        """Should initialize with default agent_id."""
        orchestrator = MainOrchestrator()

        assert orchestrator.agent_id == 'main_orchestrator_001'
        assert orchestrator.NON_INTERVENTION is True

    def test_custom_agent_id(self):
        """Should accept custom agent_id."""
        orchestrator = MainOrchestrator(agent_id='custom_orchestrator')

        assert orchestrator.agent_id == 'custom_orchestrator'

    def test_initialization_with_df(self):
        """Should initialize with Directory Facilitator."""
        df = DirectoryFacilitator()
        orchestrator = MainOrchestrator(df=df)

        assert orchestrator.df is df

    def test_initialization_with_blackboard(self):
        """Should initialize with Blackboard."""
        bb = Blackboard()
        orchestrator = MainOrchestrator(blackboard=bb)

        assert orchestrator.blackboard is bb

    def test_initialization_with_agent_pool(self):
        """Should initialize with AgentPool."""
        pool = Mock()
        orchestrator = MainOrchestrator(agent_pool=pool)

        assert orchestrator.agent_pool is pool

    def test_non_intervention_is_hardcoded(self):
        """NON_INTERVENTION should be True and not changeable."""
        orchestrator = MainOrchestrator()

        # It's True by default
        assert orchestrator.NON_INTERVENTION is True

        # Even if set to False, process should still check
        orchestrator.NON_INTERVENTION = False
        # The process method will raise RuntimeError if this is False

    def test_statistics_initialized(self):
        """Should initialize statistics to zero."""
        orchestrator = MainOrchestrator()

        assert orchestrator.tasks_routed == 0
        assert orchestrator.tasks_completed == 0
        assert orchestrator.tasks_failed == 0
        assert orchestrator.agents_woken == 0
        assert orchestrator.agents_activated == 0

    def test_task_tracking_initialized(self):
        """Should initialize empty task tracking."""
        orchestrator = MainOrchestrator()

        assert orchestrator.active_tasks == {}
        assert orchestrator.completed_tasks == []


# =============================================================================
# Decomposition Tests
# =============================================================================


class TestDecomposition:
    """Tests for task decomposition."""

    def test_decompose_returns_single_task(self):
        """Phase 1 decomposition returns single task."""
        orchestrator = MainOrchestrator()
        problem = Mock(spec=StructuredProblem)

        subtasks = orchestrator._decompose(problem)

        # Phase 1: single-step tasks only
        assert len(subtasks) == 1
        assert subtasks[0] is problem


# =============================================================================
# Service Type Mapping Tests
# =============================================================================


class TestServiceTypeMapping:
    """Tests for service type mapping."""

    def test_get_service_type_calculus(self):
        """Should map Calculus to math.calculus."""
        orchestrator = MainOrchestrator()

        service_type = orchestrator._get_service_type(MathDomain.CALCULUS)

        assert service_type == 'math.calculus'

    def test_get_service_type_algebra(self):
        """Should map Algebra to math.algebra."""
        orchestrator = MainOrchestrator()

        service_type = orchestrator._get_service_type(MathDomain.ALGEBRA)

        assert service_type == 'math.algebra'

    def test_get_service_type_linear_algebra(self):
        """Should map LinearAlgebra to math.linalg."""
        orchestrator = MainOrchestrator()

        service_type = orchestrator._get_service_type(MathDomain.LINEAR_ALGEBRA)

        assert service_type == 'math.linalg'

    def test_get_service_type_statistics(self):
        """Should map Statistics to math.stats."""
        orchestrator = MainOrchestrator()

        service_type = orchestrator._get_service_type(MathDomain.STATISTICS)

        assert service_type == 'math.stats'


# =============================================================================
# Agent Finding Tests
# =============================================================================


class TestAgentFinding:
    """Tests for finding capable agents."""

    def test_find_capable_agents_with_df(self):
        """Should query DF for agents."""
        df = Mock()
        df.search.return_value = [
            Mock(agent_id='agent_1'),
            Mock(agent_id='agent_2')
        ]
        orchestrator = MainOrchestrator(df=df)

        agents = orchestrator._find_capable_agents('math.calculus')

        assert len(agents) == 2
        df.search.assert_called_once_with(service_type='math.calculus')

    def test_find_capable_agents_without_df(self):
        """Should return empty list without DF."""
        orchestrator = MainOrchestrator(df=None)

        agents = orchestrator._find_capable_agents('math.calculus')

        assert agents == []


# =============================================================================
# Agent Pool Integration Tests
# =============================================================================


class TestAgentPoolIntegration:
    """Tests for AgentPool integration."""

    def test_wake_domain_agents_with_pool(self):
        """Should wake agents via pool."""
        pool = Mock()
        pool.wake_for_domain.return_value = ['agent_1', 'agent_2']
        orchestrator = MainOrchestrator(agent_pool=pool)

        woken = orchestrator._wake_domain_agents('calculus')

        assert woken == ['agent_1', 'agent_2']
        assert orchestrator.agents_woken == 2
        pool.wake_for_domain.assert_called_once_with('calculus')

    def test_wake_domain_agents_without_pool(self):
        """Should return empty without pool."""
        orchestrator = MainOrchestrator(agent_pool=None)

        woken = orchestrator._wake_domain_agents('calculus')

        assert woken == []

    def test_activate_agent_with_pool(self):
        """Should activate agent via pool."""
        pool = Mock()
        pool.activate.return_value = True
        orchestrator = MainOrchestrator(agent_pool=pool)

        result = orchestrator._activate_agent('agent_1')

        assert result is True
        assert orchestrator.agents_activated == 1
        pool.activate.assert_called_once_with('agent_1')

    def test_activate_agent_without_pool(self):
        """Should return True without pool."""
        orchestrator = MainOrchestrator(agent_pool=None)

        result = orchestrator._activate_agent('agent_1')

        assert result is True

    def test_deactivate_agent_with_pool(self):
        """Should deactivate agent via pool."""
        pool = Mock()
        pool.deactivate.return_value = True
        orchestrator = MainOrchestrator(agent_pool=pool)

        result = orchestrator._deactivate_agent('agent_1', return_to_standby=True)

        assert result is True
        pool.deactivate.assert_called_once_with('agent_1', True)

    def test_deactivate_agent_without_pool(self):
        """Should return True without pool."""
        orchestrator = MainOrchestrator(agent_pool=None)

        result = orchestrator._deactivate_agent('agent_1')

        assert result is True


# =============================================================================
# Blackboard Task Posting Tests
# =============================================================================


class TestBlackboardTaskPosting:
    """Tests for posting tasks to Blackboard."""

    def test_post_task_to_blackboard(self):
        """Should post task entry to Blackboard."""
        bb = Mock()
        orchestrator = MainOrchestrator(blackboard=bb)

        problem = Mock(spec=StructuredProblem)
        problem.domain = MathDomain.ALGEBRA
        problem.problem_type = Mock(value='equation')
        problem.raw_input = 'x + 1 = 0'
        problem.omdoc_content = Mock()
        problem.sympy_expr = None
        problem.metadata = {}

        task = orchestrator._post_task_to_blackboard(problem, 'algebra_agent')

        assert task.task_id is not None
        assert task.assigned_agent == 'algebra_agent'
        assert task.status == EntryStatus.PENDING
        bb.post.assert_called_once()

    def test_post_task_without_blackboard(self):
        """Should return failed task without Blackboard."""
        orchestrator = MainOrchestrator(blackboard=None)

        problem = Mock(spec=StructuredProblem)
        task = orchestrator._post_task_to_blackboard(problem, 'agent')

        assert task.status == EntryStatus.FAILED
        assert task.error == "No Blackboard available"

    def test_post_task_increments_counter(self):
        """Should increment tasks_routed counter."""
        bb = Mock()
        orchestrator = MainOrchestrator(blackboard=bb)

        problem = Mock(spec=StructuredProblem)
        problem.domain = MathDomain.ALGEBRA
        problem.problem_type = Mock(value='equation')
        problem.raw_input = 'x + 1 = 0'
        problem.omdoc_content = Mock()
        problem.sympy_expr = None
        problem.metadata = {}

        initial = orchestrator.tasks_routed
        orchestrator._post_task_to_blackboard(problem, 'agent')

        assert orchestrator.tasks_routed == initial + 1


# =============================================================================
# BDI Interface Tests
# =============================================================================


class TestOrchestratorBDI:
    """Tests for BDI interface."""

    def test_update_beliefs(self):
        """update_beliefs should not raise."""
        orchestrator = MainOrchestrator()
        orchestrator.update_beliefs()  # Should not raise

    def test_deliberate(self):
        """deliberate should return list."""
        orchestrator = MainOrchestrator()
        result = orchestrator.deliberate()

        assert isinstance(result, list)

    def test_execute_step(self):
        """execute_step should not raise."""
        from symbo_agentic_reasoners.core.bdi_agent import Intention
        orchestrator = MainOrchestrator()
        intention = Mock(spec=Intention)

        orchestrator.execute_step(intention)  # Should not raise

    def test_get_statistics(self):
        """Should return statistics dict."""
        orchestrator = MainOrchestrator()

        stats = orchestrator.get_statistics()

        assert isinstance(stats, dict)


# =============================================================================
# Process Tests
# =============================================================================


class TestOrchestratorProcess:
    """Tests for process method."""

    def test_process_raises_without_agents(self):
        """Should raise NoAgentAvailableError when no agents found."""
        df = Mock()
        df.search.return_value = []
        bb = Blackboard()
        orchestrator = MainOrchestrator(df=df, blackboard=bb)

        problem = Mock(spec=StructuredProblem)
        problem.domain = MathDomain.CALCULUS
        problem.problem_type = Mock(value='integral')
        problem.raw_input = 'integral of x'

        with pytest.raises(NoAgentAvailableError):
            orchestrator.process(problem)

    def test_process_enforces_non_intervention(self):
        """Should raise if NON_INTERVENTION is violated."""
        orchestrator = MainOrchestrator()
        orchestrator.NON_INTERVENTION = False

        problem = Mock(spec=StructuredProblem)
        problem.domain = MathDomain.ALGEBRA
        problem.problem_type = Mock(value='equation')
        problem.raw_input = 'x + 1 = 0'

        with pytest.raises(RuntimeError, match="NON_INTERVENTION"):
            orchestrator.process(problem)


# =============================================================================
# NoAgentAvailableError Tests
# =============================================================================


class TestNoAgentAvailableError:
    """Tests for NoAgentAvailableError exception."""

    def test_exception_with_message(self):
        """Should create exception with message."""
        error = NoAgentAvailableError("No calculus agent")

        assert str(error) == "No calculus agent"

    def test_exception_is_exception(self):
        """Should be an Exception subclass."""
        assert issubclass(NoAgentAvailableError, Exception)


# =============================================================================
# Integration Tests
# =============================================================================


class TestOrchestratorIntegration:
    """Integration tests for MainOrchestrator."""

    def test_full_initialization(self):
        """Test full initialization with all components."""
        bb = Blackboard()
        df = DirectoryFacilitator()
        pool = Mock()

        orchestrator = MainOrchestrator(
            agent_id='integration_orchestrator',
            df=df,
            blackboard=bb,
            agent_pool=pool
        )

        assert orchestrator.agent_id == 'integration_orchestrator'
        assert orchestrator.df is df
        assert orchestrator.blackboard is bb
        assert orchestrator.agent_pool is pool
        assert orchestrator.NON_INTERVENTION is True

    def test_task_lifecycle(self):
        """Test task tracking lifecycle."""
        bb = Mock()
        orchestrator = MainOrchestrator(blackboard=bb)

        problem = Mock(spec=StructuredProblem)
        problem.domain = MathDomain.ALGEBRA
        problem.problem_type = Mock(value='equation')
        problem.raw_input = 'x = 5'
        problem.omdoc_content = Mock()
        problem.sympy_expr = None
        problem.metadata = {}

        # Post task
        task = orchestrator._post_task_to_blackboard(problem, 'agent_1')

        # Should be in active tasks
        assert task.task_id in orchestrator.active_tasks

        # Simulate completion
        orchestrator.active_tasks.pop(task.task_id)
        orchestrator.completed_tasks.append(task)
        orchestrator.tasks_completed += 1

        assert task.task_id not in orchestrator.active_tasks
        assert task in orchestrator.completed_tasks


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
