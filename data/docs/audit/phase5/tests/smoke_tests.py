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

from symbo_agentic_reasoners_phase5.phase5_system import Phase5System

class Phase5SmokeTests(unittest.TestCase):
    """
    Smoke tests for Phase 5 System.
    Verifies basic health and initialization of the Apex System.
    """

    @classmethod
    def setUpClass(cls):
        print("\n[SmokeTests] Initializing Phase 5 System...")
        cls.system = Phase5System()
        cls.system.start()

    @classmethod
    def tearDownClass(cls):
        print("\n[SmokeTests] Shutting down Phase 5 System...")
        cls.system.shutdown()

    def test_system_initialization(self):
        """Test that the system initializes correctly."""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.phase4)
        self.assertIsNotNone(self.system.thought_trace_harvester)
        self.assertIsNotNone(self.system.distillation_pipeline)
        self.assertIsNotNone(self.system.complexity_gatekeeper)
        self.assertIsNotNone(self.system.confidence_fallback)
        self.assertIsNotNone(self.system.user_simulator)
        self.assertIsNotNone(self.system.identity_manager)
        self.assertIsNotNone(self.system.evolutionary_flywheel)

    def test_components_presence(self):
        """Test that all Phase 5 teams are present."""
        # Distillation & Harvest Team
        self.assertIsNotNone(self.system.thought_trace_harvester, "Thought Trace Harvester missing")
        self.assertIsNotNone(self.system.distillation_pipeline, "Distillation Pipeline missing")

        # Hybrid Deployment Team
        self.assertIsNotNone(self.system.complexity_gatekeeper, "Complexity Gatekeeper missing")
        self.assertIsNotNone(self.system.confidence_fallback, "Confidence Fallback missing")

        # Operational Hardening Team
        self.assertIsNotNone(self.system.user_simulator, "User Simulator missing")
        self.assertIsNotNone(self.system.identity_manager, "Identity Manager missing")

        # Evolutionary Flywheel
        self.assertIsNotNone(self.system.evolutionary_flywheel, "Evolutionary Flywheel missing")

    def test_health_check(self):
        """Test the system health check."""
        health = self.system.health_check()
        self.assertTrue(health['overall'], "System health check failed")
        self.assertTrue(health['thought_trace_harvester'], "Thought Trace Harvester health check failed")
        self.assertTrue(health['distillation_pipeline'], "Distillation Pipeline health check failed")
        self.assertTrue(health['hybrid_deployment'], "Hybrid Deployment Team health check failed")
        self.assertTrue(health['operational_hardening'], "Operational Hardening Team health check failed")
        self.assertTrue(health['evolutionary_flywheel'], "Evolutionary Flywheel health check failed")

    def test_statistics_availability(self):
        """Test that statistics are available for all components."""
        stats = self.system.get_statistics()
        self.assertIn('thought_trace_harvester', stats)
        self.assertIn('distillation_pipeline', stats)
        self.assertIn('complexity_gatekeeper', stats)
        self.assertIn('confidence_fallback', stats)
        self.assertIn('user_simulator', stats)
        self.assertIn('identity_manager', stats)
        self.assertIn('evolutionary_flywheel', stats)

if __name__ == '__main__':
    unittest.main()
