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
PHASE 2 - GRAPH THEORY AGENT (Tier 3)
=====================================

Comprehensive graph algorithms implementation.
Operates on structured data representations (adjacency matrix/list).

CAPABILITIES:
- Traversal: BFS, DFS, topological sort
- Shortest paths: Dijkstra, Bellman-Ford, Floyd-Warshall
- MST: Prim's, Kruskal's algorithms
- Connectivity: SCC (Tarjan), articulation points, bridges
- Flow: Ford-Fulkerson max flow
- Properties: Cycle detection, bipartite check

NO SYMPY - All implementations are pure Python.
"""

import sys
import os
from collections import deque, defaultdict
from typing import Dict, Any, List, Optional, Set, Tuple
import heapq

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard


# =============================================================================
# NATIVE GRAPH ALGORITHMS - NO EXTERNAL DEPENDENCIES
# =============================================================================

class UnionFind:
    """Union-Find data structure for Kruskal's algorithm."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        """Find find in search space.

        Args:
        x: X

        Returns:
        Found result or None if not found

        Example:
        >>> specialist = UnionFind()
        >>> result = specialist.find(x=...)
        # Returns computed result

        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """Perform union operation.

        Args:
        x: Description neededy

        Returns:
        Result of the operation

        Example:
        >>> specialist = UnionFind()
        >>> result = specialist.union(...)
        # Returns result
        """
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


def dijkstra(graph: Dict[int, List[Tuple[int, float]]], start: int) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Dijkstra's single-source shortest path algorithm.

    Args:
        graph: Adjacency list {node: [(neighbor, weight), ...]}
        start: Starting node

    Returns:
        (distances, parents) - shortest distances and parent pointers
    """
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    parents = {start: None}
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > distances[u]:
            continue
        for v, w in graph.get(u, []):
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                parents[v] = u
                heapq.heappush(pq, (distances[v], v))

    return distances, parents


def bellman_ford(graph: Dict[int, List[Tuple[int, float]]], start: int) -> Tuple[Dict[int, float], Dict[int, Optional[int]], bool]:
    """
    Bellman-Ford shortest path algorithm (handles negative weights).

    Returns:
        (distances, parents, has_negative_cycle)
    """
    nodes = list(graph.keys())
    for neighbors in graph.values():
        for v, _ in neighbors:
            if v not in nodes:
                nodes.append(v)

    distances = {node: float('inf') for node in nodes}
    distances[start] = 0
    parents = {start: None}

    # Relax edges V-1 times
    for _ in range(len(nodes) - 1):
        for u in graph:
            for v, w in graph[u]:
                if distances[u] != float('inf') and distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w
                    parents[v] = u

    # Check for negative cycles
    has_negative_cycle = False
    for u in graph:
        for v, w in graph[u]:
            if distances[u] != float('inf') and distances[u] + w < distances[v]:
                has_negative_cycle = True
                break

    return distances, parents, has_negative_cycle


def floyd_warshall(graph: Dict[int, List[Tuple[int, float]]]) -> Dict[int, Dict[int, float]]:
    """
    Floyd-Warshall all-pairs shortest path algorithm.

    Returns:
        Dictionary of dictionaries with all pairwise distances
    """
    nodes = list(graph.keys())
    for neighbors in graph.values():
        for v, _ in neighbors:
            if v not in nodes:
                nodes.append(v)

    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    # Initialize distance matrix
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0

    for u in graph:
        for v, w in graph[u]:
            dist[node_idx[u]][node_idx[v]] = w

    # Floyd-Warshall main loop
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Convert back to node-keyed dictionary
    result = {}
    for i, u in enumerate(nodes):
        result[u] = {}
        for j, v in enumerate(nodes):
            result[u][v] = dist[i][j]

    return result


def prim_mst(graph: Dict[int, List[Tuple[int, float]]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Prim's Minimum Spanning Tree algorithm.

    Returns:
        (mst_edges, total_weight)
    """
    if not graph:
        return [], 0

    start = next(iter(graph.keys()))
    visited = {start}
    edges = []
    total_weight = 0

    # Priority queue: (weight, from_node, to_node)
    pq = [(w, start, v) for v, w in graph.get(start, [])]
    heapq.heapify(pq)

    while pq and len(visited) < len(graph):
        weight, u, v = heapq.heappop(pq)
        if v in visited:
            continue

        visited.add(v)
        edges.append((u, v, weight))
        total_weight += weight

        for neighbor, w in graph.get(v, []):
            if neighbor not in visited:
                heapq.heappush(pq, (w, v, neighbor))

    return edges, total_weight


