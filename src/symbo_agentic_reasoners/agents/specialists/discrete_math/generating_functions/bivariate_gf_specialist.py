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
BIVARIATE GENERATING FUNCTION SPECIALIST (Tier 3)
==================================================

Handles two-variable generating functions F(x,y).

CAPABILITIES:
------------
- from_2d_array: Build F(x,y) from coefficient matrix
- extract_diagonal: Get [xⁿyⁿ]F coefficients
- substitute: Evaluate F(x,1) or F(1,y)
- coefficient_nm: Get [xⁿyᵐ]F specific coefficient

FORMULATION:
-----------
Bivariate GF: F(x,y) = Σₙ Σₘ aₙ,ₘ xⁿyᵐ

ALGORITHMIC BACKING:
-------------------
Native NumPy operations (core computation engine)

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- Wilf, H. S. (2006). Generatingfunctionology, Chapter 5.
- Flajolet, P., & Sedgewick, R. (2009). Analytic Combinatorics, Part B.
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

logger = logging.getLogger(__name__)


class BivariateGFSpecialist(BDIAgent):
    """
    Bivariate Generating Function Specialist - Two-Variable GFs

    DIRECTIVE:
    ---------
    Handle two-variable generating functions F(x,y) = Σ aₙ,ₘ xⁿyᵐ.

    OPERATIONS:
    ----------
    - from_2d_array: Build F(x,y) from 2D coefficient matrix
    - extract_diagonal: Get diagonal coefficients [xⁿyⁿ]F
    - substitute: F(x,1), F(1,y), or F(x,x) evaluation
    - coefficient_nm: Get specific [xⁿyᵐ]F coefficient
    - lattice_paths: Count lattice paths (common BGF application)

    FORMULATION:
    -----------
    BGF: F(x,y) = Σₙ≥₀ Σₘ≥₀ aₙ,ₘ xⁿyᵐ

    Example: Lattice paths F(x,y) = 1/(1-x-y)

    REFERENCE:
    ---------
    - Wilf (2006), Chapter 5: Multi-variable GFs
    - Flajolet & Sedgewick (2009), Part B
    """

    def __init__(
        self,
        agent_id: str = 'bivariate_gf_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Bivariate GF Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.bgf_constructed = 0
        self.diagonals_extracted = 0
        self.substitutions_performed = 0
        self.coefficients_extracted = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.discrete.gf.bivariate',
            agent_id=self.agent_id,
            algorithm='bivariate_gf_operations',
            cost='low',
            instance=self,
            tier='3',
            operations='from_2d_diagonal_substitute_coefficient'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered: math.discrete.gf.bivariate")

    # ==========================================================================
    # BDI IMPLEMENTATION
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for bivariate GF tasks."""
        if not self.blackboard:
            return

        try:
            bgf_tasks = self.blackboard.query_entries(
                tags=['bivariate', 'bivariate_gf', 'bgf', 'two_variable'],
                status=EntryStatus.PENDING
            )

            for task in bgf_tasks:
                belief_key = f'pending_bgf_{task.entry_id}'

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
        """DELIBERATE: Create plans for pending BGF tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_bgf_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'from_2d_array')

            intention = Intention(
                plan_id=f'bgf_{task_id}',
                steps=['claim_task', 'parse_input', 'compute', 'verify', 'post_result'],
                target_desire='compute_bgf',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan for BGF task {task_id} ({operation})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the BGF computation plan."""
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
            'operation': intention.metadata.get('operation', 'from_2d_array'),
            'coefficients_2d': metadata.get('coefficients_2d', metadata.get('matrix', [[1]])),
            'n': metadata.get('n', 0),
            'm': metadata.get('m', 0),
            'max_degree': metadata.get('max_degree', 5),
            'substitute_value': metadata.get('substitute_value', 1),
            'variable': metadata.get('variable', 'x')  # Which variable to substitute
        }

        intention.metadata['parsed_data'] = parsed_data
        intention.advance()

    def _execute_compute(self, intention: Intention):
        """Perform BGF computation."""
        parsed_data = intention.metadata.get('parsed_data', {})
        operation = parsed_data['operation']

        try:
            if operation == 'from_2d_array':
                coefficients_2d = parsed_data['coefficients_2d']
                coeff_array = np.array(coefficients_2d, dtype=float)

                result = {
                    'coefficients_2d': coeff_array.tolist(),
                    'shape': coeff_array.shape,
                    'max_degree_x': coeff_array.shape[0] - 1,
                    'max_degree_y': coeff_array.shape[1] - 1,
                    'operation': 'from_2d_array'
                }
                self.bgf_constructed += 1

            elif operation == 'extract_diagonal':
                coefficients_2d = parsed_data['coefficients_2d']
                coeff_array = np.array(coefficients_2d, dtype=float)

                # Extract diagonal: [x^n y^n]F
                diagonal = np.diag(coeff_array).tolist()

                result = {
                    'diagonal_coefficients': diagonal,
                    'length': len(diagonal),
                    'operation': 'extract_diagonal'
                }
                self.diagonals_extracted += 1

            elif operation == 'coefficient_nm':
                coefficients_2d = parsed_data['coefficients_2d']
                n = parsed_data['n']
                m = parsed_data['m']
                coeff_array = np.array(coefficients_2d, dtype=float)

                # Get [x^n y^m]F
                if n < coeff_array.shape[0] and m < coeff_array.shape[1]:
                    coefficient = float(coeff_array[n, m])
                else:
                    coefficient = 0.0

                result = {
                    'coefficient': coefficient,
                    'n': n,
                    'm': m,
                    'operation': 'coefficient_nm',
                    'notation': f'[x^{n} y^{m}]F'
                }
                self.coefficients_extracted += 1

            elif operation == 'substitute':
                coefficients_2d = parsed_data['coefficients_2d']
                variable = parsed_data['variable']
                value = parsed_data['substitute_value']
                coeff_array = np.array(coefficients_2d, dtype=float)

                if variable == 'x':
                    # F(value, y) - sum along rows with powers of value
                    powers = value ** np.arange(coeff_array.shape[0])
                    result_coeffs = np.sum(coeff_array * powers[:, np.newaxis], axis=0)
                else:  # y
                    # F(x, value) - sum along columns with powers of value
                    powers = value ** np.arange(coeff_array.shape[1])
                    result_coeffs = np.sum(coeff_array * powers, axis=1)

                result = {
                    'coefficients': result_coeffs.tolist(),
                    'variable_substituted': variable,
                    'value': value,
                    'operation': 'substitute',
                    'formula': f'F({value},y)' if variable == 'x' else f'F(x,{value})'
                }
                self.substitutions_performed += 1

            elif operation == 'lattice_paths':
                max_degree = parsed_data['max_degree']

                # Lattice paths: F(x,y) = 1/(1-x-y)
                # Coefficients: C(n+m, n) = number of paths from (0,0) to (n,m)
                coeffs = np.zeros((max_degree + 1, max_degree + 1))
                for n in range(max_degree + 1):
                    for m in range(max_degree + 1):
                        # Binomial coefficient C(n+m, n)
                        from math import comb
                        coeffs[n, m] = comb(n + m, n)

                result = {
                    'coefficients_2d': coeffs.tolist(),
                    'max_degree': max_degree,
                    'operation': 'lattice_paths',
                    'formula': '1/(1-x-y)'
                }
                self.bgf_constructed += 1

            else:
                raise ValueError(f"Unknown BGF operation: {operation}")

            result['method'] = 'bivariate_gf'
            intention.metadata['result'] = result
            self.tasks_succeeded += 1
            intention.advance()

        except Exception as e:
            raise ValueError(f"BGF computation failed: {e}")

    def _execute_verify(self, intention: Intention):
        """Verify result validity."""
        result = intention.metadata.get('result', {})

        if 'coefficients_2d' in result:
            if not isinstance(result['coefficients_2d'], list):
                raise ValueError("2D coefficients must be a list")

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
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'bgf',
                tags=['bivariate_gf', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata=result
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.remove_belief(f'pending_bgf_{task_id}')
        self.add_belief(f'completed_{task_id}', result)

        intention.advance()

    def _handle_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure."""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.ERROR,
                content=f"BGF computation failed: {error_msg}",
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else 'error',
                tags=['error', 'bivariate_gf', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        self.remove_belief(f'pending_bgf_{task_id}')
        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    # ==========================================================================
    # PUBLIC API
    # ==========================================================================

    def process(self, task_entry: Any) -> Dict[str, Any]:
        """
        Synchronous API for BGF operations.

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Result dictionary with BGF coefficients or extracted values
        """
        self.tasks_executed += 1

        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        operation = metadata.get('operation', 'from_2d_array')

        try:
            if operation == 'from_2d_array':
                coefficients_2d = metadata.get('coefficients_2d', [[1]])
                coeff_array = np.array(coefficients_2d, dtype=float)

                result = {
                    'coefficients_2d': coeff_array.tolist(),
                    'shape': coeff_array.shape,
                    'method': 'bivariate_gf'
                }
                self.bgf_constructed += 1

            elif operation == 'extract_diagonal':
                coefficients_2d = metadata.get('coefficients_2d', [[1]])
                coeff_array = np.array(coefficients_2d, dtype=float)
                diagonal = np.diag(coeff_array).tolist()

                result = {
                    'diagonal_coefficients': diagonal,
                    'method': 'diagonal_extraction'
                }
                self.diagonals_extracted += 1

            else:
                raise ValueError(f"Unknown operation: {operation}")

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] process() failed: {e}")
            return {'error': str(e), 'method': 'bivariate_gf'}

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.tasks_succeeded / max(1, self.tasks_executed),
            'bgf_constructed': self.bgf_constructed,
            'diagonals_extracted': self.diagonals_extracted,
            'substitutions_performed': self.substitutions_performed,
            'coefficients_extracted': self.coefficients_extracted,
            'tier': '3',
            'type': 'specialist',
            'domain': 'generating_functions'
        })
        return stats


if __name__ == "__main__":
    """Test Bivariate GF Specialist"""
    print("=" * 80)
    print("BIVARIATE GF SPECIALIST TEST")
    print("=" * 80)
    print()

    specialist = BivariateGFSpecialist()
    print()

    class MockTask:
        def __init__(self, metadata):
            self.metadata = metadata
            self.entry_id = 'test_001'

    # Test 1: Lattice paths
    print("Test 1: Lattice paths F(x,y) = 1/(1-x-y), 3x3")
    task1 = MockTask({'operation': 'lattice_paths', 'max_degree': 3})
    result1 = specialist.process(task1)
    if 'error' not in result1:
        print(f"  Coefficients shape: {np.array(result1.get('coefficients_2d', [])).shape}")
    print()

    # Test 2: Extract diagonal
    print("Test 2: Extract diagonal from 3x3 matrix")
    matrix = [[1, 1, 1], [1, 2, 3], [1, 3, 6]]
    task2 = MockTask({'operation': 'extract_diagonal', 'coefficients_2d': matrix})
    result2 = specialist.process(task2)
    print(f"  Diagonal: {result2.get('diagonal_coefficients', [])}")
    print()

    # Statistics
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))
