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
EVOLUTIONARY FLYWHEEL (Active Learning Loop)
=============================================

Step 5 of Phase 5 Build Order: Continuous Improvement

OBJECTIVE:
---------
Close the loop to ensure the system gets smarter with every interaction
WITHOUT human intervention. The Evolutionary Flywheel implements the
Active Learning Loop that continuously raises the baseline intelligence
of the fast Student system by learning from Teacher successes on hard cases.

AUTOMAAS PATTERN:
----------------
This step implements the AutoMaAS (Autonomous Multi-Agent System) pattern
to its fullest potential: autonomous system optimization without human
intervention. Every problem solved creates a training data point. The
1001st query of a particular type is solved more efficiently than the
1000th because the system has learned optimal agent selection and routing.

FLYWHEEL DYNAMICS:
-----------------
1. Student attempts query -> Low confidence detected
2. Query escalated to Teacher (full MAS)
3. Teacher successfully resolves with VERIFIED status
4. Trace captured with "escalated" metadata flag
5. Distillation Pipeline retrains Student with priority on escalated traces
6. Student now handles similar queries without escalation

OUTCOME:
-------
The Student gradually masters the problems that used to require the Teacher,
constantly raising the baseline intelligence of the fast system. Over time,
the escalation rate decreases as the Student absorbs more of the Teacher's
capability.

REFERENCE:
---------
- Phase_5_Build_Order_Breakdown.md: Section 6
- phase5_symbo_integration_architecture.py: EvolutionaryFlywheel class
- Phase_4_Build_Order_Breakdown.md: Section 5.3 (AutoMaAS)
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add parent paths for imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.optimization.distillation.harvester import (
    ThoughtTraceHarvester,
    ThoughtTrace,
    VerificationStatus
)
from symbo_agentic_reasoners.optimization.distillation.pipeline import DistillationPipeline


class EvolutionPhase(Enum):
    """Phases of evolutionary learning"""
    COLLECTING = "collecting"       # Gathering escalated traces
    TRAINING = "training"           # Distillation in progress
    VALIDATING = "validating"       # Validating new model
    DEPLOYED = "deployed"           # New model active
    MONITORING = "monitoring"       # Monitoring new model performance


@dataclass
class EvolutionCycle:
    """Record of a single evolution cycle"""
    cycle_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    escalations_processed: int
    training_examples: int
    previous_escalation_rate: float
    new_escalation_rate: float
    improvement: float
    status: str


