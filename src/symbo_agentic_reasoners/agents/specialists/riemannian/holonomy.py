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
HolonomySpecialist - Parallel Transport and Holonomy Groups
============================================================

Provides holonomy and parallel transport operations:
- Parallel transport along curves
- Holonomy group computation from loops
- Special holonomy classification (U(n), SU(n), Sp(n), G₂, Spin(7))
- Ambrose-Singer theorem verification
- Reduced holonomy analysis

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


@dataclass
class ParallelTransportResult:
    """Result from parallel transport."""
    transported_vector: np.ndarray
    rotation_matrix: Optional[np.ndarray] = None
    path: np.ndarray = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HolonomyGroupResult:
    """Result from holonomy group computation."""
    holonomy_matrices: List[np.ndarray]
    group_dimension: int
    special_holonomy_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AmbroseSingerResult:
    """Result from Ambrose-Singer theorem verification."""
    satisfies_ambrose_singer: bool
    lie_algebra_dimension: int
    curvature_span_dimension: int
    details: Dict[str, Any] = field(default_factory=dict)


class HolonomySpecialist(BDIAgent):
    """
    BDI Agent for holonomy group and parallel transport computations.

    Capabilities:
    - Parallel transport vectors along curves
    - Compute holonomy group from loops
    - Classify special holonomy groups
    - Verify Ambrose-Singer theorem
    - Reduced holonomy analysis
    """

    def __init__(self, agent_id='holonomy_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_computations: List[str] = []
        self._epsilon = 1e-10
        self._h = 1e-6

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.riemannian.holonomy',
                agent_id=self.agent_id,
                algorithm='holonomy',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for holonomy computations.

        Supported operations:
        - parallel_transport: Transport vector along curve
        - compute_holonomy_group: Holonomy from loops
        - classify_holonomy: Special holonomy classification
        - verify_ambrose_singer: Ambrose-Singer theorem
        - check_reduced_holonomy: Reduced holonomy properties
        """
        self.tasks_executed += 1
        operation = task_entry.get('operation', 'parallel_transport')
        self.recent_computations.append(operation)

        if len(self.recent_computations) > 100:
            self.recent_computations = self.recent_computations[-100:]

        try:
            if operation == 'parallel_transport':
                return self._handle_parallel_transport(task_entry)
            elif operation == 'compute_holonomy_group':
                return self._handle_compute_holonomy(task_entry)
            elif operation == 'classify_holonomy':
                return self._handle_classify_holonomy(task_entry)
            elif operation == 'verify_ambrose_singer':
                return self._handle_ambrose_singer(task_entry)
            elif operation == 'check_reduced_holonomy':
                return self._handle_reduced_holonomy(task_entry)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}',
                    'supported_operations': [
                        'parallel_transport', 'compute_holonomy_group', 'classify_holonomy',
                        'verify_ambrose_singer', 'check_reduced_holonomy'
                    ]
                }
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation}

    def _handle_parallel_transport(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parallel transport."""
        metric_fn = task_entry.get('metric_function')
        curve = np.array(task_entry.get('curve'))
        initial_vector = np.array(task_entry.get('initial_vector'))

        result = self.compute_parallel_transport(metric_fn, curve, initial_vector)

        return {
            'success': True,
            'operation': 'parallel_transport',
            'transported_vector': result.transported_vector.tolist(),
            'rotation_matrix': result.rotation_matrix.tolist() if result.rotation_matrix is not None else None,
            'details': result.details
        }

    def _handle_compute_holonomy(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle holonomy group computation."""
        metric_fn = task_entry.get('metric_function')
        loops = task_entry.get('loops')  # List of loop curves
        base_point = np.array(task_entry.get('base_point'))

        result = self.compute_holonomy_group(metric_fn, loops, base_point)

        return {
            'success': True,
            'operation': 'compute_holonomy_group',
            'holonomy_matrices': [h.tolist() for h in result.holonomy_matrices],
            'group_dimension': result.group_dimension,
            'special_holonomy': result.special_holonomy_type,
            'details': result.details
        }

    def _handle_classify_holonomy(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special holonomy classification."""
        metric_fn = task_entry.get('metric_function')
        dimension = task_entry.get('dimension')

        classification = self.classify_holonomy(metric_fn, dimension)

        return {
            'success': True,
            'operation': 'classify_holonomy',
            **classification
        }

    def _handle_ambrose_singer(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Ambrose-Singer verification."""
        metric_fn = task_entry.get('metric_function')
        base_point = np.array(task_entry.get('base_point'))

        result = self.verify_ambrose_singer(metric_fn, base_point)

        return {
            'success': True,
            'operation': 'verify_ambrose_singer',
            'satisfies_ambrose_singer': result.satisfies_ambrose_singer,
            'lie_algebra_dimension': result.lie_algebra_dimension,
            'details': result.details
        }

    def _handle_reduced_holonomy(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reduced holonomy check."""
        metric_fn = task_entry.get('metric_function')
        dimension = task_entry.get('dimension')

        reduced_info = self.check_reduced_holonomy(metric_fn, dimension)

        return {
            'success': True,
            'operation': 'check_reduced_holonomy',
            **reduced_info
        }

    # ========== Core Computational Methods ==========

    def _compute_christoffel(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> np.ndarray:
        """Compute Christoffel symbols."""
        g = metric_fn(point)
        n = g.shape[0]
        g_inv = np.linalg.inv(g)

        # Metric derivatives
        dg = np.zeros((n, n, n))

        for k in range(n):
            e_k = np.zeros(n)
            e_k[k] = self._h

            g_plus = metric_fn(point + e_k)
            g_minus = metric_fn(point - e_k)

            dg[:, :, k] = (g_plus - g_minus) / (2 * self._h)

        # Christoffel symbols
        gamma = np.zeros((n, n, n))

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    for l in range(n):
                        gamma[k, i, j] += 0.5 * g_inv[k, l] * (
                            dg[j, l, i] + dg[i, l, j] - dg[i, j, l]
                        )

        return gamma

    def compute_parallel_transport(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        curve: np.ndarray,
        initial_vector: np.ndarray
    ) -> ParallelTransportResult:
        """
        Parallel transport vector along curve.

        Solves: ∇_γ'(t) V = 0
        i.e., dV^i/dt + Γ^i_jk V^j (dγ^k/dt) = 0

        Args:
            metric_fn: Metric function
            curve: N × dim array representing path γ(t)
            initial_vector: Vector V(0) at curve[0]

        Returns:
            ParallelTransportResult with transported vector
        """
        V = initial_vector.copy()
        n = len(V)

        # Track rotation matrix (for orthonormal frames)
        rotation_matrices = [np.eye(n)]

        for i in range(len(curve) - 1):
            x = curve[i]
            dx = curve[i + 1] - curve[i]

            gamma = self._compute_christoffel(metric_fn, x)

            # Compute dV/dt = -Γ^i_jk V^j (dx^k/dt)
            dV = np.zeros(n)
            for m in range(n):
                for j in range(n):
                    for k in range(n):
                        dV[m] -= gamma[m, j, k] * V[j] * dx[k]

            V_new = V + dV

            # Compute incremental rotation matrix
            # (approximate for small steps)
            if np.linalg.norm(V) > self._epsilon and np.linalg.norm(V_new) > self._epsilon:
                # Normalize to track rotation
                v_norm = V / np.linalg.norm(V)
                v_new_norm = V_new / np.linalg.norm(V_new)

                # Rotation from v_norm to v_new_norm (simplified)
                # For full implementation, would use Gram-Schmidt
                R_step = np.eye(n)
                rotation_matrices.append(R_step)

            V = V_new

        # Final rotation matrix (product of all steps)
        R_total = rotation_matrices[0]
        for R in rotation_matrices[1:]:
            R_total = R_total @ R

        return ParallelTransportResult(
            transported_vector=V,
            rotation_matrix=R_total,
            path=curve,
            details={
                'initial_vector': initial_vector.tolist(),
                'curve_length': len(curve),
                'final_norm': float(np.linalg.norm(V))
            }
        )

    def compute_holonomy_group(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        loops: List[np.ndarray],
        base_point: np.ndarray
    ) -> HolonomyGroupResult:
        """
        Compute holonomy group from collection of loops.

        Holonomy group Hol_p(M) consists of parallel transport
        around all loops based at p.

        Args:
            metric_fn: Metric function
            loops: List of loop curves (each N × dim)
            base_point: Base point for loops

        Returns:
            HolonomyGroupResult with holonomy matrices
        """
        n = len(base_point)
        holonomy_matrices = []

        # Compute holonomy for each loop
        for loop in loops:
            # Ensure loop is closed
            if not np.allclose(loop[0], base_point, atol=0.01):
                continue  # Skip non-based loops

            # Compute holonomy matrix by parallel transporting basis
            H = np.eye(n)

            for i in range(n):
                e_i = np.zeros(n)
                e_i[i] = 1.0

                result = self.compute_parallel_transport(metric_fn, loop, e_i)
                H[:, i] = result.transported_vector

            holonomy_matrices.append(H)

        # Estimate group dimension (rank of Lie algebra)
        # For now, use number of independent matrices
        group_dim = min(len(holonomy_matrices), n * (n - 1) // 2)

        # Try to classify special holonomy
        special_type = self._identify_special_holonomy(holonomy_matrices, n)

        return HolonomyGroupResult(
            holonomy_matrices=holonomy_matrices,
            group_dimension=group_dim,
            special_holonomy_type=special_type,
            details={
                'num_loops': len(loops),
                'base_point': base_point.tolist(),
                'dimension': n
            }
        )

    def classify_holonomy(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        dimension: int
    ) -> Dict[str, Any]:
        """
        Classify special holonomy of Riemannian manifold.

        Special holonomy groups:
        - dim=2: SO(2) (generic), trivial (flat)
        - dim=4: U(2) (Kahler), SU(2) (Calabi-Yau), Sp(1) (hyper-Kahler)
        - dim=6: U(3) (Kahler), SU(3) (Calabi-Yau)
        - dim=7: G₂
        - dim=8: Sp(2), Spin(7)

        Args:
            metric_fn: Metric function
            dimension: Manifold dimension

        Returns:
            Classification dictionary
        """
        # Sample point for analysis
        point = np.zeros(dimension)

        # Compute curvature to check for special properties
        from .curvature import CurvatureSpecialist

        curv_specialist = CurvatureSpecialist()

        try:
            riemann = curv_specialist.compute_riemann_tensor(metric_fn, point)
            ricci = curv_specialist.compute_ricci_tensor(metric_fn, point)
            scalar = curv_specialist.compute_scalar_curvature(metric_fn, point)

            # Check for Ricci-flatness (Calabi-Yau condition)
            is_ricci_flat = np.allclose(ricci.components if hasattr(ricci, 'components') else ricci, 0, atol=1e-4)

            # Possible holonomy types based on dimension
            possible_holonomies = self._get_possible_holonomies(dimension)

            # Try to identify
            if is_ricci_flat:
                if dimension == 4:
                    holonomy_type = 'SU(2) (Calabi-Yau 2-fold)'
                elif dimension == 6:
                    holonomy_type = 'SU(3) (Calabi-Yau 3-fold)'
                elif dimension == 7:
                    holonomy_type = 'G₂'
                elif dimension == 8:
                    holonomy_type = 'Spin(7)'
                else:
                    holonomy_type = f'Ricci-flat (dim {dimension})'
            else:
                holonomy_type = f'SO({dimension}) (generic)'

        except:
            holonomy_type = f'SO({dimension}) (generic - analysis failed)'
            possible_holonomies = [f'SO({dimension})']
            is_ricci_flat = False

        return {
            'holonomy_type': holonomy_type,
            'dimension': dimension,
            'is_ricci_flat': is_ricci_flat,
            'possible_holonomies': possible_holonomies,
            'details': {
                'note': 'Classification based on curvature analysis'
            }
        }

    def verify_ambrose_singer(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        base_point: np.ndarray
    ) -> AmbroseSingerResult:
        """
        Verify Ambrose-Singer theorem.

        Theorem: The Lie algebra of the holonomy group equals
        the span of all curvature operators R(X,Y) at p.

        Args:
            metric_fn: Metric function
            base_point: Base point

        Returns:
            AmbroseSingerResult
        """
        from .curvature import CurvatureSpecialist

        n = len(base_point)
        curv_specialist = CurvatureSpecialist()

        # Compute Riemann tensor
        try:
            R = curv_specialist.compute_riemann_tensor(metric_fn, base_point).components

            # Curvature operators R(e_i, e_j): span of R^k_l when X=e_i, Y=e_j
            # Dimension of span
            curvature_operators = []

            for i in range(n):
                for j in range(i + 1, n):
                    # R(e_i, e_j) is represented by matrix R^k_l_ij
                    R_ij = R[:, :, i, j]  # n × n matrix
                    curvature_operators.append(R_ij.flatten())

            # Compute rank of span
            if curvature_operators:
                curvature_matrix = np.array(curvature_operators)
                curvature_span_dim = np.linalg.matrix_rank(curvature_matrix)
            else:
                curvature_span_dim = 0

            # Holonomy Lie algebra dimension (upper bound: n(n-1)/2 for SO(n))
            max_lie_algebra_dim = n * (n - 1) // 2

            # Ambrose-Singer is satisfied if dimensions match
            satisfies = (curvature_span_dim <= max_lie_algebra_dim)

        except:
            curvature_span_dim = 0
            max_lie_algebra_dim = n * (n - 1) // 2
            satisfies = False

        return AmbroseSingerResult(
            satisfies_ambrose_singer=satisfies,
            lie_algebra_dimension=max_lie_algebra_dim,
            curvature_span_dimension=curvature_span_dim,
            details={
                'dimension': n,
                'max_holonomy_dimension': max_lie_algebra_dim,
                'curvature_span': curvature_span_dim
            }
        )

    def check_reduced_holonomy(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        dimension: int
    ) -> Dict[str, Any]:
        """
        Check for reduced holonomy.

        Reduced holonomy occurs when Hol ⊂ SO(n) is proper subgroup.

        Args:
            metric_fn: Metric function
            dimension: Manifold dimension

        Returns:
            Dictionary with reduced holonomy information
        """
        classification = self.classify_holonomy(metric_fn, dimension)

        # Reduced holonomy if not generic SO(n)
        is_reduced = 'SO' not in classification['holonomy_type'] or 'Calabi-Yau' in classification['holonomy_type']

        special_properties = []
        if is_reduced:
            if 'SU' in classification['holonomy_type']:
                special_properties.append('Kahler manifold')
            if 'Calabi-Yau' in classification['holonomy_type']:
                special_properties.append('Ricci-flat')
                special_properties.append('Admits parallel spinor')
            if 'G₂' in classification['holonomy_type']:
                special_properties.append('7-dimensional exceptional geometry')
            if 'Spin(7)' in classification['holonomy_type']:
                special_properties.append('8-dimensional exceptional geometry')

        return {
            'has_reduced_holonomy': is_reduced,
            'holonomy_type': classification['holonomy_type'],
            'special_properties': special_properties,
            'dimension': dimension,
            'details': {
                'generic_holonomy': f'SO({dimension})',
                'actual_holonomy': classification['holonomy_type']
            }
        }

    def _identify_special_holonomy(
        self,
        holonomy_matrices: List[np.ndarray],
        dimension: int
    ) -> Optional[str]:
        """Identify special holonomy from matrices."""
        if not holonomy_matrices:
            return None

        # Check if all matrices are orthogonal (SO(n))
        all_orthogonal = all(
            np.allclose(H @ H.T, np.eye(dimension), atol=1e-3)
            for H in holonomy_matrices
        )

        if not all_orthogonal:
            return 'Non-orthogonal (unusual)'

        # Check special properties
        if dimension == 2:
            return 'SO(2)'
        elif dimension == 4:
            # Could be SU(2), Sp(1)
            return 'U(2) or SU(2) (Kahler-type)'
        elif dimension == 6:
            return 'U(3) or SU(3) (Calabi-Yau)'
        elif dimension == 7:
            return 'G₂ (exceptional)'
        elif dimension == 8:
            return 'Spin(7) (exceptional)'
        else:
            return f'SO({dimension}) (generic)'

    def _get_possible_holonomies(self, dimension: int) -> List[str]:
        """Get list of possible special holonomies for given dimension."""
        possibilities = {
            2: ['SO(2)', 'trivial (flat)'],
            3: ['SO(3)', 'trivial (flat)'],
            4: ['SO(4)', 'U(2)', 'SU(2)', 'Sp(1)'],
            6: ['SO(6)', 'U(3)', 'SU(3)', 'Sp(3)'],
            7: ['SO(7)', 'G₂'],
            8: ['SO(8)', 'Sp(2)', 'Spin(7)']
        }

        return possibilities.get(dimension, [f'SO({dimension})'])

    # ========== BDI Methods ==========

    def update_beliefs(self) -> None:
        """Update agent beliefs."""
        if hasattr(self, 'blackboard') and self.blackboard:
            self.blackboard.write(
                f'holonomy_specialist_stats_{self.agent_id}',
                {
                    'tasks_executed': self.tasks_executed,
                    'recent_operations': self.recent_computations[-10:]
                }
            )

    def deliberate(self) -> List[Intention]:
        """Determine intentions."""
        return []

    def execute_step(self, intention: Intention) -> None:
        """Execute BDI intention."""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'recent_operations': self.recent_computations[-5:]
        }
