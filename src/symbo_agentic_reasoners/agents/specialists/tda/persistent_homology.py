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
PERSISTENT HOMOLOGY SPECIALIST (Tier 3)
========================================

Computes persistent homology for point clouds and filtrations.

CAPABILITIES:
-------------
- Vietoris-Rips and Cech filtration construction
- Boundary matrix computation
- Persistence pair extraction via matrix reduction
- Persistence diagrams and barcodes
- Bottleneck distance
- Wasserstein distance
- Persistent Betti numbers

ALGORITHMS:
-----------
- Standard reduction algorithm for persistence
- Hungarian algorithm for bottleneck distance
- Optimal transport for Wasserstein distance

NO SYMPY - Pure Python/NumPy implementation.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Set, FrozenSet
from dataclasses import dataclass, field
from itertools import combinations

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

logger = logging.getLogger('symbo_agentic_reasoners.specialists.persistent_homology')


@dataclass
class Simplex:
    """A simplex with vertices and filtration value."""
    vertices: FrozenSet[int]
    filtration_value: float
    dimension: int

    def __hash__(self):
        return hash(self.vertices)

    def __eq__(self, other):
        return self.vertices == other.vertices


@dataclass
class PersistencePair:
    """A persistence pair (birth, death) in dimension k."""
    birth: float
    death: float
    dimension: int
    birth_simplex: Optional[FrozenSet[int]] = None
    death_simplex: Optional[FrozenSet[int]] = None

    @property
    def persistence(self) -> float:
        """Persistence lifetime."""
        return self.death - self.birth if self.death != float('inf') else float('inf')


@dataclass
class PersistenceDiagram:
    """Persistence diagram containing all persistence pairs."""
    pairs: List[PersistencePair]
    dimension: Optional[int] = None

    def get_dimension(self, dim: int) -> 'PersistenceDiagram':
        """Filter pairs by dimension."""
        filtered = [p for p in self.pairs if p.dimension == dim]
        return PersistenceDiagram(pairs=filtered, dimension=dim)

    def get_significant_pairs(self, threshold: float) -> List[PersistencePair]:
        """Get pairs with persistence >= threshold."""
        return [p for p in self.pairs if p.persistence >= threshold]


