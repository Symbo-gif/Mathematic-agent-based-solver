# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
HOMOTOPY SPECIALIST - Homotopy groups, fibrations, homotopy equivalence
======================================================================

Manages tasks related to homotopy theory, continuous deformations, and homotopy groups.

CRITICAL ALGORITHMS:
-------------------
- Fundamental Group Computation: π₁(X) for standard spaces
- Higher Homotopy Groups: πₙ(X) for n > 1
- Seifert-van Kampen Theorem: Computing π₁ of unions
- Fibration Sequences: Long exact sequence in homotopy
- Homotopy Equivalence: Testing homotopy type
- Whitehead Product: [f, g] in homotopy groups

WHY THIS MATTERS:
----------------
Homotopy theory is fundamental to:
- Understanding continuous deformations
- Classification of spaces up to homotopy
- Obstruction theory and bundle theory
- Algebraic topology and K-theory

CAPABILITIES:
------------
- Compute fundamental groups of standard spaces
- Apply Seifert-van Kampen theorem
- Compute higher homotopy groups
- Analyze fibrations and long exact sequences
- Check homotopy equivalence
- Compute Whitehead products
- Classify homotopy types
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
import numpy as np


class HomotopySpecialist(BDIAgent):
    """
    Homotopy Specialist - Homotopy groups, fibrations, homotopy equivalence

    DIRECTIVE:
    ---------
    Handle all homotopy theory operations with emphasis on:
    - Fundamental group computations
    - Higher homotopy groups
    - Homotopy equivalence testing
    - Fibration sequences

    KEY ALGORITHMS:
    --------------
    - π₁ Computation: Fundamental group for standard spaces
    - Van Kampen: Combine fundamental groups via pushout
    - Higher Homotopy: πₙ(X) for n > 1

    OPERATIONS:
    ----------
    - compute_fundamental_group(space_description)
    - compute_higher_homotopy_group(space, n)
    - apply_seifert_van_kampen(spaces, intersection)
    - compute_fibration_sequence(base, fiber, total)
    - check_homotopy_equivalence(space1, space2)
    - compute_whitehead_product(map1, map2)
    - classify_homotopy_type(space)
    """

    def __init__(self, agent_id='homotopy_specialist_001', df=None, blackboard=None):
        """
        Initialize Homotopy Specialist

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
        self.homotopy_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.algebraictopology.homotopy',
                agent_id=self.agent_id,
                algorithm='homotopy',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process homotopy task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of homotopy operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'fundamental_group')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'fundamental_group':
                return self._process_fundamental_group(metadata)
            elif problem_type == 'higher_homotopy':
                return self._process_higher_homotopy(metadata)
            elif problem_type == 'van_kampen':
                return self._process_van_kampen(metadata)
            elif problem_type == 'fibration':
                return self._process_fibration(metadata)
            elif problem_type == 'homotopy_equivalence':
                return self._process_homotopy_equivalence(metadata)
            elif problem_type == 'whitehead_product':
                return self._process_whitehead_product(metadata)
            elif problem_type == 'classify':
                return self._process_classify(metadata)
            else:
                return self._process_fundamental_group(metadata)

        except Exception as e:
            return {
                'operation': 'homotopy',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_fundamental_group(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process fundamental group computation request"""
        space_description = metadata.get('space', 'circle')
        basepoint = metadata.get('basepoint', '*')

        result = self.compute_fundamental_group(space_description, basepoint)
        return {
            'operation': 'fundamental_group',
            **result
        }

    def _process_higher_homotopy(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process higher homotopy group computation request"""
        space = metadata.get('space', 'sphere')
        n = metadata.get('n', 2)

        result = self.compute_higher_homotopy_group(space, n)
        return {
            'operation': 'higher_homotopy_group',
            **result
        }

    def _process_van_kampen(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Seifert-van Kampen theorem application"""
        spaces = metadata.get('spaces', [])
        intersection = metadata.get('intersection', {})

        result = self.apply_seifert_van_kampen(spaces, intersection)
        return {
            'operation': 'seifert_van_kampen',
            **result
        }

    def _process_fibration(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process fibration sequence computation"""
        base = metadata.get('base', 'sphere')
        fiber = metadata.get('fiber', 'sphere')
        total = metadata.get('total', 'unknown')

        result = self.compute_fibration_sequence(base, fiber, total)
        return {
            'operation': 'fibration_sequence',
            **result
        }

    def _process_homotopy_equivalence(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process homotopy equivalence check"""
        space1 = metadata.get('space1', 'circle')
        space2 = metadata.get('space2', 'circle')

        result = self.check_homotopy_equivalence(space1, space2)
        return {
            'operation': 'homotopy_equivalence',
            **result
        }

    def _process_whitehead_product(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Whitehead product computation"""
        map1 = metadata.get('map1', {})
        map2 = metadata.get('map2', {})

        result = self.compute_whitehead_product(map1, map2)
        return {
            'operation': 'whitehead_product',
            **result
        }

    def _process_classify(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process homotopy type classification"""
        space = metadata.get('space', 'unknown')

        result = self.classify_homotopy_type(space)
        return {
            'operation': 'classify_homotopy_type',
            **result
        }

    def compute_fundamental_group(
        self,
        space_description: str,
        basepoint: str = '*'
    ) -> Dict[str, Any]:
        """
        Compute fundamental group π₁(X, x₀)

        Args:
            space_description: Description of topological space
            basepoint: Base point for fundamental group

        Returns:
            Dict containing:
                - group: Presentation of π₁(X)
                - abelianization: H₁(X)
                - is_trivial: Whether π₁(X) = 0
                - explanation: Description
        """
        space = space_description.lower()

        # Known fundamental groups
        known_groups = {
            'circle': {'group': 'Z', 'abelianization': 'Z', 'is_trivial': False,
                      'presentation': '<a | >', 'description': 'π₁(S¹) = ℤ (infinite cyclic)'},
            's1': {'group': 'Z', 'abelianization': 'Z', 'is_trivial': False,
                   'presentation': '<a | >', 'description': 'π₁(S¹) = ℤ'},
            'sphere': {'group': '0', 'abelianization': '0', 'is_trivial': True,
                      'presentation': '<>', 'description': 'π₁(S²) = 0 (simply connected)'},
            's2': {'group': '0', 'abelianization': '0', 'is_trivial': True,
                   'presentation': '<>', 'description': 'π₁(S²) = 0'},
            'torus': {'group': 'Z × Z', 'abelianization': 'Z × Z', 'is_trivial': False,
                     'presentation': '<a, b | ab = ba>', 'description': 'π₁(T²) = ℤ × ℤ (abelian)'},
            't2': {'group': 'Z × Z', 'abelianization': 'Z × Z', 'is_trivial': False,
                   'presentation': '<a, b | ab = ba>', 'description': 'π₁(T²) = ℤ × ℤ'},
            'real_projective_plane': {'group': 'Z/2Z', 'abelianization': 'Z/2Z', 'is_trivial': False,
                                     'presentation': '<a | a² = 1>', 'description': 'π₁(ℝP²) = ℤ/2ℤ'},
            'rp2': {'group': 'Z/2Z', 'abelianization': 'Z/2Z', 'is_trivial': False,
                    'presentation': '<a | a² = 1>', 'description': 'π₁(ℝP²) = ℤ/2ℤ'},
            'klein_bottle': {'group': '<a, b | aba⁻¹b = 1>', 'abelianization': 'Z × Z/2Z',
                           'is_trivial': False, 'presentation': '<a, b | aba⁻¹b = 1>',
                           'description': 'π₁(Klein bottle) = <a, b | aba⁻¹b = 1>'},
            'figure_eight': {'group': 'F₂', 'abelianization': 'Z × Z', 'is_trivial': False,
                           'presentation': '<a, b | >', 'description': 'π₁(S¹ ∨ S¹) = ℤ * ℤ (free group on 2 generators)'},
        }

        if space in known_groups:
            data = known_groups[space]
            return {
                'space': space_description,
                'fundamental_group': data['group'],
                'presentation': data['presentation'],
                'abelianization': data['abelianization'],
                'is_trivial': data['is_trivial'],
                'is_simply_connected': data['is_trivial'],
                'explanation': data['description'],
                'basepoint': basepoint
            }

        # Generic response
        return {
            'space': space_description,
            'fundamental_group': 'unknown',
            'presentation': 'unknown',
            'is_trivial': None,
            'explanation': f"Fundamental group π₁({space_description}) requires specific computation",
            'note': 'Use Seifert-van Kampen for decomposable spaces'
        }

    def compute_higher_homotopy_group(
        self,
        space: str,
        n: int
    ) -> Dict[str, Any]:
        """
        Compute higher homotopy group πₙ(X) for n > 1

        Args:
            space: Description of topological space
            n: Dimension of homotopy group

        Returns:
            Dict containing:
                - group: πₙ(X)
                - is_trivial: Whether πₙ(X) = 0
                - explanation: Description
        """
        space = space.lower()

        # Known higher homotopy groups
        if 'sphere' in space or space.startswith('s'):
            # Extract dimension from space name (e.g., 's2' -> 2)
            try:
                if space == 'sphere':
                    dim = 2  # Default to S²
                else:
                    dim = int(space.replace('sphere', '').replace('s', ''))
            except:
                dim = 2

            if n < dim:
                return {
                    'space': space,
                    'n': n,
                    'homotopy_group': '0',
                    'is_trivial': True,
                    'explanation': f"πₙ(Sᵐ) = 0 for n < m (by Freudenthal suspension theorem)",
                    'note': 'Spheres are n-connected'
                }
            elif n == dim:
                return {
                    'space': space,
                    'n': n,
                    'homotopy_group': 'Z',
                    'is_trivial': False,
                    'explanation': f"πₙ(Sⁿ) = ℤ generated by identity map",
                    'note': 'Degree of map Sⁿ → Sⁿ'
                }
            else:
                # Known stable homotopy groups
                if dim == 2 and n == 3:
                    return {
                        'space': space,
                        'n': n,
                        'homotopy_group': 'Z',
                        'is_trivial': False,
                        'explanation': "π₃(S²) = ℤ (Hopf fibration)",
                        'note': 'Generated by Hopf map η: S³ → S²'
                    }
                elif dim == 3 and n == 3:
                    return {
                        'space': space,
                        'n': n,
                        'homotopy_group': 'Z',
                        'is_trivial': False,
                        'explanation': "π₃(S³) = ℤ",
                        'note': 'Identity map generator'
                    }
                else:
                    return {
                        'space': space,
                        'n': n,
                        'homotopy_group': 'unknown',
                        'is_trivial': None,
                        'explanation': f"πₙ(Sᵐ) for n > m is highly non-trivial",
                        'note': 'Stable homotopy groups are deep results in algebraic topology'
                    }

        return {
            'space': space,
            'n': n,
            'homotopy_group': 'unknown',
            'explanation': f"Higher homotopy group π_{n}({space}) requires specific computation",
            'note': 'Higher homotopy groups are generally difficult to compute'
        }

    def apply_seifert_van_kampen(
        self,
        spaces: List[Dict[str, Any]],
        intersection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply Seifert-van Kampen theorem to compute π₁(X ∪ Y)

        Theorem: If X = U ∪ V where U, V are path-connected open sets,
        and U ∩ V is path-connected, then:
        π₁(X) = π₁(U) *_{π₁(U∩V)} π₁(V) (amalgamated free product)

        Args:
            spaces: List of space descriptions with π₁
            intersection: Description of intersection

        Returns:
            Dict containing:
                - fundamental_group: π₁(X ∪ Y)
                - explanation: How theorem was applied
        """
        if len(spaces) < 2:
            return {
                'error': 'Need at least 2 spaces for van Kampen theorem',
                'explanation': 'Van Kampen computes π₁(X ∪ Y) from π₁(X), π₁(Y), π₁(X ∩ Y)'
            }

        space1 = spaces[0]
        space2 = spaces[1]

        # Get fundamental groups
        pi1_space1 = space1.get('pi1', 'unknown')
        pi1_space2 = space2.get('pi1', 'unknown')
        pi1_intersection = intersection.get('pi1', '0')

        # Special cases
        if pi1_intersection == '0':
            # Simply connected intersection - free product
            if pi1_space1 == '0':
                result_group = pi1_space2
            elif pi1_space2 == '0':
                result_group = pi1_space1
            elif pi1_space1 == 'Z' and pi1_space2 == 'Z':
                result_group = 'Z * Z (free group on 2 generators)'
            else:
                result_group = f"{pi1_space1} * {pi1_space2}"

            return {
                'fundamental_group': result_group,
                'space1_group': pi1_space1,
                'space2_group': pi1_space2,
                'intersection_group': pi1_intersection,
                'explanation': f"π₁(X ∪ Y) = {pi1_space1} * {pi1_space2} (free product, since intersection is simply connected)",
                'theorem': 'Seifert-van Kampen with trivial intersection'
            }

        # General case - amalgamated free product
        return {
            'fundamental_group': f"{pi1_space1} *_{{pi1_intersection}} {pi1_space2}",
            'space1_group': pi1_space1,
            'space2_group': pi1_space2,
            'intersection_group': pi1_intersection,
            'explanation': f"π₁(X ∪ Y) = {pi1_space1} *_{{{pi1_intersection}}} {pi1_space2} (amalgamated free product)",
            'theorem': 'Seifert-van Kampen theorem',
            'note': 'Amalgamated product identifies elements coming from intersection'
        }

    def compute_fibration_sequence(
        self,
        base: str,
        fiber: str,
        total: str = 'unknown'
    ) -> Dict[str, Any]:
        """
        Compute long exact sequence in homotopy for fibration F → E → B

        Long exact sequence:
        ... → πₙ(F) → πₙ(E) → πₙ(B) → πₙ₋₁(F) → ...

        Args:
            base: Base space B
            fiber: Fiber F
            total: Total space E

        Returns:
            Dict containing:
                - sequence: Long exact sequence
                - explanation: Description
        """
        # Known fibrations
        if 'hopf' in total.lower() or (fiber == 's1' and base == 's2'):
            # Hopf fibration S¹ → S³ → S²
            return {
                'fibration': 'Hopf fibration',
                'fiber': 'S¹',
                'total': 'S³',
                'base': 'S²',
                'long_exact_sequence': [
                    'π₃(S¹) = 0 → π₃(S³) = ℤ → π₃(S²) = ℤ → π₂(S¹) = 0',
                    'π₂(S³) = 0 → π₂(S²) = ℤ → π₁(S¹) = ℤ → π₁(S³) = 0'
                ],
                'explanation': 'Hopf fibration: S¹ → S³ → S² generates π₃(S²) = ℤ',
                'note': 'This shows π₃(S²) ≅ ℤ (first non-trivial higher homotopy group)'
            }

        # Generic fibration
        return {
            'fibration': f"{fiber} → {total} → {base}",
            'fiber': fiber,
            'total': total,
            'base': base,
            'long_exact_sequence': f"... → πₙ({fiber}) → πₙ({total}) → πₙ({base}) → πₙ₋₁({fiber}) → ...",
            'explanation': 'Long exact sequence in homotopy for fibration',
            'note': 'Compute specific groups by chasing diagram'
        }

    def check_homotopy_equivalence(
        self,
        space1: str,
        space2: str
    ) -> Dict[str, Any]:
        """
        Check if two spaces are homotopy equivalent

        Spaces X, Y are homotopy equivalent if there exist maps f: X → Y and g: Y → X
        such that g ∘ f ≃ id_X and f ∘ g ≃ id_Y

        Args:
            space1: First space
            space2: Second space

        Returns:
            Dict containing:
                - equivalent: Boolean or None
                - explanation: Justification
        """
        s1, s2 = space1.lower(), space2.lower()

        # Exact match
        if s1 == s2:
            return {
                'space1': space1,
                'space2': space2,
                'homotopy_equivalent': True,
                'explanation': f"{space1} and {space2} are the same space",
                'homotopy_type': space1
            }

        # Contractible spaces
        contractible = ['point', 'disk', 'ball', 'contractible']
        if s1 in contractible and s2 in contractible:
            return {
                'space1': space1,
                'space2': space2,
                'homotopy_equivalent': True,
                'explanation': 'Both spaces are contractible (homotopy equivalent to a point)',
                'homotopy_type': 'point'
            }

        # Known equivalences
        equivalences = {
            ('circle', 's1'): True,
            ('torus', 't2'): True,
            ('sphere', 's2'): True,
            ('mobius_strip', 'circle'): True,
            ('cylinder', 'circle'): True,
            ('solid_torus', 'circle'): True,
        }

        pair = (s1, s2) if (s1, s2) in equivalences else (s2, s1)
        if pair in equivalences:
            return {
                'space1': space1,
                'space2': space2,
                'homotopy_equivalent': True,
                'explanation': f"{space1} and {space2} are known to be homotopy equivalent",
                'note': 'Homotopy equivalence preserves all homotopy groups'
            }

        # Check via homotopy groups (necessary but not sufficient)
        pi1_s1 = self.compute_fundamental_group(s1)
        pi1_s2 = self.compute_fundamental_group(s2)

        if pi1_s1['fundamental_group'] != pi1_s2['fundamental_group']:
            return {
                'space1': space1,
                'space2': space2,
                'homotopy_equivalent': False,
                'explanation': f"Different fundamental groups: π₁({space1}) = {pi1_s1['fundamental_group']}, π₁({space2}) = {pi1_s2['fundamental_group']}",
                'note': 'Homotopy equivalence would preserve π₁'
            }

        return {
            'space1': space1,
            'space2': space2,
            'homotopy_equivalent': None,
            'explanation': 'Cannot determine homotopy equivalence from given information',
            'note': 'Need to check all homotopy groups (necessary) or find explicit maps (sufficient)'
        }

    def compute_whitehead_product(
        self,
        map1: Dict[str, Any],
        map2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute Whitehead product [α, β] ∈ πₚ₊ᵧ₋₁(X)

        For α ∈ πₚ(X) and β ∈ πᵧ(X), the Whitehead product [α, β] ∈ πₚ₊ᵧ₋₁(X)
        measures the failure of α and β to commute up to homotopy.

        Args:
            map1: First map α ∈ πₚ(X)
            map2: Second map β ∈ πᵧ(X)

        Returns:
            Dict containing:
                - whitehead_product: Description of [α, β]
                - dimension: p + q - 1
                - explanation: Description
        """
        p = map1.get('dimension', 2)
        q = map2.get('dimension', 2)
        space = map1.get('space', 'unknown')

        product_dim = p + q - 1

        # Special case: commuting elements
        if map1.get('commutes_with', []) and map2.get('name', '') in map1.get('commutes_with', []):
            return {
                'whitehead_product': '0',
                'dimension': product_dim,
                'is_trivial': True,
                'explanation': f"[α, β] = 0 since α and β commute up to homotopy",
                'note': 'Whitehead product measures non-commutativity'
            }

        return {
            'whitehead_product': f"[α, β] ∈ π_{{{product_dim}}}({space})",
            'dimension': product_dim,
            'map1_dimension': p,
            'map2_dimension': q,
            'explanation': f"Whitehead product of maps in π_{p} and π_{q} gives element in π_{product_dim}",
            'note': 'Whitehead products generate the graded Lie algebra structure on homotopy groups',
            'anticommutativity': '[α, β] = -(-1)^{pq}[β, α]'
        }

    def classify_homotopy_type(
        self,
        space: str
    ) -> Dict[str, Any]:
        """
        Classify homotopy type of space

        Args:
            space: Space description

        Returns:
            Dict containing:
                - homotopy_type: Classification
                - invariants: Homotopy invariants
                - explanation: Description
        """
        space = space.lower()

        # Compute invariants
        pi1 = self.compute_fundamental_group(space)

        # Contractible
        if pi1['is_trivial']:
            if space in ['sphere', 's2', 's3']:
                return {
                    'space': space,
                    'homotopy_type': 'simply-connected',
                    'fundamental_group': '0',
                    'classification': f"Higher homotopy groups determine type",
                    'explanation': f"{space} is simply connected",
                    'note': 'Need higher homotopy groups for full classification'
                }

        # Eilenberg-MacLane spaces K(G, n)
        if space in ['circle', 's1']:
            return {
                'space': space,
                'homotopy_type': 'K(ℤ, 1)',
                'fundamental_group': 'Z',
                'classification': 'Eilenberg-MacLane space K(ℤ, 1)',
                'explanation': 'Circle is K(ℤ, 1): π₁ = ℤ, πₙ = 0 for n > 1',
                'note': 'Classifying space for ℤ-bundles'
            }

        return {
            'space': space,
            'homotopy_type': 'undetermined',
            'fundamental_group': pi1['fundamental_group'],
            'explanation': f"Homotopy type determined by all πₙ({space})",
            'note': 'Full classification requires computing all homotopy groups'
        }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new homotopy problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Optimize cache if too many entries
        if self.tasks_executed > 100 and len(self.homotopy_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old homotopy cache entries'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            # Keep only recent cache entries
            if len(self.homotopy_cache) > 50:
                # Clear half of cache
                keys = list(self.homotopy_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.homotopy_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.homotopy_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
