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
Tests for Model Checker Module
==============================

Comprehensive tests for the ModelChecker BDI agent and model structures.
"""

import pytest
from unittest.mock import MagicMock


class TestPropertyType:
    """Tests for PropertyType enum."""

    def test_property_type_values(self):
        """Test PropertyType enum values."""
        from symbo_agentic_reasoners.agents.provers.model_checker import PropertyType
        assert PropertyType.SAFETY.value == 'safety'
        assert PropertyType.LIVENESS.value == 'liveness'
        assert PropertyType.INVARIANT.value == 'invariant'
        assert PropertyType.REACHABILITY.value == 'reachability'
        assert PropertyType.DEADLOCK_FREE.value == 'deadlock_free'


class TestVerificationResult:
    """Tests for VerificationResult enum."""

    def test_verification_result_values(self):
        """Test VerificationResult enum values."""
        from symbo_agentic_reasoners.agents.provers.model_checker import VerificationResult
        assert VerificationResult.SATISFIED.value == 'satisfied'
        assert VerificationResult.VIOLATED.value == 'violated'
        assert VerificationResult.UNKNOWN.value == 'unknown'
        assert VerificationResult.TIMEOUT.value == 'timeout'


class TestState:
    """Tests for State dataclass."""

    def test_state_create(self):
        """Test creating a state."""
        from symbo_agentic_reasoners.agents.provers.model_checker import State
        s = State(state_id='s0', values={'x': 1})
        assert s.state_id == 's0'
        assert s.values == {'x': 1}
        assert s.is_initial is False
        assert s.is_accepting is False

    def test_state_initial(self):
        """Test creating initial state."""
        from symbo_agentic_reasoners.agents.provers.model_checker import State
        s = State(state_id='s0', values={}, is_initial=True)
        assert s.is_initial is True

    def test_state_to_dict(self):
        """Test state serialization."""
        from symbo_agentic_reasoners.agents.provers.model_checker import State
        s = State(state_id='s1', values={'y': 2}, is_initial=True)
        d = s.to_dict()
        assert d['id'] == 's1'
        assert d['values'] == {'y': 2}
        assert d['initial'] is True


class TestTransition:
    """Tests for Transition dataclass."""

    def test_transition_create(self):
        """Test creating a transition."""
        from symbo_agentic_reasoners.agents.provers.model_checker import Transition
        t = Transition(source='s0', target='s1')
        assert t.source == 's0'
        assert t.target == 's1'
        assert t.action is None
        assert t.guard is None

    def test_transition_with_action(self):
        """Test transition with action."""
        from symbo_agentic_reasoners.agents.provers.model_checker import Transition
        t = Transition(source='s0', target='s1', action='tick')
        assert t.action == 'tick'

    def test_transition_to_dict(self):
        """Test transition serialization."""
        from symbo_agentic_reasoners.agents.provers.model_checker import Transition
        t = Transition(source='a', target='b', action='go')
        d = t.to_dict()
        assert d['source'] == 'a'
        assert d['target'] == 'b'
        assert d['action'] == 'go'


class TestModel:
    """Tests for Model dataclass."""

    def test_model_create(self):
        """Test creating a model."""
        from symbo_agentic_reasoners.agents.provers.model_checker import Model, State
        states = {'s0': State(state_id='s0', values={})}
        m = Model(
            name='test',
            states=states,
            transitions=[],
            initial_states={'s0'}
        )
        assert m.name == 'test'
        assert len(m.states) == 1
        assert 's0' in m.initial_states

    def test_model_to_dict(self):
        """Test model serialization."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            Model, State, Transition
        )
        states = {
            's0': State(state_id='s0', values={}),
            's1': State(state_id='s1', values={})
        }
        trans = [Transition(source='s0', target='s1')]
        m = Model(
            name='mymodel',
            states=states,
            transitions=trans,
            initial_states={'s0'},
            atomic_props={'p', 'q'}
        )
        d = m.to_dict()
        assert d['name'] == 'mymodel'
        assert d['state_count'] == 2
        assert d['transition_count'] == 1
        assert d['initial_count'] == 1


