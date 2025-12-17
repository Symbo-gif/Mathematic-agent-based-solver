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
Interactive Guidance Liaison
=============================

Agent 4.2 of the Undecidability Navigator

Human-in-the-Loop interface agent. When Deep Search hits a theoretical
wall, generates a Proof State Summary and requests specific guidance
from a human mathematician.

Example output: "I am stuck on this lemma; should I apply induction
or contradiction?"

Acknowledgment: The system cannot be fully autonomous in undecidable
fields — this agent operationalizes that constraint.

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 4
Reference: Phase_6_Build_Order_Breakdown.md, Step 4
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import uuid


class GuidanceStatus(Enum):
    """Status of a guidance request"""
    PENDING = 'pending'
    RECEIVED = 'received'
    APPLIED = 'applied'
    EXPIRED = 'expired'
    REJECTED = 'rejected'


class StuckReason(Enum):
    """Reasons for being stuck"""
    NO_APPLICABLE_TACTICS = 'no_applicable_tactics'
    ALL_TACTICS_FAILED = 'all_tactics_failed'
    TIMEOUT_REACHED = 'timeout_reached'
    DEPTH_LIMIT = 'depth_limit'
    RESOURCE_EXHAUSTION = 'resource_exhaustion'
    UNDECIDABLE_DETECTED = 'undecidable_detected'
    LOW_VALUE_STATES = 'low_value_states'
    UNKNOWN = 'unknown'


@dataclass
class ProofStateSummary:
    """
    Summary of proof state for human guidance.

    Contains all information needed for a mathematician to understand
    the current state and provide useful guidance.

    Attributes:
        summary_id: Unique identifier
        problem_id: ID of the problem being proven
        current_goal: Current proof goal
        proven_subgoals: Successfully proven subgoals
        remaining_subgoals: Subgoals still to prove
        attempted_tactics: Tactics that have been tried
        failure_reasons: Why attempted tactics failed
        suggested_directions: System's suggested next steps
        human_query: Specific question for the human
        context: Additional context information
        stuck_reason: Why the system is stuck
    """
    summary_id: str
    problem_id: str
    current_goal: str
    proven_subgoals: List[str]
    remaining_subgoals: List[str]
    attempted_tactics: List[str]
    failure_reasons: List[str]
    suggested_directions: List[str]
    human_query: str
    context: Dict[str, Any] = field(default_factory=dict)
    stuck_reason: StuckReason = StuckReason.UNKNOWN
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'summary_id': self.summary_id,
            'problem_id': self.problem_id,
            'current_goal': self.current_goal,
            'proven_subgoals': self.proven_subgoals,
            'remaining_subgoals': self.remaining_subgoals,
            'attempted_tactics': self.attempted_tactics,
            'failure_reasons': self.failure_reasons,
            'suggested_directions': self.suggested_directions,
            'human_query': self.human_query,
            'stuck_reason': self.stuck_reason.value,
            'created_at': self.created_at.isoformat()
        }

    def format_for_display(self) -> str:
        """Format summary for human-readable display"""
        lines = [
            "=" * 60,
            "PROOF STATE SUMMARY - HUMAN GUIDANCE REQUESTED",
            "=" * 60,
            "",
            f"Problem ID: {self.problem_id}",
            f"Stuck Reason: {self.stuck_reason.value}",
            "",
            "CURRENT GOAL:",
            f"  {self.current_goal}",
            ""
        ]

        if self.proven_subgoals:
            lines.append("PROVEN SUBGOALS:")
            for sg in self.proven_subgoals[:5]:
                lines.append(f"  ✓ {sg}")
            lines.append("")

        if self.remaining_subgoals:
            lines.append("REMAINING SUBGOALS:")
            for sg in self.remaining_subgoals[:5]:
                lines.append(f"  ○ {sg}")
            lines.append("")

        if self.attempted_tactics:
            lines.append("ATTEMPTED TACTICS:")
            for t in self.attempted_tactics[:10]:
                lines.append(f"  • {t}")
            lines.append("")

        if self.failure_reasons:
            lines.append("FAILURE REASONS:")
            for r in self.failure_reasons[:5]:
                lines.append(f"  ✗ {r}")
            lines.append("")

        if self.suggested_directions:
            lines.append("SUGGESTED DIRECTIONS:")
            for i, s in enumerate(self.suggested_directions[:5], 1):
                lines.append(f"  {i}. {s}")
            lines.append("")

        lines.extend([
            "QUESTION FOR MATHEMATICIAN:",
            self.human_query,
            "",
            "=" * 60
        ])

        return "\n".join(lines)


