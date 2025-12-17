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
Orchestration Blackboard Integration
====================================

Manages orchestrator interaction with blackboard.

Responsibilities:
- Posting tasks to blackboard for asynchronous agent execution
- Awaiting and retrieving results from blackboard
- Agent lifecycle management (activation/deactivation) during task execution
"""

import logging
import time
import uuid
from typing import Any, Optional

from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool
from symbo_agentic_reasoners.core.orchestration.data_structures import Task

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.blackboard')


class BlackboardIntegration:
    """
    Manages orchestrator interaction with blackboard.

    Handles posting tasks and awaiting results from asynchronous agents.
    Integrates with AgentPool for lifecycle management (activation/deactivation).

    Statistics:
        blackboard_posts: Number of tasks posted to blackboard
        agents_activated: Number of agents activated
        agents_deactivated: Number of agents deactivated
    """

    def __init__(
        self,
        agent_id: str,
        blackboard: Optional[Blackboard] = None,
        agent_pool: Optional[AgentPool] = None
    ):
        """
        Initialize blackboard integration.

        Args:
            agent_id: Orchestrator agent ID (for authoring entries)
            blackboard: Blackboard instance
            agent_pool: Optional AgentPool for lifecycle management
        """
        self.agent_id = agent_id
        self.blackboard = blackboard
        self.agent_pool = agent_pool
        self.blackboard_posts = 0
        self.agents_activated = 0
        self.agents_deactivated = 0

    def post_task(
        self,
        structured: StructuredProblem,
        assigned_agent: str
    ) -> Task:
        """
        Post task to Blackboard for solver agents to pick up.

        Workflow:
        1. Create Task object with unique ID
        2. Activate assigned agent (STANDBY -> ACTIVE)
        3. Create Blackboard entry with task metadata
        4. Post entry to Blackboard
        5. Return Task for tracking

        Args:
            structured: Problem to post
            assigned_agent: Agent ID that should handle this

        Returns:
            Task object for tracking

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 145-152
        """
        # Create task
        task_id = f'task_{uuid.uuid4().hex[:8]}'
        task = Task(
            task_id=task_id,
            structured_problem=structured,
            status=EntryStatus.PENDING,
            assigned_agent=assigned_agent
        )

        if not self.blackboard:
            logger.warning(f"    No Blackboard available")
            task.status = EntryStatus.FAILED
            task.error = "No Blackboard available"
            return task

        # Activate the assigned agent (STANDBY -> ACTIVE)
        if self.agent_pool:
            logger.debug(f"    Activating agent: {assigned_agent}")
            self._activate_agent(assigned_agent)

        # Create Blackboard entry
        entry = create_entry(
            entry_type=EntryType.TASK,
            content=structured.omdoc_content,
            author_agent=self.agent_id,
            conversation_id=task_id,
            tags=[structured.domain.value, 'task', task_id],
            metadata={
                'problem_type': structured.problem_type.value,
                'domain': structured.domain.value,
                'raw_input': structured.raw_input,
                'assigned_agent': assigned_agent,
                'sympy_expr': str(structured.sympy_expr) if structured.sympy_expr else None,
                'operation': structured.metadata.get('operation', 'compute'),
                'variable': structured.metadata.get('variable', 'x')  # Default to 'x'
            }
        )

        # Post to Blackboard
        self.blackboard.post(entry)
        task.blackboard_entry_id = entry.entry_id

        self.blackboard_posts += 1

        return task

    def await_result(self, task: Task, timeout: float = 30.0) -> Any:
        """
        Wait for verified result from Verification Core.

        Polls Blackboard for result entry with STATUS: VERIFIED.

        Workflow:
        1. Poll blackboard for PARTIAL_RESULT entries with task_id tag
        2. Check status: VERIFIED (success) or FAILED (error)
        3. Deactivate agent (ACTIVE -> STANDBY)
        4. Return result or raise exception

        Args:
            task: Task to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Verified result

        Raises:
            RuntimeError: If no blackboard available or task failed
            TimeoutError: If result not received within timeout

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Line 154
        "Wait for verified result"
        """
        if not self.blackboard:
            raise RuntimeError("No Blackboard available")

        start_time = time.time()
        poll_interval = 0.5  # Poll every 500ms

        while time.time() - start_time < timeout:
            # Query Blackboard for result entries (PARTIAL_RESULT from solver)
            results = self.blackboard.query_entries(
                tags=[task.task_id],
                entry_type=EntryType.PARTIAL_RESULT
            )

            for result in results:
                if result.status == EntryStatus.VERIFIED:
                    # Found verified result!
                    logger.info(f"    [OK] Received verified result")
                    task.status = EntryStatus.VERIFIED
                    task.result = result.content

                    # Deactivate agent (ACTIVE -> STANDBY)
                    if task.assigned_agent:
                        self._deactivate_agent(task.assigned_agent, return_to_standby=True)

                    # Return result string from metadata if available
                    result_str = result.metadata.get('result_str')
                    if result_str:
                        return result_str
                    return result.content

                elif result.status == EntryStatus.FAILED:
                    # Task failed
                    logger.error(f"    [X] Task failed: {result.metadata.get('error')}")
                    task.status = EntryStatus.FAILED
                    task.error = result.metadata.get('error', 'Unknown error')

                    # Deactivate agent even on failure
                    if task.assigned_agent:
                        self._deactivate_agent(task.assigned_agent, return_to_standby=True)

                    raise RuntimeError(f"Task failed: {task.error}")

            # Wait before next poll
            time.sleep(poll_interval)

        # Timeout
        task.status = EntryStatus.FAILED
        task.error = "Timeout waiting for result"

        raise TimeoutError(f"Timeout waiting for verified result (task: {task.task_id})")

    def _activate_agent(self, agent_id: str) -> bool:
        """
        Activate a specific agent (STANDBY -> ACTIVE).

        For cognitive agents, this requests the VRAM slot from AMS.

        Args:
            agent_id: Agent to activate

        Returns:
            True if activated successfully
        """
        if not self.agent_pool:
            return True  # No pool = assume always active

        result = self.agent_pool.activate(agent_id)
        if result:
            self.agents_activated += 1
        return result

    def _deactivate_agent(self, agent_id: str, return_to_standby: bool = True) -> bool:
        """
        Deactivate an agent after task completion.

        Args:
            agent_id: Agent to deactivate
            return_to_standby: If True, keep in STANDBY for quick reuse

        Returns:
            True if deactivated successfully
        """
        if not self.agent_pool:
            return True  # No pool = no-op

        result = self.agent_pool.deactivate(agent_id, return_to_standby)
        if result:
            self.agents_deactivated += 1
        return result
