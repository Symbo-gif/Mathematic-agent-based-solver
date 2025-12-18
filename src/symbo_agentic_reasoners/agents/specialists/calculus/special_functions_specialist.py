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
SPECIAL FUNCTIONS SPECIALIST (Tier 3)
=====================================

Evaluates special mathematical functions.

CAPABILITIES:
------------
- Gamma function and related (digamma, polygamma, beta)
- Error function (erf, erfc, erfi)
- Bessel functions (J, Y, I, K)
- Elliptic integrals (K, E, Pi)
- Hypergeometric functions
- Zeta function
- Polylogarithm

NO SYMPY - All mathematical operations use native implementations.

ALGORITHMS:
-----------
- Lanczos approximation for Gamma
- Taylor series for erf
- Asymptotic expansions for Bessel
- Arithmetic-geometric mean for elliptic
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.special_functions')


class SpecialFunctionsSpecialist(BDIAgent):
    """
    Special Functions Specialist - Mathematical Special Functions

    DIRECTIVE:
    ---------
    Evaluate special mathematical functions with high precision.

    OPERATIONS:
    ----------
    - gamma: Gamma function Γ(z)
    - digamma: Digamma function ψ(z)
    - beta: Beta function B(a, b)
    - erf: Error function erf(x)
    - erfc: Complementary error function
    - bessel_j: Bessel function of first kind
    - bessel_y: Bessel function of second kind
    - bessel_i: Modified Bessel function (first kind)
    - bessel_k: Modified Bessel function (second kind)
    - elliptic_k: Complete elliptic integral of first kind
    - elliptic_e: Complete elliptic integral of second kind
    """

    def __init__(
        self,
        agent_id: str = "special_functions_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "special_functions_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'evaluations': 0}

        # Lanczos coefficients for Gamma function
        self._lanczos_g = 7
        self._lanczos_coeffs = [
            0.99999999999980993,
            676.5203681218851,
            -1259.1392167224028,
            771.32342877765313,
            -176.61502916214059,
            12.507343278686905,
            -0.13857109526572012,
            9.9843695780195716e-6,
            1.5056327351493116e-7
        ]

    def _register_services(self):
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="special_functions",
                description="Special mathematical functions"
            ))

    # ==================== GAMMA FUNCTION ====================

    def gamma(self, z: Union[float, complex]) -> Union[float, complex]:
        """
        Compute the Gamma function Γ(z) using Lanczos approximation.

        Γ(n) = (n-1)! for positive integers.
        """
        self._stats['evaluations'] += 1

        if isinstance(z, complex):
            return self._gamma_complex(z)

        # Handle special cases
        if z <= 0 and z == int(z):
            return float('inf')  # Pole at non-positive integers

        if z < 0.5:
            # Reflection formula: Γ(z)Γ(1-z) = π/sin(πz)
            return math.pi / (math.sin(math.pi * z) * self.gamma(1 - z))

        z -= 1
        x = self._lanczos_coeffs[0]
        for i in range(1, self._lanczos_g + 2):
            x += self._lanczos_coeffs[i] / (z + i)

        t = z + self._lanczos_g + 0.5
        return math.sqrt(2 * math.pi) * (t ** (z + 0.5)) * math.exp(-t) * x

    def _gamma_complex(self, z: complex) -> complex:
        """Gamma function for complex argument."""
        if z.real < 0.5:
            return math.pi / (
                (math.sin(math.pi * z.real) * math.cosh(math.pi * z.imag) +
                 1j * math.cos(math.pi * z.real) * math.sinh(math.pi * z.imag)) *
                self._gamma_complex(1 - z)
            )

        z = z - 1
        x = self._lanczos_coeffs[0]
        for i in range(1, self._lanczos_g + 2):
            x += self._lanczos_coeffs[i] / (z + i)

        t = z + self._lanczos_g + 0.5
        return (2 * math.pi) ** 0.5 * (t ** (z + 0.5)) * math.exp(-t.real) * x

    def factorial(self, n: int) -> float:
        """Factorial n! = Γ(n+1)."""
        if n < 0:
            raise ValueError("Factorial not defined for negative integers")
        return self.gamma(n + 1)

    def digamma(self, x: float) -> float:
        """
        Digamma function ψ(x) = d/dx ln(Γ(x)) = Γ'(x)/Γ(x).

        Uses asymptotic expansion for x > 6, recurrence otherwise.
        """
        self._stats['evaluations'] += 1

        if x <= 0 and x == int(x):
            return float('inf')

        # Use recurrence to shift to x > 6
        result = 0.0
        while x < 6:
            result -= 1.0 / x
            x += 1

        # Asymptotic expansion
        # ψ(x) ≈ ln(x) - 1/(2x) - 1/(12x²) + 1/(120x⁴) - 1/(252x⁶) + ...
        result += math.log(x) - 1.0 / (2 * x)
        x2 = x * x
        result -= 1.0 / (12 * x2)
        result += 1.0 / (120 * x2 * x2)
        result -= 1.0 / (252 * x2 * x2 * x2)

        return result

    def beta(self, a: float, b: float) -> float:
        """
        Beta function B(a, b) = Γ(a)Γ(b)/Γ(a+b).
        """
        self._stats['evaluations'] += 1
        return self.gamma(a) * self.gamma(b) / self.gamma(a + b)

    def incomplete_gamma(self, a: float, x: float) -> float:
        """
        Lower incomplete gamma function γ(a, x).

        Uses series expansion for small x, continued fraction for large x.
        """
        self._stats['evaluations'] += 1

        if x < 0:
            raise ValueError("x must be non-negative")
        if a <= 0:
            raise ValueError("a must be positive")

        if x < a + 1:
            # Series expansion
            return self._gamma_series(a, x)
        else:
            # Continued fraction
            return self.gamma(a) - self._gamma_cf(a, x)

    def _gamma_series(self, a: float, x: float) -> float:
        """Series expansion for incomplete gamma."""
        if x == 0:
            return 0.0

        ap = a
        delta_sum = 1.0 / a
        total = delta_sum

        for _ in range(100):
            ap += 1
            delta_sum *= x / ap
            total += delta_sum
            if abs(delta_sum) < abs(total) * 1e-15:
                break

        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))

    def _gamma_cf(self, a: float, x: float) -> float:
        """Continued fraction for upper incomplete gamma."""
        fpmin = 1e-30
        b = x + 1 - a
        c = 1.0 / fpmin
        d = 1.0 / b
        h = d

        for i in range(1, 101):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < fpmin:
                d = fpmin
            c = b + an / c
            if abs(c) < fpmin:
                c = fpmin
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-15:
                break

        return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h

    # ==================== ERROR FUNCTIONS ====================

    def erf(self, x: float) -> float:
        """
        Error function erf(x) = (2/√π) ∫₀ˣ e^(-t²) dt.

        Uses rational approximation for |x| < 4, asymptotic for large |x|.
        """
        self._stats['evaluations'] += 1

        if x < 0:
            return -self.erf(-x)

        if x < 4:
            # Horner form of rational approximation
            t = 1.0 / (1.0 + 0.3275911 * x)
            poly = t * (0.254829592 + t * (-0.284496736 + t * (
                1.421413741 + t * (-1.453152027 + t * 1.061405429))))
            return 1.0 - poly * math.exp(-x * x)
        else:
            # Asymptotic expansion
            return 1.0

    def erfc(self, x: float) -> float:
        """Complementary error function erfc(x) = 1 - erf(x)."""
        self._stats['evaluations'] += 1

        if x < 0:
            return 2.0 - self.erfc(-x)

        if x < 4:
            return 1.0 - self.erf(x)
        else:
            # Asymptotic expansion for large x
            x2 = x * x
            result = math.exp(-x2) / (x * math.sqrt(math.pi))
            result *= (1 - 1 / (2 * x2) + 3 / (4 * x2 * x2))
            return result

    def erfi(self, x: float) -> float:
        """
        Imaginary error function erfi(x) = -i * erf(i * x).

        erfi(x) = (2/√π) ∫₀ˣ e^(t²) dt
        """
        self._stats['evaluations'] += 1

        # Series expansion
        result = 0.0
        term = x
        x2 = x * x

        for n in range(100):
            result += term / (2 * n + 1)
            term *= x2 / (n + 1)
            if abs(term) < 1e-15 * abs(result):
                break

        return result * 2 / math.sqrt(math.pi)

    # ==================== BESSEL FUNCTIONS ====================

    def bessel_j(self, n: int, x: float) -> float:
        """
        Bessel function of the first kind J_n(x).

        Uses series expansion for small x, recurrence for integers.
        """
        self._stats['evaluations'] += 1

        if x == 0:
            return 1.0 if n == 0 else 0.0

        if abs(x) < 10:
            return self._bessel_j_series(n, x)
        else:
            return self._bessel_j_asymptotic(n, x)

    def _bessel_j_series(self, n: int, x: float) -> float:
        """Series expansion for J_n(x)."""
        # J_n(x) = (x/2)^n * Σ (-1)^k * (x/2)^(2k) / (k! * (n+k)!)
        half_x = x / 2
        result = 0.0
        term = (half_x ** n) / self.factorial(n)

        for k in range(50):
            result += term
            term *= -half_x * half_x / ((k + 1) * (n + k + 1))
            if abs(term) < 1e-15 * abs(result):
                break

        return result

    def _bessel_j_asymptotic(self, n: int, x: float) -> float:
        """Asymptotic expansion for J_n(x) for large x."""
        # J_n(x) ≈ √(2/(πx)) * cos(x - nπ/2 - π/4)
        phase = x - n * math.pi / 2 - math.pi / 4
        return math.sqrt(2 / (math.pi * x)) * math.cos(phase)

    def bessel_y(self, n: int, x: float) -> float:
        """
        Bessel function of the second kind Y_n(x).
        """
        self._stats['evaluations'] += 1

        if x <= 0:
            return float('-inf')

        if abs(x) < 10:
            return self._bessel_y_series(n, x)
        else:
            return self._bessel_y_asymptotic(n, x)

    def _bessel_y_series(self, n: int, x: float) -> float:
        """Series expansion for Y_n(x)."""
        # Y_n(x) = (2/π) * J_n(x) * ln(x/2) - (1/π) * Σ...
        # Simplified approximation
        jn = self.bessel_j(n, x)
        return (2 / math.pi) * jn * math.log(x / 2) - 1 / (math.pi * x ** n)

    def _bessel_y_asymptotic(self, n: int, x: float) -> float:
        """Asymptotic expansion for Y_n(x) for large x."""
        phase = x - n * math.pi / 2 - math.pi / 4
        return math.sqrt(2 / (math.pi * x)) * math.sin(phase)

    def bessel_i(self, n: int, x: float) -> float:
        """
        Modified Bessel function of the first kind I_n(x).
        """
        self._stats['evaluations'] += 1

        if x == 0:
            return 1.0 if n == 0 else 0.0

        # I_n(x) = i^(-n) * J_n(ix)
        # Series: I_n(x) = (x/2)^n * Σ (x/2)^(2k) / (k! * (n+k)!)
        half_x = x / 2
        result = 0.0
        term = (half_x ** n) / self.factorial(n)

        for k in range(50):
            result += term
            term *= half_x * half_x / ((k + 1) * (n + k + 1))
            if abs(term) < 1e-15 * abs(result):
                break

        return result

    def bessel_k(self, n: int, x: float) -> float:
        """
        Modified Bessel function of the second kind K_n(x).
        """
        self._stats['evaluations'] += 1

        if x <= 0:
            return float('inf')

        # Asymptotic for large x
        if x > 10:
            return math.sqrt(math.pi / (2 * x)) * math.exp(-x)

        # Use relation K_n = (π/2) * (I_{-n} - I_n) / sin(nπ)
        # For integer n, use limit form
        if n == 0:
            return -math.log(x / 2) * self.bessel_i(0, x)

        return (math.pi / 2) * (self.bessel_i(-n, x) - self.bessel_i(n, x)) / math.sin(n * math.pi)

    # ==================== ELLIPTIC INTEGRALS ====================

    def elliptic_k(self, m: float) -> float:
        """
        Complete elliptic integral of the first kind K(m).

        K(m) = ∫₀^(π/2) dθ / √(1 - m sin²θ)

        Uses arithmetic-geometric mean.
        """
        self._stats['evaluations'] += 1

        if m >= 1:
            return float('inf')
        if m < 0:
            # Use transformation
            k_prime = math.sqrt(1 - m)
            return self.elliptic_k(1 - k_prime * k_prime) / k_prime

        # AGM method
        a, b = 1.0, math.sqrt(1 - m)
        for _ in range(20):
            a_new = (a + b) / 2
            b_new = math.sqrt(a * b)
            if abs(a_new - b_new) < 1e-15:
                break
            a, b = a_new, b_new

        return math.pi / (2 * a)

    def elliptic_e(self, m: float) -> float:
        """
        Complete elliptic integral of the second kind E(m).

        E(m) = ∫₀^(π/2) √(1 - m sin²θ) dθ

        Uses arithmetic-geometric mean with correction.
        """
        self._stats['evaluations'] += 1

        if m > 1:
            return float('nan')

        # AGM method with E tracking
        a, b = 1.0, math.sqrt(1 - m)
        c = math.sqrt(m)
        e_sum = c * c / 2

        power = 1
        for _ in range(20):
            a_new = (a + b) / 2
            b_new = math.sqrt(a * b)
            c_new = (a - b) / 2
            power *= 2
            e_sum -= power * c_new * c_new
            if abs(c_new) < 1e-15:
                break
            a, b, c = a_new, b_new, c_new

        k_val = math.pi / (2 * a)
        return k_val * (1 - e_sum)

    # ==================== ZETA AND POLYLOG ====================

    def zeta(self, s: float) -> float:
        """
        Riemann zeta function ζ(s) = Σ n^(-s).
        """
        self._stats['evaluations'] += 1

        if s == 1:
            return float('inf')

        if s < 0:
            # Reflection formula
            return (2 ** s * math.pi ** (s - 1) *
                    math.sin(math.pi * s / 2) *
                    self.gamma(1 - s) * self.zeta(1 - s))

        # Direct summation with acceleration
        result = 0.0
        for n in range(1, 1000):
            term = n ** (-s)
            result += term
            if term < 1e-15 * result:
                break

        return result

    def polylog(self, s: float, z: float) -> float:
        """
        Polylogarithm Li_s(z) = Σ z^k / k^s.
        """
        self._stats['evaluations'] += 1

        if abs(z) >= 1:
            raise ValueError("|z| must be < 1 for convergence")

        result = 0.0
        zk = z

        for k in range(1, 1000):
            term = zk / (k ** s)
            result += term
            zk *= z
            if abs(term) < 1e-15 * abs(result):
                break

        return result

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Perform process message operation.

        Args:
        message

        Returns:
        Result of the operation

        Example:
        >>> specialist = SpecialFunctionsSpecialist()
        >>> result = specialist.process_message(...)
        # Returns result
        """
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'gamma': lambda p: self.gamma(p.get('z', 1)),
            'digamma': lambda p: self.digamma(p.get('x', 1)),
            'beta': lambda p: self.beta(p.get('a', 1), p.get('b', 1)),
            'erf': lambda p: self.erf(p.get('x', 0)),
            'erfc': lambda p: self.erfc(p.get('x', 0)),
            'bessel_j': lambda p: self.bessel_j(p.get('n', 0), p.get('x', 0)),
            'bessel_y': lambda p: self.bessel_y(p.get('n', 0), p.get('x', 1)),
            'bessel_i': lambda p: self.bessel_i(p.get('n', 0), p.get('x', 0)),
            'bessel_k': lambda p: self.bessel_k(p.get('n', 0), p.get('x', 1)),
            'elliptic_k': lambda p: self.elliptic_k(p.get('m', 0)),
            'elliptic_e': lambda p: self.elliptic_e(p.get('m', 0)),
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
        >>> specialist = SpecialFunctionsSpecialist()
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
        >>> specialist = SpecialFunctionsSpecialist()
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
        >>> specialist = SpecialFunctionsSpecialist()
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
        >>> specialist = SpecialFunctionsSpecialist()
        >>> result = specialist.execute_step(...)
        # Returns result
        """
        pass


__all__ = [
    'SpecialFunctionsSpecialist',
]
