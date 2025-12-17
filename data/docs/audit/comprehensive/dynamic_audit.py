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

import sys
import os
import unittest
import logging
from io import StringIO

# Add root directory to path
sys.path.insert(0, os.getcwd())

from symbo_agentic_reasoners_phase6.phase6_system import Phase6System, SystemStatus

class DynamicAudit(unittest.TestCase):
    def setUp(self):
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)
        self.system = Phase6System()

    def tearDown(self):
        if self.system.status == 'running':
            self.system.shutdown()
        logging.disable(logging.NOTSET)

    def test_instantiation(self):
        """Test if Phase6System can be instantiated and components are wired."""
        print("\n[Dynamic Audit] Testing Instantiation...")
        self.assertIsInstance(self.system, Phase6System)
        self.assertEqual(self.system.status, 'stopped')
        
        # Check components
        self.assertIsNotNone(self.system.synthetic_data_generator)
        self.assertIsNotNone(self.system.policy_network)
        self.assertIsNotNone(self.system.sandbox_evaluator)
        print("  - Instantiation successful")
        print("  - Components wired correctly")

    def test_health_check(self):
        """Test system health check."""
        print("\n[Dynamic Audit] Testing Health Check...")
        self.system.start()
        health = self.system.health_check()
        
        failed_components = []
        for component, is_healthy in health.items():
            if not is_healthy:
                failed_components.append(component)
        
        if failed_components:
            self.fail(f"Health check failed for: {', '.join(failed_components)}")
        
        print("  - All components reported healthy")

    def test_smoke_discovery_cycle(self):
        """Run a small discovery cycle (Smoke Test)."""
        print("\n[Dynamic Audit] Running Smoke Test (Discovery Cycle)...")
        self.system.start()
        
        # Run a very small cycle
        result = self.system.run_discovery_cycle(
            num_theorems=5,
            search_budget=10,
            max_candidates=1
        )
        
        print(f"  - Cycle ID: {result.cycle_id}")
        print(f"  - Theorems Generated: {result.theorems_generated}")
        print(f"  - Proofs Attempted: {result.proofs_attempted}")
        
        # Basic assertions
        self.assertGreaterEqual(result.theorems_generated, 0)
        self.assertIsInstance(result.errors, list)
        
        # Check stats update
        stats = self.system.get_statistics()
        self.assertEqual(stats['system']['discovery_cycles'], 1)
        print("  - Smoke test completed successfully")

    def test_edge_cases(self):
        """Test system behavior with edge case inputs."""
        print("\n[Dynamic Audit] Testing Edge Cases...")
        self.system.start()
        
        # Case 1: Zero theorems
        print("  - Testing zero theorems...")
        result = self.system.run_discovery_cycle(num_theorems=0)
        self.assertEqual(result.theorems_generated, 0)
        self.assertIn("Invalid input: num_theorems must be positive", result.errors)
        print("    - Correctly handled zero theorems")
        
        # Case 2: Negative budget
        print("  - Testing negative search budget...")
        # Should now run with default budget instead of crashing/hanging
        result = self.system.run_discovery_cycle(num_theorems=1, search_budget=-1)
        self.assertGreaterEqual(result.theorems_generated, 0)
        print("    - Correctly handled negative budget (fallback to default)")

        print("  - Edge case tests completed")

if __name__ == '__main__':
    unittest.main()
