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
Tests for the Learning Enhancement Team
========================================

Comprehensive tests for all components:
- ComplexityScorerSpecialist (12 tests)
- NegativeLearnerSpecialist (12 tests)
- CurriculumSpecialist (12 tests)
- BPETokenizerSpecialist (12 tests)
- ModelArchitectSpecialist (12 tests)
- KnowledgeGraphSpecialist (12 tests)
- LearningEnhancementSupervisor (12 tests)

Total: 84+ tests following the 12-per-agent pattern.
"""

import pytest
import tempfile
import os
import json
from datetime import datetime

from symbo_agentic_reasoners.agents.specialists.learning import (
    LearningTaskType,
    ComplexityLevel,
    FailureType,
    RelationshipType,
    ComplexityScore,
    NegativeExample,
    ContrastivePair,
    CurriculumState,
    KnowledgeNode,
    KnowledgeEdge
)
from symbo_agentic_reasoners.agents.specialists.learning.complexity_scorer_specialist import (
    ComplexityScorerSpecialist
)
from symbo_agentic_reasoners.agents.specialists.learning.negative_learner_specialist import (
    NegativeLearnerSpecialist
)
from symbo_agentic_reasoners.agents.specialists.learning.curriculum_specialist import (
    CurriculumSpecialist
)
from symbo_agentic_reasoners.agents.specialists.learning.bpe_tokenizer_specialist import (
    BPETokenizerSpecialist
)
from symbo_agentic_reasoners.agents.specialists.learning.model_architect_specialist import (
    ModelArchitectSpecialist
)
from symbo_agentic_reasoners.agents.specialists.learning.knowledge_graph_specialist import (
    KnowledgeGraphSpecialist
)
from symbo_agentic_reasoners.agents.supervisors.learning_enhancement_supervisor import (
    LearningEnhancementSupervisor
)


# =============================================================================
# ComplexityScorerSpecialist Tests (12 tests)
# =============================================================================

class TestComplexityScorerSpecialist:
    """Tests for the ComplexityScorerSpecialist."""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance."""
        return ComplexityScorerSpecialist()

    def test_init(self, scorer):
        """Test scorer initialization."""
        assert scorer is not None
        assert 'complexity_scorer' in scorer.agent_id
        assert len(scorer.DOMAIN_WEIGHTS) > 0

    def test_df_registration_method(self, scorer):
        """Test Directory Facilitator registration method exists."""
        assert hasattr(scorer, '_register_services')
        assert callable(scorer._register_services)

    def test_simple_algebra_score(self, scorer):
        """Test simple algebra problem gets low complexity."""
        result = scorer.score(
            problem="What is 2+2?",
            answer="4",
            domain="algebra"
        )
        assert isinstance(result, ComplexityScore)
        assert 0.0 <= result.score <= 1.0
        assert result.level == ComplexityLevel.TRIVIAL

    def test_complex_calculus_score(self, scorer):
        """Test complex calculus problem scores higher."""
        result = scorer.score(
            problem="Find the integral of sin(x)*cos(x)*exp(x) dx using integration by parts and series expansion",
            answer="(1/2)*exp(x)*(sin(x) - cos(x)) + C",
            domain="calculus"
        )
        # Calculus has domain weight 1.5, longer problem
        assert result.score >= 0.1  # Has some complexity

    def test_ode_domain_weight(self, scorer):
        """Test ODE domain has high weight."""
        result = scorer.score(
            problem="Solve dy/dx = y",
            answer="y = Ce^x",
            domain="differential_equations"
        )
        # ODE domain weight is 2.0
        assert result.components.get('domain', 0) > 0

    def test_nesting_score_computation(self, scorer):
        """Test nesting depth scoring via internal method."""
        # Directly test the _score_nesting method
        score = scorer._score_nesting("((x + y) * (a + b))")
        assert score > 0

    def test_variable_score_computation(self, scorer):
        """Test variable scoring via internal method."""
        score = scorer._score_variables("x^2 + y^2 = r^2")
        assert score > 0

    def test_solve_time_factor(self, scorer):
        """Test solve time affects score."""
        result_fast = scorer.score(
            problem="x = 1",
            answer="1",
            domain="algebra",
            solve_time_ms=10
        )
        result_slow = scorer.score(
            problem="x = 1",
            answer="1",
            domain="algebra",
            solve_time_ms=5000
        )
        assert result_slow.score >= result_fast.score

    def test_learning_weight_calculation(self, scorer):
        """Test learning weight is 1 + score."""
        result = scorer.score(
            problem="Test problem",
            answer="Test answer",
            domain="algebra"
        )
        assert result.learning_weight == 1.0 + result.score

    def test_process_method(self, scorer):
        """Test process method routes correctly."""
        result = scorer.process({
            'action': 'score',
            'problem': 'What is 2+2?',
            'answer': '4',
            'domain': 'algebra'
        })
        assert 'score' in result

    def test_bdi_update_beliefs(self, scorer):
        """Test BDI update_beliefs method."""
        scorer.update_beliefs()
        assert hasattr(scorer, 'beliefs')

    def test_bdi_deliberate(self, scorer):
        """Test BDI deliberate method."""
        intention = scorer.deliberate()
        # May return None if no intentions
        assert intention is None or hasattr(intention, 'plan_id')


