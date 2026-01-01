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
HAMMING DISTANCE SPECIALIST COMPLETE TEST SUITE
================================================

20 comprehensive tests for HammingDistanceSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.hamming_distance_specialist import HammingDistanceSpecialist


class TestDistanceComputation:
    """Test Hamming distance computation."""

    def test_distance_identical(self):
        """Distance between identical vectors is 0."""
        specialist = HammingDistanceSpecialist()
        result = specialist.compute_distance([1, 0, 1, 0], [1, 0, 1, 0])
        assert result['success'] is True
        assert result['distance'] == 0

    def test_distance_all_different(self):
        """All positions differ."""
        specialist = HammingDistanceSpecialist()
        result = specialist.compute_distance([0, 0, 0, 0], [1, 1, 1, 1])
        assert result['success'] is True
        assert result['distance'] == 4

    def test_distance_partial(self):
        """Some positions differ."""
        specialist = HammingDistanceSpecialist()
        result = specialist.compute_distance([1, 0, 1, 0], [1, 1, 0, 0])
        assert result['success'] is True
        assert result['distance'] == 2

    def test_distance_length_mismatch(self):
        """Different lengths should fail."""
        specialist = HammingDistanceSpecialist()
        result = specialist.compute_distance([1, 0, 1], [1, 0])
        assert result['success'] is False


class TestWeightComputation:
    """Test Hamming weight computation."""

    def test_weight_zero(self):
        """All-zero vector has weight 0."""
        specialist = HammingDistanceSpecialist()
        result = specialist.compute_weight([0, 0, 0, 0])
        assert result['success'] is True
        assert result['weight'] == 0

    def test_weight_all_ones(self):
        """All-one vector has weight n."""
        specialist = HammingDistanceSpecialist()
        result = specialist.compute_weight([1, 1, 1, 1, 1])
        assert result['success'] is True
        assert result['weight'] == 5

    def test_weight_mixed(self):
        """Mixed vector."""
        specialist = HammingDistanceSpecialist()
        result = specialist.compute_weight([1, 0, 1, 0, 1])
        assert result['success'] is True
        assert result['weight'] == 3


class TestMinimumWeight:
    """Test minimum weight computation."""

    def test_minimum_weight_hamming(self):
        """Hamming(7,4) has d_min = 3."""
        specialist = HammingDistanceSpecialist()
        # Use actual weight-3 codewords from Hamming(7,4)
        codewords = [
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 0, 0],  # weight 3
            [0, 1, 1, 0, 1, 0, 0],  # weight 3
            [1, 0, 1, 0, 0, 1, 0]   # weight 3
        ]
        result = specialist.minimum_weight(codewords)
        assert result['success'] is True
        assert result['minimum_weight'] == 3

    def test_minimum_weight_empty(self):
        """Empty codeword list should fail."""
        specialist = HammingDistanceSpecialist()
        result = specialist.minimum_weight([])
        assert result['success'] is False


class TestSphereVolume:
    """Test sphere volume computation."""

    def test_sphere_volume_radius_0(self):
        """V(n,0) = 1."""
        specialist = HammingDistanceSpecialist()
        result = specialist.sphere_volume(7, 0)
        assert result['success'] is True
        assert result['volume'] == 1

    def test_sphere_volume_radius_1(self):
        """V(n,1) = 1 + n."""
        specialist = HammingDistanceSpecialist()
        result = specialist.sphere_volume(7, 1)
        assert result['success'] is True
        assert result['volume'] == 8  # 1 + 7

    def test_sphere_volume_full(self):
        """V(n,n) = 2^n for binary."""
        specialist = HammingDistanceSpecialist()
        result = specialist.sphere_volume(4, 4)
        assert result['success'] is True
        assert result['volume'] == 16  # 2^4

    def test_sphere_volume_t_exceeds_n(self):
        """t > n should fail."""
        specialist = HammingDistanceSpecialist()
        result = specialist.sphere_volume(5, 6)
        assert result['success'] is False


class TestErrorCapability:
    """Test error capability computation."""

    def test_error_capability_d3(self):
        """d=3: detects 2, corrects 1."""
        specialist = HammingDistanceSpecialist()
        result = specialist.error_capability(3)
        assert result['success'] is True
        assert result['detection_capability'] == 2
        assert result['correction_capability'] == 1

    def test_error_capability_d7(self):
        """d=7: detects 6, corrects 3."""
        specialist = HammingDistanceSpecialist()
        result = specialist.error_capability(7)
        assert result['success'] is True
        assert result['detection_capability'] == 6
        assert result['correction_capability'] == 3


class TestDistanceDistribution:
    """Test distance distribution computation."""

    def test_distribution_small_code(self):
        """Compute distance distribution."""
        specialist = HammingDistanceSpecialist()
        codewords = [
            [0, 0, 0],
            [1, 1, 1],
        ]
        result = specialist.distance_distribution(codewords)
        assert result['success'] is True
        assert result['minimum_distance'] == 3


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = HammingDistanceSpecialist()
        stats = specialist.get_stats()
        assert 'distances_computed' in stats
        assert 'weights_computed' in stats
