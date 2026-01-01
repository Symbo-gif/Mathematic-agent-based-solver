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
RATIONAL GENERATING FUNCTION SPECIALIST (Tier 3)
=================================================

Handles rational generating function analysis: P(x)/Q(x).

CAPABILITIES:
------------
- poles: Find all roots of denominator Q(x)
- dominant_singularity: Find dominant pole (smallest |pole|)
- asymptotic_growth: Extract growth rate aₙ ~ C·ρⁿ·nᵝ
- expand_to_series: Convert P(x)/Q(x) to power series

FORMULATION:
-----------
Rational GF: A(x) = P(x)/Q(x) where P, Q are polynomials

ALGORITHMIC BACKING:
-------------------
Native generating_functions engine (core/generating_functions.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Wilf, H. S. (2006). Generatingfunctionology, Chapter 4.
- Flajolet, P., & Sedgewick, R. (2009). Analytic Combinatorics, Chapter IV.
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
from symbo_agentic_reasoners.core.generating_functions import (
    RationalGF, OrdinaryGF
)

logger = logging.getLogger(__name__)


class RationalGFSpecialist(BDIAgent):
    """
    Rational Generating Function Specialist - P(x)/Q(x) Analysis

    DIRECTIVE:
    ---------
    Analyze rational generating functions for poles, dominant singularities,
    and asymptotic behavior.

    OPERATIONS:
    ----------
    - find_poles: Compute all roots of denominator
    - dominant_pole: Find pole with minimum absolute value
    - asymptotic_formula: Extract aₙ ~ C·ρⁿ·nᵝ
    - expand_series: Convert rational GF to power series

    FORMULATION:
    -----------
    Rational GF: A(x) = P(x)/Q(x)

    Singularity analysis: aₙ ~ C·ρⁿ·nᵝ where ρ = 1/|dominant pole|

    REFERENCE:
    ---------
    - Flajolet & Sedgewick (2009), Chapter IV: Complex Asymptotics
    - Wilf (2006), Chapter 4: Applications
    """

    def __init__(
        self,
        agent_id: str = 'rational_gf_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Rational GF Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.poles_found = 0
        self.dominant_poles_computed = 0
        self.asymptotic_formulas_extracted = 0
        self.series_expansions = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.discrete.gf.rational',
            agent_id=self.agent_id,
            algorithm='rational_gf_analysis',
            cost='low',
            instance=self,
            tier='3',
            operations='poles_dominant_asymptotic_expand'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.discrete.gf.rational")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for rational GF tasks."""
        if not self.blackboard:
            return

        try:
            rational_gf_tasks = self.blackboard.query_entries(
                tags=['rational_gf', 'poles', 'asymptotic'],
                status=EntryStatus.PENDING
            )

            for task in rational_gf_tasks:
                belief_key = f'pending_rational_{task.entry_id}'

                if self.has_belief(f'completed_{task.entry_id}'):
                    continue

                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans for pending rational GF tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_rational_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'find_poles')

            intention = Intention(
                plan_id=f'rational_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='analyze_rational_gf',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan for rational GF task {task_id} ({operation})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the rational GF analysis plan."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        logger.debug(f"[{self.agent_id}] Executing: {action} for task {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task_id)
            elif action == 'parse_input':
                self._execute_parse_input(intention, task)
            elif action == 'compute':
                self._execute_compute(intention)
            elif action == 'verify':
                self._execute_verify(intention)
            elif action == 'post_result':
                self._execute_post_result(intention, task)
            else:
                logger.warning(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_failure(intention, task, str(e))

    def _execute_claim_task(self, intention: Intention, task_id: str):
        """Claim task as IN_PROGRESS."""
        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
        intention.advance()

    def _execute_parse_input(self, intention: Intention, task: Any):
        """Parse and validate input parameters."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}

        parsed_data = {
            'operation': intention.metadata.get('operation', 'find_poles'),
            'numerator': metadata.get('numerator', [1]),
            'denominator': metadata.get('denominator', [1, -1]),
            'n_terms': metadata.get('n_terms', 10)
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Perform rational GF analysis."""
        parsed_data = intention.metadata.get('parsed_data', {})
        operation = parsed_data['operation']

        try:
            numerator = parsed_data['numerator']
            denominator = parsed_data['denominator']
            rational_gf = RationalGF(numerator, denominator)

            if operation == 'find_poles':
                poles = rational_gf.poles()
                result = {
                    'poles': [complex(p) if np.iscomplexobj(p) else float(p) for p in poles],
                    'pole_count': len(poles),
                    'operation': 'find_poles',
                    'numerator': numerator,
                    'denominator': denominator
                }
                # Convert complex to real/imag dict for JSON serialization
                result['poles'] = [{'real': float(p.real), 'imag': float(p.imag)} if isinstance(p, complex)
                                  else float(p) for p in poles]
                self.poles_found += 1

            elif operation == 'dominant_pole':
                dom_sing = rational_gf.dominant_singularity()
                result = {
                    'dominant_singularity': float(dom_sing),
                    'rho': 1.0 / float(dom_sing) if dom_sing != 0 else float('inf'),
                    'operation': 'dominant_pole',
                    'numerator': numerator,
                    'denominator': denominator
                }
                self.dominant_poles_computed += 1

            elif operation == 'asymptotic_formula':
                asymptotic = rational_gf.asymptotic_growth()
                result = {
                    'rho': float(asymptotic['rho']),
                    'C': float(asymptotic['C']),
                    'beta': int(asymptotic['beta']),
                    'formula': f"a_n ~ {asymptotic['C']} * {asymptotic['rho']}^n * n^{asymptotic['beta']}",
                    'operation': 'asymptotic_formula',
                    'numerator': numerator,
                    'denominator': denominator
                }
                self.asymptotic_formulas_extracted += 1

            elif operation == 'expand_series':
                n_terms = parsed_data['n_terms']
                ogf = OrdinaryGF.from_rational(numerator, denominator, n_terms)
                result = {
                    'coefficients': ogf.coefficients.tolist(),
                    'n_terms': n_terms,
                    'operation': 'expand_series',
                    'numerator': numerator,
                    'denominator': denominator
                }
                self.series_expansions += 1

            else:
                raise ValueError(f"Unknown rational GF operation: {operation}")

            result['method'] = 'rational_gf'
            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"Rational GF analysis failed: {e}")

    def _execute_verify(self, intention: Intention):
        """Verify result validity."""
        result = intention.metadata.get('result', {})

        if 'poles' in result:
            if not isinstance(result['poles'], list):
                raise ValueError("Poles must be a list")

        intention.advance()

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result to Blackboard."""
        result = intention.metadata.get('result', {})
        task_id = intention.metadata.get('task_id')

        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.RESULT,
                content=str(result),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'rational_gf',
                tags=['rational_gf', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_rational_{task_id}')
        self.add_belief(f'completed_{task_id}', result)

        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"Rational GF analysis failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'rational_gf', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        self.remove_belief(f'pending_rational_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Synchronous API for rational GF operations.

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Result dictionary with poles, asymptotic formula, or series expansion
        """
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'find_poles')

        try:
            numerator = metadata.get('numerator', [1])
            denominator = metadata.get('denominator', [1, -1])
            rational_gf = RationalGF(numerator, denominator)

            if operation == 'find_poles':
                poles = rational_gf.poles()
                result = {
                    'poles': poles.tolist(),
                    'pole_count': len(poles),
                    'method': 'rational_gf_poles'
                }
                self.poles_found += 1

            elif operation == 'dominant_pole':
                dom_sing = rational_gf.dominant_singularity()
                result = {
                    'dominant_singularity': float(dom_sing),
                    'rho': 1.0 / float(dom_sing) if dom_sing != 0 else float('inf'),
                    'method': 'dominant_singularity'
                }
                self.dominant_poles_computed += 1

            elif operation == 'asymptotic_formula':
                asymptotic = rational_gf.asymptotic_growth()
                result = asymptotic
                self.asymptotic_formulas_extracted += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'rational_gf'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'poles_found': self.poles_found,
            'dominant_poles_computed': self.dominant_poles_computed,
            'asymptotic_formulas_extracted': self.asymptotic_formulas_extracted,
            'series_expansions': self.series_expansions,
            'tier': '3',
            'type': 'specialist',
            'domain': 'generating_functions'
        })
        return stats


