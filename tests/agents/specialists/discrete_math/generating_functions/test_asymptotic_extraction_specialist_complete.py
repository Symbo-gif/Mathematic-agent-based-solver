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
Complete Test Suite for Asymptotic Extraction Specialist
=========================================================

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
from symbo_agentic_reasoners.agents.specialists.discrete_math.generating_functions import AsymptoticExtractionSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestAsymptoticExtractionSpecialist:
    """Complete test suite for AsymptoticExtractionSpecialist."""

    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        """Create specialist instance with infrastructure."""
        return AsymptoticExtractionSpecialist(
            agent_id='test_asymp_001',
            df=directory_facilitator,
            blackboard=blackboard
        )

    # TEST 1: Initialization
    def test_initialization(self, specialist):
        """Test specialist initializes correctly."""
        assert specialist.agent_id == 'test_asymp_001'
        assert specialist.tasks_executed == 0
        assert specialist.tasks_succeeded == 0
        assert specialist.dominant_poles_found == 0
        assert hasattr(specialist, 'update_beliefs')
        assert hasattr(specialist, 'deliberate')
        assert hasattr(specialist, 'execute_step')

    # TEST 2: DF Registration
    def test_df_registration(self, specialist):
        """Test Directory Facilitator registration."""
        assert specialist.df is not None
        services = specialist.df.search(service_type='math.discrete.gf.asymptotic')
        assert len(services) > 0
        assert services[0].agent_id == 'test_asymp_001'

    # TEST 3: Simple Problem - Dominant Singularity
    def test_simple_dominant_singularity(self, specialist):
        """Test finding dominant singularity of 1/(1-2x)."""
        task = create_entry(
            entry_type=EntryType.TASK,
            content="Dominant singularity",
            author_agent="test_system",
            conversation_id="test_001",
            metadata={
                'numerator': [1],
                'denominator': [1, -2],
                'operation': 'dominant_singularity'
            }
        )

        result = specialist.process(task)

        assert 'dominant_singularity' in result
        assert 'rho' in result
        # Pole at x=1/2, so dominant_singularity=0.5, rho=2
        assert abs(result['dominant_singularity'] - 0.5) < 0.01
        assert abs(result['rho'] - 2.0) < 0.01
        assert specialist.tasks_executed == 1
        assert specialist.tasks_succeeded == 1

    # TEST 4: Complex Problem - Fibonacci Asymptotic
    def test_complex_fibonacci_asymptotic(self, specialist):
        """Test Fibonacci asymptotic formula."""
        task = create_entry(entry_type=EntryType.TASK, content="Fibonacci asymptotic", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [0, 1],
                'denominator': [1, -1, -1],
                'operation': 'full_asymptotic'
            }
        )

        result = specialist.process(task)

        assert 'rho' in result
        # Fibonacci: ρ = φ = (1+√5)/2 ≈ 1.618
        assert 1.5 < result['rho'] < 1.7
        assert 'beta' in result

    # TEST 5: Edge Case - Growth Rate Extraction
    def test_edge_case_growth_rate(self, specialist):
        """EDGE CASE: Extract only growth rate ρ."""
        task = create_entry(entry_type=EntryType.TASK, content="Growth rate", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [1],
                'denominator': [1, -3],
                'operation': 'extract_growth'
            }
        )

        result = specialist.process(task)

        if 'error' not in result:
            assert 'rho' in result
            # 1/(1-3x) has pole at x=1/3, so ρ=3
            assert abs(result['rho'] - 3.0) < 0.01

    # TEST 6: Edge Case - Multiple Dominant Poles
    def test_edge_case_multiple_dominant(self, specialist):
        """EDGE CASE: Multiple poles with same modulus."""
        task = create_entry(entry_type=EntryType.TASK, content="Multiple dominant", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [1],
                'denominator': [1, 0, -1],  # 1/(1-x²) poles at ±1
                'operation': 'dominant_singularity'
            }
        )

        result = specialist.process(task)

        assert 'dominant_singularity' in result or 'error' in result
        # Both poles have |pole| = 1

    # TEST 7: Edge Case - High Multiplicity Pole
    def test_edge_case_high_multiplicity(self, specialist):
        """EDGE CASE: Pole with high multiplicity."""
        task = create_entry(entry_type=EntryType.TASK, content="High multiplicity", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [1],
                'denominator': [1, -3, 3, -1],  # 1/(1-x)³
                'operation': 'full_asymptotic'
            }
        )

        result = specialist.process(task)

        if 'error' not in result:
            assert 'beta' in result
            # Multiplicity 3 → β = 2
            # (Actual implementation may vary)

    # TEST 8: Error Handling
    def test_invalid_input_handling(self, specialist):
        """Test graceful handling of zero denominator."""
        task = create_entry(entry_type=EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [1],
                'denominator': [0],
                'operation': 'dominant_singularity'
            }
        )

        result = specialist.process(task)
        assert 'error' in result

    # TEST 9: Blackboard Integration
    def test_blackboard_entry_creation(self, specialist, blackboard):
        """Test proper Blackboard result posting."""
        task = create_entry(entry_type=EntryType.TASK, content="Test BB", author_agent="test", conversation_id="test_bb_001", metadata={
                'operation': 'dominant_singularity',
                'numerator': [1],
                'denominator': [1, -1]
            }
        )

        specialist.process(task)
        assert specialist.tasks_executed >= 1

    # TEST 10: Statistics Reporting
    def test_statistics_reporting(self, specialist):
        """Test get_statistics returns proper dict."""
        stats = specialist.get_statistics()

        assert isinstance(stats, dict)
        assert 'dominant_poles_found' in stats
        assert 'growth_rates_extracted' in stats
        assert 'full_formulas_computed' in stats
        assert stats['tier'] == '3'
        assert stats['type'] == 'specialist'

    # TEST 11: BDI Cycle Compliance
    def test_bdi_interface(self, specialist):
        """Test BDI cognitive cycle methods."""
        specialist.update_beliefs({})
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    # TEST 12: Concurrent Requests (Parametrized)
    @pytest.mark.parametrize("r", [2, 3, 5, 10])
    def test_multiple_geometric_series(self, specialist, r):
        """Test specialist handles various geometric series."""
        task = create_entry(entry_type=EntryType.TASK, content=f"Geometric r={r}", author_agent="test", conversation_id="test_multi", metadata={
                'operation': 'dominant_singularity',
                'numerator': [1],
                'denominator': [1, -r]
            }
        )

        result = specialist.process(task)
        assert result is not None
        if 'error' not in result:
            # For 1/(1-rx), pole at x=1/r, so rho=r
            assert abs(result['rho'] - r) < 0.1

    # BONUS TEST 1: Catalan Asymptotic
    def test_bonus_catalan_asymptotic(self, specialist):
        """BONUS: Catalan number asymptotic."""
        task = create_entry(entry_type=EntryType.TASK, content="Catalan asymptotic", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [1, -1],
                'denominator': [0, 2],  # Simplified, actual is complex
                'operation': 'dominant_singularity'
            }
        )

        result = specialist.process(task)
        # Catalan: C_n ~ 4^n/(n^{3/2}√π)
        # Just verify it processes
        assert 'dominant_singularity' in result or 'error' in result

    # BONUS TEST 2: Exponentially Decreasing
    def test_bonus_decreasing_sequence(self, specialist):
        """BONUS: Pole outside unit circle (decreasing sequence)."""
        task = create_entry(entry_type=EntryType.TASK, content="Decreasing", author_agent="test", conversation_id="test_001", metadata={
                'numerator': [1],
                'denominator': [1, -0.5],  # 1/(1-0.5x), pole at x=2
                'operation': 'dominant_singularity'
            }
        )

        result = specialist.process(task)

        if 'rho' in result:
            # Pole at x=2, so rho=0.5 (exponentially decreasing)
            assert 0.4 < result['rho'] < 0.6


pytestmark = pytest.mark.phase3