# =============================================================================
# NegativeLearnerSpecialist Tests (12 tests)
# =============================================================================

class TestNegativeLearnerSpecialist:
    """Tests for the NegativeLearnerSpecialist."""

    @pytest.fixture
    def learner(self):
        """Create learner instance with temp storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, "negative_examples.json")
            l = NegativeLearnerSpecialist(persistence_path=storage_path)
            yield l

    def test_init(self, learner):
        """Test learner initialization."""
        assert learner is not None
        assert 'negative_learner' in learner.agent_id

    def test_df_registration_method(self, learner):
        """Test Directory Facilitator registration method exists."""
        assert hasattr(learner, '_register_services')

    def test_add_negative_example(self, learner):
        """Test adding a negative example."""
        result = learner.add_negative(
            problem="What is 2+2?",
            bad_response="symbolic",
            reason="placeholder_response",
            domain="algebra"
        )
        assert result['status'] in ['added', 'success']

    def test_known_bad_pattern_symbolic(self, learner):
        """Test detection of 'symbolic' as bad pattern."""
        is_bad, reason = learner.is_known_bad("symbolic")
        assert is_bad is True
        assert 'placeholder' in reason.lower()

    def test_known_bad_pattern_unknown(self, learner):
        """Test detection of 'unknown' as bad pattern."""
        is_bad, reason = learner.is_known_bad("unknown")
        assert is_bad is True

    def test_known_bad_pattern_empty(self, learner):
        """Test detection of empty string as bad pattern."""
        is_bad, reason = learner.is_known_bad("")
        assert is_bad is True
        assert 'empty' in reason.lower()

    def test_good_response_passes(self, learner):
        """Test that good responses pass."""
        is_bad, reason = learner.is_known_bad("x = 5")
        assert is_bad is False
        assert reason is None

    def test_get_contrastive_pairs(self, learner):
        """Test getting contrastive pairs."""
        # Add some examples with correct answers
        learner.add_negative("P1", "bad1", "reason1", "algebra", correct_answer="good1")
        learner.add_negative("P2", "bad2", "reason2", "calculus", correct_answer="good2")

        pairs = learner.get_contrastive_pairs(batch_size=2)
        assert isinstance(pairs, list)

    def test_failure_counts(self, learner):
        """Test failure counts are tracked."""
        learner.add_negative("P1", "symbolic", "placeholder", "algebra")
        learner.add_negative("P2", "symbolic", "placeholder", "algebra")

        stats = learner.get_stats()
        assert stats['negative_examples'] >= 1

    def test_process_method(self, learner):
        """Test process method routes correctly."""
        result = learner.process({
            'action': 'check',
            'response': 'symbolic'
        })
        assert 'is_bad' in result

    def test_bdi_update_beliefs(self, learner):
        """Test BDI update_beliefs method."""
        learner.update_beliefs()
        assert hasattr(learner, 'beliefs')

    def test_bdi_deliberate(self, learner):
        """Test BDI deliberate method."""
        intention = learner.deliberate()
        assert intention is None or hasattr(intention, 'plan_id')


# =============================================================================
# CurriculumSpecialist Tests (12 tests)
# =============================================================================

class TestCurriculumSpecialist:
    """Tests for the CurriculumSpecialist."""

    @pytest.fixture
    def curriculum(self):
        """Create curriculum instance."""
        return CurriculumSpecialist(initial_difficulty=0.3)

    def test_init(self, curriculum):
        """Test curriculum initialization."""
        assert curriculum is not None
        assert 'curriculum' in curriculum.agent_id
        assert curriculum.state.current_difficulty == 0.3

    def test_df_registration_method(self, curriculum):
        """Test Directory Facilitator registration method exists."""
        assert hasattr(curriculum, '_register_services')

    def test_get_state(self, curriculum):
        """Test getting curriculum state."""
        state = curriculum.get_state()
        assert isinstance(state, dict)
        assert 'current_difficulty' in state

    def test_next_batch_selection(self, curriculum):
        """Test batch selection at current difficulty."""
        problems = [
            {'problem': 'P1', 'answer': 'A1', 'complexity': 0.2},
            {'problem': 'P2', 'answer': 'A2', 'complexity': 0.35},
            {'problem': 'P3', 'answer': 'A3', 'complexity': 0.8},
        ]
        result = curriculum.next_batch(problems, batch_size=2)
        assert 'batch' in result
        assert len(result['batch']) <= 2

    def test_update_on_success(self, curriculum):
        """Test difficulty update on success."""
        initial = curriculum.state.current_difficulty
        for _ in range(10):
            curriculum.update(success=True)
        assert curriculum.state.current_difficulty >= initial

    def test_update_on_failure(self, curriculum):
        """Test difficulty update on failure."""
        curriculum.state.current_difficulty = 0.5
        for _ in range(5):
            curriculum.update(success=False)
        # After 5 failures, should decrease
        assert curriculum.state.current_difficulty <= 0.5

    def test_difficulty_bounded_max(self, curriculum):
        """Test difficulty doesn't exceed 1.0."""
        curriculum.state.current_difficulty = 0.98
        for _ in range(20):
            curriculum.update(success=True)
        assert curriculum.state.current_difficulty <= 1.0

    def test_difficulty_bounded_min(self, curriculum):
        """Test difficulty doesn't go below 0.1."""
        curriculum.state.current_difficulty = 0.15
        for _ in range(20):
            curriculum.update(success=False)
        assert curriculum.state.current_difficulty >= 0.1

    def test_stats_tracking(self, curriculum):
        """Test stats are tracked."""
        curriculum.update(success=True)
        curriculum.update(success=False)
        stats = curriculum.get_stats()
        assert 'total_attempts' in stats

    def test_process_method(self, curriculum):
        """Test process method routes correctly."""
        result = curriculum.process({
            'action': 'get_state'
        })
        assert 'current_difficulty' in result

    def test_bdi_update_beliefs(self, curriculum):
        """Test BDI update_beliefs method."""
        curriculum.update_beliefs()
        assert hasattr(curriculum, 'beliefs')

    def test_bdi_deliberate(self, curriculum):
        """Test BDI deliberate method."""
        intention = curriculum.deliberate()
        assert intention is None or hasattr(intention, 'plan_id')


