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
GeodesicSpecialist - Geodesic Computations
===========================================

Provides comprehensive geodesic and exponential map operations:
- Solve geodesic equations via RK4 integration
- Exponential map exp_p(v)
- Riemann normal coordinates
- Parallel transport along curves
- Geodesic completeness checks

NO SYMPY - Pure Python/NumPy implementation.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


@dataclass
class GeodesicResult:
    """Result from geodesic computation."""
    path: np.ndarray  # N × dim array of points
    velocities: np.ndarray  # N × dim array of velocities
    parameter_values: np.ndarray  # Parameter values (time)
    length: float = 0.0
    is_closed: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelTransportResult:
    """Result from parallel transport."""
    transported_vector: np.ndarray
    path: np.ndarray
    details: Dict[str, Any] = field(default_factory=dict)


class GeodesicSpecialist(BDIAgent):
    """
    BDI Agent for geodesic computations on Riemannian manifolds.

    Capabilities:
    - Solve geodesic equations d²x/dt² + Γ(dx/dt, dx/dt) = 0
    - Compute exponential map exp_p(v)
    - Riemann normal coordinates
    - Parallel transport along curves
    - Check geodesic completeness
    """

    def __init__(self, agent_id='geodesic_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_computations: List[str] = []
        self._epsilon = 1e-10
        self._h = 1e-6  # Numerical derivative step

        # Import curvature specialist for Christoffel symbols
        self._curvature_specialist = None

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.riemannian.geodesic',
                agent_id=self.agent_id,
                algorithm='geodesic',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for geodesic computations.

        Supported operations:
        - solve_geodesic: Integrate geodesic equation
        - exponential_map: Compute exp_p(v)
        - normal_coordinates: Riemann normal coordinates
        - parallel_transport: Transport vector along curve
        - check_completeness: Geodesic completeness
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        operation = metadata.get('operation', 'solve_geodesic')
        self.recent_computations.append(operation)

        if len(self.recent_computations) > 100:
            self.recent_computations = self.recent_computations[-100:]

        try:
            if operation == 'solve_geodesic':
                return self._handle_solve_geodesic(metadata)
            elif operation == 'exponential_map':
                return self._handle_exponential_map(metadata)
            elif operation == 'normal_coordinates':
                return self._handle_normal_coordinates(metadata)
            elif operation == 'parallel_transport':
                return self._handle_parallel_transport(metadata)
            elif operation == 'check_completeness':
                return self._handle_check_completeness(metadata)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}',
                    'supported_operations': [
                        'solve_geodesic', 'exponential_map', 'normal_coordinates',
                        'parallel_transport', 'check_completeness'
                    ]
                }
        except Exception as e:
            return {'success': False, 'error': str(e), 'operation': operation}

    def _handle_solve_geodesic(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle geodesic solving."""
        metric_fn = task_entry.get('metric_function')
        initial_position = np.array(task_entry.get('initial_position'))
        initial_velocity = np.array(task_entry.get('initial_velocity'))
        t_max = task_entry.get('t_max', 1.0)
        n_steps = task_entry.get('n_steps', 1000)

        result = self.solve_geodesic_equation(
            metric_fn, initial_position, initial_velocity, t_max, n_steps
        )

        return {
            'success': True,
            'operation': 'solve_geodesic',
            'path': result.path.tolist(),
            'velocities': result.velocities.tolist(),
            'length': float(result.length),
            'is_closed': result.is_closed,
            'details': result.details
        }

    def _handle_exponential_map(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exponential map computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point'))
        tangent_vector = np.array(task_entry.get('tangent_vector'))

        endpoint = self.compute_exponential_map(metric_fn, point, tangent_vector)

        return {
            'success': True,
            'operation': 'exponential_map',
            'base_point': point.tolist(),
            'tangent_vector': tangent_vector.tolist(),
            'endpoint': endpoint.tolist()
        }

    def _handle_normal_coordinates(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle normal coordinates computation."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point'))

        coords_info = self.compute_normal_coordinates(metric_fn, point)

        return {
            'success': True,
            'operation': 'normal_coordinates',
            **coords_info
        }

    def _handle_parallel_transport(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parallel transport."""
        metric_fn = task_entry.get('metric_function')
        initial_vector = np.array(task_entry.get('initial_vector'))
        curve = np.array(task_entry.get('curve'))  # N × dim array

        result = self.compute_parallel_transport(metric_fn, curve, initial_vector)

        return {
            'success': True,
            'operation': 'parallel_transport',
            'transported_vector': result.transported_vector.tolist(),
            'details': result.details
        }

    def _handle_check_completeness(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Handle geodesic completeness check."""
        metric_fn = task_entry.get('metric_function')
        point = np.array(task_entry.get('point', [0, 0]))
        samples = task_entry.get('samples', 10)

        is_complete, details = self.check_geodesic_completeness(metric_fn, point, samples)

        return {
            'success': True,
            'operation': 'check_completeness',
            'is_complete': is_complete,
            'details': details
        }

    # ========== Core Computational Methods ==========

    def _compute_christoffel(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> np.ndarray:
        """
        Compute Christoffel symbols.

        Γ^k_ij = (1/2) g^{kl} (∂_i g_jl + ∂_j g_il - ∂_l g_ij)
        """
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

    def geodesic_acceleration(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        position: np.ndarray,
        velocity: np.ndarray
    ) -> np.ndarray:
        """
        Compute geodesic acceleration.

        d²x^k/dt² = -Γ^k_ij (dx^i/dt)(dx^j/dt)

        Args:
            metric_fn: Metric function
            position: Current position
            velocity: Current velocity

        Returns:
            Acceleration vector
        """
        gamma = self._compute_christoffel(metric_fn, position)
        n = len(position)

        acceleration = np.zeros(n)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    acceleration[k] -= gamma[k, i, j] * velocity[i] * velocity[j]

        return acceleration

    def solve_geodesic_equation(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        x0: np.ndarray,
        v0: np.ndarray,
        t_max: float = 1.0,
        n_steps: int = 1000
    ) -> GeodesicResult:
        """
        Solve geodesic equation via RK4 integration.

        d²x/dt² + Γ(dx/dt, dx/dt) = 0

        Args:
            metric_fn: Metric function
            x0: Initial position
            v0: Initial velocity
            t_max: Maximum parameter value
            n_steps: Number of integration steps

        Returns:
            GeodesicResult with path and velocities
        """
        n = len(x0)
        dt = t_max / n_steps

        x = x0.copy()
        v = v0.copy()

        path = [x.copy()]
        velocities = [v.copy()]
        t_values = [0]

        for step in range(n_steps):
            # RK4 integration for coupled system
            # State: (x, v), derivatives: (v, a)

            # k1
            k1_x = v
            k1_v = self.geodesic_acceleration(metric_fn, x, v)

            # k2
            x2 = x + 0.5 * dt * k1_x
            v2 = v + 0.5 * dt * k1_v
            k2_x = v2
            k2_v = self.geodesic_acceleration(metric_fn, x2, v2)

            # k3
            x3 = x + 0.5 * dt * k2_x
            v3 = v + 0.5 * dt * k2_v
            k3_x = v3
            k3_v = self.geodesic_acceleration(metric_fn, x3, v3)

            # k4
            x4 = x + dt * k3_x
            v4 = v + dt * k3_v
            k4_x = v4
            k4_v = self.geodesic_acceleration(metric_fn, x4, v4)

            # Update
            x = x + (dt / 6) * (k1_x + 2*k2_x + 2*k3_x + k4_x)
            v = v + (dt / 6) * (k1_v + 2*k2_v + 2*k3_v + k4_v)

            path.append(x.copy())
            velocities.append(v.copy())
            t_values.append((step + 1) * dt)

        path = np.array(path)
        velocities = np.array(velocities)
        t_values = np.array(t_values)

        # Compute arc length
        length = self._compute_arc_length(metric_fn, path)

        # Check if closed
        is_closed = np.linalg.norm(path[-1] - path[0]) < 0.01

        return GeodesicResult(
            path=path,
            velocities=velocities,
            parameter_values=t_values,
            length=float(length),
            is_closed=is_closed,
            details={
                'initial_position': x0.tolist(),
                'initial_velocity': v0.tolist(),
                't_max': t_max,
                'n_steps': n_steps
            }
        )

    def compute_exponential_map(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        tangent_vector: np.ndarray,
        t: float = 1.0
    ) -> np.ndarray:
        """
        Compute exponential map exp_p(v).

        Flows along geodesic starting at p with velocity v for time t.

        Args:
            metric_fn: Metric function
            point: Base point p
            tangent_vector: Tangent vector v ∈ T_p M
            t: Time parameter (default 1.0)

        Returns:
            Endpoint exp_p(t·v)
        """
        result = self.solve_geodesic_equation(
            metric_fn, point, tangent_vector, t_max=t, n_steps=100
        )

        return result.path[-1]

    def compute_normal_coordinates(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray
    ) -> Dict[str, Any]:
        """
        Compute Riemann normal coordinates centered at point.

        In normal coordinates, the metric is δ_ij + O(r²).

        Args:
            metric_fn: Metric function
            point: Center point

        Returns:
            Dictionary with normal coordinate properties
        """
        g = metric_fn(point)
        n = g.shape[0]

        # At the center, metric should be approximately identity
        metric_deviation = np.linalg.norm(g - np.eye(n), ord='fro')

        # Christoffel symbols should vanish at center
        gamma = self._compute_christoffel(metric_fn, point)
        christoffel_norm = np.linalg.norm(gamma)

        # Test exponential map on standard basis
        basis_vectors = []
        exp_map_points = []

        for i in range(n):
            e_i = np.zeros(n)
            e_i[i] = 0.1  # Small radius
            exp_point = self.compute_exponential_map(metric_fn, point, e_i)
            basis_vectors.append(e_i.tolist())
            exp_map_points.append(exp_point.tolist())

        return {
            'center_point': point.tolist(),
            'metric_at_center': g.tolist(),
            'metric_deviation_from_identity': float(metric_deviation),
            'christoffel_norm': float(christoffel_norm),
            'basis_exponential_map': {
                'basis_vectors': basis_vectors,
                'exp_map_points': exp_map_points
            }
        }

    def compute_parallel_transport(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        curve: np.ndarray,
        initial_vector: np.ndarray
    ) -> ParallelTransportResult:
        """
        Parallel transport vector along curve.

        Solves: DV/dt = 0, i.e., dV^i/dt + Γ^i_jk V^j (dx^k/dt) = 0

        Args:
            metric_fn: Metric function
            curve: Path as N × dim array
            initial_vector: Vector at curve[0]

        Returns:
            ParallelTransportResult with transported vector
        """
        V = initial_vector.copy()
        n = len(V)

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

            V = V + dV

        return ParallelTransportResult(
            transported_vector=V,
            path=curve,
            details={
                'initial_vector': initial_vector.tolist(),
                'curve_length': len(curve)
            }
        )

    def check_geodesic_completeness(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        point: np.ndarray,
        num_samples: int = 10
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if geodesics are complete (heuristic test).

        Shoots geodesics in random directions and checks for blow-up.

        Args:
            metric_fn: Metric function
            point: Starting point
            num_samples: Number of random directions to test

        Returns:
            (is_complete, details)
        """
        n = len(point)
        incomplete_count = 0
        test_results = []

        for _ in range(num_samples):
            # Random initial velocity
            v0 = np.random.randn(n)
            v0 = v0 / np.linalg.norm(v0)  # Unit vector

            try:
                result = self.solve_geodesic_equation(
                    metric_fn, point, v0, t_max=10.0, n_steps=1000
                )

                # Check for numerical blow-up
                path_norms = np.linalg.norm(result.path, axis=1)
                max_norm = np.max(path_norms)

                if max_norm > 1e6 or np.any(np.isnan(result.path)):
                    incomplete_count += 1
                    test_results.append({'direction': v0.tolist(), 'status': 'incomplete'})
                else:
                    test_results.append({'direction': v0.tolist(), 'status': 'complete'})

            except Exception as e:
                incomplete_count += 1
                test_results.append({'direction': v0.tolist(), 'status': 'error', 'error': str(e)})

        is_complete = (incomplete_count == 0)

        return is_complete, {
            'tested_directions': num_samples,
            'incomplete_count': incomplete_count,
            'completeness_ratio': (num_samples - incomplete_count) / num_samples,
            'sample_results': test_results[:5]  # Return first 5 samples
        }

    def _compute_arc_length(
        self,
        metric_fn: Callable[[np.ndarray], np.ndarray],
        path: np.ndarray
    ) -> float:
        """
        Compute arc length of path using metric.

        L = ∫ sqrt(g_ij dx^i dx^j)
        """
        length = 0.0

        for i in range(len(path) - 1):
            x = path[i]
            dx = path[i + 1] - path[i]

            g = metric_fn(x)
            ds_squared = dx @ g @ dx

            if ds_squared > 0:
                length += np.sqrt(ds_squared)

        return length

    # ========== BDI Methods ==========

    def update_beliefs(self) -> None:
        """Update agent beliefs."""
        if hasattr(self, 'blackboard') and self.blackboard:
            self.blackboard.write(
                f'geodesic_specialist_stats_{self.agent_id}',
                {
                    'tasks_executed': self.tasks_executed,
                    'recent_operations': self.recent_computations[-10:]
                }
            )

    def deliberate(self) -> List[Intention]:
        """Determine intentions."""
        intentions = []

        # Adaptive step size optimization
        if self.tasks_executed > 50 and self.tasks_executed % 25 == 0:
            intentions.append(Intention(
                action='optimize_integration',
                priority=2,
                params={'tasks_completed': self.tasks_executed}
            ))

        return intentions

    def execute_step(self, intention: Intention) -> None:
        """Execute BDI intention."""
        if intention.action == 'optimize_integration':
            # Could implement adaptive step size here
            if hasattr(self, 'blackboard') and self.blackboard:
                self.blackboard.write(
                    f'geodesic_optimization_{self.agent_id}',
                    {'timestamp': intention.params.get('tasks_completed')}
                )

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'recent_operations': self.recent_computations[-5:]
        }
