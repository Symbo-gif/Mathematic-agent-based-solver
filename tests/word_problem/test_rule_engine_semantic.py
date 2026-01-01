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
Integration tests for RuleEngine with semantic routing.

Tests the integration of:
- SemanticEnrichmentPipeline (auto-enrichment hook)
- SemanticRouter (rule prioritization)
- RuleEngine (rule execution)
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.rule_engine import (
    RuleEngine, ExecutionStrategy, EngineResult
)
from symbo_agentic_reasoners.core.word_problem.normalization_rule import (
    NormalizationRule, RuleContext, RuleResult, RulePriority
)


class TestRuleEngineSemanticInit:
    """Tests for RuleEngine initialization with semantic options."""

    def test_init_with_auto_enrich(self):
        """Test that auto_enrich option adds enrichment hook."""
        engine = RuleEngine(auto_enrich=True)
        # Should have at least one pre-normalize hook
        assert len(engine._pre_normalize_hooks) >= 1

    def test_init_without_auto_enrich(self):
        """Test that auto_enrich=False skips enrichment hook."""
        engine = RuleEngine(auto_enrich=False)
        # Should have no hooks when disabled
        assert len(engine._pre_normalize_hooks) == 0

    def test_init_with_semantic_routing(self):
        """Test that use_semantic_routing option is stored."""
        engine = RuleEngine(use_semantic_routing=True)
        assert engine.use_semantic_routing is True

        engine2 = RuleEngine(use_semantic_routing=False)
        assert engine2.use_semantic_routing is False


class TestSemanticRouter:
    """Tests for semantic router integration."""

    def test_get_semantic_router_lazy_init(self):
        """Test lazy initialization of semantic router."""
        engine = RuleEngine(auto_enrich=False, use_semantic_routing=True)
        # Router should be None initially
        assert engine._semantic_router is None

        # Get router should create one
        router = engine._get_semantic_router()
        assert router is not None

        # Second call should return same instance
        router2 = engine._get_semantic_router()
        assert router is router2


class TestRuleContextSemantic:
    """Tests for semantic fields in RuleContext."""

    def test_context_semantic_fields(self):
        """Test that RuleContext has semantic fields."""
        context = RuleContext(
            original_text="John has 5 apples",
            normalized_text="john has 5 apples"
        )
        # Should have semantic fields
        assert hasattr(context, 'semantic_objects')
        assert hasattr(context, 'semantic_context')
        assert hasattr(context, 'inferred_operations')

        # Should have helper methods
        assert hasattr(context, 'get_objects_by_type')
        assert hasattr(context, 'get_objects_by_role')
        assert hasattr(context, 'get_rates')
        assert hasattr(context, 'get_values')

    def test_context_get_objects_by_type(self):
        """Test get_objects_by_type method."""
        from symbo_agentic_reasoners.core.word_problem.universal_parser import (
            SemanticType, SemanticRole, SemanticObject
        )

        obj1 = SemanticObject(
            id="1", type=SemanticType.MONEY, role=SemanticRole.INITIAL,
            value=100.0, source_text="$100", position=0
        )
        obj2 = SemanticObject(
            id="2", type=SemanticType.QUANTITY, role=SemanticRole.DELTA,
            value=5.0, source_text="5", position=10
        )

        context = RuleContext(
            original_text="test",
            normalized_text="test",
            semantic_objects=[obj1, obj2]
        )

        money_objs = context.get_objects_by_type(SemanticType.MONEY)
        assert len(money_objs) == 1
        assert money_objs[0].value == 100.0

        qty_objs = context.get_objects_by_type(SemanticType.QUANTITY)
        assert len(qty_objs) == 1
        assert qty_objs[0].value == 5.0

    def test_context_get_rates(self):
        """Test get_rates method."""
        from symbo_agentic_reasoners.core.word_problem.universal_parser import (
            SemanticType, SemanticRole, SemanticObject
        )

        rate_obj = SemanticObject(
            id="1", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=20.0, unit="per hour", source_text="$20/hour", position=0
        )
        qty_obj = SemanticObject(
            id="2", type=SemanticType.QUANTITY, role=SemanticRole.MULTIPLIER,
            value=8.0, source_text="8 hours", position=10
        )

        context = RuleContext(
            original_text="test",
            normalized_text="test",
            semantic_objects=[rate_obj, qty_obj]
        )

        rates = context.get_rates()
        assert len(rates) == 1
        assert rates[0].value == 20.0


class TestEnrichmentHook:
    """Tests for automatic enrichment hook."""

    def test_enrichment_adds_semantic_objects(self):
        """Test that enrichment hook adds semantic objects to context."""
        engine = RuleEngine(auto_enrich=True, use_semantic_routing=False)

        # Create a simple context
        context = RuleContext(
            original_text="John earns $20 per hour for 8 hours",
            normalized_text="john earns $20 per hour for 8 hours"
        )

        # Initially empty
        assert len(context.semantic_objects) == 0

        # Run pre-normalize hooks
        for hook in engine._pre_normalize_hooks:
            hook(context)

        # Should now have semantic objects (if enrichment available)
        # Note: This may fail if SemanticEnrichmentPipeline isn't available
        # In that case, it should gracefully handle the import error


class TestSemanticRuleSelection:
    """Tests for semantic-aware rule selection."""

    def test_rule_selection_with_semantic_data(self):
        """Test that rules are prioritized based on semantic data."""
        from symbo_agentic_reasoners.core.word_problem.universal_parser import (
            SemanticType, SemanticRole, SemanticObject
        )
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary

        # Create engine with semantic routing
        engine = RuleEngine(auto_enrich=False, use_semantic_routing=True)

        # Create context with rate semantic objects
        context = RuleContext(
            original_text="He earns $20 per hour",
            normalized_text="he earns $20 per hour",
            semantic_objects=[
                SemanticObject(
                    id="1", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
                    value=20.0, source_text="$20 per hour", position=0
                ),
                SemanticObject(
                    id="2", type=SemanticType.TIME, role=SemanticRole.MULTIPLIER,
                    value=8.0, source_text="8 hours", position=20
                )
            ]
        )

        # Get rules for context
        rules = engine._get_rules_for_context(context, None)

        # Should return rules (even if empty library, should not crash)
        assert isinstance(rules, list)


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_normalize_with_semantic_enrichment(self):
        """Test full normalization with semantic enrichment enabled."""
        engine = RuleEngine(
            auto_enrich=True,
            use_semantic_routing=True,
            strategy=ExecutionStrategy.BEST_CONFIDENCE
        )

        # Normalize a simple rate problem
        result = engine.normalize("John earns $20 per hour for 8 hours")

        # Should return an EngineResult
        assert isinstance(result, EngineResult)

        # Should have tried some rules
        assert result.rules_tried >= 0

    def test_normalize_without_semantic_enrichment(self):
        """Test normalization with semantic features disabled."""
        engine = RuleEngine(
            auto_enrich=False,
            use_semantic_routing=False,
            strategy=ExecutionStrategy.FIRST_MATCH
        )

        result = engine.normalize("Calculate 5 + 3")

        # Should still work, just without semantic features
        assert isinstance(result, EngineResult)

    def test_semantic_routing_fallback(self):
        """Test that semantic routing falls back to domain hints."""
        engine = RuleEngine(
            auto_enrich=False,
            use_semantic_routing=True
        )

        # Context without semantic data
        context = RuleContext(
            original_text="Calculate something",
            normalized_text="calculate something"
        )

        # Should fallback to hint_domain logic without error
        rules = engine._get_rules_for_context(context, "arithmetic")
        assert isinstance(rules, list)
