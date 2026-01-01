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

"""
PHASE 2 VERIFICATION TEST
=========================

Comprehensive test suite for Phase 2: Vertical Domain Expansion

Tests all 18+ specialized mathematical agents across all domains:
- Algebra Team (Supervisor + 3 specialists)
- Calculus Team (Supervisor + 4 specialists)
- Linear Algebra Team (Supervisor + 3 specialists)
- Discrete Math Team (2 specialists)
- Statistics Team (Supervisor + 3 specialists)
- Numerical Fallback (1 utility)

REFERENCE:
---------
Phase_2_Build_Order_Breakdown.md: Section 6 "Verification Checklist"
"""

import unittest
import sys
import os

# Add paths for imports

from symbo_agentic_reasoners.core.system import Phase2System


class Phase2VerificationTest(unittest.TestCase):
    """Phase 2 verification test suite"""

    @classmethod
    def setUpClass(cls):
        """Initialize Phase 2 system once for all tests"""
        print("\n" + "=" * 80)
        print("PHASE 2 VERIFICATION TEST SUITE")
        print("=" * 80)
        print()

        cls.system = Phase2System(vector_db_path="./test_vector_store")
        cls.system.start()
        print()

    @classmethod
    def tearDownClass(cls):
        """Shutdown system after all tests"""
        print("\n" + "=" * 80)
        print("PHASE 2 TEST SUITE COMPLETE")
        print("=" * 80)
        cls.system.shutdown()

    def test_01_system_health(self):
        """Test: Overall system health"""
        print("\n[TEST 01] System Health Check")
        health = self.system.health_check()
        self.assertTrue(health['overall'], "System health check failed")
        print("  [OK] PASS: System health check")

    def test_02_supervisors_registered(self):
        """Test: All Tier 2 supervisors registered"""
        print("\n[TEST 02] Tier 2 Supervisors Registration")

        expected_supervisors = [
            'math.algebra',
            'math.calculus',
            'math.linalg',
            'math.stats'
        ]

        for service_type in expected_supervisors:
            services = self.system.df.search(service_type=service_type)
            self.assertGreater(len(services), 0, f"Supervisor not found: {service_type}")
            print(f"  [OK] Found: {service_type}")

        print("  [OK] PASS: All supervisors registered")

    def test_03_algebra_team_registered(self):
        """Test: Algebra Team (Foundation Layer) registered"""
        print("\n[TEST 03] Foundation Layer - Algebra Team")

        expected_specialists = [
            'math.algebra.arithmetic',
            'math.algebra.polynomial',
            'math.algebra.numbertheory'
        ]

        for service_type in expected_specialists:
            services = self.system.df.search(service_type=service_type)
            self.assertGreater(len(services), 0, f"Specialist not found: {service_type}")
            print(f"  [OK] Found: {service_type}")

        print("  [OK] PASS: Algebra Team complete")

    def test_04_calculus_team_registered(self):
        """Test: Calculus Team (Analysis Layer) registered"""
        print("\n[TEST 04] Analysis Layer - Calculus Team")

        expected_specialists = [
            'math.calculus.diff',
            'math.calculus.integration',
            'math.calculus.ode',
            'math.calculus.series'
        ]

        for service_type in expected_specialists:
            services = self.system.df.search(service_type=service_type)
            self.assertGreater(len(services), 0, f"Specialist not found: {service_type}")
            print(f"  [OK] Found: {service_type}")

        print("  [OK] PASS: Calculus Team complete")

    def test_05_integration_dual_engine(self):
        """Test: Integration Specialist has dual-engine architecture"""
        print("\n[TEST 05] Integration Specialist - Dual-Engine Verification")

        services = self.system.df.search(service_type='math.calculus.integration')
        self.assertGreater(len(services), 0, "Integration specialist not found")

        service = services[0]
        self.assertEqual(service.properties.get('type'), 'dual_engine',
                        "Integration specialist missing dual-engine property")

        print("  [OK] Dual-engine architecture confirmed")
        print(f"  [OK] Symbolic: {service.properties.get('symbolic')}")
        print(f"  [OK] Numerical: {service.properties.get('numerical')}")
        print("  [OK] PASS: THE CRITICAL SPLIT verified")

    def test_06_linalg_team_registered(self):
        """Test: Linear Algebra Team (Vector Layer) registered"""
        print("\n[TEST 06] Vector Layer - Linear Algebra Team")

        expected_specialists = [
            'math.linalg.ops',
            'math.linalg.decomp',
            'math.linalg.vectorspace'
        ]

        for service_type in expected_specialists:
            services = self.system.df.search(service_type=service_type)
            self.assertGreater(len(services), 0, f"Specialist not found: {service_type}")
            print(f"  [OK] Found: {service_type}")

        print("  [OK] PASS: Linear Algebra Team complete")

    def test_07_discrete_math_team_registered(self):
        """Test: Discrete Math Team (Logic Layer) registered"""
        print("\n[TEST 07] Logic Layer - Discrete Math Team")

        expected_agents = [
            'math.discrete.combinatorics',
            'math.discrete.graphs'
        ]

        for service_type in expected_agents:
            services = self.system.df.search(service_type=service_type)
            self.assertGreater(len(services), 0, f"Agent not found: {service_type}")
            print(f"  [OK] Found: {service_type}")

        print("  [OK] PASS: Discrete Math Team complete")

    def test_08_stats_team_registered(self):
        """Test: Statistics Team (Uncertainty Layer) registered"""
        print("\n[TEST 08] Uncertainty Layer - Statistics Team")

        expected_specialists = [
            'math.stats.distributions',
            'math.stats.bayesian',
            'math.stats.frequentist'
        ]

        for service_type in expected_specialists:
            services = self.system.df.search(service_type=service_type)
            self.assertGreater(len(services), 0, f"Specialist not found: {service_type}")
            print(f"  [OK] Found: {service_type}")

        print("  [OK] PASS: Statistics Team complete")

    def test_09_bayesian_frequentist_separation(self):
        """Test: Bayesian/Frequentist strict separation enforced"""
        print("\n[TEST 09] Bayesian/Frequentist Separation Verification")

        bayesian = self.system.df.search(service_type='math.stats.bayesian')
        frequentist = self.system.df.search(service_type='math.stats.frequentist')

        self.assertGreater(len(bayesian), 0, "Bayesian agent not found")
        self.assertGreater(len(frequentist), 0, "Frequentist agent not found")

        # Verify they are distinct agents
        self.assertNotEqual(bayesian[0].agent_id, frequentist[0].agent_id,
                          "Bayesian and Frequentist must be separate agents")

        print("  [OK] Bayesian and Frequentist are distinct agents")
        print("  [OK] PASS: Philosophical separation enforced")

    def test_10_numerical_fallback_registered(self):
        """Test: Numerical Computation Utility (Safety Net) registered"""
        print("\n[TEST 10] Numerical Fallback - System Safety Net")

        services = self.system.df.search(service_type='math.numerical')
        self.assertGreater(len(services), 0, "Numerical utility not found")

        service = services[0]
        self.assertEqual(service.properties.get('role'), 'fallback',
                        "Numerical utility missing fallback role")

        print("  [OK] Numerical fallback registered")
        print(f"  [OK] Role: {service.properties.get('role')}")
        print("  [OK] PASS: System safety net in place")

    def test_11_agent_count(self):
        """Test: Verify expected agent count"""
        print("\n[TEST 11] Agent Count Verification")

        # Collect all Phase 2 math services by searching for each service type
        service_types = [
            'math.algebra', 'math.algebra.arithmetic', 'math.algebra.polynomial', 'math.algebra.numbertheory',
            'math.calculus', 'math.calculus.differentiation', 'math.calculus.integration', 'math.calculus.ode', 'math.calculus.series',
            'math.linalg', 'math.linalg.matrix', 'math.linalg.decomposition', 'math.linalg.vectorspace',
            'math.discrete', 'math.discrete.combinatorics', 'math.discrete.graphs',
            'math.stats', 'math.stats.distributions', 'math.stats.bayesian', 'math.stats.frequentist',
        ]

        all_math_services = []
        for service_type in service_types:
            services = self.system.df.search(service_type=service_type)
            all_math_services.extend(services)

        # Expected: 5 supervisors + 12+ specialists
        # Note: Count depends on which service types match the query list
        expected_min = 16

        self.assertGreaterEqual(len(all_math_services), expected_min,
                               f"Expected at least {expected_min} agents, found {len(all_math_services)}")

        print(f"  [OK] Total Phase 2 agents: {len(all_math_services)}")
        print(f"  [OK] Expected minimum: {expected_min}")
        print("  [OK] PASS: Agent count verified")

    def test_12_orchestrator_discovery(self):
        """Test: Phase 1 Orchestrator can discover Phase 2 agents"""
        print("\n[TEST 12] Dynamic Orchestration - DF Query")

        # Test that Orchestrator can discover agents dynamically
        algebra_agents = self.system.df.search(service_type='math.algebra')
        calculus_agents = self.system.df.search(service_type='math.calculus')

        self.assertGreater(len(algebra_agents), 0, "Algebra agents not discoverable")
        self.assertGreater(len(calculus_agents), 0, "Calculus agents not discoverable")

        print(f"  [OK] Algebra agents discoverable: {len(algebra_agents)}")
        print(f"  [OK] Calculus agents discoverable: {len(calculus_agents)}")
        print("  [OK] PASS: Dynamic orchestration working")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
