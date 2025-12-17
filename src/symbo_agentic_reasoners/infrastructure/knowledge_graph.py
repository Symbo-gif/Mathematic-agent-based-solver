# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Mathematical Knowledge Graph
=============================

Structured representation of mathematical knowledge for research-level reasoning.

CAPABILITIES:
------------
- Store theorems, definitions, conjectures, heuristics, examples
- Relationship tracking (implies, generalizes, contradicts, applies-to)
- Graph querying and traversal
- Proof chain construction
- Counterexample retrieval
- Analogy-based reasoning

GRAPH STRUCTURE:
----------------
Nodes:
- Theorem: Proven mathematical statement
- Definition: Mathematical concept definition
- Conjecture: Unproven hypothesis
- Heuristic: Problem-solving pattern
- Example: Concrete instantiation
- Counterexample: Disproof instance

Edges:
- IMPLIES: A → B (A implies B)
- GENERALIZES: A generalizes B
- CONTRADICTS: A contradicts B
- APPLIES_TO: Theorem applies to domain
- EXAMPLE_OF: Instance of concept
- DEPENDS_ON: Proof dependency
- ANALOGOUS_TO: Similar structure

PERSISTENCE:
-----------
- SQLite backend for persistence
- JSON export for portability
- Graph queries with path finding

REFERENCE:
---------
- Plan: Days 37-38 - Mathematical knowledge graph
- Target: Enable research-level reasoning and discovery
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import uuid

logger = logging.getLogger('symbo_agentic_reasoners.knowledge_graph')


class NodeType(Enum):
    """Types of knowledge nodes."""
    THEOREM = "theorem"
    DEFINITION = "definition"
    CONJECTURE = "conjecture"
    HEURISTIC = "heuristic"
    EXAMPLE = "example"
    COUNTEREXAMPLE = "counterexample"
    AXIOM = "axiom"


class EdgeType(Enum):
    """Types of relationships between knowledge nodes."""
    IMPLIES = "implies"
    GENERALIZES = "generalizes"
    CONTRADICTS = "contradicts"
    APPLIES_TO = "applies_to"
    EXAMPLE_OF = "example_of"
    DEPENDS_ON = "depends_on"
    ANALOGOUS_TO = "analogous_to"
    SPECIALIZES = "specializes"


@dataclass
class KnowledgeNode:
    """Node in the mathematical knowledge graph."""
    node_id: str
    node_type: NodeType
    statement: str
    domain: str  # 'algebra', 'analysis', 'topology', etc.
    proof: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    confidence: float = 1.0  # For conjectures: 0.0-1.0


