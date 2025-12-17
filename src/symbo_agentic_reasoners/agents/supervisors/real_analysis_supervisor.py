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
        self.beliefs.update(observation)
        if "task" in observation:
            task_type = self._classify_task(observation["task"])
            self.beliefs["task_type"] = task_type
            self.beliefs["target_specialist"] = task_type

    def deliberate(self) -> List[str]:
        self.desires = []
        if "task" in self.beliefs:
            self.desires.append("route_task")
        return self.desires

    def plan(self) -> List[Intention]:
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
        task_desc = task.get("description") or task.get("task", "")
        self.update_beliefs({"task": task_desc, **task})
        self.deliberate()
        self.plan()
        return self.execute_step()
