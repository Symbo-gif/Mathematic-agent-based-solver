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
Native Complex Number Simplification Engine

Pure Python symbolic complex number manipulation without SymPy dependency.
Implements standard complex number operations and simplifications.

OPERATIONS:
-----------
1. Basic arithmetic: add, subtract, multiply, divide
2. Conjugate: conj(a + bi) = a - bi
3. Modulus/Absolute value: |a + bi| = sqrt(a^2 + b^2)
4. Argument: arg(a + bi) = atan2(b, a)
5. Polar form: r * e^(i*theta)
6. Powers of i: i^n (cyclic: 1, i, -1, -i)
7. Euler's formula: e^(i*x) = cos(x) + i*sin(x)
8. De Moivre's theorem: (r*e^(i*theta))^n = r^n * e^(i*n*theta)
"""

import math
import re
import logging
from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple, Optional, Union, List

logger = logging.getLogger('symbo_agentic_reasoners.core.native_complex')


@dataclass
class Complex:
    """
    Represents a complex number a + bi.

    Uses exact fractions where possible for precision.
    """
    real: Union[int, float, Fraction]
    imag: Union[int, float, Fraction]

    def __str__(self) -> str:
        if self.imag == 0:
            return str(self.real)
        elif self.real == 0:
            if self.imag == 1:
                return "I"
            elif self.imag == -1:
                return "-I"
            else:
                return f"{self.imag}*I"
        else:
            if self.imag == 1:
                return f"{self.real} + I"
            elif self.imag == -1:
                return f"{self.real} - I"
            elif self.imag < 0:
                return f"{self.real} - {abs(self.imag)}*I"
            else:
                return f"{self.real} + {self.imag}*I"

    def __repr__(self) -> str:
        return f"Complex({self.real}, {self.imag})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Complex):
            return self.real == other.real and self.imag == other.imag
        elif isinstance(other, (int, float)):
            return self.real == other and self.imag == 0
        return False

    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real + other.real, self.imag + other.imag)
        elif isinstance(other, (int, float, Fraction)):
            return Complex(self.real + other, self.imag)
        raise TypeError(f"Cannot add Complex and {type(other)}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real - other.real, self.imag - other.imag)
        elif isinstance(other, (int, float, Fraction)):
            return Complex(self.real - other, self.imag)
        raise TypeError(f"Cannot subtract {type(other)} from Complex")

    def __rsub__(self, other):
        if isinstance(other, (int, float, Fraction)):
            return Complex(other - self.real, -self.imag)
        raise TypeError(f"Cannot subtract Complex from {type(other)}")

    def __mul__(self, other):
        if isinstance(other, Complex):
            # (a + bi)(c + di) = (ac - bd) + (ad + bc)i
            return Complex(
                self.real * other.real - self.imag * other.imag,
                self.real * other.imag + self.imag * other.real
            )
        elif isinstance(other, (int, float, Fraction)):
            return Complex(self.real * other, self.imag * other)
        raise TypeError(f"Cannot multiply Complex and {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Complex):
            # (a + bi)/(c + di) = (a + bi)(c - di) / (c^2 + d^2)
            denom = other.real ** 2 + other.imag ** 2
            if denom == 0:
                raise ZeroDivisionError("Division by zero complex number")
            conjugate = Complex(other.real, -other.imag)
            numerator = self * conjugate
            return Complex(numerator.real / denom, numerator.imag / denom)
        elif isinstance(other, (int, float, Fraction)):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return Complex(self.real / other, self.imag / other)
        raise TypeError(f"Cannot divide Complex by {type(other)}")

    def __rtruediv__(self, other):
        if isinstance(other, (int, float, Fraction)):
            return Complex(other, 0) / self
        raise TypeError(f"Cannot divide {type(other)} by Complex")

    def __neg__(self):
        return Complex(-self.real, -self.imag)

    def __pow__(self, n: int):
        if not isinstance(n, int):
            # For non-integer powers, use polar form
            return self._pow_polar(n)

        if n == 0:
            return Complex(1, 0)
        elif n < 0:
            return Complex(1, 0) / (self ** (-n))
        elif n == 1:
            return self
        else:
            # Use repeated squaring for efficiency
            result = Complex(1, 0)
            base = self
            while n > 0:
                if n % 2 == 1:
                    result = result * base
                base = base * base
                n //= 2
            return result

    def _pow_polar(self, n: float):
        """Compute complex power using polar form."""
        r, theta = self.to_polar()
        new_r = r ** n
        new_theta = theta * n
        return Complex.from_polar(new_r, new_theta)

    @property
    def conjugate(self):
        """Return complex conjugate: conj(a + bi) = a - bi"""
        return Complex(self.real, -self.imag)

    @property
    def modulus(self) -> float:
        """Return modulus (absolute value): |a + bi| = sqrt(a^2 + b^2)"""
        return math.sqrt(float(self.real) ** 2 + float(self.imag) ** 2)

    @property
    def argument(self) -> float:
        """Return argument (phase angle) in radians."""
        return math.atan2(float(self.imag), float(self.real))

    def to_polar(self) -> Tuple[float, float]:
        """Convert to polar form (r, theta)."""
        return (self.modulus, self.argument)

    @classmethod
    def from_polar(cls, r: float, theta: float):
        """Create complex number from polar form."""
        return cls(r * math.cos(theta), r * math.sin(theta))

    def simplify(self):
        """Simplify the complex number, converting floats to fractions where possible."""
        def _simplify_component(x):
            """Perform  simplify component operation.

            Args:
            x: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj._simplify_component(...)
            """
            if isinstance(x, float):
                # Check if close to integer
                if abs(x - round(x)) < 1e-10:
                    return int(round(x))
                # Try small fractions
                for denom in range(1, 100):
                    num = x * denom
                    if abs(num - round(num)) < 1e-10:
                        return Fraction(int(round(num)), denom)
            return x

        return Complex(
            _simplify_component(self.real),
            _simplify_component(self.imag)
        )


# Constants
I = Complex(0, 1)  # The imaginary unit
ZERO = Complex(0, 0)
ONE = Complex(1, 0)


def power_of_i(n: int) -> Complex:
    """
    Compute i^n using the cyclic property.

    i^0 = 1, i^1 = i, i^2 = -1, i^3 = -i, i^4 = 1, ...
    """
    cycle = [Complex(1, 0), Complex(0, 1), Complex(-1, 0), Complex(0, -1)]
    return cycle[n % 4]


def parse_complex(expr_str: str) -> Optional[Complex]:
    """
    Parse a complex number from string.

    Supported formats:
    - "3 + 4i", "3 + 4*i", "3 + 4*I"
    - "3 - 4i", "-3 + 4i"
    - "5" (real only)
    - "4i", "4*i" (imaginary only)
    - "i", "I" (just i)
    """
    # Normalize: remove spaces, lowercase, replace I with i
    s = expr_str.replace(' ', '').replace('I', 'i').replace('*', '')

    # Just i
    if s == 'i':
        return I
    if s == '-i':
        return Complex(0, -1)

    # Just imaginary: like "4i" or "-4i"
    imag_only = re.match(r'^([+-]?\d+(?:\.\d+)?)i$', s)
    if imag_only:
        return Complex(0, float(imag_only.group(1)))

    # Just real: like "4" or "-4.5"
    real_only = re.match(r'^([+-]?\d+(?:\.\d+)?)$', s)
    if real_only:
        return Complex(float(real_only.group(1)), 0)

    # Full complex: like "3+4i" or "3-4i"
    full_complex = re.match(r'^([+-]?\d+(?:\.\d+)?)([+-])(\d+(?:\.\d+)?)i$', s)
    if full_complex:
        real = float(full_complex.group(1))
        sign = 1 if full_complex.group(2) == '+' else -1
        imag = sign * float(full_complex.group(3))
        return Complex(real, imag)

    # "a + bi" format with coefficient 1: like "3+i" or "3-i"
    plus_minus_i = re.match(r'^([+-]?\d+(?:\.\d+)?)([+-])i$', s)
    if plus_minus_i:
        real = float(plus_minus_i.group(1))
        imag = 1 if plus_minus_i.group(2) == '+' else -1
        return Complex(real, imag)

    return None


def simplify_complex(expr_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Simplify a complex expression.

    Args:
        expr_str: Expression containing complex numbers

    Returns:
        (success, result_string, method)
    """
    try:
        # Parse as simple complex number
        z = parse_complex(expr_str)
        if z is not None:
            z = z.simplify()
            return True, str(z), "native_complex"

        # Try to evaluate power of i
        i_power = re.match(r'^i\^(\d+)$', expr_str.replace(' ', '').replace('I', 'i'))
        if i_power:
            n = int(i_power.group(1))
            result = power_of_i(n)
            return True, str(result), "native_complex"

        # Try to evaluate (a+bi)^n
        pow_match = re.match(r'^\((.+)\)\^(\d+)$', expr_str.replace(' ', ''))
        if pow_match:
            base_str = pow_match.group(1)
            n = int(pow_match.group(2))
            base = parse_complex(base_str)
            if base is not None:
                result = (base ** n).simplify()
                return True, str(result), "native_complex"

        return False, None, "cannot_parse_complex"
    except Exception as e:
        logger.debug(f"Complex simplification failed: {e}")
        return False, None, f"error: {e}"


