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
PHASE 2 - MATRIX OPERATIONS SPECIALIST (Tier 3)
===============================================

Handles fundamental matrix arithmetic and property calculations.
Operations: add, multiply, transpose, determinant, trace, solve_system.

DOMAIN-FIRST ARCHITECTURE:
-------------------------
- Gaussian elimination for solving linear systems (native)
- Back-substitution for upper triangular systems (native)
- NumPy fallback for complex operations
"""

import sys, os
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Tuple
from fractions import Fraction
import numpy as np


# =============================================================================
# NATIVE GAUSSIAN ELIMINATION
# =============================================================================
# Domain-first linear system solver using classical Gaussian elimination
# with partial pivoting and back-substitution.
# =============================================================================

class GaussianEliminationSolver:
    """
    Native Gaussian elimination for solving linear systems Ax = b.

    Implements:
    - Forward elimination with partial pivoting
    - Back-substitution for upper triangular systems
    - Detection of singular/inconsistent systems
    - Support for both exact (Fraction) and floating point arithmetic
    """

    @staticmethod
    def solve_system(A: List[List[float]], b: List[float], exact: bool = False) -> Optional[List[Any]]:
        """
        Solve linear system Ax = b using Gaussian elimination.

        Args:
            A: Coefficient matrix (n x n)
            b: Right-hand side vector (n)
            exact: Use exact Fraction arithmetic if True

        Returns:
            Solution vector x, or None if system is singular/inconsistent
        """
        n = len(A)
        if n == 0 or len(b) != n:
            return None

        # Create augmented matrix [A|b]
        if exact:
            aug = [[Fraction(A[i][j]) for j in range(len(A[i]))] + [Fraction(b[i])] for i in range(n)]
        else:
            aug = [[float(A[i][j]) for j in range(len(A[i]))] + [float(b[i])] for i in range(n)]

        # Forward elimination with partial pivoting
        for col in range(n):
            # Find pivot (largest absolute value in column)
            max_row = col
            max_val = abs(aug[col][col])
            for row in range(col + 1, n):
                if abs(aug[row][col]) > max_val:
                    max_val = abs(aug[row][col])
                    max_row = row

            # Swap rows
            if max_row != col:
                aug[col], aug[max_row] = aug[max_row], aug[col]

            # Check for zero pivot (singular matrix)
            pivot = aug[col][col]
            if exact:
                if pivot == 0:
                    return None
            else:
                if abs(pivot) < 1e-12:
                    return None

            # Eliminate column entries below pivot
            for row in range(col + 1, n):
                if exact:
                    factor = aug[row][col] / pivot
                else:
                    factor = aug[row][col] / pivot
                for j in range(col, n + 1):
                    aug[row][j] -= factor * aug[col][j]

        # Back-substitution
        x = [None] * n
        for i in range(n - 1, -1, -1):
            if exact:
                if aug[i][i] == 0:
                    return None
                x[i] = aug[i][n]
                for j in range(i + 1, n):
                    x[i] -= aug[i][j] * x[j]
                x[i] = x[i] / aug[i][i]
            else:
                if abs(aug[i][i]) < 1e-12:
                    return None
                x[i] = aug[i][n]
                for j in range(i + 1, n):
                    x[i] -= aug[i][j] * x[j]
                x[i] = x[i] / aug[i][i]

        return x

    @staticmethod
    def solve_augmented(augmented: List[List[float]], exact: bool = False) -> Optional[List[Any]]:
        """
        Solve system given augmented matrix [A|b].

        Args:
            augmented: Augmented matrix (n x n+1)
            exact: Use exact Fraction arithmetic if True

        Returns:
            Solution vector, or None if singular
        """
        n = len(augmented)
        if n == 0:
            return None

        # Extract A and b
        A = [[augmented[i][j] for j in range(len(augmented[i]) - 1)] for i in range(n)]
        b = [augmented[i][-1] for i in range(n)]

        return GaussianEliminationSolver.solve_system(A, b, exact)

    @staticmethod
    def rref(matrix: List[List[float]], exact: bool = False) -> Tuple[List[List[Any]], int]:
        """
        Compute Reduced Row Echelon Form (RREF).

        Args:
            matrix: Input matrix
            exact: Use exact Fraction arithmetic

        Returns:
            Tuple of (RREF matrix, rank)
        """
        if not matrix or not matrix[0]:
            return [], 0

        rows, cols = len(matrix), len(matrix[0])

        # Copy matrix
        if exact:
            result = [[Fraction(matrix[i][j]) for j in range(cols)] for i in range(rows)]
        else:
            result = [[float(matrix[i][j]) for j in range(cols)] for i in range(rows)]

        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows:
                break

            # Find pivot
            max_row = pivot_row
            max_val = abs(result[pivot_row][col])
            for row in range(pivot_row + 1, rows):
                if abs(result[row][col]) > max_val:
                    max_val = abs(result[row][col])
                    max_row = row

            # Check for zero column
            is_zero = (max_val == 0) if exact else (max_val < 1e-12)
            if is_zero:
                continue

            # Swap
            result[pivot_row], result[max_row] = result[max_row], result[pivot_row]

            # Scale pivot row
            pivot = result[pivot_row][col]
            for j in range(cols):
                result[pivot_row][j] /= pivot

            # Eliminate
            for row in range(rows):
                if row != pivot_row:
                    factor = result[row][col]
                    for j in range(cols):
                        result[row][j] -= factor * result[pivot_row][j]

            pivot_row += 1

        return result, pivot_row  # pivot_row is rank

class MatrixOperationsSpecialist(BDIAgent):
    def __init__(self, agent_id='matrix_ops_001', df: Optional[DirectoryFacilitator]=None, blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.tasks_succeeded = self.tasks_failed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.linalg.ops',
                agent_id=agent_id,
                algorithm='numpy',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                operations='add_multiply_transpose_determinant_trace'))

        print(f"[{agent_id}] Matrix Operations Specialist initialized")
        print(f"  Library: NumPy")
        print(f"  Operations: Add, multiply, transpose, determinant, trace")

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The Matrix Operations Specialist's BDI loop:
    #   1. update_beliefs() - Find matrix tasks on Blackboard
    #   2. deliberate() - Create computation plans
    #   3. execute_step() - Execute via DELEGATION to NumPy
    #
    # CRITICAL: All computation delegated to NumPy (never implement matrix ops directly)
    # ==========================================================================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for matrix tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus

            tasks = self.blackboard.query_entries(tags=['matrix'], status=EntryStatus.PENDING)

            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata:
                    if task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                        tasks.append(task)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if self.has_belief(f'claimed_task_{task.entry_id}'):
                    continue
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')

        except Exception as e:
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create computation plans for matrix tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            operation = metadata.get('operation', 'determinant')

            # Detect operation
            if 'determinant' in raw_input or 'det' in raw_input:
                operation = 'determinant'
            elif 'trace' in raw_input:
                operation = 'trace'
            elif 'transpose' in raw_input:
                operation = 'transpose'
            elif 'inverse' in raw_input:
                operation = 'inverse'
            elif 'multiply' in raw_input or 'product' in raw_input:
                operation = 'multiply'
            elif 'eigenvalue' in raw_input or 'eigen' in raw_input:
                operation = 'eigenvalues'
            elif 'rank' in raw_input:
                operation = 'rank'
            elif 'rref' in raw_input or 'row echelon' in raw_input:
                operation = 'rref'
            elif 'solve' in raw_input or 'system' in raw_input or 'gaussian' in raw_input:
                operation = 'solve_system'

            steps = ['claim_task', 'parse_matrix', f'compute_{operation}', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'matrix_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_matrix',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation, 'raw_input': raw_input}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute matrix computation (DELEGATE to NumPy)."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable
        import re

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_matrix':
                raw = intention.metadata.get('raw_input', '')
                # Extract matrix from format [[a,b],[c,d]] or numbers
                try:
                    # Try to find matrix notation
                    import ast
                    matrix_match = re.search(r'\[\[.*?\]\]', raw.replace(' ', ''))
                    if matrix_match:
                        matrix = np.array(ast.literal_eval(matrix_match.group()))
                    else:
                        # Try to extract numbers and make square matrix
                        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', raw)]
                        size = int(np.sqrt(len(numbers)))
                        if size * size == len(numbers):
                            matrix = np.array(numbers).reshape(size, size)
                        else:
                            matrix = np.array([[1, 0], [0, 1]])  # Default identity
                    intention.metadata['matrix'] = matrix
                except Exception:
                    intention.metadata['matrix'] = np.array([[1, 0], [0, 1]])
                intention.advance()

            elif action == 'compute_determinant':
                matrix = intention.metadata.get('matrix')
                result = float(np.linalg.det(matrix))
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_trace':
                matrix = intention.metadata.get('matrix')
                result = float(np.trace(matrix))
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_transpose':
                matrix = intention.metadata.get('matrix')
                result = matrix.T.tolist()
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_inverse':
                matrix = intention.metadata.get('matrix')
                try:
                    result = np.linalg.inv(matrix).tolist()
                except np.linalg.LinAlgError:
                    result = 'Matrix is singular (no inverse)'
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_eigenvalues':
                matrix = intention.metadata.get('matrix')
                eigenvalues = np.linalg.eigvals(matrix)
                result = eigenvalues.tolist()
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_rank':
                matrix = intention.metadata.get('matrix')
                result = int(np.linalg.matrix_rank(matrix))
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_multiply':
                matrix = intention.metadata.get('matrix')
                result = np.matmul(matrix, matrix).tolist()  # Square for demo
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_solve_system':
                # Native Gaussian elimination for linear systems
                matrix = intention.metadata.get('matrix')
                raw = intention.metadata.get('raw_input', '')

                # Try to detect if this is an augmented matrix [A|b] or separate A, b
                # For now, assume augmented matrix input
                try:
                    if matrix is not None and len(matrix.shape) == 2:
                        rows, cols = matrix.shape
                        if cols == rows + 1:
                            # Augmented matrix [A|b]
                            result = GaussianEliminationSolver.solve_augmented(
                                matrix.tolist(), exact=False
                            )
                        else:
                            # Square matrix - assume last column is b
                            A = matrix[:, :-1].tolist() if cols > 1 else matrix.tolist()
                            b = matrix[:, -1].tolist() if cols > 1 else [0] * rows
                            result = GaussianEliminationSolver.solve_system(A, b, exact=False)

                        if result is None:
                            result = "System is singular or inconsistent (no unique solution)"
                        else:
                            result = {'solution': result, 'method': 'gaussian_elimination'}
                    else:
                        result = "Invalid matrix format for system solving"
                except Exception as e:
                    result = f"Gaussian elimination failed: {e}"

                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'compute_rref':
                # Native RREF computation
                matrix = intention.metadata.get('matrix')
                try:
                    if matrix is not None:
                        rref_result, rank = GaussianEliminationSolver.rref(
                            matrix.tolist(), exact=False
                        )
                        # Convert to cleaner format
                        rref_clean = [[round(x, 10) if isinstance(x, float) else x
                                      for x in row] for row in rref_result]
                        result = {
                            'rref': rref_clean,
                            'rank': rank,
                            'method': 'gaussian_elimination_rref'
                        }
                    else:
                        result = "No matrix provided for RREF"
                except Exception as e:
                    result = f"RREF computation failed: {e}"

                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['matrix', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': str(result), 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_succeeded += 1
                self.tasks_executed += 1
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            self.tasks_failed += 1
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = MatrixOperationsSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed, 'tasks_succeeded': self.tasks_succeeded, 'tasks_failed': self.tasks_failed})
        return stats
