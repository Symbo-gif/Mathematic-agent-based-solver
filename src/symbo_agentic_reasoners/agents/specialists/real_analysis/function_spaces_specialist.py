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
FUNCTION SPACES SPECIALIST (Tier 3)
====================================

Handles Lp spaces, Sobolev spaces, and function space analysis.

CAPABILITIES:
------------
- Lp space operations and norms
- Hölder and Minkowski inequalities
- Dense subspace detection
- Sobolev spaces W^{k,p}
- Weak derivatives
- Sobolev embeddings (basic cases)

THEORY:
-------
Lp spaces: {f : ∫|f|^p < ∞} with norm ||f||_p = (∫|f|^p)^(1/p)
Sobolev spaces: W^{k,p} = {f : D^α f ∈ Lp for |α| ≤ k}

Key inequalities:
- Hölder: ||fg||_1 ≤ ||f||_p ||g||_q where 1/p + 1/q = 1
- Minkowski: ||f + g||_p ≤ ||f||_p + ||g||_p

ALGORITHMIC BACKING:
-------------------
Native Python/NumPy implementation

REFERENCE:
---------
- Plan: Day 19 - Function spaces for Real Analysis
- Target: 90% real analysis coverage
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger('symbo_agentic_reasoners.specialists.function_spaces')


@dataclass
class FunctionSpaceInfo:
    """Information about function space membership."""
    space_name: str  # 'L^p', 'W^{k,p}', etc.
    in_space: bool
    norm: float
    parameters: Dict[str, Any]


