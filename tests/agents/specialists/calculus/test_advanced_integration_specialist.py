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
Tests for AdvancedIntegrationSpecialist

Standard 12-test pattern for specialists:
1. Initialization
2. Service registration
3-7. Core functionality tests (pattern classification, delegation)
8. Edge cases
9-10. BDI implementation
11. Concurrent requests
12. Statistics tracking
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.agents.specialists.calculus.advanced_integration_specialist import (
    AdvancedIntegrationSpecialist
)
from symbo_agentic_reasoners.core.bdi_agent import Intention
from symbo_agentic_reasoners.core.blackboard import EntryStatus


class TestAdvancedIntegrationSpecialist:
    """Test suite for AdvancedIntegrationSpecialist"""

    def setup_method(self):
        """Set up test fixtures"""
        self.specialist = AdvancedIntegrationSpecialist(
            agent_id='advanced_integration_test_001',
            df=None,
            blackboard=None
        )

    # Test 1: Initialization
    def test_initialization(self):
        """Test coordinator initializes correctly"""
        assert self.specialist.agent_id == 'advanced_integration_test_001'
        assert self.specialist.tasks_executed == 0
        assert self.specialist.tasks_succeeded == 0
        assert self.specialist.tasks_failed == 0
        assert self.specialist.delegations_made == 0
        assert self.specialist.fallbacks_used == 0
        assert isinstance(self.specialist.patterns_classified, dict)

    # Test 2: Service registration
    def test_service_registration(self):
        """Test coordinator registers with DF correctly"""
        mock_df = Mock()
        specialist = AdvancedIntegrationSpecialist(
            agent_id='advanced_integration_test_002',
            df=mock_df
        )

        # Verify register was called
        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.calculus.integration.advanced'
        assert call_args.agent_id == 'advanced_integration_test_002'

    # Test 3: Pattern classification - exp×trig
    def test_classify_exp_trig_pattern(self):
        """Test classification of exp×trig patterns"""
        patterns = [
            ('exp(x)*sin(x)', 'exp_trig_product'),
            ('exp(2*x)*cos(3*x)', 'exp_trig_product'),
            ('exp(-x)*sin(2*x)', 'exp_trig_product'),
        ]

        for expression, expected_pattern in patterns:
            result = self.specialist._classify_integration_pattern(expression, 'x')
            assert result == expected_pattern, f"Failed for {expression}: got {result}, expected {expected_pattern}"

    # Test 4: Pattern classification - repeated IBP
    def test_classify_repeated_ibp_pattern(self):
        """Test classification of high-degree polynomial × transcendental"""
        patterns = [
            ('x**3*exp(x)', 'repeated_ibp'),
            ('x^5*sin(x)', 'repeated_ibp'),
            ('x**4*cos(2*x)', 'repeated_ibp'),
        ]

        for expression, expected_pattern in patterns:
            result = self.specialist._classify_integration_pattern(expression, 'x')
            assert result == expected_pattern, f"Failed for {expression}: got {result}, expected {expected_pattern}"

    # Test 5: Pattern classification - chain rule
    def test_classify_chain_rule_pattern(self):
        """Test classification of chain rule patterns"""
        patterns = [
            ('sin(x**2)*x', 'chain_rule'),
            ('cos(ln(x))*1/x', 'chain_rule'),
            ('exp(x**2)*x', 'chain_rule'),
        ]

        for expression, expected_pattern in patterns:
            result = self.specialist._classify_integration_pattern(expression, 'x')
            # Should be either chain_rule or contain nested functions
            assert result in ['chain_rule', 'general'], f"Failed for {expression}: got {result}"

    # Test 6: Pattern classification - trig power
    def test_classify_trig_power_pattern(self):
        """Test classification of trig power patterns"""
        patterns = [
            ('sin(x)**4', 'trig_power'),
            ('cos(x)**5', 'trig_power'),
        ]

        for expression, expected_pattern in patterns:
            result = self.specialist._classify_integration_pattern(expression, 'x')
            assert result == expected_pattern, f"Failed for {expression}: got {result}, expected {expected_pattern}"

    # Test 7: Delegation to exp×trig specialist
    def test_delegation_to_exp_trig(self):
        """Test delegation to ExponentialTrigIntegrationSpecialist"""
        # Create mock DF with exp×trig specialist
        mock_df = Mock()
        mock_exp_trig = Mock()
        mock_exp_trig._integrate_exp_trig = Mock(return_value={
            'success': True,
            'solution': 'exp(x)*sin(x)/2',
            'method': 'reduction_formula'
        })

        mock_service = Mock()
        mock_service.instance = mock_exp_trig
        mock_df.search.return_value = [mock_service]

        specialist = AdvancedIntegrationSpecialist(
            agent_id='advanced_integration_test_007',
            df=mock_df
        )

        # Delegate
        result = specialist._delegate_to_exp_trig('exp(x)*sin(x)', 'x', Mock())

        assert result is not None
        assert result['success'] is True
        assert specialist.delegations_made == 1

    # Test 8: Edge cases - unknown pattern
    def test_unknown_pattern_fallback(self):
        """Test handling of patterns without specific specialist"""
        result = self.specialist._classify_integration_pattern('x^2 + 1', 'x')
        assert result == 'general'

    # Test 9: BDI - update_beliefs
    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard"""
        # Should not crash
        self.specialist.update_beliefs()

    def test_update_beliefs_with_tasks(self):
        """Test update_beliefs finds pending advanced tasks"""
        mock_blackboard = Mock()
        mock_task = Mock()
        mock_task.entry_id = 'task_advanced_123'
        mock_task.metadata = {'expression': 'exp(x)*sin(x)', 'complexity': 'advanced'}

        mock_blackboard.query_entries.return_value = [mock_task]

        specialist = AdvancedIntegrationSpecialist(
            agent_id='advanced_integration_test_009',
            blackboard=mock_blackboard
        )

        specialist.update_beliefs()

        # Should have created belief
        assert specialist.has_belief('pending_task_task_advanced_123')

    # Test 10: BDI - deliberate
    def test_deliberate_creates_intentions(self):
        """Test deliberate creates coordination plans"""
        mock_task = Mock()
        mock_task.entry_id = 'task_coord_456'

        self.specialist.add_belief('pending_task_task_coord_456', mock_task)

        intentions = self.specialist.deliberate()

        assert len(intentions) > 0
        intention = intentions[0]
        assert intention.plan_id == 'coordinate_integration_task_coord_456'
        assert 'classify_pattern' in intention.steps
        assert 'delegate_to_specialist' in intention.steps

    # Test 11: Concurrent task handling
    def test_concurrent_task_handling(self):
        """Test handling multiple tasks simultaneously"""
        tasks = []
        for i in range(3):
            task = Mock()
            task.entry_id = f'task_concurrent_{i}'
            task.metadata = {'expression': f'exp({i}*x)*sin(x)', 'complexity': 'advanced'}
            task.conversation_id = f'conv_{i}'
            tasks.append(task)

        # Simulate multiple pending tasks
        for task in tasks:
            self.specialist.add_belief(f'pending_task_{task.entry_id}', task)

        intentions = self.specialist.deliberate()

        # Should create one intention per task
        assert len(intentions) == 3

        # All should be unique
        plan_ids = [i.plan_id for i in intentions]
        assert len(set(plan_ids)) == 3

    # Test 12: Statistics tracking
    def test_statistics_tracking(self):
        """Test statistics are tracked correctly"""
        # Simulate task processing
        self.specialist.tasks_executed = 10
        self.specialist.tasks_succeeded = 7
        self.specialist.tasks_failed = 3
        self.specialist.delegations_made = 6
        self.specialist.fallbacks_used = 4
        self.specialist.patterns_classified = {
            'exp_trig_product': 5,
            'repeated_ibp': 2,
            'chain_rule': 1,
            'general': 2
        }

        stats = self.specialist.get_statistics()

        assert stats['tasks_executed'] == 10
        assert stats['tasks_succeeded'] == 7
        assert stats['tasks_failed'] == 3
        assert stats['delegations_made'] == 6
        assert stats['fallbacks_used'] == 4
        assert stats['success_rate'] == 70.0
        assert stats['patterns_classified']['exp_trig_product'] == 5

    # Additional test: Route selection
    def test_route_to_specialist_exp_trig(self):
        """Test routing decision for exp×trig pattern"""
        # Without DF, should gracefully handle
        result = self.specialist._route_to_specialist(
            'exp_trig_product',
            'exp(x)*sin(x)',
            'x',
            Mock()
        )

        # Without DF, should return None or error
        assert result is None or (isinstance(result, dict) and not result.get('success'))

    def test_route_to_specialist_general(self):
        """Test routing decision for general pattern falls back"""
        result = self.specialist._route_to_specialist(
            'general',
            'x^2',
            'x',
            Mock()
        )

        # Should attempt fallback
        assert self.specialist.fallbacks_used > 0


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
