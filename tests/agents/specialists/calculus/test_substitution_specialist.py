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
Tests for SubstitutionSpecialist

Standard 12-test pattern for specialists
"""

import pytest
from unittest.mock import Mock, MagicMock

from symbo_agentic_reasoners.agents.specialists.calculus.substitution_specialist import (
    SubstitutionSpecialist
)
from symbo_agentic_reasoners.core.bdi_agent import Intention
from symbo_agentic_reasoners.core.blackboard import EntryStatus


class TestSubstitutionSpecialist:
    """Test suite for SubstitutionSpecialist"""

    def setup_method(self):
        """Set up test fixtures"""
        self.specialist = SubstitutionSpecialist(
            agent_id='substitution_test_001',
            df=None,
            blackboard=None
        )

    # Test 1: Initialization
    def test_initialization(self):
        """Test specialist initializes correctly"""
        assert self.specialist.agent_id == 'substitution_test_001'
        assert self.specialist.tasks_executed == 0
        assert self.specialist.tasks_succeeded == 0
        assert self.specialist.tasks_failed == 0
        assert isinstance(self.specialist.substitutions_applied, dict)

    # Test 2: Service registration
    def test_service_registration(self):
        """Test specialist registers with DF correctly"""
        mock_df = Mock()
        specialist = SubstitutionSpecialist(
            agent_id='substitution_test_002',
            df=mock_df
        )

        # Verify register was called
        assert mock_df.register.called
        call_args = mock_df.register.call_args[0][0]
        assert call_args.service_type == 'math.calculus.integration.substitution'
        assert call_args.agent_id == 'substitution_test_002'

    # Test 3: Chain rule pattern detection
    def test_detect_chain_rule_pattern(self):
        """Test detection of chain rule patterns"""
        patterns = [
            ('sin(x**2)*x', 'chain_rule'),
            ('cos(x**3)*x', 'chain_rule'),
            ('exp(x**2)*x', 'chain_rule'),
        ]

        for expression, expected_type in patterns:
            result = self.specialist._detect_substitution_pattern(expression, 'x')
            assert result is not None, f"Failed to detect pattern for {expression}"
            assert result['type'] == expected_type

    # Test 4: Trig substitution pattern detection
    def test_detect_trig_substitution(self):
        """Test detection of trig substitution patterns"""
        # sqrt(1-x^2) pattern
        result = self.specialist._detect_substitution_pattern('sqrt(1-x**2)', 'x')
        assert result is not None
        assert result['type'] == 'trig_substitution'
        assert 'sqrt(1-x^2)' in result['form']

    # Test 5: Rational substitution pattern detection
    def test_detect_rational_substitution(self):
        """Test detection of rational substitution patterns"""
        # 1/(2x+1)^2 pattern
        result = self.specialist._detect_substitution_pattern('1/(2*x+1)**2', 'x')
        assert result is not None
        assert result['type'] == 'rational_substitution'

    # Test 6: Chain rule substitution application
    def test_apply_chain_rule_substitution_sin(self):
        """Test applying chain rule substitution for sin(x^2)*x"""
        substitution = {
            'type': 'chain_rule',
            'u_substitution': 'x**2',
            'outer_function': 'sin',
            'power': 2
        }

        result = self.specialist._apply_chain_rule_substitution(substitution, 'sin(x**2)*x', 'x')

        assert result['success'] is True
        assert 'cos(x**2)' in result['solution']
        assert result['method'] == 'u_substitution_chain_rule'

    # Test 7: Rational substitution application
    def test_apply_rational_substitution(self):
        """Test applying rational substitution for 1/(ax+b)"""
        substitution = {
            'type': 'rational_substitution',
            'u_substitution': '2*x+1',
            'power': 1
        }

        result = self.specialist._apply_rational_substitution(substitution, '1/(2*x+1)', 'x')

        assert result['success'] is True
        assert 'ln' in result['solution']
        assert result['method'] == 'u_substitution_rational'

    # Test 8: Coefficient extraction from linear expressions
    def test_extract_linear_coefficient(self):
        """Test extracting coefficient from ax+b expressions"""
        assert self.specialist._extract_linear_coefficient('2*x+1', 'x') == 2.0
        assert self.specialist._extract_linear_coefficient('3*x-5', 'x') == 3.0
        assert self.specialist._extract_linear_coefficient('x+1', 'x') == 1.0
        assert self.specialist._extract_linear_coefficient('-x+2', 'x') == -1.0

    # Test 9: BDI - update_beliefs
    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs with no blackboard"""
        # Should not crash
        self.specialist.update_beliefs()

    # Test 10: BDI - deliberate
    def test_deliberate_creates_intentions(self):
        """Test deliberate creates substitution plans"""
        mock_task = Mock()
        mock_task.entry_id = 'task_sub_789'

        self.specialist.add_belief('pending_task_task_sub_789', mock_task)

        intentions = self.specialist.deliberate()

        assert len(intentions) > 0
        intention = intentions[0]
        assert intention.plan_id == 'substitute_integrate_task_sub_789'
        assert 'detect_pattern' in intention.steps
        assert 'apply_substitution' in intention.steps
        assert 'back_substitute' in intention.steps

    # Test 11: Concurrent task handling
    def test_concurrent_task_handling(self):
        """Test handling multiple tasks"""
        tasks = []
        for i in range(3):
            task = Mock()
            task.entry_id = f'task_sub_conc_{i}'
            task.metadata = {'expression': f'sin(x**{i+2})*x'}
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
        self.specialist.tasks_executed = 10
        self.specialist.tasks_succeeded = 8
        self.specialist.tasks_failed = 2
        self.specialist.substitutions_applied = {
            'chain_rule': 5,
            'trig_substitution': 2,
            'rational_substitution': 3
        }
        self.specialist.verifications_passed = 8

        stats = self.specialist.get_statistics()

        assert stats['tasks_executed'] == 10
        assert stats['tasks_succeeded'] == 8
        assert stats['tasks_failed'] == 2
        assert stats['success_rate'] == 80.0
        assert stats['substitutions_by_type']['chain_rule'] == 5


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