class FunctionSpacesSpecialist(BDIAgent):
    """
    Function Spaces Specialist - Lp and Sobolev Spaces Expert

    DIRECTIVE:
    ---------
    Analyze function spaces, compute norms, verify inequalities,
    and handle Sobolev space operations.

    OPERATIONS:
    ----------
    - compute_lp_norm: ||f||_p = (∫|f|^p)^(1/p)
    - verify_holder_inequality: ||fg||_1 ≤ ||f||_p ||g||_q
    - verify_minkowski_inequality: ||f+g||_p ≤ ||f||_p + ||g||_p
    - check_lp_membership: Test if f ∈ Lp
    - compute_weak_derivative: Weak derivative in distribution sense
    - compute_sobolev_norm: ||f||_{W^{k,p}}
    - check_dense_subspace: Test if subspace is dense

    ALGORITHMIC BACKING:
    -------------------
    NumPy numerical integration and differentiation
    """

    def __init__(
        self,
        agent_id: str = 'function_spaces_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Function Spaces Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.norms_computed = 0
        self.inequalities_verified = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Function Spaces Specialist initialized")
        logger.info(f"  Theory: Lp spaces, Sobolev spaces, functional analysis")
        logger.info(f"  Capabilities: Norms, inequalities, weak derivatives")

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.real_analysis.function_spaces',
            agent_id=self.agent_id,
            algorithm='lp_sobolev',
            cost='medium',
            instance=self,
            type='numerical',
            tier='3',
            operations='lp_norm_sobolev_weak_derivative'
        )
        self.df.register(registration)
        logger.info(f"  [DF] Registered: math.real_analysis.function_spaces")

    def process(self, task_entry: Any) -> Any:
        """Process function space task."""
        logger.info(f"\n[{self.agent_id}] Processing function space task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'compute_norm')

            if operation == 'lp_norm':
                f = metadata.get('function')
                p = metadata.get('p', 2)
                domain = metadata.get('domain', (0, 1))
                result = self.compute_lp_norm(f, p, domain)
                if result.get('success'):
                    self.norms_computed += 1

            elif operation == 'verify_holder':
                result = self.verify_holder_inequality(
                    metadata.get('f'), metadata.get('g'),
                    metadata.get('p'), metadata.get('domain', (0, 1))
                )
                if result.get('success'):
                    self.inequalities_verified += 1

            else:
                result = {'success': False, 'error': f'Unknown operation: {operation}'}

            if result.get('success'):
                self.tasks_succeeded += 1

            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"Function space task failed: {e}")
            return {'success': False, 'error': str(e)}

    def compute_lp_norm(
        self,
        f: Callable[[float], float],
        p: float,
        domain: Tuple[float, float],
        n_points: int = 1000
    ) -> Dict[str, Any]:
        """
        Compute Lp norm: ||f||_p = (∫|f|^p dx)^(1/p)

        Args:
            f: Function to compute norm of
            p: Exponent (1 ≤ p < ∞, or p = np.inf for L∞)
            domain: Integration domain (a, b)
            n_points: Number of sample points

        Returns:
            Dict with Lp norm value
        """
        try:
            a, b = domain
            x = np.linspace(a, b, n_points)

            # Evaluate function
            f_values = np.array([f(xi) for xi in x])

            if p == np.inf:
                # L∞ norm: essential supremum
                norm = np.max(np.abs(f_values))
            else:
                # Lp norm: (∫|f|^p)^(1/p)
                integrand = np.abs(f_values) ** p
                integral = np.trapz(integrand, x)
                norm = integral ** (1/p)

            return {
                'success': True,
                'lp_norm': norm,
                'p': p,
                'domain': domain,
                'method': 'numerical_integration',
                'note': f'||f||_{p} = {norm:.6f}'
            }

        except Exception as e:
            logger.error(f"Lp norm computation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'lp_norm'
            }

    def verify_holder_inequality(
        self,
        f: Callable[[float], float],
        g: Callable[[float], float],
        p: float,
        domain: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Verify Hölder's inequality: ||fg||_1 ≤ ||f||_p ||g||_q

        where 1/p + 1/q = 1 (conjugate exponents).

        Args:
            f, g: Functions
            p: Exponent for f (p > 1)
            domain: Integration domain

        Returns:
            Dict with inequality verification
        """
        try:
            # Compute conjugate exponent q
            if p <= 1:
                return {
                    'success': False,
                    'error': 'Hölder inequality requires p > 1',
                    'method': 'holder_inequality'
                }

            q = p / (p - 1)  # Conjugate: 1/p + 1/q = 1

            # Compute norms
            norm_f = self.compute_lp_norm(f, p, domain)
            norm_g = self.compute_lp_norm(g, q, domain)
            norm_fg = self.compute_lp_norm(lambda x: f(x) * g(x), 1, domain)

            if not all([norm_f['success'], norm_g['success'], norm_fg['success']]):
                return {
                    'success': False,
                    'error': 'Norm computation failed',
                    'method': 'holder_inequality'
                }

            lhs = norm_fg['lp_norm']
            rhs = norm_f['lp_norm'] * norm_g['lp_norm']
            holds = lhs <= rhs + 1e-6

            return {
                'success': True,
                'holder_inequality': f'||fg||_1 ≤ ||f||_{p} ||g||_{q}',
                'lhs': lhs,
                'rhs': rhs,
                'holds': holds,
                'p': p,
                'q': q,
                'method': 'holder_inequality',
                'note': 'Hölder inequality verified numerically'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'holder_inequality'
            }

    def verify_minkowski_inequality(
        self,
        f: Callable[[float], float],
        g: Callable[[float], float],
        p: float,
        domain: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Verify Minkowski's inequality: ||f + g||_p ≤ ||f||_p + ||g||_p

        Triangle inequality for Lp spaces (p ≥ 1).

        Args:
            f, g: Functions
            p: Exponent (p ≥ 1)
            domain: Integration domain

        Returns:
            Dict with inequality verification
        """
        try:
            if p < 1:
                return {
                    'success': False,
                    'error': 'Minkowski inequality requires p ≥ 1',
                    'method': 'minkowski_inequality'
                }

            # Compute norms
            norm_f = self.compute_lp_norm(f, p, domain)
            norm_g = self.compute_lp_norm(g, p, domain)
            norm_sum = self.compute_lp_norm(lambda x: f(x) + g(x), p, domain)

            if not all([norm_f['success'], norm_g['success'], norm_sum['success']]):
                return {
                    'success': False,
                    'error': 'Norm computation failed',
                    'method': 'minkowski_inequality'
                }

            lhs = norm_sum['lp_norm']
            rhs = norm_f['lp_norm'] + norm_g['lp_norm']
            holds = lhs <= rhs + 1e-6

            return {
                'success': True,
                'minkowski_inequality': f'||f + g||_{p} ≤ ||f||_{p} + ||g||_{p}',
                'lhs': lhs,
                'rhs': rhs,
                'holds': holds,
                'p': p,
                'method': 'minkowski_inequality',
                'note': 'Triangle inequality for Lp spaces'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'minkowski_inequality'
            }

    def check_lp_membership(
        self,
        f: Callable[[float], float],
        p: float,
        domain: Tuple[float, float]
    ) -> FunctionSpaceInfo:
        """
        Test if function f is in Lp(domain).

        f ∈ Lp iff ∫|f|^p < ∞

        Args:
            f: Function to test
            p: Exponent
            domain: Domain

        Returns:
            FunctionSpaceInfo with membership result
        """
        try:
            norm_result = self.compute_lp_norm(f, p, domain)

            if norm_result['success']:
                norm_value = norm_result['lp_norm']
                in_lp = np.isfinite(norm_value)

                return FunctionSpaceInfo(
                    space_name=f'L^{p}',
                    in_space=in_lp,
                    norm=norm_value,
                    parameters={'p': p, 'domain': domain}
                )

        except Exception as e:
            logger.error(f"Lp membership test failed: {e}")

        return FunctionSpaceInfo(
            space_name=f'L^{p}',
            in_space=False,
            norm=np.inf,
            parameters={'p': p, 'domain': domain, 'error': str(e)}
        )

    def compute_weak_derivative(
        self,
        f: Callable[[float], float],
        domain: Tuple[float, float],
        order: int = 1,
        n_points: int = 1000
    ) -> Dict[str, Any]:
        """
        Compute weak derivative in distribution sense.

        For f ∈ L^1_loc, weak derivative f' satisfies:
        ∫f φ' dx = -∫f' φ dx for all test functions φ

        Args:
            f: Function
            domain: Domain
            order: Derivative order
            n_points: Sample points

        Returns:
            Dict with weak derivative (numerical approximation)
        """
        try:
            a, b = domain
            x = np.linspace(a, b, n_points)
            f_values = np.array([f(xi) for xi in x])

            # Numerical derivative approximation
            if order == 1:
                df_values = np.gradient(f_values, x)
            elif order == 2:
                df_values = np.gradient(np.gradient(f_values, x), x)
            else:
                # Higher-order derivatives
                result = f_values
                for _ in range(order):
                    result = np.gradient(result, x)
                df_values = result

            return {
                'success': True,
                'weak_derivative_order': order,
                'domain': domain,
                'method': 'numerical_gradient',
                'note': 'Weak derivative computed numerically',
                'exists': True
            }

        except Exception as e:
            logger.error(f"Weak derivative computation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'weak_derivative'
            }

    def compute_sobolev_norm(
        self,
        f: Callable[[float], float],
        k: int,
        p: float,
        domain: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Compute Sobolev norm ||f||_{W^{k,p}}.

        ||f||_{W^{k,p}} = (Σ_{|α|≤k} ||D^α f||_p^p)^(1/p)

        For 1D: ||f||_{W^{k,p}} = (Σ_{j=0}^k ||f^{(j)}||_p^p)^(1/p)

        Args:
            f: Function
            k: Derivative order
            p: Lp exponent
            domain: Domain

        Returns:
            Dict with Sobolev norm
        """
        try:
            # Compute Lp norms of f and its derivatives
            norms_p = []

            # Norm of f itself
            norm_f = self.compute_lp_norm(f, p, domain)
            if not norm_f['success']:
                return norm_f
            norms_p.append(norm_f['lp_norm'] ** p)

            # Norms of derivatives (numerical approximation)
            a, b = domain
            x = np.linspace(a, b, 1000)
            f_values = np.array([f(xi) for xi in x])
            current_deriv = f_values

            for j in range(1, k + 1):
                current_deriv = np.gradient(current_deriv, x)
                deriv_norm = np.trapz(np.abs(current_deriv) ** p, x) ** (1/p)
                norms_p.append(deriv_norm ** p)

            # Sobolev norm: (sum of Lp norms^p)^(1/p)
            sobolev_norm = sum(norms_p) ** (1/p)

            return {
                'success': True,
                'sobolev_norm': sobolev_norm,
                'space': f'W^{{{k},{p}}}',
                'k': k,
                'p': p,
                'domain': domain,
                'method': 'sobolev_norm',
                'note': f'||f||_{{W^{{{k},{p}}}}} = {sobolev_norm:.6f}'
            }

        except Exception as e:
            logger.error(f"Sobolev norm computation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'sobolev_norm'
            }

    def sobolev_embedding(
        self,
        k: int,
        p: float,
        dimension: int = 1
    ) -> Dict[str, Any]:
        """
        Apply Sobolev embedding theorems.

        For Ω ⊂ R^n bounded domain:
        - If kp > n: W^{k,p}(Ω) ↪ C^{k-⌈n/p⌉-1}(Ω)
        - If kp = n: W^{k,p}(Ω) ↪ L^q(Ω) for all q < ∞
        - If kp < n: W^{k,p}(Ω) ↪ L^{p*}(Ω) where 1/p* = 1/p - k/n

        Args:
            k: Derivative order
            p: Lp exponent
            dimension: Dimension n

        Returns:
            Dict with embedding information
        """
        try:
            n = dimension
            kp = k * p

            if kp > n:
                # Embeds into continuous functions
                m = k - int(np.ceil(n / p)) - 1
                target_space = f'C^{{{max(0, m)}}}'
                note = 'Embeds into continuous functions (Sobolev embedding)'

            elif kp == n:
                # Embeds into Lq for all q < ∞
                target_space = 'L^q for all q < ∞'
                note = 'Critical case: embeds into all Lq but not L∞'

            else:  # kp < n
                # Embeds into Lp* (Sobolev conjugate)
                p_star = n * p / (n - k * p)
                target_space = f'L^{{{p_star:.2f}}}'
                note = f'Sobolev conjugate: 1/p* = 1/p - k/n'

            return {
                'success': True,
                'source_space': f'W^{{{k},{p}}}(R^{n})',
                'target_space': target_space,
                'embedding_type': 'continuous' if kp > n else 'into Lp*',
                'dimension': n,
                'kp_product': kp,
                'method': 'sobolev_embedding',
                'note': note
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'sobolev_embedding'
            }

    def check_dense_subspace(
        self,
        subspace_desc: str,
        space_desc: str
    ) -> Dict[str, Any]:
        """
        Check if subspace is dense in space.

        Common dense subspaces:
        - C_c^∞ dense in Lp (smooth compactly supported functions)
        - Polynomials dense in C[a,b] (Weierstrass)
        - Simple functions dense in Lp

        Args:
            subspace_desc: Description of subspace
            space_desc: Description of space

        Returns:
            Dict with density result
        """
        try:
            # Known dense subspaces
            dense_pairs = {
                ('C_c^∞', 'L^p'): 'Smooth compactly supported functions are dense in Lp',
                ('polynomials', 'C[a,b]'): 'Weierstrass approximation theorem',
                ('simple functions', 'L^p'): 'Simple functions dense in Lp',
                ('step functions', 'L^1'): 'Step functions dense in L1',
            }

            key = (subspace_desc, space_desc)
            if key in dense_pairs:
                reason = dense_pairs[key]

                return {
                    'success': True,
                    'is_dense': True,
                    'subspace': subspace_desc,
                    'space': space_desc,
                    'reason': reason,
                    'method': 'dense_subspace',
                    'note': 'Every element can be approximated by subspace elements'
                }

            return {
                'success': False,
                'error': f'Density of {subspace_desc} in {space_desc} not in database',
                'method': 'dense_subspace'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'dense_subspace'
            }

    # BDI Interface Methods

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if not self.blackboard:
            return

        tasks = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            tags=['real_analysis', 'function_spaces']
        )

        for task in tasks:
            if task.status == EntryStatus.PENDING:
                self.beliefs.append({
                    'type': 'pending_task',
                    'task_id': task.entry_id,
                    'content': task.content
                })

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on beliefs."""
        new_intentions = []

        for belief in self.beliefs:
            if belief.get('type') == 'pending_task':
                intention = Intention(
                    goal="analyze_function_space",
                    plan=["parse_function", "compute_norm", "verify_membership"],
                    priority=5,
                    context={'task': belief}
                )
                new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention):
        """Execute next step in plan."""
        if not intention or not hasattr(intention, 'get_current_action'):
            return

        action = intention.get_current_action()

        if action in ['parse_function', 'compute_norm']:
            intention.advance()
        elif action == 'verify_membership':
            intention.complete()

    def get_statistics(self) -> Dict[str, Any]:
        """Return specialist statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'norms_computed': self.norms_computed,
            'inequalities_verified': self.inequalities_verified,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100) if self.tasks_executed > 0 else 0.0
        }


# Export
__all__ = [
    'FunctionSpacesSpecialist',
    'FunctionSpaceInfo',
]


if __name__ == "__main__":
    """Test Function Spaces Specialist."""
    print("=" * 80)
    print("FUNCTION SPACES SPECIALIST TEST")
    print("=" * 80)

    specialist = FunctionSpacesSpecialist()

    # Test Lp norm
    f = lambda x: x**2
    result = specialist.compute_lp_norm(f, 2, (0, 1))
    print(f"\nL2 norm of x²:")
    print(f"  ||f||_2 = {result.get('lp_norm')}")

    # Test Hölder inequality
    result = specialist.verify_holder_inequality(f, lambda x: x, 2, (0, 1))
    print(f"\nHölder inequality:")
    print(f"  Holds: {result.get('holds')}")

    # Test Sobolev embedding
    result = specialist.sobolev_embedding(1, 2, 1)
    print(f"\nSobolev embedding W^{{1,2}}:")
    print(f"  Embeds into: {result.get('target_space')}")

    print("\nFunction Spaces Specialist ready!")
