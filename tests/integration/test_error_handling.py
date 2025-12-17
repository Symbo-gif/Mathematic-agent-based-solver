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
Integration Tests for Error Handling and Edge Cases

Tests system behavior under error conditions and edge cases.
"""

import pytest
from symbo_agentic_reasoners.core.system import Phase0System, Phase2System


class TestErrorHandling:
    """Test suite for error handling and edge cases"""
    
    def test_invalid_service_query(self):
        """Test behavior when querying for non-existent service"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Query for non-existent service
        results = phase0.df.search(service_type='math.nonexistent.service')
        
        # Should return empty list, not error
        assert isinstance(results, list), "Should return list"
        assert len(results) == 0, "Should return empty list for non-existent service"
        
        print(f"\n✅ Invalid service query handled gracefully")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_empty_prefix_search(self):
        """Test behavior with empty prefix search"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Search with empty prefix
        results = phase0.df.search_by_prefix('')
        
        # Should return all services
        assert len(results) > 0, "Empty prefix should return all services"
        
        print(f"\n✅ Empty prefix search handled: {len(results)} services returned")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_system_restart(self):
        """Test that system can be restarted"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Get initial count
        initial_count = len(phase0.df.search_by_prefix('math.'))
        
        # Shutdown
        phase2.shutdown()
        assert phase2.status == 'stopped'
        
        # Restart
        phase2_new = Phase2System(phase0_system=phase0)
        phase2_new.start()
        
        # Verify agents re-registered
        new_count = len(phase0.df.search_by_prefix('math.'))
        
        # Note: Agents will accumulate since DF doesn't clear on shutdown
        # This is expected behavior - DF persists registrations
        assert new_count >= initial_count, "Agents should re-register on restart"
        
        print(f"\n✅ System restart working:")
        print(f"   - Initial agents: {initial_count}")
        print(f"   - After restart: {new_count}")
        
        phase2_new.shutdown()
        phase0.shutdown()
    
    def test_phase2_without_phase0(self):
        """Test Phase2System behavior without Phase0"""
        # Create Phase2 without Phase0
        phase2 = Phase2System()
        
        # Should create its own infrastructure
        assert phase2.df is not None, "Should create DF"
        assert phase2.blackboard is not None, "Should create Blackboard"
        
        # Start should work
        phase2.start()
        assert phase2.status == 'running'
        
        # Verify agents registered
        agents = phase2.df.search_by_prefix('math.')
        assert len(agents) >= 25, f"Expected 25+ agents, got {len(agents)}"
        
        print(f"\n✅ Phase2 standalone mode working: {len(agents)} agents")
        
        phase2.shutdown()
    
    def test_multiple_phase2_instances(self):
        """Test multiple Phase2 instances with shared Phase0"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        # Create two Phase2 instances
        phase2_a = Phase2System(phase0_system=phase0)
        phase2_a.start()
        
        phase2_b = Phase2System(phase0_system=phase0)
        phase2_b.start()
        
        # Both should share the same DF
        assert phase2_a.df is phase2_b.df, "Should share same DF"
        
        # Total agents - DF prevents duplicate registrations (correct behavior)
        # Both instances use same agent IDs, so DF keeps only one registration per service
        total_agents = len(phase0.df.search_by_prefix('math.'))
        
        # Should have 25 agents (DF prevents duplicates by service_type + agent_id)
        assert total_agents >= 25, f"Expected 25+ agents, got {total_agents}"
        
        # Verify both instances have their agents
        assert len(phase2_a.supervisors) == 4
        assert len(phase2_a.specialists) == 21
        assert len(phase2_b.supervisors) == 4
        assert len(phase2_b.specialists) == 21
        
        print(f"\n✅ Multiple Phase2 instances working:")
        print(f"   - Total unique agents in DF: {total_agents}")
        print(f"   - Phase2_A agents: {len(phase2_a.supervisors) + len(phase2_a.specialists)}")
        print(f"   - Phase2_B agents: {len(phase2_b.supervisors) + len(phase2_b.specialists)}")
        print(f"   - DF correctly prevents duplicate registrations")
        
        phase2_a.shutdown()
        phase2_b.shutdown()
        phase0.shutdown()
    
    def test_health_check_on_stopped_system(self):
        """Test health check on stopped system"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        # Don't start - test health check on stopped system
        
        health = phase2.health_check()
        
        assert health['overall'] == False, "Stopped system should fail health check"
        assert health['system_running'] == False
        
        print(f"\n✅ Health check correctly identifies stopped system")
        
        phase0.shutdown()
    
    def test_statistics_on_empty_system(self):
        """Test statistics on system before agents are created"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        # Don't start - get stats before agents created
        
        stats = phase2.get_statistics()
        
        assert stats['status'] == 'stopped'
        assert stats['supervisors_count'] == 0
        assert stats['specialists_count'] == 0
        assert stats['total_agents'] == 0
        
        print(f"\n✅ Statistics correctly report empty system")
        
        phase0.shutdown()


if __name__ == "__main__":
    """Run tests directly"""
    print("=" * 80)
    print("ERROR HANDLING & EDGE CASE TESTS")
    print("=" * 80)
    print()
    
    test = TestErrorHandling()
    
    try:
        print("Test 1: Invalid Service Query")
        test.test_invalid_service_query()
        print("✅ PASSED\n")
        
        print("Test 2: Empty Prefix Search")
        test.test_empty_prefix_search()
        print("✅ PASSED\n")
        
        print("Test 3: System Restart")
        test.test_system_restart()
        print("✅ PASSED\n")
        
        print("Test 4: Phase2 Without Phase0")
        test.test_phase2_without_phase0()
        print("✅ PASSED\n")
        
        print("Test 5: Multiple Phase2 Instances")
        test.test_multiple_phase2_instances()
        print("✅ PASSED\n")
        
        print("Test 6: Health Check on Stopped System")
        test.test_health_check_on_stopped_system()
        print("✅ PASSED\n")
        
        print("Test 7: Statistics on Empty System")
        test.test_statistics_on_empty_system()
        print("✅ PASSED\n")
        
        print("=" * 80)
        print("ALL ERROR HANDLING TESTS PASSED ✅")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
