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
COMPLEX ANALYSIS SUPERVISOR (Tier 2)
======================================

The Complex Analysis Supervisor acts as the "Foreman" for all complex analysis tasks.
Its primary logic is routing strategy, not direct computation.

DIRECTIVE:
---------
Route high-level complex analysis tasks to appropriate specialists based on:
- Task type (analyticity, residues, mappings, integrals)
- Problem structure analysis
- Specialist capability matching

ROUTING LOGIC:
-------------
- Analyticity/singularities/Laurent series → Analytic Functions Specialist
- Residue computation/real integrals via residues → Residue Calculus Specialist
- Domain mappings/Möbius transforms → Conformal Mapping Specialist
- Complex line integrals/Cauchy formula → Contour Integration Specialist

NO SYMPY - Pure Python/NumPy implementation.
"""

import sys
import os
from typing import List, Dict, Any, Optional
import uuid
import re

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)


class ComplexAnalysisSupervisor(BDIAgent):
    """
    Complex Analysis Supervisor - Tier 2 Strategic Router

    ROLE:
    ----
    Acts as foreman for all complex analysis tasks. Routes tasks to appropriate
    specialists based on task analysis.

    CRITICAL:
    --------
    Like all supervisors, this agent NEVER computes. It only:
    1. Analyzes task requirements
    2. Determines task type
    3. Routes to appropriate specialist
    4. Aggregates results

    ROUTING STRATEGY:
    ----------------
    - Analyticity/Cauchy-Riemann/singularities → AnalyticFunctionsSpecialist
    - Residue computation/contour via residue theorem → ResidueCalculusSpecialist
    - Conformal maps/Möbius/Schwarz-Christoffel → ConformalMappingSpecialist
    - Line integrals/Cauchy formula → ContourIntegrationSpecialist
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        blackboard: Optional[Blackboard] = None,
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        specialists: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Complex Analysis Supervisor.

        Args:
            agent_id: Unique identifier (auto-generated if not provided)
            blackboard: Shared communication channel
            directory_facilitator: Service registry
            specialists: Pre-initialized specialists (lazy loaded if not provided)
        """
        super().__init__(
            agent_id=agent_id or f"complex_analysis_supervisor_{uuid.uuid4().hex[:8]}",
            role="complex_analysis_supervisor"
        )

        self.blackboard = blackboard
        self.df = directory_facilitator
        self._specialists = specialists or {}
        self._initialized = False

        # Task type detection patterns
        self._task_patterns = {
            "analytic": [
                r"analytic", r"cauchy[\s-]*riemann", r"singularit",
                r"laurent", r"power\s+series", r"holomorphic",
                r"meromorphic", r"pole", r"essential", r"removable",
                r"zero.*order", r"branch\s+point"
            ],
            "residue": [
                r"residue", r"real\s+integral.*complex", r"improper\s+integral",
                r"integral.*infinity", r"argument\s+principle",
                r"winding\s+number", r"\bpole\b.*integral"
            ],
            "conformal": [
                r"conformal", r"mobius", r"möbius", r"linear\s+fractional",
                r"schwarz[\s-]*christoffel", r"bilinear", r"automorphism",
                r"riemann\s+mapping", r"domain.*map", r"half[\s-]*plane.*disk"
            ],
            "contour": [
                r"contour\s+integral", r"line\s+integral", r"path\s+integral",
                r"cauchy\s+integral", r"arc\s+length", r"parameteriz"
            ]
        }

    def _ensure_initialized(self):
        """Lazy initialization of specialists."""
        if self._initialized:
            return

        # Import specialists lazily
        from symbo_agentic_reasoners.agents.specialists.complex_analysis import (
            AnalyticFunctionsSpecialist,
            ResidueCalculusSpecialist,
            ConformalMappingSpecialist,
            ContourIntegrationSpecialist
        )

        if "analytic" not in self._specialists:
            self._specialists["analytic"] = AnalyticFunctionsSpecialist()
        if "residue" not in self._specialists:
            self._specialists["residue"] = ResidueCalculusSpecialist()
        if "conformal" not in self._specialists:
            self._specialists["conformal"] = ConformalMappingSpecialist()
        if "contour" not in self._specialists:
            self._specialists["contour"] = ContourIntegrationSpecialist()

        self._initialized = True

    def _classify_task(self, task_description: str) -> str:
        """
        Classify task to determine which specialist should handle it.

        Args:
            task_description: Natural language task description

        Returns:
            Specialist type: "analytic", "residue", "conformal", or "contour"
        """
        task_lower = task_description.lower()
        scores = {task_type: 0 for task_type in self._task_patterns}

        for task_type, patterns in self._task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    scores[task_type] += 1

        # Return highest scoring type, default to "contour" for general integrals
        max_score = max(scores.values())
        if max_score == 0:
            return "contour"  # Default

        for task_type, score in scores.items():
            if score == max_score:
                return task_type

        return "contour"

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """
        Update beliefs based on new observation.

        Args:
            observation: New information about the environment
        """
        self.beliefs.update(observation)

        # Analyze task if present
        if "task" in observation:
            task_type = self._classify_task(observation["task"])
            self.beliefs["task_type"] = task_type
            self.beliefs["target_specialist"] = task_type

    def deliberate(self) -> List[str]:
        """
        Deliberate on goals based on current beliefs.

        Returns:
            List of goal names
        """
        self.desires = []

        if "task" in self.beliefs:
            self.desires.append("route_task")

        if "results" in self.beliefs and "aggregate" in self.beliefs:
            self.desires.append("aggregate_results")

        return self.desires

    def plan(self) -> List[Intention]:
        """
        Create plan to achieve goals.

        Returns:
            List of intentions
        """
        intentions = []

        for goal in self.desires:
            if goal == "route_task":
                task_type = self.beliefs.get("task_type", "contour")
                intentions.append(Intention(
                    goal=goal,
                    plan=[
                        f"1. Identify task type: {task_type}",
                        f"2. Route to {task_type} specialist",
                        "3. Await results"
                    ],
                    priority=1
                ))
            elif goal == "aggregate_results":
                intentions.append(Intention(
                    goal=goal,
                    plan=[
                        "1. Collect specialist results",
                        "2. Validate results",
                        "3. Format response"
                    ],
                    priority=2
                ))

        self.intentions = sorted(intentions, key=lambda x: x.priority)
        return self.intentions

    def execute_step(self) -> Dict[str, Any]:
        """
        Execute one reasoning step.

        Returns:
            Result dictionary
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

        elif current.goal == "aggregate_results":
            result = self._aggregate_results()
            current.status = "completed"
            self.intentions.pop(0)
            return result

        return {"status": "unknown_goal", "goal": current.goal}

    def _route_task(self) -> Dict[str, Any]:
        """Route task to appropriate specialist."""
        task_type = self.beliefs.get("task_type", "contour")
        specialist = self._specialists.get(task_type)

        if specialist is None:
            return {
                "status": "error",
                "error": f"No specialist available for task type: {task_type}"
            }

        # Update specialist beliefs with task context
        specialist.update_beliefs(self.beliefs)
        specialist.deliberate()

        # Execute specialist
        result = specialist.execute_step()

        return {
            "status": "routed",
            "task_type": task_type,
            "specialist": type(specialist).__name__,
            "result": result
        }

    def _aggregate_results(self) -> Dict[str, Any]:
        """Aggregate results from specialists."""
        results = self.beliefs.get("results", [])

        if not results:
            return {"status": "no_results"}

        return {
            "status": "aggregated",
            "results": results,
            "count": len(results)
        }

    def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        High-level task handling entry point.

        Args:
            task: Task dictionary with at minimum a "description" or "task" key

        Returns:
            Result dictionary
        """
        # Update beliefs with task
        task_desc = task.get("description") or task.get("task", "")
        self.update_beliefs({"task": task_desc, **task})

        # Execute BDI cycle
        self.deliberate()
        self.plan()
        result = self.execute_step()

        return result

    def register_services(self):
        """Register supervisor services with directory facilitator."""
        if self.df is None:
            return

        services = [
            "complex_analysis_routing",
            "analyticity_analysis",
            "residue_computation",
            "conformal_mapping",
            "contour_integration"
        ]

        for service in services:
            registration = create_service_registration(
                agent_id=self.agent_id,
                service_type=service,
                capabilities={
                    "role": "supervisor",
                    "domain": "complex_analysis",
                    "tier": 2
                }
            )
            self.df.register_service(registration)
