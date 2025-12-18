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
SIMPLICIAL COMPLEX SPECIALIST (Tier 3)
=======================================

Constructs and analyzes simplicial complexes.

CAPABILITIES:
-------------
- Vietoris-Rips complex construction
- Cech complex construction
- Alpha complex (Delaunay-based)
- Boundary computation
- Face maps
- Simplicial map verification
- Nerve construction

ALGORITHMS:
-----------
- Distance-based complex construction
- Delaunay triangulation for alpha complexes
- Cover nerve construction

NO SYMPY - Pure Python/NumPy implementation.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Set, FrozenSet
from dataclasses import dataclass, field
from itertools import combinations
from collections import defaultdict

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration

logger = logging.getLogger('symbo_agentic_reasoners.specialists.simplicial_complex')


@dataclass
class SimplicialComplex:
    """
    A simplicial complex representation.

    Attributes:
        vertices: Set of vertex indices
        simplices: Dictionary mapping dimension -> set of simplices (as frozensets)
        metadata: Additional information
    """
    vertices: Set[int]
    simplices: Dict[int, Set[FrozenSet[int]]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_dimension(self) -> int:
        """Get maximum dimension of complex."""
        return max(self.simplices.keys()) if self.simplices else -1

    def get_faces(self, simplex: FrozenSet[int]) -> Set[FrozenSet[int]]:
        """Get all faces of a simplex."""
        faces = set()
        for k in range(len(simplex)):
            for face in combinations(simplex, k):
                faces.add(frozenset(face))
        return faces

    def contains(self, simplex: FrozenSet[int]) -> bool:
        """Check if complex contains simplex."""
        dim = len(simplex) - 1
        return dim in self.simplices and simplex in self.simplices[dim]

    def euler_characteristic(self) -> int:
        """Compute Euler characteristic χ = Σ(-1)^k * f_k."""
        chi = 0
        for dim, simplices in self.simplices.items():
            chi += ((-1) ** dim) * len(simplices)
        return chi


class SimplicialComplexSpecialist(BDIAgent):
    """
    BDI Agent for simplicial complex construction and analysis.

    Implements various complex construction algorithms for TDA.
    """

    def __init__(self, agent_id='simplicial_complex_specialist_001', df=None, blackboard=None):
        """
        Initialize SimplicialComplexSpecialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.complex_cache = {}
        self._epsilon = 1e-10

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.tda.simplicial_complex',
                agent_id=self.agent_id,
                algorithm='simplicial_complex',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))
            logger.info(f"{self.agent_id} registered with DF")

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a simplicial complex task.

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

        operation = metadata.get('operation', 'construct_vr')

        try:
            if operation == 'construct_vr' or operation == 'vietoris_rips':
                return self._handle_vietoris_rips(metadata)
            elif operation == 'construct_cech' or operation == 'cech':
                return self._handle_cech(metadata)
            elif operation == 'construct_alpha' or operation == 'alpha':
                return self._handle_alpha(metadata)
            elif operation == 'boundary':
                return self._handle_boundary(metadata)
            elif operation == 'face_map':
                return self._handle_face_map(metadata)
            elif operation == 'verify_map':
                return self._handle_verify_map(metadata)
            elif operation == 'nerve':
                return self._handle_nerve(metadata)
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

    def _handle_vietoris_rips(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Construct Vietoris-Rips complex."""
        point_cloud = np.array(task_entry.get('point_cloud', []))
        epsilon = task_entry.get('epsilon', 1.0)
        max_dimension = task_entry.get('max_dimension', 2)

        complex = self.construct_vietoris_rips(point_cloud, epsilon, max_dimension)

        return {
            'success': True,
            'complex': complex,
            'dimension': complex.get_dimension(),
            'f_vector': self._compute_f_vector(complex),
            'euler_characteristic': complex.euler_characteristic()
        }

    def _handle_cech(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Construct Cech complex."""
        point_cloud = np.array(task_entry.get('point_cloud', []))
        epsilon = task_entry.get('epsilon', 1.0)
        max_dimension = task_entry.get('max_dimension', 2)

        complex = self.construct_cech_complex(point_cloud, epsilon, max_dimension)

        return {
            'success': True,
            'complex': complex,
            'dimension': complex.get_dimension(),
            'f_vector': self._compute_f_vector(complex),
            'euler_characteristic': complex.euler_characteristic()
        }

    def _handle_alpha(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Construct Alpha complex."""
        point_cloud = np.array(task_entry.get('point_cloud', []))
        alpha = task_entry.get('alpha', None)

        complex = self.construct_alpha_complex(point_cloud, alpha)

        return {
            'success': True,
            'complex': complex,
            'dimension': complex.get_dimension(),
            'f_vector': self._compute_f_vector(complex),
            'euler_characteristic': complex.euler_characteristic()
        }

    def _handle_boundary(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute boundary of simplex."""
        simplex = frozenset(task_entry.get('simplex', []))
        complex_data = task_entry.get('complex', None)

        boundary = self.compute_simplicial_boundary(simplex, complex_data)

        return {
            'success': True,
            'boundary': list(boundary),
            'dimension': len(simplex) - 2
        }

    def _handle_face_map(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute face map."""
        simplex = frozenset(task_entry.get('simplex', []))
        vertex = task_entry.get('vertex')

        face = self.compute_face_map(simplex, vertex)

        return {
            'success': True,
            'face': list(face) if face else None,
            'dimension': len(face) - 1 if face else -1
        }

    def _handle_verify_map(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Verify simplicial map."""
        complex1 = task_entry.get('complex1')
        complex2 = task_entry.get('complex2')
        mapping = task_entry.get('mapping', {})

        is_valid, reason = self.check_simplicial_map(complex1, complex2, mapping)

        return {
            'success': True,
            'is_valid': is_valid,
            'reason': reason
        }

    def _handle_nerve(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Construct nerve of covering."""
        cover = task_entry.get('cover', [])

        nerve = self.compute_nerve(cover)

        return {
            'success': True,
            'nerve': nerve,
            'dimension': nerve.get_dimension(),
            'f_vector': self._compute_f_vector(nerve)
        }

    # Core algorithms

    def construct_vietoris_rips(
        self,
        point_cloud: np.ndarray,
        epsilon: float,
        max_dimension: int = 2
    ) -> SimplicialComplex:
        """
        Construct Vietoris-Rips complex.

        VR(X, ε) contains simplex σ if all pairwise distances ≤ ε.

        Args:
            point_cloud: Array of points (n_points, n_features)
            epsilon: Distance threshold
            max_dimension: Maximum simplex dimension

        Returns:
            Simplicial complex
        """
        n_points = len(point_cloud)

        # Compute distance matrix
        distances = self._compute_distance_matrix(point_cloud)

        # Build complex
        vertices = set(range(n_points))
        simplices = defaultdict(set)

        # 0-simplices (all vertices)
        simplices[0] = {frozenset([i]) for i in range(n_points)}

        # Higher dimensional simplices
        for dim in range(1, max_dimension + 1):
            for vertices_tuple in combinations(range(n_points), dim + 1):
                # Check if all pairwise distances <= epsilon
                is_simplex = True
                for i in range(len(vertices_tuple)):
                    for j in range(i + 1, len(vertices_tuple)):
                        if distances[vertices_tuple[i], vertices_tuple[j]] > epsilon:
                            is_simplex = False
                            break
                    if not is_simplex:
                        break

                if is_simplex:
                    simplices[dim].add(frozenset(vertices_tuple))

        return SimplicialComplex(
            vertices=vertices,
            simplices=dict(simplices),
            metadata={'type': 'vietoris_rips', 'epsilon': epsilon}
        )

    def construct_cech_complex(
        self,
        point_cloud: np.ndarray,
        epsilon: float,
        max_dimension: int = 2
    ) -> SimplicialComplex:
        """
        Construct Cech complex.

        Cech(X, ε) contains simplex σ if balls of radius ε around vertices have non-empty intersection.

        Args:
            point_cloud: Array of points (n_points, n_features)
            epsilon: Radius threshold
            max_dimension: Maximum simplex dimension

        Returns:
            Simplicial complex
        """
        n_points = len(point_cloud)

        # Build complex
        vertices = set(range(n_points))
        simplices = defaultdict(set)

        # 0-simplices
        simplices[0] = {frozenset([i]) for i in range(n_points)}

        # Higher dimensional simplices
        for dim in range(1, max_dimension + 1):
            for vertices_tuple in combinations(range(n_points), dim + 1):
                # Check if balls intersect (simplified: use circumradius)
                points = point_cloud[list(vertices_tuple)]
                circumradius = self._compute_circumradius(points)

                if circumradius <= epsilon:
                    simplices[dim].add(frozenset(vertices_tuple))

        return SimplicialComplex(
            vertices=vertices,
            simplices=dict(simplices),
            metadata={'type': 'cech', 'epsilon': epsilon}
        )

    def construct_alpha_complex(
        self,
        point_cloud: np.ndarray,
        alpha: Optional[float] = None
    ) -> SimplicialComplex:
        """
        Construct Alpha complex (Delaunay-based).

        Alpha complex is a subcomplex of Delaunay triangulation.

        Args:
            point_cloud: Array of points (n_points, n_features)
            alpha: Alpha parameter (None for full Delaunay)

        Returns:
            Simplicial complex
        """
        n_points = len(point_cloud)

        if point_cloud.shape[1] > 3:
            logger.warning("Alpha complex only implemented for 2D/3D. Falling back to VR.")
            return self.construct_vietoris_rips(
                point_cloud,
                alpha if alpha else 1.0,
                max_dimension=min(2, n_points - 1)
            )

        # Simplified: use Delaunay triangulation
        vertices = set(range(n_points))
        simplices = defaultdict(set)

        # 0-simplices
        simplices[0] = {frozenset([i]) for i in range(n_points)}

        # 1-simplices (edges) and 2-simplices (triangles)
        if n_points >= 2:
            # Connect nearby points (simplified Delaunay)
            distances = self._compute_distance_matrix(point_cloud)

            # 1-simplices
            threshold = alpha if alpha else np.median(distances[distances > 0])
            for i in range(n_points):
                for j in range(i + 1, n_points):
                    if distances[i, j] <= threshold:
                        simplices[1].add(frozenset([i, j]))

            # 2-simplices (triangles with small circumradius)
            if n_points >= 3 and point_cloud.shape[1] >= 2:
                for i, j, k in combinations(range(n_points), 3):
                    if (frozenset([i, j]) in simplices[1] and
                        frozenset([j, k]) in simplices[1] and
                        frozenset([i, k]) in simplices[1]):

                        points = point_cloud[[i, j, k]]
                        circumradius = self._compute_circumradius(points)

                        if alpha is None or circumradius <= alpha:
                            simplices[2].add(frozenset([i, j, k]))

        return SimplicialComplex(
            vertices=vertices,
            simplices=dict(simplices),
            metadata={'type': 'alpha', 'alpha': alpha}
        )

    def compute_simplicial_boundary(
        self,
        simplex: FrozenSet[int],
        complex: Optional[SimplicialComplex] = None
    ) -> Set[FrozenSet[int]]:
        """
        Compute boundary ∂σ of a simplex σ.

        ∂σ = Σ(-1)^i [v_0, ..., v̂_i, ..., v_n]

        Args:
            simplex: Simplex (as frozenset of vertices)
            complex: Parent complex (optional)

        Returns:
            Set of (dim-1)-faces
        """
        if len(simplex) <= 1:
            return set()

        boundary = set()
        vertices = sorted(simplex)

        for i, v in enumerate(vertices):
            # Face obtained by removing vertex v
            face = frozenset(vertices[:i] + vertices[i+1:])
            boundary.add(face)

        return boundary

    def compute_face_map(
        self,
        simplex: FrozenSet[int],
        vertex: int
    ) -> Optional[FrozenSet[int]]:
        """
        Compute face map d_i: σ → σ with i-th vertex removed.

        Args:
            simplex: Simplex (as frozenset)
            vertex: Vertex to remove

        Returns:
            Face (simplex with vertex removed), or None if vertex not in simplex
        """
        if vertex not in simplex:
            return None

        return frozenset(simplex - {vertex})

    def check_simplicial_map(
        self,
        complex1: SimplicialComplex,
        complex2: SimplicialComplex,
        mapping: Dict[int, int]
    ) -> Tuple[bool, str]:
        """
        Check if vertex mapping extends to simplicial map.

        A map φ: K → L is simplicial if φ maps simplices to simplices.

        Args:
            complex1: Source complex
            complex2: Target complex
            mapping: Vertex mapping (vertex in K → vertex in L)

        Returns:
            (is_valid, reason)
        """
        # Check all vertices are mapped
        for v in complex1.vertices:
            if v not in mapping:
                return False, f"Vertex {v} not in mapping"

        # Check image vertices exist in target
        for v, w in mapping.items():
            if w not in complex2.vertices:
                return False, f"Image vertex {w} not in target complex"

        # Check simplices map to simplices
        for dim, simplices in complex1.simplices.items():
            for simplex in simplices:
                # Map simplex
                image = frozenset(mapping[v] for v in simplex)

                # Check if image is in target complex
                if not complex2.contains(image):
                    return False, f"Simplex {simplex} maps to {image} which is not in target"

        return True, "Valid simplicial map"

    def compute_nerve(self, cover: List[Set[int]]) -> SimplicialComplex:
        """
        Compute nerve of a covering.

        Nerve(U) has simplex for each non-empty intersection of cover sets.

        Args:
            cover: List of sets (covering)

        Returns:
            Nerve complex
        """
        n = len(cover)
        vertices = set(range(n))
        simplices = defaultdict(set)

        # 0-simplices (all cover sets)
        simplices[0] = {frozenset([i]) for i in range(n)}

        # Higher dimensional simplices
        max_dim = min(n - 1, 10)  # Limit dimension for performance
        for dim in range(1, max_dim + 1):
            for indices in combinations(range(n), dim + 1):
                # Check if intersection is non-empty
                intersection = cover[indices[0]].copy()
                for i in indices[1:]:
                    intersection &= cover[i]

                if intersection:
                    simplices[dim].add(frozenset(indices))

        return SimplicialComplex(
            vertices=vertices,
            simplices=dict(simplices),
            metadata={'type': 'nerve', 'num_cover_sets': n}
        )

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

    def _compute_circumradius(self, points: np.ndarray) -> float:
        """
        Compute circumradius of simplex defined by points.

        Simplified computation using maximum distance.
        """
        if len(points) <= 1:
            return 0.0

        # Compute centroid
        centroid = np.mean(points, axis=0)

        # Circumradius approximated by max distance to centroid
        max_dist = 0.0
        for point in points:
            dist = np.linalg.norm(point - centroid)
            max_dist = max(max_dist, dist)

        return max_dist

    def _compute_f_vector(self, complex: SimplicialComplex) -> List[int]:
        """Compute f-vector (f_k = number of k-simplices)."""
        max_dim = complex.get_dimension()
        f_vector = []

        for dim in range(max_dim + 1):
            count = len(complex.simplices.get(dim, set()))
            f_vector.append(count)

        return f_vector

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
        stats['cache_size'] = len(self.complex_cache)
        return stats
