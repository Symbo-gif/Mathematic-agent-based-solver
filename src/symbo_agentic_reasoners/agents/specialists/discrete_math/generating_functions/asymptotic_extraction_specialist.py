# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
ASYMPTOTIC EXTRACTION SPECIALIST (Tier 3)
==========================================

Handles asymptotic coefficient extraction from generating functions.

CAPABILITIES:
------------
- dominant_pole: Find dominant singularity
- growth_rate: Extract ρ from aₙ ~ C·ρⁿ·nᵝ
- power_law: Determine β (power correction)
- full_formula: Complete asymptotic formula
- coefficient_extraction: Direct [xⁿ]F extraction

FORMULATION:
-----------
Singularity analysis: aₙ ~ C · ρⁿ · nᵝ
where ρ = 1/|dominant pole|, β = multiplicity - 1

ALGORITHMIC BACKING:
-------------------
Native generating_functions engine (core/generating_functions.py)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Flajolet, P., & Sedgewick, R. (2009). Analytic Combinatorics, Chapter IV-VI.
- Wilf, H. S. (2006). Generatingfunctionology, Chapter 5.
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


class AsymptoticExtractionSpecialist(BDIAgent):
    """
    Asymptotic Extraction Specialist - Singularity Analysis

    DIRECTIVE:
    ---------
    Extract asymptotic behavior of coefficients from generating functions
    using singularity analysis.

    OPERATIONS:
    ----------
    - dominant_singularity: Find dominant pole ρ
    - extract_growth_rate: Compute base growth ρ
    - power_correction: Determine polynomial factor nᵝ
    - full_asymptotic: Complete formula aₙ ~ C·ρⁿ·nᵝ
    - coefficient_extraction: Direct [xⁿ]F extraction

    FORMULATION:
    -----------
    For rational GF P(x)/Q(x), if ρ is dominant pole:
    aₙ ~ C · ρⁿ · nᵝ
    where β = multiplicity - 1

    REFERENCE:
    ---------
    - Flajolet & Sedgewick (2009), Chapter IV: Complex Asymptotics
    - Singularity analysis method
    """

    def __init__(
        self,
        agent_id: str = 'asymptotic_extraction_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Asymptotic Extraction Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.dominant_poles_found = 0
        self.growth_rates_extracted = 0
        self.full_formulas_computed = 0
        self.coefficients_extracted = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.discrete.gf.asymptotic',
            agent_id=self.agent_id,
            algorithm='singularity_analysis',
            cost='low',
            instance=self,
            tier='3',
            operations='dominant_growth_power_formula_extract'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.discrete.gf.asymptotic")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for asymptotic extraction tasks."""
        if not self.blackboard:
            return

        try:
            asymptotic_tasks = self.blackboard.query_entries(
                tags=['asymptotic', 'singularity', 'coefficient_extraction'],
                status=EntryStatus.PENDING
            )

            for task in asymptotic_tasks:
                belief_key = f'pending_asymp_{task.entry_id}'

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
        """DELIBERATE: Create plans for pending asymptotic tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_asymp_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'dominant_singularity')

            intention = Intention(
                plan_id=f'asymp_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='extract_asymptotics',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan for asymptotic task {task_id} ({operation})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the asymptotic extraction plan."""
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
            'operation': intention.metadata.get('operation', 'dominant_singularity'),
            'numerator': metadata.get('numerator', [1]),
            'denominator': metadata.get('denominator', [1, -1]),
            'n': metadata.get('n', 10),
            'n_terms': metadata.get('n_terms', 100)
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Perform asymptotic extraction."""
        parsed_data = intention.metadata.get('parsed_data', {})
        operation = parsed_data['operation']

        try:
            numerator = parsed_data['numerator']
            denominator = parsed_data['denominator']
            rational_gf = RationalGF(numerator, denominator)

            if operation == 'dominant_singularity':
                dom_sing = rational_gf.dominant_singularity()

                result = {
                    'dominant_singularity': float(dom_sing),
                    'rho': 1.0 / float(dom_sing) if dom_sing != 0 else float('inf'),
                    'operation': 'dominant_singularity',
                    'interpretation': f'Growth rate ρ = {1.0/float(dom_sing) if dom_sing != 0 else "inf"}',
                    'numerator': numerator,
                    'denominator': denominator
                }
                self.dominant_poles_found += 1

            elif operation == 'extract_growth':
                asymptotic = rational_gf.asymptotic_growth()

                result = {
                    'rho': float(asymptotic['rho']),
                    'operation': 'extract_growth',
                    'formula': f"a_n ~ ρ^n where ρ = {asymptotic['rho']:.6f}",
                    'numerator': numerator,
                    'denominator': denominator
                }
                self.growth_rates_extracted += 1

            elif operation == 'full_asymptotic':
                asymptotic = rational_gf.asymptotic_growth()

                result = {
                    'rho': float(asymptotic['rho']),
                    'C': float(asymptotic['C']),
                    'beta': int(asymptotic['beta']),
                    'formula': f"a_n ~ {asymptotic['C']:.6f} * {asymptotic['rho']:.6f}^n * n^{asymptotic['beta']}",
                    'operation': 'full_asymptotic',
                    'numerator': numerator,
                    'denominator': denominator
                }
                self.full_formulas_computed += 1

            elif operation == 'coefficient_extraction':
                # Direct coefficient extraction via series expansion
                n = parsed_data['n']
                n_terms = max(n + 1, parsed_data['n_terms'])

                ogf = OrdinaryGF.from_rational(numerator, denominator, n_terms)

                if n < len(ogf.coefficients):
                    coefficient = float(ogf.coefficients[n])
                else:
                    coefficient = 0.0

                result = {
                    'coefficient': coefficient,
                    'n': n,
                    'operation': 'coefficient_extraction',
                    'notation': f'[x^{n}]F',
                    'numerator': numerator,
                    'denominator': denominator
                }
                self.coefficients_extracted += 1

            elif operation == 'power_correction':
                asymptotic = rational_gf.asymptotic_growth()

                result = {
                    'beta': int(asymptotic['beta']),
                    'multiplicity': int(asymptotic['beta']) + 1,
                    'operation': 'power_correction',
                    'interpretation': f"Polynomial correction n^{asymptotic['beta']}",
                    'numerator': numerator,
                    'denominator': denominator
                }

            else:
                raise ValueError(f"Unknown asymptotic operation: {operation}")

            result['method'] = 'singularity_analysis'
            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"Asymptotic extraction failed: {e}")

    def _execute_verify(self, intention: Intention):
        """Verify result validity."""
        result = intention.metadata.get('result', {})

        if 'rho' in result:
            if not isinstance(result['rho'], (int, float)):
                raise ValueError("Growth rate rho must be numeric")

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
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'asymptotic',
                tags=['asymptotic', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_asymp_{task_id}')
        self.add_belief(f'completed_{task_id}', result)

        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"Asymptotic extraction failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'asymptotic', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        self.remove_belief(f'pending_asymp_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Synchronous API for asymptotic extraction.

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Result dictionary with asymptotic formula or extracted coefficient
        """
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'dominant_singularity')

        try:
            numerator = metadata.get('numerator', [1])
            denominator = metadata.get('denominator', [1, -1])
            rational_gf = RationalGF(numerator, denominator)

            if operation == 'dominant_singularity':
                dom_sing = rational_gf.dominant_singularity()

                result = {
                    'dominant_singularity': float(dom_sing),
                    'rho': 1.0 / float(dom_sing) if dom_sing != 0 else float('inf'),
                    'method': 'singularity_analysis'
                }
                self.dominant_poles_found += 1

            elif operation == 'full_asymptotic':
                asymptotic = rational_gf.asymptotic_growth()

                result = asymptotic
                self.full_formulas_computed += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'singularity_analysis'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'dominant_poles_found': self.dominant_poles_found,
            'growth_rates_extracted': self.growth_rates_extracted,
            'full_formulas_computed': self.full_formulas_computed,
            'coefficients_extracted': self.coefficients_extracted,
            'tier': '3',
            'type': 'specialist',
            'domain': 'generating_functions'
        })
        return stats