if __name__ == "__main__":
    """Test Rational GF Specialist"""
    print("=" * 80)
    print("RATIONAL GF SPECIALIST TEST")
    print("=" * 80)
    print()

    specialist = RationalGFSpecialist()
    print()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    # Test 1: Find poles of Fibonacci GF
    print("Test 1: Find poles of Fibonacci GF x/(1-x-x²)")
    task1 = MockTask({
        'operation': 'find_poles',
        'numerator': [0, 1],
        'denominator': [1, -1, -1]
    })
    result1 = specialist.process(task1)
    print(f"  Poles: {result1['poles']}")
    print()

    # Test 2: Dominant singularity
    print("Test 2: Dominant singularity of Fibonacci GF")
    task2 = MockTask({
        'operation': 'dominant_pole',
        'numerator': [0, 1],
        'denominator': [1, -1, -1]
    })
    result2 = specialist.process(task2)
    print(f"  Dominant singularity: {result2['dominant_singularity']:.6f}")
    print(f"  Growth rate ρ: {result2['rho']:.6f}")
    print()

    # Test 3: Asymptotic formula
    print("Test 3: Asymptotic formula for Fibonacci")
    task3 = MockTask({
        'operation': 'asymptotic_formula',
        'numerator': [0, 1],
        'denominator': [1, -1, -1]
    })
    result3 = specialist.process(task3)
    print(f"  ρ: {result3['rho']:.6f}")
    print(f"  β: {result3['beta']}")
    print()

    # Statistics
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
