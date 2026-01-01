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
HÖLDER INEQUALITY SPECIALIST (Tier 3)
=====================================

Verifies and applies the Hölder inequality for Lp spaces.

CAPABILITIES:
------------
- Discrete Hölder: ∑|aᵢbᵢ| ≤ ||a||_p · ||b||_q
- Conjugate exponents: 1/p + 1/q = 1
- Special cases: p=2 (Cauchy-Schwarz), p=1, p→∞
- Integral form (numerical)

ALGORITHMIC BACKING:
-------------------
Native inequalities engine (core/inequalities.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Hölder, O. (1889). "Ueber einen Mittelwerthsatz".
- Rogers, L. J. (1888). "An extension of a certain theorem in inequalities".
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable
from symbo_agentic_reasoners.core.inequalities import holder_inequality

logger = logging.getLogger(__name__)


class HolderInequalitySpecialist(BDIAgent):
    """
    Hölder Inequality Specialist - Lp Norm Inequalities

    DIRECTIVE:
    ---------
    Verify and apply Hölder inequality for conjugate exponents.

    OPERATIONS:
    ----------
    - verify: Verify Hölder inequality
    - compute_conjugate: Compute conjugate exponent q = p/(p-1)
    - compute_norms: Compute ||a||_p and ||b||_q

    INEQUALITY:
    ----------
    ∑|aᵢbᵢ| ≤ (∑|aᵢ|^p)^(1/p) · (∑|bᵢ|^q)^(1/q)
    where 1/p + 1/q = 1, p > 1
    """

    def __init__(
        self,
        agent_id: str = 'holder_inequality_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Hölder Inequality Specialist."""
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.inequalities_verified = 0

        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Hölder Inequality Specialist initialized")

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.inequalities.holder',
            agent_id=self.agent_id,
            algorithm='native_holder_inequality',
            cost='low',
            instance=self,
            tier='3',
            operations='verify_holder_conjugate_exponent_lp_norms'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.inequalities.holder")

    def update_beliefs(self):
        """PERCEIVE: Monitor for Hölder inequality tasks."""
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['holder'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['hölder'], status=EntryStatus.PENDING)
            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create verification plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            steps = ['claim_task', 'parse_input', 'verify_holder', 'post_result']
            intention = Intention(
                plan_id=f'holder_verify_{task_id}',
                steps=steps,
                target_desire='verify_holder',
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute verification step."""
        action = intention.get_current_action()
        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(intention.metadata['task_id'], EntryStatus.IN_PROGRESS)
                intention.advance()
            elif action == 'parse_input':
                task = intention.metadata['task_entry']
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                intention.metadata['a'] = np.array(metadata.get('a', []), dtype=float)
                intention.metadata['b'] = np.array(metadata.get('b', []), dtype=float)
                intention.metadata['p'] = float(metadata.get('p', 2.0))
                intention.advance()
            elif action == 'verify_holder':
                result = holder_inequality(
                    intention.metadata['a'],
                    intention.metadata['b'],
                    intention.metadata['p']
                )
                intention.metadata['result'] = result
                self.inequalities_verified += 1
                intention.advance()
            elif action == 'post_result':
                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(intention.metadata['result'])),
                        author_agent=self.agent_id,
                        tags=['holder', 'result'],
                        status=EntryStatus.COMPLETED,
                        metadata=intention.metadata['result']
                    )
                    self.blackboard.post(result_entry)
                self.tasks_succeeded += 1
                self.tasks_executed += 1
                intention.advance()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Step failed: {e}")
            self.tasks_failed += 1
            self.tasks_executed += 1
            while not intention.is_complete():
                intention.advance()

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """Process Hölder inequality verification (synchronous API)."""
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        try:
            a = np.array(metadata.get('a', []), dtype=float)
            b = np.array(metadata.get('b', []), dtype=float)
            p = float(metadata.get('p', 2.0))
            result = holder_inequality(a, b, p)
            self.tasks_executed += 1
            self.tasks_succeeded += 1
            self.inequalities_verified += 1
            return result
        except Exception as e:
            logger.error(f"[{self.agent_id}] Processing error: {e}")
            self.tasks_executed += 1
            self.tasks_failed += 1
            return {'error': str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100) if self.tasks_executed > 0 else 0.0,
            'inequalities_verified': self.inequalities_verified,
            'tier': '3',
            'domain': 'inequalities'
        }
