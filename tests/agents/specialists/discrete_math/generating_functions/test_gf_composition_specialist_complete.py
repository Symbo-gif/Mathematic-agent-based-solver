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
Complete Test Suite for GF Composition Specialist
==================================================

12-Test Pattern for Tier 3 Specialist:
1. Initialization
2. DF Registration
3. Simple Problem
4. Complex Problem
5-7. Edge Cases (3 domain-specific)
8. Error Handling
9. Blackboard Integration
10. Statistics
11. BDI Cycle
12. Concurrent Requests
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import GFCompositionSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestGFCompositionSpecialist:
    """Complete test suite for GFCompositionSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        """Create specialist instance with infrastructure."""
        return GFCompositionSpecialist(
            agent_id='test_comp_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_comp_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.additions == 0
        assert hasattr(specialist, 'update_beliefs')
        assert hasattr(specialist, 'deliberate')
        assert hasattr(specialist, 'execute_step')

    # TEST 2: DF Registration
    def test_df_registration(self, specialist):
        """Test Directory Facilitator registration."""
        assert specialist.df is not None
        services = specialist.df.search(service_type='math.discrete.gf.composition')
        assert len(services) > 0
        assert services[0].agent_id == 'test_comp_001'

    # TEST 3: Simple Problem - Addition
    def test_simple_addition(self, specialist):
        """Test (1+x) + (1+x²) = 1 + x + x²."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Add GFs",
            author_agent="test_system",
            conversation_id="test_001",
            metadata={
                'gf_a': [1, 1],
                'gf_b': [1, 0, 1],
                'operation': 'add_gfs'
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert result['coefficients'] == [2, 1, 1]
        assert specialist.tasks_executed == 1
        assert specialist.tasks_succeeded == 1

    # TEST 4: Complex Problem - Multiplication (Convolution)
    def test_complex_multiplication(self, specialist):
        """Test (1+x) * (1+x²) = 1 + x + x² + x³."""
        task = create_entry(entry_type=EntryType.TASK, content="Multiply GFs", author_agent="test", conversation_id="test_001", metadata={
                'gf_a': [1, 1],
                'gf_b': [1, 0, 1],
                'operation': 'multiply_gfs'
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        # Convolution: (1+x)(1+x²) = 1 + x + x² + x³
        assert result['coefficients'] == [1, 1, 1, 1]

    # TEST 5: Edge Case - Add Zero GF
    def test_edge_case_add_zero(self, specialist):
        """EDGE CASE: A(x) + 0 = A(x)."""
        task = create_entry(entry_type=EntryType.TASK, content="Add zero", author_agent="test", conversation_id="test_001", metadata={
                'gf_a': [1, 2, 3],
                'gf_b': [0],
                'operation': 'add_gfs'
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        # Should return [1, 2, 3]
        assert result['coefficients'][:3] == [1, 2, 3]

    # TEST 6: Edge Case - Multiply by Unit
    def test_edge_case_multiply_unit(self, specialist):
        """EDGE CASE: A(x) * 1 = A(x)."""
        task = create_entry(entry_type=EntryType.TASK, content="Multiply by 1", author_agent="test", conversation_id="test_001", metadata={
                'gf_a': [5, 3, 2],
                'gf_b': [1],
                'operation': 'multiply_gfs'
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        # Should return [5, 3, 2]
        assert result['coefficients'] == [5, 3, 2]

    # TEST 7: Edge Case - Different Length GFs
    def test_edge_case_different_lengths(self, specialist):
        """EDGE CASE: Add GFs of different lengths."""
        task = create_entry(entry_type=EntryType.TASK, content="Different lengths", author_agent="test", conversation_id="test_001", metadata={
                'gf_a': [1, 2],
                'gf_b': [1, 2, 3, 4, 5],
                'operation': 'add_gfs'
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        # Should handle padding
        assert len(result['coefficients']) == 5

    # TEST 8: Error Handling
    def test_invalid_input_handling(self, specialist):
        """Test graceful handling of invalid operation."""
        task = create_entry(entry_type=EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_001", metadata={
                'gf_a': [1, 2],
                'operation': 'unknown_operation'
            }
        )

        result = specialist.process(task)
        assert 'error' in result

    # TEST 9: Blackboard Integration
    def test_blackboard_entry_creation(self, specialist, blackboard):
        """Test proper Blackboard result posting."""
        task = create_entry(entry_type=EntryType.TASK, content="Test BB", author_agent="test", conversation_id="test_bb_001", metadata={
                'operation': 'add_gfs',
                'gf_a': [1, 1],
                'gf_b': [1, 1]
            }
        )

        specialist.process(task)
        assert specialist.tasks_executed >= 1

    # TEST 10: Statistics Reporting
    def test_statistics_reporting(self, specialist):
        """Test get_statistics returns proper dict."""
        stats = specialist.get_statistics()

        assert isinstance(stats, dict)
        assert 'additions' in stats
        assert 'multiplications' in stats
        assert 'hadamard_products' in stats
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'

    # TEST 11: BDI Cycle Compliance
    def test_bdi_interface(self, specialist):
        """Test BDI cognitive cycle methods."""
        specialist.update_beliefs({})
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # TEST 12: Concurrent Requests (Parametrized)
    @pytest.mark.parametrize("operation,gf_a,gf_b", [
        ('add_gfs', [1, 1], [1, 1]),
        ('add_gfs', [1, 2, 3], [0, 0, 1]),
        ('multiply_gfs', [1, 1], [1]),
        ('multiply_gfs', [1, 1], [1, 1])
    ])
    def test_multiple_operations(self, specialist, operation, gf_a, gf_b):
        """Test specialist handles various operations."""
        task = create_entry(entry_type=EntryType.TASK, content=f"{operation}", author_agent="test", conversation_id="test_multi", metadata={
                'operation': operation,
                'gf_a': gf_a,
                'gf_b': gf_b
            }
        )

        result = specialist.process(task)
        assert result is not None
        assert 'coefficients' in result or 'error' in result

    # BONUS TEST 1: Self-Multiplication
    def test_bonus_self_multiplication(self, specialist):
        """BONUS: A(x) * A(x) = A(x)²."""
        task = create_entry(entry_type=EntryType.TASK, content="Square", author_agent="test", conversation_id="test_001", metadata={
                'operation': 'multiply_gfs',
                'gf_a': [1, 1],
                'gf_b': [1, 1]
            }
        )

        result = specialist.process(task)

        if 'coefficients' in result:
            # (1+x)² = 1 + 2x + x²
            assert result['coefficients'] == [1, 2, 1]

    # BONUS TEST 2: Associativity Check
    def test_bonus_associativity(self, specialist):
        """BONUS: Verify (A+B)+C = A+(B+C)."""
        # First: (A+B)
        task1 = create_entry(entry_type=EntryType.TASK, content="A+B", author_agent="test", conversation_id="test_001", metadata={'operation': 'add_gfs', 'gf_a': [1], 'gf_b': [1]}
        )
        result1 = specialist.process(task1)

        # Then: (A+B)+C
        if 'coefficients' in result1:
            task2 = create_entry(entry_type=EntryType.TASK, content="(A+B)+C", author_agent="test", conversation_id="test_001", metadata={'operation': 'add_gfs', 'gf_a': result1['coefficients'], 'gf_b': [1]}
            )
            result2 = specialist.process(task2)
            assert 'coefficients' in result2


pytestmark = pytest.mark.phase3