def kruskal_mst(graph: Dict[int, List[Tuple[int, float]]]) -> Tuple[List[Tuple[int, int, float]], float]:
    """
    Kruskal's Minimum Spanning Tree algorithm.

    Returns:
        (mst_edges, total_weight)
    """
    # Collect all edges
    all_edges = []
    nodes = set(graph.keys())
    for u in graph:
        for v, w in graph[u]:
            nodes.add(v)
            if u < v:  # Avoid duplicates for undirected graphs
                all_edges.append((w, u, v))

    all_edges.sort()

    # Create node index mapping
    node_list = list(nodes)
    node_idx = {node: i for i, node in enumerate(node_list)}
    uf = UnionFind(len(node_list))

    mst_edges = []
    total_weight = 0

    for weight, u, v in all_edges:
        if uf.union(node_idx[u], node_idx[v]):
            mst_edges.append((u, v, weight))
            total_weight += weight
            if len(mst_edges) == len(nodes) - 1:
                break

    return mst_edges, total_weight


def tarjan_scc(graph: Dict[int, List[Tuple[int, float]]]) -> List[List[int]]:
    """
    Tarjan's algorithm for strongly connected components.

    Returns:
        List of SCCs (each SCC is a list of nodes)
    """
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = {}
    sccs = []

    def strongconnect(v):
        """Perform strongconnect operation.

        Args:
        v: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.strongconnect(...)
        """
        index[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True

        for neighbor, _ in graph.get(v, []):
            if neighbor not in index:
                strongconnect(neighbor)
                lowlink[v] = min(lowlink[v], lowlink[neighbor])
            elif on_stack.get(neighbor, False):
                lowlink[v] = min(lowlink[v], index[neighbor])

        if lowlink[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in graph:
        if v not in index:
            strongconnect(v)

    return sccs


def topological_sort(graph: Dict[int, List[Tuple[int, float]]]) -> Tuple[List[int], bool]:
    """
    Kahn's algorithm for topological sort.

    Returns:
        (sorted_nodes, is_dag) - sorted order and whether graph is a DAG
    """
    # Build in-degree map
    in_degree = defaultdict(int)
    nodes = set(graph.keys())
    for u in graph:
        for v, _ in graph[u]:
            nodes.add(v)
            in_degree[v] += 1

    # Initialize queue with zero in-degree nodes
    queue = deque([v for v in nodes if in_degree[v] == 0])
    result = []

    while queue:
        u = queue.popleft()
        result.append(u)
        for v, _ in graph.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    is_dag = len(result) == len(nodes)
    return result, is_dag


def has_cycle(graph: Dict[int, List[Tuple[int, float]]], directed: bool = True) -> bool:
    """
    Detect if graph has a cycle.

    Args:
        graph: Adjacency list
        directed: Whether graph is directed

    Returns:
        True if cycle exists
    """
    if directed:
        # Use DFS with colors for directed graph
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {v: WHITE for v in graph}

        def dfs(v):
            """DFS with 3-color marking for cycle detection in directed graphs."""
            color[v] = GRAY
            for neighbor, _ in graph.get(v, []):
                if color.get(neighbor, WHITE) == GRAY:
                    return True
                if color.get(neighbor, WHITE) == WHITE and dfs(neighbor):
                    return True
            color[v] = BLACK
            return False

        for v in graph:
            if color[v] == WHITE and dfs(v):
                return True
        return False
    else:
        # Use DFS with parent tracking for undirected
        visited = set()

        def dfs(v, parent):
            """DFS with parent tracking for cycle detection in undirected graphs."""
            visited.add(v)
            for neighbor, _ in graph.get(v, []):
                if neighbor not in visited:
                    if dfs(neighbor, v):
                        return True
                elif neighbor != parent:
                    return True
            return False

        for v in graph:
            if v not in visited and dfs(v, -1):
                return True
        return False


def is_bipartite(graph: Dict[int, List[Tuple[int, float]]]) -> Tuple[bool, Dict[int, int]]:
    """
    Check if graph is bipartite using BFS coloring.

    Returns:
        (is_bipartite, coloring) - coloring maps nodes to 0 or 1
    """
    color = {}

    for start in graph:
        if start in color:
            continue

        queue = deque([start])
        color[start] = 0

        while queue:
            u = queue.popleft()
            for v, _ in graph.get(u, []):
                """Perform dfs operation.

                Args:
                u: Description needed
                parent: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.dfs(...)
                """
                if v not in color:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    return False, {}

    return True, color


def find_bridges(graph: Dict[int, List[Tuple[int, float]]]) -> List[Tuple[int, int]]:
    """
    Find all bridges (cut edges) in an undirected graph.

    Returns:
        List of bridge edges as (u, v) tuples
    """
    timer = [0]
    disc = {}
    low = {}
    bridges = []

    def dfs(u, parent):
        """Depth-first search helper for bridge detection using Tarjan's algorithm."""
        disc[u] = low[u] = timer[0]
        timer[0] += 1

        for v, _ in graph.get(u, []):
            if v not in disc:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append((u, v))
            elif v != parent:
                low[u] = min(low[u], disc[v])

    for v in graph:
        if v not in disc:
            dfs(v, -1)

    return bridges


def find_articulation_points(graph: Dict[int, List[Tuple[int, float]]]) -> List[int]:
    """
    Find all articulation points (cut vertices) in an undirected graph.

    Returns:
        List of articulation point nodes
    """
    timer = [0]
    disc = {}
    low = {}
    parent = {}
    ap = set()

    def dfs(u):
        """Depth-first search helper for articulation point detection."""
        children = 0
        disc[u] = low[u] = timer[0]
        timer[0] += 1

        for v, _ in graph.get(u, []):
            if v not in disc:
                children += 1
                parent[v] = u
                dfs(v)
                low[u] = min(low[u], low[v])

                # u is articulation point if:
                # 1. u is root and has 2+ children
                # 2. u is not root and low[v] >= disc[u]
                if parent.get(u) is None and children > 1:
                    ap.add(u)
                if parent.get(u) is not None and low[v] >= disc[u]:
                    ap.add(u)
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])

    for v in graph:
        if v not in disc:
            parent[v] = None
            dfs(v)

    return list(ap)


