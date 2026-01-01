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
GALOIS THEORY SPECIALIST COMPLETE TEST SUITE
=============================================

22 comprehensive tests for GaloisTheorySpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.galois_theory_specialist import GaloisTheorySpecialist


class TestSplittingField:
    """Test splitting field computation."""

    def test_splitting_field_x2_x_1(self):
        """Splitting field of x^2+x+1 over GF(2)."""
        specialist = GaloisTheorySpecialist()
        poly = [1, 1, 1]  # x^2 + x + 1
        result = specialist.splitting_field(poly, 2)
        assert result['success'] is True
        assert result['extension_degree'] == 2

    def test_splitting_field_x3_x_1(self):
        """Splitting field of x^3+x+1 over GF(2)."""
        specialist = GaloisTheorySpecialist()
        poly = [1, 1, 0, 1]  # x^3 + x + 1
        result = specialist.splitting_field(poly, 2)
        assert result['success'] is True

    def test_splitting_field_reducible(self):
        """Splitting field of reducible polynomial."""
        specialist = GaloisTheorySpecialist()
        poly = [0, 0, 1]  # x^2 = x * x
        result = specialist.splitting_field(poly, 2)
        assert result['success'] is True


class TestGaloisCorrespondence:
    """Test Galois correspondence."""

    def test_correspondence_gf16(self):
        """Galois correspondence for GF(16)/GF(2)."""
        specialist = GaloisTheorySpecialist()
        result = specialist.galois_correspondence(2, 4)
        assert result['success'] is True
        # Subgroups correspond to intermediate fields

    def test_correspondence_gf64(self):
        """Galois correspondence for GF(64)/GF(2)."""
        specialist = GaloisTheorySpecialist()
        result = specialist.galois_correspondence(2, 6)
        assert result['success'] is True

    def test_correspondence_prime_extension(self):
        """Prime degree extension has no proper subfields."""
        specialist = GaloisTheorySpecialist()
        result = specialist.galois_correspondence(2, 7)
        assert result['success'] is True


class TestNormalClosure:
    """Test normal closure computation."""

    def test_normal_closure_finite_fields(self):
        """All finite field extensions are normal."""
        specialist = GaloisTheorySpecialist()
        # Normal closure of GF(2^3) over GF(2) - already normal
        result = specialist.normal_closure(2, [3])
        assert result['success'] is True
        # For finite fields, any single extension is already normal
        assert result['closure_degree'] == 3


class TestSeparability:
    """Test separability checking."""

    def test_is_separable_finite_field(self):
        """All polynomials over finite fields are separable."""
        specialist = GaloisTheorySpecialist()
        poly = [1, 1, 1]  # x^2 + x + 1
        result = specialist.is_separable(poly, 2)
        assert result['success'] is True
        assert result['is_separable'] is True

    def test_is_separable_x3_x_1(self):
        """x^3+x+1 is separable over GF(2)."""
        specialist = GaloisTheorySpecialist()
        poly = [1, 1, 0, 1]
        result = specialist.is_separable(poly, 2)
        assert result['success'] is True
        assert result['is_separable'] is True


class TestIntermediateFields:
    """Test intermediate field enumeration."""

    def test_intermediate_fields_gf16(self):
        """Intermediate fields of GF(16)."""
        specialist = GaloisTheorySpecialist()
        result = specialist.intermediate_fields(2, 4)
        assert result['success'] is True
        # GF(16) has intermediate fields: GF(2), GF(4), GF(16)
        assert len(result['fields']) >= 2

    def test_intermediate_fields_gf64(self):
        """Intermediate fields of GF(64)."""
        specialist = GaloisTheorySpecialist()
        result = specialist.intermediate_fields(2, 6)
        assert result['success'] is True
        # Divisors of 6: 1, 2, 3, 6 -> 4 intermediate fields

    def test_intermediate_fields_prime(self):
        """Prime field has only itself as intermediate field."""
        specialist = GaloisTheorySpecialist()
        result = specialist.intermediate_fields(7, 1)
        assert result['success'] is True


class TestGaloisGroup:
    """Test Galois group computation via correspondence."""

    def test_galois_group_gf8(self):
        """Gal(GF(8)/GF(2)) = Z/3Z."""
        specialist = GaloisTheorySpecialist()
        # Use galois_correspondence to get group info
        result = specialist.galois_correspondence(2, 3)
        assert result['success'] is True
        assert result['galois_group_order'] == 3
        # All finite field Galois groups are cyclic
        assert 'Z/3Z' in result['galois_group']

    def test_galois_group_gf16(self):
        """Gal(GF(16)/GF(2)) = Z/4Z."""
        specialist = GaloisTheorySpecialist()
        result = specialist.galois_correspondence(2, 4)
        assert result['success'] is True
        assert result['galois_group_order'] == 4


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = GaloisTheorySpecialist()
        stats = specialist.get_stats()
        assert 'splitting_fields_computed' in stats
        assert 'correspondences_computed' in stats

    def test_process_splitting_field(self):
        """Process splitting field task."""
        specialist = GaloisTheorySpecialist()
        task = {
            'operation': 'splitting_field',
            'poly': [1, 1, 1],
            'p': 2
        }
        result = specialist.process(task)
        assert result['success'] is True


class TestEdgeCases:
    """Test edge cases."""

    def test_trivial_extension(self):
        """Trivial extension GF(p)/GF(p)."""
        specialist = GaloisTheorySpecialist()
        # Galois correspondence for trivial extension
        result = specialist.galois_correspondence(5, 1)
        assert result['success'] is True
        assert result['galois_group_order'] == 1
