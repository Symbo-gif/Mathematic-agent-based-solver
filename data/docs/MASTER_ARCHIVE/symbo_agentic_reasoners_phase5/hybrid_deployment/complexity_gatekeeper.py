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
COMPLEXITY GATEKEEPER (The "Triage Nurse")
==========================================

Step 3 of Phase 5 Build Order: The Hybrid Deployment Architecture

OBJECTIVE:
---------
Implement a "Tiered Response" system that dynamically routes queries to
the optimal processing path. The Distilled Model (Student) is fast but
lacks the deep reasoning capacity of the full MAS (Teacher).

80/20 OPTIMIZATION PRINCIPLE:
----------------------------
Analysis of mathematical query distributions reveals that approximately
80% of incoming queries are standard, high-frequency patterns that can
be handled by an appropriately trained Student model. Only 20% require
the full deliberative capacity of the multi-agent swarm.

Routing all queries through the full MAS wastes computational resources
on trivial problems.

ROUTING LOGIC:
-------------
| Query Type      | Indicators                              | Route To    |
|-----------------|----------------------------------------|-------------|
| Standard Query  | High-frequency ("derivative of", etc.) | Student     |
| Novel/Complex   | Ambiguous, multi-domain, "prove that"  | Teacher     |
| High-Stakes     | "Proof Verification", formal reqs      | Teacher     |

THRESHOLDS:
----------
- STUDENT_THRESHOLD: 0.4 (below -> Student)
- TEACHER_THRESHOLD: 0.7 (above -> Teacher)
- CONFIDENCE_THRESHOLD: 0.7 (fallback trigger)

