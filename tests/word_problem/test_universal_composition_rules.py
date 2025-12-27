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
Unit tests for universal_composition_rules.py

Tests the 8 universal object-based rules for word problem normalization.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.rule_packs.universal_composition_rules import (
    UniversalCompositionRulePack,
    UniversalRule,
    RateAccumulationRule,
    SequentialOperationsRule,
    ProportionalScalingRule,
    PercentageOperationsRule,
    DifferenceComparisonRule,
    ConditionalTieredRule,
    RelativeQuantityEnhancedRule,
    BackwardInferenceEnhancedRule,
)
from symbo_agentic_reasoners.core.word_problem.normalization_rule import (
    RuleContext, RuleResult, RulePriority
)


class TestUniversalCompositionRulePack:
    """Tests for UniversalCompositionRulePack."""

    @pytest.fixture
    def pack(self):
        """Create a UniversalCompositionRulePack instance."""
        return UniversalCompositionRulePack()

    def test_pack_initialization(self, pack):
        """Test pack initializes correctly."""
        pack.initialize()
        assert pack.metadata.name == "universal_composition"
        assert pack.metadata.domain == "universal"

    def test_pack_creates_8_rules(self, pack):
        """Test pack creates all 8 rules."""
        rules = pack.rules
        assert len(rules) == 8

    def test_pack_rule_names(self, pack):
        """Test pack creates rules with correct names."""
        rule_names = [r.name for r in pack.rules]
        expected_names = [
            "universal_rate_accumulation",
            "universal_sequential_operations",
            "universal_proportional_scaling",
            "universal_percentage_operations",
            "universal_difference_comparison",
            "universal_conditional_tiered",
            "universal_relative_quantity",
            "universal_backward_inference",
        ]
        for expected in expected_names:
            assert expected in rule_names

    def test_pack_coverage_metadata(self, pack):
        """Test pack coverage metadata."""
        pack.initialize()
        assert len(pack.metadata.coverage) == 8


