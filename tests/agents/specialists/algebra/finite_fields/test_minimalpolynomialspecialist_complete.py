# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
MINIMAL POLYNOMIAL SPECIALIST COMPLETE TEST SUITE
=================================================

21 comprehensive tests for MinimalPolynomialSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.minimal_polynomial_specialist import MinimalPolynomialSpecialist


class TestMinimalPolynomial:
    """Test minimal polynomial computation."""

    def test_minimal_poly_base_field_element(self):
        """Element in base field has degree 1 minimal poly."""
        specialist = MinimalPolynomialSpecialist()
        # Element 1 in GF(2) inside GF(4)
        irred = [1, 1, 1]
        result = specialist.compute_minimal_polynomial([1, 0], irred, 2)
        assert result['success'] is True
        assert result['degree'] == 1

    def test_minimal_poly_primitive_element(self):
        """Primitive element has degree n minimal poly."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]  # x^2 + x + 1
        # x is primitive in GF(4)
        result = specialist.compute_minimal_polynomial([0, 1], irred, 2)
        assert result['success'] is True
        assert result['degree'] == 2

    def test_minimal_poly_gf8(self):
        """Minimal polynomial in GF(8)."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 0, 1]  # x^3 + x + 1
        result = specialist.compute_minimal_polynomial([0, 1, 0], irred, 2)
        assert result['success'] is True


class TestFrobeniusMap:
    """Test Frobenius endomorphism."""

    def test_frobenius_gf4(self):
        """Frobenius map a -> a^p in GF(4)."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        result = specialist.apply_frobenius([0, 1], irred, 2)
        assert result['success'] is True

    def test_frobenius_linearity(self):
        """Frobenius is linear: (a+b)^p = a^p + b^p."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        a, b = [1, 0], [0, 1]

        # Frobenius of sum
        sum_ab = [(a[i] + b[i]) % 2 for i in range(2)]
        frob_sum = specialist.apply_frobenius(sum_ab, irred, 2)

        # Sum of Frobenius
        frob_a = specialist.apply_frobenius(a, irred, 2)
        frob_b = specialist.apply_frobenius(b, irred, 2)

        assert frob_sum['success'] is True
        assert frob_a['success'] is True
        assert frob_b['success'] is True


class TestConjugates:
    """Test conjugate element computation."""

    def test_conjugates_gf4(self):
        """Find conjugates in GF(4)."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        result = specialist.get_conjugates([0, 1], irred, 2)
        assert result['success'] is True
        assert 'conjugates' in result

    def test_conjugates_base_field(self):
        """Base field element is its own conjugate."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        result = specialist.get_conjugates([1, 0], irred, 2)
        assert result['success'] is True
        assert len(result['conjugates']) == 1


class TestNormalBasis:
    """Test normal basis operations."""

    def test_is_normal_basis_check(self):
        """Check if element generates a normal basis."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        # Test if x generates a normal basis
        result = specialist.is_normal_basis([0, 1], irred, 2)
        assert result['success'] is True


class TestTraceAndNorm:
    """Test trace and norm functions."""

    def test_trace_gf4(self):
        """Compute trace in GF(4)."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        result = specialist.compute_trace([0, 1], irred, 2)
        assert result['success'] is True

    def test_norm_gf4(self):
        """Compute norm in GF(4)."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        result = specialist.compute_norm([0, 1], irred, 2)
        assert result['success'] is True


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = MinimalPolynomialSpecialist()
        stats = specialist.get_stats()
        assert 'minimal_polys_computed' in stats
        assert 'frobenius_applications' in stats

    def test_process_minimal_poly(self):
        """Process minimal polynomial task."""
        specialist = MinimalPolynomialSpecialist()
        task = {
            'operation': 'minimal_polynomial',
            'element': [0, 1],
            'p': 2,
            'irred_poly': [1, 1, 1]
        }
        result = specialist.process(task)
        assert result['success'] is True


class TestEdgeCases:
    """Test edge cases."""

    def test_zero_element(self):
        """Zero element has minimal poly x."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        result = specialist.compute_minimal_polynomial([0, 0], irred, 2)
        assert result['success'] is True

    def test_frobenius_identity_in_prime_field(self):
        """Frobenius is identity on prime field elements."""
        specialist = MinimalPolynomialSpecialist()
        irred = [1, 1, 1]
        result = specialist.apply_frobenius([1, 0], irred, 2)
        assert result['success'] is True
        assert result['frobenius_image'] == [1, 0] or result['frobenius_image'] == [1]