def conjugate(expr_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Compute complex conjugate.

    conj(a + bi) = a - bi
    """
    try:
        z = parse_complex(expr_str)
        if z is not None:
            result = z.conjugate.simplify()
            return True, str(result), "native_complex"
        return False, None, "cannot_parse_complex"
    except Exception as e:
        return False, None, f"error: {e}"


def modulus(expr_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Compute modulus (absolute value).

    |a + bi| = sqrt(a^2 + b^2)
    """
    try:
        z = parse_complex(expr_str)
        if z is not None:
            r = z.modulus
            # Simplify if integer
            if abs(r - round(r)) < 1e-10:
                return True, str(int(round(r))), "native_complex"
            return True, str(r), "native_complex"
        return False, None, "cannot_parse_complex"
    except Exception as e:
        return False, None, f"error: {e}"


def argument(expr_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Compute argument (phase angle).

    arg(a + bi) = atan2(b, a)
    """
    try:
        z = parse_complex(expr_str)
        if z is not None:
            theta = z.argument
            # Check for standard angles
            if abs(theta) < 1e-10:
                return True, "0", "native_complex"
            elif abs(theta - math.pi) < 1e-10:
                return True, "pi", "native_complex"
            elif abs(theta + math.pi) < 1e-10:
                return True, "-pi", "native_complex"
            elif abs(theta - math.pi/2) < 1e-10:
                return True, "pi/2", "native_complex"
            elif abs(theta + math.pi/2) < 1e-10:
                return True, "-pi/2", "native_complex"
            elif abs(theta - math.pi/4) < 1e-10:
                return True, "pi/4", "native_complex"
            elif abs(theta - 3*math.pi/4) < 1e-10:
                return True, "3*pi/4", "native_complex"
            else:
                return True, str(theta), "native_complex"
        return False, None, "cannot_parse_complex"
    except Exception as e:
        return False, None, f"error: {e}"


def to_polar(expr_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Convert to polar form.

    a + bi -> r * e^(i*theta)
    """
    try:
        z = parse_complex(expr_str)
        if z is not None:
            r, theta = z.to_polar()
            # Simplify r
            if abs(r - round(r)) < 1e-10:
                r_str = str(int(round(r)))
            else:
                r_str = str(r)
            # Simplify theta
            _, theta_str, _ = argument(expr_str)
            if theta_str == "0":
                return True, r_str, "native_complex"
            else:
                return True, f"{r_str}*exp(I*{theta_str})", "native_complex"
        return False, None, "cannot_parse_complex"
    except Exception as e:
        return False, None, f"error: {e}"


def multiply_complex(z1_str: str, z2_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Multiply two complex numbers.
    """
    try:
        z1 = parse_complex(z1_str)
        z2 = parse_complex(z2_str)
        if z1 is not None and z2 is not None:
            result = (z1 * z2).simplify()
            return True, str(result), "native_complex"
        return False, None, "cannot_parse_complex"
    except Exception as e:
        return False, None, f"error: {e}"


def divide_complex(z1_str: str, z2_str: str) -> Tuple[bool, Optional[str], str]:
    """
    Divide two complex numbers.
    """
    try:
        z1 = parse_complex(z1_str)
        z2 = parse_complex(z2_str)
        if z1 is not None and z2 is not None:
            result = (z1 / z2).simplify()
            return True, str(result), "native_complex"
        return False, None, "cannot_parse_complex"
    except Exception as e:
        return False, None, f"error: {e}"


# =============================================================================
# TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("NATIVE COMPLEX NUMBER ENGINE TEST")
    print("=" * 70)

    # Basic operations
    print("\n--- Basic Operations ---")
    z1 = Complex(3, 4)
    z2 = Complex(1, 2)
    print(f"z1 = {z1}")
    print(f"z2 = {z2}")
    print(f"z1 + z2 = {z1 + z2}")
    print(f"z1 - z2 = {z1 - z2}")
    print(f"z1 * z2 = {z1 * z2}")
    print(f"z1 / z2 = {z1 / z2}")

    # Conjugate and modulus
    print("\n--- Conjugate and Modulus ---")
    print(f"conj({z1}) = {z1.conjugate}")
    print(f"|{z1}| = {z1.modulus}")
    print(f"arg({z1}) = {z1.argument}")

    # Powers of i
    print("\n--- Powers of i ---")
    for n in range(8):
        print(f"i^{n} = {power_of_i(n)}")

    # Complex powers
    print("\n--- Complex Powers ---")
    z = Complex(1, 1)
    for n in range(5):
        print(f"(1+i)^{n} = {z**n}")

    # Parsing
    print("\n--- Parsing ---")
    test_strings = ["3+4i", "3 - 4i", "5", "4i", "i", "-i", "3+i"]
    for s in test_strings:
        z = parse_complex(s)
        print(f"parse_complex('{s}') = {z}")

    # API functions
    print("\n--- API Functions ---")
    success, result, method = simplify_complex("3+4i")
    print(f"simplify_complex('3+4i') = {result}")

    success, result, method = conjugate("3+4i")
    print(f"conjugate('3+4i') = {result}")

    success, result, method = modulus("3+4i")
    print(f"modulus('3+4i') = {result}")

    success, result, method = argument("1+i")
    print(f"argument('1+i') = {result}")

    success, result, method = to_polar("1+i")
    print(f"to_polar('1+i') = {result}")

    success, result, method = simplify_complex("i^5")
    print(f"simplify_complex('i^5') = {result}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
