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
ENTROPY SPECIALIST (Tier 3)
===========================

Native Python implementation for entropy computations.
Handles Shannon entropy, relative entropy (KL divergence), joint and conditional entropy.

NO SYMPY - Pure native mathematical reasoning.
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class EntropySpecialist(BDIAgent):
    """
    Specialist for entropy and information-theoretic computations.

    Capabilities:
    - Shannon entropy H(X)
    - Joint entropy H(X, Y)
    - Conditional entropy H(X|Y)
    - Relative entropy (KL divergence) D_KL(P||Q)
    - Mutual information I(X; Y)
    - Cross entropy H(P, Q)
    - Renyi entropy H_alpha(X)
    """

    def __init__(self, agent_id: str = 'entropy_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        # Register with Directory Facilitator
        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.information_theory.entropy',
                agent_id=agent_id,
                algorithm='native_entropy',
                cost='low',
                instance=self,
                tier='3',
                capabilities='shannon_joint_conditional_kl_mutual_information'
            ))

        logger.info(f"[{agent_id}] Entropy Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for entropy tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['entropy'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['information_theory'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create entropy computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'shannon_entropy')

            steps = ['claim_task', 'validate_input', 'compute_entropy', 'post_result']
            intention = Intention(
                plan_id=f'entropy_{operation}_{task_id}',
                steps=steps,
                target_desire='entropy_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Compute entropy measures."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'validate_input':
            intention.advance()
        elif action == 'compute_entropy':
            self._compute_entropy(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _compute_entropy(self, intention: Intention):
        """Compute the requested entropy measure."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'shannon_entropy')

        try:
            if operation == 'shannon_entropy':
                probs = metadata.get('probabilities', [])
                result = self.shannon_entropy(probs)
            elif operation == 'joint_entropy':
                joint_probs = metadata.get('joint_probabilities', [])
                result = self.joint_entropy(joint_probs)
            elif operation == 'conditional_entropy':
                joint_probs = metadata.get('joint_probabilities', [])
                marginal_y = metadata.get('marginal_y', [])
                result = self.conditional_entropy(joint_probs, marginal_y)
            elif operation == 'kl_divergence':
                p = metadata.get('p', [])
                q = metadata.get('q', [])
                result = self.kl_divergence(p, q)
            elif operation == 'mutual_information':
                joint_probs = metadata.get('joint_probabilities', [])
                result = self.mutual_information(joint_probs)
            elif operation == 'cross_entropy':
                p = metadata.get('p', [])
                q = metadata.get('q', [])
                result = self.cross_entropy(p, q)
            elif operation == 'renyi_entropy':
                probs = metadata.get('probabilities', [])
                alpha = metadata.get('alpha', 2)
                result = self.renyi_entropy(probs, alpha)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Entropy computation failed: {e}")
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
                tags=['entropy', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # NATIVE ENTROPY COMPUTATIONS
    # =========================================================================

    @staticmethod
    def shannon_entropy(probabilities: List[float], base: float = 2.0) -> Dict[str, Any]:
        """
        Compute Shannon entropy H(X) = -sum(p_i * log(p_i)).

        Args:
            probabilities: Probability distribution (must sum to 1)
            base: Logarithm base (2 for bits, e for nats)

        Returns:
            Dictionary with entropy value and metadata
        """
        probs = np.array(probabilities, dtype=float)

        # Validate
        if not np.isclose(probs.sum(), 1.0, atol=1e-6):
            return {'error': 'Probabilities must sum to 1', 'sum': float(probs.sum())}
        if np.any(probs < 0):
            return {'error': 'Probabilities must be non-negative'}

        # Handle zeros (0 * log(0) = 0 by convention)
        probs = probs[probs > 0]

        if base == 2.0:
            entropy = -np.sum(probs * np.log2(probs))
        elif base == math.e:
            entropy = -np.sum(probs * np.log(probs))
        else:
            entropy = -np.sum(probs * np.log(probs)) / np.log(base)

        return {
            'entropy': float(entropy),
            'base': base,
            'unit': 'bits' if base == 2.0 else 'nats' if base == math.e else f'log_{base}',
            'method': 'native_shannon'
        }

    @staticmethod
    def joint_entropy(joint_probs: List[List[float]], base: float = 2.0) -> Dict[str, Any]:
        """
        Compute joint entropy H(X, Y) = -sum(p(x,y) * log(p(x,y))).

        Args:
            joint_probs: 2D joint probability distribution
            base: Logarithm base

        Returns:
            Dictionary with joint entropy value
        """
        probs = np.array(joint_probs, dtype=float).flatten()

        if not np.isclose(probs.sum(), 1.0, atol=1e-6):
            return {'error': 'Joint probabilities must sum to 1'}

        probs = probs[probs > 0]

        if base == 2.0:
            entropy = -np.sum(probs * np.log2(probs))
        else:
            entropy = -np.sum(probs * np.log(probs)) / np.log(base)

        return {
            'joint_entropy': float(entropy),
            'base': base,
            'method': 'native_joint_entropy'
        }

    @staticmethod
    def conditional_entropy(joint_probs: List[List[float]], marginal_y: List[float] = None,
                           base: float = 2.0) -> Dict[str, Any]:
        """
        Compute conditional entropy H(X|Y) = H(X,Y) - H(Y).

        Args:
            joint_probs: 2D joint probability distribution P(X,Y)
            marginal_y: Marginal distribution P(Y), computed if not provided
            base: Logarithm base

        Returns:
            Dictionary with conditional entropy
        """
        joint = np.array(joint_probs, dtype=float)

        # Compute marginal P(Y) if not provided
        if marginal_y is None:
            marginal_y = joint.sum(axis=0)
        else:
            marginal_y = np.array(marginal_y, dtype=float)

        # H(X,Y)
        joint_flat = joint.flatten()
        joint_flat = joint_flat[joint_flat > 0]
        if base == 2.0:
            h_xy = -np.sum(joint_flat * np.log2(joint_flat))
        else:
            h_xy = -np.sum(joint_flat * np.log(joint_flat)) / np.log(base)

        # H(Y)
        marginal_y = marginal_y[marginal_y > 0]
        if base == 2.0:
            h_y = -np.sum(marginal_y * np.log2(marginal_y))
        else:
            h_y = -np.sum(marginal_y * np.log(marginal_y)) / np.log(base)

        cond_entropy = h_xy - h_y

        return {
            'conditional_entropy': float(cond_entropy),
            'joint_entropy': float(h_xy),
            'marginal_entropy_y': float(h_y),
            'base': base,
            'method': 'native_conditional_entropy'
        }

    @staticmethod
    def kl_divergence(p: List[float], q: List[float], base: float = 2.0) -> Dict[str, Any]:
        """
        Compute KL divergence D_KL(P||Q) = sum(p_i * log(p_i / q_i)).

        Args:
            p: True distribution
            q: Approximate distribution
            base: Logarithm base

        Returns:
            Dictionary with KL divergence (can be infinity if q_i=0 where p_i>0)
        """
        p = np.array(p, dtype=float)
        q = np.array(q, dtype=float)

        if len(p) != len(q):
            return {'error': 'Distributions must have same length'}

        # Check for undefined KL (q_i = 0 where p_i > 0)
        mask = p > 0
        if np.any((q[mask] == 0)):
            return {'kl_divergence': float('inf'), 'note': 'Q has zero where P is non-zero'}

        # Compute KL only where p > 0
        p_pos = p[mask]
        q_pos = q[mask]

        if base == 2.0:
            kl = np.sum(p_pos * np.log2(p_pos / q_pos))
        else:
            kl = np.sum(p_pos * np.log(p_pos / q_pos)) / np.log(base)

        return {
            'kl_divergence': float(kl),
            'base': base,
            'method': 'native_kl_divergence'
        }

    @staticmethod
    def mutual_information(joint_probs: List[List[float]], base: float = 2.0) -> Dict[str, Any]:
        """
        Compute mutual information I(X;Y) = H(X) + H(Y) - H(X,Y).

        Args:
            joint_probs: 2D joint probability distribution
            base: Logarithm base

        Returns:
            Dictionary with mutual information
        """
        joint = np.array(joint_probs, dtype=float)

        # Marginals
        p_x = joint.sum(axis=1)
        p_y = joint.sum(axis=0)

        # H(X)
        p_x_pos = p_x[p_x > 0]
        if base == 2.0:
            h_x = -np.sum(p_x_pos * np.log2(p_x_pos))
        else:
            h_x = -np.sum(p_x_pos * np.log(p_x_pos)) / np.log(base)

        # H(Y)
        p_y_pos = p_y[p_y > 0]
        if base == 2.0:
            h_y = -np.sum(p_y_pos * np.log2(p_y_pos))
        else:
            h_y = -np.sum(p_y_pos * np.log(p_y_pos)) / np.log(base)

        # H(X,Y)
        joint_flat = joint.flatten()
        joint_pos = joint_flat[joint_flat > 0]
        if base == 2.0:
            h_xy = -np.sum(joint_pos * np.log2(joint_pos))
        else:
            h_xy = -np.sum(joint_pos * np.log(joint_pos)) / np.log(base)

        mi = h_x + h_y - h_xy

        return {
            'mutual_information': float(mi),
            'entropy_x': float(h_x),
            'entropy_y': float(h_y),
            'joint_entropy': float(h_xy),
            'base': base,
            'method': 'native_mutual_information'
        }

    @staticmethod
    def cross_entropy(p: List[float], q: List[float], base: float = 2.0) -> Dict[str, Any]:
        """
        Compute cross entropy H(P, Q) = -sum(p_i * log(q_i)).

        Args:
            p: True distribution
            q: Predicted distribution
            base: Logarithm base

        Returns:
            Dictionary with cross entropy
        """
        p = np.array(p, dtype=float)
        q = np.array(q, dtype=float)

        if len(p) != len(q):
            return {'error': 'Distributions must have same length'}

        mask = p > 0
        if np.any(q[mask] <= 0):
            return {'cross_entropy': float('inf'), 'note': 'Q has zero/negative where P is non-zero'}

        p_pos = p[mask]
        q_pos = q[mask]

        if base == 2.0:
            ce = -np.sum(p_pos * np.log2(q_pos))
        else:
            ce = -np.sum(p_pos * np.log(q_pos)) / np.log(base)

        return {
            'cross_entropy': float(ce),
            'base': base,
            'method': 'native_cross_entropy'
        }

    @staticmethod
    def renyi_entropy(probabilities: List[float], alpha: float, base: float = 2.0) -> Dict[str, Any]:
        """
        Compute Renyi entropy H_alpha(X) = (1/(1-alpha)) * log(sum(p_i^alpha)).

        Special cases:
        - alpha -> 1: Shannon entropy
        - alpha = 0: Hartley entropy (log of support size)
        - alpha = 2: Collision entropy
        - alpha -> inf: Min-entropy

        Args:
            probabilities: Probability distribution
            alpha: Order parameter (alpha >= 0, alpha != 1)
            base: Logarithm base

        Returns:
            Dictionary with Renyi entropy
        """
        probs = np.array(probabilities, dtype=float)
        probs = probs[probs > 0]

        if alpha < 0:
            return {'error': 'Alpha must be non-negative'}

        if np.isclose(alpha, 1.0):
            # Limit as alpha -> 1 is Shannon entropy
            if base == 2.0:
                entropy = -np.sum(probs * np.log2(probs))
            else:
                entropy = -np.sum(probs * np.log(probs)) / np.log(base)
            return {
                'renyi_entropy': float(entropy),
                'alpha': alpha,
                'note': 'alpha=1 gives Shannon entropy',
                'method': 'native_renyi_entropy'
            }

        if alpha == 0:
            # Hartley entropy
            entropy = np.log(len(probs)) / np.log(base) if base != math.e else np.log(len(probs))
            return {
                'renyi_entropy': float(entropy),
                'alpha': alpha,
                'note': 'alpha=0 gives Hartley entropy',
                'method': 'native_renyi_entropy'
            }

        if alpha == float('inf'):
            # Min-entropy
            entropy = -np.log(np.max(probs)) / np.log(base) if base != math.e else -np.log(np.max(probs))
            return {
                'renyi_entropy': float(entropy),
                'alpha': alpha,
                'note': 'alpha=inf gives min-entropy',
                'method': 'native_renyi_entropy'
            }

        # General case
        sum_p_alpha = np.sum(probs ** alpha)
        if base == 2.0:
            entropy = (1.0 / (1.0 - alpha)) * np.log2(sum_p_alpha)
        else:
            entropy = (1.0 / (1.0 - alpha)) * np.log(sum_p_alpha) / np.log(base)

        return {
            'renyi_entropy': float(entropy),
            'alpha': alpha,
            'base': base,
            'method': 'native_renyi_entropy'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'shannon_entropy', 'joint_entropy', 'conditional_entropy',
                'kl_divergence', 'mutual_information', 'cross_entropy', 'renyi_entropy'
            ]
        }
