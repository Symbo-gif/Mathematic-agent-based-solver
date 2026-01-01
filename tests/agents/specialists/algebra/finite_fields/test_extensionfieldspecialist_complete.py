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
EXTENSION FIELD SPECIALIST COMPLETE TEST SUITE
==============================================

22 comprehensive tests for ExtensionFieldSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.extension_field_specialist import ExtensionFieldSpecialist


class TestFieldConstruction:
    """Test extension field construction."""

    def test_construct_gf4(self):
        """Construct GF(4) = GF(2^2)."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(2, 2)
        assert result['success'] is True
        assert result['field']['order'] == 4

    def test_construct_gf8(self):
        """Construct GF(8) = GF(2^3)."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(2, 3)
        assert result['success'] is True
        assert result['field']['order'] == 8

    def test_construct_trivial_n1(self):
        """n=1 gives prime field."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(5, 1)
        assert result['success'] is True
        assert result['field']['is_extension'] is False

    def test_construct_with_irred(self):
        """Construct with provided irreducible."""
        specialist = ExtensionFieldSpecialist()
        # x^2 + x + 1 is irreducible over GF(2)
        result = specialist.construct_extension_field(2, 2, [1, 1, 1])
        assert result['success'] is True

    def test_construct_invalid_p(self):
        """Composite p should fail."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(4, 2)
        assert result['success'] is False


class TestSubfieldDetection:
    """Test subfield detection."""

    def test_detect_subfield_gf2_in_gf8(self):
        """GF(2) is subfield of GF(8)."""
        specialist = ExtensionFieldSpecialist()
        # detect_subfield takes (p, n, d) primitives
        result = specialist.detect_subfield(2, 3, 1)
        assert result['success'] is True
        assert result['is_subfield'] is True

    def test_detect_subfield_gf4_in_gf16(self):
        """GF(4) is subfield of GF(16) since 2 | 4."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.detect_subfield(2, 4, 2)
        assert result['success'] is True
        assert result['is_subfield'] is True

    def test_detect_subfield_not_divisor(self):
        """GF(4) is not subfield of GF(8) since 2 does not divide 3."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.detect_subfield(2, 3, 2)
        assert result['success'] is True
        assert result['is_subfield'] is False


class TestElementOperations:
    """Test element creation and conversion."""

    def test_create_element(self):
        """Create element from coefficients."""
        specialist = ExtensionFieldSpecialist()
        field = specialist.construct_extension_field(2, 3)
        irred_poly = field['field']['irred_poly']
        # create_element takes (coeffs, p, irred_poly)
        result = specialist.create_element([1, 0, 1], 2, irred_poly)
        assert result['success'] is True

    def test_element_to_polynomial(self):
        """Convert element to polynomial representation."""
        specialist = ExtensionFieldSpecialist()
        # element_to_polynomial just takes coefficients
        result = specialist.element_to_polynomial([1, 1])
        assert result['success'] is True

    def test_degree_computation(self):
        """Compute extension degree."""
        specialist = ExtensionFieldSpecialist()
        field = specialist.construct_extension_field(3, 4)
        result = specialist.degree(field['field'])
        assert result['success'] is True
        assert result['degree'] == 4


class TestAESField:
    """Test AES-related field (Rijndael)."""

    def test_construct_gf256(self):
        """Construct GF(256) = GF(2^8) for AES."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(2, 8)
        assert result['success'] is True
        assert result['field']['order'] == 256


class TestNonBinaryFields:
    """Test non-binary extension fields."""

    def test_gf9(self):
        """Construct GF(9) = GF(3^2)."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(3, 2)
        assert result['success'] is True
        assert result['field']['order'] == 9

    def test_gf25(self):
        """Construct GF(25) = GF(5^2)."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(5, 2)
        assert result['success'] is True
        assert result['field']['order'] == 25


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = ExtensionFieldSpecialist()
        stats = specialist.get_stats()
        assert 'extension_fields_created' in stats
        assert 'subfields_detected' in stats

    def test_process_construct(self):
        """Process construct task."""
        specialist = ExtensionFieldSpecialist()
        task = {'operation': 'construct', 'p': 2, 'n': 4}
        result = specialist.process(task)
        assert result['success'] is True


class TestEdgeCases:
    """Test edge cases."""

    def test_large_extension(self):
        """Larger extension field (GF(2^10) = 1024 elements)."""
        specialist = ExtensionFieldSpecialist()
        result = specialist.construct_extension_field(2, 10)
        assert result['success'] is True
        assert result['field']['order'] == 1024

    def test_invalid_irred_degree(self):
        """Wrong degree irreducible should fail."""
        specialist = ExtensionFieldSpecialist()
        # Degree 2 poly for degree 3 extension
        result = specialist.construct_extension_field(2, 3, [1, 1, 1])
        assert result['success'] is False
