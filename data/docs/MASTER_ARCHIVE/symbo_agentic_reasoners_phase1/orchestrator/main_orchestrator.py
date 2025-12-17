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
PHASE 1 - STEP 2: THE CENTRAL NERVOUS SYSTEM (Main Orchestrator)
================================================================

The Main Orchestrator is the Tier 1 "General Contractor" whose sole job
is management, enforcing the strict separation of Problem Understanding
from Problem Solving.

CRITICAL CONSTRAINTS:
--------------------
1. NON-INTERVENTION DIRECTIVE: Orchestrator is FORBIDDEN from performing
   calculations. If it sees "2+2", it must delegate, never compute.

2. SEPARATION OF PLANNING FROM EXECUTION: Orchestrator plans, decomposes,
   and delegates. It NEVER solves.

COMPONENTS:
----------
1. Decomposition Engine: HTN (Hierarchical Task Network) logic
2. Dynamic Routing Logic: Queries Directory Facilitator for capable agents

REFERENCE:
---------
- Phase_1_Build_Order_Breakdown.md: Lines 108-160 (STEP 2)
- Phase 1 Coding Strategy: Section 3.2 "The Central Nervous System"
"""

import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import uuid

# Add parent to path for Phase 0 imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners_phase0.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners_phase0.memory.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners_phase0.core.fipa_acl import create_request, create_inform

# Import Phase 1 components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.problem_analysis import StructuredProblem, MathDomain


class NoAgentAvailableError(Exception):
    """Raised when no agent is available for a task"""
    pass


@dataclass
class Task:
    """
    Orchestrator task representation

    Represents a task that needs to be executed by a specialist agent.
    """
    task_id: str
    structured_problem: StructuredProblem
    status: EntryStatus
    assigned_agent: Optional[str] = None
    blackboard_entry_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class MainOrchestrator(BDIAgent):
    """
    Main Orchestrator - The Central Nervous System

    DIRECTIVE:
    ---------
    Tier 1 Agent that manages the problem-solving process. Enforces strict
    separation of Problem Understanding from Problem Solving.

    ARCHITECTURE:
    ------------
    - Decomposition Engine: HTN logic to break complex tasks into subtasks
    - Routing Logic: Queries Directory Facilitator to find capable agents
    - NON-INTERVENTION: NEVER computes, always delegates

    WORKFLOW:
    --------
    1. Receive StructuredProblem from Problem Analysis Team
    2. Decompose into subtasks (if complex)
    3. Query DF for capable agents by domain
    4. Post task to Blackboard with appropriate tags
    5. Wait for verified result from Verification Core
    6. Return result to user

    CRITICAL:
    --------
    The Orchestrator NEVER computes. The NON_INTERVENTION flag is
    hard-coded to True and cannot be changed.

    REFERENCE:
    ---------
    - Phase_1_Build_Order_Breakdown.md: Lines 123-156 (MainOrchestrator code)
    - Phase 1 Coding Strategy: "The Orchestrator must manage, never solve"
    """

    def __init__(
        self,
        agent_id: str = 'main_orchestrator_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Main Orchestrator

        Args:
            agent_id: Unique orchestrator identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # HARD-CODED CONSTRAINT: Non-Intervention Directive
        # This MUST remain True - Orchestrator NEVER computes
        self.NON_INTERVENTION = True

        # Task tracking
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []

        # Statistics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0

        print(f"[{self.agent_id}] Initialized")
        print(f"  NON-INTERVENTION directive: {self.NON_INTERVENTION} (HARD-CODED)")
        print(f"  Mode: Management only - NEVER computes")

    def process(self, structured: StructuredProblem) -> Any:
        """
        Process a structured problem

        This is the main entry point for the Orchestrator. It receives
        a StructuredProblem from the Problem Analysis Team and orchestrates
        the solution process.

        Args:
            structured: Fully parsed and classified problem

        Returns:
            Verified result from solver

        Raises:
            NoAgentAvailableError: If no agent can handle the problem

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 132-155 (process method)
        """
        print(f"\n[{self.agent_id}] Processing problem:")
        print(f"  Type: {structured.problem_type.value}")
        print(f"  Domain: {structured.domain.value}")
        print(f"  Input: '{structured.raw_input}'")

        # CRITICAL: Enforce NON-INTERVENTION
        if not self.NON_INTERVENTION:
            raise RuntimeError("FATAL: NON_INTERVENTION directive violated!")

        # Step 1: Decompose if complex (HTN logic)
        print(f"  [{self.agent_id}] Step 1: Decomposing task...")
        subtasks = self._decompose(structured)
        print(f"    Decomposed into {len(subtasks)} subtask(s)")

        # Step 2: Query DF for capable agent
        print(f"  [{self.agent_id}] Step 2: Finding capable agent...")
        service_type = f'math.{structured.domain.value.lower()}'
        agents = self._find_capable_agents(service_type)

        if not agents:
            error_msg = f"No agent available for domain: {structured.domain.value}"
            print(f"    ERROR: {error_msg}")
            raise NoAgentAvailableError(error_msg)

        print(f"    Found {len(agents)} capable agent(s): {[a.agent_id for a in agents]}")

        # Step 3: Post task to Blackboard
        print(f"  [{self.agent_id}] Step 3: Posting task to Blackboard...")
        task = self._post_task_to_blackboard(structured, agents[0].agent_id)
        print(f"    Posted as entry: {task.blackboard_entry_id}")

        # Step 4: Wait for verified result
        print(f"  [{self.agent_id}] Step 4: Waiting for verified result...")
        result = self._await_verified_result(task)

        return result

    def _decompose(self, structured: StructuredProblem) -> List[StructuredProblem]:
        """
        Decompose problem into subtasks using HTN logic

        This implements Hierarchical Task Network decomposition.
        For Phase 1, we only handle single-step tasks.
        Phase 2 will implement full HTN decomposition for complex problems.

        Args:
            structured: Problem to decompose

        Returns:
            List of subtasks (currently just [structured] for single-step)

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 157-160
        "Phase 1: single-step tasks only"
        """
        # Phase 1: Single-step tasks only
        # Phase 2 will implement:
        # - "simplify then integrate" -> [simplify, integrate]
        # - "factor then solve" -> [factor, solve]
        return [structured]

    def _find_capable_agents(self, service_type: str) -> List[Dict[str, Any]]:
        """
        Query Directory Facilitator for capable agents

        This implements the dynamic routing logic. The Orchestrator
        queries the DF to find agents with the required capability.

        Args:
            service_type: Service type to search for (e.g., 'math.calculus')

        Returns:
            List of agent service registrations

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 136-142
        "When Orchestrator identifies a 'Calculus' tag from the Analysis Team,
        it queries the DF for available agents with that capability"
        """
        if not self.df:
            print(f"    WARNING: No Directory Facilitator available")
            return []

        # Query DF for agents with this service type
        agents = self.df.search(service_type=service_type)

        return agents

    def _post_task_to_blackboard(
        self,
        structured: StructuredProblem,
        assigned_agent: str
    ) -> Task:
        """
        Post task to Blackboard for solver agents to pick up

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
            print(f"    WARNING: No Blackboard available")
            task.status = EntryStatus.FAILED
            task.error = "No Blackboard available"
            return task

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

        # Track task
        self.active_tasks[task_id] = task
        self.tasks_routed += 1

        return task

    def _await_verified_result(self, task: Task, timeout: float = 30.0) -> Any:
        """
        Wait for verified result from Verification Core

        Polls Blackboard for result entry with STATUS: VERIFIED

        Args:
            task: Task to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Verified result

        Raises:
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
                    print(f"    [OK] Received verified result")
                    task.status = EntryStatus.VERIFIED
                    task.result = result.content

                    # Move to completed
                    if task.task_id in self.active_tasks:
                        del self.active_tasks[task.task_id]
                    self.completed_tasks.append(task)
                    self.tasks_completed += 1

                    # Return result string from metadata if available
                    result_str = result.metadata.get('result_str')
                    if result_str:
                        return result_str
                    return result.content

                elif result.status == EntryStatus.FAILED:
                    # Task failed
                    print(f"    [X] Task failed: {result.metadata.get('error')}")
                    task.status = EntryStatus.FAILED
                    task.error = result.metadata.get('error', 'Unknown error')
                    self.tasks_failed += 1

                    raise RuntimeError(f"Task failed: {task.error}")

            # Wait before next poll
            time.sleep(poll_interval)

        # Timeout
        task.status = EntryStatus.FAILED
        task.error = "Timeout waiting for result"
        self.tasks_failed += 1

        raise TimeoutError(f"Timeout waiting for verified result (task: {task.task_id})")

    # BDI Implementation (simplified for Phase 1)
    def update_beliefs(self):
        """Update beliefs from environment"""
        # In Phase 1, we use direct method calls instead of full BDI loop
        # Phase 2 will implement full BDI reasoning
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions"""
        # In Phase 1, we use direct method calls
        # Phase 2 will implement full HTN planning
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        # In Phase 1, we use direct method calls
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'active_tasks': len(self.active_tasks),
            'non_intervention': self.NON_INTERVENTION
        })
        return stats


if __name__ == "__main__":
    """Test Main Orchestrator"""
    print("=" * 80)
    print("PHASE 1 - STEP 2: MAIN ORCHESTRATOR TEST")
    print("=" * 80)
    print()

    # Initialize Phase 0 infrastructure
    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Orchestrator
    orchestrator = MainOrchestrator(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test case: Try to process (will fail since no solver registered yet)
    print("Test: Attempting to process problem (will fail - no solver yet)...")
    print()

    from agents.problem_analysis import ProblemAnalysisTeam

    team = ProblemAnalysisTeam()
    structured = team.process("Calculate the derivative of x**2 + 1")

    print()
    print("Attempting orchestration...")
    try:
        result = orchestrator.process(structured)
        print(f"Result: {result}")
    except NoAgentAvailableError as e:
        print(f"Expected error: {e}")
        print("(This is correct - no solver agent registered yet)")

    print()
    print("=" * 80)
    print("MAIN ORCHESTRATOR TEST COMPLETE")
    print("=" * 80)
    print()
    print("Statistics:")
    import json
    print(json.dumps(orchestrator.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