@dataclass
class GuidanceRequest:
    """
    A request for human guidance.

    Attributes:
        request_id: Unique identifier
        summary: The proof state summary
        status: Current status of the request
        response: Human's response (when received)
        response_time: When the response was received
    """
    request_id: str
    summary: ProofStateSummary
    status: GuidanceStatus = GuidanceStatus.PENDING
    response: Optional[str] = None
    response_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'summary': self.summary.to_dict(),
            'status': self.status.value,
            'response': self.response,
            'created_at': self.created_at.isoformat()
        }


class InteractiveGuidanceLiaison:
    """
    Agent 4.2: Interactive Guidance Liaison - Human-in-the-Loop interface

    Manages communication with human mathematicians when the automated
    system hits theoretical walls. Generates clear, actionable summaries
    and incorporates human guidance into the search process.

    Key capabilities:
    - Proof state summarization
    - Guidance request generation
    - Human response handling
    - Guidance application tracking

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    def __init__(self, notification_callback: Callable = None, expiry_minutes: int = 60):
        """
        Initialize the Interactive Guidance Liaison.

        Args:
            notification_callback: Called when new guidance is needed
            expiry_minutes: Minutes until pending requests expire
        """
        self.notification_callback = notification_callback
        self.expiry_minutes = expiry_minutes

        # Request tracking
        self.pending_requests: Dict[str, GuidanceRequest] = {}
        self.completed_requests: Dict[str, GuidanceRequest] = {}
        self.received_guidance: Dict[str, str] = {}

        # Statistics
        self.stats = {
            'requests_created': 0,
            'guidance_received': 0,
            'guidance_applied': 0,
            'requests_expired': 0,
            'average_response_time_seconds': 0.0
        }
        self._response_times = []

    def request_guidance(
        self,
        problem,
        search_state: Dict[str, Any]
    ) -> GuidanceRequest:
        """
        Generate a guidance request when stuck.

        Args:
            problem: The problem being proven (CandidateConjecture or similar)
            search_state: Current state of the search

        Returns:
            GuidanceRequest with full summary
        """
        self.stats['requests_created'] += 1

        # Create summary
        summary = self._create_summary(problem, search_state)

        # Create request
        request = GuidanceRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            summary=summary
        )

        self.pending_requests[request.request_id] = request

        # Notify if callback registered
        if self.notification_callback:
            try:
                self.notification_callback(request)
            except (TypeError, ValueError, AttributeError, RuntimeError) as e:
                # Don't fail if notification fails - callback errors are non-critical
                pass

        return request

    def _create_summary(
        self,
        problem,
        search_state: Dict[str, Any]
    ) -> ProofStateSummary:
        """Create a proof state summary"""
        # Extract problem info
        if hasattr(problem, 'conjecture_id'):
            problem_id = problem.conjecture_id
            if hasattr(problem, 'source_theorem'):
                current_goal = problem.source_theorem.to_natural_language()
            else:
                current_goal = str(problem)
        else:
            problem_id = str(id(problem))
            current_goal = str(problem)

        # Extract search state info
        attempted_tactics = search_state.get('attempted_tactics', [])
        proven = search_state.get('proven', [])
        remaining = search_state.get('remaining', [current_goal])
        stuck_subgoals = search_state.get('stuck_subgoals', [])

        # Analyze failures
        failure_reasons = self._analyze_failures(search_state)

        # Determine stuck reason
        stuck_reason = self._determine_stuck_reason(search_state)

        # Generate suggestions
        suggestions = self._generate_suggestions(search_state, attempted_tactics)

        # Formulate human query
        human_query = self._formulate_query(
            current_goal, search_state, suggestions, stuck_reason
        )

        return ProofStateSummary(
            summary_id=f"sum_{uuid.uuid4().hex[:8]}",
            problem_id=problem_id,
            current_goal=current_goal,
            proven_subgoals=proven,
            remaining_subgoals=remaining if remaining else stuck_subgoals,
            attempted_tactics=attempted_tactics,
            failure_reasons=failure_reasons,
            suggested_directions=suggestions,
            human_query=human_query,
            context=search_state,
            stuck_reason=stuck_reason
        )

    def _analyze_failures(self, search_state: Dict[str, Any]) -> List[str]:
        """Analyze why the search failed"""
        reasons = []

        if search_state.get('timeout'):
            reasons.append("Search timed out before finding proof")

        if search_state.get('max_depth_reached'):
            reasons.append(f"Maximum search depth ({search_state.get('max_depth', 'unknown')}) reached")

        if search_state.get('max_expansions_reached'):
            reasons.append("Maximum node expansions reached")

        if search_state.get('stuck_subgoals'):
            subgoals = search_state['stuck_subgoals']
            if isinstance(subgoals, list) and subgoals:
                reasons.append(f"Stuck on subgoal: {subgoals[0][:100]}")

        if not search_state.get('attempted_tactics'):
            reasons.append("No applicable tactics were found for the goal")

        if search_state.get('all_branches_dead'):
            reasons.append("All search branches evaluated as dead ends by critic")

        if search_state.get('undecidable_detected'):
            reasons.append("Problem detected as potentially undecidable")

        if search_state.get('low_value'):
            reasons.append(f"All states have low value estimates (< {search_state.get('value_threshold', 0.1)})")

        return reasons if reasons else ["Unknown reason for being stuck"]

    def _determine_stuck_reason(self, search_state: Dict[str, Any]) -> StuckReason:
        """Determine the primary reason for being stuck"""
        if search_state.get('undecidable_detected'):
            return StuckReason.UNDECIDABLE_DETECTED
        if search_state.get('timeout'):
            return StuckReason.TIMEOUT_REACHED
        if search_state.get('max_depth_reached'):
            return StuckReason.DEPTH_LIMIT
        if search_state.get('max_expansions_reached'):
            return StuckReason.RESOURCE_EXHAUSTION
        if not search_state.get('attempted_tactics'):
            return StuckReason.NO_APPLICABLE_TACTICS
        if search_state.get('all_tactics_failed'):
            return StuckReason.ALL_TACTICS_FAILED
        if search_state.get('low_value'):
            return StuckReason.LOW_VALUE_STATES
        return StuckReason.UNKNOWN

    def _generate_suggestions(
        self,
        search_state: Dict[str, Any],
        attempted: List[str]
    ) -> List[str]:
        """Generate suggested proof directions"""
        suggestions = []
        tried = set(t.split()[0] if ' ' in t else t for t in attempted)

        # Suggest tactics not yet tried
        if 'induction' not in tried:
            suggestions.append("Try induction on a natural number variable")

        if 'cases' not in tried:
            suggestions.append("Try case analysis on a hypothesis or variable")

        if 'contradiction' not in tried and 'by_contra' not in tried:
            suggestions.append("Consider proof by contradiction")

        if 'simp' in tried and 'ring' not in tried:
            suggestions.append("Try the ring tactic for algebraic normalization")

        if 'linarith' not in tried:
            suggestions.append("Try linear arithmetic (linarith) for numeric inequalities")

        if 'have' not in tried:
            suggestions.append("Consider introducing an intermediate lemma with 'have'")

        # Suggest based on search state
        if search_state.get('low_value'):
            suggestions.append("Consider reformulating the goal or splitting it differently")

        if search_state.get('stuck_subgoals'):
            suggestions.append("Focus on the stuck subgoal - it may require a specific lemma")

        # General suggestions
        suggestions.append("Consider if the statement is actually provable as stated")
        suggestions.append("Look for a counterexample to check if the conjecture is false")

        return suggestions[:7]  # Limit suggestions

    def _formulate_query(
        self,
        goal: str,
        search_state: Dict[str, Any],
        suggestions: List[str],
        stuck_reason: StuckReason
    ) -> str:
        """Formulate a specific question for the human mathematician"""
        query_parts = [f"I am attempting to prove:\n  {goal[:200]}\n"]

        # Describe what was tried
        attempted = search_state.get('attempted_tactics', [])
        if attempted:
            query_parts.append(f"I have tried: {', '.join(attempted[:10])}")
        else:
            query_parts.append("I could not find any applicable tactics.")

        # Ask specific question based on stuck reason
        if stuck_reason == StuckReason.UNDECIDABLE_DETECTED:
            query_parts.append("\nThis problem may be undecidable. Should I:")
            query_parts.append("1. Search for a bounded/approximate solution")
            query_parts.append("2. Try a different formulation")
            query_parts.append("3. Abandon this conjecture")

        elif stuck_reason == StuckReason.NO_APPLICABLE_TACTICS:
            query_parts.append("\nNo tactics seem applicable. Please suggest:")
            query_parts.append("1. A specific tactic or lemma to try")
            query_parts.append("2. How to reformulate the goal")

        elif stuck_reason in [StuckReason.TIMEOUT_REACHED, StuckReason.RESOURCE_EXHAUSTION]:
            query_parts.append("\nSearch resources exhausted. Should I:")
            query_parts.append("1. Continue with more resources")
            query_parts.append("2. Try a different proof strategy")
            query_parts.append("3. Mark as requiring manual proof")

        else:
            query_parts.append("\nWhich approach should I try?")
            for i, s in enumerate(suggestions[:3], 1):
                query_parts.append(f"{i}. {s}")

        query_parts.append("\nOr please provide your own suggestion:")

        return "\n".join(query_parts)

    def receive_guidance(self, request_id: str, guidance: str) -> bool:
        """
        Receive guidance from human mathematician.

        Args:
            request_id: ID of the request being answered
            guidance: Human's guidance response

        Returns:
            True if guidance was successfully received
        """
        if request_id not in self.pending_requests:
            return False

        request = self.pending_requests[request_id]
        request.response = guidance
        request.response_time = datetime.now()
        request.status = GuidanceStatus.RECEIVED

        # Calculate response time
        response_seconds = (request.response_time - request.created_at).total_seconds()
        self._response_times.append(response_seconds)
        self.stats['average_response_time_seconds'] = sum(self._response_times) / len(self._response_times)

        # Move to completed
        self.completed_requests[request_id] = request
        del self.pending_requests[request_id]

        # Store guidance for retrieval
        self.received_guidance[request.summary.problem_id] = guidance

        self.stats['guidance_received'] += 1

        return True

    def get_guidance(self, problem_id: str) -> Optional[str]:
        """Get received guidance for a problem"""
        return self.received_guidance.get(problem_id)

    def mark_guidance_applied(self, request_id: str) -> bool:
        """Mark guidance as applied"""
        if request_id in self.completed_requests:
            self.completed_requests[request_id].status = GuidanceStatus.APPLIED
            self.stats['guidance_applied'] += 1
            return True
        return False

    def expire_old_requests(self):
        """Expire old pending requests"""
        now = datetime.now()
        expired = []

        for req_id, request in self.pending_requests.items():
            age_minutes = (now - request.created_at).total_seconds() / 60
            if age_minutes > self.expiry_minutes:
                expired.append(req_id)

        for req_id in expired:
            request = self.pending_requests[req_id]
            request.status = GuidanceStatus.EXPIRED
            self.completed_requests[req_id] = request
            del self.pending_requests[req_id]
            self.stats['requests_expired'] += 1

    def get_pending_count(self) -> int:
        """Get number of pending guidance requests"""
        return len(self.pending_requests)

    def get_pending_requests(self) -> List[GuidanceRequest]:
        """Get all pending guidance requests"""
        return list(self.pending_requests.values())

    def get_statistics(self) -> Dict[str, Any]:
        """Get liaison statistics"""
        return {
            **self.stats,
            'pending_requests': len(self.pending_requests),
            'completed_requests': len(self.completed_requests)
        }

    def reset(self):
        """Reset liaison state"""
        self.pending_requests.clear()
        self.completed_requests.clear()
        self.received_guidance.clear()
        self._response_times.clear()
        for key in self.stats:
            if key == 'average_response_time_seconds':
                self.stats[key] = 0.0
            else:
                self.stats[key] = 0

    def health_check(self) -> bool:
        """Check if liaison is healthy"""
        return True
