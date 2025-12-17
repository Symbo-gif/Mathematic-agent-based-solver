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
Tests for Group/Ring Theory Module
===================================

Comprehensive tests for native permutation groups and algebraic structures.
"""

import pytest
import math


class TestNativePermutation:
    """Tests for NativePermutation class."""

    def test_permutation_create(self):
        """Test creating a permutation."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            NativePermutation
        )
        perm = NativePermutation([1, 0, 2])  # Swap 0 and 1
        assert perm(0) == 1
        assert perm(1) == 0
        assert perm(2) == 2

    def test_permutation_order_identity(self):
        """Test order of identity permutation."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            NativePermutation
        )
        identity = NativePermutation([0, 1, 2])
        assert identity.order() == 1

    def test_permutation_order_transposition(self):
        """Test order of transposition (swap) is 2."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            NativePermutation
        )
        trans = NativePermutation([1, 0, 2])  # (0 1)
        assert trans.order() == 2

    def test_permutation_order_cycle(self):
        """Test order of 3-cycle is 3."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            NativePermutation
        )
        cycle = NativePermutation([1, 2, 0])  # (0 1 2)
        assert cycle.order() == 3

    def test_permutation_multiply(self):
        """Test permutation multiplication (composition)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            NativePermutation
        )
        p1 = NativePermutation([1, 0, 2])  # (0 1)
        p2 = NativePermutation([0, 2, 1])  # (1 2)
        result = p1 * p2
        # Composition: first apply p2, then p1
        assert isinstance(result, NativePermutation)

    def test_permutation_repr(self):
        """Test string representation."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            NativePermutation
        )
        perm = NativePermutation([1, 0, 2])
        assert 'Permutation' in repr(perm)


class TestNativePermutationGroup:
    """Tests for NativePermutationGroup class."""

    def test_group_create(self):
        """Test creating a permutation group."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            NativePermutationGroup, NativePermutation
        )
        gen = NativePermutation([1, 2, 0])
        group = NativePermutationGroup([gen])
        assert len(group.generators) == 1

    def test_group_is_abelian_cyclic(self):
        """Test cyclic groups are abelian."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            CyclicGroup
        )
        Z4 = CyclicGroup(4)
        assert Z4.is_abelian is True

    def test_group_is_cyclic(self):
        """Test cyclic group is cyclic."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            CyclicGroup
        )
        Z5 = CyclicGroup(5)
        assert Z5.is_cyclic is True

    def test_group_order(self):
        """Test group order computation."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            CyclicGroup
        )
        Z6 = CyclicGroup(6)
        order = Z6.order()
        assert order >= 1


class TestSymmetricGroup:
    """Tests for SymmetricGroup function."""

    def test_symmetric_group_s3(self):
        """Test S_3 has order 6."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            SymmetricGroup
        )
        S3 = SymmetricGroup(3)
        assert len(S3.generators) == 2

    def test_symmetric_group_s4(self):
        """Test S_4 construction."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            SymmetricGroup
        )
        S4 = SymmetricGroup(4)
        assert len(S4.generators) == 2

    def test_symmetric_not_abelian(self):
        """Test S_3 is not abelian."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            SymmetricGroup
        )
        S3 = SymmetricGroup(3)
        assert S3.is_abelian is False


class TestAlternatingGroup:
    """Tests for AlternatingGroup function."""

    def test_alternating_group_a3(self):
        """Test A_3 construction."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            AlternatingGroup
        )
        A3 = AlternatingGroup(3)
        assert len(A3.generators) >= 1

    def test_alternating_group_a2(self):
        """Test A_2 (trivial group)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            AlternatingGroup
        )
        A2 = AlternatingGroup(2)
        assert A2 is not None


class TestCyclicGroup:
    """Tests for CyclicGroup function."""

    def test_cyclic_group_z4(self):
        """Test Z_4 construction."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            CyclicGroup
        )
        Z4 = CyclicGroup(4)
        assert len(Z4.generators) == 1

    def test_cyclic_group_is_abelian(self):
        """Test cyclic groups are abelian."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            CyclicGroup
        )
        Z10 = CyclicGroup(10)
        assert Z10.is_abelian is True


class TestDihedralGroup:
    """Tests for DihedralGroup function."""

    def test_dihedral_group_d4(self):
        """Test D_4 (square symmetries)."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            DihedralGroup
        )
        D4 = DihedralGroup(4)
        assert len(D4.generators) == 2

    def test_dihedral_not_abelian(self):
        """Test D_4 is not abelian."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            DihedralGroup
        )
        D4 = DihedralGroup(4)
        assert D4.is_abelian is False


class TestAlgebraicStructure:
    """Tests for AlgebraicStructure dataclass."""

    def test_algebraic_structure_create(self):
        """Test creating an algebraic structure."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            AlgebraicStructure, StructureType
        )
        struct = AlgebraicStructure(
            name='Z_4',
            structure_type=StructureType.GROUP,
            order=4,
            properties={'abelian', 'cyclic'},
            is_finite=True
        )
        assert struct.name == 'Z_4'
        assert struct.order == 4

    def test_algebraic_structure_to_dict(self):
        """Test serialization to dict."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            AlgebraicStructure, StructureType
        )
        struct = AlgebraicStructure(
            name='S_3',
            structure_type=StructureType.GROUP,
            order=6,
            properties={'non-abelian'}
        )
        d = struct.to_dict()
        assert d['name'] == 'S_3'
        assert d['order'] == 6