@dataclass
class KnowledgeEdge:
    """Edge in the mathematical knowledge graph."""
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    strength: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MathematicalKnowledgeGraph:
    """
    Graph-based mathematical knowledge representation system.

    Enables research-level reasoning through:
    - Theorem dependency tracking
    - Proof chain construction
    - Analogy detection
    - Counterexample retrieval
    - Cross-domain pattern recognition
    """

    def __init__(self, db_path: str = None):
        """
        Initialize knowledge graph.

        Args:
            db_path: Path to SQLite database (creates if not exists)
        """
        if db_path is None:
            db_path = "data/knowledge_graph/math_kg.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self._create_tables()

        # In-memory cache for fast access
        self.nodes_cache: Dict[str, KnowledgeNode] = {}
        self.edges_cache: List[KnowledgeEdge] = []

        logger.info(f"Mathematical Knowledge Graph initialized at {self.db_path}")

    def _create_tables(self):
        """Create database schema."""
        cursor = self.conn.cursor()

        # Nodes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                statement TEXT NOT NULL,
                domain TEXT NOT NULL,
                proof TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence REAL DEFAULT 1.0
            )
        ''')

        # Edges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                edge_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                metadata TEXT,
                FOREIGN KEY (source_id) REFERENCES nodes(node_id),
                FOREIGN KEY (target_id) REFERENCES nodes(node_id)
            )
        ''')

        # Indices for fast queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_node_type ON nodes(node_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_domain ON nodes(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edge_type ON edges(edge_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON edges(source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_target ON edges(target_id)')

        self.conn.commit()

    def add_theorem(
        self,
        statement: str,
        domain: str,
        proof: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> KnowledgeNode:
        """
        Add theorem to knowledge graph.

        Args:
            statement: Theorem statement
            domain: Mathematical domain
            proof: Proof (if available)
            metadata: Additional information

        Returns:
            Created knowledge node
        """
        node = KnowledgeNode(
            node_id=str(uuid.uuid4()),
            node_type=NodeType.THEOREM,
            statement=statement,
            domain=domain,
            proof=proof,
            metadata=metadata or {},
            confidence=1.0
        )

        self._insert_node(node)
        self.nodes_cache[node.node_id] = node

        logger.info(f"Added theorem: {statement[:50]}...")
        return node

    def add_conjecture(
        self,
        statement: str,
        domain: str,
        confidence: float = 0.5,
        evidence: List[str] = None
    ) -> KnowledgeNode:
        """
        Add conjecture to knowledge graph.

        Args:
            statement: Conjecture statement
            domain: Mathematical domain
            confidence: Confidence level (0.0-1.0)
            evidence: Supporting evidence

        Returns:
            Created knowledge node
        """
        node = KnowledgeNode(
            node_id=str(uuid.uuid4()),
            node_type=NodeType.CONJECTURE,
            statement=statement,
            domain=domain,
            confidence=confidence,
            metadata={'evidence': evidence or []}
        )

        self._insert_node(node)
        self.nodes_cache[node.node_id] = node

        logger.info(f"Added conjecture: {statement[:50]}... (confidence: {confidence})")
        return node

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship: EdgeType,
        strength: float = 1.0,
        metadata: Dict[str, Any] = None
    ) -> KnowledgeEdge:
        """
        Add relationship between knowledge nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship: Type of relationship
            strength: Relationship strength (0.0-1.0)
            metadata: Additional information

        Returns:
            Created edge
        """
        edge = KnowledgeEdge(
            edge_id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            edge_type=relationship,
            strength=strength,
            metadata=metadata or {}
        )

        self._insert_edge(edge)
        self.edges_cache.append(edge)

        return edge

    def query_theorems_using(
        self,
        theorem_statement: str
    ) -> List[KnowledgeNode]:
        """
        Find all theorems that use/depend on given theorem.

        Args:
            theorem_statement: Theorem to search for

        Returns:
            List of dependent theorems
        """
        # Find theorem node
        source_node = self._find_node_by_statement(theorem_statement)
        if not source_node:
            return []

        # Find all nodes with DEPENDS_ON edge to this theorem
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT n.* FROM nodes n
            JOIN edges e ON n.node_id = e.source_id
            WHERE e.target_id = ? AND e.edge_type = ?
        ''', (source_node.node_id, EdgeType.DEPENDS_ON.value))

        results = []
        for row in cursor.fetchall():
            node = self._row_to_node(row)
            results.append(node)

        return results

    def find_counterexamples(
        self,
        conjecture_id: str
    ) -> List[KnowledgeNode]:
        """
        Find counterexamples to a conjecture.

        Args:
            conjecture_id: ID of conjecture node

        Returns:
            List of counterexample nodes
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT n.* FROM nodes n
            JOIN edges e ON n.node_id = e.source_id
            WHERE e.target_id = ? AND e.edge_type = ? AND n.node_type = ?
        ''', (conjecture_id, EdgeType.CONTRADICTS.value, NodeType.COUNTEREXAMPLE.value))

        return [self._row_to_node(row) for row in cursor.fetchall()]

    def find_analogous_theorems(
        self,
        theorem_id: str,
        min_strength: float = 0.5
    ) -> List[Tuple[KnowledgeNode, float]]:
        """
        Find theorems analogous to given theorem.

        Enables cross-domain transfer learning.

        Args:
            theorem_id: ID of theorem
            min_strength: Minimum analogy strength

        Returns:
            List of (analogous_theorem, strength) tuples
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT n.*, e.strength FROM nodes n
            JOIN edges e ON n.node_id = e.target_id
            WHERE e.source_id = ? AND e.edge_type = ? AND e.strength >= ?
        ''', (theorem_id, EdgeType.ANALOGOUS_TO.value, min_strength))

        results = []
        for row in cursor.fetchall():
            node = self._row_to_node(row[:-1])
            strength = row[-1]
            results.append((node, strength))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def construct_proof_chain(
        self,
        theorem_id: str
    ) -> Dict[str, Any]:
        """
        Construct proof chain showing all dependencies.

        Args:
            theorem_id: ID of theorem to analyze

        Returns:
            Dict with proof chain and dependency tree
        """
        dependencies = self._get_dependencies_recursive(theorem_id, set())

        return {
            'theorem_id': theorem_id,
            'dependencies': list(dependencies),
            'dependency_count': len(dependencies),
            'method': 'graph_traversal'
        }

    def _get_dependencies_recursive(
        self,
        node_id: str,
        visited: Set[str]
    ) -> Set[str]:
        """Recursively find all dependencies."""
        if node_id in visited:
            return set()

        visited.add(node_id)
        dependencies = {node_id}

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT target_id FROM edges
            WHERE source_id = ? AND edge_type = ?
        ''', (node_id, EdgeType.DEPENDS_ON.value))

        for (target_id,) in cursor.fetchall():
            dependencies.update(self._get_dependencies_recursive(target_id, visited))

        return dependencies

    def export_to_json(self, filepath: str):
        """Export entire knowledge graph to JSON."""
        cursor = self.conn.cursor()

        cursor.execute('SELECT * FROM nodes')
        nodes = [self._row_to_dict(row, 'node') for row in cursor.fetchall()]

        cursor.execute('SELECT * FROM edges')
        edges = [self._row_to_dict(row, 'edge') for row in cursor.fetchall()]

        graph_data = {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'node_count': len(nodes),
                'edge_count': len(edges),
                'domains': list(set(n['domain'] for n in nodes))
            }
        }

        with open(filepath, 'w') as f:
            json.dump(graph_data, f, indent=2, default=str)

        logger.info(f"Exported knowledge graph to {filepath}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM nodes')
        node_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM edges')
        edge_count = cursor.fetchone()[0]

        cursor.execute('SELECT domain, COUNT(*) FROM nodes GROUP BY domain')
        domain_stats = dict(cursor.fetchall())

        cursor.execute('SELECT node_type, COUNT(*) FROM nodes GROUP BY node_type')
        type_stats = dict(cursor.fetchall())

        return {
            'total_nodes': node_count,
            'total_edges': edge_count,
            'nodes_by_domain': domain_stats,
            'nodes_by_type': type_stats
        }

    def _insert_node(self, node: KnowledgeNode):
        """Insert node into database."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO nodes (node_id, node_type, statement, domain, proof, metadata, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            node.node_id,
            node.node_type.value,
            node.statement,
            node.domain,
            node.proof,
            json.dumps(node.metadata),
            node.confidence
        ))
        self.conn.commit()

    def _insert_edge(self, edge: KnowledgeEdge):
        """Insert edge into database."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO edges (edge_id, source_id, target_id, edge_type, strength, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            edge.edge_id,
            edge.source_id,
            edge.target_id,
            edge.edge_type.value,
            edge.strength,
            json.dumps(edge.metadata)
        ))
        self.conn.commit()

    def _find_node_by_statement(self, statement: str) -> Optional[KnowledgeNode]:
        """Find node by statement text."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM nodes WHERE statement = ?', (statement,))
        row = cursor.fetchone()
        return self._row_to_node(row) if row else None

    def _row_to_node(self, row: tuple) -> KnowledgeNode:
        """Convert database row to KnowledgeNode."""
        return KnowledgeNode(
            node_id=row[0],
            node_type=NodeType(row[1]),
            statement=row[2],
            domain=row[3],
            proof=row[4],
            metadata=json.loads(row[5]) if row[5] else {},
            created_at=row[6],
            confidence=row[7]
        )

    def _row_to_dict(self, row: tuple, row_type: str) -> Dict:
        """Convert row to dictionary."""
        if row_type == 'node':
            keys = ['node_id', 'node_type', 'statement', 'domain', 'proof', 'metadata', 'created_at', 'confidence']
        else:  # edge
            keys = ['edge_id', 'source_id', 'target_id', 'edge_type', 'strength', 'metadata']

        result = dict(zip(keys, row))
        if 'metadata' in result and result['metadata']:
            result['metadata'] = json.loads(result['metadata'])
        return result

    def close(self):
        """Close database connection."""
        self.conn.close()


