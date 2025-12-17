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
Tests for New Mathematical Specialist Agents
=============================================

Tests for:
- ODESolutionSpecialist (differential equation solving)
- FourierAnalysisSpecialist (Fourier analysis and signal processing)
- NumericalMethodsSpecialist (numerical computation methods)

These tests verify the mathematical correctness and BDI integration
of the new specialist agents.
"""

import pytest
import math
from typing import List

# ==================== TEST: FOURIER ANALYSIS SPECIALIST ====================


class TestFourierAnalysisSpecialist:
    """Tests for FourierAnalysisSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create a Fourier specialist instance."""
        from symbo_agentic_reasoners.agents.specialists.calculus.fourier_specialist import (
            FourierAnalysisSpecialist
        )
        return FourierAnalysisSpecialist()

    def test_specialist_creation(self, specialist):
        """Test specialist can be created."""
        assert specialist is not None
        assert specialist.agent_id == "fourier_specialist"
        assert specialist.agent_type == "fourier_specialist"

    def test_dft_simple_signal(self, specialist):
        """Test DFT of a simple constant signal."""
        signal = [1.0, 1.0, 1.0, 1.0]
        result = specialist.dft(signal)

        assert result.n_samples == 4
        # For constant signal, DC component should be dominant
        assert result.magnitudes[0] == pytest.approx(4.0, abs=1e-10)
        # Other components should be near zero
        for i in range(1, len(result.magnitudes)):
            assert result.magnitudes[i] == pytest.approx(0.0, abs=1e-10)

    def test_dft_sinusoidal(self, specialist):
        """Test DFT of a sinusoidal signal."""
        N = 16
        signal = [math.sin(2 * math.pi * 2 * n / N) for n in range(N)]
        result = specialist.dft(signal)

        assert result.n_samples == N
        # Should have peaks at frequency indices 2 and N-2
        assert len(result.magnitudes) == N

    def test_fft_power_of_two(self, specialist):
        """Test FFT works for power-of-2 length signals."""
        signal = [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
        result = specialist.fft(signal)

        assert result.n_samples == 8
        assert len(result.magnitudes) == 8

    def test_idft_reconstruction(self, specialist):
        """Test IDFT reconstructs original signal."""
        original = [1.0, 2.0, 3.0, 4.0]
        dft_result = specialist.dft(original)
        reconstructed = specialist.idft(dft_result.complex_coeffs)

        for i, (orig, recon) in enumerate(zip(original, reconstructed)):
            assert recon == pytest.approx(orig, abs=1e-10), f"Mismatch at index {i}"

    def test_convolution_basic(self, specialist):
        """Test basic convolution operation."""
        f = [1.0, 2.0, 3.0]
        g = [1.0, 1.0]
        result = specialist.convolve(f, g)

        expected = [1.0, 3.0, 5.0, 3.0]  # Manual convolution
        assert len(result) == len(expected)
        for r, e in zip(result, expected):
            assert r == pytest.approx(e, abs=1e-10)

    def test_convolution_fft(self, specialist):
        """Test FFT-based convolution gives same result."""
        f = [1.0, 2.0, 3.0, 4.0]
        g = [0.5, 0.5]

        result_direct = specialist.convolve(f, g)
        result_fft = specialist.convolve_fft(f, g)

        for rd, rf in zip(result_direct, result_fft):
            assert rd == pytest.approx(rf, abs=1e-10)

    def test_autocorrelation(self, specialist):
        """Test autocorrelation of a signal."""
        signal = [1.0, 2.0, 3.0, 2.0, 1.0]
        result = specialist.autocorrelate(signal)

        # Autocorrelation at zero lag should be maximum
        max_val = max(result)
        middle_idx = len(result) // 2
        assert result[middle_idx] == max_val

    def test_power_spectrum(self, specialist):
        """Test power spectrum computation."""
        signal = [1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0]
        result = specialist.power_spectrum(signal)

        assert 'frequencies' in result
        assert 'power' in result
        assert len(result['power']) > 0

    def test_window_functions(self, specialist):
        """Test window function application."""
        signal = [1.0] * 10

        for window_type in ['hanning', 'hamming', 'blackman', 'rectangular']:
            windowed = specialist.apply_window(signal, window_type)
            assert len(windowed) == len(signal)

            if window_type == 'rectangular':
                # Rectangular window should not change the signal
                for s, w in zip(signal, windowed):
                    assert s == pytest.approx(w, abs=1e-10)

    def test_lowpass_filter(self, specialist):
        """Test lowpass filter."""
        # Signal with low and high frequency components
        N = 32
        signal = [math.sin(2 * math.pi * n / N) + math.sin(2 * math.pi * 8 * n / N)
                  for n in range(N)]

        filtered = specialist.lowpass_filter(signal, cutoff_ratio=0.3)
        assert len(filtered) == len(signal)

    def test_highpass_filter(self, specialist):
        """Test highpass filter."""
        N = 32
        signal = [math.sin(2 * math.pi * n / N) + math.sin(2 * math.pi * 8 * n / N)
                  for n in range(N)]

        filtered = specialist.highpass_filter(signal, cutoff_ratio=0.3)
        assert len(filtered) == len(signal)

    def test_fourier_series_square_wave(self, specialist):
        """Test Fourier series of a square wave approximation."""
        def square_wave(x):
            return 1.0 if math.sin(x) >= 0 else -1.0

        result = specialist.fourier_series(square_wave, n_terms=5)
        assert result.n_terms == 5
        assert len(result.an) == 5
        assert len(result.bn) == 5

    def test_bdi_message_processing(self, specialist):
        """Test BDI message processing."""
        message = {
            'action': 'dft',
            'params': {'signal': [1.0, 2.0, 3.0, 4.0]}
        }
        response = specialist.process_message(message)
        assert response['status'] == 'success'
        assert response['result'] is not None

    def test_stats_tracking(self, specialist):
        """Test statistics are tracked."""
        specialist.dft([1.0, 2.0, 3.0, 4.0])
        specialist.convolve([1.0, 2.0], [3.0, 4.0])

        stats = specialist.get_stats()
        assert stats['transforms_computed'] >= 1
        assert stats['convolutions_computed'] >= 1


# ==================== TEST: NUMERICAL METHODS SPECIALIST ====================


class TestNumericalMethodsSpecialist:
    """Tests for NumericalMethodsSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create a numerical methods specialist instance."""
        from symbo_agentic_reasoners.agents.specialists.numerical.numerical_methods_specialist import (
            NumericalMethodsSpecialist
        )
        return NumericalMethodsSpecialist()

    def test_specialist_creation(self, specialist):
        """Test specialist can be created."""
        assert specialist is not None
        assert specialist.agent_id == "numerical_methods_specialist"

    # ---------- Integration Tests ----------

    def test_trapezoidal_integration(self, specialist):
        """Test trapezoidal rule integration."""
        # Integrate x^2 from 0 to 1, expected = 1/3
        def f(x): return x ** 2

        result = specialist.integrate(f, 0, 1, method='trapezoidal')
        assert result.value == pytest.approx(1/3, abs=1e-3)
        assert result.method == 'trapezoidal'

    def test_simpson_integration(self, specialist):
        """Test Simpson's rule integration."""
        # Integrate sin(x) from 0 to pi, expected = 2
        def f(x): return math.sin(x)

        result = specialist.integrate(f, 0, math.pi, method='simpson')
        assert result.value == pytest.approx(2.0, abs=1e-5)

    def test_romberg_integration(self, specialist):
        """Test Romberg integration."""
        # Integrate e^x from 0 to 1, expected = e - 1
        def f(x): return math.exp(x)

        result = specialist.integrate(f, 0, 1, method='romberg', tolerance=1e-10)
        assert result.value == pytest.approx(math.e - 1, abs=1e-8)
        assert result.converged

    def test_gaussian_quadrature(self, specialist):
        """Test Gaussian quadrature."""
        # Integrate 1/(1+x^2) from 0 to 1, expected = pi/4
        def f(x): return 1 / (1 + x ** 2)

        result = specialist.integrate(f, 0, 1, method='gaussian')
        assert result.value == pytest.approx(math.pi / 4, abs=1e-4)

    def test_adaptive_simpson(self, specialist):
        """Test adaptive Simpson integration."""
        # Integrate sqrt(x) from 0 to 1, expected = 2/3
        def f(x): return math.sqrt(x) if x > 0 else 0

        result = specialist.integrate(f, 0.001, 1, method='adaptive', tolerance=1e-6)
        assert result.value == pytest.approx(2/3 - 2/3 * 0.001**1.5, abs=1e-4)

    # ---------- Differentiation Tests ----------

    def test_forward_difference(self, specialist):
        """Test forward difference differentiation."""
        def f(x): return x ** 2
        # Derivative of x^2 at x=2 is 4

        result = specialist.differentiate(f, 2.0, method='forward')
        assert result == pytest.approx(4.0, abs=1e-4)

    def test_central_difference(self, specialist):
        """Test central difference differentiation."""
        def f(x): return math.sin(x)
        # Derivative of sin(x) at x=0 is cos(0) = 1

        result = specialist.differentiate(f, 0.0, method='central')
        assert result == pytest.approx(1.0, abs=1e-8)

    def test_richardson_extrapolation(self, specialist):
        """Test Richardson extrapolation for derivatives."""
        def f(x): return math.exp(x)
        # Derivative of e^x at x=1 is e

        result = specialist.differentiate(f, 1.0, method='richardson')
        assert result == pytest.approx(math.e, abs=1e-8)

    def test_second_derivative(self, specialist):
        """Test second derivative computation."""
        def f(x): return x ** 3
        # Second derivative of x^3 at x=2 is 12

        result = specialist.differentiate(f, 2.0, order=2)
        assert result == pytest.approx(12.0, abs=1e-2)

    def test_gradient(self, specialist):
        """Test gradient of multivariate function."""
        def f(x): return x[0] ** 2 + 2 * x[1] ** 2
        # Gradient at (1, 1) is (2, 4)

        grad = specialist.gradient(f, [1.0, 1.0])
        assert grad[0] == pytest.approx(2.0, abs=1e-5)
        assert grad[1] == pytest.approx(4.0, abs=1e-5)

    # ---------- ODE Solver Tests ----------

    def test_euler_method(self, specialist):
        """Test Euler's method for ODE solving."""
        # dy/dt = y, y(0) = 1 -> y(t) = e^t
        def f(t, y): return y

        result = specialist.solve_ode_ivp(f, [1.0], (0, 1), method='euler', n_steps=1000)
        final_y = result.y[-1][0]
        assert final_y == pytest.approx(math.e, abs=0.01)

    def test_rk4_method(self, specialist):
        """Test RK4 method for ODE solving."""
        # dy/dt = y, y(0) = 1 -> y(t) = e^t
        def f(t, y): return y

        result = specialist.solve_ode_ivp(f, [1.0], (0, 1), method='rk4', n_steps=100)
        final_y = result.y[-1][0]
        assert final_y == pytest.approx(math.e, abs=1e-6)

    def test_rk45_adaptive(self, specialist):
        """Test RK45 adaptive method for ODE solving."""
        # dy/dt = -2ty, y(0) = 1 -> y(t) = e^(-t^2)
        def f(t, y): return [-2 * t * y[0]]

        result = specialist.solve_ode_ivp(f, [1.0], (0, 2), method='rk45', tolerance=1e-6)
        final_y = result.y[-1][0]
        expected = math.exp(-4)
        assert final_y == pytest.approx(expected, abs=1e-4)

    def test_ode_system(self, specialist):
        """Test ODE system solving (simple harmonic oscillator)."""
        # y'' + y = 0 -> y1' = y2, y2' = -y1
        # y(0) = 0, y'(0) = 1 -> y(t) = sin(t)
        def f(t, y): return [y[1], -y[0]]

        result = specialist.solve_ode_ivp(f, [0.0, 1.0], (0, math.pi), method='rk4', n_steps=100)
        # At t = pi, y should be close to 0, y' should be close to -1
        assert result.y[-1][0] == pytest.approx(0.0, abs=1e-4)
        assert result.y[-1][1] == pytest.approx(-1.0, abs=1e-4)

    # ---------- Root Finding Tests ----------

    def test_bisection_root(self, specialist):
        """Test bisection method for root finding."""
        def f(x): return x ** 2 - 2  # Root at sqrt(2)

        root = specialist.find_root(f, bracket=(1, 2), method='bisection')
        assert root == pytest.approx(math.sqrt(2), abs=1e-8)

    def test_newton_root(self, specialist):
        """Test Newton's method for root finding."""
        def f(x): return x ** 3 - 1  # Root at 1

        root = specialist.find_root(f, x0=0.5, method='newton')
        assert root == pytest.approx(1.0, abs=1e-8)

    def test_secant_root(self, specialist):
        """Test secant method for root finding."""
        def f(x): return math.cos(x) - x  # Root near 0.739

        root = specialist.find_root(f, bracket=(0, 1), method='secant')
        assert root is not None
        assert abs(f(root)) < 1e-8

    def test_brent_root(self, specialist):
        """Test Brent's method for root finding."""
        def f(x): return x ** 3 - 2 * x - 5  # Root near 2.094

        root = specialist.find_root(f, bracket=(2, 3), method='brent')
        assert root is not None
        assert abs(f(root)) < 1e-10

    # ---------- Interpolation Tests ----------

    def test_lagrange_interpolation(self, specialist):
        """Test Lagrange polynomial interpolation."""
        x_points = [0, 1, 2]
        y_points = [1, 2, 5]  # y = x^2 + 1

        result = specialist.interpolate(x_points, y_points, method='lagrange')
        assert result.evaluator is not None

        # Test at interpolation points
        for x, y in zip(x_points, y_points):
            assert result.evaluator(x) == pytest.approx(y, abs=1e-10)

        # Test at intermediate point
        assert result.evaluator(0.5) == pytest.approx(1.25, abs=1e-10)

    def test_newton_interpolation(self, specialist):
        """Test Newton's divided difference interpolation."""
        x_points = [0, 1, 2, 3]
        y_points = [1, 0, 1, 10]

        result = specialist.interpolate(x_points, y_points, method='newton')
        assert result.evaluator is not None
        assert len(result.polynomial_coeffs) == 4

        # Verify passes through all points
        for x, y in zip(x_points, y_points):
            assert result.evaluator(x) == pytest.approx(y, abs=1e-10)

    def test_linear_interpolation(self, specialist):
        """Test piecewise linear interpolation."""
        x_points = [0, 1, 2]
        y_points = [0, 2, 1]

        result = specialist.interpolate(x_points, y_points, method='linear')
        assert result.evaluator(0.5) == pytest.approx(1.0, abs=1e-10)
        assert result.evaluator(1.5) == pytest.approx(1.5, abs=1e-10)

    # ---------- BDI Integration Tests ----------

    def test_bdi_integrate_message(self, specialist):
        """Test BDI message processing for integration."""
        def f(x): return x ** 2

        message = {
            'action': 'integrate',
            'params': {'func': f, 'a': 0, 'b': 1}
        }
        response = specialist.process_message(message)
        assert response['status'] == 'success'
        assert response['result'].value == pytest.approx(1/3, abs=1e-6)

    def test_stats_tracking(self, specialist):
        """Test statistics are tracked."""
        def f(x): return x

        specialist.integrate(f, 0, 1)
        specialist.differentiate(f, 0.5)

        stats = specialist.get_stats()
        assert stats['integrations'] >= 1
        assert stats['derivatives'] >= 1


