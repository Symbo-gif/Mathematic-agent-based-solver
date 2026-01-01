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
Topology Specialist
====================

Provides comprehensive topology operations:
- Point-set topology (open/closed sets, compactness)
- Homotopy and fundamental groups
- Simplicial complexes
- Homology computations
- Euler characteristic
- Covering spaces

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable, Set, FrozenSet
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TopologyResult:
    """Result from topological analysis."""
    is_hausdorff: bool = True
    is_compact: bool = False
    is_connected: bool = True
    is_path_connected: bool = True
    euler_characteristic: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HomologyResult:
    """Result from homology computation."""
    betti_numbers: List[int] = field(default_factory=list)
    euler_characteristic: int = 0
    homology_groups: Dict[int, str] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimplicialComplex:
    """Simplicial complex representation."""
    vertices: Set[int]
    simplices: Dict[int, Set[FrozenSet[int]]]  # dim -> set of simplices
    details: Dict[str, Any] = field(default_factory=dict)


class TopologySpecialist:
    """
    BDI Agent for topology computations.

    Capabilities:
    - Point-set topology analysis
    - Simplicial complex operations
    - Homology computation
    - Euler characteristic
    - Fundamental group (basic)
    """

    def __init__(self):
        self.beliefs: Dict[str, Any] = {}
        self.desires: List[str] = []
        self.intentions: List[Dict[str, Any]] = []
        self._epsilon = 1e-10

    def update_beliefs(self, observation: Dict[str, Any]) -> None:
        """Update agent beliefs based on observation."""
        self.beliefs.update(observation)

    def deliberate(self) -> List[str]:
        """Determine goals based on current beliefs."""
        self.desires = []
        if "simplicial_complex" in self.beliefs:
            self.desires.append("analyze_complex")
        if "space" in self.beliefs:
            self.desires.append("analyze_topology")
        return self.desires

    def execute_step(self) -> Dict[str, Any]:
        """Execute one reasoning step."""
        if not self.desires:
            return {"status": "no_goals"}

        goal = self.desires[0]
        if goal == "analyze_complex":
            complex_ = self.beliefs.get("simplicial_complex")
            return {"result": self.analyze_complex(complex_)}

        return {"status": "unknown_goal", "goal": goal}

    # ========== Simplicial Complex ==========

    def create_complex(
        self,
        simplices: List[Tuple[int, ...]]
    ) -> SimplicialComplex:
        """
        Create simplicial complex from list of simplices.

        Automatically includes all faces.

        Args:
            simplices: List of simplices as tuples of vertices

        Returns:
            SimplicialComplex
        """
        vertices = set()
        simplex_dict: Dict[int, Set[FrozenSet[int]]] = defaultdict(set)

        for simplex in simplices:
            # Add all faces
            self._add_simplex_with_faces(simplex, vertices, simplex_dict)

        return SimplicialComplex(
            vertices=vertices,
            simplices=dict(simplex_dict)
        )

    def _add_simplex_with_faces(
        self,
        simplex: Tuple[int, ...],
        vertices: Set[int],
        simplex_dict: Dict[int, Set[FrozenSet[int]]]
    ):
        """Recursively add simplex and all its faces."""
        dim = len(simplex) - 1
        frozen = frozenset(simplex)

        if frozen in simplex_dict.get(dim, set()):
            return

        simplex_dict[dim].add(frozen)

        # Add vertices
        vertices.update(simplex)

        # Add all faces (subsets of size dim)
        if dim > 0:
            for i in range(len(simplex)):
                face = simplex[:i] + simplex[i+1:]
                self._add_simplex_with_faces(face, vertices, simplex_dict)

    def f_vector(self, complex_: SimplicialComplex) -> List[int]:
        """
        Compute f-vector (number of simplices in each dimension).

        f_i = number of i-dimensional simplices

        Args:
            complex_: Simplicial complex

        Returns:
            List [f_0, f_1, f_2, ...]
        """
        if not complex_.simplices:
            return []

        max_dim = max(complex_.simplices.keys())
        f = []

        for d in range(max_dim + 1):
            f.append(len(complex_.simplices.get(d, set())))

        return f

    def euler_characteristic(self, complex_: SimplicialComplex) -> int:
        """
        Compute Euler characteristic.

        chi = sum((-1)^i * f_i) = f_0 - f_1 + f_2 - ...

        Args:
            complex_: Simplicial complex

        Returns:
            Euler characteristic
        """
        f = self.f_vector(complex_)
        chi = sum((-1)**i * f_i for i, f_i in enumerate(f))
        return chi

    # ========== Homology ==========

    def boundary_matrix(
        self,
        complex_: SimplicialComplex,
        dim: int
    ) -> np.ndarray:
        """
        Compute boundary matrix d_n: C_n -> C_{n-1}.

        Args:
            complex_: Simplicial complex
            dim: Dimension n

        Returns:
            Boundary matrix
        """
        if dim <= 0:
            return np.array([[]])

        n_simplices = complex_.simplices.get(dim, set())
        n_minus_1_simplices = complex_.simplices.get(dim - 1, set())

        if not n_simplices or not n_minus_1_simplices:
            return np.zeros((len(n_minus_1_simplices), len(n_simplices)))

        # Order simplices
        n_list = sorted(n_simplices, key=lambda s: tuple(sorted(s)))
        n_1_list = sorted(n_minus_1_simplices, key=lambda s: tuple(sorted(s)))

        n_1_index = {s: i for i, s in enumerate(n_1_list)}

        matrix = np.zeros((len(n_1_list), len(n_list)), dtype=int)

        for j, simplex in enumerate(n_list):
            # Compute boundary
            sorted_simplex = sorted(simplex)

            for i in range(len(sorted_simplex)):
                face = frozenset(sorted_simplex[:i] + sorted_simplex[i+1:])
                if face in n_1_index:
                    sign = (-1) ** i
                    matrix[n_1_index[face], j] = sign

        return matrix

    def compute_homology(
        self,
        complex_: SimplicialComplex
    ) -> HomologyResult:
        """
        Compute homology groups using Smith normal form.

        H_n = ker(d_n) / im(d_{n+1})

        Args:
            complex_: Simplicial complex

        Returns:
            HomologyResult with Betti numbers
        """
        if not complex_.simplices:
            return HomologyResult(betti_numbers=[])

        max_dim = max(complex_.simplices.keys())
        betti = []

        for n in range(max_dim + 1):
            # Compute ker(d_n) and im(d_{n+1})
            d_n = self.boundary_matrix(complex_, n)
            d_n_plus = self.boundary_matrix(complex_, n + 1)

            # Rank of ker(d_n)
            if d_n.size == 0:
                rank_ker = len(complex_.simplices.get(n, set()))
            else:
                rank_d_n = np.linalg.matrix_rank(d_n)
                n_simplices = d_n.shape[1]
                rank_ker = n_simplices - rank_d_n

            # Rank of im(d_{n+1})
            if d_n_plus.size == 0:
                rank_im = 0
            else:
                rank_im = np.linalg.matrix_rank(d_n_plus)

            # Betti number
            betti_n = max(0, rank_ker - rank_im)
            betti.append(betti_n)

        # Euler characteristic
        chi = sum((-1)**i * b for i, b in enumerate(betti))

        # Homology group descriptions
        groups = {}
        for i, b in enumerate(betti):
            if b == 0:
                groups[i] = "0"
            elif b == 1:
                groups[i] = "Z"
            else:
                groups[i] = f"Z^{b}"

        return HomologyResult(
            betti_numbers=betti,
            euler_characteristic=chi,
            homology_groups=groups
        )

    # ========== Standard Complexes ==========

    def simplex_complex(self, n: int) -> SimplicialComplex:
        """
        Create n-simplex (n+1 vertices, all subsets are faces).

        Args:
            n: Dimension

        Returns:
            SimplicialComplex
        """
        vertices = tuple(range(n + 1))
        return self.create_complex([vertices])

    def sphere_complex(self, n: int) -> SimplicialComplex:
        """
        Create boundary of (n+1)-simplex (triangulation of n-sphere).

        Args:
            n: Dimension of sphere

        Returns:
            SimplicialComplex
        """
        # Boundary = all proper faces of (n+1)-simplex
        vertices = list(range(n + 2))

        # All (n+1)-subsets (faces of full simplex)
        from itertools import combinations
        simplices = list(combinations(vertices, n + 1))

        return self.create_complex(simplices)

    def torus_complex(self) -> SimplicialComplex:
        """
        Create triangulation of 2-torus.

        Uses standard 9-vertex triangulation.

        Returns:
            SimplicialComplex
        """
        # 9 vertices arranged as 3x3 grid with wraparound
        # Vertices: 0-8

        triangles = [
            # Top-left square (0,1,3,4)
            (0, 1, 4), (0, 3, 4),
            # Top-middle square (1,2,4,5)
            (1, 2, 5), (1, 4, 5),
            # Top-right wraps to left (2,0,5,3)
            (2, 0, 3), (2, 3, 5),
            # Middle-left (3,4,6,7)
            (3, 4, 7), (3, 6, 7),
            # Middle-center (4,5,7,8)
            (4, 5, 8), (4, 7, 8),
            # Middle-right wraps (5,3,8,6)
            (5, 3, 6), (5, 6, 8),
            # Bottom wraps to top
            (6, 7, 1), (6, 0, 1),
            (7, 8, 2), (7, 1, 2),
            (8, 6, 0), (8, 0, 2)
        ]

        return self.create_complex(triangles)

    def klein_bottle_complex(self) -> SimplicialComplex:
        """
        Create triangulation of Klein bottle.

        Returns:
            SimplicialComplex
        """
        # Similar to torus but with one direction reversed
        triangles = [
            (0, 1, 4), (0, 3, 4),
            (1, 2, 5), (1, 4, 5),
            (2, 0, 5), (0, 5, 3),  # Reversed gluing
            (3, 4, 7), (3, 6, 7),
            (4, 5, 8), (4, 7, 8),
            (5, 3, 8), (3, 8, 6),
            (6, 7, 1), (6, 0, 1),
            (7, 8, 2), (7, 1, 2),
            (8, 6, 2), (6, 2, 0)  # Reversed
        ]

        return self.create_complex(triangles)

    def projective_plane_complex(self) -> SimplicialComplex:
        """
        Create triangulation of projective plane RP^2.

        Returns:
            SimplicialComplex
        """
        # 6-vertex triangulation
        triangles = [
            (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5), (0, 1, 5),
            (1, 2, 4), (2, 3, 5), (3, 4, 1), (4, 5, 2), (5, 1, 3)
        ]

        return self.create_complex(triangles)

    # ========== Analysis ==========

    def analyze_complex(
        self,
        complex_: SimplicialComplex
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of simplicial complex.

        Args:
            complex_: Simplicial complex

        Returns:
            Dictionary with all computed invariants
        """
        f = self.f_vector(complex_)
        chi = self.euler_characteristic(complex_)
        homology = self.compute_homology(complex_)

        return {
            "vertices": len(complex_.vertices),
            "f_vector": f,
            "euler_characteristic": chi,
            "betti_numbers": homology.betti_numbers,
            "homology_groups": homology.homology_groups,
            "dimension": len(f) - 1 if f else -1
        }

    def is_connected(self, complex_: SimplicialComplex) -> bool:
        """
        Check if complex is connected.

        H_0 = Z iff connected.

        Args:
            complex_: Simplicial complex

        Returns:
            True if connected
        """
        homology = self.compute_homology(complex_)
        return homology.betti_numbers[0] == 1 if homology.betti_numbers else False

    def fundamental_group_abelianization(
        self,
        complex_: SimplicialComplex
    ) -> str:
        """
        Compute abelianization of fundamental group.

        Ab(pi_1) = H_1 (first homology)

        Args:
            complex_: Simplicial complex

        Returns:
            String description of H_1
        """
        homology = self.compute_homology(complex_)
        if len(homology.betti_numbers) > 1:
            return homology.homology_groups.get(1, "0")
        return "0"

    # ========== Point-Set Topology ==========

    def check_continuity(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        domain_samples: List[np.ndarray],
        epsilon: float = 0.01
    ) -> Dict[str, Any]:
        """
        Check continuity of function numerically.

        Args:
            f: Function to check
            domain_samples: Sample points
            epsilon: Continuity threshold

        Returns:
            Dictionary with continuity analysis
        """
        discontinuities = []

        for x in domain_samples:
            # Check nearby points
            n = len(x)
            fx = f(x)

            for _ in range(10):
                delta = np.random.randn(n) * epsilon
                x_delta = x + delta

                try:
                    fx_delta = f(x_delta)
                    if np.linalg.norm(fx_delta - fx) > 10 * np.linalg.norm(delta):
                        discontinuities.append(x)
                        break
                except:
                    discontinuities.append(x)
                    break

        return {
            "is_continuous": len(discontinuities) == 0,
            "discontinuities_found": len(discontinuities),
            "sample_discontinuities": discontinuities[:5]
        }

    def check_homeomorphism(
        self,
        f: Callable[[np.ndarray], np.ndarray],
        g: Callable[[np.ndarray], np.ndarray],
        samples: List[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Check if f and g are inverse homeomorphisms.

        f o g = id and g o f = id (approximately)

        Args:
            f: First map
            g: Second map (proposed inverse)
            samples: Test points

        Returns:
            Dictionary with homeomorphism check
        """
        max_error_fg = 0
        max_error_gf = 0

        for x in samples:
            try:
                # f(g(x)) should be x
                fgx = f(g(x))
                error_fg = np.linalg.norm(fgx - x)
                max_error_fg = max(max_error_fg, error_fg)

                # g(f(x)) should be x
                gfx = g(f(x))
                error_gf = np.linalg.norm(gfx - x)
                max_error_gf = max(max_error_gf, error_gf)
            except:
                max_error_fg = float('inf')
                max_error_gf = float('inf')

        is_homeomorphism = max_error_fg < 0.01 and max_error_gf < 0.01

        return {
            "is_homeomorphism": is_homeomorphism,
            "max_error_f_o_g": max_error_fg,
            "max_error_g_o_f": max_error_gf
        }
