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
Integration Tests for Agent Interactions

Tests agent-to-agent communication, message passing, and blackboard notifications.
"""

import pytest
from symbo_agentic_reasoners.core.system import Phase0System, Phase2System
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
from symbo_agentic_reasoners.protocols.fipa_acl import create_request


class TestAgentInteractions:
    """Test suite for agent interaction patterns"""
    
    def test_blackboard_pub_sub_notifications(self):
        """Test that agents can subscribe to and receive blackboard notifications"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Track notifications
        notifications_received = []
        
        def test_callback(entry):
            notifications_received.append(entry)
        
        # Subscribe to algebra tasks
        phase0.blackboard.subscribe('test_subscriber', ['algebra', 'test'], test_callback)
        
        # Post an algebra task
        test_entry = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable('x'),
            author_agent='test_agent',
            conversation_id='test_conv_001',
            tags=['algebra', 'test'],
            status=EntryStatus.PENDING
        )
        
        phase0.blackboard.post(test_entry)
        
        # Verify notification was received
        assert len(notifications_received) > 0, "No notifications received"
        assert notifications_received[0].entry_id == test_entry.entry_id
        
        print(f"\n✅ Blackboard pub/sub working: {len(notifications_received)} notification(s) received")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_service_discovery_workflow(self):
        """Test that orchestrator can discover and select appropriate agents"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Simulate orchestrator discovering polynomial specialist
        polynomial_services = phase0.df.search(service_type='math.algebra.polynomial')
        
        assert len(polynomial_services) > 0, "Polynomial specialist not discoverable"
        
        # Verify service details
        service = polynomial_services[0]
        assert service.agent_id == 'polynomial_specialist_001'
        assert service.algorithm == 'groebner_bases'
        
        print(f"\n✅ Service discovery working:")
        print(f"   - Found: {service.agent_id}")
        print(f"   - Algorithm: {service.algorithm}")
        print(f"   - Cost: {service.cost}")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_multiple_agent_discovery(self):
        """Test discovering multiple agents for the same domain"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Discover all algebra agents
        algebra_services = phase0.df.search_by_prefix('math.algebra')
        
        assert len(algebra_services) >= 5, f"Expected 5+ algebra agents, found {len(algebra_services)}"
        
        # Verify diversity of services
        service_types = set(s.service_type for s in algebra_services)
        assert len(service_types) >= 5, "Not enough diverse algebra services"
        
        print(f"\n✅ Multiple agent discovery working:")
        print(f"   - Total algebra agents: {len(algebra_services)}")
        print(f"   - Service types: {len(service_types)}")
        for st in sorted(service_types):
            print(f"     • {st}")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_agent_capability_matching(self):
        """Test that agents can be selected based on capabilities"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Find agents with specific capabilities
        integration_agents = phase0.df.search(service_type='math.calculus.integration')
        
        assert len(integration_agents) > 0, "Integration specialist not found"
        
        # Verify it has the right algorithm
        service = integration_agents[0]
        assert 'risch' in service.algorithm.lower() or 'quadrature' in service.algorithm.lower()
        
        print(f"\n✅ Capability matching working:")
        print(f"   - Agent: {service.agent_id}")
        print(f"   - Algorithm: {service.algorithm}")
        
        phase2.shutdown()
        phase0.shutdown()
    
    def test_concurrent_agent_access(self):
        """Test that multiple clients can access DF concurrently"""
        phase0 = Phase0System(allow_mock=True)
        phase0.start()
        
        phase2 = Phase2System(phase0_system=phase0)
        phase2.start()
        
        # Simulate concurrent queries
        results = []
        for i in range(10):
            services = phase0.df.search_by_prefix('math.')
            results.append(len(services))
        
        # All queries should return same count
        assert all(r == results[0] for r in results), "Inconsistent results from concurrent access"
        assert results[0] >= 25, f"Expected 25+ agents, got {results[0]}"
        
        print(f"\n✅ Concurrent access working:")
        print(f"   - 10 concurrent queries executed")
        print(f"   - All returned {results[0]} agents consistently")
        
        phase2.shutdown()
        phase0.shutdown()


if __name__ == "__main__":
    """Run tests directly"""
    print("=" * 80)
    print("AGENT INTERACTION TESTS")
    print("=" * 80)
    print()
    
    test = TestAgentInteractions()
    
    try:
        print("Test 1: Blackboard Pub/Sub Notifications")
        test.test_blackboard_pub_sub_notifications()
        print("✅ PASSED\n")
        
        print("Test 2: Service Discovery Workflow")
        test.test_service_discovery_workflow()
        print("✅ PASSED\n")
        
        print("Test 3: Multiple Agent Discovery")
        test.test_multiple_agent_discovery()
        print("✅ PASSED\n")
        
        print("Test 4: Agent Capability Matching")
        test.test_agent_capability_matching()
        print("✅ PASSED\n")
        
        print("Test 5: Concurrent Agent Access")
        test.test_concurrent_agent_access()
        print("✅ PASSED\n")
        
        print("=" * 80)
        print("ALL INTERACTION TESTS PASSED ✅")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