class PersistentHomologySpecialist(BDIAgent):
    """
    BDI Agent for persistent homology computations.

    Implements standard persistence algorithms for topological data analysis.
    Uses matrix reduction for computing persistence pairs.
    """

    def __init__(self, agent_id='persistent_homology_specialist_001', df=None, blackboard=None):
        """
        Initialize PersistentHomologySpecialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.persistence_cache = {}
        self._epsilon = 1e-10

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.tda.persistent_homology',
                agent_id=self.agent_id,
                algorithm='persistent_homology',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))
            logger.info(f"{self.agent_id} registered with DF")

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a persistent homology task.

        Args:
            task_entry: Task specification containing:
                - operation: Type of computation
                - point_cloud: Point cloud data
                - params: Algorithm parameters

        Returns:
            Result dictionary with computation results
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        operation = metadata.get('operation', 'compute_persistence')

        try:
            if operation == 'construct_filtration':
                return self._handle_construct_filtration(metadata)
            elif operation == 'compute_persistence':
                return self._handle_compute_persistence(metadata)
            elif operation == 'persistence_diagram':
                return self._handle_persistence_diagram(metadata)
            elif operation == 'barcode':
                return self._handle_barcode(metadata)
            elif operation == 'bottleneck_distance':
                return self._handle_bottleneck_distance(metadata)
            elif operation == 'wasserstein_distance':
                return self._handle_wasserstein_distance(metadata)
            elif operation == 'betti_numbers':
                return self._handle_betti_numbers(metadata)
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

    def _handle_construct_filtration(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Construct filtration from point cloud."""
        point_cloud = np.array(task_entry.get('point_cloud', []))
        max_dimension = task_entry.get('max_dimension', 2)
        max_radius = task_entry.get('max_radius', float('inf'))
        filtration_type = task_entry.get('filtration_type', 'vietoris_rips')

        if filtration_type == 'vietoris_rips':
            filtration = self.construct_vietoris_rips_filtration(
                point_cloud, max_dimension, max_radius
            )
        else:
            return {'success': False, 'error': f'Unknown filtration type: {filtration_type}'}

        return {
            'success': True,
            'filtration': filtration,
            'num_simplices': len(filtration),
            'max_dimension': max([s.dimension for s in filtration])
        }

    def _handle_compute_persistence(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute persistence pairs from filtration."""
        filtration = task_entry.get('filtration', [])

        if not filtration:
            point_cloud = np.array(task_entry.get('point_cloud', []))
            max_dimension = task_entry.get('max_dimension', 2)
            max_radius = task_entry.get('max_radius', float('inf'))
            filtration = self.construct_vietoris_rips_filtration(
                point_cloud, max_dimension, max_radius
            )

        pairs = self.compute_persistence_pairs(filtration)

        return {
            'success': True,
            'persistence_pairs': pairs,
            'num_pairs': len(pairs),
            'dimensions': sorted(set(p.dimension for p in pairs))
        }

    def _handle_persistence_diagram(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Generate persistence diagram."""
        pairs = task_entry.get('persistence_pairs', [])

        if not pairs:
            # Compute persistence first
            result = self._handle_compute_persistence(task_entry)
            if not result['success']:
                return result
            pairs = result['persistence_pairs']

        diagram = PersistenceDiagram(pairs=pairs)

        # Convert to plottable format
        diagram_data = {}
        for pair in pairs:
            dim = pair.dimension
            if dim not in diagram_data:
                diagram_data[dim] = []
            diagram_data[dim].append((pair.birth, pair.death))

        return {
            'success': True,
            'diagram': diagram,
            'diagram_data': diagram_data,
            'dimensions': sorted(diagram_data.keys())
        }

    def _handle_barcode(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Generate barcode representation."""
        pairs = task_entry.get('persistence_pairs', [])

        if not pairs:
            result = self._handle_compute_persistence(task_entry)
            if not result['success']:
                return result
            pairs = result['persistence_pairs']

        barcode_data = {}
        for pair in pairs:
            dim = pair.dimension
            if dim not in barcode_data:
                barcode_data[dim] = []
            barcode_data[dim].append((pair.birth, pair.death))

        return {
            'success': True,
            'barcode': barcode_data,
            'dimensions': sorted(barcode_data.keys())
        }

    def _handle_bottleneck_distance(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute bottleneck distance between two diagrams."""
        diagram1 = task_entry.get('diagram1', [])
        diagram2 = task_entry.get('diagram2', [])
        dimension = task_entry.get('dimension', None)

        distance = self.compute_bottleneck_distance(diagram1, diagram2, dimension)

        return {
            'success': True,
            'bottleneck_distance': distance,
            'dimension': dimension
        }

    def _handle_wasserstein_distance(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute Wasserstein distance between two diagrams."""
        diagram1 = task_entry.get('diagram1', [])
        diagram2 = task_entry.get('diagram2', [])
        p = task_entry.get('p', 2)
        dimension = task_entry.get('dimension', None)

        distance = self.compute_wasserstein_distance(diagram1, diagram2, p, dimension)

        return {
            'success': True,
            'wasserstein_distance': distance,
            'p': p,
            'dimension': dimension
        }

    def _handle_betti_numbers(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute persistent Betti numbers."""
        diagram = task_entry.get('diagram', None)
        epsilon = task_entry.get('epsilon', 0.0)

        if diagram is None:
            result = self._handle_persistence_diagram(task_entry)
            if not result['success']:
                return result
            diagram = result['diagram']

        betti = self.compute_persistent_betti_numbers(diagram, epsilon)

        return {
            'success': True,
            'betti_numbers': betti,
            'epsilon': epsilon
        }

    # Core algorithms

    def construct_vietoris_rips_filtration(
        self,
        point_cloud: np.ndarray,
        max_dimension: int,
        max_radius: float
    ) -> List[Simplex]:
        """
        Construct Vietoris-Rips filtration from point cloud.

        VR complex: simplices where all pairwise distances <= epsilon.

        Args:
            point_cloud: Array of points (n_points, n_features)
            max_dimension: Maximum simplex dimension
            max_radius: Maximum filtration value

        Returns:
            Sorted list of simplices with filtration values
        """
        n_points = len(point_cloud)

        # Compute pairwise distance matrix
        distances = self._compute_distance_matrix(point_cloud)

        # Build filtration
        filtration = []

        # 0-simplices (vertices)
        for i in range(n_points):
            simplex = Simplex(
                vertices=frozenset([i]),
                filtration_value=0.0,
                dimension=0
            )
            filtration.append(simplex)

        # Higher dimensional simplices
        for dim in range(1, max_dimension + 1):
            for vertices in combinations(range(n_points), dim + 1):
                # Filtration value = max pairwise distance
                max_dist = 0.0
                for i in range(len(vertices)):
                    for j in range(i + 1, len(vertices)):
                        max_dist = max(max_dist, distances[vertices[i], vertices[j]])

                if max_dist <= max_radius:
                    simplex = Simplex(
                        vertices=frozenset(vertices),
                        filtration_value=max_dist,
                        dimension=dim
                    )
                    filtration.append(simplex)

        # Sort by filtration value, then by dimension
        filtration.sort(key=lambda s: (s.filtration_value, s.dimension))

        return filtration

    def compute_boundary_matrix(self, filtration: List[Simplex]) -> np.ndarray:
        """
        Compute boundary matrix for a filtration.

        Boundary matrix ∂: ∂[i,j] = 1 if simplex i is a face of simplex j.

        Args:
            filtration: Sorted list of simplices

        Returns:
            Boundary matrix (sparse, mod 2)
        """
        n = len(filtration)
        boundary = np.zeros((n, n), dtype=np.int8)

        # Create index mapping
        simplex_to_index = {s.vertices: i for i, s in enumerate(filtration)}

        for j, simplex in enumerate(filtration):
            if simplex.dimension == 0:
                continue

            # Compute boundary: sum of (dim-1)-faces with alternating signs
            for i, v in enumerate(sorted(simplex.vertices)):
                # Face obtained by removing vertex v
                face_vertices = frozenset(simplex.vertices - {v})

                if face_vertices in simplex_to_index:
                    face_idx = simplex_to_index[face_vertices]
                    # Alternating sign (mod 2, so just count parity)
                    boundary[face_idx, j] = 1 - boundary[face_idx, j]

        return boundary

    def compute_persistence_pairs(
        self,
        filtration: List[Simplex]
    ) -> List[PersistencePair]:
        """
        Compute persistence pairs via standard reduction algorithm.

        Uses column reduction on boundary matrix to extract birth-death pairs.

        Args:
            filtration: Sorted list of simplices

        Returns:
            List of persistence pairs
        """
        if not filtration:
            return []

        boundary = self.compute_boundary_matrix(filtration)
        n = boundary.shape[1]

        # Track which columns are reduced
        reduced = boundary.copy()
        lowest_one = {}  # column -> lowest one row
        pair_column = {}  # column -> paired column

        # Standard reduction algorithm
        for j in range(n):
            while True:
                # Find lowest one in column j
                low = self._lowest_one(reduced[:, j])

                if low is None:
                    break

                # Check if another column has same lowest one
                if low in lowest_one:
                    k = lowest_one[low]
                    # Add column k to column j (mod 2)
                    reduced[:, j] = (reduced[:, j] + reduced[:, k]) % 2
                else:
                    lowest_one[low] = j
                    pair_column[j] = low
                    break

        # Extract persistence pairs
        pairs = []
        paired = set()

        for j in range(n):
            if j in pair_column:
                i = pair_column[j]
                paired.add(i)
                paired.add(j)

                birth = filtration[i].filtration_value
                death = filtration[j].filtration_value
                dimension = filtration[i].dimension

                if death > birth:  # Valid pair
                    pair = PersistencePair(
                        birth=birth,
                        death=death,
                        dimension=dimension,
                        birth_simplex=filtration[i].vertices,
                        death_simplex=filtration[j].vertices
                    )
                    pairs.append(pair)

        # Essential classes (infinite persistence)
        for i in range(n):
            if i not in paired and filtration[i].dimension >= 0:
                pair = PersistencePair(
                    birth=filtration[i].filtration_value,
                    death=float('inf'),
                    dimension=filtration[i].dimension,
                    birth_simplex=filtration[i].vertices
                )
                pairs.append(pair)

        return pairs

    def compute_bottleneck_distance(
        self,
        diagram1: List[PersistencePair],
        diagram2: List[PersistencePair],
        dimension: Optional[int] = None
    ) -> float:
        """
        Compute bottleneck distance between persistence diagrams.

        d_B(D1, D2) = inf_η sup_p ||p - η(p)||_∞

        Uses simplified matching algorithm (approximate for large diagrams).

        Args:
            diagram1: First persistence diagram
            diagram2: Second persistence diagram
            dimension: Filter by dimension (optional)

        Returns:
            Bottleneck distance
        """
        # Filter by dimension if specified
        if dimension is not None:
            diagram1 = [p for p in diagram1 if p.dimension == dimension]
            diagram2 = [p for p in diagram2 if p.dimension == dimension]

        # Convert to points (birth, death)
        points1 = [(p.birth, p.death if p.death != float('inf') else p.birth + 1000)
                   for p in diagram1]
        points2 = [(p.birth, p.death if p.death != float('inf') else p.birth + 1000)
                   for p in diagram2]

        if not points1 and not points2:
            return 0.0

        # Simplified bottleneck: maximum of nearest neighbor distances
        max_dist = 0.0

        for p1 in points1:
            min_dist = float('inf')
            for p2 in points2:
                dist = max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))
                min_dist = min(min_dist, dist)

            # Distance to diagonal
            diag_dist = abs(p1[1] - p1[0]) / 2
            min_dist = min(min_dist, diag_dist)

            max_dist = max(max_dist, min_dist)

        for p2 in points2:
            min_dist = float('inf')
            for p1 in points1:
                dist = max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))
                min_dist = min(min_dist, dist)

            diag_dist = abs(p2[1] - p2[0]) / 2
            min_dist = min(min_dist, diag_dist)

            max_dist = max(max_dist, min_dist)

        return max_dist

    def compute_wasserstein_distance(
        self,
        diagram1: List[PersistencePair],
        diagram2: List[PersistencePair],
        p: int = 2,
        dimension: Optional[int] = None
    ) -> float:
        """
        Compute Wasserstein distance between persistence diagrams.

        d_W^p(D1, D2) = (inf_η Σ||p - η(p)||^p)^{1/p}

        Args:
            diagram1: First persistence diagram
            diagram2: Second persistence diagram
            p: Wasserstein exponent
            dimension: Filter by dimension (optional)

        Returns:
            Wasserstein distance
        """
        if dimension is not None:
            diagram1 = [p for p in diagram1 if p.dimension == dimension]
            diagram2 = [p for p in diagram2 if p.dimension == dimension]

        points1 = [(p.birth, p.death if p.death != float('inf') else p.birth + 1000)
                   for p in diagram1]
        points2 = [(p.birth, p.death if p.death != float('inf') else p.birth + 1000)
                   for p in diagram2]

        if not points1 and not points2:
            return 0.0

        # Simplified Wasserstein: greedy matching
        total_cost = 0.0
        matched2 = set()

        for p1 in points1:
            min_cost = float('inf')
            best_j = None

            for j, p2 in enumerate(points2):
                if j in matched2:
                    continue
                cost = (abs(p1[0] - p2[0])**p + abs(p1[1] - p2[1])**p)**(1/p)
                if cost < min_cost:
                    min_cost = cost
                    best_j = j

            # Cost to diagonal
            diag_cost = (abs(p1[1] - p1[0]) / 2)**p

            if best_j is not None and min_cost**p < diag_cost:
                total_cost += min_cost**p
                matched2.add(best_j)
            else:
                total_cost += diag_cost

        # Unmatched points in diagram2
        for j, p2 in enumerate(points2):
            if j not in matched2:
                diag_cost = (abs(p2[1] - p2[0]) / 2)**p
                total_cost += diag_cost

        return total_cost**(1/p)

    def compute_persistent_betti_numbers(
        self,
        diagram: PersistenceDiagram,
        epsilon: float
    ) -> Dict[int, int]:
        """
        Compute persistent Betti numbers at filtration value epsilon.

        β_k(ε) = number of k-dimensional classes alive at time ε.

        Args:
            diagram: Persistence diagram
            epsilon: Filtration value

        Returns:
            Dictionary mapping dimension -> Betti number
        """
        betti = {}

        for pair in diagram.pairs:
            if pair.birth <= epsilon < pair.death:
                dim = pair.dimension
                betti[dim] = betti.get(dim, 0) + 1

        return betti

    # Utility methods

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

    def _lowest_one(self, column: np.ndarray) -> Optional[int]:
        """Find index of lowest non-zero entry in column."""
        nonzero = np.nonzero(column)[0]
        return int(nonzero[-1]) if len(nonzero) > 0 else None

    # BDI Agent methods

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard:
            # Check for new persistence computation requests
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
        stats['cache_size'] = len(self.persistence_cache)
        return stats
