# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0

"""
Mathematical Constants
======================

Defines fundamental mathematical constants used throughout the symbolic engine.
NO SYMPY DEPENDENCY - Pure Python implementation.
"""

import math


class MathConstant:
    """Mathematical constants with known values."""
    PI = math.pi  # 3.141592653589793
    E = math.e    # 2.718281828459045
    GAMMA = 0.5772156649015329  # Euler-Mascheroni constant
    PHI = 1.618033988749895     # Golden ratio

    @staticmethod
    def is_constant(name: str) -> bool:
        """Check if a name represents a mathematical constant."""
        return name.lower() in ('pi', 'e', 'euler', 'gamma', 'phi', 'i')

    @staticmethod
    def get_value(name: str) -> float:
        """Get numerical value of a constant."""
        name_lower = name.lower()
        if name_lower == 'pi':
            return MathConstant.PI
        elif name_lower == 'e':
            return MathConstant.E
        elif name_lower in ('gamma', 'euler'):
            return MathConstant.GAMMA
        elif name_lower == 'phi':
            return MathConstant.PHI
        else:
            raise ValueError(f"Unknown constant: {name}")


__all__ = ['MathConstant']
