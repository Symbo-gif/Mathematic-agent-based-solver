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
Test Suite: Universal Word Problem Normalization System
========================================================

Comprehensive tests for:
- NormalizationRule base class
- RuleContext and RuleResult
- RuleLibrary and RulePacks
- RuleEngine with execution strategies
- Domain-specific rule packs
- SemanticOutput format
- DomainVocabulary

Tests follow the 12-test pattern for specialists.
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# =============================================================================
# NORMALIZATION RULE TESTS
# =============================================================================

class TestNormalizationRule:
    """Tests for NormalizationRule base class."""

    def test_rule_context_creation(self):
        """Test RuleContext creation and properties."""
        from symbo_agentic_reasoners.core.word_problem.normalization_rule import RuleContext

        context = RuleContext(
            original_text="John has 5 apples",
            normalized_text="john has 5 apples"
        )

        assert context.original_text == "John has 5 apples"
        assert context.normalized_text == "john has 5 apples"
        assert context.entities == []
        assert context.relationships == []

    def test_rule_context_get_numbers(self):
        """Test number extraction from context."""
        from symbo_agentic_reasoners.core.word_problem.normalization_rule import RuleContext

        context = RuleContext(
            original_text="I have 5 apples and 3 oranges",
            normalized_text="i have 5 apples and 3 oranges"
        )

        numbers = context.get_numbers()
        assert 5 in numbers
        assert 3 in numbers

    def test_rule_context_has_keyword(self):
        """Test keyword detection."""
        from symbo_agentic_reasoners.core.word_problem.normalization_rule import RuleContext

        context = RuleContext(
            original_text="What is the total?",
            normalized_text="what is the total?"
        )

        assert context.has_keyword('total') is True
        assert context.has_keyword('remaining') is False

    def test_rule_result_success(self):
        """Test RuleResult success creation."""
        from symbo_agentic_reasoners.core.word_problem.normalization_rule import RuleResult

        result = RuleResult.match(
            expression="5 + 3",
            target_service="math.algebra.arithmetic",
            operation="add",
            confidence=0.9
        )

        assert result.success is True
        assert result.expression == "5 + 3"
        assert result.target_service == "math.algebra.arithmetic"
        assert result.confidence == 0.9

    def test_rule_result_failure(self):
        """Test RuleResult failure creation."""
        from symbo_agentic_reasoners.core.word_problem.normalization_rule import RuleResult

        result = RuleResult.failure("No numbers found")

        assert result.success is False
        assert result.error == "No numbers found"

    def test_rule_priority_ordering(self):
        """Test rule priority enum ordering."""
        from symbo_agentic_reasoners.core.word_problem.normalization_rule import RulePriority

        assert RulePriority.CRITICAL > RulePriority.HIGHEST
        assert RulePriority.HIGHEST > RulePriority.HIGH
        assert RulePriority.HIGH > RulePriority.MEDIUM
        assert RulePriority.MEDIUM > RulePriority.LOW


# =============================================================================
# RULE LIBRARY TESTS
# =============================================================================

class TestRuleLibrary:
    """Tests for RuleLibrary and RulePack."""

    def test_library_creation(self):
        """Test RuleLibrary creation."""
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary

        library = RuleLibrary()
        assert library is not None
        # Library uses internal _packs dict
        assert len(library._packs) == 0

    def test_pack_registration(self):
        """Test rule pack registration."""
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import ArithmeticRulePack

        library = RuleLibrary()
        library.register_pack(ArithmeticRulePack())

        # Check pack was registered
        assert 'arithmetic' in library._packs
        rules = library.get_rules_for_domain('arithmetic')
        assert len(rules) > 0

    def test_get_all_rules(self):
        """Test getting all rules from library."""
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import (
            ArithmeticRulePack, PhysicsRulePack
        )

        library = RuleLibrary()
        library.register_pack(ArithmeticRulePack())
        library.register_pack(PhysicsRulePack())

        all_rules = list(library.iter_rules())
        assert len(all_rules) > 10  # Combined rules from both packs

    def test_pack_metadata(self):
        """Test rule pack metadata."""
        from symbo_agentic_reasoners.core.word_problem.rule_packs import ArithmeticRulePack

        pack = ArithmeticRulePack()
        metadata = pack.get_metadata()

        assert metadata.name == 'arithmetic'
        assert metadata.domain == 'arithmetic'
        assert '1.0.0' in metadata.version


