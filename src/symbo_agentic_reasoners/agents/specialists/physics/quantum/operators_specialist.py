# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
OPERATORS SPECIALIST (Tier 3)
=============================

Handles quantum mechanical operators: commutators, eigenvalue problems,
spin operators, and angular momentum.

CAPABILITIES:
- Commutator calculations
- Angular momentum operators
- Spin operators and Pauli matrices
- Eigenvalue problems
- Ladder operators
"""

from typing import Any, Dict, List, Optional, Tuple
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class OperatorsSpecialist(BDIAgent):
    """Specialist for quantum operators problems."""

    # Constants
    HBAR = 1.055e-34  # Reduced Planck constant (J*s)

    # Pauli matrices (as tuples for immutability)
    PAULI_X = ((0, 1), (1, 0))
    PAULI_Y = ((0, -1j), (1j, 0))
    PAULI_Z = ((1, 0), (0, -1))

    def __init__(
        self,
        agent_id: str = 'operators_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.quantum.operators',
                agent_id=agent_id,
                algorithm='operator_algebra',
                cost='medium',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='commutators_angular_momentum_spin'
            ))

        print(f"[{agent_id}] Operators Specialist initialized")
        print(f"  Topics: Commutators, Angular Momentum, Spin")

    def angular_momentum_eigenvalue(self, l: int, m: int) -> Dict[str, Any]:
        """
        Angular momentum eigenvalues.
        L^2 |l,m> = hbar^2 * l(l+1) |l,m>
        L_z |l,m> = hbar * m |l,m>
        """
        if abs(m) > l:
            return {'error': f'|m| must be <= l, got m={m}, l={l}'}

        L2_eigenvalue = self.HBAR**2 * l * (l + 1)
        Lz_eigenvalue = self.HBAR * m

        return {
            'L_squared': L2_eigenvalue,
            'L_z': Lz_eigenvalue,
            'l': l,
            'm': m,
            'num_m_states': 2 * l + 1
        }

    def spin_eigenvalue(self, s: float, m_s: float) -> Dict[str, Any]:
        """
        Spin angular momentum eigenvalues.
        S^2 |s,m_s> = hbar^2 * s(s+1) |s,m_s>
        S_z |s,m_s> = hbar * m_s |s,m_s>
        """
        if abs(m_s) > s:
            return {'error': f'|m_s| must be <= s'}

        S2_eigenvalue = self.HBAR**2 * s * (s + 1)
        Sz_eigenvalue = self.HBAR * m_s

        return {
            'S_squared': S2_eigenvalue,
            'S_z': Sz_eigenvalue,
            's': s,
            'm_s': m_s,
            'num_states': int(2 * s + 1)
        }

    def ladder_operator(self, l: int, m: int, raise_op: bool = True) -> Dict[str, Any]:
        """
        Ladder operators L+ and L-.
        L+ |l,m> = hbar * sqrt(l(l+1) - m(m+1)) |l,m+1>
        L- |l,m> = hbar * sqrt(l(l+1) - m(m-1)) |l,m-1>
        """
        if raise_op:
            new_m = m + 1
            if new_m > l:
                return {'result': 0, 'message': 'L+ annihilates maximum m state'}
            coefficient = self.HBAR * math.sqrt(l * (l + 1) - m * (m + 1))
        else:
            new_m = m - 1
            if new_m < -l:
                return {'result': 0, 'message': 'L- annihilates minimum m state'}
            coefficient = self.HBAR * math.sqrt(l * (l + 1) - m * (m - 1))

        return {
            'coefficient': coefficient,
            'new_m': new_m,
            'l': l,
            'original_m': m,
            'operator': 'L+' if raise_op else 'L-'
        }

    def total_angular_momentum(self, l: int, s: float) -> Dict[str, Any]:
        """
        Total angular momentum J = L + S.
        j ranges from |l-s| to l+s in integer steps.
        """
        j_min = abs(l - s)
        j_max = l + s
        j_values = []

        j = j_min
        while j <= j_max:
            j_values.append(j)
            j += 1

        return {
            'j_values': j_values,
            'l': l,
            's': s,
            'j_min': j_min,
            'j_max': j_max,
            'num_j_states': len(j_values)
        }

    def clebsch_gordan_selection(self, j1: float, j2: float,
                                  m1: float, m2: float) -> Dict[str, Any]:
        """
        Selection rules for Clebsch-Gordan coefficients.
        m = m1 + m2, and |j1-j2| <= j <= j1+j2
        """
        m = m1 + m2
        j_min = abs(j1 - j2)
        j_max = j1 + j2

        allowed_j = []
        j = j_min
        while j <= j_max:
            if abs(m) <= j:
                allowed_j.append(j)
            j += 1

        return {
            'm_total': m,
            'allowed_j': allowed_j,
            'j_range': (j_min, j_max),
            'j1': j1, 'j2': j2,
            'm1': m1, 'm2': m2
        }

    def magnetic_moment(self, l: int = 0, s: float = 0.5, g_l: float = 1,
                        g_s: float = 2.002) -> Dict[str, Any]:
        """
        Magnetic moment from angular momentum.
        mu = -g * (e/2m) * L (for orbital)
        mu = -g_s * (e/2m) * S (for spin)
        """
        # Bohr magneton
        mu_B = 9.274e-24  # J/T

        mu_orbital = g_l * mu_B * math.sqrt(l * (l + 1)) if l > 0 else 0
        mu_spin = g_s * mu_B * math.sqrt(s * (s + 1))

        return {
            'orbital_moment': mu_orbital,
            'spin_moment': mu_spin,
            'bohr_magneton': mu_B,
            'g_orbital': g_l,
            'g_spin': g_s
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an operators task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'angular_momentum')

        try:
            if operation == 'angular_momentum':
                return self.angular_momentum_eigenvalue(task['l'], task['m'])
            elif operation == 'spin':
                return self.spin_eigenvalue(task['s'], task['m_s'])
            elif operation == 'ladder':
                return self.ladder_operator(
                    task['l'], task['m'], task.get('raise', True)
                )
            elif operation == 'total_j':
                return self.total_angular_momentum(task['l'], task['s'])
            elif operation == 'clebsch_gordan':
                return self.clebsch_gordan_selection(
                    task['j1'], task['j2'], task['m1'], task['m2']
                )
            elif operation == 'magnetic_moment':
                return self.magnetic_moment(
                    task.get('l', 0), task.get('s', 0.5),
                    task.get('g_l', 1), task.get('g_s', 2.002)
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending operators tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.quantum.operators']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for operators tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_operators_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute operators computation via process()."""
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