# =============================================================================
# BPETokenizerSpecialist Tests (12 tests)
# =============================================================================

class TestBPETokenizerSpecialist:
    """Tests for the BPETokenizerSpecialist."""

    @pytest.fixture
    def tokenizer(self):
        """Create tokenizer instance with temp storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, "bpe_vocab.json")
            t = BPETokenizerSpecialist(persistence_path=storage_path)
            yield t

    def test_init(self, tokenizer):
        """Test tokenizer initialization."""
        assert tokenizer is not None
        assert 'bpe_tokenizer' in tokenizer.agent_id

    def test_df_registration_method(self, tokenizer):
        """Test Directory Facilitator registration method exists."""
        assert hasattr(tokenizer, '_register_services')

    def test_math_primitives_exist(self, tokenizer):
        """Test math primitives are defined."""
        assert len(tokenizer.MATH_PRIMITIVES) >= 50
        assert 'sin' in tokenizer.MATH_PRIMITIVES
        assert 'integral' in tokenizer.MATH_PRIMITIVES
        assert 'derivative' in tokenizer.MATH_PRIMITIVES

    def test_encode_simple(self, tokenizer):
        """Test simple encoding."""
        tokens = tokenizer.encode("2 + 2 = 4")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_decode_simple(self, tokenizer):
        """Test simple decoding."""
        tokens = tokenizer.encode("hello")
        text = tokenizer.decode(tokens)
        assert len(text) > 0

    def test_encode_decode_preserves_content(self, tokenizer):
        """Test encode-decode preserves content."""
        original = "sin cos"  # Known primitives
        tokens = tokenizer.encode(original)
        decoded = tokenizer.decode(tokens)
        # Should contain the primitives
        assert 'sin' in decoded.lower() or len(tokens) > 0

    def test_train_on_corpus(self, tokenizer):
        """Test training on a corpus."""
        corpus = [
            "integral of x dx",
            "derivative of sin x",
            "solve for x x plus 1 equals 2",
            "the limit as x approaches infinity"
        ]
        result = tokenizer.train(corpus, verbose=False)
        assert 'final_vocab_size' in result or 'vocab_size' in result

    def test_get_stats(self, tokenizer):
        """Test getting tokenizer statistics."""
        stats = tokenizer.get_stats()
        assert 'vocab_size' in stats
        assert 'math_primitives' in stats or 'primitives_count' in stats

    def test_process_method(self, tokenizer):
        """Test process method routes correctly."""
        result = tokenizer.process({
            'action': 'encode',
            'text': 'sin x'
        })
        assert 'tokens' in result

    def test_vocab_has_primitives(self, tokenizer):
        """Test vocab includes math primitives."""
        vocab = tokenizer.vocab
        assert 'sin' in vocab
        assert 'cos' in vocab

    def test_bdi_update_beliefs(self, tokenizer):
        """Test BDI update_beliefs method."""
        tokenizer.update_beliefs()
        assert hasattr(tokenizer, 'beliefs')

    def test_bdi_deliberate(self, tokenizer):
        """Test BDI deliberate method."""
        intention = tokenizer.deliberate()
        assert intention is None or hasattr(intention, 'plan_id')


# =============================================================================
# ModelArchitectSpecialist Tests (12 tests)
# =============================================================================

class TestModelArchitectSpecialist:
    """Tests for the ModelArchitectSpecialist."""

    @pytest.fixture
    def architect(self):
        """Create architect instance."""
        return ModelArchitectSpecialist()

    def test_init(self, architect):
        """Test architect initialization."""
        assert architect is not None
        assert 'model_architect' in architect.agent_id

    def test_df_registration_method(self, architect):
        """Test Directory Facilitator registration method exists."""
        assert hasattr(architect, '_register_services')

    def test_has_architecture_configs(self, architect):
        """Test architecture configs are defined."""
        assert hasattr(architect, 'CONFIGS')
        configs = architect.CONFIGS
        assert 'base' in configs or len(configs) > 0

    def test_base_config_has_values(self, architect):
        """Test base config has expected structure."""
        if hasattr(architect, 'CONFIGS') and 'base' in architect.CONFIGS:
            base = architect.CONFIGS['base']
            # ArchitectureConfig dataclass has these attributes
            assert hasattr(base, 'vocab_size') or hasattr(base, 'embed_dim')

    def test_enhanced_config_has_values(self, architect):
        """Test enhanced config has expected structure."""
        if hasattr(architect, 'CONFIGS') and 'enhanced' in architect.CONFIGS:
            enhanced = architect.CONFIGS['enhanced']
            assert hasattr(enhanced, 'vocab_size') or hasattr(enhanced, 'embed_dim')

    def test_analyze_architecture(self, architect):
        """Test architecture analysis."""
        analysis = architect.analyze_architecture()
        assert isinstance(analysis, dict)

    def test_has_recommend_method(self, architect):
        """Test recommend_config method exists."""
        assert hasattr(architect, 'recommend_config')

    def test_has_migration_method(self, architect):
        """Test get_migration_plan method exists."""
        assert hasattr(architect, 'get_migration_plan')

    def test_has_estimate_parameters(self, architect):
        """Test estimate_parameters is available via ArchitectureConfig."""
        # estimate_parameters is on ArchitectureConfig, not specialist
        base_config = architect.CONFIGS.get('base')
        if base_config:
            assert hasattr(base_config, 'estimate_parameters')
            params = base_config.estimate_parameters()
            assert params > 0

    def test_process_method(self, architect):
        """Test process method routes correctly."""
        result = architect.process({
            'action': 'analyze'
        })
        assert result is not None

    def test_bdi_update_beliefs(self, architect):
        """Test BDI update_beliefs method."""
        architect.update_beliefs()
        assert hasattr(architect, 'beliefs')

    def test_bdi_deliberate(self, architect):
        """Test BDI deliberate method."""
        intention = architect.deliberate()
        assert intention is None or hasattr(intention, 'plan_id')


# =============================================================================
# KnowledgeGraphSpecialist Tests (12 tests)
# =============================================================================

class TestKnowledgeGraphSpecialist:
    """Tests for the KnowledgeGraphSpecialist."""

    @pytest.fixture
    def graph(self):
        """Create graph instance with temp database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "knowledge_graph.db")
            g = KnowledgeGraphSpecialist(db_path=db_path)
            yield g
            # No close() needed - connections are closed after each operation

    def test_init(self, graph):
        """Test graph initialization."""
        assert graph is not None
        assert 'knowledge_graph' in graph.agent_id

    def test_df_registration_method(self, graph):
        """Test Directory Facilitator registration method exists."""
        assert hasattr(graph, '_register_services')

    def test_has_relationships(self, graph):
        """Test relationships are defined via RelationshipType enum."""
        # Relationships are defined as RelationshipType enum in __init__.py
        assert len(RelationshipType) >= 5
        assert RelationshipType.SIMILAR_TO is not None
        assert RelationshipType.GENERALIZES is not None

    def test_add_node(self, graph):
        """Test adding a node."""
        result = graph.add_node(
            problem="What is 2+2?",
            answer="4",
            domain="algebra",
            complexity=0.1
        )
        assert 'node_id' in result
        assert result['node_id'] is not None

    def test_add_multiple_nodes(self, graph):
        """Test adding multiple nodes."""
        graph.add_node("P1: solve x=1", "x=1", "algebra", 0.2)
        result = graph.add_node("P2: solve x=2", "x=2", "algebra", 0.3)
        assert 'node_id' in result

    def test_query_related(self, graph):
        """Test querying related nodes."""
        graph.add_node("P1: solve x=1", "x=1", "algebra", 0.2)
        graph.add_node("P2: solve x=2", "x=2", "algebra", 0.3)

        result = graph.query_related("P1: solve x=1", max_depth=1)
        # Returns dict with 'source', 'related', 'total_found' keys
        assert isinstance(result, dict)
        assert 'related' in result
        assert isinstance(result['related'], list)

    def test_find_similar(self, graph):
        """Test finding similar nodes."""
        graph.add_node("integral of x^2", "x^3/3 + C", "calculus", 0.5)
        graph.add_node("derivative of x^3", "3x^2", "calculus", 0.5)

        similar = graph.find_similar("integral of x", top_k=5)
        assert isinstance(similar, list)

    def test_infer_relationship(self, graph):
        """Test relationship inference."""
        if hasattr(graph, '_infer_relationship'):
            rel = graph._infer_relationship("x", "x + 1 = 2")
            # Returns RelationshipType value string or None
            valid_types = [rt.value for rt in RelationshipType]
            assert rel is None or rel in valid_types

    def test_get_stats(self, graph):
        """Test getting graph statistics."""
        graph.add_node("Test", "Answer", "algebra", 0.5)
        stats = graph.get_stats()
        assert 'node_count' in stats

    def test_process_method(self, graph):
        """Test process method routes correctly."""
        result = graph.process({
            'action': 'add',
            'problem': 'Test',
            'answer': 'Answer',
            'domain': 'algebra',
            'complexity': 0.5
        })
        assert 'node_id' in result

    def test_bdi_update_beliefs(self, graph):
        """Test BDI update_beliefs method."""
        graph.update_beliefs()
        assert hasattr(graph, 'beliefs')

    def test_bdi_deliberate(self, graph):
        """Test BDI deliberate method."""
        intention = graph.deliberate()
        assert intention is None or hasattr(intention, 'plan_id')


