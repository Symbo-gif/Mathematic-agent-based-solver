# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
MAGNETISM SPECIALIST (Tier 3)
=============================

Handles magnetic phenomena: magnetic fields, Lorentz force,
Biot-Savart law, Ampere's law, and electromagnetic induction.

CAPABILITIES:
- Magnetic field from current-carrying wires
- Lorentz force on moving charges
- Magnetic force on current-carrying wires
- Faraday's law of induction
- Inductance calculations
"""

from typing import Any, Dict, List, Optional, Tuple
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class MagnetismSpecialist(BDIAgent):
    """Specialist for magnetism problems."""

    # Constants
    MU_0 = 4 * math.pi * 1e-7  # Permeability of free space (T*m/A)

    def __init__(
        self,
        agent_id: str = 'magnetism_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.em.magnetism',
                agent_id=agent_id,
                algorithm='biot_savart_ampere',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='magnetic_field_lorentz_induction'
            ))

        print(f"[{agent_id}] Magnetism Specialist initialized")
        print(f"  Laws: Biot-Savart, Ampere's Law, Faraday's Law")

    def magnetic_field_wire(self, I: float, r: float) -> float:
        """B = mu_0 * I / (2 * pi * r) for infinite straight wire"""
        return self.MU_0 * I / (2 * math.pi * r)

    def magnetic_field_solenoid(self, n: float, I: float) -> float:
        """B = mu_0 * n * I for solenoid (n = turns per length)"""
        return self.MU_0 * n * I

    def magnetic_field_loop_center(self, I: float, R: float) -> float:
        """B = mu_0 * I / (2 * R) at center of circular loop"""
        return self.MU_0 * I / (2 * R)

    def lorentz_force(self, q: float, v: float, B: float,
                      theta: float = math.pi/2) -> Dict[str, Any]:
        """F = q * v * B * sin(theta)"""
        F = abs(q) * v * B * math.sin(theta)
        return {
            'force': F,
            'charge': q,
            'velocity': v,
            'magnetic_field': B,
            'angle': theta
        }

    def force_on_wire(self, I: float, L: float, B: float,
                      theta: float = math.pi/2) -> float:
        """F = I * L * B * sin(theta)"""
        return I * L * B * math.sin(theta)

    def magnetic_flux(self, B: float, A: float, theta: float = 0) -> float:
        """Phi = B * A * cos(theta)"""
        return B * A * math.cos(theta)

    def faradays_law(self, N: int, dPhi: float, dt: float) -> float:
        """EMF = -N * dPhi/dt"""
        return -N * dPhi / dt

    def inductance_solenoid(self, N: int, A: float, l: float,
                            mu_r: float = 1) -> float:
        """L = mu_0 * mu_r * N^2 * A / l"""
        return self.MU_0 * mu_r * N**2 * A / l

    def inductor_energy(self, L: float, I: float) -> float:
        """U = 0.5 * L * I^2"""
        return 0.5 * L * I**2

    def cyclotron_radius(self, m: float, v: float, q: float, B: float) -> float:
        """r = m * v / (q * B)"""
        return m * v / (abs(q) * B)

    def cyclotron_frequency(self, q: float, B: float, m: float) -> float:
        """f = q * B / (2 * pi * m)"""
        return abs(q) * B / (2 * math.pi * m)

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a magnetism task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'field_wire')

        try:
            if operation == 'field_wire':
                return {'B': self.magnetic_field_wire(task['I'], task['r'])}
            elif operation == 'field_solenoid':
                return {'B': self.magnetic_field_solenoid(task['n'], task['I'])}
            elif operation == 'field_loop':
                return {'B': self.magnetic_field_loop_center(task['I'], task['R'])}
            elif operation == 'lorentz':
                return self.lorentz_force(
                    task['q'], task['v'], task['B'],
                    task.get('theta', math.pi/2)
                )
            elif operation == 'force_wire':
                return {'F': self.force_on_wire(
                    task['I'], task['L'], task['B'],
                    task.get('theta', math.pi/2)
                )}
            elif operation == 'flux':
                return {'Phi': self.magnetic_flux(
                    task['B'], task['A'], task.get('theta', 0)
                )}
            elif operation == 'faraday':
                return {'EMF': self.faradays_law(task['N'], task['dPhi'], task['dt'])}
            elif operation == 'inductance':
                return {'L': self.inductance_solenoid(
                    task['N'], task['A'], task['l'], task.get('mu_r', 1)
                )}
            elif operation == 'inductor_energy':
                return {'U': self.inductor_energy(task['L'], task['I'])}
            elif operation == 'cyclotron_radius':
                return {'r': self.cyclotron_radius(
                    task['m'], task['v'], task['q'], task['B']
                )}
            elif operation == 'cyclotron_freq':
                return {'f': self.cyclotron_frequency(task['q'], task['B'], task['m'])}
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending magnetism tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.em.magnetism']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for magnetism tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_magnetism_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute magnetism computation via process()."""
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
        >>> specialist = MagnetismSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
