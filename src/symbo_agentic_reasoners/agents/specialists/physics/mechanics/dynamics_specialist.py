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
DYNAMICS SPECIALIST (Tier 3)
============================

Handles forces and Newton's laws: F=ma, friction, tension, normal forces,
inclined planes, and systems of objects.

CAPABILITIES:
- Newton's three laws applications
- Friction (static and kinetic)
- Tension and pulley systems
- Inclined plane problems
- Circular motion dynamics
"""

from typing import Any, Dict, List, Optional, Tuple
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


# ============================================================================
# NO SYMPY - All physics calculations use explicit formulas with math module
# ============================================================================


class DynamicsSpecialist(BDIAgent):
    """Specialist for dynamics (forces) problems."""

    G = 9.81  # m/s^2

    def __init__(
        self,
        agent_id: str = 'dynamics_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.mechanics.dynamics',
                agent_id=agent_id,
                algorithm='native_newton_laws',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='forces_friction_tension_incline_circular'
            ))

        print(f"[{agent_id}] Dynamics Specialist initialized (NO SYMPY)")
        print(f"  Laws: Newton's Laws, F=ma, friction, circular motion")

    def newtons_second_law(self, m: float = None, a: float = None,
                           F_net: float = None) -> Dict[str, Any]:
        """Apply F = ma to find unknown."""
        if m is not None and a is not None:
            return {'F_net': m * a}
        elif F_net is not None and m is not None:
            return {'acceleration': F_net / m}
        elif F_net is not None and a is not None:
            return {'mass': F_net / a}
        return {'error': 'Need two of: m, a, F_net'}

    def friction_force(self, N: float, mu: float,
                       friction_type: str = 'kinetic') -> Dict[str, Any]:
        """Calculate friction force. f = mu * N"""
        f = mu * N
        return {
            'friction_force': f,
            'normal_force': N,
            'coefficient': mu,
            'type': friction_type
        }

    def inclined_plane(self, m: float, theta: float, mu: float = 0) -> Dict[str, Any]:
        """
        Analyze forces on inclined plane.
        m: mass (kg)
        theta: angle (radians)
        mu: coefficient of friction
        """
        g = self.G

        # Weight components
        W = m * g
        W_parallel = W * math.sin(theta)  # Component along plane
        W_perpendicular = W * math.cos(theta)  # Component into plane

        # Normal force
        N = W_perpendicular

        # Friction force
        f = mu * N

        # Net force along plane (positive = down the plane)
        F_net = W_parallel - f

        # Acceleration
        a = F_net / m

        # Check if object moves
        static_friction_max = mu * N
        will_slide = W_parallel > static_friction_max

        return {
            'weight': W,
            'weight_parallel': W_parallel,
            'weight_perpendicular': W_perpendicular,
            'normal_force': N,
            'friction_force': f,
            'net_force': F_net,
            'acceleration': a if will_slide else 0,
            'will_slide': will_slide
        }

    def tension_two_masses(self, m1: float, m2: float,
                           mu1: float = 0, mu2: float = 0) -> Dict[str, Any]:
        """
        Atwood machine or horizontal pulley system.
        m1 hanging, m2 on table with friction.
        """
        g = self.G

        # For Atwood-like system (m1 hanging, m2 on frictionless table)
        # a = (m1 * g - mu2 * m2 * g) / (m1 + m2)
        # T = m1 * (g - a)

        friction = mu2 * m2 * g
        a = (m1 * g - friction) / (m1 + m2)
        T = m1 * (g - a)

        return {
            'acceleration': a,
            'tension': T,
            'friction_force': friction
        }

    def circular_motion(self, m: float, v: float = None, r: float = None,
                        omega: float = None, period: float = None) -> Dict[str, Any]:
        """
        Circular motion dynamics.
        F_c = mv^2/r = m*omega^2*r
        """
        results = {'mass': m}

        # Determine velocity from available info
        if v is not None:
            pass
        elif omega is not None and r is not None:
            v = omega * r
        elif period is not None and r is not None:
            omega = 2 * math.pi / period
            v = omega * r
        else:
            return {'error': 'Need velocity or (omega and radius) or (period and radius)'}

        if r is None:
            return {'error': 'Need radius'}

        # Centripetal acceleration and force
        a_c = v**2 / r
        F_c = m * a_c

        # Angular quantities
        omega = v / r
        period = 2 * math.pi / omega

        return {
            'velocity': v,
            'radius': r,
            'centripetal_acceleration': a_c,
            'centripetal_force': F_c,
            'angular_velocity': omega,
            'period': period
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a dynamics task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'newton2')

        try:
            if operation == 'newton2':
                return self.newtons_second_law(
                    task.get('m'), task.get('a'), task.get('F_net')
                )
            elif operation == 'friction':
                return self.friction_force(
                    task['N'], task['mu'], task.get('type', 'kinetic')
                )
            elif operation == 'incline':
                return self.inclined_plane(
                    task['m'], task['theta'], task.get('mu', 0)
                )
            elif operation == 'tension':
                return self.tension_two_masses(
                    task['m1'], task['m2'],
                    task.get('mu1', 0), task.get('mu2', 0)
                )
            elif operation == 'circular':
                return self.circular_motion(
                    task['m'], task.get('v'), task.get('r'),
                    task.get('omega'), task.get('period')
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending dynamics tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.mechanics.dynamics']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for dynamics tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_dynamics_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute dynamics computation via process()."""
        if not intention or not hasattr(intention, 'metadata'):
            return
        entry = intention.metadata.get('entry')
        if not entry:
            return
        action = intention.get_current_action()
        if action == 'accept_task':
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import EntryStatus
                self.blackboard.update_entry_status(entry.entry_id, EntryStatus.IN_PROGRESS)
            intention.advance()
        elif action == 'solve':
            task = entry.metadata if hasattr(entry, 'metadata') and entry.metadata else {}
            result = self.process(task)
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post_result':
            result = intention.metadata.get('result', {})
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
                from symbo_agentic_reasoners.core.omdoc_schema import create_variable
                result_entry = create_entry(
                    entry_type=EntryType.RESULT,
                    content=create_variable(str(result)),
                    author_agent=self.agent_id,
                    status=EntryStatus.COMPLETED,
                    metadata={'result': result, 'result_str': str(result)}
                )
                self.blackboard.post(result_entry)
                self.blackboard.update_entry_status(entry.entry_id, EntryStatus.COMPLETED)
            del self.beliefs[f'task_{entry.entry_id}']
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = DynamicsSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
