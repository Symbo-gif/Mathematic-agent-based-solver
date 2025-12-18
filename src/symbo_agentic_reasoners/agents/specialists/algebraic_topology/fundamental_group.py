# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
FUNDAMENTAL GROUP SPECIALIST - π₁ computation, van Kampen, covering spaces
===========================================================================

Manages tasks related to fundamental group computation and covering space theory.

CRITICAL ALGORITHMS:
-------------------
- Fundamental Group Presentation: π₁(X) = <generators | relations>
- Seifert-van Kampen Theorem: Computing π₁ of unions
- Covering Space Classification: Covering spaces via π₁
- Deck Transformations: Symmetries of coverings
- Simply Connected Test: π₁(X) = 0?
- Abelianization: π₁^ab = H₁(X)

WHY THIS MATTERS:
----------------
Fundamental group is fundamental to:
- Classification of covering spaces
- Loop space structure
- Galois theory of covering spaces
- Obstruction theory

CAPABILITIES:
------------
- Compute fundamental group presentations
- Apply van Kampen theorem
- Classify covering spaces
- Compute deck transformation groups
- Test simple connectivity
- Compute abelianization
"""

from typing import Dict, Any, List, Optional, Tuple
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class FundamentalGroupSpecialist(BDIAgent):
    """
    Fundamental Group Specialist - π₁ computation, van Kampen, covering spaces

    DIRECTIVE:
    ---------
    Handle all fundamental group operations with emphasis on:
    - π₁ presentation computation
    - van Kampen theorem application
    - Covering space classification
    - Deck transformations

    KEY ALGORITHMS:
    --------------
    - π₁ Presentation: <generators | relations>
    - Van Kampen: π₁(X ∪ Y) from π₁(X), π₁(Y), π₁(X ∩ Y)
    - Covering Classification: Subgroups of π₁(X) ↔ coverings

    OPERATIONS:
    ----------
    - compute_fundamental_group_presentation(space)
    - apply_van_kampen_theorem(spaces)
    - compute_covering_space_classification(base_space)
    - compute_deck_transformations(covering)
    - check_simply_connected(space)
    - compute_abelianization(group_presentation)
    """

    def __init__(self, agent_id='fundamental_group_specialist_001', df=None, blackboard=None):
        """
        Initialize Fundamental Group Specialist

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
        self.pi1_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.algebraictopology.fundamentalgroup',
                agent_id=self.agent_id,
                algorithm='fundamental_group',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process fundamental group task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of fundamental group operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'presentation')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'presentation':
                return self._process_presentation(metadata)
            elif problem_type == 'van_kampen':
                return self._process_van_kampen(metadata)
            elif problem_type == 'covering_classification':
                return self._process_covering_classification(metadata)
            elif problem_type == 'deck_transformations':
                return self._process_deck_transformations(metadata)
            elif problem_type == 'simply_connected':
                return self._process_simply_connected(metadata)
            elif problem_type == 'abelianization':
                return self._process_abelianization(metadata)
            else:
                return self._process_presentation(metadata)

        except Exception as e:
            return {
                'operation': 'fundamental group',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_presentation(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process fundamental group presentation computation"""
        space = metadata.get('space', 'circle')

        result = self.compute_fundamental_group_presentation(space)
        return {
            'operation': 'fundamental_group_presentation',
            **result
        }

    def _process_van_kampen(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process van Kampen theorem application"""
        spaces = metadata.get('spaces', [])

        result = self.apply_van_kampen_theorem(spaces)
        return {
            'operation': 'van_kampen_theorem',
            **result
        }

    def _process_covering_classification(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process covering space classification"""
        base_space = metadata.get('base_space', 'circle')

        result = self.compute_covering_space_classification(base_space)
        return {
            'operation': 'covering_space_classification',
            **result
        }

    def _process_deck_transformations(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process deck transformations computation"""
        covering = metadata.get('covering', {})

        result = self.compute_deck_transformations(covering)
        return {
            'operation': 'deck_transformations',
            **result
        }

    def _process_simply_connected(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process simply connected test"""
        space = metadata.get('space', 'sphere')

        result = self.check_simply_connected(space)
        return {
            'operation': 'simply_connected_test',
            **result
        }

    def _process_abelianization(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process abelianization computation"""
        group_presentation = metadata.get('group_presentation', {})

        result = self.compute_abelianization(group_presentation)
        return {
            'operation': 'abelianization',
            **result
        }

    def compute_fundamental_group_presentation(
        self,
        space: str
    ) -> Dict[str, Any]:
        """
        Compute fundamental group presentation π₁(X) = <generators | relations>

        Args:
            space: Space description

        Returns:
            Dict containing:
                - presentation: Group presentation
                - generators: List of generators
                - relations: List of relations
                - explanation: Description
        """
        space = space.lower()

        # Known fundamental groups with presentations
        known_presentations = {
            'circle': {
                'presentation': '<a | >',
                'generators': ['a'],
                'relations': [],
                'group': 'ℤ',
                'description': 'Free group on 1 generator (infinite cyclic)'
            },
            's1': {
                'presentation': '<a | >',
                'generators': ['a'],
                'relations': [],
                'group': 'ℤ',
                'description': 'Free group on 1 generator'
            },
            'sphere': {
                'presentation': '<>',
                'generators': [],
                'relations': [],
                'group': '0',
                'description': 'Trivial group (simply connected)'
            },
            's2': {
                'presentation': '<>',
                'generators': [],
                'relations': [],
                'group': '0',
                'description': 'Trivial group'
            },
            'torus': {
                'presentation': '<a, b | aba⁻¹b⁻¹ = 1>',
                'generators': ['a', 'b'],
                'relations': ['[a,b] = 1'],
                'group': 'ℤ × ℤ',
                'description': 'Abelian: generators commute'
            },
            't2': {
                'presentation': '<a, b | [a,b] = 1>',
                'generators': ['a', 'b'],
                'relations': ['aba⁻¹b⁻¹ = 1'],
                'group': 'ℤ × ℤ',
                'description': 'Fundamental group of 2-torus'
            },
            'rp2': {
                'presentation': '<a | a² = 1>',
                'generators': ['a'],
                'relations': ['a² = 1'],
                'group': 'ℤ/2ℤ',
                'description': 'Cyclic group of order 2'
            },
            'klein_bottle': {
                'presentation': '<a, b | aba⁻¹b = 1>',
                'generators': ['a', 'b'],
                'relations': ['aba⁻¹b = 1'],
                'group': 'Non-abelian',
                'description': 'Klein bottle group (non-abelian)'
            },
            'figure_eight': {
                'presentation': '<a, b | >',
                'generators': ['a', 'b'],
                'relations': [],
                'group': 'F₂ (free group on 2 generators)',
                'description': 'Free group: wedge of two circles'
            },
            'genus_2': {
                'presentation': '<a₁, b₁, a₂, b₂ | [a₁,b₁][a₂,b₂] = 1>',
                'generators': ['a₁', 'b₁', 'a₂', 'b₂'],
                'relations': ['[a₁,b₁][a₂,b₂] = 1'],
                'group': 'Surface group of genus 2',
                'description': 'Orientable surface of genus 2'
            }
        }

        if space in known_presentations:
            data = known_presentations[space]
            return {
                'space': space,
                'presentation': data['presentation'],
                'generators': data['generators'],
                'relations': data['relations'],
                'fundamental_group': data['group'],
                'explanation': data['description'],
                'note': 'Presentation: π₁(X) = <generators | relations>'
            }

        return {
            'space': space,
            'presentation': 'unknown',
            'explanation': f"Fundamental group presentation for {space} requires computation",
            'note': 'Use Seifert-van Kampen for decomposable spaces'
        }

    def apply_van_kampen_theorem(
        self,
        spaces: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply Seifert-van Kampen theorem to compute π₁(X ∪ Y)

        Theorem: If X = U ∪ V with U, V path-connected open and U ∩ V path-connected:
        π₁(X) = π₁(U) *_{π₁(U∩V)} π₁(V) (amalgamated free product)

        Args:
            spaces: List of space descriptions with π₁ info

        Returns:
            Dict containing:
                - fundamental_group: π₁(X ∪ Y)
                - explanation: How theorem applied
        """
        if len(spaces) < 2:
            return {
                'error': 'Need at least 2 spaces for van Kampen',
                'explanation': 'Van Kampen: π₁(X ∪ Y) from π₁(X), π₁(Y), π₁(X ∩ Y)'
            }

        space1 = spaces[0]
        space2 = spaces[1]
        intersection = spaces[2] if len(spaces) > 2 else {'pi1': '0'}

        pi1_u = space1.get('pi1', 'unknown')
        pi1_v = space2.get('pi1', 'unknown')
        pi1_int = intersection.get('pi1', '0')

        # Trivial intersection (simply connected)
        if pi1_int == '0':
            if pi1_u == '0':
                result_group = pi1_v
            elif pi1_v == '0':
                result_group = pi1_u
            else:
                result_group = f"{pi1_u} * {pi1_v}"

            return {
                'fundamental_group': result_group,
                'space1_pi1': pi1_u,
                'space2_pi1': pi1_v,
                'intersection_pi1': pi1_int,
                'explanation': f"π₁(X ∪ Y) = {result_group} (free product)",
                'theorem': 'Seifert-van Kampen with trivial intersection',
                'note': 'Simply connected intersection gives free product'
            }

        # Non-trivial intersection
        return {
            'fundamental_group': f"{pi1_u} *_{{{pi1_int}}} {pi1_v}",
            'space1_pi1': pi1_u,
            'space2_pi1': pi1_v,
            'intersection_pi1': pi1_int,
            'explanation': f"π₁(X ∪ Y) = {pi1_u} *_{{{pi1_int}}} {pi1_v}",
            'theorem': 'Seifert-van Kampen theorem',
            'note': 'Amalgamated free product over intersection'
        }

    def compute_covering_space_classification(
        self,
        base_space: str
    ) -> Dict[str, Any]:
        """
        Classify covering spaces of base_space via fundamental group

        Classification: Covering spaces of X ↔ subgroups of π₁(X)

        Args:
            base_space: Base space

        Returns:
            Dict containing:
                - coverings: Classification of coverings
                - explanation: Description
        """
        base = base_space.lower()

        # Compute π₁
        pi1_result = self.compute_fundamental_group_presentation(base)
        pi1 = pi1_result.get('fundamental_group', 'unknown')

        # Known classifications
        if base in ['circle', 's1']:
            # Coverings of S¹: S¹ → S¹ (degree n map), ℝ → S¹ (universal cover)
            return {
                'base_space': base,
                'fundamental_group': 'ℤ',
                'coverings': {
                    'universal': {'total': 'ℝ', 'sheets': '∞', 'group': '0'},
                    'n_fold': {'total': 'S¹', 'sheets': 'n', 'group': 'nℤ ⊂ ℤ'}
                },
                'explanation': "Coverings of S¹ classified by subgroups of ℤ",
                'note': 'Each subgroup nℤ corresponds to n-fold covering S¹ → S¹',
                'galois_correspondence': 'Subgroups of π₁(X) ↔ covering spaces'
            }

        if base in ['sphere', 's2']:
            # S² is simply connected - only trivial covering
            return {
                'base_space': base,
                'fundamental_group': '0',
                'coverings': {
                    'trivial': {'total': 'S²', 'sheets': '1', 'group': '0'}
                },
                'explanation': "S² has only trivial covering (itself)",
                'note': 'Simply connected spaces have no non-trivial coverings'
            }

        if base in ['torus', 't2']:
            # T² has π₁ = ℤ × ℤ, many coverings
            return {
                'base_space': base,
                'fundamental_group': 'ℤ × ℤ',
                'coverings': {
                    'universal': {'total': 'ℝ²', 'sheets': '∞', 'group': '0'},
                    'intermediate': {'total': 'T² or cylinder', 'sheets': 'finite', 'group': 'subgroup of ℤ×ℤ'}
                },
                'explanation': "Coverings of T² classified by subgroups of ℤ × ℤ",
                'note': 'Rich variety of intermediate coverings'
            }

        return {
            'base_space': base_space,
            'fundamental_group': pi1,
            'explanation': f"Coverings of {base_space} classified by subgroups of π₁",
            'theorem': 'Galois correspondence: subgroups ↔ coverings',
            'note': 'Universal cover has trivial π₁'
        }

    def compute_deck_transformations(
        self,
        covering: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute deck transformation group Aut(p) for covering p: E → B

        Deck transformations: homeomorphisms of E commuting with projection p

        Args:
            covering: Dict describing covering space

        Returns:
            Dict containing:
                - deck_group: Deck transformation group
                - explanation: Description
        """
        total = covering.get('total', 'unknown')
        base = covering.get('base', 'unknown')
        sheets = covering.get('sheets', 'unknown')

        # Special cases
        if base.lower() in ['circle', 's1'] and total.lower() in ['r', 'real_line']:
            # Universal cover ℝ → S¹
            return {
                'covering': f"{total} → {base}",
                'deck_group': 'ℤ',
                'generators': ['translation by 1'],
                'action': 'Deck(ℝ → S¹) = ℤ acting by integer translations',
                'explanation': 'Universal cover: deck group = π₁(base)',
                'note': 'For universal cover: Deck(p) ≅ π₁(B)'
            }

        if base.lower() in ['circle', 's1'] and total.lower() in ['circle', 's1']:
            # n-fold covering S¹ → S¹
            return {
                'covering': f"S¹ → S¹ (degree {sheets})",
                'deck_group': f'ℤ/{sheets}ℤ',
                'generators': [f'rotation by 2π/{sheets}'],
                'action': f'Cyclic group of order {sheets}',
                'explanation': f'Deck group for {sheets}-fold covering',
                'note': 'Deck(p) = quotient π₁(B) / π₁(E)'
            }

        # Generic
        return {
            'covering': f"{total} → {base}",
            'deck_group': 'Deck(p)',
            'explanation': "Deck transformations form a group",
            'theorem': 'For universal cover: Deck(p) ≅ π₁(B)',
            'note': 'In general: Deck(p) ≅ N(π₁(E)) / π₁(E) where N = normalizer'
        }

    def check_simply_connected(
        self,
        space: str
    ) -> Dict[str, Any]:
        """
        Check if space is simply connected (π₁(X) = 0)

        Args:
            space: Space description

        Returns:
            Dict containing:
                - simply_connected: Boolean
                - explanation: Justification
        """
        pi1_result = self.compute_fundamental_group_presentation(space)
        pi1 = pi1_result.get('fundamental_group', 'unknown')

        is_simply_connected = (pi1 == '0')

        if is_simply_connected:
            return {
                'space': space,
                'simply_connected': True,
                'fundamental_group': '0',
                'explanation': f"{space} is simply connected: π₁ = 0",
                'examples': 'Simply connected spaces: Sⁿ (n≥2), ℝⁿ, balls, contractible spaces',
                'note': 'Simply connected = path-connected + π₁ = 0'
            }
        elif pi1 != 'unknown':
            return {
                'space': space,
                'simply_connected': False,
                'fundamental_group': pi1,
                'explanation': f"{space} is NOT simply connected: π₁ = {pi1}",
                'note': 'Non-trivial fundamental group'
            }
        else:
            return {
                'space': space,
                'simply_connected': None,
                'fundamental_group': 'unknown',
                'explanation': f"Need to compute π₁({space}) to determine simple connectivity"
            }

    def compute_abelianization(
        self,
        group_presentation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute abelianization π₁^ab = π₁ / [π₁, π₁]

        Abelianization: largest abelian quotient of group
        Theorem: π₁(X)^ab ≅ H₁(X)

        Args:
            group_presentation: Group presentation

        Returns:
            Dict containing:
                - abelianization: π₁^ab
                - explanation: Description
        """
        generators = group_presentation.get('generators', [])
        relations = group_presentation.get('relations', [])
        group = group_presentation.get('group', 'unknown')

        # Known abelianizations
        if group == 'ℤ':
            return {
                'abelianization': 'ℤ',
                'group': group,
                'explanation': 'ℤ is already abelian: ℤ^ab = ℤ',
                'note': 'Abelian groups are their own abelianization'
            }

        if group == 'ℤ × ℤ':
            return {
                'abelianization': 'ℤ × ℤ',
                'group': group,
                'explanation': 'ℤ × ℤ is already abelian',
                'note': 'Torus fundamental group is abelian'
            }

        if group == 'ℤ/2ℤ':
            return {
                'abelianization': 'ℤ/2ℤ',
                'group': group,
                'explanation': 'Cyclic groups are abelian',
                'note': 'ℝP² fundamental group'
            }

        if group == 'F₂ (free group on 2 generators)':
            return {
                'abelianization': 'ℤ × ℤ',
                'group': group,
                'explanation': 'F₂^ab = ℤ × ℤ (free abelian on 2 generators)',
                'note': 'Abelianization kills commutators'
            }

        if 'klein' in group.lower() or 'aba⁻¹b' in str(relations):
            return {
                'abelianization': 'ℤ × ℤ/2ℤ',
                'group': 'Klein bottle group',
                'explanation': 'Klein bottle: π₁^ab = ℤ ⊕ ℤ/2ℤ',
                'note': 'Non-abelian group with mixed abelianization'
            }

        # Generic
        return {
            'abelianization': 'π₁^ab',
            'group': group,
            'explanation': "Abelianization: quotient by commutator subgroup",
            'theorem': 'π₁(X)^ab ≅ H₁(X) (Hurewicz theorem)',
            'note': 'Abelianization makes group commutative'
        }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []
        if self.tasks_executed > 100 and len(self.pi1_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old π₁ cache entries'
            ))
        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            if len(self.pi1_cache) > 50:
                keys = list(self.pi1_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.pi1_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.pi1_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
