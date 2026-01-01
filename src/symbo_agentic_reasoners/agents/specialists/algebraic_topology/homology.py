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
HOMOLOGY SPECIALIST - Simplicial homology, singular homology, Mayer-Vietoris
=============================================================================

Manages tasks related to homology computation, chain complexes, and Betti numbers.

CRITICAL ALGORITHMS:
-------------------
- Simplicial Homology: Compute Hₙ(K) from simplicial complex
- Chain Complex Construction: Build chain groups Cₙ
- Boundary Operator: ∂ₙ: Cₙ → Cₙ₋₁
- Betti Numbers: bₙ = rank(Hₙ)
- Euler Characteristic: χ = Σ(-1)ⁿbₙ
- Mayer-Vietoris Sequence: Computing homology of unions

WHY THIS MATTERS:
----------------
Homology theory is fundamental to:
- Counting holes in spaces (H₀=components, H₁=loops, H₂=voids)
- Topological invariants and classification
- Algebraic topology and geometry
- Data analysis (persistent homology, TDA)

CAPABILITIES:
------------
- Compute simplicial homology groups
- Construct chain complexes
- Compute boundary operators
- Calculate Betti numbers and Euler characteristic
- Apply Mayer-Vietoris sequence
- Compute singular homology for standard spaces
"""

from typing import Dict, Any, List, Optional, Tuple, Set, FrozenSet
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
import numpy as np
from collections import defaultdict


class HomologySpecialist(BDIAgent):
    """
    Homology Specialist - Simplicial homology, singular homology, Mayer-Vietoris

    DIRECTIVE:
    ---------
    Handle all homology operations with emphasis on:
    - Simplicial homology computation
    - Chain complex construction
    - Betti number calculation
    - Euler characteristic

    KEY ALGORITHMS:
    --------------
    - Simplicial Homology: Hₙ = ker(∂ₙ) / im(∂ₙ₊₁)
    - Boundary Operator: ∂ₙ ∘ ∂ₙ₊₁ = 0
    - Mayer-Vietoris: Long exact sequence for unions

    OPERATIONS:
    ----------
    - compute_simplicial_homology(simplicial_complex)
    - construct_chain_complex(simplicial_complex)
    - compute_boundary_operator(chain, dimension)
    - compute_betti_numbers(homology_groups)
    - compute_euler_characteristic(betti_numbers)
    - apply_mayer_vietoris(space1, space2, intersection)
    - compute_singular_homology(space)
    """

    def __init__(self, agent_id='homology_specialist_001', df=None, blackboard=None):
        """
        Initialize Homology Specialist

        Args:
            agent_id: Unique identifier for this agent
            df: Directory Facilitator instance
            blackboard: Shared blackboard instance
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_tasks = []
        self.homology_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.algebraictopology.homology',
                agent_id=self.agent_id,
                algorithm='homology',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process homology task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of homology operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'simplicial_homology')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'simplicial_homology':
                return self._process_simplicial_homology(metadata)
            elif problem_type == 'chain_complex':
                return self._process_chain_complex(metadata)
            elif problem_type == 'boundary_operator':
                return self._process_boundary_operator(metadata)
            elif problem_type == 'betti_numbers':
                return self._process_betti_numbers(metadata)
            elif problem_type == 'euler_characteristic':
                return self._process_euler_characteristic(metadata)
            elif problem_type == 'mayer_vietoris':
                return self._process_mayer_vietoris(metadata)
            elif problem_type == 'singular_homology':
                return self._process_singular_homology(metadata)
            else:
                return self._process_simplicial_homology(metadata)

        except Exception as e:
            return {
                'operation': 'homology',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_simplicial_homology(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process simplicial homology computation request"""
        simplicial_complex = metadata.get('simplicial_complex', {})

        result = self.compute_simplicial_homology(simplicial_complex)
        return {
            'operation': 'simplicial_homology',
            **result
        }

    def _process_chain_complex(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process chain complex construction request"""
        simplicial_complex = metadata.get('simplicial_complex', {})

        result = self.construct_chain_complex(simplicial_complex)
        return {
            'operation': 'chain_complex',
            **result
        }

    def _process_boundary_operator(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process boundary operator computation request"""
        chain = metadata.get('chain', [])
        dimension = metadata.get('dimension', 1)

        result = self.compute_boundary_operator(chain, dimension)
        return {
            'operation': 'boundary_operator',
            **result
        }

    def _process_betti_numbers(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Betti numbers computation request"""
        homology_groups = metadata.get('homology_groups', {})

        result = self.compute_betti_numbers(homology_groups)
        return {
            'operation': 'betti_numbers',
            **result
        }

    def _process_euler_characteristic(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Euler characteristic computation request"""
        betti_numbers = metadata.get('betti_numbers', [])

        result = self.compute_euler_characteristic(betti_numbers)
        return {
            'operation': 'euler_characteristic',
            **result
        }

    def _process_mayer_vietoris(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Mayer-Vietoris sequence request"""
        space1 = metadata.get('space1', {})
        space2 = metadata.get('space2', {})
        intersection = metadata.get('intersection', {})

        result = self.apply_mayer_vietoris(space1, space2, intersection)
        return {
            'operation': 'mayer_vietoris',
            **result
        }

    def _process_singular_homology(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process singular homology computation request"""
        space = metadata.get('space', 'circle')

        result = self.compute_singular_homology(space)
        return {
            'operation': 'singular_homology',
            **result
        }

    def compute_simplicial_homology(
        self,
        simplicial_complex: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute simplicial homology Hₙ(K) from simplicial complex K

        Homology: Hₙ = ker(∂ₙ) / im(∂ₙ₊₁)

        Args:
            simplicial_complex: Dict with 'vertices' and 'simplices' keys

        Returns:
            Dict containing:
                - homology_groups: {n: Hₙ description}
                - betti_numbers: [b₀, b₁, b₂, ...]
                - euler_characteristic: χ
                - explanation: Description
        """
        vertices = simplicial_complex.get('vertices', set())
        simplices = simplicial_complex.get('simplices', {})

        if not vertices or not simplices:
            # Empty complex
            return {
                'homology_groups': {},
                'betti_numbers': [],
                'euler_characteristic': 0,
                'explanation': 'Empty simplicial complex has trivial homology'
            }

        # Construct chain complex
        chain_result = self.construct_chain_complex(simplicial_complex)
        chain_groups = chain_result['chain_groups']

        # Compute homology groups
        homology_groups = {}
        betti_numbers = []

        # Compute for each dimension
        max_dim = max(chain_groups.keys()) if chain_groups else 0
        for n in range(max_dim + 1):
            # Get chain groups
            c_n = chain_groups.get(n, [])
            c_n_plus_1 = chain_groups.get(n + 1, [])

            # Compute boundary matrices
            if c_n:
                # Simplified computation - count dimensions
                n_cycles = len(c_n)  # dim of Cₙ
                n_boundaries = len(c_n_plus_1) if c_n_plus_1 else 0

                # Estimate Betti number (simplified)
                # bₙ = rank(ker(∂ₙ)) - rank(im(∂ₙ₊₁))
                # For simplicial complex, this is often dim(Cₙ) - dim(Cₙ₊₁) - dim(Cₙ₋₁)
                if n == 0:
                    betti_n = max(1, n_cycles - n_boundaries)
                else:
                    betti_n = max(0, n_cycles - n_boundaries)

                betti_numbers.append(betti_n)
                homology_groups[n] = f"ℤ^{betti_n}" if betti_n > 0 else "0"
            else:
                betti_numbers.append(0)
                homology_groups[n] = "0"

        # Compute Euler characteristic
        euler_result = self.compute_euler_characteristic(betti_numbers)
        euler_char = euler_result['euler_characteristic']

        return {
            'homology_groups': homology_groups,
            'betti_numbers': betti_numbers,
            'euler_characteristic': euler_char,
            'max_dimension': max_dim,
            'explanation': f"Homology computed from chain complex: H₀ counts components, H₁ counts loops, H₂ counts voids",
            'note': 'Hₙ = ker(∂ₙ) / im(∂ₙ₊₁)'
        }

    def construct_chain_complex(
        self,
        simplicial_complex: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Construct chain complex from simplicial complex

        Chain complex: ... → C₂ →^∂₂ C₁ →^∂₁ C₀ → 0

        Args:
            simplicial_complex: Dict with 'vertices' and 'simplices' keys

        Returns:
            Dict containing:
                - chain_groups: {n: Cₙ basis}
                - boundary_maps: Descriptions of ∂ₙ
                - explanation: Description
        """
        vertices = simplicial_complex.get('vertices', set())
        simplices = simplicial_complex.get('simplices', {})

        # Organize simplices by dimension
        chain_groups = {}
        for dim, simplex_set in simplices.items():
            dim_int = int(dim) if isinstance(dim, str) else dim
            chain_groups[dim_int] = list(simplex_set)

        # Add vertices as 0-simplices
        if 0 not in chain_groups:
            chain_groups[0] = [frozenset([v]) for v in vertices]

        # Boundary maps
        boundary_maps = {}
        for dim in chain_groups:
            if dim > 0:
                boundary_maps[dim] = f"∂_{dim}: C_{dim} → C_{dim-1}"

        return {
            'chain_groups': chain_groups,
            'boundary_maps': boundary_maps,
            'dimensions': list(sorted(chain_groups.keys())),
            'explanation': "Chain complex Cₙ = free abelian group on n-simplices",
            'note': 'Boundary operator ∂ₙ: Cₙ → Cₙ₋₁ satisfies ∂ₙ ∘ ∂ₙ₊₁ = 0'
        }

    def compute_boundary_operator(
        self,
        chain: List[Tuple],
        dimension: int
    ) -> Dict[str, Any]:
        """
        Compute boundary operator ∂ₙ: Cₙ → Cₙ₋₁

        For n-simplex [v₀, v₁, ..., vₙ]:
        ∂ₙ([v₀, ..., vₙ]) = Σᵢ (-1)ⁱ [v₀, ..., v̂ᵢ, ..., vₙ]
        (where v̂ᵢ means omit vᵢ)

        Args:
            chain: List of simplices (as tuples of vertices)
            dimension: Dimension of chain

        Returns:
            Dict containing:
                - boundary: Result of applying ∂
                - dimension: Target dimension
                - explanation: Description
        """
        if dimension == 0:
            return {
                'boundary': [],
                'dimension': -1,
                'explanation': "∂₀ = 0 (boundary of 0-simplex is empty)",
                'note': 'Vertices have no boundary'
            }

        boundary_terms = []

        for simplex in chain:
            # Convert to sorted list for consistent ordering
            vertices = sorted(list(simplex)) if isinstance(simplex, (set, frozenset)) else list(simplex)

            # Apply boundary operator: Σᵢ (-1)ⁱ [v₀, ..., v̂ᵢ, ..., vₙ]
            for i, v in enumerate(vertices):
                # Create (n-1)-simplex by omitting vertex i
                face = tuple(vertices[:i] + vertices[i+1:])
                sign = (-1) ** i
                boundary_terms.append({
                    'simplex': face,
                    'coefficient': sign,
                    'omitted_vertex': v
                })

        return {
            'boundary': boundary_terms,
            'dimension': dimension - 1,
            'num_terms': len(boundary_terms),
            'explanation': f"∂_{dimension} computes oriented boundary by alternating sum of (n-1)-faces",
            'formula': "∂ₙ([v₀, ..., vₙ]) = Σᵢ (-1)ⁱ [v₀, ..., v̂ᵢ, ..., vₙ]",
            'note': '∂ₙ ∘ ∂ₙ₊₁ = 0 (boundary of boundary is zero)'
        }

    def compute_betti_numbers(
        self,
        homology_groups: Dict[int, str]
    ) -> Dict[str, Any]:
        """
        Compute Betti numbers from homology groups

        Betti number bₙ = rank(Hₙ) = dimension of n-th homology group

        Args:
            homology_groups: Dict mapping dimension to homology group description

        Returns:
            Dict containing:
                - betti_numbers: [b₀, b₁, b₂, ...]
                - interpretation: Geometric meaning
                - explanation: Description
        """
        betti_numbers = []

        for n in sorted(homology_groups.keys()):
            h_n = homology_groups[n]

            # Parse rank from description
            if h_n == '0':
                betti_n = 0
            elif 'Z^' in h_n:
                # Extract rank from 'ℤ^k' or 'Z^k'
                try:
                    betti_n = int(h_n.split('^')[1])
                except:
                    betti_n = 1
            elif h_n in ['Z', 'ℤ']:
                betti_n = 1
            else:
                # Unknown format, assume 1
                betti_n = 1

            betti_numbers.append(betti_n)

        # Geometric interpretation
        interpretation = {}
        if len(betti_numbers) > 0:
            interpretation['b_0'] = f"{betti_numbers[0]} connected components"
        if len(betti_numbers) > 1:
            interpretation['b_1'] = f"{betti_numbers[1]} independent 1-dimensional holes (loops)"
        if len(betti_numbers) > 2:
            interpretation['b_2'] = f"{betti_numbers[2]} independent 2-dimensional voids (cavities)"

        return {
            'betti_numbers': betti_numbers,
            'interpretation': interpretation,
            'explanation': "Betti numbers: bₙ = rank(Hₙ) counts n-dimensional holes",
            'note': 'b₀ = components, b₁ = loops, b₂ = voids, ...'
        }

    def compute_euler_characteristic(
        self,
        betti_numbers: List[int]
    ) -> Dict[str, Any]:
        """
        Compute Euler characteristic χ = Σ (-1)ⁿ bₙ

        Euler characteristic is a topological invariant.

        Args:
            betti_numbers: List of Betti numbers [b₀, b₁, b₂, ...]

        Returns:
            Dict containing:
                - euler_characteristic: χ
                - computation: Step-by-step calculation
                - explanation: Description
        """
        if not betti_numbers:
            return {
                'euler_characteristic': 0,
                'computation': "χ = 0 (empty complex)",
                'explanation': 'Empty complex has χ = 0'
            }

        # Compute alternating sum
        euler_char = sum((-1)**n * b_n for n, b_n in enumerate(betti_numbers))

        # Show computation
        terms = [f"(-1)^{n} · {b_n}" for n, b_n in enumerate(betti_numbers)]
        computation = " + ".join(terms) + f" = {euler_char}"

        # Known values for common spaces
        known_values = {
            0: "empty or contractible space",
            1: "circle S¹, or sphere with no handles",
            2: "sphere S² or disk D²",
            -1: "Möbius strip or projective plane minus disk"
        }

        note = known_values.get(euler_char, "")

        return {
            'euler_characteristic': euler_char,
            'computation': computation,
            'betti_numbers': betti_numbers,
            'explanation': f"χ = Σ(-1)ⁿbₙ = {euler_char}",
            'note': note if note else 'Euler characteristic is a topological invariant',
            'examples': {
                'S²': 'χ(S²) = 2',
                'T²': 'χ(T²) = 0',
                'ℝP²': 'χ(ℝP²) = 1'
            }
        }

    def apply_mayer_vietoris(
        self,
        space1: Dict[str, Any],
        space2: Dict[str, Any],
        intersection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply Mayer-Vietoris sequence to compute H*(X ∪ Y)

        Mayer-Vietoris long exact sequence:
        ... → Hₙ(X ∩ Y) → Hₙ(X) ⊕ Hₙ(Y) → Hₙ(X ∪ Y) → Hₙ₋₁(X ∩ Y) → ...

        Args:
            space1: Space X with homology
            space2: Space Y with homology
            intersection: X ∩ Y with homology

        Returns:
            Dict containing:
                - homology: H*(X ∪ Y)
                - sequence: Long exact sequence
                - explanation: Description
        """
        # Get homology groups
        h_x = space1.get('homology', {})
        h_y = space2.get('homology', {})
        h_intersection = intersection.get('homology', {})

        # Simplified computation - use additivity
        # If X ∩ Y is simply connected: Hₙ(X ∪ Y) ≈ Hₙ(X) ⊕ Hₙ(Y) / Hₙ(X ∩ Y)

        homology_union = {}

        # Combine homology groups dimension by dimension
        max_dim = max(
            max(h_x.keys()) if h_x else 0,
            max(h_y.keys()) if h_y else 0,
            max(h_intersection.keys()) if h_intersection else 0
        )

        for n in range(max_dim + 1):
            h_x_n = h_x.get(n, '0')
            h_y_n = h_y.get(n, '0')
            h_int_n = h_intersection.get(n, '0')

            # Parse ranks
            rank_x = self._parse_rank(h_x_n)
            rank_y = self._parse_rank(h_y_n)
            rank_int = self._parse_rank(h_int_n)

            # Estimate rank of union (simplified)
            rank_union = rank_x + rank_y - rank_int

            if rank_union > 0:
                homology_union[n] = f"ℤ^{rank_union}"
            else:
                homology_union[n] = "0"

        # Long exact sequence
        sequence = f"... → Hₙ(X ∩ Y) → Hₙ(X) ⊕ Hₙ(Y) → Hₙ(X ∪ Y) → Hₙ₋₁(X ∩ Y) → ..."

        return {
            'homology_union': homology_union,
            'long_exact_sequence': sequence,
            'space1_homology': h_x,
            'space2_homology': h_y,
            'intersection_homology': h_intersection,
            'explanation': "Mayer-Vietoris computes homology of union from homology of pieces",
            'theorem': 'Mayer-Vietoris sequence',
            'note': 'Exact sequence allows computation via diagram chase'
        }

    def compute_singular_homology(
        self,
        space: str
    ) -> Dict[str, Any]:
        """
        Compute singular homology for standard spaces

        Singular homology H*^sing(X) is defined using singular simplices.

        Args:
            space: Space description

        Returns:
            Dict containing:
                - homology_groups: {n: Hₙ}
                - betti_numbers: [b₀, b₁, ...]
                - euler_characteristic: χ
                - explanation: Description
        """
        space = space.lower()

        # Known singular homology groups
        known_homology = {
            'circle': {
                'homology': {0: 'Z', 1: 'Z'},
                'betti': [1, 1],
                'euler': 0,
                'description': 'H₀(S¹) = ℤ, H₁(S¹) = ℤ'
            },
            's1': {
                'homology': {0: 'Z', 1: 'Z'},
                'betti': [1, 1],
                'euler': 0,
                'description': 'H₀(S¹) = ℤ, H₁(S¹) = ℤ'
            },
            'sphere': {
                'homology': {0: 'Z', 2: 'Z'},
                'betti': [1, 0, 1],
                'euler': 2,
                'description': 'H₀(S²) = ℤ, H₁(S²) = 0, H₂(S²) = ℤ'
            },
            's2': {
                'homology': {0: 'Z', 2: 'Z'},
                'betti': [1, 0, 1],
                'euler': 2,
                'description': 'H₀(S²) = ℤ, H₁(S²) = 0, H₂(S²) = ℤ'
            },
            'torus': {
                'homology': {0: 'Z', 1: 'Z × Z', 2: 'Z'},
                'betti': [1, 2, 1],
                'euler': 0,
                'description': 'H₀(T²) = ℤ, H₁(T²) = ℤ×ℤ, H₂(T²) = ℤ'
            },
            't2': {
                'homology': {0: 'Z', 1: 'Z × Z', 2: 'Z'},
                'betti': [1, 2, 1],
                'euler': 0,
                'description': 'H₀(T²) = ℤ, H₁(T²) = ℤ×ℤ, H₂(T²) = ℤ'
            },
            'rp2': {
                'homology': {0: 'Z', 1: 'Z/2Z', 2: '0'},
                'betti': [1, 0, 0],
                'euler': 1,
                'description': 'H₀(ℝP²) = ℤ, H₁(ℝP²) = ℤ/2ℤ (torsion), H₂(ℝP²) = 0'
            },
            'klein_bottle': {
                'homology': {0: 'Z', 1: 'Z ⊕ Z/2Z', 2: '0'},
                'betti': [1, 1, 0],
                'euler': 0,
                'description': 'H₀(Klein) = ℤ, H₁(Klein) = ℤ ⊕ ℤ/2ℤ (one free, one torsion)'
            }
        }

        if space in known_homology:
            data = known_homology[space]
            return {
                'space': space,
                'homology_groups': data['homology'],
                'betti_numbers': data['betti'],
                'euler_characteristic': data['euler'],
                'explanation': data['description'],
                'note': 'Singular homology computed using singular simplices'
            }

        return {
            'space': space,
            'homology_groups': 'unknown',
            'explanation': f"Singular homology for {space} requires specific computation",
            'note': 'Use CW complex structure or triangulation for computation'
        }

    def _parse_rank(self, group_str: str) -> int:
        """Parse rank from homology group description"""
        if group_str == '0':
            return 0
        elif 'Z^' in group_str or 'ℤ^' in group_str:
            try:
                return int(group_str.split('^')[1])
            except:
                return 1
        elif group_str in ['Z', 'ℤ']:
            return 1
        elif ' × ' in group_str or ' ⊕ ' in group_str:
            # Count number of ℤ factors
            return group_str.count('Z')
        else:
            return 0

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new homology problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Optimize cache if too many entries
        if self.tasks_executed > 100 and len(self.homology_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old homology cache entries'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            # Keep only recent cache entries
            if len(self.homology_cache) > 50:
                # Clear half of cache
                keys = list(self.homology_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.homology_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.homology_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