def ford_fulkerson_max_flow(graph: Dict[int, List[Tuple[int, float]]], source: int, sink: int) -> Tuple[float, Dict[Tuple[int, int], float]]:
    """
    Ford-Fulkerson max flow using BFS (Edmonds-Karp).

    Returns:
        (max_flow_value, flow_on_each_edge)
    """
    # Build capacity graph
    capacity = defaultdict(lambda: defaultdict(float))
    for u in graph:
        for v, cap in graph[u]:
            capacity[u][v] = cap

    flow = defaultdict(lambda: defaultdict(float))
    max_flow = 0

    def bfs():
        """Breadth-first search to find augmenting path for maximum flow (Ford-Fulkerson)."""
        parent = {source: None}
        visited = {source}
        queue = deque([source])

        while queue:
            u = queue.popleft()
            for v in capacity[u]:
                if v not in visited and capacity[u][v] - flow[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    if v == sink:
                        return parent
                    queue.append(v)
        return None

    while True:
        parent = bfs()
        if not parent:
            break

        # Find bottleneck
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, capacity[u][v] - flow[u][v])
            v = u

        # Update flow
        v = sink
        while v != source:
            u = parent[v]
            flow[u][v] += path_flow
            flow[v][u] -= path_flow
            v = u

        max_flow += path_flow

    # Convert flow to edge format
    edge_flow = {}
    for u in flow:
        for v in flow[u]:
            if flow[u][v] > 0:
                edge_flow[(u, v)] = flow[u][v]

    return max_flow, edge_flow

