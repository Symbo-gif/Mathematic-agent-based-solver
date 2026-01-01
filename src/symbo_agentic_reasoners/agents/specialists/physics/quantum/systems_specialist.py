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
QUANTUM SYSTEMS SPECIALIST (Tier 3)
===================================

Handles quantum systems: hydrogen atom, multi-electron atoms,
quantum wells, and tunneling.

CAPABILITIES:
- Hydrogen atom energy levels
- Bohr model calculations
- Quantum tunneling probability
- Quantum wells and barriers
- Fine structure corrections
"""

from typing import Any, Dict, List, Optional
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class QuantumSystemsSpecialist(BDIAgent):
    """Specialist for quantum systems problems."""

    # Constants
    HBAR = 1.055e-34  # Reduced Planck constant (J*s)
    H = 6.626e-34  # Planck constant
    M_E = 9.109e-31  # Electron mass (kg)
    E_CHARGE = 1.602e-19  # Elementary charge (C)
    EPSILON_0 = 8.854e-12  # Vacuum permittivity
    A_0 = 5.292e-11  # Bohr radius (m)
    RYDBERG = 13.6  # Rydberg energy (eV)

    def __init__(
        self,
        agent_id: str = 'systems_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.quantum.systems',
                agent_id=agent_id,
                algorithm='quantum_systems',
                cost='medium',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='hydrogen_tunneling_wells'
            ))

        print(f"[{agent_id}] Quantum Systems Specialist initialized")
        print(f"  Topics: Hydrogen Atom, Tunneling, Quantum Wells")

    def hydrogen_energy(self, n: int, Z: int = 1) -> Dict[str, Any]:
        """
        Hydrogen-like atom energy levels.
        E_n = -13.6 * Z^2 / n^2 eV
        """
        E_n_eV = -self.RYDBERG * Z**2 / n**2
        E_n_J = E_n_eV * self.E_CHARGE

        return {
            'energy_eV': E_n_eV,
            'energy_J': E_n_J,
            'n': n,
            'Z': Z,
            'ionization_energy_eV': abs(E_n_eV)
        }

    def hydrogen_transition(self, n_initial: int, n_final: int,
                            Z: int = 1) -> Dict[str, Any]:
        """
        Energy and wavelength for hydrogen transitions.
        """
        E_i = -self.RYDBERG * Z**2 / n_initial**2
        E_f = -self.RYDBERG * Z**2 / n_final**2
        dE = E_f - E_i  # Negative for emission

        # Wavelength
        c = 3e8
        wavelength = abs(self.H * c / (dE * self.E_CHARGE))

        series = "unknown"
        if n_final == 1:
            series = "Lyman (UV)"
        elif n_final == 2:
            series = "Balmer (visible)"
        elif n_final == 3:
            series = "Paschen (IR)"
        elif n_final == 4:
            series = "Brackett (IR)"

        return {
            'energy_change_eV': dE,
            'wavelength': wavelength,
            'wavelength_nm': wavelength * 1e9,
            'emission': n_initial > n_final,
            'series': series,
            'n_initial': n_initial,
            'n_final': n_final
        }

    def bohr_radius(self, n: int, Z: int = 1) -> Dict[str, Any]:
        """
        Bohr radius for electron orbit.
        r_n = a_0 * n^2 / Z
        """
        r_n = self.A_0 * n**2 / Z

        # Velocity
        v_n = Z * self.E_CHARGE**2 / (4 * math.pi * self.EPSILON_0 * n * self.HBAR)

        return {
            'radius': r_n,
            'radius_angstrom': r_n * 1e10,
            'velocity': v_n,
            'n': n,
            'Z': Z
        }

    def tunneling_probability(self, E: float, V0: float, L: float,
                              m: float = None) -> Dict[str, Any]:
        """
        Quantum tunneling through rectangular barrier.
        T ≈ exp(-2*kappa*L) for E < V0
        kappa = sqrt(2m(V0-E))/hbar
        """
        if m is None:
            m = self.M_E

        if E >= V0:
            return {
                'transmission': 1.0,
                'message': 'E >= V0: classical transmission',
                'E': E, 'V0': V0
            }

        kappa = math.sqrt(2 * m * (V0 - E)) / self.HBAR
        T = math.exp(-2 * kappa * L)

        return {
            'transmission_probability': T,
            'reflection_probability': 1 - T,
            'decay_constant': kappa,
            'penetration_depth': 1 / kappa,
            'barrier_height': V0,
            'barrier_width': L,
            'particle_energy': E
        }

    def quantum_well_energy(self, n: int, L: float, m: float = None) -> Dict[str, Any]:
        """
        Energy levels in finite square well (approximate).
        Uses infinite well formula as approximation.
        """
        if m is None:
            m = self.M_E

        E_n = (n**2 * math.pi**2 * self.HBAR**2) / (2 * m * L**2)

        return {
            'energy': E_n,
            'energy_eV': E_n / self.E_CHARGE,
            'n': n,
            'well_width': L,
            'mass': m
        }

    def fine_structure_correction(self, n: int, l: int, j: float,
                                   Z: int = 1) -> Dict[str, Any]:
        """
        Fine structure energy correction.
        Includes relativistic and spin-orbit coupling.
        """
        alpha = 1 / 137  # Fine structure constant

        # Relativistic correction
        E_0 = -self.RYDBERG * Z**2 / n**2

        # Fine structure correction
        E_fs = E_0 * alpha**2 * Z**2 / n * (1 / (j + 0.5) - 3 / (4 * n))

        return {
            'unperturbed_energy_eV': E_0,
            'fine_structure_correction_eV': E_fs,
            'corrected_energy_eV': E_0 + E_fs,
            'n': n, 'l': l, 'j': j,
            'fine_structure_constant': alpha
        }

    def zeeman_splitting(self, B: float, m_l: int, m_s: float) -> Dict[str, Any]:
        """
        Zeeman effect energy splitting.
        dE = mu_B * B * (m_l + 2*m_s)
        """
        mu_B = 9.274e-24  # Bohr magneton

        dE = mu_B * B * (m_l + 2 * m_s)

        return {
            'energy_shift': dE,
            'energy_shift_eV': dE / self.E_CHARGE,
            'magnetic_field': B,
            'm_l': m_l,
            'm_s': m_s,
            'bohr_magneton': mu_B
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a quantum systems task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'hydrogen_energy')

        try:
            if operation == 'hydrogen_energy':
                return self.hydrogen_energy(task['n'], task.get('Z', 1))
            elif operation == 'transition':
                return self.hydrogen_transition(
                    task['n_initial'], task['n_final'], task.get('Z', 1)
                )
            elif operation == 'bohr_radius':
                return self.bohr_radius(task['n'], task.get('Z', 1))
            elif operation == 'tunneling':
                return self.tunneling_probability(
                    task['E'], task['V0'], task['L'], task.get('m')
                )
            elif operation == 'well_energy':
                return self.quantum_well_energy(
                    task['n'], task['L'], task.get('m')
                )
            elif operation == 'fine_structure':
                return self.fine_structure_correction(
                    task['n'], task['l'], task['j'], task.get('Z', 1)
                )
            elif operation == 'zeeman':
                return self.zeeman_splitting(
                    task['B'], task['m_l'], task['m_s']
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending quantum systems tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.quantum.systems']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for quantum systems tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_systems_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute quantum systems computation via process()."""
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
        >>> specialist = QuantumSystemsSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
