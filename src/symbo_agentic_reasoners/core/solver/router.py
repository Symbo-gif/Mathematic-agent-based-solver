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
Problem Router
==============

Classifies mathematical problems and routes them to appropriate specialists.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_specialist_key(domain: str, operation: str) -> str:
    """
    Generate specialist lookup key based on domain and operation.

    Args:
        domain: Problem domain (calculus, algebra, etc.)
        operation: Operation type (derivative, integral, etc.)

    Returns:
        Specialist key string
    """
    # Map operations to specialist types
    op_map = {
        'derivative': 'calculus.diff',
        'diff': 'calculus.diff',
        'differentiate': 'calculus.diff',
        'integral': 'calculus.integrate',
        'integrate': 'calculus.integrate',
        'dsolve': 'calculus.ode',
        'ode': 'calculus.ode',
        'solve': 'algebra.solve',
        'factor': 'algebra.polynomial',
        'expand': 'algebra.polynomial',
        'simplify': 'algebra.arithmetic',
        'compute': 'algebra.arithmetic',
        'limit': 'calculus.limit',
        'series': 'calculus.series',
        'summation': 'calculus.series',  # Route infinite series to series specialist
        'product': 'calculus.series',     # Route infinite products to series specialist
    }

    if operation in op_map:
        return op_map[operation]

    # Default based on domain
    domain_defaults = {
        'calculus': 'calculus.diff',
        'algebra': 'algebra.polynomial',
        'geometry': 'geometry.basic',
        'logic': 'logic.basic'
    }

    return domain_defaults.get(domain, 'algebra.arithmetic')


def create_specialist(key: str) -> Optional[Any]:
    """
    Create specialist instance based on key (lazy loading).

    Args:
        key: Specialist key (e.g., 'calculus.diff')

    Returns:
        Specialist instance or None if not found
    """
    try:
        if key == 'calculus.diff':
            from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import (
                DifferentiationSpecialist
            )
            return DifferentiationSpecialist()

        elif key == 'calculus.integrate':
            from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import (
                IntegrationSpecialist
            )
            return IntegrationSpecialist()

        elif key == 'calculus.ode':
            from symbo_agentic_reasoners.agents.specialists.calculus.ode_solver import (
                ODESolver
            )
            return ODESolver()

        elif key == 'algebra.polynomial':
            from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import (
                PolynomialSpecialist
            )
            return PolynomialSpecialist()

        elif key == 'algebra.arithmetic':
            from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
                ArithmeticSpecialist
            )
            return ArithmeticSpecialist()

        elif key == 'algebra.solve':
            from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import (
                PolynomialSpecialist
            )
            return PolynomialSpecialist()

        elif key == 'calculus.series':
            from symbo_agentic_reasoners.agents.specialists.calculus.series_specialist import (
                SeriesSpecialist
            )
            return SeriesSpecialist()

        else:
            logger.debug(f"No specialist for key: {key}")
            return None

    except ImportError as e:
        logger.warning(f"Could not import specialist {key}: {e}")
        return None


class SpecialistRouter:
    """
    Routes problems to appropriate specialist agents.

    Manages lazy loading of specialists to minimize resource usage.
    """

    def __init__(self):
        """Initialize the router."""
        self._specialists: Dict[str, Any] = {}

    def get_specialist(self, key: str, domain: str = "", operation: str = "") -> Optional[Any]:
        """
        Get or create specialist instance (lazy initialization).

        Args:
            key: Specialist key
            domain: Problem domain (used for fallback routing)
            operation: Operation type (used for fallback routing)

        Returns:
            Specialist instance or None
        """
        if key in self._specialists:
            return self._specialists[key]

        specialist = create_specialist(key)
        if specialist:
            self._specialists[key] = specialist

        return specialist

    def clear_specialists(self) -> None:
        """Clear all loaded specialists (for testing)."""
        self._specialists.clear()

    def get_loaded_specialists(self) -> list:
        """Get list of currently loaded specialist keys."""
        return list(self._specialists.keys())
