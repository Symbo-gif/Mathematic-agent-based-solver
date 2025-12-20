# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Knowledge Graph Strategy Extensions
====================================

PURPOSE:
--------
Extends MathematicalKnowledgeGraph with strategy learning query methods.
These methods enable persistent storage and retrieval of strategy patterns,
effectiveness metrics, and composition relationships.

NEW QUERY METHODS:
------------------
1. record_strategy_application() - Record strategy use on a problem
2. get_strategy_effectiveness() - Get effectiveness metrics for a strategy
3. get_strategies_by_domain() - Get strategies effective for a domain
4. find_composable_strategies() - Find complementary strategy pairs
5. get_strategy_transfer_candidates() - Find cross-domain transfer candidates

USAGE:
------
These methods are designed to be added to the MathematicalKnowledgeGraph class
either via monkey-patching or inheritance.
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import base types
from .knowledge_graph import (
    MathematicalKnowledgeGraph, NodeType, EdgeType, KnowledgeNode, KnowledgeEdge
)

logger = logging.getLogger('symbo_agentic_reasoners.knowledge_graph_extensions')


def record_strategy_application(self, strategy_id: str, trace_id: str,
                                problem_type: str, domain: str,
                                success: bool, time_ms: float,
                                confidence: float = 1.0,
                                metadata: Dict[str, Any] = None) -> str:
    """
    Record a strategy application instance.

    Stores when and how a strategy was used, with outcome metrics.
    This data feeds strategy effectiveness calculations.

    Args:
        strategy_id: Strategy pattern identifier
        trace_id: Solution trace identifier
        problem_type: Type of problem solved
        domain: Problem domain
        success: Whether strategy led to solution
        time_ms: Time taken
        confidence: Detection confidence (0-1)
        metadata: Additional application metadata

    Returns:
        Application record ID
    """
    application_id = f"app_{trace_id}_{strategy_id[-8:]}"

    # Insert into strategy_applications table
    cursor = self.conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO strategy_applications
        (application_id, strategy_id, trace_id, problem_type, domain,
         success, time_ms, detection_confidence, applied_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        application_id,
        strategy_id,
        trace_id,
        problem_type,
        domain,
        1 if success else 0,
        time_ms,
        confidence,
        datetime.now().isoformat(),
        self._dict_to_json(metadata or {})
    ))
    self.conn.commit()

    logger.debug(f"Recorded strategy application: {strategy_id} on {problem_type}")

    return application_id


def get_strategy_effectiveness(self, strategy_id: str,
                               domain: Optional[str] = None,
                               min_samples: int = 1) -> Dict[str, Any]:
    """
    Get effectiveness metrics for a strategy.

    Calculates success rate, average time, sample size, and
    domain-specific effectiveness.

    Args:
        strategy_id: Strategy identifier
        domain: Optional domain filter
        min_samples: Minimum samples for meaningful metrics

    Returns:
        Dict with effectiveness metrics:
        - overall_success_rate: Success rate across all domains
        - overall_sample_size: Total applications
        - avg_time_ms: Average solution time
        - by_domain: Domain-specific metrics
        - is_reliable: Whether sample size is sufficient
    """
    cursor = self.conn.cursor()

    # Overall metrics
    if domain:
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(success) as successes,
                AVG(time_ms) as avg_time
            FROM strategy_applications
            WHERE strategy_id = ? AND domain = ?
        """, (strategy_id, domain))
    else:
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(success) as successes,
                AVG(time_ms) as avg_time
            FROM strategy_applications
            WHERE strategy_id = ?
        """, (strategy_id,))

    row = cursor.fetchone()

    if not row or row[0] == 0:
        return {
            'overall_success_rate': 0.0,
            'overall_sample_size': 0,
            'avg_time_ms': 0.0,
            'by_domain': {},
            'is_reliable': False
        }

    total, successes, avg_time = row
    success_rate = (successes / total) if total > 0 else 0.0

    # Domain-specific metrics
    cursor.execute("""
        SELECT
            domain,
            COUNT(*) as total,
            SUM(success) as successes,
            AVG(time_ms) as avg_time
        FROM strategy_applications
        WHERE strategy_id = ?
        GROUP BY domain
    """, (strategy_id,))

    by_domain = {}
    for domain_name, d_total, d_successes, d_avg_time in cursor.fetchall():
        by_domain[domain_name] = {
            'success_rate': (d_successes / d_total) if d_total > 0 else 0.0,
            'sample_size': d_total,
            'avg_time_ms': d_avg_time or 0.0
        }

    return {
        'overall_success_rate': success_rate,
        'overall_sample_size': total,
        'avg_time_ms': avg_time or 0.0,
        'by_domain': by_domain,
        'is_reliable': total >= min_samples
    }


