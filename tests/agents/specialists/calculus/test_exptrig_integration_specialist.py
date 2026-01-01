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
Tests for ExponentialTrigIntegrationSpecialist

Standard 12-test pattern for specialists:
1. Initialization
2. Service registration
3-7. Core functionality tests
8. Edge cases
9-10. BDI implementation
11. Concurrent requests
12. Statistics tracking
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.agents.specialists.calculus.exp_trig_integration_specialist import (
    ExponentialTrigIntegrationSpecialist
)
from symbo_agentic_reasoners.core.bdi_agent import Intention
from symbo_agentic_reasoners.core.blackboard import EntryStatus


class TestExponentialTrigIntegrationSpecialist:
    """Test suite for ExponentialTrigIntegrationSpecialist"""

    def setup_method(self):
        """Set up test fixtures"""
        self.specialist = ExponentialTrigIntegrationSpecialist(
            agent_id='exp_trig_test_001',
            df=None,  # No DF for unit tests
            blackboard=None  # No Blackboard for unit tests
        )

    # Test 1: Initialization
    def test_initialization(self):
        """Test specialist initializes correctly"""
        assert self.specialist.agent_id == 'exp_trig_test_001'
        assert self.specialist.tasks_executed == 0
        assert self.specialist.tasks_succeeded == 0
        assert self.specialist.tasks_failed == 0
        assert self.specialist.formulas_applied == 0

    # Test 2: Service registration
    def test_service_registration(self):
        """Test specialist registers with DF correctly"""
        mock_df = Mock()
        specialist = ExponentialTrigIntegrationSpecialist(
            agent_id='exp_trig_test_002',
            df=mock_df
        )

        # Verify register was called
        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.calculus.integration.exp_trig'
        assert call_args.agent_id == 'exp_trig_test_002'

    # Test 3: exp(x)*sin(x) integration
    def test_exp_sin_simple(self):
        """Test ∫exp(x)*sin(x)dx = (exp(x)/2)[sin(x) - cos(x)]"""
        result = self.specialist._integrate_exp_trig('exp(x)*sin(x)', 'x')

        assert result['success'] is True
        assert result['method'] == 'exp_trig_reduction_formula'
        assert result['coefficients']['a'] == 1.0
        assert result['coefficients']['b'] == 1.0
        assert 'sin(1.0*x)' in result['solution']
        assert 'cos(1.0*x)' in result['solution']
        assert '/ 2' in result['solution']  # (1² + 1²) = 2

    # Test 4: exp(x)*cos(x) integration
    def test_exp_cos_simple(self):
        """Test ∫exp(x)*cos(x)dx = (exp(x)/2)[cos(x) + sin(x)]"""
        result = self.specialist._integrate_exp_trig('exp(x)*cos(x)', 'x')

        assert result['success'] is True
        assert result['coefficients']['a'] == 1.0
        assert result['coefficients']['b'] == 1.0
        assert 'cos(1.0*x)' in result['solution']
        assert 'sin(1.0*x)' in result['solution']

    # Test 5: exp(2x)*sin(3x) with scaled coefficients
    def test_exp_sin_scaled(self):
        """Test ∫exp(2x)*sin(3x)dx with a=2, b=3"""
        result = self.specialist._integrate_exp_trig('exp(2*x)*sin(3*x)', 'x')

        assert result['success'] is True
        assert result['coefficients']['a'] == 2.0
        assert result['coefficients']['b'] == 3.0
        # Denominator: 2² + 3² = 13
        assert '/ 13' in result['solution']

    # Test 6: exp(-x)*cos(2x) with negative coefficient
    def test_exp_cos_negative(self):
        """Test ∫exp(-x)*cos(2x)dx with a=-1, b=2"""
        result = self.specialist._integrate_exp_trig('exp(-x)*cos(2*x)', 'x')

        assert result['success'] is True
        assert result['coefficients']['a'] == -1.0
        assert result['coefficients']['b'] == 2.0
        # Denominator: (-1)² + 2² = 5
        assert '/ 5' in result['solution']

    # Test 7: Coefficient extraction
    def test_coefficient_extraction(self):
        """Test coefficient extraction from various formats"""
        # Simple variable
        assert self.specialist._extract_coefficient('x', 'x') == 1.0

        # Negative variable
        assert self.specialist._extract_coefficient('-x', 'x') == -1.0

        # Coefficient * variable
        assert self.specialist._extract_coefficient('2*x', 'x') == 2.0
        assert self.specialist._extract_coefficient('x*3', 'x') == 3.0

        # Constant (no variable)
        assert self.specialist._extract_coefficient('5', 'x') == 5.0

    # Test 8: Edge cases and error handling
    def test_non_exp_trig_pattern(self):
        """Test handling of non-exp×trig patterns"""
        result = self.specialist._integrate_exp_trig('x^2 + 1', 'x')

        assert result['success'] is False
        assert 'error' in result

    def test_degenerate_denominator(self):
        """Test handling of a²+b²=0 case (should not occur in practice)"""
        # Manually call with a=0, b=0
        result = self.specialist._apply_reduction_formula(0.0, 0.0, 'sin', 'x')

        assert result['success'] is False
        assert 'Denominator' in result['error']

    # Test 9: BDI - update_beliefs
    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard"""
        # Should not crash
        self.specialist.update_beliefs()

    def test_update_beliefs_with_tasks(self):
        """Test update_beliefs finds pending tasks"""
        mock_blackboard = Mock()
        mock_task = Mock()
        mock_task.entry_id = 'task_123'
        mock_task.metadata = {'expression': 'exp(x)*sin(x)'}

        mock_blackboard.query_entries.return_value = [mock_task]

        specialist = ExponentialTrigIntegrationSpecialist(
            agent_id='exp_trig_test_009',
            blackboard=mock_blackboard
        )

        specialist.update_beliefs()

        # Should have created belief
        assert specialist.has_belief('pending_task_task_123')

    # Test 10: BDI - deliberate
    def test_deliberate_creates_intentions(self):
        """Test deliberate creates integration plans"""
        mock_task = Mock()
        mock_task.entry_id = 'task_456'

        self.specialist.add_belief('pending_task_task_456', mock_task)

        intentions = self.specialist.deliberate()

        assert len(intentions) > 0
        intention = intentions[0]
        assert intention.plan_id == 'integrate_exp_trig_task_456'
        assert 'apply_reduction_formula' in intention.steps

    # Test 11: Concurrent requests (simulated)
    def test_concurrent_task_handling(self):
        """Test handling multiple tasks"""
        tasks = []
        for i in range(5):
            task = Mock()
            task.entry_id = f'task_{i}'
            task.metadata = {'expression': f'exp({i}*x)*sin(x)'}
            task.conversation_id = f'conv_{i}'
            tasks.append(task)

        # Simulate processing all tasks
        for task in tasks:
            self.specialist.add_belief(f'pending_task_{task.entry_id}', task)

        intentions = self.specialist.deliberate()

        # Should create one intention per task
        assert len(intentions) == 5

        # All should be unique
        plan_ids = [i.plan_id for i in intentions]
        assert len(set(plan_ids)) == 5

    # Test 12: Statistics tracking
    def test_statistics_tracking(self):
        """Test statistics are tracked correctly"""
        # Simulate some task processing
        mock_task = Mock()
        mock_task.entry_id = 'task_stats'
        mock_task.metadata = {'expression': 'exp(x)*sin(x)', 'variable': 'x'}
        mock_task.conversation_id = 'conv_stats'

        # Process task (without blackboard, will just update stats)
        self.specialist.tasks_executed = 5
        self.specialist.tasks_succeeded = 3
        self.specialist.tasks_failed = 2
        self.specialist.formulas_applied = 3

        stats = self.specialist.get_statistics()

        assert stats['tasks_executed'] == 5
        assert stats['tasks_succeeded'] == 3
        assert stats['tasks_failed'] == 2
        assert stats['formulas_applied'] == 3
        assert stats['success_rate'] == 60.0

    # Additional Test: Formula application
    def test_apply_reduction_formula_sin(self):
        """Test reduction formula application for sin"""
        result = self.specialist._apply_reduction_formula(2.0, 3.0, 'sin', 'x')

        assert result['success'] is True
        assert '2.0*sin(3.0*x)' in result['solution']
        assert '3.0*cos(3.0*x)' in result['solution']
        assert '/ 13' in result['solution']  # 2² + 3² = 13

    def test_apply_reduction_formula_cos(self):
        """Test reduction formula application for cos"""
        result = self.specialist._apply_reduction_formula(1.0, 2.0, 'cos', 'x')

        assert result['success'] is True
        assert '1.0*cos(2.0*x)' in result['solution']
        assert '2.0*sin(2.0*x)' in result['solution']
        assert '/ 5' in result['solution']  # 1² + 2² = 5


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
