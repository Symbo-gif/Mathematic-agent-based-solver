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
MAPPER SPECIALIST (Tier 3)
===========================

Implements Mapper algorithm for topological data analysis.

CAPABILITIES:
-------------
- Mapper graph construction
- Filter function application
- Open cover construction
- Clustering in preimages
- Nerve complex computation
- Graph structure analysis

ALGORITHMS:
-----------
- Mapper algorithm (Singh, Memoli, Carlsson)
- Hierarchical clustering
- Single-linkage clustering
- Cover nerve construction

NO SYMPY - Pure Python/NumPy implementation.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field
from collections import defaultdict

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

logger = logging.getLogger('symbo_agentic_reasoners.specialists.mapper')


@dataclass
class MapperNode:
    """Node in Mapper graph."""
    node_id: int
    points: Set[int]
    cover_set: int
    centroid: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MapperEdge:
    """Edge in Mapper graph."""
    node1: int
    node2: int
    weight: float = 1.0
    shared_points: Set[int] = field(default_factory=set)


@dataclass
class MapperGraph:
    """
    Mapper graph representation.

    Attributes:
        nodes: Dictionary mapping node_id -> MapperNode
        edges: List of edges
        metadata: Additional information
    """
    nodes: Dict[int, MapperNode] = field(default_factory=dict)
    edges: List[MapperEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: MapperNode):
        """Add node to graph."""
        self.nodes[node.node_id] = node

    def add_edge(self, edge: MapperEdge):
        """Add edge to graph."""
        self.edges.append(edge)

    def get_neighbors(self, node_id: int) -> List[int]:
        """Get neighbor node IDs."""
        neighbors = []
        for edge in self.edges:
            if edge.node1 == node_id:
                neighbors.append(edge.node2)
            elif edge.node2 == node_id:
                neighbors.append(edge.node1)
        return neighbors

    def num_nodes(self) -> int:
        """Get number of nodes."""
        return len(self.nodes)

    def num_edges(self) -> int:
        """Get number of edges."""
        return len(self.edges)


