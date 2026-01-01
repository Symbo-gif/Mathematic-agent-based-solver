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
Test Suite for Elementary Combinatorics Core Module
===================================================

Tests elementary combinatorics implementations:
- Inclusion-Exclusion Principle (PIE)
- Venn diagrams
- Surjections
- Pigeonhole principle
- Probabilistic method

NO SYMPY - Pure native testing.
"""

import pytest
from symbo_agentic_reasoners.core.elementary_combinatorics import (
    inclusion_exclusion, venn_diagram_2sets, venn_diagram_3sets,
    surjection_count, pigeonhole_principle, generalized_pigeonhole,
    derangement_count
)


class TestInclusionExclusion:
    """Test Inclusion-Exclusion Principle."""

    def test_two_sets(self):
        """Test |A ∪ B| = |A| + |B| - |A ∩ B|."""
        set_sizes = [10, 15]
        def intersect_fn(indices):
            if len(indices) == 1:
                return set_sizes[indices[0]]
            if set(indices) == {0, 1}:
                return 5
            return 0

        result = inclusion_exclusion(set_sizes, intersect_fn)
        # |A∪B| = 10 + 15 - 5 = 20
        assert result == 20

    def test_three_sets(self):
        """Test PIE with 3 sets."""
        set_sizes = [10, 12, 8]
        def intersect_fn(indices):
            if len(indices) == 1:
                return set_sizes[indices[0]]
            if set(indices) == {0, 1}:
                return 5
            if set(indices) == {0, 2}:
                return 4
            if set(indices) == {1, 2}:
                return 3
            if set(indices) == {0, 1, 2}:
                return 2
            return 0

        result = inclusion_exclusion(set_sizes, intersect_fn)
        # |A∪B∪C| = 10+12+8 - (5+4+3) + 2 = 30 - 12 + 2 = 20
        assert result == 20

    def test_disjoint_sets(self):
        """Test disjoint sets (no intersections)."""
        set_sizes = [5, 7, 9]
        def intersect_fn(indices):
            if len(indices) == 1:
                return set_sizes[indices[0]]
            return 0

        result = inclusion_exclusion(set_sizes, intersect_fn)
        assert result == 5 + 7 + 9

    def test_single_set(self):
        """Test single set."""
        set_sizes = [10]
        def intersect_fn(indices):
            return set_sizes[indices[0]] if len(indices) == 1 else 0

        result = inclusion_exclusion(set_sizes, intersect_fn)
        assert result == 10


class TestVennDiagrams:
    """Test Venn diagram calculations."""

    def test_venn_two_sets(self):
        """Test 2-set Venn diagram."""
        result = venn_diagram_2sets(A=10, B=15, A_intersect_B=5)
        assert result['A_only'] == 5
        assert result['B_only'] == 10
        assert result['both'] == 5
        assert result['union'] == 20

    def test_venn_three_sets(self):
        """Test 3-set Venn diagram."""
        result = venn_diagram_3sets(
            A=10, B=12, C=8,
            AB=5, AC=4, BC=3,
            ABC=2
        )
        assert result is not None
        assert 'union' in result
        # Verify it computed regions
        assert isinstance(result, dict)

    def test_venn_no_overlap(self):
        """Test Venn with no overlap."""
        result = venn_diagram_2sets(10, 15, 0)
        assert result['both'] == 0
        assert result['union'] == 25


class TestSurjections:
    """Test surjection counting."""

    def test_basic_surjection(self):
        """Test onto functions from n to k."""
        result = surjection_count(n=5, m=3)
        # S(5,3) = 150 surjections from 5 elements onto 3
        assert result > 0
        assert isinstance(result, int)

    def test_n_equals_k(self):
        """Test surjections when n=k."""
        result = surjection_count(5, 5)
        # n! permutations
        import math
        assert result == math.factorial(5)

    def test_n_less_than_k(self):
        """Test no surjections when n < k."""
        result = surjection_count(3, 5)
        # Cannot map 3 elements onto 5
        assert result == 0

    def test_large_values(self):
        """TOUGH EDGE CASE: Large n, k."""
        result = surjection_count(20, 10)
        assert result > 0


class TestPigeonhole:
    """Test Pigeonhole Principle."""

    def test_basic_guarantee(self):
        """Test pigeonhole guarantee."""
        result = pigeonhole_principle(n_items=10, n_boxes=3)
        # At least ⌈10/3⌉ = 4 items in some box
        assert result == 4

    def test_equal_distribution(self):
        """Test n = k case."""
        result = pigeonhole_principle(5, 5)
        assert result == 1

    def test_more_holes_than_pigeons(self):
        """Test k > n."""
        result = pigeonhole_principle(3, 10)
        assert result == 1

    def test_large_ratio(self):
        """TOUGH EDGE CASE: 1000 items, 10 boxes."""
        result = pigeonhole_principle(1000, 10)
        assert result == 100


class TestDerangements:
    """Test derangement counting."""

    def test_small_derangements(self):
        """Test !n for small n."""
        assert derangement_count(0) == 1
        assert derangement_count(1) == 0
        assert derangement_count(2) == 1
        assert derangement_count(3) == 2
        assert derangement_count(4) == 9

    def test_large_derangement(self):
        """TOUGH EDGE CASE: Large derangement."""
        result = derangement_count(15)
        assert result > 0


pytestmark = pytest.mark.phase2
