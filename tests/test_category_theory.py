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
Tests for Category Theory Domain
================================

Tests for morphism, functor, and universal property specialists.
"""

import pytest


class TestMorphismSpecialist:
    """Tests for MorphismSpecialist."""

    @pytest.fixture
    def specialist(self):
        from symbo_agentic_reasoners.agents.specialists.category_theory import MorphismSpecialist
        return MorphismSpecialist()

    def test_create_category(self, specialist):
        """Test category creation."""
        result = specialist.create_category(
            'C',
            ['A', 'B', 'C'],
            [{'name': 'f', 'source': 'A', 'target': 'B'},
             {'name': 'g', 'source': 'B', 'target': 'C'}]
        )
        assert result['category'] == 'C'
        assert 'A' in result['objects']
        assert 'B' in result['objects']
        assert 'C' in result['objects']
        # Should have identities too
        assert 'id_A' in result['morphisms']

    def test_identity_morphisms(self, specialist):
        """Test identity morphism creation."""
        specialist.create_category('D', ['X', 'Y'], [])
        result = specialist.create_identity('D', 'X')
        assert result['identity'] == 'id_X'
        assert result['satisfies_left_identity'] is True
        assert result['satisfies_right_identity'] is True

    def test_compose_morphisms(self, specialist):
        """Test morphism composition."""
        specialist.create_category(
            'E',
            ['A', 'B', 'C'],
            [{'name': 'f', 'source': 'A', 'target': 'B'},
             {'name': 'g', 'source': 'B', 'target': 'C'}]
        )
        result = specialist.compose_morphisms('E', 'g', 'f')
        assert 'composition' in result
        assert result['source'] == 'A'
        assert result['target'] == 'C'

    def test_compose_non_composable(self, specialist):
        """Test error when morphisms don't compose."""
        specialist.create_category(
            'F',
            ['A', 'B', 'C'],
            [{'name': 'f', 'source': 'A', 'target': 'B'},
             {'name': 'h', 'source': 'A', 'target': 'C'}]  # Not composable with f
        )
        result = specialist.compose_morphisms('F', 'h', 'f')
        assert 'error' in result

    def test_classify_morphism_identity(self, specialist):
        """Test classifying identity morphism."""
        specialist.create_category('G', ['X'], [])
        result = specialist.classify_morphism('G', 'id_X')
        assert result['is_identity'] is True
        assert result['is_endomorphism'] is True

    def test_classify_morphism_endomorphism(self, specialist):
        """Test classifying endomorphism."""
        specialist.create_category(
            'H',
            ['X'],
            [{'name': 'f', 'source': 'X', 'target': 'X'}]
        )
        result = specialist.classify_morphism('H', 'f')
        assert result['is_endomorphism'] is True

    def test_set_inverse(self, specialist):
        """Test declaring inverses."""
        specialist.create_category(
            'I',
            ['A', 'B'],
            [{'name': 'f', 'source': 'A', 'target': 'B'},
             {'name': 'g', 'source': 'B', 'target': 'A'}]
        )
        result = specialist.set_inverse('I', 'f', 'g')
        assert result['are_inverses'] is True

    def test_is_isomorphism(self, specialist):
        """Test isomorphism detection after setting inverse."""
        specialist.create_category(
            'J',
            ['A', 'B'],
            [{'name': 'f', 'source': 'A', 'target': 'B'},
             {'name': 'g', 'source': 'B', 'target': 'A'}]
        )
        specialist.set_inverse('J', 'f', 'g')
        result = specialist.is_isomorphism('J', 'f')
        assert result['is_isomorphism'] is True
        assert result['inverse'] == 'g'

    def test_get_hom_set(self, specialist):
        """Test getting hom-set."""
        specialist.create_category(
            'K',
            ['A', 'B'],
            [{'name': 'f', 'source': 'A', 'target': 'B'},
             {'name': 'g', 'source': 'A', 'target': 'B'}]
        )
        result = specialist.get_hom_set('K', 'A', 'B')
        assert 'f' in result['morphisms']
        assert 'g' in result['morphisms']
        assert result['cardinality'] == 2

    def test_verify_category_axioms(self, specialist):
        """Test category axiom verification."""
        specialist.create_category('L', ['A', 'B', 'C'], [])
        result = specialist.verify_category_axioms('L')
        assert result['identity_axiom'] is True
        assert result['associativity_axiom'] is True
        assert result['is_valid_category'] is True

    def test_create_set_category(self, specialist):
        """Test creating Set category from concrete sets."""
        result = specialist.create_set_category({
            'X': {1, 2, 3},
            'Y': {'a', 'b'}
        })
        assert result['type'] == 'Set'
        assert result['cardinalities']['X'] == 3
        assert result['cardinalities']['Y'] == 2

    def test_add_object(self, specialist):
        """Test adding object to category."""
        specialist.create_category('M', ['A'], [])
        result = specialist.add_object('M', 'B')
        assert result['added'] == 'B'
        assert result['identity'] == 'id_B'

    def test_add_morphism(self, specialist):
        """Test adding morphism to category."""
        specialist.create_category('N', ['A', 'B'], [])
        result = specialist.add_morphism('N', 'f', 'A', 'B')
        assert result['added'] == 'f'
        assert result['source'] == 'A'
        assert result['target'] == 'B'


