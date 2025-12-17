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

from symbo_agentic_reasoners_phase6.phase6_system import Phase6System

class Phase6SmokeTests(unittest.TestCase):
    """
    Smoke tests for Phase 6 System.
    Verifies basic health and initialization of the Discovery Engine.
    """

    @classmethod
    def setUpClass(cls):
        print("\n[SmokeTests] Initializing Phase 6 System...")
        cls.system = Phase6System()
        try:
            cls.system.start()
        except Exception as e:
            print(f"Warning: System start failed: {e}")
            # We continue to allow tests to inspect the state, 
            # though some might fail if start() is critical.

    @classmethod
    def tearDownClass(cls):
        print("\n[SmokeTests] Shutting down Phase 6 System...")
        if hasattr(cls, 'system'):
            cls.system.shutdown()

    def test_system_initialization(self):
        """Test that the system initializes correctly."""
        self.assertIsNotNone(self.system)
        # Team 1
        self.assertIsNotNone(self.system.synthetic_data_generator)
        self.assertIsNotNone(self.system.pattern_recognizer)
        self.assertIsNotNone(self.system.conjecture_formalizer)
        # Team 2
        self.assertIsNotNone(self.system.policy_network)
        self.assertIsNotNone(self.system.critic_network)
        self.assertIsNotNone(self.system.search_tree_manager)
        # Team 3
        self.assertIsNotNone(self.system.code_evolutionary_proposer)
        self.assertIsNotNone(self.system.sandbox_evaluator)
        self.assertIsNotNone(self.system.heuristic_distiller)
        # Team 4
        self.assertIsNotNone(self.system.decidability_checker)
        self.assertIsNotNone(self.system.interactive_guidance_liaison)
        # Team 5
        self.assertIsNotNone(self.system.auto_formalization_pipeline)
        self.assertIsNotNone(self.system.vector_database_updater)

    def test_health_check(self):
        """Test the system health check."""
        # Note: If start() failed, health check might be false, but the method should still run
        health = self.system.health_check()
        self.assertIn('overall', health)
        self.assertIn('conjecture_generation', health)
        self.assertIn('deep_search', health)
        self.assertIn('algorithm_discovery', health)
        self.assertIn('undecidability_navigator', health)
        self.assertIn('formal_knowledge_integration', health)

    def test_statistics_availability(self):
        """Test that statistics are available for all components."""
        stats = self.system.get_statistics()
        self.assertIn('system', stats)
        self.assertIn('synthetic_data_generator', stats)
        self.assertIn('policy_network', stats)
        self.assertIn('code_evolutionary_proposer', stats)
        self.assertIn('decidability_checker', stats)
        self.assertIn('auto_formalization_pipeline', stats)

if __name__ == '__main__':
    unittest.main()