class GraphTheoryAgent(BDIAgent):
    """
    BDI Agent for comprehensive graph theory computations.

    Capabilities:
    - Traversal: BFS, DFS, topological sort
    - Shortest paths: Dijkstra, Bellman-Ford, Floyd-Warshall
    - MST: Prim's, Kruskal's algorithms
    - Connectivity: SCC (Tarjan), articulation points, bridges
    - Flow: Ford-Fulkerson max flow
    - Properties: Cycle detection, bipartite check
    """

    # Operation keywords for task routing
    OPERATION_KEYWORDS = {
        'dijkstra': ['dijkstra', 'shortest path', 'shortest_path'],
        'bellman_ford': ['bellman', 'negative weight', 'bellman-ford'],
        'floyd_warshall': ['floyd', 'warshall', 'all pairs', 'apsp'],
        'bfs': ['bfs', 'breadth first', 'breadth-first', 'level order'],
        'dfs': ['dfs', 'depth first', 'depth-first'],
        'mst': ['mst', 'minimum spanning', 'spanning tree', 'prim', 'kruskal'],
        'scc': ['scc', 'strongly connected', 'tarjan', 'kosaraju'],
        'topological': ['topological', 'topo sort', 'dependency order'],
        'cycle': ['cycle', 'cyclic', 'acyclic'],
        'bipartite': ['bipartite', 'two-color', 'two color', '2-color'],
        'max_flow': ['max flow', 'maximum flow', 'ford fulkerson', 'network flow'],
        'bridges': ['bridge', 'cut edge', 'cut-edge'],
        'articulation': ['articulation', 'cut vertex', 'cut point'],
    }

    def __init__(self, agent_id='graphtheory_001', df: Optional[DirectoryFacilitator] = None, blackboard: Optional[Blackboard] = None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.graphs',
                agent_id=agent_id,
                algorithm='graph_algorithms',
                cost='medium',
                instance=self,
                tier='3',
                algorithms='dijkstra_bellman_floyd_bfs_dfs_mst_scc_topological_cycle_bipartite_maxflow_bridges'))

        print(f"[{agent_id}] Graph Theory Agent initialized (enhanced)")
        print(f"  Algorithms: Dijkstra, Bellman-Ford, Floyd-Warshall, MST, SCC, Topo Sort, etc.")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for graph theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = self.blackboard.query_entries(tags=['graph'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['shortest_path'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['bfs'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['dfs'], status=EntryStatus.PENDING)
            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata and task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                    tasks.append(task)
            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create graph algorithm computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()

            # Determine operation using keyword matching
            operation = self._detect_operation(raw_input)

            steps = ['claim_task', 'parse_graph', f'compute_{operation}', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'graph_{operation}_{task_id}',
                steps=steps,
                target_desire='graph_algorithm',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def _detect_operation(self, raw_input: str) -> str:
        """Detect the graph algorithm operation from input text."""
        raw_lower = raw_input.lower()

        # Check each operation type by keywords (order matters for specificity)
        priority_order = [
            'bellman_ford', 'floyd_warshall', 'mst', 'scc', 'topological',
            'articulation', 'bridges', 'bipartite', 'cycle', 'max_flow',
            'bfs', 'dfs', 'dijkstra'
        ]

        for op in priority_order:
            for keyword in self.OPERATION_KEYWORDS.get(op, []):
                if keyword in raw_lower:
                    return op

        # Default to dijkstra
        return 'dijkstra'

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform graph algorithms (native implementations)."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_graph':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                # Parse adjacency list: {node: [(neighbor, weight), ...]}
                graph = metadata.get('graph', {0: [(1, 1), (2, 4)], 1: [(2, 2), (3, 5)], 2: [(3, 1)], 3: []})
                start = metadata.get('start', 0)
                end = metadata.get('end', 3)
                intention.metadata['graph'] = graph
                intention.metadata['start'] = start
                intention.metadata['end'] = end
                intention.advance()

            elif action == 'compute_dijkstra':
                graph = intention.metadata.get('graph')
                start = intention.metadata.get('start')
                end = intention.metadata.get('end')
                distances, parents = dijkstra(graph, start)
                # Reconstruct path
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = parents.get(node)
                path.reverse()
                result = {
                    'shortest_distance': distances.get(end, float('inf')),
                    'path': path,
                    'all_distances': distances
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_bellman_ford':
                graph = intention.metadata.get('graph')
                start = intention.metadata.get('start')
                end = intention.metadata.get('end')
                distances, parents, has_neg_cycle = bellman_ford(graph, start)
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = parents.get(node)
                path.reverse()
                result = {
                    'shortest_distance': distances.get(end, float('inf')),
                    'path': path,
                    'has_negative_cycle': has_neg_cycle,
                    'all_distances': distances
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_floyd_warshall':
                graph = intention.metadata.get('graph')
                all_pairs = floyd_warshall(graph)
                result = {'all_pairs_distances': all_pairs}
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_bfs':
                graph = intention.metadata.get('graph')
                start = intention.metadata.get('start')
                end = intention.metadata.get('end')
                visited = set()
                queue = deque([(start, [start])])
                visited.add(start)
                result_path = None
                while queue:
                    node, path = queue.popleft()
                    if node == end:
                        result_path = path
                        break
                    for neighbor, _ in graph.get(node, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [neighbor]))
                result = {'path': result_path, 'visited_order': list(visited)}
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_dfs':
                graph = intention.metadata.get('graph')
                start = intention.metadata.get('start')
                visited = []

                def dfs(node):
                    """Perform dfs operation.

                    Args:
                    node: Description needed

                    Returns:
                    Result of the operation

                    Example:
                    >>> result = obj.dfs(...)
                    """
                    if node in visited:
                        return
                    visited.append(node)
                    for neighbor, _ in graph.get(node, []):
                        dfs(neighbor)

                dfs(start)
                result = {'traversal_order': visited}
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_mst':
                graph = intention.metadata.get('graph')
                raw = intention.metadata.get('raw_input', '').lower()
                # Choose algorithm based on input
                if 'kruskal' in raw:
                    edges, weight = kruskal_mst(graph)
                    algo = 'Kruskal'
                else:
                    edges, weight = prim_mst(graph)
                    algo = 'Prim'
                result = {
                    'mst_edges': edges,
                    'total_weight': weight,
                    'algorithm': algo
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_scc':
                graph = intention.metadata.get('graph')
                sccs = tarjan_scc(graph)
                result = {
                    'strongly_connected_components': sccs,
                    'num_components': len(sccs)
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_topological':
                graph = intention.metadata.get('graph')
                sorted_nodes, is_dag = topological_sort(graph)
                result = {
                    'topological_order': sorted_nodes,
                    'is_dag': is_dag
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_cycle':
                graph = intention.metadata.get('graph')
                raw = intention.metadata.get('raw_input', '').lower()
                directed = 'undirected' not in raw
                cycle_exists = has_cycle(graph, directed=directed)
                result = {
                    'has_cycle': cycle_exists,
                    'graph_type': 'directed' if directed else 'undirected'
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_bipartite':
                graph = intention.metadata.get('graph')
                is_bip, coloring = is_bipartite(graph)
                result = {
                    'is_bipartite': is_bip,
                    'coloring': coloring if is_bip else None
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_max_flow':
                graph = intention.metadata.get('graph')
                start = intention.metadata.get('start')
                end = intention.metadata.get('end')
                max_flow_val, edge_flows = ford_fulkerson_max_flow(graph, start, end)
                result = {
                    'max_flow': max_flow_val,
                    'edge_flows': edge_flows
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_bridges':
                graph = intention.metadata.get('graph')
                bridge_edges = find_bridges(graph)
                result = {
                    'bridges': bridge_edges,
                    'num_bridges': len(bridge_edges)
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'compute_articulation':
                graph = intention.metadata.get('graph')
                ap_nodes = find_articulation_points(graph)
                result = {
                    'articulation_points': ap_nodes,
                    'num_articulation_points': len(ap_nodes)
                }
                intention.metadata['result'] = result
                intention.advance()

            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(
                        EntryType.PARTIAL_RESULT,
                        create_variable(str(result)),
                        self.agent_id,
                        task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        ['graph', 'result', task_id],
                        EntryStatus.COMPLETED,
                        {'result': str(result), 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = GraphTheoryAgent()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed})
        return stats
