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
INFORMATION THEORY SUPERVISOR (Tier 2)
======================================

Routes information-theoretic problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import re
from typing import Dict, Any, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class InformationTheorySupervisor(BDIAgent):
    """
    Supervisor for information theory domain.

    Routes to:
    - EntropySpecialist: Shannon entropy, KL divergence, mutual information
    - CodingTheorySpecialist: Huffman codes, Hamming codes
    - ChannelCapacitySpecialist: BSC, BEC, AWGN capacity

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing decisions
    ENTROPY_KEYWORDS = [
        'entropy', 'shannon', 'kl divergence', 'kullback', 'leibler',
        'cross entropy', 'joint entropy', 'conditional entropy', 'renyi'
    ]

    CODING_KEYWORDS = [
        'huffman', 'hamming', 'error correct', 'parity', 'syndrome',
        'code table', 'encode', 'decode', 'codeword', 'reed solomon'
    ]

    CHANNEL_KEYWORDS = [
        'channel', 'capacity', 'bsc', 'bec', 'awgn', 'snr',
        'binary symmetric', 'erasure', 'gaussian', 'rate distortion'
    ]

    # Error correcting code keywords for the 6 new specialists
    ERROR_CORRECTING_KEYWORDS = [
        'linear code', 'generator matrix', 'parity check', 'parity-check',
        'hamming distance', 'minimum distance', 'dual code', 'self-dual',
        'macwilliams', 'weight distribution', 'systematic form', 'codeword',
        '[n,k,d]', 'singleton bound', 'plotkin bound', 'griesmer bound',
        'gilbert-varshamov', 'sphere packing', 'perfect code', 'golay',
        'doubly-even', 'hull dimension', 'lcd code', 'error correct'
    ]

    def __init__(self, agent_id: str = 'information_theory_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._entropy_specialist = None
        self._coding_specialist = None
        self._channel_specialist = None

        # Error correcting code specialists (lazy-loaded)
        self._linear_code_specialist = None
        self._hamming_distance_specialist = None
        self._generator_matrix_specialist = None
        self._parity_check_specialist = None
        self._minimum_distance_specialist = None
        self._dual_code_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.information_theory',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='entropy_coding_channel_routing'
            ))

        logger.info(f"[{agent_id}] Information Theory Supervisor initialized")

    @property
    def entropy_specialist(self):
        """Lazy load entropy specialist."""
        if self._entropy_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory import EntropySpecialist
            self._entropy_specialist = EntropySpecialist(
                agent_id='entropy_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._entropy_specialist

    @property
    def coding_specialist(self):
        """Lazy load coding theory specialist."""
        if self._coding_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory import CodingTheorySpecialist
            self._coding_specialist = CodingTheorySpecialist(
                agent_id='coding_theory_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._coding_specialist

    @property
    def channel_specialist(self):
        """Lazy load channel capacity specialist."""
        if self._channel_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory import ChannelCapacitySpecialist
            self._channel_specialist = ChannelCapacitySpecialist(
                agent_id='channel_capacity_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._channel_specialist

    # ========================================
    # Error Correcting Code Specialists
    # ========================================

    @property
    def linear_code_specialist(self):
        """Lazy load linear code specialist."""
        if self._linear_code_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting import LinearCodeSpecialist
            self._linear_code_specialist = LinearCodeSpecialist(
                agent_id='linear_code_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._linear_code_specialist

    @property
    def hamming_distance_specialist(self):
        """Lazy load Hamming distance specialist."""
        if self._hamming_distance_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting import HammingDistanceSpecialist
            self._hamming_distance_specialist = HammingDistanceSpecialist(
                agent_id='hamming_distance_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._hamming_distance_specialist

    @property
    def generator_matrix_specialist(self):
        """Lazy load generator matrix specialist."""
        if self._generator_matrix_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting import GeneratorMatrixSpecialist
            self._generator_matrix_specialist = GeneratorMatrixSpecialist(
                agent_id='generator_matrix_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._generator_matrix_specialist

    @property
    def parity_check_specialist(self):
        """Lazy load parity check specialist."""
        if self._parity_check_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting import ParityCheckSpecialist
            self._parity_check_specialist = ParityCheckSpecialist(
                agent_id='parity_check_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._parity_check_specialist

    @property
    def minimum_distance_specialist(self):
        """Lazy load minimum distance specialist."""
        if self._minimum_distance_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting import MinimumDistanceSpecialist
            self._minimum_distance_specialist = MinimumDistanceSpecialist(
                agent_id='minimum_distance_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._minimum_distance_specialist

    @property
    def dual_code_specialist(self):
        """Lazy load dual code specialist."""
        if self._dual_code_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.information_theory.error_correcting import DualCodeSpecialist
            self._dual_code_specialist = DualCodeSpecialist(
                agent_id='dual_code_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._dual_code_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for information theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            # Query for information theory related tasks
            tasks = self.blackboard.query_entries(tags=['information_theory'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['entropy'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['coding'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['channel'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'routed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Determine routing
            target_specialist = self._determine_specialist(task)

            steps = ['route_task']
            intention = Intention(
                plan_id=f'route_info_theory_{task_id}',
                steps=steps,
                target_desire='information_theory_routing',
                metadata={'task_id': task_id, 'task_entry': task, 'target': target_specialist}
            )
            new_intentions.append(intention)
        return new_intentions

    def _determine_specialist(self, task) -> str:
        """Determine which specialist should handle this task."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        content = str(task.content).lower() if hasattr(task, 'content') else ''

        # Check explicit operation type
        operation = metadata.get('operation', '').lower()

        # Route based on operation
        if any(kw in operation for kw in ['entropy', 'kl_divergence', 'mutual_info', 'cross_entropy']):
            return 'entropy'
        if any(kw in operation for kw in ['huffman', 'hamming', 'parity', 'syndrome']):
            return 'coding'
        if any(kw in operation for kw in ['bsc', 'bec', 'awgn', 'channel', 'capacity', 'rate_distortion']):
            return 'channel'

        # Check content keywords
        combined_text = f"{content} {operation}"

        # Check for specific error correcting code operations FIRST (more specific)
        ec_specific_keywords = {
            'linear_code': ['linear code', 'construct code', 'validate parameters', '[n,k,d]'],
            'generator_matrix': ['generator matrix', 'encode', 'systematic form', 'codeword generation'],
            'parity_check': ['parity check', 'syndrome', 'syndrome decode', 'standard array'],
            'hamming_distance': ['hamming distance', 'hamming weight', 'sphere volume', 'error capability'],
            'minimum_distance': ['minimum distance', 'weight distribution', 'perfect code', 'bounds'],
            'dual_code': ['dual code', 'self-dual', 'macwilliams', 'doubly-even', 'hull']
        }

        for specialist, keywords in ec_specific_keywords.items():
            if any(kw in combined_text for kw in keywords):
                return specialist

        # Broader error correcting score
        ec_score = sum(1 for kw in self.ERROR_CORRECTING_KEYWORDS if kw in combined_text)

        entropy_score = sum(1 for kw in self.ENTROPY_KEYWORDS if kw in combined_text)
        coding_score = sum(1 for kw in self.CODING_KEYWORDS if kw in combined_text)
        channel_score = sum(1 for kw in self.CHANNEL_KEYWORDS if kw in combined_text)

        scores = {
            'entropy': entropy_score,
            'coding': coding_score,
            'channel': channel_score,
            'linear_code': ec_score  # Route to linear code for general EC tasks
        }

        # Return highest scoring, default to entropy
        best = max(scores, key=scores.get) if max(scores.values()) > 0 else 'entropy'
        return best

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'entropy')

            # Mark as routed to prevent re-routing
            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            # Get the appropriate specialist
            specialist_map = {
                'entropy': self.entropy_specialist,
                'coding': self.coding_specialist,
                'channel': self.channel_specialist,
                # Error correcting code specialists
                'linear_code': self.linear_code_specialist,
                'hamming_distance': self.hamming_distance_specialist,
                'generator_matrix': self.generator_matrix_specialist,
                'parity_check': self.parity_check_specialist,
                'minimum_distance': self.minimum_distance_specialist,
                'dual_code': self.dual_code_specialist,
            }

            specialist = specialist_map.get(target, self.entropy_specialist)

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            # Let the specialist pick up the task from blackboard
            # (it's already there, we just need the specialist to run)
            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for information theory problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Entropy operations
        if problem_type == 'shannon_entropy':
            return self.entropy_specialist.shannon_entropy(
                problem.get('probabilities', [])
            )
        if problem_type == 'kl_divergence':
            return self.entropy_specialist.kl_divergence(
                problem.get('p', []),
                problem.get('q', [])
            )
        if problem_type == 'mutual_information':
            return self.entropy_specialist.mutual_information(
                problem.get('joint_probabilities', [])
            )
        if problem_type == 'joint_entropy':
            return self.entropy_specialist.joint_entropy(
                problem.get('joint_probabilities', [])
            )
        if problem_type == 'conditional_entropy':
            return self.entropy_specialist.conditional_entropy(
                problem.get('joint_probabilities', [])
            )

        # Coding operations
        if problem_type == 'huffman_build':
            return self.coding_specialist.build_huffman_code(
                problem.get('symbols', []),
                problem.get('frequencies', [])
            )
        if problem_type == 'huffman_encode':
            return self.coding_specialist.huffman_encode(
                problem.get('message', ''),
                problem.get('code_table')
            )
        if problem_type == 'huffman_decode':
            return self.coding_specialist.huffman_decode(
                problem.get('encoded', ''),
                problem.get('code_table', {})
            )
        if problem_type == 'hamming_encode':
            return self.coding_specialist.hamming_encode_74(
                problem.get('data_bits', [])
            )
        if problem_type == 'hamming_decode':
            return self.coding_specialist.hamming_decode_74(
                problem.get('received', [])
            )

        # Channel operations
        if problem_type == 'bsc_capacity':
            return self.channel_specialist.binary_symmetric_channel_capacity(
                problem.get('crossover_probability', 0.1)
            )
        if problem_type == 'bec_capacity':
            return self.channel_specialist.binary_erasure_channel_capacity(
                problem.get('erasure_probability', 0.1)
            )
        if problem_type == 'awgn_capacity':
            return self.channel_specialist.awgn_channel_capacity(
                problem.get('snr', 10.0),
                problem.get('bandwidth', 1.0)
            )
        if problem_type == 'channel_capacity':
            return self.channel_specialist.compute_channel_capacity(
                problem.get('channel_matrix', [])
            )
        if problem_type == 'rate_distortion':
            return self.channel_specialist.rate_distortion_bound(
                problem.get('source_distribution', []),
                problem.get('distortion', 0.1)
            )

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': [
                'entropy', 'coding', 'channel',
                'linear_code', 'hamming_distance', 'generator_matrix',
                'parity_check', 'minimum_distance', 'dual_code'
            ]
        }

        # Add specialist stats if loaded
        if self._entropy_specialist:
            stats['entropy_tasks'] = self._entropy_specialist.tasks_executed
        if self._coding_specialist:
            stats['coding_tasks'] = self._coding_specialist.tasks_executed
        if self._channel_specialist:
            stats['channel_tasks'] = self._channel_specialist.tasks_executed

        # Error correcting code specialists stats
        if self._linear_code_specialist:
            stats['linear_code_tasks'] = self._linear_code_specialist.tasks_executed
        if self._hamming_distance_specialist:
            stats['hamming_distance_tasks'] = self._hamming_distance_specialist.tasks_executed
        if self._generator_matrix_specialist:
            stats['generator_matrix_tasks'] = self._generator_matrix_specialist.tasks_executed
        if self._parity_check_specialist:
            stats['parity_check_tasks'] = self._parity_check_specialist.tasks_executed
        if self._minimum_distance_specialist:
            stats['minimum_distance_tasks'] = self._minimum_distance_specialist.tasks_executed
        if self._dual_code_specialist:
            stats['dual_code_tasks'] = self._dual_code_specialist.tasks_executed

        return stats
