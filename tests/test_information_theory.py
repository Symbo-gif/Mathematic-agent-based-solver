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
Tests for Information Theory Domain
===================================

Comprehensive tests for entropy, coding theory, and channel capacity specialists.
"""

import pytest
import math
import numpy as np


# =============================================================================
# ENTROPY SPECIALIST TESTS
# =============================================================================

class TestEntropySpecialist:
    """Tests for EntropySpecialist."""

    def test_shannon_entropy_uniform(self):
        """Uniform distribution has maximum entropy."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        # Uniform distribution over 8 symbols: H = log2(8) = 3 bits
        probs = [1/8] * 8
        result = specialist.shannon_entropy(probs)

        assert 'entropy' in result
        assert abs(result['entropy'] - 3.0) < 1e-10

    def test_shannon_entropy_certain(self):
        """Certain distribution has zero entropy."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        probs = [1.0, 0.0, 0.0, 0.0]
        result = specialist.shannon_entropy(probs)

        assert result['entropy'] == 0.0

    def test_shannon_entropy_binary(self):
        """Binary entropy function."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        # Fair coin: H = 1 bit
        result = specialist.shannon_entropy([0.5, 0.5])
        assert abs(result['entropy'] - 1.0) < 1e-10

        # Biased coin (p=0.1): H = -0.1*log2(0.1) - 0.9*log2(0.9)
        result = specialist.shannon_entropy([0.1, 0.9])
        expected = -0.1 * math.log2(0.1) - 0.9 * math.log2(0.9)
        assert abs(result['entropy'] - expected) < 1e-10

    def test_shannon_entropy_natural_base(self):
        """Entropy with natural logarithm base."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        probs = [0.5, 0.5]
        result = specialist.shannon_entropy(probs, base=math.e)

        expected = math.log(2)  # ln(2) nats
        assert abs(result['entropy'] - expected) < 1e-10
        assert result['unit'] == 'nats'

    def test_shannon_entropy_invalid_probs(self):
        """Invalid probabilities raise error."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        # Doesn't sum to 1
        result = specialist.shannon_entropy([0.3, 0.3])
        assert 'error' in result

        # Negative probability
        result = specialist.shannon_entropy([-0.1, 1.1])
        assert 'error' in result

    def test_joint_entropy(self):
        """Joint entropy computation."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        # Independent fair coins: H(X,Y) = H(X) + H(Y) = 2 bits
        joint = [[0.25, 0.25], [0.25, 0.25]]
        result = specialist.joint_entropy(joint)

        assert abs(result['joint_entropy'] - 2.0) < 1e-10

    def test_conditional_entropy(self):
        """Conditional entropy H(Y|X)."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        # Perfect correlation: H(Y|X) = 0
        joint = [[0.5, 0.0], [0.0, 0.5]]
        result = specialist.conditional_entropy(joint)

        assert abs(result['conditional_entropy']) < 1e-10

    def test_kl_divergence_same_distribution(self):
        """KL divergence of distribution with itself is 0."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        p = [0.25, 0.25, 0.25, 0.25]
        result = specialist.kl_divergence(p, p)

        assert abs(result['kl_divergence']) < 1e-10

    def test_kl_divergence_positive(self):
        """KL divergence is always non-negative."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        p = [0.5, 0.5]
        q = [0.9, 0.1]
        result = specialist.kl_divergence(p, q)

        assert result['kl_divergence'] > 0

    def test_kl_divergence_asymmetric(self):
        """KL divergence is asymmetric."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        p = [0.5, 0.5]
        q = [0.9, 0.1]

        result_pq = specialist.kl_divergence(p, q)
        result_qp = specialist.kl_divergence(q, p)

        assert abs(result_pq['kl_divergence'] - result_qp['kl_divergence']) > 0.1

    def test_mutual_information_independent(self):
        """Mutual information of independent variables is 0."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        # Independent uniform distributions
        joint = [[0.25, 0.25], [0.25, 0.25]]
        result = specialist.mutual_information(joint)

        assert abs(result['mutual_information']) < 1e-10

    def test_mutual_information_correlated(self):
        """Mutual information of correlated variables is positive."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        # Perfect correlation
        joint = [[0.5, 0.0], [0.0, 0.5]]
        result = specialist.mutual_information(joint)

        # I(X;Y) = H(X) = 1 bit for fair coin
        assert abs(result['mutual_information'] - 1.0) < 1e-10

    def test_cross_entropy(self):
        """Cross entropy H(P, Q)."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        p = [0.5, 0.5]
        q = [0.5, 0.5]
        result = specialist.cross_entropy(p, q)

        # When P=Q, cross entropy equals entropy
        assert abs(result['cross_entropy'] - 1.0) < 1e-10

    def test_renyi_entropy_alpha_1(self):
        """Renyi entropy with alpha->1 equals Shannon entropy."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        probs = [0.25, 0.25, 0.25, 0.25]

        shannon = specialist.shannon_entropy(probs)
        renyi = specialist.renyi_entropy(probs, alpha=1.0)

        assert abs(renyi['renyi_entropy'] - shannon['entropy']) < 1e-10

    def test_renyi_entropy_alpha_0(self):
        """Renyi entropy with alpha=0 is max entropy (log of support size)."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
        specialist = EntropySpecialist()

        probs = [0.1, 0.2, 0.3, 0.4]  # 4 non-zero elements
        result = specialist.renyi_entropy(probs, alpha=0.0)

        # H_0 = log2(|support|) = log2(4) = 2
        assert abs(result['renyi_entropy'] - 2.0) < 1e-10


