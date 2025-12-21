# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
PRIME FIELD SPECIALIST COMPLETE TEST SUITE
==========================================

20 comprehensive tests for PrimeFieldSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.prime_field_specialist import PrimeFieldSpecialist


class TestPrimeFieldCreation:
    """Test prime field construction."""

    def test_create_gf2(self):
        """Create smallest prime field GF(2)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.create_prime_field(2)
        assert result['success'] is True
        assert result['field']['p'] == 2
        assert result['field']['order'] == 2

    def test_create_gf7(self):
        """Create GF(7)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.create_prime_field(7)
        assert result['success'] is True
        assert result['field']['multiplicative_group_order'] == 6

    def test_create_large_prime(self):
        """Create large prime field."""
        specialist = PrimeFieldSpecialist()
        # 10^9 + 7 is a common cryptographic prime
        result = specialist.create_prime_field(1000000007)
        assert result['success'] is True

    def test_create_composite_fails(self):
        """Composite modulus should fail."""
        specialist = PrimeFieldSpecialist()
        result = specialist.create_prime_field(4)
        assert result['success'] is False

    def test_create_one_fails(self):
        """p=1 should fail."""
        specialist = PrimeFieldSpecialist()
        result = specialist.create_prime_field(1)
        assert result['success'] is False


class TestElementInverse:
    """Test multiplicative inverse computation."""

    def test_inverse_in_gf7(self):
        """Compute 3^(-1) in GF(7)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.field_element_inverse(3, 7)
        assert result['success'] is True
        assert result['inverse'] == 5  # 3*5 = 15 = 1 mod 7
        assert result['verification'] is True

    def test_inverse_in_gf11(self):
        """Compute inverse in GF(11)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.field_element_inverse(4, 11)
        assert result['success'] is True
        assert (4 * result['inverse']) % 11 == 1

    def test_inverse_zero_fails(self):
        """Zero has no inverse."""
        specialist = PrimeFieldSpecialist()
        result = specialist.field_element_inverse(0, 7)
        assert result['success'] is False

    def test_inverse_composite_modulus_fails(self):
        """Non-prime modulus should fail."""
        specialist = PrimeFieldSpecialist()
        result = specialist.field_element_inverse(3, 6)
        assert result['success'] is False


class TestPrimitiveElement:
    """Test primitive element (generator) finding."""

    def test_primitive_element_gf7(self):
        """Find primitive element in GF(7)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.primitive_element(7)
        assert result['success'] is True
        g = result['primitive_element']
        # g should have order 6 (= 7-1)
        assert result['order'] == 6

    def test_primitive_element_gf2(self):
        """GF(2) has trivial primitive element."""
        specialist = PrimeFieldSpecialist()
        result = specialist.primitive_element(2)
        assert result['success'] is True
        assert result['primitive_element'] == 1

    def test_primitive_element_gf13(self):
        """Find primitive element in GF(13)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.primitive_element(13)
        assert result['success'] is True
        assert result['order'] == 12


class TestElementOrder:
    """Test multiplicative order computation."""

    def test_order_identity(self):
        """Order of 1 is 1."""
        specialist = PrimeFieldSpecialist()
        result = specialist.element_order(1, 7)
        assert result['success'] is True
        assert result['order'] == 1

    def test_order_element_in_gf7(self):
        """Order of 2 in GF(7)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.element_order(2, 7)
        assert result['success'] is True
        # 2^1=2, 2^2=4, 2^3=1 mod 7, so order is 3
        assert result['order'] == 3

    def test_order_zero_fails(self):
        """Zero has no order."""
        specialist = PrimeFieldSpecialist()
        result = specialist.element_order(0, 7)
        assert result['success'] is False


class TestQuadraticResidue:
    """Test quadratic residue checks."""

    def test_qr_in_gf7(self):
        """1, 2, 4 are QR in GF(7)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.is_quadratic_residue(2, 7)
        assert result['success'] is True
        assert result['is_quadratic_residue'] is True

    def test_nqr_in_gf7(self):
        """3 is non-QR in GF(7)."""
        specialist = PrimeFieldSpecialist()
        result = specialist.is_quadratic_residue(3, 7)
        assert result['success'] is True
        assert result['is_quadratic_residue'] is False

    def test_qr_zero(self):
        """Zero is always QR."""
        specialist = PrimeFieldSpecialist()
        result = specialist.is_quadratic_residue(0, 7)
        assert result['success'] is True
        assert result['is_quadratic_residue'] is True


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = PrimeFieldSpecialist()
        stats = specialist.get_stats()
        assert 'prime_fields_created' in stats
        assert 'elements_inverted' in stats

    def test_process_create(self):
        """Process create field task."""
        specialist = PrimeFieldSpecialist()
        task = {'operation': 'create', 'p': 11}
        result = specialist.process(task)
        assert result['success'] is True
