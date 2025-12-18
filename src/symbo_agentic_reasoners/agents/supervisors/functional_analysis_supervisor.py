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
FUNCTIONAL ANALYSIS SUPERVISOR (Tier 2)
=========================================

Routes functional analysis tasks to appropriate specialists.

ROUTING LOGIC:
-------------
- Norms/dual spaces/Banach theorems → BanachSpaceSpecialist
- Inner products/orthogonality/projections → HilbertSpaceSpecialist
- Spectrum/resolvent/operator theory → OperatorTheorySpecialist

NO SYMPY - Pure Python/NumPy implementation.
"""

import re
from typing import List, Dict, Any, Optional
import uuid

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class FunctionalAnalysisSupervisor(BDIAgent):
    """
    Functional Analysis Supervisor - Tier 2 Strategic Router
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        blackboard: Optional[Blackboard] = None,
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        specialists: Optional[Dict[str, Any]] = None
    ):
        """Initialize Functional Analysis Supervisor.

        Sets up routing infrastructure for functional analysis problems.
        Uses lazy initialization for specialists.

        Args:
            agent_id: Unique identifier (auto-generated if None)
            blackboard: Shared memory for agent communication
            directory_facilitator: Service registry for finding specialists
            specialists: Pre-initialized specialist dict (optional)

        Example:
            >>> supervisor = FunctionalAnalysisSupervisor()
            >>> result = supervisor.handle_task({"task": "Verify Banach space axioms"})
        """
        super().__init__(
            agent_id=agent_id or f"functional_analysis_supervisor_{uuid.uuid4().hex[:8]}",
            role="functional_analysis_supervisor"
        )

        self.blackboard = blackboard
        self.df = directory_facilitator
        self._specialists = specialists or {}
        self._initialized = False

        self._task_patterns = {
            "banach": [
                r"banach", r"\bnorm\b", r"bounded\s+operator", r"dual\s+space",
                r"hahn[\s-]*banach", r"open\s+mapping", r"closed\s+graph",
                r"uniform\s+boundedness", r"lipschitz"
            ],
            "hilbert": [
                r"hilbert", r"inner\s+product", r"orthogonal", r"orthonormal",
                r"gram[\s-]*schmidt", r"projection", r"fourier", r"parseval",
                r"bessel", r"riesz\s+representation"
            ],
            "operator": [
                r"spectrum", r"spectral", r"resolvent", r"eigenvalue",
                r"self[\s-]*adjoint", r"unitary", r"normal\s+operator",
                r"compact\s+operator", r"functional\s+calculus"
            ]
        }

    def _ensure_initialized(self):
        """Lazy initialization of specialists to avoid circular imports.

        Creates BanachSpaceSpecialist, HilbertSpaceSpecialist, and OperatorTheorySpecialist on first use.

        Notes:
            - Called automatically before routing tasks
            - Prevents import cycles at module load time
            - Specialists are reused across multiple tasks
        """
        if self._initialized:
            return

        from symbo_agentic_reasoners.agents.specialists.functional_analysis import (
            BanachSpaceSpecialist,
            HilbertSpaceSpecialist,
            OperatorTheorySpecialist
        )

        if "banach" not in self._specialists:
            self._specialists["banach"] = BanachSpaceSpecialist()
        if "hilbert" not in self._specialists:
            self._specialists["hilbert"] = HilbertSpaceSpecialist()
        if "operator" not in self._specialists:
            self._specialists["operator"] = OperatorTheorySpecialist()

        self._initialized = True

    def _classify_task(self, task_description: str) -> str:
        """Classify task into specialist category using keyword matching.

        Categories:
        - banach: Norms, dual spaces, bounded operators (BanachSpaceSpecialist)
        - hilbert: Inner products, orthogonality, projections (HilbertSpaceSpecialist)
        - operator: Spectrum, resolvent, eigenvalues (OperatorTheorySpecialist)

        Args:
            task_description: Natural language task description

        Returns:
            Task type string ('banach', 'hilbert', or 'operator')

        Example:
            >>> supervisor = FunctionalAnalysisSupervisor()
            >>> supervisor._classify_task("Apply Gram-Schmidt orthogonalization")
            'hilbert'
            >>> supervisor._classify_task("Compute spectrum of operator")
            'operator'

        Notes:
            - Uses regex pattern matching on task keywords
            - Defaults to 'hilbert' if no patterns match
            - Scores each category by number of keyword matches
        """
        task_lower = task_description.lower()
        scores = {task_type: 0 for task_type in self._task_patterns}

        for task_type, patterns in self._task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    scores[task_type] += 1

        max_score = max(scores.values())
        if max_score == 0:
            return "hilbert"

        for task_type, score in scores.items():
            if score == max_score:
                return task_type

        return "hilbert"

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs with new observations.

        Classifies task type if task description is provided.

        Args:
            observation: Dict containing task information and parameters

        Notes:
            - Part of BDI (Belief-Desire-Intention) architecture
            - Automatically classifies task into specialist category
            - Updates stored as key-value pairs in self.beliefs
        """
        self.beliefs.update(observation)
        if "task" in observation:
            task_type = self._classify_task(observation["task"])
            self.beliefs["task_type"] = task_type

    def deliberate(self) -> List[str]:
        """Generate desires (goals) based on current beliefs.

        Returns:
            List of goal strings (e.g., ['route_task'])

        Notes:
            - Part of BDI architecture
            - Currently generates single 'route_task' goal if task present
            - Desires are transformed into intentions by plan()
        """
        self.desires = []
        if "task" in self.beliefs:
            self.desires.append("route_task")
        return self.desires

    def plan(self) -> List[Intention]:
        """Create concrete intentions from desires.

        Converts abstract goals into actionable plans with priorities.

        Returns:
            List of Intention objects sorted by priority

        Notes:
            - Part of BDI architecture
            - Creates routing plan for each 'route_task' desire
            - Higher priority (lower number) intentions execute first
        """
        intentions = []
        for goal in self.desires:
            if goal == "route_task":
                task_type = self.beliefs.get("task_type", "hilbert")
                intentions.append(Intention(
                    goal=goal,
                    plan=[f"Route to {task_type} specialist"],
                    priority=1
                ))
        self.intentions = sorted(intentions, key=lambda x: x.priority)
        return self.intentions

    def execute_step(self) -> Dict[str, Any]:
        """Execute next step in current intention.

        Processes the highest-priority intention and delegates to specialists.

        Returns:
            Dict with execution results including status and specialist output

        Notes:
            - Part of BDI architecture
            - Auto-generates intentions if none exist
            - Removes completed intentions from queue
            - Returns error status for unknown goals
        """
        self._ensure_initialized()

        if not self.intentions:
            self.deliberate()
            self.plan()

        if not self.intentions:
            return {"status": "no_intentions"}

        current = self.intentions[0]

        if current.goal == "route_task":
            result = self._route_task()
            current.status = "completed"
            self.intentions.pop(0)
            return result

        return {"status": "unknown_goal", "goal": current.goal}

    def _route_task(self) -> Dict[str, Any]:
        """Route task to appropriate specialist based on classification.

        Delegates task execution to Banach, Hilbert, or Operator specialists.

        Returns:
            Dict containing routing status and specialist results

        Example:
            Result structure:
            {
                "status": "routed",
                "task_type": "hilbert",
                "specialist": "HilbertSpaceSpecialist",
                "result": {...}  # Specialist's output
            }

        Notes:
            - Shares beliefs with specialist via update_beliefs()
            - Specialist executes full BDI cycle (deliberate → execute)
            - Returns error if specialist not found
        """
        task_type = self.beliefs.get("task_type", "hilbert")
        specialist = self._specialists.get(task_type)

        if specialist is None:
            return {"status": "error", "error": f"No specialist for: {task_type}"}

        specialist.update_beliefs(self.beliefs)
        specialist.deliberate()
        result = specialist.execute_step()

        return {
            "status": "routed",
            "task_type": task_type,
            "specialist": type(specialist).__name__,
            "result": result
        }

    def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for task processing.

        Orchestrates full BDI cycle: beliefs → desires → intentions → execution.

        Args:
            task: Dict with 'task' or 'description' key plus parameters

        Returns:
            Dict with routing results and specialist output

        Example:
            >>> supervisor = FunctionalAnalysisSupervisor()
            >>> result = supervisor.handle_task({
            ...     "task": "Compute operator spectrum",
            ...     "matrix": [[1, 2], [2, 1]]
            ... })
            >>> result["status"]
            'routed'
            >>> result["task_type"]
            'operator'

        Notes:
            - Convenience method combining update_beliefs, deliberate, plan, execute
            - Accepts flexible task dict format
            - Automatically routes to correct specialist
        """
        task_desc = task.get("description") or task.get("task", "")
        self.update_beliefs({"task": task_desc, **task})
        self.deliberate()
        self.plan()
        return self.execute_step()