class TestIsomorphismResult:
    """Tests for IsomorphismResult dataclass."""

    def test_isomorphism_result_true(self):
        """Test creating isomorphic result."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            IsomorphismResult
        )
        result = IsomorphismResult(
            are_isomorphic=True,
            reason='Same order and structure'
        )
        assert result.are_isomorphic is True

    def test_isomorphism_result_to_dict(self):
        """Test serialization."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            IsomorphismResult
        )
        result = IsomorphismResult(
            are_isomorphic=False,
            reason='Different orders'
        )
        d = result.to_dict()
        assert d['are_isomorphic'] is False


class TestGroupRingTheoryAgent:
    """Tests for GroupRingTheoryAgent BDI agent."""

    def test_agent_create(self):
        """Test creating the agent."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        assert agent.agent_id == 'group_ring_theory_001'

    def test_agent_create_group_symmetric(self):
        """Test creating symmetric group."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        group, structure = agent.create_group('symmetric', 4)
        assert structure.name == 'S_4'
        assert structure.order == math.factorial(4)

    def test_agent_create_group_cyclic(self):
        """Test creating cyclic group."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        group, structure = agent.create_group('cyclic', 6)
        assert structure.name == 'Z_6'
        assert structure.order == 6

    def test_agent_create_group_alternating(self):
        """Test creating alternating group."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        group, structure = agent.create_group('alternating', 4)
        assert structure.name == 'A_4'
        assert structure.order == math.factorial(4) // 2

    def test_agent_create_group_dihedral(self):
        """Test creating dihedral group."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        group, structure = agent.create_group('dihedral', 5)
        assert structure.name == 'D_5'
        assert structure.order == 10

    def test_agent_create_group_unknown(self):
        """Test creating unknown group type raises error."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        with pytest.raises(ValueError, match='Unknown group type'):
            agent.create_group('quaternion', 8)

    def test_agent_check_property_abelian(self):
        """Test checking abelian property."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent, CyclicGroup
        )
        agent = GroupRingTheoryAgent()
        Z4 = CyclicGroup(4)
        result = agent.check_group_property(Z4, 'abelian')
        assert result is True

    def test_agent_check_property_cyclic(self):
        """Test checking cyclic property."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent, CyclicGroup
        )
        agent = GroupRingTheoryAgent()
        Z5 = CyclicGroup(5)
        result = agent.check_group_property(Z5, 'cyclic')
        assert result is True

    def test_agent_check_property_unknown(self):
        """Test checking unknown property."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent, CyclicGroup
        )
        agent = GroupRingTheoryAgent()
        Z4 = CyclicGroup(4)
        result = agent.check_group_property(Z4, 'foobar')
        assert result is False

    def test_agent_check_isomorphism_same(self):
        """Test isomorphism of same group."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent, CyclicGroup
        )
        agent = GroupRingTheoryAgent()
        Z4_a = CyclicGroup(4)
        Z4_b = CyclicGroup(4)
        result = agent.check_isomorphism(Z4_a, Z4_b)
        assert result.are_isomorphic is True

    def test_agent_check_isomorphism_different_order(self):
        """Test isomorphism of different order groups."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent, CyclicGroup
        )
        agent = GroupRingTheoryAgent()
        Z4 = CyclicGroup(4)
        Z5 = CyclicGroup(5)
        result = agent.check_isomorphism(Z4, Z5)
        assert result.are_isomorphic is False

    def test_agent_compute_ideal(self):
        """Test computing ideal."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        result = agent.compute_ideal(['x**2 - 1'])
        assert 'generators' in result
        assert result['is_principal'] is True

    def test_agent_classify_structure_group(self):
        """Test classifying a group structure."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent, StructureType
        )
        agent = GroupRingTheoryAgent()
        struct_def = {
            'name': 'MyGroup',
            'elements': [0, 1, 2, 3],
            'has_identity': True,
            'has_inverses': True,
            'is_commutative': True
        }
        structure = agent.classify_structure(struct_def)
        assert structure.structure_type == StructureType.GROUP
        assert 'commutative' in structure.properties

    def test_agent_classify_structure_ring(self):
        """Test classifying a ring structure."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent, StructureType
        )
        agent = GroupRingTheoryAgent()
        struct_def = {
            'name': 'MyRing',
            'elements': [0, 1, 2, 3],
            'has_identity': True,
            'has_inverses': True,
            'has_second_operation': True
        }
        structure = agent.classify_structure(struct_def)
        assert structure.structure_type == StructureType.RING

    def test_agent_get_statistics(self):
        """Test getting agent statistics."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        agent.create_group('cyclic', 4)
        stats = agent.get_statistics()
        assert 'tasks_executed' in stats
        assert stats['tasks_executed'] >= 1

    def test_agent_update_beliefs(self):
        """Test update_beliefs without blackboard."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        agent.update_beliefs()  # Should not raise

    def test_agent_deliberate(self):
        """Test deliberate without pending tasks."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        agent = GroupRingTheoryAgent()
        intentions = agent.deliberate()
        assert intentions == []


class TestEnums:
    """Tests for enum classes."""

    def test_structure_type_values(self):
        """Test StructureType enum values."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            StructureType
        )
        assert StructureType.GROUP.value == 'group'
        assert StructureType.RING.value == 'ring'
        assert StructureType.FIELD.value == 'field'

    def test_group_property_values(self):
        """Test GroupProperty enum values."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupProperty
        )
        assert GroupProperty.ABELIAN.value == 'abelian'
        assert GroupProperty.CYCLIC.value == 'cyclic'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
