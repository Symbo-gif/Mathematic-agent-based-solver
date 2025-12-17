# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
KINEMATICS SPECIALIST (Tier 3)
==============================

Handles motion without considering forces: displacement, velocity,
acceleration, projectile motion, and relative motion.

CAPABILITIES:
- 1D/2D/3D motion equations
- Projectile motion (parabolic trajectories)
- Uniform and non-uniform acceleration
- Relative velocity calculations
- Free fall problems
"""

from typing import Any, Dict, List, Optional
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


# ============================================================================
# NATIVE KINEMATICS SOLVER (NO SYMPY)
# ============================================================================

class NativeKinematicsSolver:
    """
    Native kinematics equation solver without SymPy.
    Uses explicit algebraic manipulation of kinematic equations:
      v = v0 + a*t
      x = x0 + v0*t + 0.5*a*t^2
      v^2 = v0^2 + 2*a*(x - x0)
      x = x0 + 0.5*(v + v0)*t
    """

    @staticmethod
    def solve(known: Dict[str, float], find: str) -> Dict[str, Any]:
        """
        Solve kinematic equations for an unknown variable.
        Known can include: v0, v, a, t, x0, x
        """
        v0 = known.get('v0')
        v = known.get('v')
        a = known.get('a')
        t = known.get('t')
        x0 = known.get('x0', 0)  # Default starting position to 0
        x = known.get('x')

        # Calculate displacement if x and x0 are given
        s = None
        if x is not None and x0 is not None:
            s = x - x0

        try:
            if find == 'v':
                # v = v0 + a*t
                if v0 is not None and a is not None and t is not None:
                    return {'solution': [v0 + a * t]}
                # v^2 = v0^2 + 2*a*s
                if v0 is not None and a is not None and s is not None:
                    val = v0**2 + 2 * a * s
                    if val >= 0:
                        return {'solution': [math.sqrt(val), -math.sqrt(val)]}
                    return {'error': 'No real solution (negative under square root)'}
                return {'error': 'Insufficient known values to solve for v'}

            elif find == 'v0':
                # v0 = v - a*t
                if v is not None and a is not None and t is not None:
                    return {'solution': [v - a * t]}
                # v0^2 = v^2 - 2*a*s
                if v is not None and a is not None and s is not None:
                    val = v**2 - 2 * a * s
                    if val >= 0:
                        return {'solution': [math.sqrt(val), -math.sqrt(val)]}
                    return {'error': 'No real solution (negative under square root)'}
                return {'error': 'Insufficient known values to solve for v0'}

            elif find == 'a':
                # a = (v - v0) / t
                if v is not None and v0 is not None and t is not None and t != 0:
                    return {'solution': [(v - v0) / t]}
                # a = (v^2 - v0^2) / (2*s)
                if v is not None and v0 is not None and s is not None and s != 0:
                    return {'solution': [(v**2 - v0**2) / (2 * s)]}
                # a = 2*(s - v0*t) / t^2
                if s is not None and v0 is not None and t is not None and t != 0:
                    return {'solution': [2 * (s - v0 * t) / (t**2)]}
                return {'error': 'Insufficient known values to solve for a'}

            elif find == 't':
                # t = (v - v0) / a
                if v is not None and v0 is not None and a is not None and a != 0:
                    return {'solution': [(v - v0) / a]}
                # From s = v0*t + 0.5*a*t^2: quadratic in t
                if s is not None and v0 is not None and a is not None:
                    # 0.5*a*t^2 + v0*t - s = 0
                    A = 0.5 * a
                    B = v0
                    C = -s
                    if A == 0:
                        if B != 0:
                            return {'solution': [-C / B]}
                        return {'error': 'Cannot solve for t'}
                    disc = B**2 - 4 * A * C
                    if disc < 0:
                        return {'error': 'No real solution for t'}
                    solutions = [(-B + math.sqrt(disc)) / (2 * A),
                                (-B - math.sqrt(disc)) / (2 * A)]
                    # Filter positive times
                    positive = [sol for sol in solutions if sol >= 0]
                    return {'solution': positive if positive else solutions}
                return {'error': 'Insufficient known values to solve for t'}

            elif find == 'x':
                # x = x0 + v0*t + 0.5*a*t^2
                if x0 is not None and v0 is not None and t is not None and a is not None:
                    return {'solution': [x0 + v0 * t + 0.5 * a * t**2]}
                # x = x0 + 0.5*(v + v0)*t
                if x0 is not None and v is not None and v0 is not None and t is not None:
                    return {'solution': [x0 + 0.5 * (v + v0) * t]}
                # x = x0 + (v^2 - v0^2) / (2*a)
                if x0 is not None and v is not None and v0 is not None and a is not None and a != 0:
                    return {'solution': [x0 + (v**2 - v0**2) / (2 * a)]}
                return {'error': 'Insufficient known values to solve for x'}

            elif find == 'x0':
                # x0 = x - v0*t - 0.5*a*t^2
                if x is not None and v0 is not None and t is not None and a is not None:
                    return {'solution': [x - v0 * t - 0.5 * a * t**2]}
                return {'error': 'Insufficient known values to solve for x0'}

            else:
                return {'error': f'Unknown variable to solve for: {find}'}

        except Exception as e:
            return {'error': str(e)}


class KinematicsSpecialist(BDIAgent):
    """Specialist for kinematics (motion) problems."""

    # Standard kinematic equations
    # v = v0 + at
    # x = x0 + v0*t + 0.5*a*t^2
    # v^2 = v0^2 + 2*a*(x - x0)
    # x = x0 + 0.5*(v + v0)*t

    G = 9.81  # m/s^2

    def __init__(
        self,
        agent_id: str = 'kinematics_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.mechanics.kinematics',
                agent_id=agent_id,
                algorithm='native_kinematic_equations',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='motion_projectile_freefall_velocity'
            ))

        print(f"[{agent_id}] Kinematics Specialist initialized (NO SYMPY)")
        print(f"  Equations: v=v0+at, x=x0+v0t+0.5at^2, v^2=v0^2+2a(x-x0)")

    def solve_kinematics(self, known: Dict[str, float], find: str) -> Dict[str, Any]:
        """
        Solve kinematic equation for unknown variable using native solver.
        Known can include: v0, v, a, t, x0, x (displacement = x - x0)
        """
        return NativeKinematicsSolver.solve(known, find)

    def projectile_motion(self, v0: float, angle: float, h0: float = 0) -> Dict[str, Any]:
        """
        Calculate projectile motion parameters.
        v0: initial velocity (m/s)
        angle: launch angle (radians)
        h0: initial height (m)
        """
        g = self.G
        v0x = v0 * math.cos(angle)
        v0y = v0 * math.sin(angle)

        # Time of flight (solving h0 + v0y*t - 0.5*g*t^2 = 0)
        discriminant = v0y**2 + 2*g*h0
        if discriminant < 0:
            return {'error': 'Invalid parameters'}

        t_flight = (v0y + math.sqrt(discriminant)) / g

        # Maximum height
        h_max = h0 + v0y**2 / (2*g)

        # Range
        range_x = v0x * t_flight

        return {
            'initial_velocity_x': v0x,
            'initial_velocity_y': v0y,
            'time_of_flight': t_flight,
            'max_height': h_max,
            'range': range_x,
            'time_to_max_height': v0y / g
        }

    def free_fall(self, h: float = None, t: float = None, v0: float = 0) -> Dict[str, Any]:
        """Calculate free fall parameters."""
        g = self.G

        if h is not None:
            # Given height, find time and final velocity
            t_fall = math.sqrt(2*h/g) if v0 == 0 else (-v0 + math.sqrt(v0**2 + 2*g*h)) / g
            v_final = v0 + g * t_fall
            return {'time': t_fall, 'final_velocity': v_final, 'height': h}
        elif t is not None:
            # Given time, find height and final velocity
            h_fall = v0*t + 0.5*g*t**2
            v_final = v0 + g*t
            return {'time': t, 'final_velocity': v_final, 'height': h_fall}

        return {'error': 'Need either height or time'}

    def relative_velocity(self, v_a: tuple, v_b: tuple) -> Dict[str, Any]:
        """Calculate relative velocity of A with respect to B."""
        v_rel = tuple(a - b for a, b in zip(v_a, v_b))
        speed = math.sqrt(sum(c**2 for c in v_rel))
        return {'relative_velocity': v_rel, 'relative_speed': speed}

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a kinematics task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'solve')

        try:
            if operation == 'solve':
                return self.solve_kinematics(task['known'], task['find'])
            elif operation == 'projectile':
                return self.projectile_motion(
                    task['v0'], task['angle'], task.get('h0', 0)
                )
            elif operation == 'free_fall':
                return self.free_fall(task.get('h'), task.get('t'), task.get('v0', 0))
            elif operation == 'relative_velocity':
                return self.relative_velocity(task['v_a'], task['v_b'])
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending kinematics tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.mechanics.kinematics']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for kinematics tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_kinematics_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute kinematics computation via process()."""
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
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