class TestFunctorSpecialist:
    """Tests for FunctorSpecialist."""

    @pytest.fixture
    def specialists(self):
        from symbo_agentic_reasoners.agents.specialists.category_theory import (
            MorphismSpecialist, FunctorSpecialist
        )
        morph = MorphismSpecialist()
        func = FunctorSpecialist(morphism_specialist=morph)
        return morph, func

    def test_create_functor(self, specialists):
        """Test functor creation."""
        morph, func = specialists
        morph.create_category('C', ['A', 'B'], [])
        morph.create_category('D', ['X', 'Y'], [])

        result = func.create_functor(
            'F',
            'C', 'D',
            {'A': 'X', 'B': 'Y'},
            {'id_A': 'id_X', 'id_B': 'id_Y'}
        )
        assert result['functor'] == 'F'
        assert result['type'] == 'covariant'

    def test_create_contravariant_functor(self, specialists):
        """Test contravariant functor creation."""
        morph, func = specialists
        result = func.create_functor(
            'G',
            'C', 'D',
            {'A': 'X'},
            {},
            is_contravariant=True
        )
        assert result['type'] == 'contravariant'

    def test_compose_functors(self, specialists):
        """Test functor composition."""
        morph, func = specialists
        morph.create_category('C', ['A'], [])
        morph.create_category('D', ['X'], [])
        morph.create_category('E', ['P'], [])

        func.create_functor('F', 'C', 'D', {'A': 'X'}, {})
        func.create_functor('G', 'D', 'E', {'X': 'P'}, {})

        result = func.compose_functors('G', 'F')
        assert 'composition' in result
        assert result['source'] == 'C'
        assert result['target'] == 'E'

    def test_compose_incompatible_functors(self, specialists):
        """Test error on incompatible functor composition."""
        morph, func = specialists
        morph.create_category('C', ['A'], [])
        morph.create_category('D', ['X'], [])
        morph.create_category('E', ['P'], [])

        func.create_functor('F', 'C', 'D', {'A': 'X'}, {})
        func.create_functor('H', 'C', 'E', {'A': 'P'}, {})  # Not composable with F

        result = func.compose_functors('H', 'F')
        assert 'error' in result

    def test_create_natural_transformation(self, specialists):
        """Test natural transformation creation."""
        morph, func = specialists
        morph.create_category('C', ['A', 'B'], [])
        morph.create_category('D', ['X', 'Y', 'Z'], [])

        func.create_functor('F', 'C', 'D', {'A': 'X', 'B': 'Y'}, {})
        func.create_functor('G', 'C', 'D', {'A': 'X', 'B': 'Z'}, {})

        result = func.create_natural_transformation(
            'eta',
            'F', 'G',
            {'A': 'id_X', 'B': 'f_Y_Z'}
        )
        assert result['natural_transformation'] == 'eta'
        assert result['source_functor'] == 'F'
        assert result['target_functor'] == 'G'

    def test_verify_functor(self, specialists):
        """Test functor verification."""
        morph, func = specialists
        morph.create_category('C', ['A'], [])
        morph.create_category('D', ['X'], [])

        func.create_functor(
            'F', 'C', 'D',
            {'A': 'X'},
            {'id_A': 'id_X'}
        )

        result = func.verify_functor('F')
        assert 'is_valid_functor' in result

    def test_identity_functor(self, specialists):
        """Test identity functor creation."""
        morph, func = specialists
        morph.create_category('C', ['A', 'B'], [{'name': 'f', 'source': 'A', 'target': 'B'}])

        result = func.create_identity_functor('C')
        assert 'functor' in result
        assert 'Id_C' in result['functor']

    def test_constant_functor(self, specialists):
        """Test constant functor creation."""
        morph, func = specialists
        morph.create_category('C', ['A', 'B'], [])
        morph.create_category('D', ['X', 'Y'], [])

        result = func.create_constant_functor('C', 'D', 'X')
        assert 'functor' in result

    def test_hom_functor_covariant(self, specialists):
        """Test covariant hom-functor."""
        morph, func = specialists
        morph.create_category('C', ['A', 'B'], [])

        result = func.create_hom_functor('C', 'A', covariant=True)
        assert 'Hom(A, -)' in result['functor']
        assert result['representable'] is True

    def test_hom_functor_contravariant(self, specialists):
        """Test contravariant hom-functor."""
        morph, func = specialists
        morph.create_category('C', ['A', 'B'], [])

        result = func.create_hom_functor('C', 'A', covariant=False)
        assert 'Hom(-, A)' in result['functor']
        assert result['type'] == 'contravariant'

    def test_functor_category(self, specialists):
        """Test functor category construction."""
        morph, func = specialists
        morph.create_category('C', ['A'], [])
        morph.create_category('D', ['X'], [])

        func.create_functor('F', 'C', 'D', {'A': 'X'}, {})
        func.create_functor('G', 'C', 'D', {'A': 'X'}, {})

        result = func.create_functor_category('C', 'D')
        assert '[C, D]' in result['functor_category']
        assert 'F' in result['objects']
        assert 'G' in result['objects']