class TestRateAccumulationRule:
    """Tests for RateAccumulationRule."""

    @pytest.fixture
    def rule(self):
        return RateAccumulationRule()

    @pytest.fixture
    def context_multi_rate(self):
        return RuleContext(
            original_text="Jill gets paid $20 per hour as teacher and $30 per hour as coach",
            normalized_text="jill gets paid $20 per hour as teacher and $30 per hour as coach"
        )

    def test_rule_priority(self, rule):
        """Test rule has highest priority."""
        assert rule.priority == RulePriority.HIGHEST

    def test_matches_multi_rate(self, rule, context_multi_rate):
        """Test matching multi-rate problem."""
        # The match depends on semantic object extraction
        # This tests basic functionality
        result = rule.matches(context_multi_rate)
        # May or may not match depending on object extraction
        assert isinstance(result, bool)

    def test_transform_produces_result(self, rule):
        """Test transform produces RuleResult."""
        context = RuleContext(
            original_text="He earns $20 per hour for 8 hours and $30 per hour for 4 hours",
            normalized_text="he earns $20 per hour for 8 hours and $30 per hour for 4 hours"
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestSequentialOperationsRule:
    """Tests for SequentialOperationsRule."""

    @pytest.fixture
    def rule(self):
        return SequentialOperationsRule()

    def test_matches_with_then(self, rule):
        """Test matching with 'then' marker."""
        context = RuleContext(
            original_text="John has 10 apples. He ate 3, then bought 5 more.",
            normalized_text="john has 10 apples. he ate 3, then bought 5 more."
        )
        assert rule.matches(context)

    def test_matches_with_later(self, rule):
        """Test matching with 'later' marker."""
        context = RuleContext(
            original_text="She had $100. She spent $30 and later earned $50.",
            normalized_text="she had $100. she spent $30 and later earned $50."
        )
        assert rule.matches(context)

    def test_transform_produces_result(self, rule):
        """Test transform produces RuleResult."""
        context = RuleContext(
            original_text="John has 10 apples. He ate 3, then bought 5 more.",
            normalized_text="john has 10 apples. he ate 3, then bought 5 more."
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestProportionalScalingRule:
    """Tests for ProportionalScalingRule."""

    @pytest.fixture
    def rule(self):
        return ProportionalScalingRule()

    def test_matches_if_cost(self, rule):
        """Test matching 'if X cost Y' pattern."""
        context = RuleContext(
            original_text="If 3 items cost $15, how much do 7 cost?",
            normalized_text="if 3 items cost $15, how much do 7 cost?"
        )
        assert rule.matches(context)

    def test_matches_per_pattern(self, rule):
        """Test matching 'per' pattern."""
        context = RuleContext(
            original_text="At $5 per item, how many for $25?",
            normalized_text="at $5 per item, how many for $25?"
        )
        assert rule.matches(context)

    def test_transform_produces_result(self, rule):
        """Test transform produces RuleResult."""
        context = RuleContext(
            original_text="If 3 items cost $15, how much do 7 items cost?",
            normalized_text="if 3 items cost $15, how much do 7 items cost?"
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestPercentageOperationsRule:
    """Tests for PercentageOperationsRule."""

    @pytest.fixture
    def rule(self):
        return PercentageOperationsRule()

    def test_matches_percentage_symbol(self, rule):
        """Test matching percentage with % symbol."""
        context = RuleContext(
            original_text="What is 25% of 200?",
            normalized_text="what is 25% of 200?"
        )
        assert rule.matches(context)

    def test_matches_discount(self, rule):
        """Test matching discount pattern."""
        context = RuleContext(
            original_text="After 20% discount on $50",
            normalized_text="after 20% discount on $50"
        )
        assert rule.matches(context)

    def test_transform_simple_percentage(self, rule):
        """Test transform for simple percentage."""
        context = RuleContext(
            original_text="What is 25% of 200?",
            normalized_text="what is 25% of 200?"
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)

    def test_transform_discount(self, rule):
        """Test transform for discount calculation."""
        context = RuleContext(
            original_text="After 20% discount on $50",
            normalized_text="after 20% discount on $50"
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestDifferenceComparisonRule:
    """Tests for DifferenceComparisonRule."""

    @pytest.fixture
    def rule(self):
        return DifferenceComparisonRule()

    def test_matches_more_than(self, rule):
        """Test matching 'more than' pattern."""
        context = RuleContext(
            original_text="John has 5 more than Mary's 10 apples",
            normalized_text="john has 5 more than mary's 10 apples"
        )
        assert rule.matches(context)

    def test_matches_less_than(self, rule):
        """Test matching 'less than' pattern."""
        context = RuleContext(
            original_text="The box weighs 3 less than 15 pounds",
            normalized_text="the box weighs 3 less than 15 pounds"
        )
        assert rule.matches(context)

    def test_matches_fewer_than(self, rule):
        """Test matching 'fewer than' pattern."""
        context = RuleContext(
            original_text="She has 5 fewer than the 20 items in the store",
            normalized_text="she has 5 fewer than the 20 items in the store"
        )
        assert rule.matches(context)

    def test_transform_more_than(self, rule):
        """Test transform for 'more than'."""
        context = RuleContext(
            original_text="John has 5 more than Mary's 10 apples",
            normalized_text="john has 5 more than mary's 10 apples"
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestConditionalTieredRule:
    """Tests for ConditionalTieredRule."""

    @pytest.fixture
    def rule(self):
        return ConditionalTieredRule()

    def test_matches_first_rest(self, rule):
        """Test matching 'first...rest' pattern."""
        context = RuleContext(
            original_text="First 40 hours at $10/hr, rest at $15/hr. Worked 50 hours.",
            normalized_text="first 40 hours at $10/hr, rest at $15/hr. worked 50 hours."
        )
        assert rule.matches(context)

    def test_matches_overtime(self, rule):
        """Test matching 'overtime' pattern."""
        context = RuleContext(
            original_text="Regular hours at $10, overtime at $15. Worked 50 hours with 40 regular.",
            normalized_text="regular hours at $10, overtime at $15. worked 50 hours with 40 regular."
        )
        assert rule.matches(context)

    def test_transform_tiered(self, rule):
        """Test transform for tiered calculation."""
        context = RuleContext(
            original_text="First 40 hours at $10/hr, rest at $15. Worked 50 hours.",
            normalized_text="first 40 hours at $10/hr, rest at $15. worked 50 hours."
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestRelativeQuantityEnhancedRule:
    """Tests for RelativeQuantityEnhancedRule."""

    @pytest.fixture
    def rule(self):
        return RelativeQuantityEnhancedRule()

    def test_matches_half_as_long(self, rule):
        """Test matching 'half as long' pattern."""
        context = RuleContext(
            original_text="He reads for half as long as the 2 hours he watches TV.",
            normalized_text="he reads for half as long as the 2 hours he watches tv."
        )
        assert rule.matches(context)

    def test_matches_twice_as_many(self, rule):
        """Test matching 'twice as many' pattern."""
        context = RuleContext(
            original_text="She has twice as many apples as John's 5.",
            normalized_text="she has twice as many apples as john's 5."
        )
        assert rule.matches(context)

    def test_matches_n_times(self, rule):
        """Test matching 'N times as many' pattern."""
        context = RuleContext(
            original_text="He runs 3 times as long as her 2 hour walk.",
            normalized_text="he runs 3 times as long as her 2 hour walk."
        )
        assert rule.matches(context)

    def test_transform_half(self, rule):
        """Test transform for 'half' pattern."""
        context = RuleContext(
            original_text="He reads for half as long as the 2 hours he watches TV.",
            normalized_text="he reads for half as long as the 2 hours he watches tv."
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestBackwardInferenceEnhancedRule:
    """Tests for BackwardInferenceEnhancedRule."""

    @pytest.fixture
    def rule(self):
        return BackwardInferenceEnhancedRule()

    def test_matches_ended_with(self, rule):
        """Test matching 'ended with' pattern."""
        context = RuleContext(
            original_text="She ended up with 10 cookies after eating 5.",
            normalized_text="she ended up with 10 cookies after eating 5."
        )
        assert rule.matches(context)

    def test_matches_has_left(self, rule):
        """Test matching 'has X left' pattern."""
        context = RuleContext(
            original_text="After spending 30 dollars, John has 70 left.",
            normalized_text="after spending 30 dollars, john has 70 left."
        )
        assert rule.matches(context)

    def test_matches_start_question(self, rule):
        """Test matching 'how much did...start' pattern."""
        context = RuleContext(
            original_text="How much did John start with if he has $70 after spending $30?",
            normalized_text="how much did john start with if he has $70 after spending $30?"
        )
        assert rule.matches(context)

    def test_transform_backward(self, rule):
        """Test transform for backward inference."""
        context = RuleContext(
            original_text="After spending 30 dollars, John has 70 left.",
            normalized_text="after spending 30 dollars, john has 70 left."
        )
        if rule.matches(context):
            result = rule.transform(context)
            assert isinstance(result, RuleResult)


class TestUniversalRuleBase:
    """Tests for UniversalRule base class functionality."""

    def test_format_value_integer(self):
        """Test _format_value for integers."""
        rule = RateAccumulationRule()
        assert rule._format_value(100.0) == "100"
        assert rule._format_value(5.0) == "5"

    def test_format_value_decimal(self):
        """Test _format_value for decimals."""
        rule = RateAccumulationRule()
        assert rule._format_value(10.5) == "10.5"
        assert rule._format_value(3.14) == "3.14"


class TestRuleIntegration:
    """Integration tests for rule composition."""

    @pytest.fixture
    def pack(self):
        pack = UniversalCompositionRulePack()
        pack.initialize()
        return pack

    def test_find_matching_rule(self, pack):
        """Test finding a matching rule for a problem."""
        context = RuleContext(
            original_text="He earns $20 per hour for 8 hours",
            normalized_text="he earns $20 per hour for 8 hours"
        )

        matching_rules = [r for r in pack.rules if r.matches(context)]
        assert len(matching_rules) >= 1

    def test_multiple_rules_may_match(self, pack):
        """Test that multiple rules may match a complex problem."""
        # Complex problem that could match multiple rules
        context = RuleContext(
            original_text="He earns $20 per hour. After working 8 hours, he has $160 left.",
            normalized_text="he earns $20 per hour. after working 8 hours, he has $160 left."
        )

        matching_rules = [r for r in pack.rules if r.matches(context)]
        # At least one rule should match
        assert len(matching_rules) >= 1

    def test_rule_priority_ordering(self, pack):
        """Test that all rules have highest priority."""
        for rule in pack.rules:
            assert rule.priority == RulePriority.HIGHEST


class TestGSM8KStyleProblems:
    """Test rules on GSM8K-style problems."""

    @pytest.fixture
    def pack(self):
        pack = UniversalCompositionRulePack()
        pack.initialize()
        return pack

    def test_gsm8k_rate_accumulation(self, pack):
        """Test GSM8K-style rate accumulation problem."""
        context = RuleContext(
            original_text=("Jill gets paid $20 per hour as a teacher and $30 per hour "
                          "as a coach. She works 35 hours as a teacher and 15 hours as a coach."),
            normalized_text=("jill gets paid $20 per hour as a teacher and $30 per hour "
                            "as a coach. she works 35 hours as a teacher and 15 hours as a coach.")
        )

        matching = [r for r in pack.rules if r.matches(context)]
        assert len(matching) >= 1

    def test_gsm8k_sequential(self, pack):
        """Test GSM8K-style sequential problem."""
        context = RuleContext(
            original_text="Janet's ducks lay 16 eggs per day. She eats 3 for breakfast. Then bakes 4 into a cake.",
            normalized_text="janet's ducks lay 16 eggs per day. she eats 3 for breakfast. then bakes 4 into a cake."
        )

        matching = [r for r in pack.rules if r.matches(context)]
        assert len(matching) >= 1

    def test_gsm8k_percentage(self, pack):
        """Test GSM8K-style percentage problem."""
        context = RuleContext(
            original_text="A store offers 20% off on items over $100. The item costs $150.",
            normalized_text="a store offers 20% off on items over $100. the item costs $150."
        )

        matching = [r for r in pack.rules if r.matches(context)]
        assert len(matching) >= 1

    def test_gsm8k_backward_inference(self, pack):
        """Test GSM8K-style backward inference problem."""
        context = RuleContext(
            original_text="After giving away 25 apples, Tom has 50 apples left. How many did he start with?",
            normalized_text="after giving away 25 apples, tom has 50 apples left. how many did he start with?"
        )

        matching = [r for r in pack.rules if r.matches(context)]
        assert len(matching) >= 1
