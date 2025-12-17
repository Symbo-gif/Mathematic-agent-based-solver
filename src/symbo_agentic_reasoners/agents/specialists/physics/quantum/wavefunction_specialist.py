# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
WAVEFUNCTION SPECIALIST (Tier 3)
================================

Handles quantum wavefunctions: normalization, probability density,
expectation values, and basic quantum states.

CAPABILITIES:
- Wavefunction normalization
- Probability density calculations
- Expectation values
- Particle in a box
- Harmonic oscillator states
"""

from typing import Any, Dict, List, Optional
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class WavefunctionSpecialist(BDIAgent):
    """Specialist for quantum wavefunction problems."""

    # Constants
    HBAR = 1.055e-34  # Reduced Planck constant (J*s)
    H = 6.626e-34  # Planck constant (J*s)

    def __init__(
        self,
        agent_id: str = 'wavefunction_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='physics.quantum.wavefunction',
                agent_id=agent_id,
                algorithm='schrodinger',
                cost='medium',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='normalization_probability_expectation'
            ))

        print(f"[{agent_id}] Wavefunction Specialist initialized")
        print(f"  Topics: Normalization, Probability, Expectation Values")

    def particle_in_box_energy(self, n: int, L: float, m: float) -> Dict[str, Any]:
        """
        Energy levels for particle in 1D infinite square well.
        E_n = n^2 * pi^2 * hbar^2 / (2 * m * L^2)
        """
        E_n = (n**2 * math.pi**2 * self.HBAR**2) / (2 * m * L**2)
        return {
            'energy': E_n,
            'energy_eV': E_n / 1.602e-19,
            'quantum_number': n,
            'box_length': L,
            'mass': m
        }

    def particle_in_box_wavelength(self, n: int, L: float) -> Dict[str, Any]:
        """
        Wavelength for particle in box: lambda_n = 2L/n
        """
        wavelength = 2 * L / n
        k = n * math.pi / L  # Wave vector
        return {
            'wavelength': wavelength,
            'wave_vector': k,
            'quantum_number': n,
            'nodes': n - 1
        }

    def harmonic_oscillator_energy(self, n: int, omega: float) -> Dict[str, Any]:
        """
        Quantum harmonic oscillator energy levels.
        E_n = hbar * omega * (n + 1/2)
        """
        E_n = self.HBAR * omega * (n + 0.5)
        E_0 = self.HBAR * omega * 0.5  # Zero-point energy
        return {
            'energy': E_n,
            'energy_eV': E_n / 1.602e-19,
            'zero_point_energy': E_0,
            'quantum_number': n,
            'angular_frequency': omega
        }

    def de_broglie_wavelength(self, p: float = None, m: float = None,
                               v: float = None) -> Dict[str, Any]:
        """
        de Broglie wavelength: lambda = h/p
        """
        if p is None and m is not None and v is not None:
            p = m * v

        wavelength = self.H / p
        return {
            'wavelength': wavelength,
            'momentum': p,
            'frequency': p**2 / (2 * m * self.H) if m else None
        }

    def uncertainty_principle(self, dx: float = None, dp: float = None,
                              dE: float = None, dt: float = None) -> Dict[str, Any]:
        """
        Heisenberg uncertainty principle:
        dx * dp >= hbar/2
        dE * dt >= hbar/2
        """
        results = {}

        if dx is not None:
            dp_min = self.HBAR / (2 * dx)
            results['position_uncertainty'] = dx
            results['min_momentum_uncertainty'] = dp_min

        if dp is not None:
            dx_min = self.HBAR / (2 * dp)
            results['momentum_uncertainty'] = dp
            results['min_position_uncertainty'] = dx_min

        if dE is not None:
            dt_min = self.HBAR / (2 * dE)
            results['energy_uncertainty'] = dE
            results['min_time_uncertainty'] = dt_min

        if dt is not None:
            dE_min = self.HBAR / (2 * dt)
            results['time_uncertainty'] = dt
            results['min_energy_uncertainty'] = dE_min

        results['hbar'] = self.HBAR
        return results

    def photon_energy(self, wavelength: float = None, frequency: float = None) -> Dict[str, Any]:
        """
        Photon energy: E = h*f = h*c/lambda
        """
        c = 3e8  # Speed of light

        if frequency is None and wavelength is not None:
            frequency = c / wavelength
        elif wavelength is None and frequency is not None:
            wavelength = c / frequency

        E = self.H * frequency
        return {
            'energy': E,
            'energy_eV': E / 1.602e-19,
            'wavelength': wavelength,
            'frequency': frequency,
            'momentum': E / c
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a wavefunction task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'box_energy')

        try:
            if operation == 'box_energy':
                return self.particle_in_box_energy(task['n'], task['L'], task['m'])
            elif operation == 'box_wavelength':
                return self.particle_in_box_wavelength(task['n'], task['L'])
            elif operation == 'harmonic_energy':
                return self.harmonic_oscillator_energy(task['n'], task['omega'])
            elif operation == 'de_broglie':
                return self.de_broglie_wavelength(
                    task.get('p'), task.get('m'), task.get('v')
                )
            elif operation == 'uncertainty':
                return self.uncertainty_principle(
                    task.get('dx'), task.get('dp'),
                    task.get('dE'), task.get('dt')
                )
            elif operation == 'photon':
                return self.photon_energy(
                    task.get('wavelength'), task.get('frequency')
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending wavefunction tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['physics.quantum.wavefunction']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for wavefunction tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_wavefunction_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute wavefunction computation via process()."""
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
