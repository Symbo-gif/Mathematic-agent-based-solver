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
Test Suite: GSM8K Reasoning Agents
==================================

Comprehensive tests for the word problem reasoning agents:
- ReasoningTensor
- SignReasoningSpecialist
- EntityStateTracker
- ComparativeResolver
- PercentageDirectionAgent
- MultiStepPlanner
- WordProblemReasoningSupervisor
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# =============================================================================
# ReasoningTensor Tests
# =============================================================================

class TestReasoningTensor:
    """Tests for ReasoningTensor class."""

    def test_tensor_creation(self):
        """Test basic tensor creation."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=['john', 'mary'])
        assert tensor is not None
        assert len(tensor.entities) == 2
        assert 'john' in tensor.entities

    def test_set_and_get_value(self):
        """Test setting and getting entity values."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=['eggs'])
        tensor.set_entity_value('eggs', 16)
        assert tensor.get_entity_value('eggs') == 16

    def test_add_operation(self):
        """Test addition operation."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=['apples'])
        tensor.set_entity_value('apples', 10)
        result = tensor.apply_operation('apples', 'add', 5)
        assert result == 15

    def test_subtract_operation(self):
        """Test subtraction operation."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=['eggs'])
        tensor.set_entity_value('eggs', 16)
        result = tensor.apply_operation('eggs', 'subtract', 3)
        assert result == 13

    def test_multiple_operations(self):
        """Test multiple sequential operations."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=['eggs'])
        tensor.set_entity_value('eggs', 16)
        tensor.apply_operation('eggs', 'subtract', 3)
        tensor.apply_operation('eggs', 'subtract', 4)
        tensor.apply_operation('eggs', 'add', 5)
        assert tensor.get_latest_value('eggs') == 14  # 16 - 3 - 4 + 5

    def test_dynamic_entity_addition(self):
        """Test adding entities dynamically."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=[])
        tensor.add_entity('new_entity')
        tensor.set_entity_value('new_entity', 100)
        assert tensor.get_entity_value('new_entity') == 100

    def test_state_history(self):
        """Test state history tracking."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=['x'])
        tensor.set_entity_value('x', 10)
        tensor.apply_operation('x', 'add', 5)

        history = tensor.get_state_history('x')
        assert len(history) == 2

    def test_constraints(self):
        """Test constraint addition."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import ReasoningTensor

        tensor = ReasoningTensor(entities=['a', 'b'])
        tensor.add_constraint('a', '2 * b', '==')
        assert len(tensor.constraints) == 1


# =============================================================================
# SignInferenceRules Tests
# =============================================================================

class TestSignInferenceRules:
    """Tests for SignInferenceRules class."""

    def test_gives_subject_subtract(self):
        """Test 'gives' from subject perspective is subtract."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import SignInferenceRules

        rules = SignInferenceRules()
        result = rules.infer('gives', {'perspective': 'subject'})
        assert result == 'subtract'

    def test_gives_object_add(self):
        """Test 'gives' from object perspective is add."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import SignInferenceRules

        rules = SignInferenceRules()
        result = rules.infer('gives', {'perspective': 'object'})
        assert result == 'add'

    def test_gives_more_flip(self):
        """Test 'gives more' flips the sign."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import SignInferenceRules

        rules = SignInferenceRules()
        result = rules.infer('gives', {'perspective': 'subject', 'modifier': 'more'})
        assert result == 'add'  # Flipped from subtract

    def test_gives_away_confirm(self):
        """Test 'gives away' confirms subtraction."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import SignInferenceRules

        rules = SignInferenceRules()
        result = rules.infer('gives', {'perspective': 'subject', 'modifier': 'away'})
        assert result == 'subtract'

    def test_earns_add(self):
        """Test 'earns' is add."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import SignInferenceRules

        rules = SignInferenceRules()
        result = rules.infer('earns', {'perspective': 'subject'})
        assert result == 'add'

    def test_loses_subtract(self):
        """Test 'loses' is subtract."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import SignInferenceRules

        rules = SignInferenceRules()
        result = rules.infer('loses', {'perspective': 'subject'})
        assert result == 'subtract'

    def test_unknown_verb(self):
        """Test unknown verb returns unknown."""
        from symbo_agentic_reasoners.optimization.symbo.reasoning_tensor import SignInferenceRules

        rules = SignInferenceRules()
        result = rules.infer('frobnicates', {'perspective': 'subject'})
        assert result == 'unknown'


# =============================================================================
# SignReasoningSpecialist Tests
# =============================================================================