if __name__ == "__main__":
    """Test Asymptotic Extraction Specialist"""
    print("=" * 80)
    print("ASYMPTOTIC EXTRACTION SPECIALIST TEST")
    print("=" * 80)
    print()

    specialist = AsymptoticExtractionSpecialist()
    print()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    # Test 1: Fibonacci asymptotic
    print("Test 1: Fibonacci GF asymptotic formula")
    task1 = MockTask({
        'operation': 'full_asymptotic',
        'numerator': [0, 1],
        'denominator': [1, -1, -1]
    })
    result1 = specialist.process(task1)
    print(f"  ρ = {result1.get('rho', 'N/A'):.6f} (should be φ ≈ 1.618034)")
    print(f"  β = {result1.get('beta', 'N/A')}")
    print()

    # Test 2: Dominant singularity
    print("Test 2: Find dominant singularity of 1/(1-2x)")
    task2 = MockTask({
        'operation': 'dominant_singularity',
        'numerator': [1],
        'denominator': [1, -2]
    })
    result2 = specialist.process(task2)
    print(f"  Dominant singularity: {result2.get('dominant_singularity', 'N/A'):.6f}")
    print(f"  Growth rate ρ: {result2.get('rho', 'N/A'):.6f}")
    print()

    # Statistics
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
