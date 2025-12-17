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
PHASE 2 - NUMERICAL COMPUTATION UTILITY (Tier 3)
================================================

THE SYSTEM SAFETY NET - Ultimate fallback for all supervisors.

Ensures system NEVER "gives up" when symbolic math is computationally
intractable or mathematically impossible (e.g., Abel-Ruffini theorem for degree 5+ polynomials).

This agent does NOT "reason"; it "crunches."
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners_phase0.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners_phase0.memory.blackboard import Blackboard
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import optimize, integrate, linalg

class NumericalComputationUtility(BDIAgent):
    """
    Numerical Computation Utility - The System Safety Net

    ROLE:
    ----
    High-performance computational engine for all teams. Acts as the fallback
    destination for any supervisor that cannot obtain a symbolic solution.

    EXAMPLE:
    -------
    If Algebra Supervisor cannot solve a degree-5+ polynomial symbolically,
    it routes to this agent for numerical root approximation.

    LIBRARY:
    -------
    NumPy/SciPy (high-performance numerical computation)

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 161-166
    """

    def __init__(self, agent_id='numerical_utility_001', df: Optional[DirectoryFacilitator]=None, blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = self.fallback_calls = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.numerical',
                agent_id=agent_id,
                algorithm='numpy_scipy',
                cost='high',
                tier='3',
                role='fallback',
                library='numpy_scipy',
                type='approximate'))

        print(f"[{agent_id}] Numerical Computation Utility initialized")
        print(f"  ROLE: SYSTEM SAFETY NET")
        print(f"  Library: NumPy + SciPy")
        print(f"  Purpose: Fallback for intractable symbolic computations")

    def update_beliefs(self):
        """Update beliefs from environment (Placeholder)."""
        pass

    def deliberate(self) -> List[Intention]:
        """Deliberate on beliefs and desires (Placeholder)."""
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step (Placeholder)."""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'fallback_calls': self.fallback_calls
        })
        return stats


if __name__ == "__main__":
    """Test Numerical Utility"""
    print("=" * 80)
    print("PHASE 2 - NUMERICAL COMPUTATION UTILITY TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

    phase0 = Phase0System()
    phase0.start()
    print()

    utility = NumericalComputationUtility(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("NUMERICAL UTILITY READY (System Safety Net)")
    print("=" * 80)
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.numerical')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Role: {service.properties.get('role')}")

    phase0.shutdown()
