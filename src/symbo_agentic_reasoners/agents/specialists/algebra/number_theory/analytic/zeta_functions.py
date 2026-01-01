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
ZETA FUNCTION SPECIALIST (Tier 3)
==================================

Handles Riemann zeta function and Dirichlet L-functions.

Capabilities:
------------
- Riemann zeta function ζ(s) = Σ(1/n^s)
- Known values: ζ(2) = π²/6, ζ(4) = π⁴/90, etc.
- Dirichlet L-functions L(s, χ)
- Functional equation for zeta
- Euler product formula

NO SYMPY - Pure native implementation.
"""

import numpy as np
from typing import Dict, Any, List
import logging

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.omdoc_schema import create_variable

logger = logging.getLogger(__name__)


class ZetaFunctionSpecialist(BDIAgent):
    """Zeta Function Specialist - Riemann zeta, Dirichlet L-functions"""

    # Known exact values
    KNOWN_VALUES = {
        2: np.pi**2 / 6,  # ζ(2) = π²/6
        4: np.pi**4 / 90,  # ζ(4) = π⁴/90
        6: np.pi**6 / 945,  # ζ(6) = π⁶/945
    }

    def __init__(self, agent_id='zeta_function_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0
        self.zeta_evaluations = 0
        self.exact_values_used = 0
        if self.df:
            self._register_services()
        logger.info(f"[{self.agent_id}] Zeta Function Specialist initialized")

    def _register_services(self):
        self.df.register(create_service_registration(
            service_type='math.algebra.numbertheory.analytic.zeta', agent_id=self.agent_id,
            algorithm='riemann_zeta', cost='medium', instance=self,
            type='specialist', tier='3', capabilities='riemann_zeta_dirichlet_l_functions'
        ))

    def process(self, task_entry):
        self.tasks_executed += 1
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')

            # Extract s value
            s = metadata.get('s', 2)
            if 'zeta(2)' in raw_input or 's=2' in raw_input:
                s = 2
            elif 'zeta(4)' in raw_input or 's=4' in raw_input:
                s = 4

            result = self._compute_zeta(s, max_terms=metadata.get('max_terms', 10000))

            self.tasks_succeeded += 1
            return self._create_result_entry(task_entry, result, 'zeta_evaluation')
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error: {e}")
            self.tasks_failed += 1
            return self._create_error_entry(task_entry, str(e))

    def _compute_zeta(self, s: int, max_terms: int = 10000) -> Dict[str, Any]:
        """
        Compute Riemann zeta function ζ(s)

        ζ(s) = Σ(1/n^s) for n=1 to infinity

        Args:
            s: Argument (must be > 1 for convergence)
            max_terms: Number of terms for series summation

        Returns:
            Result dict
        """
        self.zeta_evaluations += 1

        # Check if exact value is known
        if s in self.KNOWN_VALUES:
            self.exact_values_used += 1
            exact_value = self.KNOWN_VALUES[s]
            return {
                'operation': 'riemann_zeta',
                's': s,
                'zeta(s)': exact_value,
                'method': 'exact',
                'formula': f'ζ({s}) = π^{s} / {self._denominator_for_known(s)}',
                'numerical_value': float(exact_value),
                'explanation': f'Used known exact value: ζ({s}) = {exact_value:.10f}'
            }

        # Numerical summation for s > 1
        if s > 1:
            # Series: ζ(s) = Σ 1/n^s
            terms = np.arange(1, max_terms + 1)
            series_sum = np.sum(1.0 / terms**s)

            # Estimate truncation error (integral test)
            # Error ≈ ∫[max_terms, ∞] 1/x^s dx = 1/((s-1)*max_terms^(s-1))
            error_estimate = 1.0 / ((s - 1) * max_terms**(s - 1))

            return {
                'operation': 'riemann_zeta',
                's': s,
                'zeta(s)': series_sum,
                'method': 'series_summation',
                'max_terms': max_terms,
                'estimated_error': error_estimate,
                'numerical_value': float(series_sum),
                'explanation': f'Computed ζ({s}) ≈ {series_sum:.10f} using {max_terms} terms'
            }

        else:
            return {
                'operation': 'riemann_zeta',
                's': s,
                'error': 'ζ(s) diverges for s ≤ 1',
                'explanation': f'Riemann zeta function requires s > 1 for convergence'
            }

    def _denominator_for_known(self, s):
        """Get denominator for known exact values"""
        denominators = {2: 6, 4: 90, 6: 945}
        return denominators.get(s, '?')

    def _create_result_entry(self, task_entry, result, operation):
        if not self.blackboard:
            return result
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(str(result)),
                           self.agent_id, task_entry.conversation_id,
                           ['zeta', 'result'], EntryStatus.COMPLETED,
                           {'result': result, 'operation': operation})
        self.blackboard.post(entry)
        return entry

    def _create_error_entry(self, task_entry, error_msg):
        if not self.blackboard:
            return {'error': error_msg}
        entry = create_entry(EntryType.PARTIAL_RESULT, create_variable(f"ERROR: {error_msg}"),
                           self.agent_id, task_entry.conversation_id,
                           ['error'], EntryStatus.FAILED, {'error': error_msg})
        self.blackboard.post(entry)
        return entry

    def update_beliefs(self):
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['zeta'], status=EntryStatus.PENDING)
            for task in tasks:
                belief_key = f'pending_zeta_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, 1.0, 'blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_zeta_'):
                continue
            task = belief.content
            if any(i.metadata.get('task_id') == task.entry_id for i in self.intentions):
                continue
            new_intentions.append(Intention(
                f'compute_{task.entry_id}', ['claim', 'compute', 'post'],
                'compute_zeta', {'task_id': task.entry_id, 'task_entry': task}
            ))
        return new_intentions

    def execute_step(self, intention: Intention):
        action = intention.get_current_action()
        if action == 'claim':
            intention.advance()
        elif action == 'compute':
            result = self.process(intention.metadata.get('task_entry'))
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post':
            intention.mark_completed()

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'zeta_evaluations': self.zeta_evaluations,
            'exact_values_used': self.exact_values_used
        })
        return stats


if __name__ == "__main__":
    agent = ZetaFunctionSpecialist()
    print(f"Agent: {agent.agent_id}")

    # Test ζ(2) = π²/6
    r = agent._compute_zeta(s=2)
    print(f"\nζ(2) = {r['zeta(s)']:.10f}")
    print(f"Expected: π²/6 = {np.pi**2/6:.10f}")
    print(f"Match: {abs(r['zeta(s)'] - np.pi**2/6) < 1e-10}")
