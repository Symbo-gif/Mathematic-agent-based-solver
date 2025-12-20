# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Phase 1 Integration Test
========================

Comprehensive test of Strategy Learning Phase 1 components:
1. KnowledgeGraph schema extensions
2. StrategyNode and SuccessMetrics
3. Strategy pattern data structures
4. Bootstrap strategy library
5. Database queries

USAGE:
------
python scripts/test_phase1_strategy_learning.py
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symbo_agentic_reasoners.infrastructure.knowledge_graph import (
    MathematicalKnowledgeGraph,
    StrategyNode,
    SuccessMetrics,
    NodeType,
    EdgeType
)
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_patterns import (
    StrategyPattern,
    StrategyDetectionResult,
    StrategyDetection,
    TemplatePattern,
    StrategyApplication,
    StrategyCategory,
    DetectionConfidence,
    get_strategy_keywords,
    compute_composition_strength,
    STRATEGY_KEYWORDS
)
import uuid
from datetime import datetime


def test_success_metrics():
    """Test SuccessMetrics dataclass."""
    print("\n" + "=" * 80)
    print("TEST 1: SuccessMetrics")
    print("=" * 80)

    metrics = SuccessMetrics(
        domain="algebra",
        applications=10,
        successes=8,
        avg_time_ms=1250.5,
        avg_complexity_reduction=0.3,
        last_success="2025-12-19T10:30:00"
    )

    print(f"[OK] Created SuccessMetrics for {metrics.domain}")
    print(f"  Applications: {metrics.applications}")
    print(f"  Successes: {metrics.successes}")
    print(f"  Success Rate: {metrics.successes / metrics.applications:.2%}")
    print(f"  Avg Time: {metrics.avg_time_ms:.1f}ms")

    assert metrics.domain == "algebra"
    assert metrics.applications == 10
    assert metrics.successes == 8

    print("[OK] All SuccessMetrics assertions passed!")


def test_strategy_node():
    """Test StrategyNode creation and serialization."""
    print("\n" + "=" * 80)
    print("TEST 2: StrategyNode")
    print("=" * 80)

    # Create a strategy node
    node = StrategyNode(
        node_id="strategy_test_invariant",
        node_type=NodeType.STRATEGY,
        statement="Invariant Method",
        domain="algebra",
        category="heuristic",
        abstract_description="Find quantities preserved under transformations",
        detection_signals=["invariant", "preserved", "conserved"],
        applicability_conditions=["has_symmetry=true", "domain=algebra|topology"],
        composition_compatible=["strategy_symmetrization"],
        success_rates_by_domain={
            "algebra": SuccessMetrics(domain="algebra", applications=5, successes=4, avg_time_ms=1000.0),
            "topology": SuccessMetrics(domain="topology", applications=3, successes=2, avg_time_ms=1500.0)
        },
        typical_agent_sequence=["structure_recognizer", "invariant_measure_specialist"],
        reformulation_pattern="algebraic → invariant structure"
    )

    print(f"[OK] Created StrategyNode: {node.statement}")
    print(f"  Category: {node.category}")
    print(f"  Domain: {node.domain}")
    print(f"  Detection signals: {len(node.detection_signals)}")
    print(f"  Applicability conditions: {len(node.applicability_conditions)}")
    print(f"  Success rates tracked for: {list(node.success_rates_by_domain.keys())}")

    # Check inheritance
    assert isinstance(node, StrategyNode)
    assert node.node_type == NodeType.STRATEGY
    assert node.category == "heuristic"
    assert len(node.detection_signals) == 3

    print("[OK] All StrategyNode assertions passed!")


