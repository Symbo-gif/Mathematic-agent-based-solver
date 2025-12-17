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

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from symbo_agentic_reasoners_phase3.phase3_system import Phase3System

class Phase3SmokeTests(unittest.TestCase):
    """
    Smoke tests for Phase 3 System.
    Verifies basic health and initialization of the Meta-Cognitive Middleware.
    """

    @classmethod
    def setUpClass(cls):
        print("\n[SmokeTests] Initializing Phase 3 System...")
        cls.system = Phase3System()
        cls.system.start()

    @classmethod
    def tearDownClass(cls):
        print("\n[SmokeTests] Shutting down Phase 3 System...")
        cls.system.shutdown()

    def test_system_initialization(self):
        """Test that the system initializes correctly."""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.phase2)
        self.assertIsNotNone(self.system.orchestrator)

    def test_components_presence(self):
        """Test that all Phase 3 teams are present."""
        orchestrator = self.system.orchestrator
        self.assertIsNotNone(orchestrator.precondition_team, "Precondition Validation Team missing")
        self.assertIsNotNone(orchestrator.knowledge_team, "Knowledge Management Team missing")
        self.assertIsNotNone(orchestrator.hypothesis_team, "Hypothesis Generation Team missing")

    def test_health_check(self):
        """Test the system health check."""
        health = self.system.health_check()
        self.assertTrue(health['overall'], "System health check failed")
        self.assertTrue(health['precondition_team'], "Precondition Team health check failed")
        self.assertTrue(health['knowledge_team'], "Knowledge Team health check failed")
        self.assertTrue(health['hypothesis_team'], "Hypothesis Team health check failed")
        self.assertTrue(health['orchestrator'], "Orchestrator health check failed")

    def test_statistics_availability(self):
        """Test that statistics are available for all components."""
        stats = self.system.get_statistics()
        self.assertIn('orchestrator', stats)
        
        orch_stats = stats['orchestrator']
        self.assertIn('precondition_team', orch_stats)
        self.assertIn('knowledge_team', orch_stats)
        self.assertIn('hypothesis_team', orch_stats)

if __name__ == '__main__':
    unittest.main()
