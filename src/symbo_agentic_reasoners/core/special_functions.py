"""
Special Functions for Integration
==================================

Defines special functions that appear in integration results.

FUNCTIONS SUPPORTED:
- erf(x): Error function - ∫exp(-t²)dt from 0 to x
- Ei(x): Exponential integral - ∫exp(t)/t dt from -∞ to x
- Si(x): Sine integral - ∫sin(t)/t dt from 0 to x
- Ci(x): Cosine integral - ∫cos(t)/t dt from 0 to x

These are represented symbolically, not evaluated numerically.

100% Native Python - NO SymPy dependency
"""

import math
from typing import Optional


class SpecialFunction:
    """Base class for special functions."""

    def __init__(self, name: str, argument: str):
        """
        Initialize special function.

        Args:
            name: Function name (erf, Ei, Si, Ci)
            argument: Argument expression
        """
        self.name = name
        self.argument = argument

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name}({self.argument})"

    def __repr__(self) -> str:
        """Debug representation."""
        return f"SpecialFunction({self.name}, {self.argument})"


def erf(x: str) -> str:
    """
    Error function: erf(x) = (2/√π) ∫₀ˣ exp(-t²) dt

    Used for: ∫exp(-x²)dx, ∫exp(-ax²)dx

    Args:
        x: Argument expression

    Returns:
        String representation: "erf(x)"
    """
    return f"erf({x})"


def Ei(x: str) -> str:
    """
    Exponential integral: Ei(x) = ∫₋∞ˣ exp(t)/t dt

    Used for: ∫exp(x)/x dx

    Args:
        x: Argument expression

    Returns:
        String representation: "Ei(x)"
    """
    return f"Ei({x})"


def Si(x: str) -> str:
    """
    Sine integral: Si(x) = ∫₀ˣ sin(t)/t dt

    Used for: ∫sin(x)/x dx

    Args:
        x: Argument expression

    Returns:
        String representation: "Si(x)"
    """
    return f"Si({x})"


def Ci(x: str) -> str:
    """
    Cosine integral: Ci(x) = ∫₀ˣ cos(t)/t dt

    Used for: ∫cos(x)/x dx

    Args:
        x: Argument expression

    Returns:
        String representation: "Ci(x)"
    """
    return f"Ci({x})"


# Common integral results using special functions
SPECIAL_FUNCTION_INTEGRALS = {
    # Gaussian integrals
    'exp(-x**2)': 'sqrt(pi)/2 * erf(x)',
    'exp(-x^2)': 'sqrt(pi)/2 * erf(x)',

    # Exponential integrals
    'exp(x)/x': 'Ei(x)',
    'exp(-x)/x': 'Ei(-x)',

    # Trigonometric integrals
    'sin(x)/x': 'Si(x)',
    'cos(x)/x': 'Ci(x)',
}


def format_integral_with_special_functions(pattern: str, var: str = 'x') -> Optional[str]:
    """
    Format integral result using special functions.

    Args:
        pattern: Integration pattern
        var: Integration variable

    Returns:
        Integral result or None if no special function applies
    """
    # Normalize pattern
    pattern_clean = pattern.replace(' ', '').lower()

    # Check exact matches
    for key, value in SPECIAL_FUNCTION_INTEGRALS.items():
        key_clean = key.replace(' ', '').lower()
        if pattern_clean == key_clean:
            return value

    return None


if __name__ == "__main__":
    # Test special functions
    print("Special Function Tests:")
    print("=" * 60)

    test_cases = [
        ("exp(-x**2)", "sqrt(pi)/2 * erf(x)"),
        ("exp(x)/x", "Ei(x)"),
        ("sin(x)/x", "Si(x)"),
        ("cos(x)/x", "Ci(x)"),
    ]

    for pattern, expected in test_cases:
        result = format_integral_with_special_functions(pattern)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status:4s} integral({pattern:15s}) = {result or 'None':20s}")
