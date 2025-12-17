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
Orchestration Decomposition Engine
===================================

HTN (Hierarchical Task Network) decomposition logic for breaking down
complex problems into subtasks.

Responsibilities:
- Problem decomposition using HTN logic
- Agent pool management (wake/activate/deactivate)
- Domain-based agent selection
"""

import logging
from typing import List, Optional
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem
from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.decomposition')


class DecompositionEngine:
    """
    HTN-based problem decomposition engine.

    Decomposes complex problems into subtasks and manages agent lifecycle.
    """

    def __init__(self, agent_pool: Optional[AgentPool] = None):
        """
        Initialize decomposition engine.

        Args:
            agent_pool: Optional agent pool for lifecycle management
        """
        self.agent_pool = agent_pool
        self.agents_woken = 0
        self.agents_activated = 0

    def decompose(self, structured: StructuredProblem) -> List[StructuredProblem]:
        """
        Decompose problem into subtasks using HTN logic.

        This implements Hierarchical Task Network decomposition.
        For Phase 1, we only handle single-step tasks.
        Phase 2 will implement full HTN decomposition for complex problems.

        Args:
            structured: Problem to decompose

        Returns:
            List of subtasks (currently just [structured] for single-step)

        Reference:
            Phase_1_Build_Order_Breakdown.md: Lines 157-160
            "Phase 1: single-step tasks only"
        """
        # Phase 1: Single-step tasks only
        # Phase 2 will implement:
        # - "simplify then integrate" -> [simplify, integrate]
        # - "factor then solve" -> [factor, solve]
        return [structured]

    def wake_domain_agents(self, domain: str) -> List[str]:
        """
        Wake agents for a problem domain using AgentPool.

        This brings agents from DORMANT -> STANDBY state, preparing
        them for quick activation without allocating VRAM yet.

        Args:
            domain: Problem domain (e.g., 'algebra', 'calculus')

        Returns:
            List of agent IDs that were woken
        """
        if not self.agent_pool:
            return []

        woken = self.agent_pool.wake_for_domain(domain)
        self.agents_woken += len(woken)
        logger.debug(f"Woke {len(woken)} agents for domain '{domain}'")
        return woken

    def activate_agent(self, agent_id: str) -> bool:
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
            logger.debug(f"Activated agent '{agent_id}'")
        else:
            logger.warning(f"Failed to activate agent '{agent_id}'")
        return result

    def deactivate_agent(self, agent_id: str, return_to_standby: bool = True) -> bool:
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
            logger.debug(f"Deactivated agent '{agent_id}' (standby={return_to_standby})")
        return result


__all__ = [
    'DecompositionEngine',
]
