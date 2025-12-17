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

from symbo_agentic_reasoners_phase4.phase4_system import Phase4System

class Phase4SmokeTests(unittest.TestCase):
    """
    Smoke tests for Phase 4 System.
    Verifies basic health and initialization of the Self-Correcting System.
    """

    @classmethod
    def setUpClass(cls):
        print("\n[SmokeTests] Initializing Phase 4 System...")
        cls.system = Phase4System()
        cls.system.start()

    @classmethod
    def tearDownClass(cls):
        print("\n[SmokeTests] Shutting down Phase 4 System...")
        cls.system.shutdown()

    def test_system_initialization(self):
        """Test that the system initializes correctly."""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.phase3)
        self.assertIsNotNone(self.system.conflict_resolution_team)
        self.assertIsNotNone(self.system.failure_analysis_team)
        self.assertIsNotNone(self.system.meta_learning_team)

    def test_components_presence(self):
        """Test that all Phase 4 teams are present."""
        # Conflict Resolution Team
        crt = self.system.conflict_resolution_team
        self.assertIsNotNone(crt.debate_moderator, "Debate Moderator missing")
        self.assertIsNotNone(crt.evidence_weigher, "Evidence Weigher missing")
        self.assertIsNotNone(crt.consensus_builder, "Consensus Builder missing")

        # Failure Analysis Team
        fat = self.system.failure_analysis_team
        self.assertIsNotNone(fat.error_classifier, "Error Classifier missing")
        self.assertIsNotNone(fat.root_cause_analyzer, "Root Cause Analyzer missing")
        self.assertIsNotNone(fat.alternative_path_generator, "Alternative Path Generator missing")

        # Meta-Learning Team
        mlt = self.system.meta_learning_team
        self.assertIsNotNone(mlt.performance_monitor, "Performance Monitor missing")
        self.assertIsNotNone(mlt.optimizer, "Agent Selector Optimizer missing")
        self.assertIsNotNone(mlt.dispatcher, "Adaptive Dispatcher missing")

    def test_health_check(self):
        """Test the system health check."""
        health = self.system.health_check()
        self.assertTrue(health['overall'], "System health check failed")
        self.assertTrue(health['conflict_resolution_team'], "Conflict Resolution Team health check failed")
        self.assertTrue(health['failure_analysis_team'], "Failure Analysis Team health check failed")
        self.assertTrue(health['meta_learning_team'], "Meta-Learning Team health check failed")
        self.assertTrue(health['protocols'], "Protocol Integration health check failed")

    def test_statistics_availability(self):
        """Test that statistics are available for all components."""
        stats = self.system.get_statistics()
        self.assertIn('conflict_resolution', stats)
        self.assertIn('failure_analysis', stats)
        self.assertIn('meta_learning', stats)
        self.assertIn('protocols', stats)

if __name__ == '__main__':
    unittest.main()