def test_knowledge_graph_schema():
    """Test KnowledgeGraph schema with strategy support."""
    print("\n" + "=" * 80)
    print("TEST 3: KnowledgeGraph Schema Extensions")
    print("=" * 80)

    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_kg.db"

    try:
        kg = MathematicalKnowledgeGraph(str(db_path))

        # Test 1: Verify tables exist
        cursor = kg.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"[OK] Database created at {db_path}")
        print(f"  Tables: {', '.join(tables)}")

        assert "nodes" in tables
        assert "edges" in tables
        assert "strategy_applications" in tables
        print("[OK] All required tables exist!")

        # Test 2: Verify node schema includes strategy columns
        cursor.execute("PRAGMA table_info(nodes)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        print(f"\n[OK] Node table has {len(columns)} columns")

        strategy_columns = [
            'strategy_category', 'abstract_description', 'detection_signals',
            'applicability_conditions', 'composition_compatible',
            'success_rates_by_domain', 'typical_agent_sequence', 'reformulation_pattern'
        ]

        for col in strategy_columns:
            assert col in columns, f"Missing column: {col}"

        print(f"[OK] All strategy-specific columns present: {', '.join(strategy_columns)}")

        # Test 3: Insert a strategy node
        strategy = StrategyNode(
            node_id=str(uuid.uuid4()),
            node_type=NodeType.STRATEGY,
            statement="Test Strategy",
            domain="test_domain",
            category="heuristic",
            abstract_description="Test description",
            detection_signals=["test_signal"],
            applicability_conditions=["test_condition"],
            composition_compatible=[],
            success_rates_by_domain={
                "test_domain": SuccessMetrics(
                    domain="test_domain",
                    applications=1,
                    successes=1,
                    avg_time_ms=500.0
                )
            },
            typical_agent_sequence=["test_agent"]
        )

        kg._insert_node(strategy)
        print(f"\n[OK] Inserted strategy node: {strategy.statement}")

        # Test 4: Retrieve strategy node
        retrieved = kg.get_node(strategy.node_id)

        assert retrieved is not None
        assert isinstance(retrieved, StrategyNode)
        assert retrieved.statement == "Test Strategy"
        assert retrieved.category == "heuristic"
        assert len(retrieved.detection_signals) == 1
        assert "test_domain" in retrieved.success_rates_by_domain

        print(f"[OK] Retrieved strategy node successfully")
        print(f"  Statement: {retrieved.statement}")
        print(f"  Category: {retrieved.category}")
        print(f"  Detection signals: {retrieved.detection_signals}")

        # Test 5: Verify strategy_applications table schema
        cursor.execute("PRAGMA table_info(strategy_applications)")
        app_columns = {row[1]: row[2] for row in cursor.fetchall()}

        required_app_columns = [
            'application_id', 'strategy_id', 'trace_id', 'conversation_id',
            'problem_type', 'domain', 'success', 'time_ms',
            'detection_confidence', 'applied_at', 'metadata'
        ]

        for col in required_app_columns:
            assert col in app_columns, f"Missing application column: {col}"

        print(f"\n[OK] strategy_applications table has all required columns")

        # Test 6: Verify indices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indices = [row[0] for row in cursor.fetchall()]

        expected_indices = [
            'idx_strategy_applications_strategy',
            'idx_strategy_applications_domain',
            'idx_strategy_applications_problem'
        ]

        for idx in expected_indices:
            assert idx in indices, f"Missing index: {idx}"

        print(f"[OK] All strategy application indices exist")

        kg.close()
        print("\n[OK] All KnowledgeGraph schema tests passed!")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_strategy_patterns():
    """Test strategy pattern data structures."""
    print("\n" + "=" * 80)
    print("TEST 4: Strategy Pattern Data Structures")
    print("=" * 80)

    # Test StrategyPattern
    pattern = StrategyPattern(
        pattern_id="test_pattern",
        name="Test Pattern",
        category=StrategyCategory.HEURISTIC,
        description="Test pattern description",
        abstract_description="Abstract test",
        detection_signals=["signal1", "signal2"],
        applicability_conditions=["condition1"]
    )

    pattern.add_application(success=True, domain="algebra")
    pattern.add_application(success=True, domain="algebra")
    pattern.add_application(success=False, domain="topology")

    print(f"[OK] Created StrategyPattern: {pattern.name}")
    print(f"  Success rate: {pattern.success_rate:.2%}")
    print(f"  Total applications: {pattern.total_applications}")

    assert pattern.total_applications == 3
    assert pattern.success_count == 2
    assert abs(pattern.success_rate - 0.6667) < 0.01

    # Test StrategyDetectionResult
    detection = StrategyDetectionResult(
        strategy_id="test_strategy",
        strategy_name="Test Strategy",
        category=StrategyCategory.HEURISTIC,
        confidence=0.85,
        evidence=["evidence1", "evidence2"]
    )

    print(f"\n[OK] Created StrategyDetectionResult")
    print(f"  Confidence: {detection.confidence:.2%}")
    print(f"  Level: {detection.confidence_level.value}")

    assert detection.confidence_level == DetectionConfidence.HIGH

    # Test StrategyApplication
    app = StrategyApplication(
        application_id=str(uuid.uuid4()),
        strategy_id="strategy_test",
        trace_id="trace_123",
        conversation_id="conv_456",
        problem_type="integration",
        domain="calculus",
        success=True,
        time_ms=1250.5,
        detection_confidence=0.85
    )

    app_dict = app.to_dict()

    print(f"\n[OK] Created StrategyApplication")
    print(f"  Strategy: {app.strategy_id}")
    print(f"  Success: {app.success}")
    print(f"  Time: {app.time_ms}ms")

    assert 'application_id' in app_dict
    assert app_dict['success'] == True

    print("\n[OK] All strategy pattern tests passed!")


def test_strategy_keywords():
    """Test strategy keyword vocabulary."""
    print("\n" + "=" * 80)
    print("TEST 5: Strategy Keywords and Composition")
    print("=" * 80)

    # Test keyword retrieval
    polya_keywords = get_strategy_keywords('polya_cycle')

    print(f"[OK] Retrieved keywords for 'polya_cycle'")
    print(f"  Keywords: {len(polya_keywords['keywords'])} items")
    print(f"  Agent patterns: {len(polya_keywords['agent_patterns'])} items")
    print(f"  Metadata signals: {len(polya_keywords['metadata_signals'])} items")

    assert 'reformulate' in polya_keywords['keywords']
    assert 'decompose' in polya_keywords['keywords']

    # Test all 12 strategies have keywords
    strategy_keys = [
        'polya_cycle', 'problem_re_encoding', 'local_global',
        'invariant_method', 'extremal_elements', 'symmetrization', 'functional_viewpoint',
        'infinite_descent', 'graphical_revisualization', 'fixed_point',
        'template_mining', 'multi_solution_synthesis'
    ]

    print(f"\n[OK] Testing all {len(strategy_keys)} strategies have keywords:")
    for key in strategy_keys:
        keywords = get_strategy_keywords(key)
        assert len(keywords['keywords']) > 0, f"No keywords for {key}"
        print(f"  [OK] {key}: {len(keywords['keywords'])} keywords")

    # Test composition strength
    strength = compute_composition_strength('polya_cycle', 'invariant_method')

    print(f"\n[OK] Composition strength (Pólya + Invariant): {strength:.2%}")
    assert strength > 0.5

    print("\n[OK] All keyword and composition tests passed!")


def test_bootstrap_script():
    """Test bootstrap script functionality."""
    print("\n" + "=" * 80)
    print("TEST 6: Bootstrap Strategy Library")
    print("=" * 80)

    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_bootstrap.db"

    try:
        # Import and run bootstrap
        from symbo_agentic_reasoners.infrastructure import knowledge_graph as kg_module

        # Create new KG instance
        kg = MathematicalKnowledgeGraph(str(db_path))

        # Manually set as global instance for bootstrap
        original_instance = kg_module._kg_instance
        kg_module._kg_instance = kg

        try:
            # Import bootstrap function directly by path
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bootstrap_strategy_library",
                Path(__file__).parent / "bootstrap_strategy_library.py"
            )
            bootstrap_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bootstrap_module)

            print("Running bootstrap_strategy_library()...")
            bootstrap_module.bootstrap_strategy_library()

            # Verify strategies were created
            stats = kg.get_statistics()

            print(f"\n[OK] Bootstrap completed!")
            print(f"  Total nodes: {stats['total_nodes']}")
            print(f"  Total edges: {stats['total_edges']}")

            strategy_count = stats.get('nodes_by_type', {}).get('strategy', 0)
            print(f"  Strategy nodes: {strategy_count}")

            assert strategy_count == 12, f"Expected 12 strategies, got {strategy_count}"

            # Query specific strategies
            cursor = kg.conn.cursor()
            cursor.execute("SELECT statement, strategy_category FROM nodes WHERE node_type = 'strategy'")
            strategies = cursor.fetchall()

            print(f"\n[OK] All 12 strategies populated:")
            categories = {}
            for name, category in strategies:
                print(f"  [OK] {name} ({category})")
                categories[category] = categories.get(category, 0) + 1

            print(f"\n[OK] Category distribution:")
            for cat, count in categories.items():
                print(f"  {cat}: {count} strategies")

            assert categories.get('structural', 0) == 3
            assert categories.get('heuristic', 0) == 4
            assert categories.get('nonstandard', 0) == 3
            assert categories.get('meta', 0) == 2

            # Check composition edges
            cursor.execute("SELECT COUNT(*) FROM edges WHERE edge_type = 'composed_with'")
            comp_count = cursor.fetchone()[0]

            print(f"\n[OK] Composition edges: {comp_count}")
            assert comp_count > 0

            print("\n[OK] All bootstrap tests passed!")

        finally:
            # Restore original instance
            kg_module._kg_instance = original_instance

        kg.close()

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_edge_types():
    """Test new edge types."""
    print("\n" + "=" * 80)
    print("TEST 7: New Edge Types")
    print("=" * 80)

    new_edge_types = [
        EdgeType.SOLVED_BY,
        EdgeType.EFFECTIVE_FOR,
        EdgeType.COMPOSED_WITH,
        EdgeType.PREREQUISITE_OF,
        EdgeType.ENABLES,
        EdgeType.SUBSUMES,
        EdgeType.REFINES
    ]

    print("[OK] Verifying new edge types exist:")
    for edge_type in new_edge_types:
        print(f"  [OK] {edge_type.name} = '{edge_type.value}'")
        assert edge_type.value in [
            'solved_by', 'effective_for', 'composed_with',
            'prerequisite_of', 'enables', 'subsumes', 'refines'
        ]

    print("\n[OK] All edge type tests passed!")


