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

# Add parent directory to path to import symbo_agentic_reasoners_phase0
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

class Phase0SmokeTest(unittest.TestCase):
    """
    Smoke tests for Phase 0 System.
    Verifies that the system can start, components are healthy, and basic operations work.
    """

    def setUp(self):
        self.system = Phase0System()
        self.system.start()

    def tearDown(self):
        self.system.shutdown()

    def test_system_health(self):
        """Test overall system health check"""
        health = self.system.health_check()
        self.assertTrue(health['overall'], "Overall system health check failed")
        self.assertTrue(health['infrastructure'], "Infrastructure health check failed")
        self.assertTrue(health['city_manager'], "City Manager (AMS) health check failed")
        self.assertTrue(health['laws'], "Laws (FIPA/OMDoc) health check failed")
        self.assertTrue(health['library'], "Library (Blackboard/VectorDB) health check failed")

    def test_component_initialization(self):
        """Test that all components are initialized"""
        self.assertIsNotNone(self.system.ams, "AMS not initialized")
        self.assertIsNotNone(self.system.df, "DF not initialized")
        self.assertIsNotNone(self.system.acc, "ACC not initialized")
        self.assertIsNotNone(self.system.blackboard, "Blackboard not initialized")
        self.assertIsNotNone(self.system.vector_db, "Vector DB not initialized")

    def test_statistics_availability(self):
        """Test that statistics can be retrieved"""
        stats = self.system.get_statistics()
        self.assertIn('ams', stats)
        self.assertIn('df', stats)
        self.assertIn('acc', stats)
        self.assertIn('blackboard', stats)
        self.assertIn('vector_db', stats)

if __name__ == '__main__':
    unittest.main()