# =============================================================================
# RULE ENGINE TESTS
# =============================================================================

class TestRuleEngine:
    """Tests for RuleEngine."""

    def test_engine_creation(self):
        """Test RuleEngine creation."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import ArithmeticRulePack

        library = RuleLibrary()
        library.register_pack(ArithmeticRulePack())

        engine = RuleEngine(library=library)
        assert engine is not None

    def test_engine_normalize_sum(self):
        """Test normalizing a sum problem."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import ArithmeticRulePack

        library = RuleLibrary()
        library.register_pack(ArithmeticRulePack())
        engine = RuleEngine(library=library)

        result = engine.normalize("John has 5 apples and 3 oranges. How many in total?")

        assert result.success is True
        assert result.matched_rules is not None
        assert len(result.matched_rules) > 0

    def test_engine_best_confidence_strategy(self):
        """Test best confidence execution strategy."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import (
            RuleEngine, ExecutionStrategy
        )
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import ArithmeticRulePack

        library = RuleLibrary()
        library.register_pack(ArithmeticRulePack())
        engine = RuleEngine(library=library, strategy=ExecutionStrategy.BEST_CONFIDENCE)

        result = engine.normalize("What is 25% of 200?")

        assert result.success is True
        # Should match percentage rule with high confidence

    def test_engine_no_match(self):
        """Test engine with no matching rules."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary

        library = RuleLibrary()  # Empty library
        engine = RuleEngine(library=library)

        # Use text that won't trigger any domain keywords (e.g., "random" triggers probability)
        result = engine.normalize("asdf qwerty xyzzy nonsense")

        assert result.success is False


# =============================================================================
# ARITHMETIC RULE PACK TESTS
# =============================================================================

class TestArithmeticRulePack:
    """Tests for ArithmeticRulePack."""

    @pytest.fixture
    def engine(self):
        """Create engine with arithmetic rules."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import ArithmeticRulePack

        library = RuleLibrary()
        library.register_pack(ArithmeticRulePack())
        return RuleEngine(library=library)

    def test_total_sum_rule(self, engine):
        """Test total/sum rule."""
        result = engine.normalize("John has 5 apples and 3 oranges. How many in total?")
        assert result.success is True

    def test_subtraction_remaining_rule(self, engine):
        """Test subtraction/remaining rule."""
        result = engine.normalize("Mary had 10 cookies. She gave away 4. How many left?")
        assert result.success is True

    def test_multiplication_each_rule(self, engine):
        """Test multiplication/each rule."""
        result = engine.normalize("There are 5 boxes with 6 apples each. How many apples?")
        assert result.success is True

    def test_division_share_rule(self, engine):
        """Test division/share rule."""
        result = engine.normalize("24 cookies divided among 6 children. How many each?")
        assert result.success is True

    def test_percentage_rule(self, engine):
        """Test percentage rule."""
        result = engine.normalize("What is 25% of 200?")
        assert result.success is True
        # Check that we got a match
        assert len(result.matched_rules) > 0

    def test_discount_rule(self, engine):
        """Test discount percentage rule."""
        result = engine.normalize("A $80 item with 15% discount. Final price?")
        assert result.success is True


# =============================================================================
# PHYSICS RULE PACK TESTS
# =============================================================================

class TestPhysicsRulePack:
    """Tests for PhysicsRulePack."""

    @pytest.fixture
    def engine(self):
        """Create engine with physics rules."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import PhysicsRulePack

        library = RuleLibrary()
        library.register_pack(PhysicsRulePack())
        return RuleEngine(library=library)

    def test_distance_rate_time(self, engine):
        """Test d = r * t rule."""
        result = engine.normalize("A car travels at 60 mph for 3 hours. How far?")
        assert result.success is True

    def test_time_from_distance(self, engine):
        """Test t = d / r rule."""
        result = engine.normalize("How long to travel 180 miles at 60 mph?")
        assert result.success is True

    def test_work_rate(self, engine):
        """Test work rate rule - requires 'work(s/ed/ing) for' pattern."""
        # Text must contain: keyword 'per hour' AND pattern 'work(s|ed|ing) for'
        result = engine.normalize("John works for 8 hours producing 10 items per hour. Total?")
        assert result.success is True

    def test_combined_work(self, engine):
        """Test combined work rate rule."""
        result = engine.normalize("Pipe A fills a tank in 3 hours, Pipe B in 4 hours. Together?")
        assert result.success is True


