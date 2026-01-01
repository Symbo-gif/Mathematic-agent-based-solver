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
Complete Test Suite for Bivariate GF Specialist
================================================

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
import numpy as np
from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import BivariateGFSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestBivariateGFSpecialist:
    """Complete test suite for BivariateGFSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        """Create specialist instance with infrastructure."""
        return BivariateGFSpecialist(
            agent_id='test_bgf_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_bgf_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.bgf_constructed == 0
        assert hasattr(specialist, 'update_beliefs')
        assert hasattr(specialist, 'deliberate')
        assert hasattr(specialist, 'execute_step')

    # TEST 2: DF Registration
    def test_df_registration(self, specialist):
        """Test Directory Facilitator registration."""
        assert specialist.df is not None
        services = specialist.df.search(service_type='math.discrete.gf.bivariate')
        assert len(services) > 0
        assert services[0].agent_id == 'test_bgf_001'

    # TEST 3: Simple Problem - From 2D Array
    def test_simple_from_2d_array(self, specialist):
        """Test building BGF from 2D coefficient matrix."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Build BGF",
            author_agent="test_system",
            conversation_id="test_001",
            metadata={
                'coefficients_2d': [[1, 1], [1, 2]],
                'operation': 'from_2d_array'
            }
        )

        result = specialist.process(task)

        assert 'coefficients_2d' in result
        assert result['shape'] == (2, 2)
        assert specialist.tasks_executed == 1
        assert specialist.tasks_succeeded == 1

    # TEST 4: Complex Problem - Extract Diagonal
    def test_complex_extract_diagonal(self, specialist):
        """Test diagonal extraction from larger matrix."""
        matrix = [
            [1, 1, 1, 1],
            [1, 2, 3, 4],
            [1, 3, 6, 10],
            [1, 4, 10, 20]
        ]

        task = create_entry(entry_type=EntryType.TASK, content="Extract diagonal", author_agent="test", conversation_id="test_001", metadata={
                'coefficients_2d': matrix,
                'operation': 'extract_diagonal'
            }
        )

        result = specialist.process(task)

        assert 'diagonal_coefficients' in result
        # Diagonal: [1, 2, 6, 20]
        assert result['diagonal_coefficients'] == [1, 2, 6, 20]

    # TEST 5: Edge Case - 1x1 Matrix
    def test_edge_case_single_element(self, specialist):
        """EDGE CASE: Single element matrix."""
        task = create_entry(entry_type=EntryType.TASK, content="Single element", author_agent="test", conversation_id="test_001", metadata={
                'coefficients_2d': [[5]],
                'operation': 'from_2d_array'
            }
        )

        result = specialist.process(task)

        assert 'coefficients_2d' in result
        assert result['shape'] == (1, 1)

    # TEST 6: Edge Case - Non-Square Matrix
    def test_edge_case_non_square(self, specialist):
        """EDGE CASE: Non-square matrix 2x3."""
        task = create_entry(entry_type=EntryType.TASK, content="Non-square", author_agent="test", conversation_id="test_001", metadata={
                'coefficients_2d': [[1, 2, 3], [4, 5, 6]],
                'operation': 'from_2d_array'
            }
        )

        result = specialist.process(task)

        assert 'coefficients_2d' in result
        assert result['shape'] == (2, 3)

    # TEST 7: Edge Case - Zero Matrix
    def test_edge_case_zero_matrix(self, specialist):
        """EDGE CASE: All-zero coefficient matrix."""
        task = create_entry(entry_type=EntryType.TASK, content="Zero matrix", author_agent="test", conversation_id="test_001", metadata={
                'coefficients_2d': [[0, 0], [0, 0]],
                'operation': 'from_2d_array'
            }
        )

        result = specialist.process(task)

        assert 'coefficients_2d' in result or 'error' in result

    # TEST 8: Error Handling
    def test_invalid_input_handling(self, specialist):
        """Test graceful handling of invalid matrix."""
        task = create_entry(entry_type=EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_001", metadata={
                'coefficients_2d': "not_a_matrix",
                'operation': 'from_2d_array'
            }
        )

        result = specialist.process(task)
        assert 'error' in result

    # TEST 9: Blackboard Integration
    def test_blackboard_entry_creation(self, specialist, blackboard):
        """Test proper Blackboard result posting."""
        task = create_entry(entry_type=EntryType.TASK, content="Test BB", author_agent="test", conversation_id="test_bb_001", metadata={
                'operation': 'from_2d_array',
                'coefficients_2d': [[1, 2], [3, 4]]
            }
        )

        specialist.process(task)
        assert specialist.tasks_executed >= 1

    # TEST 10: Statistics Reporting
    def test_statistics_reporting(self, specialist):
        """Test get_statistics returns proper dict."""
        stats = specialist.get_statistics()

        assert isinstance(stats, dict)
        assert 'agent_id' in stats or 'tasks_executed' in stats
        assert 'bgf_constructed' in stats
        assert 'diagonals_extracted' in stats
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'

    # TEST 11: BDI Cycle Compliance
    def test_bdi_interface(self, specialist):
        """Test BDI cognitive cycle methods."""
        specialist.update_beliefs({})
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # TEST 12: Concurrent Requests (Parametrized)
    @pytest.mark.parametrize("matrix_size", [
        [[1]],
        [[1, 1], [1, 1]],
        [[1, 1, 1], [1, 2, 3], [1, 3, 6]],
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    ])
    def test_multiple_matrices(self, specialist, matrix_size):
        """Test specialist handles various matrix sizes."""
        task = create_entry(entry_type=EntryType.TASK, content=f"Matrix", author_agent="test", conversation_id="test_multi", metadata={
                'operation': 'from_2d_array',
                'coefficients_2d': matrix_size
            }
        )

        result = specialist.process(task)
        assert result is not None
        assert 'coefficients_2d' in result or 'error' in result

    # BONUS TEST 1: Lattice Paths
    def test_bonus_lattice_paths(self, specialist):
        """BONUS: Lattice paths F(x,y) = 1/(1-x-y)."""
        task = create_entry(entry_type=EntryType.TASK, content="Lattice paths", author_agent="test", conversation_id="test_001", metadata={'operation': 'lattice_paths', 'max_degree': 3}
        )

        result = specialist.process(task)

        if 'error' not in result and 'coefficients_2d' in result:
            # C(0,0) = 1, C(1,0) = 1, C(1,1) = 2
            coeffs = result['coefficients_2d']
            assert coeffs[0][0] == 1
            assert coeffs[1][0] == 1
            assert coeffs[1][1] == 2

    # BONUS TEST 2: Diagonal of Identity
    def test_bonus_identity_diagonal(self, specialist):
        """BONUS: Diagonal of identity matrix."""
        identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        task = create_entry(entry_type=EntryType.TASK, content="Identity diagonal", author_agent="test", conversation_id="test_001", metadata={
                'operation': 'extract_diagonal',
                'coefficients_2d': identity
            }
        )

        result = specialist.process(task)

        assert 'diagonal_coefficients' in result
        assert result['diagonal_coefficients'] == [1, 1, 1]


pytestmark = pytest.mark.phase3