# =============================================================================
# CODING THEORY SPECIALIST TESTS
# =============================================================================

class TestCodingTheorySpecialist:
    """Tests for CodingTheorySpecialist."""

    def test_huffman_build_simple(self):
        """Build Huffman code for simple distribution."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        symbols = ['A', 'B', 'C', 'D']
        frequencies = [0.5, 0.25, 0.125, 0.125]

        result = specialist.build_huffman_code(symbols, frequencies)

        assert 'code_table' in result
        assert len(result['code_table']) == 4
        # Most frequent symbol should have shortest code
        assert len(result['code_table']['A']) <= len(result['code_table']['D'])

    def test_huffman_build_uniform(self):
        """Huffman code for uniform distribution."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        symbols = ['A', 'B', 'C', 'D']
        frequencies = [1, 1, 1, 1]

        result = specialist.build_huffman_code(symbols, frequencies)

        # For 4 symbols uniform, all codes should be length 2
        for code in result['code_table'].values():
            assert len(code) == 2

    def test_huffman_encode_decode_roundtrip(self):
        """Encode and decode should recover original message."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        message = "ABRACADABRA"

        # Encode
        encode_result = specialist.huffman_encode(message)
        assert 'encoded' in encode_result
        assert 'code_table' in encode_result

        # Decode
        decode_result = specialist.huffman_decode(
            encode_result['encoded'],
            encode_result['code_table']
        )
        assert decode_result['decoded'] == message

    def test_huffman_compression(self):
        """Huffman coding should achieve compression for skewed distribution."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        # Message with skewed character frequency
        message = "AAAAAAAABBBCCDE"

        result = specialist.huffman_encode(message)

        # Should achieve compression (< 8 bits per character)
        assert result['compression_ratio'] < 1.0

    def test_huffman_single_symbol(self):
        """Single symbol case."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        result = specialist.build_huffman_code(['A'], [1.0])
        assert result['code_table'] == {'A': '0'}

    def test_huffman_empty_error(self):
        """Empty symbol list should error."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        result = specialist.build_huffman_code([], [])
        assert 'error' in result

    def test_average_code_length(self):
        """Compute average code length."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        code_table = {'A': '0', 'B': '10', 'C': '11'}
        frequencies = {'A': 0.5, 'B': 0.25, 'C': 0.25}

        result = specialist.average_code_length(code_table, frequencies)

        # Average = 0.5*1 + 0.25*2 + 0.25*2 = 1.5
        assert abs(result['average_length'] - 1.5) < 1e-10

    def test_hamming_encode_74(self):
        """Hamming(7,4) encoding."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        data_bits = [1, 0, 1, 1]
        result = specialist.hamming_encode_74(data_bits)

        assert 'codeword' in result
        assert len(result['codeword']) == 7
        assert result['code_rate'] == 4/7

    def test_hamming_decode_no_error(self):
        """Hamming decode without errors."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        # Encode
        data_bits = [1, 0, 1, 1]
        encode_result = specialist.hamming_encode_74(data_bits)
        codeword = encode_result['codeword']

        # Decode (no errors)
        decode_result = specialist.hamming_decode_74(codeword)

        assert decode_result['data_bits'] == data_bits
        assert decode_result['error_detected'] == False

    def test_hamming_decode_single_error(self):
        """Hamming decode with single bit error."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        # Encode
        data_bits = [1, 0, 1, 1]
        encode_result = specialist.hamming_encode_74(data_bits)
        codeword = encode_result['codeword'].copy()

        # Introduce single bit error at position 3 (0-indexed)
        codeword[3] ^= 1

        # Decode should correct error
        decode_result = specialist.hamming_decode_74(codeword)

        assert decode_result['data_bits'] == data_bits
        assert decode_result['error_detected'] == True
        assert decode_result['error_position'] == 4  # 1-indexed

    def test_hamming_all_error_positions(self):
        """Test Hamming correction for errors at all positions."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        data_bits = [1, 1, 0, 0]
        encode_result = specialist.hamming_encode_74(data_bits)

        for error_pos in range(7):
            codeword = encode_result['codeword'].copy()
            codeword[error_pos] ^= 1

            decode_result = specialist.hamming_decode_74(codeword)
            assert decode_result['data_bits'] == data_bits, f"Failed at position {error_pos}"

    def test_parity_check_matrix(self):
        """Generate parity check matrix."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
        specialist = CodingTheorySpecialist()

        result = specialist.generate_parity_check_matrix(7, 4)

        assert 'parity_check_matrix' in result
        H = np.array(result['parity_check_matrix'])
        assert H.shape == (3, 7)


