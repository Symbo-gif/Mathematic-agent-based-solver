# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
CIRCUITS SPECIALIST (Tier 3)
============================

Handles electrical circuits: Ohm's law, Kirchhoff's laws,
series/parallel resistors, RC/RL circuits, and power.

CAPABILITIES:
- Ohm's law (V = IR)
- Series and parallel resistor combinations
- Kirchhoff's voltage and current laws
- RC and RL circuit transients
- Power calculations
"""

from typing import Any, Dict, List, Optional
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class CircuitsSpecialist(BDIAgent):
    """Specialist for electrical circuit problems."""

    def __init__(
        self,
        agent_id: str = 'circuits_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.em.circuits',
                agent_id=agent_id,
                algorithm='kirchhoff_ohm',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='ohm_kirchhoff_series_parallel_rc_rl'
            ))

        print(f"[{agent_id}] Circuits Specialist initialized")
        print(f"  Laws: Ohm's Law, Kirchhoff's Laws")

    def ohms_law(self, V: float = None, I: float = None,
                 R: float = None) -> Dict[str, Any]:
        """V = I * R"""
        if V is not None and I is not None:
            return {'R': V / I, 'V': V, 'I': I}
        elif V is not None and R is not None:
            return {'I': V / R, 'V': V, 'R': R}
        elif I is not None and R is not None:
            return {'V': I * R, 'I': I, 'R': R}
        return {'error': 'Need two of: V, I, R'}

    def resistors_series(self, resistors: List[float]) -> Dict[str, Any]:
        """R_total = R1 + R2 + ... + Rn"""
        R_total = sum(resistors)
        return {
            'R_equivalent': R_total,
            'resistors': resistors,
            'configuration': 'series'
        }

    def resistors_parallel(self, resistors: List[float]) -> Dict[str, Any]:
        """1/R_total = 1/R1 + 1/R2 + ... + 1/Rn"""
        inv_sum = sum(1/R for R in resistors)
        R_total = 1 / inv_sum
        return {
            'R_equivalent': R_total,
            'resistors': resistors,
            'configuration': 'parallel'
        }

    def power_electrical(self, P: float = None, V: float = None,
                         I: float = None, R: float = None) -> Dict[str, Any]:
        """P = V*I = I^2*R = V^2/R"""
        if V is not None and I is not None:
            return {'P': V * I, 'V': V, 'I': I}
        elif I is not None and R is not None:
            return {'P': I**2 * R, 'I': I, 'R': R}
        elif V is not None and R is not None:
            return {'P': V**2 / R, 'V': V, 'R': R}
        return {'error': 'Need (V, I), (I, R), or (V, R)'}

    def rc_circuit_charging(self, R: float, C: float, V0: float,
                            t: float) -> Dict[str, Any]:
        """
        RC circuit charging from 0 to V0.
        V(t) = V0 * (1 - e^(-t/RC))
        I(t) = (V0/R) * e^(-t/RC)
        """
        tau = R * C  # Time constant
        V_t = V0 * (1 - math.exp(-t / tau))
        I_t = (V0 / R) * math.exp(-t / tau)

        return {
            'voltage': V_t,
            'current': I_t,
            'time_constant': tau,
            'time': t,
            'percent_charged': 100 * V_t / V0
        }

    def rc_circuit_discharging(self, R: float, C: float, V0: float,
                               t: float) -> Dict[str, Any]:
        """
        RC circuit discharging from V0.
        V(t) = V0 * e^(-t/RC)
        """
        tau = R * C
        V_t = V0 * math.exp(-t / tau)
        I_t = -(V0 / R) * math.exp(-t / tau)

        return {
            'voltage': V_t,
            'current': abs(I_t),
            'time_constant': tau,
            'time': t,
            'percent_remaining': 100 * V_t / V0
        }

    def rl_circuit(self, R: float, L: float, V0: float,
                   t: float, charging: bool = True) -> Dict[str, Any]:
        """
        RL circuit transient.
        I(t) = (V0/R) * (1 - e^(-Rt/L)) for charging
        """
        tau = L / R  # Time constant
        I_max = V0 / R

        if charging:
            I_t = I_max * (1 - math.exp(-t / tau))
        else:
            I_t = I_max * math.exp(-t / tau)

        return {
            'current': I_t,
            'max_current': I_max,
            'time_constant': tau,
            'time': t,
            'state': 'charging' if charging else 'discharging'
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a circuits task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'ohm')

        try:
            if operation == 'ohm':
                return self.ohms_law(task.get('V'), task.get('I'), task.get('R'))
            elif operation == 'series':
                return self.resistors_series(task['resistors'])
            elif operation == 'parallel':
                return self.resistors_parallel(task['resistors'])
            elif operation == 'power':
                return self.power_electrical(
                    task.get('P'), task.get('V'), task.get('I'), task.get('R')
                )
            elif operation == 'rc_charge':
                return self.rc_circuit_charging(
                    task['R'], task['C'], task['V0'], task['t']
                )
            elif operation == 'rc_discharge':
                return self.rc_circuit_discharging(
                    task['R'], task['C'], task['V0'], task['t']
                )
            elif operation == 'rl':
                return self.rl_circuit(
                    task['R'], task['L'], task['V0'], task['t'],
                    task.get('charging', True)
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending circuits tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.em.circuits']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for circuits tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_circuits_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute circuits computation via process()."""
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
        >>> specialist = CircuitsSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