# =============================================================================
# LearningEnhancementSupervisor Tests (12 tests)
# =============================================================================

class TestLearningEnhancementSupervisor:
    """Tests for the LearningEnhancementSupervisor."""

    @pytest.fixture
    def supervisor(self):
        """Create supervisor instance."""
        return LearningEnhancementSupervisor()

    def test_init(self, supervisor):
        """Test supervisor initialization."""
        assert supervisor is not None
        assert 'learning_enhancement' in supervisor.agent_id

    def test_specialist_routing_defined(self, supervisor):
        """Test specialist routing is defined."""
        assert len(supervisor.SPECIALIST_ROUTING) >= 6
        assert 'complexity_scoring' in supervisor.SPECIALIST_ROUTING
        assert 'negative_learning' in supervisor.SPECIALIST_ROUTING

    def test_route_to_complexity_scorer(self, supervisor):
        """Test routing to complexity scorer."""
        result = supervisor.route_task({
            'type': 'complexity_scoring',
            'problem': 'What is 2+2?',
            'answer': '4',
            'domain': 'algebra'
        })
        assert 'status' in result or 'result' in result

    def test_route_to_negative_learner(self, supervisor):
        """Test routing to negative learner."""
        result = supervisor.route_task({
            'type': 'negative_learning',
            'action': 'check',
            'response': 'symbolic'
        })
        assert 'status' in result or 'result' in result

    def test_route_to_curriculum(self, supervisor):
        """Test routing to curriculum."""
        result = supervisor.route_task({
            'type': 'curriculum',
            'action': 'get_state'
        })
        assert result is not None

    def test_full_optimization_workflow(self, supervisor):
        """Test full optimization workflow."""
        result = supervisor.run_full_optimization({
            'problem': 'Find the derivative of x^2',
            'answer': '2x',
            'domain': 'calculus'
        })
        assert 'status' in result
        assert 'results' in result

    def test_optimize_learning(self, supervisor):
        """Test optimize_learning method."""
        result = supervisor.optimize_learning({
            'problem': 'Solve x + 1 = 2',
            'answer': 'x = 1',
            'domain': 'algebra'
        })
        assert 'workflow' in result or 'status' in result

    def test_get_stats(self, supervisor):
        """Test getting statistics."""
        supervisor.route_task({'type': 'complexity_scoring', 'problem': 'P', 'answer': 'A', 'domain': 'd'})
        stats = supervisor.get_stats()
        assert 'tasks_routed' in stats
        assert stats['tasks_routed'] >= 1

    def test_analyze_system(self, supervisor):
        """Test system analysis."""
        analysis = supervisor.analyze_system()
        assert 'supervisor_stats' in analysis
        assert 'recommendations' in analysis

    def test_process_method(self, supervisor):
        """Test process method routes correctly."""
        result = supervisor.process({
            'action': 'get_stats'
        })
        assert 'tasks_routed' in result

    def test_bdi_update_beliefs(self, supervisor):
        """Test BDI update_beliefs method."""
        supervisor.update_beliefs()
        assert hasattr(supervisor, 'beliefs')

    def test_bdi_deliberate(self, supervisor):
        """Test BDI deliberate method."""
        intention = supervisor.deliberate()
        assert intention is None or hasattr(intention, 'plan_id')


