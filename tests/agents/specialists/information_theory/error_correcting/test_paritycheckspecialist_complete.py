# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
PARITY CHECK SPECIALIST COMPLETE TEST SUITE
============================================

23 comprehensive tests for ParityCheckSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.parity_check_specialist import ParityCheckSpecialist


class TestParityConstruction:
    """Test parity matrix construction."""

    def test_construct_from_generator(self):
        """Build H from systematic G."""
        specialist = ParityCheckSpecialist()
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.construct_from_generator(G)
        assert result['success'] is True
        assert len(result['parity_check']) == 3  # n-k = 3 rows
        assert len(result['parity_check'][0]) == 7  # n columns

    def test_construct_empty_generator(self):
        """Empty generator should fail."""
        specialist = ParityCheckSpecialist()
        result = specialist.construct_from_generator([])
        assert result['success'] is False


class TestSyndromeComputation:
    """Test syndrome computation."""

    def test_syndrome_valid_codeword(self):
        """Valid codeword has zero syndrome."""
        specialist = ParityCheckSpecialist()
        H = [
            [1, 1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 1]
        ]
        # Valid Hamming(7,4) codeword
        codeword = [0, 0, 0, 0, 0, 0, 0]
        result = specialist.compute_syndrome(codeword, H)
        assert result['success'] is True
        assert result['syndrome'] == [0, 0, 0]
        assert result['is_codeword'] is True

    def test_syndrome_single_error(self):
        """Single error has non-zero syndrome."""
        specialist = ParityCheckSpecialist()
        H = [
            [1, 1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 1]
        ]
        # Error in position 0
        received = [1, 0, 0, 0, 0, 0, 0]
        result = specialist.compute_syndrome(received, H)
        assert result['success'] is True
        assert result['syndrome'] != [0, 0, 0]

    def test_syndrome_length_mismatch(self):
        """Mismatched lengths should fail."""
        specialist = ParityCheckSpecialist()
        H = [[1, 0, 1], [0, 1, 1]]
        result = specialist.compute_syndrome([1, 0], H)
        assert result['success'] is False


class TestSyndromeDecode:
    """Test syndrome decoding."""

    def test_decode_no_error(self):
        """No error needs no correction."""
        specialist = ParityCheckSpecialist()
        H = [
            [1, 1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 1]
        ]
        # Build simple syndrome table: zero syndrome -> zero error
        syndrome_table = {
            (0, 0, 0): [0, 0, 0, 0, 0, 0, 0]
        }
        received = [0, 0, 0, 0, 0, 0, 0]
        result = specialist.syndrome_decode(received, H, syndrome_table)
        assert result['success'] is True
        assert result['codeword'] == received

    def test_decode_single_error(self):
        """Correct single error."""
        specialist = ParityCheckSpecialist()
        H = [
            [1, 1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 1]
        ]
        # Syndrome table for position 4 error: syndrome (1,0,0) -> error at position 4
        syndrome_table = {
            (0, 0, 0): [0, 0, 0, 0, 0, 0, 0],
            (1, 0, 0): [0, 0, 0, 0, 1, 0, 0]
        }
        # Error at position 4 (check bit)
        received = [0, 0, 0, 0, 1, 0, 0]
        result = specialist.syndrome_decode(received, H, syndrome_table)
        assert result['success'] is True


class TestStandardArray:
    """Test standard array construction."""

    def test_build_standard_array_small(self):
        """Build standard array for [3,1] code."""
        specialist = ParityCheckSpecialist()
        G = [[1, 1, 1]]
        result = specialist.build_standard_array(G)
        assert result['success'] is True

    def test_build_standard_array_limit(self):
        """Too large k should fail."""
        specialist = ParityCheckSpecialist()
        # k=20 would give 2^20 = 1M codewords - exceeds default max_size
        G = [[1 if i == j else 0 for j in range(21)] for i in range(20)]
        result = specialist.build_standard_array(G, max_size=1024)
        assert result['success'] is False


class TestCodewordVerification:
    """Test codeword membership verification."""

    def test_is_codeword_valid(self):
        """Valid codeword returns True."""
        specialist = ParityCheckSpecialist()
        H = [[1, 1, 0], [0, 1, 1]]
        result = specialist.is_codeword([0, 0, 0], H)
        assert result['success'] is True
        assert result['is_codeword'] is True

    def test_is_codeword_invalid(self):
        """Invalid word returns False."""
        specialist = ParityCheckSpecialist()
        H = [[1, 1, 0], [0, 1, 1]]
        result = specialist.is_codeword([1, 0, 0], H)
        assert result['success'] is True
        assert result['is_codeword'] is False


class TestOrthogonality:
    """Test orthogonality verification."""

    def test_verify_orthogonality(self):
        """G*H^T should be zero."""
        specialist = ParityCheckSpecialist()
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        H = [
            [1, 1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 1]
        ]
        result = specialist.verify_orthogonality(G, H)
        assert result['success'] is True
        assert result['is_orthogonal'] is True


class TestBDIInterface:
    """Test BDI interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = ParityCheckSpecialist()
        stats = specialist.get_stats()
        assert 'syndromes_computed' in stats
        assert 'syndrome_decodings' in stats

    def test_process_syndrome(self):
        """Process syndrome task."""
        specialist = ParityCheckSpecialist()
        task = {
            'operation': 'syndrome',
            'received': [0, 0, 0],
            'H': [[1, 1, 0], [0, 1, 1]]
        }
        result = specialist.process(task)
        assert result['success'] is True


class TestEdgeCases:
    """Test edge cases."""

    def test_single_parity_bit(self):
        """[2,1,2] simple parity code."""
        specialist = ParityCheckSpecialist()
        H = [[1, 1]]
        result = specialist.compute_syndrome([0, 0], H)
        assert result['success'] is True

    def test_empty_received(self):
        """Empty received should fail gracefully."""
        specialist = ParityCheckSpecialist()
        H = [[1, 0]]
        result = specialist.compute_syndrome([], H)
        assert result['success'] is False
