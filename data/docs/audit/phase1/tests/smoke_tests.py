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

import sys
import os
import unittest
from typing import Dict, Any

# Add parent directory to path to import symbo_agentic_reasoners_phase1 and symbo_agentic_reasoners_phase0
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from symbo_agentic_reasoners_phase1.phase1_system import Phase1System

class Phase1SmokeTest(unittest.TestCase):
    """
    Smoke tests for Phase 1 System.
    Verifies that the Cognitive Chassis can start, components are healthy, and basic operations work.
    """

    def setUp(self):
        self.system = Phase1System()
        self.system.start()

    def tearDown(self):
        self.system.shutdown()

    def test_system_health(self):
        """Test overall system health check"""
        health = self.system.health_check()
        self.assertTrue(health['overall'], "Overall system health check failed")
        self.assertTrue(health['phase0'], "Phase 0 Infrastructure health check failed")
        self.assertTrue(health['problem_analysis'], "Problem Analysis Team health check failed")
        self.assertTrue(health['orchestrator'], "Main Orchestrator health check failed")
        self.assertTrue(health['pilot_solver'], "Pilot Solver health check failed")
        self.assertTrue(health['verification_core'], "Verification Core health check failed")

    def test_component_initialization(self):
        """Test that all Phase 1 components are initialized"""
        self.assertIsNotNone(self.system.problem_analysis, "Problem Analysis Team not initialized")
        self.assertIsNotNone(self.system.orchestrator, "Main Orchestrator not initialized")
        self.assertIsNotNone(self.system.pilot_solver, "Pilot Solver not initialized")
        self.assertIsNotNone(self.system.verification_core, "Verification Core not initialized")
        self.assertIsNotNone(self.system.phase0, "Phase 0 System not initialized")

    def test_statistics_availability(self):
        """Test that statistics can be retrieved"""
        stats = self.system.get_statistics()
        self.assertIn('phase0', stats)
        self.assertIn('orchestrator', stats)
        self.assertIn('pilot_solver', stats)
        self.assertIn('verification_core', stats)

if __name__ == '__main__':
    unittest.main()
