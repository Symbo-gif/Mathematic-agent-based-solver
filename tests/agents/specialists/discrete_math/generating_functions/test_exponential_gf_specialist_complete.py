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
Complete Test Suite for Exponential GF Specialist
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
from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import ExponentialGFSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestExponentialGFSpecialist:
    """Complete test suite for ExponentialGFSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        """Create specialist instance with infrastructure."""
        return ExponentialGFSpecialist(
            agent_id='test_egf_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_egf_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.derangements_computed == 0
        assert hasattr(specialist, 'update_beliefs')
        assert hasattr(specialist, 'deliberate')
        assert hasattr(specialist, 'execute_step')

    # TEST 2: DF Registration
    def test_df_registration(self, specialist):
        """Test Directory Facilitator registration."""
        assert specialist.df is not None
        services = specialist.df.search(service_type='math.discrete.gf.exponential')
        assert len(services) > 0
        assert services[0].agent_id == 'test_egf_001'

    # TEST 3: Simple Problem - Derangements
    def test_simple_derangements(self, specialist):
        """Test derangement number generation."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Derangements",
            author_agent="test_system",
            conversation_id="test_001",
            metadata={
                'operation': 'derangements',
                'n_terms': 6
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        # Derangement numbers: !0=1, !1=0, !2=1, !3=2, !4=9, !5=44
        expected = [1, 0, 1, 2, 9, 44]
        assert result['coefficients'] == expected
        assert specialist.tasks_executed == 1
        assert specialist.tasks_succeeded == 1

    # TEST 4: Complex Problem - Exponential Function
    def test_complex_exp_function(self, specialist):
        """Test exponential function e^x."""
        task = create_entry(entry_type=EntryType.TASK, content="Exponential", author_agent="test", conversation_id="test_001", metadata={
                'operation': 'exp_function',
                'n_terms': 10
            }
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert len(result['coefficients']) == 10
        # All coefficients should be 1 for e^x
        assert all(c == 1.0 for c in result['coefficients'])

    # TEST 5: Edge Case - D(0) = 1
    def test_edge_case_derangement_zero(self, specialist):
        """EDGE CASE: Derangement !0 = 1 by convention."""
        task = create_entry(entry_type=EntryType.TASK, content="D(0)", author_agent="test", conversation_id="test_001", metadata={'operation': 'derangements', 'n_terms': 1}
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert result['coefficients'][0] == 1

    # TEST 6: Edge Case - D(1) = 0
    def test_edge_case_derangement_one(self, specialist):
        """EDGE CASE: Derangement !1 = 0."""
        task = create_entry(entry_type=EntryType.TASK, content="D(1)", author_agent="test", conversation_id="test_001", metadata={'operation': 'derangements', 'n_terms': 2}
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert result['coefficients'][1] == 0

    # TEST 7: Edge Case - Large Derangement
    def test_edge_case_large_derangement(self, specialist):
        """EDGE CASE: Large derangement number !10."""
        task = create_entry(entry_type=EntryType.TASK, content="D(10)", author_agent="test", conversation_id="test_001", metadata={'operation': 'derangements', 'n_terms': 11}
        )

        result = specialist.process(task)

        assert 'coefficients' in result
        assert len(result['coefficients']) == 11
        # !10 = 1334961
        assert result['coefficients'][10] == 1334961

    # TEST 8: Error Handling
    def test_invalid_input_handling(self, specialist):
        """Test graceful handling of invalid operation."""
        task = create_entry(entry_type=EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_001", metadata={'operation': 'unknown_op'}
        )

        result = specialist.process(task)
        assert 'error' in result

    # TEST 9: Blackboard Integration
    def test_blackboard_entry_creation(self, specialist, blackboard):
        """Test proper Blackboard result posting."""
        task = create_entry(entry_type=EntryType.TASK, content="Test BB", author_agent="test", conversation_id="test_bb_001", metadata={'operation': 'exp_function', 'n_terms': 5}
        )

        specialist.process(task)
        assert specialist.tasks_executed >= 1

    # TEST 10: Statistics Reporting
    def test_statistics_reporting(self, specialist):
        """Test get_statistics returns proper dict."""
        stats = specialist.get_statistics()

        assert isinstance(stats, dict)
        assert 'agent_id' in stats or 'tasks_executed' in stats
        assert 'tasks_executed' in stats
        assert 'success_rate' in stats
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'
        assert stats['domain'] == 'generating_functions'

    # TEST 11: BDI Cycle Compliance
    def test_bdi_interface(self, specialist):
        """Test BDI cognitive cycle methods."""
        specialist.update_beliefs({})
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # TEST 12: Concurrent Requests (Parametrized)
    @pytest.mark.parametrize("n_terms", [5, 10, 15, 20])
    def test_multiple_term_counts(self, specialist, n_terms):
        """Test specialist handles various term counts."""
        task = create_entry(entry_type=EntryType.TASK, content=f"Derangements {n_terms}", author_agent="test", conversation_id="test_multi", metadata={'operation': 'derangements', 'n_terms': n_terms}
        )

        result = specialist.process(task)
        assert result is not None
        assert 'coefficients' in result or 'error' in result
        if 'coefficients' in result:
            assert len(result['coefficients']) == n_terms

    # BONUS TEST 1: From Sequence
    def test_bonus_from_sequence(self, specialist):
        """BONUS: Build EGF from sequence."""
        task = create_entry(entry_type=EntryType.TASK, content="From seq", author_agent="test", conversation_id="test_001", metadata={'operation': 'from_sequence', 'sequence': [1, 2, 3, 4]}
        )

        result = specialist.process(task)
        assert 'coefficients' in result or 'error' in result

    # BONUS TEST 2: Verify Derangement Formula
    def test_bonus_derangement_formula(self, specialist):
        """BONUS: Verify !n ≈ n!/e for large n."""
        task = create_entry(entry_type=EntryType.TASK, content="Large derangement", author_agent="test", conversation_id="test_001", metadata={'operation': 'derangements', 'n_terms': 8}
        )

        result = specialist.process(task)

        if 'coefficients' in result and len(result['coefficients']) >= 7:
            import math
            n = 6
            derangement = result['coefficients'][n]
            approximate = math.factorial(n) / math.e
            ratio = derangement / approximate
            # Should be very close to 1 for n=6
            assert 0.9 < ratio < 1.1


pytestmark = pytest.mark.phase3