class TestSignReasoningSpecialist:
    """Tests for SignReasoningSpecialist class."""

    @pytest.fixture
    def specialist(self):
        from symbo_agentic_reasoners.agents.specialists.word_problem.sign_reasoning_specialist import SignReasoningSpecialist
        return SignReasoningSpecialist()

    def test_specialist_creation(self, specialist):
        """Test specialist instantiation."""
        assert specialist is not None
        assert specialist.agent_id == 'sign_reasoning_specialist_001'

    def test_infer_sign_gives(self, specialist):
        """Test sign inference for 'gives'."""
        result = specialist.infer_sign('gives', {'perspective': 'subject'})
        assert result.operation == 'subtract'
        assert result.confidence > 0

    def test_infer_sign_with_modifier(self, specialist):
        """Test sign inference with modifier."""
        result = specialist.infer_sign('gives', {
            'perspective': 'subject',
            'modifier': 'more'
        })
        assert result.operation == 'add'
        assert 'sign_flip' in result.rules_applied[0] or len(result.rules_applied) > 1

    def test_analyze_text(self, specialist):
        """Test analyzing full text."""
        results = specialist.analyze_text("John gives Mary 5 apples")
        assert len(results) >= 1

    def test_statistics(self, specialist):
        """Test statistics tracking."""
        specialist.infer_sign('gives', {'perspective': 'subject'})
        specialist.infer_sign('receives', {'perspective': 'subject'})
        stats = specialist.get_statistics()
        assert stats['inferences_made'] == 2


# =============================================================================
# EntityStateTracker Tests
# =============================================================================

class TestEntityStateTracker:
    """Tests for EntityStateTracker class."""

    @pytest.fixture
    def tracker(self):
        from symbo_agentic_reasoners.agents.specialists.word_problem.entity_state_tracker import EntityStateTracker
        return EntityStateTracker()

    def test_tracker_creation(self, tracker):
        """Test tracker instantiation."""
        assert tracker is not None
        assert tracker.agent_id == 'entity_state_tracker_001'

    def test_track_simple_sequence(self, tracker):
        """Test tracking a simple operation sequence."""
        result = tracker.track_entities(
            entities=['eggs'],
            initial_values={'eggs': 16},
            operations=[
                {'entity': 'eggs', 'operation': 'subtract', 'operand': 3},
                {'entity': 'eggs', 'operation': 'subtract', 'operand': 4},
            ]
        )
        assert result.final_states['eggs'] == 9  # 16 - 3 - 4

    def test_track_multiple_entities(self, tracker):
        """Test tracking multiple entities."""
        result = tracker.track_entities(
            entities=['john', 'mary'],
            initial_values={'john': 10, 'mary': 5},
            operations=[
                {'entity': 'john', 'operation': 'subtract', 'operand': 3},
                {'entity': 'mary', 'operation': 'add', 'operand': 3},
            ]
        )
        assert result.final_states['john'] == 7
        assert result.final_states['mary'] == 8

    def test_state_history(self, tracker):
        """Test state history is recorded."""
        result = tracker.track_entities(
            entities=['x'],
            initial_values={'x': 100},
            operations=[
                {'entity': 'x', 'operation': 'subtract', 'operand': 10},
                {'entity': 'x', 'operation': 'add', 'operand': 5},
            ]
        )
        assert 'x' in result.state_history
        assert len(result.state_history['x']) >= 3  # Initial + 2 ops


# =============================================================================
# ComparativeResolver Tests
# =============================================================================

class TestComparativeResolver:
    """Tests for ComparativeResolver class."""

    @pytest.fixture
    def resolver(self):
        from symbo_agentic_reasoners.agents.specialists.word_problem.comparative_resolver import ComparativeResolver
        return ComparativeResolver()

    def test_resolver_creation(self, resolver):
        """Test resolver instantiation."""
        assert resolver is not None
        assert resolver.agent_id == 'comparative_resolver_001'

    def test_resolve_multiple(self, resolver):
        """Test resolving multiplicative comparative."""
        result = resolver.resolve(
            comparatives=[
                {'subject': 'alice', 'reference': 'bob', 'type': 'multiple', 'factor': 2}
            ],
            known_values={'bob': 10}
        )
        assert 'alice' in result.resolved_values
        assert result.resolved_values['alice'] == 20

    def test_resolve_difference(self, resolver):
        """Test resolving difference comparative."""
        result = resolver.resolve(
            comparatives=[
                {'subject': 'alice', 'reference': 'bob', 'type': 'difference', 'factor': 5}
            ],
            known_values={'bob': 10}
        )
        assert result.resolved_values['alice'] == 15  # 10 + 5

    def test_resolve_chain(self, resolver):
        """Test resolving chain of comparatives."""
        result = resolver.resolve(
            comparatives=[
                {'subject': 'alice', 'reference': 'bob', 'type': 'multiple', 'factor': 2},
                {'subject': 'bob', 'reference': 'carol', 'type': 'difference', 'factor': 3},
            ],
            known_values={'carol': 5}
        )
        # carol = 5, bob = 5 + 3 = 8, alice = 2 * 8 = 16
        assert result.resolved_values['carol'] == 5
        assert result.resolved_values['bob'] == 8
        assert result.resolved_values['alice'] == 16