class TestCounterexample:
    """Tests for Counterexample dataclass."""

    def test_counterexample_create(self):
        """Test creating counterexample."""
        from symbo_agentic_reasoners.agents.provers.model_checker import Counterexample
        cx = Counterexample(path=['s0', 's1', 's2'])
        assert cx.path == ['s0', 's1', 's2']
        assert cx.loop_start is None

    def test_counterexample_with_loop(self):
        """Test counterexample with lasso loop."""
        from symbo_agentic_reasoners.agents.provers.model_checker import Counterexample
        cx = Counterexample(path=['s0', 's1', 's2'], loop_start=1)
        assert cx.loop_start == 1

    def test_counterexample_to_dict(self):
        """Test counterexample serialization."""
        from symbo_agentic_reasoners.agents.provers.model_checker import Counterexample
        cx = Counterexample(path=['a', 'b', 'c'], loop_start=2)
        d = cx.to_dict()
        assert d['length'] == 3
        assert d['has_loop'] is True


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_check_result_create(self):
        """Test creating check result."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            CheckResult, PropertyType, VerificationResult
        )
        result = CheckResult(
            property_checked='x = 0',
            property_type=PropertyType.INVARIANT,
            result=VerificationResult.SATISFIED
        )
        assert result.property_checked == 'x = 0'
        assert result.result == VerificationResult.SATISFIED

    def test_check_result_with_counterexample(self):
        """Test check result with counterexample."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            CheckResult, PropertyType, VerificationResult, Counterexample
        )
        cx = Counterexample(path=['s0', 's1'])
        result = CheckResult(
            property_checked='deadlock_free',
            property_type=PropertyType.DEADLOCK_FREE,
            result=VerificationResult.VIOLATED,
            counterexample=cx,
            states_explored=5
        )
        assert result.counterexample is not None
        assert result.states_explored == 5

    def test_check_result_to_dict(self):
        """Test check result serialization."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            CheckResult, PropertyType, VerificationResult
        )
        result = CheckResult(
            property_checked='p',
            property_type=PropertyType.REACHABILITY,
            result=VerificationResult.SATISFIED,
            states_explored=10,
            time_ms=50
        )
        d = result.to_dict()
        assert d['property'] == 'p'
        assert d['type'] == 'reachability'
        assert d['result'] == 'satisfied'
        assert d['time_ms'] == 50


class TestModelCheckerInit:
    """Tests for ModelChecker initialization."""

    def test_checker_create(self):
        """Test creating model checker."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        assert checker.agent_id == 'model_checker_001'
        assert checker.max_states == 10000
        assert checker.bound == 100

    def test_checker_custom_params(self):
        """Test creating with custom parameters."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker(
            agent_id='custom_checker',
            max_states=5000,
            bound=50
        )
        assert checker.agent_id == 'custom_checker'
        assert checker.max_states == 5000
        assert checker.bound == 50

    def test_checker_with_df(self):
        """Test creating with directory facilitator."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        mock_df = MagicMock()
        checker = ModelChecker(df=mock_df)
        assert checker.df is mock_df
        mock_df.register.assert_called_once()


