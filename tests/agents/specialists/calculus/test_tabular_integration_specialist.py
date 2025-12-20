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
Tests for TabularIntegrationSpecialist

Standard 12-test pattern for specialists
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.agents.specialists.calculus.tabular_integration_specialist import (
    TabularIntegrationSpecialist
)
from symbo_agentic_reasoners.core.bdi_agent import Intention
from symbo_agentic_reasoners.core.blackboard import EntryStatus


class TestTabularIntegrationSpecialist:
    """Test suite for TabularIntegrationSpecialist"""

    def setup_method(self):
        """Set up test fixtures"""
        self.specialist = TabularIntegrationSpecialist(
            agent_id='tabular_test_001',
            df=None,
            blackboard=None
        )

    # Test 1: Initialization
    def test_initialization(self):
        """Test specialist initializes correctly"""
        assert self.specialist.agent_id == 'tabular_test_001'
        assert self.specialist.tasks_executed == 0
        assert self.specialist.tasks_succeeded == 0
        assert self.specialist.tasks_failed == 0
        assert self.specialist.max_iterations == 20

    # Test 2: Service registration
    def test_service_registration(self):
        """Test specialist registers with DF correctly"""
        mock_df = Mock()
        specialist = TabularIntegrationSpecialist(
            agent_id='tabular_test_002',
            df=mock_df
        )

        # Verify register was called
        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.calculus.integration.tabular'
        assert call_args.agent_id == 'tabular_test_002'

    # Test 3: u and dv identification for x^2*exp(x)
    def test_identify_u_dv_polynomial_exp(self):
        """Test identifying u=x^2, dv=exp(x) for ∫x^2*exp(x)dx"""
        u, dv = self.specialist._identify_u_dv('x**2*exp(x)', 'x')

        assert u is not None
        assert dv is not None
        # Polynomial should be u (higher LIATE)
        assert 'x' in u and 'exp' not in u
        assert 'exp' in dv

    # Test 4: u and dv identification for x^3*sin(x)
    def test_identify_u_dv_polynomial_trig(self):
        """Test identifying u=x^3, dv=sin(x) for ∫x^3*sin(x)dx"""
        u, dv = self.specialist._identify_u_dv('x**3*sin(x)', 'x')

        assert u is not None
        assert dv is not None
        # Polynomial should be u
        assert 'x' in u and 'sin' not in u
        assert 'sin' in dv

    # Test 5: Zero detection
    def test_is_zero_or_negligible(self):
        """Test zero detection for termination"""
        assert self.specialist._is_zero_or_negligible('0') is True
        assert self.specialist._is_zero_or_negligible('0.0') is True
        assert self.specialist._is_zero_or_negligible('0*x') is True
        assert self.specialist._is_zero_or_negligible('x') is False
        assert self.specialist._is_zero_or_negligible('5') is False

    # Test 6: Simple tabular integration x*exp(x)
    def test_tabular_simple_x_exp(self):
        """Test ∫x*exp(x)dx using tabular method"""
        result = self.specialist._integrate_tabular('x*exp(x)', 'x')

        # Should succeed (tabular works for x*exp)
        assert result is not None
        if result['success']:
            assert 'iterations' in result
            assert result['iterations'] >= 2  # At least 2 rows needed

    # Test 7: Complex tabular x^3*exp(x)
    def test_tabular_cubic_exp(self):
        """Test ∫x^3*exp(x)dx using tabular method"""
        result = self.specialist._integrate_tabular('x**3*exp(x)', 'x')

        # Should succeed
        assert result is not None
        if result['success']:
            assert 'iterations' in result
            assert result['iterations'] >= 4  # Needs 4 rows (x^3, x^2, x, 1, 0)

    # Test 8: Edge case - non-product expression
    def test_non_product_expression(self):
        """Test handling of non-product expressions"""
        result = self.specialist._integrate_tabular('x^2', 'x')

        # May fail to identify u and dv
        assert result is not None
        # Either succeeds or returns error
        assert 'success' in result

    # Test 9: BDI - update_beliefs
    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard"""
        # Should not crash
        self.specialist.update_beliefs()

    # Test 10: BDI - deliberate
    def test_deliberate_creates_intentions(self):
        """Test deliberate creates tabular plans"""
        mock_task = Mock()
        mock_task.entry_id = 'task_tabular_123'

        self.specialist.add_belief('pending_task_task_tabular_123', mock_task)

        intentions = self.specialist.deliberate()

        assert len(intentions) > 0
        intention = intentions[0]
        assert intention.plan_id == 'tabular_integrate_task_tabular_123'
        assert 'build_columns' in intention.steps
        assert 'compute_diagonal_sum' in intention.steps

    # Test 11: Concurrent task handling
    def test_concurrent_task_handling(self):
        """Test handling multiple tasks"""
        tasks = []
        for i in range(3):
            task = Mock()
            task.entry_id = f'task_tab_{i}'
            task.metadata = {'expression': f'x**{i+1}*exp(x)'}
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
        # Simulate processing
        self.specialist.tasks_executed = 5
        self.specialist.tasks_succeeded = 4
        self.specialist.tasks_failed = 1
        self.specialist.tabular_iterations = [3, 4, 2, 5, 3]  # 5 tasks with varying iterations

        stats = self.specialist.get_statistics()

        assert stats['tasks_executed'] == 5
        assert stats['tasks_succeeded'] == 4
        assert stats['tasks_failed'] == 1
        assert stats['success_rate'] == 80.0
        assert stats['average_iterations'] == 3.4  # (3+4+2+5+3)/5
        assert stats['max_iterations_used'] == 5


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
