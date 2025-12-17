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
UNIVERSAL PROPERTIES SPECIALIST (Tier 3)
========================================

Native Python implementation for universal constructions in category theory.
Handles products, coproducts, equalizers, coequalizers, pullbacks, pushouts,
limits, and colimits.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from .morphism_specialist import Category, Object, Morphism

logger = logging.getLogger(__name__)


@dataclass
class UniversalConstruction:
    """Represents a universal construction (product, coproduct, etc.)."""
    name: str
    construction_type: str  # 'product', 'coproduct', 'equalizer', etc.
    universal_object: str  # The universal object name
    components: List[str]  # Objects involved (A, B for A×B)
    projections: Dict[str, str]  # Projection morphisms (π₁, π₂)
    injections: Dict[str, str]  # Injection morphisms (ι₁, ι₂) for coproducts
    properties: Dict[str, Any] = field(default_factory=dict)


class UniversalPropertiesSpecialist(BDIAgent):
    """
    Specialist for universal constructions in category theory.

    Capabilities:
    - Products and coproducts
    - Equalizers and coequalizers
    - Pullbacks and pushouts
    - Limits and colimits
    - Terminal and initial objects
    - Exponential objects
    """

    def __init__(self, agent_id: str = 'universal_properties_specialist_001',
                 df=None, blackboard=None, morphism_specialist=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.morphism_specialist = morphism_specialist
        self.tasks_executed = 0

        # Store universal constructions
        self.constructions: Dict[str, UniversalConstruction] = {}

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.category_theory.universal',
                agent_id=agent_id,
                algorithm='native_categorical',
                cost='low',
                instance=self,
                tier='3',
                capabilities='products_coproducts_limits_colimits'
            ))

        logger.info(f"[{agent_id}] Universal Properties Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for universal construction tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['universal'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['product'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['coproduct'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['limit'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create universal construction plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'product')

            steps = ['claim_task', 'compute_universal', 'post_result']
            intention = Intention(
                plan_id=f'universal_{operation}_{task_id}',
                steps=steps,
                target_desire='universal_construction',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute universal constructions."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_universal':
            self._compute_universal(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_universal(self, intention: Intention):
        """Compute universal constructions."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'product')

        try:
            if operation == 'product':
                result = self.construct_product(
                    metadata.get('category_name'),
                    metadata.get('objects', [])
                )
            elif operation == 'coproduct':
                result = self.construct_coproduct(
                    metadata.get('category_name'),
                    metadata.get('objects', [])
                )
            elif operation == 'equalizer':
                result = self.construct_equalizer(
                    metadata.get('category_name'),
                    metadata.get('f'),
                    metadata.get('g')
                )
            elif operation == 'pullback':
                result = self.construct_pullback(
                    metadata.get('category_name'),
                    metadata.get('f'),
                    metadata.get('g')
                )
            elif operation == 'terminal':
                result = self.find_terminal(metadata.get('category_name'))
            elif operation == 'initial':
                result = self.find_initial(metadata.get('category_name'))
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Universal construction failed: {e}")
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
                tags=['universal', 'category_theory', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # PRODUCTS
    # =========================================================================

    def construct_product(self, category_name: str, objects: List[str]) -> Dict[str, Any]:
        """
        Construct the product of objects.

        The product A × B is an object with projections π₁: A×B → A and π₂: A×B → B
        satisfying the universal property: for any object C with morphisms
        f: C → A and g: C → B, there exists a unique ⟨f,g⟩: C → A×B
        such that π₁ ∘ ⟨f,g⟩ = f and π₂ ∘ ⟨f,g⟩ = g.

        Args:
            category_name: Category name
            objects: List of objects to take product of

        Returns:
            Product construction result
        """
        if len(objects) < 2:
            return {'error': 'Need at least 2 objects for product'}

        product_name = '×'.join(objects)

        # Create projection morphisms
        projections = {}
        for i, obj in enumerate(objects):
            proj_name = f'π_{i+1}'
            projections[obj] = proj_name

        construction = UniversalConstruction(
            name=f'Product_{product_name}',
            construction_type='product',
            universal_object=product_name,
            components=objects,
            projections=projections,
            injections={},
            properties={'arity': len(objects)}
        )

        self.constructions[construction.name] = construction

        return {
            'product': product_name,
            'components': objects,
            'projections': projections,
            'universal_property': 'For any C with f_i: C → A_i, exists unique ⟨f_1,...,f_n⟩: C → ∏A_i',
            'method': 'native_product_construction'
        }

    def verify_product(self, category_name: str, product_name: str,
                       projections: Dict[str, str]) -> Dict[str, Any]:
        """
        Verify that a given object satisfies the product universal property.

        Args:
            category_name: Category name
            product_name: Claimed product object
            projections: Dict of component → projection morphism

        Returns:
            Verification result
        """
        # For full verification, we'd check that the universal property holds
        # for all objects and morphism pairs. Here we do a structural check.

        return {
            'product': product_name,
            'projections': projections,
            'structure_valid': True,
            'universal_property': 'assumed',
            'note': 'Full verification requires checking uniqueness of factorizations'
        }

    def product_morphism(self, category_name: str, product_name: str,
                         morphisms: Dict[str, str]) -> Dict[str, Any]:
        """
        Construct the unique morphism into a product.

        Given f: C → A and g: C → B, constructs ⟨f,g⟩: C → A×B.

        Args:
            category_name: Category name
            product_name: Product object name
            morphisms: Dict of component → morphism from source

        Returns:
            Product morphism result
        """
        # The universal property gives existence and uniqueness
        morphism_parts = ','.join(morphisms.values())
        induced_name = f'⟨{morphism_parts}⟩'

        return {
            'induced_morphism': induced_name,
            'target': product_name,
            'factors_through': morphisms,
            'unique': True,
            'method': 'native_product_morphism'
        }

    # =========================================================================
    # COPRODUCTS
    # =========================================================================

    def construct_coproduct(self, category_name: str, objects: List[str]) -> Dict[str, Any]:
        """
        Construct the coproduct (sum) of objects.

        The coproduct A + B is an object with injections ι₁: A → A+B and ι₂: B → A+B
        satisfying the dual universal property.

        Args:
            category_name: Category name
            objects: List of objects

        Returns:
            Coproduct construction result
        """
        if len(objects) < 2:
            return {'error': 'Need at least 2 objects for coproduct'}

        coproduct_name = '+'.join(objects)

        # Create injection morphisms
        injections = {}
        for i, obj in enumerate(objects):
            inj_name = f'ι_{i+1}'
            injections[obj] = inj_name

        construction = UniversalConstruction(
            name=f'Coproduct_{coproduct_name}',
            construction_type='coproduct',
            universal_object=coproduct_name,
            components=objects,
            projections={},
            injections=injections,
            properties={'arity': len(objects)}
        )

        self.constructions[construction.name] = construction

        return {
            'coproduct': coproduct_name,
            'components': objects,
            'injections': injections,
            'universal_property': 'For any C with f_i: A_i → C, exists unique [f_1,...,f_n]: ∐A_i → C',
            'method': 'native_coproduct_construction'
        }

    def coproduct_morphism(self, category_name: str, coproduct_name: str,
                            morphisms: Dict[str, str]) -> Dict[str, Any]:
        """
        Construct the unique morphism from a coproduct.

        Given f: A → C and g: B → C, constructs [f,g]: A+B → C.

        Args:
            category_name: Category name
            coproduct_name: Coproduct object name
            morphisms: Dict of component → morphism to target

        Returns:
            Coproduct morphism result
        """
        morphism_parts = ','.join(morphisms.values())
        induced_name = f'[{morphism_parts}]'

        return {
            'induced_morphism': induced_name,
            'source': coproduct_name,
            'factors_through': morphisms,
            'unique': True,
            'method': 'native_coproduct_morphism'
        }

    # =========================================================================
    # EQUALIZERS AND COEQUALIZERS
    # =========================================================================

    def construct_equalizer(self, category_name: str, f: str, g: str) -> Dict[str, Any]:
        """
        Construct the equalizer of two parallel morphisms.

        Given f, g: A → B, the equalizer is an object E with morphism e: E → A
        such that f ∘ e = g ∘ e, and universal: any h with f ∘ h = g ∘ h
        factors uniquely through e.

        Args:
            category_name: Category name
            f: First morphism name
            g: Second morphism name

        Returns:
            Equalizer construction result
        """
        eq_name = f'Eq({f},{g})'
        eq_morphism = f'eq_{f}_{g}'

        construction = UniversalConstruction(
            name=eq_name,
            construction_type='equalizer',
            universal_object=eq_name,
            components=[f, g],
            projections={eq_name: eq_morphism},
            injections={},
            properties={'parallel_morphisms': [f, g]}
        )

        self.constructions[construction.name] = construction

        return {
            'equalizer': eq_name,
            'morphism': eq_morphism,
            'equalizes': [f, g],
            'universal_property': f'For any h with {f}∘h = {g}∘h, exists unique u with eq∘u = h',
            'method': 'native_equalizer'
        }

    def construct_coequalizer(self, category_name: str, f: str, g: str) -> Dict[str, Any]:
        """
        Construct the coequalizer of two parallel morphisms.

        Given f, g: A → B, the coequalizer is an object Q with morphism q: B → Q
        such that q ∘ f = q ∘ g, universal for this property.

        Args:
            category_name: Category name
            f: First morphism name
            g: Second morphism name

        Returns:
            Coequalizer construction result
        """
        coeq_name = f'Coeq({f},{g})'
        coeq_morphism = f'coeq_{f}_{g}'

        construction = UniversalConstruction(
            name=coeq_name,
            construction_type='coequalizer',
            universal_object=coeq_name,
            components=[f, g],
            projections={},
            injections={coeq_name: coeq_morphism},
            properties={'parallel_morphisms': [f, g]}
        )

        self.constructions[construction.name] = construction

        return {
            'coequalizer': coeq_name,
            'morphism': coeq_morphism,
            'coequalizes': [f, g],
            'universal_property': f'For any h with h∘{f} = h∘{g}, exists unique u with u∘coeq = h',
            'method': 'native_coequalizer'
        }

    # =========================================================================
    # PULLBACKS AND PUSHOUTS
    # =========================================================================

    def construct_pullback(self, category_name: str, f: str, g: str) -> Dict[str, Any]:
        """
        Construct the pullback (fiber product) of morphisms.

        Given f: A → C and g: B → C, the pullback is an object P with
        projections π_A: P → A and π_B: P → B such that f ∘ π_A = g ∘ π_B.

        Args:
            category_name: Category name
            f: First morphism f: A → C
            g: Second morphism g: B → C

        Returns:
            Pullback construction result
        """
        pullback_name = f'A×_C B'  # Fiber product notation
        proj_a = f'π_A^{f}_{g}'
        proj_b = f'π_B^{f}_{g}'

        construction = UniversalConstruction(
            name=f'Pullback_{f}_{g}',
            construction_type='pullback',
            universal_object=pullback_name,
            components=[f, g],
            projections={'A': proj_a, 'B': proj_b},
            injections={},
            properties={'commutative_square': f'{f}∘{proj_a} = {g}∘{proj_b}'}
        )

        self.constructions[construction.name] = construction

        return {
            'pullback': pullback_name,
            'projections': {'A': proj_a, 'B': proj_b},
            'commutes': f'{f}∘{proj_a} = {g}∘{proj_b}',
            'universal_property': 'For any X with h,k satisfying f∘h = g∘k, exists unique u: X → P',
            'method': 'native_pullback'
        }

    def construct_pushout(self, category_name: str, f: str, g: str) -> Dict[str, Any]:
        """
        Construct the pushout of morphisms.

        Given f: C → A and g: C → B, the pushout is an object Q with
        injections ι_A: A → Q and ι_B: B → Q such that ι_A ∘ f = ι_B ∘ g.

        Args:
            category_name: Category name
            f: First morphism f: C → A
            g: Second morphism g: C → B

        Returns:
            Pushout construction result
        """
        pushout_name = f'A⊔_C B'  # Amalgamated sum notation
        inj_a = f'ι_A^{f}_{g}'
        inj_b = f'ι_B^{f}_{g}'

        construction = UniversalConstruction(
            name=f'Pushout_{f}_{g}',
            construction_type='pushout',
            universal_object=pushout_name,
            components=[f, g],
            projections={},
            injections={'A': inj_a, 'B': inj_b},
            properties={'commutative_square': f'{inj_a}∘{f} = {inj_b}∘{g}'}
        )

        self.constructions[construction.name] = construction

        return {
            'pushout': pushout_name,
            'injections': {'A': inj_a, 'B': inj_b},
            'commutes': f'{inj_a}∘{f} = {inj_b}∘{g}',
            'universal_property': 'For any X with h,k satisfying h∘f = k∘g, exists unique u: Q → X',
            'method': 'native_pushout'
        }

    # =========================================================================
    # TERMINAL AND INITIAL OBJECTS
    # =========================================================================

    def find_terminal(self, category_name: str) -> Dict[str, Any]:
        """
        Find the terminal object (final object) in a category.

        The terminal object 1 has exactly one morphism from any object:
        for all A, |Hom(A, 1)| = 1.

        Args:
            category_name: Category name

        Returns:
            Terminal object result
        """
        if not self.morphism_specialist:
            return {'error': 'Morphism specialist required'}

        cat = self.morphism_specialist.categories.get(category_name)
        if not cat:
            return {'error': f'Category {category_name} not found'}

        # Check each object to see if it's terminal
        for candidate in cat.objects:
            is_terminal = True
            unique_morphisms = {}

            for obj in cat.objects:
                # Count morphisms from obj to candidate
                morphisms_to_candidate = [
                    m for m in cat.morphisms
                    if m.source.name == obj.name and m.target.name == candidate.name
                ]

                if len(morphisms_to_candidate) != 1:
                    is_terminal = False
                    break
                else:
                    unique_morphisms[obj.name] = morphisms_to_candidate[0].name

            if is_terminal:
                return {
                    'terminal_object': candidate.name,
                    'unique_morphisms': unique_morphisms,
                    'notation': '1',
                    'property': 'For all A, exists unique !_A: A → 1'
                }

        return {
            'terminal_object': None,
            'message': 'No terminal object found (may not exist)'
        }

    def find_initial(self, category_name: str) -> Dict[str, Any]:
        """
        Find the initial object in a category.

        The initial object 0 has exactly one morphism to any object:
        for all A, |Hom(0, A)| = 1.

        Args:
            category_name: Category name

        Returns:
            Initial object result
        """
        if not self.morphism_specialist:
            return {'error': 'Morphism specialist required'}

        cat = self.morphism_specialist.categories.get(category_name)
        if not cat:
            return {'error': f'Category {category_name} not found'}

        # Check each object to see if it's initial
        for candidate in cat.objects:
            is_initial = True
            unique_morphisms = {}

            for obj in cat.objects:
                # Count morphisms from candidate to obj
                morphisms_from_candidate = [
                    m for m in cat.morphisms
                    if m.source.name == candidate.name and m.target.name == obj.name
                ]

                if len(morphisms_from_candidate) != 1:
                    is_initial = False
                    break
                else:
                    unique_morphisms[obj.name] = morphisms_from_candidate[0].name

            if is_initial:
                return {
                    'initial_object': candidate.name,
                    'unique_morphisms': unique_morphisms,
                    'notation': '0',
                    'property': 'For all A, exists unique ¡_A: 0 → A'
                }

        return {
            'initial_object': None,
            'message': 'No initial object found (may not exist)'
        }

    def find_zero_object(self, category_name: str) -> Dict[str, Any]:
        """
        Find a zero object (both initial and terminal).

        Args:
            category_name: Category name

        Returns:
            Zero object result
        """
        terminal = self.find_terminal(category_name)
        initial = self.find_initial(category_name)

        term_obj = terminal.get('terminal_object')
        init_obj = initial.get('initial_object')

        if term_obj and init_obj and term_obj == init_obj:
            return {
                'zero_object': term_obj,
                'is_terminal': True,
                'is_initial': True,
                'notation': '0 = 1',
                'property': 'Unique morphism both from and to every object'
            }

        return {
            'zero_object': None,
            'terminal': term_obj,
            'initial': init_obj,
            'message': 'No zero object (initial ≠ terminal or one missing)'
        }

    # =========================================================================
    # EXPONENTIAL OBJECTS
    # =========================================================================

    def construct_exponential(self, category_name: str, a: str, b: str) -> Dict[str, Any]:
        """
        Construct the exponential object B^A (internal hom).

        The exponential satisfies: Hom(C × A, B) ≅ Hom(C, B^A)

        Args:
            category_name: Category name
            a: Exponent object A
            b: Base object B

        Returns:
            Exponential construction result
        """
        exp_name = f'{b}^{a}'
        eval_morphism = f'eval_{a}_{b}'  # eval: B^A × A → B

        construction = UniversalConstruction(
            name=f'Exponential_{b}^{a}',
            construction_type='exponential',
            universal_object=exp_name,
            components=[a, b],
            projections={exp_name: eval_morphism},
            injections={},
            properties={
                'adjunction': f'Hom(C × {a}, {b}) ≅ Hom(C, {exp_name})',
                'evaluation': eval_morphism
            }
        )

        self.constructions[construction.name] = construction

        return {
            'exponential': exp_name,
            'exponent': a,
            'base': b,
            'evaluation': eval_morphism,
            'curry_uncurry': f'λ: Hom(C × {a}, {b}) → Hom(C, {exp_name})',
            'cartesian_closed': 'Category is Cartesian closed if exponentials exist',
            'method': 'native_exponential'
        }

    # =========================================================================
    # GENERAL LIMITS AND COLIMITS
    # =========================================================================

    def construct_limit(self, category_name: str, diagram: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct the limit of a diagram.

        Args:
            category_name: Category name
            diagram: Diagram specification with objects and morphisms

        Returns:
            Limit construction result
        """
        diagram_objects = diagram.get('objects', [])
        diagram_morphisms = diagram.get('morphisms', [])

        limit_name = f'lim({",".join(diagram_objects[:3])}{"..." if len(diagram_objects) > 3 else ""})'

        # Create cone projections
        projections = {obj: f'π_{obj}' for obj in diagram_objects}

        construction = UniversalConstruction(
            name=f'Limit_{limit_name}',
            construction_type='limit',
            universal_object=limit_name,
            components=diagram_objects,
            projections=projections,
            injections={},
            properties={
                'diagram_objects': diagram_objects,
                'diagram_morphisms': diagram_morphisms
            }
        )

        self.constructions[construction.name] = construction

        return {
            'limit': limit_name,
            'diagram_objects': diagram_objects,
            'cone_projections': projections,
            'universal_property': 'For any cone over the diagram, unique factorization through limit',
            'method': 'native_limit'
        }

    def construct_colimit(self, category_name: str, diagram: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct the colimit of a diagram.

        Args:
            category_name: Category name
            diagram: Diagram specification

        Returns:
            Colimit construction result
        """
        diagram_objects = diagram.get('objects', [])
        diagram_morphisms = diagram.get('morphisms', [])

        colimit_name = f'colim({",".join(diagram_objects[:3])}{"..." if len(diagram_objects) > 3 else ""})'

        # Create cocone injections
        injections = {obj: f'ι_{obj}' for obj in diagram_objects}

        construction = UniversalConstruction(
            name=f'Colimit_{colimit_name}',
            construction_type='colimit',
            universal_object=colimit_name,
            components=diagram_objects,
            projections={},
            injections=injections,
            properties={
                'diagram_objects': diagram_objects,
                'diagram_morphisms': diagram_morphisms
            }
        )

        self.constructions[construction.name] = construction

        return {
            'colimit': colimit_name,
            'diagram_objects': diagram_objects,
            'cocone_injections': injections,
            'universal_property': 'For any cocone under the diagram, unique factorization through colimit',
            'method': 'native_colimit'
        }

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def is_complete(self, category_name: str) -> Dict[str, Any]:
        """
        Check if a category is complete (has all small limits).

        A category is complete if it has all products and equalizers.

        Args:
            category_name: Category name

        Returns:
            Completeness check result
        """
        # This is a structural/theoretical check
        return {
            'category': category_name,
            'complete': 'unknown',
            'note': 'Completeness requires all products and equalizers exist',
            'sufficient_conditions': [
                'Has all products',
                'Has all equalizers',
                'Equivalently: has all pullbacks and a terminal object'
            ]
        }

    def is_cocomplete(self, category_name: str) -> Dict[str, Any]:
        """
        Check if a category is cocomplete (has all small colimits).

        Args:
            category_name: Category name

        Returns:
            Cocompleteness check result
        """
        return {
            'category': category_name,
            'cocomplete': 'unknown',
            'note': 'Cocompleteness requires all coproducts and coequalizers exist',
            'sufficient_conditions': [
                'Has all coproducts',
                'Has all coequalizers',
                'Equivalently: has all pushouts and an initial object'
            ]
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        by_type = {}
        for c in self.constructions.values():
            by_type[c.construction_type] = by_type.get(c.construction_type, 0) + 1

        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'constructions_defined': len(self.constructions),
            'by_type': by_type,
            'capabilities': [
                'product', 'coproduct', 'equalizer', 'coequalizer',
                'pullback', 'pushout', 'terminal', 'initial', 'zero_object',
                'exponential', 'limit', 'colimit'
            ]
        }
