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
CHANNEL CAPACITY SPECIALIST (Tier 3)
====================================

Native Python implementation for channel capacity computations.
Handles binary symmetric channels, erasure channels, AWGN capacity.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class ChannelCapacitySpecialist(BDIAgent):
    """
    Specialist for channel capacity computations.

    Capabilities:
    - Binary symmetric channel (BSC) capacity
    - Binary erasure channel (BEC) capacity
    - AWGN channel capacity (Shannon-Hartley)
    - Mutual information maximization
    - Channel matrix analysis
    - Rate-distortion bounds
    """

    def __init__(self, agent_id: str = 'channel_capacity_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.information_theory.channel',
                agent_id=agent_id,
                algorithm='native_channel_capacity',
                cost='low',
                instance=self,
                tier='3',
                capabilities='bsc_bec_awgn_mutual_info'
            ))

        logger.info(f"[{agent_id}] Channel Capacity Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for channel capacity tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['channel'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['capacity'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['mutual_info'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create channel capacity computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'bsc_capacity')

            steps = ['claim_task', 'compute_capacity', 'post_result']
            intention = Intention(
                plan_id=f'channel_{operation}_{task_id}',
                steps=steps,
                target_desire='channel_capacity_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute channel capacity operations."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'compute_capacity':
            self._compute_capacity(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_capacity(self, intention: Intention):
        """Compute the requested channel capacity operation."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'bsc_capacity')

        try:
            if operation == 'bsc_capacity':
                p = metadata.get('crossover_probability', 0.1)
                result = self.binary_symmetric_channel_capacity(p)
            elif operation == 'bec_capacity':
                epsilon = metadata.get('erasure_probability', 0.1)
                result = self.binary_erasure_channel_capacity(epsilon)
            elif operation == 'awgn_capacity':
                snr = metadata.get('snr', 10.0)
                bandwidth = metadata.get('bandwidth', 1.0)
                result = self.awgn_channel_capacity(snr, bandwidth)
            elif operation == 'channel_capacity':
                channel_matrix = metadata.get('channel_matrix', [])
                result = self.compute_channel_capacity(channel_matrix)
            elif operation == 'mutual_information':
                joint_probs = metadata.get('joint_probabilities', [])
                result = self.mutual_information_from_joint(joint_probs)
            elif operation == 'rate_distortion':
                source_dist = metadata.get('source_distribution', [])
                distortion = metadata.get('distortion', 0.1)
                result = self.rate_distortion_bound(source_dist, distortion)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Channel computation failed: {e}")
            intention.metadata['result'] = {'error': str(e)}
            intention.advance()

    def _post_result(self, intention: Intention):
        """Post result to blackboard."""
        if self.blackboard:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            task = intention.metadata.get('task_entry')
            result = intention.metadata.get('result', {})

            result_entry = create_entry(
                content=result,
                entry_type=EntryType.RESULT,
                tags=['channel', 'capacity', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # BINARY SYMMETRIC CHANNEL
    # =========================================================================

    @staticmethod
    def binary_symmetric_channel_capacity(p: float) -> Dict[str, Any]:
        """
        Compute capacity of Binary Symmetric Channel (BSC).

        C = 1 - H(p) where H(p) is binary entropy function.

        Args:
            p: Crossover probability (probability of bit flip)

        Returns:
            Dictionary with capacity and related metrics
        """
        if not 0 <= p <= 1:
            return {'error': 'Crossover probability must be in [0, 1]'}

        # Binary entropy function H(p) = -p*log2(p) - (1-p)*log2(1-p)
        if p == 0 or p == 1:
            binary_entropy = 0.0
        else:
            binary_entropy = -p * math.log2(p) - (1 - p) * math.log2(1 - p)

        capacity = 1.0 - binary_entropy

        return {
            'capacity': capacity,
            'binary_entropy': binary_entropy,
            'crossover_probability': p,
            'unit': 'bits per channel use',
            'method': 'native_bsc_capacity'
        }

    # =========================================================================
    # BINARY ERASURE CHANNEL
    # =========================================================================

    @staticmethod
    def binary_erasure_channel_capacity(epsilon: float) -> Dict[str, Any]:
        """
        Compute capacity of Binary Erasure Channel (BEC).

        C = 1 - epsilon (simple formula!)

        Args:
            epsilon: Erasure probability

        Returns:
            Dictionary with capacity
        """
        if not 0 <= epsilon <= 1:
            return {'error': 'Erasure probability must be in [0, 1]'}

        capacity = 1.0 - epsilon

        return {
            'capacity': capacity,
            'erasure_probability': epsilon,
            'unit': 'bits per channel use',
            'method': 'native_bec_capacity'
        }

    # =========================================================================
    # AWGN CHANNEL (SHANNON-HARTLEY)
    # =========================================================================

    @staticmethod
    def awgn_channel_capacity(snr: float, bandwidth: float = 1.0) -> Dict[str, Any]:
        """
        Compute capacity of Additive White Gaussian Noise channel.

        Shannon-Hartley theorem: C = B * log2(1 + SNR)

        Args:
            snr: Signal-to-noise ratio (linear, not dB)
            bandwidth: Channel bandwidth in Hz

        Returns:
            Dictionary with capacity in bits/second
        """
        if snr < 0:
            return {'error': 'SNR must be non-negative'}
        if bandwidth <= 0:
            return {'error': 'Bandwidth must be positive'}

        # Shannon-Hartley theorem
        capacity = bandwidth * math.log2(1 + snr)

        # Also compute SNR in dB for reference
        snr_db = 10 * math.log10(snr) if snr > 0 else float('-inf')

        return {
            'capacity': capacity,
            'snr_linear': snr,
            'snr_db': snr_db,
            'bandwidth': bandwidth,
            'unit': 'bits per second' if bandwidth != 1.0 else 'bits per channel use',
            'method': 'native_shannon_hartley'
        }

    # =========================================================================
    # GENERAL DISCRETE MEMORYLESS CHANNEL
    # =========================================================================

    @staticmethod
    def compute_channel_capacity(channel_matrix: List[List[float]],
                                  max_iterations: int = 100,
                                  tolerance: float = 1e-10) -> Dict[str, Any]:
        """
        Compute capacity of discrete memoryless channel using Blahut-Arimoto algorithm.

        Args:
            channel_matrix: P(Y|X) - rows are inputs, columns are outputs
            max_iterations: Maximum iterations for convergence
            tolerance: Convergence tolerance

        Returns:
            Dictionary with capacity and optimal input distribution
        """
        P = np.array(channel_matrix, dtype=float)

        if P.ndim != 2:
            return {'error': 'Channel matrix must be 2D'}

        n_inputs, n_outputs = P.shape

        # Verify it's a valid channel matrix (rows sum to 1)
        row_sums = P.sum(axis=1)
        if not np.allclose(row_sums, 1.0, atol=1e-6):
            return {'error': 'Channel matrix rows must sum to 1'}

        if np.any(P < 0):
            return {'error': 'Channel matrix must have non-negative entries'}

        # Initialize uniform input distribution
        q = np.ones(n_inputs) / n_inputs

        # Blahut-Arimoto algorithm
        capacity_history = []

        for iteration in range(max_iterations):
            # Compute output distribution: P(Y) = sum_x q(x) * P(Y|X=x)
            r = q @ P  # shape: (n_outputs,)
            r = np.maximum(r, 1e-300)  # avoid log(0)

            # Compute conditional distribution P(X|Y)
            # Using Bayes: P(X=x|Y=y) = q(x) * P(Y=y|X=x) / P(Y=y)

            # Compute mutual information terms for each input
            mutual_info_per_input = np.zeros(n_inputs)
            for x in range(n_inputs):
                for y in range(n_outputs):
                    if P[x, y] > 0:
                        mutual_info_per_input[x] += P[x, y] * math.log2(P[x, y] / r[y])

            # Compute current capacity estimate
            capacity = np.sum(q * mutual_info_per_input)
            capacity_history.append(capacity)

            # Update input distribution (Blahut-Arimoto update)
            c = np.exp2(mutual_info_per_input)
            q_new = q * c
            q_new = q_new / np.sum(q_new)

            # Check convergence
            if iteration > 0 and abs(capacity_history[-1] - capacity_history[-2]) < tolerance:
                break

            q = q_new

        return {
            'capacity': capacity,
            'optimal_input_distribution': q.tolist(),
            'iterations': iteration + 1,
            'converged': iteration < max_iterations - 1,
            'unit': 'bits per channel use',
            'method': 'native_blahut_arimoto'
        }

    # =========================================================================
    # MUTUAL INFORMATION FROM JOINT DISTRIBUTION
    # =========================================================================

    @staticmethod
    def mutual_information_from_joint(joint_probs: List[List[float]]) -> Dict[str, Any]:
        """
        Compute mutual information I(X;Y) from joint probability matrix P(X,Y).

        I(X;Y) = sum_{x,y} P(x,y) * log2(P(x,y) / (P(x) * P(y)))

        Args:
            joint_probs: Joint probability matrix P(X,Y)

        Returns:
            Dictionary with mutual information
        """
        P_xy = np.array(joint_probs, dtype=float)

        if P_xy.ndim != 2:
            return {'error': 'Joint probability must be 2D matrix'}

        if not np.isclose(P_xy.sum(), 1.0, atol=1e-6):
            return {'error': 'Joint probabilities must sum to 1'}

        if np.any(P_xy < 0):
            return {'error': 'Probabilities must be non-negative'}

        # Marginal distributions
        P_x = P_xy.sum(axis=1)  # sum over Y
        P_y = P_xy.sum(axis=0)  # sum over X

        # Compute mutual information
        mutual_info = 0.0
        for i in range(P_xy.shape[0]):
            for j in range(P_xy.shape[1]):
                if P_xy[i, j] > 0 and P_x[i] > 0 and P_y[j] > 0:
                    mutual_info += P_xy[i, j] * math.log2(P_xy[i, j] / (P_x[i] * P_y[j]))

        # Also compute entropies
        H_x = -np.sum(P_x[P_x > 0] * np.log2(P_x[P_x > 0]))
        H_y = -np.sum(P_y[P_y > 0] * np.log2(P_y[P_y > 0]))

        # Joint entropy
        P_flat = P_xy.flatten()
        H_xy = -np.sum(P_flat[P_flat > 0] * np.log2(P_flat[P_flat > 0]))

        return {
            'mutual_information': mutual_info,
            'entropy_x': H_x,
            'entropy_y': H_y,
            'joint_entropy': H_xy,
            'conditional_entropy_y_given_x': H_xy - H_x,
            'conditional_entropy_x_given_y': H_xy - H_y,
            'unit': 'bits',
            'method': 'native_mutual_information'
        }

    # =========================================================================
    # RATE-DISTORTION
    # =========================================================================

    @staticmethod
    def rate_distortion_bound(source_distribution: List[float],
                               distortion: float,
                               distortion_type: str = 'hamming') -> Dict[str, Any]:
        """
        Compute rate-distortion bound for a source.

        For binary source with Hamming distortion:
        R(D) = H(p) - H(D) for D <= min(p, 1-p)

        Args:
            source_distribution: Source probability distribution
            distortion: Target distortion level D
            distortion_type: Type of distortion measure

        Returns:
            Dictionary with rate-distortion bound
        """
        probs = np.array(source_distribution, dtype=float)

        if not np.isclose(probs.sum(), 1.0, atol=1e-6):
            return {'error': 'Source distribution must sum to 1'}

        if np.any(probs < 0):
            return {'error': 'Probabilities must be non-negative'}

        if not 0 <= distortion <= 1:
            return {'error': 'Distortion must be in [0, 1]'}

        # Source entropy
        H_source = -np.sum(probs[probs > 0] * np.log2(probs[probs > 0]))

        if distortion_type == 'hamming' and len(probs) == 2:
            # Binary source with Hamming distortion
            p = probs[1]  # Probability of 1

            D_max = min(p, 1 - p)

            if distortion >= D_max:
                rate = 0.0
            elif distortion == 0:
                rate = H_source
            else:
                # R(D) = H(p) - H(D)
                H_D = -distortion * math.log2(distortion) - (1 - distortion) * math.log2(1 - distortion)
                rate = H_source - H_D
                rate = max(0, rate)

            return {
                'rate': rate,
                'distortion': distortion,
                'source_entropy': H_source,
                'max_distortion': D_max,
                'distortion_type': distortion_type,
                'method': 'native_binary_rate_distortion'
            }
        else:
            # General case - use lower bound
            # R(D) >= H(X) - log2(|X|*D + 1) (rough bound)
            alphabet_size = len(probs)
            lower_bound = max(0, H_source - math.log2(alphabet_size * distortion + 1))

            return {
                'rate_lower_bound': lower_bound,
                'distortion': distortion,
                'source_entropy': H_source,
                'alphabet_size': alphabet_size,
                'distortion_type': distortion_type,
                'note': 'General case uses approximate bound',
                'method': 'native_rate_distortion_bound'
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'bsc_capacity', 'bec_capacity', 'awgn_capacity',
                'channel_capacity', 'mutual_information', 'rate_distortion'
            ]
        }
