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
FOURIER ANALYSIS SPECIALIST (Tier 3)
====================================

Performs Fourier analysis including series expansion, transforms, and convolution.

CAPABILITIES:
------------
- Fourier series expansion (sine, cosine, complex)
- Discrete Fourier Transform (DFT)
- Inverse DFT
- Convolution and correlation
- Power spectral density
- Signal filtering operations

ALGORITHMS:
-----------
Native implementation - NO SymPy or SciPy dependency

1. Fourier Series: f(x) = a0/2 + sum(an*cos(nx) + bn*sin(nx))
2. DFT: X[k] = sum(x[n] * exp(-2*pi*i*k*n/N))
3. IDFT: x[n] = (1/N) * sum(X[k] * exp(2*pi*i*k*n/N))
4. Convolution: (f*g)(t) = integral(f(tau)*g(t-tau), tau)
5. Correlation: (f*g)(t) = integral(f(tau)*g(tau+t), tau)

REFERENCE:
---------
- Mathematical Capability Gap Analysis: Signal processing at 45%
- Target: 70% capability for Fourier methods
"""

import logging
import math
import cmath
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass

# NO SYMPY - Use native symbolic engine
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, sympify, simplify, parse_expr, Expr, Integer, Float,
    Sin, Cos, Exp, Log, Pow, Add, Mul, Rational, pi as native_pi
)
from symbo_agentic_reasoners.core.calculus import (
    integrate as native_integrate,
)
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.fallback_tracker import track_computation, get_tracker

logger = logging.getLogger('symbo_agentic_reasoners.specialists.fourier')


@dataclass
class FourierSeriesResult:
    """Result of Fourier series expansion."""
    a0: Union[float, Expr]  # Constant term
    an: List[Union[float, Expr]]  # Cosine coefficients
    bn: List[Union[float, Expr]]  # Sine coefficients
    n_terms: int
    period: float
    series_expr: Optional[Expr] = None
    converged: bool = True


@dataclass
class DFTResult:
    """Result of Discrete Fourier Transform."""
    magnitudes: List[float]
    phases: List[float]
    frequencies: List[float]
    complex_coeffs: List[complex]
    n_samples: int
    sample_rate: Optional[float] = None


class FourierAnalysisSpecialist(BDIAgent):
    """
    Fourier Analysis Specialist - Signal Processing and Series Expansion

    DIRECTIVE:
    ---------
    Perform Fourier analysis on functions and signals using
    native mathematical algorithms.

    OPERATIONS:
    ----------
    - fourier_series: Compute Fourier series coefficients
    - dft: Discrete Fourier Transform
    - idft: Inverse Discrete Fourier Transform
    - convolve: Convolution of signals
    - correlate: Correlation of signals
    - power_spectrum: Power spectral density
    """

    def __init__(
        self,
        agent_id: str = "fourier_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)

        # Set additional attributes
        self.agent_type = "fourier_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard

        # Register services
        self._register_services()

        # Track computation stats
        self._stats = {
            'series_computed': 0,
            'transforms_computed': 0,
            'convolutions_computed': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="fourier_series",
                    description="Compute Fourier series expansion"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="dft",
                    description="Discrete Fourier Transform"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="convolution",
                    description="Signal convolution"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== FOURIER SERIES ====================

    def fourier_series(
        self,
        func: Union[str, Callable],
        var: str = 'x',
        period: float = 2 * math.pi,
        n_terms: int = 10,
    ) -> FourierSeriesResult:
        """
        Compute Fourier series coefficients for a periodic function.

        f(x) = a0/2 + sum_{n=1}^{N} [an*cos(n*omega*x) + bn*sin(n*omega*x)]

        where omega = 2*pi/period

        Args:
            func: Function as string expression or callable
            var: Independent variable name
            period: Period of the function (default 2*pi)
            n_terms: Number of terms to compute

        Returns:
            FourierSeriesResult with coefficients
        """
        try:
            omega = 2 * math.pi / period
            half_period = period / 2

            # Get function evaluator
            if isinstance(func, str):
                eval_func = self._create_evaluator(func, var)
            else:
                eval_func = func

            # Compute a0 (constant term)
            a0 = self._compute_a0(eval_func, -half_period, half_period, period)

            # Compute an (cosine coefficients) and bn (sine coefficients)
            an = []
            bn = []

            for n in range(1, n_terms + 1):
                an_val = self._compute_an(eval_func, n, omega, -half_period, half_period, period)
                bn_val = self._compute_bn(eval_func, n, omega, -half_period, half_period, period)
                an.append(an_val)
                bn.append(bn_val)

            # Build series expression
            series_expr = self._build_series_expr(a0, an, bn, var, omega)

            self._stats['series_computed'] += 1

            return FourierSeriesResult(
                a0=a0,
                an=an,
                bn=bn,
                n_terms=n_terms,
                period=period,
                series_expr=series_expr,
                converged=True
            )

        except Exception as e:
            logger.warning(f"Fourier series computation failed: {e}")
            return FourierSeriesResult(
                a0=0, an=[], bn=[], n_terms=0, period=period, converged=False
            )

    def _compute_a0(self, func, a: float, b: float, period: float) -> float:
        """Compute a0 = (1/T) * integral(f(x), x, -T/2, T/2)."""
        integral = self._numerical_integrate(func, a, b)
        return (2 / period) * integral

    def _compute_an(self, func, n: int, omega: float, a: float, b: float, period: float) -> float:
        """Compute an = (2/T) * integral(f(x)*cos(n*omega*x), x, -T/2, T/2)."""
        def integrand(x):
            """Perform integrand operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.integrand(...)
            """
            return func(x) * math.cos(n * omega * x)
        integral = self._numerical_integrate(integrand, a, b)
        return (2 / period) * integral

    def _compute_bn(self, func, n: int, omega: float, a: float, b: float, period: float) -> float:
        """Compute bn = (2/T) * integral(f(x)*sin(n*omega*x), x, -T/2, T/2)."""
        def integrand(x):
            """Perform integrand operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.integrand(...)
            """
            return func(x) * math.sin(n * omega * x)
        integral = self._numerical_integrate(integrand, a, b)
        return (2 / period) * integral

    def _numerical_integrate(self, func: Callable, a: float, b: float, n_points: int = 1000) -> float:
        """Simpson's rule numerical integration."""
        if n_points % 2 == 0:
            n_points += 1

        h = (b - a) / (n_points - 1)
        total = func(a) + func(b)

        for i in range(1, n_points - 1):
            x = a + i * h
            if i % 2 == 0:
                total += 2 * func(x)
            else:
                total += 4 * func(x)

        return (h / 3) * total

    def _create_evaluator(self, expr_str: str, var: str) -> Callable:
        """Create a numeric evaluator from string expression."""
        # Safe math namespace
        namespace = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'exp': math.exp, 'log': math.log, 'sqrt': math.sqrt,
            'abs': abs, 'pi': math.pi, 'e': math.e,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
        }

        def evaluator(val):
            """Perform evaluator operation.

            Args:
            val: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.evaluator(...)
            """
            namespace[var] = val
            try:
                return eval(expr_str, {"__builtins__": {}}, namespace)
            except Exception:
                return 0.0

        return evaluator

    def _build_series_expr(
        self, a0: float, an: List[float], bn: List[float], var: str, omega: float
    ) -> str:
        """Build symbolic expression for the series."""
        x = Symbol(var)
        terms = [f"{a0/2:.6g}"]

        for n, (a, b) in enumerate(zip(an, bn), start=1):
            if abs(a) > 1e-10:
                terms.append(f"{a:.6g}*cos({n}*{omega:.6g}*{var})")
            if abs(b) > 1e-10:
                terms.append(f"{b:.6g}*sin({n}*{omega:.6g}*{var})")

        return " + ".join(terms) if terms else "0"

    # ==================== DFT / IDFT ====================

    def dft(self, signal: List[float], sample_rate: Optional[float] = None) -> DFTResult:
        """
        Compute Discrete Fourier Transform.

        X[k] = sum_{n=0}^{N-1} x[n] * exp(-2*pi*i*k*n/N)

        Args:
            signal: Input signal samples
            sample_rate: Sample rate in Hz (for frequency calculation)

        Returns:
            DFTResult with magnitudes, phases, and frequencies
        """
        N = len(signal)
        complex_coeffs = []

        for k in range(N):
            total = complex(0, 0)
            for n in range(N):
                angle = -2 * math.pi * k * n / N
                total += signal[n] * cmath.exp(complex(0, angle))
            complex_coeffs.append(total)

        # Extract magnitudes and phases
        magnitudes = [abs(c) for c in complex_coeffs]
        phases = [cmath.phase(c) for c in complex_coeffs]

        # Calculate frequencies
        if sample_rate:
            frequencies = [k * sample_rate / N for k in range(N)]
        else:
            frequencies = list(range(N))

        self._stats['transforms_computed'] += 1

        return DFTResult(
            magnitudes=magnitudes,
            phases=phases,
            frequencies=frequencies,
            complex_coeffs=complex_coeffs,
            n_samples=N,
            sample_rate=sample_rate
        )

    def idft(self, coeffs: List[complex]) -> List[float]:
        """
        Compute Inverse Discrete Fourier Transform.

        x[n] = (1/N) * sum_{k=0}^{N-1} X[k] * exp(2*pi*i*k*n/N)

        Args:
            coeffs: DFT coefficients

        Returns:
            Reconstructed signal samples
        """
        N = len(coeffs)
        signal = []

        for n in range(N):
            total = complex(0, 0)
            for k in range(N):
                angle = 2 * math.pi * k * n / N
                total += coeffs[k] * cmath.exp(complex(0, angle))
            signal.append((total / N).real)

        return signal

    def fft(self, signal: List[float]) -> DFTResult:
        """
        Fast Fourier Transform using Cooley-Tukey algorithm.

        Optimized O(N log N) implementation for power-of-2 lengths.
        Falls back to DFT for non-power-of-2.

        Args:
            signal: Input signal samples

        Returns:
            DFTResult with magnitudes, phases, and frequencies
        """
        N = len(signal)

        # Check if N is power of 2
        if N & (N - 1) != 0 or N == 0:
            # Fall back to regular DFT
            return self.dft(signal)

        # Cooley-Tukey recursive FFT
        complex_coeffs = self._fft_recursive([complex(x) for x in signal])

        magnitudes = [abs(c) for c in complex_coeffs]
        phases = [cmath.phase(c) for c in complex_coeffs]
        frequencies = list(range(N))

        self._stats['transforms_computed'] += 1

        return DFTResult(
            magnitudes=magnitudes,
            phases=phases,
            frequencies=frequencies,
            complex_coeffs=complex_coeffs,
            n_samples=N,
            sample_rate=None
        )

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

    # ==================== CONVOLUTION ====================

    def convolve(self, f: List[float], g: List[float]) -> List[float]:
        """
        Compute discrete convolution of two signals.

        (f * g)[n] = sum_k f[k] * g[n - k]

        Args:
            f: First signal
            g: Second signal

        Returns:
            Convolution result (length len(f) + len(g) - 1)
        """
        n_f = len(f)
        n_g = len(g)
        n_result = n_f + n_g - 1

        result = [0.0] * n_result

        for i in range(n_f):
            for j in range(n_g):
                result[i + j] += f[i] * g[j]

        self._stats['convolutions_computed'] += 1
        return result

    def convolve_fft(self, f: List[float], g: List[float]) -> List[float]:
        """
        Compute convolution using FFT (faster for large signals).

        Uses the convolution theorem: F(f*g) = F(f) * F(g)

        Args:
            f: First signal
            g: Second signal

        Returns:
            Convolution result
        """
        n_result = len(f) + len(g) - 1

        # Pad to power of 2 for FFT efficiency
        n_fft = 1
        while n_fft < n_result:
            n_fft *= 2

        # Zero-pad signals
        f_padded = f + [0.0] * (n_fft - len(f))
        g_padded = g + [0.0] * (n_fft - len(g))

        # FFT both signals
        F_f = self._fft_recursive([complex(x) for x in f_padded])
        F_g = self._fft_recursive([complex(x) for x in g_padded])

        # Multiply in frequency domain
        F_result = [a * b for a, b in zip(F_f, F_g)]

        # Inverse FFT
        result = self._ifft_recursive(F_result)

        # Return real part, trimmed to correct length
        self._stats['convolutions_computed'] += 1
        return [x.real for x in result[:n_result]]

    def _ifft_recursive(self, x: List[complex]) -> List[complex]:
        """Inverse FFT using conjugate trick."""
        N = len(x)
        # Take conjugate, apply FFT, take conjugate, divide by N
        conjugated = [c.conjugate() for c in x]
        fft_result = self._fft_recursive(conjugated)
        return [c.conjugate() / N for c in fft_result]

    # ==================== CORRELATION ====================

    def correlate(self, f: List[float], g: List[float]) -> List[float]:
        """
        Compute cross-correlation of two signals.

        (f * g)[n] = sum_k f[k] * g[k + n]

        Args:
            f: First signal
            g: Second signal

        Returns:
            Cross-correlation result
        """
        # Correlation is convolution with time-reversed second signal
        g_reversed = g[::-1]
        return self.convolve(f, g_reversed)

    def autocorrelate(self, signal: List[float]) -> List[float]:
        """
        Compute autocorrelation of a signal.

        Args:
            signal: Input signal

        Returns:
            Autocorrelation result
        """
        return self.correlate(signal, signal)

    # ==================== POWER SPECTRUM ====================

    def power_spectrum(self, signal: List[float], sample_rate: Optional[float] = None) -> Dict[str, List[float]]:
        """
        Compute power spectral density.

        PSD = |X[k]|^2 / N

        Args:
            signal: Input signal
            sample_rate: Sample rate for frequency axis

        Returns:
            Dict with 'frequencies' and 'power' arrays
        """
        dft_result = self.fft(signal)
        N = len(signal)

        # Compute power (one-sided for real signals)
        power = [(m ** 2) / N for m in dft_result.magnitudes[:N // 2 + 1]]

        # Adjust DC and Nyquist
        if len(power) > 0:
            power[0] /= 2
            if len(power) > 1 and N % 2 == 0:
                power[-1] /= 2

        # Calculate frequencies
        if sample_rate:
            frequencies = [k * sample_rate / N for k in range(len(power))]
        else:
            frequencies = list(range(len(power)))

        return {
            'frequencies': frequencies,
            'power': power,
        }

    # ==================== WINDOWING ====================

    def apply_window(self, signal: List[float], window_type: str = 'hanning') -> List[float]:
        """
        Apply a window function to a signal.

        Args:
            signal: Input signal
            window_type: 'hanning', 'hamming', 'blackman', 'rectangular'

        Returns:
            Windowed signal
        """
        N = len(signal)

        if window_type == 'hanning':
            window = [0.5 * (1 - math.cos(2 * math.pi * n / (N - 1))) for n in range(N)]
        elif window_type == 'hamming':
            window = [0.54 - 0.46 * math.cos(2 * math.pi * n / (N - 1)) for n in range(N)]
        elif window_type == 'blackman':
            window = [
                0.42 - 0.5 * math.cos(2 * math.pi * n / (N - 1))
                + 0.08 * math.cos(4 * math.pi * n / (N - 1))
                for n in range(N)
            ]
        else:  # rectangular
            window = [1.0] * N

        return [s * w for s, w in zip(signal, window)]

    # ==================== FILTERING ====================

    def lowpass_filter(self, signal: List[float], cutoff_ratio: float = 0.5) -> List[float]:
        """
        Apply lowpass filter in frequency domain.

        Args:
            signal: Input signal
            cutoff_ratio: Cutoff frequency as ratio of Nyquist (0-1)

        Returns:
            Filtered signal
        """
        N = len(signal)
        cutoff_bin = int(cutoff_ratio * N / 2)

        # FFT
        coeffs = self._fft_recursive([complex(x) for x in signal])

        # Zero out high frequencies
        for k in range(cutoff_bin, N - cutoff_bin):
            coeffs[k] = 0

        # IFFT
        result = self._ifft_recursive(coeffs)
        return [x.real for x in result]

    def highpass_filter(self, signal: List[float], cutoff_ratio: float = 0.5) -> List[float]:
        """
        Apply highpass filter in frequency domain.

        Args:
            signal: Input signal
            cutoff_ratio: Cutoff frequency as ratio of Nyquist (0-1)

        Returns:
            Filtered signal
        """
        N = len(signal)
        cutoff_bin = int(cutoff_ratio * N / 2)

        # FFT
        coeffs = self._fft_recursive([complex(x) for x in signal])

        # Zero out low frequencies
        for k in range(cutoff_bin):
            coeffs[k] = 0
            coeffs[N - 1 - k] = 0

        # IFFT
        result = self._ifft_recursive(coeffs)
        return [x.real for x in result]

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'fourier_series':
            result = self.fourier_series(**params)
            return {'status': 'success', 'result': result}
        elif action == 'dft':
            result = self.dft(**params)
            return {'status': 'success', 'result': result}
        elif action == 'fft':
            result = self.fft(**params)
            return {'status': 'success', 'result': result}
        elif action == 'convolve':
            result = self.convolve(**params)
            return {'status': 'success', 'result': result}
        elif action == 'correlate':
            result = self.correlate(**params)
            return {'status': 'success', 'result': result}
        elif action == 'power_spectrum':
            result = self.power_spectrum(**params)
            return {'status': 'success', 'result': result}
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return dict(self._stats)

    # ==================== ABSTRACT BDI METHODS ====================

    def update_beliefs(self):
        """
        Update beliefs from environment.

        For FourierAnalysisSpecialist, this reads pending Fourier analysis
        tasks from the Blackboard and updates internal beliefs.
        """
        if self.blackboard:
            # Check for pending Fourier analysis requests
            entries = self.blackboard.query_entries(
                tags=['fourier', 'signal_processing'],
                status='pending'
            ) if hasattr(self.blackboard, 'query_entries') else []

            for entry in entries:
                self.add_belief('pending_fourier_task', entry, source='blackboard')

    def deliberate(self) -> List:
        """
        Compare beliefs to desires, generate new intentions.

        Examines current beliefs about pending tasks and generates
        intentions for Fourier analysis operations.
        """
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        new_intentions = []

        # Check for pending Fourier tasks
        if self.has_belief('pending_fourier_task'):
            task_belief = self.get_belief('pending_fourier_task')
            if task_belief:
                task = task_belief.content
                task_type = task.get('type', 'dft') if isinstance(task, dict) else 'dft'

                # Generate intention based on task type
                intention = Intention(
                    goal=f"compute_{task_type}",
                    plan=[f"analyze_input", f"execute_{task_type}", "post_results"],
                    priority=5,
                    context={'task': task}
                )
                new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention):
        """
        Execute next step in plan - delegate to Fourier operations.

        Args:
            intention: The current intention being executed
        """
        if not intention or not hasattr(intention, 'get_current_action'):
            return

        action = intention.get_current_action()
        context = intention.context if hasattr(intention, 'context') else {}

        if action == 'analyze_input':
            # Verify input is valid
            logger.debug(f"Analyzing input for Fourier task")
            intention.advance()

        elif action.startswith('execute_'):
            task_type = action.replace('execute_', '')
            task = context.get('task', {})

            try:
                if task_type == 'dft':
                    signal = task.get('signal', [])
                    result = self.dft(signal)
                elif task_type == 'fft':
                    signal = task.get('signal', [])
                    result = self.fft(signal)
                elif task_type == 'fourier_series':
                    func = task.get('func', 'x')
                    result = self.fourier_series(func)
                else:
                    result = None

                intention.context['result'] = result
                intention.advance()

            except Exception as e:
                logger.error(f"Fourier execution failed: {e}")
                intention.fail(str(e))

        elif action == 'post_results':
            # Post results to blackboard
            result = context.get('result')
            if self.blackboard and result:
                entry = create_entry(
                    content=result,
                    entry_type=EntryType.RESULT,
                    tags=['fourier', 'result'],
                    agent_id=self.agent_id
                )
                self.blackboard.post_entry(entry)

            intention.complete()


# Convenience functions
def fourier_series(func, var='x', period=2*math.pi, n_terms=10) -> FourierSeriesResult:
    """Compute Fourier series coefficients."""
    specialist = FourierAnalysisSpecialist()
    return specialist.fourier_series(func, var, period, n_terms)


def dft(signal: List[float], sample_rate: Optional[float] = None) -> DFTResult:
    """Compute Discrete Fourier Transform."""
    specialist = FourierAnalysisSpecialist()
    return specialist.dft(signal, sample_rate)


def fft(signal: List[float]) -> DFTResult:
    """Compute Fast Fourier Transform."""
    specialist = FourierAnalysisSpecialist()
    return specialist.fft(signal)


def convolve(f: List[float], g: List[float]) -> List[float]:
    """Compute convolution of two signals."""
    specialist = FourierAnalysisSpecialist()
    return specialist.convolve(f, g)


__all__ = [
    'FourierAnalysisSpecialist',
    'FourierSeriesResult',
    'DFTResult',
    'fourier_series',
    'dft',
    'fft',
    'convolve',
]