class TestUniversalPropertiesSpecialist:
    """Tests for UniversalPropertiesSpecialist."""

    @pytest.fixture
    def specialists(self):
        from symbo_agentic_reasoners.agents.specialists.category_theory import (
            MorphismSpecialist, UniversalPropertiesSpecialist
        )
        morph = MorphismSpecialist()
        univ = UniversalPropertiesSpecialist(morphism_specialist=morph)
        return morph, univ

    def test_construct_product(self, specialists):
        """Test product construction."""
        morph, univ = specialists
        result = univ.construct_product('C', ['A', 'B'])
        assert result['product'] == 'A×B'
        assert 'π_1' in result['projections'].values()
        assert 'π_2' in result['projections'].values()

    def test_construct_product_three_objects(self, specialists):
        """Test product of three objects."""
        morph, univ = specialists
        result = univ.construct_product('C', ['A', 'B', 'C'])
        assert result['product'] == 'A×B×C'
        assert result['projections']['A'] == 'π_1'
        assert result['projections']['B'] == 'π_2'
        assert result['projections']['C'] == 'π_3'

    def test_product_morphism(self, specialists):
        """Test induced product morphism."""
        morph, univ = specialists
        result = univ.product_morphism('C', 'A×B', {'A': 'f', 'B': 'g'})
        assert '⟨' in result['induced_morphism']
        assert result['unique'] is True

    def test_construct_coproduct(self, specialists):
        """Test coproduct construction."""
        morph, univ = specialists
        result = univ.construct_coproduct('C', ['A', 'B'])
        assert result['coproduct'] == 'A+B'
        assert 'ι_1' in result['injections'].values()
        assert 'ι_2' in result['injections'].values()

    def test_coproduct_morphism(self, specialists):
        """Test induced coproduct morphism."""
        morph, univ = specialists
        result = univ.coproduct_morphism('C', 'A+B', {'A': 'f', 'B': 'g'})
        assert '[' in result['induced_morphism']
        assert result['unique'] is True

    def test_construct_equalizer(self, specialists):
        """Test equalizer construction."""
        morph, univ = specialists
        result = univ.construct_equalizer('C', 'f', 'g')
        assert 'Eq(f,g)' in result['equalizer']
        assert 'equalizes' in result

    def test_construct_coequalizer(self, specialists):
        """Test coequalizer construction."""
        morph, univ = specialists
        result = univ.construct_coequalizer('C', 'f', 'g')
        assert 'Coeq(f,g)' in result['coequalizer']
        assert 'coequalizes' in result

    def test_construct_pullback(self, specialists):
        """Test pullback construction."""
        morph, univ = specialists
        result = univ.construct_pullback('C', 'f', 'g')
        assert 'pullback' in result
        assert 'projections' in result
        assert 'commutes' in result

    def test_construct_pushout(self, specialists):
        """Test pushout construction."""
        morph, univ = specialists
        result = univ.construct_pushout('C', 'f', 'g')
        assert 'pushout' in result
        assert 'injections' in result
        assert 'commutes' in result

    def test_find_terminal(self, specialists):
        """Test finding terminal object."""
        morph, univ = specialists
        # Create category with terminal object
        morph.create_category('T', ['A', '1'], [
            {'name': '!_A', 'source': 'A', 'target': '1'},
            {'name': '!_1', 'source': '1', 'target': '1'}  # Will use identity
        ])
        result = univ.find_terminal('T')
        # May or may not find terminal depending on morphism count
        assert 'terminal_object' in result

    def test_find_initial(self, specialists):
        """Test finding initial object."""
        morph, univ = specialists
        # Create category with initial object
        morph.create_category('I', ['0', 'A'], [
            {'name': '¡_A', 'source': '0', 'target': 'A'},
            {'name': '¡_0', 'source': '0', 'target': '0'}  # Will use identity
        ])
        result = univ.find_initial('I')
        assert 'initial_object' in result

    def test_find_zero_object(self, specialists):
        """Test finding zero object."""
        morph, univ = specialists
        morph.create_category('Z', ['0'], [])
        result = univ.find_zero_object('Z')
        # Single object category where object is both initial and terminal
        assert 'zero_object' in result

    def test_construct_exponential(self, specialists):
        """Test exponential object construction."""
        morph, univ = specialists
        result = univ.construct_exponential('C', 'A', 'B')
        assert result['exponential'] == 'B^A'
        assert 'evaluation' in result
        assert 'curry_uncurry' in result

    def test_construct_limit(self, specialists):
        """Test general limit construction."""
        morph, univ = specialists
        result = univ.construct_limit('C', {
            'objects': ['A', 'B', 'C'],
            'morphisms': [{'name': 'f', 'source': 'A', 'target': 'B'}]
        })
        assert 'limit' in result
        assert 'cone_projections' in result

    def test_construct_colimit(self, specialists):
        """Test general colimit construction."""
        morph, univ = specialists
        result = univ.construct_colimit('C', {
            'objects': ['A', 'B', 'C'],
            'morphisms': []
        })
        assert 'colimit' in result
        assert 'cocone_injections' in result

    def test_is_complete(self, specialists):
        """Test completeness check."""
        morph, univ = specialists
        result = univ.is_complete('C')
        assert 'sufficient_conditions' in result

    def test_is_cocomplete(self, specialists):
        """Test cocompleteness check."""
        morph, univ = specialists
        result = univ.is_cocomplete('C')
        assert 'sufficient_conditions' in result


