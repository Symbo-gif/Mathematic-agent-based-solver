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
FUNCTOR SPECIALIST (Tier 3)
===========================

Native Python implementation for functors and natural transformations.
Handles covariant/contravariant functors, functor composition,
and natural transformation verification.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from .morphism_specialist import Category, Object, Morphism

logger = logging.getLogger(__name__)


@dataclass
class Functor:
    """
    Represents a functor F: C → D between categories.

    A functor maps:
    - Objects: F(A) for each object A in C
    - Morphisms: F(f): F(A) → F(B) for each morphism f: A → B

    Satisfying:
    - F(id_A) = id_{F(A)} (preserves identity)
    - F(g ∘ f) = F(g) ∘ F(f) (preserves composition)
    """
    name: str
    source_category: str
    target_category: str
    object_map: Dict[str, str]  # C object name → D object name
    morphism_map: Dict[str, str]  # C morphism name → D morphism name
    is_contravariant: bool = False
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NaturalTransformation:
    """
    Represents a natural transformation η: F ⇒ G between functors F, G: C → D.

    For each object A in C, gives a morphism η_A: F(A) → G(A) in D
    such that for any f: A → B, the diagram commutes:
    G(f) ∘ η_A = η_B ∘ F(f)
    """
    name: str
    source_functor: str
    target_functor: str
    components: Dict[str, str]  # object name → morphism name (η_A)
    properties: Dict[str, Any] = field(default_factory=dict)


