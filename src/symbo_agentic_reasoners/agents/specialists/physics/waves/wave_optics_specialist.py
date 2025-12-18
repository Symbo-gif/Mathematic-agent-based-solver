# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
WAVE OPTICS SPECIALIST (Tier 3)
===============================

Wave physics and optics calculations.

CAPABILITIES:
------------
- Wave equations and properties
- Interference and diffraction
- Snell's law and refraction
- Lens equations
- Polarization
- Standing waves

NO SYMPY - All mathematical operations use native implementations.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.wave_optics')


@dataclass
class WaveProperties:
    """Properties of a wave."""
    amplitude: float
    frequency: float  # Hz
    wavelength: float  # m
    velocity: float  # m/s
    period: float  # s
    wave_number: float  # rad/m
    angular_frequency: float  # rad/s


class WaveOpticsSpecialist(BDIAgent):
    """
    Wave Optics Specialist - Wave Physics and Optics

    DIRECTIVE:
    ---------
    Provide wave physics and optics calculations.

    OPERATIONS:
    ----------
    - wave_properties: Calculate wave properties
    - snells_law: Refraction calculations
    - lens_equation: Thin lens calculations
    - diffraction_single_slit: Single slit diffraction
    - interference_double_slit: Young's double slit
    """

    def __init__(
        self,
        agent_id: str = "wave_optics_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "wave_optics_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'calculations': 0}

        # Physical constants
        self.c = 299792458  # Speed of light in vacuum (m/s)
        self.h = 6.62607015e-34  # Planck constant (J·s)

    def _register_services(self):
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="wave_optics",
                description="Wave physics and optics"
            ))

    # ==================== WAVE PROPERTIES ====================

    def wave_properties(
        self,
        frequency: Optional[float] = None,
        wavelength: Optional[float] = None,
        velocity: Optional[float] = None,
        amplitude: float = 1.0,
    ) -> WaveProperties:
        """
        Calculate wave properties from given parameters.

        Provide any two of: frequency, wavelength, velocity.
        Uses v = fλ relationship.
        """
        self._stats['calculations'] += 1

        # Calculate missing parameter
        if frequency and wavelength:
            velocity = frequency * wavelength
        elif frequency and velocity:
            wavelength = velocity / frequency
        elif wavelength and velocity:
            frequency = velocity / wavelength
        else:
            raise ValueError("Need at least two of: frequency, wavelength, velocity")

        period = 1 / frequency
        wave_number = 2 * math.pi / wavelength
        angular_frequency = 2 * math.pi * frequency

        return WaveProperties(
            amplitude=amplitude,
            frequency=frequency,
            wavelength=wavelength,
            velocity=velocity,
            period=period,
            wave_number=wave_number,
            angular_frequency=angular_frequency
        )

    def wave_displacement(
        self,
        amplitude: float,
        angular_frequency: float,
        wave_number: float,
        x: float,
        t: float,
        phase: float = 0.0,
    ) -> float:
        """Calculate wave displacement y(x,t) = A sin(kx - ωt + φ)."""
        self._stats['calculations'] += 1
        return amplitude * math.sin(wave_number * x - angular_frequency * t + phase)

    # ==================== OPTICS ====================

    def snells_law(
        self,
        n1: float,
        n2: float,
        theta1: Optional[float] = None,
        theta2: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Snell's law: n1 sin(θ1) = n2 sin(θ2)

        Args:
            n1: Refractive index of medium 1
            n2: Refractive index of medium 2
            theta1: Angle of incidence (radians)
            theta2: Angle of refraction (radians)

        Returns:
            Dict with theta1, theta2, and critical_angle if applicable
        """
        self._stats['calculations'] += 1

        result = {'n1': n1, 'n2': n2}

        if theta1 is not None:
            sin_theta2 = (n1 / n2) * math.sin(theta1)
            if abs(sin_theta2) <= 1:
                result['theta1'] = theta1
                result['theta2'] = math.asin(sin_theta2)
            else:
                result['total_internal_reflection'] = True
                result['theta1'] = theta1

        elif theta2 is not None:
            sin_theta1 = (n2 / n1) * math.sin(theta2)
            if abs(sin_theta1) <= 1:
                result['theta1'] = math.asin(sin_theta1)
                result['theta2'] = theta2

        # Critical angle (if n1 > n2)
        if n1 > n2:
            result['critical_angle'] = math.asin(n2 / n1)

        return result

    def brewster_angle(self, n1: float, n2: float) -> float:
        """Brewster's angle for complete polarization."""
        self._stats['calculations'] += 1
        return math.atan(n2 / n1)

    def lens_equation(
        self,
        focal_length: Optional[float] = None,
        object_distance: Optional[float] = None,
        image_distance: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Thin lens equation: 1/f = 1/do + 1/di

        Args:
            focal_length: f
            object_distance: do (positive for real object)
            image_distance: di (positive for real image)

        Returns:
            Dict with f, do, di, and magnification
        """
        self._stats['calculations'] += 1

        result = {}

        if focal_length and object_distance:
            image_distance = 1 / (1 / focal_length - 1 / object_distance)
        elif focal_length and image_distance:
            object_distance = 1 / (1 / focal_length - 1 / image_distance)
        elif object_distance and image_distance:
            focal_length = 1 / (1 / object_distance + 1 / image_distance)

        result['focal_length'] = focal_length
        result['object_distance'] = object_distance
        result['image_distance'] = image_distance

        if object_distance:
            result['magnification'] = -image_distance / object_distance
            result['image_real'] = image_distance > 0
            result['image_inverted'] = result['magnification'] < 0

        return result

    def mirror_equation(
        self,
        focal_length: Optional[float] = None,
        object_distance: Optional[float] = None,
        image_distance: Optional[float] = None,
    ) -> Dict[str, float]:
        """Mirror equation (same as lens equation)."""
        return self.lens_equation(focal_length, object_distance, image_distance)

    # ==================== DIFFRACTION & INTERFERENCE ====================

    def single_slit_diffraction(
        self,
        wavelength: float,
        slit_width: float,
        angle: float,
    ) -> Dict[str, float]:
        """
        Single slit diffraction intensity.

        Args:
            wavelength: Wavelength of light
            slit_width: Width of slit
            angle: Angle from central maximum (radians)

        Returns:
            Dict with intensity ratio and whether it's a minimum
        """
        self._stats['calculations'] += 1

        beta = (math.pi * slit_width * math.sin(angle)) / wavelength

        if abs(beta) < 1e-10:
            intensity_ratio = 1.0
        else:
            intensity_ratio = (math.sin(beta) / beta) ** 2

        # Minima occur at sin(θ) = mλ/a for m = ±1, ±2, ...
        m = slit_width * math.sin(angle) / wavelength
        is_minimum = abs(m - round(m)) < 0.01 and abs(round(m)) >= 1

        return {
            'intensity_ratio': intensity_ratio,
            'beta': beta,
            'is_minimum': is_minimum,
            'order': round(m) if is_minimum else None
        }

    def double_slit_interference(
        self,
        wavelength: float,
        slit_separation: float,
        screen_distance: float,
        y_position: float,
    ) -> Dict[str, float]:
        """
        Young's double slit interference.

        Args:
            wavelength: Wavelength of light
            slit_separation: Distance between slits (d)
            screen_distance: Distance to screen (L)
            y_position: Position on screen from center

        Returns:
            Dict with path difference, phase difference, and intensity
        """
        self._stats['calculations'] += 1

        angle = math.atan(y_position / screen_distance)
        path_difference = slit_separation * math.sin(angle)
        phase_difference = (2 * math.pi * path_difference) / wavelength

        # Intensity proportional to cos²(δ/2)
        intensity_ratio = math.cos(phase_difference / 2) ** 2

        # Fringe order
        m = path_difference / wavelength

        return {
            'path_difference': path_difference,
            'phase_difference': phase_difference,
            'intensity_ratio': intensity_ratio,
            'fringe_order': m,
            'is_maximum': abs(m - round(m)) < 0.01,
            'is_minimum': abs(m - round(m) - 0.5) < 0.01 or abs(m - round(m) + 0.5) < 0.01
        }

    def fringe_spacing(
        self,
        wavelength: float,
        slit_separation: float,
        screen_distance: float,
    ) -> float:
        """Calculate fringe spacing in double slit experiment."""
        self._stats['calculations'] += 1
        return wavelength * screen_distance / slit_separation

    # ==================== STANDING WAVES ====================

    def standing_wave_frequencies(
        self,
        length: float,
        velocity: float,
        boundary_type: str = 'fixed-fixed',
        n_harmonics: int = 5,
    ) -> List[float]:
        """
        Calculate standing wave frequencies.

        Args:
            length: Length of medium
            velocity: Wave velocity in medium
            boundary_type: 'fixed-fixed', 'open-open', or 'fixed-open'
            n_harmonics: Number of harmonics to calculate

        Returns:
            List of harmonic frequencies
        """
        self._stats['calculations'] += 1

        frequencies = []

        if boundary_type in ['fixed-fixed', 'open-open']:
            # f_n = n * v / (2L) for n = 1, 2, 3, ...
            for n in range(1, n_harmonics + 1):
                frequencies.append(n * velocity / (2 * length))

        elif boundary_type == 'fixed-open':
            # f_n = n * v / (4L) for n = 1, 3, 5, ... (odd only)
            for n in range(1, 2 * n_harmonics, 2):
                frequencies.append(n * velocity / (4 * length))

        return frequencies[:n_harmonics]

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Perform process message operation.

        Args:
        message

        Returns:
        Result of the operation

        Example:
        >>> specialist = WaveOpticsSpecialist()
        >>> result = specialist.process_message(...)
        # Returns result
        """
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'wave_properties': lambda p: self.wave_properties(**p),
            'snells_law': lambda p: self.snells_law(**p),
            'lens_equation': lambda p: self.lens_equation(**p),
            'single_slit_diffraction': lambda p: self.single_slit_diffraction(**p),
            'double_slit_interference': lambda p: self.double_slit_interference(**p),
        }

        if action in handlers:
            result = handlers[action](params)
            return {'status': 'success', 'result': result}
        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Compute get stats using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = WaveOpticsSpecialist()
        >>> result = specialist.get_stats()
        # Returns computed result

        """
        return dict(self._stats)

    def update_beliefs(self):
        """Perform update beliefs operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = WaveOpticsSpecialist()
        >>> result = specialist.update_beliefs(...)
        # Returns result
        """
        pass

    def deliberate(self) -> List:
        """Perform deliberate operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = WaveOpticsSpecialist()
        >>> result = specialist.deliberate(...)
        # Returns result
        """
        return []

    def execute_step(self, intention):
        """Perform execute step operation.

        Args:
        intention

        Returns:
        Result of the operation

        Example:
        >>> specialist = WaveOpticsSpecialist()
        >>> result = specialist.execute_step(...)
        # Returns result
        """
        pass


__all__ = [
    'WaveOpticsSpecialist',
    'WaveProperties',
]
