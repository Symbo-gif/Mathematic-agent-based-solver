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
            from symbo_agentic_reasoners.agents.specialists.calculus.ode_specialist import (
                ODESolutionSpecialist
            )
            return ODESolutionSpecialist()

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
        self._df = None  # Directory Facilitator (lazy init)
        self._blackboard = None  # Blackboard (lazy init)

    def _ensure_infrastructure(self):
        """Ensure DF and Blackboard are initialized"""
        if not self._df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
            from symbo_agentic_reasoners.core.blackboard import Blackboard

            self._df = DirectoryFacilitator()
            self._blackboard = Blackboard()

            # Register all advanced integration specialists with DF
            self._register_integration_team()

    def _register_integration_team(self):
        """Register advanced integration specialists with DF"""
        try:
            # Create and register ExpTrig specialist
            from symbo_agentic_reasoners.agents.specialists.calculus.exp_trig_integration_specialist import (
                ExponentialTrigIntegrationSpecialist
            )
            exp_trig = ExponentialTrigIntegrationSpecialist(df=self._df, blackboard=self._blackboard)
            self._specialists['calculus.integration.exp_trig'] = exp_trig

            # Create and register Advanced Integration coordinator
            from symbo_agentic_reasoners.agents.specialists.calculus.advanced_integration_specialist import (
                AdvancedIntegrationSpecialist
            )
            advanced = AdvancedIntegrationSpecialist(df=self._df, blackboard=self._blackboard)
            self._specialists['calculus.integration.advanced'] = advanced

            # Create and register Tabular specialist
            from symbo_agentic_reasoners.agents.specialists.calculus.tabular_integration_specialist import (
                TabularIntegrationSpecialist
            )
            tabular = TabularIntegrationSpecialist(df=self._df, blackboard=self._blackboard)
            self._specialists['calculus.integration.tabular'] = tabular

            # Create and register Substitution specialist
            from symbo_agentic_reasoners.agents.specialists.calculus.substitution_specialist import (
                SubstitutionSpecialist
            )
            substitution = SubstitutionSpecialist(df=self._df, blackboard=self._blackboard)
            self._specialists['calculus.integration.substitution'] = substitution

            logger.info("Advanced integration team registered with DF")

        except Exception as e:
            logger.warning(f"Could not register integration team: {e}")

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

        # Ensure infrastructure is ready (for ODE specialist to access integration team)
        if key == 'calculus.ode':
            self._ensure_infrastructure()

        # Create specialist with DF and Blackboard if ODE
        if key == 'calculus.ode':
            from symbo_agentic_reasoners.agents.specialists.calculus.ode_specialist import (
                ODESolutionSpecialist
            )
            specialist = ODESolutionSpecialist(df=self._df, blackboard=self._blackboard)
        else:
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