class MapperSpecialist(BDIAgent):
    """
    BDI Agent for Mapper algorithm implementation.

    Implements topological visualization via Mapper construction.
    """

    def __init__(self, agent_id='mapper_specialist_001', df=None, blackboard=None):
        """
        Initialize MapperSpecialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.mapper_cache = {}
        self._epsilon = 1e-10

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.tda.mapper',
                agent_id=self.agent_id,
                algorithm='mapper',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))
            logger.info(f"{self.agent_id} registered with DF")

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Mapper task.

        Args:
            task_entry: Task specification containing:
                - operation: Type of computation
                - point_cloud: Point cloud data
                - filter_function: Filter function or name
                - cover_params: Cover parameters

        Returns:
            Result dictionary with computation results
        """
        self.tasks_executed += 1
        operation = task_entry.get('operation', 'construct_mapper')

        try:
            if operation == 'construct_mapper' or operation == 'mapper':
                return self._handle_construct_mapper(task_entry)
            elif operation == 'construct_cover':
                return self._handle_construct_cover(task_entry)
            elif operation == 'cluster_preimages':
                return self._handle_cluster_preimages(task_entry)
            elif operation == 'build_nerve':
                return self._handle_build_nerve(task_entry)
            elif operation == 'analyze_structure':
                return self._handle_analyze_structure(task_entry)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }
        except Exception as e:
            logger.error(f"Error in {operation}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'operation': operation
            }

    def _handle_construct_mapper(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Construct Mapper graph."""
        point_cloud = np.array(task_entry.get('point_cloud', []))
        filter_function = task_entry.get('filter_function', 'coordinate_0')
        cover_params = task_entry.get('cover_params', {})

        # Apply filter function
        if isinstance(filter_function, str):
            filter_values = self._apply_filter(point_cloud, filter_function)
        else:
            filter_values = np.array([filter_function(p) for p in point_cloud])

        # Construct Mapper
        mapper_graph = self.construct_mapper_graph(
            point_cloud, filter_values, cover_params
        )

        # Analyze structure
        analysis = self.analyze_mapper_structure(mapper_graph)

        return {
            'success': True,
            'mapper_graph': mapper_graph,
            'num_nodes': mapper_graph.num_nodes(),
            'num_edges': mapper_graph.num_edges(),
            'analysis': analysis
        }

    def _handle_construct_cover(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Construct open cover."""
        filter_values = np.array(task_entry.get('filter_values', []))
        n_intervals = task_entry.get('n_intervals', 10)
        overlap = task_entry.get('overlap', 0.3)

        cover = self.construct_cover(filter_values, n_intervals, overlap)

        return {
            'success': True,
            'cover': cover,
            'num_sets': len(cover)
        }

    def _handle_cluster_preimages(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Cluster points in cover set preimage."""
        point_cloud = np.array(task_entry.get('point_cloud', []))
        cover_set = task_entry.get('cover_set', set())

        clusters = self.cluster_preimages(point_cloud, cover_set)

        return {
            'success': True,
            'clusters': clusters,
            'num_clusters': len(clusters)
        }

    def _handle_build_nerve(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Build nerve complex."""
        clusters = task_entry.get('clusters', [])

        nerve = self.build_nerve_complex(clusters)

        return {
            'success': True,
            'nerve': nerve,
            'num_nodes': nerve.num_nodes(),
            'num_edges': nerve.num_edges()
        }

    def _handle_analyze_structure(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Mapper graph structure."""
        mapper_graph = task_entry.get('mapper_graph')

        if mapper_graph is None:
            return {'success': False, 'error': 'No mapper graph provided'}

        analysis = self.analyze_mapper_structure(mapper_graph)

        return {
            'success': True,
            'analysis': analysis
        }

    # Core algorithms

    def construct_mapper_graph(
        self,
        point_cloud: np.ndarray,
        filter_values: np.ndarray,
        cover_params: Dict[str, Any]
    ) -> MapperGraph:
        """
        Construct Mapper graph from point cloud.

        Main Mapper algorithm:
        1. Apply filter function f: X → R
        2. Construct cover of range(f)
        3. Cluster points in each preimage
        4. Build nerve of resulting cover

        Args:
            point_cloud: Data points (n_points, n_features)
            filter_values: Filter function values for each point
            cover_params: Parameters for cover construction

        Returns:
            Mapper graph
        """
        n_intervals = cover_params.get('n_intervals', 10)
        overlap = cover_params.get('overlap', 0.3)
        clustering_method = cover_params.get('clustering', 'single_linkage')

        # Step 1: Construct cover of filter range
        cover = self.construct_cover(filter_values, n_intervals, overlap)

        # Step 2: Cluster points in each cover set preimage
        all_clusters = []
        node_id = 0

        for i, cover_set in enumerate(cover):
            # Get points in this cover set
            points_in_set = list(cover_set)
            if not points_in_set:
                continue

            # Cluster these points
            clusters = self.cluster_preimages(
                point_cloud[points_in_set],
                set(range(len(points_in_set))),
                method=clustering_method
            )

            # Create nodes for each cluster
            for cluster in clusters:
                # Map back to original indices
                original_indices = {points_in_set[j] for j in cluster}

                node = MapperNode(
                    node_id=node_id,
                    points=original_indices,
                    cover_set=i,
                    centroid=np.mean(point_cloud[list(original_indices)], axis=0)
                )
                all_clusters.append(node)
                node_id += 1

        # Step 3: Build nerve (connect overlapping clusters)
        mapper_graph = self.build_nerve_complex(all_clusters)

        return mapper_graph

    def construct_cover(
        self,
        filter_values: np.ndarray,
        n_intervals: int,
        overlap: float
    ) -> List[Set[int]]:
        """
        Construct open cover of filter range.

        Creates overlapping intervals covering [min, max] of filter values.

        Args:
            filter_values: Filter function values
            n_intervals: Number of intervals
            overlap: Overlap percentage (0 to 1)

        Returns:
            List of sets (each set contains point indices in that interval)
        """
        min_val = np.min(filter_values)
        max_val = np.max(filter_values)

        if min_val == max_val:
            # Degenerate case: all points have same filter value
            return [set(range(len(filter_values)))]

        # Compute interval parameters
        interval_length = (max_val - min_val) / (n_intervals - (n_intervals - 1) * overlap)
        step = interval_length * (1 - overlap)

        cover = []

        for i in range(n_intervals):
            # Interval bounds
            left = min_val + i * step
            right = left + interval_length

            # Find points in this interval
            points = set(np.where((filter_values >= left) & (filter_values <= right))[0])

            if points:
                cover.append(points)

        return cover

    def cluster_preimages(
        self,
        point_cloud: np.ndarray,
        cover_set: Set[int],
        method: str = 'single_linkage'
    ) -> List[Set[int]]:
        """
        Cluster points in a cover set preimage.

        Args:
            point_cloud: Point cloud (full or subset)
            cover_set: Set of point indices to cluster
            method: Clustering method ('single_linkage', 'complete_linkage')

        Returns:
            List of clusters (each cluster is a set of point indices)
        """
        if not cover_set:
            return []

        points = list(cover_set)
        if len(points) == 1:
            return [cover_set]

        # Compute distance matrix for points in cover set
        distances = self._compute_distance_matrix(point_cloud[points])

        # Hierarchical clustering
        if method == 'single_linkage':
            clusters = self._single_linkage_clustering(distances, points)
        else:
            clusters = self._single_linkage_clustering(distances, points)

        return clusters

    def build_nerve_complex(self, clusters: List[MapperNode]) -> MapperGraph:
        """
        Build nerve of cluster covering.

        Two clusters are connected if they share points.

        Args:
            clusters: List of cluster nodes

        Returns:
            Mapper graph (nerve of clustering)
        """
        mapper_graph = MapperGraph()

        # Add nodes
        for cluster in clusters:
            mapper_graph.add_node(cluster)

        # Add edges for overlapping clusters
        for i, cluster1 in enumerate(clusters):
            for j in range(i + 1, len(clusters)):
                cluster2 = clusters[j]

                # Check for overlap
                shared = cluster1.points & cluster2.points

                if shared:
                    edge = MapperEdge(
                        node1=cluster1.node_id,
                        node2=cluster2.node_id,
                        weight=len(shared),
                        shared_points=shared
                    )
                    mapper_graph.add_edge(edge)

        return mapper_graph

    def analyze_mapper_structure(self, mapper_graph: MapperGraph) -> Dict[str, Any]:
        """
        Analyze topological structure of Mapper graph.

        Computes:
        - Connected components
        - Loops/cycles
        - Branching points
        - Flare detection

        Args:
            mapper_graph: Mapper graph

        Returns:
            Analysis dictionary
        """
        # Compute connected components
        components = self._find_connected_components(mapper_graph)

        # Compute node degrees
        degrees = defaultdict(int)
        for edge in mapper_graph.edges:
            degrees[edge.node1] += 1
            degrees[edge.node2] += 1

        # Find special structures
        branching_points = [n for n, d in degrees.items() if d >= 3]
        leaf_nodes = [n for n, d in degrees.items() if d == 1]

        # Estimate loops (simple cycle detection)
        num_loops = self._count_simple_cycles(mapper_graph)

        return {
            'num_components': len(components),
            'component_sizes': [len(c) for c in components],
            'num_branching_points': len(branching_points),
            'num_leaf_nodes': len(leaf_nodes),
            'estimated_loops': num_loops,
            'avg_degree': np.mean(list(degrees.values())) if degrees else 0,
            'max_degree': max(degrees.values()) if degrees else 0
        }

    # Utility methods

    def _apply_filter(self, point_cloud: np.ndarray, filter_name: str) -> np.ndarray:
        """
        Apply named filter function.

        Args:
            point_cloud: Point cloud
            filter_name: Name of filter function

        Returns:
            Filter values
        """
        if filter_name == 'coordinate_0':
            return point_cloud[:, 0]
        elif filter_name == 'coordinate_1':
            return point_cloud[:, 1] if point_cloud.shape[1] > 1 else point_cloud[:, 0]
        elif filter_name == 'norm':
            return np.linalg.norm(point_cloud, axis=1)
        elif filter_name == 'density':
            # Estimate local density (number of neighbors within radius)
            distances = self._compute_distance_matrix(point_cloud)
            radius = np.median(distances[distances > 0])
            density = np.sum(distances < radius, axis=1)
            return density.astype(float)
        else:
            # Default: first coordinate
            return point_cloud[:, 0]

    def _compute_distance_matrix(self, points: np.ndarray) -> np.ndarray:
        """Compute pairwise Euclidean distance matrix."""
        n = len(points)
        distances = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(points[i] - points[j])
                distances[i, j] = dist
                distances[j, i] = dist

        return distances

    def _single_linkage_clustering(
        self,
        distances: np.ndarray,
        points: List[int],
        threshold: Optional[float] = None
    ) -> List[Set[int]]:
        """
        Single-linkage hierarchical clustering.

        Args:
            distances: Distance matrix
            points: Point indices
            threshold: Distance threshold (None for auto)

        Returns:
            List of clusters
        """
        n = len(points)

        if threshold is None:
            # Auto threshold: use median distance
            threshold = np.median(distances[distances > 0]) if n > 1 else 1.0

        # Union-Find for connected components
        parent = list(range(n))

        def find(x):
            """Union-Find find with path compression."""
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            """Union-Find union operation."""
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # Connect points within threshold
        for i in range(n):
            for j in range(i + 1, n):
                if distances[i, j] <= threshold:
                    union(i, j)

        # Extract clusters
        clusters_dict = defaultdict(set)
        for i in range(n):
            root = find(i)
            clusters_dict[root].add(i)

        return list(clusters_dict.values())

    def _find_connected_components(self, mapper_graph: MapperGraph) -> List[Set[int]]:
        """Find connected components in graph."""
        visited = set()
        components = []

        def dfs(node_id, component):
            """Depth-first search to find connected components."""
            if node_id in visited:
                return
            visited.add(node_id)
            component.add(node_id)

            for neighbor in mapper_graph.get_neighbors(node_id):
                dfs(neighbor, component)

        for node_id in mapper_graph.nodes:
            if node_id not in visited:
                component = set()
                dfs(node_id, component)
                components.append(component)

        return components

    def _count_simple_cycles(self, mapper_graph: MapperGraph) -> int:
        """
        Estimate number of simple cycles.

        Uses Euler characteristic approximation: χ = V - E + F
        For planar graph: F = E - V + 2
        Number of loops ≈ E - V + 1 (for connected graph)
        """
        V = mapper_graph.num_nodes()
        E = mapper_graph.num_edges()

        if V == 0:
            return 0

        # Estimate: cycles ≈ E - V + #components
        components = self._find_connected_components(mapper_graph)
        return max(0, E - V + len(components))

    # BDI Agent methods

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard:
            pass

    def deliberate(self) -> List[str]:
        """Generate goals based on beliefs."""
        return []

    def execute_step(self, step: int):
        """Execute one reasoning step."""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        stats['cache_size'] = len(self.mapper_cache)
        return stats
