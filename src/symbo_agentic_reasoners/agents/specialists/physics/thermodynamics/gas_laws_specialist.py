# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
GAS LAWS SPECIALIST (Tier 3)
============================

Handles ideal gas law and thermodynamic processes:
PV=nRT, isothermal, adiabatic, isobaric, isochoric processes.

CAPABILITIES:
- Ideal gas law (PV = nRT)
- Combined gas law
- Isothermal processes
- Adiabatic processes
- Work and heat in thermodynamic cycles
"""

from typing import Any, Dict, List, Optional
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class GasLawsSpecialist(BDIAgent):
    """Specialist for gas laws and thermodynamic processes."""

    # Constants
    R = 8.314  # Universal gas constant (J/(mol*K))
    K_B = 1.38e-23  # Boltzmann constant (J/K)

    def __init__(
        self,
        agent_id: str = 'gas_laws_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.thermo.gas',
                agent_id=agent_id,
                algorithm='ideal_gas',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='ideal_gas_isothermal_adiabatic_cycles'
            ))

        print(f"[{agent_id}] Gas Laws Specialist initialized")
        print(f"  Laws: Ideal Gas Law, Thermodynamic Processes")

    def ideal_gas_law(self, P: float = None, V: float = None,
                      n: float = None, T: float = None) -> Dict[str, Any]:
        """PV = nRT - solve for the unknown"""
        if P is None:
            P = n * self.R * T / V
            return {'P': P, 'V': V, 'n': n, 'T': T}
        elif V is None:
            V = n * self.R * T / P
            return {'P': P, 'V': V, 'n': n, 'T': T}
        elif n is None:
            n = P * V / (self.R * T)
            return {'P': P, 'V': V, 'n': n, 'T': T}
        elif T is None:
            T = P * V / (n * self.R)
            return {'P': P, 'V': V, 'n': n, 'T': T}
        return {'error': 'Provide exactly three of: P, V, n, T'}

    def combined_gas_law(self, P1: float, V1: float, T1: float,
                         P2: float = None, V2: float = None,
                         T2: float = None) -> Dict[str, Any]:
        """P1*V1/T1 = P2*V2/T2"""
        ratio = P1 * V1 / T1

        if P2 is None:
            P2 = ratio * T2 / V2
        elif V2 is None:
            V2 = ratio * T2 / P2
        elif T2 is None:
            T2 = P2 * V2 / ratio

        return {
            'P1': P1, 'V1': V1, 'T1': T1,
            'P2': P2, 'V2': V2, 'T2': T2
        }

    def isothermal_work(self, n: float, T: float,
                        V1: float, V2: float) -> Dict[str, Any]:
        """W = n*R*T*ln(V2/V1) for isothermal expansion"""
        W = n * self.R * T * math.log(V2 / V1)
        return {
            'work': W,
            'process': 'isothermal',
            'expansion': V2 > V1,
            'heat_absorbed': W  # For isothermal, Q = W
        }

    def adiabatic_process(self, P1: float, V1: float, V2: float,
                          gamma: float = 1.4) -> Dict[str, Any]:
        """
        Adiabatic process: PV^gamma = constant
        gamma = Cp/Cv (1.4 for diatomic ideal gas)
        """
        P2 = P1 * (V1 / V2)**gamma

        # Work done
        W = (P1 * V1 - P2 * V2) / (gamma - 1)

        return {
            'P1': P1, 'V1': V1,
            'P2': P2, 'V2': V2,
            'gamma': gamma,
            'work': W,
            'heat': 0,  # Adiabatic = no heat transfer
            'process': 'adiabatic'
        }

    def isobaric_work(self, P: float, V1: float, V2: float) -> Dict[str, Any]:
        """W = P * (V2 - V1) for constant pressure"""
        W = P * (V2 - V1)
        return {
            'work': W,
            'pressure': P,
            'process': 'isobaric'
        }

    def isochoric_process(self, n: float, Cv: float,
                          T1: float, T2: float) -> Dict[str, Any]:
        """Constant volume: W = 0, Q = n*Cv*dT"""
        Q = n * Cv * (T2 - T1)
        return {
            'work': 0,
            'heat': Q,
            'process': 'isochoric'
        }

    def carnot_efficiency(self, T_hot: float, T_cold: float) -> Dict[str, Any]:
        """eta = 1 - T_cold/T_hot"""
        eta = 1 - T_cold / T_hot
        return {
            'efficiency': eta,
            'efficiency_percent': eta * 100,
            'T_hot': T_hot,
            'T_cold': T_cold
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a gas laws task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'ideal_gas')

        try:
            if operation == 'ideal_gas':
                return self.ideal_gas_law(
                    task.get('P'), task.get('V'),
                    task.get('n'), task.get('T')
                )
            elif operation == 'combined':
                return self.combined_gas_law(
                    task['P1'], task['V1'], task['T1'],
                    task.get('P2'), task.get('V2'), task.get('T2')
                )
            elif operation == 'isothermal':
                return self.isothermal_work(
                    task['n'], task['T'], task['V1'], task['V2']
                )
            elif operation == 'adiabatic':
                return self.adiabatic_process(
                    task['P1'], task['V1'], task['V2'],
                    task.get('gamma', 1.4)
                )
            elif operation == 'isobaric':
                return self.isobaric_work(task['P'], task['V1'], task['V2'])
            elif operation == 'isochoric':
                return self.isochoric_process(
                    task['n'], task['Cv'], task['T1'], task['T2']
                )
            elif operation == 'carnot':
                return self.carnot_efficiency(task['T_hot'], task['T_cold'])
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending gas laws tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.thermo.gas']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for gas laws tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_gas_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute gas laws computation via process()."""
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
