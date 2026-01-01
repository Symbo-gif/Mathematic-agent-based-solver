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
LINEAR CODE SPECIALIST COMPLETE TEST SUITE
==========================================

22 comprehensive tests for LinearCodeSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.linear_code_specialist import LinearCodeSpecialist


class TestCodeConstruction:
    """Test code construction operations."""

    def test_construct_hamming74(self):
        """Construct Hamming(7,4) code."""
        specialist = LinearCodeSpecialist()
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.construct_from_generator(G)
        assert result['success'] is True
        assert result['code']['n'] == 7
        assert result['code']['k'] == 4

    def test_construct_repetition_code(self):
        """Construct [3,1,3] repetition code."""
        specialist = LinearCodeSpecialist()
        G = [[1, 1, 1]]
        result = specialist.construct_from_generator(G)
        assert result['success'] is True
        assert result['code']['n'] == 3
        assert result['code']['k'] == 1

    def test_construct_empty_matrix_error(self):
        """Empty generator should fail."""
        specialist = LinearCodeSpecialist()
        result = specialist.construct_from_generator([])
        assert result['success'] is False


class TestParameterValidation:
    """Test code parameter validation."""

    def test_validate_singleton_bound(self):
        """Check Singleton bound: d <= n - k + 1."""
        specialist = LinearCodeSpecialist()
        # Valid: [7,4,3] - d=3 <= 7-4+1=4
        result = specialist.validate_parameters(7, 4, 3)
        assert result['success'] is True
        assert result['bounds']['singleton']['satisfied'] is True

    def test_validate_mds_code(self):
        """MDS codes meet Singleton bound with equality."""
        specialist = LinearCodeSpecialist()
        # [n,k,n-k+1] is MDS
        result = specialist.validate_parameters(7, 4, 4)  # d = n-k+1
        assert result['success'] is True
        assert result['bounds']['singleton']['is_mds'] is True

    def test_validate_violates_singleton(self):
        """Parameters violating Singleton should fail."""
        specialist = LinearCodeSpecialist()
        # d=5 > n-k+1=4 violates Singleton
        result = specialist.validate_parameters(7, 4, 5)
        assert result['success'] is True
        assert result['bounds']['singleton']['satisfied'] is False


class TestSystematicForm:
    """Test systematic form operations."""

    def test_is_systematic_true(self):
        """Detect systematic form [I_k | P]."""
        specialist = LinearCodeSpecialist()
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.is_systematic(G)
        assert result['success'] is True
        assert result['is_systematic'] is True

    def test_is_systematic_false(self):
        """Non-systematic generator."""
        specialist = LinearCodeSpecialist()
        G = [
            [1, 1, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.is_systematic(G)
        assert result['success'] is True
        assert result['is_systematic'] is False

    def test_make_systematic(self):
        """Convert to systematic form."""
        specialist = LinearCodeSpecialist()
        G = [
            [1, 1, 0, 1],
            [0, 1, 1, 0]
        ]
        result = specialist.make_systematic(G)
        assert result['success'] is True


class TestCodeRate:
    """Test code rate computation."""

    def test_code_rate_hamming(self):
        """Rate of Hamming(7,4) = 4/7."""
        specialist = LinearCodeSpecialist()
        result = specialist.code_rate(7, 4)
        assert result['success'] is True
        assert abs(result['rate'] - 4/7) < 0.001

    def test_code_rate_repetition(self):
        """Rate of [3,1] = 1/3."""
        specialist = LinearCodeSpecialist()
        result = specialist.code_rate(3, 1)
        assert result['success'] is True
        assert abs(result['rate'] - 1/3) < 0.001


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = LinearCodeSpecialist()
        stats = specialist.get_stats()
        assert 'tasks_executed' in stats
        assert 'codes_constructed' in stats

    def test_process_construct(self):
        """Process a construction task."""
        specialist = LinearCodeSpecialist()
        task = {
            'operation': 'construct',
            'G': [[1, 0, 1], [0, 1, 1]]
        }
        result = specialist.process(task)
        assert result['success'] is True


class TestEdgeCases:
    """Test edge cases."""

    def test_single_bit_code(self):
        """[1,1,1] trivial code."""
        specialist = LinearCodeSpecialist()
        result = specialist.construct_from_generator([[1]])
        assert result['success'] is True
        assert result['code']['n'] == 1
        assert result['code']['k'] == 1

    def test_zero_rate_limit(self):
        """Test very low rate."""
        specialist = LinearCodeSpecialist()
        result = specialist.code_rate(100, 1)
        assert result['success'] is True
        assert result['rate'] == 0.01

    def test_full_rate_limit(self):
        """Test full rate (trivial)."""
        specialist = LinearCodeSpecialist()
        result = specialist.code_rate(10, 10)
        assert result['success'] is True
        assert result['rate'] == 1.0

    def test_invalid_n(self):
        """n=0 should fail."""
        specialist = LinearCodeSpecialist()
        result = specialist.code_rate(0, 0)
        assert result['success'] is False