# =============================================================================
# PercentageDirectionAgent Tests
# =============================================================================

class TestPercentageDirectionAgent:
    """Tests for PercentageDirectionAgent class."""

    @pytest.fixture
    def agent(self):
        from symbo_agentic_reasoners.agents.specialists.word_problem.percentage_direction_agent import PercentageDirectionAgent
        return PercentageDirectionAgent()

    def test_agent_creation(self, agent):
        """Test agent instantiation."""
        assert agent is not None
        assert agent.agent_id == 'percentage_direction_agent_001'

    def test_forward_percentage(self, agent):
        """Test forward percentage calculation."""
        result = agent.analyze("What is 25% of 100?")
        assert result.direction.value == 'forward'
        assert result.percentage == 25.0
        assert result.computed_answer == 25.0

    def test_discount_detection(self, agent):
        """Test discount pattern detection."""
        result = agent.analyze("25% off a $100 item")
        assert result.direction.value == 'discount'
        assert result.percentage == 25.0

    def test_markup_detection(self, agent):
        """Test markup pattern detection."""
        result = agent.analyze("Price increased by 20%")
        assert result.direction.value == 'markup'
        assert result.percentage == 20.0


# =============================================================================
# MultiStepPlanner Tests
# =============================================================================

class TestMultiStepPlanner:
    """Tests for MultiStepPlanner class."""

    @pytest.fixture
    def planner(self):
        from symbo_agentic_reasoners.agents.specialists.word_problem.multistep_planner import MultiStepPlanner
        return MultiStepPlanner()

    def test_planner_creation(self, planner):
        """Test planner instantiation."""
        assert planner is not None
        assert planner.agent_id == 'multistep_planner_001'

    def test_plan_simple_problem(self, planner):
        """Test planning for a simple problem."""
        result = planner.plan(
            problem_text="Janet has 16 eggs. She eats 3. How many left?",
            sentences=["Janet has 16 eggs.", "She eats 3.", "How many left?"],
            detected_operations=[]
        )
        assert len(result.steps) >= 1
        assert result.sentence_count == 3

    def test_plan_multi_step(self, planner):
        """Test planning for multi-step problem."""
        result = planner.plan(
            problem_text="John has 10 apples. He gives 3 away. He buys 5 more. How many does he have?",
            sentences=[
                "John has 10 apples.",
                "He gives 3 away.",
                "He buys 5 more.",
                "How many does he have?"
            ],
            detected_operations=[]
        )
        assert result.sentence_count == 4


# =============================================================================
# Integration Tests (using new WordProblemSupervisor)
# =============================================================================

class TestReasoningAgentsIntegration:
    """Integration tests for the reasoning agents working together."""

    def test_gsm8k_style_problem(self):
        """Test a GSM8K-style problem using new supervisor."""
        from symbo_agentic_reasoners.agents.supervisors.word_problem_supervisor import WordProblemSupervisor

        supervisor = WordProblemSupervisor()
        result = supervisor.solve_word_problem(
            "Janet's ducks lay 16 eggs per day. She eats 3 for breakfast and uses 4 for baking. How many eggs left?"
        )

        # New supervisor returns dict, not dataclass
        assert result.get('success') is True or result.get('answer') is not None

    def test_comparative_problem(self):
        """Test a comparative relationship problem."""
        from symbo_agentic_reasoners.agents.specialists.word_problem.comparative_resolver import ComparativeResolver

        resolver = ComparativeResolver()
        result = resolver.resolve(
            comparatives=[
                {'subject': 'alice', 'reference': 'bob', 'type': 'multiple', 'factor': 2},
                {'subject': 'bob', 'reference': 'carol', 'type': 'difference', 'factor': 3},
            ],
            known_values={'carol': 5}
        )

        # Verify the chain was resolved correctly
        assert result.resolved_values['carol'] == 5
        assert result.resolved_values['bob'] == 8  # 5 + 3
        assert result.resolved_values['alice'] == 16  # 2 * 8

    def test_percentage_problem(self):
        """Test a percentage problem."""
        from symbo_agentic_reasoners.agents.specialists.word_problem.percentage_direction_agent import PercentageDirectionAgent

        agent = PercentageDirectionAgent()
        result = agent.analyze("A shirt costs $80. There is a 25% off sale. What is the sale price?")

        assert result.direction.value == 'discount'
        assert result.percentage == 25.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
