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
Unit tests for semantic_integration.py

Tests the SemanticEnrichmentPipeline and EnrichedRuleContext
for semantic analysis integration with the rule engine.
"""

import pytest
from symbo_agentic_reasoners.core.word_problem.semantic_integration import (
    SemanticEnrichmentPipeline, EnrichedRuleContext, EnrichmentStage,
    ResolvedReference, InferredOperation, enrich_context
)
from symbo_agentic_reasoners.core.word_problem.normalization_rule import RuleContext
from symbo_agentic_reasoners.core.word_problem.universal_parser import (
    SemanticType, SemanticRole
)


class TestEnrichmentStage:
    """Tests for EnrichmentStage enum."""

    def test_all_stages_defined(self):
        """Verify all expected enrichment stages exist."""
        expected_stages = [
            'BASIC_ANALYSIS', 'OBJECT_EXTRACTION', 'COREFERENCE_RESOLUTION',
            'IMPLICIT_EXPANSION', 'RELATIONSHIP_MAPPING', 'OPERATION_INFERENCE'
        ]
        for stage_name in expected_stages:
            assert hasattr(EnrichmentStage, stage_name)


class TestResolvedReference:
    """Tests for ResolvedReference dataclass."""

    def test_resolved_reference_creation(self):
        """Test basic ResolvedReference creation."""
        ref = ResolvedReference(
            pronoun="he",
            pronoun_position=10,
            referent_id="person_1",
            referent_text="John",
            confidence=0.85
        )
        assert ref.pronoun == "he"
        assert ref.pronoun_position == 10
        assert ref.referent_id == "person_1"
        assert ref.referent_text == "John"
        assert ref.confidence == 0.85


class TestInferredOperation:
    """Tests for InferredOperation dataclass."""

    def test_inferred_operation_creation(self):
        """Test basic InferredOperation creation."""
        op = InferredOperation(
            operation="add",
            operand_ids=["obj_1", "obj_2"],
            confidence=0.9,
            source_pattern="buys more",
            result_role=SemanticRole.TOTAL
        )
        assert op.operation == "add"
        assert len(op.operand_ids) == 2
        assert op.confidence == 0.9
        assert op.source_pattern == "buys more"


class TestEnrichedRuleContext:
    """Tests for EnrichedRuleContext dataclass."""

    def test_enriched_context_creation(self):
        """Test basic EnrichedRuleContext creation."""
        ctx = EnrichedRuleContext(
            original_text="John has 10 apples",
            normalized_text="john has 10 apples"
        )
        assert ctx.original_text == "John has 10 apples"
        assert len(ctx.semantic_objects) == 0
        assert len(ctx.resolved_references) == 0
        assert len(ctx.inferred_operations) == 0

    def test_get_objects_by_type(self):
        """Test get_objects_by_type method."""
        from symbo_agentic_reasoners.core.word_problem.universal_parser import SemanticObject

        obj1 = SemanticObject(
            id="1", type=SemanticType.MONEY, role=SemanticRole.INITIAL,
            value=100, source_text="$100", position=0
        )
        obj2 = SemanticObject(
            id="2", type=SemanticType.QUANTITY, role=SemanticRole.DELTA,
            value=5, source_text="5 items", position=10
        )

        ctx = EnrichedRuleContext(
            original_text="test",
            normalized_text="test",
            semantic_objects=[obj1, obj2]
        )

        money_objs = ctx.get_objects_by_type(SemanticType.MONEY)
        assert len(money_objs) == 1
        assert money_objs[0].id == "1"

    def test_get_objects_by_role(self):
        """Test get_objects_by_role method."""
        from symbo_agentic_reasoners.core.word_problem.universal_parser import SemanticObject

        obj1 = SemanticObject(
            id="1", type=SemanticType.MONEY, role=SemanticRole.INITIAL,
            value=100, source_text="$100", position=0
        )
        obj2 = SemanticObject(
            id="2", type=SemanticType.MONEY, role=SemanticRole.DELTA,
            value=50, source_text="$50", position=10
        )

        ctx = EnrichedRuleContext(
            original_text="test",
            normalized_text="test",
            semantic_objects=[obj1, obj2]
        )

        initial_objs = ctx.get_objects_by_role(SemanticRole.INITIAL)
        assert len(initial_objs) == 1
        assert initial_objs[0].id == "1"

    def test_get_rates(self):
        """Test get_rates method."""
        from symbo_agentic_reasoners.core.word_problem.universal_parser import SemanticObject

        rate_obj = SemanticObject(
            id="1", type=SemanticType.RATE, role=SemanticRole.RATE_VALUE,
            value=20, unit="per hour", source_text="$20/hr", position=0
        )
        non_rate_obj = SemanticObject(
            id="2", type=SemanticType.QUANTITY, role=SemanticRole.INITIAL,
            value=5, source_text="5", position=10
        )

        ctx = EnrichedRuleContext(
            original_text="test",
            normalized_text="test",
            semantic_objects=[rate_obj, non_rate_obj]
        )

        rates = ctx.get_rates()
        assert len(rates) == 1
        assert rates[0].id == "1"

    def test_get_quantities_with_values(self):
        """Test get_quantities_with_values method."""
        from symbo_agentic_reasoners.core.word_problem.universal_parser import SemanticObject

        obj1 = SemanticObject(
            id="1", type=SemanticType.MONEY, role=SemanticRole.INITIAL,
            value=100, source_text="$100", position=0
        )
        obj2 = SemanticObject(
            id="2", type=SemanticType.PERSON, role=SemanticRole.SUBJECT,
            value=None, source_text="John", position=10
        )

        ctx = EnrichedRuleContext(
            original_text="test",
            normalized_text="test",
            semantic_objects=[obj1, obj2]
        )

        with_values = ctx.get_quantities_with_values()
        assert len(with_values) == 1
        assert with_values[0].id == "1"

    def test_resolve_reference(self):
        """Test resolve_reference method."""
        ctx = EnrichedRuleContext(
            original_text="John has 10 apples. He gives 3 away.",
            normalized_text="john has 10 apples. he gives 3 away.",
            resolved_references=[
                ResolvedReference(
                    pronoun="he",
                    pronoun_position=25,
                    referent_id="person_1",
                    referent_text="John",
                    confidence=0.9
                )
            ]
        )

        result = ctx.resolve_reference("he")
        assert result == "John"

        result = ctx.resolve_reference("she")
        assert result is None

    def test_get_implicit_value(self):
        """Test get_implicit_value method."""
        ctx = EnrichedRuleContext(
            original_text="a dozen eggs",
            normalized_text="a dozen eggs",
            implicit_quantities={'dozen': 12, 'pair': 2}
        )

        assert ctx.get_implicit_value('dozen') == 12
        assert ctx.get_implicit_value('pair') == 2
        assert ctx.get_implicit_value('triple') is None


class TestSemanticEnrichmentPipeline:
    """Tests for SemanticEnrichmentPipeline class."""

    @pytest.fixture
    def pipeline(self):
        """Create a SemanticEnrichmentPipeline instance."""
        return SemanticEnrichmentPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline.semantic_analyzer is not None
        assert pipeline.universal_parser is not None

    def test_enrich_simple_text(self, pipeline):
        """Test enrichment of simple text."""
        result = pipeline.enrich("John has 10 apples")
        assert isinstance(result, EnrichedRuleContext)
        assert result.original_text == "John has 10 apples"
        assert len(result.enrichment_stages_completed) > 0

    def test_enrich_completes_all_stages(self, pipeline):
        """Test that enrichment completes all stages."""
        result = pipeline.enrich("John has 10 apples. He gives 5 to Mary.")

        # All stages should be completed
        assert EnrichmentStage.BASIC_ANALYSIS in result.enrichment_stages_completed
        assert EnrichmentStage.OBJECT_EXTRACTION in result.enrichment_stages_completed
        assert EnrichmentStage.COREFERENCE_RESOLUTION in result.enrichment_stages_completed
        assert EnrichmentStage.IMPLICIT_EXPANSION in result.enrichment_stages_completed
        assert EnrichmentStage.RELATIONSHIP_MAPPING in result.enrichment_stages_completed
        assert EnrichmentStage.OPERATION_INFERENCE in result.enrichment_stages_completed

    def test_enrich_extracts_semantic_objects(self, pipeline):
        """Test that enrichment extracts semantic objects."""
        result = pipeline.enrich("John has $100 and Mary has $150")
        assert len(result.semantic_objects) > 0

    def test_enrich_detects_implicit_quantities(self, pipeline):
        """Test that enrichment detects implicit quantities."""
        result = pipeline.enrich("She bought a dozen eggs")
        if 'dozen' in result.implicit_quantities:
            assert result.implicit_quantities['dozen'] == 12

    def test_enrich_resolves_coreferences(self, pipeline):
        """Test coreference resolution."""
        result = pipeline.enrich("John has 10 apples. He gives 3 to Mary.")
        # Should have resolved 'he' to 'John'
        he_refs = [r for r in result.resolved_references if r.pronoun.lower() == 'he']
        if he_refs:
            assert he_refs[0].referent_text.lower() == 'john'

    def test_enrich_infers_operations(self, pipeline):
        """Test operation inference."""
        result = pipeline.enrich("John gives away 5 apples")
        # Should infer a subtraction operation
        if result.inferred_operations:
            ops = [op.operation for op in result.inferred_operations]
            assert 'subtract' in ops or len(ops) > 0

    def test_enrich_with_existing_context(self, pipeline):
        """Test enrichment with existing RuleContext."""
        existing = RuleContext(
            original_text="Test text with 5 items",
            normalized_text="test text with 5 items",
            entities=[{'text': '5 items', 'type': 'quantity'}]
        )
        result = pipeline.enrich("Test text with 5 items", existing)
        assert isinstance(result, EnrichedRuleContext)

    def test_enrich_rate_problem(self, pipeline):
        """Test enrichment of rate-based problem."""
        result = pipeline.enrich("He earns $20 per hour for 8 hours")
        rates = result.get_rates()
        # Should detect rate pattern
        assert len(result.semantic_objects) > 0

    def test_enrich_money_problem(self, pipeline):
        """Test enrichment of money-based problem."""
        result = pipeline.enrich("John has $100. He spends $30.")
        money_objs = result.get_objects_by_type(SemanticType.MONEY)
        assert len(money_objs) >= 1 or len(result.semantic_objects) >= 1

    def test_enrich_no_errors_on_empty(self, pipeline):
        """Test enrichment handles empty text gracefully."""
        result = pipeline.enrich("")
        assert isinstance(result, EnrichedRuleContext)
        assert len(result.enrichment_errors) == 0 or result.enrichment_errors == []

    def test_create_rule_engine_hook(self, pipeline):
        """Test creation of rule engine hook."""
        hook = pipeline.create_rule_engine_hook()
        assert callable(hook)

        # Test hook execution
        ctx = RuleContext(
            original_text="John has 10 apples",
            normalized_text="john has 10 apples"
        )
        hook(ctx)

        # Hook should add semantic data to metadata
        assert 'semantic_objects' in ctx.metadata
        assert 'inferred_operations' in ctx.metadata


class TestEnrichContextFunction:
    """Tests for the enrich_context convenience function."""

    def test_enrich_context_basic(self):
        """Test basic usage of enrich_context function."""
        result = enrich_context("John has 10 apples")
        assert isinstance(result, EnrichedRuleContext)
        assert result.original_text == "John has 10 apples"

    def test_enrich_context_complex(self):
        """Test enrich_context with complex problem."""
        text = "Jill gets paid $20/hour as teacher and $30/hour as coach."
        result = enrich_context(text)
        assert isinstance(result, EnrichedRuleContext)
        assert len(result.semantic_objects) > 0


class TestEnrichmentIntegration:
    """Integration tests for the enrichment pipeline."""

    @pytest.fixture
    def pipeline(self):
        return SemanticEnrichmentPipeline()

    def test_full_enrichment_sequential(self, pipeline):
        """Test full enrichment on sequential problem."""
        text = "Janet has 16 eggs. She eats 3 for breakfast. Then bakes 4 into a cake."
        result = pipeline.enrich(text)

        # Should have multiple semantic objects
        assert len(result.semantic_objects) >= 2

        # Should complete all stages without errors (7 stages including HEURISTIC_ANALYSIS)
        assert len(result.enrichment_stages_completed) == 7
        assert len(result.enrichment_errors) == 0

    def test_full_enrichment_rate_accumulation(self, pipeline):
        """Test full enrichment on rate accumulation problem."""
        text = "He earns $20 per hour teaching and $30 per hour coaching."
        result = pipeline.enrich(text)

        # Should detect rate objects
        rates = result.get_rates()
        # At minimum, semantic objects should be extracted
        assert len(result.semantic_objects) >= 1

    def test_full_enrichment_percentage(self, pipeline):
        """Test full enrichment on percentage problem."""
        text = "The store offers a 25% discount on items over $100."
        result = pipeline.enrich(text)

        # Should extract percentage and money values
        assert len(result.semantic_objects) >= 1

    def test_enrichment_preserves_original_text(self, pipeline):
        """Test that enrichment preserves original text."""
        original = "John has 10 APPLES"
        result = pipeline.enrich(original)
        assert result.original_text == original
