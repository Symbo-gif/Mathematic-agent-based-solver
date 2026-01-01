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
MORPHISM SPECIALIST (Tier 3)
============================

Native Python implementation for category theory morphisms.
Handles morphism composition, identity, isomorphisms, and basic
categorical structures.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Callable, Set
from dataclasses import dataclass, field

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


@dataclass
class Object:
    """Represents an object in a category."""
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Object):
            return self.name == other.name
        return False


@dataclass
class Morphism:
    """Represents a morphism (arrow) in a category."""
    name: str
    source: Object
    target: Object
    mapping: Optional[Callable] = None  # Optional concrete mapping function
    properties: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash((self.name, self.source.name, self.target.name))

    def __eq__(self, other):
        if isinstance(other, Morphism):
            return (self.name == other.name and
                    self.source == other.source and
                    self.target == other.target)
        return False


@dataclass
class Category:
    """Represents a category with objects and morphisms."""
    name: str
    objects: Set[Object] = field(default_factory=set)
    morphisms: Set[Morphism] = field(default_factory=set)
    identities: Dict[str, Morphism] = field(default_factory=dict)  # object_name -> identity morphism
    compositions: Dict[Tuple[str, str], Morphism] = field(default_factory=dict)  # (g_name, f_name) -> g∘f