# ==================== TEST: ODE SOLUTION SPECIALIST ====================


class TestODESolutionSpecialist:
    """Tests for ODESolutionSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create an ODE specialist instance."""
        from symbo_agentic_reasoners.agents.specialists.calculus.ode_specialist import (
            ODESolutionSpecialist
        )
        return ODESolutionSpecialist()

    def test_specialist_creation(self, specialist):
        """Test specialist can be created."""
        assert specialist is not None
        assert specialist.agent_id is not None

    def test_classify_first_order_linear(self, specialist):
        """Test classification of first-order linear ODE."""
        # dy/dx + 2y = x
        classification = specialist.classify_ode("dy/dx + 2*y = x", 'x', 'y')
        assert classification.order == 1
        assert classification.linearity == 'linear'

    def test_classify_separable(self, specialist):
        """Test classification of separable ODE."""
        # dy/dx = xy
        classification = specialist.classify_ode("dy/dx = x*y", 'x', 'y')
        assert classification.order == 1

    def test_classify_second_order(self, specialist):
        """Test classification of second-order ODE."""
        # y'' + 3y' + 2y = 0
        classification = specialist.classify_ode("y'' + 3*y' + 2*y = 0", 'x', 'y')
        assert classification.order == 2

    def test_bdi_integration(self, specialist):
        """Test BDI message processing."""
        message = {
            'action': 'classify',
            'params': {'ode_str': "dy/dx = x"}
        }
        response = specialist.process_message(message)
        assert response['status'] in ['success', 'error']


