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
CONFIDENCE FALLBACK MECHANISM
=============================

Step 3 of Phase 5 Build Order: Safety Valve for Hybrid Deployment

OBJECTIVE:
---------
Implement a safety valve on the Distilled Model. If the Student generates
a solution with a low confidence score (below configurable threshold) or
fails the Ax-Prover verification check, the system automatically escalates
the problem to the full MAS.

This creates a seamless "Fail-Over" to higher intelligence.

FALLBACK TRIGGERS:
-----------------
1. Confidence < 0.7 (configurable)
2. Verification failure (Ax-Prover rejects)
3. Timeout (Student taking too long)
4. Explicit uncertainty markers in answer
5. Query complexity increases during solving

ESCALATION FLOW:
---------------
1. Student attempts query
2. Fallback mechanism monitors result
3. If trigger condition met -> escalate to Teacher
4. Teacher result marked as "escalated" for priority learning
5. Evolutionary Flywheel captures for retraining

REFERENCE:
---------
- Phase_5_Build_Order_Breakdown.md: Section 4.3.2
- phase5_symbo_integration_architecture.py: handle_student_failure
"""

import os
import sys
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from dataclasses import dataclass

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class EscalationReason(Enum):
    """Reasons for escalating from Student to Teacher"""
    LOW_CONFIDENCE = "low_confidence"
    VERIFICATION_FAILED = "verification_failed"
    TIMEOUT = "timeout"
    UNCERTAINTY_MARKERS = "uncertainty_markers"
    COMPLEXITY_INCREASE = "complexity_increase"
    EXPLICIT_REQUEST = "explicit_request"
    DOMAIN_MISMATCH = "domain_mismatch"


@dataclass
class EscalationEvent:
    """Records an escalation event for analysis"""
    timestamp: datetime
    query_preview: str
    student_confidence: float
    reason: EscalationReason
    student_answer: Optional[str]
    teacher_success: Optional[bool]


class ConfidenceFallback:
    """
    Confidence Fallback Mechanism - Safety valve for Student model.

    Implements the Phase 5 "Confidence Fallback" that ensures low-confidence
    or incorrect Student answers are automatically escalated to the full MAS.

    KEY PRINCIPLE:
    -------------
    The hybrid system must NEVER produce worse results than the full MAS.
    The fallback mechanism ensures that when the Student is uncertain,
    the system falls back to the Teacher for guaranteed quality.

    FALLBACK CONDITIONS:
    -------------------
    1. Confidence < threshold (default 0.7)
    2. Verification failure (Ax-Prover rejects answer)
    3. Timeout (Student exceeds time limit)
    4. Uncertainty markers in answer text
    5. Query complexity increased during solving

    USAGE:
    -----
    fallback = ConfidenceFallback()

    # Check if escalation needed
    should_escalate, reason = fallback.check_student_result(
        query="Prove x^2 >= 0",
        student_confidence=0.5,
        student_answer="x^2 is always non-negative"
    )

    if should_escalate:
        # Route to Teacher
        teacher_result = teacher_system.solve(query)
        # Record for learning
        fallback.record_escalation(query, student_confidence, teacher_result)

    REFERENCE:
    ---------
    Phase_5_Build_Order_Breakdown.md: Section 4.3.2
    """

    # Default thresholds
    DEFAULT_CONFIDENCE_THRESHOLD = 0.7
    DEFAULT_TIMEOUT_MS = 5000  # 5 seconds

    # Uncertainty markers in text
    UNCERTAINTY_MARKERS = [
        'i am not sure', 'uncertain', 'might be', 'possibly',
        'error', 'cannot determine', 'unable to', 'not confident',
        'approximately', 'roughly', 'may be wrong', 'check this',
        'i think', 'perhaps', 'maybe', 'unclear'
    ]

    def __init__(
        self,
        confidence_threshold: float = None,
        timeout_ms: float = None,
        teacher_system=None
    ):
        """
        Initialize the Confidence Fallback mechanism.

        Args:
            confidence_threshold: Minimum confidence to accept Student answer
            timeout_ms: Maximum time for Student before escalation
            teacher_system: Reference to Teacher (full MAS)
        """
        print("  [+] Initializing Confidence Fallback Mechanism")

        self.confidence_threshold = (
            confidence_threshold or self.DEFAULT_CONFIDENCE_THRESHOLD
        )
        self.timeout_ms = timeout_ms or self.DEFAULT_TIMEOUT_MS
        self.teacher_system = teacher_system

        # Escalation history
        self.escalation_history: List[EscalationEvent] = []

        # Statistics
        self.stats = {
            'total_checks': 0,
            'escalations': 0,
            'escalation_reasons': {r.value: 0 for r in EscalationReason},
            'teacher_success_after_escalation': 0
        }

        print(f"      Confidence threshold: {self.confidence_threshold}")
        print(f"      Timeout: {self.timeout_ms}ms")
        print("      [OK] Confidence Fallback ready")

    def check_student_result(
        self,
        query: str,
        student_confidence: float,
        student_answer: str = None,
        latency_ms: float = 0,
        verification_passed: bool = True
    ) -> Tuple[bool, EscalationReason]:
        """
        Check if Student result should be escalated to Teacher.

        This is the main entry point for fallback checking.

        Args:
            query: The original mathematical query
            student_confidence: Student's confidence in its answer (0-1)
            student_answer: The Student's answer text
            latency_ms: Time taken by Student
            verification_passed: Whether Ax-Prover verified the answer

        Returns:
            Tuple of (should_escalate, reason)
        """
        self.stats['total_checks'] += 1

        # Check 1: Low confidence
        if student_confidence < self.confidence_threshold:
            self._record_escalation_reason(EscalationReason.LOW_CONFIDENCE)
            return True, EscalationReason.LOW_CONFIDENCE

        # Check 2: Verification failure
        if not verification_passed:
            self._record_escalation_reason(EscalationReason.VERIFICATION_FAILED)
            return True, EscalationReason.VERIFICATION_FAILED

        # Check 3: Timeout
        if latency_ms > self.timeout_ms:
            self._record_escalation_reason(EscalationReason.TIMEOUT)
            return True, EscalationReason.TIMEOUT

        # Check 4: Uncertainty markers in answer
        if student_answer and self._has_uncertainty_markers(student_answer):
            self._record_escalation_reason(EscalationReason.UNCERTAINTY_MARKERS)
            return True, EscalationReason.UNCERTAINTY_MARKERS

        # No escalation needed
        return False, None

    def _has_uncertainty_markers(self, answer: str) -> bool:
        """Check if answer contains uncertainty markers"""
        answer_lower = answer.lower()
        return any(marker in answer_lower for marker in self.UNCERTAINTY_MARKERS)

    def _record_escalation_reason(self, reason: EscalationReason):
        """Record an escalation reason for statistics"""
        self.stats['escalations'] += 1
        self.stats['escalation_reasons'][reason.value] += 1

    def record_escalation(
        self,
        query: str,
        student_confidence: float,
        reason: EscalationReason,
        student_answer: str = None,
        teacher_result: Dict = None
    ):
        """
        Record an escalation event for learning and analysis.

        Args:
            query: The query that was escalated
            student_confidence: Student's confidence
            reason: Reason for escalation
            student_answer: Student's answer (if any)
            teacher_result: Result from Teacher system
        """
        teacher_success = None
        if teacher_result:
            teacher_success = teacher_result.get('verified', False)
            if teacher_success:
                self.stats['teacher_success_after_escalation'] += 1

        event = EscalationEvent(
            timestamp=datetime.now(),
            query_preview=query[:50],
            student_confidence=student_confidence,
            reason=reason,
            student_answer=student_answer[:100] if student_answer else None,
            teacher_success=teacher_success
        )
        self.escalation_history.append(event)

    def should_force_teacher(self, query: str) -> Tuple[bool, str]:
        """
        Check if query should bypass Student entirely.

        Some queries should always go to Teacher regardless of
        initial classification.

        Args:
            query: The mathematical query

        Returns:
            Tuple of (force_teacher, reason)
        """
        query_lower = query.lower()

        # Force Teacher for formal verification requests
        if any(kw in query_lower for kw in [
            'formally verify', 'prove rigorously',
            'certify', 'guaranteed correct', 'must be exact'
        ]):
            return True, "explicit_formal_request"

        # Force Teacher for high-stakes domains
        if any(kw in query_lower for kw in [
            'safety critical', 'mission critical',
            'financial', 'medical', 'legal'
        ]):
            return True, "high_stakes_domain"

        return False, ""

    def adjust_threshold(self, new_threshold: float):
        """
        Adjust confidence threshold dynamically.

        Can be used by Evolutionary Flywheel to tune based on
        observed escalation success rates.

        Args:
            new_threshold: New confidence threshold (0-1)
        """
        if 0.0 < new_threshold < 1.0:
            self.confidence_threshold = new_threshold

    def get_escalation_rate(self) -> float:
        """Get current escalation rate as percentage"""
        if self.stats['total_checks'] == 0:
            return 0.0
        return (self.stats['escalations'] / self.stats['total_checks']) * 100

    def get_teacher_success_rate(self) -> float:
        """Get Teacher success rate on escalated queries"""
        if self.stats['escalations'] == 0:
            return 0.0
        return (
            self.stats['teacher_success_after_escalation'] /
            self.stats['escalations']
        ) * 100

    def get_recent_escalations(self, count: int = 10) -> List[Dict]:
        """Get recent escalation events"""
        recent = self.escalation_history[-count:]
        return [
            {
                'timestamp': e.timestamp.isoformat(),
                'query_preview': e.query_preview,
                'student_confidence': e.student_confidence,
                'reason': e.reason.value,
                'teacher_success': e.teacher_success
            }
            for e in recent
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get fallback mechanism statistics"""
        return {
            'total_checks': self.stats['total_checks'],
            'total_escalations': self.stats['escalations'],
            'escalation_rate': self.get_escalation_rate(),
            'teacher_success_rate': self.get_teacher_success_rate(),
            'escalation_reasons': self.stats['escalation_reasons'],
            'current_threshold': self.confidence_threshold,
            'timeout_ms': self.timeout_ms
        }