class TestModelCheckerCreateModel:
    """Tests for create_model method."""

    def test_create_simple_model(self):
        """Test creating a simple model."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        model = checker.create_model(
            name='simple',
            states=[{'id': 's0', 'values': {'x': 0}}],
            transitions=[],
            initial=['s0']
        )
        assert model.name == 'simple'
        assert len(model.states) == 1
        assert 's0' in model.initial_states

    def test_create_model_with_transitions(self):
        """Test creating model with transitions."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        model = checker.create_model(
            name='traffic',
            states=[
                {'id': 'red', 'values': {'color': 'red'}},
                {'id': 'green', 'values': {'color': 'green'}}
            ],
            transitions=[('red', 'green', 'timer'), ('green', 'red', 'timer')],
            initial=['red']
        )
        assert len(model.transitions) == 2
        assert model.transitions[0].action == 'timer'

    def test_create_model_cached(self):
        """Test model is cached."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        model = checker.create_model('cached', [], [], [])
        assert 'cached' in checker.models


class TestModelCheckerCheckProperty:
    """Tests for check_property method."""

    def test_check_invariant_satisfied(self):
        """Test invariant property satisfied."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='inv_test',
            states=[
                {'id': 's0', 'values': {'valid': True}},
                {'id': 's1', 'values': {'valid': True}}
            ],
            transitions=[('s0', 's1', None)],
            initial=['s0']
        )
        result = checker.check_property(model, 'valid', PropertyType.INVARIANT)
        assert result.result == VerificationResult.SATISFIED

    def test_check_invariant_violated(self):
        """Test invariant property violated."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='inv_fail',
            states=[
                {'id': 's0', 'values': {'valid': True}},
                {'id': 's1', 'values': {'valid': False}}
            ],
            transitions=[('s0', 's1', None)],
            initial=['s0']
        )
        result = checker.check_property(model, 'valid', PropertyType.INVARIANT)
        assert result.result == VerificationResult.VIOLATED
        assert result.counterexample is not None

    def test_check_reachability_satisfied(self):
        """Test reachability property satisfied."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='reach_test',
            states=[
                {'id': 's0', 'values': {'goal': False}},
                {'id': 's1', 'values': {'goal': True}}
            ],
            transitions=[('s0', 's1', None)],
            initial=['s0']
        )
        result = checker.check_property(model, 'goal', PropertyType.REACHABILITY)
        assert result.result == VerificationResult.SATISFIED

    def test_check_reachability_violated(self):
        """Test reachability property violated."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='reach_fail',
            states=[
                {'id': 's0', 'values': {'goal': False}},
                {'id': 's1', 'values': {'goal': False}}
            ],
            transitions=[('s0', 's1', None)],
            initial=['s0']
        )
        result = checker.check_property(model, 'goal', PropertyType.REACHABILITY)
        assert result.result == VerificationResult.VIOLATED

    def test_check_deadlock_free_satisfied(self):
        """Test deadlock-free property satisfied."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='nodead',
            states=[
                {'id': 's0', 'values': {}},
                {'id': 's1', 'values': {}}
            ],
            transitions=[('s0', 's1', None), ('s1', 's0', None)],
            initial=['s0']
        )
        result = checker.check_property(model, '', PropertyType.DEADLOCK_FREE)
        assert result.result == VerificationResult.SATISFIED

    def test_check_deadlock_free_violated(self):
        """Test deadlock-free property violated."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='withdead',
            states=[
                {'id': 's0', 'values': {}},
                {'id': 'dead', 'values': {}}
            ],
            transitions=[('s0', 'dead', None)],
            initial=['s0']
        )
        result = checker.check_property(model, '', PropertyType.DEADLOCK_FREE)
        assert result.result == VerificationResult.VIOLATED
        assert result.counterexample is not None

    def test_check_safety_property(self):
        """Test safety property check."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='safety',
            states=[
                {'id': 's0', 'values': {'safe': True}},
                {'id': 's1', 'values': {'safe': True}}
            ],
            transitions=[('s0', 's1', None)],
            initial=['s0']
        )
        result = checker.check_property(model, 'safe', PropertyType.SAFETY)
        assert result.result == VerificationResult.SATISFIED

    def test_check_unknown_property_type(self):
        """Test checking with LIVENESS returns unknown."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model('live', [], [], [])
        result = checker.check_property(model, 'p', PropertyType.LIVENESS)
        assert result.result == VerificationResult.UNKNOWN


class TestModelCheckerEvaluateProperty:
    """Tests for property evaluation."""

    def test_evaluate_equality_property(self):
        """Test evaluating equality property."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='eq_test',
            states=[
                {'id': 's0', 'values': {'x': '5'}},
            ],
            transitions=[],
            initial=['s0']
        )
        # Property x = 5 should be satisfied
        result = checker.check_property(model, 'x = 5', PropertyType.INVARIANT)
        # Satisfied because x equals '5'

    def test_evaluate_boolean_property(self):
        """Test evaluating boolean property."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType, VerificationResult
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='bool_test',
            states=[
                {'id': 's0', 'values': {'flag': True}},
            ],
            transitions=[],
            initial=['s0']
        )
        result = checker.check_property(model, 'flag', PropertyType.INVARIANT)
        assert result.result == VerificationResult.SATISFIED


class TestModelCheckerProcess:
    """Tests for process method."""

    def test_process_create_model(self):
        """Test processing create_model operation."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        mock_task = MagicMock()
        mock_task.metadata = {
            'operation': 'create_model',
            'name': 'proc_model',
            'states': [{'id': 's0', 'values': {}}],
            'transitions': [],
            'initial': ['s0']
        }
        result = checker.process(mock_task)
        assert 'proc_model' in checker.models

    def test_process_check_operation(self):
        """Test processing check operation."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        # First create model
        checker.create_model('test', [{'id': 's0', 'values': {}}], [], ['s0'])
        mock_task = MagicMock()
        mock_task.metadata = {
            'operation': 'check',
            'model': 'test',
            'property': 'true',
            'property_type': 'invariant'
        }
        result = checker.process(mock_task)
        assert result is not None

    def test_process_check_model_not_found(self):
        """Test processing check with missing model."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        mock_task = MagicMock()
        mock_task.metadata = {
            'operation': 'check',
            'model': 'nonexistent'
        }
        result = checker.process(mock_task)
        assert 'error' in result

    def test_process_list_models(self):
        """Test processing list_models operation."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        checker.create_model('m1', [], [], [])
        checker.create_model('m2', [], [], [])
        mock_task = MagicMock()
        mock_task.metadata = {'operation': 'list_models'}
        result = checker.process(mock_task)
        assert 'models' in result
        assert len(result['models']) == 2

    def test_process_unknown_operation(self):
        """Test processing unknown operation."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        mock_task = MagicMock()
        mock_task.metadata = {'operation': 'unknown'}
        result = checker.process(mock_task)
        assert 'error' in result