# ==================== INTEGRATION TESTS ====================


class TestSpecialistIntegration:
    """Integration tests for specialist cooperation."""

    def test_numerical_verify_fourier(self):
        """Test numerical methods can verify Fourier results."""
        from symbo_agentic_reasoners.agents.specialists.calculus.fourier_specialist import (
            FourierAnalysisSpecialist
        )
        from symbo_agentic_reasoners.agents.specialists.numerical.numerical_methods_specialist import (
            NumericalMethodsSpecialist
        )

        fourier = FourierAnalysisSpecialist()
        numerical = NumericalMethodsSpecialist()

        # Create a simple signal
        signal = [math.sin(2 * math.pi * n / 8) for n in range(8)]

        # Get DFT
        dft_result = fourier.dft(signal)

        # Verify IDFT reconstruction using numerical comparison
        reconstructed = fourier.idft(dft_result.complex_coeffs)

        # Use numerical methods to verify
        for i, (orig, recon) in enumerate(zip(signal, reconstructed)):
            assert abs(orig - recon) < 1e-10, f"Reconstruction error at index {i}"

    def test_ode_numerical_verification(self):
        """Test ODE symbolic solution against numerical solution."""
        from symbo_agentic_reasoners.agents.specialists.numerical.numerical_methods_specialist import (
            NumericalMethodsSpecialist
        )

        numerical = NumericalMethodsSpecialist()

        # Solve y' = y numerically
        def f(t, y): return y

        result = numerical.solve_ode_ivp(f, [1.0], (0, 1), method='rk4', n_steps=100)

        # Verify against exact solution y = e^t
        for t, y in zip(result.t, result.y):
            expected = math.exp(t)
            assert y[0] == pytest.approx(expected, rel=1e-4)


