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

import unittest
import sys
import os
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from symbo_agentic_reasoners_phase5.phase5_system import Phase5System
from symbo_agentic_reasoners_phase5.hybrid_deployment.complexity_gatekeeper import QueryRoute
from symbo_agentic_reasoners_phase5.hybrid_deployment.confidence_fallback import EscalationReason
from symbo_agentic_reasoners_phase5.distillation.thought_trace_harvester import VerificationStatus

class Phase5EdgeTests(unittest.TestCase):
    """
    Edge tests for Phase 5 System.
    Verifies capabilities and boundaries of the Apex System.
    """

    @classmethod
    def setUpClass(cls):
        print("\n[EdgeTests] Initializing Phase 5 System...")
        # Use a temporary directory for thought traces to avoid polluting the real one
        cls.test_trace_path = "./audit_test_traces"
        if os.path.exists(cls.test_trace_path):
            shutil.rmtree(cls.test_trace_path)
        os.makedirs(cls.test_trace_path)

        cls.system = Phase5System(thought_trace_path=cls.test_trace_path)
        cls.system.start()

    @classmethod
    def tearDownClass(cls):
        print("\n[EdgeTests] Shutting down Phase 5 System...")
        cls.system.shutdown()
        # Clean up test traces
        if os.path.exists(cls.test_trace_path):
            shutil.rmtree(cls.test_trace_path)

    def test_gatekeeper_routing_simple(self):
        """Test that simple queries are routed to the Student."""
        query = "Find the derivative of x^2"
        destination, complexity = self.system.complexity_gatekeeper.route_query(query)
        
        # Should route to STUDENT
        self.assertEqual(destination, QueryRoute.STUDENT)
        # Complexity should be low (< 0.4)
        self.assertLess(complexity, self.system.complexity_gatekeeper.STUDENT_THRESHOLD)

    def test_gatekeeper_routing_complex(self):
        """Test that complex queries are routed to the Teacher."""
        query = "Prove that the Riemann Hypothesis implies the distribution of prime numbers follows..."
        destination, complexity = self.system.complexity_gatekeeper.route_query(query)
        
        # Should route to TEACHER
        self.assertEqual(destination, QueryRoute.TEACHER)
        # Complexity should be high (> 0.7)
        self.assertGreaterEqual(complexity, self.system.complexity_gatekeeper.TEACHER_THRESHOLD)

    def test_confidence_fallback(self):
        """Test that low confidence triggers escalation."""
        query = "Solve for x"
        low_confidence = 0.3
        
        should_escalate, reason = self.system.confidence_fallback.check_student_result(
            query=query,
            student_confidence=low_confidence,
            student_answer="x = 5 maybe?"
        )
        
        self.assertTrue(should_escalate)
        self.assertEqual(reason, EscalationReason.LOW_CONFIDENCE)

    def test_trace_harvesting(self):
        """Test that verified traces are correctly harvested."""
        harvester = self.system.thought_trace_harvester
        initial_count = len(harvester.verified_traces)
        
        # 1. Begin trace
        trace_id = harvester.begin_trace("Integrate x dx", "calculus")
        
        # 2. Record steps
        harvester.record_symbolic_step(trace_id, "x^2/2", "integration", "Integration_Specialist")
        
        # 3. Finalize as VERIFIED
        harvester.finalize_trace(
            trace_id=trace_id,
            final_answer="x^2/2 + C",
            verification_status=VerificationStatus.VERIFIED,
            confidence=0.95,
            latency_ms=100.0
        )
        
        # 4. Verify it was added to verified_traces
        self.assertEqual(len(harvester.verified_traces), initial_count + 1)
        self.assertEqual(harvester.verified_traces[-1].trace_id, trace_id)

    def test_flywheel_trigger(self):
        """Test that the evolutionary flywheel triggers on escalation threshold."""
        flywheel = self.system.evolutionary_flywheel
        flywheel.reset() # Reset state for test
        
        # Set a low threshold for testing
        flywheel.escalation_threshold = 2
        
        # Record 1st escalation
        flywheel.record_escalation(
            query="Hard problem 1",
            student_confidence=0.2,
            teacher_result={'verified': True, 'answer': '42'}
        )
        self.assertEqual(flywheel.escalation_count, 1)
        self.assertEqual(flywheel.stats['evolution_cycles'], 0)
        
        # Record 2nd escalation (should trigger)
        flywheel.record_escalation(
            query="Hard problem 2",
            student_confidence=0.2,
            teacher_result={'verified': True, 'answer': '42'}
        )
        
        # Should have triggered evolution (reset count, increment cycle)
        self.assertEqual(flywheel.escalation_count, 0)
        self.assertEqual(flywheel.stats['evolution_cycles'], 1)

if __name__ == '__main__':
    unittest.main()
