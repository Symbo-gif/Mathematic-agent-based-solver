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
REAL ANALYSIS SUPERVISOR (Tier 2)
===================================

The Real Analysis Supervisor acts as the "Foreman" for all real analysis tasks.
Routes tasks to appropriate specialists based on task analysis.

ROUTING LOGIC:
-------------
- Measure/integration/Lp spaces → MeasureTheorySpecialist
- Metric spaces/completeness/fixed points → MetricSpaceSpecialist
- Sequences/series/convergence tests → SequencesSeriesSpecialist

NO SYMPY - Pure Python/NumPy implementation.
"""

import re
from typing import List, Dict, Any, Optional
import uuid

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)


class RealAnalysisSupervisor(BDIAgent):
    """
    Real Analysis Supervisor - Tier 2 Strategic Router

    Routes real analysis tasks to:
    - MeasureTheorySpecialist
    - MetricSpaceSpecialist
    - SequencesSeriesSpecialist
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        blackboard: Optional[Blackboard] = None,
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        specialists: Optional[Dict[str, Any]] = None
    ):
        """Initialize Real Analysis Supervisor.

        Sets up routing infrastructure for real analysis problems.
        Uses lazy initialization for specialists.

        Args:
            agent_id: Unique identifier (auto-generated if None)
            blackboard: Shared memory for agent communication
            directory_facilitator: Service registry for finding specialists
            specialists: Pre-initialized specialist dict (optional)

        Example:
            >>> supervisor = RealAnalysisSupervisor()
            >>> result = supervisor.handle_task({"task": "Apply dominated convergence theorem"})
        """
        super().__init__(
            agent_id=agent_id or f"real_analysis_supervisor_{uuid.uuid4().hex[:8]}",
            role="real_analysis_supervisor"
        )

        self.blackboard = blackboard
        self.df = directory_facilitator
        self._specialists = specialists or {}
        self._initialized = False

        self._task_patterns = {
            "measure": [
                r"measure", r"lebesgue", r"integra", r"l\^?p\s", r"lp\s+space",
                r"sigma[\s-]*finite", r"measurable", r"dominated\s+convergence",
                r"monotone\s+convergence", r"fatou", r"fubini", r"product\s+measure"
            ],
            "metric": [
                r"metric\s+space", r"complete", r"compact", r"continu",
                r"fixed\s+point", r"banach", r"brouwer", r"lipschitz",
                r"open\s+set", r"closed\s+set", r"cauchy"
            ],
            "sequence": [
                r"sequence", r"series", r"converg", r"ratio\s+test",
                r"root\s+test", r"alternating", r"power\s+series",
                r"radius.*convergence", r"uniform.*converg", r"limsup", r"liminf"
            ]
        }

    def _ensure_initialized(self):
        """Lazy initialization of specialists to avoid circular imports.

        Creates MeasureTheorySpecialist, MetricSpaceSpecialist, and SequencesSeriesSpecialist on first use.

        Notes:
            - Called automatically before routing tasks
            - Prevents import cycles at module load time
            - Specialists are reused across multiple tasks
        """
        if self._initialized:
            return

        from symbo_agentic_reasoners.agents.specialists.real_analysis import (
            MeasureTheorySpecialist,
            MetricSpaceSpecialist,
            SequencesSeriesSpecialist
        )

        if "measure" not in self._specialists:
            self._specialists["measure"] = MeasureTheorySpecialist()
        if "metric" not in self._specialists:
            self._specialists["metric"] = MetricSpaceSpecialist()
        if "sequence" not in self._specialists:
            self._specialists["sequence"] = SequencesSeriesSpecialist()

        self._initialized = True

    def _classify_task(self, task_description: str) -> str:
        """Classify task into specialist category using keyword matching.

        Categories:
        - measure: Lebesgue integration, Lp spaces (MeasureTheorySpecialist)
        - metric: Metric spaces, completeness, fixed points (MetricSpaceSpecialist)
        - sequence: Sequences, series, convergence tests (SequencesSeriesSpecialist)

        Args:
            task_description: Natural language task description

        Returns:
            Task type string ('measure', 'metric', or 'sequence')

        Example:
            >>> supervisor = RealAnalysisSupervisor()
            >>> supervisor._classify_task("Apply dominated convergence theorem")
            'measure'
            >>> supervisor._classify_task("Test series convergence using ratio test")
            'sequence'

        Notes:
            - Uses regex pattern matching on task keywords
            - Defaults to 'sequence' if no patterns match
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
            return "sequence"

        for task_type, score in scores.items():
            if score == max_score:
                return task_type

        return "sequence"

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
            self.beliefs["target_specialist"] = task_type

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
                task_type = self.beliefs.get("task_type", "sequence")
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
            return {"status": "no_intentions", "agent": self.agent_id}

        current = self.intentions[0]

        if current.goal == "route_task":
            result = self._route_task()
            current.status = "completed"
            self.intentions.pop(0)
            return result

        return {"status": "unknown_goal", "goal": current.goal}

    def _route_task(self) -> Dict[str, Any]:
        """Route task to appropriate specialist based on classification.

        Delegates task execution to MeasureTheory, MetricSpace, or SequencesSeries specialists.

        Returns:
            Dict containing routing status and specialist results

        Example:
            Result structure:
            {
                "status": "routed",
                "task_type": "measure",
                "specialist": "MeasureTheorySpecialist",
                "result": {...}  # Specialist's output
            }

        Notes:
            - Shares beliefs with specialist via update_beliefs()
            - Specialist executes full BDI cycle (deliberate → execute)
            - Returns error if specialist not found
        """
        task_type = self.beliefs.get("task_type", "sequence")
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
            >>> supervisor = RealAnalysisSupervisor()
            >>> result = supervisor.handle_task({
            ...     "task": "Prove convergence using monotone convergence theorem",
            ...     "function": "f_n(x) = x/n"
            ... })
            >>> result["status"]
            'routed'
            >>> result["task_type"]
            'measure'

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