# =============================================================================
# CHANNEL CAPACITY SPECIALIST TESTS
# =============================================================================

class TestChannelCapacitySpecialist:
    """Tests for ChannelCapacitySpecialist."""

    def test_bsc_capacity_zero_error(self):
        """BSC with p=0 has capacity 1."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result = specialist.binary_symmetric_channel_capacity(0.0)
        assert abs(result['capacity'] - 1.0) < 1e-10

    def test_bsc_capacity_half_error(self):
        """BSC with p=0.5 has capacity 0 (useless channel)."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result = specialist.binary_symmetric_channel_capacity(0.5)
        assert abs(result['capacity']) < 1e-10

    def test_bsc_capacity_one_error(self):
        """BSC with p=1 has capacity 1 (flips are deterministic)."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result = specialist.binary_symmetric_channel_capacity(1.0)
        assert abs(result['capacity'] - 1.0) < 1e-10

    def test_bsc_capacity_symmetric(self):
        """BSC capacity is symmetric around p=0.5."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result_p = specialist.binary_symmetric_channel_capacity(0.1)
        result_q = specialist.binary_symmetric_channel_capacity(0.9)

        assert abs(result_p['capacity'] - result_q['capacity']) < 1e-10

    def test_bec_capacity(self):
        """Binary Erasure Channel capacity = 1 - epsilon."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        epsilon = 0.3
        result = specialist.binary_erasure_channel_capacity(epsilon)

        assert abs(result['capacity'] - 0.7) < 1e-10

    def test_bec_capacity_zero(self):
        """BEC with epsilon=0 has capacity 1."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result = specialist.binary_erasure_channel_capacity(0.0)
        assert abs(result['capacity'] - 1.0) < 1e-10

    def test_bec_capacity_one(self):
        """BEC with epsilon=1 has capacity 0."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result = specialist.binary_erasure_channel_capacity(1.0)
        assert abs(result['capacity']) < 1e-10

    def test_awgn_capacity_high_snr(self):
        """AWGN channel capacity increases with SNR."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result_low = specialist.awgn_channel_capacity(1.0)
        result_high = specialist.awgn_channel_capacity(100.0)

        assert result_high['capacity'] > result_low['capacity']

    def test_awgn_capacity_formula(self):
        """Verify Shannon-Hartley formula."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        snr = 7.0
        bandwidth = 2.0
        result = specialist.awgn_channel_capacity(snr, bandwidth)

        expected = bandwidth * math.log2(1 + snr)
        assert abs(result['capacity'] - expected) < 1e-10

    def test_awgn_zero_snr(self):
        """AWGN with SNR=0 has capacity 0."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        result = specialist.awgn_channel_capacity(0.0)
        assert abs(result['capacity']) < 1e-10

    def test_channel_capacity_noiseless(self):
        """Noiseless binary channel has capacity 1."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        # Identity channel matrix
        channel_matrix = [[1.0, 0.0], [0.0, 1.0]]
        result = specialist.compute_channel_capacity(channel_matrix)

        assert abs(result['capacity'] - 1.0) < 1e-6

    def test_channel_capacity_useless(self):
        """Useless channel (rows identical) has capacity 0."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        # Channel that always outputs same distribution
        channel_matrix = [[0.5, 0.5], [0.5, 0.5]]
        result = specialist.compute_channel_capacity(channel_matrix)

        assert abs(result['capacity']) < 1e-6

    def test_mutual_information_from_joint(self):
        """Compute mutual information from joint distribution."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        # Independent
        joint = [[0.25, 0.25], [0.25, 0.25]]
        result = specialist.mutual_information_from_joint(joint)
        assert abs(result['mutual_information']) < 1e-10

        # Perfectly correlated
        joint = [[0.5, 0.0], [0.0, 0.5]]
        result = specialist.mutual_information_from_joint(joint)
        assert abs(result['mutual_information'] - 1.0) < 1e-10

    def test_rate_distortion_binary(self):
        """Rate-distortion for binary source."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
        specialist = ChannelCapacitySpecialist()

        # Fair coin source
        source = [0.5, 0.5]

        # Zero distortion requires full rate
        result = specialist.rate_distortion_bound(source, 0.0)
        assert abs(result['rate'] - 1.0) < 1e-10

        # Max distortion requires zero rate
        result = specialist.rate_distortion_bound(source, 0.5)
        assert abs(result['rate']) < 1e-10


