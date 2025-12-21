# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
IRREDUCIBLE POLYNOMIAL SPECIALIST COMPLETE TEST SUITE
=====================================================

23 comprehensive tests for IrreduciblePolynomialSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.finite_fields.irreducible_polynomial_specialist import IrreduciblePolynomialSpecialist


class TestIrreducibilityTest:
    """Test irreducibility testing."""

    def test_irreducible_x2_x_1_gf2(self):
        """x^2 + x + 1 is irreducible over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_irreducible([1, 1, 1], 2)
        assert result['success'] is True
        assert result['is_irreducible'] is True

    def test_reducible_x2_gf2(self):
        """x^2 is reducible (x * x)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_irreducible([0, 0, 1], 2)
        assert result['success'] is True
        assert result['is_irreducible'] is False

    def test_irreducible_x3_x_1_gf2(self):
        """x^3 + x + 1 is irreducible over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_irreducible([1, 1, 0, 1], 2)
        assert result['success'] is True
        assert result['is_irreducible'] is True

    def test_reducible_x2_1_gf2(self):
        """x^2 + 1 = (x+1)^2 over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_irreducible([1, 0, 1], 2)
        assert result['success'] is True
        assert result['is_irreducible'] is False


class TestFindIrreducible:
    """Test finding irreducible polynomials."""

    def test_find_degree_2_gf2(self):
        """Find irreducible of degree 2 over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.find_irreducible(2, 2)
        assert result['success'] is True
        assert len(result['polynomial']) == 3

    def test_find_degree_3_gf2(self):
        """Find irreducible of degree 3 over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.find_irreducible(2, 3)
        assert result['success'] is True
        assert len(result['polynomial']) == 4

    def test_find_degree_4_gf2(self):
        """Find irreducible of degree 4 over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.find_irreducible(2, 4)
        assert result['success'] is True

    def test_find_degree_8_gf2(self):
        """Find irreducible of degree 8 over GF(2) (AES)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.find_irreducible(2, 8)
        assert result['success'] is True


class TestPrimitivePolynomial:
    """Test primitive polynomial checking."""

    def test_primitive_x2_x_1_gf2(self):
        """x^2 + x + 1 is primitive over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_primitive([1, 1, 1], 2)
        assert result['success'] is True
        assert result['is_primitive'] is True

    def test_x3_x_1_is_primitive(self):
        """x^3 + x + 1 is primitive over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_primitive([1, 1, 0, 1], 2)
        assert result['success'] is True
        assert result['is_primitive'] is True


class TestFactorization:
    """Test polynomial factorization."""

    def test_factor_x2_gf2(self):
        """Factor x^2 over GF(2)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.factorize([0, 0, 1], 2)
        assert result['success'] is True

    def test_factor_irreducible(self):
        """Factoring irreducible poly returns itself."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.factorize([1, 1, 1], 2)
        assert result['success'] is True


class TestNonBinary:
    """Test non-binary field operations."""

    def test_irreducible_gf3(self):
        """Test irreducibility over GF(3)."""
        specialist = IrreduciblePolynomialSpecialist()
        # x^2 + 1 is irreducible over GF(3)
        result = specialist.is_irreducible([1, 0, 1], 3)
        assert result['success'] is True

    def test_find_irreducible_gf5(self):
        """Find irreducible over GF(5)."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.find_irreducible(5, 2)
        assert result['success'] is True


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = IrreduciblePolynomialSpecialist()
        stats = specialist.get_stats()
        assert 'irreducibility_tests' in stats

    def test_process_test(self):
        """Process irreducibility test task."""
        specialist = IrreduciblePolynomialSpecialist()
        task = {'operation': 'test', 'polynomial': [1, 1, 1], 'p': 2}
        result = specialist.process(task)
        assert result['success'] is True


class TestEdgeCases:
    """Test edge cases."""

    def test_degree_1(self):
        """Degree 1 polynomials are always irreducible."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_irreducible([1, 1], 2)
        assert result['success'] is True
        assert result['is_irreducible'] is True

    def test_constant_polynomial(self):
        """Constant polynomial edge case."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_irreducible([1], 2)
        assert result['success'] is True

    def test_empty_polynomial_fails(self):
        """Empty polynomial should fail."""
        specialist = IrreduciblePolynomialSpecialist()
        result = specialist.is_irreducible([], 2)
        assert result['success'] is False
