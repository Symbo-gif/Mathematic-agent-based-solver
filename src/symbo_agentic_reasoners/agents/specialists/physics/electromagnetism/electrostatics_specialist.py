# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
ELECTROSTATICS SPECIALIST (Tier 3)
==================================

Handles electrostatic phenomena: Coulomb's law, electric fields,
electric potential, Gauss's law, and capacitance.

CAPABILITIES:
- Coulomb's law calculations
- Electric field from point charges
- Electric potential and voltage
- Gauss's law applications
- Capacitance calculations
"""

from typing import Any, Dict, List, Optional
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class ElectrostaticsSpecialist(BDIAgent):
    """Specialist for electrostatics problems."""

    # Constants
    K = 8.99e9  # Coulomb's constant (N*m^2/C^2)
    EPSILON_0 = 8.85e-12  # Permittivity of free space (F/m)
    E_CHARGE = 1.6e-19  # Elementary charge (C)

    def __init__(
        self,
        agent_id: str = 'electrostatics_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.em.electrostatics',
                agent_id=agent_id,
                algorithm='coulomb_gauss',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='coulomb_field_potential_gauss_capacitance'
            ))

        print(f"[{agent_id}] Electrostatics Specialist initialized")
        print(f"  Laws: Coulomb's Law, Gauss's Law")

    def coulombs_law(self, q1: float, q2: float, r: float) -> Dict[str, Any]:
        """F = k * q1 * q2 / r^2"""
        F = self.K * q1 * q2 / r**2
        return {
            'force': abs(F),
            'attractive': F < 0,
            'q1': q1, 'q2': q2, 'distance': r
        }

    def electric_field_point(self, q: float, r: float) -> Dict[str, Any]:
        """E = k * q / r^2"""
        E = self.K * q / r**2
        return {
            'field_magnitude': abs(E),
            'direction': 'away from charge' if q > 0 else 'toward charge',
            'charge': q, 'distance': r
        }

    def electric_potential_point(self, q: float, r: float) -> float:
        """V = k * q / r"""
        return self.K * q / r

    def potential_energy(self, q1: float, q2: float, r: float) -> float:
        """U = k * q1 * q2 / r"""
        return self.K * q1 * q2 / r

    def capacitance_parallel_plate(self, A: float, d: float,
                                    epsilon_r: float = 1) -> Dict[str, Any]:
        """C = epsilon_0 * epsilon_r * A / d"""
        C = self.EPSILON_0 * epsilon_r * A / d
        return {
            'capacitance': C,
            'area': A,
            'separation': d,
            'dielectric_constant': epsilon_r
        }

    def capacitor_energy(self, C: float = None, V: float = None,
                         Q: float = None) -> Dict[str, Any]:
        """U = 0.5 * C * V^2 = 0.5 * Q^2 / C = 0.5 * Q * V"""
        if C is not None and V is not None:
            Q = C * V
            U = 0.5 * C * V**2
        elif Q is not None and C is not None:
            V = Q / C
            U = 0.5 * Q**2 / C
        elif Q is not None and V is not None:
            C = Q / V
            U = 0.5 * Q * V
        else:
            return {'error': 'Need two of: C, V, Q'}

        return {'energy': U, 'capacitance': C, 'voltage': V, 'charge': Q}

    def electric_field_infinite_line(self, lambda_: float, r: float) -> float:
        """E = lambda / (2 * pi * epsilon_0 * r) for infinite line charge"""
        return lambda_ / (2 * math.pi * self.EPSILON_0 * r)

    def electric_field_infinite_plane(self, sigma: float) -> float:
        """E = sigma / (2 * epsilon_0) for infinite plane"""
        return sigma / (2 * self.EPSILON_0)

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an electrostatics task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'coulomb')

        try:
            if operation == 'coulomb':
                return self.coulombs_law(task['q1'], task['q2'], task['r'])
            elif operation == 'electric_field':
                return self.electric_field_point(task['q'], task['r'])
            elif operation == 'potential':
                return {'V': self.electric_potential_point(task['q'], task['r'])}
            elif operation == 'potential_energy':
                return {'U': self.potential_energy(task['q1'], task['q2'], task['r'])}
            elif operation == 'capacitance':
                return self.capacitance_parallel_plate(
                    task['A'], task['d'], task.get('epsilon_r', 1)
                )
            elif operation == 'capacitor_energy':
                return self.capacitor_energy(
                    task.get('C'), task.get('V'), task.get('Q')
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending electrostatics tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.em.electrostatics']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for electrostatics tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_electrostatics_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute electrostatics computation via process()."""
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
        >>> specialist = ElectrostaticsSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
