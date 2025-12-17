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
Orchestration Learning and Memory
===================================

Learning and memory management for orchestrator.

Implements 'look-before-leap' pattern - check cache before solving.
Records successful solutions for future retrieval.

Responsibilities:
- Cache checking (look_before_leap)
- Solution recording for future retrieval
- Integration with Knowledge Management Team (Phase 3 feature)
"""

import logging
import uuid
from typing import Optional

from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem

# Optional import - KnowledgeManagementTeam may not be available
try:
    from symbo_agentic_reasoners.middleware.knowledge_management import (
        KnowledgeManagementTeam, RetrievalConfidence
    )
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False
    KnowledgeManagementTeam = None
    RetrievalConfidence = None

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.learning')


class LearningMemory:
    """
    Learning and memory management for orchestrator.

    Implements 'look-before-leap' pattern - check cache before solving.
    Records successful solutions for future retrieval (Phase 3 feature).

    Requires:
        - KnowledgeManagementTeam (optional, from Phase 3)
        - Vector database backend (optional)

    Statistics:
        cache_hits: Number of problems solved from memory
        cache_misses: Number of problems not found in memory
        solutions_recorded: Number of new solutions stored
    """

    def __init__(
        self,
        agent_id: str,
        knowledge_team: Optional['KnowledgeManagementTeam'] = None
    ):
        """
        Initialize learning and memory management.

        Args:
            agent_id: Orchestrator agent ID (for logging)
            knowledge_team: Optional KnowledgeManagementTeam instance
        """
        self.agent_id = agent_id
        self.knowledge_team = knowledge_team
        self.cache_hits = 0
        self.cache_misses = 0
        self.solutions_recorded = 0

    def look_before_leap(self, structured: StructuredProblem) -> Optional[str]:
        """
        Check memory for existing solutions before computing.

        The "Look-Before-You-Leap" protocol queries the knowledge management
        team to see if we've already solved a similar problem.

        This is a Phase 3 feature that requires:
        - KnowledgeManagementTeam to be initialized
        - Vector database backend

        Args:
            structured: The problem to look up

        Returns:
            Cached result string if found, None otherwise

        Note:
            If knowledge_team is not available, always returns None
            (graceful degradation - solve from scratch)
        """
        if not self.knowledge_team or not KNOWLEDGE_AVAILABLE:
            self.cache_misses += 1
            return None

        try:
            # Query the retrieval specialist
            retrieval_result = self.knowledge_team.look_before_leap(
                structured.raw_input
            )

            # Check if the retrieval found a high-confidence match
            if retrieval_result.should_skip_solving():
                logger.debug(
                    f"    [LEARNING] Found cached solution with confidence: "
                    f"{retrieval_result.confidence}"
                )
                self.cache_hits += 1
                return retrieval_result.theorem_content

            self.cache_misses += 1
            return None

        except Exception as e:
            logger.debug(f"    [LEARNING] Lookup failed: {e}")
            self.cache_misses += 1
            return None

    def record_solution(self, structured: StructuredProblem, result: str) -> None:
        """
        Record a successful solution for future retrieval.

        Stores the problem and its solution in the vector database so
        that similar future problems can be resolved from memory.

        This is a Phase 3 feature that requires:
        - KnowledgeManagementTeam to be initialized
        - Vector database backend

        Args:
            structured: The original problem
            result: The computed result

        Note:
            If knowledge_team is not available, this is a no-op
            (graceful degradation - no learning occurs)
        """
        if not self.knowledge_team or not KNOWLEDGE_AVAILABLE:
            return

        try:
            # Generate a conversation ID for this solution
            conversation_id = f"solution_{uuid.uuid4().hex[:8]}"

            # Record the result
            entry_id = self.knowledge_team.record_result(
                conversation_id=conversation_id,
                problem=structured.raw_input,
                result=result,
                proof_trace=None  # Could add solving trace here in future
            )

            self.solutions_recorded += 1
            logger.debug(f"    [LEARNING] Recorded solution: {entry_id}")

        except Exception as e:
            logger.debug(f"    [LEARNING] Recording failed: {e}")