def run_all_tests():
    """Run all Phase 1 tests."""
    print("=" * 80)
    print("PHASE 1 STRATEGY LEARNING - COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    tests = [
        ("SuccessMetrics", test_success_metrics),
        ("StrategyNode", test_strategy_node),
        ("KnowledgeGraph Schema", test_knowledge_graph_schema),
        ("Strategy Patterns", test_strategy_patterns),
        ("Strategy Keywords", test_strategy_keywords),
        ("Bootstrap Script", test_bootstrap_script),
        ("Edge Types", test_edge_types),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n[FAIL] TEST FAILED: {name}")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed} [OK]")
    print(f"Failed: {failed} [FAIL]")

    if failed == 0:
        print("\n ALL PHASE 1 TESTS PASSED!")
        print("\nPhase 1 is ready. Components verified:")
        print("  [OK] KnowledgeGraph schema extensions (STRATEGY node, 7 edge types, strategy_applications table)")
        print("  [OK] StrategyNode and SuccessMetrics dataclasses")
        print("  [OK] Strategy pattern data structures (5 classes)")
        print("  [OK] Strategy keywords for all 12 strategies")
        print("  [OK] Bootstrap script (12 strategies + composition edges)")
        print("\nReady to proceed with Phase 2: Strategy Learning Agents")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please review errors above.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
