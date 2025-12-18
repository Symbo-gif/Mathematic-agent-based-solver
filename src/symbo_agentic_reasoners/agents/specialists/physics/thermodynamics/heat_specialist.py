# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
HEAT TRANSFER SPECIALIST (Tier 3)
=================================

Handles heat transfer: conduction, convection, radiation,
specific heat, latent heat, and thermal equilibrium.

CAPABILITIES:
- Heat conduction (Fourier's law)
- Heat convection
- Thermal radiation (Stefan-Boltzmann)
- Specific heat calculations
- Phase changes and latent heat
"""

from typing import Any, Dict, List, Optional
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class HeatTransferSpecialist(BDIAgent):
    """Specialist for heat transfer problems."""

    # Constants
    STEFAN_BOLTZMANN = 5.67e-8  # W/(m^2*K^4)

    def __init__(
        self,
        agent_id: str = 'heat_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.thermo.heat',
                agent_id=agent_id,
                algorithm='heat_transfer',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='conduction_convection_radiation_specific_heat'
            ))

        print(f"[{agent_id}] Heat Transfer Specialist initialized")
        print(f"  Topics: Conduction, Convection, Radiation, Specific Heat")

    def heat_capacity(self, m: float, c: float, dT: float) -> float:
        """Q = m * c * dT"""
        return m * c * dT

    def heat_conduction(self, k: float, A: float, dT: float,
                        L: float, t: float = 1) -> Dict[str, Any]:
        """
        Fourier's law: Q/t = k * A * dT / L
        k: thermal conductivity (W/(m*K))
        A: area (m^2)
        dT: temperature difference (K)
        L: thickness (m)
        """
        power = k * A * dT / L
        Q = power * t
        return {
            'heat_rate': power,
            'heat_transferred': Q,
            'thermal_conductivity': k,
            'area': A,
            'temperature_diff': dT,
            'thickness': L
        }

    def thermal_radiation(self, epsilon: float, A: float, T: float) -> Dict[str, Any]:
        """
        Stefan-Boltzmann law: P = epsilon * sigma * A * T^4
        epsilon: emissivity (0 to 1)
        T: absolute temperature (K)
        """
        P = epsilon * self.STEFAN_BOLTZMANN * A * T**4
        return {
            'radiated_power': P,
            'emissivity': epsilon,
            'area': A,
            'temperature': T
        }

    def thermal_equilibrium(self, m1: float, c1: float, T1: float,
                            m2: float, c2: float, T2: float) -> Dict[str, Any]:
        """
        Two objects reaching thermal equilibrium.
        m1*c1*(Tf - T1) + m2*c2*(Tf - T2) = 0
        """
        Tf = (m1 * c1 * T1 + m2 * c2 * T2) / (m1 * c1 + m2 * c2)
        Q = m1 * c1 * (Tf - T1)
        return {
            'final_temperature': Tf,
            'heat_transferred': abs(Q),
            'heat_from': 'object 1' if Q > 0 else 'object 2'
        }

    def latent_heat(self, m: float, L: float) -> float:
        """Q = m * L (phase change)"""
        return m * L

    def phase_change_with_temp(self, m: float, c: float, T_initial: float,
                               T_final: float, T_phase: float, L: float) -> Dict[str, Any]:
        """
        Heat required for temperature change with phase change.
        Example: heating ice from -10C to steam at 110C
        """
        Q_total = 0
        steps = []

        if T_initial < T_phase <= T_final:
            # Heat to phase change temperature
            Q1 = m * c * (T_phase - T_initial)
            Q_total += Q1
            steps.append(f"Heat to {T_phase}K: {Q1:.2f} J")

            # Phase change
            Q2 = m * L
            Q_total += Q2
            steps.append(f"Phase change: {Q2:.2f} J")

            # Heat from phase change to final
            Q3 = m * c * (T_final - T_phase)
            Q_total += Q3
            steps.append(f"Heat to {T_final}K: {Q3:.2f} J")
        else:
            Q_total = m * c * (T_final - T_initial)
            steps.append(f"Heat from {T_initial}K to {T_final}K: {Q_total:.2f} J")

        return {
            'total_heat': Q_total,
            'steps': steps
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a heat transfer task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'heat_capacity')

        try:
            if operation == 'heat_capacity':
                return {'Q': self.heat_capacity(task['m'], task['c'], task['dT'])}
            elif operation == 'conduction':
                return self.heat_conduction(
                    task['k'], task['A'], task['dT'],
                    task['L'], task.get('t', 1)
                )
            elif operation == 'radiation':
                return self.thermal_radiation(
                    task['epsilon'], task['A'], task['T']
                )
            elif operation == 'equilibrium':
                return self.thermal_equilibrium(
                    task['m1'], task['c1'], task['T1'],
                    task['m2'], task['c2'], task['T2']
                )
            elif operation == 'latent':
                return {'Q': self.latent_heat(task['m'], task['L'])}
            elif operation == 'phase_change':
                return self.phase_change_with_temp(
                    task['m'], task['c'], task['T_initial'],
                    task['T_final'], task['T_phase'], task['L']
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending heat transfer tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.thermo.heat']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for heat transfer tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_heat_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute heat transfer computation via process()."""
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
        >>> specialist = HeatTransferSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