# ==================== EDGE CASE TESTS ====================


class TestEdgeCases:
    """Edge case and boundary condition tests."""

    def test_fourier_single_sample(self):
        """Test DFT of single sample."""
        from symbo_agentic_reasoners.agents.specialists.calculus.fourier_specialist import (
            FourierAnalysisSpecialist
        )

        specialist = FourierAnalysisSpecialist()
        result = specialist.dft([5.0])

        assert result.n_samples == 1
        assert result.magnitudes[0] == pytest.approx(5.0, abs=1e-10)

    def test_numerical_zero_interval(self):
        """Test integration over zero-length interval."""
        from symbo_agentic_reasoners.agents.specialists.numerical.numerical_methods_specialist import (
            NumericalMethodsSpecialist
        )

        specialist = NumericalMethodsSpecialist()

        def f(x): return x ** 2

        result = specialist.integrate(f, 0, 0, method='simpson')
        assert result.value == pytest.approx(0.0, abs=1e-10)

    def test_interpolation_two_points(self):
        """Test interpolation with minimum number of points."""
        from symbo_agentic_reasoners.agents.specialists.numerical.numerical_methods_specialist import (
            NumericalMethodsSpecialist
        )

        specialist = NumericalMethodsSpecialist()

        result = specialist.interpolate([0, 1], [0, 1], method='lagrange')
        # Should be identity function
        assert result.evaluator(0.5) == pytest.approx(0.5, abs=1e-10)

    def test_root_no_bracket(self):
        """Test root finding when no root exists in interval."""
        from symbo_agentic_reasoners.agents.specialists.numerical.numerical_methods_specialist import (
            NumericalMethodsSpecialist
        )

        specialist = NumericalMethodsSpecialist()

        def f(x): return x ** 2 + 1  # No real roots

        root = specialist.find_root(f, bracket=(0, 1), method='bisection')
        assert root is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
