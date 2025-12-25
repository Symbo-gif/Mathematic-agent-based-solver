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
LEARNING ENHANCEMENT TEAM - Knowledge Graph Specialist (Tier 3)
================================================================

Manages graph-structured mathematical knowledge with relationship inference.
Transforms flat dictionary knowledge store into interconnected knowledge graph.

PROBLEM:
-------
Flat dictionary knowledge store lacks relationship awareness:
- No connection between "x^2" and "4" (specialization)
- No link between "sin" and "arcsin" (inverses)
- No chain from "derivative" to "integral" (related concepts)

SOLUTION:
--------
SQLite-backed knowledge graph with:
- Nodes: Problem-answer pairs with metadata
- Edges: Inferred relationships between nodes
- Queries: Graph traversal for related knowledge

RELATIONSHIP TYPES:
------------------
1. generalizes: x^2 generalizes 4
2. specializes: 4 specializes x^2
3. transforms_to: sin(x)^2 + cos(x)^2 -> 1
4. requires: integral requires antiderivative
5. similar_to: sqrt(2) similar to sqrt(3)
6. inverse_of: sin <-> arcsin
7. derives_from: chain rule derives from composition
8. proves: axiom proves theorem

REFERENCE:
---------
- Plan: lexical-leaping-tower.md Phase 3 Priority 6
"""

import os
import re
import sqlite3
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

from . import KnowledgeNode, KnowledgeEdge, RelationshipType

logger = logging.getLogger('symbo_agentic_reasoners.learning.knowledge_graph')


class KnowledgeGraphSpecialist(BDIAgent):
    """
    Knowledge Graph Specialist - Tier 3

    Manages graph-structured mathematical knowledge with SQLite backend.
    Infers relationships between problems and enables graph-based retrieval.

    ROLE:
    ----
    1. Build and maintain knowledge graph
    2. Infer relationships between problems
    3. Enable graph-based knowledge retrieval
    4. Track relationship patterns

    GRAPH STRUCTURE:
    ---------------
    - Nodes: Problem-answer pairs with complexity, domain, embeddings
    - Edges: Typed relationships with weights

    RELATIONSHIP INFERENCE:
    ----------------------
    - Text similarity -> similar_to
    - Containment -> generalizes/specializes
    - Function pairs -> inverse_of
    - Topic keywords -> requires/derives_from

    Example:
        >>> graph = KnowledgeGraphSpecialist()
        >>> node_id = graph.add_node("solve x^2 = 4", "x = ±2", "algebra")
        >>> related = graph.query_related("x = 2", max_depth=2)
    """

    # Inverse function pairs
    INVERSE_PAIRS = [
        ('sin', 'arcsin'), ('cos', 'arccos'), ('tan', 'arctan'),
        ('sinh', 'arcsinh'), ('cosh', 'arccosh'), ('tanh', 'arctanh'),
        ('log', 'exp'), ('ln', 'exp'), ('sqrt', 'square'),
        ('derivative', 'integral'), ('differentiate', 'integrate'),
    ]

    # Topic keywords for relationship inference
    TOPIC_KEYWORDS = {
        'calculus': ['derivative', 'integral', 'limit', 'continuous', 'differentiable'],
        'algebra': ['solve', 'factor', 'expand', 'simplify', 'polynomial'],
        'linear_algebra': ['matrix', 'vector', 'eigenvalue', 'determinant', 'rank'],
        'number_theory': ['prime', 'divisor', 'gcd', 'lcm', 'modulo'],
        'geometry': ['angle', 'triangle', 'circle', 'area', 'volume'],
        'trigonometry': ['sin', 'cos', 'tan', 'angle', 'radian'],
    }

    def __init__(
        self,
        agent_id: str = 'knowledge_graph_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        db_path: str = None
    ):
        """
        Initialize Knowledge Graph Specialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
            db_path: Path to SQLite database
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Set default database path
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                '..', '..', '..', '..', '..',
                'data', 'symbo_llm', 'knowledge_graph.db'
            )
        self.db_path = os.path.abspath(db_path)

        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        # Statistics
        self.nodes_added = 0
        self.edges_added = 0
        self.queries_performed = 0

        # BDI state
        self.beliefs: Dict[str, Any] = {
            'graph_density': 0.0,
            'orphan_nodes': 0,
            'maintenance_needed': False
        }

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Knowledge Graph initialized at {self.db_path}")

    def _register_services(self) -> None:
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            agent_id=self.agent_id,
            service_type='learning.knowledge_graph',
            description='Graph-structured mathematical knowledge management',
            capabilities=['add_node', 'query_related', 'find_similar', 'analyze']
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered with DF")

    def _init_database(self) -> None:
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript('''
                -- Knowledge nodes
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    problem_text TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    domain TEXT DEFAULT 'unknown',
                    complexity REAL DEFAULT 0.5,
                    embedding BLOB,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed DATETIME
                );

                -- Relationship edges
                CREATE TABLE IF NOT EXISTS edges (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (source_id, target_id, relationship),
                    FOREIGN KEY (source_id) REFERENCES nodes(id),
                    FOREIGN KEY (target_id) REFERENCES nodes(id)
                );

                -- Indexes for fast queries
                CREATE INDEX IF NOT EXISTS idx_nodes_domain ON nodes(domain);
                CREATE INDEX IF NOT EXISTS idx_nodes_complexity ON nodes(complexity);
                CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
                CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
                CREATE INDEX IF NOT EXISTS idx_edges_relationship ON edges(relationship);
            ''')
            conn.commit()
        finally:
            conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_node(
        self,
        problem: str,
        answer: str,
        domain: str = 'unknown',
        complexity: float = 0.5,
        embedding: List[float] = None,
        auto_link: bool = True
    ) -> Dict[str, Any]:
        """
        Add a knowledge node to the graph.

        Args:
            problem: The problem text
            answer: The solution
            domain: Problem domain
            complexity: Complexity score (0.0-1.0)
            embedding: Optional vector embedding
            auto_link: Whether to automatically infer relationships

        Returns:
            Result with node_id and edges_created
        """
        # Generate node ID
        node_id = self._generate_id(problem)

        # Serialize embedding if provided
        embedding_blob = None
        if embedding:
            import struct
            embedding_blob = struct.pack(f'{len(embedding)}f', *embedding)

        conn = self._get_connection()
        try:
            # Insert or update node
            conn.execute('''
                INSERT OR REPLACE INTO nodes
                (id, problem_text, answer, domain, complexity, embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (node_id, problem, answer, domain, complexity, embedding_blob))

            conn.commit()
            self.nodes_added += 1

            # Auto-link to related nodes
            edges_created = 0
            if auto_link:
                edges_created = self._infer_and_create_edges(conn, node_id, problem, domain)

            conn.commit()

            return {
                'node_id': node_id,
                'edges_created': edges_created,
                'domain': domain,
                'complexity': complexity
            }

        finally:
            conn.close()

    def _generate_id(self, text: str) -> str:
        """Generate a unique ID for a text."""
        # Use MD5 hash for consistent ID generation
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def _infer_and_create_edges(
        self,
        conn: sqlite3.Connection,
        node_id: str,
        problem: str,
        domain: str
    ) -> int:
        """Infer and create relationship edges."""
        edges_created = 0

        # Find similar nodes to link
        similar_nodes = self._find_similar_nodes(conn, problem, domain, exclude_id=node_id)

        for similar in similar_nodes[:10]:  # Limit to 10 relationships
            relationship = self._infer_relationship(problem, similar['problem_text'])

            if relationship:
                try:
                    conn.execute('''
                        INSERT OR IGNORE INTO edges
                        (source_id, target_id, relationship, weight, created_at)
                        VALUES (?, ?, ?, ?, datetime('now'))
                    ''', (node_id, similar['id'], relationship, 1.0))
                    edges_created += 1
                    self.edges_added += 1
                except Exception as e:
                    logger.debug(f"Edge creation skipped: {e}")

        return edges_created

    def _find_similar_nodes(
        self,
        conn: sqlite3.Connection,
        problem: str,
        domain: str,
        exclude_id: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """Find similar nodes based on domain and text similarity."""
        # Start with domain match
        query = 'SELECT * FROM nodes WHERE domain = ?'
        params = [domain]

        if exclude_id:
            query += ' AND id != ?'
            params.append(exclude_id)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]

        # Sort by text similarity
        problem_words = set(problem.lower().split())
        for result in results:
            other_words = set(result['problem_text'].lower().split())
            overlap = len(problem_words & other_words)
            total = len(problem_words | other_words)
            result['similarity'] = overlap / total if total > 0 else 0

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results

    def _infer_relationship(self, problem1: str, problem2: str) -> Optional[str]:
        """Infer relationship between two problems."""
        p1_lower = problem1.lower()
        p2_lower = problem2.lower()

        # Check for generalization/specialization (containment)
        if len(p1_lower) < len(p2_lower) and p1_lower in p2_lower:
            return RelationshipType.GENERALIZES.value
        if len(p2_lower) < len(p1_lower) and p2_lower in p1_lower:
            return RelationshipType.SPECIALIZES.value

        # Check for inverse functions
        for func1, func2 in self.INVERSE_PAIRS:
            if func1 in p1_lower and func2 in p2_lower:
                return RelationshipType.INVERSE_OF.value
            if func2 in p1_lower and func1 in p2_lower:
                return RelationshipType.INVERSE_OF.value

        # Check for similar structure
        p1_words = set(p1_lower.split())
        p2_words = set(p2_lower.split())
        overlap = len(p1_words & p2_words)
        total = len(p1_words | p2_words)
        similarity = overlap / total if total > 0 else 0

        if similarity > 0.5:
            return RelationshipType.SIMILAR_TO.value

        # Check for topic relationships
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            p1_has = any(kw in p1_lower for kw in keywords)
            p2_has = any(kw in p2_lower for kw in keywords)
            if p1_has and p2_has:
                return RelationshipType.SIMILAR_TO.value

        return None

    def query_related(
        self,
        problem: str,
        relationship: str = None,
        max_depth: int = 2,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Find related knowledge via graph traversal.

        Args:
            problem: The problem to find relations for
            relationship: Optional filter by relationship type
            max_depth: Maximum traversal depth
            limit: Maximum results

        Returns:
            Related nodes with paths
        """
        self.queries_performed += 1

        node_id = self._generate_id(problem)

        conn = self._get_connection()
        try:
            # Check if node exists
            cursor = conn.execute('SELECT * FROM nodes WHERE id = ?', (node_id,))
            source_node = cursor.fetchone()

            if not source_node:
                # Try fuzzy match
                return self._fuzzy_query_related(conn, problem, limit)

            # BFS traversal
            visited = {node_id}
            current_level = [node_id]
            results = []

            for depth in range(max_depth):
                next_level = []

                for current_id in current_level:
                    # Get outgoing edges
                    query = 'SELECT * FROM edges WHERE source_id = ?'
                    params = [current_id]

                    if relationship:
                        query += ' AND relationship = ?'
                        params.append(relationship)

                    cursor = conn.execute(query, params)

                    for edge in cursor.fetchall():
                        target_id = edge['target_id']
                        if target_id not in visited:
                            visited.add(target_id)
                            next_level.append(target_id)

                            # Get target node
                            node_cursor = conn.execute(
                                'SELECT * FROM nodes WHERE id = ?',
                                (target_id,)
                            )
                            target_node = node_cursor.fetchone()

                            if target_node:
                                results.append({
                                    'node_id': target_id,
                                    'problem': target_node['problem_text'],
                                    'answer': target_node['answer'],
                                    'domain': target_node['domain'],
                                    'relationship': edge['relationship'],
                                    'depth': depth + 1,
                                    'weight': edge['weight']
                                })

                current_level = next_level

                if len(results) >= limit:
                    break

            return {
                'source': problem,
                'source_id': node_id,
                'related': results[:limit],
                'total_found': len(results)
            }

        finally:
            conn.close()

    def _fuzzy_query_related(
        self,
        conn: sqlite3.Connection,
        problem: str,
        limit: int
    ) -> Dict[str, Any]:
        """Find related nodes using fuzzy matching."""
        # Find similar nodes by text
        cursor = conn.execute('SELECT * FROM nodes LIMIT 1000')
        all_nodes = cursor.fetchall()

        problem_words = set(problem.lower().split())
        scored_nodes = []

        for node in all_nodes:
            node_words = set(node['problem_text'].lower().split())
            overlap = len(problem_words & node_words)
            if overlap > 0:
                scored_nodes.append({
                    'node_id': node['id'],
                    'problem': node['problem_text'],
                    'answer': node['answer'],
                    'domain': node['domain'],
                    'similarity': overlap / len(problem_words | node_words)
                })

        scored_nodes.sort(key=lambda x: x['similarity'], reverse=True)

        return {
            'source': problem,
            'source_id': None,
            'related': scored_nodes[:limit],
            'total_found': len(scored_nodes),
            'note': 'Fuzzy matching used - exact node not found'
        }

    def find_similar(
        self,
        problem: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar problems by text similarity.

        Args:
            problem: Problem to find similar to
            top_k: Number of results

        Returns:
            List of similar problems
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute('SELECT * FROM nodes')
            all_nodes = cursor.fetchall()

            problem_words = set(problem.lower().split())
            results = []

            for node in all_nodes:
                node_words = set(node['problem_text'].lower().split())
                overlap = len(problem_words & node_words)
                total = len(problem_words | node_words)
                similarity = overlap / total if total > 0 else 0

                if similarity > 0.1:  # Minimum threshold
                    results.append({
                        'node_id': node['id'],
                        'problem': node['problem_text'],
                        'answer': node['answer'],
                        'domain': node['domain'],
                        'complexity': node['complexity'],
                        'similarity': similarity
                    })

            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]

        finally:
            conn.close()

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        conn = self._get_connection()
        try:
            # Node count
            cursor = conn.execute('SELECT COUNT(*) as count FROM nodes')
            node_count = cursor.fetchone()['count']

            # Edge count
            cursor = conn.execute('SELECT COUNT(*) as count FROM edges')
            edge_count = cursor.fetchone()['count']

            # Domain distribution
            cursor = conn.execute('''
                SELECT domain, COUNT(*) as count
                FROM nodes GROUP BY domain ORDER BY count DESC
            ''')
            domain_dist = {row['domain']: row['count'] for row in cursor.fetchall()}

            # Relationship distribution
            cursor = conn.execute('''
                SELECT relationship, COUNT(*) as count
                FROM edges GROUP BY relationship ORDER BY count DESC
            ''')
            rel_dist = {row['relationship']: row['count'] for row in cursor.fetchall()}

            # Orphan nodes (no edges)
            cursor = conn.execute('''
                SELECT COUNT(*) as count FROM nodes n
                WHERE NOT EXISTS (SELECT 1 FROM edges e WHERE e.source_id = n.id OR e.target_id = n.id)
            ''')
            orphan_count = cursor.fetchone()['count']

            # Graph density
            max_edges = node_count * (node_count - 1) if node_count > 1 else 1
            density = edge_count / max_edges if max_edges > 0 else 0

            return {
                'node_count': node_count,
                'edge_count': edge_count,
                'domain_distribution': domain_dist,
                'relationship_distribution': rel_dist,
                'orphan_nodes': orphan_count,
                'graph_density': density,
                'avg_edges_per_node': edge_count / node_count if node_count > 0 else 0,
                'queries_performed': self.queries_performed,
                'nodes_added': self.nodes_added,
                'edges_added': self.edges_added
            }

        finally:
            conn.close()

    def analyze_graph(self) -> Dict[str, Any]:
        """
        Analyze graph structure and generate insights.

        Returns:
            Analysis with recommendations
        """
        stats = self.get_graph_stats()

        recommendations = []

        # Check for sparse graph
        if stats['graph_density'] < 0.01 and stats['node_count'] > 100:
            recommendations.append(
                "Graph is very sparse. Consider running relationship inference "
                "on existing nodes to discover more connections."
            )

        # Check for orphan nodes
        orphan_pct = stats['orphan_nodes'] / stats['node_count'] if stats['node_count'] > 0 else 0
        if orphan_pct > 0.5:
            recommendations.append(
                f"{orphan_pct:.1%} of nodes have no relationships. "
                "Consider linking isolated nodes to improve knowledge connectivity."
            )

        # Check domain balance
        if stats['domain_distribution']:
            domains = list(stats['domain_distribution'].values())
            if max(domains) > 10 * min(domains) if min(domains) > 0 else True:
                recommendations.append(
                    "Domain distribution is imbalanced. Some domains have "
                    "significantly more coverage than others."
                )

        # Check relationship diversity
        if len(stats['relationship_distribution']) < 3:
            recommendations.append(
                "Limited relationship types being used. Consider enriching "
                "relationship inference to capture more connection types."
            )

        return {
            'stats': stats,
            'health_score': self._calculate_health_score(stats),
            'recommendations': recommendations
        }

    def _calculate_health_score(self, stats: Dict) -> float:
        """Calculate overall graph health score (0-1)."""
        scores = []

        # Density score (higher is better, but not too high)
        density = min(stats['graph_density'] * 100, 1.0)
        scores.append(density)

        # Orphan penalty
        orphan_pct = stats['orphan_nodes'] / stats['node_count'] if stats['node_count'] > 0 else 1
        scores.append(1.0 - orphan_pct)

        # Relationship diversity
        rel_types = len(stats['relationship_distribution'])
        rel_score = min(rel_types / 5, 1.0)  # 5+ types is good
        scores.append(rel_score)

        # Domain diversity
        domain_count = len(stats['domain_distribution'])
        domain_score = min(domain_count / 10, 1.0)  # 10+ domains is good
        scores.append(domain_score)

        return sum(scores) / len(scores) if scores else 0.0

    def get_stats(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        return self.get_graph_stats()

    # BDI Agent methods
    def update_beliefs(self, percept: Dict[str, Any] = None) -> None:
        """Update beliefs based on graph state."""
        try:
            stats = self.get_graph_stats()
            self.beliefs['graph_density'] = stats['graph_density']
            self.beliefs['orphan_nodes'] = stats['orphan_nodes']

            # Check if maintenance needed
            orphan_pct = stats['orphan_nodes'] / stats['node_count'] if stats['node_count'] > 0 else 0
            self.beliefs['maintenance_needed'] = orphan_pct > 0.3 or stats['graph_density'] < 0.001
        except Exception as e:
            logger.error(f"Error updating beliefs: {e}")

    def deliberate(self) -> Optional[Intention]:
        """Deliberate on current beliefs."""
        if self.beliefs.get('maintenance_needed', False):
            return Intention(
                plan_id='graph_maintenance',
                steps=['analyze_orphans', 'infer_relationships', 'validate'],
                target_desire='connected_graph'
            )
        return None

    def execute_step(self) -> bool:
        """Execute one step of agent processing."""
        if self.blackboard:
            # Would check for pending graph tasks
            pass
        return False

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the supervisor.

        Args:
            task_entry: Task with 'action' and relevant data

        Returns:
            Processing result
        """
        action = task_entry.get('action', 'get_stats')

        if action == 'add':
            return self.add_node(
                problem=task_entry.get('problem', ''),
                answer=task_entry.get('answer', ''),
                domain=task_entry.get('domain', 'unknown'),
                complexity=task_entry.get('complexity', 0.5),
                embedding=task_entry.get('embedding'),
                auto_link=task_entry.get('auto_link', True)
            )

        elif action == 'query_related':
            return self.query_related(
                problem=task_entry.get('problem', ''),
                relationship=task_entry.get('relationship'),
                max_depth=task_entry.get('max_depth', 2),
                limit=task_entry.get('limit', 10)
            )

        elif action == 'find_similar':
            return {
                'similar': self.find_similar(
                    problem=task_entry.get('problem', ''),
                    top_k=task_entry.get('top_k', 5)
                )
            }

        elif action == 'get_stats':
            return self.get_graph_stats()

        elif action == 'analyze':
            return self.analyze_graph()

        else:
            return {'error': f'Unknown action: {action}'}