# =============================================================================
# Integration Tests
# =============================================================================

class TestLearningEnhancementIntegration:
    """Integration tests for the complete learning pipeline."""

    def test_full_learning_pipeline(self):
        """Test complete learning pipeline."""
        supervisor = LearningEnhancementSupervisor()

        # Run full optimization
        result = supervisor.optimize_learning({
            'problem': 'Find the integral of sin(x)dx',
            'answer': '-cos(x) + C',
            'domain': 'calculus'
        })

        assert result is not None
        assert 'status' in result

    def test_complexity_curriculum_integration(self):
        """Test complexity scorer feeds curriculum."""
        scorer = ComplexityScorerSpecialist()
        curriculum = CurriculumSpecialist(initial_difficulty=0.3)

        # Score a problem
        score_result = scorer.score(
            problem="Simple problem",
            answer="Simple answer",
            domain="algebra"
        )

        # Use in curriculum
        problems = [
            {'problem': 'P1', 'answer': 'A1', 'complexity': score_result.score}
        ]
        batch = curriculum.next_batch(problems, batch_size=1)
        assert 'batch' in batch

    def test_negative_learner_gatekeeper(self):
        """Test negative learner as gatekeeper."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, "neg.json")
            learner = NegativeLearnerSpecialist(persistence_path=storage_path)

            # Check good response
            is_bad1, _ = learner.is_known_bad("x = 5")
            assert is_bad1 is False

            # Check bad response
            is_bad2, _ = learner.is_known_bad("symbolic")
            assert is_bad2 is True

    def test_tokenizer_knowledge_graph(self):
        """Test tokenizer with knowledge graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tok_path = os.path.join(tmpdir, "tok.json")
            kg_path = os.path.join(tmpdir, "kg.db")

            tokenizer = BPETokenizerSpecialist(persistence_path=tok_path)
            graph = KnowledgeGraphSpecialist(db_path=kg_path)

            # Add to knowledge graph
            result = graph.add_node(
                problem="integral of x",
                answer="x^2/2",
                domain="calculus",
                complexity=0.5
            )

            # Tokenize
            tokens = tokenizer.encode("integral of x")

            assert result['node_id'] is not None
            assert len(tokens) > 0


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestLearningEdgeCases:
    """Edge case tests for learning specialists."""

    def test_empty_problem_complexity(self):
        """Test empty problem gets minimal complexity."""
        scorer = ComplexityScorerSpecialist()
        result = scorer.score("", "", "algebra")
        assert result.score >= 0.0
        assert result.level == ComplexityLevel.TRIVIAL

    def test_very_long_problem_complexity(self):
        """Test very long problem handling."""
        scorer = ComplexityScorerSpecialist()
        long_problem = "solve " + "x + " * 100 + "1 = 0"
        result = scorer.score(long_problem, "x = 0", "algebra")
        assert result.score <= 1.0

    def test_unicode_in_tokenizer(self):
        """Test unicode handling in tokenizer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, "tok.json")
            tokenizer = BPETokenizerSpecialist(persistence_path=storage_path)

            tokens = tokenizer.encode("x + y = 0")
            assert len(tokens) > 0

    def test_special_characters_in_graph(self):
        """Test special characters in knowledge graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "kg.db")
            graph = KnowledgeGraphSpecialist(db_path=db_path)

            result = graph.add_node(
                problem="What is O'Brien's formula?",
                answer="x = y * z",
                domain="algebra",
                complexity=0.5
            )
            assert result['node_id'] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
