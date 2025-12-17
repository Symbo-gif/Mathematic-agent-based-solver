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

"""
Integration Tests for Agent Registration System

Tests that all Phase 2 agents successfully register with the Directory Facilitator
and are discoverable by the orchestrator.

This addresses the critical issue: "0 agents discoverable despite 71 implementations"
"""

import pytest
from symbo_agentic_reasoners.core.system import Phase0System, Phase2System


class TestAgentRegistration:
    """Test suite for agent registration system"""
    
    def test_phase2_system_initialization(self):
        """Test that Phase2System initializes correctly"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        
        assert phase2.df is not None
        assert phase2.blackboard is not None
        assert phase2.status == 'stopped'
        
        phase0.shutdown()
    
    def test_phase2_system_starts_and_bootstraps_agents(self):
        """Test that Phase2System starts and bootstraps all agents"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Verify system is running
        assert phase2.status == 'running'
        
        # Verify agents were instantiated
        assert len(phase2.supervisors) >= 4, f"Expected 4+ supervisors, got {len(phase2.supervisors)}"
        assert len(phase2.specialists) >= 20, f"Expected 20+ specialists, got {len(phase2.specialists)}"
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_agents_register_with_directory_facilitator(self):
        """Test that agents register with DF during initialization"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        # Get initial DF count (infrastructure services)
        initial_math_services = phase0.df.search_by_prefix('math.')
        initial_count = len(initial_math_services)
        
        # Start Phase 2
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Verify agents registered
        agent_services = phase0.df.search_by_prefix('math.')
        
        assert len(agent_services) > initial_count, "No agents registered with DF"
        assert len(agent_services) >= 24, f"Expected 24+ agents, got {len(agent_services)}"
        
        print(f"\n✅ Successfully registered {len(agent_services)} mathematical agents")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_agents_discoverable_by_service_type(self):
        """Test that agents can be discovered by service type"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Test discovery by domain
        algebra_agents = phase0.df.search(service_type='math.algebra')
        assert len(algebra_agents) > 0, "No algebra agents found"
        
        calculus_agents = phase0.df.search(service_type='math.calculus')
        assert len(calculus_agents) > 0, "No calculus agents found"
        
        # Linear algebra agents use both math.linalg and math.linear_algebra
        linalg_agents = phase0.df.search_by_prefix('math.linalg')
        linalg_agents.extend(phase0.df.search_by_prefix('math.linear_algebra'))
        assert len(linalg_agents) > 0, "No linear algebra agents found"
        
        stats_agents = phase0.df.search(service_type='math.stats')
        assert len(stats_agents) > 0, "No statistics agents found"
        
        print(f"\n✅ Agent discovery working:")
        print(f"   - Algebra: {len(algebra_agents)} agents")
        print(f"   - Calculus: {len(calculus_agents)} agents")
        print(f"   - Linear Algebra: {len(linalg_agents)} agents")
        print(f"   - Statistics: {len(stats_agents)} agents")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_specific_specialists_discoverable(self):
        """Test that specific specialist types are discoverable"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Test specific service types
        polynomial_agents = phase0.df.search(service_type='math.algebra.polynomial')
        assert len(polynomial_agents) > 0, "Polynomial specialist not found"
        
        integration_agents = phase0.df.search(service_type='math.calculus.integration')
        assert len(integration_agents) > 0, "Integration specialist not found"
        
        # Matrix operations uses math.linalg.ops
        matrix_agents = phase0.df.search(service_type='math.linalg.ops')
        assert len(matrix_agents) > 0, "Matrix operations specialist not found"
        
        print(f"\n✅ Specific specialists discoverable:")
        print(f"   - Polynomial: {polynomial_agents[0].agent_id if polynomial_agents else 'None'}")
        print(f"   - Integration: {integration_agents[0].agent_id if integration_agents else 'None'}")
        print(f"   - Matrix Ops: {matrix_agents[0].agent_id if matrix_agents else 'None'}")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_phase2_health_check(self):
        """Test Phase2System health check"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Run health check
        health = phase2.health_check()
        
        assert health['overall'] == True, "Phase 2 health check failed"
        assert health['system_running'] == True
        assert health['agents_instantiated'] == True
        assert health['df_registration'] == True
        
        print(f"\n✅ Phase 2 health check passed")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_phase2_statistics(self):
        """Test Phase2System statistics reporting"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Get statistics
        stats = phase2.get_statistics()
        
        assert stats['status'] == 'running'
        assert stats['supervisors_count'] >= 4
        assert stats['specialists_count'] >= 20
        assert stats['total_agents'] >= 24
        assert 'registered_agents' in stats
        
        print(f"\n✅ Phase 2 Statistics:")
        print(f"   - Status: {stats['status']}")
        print(f"   - Supervisors: {stats['supervisors_count']}")
        print(f"   - Specialists: {stats['specialists_count']}")
        print(f"   - Total Agents: {stats['total_agents']}")
        print(f"   - Registered with DF: {stats.get('registered_agents', 'N/A')}")
        
        phase2.shutdown()
        phase0.shutdown()


if __name__ == "__main__":
    """Run tests directly"""
    print("=" * 80)
    print("AGENT REGISTRATION SYSTEM TESTS")
    print("=" * 80)
    print()
    
    test = TestAgentRegistration()
    
    try:
        print("Test 1: Phase2System Initialization")
        test.test_phase2_system_initialization()
        print("✅ PASSED\n")
        
        print("Test 2: Phase2System Starts and Bootstraps Agents")
        test.test_phase2_system_starts_and_bootstraps_agents()
        print("✅ PASSED\n")
        
        print("Test 3: Agents Register with Directory Facilitator")
        test.test_agents_register_with_directory_facilitator()
        print("✅ PASSED\n")
        
        print("Test 4: Agents Discoverable by Service Type")
        test.test_agents_discoverable_by_service_type()
        print("✅ PASSED\n")
        
        print("Test 5: Specific Specialists Discoverable")
        test.test_specific_specialists_discoverable()
        print("✅ PASSED\n")
        
        print("Test 6: Phase2 Health Check")
        test.test_phase2_health_check()
        print("✅ PASSED\n")
        
        print("Test 7: Phase2 Statistics")
        test.test_phase2_statistics()
        print("✅ PASSED\n")
        
        print("=" * 80)
        print("ALL TESTS PASSED ✅")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
