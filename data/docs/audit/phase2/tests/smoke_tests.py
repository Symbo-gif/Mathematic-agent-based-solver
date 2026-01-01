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

# Add parent directory to path to import symbo_agentic_reasoners_phase2, symbo_agentic_reasoners_phase1, symbo_agentic_reasoners_phase0
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from symbo_agentic_reasoners_phase2.phase2_system import Phase2System

class Phase2SmokeTest(unittest.TestCase):
    """
    Smoke tests for Phase 2 System.
    Verifies that the Mathematical Workforce can start, components are healthy, and basic operations work.
    """

    def setUp(self):
        self.system = Phase2System()
        self.system.start()

    def tearDown(self):
        self.system.shutdown()

    def test_system_health(self):
        """Test overall system health check"""
        health = self.system.health_check()
        self.assertTrue(health['overall'], "Overall system health check failed")
        self.assertTrue(health['phase1'], "Phase 1 Infrastructure health check failed")
        self.assertTrue(health['supervisors'], "Tier 2 Supervisors health check failed")
        self.assertTrue(health['algebra'], "Algebra Team health check failed")
        self.assertTrue(health['calculus'], "Calculus Team health check failed")
        self.assertTrue(health['linalg'], "Linear Algebra Team health check failed")
        self.assertTrue(health['numerical'], "Numerical Fallback health check failed")

    def test_component_initialization(self):
        """Test that all Phase 2 components are initialized"""
        # Supervisors
        self.assertIsNotNone(self.system.algebra_supervisor, "Algebra Supervisor not initialized")
        self.assertIsNotNone(self.system.calculus_supervisor, "Calculus Supervisor not initialized")
        self.assertIsNotNone(self.system.linalg_supervisor, "Linear Algebra Supervisor not initialized")
        self.assertIsNotNone(self.system.stats_supervisor, "Statistics Supervisor not initialized")

        # Specialists - Algebra
        self.assertIsNotNone(self.system.arithmetic_specialist, "Arithmetic Specialist not initialized")
        self.assertIsNotNone(self.system.polynomial_specialist, "Polynomial Specialist not initialized")
        self.assertIsNotNone(self.system.numbertheory_specialist, "Number Theory Specialist not initialized")

        # Specialists - Calculus
        self.assertIsNotNone(self.system.differentiation_specialist, "Differentiation Specialist not initialized")
        self.assertIsNotNone(self.system.integration_specialist, "Integration Specialist not initialized")
        self.assertIsNotNone(self.system.ode_solver, "ODE Solver not initialized")
        self.assertIsNotNone(self.system.series_specialist, "Series Specialist not initialized")

        # Specialists - Linear Algebra
        self.assertIsNotNone(self.system.matrix_ops, "Matrix Ops Specialist not initialized")
        self.assertIsNotNone(self.system.decomposition, "Decomposition Specialist not initialized")
        self.assertIsNotNone(self.system.vectorspace, "Vector Space Analyst not initialized")

        # Specialists - Discrete Math
        self.assertIsNotNone(self.system.combinatorics, "Combinatorics Agent not initialized")
        self.assertIsNotNone(self.system.graphtheory, "Graph Theory Agent not initialized")

        # Specialists - Statistics
        self.assertIsNotNone(self.system.distribution, "Distribution Specialist not initialized")
        self.assertIsNotNone(self.system.bayesian, "Bayesian Inference Engine not initialized")
        self.assertIsNotNone(self.system.frequentist, "Frequentist Agent not initialized")

        # Numerical Fallback
        self.assertIsNotNone(self.system.numerical_utility, "Numerical Utility not initialized")

    def test_statistics_availability(self):
        """Test that statistics can be retrieved"""
        stats = self.system.get_statistics()
        self.assertIn('phase1', stats)
        self.assertIn('supervisors', stats)
        self.assertIn('specialists', stats)
        
        self.assertIn('algebra', stats['supervisors'])
        self.assertIn('calculus', stats['supervisors'])
        
        self.assertIn('arithmetic', stats['specialists'])
        self.assertIn('integration', stats['specialists'])

if __name__ == '__main__':
    unittest.main()