class EvolutionaryFlywheel:
    """
    Evolutionary Flywheel - Active Learning Loop

    Implements continuous improvement where the Student learns from
    Teacher successes on escalated queries.

    KEY PRINCIPLE:
    -------------
    When Student fails (low confidence) but Teacher succeeds (VERIFIED),
    this creates HIGH-PRIORITY training data. The system prioritizes
    learning from these "hard cases" to reduce future escalations.

    TRIGGERS:
    --------
    - Escalation count reaches threshold (default: 10)
    - Periodic schedule (e.g., hourly)
    - Manual trigger for immediate learning
    - Escalation rate exceeds acceptable threshold

    EVOLUTION FLOW:
    --------------
    1. Monitor escalation events
    2. When threshold reached, trigger distillation
    3. Train Student on escalated traces (3x priority)
    4. Deploy updated Student model
    5. Monitor new escalation rate
    6. Report improvement metrics

    USAGE:
    -----
    flywheel = EvolutionaryFlywheel(harvester, distillation_pipeline)

    # Record an escalation
    flywheel.record_escalation(query, student_confidence, teacher_result)

    # Check if evolution should trigger
    if flywheel.should_evolve():
        result = flywheel.trigger_evolution_cycle()

    # Get evolution metrics
    metrics = flywheel.get_evolution_metrics()

    REFERENCE:
    ---------
    Phase_5_Build_Order_Breakdown.md: Section 6.4
    phase5_symbo_integration_architecture.py: lines 550-620
    """

    # Default thresholds
    DEFAULT_ESCALATION_THRESHOLD = 10   # Trigger after N escalations
    DEFAULT_MAX_ESCALATION_RATE = 0.25  # Max 25% escalation rate
    DEFAULT_MIN_IMPROVEMENT = 0.05      # Require 5% improvement

    def __init__(
        self,
        harvester: ThoughtTraceHarvester = None,
        distillation: DistillationPipeline = None,
        escalation_threshold: int = None,
        max_escalation_rate: float = None
    ):
        """
        Initialize the Evolutionary Flywheel.

        Args:
            harvester: ThoughtTraceHarvester for trace capture
            distillation: DistillationPipeline for training
            escalation_threshold: Trigger distillation after N escalations
            max_escalation_rate: Maximum acceptable escalation rate
        """
        print("  [+] Initializing Evolutionary Flywheel (Active Learning Loop)")

        self.harvester = harvester
        self.distillation = distillation

        self.escalation_threshold = (
            escalation_threshold or self.DEFAULT_ESCALATION_THRESHOLD
        )
        self.max_escalation_rate = (
            max_escalation_rate or self.DEFAULT_MAX_ESCALATION_RATE
        )

        # Current state
        self.current_phase = EvolutionPhase.COLLECTING
        self.escalation_count = 0
        self.total_queries = 0

        # Evolution history
        self.evolution_cycles: List[EvolutionCycle] = []
        self.cycle_count = 0

        # Pending escalations (awaiting Teacher resolution)
        self.pending_escalations: List[Dict] = []

        # Statistics
        self.stats = {
            'total_escalations': 0,
            'evolution_cycles': 0,
            'total_improvement': 0.0,
            'current_escalation_rate': 0.0,
            'baseline_escalation_rate': 0.25  # Starting assumption
        }

        print(f"      Escalation threshold: {self.escalation_threshold}")
        print(f"      Max escalation rate: {self.max_escalation_rate * 100}%")
        print("      AutoMaAS pattern: ENABLED")
        print("      [OK] Evolutionary Flywheel ready")

    def record_query(self, routed_to: str):
        """
        Record a query for escalation rate tracking.

        Args:
            routed_to: "student" or "teacher"
        """
        self.total_queries += 1

    def record_escalation(
        self,
        query: str,
        student_confidence: float,
        teacher_result: Dict,
        trace_id: str = None
    ):
        """
        Record an escalation event for learning.

        This is called when Student fails (low confidence) but
        Teacher succeeds (VERIFIED status).

        Args:
            query: The query that was escalated
            student_confidence: Student's confidence (that triggered escalation)
            teacher_result: Result from Teacher system
            trace_id: ID of the thought trace (if available)
        """
        self.escalation_count += 1
        self.stats['total_escalations'] += 1

        # Update escalation rate
        if self.total_queries > 0:
            self.stats['current_escalation_rate'] = (
                self.stats['total_escalations'] / self.total_queries
            )

        # Mark trace as high-priority if available
        if trace_id and self.harvester:
            trace = self.harvester._get_trace(trace_id)
            if trace:
                trace.metadata['escalated'] = True
                trace.metadata['student_confidence'] = student_confidence
                trace.metadata['learning_priority'] = 'high'

        # Store escalation for processing
        self.pending_escalations.append({
            'query': query,
            'student_confidence': student_confidence,
            'teacher_verified': teacher_result.get('verified', False),
            'trace_id': trace_id,
            'timestamp': datetime.now().isoformat()
        })

        # Check if we should trigger evolution
        if self.should_evolve():
            self._trigger_evolution_cycle()

    def should_evolve(self) -> bool:
        """
        Check if evolution cycle should be triggered.

        Returns:
            True if evolution should be triggered
        """
        # Trigger if escalation count exceeds threshold
        if self.escalation_count >= self.escalation_threshold:
            return True

        # Trigger if escalation rate exceeds maximum
        if (self.total_queries > 100 and
            self.stats['current_escalation_rate'] > self.max_escalation_rate):
            return True

        return False

    def _trigger_evolution_cycle(self):
        """
        Trigger an evolution cycle.

        This runs the distillation pipeline with priority on
        escalated traces.
        """
        if self.current_phase == EvolutionPhase.TRAINING:
            return  # Already training

        self.current_phase = EvolutionPhase.TRAINING
        cycle_id = f"evolution_{self.cycle_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n    [EVOLUTION] Triggering cycle {cycle_id}")
        print(f"      Escalations to process: {self.escalation_count}")

        # Record starting escalation rate
        previous_rate = self.stats['current_escalation_rate']

        # Run distillation with priority on escalated traces
        if self.distillation:
            result = self.distillation.run_distillation(prioritize_escalated=True)
            training_examples = result.get('examples_trained', 0)
            print(f"      Training examples: {training_examples}")
        else:
            training_examples = 0

        # Create cycle record
        cycle = EvolutionCycle(
            cycle_id=cycle_id,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            escalations_processed=self.escalation_count,
            training_examples=training_examples,
            previous_escalation_rate=previous_rate,
            new_escalation_rate=previous_rate,  # Will be updated after monitoring
            improvement=0.0,
            status='completed'
        )

        self.evolution_cycles.append(cycle)
        self.cycle_count += 1
        self.stats['evolution_cycles'] += 1

        # Reset escalation count
        self.escalation_count = 0
        self.pending_escalations = []

        # Move to monitoring phase
        self.current_phase = EvolutionPhase.MONITORING

        print(f"      [EVOLUTION] Cycle {cycle_id} completed")

    def trigger_immediate_evolution(self) -> Dict[str, Any]:
        """
        Trigger evolution cycle immediately.

        Use for manual triggering or testing.

        Returns:
            Evolution cycle results
        """
        previous_count = self.escalation_count
        self._trigger_evolution_cycle()

        return {
            'triggered': True,
            'escalations_processed': previous_count,
            'cycle_id': self.evolution_cycles[-1].cycle_id if self.evolution_cycles else None
        }

    def update_escalation_rate(self, new_rate: float):
        """
        Update the observed escalation rate after evolution.

        Called after a period of monitoring the evolved Student.

        Args:
            new_rate: New observed escalation rate
        """
        if self.evolution_cycles:
            last_cycle = self.evolution_cycles[-1]
            last_cycle.new_escalation_rate = new_rate
            last_cycle.improvement = (
                last_cycle.previous_escalation_rate - new_rate
            )
            self.stats['total_improvement'] += last_cycle.improvement

            if last_cycle.improvement > 0:
                print(f"    [EVOLUTION] Improvement: {last_cycle.improvement * 100:.1f}% reduction in escalations")

        self.stats['current_escalation_rate'] = new_rate

    def get_evolution_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive evolution metrics.

        Returns:
            Dictionary of evolution metrics
        """
        cycles = self.evolution_cycles

        return {
            'total_cycles': len(cycles),
            'current_phase': self.current_phase.value,
            'current_escalation_rate': self.stats['current_escalation_rate'] * 100,
            'baseline_escalation_rate': self.stats['baseline_escalation_rate'] * 100,
            'total_improvement': self.stats['total_improvement'] * 100,
            'pending_escalations': len(self.pending_escalations),
            'escalation_count': self.escalation_count,
            'escalation_threshold': self.escalation_threshold,
            'recent_cycles': [
                {
                    'cycle_id': c.cycle_id,
                    'started': c.started_at.isoformat(),
                    'escalations': c.escalations_processed,
                    'improvement': c.improvement * 100
                }
                for c in cycles[-5:]
            ]
        }

    def get_learning_insights(self) -> List[Dict[str, Any]]:
        """
        Get insights about what the system is learning.

        Analyzes escalated traces to identify patterns.

        Returns:
            List of learning insights
        """
        insights = []

        # Analyze pending escalations for patterns
        if self.pending_escalations:
            # Group by query type
            query_types = {}
            for esc in self.pending_escalations:
                query = esc['query'].lower()
                if 'prove' in query:
                    qt = 'proof'
                elif 'integrate' in query:
                    qt = 'integration'
                elif 'solve' in query:
                    qt = 'equation'
                else:
                    qt = 'general'

                query_types[qt] = query_types.get(qt, 0) + 1

            # Report most common escalation types
            for qt, count in sorted(query_types.items(), key=lambda x: -x[1]):
                if count > 1:
                    insights.append({
                        'type': 'pattern',
                        'category': qt,
                        'count': count,
                        'recommendation': f"Student struggles with {qt} queries"
                    })

        # Analyze evolution cycles for trends
        if len(self.evolution_cycles) >= 2:
            recent = self.evolution_cycles[-2:]
            if recent[1].improvement > recent[0].improvement:
                insights.append({
                    'type': 'trend',
                    'observation': 'Improvement rate increasing',
                    'recommendation': 'Evolution is effective'
                })
            elif recent[1].improvement < 0:
                insights.append({
                    'type': 'warning',
                    'observation': 'Escalation rate increased after evolution',
                    'recommendation': 'Review training data quality'
                })

        return insights

    def get_statistics(self) -> Dict[str, Any]:
        """Get flywheel statistics"""
        return {
            'total_escalations': self.stats['total_escalations'],
            'evolution_cycles': self.stats['evolution_cycles'],
            'total_improvement': self.stats['total_improvement'] * 100,
            'current_escalation_rate': self.stats['current_escalation_rate'] * 100,
            'current_phase': self.current_phase.value,
            'pending_count': len(self.pending_escalations),
            'threshold': self.escalation_threshold,
            'queries_tracked': self.total_queries
        }

    def reset(self):
        """Reset the flywheel state (for testing)"""
        self.escalation_count = 0
        self.total_queries = 0
        self.pending_escalations = []
        self.current_phase = EvolutionPhase.COLLECTING