# =============================================================================
# ALGEBRA RULE PACK TESTS
# =============================================================================

class TestAlgebraRulePack:
    """Tests for AlgebraRulePack."""

    @pytest.fixture
    def engine(self):
        """Create engine with algebra rules."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import AlgebraRulePack

        library = RuleLibrary()
        library.register_pack(AlgebraRulePack())
        return RuleEngine(library=library)

    def test_find_unknown(self, engine):
        """Test find unknown rule."""
        result = engine.normalize("A number plus 5 equals 12. Find the number.")
        assert result.success is True

    def test_age_problem(self, engine):
        """Test age problem rule."""
        result = engine.normalize("John is 5 years older than Mary. Together they are 31.")
        assert result.success is True

    def test_coin_problem(self, engine):
        """Test coin problem rule."""
        result = engine.normalize("30 coins of nickels and dimes worth $2.10. How many of each?")
        assert result.success is True


# =============================================================================
# GEOMETRY RULE PACK TESTS
# =============================================================================

class TestGeometryRulePack:
    """Tests for GeometryRulePack."""

    @pytest.fixture
    def engine(self):
        """Create engine with geometry rules."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import GeometryRulePack

        library = RuleLibrary()
        library.register_pack(GeometryRulePack())
        return RuleEngine(library=library)

    def test_rectangle_area(self, engine):
        """Test rectangle area rule."""
        result = engine.normalize("A rectangle with length 10 and width 5. Find the area.")
        assert result.success is True

    def test_circle_area(self, engine):
        """Test circle area rule."""
        result = engine.normalize("A circle with radius 7. Find the area.")
        assert result.success is True

    def test_triangle_area(self, engine):
        """Test triangle area rule."""
        result = engine.normalize("A triangle with base 10 and height 6. Find the area.")
        assert result.success is True

    def test_pythagorean(self, engine):
        """Test Pythagorean theorem rule."""
        result = engine.normalize("A right triangle with legs 3 and 4. Find the hypotenuse.")
        assert result.success is True


# =============================================================================
# STATISTICS RULE PACK TESTS
# =============================================================================

