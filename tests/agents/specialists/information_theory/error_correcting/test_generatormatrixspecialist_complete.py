# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
GENERATOR MATRIX SPECIALIST COMPLETE TEST SUITE
================================================

21 comprehensive tests for GeneratorMatrixSpecialist.
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.generator_matrix_specialist import GeneratorMatrixSpecialist


class TestEncoding:
    """Test encoding operations."""

    def test_encode_hamming74(self):
        """Encode message with Hamming(7,4)."""
        specialist = GeneratorMatrixSpecialist()
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        message = [1, 0, 1, 1]
        result = specialist.encode(message, G)
        assert result['success'] is True
        assert len(result['codeword']) == 7
        # First 4 bits should equal message (systematic)
        assert result['codeword'][:4] == message

    def test_encode_all_zeros(self):
        """Zero message encodes to zero codeword."""
        specialist = GeneratorMatrixSpecialist()
        G = [[1, 0, 1], [0, 1, 1]]
        result = specialist.encode([0, 0], G)
        assert result['success'] is True
        assert result['codeword'] == [0, 0, 0]

    def test_encode_length_mismatch(self):
        """Message length != k should fail."""
        specialist = GeneratorMatrixSpecialist()
        G = [[1, 0, 1], [0, 1, 1]]
        result = specialist.encode([1, 0, 1], G)  # 3 != 2
        assert result['success'] is False

    def test_encode_empty_matrix(self):
        """Empty generator should fail."""
        specialist = GeneratorMatrixSpecialist()
        result = specialist.encode([1], [])
        assert result['success'] is False


class TestSystematicEncoding:
    """Test systematic encoding."""

    def test_systematic_encode(self):
        """Systematic encode c = (m | m*P)."""
        specialist = GeneratorMatrixSpecialist()
        P = [[1, 1, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]]  # 4x3 parity
        message = [1, 0, 1, 0]
        result = specialist.systematic_encode(message, P)
        assert result['success'] is True
        # First k=4 bits are message
        assert result['codeword'][:4] == message
        assert result['is_systematic'] is True

    def test_systematic_encode_empty_parity(self):
        """Empty parity matrix should fail."""
        specialist = GeneratorMatrixSpecialist()
        result = specialist.systematic_encode([1, 0], [])
        assert result['success'] is False


class TestCodewordGeneration:
    """Test codeword generation."""

    def test_generate_all_codewords_small(self):
        """Generate all codewords for [3,2] code."""
        specialist = GeneratorMatrixSpecialist()
        G = [[1, 0, 1], [0, 1, 1]]
        result = specialist.generate_all_codewords(G)
        assert result['success'] is True
        assert result['count'] == 4  # 2^2 = 4

    def test_generate_all_codewords_hamming(self):
        """Generate all 16 Hamming(7,4) codewords."""
        specialist = GeneratorMatrixSpecialist()
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.generate_all_codewords(G)
        assert result['success'] is True
        assert result['count'] == 16


class TestHammingConstruction:
    """Test Hamming code construction."""

    def test_construct_hamming_r2(self):
        """Hamming(3,1) for r=2."""
        specialist = GeneratorMatrixSpecialist()
        result = specialist.construct_hamming_generator(2)
        assert result['success'] is True
        assert result['n'] == 3
        assert result['k'] == 1

    def test_construct_hamming_r3(self):
        """Hamming(7,4) for r=3."""
        specialist = GeneratorMatrixSpecialist()
        result = specialist.construct_hamming_generator(3)
        assert result['success'] is True
        assert result['n'] == 7
        assert result['k'] == 4
        assert result['d'] == 3

    def test_construct_hamming_r_too_small(self):
        """r < 2 should fail."""
        specialist = GeneratorMatrixSpecialist()
        result = specialist.construct_hamming_generator(1)
        assert result['success'] is False


class TestParityExtraction:
    """Test parity matrix extraction."""

    def test_extract_parity(self):
        """Extract P from [I_k | P]."""
        specialist = GeneratorMatrixSpecialist()
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.extract_parity_matrix(G)
        assert result['success'] is True
        assert result['k'] == 4
        assert result['redundancy'] == 3

    def test_extract_parity_non_systematic(self):
        """Non-systematic should fail."""
        specialist = GeneratorMatrixSpecialist()
        G = [[1, 1, 1], [0, 1, 0]]
        result = specialist.extract_parity_matrix(G)
        assert result['success'] is False


class TestBDIInterface:
    """Test BDI interface."""

    def test_get_stats(self):
        """Get statistics."""
        specialist = GeneratorMatrixSpecialist()
        stats = specialist.get_stats()
        assert 'encodings_performed' in stats
        assert 'generators_constructed' in stats

    def test_process_encode(self):
        """Process encode task."""
        specialist = GeneratorMatrixSpecialist()
        task = {
            'operation': 'encode',
            'message': [1, 0],
            'G': [[1, 0, 1], [0, 1, 1]]
        }
        result = specialist.process(task)
        assert result['success'] is True