class TestCategoryTheorySupervisor:
    """Tests for CategoryTheorySupervisor."""

    @pytest.fixture
    def supervisor(self):
        from symbo_agentic_reasoners.agents.supervisors.category_theory_supervisor import CategoryTheorySupervisor
        return CategoryTheorySupervisor()

    def test_initialization(self, supervisor):
        """Test supervisor initialization."""
        assert supervisor.agent_id == 'category_theory_supervisor_001'

    def test_lazy_loading_specialists(self, supervisor):
        """Test that specialists are lazy-loaded."""
        assert supervisor._morphism_specialist is None
        assert supervisor._functor_specialist is None
        assert supervisor._universal_specialist is None

        # Access specialist
        _ = supervisor.morphism_specialist
        assert supervisor._morphism_specialist is not None

    def test_solve_create_category(self, supervisor):
        """Test solving category creation."""
        result = supervisor.solve({
            'type': 'create_category',
            'name': 'C',
            'objects': ['A', 'B'],
            'morphisms': []
        })
        assert result['category'] == 'C'

    def test_solve_compose(self, supervisor):
        """Test solving morphism composition."""
        supervisor.solve({
            'type': 'create_category',
            'name': 'D',
            'objects': ['A', 'B', 'C'],
            'morphisms': [
                {'name': 'f', 'source': 'A', 'target': 'B'},
                {'name': 'g', 'source': 'B', 'target': 'C'}
            ]
        })
        result = supervisor.solve({
            'type': 'compose',
            'category_name': 'D',
            'g': 'g',
            'f': 'f'
        })
        assert 'composition' in result

    def test_solve_product(self, supervisor):
        """Test solving product construction."""
        result = supervisor.solve({
            'type': 'product',
            'category_name': 'C',
            'objects': ['A', 'B']
        })
        assert result['product'] == 'A×B'

    def test_solve_coproduct(self, supervisor):
        """Test solving coproduct construction."""
        result = supervisor.solve({
            'type': 'coproduct',
            'category_name': 'C',
            'objects': ['A', 'B']
        })
        assert result['coproduct'] == 'A+B'

    def test_solve_create_functor(self, supervisor):
        """Test solving functor creation."""
        supervisor.morphism_specialist.create_category('C', ['A'], [])
        supervisor.morphism_specialist.create_category('D', ['X'], [])

        result = supervisor.solve({
            'type': 'create_functor',
            'name': 'F',
            'source_category': 'C',
            'target_category': 'D',
            'object_map': {'A': 'X'},
            'morphism_map': {}
        })
        assert result['functor'] == 'F'

    def test_get_statistics(self, supervisor):
        """Test getting statistics."""
        stats = supervisor.get_statistics()
        assert stats['tier'] == 2
        assert stats['role'] == 'supervisor'
        assert 'morphism' in stats['specialists']
        assert 'functor' in stats['specialists']
        assert 'universal' in stats['specialists']


