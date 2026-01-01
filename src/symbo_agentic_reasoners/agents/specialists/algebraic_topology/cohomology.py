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
COHOMOLOGY SPECIALIST - Cohomology rings, cup product, Universal Coefficient Theorem
====================================================================================

Manages tasks related to cohomology theory, cup products, and cohomology rings.

CRITICAL ALGORITHMS:
-------------------
- Cohomology Group Computation: H^n(X) from chain complex
- Cup Product: ∪: H^p(X) × H^q(X) → H^{p+q}(X)
- Universal Coefficient Theorem: H^n(X) from H_n(X)
- Poincaré Duality: H^k(M) ≅ H_{n-k}(M) for n-manifolds
- Cohomology Ring Structure: Ring structure on H*(X)
- Characteristic Classes: Chern/Stiefel-Whitney classes

WHY THIS MATTERS:
----------------
Cohomology theory is fundamental to:
- Ring structure on topology (cup product)
- Duality theory for manifolds
- Characteristic classes and fiber bundles
- Algebraic geometry and sheaf cohomology

CAPABILITIES:
------------
- Compute cohomology groups
- Compute cup products
- Apply Universal Coefficient Theorem
- Verify Poincaré duality
- Compute cohomology ring structure
- Calculate characteristic classes
"""

from typing import Dict, Any, List, Optional, Tuple
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
import numpy as np


class CohomologySpecialist(BDIAgent):
    """
    Cohomology Specialist - Cohomology rings, cup product, Universal Coefficient Theorem

    DIRECTIVE:
    ---------
    Handle all cohomology operations with emphasis on:
    - Cohomology group computation
    - Cup product computation
    - Universal Coefficient Theorem
    - Poincaré duality

    KEY ALGORITHMS:
    --------------
    - Cohomology: H^n = Hom(H_n, ℤ)
    - Cup Product: ∪: H^p × H^q → H^{p+q}
    - UCT: H^n(X; G) from H_n(X) and G

    OPERATIONS:
    ----------
    - compute_cohomology_groups(chain_complex)
    - compute_cup_product(cocycle1, cocycle2)
    - apply_universal_coefficient_theorem(homology)
    - compute_poincare_duality(manifold, dimension)
    - compute_cohomology_ring_structure(space)
    - compute_characteristic_classes(vector_bundle)
    """

    def __init__(self, agent_id='cohomology_specialist_001', df=None, blackboard=None):
        """
        Initialize Cohomology Specialist

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
        self.cohomology_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.algebraictopology.cohomology',
                agent_id=self.agent_id,
                algorithm='cohomology',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process cohomology task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of cohomology operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'cohomology_groups')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'cohomology_groups':
                return self._process_cohomology_groups(metadata)
            elif problem_type == 'cup_product':
                return self._process_cup_product(metadata)
            elif problem_type == 'universal_coefficient':
                return self._process_universal_coefficient(metadata)
            elif problem_type == 'poincare_duality':
                return self._process_poincare_duality(metadata)
            elif problem_type == 'cohomology_ring':
                return self._process_cohomology_ring(metadata)
            elif problem_type == 'characteristic_classes':
                return self._process_characteristic_classes(metadata)
            else:
                return self._process_cohomology_groups(metadata)

        except Exception as e:
            return {
                'operation': 'cohomology',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_cohomology_groups(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process cohomology groups computation request"""
        chain_complex = metadata.get('chain_complex', {})

        result = self.compute_cohomology_groups(chain_complex)
        return {
            'operation': 'cohomology_groups',
            **result
        }

    def _process_cup_product(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process cup product computation request"""
        cocycle1 = metadata.get('cocycle1', {})
        cocycle2 = metadata.get('cocycle2', {})

        result = self.compute_cup_product(cocycle1, cocycle2)
        return {
            'operation': 'cup_product',
            **result
        }

    def _process_universal_coefficient(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Universal Coefficient Theorem application"""
        homology = metadata.get('homology', {})

        result = self.apply_universal_coefficient_theorem(homology)
        return {
            'operation': 'universal_coefficient_theorem',
            **result
        }

    def _process_poincare_duality(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Poincaré duality computation"""
        manifold = metadata.get('manifold', 'sphere')
        dimension = metadata.get('dimension', 2)

        result = self.compute_poincare_duality(manifold, dimension)
        return {
            'operation': 'poincare_duality',
            **result
        }

    def _process_cohomology_ring(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process cohomology ring structure computation"""
        space = metadata.get('space', 'circle')

        result = self.compute_cohomology_ring_structure(space)
        return {
            'operation': 'cohomology_ring_structure',
            **result
        }

    def _process_characteristic_classes(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process characteristic classes computation"""
        vector_bundle = metadata.get('vector_bundle', {})

        result = self.compute_characteristic_classes(vector_bundle)
        return {
            'operation': 'characteristic_classes',
            **result
        }

    def compute_cohomology_groups(
        self,
        chain_complex: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute cohomology groups H^n(X) from chain complex

        Cohomology: H^n = ker(δ^n) / im(δ^{n-1})
        where δ^n: C^n → C^{n+1} is coboundary operator

        Args:
            chain_complex: Dict with chain groups

        Returns:
            Dict containing:
                - cohomology_groups: {n: H^n description}
                - explanation: Description
        """
        chain_groups = chain_complex.get('chain_groups', {})

        if not chain_groups:
            return {
                'cohomology_groups': {},
                'explanation': 'Empty chain complex has trivial cohomology'
            }

        # Dual to homology computation
        # H^n(X; ℤ) = Hom(H_n(X), ℤ) for free homology
        cohomology_groups = {}

        max_dim = max(chain_groups.keys()) if chain_groups else 0
        for n in range(max_dim + 1):
            # Simplified: cohomology groups are dual to homology groups
            # For free groups: H^n ≅ H_n
            c_n = chain_groups.get(n, [])
            if c_n:
                rank_n = len(c_n)
                if rank_n > 0:
                    cohomology_groups[n] = f"ℤ^{rank_n}"
                else:
                    cohomology_groups[n] = "0"
            else:
                cohomology_groups[n] = "0"

        return {
            'cohomology_groups': cohomology_groups,
            'explanation': "Cohomology H^n(X) dual to homology H_n(X)",
            'note': 'H^n = Hom(H_n, ℤ) for free homology groups',
            'coboundary': 'δ^n: C^n → C^{n+1} is dual to boundary operator'
        }

    def compute_cup_product(
        self,
        cocycle1: Dict[str, Any],
        cocycle2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute cup product α ∪ β ∈ H^{p+q}(X)

        Cup product: ∪: H^p(X) × H^q(X) → H^{p+q}(X)
        gives ring structure to cohomology

        Args:
            cocycle1: Cocycle α ∈ H^p
            cocycle2: Cocycle β ∈ H^q

        Returns:
            Dict containing:
                - cup_product: α ∪ β
                - dimension: p + q
                - explanation: Description
        """
        p = cocycle1.get('dimension', 0)
        q = cocycle2.get('dimension', 0)
        space = cocycle1.get('space', 'unknown')

        product_dim = p + q

        # Known cup products for standard spaces
        if space.lower() in ['circle', 's1']:
            # H^1(S¹) × H^1(S¹) → H^2(S¹) = 0
            if p == 1 and q == 1:
                return {
                    'cup_product': '0',
                    'dimension': product_dim,
                    'explanation': "α ∪ β = 0 since H^2(S¹) = 0",
                    'note': 'S¹ has no 2-dimensional cohomology'
                }

        if space.lower() in ['torus', 't2']:
            # H^1(T²) × H^1(T²) → H^2(T²) ≅ ℤ
            if p == 1 and q == 1:
                return {
                    'cup_product': 'generator of H^2(T²) ≅ ℤ',
                    'dimension': product_dim,
                    'explanation': "Cup product of two 1-cocycles generates H^2(T²)",
                    'note': 'This shows cohomology ring structure: H^1 ⊗ H^1 → H^2'
                }

        return {
            'cup_product': f"α ∪ β ∈ H^{product_dim}({space})",
            'dimension': product_dim,
            'cocycle1_dimension': p,
            'cocycle2_dimension': q,
            'explanation': f"Cup product of cocycles in H^{p} and H^{q} gives cocycle in H^{product_dim}",
            'properties': {
                'associative': '(α ∪ β) ∪ γ = α ∪ (β ∪ γ)',
                'graded_commutative': 'α ∪ β = (-1)^{pq} (β ∪ α)',
                'unit': '1 ∪ α = α'
            },
            'note': 'Cup product gives H*(X) graded commutative ring structure'
        }

    def apply_universal_coefficient_theorem(
        self,
        homology: Dict[int, str]
    ) -> Dict[str, Any]:
        """
        Apply Universal Coefficient Theorem to compute H^n from H_n

        UCT: 0 → Ext(H_{n-1}(X), G) → H^n(X; G) → Hom(H_n(X), G) → 0

        For G = ℤ and free homology: H^n(X; ℤ) ≅ H_n(X)

        Args:
            homology: Homology groups {n: H_n}

        Returns:
            Dict containing:
                - cohomology: Cohomology groups H^n
                - explanation: Description
        """
        cohomology = {}

        for n, h_n in homology.items():
            # For free homology groups: H^n ≅ H_n
            # Parse homology group
            if h_n == '0':
                cohomology[n] = '0'
            elif 'ℤ' in h_n or 'Z' in h_n:
                # Free part remains the same
                cohomology[n] = h_n
            elif '/' in h_n:
                # Torsion part: Ext(Z/nZ, Z) = Z/nZ
                cohomology[n] = f"Torsion from {h_n}"
            else:
                cohomology[n] = h_n

        return {
            'cohomology_groups': cohomology,
            'homology_groups': homology,
            'theorem': 'Universal Coefficient Theorem',
            'explanation': "UCT relates cohomology to homology",
            'formula': 'H^n(X; G) computed from H_n(X) and H_{n-1}(X)',
            'note': 'For free homology: H^n(X; ℤ) ≅ Hom(H_n(X), ℤ) ≅ H_n(X)',
            'ext_term': 'Ext(H_{n-1}(X), G) captures torsion information'
        }

    def compute_poincare_duality(
        self,
        manifold: str,
        dimension: int
    ) -> Dict[str, Any]:
        """
        Compute Poincaré duality for oriented closed manifold

        Poincaré Duality: H^k(M) ≅ H_{n-k}(M) for n-dimensional closed oriented manifold M

        Args:
            manifold: Manifold description
            dimension: Dimension n of manifold

        Returns:
            Dict containing:
                - duality_isomorphisms: {k: H^k ≅ H_{n-k}}
                - explanation: Description
        """
        manifold = manifold.lower()

        # Known manifolds
        duality_isomorphisms = {}

        if 'sphere' in manifold or manifold.startswith('s'):
            # S^n: H^k(S^n) ≅ H_{n-k}(S^n)
            # H^0(S^n) ≅ ℤ ≅ H_n(S^n)
            # H^k(S^n) = 0 for 0 < k < n ≅ H_{n-k}(S^n) = 0
            # H^n(S^n) ≅ ℤ ≅ H_0(S^n)
            for k in range(dimension + 1):
                if k == 0:
                    duality_isomorphisms[k] = f"H^0(S^{dimension}) ≅ ℤ ≅ H_{dimension}(S^{dimension})"
                elif k == dimension:
                    duality_isomorphisms[k] = f"H^{dimension}(S^{dimension}) ≅ ℤ ≅ H_0(S^{dimension})"
                else:
                    duality_isomorphisms[k] = f"H^{k}(S^{dimension}) ≅ 0 ≅ H_{dimension-k}(S^{dimension})"

            return {
                'manifold': manifold,
                'dimension': dimension,
                'duality_isomorphisms': duality_isomorphisms,
                'explanation': f"Poincaré duality for S^{dimension}: H^k ≅ H_{{{dimension}-k}}",
                'theorem': 'Poincaré Duality Theorem',
                'note': 'Requires closed oriented manifold'
            }

        if 'torus' in manifold or manifold == 't2':
            # T^2: H^k(T^2) ≅ H_{2-k}(T^2)
            # H^0(T^2) ≅ ℤ ≅ H_2(T^2)
            # H^1(T^2) ≅ ℤ^2 ≅ H_1(T^2)
            # H^2(T^2) ≅ ℤ ≅ H_0(T^2)
            duality_isomorphisms = {
                0: "H^0(T^2) ≅ ℤ ≅ H_2(T^2)",
                1: "H^1(T^2) ≅ ℤ^2 ≅ H_1(T^2) (self-dual)",
                2: "H^2(T^2) ≅ ℤ ≅ H_0(T^2)"
            }

            return {
                'manifold': manifold,
                'dimension': 2,
                'duality_isomorphisms': duality_isomorphisms,
                'explanation': "Poincaré duality for torus T^2",
                'theorem': 'Poincaré Duality Theorem',
                'note': 'H^1 is self-dual (1 = 2-1)'
            }

        # Generic response
        return {
            'manifold': manifold,
            'dimension': dimension,
            'duality': f"H^k(M) ≅ H_{{{dimension}-k}}(M) for 0 ≤ k ≤ {dimension}",
            'explanation': "Poincaré duality exchanges cohomology and homology dimensions",
            'theorem': 'Poincaré Duality Theorem',
            'requirements': [
                'M is closed (compact without boundary)',
                'M is oriented',
                'M is n-dimensional manifold'
            ],
            'note': 'Fundamental result relating cohomology and homology'
        }

    def compute_cohomology_ring_structure(
        self,
        space: str
    ) -> Dict[str, Any]:
        """
        Compute cohomology ring structure H*(X) with cup product

        Args:
            space: Space description

        Returns:
            Dict containing:
                - ring_structure: Description of H*(X) as ring
                - generators: Ring generators
                - relations: Ring relations
                - explanation: Description
        """
        space = space.lower()

        # Known cohomology rings
        known_rings = {
            'circle': {
                'structure': 'ℤ[α]/(α^2)',
                'generators': {'α': 'generator of H^1(S¹) ≅ ℤ'},
                'relations': {'α^2 = 0': 'H^2(S¹) = 0'},
                'grading': {'H^0': 'ℤ', 'H^1': 'ℤ', 'H^k': '0 for k > 1'},
                'description': 'Polynomial ring truncated at degree 2'
            },
            's1': {
                'structure': 'ℤ[α]/(α^2)',
                'generators': {'α': 'generator of H^1(S¹) ≅ ℤ'},
                'relations': {'α^2 = 0': 'H^2(S¹) = 0'},
                'grading': {'H^0': 'ℤ', 'H^1': 'ℤ', 'H^k': '0 for k > 1'},
                'description': 'Polynomial ring truncated at degree 2'
            },
            'sphere': {
                'structure': 'ℤ[x]/(x^2) where x ∈ H^n(S^n)',
                'generators': {'1': 'unit in H^0', 'x': 'generator of H^n(S^n)'},
                'relations': {'x^2 = 0': 'Cup product vanishes'},
                'grading': {'H^0': 'ℤ', 'H^n': 'ℤ', 'H^k': '0 otherwise'},
                'description': 'Two-element ring: 1 and volume form'
            },
            's2': {
                'structure': 'ℤ[x]/(x^2) where x ∈ H^2(S^2)',
                'generators': {'1': 'unit in H^0', 'x': 'generator of H^2(S^2)'},
                'relations': {'x^2 = 0': 'H^4(S^2) = 0'},
                'grading': {'H^0': 'ℤ', 'H^2': 'ℤ', 'H^k': '0 otherwise'},
                'description': 'Two-element ring: 1 and surface form'
            },
            'torus': {
                'structure': 'ℤ[α, β]/(α^2 = 0, β^2 = 0) with αβ = -βα',
                'generators': {'α': 'H^1 generator', 'β': 'H^1 generator'},
                'relations': {'αβ ≠ 0': 'αβ generates H^2(T^2) ≅ ℤ'},
                'grading': {'H^0': 'ℤ', 'H^1': 'ℤ^2', 'H^2': 'ℤ'},
                'description': 'Exterior algebra on 2 generators'
            },
            't2': {
                'structure': 'ℤ[α, β]/(α^2 = 0, β^2 = 0) with αβ = -βα',
                'generators': {'α': 'H^1 generator', 'β': 'H^1 generator'},
                'relations': {'αβ ≠ 0': 'αβ generates H^2(T^2) ≅ ℤ'},
                'grading': {'H^0': 'ℤ', 'H^1': 'ℤ^2', 'H^2': 'ℤ'},
                'description': 'Exterior algebra on 2 generators'
            },
            'rp2': {
                'structure': 'ℤ[α]/(2α, α^2) where α ∈ H^1(ℝP^2)',
                'generators': {'α': 'generator of H^1(ℝP^2) ≅ ℤ/2ℤ'},
                'relations': {'2α = 0': 'torsion', 'α^2 = 0': 'H^2(ℝP^2) = 0'},
                'grading': {'H^0': 'ℤ', 'H^1': 'ℤ/2ℤ', 'H^2': '0'},
                'description': 'Torsion in cohomology ring'
            }
        }

        if space in known_rings:
            data = known_rings[space]
            return {
                'space': space,
                'cohomology_ring': data['structure'],
                'generators': data['generators'],
                'relations': data['relations'],
                'grading': data['grading'],
                'explanation': data['description'],
                'cup_product': 'Ring multiplication given by cup product ∪',
                'note': 'H*(X) is graded commutative ring'
            }

        return {
            'space': space,
            'cohomology_ring': 'unknown',
            'explanation': f"Cohomology ring H*({space}) requires specific computation",
            'note': 'Cup product ∪ gives ring structure to H*(X)'
        }

    def compute_characteristic_classes(
        self,
        vector_bundle: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute characteristic classes for vector bundle

        Characteristic classes: Chern classes (complex), Stiefel-Whitney (real)

        Args:
            vector_bundle: Dict describing vector bundle

        Returns:
            Dict containing:
                - characteristic_classes: Classes computed
                - explanation: Description
        """
        bundle_type = vector_bundle.get('type', 'real')
        base_space = vector_bundle.get('base', 'unknown')
        rank = vector_bundle.get('rank', 1)

        if bundle_type == 'complex':
            # Chern classes c_i ∈ H^{2i}(B)
            classes = {}
            for i in range(rank + 1):
                if i == 0:
                    classes[f'c_0'] = f"c_0 = 1 ∈ H^0({base_space})"
                else:
                    classes[f'c_{i}'] = f"c_{i} ∈ H^{2*i}({base_space})"

            return {
                'vector_bundle': 'complex',
                'base_space': base_space,
                'rank': rank,
                'characteristic_classes': classes,
                'type': 'Chern classes',
                'total_chern_class': f"c(E) = c_0 + c_1 + ... + c_{rank} ∈ H*({base_space})",
                'explanation': f"Chern classes for rank-{rank} complex bundle",
                'properties': ['c_0 = 1', 'naturality', 'additivity'],
                'note': 'Chern classes live in even-dimensional cohomology'
            }
        else:
            # Stiefel-Whitney classes w_i ∈ H^i(B; ℤ/2ℤ)
            classes = {}
            for i in range(rank + 1):
                if i == 0:
                    classes[f'w_0'] = f"w_0 = 1 ∈ H^0({base_space}; ℤ/2ℤ)"
                else:
                    classes[f'w_{i}'] = f"w_{i} ∈ H^{i}({base_space}; ℤ/2ℤ)"

            return {
                'vector_bundle': 'real',
                'base_space': base_space,
                'rank': rank,
                'characteristic_classes': classes,
                'type': 'Stiefel-Whitney classes',
                'total_sw_class': f"w(E) = w_0 + w_1 + ... + w_{rank} ∈ H*({base_space}; ℤ/2ℤ)",
                'explanation': f"Stiefel-Whitney classes for rank-{rank} real bundle",
                'properties': ['w_0 = 1', 'naturality', 'w_1 detects orientability'],
                'note': 'SW classes with ℤ/2ℤ coefficients'
            }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new cohomology problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Optimize cache if too many entries
        if self.tasks_executed > 100 and len(self.cohomology_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old cohomology cache entries'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            # Keep only recent cache entries
            if len(self.cohomology_cache) > 50:
                # Clear half of cache
                keys = list(self.cohomology_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.cohomology_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.cohomology_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