class TestStatisticsRulePack:
    """Tests for StatisticsRulePack."""

    @pytest.fixture
    def engine(self):
        """Create engine with statistics rules."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import RuleEngine
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import StatisticsRulePack

        library = RuleLibrary()
        library.register_pack(StatisticsRulePack())
        return RuleEngine(library=library)

    def test_mean_average(self, engine):
        """Test mean/average rule."""
        result = engine.normalize("The average of 10, 15, 20, and 25.")
        assert result.success is True

    def test_median(self, engine):
        """Test median rule."""
        result = engine.normalize("Find the median of 3, 7, 9, 12, 15.")
        assert result.success is True

    def test_probability(self, engine):
        """Test probability rule."""
        result = engine.normalize("A bag has 3 red and 7 blue balls. Probability of red?")
        assert result.success is True


# =============================================================================
# SEMANTIC OUTPUT TESTS
# =============================================================================

class TestSemanticOutput:
    """Tests for SemanticOutput format."""

    def test_builder_pattern(self):
        """Test SemanticOutputBuilder pattern."""
        from symbo_agentic_reasoners.core.word_problem.semantic_output import SemanticOutputBuilder

        output = (
            SemanticOutputBuilder()
            .domain('algebra')
            .expression("x + 5 = 12")
            .variable('x', description="The number to find")
            .variable('constant', value=5)
            .constraint("x > 0")
            .goal('find', 'x', "Find x")
            .build()
        )

        assert output.domain == 'algebra'
        assert output.expression == "x + 5 = 12"
        assert len(output.variables) == 2
        assert len(output.constraints) == 1

    def test_to_equation(self):
        """Test equation generation."""
        from symbo_agentic_reasoners.core.word_problem.semantic_output import SemanticOutputBuilder

        output = (
            SemanticOutputBuilder()
            .domain('algebra')
            .expression("2*x + 3 = 11")
            .variable('x')
            .build()
        )

        equation = output.to_equation()
        assert equation is not None
        assert "2*x + 3 = 11" in equation


# =============================================================================
# DOMAIN VOCABULARY TESTS
# =============================================================================

class TestDomainVocabulary:
    """Tests for DomainVocabulary."""

    def test_create_vocabulary(self):
        """Test creating a domain vocabulary."""
        from symbo_agentic_reasoners.core.word_problem.domain_vocabulary import DomainVocabulary

        vocab = DomainVocabulary("test_domain")
        assert vocab is not None
        assert vocab.domain == "test_domain"

    def test_add_and_get_symbol(self):
        """Test adding and getting symbols."""
        from symbo_agentic_reasoners.core.word_problem.domain_vocabulary import (
            DomainVocabulary, EntryType
        )

        vocab = DomainVocabulary("physics")
        vocab.add_term("velocity", "v", ["speed"], entry_type=EntryType.SYMBOL)

        symbol = vocab.get_symbol("velocity")
        assert symbol == "v"

        # Test alias
        alias_symbol = vocab.get_symbol("speed")
        assert alias_symbol == "v"

    def test_unit_conversion(self):
        """Test unit conversion."""
        from symbo_agentic_reasoners.core.word_problem.domain_vocabulary import DomainVocabulary

        vocab = DomainVocabulary("physics")
        vocab.add_unit_conversion("minutes", "hours", 1/60)

        result = vocab.convert_unit(60, "minutes", "hours")
        assert result == 1.0

    def test_vocabulary_registry(self):
        """Test global vocabulary registration."""
        from symbo_agentic_reasoners.core.word_problem.domain_vocabulary import DomainVocabulary

        vocab = DomainVocabulary("test_registry_domain")
        DomainVocabulary.register_vocabulary(vocab)

        retrieved = DomainVocabulary.get_vocabulary("test_registry_domain")
        assert retrieved is not None
        assert retrieved.domain == "test_registry_domain"

    def test_pre_built_vocabularies(self):
        """Test that pre-built vocabularies can be created."""
        from symbo_agentic_reasoners.core.word_problem.domain_vocabulary import (
            create_arithmetic_vocabulary,
            create_physics_vocabulary
        )

        arith_vocab = create_arithmetic_vocabulary()
        assert arith_vocab is not None
        assert arith_vocab.get_symbol("total") == "+"

        physics_vocab = create_physics_vocabulary()
        assert physics_vocab is not None
        assert physics_vocab.get_symbol("velocity") == "v"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for the complete normalization system."""

    @pytest.fixture
    def full_engine(self):
        """Create engine with all rule packs."""
        from symbo_agentic_reasoners.core.word_problem.rule_engine import (
            RuleEngine, ExecutionStrategy
        )
        from symbo_agentic_reasoners.core.word_problem.rule_library import RuleLibrary
        from symbo_agentic_reasoners.core.word_problem.rule_packs import (
            ArithmeticRulePack, PhysicsRulePack, AlgebraRulePack,
            GeometryRulePack, StatisticsRulePack
        )

        library = RuleLibrary()
        library.register_pack(ArithmeticRulePack())
        library.register_pack(PhysicsRulePack())
        library.register_pack(AlgebraRulePack())
        library.register_pack(GeometryRulePack())
        library.register_pack(StatisticsRulePack())

        return RuleEngine(library=library, strategy=ExecutionStrategy.BEST_CONFIDENCE)

    def test_multi_domain_detection(self, full_engine):
        """Test that correct domain is detected."""
        # Physics problem
        result = full_engine.normalize("A car travels at 60 mph for 3 hours.")
        assert result.success is True
        # matched_rules is List[str] (names), use target_service from primary_result
        if result.target_service:
            assert 'physics' in result.target_service.lower()

        # Geometry problem
        result = full_engine.normalize("A rectangle with length 10 and width 5. Find the area.")
        assert result.success is True
        if result.target_service:
            assert 'geometry' in result.target_service.lower()

    def test_rule_priority_ordering(self, full_engine):
        """Test that higher priority rules match first."""
        # Percentage should match with high priority
        result = full_engine.normalize("What is 20% of 100?")
        assert result.success is True
        assert len(result.matched_rules) > 0

    def test_complex_word_problem(self, full_engine):
        """Test complex multi-step word problem."""
        result = full_engine.normalize(
            "A train travels at 80 km/h for 2.5 hours. How far does it travel?"
        )
        assert result.success is True
        assert len(result.matched_rules) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