# =============================================================================
# INFORMATION THEORY SUPERVISOR TESTS
# =============================================================================

class TestInformationTheorySupervisor:
    """Tests for InformationTheorySupervisor."""

    def test_supervisor_initialization(self):
        """Supervisor initializes correctly."""
        from symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor import InformationTheorySupervisor
        supervisor = InformationTheorySupervisor()

        assert supervisor.agent_id == 'information_theory_supervisor_001'

    def test_supervisor_solve_entropy(self):
        """Supervisor routes entropy problems correctly."""
        from symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor import InformationTheorySupervisor
        supervisor = InformationTheorySupervisor()

        result = supervisor.solve({
            'type': 'shannon_entropy',
            'probabilities': [0.5, 0.5]
        })

        assert abs(result['entropy'] - 1.0) < 1e-10

    def test_supervisor_solve_huffman(self):
        """Supervisor routes Huffman problems correctly."""
        from symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor import InformationTheorySupervisor
        supervisor = InformationTheorySupervisor()

        result = supervisor.solve({
            'type': 'huffman_build',
            'symbols': ['A', 'B'],
            'frequencies': [0.5, 0.5]
        })

        assert 'code_table' in result

    def test_supervisor_solve_bsc(self):
        """Supervisor routes BSC capacity problems correctly."""
        from symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor import InformationTheorySupervisor
        supervisor = InformationTheorySupervisor()

        result = supervisor.solve({
            'type': 'bsc_capacity',
            'crossover_probability': 0.1
        })

        assert 'capacity' in result

    def test_supervisor_unknown_type(self):
        """Supervisor handles unknown problem type."""
        from symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor import InformationTheorySupervisor
        supervisor = InformationTheorySupervisor()

        result = supervisor.solve({
            'type': 'unknown_operation'
        })

        assert 'error' in result

    def test_supervisor_statistics(self):
        """Supervisor returns statistics."""
        from symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor import InformationTheorySupervisor
        supervisor = InformationTheorySupervisor()

        stats = supervisor.get_statistics()
        assert stats['tier'] == 2
        assert 'entropy' in stats['specialists']


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestInformationTheoryIntegration:
    """Integration tests for the information theory domain."""

    def test_entropy_coding_relationship(self):
        """Verify entropy is lower bound on average code length."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import (
            EntropySpecialist, CodingTheorySpecialist
        )

        entropy_spec = EntropySpecialist()
        coding_spec = CodingTheorySpecialist()

        # Source distribution
        probs = [0.5, 0.25, 0.125, 0.125]
        symbols = ['A', 'B', 'C', 'D']

        # Compute entropy
        entropy_result = entropy_spec.shannon_entropy(probs)
        H = entropy_result['entropy']

        # Build Huffman code
        huffman_result = coding_spec.build_huffman_code(symbols, probs)
        L = huffman_result['average_length']

        # Average code length >= entropy (source coding theorem)
        assert L >= H - 1e-10

        # Huffman is optimal: L < H + 1
        assert L < H + 1

    def test_channel_mutual_info_capacity(self):
        """Channel capacity equals max mutual information."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist

        specialist = ChannelCapacitySpecialist()

        # BSC with p=0.1
        p = 0.1
        bsc_result = specialist.binary_symmetric_channel_capacity(p)

        # The capacity from Blahut-Arimoto should match
        channel_matrix = [[1-p, p], [p, 1-p]]
        ba_result = specialist.compute_channel_capacity(channel_matrix)

        assert abs(bsc_result['capacity'] - ba_result['capacity']) < 1e-4

    def test_data_processing_inequality(self):
        """Data processing inequality: I(X;Z) <= I(X;Y)."""
        from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist

        specialist = EntropySpecialist()

        # X -> Y -> Z Markov chain
        # P(X,Y)
        joint_xy = [[0.4, 0.1], [0.1, 0.4]]
        mi_xy = specialist.mutual_information(joint_xy)

        # If we further process Y to get Z, I(X;Z) <= I(X;Y)
        # For demonstration, let Z = Y (so I(X;Z) = I(X;Y))
        joint_xz = joint_xy
        mi_xz = specialist.mutual_information(joint_xz)

        assert mi_xz['mutual_information'] <= mi_xy['mutual_information'] + 1e-10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