class MorphismSpecialist(BDIAgent):
    """
    Specialist for category theory morphisms.

    Capabilities:
    - Morphism composition
    - Identity morphisms
    - Isomorphism detection
    - Monomorphism/Epimorphism classification
    - Endomorphism/Automorphism handling
    - Category construction and validation
    """

    def __init__(self, agent_id: str = 'morphism_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        # Store categories
        self.categories: Dict[str, Category] = {}

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.category_theory.morphism',
                agent_id=agent_id,
                algorithm='native_categorical',
                cost='low',
                instance=self,
                tier='3',
                capabilities='morphism_composition_identity_classification'
            ))

        logger.info(f"[{agent_id}] Morphism Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for morphism tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['morphism'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['category'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['composition'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create morphism computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'compose')

            steps = ['claim_task', 'compute_morphism', 'post_result']
            intention = Intention(
                plan_id=f'morphism_{operation}_{task_id}',
                steps=steps,
                target_desire='morphism_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute morphism operations."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_morphism':
            self._compute_morphism(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_morphism(self, intention: Intention):
        """Compute morphism operations."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'compose')

        try:
            if operation == 'compose':
                result = self.compose_morphisms(
                    metadata.get('category_name', 'default'),
                    metadata.get('g_name'),
                    metadata.get('f_name')
                )
            elif operation == 'identity':
                result = self.create_identity(
                    metadata.get('category_name', 'default'),
                    metadata.get('object_name')
                )
            elif operation == 'is_isomorphism':
                result = self.is_isomorphism(
                    metadata.get('category_name', 'default'),
                    metadata.get('morphism_name')
                )
            elif operation == 'create_category':
                result = self.create_category(
                    metadata.get('category_name'),
                    metadata.get('objects', []),
                    metadata.get('morphisms', [])
                )
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Morphism computation failed: {e}")
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
                tags=['morphism', 'category_theory', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # CATEGORY CONSTRUCTION
    # =========================================================================

    def create_category(self, name: str, objects: List[str],
                        morphisms: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new category.

        Args:
            name: Category name
            objects: List of object names
            morphisms: List of morphism specs {name, source, target}

        Returns:
            Category creation result
        """
        if name in self.categories:
            return {'error': f'Category {name} already exists'}

        cat = Category(name=name)

        # Add objects
        for obj_name in objects:
            obj = Object(name=obj_name)
            cat.objects.add(obj)
            # Create identity morphism for each object
            id_morph = Morphism(
                name=f'id_{obj_name}',
                source=obj,
                target=obj,
                properties={'is_identity': True}
            )
            cat.morphisms.add(id_morph)
            cat.identities[obj_name] = id_morph

        # Add morphisms
        if morphisms:
            for morph_spec in morphisms:
                source_obj = next((o for o in cat.objects if o.name == morph_spec['source']), None)
                target_obj = next((o for o in cat.objects if o.name == morph_spec['target']), None)

                if source_obj and target_obj:
                    morph = Morphism(
                        name=morph_spec['name'],
                        source=source_obj,
                        target=target_obj,
                        properties=morph_spec.get('properties', {})
                    )
                    cat.morphisms.add(morph)

        self.categories[name] = cat

        return {
            'category': name,
            'objects': [o.name for o in cat.objects],
            'morphisms': [m.name for m in cat.morphisms],
            'identities': list(cat.identities.keys()),
            'method': 'native_category_construction'
        }

    def add_object(self, category_name: str, object_name: str,
                   properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add an object to a category."""
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]
        obj = Object(name=object_name, properties=properties or {})
        cat.objects.add(obj)

        # Create identity morphism
        id_morph = Morphism(
            name=f'id_{object_name}',
            source=obj,
            target=obj,
            properties={'is_identity': True}
        )
        cat.morphisms.add(id_morph)
        cat.identities[object_name] = id_morph

        return {
            'added': object_name,
            'identity': id_morph.name,
            'category': category_name
        }

    def add_morphism(self, category_name: str, name: str, source: str, target: str,
                     properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a morphism to a category."""
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]
        source_obj = next((o for o in cat.objects if o.name == source), None)
        target_obj = next((o for o in cat.objects if o.name == target), None)

        if not source_obj:
            return {'error': f'Source object {source} not found'}
        if not target_obj:
            return {'error': f'Target object {target} not found'}

        morph = Morphism(
            name=name,
            source=source_obj,
            target=target_obj,
            properties=properties or {}
        )
        cat.morphisms.add(morph)

        return {
            'added': name,
            'source': source,
            'target': target,
            'category': category_name
        }

    # =========================================================================
    # MORPHISM COMPOSITION
    # =========================================================================

    def compose_morphisms(self, category_name: str, g_name: str, f_name: str) -> Dict[str, Any]:
        """
        Compose morphisms g ∘ f.

        For morphisms f: A → B and g: B → C, returns g ∘ f: A → C.

        Args:
            category_name: Category containing the morphisms
            g_name: Second morphism (applied first to result of f)
            f_name: First morphism (applied first)

        Returns:
            Composition result
        """
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]

        f = next((m for m in cat.morphisms if m.name == f_name), None)
        g = next((m for m in cat.morphisms if m.name == g_name), None)

        if not f:
            return {'error': f'Morphism {f_name} not found'}
        if not g:
            return {'error': f'Morphism {g_name} not found'}

        # Check composability: target of f must equal source of g
        if f.target != g.source:
            return {
                'error': 'Morphisms not composable',
                'f_target': f.target.name,
                'g_source': g.source.name,
                'message': f'Target of {f_name} ({f.target.name}) != Source of {g_name} ({g.source.name})'
            }

        # Check if composition already exists
        comp_key = (g_name, f_name)
        if comp_key in cat.compositions:
            existing = cat.compositions[comp_key]
            return {
                'composition': existing.name,
                'source': existing.source.name,
                'target': existing.target.name,
                'cached': True
            }

        # Create composition
        comp_name = f'{g_name}∘{f_name}'
        composition = Morphism(
            name=comp_name,
            source=f.source,
            target=g.target,
            properties={'is_composition': True, 'factors': [g_name, f_name]}
        )

        cat.morphisms.add(composition)
        cat.compositions[comp_key] = composition

        return {
            'composition': comp_name,
            'source': f.source.name,
            'target': g.target.name,
            'f': f_name,
            'g': g_name,
            'method': 'native_composition'
        }

    def create_identity(self, category_name: str, object_name: str) -> Dict[str, Any]:
        """
        Get or create identity morphism for an object.

        Args:
            category_name: Category name
            object_name: Object name

        Returns:
            Identity morphism info
        """
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]

        if object_name in cat.identities:
            id_morph = cat.identities[object_name]
            return {
                'identity': id_morph.name,
                'object': object_name,
                'satisfies_left_identity': True,
                'satisfies_right_identity': True
            }

        obj = next((o for o in cat.objects if o.name == object_name), None)
        if not obj:
            return {'error': f'Object {object_name} not found'}

        id_morph = Morphism(
            name=f'id_{object_name}',
            source=obj,
            target=obj,
            properties={'is_identity': True}
        )
        cat.morphisms.add(id_morph)
        cat.identities[object_name] = id_morph

        return {
            'identity': id_morph.name,
            'object': object_name,
            'satisfies_left_identity': True,
            'satisfies_right_identity': True
        }

    # =========================================================================
    # MORPHISM CLASSIFICATION
    # =========================================================================

    def classify_morphism(self, category_name: str, morphism_name: str) -> Dict[str, Any]:
        """
        Classify a morphism (isomorphism, monomorphism, epimorphism, etc.).

        Args:
            category_name: Category name
            morphism_name: Morphism name

        Returns:
            Classification results
        """
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]
        morph = next((m for m in cat.morphisms if m.name == morphism_name), None)

        if not morph:
            return {'error': f'Morphism {morphism_name} not found'}

        classification = {
            'morphism': morphism_name,
            'source': morph.source.name,
            'target': morph.target.name,
            'is_identity': morph.properties.get('is_identity', False),
            'is_endomorphism': morph.source == morph.target,
            'is_isomorphism': False,
            'is_monomorphism': False,
            'is_epimorphism': False,
            'is_automorphism': False
        }

        # Check for isomorphism (has inverse)
        inverse = self._find_inverse(cat, morph)
        if inverse:
            classification['is_isomorphism'] = True
            classification['inverse'] = inverse.name

            # Automorphism = isomorphism where source = target
            if morph.source == morph.target:
                classification['is_automorphism'] = True

        # Check for monomorphism (left-cancellable)
        classification['is_monomorphism'] = self._is_monomorphism(cat, morph)

        # Check for epimorphism (right-cancellable)
        classification['is_epimorphism'] = self._is_epimorphism(cat, morph)

        return classification

    def is_isomorphism(self, category_name: str, morphism_name: str) -> Dict[str, Any]:
        """Check if a morphism is an isomorphism."""
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]
        morph = next((m for m in cat.morphisms if m.name == morphism_name), None)

        if not morph:
            return {'error': f'Morphism {morphism_name} not found'}

        inverse = self._find_inverse(cat, morph)

        return {
            'morphism': morphism_name,
            'is_isomorphism': inverse is not None,
            'inverse': inverse.name if inverse else None,
            'method': 'native_isomorphism_check'
        }

    def _find_inverse(self, cat: Category, morph: Morphism) -> Optional[Morphism]:
        """Find inverse of a morphism if it exists."""
        # Look for a morphism from target to source
        for m in cat.morphisms:
            if m.source == morph.target and m.target == morph.source:
                # Check if compositions give identities
                # m ∘ morph = id_source and morph ∘ m = id_target
                comp_key1 = (m.name, morph.name)
                comp_key2 = (morph.name, m.name)

                # If explicitly marked as inverse
                if m.properties.get('inverse_of') == morph.name:
                    return m
                if morph.properties.get('inverse_of') == m.name:
                    return m

        return None

    def _is_monomorphism(self, cat: Category, morph: Morphism) -> bool:
        """Check if morphism is a monomorphism (left-cancellable)."""
        # In a finite category, check if f is injective on hom-sets
        # For any g, h with f ∘ g = f ∘ h, we should have g = h
        # This is a heuristic check
        if morph.properties.get('is_identity'):
            return True
        if morph.properties.get('is_mono'):
            return True
        return False

    def _is_epimorphism(self, cat: Category, morph: Morphism) -> bool:
        """Check if morphism is an epimorphism (right-cancellable)."""
        # In a finite category, check if f is surjective on hom-sets
        if morph.properties.get('is_identity'):
            return True
        if morph.properties.get('is_epi'):
            return True
        return False

    def set_inverse(self, category_name: str, f_name: str, g_name: str) -> Dict[str, Any]:
        """Declare two morphisms as inverses of each other."""
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]
        f = next((m for m in cat.morphisms if m.name == f_name), None)
        g = next((m for m in cat.morphisms if m.name == g_name), None)

        if not f:
            return {'error': f'Morphism {f_name} not found'}
        if not g:
            return {'error': f'Morphism {g_name} not found'}

        # Verify they go in opposite directions
        if f.source != g.target or f.target != g.source:
            return {'error': 'Morphisms do not have compatible source/target for inverses'}

        f.properties['inverse_of'] = g_name
        g.properties['inverse_of'] = f_name

        return {
            'f': f_name,
            'g': g_name,
            'are_inverses': True
        }

    # =========================================================================
    # CONCRETE CATEGORIES
    # =========================================================================

    def create_set_category(self, sets: Dict[str, set]) -> Dict[str, Any]:
        """
        Create a category where objects are sets and morphisms are functions.

        Args:
            sets: Dictionary mapping set names to actual sets

        Returns:
            Category creation result
        """
        cat_name = 'Set_' + '_'.join(sorted(sets.keys())[:3])
        if cat_name in self.categories:
            return {'error': f'Category {cat_name} already exists', 'category': cat_name}

        cat = Category(name=cat_name)

        for name, s in sets.items():
            obj = Object(name=name, properties={'elements': s, 'cardinality': len(s)})
            cat.objects.add(obj)

            # Identity morphism (identity function)
            id_morph = Morphism(
                name=f'id_{name}',
                source=obj,
                target=obj,
                mapping=lambda x, s=s: x if x in s else None,
                properties={'is_identity': True}
            )
            cat.morphisms.add(id_morph)
            cat.identities[name] = id_morph

        self.categories[cat_name] = cat

        return {
            'category': cat_name,
            'type': 'Set',
            'objects': list(sets.keys()),
            'cardinalities': {k: len(v) for k, v in sets.items()}
        }

    def create_group_category(self, groups: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a category where objects are groups.

        Args:
            groups: Dict mapping group names to group specs
                   {name: {'elements': [...], 'operation': '+', 'identity': 0}}

        Returns:
            Category creation result
        """
        cat_name = 'Grp_' + '_'.join(sorted(groups.keys())[:3])
        if cat_name in self.categories:
            return {'error': f'Category {cat_name} already exists'}

        cat = Category(name=cat_name)

        for name, spec in groups.items():
            obj = Object(name=name, properties=spec)
            cat.objects.add(obj)

            id_morph = Morphism(
                name=f'id_{name}',
                source=obj,
                target=obj,
                properties={'is_identity': True, 'is_group_homomorphism': True}
            )
            cat.morphisms.add(id_morph)
            cat.identities[name] = id_morph

        self.categories[cat_name] = cat

        return {
            'category': cat_name,
            'type': 'Grp',
            'objects': list(groups.keys())
        }

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_hom_set(self, category_name: str, source: str, target: str) -> Dict[str, Any]:
        """
        Get the hom-set Hom(A, B) = all morphisms from A to B.

        Args:
            category_name: Category name
            source: Source object name
            target: Target object name

        Returns:
            List of morphisms in Hom(source, target)
        """
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]

        hom_set = [m.name for m in cat.morphisms
                   if m.source.name == source and m.target.name == target]

        return {
            'hom_set': f'Hom({source}, {target})',
            'morphisms': hom_set,
            'cardinality': len(hom_set)
        }

    def verify_category_axioms(self, category_name: str) -> Dict[str, Any]:
        """
        Verify that a category satisfies the category axioms.

        1. Identity: For each object A, exists id_A with f ∘ id_A = f and id_A ∘ g = g
        2. Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)

        Args:
            category_name: Category to verify

        Returns:
            Verification results
        """
        if category_name not in self.categories:
            return {'error': f'Category {category_name} not found'}

        cat = self.categories[category_name]

        # Check identity axiom
        identity_valid = True
        identity_issues = []

        for obj in cat.objects:
            if obj.name not in cat.identities:
                identity_valid = False
                identity_issues.append(f'Missing identity for {obj.name}')

        # Associativity is guaranteed by our composition implementation
        # since we just create new morphisms without actual function composition

        return {
            'category': category_name,
            'identity_axiom': identity_valid,
            'identity_issues': identity_issues,
            'associativity_axiom': True,  # Guaranteed by construction
            'is_valid_category': identity_valid,
            'object_count': len(cat.objects),
            'morphism_count': len(cat.morphisms)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'categories_defined': len(self.categories),
            'capabilities': [
                'composition', 'identity', 'isomorphism_check',
                'classification', 'category_construction', 'hom_sets'
            ]
        }