def get_strategies_by_domain(self, domain: str,
                             min_success_rate: float = 0.5,
                             min_samples: int = 3,
                             limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get strategies most effective for a domain.

    Retrieves strategies with high success rates in the specified domain,
    ordered by effectiveness.

    Args:
        domain: Target domain
        min_success_rate: Minimum success rate threshold
        min_samples: Minimum applications for inclusion
        limit: Maximum strategies to return

    Returns:
        List of strategy info dicts sorted by success rate
    """
    cursor = self.conn.cursor()

    cursor.execute("""
        SELECT
            sa.strategy_id,
            n.statement as strategy_name,
            COUNT(*) as sample_size,
            SUM(sa.success) * 1.0 / COUNT(*) as success_rate,
            AVG(sa.time_ms) as avg_time
        FROM strategy_applications sa
        JOIN nodes n ON sa.strategy_id = n.node_id
        WHERE sa.domain = ?
        GROUP BY sa.strategy_id
        HAVING sample_size >= ? AND success_rate >= ?
        ORDER BY success_rate DESC, sample_size DESC
        LIMIT ?
    """, (domain, min_samples, min_success_rate, limit))

    strategies = []
    for row in cursor.fetchall():
        strategies.append({
            'strategy_id': row[0],
            'strategy_name': row[1],
            'sample_size': row[2],
            'success_rate': row[3],
            'avg_time_ms': row[4],
            'domain': domain
        })

    return strategies


def find_composable_strategies(self, strategy_id: str,
                               min_co_occurrence: int = 3,
                               min_success_rate: float = 0.6,
                               limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find strategies that compose well with a given strategy.

    Identifies strategies frequently used together with high success rates.
    Uses co-occurrence in successful solution traces.

    Args:
        strategy_id: Base strategy to find compositions for
        min_co_occurrence: Minimum times strategies appeared together
        min_success_rate: Minimum success rate when composed
        limit: Maximum results to return

    Returns:
        List of composable strategy info dicts
    """
    cursor = self.conn.cursor()

    # Find strategies that appear in the same traces
    cursor.execute("""
        SELECT
            sa2.strategy_id,
            n.statement as strategy_name,
            COUNT(DISTINCT sa1.trace_id) as co_occurrences,
            SUM(sa1.success) * 1.0 / COUNT(*) as success_rate
        FROM strategy_applications sa1
        JOIN strategy_applications sa2
            ON sa1.trace_id = sa2.trace_id
            AND sa1.strategy_id != sa2.strategy_id
        JOIN nodes n ON sa2.strategy_id = n.node_id
        WHERE sa1.strategy_id = ?
        GROUP BY sa2.strategy_id
        HAVING co_occurrences >= ? AND success_rate >= ?
        ORDER BY success_rate DESC, co_occurrences DESC
        LIMIT ?
    """, (strategy_id, min_co_occurrence, min_success_rate, limit))

    compositions = []
    for row in cursor.fetchall():
        compositions.append({
            'strategy_id': row[0],
            'strategy_name': row[1],
            'co_occurrences': row[2],
            'success_rate': row[3],
            'composition_strength': row[3] * (row[2] / max(min_co_occurrence, 1))
        })

    return compositions


def get_strategy_transfer_candidates(self, source_domain: str,
                                     target_domain: str,
                                     min_source_effectiveness: float = 0.6,
                                     limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find strategies for cross-domain transfer.

    Identifies strategies highly effective in source domain with potential
    for application in target domain.

    Args:
        source_domain: Domain where strategy is proven
        target_domain: Domain to transfer to
        min_source_effectiveness: Minimum success rate in source
        limit: Maximum candidates to return

    Returns:
        List of transfer candidate dicts with metrics
    """
    cursor = self.conn.cursor()

    # Get strategies effective in source domain
    cursor.execute("""
        SELECT
            sa.strategy_id,
            n.statement as strategy_name,
            COUNT(*) as source_samples,
            SUM(sa.success) * 1.0 / COUNT(*) as source_success_rate,
            AVG(sa.time_ms) as source_avg_time
        FROM strategy_applications sa
        JOIN nodes n ON sa.strategy_id = n.node_id
        WHERE sa.domain = ?
        GROUP BY sa.strategy_id
        HAVING source_success_rate >= ?
        ORDER BY source_success_rate DESC
    """, (source_domain, min_source_effectiveness))

    source_strategies = cursor.fetchall()

    candidates = []
    for s_id, s_name, s_samples, s_rate, s_time in source_strategies:
        # Check if already used in target domain
        cursor.execute("""
            SELECT
                COUNT(*) as target_samples,
                SUM(success) * 1.0 / COUNT(*) as target_success_rate
            FROM strategy_applications
            WHERE strategy_id = ? AND domain = ?
        """, (s_id, target_domain))

        target_row = cursor.fetchone()
        target_samples = target_row[0] if target_row else 0
        target_rate = target_row[1] if (target_row and target_row[1]) else 0.0

        # Estimate transfer potential
        if target_samples > 0:
            transfer_confidence = 'validated'
            estimated_effectiveness = target_rate
        else:
            transfer_confidence = 'exploratory'
            estimated_effectiveness = s_rate * 0.7  # Conservative estimate

        candidates.append({
            'strategy_id': s_id,
            'strategy_name': s_name,
            'source_domain': source_domain,
            'target_domain': target_domain,
            'source_effectiveness': s_rate,
            'source_samples': s_samples,
            'target_effectiveness': target_rate if target_samples > 0 else None,
            'target_samples': target_samples,
            'estimated_effectiveness': estimated_effectiveness,
            'transfer_confidence': transfer_confidence
        })

    # Sort by estimated effectiveness
    candidates.sort(key=lambda x: x['estimated_effectiveness'], reverse=True)

    return candidates[:limit]


def _dict_to_json(self, d: Dict) -> str:
    """Helper to convert dict to JSON string."""
    import json
    return json.dumps(d, default=str)


# Extension installer
def install_strategy_extensions(knowledge_graph: MathematicalKnowledgeGraph):
    """
    Install strategy query methods onto a KnowledgeGraph instance.

    Args:
        knowledge_graph: MathematicalKnowledgeGraph instance to extend

    Usage:
        kg = MathematicalKnowledgeGraph()
        install_strategy_extensions(kg)
        kg.record_strategy_application(...)  # New methods available
    """
    # Bind methods to instance
    import types

    knowledge_graph.record_strategy_application = types.MethodType(
        record_strategy_application, knowledge_graph
    )
    knowledge_graph.get_strategy_effectiveness = types.MethodType(
        get_strategy_effectiveness, knowledge_graph
    )
    knowledge_graph.get_strategies_by_domain = types.MethodType(
        get_strategies_by_domain, knowledge_graph
    )
    knowledge_graph.find_composable_strategies = types.MethodType(
        find_composable_strategies, knowledge_graph
    )
    knowledge_graph.get_strategy_transfer_candidates = types.MethodType(
        get_strategy_transfer_candidates, knowledge_graph
    )
    knowledge_graph._dict_to_json = types.MethodType(
        _dict_to_json, knowledge_graph
    )

    logger.info("Strategy extensions installed on KnowledgeGraph")


if __name__ == "__main__":
    """Test strategy extensions"""
    print("=" * 80)
    print("KNOWLEDGE GRAPH STRATEGY EXTENSIONS TEST")
    print("=" * 80)
    print()

    # Create test knowledge graph
    from .knowledge_graph import MathematicalKnowledgeGraph
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_kg.db")
        kg = MathematicalKnowledgeGraph(db_path=db_path)

        # Install extensions
        install_strategy_extensions(kg)
        print("[OK] Strategy extensions installed")
        print()

        # Test 1: Record strategy applications
        print("TEST 1: Record Strategy Applications")
        print("-" * 40)

        # Add a strategy node first
        kg._insert_node(KnowledgeNode(
            node_id="strategy_invariant_method",
            node_type=NodeType.STRATEGY,
            statement="Invariant Method",
            proof=None,
            domain="mathematics",
            confidence=1.0,
            metadata={}
        ))

        # Record applications
        for i in range(5):
            success = i < 4  # 4 successes, 1 failure
            kg.record_strategy_application(
                strategy_id="strategy_invariant_method",
                trace_id=f"trace_{i:03d}",
                problem_type="algebra",
                domain="algebra",
                success=success,
                time_ms=800 + i * 50,
                confidence=0.9
            )

        print("Recorded 5 strategy applications (4 successes, 1 failure)")
        print()

        # Test 2: Get strategy effectiveness
        print("TEST 2: Get Strategy Effectiveness")
        print("-" * 40)
        effectiveness = kg.get_strategy_effectiveness("strategy_invariant_method")
        print(f"Overall Success Rate: {effectiveness['overall_success_rate']:.1%}")
        print(f"Sample Size: {effectiveness['overall_sample_size']}")
        print(f"Avg Time: {effectiveness['avg_time_ms']:.1f} ms")
        print(f"Reliable: {effectiveness['is_reliable']}")
        print()

        # Test 3: Get strategies by domain
        print("TEST 3: Get Strategies by Domain")
        print("-" * 40)
        strategies = kg.get_strategies_by_domain("algebra", min_samples=3)
        print(f"Found {len(strategies)} strategies for algebra domain")
        for s in strategies:
            print(f"  - {s['strategy_name']}: {s['success_rate']:.1%} ({s['sample_size']} samples)")
        print()

        # Test 4: Find composable strategies
        print("TEST 4: Find Composable Strategies")
        print("-" * 40)
        print("(Requires multiple strategies in same traces - skipping)")
        print()

        # Test 5: Get transfer candidates
        print("TEST 5: Get Transfer Candidates")
        print("-" * 40)
        candidates = kg.get_strategy_transfer_candidates("algebra", "geometry")
        print(f"Found {len(candidates)} transfer candidates (algebra -> geometry)")
        for c in candidates:
            print(f"  - {c['strategy_name']}: {c['source_effectiveness']:.1%} in source")
        print()

        kg.close()

    print("=" * 80)
    print("KNOWLEDGE GRAPH STRATEGY EXTENSIONS TEST COMPLETE")
    print("=" * 80)