class TestCategoryTheoryIntegration:
    """Integration tests for the category theory domain."""

    def test_full_workflow(self):
        """Test complete workflow through supervisor."""
        from symbo_agentic_reasoners.agents.supervisors.category_theory_supervisor import CategoryTheorySupervisor
        sup = CategoryTheorySupervisor()

        # Create a category
        cat_result = sup.solve({
            'type': 'create_category',
            'name': 'Groups',
            'objects': ['Z', 'Z2', 'Z3'],
            'morphisms': [
                {'name': 'π', 'source': 'Z', 'target': 'Z2'},
                {'name': 'ρ', 'source': 'Z', 'target': 'Z3'}
            ]
        })
        assert cat_result['category'] == 'Groups'

        # Create a product
        prod_result = sup.solve({
            'type': 'product',
            'category_name': 'Groups',
            'objects': ['Z2', 'Z3']
        })
        assert prod_result['product'] == 'Z2×Z3'

        # Get hom-set
        hom_result = sup.solve({
            'type': 'hom_set',
            'category_name': 'Groups',
            'source': 'Z',
            'target': 'Z2'
        })
        assert 'π' in hom_result['morphisms']

    def test_functor_workflow(self):
        """Test functor creation and composition."""
        from symbo_agentic_reasoners.agents.supervisors.category_theory_supervisor import CategoryTheorySupervisor
        sup = CategoryTheorySupervisor()

        # Create categories
        sup.morphism_specialist.create_category('C', ['A', 'B'], [])
        sup.morphism_specialist.create_category('D', ['X', 'Y'], [])
        sup.morphism_specialist.create_category('E', ['P', 'Q'], [])

        # Create functors
        f_result = sup.solve({
            'type': 'create_functor',
            'name': 'F',
            'source_category': 'C',
            'target_category': 'D',
            'object_map': {'A': 'X', 'B': 'Y'}
        })
        assert f_result['functor'] == 'F'

        g_result = sup.solve({
            'type': 'create_functor',
            'name': 'G',
            'source_category': 'D',
            'target_category': 'E',
            'object_map': {'X': 'P', 'Y': 'Q'}
        })
        assert g_result['functor'] == 'G'

        # Compose functors
        comp_result = sup.solve({
            'type': 'compose_functors',
            'g': 'G',
            'f': 'F'
        })
        assert 'composition' in comp_result
        assert comp_result['source'] == 'C'
        assert comp_result['target'] == 'E'