# Singleton instance
_kg_instance = None

def get_knowledge_graph() -> MathematicalKnowledgeGraph:
    """Get global knowledge graph instance."""
    global _kg_instance
    if _kg_instance is None:
        _kg_instance = MathematicalKnowledgeGraph()
    return _kg_instance


if __name__ == "__main__":
    """Test Mathematical Knowledge Graph."""
    print("=" * 80)
    print("MATHEMATICAL KNOWLEDGE GRAPH TEST")
    print("=" * 80)

    kg = MathematicalKnowledgeGraph("test_kg.db")

    # Add fundamental theorem
    pythagorean = kg.add_theorem(
        statement="In right triangle: a² + b² = c²",
        domain="geometry",
        proof="Classical geometric proof",
        metadata={'discoverer': 'Pythagoras', 'year': -500}
    )

    # Add related theorem
    distance = kg.add_theorem(
        statement="Distance formula: d = √((x₂-x₁)² + (y₂-y₁)²)",
        domain="geometry",
        metadata={'application': 'analytic_geometry'}
    )

    # Link them
    kg.add_relationship(
        distance.node_id,
        pythagorean.node_id,
        EdgeType.DEPENDS_ON,
        strength=1.0
    )

    # Add conjecture
    goldbach = kg.add_conjecture(
        statement="Every even integer > 2 is sum of two primes",
        domain="number_theory",
        confidence=0.99  # Very high confidence but unproven
    )

    # Statistics
    stats = kg.get_statistics()
    print(f"\nKnowledge Graph Statistics:")
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Total edges: {stats['total_edges']}")
    print(f"  Domains: {list(stats['nodes_by_domain'].keys())}")

    # Query
    dependents = kg.query_theorems_using("In right triangle: a² + b² = c²")
    print(f"\n  Theorems using Pythagorean theorem: {len(dependents)}")

    kg.close()
    print("\nKnowledge Graph operational!")
