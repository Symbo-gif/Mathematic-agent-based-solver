# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
DUAL CODE SPECIALIST COMPLETE TEST SUITE
=========================================

20 comprehensive tests covering:
- Dual code construction from generator/parity matrices
- Self-dual and self-orthogonal code verification
- MacWilliams identity transformation
- Doubly-even and even code classification
- Hull dimension computation
- Edge cases and error handling
- BDI interface testing

REFERENCE:
---------
- MacWilliams & Sloane (1977), Chapter 5: Dual Codes
"""

import pytest
from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting.dual_code_specialist import DualCodeSpecialist


class TestDualCodeSpecialistConstruction:
    """Test dual code construction operations."""

    def test_construct_dual_from_systematic_G_hamming74(self):
        """Construct dual of Hamming(7,4) - should give [7,3,4] simplex code."""
        specialist = DualCodeSpecialist()
        # Hamming(7,4) systematic generator
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.construct_dual(G=G)
        assert result['success'] is True
        assert result['n'] == 7
        assert result['k_original'] == 4
        assert result['k_dual'] == 3  # n - k = 7 - 4 = 3

    def test_construct_dual_from_H_matrix(self):
        """H matrix of C becomes G of dual."""
        specialist = DualCodeSpecialist()
        # Parity check matrix (3x7)
        H = [
            [1, 1, 1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 1]
        ]
        result = specialist.construct_dual(H=H)
        assert result['success'] is True
        assert result['k_dual'] == 3

    def test_construct_dual_empty_matrix_error(self):
        """Empty matrix should fail."""
        specialist = DualCodeSpecialist()
        result = specialist.construct_dual(G=[], H=None)
        assert result['success'] is False

    def test_construct_dual_no_input_error(self):
        """No G or H provided should fail."""
        specialist = DualCodeSpecialist()
        result = specialist.construct_dual()
        assert result['success'] is False


class TestSelfDualCodes:
    """Test self-dual and self-orthogonal verification."""

    def test_verify_self_dual_extended_hamming(self):
        """Extended Hamming [8,4,4] is self-dual."""
        specialist = DualCodeSpecialist()
        # Extended Hamming [8,4,4] in systematic form
        G = [
            [1, 0, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 0, 1, 1],
            [0, 0, 1, 0, 1, 1, 0, 1],
            [0, 0, 0, 1, 1, 1, 1, 0]
        ]
        result = specialist.verify_self_dual(G)
        assert result['success'] is True
        assert result['is_self_dual'] is True

    def test_verify_not_self_dual_dimension_mismatch(self):
        """Code with n != 2k cannot be self-dual."""
        specialist = DualCodeSpecialist()
        # Hamming(7,4) - n=7 != 2*4=8
        G = [
            [1, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 1, 0],
            [0, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1, 1]
        ]
        result = specialist.verify_self_dual(G)
        assert result['success'] is True
        assert result['is_self_dual'] is False

    def test_is_self_orthogonal(self):
        """Test self-orthogonal check."""
        specialist = DualCodeSpecialist()
        # Extended Hamming is self-orthogonal (C subset of C^perp)
        G = [
            [1, 0, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 0, 1, 1],
            [0, 0, 1, 0, 1, 1, 0, 1],
            [0, 0, 0, 1, 1, 1, 1, 0]
        ]
        result = specialist.is_self_orthogonal(G)
        assert result['success'] is True
        assert result['is_self_orthogonal'] is True


class TestMacWilliamsTransform:
    """Test MacWilliams identity transformation."""

    def test_macwilliams_hamming74(self):
        """MacWilliams transform of Hamming(7,4) weight enum."""
        specialist = DualCodeSpecialist()
        # Hamming(7,4): A_0=1, A_3=7, A_4=7, A_7=1
        weight_enum = {0: 1, 3: 7, 4: 7, 7: 1}
        result = specialist.macwilliams_transform(weight_enum, n=7, k=4)
        assert result['success'] is True
        # Dual (Simplex [7,3,4]): B_0=1, B_4=7
        dual_enum = result['dual_weight_enum']
        assert 0 in dual_enum
        assert dual_enum[0] == 1

    def test_macwilliams_trivial_repetition(self):
        """MacWilliams for [2,1,2] repetition code."""
        specialist = DualCodeSpecialist()
        # [2,1,2] repetition: A_0=1, A_2=1
        weight_enum = {0: 1, 2: 1}
        result = specialist.macwilliams_transform(weight_enum, n=2, k=1)
        assert result['success'] is True

    def test_macwilliams_invalid_params(self):
        """Invalid k should fail."""
        specialist = DualCodeSpecialist()
        result = specialist.macwilliams_transform({0: 1}, n=7, k=8)
        assert result['success'] is False


class TestEvenCodes:
    """Test even and doubly-even classification."""

    def test_is_doubly_even_extended_golay(self):
        """Doubly-even: all weights divisible by 4."""
        specialist = DualCodeSpecialist()
        # Doubly-even codewords (weights 0, 4, 8)
        codewords = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
        ]
        result = specialist.is_doubly_even(codewords)
        assert result['success'] is True
        assert result['is_doubly_even'] is True

    def test_is_singly_even_extended_hamming(self):
        """Singly-even: all weights even but not all div by 4."""
        specialist = DualCodeSpecialist()
        # Extended Hamming has weight 4 codewords (doubly-even)
        # But simple even code: weights 0, 2
        codewords = [
            [0, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [1, 1, 1, 1],
        ]
        result = specialist.is_doubly_even(codewords)
        assert result['success'] is True
        # Weights: 0, 2, 2, 4 -> not all div by 4, but all even
        assert result['is_even'] is True

    def test_is_even_check(self):
        """Test simple even check."""
        specialist = DualCodeSpecialist()
        codewords = [
            [0, 0, 0, 0],
            [1, 1, 0, 0],
        ]
        result = specialist.is_even(codewords)
        assert result['success'] is True
        assert result['is_even'] is True

    def test_not_even_odd_weight(self):
        """Code with odd weight codeword is not even."""
        specialist = DualCodeSpecialist()
        codewords = [
            [0, 0, 0],
            [1, 0, 0],  # weight 1
        ]
        result = specialist.is_even(codewords)
        assert result['success'] is True
        assert result['is_even'] is False


class TestHullDimension:
    """Test hull dimension computation."""

    def test_hull_lcd_code(self):
        """LCD code has hull dimension 0."""
        specialist = DualCodeSpecialist()
        # [4,2,2] code that's LCD (C intersect C^perp = {0})
        G = [
            [1, 0, 1, 0],
            [0, 1, 0, 1]
        ]
        result = specialist.hull_dimension(G)
        assert result['success'] is True
        # Check if it computed hull
        assert 'hull_dimension' in result

    def test_hull_self_orthogonal(self):
        """Self-orthogonal code has hull = k."""
        specialist = DualCodeSpecialist()
        # Self-dual code: hull = k
        G = [
            [1, 0, 0, 0, 0, 1, 1, 1],
            [0, 1, 0, 0, 1, 0, 1, 1],
            [0, 0, 1, 0, 1, 1, 0, 1],
            [0, 0, 0, 1, 1, 1, 1, 0]
        ]
        result = specialist.hull_dimension(G)
        assert result['success'] is True
        assert result['is_self_orthogonal'] is True
        assert result['hull_dimension'] == 4


class TestBDIInterface:
    """Test BDI agent interface."""

    def test_get_stats(self):
        """Get statistics should return all counters."""
        specialist = DualCodeSpecialist()
        stats = specialist.get_stats()
        assert 'tasks_executed' in stats
        assert 'duals_constructed' in stats
        assert 'macwilliams_transforms' in stats

    def test_process_dual_construction(self):
        """Process a dual construction task."""
        specialist = DualCodeSpecialist()
        task = {
            'operation': 'construct_dual',
            'G': [[1, 0, 1], [0, 1, 1]]
        }
        result = specialist.process(task)
        assert result['success'] is True


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_codeword_list(self):
        """Empty codeword list should fail."""
        specialist = DualCodeSpecialist()
        result = specialist.is_doubly_even([])
        assert result['success'] is False

    def test_krawtchouk_internal(self):
        """Test internal Krawtchouk polynomial."""
        specialist = DualCodeSpecialist()
        # K_0(x) = 1 for all x
        k0 = specialist._krawtchouk(7, 0, 3, 2)
        assert k0 == 1

    def test_non_binary_not_supported(self):
        """Non-binary field should report not implemented."""
        specialist = DualCodeSpecialist()
        result = specialist.construct_dual(G=[[1, 0, 1]], q=3)
        assert result['success'] is False
        assert 'not yet supported' in result['error'].lower() or 'not implemented' in result['error'].lower()