REFERENCE:
---------
- Phase_5_Build_Order_Breakdown.md: Section 4
- phase5_symbo_integration_architecture.py: ComplexityGatekeeper class
"""

import os
import sys
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import threading

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Get module logger
logger = logging.getLogger('symbo_agentic_reasoners.phase5.complexity_gatekeeper')


class QueryRoute(Enum):
    """Possible routing destinations for queries"""
    STUDENT = "student"   # Fast path - distilled model
    TEACHER = "teacher"   # Deep path - full MAS


@dataclass
class RoutingDecision:
    """Records a routing decision for analysis"""
    timestamp: datetime
    query_preview: str
    query_type: str
    complexity: float
    destination: QueryRoute
    reason: str


class ComplexityGatekeeper:
    """
    Phase 5 "Triage Nurse" - Routes queries to Student or full MAS.

    Implements the core Phase 5 optimization: fast model handles ~80% of
    interactions, full MAS reserved for complex problems.

    KEY INSIGHT FROM DOCUMENTATION:
    ------------------------------
    - "Standard queries route to Distilled Student Model"
    - "Novel/high-stakes queries route to Full Tier-3 Multi-Agent Hierarchy"
    - "~80% of queries solved instantly, 20% reserved for deep reasoning"

    COMPLEXITY INDICATORS:
    ---------------------
    Teacher Keywords (require deep reasoning):
      - prove, proof, theorem, lemma, verify, formal
      - perturbation, grobner, eigenvalue, eigenvector, svd
      - differential equation, pde, ode, stochastic

    Student Keywords (fast path):
      - derivative, differentiate, integrate, sum
      - simplify, expand, factor, solve, calculate

    USAGE:
    -----
    gatekeeper = ComplexityGatekeeper()

    # Route a query
    destination, complexity = gatekeeper.route_query("Find the derivative of x^2")

    # Check statistics
    stats = gatekeeper.get_routing_stats()

    REFERENCE:
    ---------
    Phase_5_Build_Order_Breakdown.md: Section 4.3.1
    phase5_symbo_integration_architecture.py: lines 290-410
    """

    # Complexity thresholds
    STUDENT_THRESHOLD = 0.4   # Below this -> Student
    TEACHER_THRESHOLD = 0.7   # Above this -> Teacher
    CONFIDENCE_THRESHOLD = 0.7  # Student confidence fallback

    # Keywords indicating high complexity (require Teacher)
    TEACHER_KEYWORDS = [
        'prove', 'proof', 'theorem', 'lemma', 'verify', 'formal',
        'perturbation', 'grobner', 'groebner', 'undecidable',
        'optimize', 'eigenvalue', 'eigenvector', 'svd',
        'differential equation', 'pde', 'ode', 'stochastic',
        'conjecture', 'hypothesis', 'induction', 'contradiction',
        'convergence', 'divergence', 'limit', 'supremum', 'infimum',
        'riemann', 'lebesgue', 'measure', 'topology'
    ]

    # Keywords indicating low complexity (Student can handle)
    STUDENT_KEYWORDS = [
        'derivative', 'differentiate', 'integrate', 'sum',
        'simplify', 'expand', 'factor', 'solve', 'calculate',
        'compute', 'evaluate', 'find', 'what is', 'determine',
        'add', 'subtract', 'multiply', 'divide', 'power',
        'square root', 'cube root', 'logarithm', 'exponential',
        'sine', 'cosine', 'tangent', 'basic', 'simple'
    ]

    # Query type base complexities
    QUERY_TYPE_WEIGHTS = {
        'proof': 0.7,
        'optimization': 0.5,
        'symbolic': 0.4,
        'computation': 0.2,
        'general': 0.3
    }

    def __init__(
        self,
        student_model=None,
        teacher_system=None,
        adaptive_thresholds: bool = True,
        symbo_adapter=None
    ):
        """
        Initialize the Complexity Gatekeeper.

        Args:
            student_model: Reference to Student (SymboLLMCore)
            teacher_system: Reference to Teacher (full MAS)
            adaptive_thresholds: Enable adaptive threshold adjustment
            symbo_adapter: Reference to SymboLLMAdapter for knowledge-aware routing
        """
        print("  [+] Initializing Complexity Gatekeeper (Triage Nurse)")

        self.student_model = student_model
        self.teacher_system = teacher_system
        self.adaptive_thresholds = adaptive_thresholds
        self.symbo_adapter = symbo_adapter

        # Thread safety lock for shared state
        self._lock = threading.Lock()

        # Routing history for analysis
        self.routing_history: List[RoutingDecision] = []

        # Adaptive success rates
        self.student_success_rate = 0.9
        self.student_attempts = 0
        self.student_successes = 0

        # Statistics
        self.stats = {
            'total_queries': 0,
            'student_routed': 0,
            'teacher_routed': 0,
            'escalations': 0,
            'knowledge_hits': 0
        }

        logger.info("ComplexityGatekeeper initialized", extra={
            'student_threshold': self.STUDENT_THRESHOLD,
            'teacher_threshold': self.TEACHER_THRESHOLD,
            'symbo_enabled': symbo_adapter is not None
        })

        print(f"      Student threshold: {self.STUDENT_THRESHOLD}")
        print(f"      Teacher threshold: {self.TEACHER_THRESHOLD}")
        print(f"      Confidence threshold: {self.CONFIDENCE_THRESHOLD}")
        if symbo_adapter:
            print("      Symbo knowledge-aware routing: ENABLED")
        print("      [OK] Complexity Gatekeeper ready")

    def classify_query(self, query: str) -> Tuple[float, str]:
        """
        Classify query complexity using lightweight heuristics.

        This is the first-pass classification that determines routing.

        Args:
            query: The mathematical query string

        Returns:
            Tuple of (complexity_score, query_type)
        """
        query_lower = query.lower()

        # Determine query type
        query_type = self._detect_query_type(query_lower)

        # Start with base complexity for query type
        base_complexity = self.QUERY_TYPE_WEIGHTS.get(query_type, 0.3)
        complexity = base_complexity

        # Check for Teacher-requiring keywords
        teacher_matches = sum(
            1 for kw in self.TEACHER_KEYWORDS
            if kw in query_lower
        )
        complexity += teacher_matches * 0.15

        # Check for Student-suitable keywords
        student_matches = sum(
            1 for kw in self.STUDENT_KEYWORDS
            if kw in query_lower
        )
        complexity -= student_matches * 0.1

        # Complexity modifiers

        # Higher-order terms increase complexity
        if any(term in query_lower for term in [
            'second order', '2nd order', 'hessian',
            'third order', 'higher order', 'nth order'
        ]):
            complexity += 0.15

        # Multi-step problems
        if query.count('?') > 1 or 'then' in query_lower or 'and' in query_lower:
            complexity += 0.1

        # Domain-specific indicators (economics/physics models)
        if any(domain in query_lower for domain in [
            'rbc', 'dsge', 'steady state', 'equilibrium',
            'hamiltonian', 'lagrangian', 'variational'
        ]):
            complexity += 0.2

        # Length indicator (longer queries often more complex)
        if len(query) > 200:
            complexity += 0.05
        elif len(query) > 500:
            complexity += 0.1

        # Clamp to valid range
        complexity = max(0.0, min(1.0, complexity))

        return complexity, query_type

    def _detect_query_type(self, query_lower: str) -> str:
        """Detect the type of mathematical query"""
        if any(kw in query_lower for kw in ['prove', 'proof', 'theorem', 'lemma', 'show that']):
            return 'proof'
        elif any(kw in query_lower for kw in ['optimize', 'minimize', 'maximize', 'optimal']):
            return 'optimization'
        elif any(kw in query_lower for kw in ['solve', 'equation', 'polynomial', 'system']):
            return 'symbolic'
        elif any(kw in query_lower for kw in ['compute', 'calculate', 'evaluate', 'derivative']):
            return 'computation'
        else:
            return 'general'

    def _check_symbo_knowledge(self, query: str) -> Tuple[bool, float]:
        """
        Check if Symbo has relevant knowledge for this query.

        Args:
            query: The mathematical query

        Returns:
            Tuple of (has_knowledge, confidence_boost)
        """
        if self.symbo_adapter is None:
            return False, 0.0

        try:
            # Query Symbo's knowledge store
            if hasattr(self.symbo_adapter, 'model') and hasattr(self.symbo_adapter.model, 'query_knowledge_store'):
                results = self.symbo_adapter.model.query_knowledge_store(query, top_k=3)

                if results and len(results) > 0:
                    # Found relevant knowledge - boost confidence in Student
                    self.stats['knowledge_hits'] += 1

                    # Higher quality results (longer responses) give more confidence
                    best_result = results[0]
                    response_len = len(best_result.get('response', '') or best_result.get('fact', ''))

                    if response_len > 100:
                        return True, 0.15  # High-quality knowledge hit
                    elif response_len > 20:
                        return True, 0.10  # Moderate knowledge hit
                    else:
                        return True, 0.05  # Low-quality hit

        except (AttributeError, KeyError, TypeError) as e:
            logger.debug(f"Symbo knowledge lookup failed: {type(e).__name__}: {e}")
            return False, 0.0
        except Exception as e:
            logger.warning(f"Unexpected error in Symbo knowledge check: {type(e).__name__}: {e}")
            return False, 0.0

        return False, 0.0

    def route_query(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Tuple[QueryRoute, float]:
        """
        Route query to appropriate system (Student or Teacher).

        This is the main entry point for query routing.
        Uses Symbo's knowledge store for smarter routing when available.

        Args:
            query: The mathematical query
            context: Optional context dictionary

        Returns:
            Tuple of (destination, complexity_score)
        """
        complexity, query_type = self.classify_query(query)

        # Check Symbo's knowledge store for relevant prior knowledge
        has_knowledge, knowledge_boost = self._check_symbo_knowledge(query)
        if has_knowledge:
            # Reduce complexity if Symbo has relevant knowledge
            complexity = max(0.0, complexity - knowledge_boost)

        # Check for explicit escalation keywords
        if any(kw in query.lower() for kw in [
            'verify formally', 'formal proof', 'guaranteed',
            'certify', 'must be exact'
        ]):
            destination = QueryRoute.TEACHER
            reason = "explicit_escalation"
        # High complexity -> Teacher
        elif complexity >= self.TEACHER_THRESHOLD:
            destination = QueryRoute.TEACHER
            reason = "high_complexity"
        # Low complexity -> Student
        elif complexity < self.STUDENT_THRESHOLD:
            destination = QueryRoute.STUDENT
            reason = "low_complexity" if not has_knowledge else "knowledge_hit_low_complexity"
        # Gray zone -> Default to Student with potential fallback
        else:
            destination = QueryRoute.STUDENT
            reason = "gray_zone_default_student" if not has_knowledge else "knowledge_hit_gray_zone"

        # Thread-safe statistics and history update
        with self._lock:
            self.stats['total_queries'] += 1
            if destination == QueryRoute.STUDENT:
                self.stats['student_routed'] += 1
            else:
                self.stats['teacher_routed'] += 1

            # Log routing decision
            decision = RoutingDecision(
                timestamp=datetime.now(),
                query_preview=query[:50],
                query_type=query_type,
                complexity=complexity,
                destination=destination,
                reason=reason
            )
            self.routing_history.append(decision)

        logger.debug(f"Routed query to {destination.value}", extra={
            'query_type': query_type,
            'complexity': complexity,
            'reason': reason
        })

        return destination, complexity

    def should_escalate(
        self,
        query: str,
        student_confidence: float,
        student_answer: str = None
    ) -> Tuple[bool, str]:
        """
        Determine if a Student result should be escalated to Teacher.

        This implements the Phase 5 "Confidence Fallback Mechanism".

        Args:
            query: The original query
            student_confidence: Student's confidence in its answer
            student_answer: The Student's answer (optional)

        Returns:
            Tuple of (should_escalate, reason)
        """
        # Low confidence -> escalate
        if student_confidence < self.CONFIDENCE_THRESHOLD:
            with self._lock:
                self.stats['escalations'] += 1
            logger.info(f"Escalating due to low confidence: {student_confidence:.2f}")
            return True, f"low_confidence ({student_confidence:.2f})"

        # Check for signs of uncertainty in answer
        if student_answer:
            uncertainty_markers = [
                'i am not sure', 'uncertain', 'might be',
                'possibly', 'error', 'cannot', 'unable'
            ]
            if any(marker in student_answer.lower() for marker in uncertainty_markers):
                with self._lock:
                    self.stats['escalations'] += 1
                logger.info("Escalating due to uncertainty markers in answer")
                return True, "uncertainty_in_answer"

        return False, "adequate_confidence"

    def record_student_result(self, success: bool):
        """
        Record Student success/failure for adaptive thresholds.

        Args:
            success: Whether Student's answer was verified correct
        """
        with self._lock:
            self.student_attempts += 1
            if success:
                self.student_successes += 1

            # Update success rate (rolling average)
            if self.student_attempts > 0:
                self.student_success_rate = (
                    self.student_successes / self.student_attempts
                )

            # Adaptive threshold adjustment
            if self.adaptive_thresholds and self.student_attempts >= 100:
                self._adjust_thresholds()
                logger.info(f"Adjusted thresholds: student={self.STUDENT_THRESHOLD:.2f}")

    def _adjust_thresholds(self):
        """
        Adjust routing thresholds based on Student performance.

        If Student is performing well, can route more to Student.
        If Student is struggling, route more to Teacher.
        """
        if self.student_success_rate > 0.95:
            # Student doing very well - route more to Student
            self.STUDENT_THRESHOLD = min(0.5, self.STUDENT_THRESHOLD + 0.01)
        elif self.student_success_rate < 0.85:
            # Student struggling - route more to Teacher
            self.STUDENT_THRESHOLD = max(0.3, self.STUDENT_THRESHOLD - 0.01)

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics (thread-safe)"""
        with self._lock:
            total = self.stats['total_queries']
            student = self.stats['student_routed']
            teacher = self.stats['teacher_routed']
            knowledge_hits = self.stats.get('knowledge_hits', 0)
            escalations = self.stats['escalations']
            success_rate = self.student_success_rate

        return {
            'total_queries': total,
            'student_routed': student,
            'teacher_routed': teacher,
            'student_percentage': (student / max(total, 1)) * 100,
            'teacher_percentage': (teacher / max(total, 1)) * 100,
            'escalations': escalations,
            'escalation_rate': (escalations / max(student, 1)) * 100,
            'student_success_rate': success_rate * 100,
            'knowledge_hits': knowledge_hits,
            'knowledge_hit_rate': (knowledge_hits / max(total, 1)) * 100,
            'symbo_enabled': self.symbo_adapter is not None,
            'current_thresholds': {
                'student': self.STUDENT_THRESHOLD,
                'teacher': self.TEACHER_THRESHOLD,
                'confidence': self.CONFIDENCE_THRESHOLD
            }
        }

    def get_recent_routing(self, count: int = 10) -> List[Dict]:
        """Get recent routing decisions (thread-safe)"""
        with self._lock:
            recent = list(self.routing_history[-count:])
        return [
            {
                'timestamp': d.timestamp.isoformat(),
                'query_preview': d.query_preview,
                'query_type': d.query_type,
                'complexity': d.complexity,
                'destination': d.destination.value,
                'reason': d.reason
            }
            for d in recent
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get gatekeeper statistics"""
        return self.get_routing_stats()
