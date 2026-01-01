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
SPECTRAL ANALYSIS SPECIALIST (Tier 3)
======================================

Power spectral density and frequency domain analysis.

CAPABILITIES:
------------
- Periodogram estimation
- Welch's method (averaged periodogram)
- Power spectral density (PSD)
- Dominant frequency identification
- Cross-spectral density
- Coherence function
- Band-pass filtering

ALGORITHMS:
-----------
Native implementation using FFT - NO external dependencies

1. Periodogram: S(f) = (1/N) |FFT(x)|^2
2. Welch's method: Average of periodograms from overlapping windows
3. Cross-spectrum: S_xy(f) = FFT(x) * conj(FFT(y))
4. Coherence: C_xy(f) = |S_xy(f)|^2 / (S_xx(f) * S_yy(f))
"""

import logging
import math
import cmath
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.spectral_analysis')


@dataclass
class SpectralResult:
    """Result of spectral analysis."""
    frequencies: List[float]
    power: List[float]
    phase: Optional[List[float]] = None
    method: str = 'periodogram'


@dataclass
class CoherenceResult:
    """Result of coherence analysis."""
    frequencies: List[float]
    coherence: List[float]
    cross_spectrum: List[complex]


class SpectralAnalysisSpecialist(BDIAgent):
    """
    Spectral Analysis Specialist - Frequency Domain Analysis

    DIRECTIVE:
    ---------
    Perform spectral analysis of time series data using
    frequency domain methods.

    OPERATIONS:
    ----------
    - compute_periodogram: Basic periodogram
    - welch_method: Welch's averaged periodogram
    - compute_spectral_density: PSD estimation
    - identify_dominant_frequencies: Peak detection
    - compute_cross_spectrum: Cross-spectral density
    - compute_coherence: Coherence function
    - filter_frequency_band: Band-pass filtering
    """

    def __init__(
        self,
        agent_id: str = 'spectral_analysis_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = 'spectral_analysis_specialist'
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self._register_services()
        self._stats = {'spectra_computed': 0, 'coherence_computed': 0}

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type='math.statistics.timeseries.spectral_analysis',
                    description='Spectral analysis and frequency domain methods'
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== FFT IMPLEMENTATION ====================

    def _fft_recursive(self, x: List[complex]) -> List[complex]:
        """Recursive Cooley-Tukey FFT implementation."""
        N = len(x)

        if N <= 1:
            return x

        # Split into even and odd
        even = self._fft_recursive(x[0::2])
        odd = self._fft_recursive(x[1::2])

        # Combine
        result = [complex(0)] * N
        for k in range(N // 2):
            t = cmath.exp(-2j * math.pi * k / N) * odd[k]
            result[k] = even[k] + t
            result[k + N // 2] = even[k] - t

        return result

    def _ifft_recursive(self, x: List[complex]) -> List[complex]:
        """Inverse FFT using conjugate trick."""
        N = len(x)
        # Take conjugate, apply FFT, take conjugate, divide by N
        conjugated = [c.conjugate() for c in x]
        fft_result = self._fft_recursive(conjugated)
        return [c.conjugate() / N for c in fft_result]

    def _pad_to_power_of_2(self, data: List[float]) -> List[complex]:
        """Pad data to next power of 2 for FFT."""
        n = len(data)
        n_fft = 1
        while n_fft < n:
            n_fft *= 2

        padded = [complex(x) for x in data] + [complex(0)] * (n_fft - n)
        return padded

    # ==================== PERIODOGRAM ====================

    def compute_periodogram(
        self,
        data: List[float],
        sample_rate: float = 1.0,
    ) -> SpectralResult:
        """
        Compute periodogram (raw power spectral density estimate).

        Periodogram: P(f) = (1/N) |FFT(x)|^2

        Args:
            data: Time series data
            sample_rate: Sampling rate in Hz

        Returns:
            SpectralResult with power spectral density
        """
        self._stats['spectra_computed'] += 1

        N = len(data)
        if N == 0:
            return SpectralResult(frequencies=[], power=[], method='periodogram')

        # Apply FFT
        padded = self._pad_to_power_of_2(data)
        N_fft = len(padded)
        fft_result = self._fft_recursive(padded)

        # Compute power (one-sided for real signals)
        power = [(abs(fft_result[k]) ** 2) / N for k in range(N_fft // 2 + 1)]

        # Frequencies
        frequencies = [k * sample_rate / N_fft for k in range(N_fft // 2 + 1)]

        # Phase
        phase = [cmath.phase(fft_result[k]) for k in range(N_fft // 2 + 1)]

        return SpectralResult(
            frequencies=frequencies,
            power=power,
            phase=phase,
            method='periodogram'
        )

    # ==================== WELCH'S METHOD ====================

    def welch_method(
        self,
        data: List[float],
        window_size: int = 256,
        overlap: float = 0.5,
        sample_rate: float = 1.0,
    ) -> SpectralResult:
        """
        Welch's method for power spectral density estimation.

        Averages periodograms from overlapping windowed segments.

        Args:
            data: Time series data
            window_size: Size of each window
            overlap: Overlap ratio (0-1)
            sample_rate: Sampling rate in Hz

        Returns:
            SpectralResult with averaged PSD
        """
        self._stats['spectra_computed'] += 1

        N = len(data)
        if N < window_size:
            # Fall back to periodogram
            return self.compute_periodogram(data, sample_rate)

        # Calculate step size
        step = int(window_size * (1 - overlap))
        if step == 0:
            step = 1

        # Apply Hanning window
        window = [0.5 * (1 - math.cos(2 * math.pi * n / (window_size - 1)))
                  for n in range(window_size)]

        # Compute periodograms for each window
        n_segments = 0
        accumulated_power = None

        for start in range(0, N - window_size + 1, step):
            segment = data[start:start + window_size]

            # Apply window
            windowed = [segment[i] * window[i] for i in range(window_size)]

            # Compute periodogram
            result = self.compute_periodogram(windowed, sample_rate)

            if accumulated_power is None:
                accumulated_power = result.power[:]
            else:
                accumulated_power = [accumulated_power[i] + result.power[i]
                                    for i in range(len(result.power))]

            n_segments += 1

        # Average
        if n_segments > 0 and accumulated_power:
            averaged_power = [p / n_segments for p in accumulated_power]
        else:
            averaged_power = []

        # Use frequencies from last segment
        frequencies = result.frequencies if result else []

        return SpectralResult(
            frequencies=frequencies,
            power=averaged_power,
            method='welch'
        )

    # ==================== SPECTRAL DENSITY ====================

    def compute_spectral_density(
        self,
        data: List[float],
        method: str = 'welch',
        sample_rate: float = 1.0,
        **kwargs
    ) -> SpectralResult:
        """
        Compute power spectral density using specified method.

        Args:
            data: Time series data
            method: 'periodogram' or 'welch'
            sample_rate: Sampling rate in Hz
            **kwargs: Additional parameters for method

        Returns:
            SpectralResult with PSD
        """
        if method == 'periodogram':
            return self.compute_periodogram(data, sample_rate)
        elif method == 'welch':
            window_size = kwargs.get('window_size', min(256, len(data) // 4))
            overlap = kwargs.get('overlap', 0.5)
            return self.welch_method(data, window_size, overlap, sample_rate)
        else:
            raise ValueError(f"Unknown method: {method}")

    # ==================== DOMINANT FREQUENCIES ====================

    def identify_dominant_frequencies(
        self,
        spectrum: SpectralResult,
        n_peaks: int = 5,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Identify dominant frequencies in spectrum.

        Args:
            spectrum: SpectralResult from spectral analysis
            n_peaks: Number of peaks to identify
            threshold: Minimum power threshold (default: mean + 2*std)

        Returns:
            Dict with peak frequencies, powers, and indices
        """
        power = spectrum.power
        frequencies = spectrum.frequencies

        if not power:
            return {'frequencies': [], 'powers': [], 'indices': []}

        # Calculate threshold
        if threshold is None:
            mean_power = sum(power) / len(power)
            std_power = math.sqrt(sum((p - mean_power) ** 2 for p in power) / len(power))
            threshold = mean_power + 2 * std_power

        # Find peaks (local maxima above threshold)
        peaks = []
        for i in range(1, len(power) - 1):
            if power[i] > power[i-1] and power[i] > power[i+1] and power[i] > threshold:
                peaks.append((i, frequencies[i], power[i]))

        # Sort by power (descending)
        peaks.sort(key=lambda x: x[2], reverse=True)

        # Return top n_peaks
        peaks = peaks[:n_peaks]

        return {
            'indices': [p[0] for p in peaks],
            'frequencies': [p[1] for p in peaks],
            'powers': [p[2] for p in peaks],
        }

    # ==================== CROSS-SPECTRUM ====================

    def compute_cross_spectrum(
        self,
        data1: List[float],
        data2: List[float],
        sample_rate: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Compute cross-spectral density between two signals.

        S_xy(f) = FFT(x) * conj(FFT(y))

        Args:
            data1: First time series
            data2: Second time series
            sample_rate: Sampling rate in Hz

        Returns:
            Dict with frequencies, cross_spectrum, magnitude, phase
        """
        self._stats['spectra_computed'] += 1

        N = min(len(data1), len(data2))
        if N == 0:
            return {
                'frequencies': [],
                'cross_spectrum': [],
                'magnitude': [],
                'phase': []
            }

        # Truncate to same length
        data1 = data1[:N]
        data2 = data2[:N]

        # Pad to power of 2
        padded1 = self._pad_to_power_of_2(data1)
        padded2 = self._pad_to_power_of_2(data2)
        N_fft = len(padded1)

        # FFT both signals
        fft1 = self._fft_recursive(padded1)
        fft2 = self._fft_recursive(padded2)

        # Cross-spectrum (one-sided)
        cross_spectrum = [fft1[k] * fft2[k].conjugate() for k in range(N_fft // 2 + 1)]

        # Magnitude and phase
        magnitude = [abs(c) for c in cross_spectrum]
        phase = [cmath.phase(c) for c in cross_spectrum]

        # Frequencies
        frequencies = [k * sample_rate / N_fft for k in range(N_fft // 2 + 1)]

        return {
            'frequencies': frequencies,
            'cross_spectrum': cross_spectrum,
            'magnitude': magnitude,
            'phase': phase,
        }

    # ==================== COHERENCE ====================

    def compute_coherence(
        self,
        data1: List[float],
        data2: List[float],
        sample_rate: float = 1.0,
    ) -> CoherenceResult:
        """
        Compute coherence function between two signals.

        Coherence: C_xy(f) = |S_xy(f)|^2 / (S_xx(f) * S_yy(f))

        Args:
            data1: First time series
            data2: Second time series
            sample_rate: Sampling rate in Hz

        Returns:
            CoherenceResult with frequencies and coherence
        """
        self._stats['coherence_computed'] += 1

        # Cross-spectrum
        cross_result = self.compute_cross_spectrum(data1, data2, sample_rate)

        # Auto-spectra
        auto1 = self.compute_periodogram(data1, sample_rate)
        auto2 = self.compute_periodogram(data2, sample_rate)

        # Coherence
        coherence = []
        for i in range(len(cross_result['cross_spectrum'])):
            cross_power = abs(cross_result['cross_spectrum'][i]) ** 2
            auto_power1 = auto1.power[i] if i < len(auto1.power) else 1e-10
            auto_power2 = auto2.power[i] if i < len(auto2.power) else 1e-10

            denom = auto_power1 * auto_power2
            if denom > 0:
                coh = cross_power / denom
                coherence.append(min(coh, 1.0))  # Clamp to [0, 1]
            else:
                coherence.append(0.0)

        return CoherenceResult(
            frequencies=cross_result['frequencies'],
            coherence=coherence,
            cross_spectrum=cross_result['cross_spectrum']
        )

    # ==================== FILTERING ====================

    def filter_frequency_band(
        self,
        data: List[float],
        low_freq: float,
        high_freq: float,
        sample_rate: float = 1.0,
    ) -> List[float]:
        """
        Band-pass filter in frequency domain.

        Args:
            data: Time series data
            low_freq: Low cutoff frequency (Hz)
            high_freq: High cutoff frequency (Hz)
            sample_rate: Sampling rate in Hz

        Returns:
            Filtered time series
        """
        N = len(data)
        if N == 0:
            return []

        # Pad to power of 2
        padded = self._pad_to_power_of_2(data)
        N_fft = len(padded)

        # FFT
        fft_result = self._fft_recursive(padded)

        # Create filter mask
        for k in range(N_fft):
            freq = k * sample_rate / N_fft
            # Handle negative frequencies (second half)
            if k > N_fft // 2:
                freq = (k - N_fft) * sample_rate / N_fft

            # Zero out frequencies outside band
            if not (low_freq <= abs(freq) <= high_freq):
                fft_result[k] = complex(0, 0)

        # Inverse FFT
        filtered = self._ifft_recursive(fft_result)

        # Return real part, truncated to original length
        return [x.real for x in filtered[:N]]

    # ==================== BDI INTEGRATION ====================

    def process(self, task_entry):
        """Process incoming task."""
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry

        task_type = metadata.get('task_type', 'compute_periodogram')
        params = metadata.get('params', {})

        handlers = {
            'compute_periodogram': lambda p: self.compute_periodogram(**p),
            'welch_method': lambda p: self.welch_method(**p),
            'compute_spectral_density': lambda p: self.compute_spectral_density(**p),
            'identify_dominant_frequencies': lambda p: self.identify_dominant_frequencies(**p),
            'compute_cross_spectrum': lambda p: self.compute_cross_spectrum(**p),
            'compute_coherence': lambda p: self.compute_coherence(**p),
            'filter_frequency_band': lambda p: self.filter_frequency_band(**p),
        }

        if task_type in handlers:
            result = handlers[task_type](params)
            return {'status': 'success', 'result': result}

        return {
            'operation': 'spectral analysis',
            'explanation': 'Power spectral density, periodogram',
            'status': 'success'
        }

    def update_beliefs(self):
        """Update beliefs from blackboard."""
        if self.blackboard and hasattr(self.blackboard, 'query_entries'):
            entries = self.blackboard.query_entries(
                tags=['spectral', 'frequency'],
                status='pending'
            )
            for entry in entries:
                self.add_belief('pending_spectral_task', entry, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on beliefs."""
        intentions = []

        if self.tasks_executed > 40:
            intentions.append(Intention(
                goal='optimize_fft',
                plan=['cache_twiddle_factors', 'optimize_memory'],
                priority=2
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute intention step."""
        if intention.goal == 'optimize_fft':
            logger.info("Optimizing FFT computations")

    def get_statistics(self):
        """Get agent statistics."""
        return {
            **super().get_statistics(),
            'tasks_executed': self.tasks_executed,
            **self._stats
        }


__all__ = [
    'SpectralAnalysisSpecialist',
    'SpectralResult',
    'CoherenceResult',
]