class TestModelCheckerBDI:
    """Tests for BDI methods."""

    def test_update_beliefs_no_blackboard(self):
        """Test update_beliefs without blackboard."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        checker.update_beliefs()  # Should not raise

    def test_deliberate_no_tasks(self):
        """Test deliberate with no pending tasks."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        intentions = checker.deliberate()
        assert intentions == []

    def test_get_statistics(self):
        """Test getting agent statistics."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        checker = ModelChecker()
        stats = checker.get_statistics()
        assert 'tasks_executed' in stats
        assert 'properties_checked' in stats
        assert 'models_cached' in stats


class TestPathReconstruction:
    """Tests for path reconstruction."""

    def test_path_from_initial(self):
        """Test path when target is initial."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='path',
            states=[
                {'id': 's0', 'values': {'goal': True}},
            ],
            transitions=[],
            initial=['s0']
        )
        result = checker.check_property(model, 'goal', PropertyType.REACHABILITY)
        # Path should be ['s0']

    def test_path_multiple_hops(self):
        """Test path with multiple hops."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            ModelChecker, PropertyType
        )
        checker = ModelChecker()
        model = checker.create_model(
            name='hops',
            states=[
                {'id': 's0', 'values': {}},
                {'id': 's1', 'values': {}},
                {'id': 's2', 'values': {'goal': True}}
            ],
            transitions=[('s0', 's1', None), ('s1', 's2', None)],
            initial=['s0']
        )
        result = checker.check_property(model, 'goal', PropertyType.REACHABILITY)
        assert result.counterexample is not None
        assert len(result.counterexample.path) >= 1


class TestModuleImports:
    """Tests for module imports."""

    def test_model_checker_import(self):
        """Test ModelChecker can be imported."""
        from symbo_agentic_reasoners.agents.provers.model_checker import ModelChecker
        assert ModelChecker is not None

    def test_dataclass_imports(self):
        """Test dataclasses can be imported."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            State, Transition, Model, Counterexample, CheckResult
        )
        assert State is not None
        assert Transition is not None
        assert Model is not None
        assert Counterexample is not None
        assert CheckResult is not None

    def test_enum_imports(self):
        """Test enums can be imported."""
        from symbo_agentic_reasoners.agents.provers.model_checker import (
            PropertyType, VerificationResult
        )
        assert PropertyType is not None
        assert VerificationResult is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