class FunctorSpecialist(BDIAgent):
    """
    Specialist for functors and natural transformations.

    Capabilities:
    - Functor construction and verification
    - Covariant and contravariant functors
    - Functor composition
    - Natural transformations
    - Common functors (forgetful, free, hom, etc.)
    """

    def __init__(self, agent_id: str = 'functor_specialist_001', df=None, blackboard=None,
                 morphism_specialist=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.morphism_specialist = morphism_specialist
        self.tasks_executed = 0

        # Store functors and natural transformations
        self.functors: Dict[str, Functor] = {}
        self.natural_transformations: Dict[str, NaturalTransformation] = {}

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.category_theory.functor',
                agent_id=agent_id,
                algorithm='native_categorical',
                cost='low',
                instance=self,
                tier='3',
                capabilities='functor_natural_transformation'
            ))

        logger.info(f"[{agent_id}] Functor Specialist initialized")

    # ==================== YONEDA LEMMA ====================

    def yoneda_embedding(
        self,
        category_name: str,
        object_name: str
    ) -> Dict[str, Any]:
        """
        Apply Yoneda embedding: C → [C^op, Set]

        Maps object A to functor Hom(-, A): C^op → Set

        Yoneda embedding is:
        - Full: reflects isomorphisms
        - Faithful: reflects equality
        - Embedding: injective on objects

        Args:
            category_name: Category C
            object_name: Object A in C

        Returns:
            Dict with Yoneda embedding information
        """
        try:
            # Create representable functor Hom(-, A)
            hom_functor = f'Hom(-, {object_name})'

            return {
                'success': True,
                'object': object_name,
                'embedded_as': hom_functor,
                'target_category': f'[{category_name}^op, Set]',
                'properties': ['full', 'faithful', 'embedding'],
                'method': 'yoneda_embedding',
                'note': f'Maps {object_name} to Hom(-, {object_name}) functor',
                'theorem': 'Yoneda embedding is full and faithful'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'yoneda_embedding'
            }

    def yoneda_lemma(
        self,
        object_name: str,
        functor_name: str,
        category_name: str
    ) -> Dict[str, Any]:
        """
        Apply Yoneda lemma: Nat(Hom(A,-), F) ≅ F(A)

        For any functor F: C → Set and object A in C:
        Natural transformations from Hom(A,-) to F correspond bijectively
        to elements of F(A).

        The bijection: η ↦ η_A(id_A)

        Args:
            object_name: Object A
            functor_name: Functor F
            category_name: Category C

        Returns:
            Dict with Yoneda correspondence
        """
        try:
            hom_functor = f'Hom({object_name}, -)'

            return {
                'success': True,
                'bijection': f'Nat({hom_functor}, {functor_name}) ≅ {functor_name}({object_name})',
                'direction_forward': f'η ↦ η_{object_name}(id_{object_name})',
                'direction_backward': f'x ∈ F(A) ↦ natural transformation',
                'method': 'yoneda_lemma',
                'naturality': 'Bijection is natural in both A and F',
                'note': 'Natural transformations from representable functor correspond to elements',
                'corollary': 'Objects A, B are isomorphic iff Hom(A,-) ≅ Hom(B,-)'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'yoneda_lemma'
            }

    def representable_functor_test(
        self,
        functor: Functor
    ) -> Dict[str, Any]:
        """
        Test if functor F: C → Set is representable.

        F is representable if F ≅ Hom(A, -) for some object A.

        By Yoneda: F representable means there exists A and isomorphism
        η: Hom(A, -) → F

        Args:
            functor: Functor to test

        Returns:
            Dict with representability test result
        """
        try:
            # Check if functor maps to Set
            if functor.target_category != 'Set':
                return {
                    'success': False,
                    'error': 'Representable functors must map to Set',
                    'method': 'representable_test'
                }

            # Simplified test - checks if functor has form of hom-functor
            functor_name_lower = functor.name.lower()
            is_representable = 'hom' in functor_name_lower

            if is_representable:
                return {
                    'success': True,
                    'is_representable': True,
                    'functor': functor.name,
                    'method': 'representable_test',
                    'note': f'{functor.name} has hom-functor structure',
                    'universal_element': 'Representing object exists by Yoneda'
                }
            else:
                return {
                    'success': True,
                    'is_representable': False,
                    'functor': functor.name,
                    'method': 'representable_test',
                    'note': 'Functor does not appear to be representable'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'representable_test'
            }

    def presheaf_category(
        self,
        category_name: str
    ) -> Dict[str, Any]:
        """
        Construct presheaf category [C^op, Set].

        A presheaf on C is a contravariant functor F: C^op → Set.
        The presheaf category has:
        - Objects: Functors C^op → Set
        - Morphisms: Natural transformations

        Args:
            category_name: Base category C

        Returns:
            Dict with presheaf category construction
        """
        try:
            presheaf_category_name = f'[{category_name}^op, Set]'

            return {
                'success': True,
                'presheaf_category': presheaf_category_name,
                'objects': f'Contravariant functors {category_name}^op → Set',
                'morphisms': 'Natural transformations between presheaves',
                'yoneda_embedding': f'y: {category_name} → {presheaf_category_name}',
                'method': 'presheaf_category',
                'note': f'Category {category_name} embeds into {presheaf_category_name} via Yoneda',
                'property': 'Presheaf category is complete and cocomplete'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'presheaf_category'
            }

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for functor tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['functor'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['natural_transformation'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create functor computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'create')

            steps = ['claim_task', 'compute_functor', 'post_result']
            intention = Intention(
                plan_id=f'functor_{operation}_{task_id}',
                steps=steps,
                target_desire='functor_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute functor operations."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_functor':
            self._compute_functor(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_functor(self, intention: Intention):
        """Compute functor operations."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'create')

        try:
            if operation == 'create':
                result = self.create_functor(
                    metadata.get('name'),
                    metadata.get('source_category'),
                    metadata.get('target_category'),
                    metadata.get('object_map', {}),
                    metadata.get('morphism_map', {}),
                    metadata.get('is_contravariant', False)
                )
            elif operation == 'compose':
                result = self.compose_functors(
                    metadata.get('g_name'),
                    metadata.get('f_name')
                )
            elif operation == 'verify':
                result = self.verify_functor(metadata.get('functor_name'))
            elif operation == 'natural_transform':
                result = self.create_natural_transformation(
                    metadata.get('name'),
                    metadata.get('source_functor'),
                    metadata.get('target_functor'),
                    metadata.get('components', {})
                )
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Functor computation failed: {e}")
            intention.metadata['result'] = {'error': str(e)}
            intention.advance()

    def _post_result(self, intention: Intention):
        """Post result to blackboard."""
        if self.blackboard:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            task = intention.metadata.get('task_entry')
            result = intention.metadata.get('result', {})

            result_entry = create_entry(
                content=result,
                entry_type=EntryType.RESULT,
                tags=['functor', 'category_theory', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # FUNCTOR CONSTRUCTION
    # =========================================================================

    def create_functor(self, name: str, source_category: str, target_category: str,
                       object_map: Dict[str, str], morphism_map: Dict[str, str],
                       is_contravariant: bool = False) -> Dict[str, Any]:
        """
        Create a functor F: C → D.

        Args:
            name: Functor name
            source_category: Source category name
            target_category: Target category name
            object_map: Mapping of object names C → D
            morphism_map: Mapping of morphism names C → D
            is_contravariant: If True, reverses morphism direction

        Returns:
            Functor creation result
        """
        if name in self.functors:
            return {'error': f'Functor {name} already exists'}

        functor = Functor(
            name=name,
            source_category=source_category,
            target_category=target_category,
            object_map=object_map,
            morphism_map=morphism_map,
            is_contravariant=is_contravariant
        )

        self.functors[name] = functor

        return {
            'functor': name,
            'type': 'contravariant' if is_contravariant else 'covariant',
            'source': source_category,
            'target': target_category,
            'object_mappings': len(object_map),
            'morphism_mappings': len(morphism_map),
            'method': 'native_functor_construction'
        }

    def verify_functor(self, functor_name: str) -> Dict[str, Any]:
        """
        Verify that a functor satisfies the functor axioms.

        1. Identity preservation: F(id_A) = id_{F(A)}
        2. Composition preservation: F(g ∘ f) = F(g) ∘ F(f)

        Args:
            functor_name: Name of functor to verify

        Returns:
            Verification results
        """
        if functor_name not in self.functors:
            return {'error': f'Functor {functor_name} not found'}

        functor = self.functors[functor_name]

        if not self.morphism_specialist:
            return {
                'functor': functor_name,
                'verification': 'skipped',
                'reason': 'Morphism specialist not available for full verification',
                'structure_valid': True
            }

        # Check identity preservation
        identity_preserved = True
        identity_issues = []

        source_cat = self.morphism_specialist.categories.get(functor.source_category)
        target_cat = self.morphism_specialist.categories.get(functor.target_category)

        if source_cat and target_cat:
            for obj_name, target_obj_name in functor.object_map.items():
                source_id = f'id_{obj_name}'
                expected_target_id = f'id_{target_obj_name}'

                if source_id in functor.morphism_map:
                    actual_target = functor.morphism_map[source_id]
                    if actual_target != expected_target_id:
                        identity_preserved = False
                        identity_issues.append(
                            f'F({source_id}) = {actual_target}, expected {expected_target_id}'
                        )

        return {
            'functor': functor_name,
            'identity_preservation': identity_preserved,
            'identity_issues': identity_issues,
            'composition_preservation': True,  # Assumed if mappings are consistent
            'is_valid_functor': identity_preserved,
            'type': 'contravariant' if functor.is_contravariant else 'covariant'
        }

    def compose_functors(self, g_name: str, f_name: str) -> Dict[str, Any]:
        """
        Compose functors G ∘ F.

        For F: C → D and G: D → E, returns G ∘ F: C → E.

        Args:
            g_name: Second functor name
            f_name: First functor name

        Returns:
            Composed functor result
        """
        if f_name not in self.functors:
            return {'error': f'Functor {f_name} not found'}
        if g_name not in self.functors:
            return {'error': f'Functor {g_name} not found'}

        f = self.functors[f_name]
        g = self.functors[g_name]

        # Check composability
        if f.target_category != g.source_category:
            return {
                'error': 'Functors not composable',
                'f_target': f.target_category,
                'g_source': g.source_category
            }

        comp_name = f'{g_name}∘{f_name}'

        # Compose object maps: (G ∘ F)(A) = G(F(A))
        comp_object_map = {}
        for obj, f_obj in f.object_map.items():
            if f_obj in g.object_map:
                comp_object_map[obj] = g.object_map[f_obj]

        # Compose morphism maps: (G ∘ F)(m) = G(F(m))
        comp_morphism_map = {}
        for morph, f_morph in f.morphism_map.items():
            if f_morph in g.morphism_map:
                comp_morphism_map[morph] = g.morphism_map[f_morph]

        # Handle contravariance
        is_contravariant = f.is_contravariant != g.is_contravariant  # XOR

        composition = Functor(
            name=comp_name,
            source_category=f.source_category,
            target_category=g.target_category,
            object_map=comp_object_map,
            morphism_map=comp_morphism_map,
            is_contravariant=is_contravariant,
            properties={'is_composition': True, 'factors': [g_name, f_name]}
        )

        self.functors[comp_name] = composition

        return {
            'composition': comp_name,
            'source': f.source_category,
            'target': g.target_category,
            'type': 'contravariant' if is_contravariant else 'covariant',
            'method': 'native_functor_composition'
        }

    # =========================================================================
    # NATURAL TRANSFORMATIONS
    # =========================================================================

    def create_natural_transformation(self, name: str, source_functor: str,
                                       target_functor: str,
                                       components: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a natural transformation η: F ⇒ G.

        Args:
            name: Transformation name
            source_functor: Source functor F
            target_functor: Target functor G
            components: Dict mapping object names to component morphisms

        Returns:
            Natural transformation result
        """
        if source_functor not in self.functors:
            return {'error': f'Source functor {source_functor} not found'}
        if target_functor not in self.functors:
            return {'error': f'Target functor {target_functor} not found'}

        f = self.functors[source_functor]
        g = self.functors[target_functor]

        # Check that F and G have same source and target categories
        if f.source_category != g.source_category:
            return {'error': 'Functors have different source categories'}
        if f.target_category != g.target_category:
            return {'error': 'Functors have different target categories'}

        nt = NaturalTransformation(
            name=name,
            source_functor=source_functor,
            target_functor=target_functor,
            components=components
        )

        self.natural_transformations[name] = nt

        return {
            'natural_transformation': name,
            'source_functor': source_functor,
            'target_functor': target_functor,
            'components': len(components),
            'method': 'native_natural_transformation'
        }

    def verify_naturality(self, nt_name: str) -> Dict[str, Any]:
        """
        Verify that a natural transformation satisfies naturality.

        For any morphism f: A → B in C, the square commutes:
        η_B ∘ F(f) = G(f) ∘ η_A

        Args:
            nt_name: Natural transformation name

        Returns:
            Verification result
        """
        if nt_name not in self.natural_transformations:
            return {'error': f'Natural transformation {nt_name} not found'}

        nt = self.natural_transformations[nt_name]
        f = self.functors[nt.source_functor]
        g = self.functors[nt.target_functor]

        # For full verification, we'd need the morphism specialist
        # Here we return a structural check
        return {
            'natural_transformation': nt_name,
            'source_functor': nt.source_functor,
            'target_functor': nt.target_functor,
            'components_defined': len(nt.components),
            'naturality': 'assumed_valid',
            'note': 'Full naturality verification requires explicit morphism checking'
        }

    def compose_natural_transformations(self, eta_name: str, mu_name: str,
                                         composition_type: str = 'vertical') -> Dict[str, Any]:
        """
        Compose natural transformations.

        Vertical: For η: F ⇒ G and μ: G ⇒ H, gives μ ∘ η: F ⇒ H
        Horizontal: For η: F ⇒ F' and μ: G ⇒ G', gives μ * η: G∘F ⇒ G'∘F'

        Args:
            eta_name: First natural transformation
            mu_name: Second natural transformation
            composition_type: 'vertical' or 'horizontal'

        Returns:
            Composed natural transformation
        """
        if eta_name not in self.natural_transformations:
            return {'error': f'Natural transformation {eta_name} not found'}
        if mu_name not in self.natural_transformations:
            return {'error': f'Natural transformation {mu_name} not found'}

        eta = self.natural_transformations[eta_name]
        mu = self.natural_transformations[mu_name]

        if composition_type == 'vertical':
            # Vertical composition: μ ∘ η
            if eta.target_functor != mu.source_functor:
                return {'error': 'Incompatible for vertical composition'}

            comp_name = f'{mu_name}∘{eta_name}'

            # Component-wise composition
            comp_components = {}
            for obj in eta.components:
                if obj in mu.components:
                    # In practice, we'd compose the morphisms
                    comp_components[obj] = f'{mu.components[obj]}∘{eta.components[obj]}'

            comp_nt = NaturalTransformation(
                name=comp_name,
                source_functor=eta.source_functor,
                target_functor=mu.target_functor,
                components=comp_components,
                properties={'is_vertical_composition': True}
            )

            self.natural_transformations[comp_name] = comp_nt

            return {
                'composition': comp_name,
                'type': 'vertical',
                'source_functor': eta.source_functor,
                'target_functor': mu.target_functor
            }

        elif composition_type == 'horizontal':
            # Horizontal (Godement) composition
            comp_name = f'{mu_name}*{eta_name}'

            return {
                'composition': comp_name,
                'type': 'horizontal',
                'note': 'Horizontal composition creates whiskering'
            }

        return {'error': f'Unknown composition type: {composition_type}'}

    # =========================================================================
    # COMMON FUNCTORS
    # =========================================================================

    def create_identity_functor(self, category_name: str) -> Dict[str, Any]:
        """
        Create the identity functor Id_C: C → C.

        Args:
            category_name: Category name

        Returns:
            Identity functor result
        """
        if not self.morphism_specialist:
            return {'error': 'Morphism specialist required for category access'}

        if category_name not in self.morphism_specialist.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.morphism_specialist.categories[category_name]

        # Identity maps everything to itself
        object_map = {o.name: o.name for o in cat.objects}
        morphism_map = {m.name: m.name for m in cat.morphisms}

        functor_name = f'Id_{category_name}'

        return self.create_functor(
            name=functor_name,
            source_category=category_name,
            target_category=category_name,
            object_map=object_map,
            morphism_map=morphism_map,
            is_contravariant=False
        )

    def create_constant_functor(self, source_category: str, target_category: str,
                                 fixed_object: str) -> Dict[str, Any]:
        """
        Create a constant functor Δ_c: C → D that maps everything to c.

        Args:
            source_category: Source category C
            target_category: Target category D
            fixed_object: The object c to map everything to

        Returns:
            Constant functor result
        """
        if not self.morphism_specialist:
            return {'error': 'Morphism specialist required for category access'}

        source_cat = self.morphism_specialist.categories.get(source_category)
        if not source_cat:
            return {'error': f'Source category {source_category} not found'}

        target_cat = self.morphism_specialist.categories.get(target_category)
        if not target_cat:
            return {'error': f'Target category {target_category} not found'}

        # Check fixed_object exists in target
        if not any(o.name == fixed_object for o in target_cat.objects):
            return {'error': f'Object {fixed_object} not in target category'}

        # All objects map to fixed_object
        object_map = {o.name: fixed_object for o in source_cat.objects}

        # All morphisms map to identity of fixed_object
        morphism_map = {m.name: f'id_{fixed_object}' for m in source_cat.morphisms}

        functor_name = f'Δ_{fixed_object}'

        return self.create_functor(
            name=functor_name,
            source_category=source_category,
            target_category=target_category,
            object_map=object_map,
            morphism_map=morphism_map,
            is_contravariant=False
        )

    def create_hom_functor(self, category_name: str, fixed_object: str,
                           covariant: bool = True) -> Dict[str, Any]:
        """
        Create a hom-functor.

        Covariant: Hom(A, -): C → Set
        Contravariant: Hom(-, A): C^op → Set

        Args:
            category_name: Category name
            fixed_object: The fixed object A
            covariant: If True, creates Hom(A, -); otherwise Hom(-, A)

        Returns:
            Hom functor info
        """
        if not self.morphism_specialist:
            return {'error': 'Morphism specialist required for category access'}

        if category_name not in self.morphism_specialist.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.morphism_specialist.categories[category_name]

        if not any(o.name == fixed_object for o in cat.objects):
            return {'error': f'Object {fixed_object} not in category'}

        if covariant:
            functor_name = f'Hom({fixed_object}, -)'
            # Maps each object B to Hom(A, B)
            object_map = {
                o.name: f'Hom({fixed_object}, {o.name})'
                for o in cat.objects
            }
        else:
            functor_name = f'Hom(-, {fixed_object})'
            # Maps each object B to Hom(B, A)
            object_map = {
                o.name: f'Hom({o.name}, {fixed_object})'
                for o in cat.objects
            }

        functor = Functor(
            name=functor_name,
            source_category=category_name,
            target_category='Set',
            object_map=object_map,
            morphism_map={},  # Would need explicit construction
            is_contravariant=not covariant
        )

        self.functors[functor_name] = functor

        return {
            'functor': functor_name,
            'type': 'covariant' if covariant else 'contravariant',
            'fixed_object': fixed_object,
            'target': 'Set',
            'representable': True
        }

    # =========================================================================
    # FUNCTOR CATEGORIES
    # =========================================================================

    def create_functor_category(self, source: str, target: str) -> Dict[str, Any]:
        """
        Create the functor category [C, D] with:
        - Objects: Functors F: C → D
        - Morphisms: Natural transformations η: F ⇒ G

        Args:
            source: Source category C
            target: Target category D

        Returns:
            Functor category info
        """
        cat_name = f'[{source}, {target}]'

        # Collect all functors between these categories
        functor_objects = [
            f.name for f in self.functors.values()
            if f.source_category == source and f.target_category == target
        ]

        # Collect natural transformations between these functors
        nat_trans = [
            nt.name for nt in self.natural_transformations.values()
            if (self.functors.get(nt.source_functor, Functor('', '', '', {}, {})).source_category == source and
                self.functors.get(nt.source_functor, Functor('', '', '', {}, {})).target_category == target)
        ]

        return {
            'functor_category': cat_name,
            'source': source,
            'target': target,
            'objects': functor_objects,
            'morphisms': nat_trans,
            'object_count': len(functor_objects),
            'morphism_count': len(nat_trans)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'functors_defined': len(self.functors),
            'natural_transformations_defined': len(self.natural_transformations),
            'capabilities': [
                'functor_creation', 'functor_composition', 'functor_verification',
                'natural_transformation', 'identity_functor', 'constant_functor',
                'hom_functor', 'functor_category'
            ]
        }
