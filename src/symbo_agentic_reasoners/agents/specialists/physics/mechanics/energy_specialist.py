# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
ENERGY SPECIALIST (Tier 3)
==========================

Handles energy and work: kinetic energy, potential energy, work,
power, conservation of energy, and collisions.

CAPABILITIES:
- Kinetic and potential energy calculations
- Work-energy theorem
- Conservation of mechanical energy
- Power calculations
- Elastic and inelastic collisions
- Momentum conservation
"""

from typing import Any, Dict, List, Optional, Tuple
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class EnergySpecialist(BDIAgent):
    """Specialist for energy and work problems."""

    G = 9.81  # m/s^2

    def __init__(
        self,
        agent_id: str = 'energy_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.mechanics.energy',
                agent_id=agent_id,
                algorithm='energy_conservation',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='kinetic_potential_work_power_collisions'
            ))

        print(f"[{agent_id}] Energy Specialist initialized")
        print(f"  Concepts: KE, PE, Work, Power, Conservation, Collisions")

    def kinetic_energy(self, m: float, v: float) -> float:
        """KE = 0.5 * m * v^2"""
        return 0.5 * m * v**2

    def potential_energy_gravity(self, m: float, h: float) -> float:
        """PE = m * g * h"""
        return m * self.G * h

    def potential_energy_spring(self, k: float, x: float) -> float:
        """PE = 0.5 * k * x^2"""
        return 0.5 * k * x**2

    def work(self, F: float, d: float, theta: float = 0) -> float:
        """W = F * d * cos(theta)"""
        return F * d * math.cos(theta)

    def power(self, W: float = None, t: float = None,
              F: float = None, v: float = None) -> Dict[str, Any]:
        """P = W/t or P = F*v"""
        if W is not None and t is not None:
            return {'power': W / t, 'unit': 'W'}
        elif F is not None and v is not None:
            return {'power': F * v, 'unit': 'W'}
        return {'error': 'Need (W, t) or (F, v)'}

    def conservation_energy(self, m: float, h1: float, v1: float,
                            h2: float = None, v2: float = None,
                            work_nc: float = 0) -> Dict[str, Any]:
        """
        Apply conservation of energy: KE1 + PE1 + W_nc = KE2 + PE2
        Solve for unknown (h2 or v2)
        work_nc: work done by non-conservative forces (friction, etc.)
        """
        KE1 = self.kinetic_energy(m, v1)
        PE1 = self.potential_energy_gravity(m, h1)
        E1 = KE1 + PE1

        if v2 is None and h2 is not None:
            # Solve for v2
            PE2 = self.potential_energy_gravity(m, h2)
            KE2 = E1 + work_nc - PE2
            if KE2 < 0:
                return {'error': 'Insufficient energy to reach height'}
            v2 = math.sqrt(2 * KE2 / m)
            return {
                'v2': v2,
                'KE1': KE1, 'PE1': PE1,
                'KE2': KE2, 'PE2': PE2
            }
        elif h2 is None and v2 is not None:
            # Solve for h2
            KE2 = self.kinetic_energy(m, v2)
            PE2 = E1 + work_nc - KE2
            h2 = PE2 / (m * self.G)
            return {
                'h2': h2,
                'KE1': KE1, 'PE1': PE1,
                'KE2': KE2, 'PE2': PE2
            }

        return {'error': 'Need either h2 or v2'}

    def elastic_collision_1d(self, m1: float, v1: float,
                              m2: float, v2: float = 0) -> Dict[str, Any]:
        """
        1D elastic collision.
        Both momentum and kinetic energy conserved.
        """
        # v1' = ((m1-m2)v1 + 2m2v2) / (m1+m2)
        # v2' = ((m2-m1)v2 + 2m1v1) / (m1+m2)
        v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

        # Verify conservation
        p_initial = m1 * v1 + m2 * v2
        p_final = m1 * v1_final + m2 * v2_final
        KE_initial = 0.5 * m1 * v1**2 + 0.5 * m2 * v2**2
        KE_final = 0.5 * m1 * v1_final**2 + 0.5 * m2 * v2_final**2

        return {
            'v1_final': v1_final,
            'v2_final': v2_final,
            'momentum_conserved': abs(p_initial - p_final) < 1e-10,
            'KE_conserved': abs(KE_initial - KE_final) < 1e-10
        }

    def inelastic_collision_1d(self, m1: float, v1: float,
                                m2: float, v2: float = 0) -> Dict[str, Any]:
        """
        Perfectly inelastic collision (objects stick together).
        Only momentum conserved.
        """
        v_final = (m1 * v1 + m2 * v2) / (m1 + m2)

        KE_initial = 0.5 * m1 * v1**2 + 0.5 * m2 * v2**2
        KE_final = 0.5 * (m1 + m2) * v_final**2
        KE_lost = KE_initial - KE_final

        return {
            'v_final': v_final,
            'combined_mass': m1 + m2,
            'KE_initial': KE_initial,
            'KE_final': KE_final,
            'KE_lost': KE_lost,
            'KE_lost_percent': 100 * KE_lost / KE_initial if KE_initial > 0 else 0
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an energy task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'kinetic_energy')

        try:
            if operation == 'kinetic_energy':
                return {'KE': self.kinetic_energy(task['m'], task['v'])}
            elif operation == 'potential_gravity':
                return {'PE': self.potential_energy_gravity(task['m'], task['h'])}
            elif operation == 'potential_spring':
                return {'PE': self.potential_energy_spring(task['k'], task['x'])}
            elif operation == 'work':
                return {'W': self.work(task['F'], task['d'], task.get('theta', 0))}
            elif operation == 'power':
                return self.power(task.get('W'), task.get('t'),
                                 task.get('F'), task.get('v'))
            elif operation == 'conservation':
                return self.conservation_energy(
                    task['m'], task['h1'], task['v1'],
                    task.get('h2'), task.get('v2'), task.get('work_nc', 0)
                )
            elif operation == 'elastic_collision':
                return self.elastic_collision_1d(
                    task['m1'], task['v1'], task['m2'], task.get('v2', 0)
                )
            elif operation == 'inelastic_collision':
                return self.inelastic_collision_1d(
                    task['m1'], task['v1'], task['m2'], task.get('v2', 0)
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending energy tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.mechanics.energy']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for energy tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_energy_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute energy computation via process()."""
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
        >>> specialist = EnergySpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
